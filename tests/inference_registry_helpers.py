"""Shared helpers for inference registry equivalence tests."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from panel_exp.panel_data import PanelDataset, TimePeriod

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "inference_golden"

# Legacy ``self.results`` key contract per inference mode (post-run, success path).
LEGACY_RESULTS_KEYS: dict[str | None, frozenset[str]] = {
    None: frozenset({"times", "y", "y_hat"}),
    "UnitJackKnife": frozenset({"times", "y", "y_hat", "y_lower", "y_upper"}),
    "JKP": frozenset({"times", "y", "y_hat", "y_lower", "y_upper"}),
    "Bayesian": frozenset({"times", "y", "y_hat", "y_lower", "y_upper"}),
    "BlockResidualBootstrap": frozenset(
        {
            "times",
            "y",
            "y_hat",
            "y_lower",
            "y_upper",
            "block_residual_bootstrap_stats",
            "effect_cumulative_brb",
            "effect_ci_lower_cumulative_brb",
            "effect_ci_upper_cumulative_brb",
        }
    ),
    "Conformal": frozenset({"times", "y", "y_hat", "y_lower", "y_upper"}),
    "Kfold": frozenset({"times", "y", "y_hat", "y_lower", "y_upper"}),
    "Placebo": frozenset(
        {
            "times",
            "y",
            "y_hat",
            "y_lower",
            "y_upper",
            "placebo_stats",
            "intervals_available",
            "interval_type",
        }
    ),
    "Placebo_unsupported": frozenset(
        {
            "times",
            "y",
            "y_hat",
            "placebo_unsupported",
            "intervals_available",
            "interval_type",
        }
    ),
    "TimeSeriesKfold": frozenset(
        {
            "times",
            "y",
            "y_hat",
            "y_lower",
            "y_upper",
            "effect_cumulative_tsk",
            "effect_ci_lower_cumulative_tsk",
            "effect_ci_upper_cumulative_tsk",
        }
    ),
}

# Optional keys that may appear on successful Placebo runs.
PLACEBO_OPTIONAL_KEYS = frozenset(
    {
        "effect_ci_lower_inversion",
        "effect_ci_upper_inversion",
        "effect_interval_type",
        "inference_metadata",
    }
)

GOLDEN_NUMERIC_KEYS: dict[str, tuple[str, ...]] = {
    "point_estimate": ("y_hat",),
    "UnitJackKnife": ("y_hat", "y_lower", "y_upper"),
    "JKP": ("y_hat", "y_lower", "y_upper"),
    "Bayesian": ("y_hat", "y_lower", "y_upper"),
    "BlockResidualBootstrap": (
        "y_hat",
        "y_lower",
        "y_upper",
        "effect_cumulative_brb",
        "effect_ci_lower_cumulative_brb",
        "effect_ci_upper_cumulative_brb",
    ),
    "Conformal": ("y_hat", "y_lower", "y_upper"),
    "Kfold": ("y_hat", "y_lower", "y_upper"),
    "Placebo": ("y_hat", "y_lower", "y_upper"),
    "TimeSeriesKfold": (
        "y_hat",
        "y_lower",
        "y_upper",
        "effect_cumulative_tsk",
        "effect_ci_lower_cumulative_tsk",
        "effect_ci_upper_cumulative_tsk",
    ),
}


def make_tbr_panel(
    seed: int = 42,
    n_time: int = 30,
    treat_start: int = 22,
    n_controls: int = 4,
) -> PanelDataset:
    rng = np.random.default_rng(seed)
    y = np.linspace(1000, 1200, n_time) + rng.normal(0, 25, n_time)
    rows = [y]
    geos = ["treated"]
    for i in range(n_controls):
        rows.append(np.linspace(800 + 50 * i, 960 + 50 * i, n_time) + rng.normal(0, 20, n_time))
        geos.append(f"ctrl_{i}")
    wide = pd.DataFrame(np.vstack(rows), index=geos, columns=range(n_time))
    return PanelDataset(wide, [TimePeriod(treat_start, None)], ["treated"])


def make_scm_panel(
    seed: int = 42,
    n_time: int = 30,
    treat_start: int = 22,
    n_ctrl: int = 6,
) -> PanelDataset:
    rng = np.random.default_rng(seed)
    y = np.cumsum(rng.standard_normal(n_time)) * 10 + 100
    rows = [y]
    geos = ["treated"]
    for i in range(n_ctrl):
        rows.append(np.cumsum(rng.standard_normal(n_time)) * 10 + 50 * i)
        geos.append(f"ctrl_{i}")
    wide = pd.DataFrame(np.vstack(rows), index=geos, columns=range(n_time))
    return PanelDataset(wide, [TimePeriod(treat_start, None)], ["treated"])


def load_golden(mode: str) -> dict[str, np.ndarray]:
    path = GOLDEN_DIR / f"{mode}.npz"
    if not path.exists():
        raise FileNotFoundError(path)
    with np.load(path) as data:
        return {k: data[k] for k in data.files}


def assert_arrays_allclose(
    actual: np.ndarray,
    expected: np.ndarray,
    *,
    rtol: float = 1e-10,
    atol: float = 1e-10,
    label: str = "",
) -> None:
    np.testing.assert_allclose(
        np.asarray(actual, dtype=float),
        np.asarray(expected, dtype=float),
        rtol=rtol,
        atol=atol,
        err_msg=label,
    )
