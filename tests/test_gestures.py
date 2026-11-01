from __future__ import annotations

from anime_filter.commands import Command
from anime_filter.gestures import InstantTransmission
from anime_filter.perception.types import PerceptionResult, Point
from tests.conftest import make_hand


def test_matches_two_fingers_on_forehead(face: list[Point]) -> None:
    g = InstantTransmission()
    assert g.matches(PerceptionResult(hands=[make_hand((0.5, 0.31))], face=face))


def test_rejects_hand_far_from_forehead(face: list[Point]) -> None:
    g = InstantTransmission()
    assert not g.matches(PerceptionResult(hands=[make_hand((0.15, 0.6))], face=face))


def test_rejects_open_hand(face: list[Point]) -> None:
    g = InstantTransmission()
    hand = make_hand((0.5, 0.31), two_fingers=False)
    assert not g.matches(PerceptionResult(hands=[hand], face=face))


def test_rejects_without_face() -> None:
    g = InstantTransmission()
    assert not g.matches(PerceptionResult(hands=[make_hand((0.5, 0.31))], face=None))


def test_fires_after_hold_then_cooldown(face: list[Point]) -> None:
    g = InstantTransmission(hold_frames=3, cooldown_s=1.0)
    p = PerceptionResult(hands=[make_hand((0.5, 0.31))], face=face)
    fired = [g.update(p, ts) for ts in range(0, 100, 10)]  # 10 frame in 100 ms
    assert fired.count(Command.TOGGLE_VANISH) == 1
    assert fired[2] is Command.TOGGLE_VANISH
    assert g.update(p, 2000) is None  # dopo il cooldown la streak riparte da zero
