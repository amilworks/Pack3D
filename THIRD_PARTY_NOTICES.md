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

| Files | License | License text |
| :--- | :--- | :--- |
| Inter and DM Mono fonts (`website/fonts/`) | SIL Open Font License 1.1 | `website/fonts/OFL-Inter.txt`, `website/fonts/OFL-DM-Mono.txt` |
| d3 7.8.5 (`website/d3.min.js`) | ISC | `website/d3-LICENSE.txt` |

The equations on the website were rendered to SVG ahead of time with MathJax 3.2.2, which is
released under the Apache License 2.0. Figure 1 is the authors' own figure from the paper.

## Data

No dataset is included, and this repository grants no dataset license. Obtain each dataset from its
provider, under its own terms. As the paper's appendix on data access states:

- The Allen Institute for Cell Science WTC-11 hiPSC Single-Cell Image Dataset v1 comes from the
  Allen Cell Explorer, under the [Allen Institute's terms of use](https://www.allencell.org/terms-of-use.html).
- The Medical Segmentation Decathlon's Heart and Spleen descriptors specify CC BY-SA 4.0.
- NoduleMNIST3D, from MedMNIST, is distributed under CC BY 4.0. The paper uses it only for an
  auxiliary control.

This notice is an inventory, not legal advice, and it does not replace the upstream licenses.
