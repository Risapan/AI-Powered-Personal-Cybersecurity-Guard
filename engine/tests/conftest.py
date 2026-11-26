from collections.abc import Callable
from typing import Any

import pytest

from friday_engine.contracts import (
    Confidence,
    Finding,
    Severity,
    Signal,
    Subject,
    SubjectKind,
    Verdict,
)


def _signal(**overrides: Any) -> Signal:
    data: dict[str, Any] = {
        "id": "url.ip_literal_host",
        "title": "The address is a raw IP instead of a domain name",
        "evidence": {"host": "192.0.2.10"},
        "weight": 0.4,
        "rule_version": "1.0.0",
    }
    data.update(overrides)
    return Signal(**data)


def _finding(**overrides: Any) -> Finding:
    data: dict[str, Any] = {
        "subject": Subject(
            kind=SubjectKind.URL,
            value_redacted="http://192.0.2.10/login?user",
            host="192.0.2.10",
        ),
        "verdict": Verdict.SUSPICIOUS,
        "severity": Severity.MEDIUM,
        "confidence": Confidence.LOW,
        "signals": (_signal(),),
        "limitations": ("Only the URL was checked, not the page content.",),
        "rule_set_version": "0.1.0",
    }
    data.update(overrides)
    return Finding(**data)


@pytest.fixture
def make_signal() -> Callable[..., Signal]:
    return _signal


@pytest.fixture
def make_finding() -> Callable[..., Finding]:
    return _finding
