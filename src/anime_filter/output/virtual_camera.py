"""Uscita su webcam virtuale tramite pyvirtualcam.

Backend per OS (vedi README per l'installazione):
  - Windows: OBS Virtual Camera oppure Unity Capture
  - macOS:   OBS Virtual Camera (system extension, OBS >= 30)
  - Linux:   v4l2loopback
"""

from __future__ import annotations

import logging
from types import TracebackType

import cv2
import numpy as np
import pyvirtualcam

from anime_filter.types import Frame

log = logging.getLogger(__name__)


class VirtualCamera:
    def __init__(
        self,
        width: int,
        height: int,
        fps: int,
        backend: str | None = None,
        device: str | None = None,
    ) -> None:
        self.width, self.height, self.fps = width, height, fps
        self.backend, self.device = backend, device
        self._cam: pyvirtualcam.Camera | None = None

    def open(self) -> None:
        self._cam = pyvirtualcam.Camera(
            width=self.width,
            height=self.height,
            fps=self.fps,
            fmt=pyvirtualcam.PixelFormat.BGR,
            backend=self.backend,
            device=self.device,
        )
        log.info("Webcam virtuale attiva: %s (%s)", self._cam.device, self._cam.backend)

    def send(self, frame: Frame) -> None:
        if self._cam is None:
            raise RuntimeError("Webcam virtuale non aperta")
        h, w = frame.shape[:2]
        if (w, h) != (self.width, self.height):
            frame = np.asarray(cv2.resize(frame, (self.width, self.height)), np.uint8)
        self._cam.send(frame)

    def close(self) -> None:
        if self._cam is not None:
            self._cam.close()
            self._cam = None

    def __enter__(self) -> VirtualCamera:
        self.open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
