import {useEffect,useState} from "react";
import "../styles/example_execute.css";

export type ExampleArgument={datatype?:string;label?:string;default?:unknown;options?:unknown[]};
export type ExampleExecute={action:string;arguments?:Record<string,ExampleArgument>};

const optionValue=(option:unknown)=>typeof option==="string"?option:JSON.stringify(option);
const initial=(contract:ExampleExecute)=>Object.fromEntries(Object.entries(contract.arguments||{}).map(([name,arg])=>[name,optionValue(arg.default??"")]));
const parse=(arg:ExampleArgument,raw:string)=>{
 if(arg.options?.length){const match=arg.options.find(option=>optionValue(option)===raw);if(match!==undefined)return match}
 return /text|string|markdown/i.test(arg.datatype||"Text")?raw:raw.trim()?JSON.parse(raw):null;
};
const inputKind=(arg:ExampleArgument)=>{const datatype=String(arg.datatype||"Text");if(arg.options?.length)return"choice";if(/bool/i.test(datatype))return"boolean";if(/int|float|double|decimal|number/i.test(datatype))return"number";if(/text|string|markdown/i.test(datatype))return"text";return"structured"};

export function ExampleExecutePanel({contract,onExecute}:{contract:ExampleExecute;onExecute:(args:Record<string,unknown>)=>Promise<unknown>}){
 const[values,setValues]=useState<Record<string,string>>(()=>initial(contract)),[result,setResult]=useState<unknown>(null),[error,setError]=useState<string|null>(null),[running,setRunning]=useState(false);
 useEffect(()=>{setValues(initial(contract));setResult(null);setError(null)},[contract]);
 const run=async()=>{setRunning(true);setError(null);setResult(null);try{const args=Object.fromEntries(Object.entries(contract.arguments||{}).map(([name,arg])=>[name,parse(arg,values[name]||"")]));setResult(await onExecute(args))}catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setRunning(false)}};
 const change=(name:string,value:string)=>setValues(current=>({...current,[name]:value}));
 return <section className="example-execute"><div className="llm-subhead"><div><span>EXAMPLE EXECUTE</span><b>{contract.action}</b></div><button className="primary" onClick={()=>void run()} disabled={running}>{running?"Running…":"▶ Run example"}</button></div><div className="example-arguments">{Object.entries(contract.arguments||{}).map(([name,arg])=>{const kind=inputKind(arg),value=values[name]||"";return <label key={name} className={`example-argument-${kind}`}><span>{arg.label||name} <em>{arg.datatype||"Text"}</em></span>{kind==="boolean"?<input type="checkbox" checked={value==="true"} onChange={event=>change(name,String(event.target.checked))}/>:kind==="number"?<input type="number" value={value} onChange={event=>change(name,event.target.value)}/>:kind==="choice"?<select value={value} onChange={event=>change(name,event.target.value)}>{arg.options!.map(option=><option key={optionValue(option)} value={optionValue(option)}>{String(option)}</option>)}</select>:<textarea value={value} rows={kind==="structured"?6:3} onChange={event=>change(name,event.target.value)}/>}</label>})}</div>{error&&<div className="demo-notice"><b>Example failed</b><span>{error}</span></div>}{result!==null&&<div className="example-result"><span>RESULT</span><pre>{typeof result==="string"?result:JSON.stringify(result,null,2)}</pre></div>}</section>;
}
