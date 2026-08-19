import { useEffect, useMemo, useRef, useState } from "react";
import type { WorkflowPageDefinition } from "./WorkflowPageHost";
import { ResourceSourceEditor } from "./ResourceSourceEditor";

type Props = {
  workspaceId: string;
  pageId: string;
  disabled?: boolean;
  liveDefinition?: WorkflowPageDefinition;
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

type SourcePayload = {
  content: string;
  sourceLabel: string;
  modified: number | null;
};

function parseSourcePayload(pageId: string, payload: Record<string, unknown>): SourcePayload {
  const nextContent = String(payload.content || "");
  const record = payload.workflowPage && typeof payload.workflowPage === "object"
    ? payload.workflowPage as Record<string, unknown>
    : {};
  const sourceLabel = `${String(record.source || "effective")} · ${String(record.path || pageId)}`;
  const modifiedRaw = payload.modified;
  return {
    content: nextContent,
    sourceLabel,
    modified: typeof modifiedRaw === "number" && Number.isFinite(modifiedRaw) ? modifiedRaw : null,
  };
}

function formatDiskTimestamp(timestamp: number | null): string {
  if (timestamp === null) return "unknown time";
  return new Date(timestamp * 1000).toLocaleString();
}

export function WorkflowPageSourceEditor({ workspaceId, pageId, disabled = false, liveDefinition, onSaved }: Props) {
  const [content, setContent] = useState("");
  const [savedContent, setSavedContent] = useState("");
  const [savedModified, setSavedModified] = useState<number | null>(null);
  const [diskContent, setDiskContent] = useState("");
  const [diskModified, setDiskModified] = useState<number | null>(null);
  const [source, setSource] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [valid, setValid] = useState(true);
  const lastSynchronizedLiveSource = useRef("");
  const liveSource = liveDefinition ? `${JSON.stringify(liveDefinition, null, 2)}\n` : "";

  const loadSource = async (showMessage = false) => {
    setBusy(true);
    setMessage("");
    try {
      const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/workflow-pages/${encodeURIComponent(pageId)}/source`) as Record<string, unknown>;
      const parsed = parseSourcePayload(pageId, payload);
      setContent(parsed.content);
      setSavedContent(parsed.content);
      setSavedModified(parsed.modified);
      setDiskContent(parsed.content);
      setDiskModified(parsed.modified);
      setSource(parsed.sourceLabel);
      if (showMessage) {
        setMessage(`Reloaded from disk (${formatDiskTimestamp(parsed.modified)}).`);
      }
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      await loadSource(false);
      if (cancelled) return;
    })();
    return () => { cancelled = true; };
  }, [workspaceId, pageId]);

  useEffect(() => {
    let cancelled = false;
    const poll = async () => {
      try {
        const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/workflow-pages/${encodeURIComponent(pageId)}/source`) as Record<string, unknown>;
        if (cancelled) return;
        const parsed = parseSourcePayload(pageId, payload);
        setDiskContent(parsed.content);
        setDiskModified(parsed.modified);
        setSource(parsed.sourceLabel);
      } catch {
        // Keep current editor state; polling failures should not interrupt editing.
      }
    };
    const handle = window.setInterval(() => { void poll(); }, 5000);
    return () => {
      cancelled = true;
      window.clearInterval(handle);
    };
  }, [workspaceId, pageId]);

  useEffect(() => {
    if (!liveSource || liveSource === content) return;
    if (content && content !== savedContent && content !== lastSynchronizedLiveSource.current) return;
    lastSynchronizedLiveSource.current = liveSource;
    setContent(liveSource);
    if (savedContent && liveSource !== savedContent) {
      setMessage("Live page components synchronized. Validate and Apply to persist this layout.");
    }
  }, [liveSource]);

  const diskChanged = useMemo(() => {
    if (!diskContent && !savedContent) return false;
    if (diskContent !== savedContent) return true;
    if (diskModified === null || savedModified === null) return false;
    return Math.abs(diskModified - savedModified) > 0.0001;
  }, [diskContent, diskModified, savedContent, savedModified]);

  const dirty = content !== savedContent;

  const save = async () => {
    setBusy(true);
    setMessage("");
    try {
      const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/workflow-pages/${encodeURIComponent(pageId)}/source`, {
        method: "PUT",
        body: JSON.stringify({ content }),
      }) as Record<string, unknown>;
      const parsed = parseSourcePayload(pageId, payload);
      setContent(parsed.content);
      setSavedContent(parsed.content);
      setSavedModified(parsed.modified);
      setDiskContent(parsed.content);
      setDiskModified(parsed.modified);
      setSource(parsed.sourceLabel);
      setMessage(payload.createdOverride ? `Workspace override created and applied live (${formatDiskTimestamp(parsed.modified)}).` : `Page specification applied live (${formatDiskTimestamp(parsed.modified)}).`);
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
      <button type="button" disabled={disabled || busy || !diskChanged} onClick={() => void loadSource(true)}>
        {diskChanged ? `Reload changes (${formatDiskTimestamp(diskModified)})` : "Reload"}
      </button>
      <button type="button" disabled={disabled || busy || !valid || (!dirty && !diskChanged)} onClick={() => void save()}>
        {diskChanged && !dirty ? "Validate and Apply (overwrite disk changes)" : "Validate and Apply"}
      </button>
    </div>
    <ResourceSourceEditor
      value={content}
      onChange={setContent}
      onValidityChange={setValid}
      className="workflow-page-source-editor"
      label="Current page specification (MeTTa/JSON)"
      showEnablement={false}
      disabled={disabled || busy}
    />
    <div className="english-workflow-editor-meta">
      <span>{dirty ? "Unsaved changes" : "Saved"}</span>
      <span>{diskChanged ? `Disk changed at ${formatDiskTimestamp(diskModified)}` : `Disk synced at ${formatDiskTimestamp(diskModified)}`}</span>
      {message && <span>{message}</span>}
    </div>
  </>;
}
