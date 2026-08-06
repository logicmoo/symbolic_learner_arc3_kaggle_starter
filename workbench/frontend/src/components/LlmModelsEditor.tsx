import { useEffect, useMemo, useState } from "react";
import "../styles/models_editor.css";

type Source = "shared" | "workspace";
type RecordFile<T> = { path:string; source?:Source; workspaceId?:string; document?:T; error?:string; resolved?:ModelResolution };
type BackendDef = { kind:"backend"; id:string; label?:string; description?:string; provider:string; official?:boolean; enabled?:boolean; capabilities?:string[]; configuration?:Record<string,unknown>; modelDefaults?:Record<string,unknown> };
type ModelDef = { kind:"model"; id:string; label?:string; description?:string; inherits:string; model?:string; enabled?:boolean; capabilities?:string[]; defaults?:Record<string,unknown>; environment?:Record<string,unknown> };
type ModelResolution = { parentId?:string; parentKind?:"backend"|"model"; backendId?:string; backendSource?:Source; backendPath?:string; backend?:BackendDef|null; inheritance?:string[]; configuration?:Record<string,unknown>; defaults?:Record<string,unknown>; model?:string; enabled?:boolean };
type Library<T> = { shared:RecordFile<T>[]; workspace:RecordFile<T>[]; effective:RecordFile<T>[] };
type Snapshot = { workspace:{id:string;label:string;root:string}; backends:RecordFile<BackendDef>[]; backendLibrary?:Library<BackendDef>; models:RecordFile<ModelDef>[]; modelLibrary?:Library<ModelDef> };
type Layout = "tiles"|"list";
type CatalogItem = {kind:"backend"|"model"; id:string; label:string; record:RecordFile<BackendDef>|RecordFile<ModelDef>};

const slug=(value:string)=>value.toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"")||"item";
async function request(path:string,init?:RequestInit){const response=await fetch(path,{headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});const payload=await response.json();if(!response.ok)throw new Error(payload.error||payload.detail||response.statusText);return payload;}
function isLlmBackend(record:RecordFile<BackendDef>){const item=record.document;if(!item)return false;const caps=(item.capabilities||[]).join(" ").toLowerCase();return caps.includes("llm")||/openai|anthropic|openrouter|groq|ollama|unsloth|llm/.test(item.provider.toLowerCase());}
function num(value:unknown,fallback:number){return typeof value==="number"&&Number.isFinite(value)?value:fallback;}

function ModelForm({source,onChange,items}:{source:string;onChange:(value:string)=>void;items:CatalogItem[]}){
 const document=useMemo<ModelDef|null>(()=>{try{return JSON.parse(source) as ModelDef}catch{return null}},[source]);
 if(!document)return <div className="demo-notice"><b>Invalid model JSON</b><span>Fix the JSON before using the structured configurator.</span></div>;
 const defaults=document.defaults||{};
 const update=(patch:Partial<ModelDef>)=>onChange(JSON.stringify({...document,...patch},null,2));
 const updateDefault=(name:string,value:unknown)=>update({defaults:{...defaults,[name]:value}});
 return <div className="model-config-form">
  <label><span>ID</span><input value={document.id} onChange={e=>update({id:e.target.value})}/></label>
  <label><span>LABEL</span><input value={document.label||""} onChange={e=>update({label:e.target.value})}/></label>
  <label><span>INHERITS FROM</span><select value={document.inherits} onChange={e=>update({inherits:e.target.value})}>{items.filter(item=>item.id!==document.id).map(item=><option key={`${item.kind}:${item.id}`} value={item.id}>{item.kind.toUpperCase()} · {item.label}</option>)}</select></label>
  <label><span>MODEL ID OVERRIDE</span><input value={document.model||""} placeholder="inherit from parent" onChange={e=>update({model:e.target.value||undefined})}/></label>
  <label><span>TEMPERATURE</span><input type="number" step="0.01" value={num(defaults.temperature,0)} onChange={e=>updateDefault("temperature",Number(e.target.value))}/></label>
  <label><span>TOP P</span><input type="number" step="0.01" value={num(defaults.topP,1)} onChange={e=>updateDefault("topP",Number(e.target.value))}/></label>
  <label><span>MAX OUTPUT TOKENS</span><input type="number" step="1" value={num(defaults.maxOutputTokens,12000)} onChange={e=>updateDefault("maxOutputTokens",Number(e.target.value))}/></label>
  <label><span>REASONING EFFORT</span><select value={String(defaults.reasoningEffort||"medium")} onChange={e=>updateDefault("reasoningEffort",e.target.value)}><option>low</option><option>medium</option><option>high</option></select></label>
  <label><span>TIMEOUT SECONDS</span><input type="number" step="1" value={num(defaults.timeoutSeconds,300)} onChange={e=>updateDefault("timeoutSeconds",Number(e.target.value))}/></label>
  <label><span>CURRENT IMAGE DETAIL</span><select value={String(defaults.currentImageDetail||"high")} onChange={e=>updateDefault("currentImageDetail",e.target.value)}><option>low</option><option>high</option></select></label>
  <label><span>PARENT IMAGE DETAIL</span><select value={String(defaults.parentImageDetail||"low")} onChange={e=>updateDefault("parentImageDetail",e.target.value)}><option>low</option><option>high</option></select></label>
  <label className="model-enable-field"><span>AVAILABLE TO TASKS</span><input type="checkbox" checked={document.enabled!==false} onChange={e=>update({enabled:e.target.checked})}/></label>
 </div>;
}

export function LlmModelsEditor({workspaceId}:{workspaceId:string}){
 const[snapshot,setSnapshot]=useState<Snapshot|null>(null),[layout,setLayout]=useState<Layout>("tiles");
 const[selectedModel,setSelectedModel]=useState<RecordFile<ModelDef>|null>(null),[modelSource,setModelSource]=useState(""),[modelTarget,setModelTarget]=useState<string|null>(null);
 const[selectedBackend,setSelectedBackend]=useState<RecordFile<BackendDef>|null>(null),[backendSource,setBackendSource]=useState(""),[backendTarget,setBackendTarget]=useState<string|null>(null);
 const[busy,setBusy]=useState(false),[error,setError]=useState<string|null>(null);
 const load=async()=>{const next=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/snapshot`) as Snapshot;setSnapshot(next);return next};
 useEffect(()=>{void load().catch(reason=>setError(String(reason)))},[workspaceId]);
 const backends=useMemo(()=>(snapshot?.backends||[]).filter(isLlmBackend),[snapshot]);
 const models=snapshot?.models||[];
 const items=useMemo<CatalogItem[]>(()=>[
  ...backends.filter(x=>x.document).map(record=>({kind:"backend" as const,id:record.document!.id,label:record.document!.label||record.document!.id,record})),
  ...models.filter(x=>x.document).map(record=>({kind:"model" as const,id:record.document!.id,label:record.document!.label||record.document!.id,record}))
 ],[backends,models]);
 const children=useMemo(()=>{const map=new Map<string,RecordFile<ModelDef>[]>();for(const record of models){const parent=record.document?.inherits;if(!parent)continue;const rows=map.get(parent)||[];rows.push(record);map.set(parent,rows)}return map},[models]);
 const perform=async(work:()=>Promise<void>)=>{setBusy(true);setError(null);try{await work()}catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setBusy(false)}};
 const openModel=(record:RecordFile<ModelDef>)=>{setSelectedModel(record);setSelectedBackend(null);setModelSource(record.document?JSON.stringify(record.document,null,2):"");setModelTarget(workspaceId==="shared"||record.source==="workspace"?record.path:null)};
 const openBackend=(record:RecordFile<BackendDef>)=>{setSelectedBackend(record);setSelectedModel(null);setBackendSource(record.document?JSON.stringify(record.document,null,2):"");setBackendTarget(workspaceId==="shared"||record.source==="workspace"?record.path:null)};
 useEffect(()=>{if(!snapshot)return;if(!selectedModel&&!selectedBackend){if(models[0])openModel(models[0]);else if(backends[0])openBackend(backends[0])}},[snapshot]);
 const saveModel=()=>perform(async()=>{const document=JSON.parse(modelSource) as ModelDef;if(document.kind!=="model"||!document.id||!document.inherits)throw new Error("Model requires kind, id, and inherits");const path=modelTarget||`models/${slug(document.id)}.json`;await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`,{method:"PUT",body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});const next=await load();const saved=next.models.find(x=>x.document?.id===document.id);if(saved)openModel(saved)});
 const cloneVariant=(record=selectedModel)=>{if(!record?.document)return;const base=record.document;const id=`${base.id}-variant`;const document:ModelDef={kind:"model",id,label:`${base.label||base.id} variant`,inherits:base.id,enabled:true,defaults:{temperature:(base.defaults||{}).temperature??0}};setSelectedModel({path:`models/${slug(id)}.json`,source:workspaceId==="shared"?"shared":"workspace",workspaceId,document});setSelectedBackend(null);setModelSource(JSON.stringify(document,null,2));setModelTarget(`models/${slug(id)}.json`)};
 const newModel=(parent:CatalogItem)=>{const id=`${parent.id}-model`;const document:ModelDef={kind:"model",id,label:`${parent.label} model`,inherits:parent.id,enabled:true,defaults:{temperature:0,topP:1,maxOutputTokens:12000,reasoningEffort:"medium",timeoutSeconds:300}};setSelectedModel({path:`models/${slug(id)}.json`,source:workspaceId==="shared"?"shared":"workspace",workspaceId,document});setSelectedBackend(null);setModelSource(JSON.stringify(document,null,2));setModelTarget(`models/${slug(id)}.json`)};
 const saveBackend=()=>perform(async()=>{const document=JSON.parse(backendSource) as BackendDef;if(document.kind!=="backend"||!document.id||!document.provider)throw new Error("Backend requires kind, id, and provider");const path=backendTarget||`models/backend_${slug(document.id)}.json`;await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`,{method:"PUT",body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});const next=await load();const saved=next.backends.find(x=>x.document?.id===document.id);if(saved)openBackend(saved)});
 const card=(item:CatalogItem,depth=0):JSX.Element=>{
  const isBackend=item.kind==="backend";const model=!isBackend?(item.record as RecordFile<ModelDef>):null;const resolved=model?.resolved;const nested=children.get(item.id)||[];
  return <div className={`inheritance-node ${layout} ${isBackend?"backend-node":"model-node"}`} key={`${item.kind}:${item.id}`} style={{"--tree-depth":depth} as React.CSSProperties}>
   <div className="inheritance-row">
    <button className="inheritance-main" onClick={()=>isBackend?openBackend(item.record as RecordFile<BackendDef>):openModel(item.record as RecordFile<ModelDef>)}><span>{isBackend?"BACKEND":"MODEL"}</span><b>{item.label}</b><small>{isBackend?(item.record as RecordFile<BackendDef>).document?.provider:(model?.document?.model||resolved?.model||"inherits model id")}</small>{!isBackend&&<em>temp {String((resolved?.defaults||model?.document?.defaults||{}).temperature??"—")}</em>}</button>
    <button className="hier-mini" onClick={()=>newModel(item)}>+ child model</button>
   </div>
   {nested.length>0&&<div className="inheritance-children">{nested.map(record=>card({kind:"model",id:record.document!.id,label:record.document!.label||record.document!.id,record},depth+1))}</div>}
  </div>;
 };
 if(!snapshot)return <section className="resource-view"><div className="studio-empty">Loading model catalog…</div></section>;
 const roots=backends.filter(x=>x.document).map(record=>({kind:"backend" as const,id:record.document!.id,label:record.document!.label||record.document!.id,record}));
 return <section className="resource-view llm-model-editor">
  <div className="resource-heading"><div><span>MODEL CATALOG</span><h1>Models & backends</h1><p>Everything lives in one models directory. Backends are root configuration objects; models inherit from either a backend or another model.</p></div><div className="layout-switch"><button className={layout==="tiles"?"active":""} onClick={()=>setLayout("tiles")}>▦ Tiles</button><button className={layout==="list"?"active":""} onClick={()=>setLayout("list")}>☷ List</button></div></div>
  {error&&<div className="demo-notice"><b>Configuration error</b><span>{error}</span></div>}
  <div className={`inheritance-tree ${layout}`}>{roots.map(root=>card(root))}</div>
  {selectedModel&&<section className="model-editor-drawer"><div className="drawer-heading"><div><span>MODEL CONFIGURATOR</span><h2>{selectedModel.document?.label||selectedModel.document?.id}</h2><small>{selectedModel.source} · {selectedModel.path}</small></div><div><button onClick={()=>cloneVariant()}>Clone child variant</button><button className="primary" disabled={busy} onClick={saveModel}>Save model</button></div></div><ModelForm source={modelSource} onChange={setModelSource} items={items}/><details><summary>Raw JSON</summary><textarea className="raw-json-editor" value={modelSource} onChange={e=>setModelSource(e.target.value)}/></details><aside className="resolved-inheritance"><span>RESOLVED INHERITANCE</span><pre>{JSON.stringify(selectedModel.resolved||{},null,2)}</pre></aside></section>}
  {selectedBackend?.document&&<section className="model-editor-drawer"><div className="drawer-heading"><div><span>BACKEND CONFIGURATOR</span><h2>{selectedBackend.document.label||selectedBackend.document.id}</h2><small>{selectedBackend.source} · {selectedBackend.path}</small></div><div><button onClick={()=>newModel({kind:"backend",id:selectedBackend.document!.id,label:selectedBackend.document!.label||selectedBackend.document!.id,record:selectedBackend})}>+ Child model</button><button className="primary" disabled={busy} onClick={saveBackend}>Save backend</button></div></div><div className="backend-inheritance-summary"><div><span>PROVIDER</span><b>{selectedBackend.document.provider}</b></div><div><span>CONFIGURATION</span><pre>{JSON.stringify(selectedBackend.document.configuration||{},null,2)}</pre></div><div><span>MODEL DEFAULTS</span><pre>{JSON.stringify(selectedBackend.document.modelDefaults||{},null,2)}</pre></div></div><textarea className="raw-json-editor" value={backendSource} onChange={e=>setBackendSource(e.target.value)}/></section>}
 </section>;
}
