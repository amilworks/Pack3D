#!/usr/bin/env python3
"""Guarded, non-destructive PACK3D rebuttal training entry point.

This process-local runner preserves all historical implementation files and
artifacts. It applies the packed-sequence RoPE correction when requested and
adds runtime checks needed for claim-grade rebuttal runs.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import math
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import torch
from torch.utils.data import DataLoader, Dataset

import hypernsa.attention.hypernsa_morton as attention_impl
from hypernsa.training.wandb_utils import load_config
from rebuttal.scripts.artifact_claim_lock_2026_07_26 import (
    acquire_artifact_claim,
)


PATCH_DATE_TOKEN = "20260726"
LegacyHypergridMortonSparseAttention = (
    attention_impl.HypergridMortonSparseAttention
)


class RebuttalAttention20260726(LegacyHypergridMortonSparseAttention):
    """Legacy attention plus the minimal corrected packed-position RoPE."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if (
            self.pos_encoding == "packed_sequence_rope"
            and self.full_layer_execution == "query_tiled"
        ):
            raise ValueError(
                "Corrected packed-sequence RoPE requires full execution: "
                "the legacy query-tiled path restarts packed positions in "
                "each query tile."
            )
        if (
            self.compressed_rope_mode != "token_before_compression"
            and not self.separate_branch_kv
        ):
            raise ValueError(
                "Compression-placement controls require separate_branch_kv: "
                "shared K/V cannot independently change compressed-key RoPE."
            )
        if self.pos_encoding != "packed_sequence_rope":
            return
        pair_counts = [self.dim_head // 2] + [0] * (self.ndim - 1)
        self.rotary_axis_pair_counts_tuple = tuple(pair_counts)
        self.rotary_axis_pair_counts.copy_(
            torch.tensor(
                pair_counts,
                device=self.rotary_axis_pair_counts.device,
                dtype=self.rotary_axis_pair_counts.dtype,
            )
        )

    def _mix_branch_outputs(
        self,
        ref: torch.Tensor,
        gates: torch.Tensor,
        *,
        local: torch.Tensor | None = None,
        coarse: torch.Tensor | None = None,
        selected: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, str]:
        if (
            self.branch_mixer_mode == "local_residual_global"
            and self.enable_local_branch
            and local is not None
            and bool((gates[..., 0] == 0).any().item())
        ):
            raise RuntimeError(
                "An enabled local residual branch received an exact-zero "
                "softmax gate. The legacy presence test would silently "
                "remove it; dated rebuttal configs do not permit per-query "
                "branch disabling."
            )
        if (
            self.branch_mixer_mode == "compressed_residual_local"
            and self.enable_compressed_branch
            and coarse is not None
            and bool((gates[..., 1] == 0).any().item())
        ):
            raise RuntimeError(
                "An enabled compressed residual branch received an "
                "exact-zero softmax gate; refusing silent removal."
            )
        return super()._mix_branch_outputs(
            ref,
            gates,
            local=local,
            coarse=coarse,
            selected=selected,
        )


def _parse_wrapper_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", required=True)
    parser.add_argument("--override", action="append", default=[])
    return parser.parse_known_args()


def _refuse_artifact_collision(cfg: dict[str, Any]) -> None:
    phase = str(cfg.get("phase", ""))
    run_id = str(cfg.get("run_id", ""))
    if PATCH_DATE_TOKEN not in phase or PATCH_DATE_TOKEN not in run_id:
        raise ValueError(
            "Rebuttal runs require both phase and run_id to contain "
            f"{PATCH_DATE_TOKEN}."
        )
    paths = (
        ROOT / "results/raw" / f"{phase}_{run_id}.jsonl",
        ROOT / "results/checkpoints" / run_id,
    )
    collisions = [str(path) for path in paths if path.exists()]
    if collisions:
        raise FileExistsError(
            "Refusing to replace an existing rebuttal artifact: "
            + ", ".join(collisions)
        )


def _effective_compressed_tokens(attn: Any) -> float:
    block_valid = attn.block_valid_mask.bool().any(dim=-1)
    pool = int(attn.coarse_summary_pool_size)
    pad = (-int(block_valid.numel())) % pool
    if pad:
        block_valid = torch.nn.functional.pad(block_valid, (0, pad))
    active_groups = block_valid.reshape(-1, pool).any(dim=-1).sum()
    return float(int(active_groups.item()) * int(attn.num_summary_atoms))


def _rope_attestation(attn: Any, device: torch.device) -> tuple[str, float]:
    pair_counts = tuple(
        int(value) for value in attn.rotary_axis_pair_counts_tuple
    )
    if attn.pos_encoding not in {"axial_rope", "packed_sequence_rope"}:
        return "x".join(map(str, pair_counts)), 0.0
    probe = torch.randn(
        1,
        attn.heads,
        min(attn.num_tokens_padded, 32),
        attn.dim_head,
        device=device,
    )
    coords = attn.coords_packed[: probe.shape[2]].to(device)
    rotated = attn._apply_axial_rope(probe, coords)
    delta = float((rotated - probe).abs().max().item())
    if not math.isfinite(delta) or delta <= 1e-6:
        raise RuntimeError(
            f"{attn.pos_encoding} was inactive at runtime: max delta={delta}"
        )
    if attn.pos_encoding == "packed_sequence_rope":
        expected = (attn.dim_head // 2,) + (0,) * (attn.ndim - 1)
        if pair_counts != expected:
            raise RuntimeError(
                "Corrected packed RoPE pair allocation mismatch: "
                f"expected={expected}, actual={pair_counts}"
            )
    return "x".join(map(str, pair_counts)), delta


class _AugmentedMedicalDataset20260726(Dataset):
    """Paired 3D spatial transforms plus image-only intensity transforms."""

    def __init__(self, dataset: Dataset, config: dict[str, Any]) -> None:
        self.dataset = dataset
        self.config = config

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, index: int):
        sample = self.dataset[index]
        image, label, *rest = sample
        flip_probability = float(
            self.config.get("flip_probability", 0.5)
        )
        for image_dim, label_dim in ((1, 0), (2, 1), (3, 2)):
            if float(torch.rand(())) < flip_probability:
                image = torch.flip(image, dims=(image_dim,))
                label = torch.flip(label, dims=(label_dim,))
        if bool(self.config.get("rotate_xy", True)):
            turns = int(torch.randint(0, 4, ()).item())
            if turns:
                image = torch.rot90(image, turns, dims=(2, 3))
                label = torch.rot90(label, turns, dims=(1, 2))
        image_std = image.float().std().clamp_min(1e-6)
        scale_width = float(self.config.get("intensity_scale_width", 0.1))
        shift_width = float(self.config.get("intensity_shift_width", 0.1))
        noise_std = float(self.config.get("noise_std", 0.02))
        scale = 1.0 + (
            2.0 * float(torch.rand(())) - 1.0
        ) * scale_width
        shift = (
            2.0 * float(torch.rand(())) - 1.0
        ) * shift_width * float(image_std)
        image = image * scale + shift
        if noise_std > 0:
            image = image + torch.randn_like(image) * (
                noise_std * image_std
            )
        output = (image.contiguous(), label.contiguous(), *rest)
        return output


def _install_runtime_guards(
    training_script: Any,
    cfg: dict[str, Any],
) -> None:
    original_audit = training_script._runtime_model_audit
    original_aux_metrics = training_script.aux_metrics
    original_evaluate = training_script.evaluate
    original_grad_norm = training_script.grad_norm
    original_log_artifact_files = training_script.log_artifact_files
    original_make_loaders = training_script.make_loaders
    training_cfg = cfg.get("training", {})
    augmentation_cfg = training_cfg.get(
        "medical_augmentation_20260726",
        {},
    )
    augmentation_enabled = bool(augmentation_cfg.get("enabled", False))
    cosine_cfg = training_cfg.get("cosine_lr_20260726", {})
    cosine_enabled = bool(cosine_cfg.get("enabled", False))

    def runtime_audit(
        model: Any,
        cfg: dict[str, Any],
        meta: dict[str, Any],
        device: torch.device,
    ) -> dict[str, Any]:
        model_cfg = cfg.get("model", {})
        configured_pos_encoding = str(model_cfg.get("pos_encoding", ""))
        backbone_pos_encodings = {
            "learned_full",
            "learned_separable_3d",
            "learned_low_rank_3d",
            "coordinate_fourier_mlp",
        }
        audit_cfg = cfg
        if configured_pos_encoding in backbone_pos_encodings:
            audit_cfg = deepcopy(cfg)
            audit_cfg["model"]["pos_encoding"] = "none"
        row = original_audit(model, audit_cfg, meta, device)
        attn = training_script.first_hyper_attn(model)
        if attn is None:
            raise RuntimeError(
                "Rebuttal PACK3D run did not create an attention module"
            )
        backbone_pos_encoding = str(
            getattr(model.backbone, "pos_encoding", "")
        )
        if backbone_pos_encoding != configured_pos_encoding:
            raise RuntimeError(
                "Backbone positional encoding runtime mismatch: "
                f"expected={configured_pos_encoding}, "
                f"actual={backbone_pos_encoding}"
            )
        pair_counts, rope_delta = _rope_attestation(attn, device)
        expected_mixer = str(model_cfg.get("branch_mixer_mode", ""))
        if expected_mixer and attn.branch_mixer_mode != expected_mixer:
            raise RuntimeError(
                "Branch mixer runtime mismatch: "
                f"expected={expected_mixer}, actual={attn.branch_mixer_mode}"
            )
        row.update(
            {
                "rebuttal_runner_date": "2026-07-26",
                "historical_artifacts_preserved": True,
                "historical_packed_rope_noop_fixed": (
                    attn.pos_encoding == "packed_sequence_rope"
                ),
                "pos_encoding": configured_pos_encoding,
                "pos_encoding_placement": (
                    "backbone_token_embedding"
                    if configured_pos_encoding in backbone_pos_encodings
                    else "attention_qk"
                    if configured_pos_encoding
                    in {
                        "axial_rope",
                        "packed_sequence_rope",
                        "relative_position_bias_3d",
                        "alibi_3d",
                    }
                    else "none"
                ),
                "attention_pos_encoding_runtime": str(attn.pos_encoding),
                "backbone_pos_encoding_runtime": backbone_pos_encoding,
                "rotary_axis_pair_counts": pair_counts,
                "rope_runtime_max_delta": rope_delta,
                "rotary_axis_scales_runtime": "x".join(
                    f"{float(value):.8g}"
                    for value in attn.rotary_axis_scales.detach().cpu()
                ),
                "fine_summary_tokens_per_query": float(
                    int(attn.num_blocks) * int(attn.num_summary_atoms)
                ),
                "effective_compressed_tokens_per_query": (
                    _effective_compressed_tokens(attn)
                ),
                "medical_augmentation_20260726": augmentation_enabled,
                "cosine_lr_20260726": cosine_enabled,
                "cosine_lr_min_ratio": float(
                    cosine_cfg.get("min_lr_ratio", 0.05)
                )
                if cosine_enabled
                else "",
                "cosine_lr_warmup_steps": int(
                    cosine_cfg.get("warmup_steps", 0)
                )
                if cosine_enabled
                else "",
                "redundant_offline_wandb_artifact_copy_disabled": True,
                "duplicate_final_evaluation_cache_enabled": True,
                "active_residual_zero_gate_guard": True,
            }
        )
        return row

    def strict_aux_metrics(
        model: Any,
        aux: dict[str, Any] | None,
        target_mask=None,
    ) -> dict[str, Any]:
        out = original_aux_metrics(model, aux, target_mask=target_mask)
        attn = training_script.first_hyper_attn(model)
        if attn is None:
            return out
        out["compressed_tokens_per_query"] = _effective_compressed_tokens(attn)
        out["fine_summary_tokens_per_query"] = float(
            int(attn.num_blocks) * int(attn.num_summary_atoms)
        )
        if (
            aux is not None
            and attn.enable_local_branch
            and attn.local_attention_backend == "triton"
            and aux.get("local_attention_backend_actual") != "triton_local"
        ):
            raise RuntimeError(
                "Required triton_local path did not execute: "
                f"{aux.get('local_attention_fallback_reason', 'unknown reason')}"
            )
        return out

    def strict_grad_norm(parameters) -> float:
        params = list(parameters)
        bad_count = sum(
            parameter.grad is not None
            and not bool(torch.isfinite(parameter.grad).all())
            for parameter in params
        )
        if bad_count:
            raise RuntimeError(
                "Nonfinite gradients before optimizer.step() in "
                f"{bad_count} parameter tensors"
            )
        value = float(original_grad_norm(params))
        if not math.isfinite(value):
            raise RuntimeError(f"Nonfinite aggregate gradient norm: {value}")
        return value

    training_script._runtime_model_audit = runtime_audit
    training_script.aux_metrics = strict_aux_metrics
    training_script.grad_norm = strict_grad_norm

    evaluation_cache: dict[str, Any] = {}

    def reuse_unchanged_evaluation(
        model: Any,
        loader: Any,
        device: torch.device,
        eval_cfg: dict[str, Any],
        num_classes: int,
    ) -> dict[str, Any]:
        state_versions = tuple(
            int(tensor._version)
            for tensor in (
                *model.parameters(),
                *model.buffers(),
            )
        )
        key = (
            id(model),
            id(loader),
            id(eval_cfg),
            str(device),
            int(num_classes),
            state_versions,
        )
        if evaluation_cache.get("key") == key:
            return deepcopy(evaluation_cache["result"])
        result = original_evaluate(
            model,
            loader,
            device,
            eval_cfg,
            num_classes,
        )
        evaluation_cache["key"] = key
        evaluation_cache["result"] = deepcopy(result)
        return result

    training_script.evaluate = reuse_unchanged_evaluation

    def keep_local_artifacts_only(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        return None

    if original_log_artifact_files is None:
        raise RuntimeError("Expected legacy artifact logger is unavailable")
    training_script.log_artifact_files = keep_local_artifacts_only

    if augmentation_enabled:
        if str(cfg.get("data", {}).get("dataset", "")).lower() != "msd":
            raise ValueError(
                "medical_augmentation_20260726 is restricted to MSD runs"
            )

        def augmented_make_loaders(loader_cfg: dict[str, Any]):
            train_loader, val_loader, meta = original_make_loaders(loader_cfg)
            augmented = _AugmentedMedicalDataset20260726(
                train_loader.dataset,
                augmentation_cfg,
            )
            train_loader = DataLoader(
                augmented,
                batch_size=train_loader.batch_size,
                shuffle=True,
                num_workers=train_loader.num_workers,
                drop_last=train_loader.drop_last,
                pin_memory=train_loader.pin_memory,
            )
            return train_loader, val_loader, meta

        training_script.make_loaders = augmented_make_loaders

    if cosine_enabled:
        original_adamw = training_script.torch.optim.AdamW
        max_steps = int(training_cfg["max_steps"])
        min_ratio = float(cosine_cfg.get("min_lr_ratio", 0.05))
        warmup_steps = int(cosine_cfg.get("warmup_steps", 0))
        if max_steps <= 0:
            raise ValueError("Cosine LR requires positive training.max_steps")
        if not 0.0 <= min_ratio <= 1.0:
            raise ValueError("cosine_lr min_lr_ratio must be in [0,1]")
        if not 0 <= warmup_steps < max_steps:
            raise ValueError(
                "cosine_lr warmup_steps must be in [0,max_steps)"
            )

        class CosineAdamW20260726(original_adamw):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs)
                self._rebuttal_base_lrs = [
                    float(group["lr"]) for group in self.param_groups
                ]
                self._rebuttal_step = 0

            def step(self, closure=None):
                step_index = self._rebuttal_step + 1
                if warmup_steps and step_index <= warmup_steps:
                    multiplier = step_index / warmup_steps
                else:
                    decay_steps = max(max_steps - warmup_steps, 1)
                    progress = min(
                        max(
                            (step_index - warmup_steps - 1)
                            / max(decay_steps - 1, 1),
                            0.0,
                        ),
                        1.0,
                    )
                    multiplier = min_ratio + (
                        1.0 - min_ratio
                    ) * 0.5 * (1.0 + math.cos(math.pi * progress))
                for group, base_lr in zip(
                    self.param_groups,
                    self._rebuttal_base_lrs,
                ):
                    group["lr"] = base_lr * multiplier
                result = super().step(closure=closure)
                self._rebuttal_step = step_index
                return result

        training_script.torch.optim.AdamW = CosineAdamW20260726


def main() -> int:
    wrapper_args, _ = _parse_wrapper_args()
    cfg = load_config(wrapper_args.config, wrapper_args.override)
    _artifact_claim = acquire_artifact_claim(
        ROOT,
        phase=str(cfg.get("phase", "")),
        run_id=str(cfg.get("run_id", "")),
    )
    _refuse_artifact_collision(cfg)

    attention_impl.HypergridMortonSparseAttention = RebuttalAttention20260726

    import scripts.train_3d_segmentation as training_script

    _install_runtime_guards(training_script, cfg)
    return int(training_script.main())


if __name__ == "__main__":
    raise SystemExit(main())
