"""A small principal-contract attention layer, independent of task decoders."""
import math

import torch
from torch import nn

from .geometry import TokenLayout
from .reference import pack3d_reference
from .rope import axial_rope, balanced_pairs


class PACK3DAttention(nn.Module):
    """Local residual plus gated compressed attention and an outer residual.

    Input/output: [batch,packed_tokens,dim]. Layout metadata must travel with
    the tokens. Separate local/global K/V projections, one learned fine atom,
    and two-stage compression implement the principal mathematical contract.
    No selected branch, dropout, decoder, or implicit backend substitution.

    This clean API is not state-dict compatible with the historical layer.
    The reproduction adapter preserves historical checkpoint parameter names.
    """

    def __init__(self, dim, *, heads=4, kv_heads=2, head_dim=32, block_volume=8,
                 backend="reference", position_encoding="axial", temperature=1.0):
        super().__init__()
        if any(type(v) is not int or v <= 0 for v in (dim, heads, kv_heads, head_dim, block_volume)):
            raise ValueError("dimensions must be positive integers")
        if heads % kv_heads or head_dim not in (16, 32, 64, 128) or block_volume > 64:
            raise ValueError("unsupported grouped-head dimensions or block volume")
        if backend not in ("reference", "triton"):
            raise ValueError("backend must be explicitly reference or triton")
        if position_encoding not in ("axial", "packed"):
            raise ValueError("position_encoding must be axial or packed")
        if not math.isfinite(temperature) or temperature <= 0:
            raise ValueError("temperature must be finite and positive")
        self.dim, self.heads, self.kv_heads, self.head_dim = dim, heads, kv_heads, head_dim
        self.backend, self.position_encoding = backend, position_encoding
        self.temperature = float(temperature)
        self.norm = nn.LayerNorm(dim)
        self.to_q = nn.Linear(dim, heads * head_dim, bias=False)
        self.to_kv = nn.Linear(dim, 4 * kv_heads * head_dim, bias=False)
        self.pool_weight = nn.Parameter(torch.empty(head_dim))
        nn.init.uniform_(self.pool_weight, -1 / math.sqrt(head_dim), 1 / math.sqrt(head_dim))
        self.slot_bias = nn.Parameter(torch.empty(block_volume))
        nn.init.normal_(self.slot_bias, std=0.02)
        self.gate = nn.Linear(dim, heads * 2)
        nn.init.zeros_(self.gate.bias)
        self.local_scale = nn.Parameter(torch.ones(head_dim))
        self.global_scale = nn.Parameter(torch.full((head_dim,), 0.25))
        self.to_out = nn.Linear(heads * head_dim, dim, bias=False)

    def forward(self, x, layout: TokenLayout):
        layout.check_unmodified()
        if x.ndim != 3 or x.shape[1:] != (layout.geometry.num_tokens, self.dim):
            raise ValueError("x must be [batch,layout_tokens,dim]")
        if x.device != layout.coords.device:
            raise ValueError("x and layout are on different devices; move both with .to(device)")
        if layout.geometry.blocks.shape[1] != len(self.slot_bias):
            raise ValueError("layout canonical slot count must match block_volume")
        if self.backend not in ("reference", "triton"):
            raise ValueError("unknown backend; implicit fallback is disabled")
        residual, b, n = x, x.shape[0], x.shape[1]
        x = self.norm(x)
        q = self.to_q(x).reshape(b, n, self.heads, self.head_dim).transpose(1, 2)
        kl, vl, kg, vg = (t.reshape(b, n, self.kv_heads, self.head_dim).transpose(1, 2)
                          for t in self.to_kv(x).chunk(4, -1))
        coords, pairs = layout.coords, balanced_pairs(self.head_dim)
        if self.position_encoding == "packed":
            seq = torch.arange(n, device=x.device)
            coords = torch.stack((seq, torch.zeros_like(seq), torch.zeros_like(seq)), -1)
            pairs = (self.head_dim // 2, 0, 0)
        elif self.position_encoding != "axial":
            raise ValueError("unknown position_encoding")
        q, kl, kg = (axial_rope(t, coords, pairs=pairs) for t in (q, kl, kg))
        gates = self.gate(x).reshape(b, n, self.heads, 2).softmax(-1)
        gate = gates[..., 1].transpose(1, 2)
        core = pack3d_reference
        if self.backend == "triton":
            from .backends.triton.autograd import pack3d_streamed
            core = pack3d_streamed
        out = core(q, kl, vl, kg, vg, self.pool_weight, self.slot_bias, gate,
                   self.local_scale, self.global_scale, layout.geometry, temperature=self.temperature)
        return residual + self.to_out(out.transpose(1, 2).reshape(b, n, -1))
