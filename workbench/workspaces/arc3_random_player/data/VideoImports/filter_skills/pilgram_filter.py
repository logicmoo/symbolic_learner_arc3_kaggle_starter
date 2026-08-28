"""Pilgram skill: Instagram-style color filters from the MIT-licensed
pilgram library (pip install pilgram) — a downloaded image-editing skill the
workbench calls directly, no LLM in the loop.

params.style picks the filter: aden, brannan, brooklyn, clarendon, earlybird,
gingham, hudson, inkwell, kelvin, lark, lofi, maven, mayfair, moon, nashville,
perpetua, reyes, rise, slumber (see pilgram's docs).
"""

from PIL import Image

import pilgram

# Every callable filter pilgram ships (aden … xpro2, incl. _1977), so the
# workbench can offer the full set as a combo, not just lofi.
_STYLES = sorted(
    name for name in dir(pilgram)
    if not name.startswith("__") and name not in {"css", "util"} and callable(getattr(pilgram, name))
)

SKILL = {
    "title": "Pilgram color filter (downloaded)",
    "description": "Instagram-style filters from the MIT pilgram library; params.style picks which one.",
    "params": {"style": "lofi"},
    "paramChoices": {"style": _STYLES},
}


def apply(image: Image.Image, params: dict) -> Image.Image:
    style = str(params.get("style") or "lofi").lower()
    transform = getattr(pilgram, style, None)
    if transform is None or style in {"css", "util"} or style.startswith("__"):
        raise ValueError(f"pilgram has no filter named '{style}'")
    return transform(image.convert("RGB"))
