from types import SimpleNamespace

from omega_vision import (
    ChangeDetector,
    EncounterChangeSession,
    EncounterRecord,
    InMemorySemanticBackend,
    InstanceMatcher,
    InstanceParameters,
    StructuralCorrespondenceInferer,
    SymbolicStore,
)


def _instance(*, position=(0.0, 0.0), scale=(1.0, 1.0), color="red", shape="square"):
    return InstanceParameters(
        position=position,
        orientation=0.0,
        scale=scale,
        appearance={"color": color, "shape": shape},
        supported_transformations=("translation", "recolor", "scale"),
    )


def test_change_detector_classifies_property_appearance_and_disappearance() -> None:
    matcher = InstanceMatcher()
    proposal = matcher.compare(
        candidate_id="candidate-a",
        current=_instance(position=(2.0, 0.0), scale=(2.0, 2.0), color="blue", shape="circle"),
        stored_identity_id="object-a",
        stored=_instance(),
    )
    changes = ChangeDetector().detect(
        proposals={"candidate-a": proposal},
        correspondence={"candidate-a": ("object-a",)},
        before_identity_ids=("object-a", "object-gone"),
        after_candidate_ids=("candidate-a", "candidate-new"),
    )

    assert {item.kind for item in changes} == {
        "appeared",
        "disappeared",
        "moved",
        "recolored",
        "resized",
        "reshaped",
    }
    assert len({item.change_id for item in changes}) == len(changes)


def test_change_detector_retains_explicit_split_and_merge_structure() -> None:
    changes = ChangeDetector().detect(
        proposals={},
        correspondence={
            "candidate-left": ("compound",),
            "candidate-right": ("compound",),
            "candidate-merged": ("object-a", "object-b"),
        },
        before_identity_ids=("compound", "object-a", "object-b"),
        after_candidate_ids=("candidate-left", "candidate-right", "candidate-merged"),
    )

    split = next(item for item in changes if item.kind == "split")
    merged = next(item for item in changes if item.kind == "merged")
    assert split.before_identity_ids == ("compound",)
    assert split.after_candidate_ids == ("candidate-left", "candidate-right")
    assert merged.before_identity_ids == ("object-a", "object-b")
    assert merged.after_candidate_ids == ("candidate-merged",)


def _encounter(cells, *, position=(0.0, 0.0)):
    return SimpleNamespace(
        instance=InstanceParameters(position=position, geometry={"cells": cells})
    )


def test_structural_correspondence_infers_exact_splits_and_merges() -> None:
    inferer = StructuralCorrespondenceInferer()
    split = inferer.infer(
        {"whole": _encounter(((0, 0), (1, 0), (2, 0), (3, 0)))},
        {
            "left": _encounter(((0, 0), (1, 0))),
            "right": _encounter(((2, 0), (3, 0))),
        },
    )
    merged = inferer.infer(
        {
            "left": _encounter(((0, 0), (1, 0))),
            "right": _encounter(((0, 0), (1, 0)), position=(2.0, 0.0)),
        },
        {"whole": _encounter(((0, 0), (1, 0), (2, 0), (3, 0)))},
    )

    assert split == {"left": ("whole",), "right": ("whole",)}
    assert merged == {"whole": ("left", "right")}


def test_structural_correspondence_does_not_force_overlap_or_partial_coverage() -> None:
    inferred = StructuralCorrespondenceInferer().infer(
        {"whole": _encounter(((0, 0), (1, 0), (2, 0)))},
        {
            "overlap-a": _encounter(((0, 0), (1, 0))),
            "overlap-b": _encounter(((1, 0), (2, 0))),
            "unrelated": _encounter(((7, 7),)),
        },
    )

    assert inferred == {}


def test_encounter_change_session_persists_automatically_inferred_split() -> None:
    store = SymbolicStore(InMemorySemanticBackend())
    store.put_encounter(
        EncounterRecord.create(
            observation_id="before",
            action_tree_node="nodes/1",
            candidate_identity_id="whole",
            instance=InstanceParameters(
                geometry={"cells": ((0, 0), (1, 0), (2, 0), (3, 0))}
            ),
        )
    )
    for candidate_id, cells in (
        ("left", ((0, 0), (1, 0))),
        ("right", ((2, 0), (3, 0))),
    ):
        store.put_encounter(
            EncounterRecord.create(
                observation_id="after",
                action_tree_node="nodes/2",
                candidate_identity_id=candidate_id,
                instance=InstanceParameters(geometry={"cells": cells}),
            )
        )

    proposals, changes, _residuals = EncounterChangeSession(store).detect(
        "before", "after"
    )

    assert {(item.candidate_id, item.stored_identity_id) for item in proposals} == {
        ("left", "whole"),
        ("right", "whole"),
    }
    assert [item.kind for item in changes] == ["split"]
    assert store.values("object_changes") == changes


def test_encounter_change_session_persists_and_replays_inferred_merge() -> None:
    store = SymbolicStore(InMemorySemanticBackend())
    for candidate_id, position in (("left", (0.0, 0.0)), ("right", (2.0, 0.0))):
        store.put_encounter(
            EncounterRecord.create(
                observation_id="before",
                action_tree_node="nodes/1",
                candidate_identity_id=candidate_id,
                instance=InstanceParameters(
                    position=position, geometry={"cells": ((0, 0), (1, 0))}
                ),
            )
        )
    store.put_encounter(
        EncounterRecord.create(
            observation_id="after",
            action_tree_node="nodes/2",
            candidate_identity_id="whole",
            instance=InstanceParameters(
                geometry={"cells": ((0, 0), (1, 0), (2, 0), (3, 0))}
            ),
        )
    )

    proposals, changes, residuals = EncounterChangeSession(store).detect(
        "before", "after"
    )
    replayed = SymbolicStore(InMemorySemanticBackend()).replay(store.snapshot())

    assert {(item.candidate_id, item.stored_identity_id) for item in proposals} == {
        ("whole", "left"),
        ("whole", "right"),
    }
    assert [item.kind for item in changes] == ["merged"]
    assert residuals == ()
    assert replayed.values("object_changes") == changes
    assert replayed.values("match_proposals") == store.values("match_proposals")
