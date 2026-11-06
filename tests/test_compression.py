import torch
from pack3d import build_layout
from pack3d.compression import compress_summaries
from pack3d.rope import axial_rope


def test_relative_summary_identity_with_learned_weights():
    torch.manual_seed(4)
    layout = build_layout((2, 2, 4), pool_size=2)
    q, k, v = torch.randn(3, 1, 1, 16, 16, dtype=torch.float64)
    w, bias = torch.randn(16, dtype=torch.float64), torch.randn(8, dtype=torch.float64)
    rotated = axial_rope(k, layout.coords)
    sk, _ = compress_summaries(rotated, v, w, bias, layout.geometry, temperature=.7)
    index = layout.geometry.blocks.long()
    a = ((rotated[:, :, index] * w).sum(-1) / .7 + bias).softmax(-1)
    effective = a.flatten(-2) / 2
    for i in (0, 7, 15):
        relative = axial_rope(k, layout.coords - layout.coords[i])
        rhs = ((q[:, :, i, None] * relative).sum(-1) * effective).sum(-1)
        lhs = (axial_rope(q, layout.coords)[:, :, i] * sk[:, :, 0]).sum(-1)
        torch.testing.assert_close(lhs, rhs, atol=1e-12, rtol=1e-12)


def test_common_summary_permutation_is_noop():
    q, k, v = torch.randn(3, 1, 2, 5, 16)
    p = torch.randperm(5)
    reference = (q @ k.transpose(-1, -2)).softmax(-1) @ v
    changed = (q @ k[:, :, p].transpose(-1, -2)).softmax(-1) @ v[:, :, p]
    torch.testing.assert_close(reference, changed)
