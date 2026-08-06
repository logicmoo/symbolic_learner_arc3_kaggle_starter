import { useEffect, useMemo, useState } from "react";
import "./WorkflowEnginePage.css";

type Workflow = { id:string; version?:number; label?:string; inputs:Record<string,string>; outputs:Record<string,string>; steps:any[] };
type Capability = { status:"implemented"|"partial"|"unavailable"|"failed"; detail:string };
type EngineRun = { id:string; workflowId:string; workflowVersion:number; status:string; inputs:any; outputs:any; error?:string; steps:any[]; artifacts:any[]; events:any[]; logs:any[]; children:any[] };

const blankWorkflow = (): Workflow => ({ id:"new_workflow", label:"New workflow", inputs:{}, outputs:{}, steps:[] });

async function api(path:string, init?:RequestInit) {
  const response = await fetch(`/api/engine${path}`, { headers:{"Content-Type":"application/json",...(init?.headers||{})}, ...init });
  const payload = await response.json();
  if(!response.ok) throw new Error(payload.error || payload.detail || response.statusText);
  return payload;
}

export function UnmockedWorkflowEnginePage() {
  const [workflows,setWorkflows]=useState<Workflow[]>([]);
  const [implementations,setImplementations]=useState<any[]>([]);
  const [capabilities,setCapabilities]=useState<Record<string,Capability>>({});
  const [document,setDocument]=useState("");
  const [inputs,setInputs]=useState("{}");
  const [validation,setValidation]=useState<string[]|null>(null);
  const [run,setRun]=useState<EngineRun|null>(null);
  const [error,setError]=useState<string|null>(null);
  const [busy,setBusy]=useState(false);
  const parsed=useMemo(()=>{try{return document?JSON.parse(document) as Workflow:null}catch{return null}},[document]);

  const refreshCatalog=async()=>{
    const [w,i,c]=await Promise.all([api('/workflows'),api('/implementations'),api('/capabilities')]);
    setWorkflows(w.workflows); setImplementations(i.implementations); setCapabilities(c.capabilities);
    if(!document){
      const first=w.workflows[0] || blankWorkflow();
      setDocument(JSON.stringify(first,null,2));
    }
  };

  useEffect(()=>{void refreshCatalog().catch(e=>setError(String(e)))},[]);
  useEffect(()=>{
    if(!run || ["completed","failed","cancelled"].includes(run.status)) return;
    const timer=setInterval(async()=>{try{const p=await api(`/runs/${run.id}`);setRun(p.run)}catch(e){setError(String(e))}},1000);
    return()=>clearInterval(timer);
  },[run?.id,run?.status]);

  const perform=async(fn:()=>Promise<void>)=>{setBusy(true);setError(null);try{await fn()}catch(e){setError(e instanceof Error?e.message:String(e))}finally{setBusy(false)}};
  const validate=()=>perform(async()=>{if(!parsed)throw new Error('Invalid JSON');const p=await api('/workflows/validate',{method:'POST',body:JSON.stringify(parsed)});setValidation(p.errors)});
  const save=()=>perform(async()=>{if(!parsed)throw new Error('Invalid JSON');const p=await api('/workflows',{method:'POST',body:JSON.stringify(parsed)});setDocument(JSON.stringify(p.workflow,null,2));setValidation([]);await refreshCatalog()});
  const start=()=>perform(async()=>{if(!parsed)throw new Error('Invalid workflow JSON');let saved=parsed;if(!parsed.version){const p=await api('/workflows',{method:'POST',body:JSON.stringify(parsed)});saved=p.workflow;setDocument(JSON.stringify(saved,null,2))}const p=await api('/runs',{method:'POST',body:JSON.stringify({workflowId:saved.id,version:saved.version,inputs:JSON.parse(inputs)})});setRun(p.run)});
  const command=(name:string)=>perform(async()=>{if(!run)return;const p=await api(`/runs/${run.id}/commands`,{method:'POST',body:JSON.stringify({command:name})});setRun(p.run)});
  const submitHuman=(stepId:string)=>perform(async()=>{if(!run)return;const raw=prompt('Human step values as JSON','{}');if(raw===null)return;const p=await api(`/runs/${run.id}/steps/${stepId}/input`,{method:'POST',body:raw});setRun(p.run)});

  return <main className="engine-page">
    <header><div><h1>MeTTa Workflow Engine</h1><p>Backend-authoritative workflow definitions, capabilities, execution, artifacts and logs</p></div><div className="live">● ENGINE LIVE</div></header>
    {error&&<div className="engine-error">{error}<button onClick={()=>setError(null)}>×</button></div>}
    <section className="engine-grid">
      <aside className="engine-panel catalog"><div className="panel-title"><h2>Workflows</h2><button onClick={()=>{setDocument(JSON.stringify(blankWorkflow(),null,2));setValidation(null)}}>New</button></div>{workflows.length===0&&<p>No persisted workflows.</p>}{workflows.map(w=><button key={`${w.id}:${w.version}`} onClick={()=>{setDocument(JSON.stringify(w,null,2));setValidation(null)}}><b>{w.label||w.id}</b><small>{w.id} · v{w.version}</small></button>)}<h2>Registered implementations</h2>{implementations.map(i=><div className="implementation" key={i.name}><b>{i.name}</b><small>{Object.keys(i.inputs).join(', ')||'no inputs'} → {Object.keys(i.outputs).join(', ')||'no outputs'}</small></div>)}</aside>
      <section className="engine-panel editor"><div className="panel-title"><h2>Workflow document</h2><div><button disabled={busy} onClick={validate}>Validate</button><button disabled={busy} onClick={save}>Save version</button><button className="primary" disabled={busy} onClick={start}>Run</button></div></div><textarea value={document} onChange={e=>{setDocument(e.target.value);setValidation(null)}} spellCheck={false}/><label>Run inputs</label><textarea className="inputs" value={inputs} onChange={e=>setInputs(e.target.value)} spellCheck={false}/>{validation===null?<div className="validation">Not validated</div>:validation.length?<ul className="validation bad">{validation.map(v=><li key={v}>{v}</li>)}</ul>:<div className="validation good">Validated by backend</div>}</section>
      <aside className="engine-panel capability"><h2>Runtime capabilities</h2>{Object.entries(capabilities).map(([name,value])=><div key={name} title={value.detail}><span>{value.status==='implemented'?'✓':value.status==='partial'?'◐':value.status==='unavailable'?'—':'!'}</span><b>{name}</b><small>{value.status}</small><p>{value.detail}</p></div>)}</aside>
    </section>
    {run&&<section className="run-panel"><div className="run-head"><div><h2>Run {run.id.slice(0,8)}</h2><span className={`run-status ${run.status}`}>{run.status}</span></div><div><button onClick={()=>command('pause')}>Pause</button><button onClick={()=>command('resume')}>Resume</button><button onClick={()=>command('advance')}>Advance</button><button onClick={()=>command('replay')}>Replay</button><button className="danger" onClick={()=>command('cancel')}>Cancel</button></div></div><div className="run-columns"><div><h3>Steps</h3>{run.steps.map(step=><button className="step-row" key={step.stepId} onClick={()=>step.status==='waiting'&&submitHuman(step.stepId)}><b>{step.stepId}</b><span>{step.status}</span><small>attempt {step.attempt}{step.childRunId?` · child ${step.childRunId.slice(0,8)}`:''}</small>{step.error&&<em>{step.error}</em>}</button>)}</div><div><h3>Artifacts</h3>{run.artifacts.map(a=><details key={a.id}><summary>{a.name} <small>{a.datatype}</small></summary><pre>{JSON.stringify(a,null,2)}</pre></details>)}</div><div><h3>Events / logs</h3>{run.events.slice().reverse().map(e=><div className="event" key={e.id}><b>{e.kind}</b><small>{e.stepId||'workflow'} · {e.createdAt}</small></div>)}{run.logs.slice().reverse().map(l=><div className={`log ${l.stream}`} key={l.id}><b>{l.stream}</b><pre>{l.message}</pre></div>)}</div></div><details><summary>Run outputs</summary><pre>{JSON.stringify(run.outputs,null,2)}</pre></details></section>}
  </main>;
}
