from io import BytesIO

from PIL import Image

from object_memory import ImageAdapter, PythonProvider, SimpleVideoAdapter


def _extract(image: Image.Image):
    return {
        "source": "fixture_segments",
        "algorithm": "known-boxes",
        "objects": [
            {
                "id": "red-square",
                "bounds": [0, 0, image.width, image.height],
                "properties": {"color": "red"},
            }
        ],
    }


def _png_bytes(color: str) -> bytes:
    output = BytesIO()
    Image.new("RGB", (3, 2), color).save(output, format="PNG")
    return output.getvalue()


def test_image_adapter_accepts_encoded_bytes_and_normalizes_candidates() -> None:
    adapter = ImageAdapter(_extract, PythonProvider({}))

    batch = adapter.normalize(
        observation_id="camera-1",
        image=_png_bytes("red"),
        action_tree_node="nodes/00001",
        artifact_uri="nodes/00001/camera.png",
    )

    assert batch.observation.source_modality == "raster_image"
    assert batch.observation.dimensions == (2, 3, 3)
    assert batch.observation.artifacts[0].media_type == "image/png"
    assert batch.observation.artifacts[0].content_hash.startswith("sha256:")
    assert batch.candidates[0].domain == "image"
    assert adapter.candidate_detail("red-square")["normalizedStructure"] == {
        "geometry": {"bounds": (0, 0, 3, 2)},
        "properties": {"color": "red"},
        "relationships": (),
        "topology": {},
    }


def test_simple_video_adapter_preserves_frame_order_and_provenance() -> None:
    adapter = SimpleVideoAdapter(ImageAdapter(_extract, PythonProvider({})))

    batches = adapter.normalize(
        observation_id="clip-7",
        frames=[Image.new("RGB", (2, 2)), Image.new("RGB", (4, 3))],
        action_tree_node="nodes/00007",
        artifact_uri="nodes/00007/clip.mp4",
    )

    assert [batch.observation.dimensions for batch in batches] == [(2, 2, 3), (3, 4, 3)]
    assert [batch.observation.provenance[0].sequence for batch in batches] == [0, 1]
    assert [batch.candidates[0].observation_id for batch in batches] == [
        "clip-7:frame:0",
        "clip-7:frame:1",
    ]
