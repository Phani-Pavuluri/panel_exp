"""Shared setup helpers for ImpactAnalyzer inference modes."""

from __future__ import annotations

from typing import Any

import numpy as np

from panel_exp.inference.context import InferenceRunContext


def prepare_y_and_y_hat(ctx: InferenceRunContext) -> np.ndarray:
    """Fit model, predict, normalize shapes; populate ``analyzer.results`` base keys."""
    a = ctx.analyzer
    a.fit_data(ctx.panel_data)
    a.model = a.fit_model()
    a.y_hat = a.model.predict(a.panel_data.control_series(a.panel_data.treated_units).values.T)

    y = a.panel_data.treated_series(a.panel_data.treated_units).values.T
    if y.shape[0] == a.panel_data.num_timepoints and y.shape[1] == 1:
        y = y.reshape(-1)

    if (
        len(a.y_hat.shape) == 2
        and a.y_hat.shape[0] == a.panel_data.num_timepoints
        and a.y_hat.shape[1] == 1
    ):
        a.y_hat = a.y_hat.reshape(-1)

    a.results = {
        "times": a.panel_data.times,
        "y": y,
        "y_hat": a.y_hat,
    }
    return y


def flatten_single_unit_results(a: Any) -> None:
    if len(a.panel_data.treated_units) == 1:
        a.results["y_upper"] = a.results["y_upper"].flatten()
        a.results["y_hat"] = a.results["y_hat"].flatten()
        a.results["y_lower"] = a.results["y_lower"].flatten()


def apply_bounds_to_results(a: Any, bounds: np.ndarray) -> None:
    """Map k-fold / placebo / BRB bounds tensor to y_lower, y_hat, y_upper."""
    a.results["y_upper"] = -bounds[:, :, 2].T + a.results["y"].reshape(bounds[:, :, 2].T.shape)
    a.results["y_hat"] = -bounds[:, :, 1].T + a.results["y"].reshape(bounds[:, :, 1].T.shape)
    a.results["y_lower"] = -bounds[:, :, 0].T + a.results["y"].reshape(bounds[:, :, 0].T.shape)
    flatten_single_unit_results(a)
