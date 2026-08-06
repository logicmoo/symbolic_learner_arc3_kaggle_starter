from runtime import DEFAULT_GRID, analyze_grid


def test_default_grid_extracts_real_objects() -> None:
    result = analyze_grid(DEFAULT_GRID)
    assert result["objectCount"] == 2
    assert result["exactMatch"] is True
    assert result["differenceCount"] == 0
    assert {obj["shape"] for obj in result["objects"]} == {"hollow_square", "angle"}
    assert "object(obj_blue_1)." in result["prologFacts"]
    assert "object(obj_red_1)." in result["prologFacts"]


def test_grid_changes_change_backend_result() -> None:
    changed = [row[:] for row in DEFAULT_GRID]
    changed[0][0] = 3
    result = analyze_grid(changed)
    assert result["objectCount"] == 3
    assert any(obj["colorName"] == "green" for obj in result["objects"])


def test_invalid_grid_is_rejected() -> None:
    try:
        analyze_grid([[1, 2], [3]])
    except ValueError as error:
        assert "same width" in str(error)
    else:
        raise AssertionError("ragged grid should fail validation")
