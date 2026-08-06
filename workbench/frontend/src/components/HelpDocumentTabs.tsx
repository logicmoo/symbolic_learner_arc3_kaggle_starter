import {useEffect,useState} from "react";
import "../styles/help_tabs.css";

type HelpTab={id:string;label:string;path?:string};

const docTabs:HelpTab[]=[
 {id:"overview",label:"Overview",path:"docs/models_profiles_tasks_prompts.md"},
 {id:"llms",label:"LLMs",path:"docs/llm_catalog.md"},
 {id:"tasks",label:"Tasks",path:"docs/tasks.md"},
 {id:"prompts",label:"Prompts",path:"docs/prompts.md"},
 {id:"migration",label:"Migration",path:"docs/legacy_llm_migration.md"},
];

async function readShared(path:string){
 const response=await fetch(`/api/workspaces/shared/file?path=${encodeURIComponent(path)}`);
 const text=await response.text();
 let payload:any;
 try{payload=JSON.parse(text)}catch{throw new Error(text||response.statusText)}
 if(!response.ok)throw new Error(payload.detail||response.statusText);
 return String(payload.file?.content||"");
}

export function HelpDocumentTabs({preferred,context}:{preferred?:string;context?:string}){
 const tabs:HelpTab[]=[{id:"context",label:"Context"},...docTabs];
 const initial=preferred&&tabs.some(tab=>tab.id===preferred)?preferred:"context";
 const[active,setActive]=useState(initial);
 const[docs,setDocs]=useState<Record<string,string>>({});
 useEffect(()=>{void Promise.all(docTabs.map(async tab=>[tab.id,await readShared(tab.path!)] as const)).then(entries=>setDocs(Object.fromEntries(entries))).catch(()=>setDocs({}))},[]);
 useEffect(()=>{if(preferred&&tabs.some(tab=>tab.id===preferred))setActive(preferred)},[preferred]);
 const tab=tabs.find(item=>item.id===active)!;
 const content=active==="context"?(context||"No contextual inspector data is available for this page."):(docs[active]||"Loading shared documentation…");
 return <div className="help-doc-inspector">
  <div className="help-doc-tabs">{tabs.map(item=><button key={item.id} className={active===item.id?"active":""} onClick={()=>setActive(item.id)}>{item.label}</button>)}</div>
  <div className="inspect-section relationship-guide"><pre className="mini-code relationship-markdown">{content}</pre></div>
  <div className="provenance-foot">{active==="context"?<><span>INSPECTOR SOURCE</span><code>current workspace state</code><span className="verified">✓ live data</span></>:<><span>DOCUMENTATION SOURCE</span><code>shared/{tab.path}</code><span className="verified">✓ filesystem backed</span></>}</div>
 </div>;
}
