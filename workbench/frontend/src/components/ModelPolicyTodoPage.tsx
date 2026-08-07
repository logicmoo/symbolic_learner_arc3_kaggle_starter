import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "../styles/help_tabs.css";
import "../styles/model_policy_todo.css";

type TodoPayload = { status: "pending"; specificationPath: string; mockupPath: string; mockupAvailable: boolean; markdown: string };

export function ModelPolicyTodoPage() {
  const [payload, setPayload] = useState<TodoPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { fetch("/api/model-policy/todo").then(async response => { const body = await response.json(); if (!response.ok) throw new Error(body.error || body.detail || response.statusText); setPayload(body); }).catch(reason => setError(String(reason))); }, []);
  return <section className="resource-view model-policy-todo-page">
    <div className="resource-heading"><div><span>SYSTEM · IMPLEMENTATION PENDING</span><h1>Model Runtime Usage and Benchmarking Policies</h1><p>The checked-in specification and visual reference are read directly from the repository. No policy records are fabricated on this page.</p></div></div>
    {error && <div className="backend-error"><b>Model Policy specification unavailable</b><span>{error}</span></div>}
    {!payload && !error && <div className="studio-empty">Loading filesystem policy specification…</div>}
    {payload && <div className="model-policy-todo-layout"><article className="relationship-markdown markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{payload.markdown}</ReactMarkdown></article><aside className="model-policy-reference"><span>VISUAL ACCEPTANCE REFERENCE</span><b>{payload.mockupPath}</b>{payload.mockupAvailable ? <img src="/api/model-policy/todo/mockup" alt="Model runtime policy design mockup" /> : <p>The checked-in mockup is missing.</p>}<small>{payload.specificationPath}</small></aside></div>}
  </section>;
}
