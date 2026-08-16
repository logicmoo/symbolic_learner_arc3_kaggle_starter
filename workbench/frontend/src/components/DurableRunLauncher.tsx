import type { ReactNode } from "react";

import "../styles/durable_run_launcher.css";
import { ThreeStateAccordionMember, type AccordionDisplayMode } from "./ThreeStateAccordion";

type DurableRunLauncherProps = {
  status: string;
  statusDetail: string;
  blocked: boolean;
  fields: ReactNode;
  actions: ReactNode;
  displayMode?: AccordionDisplayMode;
  onDisplayModeChange?: (mode: AccordionDisplayMode) => void;
};

export function DurableRunLauncher({ status, statusDetail, blocked, fields, actions, displayMode = "scroll", onDisplayModeChange }: DurableRunLauncherProps) {
  return (
    <ThreeStateAccordionMember
      stackId="left-stack"
      initialIndex={0}
      initialPlacementVersion="runner-first-v1"
      label="WORKFLOW RUNNER"
      value={status}
      detail={statusDetail}
      mode={displayMode}
      onChange={(nextMode) => onDisplayModeChange?.(nextMode)}
      baseClass="durable-run-launcher panel-frame"
      scrollSize="360px"
      itemHeader={<button type="button" className="durable-run-launcher-head" onClick={() => onDisplayModeChange?.("strip")}>
          <div>
            <span>WORKFLOW RUNNER</span>
            <h2>Configure and launch a durable run</h2>
            <p>Choose a workflow, provide its inputs, then validate or launch it.</p>
          </div>
          <div className={`durable-run-launcher-state ${blocked ? "blocked" : "ready"}`}>
            <b>{status}</b>
            <small>{statusDetail}</small>
          </div>
      </button>}
      footer={<div className="durable-run-launcher-actions">{actions}</div>}
    >
        <div className="durable-run-launcher-scroll">
          <div className="durable-run-launcher-fields">{fields}</div>
        </div>
    </ThreeStateAccordionMember>
  );
}
