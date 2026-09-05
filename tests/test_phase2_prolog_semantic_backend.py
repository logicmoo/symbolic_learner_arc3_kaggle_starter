from pathlib import Path
import shutil
import subprocess

import pytest

from omega_vision import (
    ActionRecommendation,
    ArtifactRef,
    CommittedAtom,
    ConfidenceHistoryRecord,
    EncounterRecord,
    Observation,
    ObjectChange,
    PrologSemanticBackend,
    ResidualCandidate,
    ResidualDisposition,
    SymbolicStore,
    TurtleProgramRef,
    TransitionRule,
)


def test_prolog_semantic_backend_round_trips_and_hydrates(tmp_path: Path) -> None:
    path = tmp_path / "semantic_memory.pl"
    store = SymbolicStore(PrologSemanticBackend(path))
    artifact = ArtifactRef.create(
        artifact_type="turtle_program",
        uri="memory://object/red",
        content_hash="sha256:red",
    )
    observation = store.put_observation(
        Observation.create(
            source_modality="logical_grid",
            artifacts=(artifact,),
            action_tree_node="node/initial",
        )
    )
    first = store.put_encounter(
        EncounterRecord.create(
            observation_id=observation.observation_id,
            action_tree_node="node/initial",
            object_identity_id="red_ball",
            turtle_programs=(TurtleProgramRef(artifact, fit_score=1.0),),
        )
    )
    second = store.put_encounter(
        EncounterRecord.create(
            observation_id="next-observation",
            action_tree_node="node/right",
            object_identity_id="red_ball",
            previous_encounter_id=first.encounter_id,
        )
    )
    atom = store.put_atom(
        CommittedAtom(
            "red_ball",
            "object",
            {"description": 'red "ball"\nwith unicode π'},
            confidence=0.75,
            provenance=("fixture",),
        )
    )
    confidence_record = store.put_confidence_history(
        ConfidenceHistoryRecord(0, "red_ball", 0.75, "active", "evidence", "ev-1")
    )
    change = store.put_object_change(
        ObjectChange.create(
            kind="moved",
            before_identity_ids=("red_ball",),
            after_candidate_ids=("candidate-red",),
            properties={"position": {"from": (1.0, 1.0), "to": (2.0, 1.0)}},
            evidence_ids=("ev-1",),
        )
    )
    residual = store.put_residual(
        ResidualCandidate.create(
            source_candidate_id="candidate-red",
            disposition=ResidualDisposition.PROVISIONAL,
            residual_length=1.0,
            structured=True,
            provenance=("proposal-red", "field:appearance.shape"),
        )
    )
    rule = store.put_transition_rule(
        TransitionRule(
            "rule-red-right",
            ("red_ball",),
            {"action": "RIGHT"},
            ({"kind": "moved", "delta": [1, 0]},),
            assumptions=("identity remains stable",),
            critiques=("one observation",),
            supporting_evidence_ids=("ev-1",),
            bootstrap_probability=0.5,
        )
    )
    recommendation = store.put_action_recommendation(
        ActionRecommendation.create(
            rule_id=rule.rule_id,
            source_state_id=observation.observation_id,
            recommended_action=rule.action_or_event,
            attempted_action={"action": "RIGHT"},
            created_sequence=3,
            available_evidence_ids=("ev-1",),
            probability=0.5,
        )
    )

    loaded = SymbolicStore(PrologSemanticBackend(path)).hydrate()

    assert loaded.get("observations", observation.observation_id) == observation
    assert loaded.encounters.records() == (first, second)
    assert loaded.artifacts.get(artifact.artifact_id) == artifact
    assert loaded.get("atoms", atom.handle) == atom
    assert loaded.values("confidence_history") == (confidence_record,)
    assert loaded.values("object_changes") == (change,)
    assert loaded.values("residuals") == (residual,)
    assert loaded.values("transition_rules") == (rule,)
    assert loaded.values("action_recommendations") == (recommendation,)
    assert loaded.snapshot() == store.snapshot()
    source = path.read_text(encoding="utf-8")
    assert ":- dynamic semantic_record/3." in source
    assert "red_ball" in source


@pytest.mark.skipif(shutil.which("swipl") is None, reason="SWI-Prolog is unavailable")
def test_prolog_semantic_backend_is_live_swi_prolog_data(tmp_path: Path) -> None:
    path = tmp_path / "semantic_memory.pl"
    store = SymbolicStore(PrologSemanticBackend(path))
    artifact = store.put_artifact(
        ArtifactRef.create(artifact_type="mask", uri="memory://mask/one")
    )

    result = subprocess.run(
        [
            "swipl",
            "-q",
            "-s",
            str(path),
            "-g",
            (
                "findall(Id, semantic_record(\"artifacts\", Id, _), Ids),"
                "length(Ids, 1),halt"
            ),
        ],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert artifact.artifact_id in path.read_text(encoding="utf-8")
