import { useEffect, useRef, useState } from "react";
import type { CSSProperties } from "react";
import { jsonDocumentToMetta, mettaDocumentToJson } from "../lib/mettaResourceCodec";
import "../styles/operation_editor.css";

type Props = { value: string; onChange: (json: string) => void; className?: string; style?: CSSProperties; label?: string; showEnablement?: boolean };

export function ResourceSourceEditor({ value, onChange, className = "", style, label = "Edit this resource directly", showEnablement = true }: Props) {
  const [format, setFormat] = useState<"metta" | "json">("metta");
  const [metta, setMetta] = useState("");
  const [error, setError] = useState("");
  const emittedJson = useRef<string | null>(null);

  useEffect(() => {
    if (value === emittedJson.current) { emittedJson.current = null; return; }
    if (!value) { setMetta(""); return; }
    try { setMetta(jsonDocumentToMetta(value)); setError(""); }
    catch { /* Preserve an in-progress invalid source. */ }
  }, [value]);

  const editMetta = (next: string) => {
    setMetta(next);
    try { const json = mettaDocumentToJson(next); emittedJson.current = json; onChange(json); setError(""); }
    catch (reason) { onChange(""); setError(reason instanceof Error ? reason.message : String(reason)); }
  };
  let resource: Record<string, unknown> | null = null;
  try { const parsed = JSON.parse(value); if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) resource = parsed; } catch { /* Invalid source remains editable. */ }
  const resourceEnabled = resource?.enabled !== false;
  const setEnabled = (enabled: boolean) => { if (resource) onChange(JSON.stringify({ ...resource, enabled }, null, 2)); };

  return <div className="operation-json-block resource-source-editor">
    <div className="llm-subhead"><div><span>RESOURCE SOURCE</span><b>{label}</b></div><div className="source-format-tabs">{showEnablement&&resource&&<button className={`resource-enable-action ${resourceEnabled?"disable-resource":"enable-resource"}`} onClick={()=>setEnabled(!resourceEnabled)}>{resourceEnabled?"Disable Resource":"Enable Resource"}</button>}<button className={format === "metta" ? "active" : ""} onClick={() => setFormat("metta")}>MeTTa</button><button className={format === "json" ? "active" : ""} onClick={() => setFormat("json")}>JSON</button></div></div>
    <textarea className={`raw-json-editor operation-visible-editor ${className}`.trim()} style={style} value={format === "metta" ? metta : value} onChange={event => format === "metta" ? editMetta(event.target.value) : onChange(event.target.value)} />
    {error && <div className="validation bad">Invalid MeTTa resource: {error}</div>}
  </div>;
}
