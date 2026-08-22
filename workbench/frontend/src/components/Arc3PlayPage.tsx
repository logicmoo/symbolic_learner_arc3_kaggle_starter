import { useCallback, useEffect, useMemo, useRef, useState, type MouseEvent as ReactMouseEvent } from "react";
import { type WorkflowPageDefinition } from "./WorkflowPageHost";
import { Arc3B1B2PipelinePage, type ModelChoice, type WorkspaceFileRecord } from "./Arc3B1B2PipelinePage";
import "../styles/arc3_play.css";

type Props = {
  pageDefinition: WorkflowPageDefinition;
  workspaceId: string;
  workspaceLabel: string;
  b1b2PageDefinition?: WorkflowPageDefinition;
  b1b2Models?: ModelChoice[];
  b1b2Files?: WorkspaceFileRecord[];
  onB1B2PageDefinitionSaved?: () => Promise<unknown> | unknown;
};

type GameInfo = {
  game_id: string;
  short_id?: string;
  title?: string;
  tags?: string[];
  level_count?: number | null;
};

type PlayAction = {
  id: string;
  label: string;
  complex: boolean;
  enabled: boolean;
};

type PlayMove = {
  index: number;
  action: string;
  data: Record<string, number>;
  directory: string;
  state?: string | null;
  level?: string | null;
  recorded_at?: string;
  level_completed?: string;
};

type ReplayOp = {
  op: string;
  action?: string;
  data?: Record<string, number>;
  directory?: string | null;
  level?: string | null;
};

type PlaySessionSnapshot = {
  id: string;
  workspaceId: string;
  gameId: string;
  gameDirectory: string;
  createdAt: string;
  closed: boolean;
  state?: string | null;
  level?: string | null;
  moveCount: number;
  levelMoveCount: number;
  levelDir: string;
  levelDirs: string[];
  framePath?: string | null;
  forkedFrom?: string | null;
  availableActions: PlayAction[];
  replayLog?: ReplayOp[];
  moves?: PlayMove[];
  recordingsPath?: string;
  recordingsPathIsDefault?: boolean;
};

type PlaySavepoint = {
  id: string;
  created_at: string;
  label?: string | null;
  game_id: string;
  game_directory: string;
  level?: string | null;
  level_directory?: string | null;
  move_index?: number | null;
  state?: string | null;
  move_total?: number;
};

type PlayRecording = {
  path: string;
  name: string;
  gameId?: string | null;
  sizeBytes?: number;
  kind?: "human-jsonl" | "release-run" | null;
  totalActions?: number | null;
};

const FRAME_SCALE = 10;

async function request(path: string, init?: RequestInit) {
  const response = await fetch(path, {
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  const raw = await response.text();
  let payload: Record<string, unknown> = {};
  try {
    payload = raw ? (JSON.parse(raw) as Record<string, unknown>) : {};
  } catch {
    payload = {};
  }
  if (!response.ok) {
    const detail = payload.error ?? payload.detail ?? raw ?? response.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return payload;
}

const KEY_TO_ACTION: Record<string, string> = {
  ArrowUp: "ACTION1",
  ArrowDown: "ACTION2",
  ArrowLeft: "ACTION3",
  ArrowRight: "ACTION4",
  " ": "ACTION5",
};

export function Arc3PlayPage({
  pageDefinition,
  workspaceId,
  workspaceLabel,
  b1b2PageDefinition,
  b1b2Models,
  b1b2Files,
  onB1B2PageDefinitionSaved,
}: Props) {
  const [games, setGames] = useState<GameInfo[]>([]);
  const [gamesLoading, setGamesLoading] = useState(false);
  const [session, setSession] = useState<PlaySessionSnapshot | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [armedAction, setArmedAction] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [recordingsPathDraft, setRecordingsPathDraft] = useState("");
  const [savepoints, setSavepoints] = useState<PlaySavepoint[]>([]);
  const [recordings, setRecordings] = useState<PlayRecording[]>([]);
  const [importNote, setImportNote] = useState("");
  const [retainLargestCount, setRetainLargestCount] = useState("10");
  const [rewindOpen, setRewindOpen] = useState(false);
  const [rewindHover, setRewindHover] = useState<number | null>(null);
  const [autoSelect, setAutoSelect] = useState(true);
  const [inspectOrdinal, setInspectOrdinal] = useState<number | null>(null);
  const [inspectScan, setInspectScan] = useState<Record<string, string[]> | null>(null);
  const [inspectLoading, setInspectLoading] = useState(false);
  const [inspectCopied, setInspectCopied] = useState(false);
  const [replayScript, setReplayScript] = useState<ReplayOp[] | null>(null);
  const [replayPos, setReplayPos] = useState(0);
  const [replayPlaying, setReplayPlaying] = useState(false);
  const [replaySpeedMs, setReplaySpeedMs] = useState(300);
  const [timelineHover, setTimelineHover] = useState<number | null>(null);
  const [selectedGameId, setSelectedGameId] = useState("");
  const [filterGameId, setFilterGameId] = useState("");
  const [expandedMoveDir, setExpandedMoveDir] = useState<string | null>(null);
  const [moveScanResults, setMoveScanResults] = useState<Record<string, Record<string, string[]> | null>>({});
  const [moveScanLoading, setMoveScanLoading] = useState<string | null>(null);
  const [collapsedSections, setCollapsedSections] = useState<Record<string, boolean>>({});
  const toggleSection = (key: string) =>
    setCollapsedSections((current) => ({ ...current, [key]: !current[key] }));
  const boardRef = useRef<HTMLImageElement | null>(null);
  const columnsRef = useRef<HTMLDivElement | null>(null);
  const [colWidths, setColWidths] = useState<{ left: number; right: number }>(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("arc3PlayColWidths") || "null") as {
        left?: number;
        right?: number;
      } | null;
      if (saved && typeof saved.left === "number" && typeof saved.right === "number") {
        return { left: saved.left, right: saved.right };
      }
    } catch {
      // fall through to defaults
    }
    return { left: 220, right: 340 };
  });

  useEffect(() => {
    try {
      localStorage.setItem("arc3PlayColWidths", JSON.stringify(colWidths));
    } catch {
      // storage unavailable — widths just won't persist
    }
  }, [colWidths]);

  const startColumnDrag = (side: "left" | "right") => (event: ReactMouseEvent) => {
    event.preventDefault();
    const startX = event.clientX;
    const startWidth = colWidths[side];
    const onMove = (move: MouseEvent) => {
      const delta = move.clientX - startX;
      setColWidths((current) => {
        const total = columnsRef.current?.clientWidth ?? 1200;
        const other = side === "left" ? current.right : current.left;
        const raw = side === "left" ? startWidth + delta : startWidth - delta;
        const max = Math.max(140, total - other - 260);
        const next = Math.min(Math.max(140, raw), max);
        return side === "left" ? { ...current, left: next } : { ...current, right: next };
      });
    };
    const onUp = () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
      document.body.style.cursor = "";
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    document.body.style.cursor = "col-resize";
  };

  // Embed only the B1 -> B2 "Run B1 Then B2" runner-stack panel (its center
  // column) in the Play page's left column; the B1B2 page's own DATA/SOURCE
  // columns are emptied here since Play already has its own recording panels.
  const b1b2CenterOnlyDefinition = useMemo<WorkflowPageDefinition | null>(() => {
    if (!b1b2PageDefinition) return null;
    const columns = (b1b2PageDefinition.layout?.columns || []).map((column) =>
      column.id === "center" ? column : { ...column, members: [] },
    );
    return { ...b1b2PageDefinition, layout: { ...b1b2PageDefinition.layout, columns } };
  }, [b1b2PageDefinition]);

  const assetUrl = useCallback(
    (path: string) => `/api/workspaces/${encodeURIComponent(workspaceId)}/asset?path=${encodeURIComponent(path)}`,
    [workspaceId],
  );

  const loadGames = useCallback(async (refresh: boolean) => {
    setGamesLoading(true);
    setError("");
    try {
      const payload = await request(`/api/arc3-play/games${refresh ? "?refresh=true" : ""}`);
      setGames((payload.games as GameInfo[]) || []);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setGamesLoading(false);
    }
  }, []);

  // Resuming a save-point (or fast-forwarding an auto-imported recording)
  // used to drop straight into the ending state with no way to look back.
  // Populate the timeline from the resumed session's own replay log instead
  // -- positioned at the end (so play continues live from where it left
  // off) but fully scrubbable, so a slide/click on any tick steps back to
  // that point in the run.
  const applyResumedSession = useCallback((snap: PlaySessionSnapshot) => {
    setSession(snap);
    const script = (snap.replayLog || []).filter((op) => op.op === "step" || op.op === "reset");
    setReplayScript(script.length > 0 ? script : null);
    setReplayPos(script.length);
  }, []);

  useEffect(() => {
    void loadGames(false);
  }, [loadGames]);

  // Deep-link support: the games gallery page's "Play & Record" button
  // navigates here with ?game=<shortId>. This preselects the picker AND
  // turns Filter on for that game AND refreshes the games catalog, then
  // tries to auto-resume the game's most recent progress: first the
  // latest matching IMPORTABLES recording (auto-imported, which itself
  // creates a save-point), else the latest matching RESTART-POINT
  // (save-point) for the game -- so a double-click from the gallery lands
  // you back where you left off rather than a blank new session. Runs
  // once per page load (guarded against React StrictMode's dev-only
  // double-invoke); if neither a recording nor a save-point exists, the
  // picker/filter still land correctly and the effect below falls back
  // to the first catalog game if this id turns out to be invalid/unknown.
  const deepLinkHandledRef = useRef(false);
  useEffect(() => {
    const requested = new URLSearchParams(window.location.search).get("game");
    if (!requested) return;
    setSelectedGameId(requested);
    setFilterGameId(requested);
    if (deepLinkHandledRef.current) return;
    deepLinkHandledRef.current = true;
    void loadGames(true);
    void (async () => {
      try {
        const [savepointsPayload, recordingsPayload] = await Promise.all([
          request(`/api/arc3-play/savepoints?workspaceId=${encodeURIComponent(workspaceId)}`),
          request(`/api/arc3-play/recordings?workspaceId=${encodeURIComponent(workspaceId)}`),
        ]);
        const freshSavepoints = (savepointsPayload.savepoints as PlaySavepoint[]) || [];
        const freshRecordings = (recordingsPayload.recordings as PlayRecording[]) || [];
        setSavepoints(freshSavepoints);
        setRecordings(freshRecordings);

        const matchingRecordings = freshRecordings.filter((recording) => recording.gameId === requested);
        const lastRecording = matchingRecordings[matchingRecordings.length - 1];
        let savepointId: string | null = null;
        if (lastRecording) {
          const imported = await request("/api/arc3-play/import-recording", {
            method: "POST",
            body: JSON.stringify({ workspaceId, path: lastRecording.path }),
          });
          savepointId = (imported.savepoint as { id?: string } | undefined)?.id || null;
          const refreshed = await request(`/api/arc3-play/savepoints?workspaceId=${encodeURIComponent(workspaceId)}`);
          setSavepoints((refreshed.savepoints as PlaySavepoint[]) || []);
        }
        if (!savepointId) {
          // Savepoints are already newest-first from the server, so the
          // first match here is the most recent restart-point.
          savepointId = freshSavepoints.find((point) => point.game_directory === requested)?.id || null;
        }
        if (!savepointId) return;
        const payload = await request("/api/arc3-play/sessions", {
          method: "POST",
          body: JSON.stringify({ workspaceId, savepointId }),
        });
        applyResumedSession(payload.session as PlaySessionSnapshot);
      } catch (reason) {
        setError(reason instanceof Error ? reason.message : String(reason));
      }
    })();
  }, []);

  useEffect(() => {
    if (!games.length) return;
    if (selectedGameId && games.some((game) => (game.short_id || game.game_id) === selectedGameId)) return;
    setSelectedGameId(games[0].short_id || games[0].game_id);
  }, [games, selectedGameId]);

  // Keep the editable recordings-path field synced with the current
  // session's effective path (server-authoritative; blank when it's on
  // the default data/Recordings/<game>/ location, so "Set" only submits
  // an explicit override).
  useEffect(() => {
    setRecordingsPathDraft(session && !session.recordingsPathIsDefault ? session.recordingsPath || "" : "");
  }, [session?.id, session?.recordingsPath, session?.recordingsPathIsDefault]);

  const loadSavepoints = useCallback(async () => {
    try {
      const payload = await request(`/api/arc3-play/savepoints?workspaceId=${encodeURIComponent(workspaceId)}`);
      setSavepoints((payload.savepoints as PlaySavepoint[]) || []);
    } catch {
      setSavepoints([]);
    }
  }, [workspaceId]);

  useEffect(() => {
    void loadSavepoints();
  }, [loadSavepoints]);

  const loadRecordings = useCallback(async () => {
    try {
      const payload = await request(`/api/arc3-play/recordings?workspaceId=${encodeURIComponent(workspaceId)}`);
      setRecordings((payload.recordings as PlayRecording[]) || []);
    } catch {
      setRecordings([]);
    }
  }, [workspaceId]);

  useEffect(() => {
    void loadRecordings();
  }, [loadRecordings]);

  const perform = useCallback(async (work: () => Promise<void>) => {
    setBusy(true);
    setError("");
    try {
      await work();
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : String(reason);
      setError(message);
      if (message.includes("unknown play session")) {
        // Backend lost the session (e.g. reload) — flip to closed so
        // START SESSION and fork-from-history become available.
        setSession((current) => (current ? { ...current, closed: true } : current));
      }
    } finally {
      setBusy(false);
    }
  }, []);

  const startGame = (gameId: string) =>
    perform(async () => {
      if (session && !session.closed) {
        if (session.moveCount > 0) {
          // Jumping to another game: save the abandoned position first.
          await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/fork`, {
            method: "POST",
            body: JSON.stringify({ label: `auto save (switched to ${gameId})` }),
          }).catch(() => undefined);
        }
        await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}`, { method: "DELETE" }).catch(() => undefined);
      }
      const payload = await request("/api/arc3-play/sessions", {
        method: "POST",
        body: JSON.stringify({ workspaceId, gameId }),
      });
      setArmedAction(null);
      setReplayScript(null);
      setReplayPlaying(false);
      setSession(payload.session as PlaySessionSnapshot);
      await loadSavepoints();
    });

  const refreshRecording = () =>
    perform(async () => {
      if (!session) return;
      const payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}`);
      setSession(payload.session as PlaySessionSnapshot);
    });

  const setRecordingsPath = (path: string | null) =>
    perform(async () => {
      if (!session) return;
      const payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/recordings-path`, {
        method: "PUT",
        body: JSON.stringify({ path }),
      });
      setSession(payload.session as PlaySessionSnapshot);
    });

  const playFromMove = (move: PlayMove) =>
    perform(async () => {
      if (!session) return;
      const log = session.replayLog || [];
      const cut = log.findIndex((entry) => entry.directory === move.directory);
      if (cut < 0) return;
      const payload = await request("/api/arc3-play/sessions", {
        method: "POST",
        body: JSON.stringify({
          workspaceId,
          gameId: session.gameDirectory,
          replayLog: log.slice(0, cut + 1),
          forkedFrom: `history ${move.directory}`,
        }),
      });
      setArmedAction(null);
      setReplayScript(null);
      setReplayPlaying(false);
      setSession(payload.session as PlaySessionSnapshot);
    });

  const sendAction = (actionId: string, x?: number, y?: number) =>
    perform(async () => {
      if (!session) return;
      const payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/action`, {
        method: "POST",
        body: JSON.stringify({ action: actionId, x, y }),
      });
      setReplayScript(null);
      setReplayPlaying(false);
      setSession(payload.session as PlaySessionSnapshot);
    });

  const resetAttempt = () =>
    perform(async () => {
      if (!session) return;
      const payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/reset`, { method: "POST" });
      setArmedAction(null);
      setReplayScript(null);
      setReplayPlaying(false);
      setSession(payload.session as PlaySessionSnapshot);
    });

  const restartGame = () =>
    perform(async () => {
      if (!session) return;
      const payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/restart`, { method: "POST" });
      setArmedAction(null);
      setReplayScript(null);
      setReplayPlaying(false);
      setSession(payload.session as PlaySessionSnapshot);
    });

  const undoMove = (count: number) =>
    perform(async () => {
      if (!session) return;
      const payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/undo`, {
        method: "POST",
        body: JSON.stringify({ count }),
      });
      setArmedAction(null);
      setReplayScript(null);
      setReplayPlaying(false);
      setSession(payload.session as PlaySessionSnapshot);
    });

  const forkSavepoint = () =>
    perform(async () => {
      if (!session) return;
      await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/fork`, {
        method: "POST",
        body: JSON.stringify({}),
      });
      await loadSavepoints();
    });

  const resumeSavepoint = (savepointId: string) =>
    perform(async () => {
      if (session && !session.closed) {
        await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}`, { method: "DELETE" }).catch(() => undefined);
      }
      const payload = await request("/api/arc3-play/sessions", {
        method: "POST",
        body: JSON.stringify({ workspaceId, savepointId }),
      });
      setArmedAction(null);
      setReplayPlaying(false);
      applyResumedSession(payload.session as PlaySessionSnapshot);
    });

  const loadSavepoint = (point: PlaySavepoint) =>
    perform(async () => {
      // Load = start a fresh session at move zero with the savepoint's
      // recipe queued, so it can be stepped through one move at a time.
      const detail = await request(
        `/api/arc3-play/savepoints/${encodeURIComponent(point.id)}?workspaceId=${encodeURIComponent(workspaceId)}`,
      );
      const full = detail.savepoint as PlaySavepoint & { replay_log?: ReplayOp[] };
      const script = (full.replay_log || []).filter((op) => op.op === "step" || op.op === "reset");
      if (session && !session.closed) {
        await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}`, { method: "DELETE" }).catch(() => undefined);
      }
      const payload = await request("/api/arc3-play/sessions", {
        method: "POST",
        body: JSON.stringify({ workspaceId, gameId: full.game_id || full.game_directory }),
      });
      setArmedAction(null);
      setSession(payload.session as PlaySessionSnapshot);
      setReplayScript(script);
      setReplayPos(0);
    });

  const stepReplay = () =>
    perform(async () => {
      if (!session || !replayScript || replayPos >= replayScript.length) return;
      const op = replayScript[replayPos];
      let payload;
      if (op.op === "reset") {
        payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/reset`, { method: "POST" });
      } else {
        payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/action`, {
          method: "POST",
          body: JSON.stringify({ action: op.action, x: op.data?.x, y: op.data?.y }),
        });
      }
      setSession(payload.session as PlaySessionSnapshot);
      setReplayPos(replayPos + 1);
    });

  // Auto-play: while replayPlaying, step on a timer that reschedules itself
  // after each move lands (via the busy/replayPos deps), so Pause always
  // freezes at the current position and Play resumes from right there.
  useEffect(() => {
    if (!replayPlaying || !replayScript || busy) return;
    if (replayPos >= replayScript.length) {
      setReplayPlaying(false);
      return;
    }
    const timer = window.setTimeout(() => {
      void stepReplay();
    }, replaySpeedMs);
    return () => window.clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [replayPlaying, replayPos, busy, replayScript, replaySpeedMs]);

  // Chapter markers: tick index -> level label, at every position where the
  // move's directory crosses into a new attempt directory (a fresh
  // saved_<NNN>/import-named/level_<n>_<rank> dir). The label itself comes
  // from each op's own "level" field rather than being parsed out of the
  // directory name, since directory names no longer encode the level.
  const chapterStarts = useMemo(() => {
    const starts = new Map<number, string>();
    if (!replayScript) return starts;
    let prevLevelKey: string | null = null;
    replayScript.forEach((op, i) => {
      if (op.op !== "step" || !op.directory) return;
      const lastSlash = op.directory.lastIndexOf("/");
      const levelKey = lastSlash >= 0 ? op.directory.slice(0, lastSlash) : op.directory;
      if (levelKey !== prevLevelKey) {
        starts.set(i + 1, op.level || "?");
        prevLevelKey = levelKey;
      }
    });
    return starts;
  }, [replayScript]);

  const takeBackReplay = () =>
    perform(async () => {
      if (!session || !replayScript || replayPos <= 0) return;
      const previous = replayScript[replayPos - 1];
      if (previous.op === "step" && session.levelMoveCount > 0) {
        const payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/undo`, {
          method: "POST",
          body: JSON.stringify({ count: 1 }),
        });
        setSession(payload.session as PlaySessionSnapshot);
      } else {
        // Crossed a level/reset boundary: rebuild the session up to the
        // previous position by replaying the truncated recipe.
        await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}`, { method: "DELETE" }).catch(() => undefined);
        const payload = await request("/api/arc3-play/sessions", {
          method: "POST",
          body: JSON.stringify({
            workspaceId,
            gameId: session.gameId || session.gameDirectory,
            replayLog: replayScript.slice(0, replayPos - 1),
            forkedFrom: "replay step-back",
          }),
        });
        setSession(payload.session as PlaySessionSnapshot);
      }
      setReplayPos(replayPos - 1);
    });

  const seekReplay = (target: number) =>
    perform(async () => {
      if (!session || !replayScript) return;
      const clamped = Math.max(0, Math.min(target, replayScript.length));
      if (clamped === replayPos) return;
      setReplayPlaying(false);
      // Uniform for forward or backward jumps: rebuild the session by
      // replaying the recipe up to the clicked timeline position.
      await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}`, { method: "DELETE" }).catch(() => undefined);
      const payload = await request("/api/arc3-play/sessions", {
        method: "POST",
        body: JSON.stringify({
          workspaceId,
          gameId: session.gameId || session.gameDirectory,
          replayLog: replayScript.slice(0, clamped),
          forkedFrom: `replay seek ${clamped}`,
        }),
      });
      setSession(payload.session as PlaySessionSnapshot);
      setReplayPos(clamped);
    });

  const dedupeSavepoints = () =>
    perform(async () => {
      const payload = await request(`/api/arc3-play/savepoints/dedupe?workspaceId=${encodeURIComponent(workspaceId)}`, {
        method: "POST",
      });
      setImportNote(`de-duplicated save-points: removed ${payload.removed ?? 0}`);
      await loadSavepoints();
    });

  const dedupeRecordings = () =>
    perform(async () => {
      const payload = await request(`/api/arc3-play/recordings/dedupe?workspaceId=${encodeURIComponent(workspaceId)}`, {
        method: "POST",
      });
      setImportNote(`de-duplicated recordings: removed ${payload.count ?? 0} stale level dir(s)`);
      await loadSavepoints();
    });

  const sortRecordingsBySize = () =>
    perform(async () => {
      const gameParam = filterGameId ? `&gameId=${encodeURIComponent(filterGameId)}` : "";
      const payload = await request(
        `/api/arc3-play/recordings/sort-by-size?workspaceId=${encodeURIComponent(workspaceId)}${gameParam}`,
        { method: "POST" },
      );
      setImportNote(`sorted by size: renamed ${payload.count ?? 0} imported dir(s)`);
      await loadSavepoints();
    });

  const retainLargestRecordings = () =>
    perform(async () => {
      const keep = Math.max(0, parseInt(retainLargestCount, 10) || 0);
      const gameParam = filterGameId ? `&gameId=${encodeURIComponent(filterGameId)}` : "";
      const payload = await request(
        `/api/arc3-play/recordings/retain-largest?workspaceId=${encodeURIComponent(workspaceId)}&keep=${keep}${gameParam}`,
        { method: "POST" },
      );
      setImportNote(`retained largest ${keep}: removed ${payload.count ?? 0} smaller imported dir(s)`);
      await loadSavepoints();
    });

  const duplicateSavepoint = (savepointId: string) =>
    perform(async () => {
      await request(
        `/api/arc3-play/savepoints/${encodeURIComponent(savepointId)}/duplicate?workspaceId=${encodeURIComponent(workspaceId)}`,
        { method: "POST" },
      );
      await loadSavepoints();
    });

  const deleteSavepoint = (savepointId: string) =>
    perform(async () => {
      await request(
        `/api/arc3-play/savepoints/${encodeURIComponent(savepointId)}?workspaceId=${encodeURIComponent(workspaceId)}`,
        { method: "DELETE" },
      );
      await loadSavepoints();
    });

  const importRecording = (recording: PlayRecording) =>
    perform(async () => {
      setImportNote("");
      const payload = await request("/api/arc3-play/import-recording", {
        method: "POST",
        body: JSON.stringify({ workspaceId, path: recording.path }),
      });
      const info = payload.imported as { moveCount?: number; gameDirectory?: string; state?: string } | undefined;
      setImportNote(
        `imported ${recording.name}: ${info?.moveCount ?? "?"} moves -> ${info?.gameDirectory ?? "?"} (${info?.state ?? "?"})`,
      );
      await loadSavepoints();
    });

  const importAllImportables = (list: PlayRecording[]) =>
    perform(async () => {
      setImportNote("");
      let imported = 0;
      let failed = 0;
      for (const recording of list) {
        try {
          await request("/api/arc3-play/import-recording", {
            method: "POST",
            body: JSON.stringify({ workspaceId, path: recording.path }),
          });
          imported += 1;
        } catch {
          failed += 1;
        }
      }
      setImportNote(
        `imported ${imported} of ${list.length} recording${list.length === 1 ? "" : "s"}` +
          (failed ? ` (${failed} failed)` : ""),
      );
      await loadSavepoints();
    });

  const importAllImportablesAsMovelists = (list: PlayRecording[]) =>
    perform(async () => {
      setImportNote("");
      let imported = 0;
      let failed = 0;
      for (const recording of list) {
        try {
          await request("/api/arc3-play/import-movelist", {
            method: "POST",
            body: JSON.stringify({ workspaceId, path: recording.path }),
          });
          imported += 1;
        } catch {
          failed += 1;
        }
      }
      setImportNote(
        `imported ${imported} of ${list.length} move-list${list.length === 1 ? "" : "s"} (no images/state written)` +
          (failed ? ` (${failed} failed)` : ""),
      );
      await loadSavepoints();
    });

  const importAllRecordingsMoves = () =>
    perform(async () => {
      const gameParam = filterGameId ? `&gameId=${encodeURIComponent(filterGameId)}` : "";
      const payload = await request(
        `/api/arc3-play/recordings/import-movelists?workspaceId=${encodeURIComponent(workspaceId)}${gameParam}`,
        { method: "POST" },
      );
      setImportNote(`created ${payload.created ?? 0} move-list(s) from existing Recordings`);
      await loadSavepoints();
    });

  const importAllMovelistsAsRecordings = () =>
    perform(async () => {
      const gameParam = filterGameId ? `&gameId=${encodeURIComponent(filterGameId)}` : "";
      const payload = await request(
        `/api/arc3-play/recordings/materialize-movelists?workspaceId=${encodeURIComponent(workspaceId)}${gameParam}`,
        { method: "POST" },
      );
      setImportNote(`materialized ${payload.count ?? 0} Recording(s) from move-lists`);
      await loadSavepoints();
    });

  const endSession = () =>
    perform(async () => {
      if (!session) return;
      const payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}`, { method: "DELETE" });
      setArmedAction(null);
      setSession(payload.session as PlaySessionSnapshot);
    });

  const handleActionButton = (action: PlayAction) => {
    if (!action.enabled || busy || !session || session.closed) return;
    if (action.complex) {
      setArmedAction((current) => (current === action.id ? null : action.id));
      return;
    }
    void sendAction(action.id);
  };

  const handleBoardClick = (event: React.MouseEvent<HTMLImageElement>) => {
    if (!session || session.closed || busy) return;
    // No armed action: fall back to an enabled coordinate action (CLICK).
    const fallback = !armedAction && autoSelect
      ? session.availableActions.find(
          (action) => action.complex && action.enabled && action.label.toUpperCase() === "CLICK",
        ) || session.availableActions.find((action) => action.complex && action.enabled)
      : null;
    const action = armedAction || (fallback ? fallback.id : null);
    if (!action) return;
    const image = boardRef.current;
    if (!image || !image.naturalWidth || !image.clientWidth) return;
    const bounds = image.getBoundingClientRect();
    const px = ((event.clientX - bounds.left) * image.naturalWidth) / bounds.width;
    const py = ((event.clientY - bounds.top) * image.naturalHeight) / bounds.height;
    const gx = Math.max(0, Math.floor(px / FRAME_SCALE));
    const gy = Math.max(0, Math.floor(py / FRAME_SCALE));
    setArmedAction(null);
    void sendAction(action, gx, gy);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (!session || session.closed || busy) return;
    const actionId = KEY_TO_ACTION[event.key];
    if (!actionId) return;
    const known = session.availableActions.find((action) => action.id === actionId);
    if (!known || !known.enabled) return;
    event.preventDefault();
    void sendAction(actionId);
  };

  const copyLevelDir = async () => {
    if (!session) return;
    try {
      await navigator.clipboard.writeText(session.levelDir);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  };

  const copyMoveDir = async (directory: string) => {
    try {
      await navigator.clipboard.writeText(directory);
      setInspectCopied(true);
      window.setTimeout(() => setInspectCopied(false), 1500);
    } catch {
      setInspectCopied(false);
    }
  };

  const loadMoveScan = useCallback(
    async (directory: string) => {
      setInspectLoading(true);
      try {
        const response = await fetch(assetUrl(`${directory}/state.json`), { cache: "no-store" });
        if (!response.ok) {
          setInspectScan(null);
          return;
        }
        const parsed = await response.json();
        const results = parsed && typeof parsed === "object" ? parsed.scan?.results : null;
        setInspectScan(results && typeof results === "object" ? results : null);
      } catch {
        setInspectScan(null);
      } finally {
        setInspectLoading(false);
      }
    },
    [assetUrl],
  );

  const toggleMoveExpand = (directory: string) => {
    setExpandedMoveDir((current) => (current === directory ? null : directory));
  };

  const scanMoveDir = useCallback(
    async (directory: string) => {
      setMoveScanLoading(directory);
      try {
        const response = await fetch(assetUrl(`${directory}/state.json`), { cache: "no-store" });
        if (!response.ok) {
          setMoveScanResults((current) => ({ ...current, [directory]: null }));
          return;
        }
        const parsed = await response.json();
        const results = parsed && typeof parsed === "object" ? parsed.scan?.results : null;
        setMoveScanResults((current) => ({ ...current, [directory]: results && typeof results === "object" ? results : null }));
      } catch {
        setMoveScanResults((current) => ({ ...current, [directory]: null }));
      } finally {
        setMoveScanLoading((current) => (current === directory ? null : current));
      }
    },
    [assetUrl],
  );

  const moves = session?.moves || [];
  const levelDirRank = new Map((session?.levelDirs || []).map((dir, idx) => [dir, idx] as const));
  const movesNumeric = [...moves].sort((a, b) => {
    const levelDirOf = (move: PlayMove) => move.directory.slice(0, move.directory.lastIndexOf("/"));
    const levelA = levelDirRank.get(levelDirOf(a)) ?? -1;
    const levelB = levelDirRank.get(levelDirOf(b)) ?? -1;
    if (levelA !== levelB) return levelA - levelB;
    return a.index - b.index;
  });
  const newestFirst = [...movesNumeric].reverse();
  const filteredSavepoints = filterGameId ? savepoints.filter((point) => point.game_directory === filterGameId) : savepoints;
  const filteredRecordings = filterGameId ? recordings.filter((recording) => recording.gameId === filterGameId) : recordings;
  const sortedRecordings = [...filteredRecordings].sort((a, b) => {
    const gameCompare = (a.gameId || "").localeCompare(b.gameId || "", undefined, { numeric: true, sensitivity: "base" });
    if (gameCompare !== 0) return gameCompare;
    return a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: "base" });
  });
  const levelMoves = session ? moves.filter((move) => move.directory.startsWith(`${session.levelDir}/`)) : [];
  const levelIndexByDir = new Map(levelMoves.map((move, idx) => [move.directory, idx] as const));
  const rewindUndoneDirs = new Set(
    rewindHover ? levelMoves.slice(-rewindHover).map((move) => move.directory) : [],
  );
  const rewindTargetDir = rewindHover
    ? levelMoves[levelMoves.length - rewindHover - 1]?.directory ?? null
    : null;
  const stateName = session?.state || "";
  const stateClass = stateName === "WIN" ? "win" : stateName === "GAME_OVER" ? "over" : "live";
  const actionLabels = new Map((session?.availableActions || []).map((action) => [action.id, action.label] as const));
  const actionShort = (action: string) => actionLabels.get(action) || action;
  const actionFull = (action: string) => {
    const label = actionLabels.get(action);
    return label && label !== action ? `${label} (${action})` : action;
  };

  return (
    <div className="arc3-play-page">
      <header className="arc3-play-header">
        <div>
          <h2>{pageDefinition.label || "Play & Record"}</h2>
          <small>
            {workspaceLabel} · every move is recorded to data/Recordings/&lt;game&gt;/saved_&lt;NNN&gt;/0..k for B1 -&gt; B2 setups
          </small>
        </div>
        <div className="arc3-play-game-picker">
          <select
            value={selectedGameId}
            disabled={busy || gamesLoading || !games.length}
            onChange={(event) => setSelectedGameId(event.target.value)}
          >
            {!games.length && <option value="">No games returned by the ARC engine.</option>}
            {games.map((game) => {
              const shortId = game.short_id || game.game_id;
              return (
                <option key={game.game_id} value={shortId}>
                  {shortId} — {game.title || game.game_id}
                </option>
              );
            })}
          </select>
          <button
            title="Scope SAVE-POINTS and IMPORTABLES below to the selected game"
            disabled={!selectedGameId}
            onClick={() => setFilterGameId((current) => (current === selectedGameId ? "" : selectedGameId))}
          >
            {filterGameId === selectedGameId && filterGameId ? "Filter: ON" : "Filter"}
          </button>
          <button
            disabled={busy || !selectedGameId}
            onClick={() => void startGame(selectedGameId)}
          >
            {session && !session.closed && session.gameDirectory === selectedGameId ? "Playing" : "Start new game"}
          </button>
          <button onClick={() => void loadGames(true)} disabled={gamesLoading}>
            {gamesLoading ? "Loading…" : "Refresh"}
          </button>
        </div>
        {error && <div className="arc3-play-error">{error}</div>}
      </header>
      <div
        className="arc3-play-columns"
        ref={columnsRef}
        style={{ gridTemplateColumns: `${colWidths.left}px 6px minmax(0, 1fr) 6px ${colWidths.right}px` }}
      >
        <section className="arc3-play-b1b2-column">
          <div className="arc3-play-section-title">
            <span>B1 -&gt; B2 RUNNER STACK</span>
          </div>
          {b1b2CenterOnlyDefinition ? (
            <Arc3B1B2PipelinePage
              pageDefinition={b1b2CenterOnlyDefinition}
              workspaceId={workspaceId}
              workspaceLabel={workspaceLabel}
              models={b1b2Models || []}
              files={b1b2Files || []}
              onPageDefinitionSaved={onB1B2PageDefinitionSaved || (() => {})}
            />
          ) : (
            <div className="arc3-play-empty">B1 -&gt; B2 runner stack unavailable (page definition not loaded).</div>
          )}
        </section>

        <div
          className="arc3-play-col-resizer"
          title="Drag to resize"
          onMouseDown={startColumnDrag("left")}
        />

        <section className="arc3-play-board-column">
          {!session && <div className="arc3-play-empty">Pick a game on the left to start playing and recording.</div>}
          {session && (
            <>
              <div className="arc3-play-status">
                <b>{session.gameDirectory}</b>
                <span className={`arc3-play-state ${stateClass}`}>{stateName || "?"}</span>
                <span>level {session.level}</span>
                <span>{session.levelMoveCount} moves this level</span>
                <span>{session.moveCount} total</span>
                {session.closed && <span className="arc3-play-state over">session closed</span>}
              </div>
              <div
                className={`arc3-play-board ${armedAction ? "armed" : ""}`}
                tabIndex={0}
                onKeyDown={handleKeyDown}
                title={
                  armedAction
                    ? `Click the board to send ${armedAction} at that cell`
                    : autoSelect && session.availableActions.some((action) => action.complex && action.enabled)
                      ? "Click a cell to auto-CLICK it · arrow keys / Space play directly"
                      : "Arrow keys / Space play directly"
                }
              >
                {session.framePath ? (
                  <img
                    ref={boardRef}
                    src={assetUrl(session.framePath)}
                    alt={`Current ${session.gameDirectory} frame`}
                    onClick={handleBoardClick}
                    draggable={false}
                  />
                ) : (
                  <div className="arc3-play-empty">No frame captured.</div>
                )}
              </div>
              {armedAction && (
                <div className="arc3-play-armed-note">
                  {armedAction} armed — click a board cell to fire it, or press the button again to disarm.
                </div>
              )}
              <div className="arc3-play-actions">
                {session.availableActions.map((action) => (
                  <button
                    key={action.id}
                    className={`arc3-play-action ${armedAction === action.id ? "armed" : ""}`}
                    disabled={!action.enabled || busy || session.closed}
                    onClick={() => handleActionButton(action)}
                    title={action.complex ? `${action.id}: arm, then click the board` : action.id}
                  >
                    {action.label}
                  </button>
                ))}
                {session.availableActions.some((action) => action.complex && action.enabled) && (
                  <button
                    className={`arc3-play-action arc3-play-autoselect ${autoSelect ? "down" : ""}`}
                    title="When down, clicking a board cell fires CLICK there automatically (no arming needed)"
                    onClick={() => setAutoSelect((value) => !value)}
                  >
                    auto-CLICK
                  </button>
                )}
              </div>
              <div className="arc3-play-actions arc3-play-session-controls">
                {session.closed && (
                  <button
                    className="arc3-play-action"
                    disabled={busy}
                    title="Start a fresh session of this game"
                    onClick={() => void startGame(session.gameDirectory)}
                  >
                    START SESSION
                  </button>
                )}
                <span
                  className="arc3-play-rewind-wrap"
                  onMouseLeave={() => {
                    setRewindOpen(false);
                    setRewindHover(null);
                  }}
                >
                  <button
                    className="arc3-play-action reset arc3-play-rewind"
                    disabled={busy || session.closed || !session.levelMoveCount}
                    title="Rewind: reset the level and deterministically replay all but the last N moves"
                    onClick={() => setRewindOpen((open) => !open)}
                  >
                    Rewind… {rewindOpen ? "▾" : "▴"}
                  </button>
                  {rewindOpen && !session.closed && session.levelMoveCount > 0 && (
                    <div className="arc3-play-rewind-menu">
                      {Array.from({ length: session.levelMoveCount }, (_, offset) => offset + 1).map((count) => {
                        const undone = levelMoves.slice(-count).reverse();
                        const target = levelMoves[levelMoves.length - count - 1] || null;
                        const shown = undone.slice(0, 4);
                        return (
                          <button
                            key={count}
                            className="arc3-play-rewind-option"
                            onMouseEnter={() => setRewindHover(count)}
                            onFocus={() => setRewindHover(count)}
                            onClick={() => {
                              setRewindOpen(false);
                              setRewindHover(null);
                              void undoMove(count);
                            }}
                          >
                            <b>
                              Rewind {count} move{count > 1 ? "s" : ""}
                            </b>
                            <span className="arc3-play-rewind-undoes">
                              {shown.map((move) => (
                                <span key={move.directory} className="arc3-play-rewind-thumb">
                                  <img src={assetUrl(`${move.directory}/image.png`)} alt={`Move ${move.index}`} loading="lazy" />
                                  <small>
                                    {move.index}/ {actionShort(move.action)}
                                  </small>
                                </span>
                              ))}
                              {undone.length > shown.length && <small>+{undone.length - shown.length} more</small>}
                            </span>
                            <small className="arc3-play-rewind-back">
                              {target ? `back to ${target.index}/ · ${actionShort(target.action)}` : "back to level start"}
                            </small>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </span>
                <button
                  className="arc3-play-action reset"
                  disabled={busy || session.closed}
                  title="Save-point: snapshot this position to the game log (keep playing); resume it later"
                  onClick={() => void forkSavepoint()}
                >
                  Fork
                </button>
                <button
                  className="arc3-play-action reset"
                  disabled={busy || session.closed}
                  title="Restart the current level (new attempt dir)"
                  onClick={() => void resetAttempt()}
                >
                  Restart Level{session.level ? `_${session.level}` : ""}
                </button>
                <button
                  className="arc3-play-action reset"
                  disabled={busy || session.closed}
                  title="Restart the whole game from level 1 (fresh environment)"
                  onClick={() => void restartGame()}
                >
                  Restart game
                </button>
                <button className="arc3-play-action end" disabled={busy || session.closed} onClick={() => void endSession()}>
                  End session
                </button>
              </div>
              {replayScript && (
                <div className="arc3-play-actions arc3-play-replayer">
                  <small>
                    REPLAY {replayPos}/{replayScript.length}
                  </small>
                  <button
                    className="arc3-play-action reset"
                    disabled={busy || session.closed || replayPos <= 0 || replayPlaying}
                    title="Undo the last replayed move"
                    onClick={() => void takeBackReplay()}
                  >
                    |&lt; take-back-move
                  </button>
                  <button
                    className={`arc3-play-action watch ${replayPlaying ? "down" : ""}`}
                    disabled={busy || session.closed || (!replayPlaying && replayPos >= replayScript.length)}
                    title={replayPlaying ? "Pause the replay (stays at the current move)" : "Watch: auto-step from the current move"}
                    onClick={() => setReplayPlaying((playing) => !playing)}
                  >
                    {replayPlaying ? "Ⅱ Pause" : "▶ Watch replay"}
                  </button>
                  <button
                    className="arc3-play-action resume-step"
                    disabled={busy || session.closed || replayPos >= replayScript.length || replayPlaying}
                    title="Play the next recorded move"
                    onClick={() => void stepReplay()}
                  >
                    step one move &gt;|
                  </button>
                  <select
                    className="arc3-play-replay-speed"
                    value={replaySpeedMs}
                    disabled={busy}
                    title="Watch speed"
                    onChange={(event) => setReplaySpeedMs(Number(event.target.value))}
                  >
                    <option value={700}>0.5x</option>
                    <option value={300}>1x</option>
                    <option value={120}>2x</option>
                    <option value={40}>4x</option>
                  </select>
                  <button
                    className="arc3-play-action end"
                    disabled={busy}
                    title="Stop following the recording (keep playing live)"
                    onClick={() => {
                      setReplayPlaying(false);
                      setReplayScript(null);
                    }}
                  >
                    Detach
                  </button>
                </div>
              )}
              {replayScript && replayScript.length > 0 && (
                <div className="arc3-play-timeline">
                  {Array.from({ length: replayScript.length + 1 }, (_, index) => index).map((index) => {
                    const op = index > 0 ? replayScript[index - 1] : null;
                    const isCurrent = index === replayPos;
                    const directory = op && op.op === "step" ? op.directory : null;
                    const chapterLabel = chapterStarts.get(index);
                    return (
                      <button
                        key={index}
                        className={`arc3-play-timeline-tick ${op?.op === "reset" ? "reset" : "step"} ${isCurrent ? "current" : ""} ${chapterLabel ? "chapter-start" : ""}`}
                        title={
                          chapterLabel
                            ? `Level ${chapterLabel} begins (move ${index})`
                            : index === 0
                              ? "Start"
                              : `${index}: ${op?.op === "reset" ? "RESET" : op?.action}`
                        }
                        onMouseEnter={() => setTimelineHover(index)}
                        onMouseLeave={() => setTimelineHover((hover) => (hover === index ? null : hover))}
                        onClick={() => void seekReplay(index)}
                      >
                        {chapterLabel && <span className="arc3-play-timeline-chapter-label">L{chapterLabel}</span>}
                        {timelineHover === index && (
                          <span className="arc3-play-timeline-preview">
                            {directory ? (
                              <img src={assetUrl(`${directory}/image.png`)} alt={`move ${index}`} draggable={false} />
                            ) : (
                              <span className="arc3-play-timeline-preview-label">
                                {index === 0 ? "start" : "reset"}
                              </span>
                            )}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}
            </>
          )}
        </section>

        <div
          className="arc3-play-col-resizer"
          title="Drag to resize"
          onMouseDown={startColumnDrag("right")}
        />

        <section className="arc3-play-recording">
          <div className="arc3-play-section-title">
            <span>RECORDINGS</span>
            <span className="arc3-play-section-actions">
              <button
                className="arc3-play-rescan"
                title="Reload the current session's recorded moves from disk"
                disabled={!session || busy}
                onClick={() => void refreshRecording()}
              >
                Refresh
              </button>
              <button
                className="arc3-play-rescan"
                disabled={busy || !sortedRecordings.length}
                title="Import every IMPORTABLE recording currently listed below into full Recordings + move-lists (respects Filter)"
                onClick={() => void importAllImportables(sortedRecordings)}
              >
                Import All Importables
              </button>
              <button
                className="arc3-play-rescan"
                disabled={busy}
                title="For every MOVE-LIST whose Recording doesn't exist on disk yet, replay it into a fresh saved_<NNN> Recording (respects Filter)"
                onClick={() => void importAllMovelistsAsRecordings()}
              >
                Import All Movelists
              </button>
              <button
                className="arc3-play-rescan"
                disabled={busy}
                title="Rank imported recording dirs on disk by size (biggest = _size_0001); respects Filter. Never touches live-play saved_<NNN> dirs."
                onClick={() => void sortRecordingsBySize()}
              >
                Sort dirs by size
              </button>
              <input
                type="number"
                min={0}
                className="arc3-play-retain-count"
                aria-label="Number of largest imported recordings to retain"
                value={retainLargestCount}
                onChange={(event) => setRetainLargestCount(event.target.value)}
                disabled={busy}
              />
              <button
                className="arc3-play-rescan"
                disabled={busy}
                title="Delete every imported recording dir beyond the N largest (by size); respects Filter. Never touches live-play saved_<NNN> dirs."
                onClick={() => void retainLargestRecordings()}
              >
                Retain N Largest
              </button>
              <button className="arc3-play-collapse-toggle" onClick={() => toggleSection("recordings")}>
                {collapsedSections.recordings ? "▸ Expand" : "▾ Collapse"}
              </button>
            </span>
          </div>
          {!collapsedSections.recordings && (
            <>
              {!session && <div className="arc3-play-empty">Recording paths sometimes only appear once a game starts.</div>}
              {session && (
                <>
                  <div className="arc3-play-target">
                    <small>ACTIVE LEVEL DIR (use as B1 -&gt; B2 setup stateDir)</small>
                    <code>{session.levelDir}</code>
                    <button onClick={() => void copyLevelDir()}>{copied ? "Copied" : "Copy path"}</button>
                    {session.forkedFrom && <small>resumed from save-point {session.forkedFrom}</small>}
                  </div>
                  <div className="arc3-play-target arc3-play-recordings-path">
                    <small title="Where future level dirs + savepoints.json for this session are written. Blank = default data/Recordings/<game>/. Applies to the next attempt/level, not files already on disk.">
                      RECORDINGS PATH (workspace-relative)
                    </small>
                    <input
                      type="text"
                      value={recordingsPathDraft}
                      placeholder={`data/Recordings/${session.gameDirectory} (default)`}
                      disabled={busy}
                      onChange={(event) => setRecordingsPathDraft(event.target.value)}
                    />
                    <div className="arc3-play-recordings-path-actions">
                      <button
                        disabled={busy || recordingsPathDraft.trim() === (session.recordingsPathIsDefault ? "" : session.recordingsPath || "")}
                        onClick={() => void setRecordingsPath(recordingsPathDraft.trim() || null)}
                      >
                        Set
                      </button>
                      <button disabled={busy || session.recordingsPathIsDefault} onClick={() => void setRecordingsPath(null)}>
                        Reset to default
                      </button>
                    </div>
                    <small>
                      Currently: <code>{session.recordingsPath}</code>
                      {session.recordingsPathIsDefault ? " (default)" : " (custom)"}
                    </small>
                  </div>
              {levelMoves.length > 0 && (
                <div className="arc3-play-move-setup">
                  <small>MOVE AS SETUP (bootstrap the same way a B1-&gt;B2 setup scans its dir, but over 0/ 1/ 2/ …)</small>
                  <div className="arc3-play-move-setup-row">
                    <select
                      value={inspectOrdinal ?? levelMoves.length - 1}
                      onChange={(event) => {
                        const ordinal = Number(event.target.value);
                        setInspectOrdinal(ordinal);
                        setInspectScan(null);
                      }}
                    >
                      {levelMoves.map((move, ordinal) => (
                        <option key={move.directory} value={ordinal}>
                          {ordinal}/ {actionShort(move.action)}
                          {ordinal === levelMoves.length - 1 ? " (latest)" : ""}
                        </option>
                      ))}
                    </select>
                    <button
                      disabled={inspectLoading}
                      onClick={() => {
                        const ordinal = inspectOrdinal ?? levelMoves.length - 1;
                        void loadMoveScan(levelMoves[ordinal].directory);
                      }}
                    >
                      {inspectLoading ? "Scanning…" : "Scan"}
                    </button>
                    <button onClick={() => void copyMoveDir(levelMoves[inspectOrdinal ?? levelMoves.length - 1].directory)}>
                      {inspectCopied ? "Copied" : "Copy path"}
                    </button>
                  </div>
                  {inspectScan && (
                    <div className="arc3-play-move-scan">
                      {Object.entries(inspectScan)
                        .filter(([, paths]) => paths.length > 0)
                        .map(([bucket, paths]) => (
                          <span key={bucket} className="arc3-play-move-scan-bucket">
                            {bucket}: {paths.length}
                          </span>
                        ))}
                      {Object.values(inspectScan).every((paths) => paths.length === 0) && (
                        <span className="arc3-play-move-scan-bucket">only image.png so far</span>
                      )}
                    </div>
                  )}
                </div>
              )}
              {session.levelDirs.length > 1 && (
                <div className="arc3-play-leveldirs">
                  <small>ALL ATTEMPT/LEVEL DIRS THIS SESSION</small>
                  {session.levelDirs.map((dir) => (
                    <code key={dir}>{dir}</code>
                  ))}
                </div>
              )}
              <div className="arc3-play-moves">
                <small>MOVES (newest first — stored in 0/ 1/ 2/ …)</small>
                {newestFirst.map((move) => {
                  const levelIdx = levelIndexByDir.get(move.directory);
                  const rewindCount = levelIdx === undefined ? 0 : levelMoves.length - 1 - levelIdx;
                  const canRewind = !session.closed && !busy && rewindCount > 0;
                  const canReplayFrom =
                    session.closed && !busy && (session.replayLog || []).some((entry) => entry.directory === move.directory);
                  const clickable = canRewind || canReplayFrom;
                  return (
                  <div
                    key={move.directory}
                    className={`arc3-play-move${rewindUndoneDirs.has(move.directory) ? " will-undo" : ""}${
                      rewindTargetDir === move.directory ? " rewind-target" : ""
                    }${clickable ? " clickable" : ""}`}
                    title={
                      canRewind
                        ? `Click to rewind here — undoes the ${rewindCount} newer move${rewindCount > 1 ? "s" : ""}`
                        : canReplayFrom
                          ? "Click to fork a new session playing from here"
                          : levelIdx !== undefined && rewindCount === 0 && !session.closed
                            ? "Current position"
                            : undefined
                    }
                    onMouseEnter={canRewind ? () => setRewindHover(rewindCount) : undefined}
                    onMouseLeave={canRewind ? () => setRewindHover(null) : undefined}
                    onClick={
                      canRewind
                        ? () => {
                            setRewindHover(null);
                            void undoMove(rewindCount);
                          }
                        : canReplayFrom
                          ? () => void playFromMove(move)
                          : undefined
                    }
                  >
                    <img src={assetUrl(`${move.directory}/image.png`)} alt={`Move ${move.index}`} loading="lazy" />
                    <div>
                      <b>
                        {move.index}/ · {actionFull(move.action)}
                        {move.data && Object.keys(move.data).length > 0 && (
                          <span className="arc3-play-move-data"> {JSON.stringify(move.data)}</span>
                        )}
                        <button
                          className="arc3-play-move-expand"
                          title="Show this move as a B1->B2 setup (path/scan)"
                          onClick={(event) => {
                            event.stopPropagation();
                            toggleMoveExpand(move.directory);
                          }}
                        >
                          {expandedMoveDir === move.directory ? "▾" : "▸"}
                        </button>
                      </b>
                      <small>
                        state {move.state || "?"} · level {move.level || "?"}
                        {move.level_completed && <em> · completed level {move.level_completed}</em>}
                      </small>
                      <code>{move.directory}</code>
                      {expandedMoveDir === move.directory && (
                        <div className="arc3-play-move-setup" onClick={(event) => event.stopPropagation()}>
                          <div className="arc3-play-move-setup-row">
                            <button onClick={() => void copyMoveDir(move.directory)}>
                              {inspectCopied ? "Copied" : "Copy path"}
                            </button>
                            <button disabled={moveScanLoading === move.directory} onClick={() => void scanMoveDir(move.directory)}>
                              {moveScanLoading === move.directory ? "Scanning…" : "Scan"}
                            </button>
                          </div>
                          {moveScanResults[move.directory] && (
                            <div className="arc3-play-move-scan">
                              {Object.entries(moveScanResults[move.directory] || {})
                                .filter(([, paths]) => paths.length > 0)
                                .map(([bucket, paths]) => (
                                  <span key={bucket} className="arc3-play-move-scan-bucket">
                                    {bucket}: {paths.length}
                                  </span>
                                ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  );
                })}
                {!newestFirst.length && <div className="arc3-play-empty">No moves recorded yet.</div>}
              </div>
                </>
              )}
            </>
          )}
          <div className="arc3-play-savepoints">
            <small>
              MOVE-LISTS (fork a session to add one)
              <button className="arc3-play-collapse-toggle" onClick={() => toggleSection("restartPoints")}>
                {collapsedSections.restartPoints ? "▸ Expand" : "▾ Collapse"}
              </button>
              <button
                className="arc3-play-rescan"
                disabled={busy || !sortedRecordings.length}
                title="Import every IMPORTABLE recording currently listed below into move-lists only -- skips the expensive per-move image/state writes (respects Filter)"
                onClick={() => void importAllImportablesAsMovelists(sortedRecordings)}
              >
                Import All Importables
              </button>
              <button
                className="arc3-play-rescan"
                disabled={busy}
                title="For every Recording directory without a move-list yet, derive one from its own recorded moves (respects Filter)"
                onClick={() => void importAllRecordingsMoves()}
              >
                Import All Recordings' Moves
              </button>
              <button
                className="arc3-play-rescan"
                disabled={busy}
                title="Collapse duplicate save-points (same source recording or identical replay recipe)"
                onClick={() => void dedupeSavepoints()}
              >
                De-duplicate
              </button>
            </small>
            {!collapsedSections.restartPoints && (
              <>
                {filteredSavepoints.map((point) => (
              <div key={point.id} className="arc3-play-savepoint">
                <div>
                  <b>
                    {point.game_directory} · level {point.level || "?"} · {point.move_total ?? 0} moves
                  </b>
                  <small>
                    {point.label ? `${point.label} · ` : ""}
                    {point.created_at} · {point.state || "?"}
                  </small>
                </div>
                <div className="arc3-play-savepoint-buttons">
                  <button
                    className="resume"
                    disabled={busy}
                    title="Replay this save-point into a fresh session"
                    onClick={() => void resumeSavepoint(point.id)}
                  >
                    Resume
                  </button>
                  <button
                    className="load"
                    disabled={busy}
                    title="Load at move 1 to step through it move by move"
                    onClick={() => void loadSavepoint(point)}
                  >
                    Load
                  </button>
                  <button
                    className="dup"
                    disabled={busy}
                    title="Duplicate this save-point"
                    onClick={() => void duplicateSavepoint(point.id)}
                  >
                    Duplicate
                  </button>
                  <button
                    className="del"
                    disabled={busy}
                    title="Delete this save-point"
                    onClick={() => void deleteSavepoint(point.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
                {!filteredSavepoints.length && <div className="arc3-play-empty">No save-points yet.</div>}
              </>
            )}
          </div>
          <div className="arc3-play-savepoints arc3-play-recordings">
            <small>
              IMPORTABLES (official ARC-AGI-3 JSONL play logs / release-run logs in data/importables/)
              <button className="arc3-play-collapse-toggle" onClick={() => toggleSection("importables")}>
                {collapsedSections.importables ? "▸ Expand" : "▾ Collapse"}
              </button>
              <button
                className="arc3-play-rescan"
                disabled={busy}
                title="Rescan data/importables/ for recordings"
                onClick={() => void loadRecordings()}
              >
                Rescan
              </button>
              <button
                className="arc3-play-rescan"
                disabled={busy}
                title="Remove stale level dirs left behind by re-importing the same file"
                onClick={() => void dedupeRecordings()}
              >
                De-duplicate
              </button>
              <button
                className="arc3-play-rescan"
                disabled={busy || !sortedRecordings.length}
                title="Import every recording currently listed below (respects Filter)"
                onClick={() => void importAllImportables(sortedRecordings)}
              >
                Import All Importables
              </button>
            </small>
            {!collapsedSections.importables && (
              <>
                {importNote && <div className="arc3-play-import-note">{importNote}</div>}
                {sortedRecordings.map((recording) => (
                  <div key={recording.path} className="arc3-play-savepoint">
                    <div className="arc3-play-savepoint-info">
                      <b>{recording.name}</b>
                      <small>
                        {recording.kind === "release-run" ? "release run" : "human recording"} ·{" "}
                        {recording.gameId || "?"}
                        {recording.kind === "release-run" && recording.totalActions
                          ? ` · ${recording.totalActions} actions`
                          : ` · ${Math.round((recording.sizeBytes || 0) / 1024)} KB`}{" "}
                        · {recording.path}
                      </small>
                    </div>
                    <div className="arc3-play-savepoint-buttons">
                      <button
                        className="dup"
                        disabled={busy}
                        title="Convert to level recordings + a resumable save-point"
                        onClick={() => void importRecording(recording)}
                      >
                        Import
                      </button>
                    </div>
                  </div>
                ))}
                {!sortedRecordings.length && (
                  <div className="arc3-play-empty">
                    No importable recordings found.{" "}
                    <button className="arc3-play-rescan" disabled={busy} onClick={() => void loadRecordings()}>
                      Scan data/importables/
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
