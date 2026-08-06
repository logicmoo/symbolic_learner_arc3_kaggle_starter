import { Check, Circle, Loader2, AlertTriangle } from "lucide-react";
import type { WorkflowStepDefinition, WorkflowStepId, WorkflowStepStatus } from "../workflow/workflowTypes";

interface Props { steps: WorkflowStepDefinition[]; selectedStepId: WorkflowStepId; statuses: Record<WorkflowStepId, WorkflowStepStatus>; onSelectStep: (id: WorkflowStepId) => void; }

function StatusIcon({ status }: { status: WorkflowStepStatus }) {
  if (status === "running") return <Loader2 size={15} className="spin" />;
  if (status === "completed") return <Check size={15} />;
  if (status === "failed" || status === "warning") return <AlertTriangle size={15} />;
  return <Circle size={12} />;
}

export function WorkflowRail({ steps, selectedStepId, statuses, onSelectStep }: Props) {
  return <aside className="workflow-rail panel">
    <div className="panel-heading"><div><span className="eyebrow">Pipeline</span><h2>Workflow</h2></div><span className="badge">{steps.length} stages</span></div>
    <nav>{steps.map(step => <button key={step.id} className={`workflow-step ${selectedStepId === step.id ? "workflow-step--selected" : ""}`} onClick={() => onSelectStep(step.id)} title={step.description}>
      <span className="workflow-step__number">{step.order}</span>
      <span className="workflow-step__text"><strong>{step.shortTitle}</strong><small>{step.consumes.slice(0,2).join(" + ")} → {step.produces.slice(0,2).join(" + ")}</small></span>
      <span className={`workflow-step__status status-${statuses[step.id]}`}><StatusIcon status={statuses[step.id]} /></span>
    </button>)}</nav>
  </aside>;
}
