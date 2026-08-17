import {useEffect,useState} from "react";
import {ResourceExecutionPlayground} from "./ResourceExecutionPlayground";

type WorkspaceFile={path:string;name:string;suffix:string;size:number;modified:number;kind:string};
type FileResource={kind:"data"|"artifact";id:string;label:string;workspacePath:string;format:string;size:number;modified:number;mediaType:string;value?:unknown;valueEncoding?:string;contentOmitted?:boolean};

const textSuffixes=new Set([".txt",".md",".json",".jsonl",".csv",".tsv",".metta",".pl",".py",".xml",".yaml",".yml"]);
const imageMedia=(mediaType:string)=>mediaType.startsWith("image/");
const blobDataUrl=(blob:Blob)=>new Promise<string>((resolve,reject)=>{const reader=new FileReader();reader.onerror=()=>reject(reader.error||new Error("Could not read workspace asset"));reader.onload=()=>resolve(String(reader.result||""));reader.readAsDataURL(blob)});

export function WorkspaceFileRunner({workspaceId,file,resourceKind}:{workspaceId:string;file:WorkspaceFile;resourceKind:"data"|"artifact"}){
 const[resource,setResource]=useState<FileResource|null>(null),[error,setError]=useState("");
 useEffect(()=>{let active=true;setResource(null);setError("");void(async()=>{try{const response=await fetch(`/api/workspaces/${encodeURIComponent(workspaceId)}/asset?path=${encodeURIComponent(file.path)}`,{cache:"no-store"});if(!response.ok)throw new Error(`Could not load selected file (${response.status})`);const mediaType=(response.headers.get("content-type")||"application/octet-stream").split(";",1)[0];const next:FileResource={kind:resourceKind,id:file.path,label:file.name,workspacePath:file.path,format:file.suffix||"file",size:file.size,modified:file.modified,mediaType};if(imageMedia(mediaType)){next.value=await blobDataUrl(await response.blob());next.valueEncoding="data-url"}else if(mediaType.startsWith("text/")||mediaType.includes("json")||textSuffixes.has(file.suffix.toLowerCase())){const text=await response.text();try{next.value=JSON.parse(text)}catch{next.value=text}next.valueEncoding="text"}else{next.contentOmitted=true}if(active)setResource(next)}catch(reason){if(active)setError(reason instanceof Error?reason.message:String(reason))}})();return()=>{active=false}},[workspaceId,file.path,resourceKind]);
 return <section className="workspace-file-runner"><div className="llm-subhead"><div><span>SELECTED FILE RUNNER</span><b>{file.name}</b><small>The file is loaded through the workspace asset provider and supplied as a typed resource to the universal runner.</small></div></div>{error&&<div className="demo-notice"><b>FILE LOAD FAILED</b><span>{error}</span></div>}{resource?<ResourceExecutionPlayground workspaceId={workspaceId} resource={resource} operationIds={resourceKind==="data"?["data_inspect","resource_validate"]:["artifact_inspect","resource_validate"]}/>:!error&&<div className="studio-empty">Loading the selected file through the resource provider…</div>}</section>;
}
