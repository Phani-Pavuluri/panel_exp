"""
Validation metrics for synthetic truth recovery.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence

import numpy as np


@dataclass(frozen=True)
class ValidationResult:
    estimator_name: str
    scenario_name: str
    bias: float
    rmse: float
    coverage: float
    false_positive_rate: float
    false_negative_rate: float
    power: float
    interval_width: float
    n_replications: int = 0
    truth: float = float("nan")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReplicationRecord:
    estimate: float
    truth: float
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    significant: Optional[bool] = None


def aggregate_replications(
    *,
    estimator_name: str,
    scenario_name: str,
    records: Sequence[ReplicationRecord],
    alternative_threshold: float = 0.02,
) -> ValidationResult:
    """
    Aggregate replication outcomes into summary metrics.

    Parameters
    ----------
    alternative_threshold : float
        Minimum |truth| to count false negatives / power (relative scale).
    """
    if not records:
        return ValidationResult(
            estimator_name=estimator_name,
            scenario_name=scenario_name,
            bias=float("nan"),
            rmse=float("nan"),
            coverage=float("nan"),
            false_positive_rate=float("nan"),
            false_negative_rate=float("nan"),
            power=float("nan"),
            interval_width=float("nan"),
            n_replications=0,
        )

    estimates = np.array([r.estimate for r in records], dtype=float)
    truths = np.array([r.truth for r in records], dtype=float)
    truth = float(np.nanmean(truths))
    errors = estimates - truths

    bias = float(np.nanmean(errors))
    rmse = float(np.sqrt(np.nanmean(errors**2)))

    coverage_vals: List[float] = []
    width_vals: List[float] = []
    for rec in records:
        if rec.ci_lower is None or rec.ci_upper is None:
            continue
        if not (np.isfinite(rec.ci_lower) and np.isfinite(rec.ci_upper)):
            continue
        coverage_vals.append(
            1.0 if rec.ci_lower <= rec.truth <= rec.ci_upper else 0.0
        )
        width_vals.append(float(rec.ci_upper - rec.ci_lower))

    coverage = float(np.mean(coverage_vals)) if coverage_vals else float("nan")
    interval_width = float(np.mean(width_vals)) if width_vals else float("nan")

    sig_flags = [r.significant for r in records if r.significant is not None]
    false_positive_rate = float("nan")
    false_negative_rate = float("nan")
    power = float("nan")

    if sig_flags:
        sig = np.array(sig_flags, dtype=bool)
        is_null = np.isclose(truths, 0.0)
        is_alt = np.abs(truths) >= alternative_threshold

        if np.any(is_null):
            false_positive_rate = float(np.mean(sig[is_null]))
        if np.any(is_alt):
            false_negative_rate = float(np.mean(~sig[is_alt]))
            power = float(np.mean(sig[is_alt]))

    return ValidationResult(
        estimator_name=estimator_name,
        scenario_name=scenario_name,
        bias=bias,
        rmse=rmse,
        coverage=coverage,
        false_positive_rate=false_positive_rate,
        false_negative_rate=false_negative_rate,
        power=power,
        interval_width=interval_width,
        n_replications=len(records),
        truth=truth,
    )
