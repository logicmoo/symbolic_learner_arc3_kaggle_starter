import { useMemo, useState } from "react";

type Workflow = {
  id: string; label?: string; description?: string; inputs?: Record<string, string>; outputs?: Record<string, string>;
  planProvenance?: { planner?: string; domain?: string; problem?: string; sourcePlan?: string };
  steps: Array<{ id: string; [key: string]: unknown }>;
};
type OperationRecord = { document?: { id?: string; label?: string; parents?: unknown[] } };

const groundedActions = (source: string) => [...new Set(source.split(/\r?\n/).flatMap(line => {
  const match = line.match(/(?:^|:\s*)\(\s*([^\s()]+)/);
  return match?.[1] ? [match[1].toLowerCase()] : [];
}))];

export function PddlPlanImportPanel({ workspaceId, workflow, onImported }: { workspaceId: string; workflow: Workflow; onImported: (workflow: Workflow) => void }) {
  const provenance = workflow.planProvenance || {};
  const [sourcePlan, setSourcePlan] = useState(provenance.sourcePlan || "");
  const [planner, setPlanner] = useState(provenance.planner || "");
  const [domain, setDomain] = useState(provenance.domain || "");
  const [problem, setProblem] = useState(provenance.problem || "");
  const [actionMap, setActionMap] = useState<Record<string, string>>({});
  const [operations, setOperations] = useState<Array<{ id: string; label: string }>>([]);
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
      setOperations(records.flatMap(record => record.document?.id && !(record.document.parents || []).length ? [{ id: record.document.id, label: record.document.label || record.document.id }] : []).sort((a, b) => a.label.localeCompare(b.label)));
    } catch (reason) { setMessage(`Operation catalog unavailable: ${reason instanceof Error ? reason.message : String(reason)}`); }
  };
  const convert = async () => {
    setBusy(true); setMessage("");
    try {
      const response = await fetch("/api/engine/workflows/import-pddl-plan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: workflow.id, label: workflow.label, description: workflow.description, inputs: workflow.inputs, outputs: workflow.outputs, planner, domain, problem, sourcePlan, actionMap }) });
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
    <div className="pddl-action-map"><div><span>ACTION TO OPERATION MAP</span><small>Unmapped names use their normalized PDDL action name as the Operation ID.</small></div>{actions.map(action => <label key={action}><code>{action}</code><select aria-label={`Operation for ${action}`} value={actionMap[action] || ""} onChange={event => setActionMap(current => ({ ...current, [action]: event.target.value }))}><option value="">Use {action}</option>{operations.map(operation => <option key={operation.id} value={operation.id}>{operation.label} · {operation.id}</option>)}</select></label>)}{sourcePlan.trim() && !actions.length && <small>No grounded action forms were recognized.</small>}</div>
    <button disabled={busy || !sourcePlan.trim()} onClick={() => void convert()}>{busy ? "Converting…" : "Convert into workflow steps"}</button>
    {message && <p>{message}</p>}
  </details>;
}
