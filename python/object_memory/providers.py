from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from .models import CandidateObject, ExecutionMode, NormalizedResult


@dataclass(frozen=True)
class ProviderCapabilities:
    mode: ExecutionMode
    candidate_parts: tuple[str, ...] = ()
    semantic_record_families: tuple[str, ...] = ()
    dynamic_candidate_parts: bool = False

    def supports_candidate_part(self, name: str) -> bool:
        return self.dynamic_candidate_parts or name in self.candidate_parts


class UnsupportedProviderCapability(KeyError):
    """Machine-readable failure for a capability the provider does not expose."""

    def __init__(
        self,
        *,
        mode: ExecutionMode,
        capability_kind: str,
        requested: str,
        available: tuple[str, ...],
    ) -> None:
        self.mode = mode
        self.capability_kind = capability_kind
        self.requested = requested
        self.available = available
        super().__init__(
            f"{mode.value} provider does not support {capability_kind} "
            f"{requested!r}; available: {', '.join(available) or 'none'}"
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "error": "unsupported_provider_capability",
            "mode": self.mode.value,
            "capabilityKind": self.capability_kind,
            "requested": self.requested,
            "available": list(self.available),
        }


class ArtifactProvider(ABC):
    """One stable contract with backend-specific implementations."""

    mode: ExecutionMode

    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        raise NotImplementedError

    @abstractmethod
    def get_candidate_part(self, candidate: CandidateObject, name: str) -> NormalizedResult:
        raise NotImplementedError


class PythonProvider(ArtifactProvider):
    mode = ExecutionMode.PYTHON

    def __init__(self, resolvers: Mapping[str, Callable[[CandidateObject], Any]]) -> None:
        self._resolvers = dict(resolvers)

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            mode=self.mode,
            candidate_parts=tuple(sorted(self._resolvers)),
        )

    def get_candidate_part(self, candidate: CandidateObject, name: str) -> NormalizedResult:
        try:
            resolver = self._resolvers[name]
        except KeyError as exc:
            raise UnsupportedProviderCapability(
                mode=self.mode,
                capability_kind="candidate_part",
                requested=name,
                available=self.capabilities().candidate_parts,
            ) from exc
        return NormalizedResult(value=resolver(candidate), mode=self.mode)


class GptArtifactProvider(ArtifactProvider):
    """Reads GPT-generated or cached artifacts; it does not emulate native analysis."""

    mode = ExecutionMode.GPT
    ARTIFACT_NAMES = {
        "properties": "objects.pl",
        "correspondence": "similarities.pl",
        "differences": "differences.pl",
        "rules": "rules.pl",
        "generative_form": "turtle_from_image.pl",
    }

    def __init__(self, node_path: str | Path) -> None:
        self.node_path = Path(node_path)

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            mode=self.mode,
            candidate_parts=tuple(sorted(self.ARTIFACT_NAMES)),
        )

    def get_candidate_part(self, candidate: CandidateObject, name: str) -> NormalizedResult:
        artifact_name = self.ARTIFACT_NAMES.get(name)
        if artifact_name is None:
            raise UnsupportedProviderCapability(
                mode=self.mode,
                capability_kind="candidate_part",
                requested=name,
                available=self.capabilities().candidate_parts,
            )
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

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            mode=self.mode,
            semantic_record_families=tuple(sorted(self.SEMANTIC_NAMESPACES)),
            dynamic_candidate_parts=True,
        )

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
            raise UnsupportedProviderCapability(
                mode=self.mode,
                capability_kind="semantic_record_family",
                requested=name,
                available=self.capabilities().semantic_record_families,
            ) from exc
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
