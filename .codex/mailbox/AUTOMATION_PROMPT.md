# Codex mailbox automation prompt

Copy the prompt below into a recurring Codex automation for the workspace that
should receive mailbox work. Replace every `<PLACEHOLDER>` before enabling it.

Schedule the Codex automation approximately every five minutes. Each wake runs
one bounded polling session that checks immediately and then every 30 seconds,
for at most ten checks. Do **not** schedule a new Codex task every 30 seconds;
the bounded client command performs those checks and prevents overlapping
polling sessions.

```text
Mailbox identity: symbolic-learner-workbench-codex
Mailbox REST URL: http://127.0.0.1:46667
Mailbox token environment variable: AGENT_MAILBOX_TOKEN
Workspace directory: C:\snet\PeTTa\repos\symbolic_learner_workbench

From the workspace directory, first inspect running processes and reuse or
await any active `agent_mailbox.py poll symbolic-learner-workbench-codex` subprocess. Never start an
overlapping polling session for this identity.

Set AGENT_MAILBOX_URL to http://127.0.0.1:46667. If the relay requires authentication,
read the secret from AGENT_MAILBOX_TOKEN. Never print, log, echo, or place that
token on the command line. Do not put secrets in repository files.

Locate `agent_mailbox.py` in the workspace. On Windows PowerShell, prefer the
workspace virtual-environment Python when present, otherwise use `py -3` or
`python`. On WSL/Linux, prefer the workspace virtual environment when present,
otherwise use `python3` or `python`.

When no prior polling session is running, execute the platform-equivalent of:

python agent_mailbox.py poll symbolic-learner-workbench-codex --interval 30 --checks 10 --require-port 46667

The poll checks immediately and then every 30 seconds for ten checks maximum.
It exits early when addressed mail arrives. Exit status 2 with a
`monitored_process_failure` object means a required listener disappeared.
Empty successful output is a healthy no-op.

Ignore outbound echoes, empty messages, system events, messages not addressed
to symbolic-learner-workbench-codex, and already-handled message IDs. For genuine new requests:

1. Immediately acknowledge the source through the mailbox.
2. Perform only work authorized by the message and this workspace's AGENTS.md.
3. Send concise progress and completion or failure messages through the
   mailbox, preserving correlation, origin, channel, thread, and run metadata.
4. Do not commit, push, publish, or contact additional external systems unless
   the request authorizes it.

Keep required workspace services and the Mailbox Channel Relay Bridging Proxy
running. Remain quiet for healthy polling sessions. Surface only genuine work,
relay failures, authentication failures, or required-service failures.
```

## Example: REST relay on the same machine

This workspace uses the stable identity `symbolic-learner-workbench-codex`, the
local relay at `http://127.0.0.1:46667`, and a required-port check for 46667.

```text
--require-port 46667 --require-port 5173 --require-port 8000
```

For a remote relay, use its HTTPS public origin instead:

```text
https://relay.example.com
```

## PowerShell preparation

Download the client into the workspace:

```powershell
Invoke-WebRequest `
  http://127.0.0.1:46667/agent_mailbox.py `
  -OutFile agent_mailbox.py
```

Set per-user or per-session connection details. Prefer a secret manager or the
Codex automation environment for production tokens:

```powershell
$env:AGENT_MAILBOX_URL = 'http://127.0.0.1:46667'
$env:AGENT_MAILBOX_TOKEN = '<secret-if-required>'
python agent_mailbox.py check
```

Manual polling test:

```powershell
python agent_mailbox.py poll my-agent --interval 30 --checks 10 `
  --require-port 46667
```

## WSL/Linux preparation

```bash
curl -fsSLo agent_mailbox.py \
  http://127.0.0.1:46667/agent_mailbox.py

export AGENT_MAILBOX_URL='http://127.0.0.1:46667'
export AGENT_MAILBOX_TOKEN='<secret-if-required>'
python3 agent_mailbox.py check
```

Manual polling test:

```bash
python3 agent_mailbox.py poll my-agent \
  --interval 30 --checks 10 --require-port 46667
```

Modern WSL commonly reaches a Windows-hosted loopback service directly. If it
does not, use the Windows host address or the relay's LAN/public HTTPS name.

## Direct JSONL alternative

For machines sharing a filesystem, replace the REST environment with a direct
directory. `AGENT_MAILBOX_DIR` takes precedence over `AGENT_MAILBOX_URL`:

PowerShell:

```powershell
$env:AGENT_MAILBOX_DIR = 'C:\mailboxes\team-a'
Remove-Item Env:AGENT_MAILBOX_URL -ErrorAction SilentlyContinue
python agent_mailbox.py check
```

WSL/Linux:

```bash
export AGENT_MAILBOX_DIR='/mnt/c/mailboxes/team-a'
unset AGENT_MAILBOX_URL
python3 agent_mailbox.py check
```

Do not let two consumers share the same recipient and cursor unless they are
intentionally sharing work. Use stable unique identities or `--cursor` names
for independent consumers.

## Creating the Codex automation

1. Open the intended workspace in Codex Desktop.
2. Create a recurring automation for that workspace.
3. Choose an interval near five minutes.
4. Paste the customized prompt from this file.
5. Provide `AGENT_MAILBOX_TOKEN` through the automation environment when the
   server requires it; do not paste the token into the prompt.
6. Run the automation once manually and confirm `agent_mailbox.py check`
   succeeds before leaving it unattended.

Copying this file and `agent_mailbox.py` into a workspace prepares everything
the automation needs, but does not itself create or enable a Codex recurring
task. Each Codex installation/user must create that task once.
