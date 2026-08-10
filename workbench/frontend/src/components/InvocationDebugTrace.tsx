import {useEffect,useMemo,useState} from "react";
import {jsonValueToMetta} from "../lib/mettaResourceCodec";
import "../styles/invocation_debug_trace.css";

type TraceTab={id:string;label:string;content:string;language:"metta"|"json"|"text"};

const blockField=/^(?:stdout|stderr|stdOut|stdErr|body|bodyText|requestBody|responseBody|source|sourceCode|generatedSource|prompt|raw|content)$/i;
const tabLabel=(path:string)=>path.split(".").map(part=>part.replace(/([a-z])([A-Z])/g,"$1 $2")).join(" · ");
const formattedBlock=(content:string):Pick<TraceTab,"content"|"language">=>{const trimmed=content.trim();if(trimmed.startsWith("{")||trimmed.startsWith("["))try{return{content:JSON.stringify(JSON.parse(trimmed),null,2),language:"json"}}catch{/* Preserve non-JSON block text. */}return{content,language:"text"}};

function collectStringBlocks(value:unknown,path:string[]=[]):TraceTab[]{
 if(Array.isArray(value))return value.flatMap((item,index)=>collectStringBlocks(item,[...path,String(index)]));
 if(!value||typeof value!=="object")return[];
 return Object.entries(value as Record<string,unknown>).flatMap(([key,child])=>{
  const next=[...path,key];
  if(typeof child==="string"&&(child.includes("\n")||child.length>=160||blockField.test(key))){const id=next.join(".");return[{id:`field:${id}`,label:tabLabel(id),...formattedBlock(child)}]}
  return collectStringBlocks(child,next);
 });
}

export function debugTraceTabs(content:string):TraceTab[]{
 try{
  const parsed=JSON.parse(content);
  const json=JSON.stringify(parsed,null,2);
  const fieldTabs=collectStringBlocks(parsed);
  const unique=[...new Map(fieldTabs.map(tab=>[tab.id,tab])).values()];
  return[{id:"metta",label:"MeTTa",content:jsonValueToMetta(parsed),language:"metta"},{id:"json",label:"JSON",content:json,language:"json"},...unique];
 }catch{return[{id:"raw",label:"Raw trace",content,language:"text"}]}
}

export function InvocationDebugTrace({path,content}:{path:string;content:string}){
 const tabs=useMemo(()=>debugTraceTabs(content),[content]);
 const[active,setActive]=useState(tabs[0]?.id||"raw");
 useEffect(()=>setActive(tabs[0]?.id||"raw"),[content]);
 const selected=tabs.find(tab=>tab.id===active)||tabs[0];
 return <details className="operation-debug-trace invocation-debug-trace" open>
  <summary><span>COMPLETE DEBUG TRACE</span><code>{path}</code></summary>
  <nav aria-label="Debug trace views">{tabs.map(tab=><button type="button" className={tab.id===selected?.id?"active":""} aria-pressed={tab.id===selected?.id} key={tab.id} onClick={()=>setActive(tab.id)}>{tab.label}</button>)}</nav>
  {selected&&<pre data-language={selected.language}>{selected.content}</pre>}
 </details>;
}
