# Attention timing

The benchmark times forward plus backward of the complete clean attention
layer, including projections, RoPE, gates, and output residual. It excludes
geometry construction, kernel compilation, decoder, loss pipeline, and optimizer.
The scalar loss is only a backward driver. It is not an end-to-end training rate.

```bash
python benchmarks/attention.py --grid 4 4 4 --backend reference --device cpu \
  --iterations 5 --warmup 2 --output artifacts/cpu-benchmark.json
```

For GPU measurement, set `CUDA_VISIBLE_DEVICES` to one authorized device and use
`--backend triton --device cuda --dtype bf16`. The default allocator cap is 4 GiB;
at least another 2 GiB must be free. It does not stop or alter other GPU jobs.
Every output path must be new.

Before timing, a small `4^3` field is compared with the reference for outputs and
all layer gradients. This gate is explicitly smaller than a requested large
benchmark grid; it is not a dense-reference comparison at that large shape.
Use the correctness suite for broader numerical validation.

The JSON records raw timing samples, shape, summary count, dtype, software,
device, and incremental allocated peak memory above warmed persistent state.
CPU memory is not reported. PyTorch allocator measurements exclude allocations
outside that allocator. All timings default to provisional because the script
cannot attest exclusive hardware access. They must not replace historical paper
timings or be advertised as universal speed/memory improvements.
