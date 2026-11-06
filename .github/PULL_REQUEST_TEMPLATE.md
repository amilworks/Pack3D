## What this changes

<!-- One or two sentences. Link the issue it closes, if there is one. -->

## Could it change a reported number?

<!-- No, or which number and why. -->

## Checklist

- [ ] `ruff check src tests examples reproduce/*.py reproduce/data benchmarks tools` passes.
- [ ] `python -m pytest -q` passes.
- [ ] `python tools/check_release.py` passes.
- [ ] A change that can alter numbers comes with a test that compares outputs and gradients.
- [ ] Files under `results/`, `reproduce/paper_backend/` and `reproduce/configs/` are unchanged.
- [ ] GPU changes only: `PACK3D_TEST_CUDA=1 python -m pytest tests/test_triton.py -q` passes. GPU used:
