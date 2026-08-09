from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from datatype_library import interface_type_inventory, load_workspace_concrete_datatype_records, load_workspace_datatype_records, load_workspace_representation_records, resolve_datatype_representation
from representation_planner import plan_representation_conversion


SHARED = ROOT / "workbench" / "workspaces" / "shared"
ARC3 = ROOT / "workbench" / "workspaces" / "arc3"


def test_image_is_abstract_datatype_with_multiple_representations() -> None:
    datatypes = {record["document"]["id"]: record["document"] for record in load_workspace_datatype_records(SHARED) if record.get("document")}
    image = datatypes["image"]
    assert image["kind"] == "semantic_datatype"
    assert image["preferredChild"] == "bitmap"
    assert {"bitmap", "logo_program", "scene_graph", "natural_language"}.issubset(image["children"])


def test_object_is_a_first_class_semantic_datatype() -> None:
    datatypes = {record["document"]["id"]: record["document"] for record in load_workspace_datatype_records(SHARED) if record.get("document")}
    representations = {record["document"]["id"]: record["document"] for record in load_workspace_representation_records(SHARED) if record.get("document")}
    object_type = datatypes["object"]
    assert object_type["kind"] == "semantic_datatype"
    assert object_type["parents"] == ["information"]
    assert object_type["preferredChild"] == "json_object"
    assert object_type["children"] == ["json_object", "python_object"]
    assert "object" in datatypes["information"]["children"]
    assert "object" in representations["json_object"]["parents"]
    assert "object" in representations["python_object"]["parents"]


def test_semantic_datatype_hierarchy_is_explicit_and_bidirectional() -> None:
    datatypes = {record["document"]["id"]: record["document"] for record in load_workspace_datatype_records(SHARED) if record.get("document")}
    assert datatypes["identity_map"]["parents"] == ["information"]
    assert "identity_map" in datatypes["information"]["children"]
    assert datatypes["human_intervention"]["parents"] == ["intervention"]
    assert "human_intervention" in datatypes["intervention"]["children"]
    assert datatypes["objectified_observation"]["parents"] == ["observation"]
    assert "objectified_observation" in datatypes["observation"]["children"]


def test_bitmap_encodings_are_independent_concrete_datatypes() -> None:
    representations = {record["document"]["id"]: record["document"] for record in load_workspace_representation_records(SHARED) if record.get("document")}
    bitmap = representations["bitmap"]
    assert bitmap["parents"] == ["image"]
    assert set(bitmap["children"]) == {"png", "jpeg", "bmp"}
    concrete = {record["document"]["id"]: record["document"] for record in load_workspace_concrete_datatype_records(SHARED) if record.get("document")}
    assert concrete["png"]["kind"] == "concrete_datatype"
    assert concrete["png"]["parents"] == ["bitmap"]
    assert concrete["json"]["parents"] == ["json_object", "object_list", "scene_graph"]


def test_workspace_inherits_shared_representations() -> None:
    resolved = resolve_datatype_representation(ARC3, "image", "scene_graph")
    assert resolved["datatype"]["id"] == "image"
    assert resolved["representation"]["id"] == "scene_graph"
    assert resolved["representationRecord"]["source"] == "shared"


def test_datatype_resolution_accepts_interface_case() -> None:
    resolved = resolve_datatype_representation(ARC3, "Object", "JSON_OBJECT")
    assert resolved["datatype"]["id"] == "object"
    assert resolved["representation"]["id"] == "json_object"


def test_interface_inventory_scans_canonical_workflows_and_matches_case() -> None:
    inventory = interface_type_inventory(ARC3)
    undeclared = set(inventory["undeclaredDatatypes"])
    assert {"Image", "Text", "Object"}.isdisjoint(undeclared)
    assert not any(datatype.startswith("$") for datatype in undeclared)
    workflow_references = [reference for reference in inventory["references"] if reference["ownerKind"] == "workflow"]
    assert any(reference["ownerId"] == "arc3_observe_choose_record" and reference["datatype"] == "Object" for reference in workflow_references)


def test_planner_finds_multi_step_bitmap_to_logo_path() -> None:
    plan = plan_representation_conversion(ARC3, "image", "bitmap", "logo_program")
    assert plan["datatype"] == "image"
    assert plan["from"] == "bitmap"
    assert plan["to"] == "logo_program"
    assert len(plan["steps"]) == 2
    assert plan["steps"][0]["from"] == "bitmap"
    assert plan["steps"][-1]["to"] == "logo_program"
