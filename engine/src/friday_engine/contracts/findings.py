"""Signals, intel results and findings: what the detection and risk engines produce."""

from datetime import UTC, datetime
from typing import Annotated, Self
from uuid import UUID, uuid4

from pydantic import AwareDatetime, Field, StringConstraints, model_validator

from .base import Contract
from .enums import (
    Confidence,
    IntelStatus,
    Severity,
    SubjectKind,
    UserFeedback,
    Verdict,
)

SignalId = Annotated[
    str,
    StringConstraints(max_length=100, pattern=r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$"),
]
"""Dotted rule id, e.g. ``url.ip_literal_host``."""

SemVer = Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
EvidenceKey = Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_]{0,63}$")]
EvidenceValue = Annotated[str, StringConstraints(max_length=2048)] | int | float | bool
ShortText = Annotated[str, StringConstraints(min_length=1, max_length=200)]
LongText = Annotated[str, StringConstraints(min_length=1, max_length=500)]


def _now() -> datetime:
    return datetime.now(UTC)


class Signal(Contract):
    """One thing a rule noticed, with the evidence that made it fire."""

    id: SignalId
    title: ShortText
    evidence: dict[EvidenceKey, EvidenceValue] = Field(max_length=32)
    weight: float = Field(gt=0.0, le=1.0)
    rule_version: SemVer


class Subject(Contract):
    """What was checked. Stored already redacted (no fragment, no query values)."""

    kind: SubjectKind
    value_redacted: Annotated[str, StringConstraints(min_length=1, max_length=4096)]
    host: Annotated[str, StringConstraints(min_length=1, max_length=253)] | None = None

    @model_validator(mode="after")
    def _no_fragment(self) -> Self:
        # Fragments are removed before a URL leaves the extension (T3). If one shows
        # up here, something upstream is broken, so refuse rather than store it.
        if self.kind is SubjectKind.URL and "#" in self.value_redacted:
            raise ValueError("URL subjects must not contain a fragment")
        return self


class IntelResult(Contract):
    """The outcome of one reputation lookup, including lookups that didn't happen."""

    provider: Annotated[str, StringConstraints(pattern=r"^[a-z0-9_]{1,40}$")]
    status: IntelStatus
    indicator_sent: Annotated[str, StringConstraints(min_length=1, max_length=512)] | None = None
    fetched_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def _consistent_with_status(self) -> Self:
        if self.status is IntelStatus.DISABLED:
            if self.indicator_sent is not None or self.fetched_at is not None:
                raise ValueError("a disabled lookup can't have sent anything")
        elif self.indicator_sent is None or self.fetched_at is None:
            raise ValueError(f"a '{self.status}' result must record what was sent and when")
        return self


class Finding(Contract):
    """The result of checking one subject. This is what users see and what gets stored."""

    id: UUID = Field(default_factory=uuid4)
    created_at: AwareDatetime = Field(default_factory=_now)
    subject: Subject
    verdict: Verdict
    severity: Severity
    confidence: Confidence
    signals: tuple[Signal, ...] = Field(default=(), max_length=50)
    intel: tuple[IntelResult, ...] = Field(default=(), max_length=5)
    limitations: tuple[LongText, ...] = Field(min_length=1, max_length=10)
    rule_set_version: SemVer
    user_feedback: UserFeedback = UserFeedback.NONE

    @model_validator(mode="after")
    def _verdict_matches_evidence(self) -> Self:
        ids = [s.id for s in self.signals]
        if len(ids) != len(set(ids)):
            raise ValueError("signal ids must be unique within a finding")

        intel_hit = any(r.status is IntelStatus.HIT for r in self.intel)

        if self.verdict is Verdict.SUSPICIOUS:
            if not self.signals and not intel_hit:
                raise ValueError("'suspicious' needs at least one signal or intel hit")
            if self.severity is Severity.NONE:
                raise ValueError("'suspicious' can't have severity 'none'")

        if self.verdict is Verdict.NOT_DETECTED:
            if self.severity is not Severity.NONE:
                raise ValueError("'not_detected' must have severity 'none'")
            if intel_hit:
                raise ValueError("'not_detected' contradicts an intel hit")

        return self

    def signal_ids(self) -> frozenset[str]:
        return frozenset(s.id for s in self.signals)
