"""Acquisizione webcam cross-platform via OpenCV."""

from __future__ import annotations

import logging
import sys
from types import TracebackType

import cv2
import numpy as np

from anime_filter.types import Frame

log = logging.getLogger(__name__)


def _default_api() -> int:
    """Backend nativo per OS: più affidabile e veloce del default di OpenCV."""
    if sys.platform == "darwin":
        return int(cv2.CAP_AVFOUNDATION)
    if sys.platform == "win32":
        return int(cv2.CAP_MSMF)  # alternativa: cv2.CAP_DSHOW se MSMF è lento ad aprirsi
    return int(cv2.CAP_V4L2)


class Webcam:
    def __init__(self, index: int = 0, width: int = 1280, height: int = 720, fps: int = 30) -> None:
        self.index, self.width, self.height, self.fps = index, width, height, fps
        self._cap: cv2.VideoCapture | None = None

    def open(self) -> None:
        cap = cv2.VideoCapture(self.index, _default_api())
        if not cap.isOpened():
            raise RuntimeError(f"Impossibile aprire la webcam #{self.index}")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        # La camera può non supportare la risoluzione richiesta: usiamo quella reale.
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        log.info("Webcam #%d aperta a %dx%d", self.index, self.width, self.height)
        self._cap = cap

    def read(self) -> Frame | None:
        if self._cap is None:
            raise RuntimeError("Webcam non aperta")
        ok, frame = self._cap.read()
        return np.asarray(frame, np.uint8) if ok else None

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def __enter__(self) -> Webcam:
        self.open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
