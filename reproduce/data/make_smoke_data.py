"""Generate tiny synthetic I/O fixtures, not scientific benchmark evidence."""
import argparse
import json
from pathlib import Path
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    rng = np.random.default_rng(7)
    records = {"train": [], "val": []}
    for split, count in (("train", 2), ("val", 1)):
        for i in range(count):
            image = rng.normal(size=(1, 4, 4, 4)).astype(np.float32)
            label = (image[0] > 0).astype(np.int64)
            name = f"{split}_{i}.npz"
            np.savez_compressed(args.output / name, image=image, label=label)
            records[split].append(name)
    manifest = {"task": "synthetic_io_smoke_only", "num_classes": 2, "preprocessed": records}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(args.output / "manifest.json")


if __name__ == "__main__":
    main()
