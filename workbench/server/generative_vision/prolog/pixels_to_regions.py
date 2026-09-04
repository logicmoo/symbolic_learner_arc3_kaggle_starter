"""pixels_to_regions.py — bbox-FREE perception for any image (ARC, cartoon, CGI).

No bounding boxes anywhere. We quantize colors, label every connected region,
then derive PURELY TOPOLOGICAL facts from the pixels:

  region(Id, Color, Area, centroid(CX,CY)).
  adjacent(A, B).        % some pixel of A is 4-adjacent to some pixel of B
  encloses(Outer, Inner).% Inner's only neighbour is Outer and it never touches
                         % the image edge -> Outer completely surrounds Inner
  border(Id).            % region has a pixel on the image edge
  img_size(W, H).

Prolog then reasons over adjacency + enclosure — never a box. Optionally also
emit the quantized cell/3 grid (--grid) for full pixel fidelity.

Usage:
    python pixels_to_regions.py IMG.png --colors 14 --smooth 3 --minfrac 0.0008 --prolog out.pl
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

STRUCT4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])


def quantize(img: Image.Image, n_colors: int, smooth: int):
    rgb = img.convert("RGB")
    if smooth > 0:
        rgb = rgb.filter(ImageFilter.MedianFilter(size=smooth))
    q = rgb.quantize(colors=n_colors, method=Image.MEDIANCUT)
    idx = np.array(q)
    pal = q.getpalette()[: n_colors * 3]
    colors = [(pal[i], pal[i + 1], pal[i + 2]) for i in range(0, len(pal), 3)]
    return idx, colors


def label_map(idx: np.ndarray, colors):
    """Assign every pixel a globally-unique region label; collect per-region
    color / area / centroid / border-touch (no bbox)."""
    h, w = idx.shape
    labels = np.zeros((h, w), dtype=np.int32)
    info: dict[int, dict] = {}
    nxt = 1
    for ci in np.unique(idx):
        lab, n = ndimage.label(idx == ci, structure=STRUCT4)
        for comp in range(1, n + 1):
            sel = lab == comp
            gid = nxt
            nxt += 1
            labels[sel] = gid
            ys, xs = np.where(sel)
            r, g, b = colors[ci]
            info[gid] = {
                "color": f"#{r:02x}{g:02x}{b:02x}",
                "area": int(xs.size),
                "cx": int(round(xs.mean())),
                "cy": int(round(ys.mean())),
                "border": bool(xs.min() == 0 or ys.min() == 0 or xs.max() == w - 1 or ys.max() == h - 1),
            }
    return labels, info


def adjacency(labels: np.ndarray):
    pairs = set()
    for A, B in ((labels[:, :-1], labels[:, 1:]), (labels[:-1, :], labels[1:, :])):
        d = A != B
        if not d.any():
            continue
        u = np.stack([A[d], B[d]], axis=1)
        u.sort(axis=1)
        for a, b in np.unique(u, axis=0):
            pairs.add((int(a), int(b)))
    return pairs


def enclosures(info, neigh):
    """Inner is enclosed by Outer iff Inner never touches the edge and its ONLY
    neighbouring region is Outer — a true surround, independent of shape."""
    out = []
    for gid, i in info.items():
        if i["border"]:
            continue
        ns = neigh.get(gid, set())
        if len(ns) == 1:
            out.append((next(iter(ns)), gid))
    return out


def to_prolog(info, pairs, big: set, w: int, h: int) -> str:
    neigh = defaultdict(set)
    for a, b in pairs:
        neigh[a].add(b)
        neigh[b].add(a)
    encl = [(o, i) for (o, i) in enclosures(info, neigh) if o in big and i in big]
    L = [
        "% bbox-FREE region facts (topology only).",
        ":- dynamic region/4.", ":- dynamic adjacent/2.",
        ":- dynamic encloses/2.", ":- dynamic border/1.", ":- dynamic img_size/2.",
        f"img_size({w}, {h}).", "",
    ]
    for gid in sorted(big, key=lambda g: -info[g]["area"]):
        i = info[gid]
        L.append(f"region(r{gid}, '{i['color']}', {i['area']}, centroid({i['cx']},{i['cy']})).")
        if i["border"]:
            L.append(f"border(r{gid}).")
    L.append("")
    for a, b in sorted(pairs):
        if a in big and b in big:
            L.append(f"adjacent(r{a}, r{b}).")
    L.append("")
    for o, i in encl:
        L.append(f"encloses(r{o}, r{i}).")
    return "\n".join(L) + "\n"


def grid_to_prolog(idx: np.ndarray, colors, cell: int) -> str:
    h, w = idx.shape
    gh, gw = h // cell, w // cell
    L = ["% quantized pixel grid: cell(X, Y, Color).", ":- dynamic cell/3.", ""]
    for gy in range(gh):
        for gx in range(gw):
            block = idx[gy*cell:(gy+1)*cell, gx*cell:(gx+1)*cell]
            ci = int(np.bincount(block.ravel()).argmax())
            r, g, b = colors[ci]
            L.append(f"cell({gx}, {gy}, '#{r:02x}{g:02x}{b:02x}').")
    return "\n".join(L) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--colors", type=int, default=14)
    ap.add_argument("--minfrac", type=float, default=0.0008)
    ap.add_argument("--smooth", type=int, default=0)
    ap.add_argument("--prolog")
    ap.add_argument("--grid")
    ap.add_argument("--cell", type=int, default=1)
    args = ap.parse_args(argv)

    img = Image.open(args.image)
    w, h = img.size
    idx, colors = quantize(img, args.colors, args.smooth)
    labels, info = label_map(idx, colors)
    min_area = max(12, int(args.minfrac * w * h))
    big = {gid for gid, i in info.items() if i["area"] >= min_area}
    pairs = adjacency(labels)
    print(f"{args.image}: {w}x{h}px, {args.colors} colors (smooth={args.smooth}), "
          f"min_area={min_area}px -> {len(big)} regions, {sum(1 for a,b in pairs if a in big and b in big)} adjacencies")
    if args.prolog:
        Path(args.prolog).write_text(to_prolog(info, pairs, big, w, h), encoding="utf-8")
        print("wrote", args.prolog)
    if args.grid:
        Path(args.grid).write_text(grid_to_prolog(idx, colors, max(1, args.cell)), encoding="utf-8")
        gh, gw = h // max(1, args.cell), w // max(1, args.cell)
        print(f"wrote {args.grid}  ({gw}x{gh} = {gw*gh} cell/3 facts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
