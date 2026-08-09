import {useEffect,useMemo,useState} from "react";
import "../styles/operation_editor.css";
import "../styles/operation_playground.css";
import {jsonValueToMetta} from "../lib/mettaResourceCodec";

type ExampleArgument={datatype?:string;label?:string;default?:unknown;options?:unknown[]};
type DatatypeContract=string|Record<string,unknown>;
type OperationDef={id:string;label?:string;implementation?:string;inputs?:Record<string,DatatypeContract>;outputs?:Record<string,DatatypeContract>;parameters?:Record<string,unknown>;children?:string[];preferredChild?:string;example_execute?:{action?:string;arguments?:Record<string,ExampleArgument>;parameters?:Record<string,ExampleArgument>}};
type OperationImplementationDef={id:string;label?:string;implementation:string};
type InvocationResult={operation:{id:string;label:string;inputs:Record<string,DatatypeContract>;outputs:Record<string,DatatypeContract>};implementation:{id:string;label:string;route:string};resolvedPrompts?:Array<{promptId:string;implementationId:string;targets?:string[];version?:number}>;inputs:Record<string,unknown>;outputs:Record<string,unknown>;elapsedMs:number;debugLogPath?:string};
type RequestFailureDetail={message?:string;debugLogPath?:string};

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

function TypedValueInput({datatype,value,options,onChange,placeholder}:{datatype:string;value:string;options?:unknown[];onChange:(value:string)=>void;placeholder?:string}){
 if(options?.length)return <select value={value} onChange={event=>onChange(event.target.value)}>{options.map(option=>{const raw=typeof option==="string"?option:JSON.stringify(option);return <option key={raw} value={raw}>{String(option)}</option>})}</select>;
 if(isTextDatatype(datatype))return <textarea value={value} placeholder={placeholder} onChange={event=>onChange(event.target.value)}/>;
 if(/image|bitmap|png|jpe?g/i.test(datatype))return <div className="operation-image-input"><input type="file" accept="image/*" onChange={event=>{const file=event.target.files?.[0];if(!file)return;const reader=new FileReader();reader.onload=()=>onChange(String(reader.result||""));reader.readAsDataURL(file)}}/><textarea value={value} placeholder="Upload a bitmap or paste a data:image/... URL" onChange={event=>onChange(event.target.value)}/>{value.startsWith("data:image/")&&<img src={value} alt="Operation input preview"/>}</div>;
 if(/bool/i.test(datatype))return <input type="checkbox" checked={value==="true"} onChange={event=>onChange(String(event.target.checked))}/>;
 if(/int|float|double|decimal|number/i.test(datatype))return <input type="number" value={value} onChange={event=>onChange(event.target.value)}/>;
 return <textarea value={value} placeholder={placeholder} onChange={event=>onChange(event.target.value)}/>;
}

export function OperationPlayground({workspaceId,operation,variants}:{workspaceId:string;operation:OperationDef;variants:OperationImplementationDef[]}){
 const fallback:OperationImplementationDef={id:`${operation.id}.automatic_llm_fallback`,label:"Automatic LLM fallback (openrouter/free)",implementation:"llm.complete"};
 const direct:OperationImplementationDef|null=operation.implementation?{id:operation.id,label:operation.label||operation.id,implementation:operation.implementation}:null;
 const runnableVariants=variants.length?variants:direct?[direct]:[fallback];
 const preferred=runnableVariants.some(item=>item.id===operation.preferredChild)?operation.preferredChild!:runnableVariants[0]?.id||"";
 const defaults=(values:Record<string,ExampleArgument>)=>Object.fromEntries(Object.entries(values).map(([name,arg])=>[name,typeof arg.default==="string"?arg.default:JSON.stringify(arg.default??"")]));
 const[variant,setVariant]=useState(preferred),[rawInputs,setRawInputs]=useState<Record<string,string>>(()=>defaults(operation.example_execute?.arguments||{})),[rawParameters,setRawParameters]=useState<Record<string,string>>(()=>defaults(operation.example_execute?.parameters||{})),[result,setResult]=useState<InvocationResult|null>(null),[error,setError]=useState<string|null>(null),[running,setRunning]=useState(false);
 const[debugLogPath,setDebugLogPath]=useState<string|null>(null),[debugLog,setDebugLog]=useState<string>("");
 const inputs=useMemo(()=>Object.entries(operation.inputs||{}),[operation.id,operation.inputs]);
 const parameters=useMemo(()=>Object.entries(operation.parameters||{}),[operation.id,operation.parameters]);
 const outputs=Object.entries(operation.outputs||{});
 const invocationVariant=runnableVariants.length===1?runnableVariants[0].id:variant;
 const selected=runnableVariants.find(item=>item.id===invocationVariant)||null;
 const loadDebugLog=async(path:string)=>{
  setDebugLogPath(path);setDebugLog("Loading complete invocation trace...");
  try{const payload=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations/debug-log?path=${encodeURIComponent(path)}`);setDebugLog(String(payload.content||""))}
  catch(reason){setDebugLog(`Debug trace could not be loaded: ${reason instanceof Error?reason.message:String(reason)}`)}
 };
 const run=async()=>{
  setRunning(true);setError(null);setResult(null);setDebugLogPath(null);setDebugLog("");
  try{
   const values:Record<string,unknown>={};
   for(const[name,datatype]of inputs){const raw=rawInputs[name]??"",label=datatypeLabel(datatype),options=operation.example_execute?.arguments?.[name]?.options,matched=options?.find(option=>(typeof option==="string"?option:JSON.stringify(option))===raw);values[name]=matched!==undefined?matched:parseInput(label,raw)}
   const parameterValues:Record<string,unknown>={};
   for(const[name,fallback]of parameters){const raw=rawParameters[name];if(raw===undefined||raw==="")parameterValues[name]=fallback;else try{parameterValues[name]=JSON.parse(raw)}catch{parameterValues[name]=raw}}
   const payload=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations/${encodeURIComponent(operation.id)}/invoke`,{method:"POST",body:JSON.stringify({implementationVariant:invocationVariant||undefined,inputs:values,parameters:parameterValues})});
   const invocation=payload as InvocationResult;setResult(invocation);if(invocation.debugLogPath)await loadDebugLog(invocation.debugLogPath);
  }catch(reason){setError(reason instanceof Error?reason.message:String(reason));if(reason instanceof RequestFailure&&typeof reason.detail==="object"&&reason.detail.debugLogPath)await loadDebugLog(reason.detail.debugLogPath)}finally{setRunning(false)}
 };
 useEffect(()=>{setVariant(preferred);setRawInputs(defaults(operation.example_execute?.arguments||{}));setRawParameters(defaults(operation.example_execute?.parameters||{}));setResult(null);setError(null);setDebugLogPath(null);setDebugLog("")},[operation.id]);
 return <section className="operation-playground">
  <div className="llm-subhead"><div><span>OPERATION PLAYGROUND</span><b>Invoke the abstract operation with a concrete variant</b></div><button className="primary" onClick={run} disabled={running||!invocationVariant}>{running?"Running…":"▶ Run"}</button></div>
  <div className="operation-playground-grid">
   <label className="operation-playground-field"><span>RUN VARIANT</span><select value={invocationVariant} disabled={runnableVariants.length===1} onChange={event=>{setVariant(event.target.value);setResult(null);setError(null)}}>{runnableVariants.map(item=><option key={item.id} value={item.id}>{item.label||item.id} · {item.implementation}</option>)}</select><small>{variants.length?`${selected?`Executes ${selected.implementation}`:"Select an implementation"}. This does not change the saved preferred implementation.`:direct?`Executes the operation's declared ${direct.implementation} implementation directly.`:"No concrete implementation exists, so the runtime derives a prompt from this operation and uses openrouter/free."}</small></label>
   {inputs.map(([name,datatype])=>{const example=operation.example_execute?.arguments?.[name],label=datatypeLabel(datatype);return <label className="operation-playground-field" key={name}><span>INPUT · {name} <em>{label}</em></span><TypedValueInput datatype={label} value={rawInputs[name]??""} options={example?.options} placeholder={isTextDatatype(label)?`Enter ${name}…`:/^any$/i.test(label.trim())?"Enter text or a JSON value…":`Enter ${label} as JSON…`} onChange={value=>setRawInputs(current=>({...current,[name]:value}))}/></label>})}
   {parameters.map(([name,fallback])=>{const example=operation.example_execute?.parameters?.[name],datatype=example?.datatype||typeof fallback;return <label className="operation-playground-field" key={`parameter:${name}`}><span>PARAMETER · {name} <em>{datatype}</em></span><TypedValueInput datatype={datatype} value={rawParameters[name]??(typeof fallback==="string"?fallback:JSON.stringify(fallback??""))} options={example?.options} placeholder={`Configure ${name}…`} onChange={value=>setRawParameters(current=>({...current,[name]:value}))}/></label>})}
  </div>
  <div className="operation-playground-contract"><span>OUTPUT CONTRACT</span>{outputs.map(([name,datatype])=><code key={name}>{name}: {datatypeLabel(datatype)}</code>)}</div>
  {error&&<div className="demo-notice"><b>Invocation failed</b><span>{error}</span></div>}
  {result&&<div className="operation-playground-result"><div><span>RESULT</span><b>{result.implementation.label}</b><small>{result.implementation.route} · {result.elapsedMs} ms</small></div><pre>{jsonValueToMetta(result.outputs)}</pre>{result.resolvedPrompts&&result.resolvedPrompts.length>0&&<div className="operation-playground-prompts"><span>RESOLVED PROMPTS</span>{result.resolvedPrompts.map(item=><code key={`${item.promptId}:${item.implementationId}`}>{item.promptId} → {item.implementationId}</code>)}</div>}</div>}
  {debugLogPath&&<details className="operation-debug-trace" open><summary><span>COMPLETE DEBUG TRACE</span><code>{debugLogPath}</code></summary><pre>{debugLog}</pre></details>}
 </section>;
}
