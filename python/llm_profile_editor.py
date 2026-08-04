from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from llm_model_catalog import CatalogAwareLlmProviderRouter
from llm_readme_patch import transcript_is_restorable
from llm_transcripts import (
    list_transcripts,
    restore_transcript,
    transcript_metadata,
)


@dataclass
class EditorResult:
    run_batch: bool = False
    saved: bool = False


def _config_path(runner: Any) -> Path:
    return Path(runner.llm_router().catalog_path).resolve()


def _read(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"LLM catalog must be one JSON object: {path}")
    for key in ("llm_providers", "llm_models", "llm_profiles", "prompt_text"):
        if key not in raw:
            raise ValueError(f"LLM catalog is missing {key}")
    return raw


def _write_validated(path: Path, raw: dict[str, Any]) -> None:
    previous = path.read_text(encoding="utf-8")
    path.write_text(
        json.dumps(raw, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    try:
        CatalogAwareLlmProviderRouter(path)
    except Exception:
        path.write_text(previous, encoding="utf-8")
        raise


def _newest_selected_model_transcript(
    router: CatalogAwareLlmProviderRouter,
    selected_model_id: str,
    fresh: list[Path],
) -> Path | None:
    for path in fresh:
        if not transcript_is_restorable(path):
            continue
        profile_id = str(transcript_metadata(path).get("provider_id") or "")
        profile = router.profile_by_id.get(profile_id)
        if profile and profile.model_id == selected_model_id:
            return path
    return None


def _run_batch(runner: Any) -> None:
    old_router = runner.llm_router()
    selected_model_id = old_router.active_model().model_id
    store, node = runner._require_node()
    before = {path.name for path in list_transcripts(node)}
    before_active = next(
        (path for path in list_transcripts(node) if transcript_is_restorable(path)),
        None,
    )
    router = runner.reload_llm_router(active_model_id=selected_model_id)
    successes: list[str] = []
    failures: list[str] = []

    for profile in router.batch_profiles():
        model = router.model_by_id[profile.model_id]
        backend = router.backend_by_id[model.provider_id]
        print(
            f"\nBatch profile: {profile.label}\n"
            f"  backend={backend.backend_id} model={model.model_id}\n"
            f"  L{profile.analysis_level} tokens={profile.max_output_tokens} "
            f"timeout={profile.timeout_seconds:g}s"
        )
        try:
            runner._run_gpt_analysis_level(
                profile.analysis_level,
                profile_id=profile.profile_id,
                mode="batch",
            )
            successes.append(profile.label)
        except Exception as exc:
            print(f"Skipped after failure: {exc}")
            failures.append(f"{profile.label}: {exc}")

    fresh = [
        path for path in list_transcripts(node) if path.name not in before
    ]
    target = _newest_selected_model_transcript(
        router, selected_model_id, fresh
    )
    if target is None:
        target = before_active
    if target is not None and target.exists() and transcript_is_restorable(target):
        restore_transcript(store, node, target)
    try:
        router.select_model(selected_model_id)
    except Exception:
        pass

    print("\nMulti-model batch complete.")
    print(f"  successful profiles: {len(successes)}")
    print(f"  failed/skipped profiles: {len(failures)}")
    print(f"  new comparison transcripts: {len(fresh)}")
    if target is not None:
        print(
            "  active README/artifacts restored to the lowercase-g selected "
            f"model: {target.name}"
        )


def _nullable_float(text: str) -> float | None:
    value = text.strip()
    return None if not value else float(value)


def _nullable_int(text: str) -> int | None:
    value = text.strip()
    return None if not value else int(value)


def _gui_editor(runner: Any, path: Path, raw: dict[str, Any]) -> EditorResult:
    import tkinter as tk
    from tkinter import messagebox, ttk

    result = EditorResult()
    root = tk.Tk()
    root.title("ARC3 LLM Providers, Models, and Profiles")
    root.geometry("1780x840")
    ttk.Label(
        root,
        text=(
            "Providers are backends; models select providers; level profiles "
            "select models and independently enable Single and Batch use."
        ),
    ).pack(anchor="w", padx=10, pady=(10, 2))
    ttk.Label(root, text=str(path)).pack(anchor="w", padx=10, pady=(0, 8))

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10)

    provider_vars: list[dict[str, Any]] = []
    model_vars: list[dict[str, Any]] = []
    profile_vars: list[dict[str, Any]] = []

    def scrollable_tab(title: str):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)
        canvas = tk.Canvas(frame, highlightthickness=0)
        ybar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        xbar = ttk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
        body = ttk.Frame(canvas)
        body.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return frame, body

    _provider_tab, provider_body = scrollable_tab("Provider backends")
    _model_tab, model_body = scrollable_tab("Models")
    _profile_tab, profile_body = scrollable_tab("Level profiles")

    provider_columns = [
        "ID", "Label", "Adapter", "Enabled", "API key env", "Key optional",
        "Base URL", "Base URL env", "Health URL", "Health URL env",
        "Reasoning", "Timeout", "Default model",
    ]
    for column, label in enumerate(provider_columns):
        ttk.Label(provider_body, text=label).grid(
            row=0, column=column, sticky="w", padx=2
        )

    for row_index, item in enumerate(raw["llm_providers"], start=1):
        values = {
            "id": tk.StringVar(value=str(item.get("id", ""))),
            "label": tk.StringVar(value=str(item.get("label", ""))),
            "adapter": tk.StringVar(value=str(item.get("adapter", ""))),
            "enabled": tk.StringVar(value=str(item.get("enabled", "auto")).lower()),
            "api_key_env": tk.StringVar(value=str(item.get("api_key_env", "") or "")),
            "api_key_optional": tk.BooleanVar(value=bool(item.get("api_key_optional", False))),
            "base_url": tk.StringVar(value=str(item.get("base_url", "") or "")),
            "base_url_env": tk.StringVar(value=str(item.get("base_url_env", "") or "")),
            "health_url": tk.StringVar(value=str(item.get("health_url", "") or "")),
            "health_url_env": tk.StringVar(value=str(item.get("health_url_env", "") or "")),
            "supports_reasoning": tk.BooleanVar(value=bool(item.get("supports_reasoning", False))),
            "timeout_seconds": tk.StringVar(value=str(item.get("timeout_seconds", 600))),
            "default_model": tk.StringVar(value=str(item.get("default_model", "") or "")),
        }
        provider_vars.append(values)
        entries = [
            ("id", 16), ("label", 24), ("adapter", 20), ("enabled", 8),
            ("api_key_env", 22), None, ("base_url", 34), ("base_url_env", 22),
            ("health_url", 34), ("health_url_env", 22), None,
            ("timeout_seconds", 9), ("default_model", 25),
        ]
        for column, entry in enumerate(entries):
            if entry is None:
                key = "api_key_optional" if column == 5 else "supports_reasoning"
                ttk.Checkbutton(provider_body, variable=values[key]).grid(
                    row=row_index, column=column
                )
            elif entry[0] == "enabled":
                ttk.Combobox(
                    provider_body,
                    textvariable=values["enabled"],
                    values=("auto", "true", "false"),
                    width=7,
                ).grid(row=row_index, column=column, sticky="ew")
            else:
                ttk.Entry(
                    provider_body,
                    textvariable=values[entry[0]],
                    width=entry[1],
                ).grid(row=row_index, column=column, sticky="ew")

    model_columns = [
        "ID", "Provider", "Label", "Model slug", "Model env",
        "Reasoning", "Vision", "Default level",
    ]
    for column, label in enumerate(model_columns):
        ttk.Label(model_body, text=label).grid(
            row=0, column=column, sticky="w", padx=2
        )
    for row_index, item in enumerate(raw["llm_models"], start=1):
        values = {
            "id": tk.StringVar(value=str(item.get("id", ""))),
            "provider": tk.StringVar(value=str(item.get("provider", ""))),
            "label": tk.StringVar(value=str(item.get("label", ""))),
            "model": tk.StringVar(value=str(item.get("model", ""))),
            "model_env": tk.StringVar(value=str(item.get("model_env", "") or "")),
            "supports_reasoning": tk.BooleanVar(value=bool(item.get("supports_reasoning", False))),
            "vision": tk.BooleanVar(value=bool(item.get("vision", True))),
            "default_level": tk.StringVar(value=str(item.get("default_level", 3))),
        }
        model_vars.append(values)
        for column, (key, width) in enumerate(
            [
                ("id", 28), ("provider", 16), ("label", 30),
                ("model", 54), ("model_env", 24),
            ]
        ):
            ttk.Entry(model_body, textvariable=values[key], width=width).grid(
                row=row_index, column=column, sticky="ew"
            )
        ttk.Checkbutton(
            model_body, variable=values["supports_reasoning"]
        ).grid(row=row_index, column=5)
        ttk.Checkbutton(model_body, variable=values["vision"]).grid(
            row=row_index, column=6
        )
        ttk.Combobox(
            model_body,
            textvariable=values["default_level"],
            values=("2", "3", "4"),
            width=6,
        ).grid(row=row_index, column=7)

    profile_columns = [
        "Single", "Batch", "ID", "Model", "Label", "Level", "Tokens",
        "Temp", "Top-p", "Reasoning", "Current image", "Parent image",
        "Timeout", "Seed", "Prompt sections (ordered, comma-separated)",
    ]
    for column, label in enumerate(profile_columns):
        ttk.Label(profile_body, text=label).grid(
            row=0, column=column, sticky="w", padx=2
        )
    for row_index, item in enumerate(raw["llm_profiles"], start=1):
        values = {
            "single_enabled": tk.BooleanVar(value=bool(item.get("single_enabled", False))),
            "batch_enabled": tk.BooleanVar(value=bool(item.get("batch_enabled", False))),
            "id": tk.StringVar(value=str(item.get("id", ""))),
            "model": tk.StringVar(value=str(item.get("model", ""))),
            "label": tk.StringVar(value=str(item.get("label", ""))),
            "analysis_level": tk.StringVar(value=str(item.get("analysis_level", 3))),
            "max_output_tokens": tk.StringVar(value=str(item.get("max_output_tokens", 12000))),
            "temperature": tk.StringVar(value="" if item.get("temperature") is None else str(item["temperature"])),
            "top_p": tk.StringVar(value="" if item.get("top_p") is None else str(item["top_p"])),
            "reasoning_effort": tk.StringVar(value=str(item.get("reasoning_effort", "low"))),
            "current_image_detail": tk.StringVar(value=str(item.get("current_image_detail", "low"))),
            "parent_image_detail": tk.StringVar(value=str(item.get("parent_image_detail", "low"))),
            "timeout_seconds": tk.StringVar(value=str(item.get("timeout_seconds", 600))),
            "seed": tk.StringVar(value="" if item.get("seed") is None else str(item["seed"])),
            "prompt_text": tk.StringVar(value=", ".join(item.get("prompt_text") or [])),
        }
        profile_vars.append(values)
        ttk.Checkbutton(
            profile_body, variable=values["single_enabled"]
        ).grid(row=row_index, column=0)
        ttk.Checkbutton(
            profile_body, variable=values["batch_enabled"]
        ).grid(row=row_index, column=1)
        text_fields = [
            ("id", 32), ("model", 30), ("label", 34),
            ("analysis_level", 6), ("max_output_tokens", 9),
            ("temperature", 7), ("top_p", 7), ("reasoning_effort", 10),
            ("current_image_detail", 10), ("parent_image_detail", 10),
            ("timeout_seconds", 9), ("seed", 7), ("prompt_text", 95),
        ]
        for offset, (key, width) in enumerate(text_fields, start=2):
            if key == "analysis_level":
                widget = ttk.Combobox(
                    profile_body,
                    textvariable=values[key],
                    values=("2", "3", "4"),
                    width=width,
                )
            elif key == "reasoning_effort":
                widget = ttk.Combobox(
                    profile_body,
                    textvariable=values[key],
                    values=("none", "low", "medium", "high"),
                    width=width,
                )
            elif key in {"current_image_detail", "parent_image_detail"}:
                widget = ttk.Combobox(
                    profile_body,
                    textvariable=values[key],
                    values=("low", "high"),
                    width=width,
                )
            else:
                widget = ttk.Entry(
                    profile_body, textvariable=values[key], width=width
                )
            widget.grid(row=row_index, column=offset, sticky="ew")

    def collect() -> dict[str, Any]:
        updated = dict(raw)
        updated["llm_providers"] = []
        for values in provider_vars:
            enabled_text = values["enabled"].get().strip().lower()
            enabled: bool | str
            if enabled_text == "true":
                enabled = True
            elif enabled_text == "false":
                enabled = False
            else:
                enabled = "auto"
            item = {
                "id": values["id"].get().strip(),
                "label": values["label"].get().strip(),
                "adapter": values["adapter"].get().strip(),
                "enabled": enabled,
                "api_key_env": values["api_key_env"].get().strip() or None,
                "api_key_optional": bool(values["api_key_optional"].get()),
                "base_url": values["base_url"].get().strip() or None,
                "base_url_env": values["base_url_env"].get().strip() or None,
                "health_url": values["health_url"].get().strip() or None,
                "health_url_env": values["health_url_env"].get().strip() or None,
                "supports_reasoning": bool(values["supports_reasoning"].get()),
                "timeout_seconds": float(values["timeout_seconds"].get()),
                "default_model": values["default_model"].get().strip() or None,
            }
            updated["llm_providers"].append(
                {key: value for key, value in item.items() if value is not None}
            )

        updated["llm_models"] = []
        for values in model_vars:
            updated["llm_models"].append(
                {
                    "id": values["id"].get().strip(),
                    "provider": values["provider"].get().strip(),
                    "label": values["label"].get().strip(),
                    "model": values["model"].get().strip(),
                    "model_env": values["model_env"].get().strip() or None,
                    "supports_reasoning": bool(values["supports_reasoning"].get()),
                    "vision": bool(values["vision"].get()),
                    "default_level": int(values["default_level"].get()),
                }
            )
            if updated["llm_models"][-1]["model_env"] is None:
                updated["llm_models"][-1].pop("model_env")

        updated["llm_profiles"] = []
        for values in profile_vars:
            sections = [
                name.strip()
                for name in values["prompt_text"].get().split(",")
                if name.strip()
            ]
            updated["llm_profiles"].append(
                {
                    "id": values["id"].get().strip(),
                    "model": values["model"].get().strip(),
                    "label": values["label"].get().strip(),
                    "analysis_level": int(values["analysis_level"].get()),
                    "single_enabled": bool(values["single_enabled"].get()),
                    "batch_enabled": bool(values["batch_enabled"].get()),
                    "max_output_tokens": int(values["max_output_tokens"].get()),
                    "temperature": _nullable_float(values["temperature"].get()),
                    "top_p": _nullable_float(values["top_p"].get()),
                    "reasoning_effort": values["reasoning_effort"].get().strip(),
                    "current_image_detail": values["current_image_detail"].get().strip(),
                    "parent_image_detail": values["parent_image_detail"].get().strip(),
                    "timeout_seconds": float(values["timeout_seconds"].get()),
                    "seed": _nullable_int(values["seed"].get()),
                    "prompt_text": sections,
                }
            )
        return updated

    def save(run_batch: bool) -> None:
        try:
            updated = collect()
            _write_validated(path, updated)
            result.saved = True
            result.run_batch = run_batch
            if run_batch:
                root.destroy()
            else:
                messagebox.showinfo("ARC3 LLM catalog", "Saved llm_providers.json")
        except Exception as exc:
            messagebox.showerror("Unable to save", str(exc))

    buttons = ttk.Frame(root)
    buttons.pack(fill="x", padx=10, pady=10)
    ttk.Button(buttons, text="Save", command=lambda: save(False)).pack(side="left")
    ttk.Button(
        buttons,
        text="Save and Run Batch-Enabled Profiles",
        command=lambda: save(True),
    ).pack(side="left", padx=8)
    ttk.Button(buttons, text="Cancel", command=root.destroy).pack(side="right")
    root.mainloop()
    return result


def _text_editor(runner: Any, path: Path, raw: dict[str, Any]) -> None:
    while True:
        print("\nLLM MODEL PROFILES")
        for index, profile in enumerate(raw["llm_profiles"], start=1):
            single = "S" if profile.get("single_enabled") else "-"
            batch = "B" if profile.get("batch_enabled") else "-"
            print(
                f" {index:>2}. [{single}{batch}] {profile.get('label')} "
                f"model={profile.get('model')} L{profile.get('analysis_level')} "
                f"tokens={profile.get('max_output_tokens')}"
            )
        print("Commands: b NUMBER=batch toggle  s NUMBER=single toggle")
        print("          e=open unified JSON  w=write  r=write and run batch  Enter=cancel")
        command = input("Catalog editor: ").strip()
        if not command:
            return
        lower = command.lower()
        if lower in {"e", "edit"}:
            runner._analyzer().edit_prompts()
            raw = _read(path)
            continue
        if lower in {"w", "write"}:
            _write_validated(path, raw)
            runner.reload_llm_router()
            print(f"Saved: {path}")
            continue
        if lower in {"r", "run"}:
            _write_validated(path, raw)
            runner.reload_llm_router()
            _run_batch(runner)
            return
        action, number = lower.split(None, 1)
        index = int(number) - 1
        profile = raw["llm_profiles"][index]
        if action == "b":
            profile["batch_enabled"] = not bool(profile.get("batch_enabled"))
        elif action == "s":
            profile["single_enabled"] = not bool(profile.get("single_enabled"))
        else:
            raise ValueError("Use b NUMBER or s NUMBER")


def open_profile_editor(runner: Any) -> None:
    path = _config_path(runner)
    raw = _read(path)
    force_text = os.environ.get("ARC3_LLM_PROFILE_EDITOR", "").strip().lower() in {
        "text", "cli", "console"
    }
    if force_text:
        _text_editor(runner, path, raw)
        return
    try:
        result = _gui_editor(runner, path, raw)
    except Exception as exc:
        print(f"GUI catalog editor unavailable ({exc}); using text editor.")
        _text_editor(runner, path, raw)
        return
    if result.saved:
        runner.reload_llm_router()
    if result.run_batch:
        _run_batch(runner)


def install_profile_editor_ui(ui_module: Any) -> None:
    if getattr(ui_module.read_key, "_arc3_catalog_editor", False):
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
            print("No active ARC3 runner is available for LLM catalog editing.")
        else:
            try:
                open_profile_editor(runner)
            except Exception as exc:
                print(f"LLM catalog editor error: {exc}")
        return "\r"

    def print_controls(runner: Any, rows: list[dict[str, Any]]) -> None:
        original_print_controls(runner, rows)
        print(
            "LLM catalog: (G) edit provider backends, models, and "
            "Single/Batch level profiles"
        )

    read_key._arc3_catalog_editor = True  # type: ignore[attr-defined]
    ui_module.read_key = read_key
    ui_module.print_controls = print_controls
