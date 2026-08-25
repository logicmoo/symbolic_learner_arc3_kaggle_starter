import { useEffect, useMemo, useRef, useState } from "react";
import { MOUNT } from "./api";
import { EventBubble } from "./EventBubble";
import { useCollab } from "./useCollab";
import type { CollabEvent, Format, ViewMode } from "./types";
import { compactData, eventText, shortTs } from "./util";

function EventList({ events }: { events: CollabEvent[] }) {
  return (
    <table className="wsc-list">
      <tbody>
        {events.map((event) => (
          <tr key={event.id}>
            <td className="wsc-c-ts">{shortTs(event.ts)}</td>
            <td className="wsc-c-src">{event.source_id || event.source_kind || "—"}</td>
            <td className="wsc-c-type">{event.type}</td>
            <td className="wsc-c-sum">
              {eventText(event) || <span className="wsc-muted">{compactData(event)}</span>}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function App() {
  const { status, streams, buffers, seed } = useCollab();
  const [stream, setStream] = useState("conversation");
  const [format, setFormat] = useState<Format>("markdown");
  const [view, setView] = useState<ViewMode>("tiles");
  const [query, setQuery] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (streams.length && !streams.includes(stream)) setStream(streams[0]);
  }, [streams, stream]);

  useEffect(() => { if (stream) void seed(stream); }, [stream, seed]);

  const events = buffers[stream] ?? [];
  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return events;
    return events.filter((event) => JSON.stringify(event).toLowerCase().includes(needle));
  }, [events, query]);

  useEffect(() => {
    const node = scrollRef.current;
    if (!node) return;
    const atBottom = node.scrollHeight - node.scrollTop - node.clientHeight < 80;
    if (atBottom) node.scrollTop = node.scrollHeight;
  }, [filtered.length, view, format]);

  const shown = view === "tiles" ? filtered.slice(-300) : filtered.slice(-500);

  return (
    <div className="wsc-shell">
      <header className="wsc-top">
        <span className="wsc-brand">WS_COLLAB</span>
        <span className="wsc-subtitle">Streams · shared-TSX admin</span>
        <span className="wsc-spacer" />
        <a className="wsc-link" href={`${MOUNT}/admin/`}>Classic admin ↗</a>
        <span className={`wsc-status wsc-status-${status}`}>{status}</span>
      </header>

      <div className="wsc-toolbar">
        <select value={stream} onChange={(event) => setStream(event.target.value)}>
          {streams.map((name) => (
            <option key={name} value={name}>{name} ({(buffers[name] ?? []).length})</option>
          ))}
        </select>
        <div className="wsc-seg">
          <button className={view === "list" ? "on" : ""} onClick={() => setView("list")}>List</button>
          <button className={view === "tiles" ? "on" : ""} onClick={() => setView("tiles")}>Tiles</button>
        </div>
        <select value={format} onChange={(event) => setFormat(event.target.value as Format)}>
          <option value="markdown">Markdown</option>
          <option value="json">JSON</option>
          <option value="metta">MeTTa</option>
          <option value="text">Text</option>
        </select>
        <input
          type="search"
          placeholder="filter…"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <span className="wsc-spacer" />
        <span className="wsc-count">{filtered.length} shown</span>
      </div>

      <div className={`wsc-body wsc-body-${view}`} ref={scrollRef}>
        {shown.length === 0 && <div className="wsc-empty">No events yet on “{stream}”.</div>}
        {view === "tiles"
          ? shown.map((event) => <EventBubble key={event.id} event={event} format={format} />)
          : <EventList events={shown} />}
      </div>
    </div>
  );
}
