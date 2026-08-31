"""Two-way Google Meet <-> agent-mailbox bridge using Meet's own live captions.

Local speech recognition (scripts/stt_mailbox_listener.py, Vosk) is mediocre;
Google Meet's caption model is excellent. This script turns a Meet tab in YOUR
OWN Chrome into the recognizer — and a mouthpiece:

  IN   Meet live captions  ->  agent mailbox (one message per finished line,
       sender "meet-<speaker>"), exactly like the STT listener's messages.
  OUT  mailbox messages addressed to the bridge (default recipient
       "google-meet")  ->  posted into the Meet's in-call chat, and optionally
       spoken aloud with Windows TTS (--speak).

ALWAYS-ON: run with no arguments and the bridge keeps a meeting of its own in
the background as the STT surface — it signs into the popup browser (SSO
persists), CREATES an instant meeting, posts the join link to the mailbox,
and transcribes whoever talks in it. While running you can point it at any
other meeting by MAILBOX COMMAND — send to the "google-meet" recipient:

    /join https://meet.google.com/xxx-yyyy-zzz   switch to that meeting
    /new                                          spin up a fresh meeting

(the operator still clicks "Join now" in the popup window; the bridge
re-attaches automatically and posts where it went).

Nothing here logs into Google: you join the meeting normally in a Chrome you
started with remote debugging enabled, then the bridge attaches over the
DevTools protocol (CDP) and reads/writes the page.

Setup — two ways to connect:

  A) Let the bridge POP UP its own browser (default when --meet is given):
       python scripts/meet_caption_bridge.py --meet https://meet.google.com/xxx-yyyy-zzz
     A dedicated Chrome window opens (its own persistent profile, so your
     Google SSO login sticks between runs — you sign in ONCE and the session
     is reused until Google expires it; run with --forget-sso to wipe the
     stored login and pick an account again). Pick your account on the Google
     page, join the call, turn on captions ("c") — the bridge waits, attaches,
     and starts bridging automatically.

  B) Attach to a Chrome YOU started:
       chrome.exe --remote-debugging-port=9222
     join the Meet there, then run the bridge with no --meet argument.

For the OUT direction, open the in-call chat panel once (the bridge will
try to open it itself if it can find the button).

Usage (from the repository root):
  python scripts/meet_caption_bridge.py                      # ALWAYS-ON: create
                                                             # + join a background
                                                             # STT meeting (or
                                                             # reuse one already
                                                             # open)
  python scripts/meet_caption_bridge.py --meet <meet-url>    # join a given meet
  python scripts/meet_caption_bridge.py --new                # force-create one
  python scripts/meet_caption_bridge.py --attach-only        # never pop a browser
  python scripts/meet_caption_bridge.py --list-tabs          # show CDP tabs
  python scripts/meet_caption_bridge.py --no-out             # captions only
  python scripts/meet_caption_bridge.py --speak              # + local TTS

Transcripts are delivered through the bundled ``mailbox_chat`` agent-mailbox
client (same store the workbench Chat UI reads); AGENT_MAILBOX_DIR overrides
the mailbox directory exactly like the other listeners.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

import requests
from websocket import create_connection  # websocket-client

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CDP = "http://127.0.0.1:9222"
DEFAULT_RECIPIENTS = ["symbolic-workbench-user"]
DEFAULT_SENDER_PREFIX = "meet-"
DEFAULT_OUTBOX = "google-meet"
DEFAULT_OUT_CURSOR = "meet-bridge"


def _mailbox_client() -> Any:
    """Same resolution order as scripts/stt_mailbox_listener.py."""
    try:
        from mailbox_channels import agent_mailbox as client  # type: ignore

        return client
    except Exception:
        pass
    plugin_src = ROOT / "workbench" / "plugins" / "mailbox_chat" / "src"
    if str(plugin_src) not in sys.path:
        sys.path.insert(0, str(plugin_src))
    os.environ.setdefault("AGENT_MAILBOX_DIR", str(ROOT / "mailbox"))
    from mailbox_chat import agent_mailbox as client  # type: ignore

    return client


# --------------------------------------------------------------------------
# CDP plumbing (stdlib + websocket-client; no Playwright/Selenium needed)
# --------------------------------------------------------------------------
class CdpTab:
    def __init__(self, ws_url: str) -> None:
        # suppress_origin: Chrome rejects DevTools websocket handshakes that
        # carry a browser-style Origin header with HTTP 403.
        self.ws = create_connection(ws_url, timeout=10, suppress_origin=True)
        self._id = 0

    def call(self, method: str, params: dict[str, Any] | None = None, timeout: float = 10.0) -> Any:
        self._id += 1
        wanted = self._id
        self.ws.send(json.dumps({"id": wanted, "method": method, "params": params or {}}))
        deadline = time.time() + timeout
        while time.time() < deadline:
            payload = json.loads(self.ws.recv())
            if payload.get("id") == wanted:
                return payload.get("result")
        raise TimeoutError(f"CDP {method} timed out")

    def evaluate(self, expression: str, await_promise: bool = False, timeout: float = 10.0) -> Any:
        result = self.call(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True, "awaitPromise": await_promise},
            timeout=timeout,
        )
        return ((result or {}).get("result") or {}).get("value")

    def close(self) -> None:
        try:
            self.ws.close()
        except Exception:
            pass


def list_tabs(cdp: str) -> list[dict[str, Any]]:
    return requests.get(f"{cdp}/json", timeout=5).json()


def cdp_alive(cdp: str) -> bool:
    try:
        requests.get(f"{cdp}/json/version", timeout=2)
        return True
    except Exception:
        return False


def find_meet_tab(cdp: str) -> dict[str, Any] | None:
    for tab in list_tabs(cdp):
        if tab.get("type") == "page" and "meet.google.com" in str(tab.get("url", "")):
            return tab
    return None


# --------------------------------------------------------------------------
# SSO popup: launch a dedicated browser the operator signs into
# --------------------------------------------------------------------------
DEFAULT_PROFILE = Path.home() / ".cache" / "ws_collab_models" / "meet_bridge_profile"

BROWSER_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    str(Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_browser(explicit: str | None) -> str:
    if explicit:
        if Path(explicit).is_file():
            return explicit
        raise SystemExit(f"--browser not found: {explicit}")
    for candidate in BROWSER_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    for name in ("chrome", "msedge"):
        found = subprocess.run(["where.exe", name], capture_output=True, text=True, check=False)
        line = (found.stdout or "").strip().splitlines()
        if line:
            return line[0]
    raise SystemExit("No Chrome/Edge found — pass --browser <path to chrome.exe>")


def launch_browser(args: argparse.Namespace) -> str:
    """Pop up the bridge's own browser so the operator can pick their Google
    account (SSO); returns the CDP endpoint once it is answering."""
    port = args.port
    cdp = f"http://127.0.0.1:{port}"
    profile = Path(args.profile).expanduser()
    profile.mkdir(parents=True, exist_ok=True)
    if not cdp_alive(cdp):
        browser = find_browser(args.browser)
        url = args.meet or ("https://meet.google.com/new" if args.new else "https://accounts.google.com/")
        subprocess.Popen(
            [
                browser,
                f"--remote-debugging-port={port}",
                f"--user-data-dir={profile}",
                "--no-first-run",
                "--no-default-browser-check",
                "--use-fake-ui-for-media-stream",
                "--autoplay-policy=no-user-gesture-required",
                "--new-window",
                url,
            ],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        print(f"[bridge] browser window opened ({Path(browser).name}, profile {profile})")
        print("[bridge] pick your Google account in that window (SSO persists for next time)…")
        deadline = time.time() + 60
        while time.time() < deadline and not cdp_alive(cdp):
            time.sleep(0.5)
        if not cdp_alive(cdp):
            raise SystemExit("The launched browser never opened its DevTools port — is another instance using the profile?")
    elif args.meet or args.new:
        # Browser already up: only open a NEW tab if one isn't already
        # sitting on this exact meeting room. Otherwise every restart of
        # just the python process (Chrome left running) clones a duplicate
        # tab, and Meet — seeing the same account twice — offers a
        # "Switch the call here / Join here too" prompt on the new one
        # instead of just reattaching to the real, already-in-call tab.
        target = args.meet or "https://meet.google.com/new"
        existing = find_meet_tab(cdp)
        room = re.compile(r"meet\.google\.com/([a-z0-9-]+)", re.IGNORECASE)
        target_match = room.search(target)
        target_room = target_match.group(1) if target_match else None
        existing_match = room.search(str(existing.get("url") or "")) if existing else None
        existing_room = existing_match.group(1) if existing_match else None
        if not (existing and target_room and target_room == existing_room):
            try:
                requests.put(f"{cdp}/json/new?{target}", timeout=5)
            except Exception:
                try:
                    requests.get(f"{cdp}/json/new?{target}", timeout=5)
                except Exception:
                    pass
    return cdp


def wait_for_meet_tab(cdp: str, timeout: float = 900.0, require_room: bool = False) -> dict[str, Any]:
    """Wait while the operator signs in and joins the call.

    With require_room, keep waiting until the tab has left transitional pages
    (meet.google.com/new, the landing page) and shows a real room URL like
    meet.google.com/xxx-yyyy-zzz.
    """
    room = re.compile(r"meet\.google\.com/[a-z]{3,4}-[a-z]{3,5}-[a-z]{3,4}(\?|$|/)", re.IGNORECASE)
    told = False
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            tab = find_meet_tab(cdp)
        except Exception:
            tab = None
        if tab and (not require_room or room.search(str(tab.get("url") or ""))):
            return tab
        if not told:
            told = True
            print("[bridge] waiting for a meet.google.com tab — sign in and open the meeting in the popped-up window…")
        time.sleep(1.5)
    raise SystemExit("Timed out waiting for a Google Meet tab (15 min).")


# --------------------------------------------------------------------------
# IN: caption scraping
# --------------------------------------------------------------------------
# Meet's own CSS class names churn across releases, so guessing specific
# classes (the old approach) silently breaks and, worse, can silently DROP
# captions when a text-pattern heuristic misfires with no visible error.
# Instead: find the captions region using only its stable semantic
# aria-label/role. Prefer an `[aria-live]` match specifically — that's the
# accessibility signal for a small, transient, live-updating region (the
# actual live-caption ticker), as opposed to Meet's separate, non-live
# scrolling transcript/history panel, which can ALSO match a broad
# aria-label search and (being a full growing history, not a live line)
# will always have far more text — a "pick whichever has the most text"
# heuristic actively prefers the WRONG one. Only fall back to the biggest
# candidate if nothing is marked aria-live at all. Track each caption ROW
# by DOM ELEMENT IDENTITY (a stable key assigned the first time that exact
# node is seen, kept on `window` across polls) rather than by guessing from
# its text content — a row is either a brand new DOM node (new utterance)
# or the SAME node still growing (interim speech), unambiguous and immune
# to class-name churn since it depends only on the region's own generic
# child structure and DOM identity, both stable.
CAPTIONS_JS = r"""
(() => {
  const labelSel = 'div[aria-label*="aption" i], div[role="region"][aria-label*="ubtitle" i], div[role="region"][aria-label*="aption" i]';
  const candidates = [...document.querySelectorAll(labelSel)];
  const liveOnes = candidates.filter((c) => c.hasAttribute("aria-live") || c.closest("[aria-live]"));
  let region = null, bestLen = -1;
  const pool = liveOnes.length ? liveOnes : candidates;
  for (const c of pool) {
    const len = (c.innerText || "").length;
    if (len > bestLen) { region = c; bestLen = len; }
  }
  if (!region) {
    const inCall = !!document.querySelector('button[aria-label*="captions" i], [data-is-muted]');
    return JSON.stringify({ ok: false, note: inCall ? "captions look OFF - press c in the Meet" : "not in a call yet?" });
  }
  window.__meetCaptionRows = window.__meetCaptionRows || new Map();
  const seen = window.__meetCaptionRows;
  let rowEls = [...region.children].filter(el => (el.innerText || "").trim().length > 0);
  // In Meet's "single continuously-growing row" mode the region can hold
  // its text directly (no per-utterance child elements at all) — fall back
  // to treating the region itself as the one row rather than silently
  // dropping everything just because it has no useful children.
  let fallbackNote = null;
  if (!rowEls.length && (region.innerText || "").trim()) {
    rowEls = [region];
    fallbackNote = `no child rows; using region itself (childCount=${region.children.length})`;
  }
  const rows = [];
  const liveKeys = [];
  rowEls.forEach((rowEl) => {
    let info = seen.get(rowEl);
    if (!info) {
      info = { key: `row-${seen.size}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}` };
      seen.set(rowEl, info);
    }
    liveKeys.push(info.key);
    // Best-effort speaker split: if this row has more than one child
    // element, treat the first as the speaker name and the rest as the
    // caption text — a generic structural guess, never a class-name
    // dependency. If it doesn't cleanly apply, fall back to the row's
    // whole text under a generic "Speaker" label rather than dropping it.
    let speaker = "Speaker";
    let text = (rowEl.innerText || "").trim();
    if (rowEl.children.length > 1) {
      const nameText = (rowEl.children[0].innerText || "").trim();
      const restText = [...rowEl.children].slice(1).map((c) => c.innerText || "").join(" ").replace(/\s+/g, " ").trim();
      if (nameText && restText && nameText.length < 60) { speaker = nameText; text = restText; }
    }
    text = text.replace(/\s+/g, " ").trim();
    if (text) rows.push({ key: info.key, speaker, text });
  });
  // Forget rows no longer present at all, so this Map never grows
  // unbounded across a long meeting.
  for (const el of [...seen.keys()]) { if (!rowEls.includes(el)) seen.delete(el); }
  return JSON.stringify({ ok: true, rows, liveKeys, note: fallbackNote });
})()
"""


# Unattended join: on the pre-join screen turn the camera OFF, set the mic,
# and click Join; once in the call, auto-admit knockers, answer Google's
# solo-meeting "Are you still there?" check, and keep captions switched on.
# mic policy: "keep"     — never touch the mic (the host: manual mutes rule)
#             "muted"    — companion at rest: force/keep it muted
#             "speaking" — companion during SAPI playback: ensure unmuted
#                          (its mic is a fake audio device, never the room mic)
def autojoin_js(policy: str) -> str:
    want = {"keep": "null", "muted": "false", "speaking": "true"}[policy]
    return r"""
(() => {
  const WANT_MIC = %s;
  const byLabel = (pattern) =>
    [...document.querySelectorAll('button, [role="button"]')].find(
      (b) => pattern.test(b.getAttribute("aria-label") || ""));
  // Google's solo-meeting "Are you still there?" check: always stay.
  const stay = [...document.querySelectorAll("button")].find((b) =>
    /stay in the call|keep waiting|i'm here|im here/i.test((b.textContent || "") + (b.getAttribute("aria-label") || "")));
  if (stay) { stay.click(); return "stayed-in-call"; }
  if (document.querySelector('button[aria-label*="eave call" i]')) {
    // The toolbar "Admit N guest(s)" notification is itself a <div
    // role="button"> that only OPENS the People panel — it is not the
    // actual admit action, and it sorts before the real button in DOM
    // order, so a prefix match on "admit" keeps re-clicking it forever
    // without ever admitting anyone. The real action is a plain <button>
    // reading exactly "Admit" (per-person, aria-label "Admit <name>") or
    // "Admit all" inside that panel — match those exactly ($-anchored).
    // Google shows an "Admit all? / Douglas Miles / Cancel / Admit all"
    // confirmation dialog when a knocker shares a display name with
    // someone already in the call (true here: both HOST and COMPANION
    // are the same operator's accounts, always named "Douglas Miles").
    // Per the operator's explicit instruction, this room is private and
    // only intended participants ever know its URL, so auto-confirming
    // that ONE specific dialog is authorized — but stay scoped to it:
    // only click a button inside the dialog whose text is itself
    // "Admit"/"Admit all" ($-anchored), never any other dialog Meet might
    // show (e.g. a future "Leave meeting?" prompt), which still gets left
    // untouched for a human to resolve.
    const openDialog = document.querySelector('[role="dialog"], [role="alertdialog"]');
    if (openDialog) {
      const confirmAdmit = [...openDialog.querySelectorAll('button, [role="button"]')].find((b) =>
        /^admit( all)?$/i.test((b.textContent || "").trim()));
      if (confirmAdmit) { confirmAdmit.click(); return "admitted-via-confirmation"; }
    } else {
      const admit = [...document.querySelectorAll('button, [role="button"]')].find((b) =>
        /^admit( all)?$/i.test((b.textContent || "").trim()));
      if (admit) { admit.click(); return "admitted"; }
      const chip = [...document.querySelectorAll('[role="button"]')].find((b) =>
        /^admit \d/i.test((b.textContent || "").trim()));
      if (chip) { chip.click(); return "admit-panel-opened"; }
    }
    if (WANT_MIC === false) {
      const mic = byLabel(/turn off microphone/i);
      if (mic) { mic.click(); return "muted"; }
    } else if (WANT_MIC === true) {
      const mic = byLabel(/turn on microphone/i);
      if (mic) { mic.click(); return "unmuted-for-speech"; }
    }
    const cc = byLabel(/turn on captions/i);
    if (cc) { cc.click(); return "captions-clicked"; }
    if (openDialog) { return "unrecognized-dialog-open"; }
    return "in-call";
  }
  if (WANT_MIC === false) {
    const micOff = byLabel(/turn off microphone/i);
    if (micOff) micOff.click();
  } else if (WANT_MIC === true) {
    const micOn = byLabel(/turn on microphone/i);
    if (micOn) micOn.click();
  }
  // WANT_MIC === null ("keep"): leave the mic exactly as it already is.
  const camOff = byLabel(/turn off camera/i);
  if (camOff) camOff.click();
  const join = [...document.querySelectorAll("button")].find((b) =>
    /join now|ask to join|join anyway|rejoin/i.test((b.textContent || "") + (b.getAttribute("aria-label") || "")));
  if (join && !join.disabled) { join.click(); return "join-clicked"; }
  return "waiting-prejoin";
})()
""" % want


# A sentence boundary: one or more .!? immediately followed by whitespace or
# end-of-string. Deliberately simple (this is ASR captions, not copy-edited
# prose) — matches the same heuristic already used to count "Transcribe"
# lines in the admin UI.
_SENTENCE_END_RE = re.compile(r"[.!?]+(?=\s|$)")


def _first_sentence_boundary(text: str) -> int | None:
    """Index just past the FIRST sentence-ending punctuation in `text`, or
    None if it doesn't contain one yet."""
    m = _SENTENCE_END_RE.search(text)
    return m.end() if m else None


class CaptionTracker:
    """Trap every row-text CHANGE, keyed by DOM element identity, and relay
    it immediately — zero latency, no settle timers on the bridge side at
    all. Google's live captions get revised unpredictably (confirmed live:
    identical audio produced a "first version", then a few seconds later a
    completely different "corrected version" of the same stretch of
    speech) — every attempted "decide what's final on the bridge side"
    heuristic ended up either hiding updates the listener needed to see,
    or replaying huge duplicate blobs. So the bridge still never WAITS
    before relaying a change.

    BUT: Meet frequently keeps the SAME DOM row growing for an entire
    monologue (one speaker, one row, thousands of characters) rather than
    starting a new row per utterance — confirmed live (a single row grew
    past 3000 chars covering many minutes of speech). Relaying that as one
    ever-growing "line" makes the raw emit stream useless as a log of
    distinct speech events. So the moment the growing text crosses a
    completed sentence (`.`/`!`/`?`), that finished sentence is FROZEN
    under the key it was already growing under (it will never be updated
    again — "give the last line the old key") and a brand-new key is
    minted for whatever comes next in the same DOM row — the still-growing
    line keeps extending in FRONT of what's already been dished out, never
    behind it.

    Three explicit per-DOM-row buffers:
      1. `raw`      — an exact mirror of Meet's own row text, untouched.
      2. `pending`  — the still-unsettled tail of `raw` (tracked as an
                       offset, not copied) that hasn't crossed a sentence
                       boundary yet; every CHANGE to it is still relayed
                       immediately (in place, same key) so the consumer
                       sees the line growing in real time, same as before.
      3. `ready`    — completed sentences peeled off of `pending` the
                       instant they cross a boundary, queued here and then
                       dished out to the real consumer (mailbox emit(), one
                       call per sentence) in the SAME poll, in order — a
                       real queue rather than an inline emit so multiple
                       sentences completing between two polls are still
                       dished out as distinct, separately-ordered items.
    """

    def __init__(self, settle: float) -> None:
        self.settle = settle  # kept for CLI/call-site compatibility; unused
        # Buffer 1 — RAW: last-seen full text of each DOM row, unmodified.
        self.raw: dict[str, str] = {}
        # Buffer 2 — PENDING: how much of `raw` has already been settled
        # into `ready`/dished-out sentences (an offset into `raw`, not a
        # copy) + which key is currently receiving updates for what's left.
        self.settled_len: dict[str, int] = {}
        self.active_key: dict[str, str] = {}
        self.clone_seq: dict[str, int] = {}
        # Per DOM row: what key the CURRENT active_key replaces (the key
        # that was just frozen when this active_key was minted) — makes the
        # chain explicit for a consumer (row1 -> row1#1 -> row1#2 is really
        # one continuous utterance stream Meet never split into separate
        # rows itself) instead of leaving it to be inferred from the key
        # naming convention. None for a row's very first/original key.
        self.replaces: dict[str, str | None] = {}
        # Buffer 3 — READY: completed sentences waiting to be dished out,
        # one at a time, to the real consumer. Populated then fully drained
        # within the same update() call (no added latency) but kept as an
        # explicit queue so the dispatch step is its own, separate stage.
        # `final`: True for a completed sentence ("phrase") that will never
        # be updated again once dished out; False for the still-growing
        # live remainder — lets a consumer distinguish settled phrases from
        # in-progress speech without guessing from the text itself.
        # `replaces`: the key this one continues from (None if it's the
        # row's original key).
        self.ready: list[tuple[str, str, str, bool, str | None]] = []  # (key, speaker, text, final, replaces)
        # On the very first poll after a (re)start, whatever's already
        # visible could be minutes of accumulated on-screen history (Meet's
        # captions region keeps a long scroll-back) rather than something
        # newly said — baseline it silently instead of relaying it as a
        # wall of "new" updates every single time the bridge restarts.
        self.baselined = False

    def update(self, rows: list[dict[str, str]], live_keys: list[str], emit) -> None:
        if not self.baselined:
            self.baselined = True
            for row in rows:
                self.raw[row["key"]] = row["text"]
                self.settled_len[row["key"]] = len(row["text"])
            return
        seen_keys = set()
        for row in rows:
            dom_key, speaker, text = row["key"], row["speaker"], row["text"]
            text = text.strip()
            seen_keys.add(dom_key)
            if len(text) < 2 or self.raw.get(dom_key) == text:
                continue
            self.raw[dom_key] = text  # buffer 1: mirror updated first
            settled_len = self.settled_len.get(dom_key, 0)
            active_key = self.active_key.get(dom_key, dom_key)
            replaces = self.replaces.get(dom_key)
            # Consume buffer 2 (the still-unsettled tail): peel off every
            # COMPLETED sentence, queuing each into buffer 3 (`ready`) —
            # the still-growing part always stays IN FRONT of (after) the
            # already-settled offset, never overlapping it.
            while True:
                pending = text[settled_len:]
                boundary = _first_sentence_boundary(pending)
                if boundary is None:
                    break
                sentence = pending[:boundary].strip()
                if sentence:
                    self.ready.append((active_key, speaker, sentence, True, replaces))
                settled_len += boundary
                self.clone_seq[dom_key] = self.clone_seq.get(dom_key, 0) + 1
                replaces = active_key  # the NEXT key continues from this one
                active_key = f"{dom_key}#{self.clone_seq[dom_key]}"
            self.settled_len[dom_key] = settled_len
            self.active_key[dom_key] = active_key
            self.replaces[dom_key] = replaces
            # Whatever hasn't crossed a boundary yet is still relayed live,
            # in place, under the (still-open) active key — the consumer
            # keeps seeing the growing line in real time, it just no longer
            # carries the already-dished-out sentences in front of it.
            live_pending = text[settled_len:].strip()
            if live_pending:
                self.ready.append((active_key, speaker, live_pending, False, replaces))
        # Dispatch buffer 3: dish out every queued item to the real
        # consumer, one at a time, in order, then clear the queue.
        for key, speaker, text, final, replaces in self.ready:
            emit(key, speaker, text, final=final, replaces=replaces)
        self.ready.clear()
        # Forget rows no longer present at all, so these dicts never grow
        # unbounded across a long meeting.
        for dom_key in list(self.raw):
            if dom_key not in seen_keys:
                self.raw.pop(dom_key, None)
                self.settled_len.pop(dom_key, None)
                self.active_key.pop(dom_key, None)
                self.clone_seq.pop(dom_key, None)


# --------------------------------------------------------------------------
# OUT: post mailbox replies into the Meet chat (+ optional TTS)
# --------------------------------------------------------------------------
SEND_CHAT_JS_TEMPLATE = r"""
(() => {
  const TEXT = %s;
  let input = document.querySelector('textarea[aria-label*="essage" i], input[aria-label*="essage" i], textarea[placeholder*="essage" i]');
  if (!input) {
    const opener = document.querySelector('button[aria-label*="chat" i], button[aria-label*="everyone" i]');
    if (opener) { opener.click(); return "opened-chat-retry"; }
    return "no-chat-input";
  }
  const proto = input.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto, "value").set.call(input, TEXT);
  input.dispatchEvent(new Event("input", { bubbles: true }));
  const send = [...document.querySelectorAll("button")].find(b => /send/i.test(b.getAttribute("aria-label") || "") && !b.disabled);
  if (send) { send.click(); return "sent"; }
  input.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true }));
  return "sent-enter";
})()
"""


def speak_windows(text: str) -> None:
    """Best-effort local TTS through Windows SAPI (no extra pip deps)."""
    script = (
        "Add-Type -AssemblyName System.Speech;"
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        "$s.Speak([Console]::In.ReadToEnd())"
    )
    try:
        proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", script],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        proc.communicate(input=text.encode("utf-8"), timeout=120)
    except Exception as error:  # noqa: BLE001 - TTS must never kill the bridge
        print(f"[tts] {error}", file=sys.stderr)


# --------------------------------------------------------------------------
# Synthetic mic: SAPI speech INTO the meeting — no virtual-cable driver.
#
# The companion tab's getUserMedia is patched so the "microphone" Meet sees
# is a WebAudio MediaStreamDestination we control. To talk, the bridge
# synthesizes a WAV with Windows SAPI, ships it into the tab over CDP as
# base64, and plays it into that destination. The REAL room mic is never
# touched by the companion.
# --------------------------------------------------------------------------
GUM_PATCH_JS = r"""
(() => {
  if (window.__sapiPatched) return;
  window.__sapiPatched = true;
  const real = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
  navigator.mediaDevices.getUserMedia = async (constraints) => {
    if (constraints && constraints.audio) {
      if (!window.__sapiCtx) {
        window.__sapiCtx = new AudioContext({ sampleRate: 48000 });
        window.__sapiSink = window.__sapiCtx.createMediaStreamDestination();
        // A silent keep-alive so the track always produces samples.
        const silence = window.__sapiCtx.createGain();
        silence.gain.value = 0.0001;
        const osc = window.__sapiCtx.createOscillator();
        osc.connect(silence).connect(window.__sapiSink);
        osc.start();
      }
      const stream = new MediaStream(window.__sapiSink.stream.getAudioTracks());
      if (constraints.video) {
        try {
          const cam = await real({ video: constraints.video });
          cam.getVideoTracks().forEach((track) => stream.addTrack(track));
        } catch (error) { /* camera denied/absent is fine */ }
      }
      return stream;
    }
    return real(constraints);
  };
})();
"""

SPEAK_INTO_MEETING_JS = r"""
(async () => {
  const B64 = %s;
  if (!window.__sapiCtx || !window.__sapiSink) return "no-synthetic-mic";
  const ctx = window.__sapiCtx;
  if (ctx.state === "suspended") await ctx.resume();
  const bytes = Uint8Array.from(atob(B64), (c) => c.charCodeAt(0));
  const buffer = await ctx.decodeAudioData(bytes.buffer);
  const source = ctx.createBufferSource();
  source.buffer = buffer;
  source.connect(window.__sapiSink);
  source.start();
  return "speaking:" + Math.round(buffer.duration * 1000);
})()
"""


def sapi_wav_base64(text: str) -> tuple[str, float]:
    """Synthesize text to a WAV with Windows SAPI; return (base64, seconds)."""
    import base64
    import tempfile
    import wave

    handle, path = tempfile.mkstemp(suffix=".wav", prefix="meet_say_")
    os.close(handle)
    try:
        script = (
            "Add-Type -AssemblyName System.Speech;"
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            f"$s.SetOutputToWaveFile('{path}');"
            "$s.Speak([Console]::In.ReadToEnd());"
            "$s.Dispose()"
        )
        proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", script],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        proc.communicate(input=text.encode("utf-8"), timeout=120)
        with wave.open(path, "rb") as reader:
            duration = reader.getnframes() / float(reader.getframerate() or 22050)
        data = Path(path).read_bytes()
        return base64.b64encode(data).decode("ascii"), duration
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# --------------------------------------------------------------------------
# Virtual-cable audio routing (configurable alternative to the in-page
# WebAudio synthetic mic above). A "cable" is really a mirrored device pair:
# whatever plays into its PLAYBACK ("Input") endpoint instantly appears as if
# recorded from its RECORDING ("Output") endpoint. So: we play SAPI speech to
# the cable's playback side; Chrome/Meet is pointed at the cable's recording
# side as its microphone. Fully opt-in — with neither flag set, behavior is
# unchanged (the WebAudio patch above keeps working as today).
# --------------------------------------------------------------------------
def list_audio_devices() -> None:
    """Print every Windows audio device sounddevice can see (index, name,
    in/out channel counts) — use this to find a virtual cable's exact name
    once one is installed."""
    import sounddevice as sd

    for index, entry in enumerate(sd.query_devices()):
        kind = []
        if entry.get("max_input_channels", 0) > 0:
            kind.append("in")
        if entry.get("max_output_channels", 0) > 0:
            kind.append("out")
        print(f"[{index:3}] {entry.get('name', '?')!r}  ({'/'.join(kind) or 'none'}, "
              f"in={entry.get('max_input_channels', 0)} out={entry.get('max_output_channels', 0)})")


def resolve_audio_device(name_substring: str, *, want: str) -> int:
    """Resolve a device spec — either a literal device index (e.g. "17") or
    a case-insensitive name substring — to a device index.

    ``want`` is "output" (playback, e.g. a cable's "Input" side we play TTS
    to) or "input" (recording, e.g. a cable's "Output" side — only used for a
    future CLIENT "synthetic ear"). Fails loudly (never guesses) on zero or
    multiple name matches, listing candidates either way. A virtual cable
    commonly registers the SAME name multiple times (once per Windows host
    API: MME/DirectSound/WASAPI/WDM-KS) with different channel counts/sample
    rates — pass the exact index from --list-audio-devices to disambiguate
    when a name substring is not unique enough.
    """
    import sounddevice as sd

    channel_key = "max_output_channels" if want == "output" else "max_input_channels"
    spec = name_substring.strip()
    if spec.isdigit():
        index = int(spec)
        devices = sd.query_devices()
        if not (0 <= index < len(devices)):
            raise ValueError(f"device index {index} out of range (0..{len(devices) - 1})")
        if devices[index].get(channel_key, 0) <= 0:
            raise ValueError(f"device #{index} {devices[index].get('name')!r} has no {want} channels")
        return index
    needle = spec.lower()
    matches = [
        (index, entry) for index, entry in enumerate(sd.query_devices())
        if needle in str(entry.get("name", "")).lower() and entry.get(channel_key, 0) > 0
    ]
    if not matches:
        raise ValueError(
            f"no {want} device matches {name_substring!r} — run --list-audio-devices to see what's available"
        )
    if len(matches) > 1:
        candidates = ", ".join(f"{i}:{e.get('name')!r}" for i, e in matches)
        raise ValueError(
            f"{name_substring!r} matches {len(matches)} {want} devices ({candidates}); "
            "pass the exact index instead (a virtual cable often registers once per host API)"
        )
    return matches[0][0]


def play_wav_bytes_to_device(wav_bytes: bytes, device_index: int) -> float:
    """Play a synthesized WAV out to a specific device (e.g. a cable's
    playback side) instead of decoding it into the in-page WebAudio patch.
    Returns the clip duration in seconds. Blocks until playback finishes.

    Two real bugs were found and fixed here via live testing against an
    actual VB-CABLE device, not just code review:

    1. Resamples to the device's own native rate before playing: MME (and
       some other Windows host APIs) do NOT resample on the fly the way
       WASAPI shared mode does — feeding a mismatched sample rate (e.g.
       SAPI's 22050 Hz WAV output into a 44100 Hz-native cable device)
       silently produces a single click/pop instead of the real audio,
       with no error raised.
    2. Streams in fixed-size chunks via `sd.OutputStream` rather than
       handing the whole clip to `sd.play()` in one call: MME has a hard
       internal single-buffer limit around 65536 samples (~1.4s at
       44100 Hz) — a `sd.play()` call for anything longer than that
       silently plays NOTHING (not even a click), also with no error
       raised. Empirically bisected the exact threshold live (1.3s clips
       played fine, 1.5s+ clips were totally silent) before finding the
       fix; chunked streaming has no such limit regardless of clip length.
    """
    import io
    import wave

    import numpy as np
    import sounddevice as sd

    with wave.open(io.BytesIO(wav_bytes), "rb") as reader:
        frames = reader.readframes(reader.getnframes())
        sample_rate = reader.getframerate()
        sample_width = reader.getsampwidth()
        channels = reader.getnchannels()
    dtype = {1: np.uint8, 2: np.int16, 4: np.int32}.get(sample_width, np.int16)
    raw = np.frombuffer(frames, dtype=dtype)
    if channels > 1:
        raw = raw.reshape(-1, channels)
    duration = len(raw) / float(sample_rate or 1)
    # Normalize to float32 in [-1, 1] regardless of source bit depth.
    max_val = {1: 128.0, 2: 32768.0, 4: 2147483648.0}.get(sample_width, 32768.0)
    offset = 128.0 if sample_width == 1 else 0.0
    samples = ((raw.astype(np.float32) - offset) / max_val).astype(np.float32)

    device_info = sd.query_devices(device_index)
    target_rate = int(device_info.get("default_samplerate") or sample_rate)
    if target_rate != sample_rate:
        from scipy.signal import resample

        new_length = max(1, int(round(len(samples) * target_rate / sample_rate)))
        samples = resample(samples, new_length, axis=0).astype(np.float32)
    if samples.ndim == 1:
        samples = samples.reshape(-1, 1)

    blocksize = 4096
    frame_count = len(samples)
    out_channels = samples.shape[1]
    with sd.OutputStream(samplerate=target_rate, device=device_index, channels=out_channels, dtype="float32", blocksize=blocksize) as stream:
        index = 0
        while index < frame_count:
            chunk = samples[index:index + blocksize]
            if len(chunk) < blocksize:
                pad = np.zeros((blocksize - len(chunk), out_channels), dtype="float32")
                chunk = np.vstack([chunk, pad])
            stream.write(chunk)
            index += blocksize
    return duration


# Selects a device by name in Meet's own in-call Audio Settings mic dropdown
# (so Meet actually captures from a virtual cable's recording side instead of
# real hardware). Best-effort: Meet's device-picker markup is not covered by
# a live test yet (no cable is installed on this machine to verify against);
# only wired in when --mic-select-device is explicitly configured, so it is
# a no-op with zero risk when unset.
SELECT_MIC_DEVICE_JS = r"""
(() => {
  const NEEDLE = %s;
  const opener = [...document.querySelectorAll('button, [role="button"]')].find((b) =>
    /audio settings/i.test(b.getAttribute("aria-label") || ""));
  const micList = document.querySelector('select[aria-label*="microphone" i], [role="menu"][aria-label*="microphone" i]');
  if (!micList) {
    if (opener) { opener.click(); return "opened-audio-settings"; }
    return "no-audio-settings-control";
  }
  const options = [...micList.querySelectorAll('option, [role="menuitemradio"], [role="option"]')];
  const match = options.find((o) => (o.textContent || "").toLowerCase().includes(NEEDLE));
  if (!match) return "no-matching-mic-option";
  if (match.tagName === "OPTION") {
    micList.value = match.value;
    micList.dispatchEvent(new Event("change", { bubbles: true }));
  } else {
    match.click();
  }
  return "mic-selected:" + NEEDLE;
})()
""" 


def message_text(message: dict[str, Any]) -> str:
    for key in ("text", "message", "body", "content"):
        value = message.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cdp", default=os.environ.get("MEET_BRIDGE_CDP", DEFAULT_CDP), help="Chrome DevTools endpoint for attach mode (default %(default)s)")
    parser.add_argument("--meet", default=None, help="Google Meet URL — pops up the bridge's own browser for SSO sign-in and joins there")
    parser.add_argument("--new", action="store_true", help="CREATE a new instant meeting (meet.google.com/new) for the signed-in account, join it, and post its link to the mailbox")
    parser.add_argument("--attach-only", action="store_true", help="Never pop a browser: only attach to an existing meet tab on --cdp")
    parser.add_argument("--companion", action="store_true", help="ALSO keep a second signed-in account (own SSO profile, one-time sign-in) sitting MUTED in the meeting so Google sees 2 participants and won't end/nag the servant meeting. Works without it too: the bridge answers 'still there?' prompts and recreates the meeting when Google ends it.")
    parser.add_argument("--companion-port", type=int, default=None, help="DevTools port for the companion browser (default --port + 1)")
    parser.add_argument("--status-port", type=int, default=48699, help="Local health/status HTTP port for the Processes page (0 disables; default %(default)s)")
    parser.add_argument("--self-name", default="You", help="Name captions attribute to the bridge account's own mic (Meet shows 'You'; default %(default)s)")
    parser.add_argument("--no-autojoin", action="store_true", help="Do not auto-click Join/mic/captions — drive the Meet window manually")
    parser.add_argument("--launch", action="store_true", help="Pop up the bridge browser even without --meet")
    parser.add_argument("--browser", default=None, help="Path to chrome.exe/msedge.exe for the popup (auto-detected)")
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE), help="Persistent profile dir for the popup browser (keeps your SSO login; default %(default)s)")
    parser.add_argument("--port", type=int, default=9223, help="DevTools port for the popup browser (default %(default)s)")
    parser.add_argument("--forget-sso", action="store_true", help="Wipe the popup browser's stored Google login (profile dir) and exit — use when the SSO session expired or to switch accounts")
    parser.add_argument("--list-tabs", action="store_true", help="List CDP tabs and exit")
    parser.add_argument("--to", action="append", default=None, help="Mailbox recipient(s) for captions (default symbolic-workbench-user)")
    parser.add_argument("--sender-prefix", default=DEFAULT_SENDER_PREFIX, help="Caption sender prefix (default %(default)s + speaker)")
    parser.add_argument("--outbox", default=DEFAULT_OUTBOX, help="Mailbox recipient the bridge WATCHES for outgoing lines (default %(default)s)")
    parser.add_argument("--out-cursor", default=DEFAULT_OUT_CURSOR, help="Mailbox cursor name for the outbox (default %(default)s)")
    parser.add_argument("--no-out", action="store_true", help="Disable the mailbox -> Meet chat direction")
    parser.add_argument("--speak", action="store_true", help="Also speak outgoing lines with Windows TTS")
    parser.add_argument("--settle", type=float, default=1.2, help="Seconds a caption must hold still to be finalized (default %(default)s)")
    parser.add_argument("--poll", type=float, default=0.4, help="Caption poll interval seconds (default %(default)s)")
    parser.add_argument("--ignore-speaker", action="append", default=[], help="Speaker name(s) to skip (repeatable)")
    parser.add_argument("--list-audio-devices", action="store_true", help="List Windows audio devices (index, name, in/out channels) and exit — use this to find a virtual cable's exact name")
    parser.add_argument("--tts-output-device", default=os.environ.get("MEET_BRIDGE_TTS_OUTPUT_DEVICE"), help="Name (substring) of a real playback device to route /say speech to, e.g. a virtual cable's 'Input' side — omit to keep using the in-page WebAudio synthetic mic (env MEET_BRIDGE_TTS_OUTPUT_DEVICE)")
    parser.add_argument("--mic-select-device", default=os.environ.get("MEET_BRIDGE_MIC_SELECT_DEVICE"), help="Name (substring) of the device Meet's own Audio Settings mic dropdown should select, e.g. a virtual cable's 'Output' side — omit to leave Meet's mic selection alone (env MEET_BRIDGE_MIC_SELECT_DEVICE)")
    args = parser.parse_args()

    if args.list_audio_devices:
        list_audio_devices()
        return

    tts_output_device_index: int | None = None
    if args.tts_output_device:
        try:
            tts_output_device_index = resolve_audio_device(args.tts_output_device, want="output")
            print(f"[bridge] /say will play through device #{tts_output_device_index} matching {args.tts_output_device!r}")
        except ValueError as error:
            raise SystemExit(f"--tts-output-device: {error}")

    if args.forget_sso:
        import shutil

        profile = Path(args.profile).expanduser()
        if cdp_alive(f"http://127.0.0.1:{args.port}"):
            raise SystemExit("Close the bridge browser window first, then rerun --forget-sso.")
        if profile.exists():
            shutil.rmtree(profile, ignore_errors=True)
            print(f"[bridge] SSO profile wiped: {profile} — the next --meet run asks for the account again")
        else:
            print(f"[bridge] nothing to forget ({profile} does not exist)")
        return

    # SSO popup mode: unless --attach-only, the bridge owns a popup browser
    # (persistent SSO profile). Default with no --meet/--new: reuse a meeting
    # tab if one is open, otherwise CREATE the servant meeting.
    cdp_endpoint = args.cdp
    if not args.attach_only:
        cdp_endpoint = launch_browser(args)

    if args.list_tabs:
        for tab_entry in list_tabs(cdp_endpoint):
            print(f"{tab_entry.get('type'):8} {tab_entry.get('title', '')[:60]!r} {tab_entry.get('url', '')[:90]}")
        return

    client = _mailbox_client()
    recipients = args.to or list(DEFAULT_RECIPIENTS)
    ignore = {name.strip().lower() for name in args.ignore_speaker}

    def open_url(target: str) -> None:
        try:
            requests.put(f"{cdp_endpoint}/json/new?{target}", timeout=5)
        except Exception:
            try:
                requests.get(f"{cdp_endpoint}/json/new?{target}", timeout=5)
            except Exception as error:  # noqa: BLE001
                print(f"[bridge] could not open {target}: {error}", file=sys.stderr)

    created_servant = False
    if args.attach_only:
        tab_info = find_meet_tab(cdp_endpoint)
        if not tab_info:
            raise SystemExit(
                f"No meet.google.com tab found via {cdp_endpoint}.\n"
                "Either rerun without --attach-only (pops up an SSO browser window), or\n"
                "start Chrome with --remote-debugging-port=9222, join the Meet, then rerun."
            )
    else:
        tab_info = find_meet_tab(cdp_endpoint)
        if args.new or not tab_info:
            if tab_info is None and not args.meet:
                open_url("https://meet.google.com/new")
                created_servant = not args.new  # implicit servant meeting
            tab_info = wait_for_meet_tab(cdp_endpoint, require_room=True)
            created_servant = created_servant or args.new
        elif args.meet:
            tab_info = wait_for_meet_tab(cdp_endpoint)

    holder: dict[str, Any] = {"tab": CdpTab(tab_info["webSocketDebuggerUrl"]), "url": str(tab_info.get("url") or "").split("?")[0], "tab_id": tab_info.get("id")}
    meeting_url = str(tab_info.get("url") or "").split("?")[0]
    print(f"[bridge] attached: {tab_info.get('title', '')!r} {meeting_url}")

    def announce(text_line: str, metadata: dict[str, Any] | None = None) -> None:
        for recipient in recipients:
            try:
                client.send(recipient, text_line, sender="meet-bridge", metadata=metadata or {"source": "google-meet-bridge"})
            except Exception as error:  # noqa: BLE001
                print(f"[mailbox] announce failed: {error}", file=sys.stderr)

    if created_servant and "meet.google.com" in meeting_url and "/new" not in meeting_url:
        print(f"[bridge] servant meeting created: {meeting_url}")
        announce(
            f"Servant meeting is up: {meeting_url} — I sit in it alone and transcribe the room mic. "
            "You do NOT need to join; invite me elsewhere with '/join <meet-url>' (or /new).",
            {"source": "google-meet-bridge", "meetingUrl": meeting_url, "servant": True},
        )

    def emit(key: str, speaker: str, text: str, final: bool = False, replaces: str | None = None) -> None:
        if speaker.strip().lower() in ignore:
            return
        if speaker.strip().lower() in ("you", "sie", "tu", "vous"):
            speaker = args.self_name
        sender = args.sender_prefix + (re.sub(r"[^a-z0-9]+", "-", speaker.lower()).strip("-") or "speaker")
        line = f"{speaker}: {text}"
        meeting_url_now = holder.get("url")
        # Full info on every single emit — never make a consumer look
        # anything up elsewhere: which key, whether it's a settled phrase
        # or still-growing speech, what key (if any) it continues from, and
        # which meeting it came from, every time, not just on the first
        # message for a given key.
        full_meta = {
            "source": "google-meet-captions", "speaker": speaker, "key": key,
            "final": final, "replaces": replaces, "meetingUrl": meeting_url_now,
        }
        for recipient in recipients:
            try:
                client.send(recipient, line, sender=sender, metadata=dict(full_meta))
            except Exception as error:  # noqa: BLE001
                print(f"[mailbox] send failed: {error}", file=sys.stderr)
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%S")
        with captions_lock:
            # ADD the first time this row key is seen, EDIT/UPDATE it in
            # place (same position, refreshed `updated_at`) every time
            # after — one evolving entry per utterance, not a growing pile
            # of overlapping near-duplicate lines. The consumer reassembles
            # the transcript by watching each key's latest text. `final`
            # marks a completed sentence ("phrase") that will never be
            # updated again — a key only ever goes live->final once, so
            # writing it plainly here is safe (no key is reused after).
            idx = captions_index.get(key)
            if idx is not None and idx < len(captions_log) and captions_log[idx].get("key") == key:
                row = captions_log[idx]
                row.update({
                    "text": text, "updated_at": time.time(), "iso": now_iso,
                    "final": final, "replaces": replaces, "meetingUrl": meeting_url_now,
                })
            else:
                captions_log.append({
                    "key": key, "at": time.time(), "updated_at": time.time(), "iso": now_iso,
                    "speaker": speaker, "text": text, "meetingUrl": meeting_url_now,
                    "final": final, "replaces": replaces,
                })
                del captions_log[:-200]
                # Rebuild the index after any ring-buffer trim shifts positions
                # (bounded to 200 entries, so this is cheap).
                captions_index.clear()
                for i, row in enumerate(captions_log):
                    captions_index[row["key"]] = i
        status["captionCount"] = len(captions_log)
        status["emitCount"] = int(status.get("emitCount") or 0) + 1
        status["lastCaptionAt"] = now_iso
        print(f"[caption] {line}")

    tracker = CaptionTracker(args.settle)
    stop = threading.Event()

    # ---- STT-subsystem integration: /health + /captions for consumers ------
    # `captionCount` = distinct stored rows (add/edit collapses to one per
    # key); `emitCount` = total raw emit() calls ever made (every add AND
    # every edit counted separately) — the UI shows both: "Emit (N)" for
    # the raw event count, "Transcribe (M)" for the reassembled line count.
    status: dict[str, Any] = {"ok": True, "service": "meet_caption_bridge", "meetingUrl": holder.get("url"), "lastCaptionAt": None, "captionCount": 0, "emitCount": 0, "outbox": args.outbox, "recipients": recipients}
    captions_log: list[dict[str, Any]] = []  # ring buffer for the ws_collab STT driver
    captions_index: dict[str, int] = {}  # row key -> index into captions_log, for in-place ADD/EDIT
    captions_lock = threading.Lock()

    # ---- debug/status ring buffer — "other things" the admin UI can show
    # beside captions: autojoin verdicts, mic-select attempts, dialog
    # handling, /say and /join outcomes. `log()` prints exactly as a plain
    # print(...) would (same console output) and additionally remembers the
    # line here so a UI has something real to show, never fabricated.
    debug_log: list[dict[str, Any]] = []
    debug_lock = threading.Lock()

    def log(text: str, *, err: bool = False) -> None:
        print(text, file=sys.stderr if err else None)
        with debug_lock:
            debug_log.append({"at": time.time(), "iso": time.strftime("%Y-%m-%dT%H:%M:%S"), "text": text})
            del debug_log[:-200]

    def _controlled_clients() -> list[dict[str, Any]]:
        """Every participant the bridge actively drives, and which device
        stands in for their mic/speaker — HOST is real hardware and is
        never automated, so it is deliberately not listed here."""
        clients: list[dict[str, Any]] = []
        if args.companion:
            mic = args.mic_select_device or "(WebAudio synthetic mic patch)"
            if args.mic_select_device and not holder.get("companion_mic_confirmed"):
                mic += " — attempting, not yet confirmed by Meet"
            speak = (f"device #{tts_output_device_index} (virtual cable)" if tts_output_device_index is not None
                     else "(WebAudio synthetic speaker patch)")
            clients.append({
                "role": "companion",
                "state": "in-call" if holder.get("companion_tab") else "not-yet-joined",
                "mic": mic,
                "speak": speak,
            })
        return clients

    def _health_server() -> None:
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        from urllib.parse import parse_qs, urlparse

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                if parsed.path.rstrip("/") == "/captions":
                    since = 0.0
                    try:
                        since = float((parse_qs(parsed.query).get("since") or ["0"])[0])
                    except ValueError:
                        since = 0.0
                    with captions_lock:
                        # Filter by `updated_at`, not `at` (creation time) —
                        # a row can be EDITED in place long after it was
                        # first added (Meet revising it), and a poller
                        # needs to see that edit even though the row's
                        # creation time is older than their `since` cursor.
                        rows = [row for row in captions_log if row["updated_at"] > since]
                        # Every meeting URL this buffer has ever seen a caption
                        # for — lets a "which meeting" dropdown list rooms even
                        # ones the current `since` window doesn't include.
                        meetings = sorted({row.get("meetingUrl") for row in captions_log if row.get("meetingUrl")})
                    body = json.dumps({
                        "captions": rows, "now": time.time(), "meetingUrl": holder.get("url"), "meetings": meetings,
                    }).encode("utf-8")
                else:
                    with debug_lock:
                        debug_rows = list(debug_log[-50:])
                    body = json.dumps({
                        **status, "meetingUrl": holder.get("url"), "clients": _controlled_clients(),
                        "debug": debug_rows,
                    }).encode("utf-8")
                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.send_header("access-control-allow-origin", "*")
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_OPTIONS(self) -> None:  # noqa: N802
                # CORS preflight — needed for every request the admin UI
                # makes, not just POST /command: its shared api() helper
                # always attaches an Authorization header (meant for
                # ws_collab's own API), which turns even a plain GET
                # /health or /captions into a "non-simple" request that the
                # browser preflights first. Must echo "authorization" here
                # or the browser silently blocks the real request afterward
                # ("Failed to fetch", no server-side clue at all).
                self.send_response(204)
                self.send_header("access-control-allow-origin", "*")
                self.send_header("access-control-allow-methods", "GET, POST, OPTIONS")
                self.send_header("access-control-allow-headers", "content-type, authorization")
                self.send_header("content-length", "0")
                self.end_headers()

            def do_POST(self) -> None:  # noqa: N802
                # POST /command {"command": "/join <url>" | "/new" | "/say <text>"}
                # — lets a UI (the ws_collab admin's Google Meet page) drive
                # the bridge directly over HTTP, without going through the
                # mailbox_chat mailbox `out_loop` otherwise depends on.
                parsed = urlparse(self.path)
                if parsed.path.rstrip("/") != "/command":
                    self.send_response(404)
                    self.send_header("access-control-allow-origin", "*")
                    self.send_header("content-length", "0")
                    self.end_headers()
                    return
                try:
                    length = int(self.headers.get("content-length") or 0)
                    raw = self.rfile.read(length) if length else b"{}"
                    payload = json.loads(raw or b"{}")
                    command = str(payload.get("command") or "").strip()
                    verdict = handle_command(command) if command else "empty-command"
                    if verdict is None:
                        verdict = "unrecognized-command"
                    status_code, body_obj = 200, {"ok": True, "verdict": verdict}
                except Exception as error:  # noqa: BLE001
                    status_code, body_obj = 400, {"ok": False, "error": str(error)}
                body = json.dumps(body_obj).encode("utf-8")
                self.send_response(status_code)
                self.send_header("content-type", "application/json")
                self.send_header("access-control-allow-origin", "*")
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_args: Any) -> None:  # silence request spam
                return

        try:
            server = ThreadingHTTPServer(("127.0.0.1", args.status_port), Handler)
        except OSError as error:
            print(f"[status] health port {args.status_port} unavailable: {error}", file=sys.stderr)
            return
        print(f"[status] health endpoint: http://127.0.0.1:{args.status_port}/health")
        server.timeout = 1.0
        while not stop.is_set():
            server.handle_request()
        server.server_close()

    if args.status_port:
        threading.Thread(target=_health_server, daemon=True).start()

    # ---- presence companion: a second SSO keeps the meeting populated ------
    # It can also TALK: /say routes SAPI speech through its synthetic mic.
    speech_lock = threading.Lock()

    def companion_loop() -> None:
        companion_port = args.companion_port or (args.port + 1)
        companion_cdp = f"http://127.0.0.1:{companion_port}"
        companion_profile = Path(args.profile).expanduser()
        companion_profile = companion_profile.with_name(companion_profile.name + "_companion")
        told_sso = False
        told_waiting = False
        companion_tab: CdpTab | None = None
        # Synthetic-mic patch state for the CURRENT tab/JS-realm. A full
        # navigation (reload, location.href=) wipes window.* state, so this
        # must be re-applied any time the realm resets.
        mic_ready = False
        reloaded_for_mic = False
        # Whether Meet's own Audio Settings mic dropdown has been switched to
        # --mic-select-device (only relevant/attempted when that flag is set;
        # reset alongside mic_ready on every fresh tab/navigation).
        mic_selected = False
        # HANDS OFF until the operator has signed in and joined the call
        # themselves once — no navigation, no clicks, nothing that could yank
        # the window away mid-sign-in. Automation begins only after the first
        # in-call sighting.
        operator_joined = False
        while not stop.is_set():
            target = str(holder.get("url") or "")
            if "meet.google.com" not in target:
                stop.wait(3)
                continue
            try:
                if not cdp_alive(companion_cdp):
                    companion_profile.mkdir(parents=True, exist_ok=True)
                    browser = find_browser(args.browser)
                    subprocess.Popen(
                        [
                            browser,
                            f"--remote-debugging-port={companion_port}",
                            f"--user-data-dir={companion_profile}",
                            "--no-first-run", "--no-default-browser-check",
                            "--use-fake-ui-for-media-stream",
                            "--mute-audio",
                            "--new-window", target,
                        ],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    )
                    if not told_sso:
                        told_sso = True
                        print("[companion] second browser opened — sign in with the companion's Google account and JOIN the meeting yourself; I keep my hands off until you're in.")
                    deadline = time.time() + 60
                    while time.time() < deadline and not cdp_alive(companion_cdp) and not stop.is_set():
                        time.sleep(0.5)
                    companion_tab = None
                info = find_meet_tab(companion_cdp)
                if not info:
                    if operator_joined:
                        # The meeting moved after the operator was established:
                        # following it IS wanted automation.
                        try:
                            requests.put(f"{companion_cdp}/json/new?{target}", timeout=5)
                        except Exception:
                            requests.get(f"{companion_cdp}/json/new?{target}", timeout=5)
                        companion_tab = None
                        holder["companion_tab"] = None
                    elif not told_waiting:
                        told_waiting = True
                        print("[companion] waiting for YOU to open/join the meeting in the second window (no automation)…")
                    stop.wait(3)
                    continue
                if companion_tab is None:
                    companion_tab = CdpTab(info["webSocketDebuggerUrl"])
                    holder["companion_tab"] = companion_tab
                    mic_ready = False
                    reloaded_for_mic = False
                    mic_selected = False
                # Install the synthetic-mic patch ASAP so Meet's own
                # getUserMedia calls (prejoin preview, mic toggles) resolve
                # to our WebAudio destination instead of the real hardware.
                # Idempotent in JS (window.__sapiPatched guard).
                if not mic_ready:
                    try:
                        companion_tab.evaluate(GUM_PATCH_JS)
                        mic_ready = True
                    except Exception as error:  # noqa: BLE001
                        print(f"[companion] mic patch failed: {error}", file=sys.stderr)
                # Hands-off applies to SIGN-IN, not to joining: if the tab
                # shows a meet page with a Join/Rejoin button the SSO is
                # proven and the companion may (re)join unattended. Only
                # sign-in/recovery pages (accounts.google.com) are untouchable
                # — anything else on meet.google.com (e.g. the home page
                # after a "leave call") is signed-in-but-idle, safe to steer.
                state = str(companion_tab.evaluate(
                    "document.querySelector('button[aria-label*=\"eave call\" i]') ? 'in-call'"
                    " : location.hostname.includes('accounts.google') ? 'signin'"
                    " : [...document.querySelectorAll('button')].some(b => /join now|ask to join|join anyway|rejoin/i.test((b.textContent||'') + (b.getAttribute('aria-label')||''))) ? 'prejoin-ready'"
                    " : 'elsewhere'"))
                if state == "in-call" and not operator_joined:
                    operator_joined = True
                    log("[companion] you're in — taking over: staying muted, deaf, and present.")
                if state == "signin" and not operator_joined:
                    if not told_waiting:
                        told_waiting = True
                        print("[companion] waiting for YOU to sign in in the second window (no automation on sign-in pages)…")
                    stop.wait(4)
                    continue
                if state == "elsewhere":
                    # Signed in (this is meet.google.com, not a Google
                    # sign-in page) but not looking at our room — e.g. still
                    # on the post-leave-call home screen. Safe to steer there
                    # regardless of operator_joined: no OAuth flow to disturb.
                    companion_tab.evaluate("location.href = %s" % json.dumps(target))
                    mic_ready = False
                    reloaded_for_mic = False
                    mic_selected = False
                    stop.wait(4)
                    continue
                if state == "prejoin-ready" and mic_ready and not reloaded_for_mic:
                    # Meet may have already grabbed a real-mic stream for its
                    # local preview before the patch landed. One reload here
                    # (still pre-join, so nothing live is disrupted) guarantees
                    # the very next getUserMedia call sees the patched version.
                    reloaded_for_mic = True
                    mic_ready = False
                    companion_tab.evaluate("location.reload()")
                    stop.wait(3)
                    continue
                if operator_joined and target.split("?")[0] not in str(info.get("url") or ""):
                    companion_tab.evaluate("location.href = %s" % json.dumps(target))
                    mic_ready = False
                    reloaded_for_mic = False
                    mic_selected = False
                    stop.wait(4)
                    continue
                # If a real virtual cable is configured, point Meet's own mic
                # dropdown at it (once per session) so Meet actually captures
                # from the cable instead of real hardware or the WebAudio
                # patch. Best-effort/untested pending a real cable; a no-op
                # when --mic-select-device is unset.
                if state == "in-call" and args.mic_select_device and not mic_selected:
                    try:
                        mic_verdict = companion_tab.evaluate(SELECT_MIC_DEVICE_JS % json.dumps(args.mic_select_device.lower()))
                        log(f"[companion] mic-select: {mic_verdict}")
                        if isinstance(mic_verdict, str) and mic_verdict.startswith("mic-selected:"):
                            mic_selected = True
                            # Surface for /health's "controlled clients" list —
                            # confirms Meet actually adopted the device, not
                            # just that we attempted it.
                            holder["companion_mic_confirmed"] = True
                    except Exception as error:  # noqa: BLE001
                        log(f"[companion] mic-select failed: {error}", err=True)
                # While say_into_meeting() owns the mic (holder["speaking_until"]
                # in the future), don't fight it with a mute click.
                if time.time() >= float(holder.get("speaking_until") or 0):
                    verdict = companion_tab.evaluate(autojoin_js("muted"))
                    if verdict in ("join-clicked", "stayed-in-call", "muted", "admitted"):
                        log(f"[companion] {verdict}")
                # The companion is deaf as well as mute: silence every media
                # element so its tab never replays the meeting into the room
                # (the live mic would re-capture it as an echo). Always on.
                companion_tab.evaluate('document.querySelectorAll("audio,video").forEach((m) => { m.muted = true; m.volume = 0; })')
            except Exception as error:  # noqa: BLE001
                companion_tab = None
                holder["companion_tab"] = None
                log(f"[companion] {error}", err=True)
                stop.wait(3)
            stop.wait(3)

    if args.companion:
        threading.Thread(target=companion_loop, daemon=True).start()
        print("[companion] armed: a muted second account will sit in the meeting so Google keeps it alive")

    def say_into_meeting(text: str) -> None:
        """/say <text>: SAPI-speak through the companion's synthetic mic.

        Never touches the real host mic — this only works once --companion
        is running, has joined, and its getUserMedia patch has landed (or,
        with --tts-output-device configured, once Meet's mic dropdown is
        pointed at a virtual cable's recording side). Meet won't transmit
        audio while the UI shows muted, so this briefly unmutes (policy
        "speaking" — safe either way: the mic is either a synthetic WebAudio
        track or a virtual cable, never the real hardware) and re-mutes
        afterward. holder["speaking_until"] tells companion_loop's regular
        tick to back off from its own mute-enforcement while this is in
        flight.
        """
        tab = holder.get("companion_tab")
        if not tab:
            print("[say] no companion tab yet — start with --companion and let it join first", file=sys.stderr)
            return
        with speech_lock:
            try:
                b64, duration = sapi_wav_base64(text)
                holder["speaking_until"] = time.time() + duration + 2.0
                unmute_verdict = tab.evaluate(autojoin_js("speaking"))
                time.sleep(0.3)  # let the UI settle before playing
                if tts_output_device_index is not None:
                    # Real virtual-cable path: play straight to the configured
                    # Windows device, bypassing the in-page WebAudio patch —
                    # Meet is already capturing from the cable's other side.
                    import base64 as _base64

                    play_wav_bytes_to_device(_base64.b64decode(b64), tts_output_device_index)
                    verdict = f"spoke-via-device-{tts_output_device_index}"
                    log(f"[say] {unmute_verdict}/{verdict}: {text[:80]}")
                    stop.wait(duration + 0.2)
                else:
                    verdict = tab.evaluate(SPEAK_INTO_MEETING_JS % json.dumps(b64), await_promise=True, timeout=30)
                    log(f"[say] {unmute_verdict}/{verdict}: {text[:80]}")
                    if isinstance(verdict, str) and verdict.startswith("speaking"):
                        stop.wait(duration + 0.2)
            except Exception as error:  # noqa: BLE001
                log(f"[say] failed: {error}", err=True)
            finally:
                holder["speaking_until"] = 0.0
                try:
                    tab.evaluate(autojoin_js("muted"))
                except Exception as error:  # noqa: BLE001
                    log(f"[say] re-mute failed: {error}", err=True)

    def switch_to(target_url: str | None) -> None:
        """Leave for another meeting: /join <url> or /new (fresh servant room)."""
        old_id = holder.get("tab_id")
        open_url(target_url or "https://meet.google.com/new")
        room = re.compile(r"meet\.google\.com/[a-z]{3,4}-[a-z]{3,5}-[a-z]{3,4}(\?|$|/)", re.IGNORECASE)
        deadline = time.time() + 600
        info = None
        while time.time() < deadline and not stop.is_set():
            try:
                candidates = [entry for entry in list_tabs(cdp_endpoint)
                              if entry.get("type") == "page"
                              and "meet.google.com" in str(entry.get("url", ""))
                              and entry.get("id") != old_id]
                info = next((entry for entry in candidates if room.search(str(entry.get("url") or ""))), None)
            except Exception:
                info = None
            if info:
                break
            time.sleep(1.5)
        if not info:
            print("[bridge] switch failed: no new meeting tab appeared", file=sys.stderr)
            return
        old = holder.get("tab")
        holder["tab"] = CdpTab(info["webSocketDebuggerUrl"])
        holder["tab_id"] = info.get("id")
        holder["url"] = str(info.get("url") or "").split("?")[0]
        if old:
            try:
                old.close()
            except Exception:
                pass
        if old_id:
            # Hang up the previous meeting so we are not in two calls at once.
            try:
                requests.get(f"{cdp_endpoint}/json/close/{old_id}", timeout=5)
            except Exception:
                pass
        log(f"[bridge] now bridging: {holder['url']}")
        announce(f"Meet bridge moved — now in: {holder['url']}", {"source": "google-meet-bridge", "meetingUrl": holder["url"]})

    def handle_command(command: str) -> str | None:
        """Recognize /join <url>, /new (+ aliases /meet /servant), and /say
        <text>; return a short verdict string if `command` was one of those
        and has been acted on, or None if it isn't a recognized control
        command (caller should fall back to its own default behavior, e.g.
        posting the text into Meet chat as a normal line). Shared by the
        mailbox-driven out_loop and the bridge's own HTTP /command endpoint
        (used by the ws_collab admin UI) so both paths behave identically.
        """
        lowered = command.lower()
        if lowered.startswith("/join"):
            parts = command.split(None, 1)
            target = parts[1].strip() if len(parts) > 1 else None
            switch_to(target)
            return f"joined:{target}" if target else "new-servant-meeting"
        if lowered in ("/new", "/meet", "/servant"):
            switch_to(None)
            return "new-servant-meeting"
        if lowered.startswith("/say"):
            parts = command.split(None, 1)
            spoken = parts[1].strip() if len(parts) > 1 else ""
            if spoken:
                threading.Thread(target=say_into_meeting, args=(spoken,), daemon=True).start()
                return "speaking"
            return "say-empty"
        return None

    def out_loop() -> None:
        """mailbox -> Meet chat (+ optional TTS), plus /join and /new commands."""
        while not stop.is_set():
            try:
                messages = client.receive(args.outbox, cursor=args.out_cursor, advance=True)
            except Exception as error:  # noqa: BLE001
                print(f"[outbox] receive failed: {error}", file=sys.stderr)
                messages = []
            for message in messages:
                text = message_text(message)
                if not text:
                    continue
                command = text.strip()
                if handle_command(command) is not None:
                    continue
                sender = str(message.get("from") or message.get("sender") or "workbench")
                line = f"[{sender}] {text}"
                try:
                    tab = holder["tab"]
                    verdict = tab.evaluate(SEND_CHAT_JS_TEMPLATE % json.dumps(line))
                    if verdict == "opened-chat-retry":
                        time.sleep(1.0)
                        verdict = tab.evaluate(SEND_CHAT_JS_TEMPLATE % json.dumps(line))
                    print(f"[meet-chat] {verdict}: {line[:80]}")
                except Exception as error:  # noqa: BLE001
                    print(f"[meet-chat] failed: {error}", file=sys.stderr)
                if args.speak:
                    threading.Thread(target=speak_windows, args=(text,), daemon=True).start()
            stop.wait(1.5)

    if not args.no_out:
        threading.Thread(target=out_loop, daemon=True).start()
        tts_note = " + TTS" if args.speak else ""
        print(f"[bridge] OUT armed: mailbox '{args.outbox}' -> Meet chat{tts_note} (commands: /join <url>, /new, /say <text>)")
    print(f"[bridge] IN armed: captions -> mailbox {recipients} (finalize after {args.settle}s)")
    if not args.no_autojoin:
        print("[bridge] unattended: I click Join, keep the mic ON, and turn captions on myself.")

    warned = ""
    autojoin_at = 0.0
    last_autojoin_verdict = ""
    lost_since: float | None = None
    fallback_logged_keys: set[str] = set()
    try:
        while True:
            tab = holder["tab"]
            try:
                raw = tab.evaluate(CAPTIONS_JS)
                payload = json.loads(raw) if isinstance(raw, str) else {"ok": False, "note": "no payload"}
                lost_since = None
            except Exception as error:  # noqa: BLE001
                print(f"[bridge] tab lost ({error}); reattaching?", file=sys.stderr)
                time.sleep(2.0)
                info = find_meet_tab(cdp_endpoint)
                if info:
                    try:
                        tab.close()
                    except Exception:
                        pass
                    holder["tab"] = CdpTab(info["webSocketDebuggerUrl"])
                    lost_since = None
                elif not args.attach_only:
                    lost_since = lost_since or time.time()
                    if time.time() - lost_since > 20:
                        print("[bridge] meeting gone — creating a fresh servant meeting…")
                        lost_since = None
                        switch_to(None)
                continue
            if payload.get("ok"):
                # Log once PER ROW KEY (not every poll — a still-growing row
                # would otherwise spam this every ~0.4s) when the speaker/
                # text split heuristic didn't cleanly apply for that row.
                for r in payload.get("rows") or []:
                    if r.get("speaker") == "Speaker" and r.get("key") not in fallback_logged_keys:
                        fallback_logged_keys.add(r["key"])
                        log(f"[captions] speaker-split fallback used: {r.get('text', '')[:100]!r}")
                tracker.update(payload.get("rows") or [], payload.get("liveKeys") or [], emit)
                note = payload.get("note") or ""
            else:
                note = payload.get("note") or "captions not found"
            if note and note != warned:
                warned = note
                print(f"[bridge] {note}")
            # Unattended servant behavior: join + enable captions ourselves.
            # Always tick (not gated on caption "quiet"/"ok" state) — autojoin_js
            # is idempotent and harmlessly returns "in-call" when there's
            # nothing to do. A prior "only when not-quiet" gate here silently
            # stopped ALL admit/mic-policy/stay-in-call handling forever once
            # the meeting settled into its normal steady state (captions on,
            # quiet) — exactly when a late-arriving "Admit N guest" request
            # still needs to be caught.
            if not args.no_autojoin and time.time() - autojoin_at > 2.5:
                autojoin_at = time.time()
                try:
                    verdict = tab.evaluate(autojoin_js("keep"))
                    if verdict not in ("in-call", "waiting-prejoin") and verdict != last_autojoin_verdict:
                        log(f"[bridge] autojoin: {verdict}")
                    last_autojoin_verdict = verdict
                except Exception as error:  # noqa: BLE001
                    log(f"[bridge] autojoin failed: {error}", err=True)
            time.sleep(args.poll)
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        try:
            holder["tab"].close()
        except Exception:
            pass
        print("[bridge] stopped")


if __name__ == "__main__":
    main()
