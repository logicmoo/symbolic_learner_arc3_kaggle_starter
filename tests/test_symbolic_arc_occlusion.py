"""Occlusion-completion tests (SOW section 8): a partly-occluded object is
re-recognized and its hidden geometry is generatively completed by running the
held form forward, accepted only when every filled cell lies under the occluder.
A consistent completion locks with a low residual; an inconsistent one is
rejected (re-categorized)."""
import sys
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1] / "workbench" / "server" / "generative_vision" / "prolog"
sys.path.insert(0, str(_SERVER))

import symbolic_arc as sa  # noqa: E402

_T = [(0, 0), (1, 0), (2, 0), (1, 1)]          # a T tetromino (the full held object)


def _cand(cells):
    return {tuple(sa._canon_key(cells)): sa._name_of_cells(cells)}


def test_completes_partly_occluded_object():
    """The stem of a T is hidden behind an occluder; the form is completed to the
    full T, filling exactly the occluded cell."""
    frag = [(0, 0), (1, 0), (2, 0)]
    occ = [(1, 1)]
    r = sa.complete_occluded(frag, occ, candidates=_cand(_T))
    assert r is not None
    assert r["name"] == "tetromino_T"
    assert r["filled"] == [(1, 1)]
    assert r["residual"] == 1
    assert set(map(tuple, r["cells"])) == set(map(tuple, sa._norm(_T)))  # recovered whole object


def test_rejects_inconsistent_completion():
    """If the hidden cell the form needs is NOT under the occluder, the completion
    is inconsistent and rejected (returns None -> re-categorize as new)."""
    frag = [(0, 0), (1, 0), (2, 0)]
    assert sa.complete_occluded(frag, [(9, 9)], candidates=_cand(_T)) is None


def test_confidence_scales_with_visible_fraction():
    """More visible -> higher confidence (lower residual)."""
    cand = _cand(_T)
    more = sa.complete_occluded([(0, 0), (1, 0), (2, 0)], [(1, 1)], candidates=cand)   # 3/4 visible
    less = sa.complete_occluded([(0, 0), (1, 0)], [(2, 0), (1, 1)], candidates=cand)   # 2/4 visible
    assert more["confidence"] > less["confidence"]
    assert more["residual"] < less["residual"]


def test_completion_is_scale_invariant():
    """A 2x-scaled object with a scaled block occluded still completes to the base
    form at scale 2."""
    T2 = [(x * 2 + dx, y * 2 + dy) for (x, y) in _T for dx in range(2) for dy in range(2)]
    hidden = [(2, 2), (3, 2), (2, 3), (3, 3)]      # the scaled stem block
    frag = [c for c in T2 if tuple(c) not in set(map(tuple, hidden))]
    r = sa.complete_occluded(frag, hidden, candidates=_cand(_T))
    assert r is not None
    assert r["name"] == "tetromino_T"
    assert r["scale"] == 2
    assert set(map(tuple, r["cells"])) == set(map(tuple, sa._norm(T2)))


def test_completes_against_the_held_vocabulary():
    """With no explicit candidate, completion searches the held vocabulary and
    returns a consistent account: the visible fragment is fully covered and every
    filled cell lies under the occluder (recognition = reduction to a held form).
    The cheapest such account wins, so completing to a *specific* expected object
    is driven by passing that object as the candidate (see the tests above)."""
    frag = [(0, 1), (2, 1), (1, 2)]                 # three disconnected arm cells
    occ = [(1, 0), (1, 1)]                          # centre + top hidden
    r = sa.complete_occluded(frag, occ)             # search the whole vocabulary
    assert r is not None
    placed = set(map(tuple, r["cells"]))
    assert set(map(tuple, frag)) <= placed          # fragment explained
    assert set(map(tuple, r["filled"])) <= set(map(tuple, occ))  # filled only under occluder
    assert r["residual"] == len(r["filled"]) >= 1   # something was genuinely completed
