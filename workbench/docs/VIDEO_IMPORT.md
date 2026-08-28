# Video Import — Help

The Video Import page (KNOWLEDGE → Video Import) is the full loop for turning
a video you have the rights to into a playable ARC3 game recording: import →
timeline editing → frame extraction → a **preview system** for building
filter chains → entity extraction with probes → materialize.

Everything runs in the workbench itself (Python/PIL/scikit-image skills,
LUTs, yt-dlp) — a model only enters where explicitly chosen (MEMBERS, TURTLE).

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
  with offset) · start/end window (`⤓ start` / `⤒ end` take the player time)
  · max frames · a grounded frame/time estimate.
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
- Hover overlay: **▲ keeper** (adds to the group selection, green outline) ·
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

## 6. TRAIL / PROBES

Every run snapshots each step level (`input → each filter/selector → output`).
Level cards show thumbnails and counts. **Click levels to place extraction
probes** — several can sit side by side; default is the final output.

## 7. MEMBERS — entity extraction

For each probed level, the loop asks the model to outline **one member per
pass** (`{name, polygon}`), the workbench cuts it out as a **transparent
GIF**, removes it from the scene, and continues on the reduced scene:

- **Probe goal** — find any members / faces / characters / objects /
  text-signs.
- **Removal method** — median inpaint, blur fill, or transparent hole.
- **divide into X** — tell the model the scene should split into ~X members.
- Results land in **side-by-side vertical strips** (one per probe) with
  counts at the top; every cutout has **✓ accept** (becomes a cast tag on
  the frame) and **✗ return** (the cutout is composited back into the
  scene).

## 8. TURTLE, IMPORT GAME

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
- **Galleries collapse** — every gallery (INPUT IMAGES, GALLERY, OUTPUT,
  TRAIL/PROBES, MEMBER STRIPS) has an expand/collapse header and folds
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
`/api/video-import`) plus a React page, storing everything under the
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

**The preview system**: no default filter. Extraction OPENS the input-images
gallery (all other sections start collapsed) — plain tiles (image +
index/time/source caption, hover ▲ keeper / ▼ drop) — and the GROUP bar
sits DIRECTLY BELOW that gallery, preset to **Let USER decide which item is
used**: by default everything passes through, and asking is deferred to
when it matters. The other GROUP kinds (N most unique via farthest-point
sampling, evenly spread, random, most like/unlike their originals) run
immediately. "Select group" with the user kind opens a ❓ YOUR PICK section
IN PLACE (force-opened, scrolled into view, pulsing outline): multi-select
tiles with ✓ keep chosen / 🗑 remove chosen / use ALL / skip, plus
auto-curation helpers "◼ + all-black" and "▭ + flat/solid" (backend
`/select-degenerate` flags near-black and solid-color frames) — e.g. select
all the black scene-transition frames and delete them in one click. A FULL
run (apply-to-ALL) with the user kind and no selection yet ASKS the GROUP
question first; "use ALL" is the pass-through answer. One button renders
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

**Entity extraction with probes**: TRAIL level cards are clickable probes
(multi-select, side by side). For each probed level, loop a selectable
model: it outlines ONE member per pass as `{name, polygon}`; cut the
polygon out as a transparent GIF, remove it from the scene (median inpaint
/ blur fill / transparent hole), and continue on the reduced scene until
NONE or the per-frame cap ("divide into X" tells the model the target
count). Probe goals: any members / faces / characters / objects /
text-signs. Results render as one vertical strip per probe with counts at
the top; each cutout can be accepted (tags the frame's cast) or rejected —
rejection composites the transparent cutout back into the scene.

**Finish**: a TURTLE row (model writes a small Python-turtle redraw program
per reduced frame) and IMPORT GAME (materialize the frames as an ARC3
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
