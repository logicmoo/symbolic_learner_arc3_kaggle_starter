from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
PYTHON_ROOT = ROOT / "python"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

import pytest
from fastapi import HTTPException

import arc3_play_api
import arc_interactive_sync


@pytest.fixture(autouse=True)
def _isolated_thumbnail_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    cache_dir = tmp_path / "environment_thumbnails"
    monkeypatch.setattr(arc3_play_api, "_THUMBNAIL_CACHE_DIR", cache_dir)
    monkeypatch.setattr(arc3_play_api, "_catalog_cache", None)
    return cache_dir


def _fake_catalog(*_args, **_kwargs) -> list[dict]:
    return [
        {"game_id": "ez01-63be02fb", "short_id": "ez01", "title": "Ez01", "tags": []},
    ]


def test_thumbnail_path_sanitizes_short_id() -> None:
    path = arc3_play_api._thumbnail_path("weird/../id?name")
    assert path.name == "weird_.._id_name.png"
    assert path.parent == arc3_play_api._THUMBNAIL_CACHE_DIR


def test_game_preview_renders_and_caches_on_first_request(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(arc3_play_api, "_game_catalog", _fake_catalog)
    render_calls: list[str] = []

    def fake_render(full_game_id: str) -> bytes:
        render_calls.append(full_game_id)
        return b"PNGDATA"

    monkeypatch.setattr(arc3_play_api, "_render_game_preview_png", fake_render)

    response = arc3_play_api.game_preview("ez01")

    assert render_calls == ["ez01-63be02fb"]
    cache_path = arc3_play_api._thumbnail_path("ez01")
    assert cache_path.is_file()
    assert cache_path.read_bytes() == b"PNGDATA"
    assert Path(response.path) == cache_path


def test_game_preview_returns_cached_file_without_rendering_again(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(arc3_play_api, "_game_catalog", _fake_catalog)
    cache_path = arc3_play_api._thumbnail_path("ez01")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(b"ALREADY-CACHED")

    def fail_if_called(*_args, **_kwargs) -> bytes:
        raise AssertionError("should not re-render a cached preview")

    monkeypatch.setattr(arc3_play_api, "_render_game_preview_png", fail_if_called)

    response = arc3_play_api.game_preview("ez01")

    assert Path(response.path).read_bytes() == b"ALREADY-CACHED"


def test_game_preview_refresh_forces_re_render(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(arc3_play_api, "_game_catalog", _fake_catalog)
    cache_path = arc3_play_api._thumbnail_path("ez01")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(b"STALE")

    render_calls: list[str] = []

    def fake_render(full_game_id: str) -> bytes:
        render_calls.append(full_game_id)
        return b"FRESH"

    monkeypatch.setattr(arc3_play_api, "_render_game_preview_png", fake_render)

    response = arc3_play_api.game_preview("ez01", refresh=True)

    assert render_calls == ["ez01-63be02fb"]
    assert Path(response.path).read_bytes() == b"FRESH"


def test_game_preview_404_for_unknown_game(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(arc3_play_api, "_game_catalog", _fake_catalog)

    with pytest.raises(HTTPException) as error:
        arc3_play_api.game_preview("does-not-exist")
    assert error.value.status_code == 404


def test_game_preview_502_when_rendering_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(arc3_play_api, "_game_catalog", _fake_catalog)

    def broken_render(*_args, **_kwargs) -> bytes:
        raise RuntimeError("boom")

    monkeypatch.setattr(arc3_play_api, "_render_game_preview_png", broken_render)

    with pytest.raises(HTTPException) as error:
        arc3_play_api.game_preview("ez01")
    assert error.value.status_code == 502


def test_sync_games_endpoint_delegates_to_shared_sync_module_and_busts_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    source = tmp_path / "arc-interactive-env"
    dest = tmp_path / "workbench-env"
    version_dir = source / "ez01" / "63be02fb"
    version_dir.mkdir(parents=True)
    (version_dir / "metadata.json").write_text('{"game_id": "ez01-63be02fb"}', encoding="utf-8")
    (version_dir / "ez01.py").write_text("# game\n", encoding="utf-8")

    monkeypatch.setattr(arc_interactive_sync, "DEFAULT_SOURCE", source)
    monkeypatch.setattr(arc_interactive_sync, "DEFAULT_DEST", dest)

    catalog_calls: list[bool] = []

    def fake_catalog(refresh: bool = False) -> list[dict]:
        catalog_calls.append(refresh)
        return []

    monkeypatch.setattr(arc3_play_api, "_game_catalog", fake_catalog)

    summary = arc3_play_api.sync_games_from_arc_interactive()

    assert summary["available"] is True
    assert summary["copied"] == 1
    assert summary["newStems"] == ["ez01"]
    assert (dest / "ez01" / "63be02fb" / "metadata.json").is_file()
    # A new game was copied -> the catalog cache must be busted so /games
    # reflects it immediately, not after the 600s TTL.
    assert True in catalog_calls


def test_sync_games_endpoint_reports_unavailable_when_no_sibling_checkout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    missing_source = tmp_path / "does-not-exist"
    monkeypatch.setattr(arc_interactive_sync, "DEFAULT_SOURCE", missing_source)
    monkeypatch.setattr(arc_interactive_sync, "DEFAULT_DEST", tmp_path / "dest")
    monkeypatch.setattr(arc3_play_api, "_game_catalog", lambda refresh=False: [])

    summary = arc3_play_api.sync_games_from_arc_interactive()

    assert summary["available"] is False
    assert summary["copied"] == 0
