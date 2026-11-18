"""Rotate projected queries and keys directly into head-major attention buffers."""
from functools import lru_cache

import torch
from torch.autograd.function import once_differentiable
import triton
import triton.language as tl


@triton.jit
def _rotate(X, Coords, Phases, Y, N: tl.constexpr, H: tl.constexpr, D: tl.constexpr,
            SB: tl.constexpr, SH: tl.constexpr, SN: tl.constexpr, SD: tl.constexpr,
            SCN: tl.constexpr, SCA: tl.constexpr, Z_PAIRS: tl.constexpr, Y_PAIRS: tl.constexpr,
            Z_ENTRIES: tl.constexpr, Y_ENTRIES: tl.constexpr, HAS_TABLE: tl.constexpr,
            PACKED: tl.constexpr, INVERSE: tl.constexpr, ROWS: tl.constexpr):
    i = tl.program_id(0) * ROWS + tl.arange(0, ROWS)
    h, b = tl.program_id(1), tl.program_id(2)
    pair = tl.arange(0, D // 2)
    if PACKED:
        pos = i[:, None]
    else:
        axis = tl.where(pair < Z_PAIRS, 0, tl.where(pair < Z_PAIRS + Y_PAIRS, 1, 2))
        pos = tl.load(Coords + i[:, None].to(tl.int64) * SCN + axis[None, :] * SCA,
                      i[:, None] < N, 0)
    if HAS_TABLE:
        is_z, is_y = pair < Z_PAIRS, pair < Z_PAIRS + Y_PAIRS
        count = tl.where(is_z, Z_PAIRS, tl.where(is_y, Y_PAIRS, D // 2 - Z_PAIRS - Y_PAIRS))
        # Flatten [coordinate, pair within axis] into the concatenated tables.
        base = tl.where(is_z, 0, tl.where(is_y, Z_ENTRIES, Z_ENTRIES + Y_ENTRIES))
        first_pair = tl.where(is_z, 0, tl.where(is_y, Z_PAIRS, Z_PAIRS + Y_PAIRS))
        idx = pos.to(tl.int32) * count[None, :] + (base + pair - first_pair)[None, :]
        c = tl.load(Phases + idx * 2)
        s = tl.load(Phases + idx * 2 + 1)
    else:
        angle = pos.to(tl.float32) * tl.load(Phases + pair)[None, :]
        c, s = tl.cos(angle), tl.sin(angle)
    if INVERSE:
        s = -s
    src = X + b.to(tl.int64) * SB + h.to(tl.int64) * SH + i[:, None].to(tl.int64) * SN
    channel = tl.arange(0, D)
    x = tl.load(src + channel[None, :] * SD, i[:, None] < N, 0).to(tl.float32)
    even, odd = tl.split(tl.reshape(x, (ROWS, D // 2, 2)))
    rotated = tl.join(even * c - odd * s, even * s + odd * c)
    dst = Y + ((b.to(tl.int64) * H + h) * N + i[:, None]) * D + channel[None, :]
    tl.store(dst, tl.reshape(rotated, (ROWS, D)), i[:, None] < N)


def _run(x, coords, phases, pairs, table_sizes, packed, *, inverse):
    b, h, n, d = x.shape
    out = torch.empty(x.shape, dtype=x.dtype, device=x.device)
    rows = 32
    _rotate[(triton.cdiv(n, rows), h, b)](
        x, coords, phases, out, n, h, d, *x.stride(), *coords.stride(), pairs[0], pairs[1],
        table_sizes[0], table_sizes[1], bool(table_sizes[0]), packed, inverse, rows, enable_fp_fusion=False)
    return out


class _Rotary(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, coords, phases, pairs, table_sizes, packed):
        ctx.save_for_backward(coords, phases)
        ctx.pairs, ctx.table_sizes, ctx.packed = pairs, table_sizes, packed
        return _run(x, coords, phases, pairs, table_sizes, packed, inverse=False)

    @staticmethod
    @once_differentiable
    def backward(ctx, grad):
        coords, phases = ctx.saved_tensors
        dx = _run(grad, coords, phases, ctx.pairs, ctx.table_sizes, ctx.packed, inverse=True)
        return dx, None, None, None, None, None


@torch.inference_mode(False)
def _build_phases(device, pairs, table_shape):
    # A table first built during inference must also be saveable for backward.
    parts = []
    for axis, count in enumerate(pairs):
        if count:
            part = 10000.0 ** (-torch.arange(count, device=device, dtype=torch.float32) / count)
            if table_shape:
                positions = torch.arange(table_shape[axis], device=device, dtype=torch.float32)
                part = (positions[:, None] * part).flatten()
            parts.append(part)
    phase = parts[0] if len(parts) == 1 else torch.cat(parts)
    return torch.stack((phase.cos(), phase.sin()), -1) if table_shape else phase


@lru_cache(maxsize=16)
def _cached_phases(stream, pairs, table_shape):
    # Including the CUDA stream covers device identity and orders asynchronous fills and reads.
    return _build_phases(stream.device, pairs, table_shape)


def rotate_projections(q, kl, kg, coords, pairs, grid_shape, *, packed):
    pairs = tuple(pairs)
    sizes = tuple(size * p for size, p in zip(grid_shape, pairs))
    table_shape = tuple(grid_shape) if not packed and sum(sizes) <= 8192 else ()
    if not table_shape:
        sizes = (0, 0, 0)
    with torch.cuda.device(q.device):
        if torch.cuda.is_current_stream_capturing():
            # Captured allocations and writes belong to that graph's replay.
            phases = _build_phases(q.device, pairs, table_shape)
        else:
            phases = _cached_phases(torch.cuda.current_stream(), pairs, table_shape)
    return tuple(_Rotary.apply(x, coords, phases, pairs, sizes, packed) for x in (q, kl, kg))
