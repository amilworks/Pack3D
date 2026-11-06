"""Staged PACK3D CUDA kernels. See docs/backends.md for the contract.

All reductions accumulate in fp32. Backward recomputes attention probabilities
and pooling weights. No floating-point atomics or N-by-M storage are used.
"""

import torch
import triton
import triton.language as tl


@triton.jit
def _pool(K, V, W, Bias, Blocks, SK, SV, N: tl.constexpr, D: tl.constexpr,
          F: tl.constexpr, M: tl.constexpr, VOLUME: tl.constexpr, POOL: tl.constexpr,
          TEMP: tl.constexpr, PP: tl.constexpr, VV: tl.constexpr):
    m, bg = tl.program_id(0), tl.program_id(1)
    f = m * POOL + tl.arange(0, PP)
    v = tl.arange(0, VV)
    d = tl.arange(0, D)
    idx = tl.load(Blocks + f[:, None] * VOLUME + v[None, :],
                  (f[:, None] < F) & (tl.arange(0, PP)[:, None] < POOL) &
                  (v[None, :] < VOLUME), -1)
    valid = idx >= 0
    k = tl.load(K + bg * N * D + idx[:, :, None] * D + d[None, None, :],
                valid[:, :, None], 0).to(tl.float32)
    val = tl.load(V + bg * N * D + idx[:, :, None] * D + d[None, None, :],
                  valid[:, :, None], 0).to(tl.float32)
    w = tl.load(W + d).to(tl.float32)
    bias = tl.load(Bias + v, v < VOLUME, 0).to(tl.float32)
    logits = tl.sum(k * w[None, None, :], 2) / TEMP + bias[None, :]
    nonempty = tl.sum(valid.to(tl.int32), 1) > 0
    logits = tl.where(valid, logits, -float("inf"))
    mx = tl.where(nonempty, tl.max(logits, 1), 0.)
    a = tl.exp(logits - mx[:, None])
    a = a / tl.maximum(tl.sum(a, 1)[:, None], 1.e-20)
    count = tl.sum(nonempty.to(tl.float32), 0)
    sk = tl.sum(tl.sum(a[:, :, None] * k, 1), 0) / count
    sv = tl.sum(tl.sum(a[:, :, None] * val, 1), 0) / count
    tl.store(SK + (bg * M + m) * D + d, sk)
    tl.store(SV + (bg * M + m) * D + d, sv)


@triton.jit
def _local_fwd(Q, K, V, Nb, O, LSE, N: tl.constexpr, H: tl.constexpr,
               G: tl.constexpr, D: tl.constexpr, W: tl.constexpr,
               WW: tl.constexpr, BQ: tl.constexpr):
    i = tl.program_id(0) * BQ + tl.arange(0, BQ)
    bh = tl.program_id(1)
    bg = bh // H * G + (bh % H) // (H // G)
    d, w = tl.arange(0, D), tl.arange(0, WW)
    idx = tl.load(Nb + i[:, None] * W + w[None, :],
                  (i[:, None] < N) & (w[None, :] < W), -1)
    ok = idx >= 0
    q = tl.load(Q + (bh * N + i[:, None]) * D + d[None, :], i[:, None] < N, 0).to(tl.float32)
    k = tl.load(K + bg * N * D + idx[:, :, None] * D + d[None, None, :], ok[:, :, None], 0).to(tl.float32)
    v = tl.load(V + bg * N * D + idx[:, :, None] * D + d[None, None, :], ok[:, :, None], 0).to(tl.float32)
    s = tl.sum(q[:, None, :] * k, 2) * (D ** -0.5)
    s = tl.where(ok, s, -float("inf"))
    any_valid = tl.sum(ok.to(tl.int32), 1) > 0
    mx = tl.where(any_valid, tl.max(s, 1), 0.)
    p = tl.exp(s - mx[:, None])
    denom = tl.maximum(tl.sum(p, 1), 1.e-20)
    o = tl.sum((p / denom[:, None])[:, :, None] * v, 1)
    tl.store(O + (bh * N + i[:, None]) * D + d[None, :], o, i[:, None] < N)
    tl.store(LSE + bh * N + i, mx + tl.log(denom), i < N)


@triton.jit
def _global_fwd(Q, K, V, OL, Gate, SL, SG, O, LSE, Y,
                N: tl.constexpr, M: tl.constexpr, H: tl.constexpr,
                G: tl.constexpr, D: tl.constexpr, BQ: tl.constexpr, BK: tl.constexpr):
    i = tl.program_id(0) * BQ + tl.arange(0, BQ)
    bh = tl.program_id(1)
    bg = bh // H * G + (bh % H) // (H // G)
    d, j = tl.arange(0, D), tl.arange(0, BK)
    q = tl.load(Q + (bh * N + i[:, None]) * D + d[None, :], i[:, None] < N, 0)
    mx = tl.full((BQ,), -float("inf"), tl.float32)
    denom = tl.full((BQ,), 0., tl.float32)
    acc = tl.full((BQ, D), 0., tl.float32)
    for start in range(tl.cdiv(M, BK)):
        ids = start * BK + j
        k = tl.load(K + (bg * M + ids[None, :]) * D + d[:, None], ids[None, :] < M, 0)
        v = tl.load(V + (bg * M + ids[:, None]) * D + d[None, :], ids[:, None] < M, 0)
        s = tl.dot(q, k, input_precision="ieee") * (D ** -0.5)
        s = tl.where(ids[None, :] < M, s, -float("inf"))
        new_mx = tl.maximum(mx, tl.max(s, 1))
        alpha = tl.exp(mx - new_mx)
        p = tl.exp(s - new_mx[:, None])
        acc = acc * alpha[:, None] + tl.dot(p.to(v.dtype), v, input_precision="ieee")
        denom = denom * alpha + tl.sum(p, 1)
        mx = new_mx
    o = acc / denom[:, None]
    tl.store(O + (bh * N + i[:, None]) * D + d[None, :], o, i[:, None] < N)
    tl.store(LSE + bh * N + i, mx + tl.log(denom), i < N)
    ol = tl.load(OL + (bh * N + i[:, None]) * D + d[None, :], i[:, None] < N, 0).to(tl.float32)
    gate = tl.load(Gate + bh * N + i, i < N, 0).to(tl.float32)
    sl = tl.load(SL + d).to(tl.float32)
    sg = tl.load(SG + d).to(tl.float32)
    tl.store(Y + (bh * N + i[:, None]) * D + d[None, :],
             ol * sl[None, :] + o * gate[:, None] * sg[None, :], i[:, None] < N)


@triton.jit
def _mix_bwd(DY, OL, OG, Gate, SL, SG, DOL, DOG, DL, DG, DGate, DSL, DSG,
             N: tl.constexpr, D: tl.constexpr, TILES: tl.constexpr, BQ: tl.constexpr):
    t, bh = tl.program_id(0), tl.program_id(1)
    i, d = t * BQ + tl.arange(0, BQ), tl.arange(0, D)
    ptr = (bh * N + i[:, None]) * D + d[None, :]
    dy = tl.load(DY + ptr, i[:, None] < N, 0).to(tl.float32)
    ol = tl.load(OL + ptr, i[:, None] < N, 0).to(tl.float32)
    og = tl.load(OG + ptr, i[:, None] < N, 0).to(tl.float32)
    gate = tl.load(Gate + bh * N + i, i < N, 0).to(tl.float32)
    sl, sg = tl.load(SL + d).to(tl.float32), tl.load(SG + d).to(tl.float32)
    dol, dog = dy * sl[None, :], dy * gate[:, None] * sg[None, :]
    # Delta must use the same rounded upstream gradients as the attention VJP.
    dol = dol.to(DOL.dtype.element_ty).to(tl.float32)
    dog = dog.to(DOG.dtype.element_ty).to(tl.float32)
    tl.store(DOL + ptr, dol, i[:, None] < N)
    tl.store(DOG + ptr, dog, i[:, None] < N)
    tl.store(DL + bh * N + i, tl.sum(dol * ol, 1), i < N)
    tl.store(DG + bh * N + i, tl.sum(dog * og, 1), i < N)
    tl.store(DGate + bh * N + i, tl.sum(dy * og * sg[None, :], 1), i < N)
    tl.store(DSL + (bh * TILES + t) * D + d, tl.sum(dy * ol, 0))
    tl.store(DSG + (bh * TILES + t) * D + d, tl.sum(dy * og * gate[:, None], 0))


@triton.jit
def _local_dq(Q, K, V, Nb, DO, LSE, Delta, DQ, N: tl.constexpr,
              H: tl.constexpr, G: tl.constexpr, D: tl.constexpr, W: tl.constexpr,
              WW: tl.constexpr, BQ: tl.constexpr):
    i, w, d = tl.program_id(0) * BQ + tl.arange(0, BQ), tl.arange(0, WW), tl.arange(0, D)
    bh = tl.program_id(1)
    bg = bh // H * G + (bh % H) // (H // G)
    idx = tl.load(Nb + i[:, None] * W + w[None, :], (i[:, None] < N) & (w[None, :] < W), -1)
    ok = idx >= 0
    q = tl.load(Q + (bh * N + i[:, None]) * D + d[None, :], i[:, None] < N, 0).to(tl.float32)
    do = tl.load(DO + (bh * N + i[:, None]) * D + d[None, :], i[:, None] < N, 0).to(tl.float32)
    k = tl.load(K + bg * N * D + idx[:, :, None] * D + d[None, None, :], ok[:, :, None], 0).to(tl.float32)
    v = tl.load(V + bg * N * D + idx[:, :, None] * D + d[None, None, :], ok[:, :, None], 0).to(tl.float32)
    lse = tl.load(LSE + bh * N + i, i < N, 0)
    delta = tl.load(Delta + bh * N + i, i < N, 0)
    s = tl.sum(q[:, None, :] * k, 2) * (D ** -0.5)
    p = tl.where(ok, tl.exp(s - lse[:, None]), 0.)
    dp = tl.sum(do[:, None, :] * v, 2)
    ds = p * (dp - delta[:, None]) * (D ** -0.5)
    dq = tl.sum(ds[:, :, None] * k, 1)
    tl.store(DQ + (bh * N + i[:, None]) * D + d[None, :], dq, i[:, None] < N)


@triton.jit
def _local_dkv(Q, K, V, Reverse, DO, LSE, Delta, DK, DV, N: tl.constexpr,
               H: tl.constexpr, G: tl.constexpr, D: tl.constexpr, W: tl.constexpr,
               WW: tl.constexpr, BK: tl.constexpr):
    j, w, d = tl.program_id(0) * BK + tl.arange(0, BK), tl.arange(0, WW), tl.arange(0, D)
    bg = tl.program_id(1)
    ids = tl.load(Reverse + j[:, None] * W + w[None, :], (j[:, None] < N) & (w[None, :] < W), -1)
    ok = ids >= 0
    k = tl.load(K + (bg * N + j[:, None]) * D + d[None, :], j[:, None] < N, 0).to(tl.float32)
    v = tl.load(V + (bg * N + j[:, None]) * D + d[None, :], j[:, None] < N, 0).to(tl.float32)
    dk, dv = tl.full((BK, D), 0., tl.float32), tl.full((BK, D), 0., tl.float32)
    for head in range(H // G):
        bh = bg // G * H + (bg % G) * (H // G) + head
        q = tl.load(Q + bh * N * D + ids[:, :, None] * D + d[None, None, :], ok[:, :, None], 0).to(tl.float32)
        do = tl.load(DO + bh * N * D + ids[:, :, None] * D + d[None, None, :], ok[:, :, None], 0).to(tl.float32)
        lse = tl.load(LSE + bh * N + ids, ok, 0)
        delta = tl.load(Delta + bh * N + ids, ok, 0)
        s = tl.sum(q * k[:, None, :], 2) * (D ** -0.5)
        p = tl.where(ok, tl.exp(s - lse), 0.)
        ds = p * (tl.sum(do * v[:, None, :], 2) - delta) * (D ** -0.5)
        dk += tl.sum(ds[:, :, None] * q, 1)
        dv += tl.sum(p[:, :, None] * do, 1)
    tl.store(DK + (bg * N + j[:, None]) * D + d[None, :], dk, j[:, None] < N)
    tl.store(DV + (bg * N + j[:, None]) * D + d[None, :], dv, j[:, None] < N)


@triton.jit
def _global_dq(Q, K, V, DO, LSE, Delta, DQ, N: tl.constexpr, M: tl.constexpr,
               H: tl.constexpr, G: tl.constexpr, D: tl.constexpr,
               BQ: tl.constexpr, BK: tl.constexpr):
    i, j, d = tl.program_id(0) * BQ + tl.arange(0, BQ), tl.arange(0, BK), tl.arange(0, D)
    bh = tl.program_id(1)
    bg = bh // H * G + (bh % H) // (H // G)
    q = tl.load(Q + (bh * N + i[:, None]) * D + d[None, :], i[:, None] < N, 0)
    do = tl.load(DO + (bh * N + i[:, None]) * D + d[None, :], i[:, None] < N, 0)
    lse = tl.load(LSE + bh * N + i, i < N, 0)
    delta = tl.load(Delta + bh * N + i, i < N, 0)
    dq = tl.full((BQ, D), 0., tl.float32)
    for start in range(tl.cdiv(M, BK)):
        ids = start * BK + j
        k = tl.load(K + (bg * M + ids[:, None]) * D + d[None, :], ids[:, None] < M, 0)
        v = tl.load(V + (bg * M + ids[None, :]) * D + d[:, None], ids[None, :] < M, 0)
        s = tl.dot(q, tl.trans(k), input_precision="ieee") * (D ** -0.5)
        p = tl.where(ids[None, :] < M, tl.exp(s - lse[:, None]), 0.)
        dp = tl.dot(do, v, input_precision="ieee")
        ds = (p * (dp - delta[:, None]) * (D ** -0.5)).to(k.dtype)
        if M == 1:
            ds = tl.full((BQ, BK), 0, k.dtype)
        dq += tl.dot(ds, k, input_precision="ieee")
    tl.store(DQ + (bh * N + i[:, None]) * D + d[None, :], dq, i[:, None] < N)


@triton.jit
def _global_dkv(Q, K, V, DO, LSE, Delta, DK, DV, N: tl.constexpr, M: tl.constexpr,
                H: tl.constexpr, G: tl.constexpr, D: tl.constexpr, SPLITS: tl.constexpr,
                BQ: tl.constexpr, BK: tl.constexpr):
    j, i, d = tl.program_id(0) * BK + tl.arange(0, BK), tl.arange(0, BQ), tl.arange(0, D)
    bg, split = tl.program_id(1), tl.program_id(2)
    k = tl.load(K + (bg * M + j[:, None]) * D + d[None, :], j[:, None] < M, 0)
    v = tl.load(V + (bg * M + j[:, None]) * D + d[None, :], j[:, None] < M, 0)
    dk, dv = tl.full((BK, D), 0., tl.float32), tl.full((BK, D), 0., tl.float32)
    tiles_per_split: tl.constexpr = triton.cdiv(triton.cdiv(N, BQ), SPLITS)
    for head in range(H // G):
        bh = bg // G * H + (bg % G) * (H // G) + head
        for tile in range(tiles_per_split):
            ids = (split * tiles_per_split + tile) * BQ + i
            q = tl.load(Q + (bh * N + ids[:, None]) * D + d[None, :], ids[:, None] < N, 0)
            do = tl.load(DO + (bh * N + ids[:, None]) * D + d[None, :], ids[:, None] < N, 0)
            lse = tl.load(LSE + bh * N + ids, ids < N, 0)
            delta = tl.load(Delta + bh * N + ids, ids < N, 0)
            s = tl.dot(k, tl.trans(q), input_precision="ieee") * (D ** -0.5)
            p = tl.where((j[:, None] < M) & (ids[None, :] < N), tl.exp(s - lse[None, :]), 0.)
            if M == 1:
                p = ((j[:, None] < M) & (ids[None, :] < N)).to(tl.float32)
            dp = tl.dot(v, tl.trans(do), input_precision="ieee")
            ds = (p * (dp - delta[None, :]) * (D ** -0.5)).to(q.dtype)
            if M == 1:
                ds = tl.full((BK, BQ), 0, q.dtype)
            dk += tl.dot(ds, q, input_precision="ieee")
            dv += tl.dot(p.to(do.dtype), do, input_precision="ieee")
    offset = ((bg * SPLITS + split) * M + j[:, None]) * D + d[None, :]
    tl.store(DK + offset, dk, j[:, None] < M)
    tl.store(DV + offset, dv, j[:, None] < M)


@triton.jit
def _pool_bwd(K, V, W, Bias, Blocks, DSK, DSV, DK, DV, DW, DB,
              N: tl.constexpr, D: tl.constexpr, F: tl.constexpr, M: tl.constexpr,
              VOLUME: tl.constexpr, POOL: tl.constexpr, TEMP: tl.constexpr,
              PP: tl.constexpr, VV: tl.constexpr):
    m, bg = tl.program_id(0), tl.program_id(1)
    f, v, d = m * POOL + tl.arange(0, PP), tl.arange(0, VV), tl.arange(0, D)
    idx = tl.load(Blocks + f[:, None] * VOLUME + v[None, :],
                  (f[:, None] < F) & (tl.arange(0, PP)[:, None] < POOL) & (v[None, :] < VOLUME), -1)
    valid = idx >= 0
    ptr = bg * N * D + idx[:, :, None] * D + d[None, None, :]
    k = tl.load(K + ptr, valid[:, :, None], 0).to(tl.float32)
    val = tl.load(V + ptr, valid[:, :, None], 0).to(tl.float32)
    w = tl.load(W + d).to(tl.float32)
    bias = tl.load(Bias + v, v < VOLUME, 0).to(tl.float32)
    logits = tl.where(valid, tl.sum(k * w[None, None, :], 2) / TEMP + bias[None, :], -float("inf"))
    nonempty = tl.sum(valid.to(tl.int32), 1) > 0
    mx = tl.where(nonempty, tl.max(logits, 1), 0.)
    a = tl.exp(logits - mx[:, None])
    a = a / tl.maximum(tl.sum(a, 1)[:, None], 1.e-20)
    count = tl.sum(nonempty.to(tl.float32), 0)
    dk = tl.load(DSK + (bg * M + m) * D + d).to(tl.float32) / count
    dv = tl.load(DSV + (bg * M + m) * D + d).to(tl.float32) / count
    da = tl.sum(k * dk[None, None, :] + val * dv[None, None, :], 2)
    ds = a * (da - tl.sum(a * da, 1)[:, None])
    dkin = a[:, :, None] * dk[None, None, :] + ds[:, :, None] * w[None, None, :] / TEMP
    dvin = a[:, :, None] * dv[None, None, :]
    tl.store(DK + ptr, dkin, valid[:, :, None])
    tl.store(DV + ptr, dvin, valid[:, :, None])
    tl.store(DW + (bg * M + m) * D + d, tl.sum(tl.sum(ds[:, :, None] * k / TEMP, 1), 0))
    tl.store(DB + (bg * M + m) * VOLUME + v, tl.sum(ds, 0), v < VOLUME)


def _empty(shape, like, *, fp32=False):
    return torch.empty(shape, device=like.device, dtype=torch.float32 if fp32 else like.dtype)


def _local_tile(d, width, *, backward=False):
    # Keep the gathered tile in registers; larger dK/dV tiles spill on H200.
    budget = 16384 if backward else 32768
    return min(8 if backward else 16, max(1, budget // (d * triton.next_power_of_2(width))))


def forward(q, kl, vl, kg, vg, weight, bias, gate, sl, sg, geometry, temperature):
    b, h, n, d = q.shape
    g, (f, volume), m = kl.shape[1], geometry.blocks.shape, geometry.num_summaries
    sk, sv = (_empty((b, g, m, d), q) for _ in range(2))
    ol, og, y = (_empty(q.shape, q) for _ in range(3))
    ll, lg = (_empty((b, h, n), q, fp32=True) for _ in range(2))
    _pool[(m, b * g)](kg, vg, weight, bias, geometry.blocks, sk, sv, n, d, f, m,
                     volume, geometry.pool_size, temperature,
                     triton.next_power_of_2(geometry.pool_size), triton.next_power_of_2(volume))
    w = geometry.neighbors.shape[1]
    tile = _local_tile(d, w)
    _local_fwd[(triton.cdiv(n, tile), b * h)](q, kl, vl, geometry.neighbors, ol, ll,
                                             n, h, g, d, w, triton.next_power_of_2(w), tile)
    _global_fwd[(triton.cdiv(n, 64), b * h)](q, sk, sv, ol, gate, sl, sg, og, lg, y,
                                            n, m, h, g, d, 64, 64)
    return y, (sk, sv, ol, og, ll, lg)


def backward(dy, inputs, saved, geometry, temperature):
    q, kl, vl, kg, vg, weight, bias, gate, sl, sg = inputs
    sk, sv, ol, og, ll, lg = saved
    b, h, n, d = q.shape
    g, (f, volume), m = kl.shape[1], geometry.blocks.shape, geometry.num_summaries
    dol, dog, dql = (_empty(q.shape, q) for _ in range(3))
    dl, dg = (_empty((b, h, n), q, fp32=True) for _ in range(2))
    dgate = torch.empty_like(gate)
    tiles = triton.cdiv(n, 128)
    dslp, dsgp = (_empty((b * h * tiles, d), q, fp32=True) for _ in range(2))
    _mix_bwd[(tiles, b * h)](dy, ol, og, gate, sl, sg, dol, dog, dl, dg, dgate,
                             dslp, dsgp, n, d, tiles, 128)
    dkl, dvl = (torch.empty_like(kl) for _ in range(2))
    w = geometry.neighbors.shape[1]
    tile = _local_tile(d, w, backward=True)
    _local_dq[(triton.cdiv(n, tile), b * h)](q, kl, vl, geometry.neighbors, dol, ll, dl,
                                            dql, n, h, g, d, w, triton.next_power_of_2(w), tile)
    rw = geometry.reverse_neighbors.shape[1]
    tile = _local_tile(d, rw, backward=True)
    _local_dkv[(triton.cdiv(n, tile), b * g)](q, kl, vl, geometry.reverse_neighbors, dol,
                                          ll, dl, dkl, dvl, n, h, g, d, rw,
                                          triton.next_power_of_2(rw), tile)
    # Local VJPs have finished reading dOL. Reuse that buffer for global dQ,
    # then accumulate in-place into the owned local dQ buffer, never an input.
    _global_dq[(triton.cdiv(n, 64), b * h)](q, sk, sv, dog, lg, dg, dol, n, m, h, g, d, 64, 64)
    dql.add_(dol)
    del dol
    splits = min(32, max(1, triton.cdiv(n, 1024)))
    dkpart, dvpart = (_empty((b, g, splits, m, d), q, fp32=True) for _ in range(2))
    _global_dkv[(triton.cdiv(m, 64), b * g, splits)](q, sk, sv, dog, lg, dg, dkpart,
                                                    dvpart, n, m, h, g, d, splits, 64, 64)
    del dog
    dsk, dsv = dkpart.sum(2), dvpart.sum(2)
    del dkpart, dvpart
    dkg, dvg = (torch.empty_like(kg) for _ in range(2))
    dwp = _empty((b * g * m, d), q, fp32=True)
    dbp = _empty((b * g * m, volume), q, fp32=True)
    _pool_bwd[(m, b * g)](kg, vg, weight, bias, geometry.blocks, dsk, dsv, dkg, dvg,
                         dwp, dbp, n, d, f, m, volume, geometry.pool_size, temperature,
                         triton.next_power_of_2(geometry.pool_size), triton.next_power_of_2(volume))
    return (dql, dkl, dvl, dkg, dvg, dwp.sum(0).to(weight.dtype),
            dbp.sum(0).to(bias.dtype), dgate, dslp.sum(0).to(sl.dtype), dsgp.sum(0).to(sg.dtype))
