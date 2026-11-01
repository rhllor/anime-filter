from __future__ import annotations

from pathlib import Path

from anime_filter.commands import Command
from anime_filter.config import Settings
from anime_filter.controls import KeyboardController


def test_settings_from_toml(tmp_path: Path) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text('[camera]\nindex = 2\n[output]\nbackend = ""\npreview = false\n')
    s = Settings.from_toml(cfg)
    assert s.camera.index == 2
    assert s.camera.width == 1280  # default preservato
    assert s.output.backend is None
    assert s.output.preview is False


def test_example_config_is_valid() -> None:
    example = Path(__file__).parents[1] / "config.example.toml"
    assert Settings.from_toml(example).camera.fps == 30


def test_keyboard_mapping() -> None:
    kb = KeyboardController()
    assert kb.handle(ord("v")) is Command.TOGGLE_VANISH
    assert kb.handle(27) is Command.QUIT
    assert kb.handle(None) is None
    assert kb.handle(ord("z")) is None
