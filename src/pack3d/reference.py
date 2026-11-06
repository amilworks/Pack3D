"""Small differentiable PyTorch oracle; not a high-token execution path."""
import math
import torch
from .geometry import Pack3DGeometry
from ._validation import _validate_inputs
from .compression import compress_summaries

def pack3d_reference(q, kl, vl, kg, vg, weight, bias, gate, sl, sg,
                    geometry: Pack3DGeometry, *, temperature=1.0):
    """Small-shape differentiable oracle, intentionally not a fast backend."""
    _validate_inputs(q, kl, vl, kg, vg, weight, bias, gate, sl, sg, geometry, temperature)
    b, h, n, d = q.shape
    if (b * h * n * geometry.num_summaries > 8_000_000
            or b * h * n * geometry.neighbors.shape[1] * d > 32_000_000):
        raise ValueError("dense reference guard: use small shapes for correctness")
    g = kl.shape[1]
    # Keep double precision for gradcheck; accumulate low-precision inputs in fp32.
    dtype = torch.float64 if q.dtype == torch.float64 else torch.float32
    qf, klf, vlf, kgf, vgf = (t.to(dtype) for t in (q, kl, vl, kg, vg))
    sk, sv = compress_summaries(kgf, vgf, weight, bias, geometry, temperature=temperature)
    sk, sv = sk.repeat_interleave(h // g, 1), sv.repeat_interleave(h // g, 1)
    og = ((qf @ sk.transpose(-1, -2)) / math.sqrt(d)).softmax(-1) @ sv
    ni = geometry.neighbors.long()
    ok = ni >= 0
    lk = klf.repeat_interleave(h // g, 1)[:, :, ni.clamp_min(0)]
    lv = vlf.repeat_interleave(h // g, 1)[:, :, ni.clamp_min(0)]
    scores = (qf[..., None, :] * lk).sum(-1) / math.sqrt(d)
    scores = scores.masked_fill(~ok, -torch.inf)
    scores = torch.where(ok.any(-1)[None, None, :, None], scores, torch.zeros_like(scores))
    ol = (scores.softmax(-1)[..., None] * ok[..., None] * lv).sum(-2)
    return (sl.to(dtype) * ol + gate.to(dtype)[..., None] * sg.to(dtype) * og).to(q.dtype)

