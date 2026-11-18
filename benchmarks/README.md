# Attention timing

The benchmark times the complete public attention layer, including projections,
RoPE, gates, and output residual. The default mode runs forward and backward
with a synthetic scalar loss. Use `--mode inference` to time a forward pass
under `torch.inference_mode()`. Both modes exclude geometry construction and
kernel compilation. Neither runs an optimizer.

```bash
python benchmarks/attention.py --grid 4 4 4 --backend reference --device cpu \
  --iterations 5 --warmup 2 --output artifacts/cpu-benchmark.json
```

For GPU measurement, set `CUDA_VISIBLE_DEVICES` to one authorized device and use
`--backend triton --device cuda --dtype bf16`. The default allocator cap is 4 GiB;
at least another 2 GiB must be free. It does not stop or alter other GPU jobs.
Every output path must be new.

The `allen15` preset uses the paper's 512 channels, 8 query heads, 2 KV heads,
head dimension 64, raster packing, 16-token fine blocks, and 16-block coarse
pooling. With one GPU selected, run the 262,144-token grid to time inference
with 1,024 coarse summaries.

```bash
python benchmarks/attention.py --preset allen15 --grid 32 128 64 \
  --backend triton --device cuda --dtype bf16 --mode inference \
  --memory-cap-gib 8 --output artifacts/allen15-inference.json
```

Before timing, each preset checks outputs and all layer gradients against the
PyTorch reference on a smaller field. The small preset uses a 4 × 4 × 4 grid
and Allen-15 uses 4 × 8 × 16. Inference runs also check the gradient-free path.

The JSON records raw timing samples, shape, summary count, dtype, software,
device, and incremental allocated peak memory above warmed persistent state.
CPU memory is not reported. PyTorch allocator measurements exclude allocations
outside that allocator. All timings default to provisional because the script
cannot attest exclusive hardware access. They must not replace historical paper
timings or be advertised as universal speed/memory improvements.

## H200 measurements on November 17, 2026

These are medians of 25 warm runs on one shared H200 with BF16 inputs and batch
size one. The baseline is the preceding public Triton layer. The two larger
grids use the Allen-15 preset. [Raw samples, memory measurements, and CUDA profiles](results/h200_2026-11-17.json)

| Tokens | Inference before → after | Forward + backward before → after |
| ---: | ---: | ---: |
| 4,096 | 1.69 → 0.71 ms | 8.71 → 3.53 ms |
| 65,536 | 3.18 → 1.60 ms | 11.17 → 7.26 ms |
| 262,144 | 12.93 → 6.33 ms | 44.78 → 28.80 ms |

## Local backward on November 18, 2026

`--compare-indexed` times the public layer twice on the same model, input,
and graph. It alternates the two paths each iteration and checks the output,
input gradient, and every parameter gradient on the full requested grid.
With one GPU selected, this command reproduces the native Morton comparison.

```bash
python benchmarks/attention.py --preset allen15 --grid 32 128 64 \
  --backend triton --device cuda --dtype bf16 --layout native_block_morton \
  --compare-indexed --warmup 7 --iterations 31 --memory-cap-gib 8 \
  --output artifacts/morton-local-backward.json
```

Medians below are for complete forward and backward at batch size one on a
shared H200. The indexed column uses the preceding local-gradient kernels.
Both columns use the same optimized forward and global attention.

| Tokens | Packing | Dtype | Indexed | Spatial tiles |
| ---: | --- | --- | ---: | ---: |
| 4,096 | Native Morton, small preset | BF16 | 2.29 ms | 2.28 ms |
| 65,536 | Raster | BF16 | 7.21 ms | 4.77 ms |
| 65,536 | Native Morton | BF16 | 7.24 ms | 4.84 ms |
| 262,144 | Raster | BF16 | 28.73 ms | 18.81 ms |
| 262,144 | Native Morton | BF16 | 28.66 ms | 18.97 ms |
| 262,144 | Raster | FP16 | 27.96 ms | 19.15 ms |

Incremental peak allocation was 4.03 GiB for both paths on the 262,144-token
grid. Geometry is prepared before timing. Native Morton keeps an extra 1 MiB
index at this size, and raster packing uses direct strides. [Raw timings, gradient errors, and kernel profiles](results/h200_2026-11-18.json)

Regenerate the [README figure](../docs/assets/h200-attention-latency.png) from the recorded samples
with `python benchmarks/plot_h200.py` in an environment with Matplotlib installed.
