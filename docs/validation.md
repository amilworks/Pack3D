# Release validation

Date: 2026-11-06. These are release-engineering and numerical checks, not new
segmentation experiments. The original research files and frozen metric rows
were not overwritten. No principal model was retrained for this extraction.

## Review iterations

1. **Organization and scientific contract.** Separate the readable operator,
   optional kernels, and checkpoint-compatible historical backend. Check the
   relative-logit identity, two-stage compression, canonical slot transport,
   principal branch mixer, and the corrected fixed-layout claim boundaries.
2. **Numerical behavior.** Compare outputs and all supported gradients against
   the differentiable reference. Check packing transport, masking, odd lengths,
   grouped heads, finite extreme logits, singleton summaries, and optimizer steps.
3. **Reproduction and safety.** Run an offline synthetic training/evaluation
   cycle. Reject output collisions and crop-path split overlap. Restrict tensor
   loading and archive extraction; remove host identifiers. Fix undefined optional
   diagnostics to serialize as `null`, while invalid task metrics still fail.
4. **Standalone distribution.** Install a built wheel outside the checkout in
   a fresh CPU-only environment, run the tests from an isolated source copy,
   include reproduction/docs in the source distribution, and check local links,
   pinned Actions, the Pages workflow, source/config hashes, and frozen evidence.

These were successive review passes during extraction, not independent external
reviews or a comprehensive security certification.

## Public release checks

These checks were run on the public release, 0.1.0, after the repository was prepared for GitHub
(license, packaging metadata, documentation, website, and workflows). All runs are CPU-only; the GPU
rows in the next section were not repeated.

| Environment | Outcome |
| --- | --- |
| Python 3.11.18, PyTorch 2.11.0, newest optional dependencies (no constraints) | 37 passed; 31 GPU tests skipped |
| Python 3.12.3, PyTorch 2.11.0, [tested constraints](../reproduce/constraints-tested.txt) | 37 passed; 31 GPU tests skipped |
| Python 3.13.18, PyTorch 2.15.0, newest optional dependencies | 37 passed; 31 GPU tests skipped |
| Built wheel, imported outside the checkout; tests run from the unpacked source distribution | 36 passed; 32 skipped (31 GPU tests and the website check, since `website/` is not in the source distribution) |

In every environment, the three examples, `reproduce/aggregate.py` (six-seed means; sign-flip
p = 0.03125), `tools/check_release.py` and Ruff passed. `python -m build` and
`twine check --strict` passed for the wheel and the source distribution (metadata 2.4, license
expression `MIT`). actionlint 1.7.12 found no problems in the workflows, and `check-jsonschema`
validated the workflows, the Dependabot configuration, the issue forms and `CITATION.cff` against
their published schemas. The release adds one test, for the website folder, so the suite now has 68
distinct test cases. GitHub-hosted runs of the workflows happen once the repository is pushed.

## Executed numerical checks (extraction)

| Check | Outcome |
| --- | --- |
| CPU suite, development environment | 36 passed; 31 GPU tests explicitly skipped |
| CPU-only PyTorch wheel, isolated source copy | 36 passed; 31 GPU tests explicitly skipped |
| Opt-in H200 suite | 33 passed, including two CPU guard/reference checks |
| H200 suite under CUDA memcheck | 33 passed; zero reported memory errors |
| Dataset-free repacking example | Aligned output max error 0; input-gradient max error 8.88e-16 |
| Synthetic two-step training, checkpoint evaluation, repacking, collision refusal | Passed as part of CPU suite |
| Historical layer with requested local Triton execution | Runtime backend attested; finite backward |
| Historical corrected packed-RoPE control | All rotary pairs active on sequence position; nonzero transform |
| Tiny CPU and H200 BF16 benchmark harnesses | Correctness gates and forward/backward timing completed |

The paper's Appendix D.4 reports 30 GPU correctness tests, the same tests under CUDA memcheck, and
19 CPU regression tests, as counted when the paper was written; the rows above are pytest's counts
for this repository's suite. The extraction's suite had 67 distinct test cases; the CPU and GPU rows
overlap. A skip is not
a pass. GPU numerical checks include FP32, FP16, BF16, and BF16 autocast against
the historical layer. The main core gradient tests use relative-L2 tolerances
of 3e-5, 0.005, and 0.035, respectively, with separate absolute/relative checks
for selected edge cases. Low-precision equivalence is not bitwise equality.

The wheel imports from `site-packages` without either Triton or the original
research package installed. The CPU source-copy suite imports only the bounded
historical snapshot when testing checkpoint compatibility.

## Environment

- Linux, Python 3.12.3.
- Development GPU: NVIDIA H200, PyTorch 2.11.0+cu126, Triton 3.6.0.
- Clean CPU environment: PyTorch 2.11.0+cpu, no Triton installation.
- Optional reproduction dependencies: [tested constraints](../reproduce/constraints-tested.txt).
- Tests used an authorized shared GPU with a 4 GiB allocator cap. No exclusive
  device timing was performed. The tiny benchmark checks validate the harness,
  not high-token performance or paper speedups.

## Repeat the checks

```bash
python -m pip install -e '.[dev,reproduce]' -c reproduce/constraints-tested.txt   # Python 3.12+
python -m pytest -q
python examples/minimal_attention.py
python examples/repacking_equivariance.py
python examples/repack_test.py
python reproduce/aggregate.py
python tools/check_release.py
python -m build
python -m twine check --strict dist/*
```

On Python 3.11, leave out `-c reproduce/constraints-tested.txt`.

After installing a compatible CUDA PyTorch wheel and `.[triton]`, select an
authorized GPU explicitly:

```bash
CUDA_VISIBLE_DEVICES=1 PACK3D_TEST_CUDA=1 python -m pytest tests/test_triton.py -q
CUDA_VISIBLE_DEVICES=1 PACK3D_TEST_CUDA=1 compute-sanitizer --tool memcheck --error-exitcode 99 python -m pytest tests/test_triton.py -q
```

The device index is an example, not permission to use that device. Check free
memory and authorization first.

## Not established by this release

- Recovery of the published training scores from raw downloaded datasets.
- Principal-scale training with the new streamed backend, or equivalence of
  complete training trajectories across backends.
- Publication-quality timing on an exclusive GPU, performance on other GPU
  families, distributed training, or higher-order Triton derivatives.
- Runs of the GitHub-hosted workflows (tests and website deployment), or a GitHub
  or PyPI release. These happen once the repository is pushed.
- A complete third-party ownership or security audit.

See [backend limits](backends.md), [reproduction coverage](reproducibility.md),
and [third-party notices](../THIRD_PARTY_NOTICES.md) before distributing or using
the snapshot as a full paper-reproduction package.
