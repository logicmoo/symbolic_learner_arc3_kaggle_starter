"""Occlusion-completion demonstration (SOW section 8).

Run:  python scripts/occlusion_completion_demo.py

Shows a partly-occluded object being re-recognized and its hidden geometry
generatively completed: the held form is hypothesized from the visible fragment,
run forward to fill the cells behind the occluder, and accepted only when every
filled cell lies under the occluder. A consistent completion locks with a low
residual; an inconsistent fragment is rejected (re-categorized as new).
"""
from __future__ import annotations

import sys
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1] / "workbench" / "server" / "generative_vision" / "prolog"
sys.path.insert(0, str(_SERVER))

import symbolic_arc as sa  # noqa: E402


def _grid(visible, occluded, filled=()):
    """ASCII: '#' visible object cell, '?' occluder (hidden), '+' completed cell."""
    vis, occ, fil = set(map(tuple, visible)), set(map(tuple, occluded)), set(map(tuple, filled))
    xs = [x for x, _ in vis | occ | fil] or [0]
    ys = [y for _, y in vis | occ | fil] or [0]
    lines = []
    for y in range(min(ys), max(ys) + 1):
        row = []
        for x in range(min(xs), max(xs) + 1):
            row.append("+" if (x, y) in fil else "#" if (x, y) in vis else "?" if (x, y) in occ else ".")
        lines.append("  " + "".join(row))
    return "\n".join(lines)


def _demo(title, full, hidden, candidate=None):
    full_s = set(map(tuple, full))
    hidden_s = set(map(tuple, hidden))
    fragment = sorted(full_s - hidden_s)             # what the camera actually sees
    cand = {tuple(sa._canon_key(candidate)): sa._name_of_cells(candidate)} if candidate else None
    r = sa.complete_occluded(fragment, sorted(hidden_s), candidates=cand)
    print(f"\n=== {title} ===")
    print("occluded view (# seen, ? behind occluder):")
    print(_grid(fragment, hidden_s))
    if not r:
        print("result: NO consistent completion -> re-categorize as NEW object")
        return
    print(f"recognized: {r['name']}  scale={r['scale']}  orientation={r['orientation']}")
    print(f"residual (hidden cells filled): {r['residual']}   confidence (visible fraction): {r['confidence']}")
    print("completed object (# seen, + generatively filled):")
    print(_grid(r["visible"], [], r["filled"]))
    ok = set(map(tuple, r["cells"])) == set(map(tuple, sa._norm(full)))
    print(f"faithful reconstruction of the whole object: {ok}")


def main() -> None:
    T = [(0, 0), (1, 0), (2, 0), (1, 1)]                                  # T tetromino
    plus = [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)]                       # + pentomino
    T2 = [(x * 2 + dx, y * 2 + dy) for (x, y) in T for dx in range(2) for dy in range(2)]

    _demo("T tetromino, stem occluded", T, [(1, 1)], candidate=T)
    _demo("Plus pentomino, centre + one arm occluded", plus, [(1, 1), (1, 0)], candidate=plus)
    _demo("2x-scaled T, scaled stem block occluded", T2, [(2, 2), (3, 2), (2, 3), (3, 3)], candidate=T)
    # inconsistent: the 'hidden' region does not actually cover the cell the form needs
    print("\n=== Inconsistent fragment (occluder elsewhere) ===")
    frag = [(0, 0), (1, 0), (2, 0)]
    bad = sa.complete_occluded(frag, [(9, 9)], candidates={tuple(sa._canon_key(T)): "tetromino_T"})
    print("occluded view:"); print(_grid(frag, [(9, 9)]))
    print(f"result: {bad!r}  -> rejected (no lock), re-categorized as new")


if __name__ == "__main__":
    main()
