"""Regenerate the README figure from the November 18 paired H200 measurements."""
import json
from pathlib import Path
from statistics import median, quantiles

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "benchmarks/results/h200_2026-11-18.json"
FIGURE = ROOT / "docs/assets/h200-attention-latency.png"
BACKGROUND = "#F9F8F4"
INK = "#191A18"
MUTED = "#66655F"
GRID = "#D4D2C9"
SERIES = (
    ("indexed", "Indexed backward", "#EF6B35", -.17),
    ("spatial_tiles", "Spatially tiled backward", "#639B8B", .17),
)
PACKING = {"raster_block": "Raster", "native_block_morton": "Native Morton"}


def main():
    report = json.loads(REPORT.read_text())
    runs = report["protocol"]["samples_per_path"]
    workloads = sorted(report["workloads"], key=lambda w: (
        w["tokens"], w["dtype"], w["layout"] != "raster_block"))
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.facecolor": BACKGROUND,
        "figure.facecolor": BACKGROUND,
    })
    fig, ax = plt.subplots(figsize=(10.8, 7.4))
    fig.subplots_adjust(left=.355, right=.947, top=.735, bottom=.235)
    fig.add_artist(Rectangle((.018, .115), .964, .865, transform=fig.transFigure,
                             fill=False, edgecolor=INK, linewidth=.8))
    fig.text(.052, .93, "PACK3D attention", fontsize=19, weight="bold", va="center")
    fig.text(.947, .93, "NVIDIA H200", fontsize=14, color=MUTED, ha="right", va="center")
    fig.text(.052, .885, "Whole-layer forward + backward", fontsize=11, color=MUTED)
    fig.text(.947, .885, f"Batch size 1 · {runs} paired runs", fontsize=11,
             color=MUTED, ha="right")
    handles = [Line2D([], [], marker="o", linestyle="none", markersize=9,
                      markerfacecolor=color, markeredgecolor=INK, markeredgewidth=.8,
                      label=label) for _, label, color, _ in SERIES]
    fig.legend(handles=handles, loc="center right", bbox_to_anchor=(.947, .812),
               ncol=2, frameon=False, borderaxespad=0, handlelength=1,
               handletextpad=.6, columnspacing=1.8, fontsize=11)

    labels = blended_transform_factory(fig.transFigure, ax.transData)
    for xpos, label in ((.052, "Tokens"), (.174, "Packing · precision")):
        fig.text(xpos, .755, label, fontsize=10, color=MUTED)
    previous, row = None, 0.
    for work in workloads:
        if previous is not None and work["tokens"] != previous:
            ax.plot([.052, .947], [row - .32, row - .32], transform=labels,
                    color=GRID, linewidth=.65, clip_on=False, zorder=0)
            row += .36
        if work["tokens"] != previous:
            ax.text(.052, row, f'{work["tokens"]:,}', transform=labels, va="center",
                    fontsize=12, weight="bold")
        ax.text(.174, row, f'{PACKING[work["layout"]]} · {work["dtype"].upper()}',
                transform=labels, va="center", fontsize=10.5)
        for key, _, color, offset in SERIES:
            samples = work[key]["samples_ms"]
            mid = median(samples)
            if len(samples) != runs or mid != work[key]["median_ms"]:
                raise ValueError(f"Inconsistent timing samples for {key} at {work['tokens']} tokens")
            lo, _, hi = quantiles(samples, n=4, method="inclusive")
            y = row + offset
            ax.hlines(y, 0, mid, color=color, linewidth=2.1, zorder=2)
            ax.plot(mid, y, marker="o", markersize=8.5, markerfacecolor=color,
                    markeredgecolor=INK, markeredgewidth=.8, zorder=3)
            ax.errorbar(mid, y, xerr=[[mid - lo], [hi - mid]], fmt="none", color=INK,
                        elinewidth=.8, capsize=2.2, capthick=.8, zorder=4)
            ax.text(max(mid + .65, hi + .4), y, f"{mid:.2f}", va="center", fontsize=10)
        row += 1
        previous = work["tokens"]

    ax.set_ylim(row - .42, -.52)
    ax.set_xlim(0, 32.8)
    ax.set_xticks(range(0, 31, 5))
    ax.set_yticks([])
    ax.set_xlabel("Median time (ms) · Lower is better", fontsize=11.5, labelpad=14)
    ax.tick_params(axis="x", colors=MUTED, labelsize=10, length=0, pad=9)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=GRID, linewidth=.65)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK)
        ax.spines[side].set_linewidth(.8)
    fig.text(.5, .065, f"Each dot is the median of {runs} paired timings on a shared GPU. "
             "Whiskers show the middle 50%.", fontsize=10, color=MUTED, ha="center")
    fig.text(.5, .035, "The 4,096-token run uses the small preset. "
             "Larger runs use the Allen-15 preset.", fontsize=10, color=MUTED, ha="center")
    fig.savefig(FIGURE, dpi=200, facecolor=BACKGROUND)
    plt.close(fig)


if __name__ == "__main__":
    main()
