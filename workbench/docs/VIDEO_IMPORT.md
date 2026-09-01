# Video Import — Help

The Video Import page (KNOWLEDGE → Video Import) is the full loop for turning
a video you have the rights to into a playable ARC3 game recording: import →
timeline editing → frame extraction → a **preview system** for building
filter chains → entity extraction from input images → materialize.

Everything runs in the workbench itself (Python/PIL/scikit-image skills,
LUTs, yt-dlp) — a model only enters where explicitly chosen (MEMBERS, TURTLE).

Opening Video Import temporarily minimizes the App Menu, Resource Browser, and
Documentation rails to 36px so the pipeline owns the center width. Their normal
controls can restore them, and leaving Video Import restores the prior widths.
UI Debug, Generations, and UI Config start hidden on this page and remain
available from their normal topbar controls.
Hover any image and hold **Alt** to show an unclipped magnifier at exactly five
times its displayed width and five times its displayed height. Releasing Alt,
leaving the image, or blurring the window closes it immediately.

---

## 1. Import (intake row)

- **Catalog combo** — curated download candidates (`download_catalog.json`),
  each remembering what has been downloaded and extracted from it. `☆ Add to
  catalog` saves the current URL.
- **Importables combo** — loose files dropped by hand into
  `data/VideoImports/importables/`; picking one imports it.
- **URL / path box + Download / Import** — URLs download via yt-dlp, paths
  import a movie file from disk. You are responsible for having the rights
  to what you name here.
- **Quality/tool combo** — yt-dlp ceiling (`480p lo-fi`, `720p`, `1080p`,
  `best`) or `🛠 python direct fetch` for a direct `.mp4` URL.
- **⇪ Upload video…** — send a file from this computer straight in.

Imported videos appear in the list with duration, size, frames-so-far, scene
marks, and measured extraction pace.

## 2. Player and timeline

- **Marker rail** — click to seek, drag to make a selection, `◈ Mark` adds a
  scene marker at the playhead (click a marker to remove it).
- **✨ Detect scenes** — scan the video and mark every scene change
  (numpy frame-diff, no model).
- **Scene lane** — click a scene span to select it whole.
- **Segment lane + ✂ Split at cursor** — split into parts, click parts to
  keep/delete, `⟿ Trim video` re-encodes only the kept parts into a new
  video; `⤢ Selection → new video` extracts the highlighted range.
- **⤵ Frame at cursor** — grab the single frame under the playhead into the
  input images.

## 3. Extraction (top of the stack)

The EXTRACT row holds the **extract-frames-from-video criteria** — the very
top of every chain run:

- mode `every N seconds` or `per scene` (N images right after each change,
  with offset) · start/end time window · start/end scene-number window ·
  skip-scenes stride · max frames · a grounded frame/time estimate.
- Scene mode can extract short spans and sparse scenes independently. **Skip
  N scenes** advances by `N + 1`; for example, start scene 2 with skip 1
  extracts scenes 2, 4, 6, and so on. Each output frame retains its source
  scene number.
- First use defaults to scene mode, start scene 2, skip 1, one image per scene,
  and no end scene. The saved workspace page state overrides these defaults.
- **Extract frames** runs it as an interruptible job.
- The GROUP row (appears with more than one frame) applies **group
  selectors**: `N most unique` (farthest-point sampling), `N evenly spread`,
  `N random`, `N most like / most unlike their original` (needs OUTPUT).
  `✂ Keep only selected` drops everything else; selector choices carry their
  own vote history.

## 4. Input images

Plain image tiles: `#index · time · source (extract / ⤵ cursor grab)`.

- **Click an image** to make it the operator-picked input item (blue
  outline) — it feeds Preview / ▦ / permutations.
- **LLM input checkbox** is a separate explicit multi-selection. Only checked
  images can enter the recursive Describer → Planner → Outliner → Extractor workflow;
  picked images, keepers, group selectors, and implicit first/last fallbacks do
  not populate it. Selection controls remain enabled while model stages run, so
  choosing one image never locks out additional choices. Select all/none remain
  explicit user actions.
- **Clear extracted frames** removes all frame tiles, picked/group state, and
  recursive input selections from the page. It does not delete image files or
  already-derived object history.
- Hovering any image shows two independent context blocks: the parent scene's
  object description that caused the image to be extracted, and the image's
  own latest exact Describer output. A new cutout therefore retains useful
  parent context before its own Describer pass and gains the second block
  afterward; one never overwrites the other.
- Hold **Alt** for a fit-to-half-pane image magnifier plus a side
  context panel. When that image has been described, the panel shows its saved
  description and every named object with its own description and status.
  The image and context panel occupy separate non-overlapping columns, with the
  text sidecar layered above the image. Images without saved analysis say so
  rather than inventing metadata.
  The rollover gives the image the entire opposite half-page pane (half width
  and half height) and enlarges it aspect-correctly with `contain`, including
  more than 5× for very small tiles. The context owns the other half. Their combined side-by-side
  rectangle is clamped onscreen, so the magnified image pushes the context
  aside instead of covering it.
  Alt-click pins the complete image/context pair. It remains after Alt is
  released or the pointer leaves and closes only through its explicit Close
  button.
- Tile overlay: **▲ keeper** (adds to the group selection, green outline) ·
  **▼ drop** (removes the image from the candidates; files stay on disk).
- The **first group selection is the selection criteria that decides which
  images feed the chain** in preview mode (preview-only — the full run
  always takes every extracted frame).

## 5. PREPASS — the preview system for building filter chains

There is **no default filter**: start with the gallery.

- **▦ Apply all filters** — the selected image goes through every filter in
  scope → the GALLERY (one tile per filter). Scope combo: `run included` /
  `run excluded` / `run all` — exclusions never lock you out.
- **Gallery tiles** — click to pick that filter · `▲ / ▼` historical votes
  (they order the combo and the gallery) · `🚫 disable` (an *extreme
  downvote*, −10, and exclusion everywhere; `↩ enable` reverses the
  exclusion but the history remains).
- **⚙ Permutations** — the picked filter rendered across parameter
  permutations (explicit `paramGrid`, built-in grids, choice lists, or a
  numeric half/default/double fallback); click a tile to adopt those exact
  settings.
- **Filter registry (246+)** — built-ins (cartoon, pixelate, downscale),
  published presets (`⭑ Publish` → `filter_catalog.json`), `.cube` LUTs in
  `data/VideoImports/luts/`, and Python **skills** in
  `data/VideoImports/filter_skills/` (pilgram's 26 styles, ~70 Pillow
  effects, ~50 scikit-image transforms, ~85 matplotlib colormap gradient
  maps…). Drop a `.py` exporting `SKILL` + `apply(image, params)` and it
  appears — the workbench calls it directly, no LLM.
- **🚫 Find retinters** — an analytical scan that flags filters that are just
  proportional mass retinters (pointwise color remaps that keep structure)
  and excludes them from the active set.

### Chains

`＋ Chain` appends steps that **default to `<none>`** (no-ops). Each step has
its own combo (filters, or **group selectors** — also no-ops until N is set)
and its own parameters. Step `0.` always shows the extraction criteria and
the preview-candidate feed. The implicit **final step of every run is a
sort** — outputs are ordered most-changed-first, nothing is eliminated.

- **⇓ Preview chain** — runs the stack on the preview candidates (the first
  group selection, the picked input item, or N spread frames).
- **⏵ Apply to ALL frames** — the FINAL run over every extracted image.
  Group-selector steps are skipped unless `selectors in full run` is on.
- **👁 Preview** — one image, before/after panel.
- **OUTPUT grid** — plain tiles labeled with the filter/action names that
  made them; `▲ / ▼` on an output image is **credited to the filter(s) —
  and the group selectors — that produced it**.

## 6. PROCESSING TRAIL

Every run snapshots each step level (`input → each filter/selector → output`).
Level cards show thumbnails and counts and may be marked for visual inspection,
but those marks do not feed the scene-object LLM workflow. Description and all
downstream prompt stages use Extracted Frame Gallery input images directly.

## 7. SCENE OBJECTS TEXTUAL DESCRIPTION

This is a top-level stack item, not a substage inside the member gallery. One
model call per input image describes the scene and returns a named list of
individual extractable things without coordinates. It stops after saving the
exact textual output for review. Its prompt is editable in the Description
Prompt textarea; `{{goal}}` and `{{alreadyExtracted}}` are expanded for each
input image. Every visual-extraction prompt is fully rendered as soon as the
textual-description inventory is parsed, so no unfinished prompt placeholders
are displayed.

Both image-driven model selectors accept only models declaring `vision` or
`multimodal` capability. Unavailable inherited vision models remain visible but
disabled; text-only models cannot be sent input images. On initial load, an
enabled Claude Opus 4.8/4.8-fast vision model is preferred when available;
otherwise the effective workspace model remains the fallback. Manual choices
are never overwritten.

Every successful model response is cached by model ID, exact prompt, and image
content hash. The cache is part of the workspace's persisted Video Import page
state, survives reloads, covers textual descriptions,
`objects_with_sub_objects`, extraction-prompt fan-out, extraction planning,
object visuals, and turtle generation, and reports each reuse as a
`cached model response` STATUS line.

## 8. SCENE OBJECT VISUALS

All intake, player, frame-selection, filter, output, trail, and initial
description steps stay full-width above the split. The split begins at the
Extracted Images gallery. Its full-width top border is a persisted automation
strip with independent **Describer**, **Planner**, **Outliner**, **Extractor**, **Turtle Gen**,
**Turtle PNG**, **Next recursion levels**, and **Enlarge subobjects** toggles. The left column contains
the hideable galleries; the right column contains the recursive tree, selected
cycle inspector, and visual-extraction/Turtle stack.
All eight automation toggles default ON for a workspace with no saved page
state. After any change, the exact toggle state is persisted and restored
instead of resetting to the defaults.

The automation strip starts with a global **model for all calls** and a total
1–50 process ceiling. Each Describer, Planner, Outliner, Extractor, Turtle Gen, and
Turtle PNG row then
selects its model, maximum concurrent processes, and workspace-edited or
built-in prompt. Per-call models default to **use global**; per-call process
caps default to **keep below global limit**. Independent images run concurrently
up to both caps, while removals from one changing leftover scene remain ordered.
There is no hidden six-image ceiling: each ready queue uses as many workers as
the selected cap permits. Root and recursive-child Describer work share one
work-conserving pool. When Describer inherits its cap, one-third of the global
maximum is its protected share while downstream work exists. It borrows every
otherwise-idle global slot at startup, then stops refilling borrowed slots as
Planner, Outliner, Extractor, Turtle Gen, or Turtle PNG work arrives. An explicit
Describer per-call limit overrides this soft-share policy.

All enabled call types cooperate through one global semaphore and may run at
the same time. The scheduler enforces the total cap and every per-call cap,
prefers the runnable type with the lowest current utilization, and immediately
fills released slots from the shared queue. The controller reports global and
per-type active/queued counts.
All model selectors use the shared colored-tag combobox extracted from
ChatConversation. Models are grouped by backend, and individually colored chips
show useful capabilities such as vision, image output, multimodal, reasoning,
tools, JSON, audio, code, and text, plus preferred/inherited/unavailable state.
Opening or changing any model, process-limit, or prompt combo in a per-call row
opens that call's complete selected prompt in a full-width editor directly
below the controller bar. **Reload prompt** refreshes only that prompt from the
filesystem-backed page state; **Save prompt** writes the current prompt
explicitly without requiring a page reload.

Failed Describer, Planner, Extractor, Turtle Gen, and Turtle PNG work receives a
one-second cooldown and is returned to the queue rather than blocking sibling
work. Fresh/other ready work continues first; failed items then retry
indefinitely. Retry calls bypass cached failed/invalid responses so they
actually invoke the selected model again.
Each call type reserves up to two of its available initial worker slots for due
retries. When fewer retries exist, fresh work immediately borrows those slots;
when fewer fresh tasks exist, retries fill the rest, so capacity is never
deliberately left idle.
Restart-pending is a scheduler-wide drain signal. Calls already running may
finish, but queued calls and every stage about to advance stop before launching
new model work. The controller shows **RESTART PENDING · DRAINING**. Cancelling
restart resumes the retry/ready queues; starting restart keeps them paused
through page reload.
Restart intent is also stored in the local backend presence registry. Isolated
workbench tabs discover it during their five-second presence poll, display the
same notice, and stop advancing their own workers even when BroadcastChannel
cannot connect their browser contexts.

Each input image follows one cycle:

1. **Describer** — describe the current image and list only its direct visually
   separable child objects. When the image is already an extracted object, do
   not relist that parent object.
2. **Planner** — choose the foreground-first extraction order. It never writes
   or rewrites another prompt.
3. **Extractor** — use one persisted user-authored precision template for every
   call. Substitute only the single next object selected by Planner (name,
   description, position, and total), call the model, and request a pixel-edge silhouette with
   separate polygons for disconnected visible parts and hole polygons for
   enclosed gaps. The backend rasterizes at 4× resolution, downsamples an
   anti-aliased alpha mask, and saves a full-alpha PNG before precisely removing
   the same mask from the background. It separately enlarges each cutout to at
   least 640px on its longest side and adds transparent padding; this analysis
   image, not the small gallery cutout, feeds the next Describer pass.
   Planner supplies per-object surgical include/exclude/occlusion instructions,
   a clockwise landmark contour, and a normalized Turtle-style move/line
   boundary walk. Extractor treats that walk as a guide and refines it into the
   final pixel-edge polygons and holes.
   Extractor also returns an LLM-authored `backgroundFill` plan describing the
   colors, gradients, continuing edges, and texture expected behind the removed
   object. The selected Extractor model is used when it advertises image
   output; otherwise the workbench prefers the enabled GPT-5.3-Codex
   image-output resource, then the first enabled image-output model. The
   default content-aware inpaint sends the source PNG, transparent edit mask,
   and fill plan through that backend's standard OpenAI-compatible
   `/images/edits` endpoint. Only a real provider/worker image with the exact
   input dimensions is accepted, and only masked pixels are composited back;
   simulated, missing, malformed, or failed output falls back to local NumPy
   boundary diffusion. The renderer, model, provider artifact, and fallback
   reason are retained in the response and provenance. Median, blur, and
   transparent-hole modes remain explicit alternatives.

Every successful cutout may be enqueued as a new image and run through the same
Describer → Planner → Extractor cycle. Each automatic worker processes only its
own ready queue and never retries failed or `NONE` objects. Turning **Next
recursion levels** off stops new child inventories without discarding cutouts;
turning it back on makes prior cutouts eligible again. **Enlarge subobjects**
controls whether the next pass uses the padded 640px analysis image or the exact
small cutout. Manual Call LLM buttons remain available regardless of automation.
An empty direct-child inventory is the normal leaf
condition; an Extractor `NONE`, unusable geometry, or cut failure terminates
that specific sub-object branch; level 9 is the fixed safety ceiling; and
**Stop** remains the manual interrupt. The left tree labels failed branches as
`EXTRACTOR STOP`.

A successfully described leaf automatically enters Turtle termination.
**Turtle Gen** writes a constrained normalized-coordinate JSON drawing program.
**Turtle PNG** uses its independently selected model and prompt to turn that
draft into the final draw program. The backend validates and executes only the
supported drawing commands, never arbitrary Python. It saves both programs and renders a terminal PNG,
lists the terminal source image in **Pre-Turtle Leaves**, and displays the
rendered PNG in its own **Turtle Output** gallery. Both normal and Alt hover show
the Turtle program and render alongside the parent-object and image-Describer
metadata.

Every Video Import-generated image has a neighboring
`<stem>.provenance.json`. The self-contained record includes output and
original dimensions, source video/time/scene when applicable, parent image and
parent sidecar, crop/mask geometry, resize scale/padding, operation metadata,
and the complete lineage back to the first-seen frame. Turtle program/render
paths are written into the leaf image's provenance record. Legacy images receive
a minimal provenance sidecar when queried through `/image-provenance`.

The backend runner disables file watching and automatic reload. Backend edits
are applied only through an explicit, batched restart by the user or operator;
this avoids the prior WatchFiles high-CPU orphan/no-listener state.
The Vite development server also runs with HMR disabled and no surgical
file-change reload hook. UI edits become visible only after an explicit browser
reload, allowing the user/operator to batch changes first.

All workbench pages can report active work and restart-relevant changes through
the global title-frame process channel. Requesting Restart while work is active
opens a draggable, nonmodal center notice instead of interrupting the page. The
notice explains why restart was deferred, accumulates status/change entries as
the user keeps working, and waits for an explicit **Restart now** action.
Restart and Cancel Restart remain bright, colored, glowing, and full-contrast
even while lifecycle protection temporarily disables duplicate restart
submission.
Every open workbench tab phones the local backend presence registry and global
frame every five seconds with
its tab, workspace, page, URL, and activity identity. Presence and process
events cross tabs through `BroadcastChannel`, appear as Open/Active counts in
the title frame, and are exposed in `window.__workbenchGlobalFrameStatus` so an
operator can inspect exactly what is active, even across isolated browser
contexts where BroadcastChannel is unavailable. Restart-pending requests and their
change ledgers therefore appear in every open workbench, not only the tab that
originated them.

The same global title frame accepts structured realtime UI commands for
allowlisted style, `live-ui-*` class, and scroll changes. This lets an operator
apply safe ephemeral page adjustments without reload or arbitrary JavaScript
execution. Selectors and affected element counts are bounded; network-bearing
or executable CSS values are rejected. **Live patches N** reports applied
changes and restores every original value in reverse order when cleared.

The left tree is data-driven rather than a fixed possibility diagram: each orb
is one real input or extracted-object inventory; child lines represent actual
parent/child cutout relationships; labels show Describer, Planner, and Extractor
completion counts. Clicking an orb selects that cycle in the right inspector
and scrolls to its complete prompts, outputs, and errors.
The controller's **Planner output** action and the inspector's Planner status
button both open the visual-output section and smooth-scroll directly to the
selected cycle's expanded Planner response. Describer and Extractor status
buttons similarly reveal their exact output sections.
Root inventories and output cards are sorted by original frame index, so the
first image stays first even when concurrent responses finish out of order.
Planner is no longer shown complete merely because an undescribed inventory is
empty; the controller and cycle status explicitly report waiting for
Describer, queued, retrying after error, or output ready.

The sticky left gallery column contains all Extracted Images, checked Selected
Images, then per-depth (`LEVEL 0`
through the deepest discovered node) Extracted Objects and Leftover Backgrounds
galleries. Each left gallery has its own persisted hide/restore disclosure.
The right column contains the recursive workflow tree, inspector, prompts, and
execution stack. No pre-extraction section is placed inside this split.
Workflow gallery tiles do not show selection checkboxes. An ordinary click
pins that image's context popup; **Ctrl-click** exclusively selects or unselects
the tile without clearing prior selections. Input-image selections feed
Describer, while object/background selections persist for curation across runs.
The Selected Images mirror uses the same Ctrl-click rule for removal.
Its **Clear** action removes the selected roots from the workflow and clears
their complete recursive Describer/Planner/Outliner/Extractor metadata,
descendant inventories, scene pointers, Turtle state, response/provenance
caches, derived gallery selections, and pinned metadata popups. Original image
files and their durable provenance sidecars remain on disk.
The pinned popup stays at that screen position; pointer movement and hover exit
do not dismiss it. The popup remains
until its explicit **Close** button is pressed. Context popouts auto-size for
their text, never exceed half the viewport width or height, scroll overflow,
and pinned popouts can be resized in both directions within those bounds. Their
headers remain sticky inside the scroller so Close is always visible.
The popout fetches and pretty-prints the image's complete provenance JSON.
Describer, Turtle Gen, and Turtle PNG JSON are also pretty-printed within the
popout only; their persisted/raw artifacts are not rewritten.
Both ordinary pinned and Alt-click popouts also show that image's exact Planner
output and every available one-object Outliner result. Before Planner output exists, its section truthfully reports waiting for
Describer, queued, retrying after error, or not required for a no-subobject
leaf.
Every workflow gallery has its own Clear action. Clearing an extracted-object
or leftover-background level also clears its dependent descendants, making the
enabled automation stages regenerate that branch. Clearing Turtle Output
requeues leaf programs and renders. Clearing Pre-Turtle Leaves invalidates the
earliest affected extraction level so the terminal source images are generated
again before Turtle reruns.

All editable prompts and per-object call details start collapsed. Describer,
Planner, Outliner, recursive Extractor, and Turtle each have an explicit **Call LLM**
button. Initial Describer, Planner, Outliner, Extractor, and Turtle templates are supplied
by this implementation, but the running system never generates or rewrites
them; users edit and persist the templates directly. Planner returns order only:
it never returns contours, polygons, or cutout instructions. Outliner receives
one Planner-selected object per request and returns that object's polygons,
holes, clockwise contour description, and normalized Turtle trace. Independent
one-object Outliner jobs do not wait for extraction and run under their own
process cap; the warm shared workers keep taking jobs while releasing the fair
global active slot between responses. Extractor waits until an inventory's
outlines are ready, then removes objects in Planner order and reconstructs each
background from the corresponding outline. All responses continue to
use the persistent content-addressed cache.
Every Outliner result is bound to the exact source image path and decoded pixel
dimensions included in its prompt. Before cutting, the backend verifies that the
current scene is that source or a provenance descendant with the same coordinate
space. Out-of-range polygon/hole/box coordinates and dimension or lineage
mismatches are rejected rather than silently clamped onto the wrong image.

- **Inventory goal** — find any members / faces / characters / objects /
  text-signs.
- **Removal method** — median inpaint, blur fill, or transparent hole.
- Results land at the bottom in side-by-side vertical strips, one per input
  image; every cutout retains its recursive depth and parent inventory and can
  be accepted or returned.

## 9. TURTLE, IMPORT GAME

- **🐢 Generate turtle programs** — the one model-driven drawing step: a
  Python-turtle redraw program per (ideally prepass-reduced) frame, saved
  beside the frames.
- **IMPORT GAME → Materialize as recording** — arranges the frames (OUTPUT
  copies when present) as an ARC3 recording; each frame's move encodes the
  cast diff. Opens Play & Record when done.

## Everywhere

- **STATUS strip** — sticky at the top: three rolling log lines, an
  `auto-collapse` switch, and **■ Stop**, which interrupts any job or model
  loop at its next step, keeping partial results.
- **Galleries collapse** — every named gallery (USER PICK, EXTRACTED FRAME,
  FILTER EFFECT, PROCESSED OUTPUT, PROCESSING TRAIL, SCENE OBJECT VISUALS) has an
  expand/collapse header and folds
  itself after you scroll past it. `📌 pin` any gallery to freeze its state,
  or switch `auto-collapse` off globally.
- Nothing here overwrites your inputs: filters write copies, member cuts live
  beside their frames, and the input grid is never altered by a run.

---

## Appendix — the prompt that would build this

Copy the block below and hand it to a capable coding agent to rebuild
this tool from scratch:

````markdown
Build a **Video Import** page (KNOWLEDGE → Video Import) for the workbench:
a FastAPI router (`workbench/server/video_import_api.py`, mounted under
`/workbench/video-import`) plus a React page, storing everything under the
workspace's `data/VideoImports/`.

**Import**: download URLs with yt-dlp (quality ceiling combo: 480p lo-fi /
720p / 1080p / best, plus a plain-Python direct fetch for `.mp4` URLs),
import local paths, browser uploads, and a drop folder for loose files. Keep
a persistent download catalog (JSON) that backfills every imported video and
records download/extraction history. The user supplies URLs; never fetch
content for them.

**Timeline**: stream video with HTTP Range; a marker rail (click=seek,
drag=selection), persisted scene markers with a numpy frame-diff scene
detector (~4 samples/s) that is INCREMENTAL — every run resumes from the
last detected marker (`startSeconds`), keeps all earlier markers, merges +
dedupes, and records `newThisRun`/`resumedFromSeconds` in `lastScenes` — a
segment lane with split/keep/delete and re-encode trim, selection→new-video,
and a grab-single-frame-at-cursor endpoint.

**Extraction**: interval (every N seconds) or per-scene (N images right
after each change + offset) within a start/end window, max cap, and a
time/frame estimate grounded in the measured pace of prior runs. Run as
interruptible background jobs (shared job dict, progress + ETA polling, a
cancel endpoint every loop checks; partial results are kept).

**Filters as a registry** (target: hundreds): parameterized built-ins
(cartoon/pixelate/downscale), published presets in a JSON catalog, `.cube`
LUTs auto-listed from a folder (trilinear), and drop-in Python skill files
exporting `SKILL` metadata + `apply(image, params)` — the workbench executes
them directly, no LLM. Ship skills wrapping pilgram (all styles), ~70 pure
Pillow effects, ~50 scikit-image transforms, and matplotlib colormaps as
gradient maps. Skills may declare `paramChoices` (combo per param) and
`paramGrid` (permutation candidates); single-choice skills expand into one
registry entry per setting.

**The preview system**: no default filter. Extraction OPENS the **EXTRACTED
FRAME GALLERY** (all other sections start collapsed) — plain tiles (image +
index/time/source caption, hover ▲ keeper / ▼ drop) — and the GROUP bar
sits DIRECTLY BELOW that gallery, preset to **Let USER decide which item is
used**: by default everything passes through, and asking is deferred to
when it matters. The other GROUP kinds (N most unique via farthest-point
sampling, evenly spread, random, most like/unlike their originals) run
immediately. "Select group" with the user kind opens a ❓ YOUR PICK section
IN PLACE (force-opened, scrolled into view, pulsing outline): clicking a
tile USES THAT ONE ITEM immediately (the default); a multi-select toggle
switches clicks to selection for ✓ keep chosen / 🗑 remove chosen / use ALL
/ skip curation, plus
auto-curation helpers "◼ + all-black" and "▭ + flat/solid" (backend
`/select-degenerate` flags near-black and solid-color frames) — e.g. select
all the black scene-transition frames and delete them in one click. Picking
exactly ONE item flows STRAIGHT into picking its filter: the all-effects
gallery auto-renders on that item, opens, and scrolls into view. Picking a
filter tile then shows HOW IT AFFECTS ALL INPUT: the chain auto-applies to
every frame and the OUTPUT section opens into view — and then the NEXT 77
render automatically on the output of your item, and so on: the loop
continues until YOU stop it (the "auto next 77" STATUS toggle turns the
auto-continue off — then clicking an output frame starts the next round by
hand — and ■ Stop breaks it immediately). During those full runs
the let-USER-decide GROUP is a NOP — everything passes through and the
group is chosen later (explicit `select:user` chain steps still pause).
One button renders
the base image through EVERY filter in scope (included / excluded / all)
into a gallery — one tile per filter — and another renders the picked
filter across its parameter permutations. The gallery/preview base
resolves: picked item → GROUP pick → last frame (never silently the test
card); the status line names the base of every run.

**THE LOOP**: clicking a gallery tile appends that effect (with its adopted
params) to the chain AND auto-applies the whole chain to ALL extracted
frames; clicking any OUTPUT frame makes it the new gallery base and re-runs
every effect on it; the next pick extends the chain and re-applies to all —
repeat. `select:user` is also a chain step: the pipeline pauses with a YOUR
PICK section (click the item that continues, use-ALL, or skip; ■ Stop
cancels the pause).

**Votes**: persistent per-filter up/downvotes order the combo and the
gallery; disabling a filter from any of its output tiles is an extreme
downvote (−10) plus exclusion (re-enable keeps the history); an analytical
"retinter" scan flags and excludes filters that are pure pointwise color
remaps (low per-input-color output variance, preserved edge structure).
Votes on chain OUTPUT images are credited to the filters — and group
selectors — that produced them; selector history shows beside selector
choices.

**Chains as a stack**: step 0 is always the extraction criteria (+ preview
candidate count); added steps default to `<none>`; each step has its own
filter/selector combo and params (selector steps are no-ops until N is
set); the implicit final step of every run sorts outputs most-changed-first
without eliminating any. Preview runs flush per step and snapshot every
level into a TRAIL; the final full-apply mode runs the filters over ALL
extracted images (group-selector steps join only via an explicit toggle).

**Entity extraction from input images**: TRAIL level cards are inspectable but
do not select LLM inputs. For each Extracted Frame Gallery input image, use a
selectable model to run a recursive Describer → Planner → Outliner → Extractor cycle.
Describer lists direct children, Planner orders them, Outliner traces each
object in its own independently scheduled call, and Extractor cuts and
reconstructs the background from those outlines. Every cutout repeats that
same cycle until Describer returns no direct children or the branch reaches
level 9. Inventory goals:
any members / faces / characters / objects / text-signs. Results render as one
vertical strip per input image with recursive depth/parent labels; each cutout
can be accepted or rejected.

**Finish**: a TURTLE row (model writes a small Python-turtle redraw program
for leaf-object images, falling back to extracted objects/output/input frames)
and IMPORT GAME (materialize the frames as an ARC3
recording whose moves encode the cast diffs; open Play & Record).

**Ergonomics**: THE PAGE MUST BE SCROLLABLE — it lives inside the
workbench shell whose stage clips overflow, so the page root must be a
height-constrained column whose content scrolls vertically (and
horizontally where rows overflow); verify both directions in the running
app. A sticky STATUS strip (3 rolling log lines, also pushed to the app's
global footer status feed) with a global ■ Stop that interrupts any job,
model loop, or pending user pick at its next step; EVERY section (JSON
config, intake, player, inputs, prepass, gallery, output, trail, member
strips) is a collapsible that STARTS COLLAPSED, auto-folds after the user
scrolls past it, with a 📌 pin per section and a global auto-collapse
switch; output images are labeled with the filter/action names that made
them. Nothing overwrites inputs; every long-running step is interruptible
with partial results kept.

**Exact-state snapshot**: the page continuously builds a JSON object of its
ENTIRE state (video, player time, markers/segments, extraction criteria,
frames, picks, chain, gallery, outputs, trail, probes, members, toggles,
section collapse map — everything path-based against real files), and
persists it BESIDE THE IMAGE REPOSITORY as
`data/VideoImports/page_state.json` (GET/POST `/page-state`), with a
debounced localStorage mirror as fast fallback; on mount the NEWEST copy
wins (timestamped), a click the user makes while restore is in flight
always beats the restore, the video list never steals a valid selection,
and unmount flushes the state (sendBeacon). Restore is StrictMode-safe. STATUS strip: ⤓ state (copy JSON)
and ⟲ forget (start clean). A JSON CONFIG collapsible section exposes that
object through the real embedded SuperControl (UniversalArtifactEditor,
`kind: "standard"`) — File / Markdown / Resource tabs, MeTTa/JSON/Tree/Text
views, ALL/CTX tab sets — with actions ⏎ Apply-to-flow, ↻ track-live,
⤓ copy, ⟲ forget-saved: edits APPLY LIVE to the flow as soon as the text
parses (debounced), with an INVALID JSON indicator while mid-edit.

**Optional downstream invalidation** — two independent STATUS toggles:
"auto-clear stale data" (default ON) clears derived results below when
upstream DATA changes (new video, re-extract) and prunes dead pick
pointers, but never touches the workflow (chain/filters/criteria);
"auto-clear next algorithm" (default OFF) additionally drops the LATER
chain steps when an upstream step is edited.

**Naming**: the component is `VideoImportPage.tsx` — the graduated baseline
(generation v1 "organic") of the page-generations family in
`VideoImportFamily.tsx`; future rebuilds register as v2+ after updating
this prompt first.
````
