"""Time the complete public attention layer on a synthetic vision grid."""
import argparse
import copy
import json
import os
from pathlib import Path
import statistics
import time

import torch
from pack3d import PACK3DAttention, TokenLayout, build_layout, prepare_geometry


def forward_backward(layer, x, layout):
    layer.zero_grad(set_to_none=True)
    x.grad = None
    layer(x, layout).float().square().mean().backward()


@torch.inference_mode()
def inference(layer, x, layout):
    layer(x, layout)


def relative_l2(actual, expected):
    a, b = actual.detach().float(), expected.detach().float()
    return float((a - b).norm() / b.norm().clamp_min(1e-7))


def compare_indexed_gradients(model, x, layout, tolerance):
    geom = layout.geometry
    indexed = prepare_geometry(geom.neighbors, geom.blocks, geom.pool_size).to(x.device)
    other = TokenLayout(layout.grid_shape, layout.order, layout.coords, indexed)
    upstream = torch.randn_like(x)
    params = dict(model.named_parameters())
    def evaluate(case):
        y = model(x, case)
        grads = torch.autograd.grad(y, (x, *params.values()), upstream)
        return (y.detach(), *grads)

    actual, expected = evaluate(layout), evaluate(other)
    errors = {name: relative_l2(a, b) for name, a, b in
              zip(("output", "input", *params), actual, expected)}
    if not all(error < tolerance for error in errors.values()):
        raise RuntimeError(f"full-grid indexed comparison failed: {errors}")
    return other, errors


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--grid", type=int, nargs=3, default=(16, 16, 16))
    p.add_argument("--backend", choices=("reference", "triton"), default="reference")
    p.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    p.add_argument("--dtype", choices=("fp32", "fp16", "bf16"), default="fp32")
    p.add_argument("--preset", choices=("small", "allen15"), default="small",
                   help="layer dimensions, fine blocks, packing order, and summary pooling")
    p.add_argument("--mode", choices=("forward-backward", "inference"), default="forward-backward")
    p.add_argument("--layout", choices=("raster_block", "native_block_morton"),
                   help="override the preset's packing order")
    p.add_argument("--compare-indexed", action="store_true",
                   help="check full-grid gradients against the indexed kernels and alternate both timings")
    p.add_argument("--iterations", type=int, default=20)
    p.add_argument("--warmup", type=int, default=5)
    p.add_argument("--memory-cap-gib", type=float, default=4.0)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    if a.compare_indexed and (a.backend != "triton" or a.mode != "forward-backward"):
        p.error("--compare-indexed requires Triton and forward-backward mode")
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
    if a.preset == "allen15":
        dim, heads, kv_heads, head_dim = 512, 8, 2, 64
        block_shape, pool_size, order = (1, 4, 4), 16, "raster_block"
        probe_grid = (4, 8, 16)
    else:
        dim, heads, kv_heads, head_dim = 64, 4, 2, 16
        block_shape, pool_size, order = (2, 2, 2), 4, "native_block_morton"
        probe_grid = (4, 4, 4)
    order = a.layout or order
    layout_args = dict(block_shape=block_shape, pool_size=pool_size, layout=order)
    model = PACK3DAttention(dim, heads=heads, kv_heads=kv_heads, head_dim=head_dim,
                            block_volume=block_shape[0] * block_shape[1] * block_shape[2],
                            backend=a.backend).to(a.device, dtype)
    oracle = copy.deepcopy(model)
    oracle.backend = "reference"
    small = build_layout(probe_grid, **layout_args).to(a.device)
    probe = torch.randn(1, small.geometry.num_tokens, dim, device=a.device, dtype=dtype, requires_grad=True)
    rp = probe.detach().clone().requires_grad_()
    y, yr = model(probe, small), oracle(rp, small)
    dy = torch.randn_like(y)
    grads = torch.autograd.grad(y, (probe, *model.parameters()), dy)
    refs = torch.autograd.grad(yr, (rp, *oracle.parameters()), dy)
    tolerance = {torch.float32: 3e-5, torch.float16: .005, torch.bfloat16: .035}[dtype]
    errors = [relative_l2(v, r) for v, r in zip([y, *grads], [yr, *refs])]
    if a.mode == "inference":
        with torch.inference_mode():
            actual = model(probe, small)
            errors.append(relative_l2(actual, yr))
        del actual
    if not all(e < tolerance for e in errors):
        raise RuntimeError(f"small-shape correctness gate failed: {max(errors)}")
    del oracle, probe, rp, y, yr, grads, refs, dy, small
    layout = build_layout(tuple(a.grid), **layout_args).to(a.device)
    step = inference if a.mode == "inference" else forward_backward
    x = torch.randn(1, layout.geometry.num_tokens, dim, device=a.device, dtype=dtype,
                    requires_grad=a.mode == "forward-backward")
    cases = {"public": layout}
    if a.compare_indexed:
        cases["indexed"], full_grid_errors = compare_indexed_gradients(model, x, layout, tolerance)
    synchronize = torch.cuda.synchronize if a.device == "cuda" else lambda: None
    for _ in range(a.warmup):
        for case in cases.values():
            step(model, x, case)
    model.zero_grad(set_to_none=True)
    x.grad = None
    synchronize()
    baseline = torch.cuda.memory_allocated() if a.device == "cuda" else 0
    peaks = dict.fromkeys(cases, 0)
    samples = {name: [] for name in cases}
    for iteration in range(a.iterations):
        for name in (reversed(cases) if iteration % 2 else cases):
            synchronize()
            if a.device == "cuda":
                torch.cuda.reset_peak_memory_stats()
            start = time.perf_counter()
            step(model, x, cases[name])
            synchronize()
            samples[name].append(1000 * (time.perf_counter() - start))
            if a.device == "cuda":
                peaks[name] = max(peaks[name], torch.cuda.max_memory_allocated() - baseline)
    times = samples["public"]
    scope = "attention_layer_inference" if a.mode == "inference" else "attention_layer_forward_backward_no_optimizer"
    report = {"scope": scope, "backend": a.backend, "preset": a.preset, "mode": a.mode,
              "batch": 1, "dim": dim, "heads": heads, "kv_heads": kv_heads, "head_dim": head_dim,
              "block_shape": block_shape, "pool_size": pool_size, "layout": order, "radius": 1,
              "warmup": a.warmup, "iterations": a.iterations, "seed": 31,
              "grid": a.grid, "tokens": layout.geometry.num_tokens,
              "summaries": layout.geometry.num_summaries, "dtype": a.dtype,
              "torch": torch.__version__, "device": a.device,
              "gpu": torch.cuda.get_device_name() if a.device == "cuda" else None,
              "median_ms": statistics.median(times), "samples_ms": times,
              "incremental_peak_allocated_bytes": peaks["public"] if a.device == "cuda" else None,
              "correctness_gate": {"grid": probe_grid, "max_relative_l2": max(errors)},
              "publication_quality_timing": False,
              "note": "No exclusive-device attestation; compilation and geometry excluded."}
    if a.compare_indexed:
        report["indexed_comparison"] = {
            "median_ms": statistics.median(samples["indexed"]), "samples_ms": samples["indexed"],
            "incremental_peak_allocated_bytes": peaks["indexed"],
            "full_grid_relative_l2": full_grid_errors,
        }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("x") as f:
        json.dump(report, f, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
