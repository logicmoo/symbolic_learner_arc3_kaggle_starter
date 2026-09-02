from __future__ import annotations

import fnmatch
import importlib.util
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
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
    read_documentation,
    resolve_ui_pages,
    read_json_file,
    write_json_file,
)



PLUGINS_ROOT = Path(__file__).resolve().parents[1] / "plugins"
POLICY_PATH = PLUGINS_ROOT / "plugins.json"
API_PREFIX = "/workbench"
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


# A pluginsFound entry may name the git repository the plugin lives in, so a
# plugin whose directory has not been checked out yet still appears in the
# catalog as "available" and can be cloned into the plugins directory. Only
# these URL shapes are accepted, and clones always run as an argument list
# (never a shell string), so a repo value cannot smuggle in extra git flags.
_ALLOWED_REPO_SCHEMES = ("https://", "http://", "ssh://", "git://", "git@")


def _repo_of(entry: Any) -> dict[str, str]:
    """Extract the optional git coordinates from a pluginsFound entry."""

    if not isinstance(entry, dict):
        return {}
    repo = str(entry.get("repo") or "").strip()
    if not repo:
        return {}
    ref = str(entry.get("ref") or "").strip()
    result = {"repo": repo}
    if ref:
        result["ref"] = ref
    return result


def _repo_is_allowed(repo: str) -> bool:
    return bool(repo) and repo.startswith(_ALLOWED_REPO_SCHEMES)


def _plugin_dir_name(entry: Any, plugin_id: str) -> str:
    """The plugins-root-relative directory a plugin lives in.

    Uses the recorded ``path`` (``emullm/plugin.json`` -> ``emullm``) so the
    clone target matches where discovery expects the manifest, falling back to
    the plugin id.
    """

    if isinstance(entry, dict):
        raw = str(entry.get("path") or "").strip().replace("\\", "/")
        head = raw.split("/", 1)[0] if raw else ""
        if head and head not in (".", ".."):
            return head
    return plugin_id


def _git_clone_command(repo: str, ref: str, target: Path) -> list[str]:
    command = ["git", "clone", "--depth", "1"]
    if ref:
        command += ["--branch", ref]
    command += [repo, str(target)]
    return command


def _missing_declared_plugins(policy_doc: dict[str, Any], seen_ids: set[str]) -> list[dict[str, Any]]:
    """Catalog placeholders for declared-with-a-repo plugins not on disk yet.

    A pluginsFound entry that names a ``repo`` but whose directory/manifest was
    not discovered is surfaced as an ``available`` entry carrying the repo URL,
    the expected directory, and the ``git clone`` command, so the Plugins page
    can offer to check it out instead of the plugin silently not existing.
    """

    root = Path(PLUGINS_ROOT)
    placeholders: list[dict[str, Any]] = []
    for plugin_id, entry in _plugins_found(policy_doc).items():
        if plugin_id in seen_ids:
            continue
        coords = _repo_of(entry)
        if not coords:
            continue
        dir_name = _plugin_dir_name(entry, plugin_id)
        target = root / dir_name
        repo = coords["repo"]
        ref = coords.get("ref", "")
        checked_out = target.exists()
        scan_mode = "disabled" if (isinstance(entry, dict) and entry.get("enabled") is False) else str(
            (entry.get("scan") if isinstance(entry, dict) else "") or "startup"
        )
        placeholders.append({
            "id": plugin_id,
            "label": plugin_id,
            "description": "Declared in plugins.json but not checked out into the plugins directory.",
            "scan": scan_mode,
            "loaded": False,
            "adminAvailable": False,
            "adminPath": f"/{plugin_id}/admin",
            "adminApiPath": f"{API_PREFIX}/{plugin_id}/admin",
            "configPage": "",
            "available": True,
            "checkedOut": checked_out,
            "repo": repo,
            "ref": ref,
            "repoAllowed": _repo_is_allowed(repo),
            "checkoutCommand": " ".join(_git_clone_command(repo, ref, target)),
            "path": str(target),
            "uiPages": [],
            "error": "" if _repo_is_allowed(repo)
            else f"Repo URL is not an allowed git URL: {repo}",
        })
    return placeholders



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
    declared and a path is mirrored beneath ``/workbench``.
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
    which also answer at ``/llm_emul/mailbox/...`` and
    ``/ws_collab/mailbox/...``). When a declared path is not already
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
    elif path.startswith("/workbench/") or path.startswith(("http://", "https://", "ws://", "wss://")):
        # The workbench's core namespace and absolute URLs are never
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
    workbench enumerator ``/workbench/plugins/<id>/endpoints`` for embedded routers.
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
            coords = _repo_of(entry)
            # Effective mode: the pluginsFound entry wins over the manifest;
            # "enabled": false disables regardless of scan mode.
            scan_mode = str(entry.get("scan") or manifest_scan)
            if entry.get("enabled") is False:
                scan_mode = "disabled"
            # Even a checked-out plugin advertises the repo it came from, so the
            # Plugins page can always show its origin.
            item = {**manifest, "id": plugin_id, "scan": scan_mode, "path": str(manifest_path.parent), "loaded": plugin_id in _loaded}
            if coords:
                item["repo"] = coords["repo"]
                item["ref"] = coords.get("ref", "")
            item["available"] = True
            item["checkedOut"] = True
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
                    # Mirror the same routes beneath /workbench so the desktop UI
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
    # Declared-but-not-checked-out plugins (a pluginsFound entry that names a
    # repo but whose directory was not discovered) are surfaced as available
    # placeholders so they can be cloned from the Plugins page.
    catalog.extend(_missing_declared_plugins(policy_doc, set(seen_ids)))
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
    # Peek at the plugin's declared status endpoint first, so the phase both
    # verifies each participating plugin is alive and hands the hook that
    # verdict (a standalone plugin whose server is down may act differently).
    status = _peek_plugin_status(item)
    notice = {**item, "lifecyclePhase": hook_phase, "lifecycleReason": reason, "standalone": standalone,
              "statusPeek": status}
    try:
        detail = getattr(module, hook_name)(notice)
        return {"id": item.get("id"), "phase": hook_phase, "hook": hook_name, "ok": True,
                "status": status,
                "detail": detail if isinstance(detail, str) else ""}
    except Exception as error:  # noqa: BLE001 - reported, never fatal
        return {"id": item.get("id"), "phase": hook_phase, "hook": hook_name, "ok": False,
                "status": status, "detail": str(error)}


# The base this API answers on, used to peek at plugin status endpoints from
# inside lifecycle phases. Overridable for non-default ports/hosts.
_SELF_BASE = os.environ.get("WORKBENCH_SELF_BASE", "http://127.0.0.1:8000")


def _status_probe_address(item: dict[str, Any]) -> str | None:
    """Where to peek for this plugin's liveness.

    Prefers the manifest's resolved ``plugin-api.status`` section; falls back
    to the plugin's own route prefix when that root actually answers (many
    standalone servers serve their status document there).
    """

    sections = item.get("apiSections")
    if not isinstance(sections, dict):
        sections = _resolved_api_sections(str(item.get("id") or ""), item)
    status = sections.get("status") if isinstance(sections, dict) else None
    if isinstance(status, dict) and status.get("address"):
        return str(status["address"])
    prefix = f"/{item.get('id')}"
    if _route_is_registered(prefix):
        return prefix
    return None


def _peek_plugin_status(item: dict[str, Any]) -> dict[str, Any]:
    """Peek at one plugin's status endpoint and report whether it is alive.

    ``alive`` is ``True`` when the endpoint answered with any non-5xx status
    (the process behind it is up, even if the exact path is a 404), ``False``
    when the request failed or answered 5xx (a proxied mount whose standalone
    server is down surfaces here as a 502), and ``None`` when the plugin
    declares no status surface at all. Never raises: lifecycle phases must
    proceed no matter how broken one plugin's server is.
    """

    address = _status_probe_address(item)
    if not address:
        return {"alive": None, "address": None, "detail": "no status endpoint declared"}
    url = address if address.startswith(("http://", "https://")) else f"{_SELF_BASE}{address}"
    try:
        # 8s: status pages that live-probe their own upstreams (web_proxy's
        # admin document) legitimately take several seconds; dead servers
        # still fail fast with connection-refused.
        with urllib.request.urlopen(url, timeout=8) as response:  # noqa: S310 - local liveness probe
            code = int(response.getcode() or 0)
        return {"alive": True, "address": address, "detail": f"HTTP {code}"}
    except urllib.error.HTTPError as error:
        return {"alive": error.code < 500, "address": address, "detail": f"HTTP {error.code}"}
    except Exception as error:  # noqa: BLE001 - connection refused, timeout, DNS...
        return {"alive": False, "address": address, "detail": str(error)}


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


DOCUMENT_NAMES = ("ADMIN.md", "SETUP.md", "README.md")


def _plugin_doc_source(item: dict[str, Any]) -> str:
    """Return the filename of the doc that ``read_documentation`` would use, or ""."""

    directory = Path(str(item.get("path") or ""))
    declared = str((item.get("admin") or {}).get("docs") or item.get("docs") or "").strip()
    for name in ((declared,) if declared else ()) + DOCUMENT_NAMES:
        if name and (directory / name).is_file():
            return name
    return ""


def _generate_plugin_documentation(item: dict[str, Any]) -> str:
    """Build a manifest-backed help document for a plugin that ships no .md.

    It describes how to use the admin page: the configure/admin pages the
    plugin contributes, its route prefix, and its declared setup so the right
    Documentation panel is never empty for a plugin.
    """

    label = str(item.get("label") or item.get("id") or "Plugin")
    description = str(item.get("description") or "").strip()
    summary = str(item.get("summary") or "").strip()
    route_prefix = str(item.get("routePrefix") or "").strip()
    admin_path = str(item.get("adminPath") or "").strip()
    config_page = str(item.get("configPage") or "").strip()
    pages = item.get("uiPages") if isinstance(item.get("uiPages"), list) else []

    lines: list[str] = [f"# {label}", ""]
    lines.append(
        "> Auto-generated help. This plugin does not ship a documentation file "
        "yet, so this page is built from its manifest. Add an `ADMIN.md` "
        "(or point `docs` in `plugin.json` at a Markdown file) to replace it."
    )
    lines.append("")
    if summary or description:
        lines.append(summary or description)
        lines.append("")

    lines.append("## Admin pages")
    lines.append("")
    if pages:
        lines.append("This plugin contributes the following pages to the workbench:")
        lines.append("")
        for page in pages:
            if not isinstance(page, dict):
                continue
            page_label = str(page.get("label") or page.get("id") or "page")
            kind = str(page.get("kind") or "").strip()
            descriptor = str(page.get("descriptor") or page.get("address") or "").strip()
            suffix = f" — `{descriptor}`" if descriptor else ""
            kind_note = f" _({kind})_" if kind else ""
            lines.append(f"- **{page_label}**{kind_note}{suffix}")
        lines.append("")
    else:
        lines.append(
            "This plugin exposes a single administration page rendered from its "
            "manifest. Use it to review status, edit settings, and run the "
            "declared maintenance actions."
        )
        lines.append("")

    lines.append("## How to use it")
    lines.append("")
    lines.append(
        "1. Open the plugin's page from the left navigation (under **PLUGINS**)."
    )
    lines.append(
        "2. Review the status rows at the top for readiness and configuration state."
    )
    lines.append(
        "3. Edit any settings fields and save; use the maintenance actions "
        "(for example **Initialize plugin**) to (re)apply setup without a restart."
    )
    lines.append("")

    if route_prefix or admin_path or config_page:
        lines.append("## Endpoints")
        lines.append("")
        if route_prefix:
            lines.append(f"- Route prefix: `{route_prefix}`")
        if admin_path:
            lines.append(f"- Admin descriptor: `{admin_path}` (mirrored under `/workbench{admin_path}`)")
        if config_page:
            lines.append(f"- Configure page: `{config_page}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


@router.get("/{plugin_id}/documentation")
def plugin_documentation(plugin_id: str) -> dict[str, Any]:
    """Return one plugin's documentation Markdown for the workbench doc panel.

    Serves the Markdown file the plugin points at via ``docs`` in ``plugin.json``
    (falling back to ``ADMIN.md`` / ``SETUP.md`` / ``README.md``). A plugin that
    ships no documentation file gets a manifest-generated page describing how to
    use its admin page, so the right-hand Documentation area is never empty.
    """

    item = next((entry for entry in _scan(register=False) if entry.get("id") == plugin_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Unknown plugin: {plugin_id}")
    try:
        content = read_documentation(item)
    except (OSError, ValueError):
        content = ""
    source = _plugin_doc_source(item)
    generated = not content.strip()
    if generated:
        content = _generate_plugin_documentation(item)
        source = "generated"
    return {
        "pluginId": plugin_id,
        "title": str(item.get("label") or plugin_id),
        "content": content,
        "source": source,
        "generated": generated,
    }


@router.get("")
def list_plugins() -> dict[str, Any]:
    return {
        "plugins": _scan(register=False),
        "policyPath": str(POLICY_PATH),
        "manifestName": MANIFEST_NAME,
    }


def _assess_plugin(item: dict[str, Any]) -> dict[str, Any]:
    """Compare where one plugin SHOULD be against where it actually is.

    Expected state comes from its scan policy: a startup plugin should have
    completed the workbenchStartup phase and (if it has a status surface) be
    answering on it; a disabled plugin should not be loaded at all. Actual
    state is the loaded flag, the live status peek, and the initialization
    report. The verdict names the first mismatch, or "as expected".
    """

    scan = str(item.get("scan") or "startup")
    should_load = scan == "startup"
    expected = {
        "loaded": should_load,
        "phase": "workbenchStartupAfter" if should_load else "not loaded",
        "reason": f"scan={scan}",
    }
    loaded = bool(item.get("loaded"))
    status = _peek_plugin_status(item) if loaded else {"alive": None, "address": _status_probe_address(item), "detail": "not probed (plugin not loaded)"}
    initialization = item.get("initialization") if isinstance(item.get("initialization"), dict) else {}
    ready = bool(initialization.get("ready", True))
    unmet = [
        f"{check.get('kind')}:{check.get('name')}"
        for check in (initialization.get("checks") or [])
        if isinstance(check, dict) and not check.get("satisfied")
    ]
    error = str(item.get("error") or "")
    if not should_load:
        verdict = "disabled-but-loaded" if loaded else "as expected"
        phase = "loaded (should be stopped)" if loaded else "not loaded"
    elif not loaded:
        verdict = "should-be-loaded"
        phase = "not loaded"
    elif status.get("alive") is False:
        verdict = "loaded-but-server-dead"
        phase = "workbenchStartupAfter (server unreachable)"
    elif not ready:
        verdict = "running-with-unmet-requirements"
        phase = "workbenchStartupAfter"
    else:
        verdict = "as expected"
        phase = "workbenchStartupAfter" + ("" if status.get("alive") else " (no status surface to verify)")
    return {
        "id": item.get("id"),
        "label": item.get("label") or item.get("id"),
        "expected": expected,
        "actual": {
            "loaded": loaded,
            "phase": phase,
            "alive": status.get("alive"),
            "statusAddress": status.get("address"),
            "statusDetail": status.get("detail"),
            "initializationReady": ready,
            "unmetChecks": unmet,
            "error": error,
        },
        "ok": verdict == "as expected",
        "verdict": verdict,
    }


@router.get("/assessment")
def assess_plugins() -> dict[str, Any]:
    """Assess every plugin: expected phase/state versus what is actually running.

    Peeks at each loaded plugin's status endpoint, so this is heavier than
    the catalog listing — call it on demand, not on a poll.
    """

    catalog = _scan(register=False)
    assessments = [_assess_plugin(item) for item in catalog]
    return {
        "assessments": assessments,
        "okCount": sum(1 for entry in assessments if entry["ok"]),
        "total": len(assessments),
    }


@router.post("/refresh")
def refresh_plugins() -> dict[str, Any]:
    return {
        "plugins": _scan(register=True),
        "policyPath": str(POLICY_PATH),
        "manifestName": MANIFEST_NAME,
    }


@router.post("/{plugin_id}/checkout")
def checkout_plugin(plugin_id: str, body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    """Clone a declared-but-missing plugin's git repository into the plugins directory.

    The repo URL comes from the plugin's ``pluginsFound`` entry in
    ``plugins.json`` (a ``ref`` there, or in the request body, selects a
    branch/tag). The clone target is the directory discovery expects the
    manifest in, so a successful checkout is picked up by the following scan.
    The command runs as an argument list, never a shell string, and only
    allowed git URL schemes are accepted, so a repo value cannot inject extra
    flags or shell.
    """

    policy = _policy()
    entry = _plugins_found(policy).get(plugin_id)
    coords = _repo_of(entry)
    if not coords:
        raise HTTPException(status_code=400, detail=f"'{plugin_id}' has no 'repo' declared in plugins.json")
    repo = coords["repo"]
    if not _repo_is_allowed(repo):
        raise HTTPException(status_code=400, detail=f"Repo URL is not an allowed git URL: {repo}")
    ref = str(body.get("ref") or coords.get("ref") or "").strip()

    if shutil.which("git") is None:
        raise HTTPException(status_code=500, detail="git was not found on PATH")

    root = Path(PLUGINS_ROOT)
    target = root / _plugin_dir_name(entry, plugin_id)
    try:
        target.relative_to(root)
    except ValueError:
        raise HTTPException(status_code=400, detail="Refusing to check out outside the plugins directory")
    if target.exists() and any(target.iterdir()):
        raise HTTPException(status_code=409, detail=f"Target already exists and is not empty: {target}")

    command = _git_clone_command(repo, ref, target)
    try:
        result = subprocess.run(  # noqa: S603 - git executable, argument list, no shell
            command,
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(root),
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise HTTPException(status_code=500, detail=f"git clone failed to launch: {error}") from error
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "git clone failed").strip()[-2000:]
        raise HTTPException(status_code=500, detail=f"git clone failed: {detail}")

    checkout = {
        "id": plugin_id,
        "repo": repo,
        "ref": ref,
        "target": str(target),
        "command": " ".join(command),
        "ok": True,
    }
    return {
        "plugins": _scan(register=True),
        "policyPath": str(POLICY_PATH),
        "manifestName": MANIFEST_NAME,
        "checkout": checkout,
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
