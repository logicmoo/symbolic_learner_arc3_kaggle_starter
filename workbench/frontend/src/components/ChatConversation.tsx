import { useCallback, useEffect, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from "react";
import { MarkdownDocument } from "./MarkdownDocument";
import "../styles/chat.css";

// The workbench user identity and the agent they talk to. Both sides of this pair
// are read back from the shared mailbox, so the same component renders the whole
// two-way conversation.
export const DEFAULT_CHAT_USER = "symbolic-workbench-user";
export const DEFAULT_CHAT_PEER = "github-copilot-facilitator-agent";

export type ChatMessage = {
  id: string;
  timestamp?: string;
  from?: string;
  to?: string;
  text: string;
  type?: string;
};

export type ChannelOption = { id: string; kind?: string; messages?: number };

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
// The mailbox is the source of truth: every poll replaces the visible thread with
// the server's recent history, and sending simply refetches so the new message
// appears once it has been persisted.
export function ChatConversation({
  user = DEFAULT_CHAT_USER,
  peer = DEFAULT_CHAT_PEER,
  className,
  pollMs = 3000,
  showChannelPicker = true,
  onError,
}: Props) {
  const [channel, setChannel] = useState(peer);
  const [channels, setChannels] = useState<ChannelOption[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [ready, setReady] = useState(false);
  const [errorText, setErrorText] = useState("");
  const listRef = useRef<HTMLDivElement | null>(null);
  const stickBottomRef = useRef(true);

  const fetchChannels = useCallback(async () => {
    try {
      const payload = await readJson(await fetch("/api/mailbox/channels"));
      setChannels((payload.channels as ChannelOption[]) || []);
    } catch {
      // The channel list is best-effort; keep whatever we already have.
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
    fetchChannels();
    const timer = window.setInterval(fetchChannels, 15000);
    return () => window.clearInterval(timer);
  }, [fetchChannels]);

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
      await readJson(
        await fetch("/api/mailbox/send", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, to: channel, sender: user }),
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
  }, [input, sending, channel, user, fetchMessages, onError]);

  const handleKeyDown = (event: ReactKeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      send();
    }
  };

  // Keep the active channel selectable even before the list has loaded it.
  const channelOptions = channels.some((option) => option.id === channel)
    ? channels
    : [{ id: channel, kind: "mailbox" } as ChannelOption, ...channels];

  return (
    <div className={`chat-conversation ${className ?? ""}`.trim()}>
      {showChannelPicker && (
        <div className="chat-channelbar">
          <label>
            <span>Channel</span>
            <select
              value={channel}
              onChange={(event) => setChannel(event.target.value)}
              aria-label="Mailbox channel"
            >
              {channelOptions.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.id}
                  {option.messages ? ` (${option.messages})` : ""}
                </option>
              ))}
            </select>
          </label>
        </div>
      )}
      <div className="chat-messages" ref={listRef} onScroll={handleScroll}>
        {ready && messages.length === 0 && (
          <div className="chat-empty">No messages on this channel yet.</div>
        )}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`chat-message ${message.from === user ? "mine" : "theirs"}`}
          >
            <div className="chat-message-meta">
              <span className="chat-message-from">{message.from}</span>
              {message.timestamp && (
                <span className="chat-message-time">{formatTime(message.timestamp)}</span>
              )}
            </div>
            <MarkdownDocument className="chat-message-body" content={message.text || ""} />
          </div>
        ))}
      </div>
      {errorText && <div className="chat-error">{errorText}</div>}
      <div className="chat-composer">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Message ${channel}… (Enter to send, Shift+Enter for newline)`}
          rows={2}
          disabled={sending}
        />
        <button className="chat-send" onClick={send} disabled={sending || !input.trim()}>
          {sending ? "Sending…" : "Send"}
        </button>
      </div>
    </div>
  );
}
