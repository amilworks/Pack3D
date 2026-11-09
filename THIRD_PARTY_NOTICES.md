# Third-party notices

PACK3D is released under the [MIT License](LICENSE). This file lists the software and data it
depends on but does not include, and the third-party files it does include.

## Code

The package and scripts were extracted from the authors' research implementation. The source
inventory is in [reproduce/source_manifest.json](reproduce/source_manifest.json). The historical
package name, `hypernsa`, is kept under `reproduce/paper_backend/` only so that the paper's recipes
and checkpoints keep working.

PyTorch (BSD-style license) and Triton (MIT) are external dependencies; neither is vendored. MONAI
(Apache-2.0), NumPy, SciPy, NiBabel, tifffile, imagecodecs, and PyYAML are optional dependencies of
the reproduction scripts. Each keeps its own license. The GitHub Actions used by the workflows are
external and pinned to commit hashes.

## Website

The project website in [website/](website/) includes these third-party files, each with its license:

| Files | What they are | License | License text |
| :--- | :--- | :--- | :--- |
| `website/fonts/inter-latin-standard-normal.woff2`, `website/fonts/inter-latin-standard-italic.woff2` | Inter 4.001, upright and italic, variable in weight and optical size, Latin subset. Copyright 2016 The Inter Project Authors | SIL Open Font License 1.1 | `website/fonts/OFL-Inter.txt` |
| `website/fonts/dm-mono-latin-400-normal.woff2` | DM Mono 1.000 Regular, Latin subset. Copyright 2020 The DM Mono Project Authors | SIL Open Font License 1.1 | `website/fonts/OFL-DM-Mono.txt` |
| `website/d3.min.js` | A partial build of d3 7.8.5 (<https://d3js.org>): d3-array 3.2.4, d3-axis 3.0.0, d3-color 3.1.0, d3-dispatch 3.0.1, d3-drag 3.0.0, d3-ease 3.0.1, d3-format 3.1.0, d3-interpolate 3.0.1, d3-path 3.1.0, d3-scale 4.0.2, d3-selection 3.0.0, d3-shape 3.2.0, d3-time 3.1.0, d3-time-format 4.1.0, d3-timer 3.0.1, d3-transition 3.0.1 and internmap 2.0.3. Copyright Mike Bostock, with each module's years in the license text | ISC; d3-ease is also under the BSD 3-Clause License, for Robert Penner's easing equations (Copyright 2001 Robert Penner) | `website/d3-LICENSE.txt` |

[tools/d3](tools/d3/) builds `website/d3.min.js` and writes `website/d3-LICENSE.txt` from each
module's own license. To build, it installs those modules and esbuild (MIT) from npm at the versions
pinned in its `package-lock.json`; none of them is kept in the repository.

The equations on the website were rendered to SVG ahead of time with MathJax 3.2.2, which is
released under the Apache License 2.0. Figure 1, in every form the website carries it, is the authors'
own figure from the paper.

## Data

No dataset is included, and this repository grants no dataset license. Obtain each dataset from its
provider, under its own terms. As the paper's appendix on data access states:

- The Allen Institute for Cell Science WTC-11 hiPSC Single-Cell Image Dataset v1 comes from the
  Allen Cell Explorer, under the [Allen Institute's terms of use](https://www.allencell.org/terms-of-use.html).
- The Medical Segmentation Decathlon's Heart and Spleen descriptors specify CC BY-SA 4.0.
- NoduleMNIST3D, from MedMNIST, is distributed under CC BY 4.0. The paper uses it only for an
  auxiliary control.

This notice is an inventory, not legal advice, and it does not replace the upstream licenses.
