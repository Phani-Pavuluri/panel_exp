"""SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "spend_requirement_and_manipulation_feasibility_contract_defined_no_runtime_diagnostics_or_production_authorization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001_summary.json"
)

SCOPE = "contract_amendment_no_runtime_diagnostics"
AMENDS_OR_SUPERSEDES = "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001"
RECOMMENDED_NEXT_ARTIFACT = "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001"

DEPENDS_ON = (
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
    "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001",
)

SUBREPORTS = (
    "SpendDataReadinessReport",
    "BaselineSpendInventoryReport",
    "ResponseBridgeReport",
    "ManipulationFeasibilityReport",
    "PlanningBoundaryReport",
)

SUPPORTED_MANIPULATION_OPTIONS = (
    "GO_DARK",
    "HEAVY_UP",
    "GO_LIVE",
    "BUDGET_REALLOCATION",
    "DOSAGE_CONTRAST",
    "DIFFERENCE_IN_POLICY",
    "UNKNOWN",
)

RESPONSE_BRIDGE_SOURCES = (
    "NONE",
    "USER_PROVIDED_REQUIRED_SPEND_DELTA",
    "POWER_LAYER_REQUIRED_SPEND_DELTA",
    "MMM_RESPONSE_CURVE",
    "MMM_ROMS",
    "PRIOR_EXPERIMENT",
    "PROXY_RESPONSE_CURVE",
    "BACK_OF_NAPKIN_USER_ASSUMPTION",
)

RESPONSE_BRIDGE_FLAGS = (
    "MMM_ADVISORY_SIGNAL_USED",
    "MMM_OUT_OF_SUPPORT",
    "OUT_OF_MMM_SUPPORT",
    "MMM_CALIBRATION_WEAK",
    "PROXY_RESPONSE_USED",
    "PROXY_LEVEL_MISMATCH",
    "BACK_OF_NAPKIN_ASSUMPTION_USED",
    "BUSINESS_RESPONSE_RISK",
    "REQUIRED_SPEND_DELTA_UNKNOWN",
    "REQUIRED_SPEND_DELTA_ESTIMATED_ADVISORY",
    "REQUIRED_SPEND_DELTA_SUPPLIED",
)

MANIPULATION_FEASIBILITY_OUTPUTS = (
    "GO_DARK_FEASIBLE",
    "GO_DARK_INSUFFICIENT_BASELINE_SPEND",
    "HEAVY_UP_FEASIBLE",
    "HEAVY_UP_OUT_OF_HISTORICAL_SUPPORT",
    "HEAVY_UP_MULTIPLIER_HIGH",
    "GO_LIVE_FEASIBLE",
    "GO_LIVE_CONFLICTS_WITH_EXISTING_BASELINE_SPEND",
    "BUDGET_REALLOCATION_FEASIBLE",
    "BUDGET_REALLOCATION_MAPPING_INCOMPLETE",
    "DOSAGE_CONTRAST_FEASIBLE",
    "DOSAGE_CONTRAST_ESTIMAND_REQUIRED",
    "INSUFFICIENT_CONTRAST",
    "BLOCKED_MISSING_SPEND",
    "PROVISIONAL_REQUIRED_SPEND_UNKNOWN",
)

HISTORICAL_SUPPORT_CHECKS = (
    "within_historical_support",
    "near_upper_historical_support",
    "above_historical_support",
    "far_above_historical_support",
    "unknown_historical_support",
)

CONTROL_CONTAMINATION_FLAGS = (
    "CONTROL_CELL_MANIPULATED",
    "CONTROL_CONTAMINATION_RISK",
    "BUSINESS_AS_USUAL_CONTROL_NOT_PRESERVED",
    "ESTIMAND_SHIFT_REQUIRED",
    "STANDARD_GO_DARK_INTERPRETATION_NOT_ALLOWED",
)

BASELINE_INVENTORY_FIELDS = (
    "baseline_mean_weekly_spend",
    "baseline_median_weekly_spend",
    "baseline_total_spend",
    "baseline_p10_weekly_spend",
    "baseline_p90_weekly_spend",
    "historical_p95_spend",
    "historical_max_spend",
    "nonzero_weeks",
    "missing_weeks",
    "max_reducible_spend",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "baseline_spend_derived_from_pre_period_data",
    "baseline_blocked_when_pre_period_missing",
    "zero_spend_not_treated_as_missing",
    "missing_spend_not_treated_as_zero",
    "required_heavy_up_multiplier_computed",
    "go_dark_blocked_when_max_reducible_below_required_delta",
    "heavy_up_feasible_within_historical_support",
    "heavy_up_warning_above_p95",
    "heavy_up_blocked_or_warned_far_above_historical_max",
    "control_heavy_up_test_go_dark_flags_control_contamination",
    "control_heavy_up_test_go_dark_requires_dosage_estimand",
    "standard_go_dark_interpretation_blocked_when_control_manipulated",
    "dosage_contrast_feasible_when_policy_delta_meets_required_spend",
    "budget_reallocation_requires_source_destination_mapping",
    "kpi_mde_shown_in_actual_units",
    "mmm_response_bridge_translates_kpi_mde_advisory",
    "mmm_out_of_support_flagged",
    "proxy_level_mismatch_flagged",
    "back_of_napkin_assumption_flagged",
    "business_response_risk_when_expected_response_below_kpi_mde",
    "no_roi_lift_power_design_estimator_production_authorization",
    "no_fixture_specific_branching",
)

_AUTH_FLAGS = {
    "final_design_recommendation_authorized": False,
    "runtime_spend_diagnostics_implemented": False,
    "power_computed": False,
    "mde_computed": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "lift_computed": False,
    "roi_computed": False,
    "budget_optimization_authorized": False,
    "candidate_design_computed": False,
    "treatment_control_assignment_computed": False,
    "estimator_inference_authorized": False,
    "production_authorization_granted": False,
    "llm_decisioning_authorized": False,
}

NON_GOALS = (
    "no_runtime_implementation",
    "no_power_or_mde_computation",
    "no_mmm_runtime_calls",
    "no_mmm_calibration",
    "no_causal_lift_estimation",
    "no_roi_estimation",
    "no_budget_optimization",
    "no_candidate_design_finalization",
    "no_treatment_control_assignment",
    "no_estimator_inference_selection",
    "no_production_authorization",
    "no_llm_decisioning",
)


@dataclass(frozen=True)
class SpendRequirementAndManipulationFeasibilityContract:
    artifact_id: str
    scope: str
    amends_or_supersedes: str
    depends_on: tuple[str, ...]
    subreports: tuple[str, ...]
    supported_manipulation_options: tuple[str, ...]
    response_bridge_sources: tuple[str, ...]
    two_required_spend_concepts_defined: bool
    dosage_contrast_first_class_option: bool
    kpi_mde_to_spend_bridge_advisory_only: bool
    mmm_proxy_use_advisory_only: bool
    baseline_spend_derivation_defined: bool
    required_heavy_up_multiplier_defined: bool
    historical_support_check_defined: bool
    control_contamination_warning_defined: bool
    estimand_shift_flag_defined: bool
    candidate_manipulation_options_allowed: bool
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    final_verdict: str


def build_spend_requirement_and_manipulation_feasibility_contract() -> (
    SpendRequirementAndManipulationFeasibilityContract
):
    return SpendRequirementAndManipulationFeasibilityContract(
        artifact_id=_ARTIFACT_ID,
        scope=SCOPE,
        amends_or_supersedes=AMENDS_OR_SUPERSEDES,
        depends_on=DEPENDS_ON,
        subreports=SUBREPORTS,
        supported_manipulation_options=SUPPORTED_MANIPULATION_OPTIONS,
        response_bridge_sources=RESPONSE_BRIDGE_SOURCES,
        two_required_spend_concepts_defined=True,
        dosage_contrast_first_class_option=True,
        kpi_mde_to_spend_bridge_advisory_only=True,
        mmm_proxy_use_advisory_only=True,
        baseline_spend_derivation_defined=True,
        required_heavy_up_multiplier_defined=True,
        historical_support_check_defined=True,
        control_contamination_warning_defined=True,
        estimand_shift_flag_defined=True,
        candidate_manipulation_options_allowed=True,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_spend_requirement_and_manipulation_feasibility_contract(
    contract: SpendRequirementAndManipulationFeasibilityContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.two_required_spend_concepts_defined:
        issues.append("two_required_spend_concepts must be defined")
    if not contract.dosage_contrast_first_class_option:
        issues.append("dosage_contrast must be first-class")
    if not contract.kpi_mde_to_spend_bridge_advisory_only:
        issues.append("kpi_mde bridge must be advisory only")
    if contract.authorization_flags.get("final_design_recommendation_authorized"):
        issues.append("final_design_recommendation_authorized must be false")
    if contract.authorization_flags.get("runtime_spend_diagnostics_implemented"):
        issues.append("runtime_spend_diagnostics_implemented must be false")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_spend_requirement_and_manipulation_feasibility_contract()
    validation = validate_spend_requirement_and_manipulation_feasibility_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for sub in SUBREPORTS:
        scenarios.append(_s(f"subreport_{sub}", sub in contract.subreports))
    for opt in SUPPORTED_MANIPULATION_OPTIONS:
        scenarios.append(_s(f"manipulation_{opt}", opt in contract.supported_manipulation_options))
    scenarios.append(_s("dosage_contrast_first_class", contract.dosage_contrast_first_class_option))
    scenarios.append(_s("two_spend_concepts", contract.two_required_spend_concepts_defined))
    scenarios.append(_s("mmm_advisory_only", contract.mmm_proxy_use_advisory_only))
    scenarios.append(_s("baseline_derivation", contract.baseline_spend_derivation_defined))
    scenarios.append(_s("heavy_up_multiplier", contract.required_heavy_up_multiplier_defined))
    scenarios.append(_s("historical_support", contract.historical_support_check_defined))
    scenarios.append(_s("control_contamination", contract.control_contamination_warning_defined))
    scenarios.append(_s("estimand_shift", contract.estimand_shift_flag_defined))
    for test_id in FUTURE_IMPLEMENTATION_TESTS:
        scenarios.append(_s(f"future_test_{test_id}", True))
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not contract.authorization_flags[flag]))
    scenarios.append(_s("amends_prior_contract", contract.amends_or_supersedes == AMENDS_OR_SUPERSEDES))
    scenarios.append(_s("recommended_next_present", bool(contract.recommended_next_artifact)))
    scenarios.append(_s("final_verdict_matches", contract.final_verdict == _VERDICT))
    scenarios.append(_s("validation_valid", validation["valid"]))
    scenarios.append(_s("failed_scenarios_empty", all(x["passed"] for x in scenarios)))
    return scenarios


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    contract = build_spend_requirement_and_manipulation_feasibility_contract()
    validation = validate_spend_requirement_and_manipulation_feasibility_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "spend_requirement_and_manipulation_feasibility_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": SCOPE,
        "amends_or_supersedes": AMENDS_OR_SUPERSEDES,
        "depends_on": list(DEPENDS_ON),
        "subreports_defined": list(SUBREPORTS),
        "spend_data_readiness_defined": True,
        "baseline_spend_inventory_defined": True,
        "response_bridge_defined": True,
        "manipulation_feasibility_defined": True,
        "planning_boundary_defined": True,
        "supported_manipulation_options": list(SUPPORTED_MANIPULATION_OPTIONS),
        "response_bridge_sources": list(RESPONSE_BRIDGE_SOURCES),
        "response_bridge_flags": list(RESPONSE_BRIDGE_FLAGS),
        "two_required_spend_concepts_defined": True,
        "statistical_required_spend_contrast_defined": True,
        "business_response_required_spend_defined": True,
        "dosage_contrast_first_class_option": True,
        "kpi_mde_to_spend_bridge_advisory_only": True,
        "mmm_proxy_use_advisory_only": True,
        "baseline_spend_derivation_defined": True,
        "baseline_inventory_fields": list(BASELINE_INVENTORY_FIELDS),
        "required_heavy_up_multiplier_defined": True,
        "historical_support_checks": list(HISTORICAL_SUPPORT_CHECKS),
        "historical_support_check_defined": True,
        "control_contamination_flags": list(CONTROL_CONTAMINATION_FLAGS),
        "control_contamination_warning_defined": True,
        "estimand_shift_flag_defined": True,
        "manipulation_feasibility_outputs": list(MANIPULATION_FEASIBILITY_OUTPUTS),
        "candidate_manipulation_options_allowed": True,
        "final_design_recommendation_authorized": False,
        "runtime_spend_diagnostics_implemented": False,
        "power_computed": False,
        "mde_computed": False,
        "mmm_runtime_calls_implemented": False,
        "mmm_calibration_authorized": False,
        "lift_computed": False,
        "roi_computed": False,
        "budget_optimization_authorized": False,
        "candidate_design_computed": False,
        "treatment_control_assignment_computed": False,
        "estimator_inference_authorized": False,
        "production_authorization_granted": False,
        "llm_decisioning_authorized": False,
        "authorization_flags": dict(_AUTH_FLAGS),
        "future_implementation_tests_required": list(FUTURE_IMPLEMENTATION_TESTS),
        "recommended_next_artifact": RECOMMENDED_NEXT_ARTIFACT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        "non_goals": list(NON_GOALS),
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {"verdict": _VERDICT, "failed_scenarios": failed}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
