import { useEffect, useMemo, useState, type ReactNode } from "react";
import { ArtifactTreeCommandContext, type ArtifactTreeCommand } from "./ArtifactTreeBranch";
import { RepeatSwitch, TreeViewControls } from "./TreeViewControls";
import { DEFAULT_TREE_VISIBILITY_RULES, type TreeVisibilityRules, useArtifactTreeFilter } from "./useArtifactTreeFilter";
import { CategorizedArtifactNodes } from "./CategorizedArtifactTree";
import { TreePaneResizer } from "./TreePaneResizer";
import { ResourceSourceEditor, textLanguageForFilename } from "./ResourceSourceEditor";
import { MarkdownDocument } from "./MarkdownDocument";
import { fetchSubControls, type SubControlDescriptor } from "../lib/subControls";
import { SubControlBody, SubControlProvider, SuperControlDepthProvider, useSuperControlDepth } from "./subControlRegistry";
import "../styles/operation_editor.css";
import "../styles/super_control.css";

/** The host page's own editor body, always the first tab. */
const HOST_SUB_CONTROL = "__host__";

export const UNIVERSAL_ARTIFACT_EDITOR_BASELINE = "current-rich-editor";

export type UniversalArtifactTab = {
  key: string;
  kind: string;
  label: string;
  dirty?: boolean;
  subtitle?: string;
};

export type UniversalArtifactBottomPanel = {
  id: string;
  label: string;
  content: ReactNode;
  badge?: string | number;
};

export type UniversalArtifactEditorProps = {
  workspaceId?: string;
  categoryTree?: string;
  eyebrow: string;
  title: string;
  description: string;
  category?: string;
  breadcrumb?: string[];
  headerActions?: ReactNode;
  notice?: ReactNode;
  error?: string | null;
  onDismissError?: () => void;

  /** Rich specification/variant navigator on the left. */
  leftPane: ReactNode;

  /** Persistent multi-document tabs. */
  tabs: UniversalArtifactTab[];
  activeKey: string | null;
  compareKey: string | null;
  onActivate: (key: string) => void;
  onClose: (key: string) => void;

  /** Resource-specific editor body. Operations may render Python/Prolog/MeTTa/LLM panels here. The third arg is the current display view. */
  renderEditor: (key: string, secondary: boolean, view?: "single" | "full") => ReactNode;
  emptyEditor?: ReactNode;

  /** Common inspector extension: dependencies, used-by, coverage, provenance, etc. */
  inspector?: ReactNode;

  /** Optional shared controls such as Preferred Implementation, Representation, or Prompt Alternative. */
  variantControls?: ReactNode;

  /** Documentation, History, Tests, Benchmarks, Diff, Logs, or other dockable panels. */
  bottomPanels?: UniversalArtifactBottomPanel[];
  footer?: ReactNode;

  className?: string;
  treeClassName?: string;
  workspaceClassName?: string;
  tabsClassName?: string;
  panesClassName?: string;

  /** Page-selectable display: "single" shows the active tab as the whole thing; "full" is the multi-tab Super Control. Defaults to "full". */
  initialView?: "single" | "full";
  /** Hide the runtime File⇄Super Control toggle when true. */
  lockView?: boolean;
  /** Omit the left hierarchy navigator column (for filesystem hosts that bring their own browser). */
  hideNavigator?: boolean;

  /**
   * Renderers the host supplies for enumerated sub-controls it can serve itself.
   * Keyed by sub-control id, these take precedence over the shared registry, so
   * a host that already holds the document (its source, dirty state, and change
   * handler) draws that tab instead of a generic stand-in.
   */
  subControlRenderers?: Record<string, () => ReactNode>;

  /**
   * How the host wants this Super Control presented. The host declares the look
   * and the Super Control's own stylesheet supplies it; a host never styles a
   * Super Control itself.
   */
  appearance?: "page" | "embedded" | "bare";

  /**
   * The content the host is editing, as data rather than markup.
   *
   * The host supplies the text; the Super Control decides which of its
   * sub-controls can render it and wires them up. That is why a host passes
   * `content` instead of drawing a File, Markdown, or Resource view itself.
   */
  content?: SuperControlContent;
};

export type SuperControlContent = {
  text: string;
  onChange?: (value: string) => void;
  /** Path or name, used for labelling and language detection. */
  path?: string;
  /** Read-only content still gets rendered, just not edited. */
  readOnly?: boolean;
};

/**
 * Universal Artifact Editor.
 *
 * The current active rich Operations experience is the feature baseline:
 * - semantic specification -> concrete variants on the left
 * - persistent, closeable, dirty-aware editor tabs
 * - side-by-side comparison
 * - preferred/default variant controls
 * - rich type-specific editors rather than a lowest-common-denominator JSON form
 * - common inspector and dock slots
 *
 * Artifact-family adapters add capabilities; they must not remove baseline behavior.
 */
export function UniversalArtifactEditor({
  workspaceId,
  categoryTree,
  eyebrow,
  title,
  description,
  category,
  breadcrumb,
  headerActions,
  notice,
  error,
  onDismissError,
  leftPane,
  tabs,
  activeKey,
  compareKey,
  onActivate,
  onClose,
  renderEditor,
  emptyEditor,
  inspector,
  variantControls,
  bottomPanels = [],
  footer,
  className = "",
  treeClassName = "operation-tree-pane",
  workspaceClassName = "operation-editor-workspace",
  tabsClassName = "operation-document-tabs",
  panesClassName = "operation-editor-panes",
  initialView = "full",
  lockView = false,
  hideNavigator = false,
  subControlRenderers = {},
  appearance = "page",
  content,
}: UniversalArtifactEditorProps) {
  const activeTab = tabs.find(tab => tab.key === activeKey) || null;
  const compareTab = tabs.find(tab => tab.key === compareKey) || null;
  const [view, setView] = useState<"single" | "full">(initialView);
  // Only the outermost Super Control draws the sub-control strip: a sub-control
  // may itself be a Super Control page, and drawing it again would recurse.
  const depth = useSuperControlDepth();
  const outermost = depth === 0;
  const [subControls, setSubControls] = useState<SubControlDescriptor[]>([]);
  const [subControlId, setSubControlId] = useState<string>(HOST_SUB_CONTROL);
  useEffect(() => {
    if (!outermost) return;
    let cancelled = false;
    void fetchSubControls().then(list => { if (!cancelled) setSubControls(list); });
    return () => { cancelled = true; };
  }, [outermost]);
  const activeSubControl = subControls.find(entry => entry.id === subControlId) || null;
  // The host hands over content, not markup: the Super Control decides which of
  // its sub-controls can render that text and wires them up here.
  const contentRenderers = useMemo<Record<string, () => ReactNode>>(() => {
    if (!content) return {} as Record<string, () => ReactNode>;
    const change = content.readOnly || !content.onChange ? () => {} : content.onChange;
    const label = content.path || activeTab?.label || title;
    const source = (format?: "text") => <ResourceSourceEditor
      value={content.text}
      onChange={change}
      contentReadOnly={content.readOnly}
      showEnablement={false}
      label={label}
      {...(format === "text" ? { defaultFormat: "text" as const, defaultTextLang: textLanguageForFilename(label) } : {})}
    />;
    return {
      file: () => source("text"),
      resource: () => source(),
      markdown: () => <div className="markdown-render"><MarkdownDocument content={content.text} /></div>,
    };
  }, [content, activeTab?.label, title]);
  const renderers = { ...contentRenderers, ...subControlRenderers };
  const trail = breadcrumb?.length
    ? breadcrumb
    : [category || title, activeTab?.label || "Select artifact"];
  const [bottomPanelId, setBottomPanelId] = useState<string | null>(bottomPanels[0]?.id || null);
  const [navigatorCollapsed, setNavigatorCollapsed] = useState(false);
  const [viewControlsOpen, setViewControlsOpen] = useState(false);
  const [treeCommand, setTreeCommand] = useState<ArtifactTreeCommand>(null);
  const [categoryCommand, setCategoryCommand] = useState<ArtifactTreeCommand>(null);
  const [visibilityRules, setVisibilityRules] = useState<TreeVisibilityRules>(DEFAULT_TREE_VISIBILITY_RULES);
  const { treeRef, treeFilter, setTreeFilter, showParents, setShowParents, treeKinds } = useArtifactTreeFilter(visibilityRules);
  const commandTree = (action: "collapse" | "expand", target?: string) => setTreeCommand(current => ({ action, target, revision: (current?.revision || 0) + 1 }));
  const commandCategories = (action: "collapse" | "expand") => setCategoryCommand(current => ({ action, revision: (current?.revision || 0) + 1 }));
  const commandBranches = (action: "collapse" | "expand", target: string) => {
    if (target === "all") { commandCategories(action); commandTree(action); }
    else if (target === "categories") commandCategories(action);
    else commandTree(action, target);
  };
  const updateVisibilityRules = (next: TreeVisibilityRules) => {
    setVisibilityRules(next);
  };
  const activeBottomPanel = useMemo(
    () => bottomPanels.find(panel => panel.id === bottomPanelId) || bottomPanels[0] || null,
    [bottomPanels, bottomPanelId],
  );

  if (view === "single") {
    return <section className={`universal-artifact-editor uae-single ${className}`.trim()} data-editor-baseline={UNIVERSAL_ARTIFACT_EDITOR_BASELINE}>
      <div className="uae-single-bar">
        <div className="uae-single-heading"><span>{eyebrow}</span><b>{activeTab?.label || title}</b></div>
        <div className="uae-single-actions">{headerActions}{!lockView && <button type="button" className="uae-view-toggle" onClick={() => setView("full")} title="Show the full Super Control with all tabs">▣ Super Control</button>}</div>
      </div>
      {notice}
      {error && <div className="backend-error"><b>{title}</b><span>{error}</span>{onDismissError && <button onClick={onDismissError}>×</button>}</div>}
      <div className="uae-single-body">{activeKey ? renderEditor(activeKey, false, "single") : (emptyEditor || <div className="studio-empty">Select a specification or variant.</div>)}</div>
    </section>;
  }

  return <section
    className={`resource-view operation-hierarchy-page generic-hierarchy-editor universal-artifact-editor ${className}`.trim()}
    data-editor-baseline={UNIVERSAL_ARTIFACT_EDITOR_BASELINE}
    data-appearance={appearance}
  >
    <div className="artifact-breadcrumb" aria-label="Artifact breadcrumb">
      {trail.map((item,index)=><span key={`${item}:${index}`}><b>{item}</b>{index<trail.length-1&&<i>›</i>}</span>)}
    </div>

    <div className="resource-heading artifact-editor-heading">
      <div><span>{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>
      {(headerActions || !lockView) && <div className="studio-actions">{!lockView && <button type="button" className="uae-view-toggle" onClick={() => setView("single")} title="Collapse to the single editable file view">⛶ Editable File</button>}{headerActions}</div>}
    </div>

    {notice}
    {error && <div className="backend-error"><b>{title}</b><span>{error}</span>{onDismissError && <button onClick={onDismissError}>×</button>}</div>}

    <div className="artifact-common-inspector">
      <div><span>CATEGORY</span><b>{category || eyebrow}</b></div>
      <div><span>ARTIFACT</span><b>{activeTab?.label || "—"}</b></div>
      <div><span>TYPE / VARIANT</span><b>{activeTab?.kind || "—"}</b></div>
      <div><span>STATE</span><b>{activeTab?.dirty ? "unsaved" : activeTab ? "loaded" : "idle"}</b></div>
      <div><span>OPEN</span><b>{tabs.length}</b></div>
      <div><span>COMPARE</span><b>{compareTab?.label || "off"}</b></div>
      {variantControls && <div className="artifact-inspector-extension artifact-variant-controls">{variantControls}</div>}
      {inspector && <div className="artifact-inspector-extension">{inspector}</div>}
    </div>

    <div className={`operation-hierarchy-layout artifact-editor-body ${hideNavigator?"navigator-hidden":navigatorCollapsed?"navigator-collapsed":"navigator-expanded"}`}>
      {!hideNavigator && <div className={`${treeClassName} artifact-navigator`.trim()}>
        <div className="artifact-navigator-toolbar">
          <span>HIERARCHY</span>
          <div className="artifact-navigator-actions">
            <label className="artifact-tree-filter"><span>Filter tree</span><input type="search" value={treeFilter} onChange={event=>{const value=event.target.value;setTreeFilter(value);if(value.trim())commandTree("expand")}} placeholder="Filter tree…" /></label>
            <div className="tree-repeat-permanent"><RepeatSwitch value={visibilityRules.repeats} onChange={repeats=>updateVisibilityRules({...visibilityRules,repeats})} /></div>
            <button type="button" aria-label="Expand All" onClick={()=>{commandCategories("expand");commandTree("expand")}}><b>Expand All</b></button>
            <button type="button" aria-label="Collapse All" onClick={()=>{commandTree("collapse");commandCategories("collapse")}}><b>Collapse All</b></button>
            <button type="button" aria-label="Tree View Controls" aria-expanded={viewControlsOpen} aria-pressed={viewControlsOpen} onClick={()=>setViewControlsOpen(value=>!value)}><b>{viewControlsOpen ? "Hide View" : "Show View"}</b></button>
            <button type="button" aria-label={navigatorCollapsed?"Expand hierarchy":"Collapse hierarchy"} aria-expanded={!navigatorCollapsed} onClick={()=>setNavigatorCollapsed(value=>!value)}>{navigatorCollapsed?"›":"‹"}<b>{navigatorCollapsed?"":"Pane"}</b></button>
          </div>
        </div>
        {viewControlsOpen && <TreeViewControls kinds={treeKinds} rules={visibilityRules} onChange={updateVisibilityRules} showParents={showParents} onShowParentsChange={setShowParents} onBranchAction={commandBranches} />}
        <ArtifactTreeCommandContext.Provider value={treeCommand}><div className="artifact-navigator-content" ref={treeRef}><CategorizedArtifactNodes onlyCategories={false} categoryCommand={categoryCommand} workspaceId={workspaceId} categoryTree={categoryTree}>{leftPane}</CategorizedArtifactNodes></div></ArtifactTreeCommandContext.Provider>
      </div>}
      <div className={workspaceClassName}>
        <TreePaneResizer />
        <div className={tabsClassName}>
          {tabs.map(tab => <div className={`operation-document-tab ${tab.key===activeKey?"active":""}`} key={tab.key}>
            <button onClick={()=>onActivate(tab.key)} title={tab.subtitle || tab.label}>
              <span>{tab.kind}</span><b>{tab.label}</b>{tab.key===activeKey&&compareKey?<em className="artifact-pane-side left">LEFT</em>:null}{tab.key===compareKey?<em className="artifact-pane-side right">RIGHT</em>:null}{tab.dirty&&<i>●</i>}
            </button>
            <button className="close" onClick={()=>onClose(tab.key)}>×</button>
          </div>)}
        </div>
        {outermost && subControls.length > 0 && <nav className="backend-aggregate-tabs sub-control-tabs" aria-label="Sub-controls" role="tablist">
          <span className="backend-tabs-label">EDITORS</span>
          <button role="tab" aria-selected={subControlId===HOST_SUB_CONTROL} className={subControlId===HOST_SUB_CONTROL?"active":""} onClick={()=>setSubControlId(HOST_SUB_CONTROL)}>{category || eyebrow}</button>
          {subControls.map(entry => <button
            key={entry.id}
            role="tab"
            aria-selected={subControlId===entry.id}
            className={subControlId===entry.id?"active":""}
            title={entry.source==="builtin"?entry.label:`${entry.label} · ${entry.source}`}
            onClick={()=>setSubControlId(entry.id)}
          >{entry.label}</button>)}
        </nav>}
        <div className={`${panesClassName} ${compareKey&&!activeSubControl?"split":"single"}`}>
          {activeSubControl
            ? (renderers[activeSubControl.id]
                ? renderers[activeSubControl.id]()
                : <SubControlProvider value={{workspaceId,activeKey,activeLabel:activeTab?.label ?? null}}>
                    <SuperControlDepthProvider value={depth+1}><SubControlBody descriptor={activeSubControl} /></SuperControlDepthProvider>
                  </SubControlProvider>)
            : <>
                {activeKey ? renderEditor(activeKey,false,"full") : (emptyEditor || <div className="studio-empty">Select a specification or variant.</div>)}
                {compareKey ? renderEditor(compareKey,true,"full") : null}
              </>}
        </div>
      </div>
    </div>

    {bottomPanels.length > 0 && <section className="artifact-bottom-dock">
      <nav className="artifact-bottom-tabs">
        {bottomPanels.map(panel=><button
          key={panel.id}
          className={activeBottomPanel?.id===panel.id?"active":""}
          onClick={()=>setBottomPanelId(panel.id)}
        >{panel.label}{panel.badge!==undefined&&<span>{panel.badge}</span>}</button>)}
      </nav>
      <div className="artifact-bottom-content">{activeBottomPanel?.content}</div>
    </section>}

    {footer}
  </section>;
}
