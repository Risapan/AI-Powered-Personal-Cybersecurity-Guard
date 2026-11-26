"""What the local LLM is allowed to return.

The explanation has no verdict, severity or action fields on purpose. The model
can describe a finding, but there is no field through which it could change one (T10).
"""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, Field, StringConstraints

from .base import Contract
from .findings import Finding, LongText, SignalId


class UngroundedExplanationError(ValueError):
    """The explanation cites evidence that isn't in the finding (T11)."""


class Fact(Contract):
    """A statement the model makes, tied to the signals that support it."""

    text: LongText
    signal_ids: tuple[SignalId, ...] = Field(min_length=1, max_length=10)


class Explanation(Contract):
    finding_id: UUID
    model: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    facts: tuple[Fact, ...] = Field(max_length=10)
    uncertainty: tuple[LongText, ...] = Field(max_length=10)
    recommendations: tuple[LongText, ...] = Field(max_length=10)
    generated_at: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))

    def assert_grounded_in(self, finding: Finding) -> None:
        """Raise if the explanation belongs to another finding or cites unknown signals."""
        if self.finding_id != finding.id:
            raise UngroundedExplanationError("explanation is for a different finding")
        known = finding.signal_ids()
        cited = {sid for fact in self.facts for sid in fact.signal_ids}
        unknown = sorted(cited - known)
        if unknown:
            raise UngroundedExplanationError(f"cites signals not in the finding: {unknown}")
