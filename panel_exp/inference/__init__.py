"""
Auto-documentation for inference modules.
"""
from panel_exp.inference.conformal import conformal, cross_conformal_single
from panel_exp.inference.k_fold import (
    cross_fold,
    debias,
    kfold,
    panel_timeseries_kfold,
    panel_timeseries_kfold_cumulative,
)
from panel_exp.inference.placebo import placebo, placebo_with_ci_inversion

__all__ = [
    "conformal",
    "cross_conformal_single",
    "cross_fold",
    "debias",
    "kfold",
    "panel_timeseries_kfold",
    "panel_timeseries_kfold_cumulative",
    "placebo",
    "placebo_with_ci_inversion",
]
