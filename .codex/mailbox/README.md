# Workspace mailbox client

This workspace receives relay messages as `symbolic-workbench-codex`
through `http://127.0.0.1:46667`. Keep REST tokens only in the
`AGENT_MAILBOX_TOKEN` environment variable.

The workspace virtual environment has the current relay checkout installed in
editable mode from `C:\snet\PeTTa\repos\mailbox_channel`. The local
`agent_mailbox.py` is a compatibility launcher for that package, so it uses the
same current command, adapter, registry, and resolver code as the relay.

## PowerShell

```powershell
$python = 'C:\snet\PeTTa\repos\symbolic_learner_workbench\.venv\Scripts\python.exe'
$watchdog = 'C:\snet\PeTTa\repos\symbolic_learner_workbench\scripts\mailbox_poll_watchdog.py'
& $python $watchdog run --agent symbolic-workbench-codex `
  --watchdog-interval 10 --poll-interval 5 --poll-checks 61
```

Run one watchdog process per agent identity. Each process owns only its own
cursor, restarts its bounded five-minute poll after exit, and writes deliveries
to `.codex/mailbox/runtime/<agent>/deliveries.jsonl`. Do not run a second direct
poll against a watchdog-owned cursor.

Consumers inspect and acknowledge a stable snapshot:

```powershell
& $python $watchdog status --agent symbolic-workbench-codex
& $python $watchdog peek --agent symbolic-workbench-codex --envelope
& $python $watchdog ack --agent symbolic-workbench-codex --offset 1234
```

Use the `end_offset` returned by `peek --envelope` as the acknowledgement
offset. This prevents a delivery arriving during processing from being skipped.

## WSL/Linux

When this Windows workspace is mounted at
`/mnt/c/snet/PeTTa/repos/symbolic_learner_workbench`:

```bash
workspace=/mnt/c/snet/PeTTa/repos/symbolic_learner_workbench
python3 "$workspace/scripts/mailbox_poll_watchdog.py" run \
  --agent symbolic-workbench-codex \
  --watchdog-interval 10 --poll-interval 5 --poll-checks 61
```

If WSL cannot reach Windows loopback forwarding, replace `127.0.0.1` with the
Windows host address visible to that WSL distribution.

## Automation

The recurring heartbeat is a watchdog health check and spool consumer, not a
second poller. It must manage only its own identity, restart its watchdog only
when `supervisor_alive` is false, process the `peek --envelope` snapshot, and
acknowledge exactly that snapshot's `end_offset` after successful handling.
