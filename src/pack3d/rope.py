"""Coordinate-indexed planar rotations; frequencies restart for each axis."""
import math

import torch


def balanced_pairs(head_dim):
    """Allocate all pairs over (z,y,x); head_dim=64 yields (11,11,10)."""
    if type(head_dim) is not int or head_dim <= 0 or head_dim % 2:
        raise ValueError("head_dim must be a positive even integer")
    pairs = head_dim // 2
    return tuple(pairs // 3 + int(axis < pairs % 3) for axis in range(3))


def axial_rope(tensor, coords, *, pairs=None, base=10000.0):
    """Rotate [batch,heads,tokens,head_dim] using coordinates [tokens,3].

    FP16/BF16 rotations compute in FP32; FP64 is retained for mathematical
    checks. No in-place mutation. Values must not be passed through this map.
    Scalar weights can be learned; this identity alone does not make their
    content-dependent pooling rule translation equivariant.
    """
    if tensor.ndim != 4 or not tensor.is_floating_point():
        raise ValueError("tensor must be floating [batch,heads,tokens,head_dim]")
    default = balanced_pairs(tensor.shape[-1])
    pairs = default if pairs is None else tuple(pairs)
    if len(pairs) != 3 or any(type(p) is not int or p < 0 for p in pairs) or sum(pairs) * 2 != tensor.shape[-1]:
        raise ValueError("pairs must allocate every rotary pair across three axes")
    if coords.shape != (tensor.shape[2], 3) or coords.device != tensor.device:
        raise ValueError("coords must be [tokens,3] on the tensor device")
    if coords.is_complex() or (coords.is_floating_point() and not bool(torch.isfinite(coords).all())):
        raise ValueError("coordinates must be real and finite")
    if not math.isfinite(base) or base <= 1:
        raise ValueError("base must be finite and greater than one")
    dtype = torch.float64 if tensor.dtype == torch.float64 else torch.float32
    coordinates = coords.to(dtype)
    pieces, offset = [], 0
    for axis, count in enumerate(pairs):
        if not count:
            continue
        x = tensor[..., offset:offset + 2 * count].to(dtype).reshape(*tensor.shape[:-1], count, 2)
        frequency = base ** (-torch.arange(count, device=tensor.device, dtype=dtype) / count)
        angle = coordinates[:, axis, None] * frequency
        cosine, sine = angle.cos(), angle.sin()
        pieces.append(torch.stack((x[..., 0] * cosine - x[..., 1] * sine,
                                   x[..., 0] * sine + x[..., 1] * cosine), -1).flatten(-2))
        offset += 2 * count
    return torch.cat(pieces, -1).to(tensor.dtype)
