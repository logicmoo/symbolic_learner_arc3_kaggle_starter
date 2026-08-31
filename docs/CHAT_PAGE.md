# Chat page

Talk over the shared append-only mailbox (`messages.jsonl`). Every record has
`from`, `to`, optional `channel_id`, a `type` and `text`; any message can be
inspected as raw JSON with the `{ }` button.

## Per-entry editor (✎)

Every bubble everywhere also has a ✎ button: the bubble grows, tints amber and
becomes an editor holding the record's complete JSON (sized to show it all).
Like the other JSON editors it has a **MeTTa** mode toggle (same
resource codec), **Reload** discards edits, and **Save as..** downloads the
text to disk. Saving posts the complete record to `POST /workbench/mailbox/record`
(also available as worker op `edit_record` — mm-side message edits flow
through the same call):

- **Save in-place** — rewrites that record's log line wholesale (its `id` is
  kept; a timestamped `messages.jsonl.edited-*.bak` backup is written and any
  byte cursors are re-pointed).
- **Save at-end** — appends the edited version as the newest record (fresh
  `id` + `entry_key`) and marks the old line `replaced-by: entry_<n>`; for
  `*_entry` registry records latest-per-id already wins, so the original just
  becomes traceable history.

## Chat and File tabs

The **File** tab renders the canonical SuperControl. With no selected message,
its source is one JSON resource containing every record in the visible stream.
Selecting a chat bubble changes the SuperControl source to that node's complete
raw record; selecting it again returns to the whole-stream JSON.

Chat auto-scroll is explicit. It starts enabled, turns off when the user scrolls
away from the bottom or selects a message node, and resumes only through the
**Auto-scroll** toggle. Selecting a node never gets displaced by newly arriving
messages.

## Pickers (top banner)

- **FROM** — the agent identity written to `from` on sent records (the former
  YOU control).
- **TO** — the agent you address (`to`), and the agent whose cursor and
  subscription the bars below operate on.
- **CHANNEL** — the channel the view centres on. Labels show
  `readable name · id · count`.
- **SEND-TO** — optional routed channel: when set, sends carry it as
  `channel_id`, so the message lands on that channel (addressing an agent with
  a SEND-TO channel auto-subscribes it server-side).

FROM, TO, and optional stream targets can explicitly be **(none/null)**. Sending
is disabled until both FROM and TO identify an agent.

Clicking a picker's label (FROM / TO / CHANNEL / SEND-TO) opens the entity's
stored JSON entry for editing — Save posts it to the `server_agents_registry` /
`server_channels_registry` blackboard.

## Require-match bar (the filter)

The message list looks **everywhere** — the whole log, every mailbox and
channel. Each depressed button ANDs one required match:

| Button | Requires |
| --- | --- |
| `TO` | `record.to` equals the TO picker |
| `FROM` | `record.from` equals the FROM picker |
| `CHANNEL` | the record involves the CHANNEL picker (`from`, `to` or `channel_id`) |
| `SEND-TO` | `record.channel_id` equals the SEND-TO picker |
| `TEXT` | the text expression matches (case-insensitive substring, or `/regex/`) |

Only `CHANNEL` is depressed by default (the classic channel view). Depress
nothing to see the entire log; combine buttons to narrow. The bar queries
`GET /workbench/mailbox/messages?filter=1&…` server-side, so results are not limited
to what the browser has loaded.

## Cursor bar

Shows where the TO agent's cursor sits on the viewed channel (bytes behind).
`⏮ Beginning` / `Now ⏭` reposition it, `✕ Remove` deletes it. Cursors are
read positions only — subscription intent is separate.

## Subscription bar

Edits the TO agent's **explicit** subscription setting on the viewed channel:

- **Subscribed** — declare intent to follow the channel (a missing cursor is
  auto-created at `entry_0` on the next sync).
- **Unsubscribed** — sticky opt-out; subscribe-missing sweeps must honor it.
- **✕ Remove setting** — clear the explicit setting so the default inference
  returns: an agent holding a cursor counts as subscribed.

Backed by `POST /workbench/mailbox/subscription` (worker op `set_subscription`),
which re-runs the subscription sync after each edit.

## Composer and channel config

Enter sends (Shift+Enter for a newline). Messages go `FROM → TO`, routed via
SEND-TO when set. The channel-config editor below edits the
`channel_config` record for the send channel (or viewed channel when SEND-TO
is empty).

## The data model in one breath

Entries belong to the sequence of their `channel_id` (or `to` when unrouted)
and are keyed `entry_0, entry_1, …` — keys are never reused (next is always
max+1). A record relayed from another sequence may declare
`copy_of: "mailbox-id/entry_n"`. Well-known service channels
(`server_identifiers_registry`, `server_agents_registry`,
`server_channels_registry`, `server_worker_queue`, `server_events_log`,
`server_grooming_registry`, `server_adapters_relays_registry` and the two
outbound queues) are never agents; service queues list their designated
`monitors` (e.g. `server_outbound_relay_agent_to_channel` →
`outbound_delivery_resolver_agent`, which resolves address hints and routes
items to delivery bridges like `mattermost-bridge-agent`).

See also: [AGENT_MAILBOX.md](AGENT_MAILBOX.md).
