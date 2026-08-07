import {useEffect,useMemo,useState} from "react";
import "../styles/task_editor.css";

type Source="shared"|"workspace";
type ModelStrategy="single"|"parallel"|"compare"|"fallback";
type RecordFile<T>={path:string;source?:Source;workspaceId?:string;document?:T;error?:string;resolved?:{enabled?:boolean;backendId?:string;defaults?:Record<string,unknown>;model?:string}};
type TaskDef={kind:"task";id:string;label?:string;description?:string;role?:string;inputs?:Record<string,string>;outputs?:Record<string,string>;implementationSelection?:{strategy?:string;default?:string;variants?:string[]}};
type TaskImplementationDef={kind:"task_implementation";id:string;implements:string;label?:string;description?:string;implementation:string;inputs?:Record<string,string>;outputs?:Record<string,string>;parameters?:Record<string,unknown>;bindings?:Record<string,unknown>;python?:Record<string,unknown>;prolog?:Record<string,unknown>;metta?:Record<string,unknown>;modelSelection?:{models?:string[];strategy?:ModelStrategy}};
type TaskResource=TaskDef|TaskImplementationDef;
type ModelDef={kind:"model"|"profile";id:string;label?:string;inherits:string;model?:string;enabled?:boolean;defaults?:Record<string,unknown>};
type PromptDef={kind:"prompt";id:string;label?:string;description?:string;text?:string|string[];variables?:string[]};
type Snapshot={workspace:{id:string;label:string;root:string};tasks:RecordFile<TaskDef>[];taskImplementations:RecordFile<TaskImplementationDef>[];models:RecordFile<ModelDef>[];prompts:RecordFile<PromptDef>[]};
type OpenDocument={key:string;record:RecordFile<TaskResource>;source:string;dirty:boolean};

const slug=(v:string)=>v.toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"")||"resource";
const recordKey=(record:RecordFile<TaskResource>)=>`${record.workspaceId||record.source||"resource"}:${record.path}:${record.document?.id||"unknown"}`;
async function request(path:string,init?:RequestInit){const r=await fetch(path,{headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});const text=await r.text();let p:any;try{p=JSON.parse(text)}catch{throw new Error(text||r.statusText)}if(!r.ok)throw new Error(p.error||p.detail||r.statusText);return p;}

export function TaskLibraryEditor({workspaceId}:{workspaceId:string}){
 const[snapshot,setSnapshot]=useState<Snapshot|null>(null),[openDocs,setOpenDocs]=useState<OpenDocument[]>([]),[activeKey,setActiveKey]=useState<string|null>(null),[compareKey,setCompareKey]=useState<string|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState<string|null>(null);
 const load=async()=>{const next=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/snapshot`) as Snapshot;setSnapshot(next);return next};
 useEffect(()=>{setOpenDocs([]);setActiveKey(null);setCompareKey(null);void load().catch(r=>setError(String(r)))},[workspaceId]);
 const enabledModels=(snapshot?.models||[]).filter(row=>row.document&&(row.resolved?.enabled??row.document.enabled!==false));
 const prompts=snapshot?.prompts||[];
 const implementations=snapshot?.taskImplementations||[];
 const children=useMemo(()=>{const map=new Map<string,RecordFile<TaskImplementationDef>[]>();for(const row of implementations){const id=row.document?.implements;if(!id)continue;const list=map.get(id)||[];list.push(row);map.set(id,list)}return map},[implementations]);
 const perform=async(work:()=>Promise<void>)=>{setBusy(true);setError(null);try{await work()}catch(r){setError(r instanceof Error?r.message:String(r))}finally{setBusy(false)}};
 const open=(record:RecordFile<TaskResource>)=>{const key=recordKey(record);setOpenDocs(current=>current.some(doc=>doc.key===key)?current:[...current,{key,record,source:record.document?JSON.stringify(record.document,null,2):"",dirty:false}]);setActiveKey(key)};
 const close=(key:string)=>{setOpenDocs(current=>{const index=current.findIndex(doc=>doc.key===key);const next=current.filter(doc=>doc.key!==key);if(activeKey===key)setActiveKey(next[Math.max(0,index-1)]?.key||next[0]?.key||null);if(compareKey===key)setCompareKey(null);return next})};
 useEffect(()=>{if(snapshot&&openDocs.length===0){const featured=(snapshot.tasks||[]).find(row=>row.document?.id==="echo_into_titlecased")||snapshot.tasks?.[0];if(featured)open(featured as RecordFile<TaskResource>)}},[snapshot]);
 const updateSource=(key:string,source:string)=>setOpenDocs(current=>current.map(doc=>doc.key===key?{...doc,source,dirty:true}:doc));
 const active=openDocs.find(doc=>doc.key===activeKey)||null;
 const comparison=openDocs.find(doc=>doc.key===compareKey)||null;
 const chooseComparison=()=>{if(compareKey){setCompareKey(null);return}const other=[...openDocs].reverse().find(doc=>doc.key!==activeKey);if(other)setCompareKey(other.key)};
 const saveDoc=(doc:OpenDocument)=>perform(async()=>{let document:TaskResource;try{document=JSON.parse(doc.source) as TaskResource}catch{throw new Error("Task resource JSON is invalid")};const kind=document.kind;const original=doc.record.path;const path=workspaceId==="shared"||doc.record.source==="workspace"?original:`tasks/${slug(document.id)}.${kind}.json`;await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`,{method:"PUT",body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});const next=await load();const pool:RecordFile<TaskResource>[]=[...(next.tasks||[]),...(next.taskImplementations||[])];const saved=pool.find(row=>row.document?.id===document.id);if(saved){const newKey=recordKey(saved);setOpenDocs(current=>current.map(item=>item.key===doc.key?{key:newKey,record:saved,source:JSON.stringify(saved.document,null,2),dirty:false}:item));if(activeKey===doc.key)setActiveKey(newKey);if(compareKey===doc.key)setCompareKey(newKey)}});

 const renderEditor=(doc:OpenDocument,secondary=false)=>{let document:TaskResource|null=null;try{document=doc.source?JSON.parse(doc.source) as TaskResource:null}catch{document=null}const abstract=document?.kind==="task"?document:null;const selectedImplementation=document?.kind==="task_implementation"?document:null;const selectedModels=selectedImplementation?.modelSelection?.models||[];const selectedPrompts=Array.isArray(selectedImplementation?.bindings?.prompts)?selectedImplementation!.bindings!.prompts as string[]:[];const variants=abstract?(children.get(abstract.id)||[]):[];
  const patchAbstract=(patch:Partial<TaskDef>)=>{if(!abstract)return;updateSource(doc.key,JSON.stringify({...abstract,...patch},null,2))};
  const setDefaultImplementation=(id:string)=>{if(!abstract)return;const selection=abstract.implementationSelection||{};const variantIds=selection.variants?.length?selection.variants:variants.map(row=>row.document?.id).filter(Boolean) as string[];patchAbstract({implementationSelection:{...selection,default:id||undefined,variants:variantIds}})};
  const patchImpl=(patch:Partial<TaskImplementationDef>)=>{if(!selectedImplementation)return;updateSource(doc.key,JSON.stringify({...selectedImplementation,...patch},null,2))};
  const toggleModel=(id:string)=>{if(!selectedImplementation)return;const models=selectedModels.includes(id)?selectedModels.filter(x=>x!==id):[...selectedModels,id];patchImpl({modelSelection:{models,strategy:selectedImplementation.modelSelection?.strategy||"single"}})};
  const updatePrompts=(ids:string[])=>{if(!selectedImplementation)return;patchImpl({bindings:{...(selectedImplementation.bindings||{}),prompts:ids,separator:selectedImplementation.bindings?.separator||"\n\n"}})};
  const togglePrompt=(id:string)=>updatePrompts(selectedPrompts.includes(id)?selectedPrompts.filter(x=>x!==id):[...selectedPrompts,id]);
  const movePrompt=(index:number,delta:number)=>{const next=[...selectedPrompts],to=index+delta;if(to<0||to>=next.length)return;[next[index],next[to]]=[next[to],next[index]];updatePrompts(next)};
  return <section className={`task-editor-document ${secondary?"secondary":"primary"}`} key={doc.key}>
   <div className="task-editor-toolbar"><div><span>{document?.kind==="task"?"ABSTRACT TASK":"TASK IMPLEMENTATION"}{doc.dirty?" · UNSAVED":""}</span><h2>{document?.label||document?.id||doc.record.path}</h2><small>{doc.record.source} · {doc.record.path}</small></div><div className="task-editor-actions">{!secondary&&<button onClick={chooseComparison}>{compareKey?"Single pane":"Split view"}</button>}<button className="primary" onClick={()=>saveDoc(doc)} disabled={busy||!document}>Save</button></div></div>
   <div className="task-editor-scroll">
    {!document&&<div className="demo-notice"><b>Invalid JSON</b><span>Fix the JSON before saving this resource.</span></div>}
    {abstract&&<div className="task-abstract-summary"><div><span>ROLE</span><b>{abstract.role||"abstract_stage"}</b></div><div><span>DEFAULT IMPLEMENTATION</span><select value={abstract.implementationSelection?.default||""} onChange={e=>setDefaultImplementation(e.target.value)}><option value="">planner-selected</option>{variants.map(row=>{const impl=row.document!;const language=impl.implementation.startsWith("python")?"Python":impl.implementation.startsWith("prolog")?"Prolog":impl.implementation.startsWith("metta")?"MeTTa":impl.implementation.startsWith("llm")?"LLM":"Implementation";return <option key={impl.id} value={impl.id}>{language} — {impl.label||impl.id}</option>})}</select></div><div><span>INPUTS</span><code>{Object.keys(abstract.inputs||{}).join(", ")||"—"}</code></div><div><span>OUTPUTS</span><code>{Object.keys(abstract.outputs||{}).join(", ")||"—"}</code></div></div>}
    {selectedImplementation&&<div className="implementation-summary"><div><span>ROUTE</span><b>{selectedImplementation.implementation}</b></div><div><span>IMPLEMENTS</span><b>{selectedImplementation.implements}</b></div>{selectedImplementation.python&&<div className="wide"><span>PYTHON SOURCE</span><code>{String(selectedImplementation.python.module||selectedImplementation.python.file||"configured source")}{selectedImplementation.python.className?` · ${String(selectedImplementation.python.className)}`:""}{selectedImplementation.python.callable?` :: ${String(selectedImplementation.python.callable)}`:""}</code></div>}{selectedImplementation.prolog&&<div className="wide"><span>SWI-PROLOG SOURCE</span><code>{String(selectedImplementation.prolog.predicate||"predicate")} / {String(selectedImplementation.prolog.arity||"?")}</code></div>}{selectedImplementation.metta&&<div className="wide"><span>METTA SOURCE</span><code>{JSON.stringify(selectedImplementation.metta)}</code></div>}</div>}
    {selectedImplementation?.implementation.startsWith("llm")&&<div className="task-llm-config"><div className="llm-subhead"><div><span>MODEL / PROFILE DISPATCH</span><b>Execution configurations allowed for this implementation</b></div></div><div className="task-model-list compact">{enabledModels.map(row=>{const item=row.document!,checked=selectedModels.includes(item.id);return <label className={`task-model-option ${checked?"selected":""}`} key={item.id}><input type="checkbox" checked={checked} onChange={()=>toggleModel(item.id)}/><span><b>{item.label||item.id}</b><small>{item.kind} · {row.resolved?.model||item.model||"inherited model"}</small></span></label>})}</div><div className="llm-subhead"><div><span>PROMPT COMPOSITION</span><b>Ordered prompts used by this implementation</b></div></div><div className="task-model-list compact">{prompts.map(row=>{const item=row.document!,checked=selectedPrompts.includes(item.id),index=selectedPrompts.indexOf(item.id);return <div className={`task-model-option ${checked?"selected":""}`} key={item.id}><input type="checkbox" checked={checked} onChange={()=>togglePrompt(item.id)}/><span><b>{item.label||item.id}</b><small>{item.description||row.path}</small></span>{checked&&<em><button onClick={()=>movePrompt(index,-1)} disabled={index===0}>↑</button> {index+1} <button onClick={()=>movePrompt(index,1)} disabled={index===selectedPrompts.length-1}>↓</button></em>}</div>})}</div></div>}
    <div className="task-json-block"><div className="llm-subhead"><div><span>RESOURCE JSON</span><b>Edit the selected item directly</b></div></div><textarea className="raw-json-editor task-visible-editor" value={doc.source} onChange={e=>updateSource(doc.key,e.target.value)}/></div>
   </div>
  </section>};

 if(!snapshot)return <section className="resource-view"><div className="studio-empty">Loading task library…</div></section>;
 return <section className="resource-view task-hierarchy-page">
  <div className="resource-heading"><div><span>PROCESSING RESOURCES</span><h1>Tasks & implementations</h1><p>Abstract tasks are parents. Click any task or implementation to keep it open in an editor tab; use Split view to compare or copy between two resources.</p></div></div>
  {error&&<div className="demo-notice"><b>Task editor error</b><span>{error}</span></div>}
  <div className="task-hierarchy-layout">
   <div className="task-tree-pane">
    {(snapshot.tasks||[]).map(task=>{const item=task.document;if(!item)return null;const variants=children.get(item.id)||[];const selectedTask=active?.record.document?.id===item.id;return <div className="task-tree-group" key={item.id}>
      <button className={`task-tree-row task-parent ${selectedTask?"selected":""}`} onClick={()=>open(task as RecordFile<TaskResource>)}><span className="task-kind-badge">TASK</span><span><b>{item.label||item.id}</b><small>{item.description||item.id}</small></span><em>{variants.length} variants</em></button>
      <div className="task-tree-children">{variants.map(variant=>{const impl=variant.document!;const selectedImpl=active?.record.document?.id===impl.id;const language=impl.implementation.startsWith("python")?"PYTHON":impl.implementation.startsWith("prolog")?"PROLOG":impl.implementation.startsWith("metta")?"METTA":impl.implementation.startsWith("llm")?"LLM":"IMPL";return <button className={`task-tree-row task-child ${selectedImpl?"selected":""}`} key={impl.id} onClick={()=>open(variant as RecordFile<TaskResource>)}><span className={`task-kind-badge ${language.toLowerCase()}`}>{language}</span><span><b>{impl.label||impl.id}</b><small>{impl.implementation}</small></span><em>{item.implementationSelection?.default===impl.id?"default":""}</em></button>})}</div>
    </div>})}
   </div>
   <div className="task-editor-workspace">
    <div className="task-document-tabs">{openDocs.map(doc=><div className={`task-document-tab ${doc.key===activeKey?"active":""}`} key={doc.key}><button onClick={()=>setActiveKey(doc.key)}><span>{doc.record.document?.kind==="task"?"TASK":"IMPL"}</span><b>{doc.record.document?.label||doc.record.document?.id||doc.record.path}</b>{doc.dirty&&<i>●</i>}</button><button className="close" onClick={()=>close(doc.key)}>×</button></div>)}</div>
    <div className={`task-editor-panes ${comparison?"split":"single"}`}>
      {active?renderEditor(active):<div className="studio-empty">Select a task or implementation.</div>}
      {comparison&&renderEditor(comparison,true)}
    </div>
   </div>
  </div>
 </section>;
}
