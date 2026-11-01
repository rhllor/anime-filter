"""Mappatura tasti -> Command. I tasti arrivano dalla finestra di preview (cv2.waitKey)."""

from __future__ import annotations

from collections.abc import Mapping

from anime_filter.commands import Command

DEFAULT_KEYMAP: Mapping[str, Command] = {
    "v": Command.TOGGLE_VANISH,
    "c": Command.TOGGLE_CARTOON,
    "b": Command.CAPTURE_BACKGROUND,
    "q": Command.QUIT,
    "\x1b": Command.QUIT,  # ESC
}


class KeyboardController:
    def __init__(self, keymap: Mapping[str, Command] = DEFAULT_KEYMAP) -> None:
        self._keymap = {ord(k): cmd for k, cmd in keymap.items()}

    def handle(self, key: int | None) -> Command | None:
        return None if key is None else self._keymap.get(key)

    def help_lines(self) -> list[str]:
        return [
            f"[{'ESC' if code == 27 else chr(code)}] {cmd.name.lower()}"
            for code, cmd in self._keymap.items()
        ]
