from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from omega_vision.core.models import InstanceParameters, RecognitionAccount
from omega_vision.core.recognition import InstanceMatcher


@dataclass(frozen=True)
class RecognitionFixture:
    """One authority-labeled candidate and its complete identity rival set."""

    fixture_id: str
    scope: str
    current: InstanceParameters
    stored: Mapping[str, InstanceParameters]
    accepted_identity_id: str | None


@dataclass(frozen=True)
class RecognitionBenchmarkResult:
    fixture_id: str
    scope: str
    accounts: tuple[RecognitionAccount, ...]


class RecognitionBenchmarkRunner:
    """Exercise the real matcher and retain outcomes for every rival proposal."""

    def __init__(self, matcher: InstanceMatcher | None = None) -> None:
        self.matcher = matcher or InstanceMatcher()

    def run(
        self, fixtures: tuple[RecognitionFixture, ...]
    ) -> tuple[RecognitionBenchmarkResult, ...]:
        results = []
        for fixture in fixtures:
            proposals = self.matcher.proposals(
                candidate_id=fixture.fixture_id,
                current=fixture.current,
                stored=fixture.stored,
            )
            accounts = tuple(
                RecognitionAccount.create(
                    candidate_id=f"{fixture.fixture_id}:{proposal.stored_identity_id}",
                    stored_identity_id=(
                        proposal.stored_identity_id
                        if proposal.stored_identity_id == fixture.accepted_identity_id
                        else None
                    ),
                    matched_properties=proposal.matched_properties,
                    changed_properties=proposal.changed_properties,
                    allowed_transformations=proposal.allowed_transformations,
                    rival_proposal_ids=tuple(
                        item.proposal_id
                        for item in proposals
                        if item.proposal_id != proposal.proposal_id
                    ),
                    decision_confidence=float(proposal.probability or 0.0),
                    decision_outcome=(
                        proposal.stored_identity_id == fixture.accepted_identity_id
                    ),
                    decision_source=f"benchmark_authority:{fixture.scope}",
                )
                for proposal in proposals
            )
            results.append(
                RecognitionBenchmarkResult(
                    fixture_id=fixture.fixture_id,
                    scope=fixture.scope,
                    accounts=accounts,
                )
            )
        return tuple(results)

    @staticmethod
    def accounts(
        results: tuple[RecognitionBenchmarkResult, ...], *, scope: str | None = None
    ) -> tuple[RecognitionAccount, ...]:
        return tuple(
            account
            for result in results
            if scope is None or result.scope == scope
            for account in result.accounts
        )
