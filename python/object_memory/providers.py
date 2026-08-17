from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Mapping

from .models import CandidateObject, ExecutionMode, NormalizedResult


class ArtifactProvider(ABC):
    """One stable contract with backend-specific implementations."""

    mode: ExecutionMode

    @abstractmethod
    def get_candidate_part(self, candidate: CandidateObject, name: str) -> NormalizedResult:
        raise NotImplementedError


class PythonProvider(ArtifactProvider):
    mode = ExecutionMode.PYTHON

    def __init__(self, resolvers: Mapping[str, Callable[[CandidateObject], Any]]) -> None:
        self._resolvers = dict(resolvers)

    def get_candidate_part(self, candidate: CandidateObject, name: str) -> NormalizedResult:
        try:
            resolver = self._resolvers[name]
        except KeyError as exc:
            raise KeyError(f"No PYTHON resolver registered for candidate part {name!r}") from exc
        return NormalizedResult(value=resolver(candidate), mode=self.mode)


class GptArtifactProvider(ArtifactProvider):
    """Reads GPT-generated or cached artifacts; it does not emulate native analysis."""

    mode = ExecutionMode.GPT

    def __init__(self, node_path: str | Path) -> None:
        self.node_path = Path(node_path)

    def get_candidate_part(self, candidate: CandidateObject, name: str) -> NormalizedResult:
        artifact_name = {
            "properties": "objects.pl",
            "correspondence": "similarities.pl",
            "differences": "differences.pl",
            "rules": "rules.pl",
            "generative_form": "turtle_from_image.pl",
        }.get(name)
        if artifact_name is None:
            raise KeyError(f"No GPT artifact mapping for candidate part {name!r}")
        path = self.node_path / artifact_name
        if not path.exists():
            raise FileNotFoundError(path)
        text = path.read_text(encoding="utf-8")
        return NormalizedResult(
            value=text,
            mode=self.mode,
            source_refs=(str(path),),
            metadata={"artifact": artifact_name, "candidate_id": candidate.candidate_id},
        )


class PrologProvider(ArtifactProvider):
    """Delegates symbolic queries to SWI-Prolog through an injected query function."""

    mode = ExecutionMode.PROLOG
    SEMANTIC_NAMESPACES = {
        "registry": "atoms",
        "objects": "encounters",
        "differences": "object_changes",
        "similarities": "match_proposals",
        "rules": "transition_rules",
        "transcripts": "predictions",
        "evidence": "evidence",
    }

    def __init__(self, query: Callable[[str, Mapping[str, Any]], Any]) -> None:
        self._query = query

    @staticmethod
    def _predicate_name(name: str) -> str:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ValueError(f"Unsafe Prolog predicate name: {name!r}")
        return name

    def get_candidate_part(self, candidate: CandidateObject, name: str) -> NormalizedResult:
        predicate = self._predicate_name(f"candidate_{name}")
        payload = {
            "candidate_id": candidate.candidate_id,
            "observation_id": candidate.observation_id,
            "domain": candidate.domain,
            "region_ref": candidate.region_ref,
        }
        value = self._query(predicate, payload)
        return NormalizedResult(
            value=value,
            mode=self.mode,
            source_refs=(f"prolog:{predicate}",),
            metadata={"query": predicate, "payload": json.loads(json.dumps(payload))},
        )

    def get_semantic_records(
        self,
        name: str,
        filters: Mapping[str, Any] | None = None,
    ) -> NormalizedResult:
        """Query one normalized semantic namespace through the Prolog adapter."""

        try:
            namespace = self.SEMANTIC_NAMESPACES[name]
        except KeyError as exc:
            raise KeyError(f"Unknown semantic Prolog record family {name!r}") from exc
        payload = {
            "namespace": namespace,
            "filters": json.loads(json.dumps(dict(filters or {}))),
        }
        value = self._query("semantic_records", payload)
        return NormalizedResult(
            value=value,
            mode=self.mode,
            source_refs=(f"prolog:semantic_record/3:{namespace}",),
            metadata={"query": "semantic_records", "payload": payload},
        )
