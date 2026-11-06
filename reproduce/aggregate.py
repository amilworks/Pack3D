"""Aggregate frozen per-seed evidence; seeds, not voxels, are the paired units."""
import argparse
import csv
import itertools
import json
from pathlib import Path
from statistics import mean, stdev


def sign_flip(values):
    if not values or len(values) > 20:
        raise ValueError("exact enumeration requires 1..20 paired differences")
    observed = abs(sum(values))
    extreme = sum(abs(sum(s * v for s, v in zip(signs, values))) >= observed - 1e-12
                  for signs in itertools.product((-1, 1), repeat=len(values)))
    return extreme / (2 ** len(values))


def summarize(path):
    with Path(path).open(newline="") as f:
        rows = list(csv.DictReader(f))
    groups = {}
    for row in rows:
        key = row["encoding"]
        seed = int(row["seed"])
        if seed in groups.setdefault(key, {}):
            raise ValueError("duplicate encoding/seed")
        old, new = float(row["standard_dice"]), float(row["repacked_dice"])
        if not (0 <= old <= 1 and 0 <= new <= 1):
            raise ValueError("Dice must be finite in [0,1]")
        if abs(new - old - float(row["delta"])) > 1e-10:
            raise ValueError("stored delta disagrees with Dice")
        groups[key][seed] = (old, new)
    a, p = groups["PACK3D"], groups["Packed RoPE"]
    if set(a) != set(p):
        raise ValueError("paired seeds differ")
    delta = [(p[s][1] - p[s][0]) - (a[s][1] - a[s][0]) for s in sorted(a)]
    return {"seeds": sorted(a), "encodings": {name: {
        "original_mean": mean(v[0] for v in arm.values()),
        "repacked_mean": mean(v[1] for v in arm.values()),
        "change_mean": mean(v[1] - v[0] for v in arm.values()),
    } for name, arm in groups.items()}, "packed_minus_axial_change": mean(delta),
        "paired_change_sample_sd": stdev(delta), "exact_two_sided_sign_flip_p": sign_flip(delta)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=Path(__file__).resolve().parents[1] /
                   "results/allen15_repacking/seed_metrics.csv")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = json.dumps(summarize(args.input), indent=2, allow_nan=False) + "\n"
    if args.output:
        with args.output.open("x") as f:
            f.write(result)
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
