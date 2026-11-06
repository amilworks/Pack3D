import torch
from pack3d import PACK3DAttention, build_layout


def test_full_layer_repacking_outputs_and_all_parameter_gradients():
    torch.manual_seed(21)
    layout = build_layout((4, 4, 4), pool_size=2)
    p = torch.randperm(64)
    other = layout.repack(p)
    layer = PACK3DAttention(16, heads=2, kv_heads=1, head_dim=16).double()
    x = torch.randn(1, 64, 16, dtype=torch.float64, requires_grad=True)
    xp = x.detach()[:, p].clone().requires_grad_()
    y, yp = layer(x, layout), layer(xp, other)
    torch.testing.assert_close(y, yp[:, p.argsort()], atol=1e-10, rtol=1e-10)
    dy = torch.randn_like(y)
    gs = torch.autograd.grad(y, (x, *layer.parameters()), dy)
    gps = torch.autograd.grad(yp, (xp, *layer.parameters()), dy[:, p])
    torch.testing.assert_close(gs[0], gps[0][:, p.argsort()], atol=1e-10, rtol=1e-10)
    for a, b in zip(gs[1:], gps[1:]):
        torch.testing.assert_close(a, b, atol=1e-10, rtol=1e-10)
    layer.position_encoding = "packed"
    packed, packed_p = layer(x, layout), layer(xp, other)
    assert (packed - packed_p[:, p.argsort()]).abs().max() > 1e-4
