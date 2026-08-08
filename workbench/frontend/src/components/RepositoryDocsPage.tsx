import {useEffect,useMemo,useState} from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "../styles/repository_docs.css";

type DocumentEntry={path:string;name:string;size:number;modified:number;checksum:string};
type OpenDocument={path:string;content:string;format:"markdown"|"source";checksum:string};

async function requestJson(path:string){
 const response=await fetch(path);const payload=await response.json();
 if(!response.ok)throw new Error(payload.detail||response.statusText);
 return payload;
}
const parentPath=(path:string)=>path.includes("/")?path.slice(0,path.lastIndexOf("/")):"Repository root";
function resolvePath(current:string,href:string){
 const clean=href.split("#",1)[0];if(clean.startsWith("/"))return clean.replace(/^\/+/,"");
 const parts=current.split("/");parts.pop();
 for(const part of clean.split("/")){if(!part||part===".")continue;if(part==="..")parts.pop();else parts.push(part)}
 return parts.join("/");
}

export function RepositoryDocsPage({initialFilter=""}:{initialFilter?:string}){
 const[documents,setDocuments]=useState<DocumentEntry[]>([]),[opened,setOpened]=useState<OpenDocument|null>(null),[history,setHistory]=useState<OpenDocument[]>([]),[filter,setFilter]=useState(initialFilter),[error,setError]=useState(""),[refreshing,setRefreshing]=useState(false);
 const load=async(path:string,remember=false)=>{try{const payload=await requestJson(`/api/repository/file?path=${encodeURIComponent(path)}`);if(remember&&opened)setHistory(current=>[...current,opened]);setOpened({path:payload.path,content:payload.content,format:payload.format,checksum:payload.checksum});setError("")}catch(reason){setError(String(reason))}};
 const back=()=>setHistory(current=>{const next=[...current];setOpened(next.pop()||null);return next});
 const refresh=async()=>{setRefreshing(true);try{const payload=await requestJson("/api/repository/markdown-index");const next=(payload.documents||[]) as DocumentEntry[];setDocuments(next);if(opened){const current=next.find(item=>item.path===opened.path);if(!current){setOpened(null);setError(`Document was removed from disk: ${opened.path}`)}else if(current.checksum!==opened.checksum)await load(opened.path);else setError("")}else setError("")}catch(reason){setError(String(reason))}finally{setRefreshing(false)}};
 useEffect(()=>{void refresh()},[]);
 useEffect(()=>setFilter(initialFilter),[initialFilter]);
 const visible=useMemo(()=>{const query=filter.trim().toLowerCase();return query?documents.filter(item=>item.path.toLowerCase().includes(query)):documents},[documents,filter]);
 return <section className="repository-docs-page">
  <aside className="repository-docs-index">
   <div className="repository-docs-heading"><span>REPOSITORY DOCUMENTATION</span><div><h1>Docs</h1><button onClick={()=>void refresh()} disabled={refreshing}>{refreshing?"Refreshing...":"Refresh"}</button></div><p>{documents.length} Markdown files indexed from disk.</p></div>
   <input value={filter} onChange={event=>setFilter(event.target.value)} placeholder="Filter paths and filenames..." aria-label="Filter repository documents"/>
   <div className="repository-doc-links">{visible.map(item=><button key={item.path} className={opened?.path===item.path?"active":""} onClick={()=>{setHistory([]);void load(item.path)}}><small>{parentPath(item.path)}</small><b>{item.name}</b></button>)}</div>
  </aside>
  <article className="repository-doc-view markdown-body">
   {error&&<div className="backend-error">{error}</div>}
   {opened?<>
    <div className="repository-doc-path">{history.length>0&&<button onClick={back}>← Back</button>}<span>FILESYSTEM DOCUMENT</span><code>{opened.path}</code></div>
    {opened.format==="markdown"?<ReactMarkdown remarkPlugins={[remarkGfm]} components={{a:({node:_node,href="",...props})=>{
     const local=!/^(https?:|mailto:|#)/i.test(href);
     return <a {...props} href={local?"#":href} target={local?undefined:"_blank"} rel={local?undefined:"noreferrer"} onClick={local?(event=>{event.preventDefault();event.stopPropagation();void load(resolvePath(opened.path,href),true)}):undefined}/>;
    }}}>{opened.content}</ReactMarkdown>:<pre className="repository-source-view"><code>{opened.content}</code></pre>}
   </>:<div className="studio-empty">Select a Markdown document. Use "Datatype Guide" for the AtomSpace and datatype architecture guide.</div>}
  </article>
 </section>;
}
