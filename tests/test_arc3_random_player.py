from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from PIL import Image
import pytest
import arc3_random_player as arc3_random_player_module
from resource_relationships import relationship_ids

from arc3_random_player import (
    RandomArc3Player,
    assess_transition,
    build_game_preview_gallery,
    capture_observation,
    choose_action,
    discover_games,
    enumerate_game_controls,
    execute_action,
    filter_unplayed_games,
    initialize_played_games,
    load_game_metta_data,
    pick_random_move_and_execute,
    populate_game_atomspace,
    query_game_metta,
    remember_played_game,
    run_random_arc3_session,
    initialize_selected_game,
    reset_selected_game,
    select_random_game,
    start_selected_game,
    update_learning_memory,
)
from collection_operations import curate_gallery_resource, random_list_element
import workspace_api
from operation_resolution import materialize_workflow


class FakeArcade:
    def get_environments(self):
        return [
            SimpleNamespace(game_id="zz99-version", title="Zed", tags=["test"]),
            SimpleNamespace(game_id="aa00-version", title="Alpha", tags=[]),
        ]


class FakeRunner:
    def __init__(self, game_id, tree_root, **_kwargs):
        self.game_id = game_id
        self.root = Path(tree_root) / game_id
        self.root.mkdir(parents=True, exist_ok=True)
        self.step_count = 0
        self._state = "NOT_PLAYED"
        self.current_node = self._node("initial")
        self.records = []

    def _node(self, text):
        path = self.root / f"{self.step_count}.png"
        color = (sum(text.encode("ascii")) % 255, self.step_count % 255, 96, 255)
        Image.new("RGBA", (8, 8), color).save(path)
        return SimpleNamespace(image_path=path)

    def state_name(self):
        return self._state

    def current_level_label(self):
        return "1"

    def action_table(self):
        return [
            {"index": 0, "name": "RESET", "complex": False},
            {"index": 1, "name": "ACTION1", "complex": False},
        ]

    def step(self, action, data):
        self.step_count += 1
        self._state = "PLAYING"
        self.current_node = self._node(f"{action}:{data}:{self.step_count}")
        self.records.append({"action": action, "data": data, "frame_path": str(self.current_node.image_path)})

    def reset(self, *, clear_history=True):
        self._state = "PLAYING"
        if clear_history:
            self.records.clear()
        self.current_node = self._node("initialized")

    def open(self):
        self._state = "NOT_PLAYED"
        self.records.clear()
        self.current_node = self._node("opened")

    def save_history(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(self.records), encoding="utf-8")
        return Path(path)


def test_discovers_and_normalizes_server_game_catalog() -> None:
    games = discover_games(FakeArcade())
    assert [game["game_id"] for game in games] == ["aa00", "zz99"]
    assert games[1]["server_game_id"] == "zz99-version"


def test_enriches_every_game_with_its_real_first_frame(tmp_path: Path) -> None:
    games = discover_games(FakeArcade())
    gallery = build_game_preview_gallery(games, tmp_path, FakeRunner)
    enriched = gallery["games"]

    assert gallery["kind"] == "game_preview_gallery"
    assert gallery["label"] == "Game Preview Gallery"
    assert gallery["count"] == 2
    assert [game["game_id"] for game in enriched] == ["aa00", "zz99"]
    assert all(Path(game["preview"]["frame_path"]).is_file() for game in enriched)
    assert all(game["preview"]["frame_sha256"] for game in enriched)


def test_reusable_random_list_element_returns_a_real_member() -> None:
    items = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    assert random_list_element(items, seed=7) in items


def test_select_game_random_implementation_delegates_without_immediate_repeat() -> None:
    games = [{"game_id": "a"}, {"game_id": "b"}]
    assert select_random_game(games, previous_game_id="a", seed=7) == {"game_id": "b"}


def test_played_game_tracking_filters_random_selection_until_catalog_exhaustion() -> None:
    games = [{"game_id": "a"}, {"game_id": "b"}, {"game_id": "c"}]
    played = initialize_played_games()
    assert played == []
    played = remember_played_game(played, {"game_id": "b"})
    assert played == ["b"]
    assert [game["game_id"] for game in filter_unplayed_games(games, played)] == ["a", "c"]
    assert [game["game_id"] for game in filter_unplayed_games(games, ["a", "b", "c"])] == ["a", "b", "c"]


def test_selected_game_is_loaded_into_atomspace_started_and_enumerated(tmp_path: Path) -> None:
    source = tmp_path / "design" / "games" / "aa00.game.metta"
    source.parent.mkdir(parents=True)
    source.write_text('(game (id "aa00") (hint "look for symmetry"))', encoding="utf-8")
    game = {"game_id": "aa00", "title": "Alpha", "tags": ["test"]}

    knowledge = query_game_metta(game, tmp_path)
    atomspace = populate_game_atomspace(game, knowledge, tmp_path)
    session = start_selected_game(game, tmp_path, FakeRunner)
    controls = enumerate_game_controls(session)
    result = execute_action(session, {"action": "ACTION1", "data": {}})

    assert knowledge["matches"][0]["path"] == "design/games/aa00.game.metta"
    assert Path(atomspace["path"]).is_file()
    assert "look for symmetry" in Path(atomspace["path"]).read_text(encoding="utf-8")
    assert [control["name"] for control in controls] == ["RESET", "ACTION1"]
    assert result["state"] == "PLAYING"


def test_load_game_metta_data_returns_runnable_session_controls_and_first_screenshot(tmp_path: Path) -> None:
    game = {"game_id": "aa00", "title": "Alpha", "tags": []}

    loaded = load_game_metta_data(game, tmp_path, FakeRunner)

    assert loaded["handle"]
    assert loaded["session"]["handle"] == loaded["handle"]
    assert loaded["state"] == "NOT_PLAYED"
    assert loaded["initial_screenshot"] == loaded["frame_path"]
    assert [control["name"] for control in loaded["controls"]] == ["RESET", "ACTION1"]
    assert Path(loaded["atomspace"]["path"]).is_file()

    initialized = initialize_selected_game(loaded)
    assert initialized["session"]["state"] == "PLAYING"
    assert initialized["result"]["initialized"] is True
    assert initialized["result"]["moves_made"] == 0
    assert Path(initialized["initial_screenshot"]).is_file()


def test_load_game_metta_data_accepts_human_friendly_game_name(tmp_path: Path) -> None:
    loaded = load_game_metta_data("ls20", tmp_path, FakeRunner)

    assert loaded["game_id"] == "ls20"
    assert Path(loaded["initial_screenshot"]).is_file()
    observation = capture_observation(
        loaded["initial_screenshot"], loaded["state"], loaded["level"], "ls20"
    )
    assert observation["game"]["game_id"] == "ls20"


def test_initialization_does_not_depend_on_a_declared_reset_action(tmp_path: Path) -> None:
    class NoResetRunner(FakeRunner):
        def action_table(self):
            return [{"index": 1, "name": "ACTION1", "complex": False}]

    loaded = load_game_metta_data("ls20", tmp_path, NoResetRunner)
    initialized = initialize_selected_game(loaded)

    assert initialized["result"]["initialized"] is True
    assert initialized["result"]["moves_made"] == 0
    assert initialized["session"]["state"] == "PLAYING"
    assert loaded["controls"] == [{"index": 1, "name": "ACTION1", "complex": False}]


def test_reset_operation_resets_current_level_without_becoming_initialization_alias(tmp_path: Path) -> None:
    loaded = load_game_metta_data("ls20", tmp_path, FakeRunner)
    initialized = initialize_selected_game(loaded)
    execute_action(initialized["session"], {"action": "ACTION1", "data": {}})

    reset = reset_selected_game(initialized["session"])

    assert reset["result"]["reset_executed"] is True
    assert reset["result"]["reset_target"] == "level"
    assert reset["result"]["message"] == "Current level restored to its last saved checkpoint"
    assert Path(reset["reset_screenshot"]).is_file()


def test_reset_operation_can_restart_entire_game(tmp_path: Path) -> None:
    loaded = load_game_metta_data("ls20", tmp_path, FakeRunner)
    initialized = initialize_selected_game(loaded)
    execute_action(initialized["session"], {"action": "ACTION1", "data": {}})

    reset = reset_selected_game(initialized["session"], target="game")

    assert reset["result"]["reset_target"] == "game"
    assert reset["result"]["message"] == "Entire game restarted from its first level"
    assert reset["session"]["state"] == "PLAYING"


def test_checkpoint_is_an_alias_for_level_reset(tmp_path: Path) -> None:
    loaded = load_game_metta_data("ls20", tmp_path, FakeRunner)

    reset = reset_selected_game(loaded, target="checkpoint")

    assert reset["result"]["reset_target"] == "level"
    assert reset["result"]["requested_target"] == "checkpoint"


def test_reset_operation_rejects_unknown_target(tmp_path: Path) -> None:
    loaded = load_game_metta_data("ls20", tmp_path, FakeRunner)

    with pytest.raises(ValueError, match="level.*game"):
        reset_selected_game(loaded, target="checkpoint-name-that-does-not-exist")


def test_pick_random_move_executes_and_returns_next_screenshot(tmp_path: Path) -> None:
    game = {"game_id": "aa00", "title": "Alpha", "tags": []}
    loaded = load_game_metta_data(game, tmp_path, FakeRunner)

    initialized = initialize_selected_game(loaded)
    moved = pick_random_move_and_execute(initialized["session"], loaded["controls"], game, seed=7)

    assert moved["proposal"]["action"] == "ACTION1"
    assert moved["result"]["state"] == "PLAYING"
    assert moved["next_screenshot"] == moved["result"]["frame_path"]
    assert Path(moved["next_screenshot"]).is_file()
    assert moved["replay_gallery"]["move_count"] == 1
    assert [entry["title"] for entry in moved["replay_gallery"]["entries"]] == [
        "Initial frame — 0 moves",
        "Move 1 — ACTION1",
    ]
    assert Path(moved["animated_replay"]).is_file()


def test_random_move_stops_before_exceeding_move_limit(tmp_path: Path) -> None:
    game = {"game_id": "aa00", "title": "Alpha", "tags": []}
    loaded = load_game_metta_data(game, tmp_path, FakeRunner)
    initialized = initialize_selected_game(loaded)
    first = pick_random_move_and_execute(initialized["session"], loaded["controls"], game, seed=7, move_limit=1)
    stopped = pick_random_move_and_execute(first["session"], loaded["controls"], game, seed=8, move_limit=1)

    assert first["result"]["move_executed"] is True
    assert stopped["result"]["move_executed"] is False
    assert stopped["result"]["move_limit_reached"] is True
    assert stopped["result"]["moves_made"] == 1
    assert stopped["proposal"] is None


def test_automatic_mode_plays_each_catalog_game_once_and_obeys_move_limit(tmp_path: Path) -> None:
    player = RandomArc3Player(tmp_path, seconds_per_game=100, seed=7, runner_factory=FakeRunner, arcade=FakeArcade(), clock=lambda: 0.0)

    summaries = player.run(max_games=None, max_steps_per_game=2)

    assert len(summaries) == 2
    assert len({summary["game"]["game_id"] for summary in summaries}) == 2
    assert [summary["steps"] for summary in summaries] == [2, 2]


def test_interactive_session_mode_does_not_start_background_game_loop(tmp_path: Path) -> None:
    assert run_random_arc3_session(tmp_path, mode="interactive") == []


def test_automatic_session_restores_defaults_for_blank_optional_limits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class CapturingPlayer:
        def __init__(self, workspace_root: Path, *, seconds_per_game: float, seed: int | None) -> None:
            captured.update(workspace_root=workspace_root, seconds_per_game=seconds_per_game, seed=seed)

        def run(self, *, max_games: int | None, max_steps_per_game: int | None) -> list[dict[str, object]]:
            captured.update(max_games=max_games, max_steps_per_game=max_steps_per_game)
            return []

    monkeypatch.setattr(arc3_random_player_module, "RandomArc3Player", CapturingPlayer)

    assert run_random_arc3_session(tmp_path, seconds_per_game=None, move_limit=None, mode="automatic") == []
    assert captured["seconds_per_game"] == 600.0
    assert captured["max_steps_per_game"] == 10


def test_capture_observation_retains_selected_game_binding() -> None:
    selected_game = {"game_id": "aa00", "title": "Alpha"}

    observation = capture_observation(None, "NOT_PLAYED", 1, selected_game)

    assert observation["game"] == selected_game


def test_generic_gallery_resource_preserves_source_for_humans_and_ai() -> None:
    items = [{"title": "Candidate A", "frame_path": "a.png", "score": 0.8}]
    gallery = curate_gallery_resource(items, label="Candidate Review")

    assert gallery["kind"] == "gallery_resource"
    assert gallery["entries"][0]["image"] == "a.png"
    assert gallery["entries"][0]["source"]["score"] == 0.8
    assert gallery["items"] == items


def test_workbench_exposes_insertable_gallery_and_human_renderer() -> None:
    root = Path(__file__).resolve().parents[1]
    page = (root / "workbench/frontend/src/pages/FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    playground = (root / "workbench/frontend/src/components/OperationPlayground.tsx").read_text(encoding="utf-8")
    assert "INSERT OPERATION AFTER SELECTED STEP" in page
    assert "insertOperationStep" in page
    assert "completedPlaygrounds" in page
    assert 'runtime?.status || (completedPlaygrounds[step.id] ? "completed" : "not run")' in page
    assert "Expand · rerun available" in playground
    assert 'workflowStep?"▶ Run Workflow Step":"▶ Run Operation"' in playground
    assert "operation-execute-step" in playground
    assert "Auto-play all" in page
    assert "selectRelativeStep" in page
    assert "AUTOMATED RUNNER" in page
    assert 'aria-label="Runner move limit"' in page
    assert 'aria-label="Runner seconds per game"' in page
    assert 'aria-label="Runner maximum games"' in page
    assert "GALLERY RESOURCE" in playground


def test_learned_random_action_uses_reset_for_new_attempt() -> None:
    proposal = choose_action(
        [{"index": 0, "name": "RESET"}, {"index": 1, "name": "ACTION1"}],
        state="GAME_OVER",
        seed=4,
    )
    assert proposal["action"] == "RESET"


def test_learned_random_action_avoids_moves_with_no_visible_effect() -> None:
    proposal = choose_action(
        [
            {"index": 1, "name": "ACTION1"},
            {"index": 2, "name": "ACTION2"},
        ],
        state="PLAYING",
        seed=4,
        excluded_actions=["ACTION1"],
    )
    assert proposal["action"] == "ACTION2"


def test_assessment_and_memory_retain_good_and_bad_evidence() -> None:
    good = assess_transition(
        {"state": "PLAYING", "level": 1, "frame_sha256": "a"},
        {"state": "WIN", "level": 1, "frame_sha256": "b"},
    )
    bad = assess_transition(
        {"state": "PLAYING", "level": 1, "frame_sha256": "b"},
        {"state": "GAME_OVER", "level": 1, "frame_sha256": "c"},
    )
    memory = update_learning_memory({}, "aa00", "ACTION1", good)
    memory = update_learning_memory(memory, "aa00", "ACTION1", bad)
    assert memory["games"]["aa00"]["actions"]["ACTION1"]["good"] == 1
    assert memory["games"]["aa00"]["actions"]["ACTION1"]["bad"] == 1


def test_player_persists_catalog_events_history_summary_and_learning(tmp_path: Path) -> None:
    ticks = iter([0.0, 0.0, 0.1, 0.2])
    player = RandomArc3Player(
        tmp_path,
        seconds_per_game=600,
        seed=7,
        runner_factory=FakeRunner,
        arcade=FakeArcade(),
        clock=lambda: next(ticks),
    )

    summaries = player.run(max_games=1, max_steps_per_game=1)

    assert summaries[0]["steps"] == 1
    assert (tmp_path / "runtime" / "states" / "arc3_game_catalog.json").is_file()
    assert (tmp_path / "runtime" / "contexts" / "action_learning_memory.json").is_file()
    assert Path(summaries[0]["history"]).is_file()
    assert Path(summaries[0]["events"]).read_text(encoding="utf-8").count("\n") == 2


def test_random_player_workspace_is_discoverable_and_operation_backed(tmp_path: Path) -> None:
    root = (
        Path(__file__).resolve().parents[1]
        / "workbench"
        / "workspaces"
        / "arc3_random_player"
    )
    workspace = workspace_api._workspace_from_directory(root, include_counts=False)
    assert workspace["id"] == "arc3_random_player"
    assert workspace["label"] == "ARC3 Random Player"
    assert workspace["includes"] == [{"workspaceId": "shared_library_arc3", "includeInherited": True}]
    assert workspace["effectiveIncludes"] == ["shared_library_system", "shared_library_arc3"]
    arc3_library = workspace_api.get_workspace("shared_library_arc3")["workspace"]
    assert arc3_library["label"] == "ARC3 Shared Library"

    effective_operations = {
        record["document"]["id"]
        for record in workspace_api._load_operations(workspace)
        if record.get("document")
    }
    assert {
        "vision.extract_scene_objects",
        "arc3.extract_scene_objects",
        "arc3.explain_object_changes",
        "control.while",
        "control.for_each",
    } <= effective_operations

    effective_prompts = {
        record["document"]["id"]
        for record in workspace_api._load_prompts(workspace)
        if record.get("document")
    }
    assert {
        "transaction_extract_scene_objects",
        "transaction_explain_object_changes",
        "transaction_induce_rules_from_symbolic",
        "arc3_identity_registry",
        "arc3_file_separation",
        "arc3_root_state",
    } <= effective_prompts

    operations = {
        record["document"]["id"]: record["document"]
        for record in workspace_api._load_operations(workspace)
        if record.get("document")
    }
    implementations = {
        record["document"]["id"]: record["document"]
        for record in workspace_api._load_operation_implementations(workspace)
        if record.get("document")
    }
    expected_parents = {
        "arc3_random.discover_games",
        "arc3_random.initialize_played_games",
        "arc3_random.filter_unplayed_games",
        "arc3_random.remember_played_game",
        "arc3_random.run_session",
        "arc3_random.curate_viewable_gallery",
        "arc3_random.select_game",
        "arc3_random.load_game_metta_data",
        "arc3_random.initialize_selected_game",
        "arc3_random.reset_selected_game",
        "arc3_random.pick_random_move_and_execute",
        "arc3_random.capture_observation",
        "arc3_random.propose_action",
        "arc3_random.execute_action",
        "arc3_random.assess_transition",
        "arc3_random.update_memory",
        "arc3_random.should_rotate",
        "arc3_random.seen_enough",
        "arc3_random.run_session",
    }
    assert expected_parents <= operations.keys()
    assert operations["arc3_random.propose_action"]["preferredSpecialization"] == (
        "arc3_random.propose_action.python"
    )
    assert operations["arc3_random.select_game"]["preferredSpecialization"] == (
        "arc3_random.select_game.random"
    )
    assert implementations["arc3_random.select_game.random"]["delegatesTo"] == (
        "collection.random_list_element"
    )
    assert relationship_ids(operations["arc3_random.select_game"]["specializations"]) == [
        "arc3_random.select_game.random",
        "arc3_random.select_game.manual",
    ]
    assert implementations["arc3_random.select_game.manual"]["implementation"] == "human.await_input"
    assert implementations["arc3_random.select_game.manual"]["parameters"]["form"]["game"] == {
        "type": "Text",
        "prompt": "Enter the ARC game name or ID",
    }
    assert {
        implementations["arc3_random.propose_action.python"]["implementation"],
        implementations["arc3_random.propose_action.llm"]["implementation"],
    } == {"python.callable", "llm.complete"}

    prompts = {
        record["document"]["id"]
        for record in workspace_api._load_prompts(workspace)
        if record.get("workspaceId") == "arc3_random_player" and record.get("document")
    }
    assert {
        "arc3_random.select_game",
        "arc3_random.propose_action",
        "arc3_random.critique_transition",
    } <= prompts

    workflow = next(
        record["document"]
        for record in workspace_api._load_workflows(workspace)
        if record.get("workspaceId") == "arc3_random_player"
    )
    assert workflow["generation"] == {
        "operation": "workflow.populate_from_english",
        "englishSpecificationPrompt": "arc3_random_player.english_workflow_specification",
        "englishDescriptionPath": "docs/ARC3_RANDOM_PLAYER_WORKFLOW_ENGLISH.md",
        "operationCategories": ["workflow-language"],
        "preflightRequired": True,
    }
    assert [step["operation"] for step in workflow["steps"]] == [
        "echo.value",
        "arc3_random.discover_games",
        "arc3_random.filter_unplayed_games",
        "arc3_random.curate_viewable_gallery",
        "arc3_random.select_game",
        "arc3_random.remember_played_game",
        "arc3_random.load_game_metta_data",
        "arc3_random.curate_viewable_gallery",
        "arc3_random.initialize_selected_game",
        "arc3_random.pick_random_move_and_execute",
        "arc3_random.capture_observation",
        "arc3_random.assess_transition",
        "arc3_random.update_memory",
        "arc3_random.seen_enough",
        "arc3_random.filter_unplayed_games",
        "arc3_random.select_game",
        "arc3_random.remember_played_game",
        "arc3_random.run_session",
    ]
    initialize_played_games_step = workflow["steps"][0]
    assert initialize_played_games_step["inputs"] == {"played_games": []}
    assert initialize_played_games_step["outputs"] == ["played_games"]
    gallery_step = next(step for step in workflow["steps"] if step["id"] == "curate_viewable_gallery")
    chooser_step = next(step for step in workflow["steps"] if step["id"] == "select_game")
    assert gallery_step["probe"] == {"enabled": False, "required": False, "blocking": False}
    assert gallery_step["dependsOn"] == ["filter_unplayed_games"]
    assert gallery_step["inputs"]["games"] == "$unplayed_games"
    assert chooser_step["dependsOn"] == ["filter_unplayed_games"]
    assert chooser_step["inputs"]["games"] == "$unplayed_games"
    load_step = next(step for step in workflow["steps"] if step["id"] == "load_game_metta_data")
    assert load_step["dependsOn"] == ["select_game"]
    assert load_step["outputs"]["initial_screenshot"] == "initial_screenshot"
    selected_gallery = next(step for step in workflow["steps"] if step["id"] == "curate_selected_game_gallery")
    assert selected_gallery["dependsOn"] == ["load_game_metta_data"]
    assert selected_gallery["operation"] == "arc3_random.curate_viewable_gallery"
    move_step = next(step for step in workflow["steps"] if step["id"] == "pick_random_move_and_execute")
    initialize_step = next(step for step in workflow["steps"] if step["id"] == "initialize_selected_game")
    assert initialize_step["operation"] == "arc3_random.initialize_selected_game"
    assert initialize_step["outputs"]["initial_screenshot"] == "initial_game_screenshot"
    assert move_step["dependsOn"] == ["initialize_selected_game"]
    assert move_step["inputs"]["session"] == "$initialized_game_session"
    assert move_step["inputs"]["move_limit"] == "$move_limit"
    assert move_step["outputs"]["next_screenshot"] == "next_screenshot"
    capture_after = next(step for step in workflow["steps"] if step["id"] == "capture_after")
    assert capture_after["inputs"]["frame_path"] == "$next_screenshot"
    ask_step = next(step for step in workflow["steps"] if step["id"] == "ask_if_seen_enough")
    assert ask_step["operation"] == "arc3_random.seen_enough"
    assert ask_step["outputs"]["rotate"] == "rotate"
    next_step = next(step for step in workflow["steps"] if step["id"] == "select_next_game")
    assert next_step["implementationVariant"] == "arc3_random.select_game.random"
    assert next_step["inputs"]["games"] == "$games_for_next_selection"
    assert workflow["outputs"]["played_games"] == "$played_games_after_next_selection"
    automatic_step = next(step for step in workflow["steps"] if step["id"] == "play_all_remaining_games_automatically")
    assert automatic_step["operation"] == "arc3_random.run_session"
    assert automatic_step["dependsOn"] == ["filter_unplayed_games"]
    assert automatic_step["while"] == [
        {
            "operation": "control.while",
            "condition": "$unplayed_games",
            "operator": "not_empty",
            "maxIterations": 100,
        },
        {
            "operation": "control.while",
            "condition": "$elapsed_game_seconds",
            "operator": "less_than",
            "conditionPort": "$seconds_per_game",
            "maxIterations": 1000,
        },
    ]
    assert automatic_step["inputs"]["mode"] == "$mode"
    assert automatic_step["inputs"]["move_limit"] == "$move_limit"
    executable = materialize_workflow({**workflow, "workspaceId": "arc3_random_player"})
    assert all(
        step["implementation"] in {"echo.value", "python.callable", "llm.complete", "human.await_input"}
        for step in executable["steps"]
    )
