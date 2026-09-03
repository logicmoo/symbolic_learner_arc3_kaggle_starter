"""Regression tests for turtle-program normalization, especially coercing
ellipse/rectangle commands that lack an explicit box (models often emit
center+radius or x/y/width/height) so more turtle PNGs render locally."""

from video_import_pipeline import normalize_turtle_program, parse_onepass_output


def test_ellipse_center_radius_scalar_to_box() -> None:
    prog = normalize_turtle_program({"commands": [{"op": "ellipse", "cx": 100, "cy": 200, "r": 50}]})
    assert prog is not None
    assert prog["commands"][0]["box"] == [50, 150, 150, 250]


def test_circle_alias_center_and_radius_pair_to_box() -> None:
    prog = normalize_turtle_program({"commands": [{"op": "circle", "center": [10, 20], "radius": [5, 8]}]})
    assert prog is not None
    command = prog["commands"][0]
    assert command["op"] == "ellipse"  # alias normalized
    assert command["box"] == [5, 12, 15, 28]


def test_ellipse_xy_as_center_with_rx_ry_to_box() -> None:
    prog = normalize_turtle_program({"commands": [{"op": "ellipse", "x": 100, "y": 100, "rx": 30, "ry": 10}]})
    assert prog is not None
    assert prog["commands"][0]["box"] == [70, 90, 130, 110]


def test_rectangle_xywh_still_coerced_to_box() -> None:
    prog = normalize_turtle_program({"commands": [{"op": "rect", "x": 0, "y": 0, "w": 10, "h": 20}]})
    assert prog is not None
    command = prog["commands"][0]
    assert command["op"] == "rectangle"
    assert command["box"] == [0, 0, 10, 20]


def test_existing_box_is_preserved() -> None:
    prog = normalize_turtle_program({"commands": [{"op": "ellipse", "box": [1, 2, 3, 4]}]})
    assert prog is not None
    assert prog["commands"][0]["box"] == [1, 2, 3, 4]


def test_combined_parser_captures_turtle_program() -> None:
    import json

    raw = json.dumps({
        "description": "scene",
        "objects": [{"name": "a", "turtleProgram": {"commands": [{"op": "move", "x": 0, "y": 0}]}}],
    })
    out = parse_onepass_output(raw, capture_turtle=True)
    assert out["objects"][0].get("turtleProgram", {}).get("commands")


def test_onepass_parser_omits_turtle_program_by_default() -> None:
    import json

    raw = json.dumps({"objects": [{"name": "a", "turtleProgram": {"commands": [{"op": "move"}]}}]})
    out = parse_onepass_output(raw)
    assert "turtleProgram" not in out["objects"][0]
