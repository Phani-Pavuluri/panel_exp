"""Synthetic fixtures for power / MDE tests (no external CSV required)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from panel_exp.panel_data import PanelDataset, TimePeriod


def make_synthetic_power_panel(
    *,
    seed: int = 0,
    n_time: int = 24,
    treat_start: int = 18,
    n_controls: int = 4,
) -> PanelDataset:
    """Small treated + controls wide panel for fast power tests."""
    rng = np.random.default_rng(seed)
    treated = np.cumsum(rng.standard_normal(n_time)) * 2 + 100
    rows = [treated]
    geos = ["treated"]
    for i in range(n_controls):
        rows.append(np.cumsum(rng.standard_normal(n_time)) * 2 + 50 + 10 * i)
        geos.append(f"ctrl_{i}")
    wide = pd.DataFrame(np.vstack(rows), index=geos, columns=range(n_time))
    return PanelDataset(
        wide,
        treated_units=["treated"],
        treated_periods=[TimePeriod(treat_start, None)],
    )
