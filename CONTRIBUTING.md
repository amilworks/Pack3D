# Contributing to PACK3D

Thank you for your interest in PACK3D. Bug reports, questions, and pull requests are all welcome.

## Report a bug or ask a question

Open a [GitHub issue](https://github.com/amilworks/Pack3D/issues). For a bug, include:

- your Python, PyTorch and Triton versions, and your GPU if you use one;
- the backend (`reference` or `triton`);
- a minimal reproduction with synthetic tensors: shapes, dtype, and the layout you built.

Please don't attach datasets, checkpoints, credentials, or private file paths.

## Set up a development environment

Install the [PyTorch build for your machine](https://pytorch.org/get-started/locally/) first. Then,
from the repository root:

```bash
pip install -e ".[dev,reproduce]" -c reproduce/constraints-tested.txt
```

The constraints file pins the versions the paper's reproduction runs were validated with. It needs
Python 3.12 or newer; on Python 3.11, leave out `-c reproduce/constraints-tested.txt`.

## Run the checks

These are the checks that continuous integration runs, on Python 3.11, 3.12 and 3.13:

```bash
ruff check src tests examples reproduce/*.py reproduce/data benchmarks tools
python -m pytest -q
python examples/minimal_attention.py
python examples/repacking_equivariance.py
python examples/repack_test.py
python reproduce/aggregate.py
python tools/check_release.py
python -m build && python -m twine check --strict dist/*
```

`tools/check_release.py` checks local links and their anchors, YAML files, pinned GitHub Actions,
the website workflow, the checksums of the frozen results and paper recipes, and that the version
agrees across the package, `CITATION.cff` and `CHANGELOG.md`.

### GPU tests

GPU tests are opt-in, and they are skipped on CPU. To run them, install `.[triton]`, pick one GPU
that you are allowed to use, and set:

```bash
CUDA_VISIBLE_DEVICES=0 PACK3D_TEST_CUDA=1 python -m pytest tests/test_triton.py -q
```

The device index is only an example. The tests cap the PyTorch allocator at 4 GiB. Check free memory
first, and do not run them on a shared GPU without its owner's permission. CPU-only CI does not
validate the GPU implementation.

## Guidelines for changes

- **Keep the math and its execution apart.** A change to the operator itself should not be mixed
  with a change to how a backend executes it.
- **Test numerical changes.** A change that can alter numbers needs a regression test that compares
  outputs and gradients, including the relevant masking and dtype cases.
- **Preserve the layout contract.** Coordinates, neighborhoods, summary memberships, and
  within-block slots travel with the tokens. [docs/code_guide.md](docs/code_guide.md) maps each
  piece to its code.
- **Leave frozen material alone.** Do not edit the files under `results/` or
  `reproduce/paper_backend/`, or the recipes in `reproduce/configs/`. They are checksummed, and
  `tools/check_release.py` fails if they change.
- **Say when results could move.** If a change could affect a reported number, say so in the pull
  request.

## Make a release (maintainers)

1. Set the new version in `src/pack3d/__init__.py` (`__version__`) and `CITATION.cff` (`version`), and
   add a section for it to `CHANGELOG.md`. `tools/check_release.py` fails if the three disagree.
2. Merge to `main` and wait for the tests to pass.
3. Tag the merge commit `vX.Y.Z` and publish a GitHub release with the changelog section as its notes.

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
