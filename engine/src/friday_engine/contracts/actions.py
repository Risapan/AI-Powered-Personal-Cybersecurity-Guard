"""Action requests: the only way anything gets done on the user's behalf (FR-P1..P3)."""

import re
from datetime import UTC, datetime
from typing import Annotated, Self
from uuid import UUID, uuid4

from pydantic import AwareDatetime, Field, StringConstraints, model_validator

from .base import Contract
from .enums import ActionKind, ActionStatus


class InvalidTransitionError(ValueError):
    pass


ParamValue = Annotated[str, StringConstraints(min_length=1, max_length=256)]

# Which params each action takes. Anything else is rejected. OPEN_GUIDANCE takes an
# id from Friday's own table of vendor help pages, never a URL, so nothing outside
# that table (for example a link an LLM made up) can be opened.
_PARAMS_BY_ACTION: dict[ActionKind, dict[str, str]] = {
    ActionKind.MARK_BENIGN: {},
    ActionKind.DELETE_FINDING: {},
    ActionKind.OPEN_GUIDANCE: {"guide_id": r"^[a-z0-9_]{1,64}$"},
}

_ALLOWED_TRANSITIONS: dict[ActionStatus, frozenset[ActionStatus]] = {
    ActionStatus.PROPOSED: frozenset({ActionStatus.APPROVED, ActionStatus.DECLINED}),
    ActionStatus.APPROVED: frozenset({ActionStatus.DONE, ActionStatus.FAILED}),
    ActionStatus.DECLINED: frozenset(),
    ActionStatus.DONE: frozenset(),
    ActionStatus.FAILED: frozenset(),
}


class ActionRequest(Contract):
    id: UUID = Field(default_factory=uuid4)
    finding_id: UUID
    action: ActionKind
    params: dict[str, ParamValue] = Field(default_factory=dict, max_length=8)
    status: ActionStatus = ActionStatus.PROPOSED
    created_at: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))
    decided_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def _check(self) -> Self:
        expected = _PARAMS_BY_ACTION[self.action]
        if set(self.params) != set(expected):
            raise ValueError(
                f"'{self.action}' takes params {sorted(expected)}, got {sorted(self.params)}"
            )
        for name, pattern in expected.items():
            if not re.fullmatch(pattern, self.params[name]):
                raise ValueError(f"invalid value for param '{name}'")

        if (self.status is ActionStatus.PROPOSED) != (self.decided_at is None):
            raise ValueError("decided_at is set exactly when the request has left 'proposed'")
        return self

    def with_status(self, new: ActionStatus, at: datetime | None = None) -> "ActionRequest":
        """Return a copy moved to ``new``. Only the transitions in the table are allowed."""
        if new not in _ALLOWED_TRANSITIONS[self.status]:
            raise InvalidTransitionError(f"can't go from '{self.status}' to '{new}'")
        decided = self.decided_at or at or datetime.now(UTC)
        # Rebuild through validation instead of model_copy, which would skip the checks.
        data = self.model_dump()
        data.update(status=new, decided_at=decided)
        return ActionRequest.model_validate(data)
