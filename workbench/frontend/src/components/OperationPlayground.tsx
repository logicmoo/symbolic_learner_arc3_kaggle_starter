import {useEffect,useMemo,useState} from "react";
import "../styles/operation_editor.css";
import "../styles/operation_playground.css";
import {jsonValueToMetta} from "../lib/mettaResourceCodec";
import {InvocationDebugTrace} from "./InvocationDebugTrace";
import {UniversalExecutionControls,type RunnerPopulationMode} from "./UniversalExecutionControls";

type ExampleArgument={datatype?:string;label?:string;default?:unknown;options?:unknown[]};
type DatatypeContract=string|Record<string,unknown>;
type OperationDef={id:string;label?:string;implementation?:string;inputs?:Record<string,DatatypeContract>;outputs?:Record<string,DatatypeContract>;parameters?:Record<string,unknown>;children?:string[];preferredChild?:string;example_execute?:{action?:string;arguments?:Record<string,ExampleArgument>;parameters?:Record<string,ExampleArgument>}};
type OperationImplementationDef={id:string;label?:string;implementation:string;modelSelection?:{models?:string[];strategy?:string}};
type RunnerModel={id:string;label?:string;enabled?:boolean};
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
 if(isTextDatatype(datatype))return <textarea value={value} placeholder={placeholder} onChange={event=>onChange(event.target.value)}/>;
 if(/image|bitmap|png|jpe?g/i.test(datatype))return <div className="operation-image-input"><input type="file" accept="image/*" onChange={event=>{const file=event.target.files?.[0];if(!file)return;const reader=new FileReader();reader.onload=()=>onChange(String(reader.result||""));reader.readAsDataURL(file)}}/><textarea value={value} placeholder="Upload a bitmap or paste a data:image/... URL" onChange={event=>onChange(event.target.value)}/>{value.startsWith("data:image/")&&<img src={value} alt="Operation input preview"/>}</div>;
 if(/bool/i.test(datatype))return <input type="checkbox" checked={value==="true"} onChange={event=>onChange(String(event.target.checked))}/>;
 if(/int|float|double|decimal|number/i.test(datatype))return <input type="number" value={value} onChange={event=>onChange(event.target.value)}/>;
 return <textarea value={value} placeholder={placeholder} onChange={event=>onChange(event.target.value)}/>;
}

export function OperationPlayground({workspaceId,operation,variants,models=[]}:{workspaceId:string;operation:OperationDef;variants:OperationImplementationDef[];models?:RunnerModel[]}){
 const fallback:OperationImplementationDef={id:`${operation.id}.automatic_llm_fallback`,label:"Automatic LLM fallback (openrouter/free)",implementation:"llm.complete"};
 const direct:OperationImplementationDef|null=operation.implementation?{id:operation.id,label:operation.label||operation.id,implementation:operation.implementation}:null;
 const concreteVariants=variants.length?variants:direct?[direct]:[];
 const runnableVariants=[...concreteVariants,fallback];
 const preferred=runnableVariants.some(item=>item.id===operation.preferredChild)?operation.preferredChild!:runnableVariants[0]?.id||"";
 const defaults=(values:Record<string,ExampleArgument>)=>Object.fromEntries(Object.entries(values).map(([name,arg])=>[name,typeof arg.default==="string"?arg.default:JSON.stringify(arg.default??"")]));
 const[variant,setVariant]=useState(preferred),[rawInputs,setRawInputs]=useState<Record<string,string>>(()=>defaults(operation.example_execute?.arguments||{})),[rawParameters,setRawParameters]=useState<Record<string,string>>(()=>defaults(operation.example_execute?.parameters||{})),[result,setResult]=useState<InvocationResult|null>(null),[error,setError]=useState<string|null>(null),[running,setRunning]=useState(false),[populating,setPopulating]=useState<PopulationMode|null>(null),[populationMessage,setPopulationMessage]=useState<string|null>(null);
 const[debugLogPath,setDebugLogPath]=useState<string|null>(null),[debugLog,setDebugLog]=useState<string>("");
 const inputs=useMemo(()=>Object.entries(operation.inputs||{}),[operation.id,operation.inputs]);
 const parameters=useMemo(()=>Object.entries(operation.parameters||{}),[operation.id,operation.parameters]);
 const outputs=Object.entries(operation.outputs||{});
 const invocationVariant=runnableVariants.length===1?runnableVariants[0].id:variant;
 const selected=runnableVariants.find(item=>item.id===invocationVariant)||null;
 const deducedModel=selected?.modelSelection?.models?.[0]||(selected?.id===fallback.id?"openrouter/free":"");
 const[selectedModel,setSelectedModel]=useState(deducedModel);
 const clearInvocationResult=()=>{setResult(null);setError(null);setDebugLogPath(null);setDebugLog("")};
 const updateInput=(name:string,value:string)=>{setRawInputs(current=>({...current,[name]:value}));setPopulationMessage(null);clearInvocationResult()};
 const updateParameter=(name:string,value:string)=>{setRawParameters(current=>({...current,[name]:value}));clearInvocationResult()};
 const loadDebugLog=async(path:string)=>{
  setDebugLogPath(path);setDebugLog("Loading complete invocation trace...");
  try{const payload=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations/debug-log?path=${encodeURIComponent(path)}`);setDebugLog(String(payload.content||""))}
  catch(reason){setDebugLog(`Debug trace could not be loaded: ${reason instanceof Error?reason.message:String(reason)}`)}
 };
 const populateInputs=async(populationMode:PopulationMode)=>{
  setPopulating(populationMode);setPopulationMessage(null);clearInvocationResult();
  try{
   if(populationMode==="sample_input"){
    const sample=defaults(operation.example_execute?.arguments||{});setRawInputs(Object.fromEntries(inputs.map(([name])=>[name,sample[name]??""])));setPopulationMessage("Restored this operation's sample input values.");return;
   }
   if(populationMode==="empty_null"){
    setRawInputs(Object.fromEntries(inputs.map(([name,contract])=>[name,emptyValueFor(contract)])));setPopulationMessage("Set text and image inputs to empty values; other inputs to null.");return;
   }
   const responses=await Promise.allSettled([request(`/api/goal-runs?workspace_id=${encodeURIComponent(workspaceId)}&limit=100`),request(`/api/engine/runs?workspace_id=${encodeURIComponent(workspaceId)}&limit=100`)]);
   const goalRuns:RuntimeRun[]=responses[0].status==='fulfilled'&&Array.isArray(responses[0].value.goalRuns)?responses[0].value.goalRuns.map((item:any)=>item.workflowRun as RuntimeRun):[];
   const engineRuns:RuntimeRun[]=responses[1].status==='fulfilled'&&Array.isArray(responses[1].value.runs)?responses[1].value.runs as RuntimeRun[]:[];
   ingestRuntimeRuns(workspaceId,[...goalRuns,...engineRuns]);
   const populated:Record<string,string>={...rawInputs};const matched:string[]=[];
   for(const[name,contract]of inputs){const candidates=compatibleOutputs(valueBank(workspaceId).outputs,name,contract);const chosen=populationMode==="random_outputs"?candidates[Math.floor(Math.random()*candidates.length)]:candidates[0];if(!chosen)continue;populated[name]=rawArtifactValue(chosen.value);matched.push(`${name} <- ${chosen.operationLabel||chosen.operationId||"runtime"}.${chosen.name} (${chosen.datatype}${chosen.representation?` / ${chosen.representation}`:""})`)}
   setRawInputs(populated);setPopulationMessage(matched.length?`${populationMode==="random_outputs"?"Randomly loaded":"Loaded latest"} ${matched.join(" | ")} from outputs produced by any operation in this workspace.`:'No compatible outputs from any operation in this workspace were found. Existing inputs were left unchanged.');
  }catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setPopulating(null)}
 };
 const run=async(implementationVariant?:string)=>{
  setRunning(true);setError(null);setResult(null);setDebugLogPath(null);setDebugLog("");
  try{
   const values:Record<string,unknown>={};
   for(const[name,datatype]of inputs){const raw=rawInputs[name]??"",label=datatypeLabel(datatype),options=operation.example_execute?.arguments?.[name]?.options,matched=options?.find(option=>(typeof option==="string"?option:JSON.stringify(option))===raw);values[name]=matched!==undefined?matched:parseInput(label,raw)}
   const parameterValues:Record<string,unknown>={};
   for(const[name,fallback]of parameters){const raw=rawParameters[name];if(raw===undefined||raw==="")parameterValues[name]=fallback;else try{parameterValues[name]=JSON.parse(raw)}catch{parameterValues[name]=raw}}
   const payload=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations/${encodeURIComponent(operation.id)}/invoke`,{method:"POST",body:JSON.stringify({...(implementationVariant?{implementationVariant}:{}),...(selectedModel?{modelSelection:{models:[selectedModel],strategy:"single"}}:{}),inputs:values,parameters:parameterValues})});
   const invocation=payload as InvocationResult;rememberInvocation(workspaceId,operation,operation.inputs||{},values,operation.outputs||{},invocation.outputs||{});setResult(invocation);if(invocation.debugLogPath)await loadDebugLog(invocation.debugLogPath);
  }catch(reason){setError(reason instanceof Error?reason.message:String(reason));if(reason instanceof RequestFailure&&typeof reason.detail==="object"&&reason.detail.debugLogPath)await loadDebugLog(reason.detail.debugLogPath)}finally{setRunning(false)}
 };
 useEffect(()=>{setVariant(preferred);setSelectedModel(deducedModel);setRawInputs(defaults(operation.example_execute?.arguments||{}));setRawParameters(defaults(operation.example_execute?.parameters||{}));setPopulationMessage(null);setResult(null);setError(null);setDebugLogPath(null);setDebugLog("")},[operation.id]);
 return <section className="operation-playground">
  <UniversalExecutionControls title="OPERATION PLAYGROUND" description="Invoke the abstract operation with its default or a one-off route" actions={<><button type="button" title="Run the operation's saved default implementation" onClick={()=>run()} disabled={running}>{running?"Running…":"Run Default"}</button><button className="primary" type="button" title="Run the one-off implementation selected below" onClick={()=>run(invocationVariant)} disabled={running||!invocationVariant}>{running?"Running…":"▶ Run Selected"}</button></>} populating={populating} inputCount={inputs.length} onPopulate={populateInputs}/>
  <div className="operation-playground-grid">
   <div className="operation-run-route"><label className="operation-playground-field"><span>RUN WITH (THIS RUN ONLY)</span><select value={invocationVariant} disabled={runnableVariants.length===1} onChange={event=>{setVariant(event.target.value);clearInvocationResult()}}>{runnableVariants.map(item=><option key={item.id} value={item.id}>{item.label||item.id} · {item.implementation}</option>)}</select><small>{selected?.id===fallback.id?"Uses the automatic openrouter/free LLM fallback for this run only. The saved default implementation is unchanged.":selected?`Executes ${selected.implementation} for this run. The saved default implementation is unchanged.`:"Select how this invocation should run."}</small></label><div className="operation-run-actions"><button type="button" title="Run the operation's saved default implementation" onClick={()=>run()} disabled={running}>{running?"Running…":"Run Default"}</button><button className="primary" type="button" title="Run the one-off implementation selected at left" onClick={()=>run(invocationVariant)} disabled={running||!invocationVariant}>{running?"Running…":"▶ Run Selected"}</button></div></div>
   <label className="operation-playground-field"><span>OPERATION</span><select value={operation.id} disabled><option value={operation.id}>{operation.label||operation.id}</option></select><small>The open operation is selected first; other resource runners may offer compatible operations here.</small></label>
   <label className="operation-playground-field"><span>MODEL · ONE-OFF</span><select value={selectedModel} onChange={event=>setSelectedModel(event.target.value)}><option value="">Declared / deduced model</option>{models.filter(item=>item.enabled!==false).map(item=><option key={item.id} value={item.id}>{item.label||item.id}</option>)}</select><small>{selectedModel?`This run uses ${selectedModel} without changing the operation.`:"Uses the implementation's declared or deduced model."}</small></label>
   {inputs.map(([name,datatype])=>{const example=operation.example_execute?.arguments?.[name],label=datatypeLabel(datatype);return <label className="operation-playground-field" key={name}><span>INPUT · {name} <em>{label}</em></span><TypedValueInput datatype={label} value={rawInputs[name]??""} options={example?.options} placeholder={isTextDatatype(label)?`Enter ${name}…`:/^any$/i.test(label.trim())?"Enter text or a JSON value…":`Enter ${label} as JSON…`} onChange={value=>updateInput(name,value)}/></label>})}
   {parameters.map(([name,fallback])=>{const example=operation.example_execute?.parameters?.[name],datatype=example?.datatype||typeof fallback;return <label className="operation-playground-field" key={`parameter:${name}`}><span>PARAMETER · {name} <em>{datatype}</em></span><TypedValueInput datatype={datatype} value={rawParameters[name]??(typeof fallback==="string"?fallback:JSON.stringify(fallback??""))} options={example?.options} placeholder={`Configure ${name}…`} onChange={value=>updateParameter(name,value)}/></label>})}
  </div>
  {populationMessage&&<div className="operation-population-status">{populationMessage}</div>}
  <div className="operation-playground-contract"><span>OUTPUT CONTRACT</span>{outputs.map(([name,datatype])=><code key={name}>{name}: {datatypeLabel(datatype)}</code>)}</div>
  {error&&<div className="demo-notice"><b>Invocation failed</b><span>{error}</span></div>}
  {result&&<div className="operation-playground-result"><div><span>RESULT</span><b>{result.implementation.label}</b><small>{result.implementation.route} · {result.elapsedMs} ms</small></div><pre>{jsonValueToMetta(result.outputs)}</pre>{result.resolvedPrompts&&result.resolvedPrompts.length>0&&<div className="operation-playground-prompts"><span>RESOLVED PROMPTS</span>{result.resolvedPrompts.map(item=><code key={`${item.promptId}:${item.implementationId}`}>{item.promptId} → {item.implementationId}</code>)}</div>}</div>}
  {debugLogPath&&<InvocationDebugTrace path={debugLogPath} content={debugLog}/>}
 </section>;
}
