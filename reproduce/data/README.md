# Data contract

Raw datasets and prepared crops are not bundled. Obtain each dataset under its
original access and redistribution terms. This release provides the original
crop loaders and portable training/evaluation entry points, not a new claim that
raw-data preprocessing can be reconstructed without the source manifests.

Supply a JSON manifest and an explicit data root. Paths may be relative to that
root or absolute within it. Every path must exist. Duplicate paths, cross-split
path overlap, and paths escaping the root are rejected. Audit source-case/FOV
identities separately: distinct filenames do not prove independent subjects.

## Crop files

Use NumPy `.npz` archives with numeric arrays, no pickled objects:

- `image`: float32 `[channels,Z,Y,X]`.
- `label`: integer `[Z,Y,X]`, with binary class IDs for the principal tasks.

MSD and single-structure Allen manifests list paths in `preprocessed`:

```json
{
  "task": "msd_heart",
  "num_classes": 2,
  "preprocessed": {
    "train": ["train/case_a_crop0.npz"],
    "val": ["val/case_b_crop0.npz"]
  }
}
```

Multi-structure Allen uses `multistructure: true`, `structure_names`,
`num_structures`, and `samples` lists. Each sample has `path`, `structure_name`,
and `structure_id` matching the ordered names. Preserve the channel semantics
and `channel_set` metadata expected by the selected recipe, including
`structure_bf_dna` for the principal fluorescence-assisted input.

## Match the paper protocol

Allen-15 uses raw crop shape `32 x 512 x 256`, patch shape `1 x 4 x 4`, and full
`32 x 128 x 64` token-grid supervision. Keep FOV splits and structure IDs fixed.
Target fluorescence, brightfield, and DNA are inputs; no target mask or
segmentation-derived image channel is an input.

The high-token MSD studies use isotropically resampled `64^3` crops with unit
patches: Heart at 1.25 mm and Spleen at 1.5 mm. Source-case splits are separate.
Training uses four crops per case and validation two. Validation crops are
foreground-centered using the labels. These are not whole-volume challenge
scores or deployment localization tests. Changing crop selection, orientation,
resampling, or normalization changes the experiment.

Exact raw-data manifests and their redistribution review remain separate from
this release. Do not claim an exact data reproduction from the illustrative
manifest above. `make_smoke_data.py` exists only to test the I/O pipeline without
real data.
