from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from arc3_random_player import (
    RandomArc3Player,
    assess_transition,
    build_game_preview_gallery,
    capture_observation,
    choose_action,
    discover_games,
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
        path.write_bytes(text.encode("ascii"))
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
        self.records.append({"action": action, "data": data})

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
    assert "GALLERY RESOURCE" in playground


def test_learned_random_action_uses_reset_for_new_attempt() -> None:
    proposal = choose_action(
        [{"index": 0, "name": "RESET"}, {"index": 1, "name": "ACTION1"}],
        state="GAME_OVER",
        seed=4,
    )
    assert proposal["action"] == "RESET"


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

    operations = {
        record["document"]["id"]: record["document"]
        for record in workspace_api._load_operations(workspace)
        if record.get("workspaceId") == "arc3_random_player" and record.get("document")
    }
    implementations = {
        record["document"]["id"]: record["document"]
        for record in workspace_api._load_operation_implementations(workspace)
        if record.get("document")
    }
    expected_parents = {
        "arc3_random.discover_games",
        "arc3_random.build_game_preview_gallery",
        "arc3_random.select_game",
        "arc3_random.capture_observation",
        "arc3_random.propose_action",
        "arc3_random.execute_action",
        "arc3_random.assess_transition",
        "arc3_random.update_memory",
        "arc3_random.should_rotate",
        "arc3_random.run_session",
    }
    assert expected_parents <= operations.keys()
    assert operations["arc3_random.propose_action"]["preferredChild"] == (
        "arc3_random.propose_action.python"
    )
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
    assert [step["operation"] for step in workflow["steps"]] == [
        "arc3_random.discover_games",
        "arc3_random.build_game_preview_gallery",
        "gallery.curate_resource",
        "collection.random_list_element",
        "arc3_random.capture_observation",
        "arc3_random.propose_action",
        "arc3_random.execute_action",
        "arc3_random.capture_observation",
        "arc3_random.assess_transition",
        "arc3_random.update_memory",
        "arc3_random.should_rotate",
    ]
    gallery_step = next(step for step in workflow["steps"] if step["id"] == "curate_game_preview_gallery")
    chooser_step = next(step for step in workflow["steps"] if step["id"] == "select_game")
    preview_step = next(step for step in workflow["steps"] if step["id"] == "build_game_preview_gallery")
    assert preview_step["probe"] == {"enabled": False, "required": False, "blocking": False}
    assert gallery_step["dependsOn"] == ["build_game_preview_gallery"]
    assert gallery_step["probe"] == {"enabled": False, "required": False, "blocking": False}
    assert chooser_step["dependsOn"] == ["discover_games"]
    assert chooser_step["inputs"]["items"] == "$games"
    capture_steps = [step for step in workflow["steps"] if step["operation"] == "arc3_random.capture_observation"]
    assert capture_steps
    assert all(step["inputs"]["game"] == "$game" for step in capture_steps)
    executable = materialize_workflow({**workflow, "workspaceId": "arc3_random_player"})
    assert all(step["implementation"] in {"python.callable", "llm.complete"} for step in executable["steps"])
