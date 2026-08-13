[Back to repository README](README.md)

# Codex TODO and Recovery Ledger

This file is the durable implementation and recovery ledger for Codex work in
this repository. It is intentionally separate from `AGENTS.md`: `AGENTS.md`
defines stable constraints, while this file records current state, pending
work, validation evidence, and safe recovery instructions.

Codex owns updating this ledger at meaningful implementation, validation, and
handoff checkpoints. Contributors may add tasks, correct stale facts, and mark
accepted work complete. Never place credentials, tokens, or secret `.env`
values here.

## Current recovery state

- Canonical checkout: `C:\snet\PeTTa\repos\symbolic_learner_workbench`
- Active branch: `codex/workbench-navigation-v2`
- Remote branch: not configured for the current local branch
- Latest validated commit: `064d537` (`Use the root Python environment for Workbench`)
- Python environment: one repository-root `.venv` containing all optional
  ARC3, workbench, test, notebook, and integration dependencies
- Frontend dependencies: `workbench/frontend/node_modules`
- Local `.env` is ignored by Git and must point at the canonical checkout;
  never copy its secrets into this ledger

## Completed and validated

- [x] Add the shared SingularityNET OpenAI-compatible LLM backend at
  `https://llm.c.singularitynet.io/v1`, with credentials resolved only from
  `SNET_API_KEY`.
- [x] Rename the active Backends navigation concept to Systems.
- [x] Give Systems a first-class `view=systems` route and `/systems` API.
- [x] Keep vendor/API backends exclusively in Models and model policy.
- [x] Add filesystem-backed system resources for Python, SWI-Prolog, MeTTa,
  the LLM System Caller, OmegaClaw, and Codex.
- [x] Allow the system schema to represent runtimes, agents, MCP servers, and
  plugins through `systemType`.
- [x] Make root `.venv` the single Python environment used by ARC3 and the
  browser workbench; prevent launchers from creating `workbench/.venv`.
- [x] Run the full Python suite: 317 tests passed on 2026-08-11.
- [x] Run the frontend production build successfully on 2026-08-11.
- [x] Run the focused Systems, mailbox, workspace, launcher, model-policy, and
  universal-editor suite: 97 tests passed on 2026-08-11.
- [x] Start the API and Vite UI on acceptance ports and verify the live Systems
  endpoint returns `codex,llm,metta,omegaclaw,python,prolog`.
- [x] Add a durable mailbox polling command with bounded checks, early message
  exit, monitored-port failure detection, and deterministic regression tests.
- [x] Add a repository-owned Codex heartbeat definition and document its
  mapping to the machine-local installed automation.

## Next work

- [ ] Visually inspect `http://127.0.0.1:16666/?view=systems` in the active app.
- [ ] Verify every System opens from the hierarchy and preserves tabs, dirty
  markers, split comparison, raw editing, filesystem save, and reload.
- [ ] Verify `?view=backends` redirects to Models and does not expose vendor
  backends in Systems.
- [ ] Add concrete MCP or plugin system resources only when real filesystem or
  connector data exists; do not add mock catalog entries.
- [ ] Decide whether Systems should retain the shared model-editor shell or
  receive a dedicated rich system-specific configuration panel.
- [ ] Open a draft pull request for `codex/systems-menu`, normally targeting
  `codex/workbench-navigation-v2` so the Systems diff remains focused.

## Runtime recovery

- [x] Install the standalone relay client under `.codex/mailbox/` for the
  stable identity `symbolic-workbench-codex`, with a workspace-specific
  README and bounded recurring-poll prompt targeting the local relay on port
  46667. The served client was repaired upstream to run outside its package.

- [x] Extract the JSONL/REST mailbox and Mattermost relay into the standalone
  sibling project `C:\snet\PeTTa\repos\mailbox_channel_relay_bridging_proxy`,
  branded **Mailbox Channel Relay Bridging Proxy**. Workbench now acts only as
  a client and external-service controller. The proxy owns loopback port 46667,
  stays healthy in mailbox-only mode, and reports optional adapter status.
- [x] Preserve `agent_mailbox.py` filesystem and `--url` compatibility while
  using transport-neutral identities and retaining the existing mailbox data.
- [x] Separate standalone proxy configuration under `config/` from durable
  mailbox data under `mailbox/`; support independent `--config-dir` and
  `--mailbox-dir` overrides without overlapping source or runtime files.
- [x] Add the client-side `--dir` JSONL override with deterministic transport
  precedence and serve the matching client from `/agent_mailbox.py`.
- [x] Expand the canonical mailbox client with named mailbox configuration,
  peek/follow, explicit cursors and acknowledgements, filtering, bounded waits,
  output formats/files, REST timeout/retries, checks, counts, and diagnostics;
  delegate the Workbench CLI entrypoint to that canonical sibling client.
- [x] Add the mailbox-backed Discord adapter with multiple listener support,
  inbound polling, outbound text/attachments, and delivery-ledger deduplication.
- [x] Add a safe public attachment gateway with configurable advertised URL;
  IRC now emits hosted links for image and other file attachments.
- [x] Add Matrix/Element and Slack mailbox adapters with multiple listeners,
  inbound polling/sync, threads, file transfer, and durable deduplication.
- [x] Add persisted channel-to-channel routes controlled either by mailbox
  relay agents or internal presence controllers, plus trusted `!relay` runtime
  administration using open mailbox identities; remove the obsolete
  `agents.json` registry entirely.
- [x] Add optional REST Bearer authentication: clients accept `--token` or
  `AGENT_MAILBOX_TOKEN`; servers enforce it only when `MAILBOX_RELAY_TOKEN` is set.
- [x] Add REST `--curl` dry-run output for every mailbox command with Bearer
  tokens redacted and no network side effects.
- [x] Package a cross-platform `AUTOMATION_PROMPT.md` explaining how users add
  a bounded, non-overlapping mailbox poller as a recurring Codex task.
- [x] Add a paste-ready `INSTALL_WITH_CODEX.md` bootstrap prompt that instructs
  another Codex to create and validate `.codex/mailbox/` in its own workspace.
- [x] Validate the standalone proxy suite (39 passed) and focused Workbench
  mailbox/service/system integration suite (18 passed) on 2026-08-13.

- [x] Pin OmniRoute's generic `PORT` and `DASHBOARD_PORT` variables to 20128
  so loading the repository `.env` cannot make its dashboard occupy the
  Workbench API port 8000.
- [x] Pin FreeRouter's inherited `CLAWROUTER_PORT` override to 18800 so it
  cannot occupy ClawRouter's port 3456.
- [x] Restrict Uvicorn live reload to application Python source changes under
  `workbench/server`, explicitly excluding generated `environment_files`,
  `runtime`, `__pycache__`, and server-test files so execution cannot restart
  the API.

The canonical development ports are:

- UI: `http://127.0.0.1:5173`
- API: `http://127.0.0.1:8000`
- Logs: `C:\snet\PeTTa\workbench-codex-session`

Process IDs are intentionally not durable. Rediscover listeners before stopping
services:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 5173,8000 |
    Select-Object LocalPort,OwningProcess
```

Stop only the PIDs currently listening on those two ports and only after
confirming they belong to this checkout's Vite and Uvicorn commands.

## Checkout cleanup still pending

The damaged historical checkout may still exist physically at
`C:\symbolic_learner_arc3_codex`, with a temporary alias at
`C:\snet\PeTTa\repos\symbolic_learner_workbench_broken`. A detached temporary
worktree may also remain at
`C:\snet\PeTTa\repos\symbolic_learner_workbench_systems`.

Do not delete or move these paths while Codex, Vite, Uvicorn, an editor, or a
terminal holds them open. Before cleanup, verify worktree registrations with:

```powershell
git -C C:\snet\PeTTa\repos\symbolic_learner_workbench worktree list
```

Preserve the canonical checkout and its `codex/workbench-navigation-v2` branch.

## Generic insertable inspection gallery checkpoint

- The corrected direct ARC3 chooser path now binds its selected `$game` into
  both downstream observation playgrounds. Live verification selected `s5i5`
  without running either optional gallery probe and visibly populated the next
  Operation's `game` input. Evidence: `artifacts/arc3_chooser_downstream_binding_verified.png`.
- Focused ARC3 tests: 10 passed. Frontend production build and `git diff
  --check` passed on 2026-08-12.

- Added shared `gallery.curate_resource` and `collection.random_list_element`
  filesystem Operations backed by `python/collection_operations.py`.
- The workflow editor can insert any abstract Operation after the selected step;
  the inserted node is immediately available through the normal playground path.
- Gallery invocation results render human-inspectable cards while preserving the
  identical structured artifact for downstream AI/Operations.
- ARC3's `arc3_random.build_game_preview_gallery` is only an intentionally costly
  demonstration. See `workbench/workspaces/arc3_random_player/docs/GAME_PREVIEW_GALLERY_BAD_EXAMPLE.md`.
- Focused ARC/gallery tests: 9 passed. Frontend production build and live browser
  insertion check passed. Changes remain uncommitted.
- Douglas clarified that Operations should be presented as durable delayed
  Codex/agent task specifications. The Operation Playground now makes this
  lifecycle explicit (`defined`, `running`, `completed`, or `failed`) while
  retaining inputs, outputs, implementations, and invocation evidence.
- The implementation ladder explicitly includes capable agents/LLMs,
  progressively smaller models, ILP/program-synthesis systems that derive and
  write code from specifications plus evidence, and the resulting deterministic
  implementations. Non-model execution is not assumed to be manually authored.
- Fixed filesystem Python Operation loading so an entrypoint can import sibling
  modules from its own source directory. This repairs the live ARC3 discovery
  failure (`No module named 'collection_operations'`) shown in Mattermost.
- Correction after superseded ordering guidance: discovery now fans out. The
  chooser depends directly on discovery and consumes `$games`; preview and
  Gallery Curation are disabled-by-default non-blocking probe steps. The engine
  persists optional disabled probes as `skipped`, while `required true` remains
  available to specialized workflows that intentionally turn a probe into a
  gate.
- ARC3 workflow refinement: `arc3_random.select_game` is again the semantic
  workflow step. Its preferred `Select Random` child delegates to the shared
  `collection.random_list_element` behavior, so selection itself is not defined
  as intrinsically random and can still be replaced by another implementation.
- After selection, the workflow now queries real workspace MeTTa sources,
  persists the selected game's default runtime AtomSpace, starts the game,
  enumerates its live controls, and only then enters capture/propose/execute.
  Live runners stay in a process-local session registry while workflow state
  carries a JSON-compatible handle. Focused ARC3 tests: 12 passed.
- Workspace visibility correction: `arc3_random_player` now includes the
  `arc3` workspace, labeled **ARC3 Shared Library**, with inherited resources.
  Because `arc3` includes `shared`,
  the effective layer order is `shared -> arc3 -> arc3_random_player`; the
  Random Player designer can therefore resolve and display the reusable shared
  resources plus ARC3's prompt-backed symbolic-analysis Operations and Prompts.
