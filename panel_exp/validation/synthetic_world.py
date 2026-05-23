"""
Generate synthetic panel worlds with known treatment effects.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from panel_exp.panel_data import PanelDataset, TimePeriod

EffectType = Literal["absolute", "relative"]
TreatmentTiming = Literal["simultaneous", "staggered_declared"]

MISSINGNESS_POLICY_FILL_ZERO = "fill_zero"
MISSINGNESS_POLICY_NONE = "none"
PANEL_MISSINGNESS_WARNING = (
    "Missing outcomes are filled with zero in synthetic panel conversion "
    f"(missingness_policy={MISSINGNESS_POLICY_FILL_ZERO!r})."
)
RECOVERY_AGGREGATION_MODE = "relative_att_post_path_mean"

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
    structural_break_shift: float = 0.0
    structural_break_time: Optional[int] = None
    treatment_timing: TreatmentTiming = "simultaneous"
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
        if self.treatment_timing not in ("simultaneous", "staggered_declared"):
            raise ValueError(
                "treatment_timing must be 'simultaneous' or 'staggered_declared'"
            )


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

    def panel_conversion_metadata(self) -> Dict[str, object]:
        """Metadata for wide-panel conversion (missingness policy, aggregation)."""
        meta = dict(self.truth.get("panel_conversion") or {})
        meta.setdefault("missingness_policy", MISSINGNESS_POLICY_NONE)
        meta.setdefault("missing_probability", 0.0)
        meta.setdefault("missing_cell_count", 0)
        meta.setdefault("panel_conversion_warning", None)
        meta.setdefault("treatment_timing", "simultaneous")
        meta.setdefault("aggregation_mode", RECOVERY_AGGREGATION_MODE)
        meta.setdefault("n_treated_units", len(self.truth.get("treated_units", ())))
        return meta

    def to_panel_dataset(self) -> PanelDataset:
        """Build a ``PanelDataset`` for running existing estimators (validation only)."""
        wide = self.panel_data.pivot_table(
            index=UNIT_COL,
            columns=TIME_COL,
            values=OUTCOME_COL,
            aggfunc="first",
        )
        n_missing = int(wide.isna().sum().sum())
        if n_missing > 0:
            warnings.warn(PANEL_MISSINGNESS_WARNING, UserWarning, stacklevel=2)
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

        if scenario.structural_break_shift != 0.0:
            break_t = scenario.structural_break_time
            if break_t is None:
                break_t = t0
            break_t = int(max(0, min(break_t, n_periods - 1)))
            baseline[:, break_t:] += float(scenario.structural_break_shift)

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
        missing_cell_count = int(panel_data[OUTCOME_COL].isna().sum())
        missingness_policy = (
            MISSINGNESS_POLICY_FILL_ZERO
            if missing_cell_count > 0
            else MISSINGNESS_POLICY_NONE
        )
        panel_conversion_warning = (
            PANEL_MISSINGNESS_WARNING if missing_cell_count > 0 else None
        )
        scalar_truth = _scalar_truth_effect(
            observed,
            counterfactual,
            treated_units,
            t0,
            n_periods,
            scenario.effect_type,
            scenario.true_effect,
            unit_names=all_units,
        )

        donor_corr = control_donor_correlation_summary(
            observed,
            control_units,
            all_units,
            t0,
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
            "unit_names": tuple(all_units),
            "observed": observed,
            "counterfactual": counterfactual,
            "cross_geo_correlation_param": float(scenario.cross_geo_correlation),
            "donor_correlation_summary": donor_corr,
            "panel_conversion": {
                "missingness_policy": missingness_policy,
                "missing_probability": float(scenario.missing_probability),
                "missing_cell_count": missing_cell_count,
                "panel_conversion_warning": panel_conversion_warning,
                "treatment_timing": scenario.treatment_timing,
                "aggregation_mode": RECOVERY_AGGREGATION_MODE,
                "n_treated_units": len(treated_units),
            },
        }

        return cls(scenario=scenario, panel_data=panel_data, truth=truth)


def control_donor_correlation_summary(
    observed: np.ndarray,
    control_units: Sequence[str],
    unit_names: Sequence[str],
    treatment_start: int,
) -> Dict[str, float]:
    """
    Summarize mean absolute off-diagonal correlation among control geos (pre-period).
    """
    if len(control_units) < 2:
        return {
            "mean_abs_off_diag_correlation": float("nan"),
            "max_abs_correlation": float("nan"),
            "n_control_units": float(len(control_units)),
        }
    unit_to_idx = _unit_index(unit_names, observed.shape[0])
    pre = slice(0, treatment_start)
    cols: List[np.ndarray] = []
    for unit in control_units:
        gi = unit_to_idx[unit]
        series = observed[gi, pre].astype(float)
        if np.sum(np.isfinite(series)) < 2:
            continue
        cols.append(series)
    if len(cols) < 2:
        return {
            "mean_abs_off_diag_correlation": float("nan"),
            "max_abs_correlation": float("nan"),
            "n_control_units": float(len(control_units)),
        }
    mat = np.column_stack(cols)
    corr = np.corrcoef(mat, rowvar=False)
    n = corr.shape[0]
    off_diag = corr[np.triu_indices(n, k=1)]
    abs_off = np.abs(off_diag[np.isfinite(off_diag)])
    if abs_off.size == 0:
        return {
            "mean_abs_off_diag_correlation": float("nan"),
            "max_abs_correlation": float("nan"),
            "n_control_units": float(len(control_units)),
        }
    return {
        "mean_abs_off_diag_correlation": float(np.mean(abs_off)),
        "max_abs_correlation": float(np.max(abs_off)),
        "n_control_units": float(len(control_units)),
    }


def _unit_index(
    unit_names: Sequence[str],
    n_rows: int,
) -> Dict[str, int]:
    if unit_names:
        return {u: i for i, u in enumerate(unit_names)}
    return {f"geo_{i}": i for i in range(n_rows)}


def canonical_relative_att_post(
    observed: np.ndarray,
    counterfactual: np.ndarray,
    treated_units: Sequence[str],
    treatment_start: int,
    n_periods: int,
    *,
    unit_names: Optional[Sequence[str]] = None,
) -> float:
    """
    Mean relative post-period lift on treated units: E[(Y - Y(0)) / Y(0)] over
    treated geos and post times (validation / test canonical).
    """
    unit_to_idx = _unit_index(unit_names or (), observed.shape[0])
    post = slice(treatment_start, n_periods)
    lifts: List[float] = []
    for unit in treated_units:
        gi = unit_to_idx[unit]
        y = observed[gi, post]
        y_cf = counterfactual[gi, post]
        mask = np.isfinite(y) & np.isfinite(y_cf)
        if not np.any(mask):
            continue
        denom = y_cf[mask]
        denom = denom[denom != 0]
        if denom.size == 0:
            continue
        lifts.extend(((y[mask] - y_cf[mask]) / y_cf[mask])[y_cf[mask] != 0])
    if lifts:
        return float(np.mean(lifts))
    return float("nan")


def canonical_absolute_att_post(
    observed: np.ndarray,
    counterfactual: np.ndarray,
    treated_units: Sequence[str],
    treatment_start: int,
    n_periods: int,
    *,
    unit_names: Optional[Sequence[str]] = None,
) -> float:
    """Mean absolute post-period lift on treated units."""
    unit_to_idx = _unit_index(unit_names or (), observed.shape[0])
    post = slice(treatment_start, n_periods)
    lifts: List[float] = []
    for unit in treated_units:
        gi = unit_to_idx[unit]
        y = observed[gi, post]
        y_cf = counterfactual[gi, post]
        mask = np.isfinite(y) & np.isfinite(y_cf)
        if not np.any(mask):
            continue
        lifts.extend((y[mask] - y_cf[mask]).tolist())
    if lifts:
        return float(np.mean(lifts))
    return float("nan")


def canonical_cumulative_att(
    observed: np.ndarray,
    counterfactual: np.ndarray,
    treated_units: Sequence[str],
    treatment_start: int,
    n_periods: int,
    *,
    unit_names: Optional[Sequence[str]] = None,
) -> float:
    """Sum of absolute post-period increments (Y - Y(0)) on treated units."""
    unit_to_idx = _unit_index(unit_names or (), observed.shape[0])
    post = slice(treatment_start, n_periods)
    total = 0.0
    n = 0
    for unit in treated_units:
        gi = unit_to_idx[unit]
        y = observed[gi, post]
        y_cf = counterfactual[gi, post]
        mask = np.isfinite(y) & np.isfinite(y_cf)
        if not np.any(mask):
            continue
        total += float(np.nansum(y[mask] - y_cf[mask]))
        n += int(np.sum(mask))
    if n == 0:
        return float("nan")
    return total


def canonical_pooled_relative_att_post(
    observed: np.ndarray,
    counterfactual: np.ndarray,
    treated_units: Sequence[str],
    treatment_start: int,
    n_periods: int,
    *,
    unit_names: Optional[Sequence[str]] = None,
) -> float:
    """
    Pooled treated time-series: sum outcomes across treated geos each period,
    then mean relative post lift (matches DID aggregate reporting scale).
    """
    unit_to_idx = _unit_index(unit_names or (), observed.shape[0])
    post = slice(treatment_start, n_periods)
    n_post = n_periods - treatment_start
    y_sum = np.zeros(n_post, dtype=float)
    y0_sum = np.zeros(n_post, dtype=float)
    for unit in treated_units:
        gi = unit_to_idx[unit]
        y_sum += observed[gi, post]
        y0_sum += counterfactual[gi, post]
    mask = np.isfinite(y_sum) & np.isfinite(y0_sum) & (y0_sum != 0)
    if not np.any(mask):
        return float("nan")
    return float(np.mean((y_sum[mask] - y0_sum[mask]) / y0_sum[mask]))


def _scalar_truth_effect(
    observed: np.ndarray,
    counterfactual: np.ndarray,
    treated_units: Sequence[str],
    treatment_start: int,
    n_periods: int,
    effect_type: str,
    configured_effect: float,
    *,
    unit_names: Optional[Sequence[str]] = None,
) -> float:
    """
    Scalar truth on the validation scale: mean relative post lift for relative
    scenarios, mean absolute post lift otherwise.
    """
    if effect_type == "relative":
        value = canonical_relative_att_post(
            observed,
            counterfactual,
            treated_units,
            treatment_start,
            n_periods,
            unit_names=unit_names,
        )
    else:
        value = canonical_absolute_att_post(
            observed,
            counterfactual,
            treated_units,
            treatment_start,
            n_periods,
            unit_names=unit_names,
        )
    if np.isfinite(value):
        return value
    return float(configured_effect)
