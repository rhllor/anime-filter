"""Configurazione applicativa: default -> file TOML -> argomenti CLI."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field, fields, is_dataclass, replace
from pathlib import Path
from typing import Any, cast

from platformdirs import user_cache_dir


@dataclass(frozen=True)
class CameraSettings:
    index: int = 0
    width: int = 1280
    height: int = 720
    fps: int = 30


@dataclass(frozen=True)
class OutputSettings:
    virtual_camera: bool = True
    backend: str | None = None
    device: str | None = None
    preview: bool = True
    mirror_preview: bool = True


@dataclass(frozen=True)
class GestureSettings:
    enabled: bool = True
    hold_frames: int = 5
    cooldown_s: float = 1.5


@dataclass(frozen=True)
class Settings:
    camera: CameraSettings = field(default_factory=CameraSettings)
    output: OutputSettings = field(default_factory=OutputSettings)
    gestures: GestureSettings = field(default_factory=GestureSettings)
    models_dir: Path = field(
        default_factory=lambda: Path(user_cache_dir("anime-filter")) / "models"
    )

    @classmethod
    def from_toml(cls, path: Path) -> Settings:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
        return cast(Settings, _merge(cls(), data))


def _merge(obj: Any, data: dict[str, Any]) -> Any:
    """Applica ricorsivamente un dict su una dataclass frozen. Stringhe vuote -> None."""
    updates: dict[str, Any] = {}
    for f in fields(obj):
        if f.name not in data:
            continue
        current, value = getattr(obj, f.name), data[f.name]
        if is_dataclass(current) and isinstance(value, dict):
            updates[f.name] = _merge(current, value)
        elif isinstance(current, Path):
            updates[f.name] = Path(value).expanduser()
        else:
            updates[f.name] = None if value == "" else value
    return replace(obj, **updates)
