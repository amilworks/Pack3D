"""PACK3D's logo: the website's closing word, PACK3D built from cubes, in the closing word's own colors.

The word is the one initEnd in website/app.js draws: letters of 5 x 7 cubes, three cubes deep, seen by the
same camera, each cube colored by its memory position under raster order on the memory ramp, its top mixed
toward white and its side toward black, as there. Run from anywhere:

    python tools/logo.py            writes website/logo.svg, website/logo-dark.svg and website/favicon.svg
    python tools/logo.py --inline   also prints the logo and mark the bars of index.html and 404.html carry
                                    inline, and the rules that color them

logo.svg, for light backgrounds, takes the light page's ramp; logo-dark.svg, for dark ones, the dark page's.
Both draw every cube with a seam of their paper between its faces. The inline logo draws each run of faces
as one shape and gives a row of cubes one color, mixed from the page's --mem-* tokens, so it follows the
theme and stays crisp at the bar's 22px. The mark, one cube in the ramp's middle color, is the favicon and
stands in for the word where the bar is too narrow for it. Keep LIGHT and DARK in step with the --mem-*
tokens in website/index.html.
"""
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
GLYPH = {
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
}
GW, GH, DEPTH = 5, 7, 3
AZ = math.radians(18)
CA, SA, EL = math.cos(AZ), math.sin(AZ), 0.3
LIGHT = {"mem": ["#C9BAF3", "#9C84E6", "#7356D6", "#4B3AB0", "#271D69"], "paper": "#F4F4F4"}
DARK = {"mem": ["#4B3AB0", "#7356D6", "#9A7DE6", "#C9B6F4", "#F7F3FE"], "paper": "#0E0E0E"}
TOP, SIDE = 0.28, 0.38   # a top mixed toward white, a side toward black, as initEnd shades them


# ---------------------------------------------------------------- color in OKLab, as in website/app.js
def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def lab(hexcolor):
    r, g, b = (_lin(int(hexcolor[i:i + 2], 16) / 255) for i in (1, 3, 5))
    l_, m, s = (math.copysign(abs(v) ** (1 / 3), v) for v in (
        0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b,
        0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b,
        0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b))
    return (0.2104542553 * l_ + 0.793617785 * m - 0.0040720468 * s,
            1.9779984951 * l_ - 2.428592205 * m + 0.4505937099 * s,
            0.0259040371 * l_ + 0.7827717662 * m - 0.808675766 * s)


def hexof(c):
    L, a, b = c
    l_, m, s = ((L + 0.3963377774 * a + 0.2158037573 * b) ** 3, (L - 0.1055613458 * a - 0.0638541728 * b) ** 3,
                (L - 0.0894841775 * a - 1.291485548 * b) ** 3)
    rgb = (4.0767416621 * l_ - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l_ + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l_ - 0.7034186147 * m + 1.707614701 * s)
    return "#" + "".join(f"{round(min(1, max(0, _gam(min(1, max(0, v))))) * 255):02X}" for v in rgb)


def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def ramp(stops, t):
    t = min(1, max(0, t))
    x = t * (len(stops) - 1)
    i = min(len(stops) - 2, int(x))
    return mix(lab(stops[i]), lab(stops[i + 1]), x - i)


def shades(base):
    return {"top": hexof(mix(base, lab("#FFFFFF"), TOP)), "front": hexof(base), "side": hexof(mix(base, lab("#000000"), SIDE))}


# ---------------------------------------------------------------- the word and its camera
def pixels(word="PACK3D"):
    """The word's letter pixels as (x, z), z up."""
    return {(ci * (GW + 1) + gx, GH - 1 - gy)
            for ci, ch in enumerate(word) for gy, line in enumerate(GLYPH[ch])
            for gx, c in enumerate(line) if c == "#"}


def project(x, y, z):
    return (x * CA - y * SA, EL * (x * SA + y * CA) - z)


def ranks(px, depth=DEPTH):
    """Each cube's memory position under raster order (z, then y, then x), and the count."""
    width = max(x for x, _ in px) + 1
    order = sorted(((z * depth + y) * width + x, (x, y, z)) for x, z in px for y in range(depth))
    return {c: i for i, (_, c) in enumerate(order)}, len(order)


def faces(px, depth=DEPTH):
    """Every cube's visible faces, far first, as (cube, tone, four corners): the painter's order initEnd uses."""
    cubes = {(x, y, z) for x, z in px for y in range(depth)}
    out = []
    for x, y, z in cubes:
        d = x * SA + y * CA + z * EL
        if (x, y, z + 1) not in cubes:
            out.append((d, 0, (x, y, z), "top", [(x, y, z + 1), (x + 1, y, z + 1), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)]))
        if (x, y + 1, z) not in cubes:
            out.append((d, 1, (x, y, z), "front", [(x, y + 1, z + 1), (x + 1, y + 1, z + 1), (x + 1, y + 1, z), (x, y + 1, z)]))
        if (x + 1, y, z) not in cubes:
            out.append((d, 2, (x, y, z), "side", [(x + 1, y, z + 1), (x + 1, y + 1, z + 1), (x + 1, y + 1, z), (x + 1, y, z)]))
    out.sort(key=lambda f: (f[0], f[1]))
    return [f[2:] for f in out]


def runs(cells, key, step):
    """Group cells into straight runs: cells sharing key(cell), consecutive along step(cell)."""
    groups = {}
    for c in cells:
        groups.setdefault(key(c), []).append(step(c))
    for k, steps in groups.items():
        steps.sort()
        start = prev = steps[0]
        for s in steps[1:] + [None]:
            if s is not None and s == prev + 1:
                prev = s
                continue
            yield k, start, prev
            if s is not None:
                start = prev = s


def rows(px, depth=DEPTH):
    """The visible surface as one shape per run, a row of cubes to a color: {(tone, row): shapes}, sides, then tops,
    then fronts, each tone from the bottom row up. No front is ever hidden by a side or a top, sides and fronts
    never overlap one another, and a top overlaps another only under the next row up and to its right, which is
    nearer; so that order draws what the painter's order draws (checked when made)."""
    out = {}
    for x, z in sorted(p for p in px if (p[0] + 1, p[1]) not in px):
        out.setdefault(("side", z), []).append([(x + 1, 0, z + 1), (x + 1, depth, z + 1), (x + 1, depth, z), (x + 1, 0, z)])
    for z, x0, x1 in runs([p for p in px if (p[0], p[1] + 1) not in px], lambda p: p[1], lambda p: p[0]):
        out.setdefault(("top", z), []).append([(x0, 0, z + 1), (x1 + 1, 0, z + 1), (x1 + 1, depth, z + 1), (x0, depth, z + 1)])
    for z, x0, x1 in runs(list(px), lambda p: p[1], lambda p: p[0]):
        out.setdefault(("front", z), []).append([(x0, depth, z + 1), (x1 + 1, depth, z + 1), (x1 + 1, depth, z), (x0, depth, z)])
    order = {"side": 0, "top": 1, "front": 2}
    return dict(sorted(out.items(), key=lambda kv: (order[kv[0][0]], kv[0][1])))


def frame(corner_lists, height):
    """A scale and a map that set the drawing `height` tall, from its top left corner."""
    pts = [project(*c) for cs in corner_lists for c in cs]
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    k = height / (max(p[1] for p in pts) - y0)
    width = (max(p[0] for p in pts) - x0) * k

    def to(c):
        sx, sy = project(*c)
        return f"{(sx - x0) * k:.2f} {(sy - y0) * k:.2f}".replace(".00", "")
    return k, width, to


def path(polys, to):
    return "".join("M" + "L".join(to(c) for c in poly) + "Z" for poly in polys)


# ---------------------------------------------------------------- the forms
def logo_svg(theme, height=200):
    """The full logo on one theme's ramp, every cube seamed with that theme's paper."""
    px = pixels()
    rank, n = ranks(px)
    fs = faces(px)
    k, width, to = frame([c for _, _, c in fs], height)
    color = {cube: shades(ramp(theme["mem"], r / (n - 1))) for cube, r in rank.items()}
    body = "".join(f'<path fill="{color[cube][tone]}" d="M{"L".join(to(c) for c in cs)}Z"/>' for cube, tone, cs in fs)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.2f} {height}" width="{width:.0f}" '
            f'height="{height}" role="img" aria-label="PACK3D"><title>PACK3D</title>'
            f'<g stroke="{theme["paper"]}" stroke-width="{0.06 * k:.2f}" stroke-linejoin="round">{body}</g></svg>\n')


def row_mix(px, depth=DEPTH):
    """Each row's color as a mix of two --mem-* tokens, at the middle of that row's memory positions."""
    rank, n = ranks(px, depth)
    rules = []
    for z in sorted({z for _, _, z in rank}):
        rs = [r for (_, _, cz), r in rank.items() if cz == z]
        x = (min(rs) + max(rs)) / 2 / (n - 1) * 4
        i = min(3, int(x))
        rules.append(f".logo .r{z} {{ --c: color-mix(in oklab, var(--mem-{i}) {round((1 - (x - i)) * 100, 1)}%, var(--mem-{i + 1})); }}")
    return rules


def inline_logo(height=22, depth=DEPTH):
    """The bar's logo: one shape per run, each row of cubes colored by the rules row_mix() writes."""
    shapes = rows(pixels(), depth)
    _, width, to = frame([c for polys in shapes.values() for c in polys], height)
    body = "".join(f'<path class="{tone[0]} r{z}" d="{path(polys, to)}"/>' for (tone, z), polys in shapes.items())
    return (f'<svg class="logo" viewBox="0 0 {width:.2f} {height}" width="{width:.1f}" height="{height}" '
            f'aria-hidden="true">{body}</svg>')


MARK = {  # one cube, in the classic three-face view, on a 20-unit square
    "top": "M10 1.5 18 6l-8 4.4L2 6z",
    "front": "M2 6l8 4.4V19L2 14.6z",
    "side": "M18 6l-8 4.4V19l8-4.4z",
}


def mark_svg():
    """The favicon: one cube in the light ramp's middle color, which reads on a light tab and a dark one."""
    col = shades(lab(LIGHT["mem"][2]))
    body = "".join(f'<path fill="{col[tone]}" d="{d}"/>' for tone, d in MARK.items())
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">{body}</svg>\n'


def inline_mark():
    """The bar's mark, colored by the same rules as the logo, in the ramp's middle color."""
    body = "".join(f'<path class="{tone[0]}" d="{d}"/>' for tone, d in MARK.items())
    return f'<svg class="mark" viewBox="0 0 20 20" aria-hidden="true">{body}</svg>'


def rules():
    """The rules that color the inline logo and mark from the page's --mem-* tokens."""
    return "\n".join(row_mix(pixels()) + [
        ".mark { --c: var(--mem-2); }",
        ":is(.logo, .mark) .f { fill: var(--c); }",
        f":is(.logo, .mark) .t {{ fill: color-mix(in oklab, var(--c) {round((1 - TOP) * 100)}%, #FFFFFF); }}",
        f":is(.logo, .mark) .s {{ fill: color-mix(in oklab, var(--c) {round((1 - SIDE) * 100)}%, #000000); }}",
    ])


def main():
    (ROOT / "website/logo.svg").write_text(logo_svg(LIGHT))
    (ROOT / "website/logo-dark.svg").write_text(logo_svg(DARK))
    (ROOT / "website/favicon.svg").write_text(mark_svg())
    print("wrote website/logo.svg, website/logo-dark.svg and website/favicon.svg")
    if "--inline" in sys.argv:
        print(inline_logo())
        print(inline_mark())
        print(rules())


if __name__ == "__main__":
    main()
