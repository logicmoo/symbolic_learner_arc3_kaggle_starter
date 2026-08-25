import { useEffect, useMemo, useRef, useState } from "react";

export type WorkspaceResourceLocation = {
  workspaceId: string;
  path: string;
};

type WorkspaceChoice = {
  id: string;
  label?: string;
  workspaceType?: "project" | "library";
  effectiveIncludes?: string[];
};

export type WorkspaceResourceFileControlsProps = {
  currentWorkspaceId: string;
  workspaceId: string;
  originWorkspaceId?: string;
  relativePath: string;
  dirty?: boolean;
  disabled?: boolean;
  allowLoadDifferent?: boolean;
  onSave: (location: WorkspaceResourceLocation) => Promise<void> | void;
  onLoad: (location: WorkspaceResourceLocation) => Promise<void> | void;
  content: string;
  onClientContent: (content: string, name: string) => void;
};

type WritableFile = { write: (content: string) => Promise<void>; close: () => Promise<void> };
type LocalFileHandle = { name: string; getFile: () => Promise<File>; createWritable: () => Promise<WritableFile> };
type FilePickerWindow = Window & {
  showOpenFilePicker?: (options?: Record<string, unknown>) => Promise<LocalFileHandle[]>;
  showSaveFilePicker?: (options?: Record<string, unknown>) => Promise<LocalFileHandle>;
};

async function workspaceChoices(): Promise<WorkspaceChoice[]> {
  const response = await fetch("/api/workspaces", { cache: "no-store" });
  const text = await response.text();
  const payload = JSON.parse(text || "{}");
  if (!response.ok) throw new Error(payload.error || payload.detail || response.statusText);
  return Array.isArray(payload.workspaces) ? payload.workspaces : [];
}

export function WorkspaceResourceFileControls({
  currentWorkspaceId,
  workspaceId,
  originWorkspaceId,
  relativePath,
  dirty = false,
  disabled = false,
  allowLoadDifferent = true,
  onSave,
  onLoad,
  content,
  onClientContent,
}: WorkspaceResourceFileControlsProps) {
  const [workspaces, setWorkspaces] = useState<WorkspaceChoice[]>([]);
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState(workspaceId || currentWorkspaceId);
  const [selectedPath, setSelectedPath] = useState(relativePath);
  const [mode, setMode] = useState<"saveAs" | "loadFrom" | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [localFileHandle, setLocalFileHandle] = useState<LocalFileHandle | null>(null);
  const uploadRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    void workspaceChoices().then(setWorkspaces).catch(reason => setError(String(reason)));
  }, []);
  useEffect(() => {
    setSelectedWorkspaceId(workspaceId || currentWorkspaceId);
    setSelectedPath(relativePath);
    setMode(null);
  }, [currentWorkspaceId, workspaceId, relativePath]);

  const ordered = useMemo(() => {
    const byId = new Map(workspaces.map(item => [item.id, item]));
    const current = byId.get(currentWorkspaceId);
    const inheritedIds = (current?.effectiveIncludes || []).filter(id => id !== currentWorkspaceId && byId.has(id));
    const used = new Set([currentWorkspaceId, ...inheritedIds]);
    const inherited = inheritedIds.map(id => byId.get(id)!).filter(Boolean);
    const libraries = workspaces.filter(item => !used.has(item.id) && item.workspaceType === "library")
      .sort((a, b) => (a.label || a.id).localeCompare(b.label || b.id));
    const projects = workspaces.filter(item => !used.has(item.id) && item.workspaceType !== "library")
      .sort((a, b) => (a.label || a.id).localeCompare(b.label || b.id));
    return { current, inherited, libraries, projects };
  }, [currentWorkspaceId, workspaces]);

  const run = async (action: () => Promise<void> | void) => {
    setBusy(true);
    setError("");
    try { await action(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setBusy(false); }
  };
  const currentLocation = { workspaceId: workspaceId || currentWorkspaceId, path: relativePath };
  const originLocation = { workspaceId: originWorkspaceId || workspaceId || currentWorkspaceId, path: relativePath };
  const selectedLocation = { workspaceId: selectedWorkspaceId, path: selectedPath.trim() };
  const confirmMode = () => {
    if (!selectedLocation.path) { setError("A workspace-relative file path is required."); return; }
    void run(async () => {
      if (mode === "saveAs") await onSave(selectedLocation);
      else await onLoad(selectedLocation);
      setMode(null);
    });
  };
  const nativePicker = window as FilePickerWindow;
  const loadLocalFile = () => void run(async () => {
    if (!nativePicker.showOpenFilePicker) throw new Error("Native local-file access is unavailable in this browser; use Upload instead.");
    const [handle] = await nativePicker.showOpenFilePicker({ multiple: false, types: [{ description: "Resource source", accept: { "text/plain": [".json", ".metta", ".txt"] } }] });
    if (!handle) return;
    const file = await handle.getFile();
    setLocalFileHandle(handle);
    onClientContent(await file.text(), file.name);
  });
  const saveLocalFile = (saveAs: boolean) => void run(async () => {
    let handle = saveAs ? null : localFileHandle;
    if (!handle) {
      if (!nativePicker.showSaveFilePicker) throw new Error("Native local-file saving is unavailable in this browser; use Download instead.");
      handle = await nativePicker.showSaveFilePicker({ suggestedName: localFileHandle?.name || relativePath.split("/").at(-1) || "resource.json", types: [{ description: "Resource source", accept: { "text/plain": [".json", ".metta", ".txt"] } }] });
    }
    const writable = await handle.createWritable();
    await writable.write(content);
    await writable.close();
    setLocalFileHandle(handle);
  });
  const reloadLocalFile = () => void run(async () => {
    if (!localFileHandle) throw new Error("Load or Save As a local file before reloading it.");
    const file = await localFileHandle.getFile();
    onClientContent(await file.text(), file.name);
  });
  const uploadClientFile = (file: File | undefined) => void run(async () => {
    if (!file) return;
    onClientContent(await file.text(), file.name);
    if (uploadRef.current) uploadRef.current.value = "";
  });
  const downloadClientFile = () => {
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = relativePath.split("/").at(-1) || "resource.json";
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return <div className="workspace-resource-file-controls" data-resource-file-controls="shared">
    <div className="workspace-resource-file-channel"><span>WORKSPACE RESOURCE</span><div className="workspace-resource-file-actions">
      <button type="button" className={dirty ? "primary" : ""} disabled={disabled || busy || !currentLocation.path} onClick={() => void run(() => onSave(currentLocation))}>Save To Workspace</button>
      <button type="button" disabled={disabled || busy} onClick={() => setMode(mode === "saveAs" ? null : "saveAs")}>Save To Other Workspace…</button>
      <button type="button" disabled={disabled || busy || !originLocation.path} onClick={() => void run(() => onLoad(originLocation))}>Reload From Origin</button>
      {allowLoadDifferent && <button type="button" disabled={disabled || busy} onClick={() => setMode(mode === "loadFrom" ? null : "loadFrom")}>Load From Workspace…</button>}
    </div></div>
    <div className="workspace-resource-file-channel"><span>LOCAL DISK · NATIVE FILE</span><div className="workspace-resource-file-actions">
      {allowLoadDifferent && <button type="button" disabled={disabled || busy} onClick={loadLocalFile}>Load…</button>}
      <button type="button" disabled={disabled || busy || !localFileHandle} onClick={() => saveLocalFile(false)}>Save</button>
      <button type="button" disabled={disabled || busy} onClick={() => saveLocalFile(true)}>Save As…</button>
      <button type="button" disabled={disabled || busy || !localFileHandle} onClick={reloadLocalFile}>Reload Local File</button>
      <small>{localFileHandle?.name || "No local file handle"}</small>
    </div></div>
    <div className="workspace-resource-file-channel"><span>CLIENT TRANSFER</span><div className="workspace-resource-file-actions">
      {allowLoadDifferent && <label className="resource-client-upload">Upload<input ref={uploadRef} type="file" accept=".json,.metta,.txt,text/plain,application/json" disabled={disabled || busy} onChange={event => uploadClientFile(event.target.files?.[0])}/></label>}
      <button type="button" disabled={disabled || busy} onClick={downloadClientFile}>Download</button>
    </div>
    {mode && <div className="workspace-resource-file-picker">
      <label><span>WORKSPACE</span><select aria-label="Resource workspace" value={selectedWorkspaceId} disabled={busy} onChange={event => setSelectedWorkspaceId(event.target.value)}>
        {ordered.current && <option value={ordered.current.id}>{ordered.current.label || ordered.current.id} (current)</option>}
        {ordered.inherited.length > 0 && <optgroup label="Inherited workspaces">{ordered.inherited.map(item => <option key={item.id} value={item.id}>{item.label || item.id} (inherited)</option>)}</optgroup>}
        {(ordered.libraries.length > 0 || ordered.projects.length > 0) && <option disabled>──────── Other locations ────────</option>}
        {ordered.libraries.length > 0 && <optgroup label="Other libraries">{ordered.libraries.map(item => <option key={item.id} value={item.id}>{item.label || item.id}</option>)}</optgroup>}
        {ordered.projects.length > 0 && <optgroup label="Other workspaces">{ordered.projects.map(item => <option key={item.id} value={item.id}>{item.label || item.id}</option>)}</optgroup>}
        {!workspaces.some(item => item.id === selectedWorkspaceId) && <option value={selectedWorkspaceId}>{selectedWorkspaceId}</option>}
      </select></label>
      <label className="workspace-resource-path"><span>WORKSPACE-RELATIVE FILE</span><input aria-label="Workspace-relative file path" value={selectedPath} onChange={event => setSelectedPath(event.target.value)} placeholder="design/resources/example.json" /></label>
      <button type="button" className="primary" disabled={busy || !selectedPath.trim()} onClick={confirmMode}>{mode === "saveAs" ? "Save Here" : "Load File"}</button>
      <button type="button" disabled={busy} onClick={() => setMode(null)}>Cancel</button>
    </div>}
    </div>{error && <div className="validation bad">{error}</div>}
  </div>;
}
