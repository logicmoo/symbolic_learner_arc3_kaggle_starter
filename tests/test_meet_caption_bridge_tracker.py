"""Regression tests for scripts/meet_caption_bridge.py's CaptionTracker.

Covers the "trap and relay raw changes" caption pipeline: cold-start
baselining, real-time growth relay under a single DOM row's key, and the
sentence-boundary "clone the line" split that gives the completed sentence
the OLD key and starts a brand-new key for whatever the row grows into
next — verified live against a real Google Meet call growing exactly one
DOM row for an entire monologue (see plan.md Google Meet bridge rounds).
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))

import meet_caption_bridge as bridge  # noqa: E402


def _tracker() -> bridge.CaptionTracker:
    return bridge.CaptionTracker(settle=1.2)


def _row(key: str, text: str, speaker: str = "Alice") -> dict[str, str]:
    return {"key": key, "speaker": speaker, "text": text}


def _recorder() -> tuple[list[tuple[str, str, str, bool, str | None]], object]:
    """`emit(key, speaker, text, final=..., replaces=...)` — record as a
    tuple including both extra fields: `final` (True = completed "phrase"
    that won't be touched again; False = still-growing live remainder) and
    `replaces` (the key this one continues from, None for a row's very
    first/original key)."""
    emits: list[tuple[str, str, str, bool, str | None]] = []

    def emit(key: str, speaker: str, text: str, final: bool = False, replaces: str | None = None) -> None:
        emits.append((key, speaker, text, final, replaces))

    return emits, emit


def test_cold_start_baselines_silently() -> None:
    tracker = _tracker()
    emits, emit = _recorder()
    tracker.update([_row("row1", "already on screen when we attached")], [], emit)
    assert emits == []
    assert tracker.baselined is True


def test_growth_relays_immediately_under_the_same_key() -> None:
    tracker = _tracker()
    emits, emit = _recorder()
    tracker.update([_row("row1", "")], [], emit)
    tracker.update([_row("row1", "Hello")], [], emit)
    tracker.update([_row("row1", "Hello there")], [], emit)
    assert emits == [
        ("row1", "Alice", "Hello", False, None),
        ("row1", "Alice", "Hello there", False, None),
    ]


def test_sentence_boundary_freezes_the_old_key_and_starts_a_new_one() -> None:
    """The core "break this single line after a full sentence" behavior:
    once growth crosses a `.`/`!`/`?`, the completed sentence is emitted
    (final=True) under the key that had been growing, and everything
    after it moves to a brand-new key — the old key never receives
    another update. The new key's `replaces` points back at the old one,
    making the chain explicit for a consumer."""
    tracker = _tracker()
    emits, emit = _recorder()
    tracker.update([_row("row1", "")], [], emit)
    for text in ("Hello", "Hello there", "Hello there.", "Hello there. How", "Hello there. How are you?"):
        tracker.update([_row("row1", text)], [], emit)

    keys = [e[0] for e in emits]
    assert keys == ["row1", "row1", "row1", "row1#1", "row1#1"]
    assert emits[2] == ("row1", "Alice", "Hello there.", True, None)  # old key's FINAL phrase
    assert emits[-1] == ("row1#1", "Alice", "How are you?", True, "row1")
    # Every non-final (still-growing) update along the way is flagged False.
    assert [e[3] for e in emits[:2]] == [False, False]
    assert emits[3] == ("row1#1", "Alice", "How", False, "row1")

    # The old key must never be touched again even as the row keeps growing.
    tracker.update([_row("row1", "Hello there. How are you? I am fine.")], [], emit)
    assert emits[-1][0] == "row1#2"
    assert emits[-1][3] is True
    assert emits[-1][4] == "row1#1"  # continues from the previous phrase's key


def test_multiple_sentences_completed_in_one_poll_are_dished_out_in_order() -> None:
    """Meet can jump by more than one sentence between two polls (e.g. a
    slow poll interval) — every completed sentence must still get its own
    key, dispatched in order, not merged into a single event, and each
    chained to the one before it via `replaces`."""
    tracker = _tracker()
    emits, emit = _recorder()
    tracker.update([_row("row1", "")], [], emit)
    tracker.update([_row("row1", "First one. Second one. Third starts")], [], emit)

    assert emits == [
        ("row1", "Alice", "First one.", True, None),
        ("row1#1", "Alice", "Second one.", True, "row1"),
        ("row1#2", "Alice", "Third starts", False, "row1#1"),
    ]


def test_forgotten_row_cleans_up_all_internal_state() -> None:
    tracker = _tracker()
    emits, emit = _recorder()
    tracker.update([_row("row1", "")], [], emit)
    tracker.update([_row("row1", "Hello there.")], [], emit)
    assert "row1" in tracker.raw

    # The row disappears from the live DOM entirely (scrolled away).
    tracker.update([], [], emit)
    assert "row1" not in tracker.raw
    assert "row1" not in tracker.settled_len
    assert "row1" not in tracker.active_key
    assert "row1" not in tracker.clone_seq


def test_no_op_when_text_is_unchanged() -> None:
    tracker = _tracker()
    emits, emit = _recorder()
    tracker.update([_row("row1", "")], [], emit)
    tracker.update([_row("row1", "Hello there")], [], emit)
    tracker.update([_row("row1", "Hello there")], [], emit)  # repeat, unchanged
    assert emits == [("row1", "Alice", "Hello there", False, None)]
