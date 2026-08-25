import { useCallback, useEffect, useMemo, useState } from "react";
import { MarkdownDocument } from "./MarkdownDocument";

export type AdminFieldType =
  | "text"
  | "textarea"
  | "number"
  | "boolean"
  | "select"
  | "stringList"
  | "readonly";

export type AdminField = {
  id: string;
  label: string;
  type: AdminFieldType;
  value: unknown;
  help?: string;
  placeholder?: string;
  options?: string[];
};

export type AdminSection = {
  id: string;
  title: string;
  description?: string;
  fields: AdminField[];
};

export type AdminStatus = {
  label: string;
  value: string;
  tone: "ok" | "warn" | "error" | "neutral";
  detail?: string;
};

export type AdminAction = { id: string; label: string; description?: string; tone?: string };

export type AdminInitializationCheck = {
  kind: string;
  name: string;
  satisfied: boolean;
  detail?: string;
};

export type AdminInitialization = {
  ready: boolean;
  checks: AdminInitializationCheck[];
  steps?: string[];
  install?: string;
  initializePath?: string;
};

export type PluginAdminDescriptor = {
  pluginId: string;
  title: string;
  summary?: string;
  kind?: string;
  adminPath: string;
  declaredOnDisk?: boolean;
  manifestPath?: string;
  settingsPath?: string;
  initialization?: AdminInitialization;
  uiPages?: { id: string; label: string; kind: string; descriptor: string; glyph?: string }[];
  status: AdminStatus[];
  sections: AdminSection[];
  actions: AdminAction[];
  documentation?: string;
  actionResult?: Record<string, unknown>;
};

type Values = Record<string, unknown>;

const listToText = (value: unknown) =>
  Array.isArray(value) ? value.map((item) => String(item)).join("\n") : String(value ?? "");

function initialValues(sections: AdminSection[]): Values {
  const values: Values = {};
  for (const section of sections) {
    for (const field of section.fields) {
      if (field.type === "readonly") continue;
      values[field.id] = field.type === "stringList" ? listToText(field.value) : field.value;
    }
  }
  return values;
}

export function PluginAdminPanel({
  adminPath,
  declaredPath,
  available,
  onClose,
}: {
  adminPath: string;
  declaredPath?: string;
  available: boolean;
  onClose?: () => void;
}) {
  const [descriptor, setDescriptor] = useState<PluginAdminDescriptor | null>(null);
  const [values, setValues] = useState<Values>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const receive = useCallback((payload: PluginAdminDescriptor) => {
    setDescriptor(payload);
    setValues(initialValues(payload.sections || []));
  }, []);

  const request = useCallback(
    async (path: string, init?: RequestInit, successNotice?: string) => {
      setBusy(true);
      setError(null);
      setNotice(null);
      try {
        const response = await fetch(path, init);
        const text = await response.text();
        if (!response.ok) throw new Error(text || response.statusText);
        receive(JSON.parse(text) as PluginAdminDescriptor);
        if (successNotice) setNotice(successNotice);
      } catch (reason) {
        setError(reason instanceof Error ? reason.message : String(reason));
      } finally {
        setBusy(false);
      }
    },
    [receive],
  );

  useEffect(() => {
    if (!available) {
      setDescriptor(null);
      return;
    }
    void request(adminPath);
  }, [adminPath, available, request]);

  const dirty = useMemo(() => {
    if (!descriptor) return false;
    const baseline = initialValues(descriptor.sections || []);
    return Object.keys(baseline).some(
      (key) => String(baseline[key] ?? "") !== String(values[key] ?? ""),
    );
  }, [descriptor, values]);

  const save = () =>
    void request(
      `${adminPath}/settings`,
      {
        method: "PUT",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ values }),
      },
      "Settings saved to the plugin directory.",
    );

  const initialize = () =>
    void request(
      `${adminPath}/initialize`,
      { method: "POST", headers: { "content-type": "application/json" }, body: "{}" },
      "Initialization finished.",
    );

  const runAction = (action: AdminAction) =>
    void request(
      `${adminPath}/actions/${encodeURIComponent(action.id)}`,
      { method: "POST", headers: { "content-type": "application/json" }, body: "{}" },
      `${action.label} finished.`,
    );

  if (!available) {
    return (
      <section className="plugin-admin-panel">
        <header className="plugin-admin-heading">
          <div>
            <span>CONFIGURE</span>
            <h2>Plugin is not loaded</h2>
            <p>
              This plugin serves its configure page at <code>{declaredPath || adminPath}</code> on
              the workbench API port. Enable it with <b>Scan at startup</b> and refresh the plugin
              catalog to reach that page.
            </p>
          </div>
          {onClose && <button onClick={onClose}>Close</button>}
        </header>
      </section>
    );
  }

  const initialization = descriptor?.initialization;
  return (
    <section className="plugin-admin-panel">
      <header className="plugin-admin-heading">
        <div>
          <span>CONFIGURE {descriptor?.kind === "generic" ? "· SHARED PAGE" : ""}</span>
          <h2>{descriptor?.title || "Loading…"}</h2>
          {descriptor?.summary && <p>{descriptor.summary}</p>}
          <small>
            <code>{declaredPath || adminPath}</code>
          </small>
        </div>
        <div className="plugin-admin-heading-actions">
          <button disabled={busy} onClick={() => void request(adminPath)}>
            {busy ? "Working…" : "Reload"}
          </button>
          {onClose && <button onClick={onClose}>Close</button>}
        </div>
      </header>

      {error && (
        <div className="backend-error">
          <b>Configure error</b>
          <span>{error}</span>
        </div>
      )}
      {notice && <div className="plugin-admin-notice">{notice}</div>}

      {initialization && (
        <div
          className={`plugin-admin-init ${initialization.ready ? "is-ready" : "is-incomplete"}`}
        >
          <header>
            <h3>Initialization</h3>
            <button disabled={busy} onClick={initialize}>
              {busy ? "Working…" : "Initialize plugin"}
            </button>
          </header>
          <ul className="plugin-admin-checks">
            {initialization.checks.map((check) => (
              <li key={`${check.kind}:${check.name}`} className={check.satisfied ? "ok" : "error"}>
                <b>{check.satisfied ? "✓" : "✗"}</b>
                <span>
                  {check.kind} <code>{check.name}</code>
                </span>
                {check.detail && <small>{check.detail}</small>}
              </li>
            ))}
          </ul>
          {(initialization.steps || []).length > 0 && (
            <ol className="plugin-admin-steps">
              {(initialization.steps || []).map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
          )}
          {initialization.install && (
            <pre className="plugin-admin-install">{initialization.install}</pre>
          )}
        </div>
      )}

      {(descriptor?.status || []).length > 0 && (
        <div className="plugin-admin-status">
          {(descriptor?.status || []).map((item) => (
            <div key={`${item.label}:${item.value}`} className={`plugin-admin-chip tone-${item.tone}`}>
              <dt>{item.label}</dt>
              <dd>{item.value}</dd>
              {item.detail && <small>{item.detail}</small>}
            </div>
          ))}
        </div>
      )}

      {(descriptor?.sections || []).map((section) => (
        <fieldset className="plugin-admin-section" key={section.id}>
          <legend>{section.title}</legend>
          {section.description && <p>{section.description}</p>}
          {section.fields.map((field) => (
            <label className="plugin-admin-field" key={field.id}>
              <span>{field.label}</span>
              {field.type === "textarea" || field.type === "stringList" ? (
                <textarea
                  rows={field.type === "stringList" ? 4 : 3}
                  placeholder={field.placeholder}
                  value={String(values[field.id] ?? "")}
                  onChange={(event) =>
                    setValues((current) => ({ ...current, [field.id]: event.target.value }))
                  }
                />
              ) : field.type === "boolean" ? (
                <input
                  type="checkbox"
                  checked={values[field.id] === true}
                  onChange={(event) =>
                    setValues((current) => ({ ...current, [field.id]: event.target.checked }))
                  }
                />
              ) : field.type === "select" ? (
                <select
                  value={String(values[field.id] ?? "")}
                  onChange={(event) =>
                    setValues((current) => ({ ...current, [field.id]: event.target.value }))
                  }
                >
                  {(field.options || []).map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              ) : field.type === "readonly" ? (
                <output>{String(field.value ?? "")}</output>
              ) : (
                <input
                  type={field.type === "number" ? "number" : "text"}
                  placeholder={field.placeholder}
                  value={String(values[field.id] ?? "")}
                  onChange={(event) =>
                    setValues((current) => ({ ...current, [field.id]: event.target.value }))
                  }
                />
              )}
              {field.help && <small>{field.help}</small>}
            </label>
          ))}
        </fieldset>
      ))}

      <div className="plugin-admin-actions">
        <button disabled={busy || !dirty} onClick={save}>
          {dirty ? "Save settings" : "Saved"}
        </button>
        {(descriptor?.actions || []).map((action) => (
          <button key={action.id} disabled={busy} title={action.description} onClick={() => runAction(action)}>
            {action.label}
          </button>
        ))}
        {descriptor?.settingsPath && <small>Settings file: {descriptor.settingsPath}</small>}
      </div>

      {descriptor?.actionResult && (
        <pre className="plugin-admin-result">{JSON.stringify(descriptor.actionResult, null, 2)}</pre>
      )}

      {descriptor?.documentation && (
        <div className="plugin-admin-docs">
          <MarkdownDocument content={descriptor.documentation} />
        </div>
      )}
    </section>
  );
}
