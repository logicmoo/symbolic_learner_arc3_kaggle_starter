import { useCallback, useEffect, useMemo, useState } from "react";
import { type WorkflowPageDefinition } from "./WorkflowPageHost";
import "../styles/arc3_games_gallery.css";

type Props = {
  pageDefinition: WorkflowPageDefinition;
  workspaceId: string;
  workspaceLabel: string;
  onPlayGame?: (gameShortId: string) => void;
};

type GameInfo = {
  game_id: string;
  short_id?: string;
  title?: string;
  tags?: string[];
  level_count?: number | null;
};

async function request(path: string, init?: RequestInit) {
  const response = await fetch(path, { cache: "no-store", ...init });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || response.statusText);
  return payload;
}

export function Arc3GamesGalleryPage({ pageDefinition, workspaceLabel, onPlayGame }: Props) {
  const [games, setGames] = useState<GameInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState("");
  const [syncMessage, setSyncMessage] = useState("");
  const [search, setSearch] = useState("");
  const [failedPreviews, setFailedPreviews] = useState<Record<string, boolean>>({});
  const [previewNonce, setPreviewNonce] = useState(0);

  const loadGames = useCallback(async (refresh: boolean) => {
    setLoading(true);
    setError("");
    try {
      const payload = await request(`/api/arc3-play/games${refresh ? "?refresh=true" : ""}`);
      setGames((payload.games as GameInfo[]) || []);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadGames(false);
  }, [loadGames]);

  const syncFromArcInteractive = useCallback(async () => {
    setSyncing(true);
    setError("");
    setSyncMessage("");
    try {
      const summary = await request("/api/arc3-play/games/sync", { method: "POST" });
      if (!summary.available) {
        setSyncMessage("No sibling ../arc-interactive checkout found on this machine -- nothing to import.");
      } else if (summary.copied > 0) {
        setSyncMessage(
          `Imported ${summary.copied} new version dir(s) across ${(summary.newStems || []).length} game(s). ` +
            `${summary.alreadyPresent} already present.`,
        );
        setFailedPreviews({});
        setPreviewNonce((current) => current + 1);
        await loadGames(true);
      } else {
        setSyncMessage(`Already up to date (${summary.alreadyPresent} version dir(s) present).`);
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setSyncing(false);
    }
  }, [loadGames]);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return games;
    return games.filter((game) => {
      const shortId = (game.short_id || game.game_id || "").toLowerCase();
      const title = (game.title || "").toLowerCase();
      const tags = (game.tags || []).join(" ").toLowerCase();
      return shortId.includes(query) || title.includes(query) || tags.includes(query);
    });
  }, [games, search]);

  return (
    <div className="arc3-gallery-page">
      <header className="arc3-gallery-header">
        <div>
          <h2>{pageDefinition.label || "ARC3 Games"}</h2>
          <small>
            {workspaceLabel} · {games.length} game{games.length === 1 ? "" : "s"} discovered
            {search ? ` · ${filtered.length} shown` : ""}
          </small>
        </div>
        <div className="arc3-gallery-controls">
          <input
            type="search"
            aria-label="Filter games"
            placeholder="Filter by id, title, or tag…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <button
            title="Import any new games from a sibling ../arc-interactive checkout, if present"
            onClick={() => void syncFromArcInteractive()}
            disabled={syncing || loading}
          >
            {syncing ? "Syncing…" : "Sync from arc-interactive"}
          </button>
          <button onClick={() => void loadGames(true)} disabled={loading || syncing}>
            {loading ? "Loading…" : "Refresh"}
          </button>
        </div>
        {error && <div className="arc3-gallery-error">{error}</div>}
        {syncMessage && <div className="arc3-gallery-sync-message">{syncMessage}</div>}
      </header>
      <div className="arc3-gallery-grid">
        {filtered.map((game) => {
          const shortId = game.short_id || game.game_id;
          const previewFailed = failedPreviews[shortId];
          return (
            <article key={game.game_id} className="arc3-gallery-card">
              <div className="arc3-gallery-thumb">
                {previewFailed ? (
                  <div className="arc3-gallery-thumb-placeholder">No preview</div>
                ) : (
                  <img
                    src={`/api/arc3-play/games/${encodeURIComponent(shortId)}/preview?nonce=${previewNonce}`}
                    alt={game.title || shortId}
                    loading="lazy"
                    onError={() => setFailedPreviews((current) => ({ ...current, [shortId]: true }))}
                  />
                )}
              </div>
              <div className="arc3-gallery-card-body">
                <b>{shortId}</b>
                <span>{game.title || shortId}</span>
                {game.tags && game.tags.length > 0 && (
                  <div className="arc3-gallery-tags">
                    {game.tags.map((tag) => (
                      <span key={tag} className="arc3-gallery-tag">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              {onPlayGame && (
                <button className="arc3-gallery-play" onClick={() => onPlayGame(shortId)}>
                  Play &amp; Record
                </button>
              )}
            </article>
          );
        })}
        {!loading && !filtered.length && (
          <div className="arc3-gallery-empty">
            {games.length ? `No games match "${search}".` : "No games discovered yet."}
          </div>
        )}
      </div>
    </div>
  );
}
