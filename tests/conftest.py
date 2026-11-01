from __future__ import annotations

import numpy as np
import pytest

from anime_filter.gestures.instant_transmission import (
    FACE_LEFT,
    FACE_RIGHT,
    FOREHEAD,
    INDEX_PIP,
    INDEX_TIP,
    MIDDLE_PIP,
    MIDDLE_TIP,
    PINKY_PIP,
    PINKY_TIP,
    RING_PIP,
    RING_TIP,
    WRIST,
)
from anime_filter.perception.types import Point
from anime_filter.types import Frame


@pytest.fixture
def frame() -> Frame:
    rng = np.random.default_rng(0)
    return rng.integers(0, 255, size=(120, 160, 3), dtype=np.uint8)


@pytest.fixture
def face() -> list[Point]:
    """Volto sintetico: larghezza 0.2, fronte in (0.5, 0.3)."""
    pts = [Point(0.5, 0.45)] * 478
    pts[FOREHEAD] = Point(0.5, 0.3)
    pts[FACE_LEFT] = Point(0.4, 0.45)
    pts[FACE_RIGHT] = Point(0.6, 0.45)
    return pts


def make_hand(tip_xy: tuple[float, float], two_fingers: bool = True) -> list[Point]:
    """Mano sintetica con polso in basso e indice/medio puntati verso `tip_xy`."""
    wx, wy = tip_xy[0], tip_xy[1] + 0.25
    pts = [Point(wx, wy)] * 21
    pts[WRIST] = Point(wx, wy)
    for pip, tip, dx in ((INDEX_PIP, INDEX_TIP, -0.01), (MIDDLE_PIP, MIDDLE_TIP, 0.01)):
        pts[pip] = Point(wx + dx, wy - 0.12)
        pts[tip] = Point(tip_xy[0] + dx, tip_xy[1])
    for pip, tip in ((RING_PIP, RING_TIP), (PINKY_PIP, PINKY_TIP)):
        pts[pip] = Point(wx, wy - 0.10)
        # dito piegato: punta più vicina al polso del PIP (o tesa, se two_fingers=False)
        pts[tip] = Point(wx, wy - (0.05 if two_fingers else 0.22))
    return pts
