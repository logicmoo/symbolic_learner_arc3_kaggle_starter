import {useEffect,useState} from "react";
import {jsonValueToMetta} from "../lib/mettaResourceCodec";
import "../styles/operation_playground.css";

type ModelResource={id:string;label?:string;description?:string;enabled?:boolean};
type ModelInvocation={modelId:string;text?:string;latencyMs?:number;inputTokens?:number;outputTokens?:number;responseId?:string;backendId?:string;debugLogPath?:string};

class RequestFailure extends Error{debugLogPath?:string;constructor(message:string,debugLogPath?:string){super(message);this.debugLogPath=debugLogPath}}

async function request(path:string,init?:RequestInit){
 const response=await fetch(path,{cache:"no-store",headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});
 const text=await response.text();let payload:any;
 try{payload=JSON.parse(text)}catch{throw new Error(text||response.statusText)}
 if(!response.ok){const detail=payload.error||payload.detail||response.statusText;throw new RequestFailure(typeof detail==="string"?detail:String(detail?.message||JSON.stringify(detail,null,2)),typeof detail==="object"?detail?.debugLogPath:undefined)}
 return payload;
}

export function ModelResourcePlayground({workspaceId,model,resolved}:{workspaceId:string;model:ModelResource;resolved?:Record<string,unknown>}){
 const[prompt,setPrompt]=useState("Introduce yourself briefly and state which model handled this request.");
 const[timeoutSeconds,setTimeoutSeconds]=useState(120),[running,setRunning]=useState(false),[result,setResult]=useState<ModelInvocation|null>(null),[error,setError]=useState<string|null>(null),[debugLogPath,setDebugLogPath]=useState<string|null>(null),[debugLog,setDebugLog]=useState("");
 useEffect(()=>{setResult(null);setError(null);setDebugLogPath(null);setDebugLog("")},[model.id,workspaceId]);
 const loadDebugLog=async(path:string)=>{setDebugLogPath(path);setDebugLog("Loading complete invocation trace…");try{const payload=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/debug-log?path=${encodeURIComponent(path)}`);setDebugLog(String(payload.content||""))}catch(reason){setDebugLog(`Debug trace could not be loaded: ${reason instanceof Error?reason.message:String(reason)}`)}};
 const run=async()=>{setRunning(true);setResult(null);setError(null);setDebugLogPath(null);setDebugLog("");try{const invocation=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/${encodeURIComponent(model.id)}/invoke`,{method:"POST",body:JSON.stringify({prompt,timeoutSeconds})}) as ModelInvocation;setResult(invocation);if(invocation.debugLogPath)await loadDebugLog(invocation.debugLogPath)}catch(reason){setError(reason instanceof Error?reason.message:String(reason));if(reason instanceof RequestFailure&&reason.debugLogPath)await loadDebugLog(reason.debugLogPath)}finally{setRunning(false)}};
 return <section className="operation-playground model-resource-playground">
  <div className="llm-subhead"><div><span>UNIVERSAL EXECUTION RUNNER</span><b>Invoke this resource through its resolved backend and inherited defaults</b></div></div>
  <div className="operation-playground-grid">
   <label className="operation-playground-field"><span>RUN RESOURCE</span><input readOnly value={`${model.label||model.id} · ${String(resolved?.model||model.id)}`}/><small>This run uses the open resource directly and does not change its parent, preset, or saved defaults.</small></label>
   <label className="operation-playground-field"><span>TIMEOUT · seconds</span><input type="number" min={1} max={3600} value={timeoutSeconds} onChange={event=>setTimeoutSeconds(Math.max(1,Number(event.target.value)||1))}/></label>
   <label className="operation-playground-field model-runner-prompt"><span>INPUT · prompt <em>Text</em></span><textarea value={prompt} onChange={event=>setPrompt(event.target.value)} placeholder="Enter a prompt…"/></label>
   <div className="operation-run-actions"><button className="primary" type="button" onClick={()=>void run()} disabled={running||!prompt.trim()}>{running?"Running…":"▶ Run Resource"}</button></div>
  </div>
  <div className="operation-playground-contract"><span>OUTPUT CONTRACT</span><code>text: Text</code><code>response: ModelInvocation</code></div>
  {error&&<div className="demo-notice"><b>Invocation failed</b><span>{error}</span></div>}
  {result&&<div className="operation-playground-result"><div><span>RESULT</span><b>{model.label||model.id}</b><small>{result.backendId||"resolved backend"} · {result.latencyMs??0} ms · {result.inputTokens??0}/{result.outputTokens??0} tokens</small></div><pre>{result.text||""}</pre><details><summary>Complete response</summary><pre>{jsonValueToMetta(result)}</pre></details></div>}
  {debugLogPath&&<details className="operation-debug-trace" open><summary><span>COMPLETE DEBUG TRACE</span><code>{debugLogPath}</code></summary><pre>{debugLog}</pre></details>}
 </section>;
}
