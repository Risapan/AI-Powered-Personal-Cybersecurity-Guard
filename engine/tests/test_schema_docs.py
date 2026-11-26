"""Every JSON example in docs/SCHEMAS.md must be valid against the real contracts."""

import re
from pathlib import Path

import pytest
from pydantic import BaseModel

from friday_engine.contracts import ActionRequest, Explanation, Finding, IntelResult

DOC = Path(__file__).resolve().parents[2] / "docs" / "SCHEMAS.md"
MODELS: dict[str, type[BaseModel]] = {
    "Finding": Finding,
    "IntelResult": IntelResult,
    "Explanation": Explanation,
    "ActionRequest": ActionRequest,
}
EXAMPLE = re.compile(r"<!-- example: (\w+) -->\s*```json\n(.*?)```", re.DOTALL)


def _examples() -> list[tuple[str, str]]:
    return EXAMPLE.findall(DOC.read_text(encoding="utf-8"))


def test_doc_has_examples_for_every_contract() -> None:
    assert {name for name, _ in _examples()} == set(MODELS)


@pytest.mark.parametrize(("name", "body"), _examples())
def test_example_is_valid(name: str, body: str) -> None:
    MODELS[name].model_validate_json(body)
