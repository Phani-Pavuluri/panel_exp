"""
Recovery metrics for synthetic truth experiments.

Evaluates estimator outputs only; does not redefine estimators.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def aggregate_recovery_metrics(
    *,
    estimator: str,
    scenario: str,
    records: Sequence[SimulationRecord],
    recovery_tolerance: float = 0.15,
    null_threshold: float = 1e-9,
    alt_threshold: float = 0.02,
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

    coverage_vals: List[float] = []
    for rec in records:
        if rec.ci_lower is None or rec.ci_upper is None:
            continue
        if not (np.isfinite(rec.ci_lower) and np.isfinite(rec.ci_upper)):
            continue
        coverage_vals.append(
            1.0 if rec.ci_lower <= rec.true_effect <= rec.ci_upper else 0.0
        )
    coverage = float(np.mean(coverage_vals)) if coverage_vals else float("nan")

    sig_flags = [r.significant for r in records if r.significant is not None]
    false_positive_rate = float("nan")
    power = float("nan")
    if sig_flags:
        sig = np.array(sig_flags, dtype=bool)
        is_null = np.abs(truth) <= null_threshold
        is_alt = np.abs(truth) >= alt_threshold
        if np.any(is_null):
            false_positive_rate = float(np.mean(sig[is_null]))
        if np.any(is_alt):
            power = float(np.mean(sig[is_alt]))

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
    )
