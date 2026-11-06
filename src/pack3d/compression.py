"""The two summary stages, written separately for inspection and testing."""
import math

import torch


def compress_summaries(keys, values, weight, bias, geometry, *, temperature=1.0):
    """Pool rotated keys and unrotated values, [B,Hkv,N,D] -> [B,Hkv,M,D].

    Fine weights are softmax(weight dot rotated_key / temperature + slot_bias).
    Empty fine blocks contribute neither mass nor count to the coarse mean.
    Reductions use FP32 (FP64 for double inputs). The caller controls casts.
    This readable path materializes block features; use it only at small sizes.
    """
    geometry.check_unmodified()
    if keys.ndim != 4 or values.shape != keys.shape or keys.shape[2] != geometry.num_tokens:
        raise ValueError("keys/values must match [batch,kv_heads,tokens,head_dim]")
    if not keys.is_floating_point() or values.dtype != keys.dtype:
        raise ValueError("keys and values must have matching floating dtypes")
    if weight.shape != (keys.shape[-1],) or bias.shape != (geometry.blocks.shape[1],):
        raise ValueError("pool weight or canonical slot bias has the wrong shape")
    if any(t.device != keys.device for t in (values, weight, bias, *geometry.tensors)):
        raise ValueError("pooling tensors and geometry must share a device")
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be finite and positive")
    if keys.numel() > 32_000_000:
        raise ValueError("reference pooling guard: use small shapes")
    dtype = torch.float64 if keys.dtype == torch.float64 else torch.float32
    index = geometry.blocks.long()
    valid = index >= 0
    k, v = keys.to(dtype)[:, :, index.clamp_min(0)], values.to(dtype)[:, :, index.clamp_min(0)]
    logits = (k * weight.to(dtype)).sum(-1) / temperature + bias.to(dtype)
    logits = logits.masked_fill(~valid, -torch.inf)
    fine_valid = valid.any(-1)
    logits = torch.where(fine_valid[None, None, :, None], logits, torch.zeros_like(logits))
    a = logits.softmax(-1) * valid
    fine_k, fine_v = (a[..., None] * k).sum(-2), (a[..., None] * v).sum(-2)
    pooled_k, pooled_v = [], []
    for start in range(0, len(index), geometry.pool_size):
        end = start + geometry.pool_size
        count = fine_valid[start:end].sum()
        pooled_k.append(fine_k[:, :, start:end].sum(2) / count)
        pooled_v.append(fine_v[:, :, start:end].sum(2) / count)
    return torch.stack(pooled_k, 2), torch.stack(pooled_v, 2)
