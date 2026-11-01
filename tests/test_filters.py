from __future__ import annotations

import numpy as np

from anime_filter.filters import CartoonFilter, FilterChain, VanishFilter
from anime_filter.perception.types import PerceptionResult
from anime_filter.types import Frame


def test_vanish_replaces_person_with_background(frame: Frame) -> None:
    background = np.zeros_like(frame)
    vanish = VanishFilter(enabled=True, fade_frames=1, feather_px=1)
    vanish.capture_background(background)
    mask = np.ones(frame.shape[:2], np.float32)

    out = vanish.apply(frame, PerceptionResult(person_mask=mask))

    assert np.array_equal(out, background)


def test_vanish_fades_out_after_disable(frame: Frame) -> None:
    vanish = VanishFilter(enabled=True, fade_frames=2, feather_px=1)
    vanish.capture_background(np.zeros_like(frame))
    p = PerceptionResult(person_mask=np.ones(frame.shape[:2], np.float32))
    vanish.apply(frame, p)
    vanish.apply(frame, p)
    vanish.toggle()
    assert vanish.active  # ancora in dissolvenza
    vanish.apply(frame, p)
    vanish.apply(frame, p)
    assert not vanish.active


def test_vanish_without_background_is_noop(frame: Frame) -> None:
    vanish = VanishFilter(enabled=True)
    p = PerceptionResult(person_mask=np.ones(frame.shape[:2], np.float32))
    assert np.array_equal(vanish.apply(frame, p), frame)


def test_chain_requests_mask_only_when_needed() -> None:
    vanish, cartoon = VanishFilter(), CartoonFilter(enabled=True)
    chain = FilterChain([vanish, cartoon])
    assert not chain.needs_mask
    vanish.toggle()
    assert chain.needs_mask


def test_cartoon_preserves_shape(frame: Frame) -> None:
    out = CartoonFilter(enabled=True).apply(frame, PerceptionResult())
    assert out.shape == frame.shape
    assert out.dtype == np.uint8
