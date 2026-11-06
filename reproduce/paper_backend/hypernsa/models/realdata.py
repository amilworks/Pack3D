from __future__ import annotations

import math
from typing import Any, Sequence

import torch
from torch import Tensor, nn
import torch.nn.functional as F

from hypernsa.attention.hypernsa_morton import HyperNSABlock
from hypernsa.attention.layout import block_morton_layout, build_local_neighbors, pack_grid, prod, unpack_grid
from hypernsa.models.hypernsa_nd import PatchEmbedND


class DenseAttentionBlock(nn.Module):
    def __init__(self, dim: int, heads: int, kv_heads: int, dim_head: int):
        super().__init__()
        self.heads = int(heads)
        self.kv_heads = int(kv_heads)
        self.dim_head = int(dim_head)
        self.num_grouped_queries = self.heads // self.kv_heads
        self.norm = nn.LayerNorm(dim)
        self.to_q = nn.Linear(dim, self.heads * self.dim_head, bias=False)
        self.to_k = nn.Linear(dim, self.kv_heads * self.dim_head, bias=False)
        self.to_v = nn.Linear(dim, self.kv_heads * self.dim_head, bias=False)
        self.to_out = nn.Linear(self.heads * self.dim_head, dim, bias=False)
        self.ff_norm = nn.LayerNorm(dim)
        self.ff = nn.Sequential(nn.Linear(dim, 4 * dim), nn.GELU(), nn.Linear(4 * dim, dim))

    def forward(self, x: Tensor, return_aux: bool = False):
        batch, *grid, dim = x.shape
        tokens = x.reshape(batch, -1, dim)
        residual = tokens
        z = self.norm(tokens)
        q = self.to_q(z).reshape(batch, -1, self.heads, self.dim_head).transpose(1, 2)
        k = self.to_k(z).reshape(batch, -1, self.kv_heads, self.dim_head).transpose(1, 2)
        v = self.to_v(z).reshape(batch, -1, self.kv_heads, self.dim_head).transpose(1, 2)
        k = k.repeat_interleave(self.num_grouped_queries, dim=1)
        v = v.repeat_interleave(self.num_grouped_queries, dim=1)
        out = F.scaled_dot_product_attention(q, k, v, dropout_p=0.0, is_causal=False)
        out = out.transpose(1, 2).contiguous().reshape(batch, -1, self.heads * self.dim_head)
        tokens = self.to_out(out) + residual
        tokens = tokens + self.ff(self.ff_norm(tokens))
        x = tokens.reshape(batch, *grid, dim)
        if not return_aux:
            return x
        return x, {"backend_requested": "dense_sdpa", "backend_actual": "dense_sdpa", "fallback_reason": ""}


class WindowAttentionBlock(nn.Module):
    def __init__(
        self,
        dim: int,
        grid_shape: Sequence[int],
        heads: int,
        kv_heads: int,
        dim_head: int,
        block_shape: Sequence[int],
        local_radius: Sequence[int] | int,
    ):
        super().__init__()
        self.dim = int(dim)
        self.grid_shape = tuple(int(x) for x in grid_shape)
        self.heads = int(heads)
        self.kv_heads = int(kv_heads)
        self.dim_head = int(dim_head)
        self.num_grouped_queries = self.heads // self.kv_heads
        layout = block_morton_layout(self.grid_shape, tuple(int(x) for x in block_shape))
        neighbors, neighbor_mask = build_local_neighbors(layout["coords_packed"], layout["valid_token_mask"], local_radius, layout["coord_to_packed_idx"])
        for key, value in layout.items():
            if key == "coord_to_packed_idx":
                continue
            if isinstance(value, Tensor):
                self.register_buffer(key, value, persistent=False)
            else:
                setattr(self, key, value)
        self.register_buffer("local_neighbor_indices", neighbors.long(), persistent=False)
        self.register_buffer("local_neighbor_mask", neighbor_mask.bool(), persistent=False)
        self.norm = nn.LayerNorm(dim)
        self.to_q = nn.Linear(dim, self.heads * self.dim_head, bias=False)
        self.to_k = nn.Linear(dim, self.kv_heads * self.dim_head, bias=False)
        self.to_v = nn.Linear(dim, self.kv_heads * self.dim_head, bias=False)
        self.to_out = nn.Linear(self.heads * self.dim_head, dim, bias=False)
        self.ff_norm = nn.LayerNorm(dim)
        self.ff = nn.Sequential(nn.Linear(dim, 4 * dim), nn.GELU(), nn.Linear(4 * dim, dim))

    def _pack(self, x: Tensor) -> Tensor:
        return pack_grid(x, self.padded_grid_shape, self.packed_order)

    def _unpack(self, x: Tensor) -> Tensor:
        return unpack_grid(x, self.grid_shape, self.padded_grid_shape, self.packed_order)

    def forward(self, x: Tensor, return_aux: bool = False):
        batch = x.shape[0]
        packed = self._pack(x)
        residual = packed
        z = self.norm(packed)
        q = self.to_q(z).reshape(batch, self.num_tokens_padded, self.heads, self.dim_head).permute(0, 2, 1, 3).contiguous()
        k = self.to_k(z).reshape(batch, self.num_tokens_padded, self.kv_heads, self.dim_head).permute(0, 2, 1, 3).contiguous()
        v = self.to_v(z).reshape(batch, self.num_tokens_padded, self.kv_heads, self.dim_head).permute(0, 2, 1, 3).contiguous()
        qg = q.reshape(batch, self.kv_heads, self.num_grouped_queries, self.num_tokens_padded, self.dim_head)
        b_idx = torch.arange(batch, device=x.device)[:, None, None, None]
        g_idx = torch.arange(self.kv_heads, device=x.device)[None, :, None, None]
        n_idx = self.local_neighbor_indices.to(x.device)[None, None, :, :]
        local_k = k[b_idx, g_idx, n_idx, :]
        local_v = v[b_idx, g_idx, n_idx, :]
        sim = torch.einsum("bgqnd,bgnwd->bgqnw", qg, local_k) * (self.dim_head**-0.5)
        sim = sim.masked_fill(~self.local_neighbor_mask.to(x.device).view(1, 1, 1, self.num_tokens_padded, -1), torch.finfo(sim.dtype).min)
        attn = sim.softmax(dim=-1)
        out = torch.einsum("bgqnw,bgnwd->bgqnd", attn, local_v).reshape(batch, self.heads, self.num_tokens_padded, self.dim_head)
        packed = self.to_out(out.permute(0, 2, 1, 3).reshape(batch, self.num_tokens_padded, self.heads * self.dim_head)) + residual
        packed = packed + self.ff(self.ff_norm(packed))
        packed = packed * self.valid_token_mask.to(packed.device).view(1, -1, 1)
        x = self._unpack(packed)
        if not return_aux:
            return x
        return x, {
            "backend_requested": "window_attention",
            "backend_actual": "window_attention",
            "fallback_reason": "",
        }


class WindowMLPMatchedBlock(nn.Module):
    """Local-only control with an extra token MLP adapter.

    This is a reviewer-control block, not a proposed method.  It keeps the same
    local attention path as the Window baseline and spends a comparable number
    of extra parameters to a compressed/global branch without giving the model
    any nonlocal summaries.
    """

    def __init__(
        self,
        dim: int,
        grid_shape: Sequence[int],
        heads: int,
        kv_heads: int,
        dim_head: int,
        block_shape: Sequence[int],
        local_radius: Sequence[int] | int,
        adapter_hidden: int = 256,
    ):
        super().__init__()
        self.window = WindowAttentionBlock(dim, grid_shape, heads, kv_heads, dim_head, block_shape, local_radius)
        hidden = max(1, int(adapter_hidden))
        self.adapter_norm = nn.LayerNorm(dim)
        self.adapter = nn.Sequential(nn.Linear(dim, hidden), nn.GELU(), nn.Linear(hidden, dim))
        self.adapter_hidden = hidden

    def forward(self, x: Tensor, return_aux: bool = False):
        if return_aux:
            x, aux = self.window(x, return_aux=True)
        else:
            x = self.window(x, return_aux=False)
            aux = None
        residual = x
        x = x + self.adapter(self.adapter_norm(x))
        if not return_aux:
            return x
        assert aux is not None
        aux = dict(aux)
        aux.update(
            {
                "backend_requested": "window_mlp_matched",
                "backend_actual": "window_mlp_matched",
                "fallback_reason": "",
                "window_adapter_hidden": self.adapter_hidden,
            }
        )
        return x, aux


class RealDataBackbone(nn.Module):
    def __init__(
        self,
        *,
        model_name: str,
        input_shape: Sequence[int],
        in_channels: int,
        patch_shape: Sequence[int],
        dim: int,
        depth: int,
        heads: int,
        kv_heads: int,
        dim_head: int,
        block_shape: Sequence[int],
        local_radius: Sequence[int] | int,
        num_summary_atoms: int = 2,
        num_selected_blocks: int = 2,
        residual_weight: float = 0.25,
        distance_weight: float = 0.10,
        use_triton_kernel: bool = True,
        separate_branch_kv: bool = True,
        route_select_grad: bool = False,
        packed_branch_kv_projection: bool = True,
        skip_disabled_local_branch: bool = True,
        checkpoint_local_attention: bool = False,
        local_attention_backend: str = "torch",
        local_attention_block_n: int = 16,
        branch_output_fusion: str = "standard",
        coarse_attention_backend: str = "sdpa",
        coarse_summary_pool_size: int = 1,
        layout: str = "native",
        route_score_mode: str = "logsumexp_logits_current",
        route_backend: str = "torch_full",
        route_block_q: int = 16,
        route_block_c: int = 32,
        route_materialize_scores_in_aux: bool = True,
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
        branch_layer_scale_init: float | Sequence[float] | dict[str, float] = 1.0,
        branch_mixer_mode: str = "gated_sum",
        branch_gate_bias_init: float | Sequence[float] | dict[str, float] = 0.0,
        branch_gate_prior_schedule: str = "none",
        branch_gate_prior_start: float | Sequence[float] | dict[str, float] = 0.0,
        branch_gate_prior_end: float | Sequence[float] | dict[str, float] = 0.0,
        selected_mixing_mode: str = "standard",
        validate_triton_outputs: bool = False,
        window_adapter_hidden: int = 256,
        pos_encoding: str = "learned_full",
        rotary_base: float = 10000.0,
        rotary_coordinate_mode: str = "raw_grid",
        rotary_axis_scales: Sequence[float] | None = None,
        rotary_axis_pair_allocation: str = "balanced",
        learned_low_rank_pe_rank: int = 8,
        coordinate_fourier_bands: int = 16,
        coordinate_fourier_hidden: int = 128,
        compressed_rope_mode: str = "token_before_compression",
    ):
        super().__init__()
        self.model_name = model_name
        self.input_shape = tuple(int(x) for x in input_shape)
        self.in_channels = int(in_channels)
        self.patch_shape = tuple(int(x) for x in patch_shape)
        self.grid_shape = tuple(s // p for s, p in zip(self.input_shape, self.patch_shape))
        self.block_shape = tuple(int(x) for x in block_shape)
        self.layout = str(layout)
        self.dim = int(dim)
        pos_aliases = {"learned": "learned_full"}
        self.pos_encoding = pos_aliases.get(str(pos_encoding), str(pos_encoding))
        valid_pos_encodings = {
            "learned_full",
            "learned_separable_3d",
            "learned_low_rank_3d",
            "coordinate_fourier_mlp",
            "none",
            "axial_rope",
            "packed_sequence_rope",
            "relative_position_bias_3d",
            "alibi_3d",
        }
        if self.pos_encoding not in valid_pos_encodings:
            raise ValueError(f"pos_encoding must be one of {sorted(valid_pos_encodings)}")
        if self.pos_encoding in {"axial_rope", "packed_sequence_rope", "relative_position_bias_3d", "alibi_3d"} and model_name not in {"hypernsa", "hypernsa_s", "hypernsa_l", "hypernsa_lm"}:
            raise ValueError(f"pos_encoding='{self.pos_encoding}' is currently implemented for HyperNSA/Window+Global blocks")
        self.rotary_base = float(rotary_base)
        self.rotary_coordinate_mode = str(rotary_coordinate_mode)
        self.rotary_axis_scales = tuple(float(x) for x in (rotary_axis_scales or [1.0 for _ in self.grid_shape]))
        self.rotary_axis_pair_allocation = str(rotary_axis_pair_allocation)
        self.compressed_rope_mode = str(compressed_rope_mode)
        self.learned_low_rank_pe_rank = int(learned_low_rank_pe_rank)
        self.coordinate_fourier_bands = int(coordinate_fourier_bands)
        self.coordinate_fourier_hidden = int(coordinate_fourier_hidden)
        self.patch = PatchEmbedND(in_channels, self.patch_shape, self.dim)
        if self.pos_encoding == "learned_full":
            self.pos = nn.Parameter(torch.zeros(1, *self.grid_shape, self.dim))
            nn.init.trunc_normal_(self.pos, std=0.02)
        else:
            self.register_parameter("pos", None)
        if self.pos_encoding == "learned_separable_3d":
            self.pos_axes = nn.ParameterList([nn.Parameter(torch.zeros(int(size), self.dim)) for size in self.grid_shape])
            for param in self.pos_axes:
                nn.init.trunc_normal_(param, std=0.02)
        else:
            self.pos_axes = nn.ParameterList()
        if self.pos_encoding == "learned_low_rank_3d":
            rank = max(1, self.learned_low_rank_pe_rank)
            self.pos_low_rank_axes = nn.ParameterList([nn.Parameter(torch.zeros(int(size), rank)) for size in self.grid_shape])
            self.pos_low_rank_projection = nn.Linear(rank, self.dim, bias=False)
            for param in self.pos_low_rank_axes:
                nn.init.trunc_normal_(param, std=0.02)
            nn.init.trunc_normal_(self.pos_low_rank_projection.weight, std=0.02)
        else:
            self.pos_low_rank_axes = nn.ParameterList()
            self.pos_low_rank_projection = None
        if self.pos_encoding == "coordinate_fourier_mlp":
            bands = max(1, self.coordinate_fourier_bands)
            hidden = max(1, self.coordinate_fourier_hidden)
            self.register_buffer("coordinate_fourier_freqs", torch.pow(2.0, torch.arange(bands, dtype=torch.float32)), persistent=False)
            fourier_dim = len(self.grid_shape) * (1 + 2 * bands)
            self.coordinate_fourier_mlp = nn.Sequential(
                nn.Linear(fourier_dim, hidden),
                nn.GELU(),
                nn.Linear(hidden, self.dim),
            )
        else:
            self.register_buffer("coordinate_fourier_freqs", torch.empty(0), persistent=False)
            self.coordinate_fourier_mlp = None
        blocks = []
        for _ in range(int(depth)):
            if model_name in {"hypernsa", "hypernsa_s", "hypernsa_l", "hypernsa_lm"}:
                blocks.append(
                    HyperNSABlock(
                        dim=self.dim,
                        grid_shape=self.grid_shape,
                        heads=heads,
                        kv_heads=kv_heads,
                        dim_head=dim_head,
                        block_shape=self.block_shape,
                        local_radius=local_radius,
                        num_summary_atoms=num_summary_atoms,
                        num_selected_blocks=num_selected_blocks,
                        residual_weight=residual_weight,
                        distance_weight=distance_weight,
                        use_triton_kernel=use_triton_kernel,
                        separate_branch_kv=separate_branch_kv,
                        route_select_grad=route_select_grad,
                        packed_branch_kv_projection=packed_branch_kv_projection,
                        skip_disabled_local_branch=skip_disabled_local_branch,
                        checkpoint_local_attention=checkpoint_local_attention,
                        local_attention_backend=local_attention_backend,
                        local_attention_block_n=local_attention_block_n,
                        branch_output_fusion=branch_output_fusion,
                        coarse_attention_backend=coarse_attention_backend,
                        coarse_summary_pool_size=coarse_summary_pool_size,
                        layout=self.layout,
                        route_score_mode=route_score_mode,
                        route_backend=route_backend,
                        route_block_q=route_block_q,
                        route_block_c=route_block_c,
                        route_materialize_scores_in_aux=route_materialize_scores_in_aux,
                        route_shape_penalty_weight=route_shape_penalty_weight,
                        route_center_distance_weight=route_center_distance_weight,
                        route_distance_normalization=route_distance_normalization,
                        allow_raw_distance_on_probability_route=allow_raw_distance_on_probability_route,
                        branch_gate_mode=branch_gate_mode,
                        atom_assignment_mode=atom_assignment_mode,
                        route_residual_mode=route_residual_mode,
                        atom_balance_loss_weight=atom_balance_loss_weight,
                        atom_entropy_loss_weight=atom_entropy_loss_weight,
                        atom_orthogonality_loss_weight=atom_orthogonality_loss_weight,
                        atom_temperature=atom_temperature,
                        full_layer_execution=full_layer_execution,
                        query_tile_size=query_tile_size,
                        query_tile_checkpoint=query_tile_checkpoint,
                        route_granularity=route_granularity,
                        route_share_tile_size=route_share_tile_size,
                        enabled_branches=enabled_branches,
                        branch_output_norm=branch_output_norm,
                        branch_layer_scale=branch_layer_scale,
                        branch_layer_scale_init=branch_layer_scale_init,
                        branch_mixer_mode=branch_mixer_mode,
                        branch_gate_bias_init=branch_gate_bias_init,
                        branch_gate_prior_schedule=branch_gate_prior_schedule,
                        branch_gate_prior_start=branch_gate_prior_start,
                        branch_gate_prior_end=branch_gate_prior_end,
                        selected_mixing_mode=selected_mixing_mode,
                        validate_triton_outputs=validate_triton_outputs,
                        pos_encoding=self.pos_encoding if self.pos_encoding in {"axial_rope", "packed_sequence_rope", "relative_position_bias_3d", "alibi_3d"} else "none",
                        rotary_base=self.rotary_base,
                        rotary_coordinate_mode=self.rotary_coordinate_mode,
                        rotary_axis_scales=self.rotary_axis_scales,
                        rotary_axis_pair_allocation=self.rotary_axis_pair_allocation,
                        compressed_rope_mode=self.compressed_rope_mode,
                    )
                )
            elif model_name == "dense":
                blocks.append(DenseAttentionBlock(self.dim, heads, kv_heads, dim_head))
            elif model_name == "window":
                blocks.append(
                    WindowAttentionBlock(
                        self.dim,
                        self.grid_shape,
                        heads,
                        kv_heads,
                        dim_head,
                        self.block_shape,
                        local_radius,
                    )
                )
            elif model_name == "window_mlp_matched":
                blocks.append(
                    WindowMLPMatchedBlock(
                        self.dim,
                        self.grid_shape,
                        heads,
                        kv_heads,
                        dim_head,
                        self.block_shape,
                        local_radius,
                        adapter_hidden=window_adapter_hidden,
                    )
                )
            else:
                raise ValueError(f"unknown model_name={model_name}")
        self.blocks = nn.ModuleList(blocks)
        self.norm = nn.LayerNorm(self.dim)

    def _learned_separable_position(self, *, device: torch.device, dtype: torch.dtype) -> Tensor:
        out = torch.zeros(*self.grid_shape, self.dim, device=device, dtype=dtype)
        for axis, param in enumerate(self.pos_axes):
            view = [1 for _ in self.grid_shape] + [self.dim]
            view[axis] = int(self.grid_shape[axis])
            out = out + param.to(device=device, dtype=dtype).view(*view)
        return out.unsqueeze(0)

    def _learned_low_rank_position(self, *, device: torch.device, dtype: torch.dtype) -> Tensor:
        if self.pos_low_rank_projection is None:
            raise RuntimeError("learned low-rank PE projection is not initialized")
        rank = max(1, self.learned_low_rank_pe_rank)
        latent = torch.ones(*self.grid_shape, rank, device=device, dtype=dtype)
        for axis, param in enumerate(self.pos_low_rank_axes):
            view = [1 for _ in self.grid_shape] + [rank]
            view[axis] = int(self.grid_shape[axis])
            latent = latent * param.to(device=device, dtype=dtype).view(*view)
        pos = self.pos_low_rank_projection(latent.float()).to(dtype=dtype)
        return pos.unsqueeze(0)

    def _coordinate_fourier_position(self, *, device: torch.device, dtype: torch.dtype) -> Tensor:
        if self.coordinate_fourier_mlp is None:
            raise RuntimeError("coordinate Fourier MLP is not initialized")
        axes = []
        for size in self.grid_shape:
            if int(size) <= 1:
                axes.append(torch.zeros(int(size), device=device, dtype=torch.float32))
            else:
                axes.append(torch.linspace(-1.0, 1.0, int(size), device=device, dtype=torch.float32))
        mesh = torch.meshgrid(*axes, indexing="ij")
        coords = torch.stack(mesh, dim=-1)
        freqs = self.coordinate_fourier_freqs.to(device=device, dtype=torch.float32)
        feats = [coords]
        expanded = coords[..., None] * freqs.view(*([1] * (coords.ndim - 1)), -1) * math.pi
        feats.append(expanded.sin().flatten(-2))
        feats.append(expanded.cos().flatten(-2))
        inp = torch.cat(feats, dim=-1)
        pos = self.coordinate_fourier_mlp(inp).to(dtype=dtype)
        return pos.unsqueeze(0)

    def _position_tensor(self, *, device: torch.device, dtype: torch.dtype) -> Tensor | None:
        if self.pos is not None:
            return self.pos.to(device=device, dtype=dtype)
        if self.pos_encoding == "learned_separable_3d":
            return self._learned_separable_position(device=device, dtype=dtype)
        if self.pos_encoding == "learned_low_rank_3d":
            return self._learned_low_rank_position(device=device, dtype=dtype)
        if self.pos_encoding == "coordinate_fourier_mlp":
            return self._coordinate_fourier_position(device=device, dtype=dtype)
        return None

    def set_branch_gate_prior_progress(self, progress: float) -> None:
        for block in self.blocks:
            if isinstance(block, HyperNSABlock):
                block.attn.set_branch_gate_prior_progress(progress)

    def forward_features(
        self,
        x: Tensor,
        query_disable_local_mask: Tensor | None = None,
        return_aux: bool = False,
        token_condition: Tensor | None = None,
    ):
        z = self.patch(x)
        pos = self._position_tensor(device=x.device, dtype=z.dtype)
        if pos is not None:
            z = z + pos
        if token_condition is not None:
            if token_condition.shape != (x.shape[0], self.dim):
                raise ValueError(
                    f"token_condition must have shape {(x.shape[0], self.dim)}, got {tuple(token_condition.shape)}"
                )
            view_shape = (x.shape[0],) + (1,) * len(self.grid_shape) + (self.dim,)
            z = z + token_condition.to(device=z.device, dtype=z.dtype).view(view_shape)
        aux_layers = []
        for block in self.blocks:
            if return_aux:
                if isinstance(block, HyperNSABlock):
                    z, aux = block(z, query_disable_local_mask=query_disable_local_mask, return_aux=True)
                else:
                    z, aux = block(z, return_aux=True)
                aux_layers.append(aux)
            else:
                if isinstance(block, HyperNSABlock):
                    z = block(z, query_disable_local_mask=query_disable_local_mask)
                else:
                    z = block(z)
        z = self.norm(z)
        if return_aux:
            aux = dict(aux_layers[-1]) if aux_layers else {}
            aux["layers"] = aux_layers
            return z, aux
        return z

    def forward(
        self,
        x: Tensor,
        query_disable_local_mask: Tensor | None = None,
        return_aux: bool = False,
        token_condition: Tensor | None = None,
    ):
        return self.forward_features(
            x,
            query_disable_local_mask=query_disable_local_mask,
            return_aux=return_aux,
            token_condition=token_condition,
        )


class RealDataClassifier(nn.Module):
    def __init__(self, num_classes: int, **backbone_kwargs: Any):
        super().__init__()
        self.backbone = RealDataBackbone(**backbone_kwargs)
        self.head = nn.Linear(self.backbone.dim, int(num_classes))

    def forward(self, x: Tensor, query_disable_local_mask: Tensor | None = None, return_aux: bool = False):
        if return_aux:
            features, aux = self.backbone(x, query_disable_local_mask=query_disable_local_mask, return_aux=True)
        else:
            features = self.backbone(x, query_disable_local_mask=query_disable_local_mask)
            aux = None
        pooled = features.reshape(features.shape[0], -1, features.shape[-1]).mean(dim=1)
        logits = self.head(pooled)
        if return_aux:
            return logits, aux, pooled
        return logits


def patch_targets(x: Tensor, patch_shape: Sequence[int]) -> Tensor:
    batch, channels, *spatial = x.shape
    patch_shape = tuple(int(p) for p in patch_shape)
    grid = [s // p for s, p in zip(spatial, patch_shape)]
    pieces = [batch, channels]
    for g, p in zip(grid, patch_shape):
        pieces.extend([g, p])
    z = x.reshape(*pieces)
    ndim = len(grid)
    perm = [0]
    perm.extend(2 + 2 * i for i in range(ndim))
    perm.append(1)
    perm.extend(3 + 2 * i for i in range(ndim))
    z = z.permute(*perm).contiguous()
    return z.reshape(batch, prod(grid), channels * prod(patch_shape))
