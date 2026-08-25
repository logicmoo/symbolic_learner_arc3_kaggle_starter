# Workbench plugins

[Back to repository README](../../README.md)

The backend scans direct child directories of this folder for `plugin.json`.
Each manifest names an `entrypoint` exporting `create_router(manifest)`. The
scan policy is stored in `plugins.json`:

- `startup` discovers and loads the plugin when the API starts. Refresh also
  discovers and loads a newly enabled plugin without restarting.
- `disabled` skips loading it on the next API start. A plugin already loaded
  into the running Python process remains mounted until that process restarts.

The Plugins page displays the filesystem catalog, refreshes discovery, and
edits this policy. Plugin errors are visible instead of silently ignored.

A plugin adds itself to the workbench API application on the API port, and it
also contributes to the desktop UI. Every plugin has at least a configure page.

## Files a plugin directory may contain

| File | Purpose |
| --- | --- |
| `plugin.json` | Required manifest: `id`, `label`, `entrypoint`, `routePrefix`, and plugin settings. |
| `admin.json` | Administration declaration read straight from disk by the scanner. |
| `plugin.py` | Entrypoint exporting `create_router`, and optionally `create_admin_router` and `initialize`. |
| `ADMIN.md` | Documentation rendered on the configure page. |

`plugin.json` and `plugins.json` are plain JSON configuration, not workspace
MeTTa resources. Read and write them with `plugin_admin.read_json_file` and
`plugin_admin.write_json_file`; the workspace resource provider redirects every
`.json` path to a `.metta` sibling and would silently lose plugin edits.

## `admin.json`: the configure link, read from disk

The scanner reads `admin.json` without importing or calling the plugin, so the
Plugins page can construct the configure link from the filesystem alone:

```json
{
  "label": "Web Proxy administration and setup",
  "summary": "Review proxy reachability and edit the outbound allowlist.",
  "path": "/web-proxy/admin",
  "docs": "ADMIN.md",
  "kind": "custom",
  "init": {
    "requires": ["httpx", "websockets"],
    "install": "python -m pip install -e \".[all]\"",
    "files": [{ "path": "plugin.json", "description": "Plugin manifest." }],
    "steps": ["Install the required packages.", "List the allowed targets."]
  },
  "ui": {
    "pages": [
      {
        "id": "configure",
        "label": "Configure Web Proxy",
        "kind": "configure",
        "descriptor": "/web-proxy/admin",
        "glyph": "⇄",
        "group": "PLUGINS"
      }
    ]
  }
}
```

Everything is optional. A plugin that ships no `admin.json` still gets a
configure link at `<routePrefix>/admin` and a generated configure page.

The catalog entry returned by `GET /api/plugins` adds:

- `adminPath` — the link the plugin owns on the API port;
- `adminApiPath` — the same routes mirrored beneath `/api` for the browser;
- `uiPages[]` — the desktop UI contributions, each with an `apiDescriptor`;
- `initialization` — the readiness report described below.

## The administration contract

The declared `path` is served by the plugin on the API port and mirrored under
`/api` so the desktop UI reaches every plugin through one proxied namespace:

| Method and path | Purpose |
| --- | --- |
| `GET <path>` | Administration descriptor. |
| `PUT <path>/settings` | Persist edited settings. |
| `POST <path>/initialize` | Run initialization again. |
| `POST <path>/actions/{action}` | Run a declared maintenance action. |

The descriptor is data, not markup. The workbench renders `status`, `sections`
of typed `fields`, `actions`, `initialization`, and `documentation` natively so
every plugin page matches the rest of the application. Field types are `text`,
`textarea`, `number`, `boolean`, `select`, `stringList`, and `readonly`.

Build one with `plugin_admin.build_admin_router` from a `create_admin_router`
export. A plugin that exports neither `create_admin_router` nor its own admin
route receives `plugin_admin.generic_admin_router`, which edits the manifest.

## Initialization

`admin.json` declares what a plugin needs before it can work: importable
`requires` modules, `files` that must exist, the `install` command that repairs
a missing requirement, and human-readable `steps`. The scanner turns that into
an `initialization` report from disk alone, before importing anything, so a
plugin that cannot load explains itself instead of only failing with a
traceback.

A plugin may also export `initialize(manifest)`. The loader calls it once per
process, before `create_router`, and **Initialize plugin** on the configure page
re-runs it without restarting the API. Use it to verify requirements and write
missing defaults into `plugin.json`.

Editing a plugin entrypoint reloads the API, exactly like editing a server
module.

## Web proxy

`web_proxy` forwards HTTP and WebSocket traffic to targets explicitly listed
in its manifest. The initial target is the local emullm relay:

```text
/web-proxy/http/127.0.0.1:8801/<upstream-path>
```

GET, POST, PUT, PATCH, DELETE, OPTIONS, and HEAD are supported. Query strings,
request bodies, response bodies, status codes, and end-to-end headers are
preserved. WebSocket text/binary frames and negotiated subprotocols are relayed
bidirectionally. Targets not present in `allowedTargets` receive HTTP 403 (or a
WebSocket policy close), preventing this extension from becoming an open
proxy. The allowlist is re-read from `plugin.json` when it changes, so edits
made on the configure page apply without a restart.

See [`web_proxy/ADMIN.md`](web_proxy/ADMIN.md) for its configure page.
