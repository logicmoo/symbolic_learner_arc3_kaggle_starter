import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";
import { pushGlobalStatus } from "../lib/globalStatus";
import { SuperControl } from "./UniversalArtifactEditor";
import "../styles/video_import.css";
import "../styles/video_import_page.css";

/**
 * Video Import v2 — rebuilt from the build prompt in
 * workbench/docs/VIDEO_IMPORT.md (appendix), with the whole design known up
 * front: one typed API layer, one job engine, one stack runner, and a
 * uniform collapsible-section shell for every gallery.
 */

type Video = {
  path: string; title: string; duration?: number | null; sizeBytes?: number;
  frameCount?: number; scenes?: Array<{ atSeconds: number }>;
  segments?: Array<{ start: number; end: number; keep: boolean }>;
  lastExtract?: { secondsPerFrame?: number };
};
type Frame = { path: string; index: number; atSeconds?: number; characters: string[]; anonymous: number };
type FilterEntry = {
  id: string; title: string; filter: string; description?: string;
  params?: Record<string, unknown>; paramChoices?: Record<string, string[]>;
  lutPath?: string; skillPath?: string; broken?: boolean; excluded?: boolean; votes?: number;
  skill?: boolean; lut?: boolean;
};
type FilterSpec = Record<string, unknown>;
type ChainStep = { entryId: string; params: Record<string, string> };
type JobState = {
  id: string; kind: string; state: "running" | "done" | "error";
  done: number; total: number; elapsedSeconds: number; etaSeconds: number;
  frames?: Array<{ path: string; index: number; atSeconds?: number }>;
  markers?: Array<{ atSeconds: number }>;
  gallery?: Array<{ id: string; title: string; path?: string; error?: string; baseId?: string; params?: Record<string, unknown> }>;
  resultPath?: string | null; interrupted?: boolean; error?: string | null; retinters?: string[];
};
type GalleryTile = NonNullable<JobState["gallery"]>[number];
type TrailLevel = { label: string; frames: Array<{ original: string; path: string }> };
type Member = {
  framePath: string; frameIndex: number; name: string; cutout: string; box: number[];
  step: number; status: "pending" | "accepted" | "rejected"; probeIndex: number; probeLabel: string;
};

const API = "/api/video-import";

async function api(path: string, body?: unknown): Promise<Record<string, any>> {
  const response = await fetch(path.startsWith("/") ? path : `${API}/${path}`, body === undefined
    ? { headers: { "content-type": "application/json" } }
    : { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};
  if (!response.ok) throw new Error(String(payload.detail || response.statusText));
  return payload;
}

const seconds = (value?: number | null) => {
  if (!value || !Number.isFinite(value)) return "?";
  const total = Math.round(value);
  return total >= 60 ? `${Math.floor(total / 60)}m${String(total % 60).padStart(2, "0")}s` : `${total}s`;
};

/** Uniform collapsible section: header, meta, pin, auto-collapse on scroll-away. */
function Section({ id, title, meta, extra, open, pinned, autoCollapse, onToggle, onAutoCollapse, onPin, children }: {
  id: string; title: string; meta?: string; extra?: ReactNode;
  open: boolean; pinned: boolean; autoCollapse: boolean;
  onToggle: () => void; onAutoCollapse: () => void; onPin: () => void; children: ReactNode;
}) {
  const ref = useRef<HTMLElement | null>(null);
  const seen = useRef(false);
  const timer = useRef(0);
  const collapse = useRef(onAutoCollapse);
  collapse.current = onAutoCollapse;
  useEffect(() => {
    const element = ref.current;
    if (!element || !open || !autoCollapse || pinned) return undefined;
    seen.current = false;
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) { seen.current = true; window.clearTimeout(timer.current); }
      else if (seen.current) { window.clearTimeout(timer.current); timer.current = window.setTimeout(() => collapse.current(), 1200); }
    });
    observer.observe(element);
    return () => { observer.disconnect(); window.clearTimeout(timer.current); };
  }, [open, autoCollapse, pinned]);
  return (
    <section ref={ref} className={`vi2-section${open ? "" : " is-collapsed"}`} data-section={id}>
      <div className="vi2-section-head">
        <button className="vi2-section-toggle" onClick={onToggle}>{open ? "▾" : "▸"} <b>{title}</b></button>
        {meta && <small>{meta}</small>}
        <button className={`vi2-section-pin${pinned ? " is-pinned" : ""}`} title={pinned ? "Unpin" : "Pin: never auto-collapse"} onClick={onPin}>📌</button>
        {extra}
      </div>
      {open && children}
    </section>
  );
}

export function VideoImportPage({ workspaceId }: { workspaceId: string }) {
  // ---- status strip + interrupts ----------------------------------------
  const [log, setLog] = useState<Array<{ at: string; text: string }>>([]);
  const stopRef = useRef(false);
  const say = useCallback((text: string) => {
    const at = new Date().toLocaleTimeString([], { hour12: false });
    setLog((current) => [...current.slice(-2), { at, text }]);
    pushGlobalStatus(text, "video-import");
  }, []);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const run = async (label: string, work: () => Promise<string | void>) => {
    setBusy(true); stopRef.current = false; setError(""); say(`${label}…`);
    try { const result = await work(); say(result || `${label} done`); }
    catch (reason) { const message = reason instanceof Error ? reason.message : String(reason); setError(message); say(`✗ ${message}`); }
    finally { setBusy(false); }
  };

  // ---- collapsible sections ----------------------------------------------
  // Sections all START collapsed; opening is an explicit act (persisted in
  // the state snapshot via collapsedMap/pinnedMap).
  const [collapsedMap, setCollapsedMap] = useState<Record<string, boolean>>({});
  const [pinnedMap, setPinnedMap] = useState<Record<string, boolean>>({});
  const [autoCollapseOn, setAutoCollapseOn] = useState(true);
  const section = (id: string, title: string, meta?: string, extra?: ReactNode) => ({
    id, title, meta, extra,
    open: collapsedMap[id] === false,
    pinned: !!pinnedMap[id],
    autoCollapse: autoCollapseOn,
    onToggle: () => setCollapsedMap((current) => ({ ...current, [id]: current[id] === false })),
    onAutoCollapse: () => setCollapsedMap((current) => (current[id] === false ? { ...current, [id]: true } : current)),
    onPin: () => setPinnedMap((current) => ({ ...current, [id]: !current[id] })),
  });

  // ---- one job engine -----------------------------------------------------
  const [job, setJob] = useState<JobState | null>(null);
  const jobDone = useRef<(final: JobState) => void>(() => undefined);
  const pollTimer = useRef(0);
  const watchJob = (jobId: string, kind: string, onDone: (final: JobState) => void) => {
    window.clearInterval(pollTimer.current);
    jobDone.current = onDone;
    pollTimer.current = window.setInterval(async () => {
      try {
        const payload = (await api(`extract/status?jobId=${encodeURIComponent(jobId)}`)) as unknown as Omit<JobState, "kind">;
        const next = { ...payload, kind } as JobState;
        setJob(next);
        if (payload.state !== "running") {
          window.clearInterval(pollTimer.current);
          if (payload.state === "done") jobDone.current(next);
          else setError(payload.error || `${kind} failed`);
        }
      } catch (reason) {
        window.clearInterval(pollTimer.current);
        setError(reason instanceof Error ? reason.message : String(reason));
      }
    }, 500);
  };
  const awaitJob = (jobId: string, kind: string, onTick?: (state: JobState) => void) =>
    new Promise<JobState>((resolve, reject) => {
      const tick = async () => {
        try {
          const payload = (await api(`extract/status?jobId=${encodeURIComponent(jobId)}`)) as unknown as JobState;
          setJob({ ...payload, kind });
          onTick?.(payload);
          if (stopRef.current) void api("extract/cancel", { jobId }).catch(() => undefined);
          if (payload.state === "running") { window.setTimeout(tick, 500); return; }
          if (payload.state === "done") resolve(payload); else reject(new Error(payload.error || `${kind} failed`));
        } catch (reason) { reject(reason instanceof Error ? reason : new Error(String(reason))); }
      };
      void tick();
    });
  const stopEverything = () => {
    stopRef.current = true;
    if (job && job.state === "running") void api("extract/cancel", { jobId: job.id }).catch(() => undefined);
    if (userPickResolver.current) settleUserPick(null);
    say("■ stop requested — finishing the current step…");
  };
  // Optional downstream invalidation, split in two:
  // - "auto-clear stale data" (default ON): when upstream DATA changes (new
  //   video, re-extract), the derived results below are cleared.
  // - "auto-clear next algorithm" (default OFF): when an upstream chain step
  //   is edited, the LATER chain steps are dropped too. Off = the workflow
  //   below survives edits above.
  const [autoClearData, setAutoClearData] = useState(true);
  const autoClearDataRef = useRef(true);
  useEffect(() => { autoClearDataRef.current = autoClearData; }, [autoClearData]);
  const [autoClearAlgorithm, setAutoClearAlgorithm] = useState(false);
  const autoClearAlgorithmRef = useRef(false);
  useEffect(() => { autoClearAlgorithmRef.current = autoClearAlgorithm; }, [autoClearAlgorithm]);
  const skipVideoResetRef = useRef(false);
  const prevVideoPathRef = useRef<string | null>(null);

  // ---- library ------------------------------------------------------------
  const [videos, setVideos] = useState<Video[]>([]);
  const [selectedPath, setSelectedPath] = useState("");
  const selected = videos.find((video) => video.path === selectedPath) || null;
  const loadVideos = useCallback(async (pick?: string) => {
    const payload = await api(`videos?workspaceId=${encodeURIComponent(workspaceId)}`);
    const list = (payload.videos as Video[]) || [];
    setVideos(list);
    if (pick) setSelectedPath(pick);
    // Never steal the selection: the restored/live value wins whenever it is
    // still a real video; only an empty or vanished selection falls back.
    else setSelectedPath((current) => (current && list.some((video) => video.path === current) ? current : list[0]?.path || ""));
  }, [workspaceId]);
  const [catalog, setCatalog] = useState<Array<{ title: string; url: string }>>([]);
  const [importables, setImportables] = useState<Array<{ path: string; name: string }>>([]);
  useEffect(() => {
    void loadVideos();
    void api(`catalog?workspaceId=${encodeURIComponent(workspaceId)}`).then((payload) => setCatalog((payload.entries as Array<{ title: string; url: string }>) || [])).catch(() => undefined);
    void api(`importables?workspaceId=${encodeURIComponent(workspaceId)}`).then((payload) => {
      const files = ((payload.files as Array<{ path: string; name?: string }>) || []).map((entry) => ({ path: String(entry.path), name: String(entry.name || entry.path) }));
      setImportables(files);
    }).catch(() => undefined);
    void api(`filters?workspaceId=${encodeURIComponent(workspaceId)}`).then((payload) => { setFilters((payload.filters as FilterEntry[]) || []); setLedger((payload.votes as Record<string, number>) || {}); }).catch(() => undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceId]);

  // ---- intake -------------------------------------------------------------
  const [source, setSource] = useState("");
  const [nameDraft, setNameDraft] = useState("");
  const [quality, setQuality] = useState("480p");
  const fileInput = useRef<HTMLInputElement | null>(null);
  const importSource = (value?: string) =>
    run("Importing", async () => {
      const raw = (value ?? source).trim();
      if (!raw) return "nothing to import";
      const isUrl = /^https?:\/\//i.test(raw);
      const payload = await api(isUrl ? "download" : "import-file", isUrl
        ? { workspaceId, url: raw, name: nameDraft.trim() || undefined, quality: quality === "python-direct" ? undefined : quality, tool: quality === "python-direct" ? "python-direct" : "yt-dlp" }
        : { workspaceId, path: raw, name: nameDraft.trim() || undefined });
      setSource(""); setNameDraft("");
      await loadVideos(String(payload.path || ""));
      return `imported: ${payload.title}`;
    });
  const upload = (file: File | null) => {
    if (!file) return;
    void run("Uploading", async () => {
      const form = new FormData();
      form.append("workspaceId", workspaceId);
      form.append("file", file, file.name);
      const response = await fetch(`${API}/upload`, { method: "POST", body: form });
      const payload = await response.json();
      if (!response.ok) throw new Error(String(payload.detail || response.statusText));
      await loadVideos(String(payload.path || ""));
      return `uploaded: ${payload.title}`;
    });
  };

  // ---- player + timeline ---------------------------------------------------
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [playerTime, setPlayerTime] = useState(0);
  const [playerDuration, setPlayerDuration] = useState(0);
  const duration = playerDuration || Number(selected?.duration || 0);
  const [markers, setMarkers] = useState<Array<{ atSeconds: number }>>([]);
  const [segments, setSegments] = useState<Array<{ start: number; end: number; keep: boolean }>>([]);
  const [selection, setSelection] = useState<{ start: number; end: number } | null>(null);
  const railRef = useRef<HTMLDivElement | null>(null);
  const dragRef = useRef<{ startX: number; startT: number; moved: boolean } | null>(null);
  useEffect(() => {
    const previous = prevVideoPathRef.current;
    prevVideoPathRef.current = selectedPath;
    // Only a REAL video change resets (not mount, StrictMode re-runs, or restore).
    if (previous === null || previous === selectedPath) return;
    if (skipVideoResetRef.current) { skipVideoResetRef.current = false; return; }
    setMarkers(selected?.scenes || []); setSegments(selected?.segments || []); setSelection(null);
    setFrames([]); setPlayerTime(0); setPlayerDuration(0); setJob(null); setPicked(null); setKept(null);
    if (autoClearDataRef.current) { setOutput([]); setTrail([]); setProbes([]); setMembers([]); setMemberScenes({}); setGallery(null); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPath]);
  const pct = (value: number) => (duration ? `${Math.min(100, Math.max(0, (value / duration) * 100))}%` : "0%");
  const railTime = (clientX: number) => {
    const rect = railRef.current?.getBoundingClientRect();
    if (!rect || !duration) return 0;
    return Math.max(0, Math.min(duration, ((clientX - rect.left) / rect.width) * duration));
  };
  const persistMarkers = (next: Array<{ atSeconds: number }>) => {
    setMarkers(next);
    void api("markers", { workspaceId, video: selectedPath, markers: next }).catch(() => undefined);
  };
  const persistSegments = (next: Array<{ start: number; end: number; keep: boolean }>) => {
    setSegments(next);
    void api("segments", { workspaceId, video: selectedPath, segments: next }).catch(() => undefined);
  };
  const activeSegments = segments.length ? segments : (duration ? [{ start: 0, end: duration, keep: true }] : []);

  const detectScenes = () =>
    run("Detecting scenes", async () => {
      // Resume where the last run stopped: start at the last detected marker.
      const resumeAt = markers.length ? Math.max(...markers.map((marker) => marker.atSeconds)) : 0;
      const payload = await api("scenes", { workspaceId, video: selectedPath, startSeconds: resumeAt });
      watchJob(String(payload.jobId), "scenes", (final) => { setMarkers(final.markers || []); say(`scenes: ${(final.markers || []).length} marker(s) (${resumeAt ? `resumed @ ${resumeAt.toFixed(1)}s` : "from the top"})`); });
      return resumeAt ? `scanning for scene changes from ${resumeAt.toFixed(1)}s…` : "scanning for scene changes…";
    });
  const trimVideo = () =>
    run("Trimming", async () => {
      const payload = await api("trim", { workspaceId, video: selectedPath, segments: activeSegments });
      watchJob(String(payload.jobId), "trim", (final) => { void loadVideos(String(final.resultPath || "")); say("trimmed video ready"); });
      return `re-encoding kept parts…`;
    });
  const selectionToVideo = () =>
    run("Extracting selection", async () => {
      if (!selection) return "drag a selection or click a scene first";
      const payload = await api("trim", { workspaceId, video: selectedPath, segments: [{ ...selection, keep: true }], name: `${selected?.title || "clip"}-${selection.start.toFixed(1)}s` });
      watchJob(String(payload.jobId), "trim", (final) => { void loadVideos(String(final.resultPath || "")); say("selection video ready"); });
      return "re-encoding the selection…";
    });

  // ---- frames (input images) -----------------------------------------------
  const [frames, setFrames] = useState<Frame[]>([]);
  const [picked, setPicked] = useState<string | null>(null);
  const [kept, setKept] = useState<Set<string> | null>(null);
  const [mode, setMode] = useState<"interval" | "scenes">("interval");
  const [everySeconds, setEverySeconds] = useState("2");
  const [perScene, setPerScene] = useState("1");
  const [sceneOffset, setSceneOffset] = useState("0.3");
  const [rangeStart, setRangeStart] = useState("0");
  const [rangeEnd, setRangeEnd] = useState("");
  const [maxFrames, setMaxFrames] = useState("40");
  const extractBody = () => ({
    workspaceId, video: selectedPath, mode,
    everySeconds: Number(everySeconds) || 2, maxFrames: Number(maxFrames) || 40,
    perScene: Number(perScene) || 1, sceneOffsetSeconds: Number(sceneOffset) || 0.3,
    startSeconds: Number(rangeStart) || 0, endSeconds: rangeEnd.trim() ? Number(rangeEnd) : undefined,
  });
  const criteriaLabel = () =>
    mode === "scenes"
      ? `per scene ×${perScene} +${sceneOffset}s · ${rangeStart || 0}–${rangeEnd || "end"}s · max ${maxFrames}`
      : `every ${everySeconds}s · ${rangeStart || 0}–${rangeEnd || "end"}s · max ${maxFrames}`;
  const acceptFrames = (list: JobState["frames"]) => {
    const next = (list || []).map((frame) => ({ ...frame, characters: [], anonymous: 0 }));
    setFrames(next);
    // The freshly extracted images are the gallery you curate next — show them.
    setCollapsedMap((current) => ({ ...current, inputs: false }));
    // Prune selection pointers that no longer exist in the fresh extraction.
    setPicked((current) => (current && next.some((frame) => frame.path === current) ? current : null));
    setKept((current) => {
      if (!current) return null;
      const surviving = new Set([...current].filter((path) => next.some((frame) => frame.path === path)));
      return surviving.size ? surviving : null;
    });
    if (autoClearDataRef.current) {
      setOutput([]); setTrail([]); setProbes([]); setMembers([]); setMemberScenes({});
      say("stale results cleared (fresh extraction) — turn off auto-clear stale data to keep them");
    }
  };
  const extract = () =>
    run("Extracting frames", async () => {
      const payload = await api("extract", extractBody());
      watchJob(String(payload.jobId), "extract", (final) => { acceptFrames(final.frames); say(`extracted ${(final.frames || []).length} frame(s)${final.interrupted ? " (interrupted)" : ""}`); });
      return `extracting ≈${payload.estimatedFrames} frame(s)…`;
    });
  const extractAndWait = async (): Promise<Frame[]> => {
    const started = await api("extract", extractBody());
    const final = await awaitJob(String(started.jobId), "extract", (state) => say(`extract (top of stack): ${state.done}/${state.total}`));
    const fresh: Frame[] = (final.frames || []).map((frame) => ({ ...frame, characters: [], anonymous: 0 }));
    acceptFrames(final.frames);
    return fresh;
  };
  const grabAtCursor = () =>
    run("Grabbing frame", async () => {
      const payload = await api("frame-at", { workspaceId, video: selectedPath, atSeconds: playerTime });
      const grabbed: Frame = { path: String(payload.path), index: Number(payload.index) || 0, atSeconds: Number(payload.atSeconds), characters: [], anonymous: 0 };
      setFrames((current) => (current.some((frame) => frame.path === grabbed.path) ? current : [...current, grabbed].sort((a, b) => (a.atSeconds ?? 0) - (b.atSeconds ?? 0))));
      return `grabbed frame @ ${grabbed.atSeconds}s`;
    });

  // group selectors
  const [groupKind, setGroupKind] = useState<"unique" | "spread" | "random" | "like" | "unlike" | "user">("user");
  const [groupCount, setGroupCount] = useState("6");
  const selectGroup = () =>
    run("Selecting group", async () => {
      if (frames.length < 2) return "extract at least 2 frames first";
      const count = Math.max(1, Math.min(frames.length, Number(groupCount) || 6));
      if (groupKind === "user") {
        const chosen = await askUserPick(frames.map((frame) => ({ original: frame.path, current: frame.path })), "GROUP — click the item YOU want used");
        if (!chosen || !chosen.length) return "user pick skipped";
        setKept(new Set(chosen));
        if (chosen.length === 1) { setPicked(chosen[0]); setPreviewSource("selectedframe"); }
        return `you picked ${chosen.length} item(s)`;
      }
      if (groupKind === "spread" || groupKind === "random") {
        const picks = groupKind === "spread"
          ? new Set(Array.from({ length: count }, (_, at) => frames[Math.min(frames.length - 1, Math.round(at * (frames.length / count)))].path))
          : new Set([...frames].sort(() => Math.random() - 0.5).slice(0, count).map((frame) => frame.path));
        setKept(picks);
        return `selected ${picks.size} (${groupKind})`;
      }
      if (groupKind === "like" || groupKind === "unlike") {
        const bySource = new Map(output.map((entry) => [entry.source, entry.path]));
        const pairs = frames.filter((frame) => bySource.has(frame.path)).map((frame) => ({ image: bySource.get(frame.path), original: frame.path }));
        if (!pairs.length) return "run the chain first — this compares OUTPUT to original";
        const payload = await api("select-group", { workspaceId, selector: groupKind === "like" ? "like-original" : "unlike-original", pairs, count });
        setKept(new Set((payload.selected as string[]) || []));
        return `selected ${count} (${groupKind} original)`;
      }
      const payload = await api("select-group", { workspaceId, selector: "unique", images: frames.map((frame) => frame.path), count });
      setKept(new Set((payload.selected as string[]) || []));
      return `selected the ${count} most unique`;
    });

  // ---- let-the-user-decide picker ---------------------------------------------
  // A `select:user` chain step (or the GROUP "user" kind) pauses the pipeline
  // and waits for a click on the item that continues.
  const [userPick, setUserPick] = useState<{ title: string; frames: Array<{ original: string; current: string }>; chosen: Set<string> } | null>(null);
  const userPickResolver = useRef<((paths: string[] | null) => void) | null>(null);
  const askUserPick = (candidates: Array<{ original: string; current: string }>, title: string) =>
    new Promise<string[] | null>((resolve) => {
      userPickResolver.current = resolve;
      setUserPick({ title, frames: candidates, chosen: new Set<string>() });
      // The question must be SEEN: force the section open and bring it into view.
      setCollapsedMap((current) => ({ ...current, userpick: false }));
      window.setTimeout(() => {
        document.querySelector(".video-import-userpick-section")?.scrollIntoView({ behavior: "smooth", block: "center" });
      }, 120);
    });
  const settleUserPick = (paths: string[] | null) => {
    const resolve = userPickResolver.current;
    userPickResolver.current = null;
    setUserPick(null);
    resolve?.(paths);
  };

  // ---- filters, votes, chain ------------------------------------------------
  const [filters, setFilters] = useState<FilterEntry[]>([]);
  const [ledger, setLedger] = useState<Record<string, number>>({});
  const [filterId, setFilterId] = useState("");
  const [filterParams, setFilterParams] = useState<Record<string, string>>({});
  const active = filters.find((entry) => entry.id === filterId) || null;
  const pickFilter = (id: string) => {
    setFilterId(id);
    const entry = filters.find((candidate) => candidate.id === id);
    setFilterParams(entry ? Object.fromEntries(Object.entries(entry.params || {}).map(([key, value]) => [key, String(value)])) : {});
    say(entry ? `picked: ${entry.title}` : "no filter picked — ▦ runs the gallery");
  };
  const specFor = (entry: FilterEntry, raw: Record<string, string>): FilterSpec => {
    const params = Object.fromEntries(Object.entries(raw).map(([key, value]) => [key, /^-?\d+(\.\d+)?$/.test(value) ? Number(value) : value]));
    return { label: entry.title, filter: entry.filter, params, colors: params.colors, scale: params.scale, ...(entry.lutPath ? { lutPath: entry.lutPath } : {}), ...(entry.skillPath ? { skillPath: entry.skillPath } : {}) };
  };
  const [chain, setChain] = useState<ChainStep[]>([]);
  const [candidateCount, setCandidateCount] = useState("6");
  const [fullSelectors, setFullSelectors] = useState(false);
  const refreshFilters = (payload: Record<string, any>) => {
    setFilters((payload.filters as FilterEntry[]) || []);
    if (payload.votes) setLedger(payload.votes as Record<string, number>);
  };
  const vote = (ids: string[], delta: number) =>
    run(delta > 0 ? "Upvoting" : "Downvoting", async () => {
      if (!ids.length) return "nothing to credit";
      let payload: Record<string, any> | null = null;
      for (const id of ids) payload = await api("filters/vote", { workspaceId, filterId: id, delta });
      if (payload) refreshFilters(payload);
      setLedger((current) => { const next = { ...current }; for (const id of ids) next[id] = (next[id] || 0) + delta; return next; });
      return `${delta > 0 ? "▲" : "▼"} credited to ${ids.join(", ")}`;
    });
  const setDisabled = (id: string, disabled: boolean) =>
    run(disabled ? "Disabling filter" : "Re-enabling filter", async () => {
      const payload = await api("filters/disable", { workspaceId, filterId: id, disabled });
      refreshFilters(payload);
      return disabled ? `disabled ${id} (extreme downvote)` : `re-enabled ${id}`;
    });
  const scanRetinters = () =>
    run("Scanning for retinters", async () => {
      const payload = await api("filters/classify-retinters", { workspaceId });
      watchJob(String(payload.jobId), "retinter", (final) => {
        void api(`filters?workspaceId=${encodeURIComponent(workspaceId)}`).then(refreshFilters).catch(() => undefined);
        say(`retinter scan: ${(final.retinters || []).length} flagged`);
      });
      return `classifying ${payload.count} filter(s)…`;
    });

  // ---- gallery ---------------------------------------------------------------
  const [gallery, setGallery] = useState<GalleryTile[] | null>(null);
  const [galleryScope, setGalleryScope] = useState<"included" | "excluded" | "all">("included");
  const [previewSource, setPreviewSource] = useState<"testcard" | "playerframe" | "firstframe" | "selectedframe">("testcard");
  const previewBody = (): Record<string, unknown> => {
    const body: Record<string, unknown> = { workspaceId };
    if (previewSource === "selectedframe") {
      // Resolution order: explicitly picked item → your GROUP pick → last frame.
      const keptPick = kept && kept.size ? [...kept][kept.size - 1] : null;
      const base = picked || keptPick || (frames.length ? frames[frames.length - 1].path : null);
      if (base) body.image = base;
    }
    else if (previewSource === "playerframe" && selectedPath) { body.video = selectedPath; body.atSeconds = playerTime; }
    else if (previewSource === "firstframe" && frames.length) body.image = frames[0].path;
    return body;
  };
  const runGallery = (options?: { filterId?: string; image?: string }) =>
    run(options?.filterId ? "Rendering permutations" : "Rendering gallery", async () => {
      const body: Record<string, unknown> = { ...previewBody(), ...(options?.image ? { image: options.image } : {}) };
      say(`gallery base: ${typeof body.image === "string" ? String(body.image).split("/").pop() : body.video ? "player frame" : "test card"}`);
      const payload = await api("filter-gallery", { ...body, ...(options?.filterId ? { filterId: options.filterId } : { scope: galleryScope }) });
      setGallery(null);
      watchJob(String(payload.jobId), "gallery", (final) => { setGallery(final.gallery || []); say(`gallery: ${(final.gallery || []).length} tile(s)${final.interrupted ? " (interrupted)" : ""}`); });
      return `rendering ${payload.count} output(s)…`;
    });
  const [beforeAfter, setBeforeAfter] = useState<{ before: string; after: string; label: string } | null>(null);
  const previewOne = () =>
    run("Previewing", async () => {
      const specs = chainSpecs();
      if (!specs.length) return "pick a filter or arm a chain step first";
      const payload = await api("filter-preview", { ...previewBody(), chain: specs });
      setBeforeAfter({ before: String(payload.before), after: String(payload.after), label: String(payload.filter) });
      return `previewed ${payload.filter}`;
    });

  // ---- the stack ---------------------------------------------------------------
  const [output, setOutput] = useState<Array<{ source: string; path: string }>>([]);
  const [outputMode, setOutputMode] = useState<"preview" | "full" | null>(null);
  const [outputLabel, setOutputLabel] = useState("");
  const [appliedIds, setAppliedIds] = useState<string[]>([]);
  const [trail, setTrail] = useState<TrailLevel[]>([]);
  const chainSpecs = (): FilterSpec[] => {
    const steps = chain.length ? chain : (active ? [{ entryId: filterId, params: filterParams }] : []);
    return steps
      .filter((step) => step.entryId && !step.entryId.startsWith("select:"))
      .map((step) => { const entry = filters.find((candidate) => candidate.id === step.entryId); return entry ? specFor(entry, step.params) : null; })
      .filter((spec): spec is FilterSpec => spec !== null);
  };
  const runStack = async (full: boolean, chainOverride?: ChainStep[]): Promise<string> => {
    let sourceFrames = frames;
    if (!sourceFrames.length) {
      if (!selectedPath) return "pick a video first";
      say(`top of stack: extract (${criteriaLabel()})`);
      sourceFrames = await extractAndWait();
      if (!sourceFrames.length) return "extraction produced no frames";
    }
    // A FULL run over all images requires the GROUP to be named: with the
    // "user" kind and no selection yet, ask — curate (keep/delete e.g.
    // all-black scenes) or pass everything through with "use ALL".
    if (full && groupKind === "user" && !kept?.size) {
      say("GROUP for the FULL run: curate the set (or use ALL)");
      const chosen = await askUserPick(sourceFrames.map((frame) => ({ original: frame.path, current: frame.path })), "GROUP for the FULL run — keep/delete, or use ALL");
      if (stopRef.current) return "stopped at the GROUP question";
      if (chosen && chosen.length && chosen.length < sourceFrames.length) {
        const keep = new Set(chosen);
        sourceFrames = sourceFrames.filter((frame) => keep.has(frame.path));
        setKept(keep);
        say(`GROUP: ${sourceFrames.length} frame(s) continue`);
      }
    }
    // Preview candidates: first group selection > picked item > spread N.
    let candidates = sourceFrames;
    if (!full) {
      const wanted = Math.max(1, Number(candidateCount) || 6);
      if (kept?.size) candidates = sourceFrames.filter((frame) => kept.has(frame.path));
      else if (picked && sourceFrames.some((frame) => frame.path === picked)) candidates = sourceFrames.filter((frame) => frame.path === picked);
      else if (sourceFrames.length > wanted) {
        const keep = new Set(Array.from({ length: wanted }, (_, at) => Math.min(sourceFrames.length - 1, Math.round(at * (sourceFrames.length / wanted)))));
        candidates = sourceFrames.filter((_, index) => keep.has(index));
      }
      say(`preview candidates: ${candidates.length}`);
    }
    let working = candidates.map((frame) => ({ original: frame.path, current: frame.path }));
    const levels: TrailLevel[] = [{ label: full ? "input (all frames)" : "input (candidates)", frames: working.map((item) => ({ original: item.original, path: item.current })) }];
    const snapshot = (label: string) => levels.push({ label, frames: working.map((item) => ({ original: item.original, path: item.current })) });
    const steps = chainOverride?.length ? chainOverride : chain.length ? chain : (active ? [{ entryId: filterId, params: filterParams }] : []);
    if (!steps.length) return "pick a filter or arm a chain step first";
    const labels: string[] = [];
    const ids: string[] = [];
    let pending: FilterSpec[] = [];
    let applied = 0;
    const flush = async () => {
      if (!pending.length || !working.length) { pending = []; return; }
      const payload = await api("filter", { workspaceId, chain: pending, applyTo: "frames", frames: working.map((item) => item.current) });
      const bySource = new Map(((payload.frames as Array<{ source: string; path: string }>) || []).map((entry) => [entry.source, entry.path]));
      working = working.map((item) => ({ ...item, current: bySource.get(item.current) || item.current }));
      applied += pending.length; pending = [];
    };
    for (const step of steps) {
      if (stopRef.current) break;
      if (!step.entryId) continue;
      if (step.entryId.startsWith("select:")) {
        if (full && !fullSelectors) { say(`selector ${step.entryId.slice(7)}: preview-only (toggle to include)`); continue; }
        const kind = step.entryId.slice(7);
        if (kind === "user") {
          await flush();
          say("YOUR PICK: click the item that continues…");
          const chosen = await askUserPick(working.map((item) => ({ ...item })), "SELECT — let user decide which item is used");
          if (stopRef.current) break;
          if (chosen && chosen.length) {
            const keep = new Set(chosen);
            working = working.filter((item) => keep.has(item.current));
          } else say("user pick skipped — keeping all");
          labels.push(`select:user=${working.length}`); ids.push("select:user");
          snapshot(`you picked → ${working.length}`);
          continue;
        }
        const n = Number(step.params.n);
        if (!Number.isFinite(n) || n < 1 || n >= working.length) { say(`selector ${kind}: no-op`); continue; }
        await flush();
        const count = Math.round(n);
        if (kind === "spread") {
          const keep = new Set(Array.from({ length: count }, (_, at) => working[Math.min(working.length - 1, Math.round(at * (working.length / count)))].original));
          working = working.filter((item) => keep.has(item.original));
        } else if (kind === "random") {
          const keep = new Set([...working].sort(() => Math.random() - 0.5).slice(0, count).map((item) => item.original));
          working = working.filter((item) => keep.has(item.original));
        } else if (kind === "unique") {
          const payload = await api("select-group", { workspaceId, selector: "unique", images: working.map((item) => item.current), count });
          const keep = new Set((payload.selected as string[]) || []);
          working = working.filter((item) => keep.has(item.current));
        } else {
          const payload = await api("select-group", { workspaceId, selector: kind === "like" ? "like-original" : "unlike-original", pairs: working.map((item) => ({ image: item.current, original: item.original })), count });
          const keep = new Set((payload.selected as string[]) || []);
          working = working.filter((item) => keep.has(item.original));
        }
        labels.push(`select:${kind}=${working.length}`); ids.push(`select:${kind}`);
        snapshot(`selector ${kind} → ${working.length}`);
      } else {
        const entry = filters.find((candidate) => candidate.id === step.entryId);
        if (!entry) continue;
        pending.push(specFor(entry, step.params));
        labels.push(entry.title); ids.push(entry.id);
        if (!full) { await flush(); snapshot(entry.title); }
      }
    }
    await flush();
    if (!applied && !labels.some((label) => label.startsWith("select:"))) return "chain is all no-ops";
    // Implicit final step: sort most-changed-first, never eliminate.
    if (applied && working.length > 1) {
      try {
        const payload = await api("select-group", { workspaceId, selector: "unlike-original", pairs: working.map((item) => ({ image: item.current, original: item.original })), count: working.length });
        const order = new Map(((payload.selected as string[]) || []).map((original, at) => [original, at]));
        working = [...working].sort((left, right) => (order.get(left.original) ?? 0) - (order.get(right.original) ?? 0));
      } catch { /* cosmetic */ }
    }
    snapshot(full ? "FULL output" : "output (sorted)");
    setOutput(working.map((item) => ({ source: item.original, path: item.current })));
    setOutputMode(full ? "full" : "preview");
    setOutputLabel(labels.join(" → "));
    setAppliedIds([...new Set(ids)]);
    setTrail(levels);
    setProbes([]);
    return full
      ? `FULL run: ${applied} filter step(s) over ${working.length} frame(s)`
      : `preview: ${applied} filter step(s), ${working.length} candidate(s) (sorted, none eliminated)`;
  };

  // ---- probes + members ----------------------------------------------------------
  const [probes, setProbes] = useState<number[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [memberScenes, setMemberScenes] = useState<Record<string, string>>({});
  const [models, setModels] = useState<Array<{ id: string; name: string }>>([]);
  const [memberModel, setMemberModel] = useState("");
  const [turtleModel, setTurtleModel] = useState("");
  const [memberGoal, setMemberGoal] = useState<"any" | "faces" | "characters" | "objects" | "text">("any");
  const [memberFill, setMemberFill] = useState<"median" | "blur" | "hole">("median");
  const [memberMax, setMemberMax] = useState("1");
  const [memberTarget, setMemberTarget] = useState("");

  // ---- runtime state snapshot -------------------------------------------------
  // Everything on this page is path-based (real files on disk), so a JSON
  // snapshot of the pointers restores the EXACT working state after any
  // reload/rebuild. Auto-saved (debounced) per workspace; restored on mount.
  const snapshotKey = `videoImport:state:${workspaceId}`;
  const legacySnapshotKey = `vi2:state:${workspaceId}`;
  const restoredRef = useRef(false);
  const restoreStartedRef = useRef(false);
  const userTouchedRef = useRef(false);
  const buildSnapshot = () => ({
    v: 1,
    at: new Date().toISOString(),
    selectedPath, playerTime, markers, segments, mode, everySeconds, rangeStart, rangeEnd, maxFrames,
    frames, picked, kept: kept ? [...kept] : null, previewSource, galleryScope,
    filterId, filterParams, chain, candidateCount, fullSelectors,
    gallery, output, outputMode, outputLabel, appliedIds, trail, probes,
    members, memberScenes, memberGoal, memberFill, memberMax, memberTarget,
    autoClearData, autoClearAlgorithm,
    collapsedMap, pinnedMap,
  });
  // Apply a snapshot object to the live page (used by mount-restore and the
  // JSON CONFIG editor). Returns false if the object is not a v1 snapshot.
  const applySnapshot = (s: any): boolean => {
    if (!s || typeof s !== "object" || s.v !== 1) return false;
    if (s.selectedPath) { skipVideoResetRef.current = true; setSelectedPath(String(s.selectedPath)); }
    if (typeof s.playerTime === "number") setPlayerTime(s.playerTime);
    if (Array.isArray(s.markers)) setMarkers(s.markers);
    if (Array.isArray(s.segments)) setSegments(s.segments);
    if (s.mode === "interval" || s.mode === "scenes") setMode(s.mode);
    if (typeof s.everySeconds === "string") setEverySeconds(s.everySeconds);
    if (typeof s.rangeStart === "string") setRangeStart(s.rangeStart);
    if (typeof s.rangeEnd === "string") setRangeEnd(s.rangeEnd);
    if (typeof s.maxFrames === "string") setMaxFrames(s.maxFrames);
    if (Array.isArray(s.frames)) setFrames(s.frames);
    if (typeof s.picked === "string") setPicked(s.picked);
    if (Array.isArray(s.kept) && s.kept.length) setKept(new Set(s.kept.map(String)));
    if (s.previewSource) setPreviewSource(s.previewSource);
    if (s.galleryScope) setGalleryScope(s.galleryScope);
    if (typeof s.filterId === "string") setFilterId(s.filterId);
    if (s.filterParams && typeof s.filterParams === "object") setFilterParams(s.filterParams);
    if (Array.isArray(s.chain)) setChain(s.chain);
    if (typeof s.candidateCount === "string") setCandidateCount(s.candidateCount);
    if (typeof s.fullSelectors === "boolean") setFullSelectors(s.fullSelectors);
    if (Array.isArray(s.gallery)) setGallery(s.gallery);
    if (Array.isArray(s.output)) setOutput(s.output);
    if (s.outputMode === "preview" || s.outputMode === "full") setOutputMode(s.outputMode);
    if (typeof s.outputLabel === "string") setOutputLabel(s.outputLabel);
    if (Array.isArray(s.appliedIds)) setAppliedIds(s.appliedIds);
    if (Array.isArray(s.trail)) setTrail(s.trail);
    if (Array.isArray(s.probes)) setProbes(s.probes);
    if (Array.isArray(s.members)) setMembers(s.members);
    if (s.memberScenes && typeof s.memberScenes === "object") setMemberScenes(s.memberScenes);
    if (s.memberGoal) setMemberGoal(s.memberGoal);
    if (s.memberFill) setMemberFill(s.memberFill);
    if (typeof s.memberMax === "string") setMemberMax(s.memberMax);
    if (typeof s.memberTarget === "string") setMemberTarget(s.memberTarget);
    if (typeof s.autoClearData === "boolean") setAutoClearData(s.autoClearData);
    else if (typeof s.autoClear === "boolean") setAutoClearData(s.autoClear);
    if (typeof s.autoClearAlgorithm === "boolean") setAutoClearAlgorithm(s.autoClearAlgorithm);
    if (s.collapsedMap && typeof s.collapsedMap === "object") setCollapsedMap(s.collapsedMap);
    if (s.pinnedMap && typeof s.pinnedMap === "object") setPinnedMap(s.pinnedMap);
    return true;
  };
  useEffect(() => {
    if (restoreStartedRef.current) return;
    restoreStartedRef.current = true;
    void (async () => {
      // The image repository's own state file is the source of truth; the
      // browser copy is a fast fallback. The NEWEST snapshot wins — a fresh
      // "just switched video" state must beat an older, richer one.
      const stamp = (s: any) => { const t = Date.parse(String(s?.at || "")); return Number.isFinite(t) ? t : 0; };
      let fsState: any = null;
      try {
        const payload = await api(`page-state?workspaceId=${encodeURIComponent(workspaceId)}`);
        if (payload.state && typeof payload.state === "object" && !payload.state.forgotten) fsState = payload.state;
      } catch { /* backend down — fall back to the browser copy */ }
      let lsState: any = null;
      try {
        const raw = localStorage.getItem(snapshotKey) || localStorage.getItem(legacySnapshotKey);
        if (raw) lsState = JSON.parse(raw);
      } catch { lsState = null; }
      const s = !fsState ? lsState : !lsState ? fsState : stamp(fsState) >= stamp(lsState) ? fsState : lsState;
      try {
        // If the user already touched the page while we were fetching, their
        // actions win — never re-select the restored video over their click.
        if (userTouchedRef.current) { say("state restore skipped — you were already working"); }
        else if (s && applySnapshot(s)) say(`⟳ restored your state (${s === fsState ? "image repository" : "browser"}) — ${(s.frames || []).length} frame(s), ${(s.chain || []).length} chain step(s), ${(s.output || []).length} output(s)`);
      } catch { /* a corrupt snapshot is ignored, never fatal */ }
      restoredRef.current = true; // saving may begin only now
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => {
    if (!restoredRef.current) return;
    const timer = setTimeout(() => {
      const state = buildSnapshot();
      try { localStorage.setItem(snapshotKey, JSON.stringify(state)); } catch { /* quota */ }
      // Mirror into the image repository so the state lives beside the images.
      void api("page-state", { workspaceId, state }).catch(() => undefined);
    }, 900);
    return () => clearTimeout(timer);
  });
  // Flush on unmount so switching pages right after a change never loses it.
  const buildSnapshotRef = useRef(buildSnapshot);
  buildSnapshotRef.current = buildSnapshot;
  useEffect(() => () => {
    if (!restoredRef.current) return;
    const state = buildSnapshotRef.current();
    try { localStorage.setItem(snapshotKey, JSON.stringify(state)); } catch { /* quota */ }
    try { navigator.sendBeacon?.(`${API}/page-state`, new Blob([JSON.stringify({ workspaceId, state })], { type: "application/json" })); } catch { /* best effort */ }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const copyStateJson = () => {
    const text = JSON.stringify(buildSnapshot(), null, 2);
    void navigator.clipboard?.writeText(text).then(() => say("state JSON copied to clipboard")).catch(() => say("copy failed — state JSON logged to console"));
    console.log("[vi2 state]", text);
  };
  const forgetState = () => {
    try { localStorage.removeItem(snapshotKey); localStorage.removeItem(legacySnapshotKey); } catch { /* ignore */ }
    void api("page-state", { workspaceId, state: { v: 1, forgotten: true } }).catch(() => undefined);
    say("saved state forgotten — next load starts clean");
  };
  // JSON CONFIG editor draft: null = tracking the live config. Edits apply to
  // the flow LIVE as soon as the JSON parses (debounced).
  const [configDraft, setConfigDraft] = useState<string | null>(null);
  const [configValid, setConfigValid] = useState(true);
  useEffect(() => {
    if (configDraft === null) { setConfigValid(true); return; }
    const timer = setTimeout(() => {
      try {
        const parsed = JSON.parse(configDraft);
        const ok = applySnapshot(parsed);
        setConfigValid(ok);
        if (ok) say("config edit applied to the flow");
      } catch { setConfigValid(false); }
    }, 500);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [configDraft]);
  const applyConfigDraft = () => {
    if (configDraft === null) { say("config unchanged"); return; }
    try {
      const parsed = JSON.parse(configDraft);
      if (!applySnapshot(parsed)) { setError("not a v1 config object (needs \"v\": 1)"); return; }
      setConfigDraft(null);
      say("config applied — page state now matches the JSON");
    } catch (reason) { setError(`config JSON invalid: ${reason instanceof Error ? reason.message : String(reason)}`); }
  };
  // Manual workflow edits mark the results below them stale (optional clearing).
  const clearStaleResults = (reason: string) => {
    setOutput([]); setOutputMode(null); setOutputLabel(""); setAppliedIds([]);
    setTrail([]); setProbes([]); setMembers([]); setMemberScenes({});
    say(`stale results cleared (${reason})`);
  };
  const editChain = (mutate: (current: ChainStep[]) => ChainStep[], truncateAt?: number) => {
    setChain((current) => {
      let next = mutate(current);
      if (autoClearAlgorithmRef.current && truncateAt !== undefined && next.length > truncateAt) {
        next = next.slice(0, truncateAt);
        say(`later algorithm steps dropped (edited above; ${next.length} step(s) kept)`);
      }
      return next;
    });
    if (autoClearDataRef.current && (output.length || trail.length || members.length)) clearStaleResults("chain edited");
  };
  useEffect(() => {
    let cancelled = false;
    void api(`/api/workspaces/${encodeURIComponent(workspaceId)}/model-policy`).then((payload) => {
      if (cancelled) return;
      const registry = (payload.registry || {}) as Record<string, any>;
      const list = ((registry.models as Array<Record<string, any>>) || [])
        .filter((model) => model.enabled !== false)
        .map((model) => ({ id: String(model.modelResourceId || model.id || ""), name: String(model.name || model.modelId || model.id) }))
        .filter((model) => model.id);
      setModels(list);
      setMemberModel((current) => current || list[0]?.id || "");
      setTurtleModel((current) => current || list[0]?.id || "");
    }).catch(() => undefined);
    return () => { cancelled = true; };
  }, [workspaceId]);
  const asDataUrl = async (path: string): Promise<string | null> => {
    const response = await fetch(`/api/workspaces/${encodeURIComponent(workspaceId)}/player/asset?path=${encodeURIComponent(path)}`, { cache: "no-store" });
    if (!response.ok) return null;
    const blob = await response.blob();
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || ""));
      reader.onerror = () => reject(new Error("could not read frame"));
      reader.readAsDataURL(blob);
    });
  };
  const asset = (path: string) => `/api/workspaces/${encodeURIComponent(workspaceId)}/asset?path=${encodeURIComponent(path)}`;
  const extractMembers = () =>
    run("Extracting members", async () => {
      if (!memberModel) return "pick a model first";
      if (!frames.length) return "extract frames first";
      const target = Math.max(0, Math.min(12, Number(memberTarget) || 0));
      const maxPerFrame = target > 0 ? target : Math.max(1, Math.min(8, Number(memberMax) || 1));
      const activeProbes = trail.length ? (probes.length ? probes.filter((probe) => probe < trail.length) : [trail.length - 1]) : [-1];
      const scenes = { ...memberScenes };
      let extracted = 0;
      for (const probeIndex of activeProbes) {
        if (stopRef.current) break;
        const level = probeIndex >= 0 ? trail[probeIndex] : null;
        const probeLabel = level?.label || "output";
        const bySource = new Map<string, string>();
        if (level) for (const item of level.frames) bySource.set(item.original, item.path);
        else for (const item of output) bySource.set(item.source, item.path);
        const batch = frames.filter((frame) => !level || bySource.has(frame.path)).slice(0, 6);
        for (const frame of batch) {
          if (stopRef.current) break;
          const known = new Set(members.filter((member) => member.framePath === frame.path && member.probeIndex === probeIndex && member.status !== "rejected").map((member) => member.name.toLowerCase()));
          const sceneKey = `${probeIndex}:${frame.path}`;
          let scenePath = scenes[sceneKey] || bySource.get(frame.path) || frame.path;
          for (let step = 1; step <= maxPerFrame; step++) {
            if (stopRef.current) break;
            say(`👥 [${probeLabel}] #${frame.index} pass ${step}/${maxPerFrame}`);
            const image = await asDataUrl(scenePath);
            if (!image) break;
            const goalLine = {
              any: "Identify ONE distinct member (character or object) still visible in it.",
              faces: "Find ONE distinct FACE still visible in it.",
              characters: "Identify ONE distinct CHARACTER (person or creature) still visible in it.",
              objects: "Identify ONE distinct inanimate OBJECT still visible in it.",
              text: "Find ONE distinct piece of TEXT or signage still visible in it.",
            }[memberGoal];
            const prompt = [
              `You see one video-frame scene. ${goalLine}`,
              target > 0 ? `The scene should divide into about ${target} members; extracted so far: ${known.size ? [...known].join(", ") : "none"}.` : `Already extracted: ${known.size ? [...known].join(", ") : "none"}.`,
              "Answer ONLY with JSON like {\"name\": \"short name\", \"polygon\": [[x, y], ...]} (3-20 points, pixel coordinates of THIS image).",
              "If no distinct member remains, answer exactly: NONE",
            ].join("\n");
            const payload = await api(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/${encodeURIComponent(memberModel)}/invoke`, { prompt, image, timeoutSeconds: 120 });
            const raw = typeof payload.text === "string" ? payload.text.trim() : "";
            if (/^\s*none[.!]?\s*$/i.test(raw)) break;
            const match = raw.match(/\{[\s\S]*\}/);
            let name = ""; let polygon: number[][] | null = null; let box: number[] | null = null;
            if (match) {
              try {
                const parsed = JSON.parse(match[0]);
                name = String(parsed.name || "").trim().slice(0, 40);
                polygon = Array.isArray(parsed.polygon) && parsed.polygon.length >= 3 ? parsed.polygon : null;
                box = Array.isArray(parsed.box) && parsed.box.length === 4 ? parsed.box.map(Number) : null;
              } catch { /* handled below */ }
            }
            if (!name || (!polygon && !box)) break;
            if (known.has(name.toLowerCase())) continue;
            try {
              const cut = await api("member-cut", { workspaceId, image: scenePath, polygon, box, name, step, fill: memberFill });
              known.add(name.toLowerCase());
              scenePath = String(cut.scene);
              scenes[sceneKey] = scenePath;
              setMemberScenes({ ...scenes });
              setMembers((current) => [...current, { framePath: frame.path, frameIndex: frame.index, name, cutout: String(cut.cutout), box: (cut.box as number[]) || box || [0, 0, 0, 0], step, status: "pending", probeIndex, probeLabel }]);
              extracted += 1;
              say(`✂ [${probeLabel}] #${frame.index} − ${name}`);
            } catch (reason) { say(`✗ cut failed: ${reason instanceof Error ? reason.message : reason}`); break; }
          }
        }
      }
      return stopRef.current ? `stopped: ${extracted} member(s) kept` : `extraction done: ${extracted} member(s) across ${activeProbes.length} strip(s)`;
    });
  const acceptMember = (at: number) => {
    const member = members[at];
    if (!member || member.status !== "pending") return;
    setFrames((current) => current.map((frame) => (frame.path === member.framePath && !frame.characters.some((existing) => existing.toLowerCase() === member.name.toLowerCase()) ? { ...frame, characters: [...frame.characters, member.name] } : frame)));
    setMembers((current) => current.map((entry, index) => (index === at ? { ...entry, status: "accepted" } : entry)));
    say(`✓ ${member.name}`);
  };
  const rejectMember = (at: number) =>
    run("Returning member", async () => {
      const member = members[at];
      if (!member || member.status === "rejected") return "already returned";
      const sceneKey = `${member.probeIndex}:${member.framePath}`;
      const scene = memberScenes[sceneKey];
      if (scene) {
        const payload = await api("member-return", { workspaceId, scene, cutout: member.cutout, box: member.box });
        setMemberScenes((current) => ({ ...current, [sceneKey]: String(payload.scene) }));
      }
      setFrames((current) => current.map((frame) => (frame.path === member.framePath ? { ...frame, characters: frame.characters.filter((existing) => existing.toLowerCase() !== member.name.toLowerCase()) } : frame)));
      setMembers((current) => current.map((entry, index) => (index === at ? { ...entry, status: "rejected" } : entry)));
      return `returned ${member.name} to the scene`;
    });

  // ---- turtle + materialize --------------------------------------------------------
  const [gameId, setGameId] = useState("video-cast-2");
  const generateTurtle = () =>
    run("Generating turtle programs", async () => {
      if (!turtleModel) return "pick a model first";
      const pool = output.length ? output.map((entry) => entry.path) : frames.map((frame) => frame.path);
      if (!pool.length) return "extract frames first";
      let written = 0;
      for (const framePath of pool.slice(0, 6)) {
        if (stopRef.current) break;
        say(`🐢 ${framePath.split("/").pop()}`);
        const image = await asDataUrl(framePath);
        if (!image) continue;
        const payload = await api(`/api/workspaces/${encodeURIComponent(workspaceId)}/models/${encodeURIComponent(turtleModel)}/invoke`, {
          prompt: "Write a small self-contained Python turtle program that redraws the main objects of the attached image. Use simple shapes and at most ~60 drawing commands. Answer with ONLY the Python code.",
          image, timeoutSeconds: 180,
        });
        const code = typeof payload.text === "string" ? payload.text : JSON.stringify(payload);
        await api("/api/arc3-play/silo/write", { workspaceId, dir: framePath.slice(0, framePath.lastIndexOf("/")), name: `${(framePath.split("/").pop() || "frame").replace(/\.png$/i, "")}.turtle.py`, content: code });
        written += 1;
      }
      return `turtle programs written for ${written} frame(s)`;
    });
  const materialize = () =>
    run("Materializing recording", async () => {
      const bySource = new Map(output.map((entry) => [entry.source, entry.path]));
      const payload = await api("materialize", { workspaceId, gameId, frames: frames.map((frame) => ({ ...frame, path: bySource.get(frame.path) || frame.path })) });
      const directory = String(payload.gameDirectory || gameId);
      window.setTimeout(() => { window.location.href = `/?workspace=${encodeURIComponent(workspaceId)}&view=arc3-play&game=${encodeURIComponent(directory)}`; }, 600);
      return `recording ready: ${payload.levelDir} — opening Play & Record`;
    });

  const progress = job && job.total > 0 ? Math.min(100, Math.round((job.done / job.total) * 100)) : 0;
  const selectorScore = (kind: string) => { const score = ledger[`select:${kind}`] || 0; return score ? ` (${score > 0 ? "+" : ""}${score})` : ""; };

  // ---- render -----------------------------------------------------------------------
  return (
    <section className="resource-view video-import-page vi2">
      <div className="resource-heading">
        <div>
          <span>KNOWLEDGE INTAKE · GENERATION 2</span>
          <h1>Video Import 2</h1>
          <p>Rebuilt from its own build prompt (see the help tab appendix): import → timeline → the preview stack for building filter chains → probes and entity strips → materialize. Every gallery collapses, every step interrupts.</p>
        </div>
      </div>

      <div className="video-import-activity" role="status" aria-live="polite">
        <span className={`video-import-activity-dot${busy || job?.state === "running" ? " is-busy" : ""}`} />
        <b>STATUS</b>
        <div className="video-import-activity-lines">
          {log.map((line, index) => (
            <span key={`${line.at}-${index}`} className={index === log.length - 1 ? "is-current" : ""}><code>{line.at}</code> {line.text}</span>
          ))}
        </div>
        <label className="video-import-toggle">
          <input type="checkbox" checked={autoCollapseOn} onChange={(event) => setAutoCollapseOn(event.target.checked)} />
          auto-collapse
        </label>
        <label className="video-import-toggle" title="When upstream DATA changes (new video, re-extract), clear the now-stale results below. The workflow itself is never cleared.">
          <input type="checkbox" checked={autoClearData} onChange={(event) => setAutoClearData(event.target.checked)} />
          auto-clear stale data
        </label>
        <label className="video-import-toggle" title="When a chain step is edited, also drop the LATER algorithm steps. Off: the workflow below survives edits above.">
          <input type="checkbox" checked={autoClearAlgorithm} onChange={(event) => setAutoClearAlgorithm(event.target.checked)} />
          auto-clear next algorithm
        </label>
        <button title="Copy the exact page state as JSON" disabled={false} onClick={copyStateJson}>⤓ state</button>
        <button title="Forget the saved state — next load starts clean" onClick={forgetState}>⟲ forget</button>
        <button className="video-import-stop" disabled={!busy && job?.state !== "running"} onClick={stopEverything}>■ Stop</button>
      </div>
      {error && <div className="backend-error"><b>Video import error</b><span>{error}</span></div>}
      {job && (
        <div className="video-import-progress" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
          <div className="video-import-progress-track"><div className="video-import-progress-fill" style={{ width: `${job.state === "done" ? 100 : progress}%` }} /></div>
          <small>
            {job.state === "running" && `${job.kind}: ${job.done}/${job.total} · ETA ${job.etaSeconds}s`}
            {job.state === "done" && `${job.kind} done in ${job.elapsedSeconds}s${job.interrupted ? " (interrupted)" : ""}`}
            {job.state === "error" && `${job.kind} failed: ${job.error}`}
          </small>
        </div>
      )}

      <Section {...section("config", "JSON CONFIG", `the page's exact state as editable JSON${configDraft === null ? " · live" : configValid ? " · editing (applies live)" : " · INVALID JSON — keep typing"}`,
        <>
          <button disabled={busy || configDraft === null} title="Force-apply now and resume tracking the live config" onClick={applyConfigDraft}>⏎ Apply</button>
          <button disabled={configDraft === null} title="Discard edits and track the live config again" onClick={() => setConfigDraft(null)}>↻ live</button>
          <button title="Copy the config JSON" onClick={copyStateJson}>⤓ copy</button>
        </>)}>
        <div className="vi2-body video-import-config-super">
          <SuperControl
            appearance="embedded"
            className="video-import-config-editor-super"
            control={{
              kind: "standard",
              workspaceId,
              source: configDraft ?? JSON.stringify(buildSnapshot(), null, 2),
              sourceScope: "runtime",
              path: `runtime/videoImport/${workspaceId}.config.json`,
              title: "Video Import — page config",
              dirty: configDraft !== null,
              secondary: false,
              busy,
              resource: (() => {
                let doc: Record<string, unknown> = {};
                if (configDraft === null) doc = buildSnapshot() as unknown as Record<string, unknown>;
                else { try { doc = JSON.parse(configDraft) as Record<string, unknown>; } catch { doc = {}; } }
                return { ...doc, kind: "video_import_config", id: `videoImport.${workspaceId}` } as { kind: string; id: string };
              })(),
              initialControlId: "file",
              onChange: (value) => setConfigDraft(value),
              onSave: applyConfigDraft,
              saveLabel: configValid ? "⏎ Apply to flow" : "… invalid JSON",
              actions: [
                { id: "live", label: "↻ track live", disabled: configDraft === null, onInvoke: () => setConfigDraft(null) },
                { id: "copy", label: "⤓ copy", onInvoke: copyStateJson },
                { id: "forget", label: "⟲ forget saved", onInvoke: forgetState },
              ],
            }}
          />
        </div>
      </Section>

      <Section {...section("intake", "INTAKE", `${videos.length} video(s) in the library`)}>
        <div className="vi2-body">
          <div className="video-import-row">
            <select className="video-import-catalog" value="" disabled={busy} onChange={(event) => { const entry = catalog[Number(event.target.value)]; if (entry) { setSource(entry.url); setNameDraft(entry.title); } }}>
              <option value="">catalog… ({catalog.length})</option>
              {catalog.map((entry, index) => (<option key={`${entry.url}-${index}`} value={index}>{entry.title}</option>))}
            </select>
            <select className="video-import-catalog" value="" disabled={busy} onChange={(event) => { if (event.target.value) void importSource(event.target.value); }}>
              <option value="">importables… ({importables.length})</option>
              {importables.map((file) => (<option key={file.path} value={file.path}>{file.name}</option>))}
            </select>
            <input value={source} placeholder="https://… or a movie path you have the rights to" disabled={busy} onChange={(event) => setSource(event.target.value)} />
            <input className="video-import-name" value={nameDraft} placeholder="name (optional)" disabled={busy} onChange={(event) => setNameDraft(event.target.value)} />
            <select value={quality} disabled={busy} onChange={(event) => setQuality(event.target.value)}>
              <option value="480p">480p lo-fi</option>
              <option value="720p">720p</option>
              <option value="1080p">1080p</option>
              <option value="best">best</option>
              <option value="python-direct">🛠 python direct</option>
            </select>
            <button disabled={busy || !source.trim()} onClick={() => void importSource()}>Download / Import</button>
            <input ref={fileInput} type="file" accept="video/*" style={{ display: "none" }} onChange={(event) => { upload(event.target.files?.[0] || null); event.target.value = ""; }} />
            <button disabled={busy} onClick={() => fileInput.current?.click()}>⇪ Upload…</button>
          </div>
          <div className="video-import-list" role="list">
            {videos.map((video) => (
              <button key={video.path} className={`video-import-item${video.path === selectedPath ? " is-selected" : ""}`} role="listitem" onClick={() => { userTouchedRef.current = true; setSelectedPath(video.path); }}>
                <b>{video.title}</b>
                <code>{video.path}</code>
                <small>{seconds(video.duration)} · {Math.round((video.sizeBytes || 0) / (1024 * 1024))} MB · {video.frameCount || 0} frame(s){video.scenes?.length ? ` · ${video.scenes.length} scene(s)` : ""}</small>
              </button>
            ))}
          </div>
        </div>
      </Section>

      {selected && (
        <Section {...section("player", "PLAYER / TIMELINE", `${selected.title} · ${seconds(duration)}`)}>
          <div className="vi2-body video-import-player">
            <video
              ref={videoRef}
              key={selected.path}
              controls
              preload="metadata"
              src={`${API}/stream?workspaceId=${encodeURIComponent(workspaceId)}&path=${encodeURIComponent(selected.path)}`}
              onTimeUpdate={(event) => setPlayerTime((event.target as HTMLVideoElement).currentTime)}
              onLoadedMetadata={(event) => setPlayerDuration((event.target as HTMLVideoElement).duration || 0)}
            />
            <div
              ref={railRef}
              className="video-import-rail"
              onPointerDown={(event) => { dragRef.current = { startX: event.clientX, startT: railTime(event.clientX), moved: false }; }}
              onPointerMove={(event) => {
                if (!dragRef.current || event.buttons !== 1) return;
                const now = railTime(event.clientX);
                if (Math.abs(event.clientX - dragRef.current.startX) > 4) {
                  dragRef.current.moved = true;
                  setSelection({ start: Math.min(dragRef.current.startT, now), end: Math.max(dragRef.current.startT, now) });
                }
              }}
              onPointerUp={(event) => {
                if (dragRef.current && !dragRef.current.moved && videoRef.current) videoRef.current.currentTime = railTime(event.clientX);
                dragRef.current = null;
              }}
            >
              {selection && <div className="video-import-rail-selection" style={{ left: pct(selection.start), width: `calc(${pct(selection.end)} - ${pct(selection.start)})` }} />}
              {markers.map((marker) => (
                <button key={marker.atSeconds} className="video-import-rail-marker" style={{ left: pct(marker.atSeconds) }} title={`scene @ ${marker.atSeconds}s (click to remove)`} onClick={(event) => { event.stopPropagation(); persistMarkers(markers.filter((entry) => entry !== marker)); }} />
              ))}
              <div className="video-import-rail-playhead" style={{ left: pct(playerTime) }} />
            </div>
            {markers.length > 0 && (
              <div className="video-import-scenelane">
                {[0, ...markers.map((marker) => marker.atSeconds), duration].slice(0, -1).map((start, index, bounds) => {
                  const end = [...markers.map((marker) => marker.atSeconds), duration][index];
                  return <button key={index} className="video-import-scene" style={{ left: pct(start), width: `calc(${pct(end)} - ${pct(start)})` }} title={`scene ${index}`} onClick={() => setSelection({ start, end })} />;
                })}
              </div>
            )}
            {activeSegments.length > 0 && (
              <div className="video-import-segmentlane">
                {activeSegments.map((segment, index) => (
                  <button key={index} className={`video-import-segment${segment.keep ? "" : " is-dropped"}`} style={{ left: pct(segment.start), width: `calc(${pct(segment.end)} - ${pct(segment.start)})` }} onClick={() => persistSegments(activeSegments.map((entry, at) => (at === index ? { ...entry, keep: !entry.keep } : entry)))}>
                    {segment.keep ? "keep" : "✕"}
                  </button>
                ))}
              </div>
            )}
            <div className="video-import-timeline">
              <small>t = {playerTime.toFixed(1)}s</small>
              <button disabled={busy || !duration} onClick={() => persistMarkers([...markers, { atSeconds: Math.round(playerTime * 100) / 100 }].sort((a, b) => a.atSeconds - b.atSeconds))}>◈ Mark</button>
              <button disabled={busy || !duration} onClick={() => void grabAtCursor()}>⤵ Frame at cursor</button>
              <button disabled={busy || job?.state === "running"} onClick={() => void detectScenes()}>✨ Detect scenes</button>
              <button disabled={busy || !duration} onClick={() => { const at = playerTime; persistSegments(activeSegments.flatMap((segment) => (at > segment.start && at < segment.end ? [{ ...segment, end: at }, { ...segment, start: at }] : [segment]))); }}>✂ Split at cursor</button>
              <button disabled={busy || job?.state === "running" || activeSegments.every((segment) => segment.keep)} onClick={() => void trimVideo()}>⟿ Trim video</button>
              <button disabled={busy || job?.state === "running" || !selection} onClick={() => void selectionToVideo()}>⤢ Selection → video</button>
              {selection && <small>selection {selection.start.toFixed(1)}–{selection.end.toFixed(1)}s <button disabled={busy} onClick={() => { setRangeStart(selection.start.toFixed(1)); setRangeEnd(selection.end.toFixed(1)); }}>→ window</button></small>}
            </div>
            <div className="video-import-timeline">
              <b title="The extract-frames-from-video criteria — the top of every stack run">EXTRACT</b>
              <select value={mode} disabled={busy} onChange={(event) => setMode(event.target.value as typeof mode)}>
                <option value="interval">every N seconds</option>
                <option value="scenes">per scene</option>
              </select>
              {mode === "interval"
                ? <label>every <input type="number" min={0.1} step={0.5} value={everySeconds} disabled={busy} onChange={(event) => setEverySeconds(event.target.value)} /> s</label>
                : <>
                  <label>images/scene <input type="number" min={1} max={20} value={perScene} disabled={busy} onChange={(event) => setPerScene(event.target.value)} /></label>
                  <label>offset <input type="number" min={0} step={0.1} value={sceneOffset} disabled={busy} onChange={(event) => setSceneOffset(event.target.value)} /> s</label>
                </>}
              <label>start <input type="number" min={0} value={rangeStart} disabled={busy} onChange={(event) => setRangeStart(event.target.value)} /></label>
              <label>end <input type="number" min={0} value={rangeEnd} placeholder="end" disabled={busy} onChange={(event) => setRangeEnd(event.target.value)} /></label>
              <label>max <input type="number" min={1} max={600} value={maxFrames} disabled={busy} onChange={(event) => setMaxFrames(event.target.value)} /></label>
              <button disabled={busy || job?.state === "running" || (mode === "scenes" && !markers.length)} onClick={() => void extract()}>Extract frames</button>
            </div>
          </div>
        </Section>
      )}

      {userPick && (
        <div className="video-import-userpick-section">
          <Section {...section("userpick", "❓ YOUR PICK", `${userPick.title} · ${userPick.chosen.size ? `${userPick.chosen.size} of ${userPick.frames.length} selected` : `${userPick.frames.length} candidate(s) — click to select`}`, <button onClick={() => settleUserPick(null)}>✕ skip</button>)}>
            <div className="vi2-body video-import-frames video-import-userpick">
              {userPick.frames.map((item) => {
                const on = userPick.chosen.has(item.current);
                return (
                  <article key={item.current} className={`video-import-frame is-plain is-user-pickable${on ? " is-group-pick" : ""}`}>
                    <img src={asset(item.current)} alt="candidate" loading="lazy" title={on ? "selected — click to unselect" : "click to select"} onClick={() => setUserPick((current) => {
                      if (!current) return current;
                      const chosen = new Set(current.chosen);
                      if (chosen.has(item.current)) chosen.delete(item.current); else chosen.add(item.current);
                      return { ...current, chosen };
                    })} />
                    <header><small>{on ? "✓ selected" : "click to select"}</small></header>
                  </article>
                );
              })}
            </div>
            <div className="vi2-body video-import-userpick-actions">
              <button disabled={!userPick.chosen.size} title="Continue with ONLY the selected items" onClick={() => settleUserPick([...userPick.chosen])}>✓ keep chosen ({userPick.chosen.size})</button>
              <button disabled={!userPick.chosen.size} title="DELETE the selected items — everything else continues" onClick={() => settleUserPick(userPick.frames.map((item) => item.current).filter((path) => !userPick.chosen.has(path)))}>🗑 remove chosen ({userPick.chosen.size})</button>
              <button title="Pass every item through unchanged" onClick={() => settleUserPick(userPick.frames.map((item) => item.current))}>use ALL</button>
              <button title="Auto-select the all-black frames (then 🗑 remove chosen)" onClick={() => void (async () => {
                try {
                  const payload = await api("select-degenerate", { workspaceId, images: userPick.frames.map((item) => item.current), kind: "black" });
                  const found = new Set((payload.selected as string[]) || []);
                  setUserPick((current) => current ? { ...current, chosen: new Set([...current.chosen, ...found]) } : current);
                  say(`◼ ${found.size} all-black frame(s) selected`);
                } catch (reason) { say(`✗ ${reason instanceof Error ? reason.message : String(reason)}`); }
              })()}>◼ + all-black</button>
              <button title="Auto-select flat/solid-color frames (then 🗑 remove chosen)" onClick={() => void (async () => {
                try {
                  const payload = await api("select-degenerate", { workspaceId, images: userPick.frames.map((item) => item.current), kind: "flat" });
                  const found = new Set((payload.selected as string[]) || []);
                  setUserPick((current) => current ? { ...current, chosen: new Set([...current.chosen, ...found]) } : current);
                  say(`▭ ${found.size} flat frame(s) selected`);
                } catch (reason) { say(`✗ ${reason instanceof Error ? reason.message : String(reason)}`); }
              })()}>▭ + flat/solid</button>
              <button disabled={!userPick.chosen.size} title="Clear the selection" onClick={() => setUserPick((current) => current ? { ...current, chosen: new Set() } : current)}>○ none</button>
              <button onClick={() => settleUserPick(null)}>✕ skip (keep all, no vote)</button>
            </div>
          </Section>
        </div>
      )}

      {frames.length > 0 && (
        <Section {...section("inputs", "INPUT IMAGES", `${frames.length} frame(s) · click = preview input · ▲ keeper · ▼ drop`)}>
          <div className="vi2-body video-import-frames">
            {frames.map((frame) => (
              <article key={frame.path} className={`video-import-frame is-plain${picked === frame.path ? " is-input-pick" : ""}${kept?.has(frame.path) ? " is-group-pick" : ""}`}>
                <img
                  src={asset(frame.path)}
                  alt={`frame ${frame.index}`}
                  loading="lazy"
                  onClick={() => { const next = picked === frame.path ? null : frame.path; setPicked(next); if (next) setPreviewSource("selectedframe"); say(next ? `input item: #${frame.index}` : "input item cleared"); }}
                />
                <div className="video-import-frame-votes">
                  <button disabled={busy} title="Keeper (joins the group selection)" onClick={() => setKept((current) => { const next = new Set(current || []); next.add(frame.path); return next; })}>▲</button>
                  <button disabled={busy} title="Drop from candidates" onClick={() => { setFrames((current) => current.filter((candidate) => candidate.path !== frame.path)); if (picked === frame.path) setPicked(null); }}>▼</button>
                </div>
                <header>
                  <b>#{frame.index}</b>
                  {frame.atSeconds !== undefined && <small>{frame.atSeconds}s</small>}
                  <small>{frame.path.includes("frame_at_") ? "⤵ cursor" : "extract"}</small>
                  {frame.characters.length > 0 && <small title={frame.characters.join(", ")}>👥 {frame.characters.length}</small>}
                </header>
              </article>
            ))}
          </div>
          {frames.length > 1 && (
            <div className="vi2-body video-import-groupbar">
              <b>GROUP</b>
              <select value={groupKind} disabled={busy} onChange={(event) => setGroupKind(event.target.value as typeof groupKind)}>
                <option value="user">Let USER decide which item is used{selectorScore("user")}</option>
                <option value="unique">N most unique{selectorScore("unique")}</option>
                <option value="spread">N evenly spread{selectorScore("spread")}</option>
                <option value="random">N random{selectorScore("random")}</option>
                <option value="like">N most like original{selectorScore("like")}</option>
                <option value="unlike">N most unlike original{selectorScore("unlike")}</option>
              </select>
              <label>N <input type="number" min={1} max={frames.length} value={groupCount} disabled={busy} onChange={(event) => setGroupCount(event.target.value)} /></label>
              <button disabled={busy} onClick={() => void selectGroup()}>Select group</button>
              {kept && <><small>{kept.size} selected — feeds the chain preview</small><button disabled={busy} onClick={() => { setFrames((current) => current.filter((frame) => kept.has(frame.path))); setKept(null); }}>✂ Keep only</button><button disabled={busy} onClick={() => setKept(null)}>× Clear</button></>}
            </div>
          )}
        </Section>
      )}

      {selected && (
        <Section {...section("prepass", "PREPASS / STACK", `${filters.filter((entry) => !entry.excluded && !entry.broken).length} active filter(s) · chain ${chain.length} step(s)`)}>
          <div className="vi2-body">
            <div className="video-import-timeline video-import-prepass">
              <select aria-label="Prepass filter" value={filterId} disabled={busy} onChange={(event) => pickFilter(event.target.value)}>
                <option value="">— pick a filter (or run ▦ first) —</option>
                {filters.map((entry) => (
                  <option key={entry.id} value={entry.id} disabled={entry.broken || entry.excluded}>
                    {entry.excluded ? "🚫 " : entry.skill ? "🛠 " : entry.lut ? "🎨 " : ""}{entry.title}
                  </option>
                ))}
              </select>
              {Object.entries(filterParams).map(([key, value]) => {
                const choices = active?.paramChoices?.[key];
                return (
                  <label key={key}>{key}
                    {choices?.length
                      ? <select className="video-import-param" value={value} disabled={busy} onChange={(event) => setFilterParams((current) => ({ ...current, [key]: event.target.value }))}>{choices.map((choice) => <option key={choice} value={choice}>{choice}</option>)}</select>
                      : <input className="video-import-param" value={value} disabled={busy} onChange={(event) => setFilterParams((current) => ({ ...current, [key]: event.target.value }))} />}
                  </label>
                );
              })}
              <select value={previewSource} disabled={busy} onChange={(event) => setPreviewSource(event.target.value as typeof previewSource)}>
                <option value="testcard">preview: test card</option>
                <option value="playerframe">preview: frame @ player</option>
                <option value="firstframe">preview: first frame</option>
                <option value="selectedframe">preview: selected input</option>
              </select>
              <button disabled={busy || (!active && !chain.length)} onClick={() => void previewOne()}>👁 Preview</button>
              <select value={galleryScope} disabled={busy} onChange={(event) => setGalleryScope(event.target.value as typeof galleryScope)}>
                <option value="included">run included ({filters.filter((entry) => !entry.excluded && !entry.broken).length})</option>
                <option value="excluded">run excluded ({filters.filter((entry) => entry.excluded).length})</option>
                <option value="all">run all ({filters.filter((entry) => !entry.broken).length})</option>
              </select>
              <button disabled={busy || job?.state === "running"} onClick={() => void runGallery()}>▦ Apply all filters</button>
              <button disabled={busy || job?.state === "running" || !active} onClick={() => void runGallery({ filterId })}>⚙ Permutations</button>
              <button disabled={busy || job?.state === "running"} onClick={() => void scanRetinters()}>🚫 Find retinters</button>
              <button disabled={busy} onClick={() => setChain((current) => [...current, { entryId: "", params: {} }])}>＋ Chain</button>
              <button disabled={busy || job?.state === "running" || !selectedPath || (!active && !chain.length)} onClick={() => void run("Previewing chain", () => runStack(false))}>⇓ Preview chain</button>
              <button disabled={busy || job?.state === "running" || !selectedPath || (!active && !chain.length)} onClick={() => void run("Applying to ALL frames", () => runStack(true))}>⏵ Apply to ALL frames</button>
              <label className="video-import-toggle">
                <input type="checkbox" checked={fullSelectors} disabled={busy} onChange={(event) => setFullSelectors(event.target.checked)} />
                selectors in full run
              </label>
            </div>
            {chain.length > 0 && (
              <div className="video-import-chain" role="list">
                <div className="video-import-chain-step is-extract-step">
                  <b>0.</b>
                  <span>EXTRACT · {criteriaLabel()}</span>
                  <label>preview candidates <input className="video-import-param" type="number" min={1} value={candidateCount} disabled={busy} onChange={(event) => setCandidateCount(event.target.value)} /></label>
                  <span className="video-import-chain-none">
                    {kept?.size ? `feeding: ${kept.size} group-selected (preview only)` : picked ? "feeding: the picked input item (preview only)" : frames.length ? `${frames.length} frame(s) extracted` : "runs first when the chain executes"}
                  </span>
                </div>
                {chain.map((step, index) => {
                  const entry = filters.find((candidate) => candidate.id === step.entryId) || null;
                  const isSelector = step.entryId.startsWith("select:");
                  return (
                    <div key={index} className="video-import-chain-step" role="listitem">
                      <b>{index + 1}.</b>
                      <select
                        value={step.entryId}
                        disabled={busy}
                        onChange={(event) => {
                          const id = event.target.value;
                          if (id.startsWith("select:")) { editChain((current) => current.map((existing, at) => (at === index ? { entryId: id, params: { n: "" } } : existing)), index + 1); return; }
                          const pickedEntry = filters.find((candidate) => candidate.id === id);
                          editChain((current) => current.map((existing, at) => (at === index ? { entryId: id, params: Object.fromEntries(Object.entries(pickedEntry?.params || {}).map(([key, value]) => [key, String(value)])) } : existing)), index + 1);
                        }}
                      >
                        <option value="">&lt;none&gt;</option>
                        <optgroup label="— group selectors —">
                          <option value="select:user">selector: let USER decide which item is used{selectorScore("user")}</option>
                          <option value="select:unique">selector: N most unique{selectorScore("unique")}</option>
                          <option value="select:spread">selector: N evenly spread{selectorScore("spread")}</option>
                          <option value="select:random">selector: N random{selectorScore("random")}</option>
                          <option value="select:like">selector: N most like original{selectorScore("like")}</option>
                          <option value="select:unlike">selector: N most unlike original{selectorScore("unlike")}</option>
                        </optgroup>
                        {filters.map((candidate) => (
                          <option key={candidate.id} value={candidate.id} disabled={candidate.broken || candidate.excluded}>
                            {candidate.excluded ? "🚫 " : candidate.skill ? "🛠 " : candidate.lut ? "🎨 " : ""}{candidate.title}
                          </option>
                        ))}
                      </select>
                      {isSelector && (
                        <>
                          <label>N <input className="video-import-param" type="number" min={1} placeholder="all" value={step.params.n || ""} disabled={busy} onChange={(event) => editChain((current) => current.map((existing, at) => (at === index ? { ...existing, params: { ...existing.params, n: event.target.value } } : existing)))} /></label>
                          {!(Number(step.params.n) >= 1) && <span className="video-import-chain-none">no-op until N is set</span>}
                        </>
                      )}
                      {entry && Object.entries(step.params).map(([key, value]) => {
                        const choices = entry.paramChoices?.[key];
                        return (
                          <label key={key}>{key}
                            {choices?.length
                              ? <select className="video-import-param" value={value} disabled={busy} onChange={(event) => editChain((current) => current.map((existing, at) => (at === index ? { ...existing, params: { ...existing.params, [key]: event.target.value } } : existing)))}>{choices.map((choice) => <option key={choice} value={choice}>{choice}</option>)}</select>
                              : <input className="video-import-param" value={value} disabled={busy} onChange={(event) => editChain((current) => current.map((existing, at) => (at === index ? { ...existing, params: { ...existing.params, [key]: event.target.value } } : existing)))} />}
                          </label>
                        );
                      })}
                      {!entry && !isSelector && <span className="video-import-chain-none">no-op</span>}
                      <button disabled={busy} onClick={() => editChain((current) => current.filter((_, at) => at !== index), index)}>×</button>
                    </div>
                  );
                })}
              </div>
            )}
            {beforeAfter && (
              <div className="video-import-preview">
                <figure><img src={asset(beforeAfter.before)} alt="before" /><figcaption>before</figcaption></figure>
                <span className="video-import-preview-arrow">→</span>
                <figure><img src={asset(beforeAfter.after)} alt="after" /><figcaption>after · {beforeAfter.label}</figcaption></figure>
                <button onClick={() => setBeforeAfter(null)}>×</button>
              </div>
            )}
          </div>
        </Section>
      )}

      {gallery && (
        <Section {...section("gallery", "GALLERY", `${gallery.filter((tile) => tile.path).length} tile(s) · click = add to chain + apply to ALL frames`, <button disabled={busy} onClick={() => setGallery(null)}>× Clear</button>)}>
          <div className="vi2-body video-import-gallery" role="list">
            {[...gallery]
              .sort((left, right) => ((filters.find((entry) => entry.id === (right.baseId || right.id))?.votes || 0) - (filters.find((entry) => entry.id === (left.baseId || left.id))?.votes || 0)))
              .map((tile) => {
                const baseId = tile.baseId || tile.id;
                const registered = filters.find((entry) => entry.id === baseId);
                const disabled = !!registered?.excluded;
                const score = registered?.votes || 0;
                return (
                  <div key={tile.id} className={`video-import-gallery-tile${filterId === baseId ? " is-picked" : ""}${disabled ? " is-disabled" : ""}`} role="listitem">
                    {tile.path
                      ? <img src={asset(tile.path)} alt={tile.title} loading="lazy" onClick={() => {
                          if (busy || disabled || !registered) return;
                          pickFilter(baseId);
                          const stepParams = Object.fromEntries(Object.entries(tile.params || registered.params || {}).map(([key, value]) => [key, String(value)]));
                          if (tile.params) setFilterParams(stepParams);
                          // The loop: each gallery pick appends to the chain and the whole
                          // chain re-applies to ALL extracted frames.
                          const nextChain = [...chain, { entryId: baseId, params: stepParams }];
                          setChain(nextChain);
                          void run("Applying chain to ALL frames", () => runStack(true, nextChain));
                        }} />
                      : <span className="video-import-gallery-error">✗</span>}
                    <small>{tile.title}</small>
                    <div className="video-import-gallery-votebar">
                      <button disabled={busy || !registered} onClick={() => void vote([baseId], 1)}>▲</button>
                      <span className={score > 0 ? "is-up" : score < 0 ? "is-down" : ""}>{score}</span>
                      <button disabled={busy || !registered} onClick={() => void vote([baseId], -1)}>▼</button>
                      <button className="video-import-gallery-toggle" disabled={busy || !registered} onClick={() => void setDisabled(baseId, !disabled)}>{disabled ? "↩ enable" : "🚫 disable"}</button>
                    </div>
                  </div>
                );
              })}
          </div>
        </Section>
      )}

      {output.length > 0 && (
        <Section {...section("output", `OUTPUT${outputMode === "full" ? " · FULL RUN" : " · PREVIEW"}`, `${output.length} frame(s)${outputLabel ? ` · via ${outputLabel}` : ""} · click a frame = new base, ALL effects run on it`, <button disabled={busy} onClick={() => setOutput([])}>× Clear</button>)}>
          <div className="vi2-body video-import-frames video-import-output">
            {output.map((frame) => (
              <article key={frame.path} className="video-import-frame is-plain">
                <img src={asset(frame.path)} alt="output" loading="lazy" title={`${frame.path} — click: run ALL effects on this`} onClick={() => {
                  if (busy) return;
                  setPicked(frame.path);
                  setPreviewSource("selectedframe");
                  say("new gallery base: this output frame");
                  void runGallery({ image: frame.path });
                }} />
                <div className="video-import-frame-votes">
                  <button disabled={busy || !appliedIds.length} title={`credit: ${appliedIds.join(", ")}`} onClick={() => void vote(appliedIds, 1)}>▲</button>
                  <button disabled={busy || !appliedIds.length} title={`credit: ${appliedIds.join(", ")}`} onClick={() => void vote(appliedIds, -1)}>▼</button>
                </div>
                <header><small title={frame.path}>{outputLabel || frame.path.split("/").pop()}</small></header>
              </article>
            ))}
          </div>
        </Section>
      )}

      {trail.length > 0 && (
        <Section {...section("trail", "TRAIL / PROBES", `${trail.length} level(s) · probes: ${probes.length ? probes.join(", ") : `last (${trail.length - 1})`}`)}>
          <div className="vi2-body video-import-trail" role="list">
            {trail.map((level, index) => {
              const probed = probes.includes(index) || (!probes.length && index === trail.length - 1);
              return (
                <button key={index} className={`video-import-trail-level${probed ? " is-probed" : ""}`} disabled={busy} onClick={() => setProbes((current) => (current.includes(index) ? current.filter((probe) => probe !== index) : [...current, index].sort((a, b) => a - b)))}>
                  <b>{index}. {level.label}</b>
                  <div className="video-import-trail-thumbs">{level.frames.slice(0, 4).map((item) => <img key={item.path} src={asset(item.path)} alt="" loading="lazy" />)}</div>
                  <small>{level.frames.length} frame(s){probed ? " · ◉ probed" : ""}</small>
                </button>
              );
            })}
          </div>
        </Section>
      )}

      {selected && (
        <Section {...section("members", "MEMBERS — ENTITY EXTRACTION", `${members.length} member(s) · ${members.filter((member) => member.status === "pending").length} pending`)}>
          <div className="vi2-body">
            <div className="video-import-timeline video-import-members">
              <select value={memberModel} disabled={busy} onChange={(event) => setMemberModel(event.target.value)}>
                {!models.length && <option value="">no enabled models</option>}
                {models.map((model) => <option key={model.id} value={model.id}>{model.name}</option>)}
              </select>
              <select value={memberGoal} disabled={busy} onChange={(event) => setMemberGoal(event.target.value as typeof memberGoal)}>
                <option value="any">find any members</option>
                <option value="faces">find faces</option>
                <option value="characters">find characters</option>
                <option value="objects">find objects</option>
                <option value="text">find text/signs</option>
              </select>
              <select value={memberFill} disabled={busy} onChange={(event) => setMemberFill(event.target.value as typeof memberFill)}>
                <option value="median">remove: median inpaint</option>
                <option value="blur">remove: blur fill</option>
                <option value="hole">remove: transparent hole</option>
              </select>
              <label>max/frame <input type="number" min={1} max={8} value={memberMax} disabled={busy} onChange={(event) => setMemberMax(event.target.value)} /></label>
              <label>divide into <input type="number" min={0} max={12} placeholder="off" value={memberTarget} disabled={busy} onChange={(event) => setMemberTarget(event.target.value)} /></label>
              <button disabled={busy || !memberModel || !frames.length} onClick={() => void extractMembers()}>👥 Extract members</button>
            </div>
            {members.length > 0 && (
              <div className="video-import-member-strips" role="list">
                {[...new Set(members.map((member) => member.probeIndex))].sort((a, b) => a - b).map((probeIndex) => {
                  const strip = members.map((member, at) => ({ member, at })).filter(({ member }) => member.probeIndex === probeIndex);
                  return (
                    <div key={probeIndex} className="video-import-member-strip" role="listitem">
                      <header>
                        <b>probe {probeIndex >= 0 ? probeIndex : "·"} · {strip[0]?.member.probeLabel}</b>
                        <small>{strip.length} member(s) · {strip.filter(({ member }) => member.status === "pending").length} pending · {strip.filter(({ member }) => member.status === "accepted").length} ✓ · {strip.filter(({ member }) => member.status === "rejected").length} ✗</small>
                      </header>
                      {strip.map(({ member, at }) => (
                        <article key={`${member.cutout}-${at}`} className={`video-import-member is-${member.status}`}>
                          <img src={asset(member.cutout)} alt={member.name} loading="lazy" />
                          <header><b>{member.name}</b><small>#{member.frameIndex} · pass {member.step}</small></header>
                          <div className="video-import-member-actions">
                            <button disabled={busy || member.status !== "pending"} onClick={() => acceptMember(at)}>✓</button>
                            <button disabled={busy || member.status === "rejected"} onClick={() => void rejectMember(at)}>✗ return</button>
                            <small>{member.status}</small>
                          </div>
                        </article>
                      ))}
                      {Object.entries(memberScenes).filter(([key]) => key.startsWith(`${probeIndex}:`)).map(([key, scenePath]) => (
                        <article key={key} className="video-import-member is-scene">
                          <img src={asset(scenePath)} alt="scene now" loading="lazy" />
                          <header><b>scene now</b></header>
                        </article>
                      ))}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </Section>
      )}

      {selected && (
        <Section {...section("finish", "TURTLE / IMPORT GAME", `${output.length ? "OUTPUT frames feed the finish" : "input frames feed the finish"}`)}>
          <div className="vi2-body video-import-timeline">
            <b>TURTLE</b>
            <select value={turtleModel} disabled={busy} onChange={(event) => setTurtleModel(event.target.value)}>
              {!models.length && <option value="">no enabled models</option>}
              {models.map((model) => <option key={model.id} value={model.id}>{model.name}</option>)}
            </select>
            <button disabled={busy || !turtleModel || (!frames.length && !output.length)} onClick={() => void generateTurtle()}>🐢 Generate turtle programs</button>
            <b>IMPORT GAME</b>
            <label>game id <input type="text" value={gameId} disabled={busy} onChange={(event) => setGameId(event.target.value)} /></label>
            <button disabled={busy || !frames.length || !gameId.trim()} onClick={() => void materialize()}>Materialize as recording</button>
          </div>
        </Section>
      )}
    </section>
  );
}
