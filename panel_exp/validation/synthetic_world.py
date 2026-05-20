"""
Generate synthetic panel worlds with known treatment effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from panel_exp.panel_data import PanelDataset, TimePeriod

EffectType = Literal["absolute", "relative"]

OUTCOME_COL = "outcome"
UNIT_COL = "geo"
TIME_COL = "time"


@dataclass(frozen=True)
class SyntheticScenario:
    """Specification for a single synthetic validation world."""

    name: str
    n_geos: int = 20
    n_periods: int = 50
    treatment_start: int = 35
    treated_units: Tuple[str, ...] = ()
    true_effect: float = 0.0
    effect_type: EffectType = "relative"
    baseline_level: float = 100.0
    trend: float = 0.02
    seasonality_amplitude: float = 0.0
    noise_scale: float = 1.0
    autocorrelation: float = 0.3
    cross_geo_correlation: float = 0.5
    outlier_probability: float = 0.0
    missing_probability: float = 0.0
    heterogeneous_effects: bool = False
    spillover_strength: float = 0.0
    random_state: Optional[int] = 0

    def __post_init__(self) -> None:
        if self.n_geos < 2:
            raise ValueError("n_geos must be at least 2")
        if not 0 <= self.treatment_start < self.n_periods:
            raise ValueError("treatment_start must lie in [0, n_periods)")
        if self.effect_type not in ("relative", "absolute"):
            raise ValueError("effect_type must be 'relative' or 'absolute'")
        if len(self.treated_units) >= self.n_geos:
            raise ValueError("treated_units must be a proper subset of geos")


@dataclass(frozen=True)
class SyntheticWorld:
    """
    Materialized synthetic panel with known truth.

    ``panel_data`` is long format (geo, time, outcome, treated, post).
    ``truth`` holds scalar and unit-level ground truth for validation metrics.
    """

    scenario: SyntheticScenario
    panel_data: pd.DataFrame
    truth: Dict[str, object]

    def to_panel_dataset(self) -> PanelDataset:
        """Build a ``PanelDataset`` for running existing estimators (validation only)."""
        wide = self.panel_data.pivot_table(
            index=UNIT_COL,
            columns=TIME_COL,
            values=OUTCOME_COL,
            aggfunc="first",
        )
        wide = wide.fillna(0.0)
        treated = list(self.truth["treated_units"])
        t0 = int(self.truth["treatment_start"])
        t_end = int(wide.columns.max())
        periods = [TimePeriod(t0, t_end) for _ in treated]
        return PanelDataset(
            wide,
            treated_periods=periods,
            treated_units=treated,
        )

    @classmethod
    def generate(cls, scenario: SyntheticScenario) -> "SyntheticWorld":
        seed = 0 if scenario.random_state is None else int(scenario.random_state)
        rng = np.random.default_rng(seed)

        n_geos = scenario.n_geos
        n_periods = scenario.n_periods
        t0 = scenario.treatment_start

        all_units = [f"geo_{i}" for i in range(n_geos)]
        if scenario.treated_units:
            treated_units = list(scenario.treated_units)
            for u in treated_units:
                if u not in all_units:
                    raise ValueError(f"treated unit {u!r} not in geo list")
        else:
            n_treated = max(1, min(n_geos - 1, n_geos // 5))
            idx = rng.choice(n_geos, size=n_treated, replace=False)
            treated_units = [all_units[i] for i in sorted(idx)]

        control_units = [u for u in all_units if u not in treated_units]
        times = list(range(n_periods))

        geo_fe = rng.normal(0.0, 2.0, size=n_geos)
        common = np.zeros((n_geos, n_periods))
        factor = 0.0
        for t in range(n_periods):
            shock = rng.normal(0.0, scenario.noise_scale)
            factor = (
                scenario.autocorrelation * factor
                + np.sqrt(max(0.0, 1.0 - scenario.autocorrelation**2)) * shock
            )
            seasonal = scenario.seasonality_amplitude * np.sin(
                2.0 * np.pi * t / max(4, n_periods // 4)
            )
            level = scenario.baseline_level + scenario.trend * t + seasonal + factor
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

        effect_by_unit: Dict[str, float] = {u: 0.0 for u in all_units}
        if scenario.heterogeneous_effects and scenario.true_effect != 0.0:
            spreads = rng.uniform(0.5, 1.5, size=len(treated_units))
            for u, spread in zip(treated_units, spreads):
                effect_by_unit[u] = float(scenario.true_effect * spread)
        else:
            for u in treated_units:
                effect_by_unit[u] = float(scenario.true_effect)

        counterfactual = baseline.copy()
        observed = baseline.copy()

        for gi, unit in enumerate(all_units):
            effect = effect_by_unit[unit]
            if unit not in treated_units:
                continue
            post_slice = slice(t0, n_periods)
            if scenario.effect_type == "relative":
                observed[gi, post_slice] = baseline[gi, post_slice] * (1.0 + effect)
            else:
                scale = float(np.mean(baseline[gi, :t0])) if t0 > 0 else 1.0
                observed[gi, post_slice] = baseline[gi, post_slice] + effect * scale

        if scenario.spillover_strength > 0.0:
            for gi, unit in enumerate(all_units):
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

        rows: List[Dict[str, object]] = []
        for gi, unit in enumerate(all_units):
            for t in times:
                y = float(observed[gi, t])
                if scenario.missing_probability > 0.0:
                    if rng.random() < scenario.missing_probability:
                        y = float("nan")
                treated_flag = int(unit in treated_units)
                post_flag = int(t >= t0)
                rows.append(
                    {
                        UNIT_COL: unit,
                        TIME_COL: t,
                        OUTCOME_COL: y,
                        "treated": treated_flag,
                        "post": post_flag,
                    }
                )

        panel_data = pd.DataFrame(rows)
        scalar_truth = _scalar_truth_effect(
            observed,
            counterfactual,
            treated_units,
            t0,
            n_periods,
            scenario.effect_type,
            scenario.true_effect,
        )

        truth: Dict[str, object] = {
            "scenario_name": scenario.name,
            "true_effect": scalar_truth,
            "configured_effect": scenario.true_effect,
            "effect_type": scenario.effect_type,
            "treatment_start": t0,
            "treated_units": tuple(treated_units),
            "control_units": tuple(control_units),
            "effect_by_unit": dict(effect_by_unit),
        }

        return cls(scenario=scenario, panel_data=panel_data, truth=truth)


def _scalar_truth_effect(
    observed: np.ndarray,
    counterfactual: np.ndarray,
    treated_units: Sequence[str],
    treatment_start: int,
    n_periods: int,
    effect_type: str,
    configured_effect: float,
) -> float:
    """
    Scalar truth on the validation scale: mean relative post lift for relative
    scenarios, mean absolute post lift otherwise.
    """
    all_units = [f"geo_{i}" for i in range(observed.shape[0])]
    unit_to_idx = {u: i for i, u in enumerate(all_units)}
    post = slice(treatment_start, n_periods)
    lifts: List[float] = []
    for unit in treated_units:
        gi = unit_to_idx[unit]
        y = observed[gi, post]
        y_cf = counterfactual[gi, post]
        mask = np.isfinite(y) & np.isfinite(y_cf)
        if not np.any(mask):
            continue
        if effect_type == "relative":
            denom = y_cf[mask]
            denom = denom[denom != 0]
            if denom.size == 0:
                continue
            lifts.extend(((y[mask] - y_cf[mask]) / y_cf[mask])[y_cf[mask] != 0])
        else:
            lifts.extend((y[mask] - y_cf[mask]).tolist())
    if lifts:
        return float(np.mean(lifts))
    return float(configured_effect)
