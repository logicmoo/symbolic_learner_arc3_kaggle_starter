import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ThreeStateAccordionMember, type AccordionDisplayMode } from "./ThreeStateAccordion";
import { MermaidDiagram } from "./MermaidDiagram";

type TodoPayload = { markdown: string; specificationPath: string; mockupAvailable: boolean; mockups?: Array<{view:string;description:string;available:boolean;url:string}> };

export function WorkflowRunnerTodoReference({
  displayMode,
  onDisplayModeChange,
}: {
  displayMode: AccordionDisplayMode;
  onDisplayModeChange: (mode: AccordionDisplayMode) => void;
}) {
  const [todo, setTodo] = useState<TodoPayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    void fetch("/api/workflow-runner/todo")
      .then(async response => {
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || payload.detail || response.statusText);
        setTodo(payload as TodoPayload);
      })
      .catch(reason => setError(String(reason)));
  }, []);

  return <ThreeStateAccordionMember stackId="center-stack" initialIndex={7} label="RUNNER DESIGN REFERENCE" value="Mockups and TODO" detail="REFERENCE" mode={displayMode} onChange={onDisplayModeChange} baseClass="workflow-runner-reference" scrollSize="320px" footer={<><b>REFERENCE</b><span>{todo?.specificationPath || "Workflow runner design specification"}</span></>}>
    {error && <div className="demo-notice"><b>Reference unavailable</b><span>{error}</span></div>}
    {todo && <div className="workflow-runner-reference-body">
      <div className="workflow-runner-mockups">{(todo.mockups||[]).filter(item=>item.available).map(item=><figure key={item.view}><figcaption><b>{item.view}</b><span>{item.description}</span></figcaption><a className="workflow-runner-mockup" href={item.url} target="_blank" rel="noreferrer"><img src={item.url} alt={`${item.view} workflow runner design reference`} /></a></figure>)}</div>
      <article className="markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]} components={{
        pre: ({ node: _node, children, ...props }) => {
          const child = Array.isArray(children) ? children[0] : children;
          const codeProps = (child as { props?: { className?: string; children?: unknown } } | null)?.props;
          const isMermaid = /(?:^|\s)language-mermaid(?:\s|$)/.test(codeProps?.className || "");
          if (isMermaid) {
            const codeChildren = codeProps?.children;
            const code = Array.isArray(codeChildren) ? codeChildren.join("") : String(codeChildren ?? "");
            return <MermaidDiagram code={code} />;
          }
          return <pre {...props}>{children}</pre>;
        },
      }}>{todo.markdown}</ReactMarkdown><small>{todo.specificationPath}</small></article>
    </div>}
  </ThreeStateAccordionMember>;
}
