# Page Generations — the page version-management system

Every workbench page can carry its full version history. A **page family**
registers each **generation** it has shipped (v1, v2, …); a stepper strip at
the top of the page lets the user walk through the history (`?gen=N` pins a
generation in the URL). The Video Import page is the first family on the
system (`workbench/frontend/src/components/VideoImportFamily.tsx`).

## Global policies

Defined in `workbench/frontend/src/lib/pageGenerations.ts`
(`GLOBAL_GENERATION_POLICIES`) and displayed in every page's ⓘ provenance
panel:

1. **Never take away features.** Every new generation must be a superset of
   the one before it — the union of useful features, never the lowest common
   denominator. (This is the workbench-wide baseline rule from `AGENTS.md`
   applied to page versions.)
2. **Every shipped generation stays runnable and steppable.** Upgrades add a
   generation; they never delete one.
3. **New generations are built from the written build prompt.** Each page's
   help document carries a "prompt that would build this" appendix
   (e.g. `workbench/docs/VIDEO_IMPORT.md`). To make v(N+1): update the prompt
   first so it describes the target, then build from it. Building with the
   whole design known up front beats growing it organically.
4. **Every generation records provenance** — component path, build prompt,
   builder, date, and a `nextVersionHint` — so a future codex knows exactly
   where and how to construct the next version.
5. **Consult verdicts before studying a generation** (see below).
6. **Real data only.** Generations share the same backend contracts; no
   generation may introduce mock data.

## Verdicts — red herrings are recorded, not studied

Every generation carries a `verdict` telling the workbench UI and future
codexes how to treat it:

| verdict | meaning | for the next version |
|---|---|---|
| `canonical` | the current best (★ in the stepper) | study and build on it |
| `superseded` | fine work, replaced by a newer canonical | reference freely |
| `experimental` | promising but unproven | evaluate before adopting ideas |
| `red-herring` | a recorded dead end / bad idea (⚠ in the stepper) | **do NOT study its design** — read its `lessons` field only |

Red herrings stay runnable (policy 2) because the history is part of the
record, but their role is to warn: the `lessons` field is required for them
and is the only thing a future builder should take from them. The ⓘ
provenance panel prints an explicit warning when the active generation is a
red herring.

## How to ship the next generation of any page

1. Read the family registration (e.g. `VideoImportFamily.tsx`): the active
   canonical generation's provenance names its component and build prompt;
   its `nextVersionHint` names where v(N+1) goes.
2. Check every generation's verdict; skip red herrings except for lessons.
3. Update the page's build prompt (help doc appendix) to describe the target.
4. Build the new component from that prompt. Never remove features — verify
   against the previous canonical generation in the running app.
5. Register the new generation with a full provenance block and a verdict
   (usually `canonical`, demoting the previous one to `superseded`).
6. Validate: frontend build, live page walk-through of both the new and the
   previous generation via the stepper.

## How a page adopts the system

```tsx
// MyPageFamily.tsx
const family: PageFamily = {
  family: "myPage",
  title: "MY PAGE",
  policies: ["family-specific rules…"],
  generations: [{ generation: 1, label: "organic", verdict: "canonical",
    note: "…", provenance: { componentPath: "…", builtFrom: "…" },
    component: MyPage }],
};
export const MyPageFamily = ({ workspaceId }: { workspaceId: string }) =>
  <GenerationHost family={family} workspaceId={workspaceId} />;
```

Point the view registration at the family component instead of the bare page.


## Graduation (baseline reset)

A family may **graduate**: when a rebuilt generation proves itself as the page
the user actually lives in, it can become the new **v1 baseline**, resetting
the family epoch. Rules:

1. Graduation is user-initiated ("this is ready to become v1"), never automatic.
2. The graduating component keeps its file name; provenance records the origin
   (e.g. "file name kept from its pre-graduation v2 origin").
3. Pre-graduation generations are **archived, not deleted**: their component
   files stay in the repo, runnable by re-registering them in the family. The
   baseline's `lessons` must name the archived ancestor and its path.
4. After graduation the family numbers from 1 again; the next rebuild is v2,
   constructed from the updated build prompt as usual.

First graduation: Video Import (2026-08-29) ? the from-prompt rebuild
(`VideoImportPage2.tsx`) became v1 "organic"; the original organic build
(`VideoImportPage.tsx`) is archived.
