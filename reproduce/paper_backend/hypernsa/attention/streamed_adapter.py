"""Explicit opt-in wrapper; historical models and checkpoints are not rewritten."""

import torch
from torch import nn

from .hypernsa_morton import HypergridMortonSparseAttention
from pack3d import pack3d_streamed, prepare_geometry


class StreamedPACK3D(nn.Module):
    """Wrap an existing Allen-15-contract attention layer, preserving its weights.

    Load historical state_dicts into ``layer`` before wrapping. This module's
    state_dict has a ``layer.`` prefix. Projection, axial RoPE, normalization,
    gate calculation and the outer residual retain their historical code.
    No historical ``forward`` or backend settings are monkey-patched.
    """

    _GEOMETRY_NAMES = ("local_neighbor_indices", "local_neighbor_mask", "block_token_indices",
                       "block_valid_mask", "valid_token_mask", "packed_order", "coords_packed")

    def __init__(self, layer: HypergridMortonSparseAttention):
        super().__init__()
        if not isinstance(layer, HypergridMortonSparseAttention):
            raise TypeError("expected HypergridMortonSparseAttention")
        self.layer = layer
        self._check_contract()
        if not bool(layer.valid_token_mask.all()):
            raise ValueError("adapter currently requires an unpadded token grid")
        nb = layer.local_neighbor_indices.masked_fill(~layer.local_neighbor_mask, -1)
        blocks = layer.block_token_indices.masked_fill(~layer.block_valid_mask, -1)
        self.geometry = prepare_geometry(nb, blocks, layer.coarse_summary_pool_size).to(layer.to_q.weight.device)
        self._layout_stamp = self._stamp()

    def _check_contract(self):
        l = self.layer
        expected = {"ndim": 3, "num_summary_atoms": 1, "atom_assignment_mode": "single_atom",
                    "enable_local_branch": True, "enable_compressed_branch": True,
                    "enable_selected_branch": False, "branch_mixer_mode": "local_residual_global",
                    "branch_output_norm": "none", "pos_encoding": "axial_rope",
                    "compressed_rope_mode": "token_before_compression", "full_layer_execution": "full",
                    "atom_balance_loss_weight": 0., "atom_entropy_loss_weight": 0.,
                    "atom_orthogonality_loss_weight": 0.}
        for name, value in expected.items():
            if getattr(l, name) != value:
                raise ValueError(f"unsupported adapter contract: {name}={getattr(l, name)!r}, expected {value!r}")
        if l.dim_head not in (16, 32, 64, 128) or not 1 <= l.coarse_summary_pool_size <= 32:
            raise ValueError("unsupported head dimension or summary pool size")

    def _stamp(self):
        return (self.layer.coarse_summary_pool_size,
                tuple((id(t), t._version) for t in (getattr(self.layer, n) for n in self._GEOMETRY_NAMES)))

    def _apply(self, fn, recurse=True):
        super()._apply(fn, recurse=recurse)
        self.geometry = self.geometry.to(self.layer.to_q.weight.device)
        self._layout_stamp = self._stamp()
        return self

    def forward(self, x, query_disable_local_mask=None, return_aux=False, profile_sections=False):
        self._check_contract()
        if self._stamp() != self._layout_stamp:
            raise RuntimeError("layout buffers changed; construct a new adapter for the new layout")
        if query_disable_local_mask is not None or profile_sections:
            raise ValueError("query-local disabling and historical section profiling are unsupported")
        l = self.layer
        grid = x.ndim == l.ndim + 2
        if grid:
            if tuple(x.shape[1:-1]) != l.grid_shape:
                raise ValueError("input grid shape mismatch")
            x = l._pack(x)
        if x.ndim != 3 or x.shape[1:] != (l.num_tokens_padded, l.dim):
            raise ValueError("input must be the configured grid or [batch, packed_tokens, dim]")
        residual, batch = x, x.shape[0]
        x = l.norm(x)
        q = l._apply_axial_rope(l._split_q(l.to_q(x)), l.coords_packed)
        (kl, vl), (kg, vg), _ = l._project_all_kv(x, need_local=True, need_selected=False)
        logits = l.gate_proj(x).reshape(batch, l.num_tokens_padded, l.heads, 3).permute(0, 2, 1, 3)
        logits = l._apply_branch_gate_prior(logits)
        if l.branch_gate_mode == "softmax":
            gates = l._mask_branch_logits(logits, None).softmax(-1)
        else:
            gates = l._apply_sigmoid_branch_mask(logits.sigmoid(), None)
            if l.branch_gate_mode == "sigmoid_normalized":
                gates = gates / gates.sum(-1, keepdim=True).clamp_min(1e-6)
        # The historical residual is conditional on a positive local gate.
        # Fail explicitly on underflow instead of silently changing that rule.
        if not bool(torch.isfinite(gates).all() & (gates[..., 0] > 0).all()):
            raise RuntimeError("nonfinite or exact-zero local gate; residual contract would change")
        if l.branch_layer_scale_enabled:
            sl, sg = l.branch_layer_scale[:2].to(q.dtype).unbind(0)
        else:
            sl = sg = q.new_ones(l.dim_head)
        mixed = pack3d_streamed(q, kl, vl, kg, vg, l.atom_logits.weight[0],
                               l.atom_rel_bias[:, 0], gates[..., 1], sl, sg, self.geometry,
                               temperature=max(l.atom_temperature, 1e-6))
        out = l.to_out(l._merge_heads(mixed)) + residual
        if grid:
            out = l._unpack(out)
        if return_aux:
            return out, {"backend_actual": "pack3d_streamed_2026_11_04",
                         "fallback_reason": "", "num_pooled_summaries": self.geometry.num_summaries,
                         "single_gpu_launch": False, "historical_aux_metrics_available": False}
        return out
