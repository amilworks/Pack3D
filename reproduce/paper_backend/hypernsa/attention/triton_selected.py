from __future__ import annotations

from dataclasses import dataclass
import importlib
import importlib.util
from typing import Callable

import torch
from torch import Tensor


@dataclass(frozen=True)
class BackendReport:
    """Selected-attention backend decision for one forward pass."""

    backend_requested: str
    backend_actual: str
    fallback_reason: str


def triton_status() -> dict[str, object]:
    """Return import/runtime capability for the bundled Triton selected path."""
    status: dict[str, object] = {
        "torch_cuda_available": torch.cuda.is_available(),
        "triton_importable": importlib.util.find_spec("triton") is not None,
        "native_sparse_attention_importable": False,
        "native_sparse_attention_error": "",
    }
    if not status["triton_importable"]:
        status["native_sparse_attention_error"] = "triton package is not importable"
        return status
    try:
        importlib.import_module("triton_native_sparse_attention")
        status["native_sparse_attention_importable"] = True
    except Exception as exc:  # pragma: no cover - depends on optional local CUDA stack.
        status["native_sparse_attention_error"] = str(exc)
    return status


def selected_attention(
    q: Tensor,
    k: Tensor,
    v: Tensor,
    block_size: int,
    selected_block_indices: Tensor,
    selected_block_mask: Tensor,
    *,
    use_triton_kernel: bool,
    torch_fallback: Callable[[Tensor, Tensor, Tensor, Tensor, Tensor], Tensor],
    include_block_causal: bool = False,
    validate_output: bool = False,
) -> tuple[Tensor, BackendReport]:
    """Run selected attention through Triton when valid, otherwise report fallback.

    The fallback is deliberately explicit. A caller that requested Triton gets a
    report explaining why the PyTorch grouped path was used instead.
    """
    requested = "triton_selected" if use_triton_kernel else "torch_fallback"
    if not use_triton_kernel:
        out = torch_fallback(q, k, v, selected_block_indices, selected_block_mask)
        return out, BackendReport(requested, "torch_fallback", "")
    if selected_block_indices.shape[-1] == 0:
        out = torch_fallback(q, k, v, selected_block_indices, selected_block_mask)
        return out, BackendReport(requested, "torch_fallback", "no selected blocks after routing")

    reasons: list[str] = []
    if not torch.cuda.is_available():
        reasons.append("CUDA is unavailable")
    if not q.is_cuda:
        reasons.append("query tensor is not on CUDA")
    if block_size < 16 or block_size % 16 != 0:
        reasons.append("block_size must be >=16 and divisible by 16")
    if q.shape[1] % k.shape[1] != 0:
        reasons.append("query heads must be divisible by KV heads")
    head_groups = q.shape[1] // k.shape[1]
    if 16 % head_groups != 0:
        reasons.append("query heads per KV group must divide 16 for the bundled kernel")
    if q.dtype not in (torch.float16, torch.bfloat16):
        reasons.append("Triton selected attention expects fp16 or bf16 tensors")
    if importlib.util.find_spec("triton") is None:
        reasons.append("triton package is not importable")

    native_sparse_attend = None
    if not reasons:
        try:
            native_mod = importlib.import_module("triton_native_sparse_attention")
            native_sparse_attend = native_mod.native_sparse_attend
        except Exception as exc:  # pragma: no cover - optional dependency path.
            reasons.append(f"bundled Triton module import failed: {exc}")

    if reasons:
        out = torch_fallback(q, k, v, selected_block_indices, selected_block_mask)
        return out, BackendReport(requested, "torch_fallback", "; ".join(reasons))

    try:
        assert native_sparse_attend is not None
        out = native_sparse_attend(
            q,
            k,
            v,
            block_size,
            selected_block_indices,
            selected_block_mask,
            include_block_causal=include_block_causal,
        )
        if validate_output and not torch.isfinite(out).all():
            fallback = torch_fallback(q, k, v, selected_block_indices, selected_block_mask)
            return fallback, BackendReport(requested, "torch_fallback", "Triton execution produced non-finite output")
        return out, BackendReport(requested, "triton_selected", "")
    except Exception as exc:  # pragma: no cover - requires CUDA/Triton execution.
        out = torch_fallback(q, k, v, selected_block_indices, selected_block_mask)
        return out, BackendReport(requested, "torch_fallback", f"Triton execution failed: {exc}")
