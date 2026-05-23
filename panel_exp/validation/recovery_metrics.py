"""
Recovery metrics for synthetic truth experiments.

Evaluates estimator outputs only; does not redefine estimators.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import numpy as np


@dataclass(frozen=True)
class SimulationRecord:
    """One simulation draw: predicted vs true effect and optional inference."""

    predicted_effect: float
    true_effect: float
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    significant: Optional[bool] = None
    failed: bool = False
    failure_type: Optional[str] = None
    failure_message: Optional[str] = None
    intervals_available: Optional[bool] = None
    intervals_unavailable_reason: Optional[str] = None
    point_estimand: str = "relative_att_post"
    interval_estimand: str = "unavailable"
    interval_scale: str = "unavailable"
    interval_aligned: bool = False
    significance_estimand: Optional[str] = None
    significance_aligned: bool = False


@dataclass(frozen=True)
class RecoveryResult:
    """Aggregated recovery metrics for one estimator × scenario battery."""

    estimator: str
    scenario: str
    bias: float
    absolute_bias: float
    coverage: float
    false_positive_rate: float
    power: float
    runtime_seconds: float
    recovery_success_rate: float
    n_simulations: int = 0
    failure_rate: float = 0.0
    failure_types: Dict[str, int] = field(default_factory=dict)
    coverage_status: str = "not_requested"
    coverage_unavailable_reason: Optional[str] = None
    false_positive_rate_status: str = "not_requested"
    false_positive_rate_unavailable_reason: Optional[str] = None
    power_status: str = "not_requested"
    power_unavailable_reason: Optional[str] = None
    point_estimand: str = "relative_att_post"
    interval_estimand: str = "unavailable"
    interval_scale: str = "unavailable"
    significance_estimand: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _metric_status(
    values: List[float],
    *,
    expected: bool,
    reason_if_empty: str,
) -> tuple[float, str, Optional[str]]:
    if values:
        return float(np.mean(values)), "computed", None
    if expected:
        return float("nan"), "unavailable", reason_if_empty
    return float("nan"), "not_requested", reason_if_empty


def aggregate_recovery_metrics(
    *,
    estimator: str,
    scenario: str,
    records: Sequence[SimulationRecord],
    recovery_tolerance: float = 0.15,
    null_threshold: float = 1e-9,
    alt_threshold: float = 0.02,
    intervals_expected: bool = False,
) -> RecoveryResult:
    """
    Aggregate simulation records into recovery metrics.

    recovery_success_rate: fraction with |predicted - true| <= recovery_tolerance
    (or <= max(recovery_tolerance, 2 * |true|) when |true| > null_threshold).
    """
    if not records:
        return RecoveryResult(
            estimator=estimator,
            scenario=scenario,
            bias=float("nan"),
            absolute_bias=float("nan"),
            coverage=float("nan"),
            false_positive_rate=float("nan"),
            power=float("nan"),
            runtime_seconds=0.0,
            recovery_success_rate=float("nan"),
            n_simulations=0,
            failure_rate=float("nan"),
            failure_types={},
            coverage_status="unavailable" if intervals_expected else "not_requested",
            coverage_unavailable_reason="no_records" if intervals_expected else None,
            false_positive_rate_status=(
                "unavailable" if intervals_expected else "not_requested"
            ),
            false_positive_rate_unavailable_reason=(
                "no_records" if intervals_expected else None
            ),
            power_status="unavailable" if intervals_expected else "not_requested",
            power_unavailable_reason="no_records" if intervals_expected else None,
            point_estimand="relative_att_post",
            interval_estimand="unavailable",
            interval_scale="unavailable",
            significance_estimand=None,
        )

    predicted = np.array([r.predicted_effect for r in records], dtype=float)
    truth = np.array([r.true_effect for r in records], dtype=float)
    errors = predicted - truth

    bias = float(np.nanmean(errors))
    absolute_bias = float(np.nanmean(np.abs(errors)))

    tol = np.where(
        np.abs(truth) > null_threshold,
        np.maximum(recovery_tolerance, 2.0 * np.abs(truth)),
        recovery_tolerance,
    )
    recovery_success_rate = float(
        np.nanmean(np.abs(errors) <= tol)
    )

    failed_flags = np.array([r.failed for r in records], dtype=bool)
    failure_rate = float(np.mean(failed_flags))
    failure_types = dict(Counter(r.failure_type for r in records if r.failure_type))

    coverage_vals: List[float] = []
    interval_missing_reasons: List[str] = []
    for rec in records:
        if rec.failed:
            continue
        if not rec.interval_aligned:
            interval_missing_reasons.append(
                rec.intervals_unavailable_reason or "interval_estimand_mismatch"
            )
            continue
        if rec.ci_lower is None or rec.ci_upper is None:
            if rec.intervals_unavailable_reason:
                interval_missing_reasons.append(rec.intervals_unavailable_reason)
            continue
        if not (np.isfinite(rec.ci_lower) and np.isfinite(rec.ci_upper)):
            interval_missing_reasons.append("non_finite_interval")
            continue
        coverage_vals.append(
            1.0 if rec.ci_lower <= rec.true_effect <= rec.ci_upper else 0.0
        )
    cov_reason = (
        "; ".join(sorted(set(interval_missing_reasons)))
        if interval_missing_reasons
        else "no_intervals_in_replications"
    )
    coverage, coverage_status, coverage_unavailable_reason = _metric_status(
        coverage_vals,
        expected=intervals_expected,
        reason_if_empty=cov_reason,
    )

    fpr_vals: List[float] = []
    power_vals: List[float] = []
    sig_missing = 0
    mixed_estimand = 0
    for rec in records:
        if rec.failed:
            continue
        if rec.significant is None:
            sig_missing += 1
            continue
        if not rec.significance_aligned:
            mixed_estimand += 1
            continue
        is_null = abs(rec.true_effect) <= null_threshold
        is_alt = abs(rec.true_effect) >= alt_threshold
        if is_null:
            fpr_vals.append(1.0 if rec.significant else 0.0)
        if is_alt:
            power_vals.append(1.0 if rec.significant else 0.0)

    fpr_reason = (
        "mixed_estimand_significance"
        if mixed_estimand and not fpr_vals
        else (
            "no_significance_flags"
            if sig_missing and not fpr_vals
            else "no_null_replications"
        )
    )
    false_positive_rate, fpr_status, fpr_unavailable_reason = _metric_status(
        fpr_vals,
        expected=intervals_expected,
        reason_if_empty=fpr_reason,
    )
    power, power_status, power_unavailable_reason = _metric_status(
        power_vals,
        expected=intervals_expected,
        reason_if_empty=(
            "mixed_estimand_significance"
            if mixed_estimand and not power_vals
            else "no_positive_effect_replications"
        ),
    )

    point_estimand = records[0].point_estimand if records else "relative_att_post"
    aligned_intervals = [r.interval_estimand for r in records if r.interval_aligned]
    if aligned_intervals:
        interval_estimand = aligned_intervals[0]
        interval_scale = records[
            next(i for i, r in enumerate(records) if r.interval_aligned)
        ].interval_scale
    else:
        interval_estimand = records[0].interval_estimand if records else "unavailable"
        interval_scale = records[0].interval_scale if records else "unavailable"

    sig_estims = [r.significance_estimand for r in records if r.significance_estimand]
    significance_estimand = sig_estims[0] if sig_estims else None

    return RecoveryResult(
        estimator=estimator,
        scenario=scenario,
        bias=bias,
        absolute_bias=absolute_bias,
        coverage=coverage,
        false_positive_rate=false_positive_rate,
        power=power,
        runtime_seconds=0.0,
        recovery_success_rate=recovery_success_rate,
        n_simulations=len(records),
        failure_rate=failure_rate,
        failure_types=failure_types,
        coverage_status=coverage_status,
        coverage_unavailable_reason=coverage_unavailable_reason,
        false_positive_rate_status=fpr_status,
        false_positive_rate_unavailable_reason=fpr_unavailable_reason,
        power_status=power_status,
        power_unavailable_reason=power_unavailable_reason,
        point_estimand=point_estimand,
        interval_estimand=interval_estimand,
        interval_scale=interval_scale,
        significance_estimand=significance_estimand,
    )
