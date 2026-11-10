"""PACK3D's logo: the website's closing word, PACK3D built from cubes, in black and white blocks.

The word is the one initEnd in website/app.js draws (5 x 7 letters, three cubes deep, the same camera), shaded
in three greys instead of the memory ramp: fronts in ink, tops light, sides dark. Run from anywhere:

    python tools/logo.py            writes website/logo.svg and website/favicon.svg
    python tools/logo.py --inline   also prints the compact logo and mark that index.html and 404.html carry
                                    inline in their bars

website/logo.svg draws every cube with a seam of paper between its faces, for large sizes. The inline logo
is two cubes deep, merges each face run into one shape and has no seams, so its letters stay open and crisp
at the bar's 22px; it takes its greys from the page's --logo-* tokens, so it follows the theme. The mark, a
single cube, is the favicon and stands in for the word where the bar is too narrow for it.
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
LIGHT = {"top": "#BDBDBD", "front": "#111111", "side": "#555555", "seam": "#F4F4F4"}
DARK = {"top": "#A6A6A6", "front": "#EDEDED", "side": "#5E5E5E", "seam": "#0E0E0E"}


def pixels(word="PACK3D"):
    """The word's letter pixels as (x, z), z up."""
    return {(ci * (GW + 1) + gx, GH - 1 - gy)
            for ci, ch in enumerate(word) for gy, line in enumerate(GLYPH[ch])
            for gx, c in enumerate(line) if c == "#"}


def project(x, y, z):
    return (x * CA - y * SA, EL * (x * SA + y * CA) - z)


def faces(px, depth=DEPTH):
    """Every cube's visible faces, far first, as (tone, four corners): the painter's order initEnd uses."""
    cubes = {(x, y, z) for x, z in px for y in range(depth)}
    out = []
    for x, y, z in cubes:
        depth = x * SA + y * CA + z * EL
        if (x, y, z + 1) not in cubes:
            out.append((depth, 0, "top", [(x, y, z + 1), (x + 1, y, z + 1), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)]))
        if (x, y + 1, z) not in cubes:
            out.append((depth, 1, "front", [(x, y + 1, z + 1), (x + 1, y + 1, z + 1), (x + 1, y + 1, z), (x, y + 1, z)]))
        if (x + 1, y, z) not in cubes:
            out.append((depth, 2, "side", [(x + 1, y, z + 1), (x + 1, y + 1, z + 1), (x + 1, y + 1, z), (x + 1, y, z)]))
    out.sort(key=lambda f: (f[0], f[1]))
    return [(tone, corners) for _, _, tone, corners in out]


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


def merged(px, depth=DEPTH):
    """The visible surface as runs, one shape per run, by tone: sides, then tops, then fronts. No front is ever
    hidden by a side or a top, so that order draws what the painter's order draws (checked when made)."""
    sides = [[(x + 1, 0, z1 + 1), (x + 1, depth, z1 + 1), (x + 1, depth, z0), (x + 1, 0, z0)]
             for x, z0, z1 in runs([p for p in px if (p[0] + 1, p[1]) not in px], lambda p: p[0], lambda p: p[1])]
    tops = [[(x0, 0, z + 1), (x1 + 1, 0, z + 1), (x1 + 1, depth, z + 1), (x0, depth, z + 1)]
            for z, x0, x1 in runs([p for p in px if (p[0], p[1] + 1) not in px], lambda p: p[1], lambda p: p[0])]
    fronts = [[(x0, depth, z + 1), (x1 + 1, depth, z + 1), (x1 + 1, depth, z), (x0, depth, z)]
              for z, x0, x1 in runs(list(px), lambda p: p[1], lambda p: p[0])]
    return [("side", sides), ("top", tops), ("front", fronts)]


def frame(corner_lists, height):
    """A scale and an offset that set the drawing `height` tall, from its top left corner."""
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


def logo_svg(height=200):
    """The full logo, every cube seamed with paper; light and dark by the reader's scheme."""
    fs = faces(pixels())
    k, width, to = frame([c for _, c in fs], height)
    style = (f".top{{fill:{LIGHT['top']}}}.front{{fill:{LIGHT['front']}}}.side{{fill:{LIGHT['side']}}}"
             f"g{{stroke:{LIGHT['seam']}}}@media (prefers-color-scheme:dark){{.top{{fill:{DARK['top']}}}"
             f".front{{fill:{DARK['front']}}}.side{{fill:{DARK['side']}}}g{{stroke:{DARK['seam']}}}}}")
    body = "".join(f'<path class="{tone}" d="M{"L".join(to(c) for c in cs)}Z"/>' for tone, cs in fs)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.2f} {height}" width="{width:.0f}" '
            f'height="{height}" role="img" aria-label="PACK3D"><title>PACK3D</title><style>{style}</style>'
            f'<g stroke-width="{0.06 * k:.2f}" stroke-linejoin="round">{body}</g></svg>\n')


def inline_logo(height=22, depth=2):
    """The bar's logo: the merged runs, filled from the page's --logo-* tokens."""
    shapes = merged(pixels(), depth)
    _, width, to = frame([c for _, polys in shapes for c in polys], height)
    body = "".join(f'<path fill="var(--logo-{tone})" d="{path(polys, to)}"/>' for tone, polys in shapes)
    return (f'<svg class="logo" viewBox="0 0 {width:.2f} {height}" width="{width:.1f}" height="{height}" '
            f'aria-hidden="true">{body}</svg>')


MARK = {  # one cube, in the classic three-face view, on a 20-unit square
    "top": "M10 1.5 18 6l-8 4.4L2 6z",
    "front": "M2 6l8 4.4V19L2 14.6z",
    "side": "M18 6l-8 4.4V19l8-4.4z",
}


def mark_svg():
    """The favicon: the mark, light and dark by the reader's scheme."""
    style = (f".top{{fill:{LIGHT['top']}}}.front{{fill:{LIGHT['front']}}}.side{{fill:{LIGHT['side']}}}"
             f"@media (prefers-color-scheme:dark){{.top{{fill:{DARK['top']}}}.front{{fill:{DARK['front']}}}"
             f".side{{fill:{DARK['side']}}}}}")
    body = "".join(f'<path class="{tone}" d="{d}"/>' for tone, d in MARK.items())
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><style>{style}</style>{body}</svg>\n'


def inline_mark():
    """The bar's mark, filled from the page's --logo-* tokens."""
    body = "".join(f'<path fill="var(--logo-{tone})" d="{d}"/>' for tone, d in MARK.items())
    return f'<svg class="mark" viewBox="0 0 20 20" aria-hidden="true">{body}</svg>'


def main():
    (ROOT / "website/logo.svg").write_text(logo_svg())
    (ROOT / "website/favicon.svg").write_text(mark_svg())
    print("wrote website/logo.svg and website/favicon.svg")
    if "--inline" in sys.argv:
        print(inline_logo())
        print(inline_mark())


if __name__ == "__main__":
    main()
