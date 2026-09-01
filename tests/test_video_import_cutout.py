import base64
import io
import json
import threading
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
