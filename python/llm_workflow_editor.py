from __future__ import annotations

import copy
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Mapping

from llm_workflows import (
    LlmWorkflowEngine,
    WorkflowAwareLlmProviderRouter,
    run_workflow_menu,
)

EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "config" / "example_multistep_workflow.json"


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected one JSON object: {path}")
    return value


def load_example_workflow(path: Path = EXAMPLE_PATH) -> dict[str, Any]:
    value = _read_json(path)
    if not value.get("id") or not isinstance(value.get("steps"), list):
        raise ValueError(f"Invalid example workflow: {path}")
    return value


def ensure_example_workflow(raw: dict[str, Any]) -> bool:
    workflows = raw.setdefault("llm_workflows", [])
    if not isinstance(workflows, list):
        raise ValueError("llm_workflows must be a list")
    example = load_example_workflow()
    if any(
        isinstance(item, Mapping) and str(item.get("id") or "") == example["id"]
        for item in workflows
    ):
        return False
    workflows.append(copy.deepcopy(example))
    return True


def _open_file(path: Path) -> None:
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
        return
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if editor:
        subprocess.run([editor, str(path)], check=False)
    else:
        print(path.read_text(encoding="utf-8"))
        print(f"Edit workflow JSON at: {path}")


def _write_validated(runner: Any, path: Path, raw: dict[str, Any]) -> None:
    old_router = runner.llm_router()
    base_path = Path(old_router.base_catalog_path).resolve()
    previous = path.read_text(encoding="utf-8")
    path.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        WorkflowAwareLlmProviderRouter(base_path, workflow_path=path)
    except Exception:
        path.write_text(previous, encoding="utf-8")
        raise
    runner.reload_llm_router()


def _new_workflow(index: int) -> dict[str, Any]:
    return {
        "id": f"workflow_{index}",
        "label": f"Workflow {index}",
        "description": "",
        "steps": [],
    }


def _new_step(index: int, transaction_id: str) -> dict[str, Any]:
    return {
        "id": f"step_{index}",
        "transaction": transaction_id,
    }


def _gui_editor(runner: Any, path: Path, raw: dict[str, Any]) -> None:
    import tkinter as tk
    from tkinter import messagebox, simpledialog, ttk

    router = runner.llm_router()
    ensure_example_workflow(raw)
    workflows: list[dict[str, Any]] = raw["llm_workflows"]
    transactions = [
        item for item in raw.get("llm_transactions", []) if isinstance(item, dict)
    ]
    transaction_ids = [str(item.get("id") or "") for item in transactions]
    profile_ids = sorted(router.profile_by_id)
    model_ids = ["$selected", *sorted(router.model_by_id)]

    root = tk.Tk()
    root.title("ARC3 LLM / Prolog Workflow Editor")
    root.geometry("1540x880")

    ttk.Label(
        root,
        text=(
            "Build optional multistep workflows from LLM transactions and Prolog stages. "
            "The normal g → 4 path remains unchanged."
        ),
    ).pack(anchor="w", padx=10, pady=(10, 2))
    ttk.Label(root, text=str(path)).pack(anchor="w", padx=10, pady=(0, 8))

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10)
    workflow_tab = ttk.Frame(notebook)
    transaction_tab = ttk.Frame(notebook)
    notebook.add(workflow_tab, text="Workflows")
    notebook.add(transaction_tab, text="Transaction reference")

    workflow_tab.columnconfigure(1, weight=1)
    workflow_tab.rowconfigure(0, weight=1)

    left = ttk.Frame(workflow_tab)
    left.grid(row=0, column=0, sticky="nsw", padx=(0, 8), pady=8)
    ttk.Label(left, text="Defined workflows").pack(anchor="w")
    workflow_tree = ttk.Treeview(
        left,
        columns=("label", "steps"),
        show="headings",
        height=25,
        selectmode="browse",
    )
    workflow_tree.heading("label", text="Workflow")
    workflow_tree.heading("steps", text="Steps")
    workflow_tree.column("label", width=330)
    workflow_tree.column("steps", width=55, anchor="center")
    workflow_tree.pack(fill="y", expand=True)

    left_buttons = ttk.Frame(left)
    left_buttons.pack(fill="x", pady=(6, 0))

    right = ttk.Frame(workflow_tab)
    right.grid(row=0, column=1, sticky="nsew", pady=8)
    right.columnconfigure(1, weight=1)
    right.rowconfigure(4, weight=1)

    workflow_id = tk.StringVar()
    workflow_label = tk.StringVar()
    ttk.Label(right, text="ID").grid(row=0, column=0, sticky="w")
    ttk.Entry(right, textvariable=workflow_id, width=45).grid(
        row=0, column=1, sticky="ew", padx=5
    )
    ttk.Label(right, text="Label").grid(row=1, column=0, sticky="w")
    ttk.Entry(right, textvariable=workflow_label).grid(
        row=1, column=1, sticky="ew", padx=5
    )
    ttk.Label(right, text="Description").grid(row=2, column=0, sticky="nw")
    description = tk.Text(right, height=4, wrap="word")
    description.grid(row=2, column=1, sticky="ew", padx=5, pady=(3, 8))

    ttk.Label(right, text="Ordered steps").grid(row=3, column=0, columnspan=2, sticky="w")
    step_columns = (
        "order",
        "id",
        "transaction",
        "profile",
        "model",
        "level",
        "combine",
        "optional",
    )
    step_tree = ttk.Treeview(right, columns=step_columns, show="headings", selectmode="browse")
    headings = {
        "order": "#",
        "id": "Step ID",
        "transaction": "Transaction",
        "profile": "Profile",
        "model": "Model",
        "level": "Level",
        "combine": "Combine group",
        "optional": "Optional",
    }
    widths = {
        "order": 38,
        "id": 175,
        "transaction": 235,
        "profile": 270,
        "model": 190,
        "level": 55,
        "combine": 120,
        "optional": 65,
    }
    for column in step_columns:
        step_tree.heading(column, text=headings[column])
        step_tree.column(column, width=widths[column], anchor="center" if column in {"order", "level", "optional"} else "w")
    step_tree.grid(row=4, column=0, columnspan=2, sticky="nsew")

    step_buttons = ttk.Frame(right)
    step_buttons.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(6, 0))

    selected_index: int | None = None
    loading = False

    def current_workflow() -> dict[str, Any] | None:
        nonlocal selected_index
        if selected_index is None or not 0 <= selected_index < len(workflows):
            return None
        return workflows[selected_index]

    def commit_metadata() -> None:
        if loading:
            return
        item = current_workflow()
        if item is None:
            return
        item["id"] = workflow_id.get().strip()
        item["label"] = workflow_label.get().strip()
        item["description"] = description.get("1.0", "end").strip()

    def refresh_workflow_tree(select: int | None = None) -> None:
        workflow_tree.delete(*workflow_tree.get_children())
        for index, item in enumerate(workflows):
            workflow_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(item.get("label") or item.get("id"), len(item.get("steps") or [])),
            )
        if select is not None and 0 <= select < len(workflows):
            workflow_tree.selection_set(str(select))
            workflow_tree.focus(str(select))
            workflow_tree.see(str(select))

    def refresh_steps() -> None:
        step_tree.delete(*step_tree.get_children())
        item = current_workflow()
        for index, step in enumerate((item or {}).get("steps") or []):
            step_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    index + 1,
                    step.get("id", ""),
                    step.get("transaction", ""),
                    step.get("profile", ""),
                    step.get("model", ""),
                    step.get("analysis_level", ""),
                    step.get("combine_group", ""),
                    "yes" if step.get("continue_on_error") else "",
                ),
            )

    def load_selected(_event: Any = None) -> None:
        nonlocal selected_index, loading
        commit_metadata()
        selected = workflow_tree.selection()
        if not selected:
            return
        selected_index = int(selected[0])
        item = workflows[selected_index]
        loading = True
        workflow_id.set(str(item.get("id") or ""))
        workflow_label.set(str(item.get("label") or ""))
        description.delete("1.0", "end")
        description.insert("1.0", str(item.get("description") or ""))
        loading = False
        refresh_steps()

    def add_workflow() -> None:
        commit_metadata()
        workflows.append(_new_workflow(len(workflows) + 1))
        refresh_workflow_tree(len(workflows) - 1)
        load_selected()

    def add_example() -> None:
        commit_metadata()
        example = load_example_workflow()
        existing = next(
            (i for i, item in enumerate(workflows) if item.get("id") == example["id"]),
            None,
        )
        if existing is None:
            workflows.append(copy.deepcopy(example))
            existing = len(workflows) - 1
        refresh_workflow_tree(existing)
        load_selected()

    def duplicate_workflow() -> None:
        item = current_workflow()
        if item is None:
            return
        commit_metadata()
        duplicate = copy.deepcopy(item)
        duplicate["id"] = str(duplicate.get("id") or "workflow") + "_copy"
        duplicate["label"] = str(duplicate.get("label") or "Workflow") + " (copy)"
        workflows.append(duplicate)
        refresh_workflow_tree(len(workflows) - 1)
        load_selected()

    def delete_workflow() -> None:
        nonlocal selected_index
        item = current_workflow()
        if item is None:
            return
        if not messagebox.askyesno("Delete workflow", f"Delete {item.get('label') or item.get('id')}?"):
            return
        del workflows[selected_index]  # type: ignore[index]
        selected_index = min(selected_index or 0, len(workflows) - 1) if workflows else None
        refresh_workflow_tree(selected_index)
        if selected_index is not None:
            load_selected()
        else:
            workflow_id.set("")
            workflow_label.set("")
            description.delete("1.0", "end")
            refresh_steps()

    def selected_step_index() -> int | None:
        selected = step_tree.selection()
        return int(selected[0]) if selected else None

    def edit_step_dialog(step: dict[str, Any], *, title: str) -> bool:
        dialog = tk.Toplevel(root)
        dialog.title(title)
        dialog.transient(root)
        dialog.grab_set()
        dialog.columnconfigure(1, weight=1)

        variables = {
            "id": tk.StringVar(value=str(step.get("id") or "")),
            "transaction": tk.StringVar(value=str(step.get("transaction") or (transaction_ids[0] if transaction_ids else ""))),
            "profile": tk.StringVar(value=str(step.get("profile") or "")),
            "model": tk.StringVar(value=str(step.get("model") or "")),
            "analysis_level": tk.StringVar(value="" if step.get("analysis_level") is None else str(step.get("analysis_level"))),
            "combine_group": tk.StringVar(value=str(step.get("combine_group") or "")),
            "continue_on_error": tk.BooleanVar(value=bool(step.get("continue_on_error", False))),
        }
        rows = [
            ("Step ID", "id"),
            ("Transaction", "transaction"),
            ("Exact profile (optional)", "profile"),
            ("Model (optional)", "model"),
            ("Analysis level (optional)", "analysis_level"),
            ("Combine group (optional)", "combine_group"),
        ]
        for row, (label, key) in enumerate(rows):
            ttk.Label(dialog, text=label).grid(row=row, column=0, sticky="w", padx=8, pady=4)
            if key == "transaction":
                widget = ttk.Combobox(dialog, textvariable=variables[key], values=transaction_ids, width=48)
            elif key == "profile":
                widget = ttk.Combobox(dialog, textvariable=variables[key], values=("", *profile_ids), width=48)
            elif key == "model":
                widget = ttk.Combobox(dialog, textvariable=variables[key], values=("", *model_ids), width=48)
            elif key == "analysis_level":
                widget = ttk.Combobox(dialog, textvariable=variables[key], values=("", "2", "3", "4"), width=48)
            else:
                widget = ttk.Entry(dialog, textvariable=variables[key], width=52)
            widget.grid(row=row, column=1, sticky="ew", padx=8, pady=4)
        ttk.Checkbutton(
            dialog,
            text="Continue when this step fails",
            variable=variables["continue_on_error"],
        ).grid(row=len(rows), column=0, columnspan=2, sticky="w", padx=8, pady=6)

        accepted = False

        def accept() -> None:
            nonlocal accepted
            step.clear()
            step.update(
                {
                    "id": variables["id"].get().strip(),
                    "transaction": variables["transaction"].get().strip(),
                }
            )
            optional_values = {
                "profile": variables["profile"].get().strip(),
                "model": variables["model"].get().strip(),
                "combine_group": variables["combine_group"].get().strip(),
            }
            for key, value in optional_values.items():
                if value:
                    step[key] = value
            level = variables["analysis_level"].get().strip()
            if level:
                step["analysis_level"] = int(level)
            if variables["continue_on_error"].get():
                step["continue_on_error"] = True
            accepted = True
            dialog.destroy()

        buttons = ttk.Frame(dialog)
        buttons.grid(row=len(rows) + 1, column=0, columnspan=2, sticky="ew", padx=8, pady=8)
        ttk.Button(buttons, text="OK", command=accept).pack(side="left")
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="right")
        dialog.wait_window()
        return accepted

    def add_step() -> None:
        item = current_workflow()
        if item is None:
            return
        steps = item.setdefault("steps", [])
        step = _new_step(len(steps) + 1, transaction_ids[0] if transaction_ids else "")
        if edit_step_dialog(step, title="Add workflow step"):
            steps.append(step)
            refresh_steps()
            step_tree.selection_set(str(len(steps) - 1))

    def edit_step() -> None:
        item = current_workflow()
        index = selected_step_index()
        if item is None or index is None:
            return
        step = item["steps"][index]
        if edit_step_dialog(step, title="Edit workflow step"):
            refresh_steps()
            step_tree.selection_set(str(index))

    def delete_step() -> None:
        item = current_workflow()
        index = selected_step_index()
        if item is None or index is None:
            return
        del item["steps"][index]
        refresh_steps()

    def move_step(delta: int) -> None:
        item = current_workflow()
        index = selected_step_index()
        if item is None or index is None:
            return
        target = index + delta
        if not 0 <= target < len(item["steps"]):
            return
        item["steps"][index], item["steps"][target] = item["steps"][target], item["steps"][index]
        refresh_steps()
        step_tree.selection_set(str(target))

    workflow_tree.bind("<<TreeviewSelect>>", load_selected)
    step_tree.bind("<Double-1>", lambda _event: edit_step())

    ttk.Button(left_buttons, text="New", command=add_workflow).pack(side="left")
    ttk.Button(left_buttons, text="Add Example", command=add_example).pack(side="left", padx=4)
    ttk.Button(left_buttons, text="Duplicate", command=duplicate_workflow).pack(side="left")
    ttk.Button(left_buttons, text="Delete", command=delete_workflow).pack(side="right")

    ttk.Button(step_buttons, text="Add Step", command=add_step).pack(side="left")
    ttk.Button(step_buttons, text="Edit Step", command=edit_step).pack(side="left", padx=4)
    ttk.Button(step_buttons, text="Delete Step", command=delete_step).pack(side="left")
    ttk.Button(step_buttons, text="Move Up", command=lambda: move_step(-1)).pack(side="left", padx=(12, 4))
    ttk.Button(step_buttons, text="Move Down", command=lambda: move_step(1)).pack(side="left")

    transaction_tab.columnconfigure(0, weight=1)
    transaction_tab.rowconfigure(0, weight=1)
    transaction_tree = ttk.Treeview(
        transaction_tab,
        columns=("id", "kind", "vision", "outputs", "inputs"),
        show="headings",
    )
    for column, label, width in (
        ("id", "Transaction", 260),
        ("kind", "Kind", 130),
        ("vision", "Needs images", 95),
        ("outputs", "Outputs", 320),
        ("inputs", "Inputs", 520),
    ):
        transaction_tree.heading(column, text=label)
        transaction_tree.column(column, width=width)
    transaction_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
    for item in transactions:
        transaction_tree.insert(
            "",
            "end",
            values=(
                item.get("id", ""),
                item.get("kind", ""),
                "yes" if item.get("requires_vision") else "",
                ", ".join(item.get("output_keys") or ([item.get("output_file")] if item.get("output_file") else [])),
                ", ".join(item.get("input_files") or []),
            ),
        )
    ttk.Label(
        transaction_tab,
        text="Transactions remain editable in config/llm_workflows.json; this tab is a reference while composing steps.",
    ).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 8))

    def save() -> bool:
        try:
            commit_metadata()
            _write_validated(runner, path, raw)
            messagebox.showinfo("ARC3 workflows", "Saved and validated llm_workflows.json")
            return True
        except Exception as exc:
            messagebox.showerror("Unable to save workflow catalog", str(exc))
            return False

    def save_and_run() -> None:
        item = current_workflow()
        if item is None:
            return
        workflow_to_run = workflow_id.get().strip()
        if not workflow_to_run:
            messagebox.showerror("Missing workflow ID", "The selected workflow requires an ID.")
            return
        if not save():
            return
        root.destroy()
        LlmWorkflowEngine(runner).run(workflow_to_run)

    def refresh_openrouter() -> None:
        try:
            from llm_key_controls import refresh_openrouter_models

            refresh_openrouter_models(runner)
            messagebox.showinfo(
                "OpenRouter refresh",
                "Availability was refreshed. Detailed results were printed in the debugger terminal.",
            )
        except Exception as exc:
            messagebox.showerror("OpenRouter refresh failed", str(exc))

    bottom = ttk.Frame(root)
    bottom.pack(fill="x", padx=10, pady=10)
    ttk.Button(bottom, text="Save", command=save).pack(side="left")
    ttk.Button(bottom, text="Save and Run Selected", command=save_and_run).pack(side="left", padx=6)
    ttk.Button(bottom, text="Refresh OpenRouter", command=refresh_openrouter).pack(side="left")
    ttk.Button(bottom, text="Edit Raw JSON", command=lambda: _open_file(path)).pack(side="left", padx=6)
    ttk.Button(bottom, text="Close", command=root.destroy).pack(side="right")

    refresh_workflow_tree(0 if workflows else None)
    if workflows:
        load_selected()
    root.mainloop()


def open_workflow_editor(runner: Any) -> None:
    router = runner.llm_router()
    if not isinstance(router, WorkflowAwareLlmProviderRouter):
        raise RuntimeError("Workflow router is not installed")
    path = Path(router.workflow_path).resolve()
    raw = _read_json(path)
    force_text = os.environ.get("ARC3_LLM_WORKFLOW_EDITOR", "").strip().lower() in {
        "text",
        "cli",
        "console",
    }
    if force_text:
        run_workflow_menu(runner)
        return
    try:
        _gui_editor(runner, path, raw)
    except Exception as exc:
        print(f"GUI workflow editor unavailable ({exc}); using text menu.")
        run_workflow_menu(runner)


def install_workflow_editor_ui(ui_module: Any) -> None:
    if getattr(ui_module.read_key, "_arc3_workflow_editor_ui", False):
        return
    original_read_key = ui_module.read_key
    original_print_controls = ui_module.print_controls

    def read_key() -> str:
        key = original_read_key()
        if key != "W":
            return key
        from multillm_runner import last_runner

        runner = last_runner()
        if runner is None:
            print("No active ARC3 runner is available for workflow editing.")
        else:
            try:
                open_workflow_editor(runner)
            except Exception as exc:
                print(f"LLM workflow editor error: {exc}")
        return "\r"

    def print_controls(runner: Any, rows: list[dict[str, Any]]) -> None:
        original_print_controls(runner, rows)
        print("Workflow GUI: (W) edit, validate, and run multistep LLM/Prolog workflows")

    read_key._arc3_workflow_editor_ui = True  # type: ignore[attr-defined]
    ui_module.read_key = read_key
    ui_module.print_controls = print_controls
