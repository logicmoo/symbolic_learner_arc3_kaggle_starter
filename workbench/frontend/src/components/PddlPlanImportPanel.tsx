import { useMemo, useState } from "react";

type Workflow = {
  id: string; label?: string; description?: string; inputs?: Record<string, string>; outputs?: Record<string, string>;
  planProvenance?: { planner?: string; domain?: string; problem?: string; sourcePlan?: string };
  steps: Array<{ id: string; [key: string]: unknown }>;
};
type OperationRecord = { document?: { id?: string; label?: string; parents?: unknown[]; inputs?: Record<string, unknown> } };
type GroundedAction = { name: string; arguments: string[] };

const groundedActions = (source: string): GroundedAction[] => {
  const actions = new Map<string, GroundedAction>();
  source.split(/\r?\n/).forEach(line => {
    const match = line.match(/(?:^|:\s*)\(\s*([^\s()]+)([^()]*)\)/);
    if (!match?.[1]) return;
    const name = match[1].toLowerCase(), args = match[2].trim().split(/\s+/).filter(Boolean);
    const previous = actions.get(name);
    if (!previous || args.length > previous.arguments.length) actions.set(name, { name, arguments: args });
  });
  return [...actions.values()];
};

export function PddlPlanImportPanel({ workspaceId, workflow, onImported }: { workspaceId: string; workflow: Workflow; onImported: (workflow: Workflow) => void }) {
  const provenance = workflow.planProvenance || {};
  const [sourcePlan, setSourcePlan] = useState(provenance.sourcePlan || "");
  const [planner, setPlanner] = useState(provenance.planner || "");
  const [domain, setDomain] = useState(provenance.domain || "");
  const [problem, setProblem] = useState(provenance.problem || "");
  const [actionMap, setActionMap] = useState<Record<string, string>>({});
  const [actionBindings, setActionBindings] = useState<Record<string, Record<string, number>>>({});
  const [operations, setOperations] = useState<Array<{ id: string; label: string; inputPorts: string[] }>>([]);
  const [catalogLoaded, setCatalogLoaded] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const actions = useMemo(() => groundedActions(sourcePlan), [sourcePlan]);
  const loadOperations = async () => {
    if (catalogLoaded) return;
    setCatalogLoaded(true);
    try {
      const response = await fetch(`/api/workspaces/${encodeURIComponent(workspaceId)}/snapshot`);
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || payload.error || response.statusText);
      const records = (payload.operations || []) as OperationRecord[];
      setOperations(records.flatMap(record => record.document?.id && !(record.document.parents || []).length ? [{ id: record.document.id, label: record.document.label || record.document.id, inputPorts: Object.keys(record.document.inputs || {}) }] : []).sort((a, b) => a.label.localeCompare(b.label)));
    } catch (reason) { setMessage(`Operation catalog unavailable: ${reason instanceof Error ? reason.message : String(reason)}`); }
  };
  const convert = async () => {
    setBusy(true); setMessage("");
    try {
      const response = await fetch("/api/engine/workflows/import-pddl-plan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: workflow.id, label: workflow.label, description: workflow.description, inputs: workflow.inputs, outputs: workflow.outputs, planner, domain, problem, sourcePlan, actionMap, actionBindings }) });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || payload.error || response.statusText);
      onImported(payload.workflow as Workflow);
      setMessage(`${payload.workflow.steps.length} grounded actions converted into this unsaved Workflow. Review, validate, then Save file or Run.`);
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : String(reason)); }
    finally { setBusy(false); }
  };
  return <details className="pddl-plan-import-panel" onToggle={event => { if (event.currentTarget.open) void loadOperations(); }}>
    <summary><span>PDDL GROUNDED PLAN IMPORT</span><b>Import a planner result as this executable Workflow</b><small>Uses real workspace Operations; conversion remains an unsaved draft until you review and save it.</small></summary>
    <div className="pddl-plan-import-fields">
      <label><span>PLANNER</span><input value={planner} onChange={event => setPlanner(event.target.value)} placeholder="Fast Downward" /></label>
      <label><span>DOMAIN</span><input value={domain} onChange={event => setDomain(event.target.value)} placeholder="domain.pddl" /></label>
      <label><span>PROBLEM</span><input value={problem} onChange={event => setProblem(event.target.value)} placeholder="problem.pddl" /></label>
      <label className="wide"><span>GROUNDED PLAN</span><textarea value={sourcePlan} onChange={event => setSourcePlan(event.target.value)} placeholder={'0: (move robot room-a room-b) [1]\n1: (inspect robot room-b) [1]'} /></label>
    </div>
    <div className="pddl-action-map"><div><span>ACTION TO OPERATION MAP</span><small>Selecting an Operation maps grounded arguments to its input ports in declaration order. Review the generated step before saving.</small></div>{actions.map(action => {const binding=actionBindings[action.name]||{};return <label key={action.name}><code>{action.name}</code><select aria-label={`Operation for ${action.name}`} value={actionMap[action.name] || ""} onChange={event => {const operation=operations.find(item=>item.id===event.target.value);setActionMap(current => ({ ...current, [action.name]: event.target.value }));setActionBindings(current=>({...current,[action.name]:operation?Object.fromEntries(operation.inputPorts.slice(0,action.arguments.length).map((port,index)=>[port,index])):{}}))}}><option value="">Use {action.name}</option>{operations.map(operation => <option key={operation.id} value={operation.id}>{operation.label} · {operation.id}</option>)}</select>{Object.keys(binding).length>0&&<small>{Object.entries(binding).map(([port,index])=>`${port} ← ${action.arguments[index]??`argument ${index+1}`}`).join(" · ")}</small>}</label>})}{sourcePlan.trim() && !actions.length && <small>No grounded action forms were recognized.</small>}</div>
    <button disabled={busy || !sourcePlan.trim()} onClick={() => void convert()}>{busy ? "Converting…" : "Convert into workflow steps"}</button>
    {message && <p>{message}</p>}
  </details>;
}
