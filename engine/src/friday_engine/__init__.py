"""Friday engine: local detection, risk scoring and storage."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("friday-engine")
except PackageNotFoundError:  # running from a source checkout without install
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
