import { useEffect, useMemo, useState } from "react";

type Source = "shared" | "workspace";
type RecordFile<T> = {path:string;source?:Source;workspaceId?:string;document?:T;error?:string};
type PromptDef = {kind:"prompt";id:string;label?:string;description?:string;text:string|string[];variables?:string[];metadata?:Record<string,unknown>};
type Snapshot = {workspace:{id:string;label:string;root:string};prompts:RecordFile<PromptDef>[]};

const slug=(value:string)=>value.toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"")||"prompt";
async function request(path:string,init?:RequestInit){const response=await fetch(path,{headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});const payload=await response.json();if(!response.ok)throw new Error(payload.error||payload.detail||response.statusText);return payload;}

export function PromptLibraryEditor({workspaceId}:{workspaceId:string}){
 const[snapshot,setSnapshot]=useState<Snapshot|null>(null),[selected,setSelected]=useState<RecordFile<PromptDef>|null>(null),[source,setSource]=useState(""),[target,setTarget]=useState<string|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState<string|null>(null);
 const document=useMemo<PromptDef|null>(()=>{try{return source?JSON.parse(source) as PromptDef:null}catch{return null}},[source]);
 const load=async()=>{const next=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/snapshot`) as Snapshot;setSnapshot(next);return next};
 useEffect(()=>{setSelected(null);setSource("");setTarget(null);void load().catch(reason=>setError(String(reason)))},[workspaceId]);
 const open=(record:RecordFile<PromptDef>)=>{setSelected(record);setSource(record.document?JSON.stringify(record.document,null,2):"");setTarget(workspaceId==="shared"||record.source==="workspace"?record.path:null)};
 useEffect(()=>{if(snapshot&&!selected&&snapshot.prompts?.[0])open(snapshot.prompts[0])},[snapshot]);
 const perform=async(work:()=>Promise<void>)=>{setBusy(true);setError(null);try{await work()}catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setBusy(false)}};
 const newPrompt=()=>{const id="new-prompt";const doc:PromptDef={kind:"prompt",id,label:"New prompt",description:"Reusable prompt fragment.",text:""};setSelected({path:`prompts/${id}.json`,source:workspaceId==="shared"?"shared":"workspace",workspaceId,document:doc});setSource(JSON.stringify(doc,null,2));setTarget(`prompts/${id}.json`)};
 const copyLocal=()=>{if(!document||workspaceId==="shared")return;setTarget(`prompts/${slug(document.id)}.json`)};
 const save=()=>perform(async()=>{if(!document||document.kind!=="prompt"||!document.id)throw new Error("Prompt requires kind: prompt and id");const path=target||`prompts/${slug(document.id)}.json`;await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`,{method:"PUT",body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});const next=await load();const saved=next.prompts.find(row=>row.document?.id===document.id);if(saved)open(saved)});
 if(!snapshot)return <section className="resource-view"><div className="studio-empty">Loading prompt library…</div></section>;
 return <section className="resource-view"><div className="resource-heading"><div><span>PROMPT LIBRARY</span><h1>Prompts</h1><p>Reusable prompt fragments live here. Tasks choose and order prompts; model profiles do not contain prompt lists.</p></div><button onClick={newPrompt}>+ Prompt</button></div>{error&&<div className="demo-notice"><b>Prompt editor error</b><span>{error}</span></div>}<div className="resource-table"><div className="resource-row resource-head"><span>Prompt</span><span>Source</span><span>Variables</span><span>Path</span><span>State</span></div>{snapshot.prompts.map(row=><button className="resource-row" key={`${row.workspaceId}:${row.path}`} onClick={()=>open(row)}><b>{row.document?.label||row.document?.id||row.path}</b><code>{row.source}</code><span>{row.document?.variables?.join(", ")||"—"}</span><span>{row.path}</span><em>{row.error?"error":"ready"}</em></button>)}</div>{selected&&<section className="model-editor-drawer"><div className="drawer-heading"><div><span>PROMPT EDITOR</span><h2>{document?.label||document?.id||selected.path}</h2><small>{selected.source} · {selected.path}</small></div><div>{selected.source==="shared"&&workspaceId!=="shared"&&<button onClick={copyLocal}>Make workspace-specific</button>}<button className="primary" disabled={busy||!document} onClick={save}>Save prompt</button></div></div><textarea className="raw-json-editor" value={source} onChange={e=>setSource(e.target.value)}/></section>}</section>;
}
