"""anime-filter: filtri webcam guidati da gesture e tastiera, esposti come webcam virtuale."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("anime-filter")
except PackageNotFoundError:  # pragma: no cover - esecuzione da sorgente non installato
    __version__ = "0.0.0"

__all__ = ["__version__"]
