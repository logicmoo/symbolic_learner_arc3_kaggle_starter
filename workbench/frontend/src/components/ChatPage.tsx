import {
  ChatConversation,
  DEFAULT_CHAT_USER,
  DEFAULT_CHAT_PEER,
} from "./ChatConversation";
import "../styles/chat.css";

// Full-page chat surface. The YOU / TO / CHANNEL / SEND-TO controls live in the
// shared ChatConversation, so the page is just a titled wrapper around it.
export function ChatPage() {
  return (
    <section className="chat-page">
      <header className="chat-page-header">
        <div className="chat-page-title">
          <h1>Chat</h1>
          <p>
            Talk over the shared mailbox. Pick who you are (YOU) and who you address (TO)
            from the agents, the channel to view (CHANNEL) and post into (SEND-TO) from the
            channels — all editable, and any message can be inspected as raw JSON.
          </p>
        </div>
      </header>
      <ChatConversation
        user={DEFAULT_CHAT_USER}
        peer={DEFAULT_CHAT_PEER}
        className="chat-page-conversation"
      />
    </section>
  );
}
