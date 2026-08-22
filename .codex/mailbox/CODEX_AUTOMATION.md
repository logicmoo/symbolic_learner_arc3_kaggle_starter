# Codex mailbox automation prompt

This file explains everything needed to run a Codex/Copilot agent against the
mailbox â€” for the human setting it up and for the agent that runs each wake.

Two roles are supported: a *facilitator* you talk to that distributes work, and
*subagents* that check in with the facilitator and do the work. The
"Install (one-time bootstrap)" section has a ready-to-paste prompt for each.

## How it works (for the operator)

- You create one recurring Codex automation that fires every **30 seconds** as a
  liveness **heartbeat**.
- The heartbeat does not do the polling itself. It checks whether a bounded
  polling session for this agent identity is already alive. If it is, the
  heartbeat does nothing (so sessions never overlap). If it is not â€” because it
  died or because it exited early after handling a task â€” the heartbeat restarts
  it.
- A restarted session **sits and polls for up to a 5-minute timeout** (checks
  immediately, then every 30 seconds, up to ten checks) and exits early the
  moment addressed mail arrives so the agent can act. After the agent finishes a
  quick task, the next 30-second heartbeat brings polling back within 30 seconds
  â€” no multi-minute blackout.
- Each heartbeat first **refreshes the client to the latest code**: it downloads
  `http://127.0.0.1:46667/agent_mailbox.py` (and `http://127.0.0.1:46667/channel_store.py` beside
  it, which it imports) before starting a new session, so the agent always runs
  current code.

Give the agent a stable, unique, hyphens-only identity (see "Choosing an agent
identity" in `REFERENCE.md`). Put the identity and this automation in the
workspace `AGENTS.md` so it is durable.

## For the agent reading this

The section above is what the user needs to know to set you up. If they seem
unsure, offer to walk them through it â€” you can do the whole thing with them:

1. Help them pick a stable, unique, hyphens-only agent identity.
2. Explain the 30-second heartbeat / restart-on-death / 5-minute bounded-poll
   model in plain language (recovery within 30 seconds after a quick task, no
   overlapping sessions).
3. Refresh the client to the latest code by downloading
   `http://127.0.0.1:46667/agent_mailbox.py` and `http://127.0.0.1:46667/channel_store.py`, and
   inspect them as text before running.
4. Create the recurring automation, paste the prompt below, and provide
   `AGENT_MAILBOX_TOKEN` through the automation environment (never in the prompt
   or a repo file).
5. Run one manual check (`agent_mailbox.py --url http://127.0.0.1:46667 check`) and a
   single bounded poll to confirm connectivity before leaving it unattended.

Only do this if they want the help; otherwise just follow the prompt.

## Install (one-time bootstrap)

Both roles start from the same client install and differ only by identity and
role. Replace the placeholders first; provide any token through
`AGENT_MAILBOX_TOKEN`, never in a prompt.

**Shared install** (in each agent's workspace): create `.codex/mailbox/` and
download `http://127.0.0.1:46667/agent_mailbox.py`, `http://127.0.0.1:46667/channel_store.py`, and
`http://127.0.0.1:46667/CODEX_AUTOMATION.md` into it (keep `agent_mailbox.py` and
`channel_store.py` together; inspect them as text before running). Validate with
`python .codex/mailbox/agent_mailbox.py --url http://127.0.0.1:46667 check` and one bounded
poll, then create the 30-second heartbeat automation (see "Creating the Codex
automation") that polls this agent's own identity.

### Prompt: create a facilitator

Paste into Codex in the facilitator's workspace. The facilitator is the agent you
talk to; it hands work out to subagents and reports results back.

```text
Set up a Mailbox Channel Relay *facilitator* in this workspace.

Mailbox URL: http://127.0.0.1:46667
Facilitator identity: symbolic-workbench-facilitator-codex   (e.g. <project>-facilitator-codex)

1. Do the shared install: download agent_mailbox.py, channel_store.py, and
   CODEX_AUTOMATION.md into .codex/mailbox/, inspect them, and validate with
   `check`. Keep the token in AGENT_MAILBOX_TOKEN only; never in a file.
2. Create the 30-second heartbeat automation that polls --to symbolic-workbench-facilitator-codex
   (see "Creating the Codex automation").
3. Act as facilitator:
   - Accept tasks from me and from any shared channel you watch.
   - Keep a roster of subagents that have checked in (they message you on start).
   - Dispatch each unit of work by sending it to a subagent's identity (or a
     shared channel), stamping a correlation_id.
   - Collect replies by correlation_id and report aggregated progress and
     completion/failure back to me.
Do not commit or push unless I ask.
```

### Prompt: create a subagent

Paste into Codex in each worker's workspace. On start it "meets" the facilitator
so the facilitator knows it is available, then waits for assigned work.

```text
Set up a Mailbox Channel Relay *subagent* in this workspace.

Mailbox URL: http://127.0.0.1:46667
Subagent identity: symbolic-workbench-codex            (e.g. <project>-<role>-codex)
Facilitator identity: symbolic-workbench-facilitator-codex

1. Do the shared install: download agent_mailbox.py, channel_store.py, and
   CODEX_AUTOMATION.md into .codex/mailbox/, inspect them, and validate with
   `check`. Keep the token in AGENT_MAILBOX_TOKEN only; never in a file.
2. Meet your facilitator: announce that you are available, for example
   python .codex/mailbox/agent_mailbox.py --url http://127.0.0.1:46667 send --as symbolic-workbench-codex --to symbolic-workbench-facilitator-codex "subagent symbolic-workbench-codex online and available"
3. Create the 30-second heartbeat automation that polls --to symbolic-workbench-codex
   (see "Creating the Codex automation").
4. Act as subagent:
   - Handle tasks addressed to symbolic-workbench-codex (typically from the facilitator).
   - Do only the authorized work in this workspace.
   - Send progress and completion/failure back to symbolic-workbench-facilitator-codex, echoing the
     correlation_id and routing fields from the request.
Do not commit or push unless asked.
```

Example substitutions â€” same-machine: `Mailbox URL: http://127.0.0.1:46667`;
public relay: `Mailbox URL: https://relay.example.com`. Facilitator example
`symbolic-workbench-facilitator-codex`; subagent example
`symbolic-workbench-resources-codex`.

## The prompt

Copy the prompt below into the recurring Codex automation for the workspace that
should receive mailbox work. Replace every `<PLACEHOLDER>` before enabling it.

Run the Codex automation as a liveness heartbeat every 30 seconds. Each wake
checks whether this identity's polling session is already alive: if it is, do
nothing and never start an overlapping session; if it is not (it died, or exited
early after handling work), restart it. The restarted session sits and polls for
up to a 5-minute timeout â€” it checks immediately, then every 30 seconds for at
most ten checks, and exits early when addressed mail arrives so the agent can
act. This keeps recovery within 30 seconds after a quick task while the bounded
poll does the actual checking and prevents overlapping sessions.

```text
Mailbox identity: symbolic-workbench-codex
Mailbox REST URL: http://127.0.0.1:46667
Mailbox token environment variable: AGENT_MAILBOX_TOKEN
Workspace directory: C:\snet\PeTTa\repos\symbolic_learner_workbench

This wake is a 30-second liveness heartbeat. From the workspace directory, first
inspect running processes and reuse or await any active
`agent_mailbox.py poll --to symbolic-workbench-codex` subprocess. Never start an overlapping
polling session for this identity; only (re)start one when none is alive.

Set AGENT_MAILBOX_URL to http://127.0.0.1:46667. If the relay requires authentication,
read the secret from AGENT_MAILBOX_TOKEN. Never print, log, echo, or place that
token on the command line. Do not put secrets in repository files.

Before starting a new polling session, refresh the client so it runs the latest
code: download http://127.0.0.1:46667/agent_mailbox.py (and http://127.0.0.1:46667/channel_store.py
next to it) and overwrite the local copies. Inspect them as text before running.

Locate `agent_mailbox.py` in the workspace. On Windows PowerShell, prefer the
workspace virtual-environment Python when present, otherwise use `py -3` or
`python`. On WSL/Linux, prefer the workspace virtual environment when present,
otherwise use `python3` or `python`.

When no prior polling session is running, execute the platform-equivalent of:

python agent_mailbox.py poll --to symbolic-workbench-codex --interval 30 --checks 10 --require-port 46667

The poll checks immediately and then every 30 seconds for ten checks maximum
(up to a 5-minute timeout). It exits early when addressed mail arrives; the next
30-second heartbeat restarts it. Exit status 2 with a `monitored_process_failure`
object means a required connector disappeared. Empty successful output is a
healthy no-op.

Ignore outbound echoes, empty messages, system events, messages not addressed
to symbolic-workbench-codex, and already-handled message IDs. For genuine new requests:

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

Replace `symbolic-workbench-codex` with a stable identity such as `my-project-codex`, use
`http://127.0.0.1:46667` for `http://127.0.0.1:46667`, and replace
`--require-port 46667` with zero or more repeatable checks, for example:

```text
--require-port 46667 --require-port 5173 --require-port 8000
```

For a remote relay, use its HTTPS public origin instead:

```text
https://relay.example.com
```

## Agent identity and commands

Choose the agent identity and drive the relay using the commands described in
`REFERENCE.md` (sections "Choosing an agent identity" and "mailbox-client
commands for agents"), which the relay serves at `/REFERENCE.md`.

## PowerShell preparation

Download the client into the workspace (grab `channel_store.py` too â€” the client
imports it):

```powershell
Invoke-WebRequest http://127.0.0.1:46667/agent_mailbox.py -OutFile agent_mailbox.py
Invoke-WebRequest http://127.0.0.1:46667/channel_store.py -OutFile channel_store.py
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
python agent_mailbox.py poll --to my-agent --interval 30 --checks 10 `
  --require-port 46667
```

## WSL/Linux preparation

```bash
curl -fsSLo agent_mailbox.py http://127.0.0.1:46667/agent_mailbox.py
curl -fsSLo channel_store.py http://127.0.0.1:46667/channel_store.py

export AGENT_MAILBOX_URL='http://127.0.0.1:46667'
export AGENT_MAILBOX_TOKEN='<secret-if-required>'
python3 agent_mailbox.py check
```

Manual polling test:

```bash
python3 agent_mailbox.py poll --to my-agent \
  --interval 30 --checks 10 --require-port 46667
```

Modern WSL commonly reaches a Windows-hosted loopback service directly. If it
does not, use the Windows host address or the relay's LAN/public HTTPS name.

## Direct local-store alternative

For processes on the same native filesystem, replace the REST environment with
a direct directory. `AGENT_MAILBOX_DIR` takes precedence over
`AGENT_MAILBOX_URL`:

PowerShell:

```powershell
$env:AGENT_MAILBOX_DIR = 'C:\mailboxes\team-a'
Remove-Item Env:AGENT_MAILBOX_URL -ErrorAction SilentlyContinue
python agent_mailbox.py check
```

WSL/Linux with a mailbox stored in the Linux filesystem:

```bash
export AGENT_MAILBOX_DIR="$HOME/mailboxes/team-a"
unset AGENT_MAILBOX_URL
python3 agent_mailbox.py check
```

Do not use direct file access through `/mnt/c` to share a Windows relay mailbox with
WSL. Use the relay's REST URL across the Windows/WSL boundary instead.

Do not let two consumers share the same recipient and cursor unless they are
intentionally sharing work. Use stable unique identities or `--cursor` names
for independent consumers.

## Creating the Codex automation

1. Open the intended workspace in Codex Desktop.
2. Create a recurring automation for that workspace.
3. Choose a 30-second interval (a liveness heartbeat). The bounded poll it
   (re)starts runs up to a 5-minute timeout and the heartbeat only restarts it
   when no session is alive, so heartbeats never overlap pollers.
4. Paste the customized prompt from this file.
5. Provide `AGENT_MAILBOX_TOKEN` through the automation environment when the
   server requires it; do not paste the token into the prompt.
6. Run the automation once manually and confirm `agent_mailbox.py check`
   succeeds before leaving it unattended.

Copying this file and `agent_mailbox.py` into a workspace prepares everything
the automation needs, but does not itself create or enable a Codex recurring
task. Each Codex installation/user must create that task once.
