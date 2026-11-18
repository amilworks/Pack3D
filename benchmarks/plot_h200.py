"""Regenerate the README figure from the November 18 paired H200 measurements."""
import json
from pathlib import Path
from statistics import median, quantiles

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.transforms import blended_transform_factory


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "benchmarks/results/h200_2026-11-18.json"
FIGURE = ROOT / "docs/assets/h200-attention-latency.png"
SERIES = (
    ("indexed", "Indexed backward", "#A5AAB5", -.17),
    ("spatial_tiles", "Spatially tiled backward", "#563CAF", .17),
)
PACKING = {"raster_block": "Raster", "native_block_morton": "Native Morton"}


def main():
    report = json.loads(REPORT.read_text())
    runs = report["protocol"]["samples_per_path"]
    workloads = sorted(report["workloads"], key=lambda w: (
        w["tokens"], w["dtype"], w["layout"] != "raster_block"))
    fig, ax = plt.subplots(figsize=(9.6, 6.1))
    fig.subplots_adjust(left=.365, right=.965, top=.765, bottom=.16)
    ink, muted = "#20232B", "#49505C"
    fig.text(.045, .94, "PACK3D attention latency on H200", fontsize=21, weight="bold", color=ink)
    fig.text(.045, .886, f"Whole-layer forward + backward   ·   Batch size 1   ·   {runs} paired runs",
             fontsize=12, color=muted)
    fig.legend(handles=[Patch(facecolor=color, label=label) for _, label, color, _ in SERIES],
               loc="center left", bbox_to_anchor=(.045, .829), ncol=2, frameon=False,
               borderaxespad=0, handlelength=1.3, columnspacing=2, fontsize=10)

    labels = blended_transform_factory(fig.transFigure, ax.transData)
    for xpos, label in ((.045, "Tokens"), (.173, "Packing · precision")):
        fig.text(xpos, .77, label, fontsize=10, color=muted, weight="bold")
    previous, row = None, 0.
    for work in workloads:
        if previous is not None and work["tokens"] != previous:
            ax.axhline(row - .32, color="#E4E5E9", linewidth=.8)
            row += .36
        if work["tokens"] != previous:
            ax.text(.045, row, f'{work["tokens"]:,}', transform=labels, va="center",
                    fontsize=12, weight="bold", color=ink)
        ax.text(.173, row, f'{PACKING[work["layout"]]} · {work["dtype"].upper()}',
                transform=labels, va="center", fontsize=10.7, color=ink)
        for key, _, color, offset in SERIES:
            samples = work[key]["samples_ms"]
            mid = median(samples)
            if len(samples) != runs or mid != work[key]["median_ms"]:
                raise ValueError(f"Inconsistent timing samples for {key} at {work['tokens']} tokens")
            lo, _, hi = quantiles(samples, n=4, method="inclusive")
            y = row + offset
            ax.barh(y, mid, height=.245, color=color, zorder=2)
            ax.errorbar(mid, y, xerr=[[mid - lo], [hi - mid]], fmt="none", color=ink,
                        elinewidth=.85, capsize=2, capthick=.85, zorder=3)
            ax.text(hi + .35, y, f"{mid:.2f}", va="center", fontsize=9.3,
                    color=ink if key == "indexed" else "#45298F")
        row += 1
        previous = work["tokens"]

    ax.set_ylim(row - .52, -.48)
    ax.set_xlim(0, 32.8)
    ax.set_xticks(range(0, 31, 5))
    ax.set_yticks([])
    ax.set_xlabel("Median time (ms)   ·   Lower is better", fontsize=11, color=ink, labelpad=7)
    ax.tick_params(axis="x", colors=muted, labelsize=9.5, length=0, pad=5)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color="#E4E5E9", linewidth=.75)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.axvline(0, color="#9A9FA9", linewidth=.9)
    fig.text(.045, .035, "Whiskers show the middle 50% of timings on a shared GPU. "
             "The 4,096-token run uses the small preset.", fontsize=9.5, color=muted)
    fig.savefig(FIGURE, dpi=180, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
