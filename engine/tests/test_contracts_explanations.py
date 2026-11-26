from collections.abc import Callable
from uuid import uuid4

import pytest
from pydantic import ValidationError

from friday_engine.contracts import (
    Explanation,
    Fact,
    Finding,
    UngroundedExplanationError,
)

MakeFinding = Callable[..., Finding]


def _explanation(finding: Finding, *signal_ids: str) -> Explanation:
    return Explanation(
        finding_id=finding.id,
        model="qwen3:8b",
        facts=(Fact(text="The link points to a raw IP address.", signal_ids=signal_ids),),
        uncertainty=("Only the URL was checked.",),
        recommendations=("Don't enter a password on this page.",),
    )


def test_grounded_explanation_passes(make_finding: MakeFinding) -> None:
    finding = make_finding()
    _explanation(finding, "url.ip_literal_host").assert_grounded_in(finding)


def test_made_up_signal_is_caught(make_finding: MakeFinding) -> None:
    finding = make_finding()
    explanation = _explanation(finding, "url.ip_literal_host", "url.known_phishing_kit")
    with pytest.raises(UngroundedExplanationError, match="known_phishing_kit"):
        explanation.assert_grounded_in(finding)


def test_explanation_for_another_finding_is_caught(make_finding: MakeFinding) -> None:
    explanation = _explanation(make_finding(), "url.ip_literal_host")
    with pytest.raises(UngroundedExplanationError, match="different finding"):
        explanation.assert_grounded_in(make_finding())


def test_every_fact_must_cite_evidence() -> None:
    with pytest.raises(ValidationError):
        Fact(text="This site is definitely a scam.", signal_ids=())


@pytest.mark.parametrize("field", ["verdict", "severity", "action", "command"])
def test_model_output_cant_carry_decisions(field: str) -> None:
    # Prompt injection defence (T10/T12): even if the model returns these fields,
    # the explanation contract has nowhere to put them.
    payload = {
        "finding_id": str(uuid4()),
        "model": "qwen3:8b",
        "facts": [],
        "uncertainty": [],
        "recommendations": [],
        field: "not_detected",
    }
    with pytest.raises(ValidationError, match=field):
        Explanation.model_validate(payload, strict=False)
