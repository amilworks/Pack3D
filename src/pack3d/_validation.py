"""Shared projected-tensor contract checks."""
import math

def _validate_inputs(q, kl, vl, kg, vg, weight, bias, gate, sl, sg, geometry, temperature):
    geometry.check_unmodified()
    if q.ndim != 4 or min(q.shape) < 1:
        raise ValueError("Q must have shape [batch, query_heads, tokens, head_dim]")
    b, h, n, d = q.shape
    if kl.ndim != 4 or kl.shape[0] != b or kl.shape[2:] != (n, d):
        raise ValueError("local K has incompatible dimensions")
    if not 0 < kl.shape[1] <= h or h % kl.shape[1]:
        raise ValueError("query heads must be divisible by KV heads")
    if any(t.shape != kl.shape for t in (vl, kg, vg)):
        raise ValueError("all branch K/V tensors must have matching shapes")
    if any(t.dtype != q.dtype for t in (kl, vl, kg, vg)):
        raise ValueError("Q/K/V must have the same dtype")
    if d not in (16, 32, 64, 128):
        raise ValueError("supported head dimensions are 16, 32, 64 and 128")
    if q.numel() >= 2**31 or b * kl.shape[1] * 32 * geometry.num_summaries * d >= 2**31:
        raise ValueError("shape exceeds the 32-bit kernel indexing limit")
    pool_tile = (1 << (geometry.pool_size - 1).bit_length())
    slot_tile = (1 << (geometry.blocks.shape[1] - 1).bit_length())
    if pool_tile * slot_tile * d > 32768:
        raise ValueError("pool x slot x head_dim register tile exceeds the supported budget")
    if weight.shape != (d,) or bias.shape != (geometry.blocks.shape[1],):
        raise ValueError("pool scorer/slot bias shape mismatch")
    if gate.shape != (b, h, n) or sl.shape != (d,) or sg.shape != (d,):
        raise ValueError("gate or channelwise branch scale shape mismatch")
    if n != geometry.num_tokens:
        raise ValueError("geometry token count does not match Q")
    all_tensors = (q, kl, vl, kg, vg, weight, bias, gate, sl, sg, *geometry.tensors)
    if any(t.device != q.device for t in all_tensors):
        raise ValueError("all tensors and prepared geometry must be on the same device")
    if any(not t.is_floating_point() for t in all_tensors[:10]):
        raise ValueError("attention inputs must be floating point")
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be finite and positive")


