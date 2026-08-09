import { useEffect, useState } from "react";

type IncludeSpec = { workspaceId: string; includeInherited: boolean };
type Workspace = {
  id: string; label: string; description: string; root: string;
  includes?: IncludeSpec[]; effectiveIncludes?: string[];
  workflowFileCount: number; operationFileCount: number;
  datatypeFileCount?: number; representationFileCount?: number;
  concreteDatatypeFileCount?: number; modelFileCount?: number; promptFileCount?: number;
};
type CredentialStatus = {
  environmentVariable: string;
  backendIds: string[];
  backendLabels: string[];
  configured: boolean;
  source: "workspace" | "shared" | "environment" | "missing";
  bootstrap?: { backendId: string; label: string };
};
type WorkbenchService = {
  id: string; label: string; description: string; port: number; status: string; running: boolean;
  pid?: number | null; processName?: string | null; controllable: boolean; launcher?: string | null;
  stdout: string; stderr: string;
};

export function WorkspaceSettingsPanel({workspace, workspaces, fileCount, implementationCount, onSwitch, onSaved}: {
  workspace: Workspace; workspaces: Workspace[]; fileCount: number; implementationCount: number;
  onSwitch: () => void; onSaved: () => Promise<unknown>;
}) {
  const [includes, setIncludes] = useState<IncludeSpec[]>(workspace.includes || []);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [providerStatus, setProviderStatus] = useState<{provider: string; metrics: Record<string, number>} | null>(null);
  const [credentials, setCredentials] = useState<CredentialStatus[]>([]);
  const [credentialValues, setCredentialValues] = useState<Record<string, string>>({});
  const [credentialBusy, setCredentialBusy] = useState("");
  const [services, setServices] = useState<WorkbenchService[]>([]);
  const [serviceBusy, setServiceBusy] = useState("");

  useEffect(() => setIncludes(workspace.includes || []), [workspace.id, JSON.stringify(workspace.includes || [])]);
  const refreshProviderStatus = () => void fetch("/api/system/resource-provider")
    .then(response => response.json()).then(payload => setProviderStatus(payload)).catch(reason => setMessage(String(reason)));
  const refreshCredentials = () => void fetch(`/api/workspaces/${encodeURIComponent(workspace.id)}/credentials`)
    .then(async response => {
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || response.statusText);
      setCredentials(payload.credentials || []);
    }).catch(reason => setMessage(reason instanceof Error ? reason.message : String(reason)));
  useEffect(refreshProviderStatus, [workspace.id]);
  useEffect(refreshCredentials, [workspace.id]);
  const refreshServices = () => void fetch("/api/system/services")
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
      const response = await fetch(`/api/workspaces/${encodeURIComponent(workspace.id)}/credentials/${encodeURIComponent(name)}`, {
        method, headers: {"Content-Type": "application/json"}, body: body ? JSON.stringify(body) : undefined,
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || response.statusText);
      setCredentials(payload.credentials || []);
      setCredentialValues(current => ({...current, [name]: ""}));
      setMessage(method === "PUT" ? `${name} saved for ${workspace.label}.` : `${name} workspace override removed.`);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally { setCredentialBusy(""); }
  };
  const bootstrapCredential = async (credential: CredentialStatus) => {
    if (!credential.bootstrap) return;
    const name = credential.environmentVariable;
    setCredentialBusy(name); setMessage("");
    try {
      const response = await fetch(`/api/workspaces/${encodeURIComponent(workspace.id)}/credentials/${encodeURIComponent(name)}/bootstrap`, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({backendId: credential.bootstrap.backendId}),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || response.statusText);
      setCredentials(payload.credentials || []);
      setMessage(`${name} was created by ${credential.backendLabels.join(", ")} and saved for ${workspace.label}.`);
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

  const choices = workspaces.filter(item => item.id !== workspace.id);
  const byId = new Map(workspaces.map(item => [item.id, item]));
  return <section className="resource-view workspace-settings-page">
    <div className="resource-heading"><div><span>WORKSPACE SETUP</span><h1>{workspace.label}</h1><p>{workspace.root}</p></div>
      <div className="workspace-settings-actions"><button onClick={onSwitch}>Switch workspace</button><button className="primary" disabled={busy || workspace.id === "shared"} onClick={() => void save()}>{busy ? "Saving..." : "Save inclusions"}</button></div>
    </div>
    <div className="settings-grid"><label><span>WORKSPACE TYPE</span><select value={workspace.id === "shared" ? "shared" : "project"} disabled><option value="shared">Shared library</option><option value="project">Project workspace</option></select><small>{fileCount} editable local text files discovered from disk.</small></label><label><span>ENGINE IMPLEMENTATIONS</span><select value={implementationCount} disabled><option value={implementationCount}>{implementationCount} registered implementations</option></select></label></div>
    <div className="workspace-inclusion-editor"><div className="llm-subhead"><div><span>FILESYSTEM INCLUSIONS</span><b>Low-to-high resource precedence</b><small>Shared is selected by default but can be removed. Included workspaces override earlier layers; {workspace.label} overrides every included layer.</small></div></div>
      <div className="workspace-layer-list">{includes.map((spec, index) => { const item = byId.get(spec.workspaceId); return <div className="workspace-layer" key={spec.workspaceId}><b>{index + 1}</b><span><strong>{item?.label || spec.workspaceId}</strong><small>{item?.root || "Missing workspace"}</small></span><label><input type="checkbox" checked={spec.includeInherited} disabled={spec.workspaceId === "shared"} onChange={event => changeTransitive(spec.workspaceId, event.target.checked)}/> {spec.workspaceId === "shared" ? "No inherited layers" : "Include its inherited workspaces"}</label><button disabled={index === 0} onClick={() => move(index, -1)}>Up</button><button disabled={index === includes.length - 1} onClick={() => move(index, 1)}>Down</button><button onClick={() => toggle(spec.workspaceId)}>Remove</button></div>; })}<div className="workspace-layer current"><b>{includes.length + 1}</b><span><strong>{workspace.label}</strong><small>Current workspace - highest precedence</small></span><em>override layer</em></div></div>
      {workspace.id !== "shared" && <div className="workspace-include-choices"><span>AVAILABLE WORKSPACES</span>{choices.map(item => <label key={item.id}><input type="checkbox" checked={Boolean(selected(item.id))} onChange={() => toggle(item.id)}/><b>{item.label}</b><small>{item.operationFileCount} operations - {(item.datatypeFileCount || 0) + (item.representationFileCount || 0) + (item.modelFileCount || 0) + (item.promptFileCount || 0)} catalog resources</small></label>)}</div>}
    </div>
    <div className="workspace-inclusion-editor workspace-credentials"><div className="llm-subhead"><div><span>BACKEND CREDENTIALS</span><b>Workspace-local API keys</b><small>Keys are written to the ignored runtime/.credentials store, override process environment values, and are never returned by the API.</small></div><button onClick={refreshCredentials}>Refresh status</button></div>
      <div className="workspace-credential-list">{credentials.length === 0 && <p>No visible backend requires a client API key.</p>}{credentials.map(credential => { const name = credential.environmentVariable; const status = credential.source === "workspace" ? "Workspace key configured" : credential.source === "shared" ? "Shared key inherited" : credential.source === "environment" ? "Process environment configured" : "Missing key"; return <div className="workspace-credential" key={name}><span><b>{name}</b><small>{credential.backendLabels.join(", ")}</small></span><em className={credential.source}>{status}</em><input type="password" autoComplete="off" value={credentialValues[name] || ""} placeholder="Paste a workspace override" onChange={event => setCredentialValues(current => ({...current, [name]: event.target.value}))}/><button disabled={credentialBusy === name || !(credentialValues[name] || "").trim()} onClick={() => void mutateCredential(name, "PUT", {value: credentialValues[name]})}>Save key</button>{credential.bootstrap && <button disabled={credentialBusy === name} onClick={() => void bootstrapCredential(credential)}>{credentialBusy === name ? "Connecting..." : credential.bootstrap.label}</button>}{credential.source === "workspace" && <button disabled={credentialBusy === name} onClick={() => void mutateCredential(name, "DELETE")}>Clear workspace key</button>}</div>; })}</div>
    </div>
    <div className="workspace-inclusion-editor workbench-service-monitor"><div className="llm-subhead"><div><span>WORKBENCH SERVICES</span><b>Hidden-process monitor</b><small>Live listener discovery, process identity, launch commands, and recent redacted output. Managed gateway controls are restricted to this computer.</small></div><button onClick={refreshServices}>Refresh now</button></div>
      <div className="workbench-service-summary"><b>{services.filter(service => service.running).length} / {services.length}</b><span>listeners online</span></div>
      <div className="workbench-service-list">{services.map(service => <article className={`workbench-service ${service.running ? "running" : "stopped"}`} key={service.id}>
        <div className="workbench-service-main"><i aria-label={service.status}/><span><b>{service.label}</b><small>{service.description}</small></span><code>127.0.0.1:{service.port}</code><em>{service.status}</em></div>
        <div className="workbench-service-process"><span>PID <b>{service.pid || "—"}</b></span><span>PROCESS <b>{service.processName || "not discovered"}</b></span><span>LAUNCHER <code>{service.launcher || "managed by the development session"}</code></span></div>
        {service.controllable && <div className="workbench-service-actions"><button disabled={Boolean(serviceBusy) || service.running} onClick={() => void controlService(service, "start")}>Start</button><button disabled={Boolean(serviceBusy)} onClick={() => void controlService(service, "restart")}>Restart</button><button disabled={Boolean(serviceBusy) || !service.running} onClick={() => void controlService(service, "stop")}>Stop</button></div>}
        {(service.stdout || service.stderr) && <details><summary>Recent stdout / stderr</summary><div className="workbench-service-logs">{service.stdout && <section><b>STDOUT</b><pre>{service.stdout}</pre></section>}{service.stderr && <section><b>STDERR</b><pre>{service.stderr}</pre></section>}</div></details>}
      </article>)}</div>
    </div>
    {message && <div className={`demo-notice ${message.includes("saved") || message.includes("created") ? "connected" : ""}`}><b>{message.includes("saved") || message.includes("created") ? "SAVED" : "STATUS"}</b><span>{message}</span></div>}
    <div className="workspace-inclusion-editor resource-provider-status"><div className="llm-subhead"><div><span>RESOURCE PROVIDER</span><b>{providerStatus?.provider || "Loading provider status..."}</b><small>All workspace JSON compatibility paths and physical MeTTa resources pass through this singleton boundary.</small></div><button onClick={refreshProviderStatus}>Refresh metrics</button></div>{providerStatus && <div className="provider-metric-grid">{Object.entries(providerStatus.metrics).sort(([left], [right]) => left.localeCompare(right)).map(([name, value]) => <div key={name}><span>{name}</span><b>{value}</b></div>)}</div>}</div>
  </section>;
}
