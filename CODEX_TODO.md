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
- Latest validated commit before this ledger update: `24ff5a79`
  (`Add model policy history aggregation`)
- Python environment: one repository-root `.venv` containing all optional
  ARC3, workbench, test, notebook, and integration dependencies
- Frontend dependencies: `workbench/frontend/node_modules`
- Local `.env` is ignored by Git and must point at the canonical checkout;
  never copy its secrets into this ledger

## Completed and validated

- [x] Repair the Models `+ Backend`/`+ model`/`+ preset` creation flow so new
  documents are immediately dirty and therefore expose Save. Every pending
  save now has a logical **Save in workspace** selector populated from the
  workspace registry; the backend/model/system is written to that workspace's
  canonical lifecycle directory without exposing or asking for a disk path.
  Cross-workspace saves keep the resulting resource open under its destination
  workspace identity. Focused UI contract tests and the frontend production
  build passed on 2026-08-24.

- [x] Add the shared `enullm-8801` OpenAI-compatible backend resource for the
  local emullm relay at `http://127.0.0.1:8801/v1`, with LLM completion and
  vision capabilities, keyless configuration, the requested `yourelf.same`
  default model, and filesystem categories. Backend catalog parsing and focused
  resource validation passed on 2026-08-24.

- [x] Add filesystem-backed Workbench plugin discovery under
  `workbench/plugins`, a Plugins navigation submenu/page with manual refresh
  and persisted `startup`/`disabled` scan policy, and the first `web_proxy`
  plugin. The proxy exposes the allowlisted local emullm relay at
  `/web_proxy/http/127.0.0.1:8801/`, forwards GET/POST/PUT/PATCH/DELETE/OPTIONS/
  HEAD plus bidirectional WebSockets, and rejects non-manifest targets. Live
  smoke validation preserved the upstream GET status/content type and returned
  HTTP 200 from a proxied relay POST. Focused backend/navigation tests: 65
  passed; frontend production build and `git diff --check` passed on
  2026-08-24.

- [x] Give every Workbench plugin an administration/configure page. A plugin
  now publishes `admin.json` beside `plugin.json`; the scanner reads that file
  from disk without importing the plugin, so the Plugins page constructs the
  configure link, desktop `ui.pages`, and the initialization readiness report
  from the filesystem alone. The declared `path` is served by the plugin's own
  router on the API port and mirrored beneath `/api` for the browser, exposing
  `GET <path>`, `PUT <path>/settings`, `POST <path>/initialize`, and
  `POST <path>/actions/{action}`. Descriptors are data, rendered natively by
  `PluginAdminPanel`; a plugin exporting neither `create_admin_router` nor its
  own admin route receives `plugin_admin.generic_admin_router`, so no plugin is
  left without a configure page. Plugin initialization is declarative
  (`init.requires`, `init.files`, `init.install`, `init.steps`) plus an optional
  `initialize(manifest)` hook the loader calls before `create_router` and the
  page can re-run. `web_proxy` gained a real configure page with live target
  probing, an editable outbound allowlist, and transport settings that the
  running proxy re-reads from `plugin.json`.

  Fixed while doing this: plugin JSON was being written through the workspace
  resource API, which redirects every `.json` path to a `.metta` sibling, so
  configure-page edits silently produced `plugin.metta` and lost the manifest.
  Plugin configuration now uses new `read_config_json`/`write_config_json`/
  `config_file_exists` provider methods that never mirror to MeTTa and write LF.

  Validation on 2026-08-25: `tests/test_web_proxy_plugin.py` 11 passed;
  full suite 602 passed with only the pre-existing failures/errors unchanged
  (temp-dir `PermissionError` collection errors, `docs/CHAT_PAGE.md` back-link,
  `arc3_play_api.py` provider-boundary offenders, missing operation topics);
  frontend production build and `git diff --check` passed. Live UI verified end
  to end: configure page opened from the Plugins card, initialization checks,
  target probe, and a save that persisted to `plugin.json` and re-rendered.

- [ ] Known follow-up: the API dev server reloads only on `workbench/server`
  Python changes, so editing a plugin entrypoint under `workbench/plugins`
  needs an API restart. Widening `reload_dirs` conflicts with the deliberate
  guard in `tests/test_windows_dependency_bootstrap.py`; decide the intended
  policy before changing it.

- [x] Move the plugin administration declaration out of `admin.json` and into
  `plugin.json`, which is now the only manifest. A plugin declares `configPage`
  (an absolute URL to a page it serves itself, embedded by the workbench) or
  `adminPage` (an API path serving a descriptor the workbench renders natively).
  `plugin-install` declares initialization requirements, `plugin-init` lists
  commands one plugin asks another to run, and `ui.pages` installs menu entries
  in the workbench navigation. Each plugin may export `resolve_ui_pages` to say
  where its own pages live, and `apply_plugin_init` to accept commands; a target
  may return an `APIRouter` for the loader to mount so plugins never touch the
  application object. `web_proxy` gained persisted `mounts` that relay HTTP and
  WebSockets, and WS_COLLAB uses `plugin-init` to mount `/ws_collab` onto its
  standalone server. Renamed the `web-proxy` route to `web_proxy` so every
  plugin prefix equals its id.

  Fixed while doing this: both hand-merged manifests were invalid JSON (a `//`
  comment and a missing comma), `web_proxy` had a duplicated `label` and had
  lost `allowedTargets`, the loader's injected plugin-directory `path` silently
  overwrote the declared administration path so the configure page answered 404,
  and the WS_COLLAB console built `/v1/v1/auth/whoami` when served from inside a
  versioned mount.

  The Vite dev/preview proxy is now generated from the plugin manifests and
  their persisted mounts, and anything the web server does not own falls back to
  the API, so a new plugin route needs no config edit. The API root redirects to
  the web interface using `WORKBENCH_WEB_URL`.

  Validation on 2026-08-25: `tests/test_web_proxy_plugin.py` 15 passed; frontend
  production build passed. Live UI verified: both plugins load, install their
  menu entries, list clickable URLs, the native configure page saves to
  `plugin.json`, and the WS_COLLAB console reaches WebSocket transport through
  Vite → API → web_proxy mount → the standalone server.

- [x] Add `cadence=on-activation` to the WS_COLLAB worker monitor
  (`workbench/plugins/ws_collab/ws_collab/workers.py`), resolving the tension
  between the health monitor (warn ~60s, overdue ~120s, unresponsive ~300s) and
  the doctrine's ban on agent keep-alive loops: an agent that only runs when its
  recurring automation fires was previously guaranteed to be flagged as a
  failure. A worker now declares `meta.cadence = "on-activation"` at
  registration. Its state is still tracked truthfully, but its alerts become
  severity `info` with `confirmation_required` false, it gets no unresponsive
  TTS announcement, and it is excluded from the all-workers-down team-failure
  check, which is now judged only over continuous-cadence workers. `cadence` is
  exposed on `GET /workers` and on every alert. Designed jointly with the `zira`
  agent over the WS_COLLAB conversation stream, which proposed exactly this
  combination and rejected simply raising the global thresholds because that
  hides real failures.

  Rewrote the WS_COLLAB long-running prompt (published as version 2 through
  `POST /ws_collab/v1/prompt`, version 1 preserved in durable history; also
  written to `emullm/.git/long_running_prompt.txt`). It now documents that
  **Copilot's own built-in Workflows cron is the approved recurring launcher**,
  with a worked `save_workflow` example, and that one minute is the floor
  because cron's smallest field is minutes - so a 10s or 30s cycle is not
  achievable and must be reported rather than simulated. OS schedulers,
  watchdogs, self-revival scripts, and wrapper loops remain prohibited. It also
  distinguishes the two activation shapes (bounded monitor vs persistent
  worker), explains mechanically how a persistent worker holds its turn, and
  corrects the WebSocket contract: the client sends `ping` and the server
  answers `pong`; the server's own `ping` must not be answered.

  Validation on 2026-08-25: `tests/test_workers.py` 20 passed (16 existing plus
  4 new covering declaration, informational alerts, continuous workers still
  raising danger, and team-failure exclusion); full ws_collab suite 252 passed
  with 1 pre-existing failure (`test_event_store.py` hits a Windows
  atomic-replace `PermissionError` in `jsonl_store.py`, untouched by this work).
  Verified live after restarting the 8802 server: registration reports
  `cadence: on-activation` and it appears on the worker roster.

- [x] Re-hosted Overview inside the standard resource-page shell so it behaves
  like other pages (for example Events): normal page body container, top menu
  row placement, and persistent docs/help context on the right instead of the
  previous bare/full-bleed wrapper behavior.

- [x] Seeded shared `design/models/model_overridden_properties.json` with
  initial web-sourced capability metadata for all current shared model
  resources. Data now includes OpenRouter-derived modality/token-limit fields
  where available, Hugging Face embedding metadata for BAAI/UAE models, and
  explicit unresolved notes for models without reliable public capability
  evidence in this pass.

- [x] LLM top menu modes are now real mode-specific pages on the Models
  surface: **Browse Models**, **Discover Public Properties**, and
  **Override**. Discover mode auto-focuses backend discovery, lets users select
  a worker model, and runs a web-grovel capability prompt (vision/multimodal,
  token limits, and related metadata) that merges into
  `design/models/model_overridden_properties.json`. Override mode is now a
  dedicated filesystem-backed editor for that override resource.

- [x] Workspace chooser cards now report per-resource inheritance splits without
  requiring any workspace to be opened first. Discovery now includes
  `resourceCountBreakdowns` for workflows, operations, datatypes,
  representations, models, and prompts, each with `total`, `local`,
  `inherited`, and `overridden` counts. The chooser summary renders entries in
  the format `N resource (L local / I inherited / O overridden)`.

- [x] Add a new ARC3 workflow page `arc3.two_image_prolog` for two-image upload
  and contract-driven Prolog extraction. The new renderer
  (`arc3_prompt_prolog`) is wired into `FilesystemWorkbenchPage`, presents
  dedicated BEFORE/AFTER image inputs, runs the provided combined prompt
  contract against a selected enabled model, and renders parsed outputs for
  `new_identities`, `objects_pl`, `differences_pl`, `similarities_pl`,
  `turtle_from_image_pl`, `turtle_from_diff_pl`, and `rules_pl` with a raw
  response fallback panel. Added filesystem page source editing in the right
  column via `ResourceSourceEditor`. Validation on 2026-08-18: `pytest -q
  tests/test_visual_image_diff_ui.py` passed (19 passed) using a repo-local
  temp directory override, frontend `npm run build` passed, and
  `git diff --check` passed.

- [x] Reorganize the active Workbench around the human/AI blackboard model:
  Workspace owns Overview, Goals, Planning, and Workflows; Capabilities owns
  Operations, Source Code, Systems, Models, Datatypes, and Policies; Knowledge
  owns Data, AtomSpaces, and Artifacts; Runtime owns Goal Runs, Executions,
  Events, States, and Logs; System owns Model Policy, Benchmarks, Processes,
  and Settings. Source Code reuses the Prompt editor and language-filtered
  Operation implementation editors for Prolog, MeTTa, and Python. Systems
  configures callable runtimes and agents separately from model backends, while
  Models retains backends, models, and presets. Data and AtomSpaces are
  knowledge surfaces rather than design-time datatype definitions. The active
  rich editors, documentation panel, deep links, and legacy route aliases are
  preserved. Navigation, Source Code, policy, and Systems contract validation:
  58 passed; frontend production build passed on 2026-08-17.

- [x] Add selectable Model Policy performance-history aggregation. The chart
  can display every persisted result, the latest point per model/preset series,
  or an average per series without changing the exact chronological result
  rows. Model-policy focused validation: 44 passed; frontend production build
  passed on 2026-08-17.

- [x] Make the Visual Image Diff structural columns adjustable without moving
  any content outside its existing `ThreeStateAccordionStack`. The default
  desktop proportions now match the accepted wide layout at approximately
  `1 : 2.8 : 1.9` (LEFT : CENTER : RIGHT). The two stack borders are pointer
  drag handles with keyboard adjustment, persist their ratios in browser
  storage, and reset to the accepted proportions on double-click. Existing
  two-column and one-column responsive layouts remain unchanged and hide the
  inactive drag borders. Focused Visual Image Diff/navigation/workflow tests:
  73 passed; frontend production build and `git diff --check` passed on
  2026-08-17. The full repository suite passed with `586 passed` using an
  external pytest base directory. Live browser validation confirmed the two
  separators, accepted reset proportions, and identical width state in a
  freshly opened tab after adjustment.

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
- [x] Implement `SemanticGridCaptureObserver` on the external seam. It writes
  deterministic Observation and Encounter JSON records, SHA-256-addressed
  per-candidate Turtle artifacts, previous-encounter chains, semantic-store
  entries, action-tree manifests, and README links while retaining candidate
  status until registry-backed recognition commits durable identity.
- [x] Enrich the established grid extractor with normalized geometry/topology:
  exact bounds and boundary cells, enclosed hole regions, connected-component
  count, line thickness, and pairwise spatial relations. Cover hollow,
  irregular, thick, and disconnected fixtures without changing the adapter
  boundary.
- [x] Add deterministic `InstanceMatcher` correspondence proposals. Explain
  matched and changed fields, identify declared transformations, retain every
  rival in stable advisory order, and create recognition accounts without
  allowing even perfect similarity to commit identity or confidence.
- [x] Add deterministic `ObjectChange` records and `ChangeDetector` handling
  explicit correspondences. Cover movement, recolor, resize, orientation,
  reshape, appearance/disappearance, one-to-many split, and many-to-one merge
  without treating advisory proposals as authoritative correspondence.
- [x] Extend generated `object_registry.pl` files through a managed,
  append-only `semantic_identity_decisions.pl` sidecar retained across manual
  and GPT registry rewrites. Only friendly registry IDs are accepted; SWI-Prolog
  loading and accepted/reversed history queries are verified.
- [x] Add `RegistryCorrespondenceAuthority`: explicit registry selection and
  attributable evidence are mandatory even for a perfect match; acceptance
  calibrates through `SingleWriter`, preserves rivals and property explanations,
  emits a recognition account, and records encounter/decision/evidence history.
- [x] Turn encounter history into durable unresolved recognition work. Select
  the latest known instance per identity, persist every competing proposal,
  and persist an unresolved account without authorizing identity by similarity.
- [x] Invoke unresolved recognition from live semantic grid capture whenever
  known identity history is present, persist proposal/account artifacts beside
  the state, and link them through the action-tree semantic manifest.
- [x] Build deterministic signed evidence from correspondence explanations.
  Exact properties and allowed transformations support identity; unexplained
  changes contradict it, while aggregate similarity remains advisory only.
- [x] Represent Turtle reconstruction fit as signed identity evidence. Preserve
  the artifact, fit parameters, and measured residual; exact regeneration
  supports identity while a nonzero residual contradicts it.
- [x] Invoke Turtle reconstruction during every semantic grid capture through
  the real SWI-Prolog Turtle DSL. Persist fit score, distance, residual, and
  description length on each Turtle reference; emit separately attributable
  reconstruction evidence into the encounter, semantic store, action-tree
  manifest, and deterministic replay. Renderer failures remain infrastructure
  warnings and never become fabricated negative identity evidence.
- [x] Expose explicit live registry authorization controls. Semantic observers
  enumerate only pending proposal identities present in the friendly Prolog
  registry; `Arc3Runner` forwards accept/reject selections without exposing
  observer internals. Acceptance requires proposal-linked evidence and the
  `SingleWriter`, while rejection records append-only history without changing
  confidence. Both persist a resolved account beside the originating node.
- [x] Enable semantic capture in the canonical interactive and Prolog-controlled
  ARC3 runners. A shared composition factory binds the established grid
  extractor, runner grid accessor, SWI-backed observer, semantic store, and
  single identity writer; both entry points provide an explicit
  `--no-semantic-capture` opt-out instead of silently omitting object memory.
- [x] Add complete deterministic semantic-store snapshots and replay. Restore
  all exact record namespaces in dependency order, rebuild encounter/artifact
  indexes, reject unknown namespaces, and make repeated replay idempotent.
- [x] Expose live recognition evidence through Phase 1 inspection. Persist and
  link evidence beside proposals/accounts, then summarize candidates, selected
  identity, advisory similarity, polarity, confidence, decision source, and
  rivals in each action-tree node README.
- [x] Replay semantic state directly from Phase 1 action-tree manifests. Decode
  exact nested records, deduplicate repeated links, restore encounter chains in
  predecessor order, and reject missing or cyclic history rather than silently
  producing a partial store.
- [x] Make each named English Workflow Generation Order title a quick-call
  control. Section titles now run only their existing configured generation
  step; `[group]` runs only its nested batch, while the Prompt-discovered `+`
  controls remain the sole way to append another occurrence.
- [x] Add a durable SWI-Prolog `SemanticStoreBackend`. Persist exact typed
  records as inspectable `semantic_record/3` facts, atomically rewrite the
  store, round-trip nested/unicode payloads, hydrate facade indexes after a
  restart, and verify the generated store with live SWI-Prolog.
- [x] Make durable identity commits duplicate-safe and preserve typed confidence
  history. Repeat compatible commits return the calibrated object, conflicting
  payloads fail, and evidence/lifecycle transitions survive snapshots and
  Prolog reloads through merge, split, demotion, tombstoning, and reversal.
- [x] Model degraded recognition explicitly. Add reflection, visibility, and
  noise instance parameters; explain declared degradation with signed evidence;
  and retain the best complete stored form when a later encounter is partial or
  noisier while still updating its position and supported transformations.
- [x] Connect live parent/current captures to semantic change history. Match
  stable candidates across consecutive observations, persist correspondence
  proposals and evidence-linked `ObjectChange` records, link readable summaries
  into the action tree, and retain them through disk and Prolog replay.
- [x] Separate explained transformations from potentially new structure.
  Preserve unexplained property changes as deterministic provisional residuals,
  persist and inspect them in live action trees, and round-trip them through
  semantic snapshots and the SWI-Prolog backend.
- [x] Track structured residual recurrence without auto-committing identity.
  Emit a distinct occurrence record each time, remain provisional initially,
  and advance repeated unexplained structure to `commit_request` only through
  the deterministic `ResidualGate`.
- [x] Preserve and recognize normalized grid topology. Carry normalized boundary
  cells, holes, component count, and thickness into semantic instances; prove
  translated topology with signed evidence; and regression-test exact hollow
  object regeneration through live SWI-Prolog without filling its hole.
- [x] Add the filesystem-backed `Visual Image Diff` page as three native
  `ThreeStateAccordionStack` columns. Persist the corrected ACTION3 then
  ACTION1 image sequence as workspace assets and a sequence manifest;
  split the former monolithic ARC3 analysis prompt into classified Prompt
  resources; and initialize the composer from one ordered Prompt Profile group
  while retaining inline `+ step`, removal, and reordering controls.
  The center stack's single `GENERATE VISUAL DIFF` accordion now uses the
  English Workflow composition model: selected model first, an inline Prompt
  resource palette, selected-group insertion, `[+group]`, group copy/shuffle/
  clear, wraparound rotation inside and outside groups, Prompt and effective
  model selectors, and independent `peers`/`updates` visibility. No editable
  surface was moved outside the page's three native accordion stacks. Focused
  tests (5), frontend production build, `git diff --check`, and live selected-
  group insertion/copy verification passed on 2026-08-17. Visual Image Diff
  stack controls are semantic headers with their collective size buttons built
  into the header. Each header freezes against its own independently scrolling
  stack rather than floating against the page scroll surface. Frontend build,
  `git diff --check`, 59 focused accordion/navigation tests, and live DOM/
  screenshot verification passed after the header refinement. Full repository
  validation after the refinement: 529 passed in 43.18s using an external
  Windows base-temp directory.
- [x] Make Visual Image Diff executable without leaving its three accordion
  stacks. The left sequence accordion accepts multiple image uploads, the
  center `GENERATE VISUAL DIFF` accordion selects an effective model and runs
  the selected group as one real model invocation, and the right `RESOURCE
  OUTPUTS` accordion displays status, errors, usage, and response text. The
  browser prepares a labeled contact sheet so every ordered image can pass
  through the existing single-image model endpoint. Center prompt rows now
  fit their accordion body at narrow widths, reserve a stable scrollbar
  gutter, and no longer place text or controls underneath the scrollbar.
  Added the requested eleven-stage source/normalize/object/Turtle/compare/
  rules/Prolog/validate/report pipeline as filesystem Prompt resources and
  placed them first, in supplied order, inside the existing
  `visual_image_diff.analysis_group` profile. The workspace manifest now
  distributes those eleven prompts across the five real
  `free_staged_symbolic_analysis` transaction groups: Objects (6), Changes
  (1), Prolog (1), Rules (1), and Audit (2). The first Objects entry therefore
  starts as a group rather than eleven unrelated composer rows. Model selectors
  now display the resolved backend label beside the model name while retaining
  the model resource ID as the invocation value. Accordion summary-strip clicks
  now cycle through all three native sizes (`strip`, `scroll`, `full`); the
  three sizing buttons remain direct state selectors. Visual Image Diff prompt
  and group titles now also execute as quick calls, matching the English
  Workflow generation-order behavior while submitting the current ordered
  image sequence. The former separate `+ STEPS` and `GROUP PROMPT` members are
  merged into that one center accordion, with the same compact inline composer,
  wide horizontal rows, narrow stacked rows, shuffle/clear actions, and primary
  run placement used by English Workflow. Focused Visual Image Diff tests (8),
  frontend production build, `git diff --check`, and live browser verification
  of one center member, twelve inline add controls, five groups, and eleven
  nested prompt steps passed on 2026-08-17. Full repository validation after
  the unified composer change: 539 passed in 54.46s. The RIGHT stack now also
  has a separate item-level `PROMPT CONTENT` member alongside the retained
  whole-transaction `COMPOSED GROUP PROMPT`: touching or focusing any of the
  eleven individual pipeline Prompt rows selects and highlights that resource,
  opens the inspector, and displays its complete filesystem-backed text plus
  ID, label, classification, applicability, and produced values without
  truncation. Changing a row's Prompt selector updates the same inspector.
  Focused item-inspector tests (9), frontend production build,
  `git diff --check`, live selection verification, and the full repository
  suite (543 passed in 59.29s) completed on 2026-08-17.
- [x] Add an in-page Visual Image Diff UIX comparison without replacing the
  established flat composer. CENTER now contains the original `GENERATE
  VISUAL DIFF` member unchanged and a second `GENERATE VISUAL DIFF ·
  SUBACCORDION UIX` member bound to the same filesystem Prompt resources,
  model choices, composition state, visibility routing, ordering actions, and
  invocation path. The alternate view renders five top-level group resources
  and their eleven Prompt steps as native nested `ThreeStateAccordionMember`
  instances with independent three-state controls. Managed-order accordion
  members follow the shared semantic order and intentionally disable a second,
  conflicting drag order; all existing members remain draggable. Live browser
  verification confirmed five flat rows, five group accordions, eleven nested
  Prompt accordions, right-side Prompt inspection from the alternate view,
  shared edits between both presentations, vertical scrolling, and no
  horizontal overflow. Focused accordion/navigation/UIX tests: 72 passed;
  frontend production build and `git diff --check` passed; full repository
  validation: 557 passed in 65.55s on 2026-08-17. The alternate version's
  sublist now uses native collapsed accordion strips carrying the same compact
  controls as `workflow.populate_from_english`: ordinal/state cycling, quick
  run title, `peers`/`updates`, filesystem Prompt selection, backend-qualified
  model override, and wraparound left/remove/right actions. Parent groups stay
  expandable while all eleven nested Prompt members start in `strip` mode and
  retain their own `_ | * | +` selectors. Long values remain horizontally
  reachable inside each strip and are not shortened. Frontend build, focused
  72-test validation, live verification of 11 compact Prompt strips, strip to
  scroll to strip cycling, and screenshot inspection passed on 2026-08-17.
  Full repository validation after the compact-strip refinement: 582 passed
  in 80.52s using an external Windows base-temp directory.
- [x] Make each expanded Visual Image Diff transaction a real Workflow Item +
  Operation debugger inside its existing `ThreeStateAccordionMember`. The
  debugger uses the shared rich `OperationPlayground`, retains Run/Edit
  Workflow Step tabs, and lists the exact filesystem Prompt resources used by
  the selected Prompt implementation. Replace the Prolog group's incorrect
  Turtle-renderer binding with the semantic `symbolic.get_prolog_evidence`
  Operation. Its default `prompted_llm` child binds the existing cherry-pick
  Prompt, while its `python` child deterministically collects all seven Prolog
  artifacts and asks SWI-Prolog to load-check them when available, with no
  Prompt or LLM call. The workflow keeps the semantic Operation stable and
  persists only the selected implementation override. Live browser verification
  confirmed both choices in the rich cascade selector and confirmed that the
  Python route visibly changes to `NON-PROMPT OPERATION DEBUGGER`. Focused UI,
  navigation, editor, and provider validation: 123 passed; frontend production
  build passed; full repository validation: 618 passed in 76.83s on
  2026-08-17.
- [x] Restore English Workflow as a first-class page and bind every one of the
  13 current project workflows to a real editable English description. Eleven
  missing `docs/WORKFLOW_DESCRIPTION.md` companions were derived from their
  filesystem workflow resources; the existing ARC3 and count-to-ten documents
  were retained. Entering English Workflow now refreshes a missing in-memory
  description binding from the shell snapshot, so descriptions added after a
  workspace was opened appear without making descriptions a catalog admission
  requirement. A behavior regression proves a workflow with no generation
  metadata still joins the workflow catalog. Live browser verification showed
  the complete editable Review with Approval document. Focused English,
  navigation, workflow-resource, and shell-snapshot validation: 81 passed;
  frontend production build and `git diff --check` passed. Full repository
  validation reached 636 passed with one unrelated pre-existing datatype
  backlink failure (`information.children` is missing `system_contract`) on
  2026-08-17.
- [x] Make the eleven Visual Image Diff pipeline Prompts model-provider
  neutral. Removed embedded OpenAI, Groq, and OpenRouter profile IDs from the
  Objects, Changes, and Rules stage contracts and removed the four legacy
  OpenRouter defaults from the five-group workspace manifest. Each Prompt row
  now inherits the page's selected workbench backend/model unless the user
  explicitly chooses a row override. Focused Visual Image Diff validation:
  13 passed; `git diff --check` passed; live browser verification confirmed
  all eleven Prompt steps loaded with no provider-profile strings and the
  current `ASICloud · asi1` selection on 2026-08-17.
- [x] Match the approved Visual Image Diff SUBACCORDION UIX framing. Every
  group keeps one permanent compact strip with its ordinal, `[group]` title,
  `visible`/`peers`/`updates`, group type, backend + model, left/remove/right,
  and native `-`/`*`/`+` sizing controls. Its only expanded item-header row is
  `SELECTED`, `COPY`, `SHUFFLE`, and `CLEAR`. The expanded body contains only
  the nested compact Prompt strips; the duplicate play row, flags, selectors,
  movement controls, and transaction label were removed. The attached footer
  identifies the resolved Workflow Item + Prompt or non-Prompt Operation and
  exposes `INPUT / OUTPUT` plus `RUN GROUP`; `INPUT / OUTPUT` lazily opens the
  existing rich Operation playground rather than duplicating it in the body.
  Focused Visual Image Diff validation: 14 passed; frontend production build
  and `git diff --check` passed. Live browser verification confirmed the full
  compact strip, exact four-button header, six nested compact Object prompts,
  zero duplicate body control rows, and a real six-field playground opened
  from the footer on 2026-08-17.
- [x] Keep the original Visual Diff composer and SUBACCORDION UIX synchronized
  through one shared Workflow Item + Operation playground renderer. The
  original composer now exposes the selected group's rich playground while the
  UIX keeps one playground per expandable group; both write workflow-step and
  implementation changes to the same live composition state. Focused Visual
  Image Diff validation: 14 passed; frontend production build passed; live
  browser verification confirmed both presentations resolved the Objects route
  to `vision.extract_scene_objects.automatic_llm` and selected
  `asicloud-asi1` on 2026-08-17.
- [x] Make the Visual Image Diff columns a real data-authoring-source flow.
  `LEFT STACK · DATA` begins with `RESOURCE OUTPUTS` as its declaration/index,
  followed by the filesystem image sequence and transition context; the same
  member also accumulates real playground outputs. `CENTER STACK ·
  AUTHORING` retains both composer presentations and the shared rich Operation
  playground. `RIGHT STACK · SOURCE DETAILS` is limited to the selected Prompt
  resource and the composed group Prompt. Opening a center playground now
  resolves its declared inputs from the left-side data aliases (including
  current/previous images, image collections, manifests, and sequence context),
  and successful executions merge their outputs back into the left stack for
  later steps. Live browser verification confirmed the three stack roles and
  prefilled current/previous filesystem asset URLs. Focused Visual Image Diff
  validation: 16 passed; frontend production build passed. Repository-wide
  validation reached 643 passed; all five temp-location-sensitive failures
  passed when rerun with an external base-temp, leaving only the unrelated
  pre-existing `fan_out_and_merge` editable-workflow `version` violation on
  2026-08-18.
- [x] Make filesystem `workflow_page` resources the sole source of the
  WORKFLOWS submenu and expose raw executable Workflow resources separately
  under CAPABILITIES as `Workflow Resources`, backed by the existing rich
  Workflow Editor. Effective workspace plus inherited page specifications are
  enumerated on workspace load and ordered by `menuPlacement` (`first`,
  `middle`, `last`), then numeric `order`, then label. The shared `Generate
  Workflow` page is first and ARC3 `Visual Sequencing` is middle. Every
  three-column page specification is now required to include a minimized
  `CURRENT PAGE SPECIFICATION` `ResourceSourceEditor` bound to its own
  filesystem `workflow_page` JSON; English Workflow and Visual Sequencing both
  expose and save that resolved source through the shared editor. Live browser
  verification confirmed the ordered page-resource menu, the separate rich
  Workflow Resources route, and editable source JSON on both three-column
  pages. Focused workflow-page/navigation validation: 106 passed; runtime
  discovery validation with an external base-temp: 13 passed; frontend
  production build and `git diff --check` passed. Full repository validation:
  653 passed with only the unrelated pre-existing `fan_out_and_merge`
  editable-workflow `version` violation remaining on 2026-08-18.
- [x] Softcode the shared `Generate Workflow` page entirely from its filesystem
  `workflow_page` specification and remove the dedicated
  `EnglishWorkflowPage` layout. `WorkflowPageHost` now enumerates native
  `ThreeStateAccordionStack` columns and members through a runtime component
  registry. The resolved page declares 10 LEFT data/result members, 3 CENTER
  authoring members, and 6 RIGHT source/detail members; former center outputs
  such as Workflow Draft Preview and contract results now live in LEFT. Live
  browser verification confirmed every declared member, real filesystem text
  loading, model-backed authoring controls, and the editable Current Page
  Specification. Focused workflow-page/navigation validation: 80 passed;
  frontend production build and `git diff --check` passed on 2026-08-18.
- [x] Give each of the four workbench agents an independent self-managing
  mailbox watchdog rather than a central multi-agent loop. Each supervisor owns
  exactly one identity and cursor, checks its child every 10 seconds, runs a
  bounded poll every 5 seconds for 61 checks, restarts it on exit, and preserves
  deliveries in a per-agent durable spool. Heartbeats now consume only their
  own spool and acknowledge a fixed snapshot offset so concurrently arriving
  mail cannot be skipped. All four supervisors and poll children were verified
  live; focused watchdog validation: 5 passed and `git diff --check` passed on
  2026-08-18.
- [x] Softcode Visual Image Diff through the same filesystem-driven
  `WorkflowPageHost` and runtime component registry used by Generate Workflow,
  while retaining its richer visual composer, nested subaccordion UIX, model
  invocation, image sequence authoring, source inspectors, and Operation
  playground. The page specification now declares three LEFT data members,
  three CENTER authoring members, and three RIGHT source/detail members, and
  the shared host supports controlled member modes plus the page's resizable
  column dividers. Its original three-member RIGHT stack was subsequently
  expanded into the composed group Prompt plus all 11 pipeline Prompt editors.
  Focused workflow-page/navigation validation: 88 passed;
  frontend production build and `git diff --check` passed. Live browser
  verification confirmed all nine registered surfaces exactly once, two
  column dividers, both model/group composers, and zero unavailable-component
  fallbacks on 2026-08-18.
- [x] Expand the Visual Image Diff RIGHT source-details stack into the live
  composed group Prompt followed by all 11 filesystem-backed pipeline Prompt
  resources selectable from the CENTER composers. Each named Prompt member is
  a compact rich resource editor: contract metadata, synchronized MeTTa/JSON
  text editing, validity gating, and a per-resource Save Prompt action using
  the sibling-preserving Prompt update API. Live browser verification
  confirmed 13 right-column members in the declared order, 11 Prompt editors,
  independent expansion, and zero unavailable-component fallbacks. Focused
  validation: 79 passed; frontend production build and `git diff --check`
  passed on 2026-08-18.
- [x] Add a first-class Workflow Page Builder under WORKFLOWS. CURRENT PAGE
  SPECIFICATION accepts pasted `workflow_page` JSON; CLEAR removes the draft
  and generated preview while preserving the editor, and LOAD performs one
  best-effort construction pass. The loader normalizes left/center/right,
  renders every valid declaration through `WorkflowPageHost`, and inserts
  visible recovered-error accordion members for malformed columns or members
  instead of rejecting the entire page. It initializes from a real effective
  filesystem page rather than mock content. Live browser verification covered
  CLEAR, a recovered bad component beside a valid component, three-column
  rendering, and filesystem-page restoration. Focused validation: 92 passed;
  frontend production build and `git diff --check` passed on 2026-08-18.
- [x] Split Workflow Page Builder construction into explicit LOAD and INIT
  phases. LOAD now synchronizes CURRENT PAGE SPECIFICATION with the visible
  three-column declaration and recovered error members without activating
  component bindings; INIT then initializes every valid declared component.
  CLEAR resets both phases while preserving the specification editor, and a
  refreshed filesystem definition with the same page id is synchronized back
  into the builder rather than being ignored as stale. Generate Workflow and
  Visual Sequencing retain their validate/apply-to-filesystem then snapshot-
  refresh synchronization path. Focused validation: 102 passed; frontend
  production build and `git diff --check` passed. Live browser verification
  confirmed the filesystem definition begins in LOADED state with 20 declared
  members and INIT replaces every pending surface with its initialized binding
  preview on 2026-08-18.
- [x] Turn Visual Sequencing `RESOURCE OUTPUTS` into the datafield planner for
  the LEFT stack. `READ MIDDLE FLOW` derives the 23 current datafields from the
  11 real filesystem Prompt `produces` contracts and records which Prompts
  consume and produce each field. `ADD MISSING FIELD EDITORS` inserts one
  editable accordion member per absent field immediately after RESOURCE
  OUTPUTS, without duplicating members already declared by the page. The live
  generated layout is synchronized into CURRENT PAGE SPECIFICATION as an
  unsaved definition, so Validate and Apply can persist it. Live browser
  verification confirmed 23 editors from `source_images` through
  `workflow_report`, the correct left-stack order, and a synchronized/apply-
  enabled page specification. Full validation: 667 passed; frontend production
  build and `git diff --check` passed on 2026-08-18.
- [x] Recursively convert JSON embedded inside string values during JSON→MeTTa
  serialization, including JSON contracts surrounded by natural-language
  Prompt prose. The codec uses reversible text/structured-JSON parts so the
  MeTTa→JSON path reconstructs the original string semantics; nested embedded
  JSON is handled recursively while ordinary prose and scalar-looking strings
  remain strings. Python persistence and browser-side editor codecs implement
  the same contract. Visual Sequencing Prompt editors now also expose explicit
  Load, filesystem Reload, Clear, and validated Save Prompt actions. Live
  browser verification confirmed all four controls. Full validation: 669
  passed; frontend production build and `git diff --check` passed on
  2026-08-18.
- [x] Simplify Visual Sequencing group members around resource inheritance.
  Nested Prompt steps no longer repeat a model selector; they inherit the
  containing group's selected model, including single-step quick runs.
  Arrow/× controls on nested steps were replaced by drag ordering plus a
  keyboard-accessible position selector, explicit OVERRIDE and REMOVE
  actions, and Prompt-resource replacement by drag-and-drop. Collapsed Prompt
  strips in the RIGHT source-details stack are themselves drag sources:
  dropping one on a Prompt step replaces that occurrence, while dropping it
  on a group appends a new step. Live DOM verification found 11 draggable
  right-column Prompt strips, 11 nested drag/order controls, and zero nested
  model selectors. Focused validation: 18 passed; full validation: 669 passed;
  frontend production build and `git diff --check` passed on 2026-08-18.
- [x] Retire the duplicate flat Visual Diff composer and retain the nested
  subaccordion as the sole filesystem-declared authoring component. GRAPH is
  now a live alternative presentation of that exact `generationOrder`, not a
  mock: real HTML editors are embedded directly in its SVG graph nodes. GRAPH
  keeps the RIGHT source-details stack visible as its draggable filesystem
  Prompt palette, uses one unified graph canvas and one uninterrupted vertical
  call-sequence spine, and places
  insertion targets before, between, and after the calls. Dropping on a gap
  inserts a Prompt occurrence at that exact position; dropping on a call
  replaces it. Existing calls drag-reorder and also retain keyboard-accessible
  position selectors. Group model/visibility/order/run/copy/shuffle/clear/remove
  controls and datafield editors mutate the same `generationOrder` and
  `workflowData` used by COLUMNS. Column mode retains DOM-drawn field-to-Prompt
  lines; GRAPH uses the same contracts to draw its editable edges and nodes. The
  graph no longer renders a list of per-group graph cards: S1-S5 are subtle
  annotated bands along the single global call sequence. S1 is restored as the
  `IMAGE PAIR + COMMAND` stage and explicitly consumes editable `image_pair`
  and `transition_command` fields before source, normalization, and object
  extraction. Calls are globally numbered 1-11 while the underlying editable
  groups remain intact.
  Focused Visual Image Diff validation: 19 passed; frontend production build,
  `git diff --check`, screenshot review, and live GRAPH browser verification
  passed on 2026-08-18. Updated live DOM evidence: one graph canvas, one
  sequence spine, five annotation bands, zero legacy stack cards, 11 globally
  numbered Prompt editors, both S1 input editors, and the visible RIGHT Prompt
  resource column.
- [x] Make the unified GRAPH call sequence reorderable across transaction-group
  boundaries. Every call node is a drag source; every before/between/after gap
  accepts either an existing occurrence or a filesystem Prompt dragged from
  the RIGHT column. Moving an occurrence into another segment transfers the
  real nested step to that target group and corrects same-group indices after
  removal. Dropping a RIGHT Prompt on a gap inserts it; dropping it on a call
  replaces that occurrence. Focused Visual Image Diff validation: 19 passed;
  frontend production build passed on 2026-08-18.
- [x] Replace the hand-rendered GRAPH SVG with `@xyflow/react` and
  `@dagrejs/dagre`. Prompt occurrences are single rounded custom React Flow
  nodes in one Dagre-ranked top-to-bottom sequence; data nodes, group-control
  nodes, and insertion targets share the same pannable/zoomable canvas.
  Smooth-step directed edges, a minimap, viewport controls, foreground editor
  nodes, and stack-aware collision spacing reduce occlusion. Inputs use left
  handles and outputs use bottom handles. The graph still mutates the same
  `generationOrder`/`workflowData`, supports cross-group call moves, and accepts
  filesystem Prompts from the RIGHT column at every insertion target. Focused
  Visual Image Diff validation: 19 passed; frontend production build passed on
  2026-08-18.
- [x] Add graph-wide mouseover discoverability for Visual Sequencing GRAPH mode.
  Group, Prompt, datafield, action, and insertion-gap controls now expose
  explicit hover tooltips (`title`) plus stronger hover/focus highlights on
  graph nodes and insertion targets, so every hovered graph element identifies
  itself and its action. Live verification on the default page URL
  `http://127.0.0.1:5173/?workspace=arc3_random_player&view=visualImageDiff`
  confirmed one React Flow canvas, 11 Prompt calls, visible RIGHT Prompt
  column, S1 `image_pair` and `transition_command` datafield editors, and
  nonzero tooltip counts across group, prompt, gap, and toolbar controls
  (30/77/16/6). Graph group controls also retain explicit REMOVE alongside run,
  copy, shuffle, and clear.
- [x] Make each GRAPH left-side datafield map to a right-side helper
  displayer/editor/uploader node. Each helper stays compact by default with a
  value preview and drag handle, and expands into the full editor plus file
  uploader only when selected. The helper nodes are filesystem-backed through
  the same `workflowData` mutation path as COLUMNS. Live default-port check at
  `http://127.0.0.1:5173/?workspace=arc3_random_player&view=visualImageDiff`
  confirmed 36 helper drag handles, one expanded selected editor, 35 compact
  preview helpers, and visible file upload control.
- [x] Keep moved GRAPH helper nodes as the same original node instance.
  Dragging a right-side helper now persists that helper node's position by its
  real React Flow node ID, so moving `image_pair` (or any datafield helper)
  moves the original instead of appearing as a fresh reset node.
- [x] Keep helper-node selection in-place instead of showing a separate-looking
  expanded card. Selecting a helper now slightly enlarges that same original
  node and reveals editor/upload controls inline. Live default-port verification
  confirmed one selected helper with inline editor (`selectedNodes:1`,
  `editorVisible:1`) and zero legacy separate expanded cards
  (`legacyExpandedNodes:0`).
- [x] Verify left-side datafield clicks do not trigger far-right helper changes.
  Live UI check at `http://127.0.0.1:5173/?workspace=arc3_random_player&view=visualImageDiff`
  (GRAPH mode) confirmed: initial selected helper count `0`, after clicking a
  left datafield editor it remains `0`, and only clicking a right helper sets it
  to selected with inline editor (`1`).
- [x] Make all GRAPH canvas item types draggable and persistent in-place
  (groups, Prompt nodes, left data nodes, insertion gaps, and right data helper
  nodes). Live drag verification on the default URL confirmed movement deltas
  for every node type (`~30px` each) rather than snapping back.
- [x] Remove left/right datafield duplication in GRAPH mode. Data helpers are
  now consolidated into the left data nodes only, with inline edit plus upload
  (`UP`) on that same node. Live default-port verification confirmed
  `dataDetailNodes:0` with matching left data/upload counts (`36/36`).
- [x] Move workspace resource persistence into the shared Resource Source
  editor instead of keeping a Models-only Save destination selector. The
  reusable control supplies Save, Save As, Reload, and Load From; accepts the
  active workspace plus a workspace-relative resource path; remembers the
  original workspace for later reloads; and orders destinations as current,
  inherited hierarchy, separator, other libraries, then other workspaces.
  Models now uses this common control for backends, models, presets, and
  systems. Frontend production build passed on 2026-08-24.
- [x] Derive each Backend's rich editor as an aggregate instead of presenting
  one undifferentiated source document. Backend tabs now expose File (shared
  workspace file lifecycle and JSON/MeTTa/tree source), Resource (structured
  Configuration plus resolved/inherited JSON), Backend Actions (discovery,
  enablement, defaults, capabilities, and example actions), and the Universal
  Execution Runner with backend inspect/readiness/validation Operations.
  Frontend production build passed on 2026-08-24.
- [x] Make the focused Models editor resource URL-addressable with `edit=<id>`.
  Selecting the EMULLM backend now synchronizes `edit=enullm-8801`; loading a
  Models URL with that parameter reopens the same backend. Navigation away
  clears stale `edit` state while the legacy `resource` link remains accepted.
- [x] Make backend source editing conspicuous from the derived Resource view.
  The document toolbar now exposes a prominent Edit button that reveals File
  mode, and the resolved/inherited JSON panel has a direct Edit JSON / MeTTa
  action rather than requiring users to discover the small File tab.
- [x] Make the Backend aggregate visibly and semantically tabbed. The editor
  now has a labeled EDITORS tab strip, connected tab/panel borders, a strong
  active-tab treatment, hover affordances, and tablist/tab ARIA semantics.
- [x] Distinguish every shared Resource Source file action by storage channel.
  Workspace resources use Save To Workspace, Save To Other Workspace, Reload
  From Origin, and Load From Workspace. Native browser file handles use Load,
  Save, Save As, and Reload Local File. Portable client transfer uses Upload
  and Download without falsely claiming a persistent reloadable path.
- [x] Expose Backend enablement directly in the derived Resource tab. The tab
  shows whether state is declared locally or resolved and provides an explicit
  Enable Backend / Disable Backend action without requiring Backend Actions.
- [x] Label split-comparison document tabs by pane in the upper tab menu. When
  split view is active, the primary focused document is marked LEFT and the
  comparison document is marked RIGHT with distinct visual badges.
- [x] Give the Backend aggregate two display modes. Tabs shows one derived
  editor at a time; Stack aligns File, Resource, Backend Actions, and Universal
  Execution Runner vertically in one scrolling document. Selecting a named
  editor while stacked returns to Tabs focused on that editor.
## User/UI preferences

- [x] Relink the active Workflow Canvas in the WORKFLOWS menu and make
  workspace opening deterministic. Explicit `view=` wins; otherwise a local
  workspace preference or last-page history wins, followed by inherited
  workspace preferences and the configurable system fallback (Overview by
  default). First visits therefore resolve through inheritance/system rather
  than falling into the legacy canvas route, while invalid saved page IDs open
  Settings for repair. Canvas URLs now round-trip as Canvas instead of
  reopening Current Workflow.
- [x] Add a browser-persisted User/UI Settings preference for placing shared Resource Source save/load controls above or below editor text areas; apply changes live without modifying workspace resources.
- [x] Add a shared per-page UI tools contract: show currently available UI configuration, open a context-filled Codex UI conversation, and retain page URL, scroll position, and tool state per workspace/page for safe session reloads.
- [x] Replace broad Vite/UI restart behavior with an allowlisted, debounced surgical reloader that calls `onUIRestart`, flushes all visited-page session records, and permits one browser reload per restart token; manual restart no longer touches `vite.config.ts`.
- [x] Replace the selected Operations document control with an embedded
  `UniversalArtifactEditor` Super Control. The rich Abstract Operation or
  Operation Implementation surface is now the first Super Control tab, and
  `ResourceSourceEditor` is mounted only by the shared Resource tab instead of
  remaining duplicated in `OperationLibraryEditor`. Operations supplies typed
  resource data and callbacks; Super Control owns renderer selection and its
  CSS. Operations contributes no other tabs: the existing File, Markdown,
  Resource & Inheritance, and Universal Execution Runner editors remain owned by
  Super Control, while library/model/policy/plugin pages are not injected.
  Validation on
  2026-08-26: 9 focused UI contract tests passed, the frontend production build
  passed, and live browser checks confirmed zero source editors on the Abstract
  Operation tab and exactly one on the Resource tab.
- [x] Replace the selected Topics document control with an embedded standard
  Super Control while keeping the taxonomy heading and tree outside. Topics
  contributes no special editor tab; it supplies only its filesystem resource
  text, metadata, Save/Delete actions, and an initial Resource selection. File,
  Markdown, Resource & Inheritance, and Universal Execution Runner remain the
  only tabs.
  Resource & Inheritance combines editable resource controls with the resolved
  read-only view. The latter supports save/export and reload-from-origin, never
  loading a different resource, and links to its real parent for editing.
- [x] Make embedded Super Control import and own the Models-style toolbar,
  editor-tab, source-border, scrollbar, and responsive CSS so hosts do not need
  to load component styling.
- [ ] Implement the documented Super Control display contract: Tabs, Stacked,
  Single, SplitV, and SplitH, with independently selected panes where required.
  ALL must expose every registered content-backed tab; CTX must use the
  content-backed subset of the selector API result. Registered controls without
  real renderers stay hidden rather than producing empty placeholder tabs.
  Expose ALL and CTX as persistent segmented buttons in the banner beside the
  DISPLAY selector, not as editor tabs or a pull-down.
  Mode changes must preserve dirty resource state, and every non-Tabs
  mode must retain a visible action that restores Tabs. Tabs mode must expose a
  pull-down selector for switching directly to every other display mode.
  Single must initially show the context-selected default tab, normally File
  through `ResourceSourceEditor`. Put the switcher in the Super Control header
  action slot currently occupied by the one-off Split view button; do not add a
  separate control row or absorb host-level document comparison.
- [ ] Make parsed JSON identity displays consistently include the stable `id`
  plus available `kind`, `type`, `subkind`, or equivalent role metadata. A
  human label may supplement but must not hide resource identity, and parse
  failures must be explicit. For one JSON object, derive the Super Control
  header as `KIND - Label (id)`, omit `(id)` when it equals the label, and use
  `KIND - id` when no separate label exists.
- [ ] Make `ResourceSourceEditor` choose a CodeMirror syntax mode from the source
  format, resource metadata, and filename extension. Normal source views remain
  editable; explicitly resolved/inherited views remain read-only. MeTTa must use
  a Lisp- or Clojure-compatible lexer when no dedicated MeTTa lexer is present.
  Content detection takes precedence over extension: JSON-parsable documents
  default to the MeTTa representation, while detected Markdown uses the
  CodeMirror Markdown lexer even without a Markdown filename suffix. Run every
  opened source through file-type detection using content, path/extension,
  shebang markers, and resource metadata, then load the best CodeMirror language
  extension; use plain text only when no language is confidently identified.
- [ ] Base the JSON Tree presentation on CodeMirror's parsed JSON structure and
  folding state. Give every object/array node a clickable expand/collapse
  disclosure and add persistent overlaid Expand/Collapse controls for the whole
  tree and selected branch. Tree, JSON, and MeTTa views must remain synchronized
  and folding must never mutate source.
