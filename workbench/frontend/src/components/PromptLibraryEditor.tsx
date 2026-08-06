import { useEffect, useMemo, useState } from "react";

type Source = "shared" | "workspace";
type RecordFile<T> = {path:string;source?:Source;workspaceId?:string;document?:T;error?:string};
type PromptDef = {
  kind:"prompt";
  id:string;
  label?:string;
  description?:string;
  inputs?:Record<string,string>;
  outputs?:Record<string,string>;
  text?:string|string[];
  variables?:string[];
  implementationSelection?:{default?:string;variants?:string[]};
  metadata?:Record<string,unknown>;
};
type PromptImplementationDef = {
  kind:"prompt_implementation";
  id:string;
  implements:string;
  label?:string;
  description?:string;
  version?:number;
  targets?:string[];
  language?:string;
  text:string|string[];
  metadata?:Record<string,unknown>;
};
type PromptResource = PromptDef | PromptImplementationDef;
type PromptHierarchy = {
  prompts:RecordFile<PromptDef>[];
  promptImplementations:RecordFile<PromptImplementationDef>[];
  implementationsByPrompt:Record<string,RecordFile<PromptImplementationDef>[]>;
};
type PromptPayload = {
  workspace:{id:string;label:string;root:string};
  prompts:RecordFile<PromptDef>[];
  promptLibrary?:{hierarchy?:PromptHierarchy};
};

const slug=(value:string)=>value.toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"")||"prompt";
async function request(path:string,init?:RequestInit){const response=await fetch(path,{headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});const payload=await response.json();if(!response.ok)throw new Error(payload.error||payload.detail||response.statusText);return payload;}

export function PromptLibraryEditor({workspaceId}:{workspaceId:string}){
 const[payload,setPayload]=useState<PromptPayload|null>(null),[selected,setSelected]=useState<RecordFile<PromptResource>|null>(null),[source,setSource]=useState(""),[target,setTarget]=useState<string|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState<string|null>(null);
 const document=useMemo<PromptResource|null>(()=>{try{return source?JSON.parse(source) as PromptResource:null}catch{return null}},[source]);
 const load=async()=>{const next=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/prompts`) as PromptPayload;setPayload(next);return next};
 useEffect(()=>{setSelected(null);setSource("");setTarget(null);void load().catch(reason=>setError(String(reason)))},[workspaceId]);
 const hierarchy=payload?.promptLibrary?.hierarchy;
 const prompts=hierarchy?.prompts||payload?.prompts||[];
 const implementations=hierarchy?.promptImplementations||[];
 const children=hierarchy?.implementationsByPrompt||{};
 const open=(record:RecordFile<PromptResource>)=>{setSelected(record);setSource(record.document?JSON.stringify(record.document,null,2):"");setTarget(workspaceId==="shared"||record.source==="workspace"?record.path:null)};
 useEffect(()=>{if(payload&&!selected&&prompts[0])open(prompts[0] as RecordFile<PromptResource>)},[payload]);
 const perform=async(work:()=>Promise<void>)=>{setBusy(true);setError(null);try{await work()}catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setBusy(false)}};
 const newPrompt=()=>{const id="new_prompt";const doc:PromptDef={kind:"prompt",id,label:"New Prompt",description:"Abstract prompt contract.",inputs:{text:"text"},outputs:{text:"text"},implementationSelection:{default:`${id}.default`,variants:[`${id}.default`]}};open({path:`prompts/${id}.prompt.json`,source:workspaceId==="shared"?"shared":"workspace",workspaceId,document:doc});setTarget(`prompts/${id}.prompt.json`)};
 const newImplementation=(parent:PromptDef)=>{const id=`${parent.id}.alternative`;const doc:PromptImplementationDef={kind:"prompt_implementation",id,implements:parent.id,label:`${parent.label||parent.id} — Alternative`,version:1,targets:["generic-chat"],text:["Implement the abstract prompt contract.","Return only the requested output."]};open({path:`prompts/${slug(id)}.prompt_implementation.json`,source:workspaceId==="shared"?"shared":"workspace",workspaceId,document:doc});setTarget(`prompts/${slug(id)}.prompt_implementation.json`)};
 const copyLocal=()=>{if(!document||workspaceId==="shared")return;setTarget(`prompts/${slug(document.id)}.${document.kind}.json`)};
 const save=()=>perform(async()=>{if(!document||!document.id||!["prompt","prompt_implementation"].includes(document.kind))throw new Error("Prompt resource requires id and kind=prompt or prompt_implementation");if(document.kind==="prompt_implementation"&&!document.implements)throw new Error("Prompt implementation requires implements");const path=target||`prompts/${slug(document.id)}.${document.kind}.json`;await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`,{method:"PUT",body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});const next=await load();const h=next.promptLibrary?.hierarchy;const pool:RecordFile<PromptResource>[]=[...(h?.prompts||next.prompts||[]),...(h?.promptImplementations||[])];const saved=pool.find(row=>row.document?.id===document.id);if(saved)open(saved)});
 if(!payload)return <section className="resource-view"><div className="studio-empty">Loading prompt library…</div></section>;
 return <section className="resource-view task-hierarchy-page">
  <div className="resource-heading"><div><span>PROMPT CONTRACT SYSTEM</span><h1>Prompts & alternatives</h1><p>Abstract prompts are parents; model-, language-, and optimization-specific prompt implementations are interchangeable children.</p></div><button onClick={newPrompt}>+ Abstract prompt</button></div>
  {error&&<div className="demo-notice"><b>Prompt editor error</b><span>{error}</span></div>}
  <div className="task-hierarchy-layout">
   <div className="task-tree-pane">
    {prompts.map(prompt=>{const item=prompt.document;if(!item)return null;const variants=children[item.id]||[];const declared=item.implementationSelection?.variants||[];return <div className="task-tree-group" key={item.id}>
      <div className="inheritance-row"><button className={`task-tree-row task-parent ${selected?.document?.id===item.id?"selected":""}`} onClick={()=>open(prompt as RecordFile<PromptResource>)}><span className="task-kind-badge">PROMPT</span><span><b>{item.label||item.id}</b><small>{item.description||item.id}</small></span><em>{variants.length} alternatives</em></button><button className="hier-mini" onClick={()=>newImplementation(item)}>+ alt</button></div>
      <div className="task-tree-children">{variants.map(variant=>{const child=variant.document!;const isDefault=item.implementationSelection?.default===child.id;return <button className={`task-tree-row task-child ${selected?.document?.id===child.id?"selected":""}`} key={child.id} onClick={()=>open(variant as RecordFile<PromptResource>)}><span className="task-kind-badge llm">ALT</span><span><b>{child.label||child.id}</b><small>{(child.targets||[]).join(", ")||"generic"} · v{child.version||1}</small></span><em>{isDefault?"default":declared.includes(child.id)?"variant":"implementation"}</em></button>})}</div>
    </div>})}
   </div>
   <div className="task-editor-workspace">
    {selected?<section className="model-editor-document primary"><div className="model-editor-toolbar"><div><span>{document?.kind==="prompt"?"ABSTRACT PROMPT":"PROMPT IMPLEMENTATION"}</span><h2>{document?.label||document?.id||selected.path}</h2><small>{selected.source} · {selected.path}</small></div><div className="model-editor-actions">{selected.source==="shared"&&workspaceId!=="shared"&&<button onClick={copyLocal}>Make workspace-specific</button>}{document?.kind==="prompt"&&<button onClick={()=>newImplementation(document)}>+ Alternative</button>}<button className="primary" disabled={busy||!document} onClick={save}>Save</button></div></div><div className="model-editor-scroll">{document?.kind==="prompt"&&<div className="task-abstract-summary"><div><span>DEFAULT</span><b>{document.implementationSelection?.default||"—"}</b></div><div><span>VARIANTS</span><code>{(document.implementationSelection?.variants||[]).join(", ")||"—"}</code></div><div><span>INPUTS</span><code>{Object.keys(document.inputs||{}).join(", ")||"—"}</code></div><div><span>OUTPUTS</span><code>{Object.keys(document.outputs||{}).join(", ")||"—"}</code></div></div>}{document?.kind==="prompt_implementation"&&<div className="implementation-summary"><div><span>IMPLEMENTS</span><b>{document.implements}</b></div><div><span>TARGETS</span><b>{(document.targets||[]).join(", ")||"generic"}</b></div><div><span>VERSION</span><b>{document.version||1}</b></div></div>}<textarea className="raw-json-editor model-visible-editor" value={source} onChange={e=>setSource(e.target.value)}/></div></section>:<div className="studio-empty">Select a prompt or one of its alternatives.</div>}
   </div>
  </div>
  <div className="demo-notice"><b>Hierarchy proof</b><span>{prompts.length} abstract prompt(s) · {implementations.length} concrete alternative(s). The bundled Titlecase prompt has Default, GPT-5, and Claude variants so this tree is visibly populated on first launch.</span></div>
 </section>;
}
