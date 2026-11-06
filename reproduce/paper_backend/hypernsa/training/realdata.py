from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any

import torch
from torch import Tensor, nn
from torch.utils.data import DataLoader, Subset
import torch.nn.functional as F

from hypernsa.attention.hypernsa_morton import HyperNSABlock
from hypernsa.evaluation.kernel_metrics import compute_grouped_load_metrics, route_entropy
from hypernsa.models.realdata import RealDataBackbone, RealDataClassifier, patch_targets
from hypernsa.data.medmnist import make_medmnist_dataset, medmnist_num_classes


def select_device() -> torch.device:
    if not torch.cuda.is_available():
        return torch.device("cpu")
    if torch.cuda.device_count() > 1:
        torch.cuda.set_device(1)
        return torch.device("cuda:1")
    torch.cuda.set_device(0)
    return torch.device("cuda:0")


def autocast_context(device: torch.device, precision: str):
    if device.type == "cuda" and precision in {"bf16", "bfloat16"} and torch.cuda.is_bf16_supported():
        return torch.autocast(device_type="cuda", dtype=torch.bfloat16)
    if device.type == "cuda" and precision in {"fp16", "float16"}:
        return torch.autocast(device_type="cuda", dtype=torch.float16)
    return torch.autocast(device_type=device.type, enabled=False)


def _subset_if_needed(dataset, max_samples: int | None, seed: int, split: str):
    if max_samples is None or max_samples <= 0 or max_samples >= len(dataset):
        return dataset
    generator = torch.Generator().manual_seed(int(seed) + {"train": 0, "val": 17, "test": 31}.get(split, 0))
    indices = torch.randperm(len(dataset), generator=generator)[: int(max_samples)].tolist()
    return Subset(dataset, indices)


def _manifest_path_for(name: str) -> str:
    mapping = {
        "tiny_imagenet": "data_manifests/tiny_imagenet.json",
        "imagenette": "data_manifests/imagenette.json",
        "imagenet100": "data_manifests/imagenet100.json",
        "medmnist": "data_manifests/medmnist.json",
        "msd": "data_manifests/msd.json",
    }
    return mapping.get(name, "")


def make_loaders(cfg: dict[str, Any]) -> tuple[DataLoader, DataLoader, dict[str, Any]]:
    data = cfg["data"]
    root = Path(data.get("root", "data")).expanduser()
    name = str(data["dataset"]).lower()
    seed = int(cfg.get("seed", 0))
    max_train = int(data.get("max_train_samples", 256))
    max_val = int(data.get("max_val_samples", 128))
    if name in {
        "pathmnist",
        "organamnist",
        "bloodmnist",
        "dermamnist",
        "organmnist3d",
        "nodulemnist3d",
        "vesselmnist3d",
        "synapsemnist3d",
        "adrenalmnist3d",
        "fracturemnist3d",
    }:
        spatial_size = data.get("spatial_size")
        train = make_medmnist_dataset(name, "train", root, download=bool(data.get("download", False)), max_samples=max_train, seed=seed, spatial_size=spatial_size)
        val = make_medmnist_dataset(name, "val", root, download=bool(data.get("download", False)), max_samples=max_val, seed=seed, spatial_size=spatial_size)
        meta = {"dataset": name, "dataset_status": "medmnist", "num_classes": medmnist_num_classes(name), "root": str(root), "manifest": _manifest_path_for("medmnist")}
    elif name == "tiny_imagenet":
        from hypernsa.data.tiny_imagenet import TinyImageNetDataset

        size = int(data.get("image_size", data.get("spatial_size", 224)))
        train = TinyImageNetDataset(root, "train", size=size, max_samples=max_train, seed=seed)
        val = TinyImageNetDataset(root, "val", size=size, max_samples=max_val, seed=seed)
        meta = {"dataset": name, "dataset_status": "open_proxy", "num_classes": train.num_classes, "root": str(root), "manifest": _manifest_path_for(name)}
    elif name == "imagenette":
        from hypernsa.data.imagenette import ImagenetteDataset

        size = int(data.get("image_size", data.get("spatial_size", 224)))
        train = ImagenetteDataset(root, "train", size=size, max_samples=max_train, seed=seed)
        val = ImagenetteDataset(root, "val", size=size, max_samples=max_val, seed=seed)
        meta = {"dataset": name, "dataset_status": "open_proxy", "num_classes": train.num_classes, "root": str(root), "manifest": _manifest_path_for(name)}
    elif name == "imagenet100":
        from hypernsa.data.imagenet import ImageNet100Dataset

        image_root = Path(data.get("imagenet_root", root)).expanduser()
        size = int(data.get("image_size", data.get("spatial_size", 224)))
        train = ImageNet100Dataset(image_root, "train", size=size, max_samples=max_train, seed=seed)
        val = ImageNet100Dataset(image_root, "val", size=size, max_samples=max_val, seed=seed)
        meta = {"dataset": name, "dataset_status": "imagenet100", "num_classes": train.num_classes, "root": str(image_root), "manifest": _manifest_path_for(name)}
    elif name in {"msd", "msd_task09_spleen", "msd_task02_heart"}:
        from hypernsa.data.msd import MSDPreprocessedSegmentationDataset

        manifest = Path(data.get("manifest", _manifest_path_for("msd"))).expanduser()
        train = MSDPreprocessedSegmentationDataset(manifest, "train", max_samples=max_train, seed=seed)
        val = MSDPreprocessedSegmentationDataset(manifest, "val", max_samples=max_val, seed=seed)
        meta = {
            "dataset": name,
            "dataset_status": "real3d",
            "num_classes": train.num_classes,
            "root": str(root),
            "manifest": str(manifest),
            "task": train.task,
        }
    elif name in {"modelnet40", "modelnet40_voxel"}:
        from hypernsa.data.modelnet40 import ModelNet40VoxelDataset

        manifest = Path(data["manifest"]).expanduser()
        train = ModelNet40VoxelDataset(manifest, "train", max_samples=max_train, seed=seed)
        val = ModelNet40VoxelDataset(manifest, "val", max_samples=max_val, seed=seed)
        meta = {
            "dataset": name,
            "dataset_status": "open_3d_classification",
            "num_classes": train.num_classes,
            "root": str(root),
            "manifest": str(manifest),
            "task": "voxel_classification",
        }
    elif name in {"allen", "allen_cell", "allen_cell_tomm20", "allen_cell_lmnb1", "allen_multistructure"}:
        from hypernsa.data.allen import AllenMultiStructurePreprocessedSegmentationDataset, AllenPreprocessedSegmentationDataset

        manifest = Path(data["manifest"]).expanduser()
        manifest_meta = json.loads(manifest.read_text())
        dataset_cls = AllenMultiStructurePreprocessedSegmentationDataset if bool(manifest_meta.get("multistructure", False)) else AllenPreprocessedSegmentationDataset
        train = dataset_cls(manifest, "train", max_samples=max_train, seed=seed)
        val = dataset_cls(manifest, "val", max_samples=max_val, seed=seed)
        meta = {
            "dataset": name,
            "dataset_status": "real3d_microscopy",
            "num_classes": train.num_classes,
            "root": str(root),
            "manifest": str(manifest),
            "task": train.task,
            "structure_name": train.structure_name,
            "structure_names": getattr(train, "structure_names", []),
            "num_structures": int(getattr(train, "num_structures", 1)),
            "multistructure": bool(manifest_meta.get("multistructure", False)),
        }
    else:
        raise ValueError(f"unsupported dataset for real-data loader: {name}")
    batch_size = int(data.get("batch_size", 16))
    workers = int(data.get("num_workers", 0))
    return (
        DataLoader(train, batch_size=batch_size, shuffle=True, num_workers=workers, drop_last=bool(data.get("drop_last", False))),
        DataLoader(val, batch_size=batch_size, shuffle=False, num_workers=workers, drop_last=False),
        meta,
    )


_MODEL_KEYS_USED_BY_TRAINER = {
    "structure_conditioning",
    "structure_conditioning_location",
    "num_structures",
    "segmentation_head",
    "monai_decoder_project_dim",
    "monai_decoder_features",
    "monai_decoder_upsample",
    "monai_decoder_raw_input_skip",
}


def activation_checkpointing_mode(value: Any) -> str:
    if isinstance(value, bool):
        return "full" if value else "none"
    if value is None:
        return "none"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "full" if bool(value) else "none"
    text = str(value).strip().lower().replace("-", "_")
    aliases = {
        "": "none",
        "0": "none",
        "false": "none",
        "no": "none",
        "off": "none",
        "none": "none",
        "1": "full",
        "true": "full",
        "yes": "full",
        "on": "full",
        "attention": "full",
        "pack3d": "full",
        "full": "full",
        "branch": "branch",
        "branches": "branch",
        "branch_outputs": "branch",
        "local": "local",
        "local_attention": "local",
        "query_tile": "query_tile",
        "query_tiled": "query_tile",
    }
    if text not in aliases:
        raise ValueError(
            "activation_checkpointing must be one of "
            "none/off/false, full/on/true, branch, local, or query_tile"
        )
    return aliases[text]


def model_kwargs(cfg: dict[str, Any], num_classes: int | None = None) -> dict[str, Any]:
    m = cfg["model"]
    removed_keys = {
        "talking_heads_mode": "none",
        "local_multiscale_filter": "none",
        "conv_pyramid_cross_attention": "none",
        "residual_stream_mode": "none",
        "coarse_attention_backend": "sdpa",
    }
    unsupported = []
    for key, default in removed_keys.items():
        if key in m and str(m.get(key)) != str(default):
            unsupported.append(key)
    unsupported.extend(str(key) for key in m if str(key).startswith("layer_memory"))
    if unsupported:
        raise ValueError(
            "Removed experimental options are not supported in the cleaned active method path: "
            f"{sorted(unsupported)}"
        )
    allowed_keys = {
        "name",
        "input_shape",
        "in_channels",
        "patch_shape",
        "dim",
        "depth",
        "heads",
        "kv_heads",
        "dim_head",
        "block_shape",
        "local_radius",
        "num_summary_atoms",
        "num_selected_blocks",
        "residual_weight",
        "distance_weight",
        "use_triton_kernel",
        "separate_branch_kv",
        "route_select_grad",
        "packed_branch_kv_projection",
        "skip_disabled_local_branch",
        "activation_checkpointing",
        "checkpoint_local_attention",
        "local_attention_backend",
        "local_attention_block_n",
        "branch_output_fusion",
        "coarse_attention_backend",
        "coarse_summary_pool_size",
        "layout",
        "layout_mode",
        "route_score_mode",
        "route_backend",
        "route_block_q",
        "route_block_c",
        "route_materialize_scores_in_aux",
        "route_shape_penalty_weight",
        "route_center_distance_weight",
        "route_distance_normalization",
        "allow_raw_distance_on_probability_route",
        "branch_gate_mode",
        "atom_assignment_mode",
        "route_residual_mode",
        "atom_balance_loss_weight",
        "atom_entropy_loss_weight",
        "atom_orthogonality_loss_weight",
        "atom_temperature",
        "full_layer_execution",
        "query_tile_size",
        "query_tile_checkpoint",
        "route_granularity",
        "route_share_tile_size",
        "enabled_branches",
        "branch_output_norm",
        "branch_layer_scale",
        "branch_layer_scale_init",
        "branch_mixer_mode",
        "branch_gate_bias_init",
        "branch_gate_prior_schedule",
        "branch_gate_prior_start",
        "branch_gate_prior_end",
        "branch_gate_prior_steps",
        "selected_mixing_mode",
        "validate_triton_outputs",
        "window_adapter_hidden",
        "pos_encoding",
        "rotary_base",
        "rotary_coordinate_mode",
        "rotary_axis_scales",
        "rotary_axis_pair_allocation",
        "learned_low_rank_pe_rank",
        "coordinate_fourier_bands",
        "coordinate_fourier_hidden",
        "compressed_rope_mode",
        *removed_keys.keys(),
        *_MODEL_KEYS_USED_BY_TRAINER,
    }
    unknown_keys = sorted(str(key) for key in m if str(key) not in allowed_keys and not str(key).startswith("layer_memory"))
    if unknown_keys:
        raise ValueError(f"Unsupported or ignored model keys: {unknown_keys}")
    has_activation_checkpointing = "activation_checkpointing" in m
    checkpoint_mode = activation_checkpointing_mode(m.get("activation_checkpointing", "none"))
    checkpoint_local_default = checkpoint_mode in {"full", "local"}
    branch_output_fusion_default = "checkpointed" if checkpoint_mode in {"full", "branch"} else "standard"
    query_tile_checkpoint_default = checkpoint_mode in {"full", "query_tile"}
    kwargs = {
        "model_name": str(m["name"]),
        "input_shape": tuple(int(x) for x in m["input_shape"]),
        "in_channels": int(m.get("in_channels", 1)),
        "patch_shape": tuple(int(x) for x in m["patch_shape"]),
        "dim": int(m.get("dim", int(m.get("heads", 8)) * int(m.get("dim_head", 64)))),
        "depth": int(m.get("depth", 1)),
        "heads": int(m.get("heads", 8)),
        "kv_heads": int(m.get("kv_heads", 2)),
        "dim_head": int(m.get("dim_head", 64)),
        "block_shape": tuple(int(x) for x in m["block_shape"]),
        "local_radius": tuple(int(x) for x in m.get("local_radius", [1] * len(m["input_shape"]))),
        "num_summary_atoms": int(m.get("num_summary_atoms", 2)),
        "num_selected_blocks": int(m.get("num_selected_blocks", 2)),
        "residual_weight": float(m.get("residual_weight", 0.25)),
        "distance_weight": float(m.get("distance_weight", 0.10)),
        "use_triton_kernel": bool(m.get("use_triton_kernel", False)),
        "separate_branch_kv": bool(m.get("separate_branch_kv", True)),
        "route_select_grad": bool(m.get("route_select_grad", False)),
        "packed_branch_kv_projection": bool(m.get("packed_branch_kv_projection", True)),
        "skip_disabled_local_branch": bool(m.get("skip_disabled_local_branch", True)),
        "checkpoint_local_attention": bool(checkpoint_local_default if has_activation_checkpointing else m.get("checkpoint_local_attention", False)),
        "local_attention_backend": str(m.get("local_attention_backend", "torch")),
        "local_attention_block_n": int(m.get("local_attention_block_n", 16)),
        "branch_output_fusion": str(branch_output_fusion_default if has_activation_checkpointing else m.get("branch_output_fusion", "standard")),
        "coarse_attention_backend": "sdpa",
        "coarse_summary_pool_size": int(m.get("coarse_summary_pool_size", 1)),
        "layout": str(m.get("layout", m.get("layout_mode", "native"))),
        "route_score_mode": str(m.get("route_score_mode", "logsumexp_logits_current")),
        "route_backend": str(m.get("route_backend", "torch_full")),
        "route_block_q": int(m.get("route_block_q", 16)),
        "route_block_c": int(m.get("route_block_c", 32)),
        "route_materialize_scores_in_aux": bool(m.get("route_materialize_scores_in_aux", True)),
        "route_shape_penalty_weight": float(m.get("route_shape_penalty_weight", 0.0)),
        "route_center_distance_weight": m.get("route_center_distance_weight"),
        "route_distance_normalization": str(m.get("route_distance_normalization", "raw")),
        "allow_raw_distance_on_probability_route": bool(m.get("allow_raw_distance_on_probability_route", False)),
        "branch_gate_mode": str(m.get("branch_gate_mode", "softmax")),
        "atom_assignment_mode": str(m.get("atom_assignment_mode", "current_encode_only")),
        "route_residual_mode": str(m.get("route_residual_mode", "key_residual")),
        "atom_balance_loss_weight": float(m.get("atom_balance_loss_weight", 0.0)),
        "atom_entropy_loss_weight": float(m.get("atom_entropy_loss_weight", 0.0)),
        "atom_orthogonality_loss_weight": float(m.get("atom_orthogonality_loss_weight", 0.0)),
        "atom_temperature": float(m.get("atom_temperature", 1.0)),
        "full_layer_execution": str(m.get("full_layer_execution", "full")),
        "query_tile_size": int(m.get("query_tile_size", 0)),
        "query_tile_checkpoint": bool(query_tile_checkpoint_default if has_activation_checkpointing else m.get("query_tile_checkpoint", False)),
        "route_granularity": str(m.get("route_granularity", "token_exact")),
        "route_share_tile_size": int(m.get("route_share_tile_size", 16)),
        "enabled_branches": tuple(m.get("enabled_branches", ["local", "compressed", "selected"])),
        "branch_output_norm": str(m.get("branch_output_norm", "none")),
        "branch_layer_scale": bool(m.get("branch_layer_scale", False)),
        "branch_layer_scale_init": m.get("branch_layer_scale_init", 1.0),
        "branch_mixer_mode": str(m.get("branch_mixer_mode", "gated_sum")),
        "branch_gate_bias_init": m.get("branch_gate_bias_init", 0.0),
        "branch_gate_prior_schedule": str(m.get("branch_gate_prior_schedule", "none")),
        "branch_gate_prior_start": m.get("branch_gate_prior_start", 0.0),
        "branch_gate_prior_end": m.get("branch_gate_prior_end", 0.0),
        "selected_mixing_mode": str(m.get("selected_mixing_mode", "standard")),
        "validate_triton_outputs": bool(m.get("validate_triton_outputs", False)),
        "window_adapter_hidden": int(m.get("window_adapter_hidden", 256) or 256),
        "pos_encoding": str(m.get("pos_encoding", "learned_full")),
        "rotary_base": float(m.get("rotary_base", 10000.0) or 10000.0),
        "rotary_coordinate_mode": str(m.get("rotary_coordinate_mode", "raw_grid")),
        "rotary_axis_scales": tuple(float(x) for x in m.get("rotary_axis_scales", [])) if m.get("rotary_axis_scales") else None,
        "rotary_axis_pair_allocation": str(m.get("rotary_axis_pair_allocation", "balanced")),
        "learned_low_rank_pe_rank": int(m.get("learned_low_rank_pe_rank", 8) or 8),
        "coordinate_fourier_bands": int(m.get("coordinate_fourier_bands", 16) or 16),
        "coordinate_fourier_hidden": int(m.get("coordinate_fourier_hidden", 128) or 128),
        "compressed_rope_mode": str(m.get("compressed_rope_mode", "token_before_compression")),
    }
    if num_classes is not None:
        return {"num_classes": int(num_classes), **kwargs}
    return kwargs


def build_classifier(cfg: dict[str, Any], num_classes: int) -> RealDataClassifier:
    return RealDataClassifier(**model_kwargs(cfg, num_classes=num_classes))


def build_backbone(cfg: dict[str, Any]) -> RealDataBackbone:
    return RealDataBackbone(**model_kwargs(cfg))


def first_hyper_attn(model: nn.Module):
    backbone = getattr(model, "backbone", model)
    for block in getattr(backbone, "blocks", []):
        if isinstance(block, HyperNSABlock):
            return block.attn
    return None


def block_target_mask(grid_shape: tuple[int, ...], block_shape: tuple[int, ...], batch: int, device: torch.device, *, step: int = 0) -> Tensor:
    mask = torch.zeros(batch, *grid_shape, dtype=torch.bool, device=device)
    starts = []
    for dim, block in zip(grid_shape, block_shape):
        max_start = max(dim - block, 0)
        starts.append(((step * block) % (max_start + 1)) if max_start else 0)
    slices = tuple(slice(s, min(s + b, g)) for s, b, g in zip(starts, block_shape, grid_shape))
    mask[(slice(None),) + slices] = True
    return mask


def flatten_target_mask(mask: Tensor) -> Tensor:
    return mask.reshape(mask.shape[0], -1)


def _safe_float(value: Any) -> float:
    try:
        if isinstance(value, torch.Tensor):
            value = value.detach().float().item()
        value = float(value)
        return value if math.isfinite(value) else float("nan")
    except Exception:
        return float("nan")


def representation_metrics(emb: Tensor) -> dict[str, float]:
    z = emb.detach().float()
    if z.ndim > 2:
        z = z.reshape(z.shape[0], -1)
    var = z.var(dim=0, unbiased=False)
    zc = z - z.mean(dim=0, keepdim=True)
    cov = (zc.T @ zc) / max(1, z.shape[0] - 1)
    diag = torch.diag(cov)
    offdiag = cov - torch.diag_embed(diag)
    return {
        "embedding_variance_mean": _safe_float(var.mean().item()),
        "embedding_variance_min": _safe_float(var.min().item()),
        "covariance_offdiag_mean": _safe_float(offdiag.abs().mean().item()),
        "collapse_score": _safe_float(1.0 / (var.mean().item() + 1e-6)),
    }


def aux_metrics(model: nn.Module, aux: dict[str, Any] | None, *, target_mask: Tensor | None = None) -> dict[str, Any]:
    if not aux:
        return {
            "backend_requested": "dense_sdpa" if getattr(model, "model_name", "") == "dense" else getattr(model, "model_name", ""),
            "backend_actual": "dense_sdpa" if getattr(model, "model_name", "") == "dense" else getattr(model, "model_name", ""),
            "fallback_reason": "",
        }
    attn = first_hyper_attn(model)
    gates = aux.get("gates")
    packed_target = None
    if target_mask is not None and attn is not None:
        packed_target = attn._pack_bool_mask(target_mask.detach()).to(gates.device if gates is not None else target_mask.device)
    if gates is not None and getattr(gates, "numel", lambda: 0)() > 0:
        g = gates.detach().float()
        if packed_target is not None and bool(packed_target.any()):
            active = packed_target[:, None, :, None].expand(g.shape[0], g.shape[1], g.shape[2], g.shape[3])
            g_sel = g[active].reshape(-1, 3)
        else:
            g_sel = g.reshape(-1, 3)
        gate_mean = g_sel.mean(dim=0)
        gate_entropy = -(g_sel * torch.log(g_sel.clamp_min(1e-12))).sum(dim=-1).mean()
    else:
        gate_mean = torch.tensor([float("nan")] * 3)
        gate_entropy = torch.tensor(float("nan"))
    out = {
        "backend_requested": aux.get("backend_requested", ""),
        "backend_actual": aux.get("backend_actual", ""),
        "fallback_reason": aux.get("fallback_reason", ""),
        "route_backend_actual": aux.get("route_backend_actual", ""),
        "route_fallback_reason": aux.get("route_fallback_reason", ""),
        "gate_local_mean": _safe_float(gate_mean[0].item()),
        "gate_compressed_mean": _safe_float(gate_mean[1].item()),
        "gate_selected_mean": _safe_float(gate_mean[2].item()),
        "gate_entropy_mean": _safe_float(gate_entropy.item()),
        "route_entropy_mean": _safe_float(route_entropy(aux["route_scores"])) if "route_scores" in aux else float("nan"),
        "compression_residual_mean": float(aux["compression_residual"].float().mean().item()) if "compression_residual" in aux else float("nan"),
        "compression_residual_p90": float(torch.quantile(aux["compression_residual"].float().flatten(), 0.9).item()) if "compression_residual" in aux else float("nan"),
        "route_score_mode": aux.get("route_score_mode", ""),
        "route_distance_normalization": aux.get("route_distance_normalization", ""),
        "route_distance_units": aux.get("route_distance_units", ""),
        "branch_gate_mode": aux.get("branch_gate_mode", ""),
        "branch_gate_prior_schedule": aux.get("branch_gate_prior_schedule", ""),
        "branch_gate_prior_progress": _safe_float(aux.get("branch_gate_prior_progress", float("nan"))),
        "branch_gate_prior_local": _safe_float(aux.get("branch_gate_prior_local", float("nan"))),
        "branch_gate_prior_compressed": _safe_float(aux.get("branch_gate_prior_compressed", float("nan"))),
        "branch_gate_prior_selected": _safe_float(aux.get("branch_gate_prior_selected", float("nan"))),
        "local_attention_backend_requested": aux.get("local_attention_backend_requested", ""),
        "local_attention_backend_actual": aux.get("local_attention_backend_actual", ""),
        "local_attention_fallback_reason": aux.get("local_attention_fallback_reason", ""),
        "branch_output_fusion": aux.get("branch_output_fusion", ""),
        "branch_output_norm": aux.get("branch_output_norm", ""),
        "branch_layer_scale_enabled": bool(aux.get("branch_layer_scale_enabled", False)),
        "branch_layer_scale_local_mean": _safe_float(aux.get("branch_layer_scale_local_mean", float("nan"))),
        "branch_layer_scale_compressed_mean": _safe_float(aux.get("branch_layer_scale_compressed_mean", float("nan"))),
        "branch_layer_scale_selected_mean": _safe_float(aux.get("branch_layer_scale_selected_mean", float("nan"))),
        "branch_mixer_mode": aux.get("branch_mixer_mode", ""),
        "branch_mixer_mode_effective": aux.get("branch_mixer_mode_effective", ""),
        "selected_mixing_mode": aux.get("selected_mixing_mode", ""),
        "selected_mixing_mode_effective": aux.get("selected_mixing_mode_effective", ""),
        "coarse_summary_pool_size": _safe_float(aux.get("coarse_summary_pool_size", 1)),
        "full_layer_execution": aux.get("full_layer_execution", ""),
        "query_tile_size": _safe_float(aux.get("query_tile_size", 0)),
        "query_tile_checkpoint": bool(aux.get("query_tile_checkpoint", False)),
        "route_granularity": aux.get("route_granularity", ""),
        "route_share_tile_size": _safe_float(aux.get("route_share_tile_size", 0)),
        "route_sharing_factor": _safe_float(aux.get("route_sharing_factor", 1.0)),
        "enabled_branches": aux.get("enabled_branches", ""),
        "branch_output_checkpoint_active": bool(aux.get("branch_output_checkpoint_active", False)),
        "gate_sum_mean": _safe_float(aux.get("gate_sum_mean", float("nan"))),
        "local_output_norm": _safe_float(aux.get("local_output_norm", float("nan"))),
        "compressed_output_norm": _safe_float(aux.get("compressed_output_norm", float("nan"))),
        "selected_output_norm": _safe_float(aux.get("selected_output_norm", float("nan"))),
        "local_post_output_norm": _safe_float(aux.get("local_post_output_norm", float("nan"))),
        "compressed_post_output_norm": _safe_float(aux.get("compressed_post_output_norm", float("nan"))),
        "selected_post_output_norm": _safe_float(aux.get("selected_post_output_norm", float("nan"))),
        "atom_assignment_mode": aux.get("atom_assignment_mode", ""),
        "atom_aux_loss": _safe_float(aux.get("atom_aux_loss", 0.0)),
        "atom_balance_loss": _safe_float(aux.get("atom_balance_loss", 0.0)),
        "atom_entropy_loss": _safe_float(aux.get("atom_entropy_loss", 0.0)),
        "atom_orthogonality_loss": _safe_float(aux.get("atom_orthogonality_loss", 0.0)),
        "atom_assignment_entropy_mean": _safe_float(aux.get("atom_assignment_entropy_mean", 0.0)),
        "atom_effective_count": _safe_float(aux.get("atom_effective_count", 1.0)),
        "atom_balance_mean": _safe_float(aux.get("atom_balance_mean", 1.0)),
        "atom_cosine_abs_offdiag": _safe_float(aux.get("atom_cosine_abs_offdiag", 0.0)),
        "atom_balance_loss_weight": _safe_float(aux.get("atom_balance_loss_weight", 0.0)),
        "atom_entropy_loss_weight": _safe_float(aux.get("atom_entropy_loss_weight", 0.0)),
        "atom_orthogonality_loss_weight": _safe_float(aux.get("atom_orthogonality_loss_weight", 0.0)),
        "atom_temperature": _safe_float(aux.get("atom_temperature", 1.0)),
        "route_residual_mode": aux.get("route_residual_mode", ""),
        "route_probability_sum_error": _safe_float(aux.get("route_probability_sum_error", 0.0)),
        "compressed_attention_mass_entropy": _safe_float(aux.get("compressed_attention_mass_entropy", 0.0)),
    }
    if target_mask is not None:
        out["local_disabled_fraction"] = float(target_mask.float().mean().item())
    if attn is not None and "selected_block_indices" in aux:
        selected = aux["selected_block_indices"].detach()
        sel_mask = aux["selected_block_mask"].detach()
        out.update(
            compute_grouped_load_metrics(
                selected,
                sel_mask,
                query_heads_per_kv=attn.num_grouped_queries,
                block_volume=attn.block_volume,
            )
        )
        out["selected_tokens_per_query"] = float(sel_mask.float().sum(dim=-1).mean().item() * attn.block_volume)
        out["compressed_tokens_per_query"] = float(attn.num_blocks * attn.num_summary_atoms)
        out["local_tokens_per_query"] = float(attn.local_neighbor_mask.float().sum(dim=-1).mean().item())
        centers = attn.block_centers.to(selected.device).float()
        coords = attn.coords_packed.to(selected.device).float()
        idx = selected.clamp_min(0)
        chosen_centers = centers[idx]
        query_coords = coords.view(1, 1, attn.num_tokens_padded, 1, attn.ndim)
        dist = ((chosen_centers - query_coords) ** 2).sum(dim=-1).sqrt()
        active_dist = dist[sel_mask]
        out["selected_block_distance_mean"] = float(active_dist.mean().item()) if active_dist.numel() else float("nan")
        out["selected_block_distance_p90"] = float(torch.quantile(active_dist.float(), 0.9).item()) if active_dist.numel() else float("nan")
        if "compression_residual" in aux:
            residual = aux["compression_residual"].detach().float()
            freq = torch.zeros_like(residual)
            for b in range(selected.shape[0]):
                for g in range(selected.shape[1]):
                    active = selected[b, g][sel_mask[b, g]]
                    if active.numel():
                        freq[b, g].scatter_add_(0, active.long(), torch.ones_like(active, dtype=freq.dtype))
            r = residual.flatten()
            f = freq.flatten()
            if r.numel() > 1 and float(f.std().item()) > 1e-8 and float(r.std().item()) > 1e-8:
                out["residual_selection_correlation"] = float(torch.corrcoef(torch.stack([r, f]))[0, 1].item())
            else:
                out["residual_selection_correlation"] = 0.0
    return out


def grad_norm(parameters) -> float:
    total = 0.0
    for p in parameters:
        if p.grad is not None:
            total += float(p.grad.detach().float().norm().item() ** 2)
    return math.sqrt(total)


def max_cuda_memory_gb(device: torch.device) -> float:
    if device.type != "cuda":
        return 0.0
    return float(torch.cuda.max_memory_allocated(device) / (1024**3))


def append_jsonl(path: str | Path, row: dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def phase_config_fields(cfg: dict[str, Any]) -> dict[str, Any]:
    model = cfg.get("model", {})
    data = cfg.get("data", {})
    training = cfg.get("training", {})
    corruption = training.get("input_corruption", {}) or {}
    grid_shape = tuple(int(s) // int(p) for s, p in zip(model.get("input_shape", []), model.get("patch_shape", [])))
    block_shape = tuple(int(x) for x in model.get("block_shape", []))
    block_volume = math.prod(block_shape) if block_shape else ""
    heads = int(model.get("heads", 0) or 0)
    kv_heads = int(model.get("kv_heads", 0) or 0)
    has_activation_checkpointing = "activation_checkpointing" in model
    ckpt_mode = activation_checkpointing_mode(model.get("activation_checkpointing", "none"))
    checkpoint_local_effective = ckpt_mode in {"full", "local"} if has_activation_checkpointing else bool(model.get("checkpoint_local_attention", False))
    branch_output_fusion_effective = (
        "checkpointed"
        if has_activation_checkpointing and ckpt_mode in {"full", "branch"}
        else ("standard" if has_activation_checkpointing else str(model.get("branch_output_fusion", "standard")))
    )
    query_tile_checkpoint_effective = ckpt_mode in {"full", "query_tile"} if has_activation_checkpointing else bool(model.get("query_tile_checkpoint", False))
    return {
        "dataset": str(data.get("dataset", "")),
        "dataset_status": str(data.get("dataset_status", cfg.get("dataset_status", ""))),
        "training_steps": int(training.get("max_steps", 0) or 0),
        "matched_compute_group": str(cfg.get("matched_compute_group", "")),
        "input_resolution": "x".join(map(str, model.get("input_shape", []))),
        "patch_size": "x".join(map(str, model.get("patch_shape", []))),
        "grid_shape": "x".join(map(str, grid_shape)),
        "target_grid_shape": "x".join(map(str, training.get("target_grid_shape", []))),
        "block_shape": "x".join(map(str, block_shape)),
        "heads": heads,
        "kv_heads": kv_heads,
        "query_heads_per_kv": heads // kv_heads if heads and kv_heads else "",
        "dim_head": int(model.get("dim_head", 0) or 0),
        "num_summary_atoms": int(model.get("num_summary_atoms", 0) or 0),
        "num_selected_blocks": int(model.get("num_selected_blocks", 0) or 0),
        "residual_weight": float(model.get("residual_weight", 0.0) or 0.0),
        "distance_weight": float(model.get("distance_weight", 0.0) or 0.0),
        "route_select_grad": bool(model.get("route_select_grad", False)),
        "packed_branch_kv_projection": bool(model.get("packed_branch_kv_projection", False)),
        "coarse_attention_backend": str(model.get("coarse_attention_backend", "")),
        "route_score_mode": str(model.get("route_score_mode", "logsumexp_logits_current")),
        "route_backend": str(model.get("route_backend", "torch_full")),
        "route_block_q": int(model.get("route_block_q", 16) or 16),
        "route_block_c": int(model.get("route_block_c", 32) or 32),
        "route_materialize_scores_in_aux": bool(model.get("route_materialize_scores_in_aux", True)),
        "route_shape_penalty_weight": float(model.get("route_shape_penalty_weight", 0.0) or 0.0),
        "route_center_distance_weight": model.get("route_center_distance_weight", ""),
        "route_distance_normalization": str(model.get("route_distance_normalization", "raw")),
        "route_distance_units": str(model.get("route_distance_units", "")),
        "branch_gate_mode": str(model.get("branch_gate_mode", "softmax")),
        "activation_checkpointing": str(model.get("activation_checkpointing", "none")),
        "activation_checkpointing_mode": ckpt_mode,
        "checkpoint_local_attention": bool(checkpoint_local_effective),
        "local_attention_backend": str(model.get("local_attention_backend", "torch")),
        "local_attention_block_n": int(model.get("local_attention_block_n", 16)),
        "branch_output_fusion": str(branch_output_fusion_effective),
        "coarse_summary_pool_size": int(model.get("coarse_summary_pool_size", 1) or 1),
        "branch_output_norm": str(model.get("branch_output_norm", "none")),
        "branch_layer_scale": bool(model.get("branch_layer_scale", False)),
        "branch_layer_scale_init": str(model.get("branch_layer_scale_init", 1.0)),
        "branch_mixer_mode": str(model.get("branch_mixer_mode", "gated_sum")),
        "branch_gate_bias_init": str(model.get("branch_gate_bias_init", 0.0)),
        "branch_gate_prior_schedule": str(model.get("branch_gate_prior_schedule", "none")),
        "branch_gate_prior_start": str(model.get("branch_gate_prior_start", 0.0)),
        "branch_gate_prior_end": str(model.get("branch_gate_prior_end", 0.0)),
        "branch_gate_prior_steps": int(model.get("branch_gate_prior_steps", training.get("branch_gate_prior_steps", 0)) or 0),
        "selected_mixing_mode": str(model.get("selected_mixing_mode", "standard")),
        "full_layer_execution": str(model.get("full_layer_execution", "full")),
        "query_tile_size": int(model.get("query_tile_size", 0) or 0),
        "query_tile_checkpoint": bool(query_tile_checkpoint_effective),
        "route_granularity": str(model.get("route_granularity", "token_exact")),
        "route_share_tile_size": int(model.get("route_share_tile_size", 16) or 16),
        "enabled_branches": ",".join(str(x) for x in model.get("enabled_branches", ["local", "compressed", "selected"])),
        "structure_conditioning": str(model.get("structure_conditioning", "none")),
        "structure_conditioning_location": str(model.get("structure_conditioning_location", "head_only")),
        "num_structures": int(model.get("num_structures", 1) or 1),
        "segmentation_head": str(model.get("segmentation_head", "linear")),
        "monai_decoder_project_dim": int(model.get("monai_decoder_project_dim", 0) or 0),
        "monai_decoder_features": "x".join(map(str, model.get("monai_decoder_features", []))),
        "window_adapter_hidden": int(model.get("window_adapter_hidden", 0) or 0),
        "atom_assignment_mode": str(model.get("atom_assignment_mode", "current_encode_only")),
        "atom_balance_loss_weight": float(model.get("atom_balance_loss_weight", 0.0) or 0.0),
        "atom_entropy_loss_weight": float(model.get("atom_entropy_loss_weight", 0.0) or 0.0),
        "atom_orthogonality_loss_weight": float(model.get("atom_orthogonality_loss_weight", 0.0) or 0.0),
        "atom_temperature": float(model.get("atom_temperature", 1.0) or 1.0),
        "route_residual_mode": str(model.get("route_residual_mode", "key_residual")),
        "halo_masking": bool(
            training.get(
                "halo_masking",
                cfg.get("jepa", {}).get("halo_masking", cfg.get("halo_masking", True)),
            )
        ),
        "separate_branch_kv": bool(model.get("separate_branch_kv", True)),
        "block_volume": block_volume,
        "local_radius": "x".join(map(str, model.get("local_radius", []))),
        "evidence_level": str(cfg.get("evidence_level", "")),
        "layout": str(model.get("layout", model.get("layout_mode", "native" if str(model.get("name", "")) == "hypernsa" else str(model.get("name", ""))))),
        "pos_encoding": str(model.get("pos_encoding", "learned_full")),
        "compressed_rope_mode": str(model.get("compressed_rope_mode", "token_before_compression")),
        "rotary_base": float(model.get("rotary_base", 10000.0) or 10000.0),
        "rotary_coordinate_mode": str(model.get("rotary_coordinate_mode", "raw_grid")),
        "rotary_axis_scales": "x".join(map(str, model.get("rotary_axis_scales", []))) if model.get("rotary_axis_scales") else "",
        "rotary_axis_pair_allocation": str(model.get("rotary_axis_pair_allocation", "balanced")),
        "learned_low_rank_pe_rank": int(model.get("learned_low_rank_pe_rank", 0) or 0),
        "coordinate_fourier_bands": int(model.get("coordinate_fourier_bands", 0) or 0),
        "coordinate_fourier_hidden": int(model.get("coordinate_fourier_hidden", 0) or 0),
        "input_corruption_mode": str(corruption.get("mode", "none")),
        "input_corruption_channel": int(corruption.get("channel", 0) or 0) if corruption else 0,
        "input_corruption_probability": float(corruption.get("probability", 0.0) or 0.0) if corruption else 0.0,
        "input_corruption_fraction": float(corruption.get("fraction", 0.0) or 0.0) if corruption else 0.0,
    }


def phase3a_config_fields(cfg: dict[str, Any]) -> dict[str, Any]:
    return phase_config_fields(cfg)


def load_phase3a_rows(raw_dir: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(Path(raw_dir).glob("phase3a_*.jsonl")):
        for line in path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                row.setdefault("raw_file", str(path))
                rows.append(row)
    return rows


def load_phase_rows(raw_dir: str | Path, phase: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(Path(raw_dir).glob(f"{phase}_*.jsonl")):
        for line in path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                row.setdefault("raw_file", str(path))
                rows.append(row)
    return rows
