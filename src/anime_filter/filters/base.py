"""Contratto dei filtri e catena di applicazione."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence

from anime_filter.perception.types import PerceptionResult
from anime_filter.types import Frame


class Filter(ABC):
    name: str = "filter"
    needs_mask: bool = False
    """True se il filtro richiede la segmentazione persona (costosa: calcolata solo se serve)."""

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def toggle(self) -> None:
        self.enabled = not self.enabled

    @property
    def active(self) -> bool:
        """Un filtro può restare 'attivo' anche da disabilitato (es. animazione di uscita)."""
        return self.enabled

    @abstractmethod
    def apply(self, frame: Frame, perception: PerceptionResult) -> Frame: ...


class FilterChain:
    def __init__(self, filters: Sequence[Filter]) -> None:
        self._filters = list(filters)

    def __iter__(self) -> Iterator[Filter]:
        return iter(self._filters)

    @property
    def needs_mask(self) -> bool:
        return any(f.active and f.needs_mask for f in self._filters)

    def apply(self, frame: Frame, perception: PerceptionResult) -> Frame:
        for f in self._filters:
            if f.active:
                frame = f.apply(frame, perception)
        return frame
