from __future__ import annotations

from types import SimpleNamespace

import pytest

import interactive_runner


def test_control_services_register_without_changing_dispatch_loop(capsys) -> None:
    modes = {name: dict(menu) for name, menu in interactive_runner.CONTROL_MODES.items()}
    keys = dict(interactive_runner.CONTROL_MODE_KEYS)
    handlers = dict(interactive_runner.CONTROL_MODE_HANDLERS)
    calls: list[object] = []
    runner = SimpleNamespace()
    try:
        interactive_runner.register_control_mode("phase3", title="Phase 3", key="z")
        interactive_runner.register_control_command(
            "phase3",
            7,
            "Rank learned rules",
            handler=lambda active_runner: calls.append(active_runner),
        )

        assert interactive_runner.CONTROL_MODE_KEYS["z"] == "phase3"
        interactive_runner.print_mode_menu("phase3")
        assert "(7) Rank learned rules" in capsys.readouterr().out
        interactive_runner.dispatch_control_mode(runner, "phase3", 7)
        assert calls == [runner]
    finally:
        interactive_runner.CONTROL_MODES.clear()
        interactive_runner.CONTROL_MODES.update(modes)
        interactive_runner.CONTROL_MODE_KEYS.clear()
        interactive_runner.CONTROL_MODE_KEYS.update(keys)
        interactive_runner.CONTROL_MODE_HANDLERS.clear()
        interactive_runner.CONTROL_MODE_HANDLERS.update(handlers)


def test_control_mode_registration_rejects_key_collisions() -> None:
    with pytest.raises(ValueError, match="already registered"):
        interactive_runner.register_control_mode("other", title="Other", key="g")
