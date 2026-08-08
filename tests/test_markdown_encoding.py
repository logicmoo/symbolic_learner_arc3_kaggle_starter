from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "normalize_markdown_encoding.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = spec_from_file_location("normalize_markdown_encoding", SCRIPT)
assert SPEC and SPEC.loader
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_repairs_single_and_double_decoded_utf8() -> None:
    assert MODULE.repair_text("â† Back") == "← Back"
    assert MODULE.repair_text("Ã¢â€ Â Back") == "← Back"
    assert MODULE.repair_text("meaningâ€”implementation") == "meaning—implementation"


def test_repository_markdown_has_no_known_mojibake_markers() -> None:
    offenders = []
    for path in MODULE.markdown_files(ROOT):
        text = path.read_text(encoding="utf-8")
        repaired = "".join(MODULE.repair_text(line) for line in text.splitlines(keepends=True))
        if repaired != text:
            offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []
