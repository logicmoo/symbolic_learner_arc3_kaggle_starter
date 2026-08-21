import { useCallback, useEffect, useRef, useState } from "react";
import { type WorkflowPageDefinition } from "./WorkflowPageHost";
import "../styles/arc3_play.css";

type Props = {
  pageDefinition: WorkflowPageDefinition;
  workspaceId: string;
  workspaceLabel: string;
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

export function Arc3PlayPage({ pageDefinition, workspaceId, workspaceLabel }: Props) {
  const [games, setGames] = useState<GameInfo[]>([]);
  const [gamesLoading, setGamesLoading] = useState(false);
  const [session, setSession] = useState<PlaySessionSnapshot | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [armedAction, setArmedAction] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [savepoints, setSavepoints] = useState<PlaySavepoint[]>([]);
  const [rewindOpen, setRewindOpen] = useState(false);
  const [rewindHover, setRewindHover] = useState<number | null>(null);
  const boardRef = useRef<HTMLImageElement | null>(null);

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

  useEffect(() => {
    void loadGames(false);
  }, [loadGames]);

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
      setSession(payload.session as PlaySessionSnapshot);
      await loadSavepoints();
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
      setSession(payload.session as PlaySessionSnapshot);
    });

  const sendAction = (actionId: string, x?: number, y?: number) =>
    perform(async () => {
      if (!session) return;
      const payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/action`, {
        method: "POST",
        body: JSON.stringify({ action: actionId, x, y }),
      });
      setSession(payload.session as PlaySessionSnapshot);
    });

  const resetAttempt = () =>
    perform(async () => {
      if (!session) return;
      const payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/reset`, { method: "POST" });
      setArmedAction(null);
      setSession(payload.session as PlaySessionSnapshot);
    });

  const restartGame = () =>
    perform(async () => {
      if (!session) return;
      const payload = await request(`/api/arc3-play/sessions/${encodeURIComponent(session.id)}/restart`, { method: "POST" });
      setArmedAction(null);
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
      setSession(payload.session as PlaySessionSnapshot);
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
    if (!armedAction || !session || session.closed || busy) return;
    const image = boardRef.current;
    if (!image || !image.naturalWidth || !image.clientWidth) return;
    const bounds = image.getBoundingClientRect();
    const px = ((event.clientX - bounds.left) * image.naturalWidth) / bounds.width;
    const py = ((event.clientY - bounds.top) * image.naturalHeight) / bounds.height;
    const gx = Math.max(0, Math.floor(px / FRAME_SCALE));
    const gy = Math.max(0, Math.floor(py / FRAME_SCALE));
    const action = armedAction;
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

  const moves = session?.moves || [];
  const newestFirst = [...moves].reverse();
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
            {workspaceLabel} · every move is recorded to data/&lt;game&gt;/level_&lt;n&gt;_&lt;datetime&gt;_&lt;ns&gt;/0..k for B1 -&gt; B2 setups
          </small>
        </div>
        {error && <div className="arc3-play-error">{error}</div>}
      </header>
      <div className="arc3-play-columns">
        <section className="arc3-play-games">
          <div className="arc3-play-section-title">
            <span>ARC3 GAMES</span>
            <button onClick={() => void loadGames(true)} disabled={gamesLoading}>
              {gamesLoading ? "Loading…" : "Refresh"}
            </button>
          </div>
          <div className="arc3-play-game-list">
            {games.map((game) => {
              const shortId = game.short_id || game.game_id;
              const active = session && !session.closed && session.gameDirectory === shortId;
              return (
                <button
                  key={game.game_id}
                  className={`arc3-play-game ${active ? "active" : ""}`}
                  disabled={busy}
                  onClick={() => void startGame(shortId)}
                >
                  <b>{shortId}</b>
                  <small>{game.title || game.game_id}</small>
                  {active && <em>playing</em>}
                </button>
              );
            })}
            {!games.length && !gamesLoading && <div className="arc3-play-empty">No games returned by the ARC engine.</div>}
          </div>
        </section>

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
                title={armedAction ? `Click the board to send ${armedAction} at that cell` : "Arrow keys / Space play directly"}
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
                  New attempt
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
            </>
          )}
        </section>

        <section className="arc3-play-recording">
          <div className="arc3-play-section-title">
            <span>RECORDING</span>
          </div>
          {!session && <div className="arc3-play-empty">Recording paths appear once a game starts.</div>}
          {session && (
            <>
              <div className="arc3-play-target">
                <small>ACTIVE LEVEL DIR (use as B1 -&gt; B2 setup stateDir)</small>
                <code>{session.levelDir}</code>
                <button onClick={() => void copyLevelDir()}>{copied ? "Copied" : "Copy path"}</button>
                {session.forkedFrom && <small>resumed from save-point {session.forkedFrom}</small>}
              </div>
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
                      </b>
                      <small>
                        state {move.state || "?"} · level {move.level || "?"}
                        {move.level_completed && <em> · completed level {move.level_completed}</em>}
                      </small>
                      <code>{move.directory}</code>
                    </div>
                  </div>
                  );
                })}
                {!newestFirst.length && <div className="arc3-play-empty">No moves recorded yet.</div>}
              </div>
            </>
          )}
          <div className="arc3-play-savepoints">
            <small>SAVE-POINTS (fork a session to add one)</small>
            {savepoints.map((point) => (
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
            {!savepoints.length && <div className="arc3-play-empty">No save-points yet.</div>}
          </div>
        </section>
      </div>
    </div>
  );
}
