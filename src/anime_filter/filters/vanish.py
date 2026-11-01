"""Effetto 'sparizione': sostituisce i pixel della persona con uno sfondo pulito memorizzato.

Flusso: esci dall'inquadratura, premi `b` per catturare lo sfondo, rientra e
fai il gesto del teletrasporto (o premi `v`). La transizione è una dissolvenza.
"""

from __future__ import annotations

import cv2
import numpy as np

from anime_filter.filters.base import Filter
from anime_filter.perception.types import PerceptionResult
from anime_filter.types import Frame


class VanishFilter(Filter):
    name = "vanish"
    needs_mask = True

    def __init__(self, enabled: bool = False, fade_frames: int = 8, feather_px: int = 15) -> None:
        super().__init__(enabled)
        self.fade_step = 1.0 / max(fade_frames, 1)
        self.feather_px = feather_px | 1  # kernel dispari per GaussianBlur
        self.background: Frame | None = None
        self._strength = 0.0  # 0 = visibile, 1 = sparito

    def capture_background(self, frame: Frame) -> None:
        self.background = frame.copy()

    @property
    def active(self) -> bool:
        return self.enabled or self._strength > 0.0

    def apply(self, frame: Frame, perception: PerceptionResult) -> Frame:
        target = 1.0 if self.enabled else 0.0
        if self._strength < target:
            self._strength = min(target, self._strength + self.fade_step)
        else:
            self._strength = max(target, self._strength - self.fade_step)

        mask = perception.person_mask
        background = self.background
        if background is None or mask is None or self._strength == 0.0:
            return frame
        if background.shape != frame.shape:
            background = np.asarray(cv2.resize(background, frame.shape[1::-1]), np.uint8)
            self.background = background

        soft = cv2.GaussianBlur(mask, (self.feather_px, self.feather_px), 0)
        alpha = (soft * self._strength)[..., None]
        out = frame.astype(np.float32) * (1.0 - alpha) + background.astype(np.float32) * alpha
        return out.astype(np.uint8)
