import {useEffect,useState} from "react";

type HelpTab={id:string;label:string;path:string};

const tabs:HelpTab[]=[
 {id:"overview",label:"Overview",path:"docs/models_profiles_tasks_prompts.md"},
 {id:"llms",label:"LLMs",path:"docs/llm_catalog.md"},
 {id:"tasks",label:"Tasks",path:"docs/tasks.md"},
 {id:"prompts",label:"Prompts",path:"docs/prompts.md"},
];

async function readShared(path:string){const response=await fetch(`/api/workspaces/shared/file?path=${encodeURIComponent(path)}`);const payload=await response.json();if(!response.ok)throw new Error(payload.detail||response.statusText);return String(payload.file?.content||"");}

export function HelpDocumentTabs({preferred}:{preferred?:string}){
 const[active,setActive]=useState(preferred&&tabs.some(tab=>tab.id===preferred)?preferred:"overview");
 const[docs,setDocs]=useState<Record<string,string>>({});
 useEffect(()=>{void Promise.all(tabs.map(async tab=>[tab.id,await readShared(tab.path)] as const)).then(entries=>setDocs(Object.fromEntries(entries))).catch(()=>setDocs({}))},[]);
 useEffect(()=>{if(preferred&&tabs.some(tab=>tab.id===preferred))setActive(preferred)},[preferred]);
 const tab=tabs.find(item=>item.id===active)!;
 return <div className="help-doc-inspector"><div className="help-doc-tabs">{tabs.map(item=><button key={item.id} className={active===item.id?"active":""} onClick={()=>setActive(item.id)}>{item.label}</button>)}</div><div className="inspect-section relationship-guide"><pre className="mini-code relationship-markdown">{docs[active]||"Loading shared documentation…"}</pre></div><div className="provenance-foot"><span>DOCUMENTATION SOURCE</span><code>shared/{tab.path}</code><span className="verified">✓ filesystem backed</span></div></div>;
}
