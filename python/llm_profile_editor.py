from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from llm_batch_profiles import (
    BatchProfile,
    DEFAULT_BATCH_CONFIG,
    _install_sampling_parameters,
    _profile_environment,
    _profile_state,
    _restore_selected_provider,
    _temporary_environment,
)
from llm_readme_patch import transcript_is_restorable
from llm_transcripts import list_transcripts


@dataclass
class EditorResult:
    run: bool = False
    saved: bool = False


def _provider_config_path(runner: Any) -> Path:
    return Path(runner.llm_router().config_path).resolve()


def _read_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"LLM configuration must be one JSON object: {path}")
    providers = raw.get("llm_providers")
    if not isinstance(providers, list):
        raise ValueError(f"LLM configuration has no llm_providers list: {path}")
    return raw


def _profile_from_nested(provider_id: str, raw: dict[str, Any]) -> BatchProfile:
    item = dict(raw)
    item["provider_id"] = provider_id
    return BatchProfile.from_mapping(item)


def load_unified_profiles(path: Path) -> list[BatchProfile]:
    raw = _read_json(path)
    profiles: list[BatchProfile] = []
    for provider in raw["llm_providers"]:
        if not isinstance(provider, dict):
            continue
        provider_id = str(provider.get("id") or "").strip()
        for item in provider.get("run_profiles") or []:
            if isinstance(item, dict):
                profiles.append(_profile_from_nested(provider_id, item))
    return profiles


def save_unified_profiles(path: Path, profiles: list[BatchProfile]) -> None:
    raw = _read_json(path)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for profile in profiles:
        nested = profile.to_mapping()
        nested.pop("provider_id", None)
        grouped.setdefault(profile.provider_id, []).append(nested)
    for provider in raw["llm_providers"]:
        if not isinstance(provider, dict):
            continue
        provider_id = str(provider.get("id") or "").strip()
        provider["run_profiles"] = grouped.get(provider_id, [])
    path.write_text(
        json.dumps(raw, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def migrate_legacy_profiles(path: Path) -> bool:
    """Move the temporary standalone profile file into llm_providers.json once."""
    if load_unified_profiles(path):
        return False
    if not DEFAULT_BATCH_CONFIG.exists():
        return False
    legacy = json.loads(DEFAULT_BATCH_CONFIG.read_text(encoding="utf-8"))
    items = legacy.get("profiles") if isinstance(legacy, dict) else None
    if not isinstance(items, list) or not items:
        return False
    profiles = [BatchProfile.from_mapping(item) for item in items if isinstance(item, dict)]
    save_unified_profiles(path, profiles)
    return True


def _run_profiles(runner: Any, profiles: list[BatchProfile]) -> None:
    router = runner.llm_router()
    selected_provider = router.current_spec().provider_id
    store, node = runner._require_node()
    before_names = {path.name for path in list_transcripts(node)}
    before_active = next(
        (path for path in list_transcripts(node) if transcript_is_restorable(path)),
        None,
    )
    successes: list[str] = []
    failures: list[str] = []

    for profile in profiles:
        if not profile.enabled:
            continue
        configured, state = _profile_state(profile, router)
        if not configured:
            message = f"{profile.label}: {state}"
            print(f"Skipping {message}")
            failures.append(message)
            continue
        spec = router.select(profile.provider_id)
        print(
            f"\nRunning {profile.label}\n"
            f"  provider={profile.provider_id} model={profile.model}\n"
            f"  level={profile.analysis_level} tokens={profile.max_output_tokens} "
            f"temperature={profile.temperature} top_p={profile.top_p} "
            f"timeout={profile.timeout_seconds:g}s"
        )
        try:
            with _temporary_environment(_profile_environment(profile, spec)):
                runner._run_gpt_analysis_level(profile.analysis_level)
            successes.append(profile.label)
        except Exception as exc:
            print(f"Profile failed; continuing with the next checked row: {exc}")
            failures.append(f"{profile.label}: {exc}")

    fresh = [
        path for path in list_transcripts(node) if path.name not in before_names
    ]
    restored = _restore_selected_provider(
        runner, selected_provider, before_active, fresh
    )
    try:
        router.select(selected_provider)
    except Exception:
        pass

    print("\nMulti-LLM run complete.")
    print(f"  successful: {len(successes)}")
    print(f"  failed/skipped: {len(failures)}")
    print(f"  new transcripts: {len(fresh)}")
    if restored is not None:
        print(
            "  active README and mutable artifacts restored to the provider "
            f"selected with lowercase g: {restored.name}"
        )


def _text_editor(runner: Any, path: Path, profiles: list[BatchProfile]) -> None:
    from llm_batch_profiles import _edit_profile, _print_profiles

    router = runner.llm_router()
    while True:
        _print_profiles(profiles, router)
        print("Unified source: " + str(path))
        command = input("Provider-profile editor: ").strip()
        if not command:
            return
        lower = command.lower()
        if lower == "a":
            for profile in profiles:
                profile.enabled = _profile_state(profile, router)[0]
            continue
        if lower == "n":
            for profile in profiles:
                profile.enabled = False
            continue
        if lower == "s":
            save_unified_profiles(path, profiles)
            print(f"Saved: {path}")
            continue
        if lower == "r":
            save_unified_profiles(path, profiles)
            _run_profiles(runner, profiles)
            return
        if lower.startswith("e "):
            index = int(lower.split(None, 1)[1]) - 1
            if not 0 <= index < len(profiles):
                raise ValueError("Profile number is out of range")
            _edit_profile(profiles[index])
            continue
        index = int(command) - 1
        if not 0 <= index < len(profiles):
            raise ValueError("Profile number is out of range")
        profiles[index].enabled = not profiles[index].enabled


def _gui_editor(runner: Any, path: Path, profiles: list[BatchProfile]) -> EditorResult:
    import tkinter as tk
    from tkinter import messagebox, ttk

    result = EditorResult()
    root = tk.Tk()
    root.title("ARC3 LLM Provider Profiles")
    root.geometry("1500x720")

    title = ttk.Label(
        root,
        text="Checked rows run together. Every row has provider-specific model and parameters.",
    )
    title.pack(anchor="w", padx=10, pady=(10, 4))
    ttk.Label(root, text=str(path)).pack(anchor="w", padx=10, pady=(0, 8))

    outer = ttk.Frame(root)
    outer.pack(fill="both", expand=True, padx=10)
    canvas = tk.Canvas(outer, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    body = ttk.Frame(canvas)
    body.bind(
        "<Configure>",
        lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    canvas.create_window((0, 0), window=body, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    columns = [
        ("Use", 5),
        ("Provider", 15),
        ("Label", 30),
        ("Model", 45),
        ("Level", 7),
        ("Tokens", 10),
        ("Temp", 8),
        ("Top-p", 8),
        ("Reasoning", 10),
        ("Current image", 12),
        ("Parent image", 12),
        ("Timeout", 10),
        ("Seed", 8),
    ]
    for column, (label, width) in enumerate(columns):
        ttk.Label(body, text=label).grid(row=0, column=column, sticky="w", padx=2)
        body.grid_columnconfigure(column, minsize=width * 7)

    rows: list[dict[str, Any]] = []
    for row_index, profile in enumerate(profiles, start=1):
        values: dict[str, Any] = {
            "enabled": tk.BooleanVar(value=profile.enabled),
            "provider_id": tk.StringVar(value=profile.provider_id),
            "label": tk.StringVar(value=profile.label),
            "model": tk.StringVar(value=profile.model),
            "analysis_level": tk.StringVar(value=str(profile.analysis_level)),
            "max_output_tokens": tk.StringVar(value=str(profile.max_output_tokens)),
            "temperature": tk.StringVar(value="" if profile.temperature is None else str(profile.temperature)),
            "top_p": tk.StringVar(value="" if profile.top_p is None else str(profile.top_p)),
            "reasoning_effort": tk.StringVar(value=profile.reasoning_effort),
            "current_image_detail": tk.StringVar(value=profile.current_image_detail),
            "parent_image_detail": tk.StringVar(value=profile.parent_image_detail),
            "timeout_seconds": tk.StringVar(value=str(profile.timeout_seconds)),
            "seed": tk.StringVar(value="" if profile.seed is None else str(profile.seed)),
        }
        rows.append(values)
        ttk.Checkbutton(body, variable=values["enabled"]).grid(row=row_index, column=0)
        ttk.Entry(body, textvariable=values["provider_id"], width=16).grid(row=row_index, column=1, sticky="ew")
        ttk.Entry(body, textvariable=values["label"], width=30).grid(row=row_index, column=2, sticky="ew")
        ttk.Entry(body, textvariable=values["model"], width=45).grid(row=row_index, column=3, sticky="ew")
        ttk.Combobox(body, textvariable=values["analysis_level"], values=("2", "3", "4"), width=5).grid(row=row_index, column=4)
        ttk.Entry(body, textvariable=values["max_output_tokens"], width=9).grid(row=row_index, column=5)
        ttk.Entry(body, textvariable=values["temperature"], width=7).grid(row=row_index, column=6)
        ttk.Entry(body, textvariable=values["top_p"], width=7).grid(row=row_index, column=7)
        ttk.Combobox(body, textvariable=values["reasoning_effort"], values=("none", "low", "medium", "high"), width=9).grid(row=row_index, column=8)
        ttk.Combobox(body, textvariable=values["current_image_detail"], values=("low", "high"), width=10).grid(row=row_index, column=9)
        ttk.Combobox(body, textvariable=values["parent_image_detail"], values=("low", "high"), width=10).grid(row=row_index, column=10)
        ttk.Entry(body, textvariable=values["timeout_seconds"], width=9).grid(row=row_index, column=11)
        ttk.Entry(body, textvariable=values["seed"], width=7).grid(row=row_index, column=12)

    def collect() -> list[BatchProfile]:
        updated: list[BatchProfile] = []
        for original, values in zip(profiles, rows):
            updated.append(
                BatchProfile(
                    profile_id=original.profile_id,
                    label=values["label"].get().strip(),
                    provider_id=values["provider_id"].get().strip(),
                    model=values["model"].get().strip(),
                    enabled=bool(values["enabled"].get()),
                    analysis_level=int(values["analysis_level"].get()),
                    max_output_tokens=int(values["max_output_tokens"].get()),
                    temperature=float(values["temperature"].get()) if values["temperature"].get().strip() else None,
                    top_p=float(values["top_p"].get()) if values["top_p"].get().strip() else None,
                    reasoning_effort=values["reasoning_effort"].get().strip(),
                    current_image_detail=values["current_image_detail"].get().strip(),
                    parent_image_detail=values["parent_image_detail"].get().strip(),
                    timeout_seconds=float(values["timeout_seconds"].get()),
                    seed=int(values["seed"].get()) if values["seed"].get().strip() else None,
                )
            )
        return updated

    def save_only() -> None:
        try:
            updated = collect()
            save_unified_profiles(path, updated)
            profiles[:] = updated
            result.saved = True
            messagebox.showinfo("ARC3 LLM profiles", "Saved llm_providers.json")
        except Exception as exc:
            messagebox.showerror("Unable to save", str(exc))

    def save_and_run() -> None:
        try:
            updated = collect()
            save_unified_profiles(path, updated)
            profiles[:] = updated
            result.saved = True
            result.run = True
            root.destroy()
        except Exception as exc:
            messagebox.showerror("Unable to run", str(exc))

    buttons = ttk.Frame(root)
    buttons.pack(fill="x", padx=10, pady=10)
    ttk.Button(buttons, text="Save", command=save_only).pack(side="left")
    ttk.Button(buttons, text="Save and Run Checked", command=save_and_run).pack(side="left", padx=8)
    ttk.Button(buttons, text="Cancel", command=root.destroy).pack(side="right")

    root.mainloop()
    return result


def open_profile_editor(runner: Any) -> None:
    _install_sampling_parameters()
    path = _provider_config_path(runner)
    migrated = migrate_legacy_profiles(path)
    if migrated:
        print(f"Migrated run profiles into unified config: {path}")
    profiles = load_unified_profiles(path)
    if not profiles:
        raise RuntimeError(
            "No run_profiles are defined under llm_providers in " + str(path)
        )

    force_text = os.environ.get("ARC3_LLM_PROFILE_EDITOR", "").strip().lower() in {
        "text",
        "cli",
        "console",
    }
    if force_text:
        _text_editor(runner, path, profiles)
        return
    try:
        result = _gui_editor(runner, path, profiles)
    except Exception as exc:
        print(f"GUI profile editor unavailable ({exc}); using text editor.")
        _text_editor(runner, path, profiles)
        return
    if result.run:
        _run_profiles(runner, profiles)


def install_profile_editor_ui(ui_module: Any) -> None:
    _install_sampling_parameters()
    if getattr(ui_module.read_key, "_arc3_profile_editor", False):
        return
    original_read_key = ui_module.read_key
    original_print_controls = ui_module.print_controls

    def read_key() -> str:
        key = original_read_key()
        if key != "G":
            return key
        from multillm_runner import last_runner

        runner = last_runner()
        if runner is None:
            print("No active ARC3 runner is available for LLM profile editing.")
        else:
            try:
                open_profile_editor(runner)
            except Exception as exc:
                print(f"LLM provider-profile editor error: {exc}")
        return "\r"

    def print_controls(runner: Any, rows: list[dict[str, Any]]) -> None:
        original_print_controls(runner, rows)
        print("LLM profiles: (G) edit/check provider-specific runs and execute them")

    setattr(read_key, "_arc3_profile_editor", True)
    ui_module.read_key = read_key
    ui_module.print_controls = print_controls
