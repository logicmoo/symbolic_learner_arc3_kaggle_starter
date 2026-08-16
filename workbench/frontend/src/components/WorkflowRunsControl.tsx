import type { ReactNode } from "react";

import "../styles/workflow_runs_control.css";
import "../styles/durable_runs_accordion.css";
import { ThreeStateAccordionMember, type AccordionDisplayMode } from "./ThreeStateAccordion";

type WorkflowRunsControlProps = {
  workflowRuns: boolean;
  modern: boolean;
  displayMode: AccordionDisplayMode;
  children: ReactNode;
  value?: string;
  detail?: string;
  onDisplayModeChange?: (mode: AccordionDisplayMode) => void;
  accessories?: ReactNode;
  footer?: ReactNode;
};

export function WorkflowRunsControl({ workflowRuns, modern, displayMode, children, value, detail, onDisplayModeChange, accessories, footer }: WorkflowRunsControlProps) {
  if (!workflowRuns) return <div className="runtime-record-list-pane">{children}</div>;
  if (!modern) return <ThreeStateAccordionMember stackId="right-stack" label="WORKFLOW RUNS" value={value} detail={detail} mode={displayMode} onChange={onDisplayModeChange!} baseClass="durable-runs-accordion panel-frame" scrollSize="380px" accessories={accessories} footer={footer}>{children}</ThreeStateAccordionMember>;
  return <section className={`workflow-runs-control panel-frame ${displayMode === "strip" ? "minimized" : ""}`}>{children}</section>;
}
