import { useCallback, useEffect, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import {
  ChatConversation,
  DEFAULT_CHAT_USER,
  DEFAULT_CHAT_PEER,
} from "./ChatConversation";
import "../styles/chat.css";

// Any part of the workbench can pop the mini-chat open by dispatching this event.
export const OPEN_CHAT_DOCK_EVENT = "workbench:open-chat-dock";

type Props = {
  onOpenFullPage?: () => void;
  user?: string;
  peer?: string;
};

const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));

// A floatable, draggable, resizable mini version of the Chat page. When closed it
// collapses to a launcher bubble that is always available from any view.
export function ChatDock({
  onOpenFullPage,
  user = DEFAULT_CHAT_USER,
  peer = DEFAULT_CHAT_PEER,
}: Props) {
  const [open, setOpen] = useState(false);
  const [position, setPosition] = useState(() => ({
    x: Math.max(24, window.innerWidth - 392),
    y: Math.max(24, window.innerHeight - 540),
  }));
  const [size, setSize] = useState({ width: 360, height: 468 });
  const [mode, setMode] = useState<null | "drag" | "resize">(null);
  const originRef = useRef({ px: 0, py: 0, x: 0, y: 0, width: 0, height: 0 });

  useEffect(() => {
    const openHandler = () => setOpen(true);
    window.addEventListener(OPEN_CHAT_DOCK_EVENT, openHandler);
    return () => window.removeEventListener(OPEN_CHAT_DOCK_EVENT, openHandler);
  }, []);

  useEffect(() => {
    if (!mode) return;
    const onMove = (event: PointerEvent) => {
      const origin = originRef.current;
      if (mode === "drag") {
        setPosition({
          x: clamp(origin.x + event.clientX - origin.px, 0, window.innerWidth - 120),
          y: clamp(origin.y + event.clientY - origin.py, 0, window.innerHeight - 48),
        });
      } else {
        setSize({
          width: clamp(origin.width + event.clientX - origin.px, 288, window.innerWidth - 32),
          height: clamp(origin.height + event.clientY - origin.py, 280, window.innerHeight - 32),
        });
      }
    };
    const onUp = () => setMode(null);
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
  }, [mode]);

  const startDrag = useCallback(
    (event: ReactPointerEvent<HTMLDivElement>) => {
      originRef.current = {
        ...originRef.current,
        px: event.clientX,
        py: event.clientY,
        x: position.x,
        y: position.y,
      };
      setMode("drag");
    },
    [position.x, position.y],
  );

  const startResize = useCallback(
    (event: ReactPointerEvent<HTMLDivElement>) => {
      event.stopPropagation();
      originRef.current = {
        ...originRef.current,
        px: event.clientX,
        py: event.clientY,
        width: size.width,
        height: size.height,
      };
      setMode("resize");
    },
    [size.width, size.height],
  );

  if (!open) {
    return (
      <button
        className="chat-dock-launcher"
        title="Open chat"
        aria-label="Open chat"
        onClick={() => setOpen(true)}
      >
        <span aria-hidden="true">✉</span>
      </button>
    );
  }

  return (
    <div
      className="chat-dock"
      style={{ left: position.x, top: position.y, width: size.width, height: size.height }}
    >
      <div className="chat-dock-header" onPointerDown={startDrag}>
        <span className="chat-dock-title">Chat · {peer}</span>
        <div className="chat-dock-actions">
          {onOpenFullPage && (
            <button
              title="Open full chat page"
              aria-label="Open full chat page"
              onClick={onOpenFullPage}
            >
              ⤢
            </button>
          )}
          <button title="Close chat" aria-label="Close chat" onClick={() => setOpen(false)}>
            ×
          </button>
        </div>
      </div>
      <ChatConversation user={user} peer={peer} className="chat-dock-conversation" />
      <div
        className="chat-dock-resize"
        onPointerDown={startResize}
        title="Drag to resize"
        aria-hidden="true"
      />
    </div>
  );
}
