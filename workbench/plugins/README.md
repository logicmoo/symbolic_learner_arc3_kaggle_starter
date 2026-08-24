# Workbench plugins

The backend scans direct child directories of this folder for `plugin.json`.
Each manifest names an `entrypoint` exporting `create_router(manifest)`. The
scan policy is stored in `plugins.json`:

- `startup` discovers and loads the plugin when the API starts. Refresh also
  discovers and loads a newly enabled plugin without restarting.
- `disabled` skips loading it on the next API start. A plugin already loaded
  into the running Python process remains mounted until that process restarts.

The Plugins page displays the filesystem catalog, refreshes discovery, and
edits this policy. Plugin errors are visible instead of silently ignored.

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
proxy.
