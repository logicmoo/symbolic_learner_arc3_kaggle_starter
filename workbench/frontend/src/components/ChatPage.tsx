import { useState } from "react";
import {
  ChatConversation,
  DEFAULT_CHAT_USER,
  DEFAULT_CHAT_PEER,
} from "./ChatConversation";
import "../styles/chat.css";

// Full-page chat surface. It reuses the shared ChatConversation and adds an
// identity bar so the operator can retarget which agent they are talking to on
// the shared mailbox bus.
export function ChatPage() {
  const [user, setUser] = useState(DEFAULT_CHAT_USER);
  const [peer, setPeer] = useState(DEFAULT_CHAT_PEER);
  const [draftUser, setDraftUser] = useState(DEFAULT_CHAT_USER);
  const [draftPeer, setDraftPeer] = useState(DEFAULT_CHAT_PEER);

  return (
    <section className="chat-page">
      <header className="chat-page-header">
        <div className="chat-page-title">
          <h1>Chat</h1>
          <p>
            Talk to the workbench agent over the shared mailbox. Messages render with full
            Markdown, exactly like the assistant transcript.
          </p>
        </div>
        <form
          className="chat-identities"
          onSubmit={(event) => {
            event.preventDefault();
            setUser(draftUser.trim() || DEFAULT_CHAT_USER);
            setPeer(draftPeer.trim() || DEFAULT_CHAT_PEER);
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
          <label>
            <span>Peer</span>
            <input
              value={draftPeer}
              onChange={(event) => setDraftPeer(event.target.value)}
              aria-label="Peer mailbox identity"
            />
          </label>
          <button type="submit">Apply</button>
        </form>
      </header>
      <ChatConversation
        key={`${user}:${peer}`}
        user={user}
        peer={peer}
        className="chat-page-conversation"
      />
    </section>
  );
}
