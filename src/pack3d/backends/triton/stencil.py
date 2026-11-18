"""Local backward for the radius-one voxel stencil on a complete 3D grid."""
import math

import triton
import triton.language as tl


@triton.jit
def _voxel_rows(zyx, z, y, x, Z: tl.constexpr, Y: tl.constexpr, X: tl.constexpr,
                Map, MAPPED: tl.constexpr):
    zz, yy, xx = zyx[0] + z, zyx[1] + y, zyx[2] + x
    valid = (zz >= 0) & (zz < Z) & (yy >= 0) & (yy < Y) & (xx >= 0) & (xx < X)
    index = (zz * Y + yy) * X + xx
    if MAPPED:
        index = tl.load(Map + index, valid, 0)
    return index, valid


@triton.jit
def _weighted_sum(weight, x):
    # FP16 score gradients can exceed 65504 even when the result is finite.
    # Scale each row before splitting its FP32 coefficients for tensor cores.
    if x.dtype == tl.float16:
        scale = tl.max(tl.abs(weight), 1)
        scale = tl.where(scale > 0., scale, 1.)
        weight = weight / scale[:, None]
    hi = weight.to(x.dtype)
    lo = (weight - hi.to(tl.float32)).to(x.dtype)
    out = tl.dot(hi, x) + tl.dot(lo, x)
    if x.dtype == tl.float16:
        out = out * scale[:, None]
    return out


@triton.jit
def _stencil_backward(Q, K, V, DO, LSE, Delta, Map, DQ, DK, DV,
                      Z: tl.constexpr, Y: tl.constexpr, X: tl.constexpr,
                      H: tl.constexpr, G: tl.constexpr, D: tl.constexpr,
                      TZ: tl.constexpr, TY: tl.constexpr, TX: tl.constexpr,
                      HALO_TILE: tl.constexpr, QUERY: tl.constexpr, MAPPED: tl.constexpr):
    # A program owns a brick of query rows or KV rows. All its centers share
    # one halo, and the spatial mask selects the original 27 edges per voxel.
    N: tl.constexpr = Z * Y * X
    CENTER: tl.constexpr = TZ * TY * TX
    HALO: tl.constexpr = (TZ + 2) * (TY + 2) * (TX + 2)
    ny: tl.constexpr = triton.cdiv(Y, TY)
    nx: tl.constexpr = triton.cdiv(X, TX)
    tile, head = tl.program_id(0), tl.program_id(1)
    origin = (tile // (ny * nx) * TZ, tile // nx % ny * TY, tile % nx * TX)
    row, d = tl.arange(0, CENTER), tl.arange(0, D)
    cz, cy, cx = row // (TY * TX), row // TX % TY, row % TX
    center, valid = _voxel_rows(origin, cz, cy, cx, Z, Y, X, Map, MAPPED)
    cptr = center[:, None] * D + d[None, :]
    if QUERY:
        kv_head = head // H * G + (head % H) // (H // G)
        a = tl.load(Q + head * N * D + cptr, valid[:, None], 0)
        b = tl.load(DO + head * N * D + cptr, valid[:, None], 0)
        lse = tl.load(LSE + head * N + center, valid, 0)
        delta = tl.load(Delta + head * N + center, valid, 0)
    else:
        kv_head = head
        a = tl.load(K + kv_head * N * D + cptr, valid[:, None], 0)
        b = tl.load(V + kv_head * N * D + cptr, valid[:, None], 0)
    grad = tl.full((CENTER, D), 0., tl.float32)
    if not QUERY:
        grad_v = tl.full((CENTER, D), 0., tl.float32)
    for start in range(triton.cdiv(HALO, HALO_TILE)):
        s = start * HALO_TILE + tl.arange(0, HALO_TILE)
        hz = s // ((TY + 2) * (TX + 2)) - 1
        hy = s // (TX + 2) % (TY + 2) - 1
        hx = s % (TX + 2) - 1
        neighbor, in_grid = _voxel_rows(origin, hz, hy, hx, Z, Y, X, Map, MAPPED)
        in_grid = in_grid & (s < HALO)
        edge = (valid[:, None] & in_grid[None, :] &
                (tl.abs(cz[:, None] - hz[None, :]) <= 1) &
                (tl.abs(cy[:, None] - hy[None, :]) <= 1) &
                (tl.abs(cx[:, None] - hx[None, :]) <= 1))
        ptr = neighbor[:, None] * D + d[None, :]
        if QUERY:
            k = tl.load(K + kv_head * N * D + ptr, in_grid[:, None], 0)
            v = tl.load(V + kv_head * N * D + ptr, in_grid[:, None], 0)
            score = tl.dot(a, tl.trans(k)) * (D ** -0.5)
            p = tl.where(edge, tl.exp(score - lse[:, None]), 0.)
            dp = tl.dot(b, tl.trans(v))
            ds = tl.where(edge, p * (dp - delta[:, None]) * (D ** -0.5), 0.)
            grad += _weighted_sum(ds, k)
        else:
            for group_head in range(H // G):
                q_head = head // G * H + (head % G) * (H // G) + group_head
                q = tl.load(Q + q_head * N * D + ptr, in_grid[:, None], 0)
                do = tl.load(DO + q_head * N * D + ptr, in_grid[:, None], 0)
                lse = tl.load(LSE + q_head * N + neighbor, in_grid, 0)
                delta = tl.load(Delta + q_head * N + neighbor, in_grid, 0)
                score = tl.dot(a, tl.trans(q)) * (D ** -0.5)
                p = tl.where(edge, tl.exp(score - lse[None, :]), 0.)
                dp = tl.dot(b, tl.trans(do))
                ds = tl.where(edge, p * (dp - delta[None, :]) * (D ** -0.5), 0.)
                grad += _weighted_sum(ds, q)
                grad_v += _weighted_sum(p, do)
    if QUERY:
        tl.store(DQ + head * N * D + cptr, grad, valid[:, None])
    else:
        tl.store(DK + head * N * D + cptr, grad, valid[:, None])
        tl.store(DV + head * N * D + cptr, grad_v, valid[:, None])


def local_backward(q, k, v, do, lse, delta, geometry, dq, dk, dv):
    batch, heads, _, dim = q.shape
    groups = k.shape[1]
    shape, mapping = geometry._radius_one_grid, geometry._raster_to_packed
    brick = (2, 2, 4)
    tiles = math.prod(triton.cdiv(size, width) for size, width in zip(shape, brick))
    for query, count in ((True, heads), (False, groups)):
        _stencil_backward[(tiles, batch * count)](
            q, k, v, do, lse, delta, mapping, dq, dk, dv, *shape, heads, groups, dim,
            *brick, 32, query, mapping is not None, num_warps=4)
