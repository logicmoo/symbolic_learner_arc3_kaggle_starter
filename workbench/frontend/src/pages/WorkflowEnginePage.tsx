import { useEffect, useMemo, useState } from "react";
import "./WorkflowEnginePage.css";

type Workflow = { id: string; version?: number; label?: string; inputs: Record<string,string>; outputs: Record<string,string>; steps: any[] };
type EngineRun = { id:string; workflowId:string; workflowVersion:number; status:string; inputs:any; outputs:any; error?:string; steps:any[]; artifacts:any[]; events:any[]; logs:any[]; children:any[] };

const sample: Workflow = {
  id: "generic_review",
  label: "Generic review workflow",
  inputs: { payload: "Any" },
  outputs: { result: "$approved" },
  steps: [
    { id: "copy", kind: "task", implementation: "core.echo", inputs: { value: "$payload" }, outputs: { value: "copied" } },
    { id: "approve", kind: "human", dependsOn: ["copy"], form: { approved: { type: "Boolean" } }, outputs: { approved: "approved" } }
  ]
};

async function api(path:string, init?:RequestInit) {
  const response = await fetch(`/api/engine${path}`, { headers: { "Content-Type":"application/json", ...(init?.headers||{}) }, ...init });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || payload.detail || response.statusText);
  return payload;
}

export function WorkflowEnginePage() {
  const [workflows,setWorkflows]=useState<Workflow[]>([]);
  const [implementations,setImplementations]=useState<any[]>([]);
  const [capabilities,setCapabilities]=useState<Record<string,boolean>>({});
  const [document,setDocument]=useState(JSON.stringify(sample,null,2));
  const [inputs,setInputs]=useState('{"payload":{"message":"hello"}}');
  const [validation,setValidation]=useState<string[]>([]);
  const [run,setRun]=useState<EngineRun|null>(null);
  const [error,setError]=useState<string|null>(null);
  const [busy,setBusy]=useState(false);
  const parsed=useMemo(()=>{try{return JSON.parse(document) as Workflow}catch{return null}},[document]);

  const refreshCatalog=async()=>{
    try {
      const [w,i,c]=await Promise.all([api('/workflows'),api('/implementations'),api('/capabilities')]);
      setWorkflows(w.workflows); setImplementations(i.implementations); setCapabilities(c.capabilities);
    } catch(e){setError(String(e))}
  };
  useEffect(()=>{void refreshCatalog()},[]);
  useEffect(()=>{
    if(!run || ["completed","failed","cancelled"].includes(run.status)) return;
    const timer=setInterval(async()=>{try{const p=await api(`/runs/${run.id}`);setRun(p.run)}catch{}},1000);
    return()=>clearInterval(timer);
  },[run?.id,run?.status]);

  const perform=async(fn:()=>Promise<void>)=>{setBusy(true);setError(null);try{await fn()}catch(e){setError(e instanceof Error?e.message:String(e))}finally{setBusy(false)}};
  const validate=()=>perform(async()=>{if(!parsed)throw new Error('Invalid JSON');const p=await api('/workflows/validate',{method:'POST',body:JSON.stringify(parsed)});setValidation(p.errors)});
  const save=()=>perform(async()=>{if(!parsed)throw new Error('Invalid JSON');const p=await api('/workflows',{method:'POST',body:JSON.stringify(parsed)});setDocument(JSON.stringify(p.workflow,null,2));await refreshCatalog()});
  const start=()=>perform(async()=>{if(!parsed)throw new Error('Invalid workflow JSON');let workflowId=parsed.id;if(!parsed.version){const p=await api('/workflows',{method:'POST',body:JSON.stringify(parsed)});workflowId=p.workflow.id;setDocument(JSON.stringify(p.workflow,null,2))}const p=await api('/runs',{method:'POST',body:JSON.stringify({workflowId,inputs:JSON.parse(inputs)})});setRun(p.run);await refreshCatalog()});
  const command=(name:string)=>perform(async()=>{if(!run)return;const p=await api(`/runs/${run.id}/commands`,{method:'POST',body:JSON.stringify({command:name})});setRun(p.run)});
  const submitHuman=(stepId:string)=>perform(async()=>{if(!run)return;const raw=prompt('Human step values as JSON','{"approved":true}');if(raw===null)return;const p=await api(`/runs/${run.id}/steps/${stepId}/input`,{method:'POST',body:raw});setRun(p.run)});

  return <main className="engine-page">
    <header><div><h1>MeTTa Workflow Engine</h1><p>Durable typed workflows · backend authoritative</p></div><div className="live">● ENGINE LIVE</div></header>
    {error&&<div className="engine-error">{error}<button onClick={()=>setError(null)}>×</button></div>}
    <section className="engine-grid">
      <aside className="engine-panel catalog"><h2>Workflows</h2>{workflows.map(w=><button key={`${w.id}:${w.version}`} onClick={()=>setDocument(JSON.stringify(w,null,2))}><b>{w.label||w.id}</b><small>{w.id} · v{w.version}</small></button>)}<h2>Implementations</h2>{implementations.map(i=><div className="implementation" key={i.name}><b>{i.name}</b><small>{Object.keys(i.inputs).join(', ')||'no inputs'} → {Object.keys(i.outputs).join(', ')||'no outputs'}</small></div>)}</aside>
      <section className="engine-panel editor"><div className="panel-title"><h2>Versioned workflow document</h2><div><button disabled={busy} onClick={validate}>Validate</button><button disabled={busy} onClick={save}>Save version</button><button className="primary" disabled={busy} onClick={start}>Run</button></div></div><textarea value={document} onChange={e=>setDocument(e.target.value)} spellCheck={false}/><label>Run inputs</label><textarea className="inputs" value={inputs} onChange={e=>setInputs(e.target.value)} spellCheck={false}/>{validation.length>0?<ul className="validation bad">{validation.map(v=><li key={v}>{v}</li>)}</ul>:<div className="validation good">No validation errors</div>}</section>
      <aside className="engine-panel capability"><h2>Engine capabilities</h2>{Object.entries(capabilities).map(([name,on])=><div key={name}><span>{on?'✓':'—'}</span>{name}</div>)}</aside>
    </section>
    {run&&<section className="run-panel"><div className="run-head"><div><h2>Run {run.id.slice(0,8)}</h2><span className={`run-status ${run.status}`}>{run.status}</span></div><div><button onClick={()=>command('pause')}>Pause</button><button onClick={()=>command('resume')}>Resume</button><button onClick={()=>command('advance')}>Advance</button><button onClick={()=>command('replay')}>Replay</button><button className="danger" onClick={()=>command('cancel')}>Cancel</button></div></div><div className="run-columns"><div><h3>Steps</h3>{run.steps.map(step=><button className="step-row" key={step.stepId} onClick={()=>step.status==='waiting'&&submitHuman(step.stepId)}><b>{step.stepId}</b><span>{step.status}</span><small>attempt {step.attempt}{step.childRunId?` · child ${step.childRunId.slice(0,8)}`:''}</small>{step.error&&<em>{step.error}</em>}</button>)}</div><div><h3>Artifacts</h3>{run.artifacts.map(a=><details key={a.id}><summary>{a.name} <small>{a.datatype}</small></summary><pre>{JSON.stringify(a,null,2)}</pre></details>)}</div><div><h3>Events / logs</h3>{run.events.slice().reverse().map(e=><div className="event" key={e.id}><b>{e.kind}</b><small>{e.stepId||'workflow'} · {e.createdAt}</small></div>)}{run.logs.slice().reverse().map(l=><div className={`log ${l.stream}`} key={l.id}><b>{l.stream}</b><pre>{l.message}</pre></div>)}</div></div><details><summary>Run outputs</summary><pre>{JSON.stringify(run.outputs,null,2)}</pre></details></section>}
  </main>;
}
