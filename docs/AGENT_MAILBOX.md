# Shared agent mailbox

[Back to repository README](../README.md)

The workbench can exchange local agent messages through a minimal append-only
JSONL mailbox. By default it uses the sibling
`mailbox_channel/mailbox/` directory next to this
repository. Set `AGENT_MAILBOX_DIR` to share another directory.

Each line in `messages.jsonl` contains `id`, UTC `timestamp`, `from`, `to`,
`type`, and `text`; callers of the Python API may also add `metadata`. Relay
records may carry top-level `channel_id`, `channel_type`, and `source_id`, plus
optional `thread_id` and `root_id` when an upstream user or service supplied
thread context. The adapter only transports identifiers; it never creates a
thread. Omitting `thread_id` and `root_id` is the supported flat-channel
fallback. Messages
may include `attachments`, an array of `{path, name, mime_type, size, sha256}`
records. Attached files are copied into `attachments/<message-id>/`; receivers
preserve that metadata unchanged.
Recipient-specific byte cursors in `cursors/` make `receive` return each
complete record at most once for that recipient. Keep the mailbox directory on
a local filesystem and use one active consumer per recipient identity.

From the repository root:

```powershell
python scripts/agent_mailbox.py send omegaclaw-core-codex "Please inspect the API"
python scripts/agent_mailbox.py send omegaclaw-min "Status update" --sender symbolic-workbench-codex
python scripts/agent_mailbox.py send channel-relay "UI captures" --attach .\systems.png --attach .\details.json --channel-id CHANNEL
python scripts/agent_mailbox.py send channel-relay "Relayed request" --type channel_send --channel-type mattermost --channel-id CHANNEL --source-id POST
python scripts/agent_mailbox.py send channel-relay "Thread reply" --type channel_send --channel-type mattermost --channel-id CHANNEL --source-id POST --thread-id THREAD --root-id ROOT
python scripts/agent_mailbox.py receive symbolic-workbench-codex
python scripts/agent_mailbox.py poll symbolic-workbench-codex --interval 30 --checks 10 --require-port 5173 --require-port 8000
python scripts/agent_mailbox.py status
```

The stable local agent identity defaults to `symbolic-workbench-codex`. Known
peers are `omegaclaw-core-codex`, `omegaclaw-min`, and `channel-relay`. Each successful `send` prints the
new JSON record. `receive` prints unread addressed records as JSONL and prints
nothing when there are none, which makes it suitable for polling scripts.
`--attach PATH` is repeatable. Each source must be an existing file. Basenames
are sanitized and made unique within the message, MIME type is inferred from
the copied name, and SHA-256 and byte size are calculated from the mailbox copy.

For reliable relays, preserve `from`, `to`, `type`, `timestamp`, and every
provided routing field and attachment record. Reply in the supplied thread only
when `thread_id` or `root_id` exists. Otherwise send to `channel_id` as a flat
channel message. Older records without routing fields remain valid, and
`receive` returns unknown or optional fields unchanged for forward compatibility.

Handoff: point every participating repository at the same
`AGENT_MAILBOX_DIR`, give each consumer a unique stable recipient identity,
and invoke `receive <identity>` periodically. Do not edit or truncate
`messages.jsonl`; archive it only after all consumers have been stopped and
their cursors have been coordinated.

## Canonical channel identity (converted format)

The log has been groomed (`POST /workbench/mailbox/worker` op `groom_channels`) so
that every bridged channel has exactly one id — the workspace slug never
existed:

- **Canonical id**: `mm-<host-dashed>-<platform-key>`, e.g.
  `mm-chat-singularitynet-io-81u5jjbjttng8fejorr11xns9h`. Legacy spellings
  (workspace form `mm-<host>-<workspace>-<key>`, slash form `mm/<host>/<key>`,
  bare `<key>`) are merged into it and preserved as `aliases`.
- **Channel key**: the platform UUID (opaque tail) is stored as `key` on every
  channel record; registry maps are keyed by it.
- **Message keys**: each record belonging to a channel carries
  `entry_key: "entry_<n>"` in arrival order. The next key is always max+1 —
  keys are never reused — so settled entries stay safe to delete once
  compaction lands (deletion itself comes later). New sends are stamped
  automatically. A record relayed/forwarded from another sequence (out of
  convenience, or restoring an entry that went missing) may name its original
  as `copy_of: "mailbox-id/entry_n"`; the send API accepts the field and the
  UI projection surfaces it as `copyOf`.
- **Subscriptions vs cursors**: agent entries on `server_agents_registry` keep a
  `subscriptions` map (`channel -> "subscribed" | "unsubscribed"`; opt-outs are
  sticky against subscribe-missing sweeps) separate from `cursors`, which
  store both the fast byte `offset` and the rewrite-proof
  `entries_consumed`/`entry_next` position. A subscription without a cursor is
  auto-materialized at `entry_0`. Channel entries on `server_channels_registry`
  mirror the `subscribers` list. Run op `sync_subscriptions` to re-project.
- **Typed resolver**: `GET /workbench/mailbox/resolve` returns `users`,
  `workspaces` and `channels` maps (each keyed by its own UUID) plus an
  `aliases` table mapping any name to typed refs, e.g.
  `"test": [{"type": "channel", "key": "<CHANNEL-UUID>"}]`.

Grooming is a worker op: dry-run by default, `{"apply": true}` rewrites
`messages.jsonl` in place after a timestamped backup and re-points every
cursor at the equivalent position in the new file.

Single records are edited the same guarded way: `POST /workbench/mailbox/record`
`{id, record, mode}` (worker op `edit_record`) saves a complete record either
`in-place` (rewrite that line, keep its `id`, timestamped backup + cursor
re-point) or `at-end` (append as the newest record with a fresh `entry_key`
and mark the old line `replaced-by: entry_<n>`). The chat UI's per-bubble ✎
editor and mm-side message edits both go through this call.

Registry entries are stored **flat**: the config blob IS the record's top
level — its `id` is the entity id (versions of one entity share it; the last
one out is the one the system uses) and `kind` names the entry type
(`agent_entry`, `channel_entry`, `relay_entry`, `adapter_type_entry`), with
only mailbox routing fields alongside. Legacy records that nested the blob
under `entry` are still read. Each type has two update kinds: `<kind>` is a
REPLACEMENT and `<kind>_changed_keys` is a MERGE carrying just the keys that
changed (how adapters note login/logout without erasing the declaration) —
`POST /workbench/mailbox/entity` with `merge: true` stores one.

## First-class service agents

- **`mattermost-bridge-agent`** — handles all mattermost driver jobs for every
  configured Mattermost server (inbound fan-out, outbound posts, channel IO).
  The legacy identities `mattermost`, `local-mattermost-server` and
  `mattermost-bridge` merge into it: the groom rewrites history, cursors and
  registry docs, and the API folds stray new traffic at view time. Most
  registry entries are entered by this agent — registry-sourced records carry
  `entered_by: "mattermost-bridge-agent"`.
- **`mailbox-server-agent`** — the local mailbox server itself (owns
  `messages.jsonl`, relays channel traffic, runs local delivery). The legacy
  `local-agent`, `mailbox-server` and `channel-relay` identities merge into it
  the same way.
- **`worker_pool_loader_agent`** — takes work items off `server_worker_queue`
  WITHOUT removing them. Each `worker_task` keeps its `entry_key`; the loader
  layers `worker_task_status` records (`blocked` while declared
  `depends_on: ["entry_4", …]` entries are unsettled, `submitted` when handed
  to the pool) and a final `worker_task_result` over the leftover entry. A
  dependency whose entry no longer exists counts as satisfied, so compaction
  can never wedge the queue.
- **`outbound_delivery_resolver_agent`** — monitors the outbound drop-boxes:
  `server_outbound_relay_agent_to_channel` (agent → platform-channel posts)
  and `server_outbound_relay_agent_to_agent` (agent → agent messages). The
  legacy `outbound_delivery`/`agent_to_channel`/`agent_to_agent` spellings
  fold into them, whole records split by content (endpoint evidence ⇒ the
  channel queue). Senders need not know how delivery works: they drop text
  plus whatever address hints they have (`channel_type`, `endpoint_address`,
  a human channel name like `test`). The resolver owns the know-how —
  resolving names to endpoint addresses and handing each item to the right
  delivery bridge (`mattermost` → `mattermost-bridge-agent`; an email bridge
  would register the same way).
- Service queues carry a `monitors` list naming their designated agent
  (`server_worker_queue` → loader, both outbound queues → resolver).
  Designated, not exclusive: anyone may also subscribe, e.g. a user watching
  a queue for debugging. `sync_subscriptions` auto-subscribes monitors (sticky
  opt-outs still win).
- Blackboard/service channels (`server_identifiers_registry`,
  `server_agents_registry`, `server_channels_registry`, `server_worker_queue`,
  `server_events_log`, `server_grooming_registry`,
  `server_adapters_relays_registry` and the two outbound queues) are never
  agents: their cursors or stored entries do not appear in the agents
  directory.
- **`server_grooming_registry`** — remap knowledge as data: `remap_entry`
  records fold legacy channel/agent spellings into canonical ids at view time
  (latest per id wins; an empty or self canonical retires the remap, seeds
  included), plus cumulative `remap_usage` records counting how often each
  fold fired per preposition-set (`to+channel_id`, `from`, …). Manage via
  `POST /workbench/mailbox/remap`, `GET /workbench/mailbox/remaps`, worker op `set_remap`.
- **`server_adapters_relays_registry`** — the delivery plumbing as data:
  `adapter_type_entry` per adapter type the code ships (capabilities plus its
  implementing `python-class` in the sibling repo and rollout state like
  `enabled`/`notes`), and `relay_entry` per
  presence — puppet bots with their own tokens that say things as our codex
  agents puppet them. Presences carry `relay-chat` rule lists — objects
  `{mailbox, enabled, filter, outputs-to}` (filter `as` = puppeted identity,
  `from` = author agent; outputs-to takes `mm/<server>/<channel>` names or
  `$message.channel` for the item's own channel hint): the mm presences relay
  the `server_outbound_relay_agent_to_channel` drop-box into mattermost, and
  `irc_relay_presence_jllykifsh` on QuakeNet `##logicmoo` carries its
  prospective job as `example-of-relay-chat: ["test", "image", "arc3"]` —
  software configured later will relay those mattermost channels into
  `##logicmoo` prefixed like `snet|test|douglas.miles: hi irc`). A presence
  declaration carries all the config its adapter might use; how presences map
  to sockets (one each, pooled) is the adapter's business, and the adapter
  merges login (and best-effort logout) tracking into the stored relay JSONs
  as `relay_entry_changed_keys` patches.
  `GET /workbench/mailbox/adapters-relays` merges code seeds ∪ the sibling
  `config/relays.json` ∪ stored entries.

## External Mailbox Channel Relay Bridging Proxy

Channel transport is owned by the sibling proxy project, not by Workbench,
OmegaClaw, or the FastAPI process lifecycle. The Workbench API can start, stop,
restart, and inspect it through `/workbench/system/services/channel-relay/{action}`
and `/workbench/system/services`.
It binds loopback port `46667`; `/health` is the machine-local ownership and
health signal used to detect an already-running relay and prevent overlap.

Inbound Mattermost posts are fanned out to the configured transport-neutral
recipients (by default `symbolic-workbench-codex`, `omegaclaw-core-codex`, and
`omegaclaw-min`). To post outbound, drop a record on the
`server_outbound_relay_agent_to_channel` queue (legacy `outbound_delivery`
folds into it) with whatever address hints you have — `channel_type`,
`channel_id`, `endpoint_address`, optional `root_id`/`thread_id` thread
context. The resolver/bridge agents own delivery (the relay's dispatcher
consumes that queue, suppresses duplicates via its ledger, and answers with
`channel_delivery_suppressed`/`channel_delivery_failed` records).
Credentials remain in the proxy project's ignored `.env` as `MM_URL`,
`MM_BOT_TOKEN`, and `MM_CHANNEL_ID`; they are never stored in workspace files.
The complete REST, Codex, OmegaClaw, MeTTaClaw, and workflow integration guide
is maintained by the sibling `C:\snet\PeTTa\repos\mailbox_channel\README.md`
project. This Workbench is only a client and external-service controller.

## Live speech-to-text into the mailbox

[`scripts/stt_mailbox_listener.py`](../scripts/stt_mailbox_listener.py)
listens on one or more real audio input devices, transcribes speech locally
and offline with [Vosk](https://alphacephei.com/vosk/), and posts each
finalized utterance into the shared mailbox with `send()`, so spoken words
appear in the Chat UI exactly like a typed message. It writes directly to the
local mailbox store (via the `mailbox_chat`/`mailbox_channels` client's
`send()`), so no relay/server process needs to be running.

```powershell
python scripts/stt_mailbox_listener.py --list-devices
python scripts/stt_mailbox_listener.py --device 1 --to symbolic-workbench-user
python scripts/stt_mailbox_listener.py --device 1 --device 20 --sender voice-stt-listener --partial
```

- `--device` accepts a device index (from `--list-devices`) or a
  case-insensitive substring of the device name; repeat it to transcribe
  several devices concurrently (each in its own thread with its own
  recognizer).
- `--to` selects the mailbox recipient(s); it defaults to
  `symbolic-workbench-user`, the Chat page's default-displayed channel.
- `--sender` sets the mailbox `from` identity (default `voice-stt-listener`).
- `--model` (or `STT_VOSK_MODEL_DIR`) points at a Vosk model directory;
  it defaults to `~/.cache/ws_collab_models/vosk-model-small-en-us-0.15`
  and exits with download instructions if that directory is missing.
- `--partial` also posts interim (not-yet-finalized) results as
  `stt_partial` messages; only finalized `stt_transcript` messages are sent
  by default.
- Install the extra with `python -m pip install -e ".[stt]"` (adds
  `sounddevice` and `vosk`) if they are not already present.

## Google Meet caption bridge (the better STT subsystem)

[`scripts/meet_caption_bridge.py`](../scripts/meet_caption_bridge.py) is a
second STT subsystem with far better recognition: it uses **Google Meet's own
live captions** instead of local Vosk. It is registered on the Processes page
as the managed service **Google Meet STT Bridge**
(`meet_caption_bridge.managed_service.json`, health on
`http://127.0.0.1:48699/health`, launcher
`workbench/scripts/run_meet_bridge.bat`) and can be started/stopped from
there like any other subsystem.

```powershell
python scripts/meet_caption_bridge.py                 # always-on servant meeting
python scripts/meet_caption_bridge.py --meet <url>    # join a specific meeting
python scripts/meet_caption_bridge.py --companion     # + muted 2nd account
python scripts/meet_caption_bridge.py --forget-sso    # re-pick the account
```

- With no arguments it keeps a **servant meeting** running unattended: it
  pops its own Chrome (dedicated profile — sign in ONCE, the SSO session
  persists until Google expires it), creates an instant meeting, auto-joins
  with the room mic ON and camera OFF, turns captions on, answers Google's
  "are you still there?" prompts, auto-admits knockers, and recreates the
  meeting (posting the fresh link) whenever Google ends it.
- Every finished caption line lands in the mailbox as `meet-<speaker>` →
  `symbolic-workbench-user`, exactly like the Vosk listener's messages.
- The reverse direction: anything sent to the `google-meet` recipient is
  typed into the Meet's in-call chat (`--speak` also voices it with Windows
  TTS, out loud on the local machine). Mailbox commands `/join <url>` and
  `/new` move the bridge to meetings you invite it to, so you and others can
  talk to it there.
- `--companion` keeps a second signed-in account (its own SSO profile,
  port +1) sitting muted AND deaf in the meeting so Google sees 2
  participants; with a single account the stay-in-call answers +
  auto-recreate cover it. The companion never unmutes itself and never
  plays back meeting audio (both would risk an echo loop back into the
  room mic) — it is hands-off during Google sign-in and only takes over
  join/mute maintenance after the operator has personally reached the
  call at least once.
- `/say <text>` makes the companion **speak into the meeting** without a
  virtual-audio-cable driver: its `getUserMedia` is patched (CDP-injected,
  companion tab only) so Meet's "microphone" is really a WebAudio
  `MediaStreamDestination`; the text is synthesized locally with Windows
  SAPI to a WAV, then decoded and played straight into that destination.
  The real room microphone is never touched. Requires `--companion` to be
  running and already joined.

## Codex heartbeat automation

The repository-owned source of truth for the Workbench mailbox heartbeat is
[`config/codex-automations/symbolic-workbench-mailbox-agent.toml`](../config/codex-automations/symbolic-workbench-mailbox-agent.toml).
It intentionally omits machine-local scheduler metadata such as
`target_thread_id`, `created_at`, and `updated_at`.

The installed Codex automation is stored outside Git at
`$CODEX_HOME/automations/symbolic-workbench-mailbox-agent/automation.toml`.
Its durable fields must match the repository definition:

- `id`, `kind`, `name`, `status`, and `rrule` map directly;
- `notification_policy` remains `failed_runs_only`;
- the installed prompt runs the repository `poll` command and preserves its
  non-overlap, early-exit, routing, acknowledgement, and quiet-run rules;
- `target_thread_id` binds the local installation to its Codex task and is not
  copied into the repository definition.

After changing either side, compare these durable fields and update the other
side in the same maintenance task. Use the Codex automation API to install or
update the local copy; do not copy the TOML directly into `$CODEX_HOME` because
the app owns thread binding and scheduler metadata.
