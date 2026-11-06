import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    result = subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                            capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def test_offline_training_evaluation_and_collision_guard(tmp_path):
    data, trained, evaluated = (tmp_path / n for n in ("data", "trained", "evaluated"))
    run("reproduce/data/make_smoke_data.py", "--output", data)
    base = ["--config", "reproduce/configs/smoke.yaml", "--manifest", data / "manifest.json",
            "--data-root", data, "--device", "cpu"]
    run("reproduce/train.py", *base, "--output", trained)
    best = trained / "results/checkpoints/run/best.pt"
    assert best.is_file()
    run("reproduce/evaluate.py", *base, "--checkpoint", best, "--output", evaluated,
        "--pure-repack-seed", 2026072600)
    metrics = json.loads((evaluated / "metrics.json").read_text())
    assert metrics["validation_cases"] == 1 and metrics["retraining"] is False
    assert all(len(metrics[name]) == 64 for name in ("checkpoint_sha256", "recipe_sha256", "manifest_sha256"))
    collision = subprocess.run([sys.executable, "reproduce/train.py", *map(str, base),
                                "--output", str(trained)], cwd=ROOT, capture_output=True, text=True)
    assert collision.returncode != 0 and "FileExistsError" in collision.stderr


def test_aggregation_matches_camera_ready():
    result = json.loads(run("reproduce/aggregate.py").stdout)
    assert result["exact_two_sided_sign_flip_p"] == 0.03125
    assert abs(result["encodings"]["PACK3D"]["original_mean"] - .8246801675185059) < 1e-12
    assert len(result["seeds"]) == 6


def test_public_recipes_preserve_scientific_fields():
    manifest = json.loads((ROOT / "reproduce/config_manifest.json").read_text())
    assert len(manifest["configs"]) == 45
    for row in manifest["configs"]:
        cfg = yaml.safe_load((ROOT / row["file"]).read_text())
        assert cfg["data"]["manifest"] is None
        assert cfg["training"]["max_steps"] == 10000
        assert cfg["model"]["name"] == "hypernsa_lm"
        assert "selected" not in cfg["model"]["enabled_branches"]


def test_historical_packed_control_has_active_rotations():
    import torch
    from rebuttal.scripts.train_3d_segmentation_rebuttal_2026_07_26 import (
        RebuttalAttention20260726, _rope_attestation,
    )
    layer = RebuttalAttention20260726(
        dim=16, grid_shape=(4, 4, 4), heads=1, kv_heads=1, dim_head=16,
        block_shape=(2, 2, 2), num_summary_atoms=1, num_selected_blocks=0,
        atom_assignment_mode="single_atom", enabled_branches=("local", "compressed"),
        pos_encoding="packed_sequence_rope", coarse_summary_pool_size=2,
    )
    allocation, change = _rope_attestation(layer, torch.device("cpu"))
    assert allocation == "8x0x0" and change > 1e-6


def test_manifest_overlap_rejected(tmp_path):
    spec = importlib.util.spec_from_file_location("public_reproduce_common", ROOT / "reproduce/common.py")
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    crop = tmp_path / "crop.npz"
    crop.touch()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"preprocessed": {"train": ["crop.npz"], "val": ["crop.npz"]}}))
    with pytest.raises(ValueError, match="duplicate"):
        common.resolve_manifest(manifest, tmp_path)
    with pytest.raises(RuntimeError, match="nonfinite"):
        common.clean_evaluation({"val/dice": float("nan")})
    result = common.clean_evaluation({"val/dice": .5, "attn/unused": float("nan")})
    assert result["attn/unused"] is None and result["undefined_optional_diagnostics"] == ["attn/unused"]
