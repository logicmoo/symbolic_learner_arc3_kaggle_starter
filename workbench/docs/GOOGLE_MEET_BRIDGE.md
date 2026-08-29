# Google Meet bridge — Help

The **Google Meet page** (RUNTIME → Google Meet) is the workbench surface for
the Meet STT subsystem: the meeting lives in the middle of the workbench frame
with the menu on the left and this help on the right — status, live captions,
and meeting controls all in one place. (Google blocks embedding the
meet.google.com video UI itself, so the actual video window stays in the
bridge's own popup browser; everything else about the meeting is here.)

## What the bridge is

`scripts/meet_caption_bridge.py` uses **Google Meet's live captions** as a
speech recognizer — far better than the local Vosk listener. It has two jobs:

1. **Servant meeting (always-on STT)** — run with no arguments and it creates
   an instant meeting, joins it unattended (room mic ON, camera OFF, captions
   ON), and transcribes whatever the microphone hears. You never need to join
   this meeting; it is simply the recognizer. The bridge answers Google's
   "are you still there?" prompts, auto-admits knockers, and when Google ends
   the meeting it creates a fresh one and posts the new link.
2. **Invited meetings (talk with it together)** — join any meeting with the
   controls on this page (or send `/join <url>` to the `google-meet` mailbox).
   You and other people talk normally; every finished caption line lands in
   Chat as `meet-<speaker>`, and anything sent to the `google-meet` recipient
   is typed into the Meet's in-call chat for everyone to see (`--speak` also
   voices it locally with Windows TTS).

## The page

- **Bridge card** — online/offline, the current meeting link (opens the popup
  window), caption counters. When offline it shows how to start the service:
  the **Processes** page runs it as the managed service *Google Meet STT
  Bridge* (health on `127.0.0.1:48699/health`), or run
  `python scripts/meet_caption_bridge.py` by hand.
- **MEETINGS** — paste a meeting link and *Join this meeting*, or start a
  *New servant meeting*. Commands are delivered through the real agent
  mailbox; the bridge announces where it went.
- **LIVE CAPTIONS** — the bridge's caption feed streaming in real time
  (the same lines that land in the Chat mailbox).

## Accounts and SSO

The bridge pops its own Chrome with a dedicated profile: pick your Google
account **once** and the SSO session persists until Google expires it
(`--forget-sso` wipes it to re-pick). `--companion` keeps a second signed-in
account (its own profile, one-time sign-in) sitting **muted** in the meeting so
Google always sees two participants; with a single account the stay-in-call
answers and auto-recreate keep things going anyway.

## ws_collab

ws_collab's STT driver system can consume the bridge as an engine: the bridge
exposes timestamped caption history at `127.0.0.1:48699/captions?since=<epoch>`
for correlation, and posts to the same mailbox store ws_collab bridges — so
collab workers see Meet speech exactly like local STT, only better.
