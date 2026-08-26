"""Shared administration/setup contract for workbench plugins.

Everything a plugin declares lives in its ``plugin.json``. The plugin scanner
reads that manifest from disk without importing or calling the plugin, so the
Plugins page can build the configure link, the desktop pages, and the
initialization report from the filesystem alone:

```json
{
  "configPage": "http://127.0.0.1:5173/ws_collab/admin",
  "path": "/web_proxy/admin",
  "docs": "ADMIN.md",
  "plugin-install": { "requires": ["httpx"], "install": "...", "steps": [...] },
  "plugin-init": [{ "command": "web_proxy", "path": "/ws_collab", "redirect": "..." }],
  "ui": { "pages": [{ "id": "configure", "kind": "configure", "descriptor": "..." }] }
}
```

A plugin declares its configure page in one of two ways:

* ``configPage`` — an absolute URL to a page the plugin serves itself. The
  workbench embeds it, so the plugin owns the markup.
* ``path`` — an API path serving an administration *descriptor*. The descriptor
  is data, not markup, and the workbench renders it natively so the page matches
  the rest of the application.

The declared ``path`` is served by the plugin's own router on the workbench API
port, together with the rest of the administration contract:

``GET  <path>``                  administration descriptor (JSON)
``PUT  <path>/settings``         persist edited settings
``POST <path>/initialize``       run initialization again
``POST <path>/actions/{action}`` run a declared maintenance action

A plugin that declares neither and builds no administration router receives the
generic manifest-backed page, so no plugin is ever left without one.
"""

from __future__ import annotations

import importlib.util
import json
from collections.abc import Awaitable, Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException

from resource_store import get_filesystem_provider


FIELD_TYPES = {"text", "textarea", "number", "boolean", "select", "stringList", "readonly"}
STATUS_TONES = {"ok", "warn", "error", "neutral"}
DOCUMENT_NAMES = ("ADMIN.md", "SETUP.md", "README.md")
MANIFEST_NAME = "plugin.json"
INSTALL_KEYS = ("plugin-install", "install")
INIT_KEY = "plugin-init"
CONFIGURE_KINDS = {"configure", "admin"}

DescribeAdmin = Callable[[], Awaitable[dict[str, Any]] | dict[str, Any]]
ApplySettings = Callable[[dict[str, Any]], Awaitable[dict[str, Any]] | dict[str, Any]]
RunAction = Callable[[dict[str, Any]], Awaitable[dict[str, Any]] | dict[str, Any]]


def admin_prefix(manifest: Mapping[str, Any]) -> str:
    """Return the route prefix that hosts this plugin's administration page."""

    prefix = str(manifest.get("routePrefix") or f"/plugins/{manifest.get('id') or 'plugin'}")
    return "/" + prefix.strip("/")


def admin_path(manifest: Mapping[str, Any]) -> str:
    return read_admin_manifest(manifest)["path"]


def _install_block(manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return the install declaration, accepting either accepted key name."""

    for key in INSTALL_KEYS:
        block = manifest.get(key)
        if isinstance(block, Mapping):
            return block
    return {}


def _normalized_install(declared: Mapping[str, Any], base_path: str) -> dict[str, Any]:
    return {
        "requires": [str(item) for item in declared.get("requires", []) if str(item).strip()],
        "files": [dict(item) for item in declared.get("files", []) if isinstance(item, Mapping)],
        "steps": [str(item) for item in declared.get("steps", []) if str(item).strip()],
        "install": str(declared.get("install") or ""),
        "path": f"{base_path}/initialize",
    }


def read_init_commands(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return the ``plugin-init`` commands this plugin asks other plugins to run."""

    declared = manifest.get(INIT_KEY)
    if not isinstance(declared, Sequence) or isinstance(declared, (str, bytes)):
        return []
    commands: list[dict[str, Any]] = []
    for entry in declared:
        if not isinstance(entry, Mapping):
            continue
        command = str(entry.get("command") or "").strip()
        if not command:
            continue
        commands.append({**dict(entry), "command": command, "requestedBy": str(manifest.get("id") or "")})
    return commands


def read_admin_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Read the administration declaration out of a plugin's ``plugin.json``.

    The scanner calls this without importing the plugin, so the Plugins page can
    build the configure link straight from the filesystem. ``configPage`` names
    an absolute URL the plugin serves itself; ``path`` names an API path serving
    an administration descriptor. Anything absent falls back to the default
    ``<routePrefix>/admin`` descriptor link.
    """

    label = str(manifest.get("label") or manifest.get("id") or "Plugin")
    default_path = f"{admin_prefix(manifest)}/admin"
    # ``path`` is overwritten by the loader with the plugin directory, so the
    # declared descriptor path is carried separately and a directory-shaped
    # value is ignored here.
    raw_path = str(manifest.get("adminPage") or manifest.get("declaredPath") or "")
    if not raw_path and str(manifest.get("path") or "").startswith("/"):
        raw_path = str(manifest["path"])
    path = raw_path or default_path
    if not path.startswith("/"):
        path = f"{admin_prefix(manifest)}/{path.lstrip('/')}"
    config_page = str(manifest.get("configPage") or "").strip()
    install = _install_block(manifest)
    declared = bool(
        config_page
        or raw_path
        or install
        or manifest.get("ui")
        or manifest.get(INIT_KEY)
    )
    return {
        "label": str(manifest.get("adminLabel") or f"{label} administration and setup"),
        "summary": str(manifest.get("summary") or manifest.get("description") or ""),
        "path": path,
        "configPage": config_page,
        "docs": str(manifest.get("docs") or ""),
        "kind": str(manifest.get("kind") or ("custom" if declared else "generic")),
        "declared": declared,
        "init": _normalized_install(install, path),
        "initCommands": read_init_commands(manifest),
        "ui": {"pages": normalized_ui_pages(manifest.get("ui"), manifest, config_page or path)},
    }


def initialization_report(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Check a plugin's declared initialization requirements from disk only.

    The scanner runs this before importing anything, so a plugin that cannot be
    initialized explains itself on the Plugins page instead of only failing with
    an import traceback.
    """

    declaration = read_admin_manifest(manifest)
    init = declaration.get("init") or {}
    directory = plugin_directory(manifest)
    checks: list[dict[str, Any]] = []
    for module_name in init.get("requires", []):
        try:
            found = importlib.util.find_spec(module_name) is not None
        except (ImportError, ValueError):
            found = False
        checks.append({
            "kind": "module",
            "name": module_name,
            "satisfied": found,
            "detail": "" if found else f"Python module '{module_name}' is not importable.",
        })
    for entry in init.get("files", []):
        name = str(entry.get("path") or "").strip()
        if not name:
            continue
        exists = json_file_exists(directory / name)
        checks.append({
            "kind": "file",
            "name": name,
            "satisfied": exists,
            "detail": "" if exists else str(entry.get("description") or f"{name} is missing."),
        })
    missing = [check for check in checks if not check["satisfied"]]
    return {
        "ready": not missing,
        "checks": checks,
        "steps": init.get("steps", []),
        "install": init.get("install", ""),
        "initializePath": init.get("path", f"{declaration['path']}/initialize"),
    }


def plugin_directory(manifest: Mapping[str, Any]) -> Path:
    path = manifest.get("path")
    if not path:
        raise ValueError("Plugin manifest is missing its resolved 'path'")
    return Path(str(path))


def read_json_file(path: Path) -> Any:
    """Read a plugin JSON file as plain configuration.

    Plugin manifests are plain JSON configuration, not workspace MeTTa
    resources, so they use the provider's configuration API: the resource API
    redirects every ``.json`` path to a ``.metta`` sibling.
    """

    return get_filesystem_provider().read_config_json(path)


def write_json_file(path: Path, value: Any) -> None:
    """Write a plugin JSON file as plain configuration, for the same reason."""

    get_filesystem_provider().write_config_json(path, value)


def json_file_exists(path: Path) -> bool:
    """Report whether a plugin JSON file exists, ignoring MeTTa mirrors."""

    return get_filesystem_provider().config_file_exists(path)


def manifest_path(manifest: Mapping[str, Any]) -> Path:
    return plugin_directory(manifest) / "plugin.json"


def status(label: str, value: Any, tone: str = "neutral", *, detail: str = "") -> dict[str, Any]:
    if tone not in STATUS_TONES:
        raise ValueError(f"Unknown status tone: {tone}")
    return {"label": label, "value": "" if value is None else str(value), "tone": tone, "detail": detail}


def field(
    identifier: str,
    label: str,
    kind: str,
    value: Any,
    *,
    help_text: str = "",
    placeholder: str = "",
    options: Sequence[Any] = (),
) -> dict[str, Any]:
    if kind not in FIELD_TYPES:
        raise ValueError(f"Unknown administration field type: {kind}")
    return {
        "id": identifier,
        "label": label,
        "type": kind,
        "value": value,
        "help": help_text,
        "placeholder": placeholder,
        "options": [str(option) for option in options],
    }


def section(
    identifier: str,
    title: str,
    fields: Sequence[Mapping[str, Any]],
    *,
    description: str = "",
) -> dict[str, Any]:
    return {"id": identifier, "title": title, "description": description, "fields": list(fields)}


def action(identifier: str, label: str, *, description: str = "", tone: str = "neutral") -> dict[str, Any]:
    return {"id": identifier, "label": label, "description": description, "tone": tone}


def read_documentation(manifest: Mapping[str, Any], names: Iterable[str] | None = None) -> str:
    """Return the first administration document that exists beside the plugin.

    A plugin that names a ``docs`` file in its ``admin.json`` gets that file
    first; otherwise the shared ``ADMIN.md`` / ``SETUP.md`` / ``README.md``
    order applies.
    """

    resources = get_filesystem_provider()
    directory = plugin_directory(manifest)
    if names is None:
        declared = str(read_admin_manifest(manifest).get("docs") or "").strip()
        names = ((declared,) if declared else ()) + DOCUMENT_NAMES
    for name in names:
        candidate = directory / name
        if resources.is_file(candidate):
            try:
                return resources.read_text(candidate, encoding="utf-8-sig")
            except OSError:
                continue
    return ""


def descriptor(
    manifest: Mapping[str, Any],
    *,
    title: str = "",
    summary: str = "",
    kind: str = "custom",
    status_items: Sequence[Mapping[str, Any]] = (),
    sections: Sequence[Mapping[str, Any]] = (),
    actions: Sequence[Mapping[str, Any]] = (),
    documentation: str | None = None,
) -> dict[str, Any]:
    declaration = read_admin_manifest(manifest)
    label = str(manifest.get("label") or manifest.get("id") or "Plugin")
    return {
        "pluginId": str(manifest.get("id") or ""),
        "title": title or str(declaration.get("label") or f"{label} administration"),
        "summary": summary or str(declaration.get("summary") or manifest.get("description") or ""),
        "kind": kind,
        "adminPath": declaration["path"],
        "configPage": declaration.get("configPage", ""),
        "declaredOnDisk": bool(declaration.get("declared")),
        "manifestPath": str(manifest_path(manifest)),
        "settingsPath": str(manifest_path(manifest)),
        "initialization": initialization_report(manifest),
        "uiPages": list(declaration.get("ui", {}).get("pages", [])),
        "status": list(status_items),
        "sections": list(sections),
        "actions": list(actions),
        "documentation": read_documentation(manifest) if documentation is None else documentation,
    }


def write_manifest_values(manifest: Mapping[str, Any], values: Mapping[str, Any]) -> dict[str, Any]:
    """Persist ``values`` into the plugin's ``plugin.json`` and return the merged manifest."""

    target = manifest_path(manifest)
    try:
        stored = read_json_file(target)
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=500, detail=f"Cannot read {target}: {error}") from error
    if not isinstance(stored, dict):
        raise HTTPException(status_code=500, detail=f"Plugin manifest must be an object: {target}")
    stored.update({key: value for key, value in values.items()})
    write_json_file(target, stored)
    return stored


def string_list(value: Any) -> list[str]:
    """Coerce a textarea, list, or delimited string into a clean list of strings."""

    if isinstance(value, str):
        candidates = value.replace(",", "\n").splitlines()
    elif isinstance(value, (list, tuple)):
        candidates = [str(item) for item in value]
    elif value is None:
        candidates = []
    else:
        candidates = [str(value)]
    return [item.strip() for item in candidates if item.strip()]


async def _resolve(result: Any) -> Any:
    if hasattr(result, "__await__"):
        return await result
    return result


def attach_admin_routes(
    router: APIRouter,
    manifest: Mapping[str, Any],
    *,
    describe: DescribeAdmin,
    apply_settings: ApplySettings | None = None,
    actions: Mapping[str, RunAction] | None = None,
    initialize: RunAction | None = None,
) -> APIRouter:
    """Mount the standard administration endpoints for a plugin onto ``router``.

    The base path comes from the plugin's on-disk ``admin.json`` so the routes
    served on the API port always match the link the scanner published.
    """

    base = read_admin_manifest(manifest)["path"]
    runners = dict(actions or {})

    @router.get(base, tags=["plugin-admin"])
    async def read_admin() -> dict[str, Any]:
        return await _resolve(describe())

    @router.put(f"{base}/settings", tags=["plugin-admin"])
    async def write_admin(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        if apply_settings is None:
            raise HTTPException(status_code=400, detail="This plugin has no editable settings")
        values = body.get("values") if isinstance(body.get("values"), dict) else body
        await _resolve(apply_settings(dict(values)))
        return await _resolve(describe())

    @router.post(f"{base}/initialize", tags=["plugin-admin"])
    async def initialize_plugin(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        runner = initialize or (lambda payload: ensure_declared_files(manifest))
        outcome = await _resolve(runner(dict(body)))
        payload = await _resolve(describe())
        if isinstance(outcome, dict):
            payload = {**payload, "actionResult": outcome}
        return payload

    @router.post(f"{base}/actions/{{action_id}}", tags=["plugin-admin"])
    async def run_admin_action(
        action_id: str, body: dict[str, Any] = Body(default_factory=dict)
    ) -> dict[str, Any]:
        runner = runners.get(action_id)
        if runner is None:
            raise HTTPException(status_code=404, detail=f"Unknown administration action: {action_id}")
        outcome = await _resolve(runner(dict(body)))
        payload = await _resolve(describe())
        if isinstance(outcome, dict):
            payload = {**payload, "actionResult": outcome}
        return payload

    return router


def ensure_declared_files(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Create any declared initialization files that are missing, then re-check."""

    declaration = read_admin_manifest(manifest)
    resources = get_filesystem_provider()
    directory = plugin_directory(manifest)
    created: list[str] = []
    for entry in (declaration.get("init") or {}).get("files", []):
        name = str(entry.get("path") or "").strip()
        if not name or json_file_exists(directory / name):
            continue
        template = entry.get("template")
        if isinstance(template, str):
            resources.make_directory((directory / name).parent)
            resources.write_text(directory / name, template, encoding="utf-8")
        else:
            write_json_file(directory / name, template or {})
        created.append(name)
    report = initialization_report(manifest)
    return {"created": created, "ready": report["ready"], "checks": report["checks"]}


def default_ui_pages(manifest: Mapping[str, Any], admin_link: str) -> list[dict[str, Any]]:
    """Every plugin contributes at least a configure page to the desktop UI."""

    label = str(manifest.get("label") or manifest.get("id") or "Plugin")
    return [{
        "id": "configure",
        "label": f"Configure {label}",
        "kind": "configure",
        "descriptor": admin_link,
        "external": admin_link.startswith(("http://", "https://")),
        "glyph": "⚙",
        "group": "PLUGINS",
        "declared": False,
    }]


def normalized_ui_pages(declared: Any, manifest: Mapping[str, Any], admin_link: str) -> list[dict[str, Any]]:
    """Normalize the ``ui.pages`` a plugin declares, guaranteeing a configure page.

    A ``descriptor`` that is an absolute URL is a page the plugin renders itself
    and the workbench embeds. A path is an administration descriptor the
    workbench renders natively.
    """

    block = declared if isinstance(declared, Mapping) else {}
    entries = block.get("pages") if isinstance(block.get("pages"), Sequence) else []
    pages: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        descriptor_path = str(entry.get("descriptor") or admin_link)
        external = bool(entry.get("external")) or descriptor_path.startswith(("http://", "https://"))
        if not external and not descriptor_path.startswith("/"):
            descriptor_path = f"{admin_prefix(manifest)}/{descriptor_path.lstrip('/')}"
        pages.append({
            "id": str(entry.get("id") or "page"),
            "label": str(entry.get("label") or manifest.get("label") or manifest.get("id") or "Plugin"),
            "kind": str(entry.get("kind") or "page"),
            "descriptor": descriptor_path,
            "external": external,
            "glyph": str(entry.get("glyph") or "⬡"),
            "group": str(entry.get("group") or "PLUGINS"),
            "declared": True,
        })
    if not any(page["kind"] in CONFIGURE_KINDS for page in pages):
        pages = default_ui_pages(manifest, admin_link) + pages
    return pages



def build_admin_router(
    manifest: Mapping[str, Any],
    *,
    describe: DescribeAdmin,
    apply_settings: ApplySettings | None = None,
    actions: Mapping[str, RunAction] | None = None,
    initialize: RunAction | None = None,
) -> APIRouter:
    """Build a standalone administration router for a plugin.

    The loader mounts the returned router twice: once bare, so the plugin owns
    its declared link on the API port, and once beneath ``/api`` so the desktop
    UI reaches every plugin's configure page through one proxied namespace.
    """

    return attach_admin_routes(
        APIRouter(),
        manifest,
        describe=describe,
        apply_settings=apply_settings,
        actions=actions,
        initialize=initialize,
    )


def resolve_ui_pages(
    manifest: Mapping[str, Any],
    pages: Sequence[Mapping[str, Any]],
    *,
    api_prefix: str = "/api",
) -> list[dict[str, Any]]:
    """Resolve declared ``ui.pages`` to addresses the desktop UI can open.

    This is the default resolution, used when a plugin exports no
    ``resolve_ui_pages`` of its own:

    * an absolute ``descriptor`` is a page the plugin serves itself, so it is
      opened as declared and embedded;
    * a path is an administration descriptor, mirrored beneath ``api_prefix``
      so one proxied namespace serves every plugin configure page.

    A plugin that knows better — because it runs standalone on another port, or
    serves its pages from a different base — exports ``resolve_ui_pages`` and
    returns the same shape with ``address`` filled in.
    """

    config_page = str(manifest.get("configPage") or "").strip()
    resolved: list[dict[str, Any]] = []
    for page in pages:
        descriptor = str(page.get("descriptor") or "")
        external = bool(page.get("external")) or descriptor.startswith(("http://", "https://"))
        if external:
            address = descriptor
        elif config_page and page.get("kind") in CONFIGURE_KINDS:
            address = config_page
            external = True
        else:
            address = f"{api_prefix}{descriptor}"
        resolved.append({**dict(page), "external": external, "address": address})
    return resolved


def has_admin_route(router: APIRouter, manifest: Mapping[str, Any]) -> bool:
    target = admin_path(manifest)
    return any(getattr(route, "path", None) == target for route in router.routes)


def generic_admin_router(manifest: Mapping[str, Any]) -> APIRouter:
    """Build the fallback administration page for a plugin that declares none."""

    router = APIRouter()
    plugin_id = str(manifest.get("id") or "")

    def current_manifest() -> dict[str, Any]:
        target = manifest_path(manifest)
        try:
            stored = read_json_file(target)
        except (OSError, json.JSONDecodeError):
            return dict(manifest)
        return {**dict(manifest), **stored} if isinstance(stored, dict) else dict(manifest)

    def describe() -> dict[str, Any]:
        stored = current_manifest()
        targets = [str(item) for item in stored.get("allowedTargets", []) if isinstance(item, str)]
        status_items = [
            status("Plugin", plugin_id, "neutral"),
            status("Version", stored.get("version") or "unversioned", "neutral"),
            status("Route prefix", admin_prefix(manifest), "neutral"),
            status("Entrypoint", stored.get("entrypoint") or "plugin.py", "neutral"),
            status("Administration", "Generic manifest page", "warn",
                   detail="This plugin does not publish its own administration router, so the "
                          "workbench serves the shared manifest-backed setup page."),
        ]
        sections = [
            section(
                "identity",
                "Identity",
                [
                    field("label", "Display label", "text", stored.get("label") or plugin_id,
                          help_text="Name shown on the Plugins page."),
                    field("description", "Description", "textarea", stored.get("description") or "",
                          help_text="Short summary shown on the plugin card."),
                    field("version", "Version", "text", stored.get("version") or "",
                          placeholder="1.0.0"),
                ],
                description="Manifest identity stored in plugin.json.",
            ),
            section(
                "routing",
                "Routing and access",
                [
                    field("routePrefix", "Route prefix", "text", stored.get("routePrefix") or "",
                          help_text="Path this plugin serves on the workbench API port.",
                          placeholder="/my-plugin"),
                    field("allowedTargets", "Allowed targets", "stringList", targets,
                          help_text="One target per line. Empty means the plugin declares no outbound allowlist."),
                ],
                description="Where this plugin is reachable and what it is allowed to reach.",
            ),
        ]
        return descriptor(
            manifest,
            kind="generic",
            summary=str(stored.get("description") or "")
            or "Shared setup page generated from this plugin's manifest.",
            status_items=status_items,
            sections=sections,
        )

    def apply_settings(values: Mapping[str, Any]) -> dict[str, Any]:
        updates: dict[str, Any] = {}
        for key in ("label", "description", "version", "routePrefix"):
            if key in values:
                updates[key] = str(values[key] or "").strip()
        if "allowedTargets" in values:
            updates["allowedTargets"] = string_list(values["allowedTargets"])
        return write_manifest_values(manifest, updates)

    return attach_admin_routes(router, manifest, describe=describe, apply_settings=apply_settings)
