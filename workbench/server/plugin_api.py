from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, FastAPI, HTTPException

from resource_store import get_filesystem_provider


PLUGINS_ROOT = Path(__file__).resolve().parents[1] / "plugins"
POLICY_PATH = PLUGINS_ROOT / "plugins.json"
router = APIRouter(prefix="/plugins", tags=["plugins"])
_app: FastAPI | None = None
_loaded: set[str] = set()
_catalog: list[dict[str, Any]] = []


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(get_filesystem_provider().read_text(path, encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid plugin JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Plugin JSON must contain an object: {path}")
    return value


def _policy() -> dict[str, Any]:
    if not get_filesystem_provider().is_file(POLICY_PATH):
        return {"plugins": {}}
    return _read_json(POLICY_PATH)


def _scan(*, register: bool) -> list[dict[str, Any]]:
    global _catalog
    policy = _policy().get("plugins", {})
    catalog: list[dict[str, Any]] = []
    resources = get_filesystem_provider()
    manifest_paths = [
        directory / "plugin.json"
        for directory in resources.iterdir(PLUGINS_ROOT)
        if resources.is_dir(directory) and resources.is_file(directory / "plugin.json")
    ]
    for manifest_path in sorted(manifest_paths):
        try:
            manifest = _read_json(manifest_path)
            plugin_id = str(manifest.get("id") or manifest_path.parent.name)
            configured = policy.get(plugin_id, {}) if isinstance(policy, dict) else {}
            scan_mode = str(configured.get("scan", manifest.get("scan", "startup")))
            item = {**manifest, "id": plugin_id, "scan": scan_mode, "path": str(manifest_path.parent), "loaded": plugin_id in _loaded}
            if register and scan_mode == "startup" and plugin_id not in _loaded:
                entrypoint = manifest_path.parent / str(manifest.get("entrypoint") or "plugin.py")
                spec = importlib.util.spec_from_file_location(f"workbench_plugin_{plugin_id}", entrypoint)
                if spec is None or spec.loader is None:
                    raise ValueError(f"Cannot load plugin entrypoint: {entrypoint}")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if _app is None or not hasattr(module, "create_router"):
                    raise ValueError("Plugin must export create_router(manifest)")
                _app.include_router(module.create_router(manifest))
                _loaded.add(plugin_id)
                item["loaded"] = True
            catalog.append(item)
        except Exception as error:
            catalog.append({"id": manifest_path.parent.name, "label": manifest_path.parent.name, "scan": "disabled", "loaded": False, "error": str(error), "path": str(manifest_path.parent)})
    _catalog = catalog
    return catalog


def install_plugins(app: FastAPI) -> None:
    global _app
    _app = app
    _scan(register=True)


@router.get("")
def list_plugins() -> dict[str, Any]:
    return {"plugins": _scan(register=False), "policyPath": str(POLICY_PATH)}


@router.post("/refresh")
def refresh_plugins() -> dict[str, Any]:
    return {"plugins": _scan(register=True), "policyPath": str(POLICY_PATH)}


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
    resources = get_filesystem_provider()
    resources.make_directory(POLICY_PATH.parent)
    resources.write_text(POLICY_PATH, json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    return {"plugins": _scan(register=scan_mode == "startup"), "policyPath": str(POLICY_PATH)}
