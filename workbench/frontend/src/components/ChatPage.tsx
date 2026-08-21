import { useState } from "react";
import {
  ChatConversation,
  DEFAULT_CHAT_USER,
  DEFAULT_CHAT_PEER,
} from "./ChatConversation";
import "../styles/chat.css";

// Full-page chat surface. It reuses the shared ChatConversation (which carries the
// channel picker) and adds a small identity bar so the operator can change who
// they send as on the shared mailbox bus.
export function ChatPage() {
  const [user, setUser] = useState(DEFAULT_CHAT_USER);
  const [draftUser, setDraftUser] = useState(DEFAULT_CHAT_USER);

  return (
    <section className="chat-page">
      <header className="chat-page-header">
        <div className="chat-page-title">
          <h1>Chat</h1>
          <p>
            Talk to the workbench agent over the shared mailbox. Pick any mailbox channel
            from the dropdown; messages render with full Markdown, like the assistant
            transcript.
          </p>
        </div>
        <form
          className="chat-identities"
          onSubmit={(event) => {
            event.preventDefault();
            setUser(draftUser.trim() || DEFAULT_CHAT_USER);
          }}
        >
          <label>
            <span>You</span>
            <input
              value={draftUser}
              onChange={(event) => setDraftUser(event.target.value)}
              aria-label="Your mailbox identity"
            />
          </label>
          <button type="submit">Apply</button>
        </form>
      </header>
      <ChatConversation
        key={user}
        user={user}
        peer={DEFAULT_CHAT_PEER}
        className="chat-page-conversation"
      />
    </section>
  );
}
