# Universal Artifact Editor

[Back to repository README](../../../README.md)

## Baseline

The current active application and its rich editors are the acceptance baseline. A shared editor shell must preserve the union of useful artifact-specific behavior; it must not reduce specialized editors to a generic JSON form.

## Required Capabilities

Every hierarchical artifact family should provide, where meaningful:

1. A specification parent with concrete alternatives beneath it.
2. A preferred/default alternative selector.
3. Persistent, closeable tabs with dirty markers.
4. Single-pane and split-comparison modes.
5. Rich artifact-specific controls plus interchangeable MeTTa/JSON source editing.
6. Filesystem save with shared inheritance and workspace overrides.
7. Contextual documentation on the right.
8. Tests, history, benchmarks, diffs, and logs when real data exists.
9. A playground/run surface for executable artifacts.

`UniversalArtifactEditor` supplies common hierarchy, tab, comparison, inspector, and dock chrome. It also owns embedded Super Control tabs and chooses their renderers from typed artifact data; host pages do not inject control markup or provide page-specific CSS.

The Operations page retains its page heading, hierarchy, open-document tabs, and split-pane selection. Each selected document pane asks `UniversalArtifactEditor` for an embedded Super Control. Operations contributes only the rich Abstract Operation/Operation Implementation tab. The Super Control keeps its existing built-in File, Markdown, Resource & Inheritance, and Universal Execution Runner editors; it does not inject library, model, policy, or plugin pages. `ResourceSourceEditor` is mounted only by the built-in tabs and must not remain duplicated inside the Operations renderer.

Topics follows the same host contract but contributes no special tab. Its selected document is rendered only through the standard File, Markdown, Resource & Inheritance, and Universal Execution Runner tabs; Topics supplies resource text plus save/delete callbacks and retains its taxonomy navigator outside Super Control.

Resource and Inheritance are one content-backed tab. Where a resolved inherited view exists, it appears below the editable resource controls. That resolved view is read-only, provides save/export and reload-from-origin actions, and must not offer any action that loads a different file or resource. It also identifies the effective parent and links to that real parent resource for editing.

The Chat page's outer File tab displays a real embedded SuperControl. With no chat node selected, its source is the complete visible-stream JSON resource. Selecting a message node disables chat auto-scroll and makes that node's complete raw record the SuperControl source until it is deselected; auto-scroll resumes only when the user explicitly enables it.

`UniversalArtifactEditor` imports `super_control.css` itself. That stylesheet owns the embedded toolbar, action buttons, editor tabs, source-editor sizing, borders, scrollbars, and responsive behavior, using the same visual treatment as the Models editor. Host pages must not import a separate stylesheet to make an embedded Super Control usable.

`DataCatalogPanel`, `PromptLibraryEditor`, and `LlmModelsEditor` continue to retain their specialized panels and validation until their own incremental Super Control migrations are accepted.

## Super Control Display Contract

Super Control owns its display mode. Hosts provide resource data and callbacks; they do not construct separate layouts for these modes.

| Mode | Required behavior |
|---|---|
| **Tabs** | Show the selected controls as a tabbed pane. |
| **Stacked** | Render every selected control at its maximum content length inside one outer scrolling surface. Nested editor scrollbars must not replace that single scrollbar. |
| **Single** | Render one selected control so it occupies all available Super Control content space. It opens the context-selected default tab, which is normally the File tab rendered by `ResourceSourceEditor`. |
| **SplitV** | Render two independently selected Single controls side by side, separated by a vertical divider. |
| **SplitH** | Render two independently selected Single controls one above the other, separated by a horizontal divider. |

In **Tabs** mode, the Super Control chrome displays a pull-down mode selector whose current value is Tabs. That selector can switch directly to Stacked, Single, SplitV, or SplitH.

The display-mode switcher occupies the Super Control header action position currently used by the **Split view** button. It replaces that one-off in-control button rather than adding another toolbar or control row. Document-to-document comparison owned by an outer artifact page remains a separate host-level concern.

Every mode must retain a visible, reachable way to restore **Tabs** mode. Stacked, Single, SplitV, and SplitH must not hide the Tabs action inside a pane, tab, overflow region, or other control that disappears in that mode.

The set of selectable controls is also owned by Super Control:

- **ALL** exposes every registered tab that currently has a real Super Control renderer and content.
- **CTX** exposes the contextual subset of those content-backed tabs returned by the Super Control selector API.

Registered controls without an implemented renderer are not displayed yet. Super Control must not create empty tabs or placeholder “unavailable” panels for future controls.

The Super Control banner exposes this choice as a persistent segmented **TABS | ALL | CTX** button group beside the **DISPLAY** mode selector. ALL and CTX are selection buttons, not entries in the editor-tab row.

Changing display mode or switching between ALL and CTX changes presentation only. It must not mutate the resource, discard dirty edits, or ask the host page to supply different controls.

## JSON Resource Identity

Whenever Super Control displays the identity of a parsed JSON resource, the identity must come from the document rather than only from its filename. The display normally includes the resource `id` and the applicable discriminator fields, including `kind`, `type`, `subkind`, or equivalent role metadata when present. A human-facing `label` may accompany that identity, but it must not hide the stable ID or resource type information.

When the source contains one JSON object, Super Control derives its header from that object using **`KIND - Label (id)`**. `KIND` is the best available resource discriminator (`kind`, then an applicable `type`, `subkind`, or role). The parenthesized ID is shown only when `id` differs from `label`. If the object has no separate label, the header uses **`KIND - id`** without repeating the same value.

If the source cannot be parsed, Super Control may fall back to the path or filename, but it must visibly report that the resource identity is unresolved rather than presenting the fallback as parsed metadata.

## Resource Source Rendering

`ResourceSourceEditor` displays the resource source in an editable CodeMirror surface except when the selected context is explicitly read-only, such as a resolved inheritance view. It attempts to select an appropriate syntax mode and lexer from the source format, resource metadata, and filename extension rather than treating every resource as plain text.

MeTTa source must use a Lisp- or Clojure-compatible CodeMirror lexer so parentheses, symbols, strings, comments, and nested forms receive useful syntax highlighting when a dedicated MeTTa lexer is unavailable.

Content detection takes precedence over the filename extension:

- Source that can be parsed as a JSON document is displayed as MeTTa by default, including files whose names end in `.json`. The user can still switch to JSON, Tree, Text, or Markdown views without changing the underlying resource.
- Source detected as Markdown uses CodeMirror's Markdown lexer whether or not the filename ends in `.md` or `.markdown`.

Every source opened in `ResourceSourceEditor` must pass through file-type detection. The detector considers the content, filename and full path, shebang or other language markers, and available resource metadata, then loads the best matching CodeMirror language extension. This applies to arbitrary source files, not only recognized workbench resource suffixes. If no language can be identified confidently, the editor falls back to plain text without modifying or rejecting the source.

## Tab Input Editor Growth

Runner input textareas in tab pages carry the stable `tab-input-editor` class.
Their supported growth mechanisms are explicit modifier classes:

- `tab-input-editor--opted-in` marks a field explicitly selected for this
  combined growth behavior.
- `tab-input-editor--auto-grow` expands to the content height, capped at the
  nearest tab/page boundary.
- `tab-input-editor--manual-resize` preserves the native vertical resize handle.

The Operations typed-value input and Universal Runner resource input are the
initial explicit opt-ins. Each carries both growth modifiers. When its content
exceeds the available page height it stops growing and gains an internal
vertical scrollbar. Other editors retain their existing growth behavior until
they are separately opted in.

## JSON Tree and Folding

For JSON-parsable source, `ResourceSourceEditor` provides a tree presentation derived from CodeMirror's parsed JSON structure. Object and array nodes have clickable disclosure controls that expand or collapse that node without changing the JSON document.

The tree surface also provides persistent overlaid **Expand** and **Collapse** controls. These controls operate on the structure and folding state produced by CodeMirror rather than constructing a disconnected second copy of the document. They support expanding or collapsing the whole tree and the currently selected branch while keeping node selection and source edits synchronized between Tree, JSON, and MeTTa views.

## Data Integrity

All nodes, alternatives, defaults, documents, and runtime results must originate in workspace files or backend APIs. Visual mockups may guide layout but cannot supply active data. Saves must retain semantic specification/implementation separation and must not collapse variants into a monolithic catalog.

## Regression Principle

Tests should assert behavior and visible capabilities of the current editor rather than bind the baseline to a historical commit identifier. UI validation must cover hierarchy selection, variant mutation, save/reload, tabs, split view, scrolling, and the executable playground.
