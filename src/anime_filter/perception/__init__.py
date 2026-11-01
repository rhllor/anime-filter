"""Percezione: landmark mani/volto e segmentazione persona.

`types` non dipende da MediaPipe, così gesture e filtri sono testabili senza modelli.
"""

from anime_filter.perception.types import PerceptionResult, Point

__all__ = ["PerceptionResult", "Point"]
