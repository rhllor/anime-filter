"""Teletrasporto di Goku: indice e medio uniti e tesi, appoggiati sulla fronte."""

from __future__ import annotations

from anime_filter.commands import Command
from anime_filter.gestures.base import HeldGesture
from anime_filter.perception.types import PerceptionResult, Point

# Indici landmark MediaPipe Hands
WRIST = 0
INDEX_PIP, INDEX_TIP = 6, 8
MIDDLE_PIP, MIDDLE_TIP = 10, 12
RING_PIP, RING_TIP = 14, 16
PINKY_PIP, PINKY_TIP = 18, 20

# Indici landmark MediaPipe Face Mesh
FOREHEAD = 10
FACE_LEFT, FACE_RIGHT = 234, 454


def _extended(hand: list[Point], pip: int, tip: int) -> bool:
    """Un dito è teso se la punta è più lontana dal polso rispetto all'articolazione PIP."""
    return hand[tip].dist(hand[WRIST]) > hand[pip].dist(hand[WRIST]) * 1.1


class InstantTransmission(HeldGesture):
    command = Command.TOGGLE_VANISH

    def __init__(
        self,
        hold_frames: int = 5,
        cooldown_s: float = 1.5,
        forehead_radius: float = 0.6,
        fingers_together: float = 0.35,
    ) -> None:
        super().__init__(hold_frames, cooldown_s)
        # Soglie relative alla larghezza del volto -> indipendenti dalla distanza dalla camera.
        self.forehead_radius = forehead_radius
        self.fingers_together = fingers_together

    def matches(self, perception: PerceptionResult) -> bool:
        face = perception.face
        if face is None:
            return False
        face_width = face[FACE_LEFT].dist(face[FACE_RIGHT])
        if face_width <= 0:
            return False
        forehead = face[FOREHEAD]
        return any(self._hand_matches(h, forehead, face_width) for h in perception.hands)

    def _hand_matches(self, hand: list[Point], forehead: Point, face_width: float) -> bool:
        if not (_extended(hand, INDEX_PIP, INDEX_TIP) and _extended(hand, MIDDLE_PIP, MIDDLE_TIP)):
            return False
        if _extended(hand, RING_PIP, RING_TIP) or _extended(hand, PINKY_PIP, PINKY_TIP):
            return False
        index_tip, middle_tip = hand[INDEX_TIP], hand[MIDDLE_TIP]
        if index_tip.dist(middle_tip) > self.fingers_together * face_width:
            return False
        fingertips = Point((index_tip.x + middle_tip.x) / 2, (index_tip.y + middle_tip.y) / 2)
        return fingertips.dist(forehead) < self.forehead_radius * face_width
