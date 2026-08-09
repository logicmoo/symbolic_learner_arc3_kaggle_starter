import React,{useEffect,useMemo,useState} from "react";
import type { JSX } from "react";
import {HierarchyResourceEditor} from "./HierarchyResourceEditor";
import {ArtifactTreeBranch} from "./ArtifactTreeBranch";
import {ExampleExecutePanel,type ExampleExecute} from "./ExampleExecutePanel";
import {ResourceSourceEditor} from "./ResourceSourceEditor";
import {relationshipIds} from "./resourceRelationships";
import {ResourceEnablementBadge,enablementClass,resolveResourceEnablement,type ResourceEnablement} from "./resourceEnablement";
import "../styles/models_editor.css";

type Source="shared"|"workspace";
type NodeKind="backend"|"model"|"preset";
type RecordFile<T>={path:string;source?:Source;workspaceId?:string;document?:T;error?:string;resolved?:Resolution};
type BackendDef={kind:"backend";id:string;label?:string;description?:string;provider:string;official?:boolean;enabled?:boolean;capabilities?:string[];configuration?:Record<string,unknown>;modelDefaults?:Record<string,unknown>;example_execute?:ExampleExecute};
type ModelDef={kind:"model"|"profile";id:string;label?:string;description?:string;parents?:string[];inherits?:string;model?:string;enabled?:boolean;capabilities?:string[];defaults?:Record<string,unknown>;environment?:Record<string,unknown>;example_execute?:ExampleExecute};
type ModelResource=BackendDef|ModelDef;
type Resolution={parentId?:string;parentKind?:NodeKind;backendId?:string;inheritance?:string[];configuration?:Record<string,unknown>;defaults?:Record<string,unknown>;model?:string;enabled?:boolean};
type Snapshot={backends:RecordFile<BackendDef>[];models:RecordFile<ModelDef>[]};
type Layout="tiles"|"list";
type CatalogItem={kind:NodeKind;id:string;label:string;record:RecordFile<BackendDef>|RecordFile<ModelDef>};
type OpenDocument={key:string;record:RecordFile<ModelResource>;source:string;dirty:boolean};
type DiscoveredModel={id:string;label:string;resourceId?:string;status?:"new"|"changed"|"unchanged"|"missing";capabilities?:Record<string,boolean>;limits?:Record<string,unknown>;pricing?:Record<string,unknown>;properties?:Record<string,unknown>;providerMetadata?:Record<string,unknown>};

const slug=(v:string)=>v.toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"")||"item";
const recordKey=(record:RecordFile<ModelResource>)=>`${record.workspaceId||record.source||"resource"}:${record.path}:${record.document?.id||"unknown"}`;
function flattenObject(obj:any,prefix="",result:Record<string,any>={}){for(const key in obj){const value=obj[key],name=prefix?`${prefix}.${key}`:key;if(value&&typeof value==="object"&&!Array.isArray(value)){flattenObject(value,name,result)}else{result[name]=value}}return result}
async function request(path:string,init?:RequestInit){const r=await fetch(path,{cache:"no-store",headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});const text=await r.text();let p:any;try{p=JSON.parse(text)}catch{throw new Error(text||r.statusText)}if(!r.ok)throw new Error(p.error||p.detail||r.statusText);return p;}
function isLlmBackend(record:RecordFile<BackendDef>){const item=record.document;if(!item)return false;const caps=(item.capabilities||[]).join(" ").toLowerCase();return caps.includes("llm")||/openai|anthropic|openrouter|groq|ollama|unsloth|llm/.test(item.provider.toLowerCase());}
function num(v:unknown,fallback:number){return typeof v==="number"&&Number.isFinite(v)?v:fallback;}
const modelParent=(document:ModelDef)=>document.inherits||relationshipIds(document.parents)[0]||"";

function ConfigForm({source,onChange,items}:{source:string;onChange:(v:string)=>void;items:CatalogItem[]}){
 const doc=useMemo<ModelDef|null>(()=>{try{const parsed=JSON.parse(source) as ModelResource;return parsed.kind!=="backend"?{...parsed,inherits:modelParent(parsed)}:null}catch{return null}},[source]);
 if(!doc)return <div className="demo-notice"><b>Invalid model/preset JSON</b><span>Fix this item before using the configurator.</span></div>;
 const defaults=doc.defaults||{};const update=(patch:Partial<ModelDef>)=>onChange(JSON.stringify({...doc,...patch},null,2));const updateDefault=(name:string,value:unknown)=>update({defaults:{...defaults,[name]:value}});
 const role=items.find(item=>item.id===doc.inherits)?.kind==="backend"?"Model":"Model preset";
 return <div className="model-config-form"><label><span>RESOURCE ROLE</span><input readOnly value={role}/></label><label><span>ID</span><input value={doc.id} onChange={e=>update({id:e.target.value})}/></label><label><span>LABEL</span><input value={doc.label||""} onChange={e=>update({label:e.target.value})}/></label><label><span>INHERITS FROM</span><select value={doc.inherits} onChange={e=>update({inherits:e.target.value})}>{items.filter(x=>x.id!==doc.id).map(x=><option key={`${x.kind}:${x.id}`} value={x.id}>{x.kind.toUpperCase()} · {x.label}</option>)}</select></label><label><span>MODEL ID OVERRIDE</span><input value={doc.model||""} placeholder="inherit" onChange={e=>update({model:e.target.value||undefined})}/></label><label><span>TEMPERATURE</span><input type="number" step="0.01" value={num(defaults.temperature,0)} onChange={e=>updateDefault("temperature",Number(e.target.value))}/></label><label><span>TOP P</span><input type="number" step="0.01" value={num(defaults.topP,1)} onChange={e=>updateDefault("topP",Number(e.target.value))}/></label><label><span>MAX OUTPUT TOKENS</span><input type="number" value={num(defaults.maxOutputTokens,12000)} onChange={e=>updateDefault("maxOutputTokens",Number(e.target.value))}/></label><label><span>REASONING EFFORT</span><select value={String(defaults.reasoningEffort||"medium")} onChange={e=>updateDefault("reasoningEffort",e.target.value)}><option>low</option><option>medium</option><option>high</option></select></label><label><span>ANALYSIS LEVEL</span><input type="number" value={num(defaults.analysisLevel,0)} onChange={e=>updateDefault("analysisLevel",Number(e.target.value))}/></label><label><span>TIMEOUT SECONDS</span><input type="number" value={num(defaults.timeoutSeconds,300)} onChange={e=>updateDefault("timeoutSeconds",Number(e.target.value))}/></label><label><span>CURRENT IMAGE DETAIL</span><select value={String(defaults.currentImageDetail||"high")} onChange={e=>updateDefault("currentImageDetail",e.target.value)}><option>low</option><option>high</option></select></label><label><span>PARENT IMAGE DETAIL</span><select value={String(defaults.parentImageDetail||"low")} onChange={e=>updateDefault("parentImageDetail",e.target.value)}><option>low</option><option>high</option></select></label><label className="model-enable-field"><span>AVAILABLE TO OPERATIONS</span><input type="checkbox" checked={doc.enabled!==false} onChange={e=>update({enabled:e.target.checked})}/></label></div>;
}

export function LlmModelsEditor({workspaceId}:{workspaceId:string}){
 const[snapshot,setSnapshot]=useState<Snapshot|null>(null),[layout,setLayout]=useState<Layout>("tiles"),[openDocs,setOpenDocs]=useState<OpenDocument[]>([]),[activeKey,setActiveKey]=useState<string|null>(null),[compareKey,setCompareKey]=useState<string|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState<string|null>(null),[discovery,setDiscovery]=useState<{backendId:string;models:DiscoveredModel[]}|null>(null),[discoverySelection,setDiscoverySelection]=useState<Set<string>>(new Set()),[discoveryFilter,setDiscoveryFilter]=useState(""),[discoverySort,setDiscoverySort]=useState<{key:string;dir:"asc"|"desc"}>({key:"id",dir:"asc"});
 const load=async()=>{const next=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/snapshot`) as Snapshot;setSnapshot(next);return next};
 useEffect(()=>{setOpenDocs([]);setActiveKey(null);setCompareKey(null);void load().catch(r=>setError(String(r)))},[workspaceId]);
 const backends=useMemo(()=>(snapshot?.backends||[]).filter(isLlmBackend),[snapshot]);const nodes=snapshot?.models||[];
 const backendIds=useMemo(()=>new Set(backends.flatMap(record=>record.document?.id?[record.document.id]:[])),[backends]);
 const modelRole=(document:ModelDef):NodeKind=>document.kind==="profile"||(!backendIds.has(modelParent(document))&&Boolean(modelParent(document)))?"preset":"model";
 const items=useMemo<CatalogItem[]>(()=>[...backends.filter(x=>x.document).map(record=>({kind:"backend" as const,id:record.document!.id,label:record.document!.label||record.document!.id,record})),...nodes.filter(x=>x.document).map(record=>({kind:modelRole(record.document!),id:record.document!.id,label:record.document!.label||record.document!.id,record}))],[backends,nodes,backendIds]);
 const children=useMemo(()=>{const map=new Map<string,RecordFile<ModelDef>[]>();for(const record of nodes){const parent=record.document?modelParent(record.document):"";if(!parent)continue;const rows=map.get(parent)||[];rows.push(record);map.set(parent,rows)}return map},[nodes]);
 const exampleFor=(document:ModelResource|null):ExampleExecute|null=>{let current=document;const visited=new Set<string>();while(current&&!visited.has(current.id)){visited.add(current.id);if(current.example_execute)return current.example_execute;if(current.kind==="backend")return null;const parent=items.find(item=>item.id===modelParent(current as ModelDef))?.record.document as ModelResource|undefined;current=parent||null}return null};
 const roots=backends.filter(x=>x.document).map(record=>({kind:"backend" as const,id:record.document!.id,label:record.document!.label||record.document!.id,record}));
 const perform=async(work:()=>Promise<void>)=>{setBusy(true);setError(null);try{await work()}catch(r){setError(r instanceof Error?r.message:String(r))}finally{setBusy(false)}};
 const open=(record:RecordFile<ModelResource>)=>{const key=recordKey(record);setOpenDocs(current=>current.some(doc=>doc.key===key)?current:[...current,{key,record,source:record.document?JSON.stringify(record.document,null,2):"",dirty:false}]);setActiveKey(key)};
 const close=(key:string)=>{setOpenDocs(current=>{const index=current.findIndex(doc=>doc.key===key);const next=current.filter(doc=>doc.key!==key);if(activeKey===key)setActiveKey(next[Math.max(0,index-1)]?.key||next[0]?.key||null);if(compareKey===key)setCompareKey(null);return next})};
 useEffect(()=>{if(snapshot&&openDocs.length===0){if(nodes[0])open(nodes[0] as RecordFile<ModelResource>);else if(backends[0])open(backends[0] as RecordFile<ModelResource>)}},[snapshot]);
 const updateSource=(key:string,source:string)=>setOpenDocs(current=>current.map(doc=>doc.key===key?{...doc,source,dirty:true}:doc));
 const active=openDocs.find(doc=>doc.key===activeKey)||null;
 const chooseComparison=()=>{if(compareKey){setCompareKey(null);return}const other=[...openDocs].reverse().find(doc=>doc.key!==activeKey);if(other)setCompareKey(other.key)};
 const saveDoc=(doc:OpenDocument)=>perform(async()=>{let document:ModelResource;try{document=JSON.parse(doc.source) as ModelResource}catch{throw new Error("Model resource source is invalid")};if(document.kind==="backend"&&!document.provider)throw new Error("Backend requires provider");if(document.kind!=="backend"){const parent=modelParent(document);if(!parent)throw new Error("Model requires a parent");document={...document,kind:"model",parents:[parent]};delete document.inherits}const original=doc.record.path;const directory=document.kind==="backend"?"design/backends":"design/models";const path=workspaceId==="shared"||doc.record.source==="workspace"?original:`${directory}/${slug(document.id)}.${document.kind}.json`;await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`,{method:"PUT",body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});const next=await load();const pool:RecordFile<ModelResource>[]=[...(next.backends||[]),...(next.models||[])];const saved=pool.find(row=>row.document?.id===document.id);if(saved){const newKey=recordKey(saved);setOpenDocs(current=>current.map(item=>item.key===doc.key?{key:newKey,record:saved,source:JSON.stringify(saved.document,null,2),dirty:false}:item));if(activeKey===doc.key)setActiveKey(newKey);if(compareKey===doc.key)setCompareKey(newKey)}});
 const setResourceEnabled=(doc:OpenDocument,document:ModelResource,enabled:boolean)=>{
  const source=JSON.stringify({...document,enabled},null,2);
  return saveDoc({...doc,source,dirty:true});
 };
 const newBackend=()=>{const id=`backend-${Date.now().toString(36)}`;const document:BackendDef={kind:"backend",id,label:"New LLM Backend",description:"Configure the provider endpoint before pulling models.",provider:"openai",enabled:true,capabilities:["llm"],configuration:{baseUrl:"",apiKeyEnvironmentVariable:""},modelDefaults:{}};open({path:`design/backends/${slug(id)}.backend.json`,source:workspaceId==="shared"?"shared":"workspace",workspaceId,document})};
 const newChild=(parent:CatalogItem,role:"model"|"preset")=>{const id=`${parent.id}-${role}`;const document:ModelDef={kind:"model",id,label:`${parent.label} ${role}`,parents:[parent.id],enabled:true,defaults:{temperature:0,topP:1,maxOutputTokens:12000,reasoningEffort:"medium",timeoutSeconds:300}};open({path:`design/models/${slug(id)}.model.json`,source:workspaceId==="shared"?"shared":"workspace",workspaceId,document})};
 const pullModels=(backendId:string)=>perform(async()=>{const result=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/discover/${encodeURIComponent(backendId)}`);setDiscovery({backendId,models:result.models||[]});setDiscoverySelection(new Set())});
 const purgeAndReload=async()=>{setSnapshot(null);setOpenDocs([]);setActiveKey(null);setCompareKey(null);setDiscovery(null);setDiscoverySelection(new Set());await load()};
 const importModels=(backendId:string)=>perform(async()=>{if(!discovery)return;const models=discovery.models.filter(model=>model.status!=="missing"&&discoverySelection.has(model.id));if(!models.length)throw new Error("Select at least one new or changed model");await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/import/${encodeURIComponent(backendId)}`,{method:"POST",body:JSON.stringify({models,overwrite:true})});await purgeAndReload()});
 const removeMissing=(backendId:string)=>perform(async()=>{if(!discovery)return;const resourceIds=discovery.models.filter(model=>model.status==="missing"&&discoverySelection.has(model.id)).map(model=>model.resourceId).filter(Boolean);if(!resourceIds.length)throw new Error("Select at least one missing model");await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/remove-missing/${encodeURIComponent(backendId)}`,{method:"POST",body:JSON.stringify({resourceIds})});await purgeAndReload()});
 const executeModelExample=async(modelId:string,args:Record<string,unknown>)=>request(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/${encodeURIComponent(modelId)}/example-invoke`,{method:"POST",body:JSON.stringify({arguments:args})});
 const renderTree=(item:CatalogItem,depth=0,parentEnablement?:ResourceEnablement):JSX.Element=>{const backend=item.kind==="backend";const record=item.record as RecordFile<ModelResource>;const nested=children.get(item.id)||[];const selected=active?.record.document?.id===item.id;const inherited=resolveResourceEnablement(record.document,parentEnablement);const itemEnablement=typeof record.resolved?.enabled==="boolean"?{enabled:record.resolved.enabled,source:record.document?.enabled===undefined&&parentEnablement?"parent":inherited.source} as ResourceEnablement:inherited;return <ArtifactTreeBranch className={`inheritance-node ${layout} ${item.kind}-node`} childrenClassName="inheritance-children" key={`${item.kind}:${item.id}`} label={item.label} initialCollapsed={backend} searchValue={{document:record.document,resolved:record.resolved}} style={{"--tree-depth":depth} as React.CSSProperties} header={<div className="inheritance-row"><button className={`inheritance-main ${enablementClass(itemEnablement)} ${selected?"selected":""}`} onClick={()=>open(record)}><span>{item.kind.toUpperCase()}</span><b>{item.label}</b><small>{backend?(record.document as BackendDef)?.provider:((record as RecordFile<ModelDef>).resolved?.model||(record.document as ModelDef)?.model||`inherits ${(record.document as ModelDef)?.inherits}`)}</small><div className="inheritance-status"><em>{nested.length} {backend?"models":"presets"}{!backend&&` · temp ${String((((record as RecordFile<ModelDef>).resolved?.defaults||(record.document as ModelDef)?.defaults||{}).temperature)??"—")}`}</em><ResourceEnablementBadge state={itemEnablement}/></div></button>{backend?<button className="hier-mini" onClick={()=>newChild(item,"model")}>+ model</button>:<button className="hier-mini" onClick={()=>newChild(item,"preset")}>+ preset</button>}</div>}>{nested.length?nested.map(r=>renderTree({kind:modelRole(r.document!),id:r.document!.id,label:r.document!.label||r.document!.id,record:r},depth+1,itemEnablement)):undefined}</ArtifactTreeBranch>};
     const renderEditor = (doc: OpenDocument, secondary = false) => {
  let document: ModelResource | null = null;
  try {
   document = JSON.parse(doc.source) as ModelResource;
  } catch {
   /* show raw if invalid */
  }
  const backend = document?.kind === "backend";
  const backendId = document?.id || "";
  const resourceEnabled = document
    ? (typeof document.enabled === "boolean"
      ? document.enabled
      : (typeof doc.record.resolved?.enabled === "boolean" ? doc.record.resolved.enabled : true))
    : false;
  const discoveryForThis = (discovery && discovery.backendId === backendId) ? discovery : null;
  const discoveredModels = discoveryForThis?.models || [];

  const filteredModels = (() => {
    if (!discoveryForThis) return [];
    let result = discoveredModels.map(m => ({ ...m, _flat: flattenObject(m) }));

    // Apply property and whole-resource filters: ~supported_parameters=topk, +supported_parameters=tem, +vision.
    if (discoveryFilter.trim()) {
      const parts = discoveryFilter.split(",").map(p => p.trim()).filter(Boolean);
      result = result.filter(m => {
        for (const part of parts) {
          const isExclude = part.startsWith("~");
          const isInclude = part.startsWith("+");
          const expression = (isExclude || isInclude) ? part.substring(1) : part;
          const separator = expression.indexOf("=");
          let actualValue: string;
          let expectedValue: string;
          if (separator < 0) {
            const {_flat, ...modelDocument} = m;
            actualValue = JSON.stringify(modelDocument);
            expectedValue = expression;
          } else {
            const key = expression.slice(0, separator).trim();
            expectedValue = expression.slice(separator + 1);
            if (key === "id") actualValue = m.id;
            else if (key === "label") actualValue = m.label;
            else if (key === "status") actualValue = m.status || "";
            else {
              let propertyValue = m._flat[key];
              if (propertyValue === undefined) {
                const leafMatches = Object.entries(m._flat)
                  .filter(([path]) => path.split(".").at(-1) === key)
                  .map(([, value]) => value);
                propertyValue = leafMatches.length === 1 ? leafMatches[0] : leafMatches;
              }
              actualValue = propertyValue === undefined ? "" : (JSON.stringify(propertyValue) ?? String(propertyValue));
            }
          }

          const match = actualValue.toLowerCase().includes(expectedValue.toLowerCase());
          if (isExclude && match) return false;
          if (isInclude && !match) return false;
          if (!isExclude && !isInclude && !match) return false;
        }
        return true;
      });
    }

    // Apply sort
    const { key, dir } = discoverySort;
    result.sort((a, b) => {
      let va: any = "", vb: any = "";
      if (key === "id") { va = a.id; vb = b.id; }
      else if (key === "label") { va = a.label; vb = b.label; }
      else if (key === "status") { va = a.status; vb = b.status; }
      else { va = a._flat[key] ?? ""; vb = b._flat[key] ?? ""; }

      if (typeof va === "string") va = va.toLowerCase();
      if (typeof vb === "string") vb = vb.toLowerCase();

      if (va < vb) return dir === "asc" ? -1 : 1;
      if (va > vb) return dir === "asc" ? 1 : -1;
      return 0;
    });

    return result;
  })();

  const allFlattened = filteredModels.map(m => m._flat);
  const propKeys = Array.from(new Set(discoveredModels.flatMap(m => Object.keys(flattenObject(m)))))
    .filter(key => !["id", "label", "status"].includes(key))
    .sort();

  const toggleSort = (key: string) => {
    setDiscoverySort(prev => ({
      key,
      dir: prev.key === key && prev.dir === "asc" ? "desc" : "asc"
    }));
  };

  return (
   <div className={"model-editor-scroll " + (secondary ? "secondary" : "")}>
    <div className="model-editor-document">
     <div className="model-editor-toolbar">
      <div className="model-editor-identity">
       <span className={"model-kind-badge " + (document?.kind || "")}>{document?.kind?.toUpperCase()}</span>
       <b>{document?.label || document?.id || "New Item"}</b>
       <small>{doc.record.path}</small>
      </div>
      <div className="model-editor-actions">
       {doc.dirty && <button className="primary" onClick={() => saveDoc(doc)} disabled={busy}>Save Changes</button>}
       {document && <button
        className={resourceEnabled ? "disable-resource" : "enable-resource"}
        onClick={() => setResourceEnabled(doc, document, !resourceEnabled)}
        disabled={busy}
        aria-pressed={!resourceEnabled}
        title={`${resourceEnabled ? "Disable" : "Enable"} this ${document.kind} resource`}
       >{resourceEnabled ? "Disable Resource" : "Enable Resource"}</button>}
       {backend && <button onClick={() => pullModels(backendId)} disabled={busy}>Pull Models</button>}
       {!secondary && <button onClick={chooseComparison}>{compareKey ? "Close Split" : "Split View"}</button>}
       <button className="danger" onClick={() => close(doc.key)}>Close</button>
      </div>
     </div>

     {backend && discoveryForThis && (
      <div className="model-discovery">
       <div className="llm-subhead">
        <b>DISCOVERED MODELS</b>
        <span>{discoveredModels.length} available · {discoveredModels.filter(m => m.status === "new").length} new · {discoveredModels.filter(m => m.status === "changed").length} changed · {discoveredModels.filter(m => m.status === "missing").length} missing · {discoverySelection.size} selected</span>
        <div className="model-discovery-filter">
          <input
            type="text"
            placeholder="Filter: +key=val, ~key=val, +text, ~text..."
            value={discoveryFilter}
            onChange={e => setDiscoveryFilter(e.target.value)}
          />
        </div>
        <div className="model-discovery-actions">
         <button onClick={() => setDiscoverySelection(new Set(discoveredModels.filter(m => m.status === "new" || m.status === "changed").map(m => m.id)))}>Select new/changed</button>
         <button onClick={() => setDiscoverySelection(new Set(discoveredModels.filter(m => m.status === "missing").map(m => m.id)))}>Select missing</button>
         <button onClick={() => setDiscoverySelection(new Set())}>Clear selection</button>
         <button className="primary" onClick={() => importModels(backendId)} disabled={busy || !discoveredModels.some(m => m.status !== "missing" && discoverySelection.has(m.id))}>Import/overwrite selected</button>
         <button className="danger" onClick={() => removeMissing(backendId)} disabled={busy || !discoveredModels.some(m => m.status === "missing" && discoverySelection.has(m.id))}>Remove missing</button>
        </div>
       </div>
       <div className="model-discovery-list">
        <table className="model-discovery-table">
         <thead>
          <tr>
           <th></th>
           <th onClick={() => toggleSort("status")} style={{cursor:"pointer"}}>Status {discoverySort.key === "status" ? (discoverySort.dir === "asc" ? "▲" : "▼") : ""}</th>
           <th onClick={() => toggleSort("id")} style={{cursor:"pointer"}}>ID / Label {discoverySort.key === "id" ? (discoverySort.dir === "asc" ? "▲" : "▼") : ""}</th>
           {propKeys.map(k => (
             <th key={k} onClick={() => toggleSort(k)} style={{cursor:"pointer"}}>
               {k} {discoverySort.key === k ? (discoverySort.dir === "asc" ? "▲" : "▼") : ""}
             </th>
           ))}
          </tr>
         </thead>
         <tbody>
          {filteredModels.map((model, idx) => {
           const flat = allFlattened[idx];
           const isSelected = discoverySelection.has(model.id);
           return (
            <tr key={model.id} onClick={() => {
             const next = new Set(discoverySelection);
             if (isSelected) next.delete(model.id); else next.add(model.id);
             setDiscoverySelection(next);
            }}>
             <td><input type="checkbox" checked={isSelected} readOnly /></td>
             <td><i className={"discovery-status " + (model.status || "")}>{model.status}</i></td>
             <td><b>{model.label}</b><br /><code>{model.id}</code></td>
             {propKeys.map(k => {
              const val = flat[k];
              return <td key={k}>{val === undefined ? "" : typeof val === "object" ? JSON.stringify(val) : String(val)}</td>
             })}
            </tr>
           );
          })}
         </tbody>
        </table>
       </div>
      </div>
     )}

     <div className="model-visible-editor">
      <div className="studio-section-label">RESOURCE SPECIFICATION (JSON)</div>
      <ResourceSourceEditor value={doc.source} onChange={src => updateSource(doc.key, src)} showEnablement={false} />
     </div>

     {!backend && document && (
      <div className="model-config-panes">
       <div className="model-config-pane">
        <div className="studio-section-label">CONFIGURATION</div>
        <ConfigForm source={doc.source} onChange={src => updateSource(doc.key, src)} items={items} />
       </div>
       <div className="model-config-pane resolved-inheritance">
        <div className="studio-section-label">RESOLVED INHERITANCE</div>
        <pre>{JSON.stringify(doc.record.resolved || {}, null, 2)}</pre>
       </div>
      </div>
     )}

     {backend && document && (
      <div className="backend-inheritance-summary">
       <div className="studio-section-label">BACKEND DEFAULTS & CAPABILITIES</div>
       <pre>{JSON.stringify({ provider: (document as BackendDef).provider, official: (document as BackendDef).official, enabled: (document as BackendDef).enabled, capabilities: (document as BackendDef).capabilities, modelDefaults: (document as BackendDef).modelDefaults }, null, 2)}</pre>
      </div>
     )}

     {exampleFor(document) && (
      <div className="model-playground">
       <div className="studio-section-label">PLAYGROUND / EXAMPLE INVOKE</div>
       <ExampleExecutePanel contract={exampleFor(document)!} onExecute={args => executeModelExample(document!.id, args)} />
      </div>
     )}
    </div>
   </div>
  );
 };if(!snapshot)return <section className="resource-view"><div className="studio-empty">Loading model catalog…</div></section>;
 const leftPane=<div className={`inheritance-tree ${layout}`}>{roots.map(root=>renderTree(root))}</div>;
 const tabs=openDocs.map(doc=>({key:doc.key,kind:doc.record.document?.kind?.toUpperCase()||"ITEM",label:doc.record.document?.label||doc.record.document?.id||doc.record.path,dirty:doc.dirty}));
 const actions=<div className="layout-switch"><button onClick={newBackend}>+ Backend</button>{discovery&&<button onClick={()=>setDiscoverySelection(new Set(discovery.models.map(model=>model.id)))} disabled={busy||discoverySelection.size===discovery.models.length}>Select all discovered</button>}<button className={layout==="tiles"?"active":""} onClick={()=>setLayout("tiles")}>▦ Tiles</button><button className={layout==="list"?"active":""} onClick={()=>setLayout("list")}>☷ List</button></div>;
 return <HierarchyResourceEditor workspaceId={workspaceId} categoryTree="models" eyebrow="MODEL CATALOG" title="Backends, models & presets" description="Models inherit backends; reusable model presets inherit models or other presets and override invocation defaults without containing prompts." headerActions={actions} error={error} onDismissError={()=>setError(null)} leftPane={leftPane} tabs={tabs} activeKey={activeKey} compareKey={compareKey} onActivate={setActiveKey} onClose={close} renderEditor={(key,secondary)=>{const doc=openDocs.find(item=>item.key===key);return doc?renderEditor(doc,secondary):null}} emptyEditor={<div className="studio-empty">Select a backend, model, or preset.</div>} className="llm-model-editor model-hierarchy-page" treeClassName={`model-tree-pane ${layout}`} workspaceClassName="model-editor-workspace" tabsClassName="model-document-tabs" panesClassName="model-editor-panes"/>;
}
