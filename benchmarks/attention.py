"""Correctness-gated full attention-layer forward/backward timing, no optimizer."""
import argparse
import copy
import json
import os
from pathlib import Path
import statistics
import time

import torch
from pack3d import PACK3DAttention, build_layout


def step(layer, x, layout):
    layer.zero_grad(set_to_none=True)
    x.grad = None
    layer(x, layout).float().square().mean().backward()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--grid", type=int, nargs=3, default=(16, 16, 16))
    p.add_argument("--backend", choices=("reference", "triton"), default="reference")
    p.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    p.add_argument("--dtype", choices=("fp32", "fp16", "bf16"), default="fp32")
    p.add_argument("--iterations", type=int, default=20)
    p.add_argument("--warmup", type=int, default=5)
    p.add_argument("--memory-cap-gib", type=float, default=4.0)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    if a.iterations < 3 or a.warmup < 1 or not 0 < a.memory_cap_gib <= 32:
        raise ValueError("require >=3 iterations, >=1 warmup, and a cap in (0,32] GiB")
    if a.device == "cuda":
        if not os.environ.get("CUDA_VISIBLE_DEVICES") or torch.cuda.device_count() != 1:
            raise ValueError("select exactly one authorized GPU with CUDA_VISIBLE_DEVICES")
        free, total = torch.cuda.mem_get_info()
        if free < (a.memory_cap_gib + 2) * 1024**3:
            raise RuntimeError("insufficient free memory for cap plus 2 GiB safety margin")
        torch.cuda.set_per_process_memory_fraction(a.memory_cap_gib * 1024**3 / total)
    elif a.backend == "triton":
        raise ValueError("Triton timing requires CUDA")
    dtype = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}[a.dtype]
    torch.manual_seed(31)
    model = PACK3DAttention(64, heads=4, kv_heads=2, head_dim=16, backend=a.backend).to(a.device, dtype)
    oracle = copy.deepcopy(model)
    oracle.backend = "reference"
    small = build_layout((4, 4, 4), pool_size=4).to(a.device)
    probe = torch.randn(1, 64, 64, device=a.device, dtype=dtype, requires_grad=True)
    rp = probe.detach().clone().requires_grad_()
    y, yr = model(probe, small), oracle(rp, small)
    dy = torch.randn_like(y)
    grads = torch.autograd.grad(y, (probe, *model.parameters()), dy)
    refs = torch.autograd.grad(yr, (rp, *oracle.parameters()), dy)
    tolerance = 3e-5 if dtype == torch.float32 else .035
    errors = [float((v.detach().float() - r.detach().float()).norm() / r.detach().float().norm().clamp_min(1e-7))
              for v, r in zip([y, *grads], [yr, *refs])]
    if not all(e < tolerance for e in errors):
        raise RuntimeError(f"small-shape correctness gate failed: {max(errors)}")
    del oracle, probe, rp, y, yr, grads, refs, dy, small
    layout = build_layout(tuple(a.grid), pool_size=4).to(a.device)
    x = torch.randn(1, layout.geometry.num_tokens, 64, device=a.device, dtype=dtype, requires_grad=True)
    synchronize = torch.cuda.synchronize if a.device == "cuda" else lambda: None
    for _ in range(a.warmup):
        step(model, x, layout)
    model.zero_grad(set_to_none=True)
    x.grad = None
    synchronize()
    baseline = 0
    if a.device == "cuda":
        baseline = torch.cuda.memory_allocated()
        torch.cuda.reset_peak_memory_stats()
    times = []
    for _ in range(a.iterations):
        synchronize()
        start = time.perf_counter()
        step(model, x, layout)
        synchronize()
        times.append(1000 * (time.perf_counter() - start))
    report = {"scope": "attention_layer_forward_backward_no_optimizer", "backend": a.backend,
              "grid": a.grid, "tokens": layout.geometry.num_tokens,
              "summaries": layout.geometry.num_summaries, "dtype": a.dtype,
              "torch": torch.__version__, "device": a.device,
              "gpu": torch.cuda.get_device_name() if a.device == "cuda" else None,
              "median_ms": statistics.median(times), "samples_ms": times,
              "incremental_peak_allocated_bytes": torch.cuda.max_memory_allocated() - baseline
              if a.device == "cuda" else None,
              "correctness_gate": {"grid": [4, 4, 4], "max_relative_l2": max(errors)},
              "publication_quality_timing": False,
              "note": "No exclusive-device attestation; compilation and geometry excluded."}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("x") as f:
        json.dump(report, f, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
