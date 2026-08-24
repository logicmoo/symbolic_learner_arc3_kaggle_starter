from __future__ import annotations

import asyncio
from collections.abc import Iterable
from typing import Any
from urllib.parse import urlencode

import httpx
import websockets
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response


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


def create_router(manifest: dict[str, Any]) -> APIRouter:
    prefix = str(manifest.get("routePrefix") or "/web-proxy").rstrip("/")
    allowed_targets = {
        str(target).rstrip("/")
        for target in manifest.get("allowedTargets", [])
        if isinstance(target, str)
    }
    router = APIRouter()

    @router.api_route(
        f"{prefix}/{{scheme}}/{{authority}}/{{path:path}}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        include_in_schema=True,
    )
    async def proxy_http(request: Request, scheme: str, authority: str, path: str) -> Response:
        target = _target_url(scheme, authority, path, allowed_targets, request.url.query)
        body = await request.body()
        async with httpx.AsyncClient(follow_redirects=False, timeout=None) as client:
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
                allowed_targets,
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

    return router
