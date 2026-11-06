from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import math

import torch
from torch import Tensor


@dataclass(frozen=True)
class RouteBackendReport:
    backend_requested: str
    backend_actual: str
    fallback_reason: str


def triton_route_status() -> dict[str, object]:
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
    def _insert_top2(
        cand_val,
        cand_idx,
        best1,
        idx1,
        best2,
        idx2,
    ):
        better1 = cand_val > best1
        better2 = (cand_val > best2) & (~better1)
        next_best2 = tl.where(better1, best1, tl.where(better2, cand_val, best2))
        next_idx2 = tl.where(better1, idx1, tl.where(better2, cand_idx, idx2))
        next_best1 = tl.where(better1, cand_val, best1)
        next_idx1 = tl.where(better1, cand_idx, idx1)
        return next_best1, next_idx1, next_best2, next_idx2


    @triton.jit
    def _route_lse_top2_kernel(
        Q,
        SUMMARY_K,
        RESIDUAL,
        COORDS,
        CENTERS,
        LOG_METRIC,
        BLOCK_ID,
        VALID_Q,
        OUT_IDX,
        OUT_MASK,
        OUT_SCORE,
        stride_q_b: tl.constexpr,
        stride_q_g: tl.constexpr,
        stride_q_h: tl.constexpr,
        stride_q_n: tl.constexpr,
        stride_s_b: tl.constexpr,
        stride_s_g: tl.constexpr,
        stride_s_c: tl.constexpr,
        stride_s_r: tl.constexpr,
        stride_res_b: tl.constexpr,
        stride_res_g: tl.constexpr,
        stride_out_b: tl.constexpr,
        stride_out_g: tl.constexpr,
        stride_out_n: tl.constexpr,
        BATCH: tl.constexpr,
        KV_HEADS: tl.constexpr,
        QUERY_GROUPS: tl.constexpr,
        NUM_TOKENS: tl.constexpr,
        NUM_BLOCKS: tl.constexpr,
        NUM_ATOMS: tl.constexpr,
        DIM: tl.constexpr,
        NDIM: tl.constexpr,
        NUM_SELECTED: tl.constexpr,
        BLOCK_Q: tl.constexpr,
        BLOCK_C: tl.constexpr,
        BLOCK_D: tl.constexpr,
        RESIDUAL_WEIGHT: tl.constexpr,
        CENTER_DISTANCE_WEIGHT: tl.constexpr,
        EXCLUDE_OWN: tl.constexpr,
        ROUTE_QUANTIZE: tl.constexpr,
    ):
        pid_q = tl.program_id(0)
        pid_bg = tl.program_id(1)
        off_b = pid_bg // KV_HEADS
        off_g = pid_bg - off_b * KV_HEADS

        offs_q = pid_q * BLOCK_Q + tl.arange(0, BLOCK_Q)
        offs_d = tl.arange(0, BLOCK_D)
        q_valid = (offs_q < NUM_TOKENS) & (tl.load(VALID_Q + offs_q, mask=offs_q < NUM_TOKENS, other=0) > 0)
        own_block = tl.load(BLOCK_ID + offs_q, mask=offs_q < NUM_TOKENS, other=-1)

        best1 = tl.full((BLOCK_Q,), -float("inf"), tl.float32)
        best2 = tl.full((BLOCK_Q,), -float("inf"), tl.float32)
        idx1 = tl.full((BLOCK_Q,), -1, tl.int64)
        idx2 = tl.full((BLOCK_Q,), -1, tl.int64)

        scale = 1.0 / tl.sqrt(DIM + 0.0)

        for c0 in tl.range(0, NUM_BLOCKS, BLOCK_C, num_stages=2):
            offs_c = c0 + tl.arange(0, BLOCK_C)
            c_valid = offs_c < NUM_BLOCKS
            rel = tl.zeros((BLOCK_Q, BLOCK_C), dtype=tl.float32)

            for qh in tl.static_range(0, QUERY_GROUPS):
                lse_atoms = tl.full((BLOCK_Q, BLOCK_C), -float("inf"), dtype=tl.float32)
                for atom in tl.static_range(0, NUM_ATOMS):
                    q_ptrs = (
                        Q
                        + off_b * stride_q_b
                        + off_g * stride_q_g
                        + qh * stride_q_h
                        + offs_q[:, None] * stride_q_n
                        + offs_d[None, :]
                    )
                    s_ptrs = (
                        SUMMARY_K
                        + off_b * stride_s_b
                        + off_g * stride_s_g
                        + offs_c[:, None] * stride_s_c
                        + atom * stride_s_r
                        + offs_d[None, :]
                    )
                    q = tl.load(q_ptrs, mask=(q_valid[:, None]) & (offs_d[None, :] < DIM), other=0.0)
                    k = tl.load(s_ptrs, mask=(c_valid[:, None]) & (offs_d[None, :] < DIM), other=0.0)
                    sim = tl.dot(q, tl.trans(k), out_dtype=tl.float32) * scale
                    if ROUTE_QUANTIZE == 1:
                        sim = sim.to(tl.bfloat16).to(tl.float32)
                    elif ROUTE_QUANTIZE == 2:
                        sim = sim.to(tl.float16).to(tl.float32)
                    if atom == 0:
                        lse_atoms = sim
                    else:
                        m = tl.maximum(lse_atoms, sim)
                        lse_atoms = m + tl.log(tl.exp(lse_atoms - m) + tl.exp(sim - m))
                if ROUTE_QUANTIZE == 1:
                    lse_atoms = lse_atoms.to(tl.bfloat16).to(tl.float32)
                elif ROUTE_QUANTIZE == 2:
                    lse_atoms = lse_atoms.to(tl.float16).to(tl.float32)
                rel += lse_atoms

            score = rel / QUERY_GROUPS
            if ROUTE_QUANTIZE == 1:
                score = score.to(tl.bfloat16).to(tl.float32)
            elif ROUTE_QUANTIZE == 2:
                score = score.to(tl.float16).to(tl.float32)

            if RESIDUAL_WEIGHT != 0.0:
                res = tl.load(
                    RESIDUAL + off_b * stride_res_b + off_g * stride_res_g + offs_c,
                    mask=c_valid,
                    other=0.0,
                ).to(tl.float32)
                score += RESIDUAL_WEIGHT * res[None, :]

            if CENTER_DISTANCE_WEIGHT != 0.0:
                dist = tl.zeros((BLOCK_Q, BLOCK_C), dtype=tl.float32)
                for dim_i in tl.static_range(0, NDIM):
                    q_coord = tl.load(COORDS + offs_q * NDIM + dim_i, mask=offs_q < NUM_TOKENS, other=0.0).to(tl.float32)
                    c_coord = tl.load(CENTERS + offs_c * NDIM + dim_i, mask=c_valid, other=0.0).to(tl.float32)
                    metric = tl.exp(tl.load(LOG_METRIC + off_g * NDIM + dim_i).to(tl.float32))
                    diff = q_coord[:, None] - c_coord[None, :]
                    dist += diff * diff * metric
                score -= CENTER_DISTANCE_WEIGHT * dist

            score = tl.where(q_valid[:, None] & c_valid[None, :], score, -float("inf"))
            if EXCLUDE_OWN:
                score = tl.where(offs_c[None, :] == own_block[:, None], -float("inf"), score)

            chunk1, chunk_idx1 = tl.max(score, axis=1, return_indices=True, return_indices_tie_break_left=True)
            score2 = tl.where(tl.arange(0, BLOCK_C)[None, :] == chunk_idx1[:, None], -float("inf"), score)
            chunk2, chunk_idx2 = tl.max(score2, axis=1, return_indices=True, return_indices_tie_break_left=True)
            chunk_idx1 = chunk_idx1 + c0
            chunk_idx2 = chunk_idx2 + c0

            best1, idx1, best2, idx2 = _insert_top2(chunk1, chunk_idx1, best1, idx1, best2, idx2)
            best1, idx1, best2, idx2 = _insert_top2(chunk2, chunk_idx2, best1, idx1, best2, idx2)

        out_base = OUT_IDX + off_b * stride_out_b + off_g * stride_out_g + offs_q * stride_out_n
        mask_base = OUT_MASK + off_b * stride_out_b + off_g * stride_out_g + offs_q * stride_out_n
        score_base = OUT_SCORE + off_b * stride_out_b + off_g * stride_out_g + offs_q * stride_out_n
        valid1 = q_valid & (idx1 >= 0) & (best1 > -1.0e20)
        tl.store(out_base + 0, idx1, mask=offs_q < NUM_TOKENS)
        tl.store(mask_base + 0, valid1, mask=offs_q < NUM_TOKENS)
        tl.store(score_base + 0, best1, mask=offs_q < NUM_TOKENS)
        if NUM_SELECTED == 2:
            valid2 = q_valid & (idx2 >= 0) & (best2 > -1.0e20)
            tl.store(out_base + 1, idx2, mask=offs_q < NUM_TOKENS)
            tl.store(mask_base + 1, valid2, mask=offs_q < NUM_TOKENS)
            tl.store(score_base + 1, best2, mask=offs_q < NUM_TOKENS)


    @triton.jit
    def _route_mass_top2_kernel(
        Q,
        SUMMARY_K,
        RESIDUAL,
        SHAPE,
        COORDS,
        CENTERS,
        LOG_METRIC,
        BLOCK_ID,
        VALID_Q,
        OUT_IDX,
        OUT_MASK,
        OUT_SCORE,
        OUT_SUM_ERR,
        stride_q_b: tl.constexpr,
        stride_q_g: tl.constexpr,
        stride_q_h: tl.constexpr,
        stride_q_n: tl.constexpr,
        stride_s_b: tl.constexpr,
        stride_s_g: tl.constexpr,
        stride_s_c: tl.constexpr,
        stride_s_r: tl.constexpr,
        stride_res_b: tl.constexpr,
        stride_res_g: tl.constexpr,
        stride_out_b: tl.constexpr,
        stride_out_g: tl.constexpr,
        stride_out_n: tl.constexpr,
        KV_HEADS: tl.constexpr,
        QUERY_GROUPS: tl.constexpr,
        NUM_TOKENS: tl.constexpr,
        NUM_BLOCKS: tl.constexpr,
        NUM_ATOMS: tl.constexpr,
        DIM: tl.constexpr,
        NDIM: tl.constexpr,
        NUM_SELECTED: tl.constexpr,
        BLOCK_Q: tl.constexpr,
        BLOCK_C: tl.constexpr,
        BLOCK_D: tl.constexpr,
        ROUTE_MODE: tl.constexpr,
        RESIDUAL_WEIGHT: tl.constexpr,
        CENTER_DISTANCE_WEIGHT: tl.constexpr,
        SHAPE_PENALTY_WEIGHT: tl.constexpr,
        EXCLUDE_OWN: tl.constexpr,
        ROUTE_QUANTIZE: tl.constexpr,
    ):
        pid_q = tl.program_id(0)
        pid_bg = tl.program_id(1)
        off_b = pid_bg // KV_HEADS
        off_g = pid_bg - off_b * KV_HEADS

        offs_q = pid_q * BLOCK_Q + tl.arange(0, BLOCK_Q)
        offs_d = tl.arange(0, BLOCK_D)
        q_valid = (offs_q < NUM_TOKENS) & (tl.load(VALID_Q + offs_q, mask=offs_q < NUM_TOKENS, other=0) > 0)
        own_block = tl.load(BLOCK_ID + offs_q, mask=offs_q < NUM_TOKENS, other=-1)
        scale = 1.0 / tl.sqrt(DIM + 0.0)

        max_h = tl.full((BLOCK_Q, QUERY_GROUPS), -float("inf"), tl.float32)
        for c0 in tl.range(0, NUM_BLOCKS, BLOCK_C, num_stages=2):
            offs_c = c0 + tl.arange(0, BLOCK_C)
            c_valid = offs_c < NUM_BLOCKS
            for qh in tl.static_range(0, QUERY_GROUPS):
                qh_selector = tl.arange(0, QUERY_GROUPS)[None, :] == qh
                for atom in tl.static_range(0, NUM_ATOMS):
                    q_ptrs = (
                        Q
                        + off_b * stride_q_b
                        + off_g * stride_q_g
                        + qh * stride_q_h
                        + offs_q[:, None] * stride_q_n
                        + offs_d[None, :]
                    )
                    s_ptrs = (
                        SUMMARY_K
                        + off_b * stride_s_b
                        + off_g * stride_s_g
                        + offs_c[:, None] * stride_s_c
                        + atom * stride_s_r
                        + offs_d[None, :]
                    )
                    q = tl.load(q_ptrs, mask=(q_valid[:, None]) & (offs_d[None, :] < DIM), other=0.0)
                    k = tl.load(s_ptrs, mask=(c_valid[:, None]) & (offs_d[None, :] < DIM), other=0.0)
                    sim = tl.dot(q, tl.trans(k), out_dtype=tl.float32) * scale
                    if ROUTE_QUANTIZE == 1:
                        sim = sim.to(tl.bfloat16).to(tl.float32)
                    elif ROUTE_QUANTIZE == 2:
                        sim = sim.to(tl.float16).to(tl.float32)
                    sim = tl.where(q_valid[:, None] & c_valid[None, :], sim, -float("inf"))
                    sim_max = tl.max(sim, axis=1)
                    max_h = tl.where(qh_selector, tl.maximum(max_h, sim_max[:, None]), max_h)

        denom_h = tl.zeros((BLOCK_Q, QUERY_GROUPS), tl.float32)
        for c0 in tl.range(0, NUM_BLOCKS, BLOCK_C, num_stages=2):
            offs_c = c0 + tl.arange(0, BLOCK_C)
            c_valid = offs_c < NUM_BLOCKS
            for qh in tl.static_range(0, QUERY_GROUPS):
                qh_selector = tl.arange(0, QUERY_GROUPS)[None, :] == qh
                max_col = tl.sum(tl.where(qh_selector, max_h, 0.0), axis=1)
                max_col = tl.where(q_valid, max_col, 0.0)
                atom_sum = tl.zeros((BLOCK_Q, BLOCK_C), tl.float32)
                for atom in tl.static_range(0, NUM_ATOMS):
                    q_ptrs = (
                        Q
                        + off_b * stride_q_b
                        + off_g * stride_q_g
                        + qh * stride_q_h
                        + offs_q[:, None] * stride_q_n
                        + offs_d[None, :]
                    )
                    s_ptrs = (
                        SUMMARY_K
                        + off_b * stride_s_b
                        + off_g * stride_s_g
                        + offs_c[:, None] * stride_s_c
                        + atom * stride_s_r
                        + offs_d[None, :]
                    )
                    q = tl.load(q_ptrs, mask=(q_valid[:, None]) & (offs_d[None, :] < DIM), other=0.0)
                    k = tl.load(s_ptrs, mask=(c_valid[:, None]) & (offs_d[None, :] < DIM), other=0.0)
                    sim = tl.dot(q, tl.trans(k), out_dtype=tl.float32) * scale
                    if ROUTE_QUANTIZE == 1:
                        sim = sim.to(tl.bfloat16).to(tl.float32)
                    elif ROUTE_QUANTIZE == 2:
                        sim = sim.to(tl.float16).to(tl.float32)
                    sim = tl.where(q_valid[:, None] & c_valid[None, :], sim, -float("inf"))
                    atom_sum += tl.exp(sim - max_col[:, None])
                denom_new = tl.sum(atom_sum, axis=1)
                denom_h = tl.where(qh_selector, denom_h + denom_new[:, None], denom_h)

        best1 = tl.full((BLOCK_Q,), -float("inf"), tl.float32)
        best2 = tl.full((BLOCK_Q,), -float("inf"), tl.float32)
        idx1 = tl.full((BLOCK_Q,), -1, tl.int64)
        idx2 = tl.full((BLOCK_Q,), -1, tl.int64)
        prob_sum = tl.zeros((BLOCK_Q,), tl.float32)

        for c0 in tl.range(0, NUM_BLOCKS, BLOCK_C, num_stages=2):
            offs_c = c0 + tl.arange(0, BLOCK_C)
            c_valid = offs_c < NUM_BLOCKS
            block_prob = tl.zeros((BLOCK_Q, BLOCK_C), tl.float32)
            for qh in tl.static_range(0, QUERY_GROUPS):
                qh_selector = tl.arange(0, QUERY_GROUPS)[None, :] == qh
                max_col = tl.sum(tl.where(qh_selector, max_h, 0.0), axis=1)
                max_col = tl.where(q_valid, max_col, 0.0)
                denom_col = tl.sum(tl.where(qh_selector, denom_h, 0.0), axis=1)
                atom_sum = tl.zeros((BLOCK_Q, BLOCK_C), tl.float32)
                for atom in tl.static_range(0, NUM_ATOMS):
                    q_ptrs = (
                        Q
                        + off_b * stride_q_b
                        + off_g * stride_q_g
                        + qh * stride_q_h
                        + offs_q[:, None] * stride_q_n
                        + offs_d[None, :]
                    )
                    s_ptrs = (
                        SUMMARY_K
                        + off_b * stride_s_b
                        + off_g * stride_s_g
                        + offs_c[:, None] * stride_s_c
                        + atom * stride_s_r
                        + offs_d[None, :]
                    )
                    q = tl.load(q_ptrs, mask=(q_valid[:, None]) & (offs_d[None, :] < DIM), other=0.0)
                    k = tl.load(s_ptrs, mask=(c_valid[:, None]) & (offs_d[None, :] < DIM), other=0.0)
                    sim = tl.dot(q, tl.trans(k), out_dtype=tl.float32) * scale
                    if ROUTE_QUANTIZE == 1:
                        sim = sim.to(tl.bfloat16).to(tl.float32)
                    elif ROUTE_QUANTIZE == 2:
                        sim = sim.to(tl.float16).to(tl.float32)
                    sim = tl.where(q_valid[:, None] & c_valid[None, :], sim, -float("inf"))
                    atom_sum += tl.exp(sim - max_col[:, None])
                block_prob += atom_sum / tl.maximum(denom_col[:, None], 1.0e-20)
            block_prob = block_prob / QUERY_GROUPS
            prob_sum += tl.sum(tl.where(c_valid[None, :], block_prob, 0.0), axis=1)

            res = tl.load(RESIDUAL + off_b * stride_res_b + off_g * stride_res_g + offs_c, mask=c_valid, other=0.0).to(tl.float32)
            if ROUTE_MODE == 1:
                score = block_prob + RESIDUAL_WEIGHT * res[None, :]
            elif ROUTE_MODE == 2:
                score = tl.log(tl.maximum(block_prob, 1.0e-12)) + RESIDUAL_WEIGHT * res[None, :]
            elif ROUTE_MODE == 3:
                score = block_prob * (1.0 + RESIDUAL_WEIGHT * res[None, :])
            else:
                score = tl.log(tl.maximum(block_prob, 1.0e-12)) + RESIDUAL_WEIGHT * res[None, :]

            if CENTER_DISTANCE_WEIGHT != 0.0:
                dist = tl.zeros((BLOCK_Q, BLOCK_C), dtype=tl.float32)
                for dim_i in tl.static_range(0, NDIM):
                    q_coord = tl.load(COORDS + offs_q * NDIM + dim_i, mask=offs_q < NUM_TOKENS, other=0.0).to(tl.float32)
                    c_coord = tl.load(CENTERS + offs_c * NDIM + dim_i, mask=c_valid, other=0.0).to(tl.float32)
                    metric = tl.exp(tl.load(LOG_METRIC + off_g * NDIM + dim_i).to(tl.float32))
                    diff = q_coord[:, None] - c_coord[None, :]
                    dist += diff * diff * metric
                score -= CENTER_DISTANCE_WEIGHT * dist
            if SHAPE_PENALTY_WEIGHT != 0.0:
                shape = tl.load(SHAPE + offs_c, mask=c_valid, other=0.0).to(tl.float32)
                score -= SHAPE_PENALTY_WEIGHT * shape[None, :]

            score = tl.where(q_valid[:, None] & c_valid[None, :], score, -float("inf"))
            if EXCLUDE_OWN:
                score = tl.where(offs_c[None, :] == own_block[:, None], -float("inf"), score)

            chunk1, chunk_idx1 = tl.max(score, axis=1, return_indices=True, return_indices_tie_break_left=True)
            score2 = tl.where(tl.arange(0, BLOCK_C)[None, :] == chunk_idx1[:, None], -float("inf"), score)
            chunk2, chunk_idx2 = tl.max(score2, axis=1, return_indices=True, return_indices_tie_break_left=True)
            chunk_idx1 = chunk_idx1 + c0
            chunk_idx2 = chunk_idx2 + c0
            best1, idx1, best2, idx2 = _insert_top2(chunk1, chunk_idx1, best1, idx1, best2, idx2)
            best1, idx1, best2, idx2 = _insert_top2(chunk2, chunk_idx2, best1, idx1, best2, idx2)

        out_base = OUT_IDX + off_b * stride_out_b + off_g * stride_out_g + offs_q * stride_out_n
        mask_base = OUT_MASK + off_b * stride_out_b + off_g * stride_out_g + offs_q * stride_out_n
        score_base = OUT_SCORE + off_b * stride_out_b + off_g * stride_out_g + offs_q * stride_out_n
        valid1 = q_valid & (idx1 >= 0) & (best1 > -1.0e20)
        tl.store(out_base + 0, idx1, mask=offs_q < NUM_TOKENS)
        tl.store(mask_base + 0, valid1, mask=offs_q < NUM_TOKENS)
        tl.store(score_base + 0, best1, mask=offs_q < NUM_TOKENS)
        if NUM_SELECTED == 2:
            valid2 = q_valid & (idx2 >= 0) & (best2 > -1.0e20)
            tl.store(out_base + 1, idx2, mask=offs_q < NUM_TOKENS)
            tl.store(mask_base + 1, valid2, mask=offs_q < NUM_TOKENS)
            tl.store(score_base + 1, best2, mask=offs_q < NUM_TOKENS)
        tl.store(OUT_SUM_ERR + off_b * KV_HEADS * NUM_TOKENS + off_g * NUM_TOKENS + offs_q, tl.abs(prob_sum - 1.0), mask=offs_q < NUM_TOKENS)


def route_lse_topk_triton(
    q_grouped: Tensor,
    summary_k: Tensor,
    compression_residual: Tensor,
    coords_packed: Tensor,
    block_centers: Tensor,
    log_metric: Tensor,
    block_id_packed: Tensor,
    valid_token_mask: Tensor,
    *,
    num_selected_blocks: int,
    residual_weight: float,
    route_center_distance_weight: float,
    exclude_own_block_from_selection: bool,
    block_q: int = 16,
    block_c: int = 32,
) -> tuple[Tensor, Tensor, Tensor, RouteBackendReport]:
    """Streaming exact top-k router for the current logsumexp route score.

    The kernel is intentionally narrow: it targets the high-token H200 regime
    where `num_selected_blocks <= 2` and route materialization dominates. Other
    route modes should use the existing PyTorch path until they get their own
    streaming kernels.
    """
    requested = "triton_streaming_lse"
    reasons: list[str] = []
    if triton is None:
        reasons.append("triton package is not importable")
    if not torch.cuda.is_available():
        reasons.append("CUDA is unavailable")
    if not q_grouped.is_cuda:
        reasons.append("query tensor is not on CUDA")
    if q_grouped.dtype not in (torch.float16, torch.bfloat16):
        reasons.append("Triton route kernel expects fp16 or bf16 query tensors")
    if num_selected_blocks < 1 or num_selected_blocks > 2:
        reasons.append("Triton route kernel currently supports num_selected_blocks in {1, 2}")
    if q_grouped.shape[-1] > 128:
        reasons.append("Triton route kernel supports dim_head <= 128")
    if summary_k.shape[3] > 4:
        reasons.append("Triton route kernel currently supports num_summary_atoms <= 4")
    if q_grouped.shape[2] > 16:
        reasons.append("Triton route kernel currently supports query_heads_per_kv <= 16")
    if reasons:
        empty_idx = torch.empty(0, device=q_grouped.device, dtype=torch.long)
        empty_mask = torch.empty(0, device=q_grouped.device, dtype=torch.bool)
        empty_scores = torch.empty(0, device=q_grouped.device, dtype=torch.float32)
        return empty_idx, empty_mask, empty_scores, RouteBackendReport(requested, "torch_fallback", "; ".join(reasons))

    q_grouped = q_grouped.contiguous()
    summary_k = summary_k.contiguous()
    compression_residual = compression_residual.contiguous()
    coords_packed = coords_packed.to(device=q_grouped.device, dtype=torch.float32).contiguous()
    block_centers = block_centers.to(device=q_grouped.device, dtype=torch.float32).contiguous()
    log_metric = log_metric.to(device=q_grouped.device, dtype=torch.float32).contiguous()
    block_id_packed = block_id_packed.to(device=q_grouped.device, dtype=torch.long).contiguous()
    valid_token_mask = valid_token_mask.to(device=q_grouped.device, dtype=torch.bool).contiguous()

    batch, kv_heads, query_groups, num_tokens, dim = q_grouped.shape
    _, _, num_blocks, num_atoms, _ = summary_k.shape
    ndim = coords_packed.shape[1]
    block_d = max(16, int(2 ** math.ceil(math.log2(dim))))
    selected = torch.empty((batch, kv_heads, num_tokens, num_selected_blocks), device=q_grouped.device, dtype=torch.long)
    selected_mask = torch.empty((batch, kv_heads, num_tokens, num_selected_blocks), device=q_grouped.device, dtype=torch.bool)
    selected_scores = torch.empty((batch, kv_heads, num_tokens, num_selected_blocks), device=q_grouped.device, dtype=torch.float32)
    grid = (triton.cdiv(num_tokens, block_q), batch * kv_heads)
    _route_lse_top2_kernel[grid](
        q_grouped,
        summary_k,
        compression_residual,
        coords_packed,
        block_centers,
        log_metric,
        block_id_packed,
        valid_token_mask,
        selected,
        selected_mask,
        selected_scores,
        q_grouped.stride(0),
        q_grouped.stride(1),
        q_grouped.stride(2),
        q_grouped.stride(3),
        summary_k.stride(0),
        summary_k.stride(1),
        summary_k.stride(2),
        summary_k.stride(3),
        compression_residual.stride(0),
        compression_residual.stride(1),
        selected.stride(0),
        selected.stride(1),
        selected.stride(2),
        batch,
        kv_heads,
        query_groups,
        num_tokens,
        num_blocks,
        num_atoms,
        dim,
        ndim,
        num_selected_blocks,
        block_q,
        block_c,
        block_d,
        float(residual_weight),
        float(route_center_distance_weight),
        bool(exclude_own_block_from_selection),
        1 if q_grouped.dtype is torch.bfloat16 else (2 if q_grouped.dtype is torch.float16 else 0),
        num_warps=4,
        num_stages=2,
    )
    return selected, selected_mask, selected_scores, RouteBackendReport(requested, "triton_streaming_lse", "")


def route_mass_topk_triton(
    q_grouped: Tensor,
    summary_k: Tensor,
    route_residual: Tensor,
    shape_penalty: Tensor,
    coords_packed: Tensor,
    block_centers: Tensor,
    log_metric: Tensor,
    block_id_packed: Tensor,
    valid_token_mask: Tensor,
    *,
    route_score_mode: str,
    num_selected_blocks: int,
    residual_weight: float,
    route_center_distance_weight: float,
    route_shape_penalty_weight: float,
    exclude_own_block_from_selection: bool,
    block_q: int = 16,
    block_c: int = 32,
) -> tuple[Tensor, Tensor, Tensor, Tensor, RouteBackendReport]:
    mode_to_id = {
        "compressed_attention_mass": 1,
        "log_compressed_attention_mass": 2,
        "mass_times_residual": 3,
        "calibrated_mass_residual": 4,
    }
    requested = f"triton_streaming_{route_score_mode}"
    reasons: list[str] = []
    if triton is None:
        reasons.append("triton package is not importable")
    if route_score_mode not in mode_to_id:
        reasons.append(f"unsupported compressed-mass route_score_mode={route_score_mode}")
    if not torch.cuda.is_available():
        reasons.append("CUDA is unavailable")
    if not q_grouped.is_cuda:
        reasons.append("query tensor is not on CUDA")
    if q_grouped.dtype not in (torch.float16, torch.bfloat16, torch.float32):
        reasons.append("Triton mass route kernel expects fp32, fp16, or bf16 query tensors")
    if num_selected_blocks < 1 or num_selected_blocks > 2:
        reasons.append("Triton mass route kernel currently supports num_selected_blocks in {1, 2}")
    if q_grouped.shape[-1] > 128:
        reasons.append("Triton mass route kernel supports dim_head <= 128")
    if summary_k.shape[3] > 2:
        reasons.append("Triton mass route kernel currently supports num_summary_atoms <= 2")
    if q_grouped.shape[2] > 16:
        reasons.append("Triton mass route kernel currently supports query_heads_per_kv <= 16")
    if reasons:
        empty_idx = torch.empty(0, device=q_grouped.device, dtype=torch.long)
        empty_mask = torch.empty(0, device=q_grouped.device, dtype=torch.bool)
        empty_scores = torch.empty(0, device=q_grouped.device, dtype=torch.float32)
        empty_sum = torch.empty(0, device=q_grouped.device, dtype=torch.float32)
        return empty_idx, empty_mask, empty_scores, empty_sum, RouteBackendReport(requested, "torch_fallback", "; ".join(reasons))

    q_grouped = q_grouped.contiguous()
    summary_k = summary_k.contiguous()
    route_residual = route_residual.contiguous()
    coords_packed = coords_packed.to(device=q_grouped.device, dtype=torch.float32).contiguous()
    block_centers = block_centers.to(device=q_grouped.device, dtype=torch.float32).contiguous()
    log_metric = log_metric.to(device=q_grouped.device, dtype=torch.float32).contiguous()
    block_id_packed = block_id_packed.to(device=q_grouped.device, dtype=torch.long).contiguous()
    valid_token_mask = valid_token_mask.to(device=q_grouped.device, dtype=torch.bool).contiguous()
    shape_penalty = shape_penalty.to(device=q_grouped.device, dtype=torch.float32).contiguous()

    batch, kv_heads, query_groups, num_tokens, dim = q_grouped.shape
    _, _, num_blocks, num_atoms, _ = summary_k.shape
    ndim = coords_packed.shape[1]
    block_d = max(16, int(2 ** math.ceil(math.log2(dim))))
    selected = torch.empty((batch, kv_heads, num_tokens, num_selected_blocks), device=q_grouped.device, dtype=torch.long)
    selected_mask = torch.empty((batch, kv_heads, num_tokens, num_selected_blocks), device=q_grouped.device, dtype=torch.bool)
    selected_scores = torch.empty((batch, kv_heads, num_tokens, num_selected_blocks), device=q_grouped.device, dtype=torch.float32)
    prob_sum_error = torch.empty((batch, kv_heads, num_tokens), device=q_grouped.device, dtype=torch.float32)
    grid = (triton.cdiv(num_tokens, block_q), batch * kv_heads)
    _route_mass_top2_kernel[grid](
        q_grouped,
        summary_k,
        route_residual,
        shape_penalty,
        coords_packed,
        block_centers,
        log_metric,
        block_id_packed,
        valid_token_mask,
        selected,
        selected_mask,
        selected_scores,
        prob_sum_error,
        q_grouped.stride(0),
        q_grouped.stride(1),
        q_grouped.stride(2),
        q_grouped.stride(3),
        summary_k.stride(0),
        summary_k.stride(1),
        summary_k.stride(2),
        summary_k.stride(3),
        route_residual.stride(0),
        route_residual.stride(1),
        selected.stride(0),
        selected.stride(1),
        selected.stride(2),
        kv_heads,
        query_groups,
        num_tokens,
        num_blocks,
        num_atoms,
        dim,
        ndim,
        num_selected_blocks,
        block_q,
        block_c,
        block_d,
        mode_to_id.get(route_score_mode, 1),
        float(residual_weight),
        float(route_center_distance_weight),
        float(route_shape_penalty_weight),
        bool(exclude_own_block_from_selection),
        1 if q_grouped.dtype is torch.bfloat16 else (2 if q_grouped.dtype is torch.float16 else 0),
        num_warps=4,
        num_stages=2,
    )
    return selected, selected_mask, selected_scores, prob_sum_error, RouteBackendReport(requested, f"triton_streaming_{route_score_mode}", "")
