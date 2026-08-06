import { Copy, Play } from "lucide-react";

export function CodePanel({ title, language, code, onRun }: { title: string; language: string; code: string; onRun?: () => void }) {
  const copy = () => navigator.clipboard?.writeText(code);
  return <div className="code-panel"><div className="code-panel__header"><div><strong>{title}</strong><span>{language}</span></div><div><button onClick={copy} title="Copy"><Copy size={14}/></button>{onRun && <button onClick={onRun} title="Run"><Play size={14}/></button>}</div></div><pre><code>{code}</code></pre></div>;
}
