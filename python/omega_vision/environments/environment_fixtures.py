from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageDraw

from omega_vision.evaluation.benchmark import PerceptionFixture, RasterPerturbationGenerator


@dataclass(frozen=True)
class EnvironmentProgressionFixtures:
    rendered_arcade: tuple[PerceptionFixture, ...]
    fixed_camera: tuple[PerceptionFixture, ...]
    top_down_manipulation: tuple[PerceptionFixture, ...]

    def all(self) -> tuple[PerceptionFixture, ...]:
        return (
            *self.rendered_arcade,
            *self.fixed_camera,
            *self.top_down_manipulation,
        )


def _canvas(size: tuple[int, int] = (48, 32)) -> Image.Image:
    return Image.new("RGBA", size, (0, 0, 0, 0))


def rendered_arcade_fixtures() -> tuple[PerceptionFixture, ...]:
    frame = _canvas()
    draw = ImageDraw.Draw(frame)
    draw.rectangle((3, 20, 12, 27), fill=(40, 180, 255, 255))
    draw.rectangle((30, 5, 35, 10), fill=(255, 190, 20, 255))
    draw.rectangle((40, 22, 45, 27), fill=(255, 70, 90, 255))
    return (PerceptionFixture("arcade:frame:0", frame, 3, "rendered_arcade"),)


def fixed_camera_physics_fixtures() -> tuple[PerceptionFixture, ...]:
    frames = []
    for index, x in enumerate((5, 13, 21)):
        frame = _canvas()
        draw = ImageDraw.Draw(frame)
        draw.ellipse((x, 8, x + 5, 13), fill=(100, 240, 120, 255))
        draw.rectangle((2, 25, 45, 27), fill=(100, 100, 110, 255))
        frames.append(
            PerceptionFixture(
                f"fixed-camera:frame:{index}",
                frame,
                2,
                "fixed_camera_physics",
            )
        )
    return tuple(frames)


def top_down_manipulation_fixtures() -> tuple[PerceptionFixture, ...]:
    scene = _canvas()
    draw = ImageDraw.Draw(scene)
    draw.rectangle((5, 6, 14, 15), fill=(90, 140, 255, 255))
    draw.rectangle((28, 10, 39, 20), fill=(255, 130, 60, 255))
    generator = RasterPerturbationGenerator(seed=11)
    return generator.partial_occlusion_dataset(
        "top-down:two-blocks",
        scene,
        expected_count=2,
        occlusion=(5, 6, 8, 9),
    )


def environment_progression_fixtures() -> EnvironmentProgressionFixtures:
    return EnvironmentProgressionFixtures(
        rendered_arcade=rendered_arcade_fixtures(),
        fixed_camera=fixed_camera_physics_fixtures(),
        top_down_manipulation=top_down_manipulation_fixtures(),
    )
