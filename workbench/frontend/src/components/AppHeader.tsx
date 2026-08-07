import { BrainCircuit, Play, RotateCcw, Server, Settings } from "lucide-react";

interface Props { projectName: string; operationName: string; level: number; step: number; onRun: () => void; onReset: () => void; }

export function AppHeader({ projectName, operationName, level, step, onRun, onReset }: Props) {
  return <header className="app-header">
    <div className="brand"><div className="brand-mark"><BrainCircuit size={25} /></div><div><strong>{projectName}</strong><span>ARC3 symbolic workflow debugger</span></div></div>
    <div className="operation-context"><span className="context-chip"><b>Game</b>{operationName}</span><span className="context-chip"><b>Level</b>{level}</span><span className="context-chip"><b>Step</b>{step}</span><span className="context-chip context-chip--online"><Server size={14}/> connected</span></div>
    <div className="header-actions"><button className="button button--primary" onClick={onRun}><Play size={16}/> Run stage</button><button className="icon-button" onClick={onReset} title="Reset"><RotateCcw size={17}/></button><button className="icon-button" title="Settings"><Settings size={17}/></button></div>
  </header>;
}
