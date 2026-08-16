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

- Workflow UI invariant: every grouped accordion surface must be rendered by
  `ThreeStateAccordionStack`, and every direct member must use that stack's ID.
  Do not imitate stacking with wrapper divs, page grids, positioning, or CSS
  repairs. The workflow page has exactly three structural stacks: CENTER,
  LEFT, and RIGHT. CENTER owns the full workspace column between Resource and
  Docs. Its `LEFT + RIGHT` member contains the LEFT and RIGHT stacks.
- Accordion control invariant: existing accordion members are the page layout
  and control surface. Keep each control full-width inside the appropriate
  existing member. Do not add new accordion members, floating toolbars, cards,
  side controls, or independent control rows unless the user explicitly asks
  for a new panel.
- The canonical workflow accordion names and placement destinations are listed
  in `workbench/docs/design/WORKFLOW_ACCORDION_MAP.md`. When the user names an
  accordion, place the requested control inside that exact existing member.

- Canonical checkout: `C:\snet\PeTTa\repos\symbolic_learner_workbench`
- Active branch: `codex/workbench-navigation-v2`
- Remote branch: not configured for the current local branch
- Latest validated commit before this ledger update: `f350441b`
  (`Keep launch resource selectors above dotenv defaults`)
- Python environment: one repository-root `.venv` containing all optional
  ARC3, workbench, test, notebook, and integration dependencies
- Frontend dependencies: `workbench/frontend/node_modules`
- Local `.env` is ignored by Git and must point at the canonical checkout;
  never copy its secrets into this ledger

## Completed and validated

- [x] Restore the complete repository validation baseline after the navigation,
  resource hierarchy, and runtime-discovery changes. UI contract tests now
  normalize formatting locally instead of coupling behavior checks to Prettier
  whitespace; controlled tree branches assert their three-state display mode;
  the Documentation resizer and current legacy Workflow label are asserted by
  their live UI names; generated count-to-ten guides link back to the repository
  README; and temporary pytest trees are excluded from maintained-document
  discovery. Validation on 2026-08-17: `460 passed` using an external
  `--basetemp`; frontend `npm run build` passed (with only Vite's existing
  large-chunk advisory).

- [x] Extend the English Workflow Generation Order composer inside its existing
  `ThreeStateAccordionStack`: `[+group]` now creates and selects a simultaneous
  group; a composed `[group]` row runs only that group; the full-width insertion
  selector sits below the group's children; and every occurrence exposes a real
  filesystem-backed Prompt selector followed by an effective-model override.
  Prompt/model routing is serialized into nested `generation_steps`, group model
  overrides control the actual group invocation, the analyzer receives the
  effective Prompt catalog, and saved audit files retain both the full composer
  and the last subset run. Summary, Memory, Checklist, Outputs, Rules, Workflow,
  and Group rows now have distinct semantic background/border tints. Each group
  also owns a full-width inner shuffle control, independent of the existing
  top-level shuffle. The former New/Reuse/Preserve/Hide occurrence modes are
  removed. Every listed occurrence executes, and its compact `VISIBLE` control
  independently declares whether its current value is exposed to later stages
  of other output types (`peers`, default on) or exposed as the old value to a
  later occurrence of the same type (`updates`, default off). The twenty-one
  composer outputs now map one-to-one to filesystem-backed shared prompts. The
  authoring pipelines include `+englishsteps` -> `+steps` -> `+workflow`,
  `+libops` -> `+matchops` -> `+inventops` -> `+codeops` -> `+promptops`,
  `+libdt` -> `+matchdt` -> `+inventdt` -> `+codedt`, and
  `+libwf` -> `+matchwf` -> `+inventwf` -> `+codewf`. Operation prompts are
  proposed only for new LLM-backed implementations; deterministic Operations
  do not receive unnecessary prompt resources. Datatype and Workflow selection
  use the real effective filesystem catalogs. Groups can be copied with their
  child order, Prompt/model overrides, and visibility scopes preserved under fresh
  composer identities. New and restored rows default to their matching Prompt
  while retaining the override dropdown. Focused tests: 10 passed; frontend
  production build passed on 2026-08-16. Live browser validation confirmed all
  twenty-one full-width composer buttons, real filesystem Prompt defaults for
  `englishsteps`, `steps`, and `promptops`, and a copied group whose child order,
  selected Prompts, inherited-model overrides, and visibility scopes were preserved.
  The add-output composer now keeps its controls in the same existing accordion
  while placing the Operations (`libops` onward), Datatypes (`libdt` onward),
  and Workflows (`libwf` onward) pipelines on distinct full-width rows.

- [x] Add persisted system-wide model selection with a real model catalog,
  global fallback, and an explicit `Pervasive` checkbox that makes the global
  model override operation/policy choices while still allowing the Workspace
  Overview to declare a highest-priority workspace override. The
  `generate_count_to_ten` workspace currently overrides to SNET `asi1`; the
  global fallback remains MiniMax M3 with
  pervasiveness disabled. English-to-Workflow now browses the previous
  Workflow and returns a revised Workflow JSON object instead of compiling
  MeTTa, sends every multi-field runtime input to the LLM, limits its catalog
  to the shared workflow-language primitives, and requires a combined
  `new_memory_values_plan` companion output. The UI rejects incomplete output,
  adopts the combined plan in the existing Memory / Value Plan accordion, and
  leaves filesystem application as a separate user action. Focused tests (17)
  and the frontend production build passed. Live SNET invocations on
  2026-08-16 returned a 10-step Workflow with ten combined memory values from
  `asi1-mini`, then a 16-step Workflow with seventeen combined memory values
  from `asi1`; both reported zero unresolved operations and validation reports
  with no errors or warnings. The non-mini result remains an unapplied draft
  pending review because its loop condition appears bound to the initial count
  rather than a reevaluated count.
  OmniRoute Best Free was also exercised first, but its upstream free pool
  failed twice with HTTP 400/403 and then 429, so no draft was accepted from
  that route.

- [x] Rebuild the active Workflows layout as exactly three native
  `ThreeStateAccordionStack` surfaces: CENTER, LEFT, and RIGHT. CENTER now owns
  all authoring, preflight, `LEFT + RIGHT`, and reference members; the actual
  LEFT and RIGHT stacks are DOM children of `LEFT + RIGHT`; WORKFLOW RUNNER is
  first in LEFT; and RUNNER DESIGN REFERENCE is last in CENTER. Removed the
  old center-stack drag exception so every member remains reorderable. CENTER
  also has one native `− / * / +` stack control that updates all eight direct
  members together. No CSS resizing was added. The English-to-Workflow rich
  runner now loads its model selector from the effective `/models` catalog,
  and its operation binds the abstract `workflow.generate_from_english` prompt
  with a concrete MeTTa/JSON prompt variant rather than incorrectly treating a
  child prompt ID as an abstract prompt. Focused tests: 8 workflow-layout tests
  plus prompt-resolution regression tests passed; frontend production build
  and `git diff --check` passed; live validation confirmed only the three stack
  IDs, correct nesting/order, matching 546px CENTER/member boundaries, all
  eight members changing together, and 16 enabled model choices on 2026-08-16.

- [x] Remove the experimental `Workflows (New)` page, its navigation entry,
  `workflowV2` rendering state, component, and dedicated CSS. Legacy V2 URLs
  now resolve to the active Workflows page instead of producing a dead route.

- [x] Make the workflow Resource Browser respond to its own resizable width
  with named CSS container queries rather than browser-window media queries.
  At narrow widths, branch summaries, variant toggles, stage controls, badges,
  metadata, and child rows stack without horizontal overflow; an extra-compact
  layout applies below 210px. Focused navigation tests: 33 passed; frontend
  production build passed; live validation at a 250px pane confirmed stacked
  controls and no horizontal overflow on 2026-08-15.

- [x] Give every System Settings Workspace Registry row a lazy expandable,
  synchronized MeTTa/JSON editor for its complete filesystem metadata. Saves
  preserve custom fields, enforce the registry workspace ID, and refresh the
  structured row. Each row also reports its own recursive file count, disk
  usage, and nonzero local resource counts without inherited resources. A
  separate transitive usage metric reports how many project workspaces consume
  it and lists their IDs; the inverse metric reports how many project
  workspaces each row itself consumes and lists those IDs. Focused Settings and process tests: 15 passed;
  frontend production build and `git diff
  --check` passed on 2026-08-15.

- [x] Make Managed Process Startup Policy a canonical MeTTa/JSON resource at
  `shared_library_system/policies/workbench_startup.workbench_startup_policy.metta`.
  Settings and `run_workbench` now share that resource; the former JSON config
  is read only as a migration fallback and all new saves are physical MeTTa
  through the JSON compatibility provider. System Settings now embeds a
  synchronized structured/MeTTa/JSON editor for that resource, preserves
  invalid drafts, and disables save until source validation succeeds. Service
  entries now fully define labels, launchers/batch files, working directories,
  ports, health paths, command-match patterns, and control permissions as
  independent `managed_service` resources under `design/services`, so new
  managed processes can be added without code changes. Each service owns a
  `defaultStartup` fallback; the separate startup policy contains only optional
  `start`/`hidden` overrides. Services can declare `singleton`; launch is then
  suppressed whenever any matching process already exists, including an
  externally started process without the configured listener. Ambiguous
  `hidden` was split into `hiddenWindow` (console launch behavior) and
  `hideFromProcessViewer` (Processes-page visibility); Settings always requests
  the complete list, and legacy `hidden` is read as `hiddenWindow`. `allowKill` and
  `allowRelaunch` are independently enforced by both UI and API. Focused
  tests: 13 passed; frontend
  production build and `git diff --check` passed on 2026-08-15.

- [x] Expand the Processes viewer beyond listener-only discovery: each known
  service now reports every OS process whose command line matches the process
  the Workbench would launch, including independently started Flask/Uvicorn,
  Vite, OmniRoute, router, and mailbox process trees. Matching command lines
  are redacted before reaching the browser and the socket-owning process is
  identified separately. Every match is a first-class visible row, and a
  matching external process counts as detected even without the configured
  listener. Rows expose the live working directory plus confirmed per-PID
  Kill and Relaunch controls; the backend revalidates service/PID matching
  immediately before either local-only action. Focused service-monitor tests
  (6 passed), frontend
  production build, and focused `git diff --check` passed on 2026-08-15.

- [x] Rework Workspace Overview and System Settings boundaries: Overview now
  shows real local/inherited resource counts, every effective inherited
  workspace, and workspace-specific inclusion/credential controls. System
  Settings now owns the global workspace registry (project/library type,
  chooser visibility, recoverable deletion), run_workbench process startup
  and window-visibility policy, and system resource-provider status. The right
  inspector is filesystem documentation across pages. Focused tests: 36
  passed; frontend build and live Overview/Settings checks passed on
  2026-08-14.
- [x] Accept `menu=<view>` as a navigation deep-link alias, keep legacy
  `view=<view>` compatibility, and strip stale run-selection parameters when
  opening Workspace Overview. Focused navigation tests and frontend build
  passed; the clean `menu=overview` URL was verified live on 2026-08-14.
- [x] Put the automated ARC runner controls in the persistent top bar: mode,
  move limit, seconds per game, game limit, seed, selected-step execution,
  cascade, auto-play, pause, and stop all share the same run-input state. Live
  UI editing verification passed; focused UI/ARC tests: 51 passed; frontend
  build passed on 2026-08-13.
- [x] Fix automatic-session playground inputs so workflow defaults populate
  the visible final step (`60` seconds, `10` moves, seed `0`, automatic mode),
  while Python also normalizes explicitly null time/move limits. Live UI field
  inspection passed; focused UI/ARC tests: 51 passed; frontend build passed
  on 2026-08-13.
- [x] Replace the misleading workflow `Step` control with explicit execution
  controls: Previous/Next navigate without running, `Run this step` invokes
  exactly the selected Operation playground, `Run cascade` keeps whole-graph
  execution, and `Auto-play all` starts automatic mode. Live UI validation
  ran initialization, discovery, and the dependent filter one at a time;
  focused UI/ARC tests: 50 passed; frontend build passed on 2026-08-13.
- [x] Repair ARC3 Random Player cascade startup after automatic-mode inputs
  were added: workflow-level defaults are merged before required-input
  validation, the UI seeds editable run inputs with those defaults plus the
  active workspace root, and unused clock inputs were removed. Focused engine
  and ARC tests: 37 passed; frontend build and live UI startup passed on
  2026-08-13.
- [x] Rebuild the ARC3 Random Player outer loop around real UI-steppable
  operations: human or random game selection, zero-move initialization,
  per-move game-frame capture, an 11-frame replay gallery/GIF, and an
  interactive frame player with speed and scrub controls.
- [x] Track selected ARC games from an initially empty ordered list, filter
  the live catalog before random selection, and add an explicit final step
  selecting and remembering another unplayed game. UI validation selected
  `dc22` followed by distinct `tn36`, with `[dc22, tn36]` persisted in the
  workflow context. Focused ARC tests: 17 passed; frontend build passed on
  2026-08-13.
- [x] Keep shared libraries workflow-free and give every runnable application
  workspace at most one primary workflow. Moved six former library workflows
  into dedicated workspaces and removed the duplicate Random Player workflow
  and planning strategy from the combined image/ARC workspace. Ownership
  invariant and focused workspace tests passed on 2026-08-13.

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

- [x] Refresh the navigation and workflow-runner source-contract assertions
  after the shared three-stack accordion refactor. The formatting-insensitive
  reader is scoped to those test modules so it cannot alter runtime file reads.
  Focused validation: 68 passed on 2026-08-17.
- [x] Restore a clean full-suite Windows run. Runtime-discovery tests use a
  sibling `--basetemp` so repository ancestry cannot masquerade as a discovered
  runtime root. Latest validation on 2026-08-17: 460 passed.

- [x] Visually inspect the active Vite app at
  `http://127.0.0.1:5173/?workspace=shared_library_system&view=systems`.
  Root cards now show their provider instead of `inherits undefined`.
- [x] Verify all seven shared Systems open from the hierarchy into persistent
  tabs; raw editing produces a dirty marker and split comparison opens. The
  source/save/reload path remains shared with the tested model editor lifecycle.
- [x] Verify `?view=backends` redirects to Models and does not expose vendor
  backends in Systems. Confirmed in the live app on 2026-08-17.
- [ ] Add concrete MCP or plugin system resources only when real filesystem or
  connector data exists; do not add mock catalog entries.
- [x] Retain the shared universal hierarchy/editor shell while giving Systems a
  dedicated rich configuration panel and generic resource-operation runner.
  Systems no longer enter the model/preset configurator or model-only runner.
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
- Workflows and Workflow Runs are now one navigation destination. The separate
  Runtime rail entry was removed; Canvas, Editor, and Workflow runs are sibling
  tabs under Workflows, and existing `?view=workflowRuns` deep links continue to
  open the combined page's run-history tab. Focused navigation regression tests
  and the frontend production build pass.
- Workflow Canvas and Workflow Editor now share that same Workflows destination
  instead of appearing as separate top-level tabs. The canvas is the default;
  its resource-browser editor control opens the structural/source editor while
  keeping Workflows selected. Individual Operation resources retain their rich
  OperationLibraryEditor view from workflow resource links.
- The combined Workflow Editor keeps its workflow/Operation resource tree at
  the left while retaining filesystem documentation at the right. The wide
  artifact-editor layout no longer makes the workflow tree disappear.
- Every Operation playground now has an explicit **Edit Operation** link to the
  exact resource in the full rich editor, restoring discoverable access to
  alternatives/defaults, persistent tabs, split comparison, raw source, save,
  and execution techniques from within workflows.
- Every workflow step now presents **Run Workflow Step** and **Edit Workflow
  Step** panes. The edit pane changes that step's dependencies, bindings,
  outputs, parameters, probe settings, and implementation choice in the parent
  Workflow. Editing the underlying Operation remains a separate action.
- Context leak fixed: workflow runner controls are hidden outside Workflow
  Editor/Workflow Runs, and the standalone Operations page labels its action
  **Run Operation** instead of attempting a stale selected Workflow Step.
- Fixed the missing Workflow Step panes shown for `arc3_random.discover_games`:
  the reusable `arc3_random.*` Operation family now lives in
  `shared_library_arc3`, which the Random Player workspace actually includes.
  Its workflow references can therefore resolve to abstract Operations and
  Python implementations.
- Workflow Editor now begins with a full Workflow Runner setup surface rather
  than relying on launch buttons alone: workflow selection, readiness and
  resource-resolution diagnostics, editable JSON inputs, mode, move/time/game
  limits, seed, selected-step implementation context, validation, save, single
  step launch, durable workflow launch, and automatic all-games launch.
- Each **Edit Workflow Step** pane now uses the shared synchronized MeTTa/JSON
  source editor. Applying either representation updates the same selected step
  in the parent Workflow; the underlying Operation remains a separate resource.
- Workflow Editor and Workflow Runs stay mounted as adjacent center panes. The
  existing first two tab buttons act as focus controls, assigning roughly
  two-thirds width to the selected pane while leaving the other visible. Legacy
  `view=workflowRuns` links redirect into the combined view with Runs focused;
  the left resource tree and right documentation inspector remain visible.
- The full **Configure and launch a durable run** surface spans above both
  center panes. Their divider is a keyboard-accessible vertical separator that
  can be dragged between 20% and 80%; the two tab buttons remain 2/3-width
  presets. Live geometry verification confirmed the runner clears both panes
  and spans the available center width.
- Workflow steps now accept concise same-name output lists: JSON
  `"outputs": ["played_games"]` is normalized by the durable engine to the
  runtime binding `{ "played_games": "played_games" }`. The ARC3 outer loop's
  initial step uses the real shared `echo.value` operation to publish its empty
  played-games list without a bespoke initializer.
- The Workflow Runs **Filter Records** surface now includes live All, Running,
  Failed, and Cancelled counters directly beneath the runner/splitter area.
  Running includes durable waiting and paused runs; text filtering composes with
  the selected status instead of replacing persisted history.
- Workflow Runs now uses a selected-run workspace: a full-width Spline band
  occupies the top 20%, while a dense selectable run list and the primary
  Detected Objects/evidence pane share the lower 80% at 25/75 width. The latest
  active run is selected by default, selection remains highlighted, and the
  Topology/Chronology toggle changes only that run's visualization. Spline,
  Runs, and Objects each expose hover frame controls for minimize, maximize,
  and restore.
- The shell now exposes persistent mouse-resizable Resource Browser and
  Documentation dividers with saved widths and double-click restore defaults.
  Detected Objects supports list and tile views; it owns the primary left run
  workspace while the independently scrolling run selector occupies the right.
  The selected-run spline is bottom-anchored and minimizes downward. Workflow
  Editor and Workflow Runs tabs remain repeatable two-thirds layout presets.
- Workflow panel titles now toggle minimize/default directly for the runner,
  focal task editor, run history, selected-run spline, and detected objects.
  Minimized hover frames become explicit Restore controls, offset below titles.
  Resource Browser and Documentation titles follow the same toggle convention.
- The duplicate global Automated Runner strip is hidden. A composable,
  right-anchored title-bar stack now separates permanent global actions
  (Restart App, Switch Workspace, Reset layouts, Theme) from view-contributed
  restore actions; additions grow leftward. The focal stage count follows the
  selected durable run, with the loaded frozen workflow providing its stages.
- Navigation now writes semantic, shareable `view` URLs. Workflows uses
  `?workspace=<id>&view=workflows`; direct links restore the Workflow Editor,
  while legacy `view=canvas`, `view=editor`, and `menu=Workflows` links remain
  readable for compatibility.
- The right-hand runtime workspace now places a real single-run state inspector
  immediately above Detected Objects. STEP STATES, CHAPTER STATES (ARC3 game
  levels), GAME STATES, and ALL STATES never mix runs; workflow startup inputs
  are surfaced as STARTUP STATES. Each value has a JSON-compatible two-row
  property editor for enabled/always-ignore state, semantic datatype,
  STARTUP/STEPS/CHAPTER/GAME/ALWAYS/POST-MORTEM applicability, Preferred
  Renderer, and Treat As List. Guess, Image, MeTTa,
  JSON, and compact-text renderers remain available. The States navigation item
  deep-links to this inspector inside the combined Workflow view. Detected
  Objects remains the complete global pre-fill with stable artifact/provenance
  identity for future credit assignment.
- Workflow Runner performs a preflight enumeration of provisional
  `state_value` definitions from startup inputs and declared step outputs.
  The bootstrap infers stable IDs, source bindings, datatype/list hints,
  applicability, renderer, and source-aware `allowRedefinition` defaults;
  users can override enabled state, datatype, renderer, list handling, and
  redefinition before launch. The effective JSON configuration is persisted in
  the durable `workflow.started` event, while runtime steps remain responsible
  for attaching actual values and producer provenance. The same effective
  definitions immediately populate Detected Memory Values before launch; after
  launch that control prefers the frozen configuration from the selected run.
- Docs is now a repository-wide filesystem explorer backed by the existing
  filesystem provider. It starts with a `.md` path filter, can browse all
  approved text/source files, and presents a separate unexposed-path inventory
  with exclusion reasons. Secret candidates and unsupported file types are
  classified server-side, their contents never enter the index response, and
  the direct file endpoint enforces the same deny policy.
  The collapsible filesystem tree remains visible as the permanent left-side
  navigator, honoring the exposed/unexposed selection and path filter while
  documents open independently in the right pane.
  The navigator switches between a collapsible **Tree** and a flat
  **Navigator** result list; both modes share the exposure tabs and filter.
  The four-panel tab frame contains Exposed Full Path, Exposed Navigator,
  Exposed Tree, and Unexposed Full Path. Full-path panels preserve each
  complete repository-relative path on one row.
  Navigator mode behaves as a directory browser with breadcrumbs, folders,
  parent navigation, current-directory file rows, sizes, and filtered results.
  Every exposed text/source document now has a filesystem-backed editor with
  save support. Markdown retains rendered preview/source switching; JSON and
  notebooks are validated server-side before writing. The same path/exposure
  policy guards reads and writes; finer edit policy is a later layer.
  The source editor now uses CodeMirror with syntax modes for JSON, Markdown,
  JavaScript/TypeScript, Python, CSS, and HTML. Exposed PNG, JPEG, GIF, WebP,
  and SVG assets render through a separately policy-checked repository route.
  Every open file has reveal actions for Tree, Navigator, and Full Paths. They
  switch panels, clear conflicting filters, expand/navigate to the parent,
  highlight the file, and scroll it into view.
  Repository filters accept pipe-separated alternatives; for example,
  `.md|.txt` displays paths matching either suffix.
  Full-path lists have reversible sorting, in UI order, by File Name, File
  Size, Directory Name (full directory path), Parent Name (immediate directory),
  and Parent Bytes (matching total size in that directory).
  Path Depth is also available, counting repository-relative path segments.
  Independent Hide/Show `.dotdirs` and `.dotfiles` toggles compose with all
  filters, panels, and sorts.
  Both dot-path toggles default to hidden. The default include expression is
  `.md|.metta|.json`, and a separate pipe-aware exclusion line defaults to
  `runtime/|venv/`.
- The Processes page now renders service process matches as a collapsed
  service-to-PID disclosure tree. Each PID expands independently to show its
  working directory, command line, and unchanged relaunch/kill controls.
  Process discovery includes OS parent PID and parent process name; both appear
  in each collapsed PID row and its expanded details.
  Per-PID Stop and Relaunch no longer pass Windows `taskkill /T`; they target
  only the selected PID and explicitly state that parents and children are
  preserved. Whole-service Stop/Restart remains the deliberate tree operation.
  Process relationships are now an always-expanded visual hierarchy, not a
  disclosure control. Matching parent PIDs recursively own child rows, while
  parents outside the service match appear as explicit external root nodes.
  External roots no longer display an implementation-oriented “outside match”
  message. Their API records include redacted command line and working
  directory in addition to name and PID for full parent context.
  Parent restart evidence is merged directly into the original parent nodes:
  redacted command, working directory, and ready/missing status appear within
  the relationship tree rather than in a separate panel. The UI intentionally
  does not launch an arbitrary parent yet.
  Process-tree names, directories, and redacted commands wrap without ellipsis
  or clipping. Security-sensitive values remain redacted, but visible metadata
  is not truncated.
  Parent evidence uses the available horizontal space: identity, PID, working
  directory, redacted command, and readiness flow left-to-right, with a
  responsive stacked fallback only at narrower widths.
- System Settings now manages workbench-wide credentials through the protected
  `shared_library_system` credential store. Workspace-local credential rows
  explicitly say when System Credentials or the process environment already
  supplies a key, making the workspace override clearly optional.
  Backend metadata may declare `apiKeyOptional`, `api_key_optional`, or
  `credentialRequired: false`. Credential rows label OPTIONAL versus REQUIRED;
  a missing optional key explicitly says the backend may run without it.
- The global title bar now contains a visited-page breadcrumb trail immediately
  to the right of the brand. It grows rightward without truncating labels,
  scrolls horizontally when necessary, and clicking an earlier page returns
  there while trimming the later trail.
  Docs initially opens on Exposed Full Path with the default `.md` filter.
- [x] Preserve breadcrumb forward history when returning to an earlier visited page; discard it only after navigating somewhere new.
- [x] Record meaningful within-page states in the title-bar breadcrumb, including Docs panels, directories, and opened files, while excluding transient filters and sorting.
- [x] Reserve the left-middle workflow column as empty and stack the Workflow Editor and Workflow Runs surfaces together in the right-middle column.
- [x] Make Workflow Runner reflow against its actual parent width and height; remove the stage-wide JavaScript width override.
- [x] Rebuild the Workflow Runner presentation as a parent-sized vertical stack with full-width controls, stacked state records, and responsive actions.
- [x] Keep legacy workflow controls available under Workflow Editor while mounting isolated replacement launch and runs controls under Workflow Runs; hard-contain replacements inside the right column.
- [x] Roll the active Workflows UI back to the original Detected Memory Values composition while preserving all non-Workflow pages; keep replacement experiments disabled.
- [x] Add a separately namespaced DurableRunLauncher above Workflow Runs with a fixed header/footer, scrollable field body, container-responsive controls, and real workflow actions.
- [x] Delete the active legacy Workflow Runner markup and controller hooks; portal the isolated DurableRunLauncher into the left workflow column while Workflow Runs remains on the right.
- [x] Make the selected `STAGE n OF total` surface use the shared strip/scroll/full accordion contract for every selected workflow step and participate in the global left-column controls.
- [x] Recompose Workflows (Legacy) into independent accordion stacks: one Resource Browser contents accordion; Workflow Runner, Selected Stage, and per-step members in the left column; Workflow Runs plus Startup/Step/Chapter/Game/All state members and nested Detected Objects in the right column; and Left/Right Columns, Selected Run Spline, and Runner Design Reference in the outer stack. Remove the obsolete global All Panels and Workflow Steps controls so collapsing a workflow member cannot resize the Resource Browser.
- [x] Keep the selected strip/scroll/full button visibly highlighted on every three-state accordion control after its mode changes.
- [x] Establish a shared accordion-stack host and extensible strip contract. Right-column values/objects explicitly mount into the same registered stack as Workflow Runs, while the special Left Column / Right Column strip uses the shared accessory slot for its STACK, LEFT, and RIGHT control frames.
- [x] Make the shared accordion-member API own all four visual regions: a persistent strip/banner; a non-minimized item header; a mode-sized list/body that scrolls only in `*` mode and expands in `+` mode; and a non-minimized status/summary footer. Migrate Detected Objects to that API instead of hand-drawing peer chrome.
- [x] Make accordion frames own their item canvases and reflow. The shared API now supplies the constrained `*` height through `--accordion-scroll-size`, clips arbitrary item rendering to the body canvas, and owns body scrolling; `+` releases the constraint. Repair stack-aware parent-grid selectors so a 38px collapsed Workflow Runs strip immediately pulls the following value member upward, and keep the right-column value stack as the scrolling owner for all accordion canvases.
- [x] Move the Detected Objects configuration into the shared accordion member's four-region canvas and remove the orphan Separate View controls. Its strip remains visible in every mode, while minimizing hides its header, configuration/body, and footer and reduces the complete member to 38px so the stack reflows.
- [x] Make Workflow Runs, every Values scope, and Detected Objects literal peers: all seven are now immediate children of the same right-column accordion stack, with no intermediate memory-workspace or scope-stack wrappers drawing separate chrome.
- [x] Standardize the left workflow column on the same shared member renderer as the right. Workflow Runner, Selected Stage, and all 18 Workflow Steps now receive identical persistent strips, mode-owned canvases, borders, adjacency, and stack scrolling from the left-column accordion.
- [x] Register all three spline-stack peers with the shared four-region accordion renderer. LEFT COLUMN / RIGHT COLUMN owns its stack sizing buttons in the persistent strip and its independent LEFT/RIGHT controls in the item-header banner; Selected Run Spline owns Topology/Chronology in its item-header banner; Runner Design Reference receives the same persistent strip and per-item sizing controls.
- [x] Give every shared accordion member one continuous outer frame with a purple persistent strip and a darker attached item-header banner. Keep member-specific controls—such as independent LEFT/RIGHT sizing and Spline Topology/Chronology—inside that banner above the mode-controlled body.
- [x] Treat the complete left and right column stacks as the LEFT COLUMN / RIGHT COLUMN member body. Its shared status footer spans both columns after their content and before the next Spline member; the right stack no longer overlaps that footer row.
- [x] Make accordion strips vertically reorderable. While dragging, siblings temporarily render as a compact strip list; dropping moves the member one row, persists the order, and restores every saved strip/scroll/full frame. Runner Design Reference and Selected Run Spline derive their visible grid rows from this shared order rather than fixed legacy rows.
- [x] Infer capture-loop groups preflight from repeated workflow output bindings, assign value definitions by producer step, persist the plan with the run, group runtime artifacts by iteration, and show loopbacks in the preflight spline.
# Current workflow-control checkpoint

- The workflow preflight spline is a real accordion member above the LEFT/RIGHT controls and renders dependency branches, inferred repeated-output capture groups, and explicit bounded FOR/WHILE control arcs.
- `arc3_random_player.outer_loop` now describes the existing automatic session operation as two nested bounded loops: while unplayed games remain, and while elapsed game time is below the configured seconds-per-game limit. The existing `arc3_random.run_session` implementation remains the executable owner of those loops.
- Repository Docs can summarize the current exposed/filtered file list with a selected effective workspace model and configurable first-N-lines excerpts, persist the result under `workbench/docs/generated/`, and open the Markdown immediately in the right pane. Unexposed paths are rejected server-side.
- [x] Keep SingularityNET as an enabled shared LLM backend and add a real
  `snet-asi1` model child from its live `/v1/models` catalog, so effective
  workspace model selectors can use SingularityNET rather than showing an
  enabled backend with zero selectable models.
- [x] Identify ASI:One, ASI Cloud, and SingularityNET backend resources by
  normalized base API endpoints: `https.api.asi1.ai.v1`,
  `https.inference.asicloud.cudos.org.v1`, and
  `https.llm.c.singularitynet.io.v1`; preserve provider names separately.
- [x] Add backend aliases and alias-aware resolution so legacy IDs, provider
  names, hyphenated names, and literal base URLs resolve to the canonical
  endpoint-derived backend IDs without breaking existing model parents or API
  discovery routes.
- [x] Verify authenticated model discovery for ASI:One, ASI Cloud, and
  SingularityNET: each `<baseUrl>/models` request resolves its declared
  workspace/system/environment credential and sends it as a Bearer token.
- [x] Add `run_workbench.bat /kill [web_port] [api_port]` to stop the three
  router gateways plus the workbench API and Vite process trees. Shutdown is
  scoped by listener port and verified command evidence; it never broadly
  kills every Python or Node process.
- [x] Route the sibling Mailbox Channel Relay through `run_workbench` when its
  System Settings startup policy is enabled. Record every process actually
  launched by `start_with_policy.py` in an ownership ledger, and make `/kill`
  stop only those recorded process trees—including the relay—while leaving
  independently started services untouched.
- [x] Enforce the managed-launch invariant for all six long-running services:
  each final batch command is passed as a raw argument vector through the
  Python launcher. The ownership ledger records its root PID, working
  directory, raw command, and process-tree termination scope; child Node,
  Python, npm, and cmd processes remain descendants of that owned root.
- [x] Add the loopback-only managed-command submission API and batch client.
  `run_clawrouter.bat` now expands its port and submits the final `npx.cmd`
  argument vector to the Workbench API, which validates, launches, and records
  it. If the API is unavailable, the client emits a prominent warning and
  executes the same command in legacy mode.
- [x] Move every non-bootstrap daemon to that same API submission boundary:
  OmniRoute, FreeRouter, Vite, and Mailbox Relay batch wrappers now submit
  their fully expanded final commands. The API server explicitly reports its
  unavoidable bootstrap legacy mode; foreground dependency checks and
  installers remain untracked one-shot setup commands.
- [x] Enable Mailbox Channel Relay automatic startup by default and in the
  shared startup policy. `run_workbench` still checks port 46667 health first,
  so it starts the relay only when it is not already running.
- [x] Add delayed API-startup reconciliation for enabled managed daemons.
  After an API restart it restores missing Mailbox Relay/router services,
  skips disabled services, leaves healthy external listeners unclaimed, and
  excludes the bootstrapping API and port-ambiguous Vite process. Results are
  persisted to `runtime/logs/startup-reconciliation.json`.
- [x] Fix Windows raw-command parsing by placing an explicit `--` boundary
  before every `%ComSpec% /d /c ...` child command and stripping that marker
  inside `start_with_policy.py` before launch.
- [x] Fix the Windows trailing-backslash quoting failure in `run_demo.bat`:
  pass the workbench directory as `%ROOT%.` so quoted `--cwd` values cannot
  escape their closing quote and swallow the raw child command.
- [x] Make managed launches concurrency-safe: serialize API launch admission,
  deduplicate per-service requests while a listener is still starting, and use
  unique atomic ledger temp files so API reconciliation and `run_workbench`
  cannot collide or start duplicate daemons.
- [x] Preserve required batch-local environment across API-owned launches with
  strict per-service allowlists (OmniRoute ports, Vite host/port/API target,
  FreeRouter port isolation, and Mailbox Relay `PYTHONPATH`).
- [x] Replace blind daemon health sleeps with ownership-aware waits that fail
  immediately when the API-owned process exits before opening its health port.
- [x] Add the `generate_count_to_ten` project workspace as a minimal
  English-to-workflow acceptance fixture. It inherits Shared, contains an
  authoritative English prompt and documentation, and exposes an intentionally
  empty workflow target wired to `workflow.populate_from_english` for preflight
  generation.
- [x] Stack a real-data `WORKFLOW ACTIONS` accordion above Preflight Spline and
  LEFT/RIGHT on the active Workflow page. It enumerates effective authoring
  Operations, prioritizes Generate from English, and exposes memory planning,
  preflight, and run controls without mixing them into Add Step.
# Workflow description authoring (2026-08-16)

- `workflow.populate_from_english` is the semantic authoring boundary; description editing is an implied phase rather than a separate Operation.
- ENGLISH → WORKFLOW defaults to the top of the draggable spline accordion stack.
- Its UI is a nested accordion stack: English editor, model/format, memory/value plan, draft generation, validation, and apply.
- Memory/value inference now exposes a nested evidence accordion per value with origin, source binding, datatype, and current/default value; it explicitly distinguishes runtime inference from future English-description proposals.
- English-to-workflow prompts require complete operation prototypes and exactly one complete workflow resource in the selected format.
- Generate Draft embeds the canonical rich `OperationPlayground`, prepopulated with the English specification, complete effective operation catalog, workflow schema, memory/value plan, existing workflow, validation errors, and selected output format.
- Removed the redundant Model/Output accordion because those choices belong to the rich runner; system-injected `workspace_root` is no longer misclassified as an inferred workflow memory/value.
- Flattened authoring phases into the main draggable spline stack above the rich runner. Relocated Runner Design Reference out of the overlaid runtime grid into normal main-stack flow so mockups cannot float across runner inputs.
- [x] Add the real `English Workflow` route as three native `ThreeStateAccordionStack` columns: an editable filesystem English specification, a model-resolved generation surface, and a generated-contract stack. No contract fields are shown as inferred before Analyze runs.
- [x] Make Generation Contract analysis a filesystem-backed `workflow.analyze_generation_contract` LLM Operation. One response produces summary, memory candidates, acceptance checklist, output requirements, validation rules, and a candidate Workflow in a user-controlled order.
- [x] Replace decorative generation progress with `GENERATION ORDER`, an append-only in-page audit list of the actual button-press order and the concrete outputs created by each press.
- [x] Add contract-order trials with a recorded requested/returned order, selected model, heuristic coverage score, generated Workflow step count, and backend validation issue count. Live SNET asi1 verification with Workflow first produced 12 steps, 12 acceptance checks, 2 memory candidates, and 5 validation issues (80/100).
- [x] Make Generation Order a true composer. Clicking an output title appends an occurrence; the first occurrence defaults to New and repeated occurrences default to Reuse old. Every occurrence independently supports New, Reuse old, Preserve, or Hide, repeated output names remain in the submitted order, and the remove control is positioned between the cyclic left/right controls.
- [x] Make Analyze execute the exact composed `generation_steps` sequence in one LLM call and persist the requested steps, returned order, generated contract, candidate Workflow, validation result, model, and score to the workspace filesystem. The saved sequence is restored when the English Workflow page reloads.
- [x] Composer validation on 2026-08-16: 5 focused English Workflow tests passed, the frontend production build passed, and live browser verification confirmed an empty initial order, first Summary occurrence = New, repeated Summary occurrence = Reuse old, visible `← × →` controls, and no console errors.
- [x] Add `[group]` as a first-class highlighted Generation Order container. Creating or clicking a group selects it as the insertion target; output `+` buttons then add nested steps into that group, clicking it again returns insertion to the top level, and Analyze submits the nested steps as one simultaneous batch. Groups and their children retain per-occurrence modes, repeats, cyclic movement, removal, audit order, and persistence.
- [x] Group-container validation on 2026-08-16: focused English Workflow tests (5) and the frontend production build passed; live browser checks confirmed Summary and Memory inserted as nested `1.1`/`1.2` entries while highlighted, Workflow returned to top-level `2` after unhighlighting, and no console errors were emitted.
- [x] Make Generation Contract section arrows cyclic one-position rotations: left from the first position wraps to the end, and right from the last position wraps to the beginning.
- [x] Prevent experimental contract candidates from enabling Apply. Only the authoritative Generate Draft path can enable filesystem Apply after backend validation passes.
- [x] Make `workspace=` plus `view=` authoritative deep links. Initial loads,
  browser history, and in-app location changes now switch away from an already
  selected workspace when the URL names a different one; Switch Workspace
  clears the old workspace and runtime selection parameters instead of
  immediately reopening it.
- [x] Add durable State deep links with the canonical `state=<uuid>` query
  parameter. The States destination uses the real state-artifact history,
  resolves an older state UUID to its owning run through the engine API, and
  selects that exact record without replacing it with `runtimeRecord=`.
- [x] Drive English Workflow Generation Contract buttons from effective Prompt
  resources instead of a hard-coded React list. Applicable prompts now declare
  their button name, produced section, and sortable classification in MeTTa;
  the selected Prompt ID is persisted with each generated-order occurrence.
- [x] Make English Workflow contract-section controls filesystem-driven. The
  UI now discovers effective Prompt resources whose `applicability` includes
  `english_to_workbench.contract_section`, uses each resource's `buttonName`
  and exact Prompt ID when inserting a generation step, and orders the
  controls by durable `classificationId` with deterministic name fallbacks.
  All 21 shared section Prompts declare their applicability, button name,
  classification, and produced contract field. Live verification confirmed
  the classified order and that `+ summary` selects the Summary Prompt.

# Phase 2 semantic-memory records (2026-08-17)

- [x] Freeze versioned `Observation`, `EncounterRecord`, `RecognitionAccount`,
  artifact/provenance, instance-parameter, evidence, identity-decision, and
  per-object Turtle-reference contracts in the existing object-memory package.
- [x] Give observations, encounters, artifacts, evidence, match proposals,
  recognition accounts, merge decisions, and split decisions deterministic,
  order-stable construction paths while leaving durable object identity under
  `object_registry.pl` governance.
- [x] Add focused tests for Phase 1 node linkage, artifact/provenance layering,
  Turtle references, positive/negative evidence, rivals, reversible identity
  decisions, immutability, schema versions, and deterministic identifiers.
- [x] Add an append-only semantic `EncounterLog` with Phase 1 node-linked
  records, required prior-history ordering, idempotent replay, conflict
  rejection, per-object history lookup, and deterministic log hashing.
- [x] Wrap the established deterministic `analyze_grid` implementation behind
  `GridAdapter`. Preserve the exact source-grid hash, artifact URI, dimensions,
  coordinate contract, action-tree node, extractor provenance, candidate IDs,
  regions, and Turtle details while keeping provider intermediates outside the
  persistent observation record.
- [x] Add the backend-neutral `SymbolicStore`/`SemanticStoreBackend` boundary
  with exact write-once identity, conflict rejection, idempotent composition,
  semantic encounter history, and automatic artifact/Turtle indexing. Provide
  a deterministic in-memory backend for tests while leaving the durable
  backend slot open for Prolog or AtomSpace.
- [x] Connect `CellLogoForm` to the canonical Turtle DSL through the existing
  `SWIPrologBridge`. Correct extracted programs to stamp their initial cell,
  declare pen width, and preserve one-cell/disconnected objects; calculate
  regenerated-cell fit, distance, residual, and description length. Live
  SWI-Prolog 10.1.7 validation passed alongside the canonical DSL tests.
- [x] Generate supported thick rectangular objects as a single rotated Turtle
  movement with canonical `pen_width(1..4)`, not adjacent row enumeration. An
  exact-regeneration regression test requires one `set_pos`, explicit rotation,
  pen width, and equality with the source cells.
- [x] Add `SingleWriter.apply_evidence` as the calibrated path for object
  confidence. It validates evidence subjects, deduplicates deterministic IDs,
  preserves source provenance, accumulates positive and negative weights, and
  derives the same confidence and attribution regardless of arrival order.
- [x] Add explicit, idempotent `SingleWriter` merge/split application with
  same-type validation, decision/evidence provenance, active/demoted/tombstoned
  lifecycle states, prior-state snapshots, and reversible false-merge and
  false-split behavior. Keep generated Phase 1 `object_registry.pl` files as
  the eventual synchronization target rather than creating a second registry.
- [x] Add generic action-tree semantic-record linkage. Each node can maintain
  a deterministic, conflict-checked `semantic_records.json` manifest and
  GitHub-browsable README links while keeping Phase 2/3 payloads external to
  Phase 1 `state.json` and `Arc3Runner`.
- [x] Add an optional external post-capture observer seam to `Arc3Runner`.
  Observers receive current/previous nodes and action context after durable
  Phase 1 capture; failures are isolated so semantic services cannot interrupt
  gameplay or suppress other observers.
