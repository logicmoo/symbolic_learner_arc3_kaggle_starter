from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from datatype_library import load_workspace_concrete_datatype_records, load_workspace_datatype_records, load_workspace_representation_records, resolve_datatype_representation
from representation_planner import plan_representation_conversion


SHARED = ROOT / "workbench" / "workspaces" / "shared"
ARC3 = ROOT / "workbench" / "workspaces" / "arc3"


def test_image_is_abstract_datatype_with_multiple_representations() -> None:
    datatypes = {record["document"]["id"]: record["document"] for record in load_workspace_datatype_records(SHARED) if record.get("document")}
    image = datatypes["image"]
    assert image["kind"] == "semantic_datatype"
    assert image["preferredChild"] == "bitmap"
    assert {"bitmap", "logo_program", "scene_graph", "natural_language"}.issubset(image["children"])


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


def test_planner_finds_multi_step_bitmap_to_logo_path() -> None:
    plan = plan_representation_conversion(ARC3, "image", "bitmap", "logo_program")
    assert plan["datatype"] == "image"
    assert plan["from"] == "bitmap"
    assert plan["to"] == "logo_program"
    assert len(plan["steps"]) == 2
    assert plan["steps"][0]["from"] == "bitmap"
    assert plan["steps"][-1]["to"] == "logo_program"
