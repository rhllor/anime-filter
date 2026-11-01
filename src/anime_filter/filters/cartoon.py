"""Effetto 'anime/cartoon' classico: colori appiattiti + contorni marcati."""

from __future__ import annotations

import cv2
import numpy as np

from anime_filter.filters.base import Filter
from anime_filter.perception.types import PerceptionResult
from anime_filter.types import Frame


class CartoonFilter(Filter):
    name = "cartoon"

    def apply(self, frame: Frame, perception: PerceptionResult) -> Frame:
        # Bilateral su immagine ridotta: stesso look, molto più veloce.
        small = cv2.pyrDown(frame)
        for _ in range(2):
            small = cv2.bilateralFilter(small, d=9, sigmaColor=75, sigmaSpace=75)
        color = cv2.resize(cv2.pyrUp(small), (frame.shape[1], frame.shape[0]))

        gray = cv2.medianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 7)
        edges = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize=9, C=2
        )
        return np.asarray(cv2.bitwise_and(color, color, mask=edges), np.uint8)
