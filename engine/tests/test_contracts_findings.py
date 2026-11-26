import json
from collections.abc import Callable
from datetime import datetime

import pytest
from pydantic import ValidationError

from friday_engine.contracts import (
    Finding,
    IntelResult,
    IntelStatus,
    Severity,
    Signal,
    Subject,
    SubjectKind,
    Verdict,
)

MakeFinding = Callable[..., Finding]
MakeSignal = Callable[..., Signal]


# ---------- round trip ----------


def test_finding_json_round_trip(make_finding: MakeFinding) -> None:
    original = make_finding()
    restored = Finding.model_validate_json(original.model_dump_json())
    assert restored == original


def test_findings_are_immutable(make_finding: MakeFinding) -> None:
    finding = make_finding()
    with pytest.raises(ValidationError):
        finding.verdict = Verdict.NOT_DETECTED  # type: ignore[misc]


def test_default_id_and_timestamp_are_set(make_finding: MakeFinding) -> None:
    a, b = make_finding(), make_finding()
    assert a.id != b.id
    assert a.created_at.tzinfo is not None


# ---------- vocabulary ----------


@pytest.mark.parametrize("word", ["malicious", "safe", "clean", "SUSPICIOUS", ""])
def test_verdicts_outside_the_vocabulary_are_rejected(make_finding: MakeFinding, word: str) -> None:
    payload = json.loads(make_finding().model_dump_json())
    payload["verdict"] = word
    with pytest.raises(ValidationError):
        Finding.model_validate_json(json.dumps(payload))


def test_unknown_fields_are_rejected(make_finding: MakeFinding) -> None:
    payload = json.loads(make_finding().model_dump_json())
    payload["page_text"] = "<html>...</html>"
    with pytest.raises(ValidationError, match="page_text"):
        Finding.model_validate_json(json.dumps(payload))


def test_no_type_coercion(make_signal: MakeSignal) -> None:
    with pytest.raises(ValidationError):
        make_signal(weight="0.5")


# ---------- verdict invariants ----------


def test_suspicious_needs_evidence(make_finding: MakeFinding) -> None:
    with pytest.raises(ValidationError, match="at least one signal"):
        make_finding(signals=())


def test_suspicious_can_rest_on_an_intel_hit_alone(make_finding: MakeFinding) -> None:
    hit = IntelResult(
        provider="example_feed",
        status=IntelStatus.HIT,
        indicator_sent="192.0.2.10",
        fetched_at=datetime.fromisoformat("2026-01-01T00:00:00+00:00"),
    )
    assert make_finding(signals=(), intel=(hit,)).verdict is Verdict.SUSPICIOUS


def test_suspicious_needs_a_severity(make_finding: MakeFinding) -> None:
    with pytest.raises(ValidationError, match="severity 'none'"):
        make_finding(severity=Severity.NONE)


def test_not_detected_has_no_severity(make_finding: MakeFinding) -> None:
    with pytest.raises(ValidationError, match="must have severity 'none'"):
        make_finding(verdict=Verdict.NOT_DETECTED, signals=(), severity=Severity.LOW)


def test_not_detected_cant_contradict_an_intel_hit(make_finding: MakeFinding) -> None:
    hit = IntelResult(
        provider="example_feed",
        status=IntelStatus.HIT,
        indicator_sent="example.com",
        fetched_at=datetime.fromisoformat("2026-01-01T00:00:00+00:00"),
    )
    with pytest.raises(ValidationError, match="contradicts"):
        make_finding(verdict=Verdict.NOT_DETECTED, signals=(), severity=Severity.NONE, intel=(hit,))


def test_unknown_is_allowed_without_evidence(make_finding: MakeFinding) -> None:
    finding = make_finding(verdict=Verdict.UNKNOWN, signals=(), severity=Severity.NONE)
    assert finding.verdict is Verdict.UNKNOWN


def test_limitations_are_required(make_finding: MakeFinding) -> None:
    with pytest.raises(ValidationError):
        make_finding(limitations=())


def test_duplicate_signal_ids_are_rejected(
    make_finding: MakeFinding, make_signal: MakeSignal
) -> None:
    with pytest.raises(ValidationError, match="unique"):
        make_finding(signals=(make_signal(), make_signal()))


# ---------- signals ----------


@pytest.mark.parametrize("bad_id", ["ip_literal", "URL.Ip", "url..x", "url.x-y", "1url.x"])
def test_signal_ids_must_be_dotted_lowercase(make_signal: MakeSignal, bad_id: str) -> None:
    with pytest.raises(ValidationError):
        make_signal(id=bad_id)


@pytest.mark.parametrize("weight", [0.0, -0.1, 1.01])
def test_signal_weight_range(make_signal: MakeSignal, weight: float) -> None:
    with pytest.raises(ValidationError):
        make_signal(weight=weight)


def test_evidence_must_be_flat(make_signal: MakeSignal) -> None:
    with pytest.raises(ValidationError):
        make_signal(evidence={"nested": {"a": 1}})


def test_evidence_size_is_bounded(make_signal: MakeSignal) -> None:
    with pytest.raises(ValidationError):
        make_signal(evidence={f"k{i}": i for i in range(33)})
    with pytest.raises(ValidationError):
        make_signal(evidence={"host": "a" * 2049})


# ---------- subject ----------


def test_url_subject_with_fragment_is_refused() -> None:
    with pytest.raises(ValidationError, match="fragment"):
        Subject(kind=SubjectKind.URL, value_redacted="https://x.example/#token=abc")


# ---------- intel ----------


def test_disabled_lookup_sent_nothing() -> None:
    assert IntelResult(provider="example_feed", status=IntelStatus.DISABLED).indicator_sent is None
    with pytest.raises(ValidationError, match="disabled"):
        IntelResult(provider="example_feed", status=IntelStatus.DISABLED, indicator_sent="x.com")


@pytest.mark.parametrize("status", [IntelStatus.HIT, IntelStatus.MISS, IntelStatus.ERROR])
def test_real_lookups_record_what_was_sent(status: IntelStatus) -> None:
    with pytest.raises(ValidationError, match="must record"):
        IntelResult(provider="example_feed", status=status)


def test_timestamps_must_have_a_timezone(make_finding: MakeFinding) -> None:
    with pytest.raises(ValidationError):
        make_finding(created_at=datetime(2026, 1, 1))
