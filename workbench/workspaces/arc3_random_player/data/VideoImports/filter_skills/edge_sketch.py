"""Edge-sketch skill: line-art rendering with plain PIL.

Turns a frame into a white-background pencil-sketch of its edges — useful as
a prepass before asking a model to write a small redraw (turtle) program.
"""

from PIL import Image, ImageFilter, ImageOps

SKILL = {
    "title": "Edge sketch (line art)",
    "description": "White background, dark edge lines; params.threshold tunes line density (0-255).",
    "params": {"threshold": 40},
    # Candidate values for permutation runs (⚙ Permutations in the gallery).
    "paramGrid": {"threshold": [15, 30, 40, 60, 90, 140]},
}


def apply(image: Image.Image, params: dict) -> Image.Image:
    threshold = max(0, min(255, int(params.get("threshold") or 40)))
    edges = image.convert("L").filter(ImageFilter.FIND_EDGES)
    sketch = ImageOps.invert(edges).point(lambda value: 255 if value > 255 - threshold else value)
    return sketch.convert("RGB")
