from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping


class SWIPrologBridge:
    """Invoke a Prolog controller using a JSON snapshot from Arc3Runner."""

    def __init__(
        self,
        agent_file: str | Path,
        swipl_executable: str = "swipl",
    ) -> None:
        self.agent_file = Path(agent_file).resolve()
        self.swipl_executable = swipl_executable
        if not self.agent_file.exists():
            raise FileNotFoundError(self.agent_file)

    def choose_action(self, snapshot: Mapping[str, Any]) -> dict[str, Any]:
        with tempfile.TemporaryDirectory(prefix="arc3_debugger_") as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "state.json"
            output_path = tmp_path / "action.json"
            input_path.write_text(json.dumps(snapshot), encoding="utf-8")

            goal = (
                "arc3_agent:choose_action_file("
                + repr(str(input_path))
                + ","
                + repr(str(output_path))
                + ")"
            )

            result = subprocess.run(
                [
                    self.swipl_executable,
                    "-q",
                    "-s",
                    str(self.agent_file),
                    "-g",
                    goal,
                    "-t",
                    "halt",
                ],
                cwd=self.agent_file.parent,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    "SWI-Prolog controller failed:\n" + result.stderr
                )

            return json.loads(output_path.read_text(encoding="utf-8"))

    def execute_turtle(
        self,
        program: str,
        params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a turtle/2 program through the canonical Turtle DSL."""

        params = dict(params or {})
        dsl_file = self.agent_file.parent / "turtle_dsl.pl"
        if not dsl_file.exists():
            raise FileNotFoundError(dsl_file)
        with tempfile.TemporaryDirectory(prefix="arc3_turtle_") as tmp:
            tmp_path = Path(tmp)
            program_path = tmp_path / "program.pl"
            output_path = tmp_path / "result.json"
            program_path.write_text(program, encoding="utf-8")
            state = {
                "turtle_x": int(params.get("turtle_x", 0)),
                "turtle_y": int(params.get("turtle_y", 0)),
                "direction": str(params.get("direction", "east")),
                "pen": str(params.get("pen", "up")),
                "pen_width": int(params.get("pen_width", 1)),
                "color": str(params.get("color", "black")),
                "cells": [],
            }
            state_path = tmp_path / "state.json"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            runner_path = tmp_path / "run_turtle.pl"
            runner_path.write_text(
                ":- use_module(library(http/json)).\n"
                f":- use_module({repr(str(dsl_file))}).\n"
                f":- consult({repr(str(program_path))}).\n"
                "cell_pair(cell(X,Y), [X,Y]).\n"
                "main :-\n"
                f"  open({repr(str(state_path))}, read, In), json_read_dict(In, S0, [value_string_as(atom)]), close(In),\n"
                "  turtle(_, Instructions), turtle_dsl:execute_program(Instructions, S0, S),\n"
                "  maplist(cell_pair, S.cells, Cells), Out = S.put(cells, Cells),\n"
                f"  open({repr(str(output_path))}, write, Stream), json_write_dict(Stream, Out), close(Stream).\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    self.swipl_executable,
                    "-q",
                    "-s",
                    str(runner_path),
                    "-g",
                    "main",
                    "-t",
                    "halt",
                ],
                cwd=self.agent_file.parent,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                raise RuntimeError("SWI-Prolog Turtle execution failed:\n" + result.stderr)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            payload["stdout"] = result.stdout
            payload["stderr"] = result.stderr
            return payload
