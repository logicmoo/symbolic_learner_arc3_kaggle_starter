import {useEffect,useState} from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "../styles/help_tabs.css";

type HelpTab={id:string;label:string;path?:string};
type OpenedDocument={path:string;content:string};

const docTabs:HelpTab[]=[
 {id:"overview",label:"Overview",path:"docs/models_profiles_operations_prompts.md"},
 {id:"goals",label:"Goals",path:"docs/goals.md"},
 {id:"plans",label:"Plans",path:"docs/plans.md"},
 {id:"data",label:"Data",path:"docs/data.md"},
 {id:"llms",label:"LLMs",path:"docs/llm_catalog.md"},
 {id:"operations",label:"Operations",path:"docs/operations.md"},
 {id:"policies",label:"Policies",path:"docs/policies.md"},
 {id:"prompts",label:"Prompts",path:"docs/prompts.md"},
 {id:"migration",label:"Migration",path:"docs/legacy_llm_migration.md"},
];

async function readShared(path:string){
 const response=await fetch(`/api/workspaces/shared/file?path=${encodeURIComponent(path)}`);
 const text=await response.text();let payload:any;
 try{payload=JSON.parse(text)}catch{throw new Error(text||response.statusText)}
 if(!response.ok)throw new Error(payload.error||payload.detail||response.statusText);
 return String(payload.file?.content||"");
}

async function readRepository(path:string){
 const response=await fetch(`/api/repository/markdown?path=${encodeURIComponent(path)}`);
 const payload=await response.json();
 if(!response.ok)throw new Error(payload.error||payload.detail||response.statusText);
 return {path:String(payload.path),content:String(payload.content)} as OpenedDocument;
}

const repositoryPath=(path:string)=>`workbench/workspaces/shared/${path}`;
function resolveMarkdownPath(currentPath:string,href:string){
 const clean=href.split("#",1)[0];
 if(clean.startsWith("/"))return clean.replace(/^\/+/,"");
 const parts=currentPath.split("/");parts.pop();
 for(const part of clean.split("/")){if(!part||part===".")continue;if(part==="..")parts.pop();else parts.push(part)}
 return parts.join("/");
}

export function HelpDocumentTabs({preferred,context}:{preferred?:string;context?:string}){
 const tabs:HelpTab[]=[{id:"context",label:"Context"},...docTabs];
 const initial=preferred&&tabs.some(tab=>tab.id===preferred)?preferred:"context";
 const[active,setActive]=useState(initial),[docs,setDocs]=useState<Record<string,string>>({}),[errors,setErrors]=useState<Record<string,string>>({});
 const[opened,setOpened]=useState<OpenedDocument|null>(null),[history,setHistory]=useState<OpenedDocument[]>([]);
 useEffect(()=>{let cancelled=false;setDocs({});setErrors({});for(const tab of docTabs)void readShared(tab.path!).then(content=>{if(!cancelled)setDocs(current=>({...current,[tab.id]:content}))}).catch(reason=>{if(!cancelled)setErrors(current=>({...current,[tab.id]:String(reason)}))});return()=>{cancelled=true}},[]);
 useEffect(()=>{if(preferred&&tabs.some(tab=>tab.id===preferred)){setActive(preferred);setOpened(null);setHistory([])}},[preferred]);
 const tab=tabs.find(item=>item.id===active)!;
 const baseDocument:OpenedDocument={path:tab.path?repositoryPath(tab.path):"",content:active==="context"?(context?`\`\`\`json\n${context}\n\`\`\``:"No contextual inspector data is available for this page."):errors[active]?`> **Documentation failed to load:** ${errors[active]}`:(docs[active]||"Loading shared documentation…")};
 const document=opened||baseDocument;
 const navigate=async(href:string)=>{const next=await readRepository(resolveMarkdownPath(document.path,href));setHistory(current=>[...current,document]);setOpened(next)};
 const back=()=>setHistory(current=>{const next=[...current];setOpened(next.pop()||null);return next});
 return <div className="help-doc-inspector">
  <div className="help-doc-tabs">{history.length>0&&<button onClick={back}>← Back</button>}{tabs.map(item=><button key={item.id} className={active===item.id&&!opened?"active":""} onClick={()=>{setActive(item.id);setOpened(null);setHistory([])}}>{item.label}</button>)}</div>
  <div className="inspect-section relationship-guide"><article className="relationship-markdown markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]} components={{a:({node:_node,href="",...props})=>{const localMarkdown=!/^(https?:|mailto:|#)/i.test(href)&&href.split("#",1)[0].toLowerCase().endsWith(".md");return <a {...props} href={href} target={localMarkdown?undefined:"_blank"} rel={localMarkdown?undefined:"noreferrer"} onClick={localMarkdown?event=>{event.preventDefault();void navigate(href).catch(reason=>setErrors(current=>({...current,[active]:String(reason)})))}:undefined}/>}}}>{document.content}</ReactMarkdown></article></div>
  <div className="provenance-foot">{active==="context"&&!opened?<><span>INSPECTOR SOURCE</span><code>current workspace state</code><span className="verified">✓ live data</span></>:<><span>DOCUMENTATION SOURCE</span><code>{document.path}</code><span className={errors[active]?"":"verified"}>{errors[active]?"load error":"✓ filesystem backed"}</span></>}</div>
 </div>;
}
