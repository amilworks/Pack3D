"""Validated coordinate graph and summary membership metadata."""
from dataclasses import InitVar, dataclass, field
import math
import torch
from torch import Tensor
from itertools import product

_VALIDATED_GEOMETRY = object()

@dataclass(frozen=True)
class Pack3DGeometry:
    neighbors: Tensor
    reverse_neighbors: Tensor
    blocks: Tensor
    pool_size: int
    num_tokens: int
    _seal: InitVar[object] = None
    _versions: tuple[int, ...] = field(init=False, repr=False)

    def __post_init__(self, _seal):
        if _seal is not _VALIDATED_GEOMETRY:
            raise ValueError("Use prepare_geometry() to validate indices before launching CUDA")
        object.__setattr__(self, "_versions", tuple(t._version for t in self.tensors))

    @property
    def tensors(self):
        return self.neighbors, self.reverse_neighbors, self.blocks

    @property
    def num_summaries(self):
        return math.ceil(self.blocks.shape[0] / self.pool_size)

    @torch.inference_mode(False)
    def to(self, device):
        self.check_unmodified()
        return Pack3DGeometry(*(t.to(device) for t in self.tensors), self.pool_size,
                              self.num_tokens, _seal=_VALIDATED_GEOMETRY)

    def check_unmodified(self):
        if tuple(t._version for t in self.tensors) != self._versions:
            raise RuntimeError("Geometry changed after validation; prepare it again")


@torch.inference_mode(False)
def prepare_geometry(neighbors: Tensor, blocks: Tensor, pool_size: int) -> Pack3DGeometry:
    """Validate on CPU once; -1 marks padding, not a valid token index.

    Block columns retain canonical slot identity. Consecutive groups of
    ``pool_size`` fine blocks define the second-stage partition. Reverse
    adjacency permits race-free local K/V gradients even for asymmetric graphs.
    """
    for name, value in (("neighbors", neighbors), ("blocks", blocks)):
        if value.ndim != 2 or value.dtype not in (torch.int32, torch.int64):
            raise ValueError(f"{name} must be a rank-two integer tensor")
        if min(value.shape) == 0:
            raise ValueError(f"{name} must be nonempty")
    if type(pool_size) is not int or not 1 <= pool_size <= 32:
        raise ValueError("pool_size must be an integer in [1,32]")
    nb, members = (t.detach().to(device="cpu", dtype=torch.int64).contiguous().clone()
                   for t in (neighbors, blocks))
    n = nb.shape[0]
    if nb.shape[1] > 128 or members.shape[1] > 64:
        raise ValueError("at most 128 neighbors and 64 fine-block slots are supported")
    if max(nb.numel(), members.numel()) >= 2**31:
        raise ValueError("geometry exceeds the 32-bit kernel indexing limit")
    for name, value in (("neighbors", nb), ("blocks", members)):
        if bool(((value < -1) | (value >= n)).any()):
            raise ValueError(f"{name} contains an out-of-range token")
    sorted_nb = nb.sort(dim=1).values
    if bool(((sorted_nb[:, 1:] == sorted_nb[:, :-1]) & (sorted_nb[:, 1:] >= 0)).any()):
        raise ValueError("duplicate local edges are not supported")
    covered = members[members >= 0]
    if not torch.equal(torch.bincount(covered, minlength=n), torch.ones(n, dtype=torch.int64)):
        raise ValueError("fine blocks must partition every token exactly once")
    valid_fine = (members >= 0).any(dim=1)
    for start in range(0, len(members), pool_size):
        if not bool(valid_fine[start:start + pool_size].any()):
            raise ValueError("an entirely empty coarse group is unsupported")
    src = torch.arange(n)[:, None].expand_as(nb)[nb >= 0]
    dst = nb[nb >= 0]
    order = dst.argsort(stable=True)
    src, dst = src[order], dst[order]
    counts = torch.bincount(dst, minlength=n)
    reverse_width = max(1, int(counts.max()))
    if reverse_width > 128:
        raise ValueError("reverse local degree exceeds 128")
    offsets = counts.cumsum(0) - counts
    slots = torch.arange(len(dst)) - offsets[dst]
    reverse = torch.full((n, reverse_width), -1, dtype=torch.int32)
    reverse[dst, slots] = src.to(torch.int32)
    return Pack3DGeometry(nb.to(torch.int32), reverse, members.to(torch.int32), pool_size, n,
                          _seal=_VALIDATED_GEOMETRY)


def _triple(value, name, *, allow_zero=False):
    values = (value,) * 3 if type(value) is int else tuple(value)
    minimum = 0 if allow_zero else 1
    if len(values) != 3 or any(type(v) is not int or v < minimum for v in values):
        raise ValueError(f"{name} must contain three integers >= {minimum}")
    return values


def grid_coordinates(shape):
    """Return CPU int64 coordinates [Z*Y*X, 3] in raster order (z, y, x)."""
    shape = _triple(shape, "shape")
    return torch.stack(torch.meshgrid(*(torch.arange(s) for s in shape), indexing="ij"), -1).reshape(-1, 3)


def _morton_codes(coords):
    bits = int(coords.max()).bit_length()
    if bits > 20:
        raise ValueError("Morton coordinates exceed the supported int64 range")
    code = torch.zeros(len(coords), dtype=torch.int64)
    for bit in range(bits):
        for axis in range(3):
            code |= ((coords[:, axis] >> bit) & 1) << (3 * bit + axis)
    return code


@dataclass(frozen=True)
class TokenLayout:
    """A complete unpadded 3D field, stored in an explicit token order.

    ``order[i]`` is packed token i's raster index; ``coords[i]`` is its
    (z,y,x) coordinate. Fine-block columns encode canonical slot identities.
    Treat all tensors as immutable. Use ``repack`` to transport the graph.
    Geometry is runtime metadata, not part of a learned layer's state dict.
    """

    grid_shape: tuple[int, int, int]
    order: Tensor
    coords: Tensor
    geometry: Pack3DGeometry
    _versions: tuple[int, int] = field(init=False, repr=False)

    def __post_init__(self):
        shape = _triple(self.grid_shape, "grid_shape")
        n = math.prod(shape)
        if self.order.shape != (n,) or self.order.dtype != torch.int64:
            raise ValueError("order must be an int64 permutation of the grid")
        if self.coords.shape != (n, 3) or self.coords.dtype != torch.int64:
            raise ValueError("coords must be int64 [tokens, 3]")
        order = self.order.detach().cpu()
        if not torch.equal(order.sort().values, torch.arange(n)):
            raise ValueError("order must be a permutation")
        if not torch.equal(self.coords.cpu(), grid_coordinates(shape)[order]):
            raise ValueError("coordinates do not agree with order")
        if n != self.geometry.num_tokens or any(t.device != self.order.device for t in
                                                (self.coords, *self.geometry.tensors)):
            raise ValueError("layout and geometry must agree on token count and device")
        object.__setattr__(self, "_versions", (self.order._version, self.coords._version))

    def check_unmodified(self):
        self.geometry.check_unmodified()
        if self._versions != (self.order._version, self.coords._version):
            raise RuntimeError("layout changed in place; construct a new layout")

    @torch.inference_mode(False)
    def to(self, device):
        """Move metadata to a device; does not change coordinates or membership."""
        self.check_unmodified()
        return TokenLayout(self.grid_shape, self.order.to(device), self.coords.to(device),
                           self.geometry.to(device))

    def pack(self, grid):
        """Map [batch,Z,Y,X,channels] to [batch,tokens,channels]."""
        self.check_unmodified()
        if grid.ndim != 5 or tuple(grid.shape[1:4]) != self.grid_shape:
            raise ValueError("input must match [batch,Z,Y,X,channels]")
        return grid.flatten(1, 3).index_select(1, self.order.to(grid.device))

    def unpack(self, packed):
        """Invert pack, aligning outputs to the original raster grid."""
        self.check_unmodified()
        if packed.ndim != 3 or packed.shape[1] != self.geometry.num_tokens:
            raise ValueError("packed input must have shape [batch,tokens,channels]")
        return packed.index_select(1, self.order.argsort().to(packed.device)).reshape(
            packed.shape[0], *self.grid_shape, packed.shape[-1])

    @torch.inference_mode(False)
    def repack(self, permutation):
        """New row i is old row permutation[i]; transport, never rebuild, the graph.

        Fine-block rows and columns and coarse groups retain their identity.
        Only token row indices change. Rebuild via build_layout to deliberately
        change the partition instead.
        """
        self.check_unmodified()
        n = self.geometry.num_tokens
        p = torch.as_tensor(permutation).detach().cpu()
        if p.dtype not in (torch.int32, torch.int64) or p.shape != (n,):
            raise ValueError("permutation must be an integer vector with one entry per token")
        p = p.long()
        if not torch.equal(p.sort().values, torch.arange(n)):
            raise ValueError("permutation must contain every token exactly once")
        inverse = p.argsort()
        nb = self.geometry.neighbors.cpu()[p].long()
        blocks = self.geometry.blocks.cpu().long()
        mapped_nb = torch.where(nb >= 0, inverse[nb.clamp_min(0)], -1)
        mapped_blocks = torch.where(blocks >= 0, inverse[blocks.clamp_min(0)], -1)
        geom = prepare_geometry(mapped_nb, mapped_blocks, self.geometry.pool_size)
        new = TokenLayout(self.grid_shape, self.order.cpu()[p].clone(),
                          self.coords.cpu()[p].clone(), geom)
        return new.to(self.order.device)


@torch.inference_mode(False)
def build_layout(grid_shape, block_shape=(2, 2, 2), *, radius=1, pool_size=4,
                 layout="native_block_morton"):
    """Prepare an unpadded 3D layout on CPU, once, outside attention timing.

    Each grid extent must be divisible by its block extent. Native layout uses
    Morton-ordered blocks and Morton-ordered canonical slots. Raster layout
    groups consecutive raster tokens by block *volume*, not coordinate shape.
    Local neighbors include the query and all valid offsets within radius.
    Arbitrary validated ragged blocks are available through prepare_geometry.
    """
    shape = _triple(grid_shape, "grid_shape")
    block = _triple(block_shape, "block_shape")
    rad = _triple(radius, "radius", allow_zero=True)
    if any(g % b for g, b in zip(shape, block)):
        raise ValueError("build_layout requires an unpadded grid divisible by block_shape")
    if math.prod(block) > 64 or math.prod(2 * r + 1 for r in rad) > 128:
        raise ValueError("layout exceeds supported block or neighborhood width")
    coords = grid_coordinates(shape)
    n = len(coords)
    if layout == "native_block_morton":
        block_coords, slots = coords // torch.tensor(block), coords % torch.tensor(block)
        slot_code = _morton_codes(slots)
        order = (_morton_codes(block_coords) * (int(slot_code.max()) + 1) + slot_code).argsort()
    elif layout == "raster_block":
        order = torch.arange(n)
    else:
        raise ValueError("layout must be raster_block or native_block_morton")
    coords = coords[order]
    inverse = order.argsort()
    neighbors = []
    strides = torch.tensor([shape[1] * shape[2], shape[2], 1])
    for offset in product(*(range(-r, r + 1) for r in rad)):
        target = coords + torch.tensor(offset)
        valid = ((target >= 0) & (target < torch.tensor(shape))).all(-1)
        index = (target * strides).sum(-1).clamp(0, n - 1)
        neighbors.append(torch.where(valid, inverse[index], -1))
    blocks = torch.arange(n).reshape(-1, math.prod(block))
    geom = prepare_geometry(torch.stack(neighbors, 1), blocks, pool_size)
    return TokenLayout(shape, order, coords, geom)

