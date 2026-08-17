from pathlib import Path

from object_memory import CellLogoForm
from swipl_bridge import SWIPrologBridge
from workbench.server.runtime import DEFAULT_GRID, analyze_grid


ROOT = Path(__file__).resolve().parents[1]


def _bridge() -> SWIPrologBridge:
    return SWIPrologBridge(ROOT / "prolog" / "arc3_agent.pl")


def test_cell_logo_form_executes_extracted_program_through_swi_prolog() -> None:
    extracted = analyze_grid(DEFAULT_GRID)
    blue = next(item for item in extracted["objects"] if item["id"] == "obj_blue_1")
    rendered = CellLogoForm(blue["turtleProgram"], swi_bridge=_bridge()).render()

    assert {tuple(cell) for cell in rendered["cells"]} == {
        tuple(cell) for cell in blue["cells"]
    }
    assert rendered["color"] == "blue"
    assert rendered["stderr"] == ""


def test_turtle_bridge_preserves_disconnected_runs_and_single_cells() -> None:
    grid = [[3, 0, 3], [0, 0, 0], [0, 4, 0]]
    extracted = analyze_grid(grid)

    for item in extracted["objects"]:
        rendered = CellLogoForm(item["turtleProgram"], swi_bridge=_bridge()).render()
        assert {tuple(cell) for cell in rendered["cells"]} == {
            tuple(cell) for cell in item["cells"]
        }


def test_cell_logo_fit_and_distance_use_regenerated_cells() -> None:
    extracted = analyze_grid(DEFAULT_GRID)
    blue = next(item for item in extracted["objects"] if item["id"] == "obj_blue_1")
    red = next(item for item in extracted["objects"] if item["id"] == "obj_red_1")
    blue_form = CellLogoForm(blue["turtleProgram"], swi_bridge=_bridge())
    red_form = CellLogoForm(red["turtleProgram"], swi_bridge=_bridge())

    exact = blue_form.fit_instance(blue)
    missing_cell = blue_form.fit_instance({"cells": blue["cells"][:-1]})

    assert exact.residual == 0.0
    assert exact.parameters["expected_cells"] == exact.parameters["rendered_cells"]
    assert exact.parameters["description_length"] == blue_form.description_length()
    assert 0.0 < missing_cell.residual < 1.0
    assert blue_form.distance(blue_form) == 0.0
    assert blue_form.distance(red_form) > 0.0


def test_thick_rectangle_uses_pen_width_instead_of_row_enumeration() -> None:
    grid = [
        [0, 5, 5, 5, 0],
        [0, 5, 5, 5, 0],
        [0, 5, 5, 5, 0],
        [0, 5, 5, 5, 0],
        [0, 5, 5, 5, 0],
    ]
    item = analyze_grid(grid)["objects"][0]

    assert "pen_width(3)" in item["turtleProgram"]
    assert item["turtleProgram"].count("set_pos(") == 1
    assert "rot(90)" in item["turtleProgram"]
    rendered = CellLogoForm(item["turtleProgram"], swi_bridge=_bridge()).render()
    assert {tuple(cell) for cell in rendered["cells"]} == {
        tuple(cell) for cell in item["cells"]
    }


def test_wide_rectangle_uses_one_exact_width_aware_stroke() -> None:
    grid = [[7] * 6 for _ in range(8)]
    item = analyze_grid(grid)["objects"][0]

    assert "pen_width(6)" in item["turtleProgram"]
    assert item["turtleProgram"].count("set_pos(") == 1
    assert item["turtleProgram"].count("fwd(") == 1
    rendered = CellLogoForm(item["turtleProgram"], swi_bridge=_bridge()).render()
    assert {tuple(cell) for cell in rendered["cells"]} == {
        tuple(cell) for cell in item["cells"]
    }


def test_hollow_object_preserves_hole_and_exact_topology() -> None:
    grid = [
        [0, 0, 0, 0, 0],
        [0, 5, 5, 5, 0],
        [0, 5, 0, 5, 0],
        [0, 5, 5, 5, 0],
        [0, 0, 0, 0, 0],
    ]
    item = analyze_grid(grid)["objects"][0]
    rendered = CellLogoForm(item["turtleProgram"], swi_bridge=_bridge()).render()

    assert item["shape"] == "hollow_square"
    assert item["topology"]["connectedComponents"] == 1
    assert item["topology"]["holeCount"] == 1
    assert item["topology"]["holes"] == [[[2, 2]]]
    assert item["turtleProgram"].count("set_pos(") == 1
    assert item["turtleProgram"].count("penup") == 1
    assert "rot(" in item["turtleProgram"]
    assert (2, 2) not in {tuple(cell) for cell in rendered["cells"]}
    assert {tuple(cell) for cell in rendered["cells"]} == {
        tuple(cell) for cell in item["cells"]
    }
