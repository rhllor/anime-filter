"""Tipi condivisi."""

from typing import TypeAlias

import numpy as np
import numpy.typing as npt

Frame: TypeAlias = npt.NDArray[np.uint8]
"""Immagine BGR (convenzione OpenCV), shape (H, W, 3)."""

Mask: TypeAlias = npt.NDArray[np.float32]
"""Maschera di confidenza in [0, 1], shape (H, W)."""
