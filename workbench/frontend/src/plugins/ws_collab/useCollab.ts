import { useCallback, useEffect, useRef, useState } from "react";
import { getJSON, wsUrl } from "./api";
import type { Capabilities, CollabEvent } from "./types";

const MAX_PER_STREAM = 500;

export type ConnStatus = "connecting" | "live" | "offline";

interface WsFrame {
  type: string;
  event?: CollabEvent;
  capabilities?: Capabilities;
  stream?: string;
  cursor?: string;
  error?: { message?: string };
}

/** Live WS connection to the ws_collab server with per-stream buffers. */
export function useCollab() {
  const [status, setStatus] = useState<ConnStatus>("connecting");
  const [streams, setStreams] = useState<string[]>([]);
  const [buffers, setBuffers] = useState<Record<string, CollabEvent[]>>({});
  const backoff = useRef(1000);
  const closed = useRef(false);

  const append = useCallback((event: CollabEvent) => {
    setBuffers((prev) => {
      const list = prev[event.stream] ? prev[event.stream].slice() : [];
      if (list.some((existing) => existing.id === event.id)) return prev;
      list.push(event);
      if (list.length > MAX_PER_STREAM) list.splice(0, list.length - MAX_PER_STREAM);
      return { ...prev, [event.stream]: list };
    });
  }, []);

  const seed = useCallback(async (stream: string) => {
    try {
      const res = await getJSON<{ events?: CollabEvent[] }>(`/${stream}?limit=100`);
      if (!Array.isArray(res.events) || !res.events.length) return;
      setBuffers((prev) => {
        const existing = prev[stream] ?? [];
        const seen = new Set(existing.map((event) => event.id));
        const merged = [...res.events!.filter((event) => !seen.has(event.id)), ...existing];
        merged.sort((a, b) => a.seq - b.seq);
        return { ...prev, [stream]: merged.slice(-MAX_PER_STREAM) };
      });
    } catch {
      /* backfill is best-effort; live WS will fill in */
    }
  }, []);

  useEffect(() => {
    closed.current = false;
    let socket: WebSocket | null = null;
    let timer: number | undefined;

    getJSON<Capabilities>("/capabilities")
      .then((caps) => { if (caps.streams) setStreams(Object.keys(caps.streams)); })
      .catch(() => { /* WS auth_ok also carries capabilities */ });

    const connect = () => {
      setStatus("connecting");
      try {
        socket = new WebSocket(wsUrl());
      } catch {
        setStatus("offline");
        timer = window.setTimeout(connect, backoff.current);
        return;
      }
      socket.onopen = () => socket?.send(JSON.stringify({ type: "auth", token: "local" }));
      socket.onmessage = (message) => {
        let frame: WsFrame;
        try { frame = JSON.parse(message.data as string) as WsFrame; } catch { return; }
        if (frame.type === "auth_ok") {
          backoff.current = 1000;
          setStatus("live");
          const names = frame.capabilities?.streams ? Object.keys(frame.capabilities.streams) : [];
          if (names.length) setStreams(names);
          socket?.send(JSON.stringify({ type: "subscribe", streams: names, cursors: {} }));
        } else if (frame.type === "event" && frame.event) {
          append(frame.event);
        } else if (frame.type === "ping") {
          socket?.send(JSON.stringify({ type: "pong" }));
        }
      };
      socket.onclose = () => {
        setStatus("offline");
        if (closed.current) return;
        backoff.current = Math.min(backoff.current * 2, 15000);
        timer = window.setTimeout(connect, backoff.current);
      };
      socket.onerror = () => socket?.close();
    };
    connect();

    return () => {
      closed.current = true;
      if (timer) clearTimeout(timer);
      socket?.close();
    };
  }, [append]);

  return { status, streams, buffers, seed };
}
