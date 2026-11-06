from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import platform
from typing import Any


def _version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except Exception:
        return None


def _importable(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def collect_env() -> dict[str, Any]:
    """Collect launch-time capability and environment information."""
    info: dict[str, Any] = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "packages": {
            "torch": _version("torch"),
            "torchvision": _version("torchvision"),
            "timm": _version("timm"),
            "triton": _version("triton"),
            "flash_attn": _version("flash-attn"),
            "wandb": _version("wandb"),
        },
        "cuda_available": False,
        "gpu_model": None,
        "compute_capability": None,
        "bf16_supported": False,
        "tf32_enabled": False,
        "nccl_available": False,
        "triton_importable": _importable("triton"),
        "selected_kernel_importable": False,
        "flashattention_importable": _importable("flash_attn"),
        "sdpa_available": False,
    }
    try:
        import torch

        info["cuda_available"] = bool(torch.cuda.is_available())
        info["sdpa_available"] = hasattr(torch.nn.functional, "scaled_dot_product_attention")
        info["nccl_available"] = bool(getattr(torch.distributed, "is_nccl_available", lambda: False)())
        info["tf32_enabled"] = bool(getattr(torch.backends.cuda.matmul, "allow_tf32", False))
        if torch.cuda.is_available():
            idx = torch.cuda.current_device()
            info["gpu_model"] = torch.cuda.get_device_name(idx)
            info["compute_capability"] = list(torch.cuda.get_device_capability(idx))
            info["bf16_supported"] = bool(torch.cuda.is_bf16_supported())
    except Exception as exc:
        info["torch_error"] = str(exc)
    try:
        from hypernsa.attention.triton_selected import triton_status

        status = triton_status()
        info["selected_kernel_importable"] = bool(status.get("native_sparse_attention_importable", False))
        info["selected_kernel_error"] = status.get("native_sparse_attention_error", "")
    except Exception as exc:
        info["selected_kernel_error"] = str(exc)
    return info


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit compact JSON")
    args = parser.parse_args()
    info = collect_env()
    print(json.dumps(info, indent=None if args.json else 2, sort_keys=True))


if __name__ == "__main__":
    main()
