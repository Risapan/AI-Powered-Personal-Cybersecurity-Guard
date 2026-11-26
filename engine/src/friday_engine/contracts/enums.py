"""Fixed vocabularies used across Friday.

These are deliberately small. Adding a value is a design change: it has to be
reflected in the UI wording, the risk rules and the threat model.
"""

from enum import StrEnum


class Verdict(StrEnum):
    """What Friday concluded about a subject.

    There is intentionally no "safe" and no "malicious". Rule-based URL checks
    can't prove either, so Friday never claims them (FR-R2).
    """

    NOT_DETECTED = "not_detected"  # checks ran, nothing found. Not the same as "safe"
    UNKNOWN = "unknown"  # couldn't decide: bad input, lookup failed, etc.
    SUSPICIOUS = "suspicious"  # at least one signal, worth the user's attention


class Severity(StrEnum):
    """How bad it would be if the finding is right."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Confidence(StrEnum):
    """How sure Friday is that the finding is right. Reported separately from severity."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SubjectKind(StrEnum):
    URL = "url"


class IntelStatus(StrEnum):
    HIT = "hit"  # the provider knows this indicator as bad
    MISS = "miss"  # the provider has no record. Not proof of safety
    ERROR = "error"  # timeout, rate limit, bad response. Treated as unknown
    DISABLED = "disabled"  # lookups are off (the default)


class UserFeedback(StrEnum):
    NONE = "none"
    BENIGN = "benign"  # "this is fine, stop warning me about it"
    INCORRECT = "incorrect"  # "the finding is wrong" (feeds rule tuning)


class ActionKind(StrEnum):
    """The complete allowlist of actions Friday can perform (FR-P2).

    None of these touch files, processes, network settings or the OS. Anything
    more invasive needs a threat-model update first.
    """

    MARK_BENIGN = "mark_benign"
    DELETE_FINDING = "delete_finding"
    OPEN_GUIDANCE = "open_guidance"  # open an official vendor help page in the browser


class ActionStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    DECLINED = "declined"
    DONE = "done"
    FAILED = "failed"
