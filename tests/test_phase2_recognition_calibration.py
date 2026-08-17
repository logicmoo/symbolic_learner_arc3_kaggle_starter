from dataclasses import asdict

import pytest

from object_memory import RecognitionAccount, RecognitionCalibrator, SemanticRecordCodec


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
