"""Run from the repository root after installing PACK3D. No dataset needed."""
import torch
from pack3d import PACK3DAttention, build_layout


def main():
    torch.manual_seed(7)
    layout = build_layout((4, 4, 4), block_shape=(2, 2, 2), pool_size=2)
    layer = PACK3DAttention(dim=32, heads=2, kv_heads=1, head_dim=16)
    field = torch.randn(1, 4, 4, 4, 32, requires_grad=True)
    output = layout.unpack(layer(layout.pack(field), layout))
    output.square().mean().backward()
    assert output.shape == field.shape and torch.isfinite(field.grad).all()
    print(f"Output {tuple(output.shape)}; input gradients finite; backend={layer.backend}")


if __name__ == "__main__":
    main()
