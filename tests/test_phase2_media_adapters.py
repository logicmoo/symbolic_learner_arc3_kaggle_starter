from io import BytesIO

from PIL import Image

from omega_vision import (
    ImageAdapter,
    LearnedPartRoleProvider,
    PythonProvider,
    SimpleVideoAdapter,
)


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
    structure = adapter.candidate_detail("red-square")["normalizedStructure"]
    assert structure["geometry"] == {
        "bounds": (0, 0, 3, 2),
        "width": 3,
        "height": 2,
        "cells": (),
        "boundary_cells": (),
    }
    assert structure["properties"] == {"color": "red"}
    assert structure["appearance"] == {"color": "red"}
    assert structure["relationships"] == ()
    assert structure["orientation"] is None
    assert structure["scale"] == (3, 2)


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


def test_image_adapter_normalizes_cells_compound_parts_and_orientation() -> None:
    def extract(_image: Image.Image):
        return {
            "objects": [
                {
                    "id": "bars",
                    "bounds": [2, 3, 8, 8],
                    "cells": [[2, 3], [3, 3], [4, 3], [7, 7]],
                    "contour": [[2, 3], [3, 3], [4, 3], [7, 7]],
                    "properties": {"color": "blue"},
                    "partRoles": [
                        {"role": "body", "component": 0},
                        {"role": "marker", "component": 1, "properties": {"meaning": "goal"}},
                    ],
                    "relationships": [
                        {"target": "goal", "relation": "left_of"}
                    ],
                }
            ]
        }

    adapter = ImageAdapter(extract, PythonProvider({}))
    adapter.normalize(
        observation_id="camera-structure",
        image=Image.new("RGBA", (8, 8)),
        action_tree_node="nodes/structure",
        artifact_uri="nodes/structure/camera.png",
    )
    structure = adapter.candidate_detail("bars")["normalizedStructure"]

    assert structure["geometry"]["cells"] == ((0, 0), (1, 0), (2, 0), (5, 4))
    assert structure["topology"]["compound"] is True
    assert len(structure["topology"]["compound_parts"]) == 2
    assert structure["topology"]["part_roles"] == (
        {
            "role": "body",
            "component_indices": (0,),
            "cells": ((0, 0), (1, 0), (2, 0)),
            "properties": {},
        },
        {
            "role": "marker",
            "component_indices": (1,),
            "cells": ((5, 4),),
            "properties": {"meaning": "goal"},
        },
    )
    assert structure["orientation"] is not None
    assert structure["relationships"] == (
        {"target": "goal", "relation": "left_of"},
    )


def test_image_adapter_rejects_part_role_for_unknown_component() -> None:
    def extract(_image: Image.Image):
        return {
            "objects": [
                {
                    "id": "bad-role",
                    "bounds": [0, 0, 2, 2],
                    "cells": [[0, 0]],
                    "partRoles": [{"role": "handle", "component": 3}],
                }
            ]
        }

    adapter = ImageAdapter(extract, PythonProvider({}))
    try:
        adapter.normalize(
            observation_id="bad-role",
            image=Image.new("RGB", (2, 2)),
            action_tree_node="nodes/bad-role",
            artifact_uri="nodes/bad-role/image.png",
        )
    except ValueError as error:
        assert "unknown structural component" in str(error)
    else:
        raise AssertionError("invalid semantic part role was accepted")


def test_image_adapter_learns_semantic_part_roles_from_labeled_examples() -> None:
    def extract(_image: Image.Image):
        return {
            "objects": [
                {
                    "id": "learned-tool",
                    "bounds": [0, 0, 8, 3],
                    "cells": [
                        [0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1],
                        [7, 2],
                    ],
                }
            ]
        }

    learned_roles = LearnedPartRoleProvider(
        (
            {
                "role": "body",
                "cells": [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1]],
            },
            {
                "role": "marker",
                "cells": [[0, 0]],
                "properties": {"meaning": "tip"},
            },
        )
    )
    adapter = ImageAdapter(extract, PythonProvider({}), learned_roles)
    adapter.normalize(
        observation_id="learned-roles",
        image=Image.new("RGB", (8, 3)),
        action_tree_node="nodes/learned-roles",
        artifact_uri="nodes/learned-roles/image.png",
    )

    roles = adapter.candidate_detail("learned-tool")["normalizedStructure"]["topology"]["part_roles"]
    assert tuple(item["role"] for item in roles) == ("body", "marker")
    assert roles[1]["properties"] == {
        "meaning": "tip",
        "inference": "learned_nearest_example",
    }


def test_image_adapter_infers_pairwise_raster_relationships() -> None:
    def extract(_image: Image.Image):
        return {
            "objects": [
                {"id": "frame", "bounds": [0, 0, 8, 8]},
                {"id": "left", "bounds": [1, 2, 3, 4]},
                {"id": "right", "bounds": [5, 5, 7, 7]},
            ]
        }

    adapter = ImageAdapter(extract, PythonProvider({}))
    adapter.normalize(
        observation_id="relations",
        image=Image.new("RGB", (8, 8)),
        action_tree_node="nodes/relations",
        artifact_uri="nodes/relations/image.png",
    )

    left = adapter.candidate_detail("left")["normalizedStructure"]["relationships"]
    right = adapter.candidate_detail("right")["normalizedStructure"]["relationships"]
    frame = adapter.candidate_detail("frame")["normalizedStructure"]["relationships"]
    assert {item["relation"] for item in left} >= {"inside", "left_of", "above"}
    assert {item["relation"] for item in right} >= {"inside", "right_of", "below"}
    assert {tuple(item.values()) for item in frame} >= {
        ("left", "contains"),
        ("right", "contains"),
    }
