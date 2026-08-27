from __future__ import annotations

import fnmatch
import importlib.util
import json
from pathlib import Path
from typing import Any, Iterator

from fastapi import APIRouter, Body, FastAPI, HTTPException
from starlette.routing import Match

from plugin_admin import (
    MANIFEST_NAME,
    generic_admin_router,
    has_admin_route,
    initialization_report,
    json_file_exists,
    read_admin_manifest,
    resolve_ui_pages,
    read_json_file,
    write_json_file,
)



PLUGINS_ROOT = Path(__file__).resolve().parents[1] / "plugins"
POLICY_PATH = PLUGINS_ROOT / "plugins.json"
API_PREFIX = "/api"
router = APIRouter(prefix="/plugins", tags=["plugins"])
_app: FastAPI | None = None
_loaded: set[str] = set()
_modules: dict[str, Any] = {}
_init_applied: dict[str, set[str]] = {}
_init_results: dict[str, list[dict[str, Any]]] = {}
_catalog: list[dict[str, Any]] = []


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = read_json_file(path)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid plugin JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Plugin JSON must contain an object: {path}")
    return value


def _policy() -> dict[str, Any]:
    if not json_file_exists(POLICY_PATH):
        return {"pluginsFound": {}}
    return _read_json(POLICY_PATH)


# plugins.json declares how discovery works, not just per-plugin overrides:
#   startupScan   glob masks (relative to the plugins root) probed for
#                 manifests -- two levels deep by default
#   skipScan      case-insensitive masks; a manifest whose relative path or
#                 any path segment matches is never scanned (HIDE_* default)
#   pluginsFound  auto-maintained: every plugin discovery finds is recorded
#                 here as {"path", "scan", "enabled"} so a person can flip a
#                 single "enabled": false (or set "scan": "disabled") to keep
#                 it unloaded; existing entries are never overwritten
#   *_Help        documentation keys, ignored by the loader
DEFAULT_STARTUP_SCAN = ["*/*/plugin.json", "*/plugin.json"]
DEFAULT_SKIP_SCAN = ["HIDE_*"]


def _mask_list(policy_doc: dict[str, Any], key: str, default: list[str]) -> list[str]:
    declared = policy_doc.get(key)
    if not isinstance(declared, list):
        return list(default)
    masks = [str(entry).strip() for entry in declared if str(entry).strip()]
    return masks or list(default)


def _skipped_by_masks(relative: Path, masks: list[str]) -> bool:
    rel = relative.as_posix().casefold()
    for mask in masks:
        lowered = mask.casefold()
        if fnmatch.fnmatch(rel, lowered):
            return True
        if any(fnmatch.fnmatch(part.casefold(), lowered) for part in relative.parts):
            return True
    return False


def _discover_manifests(policy_doc: dict[str, Any]) -> list[Path]:
    root = Path(PLUGINS_ROOT)
    skip = _mask_list(policy_doc, "skipScan", DEFAULT_SKIP_SCAN)
    seen: set[Path] = set()
    found: list[Path] = []
    for mask in _mask_list(policy_doc, "startupScan", DEFAULT_STARTUP_SCAN):
        try:
            matches = list(root.glob(mask))
        except (OSError, ValueError):
            continue
        for manifest_path in matches:
            directory = manifest_path.parent
            key = directory.resolve()
            if key in seen:
                continue
            if _skipped_by_masks(directory.relative_to(root), skip):
                continue
            if not json_file_exists(manifest_path):
                continue
            seen.add(key)
            found.append(manifest_path)
    return sorted(found)


def _plugins_found(policy_doc: dict[str, Any]) -> dict[str, Any]:
    section = policy_doc.get("pluginsFound")
    return section if isinstance(section, dict) else {}


def _record_plugins_found(policy_doc: dict[str, Any], found: dict[str, dict[str, Any]]) -> None:
    """Record every discovered plugin in plugins.json's pluginsFound.

    Each first sighting writes ``{"path", "scan", "enabled": true}``; existing
    entries (including ones a person flipped to ``"enabled": false`` or
    repointed with ``"scan"``) are left alone.
    """

    section = policy_doc.get("pluginsFound")
    if not isinstance(section, dict):
        section = {}
        policy_doc["pluginsFound"] = section
    missing = {pid: stub for pid, stub in found.items() if pid not in section}
    if not missing:
        return
    section.update(missing)
    try:
        Path(POLICY_PATH).write_text(json.dumps(policy_doc, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def _ui_page(page: dict[str, Any]) -> dict[str, Any]:
    """Add the browser-reachable address for a declared desktop page.

    A plugin that exported ``resolve_ui_pages`` has already set ``address``; the
    rest use the shared resolution, where an absolute descriptor is opened as
    declared and a path is mirrored beneath ``/api``.
    """

    descriptor = str(page.get("descriptor") or "")
    external = bool(page.get("external")) or descriptor.startswith(("http://", "https://"))
    address = str(page.get("address") or "") or (descriptor if external else f"{API_PREFIX}{descriptor}")
    return {**page, "external": external, "address": address, "apiDescriptor": address}


def _resolved_pages(manifest: dict[str, Any], admin: dict[str, Any]) -> list[dict[str, Any]]:
    pages = resolve_ui_pages(manifest, list(admin.get("ui", {}).get("pages", [])), api_prefix=API_PREFIX)
    return [_ui_page(page) for page in pages]


def _route_is_registered(path: str) -> bool:
    """Is ``path`` actually handled by a route mounted on the running app?

    True both for a route a plugin mounted directly (an embedded plugin's own
    ``create_router`` path) and for a ``web_proxy`` mount's catch-all route
    that forwards a standalone plugin's prefix onward -- either way, a
    request to ``path`` would reach something real, not 404.
    """

    if _app is None:
        return False
    scope = {"type": "http", "path": path, "method": "GET", "path_params": {}, "root_path": ""}
    for route in _app.routes:
        try:
            match, _ = route.matches(scope)
        except Exception:  # noqa: BLE001 - a route that cannot evaluate this scope is not a match
            continue
        if match is not Match.NONE:
            return True
    return False


def _resolve_api_section(plugin_id: str, entry: Any) -> dict[str, Any] | None:
    """Resolve one declared ``plugin-api`` section to the address a caller should use.

    A section's declared ``path`` is usually already the plugin-prefixed,
    through-the-workbench path (``/mailbox_chat/health``). Some routes are
    instead genuinely shared across several plugin prefixes and a bare,
    absolute-from-root path (see EMU_LLM's ``/mailbox/...`` shim routes,
    which also answer at ``/llm_emul/mailbox/...``, ``/ws_collab/v1/mailbox/...``,
    and ``/mailbox_chat/v1/mailbox/...``). When a declared path is not already
    prefixed with this plugin's own id, we overlay it onto our own
    absolute-from-root address space by prepending ``/<plugin_id>`` -- but we
    prefer that only when a route is actually registered there; otherwise the
    bare path, as declared, is what really answers.
    """

    if not isinstance(entry, dict):
        return None
    path = str(entry.get("path") or "")
    if not path:
        return None
    prefix = f"/{plugin_id}"
    if path == prefix or path.startswith(f"{prefix}/"):
        address = path
    elif path.startswith("/api/") or path.startswith(("http://", "https://", "ws://", "wss://")):
        # The workbench's own /api namespace and absolute URLs are never
        # overlaid onto a plugin prefix — a standalone plugin's catch-all
        # mount would otherwise "match" and swallow them.
        address = path
    else:
        prefixed = f"{prefix}{path}" if path.startswith("/") else f"{prefix}/{path}"
        address = prefixed if _route_is_registered(prefixed) else path
    return {**entry, "address": address}


def _resolved_api_sections(plugin_id: str, manifest: dict[str, Any]) -> dict[str, Any]:
    declared = manifest.get("plugin-api")
    if not isinstance(declared, dict):
        return {}
    return {name: _resolve_api_section(plugin_id, entry) for name, entry in declared.items() if name != "note"}


def _resolved_mailbox_endpoint(plugin_id: str, manifest: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve the optional top-level ``mailboxEndpoint`` manifest property.

    A plugin that serves a mailbox directory declares where its mailbox list
    answers, either as a bare path string or as ``{path, protocol?,
    description?}``. The resolved ``address`` is what mailbox-aware pages (the
    Chat page) query; every declaring plugin is queried, so no server's
    mailboxes are dropped. ``protocol`` defaults to ``ws_collab`` (a
    ``{mailboxes: [...]}`` directory whose sibling routes ``/messages``,
    ``/agents``, ... share the same base); other values (for example
    ``registry``) mark directory-only sources.
    """

    declared = manifest.get("mailboxEndpoint")
    if isinstance(declared, str):
        declared = {"path": declared}
    if not isinstance(declared, dict):
        return None
    resolved = _resolve_api_section(plugin_id, declared)
    if resolved is not None:
        resolved.setdefault("protocol", "ws_collab")
    return resolved


def _resolved_services_endpoint(plugin_id: str, manifest: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve the optional top-level ``servicesEndpoint`` manifest property.

    Points at wherever the plugin's endpoint list can be fetched: a native
    self-description (ws_collab's ``/endpoints``), an OpenAPI document, or the
    workbench enumerator ``/api/plugins/<id>/endpoints`` for embedded routers.
    The Chat page mounts each one as a queryable, read-only mailbox whose
    messages are the endpoints themselves.
    """

    declared = manifest.get("servicesEndpoint")
    if isinstance(declared, str):
        declared = {"path": declared}
    if not isinstance(declared, dict):
        return None
    return _resolve_api_section(plugin_id, declared)


def _scan(*, register: bool) -> list[dict[str, Any]]:
    global _catalog
    policy_doc = _policy()
    plugins_found = _plugins_found(policy_doc)
    catalog: list[dict[str, Any]] = []
    manifest_paths = _discover_manifests(policy_doc)
    root = Path(PLUGINS_ROOT)
    found: dict[str, dict[str, Any]] = {}
    seen_ids: dict[str, str] = {}
    for manifest_path in manifest_paths:
        try:
            manifest = _read_json(manifest_path)
            plugin_id = str(manifest.get("id") or manifest_path.parent.name)
            # One id, one plugin: a second directory declaring an already-seen
            # id is listed as a duplicate but never loaded or recorded.
            if plugin_id in seen_ids:
                catalog.append({
                    "id": manifest_path.parent.name,
                    "label": manifest_path.parent.name,
                    "scan": "disabled",
                    "loaded": False,
                    "adminAvailable": False,
                    "error": f"duplicate plugin id '{plugin_id}' (already provided by {seen_ids[plugin_id]})",
                    "path": str(manifest_path.parent),
                })
                continue
            seen_ids[plugin_id] = manifest_path.parent.relative_to(root).as_posix()
            manifest_scan = str(manifest.get("scan", "startup"))
            found[plugin_id] = {
                "path": manifest_path.relative_to(root).as_posix(),
                "scan": manifest_scan,
                "enabled": True,
            }
            entry = plugins_found.get(plugin_id) if isinstance(plugins_found.get(plugin_id), dict) else {}
            # Effective mode: the pluginsFound entry wins over the manifest;
            # "enabled": false disables regardless of scan mode.
            scan_mode = str(entry.get("scan") or manifest_scan)
            if entry.get("enabled") is False:
                scan_mode = "disabled"
            item = {**manifest, "id": plugin_id, "scan": scan_mode, "path": str(manifest_path.parent), "loaded": plugin_id in _loaded}
            # ``path`` now names the plugin directory, so the manifest's own
            # declared administration path is preserved under its own key.
            item["declaredPath"] = str(manifest.get("path") or "")
            # The administration link, desktop UI pages, and initialization
            # requirements are read from the plugin directory, so the Plugins
            # page can build them without importing or calling the plugin.
            admin = read_admin_manifest(item)
            item["admin"] = admin
            item["adminPath"] = admin["path"]
            item["configPage"] = admin.get("configPage", "")
            item["adminDeclaredOnDisk"] = bool(admin.get("declared"))
            item["adminApiPath"] = f"{API_PREFIX}{admin['path']}"
            item["uiPages"] = _resolved_pages(item, admin)
            item["initCommands"] = admin.get("initCommands", [])
            item["initCommandResults"] = _init_results.get(plugin_id, [])
            item["initialization"] = initialization_report(item)
            if register and scan_mode == "startup" and plugin_id not in _loaded:
                entrypoint = manifest_path.parent / str(manifest.get("entrypoint") or "plugin.py")
                spec = importlib.util.spec_from_file_location(f"workbench_plugin_{plugin_id}", entrypoint)
                if spec is None or spec.loader is None:
                    raise ValueError(f"Cannot load plugin entrypoint: {entrypoint}")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if _app is None or not hasattr(module, "create_router"):
                    raise ValueError("Plugin must export create_router(manifest)")
                # A plugin may prepare its filesystem state before it is mounted.
                if hasattr(module, "initialize"):
                    item["initializeResult"] = module.initialize(dict(item))
                plugin_router = module.create_router(dict(item))
                _app.include_router(plugin_router)
                # Every plugin contributes a configure page. A plugin that
                # builds its own administration router keeps it; the rest
                # receive the shared manifest-backed one at the same link.
                if hasattr(module, "create_admin_router"):
                    admin_router = module.create_admin_router(dict(item))
                elif has_admin_route(plugin_router, item):
                    admin_router = None
                else:
                    admin_router = generic_admin_router(dict(item))
                    item["admin"] = {**admin, "kind": "generic"}
                if admin_router is not None:
                    _app.include_router(admin_router)
                    # Mirror the same routes beneath /api so the desktop UI
                    # reaches every plugin configure page through one namespace.
                    _app.include_router(admin_router, prefix=API_PREFIX)
                _modules[plugin_id] = module
                _loaded.add(plugin_id)
                item["loaded"] = True
                # A plugin may resolve where its own pages live, for example a
                # plugin that serves them from its standalone port.
                if hasattr(module, "resolve_ui_pages"):
                    item["uiPages"] = [
                        _ui_page(page)
                        for page in module.resolve_ui_pages(dict(item), list(admin.get("ui", {}).get("pages", [])))
                    ]
                item["initialization"] = initialization_report(item)
            item["adminAvailable"] = item["loaded"]
            item["adminApiPath"] = f"{API_PREFIX}{item['adminPath']}"
            catalog.append(item)
        except Exception as error:
            failed = {"id": manifest_path.parent.name, "label": manifest_path.parent.name, "scan": "disabled", "loaded": False, "adminAvailable": False, "error": str(error), "path": str(manifest_path.parent)}
            try:
                declaration = read_admin_manifest(failed)
                failed["admin"] = declaration
                failed["adminPath"] = declaration["path"]
                failed["configPage"] = declaration.get("configPage", "")
                failed["adminApiPath"] = f"{API_PREFIX}{declaration['path']}"
                failed["uiPages"] = _resolved_pages(failed, declaration)
                failed["initialization"] = initialization_report(failed)
            except Exception:  # noqa: BLE001 - a broken directory still lists
                pass
            catalog.append(failed)
    if register:
        _run_init_commands(catalog)
    # Resolved after plugin-init mounts are applied, so a standalone plugin's
    # prefixed route (added to _app by _run_init_commands above) is already
    # registered by the time we check for it here.
    for item in catalog:
        item["apiSections"] = _resolved_api_sections(str(item.get("id") or ""), item)
        item["mailboxEndpoint"] = _resolved_mailbox_endpoint(str(item.get("id") or ""), item)
        item["servicesEndpoint"] = _resolved_services_endpoint(str(item.get("id") or ""), item)
    _record_plugins_found(policy_doc, found)
    _catalog = catalog
    return catalog


def _run_init_commands(catalog: list[dict[str, Any]]) -> None:
    """Run every declared ``plugin-init`` command against the plugin it names.

    A plugin may ask another loaded plugin to prepare something on its behalf,
    for example ``web_proxy`` mounting ``/ws_collab`` onto a standalone server.
    Commands run after the whole catalog is loaded so order in the directory
    listing does not matter, and each result is reported on the requesting
    plugin instead of failing the scan.
    """

    for item in catalog:
        commands = item.get("initCommands") or []
        if not commands or not item.get("loaded"):
            continue
        results: list[dict[str, Any]] = []
        for command in commands:
            target_id = str(command.get("command") or "")
            module = _modules.get(target_id)
            outcome: dict[str, Any] = {"command": target_id, "path": command.get("path", "")}
            # One plugin may send several commands to the same target (for
            # example two web_proxy mounts), so applied-tracking is keyed by
            # the whole command identity, not just the target plugin.
            command_key = f"{target_id}:{command.get('path', '')}"
            if command_key in _init_applied.get(item["id"], set()):
                continue
            if module is None:
                outcome |= {"applied": False, "detail": f"Plugin '{target_id}' is not loaded"}
            elif not hasattr(module, "apply_plugin_init"):
                outcome |= {"applied": False, "detail": f"Plugin '{target_id}' accepts no plugin-init commands"}
            else:
                try:
                    detail = module.apply_plugin_init(dict(command))
                    if isinstance(detail, APIRouter):
                        # The target plugin returned routes for the loader to
                        # mount, so plugins never touch the application object.
                        _app.include_router(detail)
                        detail = f"mounted {command.get('path', '')}"
                    outcome |= {"applied": True, "detail": detail if isinstance(detail, str) else ""}
                    _init_applied.setdefault(item["id"], set()).add(command_key)
                except Exception as error:  # noqa: BLE001 - reported, never fatal
                    outcome |= {"applied": False, "detail": str(error)}
            results.append(outcome)
        if results:
            _init_results[item["id"]] = results
            item["initCommandResults"] = results


def _call_lifecycle_hook(item: dict[str, Any], module: Any, hook_phase: str, *, reason: str) -> dict[str, Any] | None:
    """Call one declared hook on one plugin's module, if it names one it exports.

    Returns ``None`` when there is nothing to call (no module loaded, no hook
    declared for this phase, or the module does not export the named
    function) so a caller can tell "nothing to do" apart from a real result.
    """

    if module is None:
        return None
    hooks = (item.get("plugin-lifecycle") or {}).get("hooks") or {}
    hook_name = hooks.get(hook_phase)
    if not hook_name or not hasattr(module, hook_name):
        return None
    standalone = bool((item.get("plugin-lifecycle") or {}).get("standalone"))
    notice = {**item, "lifecyclePhase": hook_phase, "lifecycleReason": reason, "standalone": standalone}
    try:
        detail = getattr(module, hook_name)(notice)
        return {"id": item.get("id"), "phase": hook_phase, "hook": hook_name, "ok": True,
                "detail": detail if isinstance(detail, str) else ""}
    except Exception as error:  # noqa: BLE001 - reported, never fatal
        return {"id": item.get("id"), "phase": hook_phase, "hook": hook_name, "ok": False, "detail": str(error)}


def run_lifecycle_phase(phase: str, *, reason: str = "") -> list[dict[str, Any]]:
    """Run one declared lifecycle phase's two sub-hooks for every loaded plugin.

    Looks up ``plugin-lifecycle.hooks.<phase>`` (the "your turn" hook) and
    ``plugin-lifecycle.hooks.<phase>After`` (the "everyone's turn is done"
    hook) on each loaded plugin's manifest, and calls the named function on
    its module if the module exports it. A plugin that leaves a hook ``null``
    (the common case today -- only ``workbenchStartup``/``workbenchStartupAfter``
    are wired to a real function anywhere) is simply skipped.

    This is a notification, not a command: the hook is called with the
    catalog item plus ``lifecyclePhase``/``lifecycleReason``/``standalone`` so
    a plugin can decide what, if anything, it needs to do. In particular a
    standalone plugin (its own separate process) must not treat a
    ``workbenchShutdown`` notification as "restart yourself too" -- only the
    embedded workbench API process is restarting, not the plugin's own
    process, so a standalone plugin's own lifecycle is unaffected unless it
    explicitly decides otherwise.

    Errors are reported per plugin rather than raised, since one plugin's
    broken hook must never block the workbench's own restart or shutdown.
    """

    results: list[dict[str, Any]] = []

    def _call_round(hook_phase: str) -> None:
        for item in _catalog:
            outcome = _call_lifecycle_hook(item, _modules.get(item.get("id")), hook_phase, reason=reason)
            if outcome is not None:
                results.append(outcome)

    _call_round(phase)
    _call_round(f"{phase}After")
    return results


def run_workbench_shutdown(reason: str = "restart") -> list[dict[str, Any]]:
    """The one phase a self-restart runs: ``workbenchShutdown`` then ``workbenchShutdownAfter``.

    Deliberately does not touch install, uninstall, or workspace-* phases --
    restarting our own embedded API process is none of those things.
    """

    return run_lifecycle_phase("workbenchShutdown", reason=reason)


def install_plugins(app: FastAPI) -> None:
    global _app
    _app = app
    _scan(register=True)


@router.post("/{plugin_id}/lifecycle/{phase}")
def run_plugin_lifecycle_phase(plugin_id: str, phase: str) -> dict[str, Any]:
    """Manually call one declared lifecycle hook for one plugin.

    Lets a person exercise any ``plugin-lifecycle.hooks`` entry from the
    Plugins page instead of waiting for its one real trigger today (a
    workbench self-restart, for ``workbenchShutdown``/``workbenchShutdownAfter``)
    or for a future automatic trigger of the other phases. A ``null``/missing
    hook, an unloaded plugin, or a hook the module does not export is
    reported back as "nothing to call", never silently ignored or a 500.
    """

    item = next((entry for entry in _catalog if entry.get("id") == plugin_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Unknown plugin: {plugin_id}")
    hooks = (item.get("plugin-lifecycle") or {}).get("hooks") or {}
    if phase not in hooks:
        raise HTTPException(status_code=400, detail=f"'{plugin_id}' declares no '{phase}' lifecycle phase")
    module = _modules.get(plugin_id)
    outcome = _call_lifecycle_hook(item, module, phase, reason="manual")
    if outcome is not None:
        return outcome
    hook_name = hooks.get(phase)
    if not hook_name:
        return {"id": plugin_id, "phase": phase, "hook": None, "ok": False, "detail": "No hook is declared for this phase."}
    if module is None:
        return {"id": plugin_id, "phase": phase, "hook": hook_name, "ok": False, "detail": "Plugin is not loaded."}
    return {"id": plugin_id, "phase": phase, "hook": hook_name, "ok": False,
            "detail": f"Plugin does not export a function named '{hook_name}'."}


@router.get("/{plugin_id}/endpoints")
def list_plugin_endpoints(plugin_id: str) -> dict[str, Any]:
    """Enumerate the workbench routes registered under one plugin's prefix.

    The universal ``servicesEndpoint`` fallback for embedded plugins (their
    routers live on this FastAPI app, so this IS their swagger-style list) and
    for standalone plugins it at least names the proxy mounts. Standalone
    servers with a richer native self-description (ws_collab's ``/endpoints``)
    declare that instead.
    """

    item = next((entry for entry in _catalog if entry.get("id") == plugin_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Unknown plugin: {plugin_id}")
    prefix = f"/{plugin_id}"

    def _walk(routes: list[Any], base: str) -> Iterator[tuple[Any, str]]:
        """Yield (route, full_path) pairs, unwrapping lazy router inclusions.

        Newer FastAPI wraps ``include_router`` results in ``_IncludedRouter``
        entries that expose no ``path`` themselves; the real ``APIRoute``
        objects live on ``original_router`` and only carry their local path,
        so the include context's prefix has to be re-applied while walking.
        """

        for route in routes:
            inner = getattr(route, "original_router", None)
            if inner is not None:
                context = getattr(route, "include_context", None)
                sub_prefix = str(getattr(context, "prefix", "") or "")
                yield from _walk(list(getattr(inner, "routes", [])), base + sub_prefix)
                continue
            path = getattr(route, "path", None)
            if isinstance(path, str):
                yield route, base + path

    endpoints: list[dict[str, Any]] = []
    for route, path in _walk(list(_app.routes) if _app is not None else [], ""):
        if path != prefix and not path.startswith(f"{prefix}/"):
            continue
        methods = sorted(getattr(route, "methods", None) or [])
        endpoints.append({
            "path": path,
            "methods": [m for m in methods if m != "HEAD"] or ["*"],
            "name": getattr(route, "name", "") or "",
            "description": (getattr(route, "endpoint", None).__doc__ or "").strip().split("\n")[0]
            if getattr(route, "endpoint", None) else "",
        })
    endpoints.sort(key=lambda entry: entry["path"])
    return {"id": plugin_id, "prefix": prefix, "count": len(endpoints), "endpoints": endpoints}


@router.get("")
def list_plugins() -> dict[str, Any]:
    return {
        "plugins": _scan(register=False),
        "policyPath": str(POLICY_PATH),
        "manifestName": MANIFEST_NAME,
    }


@router.post("/refresh")
def refresh_plugins() -> dict[str, Any]:
    return {
        "plugins": _scan(register=True),
        "policyPath": str(POLICY_PATH),
        "manifestName": MANIFEST_NAME,
    }


@router.put("/{plugin_id}")
def configure_plugin(plugin_id: str, body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    scan_mode = str(body.get("scan") or "")
    if scan_mode not in {"startup", "disabled"}:
        raise HTTPException(status_code=400, detail="scan must be startup or disabled")
    policy = _policy()
    section = policy.setdefault("pluginsFound", {})
    if not isinstance(section, dict):
        section = policy["pluginsFound"] = {}
    entry = section.get(plugin_id) if isinstance(section.get(plugin_id), dict) else {}
    section[plugin_id] = {**entry, "scan": scan_mode}
    write_json_file(POLICY_PATH, policy)
    return {
        "plugins": _scan(register=scan_mode == "startup"),
        "policyPath": str(POLICY_PATH),
        "manifestName": MANIFEST_NAME,
    }
