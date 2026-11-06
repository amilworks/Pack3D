"""The repack test: change only the memory order of the tokens and compare outputs.

A pure repack moves tokens to new memory positions and carries their coordinates,
neighborhoods, summary memberships and within-block slots along. The field itself
is unchanged. A layer that reads position from coordinates gives the same outputs,
up to floating-point rounding. The same layer reading position from the packed
sequence index does not.

Runs on CPU in about a second; no dataset or checkpoint needed.
"""
import torch

from pack3d import PACK3DAttention, build_layout


def largest_change(layer, x, layout, permutation):
    """Run the layer on the original and the repacked field; compare in spatial order."""
    repacked = layout.repack(permutation)  # new row i is old row permutation[i]
    before = layer(x, layout)
    after = layer(x[:, permutation], repacked)[:, permutation.argsort()]
    return (before - after).abs().max().item()


def main():
    torch.manual_seed(0)
    layout = build_layout((8, 8, 8), block_shape=(2, 2, 2), pool_size=4)
    n = layout.geometry.num_tokens
    x = torch.randn(1, n, 32, dtype=torch.float64)
    permutation = torch.randperm(n)

    # One set of weights; only the source of position changes between the two runs.
    layer = PACK3DAttention(32, heads=2, kv_heads=1, head_dim=16).double()
    changes = {}
    for encoding, label in (("axial", "coordinates (PACK3D)"), ("packed", "sequence index")):
        layer.position_encoding = encoding
        changes[encoding] = largest_change(layer, x, layout, permutation)
        print(f"RoPE at {label:<20}  largest output change after repacking: {changes[encoding]:.1e}")

    assert changes["axial"] < 1e-10, "RoPE at coordinates should not see a pure repack"
    assert changes["packed"] > 1e-3, "RoPE at the sequence index should see the repack"


if __name__ == "__main__":
    main()
