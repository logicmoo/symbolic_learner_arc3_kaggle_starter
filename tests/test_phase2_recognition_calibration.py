from dataclasses import asdict

import pytest

from omega_vision import (
    AtomSpaceSemanticBackend,
    RecognitionAccount,
    RecognitionCalibrationPolicy,
    RecognitionCalibrator,
    SemanticRecordCodec,
    SymbolicStore,
)


def _account(confidence: float, accepted: bool, candidate: str) -> RecognitionAccount:
    return RecognitionAccount.create(
        candidate_id=candidate,
        stored_identity_id="known" if accepted else None,
        decision_confidence=confidence,
        decision_outcome=accepted,
        calibrated_confidence=confidence,
        decision_source="fixture_authority",
    )


def test_recognition_calibration_reports_reliability_and_brier_error() -> None:
    report = RecognitionCalibrator().report(
        (
            _account(0.8, True, "a"),
            _account(0.7, True, "b"),
            _account(0.2, False, "c"),
            _account(0.4, False, "d"),
        ),
        scope="sprite/alpha",
        bin_count=2,
    )

    assert report.scope == "sprite/alpha"
    assert report.sample_count == 4
    assert report.brier_score == pytest.approx((0.04 + 0.09 + 0.04 + 0.16) / 4)
    assert [(item.count, item.acceptance_rate) for item in report.bins] == [
        (2, 0.0),
        (2, 1.0),
    ]


def test_decision_calibration_fields_survive_semantic_record_replay() -> None:
    account = _account(0.65, False, "candidate-x")
    encoded = asdict(account)
    restored = SemanticRecordCodec.decode("recognition_account", encoded)

    assert restored == account
    assert restored.decision_confidence == 0.65
    assert restored.decision_outcome is False


def test_unresolved_accounts_are_excluded_from_empirical_calibration() -> None:
    unresolved = RecognitionAccount.create(
        candidate_id="candidate-u",
        stored_identity_id=None,
    )

    report = RecognitionCalibrator().report((unresolved,))

    assert report.sample_count == 0
    assert report.brier_score is None
    assert report.bins == ()


def test_isotonic_policy_is_serializable_and_improves_holdout_brier_score() -> None:
    calibrator = RecognitionCalibrator()
    policy = calibrator.fit(
        (
            _account(0.10, False, "train-a"),
            _account(0.20, False, "train-b"),
            _account(0.60, True, "train-c"),
            _account(0.70, True, "train-d"),
        ),
        scope="sprite/alpha-v1",
    )
    restored = RecognitionCalibrationPolicy.from_dict(policy.to_dict())
    holdout = (
        _account(0.15, False, "holdout-a"),
        _account(0.65, True, "holdout-b"),
    )

    raw = calibrator.report(holdout, scope="holdout")
    calibrated = calibrator.calibrated_report(holdout, restored)

    assert restored == policy
    assert policy.method == "isotonic_pav"
    assert policy.calibrate(0.15) == 0.0
    assert policy.calibrate(0.65) == 1.0
    assert calibrated.brier_score < raw.brier_score


def test_isotonic_policy_pools_non_monotone_authority_outcomes() -> None:
    policy = RecognitionCalibrator().fit(
        (
            _account(0.2, True, "a"),
            _account(0.4, False, "b"),
            _account(0.8, True, "c"),
        ),
        scope="mixed-provider",
    )

    assert tuple((item.sample_count, item.probability) for item in policy.points) == (
        (2, 0.5),
        (1, 1.0),
    )


def test_calibration_policy_survives_atomspace_reload(tmp_path) -> None:
    path = tmp_path / "calibration.metta"
    policy = RecognitionCalibrator().fit(
        (
            _account(0.2, False, "a"),
            _account(0.8, True, "b"),
        ),
        scope="raster/provider-v2",
    )
    store = SymbolicStore(AtomSpaceSemanticBackend(path=path))
    store.put_recognition_calibration(policy)

    loaded = SymbolicStore(AtomSpaceSemanticBackend(path=path)).hydrate()

    assert loaded.get("recognition_calibrations", policy.scope) == policy
