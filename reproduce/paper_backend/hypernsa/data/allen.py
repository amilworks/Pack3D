from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any, Iterable

import torch
from torch.utils.data import Dataset


DEFAULT_QUALITY_FILTERS = {
    "outlier": {"No", "False", "false", "0", ""},
    "edge_flag": {"0", "False", "false", ""},
    "meta_plate_bad_segmentation": {"False", "false", "0", ""},
}


def _json_quality_filters() -> dict[str, list[str]]:
    return {key: sorted(value) for key, value in DEFAULT_QUALITY_FILTERS.items()}


def _norm_structure(name: str) -> str:
    return str(name).strip().upper()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or str(value).strip() == "":
            return int(default)
        return int(float(str(value)))
    except Exception:
        return int(default)


def _abs_path(root: Path, value: str) -> str:
    path = Path(str(value))
    if path.is_absolute():
        return str(path)
    return str(root / path)


def _record_id(*parts: str) -> str:
    text = "|".join(str(p) for p in parts)
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def _passes_quality(row: dict[str, str], *, use_quality_filters: bool) -> bool:
    if not use_quality_filters:
        return True
    for key, allowed in DEFAULT_QUALITY_FILTERS.items():
        if str(row.get(key, "")).strip() not in allowed:
            return False
    return True


def _structure_rows(
    metadata_csv: Path,
    *,
    root: Path,
    structures: Iterable[str],
    use_quality_filters: bool = True,
    require_files: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    wanted = {_norm_structure(s) for s in structures}
    dedup: dict[str, dict[tuple[str, str, str, str], dict[str, Any]]] = {s: {} for s in wanted}
    with metadata_csv.open(newline="") as f:
        reader = csv.DictReader(f)
        for row_idx, row in enumerate(reader):
            structure = _norm_structure(row.get("structure_name", ""))
            if structure not in wanted:
                continue
            if not _passes_quality(row, use_quality_filters=use_quality_filters):
                continue
            fov_rel = str(row.get("fov_path", "")).strip()
            target_rel = str(row.get("struct_seg_path", "")).strip()
            if not fov_rel or not target_rel:
                continue
            source_path = _abs_path(root, fov_rel)
            target_path = _abs_path(root, target_rel)
            if require_files and (not Path(source_path).exists() or not Path(target_path).exists()):
                continue
            struct_channel = str(row.get("ChannelNumberStruct", "")).strip()
            brightfield_channel = str(row.get("ChannelNumberBrightfield", "")).strip()
            dna_channel = str(row.get("ChannelNumber405", "")).strip()
            membrane_channel = str(row.get("ChannelNumber638", "")).strip()
            key = (source_path, target_path, struct_channel, brightfield_channel)
            current = dedup[structure].get(key)
            if current is None:
                current = {
                    "record_id": _record_id(structure, source_path, target_path, struct_channel, brightfield_channel),
                    "source_path": source_path,
                    "target_path": target_path,
                    "structure_name": structure,
                    "struct_channel": _safe_int(struct_channel),
                    "brightfield_channel": _safe_int(brightfield_channel),
                    "dna_channel": _safe_int(dna_channel, default=-1),
                    "membrane_channel": _safe_int(membrane_channel, default=-1),
                    "original_row_idx": row_idx,
                    "cell_rows": 0,
                    "fov_id": row.get("FOVId", ""),
                    "plate_id": row.get("PlateId", ""),
                    "well_id": row.get("WellId", ""),
                    "scale_micron": row.get("scale_micron", ""),
                }
                dedup[structure][key] = current
            current["cell_rows"] = int(current["cell_rows"]) + 1
    return {s: sorted(rows.values(), key=lambda r: (str(r["source_path"]), str(r["target_path"]))) for s, rows in dedup.items()}


def _split_records(records: list[dict[str, Any]], *, train_fraction: float, seed: int) -> dict[str, list[dict[str, Any]]]:
    records = list(records)
    rng = random.Random(int(seed))
    rng.shuffle(records)
    if len(records) <= 1:
        return {"train": records, "val": records[:]}
    split_at = max(1, min(len(records) - 1, int(math.ceil(len(records) * float(train_fraction)))))
    return {"train": records[:split_at], "val": records[split_at:]}


def _write_split_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "source_path",
        "target_path",
        "structure_name",
        "brightfield_channel",
        "dna_channel",
        "membrane_channel",
        "struct_channel",
        "original_row_idx",
        "record_id",
        "cell_rows",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def build_allen_manifest(
    *,
    root: str | Path,
    metadata_csv: str | Path,
    structures: Iterable[str],
    manifest_dir: str | Path = "data_manifests",
    train_fraction: float = 0.8,
    seed: int = 13,
    use_quality_filters: bool = True,
    require_files: bool = True,
    max_fovs_per_structure: int = 0,
) -> Path:
    root = Path(root).expanduser()
    metadata_csv = Path(metadata_csv).expanduser()
    manifest_dir = Path(manifest_dir)
    structures = [_norm_structure(s) for s in structures]
    grouped = _structure_rows(
        metadata_csv,
        root=root,
        structures=structures,
        use_quality_filters=use_quality_filters,
        require_files=require_files,
    )
    manifest_dir.mkdir(parents=True, exist_ok=True)
    csv_root = manifest_dir / "allen_cell"
    structure_manifests: dict[str, dict[str, Any]] = {}
    for structure in structures:
        records = grouped.get(structure, [])
        if max_fovs_per_structure > 0:
            records = records[: int(max_fovs_per_structure)]
        split = _split_records(records, train_fraction=train_fraction, seed=seed)
        struct_slug = structure.lower()
        _write_split_csv(csv_root / struct_slug / "train.csv", split["train"])
        _write_split_csv(csv_root / struct_slug / "val.csv", split["val"])
        per_structure = {
            "dataset": "allen_cell",
            "dataset_status": "real3d_microscopy",
            "structure_name": structure,
            "root": str(root),
            "metadata_csv": str(metadata_csv),
            "quality_filters": _json_quality_filters() if use_quality_filters else {},
            "splits": ["train", "val"],
            "records": split,
            "csv": {
                "train": str(csv_root / struct_slug / "train.csv"),
                "val": str(csv_root / struct_slug / "val.csv"),
            },
            "num_samples_per_split": {key: len(value) for key, value in split.items()},
            "num_classes": 2,
            "task": f"allen_cell_{struct_slug}",
            "dedupe_key": ["fov_path", "struct_seg_path", "ChannelNumberStruct", "ChannelNumberBrightfield"],
        }
        path = manifest_dir / f"allen_cell_{struct_slug}.json"
        path.write_text(json.dumps(per_structure, indent=2, sort_keys=True))
        structure_manifests[structure] = {
            "manifest": str(path),
            "num_samples_per_split": per_structure["num_samples_per_split"],
            "csv": per_structure["csv"],
        }
    combined = {
        "dataset": "allen_cell",
        "dataset_status": "real3d_microscopy",
        "root": str(root),
        "metadata_csv": str(metadata_csv),
        "structures": structure_manifests,
        "selected_structures": structures,
        "quality_filters": _json_quality_filters() if use_quality_filters else {},
        "dedupe_key": ["fov_path", "struct_seg_path", "ChannelNumberStruct", "ChannelNumberBrightfield"],
    }
    combined_path = manifest_dir / "allen_cell_selected.json"
    combined_path.write_text(json.dumps(combined, indent=2, sort_keys=True))
    return combined_path


class AllenPreprocessedSegmentationDataset(Dataset):
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
            raise FileNotFoundError(f"no preprocessed Allen samples for split={split} in {self.manifest_path}")
        self.num_classes = int(meta.get("num_classes", 2))
        self.task = str(meta.get("task", "allen_cell"))
        self.structure_name = str(meta.get("structure_name", ""))
        self.structure_names = [self.structure_name] if self.structure_name else []
        self.num_structures = int(meta.get("num_structures", 1))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        import numpy as np

        with np.load(self.samples[index]) as npz:
            image = torch.from_numpy(npz["image"]).float()
            label = torch.from_numpy(npz["label"]).long()
        return image, label


class AllenMultiStructurePreprocessedSegmentationDataset(Dataset):
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
        self.structure_names = [str(x).upper() for x in meta.get("structure_names", [])]
        self.structure_to_id = {name: idx for idx, name in enumerate(self.structure_names)}
        samples = list(meta.get("samples", {}).get(split, []))
        if not samples:
            raise FileNotFoundError(f"no preprocessed Allen multistructure samples for split={split} in {self.manifest_path}")
        self.samples = [
            {
                "path": Path(row["path"]),
                "structure_id": int(row.get("structure_id", self.structure_to_id.get(str(row.get("structure_name", "")).upper(), 0))),
                "structure_name": str(row.get("structure_name", "")).upper(),
            }
            for row in samples
        ]
        if max_samples is not None and 0 < int(max_samples) < len(self.samples):
            generator = torch.Generator().manual_seed(int(seed) + (0 if split == "train" else 17))
            order = torch.randperm(len(self.samples), generator=generator)[: int(max_samples)].tolist()
            self.samples = [self.samples[i] for i in order]
        self.num_classes = int(meta.get("num_classes", 2))
        self.task = str(meta.get("task", "allen_cell_multistructure"))
        self.structure_name = "MULTISTRUCTURE"
        self.num_structures = max(1, int(meta.get("num_structures", len(self.structure_names) or 1)))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        import numpy as np

        row = self.samples[index]
        with np.load(row["path"]) as npz:
            image = torch.from_numpy(npz["image"]).float()
            label = torch.from_numpy(npz["label"]).long()
        structure_id = torch.tensor(int(row["structure_id"]), dtype=torch.long)
        return image, label, structure_id
