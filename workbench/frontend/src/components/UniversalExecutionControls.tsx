import type {ReactNode} from "react";

export type RunnerPopulationMode="last_outputs"|"random_outputs"|"sample_input"|"empty_null";

export function UniversalExecutionControls({title,description,actions,populating,inputCount,onPopulate}:{title?:string;description?:string;actions?:ReactNode;populating:RunnerPopulationMode|null;inputCount:number;onPopulate:(mode:RunnerPopulationMode)=>void}){
 const button=(mode:RunnerPopulationMode,label:string,titleText:string)=><button type="button" title={titleText} onClick={()=>onPopulate(mode)} disabled={populating!==null||inputCount===0}>{populating===mode?"Loading…":label}</button>;
 return <>
  {(title||description||actions)&&<div className="llm-subhead universal-runner-heading"><div>{title&&<span>{title}</span>}{description&&<b>{description}</b>}</div><div className="operation-run-actions runner-actions-top">{actions}</div></div>}
  <div className="operation-population-actions universal-population-actions"><span>POPULATE INPUTS</span>{inputCount===0?<em>No inputs to populate</em>:<>{button("last_outputs","Last Output","Use the newest compatible output produced by any resource in this workspace")}{button("random_outputs","Random Output","Use a random compatible output produced by any resource in this workspace")}{button("sample_input","Sample's Input","Restore this resource's sample input")}{button("empty_null","Empty/Null","Clear text and image inputs and set structured inputs to null")}</>}</div>
 </>;
}
