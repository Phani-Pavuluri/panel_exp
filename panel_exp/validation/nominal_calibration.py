"""
Nominal calibration smoke checks for recovery configs with aligned intervals.

Uses ``RecoveryRunner`` outputs; does not change estimators or inference.
CI smoke (small ``n_simulations``) is not production calibration — use n >= 100
for stable nominal checks (see ``MIN_REPLICATIONS_FOR_STABLE_CALIBRATION``).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping, Union

from panel_exp.validation.calibration_report import (
    MIN_REPLICATIONS_FOR_STABLE_CALIBRATION,
    CalibrationReport,
    compute_calibration_warnings,
)
from panel_exp.validation.recovery_intervals import INTERVAL_ESTIMAND_RELATIVE_ATT_POST
from panel_exp.validation.synthetic_scenarios import SyntheticScenario

NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS = frozenset(
    {
        "SCM_UnitJackKnife",
        "TBRRidge_Kfold",
        "TBRRidge_BlockResidualBootstrap",
    }
)

_CI_SMOKE_NOTE = (
    "CI smoke is not production calibration; production calibration should use "
    f"n >= {MIN_REPLICATIONS_FOR_STABLE_CALIBRATION}."
)


def is_nominal_calibration_eligible_config(estimator_config: str) -> bool:
    """True when config is designed for path-relative aligned intervals."""
    return estimator_config in NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS


def _interval_aligned_from_payload(payload: Mapping[str, Any]) -> bool:
    """True when recovery reported relative_att_post intervals (not DID cumulative)."""
    if payload.get("interval_estimand") != INTERVAL_ESTIMAND_RELATIVE_ATT_POST:
        return False
    reason = payload.get("coverage_unavailable_reason") or ""
    if "interval_estimand_mismatch" in reason:
        return False
    return bool(payload.get("intervals_expected"))


def interval_aligned_from_payload(payload: Mapping[str, Any]) -> bool:
    """True when recovery reported relative_att_post intervals (not DID cumulative)."""
    return _interval_aligned_from_payload(payload)


def payload_eligible_for_nominal_calibration(
    estimator_config: str,
    payload: Mapping[str, Any],
) -> bool:
    """True when config and payload support nominal relative-ATT calibration."""
    if not is_nominal_calibration_eligible_config(estimator_config):
        return False
    if not payload.get("intervals_expected"):
        return False
    return _interval_aligned_from_payload(payload)


def ineligible_reason_for_calibration(
    estimator_config: str,
    payload: Mapping[str, Any],
) -> str:
    """Human-readable skip reason when ``payload_eligible_for_nominal_calibration`` is False."""
    interval_est = str(payload.get("interval_estimand", "unknown"))
    if interval_est not in (
        "unknown",
        "unavailable",
        INTERVAL_ESTIMAND_RELATIVE_ATT_POST,
    ):
        return "interval_estimand_mismatch"
    if not is_nominal_calibration_eligible_config(estimator_config):
        return "not_in_nominal_calibration_registry"
    if not payload.get("intervals_expected"):
        return "intervals_not_expected"
    if not _interval_aligned_from_payload(payload):
        reason = payload.get("coverage_unavailable_reason") or ""
        if "interval_estimand_mismatch" in reason:
            return "interval_estimand_mismatch"
        return "interval_not_aligned"
    return "eligible"


def _eligible_for_nominal_calibration(
    estimator_config: str,
    payload: Mapping[str, Any],
) -> bool:
    return payload_eligible_for_nominal_calibration(estimator_config, payload)


def _build_warnings(
    payload: Mapping[str, Any],
    *,
    n_simulations: int,
    eligible: bool,
) -> List[str]:
    warnings: List[str] = []

    if not eligible:
        config = payload.get("estimator_config") or payload.get("recovery_config")
        interval_est = payload.get("interval_estimand", "unknown")
        if not is_nominal_calibration_eligible_config(str(config or "")):
            warnings.append(
                f"Config {config!r} is not eligible for nominal calibration "
                "(point-estimate or mismatched interval estimand)."
            )
        elif interval_est != INTERVAL_ESTIMAND_RELATIVE_ATT_POST:
            warnings.append(
                f"Interval estimand {interval_est!r} is not aligned with scored "
                f"{INTERVAL_ESTIMAND_RELATIVE_ATT_POST!r}; nominal calibration skipped."
            )
        else:
            reason = payload.get("coverage_unavailable_reason") or "unknown"
            warnings.append(f"Intervals not available for calibration: {reason}.")
        return warnings

    warnings.append(_CI_SMOKE_NOTE)

    if n_simulations < MIN_REPLICATIONS_FOR_STABLE_CALIBRATION:
        warnings.append(
            f"Calibration estimated from small simulation count "
            f"({n_simulations} < {MIN_REPLICATIONS_FOR_STABLE_CALIBRATION})."
        )

    if payload.get("coverage_status") == "unavailable":
        warnings.append(
            "Coverage unavailable for this run: "
            f"{payload.get('coverage_unavailable_reason', 'unknown')}."
        )

    # Advisory threshold warnings only when n is large enough for smoke to be meaningful.
    if n_simulations >= MIN_REPLICATIONS_FOR_STABLE_CALIBRATION:
        scenario = str(payload.get("scenario", ""))
        is_null = "null" in scenario.lower()
        is_positive = "positive" in scenario.lower()
        report = CalibrationReport(
            n_replications=n_simulations,
            false_positive_rate=_safe(payload.get("false_positive_rate")),
            coverage_under_null=_safe(payload.get("coverage"))
            if is_null
            else float("nan"),
            coverage_under_lift=_safe(payload.get("coverage"))
            if is_positive
            else float("nan"),
            power=_safe(payload.get("power")) if is_positive else float("nan"),
        )
        warnings.extend(compute_calibration_warnings(report))

    return warnings


def _safe(value: Any) -> float:
    if value is None:
        return float("nan")
    try:
        v = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return v if math.isfinite(v) else float("nan")


def run_nominal_calibration_check(
    estimator_config: str,
    scenario: Union[str, SyntheticScenario],
    n_simulations: int,
    *,
    alpha: float = 0.05,
    random_state: int = 0,
) -> Dict[str, Any]:
    """
    Run a recovery battery slice and summarize nominal calibration metrics.

    Only configs in ``NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`` with aligned
    ``relative_att_post`` intervals are marked ``eligible_for_nominal_calibration``.
    """
    from panel_exp.validation.recovery_runner import RecoveryRunner, all_recovery_configs

    specs = all_recovery_configs()
    if estimator_config not in specs:
        raise KeyError(
            f"Unknown estimator_config {estimator_config!r}; "
            f"known: {sorted(specs)}"
        )

    runner = RecoveryRunner(
        estimator_config,
        scenario,
        n_simulations=n_simulations,
        random_state=random_state,
        alpha=alpha,
    )
    payload = runner.run()
    scenario_name = payload.get("scenario", str(scenario))

    eligible = _eligible_for_nominal_calibration(estimator_config, payload)
    interval_aligned = _interval_aligned_from_payload(payload)

    warnings = _build_warnings(
        {**payload, "estimator_config": estimator_config},
        n_simulations=n_simulations,
        eligible=eligible,
    )

    return {
        "estimator_config": estimator_config,
        "scenario": scenario_name,
        "n_simulations": int(n_simulations),
        "alpha": float(alpha),
        "coverage": _safe(payload.get("coverage")),
        "coverage_status": payload.get("coverage_status"),
        "false_positive_rate": _safe(payload.get("false_positive_rate")),
        "false_positive_rate_status": payload.get("false_positive_rate_status"),
        "power": _safe(payload.get("power")),
        "power_status": payload.get("power_status"),
        "interval_aligned": interval_aligned,
        "eligible_for_nominal_calibration": eligible,
        "point_estimand": payload.get("point_estimand"),
        "interval_estimand": payload.get("interval_estimand"),
        "interval_scale": payload.get("interval_scale"),
        "significance_estimand": payload.get("significance_estimand"),
        "scored_target_estimand": payload.get("scored_target_estimand"),
        "warnings": warnings,
    }


__all__ = [
    "NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS",
    "ineligible_reason_for_calibration",
    "interval_aligned_from_payload",
    "is_nominal_calibration_eligible_config",
    "payload_eligible_for_nominal_calibration",
    "run_nominal_calibration_check",
]
