# Shared agent mailbox

The workbench can exchange local agent messages through a minimal append-only
JSONL mailbox. By default it uses the sibling `agent-mailbox/` directory next
to this repository. Set `AGENT_MAILBOX_DIR` to share another directory.

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
python scripts/agent_mailbox.py send omegaclaw-core-codex "UI captures" --attach .\systems.png --attach .\details.json
python scripts/agent_mailbox.py send omegaclaw-core-codex "Relayed request" --type mattermost_message --channel-type mattermost --channel-id CHANNEL --source-id POST
python scripts/agent_mailbox.py send omegaclaw-core-codex "Thread reply" --channel-type mattermost --channel-id CHANNEL --source-id POST --thread-id THREAD --root-id ROOT
python scripts/agent_mailbox.py receive symbolic-workbench-codex
python scripts/agent_mailbox.py status
```

The local identity defaults to `symbolic-workbench-codex`. Known peers are
`omegaclaw-core-codex` and `omegaclaw-min`. Each successful `send` prints the
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
