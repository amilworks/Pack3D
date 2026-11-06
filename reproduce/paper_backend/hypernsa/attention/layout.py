from __future__ import annotations

from itertools import product
import math
from typing import Any, Dict, Sequence

import torch
from torch import Tensor


def prod(xs: Sequence[int]) -> int:
    """Return the integer product of a sequence."""
    out = 1
    for x in xs:
        out *= int(x)
    return out


def next_multiple(n: int, mult: int) -> int:
    """Round ``n`` up to the next multiple of ``mult``."""
    return int(math.ceil(int(n) / int(mult)) * int(mult))


def make_coords(grid_shape: Sequence[int]) -> Tensor:
    """Return integer coordinates for an ND grid in row-major order."""
    axes = [torch.arange(int(n)) for n in grid_shape]
    mesh = torch.meshgrid(*axes, indexing="ij")
    return torch.stack(mesh, dim=-1).reshape(-1, len(grid_shape))


def morton_encode(coords: Tensor, bits: int | None = None) -> Tensor:
    """Encode integer coordinates with a standard Morton/Z-order code."""
    coords = coords.long()
    if coords.numel() == 0:
        return torch.empty(coords.shape[0], dtype=torch.long, device=coords.device)
    if bits is None:
        bits = int(coords.max().item()).bit_length()
    n, ndim = coords.shape
    code = torch.zeros(n, dtype=torch.long, device=coords.device)
    for bit in range(bits):
        for dim in range(ndim):
            code |= ((coords[:, dim] >> bit) & 1) << (bit * ndim + dim)
    return code


def row_major_codes(coords: Tensor, shape: Sequence[int]) -> Tensor:
    """Return row-major linear codes for coordinates inside ``shape``."""
    mult = []
    acc = 1
    for n in reversed(tuple(int(x) for x in shape)):
        mult.append(acc)
        acc *= n
    weights = torch.tensor(list(reversed(mult)), device=coords.device, dtype=coords.dtype)
    return (coords * weights).sum(dim=-1)


def block_morton_layout(
    grid_shape: Sequence[int],
    block_shape: Sequence[int],
    micro_order: str = "morton",
) -> Dict[str, Any]:
    """Build a two-level block-Morton packed layout.

    Blocks are sorted by Morton code of block coordinates. Tokens inside each
    block are sorted by ``micro_order``. The resulting layout guarantees that
    each native hyperblock occupies one contiguous packed interval, including
    anisotropic 2D, 3D, and 4D block shapes. Padding cells are retained for
    alignment but are excluded from validity masks and block centers.
    """
    grid_shape = tuple(int(x) for x in grid_shape)
    block_shape = tuple(int(x) for x in block_shape)
    if not 2 <= len(grid_shape) <= 4:
        raise ValueError("HyperNSA layouts are defined for 2D, 3D, or 4D grids")
    if len(grid_shape) != len(block_shape):
        raise ValueError("grid_shape and block_shape must have the same dimensionality")
    if any(g <= 0 for g in grid_shape) or any(b <= 0 for b in block_shape):
        raise ValueError("grid_shape and block_shape entries must be positive")

    padded_grid_shape = tuple(next_multiple(g, b) for g, b in zip(grid_shape, block_shape))
    coords = make_coords(padded_grid_shape)
    valid_token_mask = (coords < torch.tensor(grid_shape)).all(dim=-1)

    block_shape_t = torch.tensor(block_shape)
    block_coords = coords // block_shape_t
    local_coords = coords % block_shape_t
    block_grid_shape = tuple(pg // b for pg, b in zip(padded_grid_shape, block_shape))

    block_bits = max(int(max(bg - 1, 0)).bit_length() for bg in block_grid_shape)
    block_codes = morton_encode(block_coords, bits=block_bits)

    if micro_order == "morton":
        local_bits = max(int(max(bs - 1, 0)).bit_length() for bs in block_shape)
        local_codes = morton_encode(local_coords, bits=local_bits)
    elif micro_order == "row":
        local_codes = row_major_codes(local_coords, block_shape)
    else:
        raise ValueError(f"unknown micro_order={micro_order}")

    local_base = int(local_codes.max().item()) + 1 if local_codes.numel() else 1
    packed_order = torch.argsort(block_codes * local_base + local_codes)
    coords_packed = coords[packed_order]
    valid_token_mask_packed = valid_token_mask[packed_order]
    block_codes_packed = block_codes[packed_order]

    _, block_id_packed = torch.unique_consecutive(block_codes_packed, return_inverse=True)
    num_blocks = int(block_id_packed.max().item()) + 1
    block_volume = prod(block_shape)
    num_tokens_padded = int(coords_packed.shape[0])
    if num_tokens_padded != num_blocks * block_volume:
        raise RuntimeError("Malformed block packing: tokens do not tile into equal-size blocks")

    block_token_indices = torch.arange(num_tokens_padded).reshape(num_blocks, block_volume)
    block_valid_mask = valid_token_mask_packed.reshape(num_blocks, block_volume)

    geometry = block_geometry_stats(coords_packed, valid_token_mask_packed, block_id_packed, num_blocks)
    block_centers = geometry["block_centers"]

    inverse_packed_order = torch.empty_like(packed_order)
    inverse_packed_order[packed_order] = torch.arange(packed_order.numel())
    coord_to_packed_idx = {tuple(map(int, c.tolist())): i for i, c in enumerate(coords_packed)}

    return {
        "layout": "native",
        "grid_shape": grid_shape,
        "padded_grid_shape": padded_grid_shape,
        "block_shape": block_shape,
        "block_grid_shape": block_grid_shape,
        "coords_packed": coords_packed.float(),
        "valid_token_mask": valid_token_mask_packed.bool(),
        "packed_order": packed_order.long(),
        "inverse_packed_order": inverse_packed_order.long(),
        "block_id_packed": block_id_packed.long(),
        "block_token_indices": block_token_indices.long(),
        "block_valid_mask": block_valid_mask.bool(),
        "block_centers": block_centers.float(),
        "valid_token_count": geometry["valid_token_count"],
        "block_axis_variance": geometry["block_axis_variance"],
        "block_axis_range": geometry["block_axis_range"],
        "block_cov_trace": geometry["block_cov_trace"],
        "block_diameter": geometry["block_diameter"],
        "block_anisotropy": geometry["block_anisotropy"],
        "num_tokens_padded": num_tokens_padded,
        "num_tokens_valid": int(valid_token_mask.sum().item()),
        "num_blocks": num_blocks,
        "block_volume": block_volume,
        "coord_to_packed_idx": coord_to_packed_idx,
    }


def raster_block_layout(
    grid_shape: Sequence[int],
    block_shape: Sequence[int],
) -> Dict[str, Any]:
    """Build a raster-order 1D block layout with the same block volume.

    This is the matched non-native baseline for vision experiments. Tokens are
    padded to the same aligned hypergrid but blocks are formed by contiguous
    row-major chunks rather than native hypergrid neighborhoods.
    """
    grid_shape = tuple(int(x) for x in grid_shape)
    block_shape = tuple(int(x) for x in block_shape)
    if not 2 <= len(grid_shape) <= 4:
        raise ValueError("Raster sparse layouts are defined for 2D, 3D, or 4D grids")
    if len(grid_shape) != len(block_shape):
        raise ValueError("grid_shape and block_shape must have the same dimensionality")
    if any(g <= 0 for g in grid_shape) or any(b <= 0 for b in block_shape):
        raise ValueError("grid_shape and block_shape entries must be positive")

    padded_grid_shape = tuple(next_multiple(g, b) for g, b in zip(grid_shape, block_shape))
    coords = make_coords(padded_grid_shape)
    valid_token_mask = (coords < torch.tensor(grid_shape)).all(dim=-1)
    packed_order = torch.arange(coords.shape[0], dtype=torch.long)
    coords_packed = coords
    valid_token_mask_packed = valid_token_mask
    block_volume = prod(block_shape)
    num_tokens_padded = int(coords_packed.shape[0])
    if num_tokens_padded % block_volume != 0:
        raise RuntimeError("Malformed raster packing: padded tokens are not divisible by block volume")
    num_blocks = num_tokens_padded // block_volume
    block_id_packed = torch.arange(num_tokens_padded, dtype=torch.long) // block_volume
    block_token_indices = torch.arange(num_tokens_padded).reshape(num_blocks, block_volume)
    block_valid_mask = valid_token_mask_packed.reshape(num_blocks, block_volume)

    geometry = block_geometry_stats(coords_packed, valid_token_mask_packed, block_id_packed, num_blocks)
    block_centers = geometry["block_centers"]

    inverse_packed_order = torch.empty_like(packed_order)
    inverse_packed_order[packed_order] = torch.arange(packed_order.numel())
    coord_to_packed_idx = {tuple(map(int, c.tolist())): i for i, c in enumerate(coords_packed)}

    return {
        "layout": "raster",
        "grid_shape": grid_shape,
        "padded_grid_shape": padded_grid_shape,
        "block_shape": block_shape,
        "block_grid_shape": (num_blocks,),
        "coords_packed": coords_packed.float(),
        "valid_token_mask": valid_token_mask_packed.bool(),
        "packed_order": packed_order.long(),
        "inverse_packed_order": inverse_packed_order.long(),
        "block_id_packed": block_id_packed.long(),
        "block_token_indices": block_token_indices.long(),
        "block_valid_mask": block_valid_mask.bool(),
        "block_centers": block_centers.float(),
        "valid_token_count": geometry["valid_token_count"],
        "block_axis_variance": geometry["block_axis_variance"],
        "block_axis_range": geometry["block_axis_range"],
        "block_cov_trace": geometry["block_cov_trace"],
        "block_diameter": geometry["block_diameter"],
        "block_anisotropy": geometry["block_anisotropy"],
        "num_tokens_padded": num_tokens_padded,
        "num_tokens_valid": int(valid_token_mask.sum().item()),
        "num_blocks": num_blocks,
        "block_volume": block_volume,
        "coord_to_packed_idx": coord_to_packed_idx,
    }


def canonical_layout_name(layout: str) -> str:
    """Return the canonical name used in logs and layout dispatch."""
    mode = str(layout).lower()
    if mode in {"native", "block_morton", "native_block_morton", "morton"}:
        return "native_block_morton"
    if mode in {"raster", "raster_1d", "raster_block"}:
        return "raster_block"
    if mode in {"axial_slab_z", "z_slab", "depth_slab"}:
        return "axial_slab_z"
    if mode in {"axial_slab_xy", "xy_slab", "inplane_slab"}:
        return "axial_slab_xy"
    if mode in {"layout_bank", "bank"}:
        return "layout_bank"
    raise ValueError(f"unknown block layout={layout}")


def layout_bank_budget(
    layout_bank: Sequence[str],
    *,
    total_selected_blocks: int,
    block_volume: int,
) -> Dict[str, Any]:
    """Return fixed-token-budget metadata for layout-bank diagnostics.

    Phase 4C treats a bank as a set of candidate layouts with a single global
    selected-block budget. The attention module still executes one packed
    layout at a time; this helper prevents diagnostics and configs from
    accidentally counting candidate layouts as extra selected tokens.
    """
    if total_selected_blocks <= 0:
        raise ValueError("total_selected_blocks must be positive")
    if block_volume <= 0:
        raise ValueError("block_volume must be positive")
    bank = [canonical_layout_name(x) for x in layout_bank]
    if not bank:
        raise ValueError("layout_bank must contain at least one layout")
    unique = list(dict.fromkeys(bank))
    return {
        "layout_bank": unique,
        "total_selected_blocks": int(total_selected_blocks),
        "block_volume": int(block_volume),
        "selected_token_budget": int(total_selected_blocks) * int(block_volume),
        "per_layout_candidate_blocks": int(total_selected_blocks),
        "global_topk_across_layouts": True,
    }


def normalize_layout_route_scores(scores_by_layout: Dict[str, Tensor], eps: float = 1e-6) -> Dict[str, Tensor]:
    """Normalize per-layout route scores onto a comparable scale.

    This is used by layout-bank diagnostics. Normalization is per query/KV
    group and leaves the block axis as the ranked axis.
    """
    out: Dict[str, Tensor] = {}
    for name, scores in scores_by_layout.items():
        z = scores.float()
        mean = z.mean(dim=-1, keepdim=True)
        std = z.std(dim=-1, keepdim=True, unbiased=False).clamp_min(float(eps))
        out[canonical_layout_name(name)] = (z - mean) / std
    return out


def block_geometry_stats(
    coords_packed: Tensor,
    valid_token_mask_packed: Tensor,
    block_id_packed: Tensor,
    num_blocks: int,
) -> Dict[str, Tensor]:
    """Return valid-token-only block centers and native geometry statistics."""
    num_blocks = int(num_blocks)
    coords_f = coords_packed.float()
    if num_blocks > 0 and coords_f.shape[0] % num_blocks == 0:
        block_volume = coords_f.shape[0] // num_blocks
        ids = block_id_packed.reshape(num_blocks, block_volume)
        expected = torch.arange(num_blocks, device=block_id_packed.device).view(num_blocks, 1)
        if bool((ids == expected).all()):
            coords_b = coords_f.reshape(num_blocks, block_volume, coords_f.shape[-1])
            valid_b = valid_token_mask_packed.reshape(num_blocks, block_volume).bool()
            has_valid = valid_b.any(dim=1, keepdim=True)
            source_mask = torch.where(has_valid, valid_b, torch.ones_like(valid_b))
            source_f = source_mask.to(coords_b.dtype)
            counts = source_f.sum(dim=1).clamp_min(1.0)
            centers = (coords_b * source_f.unsqueeze(-1)).sum(dim=1) / counts.unsqueeze(-1)
            centered = coords_b - centers.unsqueeze(1)
            axis_variances = (centered.square() * source_f.unsqueeze(-1)).sum(dim=1) / counts.unsqueeze(-1)
            inf = torch.full((), float("inf"), dtype=coords_b.dtype, device=coords_b.device)
            ninf = torch.full((), float("-inf"), dtype=coords_b.dtype, device=coords_b.device)
            mins = torch.where(source_mask.unsqueeze(-1), coords_b, inf).amin(dim=1)
            maxs = torch.where(source_mask.unsqueeze(-1), coords_b, ninf).amax(dim=1)
            ranges = maxs - mins
            diameters = ranges.square().sum(dim=-1).sqrt()
            anisotropies = axis_variances.max(dim=-1).values / axis_variances.min(dim=-1).values.clamp_min(1e-6)
            return {
                "block_centers": centers.float(),
                "valid_token_count": valid_b.sum(dim=1).float(),
                "block_axis_variance": axis_variances.float(),
                "block_axis_range": ranges.float(),
                "block_cov_trace": axis_variances.sum(dim=-1).float(),
                "block_diameter": diameters.float(),
                "block_anisotropy": anisotropies.float(),
            }

    centers = []
    valid_counts = []
    axis_variances = []
    axis_ranges = []
    cov_traces = []
    diameters = []
    anisotropies = []
    for block_id in range(num_blocks):
        in_block = block_id_packed == block_id
        valid_in_block = in_block & valid_token_mask_packed
        source = coords_f[valid_in_block] if bool(valid_in_block.any()) else coords_f[in_block]
        center = source.mean(dim=0)
        centered = source - center
        var = centered.square().mean(dim=0) if source.shape[0] > 0 else torch.zeros(coords_f.shape[-1])
        ranges = source.max(dim=0).values - source.min(dim=0).values if source.shape[0] > 0 else torch.zeros(coords_f.shape[-1])
        diameter = ranges.square().sum().sqrt()
        anisotropy = var.max() / var.min().clamp_min(1e-6)
        centers.append(center)
        valid_counts.append(float(valid_in_block.sum().item()))
        axis_variances.append(var)
        # Inclusive coordinate range per axis, e.g. a contiguous 16-token
        # row-major raster chunk in a 3D volume has range [0, 0, 15].
        axis_ranges.append(ranges)
        cov_traces.append(var.sum())
        diameters.append(diameter)
        anisotropies.append(anisotropy)
    return {
        "block_centers": torch.stack(centers).float(),
        "valid_token_count": torch.tensor(valid_counts, dtype=torch.float32),
        "block_axis_variance": torch.stack(axis_variances).float(),
        "block_axis_range": torch.stack(axis_ranges).float(),
        "block_cov_trace": torch.stack(cov_traces).float(),
        "block_diameter": torch.stack(diameters).float(),
        "block_anisotropy": torch.stack(anisotropies).float(),
    }


def make_block_layout(
    grid_shape: Sequence[int],
    block_shape: Sequence[int],
    *,
    layout: str = "native",
    micro_order: str = "morton",
) -> Dict[str, Any]:
    mode = canonical_layout_name(layout)
    if mode == "native_block_morton":
        out = block_morton_layout(grid_shape, block_shape, micro_order=micro_order)
        out["layout"] = "native_block_morton"
        return out
    if mode == "raster_block":
        out = raster_block_layout(grid_shape, block_shape)
        out["layout"] = "raster_block"
        return out
    if mode in {"axial_slab_z", "axial_slab_xy"}:
        # Axial slab candidates are represented through their configured
        # block_shape while retaining contiguous block-Morton packing. This
        # keeps the selected-attention kernel contract unchanged and lets
        # Phase 4C compare hardware-compatible anisotropic blocks directly.
        out = block_morton_layout(grid_shape, block_shape, micro_order="row" if mode == "axial_slab_z" else micro_order)
        out["layout"] = mode
        return out
    if mode == "layout_bank":
        raise ValueError("layout_bank is a diagnostic/meta layout; execute a concrete packed layout such as native_block_morton or raster_block")
    raise ValueError(f"unknown block layout={layout}")


def plain_morton_block_contiguity(
    grid_shape: Sequence[int],
    block_shape: Sequence[int],
) -> bool:
    """Return whether token-level Morton keeps every native block contiguous."""
    grid_shape = tuple(int(x) for x in grid_shape)
    block_shape = tuple(int(x) for x in block_shape)
    padded_grid_shape = tuple(next_multiple(g, b) for g, b in zip(grid_shape, block_shape))
    coords = make_coords(padded_grid_shape)
    valid = (coords < torch.tensor(grid_shape)).all(dim=-1)
    bits = max(int(max(n - 1, 0)).bit_length() for n in padded_grid_shape)
    order = morton_encode(coords, bits=bits).argsort()
    coords = coords[order]
    valid = valid[order]
    block_coords = coords // torch.tensor(block_shape)
    block_ids = row_major_codes(block_coords, tuple(pg // b for pg, b in zip(padded_grid_shape, block_shape)))
    block_ids = block_ids[valid]
    indices = torch.arange(block_ids.numel())
    for bid in torch.unique(block_ids, sorted=True):
        loc = indices[block_ids == bid]
        if int(loc.max() - loc.min() + 1) != loc.numel():
            return False
    return True


def block_morton_block_contiguity(
    grid_shape: Sequence[int],
    block_shape: Sequence[int],
) -> bool:
    """Return whether block-Morton packed valid cells are contiguous per block."""
    layout = block_morton_layout(grid_shape, block_shape)
    valid = layout["valid_token_mask"]
    block_ids = layout["block_id_packed"][valid]
    indices = torch.arange(block_ids.numel())
    for bid in torch.unique(block_ids, sorted=True):
        loc = indices[block_ids == bid]
        if int(loc.max() - loc.min() + 1) != loc.numel():
            return False
    return True


def build_local_neighbors(
    coords_packed: Tensor,
    valid_token_mask: Tensor,
    local_radius: Sequence[int] | int,
    coord_to_packed_idx: Dict[tuple[int, ...], int],
) -> tuple[Tensor, Tensor]:
    """Precompute native-grid local neighbor indices and validity masks."""
    ndim = coords_packed.shape[-1]
    if isinstance(local_radius, int):
        local_radius = (int(local_radius),) * ndim
    else:
        local_radius = tuple(int(x) for x in local_radius)
    if len(local_radius) != ndim:
        raise ValueError("local_radius dimensionality must match the grid")

    num_tokens = int(coords_packed.shape[0])
    offsets = torch.tensor(list(product(*[range(-r, r + 1) for r in local_radius])), dtype=torch.long)
    num_offsets = int(offsets.shape[0])
    neighbor_indices = torch.zeros(num_tokens, num_offsets, dtype=torch.long)
    neighbor_mask = torch.zeros(num_tokens, num_offsets, dtype=torch.bool)

    # Fast path for packed layouts that contain every coordinate in the padded
    # grid exactly once. This avoids millions of Python dict lookups at H200
    # scale while preserving the same neighbor/mask contract.
    coords_long = coords_packed.long().cpu()
    valid_cpu = valid_token_mask.bool().cpu()
    if num_tokens > 0:
        padded_shape = tuple(int(x) + 1 for x in coords_long.max(dim=0).values.tolist())
        if prod(padded_shape) == num_tokens:
            weights = []
            acc = 1
            for size in reversed(padded_shape):
                weights.append(acc)
                acc *= int(size)
            weights_t = torch.tensor(list(reversed(weights)), dtype=torch.long)
            flat_codes = (coords_long * weights_t).sum(dim=-1)
            flat_to_packed = torch.empty(num_tokens, dtype=torch.long)
            flat_to_packed[flat_codes] = torch.arange(num_tokens, dtype=torch.long)
            shape_t = torch.tensor(padded_shape, dtype=torch.long)
            chunk = 65536
            token_arange = torch.arange(num_tokens, dtype=torch.long)
            for start in range(0, num_tokens, chunk):
                end = min(start + chunk, num_tokens)
                targets = coords_long[start:end, None, :] + offsets[None, :, :]
                in_bounds = ((targets >= 0) & (targets < shape_t.view(1, 1, -1))).all(dim=-1)
                linear = (targets.clamp_min(0) * weights_t.view(1, 1, -1)).sum(dim=-1).clamp(0, num_tokens - 1)
                neigh = flat_to_packed[linear]
                mask = in_bounds & valid_cpu[neigh]
                fallback = token_arange[start:end, None].expand_as(neigh)
                neighbor_indices[start:end] = torch.where(mask, neigh, fallback)
                neighbor_mask[start:end] = mask
            return neighbor_indices, neighbor_mask

    offsets_list = [tuple(int(x) for x in offset.tolist()) for offset in offsets]
    for token_idx, coord in enumerate(coords_long.tolist()):
        for j, offset in enumerate(offsets_list):
            target = tuple(ci + oi for ci, oi in zip(coord, offset))
            neighbor_idx = coord_to_packed_idx.get(target)
            if neighbor_idx is None:
                neighbor_indices[token_idx, j] = token_idx
                neighbor_mask[token_idx, j] = False
                continue
            neighbor_indices[token_idx, j] = neighbor_idx
            neighbor_mask[token_idx, j] = bool(valid_token_mask[neighbor_idx])
    return neighbor_indices, neighbor_mask


def pad_grid_to_shape(x: Tensor, target_grid_shape: Sequence[int]) -> Tensor:
    """Pad an ND token grid ``[B, *grid, C]`` to ``target_grid_shape``."""
    target_grid_shape = tuple(int(x) for x in target_grid_shape)
    if tuple(x.shape[1:-1]) == target_grid_shape:
        return x
    out = x.new_zeros((x.shape[0], *target_grid_shape, x.shape[-1]))
    out[(slice(None),) + tuple(slice(0, s) for s in x.shape[1:-1]) + (slice(None),)] = x
    return out


def pack_grid(x: Tensor, padded_grid_shape: Sequence[int], packed_order: Tensor) -> Tensor:
    """Pack ``[B, *grid, C]`` tokens into block-Morton order."""
    x = pad_grid_to_shape(x, padded_grid_shape)
    flat = x.reshape(x.shape[0], -1, x.shape[-1])
    return flat[:, packed_order.to(flat.device), :]


def unpack_grid(
    x_packed: Tensor,
    grid_shape: Sequence[int],
    padded_grid_shape: Sequence[int],
    packed_order: Tensor,
) -> Tensor:
    """Invert ``pack_grid`` and crop away alignment padding."""
    batch, num_tokens, channels = x_packed.shape
    flat = x_packed.new_zeros((batch, num_tokens, channels))
    flat[:, packed_order.to(x_packed.device), :] = x_packed
    grid_padded = flat.reshape(batch, *tuple(int(x) for x in padded_grid_shape), channels)
    return grid_padded[(slice(None),) + tuple(slice(0, int(g)) for g in grid_shape) + (slice(None),)]


def block_origins(grid_shape: Sequence[int], block_shape: Sequence[int]) -> list[tuple[int, ...]]:
    """Return row-major native block origins for synthetic data generation."""
    ranges = [range(0, int(g), int(b)) for g, b in zip(grid_shape, block_shape)]
    return [tuple(int(x) for x in origin) for origin in product(*ranges)]
