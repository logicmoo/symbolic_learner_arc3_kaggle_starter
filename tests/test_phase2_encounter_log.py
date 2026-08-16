from dataclasses import replace

import pytest

from object_memory import EncounterLog, EncounterRecord, InstanceParameters


def _encounter(node: int, *, previous: str | None = None) -> EncounterRecord:
    return EncounterRecord.create(
        observation_id=f"observation-{node}",
        action_tree_node=f"nodes/{node:05d}",
        object_identity_id="object-red-square",
        instance=InstanceParameters(position=(float(node), 2.0)),
        previous_encounter_id=previous,
    )


def test_encounter_log_is_ordered_idempotent_and_queryable_by_object() -> None:
    log = EncounterLog()
    first = log.append(_encounter(1))
    second = log.append(_encounter(2, previous=first.encounter_id))

    assert log.append(second) is second
    assert log.records() == (first, second)
    assert log.get(first.encounter_id) is first
    assert log.for_object("object-red-square") == (first, second)


def test_encounter_log_rejects_missing_history_and_identity_conflicts() -> None:
    log = EncounterLog()
    with pytest.raises(ValueError, match="previous encounter"):
        log.append(_encounter(2, previous="encounter-missing"))

    first = log.append(_encounter(1))
    conflicting = replace(first, confidence=0.9)
    with pytest.raises(ValueError, match="identity conflict"):
        log.append(conflicting)


def test_encounter_replay_has_the_same_order_and_hash() -> None:
    first = _encounter(1)
    second = _encounter(2, previous=first.encounter_id)
    source = EncounterLog().replay((first, second))
    replayed = EncounterLog().replay(source.records())

    assert replayed.records() == source.records()
    assert replayed.deterministic_hash() == source.deterministic_hash()
