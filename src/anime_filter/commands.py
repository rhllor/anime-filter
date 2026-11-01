"""Comandi astratti: tastiera e gesture producono gli stessi Command, l'app li esegue."""

from enum import Enum, auto


class Command(Enum):
    TOGGLE_VANISH = auto()
    TOGGLE_CARTOON = auto()
    CAPTURE_BACKGROUND = auto()
    QUIT = auto()
