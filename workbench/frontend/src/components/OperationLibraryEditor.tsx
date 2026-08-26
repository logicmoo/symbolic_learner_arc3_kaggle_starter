import {useEffect,useMemo,useState} from "react";
import {DEFAULT_TREE_VISIBILITY_RULES,type TreeVisibilityRules,useArtifactTreeFilter} from "./useArtifactTreeFilter";
import {RepeatSwitch,TreeViewControls} from "./TreeViewControls";
import {implementsResource,relationshipIds,specializationInheritanceMap,specializesResource} from "./resourceRelationships";
import {CategorizedArtifactTree,categoryPaths} from "./CategorizedArtifactTree";
import type {ArtifactTreeCommand} from "./ArtifactTreeBranch";
import {SuperControl} from "./UniversalArtifactEditor";
import type {
  OperationDef,
  OperationImplementationDef,
  OperationResource,
  OperationSuperControlRequest,
} from "./OperationDocumentControl";
import {ResourceEnablementBadge,enablementClass,resolveResourceEnablement} from "./resourceEnablement";
import {displayResourcePath} from "./resourcePath";
import {TreePaneResizer} from "./TreePaneResizer";
import "../styles/operation_editor.css";

type Source="shared"|"workspace";
type RecordFile<T>={path:string;source?:Source;workspaceId?:string;document?:T;error?:string;isNew?:boolean;resolved?:{enabled?:boolean;backendId?:string;defaults?:Record<string,unknown>;model?:string}};
type ModelDef={kind:"model";id:string;label?:string;implements:Record<string,unknown>;model?:string;enabled?:boolean;defaults?:Record<string,unknown>};
type PromptDef={kind:"prompt";id:string;label?:string;description?:string;text?:string|string[];variables?:string[]};
type PromptProfileDef={kind:"prompt_profile";id:string;label?:string;description?:string;prompts:string[];separator?:string};
type Snapshot={workspace:{id:string;label:string;root:string};operations:RecordFile<OperationDef>[];operationImplementations:RecordFile<OperationImplementationDef>[];models:RecordFile<ModelDef>[];prompts:RecordFile<PromptDef>[];promptLibrary?:{hierarchy?:{promptProfiles?:RecordFile<PromptProfileDef>[]}}};
type OpenDocument={key:string;record:RecordFile<OperationResource>;source:string;dirty:boolean};

const slug=(v:string)=>v.toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"")||"resource";
const recordKey=(record:RecordFile<OperationResource>)=>`${record.workspaceId||record.source||"resource"}:${record.path}:${record.document?.id||"unknown"}`;
const appearanceCategoryPath=(appearanceKey:string,itemId:string)=>{const prefix="category:";const suffix=`:${itemId}`;return appearanceKey.startsWith(prefix)&&appearanceKey.endsWith(suffix)?appearanceKey.slice(prefix.length,-suffix.length):null};
async function request(path:string,init?:RequestInit){const r=await fetch(path,{headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});const text=await r.text();let p:any;try{p=JSON.parse(text)}catch{throw new Error(text||r.statusText)}if(!r.ok)throw new Error(p.error||p.detail||r.statusText);return p;}

type SourceLanguage="prolog"|"metta"|"python";
export function OperationLibraryEditor({workspaceId,sourceLanguage}:{workspaceId:string;sourceLanguage?:SourceLanguage}){
 const[snapshot,setSnapshot]=useState<Snapshot|null>(null),[openDocs,setOpenDocs]=useState<OpenDocument[]>([]),[activeKey,setActiveKey]=useState<string|null>(null),[compareKey,setCompareKey]=useState<string|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState<string|null>(null),[navigatorCollapsed,setNavigatorCollapsed]=useState(false),[viewControlsOpen,setViewControlsOpen]=useState(false),[collapsedOperations,setCollapsedOperations]=useState<Set<string>>(()=>new Set());
 const[categoryCommand,setCategoryCommand]=useState<ArtifactTreeCommand>(null),[visibilityRules,setVisibilityRules]=useState<TreeVisibilityRules>(DEFAULT_TREE_VISIBILITY_RULES);
 const {treeRef,treeFilter,setTreeFilter,showParents,setShowParents,treeKinds}=useArtifactTreeFilter(visibilityRules);
 const load=async()=>{const next=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/snapshot`) as Snapshot;setSnapshot(next);return next};
 useEffect(()=>{setOpenDocs([]);setActiveKey(null);setCompareKey(null);void load().catch(r=>setError(String(r)))},[workspaceId]);
 const enabledModels=(snapshot?.models||[]).filter(row=>row.document&&(row.resolved?.enabled??row.document.enabled!==false));
 const prompts=snapshot?.prompts||[];
 const promptProfiles=snapshot?.promptLibrary?.hierarchy?.promptProfiles||[];
 const allImplementations=snapshot?.operationImplementations||[];
 const implementations=useMemo(()=>sourceLanguage?allImplementations.filter(row=>row.document?.implementation?.startsWith(sourceLanguage)):allImplementations,[allImplementations,sourceLanguage]);
 const specializations=useMemo(()=>{const map=new Map<string,RecordFile<OperationImplementationDef>[]>();for(const row of implementations){for(const id of relationshipIds(row.document?.implements)){const list=map.get(id)||[];list.push(row);map.set(id,list)}}return map},[implementations]);
 const perform=async(work:()=>Promise<void>)=>{setBusy(true);setError(null);try{await work()}catch(r){setError(r instanceof Error?r.message:String(r))}finally{setBusy(false)}};
 const open=(record:RecordFile<OperationResource>)=>{const key=recordKey(record);setOpenDocs(current=>current.some(doc=>doc.key===key)?current:[...current,{key,record,source:record.document?JSON.stringify(record.document,null,2):"",dirty:Boolean(record.isNew)}]);setActiveKey(key)};
 const close=(key:string)=>{setOpenDocs(current=>{const index=current.findIndex(doc=>doc.key===key);const next=current.filter(doc=>doc.key!==key);if(activeKey===key)setActiveKey(next[Math.max(0,index-1)]?.key||next[0]?.key||null);if(compareKey===key)setCompareKey(null);return next})};
 useEffect(()=>{if(snapshot&&openDocs.length===0){const requestedId=new URLSearchParams(window.location.search).get("resource");const visibleParents=(snapshot.operations||[]).filter(row=>row.document&&(!sourceLanguage||implementations.some(impl=>relationshipIds(impl.document?.implements).includes(row.document!.id))||row.document.implementation?.startsWith(sourceLanguage)));const allResources:RecordFile<OperationResource>[]=[...visibleParents,...implementations];const featured=allResources.find(row=>row.document?.id===requestedId)||(!sourceLanguage?visibleParents.find(row=>row.document?.id==="echo_into_titlecased"):undefined)||implementations[0]||visibleParents[0];if(featured)open(featured as RecordFile<OperationResource>)}},[snapshot,sourceLanguage,implementations.length]);
 const updateSource=(key:string,source:string)=>setOpenDocs(current=>current.map(doc=>doc.key===key?{...doc,source,dirty:true}:doc));
 const createSpecialization=(doc:OpenDocument,parent:OperationResource)=>{const ids=new Set([...(snapshot?.operations||[]),...(snapshot?.operationImplementations||[])].flatMap(record=>record.document?[record.document.id]:[]));for(const opened of openDocs){try{const parsed=JSON.parse(opened.source) as OperationResource;if(parsed.id)ids.add(parsed.id)}catch{/* Invalid drafts do not contribute an id. */}}const stem=`${parent.id}.specialization`;let id=stem,index=2;while(ids.has(id)){id=`${stem}_${index++}`}const implementation=sourceLanguage==="prolog"?"prolog.source":sourceLanguage==="metta"?"metta.source":"python.callable";const specialization:OperationImplementationDef={kind:"operation",id,implements:implementsResource(parent.id),label:`${parent.label||parent.id} — Specialization`,description:"Concrete Operation specialization.",categories:parent.categories,topics:parent.topics,enabled:true,implementation};const existingSpecializations=specializationInheritanceMap((parent as OperationDef).specializations);const nextSpecializations={...existingSpecializations,...specializesResource(id)};updateSource(doc.key,JSON.stringify({...parent,specializations:nextSpecializations,preferredSpecialization:(parent as OperationDef).preferredSpecialization||id},null,2));open({path:`design/operations/${slug(id)}.operation.json`,source:workspaceId==="shared"?"shared":"workspace",workspaceId,document:specialization,isNew:true})};
 const active=openDocs.find(doc=>doc.key===activeKey)||null;
 const comparison=openDocs.find(doc=>doc.key===compareKey)||null;
 const chooseComparison=()=>{if(compareKey){setCompareKey(null);return}const other=[...openDocs].reverse().find(doc=>doc.key!==activeKey);if(other)setCompareKey(other.key)};
 const saveDoc=(doc:OpenDocument)=>perform(async()=>{let document:OperationResource;try{document=JSON.parse(doc.source) as OperationResource}catch{throw new Error("Operation resource source is invalid")};if(document.kind!=="operation")throw new Error("Operation resource requires kind='operation'");const original=doc.record.path;const path=workspaceId==="shared"||doc.record.source==="workspace"?original:`design/operations/${slug(document.id)}.operation.json`;await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`,{method:"PUT",body:JSON.stringify({path,content:JSON.stringify(document,null,2)})});const next=await load();const pool:RecordFile<OperationResource>[]=[...(next.operations||[]),...(next.operationImplementations||[])];const saved=pool.find(row=>row.document?.id===document.id);if(saved){const newKey=recordKey(saved);setOpenDocs(current=>current.map(item=>item.key===doc.key?{key:newKey,record:saved,source:JSON.stringify(saved.document,null,2),dirty:false}:item));if(activeKey===doc.key)setActiveKey(newKey);if(compareKey===doc.key)setCompareKey(newKey)}});

 const renderEditor=(doc:OpenDocument,secondary=false)=>{let document:OperationResource|null=null;try{document=doc.source?JSON.parse(doc.source) as OperationResource:null}catch{document=null}const isImplementation=Boolean(document&&relationshipIds(document.implements).length);const abstract=document&&!isImplementation?document as OperationDef:null;const selectedImplementation=document&&isImplementation?document as OperationImplementationDef:null;const implementedOperation=selectedImplementation?(snapshot?.operations||[]).find(row=>row.document&&relationshipIds(selectedImplementation.implements).includes(row.document.id))?.document:null;const variants=abstract?(specializations.get(abstract.id)||[]):[];const relatedById=new Map<string,OperationResource>();for(const record of [...(snapshot?.operations||[]),...(snapshot?.operationImplementations||[])])if(record.document)relatedById.set(record.document.id,record.document);for(const opened of openDocs){try{const parsed=JSON.parse(opened.source) as OperationResource;if(parsed.id)relatedById.set(parsed.id,parsed)}catch{/* Invalid drafts are excluded from derived inheritance. */}}const control:OperationSuperControlRequest={
  kind:"operation",
  workspaceId,
  source:doc.source,
  sourceScope:doc.record.source||"resource",
  path:displayResourcePath(doc.record.path),
  dirty:doc.dirty,
  secondary,
  busy,
  variants:variants.flatMap(row=>row.document?[row.document]:[]),
  implementedOperation,
  relatedResources:[...relatedById.values()],
  models:enabledModels.flatMap(row=>row.document?[{id:row.document.id,label:row.document.label,kind:row.document.kind,model:row.resolved?.model||row.document.model,enabled:row.document.enabled}]:[]),
  prompts:prompts.flatMap(row=>row.document?[{id:row.document.id,label:row.document.label,description:row.document.description}]:[]),
  promptProfiles:promptProfiles.flatMap(row=>row.document?[{id:row.document.id,label:row.document.label,description:row.document.description,prompts:row.document.prompts}]:[]),
  onChange:value=>updateSource(doc.key,value),
  onSave:()=>saveDoc(doc),
  onToggleEnabled:document?()=>updateSource(doc.key,JSON.stringify({...document,enabled:document.enabled===false},null,2)):undefined,
  onCreateSpecialization:document?()=>createSpecialization(doc,document):undefined,
 };
 return <SuperControl key={doc.key} appearance="embedded" control={control} className="operation-document-super"/>};

 if(!snapshot)return <section className="resource-view"><div className="studio-empty">Loading operation library…</div></section>;
 const toggleOperation=(id:string)=>setCollapsedOperations(current=>{const next=new Set(current);if(next.has(id))next.delete(id);else next.add(id);return next});
 const visibleOperations=(snapshot.operations||[]).filter(row=>row.document&&(!sourceLanguage||implementations.some(impl=>relationshipIds(impl.document?.implements).includes(row.document!.id))||row.document.implementation?.startsWith(sourceLanguage)));
 const operationIds=visibleOperations.flatMap(operation=>operation.document?[operation.document.id]:[]);
 const commandCategories=(action:"collapse"|"expand")=>setCategoryCommand(current=>({action,revision:(current?.revision||0)+1}));
 const commandOperations=(action:"collapse"|"expand",ids=operationIds)=>setCollapsedOperations(current=>{const next=new Set(current);for(const id of ids)action==="collapse"?next.add(id):next.delete(id);return next});
 const commandBranches=(action:"collapse"|"expand",target:string)=>{if(target==="all"){commandCategories(action);commandOperations(action);return}if(target==="categories"){commandCategories(action);return}const rows=(snapshot.operations||[]).filter(row=>{const item=row.document;if(!item)return false;const variants=specializations.get(item.id)||[];if(target==="top-operation")return true;if(target==="unspecialized-operation")return variants.length===0;if(target==="enabled")return resolveResourceEnablement(item).enabled;if(target==="disabled")return !resolveResourceEnablement(item).enabled;if(target==="search")return JSON.stringify(item).toLowerCase().includes(treeFilter.trim().toLowerCase());return false});commandOperations(action,rows.flatMap(row=>row.document?[row.document.id]:[]))};
 const categorizedOperations=(snapshot.operations||[]).flatMap(operation=>{const item=operation.document;if(!item)return[];const variants=specializations.get(item.id)||[];const parentEnablement=resolveResourceEnablement(item);const categories=[...new Set([...categoryPaths(item.categories),...variants.flatMap(variant=>categoryPaths(variant.document?.categories))])];return [{id:item.id,categories,searchValue:item,render:(appearanceKey:string)=>{const selectedOperation=active?.record.document?.id===item.id;const branchCollapsed=collapsedOperations.has(item.id);const categoryPath=appearanceCategoryPath(appearanceKey,item.id);const operationBelongsHere=categoryPath!==null&&categoryPaths(item.categories).includes(categoryPath);const visibleVariants=categoryPath&&!operationBelongsHere?variants.filter(variant=>categoryPaths(variant.document?.categories).includes(categoryPath)):variants;return <div className={`operation-tree-group ${branchCollapsed?"branch-collapsed":""}`} key={appearanceKey} data-tree-search={JSON.stringify(item)}>
  <div className="inheritance-row"><button className={`operation-tree-row operation-parent ${enablementClass(parentEnablement)} ${selectedOperation?"selected":""}`} onClick={()=>open(operation as RecordFile<OperationResource>)}><span className="operation-kind-badge">OPERATION</span><span><b>{item.label||item.id}</b><small>{item.description||item.id}</small></span><em>{visibleVariants.length} variants <ResourceEnablementBadge state={parentEnablement}/></em></button>{visibleVariants.length>0&&<button type="button" className="tree-branch-toggle" title={branchCollapsed?"Unhide Variants":"Hide Variants"} aria-label={`${branchCollapsed?"Unhide":"Hide"} Variants for ${item.label||item.id}`} aria-expanded={!branchCollapsed} onClick={()=>toggleOperation(item.id)}><span aria-hidden="true">{branchCollapsed?"›":"⌄"}</span><b>{branchCollapsed?"Unhide Variants":"Hide Variants"}</b></button>}</div>
  <div className="operation-tree-children">{visibleVariants.map(variant=>{const impl=variant.document!;const implEnablement=resolveResourceEnablement(impl,parentEnablement);const selectedImpl=active?.record.document?.id===impl.id;const language=impl.implementation.startsWith("python")?"PYTHON":impl.implementation.startsWith("prolog")?"PROLOG":impl.implementation.startsWith("metta")?"METTA":impl.implementation.startsWith("llm")?"LLM":"IMPL";return <button className={`operation-tree-row operation-child ${enablementClass(implEnablement)} ${selectedImpl?"selected":""}`} key={impl.id} data-tree-search={JSON.stringify(impl)} onClick={()=>open(variant as RecordFile<OperationResource>)}><span className={`operation-kind-badge ${language.toLowerCase()}`}>{language}</span><span><b>{impl.label||impl.id}</b><small>{impl.implementation}</small></span><em>{item.preferredSpecialization===impl.id?"default ":""}<ResourceEnablementBadge state={implEnablement}/></em></button>})}</div>
 </div>}}]});
 return <section className="resource-view operation-hierarchy-page">
  <div className="resource-heading"><div><span>{sourceLanguage?`${sourceLanguage.toUpperCase()} SOURCE LIBRARY`:"OPERATION CONTRACT SYSTEM"}</span><h1>{sourceLanguage?`${sourceLanguage==="metta"?"MeTTa":sourceLanguage[0].toUpperCase()+sourceLanguage.slice(1)} implementation source`:"Operations & implementations"}</h1><p>{sourceLanguage?`Operations implemented through the ${sourceLanguage} backend. Select an implementation to edit its maintained source and execution binding.`:<>Every resource has <code>kind operation</code>. An Operation with a same-kind parent is a concrete implementation alternative; roots are abstract contracts.</>}</p></div></div>
  {error&&<div className="demo-notice"><b>Operation editor error</b><span>{error}</span></div>}
  <div className={`operation-hierarchy-layout operation-hierarchy ${navigatorCollapsed?"navigator-collapsed":"navigator-expanded"}`}>
   <div className="operation-tree-pane artifact-navigator operation-category-enabled">
    <div className="artifact-navigator-content categorized-operation-content" ref={treeRef}><CategorizedArtifactTree items={categorizedOperations} onlyCategories={false} categoryCommand={categoryCommand} workspaceId={workspaceId} categoryTree="operations"/></div>
    <div className="artifact-navigator-toolbar"><span>OPERATIONS</span><div className="artifact-navigator-actions"><label className="artifact-tree-filter"><span>Filter tree</span><input type="search" value={treeFilter} onChange={event=>setTreeFilter(event.target.value)} placeholder="Filter tree…" /></label><div className="tree-repeat-permanent"><RepeatSwitch value={visibilityRules.repeats} onChange={repeats=>setVisibilityRules({...visibilityRules,repeats})}/></div><button type="button" aria-label="Expand All" onClick={()=>commandBranches("expand","all")}><b>Expand All</b></button><button type="button" aria-label="Collapse All" onClick={()=>commandBranches("collapse","all")}><b>Collapse All</b></button><button type="button" aria-label="Tree View Controls" aria-expanded={viewControlsOpen} aria-pressed={viewControlsOpen} onClick={()=>setViewControlsOpen(value=>!value)}><b>{viewControlsOpen?"Hide View":"Show View"}</b></button><button type="button" aria-label={navigatorCollapsed?"Expand operations hierarchy":"Collapse operations hierarchy"} aria-expanded={!navigatorCollapsed} onClick={()=>setNavigatorCollapsed(value=>!value)}>{navigatorCollapsed?"›":"‹"}<b>{navigatorCollapsed?"":"Pane"}</b></button></div></div>
    {viewControlsOpen&&<TreeViewControls kinds={treeKinds} rules={visibilityRules} onChange={setVisibilityRules} showParents={showParents} onShowParentsChange={setShowParents} onBranchAction={commandBranches}/>}
   </div>
   <div className="operation-editor-workspace">
    <TreePaneResizer />
    <div className="operation-document-tabs">{openDocs.map(doc=><div className={`operation-document-tab ${doc.key===activeKey?"active":""}`} key={doc.key}><button onClick={()=>setActiveKey(doc.key)}><span>{relationshipIds(doc.record.document?.implements).length?"IMPL":"OPERATION"}</span><b>{doc.record.document?.label||doc.record.document?.id||doc.record.path}</b>{doc.dirty&&<i>●</i>}</button><button className="close" onClick={()=>close(doc.key)}>×</button></div>)}<button type="button" className="operation-compare-toggle" disabled={openDocs.length<2} onClick={chooseComparison}>{comparison?"Single document":"Compare documents"}</button></div>
    <div className={`operation-editor-panes ${comparison?"split":"single"}`}>
      {active?renderEditor(active):<div className="studio-empty">Select a operation or implementation.</div>}
      {comparison&&renderEditor(comparison,true)}
    </div>
   </div>
  </div>
 </section>;
}
