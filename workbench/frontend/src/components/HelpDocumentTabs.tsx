import {useEffect,useState} from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "../styles/help_tabs.css";

type HelpTab={id:string;label:string;path?:string};

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
 const text=await response.text();
 let payload:any;
 try{payload=JSON.parse(text)}catch{throw new Error(text||response.statusText)}
 if(!response.ok)throw new Error(payload.error||payload.detail||response.statusText);
 return String(payload.file?.content||"");
}

export function HelpDocumentTabs({preferred,context}:{preferred?:string;context?:string}){
 const tabs:HelpTab[]=[{id:"context",label:"Context"},...docTabs];
 const initial=preferred&&tabs.some(tab=>tab.id===preferred)?preferred:"context";
 const[active,setActive]=useState(initial);
 const[docs,setDocs]=useState<Record<string,string>>({});
 const[errors,setErrors]=useState<Record<string,string>>({});
 useEffect(()=>{
  let cancelled=false;
  setDocs({});setErrors({});
  for(const tab of docTabs){
   void readShared(tab.path!).then(content=>{if(!cancelled)setDocs(current=>({...current,[tab.id]:content}))}).catch(reason=>{if(!cancelled)setErrors(current=>({...current,[tab.id]:reason instanceof Error?reason.message:String(reason)}))});
  }
  return()=>{cancelled=true};
 },[]);
 useEffect(()=>{if(preferred&&tabs.some(tab=>tab.id===preferred))setActive(preferred)},[preferred]);
 const tab=tabs.find(item=>item.id===active)!;
 const content=active==="context"?(context?`\`\`\`json\n${context}\n\`\`\``:"No contextual inspector data is available for this page."):errors[active]?`> **Documentation failed to load:** ${errors[active]}`:(docs[active]||"Loading shared documentation…");
 return <div className="help-doc-inspector">
  <div className="help-doc-tabs">{tabs.map(item=><button key={item.id} className={active===item.id?"active":""} onClick={()=>setActive(item.id)}>{item.label}</button>)}</div>
  <div className="inspect-section relationship-guide"><article className="relationship-markdown markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]} components={{a:({node:_node,...props})=><a {...props} target="_blank" rel="noreferrer"/>}}>{content}</ReactMarkdown></article></div>
  <div className="provenance-foot">{active==="context"?<><span>INSPECTOR SOURCE</span><code>current workspace state</code><span className="verified">✓ live data</span></>:<><span>DOCUMENTATION SOURCE</span><code>shared/{tab.path}</code><span className={errors[active]?"":"verified"}>{errors[active]?"load error":"✓ filesystem backed"}</span></>}</div>
 </div>;
}
