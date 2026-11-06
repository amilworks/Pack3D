import pytest
import torch

from pack3d import build_layout


@pytest.mark.parametrize("layout", ["raster_block", "native_block_morton"])
def test_geometry_matches_paper(layout):
    from hypernsa.attention.layout import make_block_layout, build_local_neighbors
    new = build_layout((4, 4, 8), (1, 2, 2), pool_size=4, layout=layout)
    old = make_block_layout((4, 4, 8), (1, 2, 2), layout=layout)
    nb, valid = build_local_neighbors(old["coords_packed"], old["valid_token_mask"], 1,
                                      old["coord_to_packed_idx"])
    torch.testing.assert_close(new.order, old["packed_order"])
    torch.testing.assert_close(new.coords.float(), old["coords_packed"])
    torch.testing.assert_close(new.geometry.neighbors.long(), nb.masked_fill(~valid, -1))
    torch.testing.assert_close(new.geometry.blocks.long(), old["block_token_indices"])


def test_pack_roundtrip_and_transport():
    layout = build_layout((4, 4, 8), pool_size=2)
    grid = torch.randn(2, 4, 4, 8, 3)
    torch.testing.assert_close(layout.unpack(layout.pack(grid)), grid)
    p = torch.randperm(128)
    new = layout.repack(p)
    torch.testing.assert_close(new.pack(grid), layout.pack(grid)[:, p])
    torch.testing.assert_close(new.unpack(new.pack(grid)), grid)
    torch.testing.assert_close(new.coords[new.geometry.blocks.long()],
                               layout.coords[layout.geometry.blocks.long()])


@pytest.mark.parametrize("kwargs", [{"grid_shape": (3, 4, 4)}, {"radius": -1},
                                    {"block_shape": (0, 2, 2)}, {"layout": "unknown"},
                                    {"pool_size": True}, {"radius": 3}])
def test_bad_layout_rejected(kwargs):
    args = {"grid_shape": (4, 4, 4), **kwargs}
    with pytest.raises(ValueError):
        build_layout(**args)


def test_mutation_and_nonpermutation_fail():
    layout = build_layout((2, 2, 2))
    with pytest.raises(ValueError, match="permutation"):
        layout.repack(torch.zeros(8, dtype=torch.int64))
    layout.coords[0, 0] += 1
    with pytest.raises(RuntimeError, match="changed"):
        layout.pack(torch.zeros(1, 2, 2, 2, 1))


def test_named_layout_changes_partition():
    raster = build_layout((4, 4, 8), (1, 2, 2), layout="raster_block")
    native = build_layout((4, 4, 8), (1, 2, 2))
    def supports(x):
        return {frozenset(x.order[block.long()].tolist()) for block in x.geometry.blocks}
    assert supports(raster) != supports(native)
