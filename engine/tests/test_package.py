import re

import friday_engine


def test_version_is_set() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+.*", friday_engine.__version__)


def test_package_has_no_runtime_dependencies_yet() -> None:
    # The engine should stay light. New dependencies need a reason (see CONTRIBUTING.md).
    from importlib.metadata import requires

    assert not requires("friday-engine")
