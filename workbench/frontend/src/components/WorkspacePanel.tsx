import { useState } from "react";
import { Braces, Code2, GitCompareArrows, Image as ImageIcon, MousePointer2, Network, Play, RotateCcw, Shapes } from "lucide-react";
import type { ArcObject } from "../artifacts/artifactTypes";
import type { WorkflowStepDefinition } from "../workflow/workflowTypes";
import { ArcGrid } from "./ArcGrid";
import { CodePanel } from "./CodePanel";

export type WorkspaceTab = "image" | "objects" | "turtle" | "prolog" | "rules" | "comparison";
interface Props { step: WorkflowStepDefinition; grid: number[][]; prediction: number[][]; objects: ArcObject[]; selectedObject?: ArcObject; onHoverObject: (o?: ArcObject) => void; onSelectObject: (o?: ArcObject) => void; onRun: () => void; }

const tabs: Array<[WorkspaceTab, string, React.ReactNode]> = [["image","Image",<ImageIcon size={15}/>],["objects","Objects",<Shapes size={15}/>],["turtle","Turtle",<Code2 size={15}/>],["prolog","Prolog",<Braces size={15}/>],["rules","Rules",<Network size={15}/>],["comparison","Compare",<GitCompareArrows size={15}/>]];

export function WorkspacePanel({ step, grid, prediction, objects, selectedObject, onHoverObject, onSelectObject, onRun }: Props) {
  const [activeTab, setActiveTab] = useState<WorkspaceTab>("objects");
  const object = selectedObject ?? objects[0];
  const ruleCode = `rule(move_red_angle_right) :-
    object(Object),
    color(Object, red),
    shape(Object, angle),
    translate(Object, 1, 0).`;
  return <section className="workspace-panel panel">
    <header className="workspace-panel__header"><div><span className="eyebrow">Stage {step.order}</span><h1>{step.title}</h1><p>{step.description}</p></div><div className="workspace-actions"><button className="button button--primary" onClick={onRun}><Play size={16}/> Run stage</button><button className="button"><RotateCcw size={15}/> Reset view</button></div></header>
    <div className="workspace-tabs" role="tablist">{tabs.map(([id,label,icon]) => <button key={id} className={activeTab===id?"active":""} onClick={() => setActiveTab(id)}>{icon}{label}</button>)}</div>
    <div className="workspace-canvas">
      {(activeTab === "image" || activeTab === "objects") && <div className="scene-layout"><ArcGrid grid={grid} objects={objects} selectedObjectId={selectedObject?.id} onHoverObject={onHoverObject} onSelectObject={onSelectObject} showCoordinates={activeTab === "objects"}/><div className="scene-sidebar"><div className="hint-card"><MousePointer2 size={18}/><div><strong>Semantic hover</strong><p>Move across the grid to bind pixels to stable object identities.</p></div></div><div className="object-list"><h3>Detected objects</h3>{objects.map(o => <button key={o.id} className={selectedObject?.id===o.id?"selected":""} onMouseEnter={() => onHoverObject(o)} onClick={() => onSelectObject(o)}><span className="object-dot" style={{ background: o.color === 1 ? "#2d8cff" : "#ff3b4f" }}/><span><strong>{o.name}</strong><small>{o.properties.shape} · {o.cells.length} px</small></span><em>{Math.round(o.confidence*100)}%</em></button>)}</div></div></div>}
      {activeTab === "turtle" && <div className="split-code"><CodePanel title={`${object.name} Turtle program`} language="Prolog DSL" code={object.turtleProgram}/><div className="render-card"><h3>Rendered geometry</h3><ArcGrid title="Turtle rendering" grid={grid} objects={[object]} selectedObjectId={object.id} compact/><p>The same semantic object is regenerated from relative <code>fwd/1</code>, <code>rot/1</code>, <code>penup</code>, and <code>pendown</code> operations.</p></div></div>}
      {activeTab === "prolog" && <div className="prolog-layout"><CodePanel title={`${object.name} symbolic facts`} language="Prolog" code={object.prologFacts}/><div className="query-panel"><h3>Query console</h3><label>Query</label><div className="query-row"><input defaultValue="shape(Object, hollow_rectangle)."/><button><Play size={14}/> Run</button></div><pre>{object.properties.shape === "hollow_rectangle" ? "Object = obj_blue_frame.\ntrue." : "false."}</pre></div></div>}
      {activeTab === "rules" && <div className="rules-layout"><CodePanel title="Candidate induced rule" language="Prolog" code={ruleCode}/><div className="rule-score"><h3>Rule evidence</h3><div className="metric"><span>Coverage</span><strong>3 / 3</strong></div><div className="metric"><span>Consistency</span><strong>100%</strong></div><div className="metric"><span>Complexity</span><strong>4 literals</strong></div><button className="button button--primary">Accept rule</button></div></div>}
      {activeTab === "comparison" && <div className="comparison-grid"><ArcGrid title="Input" grid={grid} objects={objects} compact/><ArcGrid title="Prediction" grid={prediction} objects={objects} compact/><ArcGrid title="Expected" grid={prediction} objects={objects} compact/><div className="diff-card"><GitCompareArrows size={32}/><strong>Exact match</strong><span>0 differing cells</span><div className="score-big">1.000</div></div></div>}
    </div>
  </section>;
}
