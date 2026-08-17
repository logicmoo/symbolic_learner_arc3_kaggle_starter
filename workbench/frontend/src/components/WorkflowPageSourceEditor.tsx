import { useEffect, useRef, useState } from "react";

type Props = {
  workspaceId: string;
  pageId: string;
  disabled?: boolean;
  onSaved: () => Promise<unknown> | unknown;
};

async function request(path: string, init?: RequestInit) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) as Record<string, unknown> : {};
  if (!response.ok) throw new Error(String(payload.detail || response.statusText));
  return payload;
}

export function WorkflowPageSourceEditor({ workspaceId, pageId, disabled = false, onSaved }: Props) {
  const [content, setContent] = useState("");
  const [savedContent, setSavedContent] = useState("");
  const [source, setSource] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const lineNumberRef = useRef<HTMLPreElement | null>(null);
  const lines = Math.max(1, content.split(/\r?\n/).length);

  useEffect(() => {
    let cancelled = false;
    setBusy(true);
    setMessage("");
    void request(`/api/workspaces/${encodeURIComponent(workspaceId)}/workflow-pages/${encodeURIComponent(pageId)}/source`)
      .then((payload) => {
        if (cancelled) return;
        const nextContent = String(payload.content || "");
        const record = payload.workflowPage && typeof payload.workflowPage === "object"
          ? payload.workflowPage as Record<string, unknown>
          : {};
        setContent(nextContent);
        setSavedContent(nextContent);
        setSource(`${String(record.source || "effective")} · ${String(record.path || pageId)}`);
      })
      .catch((reason) => { if (!cancelled) setMessage(reason instanceof Error ? reason.message : String(reason)); })
      .finally(() => { if (!cancelled) setBusy(false); });
    return () => { cancelled = true; };
  }, [workspaceId, pageId]);

  const save = async () => {
    setBusy(true);
    setMessage("");
    try {
      const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/workflow-pages/${encodeURIComponent(pageId)}/source`, {
        method: "PUT",
        body: JSON.stringify({ content }),
      });
      const nextContent = String(payload.content || content);
      const record = payload.workflowPage && typeof payload.workflowPage === "object"
        ? payload.workflowPage as Record<string, unknown>
        : {};
      setContent(nextContent);
      setSavedContent(nextContent);
      setSource(`${String(record.source || "workspace")} · ${String(record.path || pageId)}`);
      setMessage(payload.createdOverride ? "Workspace override created and applied live." : "Page specification applied live.");
      await onSaved();
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  };

  return <>
    <div className="english-workflow-editor-meta">
      <code>{source || pageId}</code>
      <button type="button" disabled={disabled || busy || content === savedContent} onClick={() => void save()}>Validate and Apply</button>
    </div>
    <div className="english-workflow-editor">
      <pre ref={lineNumberRef} aria-hidden="true">{Array.from({ length: lines }, (_, index) => index + 1).join("\n")}</pre>
      <textarea aria-label="Current page specification" value={content} disabled={disabled || busy} onChange={(event) => setContent(event.target.value)} onScroll={(event) => { if (lineNumberRef.current) lineNumberRef.current.scrollTop = event.currentTarget.scrollTop; }} spellCheck={false} />
    </div>
    <div className="english-workflow-editor-meta"><span>Ln {lines}</span><span>{content === savedContent ? "Saved" : "Unsaved changes"}</span>{message && <span>{message}</span>}</div>
  </>;
}
