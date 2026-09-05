"""Seed/ingest recognitionReduce with all 200 items (20 slugs x c1..c10).

Merges real rows from data/recognition_reduce/manifest.json when present; else
seeds empty rows so thumbnails + attribution render immediately. Writes through
the app's own page-state idiom (lock + load_state + _save_page_state_payload) so
it is atomic and shard-safe. Re-run after the manifest fills to pick up rows.
"""
import sys
import json
from pathlib import Path

SERVER = r"C:\snet\PeTTa\repos\symbolic_learner_workbench\workbench\server"
sys.path.insert(0, SERVER)

import video_import_api as vip  # noqa: E402
from video_import_pipeline import load_state  # noqa: E402

WS = "guess201_reid"
root = Path(vip._workspace_root(WS))
rr_dir = root / "data" / "recognition_reduce"
cur_dir = root / "data" / "arc3_games" / "curated" / "recognition_reduce"

SLUG_ORDER = [
    "bart_simpson", "lisa_simpson", "homer_simpson", "marge_simpson",
    "maggie_simpson", "grandpa_simpson", "spongebob", "patrick_star",
    "squidward", "scooby_doo", "shaggy", "mickey_mouse", "minnie_mouse",
    "donald_duck", "goofy", "bugs_bunny", "pikachu", "mario", "sonic", "moana",
]
COND_ORDER = [
    "c1_bw", "c2_flip", "c3_rot45", "c4_busy", "c5_new",
    "c6_verybusy", "c7_withchars", "c8_typical", "c9_colorful", "c10_modality",
]
TRANSFORMS = {"c1_bw", "c2_flip", "c3_rot45"}

prov_path = Path(
    r"C:\Users\dougl\.copilot\session-state\d8ae6703-980e-4204-b654-bd655b9bf145"
    r"\files\cartoons\guess201\reid\scenes\provenance.json"
)
prov = {}
if prov_path.exists():
    try:
        prov = json.loads(prov_path.read_text(encoding="utf-8"))
    except Exception:
        prov = {}

manifest = {}
tiers = []
mf = rr_dir / "manifest.json"
if not mf.exists():
    mf = cur_dir / "manifest.json"
if mf.exists():
    try:
        mj = json.loads(mf.read_text(encoding="utf-8"))
        tiers = mj.get("tiers") or []
        for it in (mj.get("items") or []):
            if isinstance(it, dict) and it.get("id"):
                manifest[it["id"]] = it
    except Exception:
        pass


def base(p):
    return str(p or "").replace("\\", "/").split("/")[-1]


def resolve_rel(sub, name):
    if not name:
        return ""
    for b in (f"data/recognition_reduce/{sub}",
              f"data/arc3_games/curated/recognition_reduce/{sub}"):
        if (root / b / name).exists():
            return f"{b}/{name}"
    return f"data/recognition_reduce/{sub}/{name}"


def resolve_input(idv):
    return resolve_rel("pool", f"{idv}.jpg")


items = []
with_rows = 0
with_thumb = 0
for slug in SLUG_ORDER:
    for cond in COND_ORDER:
        idv = f"{slug}__{cond}"
        m = manifest.get(idv) or {}
        pv = prov.get(idv) or {}
        src = m.get("source") or pv.get("source") or (
            "transform" if cond in TRANSFORMS else "web")
        surl = m.get("source_url") or pv.get("source_url") or ""
        input_rel = resolve_input(idv)
        if (root / input_rel).exists():
            with_thumb += 1
        item = {
            "id": idv,
            "slug": slug,
            "cond": cond,
            "label": m.get("label") or slug.replace("_", " "),
            "input": f"{idv}.jpg",
            "inputPath": input_rel,
            "source": src,
            "source_url": surl,
            "scene": cond not in TRANSFORMS,
            "rows": [],
        }
        chip = base(m.get("chip"))
        if chip:
            item["chip"] = chip
            item["chipPath"] = resolve_rel("chips", chip)
        rows = []
        for r in (m.get("rows") or []):
            if not isinstance(r, dict):
                continue
            rr = dict(r)
            mb = base(r.get("metta"))
            if mb:
                rr["mettaPath"] = resolve_rel("sym", mb)
            rows.append(rr)
        item["rows"] = rows
        if rows:
            with_rows += 1
        items.append(item)

payload = {"tiers": tiers, "count": len(items), "items": items}
with vip._page_state_lock(WS):
    state = load_state(WS)
    state["recognitionReduce"] = payload
    vip._save_page_state_payload({"workspaceId": WS, "state": state})

print(f"ingested items={len(items)} with_thumb={with_thumb} "
      f"with_rows={with_rows} tiers={len(tiers)} manifest_items={len(manifest)}")
