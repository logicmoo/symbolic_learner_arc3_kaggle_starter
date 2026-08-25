from __future__ import annotations

import asyncio
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlsplit

import httpx
import websockets
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

import plugin_admin


HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}
PROBE_TIMEOUT_SECONDS = 2.0

# Set when the loader mounts this plugin, so plugin-init commands from other
# plugins can reach the live manifest and settings.
_MANIFEST: dict[str, Any] | None = None
_SETTINGS: "ProxySettings | None" = None
_REGISTERED_MOUNTS: set[str] = set()


def _filtered_headers(headers: Iterable[tuple[str, str]], *, websocket: bool = False) -> dict[str, str]:
    ignored = HOP_BY_HOP_HEADERS | {"host", "content-length"}
    if websocket:
        ignored |= {
            "sec-websocket-accept",
            "sec-websocket-extensions",
            "sec-websocket-key",
            "sec-websocket-protocol",
            "sec-websocket-version",
        }
    return {name: value for name, value in headers if name.lower() not in ignored}


def _origin_of(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def _target_url(
    scheme: str,
    authority: str,
    path: str,
    allowed_targets: set[str],
    query: str = "",
) -> str:
    if scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Only http and https targets are supported")
    origin = f"{scheme}://{authority}".rstrip("/")
    if origin not in allowed_targets:
        raise HTTPException(status_code=403, detail=f"Proxy target is not allowed: {origin}")
    target = f"{origin}/{path.lstrip('/')}"
    return f"{target}?{query}" if query else target


class ProxySettings:
    """Live view of the manifest so administration edits apply without a restart."""

    def __init__(self, manifest: dict[str, Any]) -> None:
        self._manifest = dict(manifest)
        try:
            self._path: Path | None = plugin_admin.manifest_path(manifest)
        except ValueError:
            self._path = None
        self._stamp: float | None = None
        self._values: dict[str, Any] = dict(manifest)

    @property
    def manifest(self) -> dict[str, Any]:
        return self._manifest

    def current(self) -> dict[str, Any]:
        if self._path is None or not self._path.is_file():
            return self._values
        stamp = self._path.stat().st_mtime
        if stamp != self._stamp:
            try:
                stored = json.loads(self._path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError):
                return self._values
            if isinstance(stored, dict):
                self._values = {**self._manifest, **stored}
                self._stamp = stamp
        return self._values

    def allowed_targets(self) -> set[str]:
        declared = {
            str(target).rstrip("/")
            for target in self.current().get("allowedTargets", [])
            if isinstance(target, str) and target.strip()
        }
        # A mounted redirect implicitly allows its own upstream origin.
        return declared | {_origin_of(mount["redirect"]) for mount in self.mounts()}

    def mounts(self) -> list[dict[str, str]]:
        """Path prefixes this proxy serves on behalf of another plugin."""

        mounts: list[dict[str, str]] = []
        for entry in self.current().get("mounts", []):
            if not isinstance(entry, dict):
                continue
            path = str(entry.get("path") or "").strip()
            redirect = str(entry.get("redirect") or "").strip()
            if not path or not redirect:
                continue
            mounts.append({
                "path": "/" + path.strip("/"),
                "redirect": redirect.rstrip("/"),
                "description": str(entry.get("description") or ""),
                "requestedBy": str(entry.get("requestedBy") or ""),
            })
        return mounts

    def request_timeout(self) -> float | None:
        value = self.current().get("requestTimeoutSeconds")
        try:
            seconds = float(value)
        except (TypeError, ValueError):
            return None
        return seconds if seconds > 0 else None

    def follow_redirects(self) -> bool:
        return self.current().get("followRedirects") is True


async def _probe_target(target: str) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=PROBE_TIMEOUT_SECONDS, follow_redirects=False) as client:
            response = await client.get(target)
        return {"target": target, "reachable": True, "status": response.status_code, "detail": ""}
    except Exception as error:  # noqa: BLE001 - any transport failure is reported verbatim
        # Several httpx transport errors stringify to "", so name the class too.
        detail = f"{type(error).__name__}: {error}" if str(error) else type(error).__name__
        return {"target": target, "reachable": False, "status": 0, "detail": detail}


def create_admin_router(manifest: dict[str, Any]) -> APIRouter:
    """Build the Web Proxy administration and setup page as its own router."""

    settings = ProxySettings(manifest)
    last_probe: dict[str, dict[str, Any]] = {}

    async def describe() -> dict[str, Any]:
        current = settings.current()
        targets = sorted(settings.allowed_targets())
        probes = await asyncio.gather(*(_probe_target(target) for target in targets)) if targets else []
        for probe in probes:
            last_probe[probe["target"]] = probe
        reachable = [probe for probe in probes if probe["reachable"]]
        status_items = [
            plugin_admin.status("Route prefix", plugin_admin.admin_prefix(manifest), "neutral"),
            plugin_admin.status("Allowed targets", len(targets), "ok" if targets else "warn",
                                detail="" if targets else "No target is allowed, so every proxied request returns 403."),
            plugin_admin.status(
                "Reachable now",
                f"{len(reachable)} of {len(targets)}",
                "ok" if targets and len(reachable) == len(targets) else "warn" if targets else "neutral",
            ),
            plugin_admin.status(
                "Request timeout",
                f"{settings.request_timeout():g}s" if settings.request_timeout() else "none",
                "neutral",
            ),
        ]
        for probe in probes:
            status_items.append(
                plugin_admin.status(
                    probe["target"],
                    f"HTTP {probe['status']}" if probe["reachable"] else "unreachable",
                    "ok" if probe["reachable"] else "error",
                    detail=probe["detail"],
                )
            )
        sections = [
            plugin_admin.section(
                "targets",
                "Outbound allowlist",
                [
                    plugin_admin.field(
                        "allowedTargets",
                        "Allowed targets",
                        "stringList",
                        targets,
                        help_text="One origin per line. Requests to any other origin are refused with "
                                  "HTTP 403 so this plugin never becomes an open proxy.",
                        placeholder="http://127.0.0.1:8801",
                    )
                ],
                description="Origins this proxy may forward HTTP and WebSocket traffic to.",
            ),
            plugin_admin.section(
                "transport",
                "Request handling",
                [
                    plugin_admin.field(
                        "requestTimeoutSeconds",
                        "Request timeout (seconds)",
                        "number",
                        current.get("requestTimeoutSeconds") or 0,
                        help_text="0 keeps the original behaviour of waiting indefinitely.",
                    ),
                    plugin_admin.field(
                        "followRedirects",
                        "Follow upstream redirects",
                        "boolean",
                        settings.follow_redirects(),
                        help_text="Off forwards 3xx responses to the caller unchanged.",
                    ),
                ],
                description="How proxied HTTP requests are performed.",
            ),
        ]
        return plugin_admin.descriptor(
            manifest,
            kind="custom",
            status_items=status_items,
            sections=sections,
            actions=[
                plugin_admin.action("probe", "Probe targets now",
                                    description="Re-check every allowed target and refresh this page."),
            ],
        )

    def apply_settings(values: dict[str, Any]) -> dict[str, Any]:
        updates: dict[str, Any] = {}
        if "allowedTargets" in values:
            updates["allowedTargets"] = [
                target.rstrip("/") for target in plugin_admin.string_list(values["allowedTargets"])
            ]
        if "requestTimeoutSeconds" in values:
            try:
                seconds = float(values["requestTimeoutSeconds"] or 0)
            except (TypeError, ValueError) as error:
                raise HTTPException(status_code=400, detail="Request timeout must be a number") from error
            if seconds < 0:
                raise HTTPException(status_code=400, detail="Request timeout cannot be negative")
            updates["requestTimeoutSeconds"] = int(seconds) if seconds.is_integer() else seconds
        if "followRedirects" in values:
            updates["followRedirects"] = values["followRedirects"] in (True, "true", "True", 1, "1")
        return plugin_admin.write_manifest_values(manifest, updates)

    async def probe_action(_body: dict[str, Any]) -> dict[str, Any]:
        targets = sorted(settings.allowed_targets())
        probes = await asyncio.gather(*(_probe_target(target) for target in targets)) if targets else []
        return {"probed": len(probes), "results": probes}

    def initialize_action(_body: dict[str, Any]) -> dict[str, Any]:
        return initialize(settings.current())

    return plugin_admin.build_admin_router(
        manifest,
        describe=describe,
        apply_settings=apply_settings,
        actions={"probe": probe_action},
        initialize=initialize_action,
    )


def apply_plugin_init(command: dict[str, Any]) -> Any:
    """Accept a ``plugin-init`` command from another plugin.

    Another plugin may ask this proxy to mount one of its paths onto an upstream
    base URL, for example WS_COLLAB asking for ``/ws_collab`` to reach its
    standalone server. The mount is persisted in ``plugin.json`` so it survives a
    restart and is visible on the configure page. When the path is not served
    yet this returns an ``APIRouter`` for the loader to mount, so the proxy never
    needs a reference to the API application.
    """

    path = "/" + str(command.get("path") or "").strip().strip("/")
    redirect = str(command.get("redirect") or "").strip().rstrip("/")
    if path == "/" or not redirect:
        raise ValueError("A web_proxy plugin-init command needs both 'path' and 'redirect'")
    if not redirect.startswith(("http://", "https://")):
        raise ValueError(f"Only http and https redirects are supported: {redirect}")
    if _MANIFEST is None or _SETTINGS is None:
        raise ValueError("web_proxy is not mounted yet")
    entry = {
        "path": path,
        "redirect": redirect,
        "description": str(command.get("description") or ""),
        "requestedBy": str(command.get("requestedBy") or ""),
    }
    stored = plugin_admin.read_json_file(plugin_admin.manifest_path(_MANIFEST))
    mounts = [item for item in stored.get("mounts", []) if isinstance(item, dict)]
    remaining = [item for item in mounts if str(item.get("path") or "").rstrip("/") != path]
    if remaining + [entry] != mounts:
        plugin_admin.write_manifest_values(_MANIFEST, {"mounts": remaining + [entry]})
    if path in _REGISTERED_MOUNTS:
        return f"{path} -> {redirect} (already served)"
    return _mount_router([entry], _SETTINGS)


def initialize(manifest: dict[str, Any]) -> dict[str, Any]:
    """Prepare the plugin before its router is mounted on the API application.

    The loader calls this once per process. It verifies the declared runtime
    requirements and writes any missing transport defaults into ``plugin.json``
    so the administration page always has concrete values to edit.
    """

    report = plugin_admin.initialization_report(manifest)
    defaults = {"allowedTargets": [], "mounts": [], "requestTimeoutSeconds": 0, "followRedirects": False}
    missing = {key: value for key, value in defaults.items() if key not in manifest}
    if missing:
        plugin_admin.write_manifest_values(manifest, missing)
    return {"ready": report["ready"], "checks": report["checks"], "defaultsWritten": sorted(missing)}


def _mount_router(mounts: list[dict[str, str]], settings: ProxySettings) -> APIRouter:
    """Build routes that serve mounted paths on behalf of another plugin.

    Each mount gets its own explicit routes rather than a catch-all, so this
    proxy never shadows the API application or another plugin's prefix.
    """

    router = APIRouter()
    for mount in mounts:
        base, upstream = mount["path"], mount["redirect"]

        async def proxy_mounted(
            request: Request,
            remainder: str = "",
            _base: str = base,
            _upstream: str = upstream,
        ) -> Response:
            target = f"{_upstream}/{remainder.lstrip('/')}" if remainder else _upstream
            if request.url.query:
                target = f"{target}?{request.url.query}"
            body = await request.body()
            async with httpx.AsyncClient(
                follow_redirects=settings.follow_redirects(), timeout=settings.request_timeout()
            ) as client:
                upstream_response = await client.request(
                    request.method,
                    target,
                    content=body,
                    headers=_filtered_headers(request.headers.items()),
                )
            return Response(
                content=upstream_response.content,
                status_code=upstream_response.status_code,
                headers=_filtered_headers(upstream_response.headers.multi_items()),
                media_type=upstream_response.headers.get("content-type"),
            )

        methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
        router.add_api_route(base, proxy_mounted, methods=methods, include_in_schema=False)
        router.add_api_route(
            f"{base}/{{remainder:path}}", proxy_mounted, methods=methods, include_in_schema=False
        )
        _REGISTERED_MOUNTS.add(base)
    return router


def create_router(manifest: dict[str, Any]) -> APIRouter:
    global _MANIFEST, _SETTINGS
    _MANIFEST = dict(manifest)
    prefix = str(manifest.get("routePrefix") or "/web-proxy").rstrip("/")
    settings = ProxySettings(manifest)
    _SETTINGS = settings
    router = APIRouter()

    @router.api_route(
        f"{prefix}/{{scheme}}/{{authority}}/{{path:path}}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        include_in_schema=True,
    )
    async def proxy_http(request: Request, scheme: str, authority: str, path: str) -> Response:
        target = _target_url(scheme, authority, path, settings.allowed_targets(), request.url.query)
        body = await request.body()
        async with httpx.AsyncClient(
            follow_redirects=settings.follow_redirects(), timeout=settings.request_timeout()
        ) as client:
            upstream = await client.request(
                request.method,
                target,
                content=body,
                headers=_filtered_headers(request.headers.items()),
            )
        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            headers=_filtered_headers(upstream.headers.multi_items()),
            media_type=upstream.headers.get("content-type"),
        )

    @router.websocket(f"{prefix}/{{scheme}}/{{authority}}/{{path:path}}")
    async def proxy_websocket(websocket: WebSocket, scheme: str, authority: str, path: str) -> None:
        try:
            http_url = _target_url(
                scheme,
                authority,
                path,
                settings.allowed_targets(),
                urlencode(list(websocket.query_params.multi_items())),
            )
        except HTTPException:
            await websocket.close(code=1008)
            return
        ws_url = ("wss://" if http_url.startswith("https://") else "ws://") + http_url.split("://", 1)[1]
        requested_protocols = [
            value.strip()
            for value in websocket.headers.get("sec-websocket-protocol", "").split(",")
            if value.strip()
        ]
        try:
            async with websockets.connect(
                ws_url,
                additional_headers=_filtered_headers(websocket.headers.items(), websocket=True),
                subprotocols=requested_protocols or None,
                max_size=None,
            ) as upstream:
                await websocket.accept(subprotocol=upstream.subprotocol)

                async def client_to_upstream() -> None:
                    while True:
                        message = await websocket.receive()
                        if message["type"] == "websocket.disconnect":
                            await upstream.close()
                            return
                        if message.get("bytes") is not None:
                            await upstream.send(message["bytes"])
                        elif message.get("text") is not None:
                            await upstream.send(message["text"])

                async def upstream_to_client() -> None:
                    async for message in upstream:
                        if isinstance(message, bytes):
                            await websocket.send_bytes(message)
                        else:
                            await websocket.send_text(message)

                tasks = [asyncio.create_task(client_to_upstream()), asyncio.create_task(upstream_to_client())]
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for task in pending:
                    task.cancel()
                for task in done:
                    task.result()
        except (WebSocketDisconnect, websockets.ConnectionClosed):
            return
        except Exception:
            if websocket.client_state.name != "DISCONNECTED":
                await websocket.close(code=1011)

    # Serve any mount already persisted in the manifest from a previous session.
    router.include_router(_mount_router(settings.mounts(), settings))
    return router
