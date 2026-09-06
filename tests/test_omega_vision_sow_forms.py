"""SoW A.2/A.3 regression tests: raster form, SoW name aliases, §16 future stubs,
and the delegating GenerativeForm holder."""

from __future__ import annotations

import pytest

from omega_vision.forms import (
    AbstractGenerativeForm,
    CellLogoForm,
    ContourFillForm,
    GenerativeForm,
    LayeredStrokeForm,
    PartGraph3DForm,
)


def test_contour_fill_form_is_translation_invariant_and_faithful():
    t_here = ContourFillForm({"red": [(0, 0), (1, 0), (2, 0), (1, 1)]})
    t_moved = ContourFillForm({"red": [(10, 10), (11, 10), (12, 10), (11, 11)]})

    # Determinism + affine (translation) identity (SoW §13)
    assert t_here.canonicalize() == t_moved.canonicalize()
    assert t_here.distance(t_moved) == 0.0
    # Description length = cells + layers (SoW §5)
    assert t_here.code_length() == 5.0
    # fit_instance recovers the offset with zero residual (SoW A.3)
    fit = t_here.fit_instance(t_moved)
    assert fit.residual == 0.0
    assert fit.parameters["offset"] == (10, 10)
    # render honours the fitted offset
    assert t_here.render({"offset": fit.parameters["offset"]})[(10, 10)] == "red"
    # completion returns a form (SoW §8)
    completed = t_here.complete()
    assert completed and isinstance(completed[0], ContourFillForm)
    assert t_here.domain == "raster"


def test_cell_logo_form_is_the_sow_alias_for_the_grid_form():
    assert CellLogoForm is GenerativeForm
    form = CellLogoForm("fd 3")
    assert isinstance(form, AbstractGenerativeForm)
    assert form.canonicalize() == "fd 3"
    assert form.domain == "grid"


def test_generative_form_delegates_to_a_held_subclass_instance():
    raster = ContourFillForm({"red": [(0, 0), (1, 0), (2, 0), (1, 1)]})
    holder = GenerativeForm(delegate=raster)

    # the wrapper reports and uses the delegate, not the grid implementation
    assert holder.delegate is raster
    assert holder.domain == "raster"
    assert holder.canonicalize() == raster.canonicalize()
    assert holder.render() == raster.render()
    assert holder.description_length() == int(raster.code_length())

    moved = ContourFillForm({"red": [(4, 7), (5, 7), (6, 7), (5, 8)]})
    assert holder.fit_instance(moved).parameters["offset"] == (4, 7)
    assert holder.distance(moved) == 0.0
    # wrapper-vs-wrapper comparisons unwrap both sides
    assert holder.distance(GenerativeForm(delegate=moved)) == 0.0

    with pytest.raises(TypeError):
        GenerativeForm(delegate="not a form")  # type: ignore[arg-type]

    # without a delegate the grid behaviour is unchanged
    plain = GenerativeForm("fd 3")
    assert plain.delegate is None
    assert plain.canonicalize() == "fd 3"
    assert plain.domain == "grid"


def test_future_components_are_importable_but_raise():
    from omega_vision._future import FutureComponentError
    from omega_vision.accelerators import SketchformerEmbedding
    from omega_vision.adapters import (
        AnimeRegionProposer,
        RGBDObjectProposer,
        Robot3DAdapter,
    )

    futures = (
        LayeredStrokeForm,
        PartGraph3DForm,
        Robot3DAdapter,
        RGBDObjectProposer,
        AnimeRegionProposer,
        SketchformerEmbedding,
    )
    for future in futures:
        assert future.sow_section == "§16"
        with pytest.raises(FutureComponentError):
            future()


def test_top_level_package_exports_the_sow_names():
    import omega_vision

    for name in (
        "CellLogoForm",
        "ContourFillForm",
        "FutureComponentError",
        "LayeredStrokeForm",
        "PartGraph3DForm",
        "Robot3DAdapter",
        "RGBDObjectProposer",
        "AnimeRegionProposer",
        "SketchformerEmbedding",
    ):
        assert name in omega_vision.__all__
        assert getattr(omega_vision, name) is not None
