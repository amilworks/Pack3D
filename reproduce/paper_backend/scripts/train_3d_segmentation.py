#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path
import sys
import time
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch
from torch import nn
import torch.nn.functional as F

from hypernsa.models.realdata import RealDataBackbone
from hypernsa.training.realdata import (
    append_jsonl,
    activation_checkpointing_mode,
    autocast_context,
    aux_metrics,
    block_target_mask,
    build_backbone,
    first_hyper_attn,
    grad_norm,
    make_loaders,
    max_cuda_memory_gb,
    phase_config_fields,
    select_device,
)
from hypernsa.training.wandb_utils import add_config_args, init_wandb, load_config, log_artifact_files, write_resolved_config, write_run_context
from hypernsa.utils.seed import seed_everything


LEARNING_DIAGNOSTIC_KEYS = {
    "gate_local_mean",
    "gate_compressed_mean",
    "gate_selected_mean",
    "gate_entropy_mean",
    "local_output_norm",
    "compressed_output_norm",
    "selected_output_norm",
    "local_post_output_norm",
    "compressed_post_output_norm",
    "selected_post_output_norm",
}


def _manifest_audit_fields(cfg: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    manifest_path = cfg.get("data", {}).get("manifest") or meta.get("manifest")
    out: dict[str, Any] = {
        "manifest": str(manifest_path or ""),
        "channel_set": str(cfg.get("data", {}).get("channel_set", "")),
        "input_channel_set": str(cfg.get("data", {}).get("input_channel_set", "")),
        "channel_semantics": "",
        "target_type": "",
    }
    if manifest_path:
        try:
            manifest = json.loads(Path(manifest_path).read_text())
        except Exception:
            manifest = {}
        metadata = manifest.get("metadata", {}) if isinstance(manifest, dict) else {}
        for key in ("channel_set", "input_channel_set"):
            if not out.get(key):
                out[key] = str(metadata.get(key, manifest.get(key, "")))
        semantics = metadata.get("channel_semantics", manifest.get("channel_semantics", []))
        if isinstance(semantics, (list, tuple)):
            out["channel_semantics"] = ",".join(str(x) for x in semantics)
        elif semantics:
            out["channel_semantics"] = str(semantics)
        out["target_type"] = str(metadata.get("target_type", manifest.get("target_type", meta.get("task", ""))))
    expected_channel_set = cfg.get("data", {}).get("expected_channel_set")
    if expected_channel_set and str(expected_channel_set) not in {out.get("channel_set"), out.get("input_channel_set")}:
        raise ValueError(
            f"data.expected_channel_set={expected_channel_set!r} did not match manifest channel_set="
            f"{out.get('channel_set')!r} or input_channel_set={out.get('input_channel_set')!r}"
        )
    return out


def _runtime_model_audit(
    model: "TokenSegmentationModel",
    cfg: dict[str, Any],
    meta: dict[str, Any],
    device: torch.device,
) -> dict[str, Any]:
    model_cfg = cfg.get("model", {})
    attn = first_hyper_attn(model)
    if str(model_cfg.get("name", "")) in {"hypernsa", "hypernsa_s", "hypernsa_l", "hypernsa_lm"} and attn is None:
        raise ValueError("HyperNSA/Pack3D config did not create a HyperNSABlock attention module")
    if attn is not None:
        for key in (
            "pos_encoding",
            "branch_mixer_mode",
            "branch_gate_mode",
            "branch_output_norm",
            "enabled_branches",
            "coarse_summary_pool_size",
            "route_granularity",
        ):
            if key not in model_cfg:
                continue
            expected = model_cfg[key]
            actual = getattr(attn, key)
            if isinstance(expected, (list, tuple)):
                expected_norm = tuple(str(x) for x in expected)
                actual_norm = tuple(str(x) for x in actual)
            else:
                expected_norm = str(expected)
                actual_norm = str(actual)
            if expected_norm != actual_norm:
                raise ValueError(f"Runtime audit mismatch for model.{key}: config={expected_norm!r}, actual={actual_norm!r}")
    descriptor_mode = str(model_cfg.get("structure_conditioning", "none"))
    descriptor_location = str(model_cfg.get("structure_conditioning_location", "head_only"))
    audit = {
        "kind": "runtime_audit",
        "status": "passed",
        "run_id": str(cfg.get("run_id", "")),
        "device": str(device),
        "cuda_device_index": int(torch.cuda.current_device()) if device.type == "cuda" else "",
        "model": str(model_cfg.get("name", "")),
        "input_channels": int(model_cfg.get("in_channels", 0) or 0),
        "input_shape": "x".join(map(str, model_cfg.get("input_shape", []))),
        "patch_shape": "x".join(map(str, model_cfg.get("patch_shape", []))),
        "grid_shape": "x".join(map(str, getattr(model.backbone, "grid_shape", ()))),
        "block_shape": "x".join(map(str, getattr(model.backbone, "block_shape", ()))),
        "parameter_count": int(sum(p.numel() for p in model.parameters())),
        "enabled_branches": ",".join(str(x) for x in getattr(attn, "enabled_branches", ())) if attn is not None else "",
        "pos_encoding": str(getattr(attn, "pos_encoding", getattr(model.backbone, "pos_encoding", ""))),
        "rotary_coordinate_mode": str(getattr(attn, "rotary_coordinate_mode", getattr(model.backbone, "rotary_coordinate_mode", ""))),
        "rotary_axis_pair_allocation": str(getattr(attn, "rotary_axis_pair_allocation", getattr(model.backbone, "rotary_axis_pair_allocation", ""))),
        "compressed_rope_mode": str(getattr(attn, "compressed_rope_mode", getattr(model.backbone, "compressed_rope_mode", ""))),
        "activation_checkpointing": str(model_cfg.get("activation_checkpointing", "none")),
        "activation_checkpointing_mode": activation_checkpointing_mode(model_cfg.get("activation_checkpointing", "none")),
        "checkpoint_local_attention": bool(getattr(attn, "checkpoint_local_attention", False)) if attn is not None else "",
        "branch_output_fusion": str(getattr(attn, "branch_output_fusion", "")) if attn is not None else "",
        "query_tile_checkpoint": bool(getattr(attn, "query_tile_checkpoint", False)) if attn is not None else "",
        "branch_mixer_mode": str(getattr(attn, "branch_mixer_mode", "")),
        "branch_gate_mode": str(getattr(attn, "branch_gate_mode", "")),
        "branch_output_norm": str(getattr(attn, "branch_output_norm", "")),
        "branch_layer_scale": bool(getattr(attn, "branch_layer_scale_enabled", False)),
        "branch_layer_scale_init": str(model_cfg.get("branch_layer_scale_init", "")),
        "coarse_summary_pool_size": int(getattr(attn, "coarse_summary_pool_size", 0) or 0) if attn is not None else "",
        "route_granularity": str(getattr(attn, "route_granularity", "")),
        "descriptor_mode": descriptor_mode,
        "descriptor_dim": int(getattr(model.backbone, "dim", 0) or 0) if model.structure_embedding is not None else 0,
        "descriptor_injection_site": descriptor_location if model.structure_embedding is not None else "none",
        "descriptor_injected_before_attention": bool(model.structure_embedding is not None and descriptor_location == "pre_backbone_tokens"),
        "segmentation_head": str(model.segmentation_head),
        "target_type": str(meta.get("task", "")),
    }
    audit.update(_manifest_audit_fields(cfg, meta))
    return audit


class MonaiTokenUNetHead(nn.Module):
    """MONAI BasicUNet head over the token grid.

    This is a decoder-matched reviewer control.  The attention backbone still
    produces the token grid, then the same MONAI multiscale decoder is attached
    to Window and Window+Global-LM variants.
    """

    def __init__(
        self,
        *,
        dim: int,
        in_channels: int = 0,
        num_classes: int,
        grid_shape: tuple[int, ...],
        project_dim: int = 32,
        features: list[int] | tuple[int, ...] = (32, 32, 64, 128, 256, 32),
        upsample: str = "deconv",
        include_raw_input_skip: bool = False,
    ) -> None:
        super().__init__()
        if len(grid_shape) != 3:
            raise ValueError("monai_basic_unet token decoder currently supports 3D token grids only")
        try:
            from monai.networks.nets import BasicUNet
        except Exception as exc:  # pragma: no cover - exercised only when dependency is missing
            raise ImportError("segmentation_head='monai_basic_unet' requires the `monai` package") from exc
        feat = tuple(int(x) for x in features)
        if len(feat) != 6:
            raise ValueError("monai_decoder_features must contain 6 channel values for MONAI BasicUNet")
        self.include_raw_input_skip = bool(include_raw_input_skip)
        project_in = int(dim) + (int(in_channels) if self.include_raw_input_skip else 0)
        self.project = nn.Conv3d(project_in, int(project_dim), kernel_size=1)
        self.decoder = BasicUNet(
            spatial_dims=3,
            in_channels=int(project_dim),
            out_channels=int(num_classes),
            features=feat,
            norm=("instance", {"affine": True}),
            upsample=str(upsample),
        )
        self.project_dim = int(project_dim)
        self.features = feat

    def forward(self, features: torch.Tensor, raw_input: torch.Tensor | None = None) -> torch.Tensor:
        x = features.permute(0, features.ndim - 1, *range(1, features.ndim - 1)).contiguous()
        if self.include_raw_input_skip:
            if raw_input is None:
                raise ValueError("include_raw_input_skip=True requires the raw input tensor")
            raw = raw_input
            if tuple(raw.shape[-3:]) != tuple(x.shape[-3:]):
                raw = F.interpolate(raw.float(), size=tuple(x.shape[-3:]), mode="trilinear", align_corners=False).to(dtype=x.dtype)
            x = torch.cat([x, raw.to(device=x.device, dtype=x.dtype)], dim=1)
        return self.decoder(self.project(x))


class TokenSegmentationModel(nn.Module):
    def __init__(
        self,
        backbone: RealDataBackbone,
        num_classes: int,
        *,
        num_structures: int = 1,
        structure_conditioning: str = "none",
        structure_conditioning_location: str = "head_only",
        segmentation_head: str = "linear",
        monai_decoder_project_dim: int = 32,
        monai_decoder_features: list[int] | tuple[int, ...] = (32, 32, 64, 128, 256, 32),
        monai_decoder_upsample: str = "deconv",
        monai_decoder_raw_input_skip: bool = False,
    ):
        super().__init__()
        self.backbone = backbone
        self.model_name = backbone.model_name
        self.segmentation_head = str(segmentation_head)
        self.structure_conditioning = str(structure_conditioning)
        if self.structure_conditioning == "pre_backbone_tokens":
            self.structure_conditioning = "structure_id_embedding"
            structure_conditioning_location = "pre_backbone_tokens"
        valid_locations = {"head_only", "pre_backbone_tokens"}
        if structure_conditioning_location not in valid_locations:
            raise ValueError(f"structure_conditioning_location must be one of {sorted(valid_locations)}")
        self.structure_conditioning_location = str(structure_conditioning_location)
        self.num_structures = int(num_structures)
        self.structure_embedding = (
            nn.Embedding(self.num_structures, backbone.dim)
            if self.structure_conditioning in {"structure_id_embedding", "embedding"} and self.num_structures > 1
            else None
        )
        if self.segmentation_head == "linear":
            self.head = nn.Linear(backbone.dim, int(num_classes))
        elif self.segmentation_head == "monai_basic_unet":
            self.head = MonaiTokenUNetHead(
                dim=backbone.dim,
                in_channels=int(getattr(backbone, "in_channels", 0) or 0),
                num_classes=int(num_classes),
                grid_shape=tuple(backbone.grid_shape),
                project_dim=int(monai_decoder_project_dim),
                features=tuple(int(x) for x in monai_decoder_features),
                upsample=str(monai_decoder_upsample),
                include_raw_input_skip=bool(monai_decoder_raw_input_skip),
            )
        else:
            raise ValueError("segmentation_head must be one of ['linear', 'monai_basic_unet']")

    def _condition(self, features: torch.Tensor, structure_id: torch.Tensor | None) -> torch.Tensor:
        if self.structure_embedding is None:
            return features
        if structure_id is None:
            raise ValueError("structure_id_embedding conditioning requires structure_id in each batch")
        emb = self.structure_embedding(structure_id.long().to(features.device))
        view_shape = (features.shape[0],) + (1,) * (features.ndim - 2) + (features.shape[-1],)
        return features + emb.view(view_shape)

    def _condition_vector(self, structure_id: torch.Tensor | None, device: torch.device) -> torch.Tensor | None:
        if self.structure_embedding is None or self.structure_conditioning_location != "pre_backbone_tokens":
            return None
        if structure_id is None:
            raise ValueError("pre_backbone_tokens conditioning requires structure_id in each batch")
        return self.structure_embedding(structure_id.long().to(device))

    def forward(
        self,
        x: torch.Tensor,
        query_disable_local_mask: torch.Tensor | None = None,
        return_aux: bool = False,
        structure_id: torch.Tensor | None = None,
    ):
        token_condition = self._condition_vector(structure_id, x.device)
        if return_aux:
            features, aux = self.backbone(
                x,
                query_disable_local_mask=query_disable_local_mask,
                return_aux=True,
                token_condition=token_condition,
            )
        else:
            features = self.backbone(
                x,
                query_disable_local_mask=query_disable_local_mask,
                return_aux=False,
                token_condition=token_condition,
            )
            aux = None
        if self.structure_conditioning_location == "head_only":
            features = self._condition(features, structure_id)
        if self.segmentation_head == "linear":
            logits = self.head(features).permute(0, features.ndim - 1, *range(1, features.ndim - 1)).contiguous()
        else:
            logits = self.head(features, raw_input=x)
        if return_aux:
            return logits, aux
        return logits


def _downsample_labels(label: torch.Tensor, grid_shape: tuple[int, ...]) -> torch.Tensor:
    if tuple(label.shape[1:]) == grid_shape:
        return label.long()
    z = F.interpolate(label[:, None].float(), size=grid_shape, mode="nearest")
    return z[:, 0].long()


def _target_grid_shape(cfg: dict[str, Any]) -> tuple[int, ...] | None:
    value = cfg.get("training", {}).get("target_grid_shape")
    if value is None:
        return None
    shape = tuple(int(x) for x in value)
    return shape if shape else None


def _central_slices(full_shape: tuple[int, ...], target_shape: tuple[int, ...]) -> tuple[slice, ...]:
    if len(full_shape) != len(target_shape):
        raise ValueError(f"target_grid_shape rank {len(target_shape)} does not match grid rank {len(full_shape)}")
    slices = []
    for full, target in zip(full_shape, target_shape):
        if target <= 0:
            raise ValueError(f"target_grid_shape must be positive, got {target_shape}")
        if target > full:
            raise ValueError(f"target_grid_shape {target_shape} cannot exceed grid_shape {full_shape}")
        start = (full - target) // 2
        slices.append(slice(start, start + target))
    return tuple(slices)


def _central_raw_slices(cfg: dict[str, Any], x: torch.Tensor) -> tuple[slice, ...]:
    model_cfg = cfg.get("model", {})
    spatial = tuple(int(s) for s in x.shape[2:])
    patch_shape = tuple(int(p) for p in model_cfg.get("patch_shape", [1] * len(spatial)))
    grid_shape = tuple(int(s) // int(p) for s, p in zip(spatial, patch_shape))
    target_grid = _target_grid_shape(cfg) or grid_shape
    grid_slices = _central_slices(grid_shape, target_grid)
    raw_slices = []
    for slc, patch, full in zip(grid_slices, patch_shape, spatial):
        start = int(slc.start or 0) * int(patch)
        stop = int(slc.stop or grid_shape[len(raw_slices)]) * int(patch)
        raw_slices.append(slice(max(0, start), min(int(full), stop)))
    return tuple(raw_slices)


def _apply_input_corruption(x: torch.Tensor, cfg: dict[str, Any]) -> torch.Tensor:
    corruption = cfg.get("training", {}).get("input_corruption", {})
    mode = str(corruption.get("mode", "none"))
    if mode in {"none", "", "null"}:
        return x
    channel = int(corruption.get("channel", 0))
    if channel < 0 or channel >= x.shape[1]:
        raise ValueError(f"input_corruption channel {channel} is outside input channel count {x.shape[1]}")
    value = float(corruption.get("fill_value", 0.0))
    slices = _central_raw_slices(cfg, x)
    out = x.clone()
    target = out[(slice(None), channel, *slices)]
    if mode == "target_dropout":
        probability = float(corruption.get("probability", 0.5))
        keep = torch.rand_like(target.float()) >= probability
        target.mul_(keep.to(dtype=target.dtype))
        if value != 0.0:
            target.add_((~keep).to(dtype=target.dtype) * value)
    elif mode == "target_cuboid_mask":
        inner = []
        for size in target.shape[1:]:
            width = max(1, int(round(int(size) * float(corruption.get("fraction", 0.5)))))
            start = max(0, (int(size) - width) // 2)
            inner.append(slice(start, start + width))
        target[(slice(None), *inner)] = value
    elif mode == "target_stripe_mask":
        axis = int(corruption.get("axis", -1))
        spatial_rank = target.ndim - 1
        if axis < 0:
            axis = spatial_rank + axis
        axis = max(0, min(spatial_rank - 1, axis))
        size = int(target.shape[1 + axis])
        width = max(1, int(round(size * float(corruption.get("fraction", 0.5)))))
        start = max(0, (size - width) // 2)
        inner = [slice(None) for _ in range(spatial_rank)]
        inner[axis] = slice(start, start + width)
        target[(slice(None), *inner)] = value
    else:
        raise ValueError(f"unknown input_corruption mode={mode}")
    return out


def _crop_to_target_grid(logits: torch.Tensor, target: torch.Tensor, cfg: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor]:
    target_shape = _target_grid_shape(cfg)
    if target_shape is None:
        return logits, target
    full_shape = tuple(int(x) for x in target.shape[1:])
    if target_shape == full_shape:
        return logits, target
    slices = _central_slices(full_shape, target_shape)
    return logits[(slice(None), slice(None), *slices)], target[(slice(None), *slices)]


def _dice_iou(logits: torch.Tensor, target: torch.Tensor, num_classes: int) -> dict[str, float]:
    pred = logits.argmax(dim=1)
    vals_dice = []
    vals_iou = []
    for cls in range(1, int(num_classes)):
        p = pred == cls
        t = target == cls
        inter = (p & t).sum().float()
        denom = p.sum().float() + t.sum().float()
        union = (p | t).sum().float()
        vals_dice.append(float(((2 * inter + 1e-6) / (denom + 1e-6)).item()))
        vals_iou.append(float(((inter + 1e-6) / (union + 1e-6)).item()))
    if not vals_dice:
        vals_dice = [0.0]
        vals_iou = [0.0]
    fg_recall = []
    for cls in range(1, int(num_classes)):
        p = pred == cls
        t = target == cls
        fg_recall.append(float(((p & t).sum().float() / t.sum().float().clamp_min(1.0)).item()))
    return {
        "val/dice": float(sum(vals_dice) / len(vals_dice)),
        "val/iou": float(sum(vals_iou) / len(vals_iou)),
        "val/foreground_recall": float(sum(fg_recall) / max(1, len(fg_recall))),
    }


def _soft_dice_loss(logits: torch.Tensor, target: torch.Tensor, num_classes: int) -> torch.Tensor:
    if int(num_classes) <= 1:
        return logits.new_tensor(0.0)
    probs = logits.float().softmax(dim=1)
    one_hot = F.one_hot(target.long(), num_classes=int(num_classes)).movedim(-1, 1).to(probs.dtype)
    dims = tuple(range(2, probs.ndim))
    # Foreground-only Dice is the standard binary-segmentation objective; the
    # background term can dominate small-organ crops and hide foreground errors.
    probs_fg = probs[:, 1:]
    target_fg = one_hot[:, 1:]
    inter = (probs_fg * target_fg).sum(dim=dims)
    denom = probs_fg.sum(dim=dims) + target_fg.sum(dim=dims)
    dice = (2.0 * inter + 1.0) / (denom + 1.0)
    return 1.0 - dice.mean()


def _segmentation_loss(logits: torch.Tensor, target: torch.Tensor, cfg: dict[str, Any], num_classes: int) -> tuple[torch.Tensor, dict[str, float]]:
    training = cfg.get("training", {})
    mode = str(training.get("loss", "cross_entropy"))
    ce = F.cross_entropy(logits.float(), target)
    dice = _soft_dice_loss(logits, target, num_classes)
    if mode in {"cross_entropy", "ce"}:
        loss = ce
    elif mode in {"dice_ce", "ce_dice"}:
        loss = ce + float(training.get("dice_loss_weight", 1.0)) * dice
    elif mode == "dice":
        loss = dice
    else:
        raise ValueError(f"unsupported training.loss={mode!r}")
    return loss, {"ce_loss": float(ce.detach().item()), "dice_loss": float(dice.detach().item())}


def _unpack_batch(batch):
    if len(batch) == 3:
        return batch[0], batch[1], batch[2]
    return batch[0], batch[1], None


def _is_finite_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    return False


def _accumulate_number(sums: dict[str, float], counts: dict[str, int], key: str, value: Any) -> None:
    if _is_finite_number(value):
        sums[key] = sums.get(key, 0.0) + float(value)
        counts[key] = counts.get(key, 0) + 1


def _atom_aux_loss_enabled(cfg: dict[str, Any]) -> bool:
    model_cfg = cfg.get("model", {})
    return any(
        abs(float(model_cfg.get(key, 0.0) or 0.0)) > 0.0
        for key in (
            "atom_balance_loss_weight",
            "atom_entropy_loss_weight",
            "atom_orthogonality_loss_weight",
        )
    )


def _branch_gate_prior_progress(cfg: dict[str, Any], step: int, max_steps: int) -> float:
    model_cfg = cfg.get("model", {})
    schedule = str(model_cfg.get("branch_gate_prior_schedule", "none"))
    if schedule == "none":
        return 1.0
    steps = int(model_cfg.get("branch_gate_prior_steps", cfg.get("training", {}).get("branch_gate_prior_steps", 0)) or 0)
    if steps <= 0:
        steps = max(1, int(max_steps))
    return max(0.0, min(1.0, float(step) / float(steps)))


def _set_branch_gate_prior_progress(model: TokenSegmentationModel, cfg: dict[str, Any], step: int, max_steps: int) -> None:
    progress = _branch_gate_prior_progress(cfg, step, max_steps)
    if hasattr(model.backbone, "set_branch_gate_prior_progress"):
        model.backbone.set_branch_gate_prior_progress(progress)


@torch.no_grad()
def evaluate(model: TokenSegmentationModel, loader, device: torch.device, cfg: dict[str, Any], num_classes: int) -> dict[str, Any]:
    model.eval()
    precision = str(cfg.get("training", {}).get("precision", "bf16"))
    total_loss = 0.0
    total_voxels = 0
    totals = {"val/dice": 0.0, "val/iou": 0.0, "val/foreground_recall": 0.0}
    structure_names = list(getattr(loader.dataset, "structure_names", []) or [])
    per_structure: dict[int, dict[str, float]] = {}
    per_structure_counts: dict[int, int] = {}
    aux_sums: dict[str, float] = {}
    aux_counts: dict[str, int] = {}
    aux_last: dict[str, Any] = {}
    per_structure_aux: dict[int, dict[str, float]] = {}
    per_structure_aux_counts: dict[int, dict[str, int]] = {}
    for batch_idx, batch in enumerate(loader):
        if batch_idx >= int(cfg.get("training", {}).get("eval_batches", 2)):
            break
        x, y, structure_id = _unpack_batch(batch)
        x = x.to(device, non_blocking=True)
        y = y.to(device, non_blocking=True)
        x = _apply_input_corruption(x, cfg)
        structure_id_device = structure_id.to(device, non_blocking=True) if structure_id is not None else None
        target = _downsample_labels(y, tuple(model.backbone.grid_shape))
        qmask = None
        if bool(cfg.get("training", {}).get("halo_masking", False)) and model.model_name in {"hypernsa", "hypernsa_s", "hypernsa_l", "hypernsa_lm"}:
            qmask = block_target_mask(tuple(model.backbone.grid_shape), tuple(model.backbone.block_shape), x.shape[0], device, step=batch_idx)
        with autocast_context(device, precision):
            logits, aux = model(x, query_disable_local_mask=qmask, return_aux=True, structure_id=structure_id_device)
            logits, target = _crop_to_target_grid(logits, target, cfg)
            loss, _ = _segmentation_loss(logits, target, cfg, num_classes)
        count = int(target.numel())
        total_loss += float(loss.item()) * count
        total_voxels += count
        metrics = _dice_iou(logits.float(), target, num_classes)
        batch_aux = aux_metrics(model, aux, target_mask=qmask)
        aux_last.update(batch_aux)
        for key, value in batch_aux.items():
            _accumulate_number(aux_sums, aux_counts, key, value)
        for key, value in metrics.items():
            totals[key] += value
        if structure_id is not None and x.shape[0] == 1:
            sid = int(structure_id.view(-1)[0].item())
            bucket = per_structure.setdefault(sid, {"dice": 0.0, "iou": 0.0, "foreground_recall": 0.0})
            bucket["dice"] += float(metrics["val/dice"])
            bucket["iou"] += float(metrics["val/iou"])
            bucket["foreground_recall"] += float(metrics["val/foreground_recall"])
            per_structure_counts[sid] = per_structure_counts.get(sid, 0) + 1
            aux_bucket = per_structure_aux.setdefault(sid, {})
            aux_count_bucket = per_structure_aux_counts.setdefault(sid, {})
            for key in LEARNING_DIAGNOSTIC_KEYS:
                value = batch_aux.get(key)
                if _is_finite_number(value):
                    aux_bucket[key] = aux_bucket.get(key, 0.0) + float(value)
                    aux_count_bucket[key] = aux_count_bucket.get(key, 0) + 1
    batches = max(1, min(len(loader), int(cfg.get("training", {}).get("eval_batches", 2))))
    out = {"val/loss": total_loss / max(1, total_voxels)}
    out.update({key: value / batches for key, value in totals.items()})
    if per_structure:
        dice_vals = []
        for sid, vals in sorted(per_structure.items()):
            count = max(1, per_structure_counts.get(sid, 0))
            name = structure_names[sid].lower() if sid < len(structure_names) else f"structure{sid}"
            dice = vals["dice"] / count
            out[f"val/dice_{name}"] = dice
            out[f"val/iou_{name}"] = vals["iou"] / count
            out[f"val/foreground_recall_{name}"] = vals["foreground_recall"] / count
            dice_vals.append(dice)
        out["val/macro_dice"] = float(sum(dice_vals) / max(1, len(dice_vals)))
    avg_aux = dict(aux_last)
    for key, value_sum in aux_sums.items():
        avg_aux[key] = value_sum / max(1, aux_counts.get(key, 0))
    if per_structure_aux:
        for sid, vals in sorted(per_structure_aux.items()):
            name = structure_names[sid].lower() if sid < len(structure_names) else f"structure{sid}"
            counts = per_structure_aux_counts.get(sid, {})
            for key, value_sum in vals.items():
                avg_aux[f"{key}_{name}"] = value_sum / max(1, counts.get(key, 0))
    out.update({f"attn/{k}": v for k, v in avg_aux.items()})
    return out


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    add_config_args(parser)
    args = parser.parse_args()
    cfg = load_config(args.config, args.override)
    phase = str(cfg.get("phase", "phase4a"))
    run_id = str(cfg.get("run_id", Path(args.config).stem if args.config else f"phase4a_seg_{int(time.time())}"))
    cfg.setdefault("wandb", {})
    cfg["wandb"]["tags"] = sorted(set((cfg["wandb"].get("tags") or []) + [phase, "real3d", "segmentation", str(cfg.get("model", {}).get("name", ""))]))
    seed = seed_everything(int(cfg.get("seed", 0)))
    raw_dir = Path("results/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{phase}_{run_id}.jsonl"
    if raw_path.exists():
        raw_path.unlink()
    resolved = write_resolved_config(cfg, raw_dir)
    context = write_run_context(cfg, raw_dir, command=" ".join(sys.argv))
    default_groups = {
        "phase4b": "04B_simplified_real3d",
        "phase4c": "04C_layout_aware_3d_claim",
        "phase4d": "04D_theory_impl_audit",
        "phase5a": "05A_claim_grade_3d_lm",
        "phase6a": "06A_allen_high_token_microscopy",
        "phase6b": "06B_allen_claim_grade_microscopy",
    }
    default_group = default_groups.get(phase, "04A_real_high_token_3d4d")
    run = init_wandb(cfg, mode=args.wandb_mode, group=args.wandb_group or cfg.get("wandb", {}).get("group") or default_group, outdir=raw_dir)
    status = "passed"
    try:
        device = select_device()
        train_loader, val_loader, meta = make_loaders(cfg)
        fields = phase_config_fields(cfg)
        fields["dataset_status"] = meta.get("dataset_status", fields.get("dataset_status", ""))
        cfg.setdefault("model", {})
        cfg["model"]["num_structures"] = int(meta.get("num_structures", cfg["model"].get("num_structures", 1)))
        backbone = build_backbone(cfg).to(device)
        model = TokenSegmentationModel(
            backbone,
            int(meta["num_classes"]),
            num_structures=int(meta.get("num_structures", 1)),
            structure_conditioning=str(cfg.get("model", {}).get("structure_conditioning", "none")),
            structure_conditioning_location=str(cfg.get("model", {}).get("structure_conditioning_location", "head_only")),
            segmentation_head=str(cfg.get("model", {}).get("segmentation_head", "linear")),
            monai_decoder_project_dim=int(cfg.get("model", {}).get("monai_decoder_project_dim", 32)),
            monai_decoder_features=tuple(int(x) for x in cfg.get("model", {}).get("monai_decoder_features", [32, 32, 64, 128, 256, 32])),
            monai_decoder_upsample=str(cfg.get("model", {}).get("monai_decoder_upsample", "deconv")),
            monai_decoder_raw_input_skip=bool(cfg.get("model", {}).get("monai_decoder_raw_input_skip", False)),
        ).to(device)
        audit_row = {
            **_runtime_model_audit(model, cfg, meta, device),
            **fields,
        }
        append_jsonl(raw_path, audit_row)
        run.log(audit_row, step=0)
        opt = torch.optim.AdamW(model.parameters(), lr=float(cfg.get("training", {}).get("lr", 2e-4)), weight_decay=float(cfg.get("training", {}).get("weight_decay", 1e-2)))
        max_steps = int(cfg.get("training", {}).get("max_steps", 20))
        _set_branch_gate_prior_progress(model, cfg, 0, max_steps)
        eval_every = int(cfg.get("training", {}).get("eval_every", max_steps))
        aux_every = int(cfg.get("training", {}).get("aux_every", 10))
        precision = str(cfg.get("training", {}).get("precision", "bf16"))
        use_atom_aux_loss = _atom_aux_loss_enabled(cfg)
        ckpt_dir = Path("results/checkpoints") / run_id
        ckpt_dir.mkdir(parents=True, exist_ok=True)
        best_dice = -1.0
        best_macro_dice = -1.0
        best_loss = float("inf")
        step = 0
        start = time.perf_counter()
        while step < max_steps:
            for batch in train_loader:
                if step >= max_steps:
                    break
                x, y, structure_id = _unpack_batch(batch)
                model.train()
                if device.type == "cuda":
                    torch.cuda.reset_peak_memory_stats(device)
                x = x.to(device, non_blocking=True)
                y = y.to(device, non_blocking=True)
                x = _apply_input_corruption(x, cfg)
                structure_id_device = structure_id.to(device, non_blocking=True) if structure_id is not None else None
                target = _downsample_labels(y, tuple(model.backbone.grid_shape))
                qmask = None
                if bool(cfg.get("training", {}).get("halo_masking", False)) and model.model_name in {"hypernsa", "hypernsa_s", "hypernsa_l", "hypernsa_lm"}:
                    qmask = block_target_mask(tuple(model.backbone.grid_shape), tuple(model.backbone.block_shape), x.shape[0], device, step=step)
                _set_branch_gate_prior_progress(model, cfg, step, max_steps)
                want_aux = use_atom_aux_loss or (
                    bool(cfg.get("training", {}).get("return_aux", True)) and (step % max(1, aux_every) == 0)
                )
                step_start = time.perf_counter()
                opt.zero_grad(set_to_none=True)
                with autocast_context(device, precision):
                    if want_aux:
                        logits, aux = model(x, query_disable_local_mask=qmask, return_aux=True, structure_id=structure_id_device)
                    else:
                        logits = model(x, query_disable_local_mask=qmask, return_aux=False, structure_id=structure_id_device)
                        aux = None
                    logits, target = _crop_to_target_grid(logits, target, cfg)
                    ce_loss, loss_parts = _segmentation_loss(logits, target, cfg, int(meta["num_classes"]))
                    atom_aux_loss = logits.new_tensor(0.0)
                    if use_atom_aux_loss:
                        if aux is None or "atom_aux_loss" not in aux:
                            raise RuntimeError("atom auxiliary loss is enabled, but attention aux did not contain atom_aux_loss")
                        atom_aux_loss = aux["atom_aux_loss"].to(logits.dtype)
                    loss = ce_loss + atom_aux_loss
                if not torch.isfinite(loss):
                    raise RuntimeError("nonfinite segmentation loss")
                loss.backward()
                gn = grad_norm(model.parameters())
                opt.step()
                step_ms = (time.perf_counter() - step_start) * 1000.0
                tokens = int(x.shape[0])
                for size, patch in zip(cfg["model"]["input_shape"], cfg["model"]["patch_shape"]):
                    tokens *= int(size) // int(patch)
                train_row = {
                    "kind": "train_step",
                    "status": "passed",
                    "run_id": run_id,
                    "dataset": meta["dataset"],
                    "dataset_status": meta.get("dataset_status", ""),
                    "split": "train",
                    "mode": "3d_segmentation",
                    "model": cfg["model"]["name"],
                    "ablation": cfg.get("ablation", "full"),
                    "seed": seed,
                    "step": step + 1,
                    "structure_id": int(structure_id.view(-1)[0].item()) if structure_id is not None and structure_id.numel() == 1 else "",
                    **fields,
                    "train/loss": float(loss.item()),
                    "train/lr": float(opt.param_groups[0]["lr"]),
                    "train/grad_norm": float(gn),
                    "train/step_time_ms": step_ms,
                    "train/throughput_samples_per_sec": float(x.shape[0] * 1000.0 / max(step_ms, 1e-6)),
                    "train/throughput_tokens_per_sec": float(tokens * 1000.0 / max(step_ms, 1e-6)),
                    "train/max_cuda_memory_gb": max_cuda_memory_gb(device),
                    "train/ce_loss": float(loss_parts["ce_loss"]),
                    "train/dice_loss": float(loss_parts["dice_loss"]),
                    "train/atom_aux_loss": float(atom_aux_loss.detach().float().item()),
                    **({f"attn/{k}": v for k, v in aux_metrics(model, aux, target_mask=qmask).items()} if aux is not None else {}),
                }
                append_jsonl(raw_path, train_row)
                run.log(train_row, step=step + 1)
                step += 1
                if step % eval_every == 0 or step == max_steps:
                    _set_branch_gate_prior_progress(model, cfg, step, max_steps)
                    val = evaluate(model, val_loader, device, cfg, int(meta["num_classes"]))
                    best_dice = max(best_dice, float(val["val/dice"]))
                    best_macro_dice = max(best_macro_dice, float(val.get("val/macro_dice", val["val/dice"])))
                    best_loss = min(best_loss, float(val["val/loss"]))
                    if float(val.get("val/macro_dice", val["val/dice"])) >= best_macro_dice:
                        torch.save(
                            {
                                "model": model.state_dict(),
                                "backbone": model.backbone.state_dict(),
                                "config": cfg,
                                "step": step,
                                "best_val_macro_dice": best_macro_dice,
                                "best_val_dice": best_dice,
                            },
                            ckpt_dir / "best.pt",
                        )
                    eval_row = {
                        "kind": "eval",
                        "status": "passed",
                        "run_id": run_id,
                        "dataset": meta["dataset"],
                        "dataset_status": meta.get("dataset_status", ""),
                        "split": "val",
                        "mode": "3d_segmentation",
                        "model": cfg["model"]["name"],
                        "ablation": cfg.get("ablation", "full"),
                        "seed": seed,
                        "step": step,
                        **fields,
                        **val,
                        "best_val_dice": best_dice,
                        "best_val_macro_dice": best_macro_dice,
                    }
                    append_jsonl(raw_path, eval_row)
                    run.log(eval_row, step=step)
        _set_branch_gate_prior_progress(model, cfg, max_steps, max_steps)
        final = evaluate(model, val_loader, device, cfg, int(meta["num_classes"]))
        final_macro = float(final.get("val/macro_dice", final["val/dice"]))
        if final_macro > best_macro_dice:
            best_macro_dice = final_macro
            best_dice = max(best_dice, float(final["val/dice"]))
            torch.save(
                {
                    "model": model.state_dict(),
                    "backbone": model.backbone.state_dict(),
                    "config": cfg,
                    "step": step,
                    "best_val_macro_dice": best_macro_dice,
                    "best_val_dice": best_dice,
                },
                ckpt_dir / "best.pt",
            )
        torch.save({"model": model.state_dict(), "backbone": model.backbone.state_dict(), "config": cfg}, ckpt_dir / "last.pt")
        summary = {
            "kind": "summary",
            "status": status,
            "run_id": run_id,
            "dataset": meta["dataset"],
            "dataset_status": meta.get("dataset_status", ""),
            "mode": "3d_segmentation",
            "model": cfg["model"]["name"],
            "ablation": cfg.get("ablation", "full"),
            "seed": seed,
            **fields,
            "parameter_count": int(sum(p.numel() for p in model.parameters())),
            "elapsed_seconds": time.perf_counter() - start,
            "final_val_dice": float(final["val/dice"]),
            "best_val_dice": float(max(best_dice, final["val/dice"])),
            "best_val_macro_dice": float(best_macro_dice),
            "final_val_iou": float(final["val/iou"]),
            "final_foreground_recall": float(final["val/foreground_recall"]),
            "final_loss": float(final["val/loss"]),
            "best_loss": float(min(best_loss, final["val/loss"])),
            "max_cuda_memory_gb": max_cuda_memory_gb(device),
            **{k.replace("attn/", ""): v for k, v in final.items() if k.startswith("attn/")},
        }
        append_jsonl(raw_path, summary)
        run.summary.update(summary)
        artifact_paths = [resolved, context, raw_path, ckpt_dir / "last.pt", meta.get("manifest", "")]
        if (ckpt_dir / "best.pt").exists():
            artifact_paths.append(ckpt_dir / "best.pt")
        log_artifact_files(run, name=f"{run_id}_{phase}_3d_segmentation", artifact_type=f"{phase}_run", paths=artifact_paths)
    except Exception as exc:
        status = "failed"
        summary = {"kind": "summary", "status": status, "run_id": run_id, "mode": "3d_segmentation", "error": str(exc)}
        append_jsonl(raw_path, summary)
        run.summary.update(summary)
        print(json.dumps(summary, indent=2), file=sys.stderr)
    run.finish()
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
