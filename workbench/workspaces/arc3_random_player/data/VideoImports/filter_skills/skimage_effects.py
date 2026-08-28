"""scikit-image effects skill: ~50 named scientific-image transforms
(edge detectors, ridge filters, morphology ladders, adaptive exposure,
gamma/sigmoid ladders, swirls, noise, denoisers, superpixel looks). The
workbench calls these directly - no LLM in the loop. params.effect picks one.
"""

import numpy as np
from PIL import Image


def _to_float(image):
    return np.asarray(image.convert("RGB"), dtype=np.float64) / 255.0


def _from_float(array):
    return Image.fromarray((np.clip(array, 0.0, 1.0) * 255).astype(np.uint8))


def _gray(image):
    return np.asarray(image.convert("L"), dtype=np.float64) / 255.0


def _gray_effect(function):
    def wrapped(image):
        result = function(_gray(image))
        lo, hi = float(result.min()), float(result.max())
        if hi > lo:
            result = (result - lo) / (hi - lo)
        return _from_float(np.dstack([result] * 3))
    return wrapped


def _rgb_effect(function):
    return lambda image: _from_float(function(_to_float(image)))


def _edges(kind):
    def run(gray):
        from skimage import filters
        return getattr(filters, kind)(gray)
    return _gray_effect(run)


def _ridge(kind):
    def run(gray):
        from skimage import filters
        return getattr(filters, kind)(gray)
    return _gray_effect(run)


def _gamma(value):
    def run(rgb):
        from skimage import exposure
        return exposure.adjust_gamma(rgb, value)
    return _rgb_effect(run)


def _sigmoid(cutoff, gain):
    def run(rgb):
        from skimage import exposure
        return exposure.adjust_sigmoid(rgb, cutoff=cutoff, gain=gain)
    return _rgb_effect(run)


def _swirl(strength, radius_scale):
    def swirl_image(image):
        from skimage import transform
        rgb = _to_float(image)
        height, width = rgb.shape[:2]
        out = transform.swirl(
            rgb, strength=strength,
            radius=min(height, width) * radius_scale,
            center=(width / 2, height / 2),
        )
        return _from_float(out)
    return swirl_image


def _noise(mode, **kwargs):
    def run(rgb):
        from skimage import util
        return util.random_noise(rgb, mode=mode, rng=7, **kwargs)
    return _rgb_effect(run)


def _morph(kind, size):
    def run(gray):
        from skimage import morphology
        footprint = morphology.disk(size)
        return getattr(morphology, kind)((gray * 255).astype(np.uint8), footprint) / 255.0
    return _gray_effect(run)


def _adapthist(clip):
    def run(rgb):
        from skimage import exposure
        return exposure.equalize_adapthist(rgb, clip_limit=clip)
    return _rgb_effect(run)


def _tv_denoise(weight):
    def run(rgb):
        from skimage import restoration
        return restoration.denoise_tv_chambolle(rgb, weight=weight, channel_axis=-1)
    return _rgb_effect(run)


def _slic_paint(segments):
    def paint(image):
        from skimage import color, segmentation
        rgb = _to_float(image)
        labels = segmentation.slic(rgb, n_segments=segments, compactness=10, start_label=1)
        return _from_float(color.label2rgb(labels, rgb, kind="avg", bg_label=0))
    return paint


def _felzen_paint(scale):
    def paint(image):
        from skimage import color, segmentation
        rgb = _to_float(image)
        labels = segmentation.felzenszwalb(rgb, scale=scale, sigma=0.6, min_size=40)
        return _from_float(color.label2rgb(labels, rgb, kind="avg", bg_label=-1))
    return paint


def _gabor(frequency):
    def run(gray):
        from skimage import filters
        real, _imag = filters.gabor(gray, frequency=frequency)
        return real
    return _gray_effect(run)


def _entropy(size):
    def run(gray):
        from skimage.filters.rank import entropy
        from skimage import morphology
        return entropy((gray * 255).astype(np.uint8), morphology.disk(size))
    return _gray_effect(run)


EFFECTS = {
    # Edge detectors
    "edges_sobel": _edges("sobel"),
    "edges_scharr": _edges("scharr"),
    "edges_prewitt": _edges("prewitt"),
    "edges_roberts": _edges("roberts"),
    "edges_farid": _edges("farid"),
    "edges_laplace": _edges("laplace"),
    # Ridge / vessel filters (dramatic line art)
    "ridge_meijering": _ridge("meijering"),
    "ridge_sato": _ridge("sato"),
    "ridge_frangi": _ridge("frangi"),
    "ridge_hessian": _ridge("hessian"),
    # Gabor banks
    "gabor_02": _gabor(0.2),
    "gabor_04": _gabor(0.4),
    "gabor_06": _gabor(0.6),
    # Exposure
    "gamma_04": _gamma(0.4),
    "gamma_07": _gamma(0.7),
    "gamma_15": _gamma(1.5),
    "gamma_25": _gamma(2.5),
    "sigmoid_soft": _sigmoid(0.5, 5),
    "sigmoid_hard": _sigmoid(0.5, 12),
    "sigmoid_low": _sigmoid(0.35, 8),
    "sigmoid_high": _sigmoid(0.65, 8),
    "equalize_adapt_1": _adapthist(0.01),
    "equalize_adapt_3": _adapthist(0.03),
    "equalize_adapt_8": _adapthist(0.08),
    # Swirls (geometry!)
    "swirl_soft": _swirl(3, 0.6),
    "swirl_medium": _swirl(6, 0.7),
    "swirl_hard": _swirl(10, 0.8),
    "swirl_inverse": _swirl(-6, 0.7),
    # Noise
    "noise_gaussian": _noise("gaussian", var=0.01),
    "noise_heavy": _noise("gaussian", var=0.05),
    "noise_salt_pepper": _noise("s&p", amount=0.08),
    "noise_speckle": _noise("speckle", var=0.05),
    "noise_poisson": _noise("poisson"),
    # Morphology ladders
    "morph_erode_2": _morph("erosion", 2),
    "morph_erode_4": _morph("erosion", 4),
    "morph_dilate_2": _morph("dilation", 2),
    "morph_dilate_4": _morph("dilation", 4),
    "morph_open_3": _morph("opening", 3),
    "morph_close_3": _morph("closing", 3),
    "morph_tophat_5": _morph("white_tophat", 5),
    "morph_blackhat_5": _morph("black_tophat", 5),
    # Denoise / painterly
    "denoise_tv_light": _tv_denoise(0.05),
    "denoise_tv_strong": _tv_denoise(0.15),
    "denoise_tv_paint": _tv_denoise(0.3),
    # Superpixel painting
    "superpixels_50": _slic_paint(50),
    "superpixels_150": _slic_paint(150),
    "superpixels_400": _slic_paint(400),
    "felzen_paint_100": _felzen_paint(100),
    "felzen_paint_300": _felzen_paint(300),
    # Texture
    "entropy_3": _entropy(3),
    "entropy_6": _entropy(6),
}

SKILL = {
    "title": "scikit-image effect",
    "description": "One of ~50 scikit-image transforms: edge/ridge detectors, gabor banks, exposure ladders, swirls, noise, morphology, TV denoise painting, superpixel looks, entropy texture.",
    "params": {"effect": "superpixels_150"},
    "paramChoices": {"effect": sorted(EFFECTS)},
}


def apply(image: Image.Image, params: dict) -> Image.Image:
    effect = str(params.get("effect") or "superpixels_150")
    transform = EFFECTS.get(effect)
    if transform is None:
        raise ValueError(f"unknown scikit-image effect '{effect}' (choose from {len(EFFECTS)})")
    return transform(image.convert("RGB")).convert("RGB")
