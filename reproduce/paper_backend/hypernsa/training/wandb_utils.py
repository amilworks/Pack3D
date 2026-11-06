from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
from typing import Any

import yaml

from hypernsa.utils.env import collect_env


class NoOpRun:
    """Small W&B-compatible fallback used when wandb is unavailable."""

    def __init__(self, directory: Path):
        self.dir = str(directory)
        self.summary: dict[str, Any] = {}

    def log(self, data: dict[str, Any], step: int | None = None) -> None:
        record = {"step": step, **data}
        with Path(self.dir, "wandb_noop_metrics.jsonl").open("a") as f:
            f.write(json.dumps(record) + "\n")

    def finish(self) -> None:
        Path(self.dir, "wandb_noop_summary.json").write_text(json.dumps(self.summary, indent=2))


def log_artifact_files(run: Any, *, name: str, artifact_type: str, paths: list[str | Path]) -> None:
    """Log local files as a W&B artifact when the active run supports it."""
    existing = [Path(path) for path in paths if Path(path).exists()]
    if not existing or not hasattr(run, "log_artifact"):
        return
    try:
        import wandb

        artifact = wandb.Artifact(name=name, type=artifact_type)
        for path in existing:
            artifact.add_file(str(path))
        run.log_artifact(artifact)
    except Exception:
        return


def load_config(path: str | Path | None, overrides: list[str] | None = None) -> dict[str, Any]:
    """Load YAML config and apply dotted key=value overrides."""
    cfg: dict[str, Any] = {}
    if path:
        cfg = yaml.safe_load(Path(path).read_text()) or {}
    for item in overrides or []:
        key, raw = item.split("=", 1)
        value = yaml.safe_load(raw)
        cursor = cfg
        parts = key.split(".")
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = value
    return cfg


def write_resolved_config(config: dict[str, Any], outdir: str | Path) -> Path:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / "config_resolved.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=True))
    return path


def git_context() -> dict[str, Any]:
    """Return git commit and dirty status, or an explicit non-git marker."""
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
        diff = subprocess.check_output(["git", "diff", "--stat"], text=True, stderr=subprocess.DEVNULL)
        return {"is_git_repo": True, "commit": commit, "dirty": bool(diff.strip()), "dirty_diff_stat": diff}
    except Exception:
        return {"is_git_repo": False, "commit": None, "dirty": None, "dirty_diff_stat": "", "note": "not a git repository"}


def write_run_context(config: dict[str, Any], outdir: str | Path, command: str | None = None) -> Path:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    context = {"config": config, "command": command, "git": git_context(), "environment": collect_env()}
    path = outdir / "run_context.json"
    path.write_text(json.dumps(context, indent=2, sort_keys=True))
    return path


def init_wandb(config: dict[str, Any], *, mode: str = "offline", group: str | None = None, outdir: str | Path = "results/raw"):
    """Initialize W&B in online/offline/dryrun mode, falling back to local files."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("WANDB_PROJECT", str(config.get("project", "hypernsa-vision")))
    os.environ["WANDB_MODE"] = mode
    try:
        import wandb

        return wandb.init(
            project=str(config.get("project", "hypernsa-vision")),
            entity=(config.get("wandb") or {}).get("entity"),
            group=group,
            mode=mode,
            config=config,
            tags=(config.get("wandb") or {}).get("tags"),
            dir=str(outdir),
        )
    except Exception:
        return NoOpRun(outdir)


def add_config_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--override", action="append", default=[])
    parser.add_argument("--wandb-mode", default="offline", choices=["online", "offline", "dryrun", "disabled"])
    parser.add_argument("--wandb-group", default=None)
    return parser
