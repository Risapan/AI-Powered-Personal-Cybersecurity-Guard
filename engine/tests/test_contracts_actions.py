from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from friday_engine.contracts import (
    ActionKind,
    ActionRequest,
    ActionStatus,
    InvalidTransitionError,
)


def _request(**overrides: object) -> ActionRequest:
    data: dict[str, object] = {"finding_id": uuid4(), "action": ActionKind.MARK_BENIGN}
    data.update(overrides)
    return ActionRequest.model_validate(data)


def test_new_requests_start_as_proposed() -> None:
    request = _request()
    assert request.status is ActionStatus.PROPOSED
    assert request.decided_at is None


@pytest.mark.parametrize("action", ["delete_file", "run_command", "block_ip", "quarantine"])
def test_actions_outside_the_allowlist_are_rejected(action: str) -> None:
    with pytest.raises(ValidationError):
        ActionRequest.model_validate_json(f'{{"finding_id": "{uuid4()}", "action": "{action}"}}')


def test_params_must_match_the_action() -> None:
    with pytest.raises(ValidationError, match="takes params"):
        _request(params={"path": "/etc/passwd"})


def test_guidance_takes_an_id_not_a_url() -> None:
    ok = _request(action=ActionKind.OPEN_GUIDANCE, params={"guide_id": "macos_firewall"})
    assert ok.params["guide_id"] == "macos_firewall"
    with pytest.raises(ValidationError, match="invalid value"):
        _request(action=ActionKind.OPEN_GUIDANCE, params={"guide_id": "https://evil.example"})


def test_happy_path_transitions() -> None:
    at = datetime(2026, 1, 1, tzinfo=UTC)
    done = _request().with_status(ActionStatus.APPROVED, at).with_status(ActionStatus.DONE)
    assert done.status is ActionStatus.DONE
    assert done.decided_at == at  # the decision time is the approval, not the completion


@pytest.mark.parametrize(
    ("path", "illegal"),
    [
        ((), ActionStatus.DONE),  # can't run without approval
        ((), ActionStatus.FAILED),
        ((ActionStatus.DECLINED,), ActionStatus.APPROVED),  # a "no" is final
        ((ActionStatus.APPROVED, ActionStatus.DONE), ActionStatus.APPROVED),
    ],
)
def test_illegal_transitions(path: tuple[ActionStatus, ...], illegal: ActionStatus) -> None:
    request = _request()
    for status in path:
        request = request.with_status(status)
    with pytest.raises(InvalidTransitionError):
        request.with_status(illegal)


def test_decided_at_must_match_status() -> None:
    with pytest.raises(ValidationError, match="decided_at"):
        _request(status=ActionStatus.APPROVED)
    with pytest.raises(ValidationError, match="decided_at"):
        _request(decided_at=datetime(2026, 1, 1, tzinfo=UTC))
