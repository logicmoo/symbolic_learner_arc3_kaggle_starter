import {useEffect,useMemo,useState} from "react";
import "../styles/operation_editor.css";
import "../styles/operation_playground.css";

type ExampleArgument={datatype?:string;label?:string;default?:unknown};
type OperationDef={id:string;label?:string;inputs?:Record<string,string>;outputs?:Record<string,string>;parameters?:Record<string,unknown>;children?:string[];preferredChild?:string;example_execute?:{action?:string;arguments?:Record<string,ExampleArgument>;parameters?:Record<string,ExampleArgument>}};
type OperationImplementationDef={id:string;label?:string;implementation:string};
type InvocationResult={operation:{id:string;label:string;inputs:Record<string,string>;outputs:Record<string,string>};implementation:{id:string;label:string;route:string};resolvedPrompts?:Array<{promptId:string;implementationId:string;targets?:string[];version?:number}>;inputs:Record<string,unknown>;outputs:Record<string,unknown>;elapsedMs:number};

async function request(path:string,init?:RequestInit){const response=await fetch(path,{headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});const text=await response.text();let payload:any;try{payload=JSON.parse(text)}catch{throw new Error(text||response.statusText)}if(!response.ok)throw new Error(payload.error||payload.detail||response.statusText);return payload;}

function isTextDatatype(datatype:string){return /(^|\b)(text|string|markdown|natural.?language)(\b|$)/i.test(datatype);}
function parseInput(datatype:string,raw:string):unknown{
 if(isTextDatatype(datatype))return raw;
 const value=raw.trim();
 if(!value)return null;
 try{return JSON.parse(value)}catch{throw new Error(`Input for ${datatype} must be valid JSON (or use a Text datatype).`)}
}

export function OperationPlayground({workspaceId,operation,variants}:{workspaceId:string;operation:OperationDef;variants:OperationImplementationDef[]}){
 const preferred=variants.some(item=>item.id===operation.preferredChild)?operation.preferredChild!:variants[0]?.id||"";
 const defaults=(values:Record<string,ExampleArgument>)=>Object.fromEntries(Object.entries(values).map(([name,arg])=>[name,typeof arg.default==="string"?arg.default:JSON.stringify(arg.default??"")]));
 const[variant,setVariant]=useState(preferred),[rawInputs,setRawInputs]=useState<Record<string,string>>(()=>defaults(operation.example_execute?.arguments||{})),[rawParameters,setRawParameters]=useState<Record<string,string>>(()=>defaults(operation.example_execute?.parameters||{})),[result,setResult]=useState<InvocationResult|null>(null),[error,setError]=useState<string|null>(null),[running,setRunning]=useState(false);
 const inputs=useMemo(()=>Object.entries(operation.inputs||{}),[operation.id,operation.inputs]);
 const parameters=useMemo(()=>Object.entries(operation.parameters||{}),[operation.id,operation.parameters]);
 const outputs=Object.entries(operation.outputs||{});
 const invocationVariant=variants.length===1?variants[0].id:variant;
 const selected=variants.find(item=>item.id===invocationVariant)||null;
 const run=async()=>{
  setRunning(true);setError(null);setResult(null);
  try{
   const values:Record<string,unknown>={};
   for(const[name,datatype]of inputs)values[name]=parseInput(String(datatype),rawInputs[name]??"");
   const parameterValues:Record<string,unknown>={};
   for(const[name,fallback]of parameters){const raw=rawParameters[name];if(raw===undefined||raw==="")parameterValues[name]=fallback;else try{parameterValues[name]=JSON.parse(raw)}catch{parameterValues[name]=raw}}
   const payload=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations/${encodeURIComponent(operation.id)}/invoke`,{method:"POST",body:JSON.stringify({implementationVariant:invocationVariant||undefined,inputs:values,parameters:parameterValues})});
   setResult(payload as InvocationResult);
  }catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setRunning(false)}
 };
 useEffect(()=>{setVariant(preferred);setRawInputs(defaults(operation.example_execute?.arguments||{}));setRawParameters(defaults(operation.example_execute?.parameters||{}));setResult(null);setError(null)},[operation.id]);
 return <section className="operation-playground">
  <div className="llm-subhead"><div><span>OPERATION PLAYGROUND</span><b>Invoke the abstract operation with a concrete variant</b></div><button className="primary" onClick={run} disabled={running||!invocationVariant}>{running?"Running…":"▶ Run"}</button></div>
  <div className="operation-playground-grid">
   <label className="operation-playground-field"><span>RUN VARIANT</span><select value={invocationVariant} disabled={variants.length===1} onChange={event=>{setVariant(event.target.value);setResult(null);setError(null)}}>{variants.map(item=><option key={item.id} value={item.id}>{item.label||item.id} · {item.implementation}</option>)}</select><small>{selected?`Executes ${selected.implementation}`:"Select an implementation"}. This does not change the saved preferred implementation.</small></label>
   {inputs.map(([name,datatype])=><label className="operation-playground-field" key={name}><span>INPUT · {name} <em>{datatype}</em></span><textarea value={rawInputs[name]??""} placeholder={isTextDatatype(String(datatype))?`Enter ${name}…`:`Enter ${datatype} as JSON…`} onChange={event=>setRawInputs(current=>({...current,[name]:event.target.value}))}/></label>)}
   {parameters.map(([name,fallback])=><label className="operation-playground-field" key={`parameter:${name}`}><span>PARAMETER · {name}</span><textarea value={rawParameters[name]??(typeof fallback==="string"?fallback:JSON.stringify(fallback??""))} placeholder={`Configure ${name}…`} onChange={event=>setRawParameters(current=>({...current,[name]:event.target.value}))}/></label>)}
  </div>
  <div className="operation-playground-contract"><span>OUTPUT CONTRACT</span>{outputs.map(([name,datatype])=><code key={name}>{name}: {datatype}</code>)}</div>
  {error&&<div className="demo-notice"><b>Invocation failed</b><span>{error}</span></div>}
  {result&&<div className="operation-playground-result"><div><span>RESULT</span><b>{result.implementation.label}</b><small>{result.implementation.route} · {result.elapsedMs} ms</small></div><pre>{JSON.stringify(result.outputs,null,2)}</pre>{result.resolvedPrompts&&result.resolvedPrompts.length>0&&<div className="operation-playground-prompts"><span>RESOLVED PROMPTS</span>{result.resolvedPrompts.map(item=><code key={`${item.promptId}:${item.implementationId}`}>{item.promptId} → {item.implementationId}</code>)}</div>}</div>}
 </section>;
}
