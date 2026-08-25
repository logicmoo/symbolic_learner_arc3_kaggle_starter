from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, FastAPI, HTTPException

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
from resource_store import get_filesystem_provider


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
        return {"plugins": {}}
    return _read_json(POLICY_PATH)


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


def _scan(*, register: bool) -> list[dict[str, Any]]:
    global _catalog
    policy = _policy().get("plugins", {})
    catalog: list[dict[str, Any]] = []
    resources = get_filesystem_provider()
    manifest_paths = [
        directory / "plugin.json"
        # Plugin manifests are plain configuration, so they are probed with the
        # provider's configuration API: the resource API would resolve a
        # .json path onto a .metta sibling.
        for directory in resources.iterdir(PLUGINS_ROOT)
        if resources.is_dir(directory) and json_file_exists(directory / "plugin.json")
    ]
    for manifest_path in sorted(manifest_paths):
        try:
            manifest = _read_json(manifest_path)
            plugin_id = str(manifest.get("id") or manifest_path.parent.name)
            configured = policy.get(plugin_id, {}) if isinstance(policy, dict) else {}
            scan_mode = str(configured.get("scan", manifest.get("scan", "startup")))
            item = {**manifest, "id": plugin_id, "scan": scan_mode, "path": str(manifest_path.parent), "loaded": plugin_id in _loaded}
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
            if target_id in _init_applied.get(item["id"], set()):
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
                    _init_applied.setdefault(item["id"], set()).add(target_id)
                except Exception as error:  # noqa: BLE001 - reported, never fatal
                    outcome |= {"applied": False, "detail": str(error)}
            results.append(outcome)
        if results:
            _init_results[item["id"]] = results
            item["initCommandResults"] = results


def install_plugins(app: FastAPI) -> None:
    global _app
    _app = app
    _scan(register=True)


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
    plugins = policy.setdefault("plugins", {})
    if not isinstance(plugins, dict):
        plugins = policy["plugins"] = {}
    plugins[plugin_id] = {"scan": scan_mode}
    write_json_file(POLICY_PATH, policy)
    return {
        "plugins": _scan(register=scan_mode == "startup"),
        "policyPath": str(POLICY_PATH),
        "manifestName": MANIFEST_NAME,
    }
