"""Infrastruttura comune per i riconoscitori di gesture."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from anime_filter.commands import Command
from anime_filter.perception.types import PerceptionResult


class GestureRecognizer(Protocol):
    def update(self, perception: PerceptionResult, timestamp_ms: int) -> Command | None: ...


class HeldGesture(ABC):
    """Gesture 'a posa statica': scatta dopo `hold_frames` frame consecutivi, poi cooldown.

    Le sottoclassi implementano solo `matches()` (geometria pura, facile da testare).
    """

    command: Command

    def __init__(self, hold_frames: int = 5, cooldown_s: float = 1.5) -> None:
        self.hold_frames = hold_frames
        self.cooldown_ms = int(cooldown_s * 1000)
        self._streak = 0
        self._last_fired_ms: int | None = None

    @abstractmethod
    def matches(self, perception: PerceptionResult) -> bool: ...

    def update(self, perception: PerceptionResult, timestamp_ms: int) -> Command | None:
        if (
            self._last_fired_ms is not None
            and timestamp_ms - self._last_fired_ms < self.cooldown_ms
        ):
            self._streak = 0
            return None
        self._streak = self._streak + 1 if self.matches(perception) else 0
        if self._streak >= self.hold_frames:
            self._streak = 0
            self._last_fired_ms = timestamp_ms
            return self.command
        return None
