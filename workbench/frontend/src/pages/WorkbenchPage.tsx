import { useMemo, useState } from "react";
import type { ArcObject } from "../artifacts/artifactTypes";
import { AppHeader } from "../components/AppHeader";
import { ArtifactInspector } from "../components/ArtifactInspector";
import { WorkflowRail } from "../components/WorkflowRail";
import { WorkspacePanel } from "../components/WorkspacePanel";
import { workflowSteps } from "../workflow/workflowSteps";
import type { WorkflowStepId, WorkflowStepStatus } from "../workflow/workflowTypes";

const grid = [[0,0,0,0,0,0,0,0],[0,1,1,1,0,2,0,0],[0,1,0,1,0,2,0,0],[0,1,1,1,0,2,2,0],[0,0,0,0,0,0,0,0]];
const prediction = [[0,0,0,0,0,0,0,0],[0,1,1,1,0,0,2,0],[0,1,0,1,0,0,2,0],[0,1,1,1,0,0,2,2],[0,0,0,0,0,0,0,0]];
const objects: ArcObject[] = [
  { id:"obj_blue_frame", name:"Blue frame", color:1, cells:[[1,1],[2,1],[3,1],[1,2],[3,2],[1,3],[2,3],[3,3]], confidence:.97, properties:{shape:"hollow_rectangle",width:3,height:3,pixelCount:8,hollow:true}, turtleProgram:`object(obj_blue_frame).

turtle(obj_blue_frame, [
    penup,
    set_pos(1, 1),
    setcolor(blue),
    pendown,
    fwd(2),
    rot(90),
    fwd(2),
    rot(90),
    fwd(2),
    rot(90),
    fwd(2)
]).`, prologFacts:`object(obj_blue_frame).
color(obj_blue_frame, blue).
shape(obj_blue_frame, hollow_rectangle).
bounds(obj_blue_frame, 1, 1, 3, 3).
pixel_count(obj_blue_frame, 8).
hollow(obj_blue_frame).` },
  { id:"obj_red_angle", name:"Red angle", color:2, cells:[[5,1],[5,2],[5,3],[6,3]], confidence:.94, properties:{shape:"angle",width:2,height:3,pixelCount:4,hollow:false}, turtleProgram:`object(obj_red_angle).

turtle(obj_red_angle, [
    penup,
    set_pos(5, 1),
    setcolor(red),
    pendown,
    fwd(2),
    rot(-90),
    fwd(1)
]).`, prologFacts:`object(obj_red_angle).
color(obj_red_angle, red).
shape(obj_red_angle, angle).
bounds(obj_red_angle, 5, 1, 2, 3).
pixel_count(obj_red_angle, 4).` }
];

export function WorkbenchPage() {
  const [selectedStepId,setSelectedStepId] = useState<WorkflowStepId>("turtlize_objects");
  const [selectedObject,setSelectedObject] = useState<ArcObject|undefined>(objects[0]);
  const [hoveredObject,setHoveredObject] = useState<ArcObject|undefined>();
  const [statuses,setStatuses] = useState<Record<WorkflowStepId,WorkflowStepStatus>>(() => Object.fromEntries(workflowSteps.map((s,i)=>[s.id,i<1?"completed":i===1?"ready":"idle"])) as Record<WorkflowStepId,WorkflowStepStatus>);
  const step = useMemo(()=>workflowSteps.find(s=>s.id===selectedStepId)!,[selectedStepId]);
  const run = () => { setStatuses(v=>({...v,[selectedStepId]:"running"})); setTimeout(()=>setStatuses(v=>({...v,[selectedStepId]:"completed"})),700); };
  const reset = () => { setSelectedStepId("grab_image_source"); setStatuses(Object.fromEntries(workflowSteps.map((s,i)=>[s.id,i===0?"ready":"idle"])) as Record<WorkflowStepId,WorkflowStepStatus>); };
  const activeObject = hoveredObject ?? selectedObject;
  return <div className="workbench"><AppHeader projectName="MeTTaSymbolicLearnerWorkbench" taskName="ls20" level={0} step={21} onRun={run} onReset={reset}/><main className="workbench__body"><WorkflowRail steps={workflowSteps} selectedStepId={selectedStepId} statuses={statuses} onSelectStep={setSelectedStepId}/><WorkspacePanel step={step} grid={grid} prediction={prediction} objects={objects} selectedObject={activeObject} onHoverObject={setHoveredObject} onSelectObject={setSelectedObject} onRun={run}/><ArtifactInspector object={activeObject}/></main><footer className="status-bar"><span><b>Ready</b> · scene-ls20-0-21</span><span>8 × 5 grid · 2 objects · cursor linked across representations</span></footer></div>;
}
