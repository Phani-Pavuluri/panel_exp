"""
Production-scale nominal calibration for aligned inference recovery configs.

Uses ``RecoveryRunner`` only; does not change estimators, inference, or scoring.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from panel_exp.validation.calibration_report import MIN_REPLICATIONS_FOR_STABLE_CALIBRATION
from panel_exp.validation.nominal_calibration import (
    NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS,
    _build_warnings,
    _safe,
    ineligible_reason_for_calibration,
    interval_aligned_from_payload,
    is_nominal_calibration_eligible_config,
    payload_eligible_for_nominal_calibration,
)
from panel_exp.validation.synthetic_scenarios import SyntheticScenario

DEFAULT_SCENARIOS: Tuple[str, ...] = (
    "recovery_null_effect",
    "recovery_positive_effect",
)

PRODUCTION_N_SIMULATIONS_DEFAULT = 100
PRODUCTION_RANDOM_SEEDS_DEFAULT: Tuple[int, ...] = (0, 1, 2)

BELOW_PRODUCTION_REPLICATION_WARNING = (
    "Calibration run is below production replication target; "
    f"use n_simulations >= {MIN_REPLICATIONS_FOR_STABLE_CALIBRATION} for production evidence."
)

_STABILITY_STD_THRESHOLD = 0.05
_MAX_FAILURE_RATE_WARN = 0.05


def _finite_values(values: Sequence[float]) -> List[float]:
    return [float(v) for v in values if v == v and math.isfinite(v)]


def _distribution_stats(values: Sequence[float]) -> Dict[str, float]:
    finite = _finite_values(values)
    if not finite:
        return {
            "mean": float("nan"),
            "std": float("nan"),
            "min": float("nan"),
            "max": float("nan"),
            "n": 0.0,
        }
    arr = finite
    mean = float(sum(arr) / len(arr))
    if len(arr) == 1:
        std = 0.0
    else:
        var = sum((x - mean) ** 2 for x in arr) / (len(arr) - 1)
        std = float(math.sqrt(var))
    return {
        "mean": mean,
        "std": std,
        "min": float(min(arr)),
        "max": float(max(arr)),
        "n": float(len(arr)),
    }


def evaluate_coverage_aggregate_status(
    mean_coverage: float,
    *,
    per_seed_available: bool,
) -> str:
    if not per_seed_available or mean_coverage != mean_coverage:
        return "unavailable"
    if mean_coverage >= 0.90:
        return "pass"
    if mean_coverage >= 0.80:
        return "warn"
    return "fail"


def evaluate_fpr_aggregate_status(
    mean_fpr: float,
    *,
    per_seed_available: bool,
) -> str:
    if not per_seed_available or mean_fpr != mean_fpr:
        return "unavailable"
    if mean_fpr <= 0.10:
        return "pass"
    if mean_fpr <= 0.15:
        return "warn"
    return "fail"


def evaluate_power_aggregate_status(
    mean_power: float,
    *,
    per_seed_available: bool,
) -> str:
    if not per_seed_available or mean_power != mean_power:
        return "unavailable"
    if mean_power >= 0.80:
        return "pass"
    if mean_power >= 0.60:
        return "warn"
    return "fail"


def evaluate_stability_aggregate_status(
    *,
    coverage_std: float,
    fpr_std: float,
    power_std: float,
    mean_failure_rate: float,
) -> str:
    for std in (coverage_std, fpr_std, power_std):
        if std == std and std > _STABILITY_STD_THRESHOLD:
            return "warn"
    if mean_failure_rate == mean_failure_rate and mean_failure_rate > _MAX_FAILURE_RATE_WARN:
        return "warn"
    return "pass"


def _metric_available(status: str) -> bool:
    return status == "computed"


def _merge_failure_types(runs: Sequence[Mapping[str, Any]]) -> Dict[str, int]:
    merged: Dict[str, int] = {}
    for run in runs:
        types = run.get("failure_types") or {}
        if not isinstance(types, Mapping):
            continue
        for key, count in types.items():
            merged[str(key)] = merged.get(str(key), 0) + int(count)
    return merged


def _run_recovery_payload(
    estimator_config: str,
    scenario: Union[str, SyntheticScenario],
    *,
    n_simulations: int,
    random_state: int,
    alpha: float,
) -> Dict[str, Any]:
    from panel_exp.validation.recovery_runner import RecoveryRunner

    runner = RecoveryRunner(
        estimator_config,
        scenario,
        n_simulations=n_simulations,
        random_state=random_state,
        alpha=alpha,
    )
    payload = runner.run()
    payload["estimator_config"] = estimator_config
    return payload


def _per_seed_record(
    estimator_config: str,
    scenario: str,
    *,
    n_simulations: int,
    random_state: int,
    alpha: float,
    payload: Mapping[str, Any],
) -> Dict[str, Any]:
    eligible = payload_eligible_for_nominal_calibration(estimator_config, payload)
    aligned = interval_aligned_from_payload(payload)
    warnings = _build_warnings(
        dict(payload),
        n_simulations=n_simulations,
        eligible=eligible,
    )
    return {
        "estimator_config": estimator_config,
        "scenario": scenario,
        "random_state": int(random_state),
        "n_simulations": int(n_simulations),
        "alpha": float(alpha),
        "coverage": _safe(payload.get("coverage")),
        "coverage_status": str(payload.get("coverage_status", "unknown")),
        "false_positive_rate": _safe(payload.get("false_positive_rate")),
        "false_positive_rate_status": str(
            payload.get("false_positive_rate_status", "unknown")
        ),
        "power": _safe(payload.get("power")),
        "power_status": str(payload.get("power_status", "unknown")),
        "recovery_success_rate": _safe(payload.get("recovery_success_rate")),
        "failure_rate": _safe(payload.get("failure_rate")),
        "failure_types": dict(payload.get("failure_types") or {}),
        "n_simulations_run": int(payload.get("n_simulations", n_simulations)),
        "point_estimand": payload.get("point_estimand"),
        "interval_estimand": payload.get("interval_estimand"),
        "interval_scale": payload.get("interval_scale"),
        "interval_aligned": aligned,
        "eligible_for_nominal_calibration": eligible,
        "ineligible_reason": ineligible_reason_for_calibration(estimator_config, payload),
        "warnings": warnings,
    }


def _should_run_before_eligibility_check(estimator_config: str) -> bool:
    """Run recovery when intervals may exist but alignment must be verified (e.g. DID)."""
    from panel_exp.validation.recovery_runner import all_recovery_configs

    spec = all_recovery_configs().get(estimator_config)
    if spec is None:
        return False
    return bool(spec.intervals_expected) or is_nominal_calibration_eligible_config(
        estimator_config
    )


def _skip_without_run(
    estimator_config: str,
    scenario: str,
    *,
    reason: str,
    n_simulations: int,
    alpha: float,
) -> Dict[str, Any]:
    return {
        "estimator_config": estimator_config,
        "scenario": scenario,
        "skipped": True,
        "ineligible_reason": reason,
        "eligible_for_nominal_calibration": False,
        "interval_aligned": False,
        "n_simulations": int(n_simulations),
        "alpha": float(alpha),
        "warnings": [
            f"Skipped {estimator_config!r} on {scenario!r}: {reason}.",
        ],
    }


@dataclass
class ProductionNominalCalibrationResult:
    """Full production calibration battery output."""

    n_simulations: int
    random_seeds: Tuple[int, ...]
    alpha: float
    global_warnings: List[str] = field(default_factory=list)
    per_seed_runs: List[Dict[str, Any]] = field(default_factory=list)
    skipped: List[Dict[str, Any]] = field(default_factory=list)
    aggregates: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_simulations": self.n_simulations,
            "random_seeds": list(self.random_seeds),
            "alpha": self.alpha,
            "global_warnings": list(self.global_warnings),
            "per_seed_runs": list(self.per_seed_runs),
            "skipped": list(self.skipped),
            "aggregates": list(self.aggregates),
        }


def _aggregate_config_scenario(
    estimator_config: str,
    scenario: str,
    runs: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    eligible_runs = [r for r in runs if r.get("eligible_for_nominal_calibration")]
    if not eligible_runs:
        reasons = {str(r.get("ineligible_reason", "unknown")) for r in runs}
        return {
            "estimator_config": estimator_config,
            "scenario": scenario,
            "eligible_for_nominal_calibration": False,
            "ineligible_reason": sorted(reasons)[0] if len(reasons) == 1 else "mixed",
            "n_seeds": len(runs),
            "per_seed_runs": list(runs),
            "coverage_status": "unavailable",
            "fpr_status": "unavailable",
            "power_status": "unavailable",
            "stability_status": "unavailable",
        }

    coverage_vals = [float(r["coverage"]) for r in eligible_runs]
    fpr_vals = [float(r["false_positive_rate"]) for r in eligible_runs]
    power_vals = [float(r["power"]) for r in eligible_runs]
    success_vals = [float(r["recovery_success_rate"]) for r in eligible_runs]
    fail_vals = [float(r["failure_rate"]) for r in eligible_runs]

    coverage_stats = _distribution_stats(coverage_vals)
    fpr_stats = _distribution_stats(fpr_vals)
    power_stats = _distribution_stats(power_vals)
    success_stats = _distribution_stats(success_vals)
    failure_stats = _distribution_stats(fail_vals)

    coverage_available = all(
        _metric_available(str(r.get("coverage_status", ""))) for r in eligible_runs
    )
    fpr_available = all(
        _metric_available(str(r.get("false_positive_rate_status", "")))
        for r in eligible_runs
    )
    power_available = all(
        _metric_available(str(r.get("power_status", ""))) for r in eligible_runs
    )

    coverage_status = evaluate_coverage_aggregate_status(
        coverage_stats["mean"], per_seed_available=coverage_available
    )
    fpr_status = evaluate_fpr_aggregate_status(
        fpr_stats["mean"], per_seed_available=fpr_available
    )
    power_status = evaluate_power_aggregate_status(
        power_stats["mean"], per_seed_available=power_available
    )
    stability_status = evaluate_stability_aggregate_status(
        coverage_std=coverage_stats["std"],
        fpr_std=fpr_stats["std"],
        power_std=power_stats["std"],
        mean_failure_rate=failure_stats["mean"],
    )

    first = eligible_runs[0]
    return {
        "estimator_config": estimator_config,
        "scenario": scenario,
        "eligible_for_nominal_calibration": True,
        "n_seeds": len(eligible_runs),
        "per_seed_runs": list(eligible_runs),
        "point_estimand": first.get("point_estimand"),
        "interval_estimand": first.get("interval_estimand"),
        "interval_scale": first.get("interval_scale"),
        "interval_aligned": first.get("interval_aligned"),
        "coverage": coverage_stats,
        "false_positive_rate": fpr_stats,
        "power": power_stats,
        "recovery_success_rate": success_stats,
        "failure_rate": failure_stats,
        "failure_types": _merge_failure_types(eligible_runs),
        "coverage_status": coverage_status,
        "fpr_status": fpr_status,
        "power_status": power_status,
        "stability_status": stability_status,
        "warnings": _merge_warnings(eligible_runs),
    }


def _merge_warnings(runs: Sequence[Mapping[str, Any]]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for run in runs:
        for w in run.get("warnings") or []:
            if w not in seen:
                seen.add(w)
                out.append(str(w))
    return out


def run_production_nominal_calibration(
    estimator_configs: Optional[Sequence[str]] = None,
    scenarios: Optional[Sequence[Union[str, SyntheticScenario]]] = None,
    n_simulations: int = PRODUCTION_N_SIMULATIONS_DEFAULT,
    random_seeds: Sequence[int] = PRODUCTION_RANDOM_SEEDS_DEFAULT,
    *,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """
    Run nominal calibration across seeds for aligned inference configs.

    Only configs that remain ``eligible_for_nominal_calibration`` after each run
    are aggregated. Ineligible configs (e.g. ``DID_Bootstrap``) are recorded with
    explicit reasons; failed replications remain in per-seed ``failure_rate`` /
    ``failure_types``.
    """
    from panel_exp.validation.recovery_runner import all_recovery_configs

    configs = list(
        estimator_configs or sorted(NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS)
    )
    scenario_list = list(scenarios or DEFAULT_SCENARIOS)
    seeds = tuple(int(s) for s in random_seeds)
    n_simulations = int(n_simulations)

    global_warnings: List[str] = []
    if n_simulations < MIN_REPLICATIONS_FOR_STABLE_CALIBRATION:
        global_warnings.append(BELOW_PRODUCTION_REPLICATION_WARNING)

    specs = all_recovery_configs()
    per_seed_runs: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    grouped: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}

    for estimator_config in configs:
        if estimator_config not in specs:
            for scenario in scenario_list:
                sc_name = str(scenario)
                entry = _skip_without_run(
                    estimator_config,
                    sc_name,
                    reason="unknown_recovery_config",
                    n_simulations=n_simulations,
                    alpha=alpha,
                )
                skipped.append(entry)
            continue

        for scenario in scenario_list:
            sc_name = str(
                scenario.name if isinstance(scenario, SyntheticScenario) else scenario
            )
            key = (estimator_config, sc_name)

            if not _should_run_before_eligibility_check(estimator_config):
                entry = _skip_without_run(
                    estimator_config,
                    sc_name,
                    reason="intervals_not_expected",
                    n_simulations=n_simulations,
                    alpha=alpha,
                )
                skipped.append(entry)
                grouped.setdefault(key, []).append(entry)
                continue

            for seed in seeds:
                payload = _run_recovery_payload(
                    estimator_config,
                    scenario,
                    n_simulations=n_simulations,
                    random_state=int(seed),
                    alpha=alpha,
                )
                record = _per_seed_record(
                    estimator_config,
                    sc_name,
                    n_simulations=n_simulations,
                    random_state=int(seed),
                    alpha=alpha,
                    payload=payload,
                )
                if record["eligible_for_nominal_calibration"]:
                    per_seed_runs.append(record)
                else:
                    skipped.append(
                        {
                            **record,
                            "skipped": True,
                        }
                    )
                grouped.setdefault(key, []).append(record)

    aggregates = [
        _aggregate_config_scenario(estimator_config, scenario, runs)
        for (estimator_config, scenario), runs in sorted(grouped.items())
    ]

    result = ProductionNominalCalibrationResult(
        n_simulations=n_simulations,
        random_seeds=seeds,
        alpha=alpha,
        global_warnings=global_warnings,
        per_seed_runs=per_seed_runs,
        skipped=skipped,
        aggregates=aggregates,
    )
    return result.to_dict()


__all__ = [
    "BELOW_PRODUCTION_REPLICATION_WARNING",
    "DEFAULT_SCENARIOS",
    "PRODUCTION_N_SIMULATIONS_DEFAULT",
    "PRODUCTION_RANDOM_SEEDS_DEFAULT",
    "ProductionNominalCalibrationResult",
    "evaluate_coverage_aggregate_status",
    "evaluate_fpr_aggregate_status",
    "evaluate_power_aggregate_status",
    "evaluate_stability_aggregate_status",
    "run_production_nominal_calibration",
]
