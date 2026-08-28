import { useCallback, useEffect, useState } from "react";
import { PluginAdminPanel } from "./PluginAdminPanel";

type PluginUiPage = {
  id: string;
  label: string;
  kind: string;
  descriptor: string;
  address?: string;
  apiDescriptor?: string;
  external?: boolean;
  glyph?: string;
  group?: string;
  declared?: boolean;
};
type PluginInitCommandResult = {
  command: string;
  path?: string;
  applied: boolean;
  detail?: string;
};
type PluginInitialization = {
  ready: boolean;
  checks: { kind: string; name: string; satisfied: boolean; detail?: string }[];
};
type PluginInstall = {
  requires?: string[];
  install?: string | null;
  files?: (string | { path: string; description?: string })[];
  steps?: string[];
};
type PluginUninstall = {
  uninstall?: string | null;
  steps?: string[];
};
type PluginLifecycleHooks = Record<string, string | null>;
type PluginLifecycle = {
  standalone?: boolean;
  hooks?: PluginLifecycleHooks;
  note?: string;
};
type PluginApiSection = {
  method?: string;
  path?: string;
  description?: string;
  address?: string;
} | null;
type PluginApi = Record<string, PluginApiSection | string | undefined> & { note?: string };
type PluginMount = { path: string; redirect: string; description?: string; requestedBy?: string };
type Plugin = {
  id: string;
  label?: string;
  description?: string;
  version?: string;
  routePrefix?: string;
  allowedTargets?: string[];
  mounts?: PluginMount[];
  scan: "startup" | "disabled";
  loaded: boolean;
  path: string;
  error?: string;
  adminPath?: string;
  adminApiPath?: string;
  configPage?: string;
  adminAvailable?: boolean;
  adminDeclaredOnDisk?: boolean;
  uiPages?: PluginUiPage[];
  initCommandResults?: PluginInitCommandResult[];
  initialization?: PluginInitialization;
  "plugin-install"?: PluginInstall;
  "plugin-uninstall"?: PluginUninstall;
  "plugin-lifecycle"?: PluginLifecycle;
  "plugin-api"?: PluginApi;
  apiSections?: Record<string, PluginApiSection>;
};
type PluginAssessment = {
  id: string;
  label: string;
  expected: { loaded: boolean; phase: string; reason: string };
  actual: {
    loaded: boolean;
    phase: string;
    alive: boolean | null;
    statusAddress?: string | null;
    statusDetail?: string;
    initializationReady: boolean;
    unmetChecks: string[];
    error?: string;
  };
  ok: boolean;
  verdict: string;
};
type PluginResponse = { plugins: Plugin[]; policyPath: string; manifestName?: string };
/** Phases whose invocation could stop or restart a plugin's own process --
 * never rendered as a one-click link, only as a labelled, non-clickable entry. */
const DESTRUCTIVE_API_SECTIONS = new Set(["restart", "shutdown"]);
/** The six lifecycle phases, each with its "your turn"/"everyone's turn is done" hook name. */
const LIFECYCLE_PHASES = [
  "install",
  "uninstall",
  "workbenchStartup",
  "workbenchShutdown",
  "workspaceStartup",
  "workspaceShutdown",
] as const;

export function PluginManagerPage() {
  const [catalog, setCatalog] = useState<PluginResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openPage, setOpenPage] = useState<{ pluginId: string; page: PluginUiPage } | null>(null);

  const load = useCallback(async (refresh = false) => {
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(`/api/plugins${refresh ? "/refresh" : ""}`, {
        method: refresh ? "POST" : "GET",
      });
      if (!response.ok) throw new Error(await response.text());
      setCatalog((await response.json()) as PluginResponse);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  }, []);
  useEffect(() => void load(), [load]);

  const setScan = async (plugin: Plugin, scan: Plugin["scan"]) => {
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(`/api/plugins/${encodeURIComponent(plugin.id)}`, {
        method: "PUT",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ scan }),
      });
      if (!response.ok) throw new Error(await response.text());
      setCatalog((await response.json()) as PluginResponse);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  };

  const [lifecycleResults, setLifecycleResults] = useState<
    Record<string, { hook: string | null; ok: boolean; detail?: string }>
  >({});
  const [lifecycleBusy, setLifecycleBusy] = useState<string | null>(null);
  // Assessment: expected phase/state per plugin versus what actually runs.
  const [assessment, setAssessment] = useState<{ assessments: PluginAssessment[]; okCount: number; total: number } | null>(null);
  const [assessBusy, setAssessBusy] = useState(false);
  const loadAssessment = useCallback(async () => {
    setAssessBusy(true);
    try {
      const response = await fetch("/api/plugins/assessment");
      if (!response.ok) throw new Error(await response.text());
      setAssessment(await response.json());
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setAssessBusy(false);
    }
  }, []);
  useEffect(() => void loadAssessment(), [loadAssessment]);
  const runLifecyclePhase = async (pluginId: string, phase: string) => {
    const key = `${pluginId}:${phase}`;
    setLifecycleBusy(key);
    try {
      const response = await fetch(`/api/plugins/${encodeURIComponent(pluginId)}/lifecycle/${encodeURIComponent(phase)}`, {
        method: "POST",
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || response.statusText);
      setLifecycleResults((current) => ({ ...current, [key]: payload }));
    } catch (reason) {
      setLifecycleResults((current) => ({
        ...current,
        [key]: { hook: null, ok: false, detail: reason instanceof Error ? reason.message : String(reason) },
      }));
    } finally {
      setLifecycleBusy(null);
    }
  };

  const selected = catalog?.plugins.find((plugin) => plugin.id === openPage?.pluginId);
  const manifestName = catalog?.manifestName || "plugin.json";

  // One tab per plugin plus the combined "All plugins" view; a plugin's tab
  // shows the same card the common page shows, full width. The selected tab
  // is mirrored into ?subview= and honored on a fresh load.
  const [pluginTab, setPluginTab] = useState<string>(() => {
    if (typeof window === "undefined") return "all";
    return new URLSearchParams(window.location.search).get("subview") || "all";
  });
  useEffect(() => {
    if (typeof window === "undefined") return;
    const url = new URL(window.location.href);
    if (pluginTab === "all") url.searchParams.delete("subview");
    else url.searchParams.set("subview", pluginTab);
    if (url.href !== window.location.href) window.history.replaceState(window.history.state, "", url);
  }, [pluginTab]);

  const renderCard = (plugin: Plugin) => (
          <article className="plugin-card" key={plugin.id}>
            <header>
              <div>
                <span>{plugin.loaded ? "LOADED" : plugin.scan.toUpperCase()}</span>
                <h2>
                  {plugin.label || plugin.id}
                  {plugin.version && <small className="plugin-version"> v{plugin.version}</small>}
                </h2>
              </div>
              <select
                aria-label={`${plugin.label || plugin.id} scan policy`}
                value={plugin.scan}
                disabled={busy}
                onChange={(event) => void setScan(plugin, event.target.value as Plugin["scan"])}
              >
                <option value="startup">Scan at startup</option>
                <option value="disabled">Disabled</option>
              </select>
            </header>
            <p>{plugin.description || "No description supplied."}</p>
            {plugin.routePrefix && (
              <dl>
                <dt>Route</dt>
                <dd>
                  <code>{plugin.routePrefix}</code>
                </dd>
              </dl>
            )}
            {(plugin.allowedTargets || []).map((target) => (
              <dl key={target}>
                <dt>Allowed target</dt>
                <dd>
                  <code>{target}</code>
                </dd>
              </dl>
            ))}
            {plugin.initialization && (
              <dl>
                <dt>Initialization</dt>
                <dd className={plugin.initialization.ready ? "plugin-ready" : "plugin-incomplete"}>
                  {plugin.initialization.ready
                    ? "Requirements satisfied"
                    : `${plugin.initialization.checks.filter((check) => !check.satisfied).length} unmet requirement(s)`}
                </dd>
              </dl>
            )}
            {(plugin.initCommandResults || []).map((result) => (
              <dl key={`${result.command}:${result.path}`}>
                <dt>Init command</dt>
                <dd className={result.applied ? "plugin-ready" : "plugin-incomplete"}>
                  <code>{result.command}</code> {result.detail || (result.applied ? "applied" : "not applied")}
                </dd>
              </dl>
            ))}
            {(plugin.mounts || []).map((mount) => (
              <dl key={mount.path}>
                <dt>Mount</dt>
                <dd>
                  <code>{mount.path}</code> → <code>{mount.redirect}</code>
                  {mount.requestedBy && <small> (requested by {mount.requestedBy})</small>}
                </dd>
              </dl>
            ))}
            {plugin["plugin-install"] && (
              <fieldset className="plugin-admin-section">
                <legend>Setup</legend>
                {(plugin["plugin-install"].requires || []).length > 0 && (
                  <p>Requires: {(plugin["plugin-install"].requires || []).join(", ")}</p>
                )}
                {plugin["plugin-install"].install && (
                  <pre className="plugin-admin-install">{plugin["plugin-install"].install}</pre>
                )}
                {(plugin["plugin-install"].steps || []).length > 0 && (
                  <ol className="plugin-admin-steps">
                    {(plugin["plugin-install"].steps || []).map((step, index) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ol>
                )}
              </fieldset>
            )}
            {plugin["plugin-uninstall"] && (
              <fieldset className="plugin-admin-section">
                <legend>Uninstall</legend>
                {plugin["plugin-uninstall"].uninstall && (
                  <pre className="plugin-admin-install">{plugin["plugin-uninstall"].uninstall}</pre>
                )}
                {(plugin["plugin-uninstall"].steps || []).length > 0 && (
                  <ol className="plugin-admin-steps">
                    {(plugin["plugin-uninstall"].steps || []).map((step, index) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ol>
                )}
              </fieldset>
            )}
            {plugin["plugin-lifecycle"] && (
              <fieldset className="plugin-admin-section">
                <legend>
                  Lifecycle {plugin["plugin-lifecycle"].standalone ? "(standalone)" : "(embedded)"}
                </legend>
                <ul className="plugin-lifecycle-list">
                  {LIFECYCLE_PHASES.flatMap((phase) => [phase, `${phase}After`]).map((phaseKey) => {
                    const hooks = plugin["plugin-lifecycle"]?.hooks || {};
                    if (!(phaseKey in hooks)) return null;
                    const hookName = hooks[phaseKey];
                    const key = `${plugin.id}:${phaseKey}`;
                    const result = lifecycleResults[key];
                    return (
                      <li key={phaseKey}>
                        <code>{phaseKey}</code>
                        <span>{hookName ? `→ ${hookName}` : "— (stub)"}</span>
                        <button
                          disabled={lifecycleBusy === key}
                          title={hookName ? `Call ${hookName} on this plugin now` : "No hook is declared for this phase"}
                          onClick={() => void runLifecyclePhase(plugin.id, phaseKey)}
                        >
                          {lifecycleBusy === key ? "Running…" : "Run"}
                        </button>
                        {result && (
                          <small className={result.ok ? "plugin-ready" : "plugin-incomplete"}>
                            {result.detail || (result.ok ? "ok" : "not called")}
                          </small>
                        )}
                      </li>
                    );
                  })}
                </ul>
                {plugin["plugin-lifecycle"].note && <p>{plugin["plugin-lifecycle"].note}</p>}
              </fieldset>
            )}
            {plugin.apiSections && Object.keys(plugin.apiSections).length > 0 && (
              <fieldset className="plugin-admin-section">
                <legend>API sections</legend>
                <ul className="plugin-api-list">
                  {Object.entries(plugin.apiSections).map(([name, section]) => {
                    if (!section) {
                      return (
                        <li key={name}>
                          <b>{name}</b> <small>not available</small>
                        </li>
                      );
                    }
                    const address = section.address || section.path || "";
                    const clickable = section.method === "GET" && !DESTRUCTIVE_API_SECTIONS.has(name);
                    return (
                      <li key={name}>
                        <b>{name}</b>
                        <small>{section.method}</small>
                        {clickable ? (
                          <a href={address} target="_blank" rel="noreferrer">
                            <code>{address}</code>
                          </a>
                        ) : (
                          <code>{address}</code>
                        )}
                        {section.description && <small>{section.description}</small>}
                      </li>
                    );
                  })}
                </ul>
                {plugin["plugin-api"]?.note && <p>{String(plugin["plugin-api"].note)}</p>}
              </fieldset>
            )}
            <ul className="plugin-page-links">
              {(plugin.uiPages || []).map((page) => {
                const address = page.address || page.apiDescriptor || page.descriptor;
                const open = page.external
                  ? undefined
                  : () =>
                      setOpenPage(
                        openPage?.pluginId === plugin.id && openPage.page.id === page.id
                          ? null
                          : { pluginId: plugin.id, page },
                      );
                return (
                  <li key={page.id}>
                    {page.external ? (
                      <a href={address} target="_blank" rel="noreferrer">
                        <span>{page.glyph || "⬡"}</span>
                        <b>{page.label}</b>
                        <code>{address}</code>
                      </a>
                    ) : (
                      <button
                        disabled={busy}
                        className={
                          openPage?.pluginId === plugin.id && openPage.page.id === page.id ? "is-open" : ""
                        }
                        onClick={open}
                      >
                        <span>{page.glyph || "⬡"}</span>
                        <b>{page.label}</b>
                        <code>{address}</code>
                      </button>
                    )}
                    <small>{page.kind}</small>
                  </li>
                );
              })}
            </ul>
            {plugin.adminPath && !plugin.adminDeclaredOnDisk && (
              <small>
                No page declaration in <code>{manifestName}</code>; using the shared configure page
                at <code>{plugin.adminPath}</code>.
              </small>
            )}
            <small>{plugin.path}</small>
            {plugin.error && <div className="plugin-error">{plugin.error}</div>}
          </article>
  );

  const shownPlugin = catalog?.plugins.find((plugin) => plugin.id === pluginTab);
  return (
    <section className="resource-view plugin-manager-page">
      <div className="resource-heading">
        <div>
          <span>SYSTEM EXTENSIONS</span>
          <h1>Plugins</h1>
          <p>
            Filesystem plugins discovered beneath <code>workbench/plugins</code>. Each plugin mounts
            its routes on the workbench API port and declares its pages in{" "}
            <code>{manifestName}</code>.
          </p>
        </div>
        <button disabled={busy} onClick={() => void load(true)}>
          {busy ? "Scanning…" : "Refresh plugins"}
        </button>
      </div>
      {error && (
        <div className="backend-error">
          <b>Plugin error</b>
          <span>{error}</span>
        </div>
      )}
      <div className="plugin-tabs" role="tablist" aria-label="Plugin tabs">
        <button
          type="button"
          role="tab"
          aria-selected={pluginTab === "all"}
          className={`plugin-tab${pluginTab === "all" ? " is-active" : ""}`}
          onClick={() => setPluginTab("all")}
        >
          All plugins
        </button>
        {(catalog?.plugins || []).map((plugin) => (
          <button
            key={plugin.id}
            type="button"
            role="tab"
            aria-selected={pluginTab === plugin.id}
            className={`plugin-tab${pluginTab === plugin.id ? " is-active" : ""}${plugin.loaded ? "" : " is-unloaded"}`}
            title={plugin.error || plugin.description || plugin.id}
            onClick={() => setPluginTab(plugin.id)}
          >
            {plugin.label || plugin.id}
          </button>
        ))}
      </div>
      <section className="plugin-assessment" aria-label="Plugin assessment">
        <header>
          <b>
            Assessment{assessment ? ` — ${assessment.okCount}/${assessment.total} as expected` : ""}
          </b>
          <span>where each plugin should be (from its scan policy) versus where it actually is</span>
          <button disabled={assessBusy} onClick={() => void loadAssessment()}>
            {assessBusy ? "Assessing…" : "↻ Assess"}
          </button>
        </header>
        {assessment && (
          <table>
            <thead>
              <tr>
                <th>plugin</th>
                <th>should be</th>
                <th>actually</th>
                <th>server</th>
                <th>verdict</th>
              </tr>
            </thead>
            <tbody>
              {assessment.assessments
                .filter((entry) => pluginTab === "all" || entry.id === pluginTab)
                .map((entry) => (
                  <tr key={entry.id} className={entry.ok ? "is-ok" : "is-off"}>
                    <td><b>{entry.label}</b></td>
                    <td>
                      {entry.expected.phase}
                      <small> ({entry.expected.reason})</small>
                    </td>
                    <td>{entry.actual.phase}</td>
                    <td>
                      {entry.actual.alive === true && <span className="plugin-ready">alive</span>}
                      {entry.actual.alive === false && <span className="plugin-incomplete">dead</span>}
                      {entry.actual.alive === null && <span>—</span>}
                      {entry.actual.statusAddress && (
                        <code title={entry.actual.statusDetail || ""}> {entry.actual.statusAddress}</code>
                      )}
                    </td>
                    <td className={entry.ok ? "plugin-ready" : "plugin-incomplete"}>
                      {entry.verdict}
                      {entry.actual.unmetChecks.length > 0 && (
                        <small> unmet: {entry.actual.unmetChecks.join(", ")}</small>
                      )}
                      {entry.actual.error && <small> {entry.actual.error}</small>}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        )}
        {!assessment && <p>{assessBusy ? "Probing every plugin's status endpoint…" : "No assessment yet."}</p>}
      </section>
      {pluginTab === "all" && (
        <div className="plugin-catalog">
          {(catalog?.plugins || []).map((plugin) => renderCard(plugin))}
          {!busy && catalog?.plugins.length === 0 && (
            <div className="studio-empty">No plugin manifests found.</div>
          )}
        </div>
      )}
      {pluginTab !== "all" && (
        <div className="plugin-catalog plugin-catalog-single" role="tabpanel" aria-label={shownPlugin?.label || pluginTab}>
          {shownPlugin ? renderCard(shownPlugin) : <div className="studio-empty">No plugin named {pluginTab}.</div>}
        </div>
      )}
      {openPage && (
        <PluginAdminPanel
          key={`${openPage.pluginId}:${openPage.page.id}`}
          adminPath={openPage.page.address || openPage.page.apiDescriptor || openPage.page.descriptor}
          declaredPath={openPage.page.descriptor}
          available={selected?.loaded === true}
          onClose={() => setOpenPage(null)}
        />
      )}
      {catalog && <small className="plugin-policy-path">Policy: {catalog.policyPath}</small>}
    </section>
  );
}
