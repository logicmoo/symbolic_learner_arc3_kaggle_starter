# Workbench plugins

[Back to repository README](../../README.md)

The backend scans direct child directories of this folder for `plugin.json`.
Each manifest names an `entrypoint` exporting `create_router(manifest)`. The
scan policy is stored in `plugins.json`:

- `startup` discovers and loads the plugin when the API starts. Refresh also
  discovers and loads a newly enabled plugin without restarting.
- `disabled` skips loading it on the next API start. A plugin already loaded
  into the running Python process remains mounted until that process restarts.

## Hiding a plugin directory

`HIDE_` is a filesystem-level escape hatch, not a `plugin.json` setting. The
scanner ignores any direct child directory whose name starts with `hide_`,
case-insensitively, so names such as `hide_example` and `HIDE_example` behave
the same. The plugin is omitted from the catalog and Plugins page; its manifest
is not read, its entrypoint is not imported, and its initialization commands do
not run. This differs from `scan: "disabled"`, which leaves the plugin visible
in the catalog.

Add or remove the prefix by renaming the directory, then refresh discovery or
restart the backend. Refresh cannot unmount a plugin that is already loaded, so
a restart is required to fully deactivate its existing routes.

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

## Reaching a plugin: you serve HTTP, the dev server proxies for you

A plugin never needs to know or care about the desktop UI's Vite dev server
(`workbench/frontend`, port 5173 by default) or edit anything under
`workbench/frontend/` to be reachable from it. `vite.config.ts` reads every
plugin's `routePrefix` (and any `mounts` path it asked `web_proxy` to add)
straight off disk at startup and generates a matching proxy rule to the
workbench API port (8000 by default) automatically — see
`pluginProxyPrefixes()`/`pluginProxy()` in `workbench/frontend/vite.config.ts`.
Anything the dev server does not otherwise own (its own module graph, HMR
websocket, and static assets) falls back to the API port too, so even an
undeclared path still reaches the API. In short: **the browser always talks
to Vite; Vite forwards to the API; nothing about a plugin's own code changes
between the two.**

That means a plugin's own job is only ever to *serve real HTTP*, one of two
ways:

- **Embedded** — export `create_router(manifest)` from `plugin.py`. The
  loader mounts that router directly into the same process serving the API
  port, so it is reachable the moment the plugin loads.
- **Standalone** — run your own HTTP server on your own port (see
  `plugin-lifecycle.standalone` and the "standalone plugin" paragraph
  below), and declare a `plugin-init` command asking `web_proxy` to mount
  your `routePrefix` onto that port. `web_proxy` then forwards every request
  under that prefix to your server, so it is reachable through the same API
  port as an embedded plugin, no differently from the dev server's point of
  view.

Either way, a plugin does not add CORS headers, handle the Vite dev origin,
or otherwise treat the browser specially — every request it receives has
already been proxied through the API by the time it arrives.

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
    { "command": "web_proxy", "path": "/ws_collab", "redirect": "http://127.0.0.1:8802" }
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

The catalog entry returned by `GET /workbench/plugins` adds:

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

`plugin-uninstall` is the mirror of `plugin-install`: an `uninstall` command
string (or `null` when there is nothing to run, e.g. a vendored nested project
you just delete or a first-party plugin with nothing to remove) plus
human-readable `steps` describing how to cleanly remove or disable the plugin
(stop its process, uninstall its package, un-mount anything another plugin
did on its behalf). Like `plugin-install`, this is metadata read from disk; it
is not wired to an automatic "Uninstall" button in the loader yet.

```json
"plugin-uninstall": {
  "uninstall": "python -m pip uninstall -y my-plugin",
  "steps": ["Stop the standalone server.", "Uninstall the package."]
}
```

## Lifecycle phases: `plugin-lifecycle`

There are six points where a plugin could need to run code, and **each point
is itself two sub-phases**: a "your turn" sub-phase that every plugin runs
independently (order does not matter), followed by an "everyone's turn is
done" sub-phase that runs once, after every plugin has finished its own "your
turn" work for that phase. The second sub-phase exists so a plugin can react
to what every *other* plugin declared or registered during the first —
`web_proxy` is the running example: it cannot apply another plugin's
requested mount until it knows about every plugin's requested mount, so
mounting has to happen in the phase *after* every plugin has had its turn to
ask, not during the round where plugins are still asking.

| Phase | "Your turn" hook | "Everyone's turn is done" hook | When |
| --- | --- | --- | --- |
| Install | `install` | `installAfter` | Each plugin's own `plugin-install` setup runs; then, once every plugin is considered installed, anything that depends on the full set being present runs. |
| Uninstall | `uninstall` | `uninstallAfter` | Each plugin's own `plugin-uninstall` teardown runs; then, once every plugin being removed has finished, anything else (e.g. a mount another plugin held on its behalf) is cleaned up. |
| Workbench startup | `workbenchStartup` | `workbenchStartupAfter` | The API process starts and loads each plugin; then, once every plugin has loaded, cross-plugin requests declared during loading are applied. |
| Workbench shutdown/restart | `workbenchShutdown` | `workbenchShutdownAfter` | The API process is stopping or about to reload. |
| Workspace startup | `workspaceStartup` | `workspaceStartupAfter` | A workspace becomes the active one. |
| Workspace shutdown/restart | `workspaceShutdown` | `workspaceShutdownAfter` | A workspace stops being the active one. |

Two hooks are real, wired-up code today; the rest are declarative stubs:

* **`workbenchStartup` → `initialize(manifest)`.** The loader calls this once
  per plugin, before mounting its router, while it loads every plugin's
  manifest in the plugins directory (see `_scan` in `plugin_api.py`). This is
  each plugin's "your turn" — for example, a plugin declares a `plugin-init`
  command asking another plugin (typically `web_proxy`) to do something on
  its behalf once everyone has loaded.
* **`workbenchStartupAfter` → `apply_plugin_init(command)`.** After every
  plugin has loaded (the whole "your turn" round is over), the loader calls
  `_run_init_commands`, which replays every plugin's declared `plugin-init`
  commands against the target plugin's `apply_plugin_init`. `web_proxy` is the
  only plugin that exports this today — it is how `/ws_collab`, `/emullm`,
  and `/mailbox_chat` get mounted onto their standalone servers, entirely from
  manifest declarations, without `web_proxy`'s own code needing to know about
  any of those plugins in advance.
* **`workbenchShutdown` / `workbenchShutdownAfter` → whichever function name
  a plugin declares.** Unlike the other stub phases, this one *is* wired up,
  but generically: `system_control_api.trigger_api_restart` (the handler
  behind the workbench's own **Restart** button/`/system/restart`) calls
  `plugin_api.run_workbench_shutdown()` right before touching the reload
  marker. That function looks up `plugin-lifecycle.hooks.workbenchShutdown` on
  every *loaded* plugin, calls the named function if the plugin's module
  exports it (the "your turn" round), then does the same for
  `workbenchShutdownAfter` (the "everyone's turn is done" round). A plugin
  that leaves both `null` — every plugin today — is simply skipped, so this
  currently runs as a no-op scan, not a no-op feature: the mechanism is real,
  no plugin has opted in yet.
  **This is a notification, not a command.** A self-restart only restarts the
  embedded workbench API process. A plugin running in **standalone mode**
  runs as its own separate process (see the standalone paragraph below) that
  is not restarted by this at all — its `workbenchShutdown` hook, if it ever
  implements one, must not stop or restart its own server just because it was
  notified the embedded API is restarting. It exists so a standalone plugin
  can react to *the API going away for a moment* (for example, pause
  something that depended on being reachable at `/plugin_id/...` through
  `web_proxy` during the gap) without assuming its own process needs to do
  anything else.

A self-restart deliberately runs **only** `workbenchShutdown`/
`workbenchShutdownAfter` — never install, uninstall, or any workspace-*
phase, since restarting our own embedded process is none of those things.

Every other phase — `install`/`installAfter`, `uninstall`/`uninstallAfter`,
and `workspaceStartup`/`workspaceStartupAfter`/`workspaceShutdown`/
`workspaceShutdownAfter` — remains a **declarative stub only**: not called
by anything yet. `plugin-lifecycle` in `plugin.json` records which phases a
plugin *would* need and which function name would implement each, so this is
designed once instead of per-plugin later:

```json
"plugin-lifecycle": {
  "standalone": true,
  "hooks": {
    "install": null,
    "installAfter": null,
    "uninstall": null,
    "uninstallAfter": null,
    "workbenchStartup": null,
    "workbenchStartupAfter": null,
    "workbenchShutdown": null,
    "workbenchShutdownAfter": null,
    "workspaceStartup": null,
    "workspaceStartupAfter": null,
    "workspaceShutdown": null,
    "workspaceShutdownAfter": null
  },
  "note": "Runs as its own standalone server by default; a workbench restart does not restart it, so it does not need to treat workbenchShutdown as anything more than a heads-up."
}
```

`standalone: true` matters because most of these plugins (`ws_collab`,
`emullm`, `mailbox_chat`) are full nested projects that run as their own
standalone server process by default (`ws_collab`/`emullm` also accept
`..._PLUGIN_MODE=embedded` to opt into mounting in-process instead;
`mailbox_chat` is standalone-only with no embedded mode). A standalone
process manages its own start, stop, and restart outside the workbench
entirely, so restarting the embedded workbench API does **not** restart it —
the workbench only ever talks to it over HTTP, and its `plugin.py` only
ensures the process is running (spawning it on demand, idempotently) before
returning an empty router. Its `install`/`plugin-install` phase is a
standalone install of its own nested project (its own
`requirements.txt`/`pyproject.toml`, its own venv), not something the
workbench installs on its behalf. `pycoplex` is dual-mode: its embedded router
always registers, and by default it also launches a standalone mirror of the
same routes on its own port behind the `/pycoplex` mount, so it uses the
workbench startup/shutdown phases (it
already implements `initialize` for the first) but is not workspace-scoped
today. `web_proxy` is the one plugin that is *inherently* embedded-only —
described in its own manifest as only adding routes to whichever process
embeds it, with no server of its own — so it needs the workbench phases for
the same reason (and is the one plugin that implements
`workbenchStartupAfter`, via `apply_plugin_init`), but again is not
workspace-scoped.


Set a hook to `null` to mean "not implemented" rather than omitting the key, so
the manifest always shows the full set of twelve hooks (six phases, each with
its "your turn"/"everyone's turn is done" pair) a plugin was considered
against.

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
proxy. An `allowedTargets` entry may be an exact origin
(`http://127.0.0.1:8801`) or a wildcard pattern using `*`/`?` glob syntax
(`*://127.0.0.1:*/*` allows any scheme and any port on localhost); a trailing
`/*` or `/**` is trimmed before matching, since the check is always against a
bare origin. A wildcard entry is counted in "Allowed targets" but is not
individually probed for reachability, since it is a pattern, not an address.
The allowlist is re-read from `plugin.json` when it changes, so edits
made on the configure page apply without a restart.

See [`web_proxy/ADMIN.md`](web_proxy/ADMIN.md) for its configure page.
