"""Portable I/O around the preserved paper model and training implementation."""
from copy import deepcopy
import json
import math
import os
from pathlib import Path
import sys

import torch
import yaml

SNAPSHOT = Path(__file__).resolve().parent / "paper_backend"


def clean_evaluation(result):
    """Fail on invalid task metrics; label undefined optional diagnostics null."""
    output = dict(result)
    missing = []
    for key, value in result.items():
        if isinstance(value, float) and not math.isfinite(value):
            if not key.startswith("attn/"):
                raise RuntimeError(f"nonfinite evaluation metric: {key}")
            output[key] = None
            missing.append(key)
    output["undefined_optional_diagnostics"] = sorted(missing)
    return output


def load_recipe(path):
    cfg = yaml.safe_load(Path(path).read_text())
    if not isinstance(cfg, dict) or cfg.get("model", {}).get("name") != "hypernsa_lm":
        raise ValueError("this runner supports the published PACK3D operator recipes")
    if cfg.get("data", {}).get("dataset") not in ("allen_multistructure", "allen", "msd"):
        raise ValueError("supported datasets are Allen and MSD preprocessed crops")
    if "selected" in cfg["model"].get("enabled_branches", []):
        raise ValueError("selected-token refinement is outside this release")
    if int(cfg.get("training", {}).get("max_steps", 0)) <= 0:
        raise ValueError("training.max_steps must be positive")
    return cfg


def resolve_manifest(path, root):
    """Resolve only declared preprocessed crops; reject cross-split path overlap.

    This checks crop paths, not patient identity. Source-case split auditing is
    a separate data-preparation requirement. Never infer a split from a glob.
    """
    meta = json.loads(Path(path).read_text())
    root = Path(root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    key = "samples" if meta.get("multistructure", False) else "preprocessed"
    splits = meta.get(key)
    if not isinstance(splits, dict) or not splits.get("train") or not splits.get("val"):
        raise ValueError("manifest must explicitly list nonempty train and val crops")
    seen = {}
    for split, rows in splits.items():
        for i, row in enumerate(rows):
            raw = row["path"] if key == "samples" else row
            resolved = (root / raw).resolve()
            if not resolved.is_relative_to(root) or not resolved.is_file():
                raise ValueError(f"crop is missing or outside data root: {raw}")
            if resolved in seen:
                raise ValueError(f"duplicate crop path in {seen[resolved]} and {split}")
            seen[resolved] = split
            if key == "samples":
                row["path"] = str(resolved)
            else:
                rows[i] = str(resolved)
    return meta


def device_from_name(name):
    if name == "cpu":
        return torch.device("cpu")
    if not os.environ.get("CUDA_VISIBLE_DEVICES"):
        raise ValueError("set CUDA_VISIBLE_DEVICES to one authorized GPU before using --device cuda")
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise ValueError("exactly one visible CUDA device is required")
    return torch.device("cuda:0")


def paper_modules(cfg, device):
    """Use the bounded snapshot, corrected packed RoPE, and strict runtime guards."""
    sys.path.insert(0, str(SNAPSHOT))
    import hypernsa
    if not Path(hypernsa.__file__).resolve().is_relative_to(SNAPSHOT):
        raise RuntimeError("a different hypernsa installation is already imported; use a fresh process")
    import hypernsa.attention.hypernsa_morton as attention
    from rebuttal.scripts.train_3d_segmentation_rebuttal_2026_07_26 import (
        RebuttalAttention20260726, _install_runtime_guards,
    )
    attention.HypergridMortonSparseAttention = RebuttalAttention20260726
    import scripts.train_3d_segmentation as trainer
    from hypernsa.training.wandb_utils import NoOpRun
    _install_runtime_guards(trainer, cfg)
    trainer.select_device = lambda: device
    trainer.init_wandb = lambda *args, **kwargs: NoOpRun(Path(kwargs["outdir"]))
    return attention, trainer


def create_model(cfg, meta, trainer, device):
    cfg = deepcopy(cfg)
    m = cfg["model"]
    m["num_structures"] = int(meta.get("num_structures", m.get("num_structures", 1)))
    return trainer.TokenSegmentationModel(
        trainer.build_backbone(cfg), int(meta["num_classes"]),
        num_structures=int(meta.get("num_structures", 1)),
        structure_conditioning=m.get("structure_conditioning", "none"),
        structure_conditioning_location=m.get("structure_conditioning_location", "head_only"),
        segmentation_head=m.get("segmentation_head", "linear"),
        monai_decoder_project_dim=int(m.get("monai_decoder_project_dim", 32)),
        monai_decoder_features=tuple(m.get("monai_decoder_features", [32, 32, 64, 128, 256, 32])),
        monai_decoder_upsample=m.get("monai_decoder_upsample", "deconv"),
        monai_decoder_raw_input_skip=bool(m.get("monai_decoder_raw_input_skip", False)),
    ).to(device)


def prepare_run(cfg, manifest, data_root, output):
    """Reserve a fresh output directory atomically, after validating all inputs."""
    meta = resolve_manifest(manifest, data_root)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest_out = output / "manifest_resolved.json"
    manifest_out.write_text(json.dumps(meta, indent=2) + "\n")
    cfg = deepcopy(cfg)
    cfg["data"]["manifest"] = str(manifest_out)
    cfg["data"]["root"] = str(Path(data_root).resolve())
    cfg["run_id"], cfg["phase"] = "run", "pack3d"
    path = output / "recipe.yaml"
    path.write_text(yaml.safe_dump(cfg, sort_keys=False))
    return cfg, output, path
