"""Time-period slicing for design assignment (INV-D1-001)."""

from __future__ import annotations

import pandas as pd

from panel_exp.panel_data import TimePeriod


def slice_wide_to_time_period(
    wide: pd.DataFrame,
    period: TimePeriod,
) -> pd.DataFrame:
    """
    Return a copy of ``wide`` restricted to ``period`` column labels.

    Uses the same ``iloc`` semantics as ``Design.assign`` (end label is an
  exclusive stop index in column position space).
    """
    start_idx = (
        wide.columns.get_loc(period.start) if period.start is not None else 0
    )
    end_idx = wide.columns.get_loc(period.end) if period.end is not None else None
    return wide.iloc[:, start_idx:end_idx].copy()
