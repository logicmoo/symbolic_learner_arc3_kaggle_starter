from object_memory import ChangeDetector, InstanceMatcher, InstanceParameters


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
