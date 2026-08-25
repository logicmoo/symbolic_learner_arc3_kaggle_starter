import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties, type KeyboardEvent as ReactKeyboardEvent } from "react";
import { MarkdownDocument } from "./MarkdownDocument";
import { jsonDocumentToMetta, mettaDocumentToJson } from "../lib/mettaResourceCodec";
import "../styles/chat.css";

// The workbench user identity and the agent they talk to. Both sides of this pair
// are read back from the shared mailbox, so the same component renders the whole
// two-way conversation.
export const DEFAULT_CHAT_USER = "symbolic-workbench-user";
export const DEFAULT_CHAT_PEER = "symbolic-workbench-user";

// Fields the user can organize (place/color) messages by. This base set always
// shows; any additional primitive-valued keys seen on messages (or their raw
// record) are added dynamically as new traffic arrives — the current choice is
// never changed when the list grows.
const ORGANIZE_BASE = ["from", "to", "type", "author", "mailboxName"] as const;
const ORGANIZE_SKIP = new Set(["id", "text", "raw", "timestamp", "mailboxId", "authorName"]);
const FIELD_LABELS: Record<string, string> = { mailboxName: "mailbox" };

export type ChatMessage = {
  id: string;
  timestamp?: string;
  from?: string;
  to?: string;
  text: string;
  type?: string;
  mailboxId?: string | null;
  author?: string | null;
  authorName?: string | null;
  mailboxName?: string | null;
  raw?: unknown;
};

export type MailboxOption = { id: string; kind?: string; messages?: number; name?: string | null; global_name?: string | null };

type CursorInfo = {
  mailbox: string;
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
  showMailboxPicker?: boolean;
  onError?: (message: string) => void;
  initialInput?: string;
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
// Four editable combos drive it: YOU/TO pick agents, MAILBOX (view) and SEND-TO
// (send_to) pick mailboxes. YOU/TO are enumerated with first-class agents; the
// mailbox combos list the mailbox documents. Every message carries its raw
// record so it can be inspected as JSON.
export function ChatConversation({
  user = DEFAULT_CHAT_USER,
  peer = DEFAULT_CHAT_PEER,
  className,
  pollMs = 3000,
  showMailboxPicker = true,
  onError,
  initialInput = "",
}: Props) {
  const [you, setYou] = useState(user);
  const [mailbox, setMailbox] = useState(peer);
  const [mergeMailboxes, setMergeMailboxes] = useState<string[]>([]);
  const [mergeMode, setMergeMode] = useState<"by-timestamp" | "sequential">("by-timestamp");
  // Message placement: fixed side, or "field" = each distinct value of the chosen
  // field gets its own lane (assigned left/right/center/full as it first appears).
  // Default: lane by stream name — the first stream seen justifies left.
  const [placement, setPlacement] = useState<"sender" | "left" | "right" | "center" | "full" | "field">("field");
  const [placementField, setPlacementField] = useState<string>("mailboxName");
  // Message color has two independent channels — the bubble border and the fill —
  // each "by sender", a uniform tint, or "field" (each distinct value gets a hue).
  const [borderMode, setBorderMode] = useState<"sender" | "uniform" | "field">("sender");
  const [borderField, setBorderField] = useState<string>("mailboxName");
  const [fillMode, setFillMode] = useState<"sender" | "uniform" | "field">("sender");
  const [fillField, setFillField] = useState<string>("from");
  // Layout & color options are tucked behind a collapsible header (collapsed by default).
  const [showDisplay, setShowDisplay] = useState(false);
  const [target, setTarget] = useState(peer);
  const [sendMailbox, setSendMailbox] = useState("");
  const [agents, setAgents] = useState<AgentOption[]>([]);
  const [mailboxes, setMailboxes] = useState<MailboxOption[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [input, setInput] = useState(initialInput);
  useEffect(() => {
    if (initialInput) setInput(initialInput);
  }, [initialInput]);
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
  const [inspect, setInspect] = useState<{ label: string; id: string; kind: "agent" | "mailbox" } | null>(null);
  const [inspectText, setInspectText] = useState("");
  const [inspectNote, setInspectNote] = useState("");
  const [inspectBusy, setInspectBusy] = useState(false);
  const [entryEditKey, setEntryEditKey] = useState<string | null>(null);
  const [entryEditId, setEntryEditId] = useState<string | null>(null);
  const [entryEditText, setEntryEditText] = useState("");
  const [entryEditFormat, setEntryEditFormat] = useState<"json" | "metta">("json");
  const [entryEditNote, setEntryEditNote] = useState("");
  const [entryEditBusy, setEntryEditBusy] = useState(false);
  // Require-match bar: the list looks EVERYWHERE in the log; each depressed
  // button ANDs its picker's value in as a required match. Only MAILBOX is
  // required by default (classic mailbox view).
  const [requireTo, setRequireTo] = useState(false);
  const [requireFrom, setRequireFrom] = useState(false);
  const [requireMailbox, setRequireMailbox] = useState(true);
  const [requireSendTo, setRequireSendTo] = useState(false);
  const [requireText, setRequireText] = useState(false);
  const [textExpr, setTextExpr] = useState("");
  const [textQuery, setTextQuery] = useState("");
  const listRef = useRef<HTMLDivElement | null>(null);
  const stickBottomRef = useRef(true);

  // The config editor tracks the mailbox messages are sent on (SEND-TO mailbox if
  // set, otherwise the viewed mailbox).
  const configMailbox = sendMailbox || mailbox;

  // Switching the viewed mailbox re-points addressing to it by default; the "To"
  // field can then be overridden to address anyone independently.
  const selectMailbox = useCallback((next: string) => {
    setMailbox(next);
    setTarget(next);
  }, []);

  const fetchDirectory = useCallback(async () => {
    try {
      const [agentPayload, mailboxPayload] = await Promise.all([
        readJson(await fetch("/ws_collab/v1/mailbox/agents")),
        readJson(await fetch("/ws_collab/v1/mailbox/mailboxes")),
      ]);
      setAgents((agentPayload.agents as AgentOption[]) || []);
      setMailboxes((mailboxPayload.mailboxes as MailboxOption[]) || []);
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
      const viewed = Array.from(new Set([mailbox, ...mergeMailboxes].filter(Boolean)));
      const buildParams = (mb: string) => {
        const params = new URLSearchParams({ filter: "1", limit: "300" });
        if (requireTo && target) params.set("to", target);
        if (requireFrom && you) params.set("from", you);
        if (requireMailbox && mb) params.set("mailbox", mb);
        if (requireSendTo && sendMailbox) params.set("send_to", sendMailbox);
        if (requireText && textQuery) params.set("text", textQuery);
        return params;
      };
      const batches = await Promise.all(
        viewed.map(async (mb) => {
          const payload = await readJson(await fetch(`/ws_collab/v1/mailbox/messages?${buildParams(mb).toString()}`));
          const msgs = (payload.messages as ChatMessage[]) || [];
          // Tag each message with the stream it came from so placement/color can
          // lane by stream name regardless of what the server stamped.
          return msgs.map((m) => ({ ...m, mailboxId: mb, mailboxName: mb }));
        }),
      );
      let merged = batches.flat();
      if (viewed.length > 1) {
        const seen = new Set<string>();
        merged = merged.filter((message) => {
          if (!message.id) return true;
          if (seen.has(message.id)) return false;
          seen.add(message.id);
          return true;
        });
        if (mergeMode === "by-timestamp") {
          merged.sort((a, b) => String(a.timestamp || "").localeCompare(String(b.timestamp || "")));
        }
      }
      setMessages(merged);
      setReady(true);
      setErrorText("");
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorText(message);
      onError?.(message);
    }
  }, [
    mailbox, mergeMailboxes, mergeMode, you, target, sendMailbox,
    requireTo, requireFrom, requireMailbox, requireSendTo, requireText, textQuery,
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
      const routed = sendMailbox.trim() || mailbox;
      if (routed) body.send_to = routed;
      await readJson(
        await fetch("/ws_collab/v1/mailbox/send", {
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
  }, [input, sending, target, you, sendMailbox, fetchMessages, fetchDirectory, onError]);

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
        await fetch("/ws_collab/v1/mailbox/agents", {
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

  const makeMailbox = useCallback(async () => {
    const id = newEntry.trim();
    if (!id) return;
    try {
      await readJson(
        await fetch("/ws_collab/v1/mailbox/mailboxes", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id }),
        }),
      );
      setMailboxes((prev) => (prev.some((c) => c.id === id) ? prev : [...prev, { id, kind: "mailbox" }]));
      setMailbox(id);
      setTarget(id);
      setSendMailbox(id);
      setNewEntry("");
      fetchDirectory();
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorText(message);
      onError?.(message);
    }
  }, [newEntry, fetchDirectory, onError]);

  // "Save as stream": promote the current merge combo (primary + merge rows) into
  // a durable server-side virtual merge mailbox that anyone can then consume.
  const saveMerge = useCallback(async () => {
    const seen = new Set<string>();
    const parts: string[] = [];
    for (const raw of [mailbox, ...mergeMailboxes]) {
      const v = (raw || "").trim();
      if (v && !seen.has(v)) {
        seen.add(v);
        parts.push(v);
      }
    }
    if (parts.length < 2) {
      setErrorText("Add at least one more mailbox before saving the merge as a stream.");
      return;
    }
    const suggested = `merge-${parts[0]}`.slice(0, 60).replace(/[^A-Za-z0-9._-]/g, "-");
    const name = (window.prompt("Save this merged view as a new virtual stream named:", suggested) || "").trim();
    if (!name) return;
    try {
      await readJson(
        await fetch("/ws_collab/v1/mailbox/create", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: name, source: `merge:${parts.join(",")}`, purpose: `merge of ${parts.join(", ")}` }),
        }),
      );
      await fetchDirectory();
      setMergeMailboxes([]);
      setMailbox(name);
      setTarget(name);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorText(message);
      onError?.(message);
    }
  }, [mailbox, mergeMailboxes, fetchDirectory, onError]);

  // Assign a placement lane (pos-left/right/center/full) to each distinct value of
  // the chosen field, in order of first appearance, cycling through the four lanes.
  // Read a field off a message, falling back to its raw record so newly-appearing
  // fields (that only live in raw) are still organizable.
  const fieldValue = useCallback((m: ChatMessage, field: string): string => {
    const rec = m as unknown as Record<string, unknown>;
    const top = rec[field];
    if (top !== undefined && top !== null && top !== "") return String(top);
    const raw = rec.raw;
    if (raw && typeof raw === "object") {
      const rv = (raw as Record<string, unknown>)[field];
      if (rv !== undefined && rv !== null) return String(rv);
    }
    return "";
  }, []);

  // The union of organizable fields: the base set plus any primitive-valued keys
  // discovered on the current messages (or their raw records), sorted for stability.
  const availableFields = useMemo(() => {
    const set = new Set<string>(ORGANIZE_BASE);
    const consider = (k: string, v: unknown) => {
      if (ORGANIZE_SKIP.has(k) || v === null || v === undefined || typeof v === "object") return;
      set.add(k);
    };
    for (const m of messages) {
      const rec = m as unknown as Record<string, unknown>;
      for (const k of Object.keys(rec)) consider(k, rec[k]);
      const raw = rec.raw;
      if (raw && typeof raw === "object") {
        for (const [k, v] of Object.entries(raw as Record<string, unknown>)) consider(k, v);
      }
    }
    const base = ORGANIZE_BASE as readonly string[];
    const extras = [...set].filter((k) => !base.includes(k)).sort();
    return [...base, ...extras];
  }, [messages]);

  // Render <option>s for a field picker, always including the current value even
  // if it hasn't been discovered yet (so growing the list never resets the choice).
  const fieldOptions = (current: string) =>
    (availableFields.includes(current) ? availableFields : [current, ...availableFields]).map((f) => (
      <option key={f} value={f}>
        {FIELD_LABELS[f] ?? f}
      </option>
    ));

  const fieldPlacement = useMemo(() => {
    const map = new Map<string, string>();
    if (placement !== "field") return map;
    const cycle = ["pos-left", "pos-right", "pos-center", "pos-full"];
    const assign = (key: string) => {
      if (!map.has(key)) map.set(key, cycle[map.size % cycle.length]);
    };
    // Seed lanes in stream order so the first (viewed) stream justifies left,
    // then the merge rows, before falling back to message order for other fields.
    if (placementField === "mailboxName") {
      for (const mb of [mailbox, ...mergeMailboxes].filter(Boolean)) assign(String(mb));
    }
    for (const m of messages) {
      assign(fieldValue(m, placementField));
    }
    return map;
  }, [messages, placement, placementField, mailbox, mergeMailboxes, fieldValue]);

  const placementClass = useCallback(
    (m: ChatMessage): string => {
      switch (placement) {
        case "left":
          return "pos-left";
        case "right":
          return "pos-right";
        case "center":
          return "pos-center";
        case "full":
          return "pos-full";
        case "field":
          return fieldPlacement.get(fieldValue(m, placementField)) || "";
        default:
          return "";
      }
    },
    [placement, placementField, fieldPlacement, fieldValue],
  );

  // Same idea for color: each distinct value of the chosen field gets a hue, in
  // order of first appearance (stream-seeded for the mailbox field), cycling
  // through a fixed palette. Border and fill are computed independently.
  const COLOR_HUES = [200, 280, 20, 140, 330, 50, 100, 250, 0, 170];
  const buildHueIndex = useCallback(
    (active: boolean, field: string) => {
      const map = new Map<string, number>();
      if (!active) return map;
      const put = (k: string) => {
        if (!map.has(k)) map.set(k, map.size);
      };
      if (field === "mailboxName") {
        for (const mb of [mailbox, ...mergeMailboxes].filter(Boolean)) put(String(mb));
      }
      for (const m of messages) put(fieldValue(m, field));
      return map;
    },
    [messages, mailbox, mergeMailboxes, fieldValue],
  );
  const borderHueIndex = useMemo(
    () => buildHueIndex(borderMode === "field", borderField),
    [buildHueIndex, borderMode, borderField],
  );
  const fillHueIndex = useMemo(
    () => buildHueIndex(fillMode === "field", fillField),
    [buildHueIndex, fillMode, fillField],
  );

  const messageColorStyle = useCallback(
    (m: ChatMessage): CSSProperties | undefined => {
      const style: CSSProperties = {};
      if (borderMode === "uniform") {
        style.borderColor = "var(--line)";
      } else if (borderMode === "field") {
        const idx = borderHueIndex.get(fieldValue(m, borderField)) ?? 0;
        style.borderColor = `hsl(${COLOR_HUES[idx % COLOR_HUES.length]} 65% 58%)`;
      }
      if (fillMode === "uniform") {
        style.background = "var(--panel2)";
      } else if (fillMode === "field") {
        const idx = fillHueIndex.get(fieldValue(m, fillField)) ?? 0;
        style.background = `hsl(${COLOR_HUES[idx % COLOR_HUES.length]} 60% 45% / 0.16)`;
      }
      return style.borderColor || style.background ? style : undefined;
    },
    [borderMode, borderField, borderHueIndex, fillMode, fillField, fillHueIndex, fieldValue],
  );

  // Messages without text default to the JSON view; the toggle flips from the effective state.
  const toggleRaw = (id: string, defaultOpen = false) =>
    setExpanded((prev) => ({ ...prev, [id]: !(prev[id] ?? defaultOpen) }));

  // Per-entry ✎ editor: the bubble becomes the editor. Save posts the COMPLETE
  // record to /ws_collab/v1/mailbox/record, either rewriting its log line (in-place) or
  // appending the edit as the newest record and marking the old one
  // replaced-by: entry_<n> (at-end). Like the other JSON editors it has a
  // MeTTa mode (mettaResourceCodec), Reload discards edits, Save as..
  // downloads to disk. Config-entry versions share an id, so bubbles are
  // keyed id|timestamp while saves target the id (last line out wins).
  const bubbleKey = (message: ChatMessage) => `${message.id}|${message.timestamp || ""}`;

  const closeEntryEdit = () => {
    setEntryEditKey(null);
    setEntryEditId(null);
  };

  const openEntryEdit = (message: ChatMessage) => {
    if (entryEditKey === bubbleKey(message)) {
      closeEntryEdit();
      return;
    }
    setEntryEditKey(bubbleKey(message));
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
    const message = messages.find((entry) => bubbleKey(entry) === entryEditKey);
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
        await fetch("/ws_collab/v1/mailbox/record", {
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
    if (!configMailbox) {
      setConfigText("");
      return;
    }
    try {
      const payload = await readJson(
        await fetch(`/ws_collab/v1/mailbox/mailbox-config?mailbox=${encodeURIComponent(configMailbox)}`),
      );
      setConfigText(JSON.stringify(payload.config ?? {}, null, 2));
      setConfigError("");
      setConfigNote("");
    } catch (error) {
      setConfigError(error instanceof Error ? error.message : String(error));
    }
  }, [configMailbox]);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  // Apply = subscribe any new names in `subscribers`, then persist the whole
  // edited config as a mailbox config record on server_identifiers_registry.
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
        await fetch("/ws_collab/v1/mailbox/mailbox-config", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mailbox: configMailbox, config: parsed }),
        }),
      );
      setConfigText(JSON.stringify(payload.config ?? parsed, null, 2));
      const subscribed = (payload.subscribed as string[]) || [];
      setConfigNote(
        `Stored on server_identifiers_registry${subscribed.length ? `; subscribed: ${subscribed.join(", ")}` : ""}`,
      );
      setConfigError("");
    } catch (error) {
      setConfigError(error instanceof Error ? error.message : String(error));
    } finally {
      setConfigBusy(false);
    }
  }, [configMailbox, configText]);

  // Cursor control: while looking at a mailbox with "To" set to an agent, show
  // where that agent's cursor sits on the mailbox and allow repositioning it.
  const fetchCursor = useCallback(async () => {
    if (!mailbox || !target) {
      setCursorInfo(null);
      return;
    }
    try {
      const query = `mailbox=${encodeURIComponent(mailbox)}&agent=${encodeURIComponent(target)}`;
      const payload = await readJson(await fetch(`/ws_collab/v1/mailbox/cursor?${query}`));
      setCursorInfo(payload as CursorInfo);
    } catch {
      setCursorInfo(null);
    }
  }, [mailbox, target]);

  useEffect(() => {
    fetchCursor();
  }, [fetchCursor]);

  const moveCursor = useCallback(
    async (start: "beginning" | "now" | "remove", mb: string = mailbox) => {
      if (!mb || !target) return;
      setCursorBusy(true);
      try {
        const query = `mailbox=${encodeURIComponent(mb)}&agent=${encodeURIComponent(target)}`;
        const payload = await readJson(
          start === "remove"
            ? await fetch(`/ws_collab/v1/mailbox/cursor?${query}`, { method: "DELETE" })
            : await fetch("/ws_collab/v1/mailbox/cursor", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mailbox: mb, agent: target, start }),
              }),
        );
        if (mb === mailbox) setCursorInfo(payload as CursorInfo);
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        setErrorText(message);
        onError?.(message);
      } finally {
        setCursorBusy(false);
      }
    },
    [mailbox, target, onError],
  );

  // Subscription control: set/clear the explicit subscribed|unsubscribed intent
  // for the TO agent on the viewed mailbox ("remove" reverts to the default
  // inference where cursor holders count as subscribed).
  const setSubscription = useCallback(
    async (state: "subscribed" | "unsubscribed" | "remove") => {
      if (!mailbox || !target) return;
      setSubBusy(true);
      try {
        await readJson(
          await fetch("/ws_collab/v1/mailbox/subscription", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ agent: target, mailbox, state }),
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
    [mailbox, target, fetchDirectory, fetchCursor, onError],
  );

  // Selects need the current value present as an option even before lists load.
  // Clicking a picker label (YOU/TO/MAILBOX/SEND-TO) opens an editable JSON view
  // of whatever that picker points at; clicking the same label again hides it.
  // YOU/TO show the agent record as returned by /ws_collab/v1/mailbox/agents (cursors
  // included); the mailbox labels show the mailbox record. Save posts the edited
  // JSON to the server_registry_agents blackboard (agents are stored objects;
  // server channels are only a live view of what the IRC/Mattermost server says
  // we are on, not something stored here). Reload re-queries the record.
  const loadEntity = useCallback(async (kind: "agent" | "mailbox", id: string) => {
    const endpoint = kind === "agent" ? "/ws_collab/v1/mailbox/agents" : "/ws_collab/v1/mailbox/mailboxes";
    const payload = await readJson(await fetch(endpoint));
    const list = (payload[kind === "agent" ? "agents" : "mailboxes"] as Array<Record<string, unknown>>) || [];
    return list.find((item) => item.id === id) ?? { id };
  }, []);

  const inspectId = useCallback(
    (label: string, id: string) => {
      if (!id) return;
      if (inspect && inspect.label === label && inspect.id === id) {
        setInspect(null);
        return;
      }
      const kind = label === "YOU" || label === "TO" ? ("agent" as const) : ("mailbox" as const);
      const record =
        kind === "agent"
          ? agents.find((a) => a.id === id) ?? { id }
          : mailboxes.find((c) => c.id === id) ?? { id };
      setInspect({ label, id, kind });
      setInspectText(JSON.stringify(record, null, 2));
      setInspectNote("");
    },
    [inspect, agents, mailboxes],
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
        await fetch("/ws_collab/v1/mailbox/entity", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ kind: inspect.kind, id: inspect.id, entry: parsed }),
        }),
      );
      const record = (payload.entry as Record<string, unknown>) ?? parsed;
      setInspectText(JSON.stringify(record, null, 2));
      setInspectNote(`saved to ${String(payload.mailbox ?? "")}`.trim());
      void fetchDirectory();
    } catch (error) {
      setInspectNote(error instanceof Error ? error.message : String(error));
    } finally {
      setInspectBusy(false);
    }
  }, [inspect, inspectText, fetchDirectory]);

  // Cursor moves change what an open inspector shows (the agent's cursor map or
  // the mailbox's subscribers), so requery it when it points at the affected pair.
  useEffect(() => {
    if (!cursorInfo || !inspect) return;
    const affected =
      (inspect.kind === "agent" && inspect.id === cursorInfo.agent) ||
      (inspect.kind === "mailbox" && inspect.id === cursorInfo.mailbox);
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
  const mailboxChoices = Array.from(new Set([mailbox, ...mailboxes.map((c) => c.id)].filter(Boolean))).sort(alpha);
  const sendChoices = Array.from(new Set([sendMailbox, ...mailboxes.map((c) => c.id)].filter(Boolean))).sort(alpha);

  // Mailbox options carry a readable name resolved from the identifier directory
  // (bootstrapped onto server_identifiers_registry), so opaque bridge ids get
  // annotated, and show how many entries recent traffic holds for each mailbox.
  const mailboxNames = new Map(mailboxes.map((c) => [c.id, c.name] as const));
  const mailboxCounts = new Map(mailboxes.map((c) => [c.id, c.messages] as const));
  const mailboxGlobals = new Map(mailboxes.map((c) => [c.id, c.global_name] as const));
  // The TO agent's explicit subscription setting on the viewed mailbox (if any).
  const targetRecord = agents.find((a) => a.id === target) as Record<string, unknown> | undefined;
  const targetSubs = (targetRecord?.subscriptions ?? null) as Record<string, string> | null;
  const subSetting = targetSubs && mailbox in targetSubs ? targetSubs[mailbox] : null;
  const mailboxLabel = (id: string) => {
    const name = mailboxNames.get(id);
    const base = name && name !== id ? `${name} · ${id}` : id;
    const globalName = mailboxGlobals.get(id);
    const withGlobal = globalName && globalName !== id ? `${base} · ${globalName}` : base;
    const count = mailboxCounts.get(id);
    return typeof count === "number" ? `${withGlobal} · ${count}` : withGlobal;
  };

  return (
    <div className={`chat-conversation ${className ?? ""}`.trim()}>
      {showMailboxPicker && (
        <div className="chat-controls">
          <label className="chat-control">
            <button type="button" className="chat-label" onClick={() => void inspectId("YOU", you)}>You/From</button>
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
            <button type="button" className="chat-label" onClick={() => void inspectId("SEND-TO", sendMailbox)}>Send-to</button>
            <select value={sendMailbox} onChange={(event) => setSendMailbox(event.target.value)} aria-label="Send mailbox">
              <option value="">(none)</option>
              {sendChoices.map((id) => (
                <option key={id} value={id}>{mailboxLabel(id)}</option>
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
              className={`chat-require-btn${requireMailbox ? " active" : ""}`}
              aria-pressed={requireMailbox}
              title="Require the record to involve the MAILBOX picker (from, to or send_to)"
              onClick={() => setRequireMailbox((v) => !v)}
            >
              MAILBOX
            </button>
            <button
              type="button"
              className={`chat-require-btn${requireSendTo ? " active" : ""}`}
              aria-pressed={requireSendTo}
              title="Require record.send_to to equal the SEND-TO picker"
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
          <label className="chat-control chat-mbrow">
            <button type="button" className="chat-label" onClick={() => void inspectId("MAILBOX", mailbox)}>Mailbox</button>
            <select value={mailbox} onChange={(event) => selectMailbox(event.target.value)} aria-label="Viewed mailbox">
              {mailboxChoices.map((id) => (
                <option key={id} value={id}>{mailboxLabel(id)}</option>
              ))}
            </select>
            <span className="chat-mbrow-actions">
              {target && (
                <span className="chat-mbrow-cursor" title={`Cursor for ${target} on this mailbox`}>
                  {cursorInfo
                    ? cursorInfo.initialized
                      ? `▸${cursorInfo.entry_next ?? "?"}/${cursorInfo.entries_total ?? "?"}`
                      : "no cursor"
                    : "…"}
                </span>
              )}
              <button type="button" className="chat-mbact" title="Move cursor to beginning" disabled={cursorBusy || !target} onClick={() => void moveCursor("beginning", mailbox)}>⏮</button>
              <button type="button" className="chat-mbact" title="Move cursor to now" disabled={cursorBusy || !target} onClick={() => void moveCursor("now", mailbox)}>⏭</button>
              <button type="button" className="chat-mbact" title="Remove cursor" disabled={cursorBusy || !(cursorInfo && cursorInfo.initialized)} onClick={() => void moveCursor("remove", mailbox)}>⌫</button>
              <button type="button" className="chat-mbact" title="Show this mailbox's JSON (definition, members for a merge)" disabled={!mailbox} onClick={() => void inspectId("MAILBOX", mailbox)}>{"{ }"}</button>
            </span>
          </label>
          {mergeMailboxes.map((mb, index) => (
            <label className="chat-control chat-mbrow" key={`merge-row-${index}`}>
              <span className="chat-label">＋ Mailbox</span>
              <select
                value={mb}
                onChange={(event) => setMergeMailboxes((rows) => rows.map((row, j) => (j === index ? event.target.value : row)))}
                aria-label={`Merged mailbox ${index + 1}`}
              >
                <option value="">(none)</option>
                {mailboxChoices.map((id) => (
                  <option key={id} value={id}>{mailboxLabel(id)}</option>
                ))}
              </select>
              <span className="chat-mbrow-actions">
                <button type="button" className="chat-mbact" title="Move cursor to beginning" disabled={cursorBusy || !mb || !target} onClick={() => void moveCursor("beginning", mb)}>⏮</button>
                <button type="button" className="chat-mbact" title="Move cursor to now" disabled={cursorBusy || !mb || !target} onClick={() => void moveCursor("now", mb)}>⏭</button>
                <button type="button" className="chat-mbact" title="Show this mailbox's JSON (definition, members for a merge)" disabled={!mb} onClick={() => void inspectId("MAILBOX", mb)}>{"{ }"}</button>
                <button
                  type="button"
                  className="chat-mbact"
                  title="Remove this mailbox row from the view"
                  onClick={() => setMergeMailboxes((rows) => rows.filter((_, j) => j !== index))}
                >
                  ✕
                </button>
              </span>
            </label>
          ))}
          <label className="chat-control chat-mbrow">
            <button
              type="button"
              className="chat-label"
              title="Add another mailbox to merge into the view"
              onClick={() => setMergeMailboxes((rows) => [...rows, ""])}
            >
              ＋ Add mailbox
            </button>
            {mergeMailboxes.length > 0 && (
              <select
                value={mergeMode}
                onChange={(event) => setMergeMode(event.target.value as "by-timestamp" | "sequential")}
                aria-label="Merge mode"
                title="How to combine the selected mailboxes"
              >
                <option value="by-timestamp">by timestamp</option>
                <option value="sequential">one after another</option>
              </select>
            )}
            {mergeMailboxes.some((mb) => mb.trim()) && (
              <button
                type="button"
                className="chat-mbact"
                title="Save this merged view as a new virtual stream on the server"
                onClick={() => void saveMerge()}
              >
                💾 Save as stream
              </button>
            )}
          </label>
          <label className="chat-control chat-mbrow">
            <button
              type="button"
              className="chat-label"
              title="Show or hide message layout and color options"
              onClick={() => setShowDisplay((v) => !v)}
            >
              {showDisplay ? "▾ Layout & color" : "▸ Layout & color"}
            </button>
          </label>
          {showDisplay && (
            <>
          <label className="chat-control chat-mbrow">
            <span className="chat-label" title="Where to place message bubbles">Place</span>
            <select
              value={placement}
              onChange={(event) => setPlacement(event.target.value as typeof placement)}
              aria-label="Message placement"
            >
              <option value="sender">by sender (you right)</option>
              <option value="left">all left</option>
              <option value="right">all right</option>
              <option value="center">centered</option>
              <option value="full">full width</option>
              <option value="field">by field…</option>
            </select>
            {placement === "field" && (
              <select
                value={placementField}
                onChange={(event) => setPlacementField(event.target.value)}
                aria-label="Placement field"
                title="Each distinct value of this field gets its own lane"
              >
                {fieldOptions(placementField)}
              </select>
            )}
          </label>
          <label className="chat-control chat-mbrow">
            <span className="chat-label" title="Bubble border color">Border</span>
            <select
              value={borderMode}
              onChange={(event) => setBorderMode(event.target.value as typeof borderMode)}
              aria-label="Border color"
            >
              <option value="sender">by sender (you/them)</option>
              <option value="uniform">uniform</option>
              <option value="field">by field…</option>
            </select>
            {borderMode === "field" && (
              <select
                value={borderField}
                onChange={(event) => setBorderField(event.target.value)}
                aria-label="Border field"
                title="Each distinct value of this field gets its own border hue"
              >
                {fieldOptions(borderField)}
              </select>
            )}
          </label>
          <label className="chat-control chat-mbrow">
            <span className="chat-label" title="Bubble fill color">Fill</span>
            <select
              value={fillMode}
              onChange={(event) => setFillMode(event.target.value as typeof fillMode)}
              aria-label="Fill color"
            >
              <option value="sender">by sender (you/them)</option>
              <option value="uniform">uniform</option>
              <option value="field">by field…</option>
            </select>
            {fillMode === "field" && (
              <select
                value={fillField}
                onChange={(event) => setFillField(event.target.value)}
                aria-label="Fill field"
                title="Each distinct value of this field gets its own fill hue"
              >
                {fieldOptions(fillField)}
              </select>
            )}
          </label>
            </>
          )}
          <div className="chat-make">
            <input
              value={newEntry}
              onChange={(event) => setNewEntry(event.target.value)}
              placeholder="new agent or mailbox name"
              aria-label="New agent or mailbox name"
            />
            <button type="button" onClick={makeAgent} disabled={!newEntry.trim()}>
              Make new agent
            </button>
            <button type="button" onClick={makeMailbox} disabled={!newEntry.trim()}>
              Make new mailbox
            </button>
          </div>
          {mailbox && target && (
            <div className="chat-sub">
              <span className="chat-sub-label" title="Explicit subscription intent; 'Remove setting' reverts to the default (cursor holders count as subscribed).">
                Subscription · {target} on {mailboxLabel(mailbox)}:{" "}
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
            key={`${message.id}|${message.timestamp || ""}`}
            className={`chat-message ${message.from === you ? "mine" : "theirs"}${
              placement !== "sender" ? " " + placementClass(message) : ""
            }${entryEditKey === bubbleKey(message) ? " editing" : ""}`}
            style={messageColorStyle(message)}
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
                {message.mailboxName
                  ? `(${message.type || "message"} in ${message.mailboxName} — inspect JSON)`
                  : "(no text — inspect JSON)"}
              </div>
            )}
            {(expanded[message.id] ?? !message.text) && entryEditKey !== bubbleKey(message) && (
              <pre className="chat-message-json">
                {JSON.stringify(message.raw ?? message, null, 2)}
              </pre>
            )}
            {entryEditKey === bubbleKey(message) && (
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
                  <button type="button" onClick={closeEntryEdit} disabled={entryEditBusy}>
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
          <span className="chat-config-title">Mailbox config — {mailboxLabel(configMailbox)}</span>
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
          aria-label="Mailbox config JSON"
        />
        {configError && <div className="chat-error">{configError}</div>}
        {configNote && <div className="chat-config-note">{configNote}</div>}
      </div>
    </div>
  );
}
