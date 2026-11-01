"""Entry point CLI: `anime-filter run` / `anime-filter download-models`."""

from __future__ import annotations

import argparse
import contextlib
import logging
from dataclasses import replace
from pathlib import Path

from anime_filter import __version__
from anime_filter.config import Settings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="anime-filter", description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="log di debug")
    parser.add_argument("--config", type=Path, help="file TOML di configurazione")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="avvia la pipeline (default)")
    run.add_argument("--camera", type=int, help="indice della webcam fisica")
    run.add_argument("--no-virtual-cam", action="store_true", help="solo anteprima locale")
    run.add_argument("--no-preview", action="store_true", help="nessuna finestra locale")
    run.add_argument("--backend", help="backend pyvirtualcam: obs | v4l2loopback | unitycapture")

    dl = sub.add_parser("download-models", help="scarica i modelli MediaPipe")
    dl.add_argument("--force", action="store_true")
    return parser


def _settings_from_args(args: argparse.Namespace) -> Settings:
    settings = Settings.from_toml(args.config) if args.config else Settings()
    if getattr(args, "camera", None) is not None:
        settings = replace(settings, camera=replace(settings.camera, index=args.camera))
    output = settings.output
    if getattr(args, "no_virtual_cam", False):
        output = replace(output, virtual_camera=False)
    if getattr(args, "no_preview", False):
        output = replace(output, preview=False)
    if getattr(args, "backend", None):
        output = replace(output, backend=args.backend)
    return replace(settings, output=output)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    settings = _settings_from_args(args)

    if args.command == "download-models":
        from anime_filter.perception.models import ensure_models

        paths = ensure_models(settings.models_dir, force=args.force)
        print(f"Modelli pronti in {paths.hand.parent}")
        return 0

    from anime_filter.app import App

    with contextlib.suppress(KeyboardInterrupt):
        App(settings).run()
    return 0
