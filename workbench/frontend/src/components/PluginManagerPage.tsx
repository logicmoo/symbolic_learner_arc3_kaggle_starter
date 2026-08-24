import { useCallback, useEffect, useState } from "react";

type Plugin = { id:string; label?:string; description?:string; version?:string; routePrefix?:string; allowedTargets?:string[]; scan:"startup"|"disabled"; loaded:boolean; path:string; error?:string };
type PluginResponse = { plugins:Plugin[]; policyPath:string };

export function PluginManagerPage(){
  const [catalog,setCatalog]=useState<PluginResponse|null>(null);const [busy,setBusy]=useState(false);const [error,setError]=useState<string|null>(null);
  const load=useCallback(async(refresh=false)=>{setBusy(true);setError(null);try{const response=await fetch(`/api/plugins${refresh?"/refresh":""}`,{method:refresh?"POST":"GET"});if(!response.ok)throw new Error(await response.text());setCatalog(await response.json() as PluginResponse)}catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setBusy(false)}},[]);
  useEffect(()=>void load(),[load]);
  const setScan=async(plugin:Plugin,scan:Plugin["scan"])=>{setBusy(true);setError(null);try{const response=await fetch(`/api/plugins/${encodeURIComponent(plugin.id)}`,{method:"PUT",headers:{"content-type":"application/json"},body:JSON.stringify({scan})});if(!response.ok)throw new Error(await response.text());setCatalog(await response.json() as PluginResponse)}catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setBusy(false)}};
  return <section className="resource-view plugin-manager-page"><div className="resource-heading"><div><span>SYSTEM EXTENSIONS</span><h1>Plugins</h1><p>Filesystem plugins discovered beneath <code>workbench/plugins</code>.</p></div><button disabled={busy} onClick={()=>void load(true)}>{busy?"Scanning…":"Refresh plugins"}</button></div>
    {error&&<div className="backend-error"><b>Plugin error</b><span>{error}</span></div>}
    <div className="plugin-catalog">{(catalog?.plugins||[]).map(plugin=><article className="plugin-card" key={plugin.id}><header><div><span>{plugin.loaded?"LOADED":plugin.scan.toUpperCase()}</span><h2>{plugin.label||plugin.id}</h2></div><select aria-label={`${plugin.label||plugin.id} scan policy`} value={plugin.scan} disabled={busy} onChange={event=>void setScan(plugin,event.target.value as Plugin["scan"])}><option value="startup">Scan at startup</option><option value="disabled">Disabled</option></select></header><p>{plugin.description||"No description supplied."}</p>{plugin.routePrefix&&<dl><dt>Route</dt><dd><code>{plugin.routePrefix}</code></dd></dl>}{(plugin.allowedTargets||[]).map(target=><dl key={target}><dt>Allowed target</dt><dd><code>{target}</code></dd></dl>)}<small>{plugin.path}</small>{plugin.error&&<div className="plugin-error">{plugin.error}</div>}</article>)}{!busy&&catalog?.plugins.length===0&&<div className="studio-empty">No plugin manifests found.</div>}</div>
    {catalog&&<small className="plugin-policy-path">Policy: {catalog.policyPath}</small>}
  </section>;
}
