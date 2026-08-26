import {useEffect,useMemo,useState} from "react";
import "../styles/operation_editor.css";
import "../styles/operation_playground.css";
import {jsonValueToMetta} from "../lib/mettaResourceCodec";
import {InvocationDebugTrace} from "./InvocationDebugTrace";
import {ResourceSourceEditor} from "./ResourceSourceEditor";
import {UniversalExecutionControls,type RunnerPopulationMode} from "./UniversalExecutionControls";
import {AutoGrowingTextarea} from "./AutoGrowingTextarea";

type ExampleArgument={datatype?:string;label?:string;default?:unknown;options?:unknown[]};
type DatatypeContract=string|Record<string,unknown>;
export type OperationDef={id:string;label?:string;description?:string;implementation?:string;inputs?:Record<string,DatatypeContract>;outputs?:Record<string,DatatypeContract>;parameters?:Record<string,unknown>;bindings?:{prompts?:string[];promptProfiles?:string[];separator?:string};specializations?:Record<string,unknown>;preferredSpecialization?:string;example_execute?:{action?:string;arguments?:Record<string,ExampleArgument>;parameters?:Record<string,ExampleArgument>}};
type HumanField={type?:string;label?:string;prompt?:string;required?:boolean;options?:unknown[]};
export type OperationImplementationDef={id:string;label?:string;implementation:string;parameters?:{form?:Record<string,HumanField>};bindings?:{prompts?:string[];promptProfiles?:string[];separator?:string};modelSelection?:{models?:string[];strategy?:string}};
export type RunnerModel={id:string;label?:string;enabled?:boolean};
type InvocationResult={operation:{id:string;label:string;inputs:Record<string,DatatypeContract>;outputs:Record<string,DatatypeContract>};implementation:{id:string;label:string;route:string};resolvedPrompts?:Array<{promptId:string;implementationId:string;targets?:string[];version?:number}>;inputs:Record<string,unknown>;outputs:Record<string,unknown>;elapsedMs:number;debugLogPath?:string};
type RequestFailureDetail={message?:string;debugLogPath?:string};
type RuntimeArtifact={name?:string;datatype?:string;representation?:string;payload?:unknown;value?:unknown;createdAt?:string;stepId?:string;provenance?:Record<string,unknown>};
type RuntimeRun={id?:string;workflowId?:string;createdAt?:string;inputs?:Record<string,unknown>;artifacts?:RuntimeArtifact[]};
type PopulationMode=RunnerPopulationMode;
type IndexedRuntimeValue={name:string;datatype:string;representation:string;value:unknown;timestamp:number;source:"input"|"output";operationId?:string;operationLabel?:string};
type RuntimeValueDictionary={byDatatype:Map<string,IndexedRuntimeValue[]>;byRepresentation:Map<string,IndexedRuntimeValue[]>;byName:Map<string,IndexedRuntimeValue[]>;any:IndexedRuntimeValue[]};
type RuntimeValueIndex={inputs:RuntimeValueDictionary;outputs:RuntimeValueDictionary};

const workspaceValueBanks=new Map<string,RuntimeValueIndex>();

class RequestFailure extends Error{
 detail:RequestFailureDetail|string;
 constructor(message:string,detail:RequestFailureDetail|string){super(message);this.name="RequestFailure";this.detail=detail}
}

async function request(path:string,init?:RequestInit){
 const response=await fetch(path,{headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});
 const text=await response.text();let payload:any;
 try{payload=JSON.parse(text)}catch{throw new Error(text||response.statusText)}
 if(!response.ok){const detail=payload.error||payload.detail||response.statusText;const message=typeof detail==="object"&&detail?String(detail.message||JSON.stringify(detail)):String(detail);throw new RequestFailure(message,detail)}
 return payload;
}

function isTextDatatype(datatype:string){return /(^|\b)(text|string|markdown|natural.?language)(\b|$)/i.test(datatype);}
function datatypeLabel(contract:DatatypeContract):string{
 if(typeof contract==="string")return contract;
 const datatype=String(contract.datatype||contract.type||"Any");
 const representation=contract.representation?String(contract.representation):"";
 return representation?`${datatype} / ${representation}`:datatype;
}
function parseInput(datatype:string,raw:string):unknown{
 if(isTextDatatype(datatype))return raw;
 if(/image|bitmap|png|jpe?g/i.test(datatype))return raw;
 if(/^any$/i.test(datatype.trim())){const value=raw.trim();if(!value)return "";try{return JSON.parse(value)}catch{return raw}}
 const value=raw.trim();
 if(!value)return null;
 try{return JSON.parse(value)}catch{throw new Error(`Input for ${datatype} must be valid JSON (or use a Text datatype).`)}
}

function normalized(value:string){return value.toLowerCase().replace(/[^a-z0-9]+/g," ").trim()}
function emptyDictionary():RuntimeValueDictionary{return{byDatatype:new Map(),byRepresentation:new Map(),byName:new Map(),any:[]}}
function emptyValueIndex():RuntimeValueIndex{return{inputs:emptyDictionary(),outputs:emptyDictionary()}}
function valueBank(workspaceId:string):RuntimeValueIndex{let bank=workspaceValueBanks.get(workspaceId);if(!bank){bank=emptyValueIndex();workspaceValueBanks.set(workspaceId,bank)}return bank}
function contractParts(contract:DatatypeContract):{datatype:string;representation:string}{
 if(typeof contract==="string")return{datatype:contract,representation:""};
 return{datatype:String(contract.datatype||contract.type||"Any"),representation:contract.representation?String(contract.representation):""};
}
function addIndexedValue(dictionary:RuntimeValueDictionary,entry:IndexedRuntimeValue){
 const same=(candidate:IndexedRuntimeValue)=>candidate.timestamp===entry.timestamp&&candidate.name===entry.name&&candidate.datatype===entry.datatype&&candidate.representation===entry.representation&&candidate.source===entry.source&&candidate.operationId===entry.operationId;
 const add=(map:Map<string,IndexedRuntimeValue[]>,key:string)=>{const normalizedKey=normalized(key);if(!normalizedKey)return;const values=map.get(normalizedKey)||[];if(!values.some(same))values.unshift(entry);map.set(normalizedKey,values.slice(0,100))};
 add(dictionary.byDatatype,entry.datatype);add(dictionary.byRepresentation,entry.representation);add(dictionary.byName,entry.name);if(!dictionary.any.some(same))dictionary.any.unshift(entry);dictionary.any=dictionary.any.slice(0,500);
}
function rememberInvocation(workspaceId:string,operation:Pick<OperationDef,"id"|"label">,inputContracts:Record<string,DatatypeContract>,inputValues:Record<string,unknown>,outputContracts:Record<string,DatatypeContract>,outputValues:Record<string,unknown>){
 const bank=valueBank(workspaceId),timestamp=Date.now();
 for(const[name,value]of Object.entries(inputValues)){const contract=contractParts(inputContracts[name]||"Any");addIndexedValue(bank.inputs,{name,datatype:contract.datatype,representation:contract.representation,value,timestamp,source:"input",operationId:operation.id,operationLabel:operation.label||operation.id})}
 for(const[name,value]of Object.entries(outputValues)){const contract=contractParts(outputContracts[name]||"Any");addIndexedValue(bank.outputs,{name,datatype:contract.datatype,representation:contract.representation,value,timestamp,source:"output",operationId:operation.id,operationLabel:operation.label||operation.id})}
}
function ingestRuntimeRuns(workspaceId:string,runs:RuntimeRun[]){
 const bank=valueBank(workspaceId);
 for(const[runIndex,run]of runs.entries()){
  const timestamp=run.createdAt?Date.parse(run.createdAt)||-runIndex:-runIndex;
  for(const[name,value]of Object.entries(run.inputs||{}))addIndexedValue(bank.inputs,{name,datatype:"Any",representation:"",value,timestamp,source:"input"});
  for(const artifact of run.artifacts||[]){const value=artifactValue(artifact,artifact.datatype||"Any");if(value===undefined)continue;const operationId=String(artifact.provenance?.operationId||artifact.provenance?.stepId||artifact.stepId||run.workflowId||run.id||"runtime");addIndexedValue(bank.outputs,{name:artifact.name||"artifact",datatype:artifact.datatype||"Any",representation:artifact.representation||"",value,timestamp:artifact.createdAt?Date.parse(artifact.createdAt)||timestamp:timestamp,source:"output",operationId,operationLabel:operationId})}
 }
}
function valueShapeMatches(expected:string,value:unknown):boolean{
 if(expected==="any")return true;
 if(/text|string|markdown|natural language/.test(expected))return typeof value==="string";
 if(/bool/.test(expected))return typeof value==="boolean";
 if(/int|float|double|decimal|number/.test(expected))return typeof value==="number"&&Number.isFinite(value);
 if(/scene graph|object|record|json|annotation|ruleset|evidence|description/.test(expected))return value!==null&&typeof value==="object";
 if(/program|source|code/.test(expected))return typeof value==="string"||(value!==null&&typeof value==="object");
 if(/image|bitmap|png|jpeg|jpg/.test(expected)){
  if(typeof value==="string")return true;
  if(!value||typeof value!=="object"||Array.isArray(value))return false;
  return ['dataUrl','image','bitmap','url','value'].some(key=>typeof (value as Record<string,unknown>)[key]==="string");
 }
 if(/list|array|set|sequence/.test(expected))return Array.isArray(value);
 return value!==null&&typeof value==="object";
}
function artifactScore(name:string,datatype:string,artifact:IndexedRuntimeValue):number{
 const expected=normalized(datatype),inputName=normalized(name),actualType=normalized(`${artifact.datatype} ${artifact.representation}`),actualName=normalized(artifact.name);
 if(expected==="any")return actualName===inputName?12:1;
 const tokens=expected.split(" ").filter(token=>token.length>2&&!['datatype','semantic','representation'].includes(token));
 const actualAny=normalized(artifact.datatype)==="any";
 const imageCompatible=/image|bitmap|png|jpeg|jpg/.test(expected)&&/image|bitmap|png|jpeg|jpg/.test(`${actualType} ${actualName}`);
 const textCompatible=/text|string|markdown|natural language/.test(expected)&&/text|string|markdown|natural language/.test(actualType);
 const matchingTokens=tokens.filter(token=>actualType.includes(token));
 if(actualAny&&!valueShapeMatches(expected,artifact.value))return 0;
 if(!actualAny&&actualType!==expected&&!matchingTokens.length&&!imageCompatible&&!textCompatible)return 0;
 let score=actualType===expected?30:matchingTokens.length*8;
 if(actualAny)score=1;
 if(actualName===inputName)score+=15;else if(actualName.includes(inputName)||inputName.includes(actualName))score+=5;
 if(imageCompatible)score+=14;
 if(/scene|object|program|text/.test(expected)&&tokens.some(token=>actualName.includes(token)))score+=7;
 return score;
}
function artifactValue(artifact:RuntimeArtifact,datatype:string):unknown{
 const value=artifact.payload!==undefined?artifact.payload:artifact.value;
 if(value&&typeof value==='object'&&/image|bitmap|png|jpeg|jpg/i.test(datatype)){
  const record=value as Record<string,unknown>;
  for(const key of ['dataUrl','image','bitmap','url','value'])if(typeof record[key]==='string')return record[key];
 }
 return value;
}
function rawArtifactValue(value:unknown):string{return typeof value==='string'?value:JSON.stringify(value??null,null,2)}
function compatibleOutputs(dictionary:RuntimeValueDictionary,name:string,contract:DatatypeContract):IndexedRuntimeValue[]{
 const pool=dictionary.any;
 return pool.map(entry=>({entry,score:artifactScore(name,datatypeLabel(contract),entry)})).filter(candidate=>candidate.score>0).sort((a,b)=>b.entry.timestamp-a.entry.timestamp||b.score-a.score).map(candidate=>candidate.entry);
}
function emptyValueFor(contract:DatatypeContract):string{return isTextDatatype(datatypeLabel(contract))||/image|bitmap|png|jpe?g/i.test(datatypeLabel(contract))?"":"null"}

function TypedValueInput({datatype,value,options,onChange,placeholder}:{datatype:string;value:string;options?:unknown[];onChange:(value:string)=>void;placeholder?:string}){
 if(options?.length)return <select value={value} onChange={event=>onChange(event.target.value)}>{options.map(option=>{const raw=typeof option==="string"?option:JSON.stringify(option);return <option key={raw} value={raw}>{String(option)}</option>})}</select>;
 if(isTextDatatype(datatype))return <AutoGrowingTextarea className="tab-input-editor--opted-in" value={value} placeholder={placeholder} onChange={event=>onChange(event.target.value)}/>;
 if(/image|bitmap|png|jpe?g/i.test(datatype))return <div className="operation-image-input"><input type="file" accept="image/*" onChange={event=>{const file=event.target.files?.[0];if(!file)return;const reader=new FileReader();reader.onload=()=>onChange(String(reader.result||""));reader.readAsDataURL(file)}}/><textarea value={value} placeholder="Upload a bitmap or paste a data:image/... URL" onChange={event=>onChange(event.target.value)}/>{value.startsWith("data:image/")&&<img src={value} alt="Operation input preview"/>}</div>;
 if(/bool/i.test(datatype))return <input type="checkbox" checked={value==="true"} onChange={event=>onChange(String(event.target.checked))}/>;
 if(/int|float|double|decimal|number/i.test(datatype))return <input type="number" value={value} onChange={event=>onChange(event.target.value)}/>;
 return <AutoGrowingTextarea className="tab-input-editor--opted-in" value={value} placeholder={placeholder} onChange={event=>onChange(event.target.value)}/>;
}

export function OperationPlayground({workspaceId,operation,variants,models=[],workflowStep,onWorkflowStepChange,selectedImplementationVariant,onImplementationVariantChange,onDefaultImplementationChange,inputValues,expectedInputNames,onInvocationComplete,collapsed=false,onCollapsedChange}:{workspaceId:string;operation:OperationDef;variants:OperationImplementationDef[];models?:RunnerModel[];workflowStep?:Record<string,unknown>;onWorkflowStepChange?:(step:Record<string,unknown>)=>void;selectedImplementationVariant?:string;onImplementationVariantChange?:(implementationVariant:string)=>void;onDefaultImplementationChange?:(implementationVariant:string)=>void;inputValues?:Record<string,unknown>;expectedInputNames?:string[];onInvocationComplete?:(outputs:Record<string,unknown>)=>void;collapsed?:boolean;onCollapsedChange?:(collapsed:boolean)=>void}){
 const fallback:OperationImplementationDef={id:`${operation.id}.automatic_llm_fallback`,label:"Automatic LLM fallback (ASICloud asi1-mini)",implementation:"llm.complete"};
 const direct:OperationImplementationDef|null=operation.implementation?{id:operation.id,label:operation.label||operation.id,implementation:operation.implementation}:null;
 const concreteVariants=variants.length?variants:direct?[direct]:[];
 const runnableVariants=[...concreteVariants,fallback];
 const preferred=runnableVariants.some(item=>item.id===selectedImplementationVariant)?selectedImplementationVariant!:runnableVariants.some(item=>item.id===operation.preferredSpecialization)?operation.preferredSpecialization!:runnableVariants[0]?.id||"";
 const defaults=(values:Record<string,ExampleArgument>)=>Object.fromEntries(Object.entries(values).map(([name,arg])=>[name,typeof arg.default==="string"?arg.default:JSON.stringify(arg.default??"")]));
 const[variant,setVariant]=useState(preferred),[defaultsOpen,setDefaultsOpen]=useState(false),[cascadeOpen,setCascadeOpen]=useState(false),[rawInputs,setRawInputs]=useState<Record<string,string>>(()=>defaults(operation.example_execute?.arguments||{})),[rawParameters,setRawParameters]=useState<Record<string,string>>(()=>defaults(operation.example_execute?.parameters||{})),[result,setResult]=useState<InvocationResult|null>(null),[error,setError]=useState<string|null>(null),[running,setRunning]=useState(false),[populating,setPopulating]=useState<PopulationMode|null>(null),[populationMessage,setPopulationMessage]=useState<string|null>(null);
 const[debugLogPath,setDebugLogPath]=useState<string|null>(null),[debugLog,setDebugLog]=useState<string>(""),[humanValues,setHumanValues]=useState<Record<string,string>>({});
 const[galleryIndex,setGalleryIndex]=useState(0),[galleryPlaying,setGalleryPlaying]=useState(false),[gallerySpeed,setGallerySpeed]=useState(650),[activePane,setActivePane]=useState<"run"|"edit">("run"),[workflowStepSource,setWorkflowStepSource]=useState(()=>JSON.stringify(workflowStep||{},null,2)),[workflowStepSourceValid,setWorkflowStepSourceValid]=useState(true),[workflowStepError,setWorkflowStepError]=useState("");
 const inputs=useMemo(()=>Object.entries(operation.inputs||{}),[operation.id,operation.inputs]);
 const missingBoundInputs=(expectedInputNames||inputs.map(([name])=>name)).filter(name=>inputValues!==undefined&&!(name in inputValues));
 const parameters=useMemo(()=>Object.entries(operation.parameters||{}),[operation.id,operation.parameters]);
 const outputs=Object.entries(operation.outputs||{});
 const galleryArtifact=result?Object.values(result.outputs||{}).find(value=>typeof value==="object"&&value!==null&&String((value as Record<string,unknown>).kind||"").includes("gallery")) as Record<string,unknown>|undefined:undefined;
 const galleryEntries=Array.isArray(galleryArtifact?.entries)?galleryArtifact.entries as Array<Record<string,unknown>>:[];
 const galleryAnimation=typeof galleryArtifact?.animation==="string"?galleryArtifact.animation:"";
 const assetUrl=(path:string)=>path.startsWith("data:")||path.startsWith("http")?path:`/api/workspaces/${encodeURIComponent(workspaceId)}/asset?path=${encodeURIComponent(path)}`;
 const visualOutputs=result?Object.entries(result.outputs||{}).flatMap(([name,value])=>{
  const contract=datatypeLabel(operation.outputs?.[name]||"Any");
  if(typeof value==="string"&&/image|bitmap|png|jpe?g/i.test(contract)&&value)return[{name,path:value}];
  if(value&&typeof value==="object"&&!Array.isArray(value)){
   const record=value as Record<string,unknown>;
   return ["frame_path","initial_screenshot","next_screenshot","reset_screenshot"].flatMap(field=>typeof record[field]==="string"&&record[field]?[{name:`${name}.${field}`,path:String(record[field])}]:[]);
  }
  return[];
 }).filter((item,index,items)=>items.findIndex(candidate=>candidate.path===item.path)===index):[];
 const galleryFrame=galleryEntries[Math.min(galleryIndex,Math.max(0,galleryEntries.length-1))];
 const operationEditorUrl=`?workspace=${encodeURIComponent(workspaceId)}&view=operations&resource=${encodeURIComponent(operation.id)}`;
 const invocationVariant=runnableVariants.length===1?runnableVariants[0].id:variant;
 const selected=runnableVariants.find(item=>item.id===invocationVariant)||null;
 const humanForm=selected?.implementation==="human.await_input"?(selected.parameters?.form||{}):{};
 const humanFields=Object.entries(humanForm);
 const deducedModel=selected?.modelSelection?.models?.[0]||(selected?.id===fallback.id?"asicloud-asi1-mini":"");
 const[selectedModel,setSelectedModel]=useState(deducedModel);
 const clearInvocationResult=()=>{setResult(null);setError(null);setDebugLogPath(null);setDebugLog("")};
 const updateInput=(name:string,value:string)=>{setRawInputs(current=>({...current,[name]:value}));setPopulationMessage(null);clearInvocationResult()};
 const updateParameter=(name:string,value:string)=>{setRawParameters(current=>({...current,[name]:value}));clearInvocationResult()};
 const loadDebugLog=async(path:string)=>{
  setDebugLogPath(path);setDebugLog("Loading complete invocation trace...");
  try{const payload=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations/debug-log?path=${encodeURIComponent(path)}`);setDebugLog(String(payload.content||""))}
  catch(reason){setDebugLog(`Debug trace could not be loaded: ${reason instanceof Error?reason.message:String(reason)}`)}
 };
 const populateInputs=async(populationMode:PopulationMode,targetInput?:string)=>{
  setPopulating(populationMode);setPopulationMessage(null);clearInvocationResult();
  try{
   if(populationMode==="sample_input"){
    const sample=defaults(operation.example_execute?.arguments||{});setRawInputs(current=>({...current,...Object.fromEntries(inputs.filter(([name])=>!targetInput||name===targetInput).map(([name])=>[name,sample[name]??""]))}));setPopulationMessage(targetInput?`Restored ${targetInput}'s sample input value.`:"Restored this operation's sample input values.");return;
   }
   if(populationMode==="empty_null"){
    setRawInputs(current=>({...current,...Object.fromEntries(inputs.filter(([name])=>!targetInput||name===targetInput).map(([name,contract])=>[name,emptyValueFor(contract)]))}));setPopulationMessage(targetInput?`Set ${targetInput} to its empty/null value.`:"Set text and image inputs to empty values; other inputs to null.");return;
   }
   const responses=await Promise.allSettled([request(`/api/goal-runs?workspace_id=${encodeURIComponent(workspaceId)}&limit=100`),request(`/api/engine/runs?workspace_id=${encodeURIComponent(workspaceId)}&limit=100`)]);
   const goalRuns:RuntimeRun[]=responses[0].status==='fulfilled'&&Array.isArray(responses[0].value.goalRuns)?responses[0].value.goalRuns.map((item:any)=>item.workflowRun as RuntimeRun):[];
   const engineRuns:RuntimeRun[]=responses[1].status==='fulfilled'&&Array.isArray(responses[1].value.runs)?responses[1].value.runs as RuntimeRun[]:[];
   ingestRuntimeRuns(workspaceId,[...goalRuns,...engineRuns]);
   const populated:Record<string,string>={...rawInputs};const matched:string[]=[];
   for(const[name,contract]of inputs.filter(([name])=>!targetInput||name===targetInput)){const candidates=compatibleOutputs(valueBank(workspaceId).outputs,name,contract);const chosen=populationMode==="random_outputs"?candidates[Math.floor(Math.random()*candidates.length)]:candidates[0];if(!chosen)continue;populated[name]=rawArtifactValue(chosen.value);matched.push(`${name} <- ${chosen.operationLabel||chosen.operationId||"runtime"}.${chosen.name} (${chosen.datatype}${chosen.representation?` / ${chosen.representation}`:""})`)}
   setRawInputs(populated);setPopulationMessage(matched.length?`${populationMode==="random_outputs"?"Randomly loaded":"Loaded latest"} ${matched.join(" | ")} from outputs produced by any operation in this workspace.`:'No compatible outputs from any operation in this workspace were found. Existing inputs were left unchanged.');
  }catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setPopulating(null)}
 };
 const run=async(implementationVariant?:string)=>{
  setRunning(true);setError(null);setResult(null);setDebugLogPath(null);setDebugLog("");
  try{
   if(selected?.implementation==="human.await_input"){
    const humanOutputs=Object.fromEntries(humanFields.map(([name,field])=>[name,parseInput(field.type||"Text",humanValues[name]||"")]));
    const invocation:InvocationResult={operation:{id:operation.id,label:operation.label||operation.id,inputs:operation.inputs||{},outputs:operation.outputs||{}},implementation:{id:selected.id,label:selected.label||selected.id,route:selected.implementation},inputs:{},outputs:humanOutputs,elapsedMs:0};
    rememberInvocation(workspaceId,operation,operation.inputs||{},{},operation.outputs||{},humanOutputs);setResult(invocation);onInvocationComplete?.(humanOutputs);onCollapsedChange?.(true);return;
   }
   const values:Record<string,unknown>={};
   for(const[name,datatype]of inputs){const raw=rawInputs[name]??"",label=datatypeLabel(datatype),options=operation.example_execute?.arguments?.[name]?.options,matched=options?.find(option=>(typeof option==="string"?option:JSON.stringify(option))===raw);values[name]=matched!==undefined?matched:parseInput(label,raw)}
   const parameterValues:Record<string,unknown>={};
   for(const[name,fallback]of parameters){const raw=rawParameters[name];if(raw===undefined||raw==="")parameterValues[name]=fallback;else try{parameterValues[name]=JSON.parse(raw)}catch{parameterValues[name]=raw}}
   const payload=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations/${encodeURIComponent(operation.id)}/invoke`,{method:"POST",body:JSON.stringify({...(implementationVariant?{implementationVariant}:{}),...(selectedModel?{modelSelection:{models:[selectedModel],strategy:"single"}}:{}),inputs:values,parameters:parameterValues})});
   const invocation=payload as InvocationResult;rememberInvocation(workspaceId,operation,operation.inputs||{},values,operation.outputs||{},invocation.outputs||{});setResult(invocation);onInvocationComplete?.(invocation.outputs||{});onCollapsedChange?.(true);if(invocation.debugLogPath)await loadDebugLog(invocation.debugLogPath);
  }catch(reason){setError(reason instanceof Error?reason.message:String(reason));if(reason instanceof RequestFailure&&typeof reason.detail==="object"&&reason.detail.debugLogPath)await loadDebugLog(reason.detail.debugLogPath)}finally{setRunning(false)}
 };
 useEffect(()=>{setVariant(preferred);setSelectedModel(deducedModel);setRawInputs(defaults(operation.example_execute?.arguments||{}));setRawParameters(defaults(operation.example_execute?.parameters||{}));setHumanValues({});setPopulationMessage(null);setResult(null);setError(null);setDebugLogPath(null);setDebugLog("")},[operation.id]);
 useEffect(()=>{if(!inputValues)return;setRawInputs(current=>({...current,...Object.fromEntries(Object.entries(inputValues).map(([name,value])=>[name,typeof value==="string"?value:JSON.stringify(value)]))}))},[inputValues]);
 useEffect(()=>{setGalleryIndex(0);setGalleryPlaying(false)},[galleryArtifact]);
 useEffect(()=>{if(!galleryPlaying||galleryEntries.length<2)return;const timer=window.setInterval(()=>setGalleryIndex(current=>(current+1)%galleryEntries.length),gallerySpeed);return()=>window.clearInterval(timer)},[galleryPlaying,gallerySpeed,galleryEntries.length]);
 useEffect(()=>{setWorkflowStepSource(JSON.stringify(workflowStep||{},null,2));setWorkflowStepSourceValid(true);setWorkflowStepError("")},[workflowStep]);
 if(collapsed)return <section className="operation-playground operation-playground-collapsed"><button type="button" className="operation-playground-summary" onClick={()=>onCollapsedChange?.(false)}><span>COMPLETED</span><b>{operation.label||operation.id}</b><small>{result?`${result.implementation.label} · ${result.elapsedMs} ms`:"Debug details collapsed"}</small><em>Expand · rerun available</em></button></section>;
 return <section className={`operation-playground operation-pane-${activePane}`}>
  {workflowStep&&<nav className="operation-step-tabs" aria-label={`${String(workflowStep.label||workflowStep.id||operation.label||operation.id)} workflow step panes`}><button type="button" className={activePane==="run"?"active":""} onClick={()=>setActivePane("run")}>Run Workflow Step</button><button type="button" className={activePane==="edit"?"active":""} onClick={()=>setActivePane("edit")}>Edit Workflow Step</button></nav>}
  {workflowStep&&activePane==="edit"&&<section className="operation-step-editor-pane"><span>WORKFLOW STEP EDITOR</span><h3>{String(workflowStep.label||workflowStep.id||operation.label||operation.id)}</h3><p>Edit this step's dependencies, bindings, outputs, parameters, probe behavior, or selected Operation implementation. MeTTa and JSON are synchronized views of this same Workflow Step. Saving the workflow persists applied changes.</p><ResourceSourceEditor value={workflowStepSource} onChange={value=>{setWorkflowStepSource(value);setWorkflowStepError("")}} onValidityChange={setWorkflowStepSourceValid} label="Edit this Workflow Step directly" showEnablement={false}/><div className="operation-step-editor-actions"><button type="button" disabled={!workflowStepSourceValid} title={workflowStepSourceValid?"Apply this valid source to the parent Workflow":"Fix the syntax error before applying this Workflow Step"} onClick={()=>{try{const next=JSON.parse(workflowStepSource) as Record<string,unknown>;onWorkflowStepChange?.(next);setWorkflowStepError("")}catch{setWorkflowStepError("Workflow Step must be valid MeTTa or JSON before it can be applied.")}}}>Apply to Workflow</button><a className="operation-editor-link" href={operationEditorUrl}>Edit underlying Operation</a></div>{workflowStepError&&<small className="operation-step-editor-error">{workflowStepError}</small>}</section>}
   <div className="operation-playground-grid">
   <label className="operation-playground-field operation-playground-operation"><span>OPERATION <a className="operation-editor-link" href={operationEditorUrl}>Edit Operation</a></span><select value={operation.id} disabled><option value={operation.id}>{operation.label||operation.id}</option></select><small>Open the full editor for alternatives, default selection, tabs, split comparison, raw source, save, and the executable playground.</small></label>
   <div className={`operation-defaults-band ${defaultsOpen?"expanded":""}`}><button type="button" className="operation-defaults-toggle" aria-expanded={defaultsOpen} onClick={()=>setDefaultsOpen(value=>!value)}><span>OPERATION DEFAULTS</span><code>Implementation: {concreteVariants.find(item=>item.id===operation.preferredSpecialization)?.label||operation.preferredSpecialization||"planner-selected"}</code><code>Model: {deducedModel||"Declared / deduced model"}</code><em>{defaultsOpen?"Collapse":"Change defaults"}</em></button>{defaultsOpen&&<div className="operation-defaults-editor"><label className="operation-playground-field"><span>DEFAULT IMPLEMENTATION</span><select value={operation.preferredSpecialization||""} disabled={!onDefaultImplementationChange} onChange={event=>onDefaultImplementationChange?.(event.target.value)}><option value="">planner-selected</option>{concreteVariants.map(item=><option key={item.id} value={item.id}>{item.label||item.id} · {item.implementation}</option>)}</select><small>{onDefaultImplementationChange?"Updates the Operation document. Use the editor Save button to persist it.":"Open this Operation in the Operations editor to change and save its defaults."}</small></label><label className="operation-playground-field"><span>DEFAULT MODEL</span><input value={deducedModel||"Declared / deduced model"} disabled/><small>The default model belongs to the selected implementation resource; open that implementation to edit it.</small></label></div>}</div>
   <div className={`operation-cascade-band ${cascadeOpen?"expanded":""}`}><button type="button" className="operation-cascade-toggle" aria-expanded={cascadeOpen} onClick={()=>setCascadeOpen(value=>!value)}><span>RUN WITH · WORKFLOW CASCADE</span><code>Implementation: {selected?.label||invocationVariant||"Operation default"}</code><code>Model: {selectedModel||"Operation default"}</code><em>{cascadeOpen?"Collapse":"Change overrides"}</em></button>{cascadeOpen&&<div className="operation-cascade-editor"><div className="operation-run-route"><label className="operation-playground-field"><span>SUB-IMPLEMENTATION · WORKFLOW CASCADE</span><select value={invocationVariant} disabled={runnableVariants.length===1} onChange={event=>{setVariant(event.target.value);onImplementationVariantChange?.(event.target.value);clearInvocationResult()}}>{runnableVariants.map(item=><option key={item.id} value={item.id}>{item.label||item.id} · {item.implementation}</option>)}</select><small>This sub-implementation overrides the Operation default for the pending cascade without changing the saved Operation.</small></label><div className="operation-run-actions"><button type="button" title="Run the operation's saved default implementation" onClick={()=>run()} disabled={running}>{running?"Running…":"Run Default"}</button><button className="primary" type="button" title="Run the selected workflow-cascade overrides" onClick={()=>run(invocationVariant)} disabled={running||!invocationVariant}>{running?"Running…":"▶ Run Selected"}</button></div></div><label className="operation-playground-field"><span>MODEL · WORKFLOW CASCADE</span><select value={selectedModel} onChange={event=>setSelectedModel(event.target.value)}><option value="">Use Operation default</option>{models.filter(item=>item.enabled!==false).map(item=><option key={item.id} value={item.id}>{item.label||item.id}</option>)}</select><small>{selectedModel?`The pending cascade overrides the Operation model with ${selectedModel}.`:"The pending cascade uses the Operation's default model."}</small></label></div>}</div>
   {humanFields.length>0&&<div className="human-input-contract"><div className="llm-subhead"><div><span>HUMAN INPUT</span><b>{selected?.label||"Provide the requested value"}</b></div></div>{humanFields.map(([name,field])=><label className="operation-playground-field" key={`human:${name}`}><span>{field.label||name} <em>{field.type||"Text"}</em></span><TypedValueInput datatype={field.type||"Text"} value={humanValues[name]||""} options={field.options} placeholder={field.prompt||`Enter ${name}…`} onChange={value=>setHumanValues(current=>({...current,[name]:value}))}/><small>{field.prompt}</small></label>)}</div>}
   <UniversalExecutionControls actions={<button className="primary workflow-step-button operation-execute-step" type="button" title={missingBoundInputs.length?`Waiting for upstream inputs: ${missingBoundInputs.join(", ")}`:humanFields.length?"Submit this human input and advance the workflow":workflowStep?"Run this Workflow Step with the displayed inputs":"Run this Operation with the displayed inputs"} onClick={()=>void run(invocationVariant)} disabled={running||!invocationVariant||missingBoundInputs.length>0||humanFields.some(([name,field])=>field.required!==false&&!String(humanValues[name]||"").trim())}>{running?"Running step…":missingBoundInputs.length?"Waiting for inputs…":humanFields.length?"▶ Submit Human Input":workflowStep?"▶ Run Workflow Step":"▶ Run Operation"}</button>} populating={populating} inputCount={inputs.length} onPopulate={mode=>populateInputs(mode)}/>
   {inputs.map(([name,datatype])=>{const example=operation.example_execute?.arguments?.[name],label=datatypeLabel(datatype);return <div className="operation-playground-field operation-input-field" key={name}><span>INPUT · {name} <em>{label}</em></span><div className="operation-input-population"><button type="button" disabled={populating!==null} onClick={()=>populateInputs("last_outputs",name)}>Last</button><button type="button" disabled={populating!==null} onClick={()=>populateInputs("random_outputs",name)}>Random</button><button type="button" disabled={populating!==null} onClick={()=>populateInputs("sample_input",name)}>Sample</button><button type="button" disabled={populating!==null} onClick={()=>populateInputs("empty_null",name)}>Empty/Null</button></div><TypedValueInput datatype={label} value={rawInputs[name]??""} options={example?.options} placeholder={isTextDatatype(label)?`Enter ${name}…`:/^any$/i.test(label.trim())?"Enter text or a JSON value…":`Enter ${label} as JSON…`} onChange={value=>updateInput(name,value)}/></div>})}
   {parameters.map(([name,fallback])=>{const example=operation.example_execute?.parameters?.[name],datatype=example?.datatype||typeof fallback;return <label className="operation-playground-field" key={`parameter:${name}`}><span>PARAMETER · {name} <em>{datatype}</em></span><TypedValueInput datatype={datatype} value={rawParameters[name]??(typeof fallback==="string"?fallback:JSON.stringify(fallback??""))} options={example?.options} placeholder={`Configure ${name}…`} onChange={value=>updateParameter(name,value)}/></label>})}
  </div>
  {populationMessage&&<div className="operation-population-status">{populationMessage}</div>}
  <div className="operation-playground-contract"><span>OUTPUT(S)</span>{outputs.map(([name,datatype])=><code key={name}>{name}: {datatypeLabel(datatype)}</code>)}</div>
  {error&&<div className="demo-notice"><b>Invocation failed</b><span>{error}</span></div>}
  {result&&visualOutputs.length>0&&<div className="operation-visual-outputs"><div className="inspection-gallery-heading"><span>CAPTURED IMAGE{visualOutputs.length===1?"":"S"}</span><small>{visualOutputs.length} filesystem-backed visual output{visualOutputs.length===1?"":"s"}</small></div>{visualOutputs.map(item=><figure key={`${item.name}:${item.path}`}><img src={assetUrl(item.path)} alt={`${operation.label||operation.id} ${item.name}`}/><figcaption><b>{item.name}</b><code>{item.path}</code></figcaption></figure>)}</div>}
  {result&&<div className="operation-playground-result"><div><span>RESULT</span><b>{result.implementation.label}</b><small>{result.implementation.route} · {result.elapsedMs} ms</small></div><pre>{jsonValueToMetta(result.outputs)}</pre>{galleryArtifact&&<div className="inspection-gallery"><div className="inspection-gallery-heading"><span>GALLERY RESOURCE</span><b>{String(galleryArtifact.label||"Gallery Resource")}</b><small>{galleryEntries.length} entries · same artifact available to downstream AI</small></div>{galleryFrame&&<section className="inspection-gallery-player"><div className="inspection-gallery-player-frame">{typeof galleryFrame.image==="string"&&galleryFrame.image?<img src={assetUrl(galleryFrame.image)} alt={String(galleryFrame.title||`Gallery frame ${galleryIndex+1}`)}/>:<span>NO IMAGE</span>}</div><div className="inspection-gallery-player-caption"><b>{String(galleryFrame.title||`Frame ${galleryIndex+1}`)}</b><small>{String(galleryFrame.description||"")}</small><span>{galleryIndex+1} / {galleryEntries.length}</span></div><div className="inspection-gallery-player-controls"><button onClick={()=>setGalleryIndex(current=>(current-1+galleryEntries.length)%galleryEntries.length)} aria-label="Previous game frame">◀</button><button className="primary" onClick={()=>setGalleryPlaying(value=>!value)}>{galleryPlaying?"Pause":"Play"}</button><button onClick={()=>setGalleryIndex(current=>(current+1)%galleryEntries.length)} aria-label="Next game frame">▶</button><label><span>Frame</span><input aria-label="Replay frame" type="range" min="0" max={Math.max(0,galleryEntries.length-1)} value={galleryIndex} onChange={event=>setGalleryIndex(Number(event.target.value))}/></label><label><span>Speed</span><select aria-label="Replay speed" value={gallerySpeed} onChange={event=>setGallerySpeed(Number(event.target.value))}><option value={1500}>Slow · 1.5s</option><option value={1000}>1.0s</option><option value={650}>Normal · 0.65s</option><option value={350}>Fast · 0.35s</option><option value={150}>Very fast · 0.15s</option></select></label></div></section>}{galleryAnimation&&<figure className="inspection-gallery-animation"><img src={assetUrl(galleryAnimation)} alt={`${String(galleryArtifact.label||"Gallery")} animated replay`}/><figcaption>Exported animated replay · initial frame through move {String(galleryArtifact.move_count||Math.max(0,galleryEntries.length-1))}</figcaption></figure>}<div className="inspection-gallery-grid">{galleryEntries.map((entry,index)=><article className={index===galleryIndex?"active":""} key={index} onClick={()=>setGalleryIndex(index)}><div className="inspection-gallery-image">{typeof entry.image==="string"&&entry.image?<img src={assetUrl(entry.image)} alt={String(entry.title||`Gallery item ${index+1}`)}/>:<span>NO IMAGE</span>}</div><b>{String(entry.title||`Item ${index+1}`)}</b>{Boolean(entry.description)&&<small>{String(entry.description)}</small>}</article>)}</div></div>}{result.resolvedPrompts&&result.resolvedPrompts.length>0&&<div className="operation-playground-prompts"><span>RESOLVED PROMPTS</span>{result.resolvedPrompts.map(item=><code key={`${item.promptId}:${item.implementationId}`}>{item.promptId} → {item.implementationId}</code>)}</div>}</div>}
  {debugLogPath&&<InvocationDebugTrace path={debugLogPath} content={debugLog}/>}
 </section>;
}
