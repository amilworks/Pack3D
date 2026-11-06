# Paper reproduction

These entry points use the bounded historical backend, including the corrected
packed-RoPE wrapper. They do not silently substitute the new streamed backend.
Install PyTorch for your machine, then `python -m pip install -e '.[reproduce]'`.
The CUDA paper recipes additionally require Triton.

## Dataset-free end-to-end smoke test

Run these commands from the repository root; every output directory must be new:

```bash
python reproduce/data/make_smoke_data.py --output artifacts/smoke-data
python reproduce/train.py --config reproduce/configs/smoke.yaml \
  --manifest artifacts/smoke-data/manifest.json --data-root artifacts/smoke-data \
  --output artifacts/smoke-train --device cpu
python reproduce/evaluate.py --config reproduce/configs/smoke.yaml \
  --checkpoint artifacts/smoke-train/results/checkpoints/run/best.pt \
  --manifest artifacts/smoke-data/manifest.json --data-root artifacts/smoke-data \
  --output artifacts/smoke-eval --device cpu
```

This runs two training steps on synthetic I/O fixtures. It checks the pipeline,
not the scientific result. Tracking stays local; no W&B account is needed.

## Principal runs

Choose a recipe under `configs/allen15/`, `configs/msd/heart/`, or
`configs/msd/spleen/`, and supply a prepared manifest as described in
[data/README.md](data/README.md). Set `CUDA_VISIBLE_DEVICES` to exactly one
authorized GPU. Pass `--device cuda`, `--manifest`, `--data-root`, and a fresh
`--output` to the same training command. Recipe budgets, evaluation cadence,
precision, pooling, and branch mixer are retained from the source configurations.

The wrapper validates supported recipes, rejects duplicate/cross-split crop
paths, reserves output directories atomically, checks gradients before optimizer
steps, and attests active rotary transforms. It fails on missing requested CUDA
instead of silently falling back. Existing artifacts are not overwritten.

## Evaluate changed layouts

Use `evaluate.py` with the matching original training recipe and a checkpoint
containing `model` and `config` dictionaries. Loading uses `weights_only=True`;
do not disable this guard to load untrusted pickle payloads.

- No intervention flag: original-layout full-validation evaluation.
- `--pure-repack-seed 2026072600`: intact coarse-group permutation used for the
  principal Allen intervention, preserving fine/coarse memberships and slots.
- `--layout native_block_morton` or `--layout raster_block`: a partition-changing
  named switch. This is outside the pure-repacking theorem.

The two intervention flags are mutually exclusive. Each invocation reuses the
same checkpoint without training or selection on the changed layout. MSD's
original strong group permutation used seed `20260726`; use that explicitly
when reconstructing its fixed intervention. Task metrics must be finite;
undefined optional attention diagnostics serialize as `null` with an explicit
list, not as nonstandard JSON `NaN` values.

## Frozen evidence

`python reproduce/aggregate.py` rebuilds the exact six-seed repacking summary
and paired sign-flip p-value without a dataset or GPU. The mapping of other
included results and remaining reproduction limits is in
[docs/reproducibility.md](../docs/reproducibility.md).

`paper_backend/` is a compatibility snapshot, not the recommended API for new
operator work. It includes some historically unused code paths because the
original model class shares them. Only the documented PACK3D recipes are
supported. The selected-token kernel and unrelated 2D/4D training workflows are
not bundled. Full-data training and original-checkpoint inference were not rerun
as part of repository extraction.
