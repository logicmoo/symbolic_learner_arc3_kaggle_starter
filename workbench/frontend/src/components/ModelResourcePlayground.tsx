import {useEffect,useState} from "react";
import {jsonValueToMetta} from "../lib/mettaResourceCodec";
import {InvocationDebugTrace} from "./InvocationDebugTrace";
import {UniversalExecutionControls,type RunnerPopulationMode} from "./UniversalExecutionControls";
import "../styles/operation_playground.css";

type ModelResource={id:string;label?:string;description?:string;enabled?:boolean};
type RunnerOperation={id:string;label?:string;inputs?:Record<string,unknown>};
type ModelInvocation={modelId:string;text?:string;latencyMs?:number;inputTokens?:number;outputTokens?:number;responseId?:string;backendId?:string;debugLogPath?:string};

class RequestFailure extends Error{debugLogPath?:string;constructor(message:string,debugLogPath?:string){super(message);this.debugLogPath=debugLogPath}}

async function request(path:string,init?:RequestInit){
 const response=await fetch(path,{cache:"no-store",headers:{"Content-Type":"application/json",...(init?.headers||{})},...init});
 const text=await response.text();let payload:any;
 try{payload=JSON.parse(text)}catch{throw new Error(text||response.statusText)}
 if(!response.ok){const detail=payload.error||payload.detail||response.statusText;throw new RequestFailure(typeof detail==="string"?detail:String(detail?.message||JSON.stringify(detail,null,2)),typeof detail==="object"?detail?.debugLogPath:undefined)}
 return payload;
}

export function ModelResourcePlayground({workspaceId,model,resolved,models=[]}:{workspaceId:string;model:ModelResource;resolved?:Record<string,unknown>;models?:ModelResource[]}){
 const samplePrompt="Introduce yourself briefly and state which model handled this request.";
 const[prompt,setPrompt]=useState(samplePrompt);
 const[image,setImage]=useState("");
 const[timeoutSeconds,setTimeoutSeconds]=useState(120),[running,setRunning]=useState(false),[populating,setPopulating]=useState<RunnerPopulationMode|null>(null),[populationMessage,setPopulationMessage]=useState<string|null>(null),[result,setResult]=useState<ModelInvocation|null>(null),[error,setError]=useState<string|null>(null),[debugLogPath,setDebugLogPath]=useState<string|null>(null),[debugLog,setDebugLog]=useState("");
 const[selectedModel,setSelectedModel]=useState(model.id),[selectedOperation,setSelectedOperation]=useState("direct_prompt"),[operations,setOperations]=useState<RunnerOperation[]>([]);
 useEffect(()=>{setResult(null);setError(null);setImage("");setDebugLogPath(null);setDebugLog("")},[model.id,workspaceId]);
 useEffect(()=>{setSelectedModel(model.id)},[model.id]);
 useEffect(()=>{void request(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations`).then(payload=>setOperations((payload.operations||[]).map((record:any)=>record.document).filter(Boolean))).catch(()=>setOperations([]))},[workspaceId]);
 const loadDebugLog=async(path:string)=>{setDebugLogPath(path);setDebugLog("Loading complete invocation trace…");try{const family=path.includes("operation_invocations/")?"operations":"models";const payload=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/${family}/debug-log?path=${encodeURIComponent(path)}`);setDebugLog(String(payload.content||""))}catch(reason){setDebugLog(`Debug trace could not be loaded: ${reason instanceof Error?reason.message:String(reason)}`)}};
 const run=async()=>{setRunning(true);setResult(null);setError(null);setDebugLogPath(null);setDebugLog("");try{let invocation:ModelInvocation;if(selectedOperation==="direct_prompt"){invocation=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/${encodeURIComponent(selectedModel)}/invoke`,{method:"POST",body:JSON.stringify({prompt,image:image||undefined,timeoutSeconds})}) as ModelInvocation}else{const operation=operations.find(item=>item.id===selectedOperation);const names=Object.keys(operation?.inputs||{});const inputs=Object.fromEntries(names.map((name,index)=>[name,index===0?prompt:(index===1&&image?image:null)]));const payload=await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/operations/${encodeURIComponent(selectedOperation)}/invoke`,{method:"POST",body:JSON.stringify({inputs,modelSelection:{models:[selectedModel],strategy:"single"},parameters:{timeoutSeconds}})});invocation={modelId:selectedModel,text:JSON.stringify(payload.outputs??payload,null,2),latencyMs:payload.elapsedMs,debugLogPath:payload.debugLogPath}}setResult(invocation);if(invocation.debugLogPath)await loadDebugLog(invocation.debugLogPath)}catch(reason){setError(reason instanceof Error?reason.message:String(reason));if(reason instanceof RequestFailure&&reason.debugLogPath)await loadDebugLog(reason.debugLogPath)}finally{setRunning(false)}};
 const populateInputs=async(mode:RunnerPopulationMode)=>{setPopulating(mode);setPopulationMessage(null);try{
  if(mode==="sample_input"){setPrompt(samplePrompt);setImage("");setPopulationMessage("Restored this model runner's sample prompt.");return}
  if(mode==="empty_null"){setPrompt("");setImage("");setPopulationMessage("Cleared prompt and image inputs.");return}
  const responses=await Promise.allSettled([request(`/api/goal-runs?workspace_id=${encodeURIComponent(workspaceId)}&limit=100`),request(`/api/engine/runs?workspace_id=${encodeURIComponent(workspaceId)}&limit=100`)]);
  const values:unknown[]=[];const collect=(value:unknown)=>{if(value===null||value===undefined)return;if(typeof value==="string"){if(value.trim())values.push(value);return}if(Array.isArray(value)){value.forEach(collect);return}if(typeof value==="object")Object.values(value as Record<string,unknown>).forEach(collect)};
  responses.forEach(response=>{if(response.status==="fulfilled")collect(response.value)});const strings=values.filter((value):value is string=>typeof value==="string");const images=strings.filter(value=>/^data:image\//i.test(value)||/^https?:\/\/.*\.(png|jpe?g|webp)(\?|$)/i.test(value));const texts=strings.filter(value=>!images.includes(value)&&value.length<12000);const pick=<T,>(items:T[])=>mode==="random_outputs"?items[Math.floor(Math.random()*items.length)]:items[items.length-1];const nextText=pick(texts),nextImage=pick(images);if(nextText)setPrompt(nextText);if(nextImage)setImage(nextImage);setPopulationMessage(nextText||nextImage?`Loaded ${mode==="random_outputs"?"random":"latest"} compatible values produced by resources in this workspace.`:"No compatible resource outputs were found. Existing inputs were left unchanged.");
 }catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setPopulating(null)}};
 return <section className="operation-playground model-resource-playground">
  <UniversalExecutionControls title="UNIVERSAL EXECUTION RUNNER" description="Invoke this resource through its resolved backend and inherited defaults" actions={<button className="primary" type="button" onClick={()=>void run()} disabled={running||!prompt.trim()}>{running?"Running…":"▶ Run Resource"}</button>} populating={populating} inputCount={2} onPopulate={populateInputs}/>
  <div className="operation-playground-grid">
   <label className="operation-playground-field"><span>OPERATION · ONE-OFF</span><select value={selectedOperation} onChange={event=>setSelectedOperation(event.target.value)}><option value="direct_prompt">Introduce yourself briefly · direct prompt</option>{operations.map(item=><option key={item.id} value={item.id}>{item.label||item.id}</option>)}</select><small>The initial direct-prompt operation is replaceable without changing this model resource.</small></label>
   <label className="operation-playground-field"><span>MODEL · ONE-OFF</span><select value={selectedModel} onChange={event=>setSelectedModel(event.target.value)}>{models.filter(item=>item.enabled!==false).map(item=><option key={item.id} value={item.id}>{item.label||item.id}</option>)}</select><small>The open model starts selected; choose another enabled model for this run only.</small></label>
   <label className="operation-playground-field"><span>RUN RESOURCE</span><input readOnly value={`${model.label||model.id} · ${String(resolved?.model||model.id)}`}/><small>This run uses the open resource directly and does not change its parent, preset, or saved defaults.</small></label>
   <label className="operation-playground-field"><span>TIMEOUT · seconds</span><input type="number" min={1} max={3600} value={timeoutSeconds} onChange={event=>setTimeoutSeconds(Math.max(1,Number(event.target.value)||1))}/></label>
   <label className="operation-playground-field model-runner-prompt"><span>INPUT · prompt <em>Text</em></span><textarea value={prompt} onChange={event=>setPrompt(event.target.value)} placeholder="Enter a prompt…"/></label>
   <label className="operation-playground-field model-runner-image"><span>INPUT · image <em>Optional</em></span><input type="file" accept="image/*" onChange={event=>{const file=event.target.files?.[0];if(!file)return;const reader=new FileReader();reader.onload=()=>setImage(String(reader.result||""));reader.readAsDataURL(file)}}/><textarea value={image} onChange={event=>setImage(event.target.value)} placeholder="Upload an image or paste an image URL/data URL…"/>{image.startsWith("data:image/")&&<img src={image} alt="Model input preview"/>}</label>
   <div className="operation-run-actions"><button className="primary" type="button" onClick={()=>void run()} disabled={running||!prompt.trim()}>{running?"Running…":"▶ Run Resource"}</button></div>
  </div>
  {populationMessage&&<div className="operation-population-status">{populationMessage}</div>}
  <div className="operation-playground-contract"><span>OUTPUT CONTRACT</span><code>text: Text</code><code>response: ModelInvocation</code></div>
  {error&&<div className="demo-notice"><b>Invocation failed</b><span>{error}</span></div>}
  {result&&<div className="operation-playground-result"><div><span>RESULT</span><b>{model.label||model.id}</b><small>{result.backendId||"resolved backend"} · {result.latencyMs??0} ms · {result.inputTokens??0}/{result.outputTokens??0} tokens</small></div><pre>{result.text||""}</pre><details><summary>Complete response</summary><pre>{jsonValueToMetta(result)}</pre></details></div>}
  {debugLogPath&&<InvocationDebugTrace path={debugLogPath} content={debugLog}/>}
 </section>;
}
