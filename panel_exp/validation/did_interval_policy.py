"""
DID interval estimand policy — explicit support matrix for results and recovery.

Recovery scores a path-based ``relative_att_post`` point estimate for DID, but
bootstrap and ``treatment_ci`` intervals are on absolute / cumulative ATT scale.
No scaling converts cumulative intervals to relative ATT for calibration.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping

POINT_ESTIMAND = "relative_att_post"
INTERVAL_ESTIMAND_CUMULATIVE_ATT = "cumulative_att"
INTERVAL_ESTIMAND_RELATIVE_ATT_POST = "relative_att_post"

# Recovery / nominal calibration skip reason for DID interval configs.
DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED = "did_relative_att_interval_unsupported"

DID_INTERVAL_POLICY_REASON = (
    "DID bootstrap/treatment intervals are on absolute or cumulative scale, "
    "not relative_att_post."
)

DID_INTERVAL_POLICY: Dict[str, Any] = {
    "point_estimand": POINT_ESTIMAND,
    "interval_estimand": INTERVAL_ESTIMAND_CUMULATIVE_ATT,
    "relative_att_interval_supported": False,
    "reason": DID_INTERVAL_POLICY_REASON,
    "recovery_scored_point_estimand": POINT_ESTIMAND,
    "recovery_interval_estimand": INTERVAL_ESTIMAND_CUMULATIVE_ATT,
    "treatment_effect_scale": "absolute_level_twfe_coefficient",
    "treatment_ci_scale": "cumulative_absolute_att",
    "path_y_scale": "aggregated_outcome_level",
    "path_y_hat_scale": "synthetic_control_counterfactual_level",
    "path_y_lower_y_upper_scale": "outcome_level_from_cumulative_ci",
    "comparable_to_relative_att_post": {
        "recovery_point_via_path_y_y_hat": True,
        "treatment_ci": False,
        "cumulative_ci": False,
        "mean_post_period_att_interval": False,
        "path_y_lower_y_upper_for_relative_coverage": False,
    },
}


def build_did_interval_policy() -> Dict[str, Any]:
    """Return a copy of the DID interval policy for attaching to results."""
    return dict(DID_INTERVAL_POLICY)


def is_did_recovery_config(estimator_config: str) -> bool:
    """True for recovery config keys that run ``DID`` with inference."""
    return str(estimator_config).upper().startswith("DID")


def did_interval_unavailable_reason(
    *,
    estimator_config: str | None = None,
    interval_estimand: str | None = None,
) -> str:
    """
    Standard recovery unavailable reason for DID relative-interval calibration.

    Prefer ``did_relative_att_interval_unsupported`` for DID configs; fall back to
    ``interval_estimand_mismatch`` when only estimand metadata is known.
    """
    if estimator_config is not None and is_did_recovery_config(estimator_config):
        return DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED
    if interval_estimand == INTERVAL_ESTIMAND_CUMULATIVE_ATT:
        return DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED
    return "interval_estimand_mismatch"


def nominal_calibration_ineligible_reason(
    estimator_config: str,
    payload: Mapping[str, Any],
) -> str:
    """Skip reason for nominal calibration (DID-aware)."""
    from panel_exp.validation.nominal_calibration import (
        nominal_calibration_registry_skip_reason,
    )

    removed = nominal_calibration_registry_skip_reason(estimator_config)
    if removed:
        return removed
    if is_did_recovery_config(estimator_config):
        return DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED
    interval_est = str(payload.get("interval_estimand", "unknown"))
    if interval_est not in (
        "unknown",
        "unavailable",
        INTERVAL_ESTIMAND_RELATIVE_ATT_POST,
    ):
        return "interval_estimand_mismatch"
    from panel_exp.validation.nominal_calibration import (
        is_nominal_calibration_eligible_config,
    )

    if not is_nominal_calibration_eligible_config(estimator_config):
        return "not_in_nominal_calibration_registry"
    if not payload.get("intervals_expected"):
        return "intervals_not_expected"
    reason = payload.get("coverage_unavailable_reason") or ""
    if DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED in reason:
        return DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED
    if "interval_estimand_mismatch" in reason:
        return "interval_estimand_mismatch"
    return "interval_not_aligned"


__all__ = [
    "DID_INTERVAL_POLICY",
    "DID_INTERVAL_POLICY_REASON",
    "DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED",
    "build_did_interval_policy",
    "did_interval_unavailable_reason",
    "is_did_recovery_config",
    "nominal_calibration_ineligible_reason",
]
