import { useState } from "react";


type Workflow = {
  id: string; label?: string; description?: string; inputs?: Record<string, string>; outputs?: Record<string, string>;
  planProvenance?: { planner?: string; domain?: string; problem?: string; sourcePlan?: string };
  steps: Array<{ id: string; [key: string]: unknown }>;
};


export function PddlPlanImportPanel({ workflow, onImported }: { workflow: Workflow; onImported: (workflow: Workflow) => void }) {
  const [actionMapSource, setActionMapSource] = useState("{}");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const convert = async () => {
    setBusy(true); setMessage("");
    try {
      const actionMap = JSON.parse(actionMapSource);
      const provenance = workflow.planProvenance || {};
      const response = await fetch("/api/engine/workflows/import-pddl-plan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: workflow.id, label: workflow.label, description: workflow.description, inputs: workflow.inputs, outputs: workflow.outputs, ...provenance, actionMap }) });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || payload.error || response.statusText);
      onImported(payload.workflow as Workflow);
      setMessage(`${payload.workflow.steps.length} grounded actions converted. Review and save the Workflow when ready.`);
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : String(reason)); }
    finally { setBusy(false); }
  };
  return <section className="pddl-plan-import-panel"><div><span>PDDL GROUNDED PLAN IMPORT</span><b>Map planner actions to abstract Operations</b><small>The conversion is a draft: it does not save or run the Workflow.</small></div><label><span>ACTION MAP · JSON</span><textarea value={actionMapSource} onChange={event => setActionMapSource(event.target.value)} placeholder={'{"move":"navigation.move"}'} /></label><button disabled={busy || !workflow.planProvenance?.sourcePlan?.trim()} onClick={() => void convert()}>{busy ? "Converting…" : "Convert grounded plan to steps"}</button>{message && <p>{message}</p>}</section>;
}
