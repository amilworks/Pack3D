"""Pure storage repacking preserves the graph and both summary memberships."""
import torch
from pack3d import PACK3DAttention, build_layout


def main():
    torch.manual_seed(11)
    layout = build_layout((4, 4, 4), pool_size=2)
    permutation = torch.randperm(64)
    changed = layout.repack(permutation)
    model = PACK3DAttention(32, heads=2, kv_heads=1, head_dim=16).double()
    x = torch.randn(1, 64, 32, dtype=torch.float64, requires_grad=True)
    xp = x.detach()[:, permutation].clone().requires_grad_()
    y, yp = model(x, layout), model(xp, changed)
    inverse = permutation.argsort()
    torch.testing.assert_close(y, yp[:, inverse], rtol=1e-10, atol=1e-10)
    g = torch.autograd.grad(y.square().sum(), x)[0]
    gp = torch.autograd.grad(yp.square().sum(), xp)[0]
    torch.testing.assert_close(g, gp[:, inverse], rtol=1e-10, atol=1e-10)
    print(f"Aligned output max error: {(y - yp[:, inverse]).abs().max().item():.3g}")
    print(f"Aligned gradient max error: {(g - gp[:, inverse]).abs().max().item():.3g}")


if __name__ == "__main__":
    main()
