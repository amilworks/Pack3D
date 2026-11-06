from __future__ import annotations

import hashlib
import json
import tarfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import torch
from torch.utils.data import Dataset, Subset


MSD_URLS: dict[str, str] = {
    "Task01_BrainTumour": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task01_BrainTumour.tar",
    "Task02_Heart": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task02_Heart.tar",
    "Task03_Liver": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task03_Liver.tar",
    "Task09_Spleen": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task09_Spleen.tar",
}


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_task_name(task: str) -> str:
    aliases = {
        "spleen": "Task09_Spleen",
        "task09": "Task09_Spleen",
        "task09_spleen": "Task09_Spleen",
        "heart": "Task02_Heart",
        "task02": "Task02_Heart",
        "task02_heart": "Task02_Heart",
        "brain": "Task01_BrainTumour",
        "braintumour": "Task01_BrainTumour",
        "task01": "Task01_BrainTumour",
        "task01_braintumour": "Task01_BrainTumour",
        "liver": "Task03_Liver",
        "task03": "Task03_Liver",
        "task03_liver": "Task03_Liver",
    }
    key = task.strip().replace("-", "_")
    return aliases.get(key.lower(), key)


def find_task_root(root: str | Path, task: str) -> Path | None:
    root = Path(root).expanduser()
    task = canonical_task_name(task)
    candidates = [
        root / task,
        root / "msd" / task,
        root / "MedicalSegmentationDecathlon" / task,
    ]
    for candidate in candidates:
        if (candidate / "imagesTr").exists() and (candidate / "labelsTr").exists():
            return candidate
    return None


def _download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 0:
        return
    tmp = target.with_suffix(target.suffix + ".tmp")
    with urllib.request.urlopen(url) as response, tmp.open("wb") as f:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
    tmp.replace(target)


def _extract(tar_path: Path, root: Path) -> None:
    with tarfile.open(tar_path) as tar:
        if not hasattr(tarfile, "data_filter"):
            raise RuntimeError("safe extraction requires a Python version with tarfile.data_filter")
        tar.extractall(root, filter="data")


def _case_id(path: Path) -> str:
    name = path.name
    for suffix in (".nii.gz", ".nii"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return path.stem


def _is_real_nifti(path: Path) -> bool:
    return path.name.endswith((".nii", ".nii.gz")) and not path.name.startswith("._")


def build_msd_task_manifest(root: str | Path, task: str) -> dict[str, Any]:
    task = canonical_task_name(task)
    task_root = find_task_root(root, task)
    available = task_root is not None
    cases: list[dict[str, str]] = []
    if task_root is not None:
        labels = { _case_id(p): p for p in sorted((task_root / "labelsTr").glob("*.nii*")) if _is_real_nifti(p) }
        for image in sorted((task_root / "imagesTr").glob("*.nii*")):
            if not _is_real_nifti(image):
                continue
            case = _case_id(image)
            label = labels.get(case)
            if label is not None:
                cases.append({"case_id": case, "image": str(image), "label": str(label)})
    return {
        "dataset": "msd",
        "task": task,
        "source": MSD_URLS.get(task, "https://medicaldecathlon.com/"),
        "available": available,
        "root": str(task_root or Path(root).expanduser()),
        "num_cases": len(cases),
        "cases": cases,
        "generated_timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata_sha256": _sha256_text(json.dumps(cases, sort_keys=True)),
    }


def build_msd_manifest(root: str | Path, manifest_dir: str | Path, tasks: Iterable[str]) -> Path:
    manifest_dir = Path(manifest_dir)
    manifest_dir.mkdir(parents=True, exist_ok=True)
    task_manifests = [build_msd_task_manifest(root, task) for task in tasks]
    for task_manifest in task_manifests:
        task = task_manifest["task"].lower()
        (manifest_dir / f"msd_{task}.json").write_text(json.dumps(task_manifest, indent=2, sort_keys=True))
    merged = {
        "dataset": "msd",
        "source": "https://medicaldecathlon.com/",
        "available": any(m["available"] for m in task_manifests),
        "tasks": task_manifests,
        "generated_timestamp": datetime.now(timezone.utc).isoformat(),
    }
    path = manifest_dir / "msd.json"
    path.write_text(json.dumps(merged, indent=2, sort_keys=True))
    return path


def download_msd_tasks(root: str | Path, tasks: Iterable[str], manifest_dir: str | Path, *, download: bool = True) -> Path:
    root = Path(root).expanduser()
    msd_root = root / "msd"
    msd_root.mkdir(parents=True, exist_ok=True)
    missing: list[str] = []
    for raw_task in tasks:
        task = canonical_task_name(raw_task)
        if task not in MSD_URLS:
            missing.append(f"{task}: no known open MSD URL in this scaffold")
            continue
        if find_task_root(root, task) is not None:
            continue
        if not download:
            missing.append(f"{task}: not found under {root} and download disabled")
            continue
        tar_path = root / "downloads" / f"{task}.tar"
        _download(MSD_URLS[task], tar_path)
        _extract(tar_path, msd_root)
    path = build_msd_manifest(root, manifest_dir, [canonical_task_name(t) for t in tasks])
    if missing:
        report_dir = Path("results/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "phase4a_dataset_status.md").write_text(
            "# Phase 4A Dataset Status\n\n"
            "## MSD\n\n"
            + "\n".join(f"- {item}" for item in missing)
            + "\n"
        )
    return path


class MSDPreprocessedSegmentationDataset(Dataset):
    def __init__(
        self,
        manifest: str | Path,
        split: str,
        *,
        max_samples: int | None = None,
        seed: int = 0,
    ):
        self.manifest_path = Path(manifest)
        meta = json.loads(self.manifest_path.read_text())
        samples = meta.get("preprocessed", {}).get(split, [])
        if not samples:
            root = Path(meta.get("preprocessed_root", self.manifest_path.parent))
            samples = [str(p) for p in sorted((root / split).glob("*.npz"))]
        self.samples = [Path(p) for p in samples]
        if max_samples is not None and 0 < int(max_samples) < len(self.samples):
            generator = torch.Generator().manual_seed(int(seed) + (0 if split == "train" else 17))
            order = torch.randperm(len(self.samples), generator=generator)[: int(max_samples)].tolist()
            self.samples = [self.samples[i] for i in order]
        if not self.samples:
            raise FileNotFoundError(f"no preprocessed MSD samples for split={split} in {self.manifest_path}")
        self.num_classes = int(meta.get("num_classes", 2))
        self.task = str(meta.get("task", "msd"))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        data = torch.load(self.samples[index], map_location="cpu", weights_only=True) if self.samples[index].suffix == ".pt" else None
        if data is None:
            import numpy as np

            with np.load(self.samples[index]) as npz:
                image = torch.from_numpy(npz["image"]).float()
                label = torch.from_numpy(npz["label"]).long()
        else:
            image = data["image"].float()
            label = data["label"].long()
        return image, label


def subset_dataset(dataset: Dataset, max_samples: int | None, seed: int, split: str) -> Dataset:
    if max_samples is None or int(max_samples) <= 0 or int(max_samples) >= len(dataset):
        return dataset
    generator = torch.Generator().manual_seed(int(seed) + {"train": 0, "val": 17, "test": 31}.get(split, 0))
    indices = torch.randperm(len(dataset), generator=generator)[: int(max_samples)].tolist()
    return Subset(dataset, indices)
