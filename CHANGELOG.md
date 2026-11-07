# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- The website tells its story in three full-screen figures. It opens on the storage orders drawn as
  paths: one glowing path through 512 tokens, morphing through raster, Morton, Hilbert, blocks and a
  repack. The paper's first screen threads the letters of the title to their places in memory. In the
  result chapter, the same repack runs on a cell under both models, with one spark for each changed
  prediction at the paper's rates; it replaces the two flat squares that showed those counts.
- The website's top bar is a breadcrumb, the wordmark and the chapter being read, which opens the
  contents on hover, a click, a tap or the keyboard. Buttons, option trays, figure sheets, stats,
  cards and callouts follow one design system, written up in
  [docs/design-system.md](docs/design-system.md).
- The website's link-preview card shows the closing word, PACK3D built from cubes on the dark stage,
  under the paper's title. [tools/social_card.html](tools/social_card.html) draws it.

### Fixed

- Figure labels on the website no longer set variables in capitals, where the variable *z* read as *Z*.
- The website works with touch on phones and tablets. The query and key tokens in the rotary-dials
  demo can be dragged with a finger, every chart opens its tooltip on a tap (the nearest mark within
  reach, outlined while its tip is up), a tap on the token field names the token, the closing word
  can be tapped or scrubbed with a finger, and hover styles no longer stick after a tap.

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
