import {useMemo,useState} from "react";
import "../styles/task_editor.css";
import "../styles/task_playground.css";

type TaskDef={id:string;label?:string;inputs?:Record<string,string>;outputs?:Record<string,string>;implementationSelection?:{default?:string;variants?:string[]}};
type TaskImplementationDef={id:string;label?:string;implementation:string};
type InvocationResult={task:{id:string;label:string;inputs:Record<string,string>;outputs:Record<string,string>};implementation:{id:string;label:string;route:string};resolvedPrompts?:Array<{promptId:string;implementationId:string;targets?:string[];version?:number}>;inputs:Record<string,unknown>;outputs:Record<string,unknown>;elapsedMs:number};

async function request(path:string,init?:RequestInit){const response=await fetch(path,{headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});const text=await response.text();let payload:any;try{payload=JSON.parse(text)}catch{throw new Error(text||response.statusText)}if(!response.ok)throw new Error(payload.error||payload.detail||response.statusText);return payload;}

function isTextDatatype(datatype:string){return /(^|\b)(text|string|markdown|natural.?language)(\b|$)/i.test(datatype);}
function parseInput(datatype:string,raw:string):unknown{
 if(isTextDatatype(datatype))return raw;
 const value=raw.trim();
 if(!value)return null;
 try{return JSON.parse(value)}catch{throw new Error(`Input for ${datatype} must be valid JSON (or use a Text datatype).`)}
}

export function TaskPlayground({workspaceId,task,variants}:{workspaceId:string;task:TaskDef;variants:TaskImplementationDef[]}){
 const preferred=task.implementationSelection?.default||variants[0]?.id||"";
 const[variant,setVariant]=useState(preferred),[rawInputs,setRawInputs]=useState<Record<string,string>>({}),[result,setResult]=useState<InvocationResult|null>(null),[error,setError]=useState<string|null>(null),[running,setRunning]=useState(false);
 const inputs=useMemo(()=>Object.entries(task.inputs||{}),[task.id,task.inputs]);
 const outputs=Object.entries(task.outputs||{});
 const selected=variants.find(item=>item.id===variant)||null;
 const run=async()=>{
  setRunning(true);setError(null);setResult(null);
  try{
   const values:Record<string,unknown>={};
   for(const[name,datatype]of inputs)values[name]=parseInput(String(datatype),rawInputs[name]??"");
   const payload=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/tasks/${encodeURIComponent(task.id)}/invoke`,{method:"POST",body:JSON.stringify({implementationVariant:variant||undefined,inputs:values})});
   setResult(payload as InvocationResult);
  }catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setRunning(false)}
 };
 return <section className="task-playground">
  <div className="llm-subhead"><div><span>TASK PLAYGROUND</span><b>Invoke the abstract task with a concrete variant</b></div><button className="primary" onClick={run} disabled={running||!variant}>{running?"Running…":"▶ Run"}</button></div>
  <div className="task-playground-grid">
   <label className="task-playground-field"><span>RUN VARIANT</span><select value={variant} onChange={event=>{setVariant(event.target.value);setResult(null);setError(null)}}>{variants.map(item=><option key={item.id} value={item.id}>{item.label||item.id} · {item.implementation}</option>)}</select><small>{selected?`Executes ${selected.implementation}`:"Select an implementation"}. This does not change the saved preferred implementation.</small></label>
   {inputs.map(([name,datatype])=><label className="task-playground-field" key={name}><span>INPUT · {name} <em>{datatype}</em></span><textarea value={rawInputs[name]??""} placeholder={isTextDatatype(String(datatype))?`Enter ${name}…`:`Enter ${datatype} as JSON…`} onChange={event=>setRawInputs(current=>({...current,[name]:event.target.value}))}/></label>)}
  </div>
  <div className="task-playground-contract"><span>OUTPUT CONTRACT</span>{outputs.map(([name,datatype])=><code key={name}>{name}: {datatype}</code>)}</div>
  {error&&<div className="demo-notice"><b>Invocation failed</b><span>{error}</span></div>}
  {result&&<div className="task-playground-result"><div><span>RESULT</span><b>{result.implementation.label}</b><small>{result.implementation.route} · {result.elapsedMs} ms</small></div><pre>{JSON.stringify(result.outputs,null,2)}</pre>{result.resolvedPrompts&&result.resolvedPrompts.length>0&&<div className="task-playground-prompts"><span>RESOLVED PROMPTS</span>{result.resolvedPrompts.map(item=><code key={`${item.promptId}:${item.implementationId}`}>{item.promptId} → {item.implementationId}</code>)}</div>}</div>}
 </section>;
}
