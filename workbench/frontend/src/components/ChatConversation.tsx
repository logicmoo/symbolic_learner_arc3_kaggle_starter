import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties, type KeyboardEvent as ReactKeyboardEvent } from "react";
import { MarkdownDocument } from "./MarkdownDocument";
import { SuperControl, type StandardSuperControlRequest } from "./UniversalArtifactEditor";
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
// Palette of hues for field-based coloring.
const COLOR_HUES = [200, 280, 20, 140, 330, 50, 100, 250, 0, 170];
// How a bubble field is rendered.
const BUBBLE_STYLES: [string, string][] = [
  ["text", "plain"],
  ["label", "key: value"],
  ["chip", "chip"],
  ["bubble", "colored bubble"],
];
// How a message body is rendered.
const RENDER_MODES: [string, string][] = [
  ["markdown", "Markdown"],
  ["json", "JSON"],
  ["metta", "MeTTa"],
  ["raw", "raw text"],
];

// A display profile. There is one fallthrough default plus optional per-mailbox
// overrides; each message renders using its own mailbox's profile, else the default.
type ViewSettings = {
  placement: string;
  placementField: string;
  borderMode: string;
  borderField: string;
  borderColor: string;
  fillMode: string;
  fillField: string;
  fillColor: string;
  bubbleFields: { field: string; style: string }[];
  renderMode: string;
  renderRules: { field: string; value: string; mode: string }[];
  // Where the render-rule value autocomplete pulls candidates from:
  // "view" = distinct values in the currently loaded messages (in memory),
  // "cache" = the global on-disk field cache merged across viewed streams,
  // "stream" = the on-disk field cache for the edited/primary stream only.
  valueSource: string;
};
const DEFAULT_VIEW: ViewSettings = {
  placement: "field",
  placementField: "mailboxName",
  borderMode: "sender",
  borderField: "mailboxName",
  borderColor: "#4eabda",
  fillMode: "sender",
  fillField: "from",
  fillColor: "#2b3a44",
  bubbleFields: [
    { field: "from", style: "text" },
    { field: "type", style: "chip" },
    { field: "timestamp", style: "text" },
  ],
  renderMode: "markdown",
  renderRules: [],
  valueSource: "view",
};
// Validate a parsed object into a ViewSettings, filling gaps from the default.
function coerceView(v: Record<string, unknown>): ViewSettings {
  const str = (x: unknown, d: string) => (typeof x === "string" ? x : d);
  const bf = Array.isArray(v.bubbleFields)
    ? (v.bubbleFields as unknown[])
        .map((e) => (e && typeof e === "object" ? (e as Record<string, unknown>) : null))
        .filter((e): e is Record<string, unknown> => !!e && typeof e.field === "string")
        .map((e) => ({ field: String(e.field), style: typeof e.style === "string" ? e.style : "text" }))
    : DEFAULT_VIEW.bubbleFields;
  const rr = Array.isArray(v.renderRules)
    ? (v.renderRules as unknown[])
        .map((e) => (e && typeof e === "object" ? (e as Record<string, unknown>) : null))
        .filter((e): e is Record<string, unknown> => !!e && typeof e.field === "string")
        .map((e) => ({
          field: String(e.field),
          value: typeof e.value === "string" ? e.value : "",
          mode: typeof e.mode === "string" ? e.mode : "markdown",
        }))
    : [];
  return {
    placement: str(v.placement, DEFAULT_VIEW.placement),
    placementField: str(v.placementField, DEFAULT_VIEW.placementField),
    borderMode: str(v.borderMode, DEFAULT_VIEW.borderMode),
    borderField: str(v.borderField, DEFAULT_VIEW.borderField),
    borderColor: str(v.borderColor, DEFAULT_VIEW.borderColor),
    fillMode: str(v.fillMode, DEFAULT_VIEW.fillMode),
    fillField: str(v.fillField, DEFAULT_VIEW.fillField),
    fillColor: str(v.fillColor, DEFAULT_VIEW.fillColor),
    bubbleFields: bf.length ? bf : DEFAULT_VIEW.bubbleFields,
    renderMode: str(v.renderMode, DEFAULT_VIEW.renderMode),
    renderRules: rr,
    valueSource: str(v.valueSource, DEFAULT_VIEW.valueSource),
  };
}

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

export type MailboxOption = {
  [key: string]: unknown;
  id: string;
  kind?: string;
  source?: string;
  definition?: string;
  writable?: boolean;
  messages?: number;
  unread?: number;
  activityPerMinute?: number;
  activityPerHour?: number;
  lastActivityAt?: number | null;
  cursorOffset?: number;
  cursorInitialized?: boolean;
  lastReadMessageId?: string | null;
  nextUnreadMessageId?: string | null;
  server?: string;
  name?: string | null;
  global_name?: string | null;
  origin?: string;
};

type MailboxSortMode = "name" | "activity-minute" | "activity-hour" | "unread";
type MailboxOpenMode = "last-read" | "end-mark-read";
type FieldCacheConfig = {
  defaultLimit: number | null;
  records: Record<string, Record<string, unknown>>;
};

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
  last_read_id?: string | null;
  next_unread_id?: string | null;
};
export type AgentOption = { id: string; [key: string]: unknown };

type Props = {
  workspaceId?: string;
  user?: string;
  peer?: string;
  className?: string;
  pollMs?: number;
  showMailboxPicker?: boolean;
  onError?: (message: string) => void;
  initialInput?: string;
};

type AutoScrollPolicy = "always-on" | "allow-off";

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

async function requestMailboxCursor(
  mailbox: string,
  agent: string,
  start?: "beginning" | "now" | "remove",
): Promise<CursorInfo> {
  const query = `mailbox=${encodeURIComponent(mailbox)}&agent=${encodeURIComponent(agent)}`;
  const endpoints = ["/ws_collab/v1/mailbox/cursor", "/api/mailbox/cursor"];
  let lastError: unknown = null;
  for (const endpoint of endpoints) {
    try {
      const response = start === "remove"
        ? await fetch(`${endpoint}?${query}`, { method: "DELETE" })
        : start
          ? await fetch(endpoint, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ mailbox, agent, start }),
            })
          : await fetch(`${endpoint}?${query}`);
      return await readJson(response) as unknown as CursorInfo;
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError instanceof Error ? lastError : new Error("Mailbox cursor is unavailable");
}

// Each stream property renders as its own colored chip in the mailbox picker.
const TAG_COLORS: Record<string, string> = {
  jsonl: "#7aa2d6",
  "json-file": "#8f8fd6",
  disk: "#b0855b",
  merge: "#48b7a8",
  virtual: "#c88ce0",
  http: "#6fbf73",
  workbench: "#e0a458",
  "read-only": "#d98c8c",
};

type StreamTag = { text: string; color: string };
type StreamDescription = { label: string; groupKey: string; groupLabel: string; tags: StreamTag[] };

// A combobox replacement for the mailbox pickers: a native <select> can only
// color a whole <option> one color, so to give each property tag its own color
// we render a custom dropdown whose rows carry independently-colored chips.
function StreamPicker({
  value,
  ids,
  ariaLabel,
  allowNone,
  describe,
  onChange,
}: {
  value: string;
  ids: string[];
  ariaLabel: string;
  allowNone?: boolean;
  describe: (id: string) => StreamDescription;
  onChange: (value: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (!open) return;
    const onDoc = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) setOpen(false);
    };
    const onKey = (event: globalThis.KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);
  const groups = new Map<string, { label: string; ids: string[] }>();
  for (const id of ids) {
    const d = describe(id);
    const g = groups.get(d.groupKey) ?? { label: d.groupLabel, ids: [] };
    g.ids.push(id);
    groups.set(d.groupKey, g);
  }
  const order = [...groups.keys()].sort((left, right) => left.localeCompare(right));
  const cur = value ? describe(value) : null;
  const chips = (tags: StreamTag[]) =>
    tags.map((t) => (
      <span key={t.text} className="chat-tag" style={{ color: t.color, borderColor: t.color }}>
        {t.text}
      </span>
    ));
  return (
    <div className="chat-streampick" ref={ref}>
      <button
        type="button"
        className="chat-streampick-btn"
        aria-label={ariaLabel}
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
      >
        <span className="chat-streampick-cur">{cur ? cur.label : "(none/null)"}</span>
        {cur ? chips(cur.tags) : null}
        <span className="chat-streampick-caret">▾</span>
      </button>
      {open && (
        <div className="chat-streampick-menu" role="listbox">
          {allowNone && (
            <button type="button" className={`chat-streampick-opt${value ? "" : " is-sel"}`} onClick={() => { onChange(""); setOpen(false); }}>
              <span className="chat-streampick-optlbl">(none/null)</span>
            </button>
          )}
          {order
            .filter((k) => groups.has(k))
            .map((k) => (
              <div key={k} className="chat-streampick-grp">
                <div className="chat-streampick-grphdr">{groups.get(k)!.label}</div>
                {groups.get(k)!.ids.map((id) => {
                  const d = describe(id);
                  return (
                    <button
                      key={id}
                      type="button"
                      className={`chat-streampick-opt${id === value ? " is-sel" : ""}`}
                      onClick={() => { onChange(id); setOpen(false); }}
                    >
                      <span className="chat-streampick-optlbl">{d.label}</span>
                      {chips(d.tags)}
                    </button>
                  );
                })}
              </div>
            ))}
        </div>
      )}
    </div>
  );
}

// Shared chat surface used by both the full Chat page and the floatable mini-dock.
// Four editable combos drive it: FROM/TO pick agents, MAILBOX (view) and SEND-TO
// (send_to) pick mailboxes. FROM/TO are enumerated with first-class agents; the
// mailbox combos list the mailbox documents. Every message carries its raw
// record so it can be inspected as JSON.
export function ChatConversation({
  workspaceId = "shared_library_system",
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
  const [mailboxSortMode, setMailboxSortMode] = useState<MailboxSortMode>("activity-hour");
  const [mailboxGroupField, setMailboxGroupField] = useState("server");
  const [mailboxOpenMode, setMailboxOpenMode] = useState<MailboxOpenMode>("last-read");
  const [advanceCursorOnView, setAdvanceCursorOnView] = useState(false);
  const [showMailboxListSettings, setShowMailboxListSettings] = useState(false);
  const [showRequireMatchSettings, setShowRequireMatchSettings] = useState(false);
  const [mailboxSelectionRevision, setMailboxSelectionRevision] = useState(0);
  // Display settings live in a ViewSettings profile: a fallthrough `defaultView`
  // plus optional per-mailbox overrides in `mailboxViews`. Each message renders by
  // its own mailbox's profile when present, else the default. `scope` selects which
  // profile the editor edits ("" = default, else a mailbox id).
  const [defaultView, setDefaultView] = useState<ViewSettings>(DEFAULT_VIEW);
  const [mailboxViews, setMailboxViews] = useState<Record<string, ViewSettings>>({});
  const [scope, setScope] = useState<string>("");
  // Layout & color options are tucked behind a collapsible header (collapsed by default).
  const [showDisplay, setShowDisplay] = useState(false);
  // Auto-scroll has a workspace default and an optional setting for each stream.
  // "Always on" deliberately wins over either value, so an operator can keep a
  // live monitoring view pinned to the newest message.
  const [autoScrollPolicy, setAutoScrollPolicy] = useState<AutoScrollPolicy>("allow-off");
  const [autoScrollDefault, setAutoScrollDefault] = useState(true);
  const [autoScrollByMailbox, setAutoScrollByMailbox] = useState<Record<string, boolean>>({});
  // Selecting a message to inspect it (File tab) should only pause auto-scroll
  // locally for the current view; it must never rewrite the persisted
  // workspace default or per-stream override. This checkbox lets the operator
  // opt out of that local pause entirely, and is itself a saved preference.
  const [pauseAutoScrollOnSelect, setPauseAutoScrollOnSelect] = useState(true);
  // Tracks whether the current "off" state came from selecting a node (local,
  // non-persisted) so the UI can offer a dedicated resume action that never
  // touches autoScrollDefault/autoScrollByMailbox.
  const [selectionAutoScrollPaused, setSelectionAutoScrollPaused] = useState(false);

  // The whole view (merges, placement, colors, bubble fields, render rules, and the
  // selected mailbox) persists to localStorage per workspace and is saved the instant
  // anything changes; it is loaded once on mount before the first save.
  const viewKey = useMemo(() => {
    let ws = "default";
    try {
      ws = new URLSearchParams(window.location.search).get("workspace") || "default";
    } catch {
      /* ignore */
    }
    return `wscollab.chat.view:${ws}`;
  }, []);
  const viewHydrated = useRef(false);
  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(viewKey);
      if (raw) {
        const v = JSON.parse(raw) as Record<string, unknown>;
        if (v.defaultView && typeof v.defaultView === "object") setDefaultView(coerceView(v.defaultView as Record<string, unknown>));
        if (v.mailboxViews && typeof v.mailboxViews === "object") {
          const out: Record<string, ViewSettings> = {};
          for (const [k, val] of Object.entries(v.mailboxViews as Record<string, unknown>)) {
            if (val && typeof val === "object") out[k] = coerceView(val as Record<string, unknown>);
          }
          setMailboxViews(out);
        }
        if (typeof v.scope === "string") setScope(v.scope);
        if (v.mergeMode === "by-timestamp" || v.mergeMode === "sequential") setMergeMode(v.mergeMode);
        if (["name", "activity-minute", "activity-hour", "unread"].includes(String(v.mailboxSortMode))) {
          setMailboxSortMode(v.mailboxSortMode as MailboxSortMode);
        }
        if (typeof v.mailboxGroupField === "string" && v.mailboxGroupField) setMailboxGroupField(v.mailboxGroupField);
        if (v.mailboxOpenMode === "last-read" || v.mailboxOpenMode === "end-mark-read") setMailboxOpenMode(v.mailboxOpenMode);
        if (typeof v.advanceCursorOnView === "boolean") setAdvanceCursorOnView(v.advanceCursorOnView);
        if (v.autoScrollPolicy === "always-on" || v.autoScrollPolicy === "allow-off") {
          setAutoScrollPolicy(v.autoScrollPolicy);
        }
        if (typeof v.autoScrollDefault === "boolean") setAutoScrollDefault(v.autoScrollDefault);
        if (v.autoScrollByMailbox && typeof v.autoScrollByMailbox === "object") {
          setAutoScrollByMailbox(Object.fromEntries(
            Object.entries(v.autoScrollByMailbox as Record<string, unknown>)
              .filter(([, value]) => typeof value === "boolean") as [string, boolean][],
          ));
        }
        if (typeof v.pauseAutoScrollOnSelect === "boolean") setPauseAutoScrollOnSelect(v.pauseAutoScrollOnSelect);
        if (typeof v.showDisplay === "boolean") setShowDisplay(v.showDisplay);
        if (Array.isArray(v.mergeMailboxes)) {
          setMergeMailboxes((v.mergeMailboxes as unknown[]).filter((x): x is string => typeof x === "string"));
        }
        if (typeof v.mailbox === "string" && v.mailbox) {
          setMailbox(v.mailbox);
          setTarget(v.mailbox);
        }
      }
    } catch {
      /* ignore a corrupt saved view */
    }
    viewHydrated.current = true;
  }, [viewKey]);
  useEffect(() => {
    if (!viewHydrated.current) return;
    try {
      window.localStorage.setItem(
        viewKey,
        JSON.stringify({
          defaultView,
          mailboxViews,
          scope,
          mergeMode,
          showDisplay,
          mergeMailboxes,
          mailbox,
          mailboxSortMode,
          mailboxGroupField,
          mailboxOpenMode,
          advanceCursorOnView,
          autoScrollPolicy,
          autoScrollDefault,
          autoScrollByMailbox,
          pauseAutoScrollOnSelect,
        }),
      );
    } catch {
      /* ignore storage quota errors */
    }
  }, [
    viewKey, defaultView, mailboxViews, scope, mergeMode, showDisplay, mergeMailboxes, mailbox,
    mailboxSortMode, mailboxGroupField, mailboxOpenMode, advanceCursorOnView,
    autoScrollPolicy, autoScrollDefault, autoScrollByMailbox, pauseAutoScrollOnSelect,
  ]);
  const [target, setTarget] = useState(peer);
  const [sendMailbox, setSendMailbox] = useState("");
  const [agents, setAgents] = useState<AgentOption[]>([]);
  const [mailboxes, setMailboxes] = useState<MailboxOption[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  // On-disk field cache fetched per viewed stream: stream → field → candidate values.
  // Chat-bubble observations power rendering suggestions; mailbox-definition
  // observations independently power mailbox picker sorting/grouping.
  const [cacheFields, setCacheFields] = useState<Record<string, Record<string, string[]>>>({});
  const [mailboxDefinitionFields, setMailboxDefinitionFields] = useState<Record<string, Record<string, string[]>>>({});
  const [fieldCacheConfig, setFieldCacheConfig] = useState<FieldCacheConfig>({ defaultLimit: null, records: {} });
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
  // "Chat" vs "File" tab: the File tab shows the entire visible stream as an
  // editable JSON/MeTTa document (a snapshot of the records currently in view).
  const [paneTab, setPaneTab] = useState<"chat" | "file" | "config">("chat");
  const [streamFileText, setStreamFileText] = useState("");
  const [streamFileBaseline, setStreamFileBaseline] = useState("");
  const [streamFileNote, setStreamFileNote] = useState("");
  const [selectedMessageKey, setSelectedMessageKey] = useState<string | null>(null);
  const [autoScroll, setAutoScroll] = useState(true);
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
  const pendingMailboxNavigation = useRef<{ mailbox: string; mode: MailboxOpenMode } | null>(null);
  const cursorAdvanceTimer = useRef<number | null>(null);
  const markViewedRef = useRef<() => void>(() => {});
  const personalCursor = you || user || DEFAULT_CHAT_USER;
  const hasStreamAutoScrollSetting = Object.prototype.hasOwnProperty.call(autoScrollByMailbox, mailbox);
  const configuredAutoScroll = autoScrollPolicy === "always-on"
    || (hasStreamAutoScrollSetting ? autoScrollByMailbox[mailbox] : autoScrollDefault);

  // The config editor tracks the mailbox messages are sent on (SEND-TO mailbox if
  // set, otherwise the viewed mailbox).
  const configMailbox = sendMailbox || mailbox;

  // Switching the viewed mailbox re-points addressing to it by default; the "To"
  // field can then be overridden to address anyone independently.
  const selectMailbox = useCallback((next: string) => {
    pendingMailboxNavigation.current = { mailbox: next, mode: mailboxOpenMode };
    setMailbox(next);
    setTarget(next);
    setMailboxSelectionRevision((revision) => revision + 1);
  }, [mailboxOpenMode]);

  // Once the directory has loaded, ensure the viewed mailbox is a real stream.
  // A fresh workspace opens on the peer identity ("symbolic-workbench-user"),
  // which is not a stream and shows nothing — fall back to the shared
  // "conversation" stream (or the first available) so streams show up.
  useEffect(() => {
    if (!viewHydrated.current || !mailboxes.length) return;
    const realIds = mailboxes.map((m) => m.id);
    if (realIds.includes(mailbox)) return;
    const preferred = realIds.includes("conversation") ? "conversation" : realIds[0];
    if (preferred) setMailbox(preferred);
  }, [mailboxes, mailbox]);

  const fetchDirectory = useCallback(async () => {
    try {
      const needActivity = mailboxSortMode === "activity-minute" || mailboxSortMode === "activity-hour";
      const directoryParams = new URLSearchParams({ agent: personalCursor });
      if (needActivity) directoryParams.set("include_activity", "1");
      // Every plugin that can expose a mailbox directory is queried and merged —
      // the ws_collab relay (the live, richer source: unread counts, activity,
      // dynamic + virtual mailboxes) and the core /api mailbox_channels surface
      // (legacy/other-plugin mailboxes) — so no plugin's mailboxes are dropped
      // just because another plugin also answered.
      const emptyMailboxes = { mailboxes: [] } as Record<string, unknown>;
      const [agentPayload, relayMailboxPayload, apiMailboxPayload] = await Promise.all([
        readJson(await fetch("/ws_collab/v1/mailbox/agents")),
        fetch(`/ws_collab/v1/mailbox/mailboxes?${directoryParams.toString()}`)
          .then(readJson)
          .catch(() => emptyMailboxes),
        fetch(`/api/mailbox/mailboxes?agent=${encodeURIComponent(personalCursor)}`)
          .then(readJson)
          .catch(() => emptyMailboxes),
      ]);
      setAgents((agentPayload.agents as AgentOption[]) || []);
      const combined = new Map<string, MailboxOption>();
      // Apply the core/legacy source first, then let the ws_collab relay (the
      // richer, live source) win on id collisions.
      for (const option of (apiMailboxPayload.mailboxes as MailboxOption[]) || []) combined.set(option.id, option);
      for (const option of (relayMailboxPayload.mailboxes as MailboxOption[]) || []) combined.set(option.id, option);
      const enriched = await Promise.all([...combined.values()].map(async (option) => {
        let next = option;
        if (typeof next.unread !== "number") {
          try {
            const query = `mailbox=${encodeURIComponent(option.id)}&agent=${encodeURIComponent(personalCursor)}`;
            const cursor = await readJson(await fetch(`/ws_collab/v1/mailbox/cursor?${query}`)) as unknown as CursorInfo;
            next = {
              ...next,
              unread: cursor.behind,
              cursorOffset: cursor.offset,
              cursorInitialized: cursor.initialized,
              lastReadMessageId: cursor.last_read_id,
              nextUnreadMessageId: cursor.next_unread_id,
            };
          } catch {
            // Keep directory metadata when the relay has no cursor endpoint.
          }
        }
        if (needActivity && typeof next[mailboxSortMode === "activity-minute" ? "activityPerMinute" : "activityPerHour"] !== "number") {
          try {
            const payload = await readJson(await fetch(`/ws_collab/v1/mailbox/messages?mailbox=${encodeURIComponent(option.id)}&limit=300`));
            const records = (payload.messages as ChatMessage[]) || [];
            const now = Date.now();
            const timestamps = records.map((message) => new Date(message.timestamp || "").getTime()).filter(Number.isFinite);
            next = {
              ...next,
              activityPerMinute: timestamps.filter((stamp) => stamp >= now - 60_000).length,
              activityPerHour: timestamps.filter((stamp) => stamp >= now - 3_600_000).length,
            };
          } catch {
            // Activity stays unknown when the relay cannot expose the stream.
          }
        }
        return next;
      }));
      let observedLimit: number | null = null;
      try {
        const payload = await readJson(
          await fetch("/ws_collab/v1/mailbox/field-values?mailbox=*&observation=mailbox_definition"),
        );
        observedLimit = Number.isFinite(Number(payload.cached_limit)) ? Number(payload.cached_limit) : null;
        const streams = (payload.streams as Record<string, { fields?: Record<string, { values?: unknown[] }> }>) || {};
        setMailboxDefinitionFields(Object.fromEntries(Object.entries(streams).map(([stream, entry]) => [
          stream,
          Object.fromEntries(Object.entries(entry.fields || {}).map(([field, metadata]) => [
            field,
            (metadata.values || []).map(String),
          ])),
        ])));
      } catch {
        // Keep the last known mailbox-definition observation cache.
      }
      try {
        const payload = await readJson(
          await fetch("/ws_collab/v1/mailbox/messages?mailbox=field_cache_config&limit=300"),
        );
        const records = Object.fromEntries(((payload.messages as ChatMessage[]) || []).flatMap((message) => {
          const raw = message.raw && typeof message.raw === "object" && !Array.isArray(message.raw)
            ? message.raw as Record<string, unknown>
            : null;
          const id = String(raw?.id || message.id || "");
          return id && raw ? [[id, raw]] : [];
        }));
        const configuredLimit = Number(records.default_limit?.value);
        setFieldCacheConfig({
          defaultLimit: Number.isFinite(configuredLimit) ? configuredLimit : observedLimit,
          records,
        });
      } catch {
        // Keep the last known on-disk cache configuration.
      }
      setMailboxes(enriched);
    } catch {
      // Directory is best-effort; keep whatever we already have.
    }
  }, [mailboxSortMode, personalCursor]);

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
    const openingAtEnd = (pendingMailboxNavigation.current?.mailbox === mailbox
      ? pendingMailboxNavigation.current.mode
      : mailboxOpenMode) === "end-mark-read";
    const shouldAutoScroll = autoScrollPolicy === "always-on" ? true : configuredAutoScroll;
    stickBottomRef.current = shouldAutoScroll;
    setAutoScroll(shouldAutoScroll);
    setSelectedMessageKey(null);
    setSelectionAutoScrollPaused(false);
    fetchMessages();
    const timer = window.setInterval(() => {
      if (active) fetchMessages();
    }, Math.max(1000, pollMs));
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [fetchMessages, pollMs, mailbox, mailboxOpenMode, mailboxSelectionRevision, autoScrollPolicy, configuredAutoScroll]);

  useEffect(() => {
    const node = listRef.current;
    if (node && stickBottomRef.current) node.scrollTop = node.scrollHeight;
  }, [messages]);

  const handleScroll = () => {
    const node = listRef.current;
    if (!node) return;
    const atBottom = node.scrollHeight - node.scrollTop - node.clientHeight < 48;
    if (!atBottom && stickBottomRef.current && autoScrollPolicy !== "always-on") {
      stickBottomRef.current = false;
      setAutoScroll(false);
    }
    if (atBottom && advanceCursorOnView) markViewedRef.current();
  };

  const setAutoScrollEnabled = (enabled: boolean) => {
    const next = autoScrollPolicy === "always-on" ? true : enabled;
    if (hasStreamAutoScrollSetting) {
      setAutoScrollByMailbox((settings) => ({ ...settings, [mailbox]: next }));
    } else {
      setAutoScrollDefault(next);
    }
    // This is the deliberate persisted-override control, so any local
    // selection-driven pause is superseded by it.
    setSelectionAutoScrollPaused(false);
    stickBottomRef.current = next;
    setAutoScroll(next);
    if (next) {
      const node = listRef.current;
      if (node) node.scrollTop = node.scrollHeight;
    }
  };

  const setUseStreamAutoScrollSetting = (useStreamSetting: boolean) => {
    setAutoScrollByMailbox((settings) => {
      if (useStreamSetting) return { ...settings, [mailbox]: autoScroll };
      const next = { ...settings };
      delete next[mailbox];
      return next;
    });
  };

  // Restore auto-scroll to whatever is persisted (policy/default/per-stream
  // override) for the current mailbox. This is purely local: it never writes
  // to autoScrollDefault or autoScrollByMailbox, so it can safely be used to
  // undo a selection-driven pause without altering saved settings.
  const resumeAutoScroll = () => {
    setSelectionAutoScrollPaused(false);
    const enabled = autoScrollPolicy === "always-on" ? true : configuredAutoScroll;
    stickBottomRef.current = enabled;
    setAutoScroll(enabled);
    if (enabled) {
      const node = listRef.current;
      if (node) node.scrollTop = node.scrollHeight;
    }
  };

  useEffect(() => {
    const enabled = autoScrollPolicy === "always-on" ? true : configuredAutoScroll;
    stickBottomRef.current = enabled;
    setAutoScroll(enabled);
    if (enabled && listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [autoScrollPolicy, configuredAutoScroll, mailbox]);

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || sending || !you || !target) return;
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
      setAutoScroll(true);
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

  // Register a JSON/JSONL file under the server state dir as a durable, read-only
  // "disk:" virtual stream so its contents can be inspected in chat. Runtime only —
  // no restart needed (persisted in virtual_mailboxes.json).
  const registerDiskFile = useCallback(async () => {
    const file = (window.prompt("Register a JSON/JSONL file (under the server state dir) as a virtual stream.\n\nFile name:", "field_cache_config.json") || "").trim();
    if (!file) return;
    const base = file.replace(/\.[^.]+$/, "").replace(/[^A-Za-z0-9._-]/g, "-").slice(0, 60);
    const name = (window.prompt("Name the virtual stream:", base) || "").trim();
    if (!name) return;
    try {
      await readJson(
        await fetch("/ws_collab/v1/mailbox/create", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: name, source: `disk:${file}`, purpose: `disk file ${file}` }),
        }),
      );
      await fetchDirectory();
      setMailbox(name);
      setTarget(name);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorText(message);
      onError?.(message);
    }
  }, [fetchDirectory, onError]);

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

  // The organizable fields (base set + primitive keys discovered on messages or
  // their raw records), plus the distinct-value count per field. Counts are capped
  // at 17 so we can render ">16" without unbounded sets.
  const fieldStats = useMemo(() => {
    const values = new Map<string, Set<string>>();
    const ensure = (k: string) => {
      let s = values.get(k);
      if (!s) {
        s = new Set<string>();
        values.set(k, s);
      }
      return s;
    };
    for (const b of ORGANIZE_BASE) ensure(b);
    const consider = (k: string, v: unknown) => {
      if (ORGANIZE_SKIP.has(k) || v === null || v === undefined || typeof v === "object") return;
      const s = ensure(k);
      if (s.size <= 16) s.add(String(v)); // stop growing past 17 → renders as ">16"
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
    const extras = [...values.keys()].filter((k) => !base.includes(k)).sort();
    const counts = new Map<string, number>();
    for (const [k, s] of values) counts.set(k, s.size);
    return { fields: [...base, ...extras], counts };
  }, [messages]);

  // Render <option>s for a field picker, always including the current value even
  // if it hasn't been discovered yet (so growing the list never resets the choice).
  // Each label carries the distinct-value count seen so far (">16" once capped).
  const fieldOptions = (current: string) => {
    const list = fieldStats.fields.includes(current) ? fieldStats.fields : [current, ...fieldStats.fields];
    return list.map((f) => {
      const c = fieldStats.counts.get(f);
      const suffix = c === undefined ? "" : c > 16 ? " (>16)" : ` (${c})`;
      return (
        <option key={f} value={f}>
          {(FIELD_LABELS[f] ?? f) + suffix}
        </option>
      );
    });
  };

  // The profile currently being edited, and a patcher that writes to the default
  // or the scoped mailbox override (forking from the default the first time).
  const activeView = (scope && mailboxViews[scope]) || defaultView;
  const patchActive = useCallback(
    (patch: Partial<ViewSettings>) => {
      if (scope) setMailboxViews((m) => ({ ...m, [scope]: { ...(m[scope] ?? defaultView), ...patch } }));
      else setDefaultView((v) => ({ ...v, ...patch }));
    },
    [scope, defaultView],
  );

  // Distinct values per field seen in the currently loaded messages (in memory),
  // capped so a noisy field can't grow unbounded. Feeds the "view" candidate source.
  const viewValues = useMemo(() => {
    const out = new Map<string, string[]>();
    const seen = new Map<string, Set<string>>();
    const consider = (k: string, v: unknown) => {
      if (ORGANIZE_SKIP.has(k) || v === null || v === undefined || typeof v === "object") return;
      let s = seen.get(k);
      if (!s) {
        s = new Set<string>();
        seen.set(k, s);
        out.set(k, []);
      }
      const sv = String(v);
      if (!s.has(sv) && s.size < 200) {
        s.add(sv);
        out.get(k)!.push(sv);
      }
    };
    for (const m of messages) {
      const rec = m as unknown as Record<string, unknown>;
      for (const k of Object.keys(rec)) consider(k, rec[k]);
      const raw = rec.raw;
      if (raw && typeof raw === "object") {
        for (const [k, v] of Object.entries(raw as Record<string, unknown>)) consider(k, v);
      }
    }
    return out;
  }, [messages]);

  // The stream the "stream" candidate source resolves to: the edited profile's
  // scope when scoped, else the primary viewed mailbox.
  const activeStream = scope || mailbox;

  // Lazily load the on-disk field cache for every viewed stream whenever any active
  // profile needs it ("cache"/"stream" source). Never blocks rendering; best-effort.
  useEffect(() => {
    const needsCache = [defaultView, ...Object.values(mailboxViews)].some(
      (v) => v.valueSource === "cache" || v.valueSource === "stream",
    );
    if (!needsCache) return;
    const streams = Array.from(new Set([mailbox, ...mergeMailboxes].filter(Boolean)));
    if (!streams.length) return;
    let cancelled = false;
    (async () => {
      const next: Record<string, Record<string, string[]>> = {};
      for (const s of streams) {
        try {
          const payload = await readJson(
            await fetch(`/ws_collab/v1/mailbox/field-values?mailbox=${encodeURIComponent(s)}&observation=chat_bubble`),
          );
          const fields = (payload.fields as Record<string, { values?: unknown[] }>) || {};
          const map: Record<string, string[]> = {};
          for (const [f, info] of Object.entries(fields)) {
            map[f] = Array.isArray(info?.values) ? info.values.map((x) => String(x)) : [];
          }
          next[s] = map;
        } catch {
          // best-effort per stream
        }
      }
      if (!cancelled) setCacheFields(next);
    })();
    return () => {
      cancelled = true;
    };
  }, [defaultView, mailboxViews, mailbox, mergeMailboxes]);

  // Candidate values for a field under the active profile's chosen source.
  const valueCandidates = useCallback(
    (field: string): string[] => {
      if (!field) return [];
      const src = activeView.valueSource;
      if (src === "view") return viewValues.get(field) ?? [];
      if (src === "stream") return cacheFields[activeStream]?.[field] ?? [];
      // "cache": merge the field across all viewed streams' on-disk caches.
      const seen = new Set<string>();
      const out: string[] = [];
      for (const map of Object.values(cacheFields)) {
        for (const v of map[field] ?? []) {
          if (!seen.has(v)) {
            seen.add(v);
            out.push(v);
          }
        }
      }
      return out;
    },
    [activeView.valueSource, viewValues, cacheFields, activeStream],
  );

  // Resolve the profile for a message: its mailbox override, else the default.
  const effectiveView = useCallback(
    (m: ChatMessage): ViewSettings => {
      const id = m.mailboxId || m.mailboxName || "";
      return (id && mailboxViews[id]) || defaultView;
    },
    [mailboxViews, defaultView],
  );

  // Every field any profile lanes or colors by, so we can precompute value indices.
  const laneFields = useMemo(() => {
    const set = new Set<string>();
    for (const v of [defaultView, ...Object.values(mailboxViews)]) {
      if (v.placement === "field") set.add(v.placementField);
      if (v.borderMode === "field") set.add(v.borderField);
      if (v.fillMode === "field") set.add(v.fillField);
    }
    return set;
  }, [defaultView, mailboxViews]);

  // Per-field value→index maps (stream-seeded for mailboxName) driving lanes & hues.
  const fieldIndex = useMemo(() => {
    const maps = new Map<string, Map<string, number>>();
    const ensure = (f: string) => {
      let mm = maps.get(f);
      if (!mm) {
        mm = new Map<string, number>();
        maps.set(f, mm);
      }
      return mm;
    };
    for (const f of laneFields) {
      const mm = ensure(f);
      if (f === "mailboxName") {
        for (const mb of [mailbox, ...mergeMailboxes].filter(Boolean)) {
          const k = String(mb);
          if (!mm.has(k)) mm.set(k, mm.size);
        }
      }
    }
    for (const m of messages) {
      for (const f of laneFields) {
        const mm = ensure(f);
        const k = fieldValue(m, f);
        if (!mm.has(k)) mm.set(k, mm.size);
      }
    }
    return maps;
  }, [laneFields, messages, mailbox, mergeMailboxes, fieldValue]);

  const LANES = ["pos-left", "pos-right", "pos-center", "pos-full"];
  const placementClass = useCallback(
    (m: ChatMessage): string => {
      const v = effectiveView(m);
      switch (v.placement) {
        case "left":
          return "pos-left";
        case "right":
          return "pos-right";
        case "center":
          return "pos-center";
        case "full":
          return "pos-full";
        case "field": {
          const idx = fieldIndex.get(v.placementField)?.get(fieldValue(m, v.placementField)) ?? 0;
          return LANES[idx % LANES.length];
        }
        default:
          return "";
      }
    },
    [effectiveView, fieldIndex, fieldValue],
  );

  const messageColorStyle = useCallback(
    (m: ChatMessage): CSSProperties | undefined => {
      const v = effectiveView(m);
      const style: CSSProperties = {};
      if (v.borderMode === "uniform") {
        style.borderColor = v.borderColor || "var(--line)";
      } else if (v.borderMode === "field") {
        const idx = fieldIndex.get(v.borderField)?.get(fieldValue(m, v.borderField)) ?? 0;
        style.borderColor = `hsl(${COLOR_HUES[idx % COLOR_HUES.length]} 65% 58%)`;
      }
      if (v.fillMode === "uniform") {
        style.background = v.fillColor || "var(--panel2)";
      } else if (v.fillMode === "field") {
        const idx = fieldIndex.get(v.fillField)?.get(fieldValue(m, v.fillField)) ?? 0;
        style.background = `hsl(${COLOR_HUES[idx % COLOR_HUES.length]} 60% 45% / 0.16)`;
      }
      return style.borderColor || style.background ? style : undefined;
    },
    [effectiveView, fieldIndex, fieldValue],
  );

  // Fields offered for the per-bubble display list: the organizable fields plus a
  // few display-only ones (timestamp, id), and always whatever is already chosen.
  const bubbleFieldChoices = useMemo(() => {
    const set = new Set<string>([...fieldStats.fields, "timestamp", "id"]);
    for (const e of activeView.bubbleFields) set.add(e.field);
    const pref = ["from", "author", "type", "timestamp", "to", "send_to", "id", "mailboxName"];
    return [...set].sort((a, b) => {
      const ia = pref.indexOf(a);
      const ib = pref.indexOf(b);
      if (ia !== -1 || ib !== -1) return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
      return a.localeCompare(b);
    });
  }, [fieldStats.fields, activeView.bubbleFields]);

  // Stable hue for a value (for the "colored bubble" style), drawn from the palette.
  const hueForValue = useCallback((v: string): number => {
    let h = 0;
    for (let i = 0; i < v.length; i++) h = (h * 31 + v.charCodeAt(i)) >>> 0;
    return COLOR_HUES[h % COLOR_HUES.length];
  }, []);

  // Render one field on a bubble according to its chosen display style.
  const renderBubbleField = useCallback(
    (m: ChatMessage, entry: { field: string; style: string }, key: string) => {
      const { field, style } = entry;
      let display: string;
      if (field === "from") {
        display = m.authorName || m.author || m.from || "";
        const via = m.author && m.from && m.author !== m.from ? m.from : "";
        if (style === "text" || style === "label") {
          return (
            <span key={key} className="chat-message-from">
              {display}
              {via ? <span className="chat-message-via"> via {via}</span> : null}
            </span>
          );
        }
      } else if (field === "timestamp") {
        display = m.timestamp ? formatTime(m.timestamp) : "";
      } else {
        display = fieldValue(m, field);
      }
      if (!display) return null;
      const label = FIELD_LABELS[field] ?? field;
      if (style === "bubble") {
        const h = hueForValue(display);
        return (
          <span
            key={key}
            className="chat-bubble-tag"
            style={{ borderColor: `hsl(${h} 65% 58%)`, background: `hsl(${h} 60% 45% / 0.22)` }}
            title={label}
          >
            {display}
          </span>
        );
      }
      if (style === "chip") {
        return (
          <span key={key} className="chat-message-type" title={label}>
            {display}
          </span>
        );
      }
      if (style === "label") {
        return (
          <span key={key} className="chat-message-field">
            <span className="chat-message-field-key">{label}</span> {display}
          </span>
        );
      }
      return (
        <span key={key} className="chat-message-field-text" title={label}>
          {display}
        </span>
      );
    },
    [fieldValue, hueForValue],
  );

  // The effective render mode for a message: the first matching override rule, else
  // the default. A rule matches when its field equals its value (case-insensitive),
  // or — when the value is blank — whenever the field has any value.
  const effectiveMode = useCallback(
    (m: ChatMessage): string => {
      const v = effectiveView(m);
      for (const r of v.renderRules) {
        if (!r.field) continue;
        const val = fieldValue(m, r.field);
        const match = r.value ? val.toLowerCase() === r.value.toLowerCase() : val !== "";
        if (match) return r.mode;
      }
      return v.renderMode;
    },
    [effectiveView, fieldValue],
  );

  const renderBody = useCallback(
    (m: ChatMessage) => {
      const mode = effectiveMode(m);
      const record = m.raw && typeof m.raw === "object" ? m.raw : { from: m.from, to: m.to, type: m.type, text: m.text };
      if (mode === "raw") {
        return <pre className="chat-message-raw">{m.text || "(no text)"}</pre>;
      }
      if (mode === "json") {
        return <pre className="chat-message-json">{JSON.stringify(record, null, 2)}</pre>;
      }
      if (mode === "metta") {
        let text: string;
        try {
          text = jsonDocumentToMetta(JSON.stringify(record));
        } catch {
          text = JSON.stringify(record, null, 2);
        }
        return <pre className="chat-message-json">{text}</pre>;
      }
      return m.text ? (
        <MarkdownDocument className="chat-message-body" content={m.text} />
      ) : (
        <div className="chat-message-empty">
          {m.mailboxName ? `(${m.type || "message"} in ${m.mailboxName} — inspect JSON)` : "(no text — inspect JSON)"}
        </div>
      );
    },
    [effectiveMode],
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

  // ---- Stream-as-file (the "File" tab) -----------------------------------
  const viewedStreamName = () => {
    const streams = Array.from(new Set([mailbox, ...mergeMailboxes].filter(Boolean)));
    return streams.length ? streams.join("+") : "stream";
  };
  // Rebuild the source from either the selected node or the complete visible
  // stream. The full stream uses a resource envelope so SuperControl can retain
  // stable identity while exposing every record.
  const buildStreamFile = useCallback((message?: ChatMessage | null) => {
    const records = messages.map((entry) => (entry.raw && typeof entry.raw === "object" ? entry.raw : entry));
    const raw = message?.raw && typeof message.raw === "object" ? message.raw : message;
    const document = raw
      ? {
          ...(raw as Record<string, unknown>),
          id: String((raw as Record<string, unknown>).id || message?.id || "selected-message"),
          type: String((raw as Record<string, unknown>).type || message?.type || "chat_message"),
        }
      : {
          kind: "chat_stream",
          id: viewedStreamName(),
          label: `${viewedStreamName()} visible stream`,
          records,
        };
    const json = `${JSON.stringify(document, null, 2)}\n`;
    setStreamFileText(json);
    setStreamFileBaseline(json);
    setStreamFileNote(message
      ? `Selected message ${message.id}`
      : `${records.length} record${records.length === 1 ? "" : "s"} in view`);
  }, [messages, mailbox, mergeMailboxes]);

  const selectStreamNode = (message: ChatMessage) => {
    const key = bubbleKey(message);
    const nextSelected = selectedMessageKey === key ? null : message;
    setSelectedMessageKey(nextSelected ? key : null);
    if (nextSelected) {
      // Inspecting a message pauses scrolling locally only; it must never
      // rewrite the persisted workspace default or per-stream override
      // (that would silently change auto-scroll for other streams too).
      if (pauseAutoScrollOnSelect) {
        stickBottomRef.current = false;
        setAutoScroll(false);
        setSelectionAutoScrollPaused(true);
      }
    } else if (selectionAutoScrollPaused) {
      // Deselecting restores whatever is persisted for this stream, without
      // writing to it.
      resumeAutoScroll();
    }
    buildStreamFile(nextSelected);
  };

  const openStreamFile = () => {
    try {
      const selected = messages.find(message => bubbleKey(message) === selectedMessageKey) || null;
      buildStreamFile(selected);
    } catch (error) {
      setStreamFileNote(error instanceof Error ? error.message : String(error));
    }
    setPaneTab("file");
  };

  const copyStreamFile = async () => {
    try {
      await navigator.clipboard.writeText(streamFileText);
      setStreamFileNote("copied to clipboard");
    } catch {
      setStreamFileNote("copy failed");
    }
  };

  const downloadStreamFile = () => {
    const blob = new Blob([streamFileText], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${viewedStreamName()}${selectedMessageKey ? ".selected" : ""}.json`;
    link.click();
    URL.revokeObjectURL(url);
    setStreamFileBaseline(streamFileText);
  };

  const selectedStreamMessage = messages.find(message => bubbleKey(message) === selectedMessageKey) || null;
  const streamFileResource = useMemo(() => {
    try {
      const parsed = JSON.parse(streamFileText) as Record<string, unknown>;
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return null;
      return {
        ...parsed,
        kind: String(parsed.kind || parsed.type || "chat_message"),
        id: String(parsed.id || selectedStreamMessage?.id || viewedStreamName()),
      };
    } catch {
      return null;
    }
  }, [streamFileText, selectedStreamMessage?.id, mailbox, mergeMailboxes]);
  const streamSuperControl: StandardSuperControlRequest = {
    kind: "standard",
    workspaceId,
    source: streamFileText,
    sourceScope: selectedStreamMessage ? "selected chat node" : "visible chat stream",
    path: `runtime/chat/${viewedStreamName()}${selectedStreamMessage ? `/${selectedStreamMessage.id}` : ""}.json`,
    title: selectedStreamMessage ? `Selected message ${selectedStreamMessage.id}` : `${viewedStreamName()} stream`,
    dirty: streamFileText !== streamFileBaseline,
    secondary: false,
    busy: false,
    resource: streamFileResource,
    initialControlId: "file",
    onChange: value => {
      setStreamFileText(value);
      setStreamFileNote("Source changed");
    },
    onSave: downloadStreamFile,
    saveLabel: "Download snapshot",
    actions: [
      {
        id: "refresh",
        label: selectedStreamMessage ? "Refresh selected node" : "Refresh whole stream",
        onInvoke: () => buildStreamFile(selectedStreamMessage),
      },
      {
        id: "whole-stream",
        label: "Whole stream",
        disabled: !selectedStreamMessage,
        onInvoke: () => {
          setSelectedMessageKey(null);
          buildStreamFile(null);
        },
      },
      { id: "copy", label: "Copy", onInvoke: () => void copyStreamFile() },
    ],
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

  // Cursor control always reflects the current workbench user's personal read
  // position; TO remains independent message addressing.
  const fetchCursor = useCallback(async () => {
    if (!mailbox || !personalCursor) {
      setCursorInfo(null);
      return;
    }
    try {
      setCursorInfo(await requestMailboxCursor(mailbox, personalCursor));
    } catch {
      setCursorInfo(null);
    }
  }, [mailbox, personalCursor]);

  useEffect(() => {
    fetchCursor();
  }, [fetchCursor]);

  const moveCursor = useCallback(
    async (start: "beginning" | "now" | "remove", mb: string = mailbox) => {
      if (!mb || !personalCursor) return;
      setCursorBusy(true);
      try {
        const payload = await requestMailboxCursor(mb, personalCursor, start);
        if (mb === mailbox) setCursorInfo(payload);
        void fetchDirectory();
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        setErrorText(message);
        onError?.(message);
      } finally {
        setCursorBusy(false);
      }
    },
    [mailbox, personalCursor, onError, fetchDirectory],
  );

  useEffect(() => {
    markViewedRef.current = () => {
      if (!advanceCursorOnView || !mailbox) return;
      if (cursorAdvanceTimer.current !== null) window.clearTimeout(cursorAdvanceTimer.current);
      cursorAdvanceTimer.current = window.setTimeout(() => {
        cursorAdvanceTimer.current = null;
        void moveCursor("now", mailbox);
      }, 300);
    };
    return () => {
      if (cursorAdvanceTimer.current !== null) window.clearTimeout(cursorAdvanceTimer.current);
    };
  }, [advanceCursorOnView, mailbox, moveCursor]);

  useEffect(() => {
    const pending = pendingMailboxNavigation.current;
    const node = listRef.current;
    if (!pending || pending.mailbox !== mailbox || !ready || paneTab !== "chat" || !node) return;
    const option = mailboxes.find((item) => item.id === mailbox);
    const cursorKnown = typeof option?.unread === "number" || cursorInfo?.mailbox === mailbox;
    if (pending.mode === "last-read" && !cursorKnown) return;
    window.requestAnimationFrame(() => {
      if (pending.mode === "end-mark-read") {
        node.scrollTop = node.scrollHeight;
        stickBottomRef.current = true;
        setAutoScroll(true);
        void moveCursor("now", mailbox);
      } else {
        const lastReadId = option?.lastReadMessageId || cursorInfo?.last_read_id;
        const messageNode = lastReadId
          ? [...node.querySelectorAll<HTMLElement>("[data-message-id]")].find((item) => item.dataset.messageId === lastReadId)
          : null;
        if (messageNode) messageNode.scrollIntoView({ block: "center" });
        else if ((option?.unread ?? cursorInfo?.behind ?? 0) === 0) node.scrollTop = node.scrollHeight;
        else node.scrollTop = 0;
        stickBottomRef.current = false;
        setAutoScroll(false);
      }
      pendingMailboxNavigation.current = null;
    });
  }, [cursorInfo, mailbox, mailboxes, messages, moveCursor, paneTab, ready]);

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
  // Clicking a picker label (FROM/TO/MAILBOX/SEND-TO) opens an editable JSON view
  // of whatever that picker points at; clicking the same label again hides it.
  // FROM/TO show the agent record as returned by /ws_collab/v1/mailbox/agents (cursors
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
      const kind = label === "FROM" || label === "TO" ? ("agent" as const) : ("mailbox" as const);
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

  // Dedup keeps currently-selected values present while the directory lags.
  // Mailboxes then use the arrangement selected in the collapsible Chat control.
  const alpha = (a: string, b: string) => a.toLowerCase().localeCompare(b.toLowerCase());
  const agentChoices = Array.from(new Set([you, target, ...agents.map((a) => a.id)].filter(Boolean))).sort(alpha);

  // Mailbox options carry a readable name resolved from the identifier directory
  // and live personal-cursor/activity metadata.
  const mailboxNames = new Map(mailboxes.map((c) => [c.id, c.name] as const));
  const mailboxUnread = new Map(mailboxes.map((c) => [c.id, c.unread] as const));
  const mailboxActivityMinute = new Map(mailboxes.map((c) => [c.id, c.activityPerMinute] as const));
  const mailboxActivityHour = new Map(mailboxes.map((c) => [c.id, c.activityPerHour] as const));
  const mailboxServers = new Map(mailboxes.map((c) => [c.id, c.server] as const));
  const mailboxGlobals = new Map(mailboxes.map((c) => [c.id, c.global_name] as const));
  const mailboxOrigins = new Map(mailboxes.map((c) => [c.id, c.origin] as const));
  const mailboxKinds = new Map(mailboxes.map((c) => [c.id, c.kind] as const));
  const mailboxSources = new Map(mailboxes.map((c) => [c.id, c.source] as const));
  const mailboxDefs = new Map(mailboxes.map((c) => [c.id, c.definition] as const));
  const mailboxWritable = new Map(mailboxes.map((c) => [c.id, c.writable] as const));
  const originLabel = (o?: string) => (o === "workbench" ? "Workbench server" : "ws_collab");
  const mailboxName = (id: string) => String(mailboxNames.get(id) || id);
  const mailboxById = new Map(mailboxes.map((option) => [option.id, option] as const));
  const cachedGroupFields = [...new Set(Object.values(mailboxDefinitionFields).flatMap((fields) => Object.keys(fields)))];
  const cachedBubbleFields = [...new Set(Object.values(cacheFields).flatMap((fields) => Object.keys(fields)))];
  const configuredGroupFields = [...new Set(Object.values(fieldCacheConfig.records).flatMap((record) => {
    const value = record.value && typeof record.value === "object" && !Array.isArray(record.value)
      ? record.value as Record<string, unknown>
      : record;
    const observation = value.mailbox_definition && typeof value.mailbox_definition === "object" && !Array.isArray(value.mailbox_definition)
      ? value.mailbox_definition as Record<string, unknown>
      : value;
    const fields = observation.fields && typeof observation.fields === "object" && !Array.isArray(observation.fields)
      ? Object.keys(observation.fields as Record<string, unknown>)
      : [];
    const named = String(observation.field || observation.name || "").trim();
    return [...fields, ...(named ? [named] : [])];
  }))];
  const groupFieldOptions = [
    "server",
    mailboxGroupField,
    ...[...new Set(mailboxes.flatMap((option) => Object.entries(option)
      .filter(([key, value]) => key !== "id" && value !== null && ["string", "number", "boolean"].includes(typeof value))
      .map(([key]) => key)))].filter((key) => key !== "server").sort(alpha),
    ...cachedGroupFields.sort(alpha),
    ...configuredGroupFields.sort(alpha),
    "none",
  ].filter((field, index, values) => values.indexOf(field) === index);
  const fieldLabel = (field: string) => field === "none"
    ? "None"
    : field.replace(/([a-z])([A-Z])/g, "$1 $2").replace(/[_-]+/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
  const mailboxMetric = (id: string) => mailboxSortMode === "activity-minute"
    ? mailboxActivityMinute.get(id) || 0
    : mailboxSortMode === "activity-hour"
      ? mailboxActivityHour.get(id) || 0
      : mailboxSortMode === "unread"
        ? mailboxUnread.get(id) || 0
        : 0;
  const compareMailboxes = (left: string, right: string) => mailboxSortMode === "name"
    ? alpha(mailboxName(left), mailboxName(right)) || alpha(left, right)
    : mailboxMetric(right) - mailboxMetric(left) || alpha(mailboxName(left), mailboxName(right)) || alpha(left, right);
  const mailboxChoices = Array.from(new Set([mailbox, ...mailboxes.map((c) => c.id)].filter(Boolean))).sort(compareMailboxes);
  const sendChoices = Array.from(new Set([sendMailbox, ...mailboxes.map((c) => c.id)].filter(Boolean))).sort(compareMailboxes);
  // The property tags for a stream (each rendered as its own colored chip).
  const streamTags = (id: string): StreamTag[] => {
    const kind = mailboxKinds.get(id);
    const source = mailboxSources.get(id);
    const def = String(mailboxDefs.get(id) || "").toLowerCase();
    const names: string[] = [];
    if (kind === "merge") {
      names.push("merge");
    } else if (source === "virtual") {
      names.push("virtual");
      if (def.startsWith("disk:")) {
        names.push("disk");
        names.push(def.endsWith(".jsonl") ? "jsonl" : "json-file");
      } else if (def.startsWith("http")) {
        names.push("http");
      }
    } else if (source === "jsonl") {
      names.push("jsonl");
    }
    if (mailboxWritable.get(id) === false) names.push("read-only");
    if (mailboxOrigins.get(id) === "workbench") names.push("workbench");
    const tags = names.map((t) => ({ text: t, color: TAG_COLORS[t] || "#9aa4b2" }));
    const unread = mailboxUnread.get(id);
    const perMinute = mailboxActivityMinute.get(id);
    const perHour = mailboxActivityHour.get(id);
    if (typeof unread === "number" && unread > 0) tags.push({ text: `${unread} unread`, color: "#e0a458" });
    if (typeof perMinute === "number" && perMinute > 0) tags.push({ text: `${perMinute}/min`, color: "#48b7a8" });
    else if (typeof perHour === "number" && perHour > 0) tags.push({ text: `${perHour}/hr`, color: "#7aa2d6" });
    return tags;
  };
  // The TO agent's explicit subscription setting on the viewed mailbox (if any).
  const targetRecord = agents.find((a) => a.id === target) as Record<string, unknown> | undefined;
  const targetSubs = (targetRecord?.subscriptions ?? null) as Record<string, string> | null;
  const subSetting = targetSubs && mailbox in targetSubs ? targetSubs[mailbox] : null;
  const mailboxLabel = (id: string) => {
    const name = mailboxNames.get(id);
    const base = name && name !== id ? `${name} · ${id}` : id;
    const globalName = mailboxGlobals.get(id);
    const withGlobal = globalName && globalName !== id ? `${base} · ${globalName}` : base;
    const unread = mailboxUnread.get(id);
    return typeof unread === "number" ? `${withGlobal} · ${unread}` : withGlobal;
  };
  // Everything the StreamPicker needs to render one option: label, origin group,
  // and the per-property colored chips.
  const describeStream = (id: string): StreamDescription => {
    const origin = mailboxOrigins.get(id) || "ws_collab";
    const option = mailboxById.get(id);
    const cachedValues = mailboxDefinitionFields[id]?.[mailboxGroupField] || [];
    const rawGroupValue = mailboxGroupField === "server"
      ? mailboxServers.get(id) || originLabel(origin)
      : mailboxGroupField === "origin"
        ? originLabel(origin)
        : option?.[mailboxGroupField] ?? (cachedValues.length ? cachedValues.join(" · ") : undefined);
    const groupValue = mailboxGroupField === "none" ? "All streams" : String(rawGroupValue ?? "(none)");
    return {
      label: mailboxLabel(id),
      groupKey: mailboxGroupField === "none" ? "all" : `${mailboxGroupField}:${groupValue}`,
      groupLabel: groupValue,
      tags: streamTags(id),
    };
  };

  return (
    <div className={`chat-conversation ${className ?? ""}`.trim()}>
      {showMailboxPicker && (
        <div className={`chat-controls${showRequireMatchSettings ? "" : " is-match-collapsed"}`}>
          <div className="chat-require-summary">
            <button
              type="button"
              className="chat-require-summary-toggle"
              aria-expanded={showRequireMatchSettings}
              onClick={() => setShowRequireMatchSettings((open) => !open)}
            >
              {showRequireMatchSettings ? "▾" : "▸"} Require match
            </button>
            <button type="button" className={`chat-require-btn${requireFrom ? " active" : ""}`} aria-pressed={requireFrom} onClick={() => setRequireFrom((value) => !value)}>FROM</button>
            <button type="button" className={`chat-require-btn${requireTo ? " active" : ""}`} aria-pressed={requireTo} onClick={() => setRequireTo((value) => !value)}>TO</button>
            <button type="button" className={`chat-require-btn${requireMailbox ? " active" : ""}`} aria-pressed={requireMailbox} onClick={() => setRequireMailbox((value) => !value)}>MAILBOX</button>
            <button type="button" className={`chat-require-btn${requireSendTo ? " active" : ""}`} aria-pressed={requireSendTo} onClick={() => setRequireSendTo((value) => !value)}>SEND-TO</button>
            <button type="button" className={`chat-require-btn${requireText ? " active" : ""}`} aria-pressed={requireText} onClick={() => setRequireText((value) => !value)}>TEXT</button>
            <input className="chat-require-input" value={textExpr} onChange={(event) => setTextExpr(event.target.value)} placeholder="text expression — substring or /regex/" aria-label="Text expression" />
          </div>
          <div className="chat-tabs chat-control--tabs" role="tablist">
            <button type="button" role="tab" aria-selected={paneTab === "chat"} className={`chat-tab${paneTab === "chat" ? " is-active" : ""}`} onClick={() => setPaneTab("chat")}>Chat</button>
            <button type="button" role="tab" aria-selected={paneTab === "file"} className={`chat-tab${paneTab === "file" ? " is-active" : ""}`} onClick={() => { if (paneTab !== "file") openStreamFile(); }}>File</button>
            <button type="button" role="tab" aria-selected={paneTab === "config"} className={`chat-tab${paneTab === "config" ? " is-active" : ""}`} onClick={() => setPaneTab("config")}>Config</button>
            <label className="chat-autoscroll-stream-setting" title="Use an auto-scroll setting for this stream instead of the workspace default">
              <input
                type="checkbox"
                checked={hasStreamAutoScrollSetting}
                onChange={(event) => setUseStreamAutoScrollSetting(event.target.checked)}
              />
              <span>{`Use ${mailboxLabel(mailbox)} Setting`}</span>
            </label>
            <label className="chat-autoscroll-policy">
              <span>Auto-scroll policy</span>
              <select value={autoScrollPolicy} onChange={(event) => setAutoScrollPolicy(event.target.value as AutoScrollPolicy)} aria-label="Auto-scroll policy">
                <option value="always-on">Always on</option>
                <option value="allow-off">Allow off</option>
              </select>
            </label>
            <button type="button" className={`chat-autoscroll${autoScroll ? " active" : ""}`} aria-pressed={autoScroll} disabled={autoScrollPolicy === "always-on"} onClick={() => setAutoScrollEnabled(!autoScroll)}>
              Auto-scroll · {autoScroll ? "On" : "Off"}
            </button>
            <label className="chat-autoscroll-pause-on-select" title="Pause auto-scroll locally while a message is selected, without changing the saved auto-scroll setting for any stream">
              <input
                type="checkbox"
                checked={pauseAutoScrollOnSelect}
                onChange={(event) => setPauseAutoScrollOnSelect(event.target.checked)}
              />
              <span>Pause on select</span>
            </label>
            {selectedStreamMessage && (
              <span className="chat-selected-node">
                Source · {selectedStreamMessage.id}
                {selectionAutoScrollPaused && (
                  <button type="button" className="chat-resume-autoscroll" onClick={resumeAutoScroll} title="Resume auto-scroll for this stream without changing any saved setting">
                    Resume auto-scroll
                  </button>
                )}
              </span>
            )}
          </div>
          <label className="chat-control chat-address-from-to chat-match-detail">
            <button type="button" className="chat-label" onClick={() => void inspectId("FROM", you)}>From</button>
            <select value={you} onChange={(event) => {const value=event.target.value;setYou(value);if(!value)setRequireFrom(false)}} aria-label="From agent identity">
              <option value="">(none/null)</option>
              {agentChoices.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </label>
          <label className="chat-control chat-address-from-to chat-match-detail">
            <button type="button" className="chat-label" onClick={() => void inspectId("TO", target)}>To</button>
            <select value={target} onChange={(event) => {const value=event.target.value;setTarget(value);if(!value)setRequireTo(false)}} aria-label="To agent identity">
              <option value="">(none/null)</option>
              {agentChoices.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </label>
          <label className="chat-control chat-address-send chat-match-detail">
            <button type="button" className="chat-label" onClick={() => void inspectId("SEND-TO", sendMailbox)}>Send-to</button>
            <StreamPicker value={sendMailbox} ids={sendChoices} ariaLabel="Send mailbox" allowNone describe={describeStream} onChange={setSendMailbox} />
          </label>
          <label className="chat-control chat-mbrow chat-mailbox-primary">
            <button type="button" className="chat-label" onClick={() => void inspectId("MAILBOX", mailbox)}>Mailbox</button>
            <StreamPicker value={mailbox} ids={mailboxChoices} ariaLabel="Viewed mailbox" describe={describeStream} onChange={selectMailbox} />
            <span className="chat-mbrow-actions">
              {personalCursor && (
                <span className="chat-mbrow-cursor" title={`Personal cursor for ${personalCursor} on this mailbox`}>
                  {cursorInfo
                    ? cursorInfo.initialized
                      ? `▸${cursorInfo.entry_next ?? "?"}/${cursorInfo.entries_total ?? "?"}`
                      : "no cursor"
                    : "…"}
                </span>
              )}
              <button type="button" className="chat-mbact" title="Move personal cursor to beginning" disabled={cursorBusy || !personalCursor} onClick={() => void moveCursor("beginning", mailbox)}>⏮</button>
              <button type="button" className="chat-mbact" title="Move personal cursor to now" disabled={cursorBusy || !personalCursor} onClick={() => void moveCursor("now", mailbox)}>⏭</button>
              <button type="button" className="chat-mbact" title="Remove cursor" disabled={cursorBusy || !(cursorInfo && cursorInfo.initialized)} onClick={() => void moveCursor("remove", mailbox)}>⌫</button>
              <button type="button" className={`chat-mbact${showMailboxListSettings ? " active" : ""}`} aria-expanded={showMailboxListSettings} title="Arrange mailbox list" onClick={() => setShowMailboxListSettings((value) => !value)}>☷</button>
              <button type="button" className="chat-mbact" title="Show this mailbox's JSON (definition, members for a merge)" disabled={!mailbox} onClick={() => void inspectId("MAILBOX", mailbox)}>{"{ }"}</button>
            </span>
          </label>
          {showMailboxListSettings && (
            <section className="chat-mailbox-arranger chat-stream-configuration chat-match-detail" aria-label="Mailbox list arrangement">
              <header>
                <b>Mailbox list</b>
                <span>Numbers are messages past {personalCursor}'s cursor.</span>
                <small>
                  Field cache · mailbox definitions {cachedGroupFields.length} · chat bubbles {cachedBubbleFields.length} · limit {fieldCacheConfig.defaultLimit ?? "?"} · {Object.keys(fieldCacheConfig.records).length} config records
                </small>
              </header>
              <label>
                <span>Sort</span>
                <select value={mailboxSortMode} onChange={(event) => setMailboxSortMode(event.target.value as MailboxSortMode)}>
                  <option value="name">Name</option>
                  <option value="activity-minute">Activity · per minute</option>
                  <option value="activity-hour">Activity · per hour</option>
                  <option value="unread">Unread messages</option>
                </select>
              </label>
              <label>
                <span>Group by</span>
                <select value={mailboxGroupField} onChange={(event) => setMailboxGroupField(event.target.value)}>
                  {groupFieldOptions.map((field) => <option key={field} value={field}>{fieldLabel(field)}</option>)}
                </select>
              </label>
              <label>
                <span>When selected</span>
                <select value={mailboxOpenMode} onChange={(event) => setMailboxOpenMode(event.target.value as MailboxOpenMode)}>
                  <option value="last-read">Resume at last read</option>
                  <option value="end-mark-read">Go to end and mark read</option>
                </select>
              </label>
              <label className="chat-mailbox-arranger-check">
                <input type="checkbox" checked={advanceCursorOnView} onChange={(event) => setAdvanceCursorOnView(event.target.checked)} />
                <span>Advance cursor when the end is viewed</span>
              </label>
            </section>
          )}
          {mergeMailboxes.map((mb, index) => (
            <label className="chat-control chat-mbrow chat-mailbox-merged" key={`merge-row-${index}`}>
              <span className="chat-label">＋ Mailbox</span>
              <StreamPicker
                value={mb}
                ids={mailboxChoices}
                ariaLabel={`Merged mailbox ${index + 1}`}
                allowNone
                describe={describeStream}
                onChange={(v) => setMergeMailboxes((rows) => rows.map((row, j) => (j === index ? v : row)))}
              />
              <span className="chat-mbrow-actions">
                <button type="button" className="chat-mbact" title="Move personal cursor to beginning" disabled={cursorBusy || !mb || !personalCursor} onClick={() => void moveCursor("beginning", mb)}>⏮</button>
                <button type="button" className="chat-mbact" title="Move personal cursor to now" disabled={cursorBusy || !mb || !personalCursor} onClick={() => void moveCursor("now", mb)}>⏭</button>
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
          <label className="chat-control chat-mbrow chat-mailbox-add">
            <button
              type="button"
              className="chat-label"
              title="Add another mailbox to merge into the view"
              onClick={() => setMergeMailboxes((rows) => [...rows, ""])}
            >
              ＋ Add mailbox
            </button>
            <button
              type="button"
              className="chat-mbact"
              title="Register a JSON/JSONL file (under the server state dir) as a read-only virtual stream"
              onClick={() => void registerDiskFile()}
            >
              📄 Add file stream
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
          <label className="chat-control chat-mbrow chat-stream-configuration chat-match-detail">
            <button
              type="button"
              className="chat-label"
              title="Show or hide message layout and color options"
              onClick={() => setShowDisplay((v) => !v)}
            >
              {showDisplay ? "▾" : "▸"} {`Stream configuration panel for ${mailboxLabel(mailbox)}`}
            </button>
            <select
              className="chat-scope"
              value={scope}
              onChange={(event) => setScope(event.target.value)}
              aria-label="Settings scope"
              title="Which profile these settings come from and are saved to"
            >
              <option value="">workspace default</option>
              {[...new Set([mailbox, ...mergeMailboxes].filter(Boolean))].map((id) => (
                <option key={id} value={id}>{`${mailboxLabel(id)}${mailboxViews[id] ? " ✓" : ""}`}</option>
              ))}
            </select>
            {scope && mailboxViews[scope] && (
              <button
                type="button"
                className="chat-mbact"
                title="Delete this mailbox's override and revert it to the workspace default"
                onClick={() => setMailboxViews((m) => { const n = { ...m }; delete n[scope]; return n; })}
              >
                ⟲ Reset
              </button>
            )}
          </label>
          {showDisplay && (
            <div className="chat-display-settings chat-match-detail">
          <label className="chat-control chat-mbrow">
            <span className="chat-label" title="Where to place message bubbles">Place</span>
            <select
              value={activeView.placement}
              onChange={(event) => patchActive({ placement: event.target.value })}
              aria-label="Message placement"
            >
              <option value="sender">by sender (you right)</option>
              <option value="left">all left</option>
              <option value="right">all right</option>
              <option value="center">centered</option>
              <option value="full">full width</option>
              <option value="field">by field…</option>
            </select>
            {activeView.placement === "field" && (
              <select
                value={activeView.placementField}
                onChange={(event) => patchActive({ placementField: event.target.value })}
                aria-label="Placement field"
                title="Each distinct value of this field gets its own lane"
              >
                {fieldOptions(activeView.placementField)}
              </select>
            )}
          </label>
          <label className="chat-control chat-mbrow">
            <span className="chat-label" title="Bubble border color">Border</span>
            <select
              value={activeView.borderMode}
              onChange={(event) => patchActive({ borderMode: event.target.value })}
              aria-label="Border color"
            >
              <option value="sender">by sender (you/them)</option>
              <option value="uniform">uniform</option>
              <option value="field">by field…</option>
            </select>
            {activeView.borderMode === "field" && (
              <select
                value={activeView.borderField}
                onChange={(event) => patchActive({ borderField: event.target.value })}
                aria-label="Border field"
                title="Each distinct value of this field gets its own border hue"
              >
                {fieldOptions(activeView.borderField)}
              </select>
            )}
            {activeView.borderMode === "uniform" && (
              <input
                type="color"
                className="chat-color"
                value={activeView.borderColor || "#4eabda"}
                onChange={(event) => patchActive({ borderColor: event.target.value })}
                aria-label="Border color value"
                title="Pick the uniform border color"
              />
            )}
          </label>
          <label className="chat-control chat-mbrow">
            <span className="chat-label" title="Bubble fill color">Fill</span>
            <select
              value={activeView.fillMode}
              onChange={(event) => patchActive({ fillMode: event.target.value })}
              aria-label="Fill color"
            >
              <option value="sender">by sender (you/them)</option>
              <option value="uniform">uniform</option>
              <option value="field">by field…</option>
            </select>
            {activeView.fillMode === "field" && (
              <select
                value={activeView.fillField}
                onChange={(event) => patchActive({ fillField: event.target.value })}
                aria-label="Fill field"
                title="Each distinct value of this field gets its own fill hue"
              >
                {fieldOptions(activeView.fillField)}
              </select>
            )}
            {activeView.fillMode === "uniform" && (
              <input
                type="color"
                className="chat-color"
                value={activeView.fillColor || "#2b3a44"}
                onChange={(event) => patchActive({ fillColor: event.target.value })}
                aria-label="Fill color value"
                title="Pick the uniform fill color"
              />
            )}
          </label>
          {activeView.bubbleFields.map((entry, index) => (
            <label className="chat-control chat-mbrow" key={`bubble-field-${index}`}>
              <span className="chat-label">{index === 0 ? "Fields" : "＋ Field"}</span>
              <select
                value={entry.field}
                onChange={(e) => patchActive({ bubbleFields: activeView.bubbleFields.map((r, j) => (j === index ? { ...r, field: e.target.value } : r)) })}
                aria-label={`Bubble field ${index + 1}`}
              >
                {bubbleFieldChoices.map((k) => (
                  <option key={k} value={k}>{FIELD_LABELS[k] ?? k}</option>
                ))}
              </select>
              <select
                value={entry.style}
                onChange={(e) => patchActive({ bubbleFields: activeView.bubbleFields.map((r, j) => (j === index ? { ...r, style: e.target.value } : r)) })}
                aria-label={`Bubble field ${index + 1} style`}
                title="How this field is displayed on the bubble"
              >
                {BUBBLE_STYLES.map(([v, lbl]) => (
                  <option key={v} value={v}>{lbl}</option>
                ))}
              </select>
              <span className="chat-mbrow-actions">
                <button
                  type="button"
                  className="chat-mbact"
                  title="Move up"
                  disabled={index === 0}
                  onClick={() => patchActive({ bubbleFields: (() => { const a = [...activeView.bubbleFields]; [a[index - 1], a[index]] = [a[index], a[index - 1]]; return a; })() })}
                >
                  ↑
                </button>
                <button
                  type="button"
                  className="chat-mbact"
                  title="Move down"
                  disabled={index === activeView.bubbleFields.length - 1}
                  onClick={() => patchActive({ bubbleFields: (() => { const a = [...activeView.bubbleFields]; [a[index + 1], a[index]] = [a[index], a[index + 1]]; return a; })() })}
                >
                  ↓
                </button>
                <button
                  type="button"
                  className="chat-mbact"
                  title="Remove this field from the bubble"
                  onClick={() => patchActive({ bubbleFields: activeView.bubbleFields.filter((_, j) => j !== index) })}
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
              title="Show another field on each bubble"
              onClick={() => { const used = new Set(activeView.bubbleFields.map((r) => r.field)); const next = bubbleFieldChoices.find((k) => !used.has(k)) || "type"; patchActive({ bubbleFields: [...activeView.bubbleFields, { field: next, style: "text" }] }); }}
            >
              ＋ Add field
            </button>
          </label>
          <label className="chat-control chat-mbrow">
            <span className="chat-label" title="Where the render-rule value suggestions come from">Value suggestions</span>
            <select
              value={activeView.valueSource}
              onChange={(e) => patchActive({ valueSource: e.target.value })}
              aria-label="Value suggestion source"
            >
              <option value="view">Current view (in memory)</option>
              <option value="cache">Saved cache (all streams)</option>
              <option value="stream">{`This stream only (${activeStream || "—"})`}</option>
            </select>
          </label>
          {activeView.renderRules.map((r, index) => (
            <label className="chat-control chat-mbrow" key={`render-rule-${index}`}>
              <span className="chat-label">{index === 0 ? "Render if" : "else if"}</span>
              <select
                value={r.field}
                onChange={(e) => patchActive({ renderRules: activeView.renderRules.map((x, j) => (j === index ? { ...x, field: e.target.value } : x)) })}
                aria-label={`Render rule ${index + 1} field`}
              >
                <option value="">(field)</option>
                {fieldStats.fields.map((k) => (
                  <option key={k} value={k}>{FIELD_LABELS[k] ?? k}</option>
                ))}
              </select>
              <input
                className="chat-rule-value"
                value={r.value}
                list={`chat-rvals-${index}`}
                onChange={(e) => patchActive({ renderRules: activeView.renderRules.map((x, j) => (j === index ? { ...x, value: e.target.value } : x)) })}
                placeholder="= value (blank = any)"
                aria-label={`Render rule ${index + 1} value`}
              />
              <datalist id={`chat-rvals-${index}`}>
                {valueCandidates(r.field).map((v) => (
                  <option key={v} value={v} />
                ))}
              </datalist>
              <select
                value={r.mode}
                onChange={(e) => patchActive({ renderRules: activeView.renderRules.map((x, j) => (j === index ? { ...x, mode: e.target.value } : x)) })}
                aria-label={`Render rule ${index + 1} mode`}
              >
                {RENDER_MODES.map(([v, lbl]) => (
                  <option key={v} value={v}>{lbl}</option>
                ))}
              </select>
              <span className="chat-mbrow-actions">
                <button
                  type="button"
                  className="chat-mbact"
                  title="Remove this render rule"
                  onClick={() => patchActive({ renderRules: activeView.renderRules.filter((_, j) => j !== index) })}
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
              title="Add a rule that overrides the default rendering"
              onClick={() => patchActive({ renderRules: [...activeView.renderRules, { field: "type", value: "", mode: "json" }] })}
            >
              ＋ Add render rule
            </button>
          </label>
          <label className="chat-control chat-mbrow">
            <span className="chat-label" title="Default body rendering (overridden by any matching rule above)">Render</span>
            <select value={activeView.renderMode} onChange={(e) => patchActive({ renderMode: e.target.value })} aria-label="Default render mode">
              {RENDER_MODES.map(([v, lbl]) => (
                <option key={v} value={v}>{lbl}</option>
              ))}
            </select>
          </label>
            </div>
          )}
          <div className="chat-make chat-match-detail">
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
            <div className="chat-sub chat-match-detail">
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
            <div className="chat-inspect chat-match-detail">
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
          <div className="chat-controls-divider" aria-hidden="true" />
        </div>
      )}
      {!showMailboxPicker && (
        <div className="chat-tabs" role="tablist">
          <button type="button" role="tab" aria-selected={paneTab === "chat"} className={`chat-tab${paneTab === "chat" ? " is-active" : ""}`} onClick={() => setPaneTab("chat")}>Chat</button>
          <button type="button" role="tab" aria-selected={paneTab === "file"} className={`chat-tab${paneTab === "file" ? " is-active" : ""}`} onClick={() => { if (paneTab !== "file") openStreamFile(); }}>File</button>
          <button type="button" role="tab" aria-selected={paneTab === "config"} className={`chat-tab${paneTab === "config" ? " is-active" : ""}`} onClick={() => setPaneTab("config")}>Config</button>
        </div>
      )}
      {paneTab === "chat" && (
      <div className="chat-messages" ref={listRef} onScroll={handleScroll}>
        {ready && messages.length === 0 && (
          <div className="chat-empty">No messages match the required filters.</div>
        )}
        {messages.map((message) => (
          <div
            key={`${message.id}|${message.timestamp || ""}`}
            data-message-id={message.id}
            data-mailbox-id={message.mailboxId || ""}
            className={`chat-message ${message.from === you ? "mine" : "theirs"}${
              placementClass(message) ? " " + placementClass(message) : ""
            }${entryEditKey === bubbleKey(message) ? " editing" : ""}${selectedMessageKey === bubbleKey(message) ? " selected" : ""}`}
            style={messageColorStyle(message)}
            role="button"
            tabIndex={0}
            aria-pressed={selectedMessageKey === bubbleKey(message)}
            onClick={event=>{if((event.target as HTMLElement).closest("button,input,textarea,select,a"))return;selectStreamNode(message)}}
            onKeyDown={event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();selectStreamNode(message)}}}
          >
            <div className="chat-message-meta">
              {effectiveView(message).bubbleFields.map((entry, i) => renderBubbleField(message, entry, `bf-${i}`))}
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
            {renderBody(message)}
            {(expanded[message.id] ?? (effectiveMode(message) === "markdown" && !message.text)) && entryEditKey !== bubbleKey(message) && (
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
      )}
      {paneTab === "file" && (
        <div className="chat-filepane">
          {streamFileNote&&<div className="chat-filepane-note">{streamFileNote}</div>}
          <SuperControl appearance="embedded" control={streamSuperControl} className="chat-file-super-control" />
        </div>
      )}
      {paneTab === "config" && (
        <div className="chat-config" role="tabpanel" aria-label="Mailbox configuration">
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
            spellCheck={false}
            aria-label="Mailbox config JSON"
          />
          {configError && <div className="chat-error">{configError}</div>}
          {configNote && <div className="chat-config-note">{configNote}</div>}
        </div>
      )}
      {errorText && <div className="chat-error">{errorText}</div>}
      <div className="chat-composer">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={you&&target?`Message ${target}… (Enter to send, Shift+Enter for newline)`:"Select FROM and TO to send"}
          rows={2}
          disabled={sending}
        />
        <button className="chat-send" onClick={send} disabled={sending || !input.trim() || !you || !target}>
          {sending ? "Sending…" : "Send"}
        </button>
      </div>
    </div>
  );
}
