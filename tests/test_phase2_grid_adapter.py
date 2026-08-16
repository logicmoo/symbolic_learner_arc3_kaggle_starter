from object_memory import GridAdapter, PHASE2_SCHEMA_VERSION, PythonProvider
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
