from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import torch
from torch import Tensor
import torch.nn.functional as F
from torch.utils.data import Dataset, Subset


PREFERRED_2D = ("pathmnist", "organamnist", "bloodmnist", "dermamnist")
PREFERRED_3D = ("organmnist3d", "nodulemnist3d", "adrenalmnist3d")


def _dataset_class(name: str):
    import medmnist
    from medmnist import INFO

    key = name.lower()
    if key not in INFO:
        raise KeyError(f"unknown MedMNIST dataset {name}")
    return getattr(medmnist, INFO[key]["python_class"]), INFO[key]


def medmnist_num_classes(name: str) -> int:
    _cls, info = _dataset_class(name)
    return len(info["label"])


def medmnist_modality(name: str) -> str:
    _cls, info = _dataset_class(name)
    return str(info.get("task", "multi-class"))


def _to_tensor(image: Any) -> Tensor:
    arr = np.asarray(image)
    if arr.ndim == 2:
        arr = arr[None, :, :]
    elif arr.ndim == 3:
        # 2D RGB comes as HWC; 3D volumes come as DHW.
        if arr.shape[-1] in (1, 3, 4):
            arr = np.moveaxis(arr[..., :3], -1, 0)
        else:
            arr = arr[None, :, :, :]
    elif arr.ndim == 4:
        # MedMNIST 3D commonly stores CDHW; DHWC is also handled.
        if arr.shape[0] in (1, 3, 4):
            arr = arr[:3]
        else:
            arr = np.moveaxis(arr, -1, 0)
    else:
        raise ValueError(f"unexpected MedMNIST image shape {arr.shape}")
    x = torch.as_tensor(np.array(arr, copy=True), dtype=torch.float32)
    if float(x.max()) > 2.0:
        x = x / 255.0
    return x


class TensorMedMNIST(Dataset):
    def __init__(self, name: str, split: str, root: str | Path, *, download: bool = False, spatial_size: Sequence[int] | None = None):
        cls, _info = _dataset_class(name)
        self.name = name.lower()
        self.base = cls(split=split, root=str(root), download=download)
        self.split = split
        self.spatial_size = tuple(int(x) for x in spatial_size) if spatial_size is not None else None

    def __len__(self) -> int:
        return len(self.base)

    def __getitem__(self, idx: int) -> tuple[Tensor, Tensor]:
        image, label = self.base[idx]
        x = _to_tensor(image)
        if self.spatial_size is not None and tuple(x.shape[1:]) != self.spatial_size:
            mode = "trilinear" if len(self.spatial_size) == 3 else "bilinear"
            x = F.interpolate(x.unsqueeze(0), size=self.spatial_size, mode=mode, align_corners=False).squeeze(0)
        y = torch.as_tensor(label).reshape(-1)[0].long()
        return x, y


def make_medmnist_dataset(
    name: str,
    split: str,
    root: str | Path,
    *,
    download: bool = False,
    max_samples: int | None = None,
    seed: int = 0,
    spatial_size: Sequence[int] | None = None,
) -> Dataset:
    dataset = TensorMedMNIST(name, split, root, download=download, spatial_size=spatial_size)
    if max_samples is None or max_samples <= 0 or max_samples >= len(dataset):
        return dataset
    generator = torch.Generator().manual_seed(int(seed) + {"train": 0, "val": 17, "test": 31}.get(split, 0))
    indices = torch.randperm(len(dataset), generator=generator)[: int(max_samples)].tolist()
    return Subset(dataset, indices)


def build_medmnist_manifest(root: str | Path, manifest_dir: str | Path = "data_manifests") -> dict[str, Any]:
    from medmnist import INFO

    root = Path(root).expanduser()
    manifest_dir = Path(manifest_dir)
    manifest_dir.mkdir(parents=True, exist_ok=True)
    datasets: dict[str, Any] = {}
    selected: dict[str, str] = {}
    for ndim, choices in (("2d", PREFERRED_2D), ("3d", PREFERRED_3D)):
        for name in choices:
            if name not in INFO:
                continue
            try:
                split_counts = {}
                for split in ("train", "val", "test"):
                    ds = TensorMedMNIST(name, split, root, download=True)
                    split_counts[split] = len(ds)
                datasets[name] = {
                    "python_class": INFO[name]["python_class"],
                    "task": INFO[name].get("task"),
                    "n_classes": len(INFO[name]["label"]),
                    "splits": split_counts,
                    "selected_for_phase3a": True,
                }
                selected[ndim] = name
                break
            except Exception as exc:
                datasets[name] = {"error": str(exc), "selected_for_phase3a": False}
        else:
            selected[ndim] = ""
    manifest = {"dataset": "medmnist", "root": str(root), "datasets": datasets, "selected": selected}
    (manifest_dir / "medmnist.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def choose_available_medmnist(root: str | Path, *, ndim: int) -> str:
    choices = PREFERRED_2D if int(ndim) == 2 else PREFERRED_3D
    for name in choices:
        try:
            _ = TensorMedMNIST(name, "train", root, download=False)
            return name
        except Exception:
            continue
    return choices[0]
