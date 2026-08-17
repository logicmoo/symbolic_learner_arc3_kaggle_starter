import {useMemo,useState} from "react";
import {WorkspaceFileRunner} from "./WorkspaceFileRunner";

type WorkspaceFile={path:string;name:string;suffix:string;size:number;modified:number;kind:string};
const imageSuffixes=new Set([".png",".jpg",".jpeg",".gif",".webp",".bmp",".svg"]);
const artifactFile=(file:WorkspaceFile)=>/(^|\/)(artifacts?|outputs?)(\/|$)/i.test(file.path)&&!/\.md$/i.test(file.path);

export function KnowledgeArtifactExplorer({workspaceId,files}:{workspaceId:string;files:WorkspaceFile[]}){
 const artifacts=useMemo(()=>files.filter(artifactFile).sort((left,right)=>right.modified-left.modified),[files]);
 const[selectedPath,setSelectedPath]=useState("");
 const selected=artifacts.find(file=>file.path===selectedPath)||null;
 const assetUrl=selected?`/api/workspaces/${encodeURIComponent(workspaceId)}/asset?path=${encodeURIComponent(selected.path)}`:"";
 const source=selected?.path.startsWith("runtime/")?"Runtime output":selected?.path.startsWith("knowledge/")?"Knowledge artifact":"Workspace artifact";
 return <section className="resource-view knowledge-artifact-explorer"><div className="resource-heading"><div><span>PERSISTENT TYPED OUTPUTS</span><h1>Artifacts</h1><p>Produced and imported values persisted across the workspace. The Workflow Artifact Explorer remains scoped to the active run.</p></div></div><div className="knowledge-data-layout"><div className="resource-table"><div className="resource-row resource-head"><span>ARTIFACT</span><span>SOURCE</span><span>FORMAT</span><span>SIZE</span><span>WORKSPACE PATH</span></div>{artifacts.map(file=><button type="button" className={`resource-row ${selectedPath===file.path?"selected":""}`} onClick={()=>setSelectedPath(file.path)} key={file.path}><b>{file.name}</b><code>{file.path.startsWith("runtime/")?"runtime":"knowledge"}</code><span>{file.suffix||"value"}</span><span>{file.size.toLocaleString()} bytes</span><em>{file.path}</em></button>)}{artifacts.length===0&&<div className="studio-empty">No persistent artifacts yet. Run a Workflow or import an artifact into knowledge/artifacts.</div>}</div>{selected&&<aside className="knowledge-data-preview"><span>{source.toUpperCase()}</span><h2>{selected.name}</h2>{imageSuffixes.has(selected.suffix.toLowerCase())?<img src={assetUrl} alt={`Preview of ${selected.name}`}/>:<div className="knowledge-data-file-icon">{selected.suffix||"ARTIFACT"}</div>}<dl><dt>Path</dt><dd>{selected.path}</dd><dt>Size</dt><dd>{selected.size.toLocaleString()} bytes</dd><dt>Modified</dt><dd>{new Date(selected.modified*1000).toLocaleString()}</dd></dl><a href={assetUrl} target="_blank" rel="noreferrer">Open persisted artifact</a></aside>}</div>{selected&&<WorkspaceFileRunner workspaceId={workspaceId} file={selected} resourceKind="artifact"/>}</section>;
}
