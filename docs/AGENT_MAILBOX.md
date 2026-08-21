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

The log has been groomed (`POST /api/mailbox/worker` op `groom_channels`) so
that every bridged channel has exactly one id — the workspace slug never
existed:

- **Canonical id**: `mm-<host-dashed>-<platform-key>`, e.g.
  `mm-chat-singularitynet-io-81u5jjbjttng8fejorr11xns9h`. Legacy spellings
  (workspace form `mm-<host>-<workspace>-<key>`, slash form `mm/<host>/<key>`,
  bare `<key>`) are merged into it and preserved as `aliases`.
- **Channel key**: the platform UUID (opaque tail) is stored as `key` on every
  channel record; registry maps are keyed by it.
- **Message keys**: each record belonging to a channel carries
  `entry_key: "entry_<n>"` in arrival order. A channel's entry count is always
  the next key; new sends are stamped automatically.
- **Subscriptions vs cursors**: agent entries on `server_agents` keep a
  `subscriptions` map (`channel -> "subscribed" | "unsubscribed"`; opt-outs are
  sticky against subscribe-missing sweeps) separate from `cursors`, which
  store both the fast byte `offset` and the rewrite-proof
  `entries_consumed`/`entry_next` position. A subscription without a cursor is
  auto-materialized at `entry_0`. Channel entries on `server_channels` mirror
  the `subscribers` list. Run op `sync_subscriptions` to re-project.
- **Typed resolver**: `GET /api/mailbox/resolve` returns `users`,
  `workspaces` and `channels` maps (each keyed by its own UUID) plus an
  `aliases` table mapping any name to typed refs, e.g.
  `"test": [{"type": "channel", "key": "<CHANNEL-UUID>"}]`.

Grooming is a worker op: dry-run by default, `{"apply": true}` rewrites
`messages.jsonl` in place after a timestamped backup and re-points every
cursor at the equivalent position in the new file.

## External Mailbox Channel Relay Bridging Proxy

Channel transport is owned by the sibling proxy project, not by Workbench,
OmegaClaw, or the FastAPI process lifecycle. The Workbench API can start, stop,
restart, and inspect it through `/api/system/services/channel-relay/{action}`
and `/api/system/services`.
It binds loopback port `46667`; `/health` is the machine-local ownership and
health signal used to detect an already-running relay and prevent overlap.

Inbound Mattermost posts are fanned out to the configured transport-neutral
recipients (by default `symbolic-workbench-codex`, `omegaclaw-core-codex`, and
`omegaclaw-min`). To post outbound, send a record to
`channel-relay` with `channel_type`, `channel_id`, and optional
`root_id`/`thread_id` routing
context. Credentials remain in the proxy project's ignored `.env` as `MM_URL`,
`MM_BOT_TOKEN`, and `MM_CHANNEL_ID`; they are never stored in workspace files.
The complete REST, Codex, OmegaClaw, MeTTaClaw, and workflow integration guide
is maintained by the sibling `C:\snet\PeTTa\repos\mailbox_channel\README.md`
project. This Workbench is only a client and external-service controller.

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
