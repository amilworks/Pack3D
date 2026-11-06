from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from typing import Callable

import torch
from torch import Tensor


@dataclass(frozen=True)
class LocalBackendReport:
    backend_requested: str
    backend_actual: str
    fallback_reason: str


def triton_local_status() -> dict[str, object]:
    return {
        "torch_cuda_available": torch.cuda.is_available(),
        "triton_importable": importlib.util.find_spec("triton") is not None,
    }


try:  # pragma: no cover - importability depends on optional Triton install.
    import triton
    import triton.language as tl
except Exception:  # pragma: no cover
    triton = None
    tl = None


if triton is not None:

    @triton.jit
    def _local_attention_forward_kernel(
        Q,
        K,
        V,
        NEIGHBOR,
        NEIGHBOR_MASK,
        OUT,
        stride_q_b: tl.constexpr,
        stride_q_h: tl.constexpr,
        stride_q_n: tl.constexpr,
        stride_k_b: tl.constexpr,
        stride_k_g: tl.constexpr,
        stride_k_n: tl.constexpr,
        stride_o_b: tl.constexpr,
        stride_o_h: tl.constexpr,
        stride_o_n: tl.constexpr,
        HEADS: tl.constexpr,
        KV_HEADS: tl.constexpr,
        QUERY_GROUPS: tl.constexpr,
        NUM_TOKENS: tl.constexpr,
        DIM: tl.constexpr,
        LOCAL_W: tl.constexpr,
        BLOCK_N: tl.constexpr,
        BLOCK_D: tl.constexpr,
        BLOCK_W: tl.constexpr,
    ):
        pid_n = tl.program_id(0)
        pid_bh = tl.program_id(1)
        off_b = pid_bh // HEADS
        off_h = pid_bh - off_b * HEADS
        off_g = off_h // QUERY_GROUPS

        offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
        offs_d = tl.arange(0, BLOCK_D)
        n_valid = offs_n < NUM_TOKENS
        d_valid = offs_d < DIM
        scale = 1.0 / tl.sqrt(DIM + 0.0)

        q = tl.load(
            Q
            + off_b * stride_q_b
            + off_h * stride_q_h
            + offs_n[:, None] * stride_q_n
            + offs_d[None, :],
            mask=n_valid[:, None] & d_valid[None, :],
            other=0.0,
        ).to(tl.float32)

        m = tl.full((BLOCK_N,), -float("inf"), tl.float32)
        for w in tl.static_range(0, BLOCK_W):
            if w < LOCAL_W:
                neigh = tl.load(NEIGHBOR + offs_n * LOCAL_W + w, mask=n_valid, other=0)
                neigh_ok = tl.load(NEIGHBOR_MASK + offs_n * LOCAL_W + w, mask=n_valid, other=0) > 0
                k = tl.load(
                    K
                    + off_b * stride_k_b
                    + off_g * stride_k_g
                    + neigh[:, None] * stride_k_n
                    + offs_d[None, :],
                    mask=n_valid[:, None] & neigh_ok[:, None] & d_valid[None, :],
                    other=0.0,
                ).to(tl.float32)
                sim = tl.sum(q * k, axis=1) * scale
                sim = tl.where(n_valid & neigh_ok, sim, -float("inf"))
                m = tl.maximum(m, sim)

        denom = tl.zeros((BLOCK_N,), tl.float32)
        acc = tl.zeros((BLOCK_N, BLOCK_D), tl.float32)
        for w in tl.static_range(0, BLOCK_W):
            if w < LOCAL_W:
                neigh = tl.load(NEIGHBOR + offs_n * LOCAL_W + w, mask=n_valid, other=0)
                neigh_ok = tl.load(NEIGHBOR_MASK + offs_n * LOCAL_W + w, mask=n_valid, other=0) > 0
                k = tl.load(
                    K
                    + off_b * stride_k_b
                    + off_g * stride_k_g
                    + neigh[:, None] * stride_k_n
                    + offs_d[None, :],
                    mask=n_valid[:, None] & neigh_ok[:, None] & d_valid[None, :],
                    other=0.0,
                ).to(tl.float32)
                v = tl.load(
                    V
                    + off_b * stride_k_b
                    + off_g * stride_k_g
                    + neigh[:, None] * stride_k_n
                    + offs_d[None, :],
                    mask=n_valid[:, None] & neigh_ok[:, None] & d_valid[None, :],
                    other=0.0,
                ).to(tl.float32)
                sim = tl.sum(q * k, axis=1) * scale
                sim = tl.where(n_valid & neigh_ok, sim, -float("inf"))
                p = tl.exp(sim - m)
                p = tl.where(n_valid & neigh_ok, p, 0.0)
                denom += p
                acc += p[:, None] * v

        out = acc / tl.maximum(denom[:, None], 1.0e-20)
        out = tl.where(denom[:, None] > 0.0, out, 0.0)
        tl.store(
            OUT
            + off_b * stride_o_b
            + off_h * stride_o_h
            + offs_n[:, None] * stride_o_n
            + offs_d[None, :],
            out,
            mask=n_valid[:, None] & d_valid[None, :],
        )


    @triton.jit
    def _local_attention_backward_kernel(
        Q,
        K,
        V,
        NEIGHBOR,
        NEIGHBOR_MASK,
        OUT,
        DOUT,
        DQ,
        DK,
        DV,
        stride_q_b: tl.constexpr,
        stride_q_h: tl.constexpr,
        stride_q_n: tl.constexpr,
        stride_k_b: tl.constexpr,
        stride_k_g: tl.constexpr,
        stride_k_n: tl.constexpr,
        stride_o_b: tl.constexpr,
        stride_o_h: tl.constexpr,
        stride_o_n: tl.constexpr,
        HEADS: tl.constexpr,
        KV_HEADS: tl.constexpr,
        QUERY_GROUPS: tl.constexpr,
        NUM_TOKENS: tl.constexpr,
        DIM: tl.constexpr,
        LOCAL_W: tl.constexpr,
        BLOCK_N: tl.constexpr,
        BLOCK_D: tl.constexpr,
        BLOCK_W: tl.constexpr,
    ):
        pid_n = tl.program_id(0)
        pid_bh = tl.program_id(1)
        off_b = pid_bh // HEADS
        off_h = pid_bh - off_b * HEADS
        off_g = off_h // QUERY_GROUPS

        offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
        offs_d = tl.arange(0, BLOCK_D)
        n_valid = offs_n < NUM_TOKENS
        d_valid = offs_d < DIM
        scale = 1.0 / tl.sqrt(DIM + 0.0)

        q = tl.load(
            Q
            + off_b * stride_q_b
            + off_h * stride_q_h
            + offs_n[:, None] * stride_q_n
            + offs_d[None, :],
            mask=n_valid[:, None] & d_valid[None, :],
            other=0.0,
        ).to(tl.float32)
        dout = tl.load(
            DOUT
            + off_b * stride_o_b
            + off_h * stride_o_h
            + offs_n[:, None] * stride_o_n
            + offs_d[None, :],
            mask=n_valid[:, None] & d_valid[None, :],
            other=0.0,
        ).to(tl.float32)
        out = tl.load(
            OUT
            + off_b * stride_o_b
            + off_h * stride_o_h
            + offs_n[:, None] * stride_o_n
            + offs_d[None, :],
            mask=n_valid[:, None] & d_valid[None, :],
            other=0.0,
        ).to(tl.float32)

        m = tl.full((BLOCK_N,), -float("inf"), tl.float32)
        for w in tl.static_range(0, BLOCK_W):
            if w < LOCAL_W:
                neigh = tl.load(NEIGHBOR + offs_n * LOCAL_W + w, mask=n_valid, other=0)
                neigh_ok = tl.load(NEIGHBOR_MASK + offs_n * LOCAL_W + w, mask=n_valid, other=0) > 0
                k = tl.load(
                    K
                    + off_b * stride_k_b
                    + off_g * stride_k_g
                    + neigh[:, None] * stride_k_n
                    + offs_d[None, :],
                    mask=n_valid[:, None] & neigh_ok[:, None] & d_valid[None, :],
                    other=0.0,
                ).to(tl.float32)
                sim = tl.sum(q * k, axis=1) * scale
                sim = tl.where(n_valid & neigh_ok, sim, -float("inf"))
                m = tl.maximum(m, sim)

        denom = tl.zeros((BLOCK_N,), tl.float32)
        for w in tl.static_range(0, BLOCK_W):
            if w < LOCAL_W:
                neigh = tl.load(NEIGHBOR + offs_n * LOCAL_W + w, mask=n_valid, other=0)
                neigh_ok = tl.load(NEIGHBOR_MASK + offs_n * LOCAL_W + w, mask=n_valid, other=0) > 0
                k = tl.load(
                    K
                    + off_b * stride_k_b
                    + off_g * stride_k_g
                    + neigh[:, None] * stride_k_n
                    + offs_d[None, :],
                    mask=n_valid[:, None] & neigh_ok[:, None] & d_valid[None, :],
                    other=0.0,
                ).to(tl.float32)
                sim = tl.sum(q * k, axis=1) * scale
                sim = tl.where(n_valid & neigh_ok, sim, -float("inf"))
                p = tl.exp(sim - m)
                p = tl.where(n_valid & neigh_ok, p, 0.0)
                denom += p

        delta = tl.sum(dout * out, axis=1)
        dq = tl.zeros((BLOCK_N, BLOCK_D), tl.float32)
        for w in tl.static_range(0, BLOCK_W):
            if w < LOCAL_W:
                neigh = tl.load(NEIGHBOR + offs_n * LOCAL_W + w, mask=n_valid, other=0)
                neigh_ok = tl.load(NEIGHBOR_MASK + offs_n * LOCAL_W + w, mask=n_valid, other=0) > 0
                valid = n_valid & neigh_ok & (denom > 0.0)
                k = tl.load(
                    K
                    + off_b * stride_k_b
                    + off_g * stride_k_g
                    + neigh[:, None] * stride_k_n
                    + offs_d[None, :],
                    mask=valid[:, None] & d_valid[None, :],
                    other=0.0,
                ).to(tl.float32)
                v = tl.load(
                    V
                    + off_b * stride_k_b
                    + off_g * stride_k_g
                    + neigh[:, None] * stride_k_n
                    + offs_d[None, :],
                    mask=valid[:, None] & d_valid[None, :],
                    other=0.0,
                ).to(tl.float32)
                sim = tl.sum(q * k, axis=1) * scale
                sim = tl.where(valid, sim, -float("inf"))
                p = tl.exp(sim - m) / tl.maximum(denom, 1.0e-20)
                p = tl.where(valid, p, 0.0)

                dp = tl.sum(dout * v, axis=1)
                ds = p * (dp - delta)
                dq += (ds * scale)[:, None] * k
                dk = (ds * scale)[:, None] * q
                dv = p[:, None] * dout
                kv_ptrs = (
                    off_b * stride_k_b
                    + off_g * stride_k_g
                    + neigh[:, None] * stride_k_n
                    + offs_d[None, :]
                )
                tl.atomic_add(DK + kv_ptrs, dk, sem="relaxed", mask=valid[:, None] & d_valid[None, :])
                tl.atomic_add(DV + kv_ptrs, dv, sem="relaxed", mask=valid[:, None] & d_valid[None, :])

        tl.store(
            DQ
            + off_b * stride_q_b
            + off_h * stride_q_h
            + offs_n[:, None] * stride_q_n
            + offs_d[None, :],
            dq,
            mask=n_valid[:, None] & d_valid[None, :],
        )


def _next_power_of_2(x: int) -> int:
    return 1 << (int(x) - 1).bit_length()


class _TritonLocalAttention(torch.autograd.Function):
    @staticmethod
    def forward(
        ctx,
        q: Tensor,
        k: Tensor,
        v: Tensor,
        neighbor_indices: Tensor,
        neighbor_mask: Tensor,
        block_n: int,
    ) -> Tensor:
        assert triton is not None
        q = q.contiguous()
        k = k.contiguous()
        v = v.contiguous()
        neighbor_indices = neighbor_indices.contiguous()
        neighbor_mask = neighbor_mask.contiguous()
        batch, heads, num_tokens, dim = q.shape
        kv_heads = k.shape[1]
        query_groups = heads // kv_heads
        local_w = neighbor_indices.shape[1]
        block_d = _next_power_of_2(dim)
        block_w = _next_power_of_2(local_w)
        out = torch.empty_like(q)
        grid = (triton.cdiv(num_tokens, block_n), batch * heads)
        _local_attention_forward_kernel[grid](
            q,
            k,
            v,
            neighbor_indices,
            neighbor_mask,
            out,
            q.stride(0),
            q.stride(1),
            q.stride(2),
            k.stride(0),
            k.stride(1),
            k.stride(2),
            out.stride(0),
            out.stride(1),
            out.stride(2),
            HEADS=heads,
            KV_HEADS=kv_heads,
            QUERY_GROUPS=query_groups,
            NUM_TOKENS=num_tokens,
            DIM=dim,
            LOCAL_W=local_w,
            BLOCK_N=int(block_n),
            BLOCK_D=block_d,
            BLOCK_W=block_w,
            num_warps=4,
            num_stages=3,
        )
        ctx.save_for_backward(q, k, v, neighbor_indices, neighbor_mask, out)
        ctx.block_n = int(block_n)
        return out

    @staticmethod
    def backward(ctx, dout: Tensor):
        assert triton is not None
        q, k, v, neighbor_indices, neighbor_mask, out = ctx.saved_tensors
        dout = dout.contiguous()
        batch, heads, num_tokens, dim = q.shape
        kv_heads = k.shape[1]
        query_groups = heads // kv_heads
        local_w = neighbor_indices.shape[1]
        block_n = int(ctx.block_n)
        block_d = _next_power_of_2(dim)
        block_w = _next_power_of_2(local_w)
        dq = torch.empty_like(q)
        dk = torch.zeros_like(k)
        dv = torch.zeros_like(v)
        grid = (triton.cdiv(num_tokens, block_n), batch * heads)
        _local_attention_backward_kernel[grid](
            q,
            k,
            v,
            neighbor_indices,
            neighbor_mask,
            out,
            dout,
            dq,
            dk,
            dv,
            q.stride(0),
            q.stride(1),
            q.stride(2),
            k.stride(0),
            k.stride(1),
            k.stride(2),
            out.stride(0),
            out.stride(1),
            out.stride(2),
            HEADS=heads,
            KV_HEADS=kv_heads,
            QUERY_GROUPS=query_groups,
            NUM_TOKENS=num_tokens,
            DIM=dim,
            LOCAL_W=local_w,
            BLOCK_N=block_n,
            BLOCK_D=block_d,
            BLOCK_W=block_w,
            num_warps=4,
            num_stages=3,
        )
        return dq, dk, dv, None, None, None


def local_attention(
    q: Tensor,
    k: Tensor,
    v: Tensor,
    neighbor_indices: Tensor,
    neighbor_mask: Tensor,
    *,
    use_triton_kernel: bool,
    torch_fallback: Callable[[Tensor, Tensor, Tensor], Tensor],
    block_n: int = 16,
    validate_output: bool = False,
) -> tuple[Tensor, LocalBackendReport]:
    requested = "triton_local" if use_triton_kernel else "torch_fallback"
    if not use_triton_kernel:
        return torch_fallback(q, k, v), LocalBackendReport(requested, "torch_fallback", "")

    reasons: list[str] = []
    if triton is None or tl is None:
        reasons.append("triton package is not importable")
    if not torch.cuda.is_available():
        reasons.append("CUDA is unavailable")
    if not q.is_cuda:
        reasons.append("query tensor is not on CUDA")
    if q.shape[1] % k.shape[1] != 0:
        reasons.append("query heads must be divisible by KV heads")
    if q.shape[-1] > 128:
        reasons.append("head dimension >128 is not supported by Triton local attention")
    if q.dtype not in (torch.float16, torch.bfloat16, torch.float32):
        reasons.append("Triton local attention expects fp16, bf16, or fp32 tensors")
    if neighbor_indices.shape != neighbor_mask.shape:
        reasons.append("neighbor indices and mask must have the same shape")
    if neighbor_indices.shape[0] != q.shape[2]:
        reasons.append("neighbor table must have one row per token")
    if neighbor_indices.shape[1] <= 0:
        reasons.append("local window must be non-empty")

    if reasons:
        return torch_fallback(q, k, v), LocalBackendReport(requested, "torch_fallback", "; ".join(reasons))

    try:
        assert triton is not None
        out = _TritonLocalAttention.apply(q, k, v, neighbor_indices.to(q.device), neighbor_mask.to(q.device), int(block_n))
        if validate_output and not torch.isfinite(out).all():
            return torch_fallback(q, k, v), LocalBackendReport(requested, "torch_fallback", "Triton local attention produced non-finite output")
        return out, LocalBackendReport(requested, "triton_local", "")
    except Exception as exc:  # pragma: no cover - depends on CUDA/Triton execution.
        return torch_fallback(q, k, v), LocalBackendReport(requested, "torch_fallback", f"Triton local attention failed: {exc}")
