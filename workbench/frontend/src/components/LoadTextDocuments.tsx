import { useEffect, useMemo, useRef, useState } from "react";

type TextDocumentRecord = {
  path: string;
  name: string;
  suffix: string;
  source: string;
  workspaceId: string;
};

type Props = {
  workspaceId: string;
  defaultFilter: string;
  preferredPath: string;
  preferredContent: string;
  savedPreferredContent: string;
  disabled?: boolean;
  onPreferredContentChange: (content: string) => void;
  onSavePreferredContent: () => Promise<void> | void;
  onActiveDocumentChange: (content: string, path: string) => void;
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

function matchesFilter(path: string, filter: string) {
  const terms = filter.split("|").map((term) => term.trim().toLowerCase()).filter(Boolean);
  if (!terms.length) return true;
  const candidate = path.toLowerCase();
  return terms.some((term) => candidate.endsWith(term) || candidate.includes(term));
}

function recordKey(record: TextDocumentRecord) {
  return `${record.workspaceId}:${record.path}`;
}

export function LoadTextDocuments({
  workspaceId,
  defaultFilter,
  preferredPath,
  preferredContent,
  savedPreferredContent,
  disabled = false,
  onPreferredContentChange,
  onSavePreferredContent,
  onActiveDocumentChange,
}: Props) {
  const [documents, setDocuments] = useState<TextDocumentRecord[]>([]);
  const [filter, setFilter] = useState(defaultFilter);
  const [selectedKey, setSelectedKey] = useState("");
  const [content, setContent] = useState(preferredContent);
  const [savedContent, setSavedContent] = useState(savedPreferredContent);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const lineNumberRef = useRef<HTMLPreElement | null>(null);
  const visibleDocuments = useMemo(
    () => documents.filter((record) => matchesFilter(record.path, filter)),
    [documents, filter],
  );
  const selected = documents.find((record) => recordKey(record) === selectedKey);
  const lines = Math.max(1, content.split(/\r?\n/).length);

  const refreshDocuments = async () => {
    const payload = await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/text-documents`);
    const records = Array.isArray(payload.documents) ? payload.documents as TextDocumentRecord[] : [];
    setDocuments(records);
    setSelectedKey((current) => {
      const visible = records.filter((record) => matchesFilter(record.path, filter));
      if (visible.some((record) => recordKey(record) === current)) return current;
      const preferred = visible.find((record) => record.path === preferredPath);
      return preferred ? recordKey(preferred) : visible[0] ? recordKey(visible[0]) : "";
    });
  };

  useEffect(() => {
    setFilter(defaultFilter);
    setSelectedKey("");
    setContent(preferredContent);
    setSavedContent(savedPreferredContent);
    setMessage("");
    void refreshDocuments().catch((reason) => setMessage(reason instanceof Error ? reason.message : String(reason)));
  }, [workspaceId, preferredPath, defaultFilter]);

  useEffect(() => {
    if (!selectedKey) {
      onActiveDocumentChange(preferredContent, preferredPath);
      return;
    }
    const record = documents.find((candidate) => recordKey(candidate) === selectedKey);
    if (!record) return;
    let cancelled = false;
    setBusy(true);
    setMessage("");
    void request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/text-document?path=${encodeURIComponent(record.path)}&sourceWorkspaceId=${encodeURIComponent(record.workspaceId)}`)
      .then((payload) => {
        if (cancelled) return;
        const document = payload.document && typeof payload.document === "object"
          ? payload.document as Record<string, unknown>
          : {};
        const nextContent = String(document.content || "");
        setContent(nextContent);
        setSavedContent(nextContent);
        if (record.path === preferredPath) onPreferredContentChange(nextContent);
        onActiveDocumentChange(nextContent, record.path);
      })
      .catch((reason) => { if (!cancelled) setMessage(reason instanceof Error ? reason.message : String(reason)); })
      .finally(() => { if (!cancelled) setBusy(false); });
    return () => { cancelled = true; };
  }, [workspaceId, selectedKey]);

  useEffect(() => {
    if (selected?.path !== preferredPath) return;
    setContent(preferredContent);
    setSavedContent(savedPreferredContent);
    onActiveDocumentChange(preferredContent, preferredPath);
  }, [preferredContent, savedPreferredContent]);

  useEffect(() => {
    if (!visibleDocuments.length) {
      setSelectedKey("");
      return;
    }
    if (!visibleDocuments.some((record) => recordKey(record) === selectedKey)) {
      const preferred = visibleDocuments.find((record) => record.path === preferredPath);
      setSelectedKey(recordKey(preferred || visibleDocuments[0]));
    }
  }, [filter, documents]);

  const changeContent = (nextContent: string) => {
    setContent(nextContent);
    if (selected?.path === preferredPath) onPreferredContentChange(nextContent);
    onActiveDocumentChange(nextContent, selected?.path || preferredPath);
  };

  const save = async () => {
    if (!selected) return;
    setBusy(true);
    setMessage("");
    try {
      if (selected.path === preferredPath) {
        onPreferredContentChange(content);
        await onSavePreferredContent();
      } else {
        await request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/file`, {
          method: "PUT",
          body: JSON.stringify({ path: selected.path, content }),
        });
      }
      setSavedContent(content);
      setMessage(selected.source === "workspace" ? "Saved." : "Saved as a workspace override.");
      await refreshDocuments();
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  };

  return <>
    <div className="english-workflow-editor-meta">
      <label>
        <span>FILTER</span>
        <input aria-label="English specification document filter" value={filter} disabled={disabled || busy} onChange={(event) => setFilter(event.target.value)} placeholder=".md|.txt" />
      </label>
      <label>
        <span>DOCUMENT</span>
        <select aria-label="English specification text document" value={selectedKey} disabled={disabled || busy || !visibleDocuments.length} onChange={(event) => setSelectedKey(event.target.value)}>
          {!visibleDocuments.length && <option value="">No matching text documents</option>}
          {visibleDocuments.map((record) => <option key={recordKey(record)} value={recordKey(record)}>{record.source} · {record.path}</option>)}
        </select>
      </label>
      <button type="button" disabled={disabled || busy || !selected || content === savedContent} onClick={() => void save()}>Save Document</button>
    </div>
    <div className="english-workflow-editor-meta">
      <code>{selected?.path || preferredPath || "No text document selected"}</code>
      <span>{selected ? `${selected.source} · ${selected.workspaceId}` : `${visibleDocuments.length} matching documents`}</span>
    </div>
    <div className="english-workflow-editor">
      <pre ref={lineNumberRef} aria-hidden="true">{Array.from({ length: lines }, (_, index) => index + 1).join("\n")}</pre>
      <textarea aria-label="English workflow specification" value={content} disabled={!selected || disabled || busy} onChange={(event) => changeContent(event.target.value)} onScroll={(event) => { if (lineNumberRef.current) lineNumberRef.current.scrollTop = event.currentTarget.scrollTop; }} spellCheck />
    </div>
    <div className="english-workflow-editor-meta"><span>Ln {lines}</span><span>{content === savedContent ? "Saved" : "Unsaved changes"}</span>{message && <span>{message}</span>}</div>
  </>;
}
