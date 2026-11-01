"""Finestra di anteprima locale (OpenCV HighGUI). Riceve anche gli eventi tastiera."""

from __future__ import annotations

from collections.abc import Iterable

import cv2

from anime_filter.types import Frame


class PreviewWindow:
    def __init__(self, title: str = "anime-filter", mirror: bool = True) -> None:
        self.title, self.mirror = title, mirror
        cv2.namedWindow(self.title, cv2.WINDOW_NORMAL)

    def show(self, frame: Frame, hud: Iterable[str] = ()) -> None:
        view = cv2.flip(frame, 1) if self.mirror else frame.copy()
        for i, line in enumerate(hud):
            cv2.putText(
                view, line, (12, 28 + 24 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )
        cv2.imshow(self.title, view)

    def poll_key(self) -> int | None:
        """Ritorna il codice del tasto premuto (non bloccante) oppure None."""
        key = cv2.waitKey(1)
        return None if key == -1 else key & 0xFF

    def close(self) -> None:
        cv2.destroyWindow(self.title)
