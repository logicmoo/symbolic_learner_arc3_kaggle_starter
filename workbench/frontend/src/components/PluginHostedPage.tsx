import { PluginAdminPanel } from "./PluginAdminPanel";
import type { PluginMenuEntry } from "./usePluginMenu";

/** Render a page a plugin installed into the workbench navigation.
 *
 * A plugin that serves its own page is embedded, so the plugin owns the markup.
 * A plugin that publishes an administration descriptor is rendered natively, so
 * the page matches the rest of the application.
 */
export function PluginHostedPage({ entry }: { entry: PluginMenuEntry | null }) {
  if (!entry) {
    return (
      <section className="resource-view">
        <div className="studio-empty">Select a plugin page from the navigation.</div>
      </section>
    );
  }
  if (!entry.available) {
    return (
      <section className="resource-view">
        <div className="resource-heading">
          <div>
            <span>PLUGIN PAGE</span>
            <h1>{entry.label}</h1>
            <p>
              <b>{entry.pluginLabel}</b> is not loaded, so this page is unavailable. Enable it with{" "}
              <b>Scan at startup</b> on the Plugins page and refresh the catalog.
            </p>
          </div>
        </div>
      </section>
    );
  }
  if (!entry.external) {
    return (
      <section className="resource-view">
        <PluginAdminPanel
          adminPath={entry.address}
          declaredPath={entry.declaredDescriptor}
          available
        />
      </section>
    );
  }
  return (
    <section className="resource-view plugin-hosted-page">
      <div className="resource-heading">
        <div>
          <span>{entry.pluginLabel.toUpperCase()}</span>
          <h1>{entry.label}</h1>
          <p>
            Served by the plugin at <code>{entry.address}</code>.
          </p>
        </div>
        <a href={entry.address} target="_blank" rel="noreferrer">
          Open in a new tab
        </a>
      </div>
      <iframe
        className="plugin-hosted-frame"
        src={entry.address}
        title={`${entry.pluginLabel} — ${entry.label}`}
      />
    </section>
  );
}
