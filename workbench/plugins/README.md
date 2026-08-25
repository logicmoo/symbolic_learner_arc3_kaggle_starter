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
| `plugin.json` | The only manifest: identity, routing, pages, install, and settings. |
| `plugin.py` | Entrypoint exporting `create_router`, and optionally `create_admin_router`, `initialize`, `resolve_ui_pages`, and `apply_plugin_init`. |
| `ADMIN.md` | Documentation rendered on a workbench-rendered configure page. |

`plugin.json` and `plugins.json` are plain JSON configuration, not workspace
MeTTa resources. Read and write them with `plugin_admin.read_json_file` and
`plugin_admin.write_json_file`; the workspace resource provider redirects every
`.json` path to a `.metta` sibling and would silently lose plugin edits.

A plugin's `routePrefix` is `/<id>`, so its links are predictable.

## `plugin.json`: everything the scanner reads from disk

The scanner reads the manifest without importing or calling the plugin, so the
Plugins page can build every link from the filesystem alone:

```json
{
  "id": "web_proxy",
  "routePrefix": "/web_proxy",
  "adminPage": "/web_proxy/admin",
  "configPage": "http://127.0.0.1:5173/ws_collab/admin",
  "docs": "ADMIN.md",
  "plugin-install": {
    "requires": ["httpx", "websockets"],
    "install": "python -m pip install -e \".[all]\"",
    "files": [{ "path": "plugin.json", "description": "Plugin manifest." }],
    "steps": ["Install the required packages.", "List the allowed targets."]
  },
  "plugin-init": [
    { "command": "web_proxy", "path": "/ws_collab", "redirect": "http://127.0.0.1:8802/ws_collab" }
  ],
  "ui": {
    "pages": [
      {
        "id": "configure",
        "label": "Configure Web Proxy",
        "kind": "configure",
        "descriptor": "/web_proxy/admin",
        "glyph": "⇄",
        "group": "PLUGINS"
      }
    ]
  }
}
```

A plugin declares its configure page one of two ways:

- **`configPage`** — an absolute URL to a page the plugin serves itself. The
  workbench embeds it, so the plugin owns the markup.
- **`adminPage`** — an API path serving an administration *descriptor*. The
  descriptor is data, and the workbench renders it natively.

Do not use a bare `path` key for this: the loader stores the plugin directory
under `path`. A legacy absolute `path` is still accepted.

Everything is optional. A plugin declaring nothing still gets a configure link
at `<routePrefix>/admin` and a generated configure page.

The catalog entry returned by `GET /api/plugins` adds:

- `adminPath` — the descriptor link the plugin owns on the API port;
- `adminApiPath` — the same routes mirrored beneath `/api` for the browser;
- `configPage` — the absolute page URL, when the plugin serves its own;
- `uiPages[]` — the desktop pages, each with a resolved `address`;
- `initCommandResults[]` — what each `plugin-init` command did;
- `initialization` — the readiness report described below.

## Menus: `ui.pages`

Every entry in `ui.pages` installs a menu item in the workbench navigation,
inside the declared `group` (default `PLUGINS`), with its `glyph` and `label`.
Selecting one opens the page: an absolute `address` is embedded in a frame, and
a descriptor path is rendered natively. The Plugins page lists the same pages as
clickable URLs.

`kind` is `configure` or `admin` for an administration page, `user` for a
day-to-day page. A plugin gets a configure page even if it declares none.

A plugin that knows better than the default mapping exports
`resolve_ui_pages(manifest, pages)` and returns the same entries with `address`
filled in. WS_COLLAB uses this to point every page at the console it serves.

## The administration contract

The declared `adminPage` is served by the plugin on the API port and mirrored
under `/api` so the desktop UI reaches every plugin through one proxied
namespace:

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

`plugin-install` declares what a plugin needs before it can work: importable
`requires` modules, `files` that must exist, the `install` command that repairs
a missing requirement, and human-readable `steps`. The scanner turns that into
an `initialization` report from disk alone, before importing anything, so a
plugin that cannot load explains itself instead of only failing with a
traceback.

A plugin may also export `initialize(manifest)`. The loader calls it once per
process, before `create_router`, and **Initialize plugin** on the configure page
re-runs it without restarting the API. Use it to verify requirements and write
missing defaults into `plugin.json`.

## Asking another plugin to do something: `plugin-init`

`plugin-init` is a list of commands a plugin asks *another* plugin to run once
the whole catalog is loaded, so directory order does not matter. Each command
names the target plugin in `command`. The target implements
`apply_plugin_init(command)` and returns either a description or an `APIRouter`
for the loader to mount, so plugins never touch the application object. Failures
are reported on the requesting plugin instead of breaking the scan.

WS_COLLAB uses this to ask `web_proxy` to serve `/ws_collab` from its standalone
server. The resulting mount is persisted in the proxy's `mounts`, so it survives
a restart, and relays WebSockets as well as HTTP.

## Reaching a plugin from the web port

The Vite dev and preview servers proxy each plugin's `routePrefix` and each
persisted `web_proxy` mount, generated from the manifests. Anything else the web
server does not own also falls back to the API, so a new plugin route works from
the web port without editing `vite.config.ts`. The API root redirects to the web
interface, honouring `WORKBENCH_WEB_URL`.

## Web proxy

`web_proxy` forwards HTTP and WebSocket traffic to targets explicitly listed
in its manifest. The initial target is the local emullm relay:

```text
/web_proxy/http/127.0.0.1:8801/<upstream-path>
```

GET, POST, PUT, PATCH, DELETE, OPTIONS, and HEAD are supported. Query strings,
request bodies, response bodies, status codes, and end-to-end headers are
preserved. WebSocket text/binary frames and negotiated subprotocols are relayed
bidirectionally. Targets not present in `allowedTargets` receive HTTP 403 (or a
WebSocket policy close), preventing this extension from becoming an open
proxy. The allowlist is re-read from `plugin.json` when it changes, so edits
made on the configure page apply without a restart.

See [`web_proxy/ADMIN.md`](web_proxy/ADMIN.md) for its configure page.
