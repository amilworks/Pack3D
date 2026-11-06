from __future__ import annotations

from typing import Any, Dict, Sequence

import torch
from torch import Tensor, nn

from hypernsa.attention.hypernsa_morton import HyperNSABlock
from hypernsa.attention.layout import prod


class PatchEmbedND(nn.Module):
    """Non-overlapping patch embedding for 2D, 3D, or 4D inputs."""

    def __init__(self, in_channels: int, patch_shape: Sequence[int], dim: int):
        super().__init__()
        self.patch_shape = tuple(int(x) for x in patch_shape)
        self.proj = nn.Linear(int(in_channels) * prod(self.patch_shape), int(dim))

    def forward(self, x: Tensor) -> Tensor:
        batch, channels, *spatial = x.shape
        if len(spatial) != len(self.patch_shape):
            raise ValueError("input dimensionality does not match patch_shape")
        if not 2 <= len(spatial) <= 4:
            raise ValueError("HyperNSA patch embedding expects 2D, 3D, or 4D inputs")
        for size, patch in zip(spatial, self.patch_shape):
            if size % patch != 0:
                raise ValueError(f"spatial shape {tuple(spatial)} must be divisible by patch_shape {self.patch_shape}")
        grid = [size // patch for size, patch in zip(spatial, self.patch_shape)]
        pieces = [batch, channels]
        for grid_size, patch in zip(grid, self.patch_shape):
            pieces.extend([grid_size, patch])
        x = x.reshape(*pieces)
        ndim = len(grid)
        perm = [0]
        perm.extend(2 + 2 * i for i in range(ndim))
        perm.append(1)
        perm.extend(3 + 2 * i for i in range(ndim))
        x = x.permute(*perm).contiguous()
        return self.proj(x.reshape(batch, *grid, channels * prod(self.patch_shape)))


class HyperNSANDBackbone(nn.Module):
    """Generic 2D/3D/4D HyperNSA backbone with optional patch embedding."""

    def __init__(
        self,
        *,
        grid_shape: Sequence[int],
        input_dim: int | None = None,
        in_channels: int | None = None,
        patch_shape: Sequence[int] | None = None,
        dim: int = 384,
        depth: int = 12,
        heads: int = 6,
        kv_heads: int | None = 3,
        dim_head: int = 64,
        block_shape: Sequence[int] | None = None,
        local_radius: Sequence[int] | int = 1,
        num_summary_atoms: int = 2,
        num_selected_blocks: int = 4,
        residual_weight: float = 0.25,
        distance_weight: float = 0.10,
        use_triton_kernel: bool = True,
        separate_branch_kv: bool = True,
        exclude_own_block_from_selection: bool = True,
    ):
        super().__init__()
        self.grid_shape = tuple(int(x) for x in grid_shape)
        if not 2 <= len(self.grid_shape) <= 4:
            raise ValueError("grid_shape must be 2D, 3D, or 4D")
        self.dim = int(dim)
        self.patch: PatchEmbedND | None = None
        self.in_channels = int(in_channels) if in_channels is not None else None
        if patch_shape is not None:
            if in_channels is None:
                raise ValueError("in_channels is required when patch_shape is provided")
            self.patch = PatchEmbedND(in_channels, patch_shape, dim)
            input_dim = dim
        if input_dim is None:
            input_dim = dim
        self.input_proj = nn.Identity() if int(input_dim) == dim else nn.Linear(int(input_dim), dim)
        if block_shape is None:
            block_shape = tuple(4 if size >= 4 else size for size in self.grid_shape)
        self.pos = nn.Parameter(torch.zeros(1, *self.grid_shape, dim))
        nn.init.trunc_normal_(self.pos, std=0.02)
        self.blocks = nn.ModuleList(
            [
                HyperNSABlock(
                    dim=dim,
                    grid_shape=self.grid_shape,
                    heads=heads,
                    kv_heads=kv_heads,
                    dim_head=dim_head,
                    block_shape=block_shape,
                    local_radius=local_radius,
                    num_summary_atoms=num_summary_atoms,
                    num_selected_blocks=num_selected_blocks,
                    residual_weight=residual_weight,
                    distance_weight=distance_weight,
                    use_triton_kernel=use_triton_kernel,
                    separate_branch_kv=separate_branch_kv,
                    exclude_own_block_from_selection=exclude_own_block_from_selection,
                )
                for _ in range(int(depth))
            ]
        )
        self.norm = nn.LayerNorm(dim)

    def forward_features(
        self,
        x: Tensor,
        query_disable_local_mask: Tensor | None = None,
        return_aux: bool = False,
    ) -> Tensor | tuple[Tensor, Dict[str, Any]]:
        if self.patch is not None and x.dim() == len(self.grid_shape) + 2 and self.in_channels is not None and int(x.shape[1]) == self.in_channels:
            x = self.patch(x)
        x = self.input_proj(x) + self.pos.to(x.device)
        aux_layers: list[Dict[str, Any]] = []
        for block in self.blocks:
            if return_aux:
                x, aux = block(x, query_disable_local_mask=query_disable_local_mask, return_aux=True)
                aux_layers.append(aux)
            else:
                x = block(x, query_disable_local_mask=query_disable_local_mask)
        x = self.norm(x)
        if return_aux:
            merged = dict(aux_layers[-1]) if aux_layers else {}
            merged["layers"] = aux_layers
            return x, merged
        return x

    def forward(self, x: Tensor) -> Tensor:
        return self.forward_features(x)


class HyperNSATokenClassifier(nn.Module):
    """Small classifier over all HyperNSA tokens, used for smoke experiments."""

    def __init__(self, grid_shape: Sequence[int], input_dim: int, num_classes: int = 2, **kwargs: Any):
        super().__init__()
        dim = int(kwargs.pop("dim", 32))
        self.backbone = HyperNSANDBackbone(grid_shape=grid_shape, input_dim=input_dim, dim=dim, **kwargs)
        self.head = nn.Sequential(nn.Linear(prod(grid_shape) * dim, max(64, 2 * dim)), nn.GELU(), nn.Linear(max(64, 2 * dim), num_classes))

    def forward(self, x: Tensor, query_disable_local_mask: Tensor | None = None) -> Tensor:
        features = self.backbone.forward_features(x, query_disable_local_mask=query_disable_local_mask)
        return self.head(features.reshape(features.shape[0], -1))


class ProbeClassifierND(nn.Module):
    """Classify from a single probe coordinate so attention must move evidence."""

    def __init__(
        self,
        grid_shape: Sequence[int],
        input_dim: int,
        probe_coord: Sequence[int],
        num_classes: int = 2,
        **kwargs: Any,
    ):
        super().__init__()
        dim = int(kwargs.pop("dim", 32))
        self.grid_shape = tuple(int(x) for x in grid_shape)
        self.probe_coord = tuple(int(x) for x in probe_coord)
        self.backbone = HyperNSANDBackbone(grid_shape=self.grid_shape, input_dim=input_dim, dim=dim, **kwargs)
        self.head = nn.Sequential(nn.Linear(dim, 2 * dim), nn.GELU(), nn.Linear(2 * dim, int(num_classes)))

    def forward(self, x: Tensor, query_disable_local_mask: Tensor | None = None, return_aux: bool = False):
        if return_aux:
            features, aux = self.backbone.forward_features(x, query_disable_local_mask=query_disable_local_mask, return_aux=True)
        else:
            features = self.backbone.forward_features(x, query_disable_local_mask=query_disable_local_mask)
            aux = None
        probe = features[(slice(None),) + self.probe_coord + (slice(None),)]
        logits = self.head(probe)
        if return_aux:
            return logits, aux
        return logits
