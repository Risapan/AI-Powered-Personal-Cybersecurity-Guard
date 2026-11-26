import re
from importlib.metadata import requires

import friday_engine

# Every runtime dependency needs a reason (see CONTRIBUTING.md). Adding one means
# adding it here too, so it shows up clearly in review.
ALLOWED_RUNTIME_DEPENDENCIES = {
    "pydantic",  # strict schema validation for every message crossing a trust boundary
}


def test_version_is_set() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+.*", friday_engine.__version__)


def test_runtime_dependencies_are_allowlisted() -> None:
    declared = {
        re.split(r"[<>=!~\[; ]", req, maxsplit=1)[0] for req in requires("friday-engine") or []
    }
    assert declared == ALLOWED_RUNTIME_DEPENDENCIES
