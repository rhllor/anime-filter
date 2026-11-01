from __future__ import annotations

from dataclasses import dataclass, field

from anime_filter.types import Mask


@dataclass(frozen=True, slots=True)
class Point:
    """Landmark in coordinate normalizzate [0, 1] rispetto al frame."""

    x: float
    y: float

    def dist(self, other: Point) -> float:
        return float(((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5)


@dataclass(slots=True)
class PerceptionResult:
    hands: list[list[Point]] = field(default_factory=list)
    """Una lista di 21 landmark per ogni mano (schema MediaPipe Hands)."""
    face: list[Point] | None = None
    """478 landmark del volto (schema MediaPipe Face Mesh), se presente."""
    person_mask: Mask | None = None
    """Confidenza 'persona' per pixel, calcolata solo se richiesta da un filtro."""
