import {useEffect,useMemo,useState} from "react";
import "../styles/task_editor.css";

type Source="shared"|"workspace";
type ModelStrategy="single"|"parallel"|"compare"|"fallback";
type RecordFile<T>={path:string;source?:Source;workspaceId?:string;document?:T;error?:string;resolved?:{enabled?:boolean;backendId?:string;defaults?:Record<string,unknown>;model?:string}};
type TaskDef={kind:"task";id:string;label?:string;description?:string;role?:string;inputs?:Record<string,string>;outputs?:Record<string,string>;implementationSelection?:{strategy?:string;default?:string;variants?:string[]}};
type TaskImplementationDef={kind:"task_implementation";id:string;implements:string;label?:string;description?:string;implementation:string;inputs?:Record<string,string>;outputs?:Record<string,string>;parameters?:Record<string,unknown>;bindings?:Record<string,unknown>;python?:Record<string,unknown>;prolog?:Record<string,unknown>;modelSelection?:{models?:string[];strategy?:ModelStrategy}};
type TaskResource=TaskDef|TaskImplementationDef;
type ModelDef={kind:"model"|"profile";id:string;label?:string;inherits:string;model?:string;enabled?:boolean;defaults?:Record<string,unknown>};
type PromptDef={kind:"prompt";id:string;label?:string;description?:string;text:string|string[];variables?:string[]};
type Snapshot={workspace:{id:string;label:string;root:string};tasks:RecordFile<TaskDef>[];taskImplementations:RecordFile<TaskImplementationDef>[];models:RecordFile<ModelDef>[];prompts:RecordFile<PromptDef>[]};

const slug=(v:string)=>v.toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"")||"resource";
async function request(path:string,init?:RequestInit){const r=await fetch(path,{headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});const text=await r.text();let p:any;try{p=JSON.parse(text)}catch{throw new Error(text||r.statusText)}if(!r.ok)throw new Error(p.error||p.detail||r.statusText);return p;}

export function TaskLibraryEditor({workspaceId}:{workspaceId:string}){
 const[snapshot,setSnapshot]=useState<Snapshot|null>(null),[selected,setSelected]=useState<RecordFile<TaskResource>|null>(null),[source,setSource]=useState(""),[target,setTarget]=useState<string|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState<string|null>(null);
 const load=async()=>{const next=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/snapshot`) as Snapshot;setSnapshot(next);return next};
 useEffect(()=>{setSelected(null);setSource("");setTarget(null);void load().catch(r=>setError(String(r)))},[workspaceId]);
 const document=useMemo<TaskResource|null>(()=>{try{return source?JSON.parse(source) as TaskResource:null}catch{return null}},[source]);
 const enabledModels=(snapshot?.models||[]).filter(row=>row.document&&(row.resolved?.enabled??row.document.enabled!==false));
 const prompts=snapshot?.prompts||[];
 const implementations=snapshot?.taskImplementations||[];
 const children=useMemo(()=>{const map=new Map<string,RecordFile<TaskImplementationDef>[]>();for(const row of implementations){const id=row.document?.implements;if(!id)continue;const list=map.get(id)||[];list.push(row);map.set(id,list)}return map},[implementations]);
 const perform=async(work:()=>Promise<void>)=>{setBusy(true);setError(null);try{await work()}catch(r){setError(r instanceof Error?r.message:String(r))}finally{setBusy(false)}};
 const open=(record:RecordFile<TaskResource>)=>{setSelected(record);setSource(record.document?JSON.stringify(record.document,null,2):"");setTarget(workspaceId==="shared"||record.source==="workspace"?record.path:null)};
 useEffect(()=>{if(snapshot&&!selected){const first=snapshot.tasks?.[0] as RecordFile<TaskResource>|undefined;if(first)open(first)}},[snapshot]);
 const save=()=>perform(async()=>{if(!document)throw new Error("Task resource JSON is invalid");const kind=document.kind;const path=target||`tasks/${slug(document.id)}.${kind}.json`;await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`,{method:"PUT",body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});const next=await load();const pool:RecordFile<TaskResource>[]=[...(next.tasks||[]),...(next.taskImplementations||[])];const saved=pool.find(row=>row.document?.id===document.id);if(saved)open(saved)});
 const selectedImplementation=document?.kind==="task_implementation"?document:null;
 const selectedModels=selectedImplementation?.modelSelection?.models||[];
 const selectedPrompts=Array.isArray(selectedImplementation?.bindings?.prompts)?selectedImplementation!.bindings!.prompts as string[]:[];
 const updateImpl=(patch:Partial<TaskImplementationDef>)=>{if(!selectedImplementation)return;setSource(JSON.stringify({...selectedImplementation,...patch},null,2))};
 const updateModels=(models:string[])=>{if(!selectedImplementation)return;updateImpl({modelSelection:{models,strategy:selectedImplementation.modelSelection?.strategy||"single"}})};
 const toggleModel=(id:string)=>updateModels(selectedModels.includes(id)?selectedModels.filter(x=>x!==id):[...selectedModels,id]);
 const updatePrompts=(ids:string[])=>{if(!selectedImplementation)return;updateImpl({bindings:{...(selectedImplementation.bindings||{}),prompts:ids,separator:selectedImplementation.bindings?.separator||"\n\n"}})};
 const togglePrompt=(id:string)=>updatePrompts(selectedPrompts.includes(id)?selectedPrompts.filter(x=>x!==id):[...selectedPrompts,id]);
 const movePrompt=(index:number,delta:number)=>{const next=[...selectedPrompts],to=index+delta;if(to<0||to>=next.length)return;[next[index],next[to]]=[next[to],next[index]];updatePrompts(next)};
 if(!snapshot)return <section className="resource-view"><div className="studio-empty">Loading task library…</div></section>;
 return <section className="resource-view task-hierarchy-page">
  <div className="resource-heading"><div><span>PROCESSING RESOURCES</span><h1>Tasks & implementations</h1><p>Abstract tasks are parents. Python, Prolog, MeTTa, and LLM implementations appear beneath the task they implement.</p></div></div>
  {error&&<div className="demo-notice"><b>Task editor error</b><span>{error}</span></div>}
  <div className="task-hierarchy-layout">
   <div className="task-tree-pane">
    {(snapshot.tasks||[]).map(task=>{const item=task.document; if(!item)return null;const variants=children.get(item.id)||[];const selectedTask=selected?.document?.id===item.id;return <div className="task-tree-group" key={item.id}>
      <button className={`task-tree-row task-parent ${selectedTask?"selected":""}`} onClick={()=>open(task as RecordFile<TaskResource>)}><span className="task-kind-badge">TASK</span><span><b>{item.label||item.id}</b><small>{item.description||item.id}</small></span><em>{variants.length} variants</em></button>
      <div className="task-tree-children">{variants.map(variant=>{const impl=variant.document!;const selectedImpl=selected?.document?.id===impl.id;const language=impl.implementation.startsWith("python")?"PYTHON":impl.implementation.startsWith("prolog")?"PROLOG":impl.implementation.startsWith("metta")?"METTA":impl.implementation.startsWith("llm")?"LLM":"IMPL";return <button className={`task-tree-row task-child ${selectedImpl?"selected":""}`} key={impl.id} onClick={()=>open(variant as RecordFile<TaskResource>)}><span className={`task-kind-badge ${language.toLowerCase()}`}>{language}</span><span><b>{impl.label||impl.id}</b><small>{impl.implementation}</small></span><em>{item.implementationSelection?.default===impl.id?"default":""}</em></button>})}</div>
    </div>})}
   </div>
   <div className="task-editor-pane">
    {!selected&&<div className="studio-empty">Select a task or implementation.</div>}
    {selected&&<>
      <div className="task-editor-toolbar"><div><span>{document?.kind==="task"?"ABSTRACT TASK":"TASK IMPLEMENTATION"}</span><h2>{document?.label||document?.id||selected.path}</h2><small>{selected.source} · {selected.path}</small></div><button className="primary" onClick={save} disabled={busy||!document}>Save</button></div>
      {document?.kind==="task"&&<div className="task-abstract-summary"><div><span>ROLE</span><b>{document.role||"abstract_stage"}</b></div><div><span>DEFAULT IMPLEMENTATION</span><b>{document.implementationSelection?.default||"—"}</b></div><div><span>INPUTS</span><code>{Object.keys(document.inputs||{}).join(", ")||"—"}</code></div><div><span>OUTPUTS</span><code>{Object.keys(document.outputs||{}).join(", ")||"—"}</code></div></div>}
      {selectedImplementation&&<div className="implementation-summary"><div><span>ROUTE</span><b>{selectedImplementation.implementation}</b></div><div><span>IMPLEMENTS</span><b>{selectedImplementation.implements}</b></div>{selectedImplementation.python&&<div className="wide"><span>PYTHON SOURCE</span><code>{String(selectedImplementation.python.module||selectedImplementation.python.file||"configured source")}{selectedImplementation.python.className?` · ${String(selectedImplementation.python.className)}`:""}{selectedImplementation.python.callable?` :: ${String(selectedImplementation.python.callable)}`:""}</code></div>}{selectedImplementation.prolog&&<div className="wide"><span>SWI-PROLOG SOURCE</span><code>{String(selectedImplementation.prolog.predicate||"predicate")} / {String(selectedImplementation.prolog.arity||"?")}</code></div>}</div>}
      {selectedImplementation?.implementation.startsWith("llm")&&<div className="task-llm-config"><div className="llm-subhead"><div><span>MODEL / PROFILE DISPATCH</span><b>Execution configurations allowed for this implementation</b></div></div><div className="task-model-list compact">{enabledModels.map(row=>{const item=row.document!,checked=selectedModels.includes(item.id);return <label className={`task-model-option ${checked?"selected":""}`} key={item.id}><input type="checkbox" checked={checked} onChange={()=>toggleModel(item.id)}/><span><b>{item.label||item.id}</b><small>{item.kind} · {row.resolved?.model||item.model||"inherited model"}</small></span></label>})}</div><div className="llm-subhead"><div><span>PROMPT COMPOSITION</span><b>Ordered prompts used by this implementation</b></div></div><div className="task-model-list compact">{prompts.map(row=>{const item=row.document!,checked=selectedPrompts.includes(item.id),index=selectedPrompts.indexOf(item.id);return <div className={`task-model-option ${checked?"selected":""}`} key={item.id}><input type="checkbox" checked={checked} onChange={()=>togglePrompt(item.id)}/><span><b>{item.label||item.id}</b><small>{item.description||row.path}</small></span>{checked&&<em><button onClick={()=>movePrompt(index,-1)} disabled={index===0}>↑</button> {index+1} <button onClick={()=>movePrompt(index,1)} disabled={index===selectedPrompts.length-1}>↓</button></em>}</div>})}</div></div>}
      <div className="task-json-block"><div className="llm-subhead"><div><span>RESOURCE JSON</span><b>Edit the selected item directly</b></div></div><textarea className="raw-json-editor task-visible-editor" value={source} onChange={e=>setSource(e.target.value)}/></div>
    </>}
   </div>
  </div>
 </section>;
}
