import React,{useEffect,useMemo,useState} from "react";
import type { JSX } from "react";
import {HierarchyResourceEditor} from "./HierarchyResourceEditor";
import {ArtifactTreeBranch} from "./ArtifactTreeBranch";
import {ExampleExecutePanel,type ExampleExecute} from "./ExampleExecutePanel";
import {ResourceSourceEditor} from "./ResourceSourceEditor";
import type {WorkspaceResourceLocation} from "./WorkspaceResourceFileControls";
import {mettaDocumentToJson} from "../lib/mettaResourceCodec";
import {ModelResourcePlayground} from "./ModelResourcePlayground";
import {ResourceExecutionPlayground} from "./ResourceExecutionPlayground";
import {dependsOnResource,implementsResource,inheritsFromResource,relationshipIds} from "./resourceRelationships";
import {ResourceEnablementBadge,enablementClass,resolveResourceEnablement,type ResourceEnablement} from "./resourceEnablement";
import {displayResourcePath} from "./resourcePath";
import type {TreeRelationshipMode} from "./useArtifactTreeFilter";
import "../styles/models_editor.css";

type Source="shared"|"workspace";
type NodeKind="system"|"backend"|"model"|"preset";
type ModelEditorControlId="file"|"resource"|"actions"|"runner";
type ModelEditorDisplayMode="tabs"|"stacked"|"single"|"split-v"|"split-h";
type ModelEditorTabSet="all"|"ctx";
type RecordFile<T>={path:string;source?:Source;workspaceId?:string;document?:T;error?:string;resolved?:Resolution;isNew?:boolean};
type BackendDef={kind:"backend";id:string;label?:string;description?:string;provider:string;official?:boolean;enabled?:boolean;dependsOn?:Record<string,unknown>;dependedOnBy?:Record<string,unknown>;capabilities?:string[];configuration?:Record<string,unknown>;modelDefaults?:Record<string,unknown>;example_execute?:ExampleExecute};
type SystemDef={kind:"system";id:string;label?:string;description?:string;provider:string;systemType?:"runtime"|"llm_caller"|"agent"|"mcp"|"plugin"|string;enabled?:boolean;dependsOn?:Record<string,unknown>;dependedOnBy?:Record<string,unknown>;capabilities?:string[];configuration?:Record<string,unknown>;example_execute?:ExampleExecute};
type ModelDef={kind:"model"|"profile";id:string;label?:string;description?:string;implements?:Record<string,unknown>;implementedBy?:Record<string,unknown>;preferredImplementation?:string;inheritsFrom?:Record<string,unknown>;inheritedBy?:Record<string,unknown>;dependsOn?:Record<string,unknown>;dependedOnBy?:Record<string,unknown>;model?:string;enabled?:boolean;capabilities?:string[];defaults?:Record<string,unknown>;environment?:Record<string,unknown>;example_execute?:ExampleExecute};
type ModelResource=SystemDef|BackendDef|ModelDef;
type Resolution={parentId?:string;parentKind?:NodeKind;backendId?:string;implementationPath?:string[];propertyInheritanceResolution?:Record<string,unknown>;dependencies?:string[];blockingDependencies?:string[];configuration?:Record<string,unknown>;defaults?:Record<string,unknown>;model?:string;enabled?:boolean};
type Snapshot={systems:RecordFile<SystemDef>[];backends:RecordFile<BackendDef>[];models:RecordFile<ModelDef>[]};
type Layout="tiles"|"list";
type CatalogItem={kind:NodeKind;id:string;label:string;record:RecordFile<SystemDef>|RecordFile<BackendDef>|RecordFile<ModelDef>};
type OpenDocument={key:string;record:RecordFile<ModelResource>;source:string;dirty:boolean};
type DiscoveredModel={id:string;label:string;resourceId?:string;status?:"new"|"changed"|"unchanged"|"missing";capabilities?:Record<string,boolean>;limits?:Record<string,unknown>;pricing?:Record<string,unknown>;properties?:Record<string,unknown>;providerMetadata?:Record<string,unknown>};
type ModelOverrideDocument={kind:"model_overridden_properties";id:"model_overridden_properties";models:Record<string,Record<string,unknown>>;updatedByModel?:string;updatedAt?:string;sources?:string[]};
type EnablementRequest={resourceId:string;enabled:boolean;includeDependencies:boolean;includeDependents:boolean};
const MODEL_OVERRIDE_PATH="design/models/model_overridden_properties.json";
const DEFAULT_MODEL_OVERRIDE_DOCUMENT:ModelOverrideDocument={kind:"model_overridden_properties",id:"model_overridden_properties",models:{}};
const DEFAULT_MODEL_OVERRIDE_SOURCE=`${JSON.stringify(DEFAULT_MODEL_OVERRIDE_DOCUMENT,null,2)}\n`;

const slug=(v:string)=>v.toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"")||"item";
const recordKey=(record:RecordFile<ModelResource>)=>`${record.workspaceId||record.source||"resource"}:${record.path}:${record.document?.id||"unknown"}`;
function flattenObject(obj:any,prefix="",result:Record<string,any>={}){for(const key in obj){const value=obj[key],name=prefix?`${prefix}.${key}`:key;if(value&&typeof value==="object"&&!Array.isArray(value)){flattenObject(value,name,result)}else{result[name]=value}}return result}
async function request(path:string,init?:RequestInit){const r=await fetch(path,{cache:"no-store",headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});const text=await r.text();let p:any;try{p=JSON.parse(text)}catch{throw new Error(text||r.statusText)}if(!r.ok)throw new Error(p.error||p.detail||r.statusText);return p;}
function parseJsonObject(text:string){const trimmed=text.trim();if(!trimmed)return null;const attempts=[trimmed];if(trimmed.startsWith("```"))attempts.push(trimmed.replace(/^```[a-zA-Z]*\s*/,"").replace(/\s*```$/,"").trim());for(const candidate of attempts){try{const parsed=JSON.parse(candidate);if(parsed&&typeof parsed==="object"&&!Array.isArray(parsed))return parsed as Record<string,unknown>}catch{}}return null}
function isLlmBackend(record:RecordFile<BackendDef>){const item=record.document;if(!item)return false;const caps=(item.capabilities||[]).join(" ").toLowerCase();return caps.includes("llm")||/openai|anthropic|groq|ollama|unsloth|llm/.test(item.provider.toLowerCase());}
function num(v:unknown,fallback:number){return typeof v==="number"&&Number.isFinite(v)?v:fallback;}
const modelParent=(document:ModelDef)=>relationshipIds(document.implements)[0]||"";

function ConfigForm({source,onChange,items,effectiveEnabled,onEnabledChange}:{source:string;onChange:(v:string)=>void;items:CatalogItem[];effectiveEnabled:boolean;onEnabledChange:(enabled:boolean)=>void}){
 const doc=useMemo<ModelDef|null>(()=>{try{const parsed=JSON.parse(source) as ModelResource;return parsed.kind!=="backend"&&parsed.kind!=="system"?parsed:null}catch{return null}},[source]);
 if(!doc)return <div className="demo-notice"><b>Invalid model/preset JSON</b><span>Fix this item before using the configurator.</span></div>;
 const defaults=doc.defaults||{};const update=(patch:Partial<ModelDef>)=>onChange(JSON.stringify({...doc,...patch},null,2));const updateDefault=(name:string,value:unknown)=>update({defaults:{...defaults,[name]:value}});
 const role=items.find(item=>item.id===modelParent(doc))?.kind==="backend"?"Model":"Model preset";
 const dependencyId=relationshipIds(doc.dependsOn)[0]||"";
 const inheritanceId=relationshipIds(doc.inheritsFrom)[0]||"";
 return <div className="model-config-form"><label><span>RESOURCE ROLE</span><input readOnly value={role}/></label><label><span>ID</span><input value={doc.id} onChange={e=>update({id:e.target.value})}/></label><label><span>LABEL</span><input value={doc.label||""} onChange={e=>update({label:e.target.value})}/></label><label><span>IMPLEMENTS · classification</span><select value={modelParent(doc)} onChange={e=>update({implements:implementsResource(e.target.value)})}>{items.filter(x=>x.id!==doc.id).map(x=><option key={`${x.kind}:${x.id}`} value={x.id}>{x.kind.toUpperCase()} · {x.label}</option>)}</select></label><label><span>INHERITS FROM · properties</span><select value={inheritanceId} onChange={e=>update({inheritsFrom:e.target.value?inheritsFromResource(e.target.value):{}})}><option value="">No property inheritance</option>{items.filter(x=>x.id!==doc.id).map(x=><option key={`${x.kind}:${x.id}`} value={x.id}>{x.kind.toUpperCase()} · {x.label}</option>)}</select></label><label><span>DEPENDS ON · availability</span><select value={dependencyId} onChange={e=>update({dependsOn:e.target.value?dependsOnResource(e.target.value):{}})}><option value="">No availability dependency</option>{items.filter(x=>x.id!==doc.id).map(x=><option key={`${x.kind}:${x.id}`} value={x.id}>{x.kind.toUpperCase()} · {x.label}</option>)}</select></label><label><span>MODEL ID OVERRIDE</span><input value={doc.model||""} placeholder="inherit" onChange={e=>update({model:e.target.value||undefined})}/></label><label><span>TEMPERATURE</span><input type="number" step="0.01" value={num(defaults.temperature,0)} onChange={e=>updateDefault("temperature",Number(e.target.value))}/></label><label><span>TOP P</span><input type="number" step="0.01" value={num(defaults.topP,1)} onChange={e=>updateDefault("topP",Number(e.target.value))}/></label><label><span>MAX OUTPUT TOKENS</span><input type="number" value={num(defaults.maxOutputTokens,12000)} onChange={e=>updateDefault("maxOutputTokens",Number(e.target.value))}/></label><label><span>REASONING EFFORT</span><select value={String(defaults.reasoningEffort||"medium")} onChange={e=>updateDefault("reasoningEffort",e.target.value)}><option>low</option><option>medium</option><option>high</option></select></label><label><span>ANALYSIS LEVEL</span><input type="number" value={num(defaults.analysisLevel,0)} onChange={e=>updateDefault("analysisLevel",Number(e.target.value))}/></label><label><span>TIMEOUT SECONDS</span><input type="number" value={num(defaults.timeoutSeconds,300)} onChange={e=>updateDefault("timeoutSeconds",Number(e.target.value))}/></label><label><span>CURRENT IMAGE DETAIL</span><select value={String(defaults.currentImageDetail||"high")} onChange={e=>updateDefault("currentImageDetail",e.target.value)}><option>low</option><option>high</option></select></label><label><span>PARENT IMAGE DETAIL</span><select value={String(defaults.parentImageDetail||"low")} onChange={e=>updateDefault("parentImageDetail",e.target.value)}><option>low</option><option>high</option></select></label><label className="model-enable-field"><span>AVAILABLE TO OPERATIONS</span><input type="checkbox" checked={effectiveEnabled} onChange={e=>onEnabledChange(e.target.checked)}/></label></div>;
}

function SystemConfigForm({source,onChange}:{source:string;onChange:(value:string)=>void}){
 const doc=useMemo<SystemDef|null>(()=>{try{const parsed=JSON.parse(source) as ModelResource;return parsed.kind==="system"?parsed:null}catch{return null}},[source]);
 if(!doc)return <div className="demo-notice"><b>Invalid System resource</b><span>Fix this item before using the configurator.</span></div>;
 const configuration=doc.configuration||{};
 const update=(patch:Partial<SystemDef>)=>onChange(JSON.stringify({...doc,...patch},null,2));
 const updateConfiguration=(name:string,value:unknown)=>update({configuration:{...configuration,[name]:value}});
 return <div className="model-config-form system-config-form">
  <label><span>RESOURCE ROLE</span><input readOnly value="Callable System"/></label>
  <label><span>ID</span><input value={doc.id} onChange={event=>update({id:event.target.value})}/></label>
  <label><span>LABEL</span><input value={doc.label||""} onChange={event=>update({label:event.target.value})}/></label>
  <label><span>PROVIDER</span><input value={doc.provider||""} onChange={event=>update({provider:event.target.value})}/></label>
  <label><span>SYSTEM TYPE</span><input value={doc.systemType||""} onChange={event=>update({systemType:event.target.value})}/></label>
  <label><span>TIMEOUT SECONDS</span><input type="number" min="1" value={num(configuration.timeoutSeconds,300)} onChange={event=>updateConfiguration("timeoutSeconds",Number(event.target.value))}/></label>
  <label className="wide"><span>DESCRIPTION</span><textarea value={doc.description||""} onChange={event=>update({description:event.target.value})}/></label>
  <label className="wide"><span>CAPABILITIES · one per line</span><textarea value={(doc.capabilities||[]).join("\n")} onChange={event=>update({capabilities:event.target.value.split(/\r?\n|,/).map(value=>value.trim()).filter(Boolean)})}/></label>
  <label className="model-enable-field"><span>AVAILABLE TO WORKBENCH</span><input type="checkbox" checked={doc.enabled!==false} onChange={event=>update({enabled:event.target.checked})}/></label>
 </div>;
}

function BackendConfigForm({source,onChange}:{source:string;onChange:(value:string)=>void}){
 const doc=useMemo<BackendDef|null>(()=>{try{const parsed=JSON.parse(source) as ModelResource;return parsed.kind==="backend"?parsed:null}catch{return null}},[source]);
 if(!doc)return <div className="demo-notice"><b>Invalid Backend resource</b><span>Fix this item in File mode before configuring it.</span></div>;
 const configuration=doc.configuration||{};const modelDefaults=doc.modelDefaults||{};
 const update=(patch:Partial<BackendDef>)=>onChange(JSON.stringify({...doc,...patch},null,2));
 const updateConfiguration=(name:string,value:unknown)=>update({configuration:{...configuration,[name]:value}});
 const updateDefault=(name:string,value:unknown)=>update({modelDefaults:{...modelDefaults,[name]:value}});
 return <div className="model-config-form backend-config-form">
  <label><span>ID</span><input value={doc.id} onChange={event=>update({id:event.target.value})}/></label>
  <label><span>LABEL</span><input value={doc.label||""} onChange={event=>update({label:event.target.value})}/></label>
  <label><span>PROVIDER</span><input value={doc.provider||""} onChange={event=>update({provider:event.target.value})}/></label>
  <label><span>ADAPTER</span><input value={String(configuration.adapter||"")} onChange={event=>updateConfiguration("adapter",event.target.value)}/></label>
  <label className="wide"><span>BASE URL</span><input value={String(configuration.baseUrl||"")} onChange={event=>updateConfiguration("baseUrl",event.target.value)}/></label>
  <label><span>DEFAULT MODEL</span><input value={String(configuration.defaultModel||"")} onChange={event=>updateConfiguration("defaultModel",event.target.value)}/></label>
  <label><span>TIMEOUT SECONDS</span><input type="number" min="1" value={num(configuration.timeoutSeconds,300)} onChange={event=>updateConfiguration("timeoutSeconds",Number(event.target.value))}/></label>
  <label><span>DEFAULT TEMPERATURE</span><input type="number" step="0.01" value={num(modelDefaults.temperature,0)} onChange={event=>updateDefault("temperature",Number(event.target.value))}/></label>
  <label className="wide"><span>DESCRIPTION</span><textarea value={doc.description||""} onChange={event=>update({description:event.target.value})}/></label>
  <label className="wide"><span>CAPABILITIES · one per line</span><textarea value={(doc.capabilities||[]).join("\n")} onChange={event=>update({capabilities:event.target.value.split(/\r?\n|,/).map(value=>value.trim()).filter(Boolean)})}/></label>
 </div>;
}

export function LlmModelsEditor({workspaceId,catalogMode="models",topMenuMode="browse"}:{workspaceId:string;catalogMode?:"systems"|"models";topMenuMode?:"browse"|"discover"|"override"}){
 const[snapshot,setSnapshot]=useState<Snapshot|null>(null),[layout,setLayout]=useState<Layout>("tiles"),[openDocs,setOpenDocs]=useState<OpenDocument[]>([]),[activeKey,setActiveKey]=useState<string|null>(null),[compareKey,setCompareKey]=useState<string|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState<string|null>(null),[discovery,setDiscovery]=useState<{backendId:string;models:DiscoveredModel[]}|null>(null),[discoverySelection,setDiscoverySelection]=useState<Set<string>>(new Set()),[discoveryFilter,setDiscoveryFilter]=useState(""),[discoverySort,setDiscoverySort]=useState<{key:string;dir:"asc"|"desc"}>({key:"id",dir:"asc"}),[overrideWorkerModelId,setOverrideWorkerModelId]=useState(""),[overrideFetchRaw,setOverrideFetchRaw]=useState("");
 const[overrideSource,setOverrideSource]=useState(DEFAULT_MODEL_OVERRIDE_SOURCE),[overrideDirty,setOverrideDirty]=useState(false),[overrideStatus,setOverrideStatus]=useState("");
 const[backendEditorModes,setBackendEditorModes]=useState<Record<string,ModelEditorControlId>>({});
 const[backendSecondaryEditorModes,setBackendSecondaryEditorModes]=useState<Record<string,ModelEditorControlId>>({});
 const[backendEditorDisplayModes,setBackendEditorDisplayModes]=useState<Record<string,ModelEditorDisplayMode>>({});
 const[backendEditorTabSets,setBackendEditorTabSets]=useState<Record<string,ModelEditorTabSet>>({});
 const[splitOrientation,setSplitOrientation]=useState<"left"|"right"|"up"|"down">("right");
 const[enablementRequest,setEnablementRequest]=useState<EnablementRequest|null>(null);
 const load=async()=>{const next=await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/snapshot`) as Snapshot;setSnapshot(next);return next};
 useEffect(()=>{setOpenDocs([]);setActiveKey(null);setCompareKey(null);void load().catch(r=>setError(String(r)))},[workspaceId]);
 const systems=useMemo(()=>snapshot?.systems||[],[snapshot]);const backends=useMemo(()=>(snapshot?.backends||[]).filter(isLlmBackend),[snapshot]);const nodes=catalogMode==="systems"?[]:snapshot?.models||[];
 const enabledWorkerModels=useMemo(()=>nodes.filter(row=>row.document&&row.document.enabled!==false).map(row=>({id:row.document!.id,label:row.document!.label||row.document!.id})),[nodes]);
 useEffect(()=>{if(!overrideWorkerModelId&&enabledWorkerModels[0]?.id)setOverrideWorkerModelId(enabledWorkerModels[0].id)},[enabledWorkerModels,overrideWorkerModelId]);
 const backendIds=useMemo(()=>new Set(backends.flatMap(record=>record.document?.id?[record.document.id]:[])),[backends]);
 const modelRole=(document:ModelDef):NodeKind=>document.kind==="profile"||(!backendIds.has(modelParent(document))&&Boolean(modelParent(document)))?"preset":"model";
 const items=useMemo<CatalogItem[]>(()=>catalogMode==="systems"?systems.filter(x=>x.document).map(record=>({kind:"system" as const,id:record.document!.id,label:record.document!.label||record.document!.id,record})):[...backends.filter(x=>x.document).map(record=>({kind:"backend" as const,id:record.document!.id,label:record.document!.label||record.document!.id,record})),...nodes.filter(x=>x.document).map(record=>({kind:modelRole(record.document!),id:record.document!.id,label:record.document!.label||record.document!.id,record}))],[catalogMode,systems,backends,nodes,backendIds]);
 const recordsById=useMemo(()=>new Map(items.map(item=>[item.id,item.record as RecordFile<ModelResource>])),[items]);
 const dependencyIdsFor=(resourceId:string)=>{const found:string[]=[];const visit=(id:string)=>{const document=recordsById.get(id)?.document;if(!document)return;for(const dependencyId of relationshipIds(document.dependsOn)){if(found.includes(dependencyId))continue;found.push(dependencyId);visit(dependencyId)}};visit(resourceId);return found};
 const dependentIdsFor=(resourceId:string)=>{const found:string[]=[];const visit=(id:string)=>{const declared=relationshipIds(recordsById.get(id)?.document?.dependedOnBy);for(const item of items){const document=item.record.document as ModelResource|undefined;if(document&&relationshipIds(document.dependsOn).includes(id)&&!declared.includes(item.id))declared.push(item.id)}for(const dependentId of declared){if(found.includes(dependentId)||!recordsById.has(dependentId))continue;found.push(dependentId);visit(dependentId)}};visit(resourceId);return found};
 const resourceEnablementFor=(resourceId:string,trail:string[]=[]):ResourceEnablement=>{const record=recordsById.get(resourceId),document=record?.document;if(!record||!document||trail.includes(resourceId))return{enabled:false,source:"dependency"};if(typeof record.resolved?.enabled==="boolean")return{enabled:record.resolved.enabled,source:document.enabled===false?"self":record.resolved.enabled?"self":"dependency"};const dependencies=relationshipIds(document.dependsOn).map(id=>resourceEnablementFor(id,[...trail,resourceId]));return resolveResourceEnablement(document,dependencies)};
 const exampleFor=(document:ModelResource|null):ExampleExecute|null=>{let current=document;const visited=new Set<string>();while(current&&!visited.has(current.id)){visited.add(current.id);if(current.example_execute)return current.example_execute;if(current.kind==="backend"||current.kind==="system")return null;const parent=items.find(item=>item.id===modelParent(current as ModelDef))?.record.document as ModelResource|undefined;current=parent||null}return null};
 const perform=async(work:()=>Promise<void>)=>{setBusy(true);setError(null);try{await work()}catch(r){setError(r instanceof Error?r.message:String(r))}finally{setBusy(false)}};
 const open=(record:RecordFile<ModelResource>)=>{const key=recordKey(record);setOpenDocs(current=>current.some(doc=>doc.key===key)?current:[...current,{key,record,source:record.document?JSON.stringify(record.document,null,2):"",dirty:Boolean(record.isNew)}]);setActiveKey(key)};
 const close=(key:string)=>{setOpenDocs(current=>{const index=current.findIndex(doc=>doc.key===key);const next=current.filter(doc=>doc.key!==key);if(activeKey===key)setActiveKey(next[Math.max(0,index-1)]?.key||next[0]?.key||null);if(compareKey===key)setCompareKey(null);return next})};
 useEffect(()=>{if(snapshot&&openDocs.length===0){const parameters=new URLSearchParams(window.location.search);const requestedId=parameters.get("edit")||parameters.get("resource");const pool=catalogMode==="systems"?systems:[...backends,...nodes];const requested=pool.find(row=>row.document?.id===requestedId);if(requested)open(requested as RecordFile<ModelResource>);else if(catalogMode==="systems"&&systems[0])open(systems[0] as RecordFile<ModelResource>);else if(topMenuMode==="discover"&&backends[0])open(backends[0] as RecordFile<ModelResource>);else if(nodes[0])open(nodes[0] as RecordFile<ModelResource>);else if(backends[0])open(backends[0] as RecordFile<ModelResource>)}},[snapshot,topMenuMode]);
 const updateSource=(key:string,source:string)=>setOpenDocs(current=>current.map(doc=>doc.key===key?{...doc,source,dirty:true}:doc));
 const active=openDocs.find(doc=>doc.key===activeKey)||null;
 useEffect(()=>{const focusedId=active?.record.document?.id;const url=new URL(window.location.href);if(focusedId)url.searchParams.set("edit",focusedId);else url.searchParams.delete("edit");if(url.href!==window.location.href)window.history.replaceState({},"",url)},[activeKey,active?.record.document?.id]);
 const chooseComparison=()=>{if(compareKey){setCompareKey(null);return}if(activeKey)setCompareKey(activeKey)};
 const saveDoc=(doc:OpenDocument,location?:WorkspaceResourceLocation)=>perform(async()=>{let document:ModelResource;try{document=JSON.parse(doc.source) as ModelResource}catch{throw new Error("Resource source is invalid")};if((document.kind==="backend"||document.kind==="system")&&!document.provider)throw new Error(`${document.kind==="system"?"System":"Backend"} requires provider`);if(document.kind!=="backend"&&document.kind!=="system"){const implementedId=modelParent(document);if(!implementedId)throw new Error("Model requires implements");document={...document,kind:"model",implements:implementsResource(implementedId)}}const targetWorkspaceId=location?.workspaceId||workspaceId;const directory=document.kind==="system"?"design/systems":document.kind==="backend"?"design/backends":"design/models";const path=location?.path||(!doc.record.isNew?doc.record.path:`${directory}/${slug(document.id)}.${document.kind}.json`);const result=await request(`/workbench/workspaces/${encodeURIComponent(targetWorkspaceId)}/file`,{method:"PUT",body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});if(targetWorkspaceId===workspaceId){const next=await load();const pool:RecordFile<ModelResource>[]=[...(next.systems||[]),...(next.backends||[]),...(next.models||[])];const saved=pool.find(row=>row.document?.id===document.id);if(saved){const newKey=recordKey(saved);setOpenDocs(current=>current.map(item=>item.key===doc.key?{key:newKey,record:saved,source:JSON.stringify(saved.document,null,2),dirty:false}:item));if(activeKey===doc.key)setActiveKey(newKey);if(compareKey===doc.key)setCompareKey(newKey)}}else{const saved:RecordFile<ModelResource>={path:String(result.file?.path||path),source:"workspace",workspaceId:targetWorkspaceId,document};const newKey=recordKey(saved);setOpenDocs(current=>current.map(item=>item.key===doc.key?{key:newKey,record:saved,source:JSON.stringify(document,null,2),dirty:false}:item));if(activeKey===doc.key)setActiveKey(newKey);if(compareKey===doc.key)setCompareKey(newKey)}});
 const loadDoc=(doc:OpenDocument,location:WorkspaceResourceLocation)=>perform(async()=>{const payload=await request(`/workbench/workspaces/${encodeURIComponent(location.workspaceId)}/file?path=${encodeURIComponent(location.path)}`);const raw=String(payload.file?.content||"");let source=raw;let document:ModelResource;try{document=JSON.parse(raw) as ModelResource}catch{source=mettaDocumentToJson(raw);document=JSON.parse(source) as ModelResource}const record:RecordFile<ModelResource>={path:String(payload.file?.path||location.path),source:location.workspaceId==="shared_library_system"?"shared":"workspace",workspaceId:location.workspaceId,document};const newKey=recordKey(record);setOpenDocs(current=>current.map(item=>item.key===doc.key?{key:newKey,record,source:JSON.stringify(document,null,2),dirty:false}:item));if(activeKey===doc.key)setActiveKey(newKey);if(compareKey===doc.key)setCompareKey(newKey)});
 const setResourceEnabled=(_doc:OpenDocument,document:ModelResource,enabled:boolean)=>{
  const dependencyIds=dependencyIdsFor(document.id);
  const blockedByDependency=enabled&&dependencyIds.some(id=>{
   const record=recordsById.get(id);
   return record?.document?.enabled===false||record?.resolved?.enabled===false;
  });
  setEnablementRequest({resourceId:document.id,enabled,includeDependencies:blockedByDependency,includeDependents:false});
 };
 const applyResourceEnablement=()=>perform(async()=>{
  if(!enablementRequest)return;
  const ids=new Set([enablementRequest.resourceId]);
  if(enablementRequest.includeDependencies)for(const id of dependencyIdsFor(enablementRequest.resourceId))ids.add(id);
  if(enablementRequest.includeDependents)for(const id of dependentIdsFor(enablementRequest.resourceId))ids.add(id);
  for(const id of ids){
   const record=recordsById.get(id);
   const document=record?.document;
   if(!record||!document)throw new Error(`resource not found: ${id}`);
   await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/file`,{
    method:"PUT",
    body:JSON.stringify({path:record.path,content:JSON.stringify({...document,enabled:enablementRequest.enabled},null,2)}),
   });
  }
  const next=await load();
  const pool:RecordFile<ModelResource>[]=[...(next.systems||[]),...(next.backends||[]),...(next.models||[])];
  const refreshedById=new Map(pool.filter(record=>record.document).map(record=>[record.document!.id,record]));
  const keyChanges=new Map<string,string>();
  const refreshedOpenDocs=openDocs.map(openDocument=>{
   const id=openDocument.record.document?.id;
   const refreshed=id?refreshedById.get(id):null;
   if(!refreshed)return openDocument;
   const key=recordKey(refreshed);
   keyChanges.set(openDocument.key,key);
   return {key,record:refreshed,source:JSON.stringify(refreshed.document,null,2),dirty:false};
  });
  setOpenDocs(refreshedOpenDocs);
  setActiveKey(current=>current?keyChanges.get(current)||current:current);
  setCompareKey(current=>current?keyChanges.get(current)||current:current);
  setEnablementRequest(null);
 });
 const newBackend=()=>{const systemMode=catalogMode==="systems";const id=`${systemMode?"system":"backend"}-${Date.now().toString(36)}`;const document:ModelResource=systemMode?{kind:"system",id,label:"New System",description:"Configure a runtime, agent, MCP server, or plugin.",provider:"system",systemType:"plugin",enabled:true,capabilities:["system.execute"],configuration:{}}:{kind:"backend",id,label:"New LLM Backend",description:"Configure the provider endpoint before pulling models.",provider:"openai",enabled:true,capabilities:["llm"],configuration:{baseUrl:"",apiKeyEnvironmentVariable:""},modelDefaults:{}};open({path:systemMode?`design/systems/${slug(id)}.system.json`:`design/backends/${slug(id)}.backend.json`,source:workspaceId==="shared"?"shared":"workspace",workspaceId,document,isNew:true})};
 const newImplementation=(parent:CatalogItem,role:"model"|"preset")=>{const id=`${parent.id}-${role}`;const document:ModelDef={kind:"model",id,label:`${parent.label} ${role}`,implements:implementsResource(parent.id),inheritsFrom:inheritsFromResource(parent.id),dependsOn:dependsOnResource(parent.id),enabled:true,defaults:{temperature:0,topP:1,maxOutputTokens:12000,reasoningEffort:"medium",timeoutSeconds:300}};open({path:`design/models/${slug(id)}.model.json`,source:workspaceId==="shared"?"shared":"workspace",workspaceId,document,isNew:true})};
 const pullModels=(backendId:string)=>perform(async()=>{const result=await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/models/discover/${encodeURIComponent(backendId)}`);setDiscovery({backendId,models:result.models||[]});setDiscoverySelection(new Set())});
 const purgeAndReload=async()=>{setSnapshot(null);setOpenDocs([]);setActiveKey(null);setCompareKey(null);setDiscovery(null);setDiscoverySelection(new Set());await load()};
 const importModels=(backendId:string)=>perform(async()=>{if(!discovery)return;const models=discovery.models.filter(model=>model.status!=="missing"&&discoverySelection.has(model.id));if(!models.length)throw new Error("Select at least one new or changed model");await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/models/import/${encodeURIComponent(backendId)}`,{method:"POST",body:JSON.stringify({models,overwrite:true})});await purgeAndReload()});
 const removeMissing=(backendId:string)=>perform(async()=>{if(!discovery)return;const resourceIds=discovery.models.filter(model=>model.status==="missing"&&discoverySelection.has(model.id)).map(model=>model.resourceId).filter(Boolean);if(!resourceIds.length)throw new Error("Select at least one missing model");await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/models/remove-missing/${encodeURIComponent(backendId)}`,{method:"POST",body:JSON.stringify({resourceIds})});await purgeAndReload()});
 const fetchModelOverrides=(backendId:string)=>perform(async()=>{const discoveryForBackend=(discovery&&discovery.backendId===backendId)?discovery:null;if(!discoveryForBackend)throw new Error("Pull models first.");if(!overrideWorkerModelId)throw new Error("Select an LLM worker model.");const discovered=discoveryForBackend.models||[];const candidates=discovered.filter(model=>discoverySelection.has(model.id)&&model.resourceId);const selected=candidates.length?candidates:discovered.filter(model=>(model.status==="new"||model.status==="changed")&&model.resourceId);if(!selected.length)throw new Error("Select discovered models (or leave none selected and keep new/changed rows available).");const prompt=["Return one strict JSON object only (no markdown).","Schema: {\"kind\":\"model_overridden_properties\",\"id\":\"model_overridden_properties\",\"models\":{ \"<resourceId>\": {\"capabilities\":{...optional boolean flags...}, \"limits\":{...optional token/input/output limits...}, \"defaults\":{...optional invocation defaults...}, \"notes\":\"optional\", \"sources\":[\"optional urls\"] }}}.","Grovel trusted public web sources for each selected model and extract high-confidence capability facts such as vision, multimodal, audio, summary, and token limits.","Use backend/model-declared metadata as primary truth; add overrides only where public evidence is high confidence.","Never infer capabilities from categories.","Rows to evaluate:",JSON.stringify(selected.map(model=>({resourceId:model.resourceId,id:model.id,label:model.label,status:model.status,capabilities:model.capabilities||{},limits:model.limits||{},pricing:model.pricing||{},properties:model.properties||{}})),null,2)].join("\n\n");const invocation=await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/models/${encodeURIComponent(overrideWorkerModelId)}/invoke`,{method:"POST",body:JSON.stringify({prompt,timeoutSeconds:240})});const raw=typeof invocation.text==="string"?invocation.text:JSON.stringify(invocation,null,2);setOverrideFetchRaw(raw);const parsed=parseJsonObject(raw);if(!parsed)throw new Error("LLM response was not parseable JSON.");const nextModels=((parsed.models&&typeof parsed.models==="object")?parsed.models:{}) as Record<string,Record<string,unknown>>;let existing:ModelOverrideDocument={kind:"model_overridden_properties",id:"model_overridden_properties",models:{}};try{const payload=await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/file?path=${encodeURIComponent(MODEL_OVERRIDE_PATH)}`);const loaded=parseJsonObject(String(payload.file?.content||""));if(loaded&&loaded.kind==="model_overridden_properties"&&loaded.id==="model_overridden_properties"&&loaded.models&&typeof loaded.models==="object")existing=loaded as ModelOverrideDocument}catch{}const merged:ModelOverrideDocument={kind:"model_overridden_properties",id:"model_overridden_properties",models:{...(existing.models||{}),...nextModels},updatedByModel:overrideWorkerModelId,updatedAt:new Date().toISOString(),sources:["llm_fetcher_web_capabilities"]};const nextSource=`${JSON.stringify(merged,null,2)}\n`;await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/file`,{method:"PUT",body:JSON.stringify({path:MODEL_OVERRIDE_PATH,content:nextSource})});setOverrideSource(nextSource);setOverrideDirty(false);setOverrideStatus("Overrides updated from discovered web capability fetch.");await load()});
 const executeModelExample=async(modelId:string,args:Record<string,unknown>)=>request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/models/${encodeURIComponent(modelId)}/example-invoke`,{method:"POST",body:JSON.stringify({arguments:args})});
 useEffect(()=>{if(catalogMode!=="models"||topMenuMode!=="discover")return;const activeDocument=active?.record.document as ModelResource|undefined;const backendId=(activeDocument?.kind==="backend"?activeDocument.id:(backends[0]?.document?.id||""));if(!backendId)return;if(!discovery||discovery.backendId!==backendId){void pullModels(backendId);return}const suggested=new Set(discovery.models.filter(model=>model.status==="new"||model.status==="changed").map(model=>model.id));if(suggested.size&&discoverySelection.size===0)setDiscoverySelection(suggested)},[catalogMode,topMenuMode,active?.key,backends,discovery?.backendId]);
 const loadOverrideDocument=async()=>{setOverrideStatus("");try{const payload=await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/file?path=${encodeURIComponent(MODEL_OVERRIDE_PATH)}`);const loaded=parseJsonObject(String(payload.file?.content||""));if(loaded&&loaded.kind==="model_overridden_properties"&&loaded.id==="model_overridden_properties"&&loaded.models&&typeof loaded.models==="object"){setOverrideSource(`${JSON.stringify(loaded,null,2)}\n`);setOverrideDirty(false);return}}catch{}setOverrideSource(DEFAULT_MODEL_OVERRIDE_SOURCE);setOverrideDirty(false)};
 const saveOverrideDocument=()=>perform(async()=>{const parsed=parseJsonObject(overrideSource);if(!parsed)throw new Error("Override document must be valid JSON.");if(parsed.kind!=="model_overridden_properties"||parsed.id!=="model_overridden_properties"||!parsed.models||typeof parsed.models!=="object")throw new Error("Override document must include kind/id/models for model_overridden_properties.");const normalized=`${JSON.stringify(parsed,null,2)}\n`;await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/file`,{method:"PUT",body:JSON.stringify({path:MODEL_OVERRIDE_PATH,content:normalized})});setOverrideSource(normalized);setOverrideDirty(false);setOverrideStatus("Overrides saved to design/models/model_overridden_properties.json.");await load()});
 useEffect(()=>{if(catalogMode==="models"&&topMenuMode==="override"){void loadOverrideDocument()}},[catalogMode,topMenuMode,workspaceId]);
 const relationshipParentIds=(document:ModelResource,mode:TreeRelationshipMode)=>relationshipIds(
  mode==="implementation"
   ? ("implements" in document?document.implements:undefined)
   : mode==="inheritance"
    ? ("inheritsFrom" in document?document.inheritsFrom:undefined)
    : document.dependsOn,
 );
 const relationshipForest=(mode:TreeRelationshipMode)=>{
  const childrenByParent=new Map<string,CatalogItem[]>();
  for(const item of items){
   const document=item.record.document as ModelResource|undefined;
   if(!document)continue;
   for(const parentId of relationshipParentIds(document,mode)){
    const children=childrenByParent.get(parentId)||[];
    children.push(item);
    childrenByParent.set(parentId,children);
   }
  }
  const itemIds=new Set(items.map(item=>item.id));
  const roots=items.filter(item=>{
   const document=item.record.document as ModelResource|undefined;
   return !document||!relationshipParentIds(document,mode).some(parentId=>itemIds.has(parentId));
  });
  const renderRelationshipTree=(item:CatalogItem,depth=0,trail:string[]=[]):JSX.Element=>{
   const backend=item.kind==="backend";
   const system=item.kind==="system";
   const systemMode=catalogMode==="systems";
   const rootResource=backend||system;
   const record=item.record as RecordFile<ModelResource>;
   const nested=(childrenByParent.get(item.id)||[]).filter(child=>!trail.includes(child.id));
   const selected=active?.record.document?.id===item.id;
   const itemEnablement=resourceEnablementFor(item.id);
   const relationLabel=mode==="implementation"?"implementations":mode==="inheritance"?"inheritors":"dependents";
   return <ArtifactTreeBranch className={`inheritance-node ${layout} ${item.kind}-node`} childrenClassName="inheritance-children" key={`${mode}:${trail.join(">")}:${item.kind}:${item.id}`} label={item.label} initialCollapsed={backend&&!systemMode} searchValue={{document:record.document,resolved:record.resolved}} style={{"--tree-depth":depth} as React.CSSProperties} header={<div className="inheritance-row"><button className={`inheritance-main ${enablementClass(itemEnablement)} ${selected?"selected":""}`} onClick={()=>open(record)}><span>{item.kind.toUpperCase()}</span><b>{item.label}</b><small>{rootResource?(record.document as BackendDef|SystemDef)?.provider:((record as RecordFile<ModelDef>).resolved?.model||(record.document as ModelDef)?.model||`implements ${modelParent(record.document as ModelDef)}`)}</small><div className="inheritance-status"><em>{systemMode?"callable execution system":`${nested.length} ${relationLabel}`}{!rootResource&&` · temp ${String((((record as RecordFile<ModelDef>).resolved?.defaults||(record.document as ModelDef)?.defaults||{}).temperature)??"—")}`}</em><ResourceEnablementBadge state={itemEnablement}/></div></button>{mode==="implementation"&&!systemMode&&(backend?<button className="hier-mini" onClick={()=>newImplementation(item,"model")}>+ model</button>:<button className="hier-mini" onClick={()=>newImplementation(item,"preset")}>+ preset</button>)}</div>}>{nested.length?nested.map(child=>renderRelationshipTree(child,depth+1,[...trail,item.id])):undefined}</ArtifactTreeBranch>;
  };
  return <div className={`inheritance-tree ${layout}`} data-relationship-mode={mode}>{roots.map(root=>renderRelationshipTree(root))}</div>;
 };
     const renderEditor = (doc: OpenDocument, secondary = false) => {
  let document: ModelResource | null = null;
  try {
   document = JSON.parse(doc.source) as ModelResource;
  } catch {
   /* show raw if invalid */
  }
  const backend = document?.kind === "backend";
  const system = document?.kind === "system";
  const editable=!!document;
  const inSplit=!!compareKey;
  const paneStateKey=secondary?`${doc.key}#2`:doc.key;
  const availableEditorControls:ModelEditorControlId[]=["file","resource",...(backend?["actions" as const]:[]),"runner"];
  const backendEditorTabSet=backendEditorTabSets[paneStateKey]||"ctx";
  const selectedEditorControls=availableEditorControls;
  const backendEditorMode=editable&&selectedEditorControls.includes(backendEditorModes[paneStateKey])
   ? backendEditorModes[paneStateKey]
   : secondary?"file":"resource";
  const defaultSecondaryMode=selectedEditorControls.find(control=>control!==backendEditorMode)||backendEditorMode;
  const backendSecondaryEditorMode=editable&&selectedEditorControls.includes(backendSecondaryEditorModes[paneStateKey])
   ? backendSecondaryEditorModes[paneStateKey]
   : defaultSecondaryMode;
  const backendEditorDisplayMode=editable?(inSplit?"tabs":(backendEditorDisplayModes[paneStateKey]||"tabs")):"single";
  const showBackendSection=(section:ModelEditorControlId)=>backendEditorDisplayMode==="stacked"
   || backendEditorMode===section
   || ((backendEditorDisplayMode==="split-v"||backendEditorDisplayMode==="split-h")&&backendSecondaryEditorMode===section);
  const selectBackendSection=(section:ModelEditorControlId)=>{setBackendEditorModes(current=>({...current,[paneStateKey]:section}));setBackendEditorDisplayModes(current=>({...current,[paneStateKey]:"tabs"}))};
  const backendId = document?.id || "";
  const resourceEnabled = document
    ? (doc.dirty
      ? document.enabled !== false
      : (typeof doc.record.resolved?.enabled === "boolean"
        ? doc.record.resolved.enabled
        : document.enabled !== false))
    : false;
   const resolvedSource = document
    ? backend
     ? JSON.stringify({...doc.record.resolved,provider:(document as BackendDef).provider,official:(document as BackendDef).official,enabled:(document as BackendDef).enabled,capabilities:(document as BackendDef).capabilities,configuration:(document as BackendDef).configuration,modelDefaults:(document as BackendDef).modelDefaults},null,2)
     : system
       ? JSON.stringify(doc.record.resolved || {provider:(document as SystemDef).provider,systemType:(document as SystemDef).systemType,capabilities:document.capabilities||[]},null,2)
       : JSON.stringify(doc.record.resolved || {},null,2)
    : "";
   const inheritedParentId = document
    ? (!backend && !system ? relationshipIds((document as ModelDef).inheritsFrom)[0] : "")
      || doc.record.resolved?.parentId
      || doc.record.resolved?.backendId
    : "";
   const inheritedParent = inheritedParentId ? items.find(item=>item.id===inheritedParentId) : null;
   const inheritedParentHref = inheritedParentId
    ? `?workspace=${encodeURIComponent(workspaceId)}&view=${catalogMode==="systems"?"systems":"llms"}&edit=${encodeURIComponent(inheritedParentId)}`
    : "";
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
   <div className={"model-editor-scroll " + (secondary ? "secondary " : "") + (backendEditorDisplayMode==="stacked" ? "stack-mode" : "tabs-mode")}>
    <div className={`model-editor-document model-control-${backendEditorDisplayMode}`}>
     <div className="model-editor-toolbar">
      <div className="model-editor-identity">
       <span className={"model-kind-badge " + (document?.kind || "")}>{document?.kind?.toUpperCase()}</span>
       <b>{document?.label || document?.id || "New Item"}</b>
       <small>{displayResourcePath(doc.record.path)}</small>
      </div>
      <div className="model-editor-actions">
       {backend && <button className="backend-edit-source" onClick={()=>selectBackendSection("file")} aria-pressed={backendEditorDisplayMode==="tabs"&&backendEditorMode==="file"}>{backendEditorDisplayMode==="tabs"&&backendEditorMode==="file"?"Editing File":"Edit File"}</button>}
       {document && !backend && <button
        className={resourceEnabled ? "disable-resource" : "enable-resource"}
        onClick={() => setResourceEnabled(doc, document, !resourceEnabled)}
        disabled={busy}
        aria-pressed={!resourceEnabled}
        title={`${resourceEnabled ? "Disable" : "Enable"} this ${document.kind} resource`}
       >{resourceEnabled ? "Disable Resource" : "Enable Resource"}</button>}
       <div className="super-control-tab-set" role="group" aria-label="Model Super Control tab set">
        <b>TABS</b>
        <span className="super-control-tab-set-buttons">
         <button type="button" className={backendEditorTabSet==="all"?"active":""} aria-pressed={backendEditorTabSet==="all"} onClick={()=>setBackendEditorTabSets(current=>({...current,[paneStateKey]:"all"}))}>ALL</button>
         <button type="button" className={backendEditorTabSet==="ctx"?"active":""} aria-pressed={backendEditorTabSet==="ctx"} onClick={()=>setBackendEditorTabSets(current=>({...current,[paneStateKey]:"ctx"}))}>CTX</button>
        </span>
       </div>
       <label className="super-control-mode-switcher">
        <span>DISPLAY</span>
        <select aria-label="Model Super Control display mode" value={backendEditorDisplayMode} onChange={event=>setBackendEditorDisplayModes(current=>({...current,[paneStateKey]:event.target.value as ModelEditorDisplayMode}))}>
         <option value="tabs">Tabs</option>
         <option value="stacked">Stacked</option>
         <option value="single">Single</option>
         <option value="split-v">SplitV</option>
         <option value="split-h">SplitH</option>
        </select>
       </label>
       {(backendEditorDisplayMode==="single"||backendEditorDisplayMode==="split-v"||backendEditorDisplayMode==="split-h")&&<label className="super-control-pane-selector">
        <span>{backendEditorDisplayMode==="single"?"TAB":backendEditorDisplayMode==="split-v"?"LEFT":"TOP"}</span>
        <select aria-label="Primary Model Super Control tab" value={backendEditorMode} onChange={event=>setBackendEditorModes(current=>({...current,[paneStateKey]:event.target.value as ModelEditorControlId}))}>{selectedEditorControls.map(control=><option key={control} value={control}>{control==="file"?"File":control==="resource"?"Resource & Inheritance":control==="actions"?"Backend Actions":"Universal Execution Runner"}</option>)}</select>
       </label>}
       {(backendEditorDisplayMode==="split-v"||backendEditorDisplayMode==="split-h")&&<label className="super-control-pane-selector">
        <span>{backendEditorDisplayMode==="split-v"?"RIGHT":"BOTTOM"}</span>
        <select aria-label="Secondary Model Super Control tab" value={backendSecondaryEditorMode} onChange={event=>setBackendSecondaryEditorModes(current=>({...current,[paneStateKey]:event.target.value as ModelEditorControlId}))}>{selectedEditorControls.map(control=><option key={control} value={control}>{control==="file"?"File":control==="resource"?"Resource & Inheritance":control==="actions"?"Backend Actions":"Universal Execution Runner"}</option>)}</select>
       </label>}
       <button className="danger" onClick={() => close(doc.key)}>Close</button>
      </div>
     </div>

     {backend && showBackendSection("actions") && discoveryForThis && (
      <div className="model-discovery">
       <div className="llm-subhead">
        <b>{topMenuMode==="discover"?"DISCOVER PUBLIC PROPERTIES":"DISCOVERED MODELS"}</b>
        <span>{discoveredModels.length} available · {discoveredModels.filter(m => m.status === "new").length} new · {discoveredModels.filter(m => m.status === "changed").length} changed · {discoveredModels.filter(m => m.status === "missing").length} missing · {discoverySelection.size} selected</span>
        {topMenuMode==="discover"&&<small>Select a worker model, then grovel public web capability facts (vision, multimodal, audio, token limits) into overrides.</small>}
        <div className="model-discovery-filter">
          <input
            type="text"
            placeholder="Filter: +key=val, ~key=val, +text, ~text..."
            value={discoveryFilter}
            onChange={e => setDiscoveryFilter(e.target.value)}
          />
        </div>
        <div className="model-discovery-actions">
         <button onClick={() => setDiscoverySelection(new Set(discoveredModels.map(m => m.id)))} disabled={discoveredModels.length===0 || discoverySelection.size===discoveredModels.length}>Select all</button>
         <button onClick={() => setDiscoverySelection(new Set(discoveredModels.filter(m => m.status === "new" || m.status === "changed").map(m => m.id)))}>Select new/changed</button>
         <button onClick={() => setDiscoverySelection(new Set(discoveredModels.filter(m => m.status === "missing").map(m => m.id)))}>Select missing</button>
         <button onClick={() => setDiscoverySelection(new Set())}>Clear selection</button>
         {topMenuMode==="discover"&&<><label><span>Grovel worker model</span><select value={overrideWorkerModelId} onChange={event=>setOverrideWorkerModelId(event.target.value)}>{enabledWorkerModels.map(model=><option key={model.id} value={model.id}>{model.label}</option>)}</select></label><button onClick={() => fetchModelOverrides(backendId)} disabled={busy||!enabledWorkerModels.length}>Grovel web capabilities</button></>}
         <button className="primary" onClick={() => importModels(backendId)} disabled={busy || !discoveredModels.some(m => m.status !== "missing" && discoverySelection.has(m.id))}>Import/overwrite selected</button>
         <button className="danger" onClick={() => removeMissing(backendId)} disabled={busy || !discoveredModels.some(m => m.status === "missing" && discoverySelection.has(m.id))}>Remove missing</button>
        </div>
        {topMenuMode==="discover"&&overrideFetchRaw && <details><summary>Web grovel raw model response</summary><pre>{overrideFetchRaw}</pre></details>}
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

     {editable && backendEditorDisplayMode==="tabs" && <nav className="backend-aggregate-tabs" aria-label="Editor modes" role="tablist">
      <span className="backend-tabs-label">EDITORS</span>
      <button role="tab" aria-selected={backendEditorMode==="file"} className={backendEditorMode==="file"?"active":""} onClick={()=>selectBackendSection("file")}>File</button>
      <button role="tab" aria-selected={backendEditorMode==="resource"} className={backendEditorMode==="resource"?"active":""} onClick={()=>selectBackendSection("resource")}>Resource &amp; Inheritance</button>
      {backend && <button role="tab" aria-selected={backendEditorMode==="actions"} className={backendEditorMode==="actions"?"active":""} onClick={()=>selectBackendSection("actions")}>Backend Actions</button>}
      <button role="tab" aria-selected={backendEditorMode==="runner"} className={backendEditorMode==="runner"?"active":""} onClick={()=>selectBackendSection("runner")}>Universal Execution Runner</button>
     </nav>}

     {(!editable||showBackendSection("file")) && <div className={`model-visible-editor ${backendEditorDisplayMode==="stacked"?"backend-stacked-section":""}`}>
      <div className="studio-section-label">RESOURCE SOURCE</div>
      <ResourceSourceEditor value={doc.source} onChange={src => updateSource(doc.key, src)} showEnablement={false} stacked={backendEditorDisplayMode==="stacked"} fileControls={{
       currentWorkspaceId:workspaceId,
       workspaceId:workspaceId,
       originWorkspaceId:doc.record.workspaceId||workspaceId,
       relativePath:doc.record.path,
       dirty:doc.dirty,
       onSave:location=>saveDoc(doc,location),
       onLoad:location=>loadDoc(doc,location),
      }} />
     </div>}

     {editable && document && showBackendSection("resource") && <section className={`model-control-pane model-resource-inheritance ${backendEditorDisplayMode==="stacked"?"backend-stacked-section":""}`} data-model-control="resource">
      {!backend && !system && <div className="model-config-panes">
       <div className="model-config-pane">
        <div className="studio-section-label">CONFIGURATION</div>
        <ConfigForm source={doc.source} onChange={src => updateSource(doc.key, src)} items={items} effectiveEnabled={resourceEnabled} onEnabledChange={enabled=>setResourceEnabled(doc,document,enabled)} />
       </div>
      </div>}
      {system && <div className="model-config-panes">
       <div className="model-config-pane">
        <div className="studio-section-label">SYSTEM CONFIGURATION</div>
        <SystemConfigForm source={doc.source} onChange={src => updateSource(doc.key, src)} />
       </div>
      </div>}
      {backend && <div className="model-config-panes backend-resource-editor">
       <div className="backend-resource-status"><div><span>RESOURCE STATE</span><b>{resourceEnabled?"Enabled":"Disabled"}</b><small>{typeof document.enabled==="boolean"?"Declared by this backend resource":"Resolved through inheritance/defaults"}</small></div><button className={resourceEnabled?"disable-resource":"enable-resource"} onClick={()=>setResourceEnabled(doc,document,!resourceEnabled)} disabled={busy}>{resourceEnabled?"Disable Backend":"Enable Backend"}</button></div>
       <div className="model-config-pane"><div className="studio-section-label">CONFIGURATION</div><BackendConfigForm source={doc.source} onChange={src=>updateSource(doc.key,src)}/></div>
      </div>}
      <div className="model-visible-editor resolved-resource-editor">
       <div className="resolved-resource-heading">
        <div className="studio-section-label">EDITABLE RESOURCE OVERRIDE — save writes this workspace resource</div>
        {inheritedParentId&&<a href={inheritedParentHref} onClick={event=>{if(!inheritedParent)return;event.preventDefault();open(inheritedParent.record as RecordFile<ModelResource>)}}>Edit parent · {inheritedParent?.label||inheritedParentId}</a>}
       </div>
       <ResourceSourceEditor value={doc.source} onChange={source=>updateSource(doc.key,source)} showEnablement={false} label="Editable resource override" fileControls={{
         currentWorkspaceId:workspaceId,
         workspaceId:workspaceId,
         originWorkspaceId:doc.record.workspaceId||workspaceId,
         relativePath:doc.record.path,
         dirty:doc.dirty,
         allowLoadDifferent:false,
         onSave:location=>saveDoc(doc,location),
         onLoad:location=>loadDoc(doc,location),
       }} />
       <details className="resolved-resource-preview"><summary>Resolved inheritance preview</summary><pre>{resolvedSource}</pre></details>
      </div>
     </section>}

     {backend && showBackendSection("actions") && document && <section className="backend-actions-editor">
      <div className="llm-subhead"><div><span>BACKEND ACTIONS</span><b>Discover, enable, inspect, and maintain this backend</b></div></div>
      <div className="backend-action-buttons"><button onClick={()=>pullModels(document.id)} disabled={busy}>Pull Models</button><button onClick={()=>setResourceEnabled(doc,document,!resourceEnabled)} disabled={busy}>{resourceEnabled?"Disable Backend":"Enable Backend"}</button></div>
      <div className="backend-inheritance-summary"><div className="studio-section-label">BACKEND DEFAULTS & CAPABILITIES</div><pre>{JSON.stringify({provider:(document as BackendDef).provider,official:(document as BackendDef).official,enabled:(document as BackendDef).enabled,capabilities:(document as BackendDef).capabilities,modelDefaults:(document as BackendDef).modelDefaults},null,2)}</pre></div>
     </section>}

     {backend && showBackendSection("runner") && document && resourceEnabled && <ResourceExecutionPlayground workspaceId={workspaceId} resource={document} operationIds={["backend_inspect","backend_check_readiness","resource_validate"]}/>}

     {!backend && !system && document && resourceEnabled && showBackendSection("runner") && (
      <ModelResourcePlayground workspaceId={workspaceId} model={document} resolved={doc.record.resolved as Record<string,unknown>|undefined} models={nodes.filter(row=>row.document).map(row=>({id:row.document!.id,label:row.document!.label,enabled:row.document!.enabled}))}/>
     )}

     {system && document && resourceEnabled && showBackendSection("runner") && (
      <ResourceExecutionPlayground workspaceId={workspaceId} resource={document}/>
     )}

     {exampleFor(document) && showBackendSection(backend?"actions":"runner") && (
      <div className="model-playground">
       <div className="studio-section-label">PLAYGROUND / EXAMPLE INVOKE</div>
       <ExampleExecutePanel contract={exampleFor(document)!} onExecute={args => executeModelExample(document!.id, args)} />
      </div>
     )}
    </div>
   </div>
  );
 };
 if(catalogMode==="models"&&topMenuMode==="override")return <section className="resource-view"><div className="resource-heading"><div><span>MODEL OVERRIDE PROPERTIES</span><h1>Edit capability overrides</h1><p>Edit the filesystem-backed overrides at <code>{MODEL_OVERRIDE_PATH}</code>. These values are honored first for model capability and limit metadata.</p></div><div className="studio-actions"><button onClick={()=>void loadOverrideDocument()} disabled={busy}>Reload</button><button className="primary" onClick={saveOverrideDocument} disabled={busy||!overrideDirty}>Save overrides</button></div></div>{overrideStatus&&<div className="validation good">{overrideStatus}</div>}<div className="workflow-fields"><label className="wide"><span>OVERRIDE SOURCE</span><ResourceSourceEditor value={overrideSource} onChange={value=>{setOverrideSource(value);setOverrideDirty(true);setOverrideStatus("")}} showEnablement={false} label="Edit model_overridden_properties resource directly"/></label></div></section>;
 if(!snapshot)return <section className="resource-view"><div className="studio-empty">Loading model catalog…</div></section>;
 const leftPane=(relationshipMode:TreeRelationshipMode)=>relationshipForest(relationshipMode);
 const tabs=openDocs.map(doc=>({key:doc.key,kind:doc.record.document?.kind?.toUpperCase()||"ITEM",label:doc.record.document?.label||doc.record.document?.id||doc.record.path,dirty:doc.dirty}));
 const actions=<div className="layout-switch"><button onClick={newBackend}>{catalogMode==="systems"?"+ System":"+ Backend"}</button>{discovery&&<button onClick={()=>setDiscoverySelection(new Set(discovery.models.map(model=>model.id)))} disabled={busy||discoverySelection.size===discovery.models.length}>Select all discovered</button>}{compareKey?<span className="model-split-controls"><b>COMPARE</b><button className={splitOrientation==="left"?"active":""} onClick={()=>setSplitOrientation("left")} title="Other document on the left">⬅</button><button className={splitOrientation==="right"?"active":""} onClick={()=>setSplitOrientation("right")} title="Other document on the right">➡</button><button className={splitOrientation==="up"?"active":""} onClick={()=>setSplitOrientation("up")} title="Other document above">⬆</button><button className={splitOrientation==="down"?"active":""} onClick={()=>setSplitOrientation("down")} title="Other document below">⬇</button><button onClick={chooseComparison}>Single document</button></span>:<button disabled={openDocs.length<2} onClick={chooseComparison}>Compare documents</button>}<button className={layout==="tiles"?"active":""} onClick={()=>setLayout("tiles")}>▦ Tiles</button><button className={layout==="list"?"active":""} onClick={()=>setLayout("list")}>☷ List</button></div>;
 return <>
  <HierarchyResourceEditor workspaceId={workspaceId} categoryTree="models" eyebrow={catalogMode==="systems"?"CALLABLE SYSTEMS":"MODEL CATALOG"} title={catalogMode==="systems"?"Systems":"Models & presets"} description={catalogMode==="systems"?"Configure callable execution systems. Python, SWI-Prolog, MeTTa, the LLM caller, OmegaClaw, and Codex are peers at this level.":"Models inherit model backends; reusable presets inherit models or other presets and override invocation defaults without containing prompts."} headerActions={actions} error={error} onDismissError={()=>setError(null)} leftPane={leftPane} tabs={tabs} activeKey={activeKey} compareKey={compareKey} onActivate={setActiveKey} onClose={close} renderEditor={(key,secondary)=>{const doc=openDocs.find(item=>item.key===key);return doc?renderEditor(doc,secondary):null}} emptyEditor={<div className="studio-empty">{catalogMode==="systems"?"Select a system.":"Select a model or preset."}</div>} className="llm-model-editor model-hierarchy-page" treeClassName={`model-tree-pane ${layout}`} workspaceClassName="model-editor-workspace" tabsClassName="model-document-tabs" panesClassName={`model-editor-panes split-${splitOrientation}`}/>
  {enablementRequest&&(()=>{
   const record=recordsById.get(enablementRequest.resourceId);
   const dependencyIds=dependencyIdsFor(enablementRequest.resourceId);
   const dependentIds=dependentIdsFor(enablementRequest.resourceId);
   const action=enablementRequest.enabled?"Enable":"Disable";
   return <div className="model-enablement-backdrop" role="presentation">
    <section className="model-enablement-dialog" role="dialog" aria-modal="true" aria-label={`${action} resource scope`}>
     <div><span>RESOURCE AVAILABILITY</span><h2>{action} {record?.document?.label||enablementRequest.resourceId}</h2><p>Choose which related resources receive the same explicit state.</p></div>
     <label><input type="checkbox" checked readOnly/>This resource <small>{enablementRequest.resourceId}</small></label>
     <label className={dependencyIds.length?"":"is-unavailable"}><input type="checkbox" checked={enablementRequest.includeDependencies} disabled={!dependencyIds.length} onChange={event=>setEnablementRequest(current=>current?{...current,includeDependencies:event.target.checked}:current)}/>Dependencies <small>{dependencyIds.length?dependencyIds.join(", "):"none"}</small></label>
     <label className={dependentIds.length?"":"is-unavailable"}><input type="checkbox" checked={enablementRequest.includeDependents} disabled={!dependentIds.length} onChange={event=>setEnablementRequest(current=>current?{...current,includeDependents:event.target.checked}:current)}/>Dependents <small>{dependentIds.length?`${dependentIds.length} downstream resource(s)`:"none"}</small></label>
     <footer><button type="button" onClick={()=>setEnablementRequest(null)} disabled={busy}>Cancel</button><button type="button" className="primary" onClick={()=>void applyResourceEnablement()} disabled={busy}>{action} selected scope</button></footer>
    </section>
   </div>;
  })()}
 </>;
}
