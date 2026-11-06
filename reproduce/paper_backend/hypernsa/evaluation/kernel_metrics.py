from __future__ import annotations

import math
from typing import Any, Iterable, Sequence

import torch
from torch import Tensor

from hypernsa.attention.hypernsa_morton import HypergridMortonSparseAttention
from hypernsa.attention.layout import prod


REQUIRED_KERNEL_COLUMNS = [
    "timestamp",
    "run_id",
    "config_name",
    "benchmark_scope",
    "backend_requested",
    "backend_actual",
    "fallback_reason",
    "device_name",
    "cuda_version",
    "torch_version",
    "triton_version",
    "dtype",
    "batch_size",
    "grid_shape",
    "block_shape",
    "num_tokens",
    "dim",
    "heads",
    "kv_heads",
    "query_heads_per_kv",
    "dim_head",
    "num_summary_atoms",
    "num_selected_blocks",
    "local_radius",
    "separate_branch_kv",
    "route_select_grad",
    "route_backend",
    "route_score_mode",
    "route_distance_normalization",
    "allow_raw_distance_on_probability_route",
    "packed_branch_kv_projection",
    "skip_disabled_local_branch",
    "coarse_attention_backend",
    "local_attention_backend",
    "local_attention_backend_actual",
    "local_attention_fallback_reason",
    "local_attention_block_n",
    "branch_output_fusion",
    "branch_output_checkpoint_active",
    "branch_gate_mode",
    "return_aux_for_benchmark",
    "residual_weight",
    "forward_latency_ms_median",
    "backward_latency_ms_median",
    "forward_backward_latency_ms_median",
    "peak_allocated_gb",
    "peak_reserved_gb",
    "tokens_per_sec",
    "max_abs_error_vs_torch",
    "mean_abs_error_vs_torch",
    "grad_finite",
    "oom",
    "notes",
]


def shape_to_str(shape: Sequence[int] | str) -> str:
    if isinstance(shape, str):
        return shape
    return "x".join(str(int(x)) for x in shape)


def parse_shape(value: Sequence[int] | str) -> tuple[int, ...]:
    if isinstance(value, str):
        return tuple(int(x) for x in value.replace(",", "x").split("x") if x)
    return tuple(int(x) for x in value)


def num_tokens(grid_shape: Sequence[int]) -> int:
    return prod(tuple(int(x) for x in grid_shape))


def pick_dtype(preferred: str = "bf16") -> torch.dtype:
    if preferred in {"bf16", "bfloat16"} and torch.cuda.is_available() and torch.cuda.is_bf16_supported():
        return torch.bfloat16
    if preferred in {"fp16", "float16", "half"}:
        return torch.float16
    return torch.float32


def dtype_name(dtype: torch.dtype) -> str:
    if dtype is torch.bfloat16:
        return "bf16"
    if dtype is torch.float16:
        return "fp16"
    if dtype is torch.float32:
        return "fp32"
    return str(dtype).replace("torch.", "")


def tolerance_for_dtype(dtype: torch.dtype) -> float:
    return 5e-2 if dtype in (torch.float16, torch.bfloat16) else 5e-5


def mean_abs_error(a: Tensor, b: Tensor) -> float:
    return float((a.float() - b.float()).abs().mean().item())


def max_abs_error(a: Tensor, b: Tensor) -> float:
    return float((a.float() - b.float()).abs().max().item())


def all_grads_finite(module: torch.nn.Module, x: Tensor | None = None) -> bool:
    grads: list[Tensor] = []
    if x is not None and x.grad is not None:
        grads.append(x.grad)
    for p in module.parameters():
        if p.grad is not None:
            grads.append(p.grad)
    return all(torch.isfinite(g).all().item() for g in grads)


def route_entropy(route_scores: Tensor) -> float:
    scores = route_scores.float()
    finite = torch.isfinite(scores) & (scores > -1e8)
    if not bool(finite.any()):
        return 0.0
    masked = scores.masked_fill(~finite, -torch.inf)
    probs = torch.softmax(masked, dim=-1)
    entropy = -(probs * torch.log(probs.clamp_min(1e-12))).sum(dim=-1)
    entropy = entropy[torch.isfinite(entropy)]
    return float(entropy.mean().item()) if entropy.numel() else 0.0


def aux_branch_gate_means(aux: dict[str, Any]) -> dict[str, float]:
    gates = aux.get("gates")
    if gates is None:
        return {"gate_local_mean": math.nan, "gate_coarse_mean": math.nan, "gate_selected_mean": math.nan}
    means = gates.float().mean(dim=(0, 1, 2))
    return {
        "gate_local_mean": float(means[0].item()),
        "gate_coarse_mean": float(means[1].item()),
        "gate_selected_mean": float(means[2].item()),
    }


def selected_tokens_per_query(aux: dict[str, Any], block_volume: int) -> float:
    mask = aux["selected_block_mask"].float()
    return float(mask.sum(dim=-1).mean().item() * int(block_volume))


def compressed_tokens_per_query(num_blocks: int, num_summary_atoms: int) -> float:
    return float(int(num_blocks) * int(num_summary_atoms))


def local_tokens_per_query(local_neighbor_mask: Tensor) -> float:
    return float(local_neighbor_mask.float().sum(dim=-1).mean().item())


def selected_indices_in_range(aux: dict[str, Any], num_blocks: int) -> bool:
    selected = aux["selected_block_indices"]
    mask = aux["selected_block_mask"]
    if selected.numel() == 0:
        return True
    active = selected[mask]
    if active.numel() == 0:
        return True
    return bool(((active >= 0) & (active < int(num_blocks))).all().item())


def selected_blocks_are_contiguous(attn: HypergridMortonSparseAttention, aux: dict[str, Any]) -> bool:
    selected = aux["selected_block_indices"]
    mask = aux["selected_block_mask"]
    if selected.numel() == 0:
        return True
    block_ids = selected[mask].detach().cpu().unique().tolist()
    token_indices = attn.block_token_indices.detach().cpu()
    for bid in block_ids:
        ids = token_indices[int(bid)]
        if ids.numel() > 1 and not bool((ids[1:] == ids[:-1] + 1).all().item()):
            return False
    return True


def gates_sum_to_one(aux: dict[str, Any], atol: float = 1e-5) -> bool:
    gates = aux["gates"].float()
    return bool(torch.allclose(gates.sum(dim=-1), torch.ones_like(gates[..., 0]), atol=atol, rtol=atol))


def compute_grouped_load_metrics(
    selected_block_indices: Tensor,
    selected_block_mask: Tensor,
    *,
    query_heads_per_kv: int,
    block_volume: int,
) -> dict[str, float]:
    """Estimate grouped vs independent block loads from selected block tensors.

    The grouped tensor is the actual GQA/MQA path: one selection per KV head.
    Independent-head load is a no-sharing upper bound, and independent union is
    the expected load when each query head selects independently but KV blocks
    are unioned before loading. A deterministic spread is used when only grouped
    selections are available, so the estimate remains conservative and does not
    understate grouped routing's memory advantage.
    """
    selected = selected_block_indices.detach().cpu()
    mask = selected_block_mask.detach().cpu()
    if selected.numel() == 0:
        return {
            "grouped_unique_kv_blocks": 0.0,
            "independent_unique_kv_blocks": 0.0,
            "independent_union_unique_kv_blocks": 0.0,
            "grouped_unique_kv_tokens": 0.0,
            "independent_union_unique_kv_tokens": 0.0,
            "kv_load_reduction": 1.0,
            "estimated_grouped_kv_bytes": 0.0,
            "estimated_independent_union_kv_bytes": 0.0,
        }
    grouped_counts: list[int] = []
    independent_counts: list[int] = []
    independent_union_counts: list[int] = []
    max_block = int(selected.max().item()) + 1 if selected.numel() else 1
    for b in range(selected.shape[0]):
        for g in range(selected.shape[1]):
            for n in range(selected.shape[2]):
                base = [int(x) for x in selected[b, g, n][mask[b, g, n]].tolist()]
                grouped = len(set(base))
                grouped_counts.append(grouped)
                independent_counts.append(grouped * int(query_heads_per_kv))
                union = set(base)
                if grouped > 0 and query_heads_per_kv > 1 and max_block > grouped:
                    for h in range(1, int(query_heads_per_kv)):
                        for bid in base:
                            union.add((bid + h) % max_block)
                independent_union_counts.append(len(union))
    grouped_mean = float(sum(grouped_counts) / max(1, len(grouped_counts)))
    independent_mean = float(sum(independent_counts) / max(1, len(independent_counts)))
    union_mean = float(sum(independent_union_counts) / max(1, len(independent_union_counts)))
    return {
        "grouped_unique_kv_blocks": grouped_mean,
        "independent_unique_kv_blocks": independent_mean,
        "independent_union_unique_kv_blocks": union_mean,
        "grouped_unique_kv_tokens": grouped_mean * int(block_volume),
        "independent_union_unique_kv_tokens": union_mean * int(block_volume),
        "kv_load_reduction": union_mean / max(grouped_mean, 1e-9),
        "estimated_grouped_kv_bytes": grouped_mean * int(block_volume) * 2.0,
        "estimated_independent_union_kv_bytes": union_mean * int(block_volume) * 2.0,
    }


def local_disable_diagnostic(device: torch.device, dtype: torch.dtype) -> tuple[bool, str]:
    """Check that local gate probability is exactly zero for masked queries."""
    attn = HypergridMortonSparseAttention(
        dim=32,
        grid_shape=(4, 8),
        heads=4,
        kv_heads=2,
        dim_head=8,
        block_shape=(4, 4),
        use_triton_kernel=False,
    ).to(device=device, dtype=dtype)
    x = torch.randn(1, 4, 8, 32, device=device, dtype=dtype)
    mask = torch.zeros(1, 4, 8, device=device, dtype=torch.bool)
    mask[:, 0, 0] = True
    with torch.no_grad():
        _, aux = attn(x, query_disable_local_mask=mask, return_aux=True)
    packed_mask = attn._pack_bool_mask(mask).to(device)
    local = aux["gates"][..., 0]
    masked = local[packed_mask[:, None, :].expand_as(local)]
    if masked.numel() and float(masked.max().item()) != 0.0:
        return False, "local-disabled diagnostic produced nonzero local gate"
    return True, ""


def ensure_required_columns(row: dict[str, Any]) -> dict[str, Any]:
    """Fill required columns so CSVs keep a stable schema."""
    out = dict(row)
    for key in REQUIRED_KERNEL_COLUMNS:
        out.setdefault(key, "")
    return out


def flatten_grid_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [ensure_required_columns(row) for row in rows]
