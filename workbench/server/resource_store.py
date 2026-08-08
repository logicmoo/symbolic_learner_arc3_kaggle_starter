from __future__ import annotations

import json
import os
import shutil
from collections import Counter
from copy import deepcopy
from pathlib import Path, PurePosixPath
from fnmatch import fnmatch
from threading import RLock
from typing import Any, Iterable

from metta_resource_codec import json_document_to_metta, metta_documents_to_json, split_metta_document_spans


class FilesystemProvider:
    """The single compatibility boundary for workspace filesystem access.

    It delegates to the real filesystem today. A later provider may expose the
    same logical paths from a MeTTa server or AtomSpace without changing callers.
    """

    def __init__(self) -> None:
        self._metrics: Counter[str] = Counter()
        self._metrics_lock = RLock()
        self._json_cache: dict[Path, tuple[int, int, list[Any]]] = {}
        self._cache_lock = RLock()

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

    @staticmethod
    def _metta_path(path: Path) -> Path:
        return path.with_suffix(".metta") if path.suffix.lower() == ".json" else path

    def _physical_path(self, path: Path, *, writing: bool = False) -> Path:
        if path.suffix.lower() != ".json":
            return path
        metta_path = self._metta_path(path)
        if writing or metta_path.exists():
            return metta_path
        return path

    def _invalidate(self, path: Path) -> None:
        physical = self._physical_path(path, writing=True)
        with self._cache_lock:
            self._json_cache.pop(physical.resolve(), None)

    @staticmethod
    def _logical_json_path(path: Path) -> Path:
        return path.with_suffix(".json") if path.suffix.lower() == ".metta" else path

    def glob(self, root: Path, directories: Iterable[str], pattern: str = "*.json") -> list[Path]:
        self._record("scan")
        patterns = [pattern]
        if pattern.lower().endswith(".json"):
            patterns.append(pattern[:-5] + ".metta")
        paths = [
            self._logical_json_path(path)
            for directory in directories
            for candidate_pattern in patterns
            for path in self.resolve(root, directory).glob(candidate_pattern)
        ]
        return sorted(set(paths), key=lambda path: (path.name.lower(), path.as_posix().lower()))

    def rglob(self, root: Path, pattern: str, *, ignored_names: Iterable[str] = ()) -> list[Path]:
        self._record("scan")
        ignored = set(ignored_names)
        if ignored:
            matches: list[Path] = []
            for directory, names, files in os.walk(root, topdown=True):
                names[:] = [name for name in names if name not in ignored]
                matches.extend(Path(directory) / name for name in files if fnmatch(name, pattern))
            return sorted(matches, key=lambda path: path.as_posix().lower())
        return sorted(root.rglob(pattern), key=lambda path: path.as_posix().lower())

    def iterdir(self, path: Path) -> list[Path]:
        self._record("scan", path)
        return sorted(path.iterdir(), key=lambda item: item.name.lower()) if path.is_dir() else []

    def exists(self, path: Path) -> bool:
        self._record("metadata", path)
        return self._physical_path(path).exists()

    def is_file(self, path: Path) -> bool:
        self._record("metadata", path)
        return self._physical_path(path).is_file()

    def is_dir(self, path: Path) -> bool:
        self._record("metadata", path)
        return path.is_dir()

    def stat(self, path: Path):
        self._record("metadata", path)
        return self._physical_path(path).stat()

    def make_directory(self, path: Path, *, parents: bool = True, exist_ok: bool = True) -> None:
        self._record("mkdir", path)
        path.mkdir(parents=parents, exist_ok=exist_ok)

    def read_text(self, path: Path, *, encoding: str = "utf-8") -> str:
        self._record("read", path)
        physical = self._physical_path(path)
        content = physical.read_text(encoding=encoding)
        if path.suffix.lower() == ".json" and physical.suffix.lower() == ".metta":
            documents = metta_documents_to_json(content)
            value: Any = documents[0] if len(documents) == 1 else documents
            return json.dumps(value, indent=2, ensure_ascii=False) + "\n"
        return content

    def write_text(self, path: Path, content: str, *, encoding: str = "utf-8") -> None:
        self._invalidate(path)
        self._record("write", path)
        physical = self._physical_path(path, writing=True)
        physical.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() == ".json" and physical.suffix.lower() == ".metta":
            value = json.loads(content)
            if isinstance(value, dict) and physical.exists():
                self.write_json_resource(path, value)
                return
            documents = value if isinstance(value, list) else [value]
            content = "\n".join(json_document_to_metta(item).rstrip() for item in documents) + "\n"
        physical.write_text(content, encoding=encoding)

    def read_bytes(self, path: Path) -> bytes:
        self._record("read", path)
        return path.read_bytes()

    def read_json(self, path: Path) -> Any:
        documents = self.read_json_documents(path)
        return documents[0] if len(documents) == 1 else documents

    def read_json_documents(self, path: Path) -> list[Any]:
        physical = self._physical_path(path)
        metadata = physical.stat()
        cache_key = physical.resolve()
        with self._cache_lock:
            cached = self._json_cache.get(cache_key)
            if cached and cached[0] == metadata.st_mtime_ns and cached[1] == metadata.st_size:
                self._record("cache-hit", path)
                return deepcopy(cached[2])
        self._record("cache-miss", path)
        if physical.suffix.lower() == ".metta":
            self._record("read", path)
            values = metta_documents_to_json(physical.read_text(encoding="utf-8"))
            with self._cache_lock:
                self._json_cache[cache_key] = (metadata.st_mtime_ns, metadata.st_size, deepcopy(values))
            return values
        self._record("read", path)
        source = physical.read_text(encoding="utf-8")
        decoder = json.JSONDecoder()
        values: list[Any] = []
        index = 0
        while index < len(source):
            while index < len(source) and source[index].isspace():
                index += 1
            if index >= len(source):
                break
            value, consumed = decoder.raw_decode(source, index)
            index = consumed
            values.extend(value if isinstance(value, list) else [value])
        if not values:
            raise ValueError(f"resource file is empty: {path}")
        with self._cache_lock:
            self._json_cache[cache_key] = (metadata.st_mtime_ns, metadata.st_size, deepcopy(values))
        return values

    def write_json(self, path: Path, document: Any) -> None:
        self._invalidate(path)
        if path.suffix.lower() == ".json":
            physical = self._physical_path(path, writing=True)
            if isinstance(document, dict) and physical.exists():
                self.write_json_resource(path, document)
                return
            self._record("write", path)
            physical.parent.mkdir(parents=True, exist_ok=True)
            physical.write_text(json_document_to_metta(document), encoding="utf-8")
            return
        self.write_text(path, json.dumps(document, indent=2, ensure_ascii=False) + "\n")

    def write_json_resource(self, path: Path, document: dict[str, Any]) -> None:
        self._invalidate(path)
        physical = self._physical_path(path, writing=True)
        replacement = json_document_to_metta(document).rstrip("\n")
        if physical.exists():
            source = physical.read_text(encoding="utf-8")
            resource_id = document.get("id")
            for start, end, resource_source in split_metta_document_spans(source):
                existing = metta_documents_to_json(resource_source)[0]
                if resource_id and existing.get("id") == resource_id:
                    source = source[:start] + replacement + source[end:]
                    break
            else:
                separator = "" if not source else ("" if source.endswith("\n\n") else "\n" if source.endswith("\n") else "\n\n")
                source += separator + replacement + "\n"
        else:
            source = replacement + "\n"
        self._record("write", path)
        physical.parent.mkdir(parents=True, exist_ok=True)
        physical.write_text(source, encoding="utf-8")

    def delete(self, path: Path) -> None:
        self._invalidate(path)
        self._record("delete", path)
        self._physical_path(path).unlink(missing_ok=True)

    def replace(self, source: Path, target: Path) -> None:
        self._invalidate(target)
        self._record("replace", target)
        if target.suffix.lower() == ".json":
            document = json.loads(source.read_text(encoding="utf-8"))
            if isinstance(document, dict) and self._physical_path(target).exists():
                self.write_json_resource(target, document)
                source.unlink(missing_ok=True)
                return
            physical = self._physical_path(target, writing=True)
            physical.parent.mkdir(parents=True, exist_ok=True)
            physical.write_text(json_document_to_metta(document), encoding="utf-8")
            source.unlink(missing_ok=True)
            return
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
