"""Download dei modelli MediaPipe (Apache-2.0) nella cache utente."""

from __future__ import annotations

import logging
import urllib.request
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)

_BASE = "https://storage.googleapis.com/mediapipe-models"
MODEL_URLS: dict[str, str] = {
    "hand": f"{_BASE}/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task",
    "face": f"{_BASE}/face_landmarker/face_landmarker/float16/latest/face_landmarker.task",
    "selfie": f"{_BASE}/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite",
}


@dataclass(frozen=True)
class ModelPaths:
    hand: Path
    face: Path
    selfie: Path


def ensure_models(models_dir: Path, force: bool = False) -> ModelPaths:
    models_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for name, url in MODEL_URLS.items():
        target = models_dir / url.rsplit("/", 1)[-1]
        if force or not target.exists():
            log.info("Scarico %s -> %s", url, target)
            tmp = target.with_suffix(target.suffix + ".part")
            urllib.request.urlretrieve(url, tmp)
            tmp.replace(target)
        paths[name] = target
    return ModelPaths(**paths)
