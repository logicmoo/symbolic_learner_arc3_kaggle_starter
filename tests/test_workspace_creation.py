from pathlib import Path

import pytest
from fastapi import HTTPException

import workspace_api
from advanced_workflow_engine import AdvancedWorkflowEngine
from workflow_engine import WorkflowEngine


def test_create_workspace_copies_current_default_template(tmp_path: Path, monkeypatch) -> None:
    shared = tmp_path / "shared_library_system"
    default = tmp_path / "default"
    shared.mkdir()
    (default / "workflows").mkdir(parents=True)
    starter = default / "workflows" / "starter.workflow.json"
    starter.write_text('{"kind":"workflow","id":"starter","steps":[]}', encoding="utf-8")
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])

    result = workspace_api.create_workspace({"label": "Vision Lab"})

    created = tmp_path / "vision_lab"
    assert result["templateWorkspaceId"] == "default"
    assert result["workspace"]["id"] == "vision_lab"
    assert (created / "workflows" / starter.name).read_text(encoding="utf-8") == starter.read_text(encoding="utf-8")
    assert result["workspace"]["includes"] == [{"workspaceId": "shared_library_system", "includeInherited": True}]


def test_create_workspace_never_overwrites_an_existing_directory(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "shared_library_system").mkdir()
    (tmp_path / "default").mkdir()
    (tmp_path / "vision_lab").mkdir()
    marker = tmp_path / "vision_lab" / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])

    with pytest.raises(HTTPException) as error:
        workspace_api.create_workspace({"label": "Vision Lab"})

    assert error.value.status_code == 409
    assert marker.read_text(encoding="utf-8") == "keep"


def test_create_workspace_can_copy_another_workspace(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "shared_library_system").mkdir()
    (tmp_path / "default").mkdir()
    source = tmp_path / "vision_library"
    (source / "models").mkdir(parents=True)
    (source / "models" / "vision.model.json").write_text('{"kind":"model","id":"vision"}', encoding="utf-8")
    (source / "workspace.json").write_text('{"label":"Vision Library","includes":[]}', encoding="utf-8")
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])

    result = workspace_api.create_workspace({"label": "Experiment", "templateWorkspaceId": "vision_library"})

    assert result["templateWorkspaceId"] == "vision_library"
    assert (tmp_path / "experiment" / "models" / "vision.model.json").is_file()
    assert result["workspace"]["includes"] == []


def test_workspace_picker_explains_template_and_library_roles() -> None:
    source = (Path(__file__).resolve().parents[1] / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    compact = "".join(source.split())
    assert "Create A New Workspace" in source
    assert "Create Workspace" in source
    assert 'setNewWorkspaceTemplateId("default")' in source
    assert "Workspace template" in source
    assert 'request("/api/workspaces",{method:"POST"' in compact
    assert "EDITABLE STARTER TEMPLATE" in source
    assert "Default is preselected" in source
    assert "independentcopy" in compact


def test_visual_learning_projects_are_disk_backed_and_chooser_discoverable(monkeypatch) -> None:
    workspaces_root = Path(__file__).resolve().parents[1] / "workbench" / "workspaces"
    expected = {
        "visual_learning_from_examples": "Visual Learning from Examples",
        "image_perception_to_recognizable_memory_and_arc3": "Image Perception to Recognizable Memory and ARC3",
        "omegaclaw_microatomspacing": "OmegaClaw MicroAtomSpacing",
        "atom_ant": "Atom.ANT",
    }
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [workspaces_root])
    workspace_api.invalidate_workspace_discovery()

    discovered = {
        item["id"]: item
        for item in workspace_api.discover_workspaces(force=True, include_counts=False)
    }

    for workspace_id, label in expected.items():
        root = workspaces_root / workspace_id
        assert (root / "workspace.json").is_file()
        assert discovered[workspace_id]["label"] == label
        assert Path(discovered[workspace_id]["root"]) == root.resolve()
        expected_library = (
            "shared_library_arc3"
            if workspace_id == "image_perception_to_recognizable_memory_and_arc3"
            else "shared_library_system"
        )
        assert discovered[workspace_id]["includes"] == [
            {"workspaceId": expected_library, "includeInherited": True}
        ]


def test_project_workflows_are_loaded_and_engine_valid(tmp_path: Path) -> None:
    workspaces_root = Path(__file__).resolve().parents[1] / "workbench" / "workspaces"
    expected = {
        "visual_learning_from_examples": "examples_to_visual_memory",
        "image_perception_to_recognizable_memory_and_arc3": "image_to_recognizable_arc3_memory",
        "omegaclaw_microatomspacing": "message_to_microatoms",
        "atom_ant": "atom_ant_symbolic_reasoning",
    }

    engine = AdvancedWorkflowEngine(tmp_path / "project-workflows.db")
    for workspace_id, workflow_id in expected.items():
        workspace = workspace_api._workspace_from_directory(
            workspaces_root / workspace_id,
            include_counts=False,
        )
        local = [
            record for record in workspace_api._load_workflows(workspace)
            if record.get("workspaceId") == workspace_id
        ]
        local_by_id = {record["document"]["id"]: record for record in local}
        assert workflow_id in local_by_id
        assert local_by_id[workflow_id]["source"] == "workspace"
        assert engine.validate(local_by_id[workflow_id]["document"]) == []


def test_atom_ant_symbolic_reasoning_has_bounded_repair_control_flow_and_runs(tmp_path: Path) -> None:
    workspaces_root = Path(__file__).resolve().parents[1] / "workbench" / "workspaces"
    workspace = workspace_api._workspace_from_directory(
        workspaces_root / "atom_ant",
        include_counts=False,
    )
    workflow = next(
        record["document"] for record in workspace_api._load_workflows(workspace)
        if record.get("workspaceId") == "atom_ant"
    )
    steps = {step["id"]: step for step in workflow["steps"]}
    assert list(steps) == [
        "llm_reasoning", "generate_atomese", "assess_initial_coverage",
        "repair_retry_loop", "select_adequate_candidate",
        "assess_final_coverage", "execute_and_report",
    ]
    assert steps["repair_retry_loop"]["foreach"] == {
        "items": "$repair_candidates", "itemPort": "value", "maxItems": 5,
    }
    assert steps["assess_final_coverage"]["dependsOn"] == ["select_adequate_candidate"]

    engine = AdvancedWorkflowEngine(tmp_path / "atom-ant-smoke.db")
    assert engine.validate(workflow) == []
    saved = engine.save_workflow(workflow)
    run = engine.start(saved["id"], {
        "request": {"goal": "Represent a red square in Atomese"},
        "repair_candidates": [
            {},
            {"atomese": "(EvaluationLink (PredicateNode red) (ConceptNode square))"},
        ],
    })

    assert run["status"] == "completed"
    assert run["outputs"]["report"]["adequate"] is True
    assert run["outputs"]["report"]["atomese"].startswith("(EvaluationLink")
    retry_step = next(step for step in run["steps"] if step["stepId"] == "repair_retry_loop")
    assert retry_step["status"] == "completed"
    assert retry_step["attempt"] == 1


def test_omegaclaw_places_weaker_model_memory_controls_after_persistence_and_runs(tmp_path: Path) -> None:
    workspaces_root = Path(__file__).resolve().parents[1] / "workbench" / "workspaces"
    workspace = workspace_api._workspace_from_directory(
        workspaces_root / "omegaclaw_microatomspacing",
        include_counts=False,
    )
    workflow = next(
        record["document"] for record in workspace_api._load_workflows(workspace)
        if record.get("workspaceId") == "omegaclaw_microatomspacing"
    )
    steps = {step["id"]: step for step in workflow["steps"]}

    assert steps["run_weaker_without_memory"]["dependsOn"] == ["persist_microatom_record"]
    assert steps["run_weaker_with_memory"]["dependsOn"] == ["persist_microatom_record"]
    assert steps["compare_weaker_model_controls"]["dependsOn"] == [
        "run_weaker_without_memory", "run_weaker_with_memory",
    ]
    assert steps["report_memory_grounding"]["dependsOn"] == [
        "persist_microatom_record", "compare_weaker_model_controls",
    ]
    assert workflow["outputs"]["groundingEvidence"] == "$memory_grounding_evidence"

    engine = AdvancedWorkflowEngine(tmp_path / "omegaclaw-grounding-smoke.db")
    assert engine.validate(workflow) == []
    saved = engine.save_workflow(workflow)
    run = engine.start(saved["id"], {
        "message": {"text": "Remember the red square"},
        "conversation_context": {"channel": "test"},
        "weaker_model_without_memory": {"withoutMemory": "unknown"},
        "weaker_model_with_memory": {"withMemory": "red square"},
    })
    assert run["status"] == "waiting"
    run = engine.submit_human_input(run["id"], "review_annotations", {
        "annotations": {"approved": True},
    })

    assert run["status"] == "completed"
    assert run["outputs"]["groundingEvidence"]["withoutMemory"] == "unknown"
    assert run["outputs"]["groundingEvidence"]["withMemory"] == "red square"
    assert run["outputs"]["groundingEvidence"]["channel"] == "test"


def test_project_workflows_resolve_shared_operations_and_memory_datatypes() -> None:
    workspaces_root = Path(__file__).resolve().parents[1] / "workbench" / "workspaces"
    workspace_ids = (
        "visual_learning_from_examples",
        "image_perception_to_recognizable_memory_and_arc3",
        "omegaclaw_microatomspacing",
        "atom_ant",
    )
    expected_datatypes = {
        "visual_example_set", "recognizable_memory", "contextual_memory",
        "agent_exchange", "microatom_set", "agent_interaction_memory",
        "llm_reasoning_trace", "atomese_program", "symbolic_coverage_assessment",
        "symbolic_execution_report",
        "weaker_model_control", "memory_grounding_evidence",
    }

    for workspace_id in workspace_ids:
        workspace = workspace_api._workspace_from_directory(
            workspaces_root / workspace_id,
            include_counts=False,
        )
        workflow = next(
            record["document"] for record in workspace_api._load_workflows(workspace)
            if record.get("workspaceId") == workspace_id
            and record["document"]["id"] != "arc3_random_player.outer_loop"
        )
        operation_records = workspace_api._load_operations(workspace)
        operations = {
            record["document"]["id"]: record
            for record in operation_records if record.get("document")
        }
        referenced = {
            step["operation"] for step in workflow["steps"]
            if step.get("operation")
        }
        assert referenced <= operations.keys()
        assert all(operations[operation_id]["source"] == "shared" for operation_id in referenced)

        datatype_records = workspace_api._load_datatypes(workspace)
        datatypes = {
            record["document"]["id"]: record
            for record in datatype_records if record.get("document")
        }
        assert expected_datatypes <= datatypes.keys()
        assert all(datatypes[datatype_id]["source"] == "shared" for datatype_id in expected_datatypes)
