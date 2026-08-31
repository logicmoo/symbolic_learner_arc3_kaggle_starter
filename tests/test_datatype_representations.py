from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from datatype_library import interface_type_inventory, load_workspace_concrete_datatype_records, load_workspace_datatype_records, load_workspace_representation_records, resolve_datatype_representation
from representation_planner import plan_representation_conversion
from resource_relationships import relationship_ids


SHARED = ROOT / "workbench" / "workspaces" / "shared_library_system"
ARC3 = ROOT / "workbench" / "workspaces" / "shared_library_arc3"
ARC3_OBSERVE = ROOT / "workbench" / "workspaces" / "vision_observe_choose_record"


def test_image_is_abstract_datatype_with_multiple_representations() -> None:
    datatypes = {record["document"]["id"]: record["document"] for record in load_workspace_datatype_records(SHARED) if record.get("document")}
    image = datatypes["image"]
    assert image["kind"] == "semantic_datatype"
    assert image["preferredImplementation"] == "bitmap"
    assert {"bitmap", "logo_program", "scene_graph", "natural_language"}.issubset(image["implementedBy"])


def test_object_is_a_first_class_semantic_datatype() -> None:
    datatypes = {record["document"]["id"]: record["document"] for record in load_workspace_datatype_records(SHARED) if record.get("document")}
    representations = {record["document"]["id"]: record["document"] for record in load_workspace_representation_records(SHARED) if record.get("document")}
    object_type = datatypes["object"]
    assert object_type["kind"] == "semantic_datatype"
    assert relationship_ids(object_type["implements"]) == ["information"]
    assert object_type["preferredImplementation"] == "json_object"
    assert relationship_ids(object_type["implementedBy"]) == ["json_object", "python_object"]
    assert "object" in datatypes["information"]["implementedBy"]
    assert "object" in representations["json_object"]["implements"]
    assert "object" in representations["python_object"]["implements"]


def test_semantic_datatype_hierarchy_is_explicit_and_bidirectional() -> None:
    datatypes = {record["document"]["id"]: record["document"] for record in load_workspace_datatype_records(SHARED) if record.get("document")}
    assert relationship_ids(datatypes["identity_map"]["implements"]) == ["information"]
    assert "identity_map" in datatypes["information"]["implementedBy"]
    assert relationship_ids(datatypes["human_intervention"]["implements"]) == ["intervention"]
    assert "human_intervention" in datatypes["intervention"]["implementedBy"]
    assert relationship_ids(datatypes["objectified_observation"]["implements"]) == ["observation"]
    assert "objectified_observation" in datatypes["observation"]["implementedBy"]


def test_numeric_document_and_program_contract_types_are_declared() -> None:
    datatypes = {record["document"]["id"]: record["document"] for record in load_workspace_datatype_records(SHARED) if record.get("document")}
    assert relationship_ids(datatypes["number"]["implements"]) == ["information"]
    assert relationship_ids(datatypes["file_reference"]["implements"]) == ["information"]
    assert relationship_ids(datatypes["program"]["implements"]) == ["information"]
    assert set(datatypes["program"]["implementedBy"]) == {"prolog_program", "turtle_program_set"}
    assert relationship_ids(datatypes["prolog_program"]["implements"]) == ["program"]
    assert relationship_ids(datatypes["turtle_program_set"]["implements"]) == ["program"]
    assert {"number", "file_reference", "program"}.issubset(datatypes["information"]["implementedBy"])


def test_evidence_and_reasoning_contract_types_are_declared() -> None:
    datatypes = {record["document"]["id"]: record["document"] for record in load_workspace_datatype_records(SHARED) if record.get("document")}
    expected = {"artifact_bundle", "change_description", "evidence", "evidence_bundle", "hypothesis_set", "rule_set"}
    assert expected.issubset(datatypes)
    assert expected.issubset(datatypes["information"]["implementedBy"])
    assert relationship_ids(datatypes["evidence"]["implementedBy"]) == ["transition_evidence"]
    assert relationship_ids(datatypes["transition_evidence"]["implements"]) == ["evidence"]


def test_bitmap_encodings_are_independent_concrete_datatypes() -> None:
    representations = {record["document"]["id"]: record["document"] for record in load_workspace_representation_records(SHARED) if record.get("document")}
    bitmap = representations["bitmap"]
    assert relationship_ids(bitmap["implements"]) == ["image"]
    assert set(bitmap["implementedBy"]) == {"png", "jpeg", "bmp"}
    concrete = {record["document"]["id"]: record["document"] for record in load_workspace_concrete_datatype_records(SHARED) if record.get("document")}
    assert concrete["png"]["kind"] == "concrete_datatype"
    assert relationship_ids(concrete["png"]["implements"]) == ["bitmap"]
    assert relationship_ids(concrete["json"]["implements"]) == ["json_object", "object_list", "scene_graph"]


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
    inventory = interface_type_inventory(ARC3_OBSERVE)
    undeclared = set(inventory["undeclaredDatatypes"])
    assert {"Image", "Text", "Object", "IdentityMap", "WorldModel"}.isdisjoint(undeclared)
    assert {"Number", "FileReference", "Markdown", "Program", "PrologProgram", "TurtleProgramSet"}.isdisjoint(undeclared)
    assert not any(datatype.startswith("$") for datatype in undeclared)
    assert inventory["builtinDatatypes"] == ["Any"]
    assert inventory["undeclaredDatatypes"] == []
    assert inventory["undeclaredRepresentations"] == []
    workflow_references = [reference for reference in inventory["references"] if reference["ownerKind"] == "workflow"]
    assert any(reference["ownerId"] == "vision_observe_choose_record" and reference["datatype"] == "Object" for reference in workflow_references)


def test_planner_finds_multi_step_bitmap_to_logo_path() -> None:
    plan = plan_representation_conversion(ARC3, "image", "bitmap", "logo_program")
    assert plan["datatype"] == "image"
    assert plan["from"] == "bitmap"
    assert plan["to"] == "logo_program"
    assert len(plan["steps"]) == 2
    assert plan["steps"][0]["from"] == "bitmap"
    assert plan["steps"][-1]["to"] == "logo_program"
