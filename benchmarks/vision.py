"""Compare whole PACK3D layers from two source trees on one CUDA device."""
import argparse
from contextlib import nullcontext
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

import torch
import triton

import pack3d
from attention import relative_l2


@dataclass(frozen=True)
class Case:
    name: str
    grid: tuple[int, int, int]
    layout: str = "raster_block"
    repack: str | None = None
    precision: str = "BF16"
    batch: int = 1
    small: bool = False


CASES = (
    Case("Raster volume", (32, 128, 64)),
    Case("Morton volume", (32, 128, 64), "native_block_morton"),
    Case("Raster volume", (32, 128, 64), precision="FP16"),
    Case("Morton to raster", (16, 64, 64), "native_block_morton", "raster"),
    Case("Morton to random", (16, 64, 64), "native_block_morton", "random"),
    Case("Raster volume", (16, 64, 64), precision="BF16 autocast"),
    Case("Image slices", (1, 128, 128), batch=2),
    Case("Small Morton block", (16, 16, 16), "native_block_morton", small=True),
)


def load_baseline(src):
    init = src.resolve() / "pack3d" / "__init__.py"
    if not init.is_file() or init == Path(pack3d.__file__).resolve():
        raise ValueError("--baseline-src must point to a separate checkout's src directory")
    spec = importlib.util.spec_from_file_location("pack3d_baseline", init)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fingerprints(module):
    root = Path(module.__file__).parent
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*.py"))}


def layout_for(module, case, block, pool):
    radius = (0, 1, 1) if case.grid[0] == 1 else (1, 1, 1)
    layout = module.build_layout(case.grid, block, radius=radius, pool_size=pool, layout=case.layout)
    if case.repack == "raster":
        return layout.repack(layout.order.argsort())
    if case.repack == "random":
        return layout.repack(torch.randperm(len(layout.order), generator=torch.Generator().manual_seed(17)))
    return layout


def measure_case(old, case, warmups, repeats):
    torch.manual_seed(205)
    if case.small:
        dim, heads, groups, head_dim, block, pool = 64, 4, 2, 16, (2, 2, 2), 4
    else:
        dim, heads, groups, head_dim, block, pool = 512, 8, 2, 64, (1, 4, 4), 16
    dtype = {"BF16": torch.bfloat16, "FP16": torch.float16, "BF16 autocast": torch.float32}[case.precision]
    modules = (old, pack3d)
    left, right = (layout_for(module, case, block, pool) for module in modules)
    for a, b in zip((left.coords, left.order, *left.geometry.tensors),
                    (right.coords, right.order, *right.geometry.tensors), strict=True):
        if not torch.equal(a, b):
            raise RuntimeError("Baseline and candidate layouts differ")
    layouts = (left.to("cuda"), right.to("cuda"))
    models = [module.PACK3DAttention(dim, heads=heads, kv_heads=groups, head_dim=head_dim,
                                     block_volume=math.prod(block), backend="triton").to("cuda", dtype)
              for module in modules]
    models[1].load_state_dict(models[0].state_dict())
    x = torch.randn(case.batch, math.prod(case.grid), dim, device="cuda", dtype=dtype, requires_grad=True)
    dy = torch.randn_like(x)

    def forward(index):
        amp = torch.autocast("cuda", torch.bfloat16) if case.precision == "BF16 autocast" else nullcontext()
        with amp:
            return models[index](x, layouts[index])

    def evaluate(index):
        with torch.inference_mode():
            inference = forward(index)
        out = forward(index)
        grads = torch.autograd.grad(out, (x, *models[index].parameters()), dy)
        return inference, out.detach(), *grads

    baseline, candidate = evaluate(0), evaluate(1)
    names = ("inference", "forward", "input_grad", *dict(models[0].named_parameters()))
    errors = {name: relative_l2(b, a) for name, a, b in zip(names, baseline, candidate, strict=True)}
    del baseline, candidate
    tolerance = .005 if dtype == torch.float16 else .035
    if not all(v < tolerance for v in errors.values()):
        raise RuntimeError(f"{case.name} numerical check failed: {errors}")
    report = dict(name=case.name, grid=case.grid, batch=case.batch, layout=case.layout, repack=case.repack,
                  precision=case.precision, dim=dim, heads=heads, kv_heads=groups, head_dim=head_dim,
                  block_shape=block, pool_size=pool, summaries=right.geometry.num_summaries,
                  radius=(0, 1, 1) if case.grid[0] == 1 else (1, 1, 1), errors_relative_l2=errors)
    for mode in ("inference", "forward_backward"):
        times = [[], []]
        peaks = [0, 0]
        torch.cuda.synchronize()
        for iteration in range(warmups + repeats):
            for index in ((0, 1) if iteration % 2 == 0 else (1, 0)):
                torch.cuda.reset_peak_memory_stats()
                floor = torch.cuda.memory_allocated()
                start = time.perf_counter()
                if mode == "inference":
                    with torch.inference_mode():
                        forward(index)
                else:
                    forward(index).backward(dy)
                torch.cuda.synchronize()
                elapsed = (time.perf_counter() - start) * 1000
                if iteration >= warmups:
                    times[index].append(elapsed)
                    peaks[index] = max(peaks[index], torch.cuda.max_memory_allocated() - floor)
                models[index].zero_grad(set_to_none=True)
                x.grad = None
        report[mode] = {key: {"samples_ms": values, "median_ms": statistics.median(values),
                              "peak_extra_bytes": peak}
                        for key, values, peak in zip(("baseline", "combined"), times, peaks, strict=True)}
    return report


def table(data, raw_name):
    rows = [
        f"# Combined vision optimizations on {data['gpu']}", "",
        f"Baseline `{data['baseline_revision']}`. Each value is the median whole-layer latency in "
        f"milliseconds from {data['repeats']} alternating pairs on one shared {data['gpu']}. "
        "Speedup is baseline median divided by the combined median.", "",
        "| Workload | Batch × grid (Z,Y,X) | Precision | Inference before → after (ms) | Speedup | "
        "Forward + backward before → after (ms) | Speedup |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for case in data["cases"]:
        shape = "×".join(map(str, case["grid"]))
        row = f"| {case['name']} | {case['batch']} × ({shape}) | {case['precision']} |"
        for mode in ("inference", "forward_backward"):
            before = case[mode]["baseline"]["median_ms"]
            after = case[mode]["combined"]["median_ms"]
            row += f" {before:.3f} → {after:.3f} | {before/after:.2f}× |"
        rows.append(row)
    rows += ["", "Both revisions use identical weights, inputs, upstream gradients and transported geometry. "
             "Inference uses inference mode. Backward consumes a preallocated gradient. Timings exclude "
             "geometry setup, repacking, compilation, cold rotary tables and optimizer steps. "
             "BF16 autocast uses FP32 parameters and inputs. Other rows use the named storage dtype. "
             "The small block uses 64 channels. All other rows use 512. "
             f"[Raw samples, peak allocations, source hashes and gradient errors]({raw_name})", ""]
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-src", required=True, type=Path)
    parser.add_argument("--baseline-revision", required=True, help="revision label accompanying the source hashes")
    parser.add_argument("--output", required=True, type=Path, help="new .json file and matching .md table")
    parser.add_argument("--warmup", type=int, default=7)
    parser.add_argument("--iterations", type=int, default=31)
    args = parser.parse_args()
    md = args.output.with_suffix(".md")
    if args.output.suffix != ".json" or args.output.exists() or md.exists():
        parser.error("choose new JSON and Markdown output paths")
    if args.warmup < 1 or args.iterations < 3:
        parser.error("use at least one warmup and three timed pairs")
    visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    if not visible or torch.cuda.device_count() != 1:
        parser.error("select a single available GPU with CUDA_VISIBLE_DEVICES")
    free, total = torch.cuda.mem_get_info()
    if free < 14 * 2**30:
        parser.error("this matrix needs 12 GiB plus 2 GiB of headroom")
    torch.cuda.set_per_process_memory_fraction(12 * 2**30 / total)
    torch.set_num_threads(4)
    baseline = load_baseline(args.baseline_src)
    report = dict(baseline_revision=args.baseline_revision, torch=torch.__version__, triton=triton.__version__,
                  cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(), capability=torch.cuda.get_device_capability(),
                  seed=205, repack_seed=17, warmups=args.warmup, repeats=args.iterations, allocator_cap_gib=12,
                  protocol="Alternating full-layer synchronized wall times, preallocated upstream gradient, no optimizer.",
                  source_sha256=dict(baseline=fingerprints(baseline), combined=fingerprints(pack3d)), cases=[])
    try:
        device = subprocess.check_output(["nvidia-smi", "-i", visible, "--query-gpu=index,driver_version",
                                          "--format=csv,noheader"], text=True)
        index, driver = device.strip().split(", ")
        report.update(physical_gpu=int(index), driver=driver)
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    for case in CASES:
        result = measure_case(baseline, case, args.warmup, args.iterations)
        report["cases"].append(result)
        print(f"Measured {case.name} {case.precision}", flush=True)
        torch.cuda.empty_cache()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as f:
        json.dump(report, f, indent=2, allow_nan=False)
        f.write("\n")
    with md.open("x") as f:
        f.write(table(report, args.output.name))


if __name__ == "__main__":
    main()
