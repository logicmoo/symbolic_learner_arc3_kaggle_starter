import {useEffect,useState} from "react";
import "../styles/example_execute.css";

export type ExampleArgument={datatype?:string;label?:string;default?:unknown};
export type ExampleExecute={action:string;arguments?:Record<string,ExampleArgument>};

const initial=(contract:ExampleExecute)=>Object.fromEntries(Object.entries(contract.arguments||{}).map(([name,arg])=>[name,typeof arg.default==="string"?arg.default:JSON.stringify(arg.default??"")]));
const parse=(arg:ExampleArgument,raw:string)=>/text|string|markdown/i.test(arg.datatype||"Text")?raw:raw.trim()?JSON.parse(raw):null;

export function ExampleExecutePanel({contract,onExecute}:{contract:ExampleExecute;onExecute:(args:Record<string,unknown>)=>Promise<unknown>}){
 const[values,setValues]=useState<Record<string,string>>(()=>initial(contract)),[result,setResult]=useState<unknown>(null),[error,setError]=useState<string|null>(null),[running,setRunning]=useState(false);
 useEffect(()=>{setValues(initial(contract));setResult(null);setError(null)},[contract]);
 const run=async()=>{setRunning(true);setError(null);setResult(null);try{const args=Object.fromEntries(Object.entries(contract.arguments||{}).map(([name,arg])=>[name,parse(arg,values[name]||"")]));setResult(await onExecute(args))}catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setRunning(false)}};
 return <section className="example-execute"><div className="llm-subhead"><div><span>EXAMPLE EXECUTE</span><b>{contract.action}</b></div><button className="primary" onClick={()=>void run()} disabled={running}>{running?"Running…":"▶ Run example"}</button></div><div className="example-arguments">{Object.entries(contract.arguments||{}).map(([name,arg])=><label key={name}><span>{arg.label||name} <em>{arg.datatype||"Text"}</em></span><textarea value={values[name]||""} onChange={event=>setValues(current=>({...current,[name]:event.target.value}))}/></label>)}</div>{error&&<div className="demo-notice"><b>Example failed</b><span>{error}</span></div>}{result!==null&&<div className="example-result"><span>RESULT</span><pre>{typeof result==="string"?result:JSON.stringify(result,null,2)}</pre></div>}</section>;
}
