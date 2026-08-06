import { useMemo, useState, type ReactNode } from "react";
import "../styles/task_editor.css";

type EditorTab = {
  key: string;
  kind: string;
  label: string;
  dirty?: boolean;
  subtitle?: string;
};

type BottomPanel = {
  id: string;
  label: string;
  content: ReactNode;
  badge?: string | number;
};

type HierarchyResourceEditorProps = {
  eyebrow: string;
  title: string;
  description: string;
  category?: string;
  breadcrumb?: string[];
  headerActions?: ReactNode;
  notice?: ReactNode;
  error?: string | null;
  onDismissError?: () => void;
  leftPane: ReactNode;
  tabs: EditorTab[];
  activeKey: string | null;
  compareKey: string | null;
  onActivate: (key: string) => void;
  onClose: (key: string) => void;
  renderEditor: (key: string, secondary: boolean) => ReactNode;
  emptyEditor?: ReactNode;
  inspector?: ReactNode;
  bottomPanels?: BottomPanel[];
  footer?: ReactNode;
  className?: string;
  treeClassName?: string;
  workspaceClassName?: string;
  tabsClassName?: string;
  panesClassName?: string;
};

/** Shared chrome for every first-class artifact family. */
export function HierarchyResourceEditor({
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
  bottomPanels = [],
  footer,
  className = "",
  treeClassName = "task-tree-pane",
  workspaceClassName = "task-editor-workspace",
  tabsClassName = "task-document-tabs",
  panesClassName = "task-editor-panes",
}: HierarchyResourceEditorProps) {
  const activeTab = tabs.find(tab => tab.key === activeKey) || null;
  const compareTab = tabs.find(tab => tab.key === compareKey) || null;
  const trail = breadcrumb?.length ? breadcrumb : [category || title, activeTab?.label || "Select artifact"];
  const [bottomPanelId, setBottomPanelId] = useState<string | null>(bottomPanels[0]?.id || null);
  const activeBottomPanel = useMemo(
    () => bottomPanels.find(panel => panel.id === bottomPanelId) || bottomPanels[0] || null,
    [bottomPanels, bottomPanelId],
  );

  return <section className={`resource-view task-hierarchy-page generic-hierarchy-editor universal-artifact-editor ${className}`.trim()}>
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
      {inspector && <div className="artifact-inspector-extension">{inspector}</div>}
    </div>

    <div className="task-hierarchy-layout artifact-editor-body">
      <div className={`${treeClassName} artifact-navigator`.trim()}>{leftPane}</div>
      <div className={workspaceClassName}>
        <div className={tabsClassName}>
          {tabs.map(tab => <div className={`task-document-tab ${tab.key===activeKey?"active":""}`} key={tab.key}>
            <button onClick={()=>onActivate(tab.key)} title={tab.subtitle || tab.label}><span>{tab.kind}</span><b>{tab.label}</b>{tab.dirty&&<i>●</i>}</button>
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
        {bottomPanels.map(panel=><button key={panel.id} className={activeBottomPanel?.id===panel.id?"active":""} onClick={()=>setBottomPanelId(panel.id)}>{panel.label}{panel.badge!==undefined&&<span>{panel.badge}</span>}</button>)}
      </nav>
      <div className="artifact-bottom-content">{activeBottomPanel?.content}</div>
    </section>}

    {footer}
  </section>;
}
