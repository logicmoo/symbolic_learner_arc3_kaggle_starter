import { useCallback, useEffect, useRef, useState } from "react";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import "@xterm/xterm/css/xterm.css";
import "../styles/terminal.css";

type ShellInfo = {
  shells: string[];
  default: string;
  os: string;
  ptyAvailable: boolean;
  ptyError?: string;
  defaultCwd?: string;
};

/** A first-class workbench terminal: an xterm.js view bridged over a WebSocket
 * to a real PTY-backed shell on the server (cmd/PowerShell/WSL-bash on Windows,
 * bash/sh/zsh on POSIX). */
export function TerminalPage() {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const termRef = useRef<Terminal | null>(null);
  const fitRef = useRef<FitAddon | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const [info, setInfo] = useState<ShellInfo | null>(null);
  const [shell, setShell] = useState<string>("");
  const [cwd, setCwd] = useState<string>("");
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const response = await fetch("/workbench/terminal/shells");
        if (!response.ok) throw new Error(await response.text());
        const data = (await response.json()) as ShellInfo;
        if (cancelled) return;
        setInfo(data);
        setShell(data.default);
        setCwd(data.defaultCwd || "");
        if (!data.ptyAvailable) setError(`PTY backend unavailable: ${data.ptyError || "not installed"}`);
      } catch (reason) {
        if (!cancelled) setError(reason instanceof Error ? reason.message : String(reason));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
  }, []);

  const connect = useCallback(() => {
    const term = termRef.current;
    const fit = fitRef.current;
    if (!term || !fit) return;
    disconnect();
    term.clear();

    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const query = new URLSearchParams({
      shell,
      cols: String(term.cols),
      rows: String(term.rows),
    });
    if (cwd) query.set("cwd", cwd);
    const ws = new WebSocket(`${proto}://${window.location.host}/workbench/terminal/ws?${query.toString()}`);
    wsRef.current = ws;
    setError(null);

    ws.onopen = () => {
      setConnected(true);
      fit.fit();
      ws.send(JSON.stringify({ t: "r", c: term.cols, r: term.rows }));
      term.focus();
    };
    ws.onmessage = (event) => term.write(event.data as string);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setError("WebSocket error — is the workbench API running?");
  }, [shell, cwd, disconnect]);

  // Create the xterm instance once.
  useEffect(() => {
    if (!hostRef.current) return;
    const term = new Terminal({
      cursorBlink: true,
      fontFamily: 'Consolas, "Cascadia Mono", "DejaVu Sans Mono", monospace',
      fontSize: 13,
      theme: { background: "#0e1116", foreground: "#e6edf3" },
    });
    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(hostRef.current);
    fit.fit();
    term.onData((data) => {
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ t: "i", d: data }));
    });
    termRef.current = term;
    fitRef.current = fit;

    const onResize = () => {
      fit.fit();
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ t: "r", c: term.cols, r: term.rows }));
    };
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      wsRef.current?.close();
      term.dispose();
      termRef.current = null;
      fitRef.current = null;
    };
  }, []);

  return (
    <section className="resource-view terminal-page">
      <div className="resource-heading">
        <div>
          <span>SYSTEM</span>
          <h1>Terminal</h1>
          <p>
            A real PTY-backed shell in the browser. Runs on the workbench host
            {info ? ` (${info.os === "nt" ? "Windows" : "POSIX"})` : ""}.
          </p>
        </div>
      </div>
      <div className="terminal-toolbar">
        <label>
          Shell{" "}
          <select value={shell} disabled={connected || !info?.shells.length} onChange={(e) => setShell(e.target.value)}>
            {(info?.shells || []).map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label className="terminal-cwd">
          Directory{" "}
          <input
            value={cwd}
            disabled={connected}
            placeholder="working directory"
            onChange={(e) => setCwd(e.target.value)}
          />
        </label>
        {connected ? (
          <button onClick={disconnect}>Disconnect</button>
        ) : (
          <button className="primary" disabled={!info?.ptyAvailable || !shell} onClick={connect}>
            Connect
          </button>
        )}
        <span className={connected ? "terminal-status is-on" : "terminal-status"}>
          {connected ? "connected" : "disconnected"}
        </span>
      </div>
      {error && <div className="backend-error"><b>Terminal</b><span>{error}</span></div>}
      <div className="terminal-host" ref={hostRef} />
    </section>
  );
}
