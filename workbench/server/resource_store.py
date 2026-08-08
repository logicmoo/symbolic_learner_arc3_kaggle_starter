from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path, PurePosixPath
from threading import RLock
from typing import Any, Iterable


class FilesystemProvider:
    """The single compatibility boundary for workspace filesystem access.

    It delegates to the real filesystem today. A later provider may expose the
    same logical paths from a MeTTa server or AtomSpace without changing callers.
    """

    def __init__(self) -> None:
        self._metrics: Counter[str] = Counter()
        self._metrics_lock = RLock()

    def _record(self, operation: str, path: Path | None = None) -> None:
        with self._metrics_lock:
            self._metrics[operation] += 1
            if path is not None:
                self._metrics[f"suffix:{path.suffix.lower() or '(none)'}"] += 1

    def metrics(self) -> dict[str, int]:
        with self._metrics_lock:
            return dict(self._metrics)

    def resolve(self, root: Path, logical_path: str = ".") -> Path:
        resolved_root = root.resolve()
        relative = PurePosixPath(logical_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"resource path escapes provider root: {logical_path}")
        path = (resolved_root / Path(*relative.parts)).resolve()
        if path != resolved_root and resolved_root not in path.parents:
            raise ValueError(f"resource path escapes provider root: {logical_path}")
        return path

    def glob(self, root: Path, directories: Iterable[str], pattern: str = "*.json") -> list[Path]:
        self._record("scan")
        paths = [path for directory in directories for path in self.resolve(root, directory).glob(pattern)]
        return sorted(set(paths), key=lambda path: (path.name.lower(), path.as_posix().lower()))

    def rglob(self, root: Path, pattern: str) -> list[Path]:
        self._record("scan")
        return sorted(root.rglob(pattern), key=lambda path: path.as_posix().lower())

    def iterdir(self, path: Path) -> list[Path]:
        self._record("scan", path)
        return sorted(path.iterdir(), key=lambda item: item.name.lower()) if path.is_dir() else []

    def exists(self, path: Path) -> bool:
        self._record("metadata", path)
        return path.exists()

    def is_file(self, path: Path) -> bool:
        self._record("metadata", path)
        return path.is_file()

    def is_dir(self, path: Path) -> bool:
        self._record("metadata", path)
        return path.is_dir()

    def stat(self, path: Path):
        self._record("metadata", path)
        return path.stat()

    def make_directory(self, path: Path, *, parents: bool = True, exist_ok: bool = True) -> None:
        self._record("mkdir", path)
        path.mkdir(parents=parents, exist_ok=exist_ok)

    def read_text(self, path: Path, *, encoding: str = "utf-8") -> str:
        self._record("read", path)
        return path.read_text(encoding=encoding)

    def write_text(self, path: Path, content: str, *, encoding: str = "utf-8") -> None:
        self._record("write", path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)

    def read_bytes(self, path: Path) -> bytes:
        self._record("read", path)
        return path.read_bytes()

    def read_json(self, path: Path) -> Any:
        return json.loads(self.read_text(path))

    def write_json(self, path: Path, document: Any) -> None:
        self.write_text(path, json.dumps(document, indent=2, ensure_ascii=False) + "\n")

    def delete(self, path: Path) -> None:
        self._record("delete", path)
        path.unlink(missing_ok=True)

    def replace(self, source: Path, target: Path) -> None:
        self._record("replace", target)
        source.replace(target)

    def copy_tree(self, source: Path, target: Path, *, ignored_names: Iterable[str] = ()) -> None:
        self._record("copy", target)
        shutil.copytree(source, target, ignore=shutil.ignore_patterns(*ignored_names))

    def delete_tree(self, path: Path) -> None:
        self._record("delete-tree", path)
        shutil.rmtree(path, ignore_errors=True)


class FilesystemProviderSingleton:
    def __init__(self) -> None:
        self._provider: FilesystemProvider = FilesystemProvider()
        self._lock = RLock()

    def get(self) -> FilesystemProvider:
        with self._lock:
            return self._provider

    def replace(self, provider: FilesystemProvider) -> None:
        with self._lock:
            self._provider = provider


filesystem_provider = FilesystemProviderSingleton()


def get_filesystem_provider() -> FilesystemProvider:
    return filesystem_provider.get()
