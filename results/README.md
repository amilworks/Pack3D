# Included result data

This directory includes frozen camera-ready metric exports and exact per-seed
repacking rows. The repository also includes principal training/evaluation
entry points, but no datasets or pretrained checkpoints. No principal training
or checkpoint inference was rerun during release extraction.

## Allen-15 pure repacking

File: [allen15_repacking/seed_metrics.csv](allen15_repacking/seed_metrics.csv).

Each row contains the seed, positional encoding, original-layout validation
macro Dice, repacked validation macro Dice, and `delta = repacked - original`.
The README averages the six rows for each encoding, then rounds to four decimal
places. The six matched seeds are 13, 29, 41, 53, 67, and 83.

The models use 262,144 tokens and a depth-8 backbone. Checkpoints were selected by
validation Dice on the original layout and evaluated unchanged on all 120
validation cases under both layouts. The pure repack preserves coordinates,
local neighborhoods, both stages of summary membership, and slot identities.
It is not the partition-changing raster-to-block-Morton experiment.

Allen-15 is fluorescence-assisted segmentation of Allen-generated masks. The
target fluorescence channel is an input. These numbers should not be presented
as label-free prediction, a held-out test result, or a general segmentation
leaderboard comparison. Reusing the validation population for checkpoint
selection also limits its interpretation as independent generalization evidence.

The file was copied byte-for-byte from the frozen camera-ready figure data.
Its SHA-256 is:

```text
09eabdcda4a3b9b14504f67db3345237a72ee33c7d65133cd8c3c771d6e56bb6
```

Run `python reproduce/aggregate.py` from the repository root to regenerate the
six-seed means and exact paired sign-flip result. Other CSVs are cataloged in
[manifest.json](manifest.json) and the [reproducibility map](../docs/reproducibility.md).
Some presentation exports are rounded; do not infer additional numerical precision.
