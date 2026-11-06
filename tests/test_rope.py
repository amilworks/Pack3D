import pytest
import torch
from pack3d.rope import axial_rope, balanced_pairs


def test_balanced_allocation():
    assert balanced_pairs(64) == (11, 11, 10)


def test_relative_identity_and_nonzero_rotation():
    torch.manual_seed(3)
    q, k = torch.randn(2, 1, 1, 7, 16, dtype=torch.float64)
    c, d = torch.randn(2, 7, 3, dtype=torch.float64)
    qr, kr = axial_rope(q, c), axial_rope(k, d)
    assert (qr - q).abs().max() > 0.01
    torch.testing.assert_close((qr * kr).sum(-1), (q * axial_rope(k, d - c)).sum(-1),
                               atol=1e-12, rtol=1e-12)
    torch.testing.assert_close(q.square().sum(-1), qr.square().sum(-1), atol=1e-12, rtol=1e-12)


@pytest.mark.parametrize("pairs", [(0, 0, 0), (8, 0, -1), (3, 3, 3), (True, 3, 4)])
def test_inactive_or_invalid_pairs_rejected(pairs):
    with pytest.raises(ValueError):
        axial_rope(torch.randn(1, 1, 4, 16), torch.zeros(4, 3), pairs=pairs)


def test_nonfinite_coordinates_rejected():
    with pytest.raises(ValueError, match="finite"):
        axial_rope(torch.ones(1, 1, 1, 16), torch.full((1, 3), float("nan")))
