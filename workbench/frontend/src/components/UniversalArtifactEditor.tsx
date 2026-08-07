import { useMemo, useState, type ReactNode } from "react";
import { ArtifactTreeCommandContext, type ArtifactTreeCommand } from "./ArtifactTreeBranch";
import { useArtifactTreeFilter } from "./useArtifactTreeFilter";
import "../styles/operation_editor.css";

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

  /** Resource-specific editor body. Operations may render Python/Prolog/MeTTa/LLM panels here. */
  renderEditor: (key: string, secondary: boolean) => ReactNode;
  emptyEditor?: ReactNode;

  /** Common inspector extension: dependencies, used-by, coverage, provenance, etc. */
  inspector?: ReactNode;

  /** Optional shared controls such as Preferred Implementation / Representation / Prompt Variant. */
  variantControls?: ReactNode;

  /** Documentation, History, Tests, Benchmarks, Diff, Logs, or other dockable panels. */
  bottomPanels?: UniversalArtifactBottomPanel[];
  footer?: ReactNode;

  className?: string;
  treeClassName?: string;
  workspaceClassName?: string;
  tabsClassName?: string;
  panesClassName?: string;
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
}: UniversalArtifactEditorProps) {
  const activeTab = tabs.find(tab => tab.key === activeKey) || null;
  const compareTab = tabs.find(tab => tab.key === compareKey) || null;
  const trail = breadcrumb?.length
    ? breadcrumb
    : [category || title, activeTab?.label || "Select artifact"];
  const [bottomPanelId, setBottomPanelId] = useState<string | null>(bottomPanels[0]?.id || null);
  const [navigatorCollapsed, setNavigatorCollapsed] = useState(false);
  const [variantsHidden, setVariantsHidden] = useState(false);
  const [variantsCollapsed, setVariantsCollapsed] = useState(false);
  const [treeCommand, setTreeCommand] = useState<ArtifactTreeCommand>(null);
  const { treeRef, treeFilter, setTreeFilter, showParents, setShowParents } = useArtifactTreeFilter();
  const commandTree = (action: "collapse" | "expand") => setTreeCommand(current => ({ action, revision: (current?.revision || 0) + 1 }));
  const activeBottomPanel = useMemo(
    () => bottomPanels.find(panel => panel.id === bottomPanelId) || bottomPanels[0] || null,
    [bottomPanels, bottomPanelId],
  );

  return <section
    className={`resource-view operation-hierarchy-page generic-hierarchy-editor universal-artifact-editor ${className}`.trim()}
    data-editor-baseline={UNIVERSAL_ARTIFACT_EDITOR_BASELINE}
  >
    <div className="artifact-breadcrumb" aria-label="Artifact breadcrumb">
      {trail.map((item,index)=><span key={`${item}:${index}`}><b>{item}</b>{index<trail.length-1&&<i>›</i>}</span>)}
    </div>

    <div className="resource-heading artifact-editor-heading">
      <div><span>{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>
      {headerActions && <div className="studio-actions">{headerActions}</div>}
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

    <div className={`operation-hierarchy-layout artifact-editor-body ${navigatorCollapsed?"navigator-collapsed":"navigator-expanded"}`}>
      <div className={`${treeClassName} artifact-navigator`.trim()}>
        <div className="artifact-navigator-toolbar">
          <span>HIERARCHY</span>
          <div className="artifact-navigator-actions">
            <label className="artifact-tree-filter"><span>Filter tree</span><input type="search" value={treeFilter} onChange={event=>setTreeFilter(event.target.value)} placeholder="Filter tree…" /></label>
            <button type="button" aria-label={showParents?"Hide Parents":"Show Parents"} aria-pressed={showParents} disabled={!treeFilter.trim()} onClick={()=>setShowParents(value=>!value)}><b>{showParents?"Hide Parents":"Show Parents"}</b></button>
            <button type="button" aria-label={variantsHidden?"Unhide Variants":"Hide Variants"} aria-pressed={variantsHidden} onClick={()=>{const hidden=!variantsHidden;setVariantsHidden(hidden);commandTree(hidden?"collapse":"expand")}}><b>{variantsHidden?"Unhide Variants":"Hide Variants"}</b></button>
            <button type="button" aria-label={variantsCollapsed?"Show Tree":"Only Toplevel"} aria-pressed={variantsCollapsed} onClick={()=>{const collapsed=!variantsCollapsed;setVariantsCollapsed(collapsed);commandTree(collapsed?"collapse":"expand")}}><b>{variantsCollapsed?"Show Tree":"Only Toplevel"}</b></button>
            <button type="button" aria-label={navigatorCollapsed?"Expand hierarchy":"Collapse hierarchy"} aria-expanded={!navigatorCollapsed} onClick={()=>setNavigatorCollapsed(value=>!value)}>{navigatorCollapsed?"›":"‹"}<b>{navigatorCollapsed?"":"Pane"}</b></button>
          </div>
        </div>
        <ArtifactTreeCommandContext.Provider value={treeCommand}><div className="artifact-navigator-content" ref={treeRef}>{leftPane}</div></ArtifactTreeCommandContext.Provider>
      </div>
      <div className={workspaceClassName}>
        <div className={tabsClassName}>
          {tabs.map(tab => <div className={`operation-document-tab ${tab.key===activeKey?"active":""}`} key={tab.key}>
            <button onClick={()=>onActivate(tab.key)} title={tab.subtitle || tab.label}>
              <span>{tab.kind}</span><b>{tab.label}</b>{tab.dirty&&<i>●</i>}
            </button>
            <button className="close" onClick={()=>onClose(tab.key)}>×</button>
          </div>)}
        </div>
        <div className={`${panesClassName} ${compareKey?"split":"single"}`}>
          {activeKey ? renderEditor(activeKey,false) : (emptyEditor || <div className="studio-empty">Select a specification or variant.</div>)}
          {compareKey ? renderEditor(compareKey,true) : null}
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
