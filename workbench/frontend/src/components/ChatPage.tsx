import { useEffect, useState } from "react";
import {
  ChatConversation,
  DEFAULT_CHAT_USER,
  DEFAULT_CHAT_PEER,
} from "./ChatConversation";
import { MarkdownDocument } from "./MarkdownDocument";
import "../styles/chat.css";

// Full-page chat surface. The YOU / TO / MAILBOX / SEND-TO controls live in the
// shared ChatConversation, so the page is just a titled wrapper around it plus
// the Help panel (docs/CHAT_PAGE.md) toggled from the top banner.
export function ChatPage() {
  const [helpOpen, setHelpOpen] = useState(true);
  const [helpText, setHelpText] = useState("");
  const [helpError, setHelpError] = useState("");

  useEffect(() => {
    if (!helpOpen || helpText || helpError) return;
    let cancelled = false;
    fetch("/api/repository/markdown?path=docs/CHAT_PAGE.md")
      .then(async (response) => {
        const payload = (await response.json()) as Record<string, unknown>;
        if (!response.ok) throw new Error(String(payload.error || payload.detail || response.statusText));
        if (!cancelled) setHelpText(String(payload.content || ""));
      })
      .catch((reason) => {
        if (!cancelled) setHelpError(String(reason));
      });
    return () => {
      cancelled = true;
    };
  }, [helpOpen, helpText, helpError]);

  return (
    <section className="chat-page">
      <header className="chat-page-header">
        <div className="chat-page-title">
          <div className="chat-page-title-row">
            <h1>Chat</h1>
            <button
              type="button"
              className={`chat-page-help-toggle${helpOpen ? " active" : ""}`}
              aria-pressed={helpOpen}
              onClick={() => setHelpOpen((v) => !v)}
            >
              {helpOpen ? "✕ Help" : "? Help"}
            </button>
          </div>
          <p>
            Talk over the shared mailbox. Pick who you are (YOU) and who you address (TO)
            from the agents, the mailbox to view (MAILBOX) and post into (SEND-TO) from the
            mailboxes — all editable, and any message can be inspected as raw JSON. The
            require-match bar filters the whole log: only depressed fields must match.
          </p>
        </div>
      </header>
      <div className="chat-page-body">
        <ChatConversation
          user={DEFAULT_CHAT_USER}
          peer={DEFAULT_CHAT_PEER}
          className="chat-page-conversation"
        />
        {helpOpen && (
          <aside className="chat-page-help">
            <MarkdownDocument
              content={helpError ? `> **Help failed to load:** ${helpError}` : helpText || "Loading help…"}
            />
          </aside>
        )}
      </div>
    </section>
  );
}
