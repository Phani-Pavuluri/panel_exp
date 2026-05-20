"""
Validation metrics for synthetic truth recovery.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np


@dataclass(frozen=True)
class ValidationMetrics:
    estimator_name: str
    scenario_name: str
    n_replications: int
    bias: float
    rmse: float
    coverage: Optional[float]
    false_positive_rate: Optional[float]
    false_negative_rate: Optional[float]
    power: Optional[float]
    mean_interval_width: Optional[float]
    failure_rate: float
    warnings: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReplicationOutcome:
    estimate: float
    truth: float
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    significant: Optional[bool] = None
    failed: bool = False
    error_message: Optional[str] = None


def aggregate_outcomes(
    *,
    estimator_name: str,
    scenario_name: str,
    outcomes: Sequence[ReplicationOutcome],
    alternative_threshold: float = 0.02,
) -> ValidationMetrics:
    """Aggregate replication outcomes into summary metrics."""
    n_total = len(outcomes)
    if n_total == 0:
        return ValidationMetrics(
            estimator_name=estimator_name,
            scenario_name=scenario_name,
            n_replications=0,
            bias=float("nan"),
            rmse=float("nan"),
            coverage=None,
            false_positive_rate=None,
            false_negative_rate=None,
            power=None,
            mean_interval_width=None,
            failure_rate=float("nan"),
        )

    n_failed = sum(1 for o in outcomes if o.failed)
    failure_rate = float(n_failed / n_total)

    successful = [o for o in outcomes if not o.failed and np.isfinite(o.estimate)]
    warnings: List[str] = []
    if n_failed:
        warnings.append(f"{n_failed}/{n_total} replications failed")

    if not successful:
        return ValidationMetrics(
            estimator_name=estimator_name,
            scenario_name=scenario_name,
            n_replications=n_total,
            bias=float("nan"),
            rmse=float("nan"),
            coverage=None,
            false_positive_rate=None,
            false_negative_rate=None,
            power=None,
            mean_interval_width=None,
            failure_rate=failure_rate,
            warnings=tuple(warnings),
        )

    estimates = np.array([o.estimate for o in successful], dtype=float)
    truths = np.array([o.truth for o in successful], dtype=float)
    errors = estimates - truths
    bias = float(np.mean(errors))
    rmse = float(np.sqrt(np.mean(errors**2)))

    coverage_vals: List[float] = []
    width_vals: List[float] = []
    has_intervals = False
    for o in successful:
        if o.ci_lower is None or o.ci_upper is None:
            continue
        if not (np.isfinite(o.ci_lower) and np.isfinite(o.ci_upper)):
            continue
        has_intervals = True
        coverage_vals.append(1.0 if o.ci_lower <= o.truth <= o.ci_upper else 0.0)
        width_vals.append(float(o.ci_upper - o.ci_lower))

    coverage: Optional[float] = (
        float(np.mean(coverage_vals)) if coverage_vals else None
    )
    mean_interval_width: Optional[float] = (
        float(np.mean(width_vals)) if width_vals else None
    )

    false_positive_rate: Optional[float] = None
    false_negative_rate: Optional[float] = None
    power: Optional[float] = None

    if has_intervals:
        sig_pairs = [
            (o.significant, o.truth)
            for o in successful
            if o.significant is not None
        ]
        if sig_pairs:
            sig = np.array([p[0] for p in sig_pairs], dtype=bool)
            truths_sig = np.array([p[1] for p in sig_pairs], dtype=float)
            is_null = np.isclose(truths_sig, 0.0)
            is_alt = np.abs(truths_sig) >= alternative_threshold
            if np.any(is_null):
                false_positive_rate = float(np.mean(sig[is_null]))
            if np.any(is_alt):
                false_negative_rate = float(np.mean(~sig[is_alt]))
                power = float(np.mean(sig[is_alt]))
    else:
        warnings.append("Interval metrics omitted (no intervals available)")

    return ValidationMetrics(
        estimator_name=estimator_name,
        scenario_name=scenario_name,
        n_replications=n_total,
        bias=bias,
        rmse=rmse,
        coverage=coverage,
        false_positive_rate=false_positive_rate,
        false_negative_rate=false_negative_rate,
        power=power,
        mean_interval_width=mean_interval_width,
        failure_rate=failure_rate,
        warnings=tuple(warnings),
    )


# Backward-compatible aliases
ValidationResult = ValidationMetrics
ReplicationRecord = ReplicationOutcome
aggregate_replications = aggregate_outcomes
