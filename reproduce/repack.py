"""Paper membership-preserving group permutation; explicit, seeded intervention."""
import torch

def permute_coarse_groups(
    layout: dict,
    pool: int,
    *,
    permutation_seed: int,
) -> dict:
    """Permute intact pooled-summary groups with a declared RNG seed."""
    out = dict(layout)
    num_blocks = int(layout["num_blocks"])
    block_volume = int(layout["block_volume"])
    if num_blocks % int(pool):
        raise ValueError(
            f"Expected pool={pool} to divide num_blocks={num_blocks}"
        )
    groups = torch.arange(num_blocks, dtype=torch.long).reshape(-1, int(pool))
    generator = torch.Generator().manual_seed(permutation_seed)
    group_permutation = torch.randperm(
        groups.shape[0],
        generator=generator,
    )
    if bool(torch.equal(group_permutation, torch.arange(groups.shape[0]))):
        raise RuntimeError("Random coarse-group permutation is the identity")
    block_permutation = groups[group_permutation].reshape(-1)
    packed_order = layout["packed_order"].reshape(
        num_blocks,
        block_volume,
    )[block_permutation].reshape(-1)
    coords = layout["coords_packed"].reshape(
        num_blocks,
        block_volume,
        -1,
    )[block_permutation].reshape(-1, layout["coords_packed"].shape[-1])
    valid = layout["valid_token_mask"].reshape(
        num_blocks,
        block_volume,
    )[block_permutation].reshape(-1)
    inverse = torch.empty_like(packed_order)
    inverse[packed_order] = torch.arange(packed_order.numel())
    out.update(
        {
            "layout": (
                "native_block_morton_coarse_group_sweep_"
                f"{permutation_seed}"
            ),
            "packed_order": packed_order,
            "inverse_packed_order": inverse,
            "coords_packed": coords,
            "valid_token_mask": valid,
            "block_id_packed": (
                torch.arange(num_blocks * block_volume) // block_volume
            ),
            "block_token_indices": torch.arange(
                num_blocks * block_volume
            ).reshape(num_blocks, block_volume),
            "block_valid_mask": valid.reshape(num_blocks, block_volume),
            "coord_to_packed_idx": {
                tuple(map(int, coordinate.tolist())): index
                for index, coordinate in enumerate(coords)
            },
            "repacking_permutation_seed": permutation_seed,
            "repacking_group_count": int(groups.shape[0]),
            "repacking_mean_group_displacement_fraction": float(
                (group_permutation - torch.arange(groups.shape[0]))
                .abs()
                .float()
                .mean()
                .item()
                / max(groups.shape[0] - 1, 1)
            ),
        }
    )
    for key in (
        "block_centers",
        "valid_token_count",
        "block_axis_variance",
        "block_axis_range",
        "block_cov_trace",
        "block_diameter",
        "block_anisotropy",
    ):
        if key in layout:
            out[key] = layout[key][block_permutation]
    return out
