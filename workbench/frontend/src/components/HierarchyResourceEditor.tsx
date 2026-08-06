import type { ReactNode } from "react";
import "../styles/task_editor.css";

type EditorTab = {
  key: string;
  kind: string;
  label: string;
  dirty?: boolean;
};

type HierarchyResourceEditorProps = {
  eyebrow: string;
  title: string;
  description: string;
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
  footer?: ReactNode;
};

export function HierarchyResourceEditor({
  eyebrow,
  title,
  description,
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
  footer,
}: HierarchyResourceEditorProps) {
  return <section className="resource-view task-hierarchy-page generic-hierarchy-editor">
    <div className="resource-heading">
      <div><span>{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>
      {headerActions && <div className="studio-actions">{headerActions}</div>}
    </div>

    {notice}
    {error && <div className="backend-error"><b>{title}</b><span>{error}</span>{onDismissError && <button onClick={onDismissError}>×</button>}</div>}

    <div className="task-hierarchy-layout">
      <div className="task-tree-pane">{leftPane}</div>
      <div className="task-editor-workspace">
        <div className="task-document-tabs">
          {tabs.map(tab => <div className={`task-document-tab ${tab.key===activeKey?"active":""}`} key={tab.key}>
            <button onClick={()=>onActivate(tab.key)}><span>{tab.kind}</span><b>{tab.label}</b>{tab.dirty&&<i>●</i>}</button>
            <button className="close" onClick={()=>onClose(tab.key)}>×</button>
          </div>)}
        </div>
        <div className={`task-editor-panes ${compareKey?"split":"single"}`}>
          {activeKey ? renderEditor(activeKey,false) : (emptyEditor || <div className="studio-empty">Select a resource.</div>)}
          {compareKey ? renderEditor(compareKey,true) : null}
        </div>
      </div>
    </div>

    {footer}
  </section>;
}
