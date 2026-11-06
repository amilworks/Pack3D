import subprocess
import sys

import pytest
import torch
from pack3d import PACK3DAttention, build_layout


def test_layer_gradients_and_shapes():
    torch.manual_seed(12)
    layout = build_layout((2, 2, 4), pool_size=1)
    layer = PACK3DAttention(16, heads=2, kv_heads=1, head_dim=16).double()
    x = torch.randn(1, 16, 16, dtype=torch.float64, requires_grad=True)
    y = layer(x, layout)
    assert y.shape == x.shape
    y.square().sum().backward()
    assert torch.isfinite(x.grad).all()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in layer.parameters())


def test_cpu_import_does_not_import_triton_or_paper_package():
    code = "import sys,pack3d; assert 'triton' not in sys.modules; assert 'hypernsa' not in sys.modules"
    subprocess.run([sys.executable, "-c", code], check=True, cwd="/tmp")


def test_explicit_cuda_request_never_falls_back():
    layout = build_layout((2, 2, 2))
    layer = PACK3DAttention(16, heads=1, kv_heads=1, head_dim=16, backend="triton")
    with pytest.raises(ValueError, match="CUDA"):
        layer(torch.randn(1, 8, 16), layout)


@pytest.mark.parametrize("kwargs", [{"heads": 3}, {"temperature": 0},
                                    {"backend": "auto"}, {"position_encoding": "none"}])
def test_layer_rejects_unsupported(kwargs):
    with pytest.raises(ValueError):
        PACK3DAttention(32, **kwargs)
