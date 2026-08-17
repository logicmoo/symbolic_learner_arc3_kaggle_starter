from object_memory import (
    GridAdapter,
    PHASE2_SCHEMA_VERSION,
    PythonProvider,
    normalize_grid_structure,
)
from workbench.server.runtime import DEFAULT_GRID, analyze_grid


def test_grid_adapter_wraps_existing_extractor_with_exact_phase1_provenance() -> None:
    provider = PythonProvider({})
    adapter = GridAdapter(analyze_grid, provider)
    batch = adapter.normalize(
        observation_id="arc3-level-1-step-4",
        grid=DEFAULT_GRID,
        action_tree_node="nodes/00004",
        artifact_uri="nodes/00004/state.json",
    )

    assert batch.observation.source_modality == "logical_grid"
    assert batch.observation.dimensions == (5, 8)
    assert batch.observation.action_tree_node == "nodes/00004"
    assert batch.observation.schema_version == PHASE2_SCHEMA_VERSION
    assert batch.observation.artifacts[0].content_hash == f"sha256:{analyze_grid(DEFAULT_GRID)['sha256']}"
    assert {item.candidate_id for item in batch.candidates} == {
        "obj_blue_1",
        "obj_red_1",
    }
    assert all(item.provider is provider for item in batch.candidates)
    assert adapter.candidate_detail("obj_blue_1")["shape"] == "hollow_square"
    assert "turtleProgram" in adapter.candidate_detail("obj_red_1")


def test_grid_adapter_generic_entrypoint_accepts_phase1_observation_envelope() -> None:
    adapter = GridAdapter(analyze_grid, PythonProvider({}))
    candidates = tuple(
        adapter.propose_candidates(
            {
                "observation_id": "observation-8",
                "grid": DEFAULT_GRID,
                "action_tree_node": "nodes/00008",
                "artifact_uri": "nodes/00008/state.json",
            }
        )
    )

    assert len(candidates) == 2
    assert all(item.observation_id == "observation-8" for item in candidates)
    assert all("nodes/00008" in item.provenance for item in candidates)


def test_grid_structure_normalizes_enclosures_bars_and_compound_parts() -> None:
    normalized = normalize_grid_structure(
        {
            "cells": [[4, 5], [5, 5], [4, 6], [8, 8]],
            "bounds": [4, 5, 5, 4],
            "geometry": {
                "width": 5,
                "height": 4,
                "boundaryCells": [[4, 5], [5, 5], [4, 6], [8, 8]],
            },
            "topology": {
                "connectedComponents": 2,
                "holeCount": 1,
                "holes": [[[5, 6]]],
            },
            "colorName": "blue",
            "shape": "compound",
            "pixelCount": 4,
            "lineThickness": 1,
            "partRoles": {"body": 0, "detached_marker": 1},
            "relationships": [{"target": "marker", "relation": "left_of"}],
        }
    )

    assert normalized["geometry"]["cells"] == (
        (0, 0),
        (0, 1),
        (1, 0),
        (4, 3),
    )
    assert normalized["geometry"]["horizontal_bars"] == (((0, 0), (1, 0)),)
    assert normalized["geometry"]["vertical_bars"] == (((0, 0), (0, 1)),)
    assert normalized["orientation"] is not None
    assert normalized["topology"]["connected_components"] == 2
    assert normalized["topology"]["compound"] is True
    assert len(normalized["topology"]["compound_parts"]) == 2
    assert tuple(item["role"] for item in normalized["topology"]["part_roles"]) == (
        "body",
        "detached_marker",
    )
    assert normalized["topology"]["holes"] == (((1, 1),),)
    assert normalized["topology"]["enclosures"] == (((1, 1),),)
    assert normalized["properties"] == {
        "color": "blue",
        "shape": "compound",
        "pixel_count": 4,
    }
    assert normalized["relationships"] == (
        {"target": "marker", "relation": "left_of"},
    )
