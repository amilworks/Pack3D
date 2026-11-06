# Examples

Each example runs on a CPU in a few seconds, needs no dataset or checkpoint, and checks its own
result. Run them from the repository root after `pip install -e .`.

| Example | What it shows |
| :--- | :--- |
| [minimal_attention.py](minimal_attention.py) | Pack a 4 × 4 × 4 field, run one PACK3D layer forward and backward, and unpack the output. |
| [repacking_equivariance.py](repacking_equivariance.py) | Repack the tokens and carry the layout with them: outputs and gradients stay the same, in spatial order, to float64 precision. |
| [repack_test.py](repack_test.py) | The paper's repack test on one layer. With RoPE at token coordinates, as in PACK3D, the output does not change; with RoPE at sequence index, it does. |

What you should see:

```text
$ python examples/minimal_attention.py
Output (1, 4, 4, 4, 32); input gradients finite; backend=reference

$ python examples/repacking_equivariance.py
Aligned output max error: 0
Aligned gradient max error: 8.88e-16

$ python examples/repack_test.py
RoPE at coordinates (PACK3D)  largest output change after repacking: 0.0e+00
RoPE at sequence index        largest output change after repacking: 1.7e-01
```

The last digits of the gradient error can differ across machines and PyTorch versions; anything near
1e-15 is floating-point rounding. [docs/method.md](../docs/method.md#repack-without-changing-the-operator)
explains what a repack carries and why the test works.
