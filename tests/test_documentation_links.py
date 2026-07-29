from __future__ import annotations

from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ROOT_DOCUMENTS = (
    "DEBUGGER.md",
    "KAGGLE.md",
    "SOW_PHASE_ARCHITECTURE.md",
    "TODO.md",
    "FILE_TREE.md",
)


def _local_links(path: Path) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8")
    return tuple(
        target
        for target in MARKDOWN_LINK.findall(text)
        if not target.startswith(("http://", "https://", "mailto:", "#"))
    )


def _maintained_markdown() -> tuple[Path, ...]:
    excluded = {".git", ".venv", "vendor", "action_trees", "reference"}
    return tuple(
        path
        for path in ROOT.rglob("*.md")
        if not excluded.intersection(path.relative_to(ROOT).parts)
    )


def test_root_document_set_and_old_names() -> None:
    for relative in ROOT_DOCUMENTS:
        assert (ROOT / relative).is_file(), relative

    for obsolete in (
        "ARC3_DEBUGGER_AND_KAGGLE.md",
        "IMPLEMENTATION_BACKLOG.md",
        "DOCUMENTATION.md",
    ):
        assert not (ROOT / obsolete).exists(), obsolete

    docs_dir = ROOT / "docs"
    if docs_dir.exists():
        assert not tuple(docs_dir.glob("*.md")), "maintained Markdown must stay at root"


def test_top_level_readme_links_every_root_document() -> None:
    root_text = (ROOT / "README.md").read_text(encoding="utf-8")
    for relative in ROOT_DOCUMENTS:
        assert f"]({relative})" in root_text, relative


def test_every_markdown_links_back_to_root_readme() -> None:
    root_readme = (ROOT / "README.md").resolve()
    for path in _maintained_markdown():
        if path.resolve() == root_readme:
            continue
        resolved_links = {
            (path.parent / target.split("#", 1)[0]).resolve()
            for target in _local_links(path)
            if target.split("#", 1)[0]
        }
        assert root_readme in resolved_links, path.relative_to(ROOT).as_posix()


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
                assert " — " in line or "Back to top-level README" in line, line


def test_file_tree_links_all_connected_architecture_files() -> None:
    links = set(_local_links(ROOT / "FILE_TREE.md"))
    expected = {
        "README.md",
        "DEBUGGER.md",
        "KAGGLE.md",
        "SOW_PHASE_ARCHITECTURE.md",
        "TODO.md",
        "FILE_TREE.md",
        "pyproject.toml",
        "requirements.txt",
        "scripts/_runtime.py",
        "scripts/interactive_runner.py",
        "scripts/run_webui.py",
        "scripts/prolog_controlled_runner.py",
        "scripts/re_play.py",
        "scripts/my_play.py",
        "scripts/me_play.py",
        "scripts/he_play.py",
        "scripts/play_local.py",
        "scripts/build_notebook.py",
        "scripts/slim_framework.py",
        "python/interactive_runner.py",
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
        "tests/test_runtime_home.py",
        "prolog/test_object_memory.pl",
    }
    assert expected.issubset(links), sorted(expected.difference(links))


def test_readme_documents_every_runnable_demo() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    required_commands = (
        "python scripts/interactive_runner.py ls20",
        "python scripts/run_webui.py --game ls20",
        "python scripts/prolog_controlled_runner.py",
        "python scripts/re_play.py",
        "python scripts/my_play.py",
        "python scripts/me_play.py",
        "python scripts/he_play.py",
        "python scripts/play_local.py --game ls20 --max-steps 200",
        "python scripts/build_notebook.py",
        "python scripts/slim_framework.py",
        "pytest -q",
        "swipl -q -s prolog/test_turtle_dsl.pl -g run_tests,halt",
        "swipl -q -s prolog/test_object_memory.pl -g run_tests,halt",
        "use_module('prolog/arc3_agent.pl')",
        "use_module('prolog/game_object_learner_api.pl')",
    )
    for command in required_commands:
        assert command in text, command


def test_runnable_examples_were_consolidated_into_scripts() -> None:
    for relative in (
        "scripts/interactive_runner.py",
        "scripts/run_webui.py",
        "scripts/prolog_controlled_runner.py",
        "scripts/re_play.py",
        "scripts/my_play.py",
        "scripts/me_play.py",
        "scripts/he_play.py",
    ):
        assert (ROOT / relative).is_file(), relative

    assert not (ROOT / "run_webui.py").exists()

    examples_dir = ROOT / "examples"
    if examples_dir.exists():
        assert not tuple(examples_dir.iterdir()), "examples/ should be empty or absent"

    server_text = (ROOT / "webui" / "server.py").read_text(encoding="utf-8")
    assert 'PROJECT_ROOT / "scripts" / "interactive_runner.py"' in server_text
    assert 'PROJECT_ROOT / "examples" / "interactive_runner.py"' not in server_text


def test_pyproject_metadata_and_extras_match_repository() -> None:
    project_file = ROOT / "pyproject.toml"
    data = tomllib.loads(project_file.read_text(encoding="utf-8"))
    project = data["project"]

    assert project["name"] == "logicmoo-arc3"
    assert project["description"] != "Add your description here"
    assert project["readme"] == "README.md"
    assert project["requires-python"] == ">=3.12"
    assert project["license"] == "LGPL-2.1-or-later"
    assert "arc-agi>=0.9.9" in project["dependencies"]

    extras = project["optional-dependencies"]
    assert {"debugger", "notebooks", "kaggle", "test", "all"}.issubset(extras)

    setuptools = data["tool"]["setuptools"]
    assert {"object_memory", "webui"}.issubset(set(setuptools["packages"]))
    assert data["tool"]["setuptools"]["package-dir"]["webui"] == "webui"
    assert "python" in data["tool"]["pytest"]["ini_options"]["pythonpath"]


def test_requirements_delegates_to_pyproject_extras() -> None:
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "-e .[debugger,notebooks,test]" in requirements
