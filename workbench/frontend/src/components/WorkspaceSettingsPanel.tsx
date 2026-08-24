import { useEffect, useState } from "react";
import { updateUserUiPreferences, useUserUiPreferences } from "../lib/uiPreferences";
import { WORKSPACE_OPENING_PAGE_OPTIONS, setSystemOpeningPage, setWorkspaceOpeningPage, useWorkspacePagePreferences } from "../lib/workspacePagePreferences";
import { ResourceSourceEditor } from "./ResourceSourceEditor";

type IncludeSpec = { workspaceId: string; includeInherited: boolean };
type Workspace = {
  id: string; label: string; description: string; root: string;
  workspaceType?: "project" | "library"; hidden?: boolean;
  includes?: IncludeSpec[]; effectiveIncludes?: string[];
  workflowFileCount: number; operationFileCount: number;
  datatypeFileCount?: number; representationFileCount?: number;
  concreteDatatypeFileCount?: number; modelFileCount?: number; promptFileCount?: number;
  fileCount?: number; diskUsageBytes?: number; resourceCounts?: Record<string, number>;
  usedByProjectCount?: number; usedByProjects?: string[];
  consumedProjectCount?: number; consumedProjects?: string[];
};
type CredentialStatus = {
  environmentVariable: string;
  backendIds: string[];
  backendLabels: string[];
  configured: boolean;
  source: "workspace" | "shared" | "environment" | "missing";
  required?: boolean;
  bootstrap?: { backendId: string; label: string };
};
type WorkbenchService = {
  id: string; label: string; description: string; port: number; status: string; running: boolean;
  listening?: boolean;
  pid?: number | null; processName?: string | null; controllable: boolean; launcher?: string | null;
  stdout: string; stderr: string;
  matchingProcessCount?: number;
  commandPatterns?: string[]; allowKill?: boolean; allowRelaunch?: boolean;
  workingDirectory?: string | null;
  singleton?: boolean;
  processes?: Array<{pid: number; parentPid?: number | null; parentProcessName?: string | null; parentCommandLine?: string | null; parentWorkingDirectory?: string | null; processName?: string | null; commandLine?: string | null; workingDirectory?: string | null; listener: boolean}>;
};
type StartupPolicy = Record<string, {start: boolean; hiddenWindow: boolean; hideFromProcessViewer: boolean}>;
type ModelChoice = {id: string; label: string; backendId?: string; remoteModel?: string};
type SystemModelSelection = {kind?: string; id?: string; label?: string; fallbackModelId: string; pervasive: boolean};
type WorkspaceModelSelection = {kind?: string; id?: string; label?: string; overrideModelId: string};
const formatDiskUsage=(bytes=0)=>bytes>=1024*1024*1024?`${(bytes/(1024*1024*1024)).toFixed(2)} GB`:bytes>=1024*1024?`${(bytes/(1024*1024)).toFixed(1)} MB`:bytes>=1024?`${(bytes/1024).toFixed(1)} KB`:`${bytes} B`;

function RegistryWorkspaceSourceEditor({item, busy, onSaved}: {item: Workspace; busy: boolean; onSaved: (workspace: Workspace) => void}) {
  const [source, setSource] = useState("");
  const [valid, setValid] = useState(true);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const load = async () => {
    if (source || loading) return;
    setLoading(true); setMessage("");
    try {
      const response=await fetch(`/api/workspaces/${encodeURIComponent(item.id)}/settings`); const payload=await response.json();
      if(!response.ok)throw new Error(payload.detail||response.statusText);
      setSource(JSON.stringify(payload.document,null,2));
    } catch(reason){setMessage(reason instanceof Error?reason.message:String(reason));}
    finally{setLoading(false);}
  };
  const save = async () => {
    setSaving(true); setMessage("");
    try {
      const document=JSON.parse(source);
      const response=await fetch(`/api/workspaces/${encodeURIComponent(item.id)}/settings`,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({document})});
      const payload=await response.json(); if(!response.ok)throw new Error(payload.detail||response.statusText);
      setSource(JSON.stringify(payload.document,null,2)); onSaved(payload.workspace); setMessage("Workspace metadata saved.");
    } catch(reason){setMessage(reason instanceof Error?reason.message:String(reason));}
    finally{setSaving(false);}
  };
  return <details className="registry-workspace-source" onToggle={event=>{if(event.currentTarget.open)void load()}}><summary>Edit workspace MeTTa / JSON</summary>{loading&&<p>Loading workspace metadata…</p>}{source&&<><ResourceSourceEditor value={source} onChange={setSource} onValidityChange={setValid} label={`Edit ${item.label} workspace metadata`} showEnablement={false}/><div className="registry-workspace-source-actions"><code>{item.root}\workspace.metta</code><button disabled={busy||saving||!valid} onClick={()=>void save()}>{saving?"Saving…":"Save workspace metadata"}</button></div></>}{message&&<p className={message.includes("saved")?"validation good":"validation bad"}>{message}</p>}</details>;
}

export function WorkspaceSettingsPanel({workspace, workspaces, fileCount, implementationCount, workspaceResourceCountingEnabled=false, onWorkspaceResourceCountingEnabledChange, onSwitch, onSaved, mode="settings"}: {
  workspace: Workspace; workspaces: Workspace[]; fileCount: number; implementationCount: number;
  workspaceResourceCountingEnabled?: boolean;
  onWorkspaceResourceCountingEnabledChange?: (enabled: boolean) => void;
  onSwitch: () => void; onSaved: () => Promise<unknown>; mode?: "settings" | "workspace" | "processes";
}) {
  const userUiPreferences = useUserUiPreferences();
  const workspacePagePreferences = useWorkspacePagePreferences();
  const [includes, setIncludes] = useState<IncludeSpec[]>(workspace.includes || []);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [providerStatus, setProviderStatus] = useState<{provider: string; metrics: Record<string, number>} | null>(null);
  const [credentials, setCredentials] = useState<CredentialStatus[]>([]);
  const [credentialValues, setCredentialValues] = useState<Record<string, string>>({});
  const [credentialBusy, setCredentialBusy] = useState("");
  const [services, setServices] = useState<WorkbenchService[]>([]);
  const [serviceBusy, setServiceBusy] = useState("");
  const [registry, setRegistry] = useState<Workspace[]>(workspaces);
  const [startupPolicy, setStartupPolicy] = useState<StartupPolicy>({});
  const [startupPolicySource, setStartupPolicySource] = useState("");
  const [startupPolicyValid, setStartupPolicyValid] = useState(true);
  const [modelChoices, setModelChoices] = useState<ModelChoice[]>([]);
  const [systemModelSelection, setSystemModelSelection] = useState<SystemModelSelection>({fallbackModelId:"",pervasive:false});
  const [workspaceModelSelection, setWorkspaceModelSelection] = useState<WorkspaceModelSelection>({overrideModelId:""});
  const [effectiveModelId, setEffectiveModelId] = useState("");
  const [effectiveModelSource, setEffectiveModelSource] = useState("");
  const credentialTargetId = mode==="settings" ? "shared_library_system" : workspace.id;
  const credentialTargetLabel = mode==="settings" ? "the workbench system" : workspace.label;

  useEffect(() => setIncludes(workspace.includes || []), [workspace.id, JSON.stringify(workspace.includes || [])]);
  useEffect(() => setRegistry(workspaces), [workspaces]);
  const refreshProviderStatus = () => void fetch("/api/system/resource-provider")
    .then(response => response.json()).then(payload => setProviderStatus(payload)).catch(reason => setMessage(String(reason)));
  const refreshCredentials = () => void fetch(`/api/workspaces/${encodeURIComponent(credentialTargetId)}/credentials`)
    .then(async response => {
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || response.statusText);
      setCredentials(payload.credentials || []);
    }).catch(reason => setMessage(reason instanceof Error ? reason.message : String(reason)));
  useEffect(refreshProviderStatus, [workspace.id]);
  useEffect(refreshCredentials, [credentialTargetId]);
  const refreshServices = () => void fetch(mode==="settings"?"/api/system/services?include_hidden=true":"/api/system/services")
    .then(async response => {
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || payload.error || response.statusText);
      setServices(payload.services || []);
    }).catch(reason => setMessage(reason instanceof Error ? reason.message : String(reason)));
  useEffect(() => {
    refreshServices();
    const timer = window.setInterval(refreshServices, 5000);
    return () => window.clearInterval(timer);
  }, []);
  const refreshStartupPolicy = () => void fetch("/api/system/startup").then(response => response.json()).then(payload => {
    setStartupPolicy(payload.services || {});
    setStartupPolicySource(JSON.stringify(payload.document || {kind:"workbench_startup_policy",id:"workbench_startup",services:payload.services||{}}, null, 2));
  }).catch(reason => setMessage(String(reason)));
  useEffect(refreshStartupPolicy, []);
  const modelSelectionEndpoint = mode==="settings"?"/api/system/model-selection":`/api/workspaces/${encodeURIComponent(workspace.id)}/model-selection`;
  const refreshModelSelection = () => {
    if(mode==="processes")return;
    void fetch(modelSelectionEndpoint).then(async response=>{
      const payload=await response.json();
      if(!response.ok)throw new Error(payload.detail||response.statusText);
      setModelChoices(payload.models||[]);
      if(mode==="settings")setSystemModelSelection(payload.document||{fallbackModelId:"",pervasive:false});
      else {
        setWorkspaceModelSelection(payload.document||{overrideModelId:""});
        setSystemModelSelection(payload.system||{fallbackModelId:"",pervasive:false});
        setEffectiveModelId(String(payload.effective?.models?.[0]||""));
        setEffectiveModelSource(String(payload.source||""));
      }
    }).catch(reason=>setMessage(reason instanceof Error?reason.message:String(reason)));
  };
  useEffect(refreshModelSelection,[mode,workspace.id]);

  const selected = (id: string) => includes.find(item => item.workspaceId === id);
  const toggle = (id: string) => setIncludes(current => selected(id)
    ? current.filter(item => item.workspaceId !== id)
    : [...current, {workspaceId: id, includeInherited: true}]);
  const changeTransitive = (id: string, value: boolean) => setIncludes(current => current.map(item =>
    item.workspaceId === id ? {...item, includeInherited: value} : item));
  const move = (index: number, delta: number) => setIncludes(current => {
    const target = index + delta;
    if (target < 0 || target >= current.length) return current;
    const next = [...current];
    [next[index], next[target]] = [next[target], next[index]];
    return next;
  });
  const save = async () => {
    setBusy(true); setMessage("");
    try {
      const response = await fetch(`/api/workspaces/${encodeURIComponent(workspace.id)}/settings`, {
        method: "PUT", headers: {"Content-Type": "application/json"}, body: JSON.stringify({includes}),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || payload.detail || response.statusText);
      await onSaved(); setMessage("Workspace inclusion order saved to disk.");
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally { setBusy(false); }
  };
  const mutateCredential = async (name: string, method: "PUT" | "DELETE", body?: object) => {
    setCredentialBusy(name); setMessage("");
    try {
      const response = await fetch(`/api/workspaces/${encodeURIComponent(credentialTargetId)}/credentials/${encodeURIComponent(name)}`, {
        method, headers: {"Content-Type": "application/json"}, body: body ? JSON.stringify(body) : undefined,
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || response.statusText);
      setCredentials(payload.credentials || []);
      setCredentialValues(current => ({...current, [name]: ""}));
      setMessage(method === "PUT" ? `${name} saved for ${credentialTargetLabel}.` : `${name} override removed from ${credentialTargetLabel}.`);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally { setCredentialBusy(""); }
  };
  const bootstrapCredential = async (credential: CredentialStatus) => {
    if (!credential.bootstrap) return;
    const name = credential.environmentVariable;
    setCredentialBusy(name); setMessage("");
    try {
      const response = await fetch(`/api/workspaces/${encodeURIComponent(credentialTargetId)}/credentials/${encodeURIComponent(name)}/bootstrap`, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({backendId: credential.bootstrap.backendId}),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || response.statusText);
      setCredentials(payload.credentials || []);
      setMessage(`${name} was created by ${credential.backendLabels.join(", ")} and saved for ${credentialTargetLabel}.`);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally { setCredentialBusy(""); }
  };
  const controlService = async (service: WorkbenchService, action: "start" | "restart" | "stop") => {
    setServiceBusy(`${service.id}:${action}`); setMessage("");
    try {
      const response = await fetch(`/api/system/services/${encodeURIComponent(service.id)}/${action}`, {method: "POST"});
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || payload.error || response.statusText);
      setMessage(`${service.label} ${action} requested.`);
      window.setTimeout(refreshServices, action === "stop" ? 500 : 1500);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally { setServiceBusy(""); }
  };
  const controlMatchingProcess = async (service: WorkbenchService, pid: number, action: "kill" | "relaunch") => {
    if (!window.confirm(`${action === "kill" ? "Stop only" : "Stop only and relaunch"} PID ${pid} for ${service.label}? Its parent and child processes will not be terminated. Use the service-level Stop or Restart only when you intend to terminate the complete listener tree.`)) return;
    setServiceBusy(`${service.id}:${pid}:${action}`); setMessage("");
    try {
      const response = await fetch(`/api/system/services/${encodeURIComponent(service.id)}/processes/${pid}/${action}`, {method:"POST"});
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || payload.error || response.statusText);
      setMessage(`${service.label} PID ${pid} ${action} requested.`);
      window.setTimeout(refreshServices, action === "kill" ? 500 : 1500);
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : String(reason)); }
    finally { setServiceBusy(""); }
  };
  const updateRegistryWorkspace = async (item: Workspace, patch: {workspaceType?: "project" | "library"; hidden?: boolean}) => {
    setBusy(true); setMessage("");
    try {
      const response = await fetch(`/api/workspaces/${encodeURIComponent(item.id)}/settings`, {method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(patch)});
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || payload.error || response.statusText);
      setRegistry(current => current.map(candidate => candidate.id === item.id ? {...candidate, ...payload.workspace} : candidate));
      setMessage(`${item.label} registry settings saved.`);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally { setBusy(false); }
  };
  const acceptRegistryWorkspace = (saved: Workspace) => setRegistry(current => current.map(candidate => candidate.id===saved.id?{...candidate,...saved}:candidate));
  const saveStartupPolicy = async () => {
    setBusy(true); setMessage("");
    try {
      const document = JSON.parse(startupPolicySource);
      const response = await fetch("/api/system/startup", {method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({document})});
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || payload.error || response.statusText);
      setStartupPolicy(payload.document?.services || {}); setStartupPolicySource(JSON.stringify(payload.document, null, 2)); setMessage("Workbench startup policy saved.");
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : String(reason)); }
    finally { setBusy(false); }
  };
  const changeStartupPolicy = (serviceId: string, patch: Partial<{start:boolean;hiddenWindow:boolean;hideFromProcessViewer:boolean}>) => {
    const current = startupPolicy[serviceId] || {start:false,hiddenWindow:false,hideFromProcessViewer:false};
    const services = {...startupPolicy,[serviceId]:{...current,...patch}};
    setStartupPolicy(services);
    try { const document=JSON.parse(startupPolicySource); const sourceServices=document.services||{}; setStartupPolicySource(JSON.stringify({...document,services:{...sourceServices,[serviceId]:{...(sourceServices[serviceId]||{}),...patch}}},null,2)); }
    catch { /* A source syntax error remains preserved until the user fixes it. */ }
  };
  const editStartupPolicySource = (source: string) => {
    setStartupPolicySource(source);
    try { const document=JSON.parse(source); if(document.services&&typeof document.services==="object")setStartupPolicy(document.services); }
    catch { /* ResourceSourceEditor reports and preserves invalid drafts. */ }
  };
  const saveModelSelection = async () => {
    setBusy(true); setMessage("");
    try {
      const document=mode==="settings"?systemModelSelection:workspaceModelSelection;
      const response=await fetch(modelSelectionEndpoint,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({document})});
      const payload=await response.json();
      if(!response.ok)throw new Error(payload.detail||response.statusText);
      setModelChoices(payload.models||[]);
      if(mode==="settings")setSystemModelSelection(payload.document);
      else {
        setWorkspaceModelSelection(payload.document);
        setSystemModelSelection(payload.system);
        setEffectiveModelId(String(payload.effective?.models?.[0]||""));
        setEffectiveModelSource(String(payload.source||""));
      }
      setMessage(mode==="settings"?"System model selection saved.":"Workspace model override saved.");
    } catch(reason){setMessage(reason instanceof Error?reason.message:String(reason));}
    finally{setBusy(false);}
  };
  const deleteRegistryWorkspace = async (item: Workspace) => {
    if (!window.confirm(`Delete ${item.label}? The workspace will be moved to the recoverable workspace trash.`)) return;
    setBusy(true); setMessage("");
    try {
      const response = await fetch(`/api/workspaces/${encodeURIComponent(item.id)}`, {method:"DELETE"});
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || payload.error || response.statusText);
      setRegistry(current => current.filter(candidate => candidate.id !== item.id));
      setMessage(`${item.label} deleted. Recovery path: ${payload.recoveryPath}`);
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : String(reason)); }
    finally { setBusy(false); }
  };

  const choices = workspaces.filter(item => item.id !== workspace.id);
  const byId = new Map(workspaces.map(item => [item.id, item]));
  return <section id={mode==="workspace"?"overview-workspace-configuration":undefined} className={`resource-view workspace-settings-page ${mode}-settings`}>
    {mode==="settings"&&<nav className="context-jump-tabs settings-jump-tabs"><button onClick={()=>document.querySelector(".user-ui-preferences")?.scrollIntoView({behavior:"smooth"})}>User / UI</button><button onClick={()=>document.querySelector(".system-model-selection")?.scrollIntoView({behavior:"smooth"})}>Model Selection</button><button onClick={()=>document.querySelector(".system-workspace-registry")?.scrollIntoView({behavior:"smooth"})}>Workspace Registry</button><button onClick={()=>document.querySelector(".system-startup-policy")?.scrollIntoView({behavior:"smooth"})}>Startup Processes</button><button onClick={()=>document.querySelector(".resource-provider-status")?.scrollIntoView({behavior:"smooth"})}>Resource Provider</button></nav>}
    <div className="resource-heading"><div><span>{mode==="processes"?"SYSTEM PROCESS MONITOR":mode==="workspace"?"WORKSPACE CONFIGURATION":"SYSTEM-WIDE SETTINGS"}</span><h1>{mode==="processes"?"Processes":mode==="workspace"?`${workspace.label} configuration`:"Settings"}</h1><p>{mode==="processes"?"Monitor and control the UI, API, model routers, and other managed workbench listeners.":mode==="workspace"?workspace.root:"Configuration and status shared by every filesystem workspace."}</p></div>
      {mode==="workspace"&&<div className="workspace-settings-actions"><button onClick={onSwitch}>Switch workspace</button><button className="primary" disabled={busy || workspace.id === "shared"} onClick={() => void save()}>{busy ? "Saving..." : "Save inclusions"}</button></div>}
    </div>
    {mode==="settings"&&<div className="workspace-inclusion-editor user-ui-preferences"><div className="llm-subhead"><div><span>USER / UI SETTINGS</span><b>Personal workbench presentation preferences</b><small>These choices belong to the user interface, with workspace opening choices resolving through the workspace inheritance chain before the system default.</small></div></div><div className="settings-grid user-ui-preferences-grid"><label><span>RESOURCE SOURCE · SAVE / LOAD CONTROLS</span><select aria-label="Resource Source save and load controls placement" value={userUiPreferences.resourceSourceFileControlsPlacement} onChange={event=>updateUserUiPreferences({resourceSourceFileControlsPlacement:event.target.value as "above"|"below"})}><option value="above">Above the editor text area</option><option value="below">Below the editor text area</option></select><small>Applies immediately to Resource Source and other generic editors using the shared workspace, disk, and client-transfer controls.</small></label><label><span>THIS WORKSPACE · OPENING PAGE</span><select aria-label={`${workspace.label} opening page when view is missing`} value={workspacePagePreferences.openingPageByWorkspace[workspace.id]||"inherit"} onChange={event=>setWorkspaceOpeningPage(workspace.id,event.target.value)}>{WORKSPACE_OPENING_PAGE_OPTIONS.map(option=><option key={option.value} value={option.value}>{option.label}</option>)}</select><small>Used only when the URL has no view=. An explicit view always wins. With no local history or preference, inherited workspace preferences are consulted.</small></label><label><span>SYSTEM · OPENING PAGE FALLBACK</span><select aria-label="System opening page fallback" value={workspacePagePreferences.systemOpeningPage} onChange={event=>setSystemOpeningPage(event.target.value)}>{WORKSPACE_OPENING_PAGE_OPTIONS.filter(option=>option.value!=="inherit"&&option.value!=="last").map(option=><option key={option.value} value={option.value}>{option.label}</option>)}</select><small>Defaults to Overview. It is used when neither this workspace nor its inherited workspaces resolve an opening page. A missing page opens Settings for repair.</small></label></div></div>}
    {mode!=="processes"&&<div className="settings-grid">{mode==="workspace"&&<label><span>WORKSPACE TYPE</span><select value={workspace.id === "shared" ? "shared" : "project"} disabled><option value="shared">Shared library</option><option value="project">Project workspace</option></select><small>{fileCount} editable local text files discovered from disk.</small></label>}<label><span>ENGINE IMPLEMENTATIONS</span><select value={implementationCount} disabled><option value={implementationCount}>{implementationCount} registered implementations</option></select></label>{mode==="settings"&&<label><span>WORKSPACE RESOURCE COUNTING</span><div className="workspace-setting-inline"><input type="checkbox" checked={workspaceResourceCountingEnabled} onChange={event=>onWorkspaceResourceCountingEnabledChange?.(event.target.checked)}/><b>Enable local/inherited/overridden resource counts in the workspace chooser</b></div><small>When enabled, detailed totals are hydrated by the worker pool. Disable this to use lightweight chooser metadata only.</small></label>}</div>}
    {mode!=="processes"&&<div className="workspace-inclusion-editor system-model-selection"><div className="llm-subhead"><div><span>{mode==="settings"?"SYSTEM MODEL SELECTION":"WORKSPACE MODEL OVERRIDE"}</span><b>{mode==="settings"?"Global fallback and pervasive model":"Override the system model for this workspace"}</b><small>{mode==="settings"?"The selected model is fallback-only by default. Enable Pervasive to override Operation and policy choices unless a workspace explicitly overrides it.":"A workspace override has the highest priority. Leave it empty to use the pervasive system model, the Operation or policy choice, and finally the global fallback."}</small></div><button disabled={busy} onClick={()=>void saveModelSelection()}>Save model selection</button></div><div className="system-startup-list"><article><span><b>{mode==="settings"?"Workbench default model":"Workspace execution model"}</b><small>{mode==="settings"?systemModelSelection.fallbackModelId||"No fallback selected":workspaceModelSelection.overrideModelId||`Inherited effective model: ${effectiveModelId||"none"}`}</small>{mode==="workspace"&&<small>RESOLUTION {effectiveModelSource||"unresolved"} · SYSTEM {systemModelSelection.fallbackModelId||"none"}{systemModelSelection.pervasive?" · pervasive":" · fallback only"}</small>}</span><label>{mode==="settings"?"FALLBACK MODEL":"WORKSPACE OVERRIDE"}<select aria-label={mode==="settings"?"Global fallback model":"Workspace model override"} value={mode==="settings"?systemModelSelection.fallbackModelId:workspaceModelSelection.overrideModelId} onChange={event=>mode==="settings"?setSystemModelSelection(current=>({...current,fallbackModelId:event.target.value})):setWorkspaceModelSelection(current=>({...current,overrideModelId:event.target.value}))}><option value="">{mode==="settings"?"No global fallback":"Use system and Operation resolution"}</option>{modelChoices.map(model=><option key={model.id} value={model.id}>{model.label} · {model.backendId||model.id}</option>)}</select></label>{mode==="settings"&&<label><input aria-label="Pervasive model selection" type="checkbox" checked={systemModelSelection.pervasive} disabled={!systemModelSelection.fallbackModelId} onChange={event=>setSystemModelSelection(current=>({...current,pervasive:event.target.checked}))}/> Pervasive — always use this model</label>}</article></div></div>}
    {mode==="settings"&&<div className="workspace-inclusion-editor system-workspace-registry"><div className="llm-subhead"><div><span>WORKSPACE REGISTRY</span><b>Workspace types and chooser visibility</b><small>Hidden workspaces remain available for inheritance and administration but do not appear in the workspace chooser. Expand any row to edit its complete filesystem metadata as synchronized MeTTa or JSON.</small></div></div><div className="system-workspace-list">{registry.map(item=>{const protectedWorkspace=item.id==="default"||item.id==="shared"||item.id==="shared_library_system"||item.id===workspace.id;const resourceCounts=Object.entries(item.resourceCounts||{}).filter(([,count])=>count>0);return <article key={item.id}><span><b>{item.label}</b><small>{item.id} · {item.root}</small><small className="workspace-disk-summary">{item.fileCount||0} files · {formatDiskUsage(item.diskUsageBytes)} on disk · used by {item.usedByProjectCount||0} project{item.usedByProjectCount===1?"":"s"} · consumes {item.consumedProjectCount||0} project{item.consumedProjectCount===1?"":"s"}</small><small className="workspace-project-usage">USED BY {item.usedByProjects?.length?item.usedByProjects.join(" · "):"none"} · CONSUMES {item.consumedProjects?.length?item.consumedProjects.join(" · "):"none"}</small><small className="workspace-resource-counts">{resourceCounts.length?resourceCounts.map(([kind,count])=>`${kind} ${count}`).join(" · "):"No typed resources"}</small></span><label>TYPE<select aria-label={`${item.label} workspace type`} value={item.workspaceType||"project"} disabled={busy} onChange={event=>void updateRegistryWorkspace(item,{workspaceType:event.target.value as "project"|"library"})}><option value="project">Project</option><option value="library">Library</option></select></label><label className="workspace-hidden-toggle"><input type="checkbox" checked={Boolean(item.hidden)} disabled={busy||item.id===workspace.id} onChange={event=>void updateRegistryWorkspace(item,{hidden:event.target.checked})}/> Hide from chooser</label><button className="workspace-delete-button" disabled={busy||protectedWorkspace} title={protectedWorkspace?"Active and system workspaces cannot be deleted":"Move workspace to recoverable trash"} onClick={()=>void deleteRegistryWorkspace(item)}>Delete</button><RegistryWorkspaceSourceEditor item={item} busy={busy} onSaved={acceptRegistryWorkspace}/></article>})}</div></div>}
    {mode==="settings"&&<div className="workspace-inclusion-editor system-startup-policy"><div className="llm-subhead"><div><span>RUN_WORKBENCH STARTUP · METTA/JSON</span><b>Managed process startup policy</b><small>Window visibility and Process Viewer visibility are separate. Process identity, launch metadata, control permissions, and fallback defaults live in independent managed_service resources.</small></div><button disabled={busy||!startupPolicyValid} onClick={()=>void saveStartupPolicy()}>Save startup policy</button></div><div className="system-startup-list">{services.map(service=>{const policy=startupPolicy[service.id]||{start:false,hiddenWindow:false,hideFromProcessViewer:false};return <article key={service.id}><span><b>{service.label}</b><small>{service.id} · 127.0.0.1:{service.port}</small><small>LAUNCH {service.launcher||"observation only"}</small><small>CWD {service.workingDirectory||"repository root"}</small><small>MATCH {service.commandPatterns?.join(" · ")||"listener port"}</small><small>CONTROL kill {service.allowKill===false?"disabled":"enabled"} · relaunch {service.allowRelaunch===false?"disabled":"enabled"}</small></span><label><input type="checkbox" checked={policy.start} onChange={event=>changeStartupPolicy(service.id,{start:event.target.checked})}/> Start with run_workbench</label><label><input type="checkbox" checked={policy.hiddenWindow} disabled={!policy.start} onChange={event=>changeStartupPolicy(service.id,{hiddenWindow:event.target.checked})}/> Hidden launch window</label><label><input type="checkbox" checked={policy.hideFromProcessViewer} onChange={event=>changeStartupPolicy(service.id,{hideFromProcessViewer:event.target.checked})}/> Hide from Process Viewer</label></article>})}</div><ResourceSourceEditor value={startupPolicySource} onChange={editStartupPolicySource} onValidityChange={setStartupPolicyValid} label="Edit start, window visibility, and Process Viewer overrides" showEnablement={false}/></div>}
    {mode==="workspace"&&<div className="workspace-inclusion-editor"><div className="llm-subhead"><div><span>FILESYSTEM INCLUSIONS</span><b>Low-to-high resource precedence</b><small>Shared is selected by default but can be removed. Included workspaces override earlier layers; {workspace.label} overrides every included layer.</small></div></div>
      <div className="workspace-layer-list">{includes.map((spec, index) => { const item = byId.get(spec.workspaceId); return <div className="workspace-layer" key={spec.workspaceId}><b>{index + 1}</b><span><strong>{item?.label || spec.workspaceId}</strong><small>{item?.root || "Missing workspace"}</small></span><label><input type="checkbox" checked={spec.includeInherited} disabled={spec.workspaceId === "shared"} onChange={event => changeTransitive(spec.workspaceId, event.target.checked)}/> {spec.workspaceId === "shared" ? "No inherited layers" : "Include its inherited workspaces"}</label><button disabled={index === 0} onClick={() => move(index, -1)}>Up</button><button disabled={index === includes.length - 1} onClick={() => move(index, 1)}>Down</button><button onClick={() => toggle(spec.workspaceId)}>Remove</button></div>; })}<div className="workspace-layer current"><b>{includes.length + 1}</b><span><strong>{workspace.label}</strong><small>Current workspace - highest precedence</small></span><em>override layer</em></div></div>
      {workspace.id !== "shared" && <div className="workspace-include-choices"><span>AVAILABLE WORKSPACES</span>{choices.map(item => <label key={item.id}><input type="checkbox" checked={Boolean(selected(item.id))} onChange={() => toggle(item.id)}/><b>{item.label}</b><small>{item.operationFileCount} operations - {(item.datatypeFileCount || 0) + (item.representationFileCount || 0) + (item.modelFileCount || 0) + (item.promptFileCount || 0)} catalog resources</small></label>)}</div>}
    </div>}
    {(mode==="workspace"||mode==="settings")&&<div className="workspace-inclusion-editor workspace-credentials"><div className="llm-subhead"><div><span>{mode==="settings"?"SYSTEM CREDENTIALS":"BACKEND CREDENTIALS"}</span><b>{mode==="settings"?"Workbench-wide API keys":"Workspace-local API keys"}</b><small>{mode==="settings"?"System credentials are stored in the protected shared system credential store and supplied to every workspace. Secret values are never returned by the API.":"A workspace override is optional when the workbench already supplies the credential from System Credentials or the process environment. Local overrides stay in this workspace's ignored runtime/.credentials store."}</small></div><button onClick={refreshCredentials}>Refresh status</button></div>
      <div className="workspace-credential-list">{credentials.length === 0 && <p>No visible backend declares a client API key.</p>}{credentials.map(credential => { const name = credential.environmentVariable;const optional=credential.required===false; const supplied=mode==="workspace"&&(credential.source==="shared"||credential.source==="environment");const status = mode==="settings"&&credential.source==="workspace" ? `System credential configured${optional?" · optional":""}` : credential.source === "workspace" ? `Workspace override configured${optional?" · optional":""}` : credential.source === "shared" ? "System credential supplied — no workspace key required" : credential.source === "environment" ? "Process environment supplied — no workspace key required" : optional ? "Optional credential not configured — backend may run without it" : "Required credential missing"; return <div className={`workspace-credential ${supplied?"supplied":""} ${optional?"optional":"required"}`} key={name}><span><b>{name}</b><small>{credential.backendLabels.join(", ")} · {optional?"OPTIONAL":"REQUIRED"}</small></span><em className={credential.source}>{status}</em><input type="password" autoComplete="off" value={credentialValues[name] || ""} placeholder={supplied||optional?"Optional override":"Paste required credential"} onChange={event => setCredentialValues(current => ({...current, [name]: event.target.value}))}/><button disabled={credentialBusy === name || !(credentialValues[name] || "").trim()} onClick={() => void mutateCredential(name, "PUT", {value: credentialValues[name]})}>{mode==="settings"?"Save system key":"Save workspace override"}</button>{credential.bootstrap && <button disabled={credentialBusy === name} onClick={() => void bootstrapCredential(credential)}>{credentialBusy === name ? "Connecting..." : credential.bootstrap.label}</button>}{credential.source === "workspace" && <button disabled={credentialBusy === name} onClick={() => void mutateCredential(name, "DELETE")}>{mode==="settings"?"Clear system key":"Clear workspace override"}</button>}</div>; })}</div>
    </div>}
    {mode==="processes"&&<div className="workspace-inclusion-editor workbench-service-monitor"><div className="llm-subhead"><div><span>WORKBENCH SERVICES</span><b>Hidden-process monitor</b><small>Live listener discovery, process identity, launch commands, and recent redacted output. Managed gateway controls are restricted to this computer.</small></div><button onClick={refreshServices}>Refresh now</button></div>
      <div className="workbench-service-summary"><b>{services.filter(service => service.running).length} / {services.length}</b><span>services with matching processes</span></div>
      <div className="workbench-service-list">{services.map(service => <article className={`workbench-service ${service.running ? "running" : "stopped"}`} key={service.id}>
        <div className="workbench-service-main"><i aria-label={service.status}/><span><b>{service.label}</b><small>{service.description}</small></span><code>127.0.0.1:{service.port}</code><em>{service.status}</em></div>
        <div className="workbench-service-process"><span>PID <b>{service.pid || "—"}</b></span><span>PROCESS <b>{service.processName || "not discovered"}</b></span><span>LAUNCHER <code>{service.launcher || "managed by the development session"}</code></span></div>
        {Boolean(service.processes?.length) && (()=>{
          const processes=service.processes||[],byPid=new Map(processes.map(process=>[process.pid,process])),children=new Map<number,typeof processes>();
          for(const process of processes){if(process.parentPid&&byPid.has(process.parentPid)){const siblings=children.get(process.parentPid)||[];siblings.push(process);children.set(process.parentPid,siblings)}}
          const roots=processes.filter(process=>!process.parentPid||!byPid.has(process.parentPid));
          const parentEvidence=(process:(typeof processes)[number])=>{const missing=[!process.parentCommandLine&&"command line",!process.parentWorkingDirectory&&"working directory"].filter(Boolean);return <span className={`process-tree-parent-evidence ${missing.length?"incomplete":"ready"}`}><small>PARENT</small><b>{process.parentProcessName||"unknown"}</b><code>PID {process.parentPid||"—"}</code><small>WORKING DIRECTORY</small><code>{process.parentWorkingDirectory||"Unavailable"}</code><small>REDACTED COMMAND</small><code>{process.parentCommandLine||"Unavailable"}</code><em>{missing.length?`MISSING ${missing.join(" + ").toUpperCase()}`:"ENOUGH INFORMATION TO RESTART"}</em></span>};
          const renderProcess=(process:(typeof processes)[number],depth:number):React.ReactNode=><div className="workbench-process-branch" key={process.pid} style={{"--process-depth":depth} as React.CSSProperties}><div className="workbench-process-node-row"><span className="process-tree-joint" aria-hidden="true">{depth?"└─":"●"}</span><span className="process-tree-identity"><b>{process.processName||"unknown process"}</b><code>PID {process.pid}</code>{process.listener&&<em>port listener</em>}</span>{parentEvidence(process)}<span className="process-tree-details"><small>CWD</small><code>{process.workingDirectory||"Unavailable"}</code><small>COMMAND</small><code>{process.commandLine||"Unavailable"}</code></span><span className="workbench-process-actions"><button disabled={Boolean(serviceBusy)||service.allowRelaunch===false} title={service.allowRelaunch===false?"Disabled by startup policy":"Stop only this PID, preserve relatives, then launch the service"} onClick={()=>void controlMatchingProcess(service,process.pid,"relaunch")}>Relaunch PID</button><button className="danger" disabled={Boolean(serviceBusy)||service.allowKill===false} title={service.allowKill===false?"Disabled by startup policy":"Stop only this PID; preserve its parent and children"} onClick={()=>void controlMatchingProcess(service,process.pid,"kill")}>Stop PID only</button></span></div>{(children.get(process.pid)||[]).map(child=>renderProcess(child,depth+1))}</div>;
          return <div className="workbench-matching-processes process-relation-tree"><strong>{service.matchingProcessCount} MATCHING OS PROCESS{service.matchingProcessCount===1?"":"ES"} · ALWAYS-EXPANDED PARENT/CHILD TREE</strong><div>{roots.map(root=><div className="process-root-group" key={root.pid}>{root.parentPid&&!byPid.has(root.parentPid)&&<div className="process-external-parent"><span aria-hidden="true">◆</span>{parentEvidence(root)}</div>}{renderProcess(root,root.parentPid?1:0)}</div>)}</div></div>;
        })()}
        {service.controllable && <div className="workbench-service-actions"><button disabled={Boolean(serviceBusy) || service.running} onClick={() => void controlService(service, "start")}>Start</button><button disabled={Boolean(serviceBusy)} onClick={() => void controlService(service, "restart")}>Restart</button><button disabled={Boolean(serviceBusy) || !service.running} onClick={() => void controlService(service, "stop")}>Stop</button></div>}
        {(service.stdout || service.stderr) && <details><summary>Recent stdout / stderr</summary><div className="workbench-service-logs">{service.stdout && <section><b>STDOUT</b><pre>{service.stdout}</pre></section>}{service.stderr && <section><b>STDERR</b><pre>{service.stderr}</pre></section>}</div></details>}
      </article>)}</div>
    </div>}
    {message && <div className={`demo-notice ${message.includes("saved") || message.includes("created") ? "connected" : ""}`}><b>{message.includes("saved") || message.includes("created") ? "SAVED" : "STATUS"}</b><span>{message}</span></div>}
    {mode==="settings"&&<div className="workspace-inclusion-editor resource-provider-status"><div className="llm-subhead"><div><span>RESOURCE PROVIDER</span><b>{providerStatus?.provider || "Loading provider status..."}</b><small>All workspace JSON compatibility paths and physical MeTTa resources pass through this singleton boundary.</small></div><button onClick={refreshProviderStatus}>Refresh metrics</button></div>{providerStatus && <div className="provider-metric-grid">{Object.entries(providerStatus.metrics).sort(([left], [right]) => left.localeCompare(right)).map(([name, value]) => <div key={name}><span>{name}</span><b>{value}</b></div>)}</div>}</div>}
  </section>;
}
