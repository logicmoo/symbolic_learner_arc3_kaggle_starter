import { useCallback, useEffect, useRef, useState } from "react";
import "../styles/google_meet_bridge.css";

/**
 * Google Meet — the Meet STT subsystem rehosted inside the workbench frame:
 * the workbench menu stays on the left, help on the right, and this middle
 * leg shows the live bridge — current meeting, live caption feed, and the
 * controls to create/join meetings (delivered over the real agent mailbox).
 *
 * Google does not allow meet.google.com itself inside an iframe
 * (X-Frame-Options), so the video window stays in the bridge's own popup
 * browser; everything else about the meeting lives here.
 */

const BRIDGE = "http://127.0.0.1:48699";

type BridgeHealth = {
  ok?: boolean;
  service?: string;
  meetingUrl?: string | null;
  lastCaptionAt?: string | null;
  captionCount?: number;
  outbox?: string;
  recipients?: string[];
};

type CaptionRow = { at: number; iso: string; speaker: string; text: string };

export function GoogleMeetBridgePage() {
  const [health, setHealth] = useState<BridgeHealth | null>(null);
  const [offline, setOffline] = useState(true);
  const [captions, setCaptions] = useState<CaptionRow[]>([]);
  const sinceRef = useRef(0);
  const [joinUrl, setJoinUrl] = useState("");
  const [note, setNote] = useState("");
  const feedRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let cancelled = false;
    const tick = async () => {
      try {
        const response = await fetch(`${BRIDGE}/health`, { signal: AbortSignal.timeout(2500) });
        const payload = (await response.json()) as BridgeHealth;
        if (!cancelled) { setHealth(payload); setOffline(false); }
      } catch {
        if (!cancelled) setOffline(true);
      }
    };
    void tick();
    const timer = window.setInterval(() => void tick(), 3000);
    return () => { cancelled = true; window.clearInterval(timer); };
  }, []);

  useEffect(() => {
    if (offline) return;
    let cancelled = false;
    const tick = async () => {
      try {
        const response = await fetch(`${BRIDGE}/captions?since=${sinceRef.current}`, { signal: AbortSignal.timeout(2500) });
        const payload = (await response.json()) as { captions?: CaptionRow[]; now?: number };
        const rows = payload.captions || [];
        if (!cancelled && rows.length) {
          sinceRef.current = Math.max(...rows.map((row) => row.at));
          setCaptions((current) => [...current, ...rows].slice(-400));
          window.setTimeout(() => feedRef.current?.scrollTo({ top: feedRef.current.scrollHeight }), 50);
        }
      } catch { /* bridge poll hiccup — the health loop reports offline */ }
    };
    const timer = window.setInterval(() => void tick(), 1500);
    return () => { cancelled = true; window.clearInterval(timer); };
  }, [offline]);

  const command = useCallback(async (text: string, label: string) => {
    setNote(`sending ${label}…`);
    try {
      const response = await fetch("/workbench/mailbox/send", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ to: health?.outbox || "google-meet", text, sender: "workbench-meet-page" }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setNote(`${label} sent — the bridge picks it up within ~2s`);
    } catch (reason) {
      setNote(`✗ ${label} failed: ${reason instanceof Error ? reason.message : String(reason)}`);
    }
  }, [health?.outbox]);

  return (
    <section className="resource-view google-meet-page">
      <div className="resource-heading">
        <div>
          <span>GOOGLE MEET · STT SUBSYSTEM</span>
          <h1>Google Meet bridge</h1>
          <p>
            Meet&apos;s live captions are the workbench&apos;s best speech recognizer. The bridge keeps a{" "}
            <b>servant meeting</b> listening to the room mic — and joins any meeting you invite it to, so
            you and others can talk to each other <i>and</i> to the workbench. Captions land in the agent
            mailbox; replies go back into the Meet chat.
          </p>
        </div>
      </div>

      <div className="google-meet-columns">
        <div className="google-meet-main">
          <div className={`google-meet-card ${offline ? "is-offline" : "is-online"}`}>
            <header>
              <b>{offline ? "● bridge offline" : "● bridge online"}</b>
              {!offline && health?.meetingUrl && (
                <a href={health.meetingUrl} target="_blank" rel="noreferrer" title="Open the meeting in a browser window (Google blocks embedding Meet itself)">
                  {health.meetingUrl.replace("https://", "")} ↗
                </a>
              )}
            </header>
            {offline ? (
              <div className="google-meet-offline">
                <p>
                  Start the <b>Google Meet STT Bridge</b> from the <b>Processes</b> page (SYSTEM → Processes),
                  or run it by hand:
                </p>
                <code>python scripts/meet_caption_bridge.py</code>
                <p>
                  First run: a Chrome window pops up — pick your Google account once (the SSO login persists),
                  and the bridge creates its servant meeting and joins it unattended.
                </p>
              </div>
            ) : (
              <dl className="google-meet-stats">
                <div><dt>captions</dt><dd>{health?.captionCount ?? 0}</dd></div>
                <div><dt>last caption</dt><dd>{health?.lastCaptionAt || "—"}</dd></div>
                <div><dt>command mailbox</dt><dd>{health?.outbox || "google-meet"}</dd></div>
                <div><dt>transcripts to</dt><dd>{(health?.recipients || []).join(", ") || "symbolic-workbench-user"}</dd></div>
              </dl>
            )}
          </div>

          <div className="google-meet-card">
            <header><b>MEETINGS</b><small>commands travel through the real agent mailbox</small></header>
            <div className="google-meet-joinrow">
              <input
                type="text"
                placeholder="https://meet.google.com/xxx-yyyy-zzz — a meeting you're inviting the bridge to"
                value={joinUrl}
                onChange={(event) => setJoinUrl(event.target.value)}
              />
              <button disabled={!joinUrl.trim()} onClick={() => void command(`/join ${joinUrl.trim()}`, "/join")}>
                ⇒ Join this meeting
              </button>
              <button onClick={() => void command("/new", "/new")} title="Leave for a fresh servant meeting">
                ✚ New servant meeting
              </button>
            </div>
            {note && <small className="google-meet-note">{note}</small>}
            <p className="google-meet-hint">
              In an invited meeting everyone talks normally; every finished caption line arrives in Chat as{" "}
              <code>meet-&lt;speaker&gt;</code>, and anything sent to <code>{health?.outbox || "google-meet"}</code>{" "}
              is typed into the Meet&apos;s in-call chat for all to see.
            </p>
          </div>

          <div className="google-meet-card google-meet-captions-card">
            <header><b>LIVE CAPTIONS</b><small>{captions.length ? `${captions.length} line(s) this session` : offline ? "waiting for the bridge" : "listening…"}</small></header>
            <div className="google-meet-captions" ref={feedRef}>
              {captions.length === 0 && <p className="google-meet-empty">Caption lines appear here the moment anyone speaks in the bridged meeting.</p>}
              {captions.map((row, index) => (
                <div key={`${row.at}-${index}`} className="google-meet-caption">
                  <small>{row.iso.split("T")[1] || row.iso}</small>
                  <b>{row.speaker}</b>
                  <span>{row.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
