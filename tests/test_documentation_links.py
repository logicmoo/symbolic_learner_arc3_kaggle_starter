from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ROOT_DOCUMENTS = (
    "ARC3_DEBUGGER_AND_KAGGLE.md",
    "SOW_PHASE_ARCHITECTURE.md",
    "IMPLEMENTATION_BACKLOG.md",
    "FILE_TREE.md",
)


def _local_links(path: Path) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8")
    return tuple(
        target
        for target in MARKDOWN_LINK.findall(text)
        if not target.startswith(("http://", "https://", "mailto:", "#"))
    )


def test_all_maintained_documentation_is_at_repository_root() -> None:
    for relative in ROOT_DOCUMENTS:
        assert (ROOT / relative).is_file(), relative

    assert not (ROOT / "DOCUMENTATION.md").exists()
    docs_dir = ROOT / "docs"
    if docs_dir.exists():
        assert not tuple(docs_dir.glob("*.md")), "maintained Markdown must stay at root"


def test_top_level_readme_is_documentation_index() -> None:
    root_text = (ROOT / "README.md").read_text(encoding="utf-8")
    for relative in ROOT_DOCUMENTS:
        assert f"]({relative})" in root_text, relative
    assert "documentation index" in root_text.lower()


def test_file_tree_local_links_exist_and_have_descriptions() -> None:
    file_tree = ROOT / "FILE_TREE.md"
    lines = file_tree.read_text(encoding="utf-8").splitlines()
    links = _local_links(file_tree)
    assert links

    for target in links:
        clean_target = target.split("#", 1)[0]
        resolved = (file_tree.parent / clean_target).resolve()
        assert resolved.exists(), target

    for line in lines:
        match = MARKDOWN_LINK.search(line)
        if match:
            target = match.group(1)
            if not target.startswith(("http://", "https://", "mailto:", "#")):
                assert " — " in line, line


def test_file_tree_links_all_connected_architecture_files() -> None:
    links = set(_local_links(ROOT / "FILE_TREE.md"))
    expected = {
        "README.md",
        "ARC3_DEBUGGER_AND_KAGGLE.md",
        "SOW_PHASE_ARCHITECTURE.md",
        "IMPLEMENTATION_BACKLOG.md",
        "FILE_TREE.md",
        "python/object_memory/models.py",
        "python/object_memory/providers.py",
        "python/object_memory/forms.py",
        "python/object_memory/adapters.py",
        "python/object_memory/memory.py",
        "python/object_memory/prediction.py",
        "python/object_memory/learning.py",
        "python/object_memory/integration.py",
        "prolog/object_memory_contract.pl",
        "prolog/generative_form.pl",
        "prolog/residual_gate.pl",
        "prolog/single_writer.pl",
        "prolog/transition_analysis.pl",
        "prolog/transformation_learning.pl",
        "prolog/rule_induction.pl",
        "prolog/rule_ranking.pl",
        "prolog/transition_rules.pl",
        "prolog/prediction_ledger.pl",
        "prolog/prediction_evaluation.pl",
        "prolog/game_object_learner_api.pl",
        "tests/test_object_memory_contracts.py",
        "tests/test_documentation_links.py",
        "prolog/test_object_memory.pl",
    }
    assert expected.issubset(links), sorted(expected.difference(links))
