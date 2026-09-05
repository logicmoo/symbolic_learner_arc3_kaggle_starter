from PIL import Image

from omega_vision import AlphaContourProvider, PythonProvider, SpriteAdapter


def _sprite_sheet() -> Image.Image:
    image = Image.new("RGBA", (6, 4), (0, 0, 0, 0))
    image.putpixel((0, 0), (255, 0, 0, 255))
    image.putpixel((1, 0), (255, 0, 0, 255))
    image.putpixel((0, 1), (255, 0, 0, 255))
    image.putpixel((4, 2), (0, 0, 255, 255))
    image.putpixel((4, 3), (0, 0, 255, 255))
    return image


def test_alpha_contour_provider_extracts_disconnected_sprites() -> None:
    extracted = AlphaContourProvider()(_sprite_sheet())

    assert extracted["algorithm"] == "4-connected-alpha-components"
    assert [item["bounds"] for item in extracted["objects"]] == [
        [0, 0, 2, 2],
        [4, 2, 5, 4],
    ]
    assert extracted["objects"][0]["properties"]["pixel_count"] == 3
    assert extracted["objects"][0]["vector"]["kind"] == "pixel_boundary"
    assert len(extracted["objects"][0]["contour"]) == 3


def test_sprite_adapter_uses_normalized_image_contract() -> None:
    adapter = SpriteAdapter(PythonProvider({}))

    batch = adapter.normalize(
        observation_id="sprites-1",
        image=_sprite_sheet(),
        action_tree_node="nodes/00002",
        artifact_uri="nodes/00002/sprites.png",
    )

    assert len(batch.candidates) == 2
    assert all(candidate.domain == "image" for candidate in batch.candidates)
    detail = adapter.candidate_detail("sprite_0")
    assert detail["normalizedStructure"]["geometry"]["bounds"] == (0, 0, 2, 2)
    assert detail["vector"]["points"] == [[0, 0], [0, 1], [1, 0]]
