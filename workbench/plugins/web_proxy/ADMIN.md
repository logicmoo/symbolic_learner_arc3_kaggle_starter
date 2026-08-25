# Web Proxy administration and setup

[Back to repository README](../../../README.md)

The Web Proxy plugin mounts itself on the workbench API port and forwards HTTP
and WebSocket traffic to origins that are explicitly listed in its manifest.

## Initialization

The plugin loader calls `initialize(manifest)` once per API process, before the
router is mounted. Initialization:

1. verifies the declared runtime requirements, `httpx` and `websockets`;
2. writes the missing transport defaults (`allowedTargets`,
   `requestTimeoutSeconds`, `followRedirects`) into `plugin.json` so this page
   always edits concrete values.

If a requirement is unsatisfied, install the repository extras into the root
environment and refresh the plugin catalog:

```bat
.\.venv\Scripts\python.exe -m pip install -e ".[all]"
```

**Initialize plugin** on this page re-runs the same routine without restarting
the API.

## Outbound allowlist

`Allowed targets` holds one origin per line, for example
`http://127.0.0.1:8801`. Requests to any other origin are refused with HTTP 403,
and WebSocket upgrades are closed with policy code 1008, so this plugin never
becomes an open proxy.

Proxied requests use the path form:

```text
/web_proxy/http/127.0.0.1:8801/<upstream-path>
```

GET, POST, PUT, PATCH, DELETE, OPTIONS, and HEAD are supported. Query strings,
request bodies, response bodies, status codes, and end-to-end headers are
preserved. WebSocket text and binary frames and negotiated subprotocols are
relayed bidirectionally.

Edits saved here are written to `plugin.json` and take effect on the next
proxied request; the running router re-reads the manifest when it changes.

## Request handling

- **Request timeout (seconds)** bounds each proxied HTTP request. `0` keeps the
  original behaviour of waiting indefinitely.
- **Follow upstream redirects** off forwards `3xx` responses to the caller
  unchanged, which is what a transparent proxy should normally do.

## Probing

**Probe targets now** issues a short `GET` against every allowed target and
reports the status code or the transport error. It is a reachability check, not
a health contract: a target answering `404` is still reachable.
