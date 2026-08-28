"""Pillow effects skill: ~80 named image effects built purely from PIL
(ImageFilter / ImageOps / ImageEnhance / channel + tint math). The workbench
calls these directly - no LLM in the loop. params.effect picks one.
"""

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def _enhance(factory, factor):
    return lambda image: factory(image).enhance(factor)


def _duotone(dark, light):
    def apply_duotone(image):
        gray = image.convert("L")
        return Image.merge(
            "RGB",
            [gray.point([int(dark[band] + (light[band] - dark[band]) * value / 255) for value in range(256)]) for band in range(3)],
        )
    return apply_duotone


def _swap(order):
    def apply_swap(image):
        red, green, blue = image.convert("RGB").split()
        bands = {"r": red, "g": green, "b": blue}
        return Image.merge("RGB", [bands[key] for key in order])
    return apply_swap


def _only(band_index):
    def apply_only(image):
        bands = list(image.convert("RGB").split())
        blank = bands[band_index].point(lambda _value: 0)
        return Image.merge("RGB", [bands[at] if at == band_index else blank for at in range(3)])
    return apply_only


def _threshold(level):
    return lambda image: image.convert("L").point(lambda value: 255 if value >= level else 0).convert("RGB")


def _posterize(bits):
    return lambda image: ImageOps.posterize(image.convert("RGB"), bits)


def _solarize(level):
    return lambda image: ImageOps.solarize(image.convert("RGB"), level)


def _quantize(colors):
    return lambda image: image.convert("RGB").quantize(colors).convert("RGB")


EFFECTS = {
    # ImageFilter classics
    "blur": lambda image: image.filter(ImageFilter.BLUR),
    "contour": lambda image: image.filter(ImageFilter.CONTOUR),
    "detail": lambda image: image.filter(ImageFilter.DETAIL),
    "edge_enhance": lambda image: image.filter(ImageFilter.EDGE_ENHANCE),
    "edge_enhance_more": lambda image: image.filter(ImageFilter.EDGE_ENHANCE_MORE),
    "emboss": lambda image: image.filter(ImageFilter.EMBOSS),
    "find_edges": lambda image: image.filter(ImageFilter.FIND_EDGES),
    "sharpen": lambda image: image.filter(ImageFilter.SHARPEN),
    "smooth": lambda image: image.filter(ImageFilter.SMOOTH),
    "smooth_more": lambda image: image.filter(ImageFilter.SMOOTH_MORE),
    "gaussian_2": lambda image: image.filter(ImageFilter.GaussianBlur(2)),
    "gaussian_5": lambda image: image.filter(ImageFilter.GaussianBlur(5)),
    "gaussian_9": lambda image: image.filter(ImageFilter.GaussianBlur(9)),
    "unsharp": lambda image: image.filter(ImageFilter.UnsharpMask(radius=4, percent=150)),
    "median_3": lambda image: image.filter(ImageFilter.MedianFilter(3)),
    "median_5": lambda image: image.filter(ImageFilter.MedianFilter(5)),
    "max_3": lambda image: image.filter(ImageFilter.MaxFilter(3)),
    "min_3": lambda image: image.filter(ImageFilter.MinFilter(3)),
    "mode_3": lambda image: image.filter(ImageFilter.ModeFilter(3)),
    # ImageOps
    "autocontrast": lambda image: ImageOps.autocontrast(image.convert("RGB")),
    "equalize": lambda image: ImageOps.equalize(image.convert("RGB")),
    "grayscale": lambda image: ImageOps.grayscale(image).convert("RGB"),
    "invert": lambda image: ImageOps.invert(image.convert("RGB")),
    "mirror": lambda image: ImageOps.mirror(image),
    "flip": lambda image: ImageOps.flip(image),
    "posterize_1": _posterize(1),
    "posterize_2": _posterize(2),
    "posterize_3": _posterize(3),
    "posterize_4": _posterize(4),
    "posterize_5": _posterize(5),
    "posterize_6": _posterize(6),
    "solarize_64": _solarize(64),
    "solarize_128": _solarize(128),
    "solarize_192": _solarize(192),
    # Enhancement sweeps
    "desaturate": _enhance(ImageEnhance.Color, 0.0),
    "muted_color": _enhance(ImageEnhance.Color, 0.5),
    "vivid": _enhance(ImageEnhance.Color, 1.6),
    "hyper_color": _enhance(ImageEnhance.Color, 2.4),
    "low_contrast": _enhance(ImageEnhance.Contrast, 0.5),
    "high_contrast": _enhance(ImageEnhance.Contrast, 1.6),
    "crushed_contrast": _enhance(ImageEnhance.Contrast, 2.4),
    "darken": _enhance(ImageEnhance.Brightness, 0.55),
    "brighten": _enhance(ImageEnhance.Brightness, 1.45),
    "soft_focus": _enhance(ImageEnhance.Sharpness, 0.0),
    "crisp": _enhance(ImageEnhance.Sharpness, 2.2),
    # Channel permutations and isolations
    "swap_rbg": _swap("rbg"),
    "swap_grb": _swap("grb"),
    "swap_gbr": _swap("gbr"),
    "swap_brg": _swap("brg"),
    "swap_bgr": _swap("bgr"),
    "only_red": _only(0),
    "only_green": _only(1),
    "only_blue": _only(2),
    # Duotones (gradient maps)
    "duotone_navy_cream": _duotone((16, 24, 64), (255, 244, 214)),
    "duotone_purple_gold": _duotone((48, 16, 64), (255, 200, 64)),
    "duotone_teal_white": _duotone((0, 72, 80), (240, 255, 255)),
    "duotone_red_black": _duotone((24, 0, 0), (255, 64, 64)),
    "duotone_green_black": _duotone((0, 24, 0), (96, 255, 96)),
    "duotone_blue_black": _duotone((0, 0, 32), (96, 160, 255)),
    # Quantize and threshold ladders
    "quantize_2": _quantize(2),
    "quantize_4": _quantize(4),
    "quantize_8": _quantize(8),
    "quantize_16": _quantize(16),
    "quantize_32": _quantize(32),
    "threshold_64": _threshold(64),
    "threshold_96": _threshold(96),
    "threshold_128": _threshold(128),
    "threshold_160": _threshold(160),
    "threshold_192": _threshold(192),
}

SKILL = {
    "title": "Pillow effect",
    "description": "One of ~70 pure-PIL effects (filters, ops, enhancements, channel swaps, duotones, quantize/threshold ladders); params.effect picks which.",
    "params": {"effect": "posterize_4"},
    "paramChoices": {"effect": sorted(EFFECTS)},
}


def apply(image: Image.Image, params: dict) -> Image.Image:
    effect = str(params.get("effect") or "posterize_4")
    transform = EFFECTS.get(effect)
    if transform is None:
        raise ValueError(f"unknown pillow effect '{effect}' (choose from {len(EFFECTS)})")
    return transform(image.convert("RGB")).convert("RGB")
