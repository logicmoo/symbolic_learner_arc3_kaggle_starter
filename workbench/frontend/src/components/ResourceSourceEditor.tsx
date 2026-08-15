import { useEffect, useRef, useState } from "react";
import type { CSSProperties } from "react";
import { jsonDocumentToMetta, mettaDocumentToJson } from "../lib/mettaResourceCodec";
import "../styles/operation_editor.css";

type Props = { value: string; onChange: (json: string) => void; onValidityChange?: (valid: boolean) => void; className?: string; style?: CSSProperties; label?: string; showEnablement?: boolean };

export function ResourceSourceEditor({ value, onChange, onValidityChange, className = "", style, label = "Edit this resource directly", showEnablement = true }: Props) {
  const [format, setFormat] = useState<"metta" | "json">("metta");
  const [metta, setMetta] = useState("");
  const [jsonDraft, setJsonDraft] = useState(value);
  const [error, setError] = useState("");
  const emittedJson = useRef<string | null>(null);

  useEffect(() => {
    if (value === emittedJson.current) { emittedJson.current = null; setJsonDraft(value); return; }
    setJsonDraft(value);
    if (!value) { setMetta(""); setError(""); onValidityChange?.(true); return; }
    try { setMetta(jsonDocumentToMetta(value)); setError(""); onValidityChange?.(true); }
    catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); onValidityChange?.(false); }
  }, [value]);

  const editMetta = (next: string) => {
    setMetta(next);
    try { const json = mettaDocumentToJson(next); setJsonDraft(json); emittedJson.current = json; onChange(json); setError(""); onValidityChange?.(true); }
    catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); onValidityChange?.(false); }
  };
  const editJson = (next: string) => {
    setJsonDraft(next);
    try {
      const parsed = JSON.parse(next);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error("A resource document must be a JSON object");
      setMetta(jsonDocumentToMetta(next)); emittedJson.current = next; onChange(next); setError(""); onValidityChange?.(true);
    } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); onValidityChange?.(false); }
  };
  let resource: Record<string, unknown> | null = null;
  try { const parsed = JSON.parse(value); if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) resource = parsed; } catch { /* Invalid source remains editable. */ }
  const resourceEnabled = resource?.enabled !== false;
  const setEnabled = (enabled: boolean) => { if (resource) onChange(JSON.stringify({ ...resource, enabled }, null, 2)); };

  return <div className="operation-json-block resource-source-editor">
    <div className="llm-subhead"><div><span>RESOURCE SOURCE</span><b>{label}</b></div><div className="source-format-tabs">{showEnablement&&resource&&<button className={`resource-enable-action ${resourceEnabled?"disable-resource":"enable-resource"}`} onClick={()=>setEnabled(!resourceEnabled)}>{resourceEnabled?"Disable Resource":"Enable Resource"}</button>}<button className={format === "metta" ? "active" : ""} onClick={() => setFormat("metta")}>MeTTa</button><button className={format === "json" ? "active" : ""} onClick={() => setFormat("json")}>JSON</button></div></div>
    <textarea className={`raw-json-editor operation-visible-editor ${className}`.trim()} style={style} value={format === "metta" ? metta : jsonDraft} aria-invalid={Boolean(error)} onChange={event => format === "metta" ? editMetta(event.target.value) : editJson(event.target.value)} />
    {error && <div className="validation bad">Invalid {format === "metta" ? "MeTTa" : "JSON"} syntax: {error}. Draft preserved; synchronization and saving are paused until this is fixed.</div>}
  </div>;
}
