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

- [ ] Refresh brittle source-text UI assertions after the accordion and active
  page refactor. On 2026-08-16 the production frontend build passed and the
  changed-test validation (using a repository-local pytest temp root) reported
  143 passed and 33 failed; most failures assert obsolete compact source
  strings, while runtime/browser acceptance remains the authoritative UI check.
- [ ] Restore a clean full-suite Windows run after fixing access to the shared
  `%TEMP%\\pytest-of-dougl` directory. The first full run was dominated by 130
  setup errors caused by `WinError 5`, not application exceptions.

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
