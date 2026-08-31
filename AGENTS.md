

\# MeTTaSymbolicLearnerWorkbench — Codex Instructions

[Back to repository README](README.md)


\## Codex TODO ownership and recovery



The durable Codex recovery ledger is [CODEX_TODO.md](CODEX_TODO.md). Codex
owns keeping that file current at meaningful implementation, validation, and
handoff checkpoints. Contributors may add or correct tasks, but should not use
`AGENTS.md` as a transient progress log. After context loss, restart, or
handoff, read `AGENTS.md` first and then `CODEX_TODO.md` before changing code.



\## Project Purpose



This repository implements the MeTTaSymbolicLearnerWorkbench: a

filesystem-backed symbolic artifact workbench.



The workbench edits semantic specifications and interchangeable variants:



\- Goals and interpretations

\- Planning strategies and executable workflows

\- Workflows

\- Operations and implementations

\- Datatypes and representations

\- Source code: prompts, Prolog, MeTTa, and Python bindings

\- Models, model presets, and backends

\- AtomSpaces and knowledge representations

\- Runtime runs, executions, events, states, and logs

\- Benchmark and model-runtime policies



\## Active Application



Before changing UI code, determine the active entrypoint from:



\- workbench/frontend/src/App.tsx



Do not assume that an older polished page or mock page is active.



Backend entrypoint:



\- workbench/server/app.py



Filesystem workspaces:



\- workbench/workspaces/



\## Non-Negotiable UI Baseline



The current active application and its existing rich editors are the minimum

feature baseline.



Do not replace a rich editor with a simpler generic editor.



The global artifact editor must preserve the union of useful features from

all prior editors, never the lowest common denominator.



Every hierarchical artifact editor must support:



1\. Specification parent in the left hierarchy

2\. Concrete alternatives beneath it

3\. Preferred/default alternative selector

4\. Persistent open-document tabs

5\. Dirty markers

6\. Closeable tabs

7\. Split comparison

8\. Rich artifact-specific editor panels

9\. Raw JSON editing

10\. Filesystem save

11\. Shared inheritance and workspace override

12\. Documentation on the right

13\. Tests, history, benchmarks, diff, and logs where available

14\. A playground/run surface where the artifact is executable



\## No Mocks



All displayed workspaces, operations, implementations, models, prompts,

datatypes, representations, goals, plans, runs, events, states, and logs

must come from real filesystem or backend resources.



A visual mock may be used only as a design reference.



Do not leave hard-coded mock arrays in the active application.



\## Navigation Contract



The new left navigation is:



WORKSPACE

\- Overview

\- Goals

\- Planning

\- Workflows


CAPABILITIES

\- Operations

\- Source Code (Prompts, Prolog, MeTTa, and Python)

\- Systems

\- Models (backends, models, and presets)

\- Datatypes

\- Policies


KNOWLEDGE

\- Data

\- AtomSpaces

\- Artifacts



RUNTIME

\- Goal Runs

\- Executions

\- Events

\- States

\- Logs



SYSTEM

\- Model Policy

\- Benchmarks

\- Processes

\- Settings



Reuse existing editors rather than duplicating them:



\- Operations -> existing rich OperationLibraryEditor

\- Datatypes -> existing three-level DataCatalogPanel editor

\- Source Code -> prompt editor plus language-filtered Operation implementation editors

\- Models -> existing backend/model/model-preset editor

\- Workflows -> existing workflow canvas and editor

\- Workflow Runs / Events / Logs -> existing engine runtime data where possible

\- Settings -> existing workspace setup functionality



\## Filesystem Conventions



Resource relationships use three independent bidirectional map pairs:

- `implements` / `implementedBy` represents implementation, classification,
  datatype conformance, or abstract-to-concrete relationships. These entries
  are policy-free.
- `inheritsFrom` / `inheritedBy` controls ordinary property inheritance. Each
  child-side entry declares `borrow`/`exclude`; each parent-side entry declares
  `lend`/`withhold`. Effective inheritance is the intersection of both
  permissions, minus exclusions, followed by local overrides.
- `dependsOn` / `dependedOnBy` controls effective enabled state and optional
  availability propagation.

Never infer one graph from another at runtime. `preferredImplementation`
selects one key from `implementedBy` as the default child; it is selection
metadata, not inheritance or availability. Do not persist generic `parents`,
`children`, or `inherits` fields for these relationships.

Do not equate implementation depth with concreteness. Abstractness means how much
implementation is still missing for the resource to perform its job. A
implementation may remain abstract and have deeper implementations; only a fully
resolved resource with the required behavior and execution bindings is concrete.
The UI derives abstract/partial/concrete/runnable status from the current draft, resolved
inheritance, and family-specific requirements. Do not add a persisted
`abstractness` or `concrete` source-of-truth flag.
This derived status is reversible: removing, disabling, or losing an
`implements` parent can make a formerly runnable resource abstract again.
Recompute affected descendants whenever the inheritance graph or a workspace
override changes, and show the missing parent or obligation.



Examples:



\- operation / child operation

\- semantic\_datatype / representation\_datatype / concrete\_datatype

\- prompt / child prompt

\- goal / child goal

\- planning\_strategy / child planning\_strategy

\- atomspace / child atomspace

\- model / child model / backend



Keep each family in its plural directory (for example `design/operations/` or `design/goals/`). Files may hold multiple top-level MeTTa resources, but editors must replace only the selected resource and preserve siblings.

Workspace resources use a lifecycle-first layout:

\- `design/<plural-kind>/` for editable specifications and alternatives

\- `runtime/<plural-kind>/` for generated runs, execs, events, states, resolved contexts, and logs

\- `knowledge/data/` and `knowledge/artifacts/` for workspace-held input values and persisted outputs

\- `policies/` may remain a mixed policy, observation, job, event, and benchmark family

\- `docs/` contains Markdown and is not a resource-kind directory

Shared normally has no runtime records. Maintain compatibility with legacy
root-level family directories when reading older workspaces, but all new saves
must use the lifecycle-first layout.



\## Repository Structure and Working Conventions



Core Python modules live in `python/`, including the `object_memory/` and

`worldworkbench/` packages. The active browser workbench is split between

`workbench/server/` and `workbench/frontend/`. Keep Prolog rules and native

tests in `prolog/`, reusable configuration in `config/`, command-line helpers

in `scripts/`, and Python tests in `tests/`. ARC agent code belongs in

`agent/`; `notebooks/` contains Kaggle notebook inputs and metadata. Consult

`README.md`, `workbench/README.md`, and `README_WINDOWS.md` before changing

setup or runtime behavior.



Development commands:



\- `python -m pip install -e ".[test,debugger]"` installs Python 3.12+

development dependencies.

\- `python -m pytest -q` runs the Python suite used by CI.

\- `make verify-local` smoke-tests the ARC agent; `make play-local GAME=ls20

STEPS=200` runs a targeted session. These Make targets assume a Unix-like

shell; use `README_WINDOWS.md` on Windows.

\- From `workbench/frontend/`, `npm install && npm run dev` starts Vite with hot-reloading (preferred for interactive use) and

`npm run build` type-checks and builds the frontend (used for validation/production checks, not for serving the interactive app). Node.js 22+ is required.

\- `swipl -q -s prolog/run_tests.pl` runs the SWI-Prolog test entrypoint.



Use four spaces in Python and two spaces in TypeScript and JSON. Use

`snake_case` for Python functions and modules, `PascalCase` for classes and

React components, `camelCase` for TypeScript helpers and hooks, and uppercase

names for constants. Prefer type hints, focused functions, `pathlib`, and

platform-neutral behavior. Preserve resource suffixes such as `*.operation.metta`,

`*.prompt.metta`, `*.semantic_datatype.metta`, `*.representation_datatype.metta`,
and `*.concrete_datatype.metta`. No repository-wide formatter is

configured; match nearby code and avoid unrelated reformatting.



Pytest discovers `tests/test_*.py`; name tests `test_<behavior>` and add a

regression test for every bug fix. Keep tests deterministic and mock network,

LLM, and external-service boundaries. Run focused tests while developing, then

the full suite before completion. Add Prolog tests beside related `.pl`

modules when symbolic logic changes.



\## Git Safety



\- Work on a named branch or isolated Codex worktree.

\- Do not push directly to main during development.

\- Do not run broad `git checkout <old-commit> .`.

\- Do not reset, clean, normalize, rename, or delete unrelated files.

\- Inspect `git status` and `git diff --stat` before and after changes.

\- Keep each commit coherent.

\- Open a pull request after validation.



\## Required Validation



Run before reporting completion:



```bat

git diff --check



.\\.venv\\Scripts\\python.exe -m pytest -q



cd workbench\\frontend

npm run build

cd ..\\..



run\_workbench.bat

For UI changes:

- open the relevant workspace;

- verify every new menu item;

- verify left hierarchy and alternatives;

- verify selectors mutate the correct document;

- verify save and reload;

- verify horizontal and vertical scrolling;

- capture screenshots for visual comparison.

## Definition of Done

A task is not complete merely because TypeScript compiles.

It is complete only when:

- the active application uses the change;

- data comes from the real backend/filesystem;

- old rich functionality has not disappeared;

- tests pass;

- the frontend builds;

- the page works after restart;

- the diff contains no unrelated cleanup.




This file is what stops Codex from repeatedly replacing the feature-rich editor with a simpler version.



\## 4. Store this conversation’s decisions inside the repository



Codex will not automatically inherit the full architectural history from this chat. Important decisions need to become repository files.



I would add:



```text

workbench/docs/design/

├── WORKBENCH\_NAVIGATION\_V2.md

├── UNIVERSAL\_ARTIFACT\_EDITOR.md

├── GOALS\_AND\_PLANS\_ARCHITECTURE.md

└── FILESYSTEM\_RESOURCE\_MODEL.md



workbench/docs/todo/

├── MODEL\_RUNTIME\_USAGE\_AND\_BENCHMARKING\_POLICIES.md

└── assets/

&#x20;   └── model\_runtime\_policy\_mockup.png

The full TODO text you just wrote should be saved verbatim as:


workbench/docs/todo/MODEL\_RUNTIME\_USAGE\_AND\_BENCHMARKING\_POLICIES.md

Save the latest model-policy mockup as:


workbench/docs/todo/assets/model\_runtime\_policy\_mockup.png

The model-policy screenshot becomes an explicit visual design reference rather than a temporary image trapped in chat history. The current active Operations editor is the acceptance baseline; verify it directly in the running application.

## 5. Map the new navigation to what already exists

The first Codex change should **not** implement every page. It should only establish the new shell and reuse current editors.

| New menu | Existing functionality |

|---|---|

| Goals | New hierarchical Goal editor |

| Planning | Hierarchical Planning Strategy editor |

| Workflows | Existing workflow canvas/editor |

| Operations | Existing rich Operations editor |

| Datatypes | Existing three-level semantic/representation/concrete editor |

| Source Code | Prompt editor plus Prolog, MeTTa, and Python implementation-source editors |

| Systems | System/backend editor filtered to runtimes, shells, MCP servers, and plugins |

| Models | Existing Models/backends/profiles editor |

| Goal Runs | New goal-pursuit runtime history |

| Executions | Operation and workflow execution records, including playground runs |

| Events | Existing durable events/evidence |

| States | Persisted workflow/world state snapshots |

| Logs | Existing workflow/operation logs |

| Model Policy | New page from your TODO/mockup |

| Benchmarks | Benchmark definitions and results |

| Settings | Existing Setup page |

This means **Operations is the canonical executable-artifact name**, and **Types/Data becomes Datatypes**, while the underlying editors remain the same.

## 6. Give Codex small, ordered tasks

Do not start with “implement the entire workbench.” That encourages broad rewrites.

### Codex Task 1 — Repository inventory only

Paste this first:


Read AGENTS.md and all files under workbench/docs/design and

workbench/docs/todo.



Do not modify implementation code yet.



Inspect the active React entrypoint, active workbench page, current navigation,

OperationLibraryEditor, DataCatalogPanel, PromptLibraryEditor, LlmModelsEditor,

workflow editor, runtime engine routes, workspace snapshot API, and filesystem

resource loaders.



Create:



workbench/docs/design/CODEX\_CURRENT\_IMPLEMENTATION\_INVENTORY.md



Document:



1\. Which page App.tsx actually launches

2\. Which current component should back each new navigation item

3\. Which pages are real versus mock or obsolete

4\. Which backend routes already exist

5\. Which filesystem resource kinds already exist

6\. Which features exist only in defunct pages

7\. Exact files that must change for navigation V2

8\. A regression checklist protecting the current active rich Operations editor



Do not remove or simplify any editor.

Run no normalization or broad rename.

Stop after producing the inventory document.

Review that document before allowing code changes.

### Codex Task 2 — Navigation shell only


Implement WORKBENCH\_NAVIGATION\_V2.md.



Change only the active application shell and navigation routing.



Use these groups and labels:



WORKSPACE

Goals

Planning

Workflows

CAPABILITIES

Operations

Source Code

Systems

Models

Datatypes

Policies

KNOWLEDGE

Data

AtomSpaces

Artifacts



RUNTIME

Goal Runs

Executions

Events

States

Logs



SYSTEM

Model Policy

Benchmarks

Settings



Reuse existing editor components:



Operations -> OperationLibraryEditor

Datatypes -> DataCatalogPanel

Source Code -> PromptLibraryEditor plus language-filtered OperationLibraryEditor views

Models -> LlmModelsEditor

Workflows -> existing workflow editor/canvas

Settings -> existing Setup page



For not-yet-implemented pages, use a filesystem-backed TODO/resource view,

not hard-coded fake data.



Do not change the internals of the rich Operations editor during this Codex task.



Add regression tests for route labels and component mapping.

Run the frontend build and relevant tests.

### Codex Task 3 — Preserve the model-policy page as a TODO


Add the supplied Model Runtime Usage and Benchmarking Policies specification

and mockup to workbench/docs/todo.



Add a Model Policy navigation page that reads and displays the TODO document

from the filesystem.



Do not implement fake model-policy data yet.



The page must clearly say that implementation is pending and link its sections

to the TODO document.

### Codex Task 4 — Backend model-policy contract

Have Codex implement only:


policy files

vendor files

model files

health observations

effective eligibility calculation

ping job/event records

benchmark policy files

API routes

tests

No major frontend work in that branch.

### Codex Task 5 — Model-policy frontend

Then implement the mockup against the real API:


vendor registry

dynamic model grid

frozen columns

horizontal property scrolling

composable filters

concurrent ping controls

prompt profiles

benchmark matrix

performance history

testing rules

filesystem load/save

## 7. Use parallel Codex agents carefully

Codex supports multiple concurrent agents and isolated worktrees, which is useful here.

A practical split is:


Agent A

Navigation shell and route mapping



Agent B

Model-policy backend schemas, persistence, and API



Agent C

Model-policy React page



Agent D

Regression tests and visual acceptance checks

But Agent C should not begin until Agent B has committed the API contract. Otherwise the frontend will invent another temporary schema.

## 8. Use pull requests instead of direct-to-main commits

For the first Codex phase:


codex/navigation-v2

codex/model-policy-backend

codex/model-policy-ui

codex/model-policy-tests

Merge order:


navigation-v2

    ↓

model-policy-backend

    ↓

model-policy-ui

    ↓

model-policy-tests / cleanup
