from __future__ import annotations

import time
import warnings
import math
from typing import Any, Dict, Mapping, Sequence

import torch
from torch import Tensor, nn
import torch.nn.functional as F
from torch.utils.checkpoint import checkpoint

from .layout import (
    block_morton_block_contiguity,
    block_morton_layout,
    build_local_neighbors,
    make_block_layout,
    pack_grid,
    plain_morton_block_contiguity,
    prod,
    unpack_grid,
)
from .triton_selected import BackendReport, selected_attention
from .triton_route import RouteBackendReport, route_lse_topk_triton, route_mass_topk_triton
from .triton_local import LocalBackendReport, local_attention


class _LastDimRMSNorm(nn.Module):
    """Small RMSNorm for branch tensors shaped [..., dim_head]."""

    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = float(eps)
        self.weight = nn.Parameter(torch.ones(int(dim)))

    def forward(self, x: Tensor) -> Tensor:
        normed = x.float() * torch.rsqrt(x.float().pow(2).mean(dim=-1, keepdim=True).clamp_min(self.eps))
        return (normed.to(dtype=x.dtype) * self.weight.to(device=x.device, dtype=x.dtype))


class HypergridMortonSparseAttention(nn.Module):
    """HyperNSA attention over native 2D/3D/4D block-Morton packed grids."""

    def __init__(
        self,
        dim: int,
        grid_shape: Sequence[int],
        heads: int = 4,
        kv_heads: int | None = None,
        dim_head: int = 32,
        block_shape: Sequence[int] = (4, 4),
        local_radius: Sequence[int] | int = 1,
        num_summary_atoms: int = 2,
        num_selected_blocks: int = 2,
        residual_weight: float = 0.25,
        distance_weight: float = 0.10,
        micro_order: str = "morton",
        layout: str = "native",
        use_triton_kernel: bool = False,
        separate_branch_kv: bool = True,
        packed_branch_kv_projection: bool = False,
        route_select_grad: bool = False,
        skip_disabled_local_branch: bool = True,
        checkpoint_local_attention: bool = False,
        local_attention_backend: str = "torch",
        local_attention_block_n: int = 16,
        branch_output_fusion: str = "standard",
        coarse_attention_backend: str = "einsum",
        coarse_summary_pool_size: int = 1,
        exclude_own_block_from_selection: bool = True,
        route_score_mode: str = "logsumexp_logits_current",
        route_backend: str = "torch_full",
        route_materialize_scores_in_aux: bool = True,
        route_block_q: int = 16,
        route_block_c: int = 32,
        route_shape_penalty_weight: float = 0.0,
        route_center_distance_weight: float | None = None,
        route_distance_normalization: str = "raw",
        allow_raw_distance_on_probability_route: bool = False,
        branch_gate_mode: str = "softmax",
        atom_assignment_mode: str = "current_encode_only",
        route_residual_mode: str = "key_residual",
        atom_balance_loss_weight: float = 0.0,
        atom_entropy_loss_weight: float = 0.0,
        atom_orthogonality_loss_weight: float = 0.0,
        atom_temperature: float = 1.0,
        full_layer_execution: str = "full",
        query_tile_size: int = 0,
        query_tile_checkpoint: bool = False,
        route_granularity: str = "token_exact",
        route_share_tile_size: int = 16,
        enabled_branches: Sequence[str] | None = None,
        branch_output_norm: str = "none",
        branch_layer_scale: bool = False,
        branch_layer_scale_init: float | Sequence[float] | Mapping[str, float] = 1.0,
        branch_mixer_mode: str = "gated_sum",
        branch_gate_bias_init: float | Sequence[float] | Mapping[str, float] = 0.0,
        branch_gate_prior_schedule: str = "none",
        branch_gate_prior_start: float | Sequence[float] | Mapping[str, float] = 0.0,
        branch_gate_prior_end: float | Sequence[float] | Mapping[str, float] = 0.0,
        selected_mixing_mode: str = "standard",
        validate_triton_outputs: bool = False,
        pos_encoding: str = "none",
        rotary_base: float = 10000.0,
        rotary_coordinate_mode: str = "raw_grid",
        rotary_axis_scales: Sequence[float] | None = None,
        rotary_axis_pair_allocation: str = "balanced",
        compressed_rope_mode: str = "token_before_compression",
    ):
        super().__init__()
        self.dim = int(dim)
        self.grid_shape = tuple(int(x) for x in grid_shape)
        self.ndim = len(self.grid_shape)
        if not 2 <= self.ndim <= 4:
            raise ValueError("HyperNSA attention expects a 2D, 3D, or 4D token grid")

        self.heads = int(heads)
        self.kv_heads = int(kv_heads if kv_heads is not None else heads)
        if self.heads % self.kv_heads != 0:
            raise ValueError("heads must be divisible by kv_heads")
        self.num_grouped_queries = self.heads // self.kv_heads
        self.dim_head = int(dim_head)
        self.inner_dim_q = self.heads * self.dim_head
        self.inner_dim_kv = self.kv_heads * self.dim_head
        valid_pos_encodings = {"none", "axial_rope", "packed_sequence_rope", "relative_position_bias_3d", "alibi_3d"}
        if pos_encoding not in valid_pos_encodings:
            raise ValueError(f"pos_encoding must be one of {sorted(valid_pos_encodings)}")
        self.pos_encoding = str(pos_encoding)
        self.rotary_base = float(rotary_base)
        valid_rotary_coordinate_modes = {"raw_grid", "normalized_grid", "centered_normalized_grid"}
        if rotary_coordinate_mode not in valid_rotary_coordinate_modes:
            raise ValueError(f"rotary_coordinate_mode must be one of {sorted(valid_rotary_coordinate_modes)}")
        self.rotary_coordinate_mode = str(rotary_coordinate_mode)
        if rotary_axis_scales is None:
            scales = [1.0 for _ in range(self.ndim)]
        else:
            scales = [float(x) for x in rotary_axis_scales]
            if len(scales) != self.ndim:
                raise ValueError(f"rotary_axis_scales must have length {self.ndim}, got {len(scales)}")
        self.register_buffer("rotary_axis_scales", torch.tensor(scales, dtype=torch.float32), persistent=False)
        valid_axis_pair_allocations = {"balanced", "z_light", "z_heavy", "xy_heavy"}
        if rotary_axis_pair_allocation not in valid_axis_pair_allocations:
            raise ValueError(f"rotary_axis_pair_allocation must be one of {sorted(valid_axis_pair_allocations)}")
        self.rotary_axis_pair_allocation = str(rotary_axis_pair_allocation)
        valid_compressed_rope_modes = {"token_before_compression", "summary_center_rope", "compressed_unrotated"}
        if compressed_rope_mode not in valid_compressed_rope_modes:
            raise ValueError(f"compressed_rope_mode must be one of {sorted(valid_compressed_rope_modes)}")
        self.compressed_rope_mode = str(compressed_rope_mode)
        if self.compressed_rope_mode != "token_before_compression" and self.pos_encoding != "axial_rope":
            raise ValueError("compressed_rope_mode ablations are defined only for pos_encoding='axial_rope'")

        self.block_shape = tuple(int(x) for x in block_shape)
        self.num_summary_atoms = int(num_summary_atoms)
        self.num_selected_blocks = int(num_selected_blocks)
        self.residual_weight = float(residual_weight)
        self.distance_weight = float(distance_weight)
        self.micro_order = micro_order
        self.layout = str(layout)
        self.use_triton_kernel = bool(use_triton_kernel)
        self.validate_triton_outputs = bool(validate_triton_outputs)
        self.separate_branch_kv = bool(separate_branch_kv)
        self.packed_branch_kv_projection = bool(packed_branch_kv_projection)
        self.route_select_grad = bool(route_select_grad)
        self.skip_disabled_local_branch = bool(skip_disabled_local_branch)
        self.checkpoint_local_attention = bool(checkpoint_local_attention)
        valid_local_backends = {"torch", "triton"}
        if local_attention_backend not in valid_local_backends:
            raise ValueError(f"local_attention_backend must be one of {sorted(valid_local_backends)}")
        self.local_attention_backend = str(local_attention_backend)
        self.local_attention_block_n = int(local_attention_block_n)
        valid_branch_fusion = {"standard", "sequential", "checkpointed"}
        if branch_output_fusion not in valid_branch_fusion:
            raise ValueError(f"branch_output_fusion must be one of {sorted(valid_branch_fusion)}")
        self.branch_output_fusion = str(branch_output_fusion)
        if coarse_attention_backend not in {"einsum", "sdpa"}:
            raise ValueError("coarse_attention_backend must be one of 'einsum' or 'sdpa'")
        self.coarse_attention_backend = coarse_attention_backend
        self.coarse_summary_pool_size = int(coarse_summary_pool_size)
        if self.coarse_summary_pool_size <= 0:
            raise ValueError("coarse_summary_pool_size must be positive")
        if self.pos_encoding == "relative_position_bias_3d":
            self.relative_position_bias_axes = nn.ParameterList(
                [nn.Parameter(torch.zeros(self.kv_heads, 2 * int(axis_size) - 1)) for axis_size in self.grid_shape]
            )
            for param in self.relative_position_bias_axes:
                nn.init.trunc_normal_(param, std=0.01)
        else:
            self.relative_position_bias_axes = nn.ParameterList()
        if self.pos_encoding == "alibi_3d":
            slopes = torch.pow(2.0, -torch.arange(1, self.kv_heads + 1, dtype=torch.float32) / max(float(self.kv_heads), 1.0))
        else:
            slopes = torch.zeros(self.kv_heads, dtype=torch.float32)
        self.register_buffer("alibi_3d_slopes", slopes, persistent=False)
        self.exclude_own_block_from_selection = bool(exclude_own_block_from_selection)
        valid_route_modes = {
            "logsumexp_logits_current",
            "compressed_attention_mass",
            "log_compressed_attention_mass",
            "mass_times_residual",
            "calibrated_mass_residual",
        }
        if route_score_mode not in valid_route_modes:
            raise ValueError(f"route_score_mode must be one of {sorted(valid_route_modes)}")
        self.route_score_mode = route_score_mode
        valid_route_backends = {"torch_full", "torch_chunked", "triton_streaming", "triton_tile_shared"}
        if route_backend not in valid_route_backends:
            raise ValueError(f"route_backend must be one of {sorted(valid_route_backends)}")
        self.route_backend = route_backend
        self.route_materialize_scores_in_aux = bool(route_materialize_scores_in_aux)
        self.route_block_q = int(route_block_q)
        self.route_block_c = int(route_block_c)
        self.route_shape_penalty_weight = float(route_shape_penalty_weight)
        self.route_center_distance_weight_explicit = route_center_distance_weight is not None
        probability_route_modes = {
            "compressed_attention_mass",
            "log_compressed_attention_mass",
            "mass_times_residual",
            "calibrated_mass_residual",
        }
        if route_center_distance_weight is None and route_score_mode in probability_route_modes:
            # Probability routes live on a different scale from raw squared
            # token-coordinate distances. Keep the legacy distance_weight
            # fallback only for the old logit route.
            route_center_distance_weight = 0.0
        self.route_center_distance_weight = float(distance_weight if route_center_distance_weight is None else route_center_distance_weight)
        valid_distance_normalizations = {"raw", "grid_diagonal_squared", "normalized"}
        if route_distance_normalization not in valid_distance_normalizations:
            raise ValueError(f"route_distance_normalization must be one of {sorted(valid_distance_normalizations)}")
        self.route_distance_normalization = "grid_diagonal_squared" if route_distance_normalization == "normalized" else route_distance_normalization
        self.allow_raw_distance_on_probability_route = bool(allow_raw_distance_on_probability_route)
        if (
            self.route_score_mode == "compressed_attention_mass"
            and self.route_distance_normalization == "raw"
            and self.route_center_distance_weight != 0.0
            and not self.allow_raw_distance_on_probability_route
        ):
            warnings.warn(
                "compressed_attention_mass uses probability-scale route scores but "
                "route_center_distance_weight is applied to raw squared grid distances. "
                "Use route_distance_normalization='grid_diagonal_squared', set "
                "route_center_distance_weight=0, or pass "
                "allow_raw_distance_on_probability_route=True for an intentional diagnostic.",
                UserWarning,
                stacklevel=2,
            )
        valid_gate_modes = {"softmax", "sigmoid", "sigmoid_normalized"}
        if branch_gate_mode not in valid_gate_modes:
            raise ValueError(f"branch_gate_mode must be one of {sorted(valid_gate_modes)}")
        self.branch_gate_mode = str(branch_gate_mode)
        valid_atom_modes = {"current_encode_only", "encode_decode_softmax", "sinkhorn_balanced", "orthogonal_slots", "single_atom"}
        if atom_assignment_mode not in valid_atom_modes:
            raise ValueError(f"atom_assignment_mode must be one of {sorted(valid_atom_modes)}")
        if atom_assignment_mode == "single_atom" and self.num_summary_atoms != 1:
            raise ValueError("atom_assignment_mode='single_atom' requires num_summary_atoms=1")
        self.atom_assignment_mode = atom_assignment_mode
        valid_residual_modes = {
            "none",
            "key_residual",
            "value_residual",
            "key_value_residual",
            "heterogeneity",
            "attention_error_calibrated",
        }
        if route_residual_mode not in valid_residual_modes:
            raise ValueError(f"route_residual_mode must be one of {sorted(valid_residual_modes)}")
        self.route_residual_mode = route_residual_mode
        self.atom_balance_loss_weight = float(atom_balance_loss_weight)
        self.atom_entropy_loss_weight = float(atom_entropy_loss_weight)
        self.atom_orthogonality_loss_weight = float(atom_orthogonality_loss_weight)
        self.atom_temperature = float(atom_temperature)
        valid_execution_modes = {"full", "query_tiled"}
        if full_layer_execution not in valid_execution_modes:
            raise ValueError(f"full_layer_execution must be one of {sorted(valid_execution_modes)}")
        self.full_layer_execution = str(full_layer_execution)
        self.query_tile_size = int(query_tile_size)
        self.query_tile_checkpoint = bool(query_tile_checkpoint)
        valid_route_granularities = {"token_exact", "query_tile_shared", "query_block_shared", "hierarchical_superblock"}
        if route_granularity not in valid_route_granularities:
            raise ValueError(f"route_granularity must be one of {sorted(valid_route_granularities)}")
        self.route_granularity = str(route_granularity)
        self.route_share_tile_size = int(route_share_tile_size)
        valid_branch_output_norms = {"none", "per_branch_rmsnorm"}
        if branch_output_norm not in valid_branch_output_norms:
            raise ValueError(f"branch_output_norm must be one of {sorted(valid_branch_output_norms)}")
        self.branch_output_norm = str(branch_output_norm)
        self.branch_output_norms = nn.ModuleDict()
        if self.branch_output_norm == "per_branch_rmsnorm":
            self.branch_output_norms = nn.ModuleDict(
                {
                    "local": _LastDimRMSNorm(self.dim_head),
                    "compressed": _LastDimRMSNorm(self.dim_head),
                    "selected": _LastDimRMSNorm(self.dim_head),
                }
            )
        self.branch_layer_scale_enabled = bool(branch_layer_scale)
        scale_init = self._parse_branch_layer_scale_init(branch_layer_scale_init)
        if self.branch_layer_scale_enabled:
            self.branch_layer_scale = nn.Parameter(
                torch.tensor(
                    [scale_init["local"], scale_init["compressed"], scale_init["selected"]],
                    dtype=torch.float32,
                ).view(3, 1)
                .expand(3, self.dim_head)
                .clone()
            )
        else:
            self.register_buffer(
                "branch_layer_scale",
                torch.tensor([scale_init["local"], scale_init["compressed"], scale_init["selected"]], dtype=torch.float32).view(3, 1),
                persistent=False,
            )
        valid_branch_mixer_modes = {
            "gated_sum",
            "ungated_sum",
            "local_residual_global",
            "compressed_residual_local",
        }
        if branch_mixer_mode not in valid_branch_mixer_modes:
            raise ValueError(f"branch_mixer_mode must be one of {sorted(valid_branch_mixer_modes)}")
        self.branch_mixer_mode = str(branch_mixer_mode)
        valid_selected_mixing_modes = {"standard", "residual_delta", "compressed_plus_residual"}
        if selected_mixing_mode not in valid_selected_mixing_modes:
            raise ValueError(f"selected_mixing_mode must be one of {sorted(valid_selected_mixing_modes)}")
        self.selected_mixing_mode = str(selected_mixing_mode)
        if enabled_branches is None:
            enabled = {"local", "compressed", "selected"}
        else:
            aliases = {"coarse": "compressed", "cmp": "compressed", "select": "selected"}
            enabled = {aliases.get(str(b).strip().lower(), str(b).strip().lower()) for b in enabled_branches}
        valid_branches = {"local", "compressed", "selected"}
        unknown = sorted(enabled - valid_branches)
        if unknown:
            raise ValueError(f"enabled_branches contains unknown branches: {unknown}")
        if not enabled:
            raise ValueError("enabled_branches must keep at least one output branch active")
        # The selected branch needs compressed summaries for routing, but a
        # no-compressed ablation can still disable the compressed output branch.
        self.enabled_branches = tuple(branch for branch in ("local", "compressed", "selected") if branch in enabled)
        self.enable_local_branch = "local" in enabled
        self.enable_compressed_branch = "compressed" in enabled
        self.enable_selected_branch = "selected" in enabled
        if self.route_granularity == "query_tile_shared" and self.route_share_tile_size <= 0:
            raise ValueError("route_share_tile_size must be positive when route_granularity='query_tile_shared'")
        if self.full_layer_execution == "query_tiled" and self.query_tile_size <= 0:
            raise ValueError("query_tile_size must be positive when full_layer_execution='query_tiled'")
        if self.full_layer_execution == "query_tiled" and (
            self.atom_balance_loss_weight != 0.0
            or self.atom_entropy_loss_weight != 0.0
            or self.atom_orthogonality_loss_weight != 0.0
        ):
            raise ValueError("query_tiled execution currently supports main-path atom losses only when all atom auxiliary loss weights are zero")
        self._last_atom_stats: Dict[str, Tensor] = {}
        self._last_route_stats: dict[str, Tensor] = {}
        grid_diag_sq = float(sum(max(int(g) - 1, 0) ** 2 for g in self.grid_shape))
        self.register_buffer("grid_diagonal_squared", torch.tensor(max(grid_diag_sq, 1.0), dtype=torch.float32), persistent=False)

        layout_data = make_block_layout(self.grid_shape, self.block_shape, layout=self.layout, micro_order=micro_order)
        neighbor_indices, neighbor_mask = build_local_neighbors(
            layout_data["coords_packed"],
            layout_data["valid_token_mask"],
            local_radius,
            layout_data["coord_to_packed_idx"],
        )
        for key, value in layout_data.items():
            if key == "coord_to_packed_idx":
                continue
            if isinstance(value, Tensor):
                self.register_buffer(key, value, persistent=False)
            else:
                setattr(self, key, value)
        self.register_buffer("local_neighbor_indices", neighbor_indices.to(torch.int32), persistent=False)
        self.register_buffer("local_neighbor_mask", neighbor_mask.bool(), persistent=False)
        if self.pos_encoding == "axial_rope":
            axis_pairs = self._allocate_rotary_axis_pairs()
        else:
            axis_pairs = [0 for _ in range(self.ndim)]
        self.rotary_axis_pair_counts_tuple = tuple(int(x) for x in axis_pairs)
        self.register_buffer("rotary_axis_pair_counts", torch.tensor(axis_pairs, dtype=torch.int32), persistent=False)

        self.norm = nn.LayerNorm(dim)
        self.to_q = nn.Linear(dim, self.inner_dim_q, bias=False)
        if self.separate_branch_kv and self.packed_branch_kv_projection:
            self.to_kv_branches = nn.Linear(dim, self.inner_dim_kv * 6, bias=False)
        elif self.separate_branch_kv:
            for branch in ("local", "cmp", "sel"):
                setattr(self, f"to_k_{branch}", nn.Linear(dim, self.inner_dim_kv, bias=False))
                setattr(self, f"to_v_{branch}", nn.Linear(dim, self.inner_dim_kv, bias=False))
        else:
            self.to_k = nn.Linear(dim, self.inner_dim_kv, bias=False)
            self.to_v = nn.Linear(dim, self.inner_dim_kv, bias=False)

        self.atom_logits = nn.Linear(self.dim_head, self.num_summary_atoms, bias=False)
        self.atom_rel_bias = nn.Parameter(torch.zeros(self.block_volume, self.num_summary_atoms))
        nn.init.normal_(self.atom_rel_bias, std=0.02)
        self.log_metric = nn.Parameter(torch.zeros(self.kv_heads, self.ndim))
        self.gate_proj = nn.Linear(dim, self.heads * 3)
        gate_bias_init = self._parse_branch_layer_scale_init(branch_gate_bias_init)
        with torch.no_grad():
            per_head_bias = torch.tensor(
                [
                    gate_bias_init["local"],
                    gate_bias_init["compressed"],
                    gate_bias_init["selected"],
                ],
                dtype=self.gate_proj.bias.dtype,
            )
            self.gate_proj.bias.copy_(per_head_bias.repeat(self.heads))
        self.branch_gate_bias_init = gate_bias_init
        valid_prior_schedules = {"none", "linear", "cosine"}
        if branch_gate_prior_schedule not in valid_prior_schedules:
            raise ValueError(f"branch_gate_prior_schedule must be one of {sorted(valid_prior_schedules)}")
        self.branch_gate_prior_schedule = str(branch_gate_prior_schedule)
        prior_start = self._parse_branch_layer_scale_init(branch_gate_prior_start)
        prior_end = self._parse_branch_layer_scale_init(branch_gate_prior_end)
        self.register_buffer(
            "branch_gate_prior_start_vec",
            torch.tensor([prior_start["local"], prior_start["compressed"], prior_start["selected"]], dtype=torch.float32),
            persistent=False,
        )
        self.register_buffer(
            "branch_gate_prior_end_vec",
            torch.tensor([prior_end["local"], prior_end["compressed"], prior_end["selected"]], dtype=torch.float32),
            persistent=False,
        )
        self.register_buffer("branch_gate_prior_current_vec", torch.zeros(3, dtype=torch.float32), persistent=False)
        self.register_buffer("branch_gate_prior_progress_tensor", torch.zeros((), dtype=torch.float32), persistent=False)
        self.set_branch_gate_prior_progress(0.0)
        self.to_out = nn.Linear(self.inner_dim_q, dim, bias=False)

    @staticmethod
    def _parse_branch_layer_scale_init(value: float | Sequence[float] | Mapping[str, float]) -> dict[str, float]:
        if isinstance(value, Mapping):
            return {
                "local": float(value.get("local", 1.0)),
                "compressed": float(value.get("compressed", value.get("coarse", 1.0))),
                "selected": float(value.get("selected", 1.0)),
            }
        if isinstance(value, (tuple, list)):
            if len(value) != 3:
                raise ValueError("branch_layer_scale_init sequence must contain [local, compressed, selected]")
            return {"local": float(value[0]), "compressed": float(value[1]), "selected": float(value[2])}
        scalar = float(value)
        return {"local": scalar, "compressed": scalar, "selected": scalar}

    def _allocate_rotary_axis_pairs(self) -> list[int]:
        pair_count = self.dim_head // 2
        if pair_count <= 0:
            return [0 for _ in range(self.ndim)]
        if self.ndim != 3 or self.rotary_axis_pair_allocation == "balanced":
            return [pair_count // self.ndim + (1 if axis < (pair_count % self.ndim) else 0) for axis in range(self.ndim)]
        if self.rotary_axis_pair_allocation in {"z_light", "xy_heavy"}:
            weights = torch.tensor([0.25, 0.375, 0.375], dtype=torch.float32)
        elif self.rotary_axis_pair_allocation == "z_heavy":
            weights = torch.tensor([0.50, 0.25, 0.25], dtype=torch.float32)
        else:
            raise RuntimeError(f"unknown rotary_axis_pair_allocation={self.rotary_axis_pair_allocation}")
        raw = weights * float(pair_count)
        base = torch.floor(raw).to(torch.int64)
        remainder = int(pair_count - int(base.sum().item()))
        if remainder > 0:
            frac_order = torch.argsort(raw - base.float(), descending=True)
            for idx in frac_order[:remainder].tolist():
                base[int(idx)] += 1
        return [int(x) for x in base.tolist()]

    def set_branch_gate_prior_progress(self, progress: float) -> None:
        p = float(max(0.0, min(1.0, progress)))
        if self.branch_gate_prior_schedule == "none":
            current = torch.zeros_like(self.branch_gate_prior_current_vec)
            actual = 1.0
        elif self.branch_gate_prior_schedule == "linear":
            actual = p
            current = (1.0 - actual) * self.branch_gate_prior_start_vec + actual * self.branch_gate_prior_end_vec
        elif self.branch_gate_prior_schedule == "cosine":
            actual = 0.5 - 0.5 * math.cos(math.pi * p)
            current = (1.0 - actual) * self.branch_gate_prior_start_vec + actual * self.branch_gate_prior_end_vec
        else:
            raise RuntimeError(f"unknown branch_gate_prior_schedule={self.branch_gate_prior_schedule}")
        self.branch_gate_prior_current_vec.copy_(current.to(self.branch_gate_prior_current_vec.device))
        self.branch_gate_prior_progress_tensor.fill_(actual)

    def _apply_branch_gate_prior(self, gate_logits: Tensor) -> Tensor:
        prior = self.branch_gate_prior_current_vec.to(device=gate_logits.device, dtype=gate_logits.dtype)
        if self.branch_gate_prior_schedule == "none" or bool(torch.all(prior == 0).item()):
            return gate_logits
        return gate_logits + prior.view(1, 1, 1, 3)

    def _mask_branch_logits(self, gate_logits: Tensor, disable_local: Tensor | None) -> Tensor:
        masked = gate_logits
        if not self.enable_local_branch:
            masked = masked.clone()
            masked[..., 0] = -1e9
        elif disable_local is not None:
            local_logits = masked[..., :1].masked_fill(disable_local[:, None, :, None], -1e9)
            masked = torch.cat((local_logits, masked[..., 1:]), dim=-1)
        if not self.enable_compressed_branch:
            masked = masked.clone()
            masked[..., 1] = -1e9
        if not self.enable_selected_branch:
            masked = masked.clone()
            masked[..., 2] = -1e9
        return masked

    def _apply_sigmoid_branch_mask(self, gates: Tensor, disable_local: Tensor | None) -> Tensor:
        if disable_local is not None or not (self.enable_local_branch and self.enable_compressed_branch and self.enable_selected_branch):
            gates = gates.clone()
        if not self.enable_local_branch:
            gates[..., 0] = 0.0
        elif disable_local is not None:
            gates[..., 0] = gates[..., 0].masked_fill(disable_local[:, None, :], 0.0)
        if not self.enable_compressed_branch:
            gates[..., 1] = 0.0
        if not self.enable_selected_branch:
            gates[..., 2] = 0.0
        return gates

    def _empty_selection(
        self,
        batch: int,
        kv_queries: int,
        *,
        device: torch.device,
    ) -> tuple[Tensor, Tensor, Tensor, Tensor, RouteBackendReport]:
        scores = torch.empty(batch, self.kv_heads, kv_queries, 0, device=device)
        selected = torch.empty(batch, self.kv_heads, kv_queries, 0, dtype=torch.long, device=device)
        selected_mask = torch.empty(batch, self.kv_heads, kv_queries, 0, dtype=torch.bool, device=device)
        report = RouteBackendReport(self.route_backend, "skipped", "selected branch disabled")
        return scores, scores, selected, selected_mask, report

    def _pack(self, x: Tensor) -> Tensor:
        return pack_grid(x, self.padded_grid_shape, self.packed_order)

    def _unpack(self, x_packed: Tensor) -> Tensor:
        return unpack_grid(x_packed, self.grid_shape, self.padded_grid_shape, self.packed_order)

    def _pack_bool_mask(self, mask: Tensor) -> Tensor:
        if mask.dim() == self.ndim + 1:
            packed = self._pack(mask.unsqueeze(-1).float()).squeeze(-1)
            return packed > 0.5
        if mask.dim() == 2 and mask.shape[1] == self.num_tokens_padded:
            return mask.bool()
        raise ValueError("query_disable_local_mask must be [B,*grid] or [B,num_tokens_padded]")

    def _split_q(self, x: Tensor) -> Tensor:
        batch, num_tokens, _ = x.shape
        return x.reshape(batch, num_tokens, self.heads, self.dim_head).permute(0, 2, 1, 3).contiguous()

    def _split_kv(self, x: Tensor) -> Tensor:
        batch, num_tokens, _ = x.shape
        return x.reshape(batch, num_tokens, self.kv_heads, self.dim_head).permute(0, 2, 1, 3).contiguous()

    def _merge_heads(self, x: Tensor) -> Tensor:
        batch, heads, num_tokens, dim_head = x.shape
        return x.permute(0, 2, 1, 3).contiguous().reshape(batch, num_tokens, heads * dim_head)

    @staticmethod
    def _branch_tensor_norm(x: Tensor | None, ref: Tensor) -> Tensor:
        if x is None:
            return ref.new_tensor(0.0)
        return x.detach().float().norm(dim=-1).mean().to(device=ref.device)

    def _branch_scale_tensor(self, branch: str, ref: Tensor) -> Tensor:
        idx = {"local": 0, "compressed": 1, "selected": 2}[branch]
        if not self.branch_layer_scale_enabled:
            return ref.new_ones(1, 1, 1, 1)
        return self.branch_layer_scale[idx].to(device=ref.device, dtype=ref.dtype).view(1, 1, 1, self.dim_head)

    def _normalize_branch_output(self, branch: str, value: Tensor | None) -> Tensor | None:
        if value is None:
            return None
        if self.branch_output_norm == "per_branch_rmsnorm":
            return self.branch_output_norms[branch](value)
        return value

    def _prepare_branch_outputs(
        self,
        ref: Tensor,
        *,
        local: Tensor | None = None,
        coarse: Tensor | None = None,
        selected: Tensor | None = None,
    ) -> tuple[Tensor | None, Tensor | None, Tensor | None, Dict[str, Tensor], Dict[str, Tensor], str]:
        raw_norms = {
            "local": self._branch_tensor_norm(local, ref),
            "coarse": self._branch_tensor_norm(coarse, ref),
            "selected": self._branch_tensor_norm(selected, ref),
        }

        local_n = self._normalize_branch_output("local", local)
        coarse_n = self._normalize_branch_output("compressed", coarse)
        selected_n = self._normalize_branch_output("selected", selected)

        local_out = local_n * self._branch_scale_tensor("local", ref) if local_n is not None else None
        coarse_out = coarse_n * self._branch_scale_tensor("compressed", ref) if coarse_n is not None else None

        effective_selected_mode = self.selected_mixing_mode
        if selected_n is None:
            selected_out = None
        elif self.selected_mixing_mode == "standard" or coarse_n is None or coarse_out is None:
            effective_selected_mode = "standard" if coarse_n is None and self.selected_mixing_mode != "standard" else self.selected_mixing_mode
            selected_out = selected_n * self._branch_scale_tensor("selected", ref)
        elif self.selected_mixing_mode == "residual_delta":
            selected_out = (selected_n - coarse_n) * self._branch_scale_tensor("selected", ref)
        elif self.selected_mixing_mode == "compressed_plus_residual":
            selected_out = coarse_out + (selected_n - coarse_n) * self._branch_scale_tensor("selected", ref)
        else:  # guarded by constructor
            raise RuntimeError(f"unknown selected_mixing_mode={self.selected_mixing_mode}")

        post_norms = {
            "local": self._branch_tensor_norm(local_out, ref),
            "coarse": self._branch_tensor_norm(coarse_out, ref),
            "selected": self._branch_tensor_norm(selected_out, ref),
        }
        return local_out, coarse_out, selected_out, raw_norms, post_norms, effective_selected_mode

    @staticmethod
    def _branch_present_weight(gates: Tensor, branch_idx: int) -> Tensor:
        # Disabled branches are represented by an exact zero gate after masking.
        # Active branches get unit weight here so additive mixer modes do not
        # inherit softmax's forced competition between complementary branches.
        return (gates[..., branch_idx : branch_idx + 1] > 0).to(dtype=gates.dtype)

    def _mix_branch_outputs(
        self,
        ref: Tensor,
        gates: Tensor,
        *,
        local: Tensor | None = None,
        coarse: Tensor | None = None,
        selected: Tensor | None = None,
    ) -> tuple[Tensor, str]:
        """Combine prepared branch outputs.

        The default `gated_sum` is the legacy convex/normalized mixture. The
        additive modes are for Window+Global-style models where local and
        compressed branches represent complementary spatial bands rather than
        mutually exclusive experts. Branch masks still come from `gates`, so
        disabled selected/local paths cannot leak through additive modes.
        """
        mixed = ref.new_zeros(ref.shape)
        mode = self.branch_mixer_mode

        local_present = self._branch_present_weight(gates, 0)
        coarse_present = self._branch_present_weight(gates, 1)
        selected_present = self._branch_present_weight(gates, 2)

        if mode == "gated_sum":
            if local is not None:
                mixed = mixed + gates[..., 0].unsqueeze(-1) * local
            if coarse is not None:
                mixed = mixed + gates[..., 1].unsqueeze(-1) * coarse
            if selected is not None:
                mixed = mixed + gates[..., 2].unsqueeze(-1) * selected
            return mixed, mode

        if mode == "ungated_sum":
            if local is not None:
                mixed = mixed + local_present * local
            if coarse is not None:
                mixed = mixed + coarse_present * coarse
            if selected is not None:
                mixed = mixed + selected_present * selected
            return mixed, mode

        if mode == "local_residual_global":
            if local is not None:
                mixed = mixed + local_present * local
            if coarse is not None:
                mixed = mixed + gates[..., 1].unsqueeze(-1) * coarse
            if selected is not None:
                mixed = mixed + gates[..., 2].unsqueeze(-1) * selected
            return mixed, mode

        if mode == "compressed_residual_local":
            if local is not None:
                mixed = mixed + gates[..., 0].unsqueeze(-1) * local
            if coarse is not None:
                mixed = mixed + coarse_present * coarse
            if selected is not None:
                mixed = mixed + gates[..., 2].unsqueeze(-1) * selected
            return mixed, mode

        raise RuntimeError(f"unknown branch_mixer_mode={mode}")

    def _format_axial_rope_coords(self, coords: Tensor, *, packed_sequence: bool = False) -> Tensor:
        coords_f = coords.to(dtype=torch.float32)
        if packed_sequence:
            return coords_f
        if self.rotary_coordinate_mode == "normalized_grid":
            denom = torch.tensor(
                [max(int(g) - 1, 1) for g in self.grid_shape],
                device=coords.device,
                dtype=torch.float32,
            )
            coords_f = coords_f / denom.view(1, self.ndim)
        elif self.rotary_coordinate_mode == "centered_normalized_grid":
            denom = torch.tensor(
                [max(int(g) - 1, 1) for g in self.grid_shape],
                device=coords.device,
                dtype=torch.float32,
            )
            coords_f = (coords_f / denom.view(1, self.ndim)) * 2.0 - 1.0
        elif self.rotary_coordinate_mode != "raw_grid":
            raise RuntimeError(f"unknown rotary_coordinate_mode={self.rotary_coordinate_mode}")
        return coords_f * self.rotary_axis_scales.to(device=coords.device, dtype=torch.float32).view(1, self.ndim)

    def _apply_axial_rope(self, t: Tensor, coords: Tensor | None = None) -> Tensor:
        """Apply 3D/ND RoPE to packed attention tensors.

        The repo-level ``rotary_embedding_torch.py`` implements the standard
        RoPE rotation. HyperNSA packs tokens in block/raster layouts, so the
        same unitary pairwise rotation must be indexed by packed grid
        coordinates instead of by raw sequence position.
        """
        if self.pos_encoding not in {"axial_rope", "packed_sequence_rope"}:
            return t
        if self.pos_encoding == "packed_sequence_rope":
            seq = torch.arange(t.shape[2], device=t.device, dtype=torch.long)
            zeros = torch.zeros_like(seq)
            coord_cols = [seq, zeros, zeros]
            while len(coord_cols) < self.ndim:
                coord_cols.append(zeros)
            coords_t = torch.stack(coord_cols[: self.ndim], dim=1)
            packed_sequence = True
        else:
            coords_t = self.coords_packed if coords is None else coords
            packed_sequence = False
        if coords_t.shape[0] != t.shape[2]:
            raise ValueError(f"RoPE coords length {coords_t.shape[0]} does not match token length {t.shape[2]}")
        axis_pairs = self.rotary_axis_pair_counts_tuple
        if not any(axis_pairs):
            return t
        coords_f = self._format_axial_rope_coords(coords_t.to(device=t.device), packed_sequence=packed_sequence)
        pieces: list[Tensor] = []
        offset = 0
        for axis, pairs in enumerate(axis_pairs):
            pairs_i = int(pairs)
            if pairs_i <= 0:
                continue
            width = 2 * pairs_i
            chunk = t[..., offset : offset + width]
            chunk_f = chunk.float().reshape(*chunk.shape[:-1], pairs_i, 2)
            inv_freq = 1.0 / (
                self.rotary_base
                ** (torch.arange(pairs_i, device=t.device, dtype=torch.float32) / max(float(pairs_i), 1.0))
            )
            angle = coords_f[:, axis : axis + 1] * inv_freq.view(1, pairs_i)
            cos = angle.cos().view(1, 1, -1, pairs_i)
            sin = angle.sin().view(1, 1, -1, pairs_i)
            x0 = chunk_f[..., 0]
            x1 = chunk_f[..., 1]
            rotated = torch.stack((x0 * cos - x1 * sin, x0 * sin + x1 * cos), dim=-1).flatten(-2)
            pieces.append(rotated.to(dtype=t.dtype))
            offset += width
        if offset < t.shape[-1]:
            pieces.append(t[..., offset:])
        return torch.cat(pieces, dim=-1)

    def _branch_uses_rope(self, branch: str) -> bool:
        if self.pos_encoding not in {"axial_rope", "packed_sequence_rope"}:
            return False
        if branch == "cmp" and self.compressed_rope_mode in {"summary_center_rope", "compressed_unrotated"}:
            return False
        return True

    def _apply_branch_rope(self, k: Tensor, branch: str, coords: Tensor | None = None) -> Tensor:
        return self._apply_axial_rope(k, coords) if self._branch_uses_rope(branch) else k

    def _compressed_query(self, q_rope: Tensor, q_unrotated: Tensor) -> Tensor:
        return q_unrotated if self.compressed_rope_mode == "compressed_unrotated" else q_rope

    def _project_kv(self, x: Tensor, branch: str, coords: Tensor | None = None) -> tuple[Tensor, Tensor]:
        if self.separate_branch_kv:
            if self.packed_branch_kv_projection:
                raise RuntimeError("_project_kv is not used with packed_branch_kv_projection=True")
            k = self._split_kv(getattr(self, f"to_k_{branch}")(x))
            v = self._split_kv(getattr(self, f"to_v_{branch}")(x))
            return self._apply_branch_rope(k, branch, coords), v
        k = self._split_kv(self.to_k(x))
        v = self._split_kv(self.to_v(x))
        return self._apply_branch_rope(k, branch, coords), v

    def _project_kv_branch_tokens(self, x: Tensor, branch: str, coords: Tensor | None = None) -> tuple[Tensor, Tensor]:
        """Project one branch K/V stream for an arbitrary token slice.

        Packed branch projection is kept as a parameter packing optimization,
        but tiled execution must not call the packed layer over all six branch
        streams when it only needs one branch.
        """
        if branch not in {"local", "cmp", "sel"}:
            raise ValueError(f"unknown branch={branch}")
        if self.separate_branch_kv and self.packed_branch_kv_projection:
            chunk = {"local": 0, "cmp": 2, "sel": 4}[branch]
            k0 = chunk * self.inner_dim_kv
            v0 = (chunk + 1) * self.inner_dim_kv
            weight = self.to_kv_branches.weight
            k = F.linear(x, weight[k0 : k0 + self.inner_dim_kv])
            v = F.linear(x, weight[v0 : v0 + self.inner_dim_kv])
            k_split = self._split_kv(k)
            v_split = self._split_kv(v)
            if coords is None and x.shape[1] == self.num_tokens_padded:
                coords = self.coords_packed
            return self._apply_branch_rope(k_split, branch, coords), v_split
        if self.separate_branch_kv:
            if coords is None and x.shape[1] == self.num_tokens_padded:
                coords = self.coords_packed
            return self._project_kv(x, branch, coords=coords)
        k_shared, v_shared = self._split_kv(self.to_k(x)), self._split_kv(self.to_v(x))
        if coords is None and x.shape[1] == self.num_tokens_padded:
            coords = self.coords_packed
        return self._apply_branch_rope(k_shared, branch, coords), v_shared

    def _project_all_kv(
        self,
        x: Tensor,
        *,
        need_local: bool = True,
        need_selected: bool = True,
    ) -> tuple[tuple[Tensor | None, Tensor | None], tuple[Tensor, Tensor], tuple[Tensor | None, Tensor | None]]:
        if self.separate_branch_kv and self.packed_branch_kv_projection:
            if not (need_local and need_selected):
                local = self._project_kv_branch_tokens(x, "local") if need_local else (None, None)
                selected = self._project_kv_branch_tokens(x, "sel") if need_selected else (None, None)
                return local, self._project_kv_branch_tokens(x, "cmp"), selected
            chunks = self.to_kv_branches(x).chunk(6, dim=-1)
            k_local, v_local, k_cmp, v_cmp, k_sel, v_sel = (self._split_kv(chunk) for chunk in chunks)
            coords = self.coords_packed if x.shape[1] == self.num_tokens_padded else None
            k_local = self._apply_branch_rope(k_local, "local", coords)
            k_cmp = self._apply_branch_rope(k_cmp, "cmp", coords)
            k_sel = self._apply_branch_rope(k_sel, "sel", coords)
            return (k_local if need_local else None, v_local if need_local else None), (k_cmp, v_cmp), (k_sel, v_sel)
        if self.separate_branch_kv:
            coords = self.coords_packed if x.shape[1] == self.num_tokens_padded else None
            local = self._project_kv(x, "local", coords=coords) if need_local else (None, None)
            selected = self._project_kv(x, "sel", coords=coords) if need_selected else (None, None)
            return local, self._project_kv(x, "cmp", coords=coords), selected
        k_shared, v_shared = self._split_kv(self.to_k(x)), self._split_kv(self.to_v(x))
        coords = self.coords_packed if x.shape[1] == self.num_tokens_padded else None
        k_shared = self._apply_axial_rope(k_shared, coords)
        local = (k_shared, v_shared) if need_local else (None, None)
        selected = (k_shared, v_shared) if need_selected else (None, None)
        return local, (k_shared, v_shared), selected

    def _gather_blocks(self, t: Tensor) -> Tensor:
        return t[:, :, self.block_token_indices.to(t.device), :]

    @property
    def route_distance_units(self) -> str:
        if self.route_distance_normalization == "grid_diagonal_squared":
            return "squared_grid_distance_div_grid_diagonal_squared"
        return "raw_squared_grid_distance"

    def _effective_triton_route_center_distance_weight(self) -> float:
        if self.route_distance_normalization == "grid_diagonal_squared":
            return float(self.route_center_distance_weight / float(self.grid_diagonal_squared.item()))
        return float(self.route_center_distance_weight)

    def _distance_values(self, *, start: int | None = None, end: int | None = None, device: torch.device | None = None) -> Tensor:
        device = device or self.coords_packed.device
        coords = self.coords_packed.to(device)
        centers = self.block_centers[slice(start, end)].to(device) if start is not None or end is not None else self.block_centers.to(device)
        diff = coords[:, None, :] - centers[None, :, :]
        metric = self.log_metric.exp().to(device)[:, None, None, :]
        dist = (diff[None] ** 2 * metric).sum(dim=-1)
        if self.route_distance_normalization == "grid_diagonal_squared":
            dist = dist / self.grid_diagonal_squared.to(device).clamp_min(1.0)
        return dist

    def _distance_bias(self) -> Tensor:
        dist = self._distance_values()
        return -self.route_center_distance_weight * dist

    def _distance_bias_for_queries(
        self,
        q_start: int,
        q_end: int,
        *,
        block_start: int | None = None,
        block_end: int | None = None,
        device: torch.device,
    ) -> Tensor:
        coords = self.coords_packed[q_start:q_end].to(device)
        centers = self.block_centers[slice(block_start, block_end)].to(device) if block_start is not None or block_end is not None else self.block_centers.to(device)
        diff = coords[:, None, :] - centers[None, :, :]
        metric = self.log_metric.exp().to(device)[:, None, None, :]
        dist = (diff[None] ** 2 * metric).sum(dim=-1)
        if self.route_distance_normalization == "grid_diagonal_squared":
            dist = dist / self.grid_diagonal_squared.to(device).clamp_min(1.0)
        return -self.route_center_distance_weight * dist

    def _distance_bias_for_coords(
        self,
        coords: Tensor,
        *,
        block_start: int | None = None,
        block_end: int | None = None,
        device: torch.device,
    ) -> Tensor:
        coords = coords.to(device)
        centers = self.block_centers[slice(block_start, block_end)].to(device) if block_start is not None or block_end is not None else self.block_centers.to(device)
        diff = coords[:, None, :] - centers[None, :, :]
        metric = self.log_metric.exp().to(device)[:, None, None, :]
        dist = (diff[None] ** 2 * metric).sum(dim=-1)
        if self.route_distance_normalization == "grid_diagonal_squared":
            dist = dist / self.grid_diagonal_squared.to(device).clamp_min(1.0)
        return -self.route_center_distance_weight * dist

    def _local_attention_torch(
        self,
        q: Tensor,
        k: Tensor,
        v: Tensor,
        neighbor_indices: Tensor | None = None,
        neighbor_mask: Tensor | None = None,
    ) -> Tensor:
        batch = q.shape[0]
        num_queries = q.shape[2]
        q_grouped = q.reshape(batch, self.kv_heads, self.num_grouped_queries, num_queries, self.dim_head)
        b_idx = torch.arange(batch, device=q.device)[:, None, None, None]
        g_idx = torch.arange(self.kv_heads, device=q.device)[None, :, None, None]
        neighbor = self.local_neighbor_indices if neighbor_indices is None else neighbor_indices
        mask_t = self.local_neighbor_mask if neighbor_mask is None else neighbor_mask
        neighbor_idx = neighbor.to(q.device).long()[None, None, :, :]
        local_k = k[b_idx, g_idx, neighbor_idx, :]
        local_v = v[b_idx, g_idx, neighbor_idx, :]
        sim = torch.einsum("bgqnd,bgnwd->bgqnw", q_grouped, local_k) * (self.dim_head**-0.5)
        mask = mask_t.to(q.device).view(1, 1, 1, num_queries, -1)
        sim = sim.masked_fill(~mask, torch.finfo(sim.dtype).min)
        attn = sim.softmax(dim=-1)
        out = torch.einsum("bgqnw,bgnwd->bgqnd", attn, local_v)
        return out.reshape(batch, self.heads, num_queries, self.dim_head)

    def _compute_atom_stats(self, decode: Tensor, summary_k: Tensor, valid: Tensor) -> Dict[str, Tensor]:
        zero = summary_k.new_tensor(0.0)
        if self.num_summary_atoms <= 1:
            return {
                "atom_aux_loss": zero,
                "atom_balance_loss": zero,
                "atom_entropy_loss": zero,
                "atom_orthogonality_loss": zero,
                "atom_assignment_entropy_mean": zero,
                "atom_effective_count": zero + 1.0,
                "atom_balance_mean": zero + 1.0,
                "atom_cosine_abs_offdiag": zero,
            }

        valid_f = valid.to(decode.dtype)
        valid_tokens = valid_f.sum(dim=-2).clamp_min(1.0)
        responsibilities = decode * valid_f
        atom_mass = responsibilities.sum(dim=-2) / valid_tokens
        target_mass = decode.new_full((), 1.0 / float(self.num_summary_atoms))
        balance_loss = (atom_mass - target_mass).square().mean()

        log_r = math.log(float(self.num_summary_atoms))
        token_entropy = -(decode.clamp_min(1e-8).log() * decode * valid_f).sum(dim=-1, keepdim=True)
        entropy_denom = valid_f.expand_as(token_entropy).sum().clamp_min(1.0)
        entropy_mean = token_entropy.sum() / entropy_denom
        entropy_loss = entropy_mean / max(log_r, 1e-6)
        effective_count = torch.exp(entropy_mean)

        normalized = F.normalize(summary_k.float(), dim=-1)
        cosine = torch.einsum("bgcrd,bgcsd->bgcrs", normalized, normalized)
        eye = torch.eye(self.num_summary_atoms, device=cosine.device, dtype=torch.bool).view(
            1, 1, 1, self.num_summary_atoms, self.num_summary_atoms
        )
        offdiag = cosine.masked_select((~eye).expand_as(cosine))
        if offdiag.numel() == 0:
            orthogonality_loss = zero
            offdiag_abs = zero
        else:
            orthogonality_loss = offdiag.square().mean().to(summary_k.dtype)
            offdiag_abs = offdiag.abs().mean().to(summary_k.dtype)

        weighted_loss = (
            self.atom_balance_loss_weight * balance_loss
            + self.atom_entropy_loss_weight * entropy_loss
            + self.atom_orthogonality_loss_weight * orthogonality_loss
        )
        return {
            "atom_aux_loss": weighted_loss.to(summary_k.dtype),
            "atom_balance_loss": balance_loss.to(summary_k.dtype),
            "atom_entropy_loss": entropy_loss.to(summary_k.dtype),
            "atom_orthogonality_loss": orthogonality_loss.to(summary_k.dtype),
            "atom_assignment_entropy_mean": entropy_mean.to(summary_k.dtype),
            "atom_effective_count": effective_count.to(summary_k.dtype),
            "atom_balance_mean": atom_mass.max(dim=-1).values.mean().to(summary_k.dtype),
            "atom_cosine_abs_offdiag": offdiag_abs.to(summary_k.dtype),
        }

    def _compute_compression_from_blocks(
        self,
        k_blocks: Tensor,
        v_blocks: Tensor,
        valid: Tensor,
    ) -> tuple[Tensor, Tensor, Tensor, Tensor, Dict[str, Tensor]]:
        logits = self.atom_logits(k_blocks) / max(self.atom_temperature, 1e-6)
        logits = logits + self.atom_rel_bias.to(k_blocks.device).view(1, 1, 1, self.block_volume, self.num_summary_atoms)
        logits = logits.masked_fill(~valid, torch.finfo(logits.dtype).min)
        if self.atom_assignment_mode == "single_atom":
            encode = logits.softmax(dim=-2) * valid
            encode = encode / encode.sum(dim=-2, keepdim=True).clamp_min(1e-6)
            # One atom decodes every valid token from the same block summary.
            # Reusing token-normalized encode weights here would reconstruct
            # each token as encode[u] * summary instead of summary, inflating
            # the R=1 compression residual by construction.
            decode = valid.to(logits.dtype).expand_as(encode)
        elif self.atom_assignment_mode == "current_encode_only":
            encode = logits.softmax(dim=-2) * valid
            encode = encode / encode.sum(dim=-2, keepdim=True).clamp_min(1e-6)
            decode = encode
        else:
            encode = logits.softmax(dim=-2) * valid
            encode = encode / encode.sum(dim=-2, keepdim=True).clamp_min(1e-6)
            decode_logits = logits.masked_fill(~valid, -1e9)
            decode = decode_logits.softmax(dim=-1) * valid
            decode = decode / decode.sum(dim=-1, keepdim=True).clamp_min(1e-6)
            if self.atom_assignment_mode == "sinkhorn_balanced":
                for _ in range(2):
                    decode = decode / decode.sum(dim=-1, keepdim=True).clamp_min(1e-6)
                    decode = decode / decode.sum(dim=-2, keepdim=True).clamp_min(1e-6)
                decode = decode * valid
                decode = decode / decode.sum(dim=-1, keepdim=True).clamp_min(1e-6)
            elif self.atom_assignment_mode == "orthogonal_slots":
                # The slot logits provide the orthogonalization pressure during training;
                # inference uses the same normalized encode/decode responsibilities.
                pass
        summary_k = torch.einsum("bgcvr,bgcvd->bgcrd", encode, k_blocks)
        summary_v = torch.einsum("bgcvr,bgcvd->bgcrd", encode, v_blocks)
        recon = torch.einsum("bgcvr,bgcrd->bgcvd", decode, summary_k)
        sqerr = ((k_blocks - recon) ** 2) * valid
        denom = valid.sum(dim=(-2, -1)).clamp_min(1.0)
        residual_energy = sqerr.sum(dim=(-2, -1)) / denom
        compression_residual = torch.log1p(residual_energy)
        atom_stats = self._compute_atom_stats(decode, summary_k, valid)
        return summary_k, summary_v, compression_residual, decode, atom_stats

    def _compute_compression(self, k_cmp: Tensor, v_cmp: Tensor) -> tuple[Tensor, Tensor, Tensor, Tensor]:
        k_blocks = self._gather_blocks(k_cmp)
        v_blocks = self._gather_blocks(v_cmp)
        valid = self.block_valid_mask.to(k_cmp.device).view(1, 1, self.num_blocks, self.block_volume, 1)
        summary_k, summary_v, compression_residual, decode, stats = self._compute_compression_from_blocks(k_blocks, v_blocks, valid)
        self._last_atom_stats = stats
        return summary_k, summary_v, compression_residual, decode

    def _compute_compression_from_tokens_tiled(self, x: Tensor, *, block_chunk: int | None = None) -> tuple[Tensor, Tensor, Tensor, Tensor]:
        chunk = int(block_chunk or self.route_block_c)
        chunk = max(1, min(chunk, self.num_blocks))
        batch = x.shape[0]
        device = x.device
        dtype = x.dtype
        summary_k_parts: list[Tensor] = []
        summary_v_parts: list[Tensor] = []
        residual_parts: list[Tensor] = []
        decode_parts: list[Tensor] = []
        stats_acc: dict[str, Tensor] = {}
        stats_count = 0
        token_indices_all = self.block_token_indices.to(device)
        valid_all = self.block_valid_mask.to(device).view(1, 1, self.num_blocks, self.block_volume, 1)
        for start in range(0, self.num_blocks, chunk):
            end = min(start + chunk, self.num_blocks)
            token_idx = token_indices_all[start:end].reshape(-1)
            x_blocks = x.index_select(1, token_idx).reshape(batch, end - start, self.block_volume, self.dim)
            flat = x_blocks.reshape(batch, (end - start) * self.block_volume, self.dim)
            coords = self.coords_packed.to(device).index_select(0, token_idx)
            k_cmp, v_cmp = self._project_kv_branch_tokens(flat, "cmp", coords=coords)
            k_blocks = k_cmp.reshape(batch, self.kv_heads, end - start, self.block_volume, self.dim_head)
            v_blocks = v_cmp.reshape(batch, self.kv_heads, end - start, self.block_volume, self.dim_head)
            valid = valid_all[:, :, start:end]
            summary_k, summary_v, residual, decode, stats = self._compute_compression_from_blocks(k_blocks, v_blocks, valid)
            summary_k_parts.append(summary_k)
            summary_v_parts.append(summary_v)
            residual_parts.append(residual)
            decode_parts.append(decode)
            for key, value in stats.items():
                stats_acc[key] = stats_acc.get(key, torch.zeros((), device=device, dtype=value.dtype)) + value.detach()
            stats_count += 1
        if stats_count:
            self._last_atom_stats = {key: value / stats_count for key, value in stats_acc.items()}
        else:
            zero = torch.zeros((), device=device, dtype=dtype)
            self._last_atom_stats = {"atom_aux_loss": zero}
        return (
            torch.cat(summary_k_parts, dim=2),
            torch.cat(summary_v_parts, dim=2),
            torch.cat(residual_parts, dim=2),
            torch.cat(decode_parts, dim=2),
        )

    def _route_residual_term(self, compression_residual: Tensor) -> Tensor:
        if self.route_residual_mode == "none":
            return torch.zeros_like(compression_residual)
        if self.route_residual_mode == "heterogeneity" and hasattr(self, "block_cov_trace"):
            geom = self.block_cov_trace.to(compression_residual.device).view(1, 1, self.num_blocks)
            geom = (geom - geom.mean(dim=-1, keepdim=True)) / geom.std(dim=-1, keepdim=True).clamp_min(1e-6)
            return geom.expand_as(compression_residual)
        return compression_residual

    def _compressed_block_probability(self, sim_atoms: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        batch = sim_atoms.shape[0]
        num_queries = sim_atoms.shape[3]
        flat = sim_atoms.reshape(batch, self.kv_heads, self.num_grouped_queries, num_queries, self.num_blocks * self.num_summary_atoms)
        probs = flat.float().softmax(dim=-1).reshape(
            batch,
            self.kv_heads,
            self.num_grouped_queries,
            num_queries,
            self.num_blocks,
            self.num_summary_atoms,
        )
        block_probs_per_head = probs.sum(dim=-1)
        block_probs = block_probs_per_head.mean(dim=2)
        entropy = -(block_probs * block_probs.clamp_min(1e-12).log()).sum(dim=-1).mean()
        sum_error = (block_probs.sum(dim=-1) - 1.0).abs().mean()
        return block_probs, entropy, sum_error

    def _pool_coarse_summaries(self, summary_k: Tensor, summary_v: Tensor) -> tuple[Tensor, Tensor]:
        """Optionally coarsen global branch summaries for large-context runs.

        This affects only the compressed/global output branch. The route and
        selected-refinement paths keep the original per-block summaries.
        """
        pool = int(self.coarse_summary_pool_size)
        if pool == 1:
            return summary_k, summary_v
        num_blocks = summary_k.shape[2]
        pad = (-num_blocks) % pool
        block_valid = self.block_valid_mask.to(device=summary_k.device).any(dim=-1).to(dtype=summary_k.dtype)
        if pad:
            summary_k = F.pad(summary_k, (0, 0, 0, 0, 0, pad))
            summary_v = F.pad(summary_v, (0, 0, 0, 0, 0, pad))
            block_valid = F.pad(block_valid, (0, pad))
        pooled_blocks = summary_k.shape[2] // pool
        counts = block_valid.reshape(pooled_blocks, pool).sum(dim=1)
        keep = counts > 0
        denom = counts.clamp_min(1.0).view(1, 1, pooled_blocks, 1, 1)
        weights = block_valid.reshape(1, 1, pooled_blocks, pool, 1, 1)
        k = (summary_k.reshape(summary_k.shape[0], summary_k.shape[1], pooled_blocks, pool, self.num_summary_atoms, self.dim_head) * weights).sum(dim=3) / denom
        v = (summary_v.reshape(summary_v.shape[0], summary_v.shape[1], pooled_blocks, pool, self.num_summary_atoms, self.dim_head) * weights).sum(dim=3) / denom
        return k[:, :, keep], v[:, :, keep]

    def _pooled_coarse_coords(self, device: torch.device) -> Tensor:
        pool = int(self.coarse_summary_pool_size)
        centers = self.block_centers.to(device=device, dtype=torch.float32)
        block_valid = self.block_valid_mask.to(device=device).any(dim=-1).to(dtype=torch.float32)
        if pool == 1:
            keep = block_valid > 0
            return centers[keep]
        num_blocks = centers.shape[0]
        pad = (-num_blocks) % pool
        if pad:
            centers = F.pad(centers, (0, 0, 0, pad))
            block_valid = F.pad(block_valid, (0, pad))
        pooled_blocks = centers.shape[0] // pool
        counts = block_valid.reshape(pooled_blocks, pool).sum(dim=1)
        keep = counts > 0
        weights = block_valid.reshape(pooled_blocks, pool, 1)
        pooled = (centers.reshape(pooled_blocks, pool, self.ndim) * weights).sum(dim=1) / counts.clamp_min(1.0).view(-1, 1)
        return pooled[keep]

    def _coarse_position_bias(self, q: Tensor, num_summary: int) -> Tensor | None:
        if self.pos_encoding not in {"relative_position_bias_3d", "alibi_3d"}:
            return None
        if q.shape[2] != self.num_tokens_padded:
            raise RuntimeError(f"{self.pos_encoding} currently expects full-layer compressed attention, got q={q.shape[2]}")
        bias_elements = int(self.kv_heads) * int(q.shape[2]) * int(num_summary)
        if bias_elements > 256_000_000:
            raise RuntimeError(
                f"{self.pos_encoding} would materialize {bias_elements:,} compressed-branch bias elements. "
                "This reviewer-control needs a bias-aware streaming compressed-attention kernel at this token count; "
                "use axial_rope/packed_sequence_rope for kernel-compatible 262k controls."
            )
        q_coords = self.coords_packed.to(device=q.device, dtype=torch.float32)
        coarse_coords = self._pooled_coarse_coords(q.device)
        if self.num_summary_atoms > 1:
            coarse_coords = coarse_coords[:, None, :].expand(-1, self.num_summary_atoms, -1).reshape(-1, self.ndim)
        if coarse_coords.shape[0] != num_summary:
            raise RuntimeError(f"coarse coord count {coarse_coords.shape[0]} does not match summaries {num_summary}")
        delta = coarse_coords[None, :, :] - q_coords[:, None, :]
        if self.pos_encoding == "alibi_3d":
            denom = torch.tensor(self.grid_shape, device=q.device, dtype=torch.float32).clamp_min(1.0).view(1, 1, self.ndim)
            dist = (delta.abs() / denom).sum(dim=-1)
            return -self.alibi_3d_slopes.to(device=q.device, dtype=q.dtype).view(self.kv_heads, 1, 1) * dist.to(dtype=q.dtype).view(
                1,
                q.shape[2],
                num_summary,
            )
        bias = q.new_zeros(self.kv_heads, q.shape[2], num_summary)
        for axis, table in enumerate(self.relative_position_bias_axes):
            max_offset = int(self.grid_shape[axis]) - 1
            idx = delta[..., axis].round().long().clamp(-max_offset, max_offset) + max_offset
            bias = bias + table.to(device=q.device, dtype=q.dtype)[:, idx]
        return bias

    def _coarse_attention_torch(self, q: Tensor, summary_k: Tensor, summary_v: Tensor) -> Tensor:
        batch = q.shape[0]
        num_queries = q.shape[2]
        q_grouped = q.reshape(batch, self.kv_heads, self.num_grouped_queries, num_queries, self.dim_head)
        summary_k, summary_v = self._pool_coarse_summaries(summary_k, summary_v)
        num_coarse_blocks = summary_k.shape[2]
        coarse_k = summary_k.reshape(batch, self.kv_heads, num_coarse_blocks * self.num_summary_atoms, self.dim_head)
        coarse_v = summary_v.reshape(batch, self.kv_heads, num_coarse_blocks * self.num_summary_atoms, self.dim_head)
        if self.compressed_rope_mode == "summary_center_rope":
            coarse_coords = self._pooled_coarse_coords(q.device)
            if self.num_summary_atoms > 1:
                coarse_coords = coarse_coords[:, None, :].expand(-1, self.num_summary_atoms, -1).reshape(-1, self.ndim)
            if coarse_coords.shape[0] != coarse_k.shape[2]:
                raise RuntimeError(f"coarse coord count {coarse_coords.shape[0]} does not match summaries {coarse_k.shape[2]}")
            coarse_k = self._apply_axial_rope(coarse_k, coarse_coords)
        position_bias = self._coarse_position_bias(q, coarse_k.shape[2])
        if self.coarse_attention_backend == "sdpa" and position_bias is None:
            num_summary = coarse_k.shape[2]
            q_flat = q_grouped.reshape(batch * self.kv_heads * self.num_grouped_queries, num_queries, self.dim_head)
            k_flat = (
                coarse_k[:, :, None, :, :]
                .expand(batch, self.kv_heads, self.num_grouped_queries, num_summary, self.dim_head)
                .reshape(batch * self.kv_heads * self.num_grouped_queries, num_summary, self.dim_head)
            )
            v_flat = (
                coarse_v[:, :, None, :, :]
                .expand(batch, self.kv_heads, self.num_grouped_queries, num_summary, self.dim_head)
                .reshape(batch * self.kv_heads * self.num_grouped_queries, num_summary, self.dim_head)
            )
            out = F.scaled_dot_product_attention(
                q_flat[:, None, :, :],
                k_flat[:, None, :, :],
                v_flat[:, None, :, :],
                dropout_p=0.0,
                is_causal=False,
            )
            return out[:, 0].reshape(batch, self.kv_heads, self.num_grouped_queries, num_queries, self.dim_head).reshape(
                batch,
                self.heads,
                num_queries,
                self.dim_head,
            )
        sim = torch.einsum("bgqnd,bgmd->bgqnm", q_grouped, coarse_k) * (self.dim_head**-0.5)
        if position_bias is not None:
            sim = sim + position_bias.view(1, self.kv_heads, 1, num_queries, coarse_k.shape[2])
        attn = sim.softmax(dim=-1)
        out = torch.einsum("bgqnm,bgmd->bgqnd", attn, coarse_v)
        return out.reshape(batch, self.heads, num_queries, self.dim_head)

    def _route_blocks_torch_full(self, q: Tensor, summary_k: Tensor, compression_residual: Tensor) -> tuple[Tensor, Tensor, Tensor, Tensor]:
        batch = q.shape[0]
        q_grouped = q.reshape(batch, self.kv_heads, self.num_grouped_queries, self.num_tokens_padded, self.dim_head)
        sim_atoms = torch.einsum("bgqnd,bgcrd->bgqncr", q_grouped, summary_k) * (self.dim_head**-0.5)
        route_probability_sum_error = q.new_tensor(0.0)
        compressed_mass_entropy = q.new_tensor(0.0)
        block_probability = None
        if self.route_score_mode == "logsumexp_logits_current":
            route_relevance = torch.logsumexp(sim_atoms, dim=-1).mean(dim=2)
        else:
            block_probability, compressed_mass_entropy, route_probability_sum_error = self._compressed_block_probability(sim_atoms)
            if self.route_score_mode == "compressed_attention_mass":
                route_relevance = block_probability
            elif self.route_score_mode == "log_compressed_attention_mass":
                route_relevance = block_probability.clamp_min(1e-12).log()
            elif self.route_score_mode == "mass_times_residual":
                residual_term = self._route_residual_term(compression_residual).unsqueeze(2)
                route_relevance = block_probability * (1.0 + self.residual_weight * residual_term)
            elif self.route_score_mode == "calibrated_mass_residual":
                residual_term = self._route_residual_term(compression_residual)
                residual_term = (residual_term - residual_term.mean(dim=-1, keepdim=True)) / residual_term.std(dim=-1, keepdim=True).clamp_min(1e-6)
                route_relevance = block_probability.clamp_min(1e-12).log() + self.residual_weight * residual_term.unsqueeze(2)
            else:
                raise RuntimeError(f"unhandled route_score_mode={self.route_score_mode}")
        residual_for_route = self._route_residual_term(compression_residual)
        route_scores = (
            route_relevance
            + self._distance_bias().to(q.device).unsqueeze(0)
        )
        if self.route_score_mode not in {"mass_times_residual", "calibrated_mass_residual"}:
            route_scores = route_scores + self.residual_weight * residual_for_route.unsqueeze(2)
        if self.route_shape_penalty_weight != 0.0 and hasattr(self, "block_cov_trace"):
            shape = self.block_cov_trace.to(q.device)
            shape = shape / shape.mean().clamp_min(1e-6)
            route_scores = route_scores - self.route_shape_penalty_weight * shape.view(1, 1, 1, self.num_blocks)
        block_range = torch.arange(self.num_blocks, device=q.device).view(1, 1, 1, self.num_blocks)
        if self.exclude_own_block_from_selection:
            own_block = self.block_id_packed.to(q.device).view(1, 1, self.num_tokens_padded, 1)
            route_scores = route_scores.masked_fill(block_range == own_block, -1e9)
            max_selectable = max(self.num_blocks - 1, 0)
        else:
            max_selectable = self.num_blocks
        valid_query = self.valid_token_mask.to(q.device).view(1, 1, self.num_tokens_padded, 1)
        route_scores = route_scores.masked_fill(~valid_query, -1e9)
        num_selected = min(self.num_selected_blocks, max_selectable)
        if num_selected == 0:
            selected = torch.empty(batch, self.kv_heads, self.num_tokens_padded, 0, dtype=torch.long, device=q.device)
            selected_mask = torch.empty(batch, self.kv_heads, self.num_tokens_padded, 0, dtype=torch.bool, device=q.device)
        else:
            selected_scores, selected = route_scores.topk(num_selected, dim=-1)
            selected_mask = selected_scores > -1e8
        self._last_route_stats = {
            "compressed_attention_mass_entropy": compressed_mass_entropy.detach(),
            "route_probability_sum_error": route_probability_sum_error.detach(),
        }
        if block_probability is not None:
            self._last_route_stats["compressed_attention_mass"] = block_probability.detach()
        return route_scores, route_relevance, selected, selected_mask

    def _route_blocks_triton_streaming(
        self,
        q: Tensor,
        summary_k: Tensor,
        compression_residual: Tensor,
    ) -> tuple[Tensor, Tensor, Tensor, Tensor, RouteBackendReport]:
        batch = q.shape[0]
        requested = "triton_tile_shared" if self.route_backend == "triton_tile_shared" else "triton_streaming"
        mass_modes = {"compressed_attention_mass", "log_compressed_attention_mass", "mass_times_residual", "calibrated_mass_residual"}
        if self.route_score_mode not in {"logsumexp_logits_current", *mass_modes}:
            route_scores, route_relevance, selected, selected_mask = self._route_blocks_torch_full(q, summary_k, compression_residual)
            report = RouteBackendReport(requested, "torch_full", f"{requested} does not support route_score_mode={self.route_score_mode}")
            return route_scores, route_relevance, selected, selected_mask, report
        if self.route_score_mode == "logsumexp_logits_current" and self.route_shape_penalty_weight != 0.0:
            route_scores, route_relevance, selected, selected_mask = self._route_blocks_torch_full(q, summary_k, compression_residual)
            report = RouteBackendReport(requested, "torch_full", f"{requested} currently does not support route_shape_penalty_weight")
            return route_scores, route_relevance, selected, selected_mask, report
        if self.route_backend == "triton_tile_shared":
            route_scores, route_relevance, selected, selected_mask = self._route_blocks_torch_full(q, summary_k, compression_residual)
            report = RouteBackendReport(requested, "torch_full", "tile-shared routing is implemented as a V2 benchmark mode placeholder; exact torch route used")
            return route_scores, route_relevance, selected, selected_mask, report

        q_grouped = q.reshape(batch, self.kv_heads, self.num_grouped_queries, self.num_tokens_padded, self.dim_head)
        if self.route_score_mode != "logsumexp_logits_current":
            route_residual = self._route_residual_term(compression_residual)
            if self.route_score_mode == "calibrated_mass_residual":
                route_residual = (route_residual - route_residual.mean(dim=-1, keepdim=True)) / route_residual.std(dim=-1, keepdim=True).clamp_min(1e-6)
            shape = torch.zeros(self.num_blocks, device=q.device, dtype=torch.float32)
            if self.route_shape_penalty_weight != 0.0 and hasattr(self, "block_cov_trace"):
                trace = self.block_cov_trace.to(q.device, dtype=torch.float32)
                shape = trace / trace.mean().clamp_min(1e-6)
            try:
                selected, selected_mask, selected_scores, sum_error, report = route_mass_topk_triton(
                    q_grouped,
                    summary_k,
                    route_residual,
                    shape,
                    self.coords_packed,
                    self.block_centers,
                    self.log_metric,
                    self.block_id_packed,
                    self.valid_token_mask,
                    route_score_mode=self.route_score_mode,
                    num_selected_blocks=min(self.num_selected_blocks, max(self.num_blocks - 1 if self.exclude_own_block_from_selection else self.num_blocks, 0)),
                    residual_weight=self.residual_weight,
                    route_center_distance_weight=self._effective_triton_route_center_distance_weight(),
                    route_shape_penalty_weight=self.route_shape_penalty_weight,
                    exclude_own_block_from_selection=self.exclude_own_block_from_selection,
                    block_q=self.route_block_q,
                    block_c=self.route_block_c,
                )
            except Exception as exc:
                route_scores, route_relevance, selected, selected_mask = self._route_blocks_torch_full(q, summary_k, compression_residual)
                report = RouteBackendReport(requested, "torch_full", f"{requested} mass route failed: {type(exc).__name__}: {exc}")
                return route_scores, route_relevance, selected, selected_mask, report
            if not str(report.backend_actual).startswith("triton_streaming_"):
                route_scores, route_relevance, selected, selected_mask = self._route_blocks_torch_full(q, summary_k, compression_residual)
                report = RouteBackendReport(report.backend_requested, "torch_full", report.fallback_reason)
                return route_scores, route_relevance, selected, selected_mask, report
            route_scores = selected_scores.to(q.dtype)
            self._last_route_stats = {
                "compressed_attention_mass_entropy": q.new_tensor(0.0),
                "route_probability_sum_error": sum_error.float().mean().detach(),
            }
            return route_scores, route_scores, selected, selected_mask, report

        selected, selected_mask, selected_scores, report = route_lse_topk_triton(
            q_grouped,
            summary_k,
            compression_residual,
            self.coords_packed,
            self.block_centers,
            self.log_metric,
            self.block_id_packed,
            self.valid_token_mask,
            num_selected_blocks=min(self.num_selected_blocks, max(self.num_blocks - 1 if self.exclude_own_block_from_selection else self.num_blocks, 0)),
            residual_weight=self.residual_weight,
            route_center_distance_weight=self._effective_triton_route_center_distance_weight(),
            exclude_own_block_from_selection=self.exclude_own_block_from_selection,
            block_q=self.route_block_q,
            block_c=self.route_block_c,
        )
        if report.backend_actual != "triton_streaming_lse":
            route_scores, route_relevance, selected, selected_mask = self._route_blocks_torch_full(q, summary_k, compression_residual)
            report = RouteBackendReport(report.backend_requested, "torch_full", report.fallback_reason)
            return route_scores, route_relevance, selected, selected_mask, report
        if selected.shape[-1] == 0:
            route_scores = q.new_empty(batch, self.kv_heads, self.num_tokens_padded, 0)
            route_relevance = route_scores
        else:
            route_scores = selected_scores.to(q.dtype)
            route_relevance = route_scores
        self._last_route_stats = {
            "compressed_attention_mass_entropy": q.new_tensor(0.0),
            "route_probability_sum_error": q.new_tensor(0.0),
        }
        return route_scores, route_relevance, selected, selected_mask, report

    def _distance_bias_chunk(self, start: int, end: int, device: torch.device) -> Tensor:
        dist = self._distance_values(start=start, end=end, device=device)
        return -self.route_center_distance_weight * dist

    def _route_blocks_torch_chunked(
        self,
        q: Tensor,
        summary_k: Tensor,
        compression_residual: Tensor,
        *,
        block_chunk: int | None = None,
    ) -> tuple[Tensor, Tensor, Tensor, Tensor, RouteBackendReport]:
        requested = "torch_chunked"
        batch = q.shape[0]
        q_grouped = q.reshape(batch, self.kv_heads, self.num_grouped_queries, self.num_tokens_padded, self.dim_head)
        max_selectable = self.num_blocks - 1 if self.exclude_own_block_from_selection else self.num_blocks
        num_selected = min(self.num_selected_blocks, max(max_selectable, 0))
        if num_selected == 0:
            empty = torch.empty(batch, self.kv_heads, self.num_tokens_padded, 0, device=q.device, dtype=q.dtype)
            selected = torch.empty(batch, self.kv_heads, self.num_tokens_padded, 0, dtype=torch.long, device=q.device)
            selected_mask = torch.empty(batch, self.kv_heads, self.num_tokens_padded, 0, dtype=torch.bool, device=q.device)
            return empty, empty, selected, selected_mask, RouteBackendReport(requested, "torch_chunked", "")
        chunk = int(block_chunk or self.route_block_c)
        chunk = max(1, min(chunk, self.num_blocks))
        best_scores = torch.full((batch, self.kv_heads, self.num_tokens_padded, num_selected), -torch.inf, device=q.device, dtype=torch.float32)
        best_idx = torch.full((batch, self.kv_heads, self.num_tokens_padded, num_selected), -1, device=q.device, dtype=torch.long)
        residual_for_route = self._route_residual_term(compression_residual)
        residual_for_relevance = residual_for_route
        if self.route_score_mode == "calibrated_mass_residual":
            residual_for_relevance = (residual_for_relevance - residual_for_relevance.mean(dim=-1, keepdim=True)) / residual_for_relevance.std(dim=-1, keepdim=True).clamp_min(1e-6)
        block_range_all = torch.arange(self.num_blocks, device=q.device)
        own_block = self.block_id_packed.to(q.device).view(1, 1, self.num_tokens_padded, 1)
        valid_query = self.valid_token_mask.to(q.device).view(1, 1, self.num_tokens_padded, 1)

        denom = None
        max_logits = None
        prob_sum = None
        mass_modes = {"compressed_attention_mass", "log_compressed_attention_mass", "mass_times_residual", "calibrated_mass_residual"}
        if self.route_score_mode in mass_modes:
            max_logits = torch.full(
                (batch, self.kv_heads, self.num_grouped_queries, self.num_tokens_padded),
                -torch.inf,
                device=q.device,
                dtype=torch.float32,
            )
            for start in range(0, self.num_blocks, chunk):
                end = min(start + chunk, self.num_blocks)
                sim_atoms = torch.einsum("bgqnd,bgcrd->bgqncr", q_grouped, summary_k[:, :, start:end]) * (self.dim_head**-0.5)
                max_logits = torch.maximum(max_logits, sim_atoms.float().amax(dim=(-2, -1)))
            denom = torch.zeros_like(max_logits)
            for start in range(0, self.num_blocks, chunk):
                end = min(start + chunk, self.num_blocks)
                sim_atoms = torch.einsum("bgqnd,bgcrd->bgqncr", q_grouped, summary_k[:, :, start:end]) * (self.dim_head**-0.5)
                denom = denom + torch.exp(sim_atoms.float() - max_logits[..., None, None]).sum(dim=(-2, -1))
            prob_sum = torch.zeros(batch, self.kv_heads, self.num_tokens_padded, device=q.device, dtype=torch.float32)

        for start in range(0, self.num_blocks, chunk):
            end = min(start + chunk, self.num_blocks)
            sim_atoms = torch.einsum("bgqnd,bgcrd->bgqncr", q_grouped, summary_k[:, :, start:end]) * (self.dim_head**-0.5)
            if self.route_score_mode == "logsumexp_logits_current":
                route_scores = torch.logsumexp(sim_atoms, dim=-1).mean(dim=2)
                route_scores = route_scores + self.residual_weight * residual_for_route[:, :, start:end].unsqueeze(2)
            else:
                assert max_logits is not None and denom is not None and prob_sum is not None
                block_probability = torch.exp(sim_atoms.float() - max_logits[..., None, None]).sum(dim=-1) / denom[..., None].clamp_min(1e-20)
                block_probability = block_probability.mean(dim=2)
                prob_sum = prob_sum + block_probability.sum(dim=-1)
                if self.route_score_mode == "compressed_attention_mass":
                    route_scores = block_probability + self.residual_weight * residual_for_route[:, :, start:end].unsqueeze(2)
                elif self.route_score_mode == "log_compressed_attention_mass":
                    route_scores = block_probability.clamp_min(1e-12).log() + self.residual_weight * residual_for_route[:, :, start:end].unsqueeze(2)
                elif self.route_score_mode == "mass_times_residual":
                    route_scores = block_probability * (1.0 + self.residual_weight * residual_for_relevance[:, :, start:end].unsqueeze(2))
                elif self.route_score_mode == "calibrated_mass_residual":
                    route_scores = block_probability.clamp_min(1e-12).log() + self.residual_weight * residual_for_relevance[:, :, start:end].unsqueeze(2)
                else:
                    raise RuntimeError(f"unhandled route_score_mode={self.route_score_mode}")
            route_scores = route_scores + self._distance_bias_chunk(start, end, q.device).unsqueeze(0)
            if self.route_shape_penalty_weight != 0.0 and hasattr(self, "block_cov_trace"):
                shape = self.block_cov_trace[start:end].to(q.device)
                shape = shape / self.block_cov_trace.to(q.device).mean().clamp_min(1e-6)
                route_scores = route_scores - self.route_shape_penalty_weight * shape.view(1, 1, 1, end - start)
            if self.exclude_own_block_from_selection:
                block_range = block_range_all[start:end].view(1, 1, 1, end - start)
                route_scores = route_scores.masked_fill(block_range == own_block, -1e9)
            route_scores = route_scores.masked_fill(~valid_query, -1e9)
            take = min(num_selected, end - start)
            cand_scores, cand_idx = route_scores.topk(take, dim=-1)
            cand_idx = cand_idx + start
            merged_scores = torch.cat((best_scores, cand_scores.float()), dim=-1)
            merged_idx = torch.cat((best_idx, cand_idx.long()), dim=-1)
            best_scores, order = merged_scores.topk(num_selected, dim=-1)
            best_idx = torch.gather(merged_idx, -1, order)
        selected_mask = best_scores > -1e8
        route_scores_sparse = best_scores.to(q.dtype)
        prob_error = q.new_tensor(0.0)
        if prob_sum is not None:
            prob_error = (prob_sum - 1.0).abs().mean().to(q.dtype)
        self._last_route_stats = {
            "compressed_attention_mass_entropy": q.new_tensor(0.0),
            "route_probability_sum_error": prob_error,
        }
        return route_scores_sparse, route_scores_sparse, best_idx, selected_mask, RouteBackendReport(requested, "torch_chunked", "")

    def _route_blocks_torch_chunked_query_slice(
        self,
        q: Tensor,
        summary_k: Tensor,
        compression_residual: Tensor,
        *,
        q_start: int,
        q_end: int,
        block_chunk: int | None = None,
        query_coords: Tensor | None = None,
        query_block_id: Tensor | None = None,
        query_valid_mask: Tensor | None = None,
    ) -> tuple[Tensor, Tensor, Tensor, Tensor, RouteBackendReport]:
        requested = "torch_chunked"
        batch = q.shape[0]
        num_queries = q.shape[2]
        q_grouped = q.reshape(batch, self.kv_heads, self.num_grouped_queries, num_queries, self.dim_head)
        max_selectable = self.num_blocks - 1 if self.exclude_own_block_from_selection else self.num_blocks
        num_selected = min(self.num_selected_blocks, max(max_selectable, 0))
        if num_selected == 0:
            empty = torch.empty(batch, self.kv_heads, num_queries, 0, device=q.device, dtype=q.dtype)
            selected = torch.empty(batch, self.kv_heads, num_queries, 0, dtype=torch.long, device=q.device)
            selected_mask = torch.empty(batch, self.kv_heads, num_queries, 0, dtype=torch.bool, device=q.device)
            return empty, empty, selected, selected_mask, RouteBackendReport(requested, "torch_chunked", "")
        chunk = int(block_chunk or self.route_block_c)
        chunk = max(1, min(chunk, self.num_blocks))
        best_scores = torch.full((batch, self.kv_heads, num_queries, num_selected), -torch.inf, device=q.device, dtype=torch.float32)
        best_idx = torch.full((batch, self.kv_heads, num_queries, num_selected), -1, device=q.device, dtype=torch.long)
        residual_for_route = self._route_residual_term(compression_residual)
        residual_for_relevance = residual_for_route
        if self.route_score_mode == "calibrated_mass_residual":
            residual_for_relevance = (residual_for_relevance - residual_for_relevance.mean(dim=-1, keepdim=True)) / residual_for_relevance.std(dim=-1, keepdim=True).clamp_min(1e-6)
        block_range_all = torch.arange(self.num_blocks, device=q.device)
        query_block_id = self.block_id_packed[q_start:q_end] if query_block_id is None else query_block_id
        query_valid_mask = self.valid_token_mask[q_start:q_end] if query_valid_mask is None else query_valid_mask
        if query_block_id.numel() != num_queries or query_valid_mask.numel() != num_queries:
            raise ValueError("query metadata length must match q query length")
        own_block = query_block_id.to(q.device).view(1, 1, num_queries, 1)
        valid_query = query_valid_mask.to(q.device).view(1, 1, num_queries, 1)

        denom = None
        max_logits = None
        prob_sum = None
        mass_modes = {"compressed_attention_mass", "log_compressed_attention_mass", "mass_times_residual", "calibrated_mass_residual"}
        if self.route_score_mode in mass_modes:
            max_logits = torch.full(
                (batch, self.kv_heads, self.num_grouped_queries, num_queries),
                -torch.inf,
                device=q.device,
                dtype=torch.float32,
            )
            for start in range(0, self.num_blocks, chunk):
                end = min(start + chunk, self.num_blocks)
                sim_atoms = torch.einsum("bgqnd,bgcrd->bgqncr", q_grouped, summary_k[:, :, start:end]) * (self.dim_head**-0.5)
                max_logits = torch.maximum(max_logits, sim_atoms.float().amax(dim=(-2, -1)))
            denom = torch.zeros_like(max_logits)
            for start in range(0, self.num_blocks, chunk):
                end = min(start + chunk, self.num_blocks)
                sim_atoms = torch.einsum("bgqnd,bgcrd->bgqncr", q_grouped, summary_k[:, :, start:end]) * (self.dim_head**-0.5)
                denom = denom + torch.exp(sim_atoms.float() - max_logits[..., None, None]).sum(dim=(-2, -1))
            prob_sum = torch.zeros(batch, self.kv_heads, num_queries, device=q.device, dtype=torch.float32)

        for start in range(0, self.num_blocks, chunk):
            end = min(start + chunk, self.num_blocks)
            sim_atoms = torch.einsum("bgqnd,bgcrd->bgqncr", q_grouped, summary_k[:, :, start:end]) * (self.dim_head**-0.5)
            if self.route_score_mode == "logsumexp_logits_current":
                route_scores = torch.logsumexp(sim_atoms, dim=-1).mean(dim=2)
                route_scores = route_scores + self.residual_weight * residual_for_route[:, :, start:end].unsqueeze(2)
            else:
                assert max_logits is not None and denom is not None and prob_sum is not None
                block_probability = torch.exp(sim_atoms.float() - max_logits[..., None, None]).sum(dim=-1) / denom[..., None].clamp_min(1e-20)
                block_probability = block_probability.mean(dim=2)
                prob_sum = prob_sum + block_probability.sum(dim=-1)
                if self.route_score_mode == "compressed_attention_mass":
                    route_scores = block_probability + self.residual_weight * residual_for_route[:, :, start:end].unsqueeze(2)
                elif self.route_score_mode == "log_compressed_attention_mass":
                    route_scores = block_probability.clamp_min(1e-12).log() + self.residual_weight * residual_for_route[:, :, start:end].unsqueeze(2)
                elif self.route_score_mode == "mass_times_residual":
                    route_scores = block_probability * (1.0 + self.residual_weight * residual_for_relevance[:, :, start:end].unsqueeze(2))
                elif self.route_score_mode == "calibrated_mass_residual":
                    route_scores = block_probability.clamp_min(1e-12).log() + self.residual_weight * residual_for_relevance[:, :, start:end].unsqueeze(2)
                else:
                    raise RuntimeError(f"unhandled route_score_mode={self.route_score_mode}")
            if query_coords is None:
                distance_bias = self._distance_bias_for_queries(q_start, q_end, block_start=start, block_end=end, device=q.device)
            else:
                if query_coords.shape[0] != num_queries:
                    raise ValueError("query_coords length must match q query length")
                distance_bias = self._distance_bias_for_coords(query_coords, block_start=start, block_end=end, device=q.device)
            route_scores = route_scores + distance_bias.unsqueeze(0)
            if self.route_shape_penalty_weight != 0.0 and hasattr(self, "block_cov_trace"):
                shape = self.block_cov_trace[start:end].to(q.device)
                shape = shape / self.block_cov_trace.to(q.device).mean().clamp_min(1e-6)
                route_scores = route_scores - self.route_shape_penalty_weight * shape.view(1, 1, 1, end - start)
            if self.exclude_own_block_from_selection:
                block_range = block_range_all[start:end].view(1, 1, 1, end - start)
                route_scores = route_scores.masked_fill(block_range == own_block, -1e9)
            route_scores = route_scores.masked_fill(~valid_query, -1e9)
            take = min(num_selected, end - start)
            cand_scores, cand_idx = route_scores.topk(take, dim=-1)
            cand_idx = cand_idx + start
            merged_scores = torch.cat((best_scores, cand_scores.float()), dim=-1)
            merged_idx = torch.cat((best_idx, cand_idx.long()), dim=-1)
            best_scores, order = merged_scores.topk(num_selected, dim=-1)
            best_idx = torch.gather(merged_idx, -1, order)
        selected_mask = best_scores > -1e8
        prob_error = q.new_tensor(0.0)
        if prob_sum is not None:
            prob_error = (prob_sum - 1.0).abs().mean().to(q.dtype)
        self._last_route_stats = {
            "compressed_attention_mass_entropy": q.new_tensor(0.0),
            "route_probability_sum_error": prob_error,
        }
        route_scores_sparse = best_scores.to(q.dtype)
        return route_scores_sparse, route_scores_sparse, best_idx, selected_mask, RouteBackendReport(requested, "torch_chunked", "")

    def _route_blocks_with_backend_query_slice_exact(
        self,
        q: Tensor,
        summary_k: Tensor,
        compression_residual: Tensor,
        *,
        q_start: int,
        q_end: int,
        materialize_scores: bool = False,
        query_coords: Tensor | None = None,
        query_block_id: Tensor | None = None,
        query_valid_mask: Tensor | None = None,
    ) -> tuple[Tensor, Tensor, Tensor, Tensor, RouteBackendReport]:
        coords = self.coords_packed[q_start:q_end] if query_coords is None else query_coords
        block_ids = self.block_id_packed[q_start:q_end] if query_block_id is None else query_block_id
        valid_mask = self.valid_token_mask[q_start:q_end] if query_valid_mask is None else query_valid_mask
        if self.route_backend in {"torch_full", "torch_chunked"} or materialize_scores:
            return self._route_blocks_torch_chunked_query_slice(
                q,
                summary_k,
                compression_residual,
                q_start=q_start,
                q_end=q_end,
                query_coords=coords,
                query_block_id=block_ids,
                query_valid_mask=valid_mask,
            )
        requested = "triton_tile_shared" if self.route_backend == "triton_tile_shared" else "triton_streaming"
        if self.route_backend == "triton_tile_shared":
            route_scores, route_relevance, selected, selected_mask, _ = self._route_blocks_torch_chunked_query_slice(
                q,
                summary_k,
                compression_residual,
                q_start=q_start,
                q_end=q_end,
                query_coords=coords,
                query_block_id=block_ids,
                query_valid_mask=valid_mask,
            )
            return route_scores, route_relevance, selected, selected_mask, RouteBackendReport(requested, "torch_chunked", "tile-shared routing is a placeholder; exact tiled torch route used")
        batch = q.shape[0]
        q_grouped = q.reshape(batch, self.kv_heads, self.num_grouped_queries, q.shape[2], self.dim_head)
        if self.route_score_mode == "logsumexp_logits_current":
            try:
                selected, selected_mask, selected_scores, report = route_lse_topk_triton(
                    q_grouped,
                    summary_k,
                    compression_residual,
                    coords,
                    self.block_centers,
                    self.log_metric,
                    block_ids,
                    valid_mask,
                    num_selected_blocks=min(self.num_selected_blocks, max(self.num_blocks - 1 if self.exclude_own_block_from_selection else self.num_blocks, 0)),
                    residual_weight=self.residual_weight,
                    route_center_distance_weight=self._effective_triton_route_center_distance_weight(),
                    exclude_own_block_from_selection=self.exclude_own_block_from_selection,
                    block_q=self.route_block_q,
                    block_c=self.route_block_c,
                )
            except Exception as exc:
                route_scores, route_relevance, selected, selected_mask, _ = self._route_blocks_torch_chunked_query_slice(
                    q,
                    summary_k,
                    compression_residual,
                    q_start=q_start,
                    q_end=q_end,
                    query_coords=coords,
                    query_block_id=block_ids,
                    query_valid_mask=valid_mask,
                )
                return route_scores, route_relevance, selected, selected_mask, RouteBackendReport(requested, "torch_chunked", f"{requested} tiled lse route failed: {type(exc).__name__}: {exc}")
            if report.backend_actual != "triton_streaming_lse":
                route_scores, route_relevance, selected, selected_mask, _ = self._route_blocks_torch_chunked_query_slice(
                    q,
                    summary_k,
                    compression_residual,
                    q_start=q_start,
                    q_end=q_end,
                    query_coords=coords,
                    query_block_id=block_ids,
                    query_valid_mask=valid_mask,
                )
                return route_scores, route_relevance, selected, selected_mask, RouteBackendReport(report.backend_requested, "torch_chunked", report.fallback_reason)
            route_scores = selected_scores.to(q.dtype)
            return route_scores, route_scores, selected, selected_mask, report
        mass_modes = {"compressed_attention_mass", "log_compressed_attention_mass", "mass_times_residual", "calibrated_mass_residual"}
        if self.route_score_mode not in mass_modes:
            route_scores, route_relevance, selected, selected_mask, _ = self._route_blocks_torch_chunked_query_slice(
                q,
                summary_k,
                compression_residual,
                q_start=q_start,
                q_end=q_end,
                query_coords=coords,
                query_block_id=block_ids,
                query_valid_mask=valid_mask,
            )
            return route_scores, route_relevance, selected, selected_mask, RouteBackendReport(requested, "torch_chunked", f"{requested} does not support route_score_mode={self.route_score_mode}")
        route_residual = self._route_residual_term(compression_residual)
        if self.route_score_mode == "calibrated_mass_residual":
            route_residual = (route_residual - route_residual.mean(dim=-1, keepdim=True)) / route_residual.std(dim=-1, keepdim=True).clamp_min(1e-6)
        shape = torch.zeros(self.num_blocks, device=q.device, dtype=torch.float32)
        if self.route_shape_penalty_weight != 0.0 and hasattr(self, "block_cov_trace"):
            trace = self.block_cov_trace.to(q.device, dtype=torch.float32)
            shape = trace / trace.mean().clamp_min(1e-6)
        try:
            selected, selected_mask, selected_scores, sum_error, report = route_mass_topk_triton(
                q_grouped,
                summary_k,
                route_residual,
                shape,
                coords,
                self.block_centers,
                self.log_metric,
                block_ids,
                valid_mask,
                route_score_mode=self.route_score_mode,
                num_selected_blocks=min(self.num_selected_blocks, max(self.num_blocks - 1 if self.exclude_own_block_from_selection else self.num_blocks, 0)),
                residual_weight=self.residual_weight,
                route_center_distance_weight=self._effective_triton_route_center_distance_weight(),
                route_shape_penalty_weight=self.route_shape_penalty_weight,
                exclude_own_block_from_selection=self.exclude_own_block_from_selection,
                block_q=self.route_block_q,
                block_c=self.route_block_c,
            )
        except Exception as exc:
            route_scores, route_relevance, selected, selected_mask, _ = self._route_blocks_torch_chunked_query_slice(
                q,
                summary_k,
                compression_residual,
                q_start=q_start,
                q_end=q_end,
                query_coords=coords,
                query_block_id=block_ids,
                query_valid_mask=valid_mask,
            )
            return route_scores, route_relevance, selected, selected_mask, RouteBackendReport(requested, "torch_chunked", f"{requested} tiled mass route failed: {type(exc).__name__}: {exc}")
        if not str(report.backend_actual).startswith("triton_streaming_"):
            route_scores, route_relevance, selected, selected_mask, _ = self._route_blocks_torch_chunked_query_slice(
                q,
                summary_k,
                compression_residual,
                q_start=q_start,
                q_end=q_end,
                query_coords=coords,
                query_block_id=block_ids,
                query_valid_mask=valid_mask,
            )
            return route_scores, route_relevance, selected, selected_mask, RouteBackendReport(report.backend_requested, "torch_chunked", report.fallback_reason)
        self._last_route_stats = {
            "compressed_attention_mass_entropy": q.new_tensor(0.0),
            "route_probability_sum_error": sum_error.float().mean().detach(),
        }
        route_scores = selected_scores.to(q.dtype)
        return route_scores, route_scores, selected, selected_mask, report

    def _route_share_group_size(self) -> tuple[int, str]:
        if self.route_granularity == "query_block_shared":
            return max(1, int(self.block_volume)), "query_block_shared"
        if self.route_granularity == "query_tile_shared":
            return max(1, int(self.route_share_tile_size)), "query_tile_shared"
        if self.route_granularity == "hierarchical_superblock":
            # The coarse-to-fine superblock selector is intentionally not
            # implemented yet. Use the nearest method-safe sharing unit and
            # report the fallback through route stats/aux instead of silently
            # claiming hierarchical routing.
            return max(1, int(self.block_volume)), "query_block_shared"
        return 1, "token_exact"

    def _pooled_shared_queries(
        self,
        q: Tensor,
        *,
        q_start: int,
        q_end: int,
        group_size: int,
    ) -> tuple[Tensor, Tensor, Tensor, Tensor, int, float]:
        batch, heads, num_queries, dim = q.shape
        num_groups = int(math.ceil(num_queries / group_size))
        padded = num_groups * group_size
        pad = padded - num_queries
        if pad:
            q_work = F.pad(q, (0, 0, 0, pad))
            valid = F.pad(self.valid_token_mask[q_start:q_end].to(q.device), (0, pad), value=False)
            token_ids = F.pad(torch.arange(q_start, q_end, device=q.device, dtype=torch.long), (0, pad), value=max(q_end - 1, q_start))
        else:
            q_work = q
            valid = self.valid_token_mask[q_start:q_end].to(q.device)
            token_ids = torch.arange(q_start, q_end, device=q.device, dtype=torch.long)
        q_groups = q_work.reshape(batch, heads, num_groups, group_size, dim)
        valid_groups = valid.reshape(num_groups, group_size)
        weights = valid_groups.to(q.dtype).view(1, 1, num_groups, group_size, 1)
        denom = weights.sum(dim=3).clamp_min(1.0)
        q_shared = ((q_groups * weights).sum(dim=3) / denom).to(q.dtype)
        first_offsets = valid_groups.float().argmax(dim=1).long()
        group_token_ids = token_ids.reshape(num_groups, group_size)[torch.arange(num_groups, device=q.device), first_offsets]
        shared_coords = self.coords_packed.to(q.device).index_select(0, group_token_ids)
        shared_block_ids = self.block_id_packed.to(q.device).index_select(0, group_token_ids)
        shared_valid = valid_groups.any(dim=1)
        sharing_factor = float(num_queries) / float(max(num_groups, 1))
        return q_shared, shared_coords, shared_block_ids, shared_valid, pad, sharing_factor

    def _route_blocks_shared_query_slice(
        self,
        q: Tensor,
        summary_k: Tensor,
        compression_residual: Tensor,
        *,
        q_start: int,
        q_end: int,
        materialize_scores: bool = False,
    ) -> tuple[Tensor, Tensor, Tensor, Tensor, RouteBackendReport]:
        group_size, actual_granularity = self._route_share_group_size()
        if group_size <= 1:
            return self._route_blocks_with_backend_query_slice_exact(
                q,
                summary_k,
                compression_residual,
                q_start=q_start,
                q_end=q_end,
                materialize_scores=materialize_scores,
            )
        q_shared, shared_coords, shared_block_ids, shared_valid, pad, sharing_factor = self._pooled_shared_queries(
            q,
            q_start=q_start,
            q_end=q_end,
            group_size=group_size,
        )
        route_scores_g, route_relevance_g, selected_g, selected_mask_g, report = self._route_blocks_with_backend_query_slice_exact(
            q_shared,
            summary_k,
            compression_residual,
            q_start=q_start,
            q_end=q_start + q_shared.shape[2],
            materialize_scores=materialize_scores,
            query_coords=shared_coords,
            query_block_id=shared_block_ids,
            query_valid_mask=shared_valid,
        )
        repeat = group_size
        route_scores = route_scores_g.repeat_interleave(repeat, dim=2)
        route_relevance = route_relevance_g.repeat_interleave(repeat, dim=2)
        selected = selected_g.repeat_interleave(repeat, dim=2)
        selected_mask = selected_mask_g.repeat_interleave(repeat, dim=2)
        if pad:
            route_scores = route_scores[:, :, :-pad]
            route_relevance = route_relevance[:, :, :-pad]
            selected = selected[:, :, :-pad]
            selected_mask = selected_mask[:, :, :-pad]
        if self.exclude_own_block_from_selection:
            # Representative-block exclusion is exact for query_block_shared
            # and approximate for larger query tiles. Keep the selected-token
            # budget fixed and avoid producing all-masked selected rows, which
            # selected Triton kernels correctly treat as outside their contract.
            own = self.block_id_packed[q_start:q_end].to(q.device).view(1, 1, q.shape[2], 1)
            filtered = selected_mask & (selected != own)
            selected_mask = torch.where(filtered.any(dim=-1, keepdim=True), filtered, selected_mask)
        # repeat_interleave plus truncation can leave non-contiguous views. The
        # selected Triton kernel assumes dense row-major selected block tensors,
        # so materialize that contract explicitly before crossing the kernel
        # boundary.
        route_scores = route_scores.contiguous()
        route_relevance = route_relevance.contiguous()
        selected = selected.contiguous()
        selected_mask = selected_mask.contiguous()
        self._last_route_stats["route_sharing_factor"] = q.new_tensor(sharing_factor)
        self._last_route_stats["route_granularity_actual_code"] = q.new_tensor(
            1.0 if actual_granularity == "query_tile_shared" else 2.0 if actual_granularity == "query_block_shared" else 0.0
        )
        fallback = report.fallback_reason
        if self.route_granularity == "hierarchical_superblock":
            msg = "hierarchical_superblock not implemented; query_block_shared used"
            fallback = f"{fallback}; {msg}" if fallback else msg
            report = RouteBackendReport(report.backend_requested, report.backend_actual, fallback)
        return route_scores, route_relevance, selected, selected_mask, report

    def _route_blocks_with_backend_query_slice(
        self,
        q: Tensor,
        summary_k: Tensor,
        compression_residual: Tensor,
        *,
        q_start: int,
        q_end: int,
        materialize_scores: bool = False,
    ) -> tuple[Tensor, Tensor, Tensor, Tensor, RouteBackendReport]:
        if self.route_granularity == "token_exact":
            self._last_route_stats["route_sharing_factor"] = q.new_tensor(1.0)
            self._last_route_stats["route_granularity_actual_code"] = q.new_tensor(0.0)
            return self._route_blocks_with_backend_query_slice_exact(
                q,
                summary_k,
                compression_residual,
                q_start=q_start,
                q_end=q_end,
                materialize_scores=materialize_scores,
            )
        return self._route_blocks_shared_query_slice(
            q,
            summary_k,
            compression_residual,
            q_start=q_start,
            q_end=q_end,
            materialize_scores=materialize_scores,
        )

    def _route_blocks_with_backend(
        self,
        q: Tensor,
        summary_k: Tensor,
        compression_residual: Tensor,
        *,
        materialize_scores: bool = True,
    ) -> tuple[Tensor, Tensor, Tensor, Tensor, RouteBackendReport]:
        if self.route_granularity != "token_exact":
            return self._route_blocks_shared_query_slice(
                q,
                summary_k,
                compression_residual,
                q_start=0,
                q_end=q.shape[2],
                materialize_scores=materialize_scores,
            )
        self._last_route_stats["route_sharing_factor"] = q.new_tensor(1.0)
        self._last_route_stats["route_granularity_actual_code"] = q.new_tensor(0.0)
        if self.route_backend == "torch_full" or materialize_scores:
            route_scores, route_relevance, selected, selected_mask = self._route_blocks_torch_full(q, summary_k, compression_residual)
            report = RouteBackendReport(self.route_backend, "torch_full", "")
            return route_scores, route_relevance, selected, selected_mask, report
        if self.route_backend == "torch_chunked":
            return self._route_blocks_torch_chunked(q, summary_k, compression_residual)
        return self._route_blocks_triton_streaming(q, summary_k, compression_residual)

    def _route_blocks(
        self,
        q: Tensor,
        summary_k: Tensor,
        compression_residual: Tensor,
    ) -> tuple[Tensor, Tensor, Tensor, Tensor]:
        return self._route_blocks_with_backend(q, summary_k, compression_residual, materialize_scores=True)[:4]

    def _selected_attention_torch(
        self,
        q: Tensor,
        k: Tensor,
        v: Tensor,
        selected_block_indices: Tensor,
        selected_block_mask: Tensor,
    ) -> Tensor:
        """GQA-faithful selected-block PyTorch fallback."""
        batch, _, num_queries, _ = q.shape
        num_selected = selected_block_indices.shape[-1]
        if num_selected == 0:
            return q.new_zeros(batch, self.heads, num_queries, self.dim_head)
        q_grouped = q.reshape(batch, self.kv_heads, self.num_grouped_queries, num_queries, self.dim_head)
        token_idx = self.block_token_indices.to(q.device)[selected_block_indices]
        token_valid = self.block_valid_mask.to(q.device)[selected_block_indices]
        full_mask = (token_valid & selected_block_mask.unsqueeze(-1)).reshape(
            batch, self.kv_heads, num_queries, num_selected * self.block_volume
        )
        b_idx = torch.arange(batch, device=q.device)[:, None, None, None, None]
        g_idx = torch.arange(self.kv_heads, device=q.device)[None, :, None, None, None]
        selected_k = k[b_idx, g_idx, token_idx, :].reshape(
            batch, self.kv_heads, num_queries, num_selected * self.block_volume, self.dim_head
        )
        selected_v = v[b_idx, g_idx, token_idx, :].reshape(
            batch, self.kv_heads, num_queries, num_selected * self.block_volume, self.dim_head
        )
        sim = torch.einsum("bgqnd,bgnmd->bgqnm", q_grouped, selected_k) * (self.dim_head**-0.5)
        sim = sim.masked_fill(~full_mask.unsqueeze(2), torch.finfo(sim.dtype).min)
        attn = sim.softmax(dim=-1)
        out = torch.einsum("bgqnm,bgnmd->bgqnd", attn, selected_v)
        return out.reshape(batch, self.heads, num_queries, self.dim_head)

    def _forward_query_tiled(
        self,
        x: Tensor,
        *,
        query_disable_local_mask: Tensor | None,
        return_aux: bool,
        profile_sections: bool,
        original_grid_format: bool,
    ):
        if profile_sections:
            warnings.warn("profile_sections for query_tiled reports aggregate Python-section timing only", UserWarning, stacklevel=2)
        batch = x.shape[0]
        residual = x
        x = self.norm(x)
        disable_local_packed = self._pack_bool_mask(query_disable_local_mask).to(x.device) if query_disable_local_mask is not None else None
        local_all_disabled = (
            (not self.enable_local_branch)
            or (
                self.skip_disabled_local_branch
                and disable_local_packed is not None
                and bool(disable_local_packed.all().item())
            )
        )

        total_start = time.perf_counter() if profile_sections else 0.0
        section_times_ms: dict[str, float] = {}

        def _section(name: str, fn):
            if profile_sections and x.is_cuda:
                torch.cuda.synchronize(x.device)
            start = time.perf_counter()
            value = fn()
            if profile_sections and x.is_cuda:
                torch.cuda.synchronize(x.device)
            if profile_sections:
                section_times_ms[name] = section_times_ms.get(name, 0.0) + (time.perf_counter() - start) * 1000.0
            return value

        summary_k, summary_v, compression_residual, atom_weights = _section(
            "compression_time_ms",
            lambda: self._compute_compression_from_tokens_tiled(x),
        )
        k_local: Tensor | None
        v_local: Tensor | None
        if local_all_disabled:
            k_local = None
            v_local = None
        else:
            k_local, v_local = _section("local_kv_projection_time_ms", lambda: self._project_kv_branch_tokens(x, "local"))
        if self.enable_selected_branch and self.num_selected_blocks > 0:
            k_sel, v_sel = _section("selected_kv_projection_time_ms", lambda: self._project_kv_branch_tokens(x, "sel"))
        else:
            k_sel = None
            v_sel = None

        out_packed = x.new_empty(batch, self.num_tokens_padded, self.dim)
        selected_tiles: list[Tensor] = []
        selected_mask_tiles: list[Tensor] = []
        route_backend_reports: list[RouteBackendReport] = []
        backend = BackendReport("triton_selected" if self.use_triton_kernel else "torch_fallback", "not_run", "")
        local_backend: LocalBackendReport = LocalBackendReport(
            "triton_local" if self.local_attention_backend == "triton" else "torch_fallback",
            "not_run",
            "",
        )
        tile = max(1, int(self.query_tile_size))

        def _tile_forward(
            start: int,
            end: int,
            x_tile_arg: Tensor | None = None,
            residual_tile_arg: Tensor | None = None,
        ) -> tuple[Tensor, Tensor, Tensor, RouteBackendReport, BackendReport, LocalBackendReport]:
            nonlocal backend, local_backend
            x_tile = x[:, start:end] if x_tile_arg is None else x_tile_arg
            residual_tile = residual[:, start:end] if residual_tile_arg is None else residual_tile_arg
            q_tile_unrotated = self._split_q(self.to_q(x_tile))
            q_tile = self._apply_axial_rope(q_tile_unrotated, self.coords_packed[start:end])

            def _route_call():
                if not self.enable_selected_branch or self.num_selected_blocks <= 0:
                    return self._empty_selection(batch, end - start, device=q_tile.device)
                if self.route_select_grad:
                    return self._route_blocks_with_backend_query_slice(
                        q_tile,
                        summary_k,
                        compression_residual,
                        q_start=start,
                        q_end=end,
                        materialize_scores=return_aux and self.route_materialize_scores_in_aux,
                    )
                with torch.no_grad():
                    return self._route_blocks_with_backend_query_slice(
                        q_tile,
                        summary_k,
                        compression_residual,
                        q_start=start,
                        q_end=end,
                        materialize_scores=return_aux and self.route_materialize_scores_in_aux,
                    )

            _route_scores, _route_relevance, selected_block_indices, selected_block_mask, route_backend = _section("route_overhead_time_ms", _route_call)

            gate_logits = self.gate_proj(x_tile).reshape(batch, end - start, self.heads, 3).permute(0, 2, 1, 3)
            gate_logits = self._apply_branch_gate_prior(gate_logits)
            disable_tile = disable_local_packed[:, start:end] if disable_local_packed is not None else None
            if self.branch_gate_mode == "softmax":
                gates = self._mask_branch_logits(gate_logits, disable_tile).softmax(dim=-1)
            else:
                gates = self._apply_sigmoid_branch_mask(gate_logits.sigmoid(), disable_tile)
                if self.branch_gate_mode == "sigmoid_normalized":
                    gates = gates / gates.sum(dim=-1, keepdim=True).clamp_min(1e-6)

            local: Tensor | None = None
            coarse: Tensor | None = None
            selected: Tensor | None = None
            if local_all_disabled:
                local_backend = LocalBackendReport(
                    "triton_local" if self.local_attention_backend == "triton" else "torch_fallback",
                    "skipped",
                    "local branch disabled for all queries",
                )
            else:
                assert k_local is not None and v_local is not None
                neighbor_indices = self.local_neighbor_indices[start:end]
                neighbor_mask = self.local_neighbor_mask[start:end]
                if self.local_attention_backend == "triton":
                    local, local_backend = local_attention(
                        q_tile,
                        k_local,
                        v_local,
                        neighbor_indices,
                        neighbor_mask,
                        use_triton_kernel=True,
                        torch_fallback=lambda q_, k_, v_: self._local_attention_torch(q_, k_, v_, neighbor_indices, neighbor_mask),
                        block_n=self.local_attention_block_n,
                        validate_output=self.validate_triton_outputs,
                    )
                else:
                    local_backend = LocalBackendReport("torch_fallback", "torch_fallback", "")
                    local = self._local_attention_torch(q_tile, k_local, v_local, neighbor_indices, neighbor_mask)

            if self.enable_compressed_branch:
                coarse = self._coarse_attention_torch(self._compressed_query(q_tile, q_tile_unrotated), summary_k, summary_v)
            if self.enable_selected_branch and self.num_selected_blocks > 0:
                assert k_sel is not None and v_sel is not None
                selected, backend = selected_attention(
                    q_tile,
                    k_sel,
                    v_sel,
                    self.block_volume,
                    selected_block_indices,
                    selected_block_mask,
                    use_triton_kernel=self.use_triton_kernel,
                    torch_fallback=self._selected_attention_torch,
                    include_block_causal=False,
                    validate_output=self.validate_triton_outputs,
                )
            else:
                backend = BackendReport("triton_selected" if self.use_triton_kernel else "torch_fallback", "skipped", "selected branch disabled")
            local_mix, coarse_mix, selected_mix, _, _, _ = self._prepare_branch_outputs(
                q_tile,
                local=local,
                coarse=coarse,
                selected=selected,
            )
            mixed, _ = self._mix_branch_outputs(
                q_tile,
                gates,
                local=local_mix,
                coarse=coarse_mix,
                selected=selected_mix,
            )
            out_tile = self.to_out(self._merge_heads(mixed)) + residual_tile
            out_tile = out_tile * self.valid_token_mask[start:end].to(out_tile.device).view(1, -1, 1)
            return out_tile, selected_block_indices, selected_block_mask, route_backend, backend, local_backend

        for start in range(0, self.num_tokens_padded, tile):
            end = min(start + tile, self.num_tokens_padded)
            if self.query_tile_checkpoint and self.training and torch.is_grad_enabled() and not return_aux and not profile_sections:
                def _checkpointed(x_tile: Tensor, residual_tile: Tensor, start_i: int = start, end_i: int = end) -> Tensor:
                    return _tile_forward(start_i, end_i, x_tile, residual_tile)[0]

                out_tile = checkpoint(
                    _checkpointed,
                    x[:, start:end],
                    residual[:, start:end],
                    use_reentrant=False,
                    preserve_rng_state=False,
                )
                selected_block_indices = torch.empty(batch, self.kv_heads, end - start, 0, device=x.device, dtype=torch.long)
                selected_block_mask = torch.empty(batch, self.kv_heads, end - start, 0, device=x.device, dtype=torch.bool)
            else:
                out_tile, selected_block_indices, selected_block_mask, route_backend, backend, local_backend = _tile_forward(start, end)
                route_backend_reports.append(route_backend)
            out_packed[:, start:end] = out_tile
            if return_aux:
                selected_tiles.append(selected_block_indices.detach())
                selected_mask_tiles.append(selected_block_mask.detach())

        out = out_packed
        if profile_sections:
            section_times_ms["total_attention_time_ms"] = (time.perf_counter() - total_start) * 1000.0
        if original_grid_format:
            out = self._unpack(out)
        if not return_aux:
            return out

        if route_backend_reports:
            actual = route_backend_reports[0].backend_actual
            requested = route_backend_reports[0].backend_requested
            fallback = "; ".join(sorted({r.fallback_reason for r in route_backend_reports if r.fallback_reason}))
            if any(r.backend_actual != actual for r in route_backend_reports):
                actual = "mixed_tiled_route_backends"
        else:
            requested = self.route_backend
            actual = "checkpointed_not_materialized"
            fallback = ""
        selected_block_indices = torch.cat(selected_tiles, dim=2) if selected_tiles else torch.empty(0, device=x.device, dtype=torch.long)
        selected_block_mask = torch.cat(selected_mask_tiles, dim=2) if selected_mask_tiles else torch.empty(0, device=x.device, dtype=torch.bool)
        zero = out.new_tensor(0.0)
        aux: Dict[str, Any] = {
            "backend_requested": backend.backend_requested,
            "backend_actual": backend.backend_actual,
            "fallback_reason": backend.fallback_reason,
            "selected_block_indices": selected_block_indices,
            "selected_block_mask": selected_block_mask,
            "route_scores": torch.empty(0, device=out.device, dtype=out.dtype),
            "compression_residual": compression_residual.detach(),
            "residual_score": compression_residual.detach(),
            "route_relevance": torch.empty(0, device=out.device, dtype=out.dtype),
            "gates": torch.empty(0, 0, 0, 3, device=out.device, dtype=out.dtype),
            "valid_token_mask": self.valid_token_mask.detach(),
            "block_id_packed": self.block_id_packed.detach(),
            "atom_weights": atom_weights.detach(),
            "backend_report": BackendReport(backend.backend_requested, backend.backend_actual, backend.fallback_reason),
            "route_select_grad": self.route_select_grad,
            "route_backend_requested": requested,
            "route_backend_actual": actual,
            "route_fallback_reason": fallback,
            "route_granularity": self.route_granularity,
            "route_share_tile_size": self.route_share_tile_size,
            "route_sharing_factor": self._last_route_stats.get("route_sharing_factor", zero + 1.0).detach(),
            "route_scores_sparse": True,
            "route_materialize_scores_in_aux": False,
            "enabled_branches": ",".join(self.enabled_branches),
            "packed_branch_kv_projection": self.packed_branch_kv_projection,
            "skip_disabled_local_branch": self.skip_disabled_local_branch,
            "checkpoint_local_attention": self.checkpoint_local_attention,
            "branch_output_fusion": self.branch_output_fusion,
            "branch_output_norm": self.branch_output_norm,
            "branch_layer_scale_enabled": self.branch_layer_scale_enabled,
            "branch_layer_scale_local_mean": self.branch_layer_scale[0].detach().float().mean(),
            "branch_layer_scale_compressed_mean": self.branch_layer_scale[1].detach().float().mean(),
            "branch_layer_scale_selected_mean": self.branch_layer_scale[2].detach().float().mean(),
            "branch_mixer_mode": self.branch_mixer_mode,
            "branch_mixer_mode_effective": self.branch_mixer_mode,
            "selected_mixing_mode": self.selected_mixing_mode,
            "selected_mixing_mode_effective": self.selected_mixing_mode,
            "branch_output_checkpoint_active": False,
            "local_attention_backend_requested": local_backend.backend_requested,
            "local_attention_backend_actual": local_backend.backend_actual,
            "local_attention_fallback_reason": local_backend.fallback_reason,
            "local_attention_backend": self.local_attention_backend,
            "validate_triton_outputs": self.validate_triton_outputs,
            "pos_encoding": self.pos_encoding,
            "compressed_rope_mode": self.compressed_rope_mode,
            "rotary_base": self.rotary_base,
            "rotary_coordinate_mode": self.rotary_coordinate_mode,
            "rotary_axis_scales": ",".join(f"{float(x):g}" for x in self.rotary_axis_scales.detach().cpu().tolist()),
            "rotary_axis_pair_allocation": self.rotary_axis_pair_allocation,
            "rotary_axis_pair_counts": ",".join(str(int(x)) for x in self.rotary_axis_pair_counts_tuple),
            "layout": self.layout,
            "route_score_mode": self.route_score_mode,
            "route_backend": self.route_backend,
            "coarse_attention_backend": self.coarse_attention_backend,
            "coarse_summary_pool_size": self.coarse_summary_pool_size,
            "full_layer_execution": self.full_layer_execution,
            "query_tile_size": self.query_tile_size,
            "query_tile_checkpoint": self.query_tile_checkpoint,
            "route_block_q": self.route_block_q,
            "route_block_c": self.route_block_c,
            "route_shape_penalty_weight": self.route_shape_penalty_weight,
            "route_center_distance_weight": self.route_center_distance_weight,
            "route_center_distance_weight_explicit": self.route_center_distance_weight_explicit,
            "route_distance_normalization": self.route_distance_normalization,
            "route_distance_units": self.route_distance_units,
            "allow_raw_distance_on_probability_route": self.allow_raw_distance_on_probability_route,
            "branch_gate_mode": self.branch_gate_mode,
            "branch_gate_prior_schedule": self.branch_gate_prior_schedule,
            "branch_gate_prior_progress": self.branch_gate_prior_progress_tensor.detach(),
            "branch_gate_prior_local": self.branch_gate_prior_current_vec[0].detach(),
            "branch_gate_prior_compressed": self.branch_gate_prior_current_vec[1].detach(),
            "branch_gate_prior_selected": self.branch_gate_prior_current_vec[2].detach(),
            "gate_sum_mean": zero,
            "local_output_norm": zero,
            "compressed_output_norm": zero,
            "selected_output_norm": zero,
            "local_post_output_norm": zero,
            "compressed_post_output_norm": zero,
            "selected_post_output_norm": zero,
            "atom_assignment_mode": self.atom_assignment_mode,
            "atom_aux_loss": self._last_atom_stats.get("atom_aux_loss", zero).detach(),
            "atom_balance_loss": self._last_atom_stats.get("atom_balance_loss", zero).detach(),
            "atom_entropy_loss": self._last_atom_stats.get("atom_entropy_loss", zero).detach(),
            "atom_orthogonality_loss": self._last_atom_stats.get("atom_orthogonality_loss", zero).detach(),
            "atom_assignment_entropy_mean": self._last_atom_stats.get("atom_assignment_entropy_mean", zero).detach(),
            "atom_effective_count": self._last_atom_stats.get("atom_effective_count", zero + 1.0).detach(),
            "atom_balance_mean": self._last_atom_stats.get("atom_balance_mean", zero).detach(),
            "atom_cosine_abs_offdiag": self._last_atom_stats.get("atom_cosine_abs_offdiag", zero).detach(),
            "compressed_attention_mass_entropy": self._last_route_stats.get("compressed_attention_mass_entropy", zero).detach(),
            "route_probability_sum_error": self._last_route_stats.get("route_probability_sum_error", zero).detach(),
        }
        if profile_sections:
            aux["section_times_ms"] = section_times_ms
        return out, aux

    def forward(
        self,
        x: Tensor,
        query_disable_local_mask: Tensor | None = None,
        return_aux: bool = False,
        profile_sections: bool = False,
    ) -> Tensor | tuple[Tensor, Dict[str, Any]]:
        original_grid_format = x.dim() == self.ndim + 2
        if original_grid_format:
            if tuple(x.shape[1:-1]) != self.grid_shape:
                raise ValueError(f"expected grid shape {self.grid_shape}, got {tuple(x.shape[1:-1])}")
            x = self._pack(x)
        elif x.dim() == 3:
            if x.shape[1] != self.num_tokens_padded:
                raise ValueError(f"expected {self.num_tokens_padded} packed tokens, got {x.shape[1]}")
        else:
            raise ValueError(f"unexpected input shape {tuple(x.shape)}")

        if self.full_layer_execution == "query_tiled":
            return self._forward_query_tiled(
                x,
                query_disable_local_mask=query_disable_local_mask,
                return_aux=return_aux,
                profile_sections=profile_sections,
                original_grid_format=original_grid_format,
            )

        batch = x.shape[0]
        residual = x
        x = self.norm(x)
        disable_local_packed = self._pack_bool_mask(query_disable_local_mask).to(x.device) if query_disable_local_mask is not None else None
        section_times_ms: dict[str, float] = {}

        def _sync_if_needed() -> None:
            if profile_sections and x.is_cuda:
                torch.cuda.synchronize(x.device)

        def _section(name: str, fn):
            if not profile_sections:
                return fn()
            _sync_if_needed()
            start = time.perf_counter()
            value = fn()
            _sync_if_needed()
            section_times_ms[name] = (time.perf_counter() - start) * 1000.0
            return value

        q_unrotated = self._split_q(self.to_q(x))
        q = self._apply_axial_rope(q_unrotated, self.coords_packed)
        local_all_disabled = (
            (not self.enable_local_branch)
            or (
                self.skip_disabled_local_branch
                and disable_local_packed is not None
                and bool(disable_local_packed.all().item())
            )
        )
        selected_branch_active = self.enable_selected_branch and self.num_selected_blocks > 0
        (k_local, v_local), (k_cmp, v_cmp), (k_sel, v_sel) = self._project_all_kv(
            x,
            need_local=not local_all_disabled,
            need_selected=selected_branch_active,
        )

        total_start = time.perf_counter() if profile_sections else 0.0
        summary_k, summary_v, compression_residual, atom_weights = _section(
            "compression_time_ms",
            lambda: self._compute_compression(k_cmp, v_cmp),
        )
        def _route_call():
            if not self.enable_selected_branch or self.num_selected_blocks <= 0:
                return self._empty_selection(batch, self.num_tokens_padded, device=q.device)
            if self.route_select_grad:
                return self._route_blocks_with_backend(q, summary_k, compression_residual, materialize_scores=return_aux and self.route_materialize_scores_in_aux)
            with torch.no_grad():
                return self._route_blocks_with_backend(q, summary_k, compression_residual, materialize_scores=return_aux and self.route_materialize_scores_in_aux)

        route_scores, route_relevance, selected_block_indices, selected_block_mask, route_backend = _section(
            "route_overhead_time_ms",
            _route_call,
        )
        gate_logits = self.gate_proj(x).reshape(batch, self.num_tokens_padded, self.heads, 3).permute(0, 2, 1, 3)
        gate_logits = self._apply_branch_gate_prior(gate_logits)
        if self.branch_gate_mode == "softmax":
            gates = self._mask_branch_logits(gate_logits, disable_local_packed).softmax(dim=-1)
        else:
            gates = self._apply_sigmoid_branch_mask(gate_logits.sigmoid(), disable_local_packed)
            if self.branch_gate_mode == "sigmoid_normalized":
                gates = gates / gates.sum(dim=-1, keepdim=True).clamp_min(1e-6)

        local_backend: LocalBackendReport = LocalBackendReport("torch_fallback", "torch_fallback", "")
        backend = BackendReport("triton_selected" if self.use_triton_kernel else "torch_fallback", "torch_fallback", "")

        def _torch_local(q_: Tensor, k_: Tensor, v_: Tensor) -> Tensor:
            return self._local_attention_torch(q_, k_, v_)

        def _local_call(q_: Tensor = q, k_: Tensor | None = k_local, v_: Tensor | None = v_local) -> Tensor:
            nonlocal local_backend
            if local_all_disabled:
                local_backend = LocalBackendReport(
                    "triton_local" if self.local_attention_backend == "triton" else "torch_fallback",
                    "skipped",
                    "local branch disabled for all queries",
                )
                return q_.new_zeros(batch, self.heads, self.num_tokens_padded, self.dim_head)
            assert k_ is not None and v_ is not None
            if self.local_attention_backend == "triton":
                out_l, local_backend = local_attention(
                    q_,
                    k_,
                    v_,
                    self.local_neighbor_indices,
                    self.local_neighbor_mask,
                    use_triton_kernel=True,
                    torch_fallback=_torch_local,
                    block_n=self.local_attention_block_n,
                    validate_output=self.validate_triton_outputs,
                )
                return out_l
            if self.checkpoint_local_attention and self.training and torch.is_grad_enabled():
                return checkpoint(_torch_local, q_, k_, v_, use_reentrant=False, preserve_rng_state=False)
            return _torch_local(q_, k_, v_)

        def _selected_call(q_: Tensor = q, k_: Tensor = k_sel, v_: Tensor = v_sel) -> Tensor:
            nonlocal backend
            if not self.enable_selected_branch or self.num_selected_blocks <= 0:
                backend = BackendReport("triton_selected" if self.use_triton_kernel else "torch_fallback", "skipped", "selected branch disabled")
                return q_.new_zeros(batch, self.heads, q_.shape[2], self.dim_head)
            assert k_ is not None and v_ is not None
            out_s, backend = selected_attention(
                q_,
                k_,
                v_,
                self.block_volume,
                selected_block_indices,
                selected_block_mask,
                use_triton_kernel=self.use_triton_kernel,
                torch_fallback=self._selected_attention_torch,
                include_block_causal=False,
                validate_output=self.validate_triton_outputs,
            )
            return out_s

        branch_norms = {
            "local": q.new_tensor(float("nan")),
            "coarse": q.new_tensor(float("nan")),
            "selected": q.new_tensor(float("nan")),
        }

        def _combine_branches(
            q_: Tensor,
            k_local_: Tensor,
            v_local_: Tensor,
            summary_k_: Tensor,
            summary_v_: Tensor,
            k_sel_: Tensor,
            v_sel_: Tensor,
            gates_: Tensor,
        ) -> Tensor:
            local = None
            coarse = None
            selected = None
            if not local_all_disabled:
                local = _local_call(q_, k_local_, v_local_)
            if self.enable_compressed_branch:
                coarse = self._coarse_attention_torch(self._compressed_query(q_, q_unrotated), summary_k_, summary_v_)
            if self.enable_selected_branch and self.num_selected_blocks > 0:
                selected = _selected_call(q_, k_sel_, v_sel_)
            local_mix, coarse_mix, selected_mix, _, _, _ = self._prepare_branch_outputs(
                q_,
                local=local,
                coarse=coarse,
                selected=selected,
            )
            mixed, _ = self._mix_branch_outputs(
                q_,
                gates_,
                local=local_mix,
                coarse=coarse_mix,
                selected=selected_mix,
            )
            return mixed

        use_branch_checkpoint = (
            self.branch_output_fusion == "checkpointed"
            and self.training
            and torch.is_grad_enabled()
            and not return_aux
            and not profile_sections
        )
        if use_branch_checkpoint:
            dummy_local = q if k_local is None else k_local
            dummy_local_v = q if v_local is None else v_local
            dummy_sel = q if k_sel is None else k_sel
            dummy_sel_v = q if v_sel is None else v_sel
            out = checkpoint(
                _combine_branches,
                q,
                dummy_local,
                dummy_local_v,
                summary_k,
                summary_v,
                dummy_sel,
                dummy_sel_v,
                gates,
                use_reentrant=False,
                preserve_rng_state=False,
            )
        elif self.branch_output_fusion in {"sequential", "checkpointed"}:
            out = q.new_zeros(batch, self.heads, self.num_tokens_padded, self.dim_head)
            local = None
            coarse = None
            selected = None
            if local_all_disabled:
                local_backend = LocalBackendReport(
                    "triton_local" if self.local_attention_backend == "triton" else "torch_fallback",
                    "skipped",
                    "local branch disabled for all queries",
                )
            else:
                assert k_local is not None and v_local is not None
                local = _section("local_branch_time_ms", lambda: _local_call(q, k_local, v_local))
            if self.enable_compressed_branch:
                coarse = _section("coarse_branch_time_ms", lambda: self._coarse_attention_torch(self._compressed_query(q, q_unrotated), summary_k, summary_v))
            else:
                branch_norms["coarse"] = q.new_tensor(0.0)
            if self.enable_selected_branch and self.num_selected_blocks > 0:
                selected = _section("selected_attention_time_ms", _selected_call)
            else:
                branch_norms["selected"] = q.new_tensor(0.0)
                backend = BackendReport("triton_selected" if self.use_triton_kernel else "torch_fallback", "skipped", "selected branch disabled")
            local_mix, coarse_mix, selected_mix, branch_norms, branch_post_norms, selected_mixing_effective = self._prepare_branch_outputs(
                q,
                local=local,
                coarse=coarse,
                selected=selected,
            )
            out, _ = self._mix_branch_outputs(q, gates, local=local_mix, coarse=coarse_mix, selected=selected_mix)
        else:
            out_local = None
            out_coarse = None
            out_refine = None
            if not local_all_disabled:
                out_local = _section("local_branch_time_ms", _local_call)
            else:
                branch_norms["local"] = q.new_tensor(0.0)
                local_backend = LocalBackendReport(
                    "triton_local" if self.local_attention_backend == "triton" else "torch_fallback",
                    "skipped",
                    "local branch disabled",
                )
            if self.enable_compressed_branch:
                out_coarse = _section("coarse_branch_time_ms", lambda: self._coarse_attention_torch(self._compressed_query(q, q_unrotated), summary_k, summary_v))
            else:
                branch_norms["coarse"] = q.new_tensor(0.0)
            if self.enable_selected_branch and self.num_selected_blocks > 0:
                out_refine = _section("selected_attention_time_ms", _selected_call)
            else:
                branch_norms["selected"] = q.new_tensor(0.0)
                backend = BackendReport("triton_selected" if self.use_triton_kernel else "torch_fallback", "skipped", "selected branch disabled")
            out_local, out_coarse, out_refine, branch_norms, branch_post_norms, selected_mixing_effective = self._prepare_branch_outputs(
                q,
                local=out_local,
                coarse=out_coarse,
                selected=out_refine,
            )
            out, _ = self._mix_branch_outputs(q, gates, local=out_local, coarse=out_coarse, selected=out_refine)
        out = self.to_out(self._merge_heads(out)) + residual
        out = out * self.valid_token_mask.to(out.device).view(1, -1, 1)
        if profile_sections:
            _sync_if_needed()
            section_times_ms["total_attention_time_ms"] = (time.perf_counter() - total_start) * 1000.0
        if original_grid_format:
            out = self._unpack(out)
        if not return_aux:
            return out

        aux: Dict[str, Any] = {
            "backend_requested": backend.backend_requested,
            "backend_actual": backend.backend_actual,
            "fallback_reason": backend.fallback_reason,
            "selected_block_indices": selected_block_indices.detach(),
            "selected_block_mask": selected_block_mask.detach(),
            "route_scores": route_scores.detach(),
            "compression_residual": compression_residual.detach(),
            "residual_score": compression_residual.detach(),
            "route_relevance": route_relevance.detach(),
            "gates": gates.detach(),
            "valid_token_mask": self.valid_token_mask.detach(),
            "block_id_packed": self.block_id_packed.detach(),
            "atom_weights": atom_weights.detach(),
            "backend_report": BackendReport(backend.backend_requested, backend.backend_actual, backend.fallback_reason),
            "route_select_grad": self.route_select_grad,
            "route_backend_requested": route_backend.backend_requested,
            "route_backend_actual": route_backend.backend_actual,
            "route_fallback_reason": route_backend.fallback_reason,
            "route_granularity": self.route_granularity,
            "route_share_tile_size": self.route_share_tile_size,
            "route_sharing_factor": self._last_route_stats.get("route_sharing_factor", torch.tensor(1.0, device=out.device)).detach(),
            "route_scores_sparse": route_scores.shape[-1] == selected_block_indices.shape[-1],
            "route_materialize_scores_in_aux": self.route_materialize_scores_in_aux,
            "enabled_branches": ",".join(self.enabled_branches),
            "packed_branch_kv_projection": self.packed_branch_kv_projection,
            "skip_disabled_local_branch": self.skip_disabled_local_branch,
            "checkpoint_local_attention": self.checkpoint_local_attention,
            "branch_output_fusion": self.branch_output_fusion,
            "branch_output_norm": self.branch_output_norm,
            "branch_layer_scale_enabled": self.branch_layer_scale_enabled,
            "branch_layer_scale_local_mean": self.branch_layer_scale[0].detach().float().mean(),
            "branch_layer_scale_compressed_mean": self.branch_layer_scale[1].detach().float().mean(),
            "branch_layer_scale_selected_mean": self.branch_layer_scale[2].detach().float().mean(),
            "branch_mixer_mode": self.branch_mixer_mode,
            "branch_mixer_mode_effective": self.branch_mixer_mode,
            "selected_mixing_mode": self.selected_mixing_mode,
            "selected_mixing_mode_effective": selected_mixing_effective,
            "branch_output_checkpoint_active": use_branch_checkpoint,
            "local_attention_backend_requested": local_backend.backend_requested,
            "local_attention_backend_actual": local_backend.backend_actual,
            "local_attention_fallback_reason": local_backend.fallback_reason,
            "local_attention_backend": self.local_attention_backend,
            "local_attention_block_n": self.local_attention_block_n,
            "validate_triton_outputs": self.validate_triton_outputs,
            "pos_encoding": self.pos_encoding,
            "compressed_rope_mode": self.compressed_rope_mode,
            "rotary_base": self.rotary_base,
            "rotary_coordinate_mode": self.rotary_coordinate_mode,
            "rotary_axis_scales": ",".join(f"{float(x):g}" for x in self.rotary_axis_scales.detach().cpu().tolist()),
            "rotary_axis_pair_allocation": self.rotary_axis_pair_allocation,
            "rotary_axis_pair_counts": ",".join(str(int(x)) for x in self.rotary_axis_pair_counts_tuple),
            "coarse_attention_backend": self.coarse_attention_backend,
            "coarse_summary_pool_size": self.coarse_summary_pool_size,
            "layout": self.layout,
            "route_score_mode": self.route_score_mode,
            "route_backend": self.route_backend,
            "full_layer_execution": self.full_layer_execution,
            "query_tile_size": self.query_tile_size,
            "query_tile_checkpoint": self.query_tile_checkpoint,
            "route_block_q": self.route_block_q,
            "route_block_c": self.route_block_c,
            "route_shape_penalty_weight": self.route_shape_penalty_weight,
            "route_center_distance_weight": self.route_center_distance_weight,
            "route_center_distance_weight_explicit": self.route_center_distance_weight_explicit,
            "route_distance_normalization": self.route_distance_normalization,
            "route_distance_units": self.route_distance_units,
            "allow_raw_distance_on_probability_route": self.allow_raw_distance_on_probability_route,
            "branch_gate_mode": self.branch_gate_mode,
            "branch_gate_prior_schedule": self.branch_gate_prior_schedule,
            "branch_gate_prior_progress": self.branch_gate_prior_progress_tensor.detach(),
            "branch_gate_prior_local": self.branch_gate_prior_current_vec[0].detach(),
            "branch_gate_prior_compressed": self.branch_gate_prior_current_vec[1].detach(),
            "branch_gate_prior_selected": self.branch_gate_prior_current_vec[2].detach(),
            "gate_sum_mean": gates.detach().float().sum(dim=-1).mean(),
            "local_output_norm": branch_norms["local"],
            "compressed_output_norm": branch_norms["coarse"],
            "selected_output_norm": branch_norms["selected"],
            "local_post_output_norm": branch_post_norms["local"],
            "compressed_post_output_norm": branch_post_norms["coarse"],
            "selected_post_output_norm": branch_post_norms["selected"],
            "atom_assignment_mode": self.atom_assignment_mode,
            "atom_aux_loss": self._last_atom_stats.get("atom_aux_loss", torch.tensor(0.0, device=out.device)),
            "atom_balance_loss": self._last_atom_stats.get("atom_balance_loss", torch.tensor(0.0, device=out.device)).detach(),
            "atom_entropy_loss": self._last_atom_stats.get("atom_entropy_loss", torch.tensor(0.0, device=out.device)).detach(),
            "atom_orthogonality_loss": self._last_atom_stats.get("atom_orthogonality_loss", torch.tensor(0.0, device=out.device)).detach(),
            "atom_assignment_entropy_mean": self._last_atom_stats.get("atom_assignment_entropy_mean", torch.tensor(0.0, device=out.device)).detach(),
            "atom_effective_count": self._last_atom_stats.get("atom_effective_count", torch.tensor(1.0, device=out.device)).detach(),
            "atom_balance_mean": self._last_atom_stats.get("atom_balance_mean", torch.tensor(1.0, device=out.device)).detach(),
            "atom_cosine_abs_offdiag": self._last_atom_stats.get("atom_cosine_abs_offdiag", torch.tensor(0.0, device=out.device)).detach(),
            "atom_balance_loss_weight": self.atom_balance_loss_weight,
            "atom_entropy_loss_weight": self.atom_entropy_loss_weight,
            "atom_orthogonality_loss_weight": self.atom_orthogonality_loss_weight,
            "atom_temperature": self.atom_temperature,
            "route_residual_mode": self.route_residual_mode,
            "compressed_attention_mass_entropy": self._last_route_stats.get("compressed_attention_mass_entropy", torch.tensor(0.0)).detach(),
            "route_probability_sum_error": self._last_route_stats.get("route_probability_sum_error", torch.tensor(0.0)).detach(),
            "block_cov_trace": getattr(self, "block_cov_trace", torch.empty(0)).detach(),
            "block_diameter": getattr(self, "block_diameter", torch.empty(0)).detach(),
        }
        if profile_sections:
            aux["profile_times_ms"] = section_times_ms
        return out, aux


class FeedForward(nn.Module):
    """Pre-norm MLP residual block for packed or grid token tensors."""

    def __init__(self, dim: int, mult: int = 4):
        super().__init__()
        self.norm = nn.LayerNorm(dim)
        self.fc1 = nn.Linear(dim, dim * mult)
        self.fc2 = nn.Linear(dim * mult, dim)

    def forward(self, x: Tensor) -> Tensor:
        return x + self.fc2(F.gelu(self.fc1(self.norm(x))))


class HyperNSABlock(nn.Module):
    """Attention plus MLP block preserving HyperNSA aux reporting."""

    def __init__(self, dim: int, grid_shape: Sequence[int], **kwargs: Any):
        super().__init__()
        self.attn = HypergridMortonSparseAttention(dim=dim, grid_shape=grid_shape, **kwargs)
        self.ff = FeedForward(dim)

    def forward(
        self,
        x: Tensor,
        query_disable_local_mask: Tensor | None = None,
        return_aux: bool = False,
    ) -> Tensor | tuple[Tensor, Dict[str, Any]]:
        if return_aux:
            x, aux = self.attn(x, query_disable_local_mask=query_disable_local_mask, return_aux=True)
        else:
            x = self.attn(x, query_disable_local_mask=query_disable_local_mask)
            aux = None
        batch = x.shape[0]
        x = self.ff(x.reshape(batch, -1, x.shape[-1])).reshape_as(x)
        if return_aux:
            return x, aux
        return x


__all__ = [
    "HypergridMortonSparseAttention",
    "HyperNSABlock",
    "FeedForward",
    "block_morton_layout",
    "make_block_layout",
    "block_morton_block_contiguity",
    "plain_morton_block_contiguity",
    "pack_grid",
    "unpack_grid",
    "prod",
]
