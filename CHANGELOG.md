# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-06

First public release, accompanying the NeurIPS 2026 paper
[Geometry Matters in Packed 3D Attention](https://arxiv.org/abs/2610.38694).

### Added

- The `pack3d` package: explicit 3D geometry (`build_layout`, `TokenLayout.repack`), axial RoPE,
  learned two-stage compression, a differentiable reference implementation, and the
  `PACK3DAttention` layer.
- An optional streamed Triton backend with an explicit backward pass (`backend="triton"`).
- CPU examples for a forward and backward pass, packing equivariance, and the repack test.
- The paper's 45 recipes for Allen-15, MSD Heart and MSD Spleen, with offline training and
  checkpoint evaluation through the paper backend.
- Frozen per-seed and camera-ready results, with checksums and a dataset-free aggregator.
- Safety checks in the reproduction scripts: tensor-only checkpoint loading, restricted archive
  extraction, refusal to overwrite outputs, and strict JSON for evaluation metrics.
- The project website under `website/`, deployed with GitHub Pages.
- The MIT license, citation metadata, contribution guide, issue and pull request templates,
  continuous integration, and Dependabot updates for the pinned GitHub Actions.

### Notes

- The new API does not use the state-dict names of the paper's historical layer. To load the
  paper's checkpoints, use the paper backend in `reproduce/`.
- Scientific corrections made after review are listed in
  [docs/corrections.md](docs/corrections.md).

[0.1.0]: https://github.com/amilworks/Pack3D/releases/tag/v0.1.0
