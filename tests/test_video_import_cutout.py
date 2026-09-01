import base64
import io
import json
import threading
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw
import pytest

import video_import_api


def test_concurrent_scene_and_extraction_metadata_updates_are_merged(tmp_path: Path) -> None:
    video_path = tmp_path / "video.mp4"
    video_path.write_bytes(b"video")
    (tmp_path / "video.json").write_text('{"title":"source"}', encoding="utf-8")
    barrier = threading.Barrier(3)

    def update(payload: dict) -> None:
        barrier.wait()
        video_import_api._merge_video_meta(video_path, payload)

    scene_thread = threading.Thread(target=update, args=({"scenes": [{"atSeconds": 1.0}], "lastScenes": {"count": 1}},))
    extract_thread = threading.Thread(target=update, args=({"lastExtract": {"count": 4}},))
    scene_thread.start()
    extract_thread.start()
    barrier.wait()
    scene_thread.join()
    extract_thread.join()

    saved = json.loads((tmp_path / "video.json").read_text(encoding="utf-8"))
    assert saved["title"] == "source"
    assert saved["lastScenes"] == {"count": 1}
    assert saved["lastExtract"] == {"count": 4}


def test_video_caption_webvtt_round_trip() -> None:
    cues = [
        {"start": 1.25, "end": 3.5, "text": "Hello world"},
        {"start": 65.0, "end": 67.125, "text": "Second cue"},
    ]
    rendered = video_import_api._captions_to_webvtt(cues)
    assert "00:00:01.250 --> 00:00:03.500" in rendered
    assert video_import_api._parse_webvtt(rendered) == cues


def test_page_state_compacts_cached_debug_image_payloads() -> None:
    state = {
        "modelResponseCache": {
            "key": {
                "payload": {
                    "text": "answer",
                    "latencyMs": 12,
                    "debugExecution": {"request": {"image": "data:image/png;base64,large"}},
                    "response": {"large": "payload"},
                }
            }
        }
    }

    compacted = video_import_api._compact_page_state(state)

    assert compacted["modelResponseCache"]["key"]["payload"] == {
        "text": "answer",
        "latencyMs": 12,
    }


def test_page_state_shards_heavy_collections_and_hydrates_them(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(video_import_api, "_workspace_root", lambda _workspace_id: tmp_path)
    state = {
        "v": 1,
        "selectedPath": "data/video.mp4",
        "memberInventories": [{"id": "inventory"}],
        "modelResponseCache": {"key": {"payload": {"text": "answer"}}},
    }

    saved = video_import_api._save_page_state_payload(
        {"workspaceId": "workspace", "state": state}
    )

    manifest = json.loads(Path(saved["path"]).read_text(encoding="utf-8"))
    assert Path(saved["path"]).parent == tmp_path / "data" / "video_import"
    assert "memberInventories" not in manifest
    assert "modelResponseCache" not in manifest
    assert manifest["stateShards"] == video_import_api._PAGE_STATE_SHARDS
    restored = video_import_api.get_page_state("workspace")["state"]
    assert restored == state


def test_image_edit_falls_back_to_declared_backend_when_model_resolution_is_blocked(
    tmp_path: Path,
    monkeypatch,
) -> None:
    generated_buffer = io.BytesIO()
    Image.new("RGB", (16, 16), "green").save(generated_buffer, format="PNG")
    encoded = base64.b64encode(generated_buffer.getvalue()).decode("ascii")
    monkeypatch.setattr(
        video_import_api,
        "_model_execution_parameters",
        lambda *_: {"model": "resource-model"},
    )
    monkeypatch.setattr(
        video_import_api,
        "resolve_model_records",
        lambda *_: [{
            "document": {
                "id": "resource-model",
                "model": "provider-model",
                "discovery": {"backendId": "provider"},
            },
            "error": "canonical relationship migration is incomplete",
        }],
    )
    monkeypatch.setattr(
        video_import_api,
        "load_workspace_backend_records",
        lambda *_: [{
            "document": {
                "id": "provider",
                "configuration": {"baseUrl": "http://provider.test/v1", "timeoutSeconds": 10},
            },
        }],
    )

    class Response:
        def __enter__(self): return self
        def __exit__(self, *_args): return None
        def read(self): return json.dumps({"data": [{"source": "worker", "b64_json": encoded}]}).encode()

    def open_request(request, **_kwargs):
        assert request.full_url == "http://provider.test/v1/images/edits"
        assert request.headers["Content-type"].startswith("multipart/form-data; boundary=")
        return Response()

    monkeypatch.setattr(video_import_api.urllib.request, "urlopen", open_request)
    source = Image.new("RGB", (16, 16), "white")
    mask = Image.new("RGBA", (16, 16), (255, 255, 255, 0))
    result, metadata = video_import_api._try_model_image_edit(
        tmp_path,
        "resource-model",
        source,
        mask,
        "reconstruct background",
    )

    assert result is not None
    assert result.getpixel((8, 8)) == (0, 128, 0)
    assert metadata["renderer"] == "model_image_edit"
    assert metadata["remoteModel"] == "provider-model"


def test_scene_extraction_targets_support_scene_windows_and_skips() -> None:
    assert video_import_api._scene_marker_limit(None) is None
    assert video_import_api._scene_marker_limit(0) is None
    assert video_import_api._scene_marker_limit(120) == 120
    assert video_import_api._scene_marker_limit(20_000) == 10_000
    assert video_import_api._scene_detection_float(
        None,
        default=4,
        minimum=0.25,
        maximum=30,
        label="samplesPerSecond",
    ) == 4
    with pytest.raises(video_import_api.HTTPException, match="between 0.25 and 30"):
        video_import_api._scene_detection_float(
            31,
            default=4,
            minimum=0.25,
            maximum=30,
            label="samplesPerSecond",
        )

    targets = video_import_api._scene_extraction_targets(
        [10, 20, 30, 40, 50],
        duration=60,
        start_seconds=0,
        end_seconds=55,
        start_scene=2,
        end_scene=None,
        skip_scenes=1,
        per_scene=1,
        scene_offset=0.5,
        max_frames=20,
    )
    assert targets == [(10.5, 2), (30.5, 4), (50.5, 6)]

    short_window = video_import_api._scene_extraction_targets(
        [10, 20, 30, 40, 50],
        duration=60,
        start_seconds=24,
        end_seconds=35,
        start_scene=2,
        end_scene=6,
        skip_scenes=1,
        per_scene=1,
        scene_offset=0.5,
        max_frames=20,
    )
    assert short_window == [(30.5, 4)]


def test_planner_number_preview_and_outliner_trace_verification(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(video_import_api, "_workspace_root", lambda _workspace_id: tmp_path)
    source_path = tmp_path / "data" / "input.png"
    source_path.parent.mkdir(parents=True)
    Image.new("RGB", (100, 100), "white").save(source_path)

    planner = video_import_api.planner_visualization(
        {
            "workspaceId": "test",
            "image": "data/input.png",
            "labels": [
                {"object": "square", "number": 1, "point": [50, 50]},
                {"object": "corner", "number": 2, "point": [10, 10]},
            ],
        }
    )
    assert planner["labels"][0]["number"] == 1
    assert (tmp_path / planner["visualizationImage"]).is_file()
    assert (tmp_path / planner["provenance"]).is_file()

    polygon = [[20, 20], [80, 20], [80, 80], [20, 80]]
    trace = [
        {"op": "move", "x": 202, "y": 202},
        {"op": "line", "x": 808, "y": 202},
        {"op": "line", "x": 808, "y": 808},
        {"op": "line", "x": 202, "y": 808},
        {"op": "line", "x": 202, "y": 202},
    ]
    verification = video_import_api.outline_verification(
        {
            "workspaceId": "test",
            "image": "data/input.png",
            "name": "square",
            "polygons": [polygon],
            "holes": [],
            "traceTurtle": trace,
            "plannerNumber": 1,
        }
    )
    assert verification["verified"] is True
    assert verification["traceAgreement"] >= 0.7
    assert verification["boundaryCoverage"] >= 0.45
    assert (tmp_path / verification["verificationImage"]).is_file()

    cut = video_import_api.member_cut(
        {
            "workspaceId": "test",
            "image": "data/input.png",
            "name": "square",
            "step": 1,
            "polygons": [polygon],
            "outlineSourceImage": "data/input.png",
            "outlineSourceDimensions": {"width": 100, "height": 100},
            "outlineVerificationImage": verification["verificationImage"],
            "outlineGeometryHash": verification["geometryHash"],
        }
    )
    assert cut["outlineAlignment"]["traceVerified"] is True
    assert cut["outlineAlignment"]["geometryHash"] == verification["geometryHash"]

    with pytest.raises(video_import_api.HTTPException, match="does not agree"):
        video_import_api.outline_verification(
            {
                "workspaceId": "test",
                "image": "data/input.png",
                "name": "wrong",
                "polygons": [polygon],
                "traceTurtle": [
                    {"op": "move", "x": 400, "y": 400},
                    {"op": "line", "x": 500, "y": 400},
                    {"op": "line", "x": 500, "y": 500},
                ],
            }
        )


def test_standard_stream_urls_and_arc_playback_import_include_move_prefix(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(video_import_api, "_workspace_root", lambda _workspace_id: tmp_path)
    urls = video_import_api._stream_router_urls("media.example.test", "My Stream")
    assert urls["publishWhip"] == "http://media.example.test:8889/my-stream/whip"
    assert urls["publishRtmp"] == "rtmp://media.example.test:1935/my-stream"
    assert urls["watchWhep"] == "http://media.example.test:8889/my-stream/whep"
    assert urls["watchHls"] == "http://media.example.test:8888/my-stream/index.m3u8"
    assert video_import_api._stream_source_url(urls["watchHls"]) == urls["watchHls"]
    with pytest.raises(video_import_api.HTTPException, match="sourceUrl must use"):
        video_import_api._stream_source_url("file:///private/video.mp4")

    recording = tmp_path / "data" / "Recordings" / "game-one" / "saved_001"
    (recording / "0").mkdir(parents=True)
    (recording / "1").mkdir()
    moves = [
        {"index": 0, "action": "ACTION1", "data": {"x": 1}},
        {"index": 1, "action": "ACTION2", "data": {"y": 2}},
    ]
    (recording / "recording.json").write_text(
        json.dumps({"game_id": "game-one", "level": 1, "moves": moves}),
        encoding="utf-8",
    )
    Image.new("RGB", (12, 12), "black").save(recording / "image.png")
    for index, color in enumerate(("red", "blue")):
        Image.new("RGB", (12, 12), color).save(recording / str(index) / "image.png")
        (recording / str(index) / "state.json").write_text(
            json.dumps(
                {
                    "incoming_action": moves[index]["action"],
                    "action_data": moves[index]["data"],
                    "action_path": [str(value) for value in range(index + 1)],
                    "state": "NOT_FINISHED",
                    "level": 1,
                }
            ),
            encoding="utf-8",
        )
    curated = tmp_path / "data" / "curated_game"
    curated.mkdir()
    Image.new("RGB", (10, 10), "green").save(curated / "frame_10.png")
    Image.new("RGB", (10, 10), "yellow").save(curated / "frame_2.png")

    listing = video_import_api.list_arc_recordings("test")["recordings"]
    assert listing[0]["frames"] == 3
    assert listing[0]["path"].startswith("data/arc3_games/recordings/")
    imported = video_import_api.import_arc_recording(
        {
            "workspaceId": "test",
            "recording": listing[0]["path"],
        }
    )
    assert len(imported["frames"]) == 3
    assert imported["frames"][0]["path"].startswith("data/vision_frames/")
    root_provenance = json.loads(
        (tmp_path / imported["frames"][0]["provenance"]).read_text(encoding="utf-8")
    )
    first_move_provenance = json.loads(
        (tmp_path / imported["frames"][1]["provenance"]).read_text(encoding="utf-8")
    )
    second_move_provenance = json.loads(
        (tmp_path / imported["frames"][2]["provenance"]).read_text(encoding="utf-8")
    )
    assert root_provenance["source"]["moveList"] == []
    assert first_move_provenance["source"]["moveList"] == moves[:1]
    assert second_move_provenance["source"]["moveList"] == moves
    assert second_move_provenance["source"]["incomingAction"] == "ACTION2"
    curated_sources = video_import_api.list_curated_image_sources("test")["sources"]
    assert curated_sources == [
        {
            "path": "data/arc3_games/curated/curated_game",
            "label": "curated_game",
            "frames": 2,
            "preview": "data/arc3_games/curated/curated_game/frame_2.png",
        }
    ]
    curated_import = video_import_api.import_curated_image_source(
        {"workspaceId": "test", "source": curated_sources[0]["path"]}
    )
    assert len(curated_import["frames"]) == 2
    assert curated_import["frames"][0]["path"].startswith("data/vision_frames/")

    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w") as archive:
        for name, color in (("frames/002.png", "blue"), ("frames/001.png", "red")):
            image_buffer = io.BytesIO()
            Image.new("RGB", (8, 8), color).save(image_buffer, format="PNG")
            archive.writestr(name, image_buffer.getvalue())
    archive_buffer.seek(0)
    archive_import = video_import_api._import_image_archive(
        "test",
        "sequence.zip",
        archive_buffer,
    )
    assert len(archive_import["frames"]) == 2
    assert archive_import["frames"][0]["path"].startswith("data/vision_frames/")
    archive_provenance = json.loads(
        (tmp_path / archive_import["frames"][0]["provenance"]).read_text(encoding="utf-8")
    )
    assert archive_provenance["source"]["archiveName"] == "sequence.zip"
    assert archive_provenance["source"]["archiveEntry"] == "frames/001.png"


def test_turtle_leaf_program_is_safely_rendered_and_linked_to_provenance(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(video_import_api, "_workspace_root", lambda _: tmp_path)
    source_path = tmp_path / "data" / "leaf.png"
    source_path.parent.mkdir(parents=True)
    Image.new("RGBA", (40, 20), (0, 0, 0, 0)).save(source_path)

    result = video_import_api.turtle_render(
        {
            "workspaceId": "test",
            "sourceImage": "data/leaf.png",
            "subjectName": "red leaf",
            "modelId": "test-model",
            "prompt": "draw it",
            "program": {
                "version": 1,
                "background": "transparent",
                "commands": [
                    {"op": "rectangle", "box": [100, 100, 900, 900], "fill": "#ff0000"},
                    {"op": "move", "x": 100, "y": 500},
                    {"op": "line", "x": 900, "y": 500, "color": "#ffffff", "width": 3},
                ],
            },
        }
    )

    assert result["programPath"] == "data/leaf.turtle.json"
    assert result["renderedImage"] == "data/leaf.turtle.png"
    rendered = Image.open(tmp_path / result["renderedImage"]).convert("RGBA")
    assert rendered.size == (40, 20)
    assert rendered.getpixel((20, 10))[3] == 255
    program = json.loads((tmp_path / result["programPath"]).read_text(encoding="utf-8"))
    assert program["kind"] == "turtle_program"
    assert program["sourceImage"] == "data/leaf.png"
    source_provenance = json.loads((tmp_path / "data" / "leaf.provenance.json").read_text(encoding="utf-8"))
    assert source_provenance["terminal"]["renderedImage"] == result["renderedImage"]
    render_provenance = json.loads((tmp_path / result["provenance"]).read_text(encoding="utf-8"))
    assert render_provenance["operation"] == "render_turtle_program"
    assert render_provenance["parent"]["image"] == "data/leaf.png"


def test_member_cut_preserves_precise_multipart_alpha_and_holes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(video_import_api, "_workspace_root", lambda _: tmp_path)
    image_path = tmp_path / "data" / "input.png"
    image_path.parent.mkdir(parents=True)
    image = Image.new("RGB", (40, 40), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((5, 5, 20, 30), fill="red")
    draw.rectangle((25, 10, 35, 20), fill="blue")
    image.save(image_path)

    result = video_import_api.member_cut(
        {
            "workspaceId": "test",
            "image": "data/input.png",
            "name": "multipart",
            "step": 1,
            "fill": "hole",
            "polygons": [
                [[5, 5], [20, 5], [20, 30], [5, 30]],
                [[25, 10], [35, 10], [35, 20], [25, 20]],
            ],
            "holes": [[[10, 10], [15, 10], [15, 15], [10, 15]]],
        }
    )

    assert result["cutout"].endswith(".png")
    assert result["polygonCount"] == 2
    assert result["holeCount"] == 1
    assert result["maskScale"] == 4
    assert result["nextPassImage"].endswith(".png")
    assert result["nextPassScale"] > 1
    assert result["nextPassPadding"] >= 16
    assert result["cutoutProvenance"].endswith(".provenance.json")
    assert result["nextPassProvenance"].endswith(".provenance.json")
    assert result["sceneProvenance"].endswith(".provenance.json")

    cutout_provenance = json.loads((tmp_path / result["cutoutProvenance"]).read_text(encoding="utf-8"))
    assert cutout_provenance["operation"] == "extract_object_cutout"
    assert cutout_provenance["root"]["firstSeenImage"] == "data/input.png"
    assert cutout_provenance["originalDimensions"] == {"width": 40, "height": 40}
    assert cutout_provenance["parent"]["image"] == "data/input.png"
    assert cutout_provenance["transform"]["cropBox"] == result["box"]

    next_pass_provenance = json.loads((tmp_path / result["nextPassProvenance"]).read_text(encoding="utf-8"))
    assert next_pass_provenance["parent"]["image"] == result["cutout"]
    assert next_pass_provenance["transform"]["sourceDimensions"] == {
        "width": cutout_provenance["dimensions"]["width"],
        "height": cutout_provenance["dimensions"]["height"],
    }
    assert next_pass_provenance["transform"]["scale"] == result["nextPassScale"]
    assert len(next_pass_provenance["lineage"]) == 3

    source_provenance = tmp_path / "data" / "input.provenance.json"
    assert source_provenance.is_file()

    x0, y0, _, _ = result["box"]
    cutout = Image.open(tmp_path / result["cutout"]).convert("RGBA")
    alpha = cutout.getchannel("A")
    assert alpha.getpixel((7 - x0, 7 - y0)) >= 250
    assert alpha.getpixel((12 - x0, 12 - y0)) <= 5
    assert alpha.getpixel((30 - x0, 15 - y0)) >= 250
    assert any(0 < value < 255 for value in alpha.getdata())
    next_pass = Image.open(tmp_path / result["nextPassImage"]).convert("RGBA")
    assert max(next_pass.size) > 640

    scene = Image.open(tmp_path / result["scene"]).convert("RGBA")
    assert scene.getpixel((7, 7))[3] == 0
    assert scene.getpixel((12, 12))[3] == 255

    compact = video_import_api.member_cut(
        {
            "workspaceId": "test",
            "image": "data/input.png",
            "name": "compact",
            "step": 2,
            "fill": "hole",
            "box": [5, 5, 20, 30],
            "enlargeForNextPass": False,
        }
    )
    assert compact["nextPassImage"] == compact["cutout"]
    assert compact["nextPassScale"] == 1
    assert compact["nextPassPadding"] == 0
    assert compact["enlargedForNextPass"] is False

    inpainted = video_import_api.member_cut(
        {
            "workspaceId": "test",
            "image": "data/input.png",
            "name": "red rectangle",
            "step": 3,
            "fill": "inpaint",
            "box": [5, 5, 20, 30],
            "outlineSourceImage": "data/input.png",
            "outlineSourceDimensions": {"width": 40, "height": 40},
            "fillInstructions": {
                "description": "continue the surrounding white background",
                "colors": ["#ffffff"],
            },
        }
    )
    inpainted_scene = Image.open(tmp_path / inpainted["scene"]).convert("RGB")
    assert all(channel >= 240 for channel in inpainted_scene.getpixel((10, 15)))
    assert inpainted["fillInstructions"]["description"] == "continue the surrounding white background"
    assert inpainted["outlineAlignment"]["verified"] is True
    inpainted_provenance = json.loads((tmp_path / inpainted["sceneProvenance"]).read_text(encoding="utf-8"))
    assert inpainted_provenance["transform"]["fill"] == "inpaint"
    assert inpainted_provenance["transform"]["fillInstructions"]["colors"] == ["#ffffff"]

    monkeypatch.setattr(
        video_import_api,
        "_try_model_image_edit",
        lambda *_: (
            Image.new("RGB", (40, 40), "#00ff00"),
            {
                "renderer": "model_image_edit",
                "modelId": "generic-image-model",
                "source": "provider",
                "artifact": {"mime_type": "image/png"},
            },
        ),
    )
    generated = video_import_api.member_cut(
        {
            "workspaceId": "test",
            "image": "data/input.png",
            "name": "generated background",
            "step": 4,
            "fill": "inpaint",
            "box": [5, 5, 20, 30],
            "imageGenerationModelId": "generic-image-model",
            "fillInstructions": {"description": "continue the scene"},
        }
    )
    generated_scene = Image.open(tmp_path / generated["scene"]).convert("RGB")
    assert generated_scene.getpixel((10, 15)) == (0, 255, 0)
    assert generated_scene.getpixel((0, 0)) == (255, 255, 255)
    assert generated["fillRenderer"] == "model_image_edit"
    assert generated["imageGeneration"]["modelId"] == "generic-image-model"
    generated_provenance = json.loads((tmp_path / generated["sceneProvenance"]).read_text(encoding="utf-8"))
    assert generated_provenance["transform"]["imageGeneration"]["renderer"] == "model_image_edit"

    descendant = video_import_api.member_cut(
        {
            "workspaceId": "test",
            "image": inpainted["scene"],
            "name": "blue rectangle",
            "step": 5,
            "fill": "median",
            "box": [25, 10, 35, 20],
            "outlineSourceImage": "data/input.png",
            "outlineSourceDimensions": {"width": 40, "height": 40},
        }
    )
    assert descendant["outlineAlignment"]["verified"] is True
    assert descendant["outlineAlignment"]["outlineSourceImage"] == "data/input.png"

    wrong_size_path = tmp_path / "data" / "wrong-size.png"
    Image.new("RGB", (20, 20), "white").save(wrong_size_path)
    with pytest.raises(video_import_api.HTTPException, match="Outliner coordinate space is 20x20") as mismatch:
        video_import_api.member_cut(
            {
                "workspaceId": "test",
                "image": "data/input.png",
                "name": "misaligned",
                "step": 6,
                "box": [5, 5, 20, 20],
                "outlineSourceImage": "data/wrong-size.png",
                "outlineSourceDimensions": {"width": 20, "height": 20},
            }
        )
    assert mismatch.value.status_code == 409

    with pytest.raises(video_import_api.HTTPException, match="outside the 40x40 Outliner coordinate space") as outside:
        video_import_api.member_cut(
            {
                "workspaceId": "test",
                "image": "data/input.png",
                "name": "outside",
                "step": 7,
                "polygon": [[5, 5], [41, 5], [5, 20]],
                "outlineSourceImage": "data/input.png",
                "outlineSourceDimensions": {"width": 40, "height": 40},
            }
        )
    assert outside.value.status_code == 409
