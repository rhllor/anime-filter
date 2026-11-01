"""Loop principale: capture -> perception -> comandi -> filtri -> output."""

from __future__ import annotations

import logging
import time
from contextlib import ExitStack

from anime_filter.capture import Webcam
from anime_filter.commands import Command
from anime_filter.config import Settings
from anime_filter.controls import KeyboardController
from anime_filter.filters import CartoonFilter, FilterChain, VanishFilter
from anime_filter.gestures import GestureRecognizer, InstantTransmission
from anime_filter.output import PreviewWindow, VirtualCamera
from anime_filter.perception.models import ensure_models
from anime_filter.types import Frame

log = logging.getLogger(__name__)


class App:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.vanish = VanishFilter()
        self.cartoon = CartoonFilter()
        # Ordine rilevante: prima si rimuove la persona, poi si stilizza l'intera scena.
        self.filters = FilterChain([self.vanish, self.cartoon])
        self.keyboard = KeyboardController()
        g = settings.gestures
        self.gestures: list[GestureRecognizer] = (
            [InstantTransmission(g.hold_frames, g.cooldown_s)] if g.enabled else []
        )
        self._running = False

    def dispatch(self, command: Command, frame: Frame) -> None:
        log.info("Comando: %s", command.name)
        match command:
            case Command.TOGGLE_VANISH:
                if self.vanish.background is None:
                    log.warning("Nessuno sfondo catturato: esci dall'inquadratura e premi 'b'")
                self.vanish.toggle()
            case Command.TOGGLE_CARTOON:
                self.cartoon.toggle()
            case Command.CAPTURE_BACKGROUND:
                self.vanish.capture_background(frame)
            case Command.QUIT:
                self._running = False

    def run(self) -> None:
        # Import locale: MediaPipe è pesante, così CLI e test restano veloci.
        from anime_filter.perception.mediapipe_perceiver import MediaPipePerceiver

        s = self.settings
        perceiver = MediaPipePerceiver(ensure_models(s.models_dir))
        with ExitStack() as stack:
            stack.callback(perceiver.close)
            cam = stack.enter_context(
                Webcam(s.camera.index, s.camera.width, s.camera.height, s.camera.fps)
            )
            vcam = (
                stack.enter_context(
                    VirtualCamera(cam.width, cam.height, cam.fps, s.output.backend, s.output.device)
                )
                if s.output.virtual_camera
                else None
            )
            preview = PreviewWindow(mirror=s.output.mirror_preview) if s.output.preview else None
            if preview is not None:
                stack.callback(preview.close)

            self._running = True
            last_ts = 0
            while self._running:
                frame = cam.read()
                if frame is None:
                    log.warning("Frame non disponibile dalla webcam")
                    continue
                ts = max(int(time.monotonic() * 1000), last_ts + 1)
                last_ts = ts

                perception = perceiver.process(frame, ts, need_mask=self.filters.needs_mask)

                commands = [g.update(perception, ts) for g in self.gestures]
                if preview is not None:
                    commands.append(self.keyboard.handle(preview.poll_key()))
                for cmd in filter(None, commands):
                    self.dispatch(cmd, frame)
                if self.filters.needs_mask and perception.person_mask is None:
                    # Un comando ha appena attivato un filtro che richiede la maschera.
                    perception = perceiver.process(frame, ts + 1, need_mask=True)
                    last_ts = ts + 1

                out = self.filters.apply(frame, perception)

                if vcam is not None:
                    vcam.send(out)
                if preview is not None:
                    hud = [f"{f.name}: {'ON' if f.enabled else 'off'}" for f in self.filters]
                    preview.show(out, hud)
