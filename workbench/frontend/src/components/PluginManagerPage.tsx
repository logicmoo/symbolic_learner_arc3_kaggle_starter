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
type Plugin = {
  id: string;
  label?: string;
  description?: string;
  version?: string;
  routePrefix?: string;
  allowedTargets?: string[];
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
};
type PluginResponse = { plugins: Plugin[]; policyPath: string; manifestName?: string };

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

  const selected = catalog?.plugins.find((plugin) => plugin.id === openPage?.pluginId);
  const manifestName = catalog?.manifestName || "plugin.json";

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
      <div className="plugin-catalog">
        {(catalog?.plugins || []).map((plugin) => (
          <article className="plugin-card" key={plugin.id}>
            <header>
              <div>
                <span>{plugin.loaded ? "LOADED" : plugin.scan.toUpperCase()}</span>
                <h2>{plugin.label || plugin.id}</h2>
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
        ))}
        {!busy && catalog?.plugins.length === 0 && (
          <div className="studio-empty">No plugin manifests found.</div>
        )}
      </div>
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
