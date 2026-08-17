import {useEffect,useState} from "react";
import {OperationLibraryEditor} from "./OperationLibraryEditor";
import {PromptLibraryEditor} from "./PromptLibraryEditor";

type SourceTab="prompts"|"prolog"|"metta"|"python";
const tabs:Array<{id:SourceTab;label:string;description:string}>=[
 {id:"prompts",label:"Prompts",description:"LLM instructions maintained as reusable implementation source."},
 {id:"prolog",label:"Prolog",description:"Predicates and embedded SWI-Prolog source bound to Operations."},
 {id:"metta",label:"MeTTa",description:"MeTTa expressions and source-backed Operation implementations."},
 {id:"python",label:"Python",description:"Python modules, callables, and their Operation bindings."},
];

const sourceTabFromLocation=():SourceTab=>{
 const requested=new URLSearchParams(window.location.search).get("sourceLanguage");
 return tabs.some(item=>item.id===requested)?requested as SourceTab:"prompts";
};

export function SourceCodeEditor({workspaceId}:{workspaceId:string}){
 const[tab,setTab]=useState<SourceTab>(sourceTabFromLocation);
 useEffect(()=>{const restore=()=>setTab(sourceTabFromLocation());window.addEventListener("popstate",restore);return()=>window.removeEventListener("popstate",restore)},[]);
 const selectTab=(next:SourceTab)=>{setTab(next);const url=new URL(window.location.href);if(next==="prompts")url.searchParams.delete("sourceLanguage");else url.searchParams.set("sourceLanguage",next);window.history.pushState({},"",url)};
 return <section className="source-code-library">
  <div className="source-code-tabs" role="tablist" aria-label="Source code languages">{tabs.map(item=><button role="tab" aria-selected={tab===item.id} className={tab===item.id?"active":""} key={item.id} onClick={()=>selectTab(item.id)}><b>{item.label}</b><small>{item.description}</small></button>)}</div>
  {tab==="prompts"?<PromptLibraryEditor workspaceId={workspaceId}/>:<OperationLibraryEditor workspaceId={workspaceId} sourceLanguage={tab}/>}
 </section>;
}
