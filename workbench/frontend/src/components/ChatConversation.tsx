import { useCallback, useEffect, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from "react";
import { MarkdownDocument } from "./MarkdownDocument";
import { jsonDocumentToMetta, mettaDocumentToJson } from "../lib/mettaResourceCodec";
import "../styles/chat.css";

// The workbench user identity and the agent they talk to. Both sides of this pair
// are read back from the shared mailbox, so the same component renders the whole
// two-way conversation.
export const DEFAULT_CHAT_USER = "symbolic-workbench-user";
export const DEFAULT_CHAT_PEER = "symbolic-workbench-user";

export type ChatMessage = {
  id: string;
  timestamp?: string;
  from?: string;
  to?: string;
  text: string;
  type?: string;
  channelId?: string | null;
  author?: string | null;
  authorName?: string | null;
  channelName?: string | null;
  raw?: unknown;
};

export type ChannelOption = { id: string; kind?: string; messages?: number; name?: string | null };

type CursorInfo = {
  channel: string;
  agent: string;
  initialized: boolean;
  offset: number;
  size: number;
  behind: number;
  entries_consumed?: number;
  entry_next?: string;
  entries_total?: number;
};
export type AgentOption = { id: string; [key: string]: unknown };

type Props = {
  user?: string;
  peer?: string;
  className?: string;
  pollMs?: number;
  showChannelPicker?: boolean;
  onError?: (message: string) => void;
};

function formatTime(value?: string): string {
  if (!value) return "";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

async function readJson(response: Response): Promise<Record<string, unknown>> {
  const payload = (await response.json()) as Record<string, unknown>;
  if (!response.ok) {
    const detail = payload.error || payload.detail || response.statusText;
    throw new Error(String(detail));
  }
  return payload;
}

// Shared chat surface used by both the full Chat page and the floatable mini-dock.
// Four editable combos drive it: YOU/TO pick agents, CHANNEL (view) and SEND-TO
// (channel_id) pick channels. All are editable so a new name can be typed in;
// addressing an agent with a SEND-TO channel auto-subscribes it server-side. Every
// message carries its raw record so it can be inspected as JSON.
export function ChatConversation({
  user = DEFAULT_CHAT_USER,
  peer = DEFAULT_CHAT_PEER,
  className,
  pollMs = 3000,
  showChannelPicker = true,
  onError,
}: Props) {
  const [you, setYou] = useState(user);
  const [channel, setChannel] = useState(peer);
  const [target, setTarget] = useState(peer);
  const [sendChannel, setSendChannel] = useState("");
  const [agents, setAgents] = useState<AgentOption[]>([]);
  const [channels, setChannels] = useState<ChannelOption[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [ready, setReady] = useState(false);
  const [errorText, setErrorText] = useState("");
  const [newEntry, setNewEntry] = useState("");
  const [configText, setConfigText] = useState("");
  const [configError, setConfigError] = useState("");
  const [configNote, setConfigNote] = useState("");
  const [configBusy, setConfigBusy] = useState(false);
  const [cursorInfo, setCursorInfo] = useState<CursorInfo | null>(null);
  const [cursorBusy, setCursorBusy] = useState(false);
  const [subBusy, setSubBusy] = useState(false);
  const [inspect, setInspect] = useState<{ label: string; id: string; kind: "agent" | "channel" } | null>(null);
  const [inspectText, setInspectText] = useState("");
  const [inspectNote, setInspectNote] = useState("");
  const [inspectBusy, setInspectBusy] = useState(false);
  const [entryEditId, setEntryEditId] = useState<string | null>(null);
  const [entryEditText, setEntryEditText] = useState("");
  const [entryEditFormat, setEntryEditFormat] = useState<"json" | "metta">("json");
  const [entryEditNote, setEntryEditNote] = useState("");
  const [entryEditBusy, setEntryEditBusy] = useState(false);
  // Require-match bar: the list looks EVERYWHERE in the log; each depressed
  // button ANDs its picker's value in as a required match. Only CHANNEL is
  // required by default (classic channel view).
  const [requireTo, setRequireTo] = useState(false);
  const [requireFrom, setRequireFrom] = useState(false);
  const [requireChannel, setRequireChannel] = useState(true);
  const [requireSendTo, setRequireSendTo] = useState(false);
  const [requireText, setRequireText] = useState(false);
  const [textExpr, setTextExpr] = useState("");
  const [textQuery, setTextQuery] = useState("");
  const listRef = useRef<HTMLDivElement | null>(null);
  const stickBottomRef = useRef(true);

  // The config editor tracks the channel messages are sent on (SEND-TO channel if
  // set, otherwise the viewed channel).
  const configChannel = sendChannel || channel;

  // Switching the viewed channel re-points addressing to it by default; the "To"
  // field can then be overridden to address anyone independently.
  const selectChannel = useCallback((next: string) => {
    setChannel(next);
    setTarget(next);
  }, []);

  const fetchDirectory = useCallback(async () => {
    try {
      const [agentPayload, channelPayload] = await Promise.all([
        readJson(await fetch("/api/mailbox/agents")),
        readJson(await fetch("/api/mailbox/channels")),
      ]);
      setAgents((agentPayload.agents as AgentOption[]) || []);
      setChannels((channelPayload.channels as ChannelOption[]) || []);
    } catch {
      // Directory is best-effort; keep whatever we already have.
    }
  }, []);

  // Debounce the text expression so typing doesn't refetch per keystroke.
  useEffect(() => {
    const timer = window.setTimeout(() => setTextQuery(textExpr.trim()), 400);
    return () => window.clearTimeout(timer);
  }, [textExpr]);

  const fetchMessages = useCallback(async () => {
    try {
      const params = new URLSearchParams({ filter: "1", limit: "300" });
      if (requireTo && target) params.set("to", target);
      if (requireFrom && you) params.set("from", you);
      if (requireChannel && channel) params.set("channel", channel);
      if (requireSendTo && sendChannel) params.set("channel_id", sendChannel);
      if (requireText && textQuery) params.set("text", textQuery);
      const payload = await readJson(await fetch(`/api/mailbox/messages?${params.toString()}`));
      setMessages((payload.messages as ChatMessage[]) || []);
      setReady(true);
      setErrorText("");
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorText(message);
      onError?.(message);
    }
  }, [
    channel, you, target, sendChannel,
    requireTo, requireFrom, requireChannel, requireSendTo, requireText, textQuery,
    onError,
  ]);

  useEffect(() => {
    fetchDirectory();
    const timer = window.setInterval(fetchDirectory, 15000);
    return () => window.clearInterval(timer);
  }, [fetchDirectory]);

  useEffect(() => {
    let active = true;
    setReady(false);
    setMessages([]);
    stickBottomRef.current = true;
    fetchMessages();
    const timer = window.setInterval(() => {
      if (active) fetchMessages();
    }, Math.max(1000, pollMs));
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [fetchMessages, pollMs]);

  useEffect(() => {
    const node = listRef.current;
    if (node && stickBottomRef.current) node.scrollTop = node.scrollHeight;
  }, [messages]);

  const handleScroll = () => {
    const node = listRef.current;
    if (!node) return;
    stickBottomRef.current = node.scrollHeight - node.scrollTop - node.clientHeight < 48;
  };

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || sending) return;
    setSending(true);
    try {
      const body: Record<string, unknown> = { text, to: target, sender: you };
      const routed = sendChannel.trim();
      if (routed) body.channel_id = routed;
      await readJson(
        await fetch("/api/mailbox/send", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }),
      );
      setInput("");
      stickBottomRef.current = true;
      await fetchMessages();
      void fetchDirectory(); // refresh picker counts/lastMessageAt right away
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorText(message);
      onError?.(message);
    } finally {
      setSending(false);
    }
  }, [input, sending, target, you, sendChannel, fetchMessages, fetchDirectory, onError]);

  const handleKeyDown = (event: ReactKeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      send();
    }
  };

  const makeAgent = useCallback(async () => {
    const id = newEntry.trim();
    if (!id) return;
    try {
      await readJson(
        await fetch("/api/mailbox/agents", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id }),
        }),
      );
      setAgents((prev) => (prev.some((a) => a.id === id) ? prev : [...prev, { id }]));
      setTarget(id);
      setNewEntry("");
      fetchDirectory();
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorText(message);
      onError?.(message);
    }
  }, [newEntry, fetchDirectory, onError]);

  const makeChannel = useCallback(async () => {
    const id = newEntry.trim();
    if (!id) return;
    try {
      await readJson(
        await fetch("/api/mailbox/channels", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id }),
        }),
      );
      setChannels((prev) => (prev.some((c) => c.id === id) ? prev : [...prev, { id, kind: "channel" }]));
      setChannel(id);
      setTarget(id);
      setSendChannel(id);
      setNewEntry("");
      fetchDirectory();
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorText(message);
      onError?.(message);
    }
  }, [newEntry, fetchDirectory, onError]);

  // Messages without text default to the JSON view; the toggle flips from the effective state.
  const toggleRaw = (id: string, defaultOpen = false) =>
    setExpanded((prev) => ({ ...prev, [id]: !(prev[id] ?? defaultOpen) }));

  // Per-entry ✎ editor: the bubble becomes the editor. Save posts the COMPLETE
  // record to /api/mailbox/record, either rewriting its log line (in-place) or
  // appending the edit as the newest record and marking the old one
  // replaced-by: entry_<n> (at-end). Like the other JSON editors it has a
  // MeTTa mode (mettaResourceCodec), Reload discards edits, Save as..
  // downloads to disk.
  const openEntryEdit = (message: ChatMessage) => {
    if (entryEditId === message.id) {
      setEntryEditId(null);
      return;
    }
    setEntryEditId(message.id);
    setEntryEditFormat("json");
    setEntryEditText(JSON.stringify(message.raw ?? message, null, 2));
    setEntryEditNote("");
  };

  const entryEditAsJson = (): string => {
    if (entryEditFormat === "json") return entryEditText;
    return mettaDocumentToJson(entryEditText);
  };

  const toggleEntryEditFormat = () => {
    try {
      if (entryEditFormat === "json") {
        setEntryEditText(jsonDocumentToMetta(entryEditText));
        setEntryEditFormat("metta");
      } else {
        setEntryEditText(mettaDocumentToJson(entryEditText));
        setEntryEditFormat("json");
      }
      setEntryEditNote("");
    } catch (error) {
      setEntryEditNote(error instanceof Error ? error.message : String(error));
    }
  };

  const reloadEntryEdit = () => {
    const message = messages.find((entry) => entry.id === entryEditId);
    if (!message) {
      setEntryEditNote("record is no longer in view");
      return;
    }
    const json = JSON.stringify(message.raw ?? message, null, 2);
    try {
      setEntryEditText(entryEditFormat === "metta" ? jsonDocumentToMetta(json) : json);
      setEntryEditNote("reloaded — edits discarded");
    } catch (error) {
      setEntryEditNote(error instanceof Error ? error.message : String(error));
    }
  };

  const downloadEntryEdit = () => {
    const extension = entryEditFormat === "metta" ? "metta" : "json";
    const blob = new Blob([entryEditText], {
      type: extension === "json" ? "application/json" : "text/plain",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${entryEditId || "record"}.${extension}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const saveEntryEdit = async (mode: "in-place" | "at-end") => {
    if (!entryEditId) return;
    let record: unknown;
    try {
      record = JSON.parse(entryEditAsJson());
    } catch (error) {
      setEntryEditNote(`invalid ${entryEditFormat === "metta" ? "MeTTa" : "JSON"}: ${
        error instanceof Error ? error.message : String(error)
      }`);
      return;
    }
    setEntryEditBusy(true);
    try {
      const payload = await readJson(
        await fetch("/api/mailbox/record", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: entryEditId, record, mode }),
        }),
      );
      setEntryEditNote(
        mode === "at-end" && payload.entryKey ? `saved at-end as ${payload.entryKey}` : `saved ${mode}`,
      );
      await fetchMessages();
    } catch (error) {
      setEntryEditNote(error instanceof Error ? error.message : String(error));
    } finally {
      setEntryEditBusy(false);
    }
  };

  const fetchConfig = useCallback(async () => {
    if (!configChannel) {
      setConfigText("");
      return;
    }
    try {
      const payload = await readJson(
        await fetch(`/api/mailbox/channel-config?channel=${encodeURIComponent(configChannel)}`),
      );
      setConfigText(JSON.stringify(payload.config ?? {}, null, 2));
      setConfigError("");
      setConfigNote("");
    } catch (error) {
      setConfigError(error instanceof Error ? error.message : String(error));
    }
  }, [configChannel]);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  // Apply = subscribe any new names in `subscribers`, then persist the whole
  // edited config as a channel_config record on the server_registry channel.
  const applyConfig = useCallback(async () => {
    let parsed: unknown;
    try {
      parsed = JSON.parse(configText);
    } catch (error) {
      setConfigError(`Invalid JSON: ${error instanceof Error ? error.message : String(error)}`);
      return;
    }
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      setConfigError("Config must be a JSON object");
      return;
    }
    setConfigBusy(true);
    try {
      const payload = await readJson(
        await fetch("/api/mailbox/channel-config", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ channel: configChannel, config: parsed }),
        }),
      );
      setConfigText(JSON.stringify(payload.config ?? parsed, null, 2));
      const subscribed = (payload.subscribed as string[]) || [];
      setConfigNote(
        `Stored on server_registry${subscribed.length ? `; subscribed: ${subscribed.join(", ")}` : ""}`,
      );
      setConfigError("");
    } catch (error) {
      setConfigError(error instanceof Error ? error.message : String(error));
    } finally {
      setConfigBusy(false);
    }
  }, [configChannel, configText]);

  // Cursor control: while looking at a channel with "To" set to an agent, show
  // where that agent's cursor sits on the channel and allow repositioning it.
  const fetchCursor = useCallback(async () => {
    if (!channel || !target) {
      setCursorInfo(null);
      return;
    }
    try {
      const query = `channel=${encodeURIComponent(channel)}&agent=${encodeURIComponent(target)}`;
      const payload = await readJson(await fetch(`/api/mailbox/cursor?${query}`));
      setCursorInfo(payload as CursorInfo);
    } catch {
      setCursorInfo(null);
    }
  }, [channel, target]);

  useEffect(() => {
    fetchCursor();
  }, [fetchCursor]);

  const moveCursor = useCallback(
    async (start: "beginning" | "now" | "remove") => {
      if (!channel || !target) return;
      setCursorBusy(true);
      try {
        const query = `channel=${encodeURIComponent(channel)}&agent=${encodeURIComponent(target)}`;
        const payload = await readJson(
          start === "remove"
            ? await fetch(`/api/mailbox/cursor?${query}`, { method: "DELETE" })
            : await fetch("/api/mailbox/cursor", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ channel, agent: target, start }),
              }),
        );
        setCursorInfo(payload as CursorInfo);
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        setErrorText(message);
        onError?.(message);
      } finally {
        setCursorBusy(false);
      }
    },
    [channel, target, onError],
  );

  // Subscription control: set/clear the explicit subscribed|unsubscribed intent
  // for the TO agent on the viewed channel ("remove" reverts to the default
  // inference where cursor holders count as subscribed).
  const setSubscription = useCallback(
    async (state: "subscribed" | "unsubscribed" | "remove") => {
      if (!channel || !target) return;
      setSubBusy(true);
      try {
        await readJson(
          await fetch("/api/mailbox/subscription", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ agent: target, channel, state }),
          }),
        );
        await Promise.all([fetchDirectory(), fetchCursor()]);
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        setErrorText(message);
        onError?.(message);
      } finally {
        setSubBusy(false);
      }
    },
    [channel, target, fetchDirectory, fetchCursor, onError],
  );

  // Selects need the current value present as an option even before lists load.
  // Clicking a picker label (YOU/TO/CHANNEL/SEND-TO) opens an editable JSON view
  // of whatever that picker points at; clicking the same label again hides it.
  // YOU/TO show the agent record as returned by /api/mailbox/agents (cursors
  // included); the channel labels show the channel record. Save posts the edited
  // JSON to the server_agents_registry / server_channels_registry blackboard
  // channel; Reload
  // re-queries the record.
  const loadEntity = useCallback(async (kind: "agent" | "channel", id: string) => {
    const endpoint = kind === "agent" ? "/api/mailbox/agents" : "/api/mailbox/channels";
    const payload = await readJson(await fetch(endpoint));
    const list = (payload[kind === "agent" ? "agents" : "channels"] as Array<Record<string, unknown>>) || [];
    return list.find((item) => item.id === id) ?? { id };
  }, []);

  const inspectId = useCallback(
    (label: string, id: string) => {
      if (!id) return;
      if (inspect && inspect.label === label && inspect.id === id) {
        setInspect(null);
        return;
      }
      const kind = label === "YOU" || label === "TO" ? ("agent" as const) : ("channel" as const);
      const record =
        kind === "agent"
          ? agents.find((a) => a.id === id) ?? { id }
          : channels.find((c) => c.id === id) ?? { id };
      setInspect({ label, id, kind });
      setInspectText(JSON.stringify(record, null, 2));
      setInspectNote("");
    },
    [inspect, agents, channels],
  );

  const reloadInspect = useCallback(async () => {
    if (!inspect) return;
    setInspectBusy(true);
    try {
      const record = await loadEntity(inspect.kind, inspect.id);
      setInspectText(JSON.stringify(record, null, 2));
      setInspectNote("reloaded");
      void fetchDirectory();
    } catch (error) {
      setInspectNote(error instanceof Error ? error.message : String(error));
    } finally {
      setInspectBusy(false);
    }
  }, [inspect, loadEntity, fetchDirectory]);

  const saveInspect = useCallback(async () => {
    if (!inspect) return;
    let parsed: unknown;
    try {
      parsed = JSON.parse(inspectText);
    } catch (error) {
      setInspectNote(`Invalid JSON: ${error instanceof Error ? error.message : String(error)}`);
      return;
    }
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      setInspectNote("Entry must be a JSON object");
      return;
    }
    setInspectBusy(true);
    try {
      const payload = await readJson(
        await fetch("/api/mailbox/entity", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ kind: inspect.kind, id: inspect.id, entry: parsed }),
        }),
      );
      const record = (payload.entry as Record<string, unknown>) ?? parsed;
      setInspectText(JSON.stringify(record, null, 2));
      setInspectNote(`saved to ${String(payload.channel ?? "")}`.trim());
      void fetchDirectory();
    } catch (error) {
      setInspectNote(error instanceof Error ? error.message : String(error));
    } finally {
      setInspectBusy(false);
    }
  }, [inspect, inspectText, fetchDirectory]);

  // Cursor moves change what an open inspector shows (the agent's cursor map or
  // the channel's subscribers), so requery it when it points at the affected pair.
  useEffect(() => {
    if (!cursorInfo || !inspect) return;
    const affected =
      (inspect.kind === "agent" && inspect.id === cursorInfo.agent) ||
      (inspect.kind === "channel" && inspect.id === cursorInfo.channel);
    if (!affected) return;
    let stale = false;
    loadEntity(inspect.kind, inspect.id)
      .then((record) => {
        if (!stale) setInspectText(JSON.stringify(record, null, 2));
      })
      .catch(() => {
        // keep the current text when the refresh fails
      });
    return () => {
      stale = true;
    };
  }, [cursorInfo, inspect, loadEntity]);

  // Combo boxes list alphabetically (case-insensitive); dedup keeps the
  // currently-selected values present even when the directory lags.
  const alpha = (a: string, b: string) => a.toLowerCase().localeCompare(b.toLowerCase());
  const agentChoices = Array.from(new Set([you, target, ...agents.map((a) => a.id)].filter(Boolean))).sort(alpha);
  const channelChoices = Array.from(new Set([channel, ...channels.map((c) => c.id)].filter(Boolean))).sort(alpha);
  const sendChoices = Array.from(new Set([sendChannel, ...channels.map((c) => c.id)].filter(Boolean))).sort(alpha);

  // Channel options carry a readable name resolved from the identifier directory
  // (bootstrapped onto server_identifiers_registry), so opaque bridge ids get
  // annotated, and show how many entries recent traffic holds for each channel.
  const channelNames = new Map(channels.map((c) => [c.id, c.name] as const));
  const channelCounts = new Map(channels.map((c) => [c.id, c.messages] as const));
  // The TO agent's explicit subscription setting on the viewed channel (if any).
  const targetRecord = agents.find((a) => a.id === target) as Record<string, unknown> | undefined;
  const targetSubs = (targetRecord?.subscriptions ?? null) as Record<string, string> | null;
  const subSetting = targetSubs && channel in targetSubs ? targetSubs[channel] : null;
  const channelLabel = (id: string) => {
    const name = channelNames.get(id);
    const base = name && name !== id ? `${name} · ${id}` : id;
    const count = channelCounts.get(id);
    return typeof count === "number" ? `${base} · ${count}` : base;
  };

  return (
    <div className={`chat-conversation ${className ?? ""}`.trim()}>
      {showChannelPicker && (
        <div className="chat-controls">
          <label className="chat-control">
            <button type="button" className="chat-label" onClick={() => void inspectId("YOU", you)}>You</button>
            <select value={you} onChange={(event) => setYou(event.target.value)} aria-label="Your agent identity">
              {agentChoices.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </label>
          <label className="chat-control">
            <button type="button" className="chat-label" onClick={() => void inspectId("TO", target)}>To</button>
            <select value={target} onChange={(event) => setTarget(event.target.value)} aria-label="Addressed agent">
              {agentChoices.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </label>
          <label className="chat-control">
            <button type="button" className="chat-label" onClick={() => void inspectId("CHANNEL", channel)}>Channel</button>
            <select value={channel} onChange={(event) => selectChannel(event.target.value)} aria-label="Viewed channel">
              {channelChoices.map((id) => (
                <option key={id} value={id}>{channelLabel(id)}</option>
              ))}
            </select>
          </label>
          <label className="chat-control">
            <button type="button" className="chat-label" onClick={() => void inspectId("SEND-TO", sendChannel)}>Send-to</button>
            <select value={sendChannel} onChange={(event) => setSendChannel(event.target.value)} aria-label="Send channel">
              <option value="">(none)</option>
              {sendChoices.map((id) => (
                <option key={id} value={id}>{channelLabel(id)}</option>
              ))}
            </select>
          </label>
          <div className="chat-require">
            <span className="chat-require-label" title="The list looks EVERYWHERE in the log; each depressed button requires its picker's value to match (AND).">
              Require match
            </span>
            <button
              type="button"
              className={`chat-require-btn${requireTo ? " active" : ""}`}
              aria-pressed={requireTo}
              title="Require record.to to equal the TO picker"
              onClick={() => setRequireTo((v) => !v)}
            >
              TO
            </button>
            <button
              type="button"
              className={`chat-require-btn${requireFrom ? " active" : ""}`}
              aria-pressed={requireFrom}
              title="Require record.from to equal the YOU picker"
              onClick={() => setRequireFrom((v) => !v)}
            >
              FROM
            </button>
            <button
              type="button"
              className={`chat-require-btn${requireChannel ? " active" : ""}`}
              aria-pressed={requireChannel}
              title="Require the record to involve the CHANNEL picker (from, to or channel_id)"
              onClick={() => setRequireChannel((v) => !v)}
            >
              CHANNEL
            </button>
            <button
              type="button"
              className={`chat-require-btn${requireSendTo ? " active" : ""}`}
              aria-pressed={requireSendTo}
              title="Require record.channel_id to equal the SEND-TO picker"
              onClick={() => setRequireSendTo((v) => !v)}
            >
              SEND-TO
            </button>
            <button
              type="button"
              className={`chat-require-btn${requireText ? " active" : ""}`}
              aria-pressed={requireText}
              title="Require the text expression below to match (substring, or /regex/)"
              onClick={() => setRequireText((v) => !v)}
            >
              TEXT
            </button>
            <input
              className="chat-require-input"
              value={textExpr}
              onChange={(event) => setTextExpr(event.target.value)}
              placeholder="text expression — substring or /regex/"
              aria-label="Text expression"
            />
          </div>
          <div className="chat-make">
            <input
              value={newEntry}
              onChange={(event) => setNewEntry(event.target.value)}
              placeholder="new agent or channel name"
              aria-label="New agent or channel name"
            />
            <button type="button" onClick={makeAgent} disabled={!newEntry.trim()}>
              Make new agent
            </button>
            <button type="button" onClick={makeChannel} disabled={!newEntry.trim()}>
              Make new channel
            </button>
          </div>
          {channel && target && (
            <div className="chat-cursor">
              <span className="chat-cursor-label">
                Cursor · {target} on {channelLabel(channel)}:{" "}
                {cursorInfo
                  ? cursorInfo.initialized
                    ? `${cursorInfo.entry_next ?? "?"} next · ${cursorInfo.entries_consumed ?? 0}/${cursorInfo.entries_total ?? "?"} entries consumed · ${cursorInfo.behind} bytes behind`
                    : `no cursor set (channel holds ${cursorInfo.entries_total ?? 0} entries)`
                  : "…"}
              </span>
              <button type="button" disabled={cursorBusy} onClick={() => void moveCursor("beginning")}>
                ⏮ Beginning
              </button>
              <button type="button" disabled={cursorBusy} onClick={() => void moveCursor("now")}>
                Now ⏭
              </button>
              <button
                type="button"
                disabled={cursorBusy || !(cursorInfo && cursorInfo.initialized)}
                onClick={() => void moveCursor("remove")}
              >
                ✕ Remove
              </button>
            </div>
          )}
          {channel && target && (
            <div className="chat-sub">
              <span className="chat-sub-label" title="Explicit subscription intent; 'Remove setting' reverts to the default (cursor holders count as subscribed).">
                Subscription · {target} on {channelLabel(channel)}:{" "}
                {subSetting ?? (cursorInfo && cursorInfo.initialized ? "(default: subscribed via cursor)" : "(no setting)")}
              </span>
              <button
                type="button"
                className={subSetting === "subscribed" ? "active" : ""}
                disabled={subBusy}
                onClick={() => void setSubscription("subscribed")}
              >
                Subscribed
              </button>
              <button
                type="button"
                className={subSetting === "unsubscribed" ? "active" : ""}
                disabled={subBusy}
                onClick={() => void setSubscription("unsubscribed")}
              >
                Unsubscribed
              </button>
              <button type="button" disabled={subBusy || !subSetting} onClick={() => void setSubscription("remove")}>
                ✕ Remove setting
              </button>
            </div>
          )}
          {inspect && (
            <div className="chat-inspect">
              <div className="chat-inspect-head">
                <span>{inspect.label} · {inspect.id}</span>
                {inspectNote && <span className="chat-inspect-note">{inspectNote}</span>}
                <button type="button" className="chat-json-toggle" disabled={inspectBusy} onClick={() => void reloadInspect()}>
                  ⟳ Reload
                </button>
                <button type="button" className="chat-json-toggle" disabled={inspectBusy} onClick={() => void saveInspect()}>
                  Save
                </button>
                <button type="button" className="chat-json-toggle" onClick={() => setInspect(null)}>
                  ✕
                </button>
              </div>
              <textarea
                className="chat-inspect-edit"
                value={inspectText}
                onChange={(event) => setInspectText(event.target.value)}
                spellCheck={false}
                aria-label={`${inspect.kind} JSON entry`}
              />
            </div>
          )}
        </div>
      )}
      <div className="chat-messages" ref={listRef} onScroll={handleScroll}>
        {ready && messages.length === 0 && (
          <div className="chat-empty">No messages match the required filters.</div>
        )}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`chat-message ${message.from === you ? "mine" : "theirs"}${
              entryEditId === message.id ? " editing" : ""
            }`}
          >
            <div className="chat-message-meta">
              <span className="chat-message-from">{message.authorName || message.author || message.from}</span>
              {message.author && message.from && message.author !== message.from && (
                <span className="chat-message-via">via {message.from}</span>
              )}
              {message.type && message.type !== "message" && (
                <span className="chat-message-type">{message.type}</span>
              )}
              {message.timestamp && (
                <span className="chat-message-time">{formatTime(message.timestamp)}</span>
              )}
              <button
                type="button"
                className="chat-json-toggle"
                title="Inspect raw JSON"
                aria-label="Inspect raw JSON"
                onClick={() => toggleRaw(message.id, !message.text)}
              >
                {"{ }"}
              </button>
              <button
                type="button"
                className="chat-json-toggle"
                title="Edit record JSON"
                aria-label="Edit record JSON"
                onClick={() => openEntryEdit(message)}
              >
                {"\u270e"}
              </button>
            </div>
            {message.text ? (
              <MarkdownDocument className="chat-message-body" content={message.text} />
            ) : (
              <div className="chat-message-empty">
                {message.channelName
                  ? `(${message.type || "message"} in ${message.channelName} — inspect JSON)`
                  : "(no text — inspect JSON)"}
              </div>
            )}
            {(expanded[message.id] ?? !message.text) && entryEditId !== message.id && (
              <pre className="chat-message-json">
                {JSON.stringify(message.raw ?? message, null, 2)}
              </pre>
            )}
            {entryEditId === message.id && (
              <div className="chat-entry-edit">
                <textarea
                  value={entryEditText}
                  onChange={(event) => setEntryEditText(event.target.value)}
                  rows={Math.min(40, entryEditText.split("\n").length + 1)}
                  spellCheck={false}
                  disabled={entryEditBusy}
                />
                <div className="chat-entry-edit-actions">
                  <button type="button" onClick={toggleEntryEditFormat} disabled={entryEditBusy}>
                    {entryEditFormat === "json" ? "MeTTa" : "JSON"}
                  </button>
                  <button type="button" onClick={reloadEntryEdit} disabled={entryEditBusy}>
                    Reload
                  </button>
                  <button type="button" onClick={() => saveEntryEdit("in-place")} disabled={entryEditBusy}>
                    Save in-place
                  </button>
                  <button type="button" onClick={() => saveEntryEdit("at-end")} disabled={entryEditBusy}>
                    Save at-end
                  </button>
                  <button type="button" onClick={downloadEntryEdit} disabled={entryEditBusy}>
                    Save as..
                  </button>
                  <button type="button" onClick={() => setEntryEditId(null)} disabled={entryEditBusy}>
                    Close
                  </button>
                  {entryEditNote && <span className="chat-entry-edit-note">{entryEditNote}</span>}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      {errorText && <div className="chat-error">{errorText}</div>}
      <div className="chat-composer">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Message ${target}… (Enter to send, Shift+Enter for newline)`}
          rows={2}
          disabled={sending}
        />
        <button className="chat-send" onClick={send} disabled={sending || !input.trim()}>
          {sending ? "Sending…" : "Send"}
        </button>
      </div>
      <div className="chat-config">
        <div className="chat-config-head">
          <span className="chat-config-title">Channel config — {channelLabel(configChannel)}</span>
          <button type="button" onClick={fetchConfig} disabled={configBusy}>
            Reload
          </button>
          <button type="button" onClick={applyConfig} disabled={configBusy || !configText.trim()}>
            {configBusy ? "Applying…" : "Apply"}
          </button>
        </div>
        <textarea
          className="chat-config-editor"
          value={configText}
          onChange={(event) => setConfigText(event.target.value)}
          rows={8}
          spellCheck={false}
          aria-label="Channel config JSON"
        />
        {configError && <div className="chat-error">{configError}</div>}
        {configNote && <div className="chat-config-note">{configNote}</div>}
      </div>
    </div>
  );
}
