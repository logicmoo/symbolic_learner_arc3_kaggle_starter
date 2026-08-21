import { useCallback, useEffect, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from "react";
import { MarkdownDocument } from "./MarkdownDocument";
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
export type AgentOption = { id: string };

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

  const fetchMessages = useCallback(async () => {
    try {
      const query = `channel=${encodeURIComponent(channel)}&limit=300`;
      const payload = await readJson(await fetch(`/api/mailbox/messages?${query}`));
      setMessages((payload.messages as ChatMessage[]) || []);
      setReady(true);
      setErrorText("");
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorText(message);
      onError?.(message);
    }
  }, [channel, onError]);

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
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorText(message);
      onError?.(message);
    } finally {
      setSending(false);
    }
  }, [input, sending, target, you, sendChannel, fetchMessages, onError]);

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

  // Selects need the current value present as an option even before lists load.
  const agentChoices = Array.from(new Set([you, target, ...agents.map((a) => a.id)].filter(Boolean)));
  const channelChoices = Array.from(new Set([channel, ...channels.map((c) => c.id)].filter(Boolean)));
  const sendChoices = Array.from(new Set([sendChannel, ...channels.map((c) => c.id)].filter(Boolean)));

  // Channel options carry a readable name resolved from the identifier directory
  // (bootstrapped onto server_registry), so opaque bridge ids get annotated.
  const channelNames = new Map(channels.map((c) => [c.id, c.name] as const));
  const channelLabel = (id: string) => {
    const name = channelNames.get(id);
    return name && name !== id ? `${name} · ${id}` : id;
  };

  return (
    <div className={`chat-conversation ${className ?? ""}`.trim()}>
      {showChannelPicker && (
        <div className="chat-controls">
          <label className="chat-control">
            <span>You</span>
            <select value={you} onChange={(event) => setYou(event.target.value)} aria-label="Your agent identity">
              {agentChoices.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </label>
          <label className="chat-control">
            <span>To</span>
            <select value={target} onChange={(event) => setTarget(event.target.value)} aria-label="Addressed agent">
              {agentChoices.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </label>
          <label className="chat-control">
            <span>Channel</span>
            <select value={channel} onChange={(event) => selectChannel(event.target.value)} aria-label="Viewed channel">
              {channelChoices.map((id) => (
                <option key={id} value={id}>{channelLabel(id)}</option>
              ))}
            </select>
          </label>
          <label className="chat-control">
            <span>Send-to</span>
            <select value={sendChannel} onChange={(event) => setSendChannel(event.target.value)} aria-label="Send channel">
              <option value="">(none)</option>
              {sendChoices.map((id) => (
                <option key={id} value={id}>{channelLabel(id)}</option>
              ))}
            </select>
          </label>
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
        </div>
      )}
      <div className="chat-messages" ref={listRef} onScroll={handleScroll}>
        {ready && messages.length === 0 && (
          <div className="chat-empty">No messages on this channel yet.</div>
        )}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`chat-message ${message.from === you ? "mine" : "theirs"}`}
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
            {(expanded[message.id] ?? !message.text) && (
              <pre className="chat-message-json">
                {JSON.stringify(message.raw ?? message, null, 2)}
              </pre>
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
