from workbench.server.runtime import analyze_grid


def test_hollow_object_exposes_exact_hole_boundary_and_topology() -> None:
    grid = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    obj = analyze_grid(grid)["objects"][0]

    assert obj["shape"] == "hollow_rectangle"
    assert obj["topology"]["connectedComponents"] == 1
    assert obj["topology"]["holeCount"] == 1
    assert len(obj["topology"]["holes"][0]) == 6
    assert len(obj["geometry"]["boundaryCells"]) == obj["pixelCount"]


def test_thick_line_and_inter_object_relationships_are_normalized() -> None:
    grid = [
        [2, 2, 0, 0, 3],
        [2, 2, 0, 0, 3],
        [2, 2, 0, 0, 3],
        [2, 2, 0, 0, 0],
    ]
    result = analyze_grid(grid)
    red = next(item for item in result["objects"] if item["colorName"] == "red")
    green = next(item for item in result["objects"] if item["colorName"] == "green")

    assert red["lineThickness"] == 2
    assert red["geometry"] == {
        **red["geometry"],
        "minX": 0,
        "minY": 0,
        "maxX": 1,
        "maxY": 3,
        "width": 2,
        "height": 4,
    }
    assert {item["relation"] for item in red["relationships"]} >= {"left_of"}
    assert {item["relation"] for item in green["relationships"]} >= {"right_of"}
