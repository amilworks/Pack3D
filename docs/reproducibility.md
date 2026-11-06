# Reproducibility map

There are three different levels of reproduction:

1. **Operator checks:** the dataset-free [examples](../examples/) and the numerical tests.
2. **Metric regeneration:** recompute the README's six-seed summary from frozen
   per-seed data with `python reproduce/aggregate.py`.
3. **Model runs:** use supplied principal recipes, your prepared dataset, and the
   paper backend through [reproduce/train.py](../reproduce/train.py) and
   [reproduce/evaluate.py](../reproduce/evaluate.py).

The release smoke test checks wiring, not recovery of a published Dice score.
No principal model was retrained during extraction. Dataset files and pretrained
checkpoints are not bundled. Full historical raw-data preprocessing, all auxiliary
classification experiments, and U-Net/UNETR training programs are not part of this
first operator release; their included result tables remain frozen evidence.

Use `python -m pip install -e '.[dev,reproduce]' -c reproduce/constraints-tested.txt`
to select the optional dependency versions validated for this extraction. Install
your CPU/CUDA PyTorch wheel first. The constraints need Python 3.12 or newer. They
record a tested environment, not a claim that other dependency versions fail.

## Result families

| Family | Included evidence | Reproduction boundary |
| --- | --- | --- |
| Allen-15 six-seed pure repacking | [exact per-seed CSV](../results/allen15_repacking/seed_metrics.csv) | Aggregator uses exact source precision; evaluate unchanged best checkpoints on all 120 cases |
| Allen positional/placement controls | [factor seeds](../results/camera_ready/factor-seeds.csv) | Three matched seeds; no reliable fixed-layout winner |
| MSD Heart/Spleen 262k | [medical seeds](../results/camera_ready/medical-seeds.csv) | Independent depth-one training, foreground-centered crops, not zero-shot/full-volume transfer |
| Six-seed U-Net comparison | [U-Net seeds](../results/camera_ready/unet-seeds.csv), [structures](../results/camera_ready/structure-results.csv) | Frozen architecture-control evidence; U-Net training not ported |
| Historical systems allocation | [memory table](../results/camera_ready/system-memory.csv) | Historical backend, not new streamed measurements |
| Auxiliary controls | [thresholds](../results/camera_ready/threshold-controls.csv), [Allen-6 interventions](../results/camera_ready/allen6-interventions.csv), [nodule controls](../results/camera_ready/nodule-controls.csv) | Separate data/model contracts; do not relabel as Allen-15 |

Most camera-ready CSVs are presentation exports rounded to their printed
precision. Do not use them to reconstruct more precise p-values than their source
rows permit. The exact repacking CSV is separately preserved and hashed.

The [config manifest](../reproduce/config_manifest.json) maps 45 portable recipes
to their original run IDs and source hashes. Only operational names, data-root
arguments, tracking metadata, and obsolete launcher/status labels were changed;
model/training fields were retained.
[source_manifest.json](../reproduce/source_manifest.json) records extraction
provenance. A source hash identifies a version; it does not certify behavior.

## Important experimental boundaries

Best means the original-layout validation-selected checkpoint; it is not an
independent test score. Paired comparisons use seeds, not voxels, as the sampling
units. All 120 Allen-15 validation cases were used for its layout interventions.
MSD medical evaluations use foreground-centered crops selected with labels.
Allen target fluorescence is an input and its masks are automatically generated.

Pure repacking transports both summary stages and is theorem-aligned. A named
raster/native switch changes the partition and is evaluated separately. The
evaluation CLI makes these interventions mutually exclusive. Repeat the baseline
evaluation with the same checkpoint and protocol before computing a change.
