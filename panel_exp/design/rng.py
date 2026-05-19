"""Reproducible RNG helpers for design modules."""

from __future__ import annotations

from typing import Optional

import numpy as np


def make_generator(random_state: Optional[int] = None) -> np.random.Generator:
    """
    Return a numpy ``Generator`` for geo-supported design paths.

    Contract
    --------
    - ``random_state`` is an integer seed: repeated calls produce identical assignments.
    - ``random_state=None`` defaults to seed ``42`` (legacy reproducible default).
    - Use ``np.random.default_rng()`` directly only when truly unseeded draws are required.
    """
    if random_state is None:
        random_state = 42
    return np.random.default_rng(random_state)
