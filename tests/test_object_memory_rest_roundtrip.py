"""The object-memory contract dataclasses must work identically whether used via
local Python import or over REST (as JSON). These tests lock that dual-mode
parity: a payload serialises to plain JSON, round-trips through from_dict/to_dict
unchanged, and validation rejects malformed input with a structured error.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

import pytest  # noqa: E402

from object_memory import (  # noqa: E402
    GameObjectLearnerPayload,
    IntegrationError,
    IntegrationValidator,
)


def _payload() -> GameObjectLearnerPayload:
    return GameObjectLearnerPayload(
        "s2",
        (
            {"id": "player", "candidate_identity_id": "c", "object_identity_id": "player",
             "encounter_id": "e2", "position": [2, 1], "shape": "domino", "colour": "red",
             "relationships": {"adjacent_to": ["wall"]}, "evidence_ids": ("ev1",)},
            {"id": "wall", "position": [3, 1], "shape": "box", "colour": "grey"},
        ),
        correspondences=({"candidate_id": "c", "stored_identity_id": "player",
                          "evidence_ids": ("ev1",)},),
        transitions=({"id": "player", "action": "step",
                      "properties": {"position": {"from": [1, 1], "to": [2, 1]}}},),
        provenance=("f1", "f2"),
        identity_ids=("player", "wall"),
        encounter_ids=("e1", "e2"),
        evidence=({"evidence_id": "ev1", "subject_id": "player", "polarity": "supports"},),
    )


def test_payload_is_json_serializable_over_rest():
    payload = IntegrationValidator().validate(_payload())
    as_dict = payload.to_dict()
    # Fully JSON round-trippable, i.e. safe to send/receive over REST unchanged.
    assert json.loads(json.dumps(as_dict)) == as_dict


def test_local_and_rest_construction_are_equivalent():
    payload = IntegrationValidator().validate(_payload())
    as_dict = payload.to_dict()
    # Deserialise as a REST server would, re-serialise, and compare JSON: the
    # dataclass behaves identically whether built locally or from a JSON body.
    rebuilt = GameObjectLearnerPayload.from_dict(as_dict)
    assert rebuilt.to_dict() == as_dict
    # And a validator accepts the re-built payload just the same.
    assert IntegrationValidator().validate(rebuilt).to_dict() == as_dict


def test_malformed_payload_raises_structured_error():
    with pytest.raises(IntegrationError):
        IntegrationValidator().validate(GameObjectLearnerPayload("x", ({"noid": True},)))
