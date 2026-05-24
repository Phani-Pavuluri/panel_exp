"""
Nominal calibration smoke checks for recovery configs with aligned intervals.

Uses ``RecoveryRunner`` outputs; does not change estimators or inference.
CI smoke (small ``n_simulations``) is not production calibration — use n >= 100
for stable nominal checks (see ``MIN_REPLICATIONS_FOR_STABLE_CALIBRATION``).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from panel_exp.validation.calibration_report import (
    MIN_REPLICATIONS_FOR_STABLE_CALIBRATION,
    CalibrationReport,
    compute_calibration_warnings,
)
from panel_exp.validation.did_interval_policy import (
    DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED,
    nominal_calibration_ineligible_reason,
)
from panel_exp.validation.recovery_intervals import INTERVAL_ESTIMAND_RELATIVE_ATT_POST
from panel_exp.validation.synthetic_scenarios import SyntheticScenario

NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS = frozenset({"SCM_UnitJackKnife"})

# Removed from eligibility after Run 001 (see docs/CALIBRATION_FAILURE_ANALYSIS_001.md).
BRB_BOUNDS_INVERTED_RUN001 = "brb_bounds_inverted_run001"
KFOLD_MULTI_TREATED_UNSUPPORTED_RUN001 = "kfold_multi_treated_unsupported_run001"

NOMINAL_CALIBRATION_REMOVED_CONFIG_REASONS: Dict[str, str] = {
    "TBRRidge_BlockResidualBootstrap": BRB_BOUNDS_INVERTED_RUN001,
    "TBRRidge_Kfold": KFOLD_MULTI_TREATED_UNSUPPORTED_RUN001,
}

SCM_UNIT_JACKKNIFE_NOMINAL_CALIBRATION_NOTES: Tuple[str, ...] = (
    "SCM_UnitJackKnife passed null FPR/coverage in Run 001 but showed zero power "
    "on positive scenario.",
    "Use for null monitoring only until power behavior is characterized.",
)

_CI_SMOKE_NOTE = (
    "CI smoke is not production calibration; production calibration should use "
    f"n >= {MIN_REPLICATIONS_FOR_STABLE_CALIBRATION}."
)


def is_nominal_calibration_eligible_config(estimator_config: str) -> bool:
    """True when config is designed for path-relative aligned intervals."""
    return estimator_config in NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS


def nominal_calibration_registry_skip_reason(estimator_config: str) -> Optional[str]:
    """Explicit skip reason for configs removed from eligibility (Run 001 evidence)."""
    return NOMINAL_CALIBRATION_REMOVED_CONFIG_REASONS.get(estimator_config)


def scm_unit_jackknife_calibration_notes() -> Tuple[str, ...]:
    """Advisory notes for SCM unit jackknife nominal calibration (Run 001)."""
    return SCM_UNIT_JACKKNIFE_NOMINAL_CALIBRATION_NOTES


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
    removed = nominal_calibration_registry_skip_reason(estimator_config)
    if removed:
        return removed
    if payload_eligible_for_nominal_calibration(estimator_config, payload):
        return "eligible"
    return nominal_calibration_ineligible_reason(estimator_config, payload)


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
        config = str(payload.get("estimator_config") or payload.get("recovery_config") or "")
        removed = nominal_calibration_registry_skip_reason(config)
        if removed:
            warnings.append(
                f"Config {config!r} is not eligible for nominal calibration "
                f"(skip_reason={removed!r})."
            )
        interval_est = payload.get("interval_estimand", "unknown")
        if not removed and not is_nominal_calibration_eligible_config(config):
            warnings.append(
                f"Config {config!r} is not eligible for nominal calibration "
                "(point-estimate or mismatched interval estimand)."
            )
        elif interval_est != INTERVAL_ESTIMAND_RELATIVE_ATT_POST:
            warnings.append(
                f"Interval estimand {interval_est!r} is not aligned with scored "
                f"{INTERVAL_ESTIMAND_RELATIVE_ATT_POST!r}; nominal calibration skipped "
                f"({DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED} for DID)."
            )
        else:
            reason = payload.get("coverage_unavailable_reason") or "unknown"
            warnings.append(f"Intervals not available for calibration: {reason}.")
        return warnings

    config = str(payload.get("estimator_config") or payload.get("recovery_config") or "")
    if config == "SCM_UnitJackKnife":
        warnings.extend(SCM_UNIT_JACKKNIFE_NOMINAL_CALIBRATION_NOTES)

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


def _skipped_calibration_check_response(
    estimator_config: str,
    scenario_name: str,
    *,
    skip_reason: str,
    n_simulations: int,
    alpha: float,
) -> Dict[str, Any]:
    """Nominal calibration payload when config is registry-removed (no recovery run)."""
    warnings = [
        f"Config {estimator_config!r} is not eligible for nominal calibration "
        f"(skip_reason={skip_reason!r}).",
    ]
    return {
        "estimator_config": estimator_config,
        "scenario": scenario_name,
        "n_simulations": int(n_simulations),
        "alpha": float(alpha),
        "coverage": float("nan"),
        "coverage_status": "unavailable",
        "false_positive_rate": float("nan"),
        "false_positive_rate_status": "unavailable",
        "power": float("nan"),
        "power_status": "unavailable",
        "interval_aligned": False,
        "eligible_for_nominal_calibration": False,
        "ineligible_reason": skip_reason,
        "skip_reason": skip_reason,
        "point_estimand": None,
        "interval_estimand": "unavailable",
        "interval_scale": "unavailable",
        "significance_estimand": None,
        "scored_target_estimand": None,
        "warnings": warnings,
        "skipped": True,
    }


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

    scenario_name = (
        scenario.name if isinstance(scenario, SyntheticScenario) else str(scenario)
    )
    registry_skip = nominal_calibration_registry_skip_reason(estimator_config)
    if registry_skip:
        return _skipped_calibration_check_response(
            estimator_config,
            scenario_name,
            skip_reason=registry_skip,
            n_simulations=n_simulations,
            alpha=alpha,
        )

    runner = RecoveryRunner(
        estimator_config,
        scenario,
        n_simulations=n_simulations,
        random_state=random_state,
        alpha=alpha,
    )
    payload = runner.run()
    scenario_name = payload.get("scenario", scenario_name)

    eligible = _eligible_for_nominal_calibration(estimator_config, payload)
    interval_aligned = _interval_aligned_from_payload(payload)
    ineligible_reason = ineligible_reason_for_calibration(estimator_config, payload)

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
        "ineligible_reason": ineligible_reason,
        "skip_reason": None if eligible else ineligible_reason,
        "point_estimand": payload.get("point_estimand"),
        "interval_estimand": payload.get("interval_estimand"),
        "interval_scale": payload.get("interval_scale"),
        "significance_estimand": payload.get("significance_estimand"),
        "scored_target_estimand": payload.get("scored_target_estimand"),
        "warnings": warnings,
    }


__all__ = [
    "BRB_BOUNDS_INVERTED_RUN001",
    "KFOLD_MULTI_TREATED_UNSUPPORTED_RUN001",
    "NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS",
    "NOMINAL_CALIBRATION_REMOVED_CONFIG_REASONS",
    "SCM_UNIT_JACKKNIFE_NOMINAL_CALIBRATION_NOTES",
    "ineligible_reason_for_calibration",
    "nominal_calibration_registry_skip_reason",
    "scm_unit_jackknife_calibration_notes",
    "interval_aligned_from_payload",
    "is_nominal_calibration_eligible_config",
    "payload_eligible_for_nominal_calibration",
    "run_nominal_calibration_check",
    "DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED",
]
