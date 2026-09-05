"""SoW layout tests for the :mod:`omega_vision` package.

Verifies that every SoW Appendix-A-named class is importable under the SoW layout,
that the net-new SoW-laid-out pieces behave, and that the deterministic-core
invariants hold through the façade. Implementation lives in :mod:`object_memory`;
these tests exercise the SoW-named surface.
"""

from __future__ import annotations

import pytest


def test_sow_named_symbols_are_importable():
    import omega_vision as ov

    # SoW A.2 core, A.3 forms, A.4 data types, A.6 adapters, §15 accelerators
    for name in (
        "SingleWriter", "AtomStore", "EncounterLog", "ResidualGate", "PredictionLedger",
        "IdentityMerge", "GameLearningPipeline",
        "GenerativeForm", "CellLogoForm", "ContourFillForm",
        "Observation", "CandidateObject", "RecognitionAccount", "ResidualCandidate",
        "CommittedAtom", "TransitionRule", "PredictionRecord",
        "GridAdapter", "GridIndividuator", "SpriteAdapter", "RasterSegmenter",
        "PerceptualHash", "VectorTraceIndex", "FaissIndex",
        "GridMetrics", "RasterMetrics",
        "new_memory", "new_writer", "build_store", "process_observation",
    ):
        assert hasattr(ov, name), f"omega_vision is missing SoW name {name!r}"


def test_module_layout_matches_sow_appendix_a2():
    # A.2 file/folder layout resolves to real modules
    from omega_vision.core import schemas, single_writer, atom_store, encounter_log  # noqa: F401
    from omega_vision.core import residual_gate, identity_merge, prediction_ledger  # noqa: F401
    from omega_vision.core import rule_induction, evaluation  # noqa: F401
    from omega_vision.forms import base, cell_logo, contour_fill  # noqa: F401
    from omega_vision.adapters import grid, sprite  # noqa: F401
    from omega_vision.accelerators import vector_trace, perceptual_hash, faiss_index  # noqa: F401
    from omega_vision import environments  # noqa: F401


def test_contour_fill_form_is_translation_invariant_and_faithful():
    from omega_vision.forms import ContourFillForm

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
    # completion returns a form (SoW §8)
    completed = t_here.complete()
    assert completed and isinstance(completed[0], ContourFillForm)


def test_grid_individuator_cuts_scene_into_objects():
    from omega_vision.adapters import GridIndividuator

    grid = [
        [0, 1, 1],
        [0, 1, 0],
        [2, 0, 0],
    ]
    regions = GridIndividuator().individuate(grid)
    colours = sorted(r["color"] for r in regions)
    assert colours == [1, 2]
    ones = next(r for r in regions if r["color"] == 1)
    assert set(ones["cells"]) == {(1, 0), (2, 0), (1, 1)}


def test_raster_segmenter_groups_connected_foreground():
    from omega_vision.adapters import RasterSegmenter

    pixels = [
        [0, 0, 0],
        [0, 5, 0],
        [0, 5, 5],
    ]
    regions = RasterSegmenter(background=0).segment(pixels)
    assert len(regions) == 1
    assert set(regions[0]["cells"]) == {(1, 1), (1, 2), (2, 2)}


def test_accelerators_are_recall_only_but_functional():
    from omega_vision.accelerators import FaissIndex, PerceptualHash, VectorTraceIndex
    from omega_vision.forms import ContourFillForm

    ph = PerceptualHash()
    same = ph.hash([[0, 0], [0, 1]])
    assert ph.distance(same, same) == 0
    assert ph.distance(same, ph.hash([[1, 1], [1, 0]])) > 0

    fx = FaissIndex()
    fx.add("a", [1.0, 0.0, 0.0])
    fx.add("b", [0.0, 1.0, 0.0])
    assert fx.search([1.0, 0.0, 0.0], k=1)[0][0] == "a"

    vt = VectorTraceIndex()
    vt.add("t", ContourFillForm({"red": [(0, 0), (1, 0), (2, 0), (1, 1)]}))
    assert vt.query(ContourFillForm({"red": [(5, 5), (6, 5), (7, 5), (6, 6)]}), k=1) == ("t",)


def test_deterministic_core_invariants_through_the_facade():
    import omega_vision as ov
    from omega_vision.core.schemas import CommittedAtom, ResidualCandidate, ResidualDisposition
    from omega_vision.core import PredictionRecord

    # single writer + confidence floor (SoW A.1.1/A.1.2)
    writer = ov.new_writer()
    atom = writer.commit(CommittedAtom(handle="obj:1", atom_type="object", payload={}))
    assert atom.confidence == 0.0
    assert writer.accrue_evidence("obj:1", confidence=0.5, evidence="seen").confidence == 0.5

    # explicit residual -> three-way disposition (SoW §7)
    gate = ov.ResidualGate()
    disposition = gate.evaluate(ResidualCandidate(
        residual_id="r", source_candidate_id="c",
        disposition=ResidualDisposition.PROVISIONAL, residual_length=4.0,
        structured=True, recurrence_count=3, prediction_gain=0.2, provenance=()))
    assert disposition in tuple(ResidualDisposition)

    # predict-before-check ledger (SoW §10, A.1.7)
    ledger = ov.PredictionLedger()
    ledger.record(PredictionRecord(prediction_id="p", rule_id="r", source_state_id="s0",
                                   predicted_effects=("down",), created_sequence=1))
    graded = ledger.grade("p", outcome_sequence=2, outcome="down", grade=1.0)
    assert graded.grade == 1.0


def test_process_observation_factory_segments_via_adapter():
    import omega_vision as ov

    class _FakeAdapter:
        def propose_candidates(self, observation):
            return ["cand-1", "cand-2"]

    result = ov.process_observation("obs", _FakeAdapter())
    assert result["candidates"] == ("cand-1", "cand-2")


def test_future_components_are_importable_but_raise():
    from omega_vision._future import FutureComponentError
    from omega_vision.forms import LayeredStrokeForm, PartGraph3DForm
    from omega_vision.adapters import Robot3DAdapter

    for future in (LayeredStrokeForm, PartGraph3DForm, Robot3DAdapter):
        with pytest.raises(FutureComponentError):
            future()
