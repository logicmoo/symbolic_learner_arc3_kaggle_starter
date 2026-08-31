import { useEffect, useMemo, useState } from "react";
import "./WorkflowEnginePage.css";

type Workspace = {
  id:string; label:string; description:string; root:string; manifest:string;
  workflowDirectory:string; workflowDirectoryRelative:string;
  promptDirectory:string; promptDirectoryRelative:string;
  configDirectory:string; configDirectoryRelative:string;
  workflowFileCount:number; metadata:Record<string,unknown>;
};
type WorkspaceFile = { path:string; name:string; suffix:string; size:number; modified:number; kind:string; content?:string };
type WorkflowFile = { path:string; document?:any; error?:string };
type Snapshot = { workspace:Workspace; workflows:WorkflowFile[]; files:WorkspaceFile[] };
type Capability = { status:"implemented"|"partial"|"unavailable"|"failed"; detail:string };
type EngineRun = { id:string; workflowId:string; workflowVersion:number; status:string; inputs:any; outputs:any; error?:string; steps:any[]; artifacts:any[]; events:any[]; logs:any[]; children:any[] };

async function request(path:string, init?:RequestInit) {
  const response = await fetch(path, { headers:{"Content-Type":"application/json",...(init?.headers||{})}, ...init });
  const payload = await response.json();
  if(!response.ok) throw new Error(payload.error || payload.detail || response.statusText);
  return payload;
}
const engine=(path:string,init?:RequestInit)=>request(`/workbench/engine${path}`,init);

export function WorkspaceWorkbenchPage(){
  const [workspaces,setWorkspaces]=useState<Workspace[]>([]);
  const [workspace,setWorkspace]=useState<Workspace|null>(null);
  const [snapshot,setSnapshot]=useState<Snapshot|null>(null);
  const [selectedPath,setSelectedPath]=useState<string|null>(null);
  const [document,setDocument]=useState("");
  const [inputs,setInputs]=useState("{}");
  const [implementations,setImplementations]=useState<any[]>([]);
  const [capabilities,setCapabilities]=useState<Record<string,Capability>>({});
  const [validation,setValidation]=useState<string[]|null>(null);
  const [run,setRun]=useState<EngineRun|null>(null);
  const [error,setError]=useState<string|null>(null);
  const [busy,setBusy]=useState(false);
  const parsed=useMemo(()=>{try{return document?JSON.parse(document):null}catch{return null}},[document]);

  useEffect(()=>{void request('/workbench/workspaces').then(p=>setWorkspaces(p.workspaces)).catch(e=>setError(String(e)))},[]);
  useEffect(()=>{
    if(!run || ["completed","failed","cancelled"].includes(run.status)) return;
    const timer=setInterval(()=>void engine(`/runs/${run.id}`).then(p=>setRun(p.run)).catch(e=>setError(String(e))),1000);
    return()=>clearInterval(timer);
  },[run?.id,run?.status]);

  const perform=async(fn:()=>Promise<void>)=>{setBusy(true);setError(null);try{await fn()}catch(e){setError(e instanceof Error?e.message:String(e))}finally{setBusy(false)}};

  const chooseWorkspace=(item:Workspace)=>perform(async()=>{
    const [s,i,c]=await Promise.all([
      request(`/workbench/workspaces/${encodeURIComponent(item.id)}/snapshot`),
      engine('/implementations'), engine('/capabilities')
    ]);
    setWorkspace(s.workspace); setSnapshot(s); setImplementations(i.implementations); setCapabilities(c.capabilities);
    const first=s.workflows.find((row:WorkflowFile)=>row.document);
    if(first){setSelectedPath(first.path);setDocument(JSON.stringify(first.document,null,2));}
    else {setSelectedPath(null);setDocument("");}
    setValidation(null); setRun(null);
  });

  const openFile=(path:string)=>perform(async()=>{
    if(!workspace)return;
    const p=await request(`/workbench/workspaces/${encodeURIComponent(workspace.id)}/file?path=${encodeURIComponent(path)}`);
    setSelectedPath(path); setDocument(p.file.content); setValidation(null);
  });

  const persistCurrentFile=async(content:string=document)=>{
    if(!workspace)throw new Error('Select a workspace');
    const id=parsed?.id || 'workflow';
    const path=selectedPath || `${workspace.workflowDirectoryRelative}/${id}.json`;
    await request(`/workbench/workspaces/${encodeURIComponent(workspace.id)}/file`,{method:'PUT',body:JSON.stringify({path,content})});
    const s=await request(`/workbench/workspaces/${encodeURIComponent(workspace.id)}/snapshot`);
    setSnapshot(s);setSelectedPath(path);
  };

  const saveFile=()=>perform(async()=>{await persistCurrentFile()});

  const validate=()=>perform(async()=>{
    if(!parsed)throw new Error('Current file is not valid workflow JSON');
    const p=await engine('/workflows/validate',{method:'POST',body:JSON.stringify(parsed)});setValidation(p.errors);
  });

  const saveVersion=()=>perform(async()=>{
    if(!parsed)throw new Error('Current file is not valid workflow JSON');
    const p=await engine('/workflows',{method:'POST',body:JSON.stringify(parsed)});
    const content=JSON.stringify(p.workflow,null,2);
    setDocument(content);setValidation([]);
    await persistCurrentFile(content);
  });

  const start=()=>perform(async()=>{
    if(!parsed)throw new Error('Current file is not valid workflow JSON');
    let saved=parsed;
    if(!parsed.version){const p=await engine('/workflows',{method:'POST',body:JSON.stringify(parsed)});saved=p.workflow;const content=JSON.stringify(saved,null,2);setDocument(content);await persistCurrentFile(content);}
    const p=await engine('/runs',{method:'POST',body:JSON.stringify({workflowId:saved.id,version:saved.version,inputs:JSON.parse(inputs)})});setRun(p.run);
  });

  const command=(name:string)=>perform(async()=>{if(!run)return;const p=await engine(`/runs/${run.id}/commands`,{method:'POST',body:JSON.stringify({command:name})});setRun(p.run)});
  const submitHuman=(stepId:string)=>perform(async()=>{if(!run)return;const raw=prompt('Human step values as JSON','{}');if(raw===null)return;const p=await engine(`/runs/${run.id}/steps/${stepId}/input`,{method:'POST',body:raw});setRun(p.run)});

  if(!workspace){
    return <main className="engine-page"><header><div><h1>Select a workspace</h1><p>Workspaces are discovered from real <code>workbench.workspace.json</code> files.</p></div><div className="live">● FILESYSTEM</div></header>{error&&<div className="engine-error">{error}</div>}<section className="run-panel"><h2>Available workspaces</h2>{workspaces.length===0?<p>No workspace manifests were found. Add a <code>workbench.workspace.json</code> file under a configured workspace root.</p>:<div className="workspace-picker">{workspaces.map(item=><button key={item.root} className="step-row" onClick={()=>chooseWorkspace(item)}><b>{item.label}</b><span>{item.workflowFileCount} workflows</span><small>{item.root}</small><em>{item.description}</em></button>)}</div>}</section></main>;
  }

  return <main className="engine-page">
    <header><div><h1>{workspace.label}</h1><p>{workspace.root}</p></div><div><button onClick={()=>{setWorkspace(null);setSnapshot(null)}}>Switch workspace</button> <span className="live">● FILES LIVE</span></div></header>
    {error&&<div className="engine-error">{error}<button onClick={()=>setError(null)}>×</button></div>}
    <section className="engine-grid">
      <aside className="engine-panel catalog"><h2>Workflow files</h2>{snapshot?.workflows.map(row=><button key={row.path} className={selectedPath===row.path?'selected':''} onClick={()=>openFile(row.path)}><b>{row.document?.label||row.document?.id||row.path}</b><small>{row.path}</small>{row.error&&<em>{row.error}</em>}</button>)}<h2>Workspace files</h2>{snapshot?.files.slice(0,300).map(file=><button key={file.path} onClick={()=>openFile(file.path)}><b>{file.name}</b><small>{file.path}</small></button>)}</aside>
      <section className="engine-panel editor"><div className="panel-title"><h2>{selectedPath||'New workflow file'}</h2><div><button disabled={busy} onClick={validate}>Validate</button><button disabled={busy} onClick={saveFile}>Save file</button><button disabled={busy} onClick={saveVersion}>Save engine version</button><button className="primary" disabled={busy} onClick={start}>Run</button></div></div><textarea value={document} onChange={e=>{setDocument(e.target.value);setValidation(null)}} spellCheck={false}/><label>Run inputs</label><textarea className="inputs" value={inputs} onChange={e=>setInputs(e.target.value)} spellCheck={false}/>{validation===null?<div className="validation">Not validated</div>:validation.length?<ul className="validation bad">{validation.map(v=><li key={v}>{v}</li>)}</ul>:<div className="validation good">Validated by backend</div>}</section>
      <aside className="engine-panel capability"><h2>Registered implementations</h2>{implementations.map(i=><div className="implementation" key={i.name}><b>{i.name}</b><small>{Object.keys(i.inputs).join(', ')||'no inputs'} → {Object.keys(i.outputs).join(', ')||'no outputs'}</small></div>)}<h2>Capabilities</h2>{Object.entries(capabilities).map(([name,value])=><div key={name} title={value.detail}><span>{value.status==='implemented'?'✓':value.status==='partial'?'◐':value.status==='unavailable'?'—':'!'}</span><b>{name}</b><small>{value.status}</small><p>{value.detail}</p></div>)}</aside>
    </section>
    {run&&<section className="run-panel"><div className="run-head"><div><h2>Run {run.id.slice(0,8)}</h2><span className={`run-status ${run.status}`}>{run.status}</span></div><div><button onClick={()=>command('pause')}>Pause</button><button onClick={()=>command('resume')}>Resume</button><button onClick={()=>command('advance')}>Advance</button><button onClick={()=>command('replay')}>Replay</button><button className="danger" onClick={()=>command('cancel')}>Cancel</button></div></div><div className="run-columns"><div><h3>Steps</h3>{run.steps.map(step=><button className="step-row" key={step.stepId} onClick={()=>step.status==='waiting'&&submitHuman(step.stepId)}><b>{step.stepId}</b><span>{step.status}</span><small>attempt {step.attempt}{step.childRunId?` · child ${step.childRunId.slice(0,8)}`:''}</small>{step.error&&<em>{step.error}</em>}</button>)}</div><div><h3>Artifacts</h3>{run.artifacts.map(a=><details key={a.id}><summary>{a.name} <small>{a.datatype}</small></summary><pre>{JSON.stringify(a,null,2)}</pre></details>)}</div><div><h3>Events / logs</h3>{run.events.slice().reverse().map(e=><div className="event" key={e.id}><b>{e.kind}</b><small>{e.stepId||'workflow'} · {e.createdAt}</small></div>)}{run.logs.slice().reverse().map(l=><div className={`log ${l.stream}`} key={l.id}><b>{l.stream}</b><pre>{l.message}</pre></div>)}</div></div><details><summary>Run outputs</summary><pre>{JSON.stringify(run.outputs,null,2)}</pre></details></section>}
  </main>;
}
