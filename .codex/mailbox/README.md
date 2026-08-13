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
$client = 'C:\snet\PeTTa\repos\symbolic_learner_workbench\.codex\mailbox\agent_mailbox.py'
& $python $client --url http://127.0.0.1:46667 check
& $python $client --url http://127.0.0.1:46667 poll symbolic-workbench-codex --interval 30 --checks 10 --require-port 46667
```

## WSL/Linux

When this Windows workspace is mounted at
`/mnt/c/snet/PeTTa/repos/symbolic_learner_workbench`:

```bash
workspace=/mnt/c/snet/PeTTa/repos/symbolic_learner_workbench
python3 "$workspace/.codex/mailbox/agent_mailbox.py" \
  --url http://127.0.0.1:46667 check
python3 "$workspace/.codex/mailbox/agent_mailbox.py" \
  --url http://127.0.0.1:46667 poll symbolic-workbench-codex \
  --interval 30 --checks 10 --require-port 46667
```

If WSL cannot reach Windows loopback forwarding, replace `127.0.0.1` with the
Windows host address visible to that WSL distribution.

## Automation

Use the customized `AUTOMATION_PROMPT.md` in this directory as the recurring
Codex task prompt. Each run is bounded and must not overlap another poller using
the same identity.
