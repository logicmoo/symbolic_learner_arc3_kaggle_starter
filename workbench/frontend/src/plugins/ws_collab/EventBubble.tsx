import { MarkdownDocument } from "../../components/MarkdownDocument";
import { jsonValueToMetta } from "../../lib/mettaResourceCodec";
import type { CollabEvent, Format } from "./types";
import { pickText, shortTs } from "./util";

function BubbleBody({ data, format }: { data: Record<string, unknown>; format: Format }) {
  if (format === "json") {
    return <pre className="wsc-code">{JSON.stringify(data, null, 2)}</pre>;
  }
  if (format === "metta") {
    let text: string;
    try { text = jsonValueToMetta(data); } catch { text = JSON.stringify(data, null, 2); }
    return <pre className="wsc-code">{text}</pre>;
  }
  const text = pickText(data);
  if (format === "text") {
    return <div className="wsc-plain">{text || JSON.stringify(data)}</div>;
  }
  const content = text || `\`\`\`json\n${JSON.stringify(data, null, 2)}\n\`\`\``;
  return <MarkdownDocument content={content} className="wsc-md" />;
}

/** One event rendered as a chat bubble, mirroring the workbench mailbox reader. */
export function EventBubble({ event, format }: { event: CollabEvent; format: Format }) {
  const data = event.data ?? {};
  const kind = event.source_kind || "system";
  return (
    <div className={`wsc-row wsc-kind-${kind}`}>
      <div className="wsc-bubble">
        <div className="wsc-head">
          <span className="wsc-bsrc">{event.source_id || kind}</span>
          <span className="wsc-btype">{event.type}</span>
          <span className="wsc-bts">{shortTs(event.ts)}</span>
        </div>
        <BubbleBody data={data} format={format} />
      </div>
    </div>
  );
}
