# Copilot automation prompt (llm_emul worker)

[← Back to top-level README](../../README.md)

This file explains everything needed to run a Copilot agent as an
`llm_emul` **worker** -- for the human setting it up and for the agent
that runs each wake. An `llm_emul` worker connects to the relay, waits a
short while for a relayed request, answers it as the model, then rests --
so an idle agent isn't tied up. See `design/LLM_EMUL_RELAY.md` for the
full server design and `LLM_EMUL_ONBOARDING.md` for the hands-on worker
walkthrough (both are also served live under `/llm_emul/docs/...`).

Every worker connects under its own **worker_id** (e.g. `yourself`,
`alice`, `bob`). A request for model `"<worker_id>/<persona>"` is routed
to whoever is currently connected under that worker_id, so several
agents can be online at once, each independently addressable. There is no
facilitator/subagent split -- the relay itself does the routing by
worker_id.

## How it works (for the operator)

- You create one recurring Copilot automation that fires every **30 seconds**
  as a liveness **heartbeat**.
- The heartbeat does not talk to the relay itself. It checks whether a
  worker loop for this worker_id is already alive. If it is, the heartbeat
  does nothing (so you never run two loops for the same worker_id). If it
  is not -- because it died -- the heartbeat restarts it.
- A restarted worker loop runs `scripts/llm_emul_worker.py`, which
  **connects and waits up to ~10 seconds** for a relayed request, answers
  it if one arrives (then immediately loops for the next), or disconnects
  and rests a **randomized** interval (up to ~30 seconds) before
  reconnecting. That rest is a randomized max, not a fixed cadence, and
  each connect/idle/rest cycle is independent of any wall clock -- do not
  "fix" it into a synchronized heartbeat.
- No client download is required: the worker script already lives in the
  repo at `scripts/llm_emul_worker.py`. (If you're running against a
  remote/standalone relay, copy that one script to the machine that will
  host the worker.)

Give the agent a stable, unique, hyphens-only worker_id. Put the
worker_id and this automation in the workspace `AGENTS.md` so it is
durable.

## For the agent reading this

The section above is what the user needs to know to set you up. If they
seem unsure, offer to walk them through it -- you can do the whole thing
with them:

1. Help them pick a stable, unique, hyphens-only worker_id.
2. Explain the 30-second heartbeat / restart-on-death model, and that the
   worker loop itself does connect/wait(~10s)/rest(~<=30s) with randomized
   rests (no overlapping loops per worker_id).
3. Confirm connectivity: `curl http://127.0.0.1:8000/v1/models` should
   list the personas, and one `--once` worker run should connect cleanly.
4. Create the recurring automation, paste the prompt below, and (only if
   the deployment requires a token) provide `LLM_EMUL_TOKEN` through the
   automation environment -- never in the prompt or a repo file.
5. Run one manual `--once` cycle to confirm the round trip before leaving
   it unattended.

Only do this if they want the help; otherwise just follow the prompt.

## Install (one-time bootstrap)

The worker client is `scripts/llm_emul_worker.py`, already present in this
repo -- no download step. In each worker's workspace:

1. Confirm the relay is reachable:
   `curl http://127.0.0.1:8000/v1/models` (or your standalone port).
2. Pick a worker_id and do one bounded test run:
   `python scripts/llm_emul_worker.py --worker-id <worker-id> --once`
3. Create the 30-second heartbeat automation (see "Creating the Copilot
   automation") that keeps a worker loop alive for that worker_id.

A token is **not required** by the current relay -- workers can connect
and answer requests without one. If a deployment chooses to require one,
mint it at `http://127.0.0.1:8000/llm_emul/tokens/new` and supply it
through `LLM_EMUL_TOKEN` in the automation environment, never in a file.

### Prompt: create a worker

Paste into Copilot in the worker's workspace. On start it connects under its
worker_id and begins serving relayed requests.

```text
Set up an llm_emul *worker* in this workspace.

Relay base URL: http://127.0.0.1:8000
Worker identity (worker_id): symbolic-workbench-worker   (e.g. <project>-worker)

1. Confirm the relay is reachable: `curl http://127.0.0.1:8000/v1/models`
   should list personas. Keep any token in LLM_EMUL_TOKEN only, never in a file.
2. Do one bounded test run:
   python scripts/llm_emul_worker.py --worker-id symbolic-workbench-worker --once
3. Create the 30-second heartbeat automation that keeps a worker loop alive
   for symbolic-workbench-worker (see "Creating the Copilot automation").
4. Act as a worker:
   - When a request is relayed to you, read its model/persona line and its
     prompt, then write your answer to the reply file so it is sent back.
   - Honor the persona suffix (yourself/same, yourself/percentNN): shift
     apparent thoroughness/capability, never safety or honesty.
   - Only declare a "pretend" capability (--capabilities images,embeddings,
     moderations,audio_transcription,audio_speech) if you're willing to be
     asked for it regularly.
Do not commit or push unless I ask.
```

Run several workers by repeating this with different `--worker-id` values;
each is routed to independently by its model prefix.

## The prompt

Copy the prompt below into the recurring Copilot automation for the
workspace that should host the worker. Replace every `<PLACEHOLDER>`
before enabling it.

Run the Copilot automation as a liveness heartbeat every 30 seconds. Each
wake checks whether this worker_id's loop is already alive: if it is, do
nothing and never start a second loop for the same worker_id; if it is not
(it died), restart it. The worker loop connects, waits up to ~10 seconds
for a relayed request, answers it and loops, or rests a randomized
interval (up to ~30 seconds) and reconnects.

```text
Worker identity (worker_id): symbolic-workbench-worker
Relay base URL: http://127.0.0.1:8000
Token environment variable (optional): LLM_EMUL_TOKEN
Workspace directory: C:\snet\PeTTa\repos\symbolic_learner_workbench

This wake is a 30-second liveness heartbeat. From the workspace directory,
first inspect running processes and reuse any active
`llm_emul_worker.py --worker-id symbolic-workbench-worker` loop. Never start a second
loop for this worker_id; only (re)start one when none is alive.

If the relay requires authentication, read the secret from LLM_EMUL_TOKEN.
Never print, log, echo, or place that token on the command line. Do not
put secrets in repository files. (The current relay does not require a
token.)

Locate `scripts/llm_emul_worker.py` in the workspace. On Windows
PowerShell, prefer the workspace virtual-environment Python when present,
otherwise use `py -3` or `python`. On WSL/Linux, prefer the workspace
virtual environment when present, otherwise use `python3` or `python`.

When no prior worker loop is running, execute the platform-equivalent of:

python scripts/llm_emul_worker.py --worker-id symbolic-workbench-worker

The loop connects to ws://127.0.0.1:8000/llm_emul/symbolic-workbench-worker/ws,
waits up to ~10 seconds per connection for a relayed request, answers it
(writing the reply so it is sent back), then loops; if idle it disconnects
and rests a randomized interval (up to ~30 seconds) before reconnecting.
Empty idle cycles are a healthy no-op.

For each relayed request:

1. Read the model/persona line and the prompt.
2. Compose an answer at the requested capability level; honor the persona
   but keep judgment, safety, and honesty intact.
3. Only answer non-text "pretend" surfaces (embeddings/moderations/images/
   audio) if this worker declared that capability at connect time.
4. Do not commit, push, publish, or contact additional external systems
   unless the request authorizes it.

Keep required workspace services and the relay running. Remain quiet for
healthy idle cycles. Surface only genuine work, relay failures, or
authentication failures.
```

## Example: relay on the same machine

Use `http://127.0.0.1:8000` for the base URL (or your standalone port from
`workbench/scripts/run_llm_emul_standalone.py`). The worker's WebSocket
URL is derived automatically as
`ws://127.0.0.1:8000/llm_emul/<worker-id>/ws`; override the whole URL with
`--ws-url` if needed, or the host with `--host-ws-url`.

For a remote relay, point at its HTTPS public origin instead:

```text
python scripts/llm_emul_worker.py --worker-id my-worker --host-ws-url wss://relay.example.com
```

## Worker identity and commands

Choose a stable, unique, hyphens-only worker_id. Drive and inspect the
relay with:

- `curl http://127.0.0.1:8000/v1/models` -- personas across all connected workers
- `curl http://127.0.0.1:8000/llm_emul/caps/<worker-id>` -- is this worker
  connected, its models, its declared capabilities
- `curl http://127.0.0.1:8000/admin/llm_emul/state` -- full picture: every
  connected worker_id, usage counts, pending requests

See `LLM_EMUL_ONBOARDING.md` for the request/reply mechanics and
`design/LLM_EMUL_RELAY.md` for the complete route map.

## PowerShell preparation

The worker client is already in the repo, so there's no download. Optional
connection details (prefer a secret manager or the Copilot automation
environment for production tokens):

```powershell
$env:LLM_EMUL_TOKEN = '<secret-if-required>'   # optional; not currently enforced
curl http://127.0.0.1:8000/v1/models
python scripts/llm_emul_worker.py --worker-id my-worker --once
```

Run the loop unattended (foreground; the heartbeat automation is what
keeps it alive across restarts):

```powershell
python scripts/llm_emul_worker.py --worker-id my-worker
```

## WSL/Linux preparation

```bash
export LLM_EMUL_TOKEN='<secret-if-required>'   # optional; not currently enforced
curl http://127.0.0.1:8000/v1/models
python3 scripts/llm_emul_worker.py --worker-id my-worker --once
```

Modern WSL commonly reaches a Windows-hosted loopback service directly. If
it does not, use the Windows host address or the relay's LAN/public HTTPS
name via `--host-ws-url`.

Do not run two loops under the same worker_id unless they are
intentionally sharing that identity's traffic -- a new connection under an
existing worker_id replaces the previous one as the active relay target.
Use distinct worker_ids for independent workers.

## Creating the Copilot automation

1. Open the intended workspace in Copilot Desktop.
2. Create a recurring automation for that workspace.
3. Choose a 30-second interval (a liveness heartbeat). The worker loop it
   (re)starts runs its own connect/idle/rest cycle, and the heartbeat only
   restarts it when no loop is alive, so heartbeats never stack loops.
4. Paste the customized prompt from this file.
5. Provide `LLM_EMUL_TOKEN` through the automation environment only if the
   server requires it; do not paste any token into the prompt.
6. Run the automation once manually and confirm
   `python scripts/llm_emul_worker.py --worker-id <id> --once` completes a
   clean connect before leaving it unattended.

Having this file and `scripts/llm_emul_worker.py` in a workspace prepares
everything the automation needs, but does not itself create or enable a
Copilot recurring task. Each Copilot installation/user must create that task
once.
