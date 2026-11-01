"""Wrapper sulla MediaPipe Tasks API (HandLandmarker, FaceLandmarker, ImageSegmenter)."""

from __future__ import annotations

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from anime_filter.perception.models import ModelPaths
from anime_filter.perception.types import PerceptionResult, Point
from anime_filter.types import Frame

_VIDEO = vision.RunningMode.VIDEO


class MediaPipePerceiver:
    def __init__(self, models: ModelPaths, num_hands: int = 2) -> None:
        self._hands = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=str(models.hand)),
                running_mode=_VIDEO,
                num_hands=num_hands,
            )
        )
        self._face = vision.FaceLandmarker.create_from_options(
            vision.FaceLandmarkerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=str(models.face)),
                running_mode=_VIDEO,
                num_faces=1,
            )
        )
        self._segmenter = vision.ImageSegmenter.create_from_options(
            vision.ImageSegmenterOptions(
                base_options=mp_python.BaseOptions(model_asset_path=str(models.selfie)),
                running_mode=_VIDEO,
                output_confidence_masks=True,
                output_category_mask=False,
            )
        )

    def process(self, frame: Frame, timestamp_ms: int, need_mask: bool) -> PerceptionResult:
        """`timestamp_ms` deve essere strettamente crescente (vincolo della modalità VIDEO)."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        hands_res = self._hands.detect_for_video(image, timestamp_ms)
        face_res = self._face.detect_for_video(image, timestamp_ms)

        result = PerceptionResult(
            hands=[[Point(lm.x, lm.y) for lm in hand] for hand in hands_res.hand_landmarks],
            face=(
                [Point(lm.x, lm.y) for lm in face_res.face_landmarks[0]]
                if face_res.face_landmarks
                else None
            ),
        )
        if need_mask:
            seg = self._segmenter.segment_for_video(image, timestamp_ms)
            # selfie_segmenter produce un'unica maschera: confidenza "persona".
            mask = np.asarray(seg.confidence_masks[-1].numpy_view(), np.float32)
            result.person_mask = mask.reshape(frame.shape[:2])  # (H, W, 1) -> (H, W)
        return result

    def close(self) -> None:
        self._hands.close()
        self._face.close()
        self._segmenter.close()
