"""
Generate synthetic panel worlds with known treatment effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

import numpy as np
import pandas as pd

from panel_exp.panel_data import PanelDataset, TimePeriod


@dataclass(frozen=True)
class SyntheticScenario:
    """Specification for a single synthetic validation world."""

    scenario_name: str
    n_geos: int = 20
    n_periods: int = 50
    treatment_start: int = 35
    n_treated: int = 4
    true_effect: float = 0.0
    effect_type: str = "relative"
    seasonality: float = 0.0
    trend: float = 0.02
    noise_scale: float = 1.0
    autocorrelation: float = 0.3
    cross_geo_correlation: float = 0.5
    outlier_probability: float = 0.0
    missing_probability: float = 0.0
    spillover_strength: float = 0.0
    heterogeneous_effects: bool = False
    random_state: int = 0

    def __post_init__(self) -> None:
        if self.n_geos < 2:
            raise ValueError("n_geos must be at least 2")
        if self.n_treated >= self.n_geos:
            raise ValueError("n_treated must be smaller than n_geos")
        if not 0 <= self.treatment_start < self.n_periods:
            raise ValueError("treatment_start must lie in [0, n_periods)")
        if self.effect_type not in ("relative", "absolute"):
            raise ValueError("effect_type must be 'relative' or 'absolute'")


@dataclass
class SyntheticWorld:
    """
    Materialized synthetic panel with known counterfactual and truth metric.

    ``truth_mean_relative_att`` is the mean post-period relative lift on treated
    units: mean((Y - Y_cf) / Y_cf) over treated geos and post periods.
    """

    scenario: SyntheticScenario
    wide_data: pd.DataFrame
    counterfactual_wide: pd.DataFrame
    treated_units: List[str]
    treatment_start: int
    truth_mean_relative_att: float
    panel: PanelDataset
    unit_effects: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, object] = field(default_factory=dict)

    @classmethod
    def generate(cls, scenario: SyntheticScenario) -> "SyntheticWorld":
        rng = np.random.default_rng(scenario.random_state)
        n_geos = scenario.n_geos
        n_periods = scenario.n_periods
        t0 = scenario.treatment_start

        units = [f"geo_{i}" for i in range(n_geos)]
        times = list(range(n_periods))

        treated_idx = rng.choice(n_geos, size=scenario.n_treated, replace=False)
        treated_units = [units[i] for i in sorted(treated_idx)]

        geo_fe = rng.normal(0.0, 2.0, size=n_geos)
        common = np.zeros((n_geos, n_periods))
        factor = 0.0
        for t in range(n_periods):
            shock = rng.normal(0.0, scenario.noise_scale)
            factor = (
                scenario.autocorrelation * factor
                + np.sqrt(max(0.0, 1.0 - scenario.autocorrelation**2)) * shock
            )
            seasonal = (
                scenario.seasonality
                * np.sin(2.0 * np.pi * t / max(4, n_periods // 4))
            )
            level = 100.0 + scenario.trend * t + seasonal + factor
            common[:, t] = level

        eps = rng.normal(0.0, scenario.noise_scale, size=(n_geos, n_periods))
        for i in range(n_geos):
            ar = np.zeros(n_periods)
            for t in range(1, n_periods):
                ar[t] = (
                    scenario.autocorrelation * ar[t - 1]
                    + rng.normal(0.0, scenario.noise_scale * 0.5)
                )
            eps[i] += ar

        cross = scenario.cross_geo_correlation * rng.normal(
            0.0, scenario.noise_scale, size=n_periods
        )
        baseline = common + geo_fe[:, None] + eps + cross[None, :]
        baseline = np.maximum(baseline, 1.0)

        unit_effects: Dict[str, float] = {}
        if scenario.heterogeneous_effects and scenario.true_effect != 0.0:
            spreads = rng.uniform(0.5, 1.5, size=scenario.n_treated)
            for u, spread in zip(treated_units, spreads):
                unit_effects[u] = float(scenario.true_effect * spread)
        else:
            for u in treated_units:
                unit_effects[u] = float(scenario.true_effect)

        counterfactual = baseline.copy()
        observed = baseline.copy()

        for gi, unit in enumerate(units):
            effect = unit_effects.get(unit, 0.0)
            if unit not in treated_units:
                continue
            post_slice = slice(t0, n_periods)
            if scenario.effect_type == "relative":
                observed[gi, post_slice] = baseline[gi, post_slice] * (1.0 + effect)
            else:
                scale = float(np.mean(baseline[gi, :t0])) if t0 > 0 else 1.0
                observed[gi, post_slice] = baseline[gi, post_slice] + effect * scale

        if scenario.spillover_strength > 0.0:
            for gi, unit in enumerate(units):
                if unit in treated_units:
                    continue
                post_slice = slice(t0, n_periods)
                if scenario.effect_type == "relative":
                    observed[gi, post_slice] *= (
                        1.0 + scenario.spillover_strength * scenario.true_effect
                    )
                else:
                    scale = float(np.mean(baseline[gi, :t0])) if t0 > 0 else 1.0
                    observed[gi, post_slice] += (
                        scenario.spillover_strength * scenario.true_effect * scale
                    )

        if scenario.outlier_probability > 0.0:
            n_outliers = rng.binomial(
                n_geos * n_periods, scenario.outlier_probability
            )
            if n_outliers > 0:
                flat_idx = rng.choice(
                    n_geos * n_periods,
                    size=min(n_outliers, n_geos * n_periods),
                    replace=False,
                )
                for idx in flat_idx:
                    gi, t = divmod(int(idx), n_periods)
                    observed[gi, t] *= rng.uniform(1.5, 3.0)

        if scenario.missing_probability > 0.0:
            mask = rng.random((n_geos, n_periods)) < scenario.missing_probability
            observed = observed.astype(float)
            observed[mask] = np.nan

        wide_obs = pd.DataFrame(observed, index=units, columns=times)
        wide_cf = pd.DataFrame(counterfactual, index=units, columns=times)

        truth = _mean_relative_att(wide_obs, wide_cf, treated_units, t0, n_periods)

        treated_periods = [TimePeriod(t0, times[-1]) for _ in treated_units]
        panel = PanelDataset(
            wide_obs.fillna(0.0),
            treated_periods=treated_periods,
            treated_units=treated_units,
        )

        metadata = {
            "effect_type": scenario.effect_type,
            "n_treated": scenario.n_treated,
            "treatment_start": t0,
            "heterogeneous_effects": scenario.heterogeneous_effects,
        }

        return cls(
            scenario=scenario,
            wide_data=wide_obs,
            counterfactual_wide=wide_cf,
            treated_units=treated_units,
            treatment_start=t0,
            truth_mean_relative_att=truth,
            panel=panel,
            unit_effects=unit_effects,
            metadata=metadata,
        )


def _mean_relative_att(
    observed: pd.DataFrame,
    counterfactual: pd.DataFrame,
    treated_units: Sequence[str],
    treatment_start: int,
    n_periods: int,
) -> float:
    """Mean relative lift on treated units in the post period."""
    rel_lifts: List[float] = []
    post_cols = list(range(treatment_start, n_periods))
    for unit in treated_units:
        y = observed.loc[unit, post_cols].to_numpy(dtype=float)
        y_cf = counterfactual.loc[unit, post_cols].to_numpy(dtype=float)
        mask = np.isfinite(y) & np.isfinite(y_cf) & (y_cf != 0)
        if not np.any(mask):
            continue
        rel_lifts.extend(((y[mask] - y_cf[mask]) / y_cf[mask]).tolist())
    if not rel_lifts:
        return float("nan")
    return float(np.mean(rel_lifts))
