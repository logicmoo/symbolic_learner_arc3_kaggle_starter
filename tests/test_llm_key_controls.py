from __future__ import annotations

from types import SimpleNamespace

import llm_key_controls
import llm_profile_editor
import llm_workflows
import multillm_runner


class DummyUi(SimpleNamespace):
    def __init__(self, key: str) -> None:
        super().__init__()
        self.read_key = lambda: key
        self.print_controls = self._print_controls

    @staticmethod
    def _print_controls(_runner, _rows) -> None:
        print("Files: (w) Save History  (e) Export State  (q) Quit")


def install_all(ui: DummyUi) -> None:
    llm_profile_editor.install_profile_editor_ui(ui)
    llm_workflows.install_workflow_ui(ui)
    llm_key_controls.install_llm_key_controls(ui)


def test_agreed_keys_dispatch(monkeypatch) -> None:
    runner = object()
    monkeypatch.setattr(multillm_runner, "_LAST_RUNNER", runner)
    calls: list[str] = []
    monkeypatch.setattr(
        llm_profile_editor,
        "open_profile_editor",
        lambda value: calls.append("G"),
    )
    monkeypatch.setattr(
        llm_workflows,
        "run_workflow_menu",
        lambda value: calls.append("W"),
    )
    monkeypatch.setattr(
        llm_key_controls,
        "run_checked_batch",
        lambda value: calls.append("b"),
    )
    monkeypatch.setattr(
        llm_key_controls,
        "repeat_last_workflow",
        lambda value: calls.append("w"),
    )
    monkeypatch.setattr(
        llm_key_controls,
        "refresh_openrouter_models",
        lambda value: calls.append("O"),
    )
    monkeypatch.setattr(
        llm_key_controls,
        "save_history",
        lambda value: calls.append("H"),
    )

    for key in ("G", "W", "b", "w", "O", "H"):
        ui = DummyUi(key)
        install_all(ui)
        assert ui.read_key() == "\r"

    assert calls == ["G", "W", "b", "w", "O", "H"]


def test_help_shows_every_llm_key_and_remaps_history(capsys) -> None:
    ui = DummyUi("?")
    install_all(ui)
    ui.print_controls(object(), [])
    text = capsys.readouterr().out

    assert "(H) Save History" in text
    assert "(w) Save History" not in text
    for fragment in (
        "(g) Next Model",
        "(G) Catalog/Batch Editor",
        "(2/3/4) Light/Deep/Extreme",
        "(b) Run Batch",
        "(W) Choose Workflow",
        "(w) Repeat Workflow",
        "(O) Refresh OpenRouter",
    ):
        assert fragment in text


def test_repeat_without_selection_explains_next_action(capsys) -> None:
    class FakeRouter(llm_workflows.WorkflowAwareLlmProviderRouter):
        pass

    router = object.__new__(FakeRouter)
    router.workflow_by_id = {}
    runner = SimpleNamespace(llm_router=lambda: router)

    llm_key_controls.repeat_last_workflow(runner)

    assert "Press uppercase W first" in capsys.readouterr().out
