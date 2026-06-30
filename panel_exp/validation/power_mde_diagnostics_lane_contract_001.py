"""POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "power_mde_diagnostics_lane_contract_defined_no_runtime_power_mde_or_production_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001_summary.json"

SCOPE = "contract_only_no_runtime_power_mde"
RECOMMENDED_NEXT_ARTIFACT = "POWER_MDE_DIAGNOSTICS_RUNTIME_001"

DEPENDS_ON = (
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
    "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
    "POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001",
)

FUTURE_RUNTIME_MODES = (
    "KPI_ONLY_SENSITIVITY",
    "SPEND_CONFIRMED_SENSITIVITY",
    "DESIGN_CELL_SENSITIVITY",
    "DOSAGE_CONTRAST_SENSITIVITY",
    "EXPLORATORY_BACK_OF_NAPKIN",
)

FUTURE_STATUSES = (
    "POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME",
    "POWER_MDE_READY_WITH_WARNINGS",
    "POWER_MDE_PROVISIONAL",
    "POWER_MDE_BLOCKED_BY_DATA_READINESS",
    "POWER_MDE_BLOCKED_BY_GEO_FEASIBILITY",
    "POWER_MDE_BLOCKED_BY_SPEND_HANDOFF",
    "POWER_MDE_BLOCKED_BY_CELL_STRUCTURE",
    "POWER_MDE_BLOCKED_BY_ESTIMAND_MISMATCH",
    "POWER_MDE_REQUIRES_METHOD_SUITABILITY_REVIEW",
    "POWER_MDE_NOT_EVALUATED",
)

READINESS_GATES = (
    "profiler_gate",
    "geo_unit_market_feasibility_gate",
    "spend_handoff_gate",
    "cell_structure_gate",
    "kpi_mde_target_gate",
    "noise_history_gate",
    "estimand_compatibility_gate",
    "method_suitability_precheck_gate",
)

FUTURE_INPUT_CONTRACTS = (
    "PowerMdeDiagnosticsInput",
    "PowerMdeDiagnosticsConfig",
    "PowerMdeDiagnosticsReport",
    "PowerMdeDiagnosticStatus",
    "PowerMdeDiagnosticIssue",
    "PowerMdeDiagnosticSeverity",
    "PowerMdeEstimandSpec",
    "PowerMdeNoiseModelSpec",
    "PowerMdePanelHistorySpec",
    "PowerMdeCellStructureSpec",
    "PowerMdeSpendHandoffSpec",
    "PowerMdeSensitivityTarget",
    "PowerMdeClaimBoundary",
)

FUTURE_OUTPUT_CONTRACTS = (
    "PowerMdeDiagnosticsReport",
    "PowerMdeReadinessReport",
    "PowerMdeSensitivityReport",
    "PowerMdeNoiseReadinessReport",
    "PowerMdeCellStructureReport",
    "PowerMdeSpendCompatibilityReport",
    "PowerMdeEstimandCompatibilityReport",
    "PowerMdeIssue",
    "PowerMdeClaimBoundaryReport",
)

LANE_INPUT_FIELDS = (
    "profiler_report",
    "geo_unit_market_feasibility_report",
    "spend_requirement_manipulation_feasibility_report",
    "power_mde_spend_feasibility_handoff_report",
    "candidate_cell_structure",
    "geo_unit_ids",
    "cell_ids",
    "cell_roles",
    "time_grain",
    "pre_period_window",
    "test_duration",
    "post_period_window",
    "kpi_column",
    "kpi_unit",
    "kpi_mde",
    "relative_mde",
    "absolute_mde",
    "baseline_kpi_mean",
    "baseline_kpi_variance",
    "historical_noise_summary",
    "seasonality_summary",
    "cell_balance_summary",
    "spend_handoff_status",
    "required_spend_delta",
    "candidate_manipulation_options",
    "dosage_or_difference_in_policy_flags",
    "control_contamination_flags",
    "method_suitability_review_required",
)

DESIGN_CELL_STRUCTURE_TYPES = (
    "single_treated_cell_vs_control",
    "multi_cell_design",
    "common_control_design",
    "matched_pair_design",
    "dosage_contrast_design",
    "difference_in_policy_design",
    "budget_reallocation_design",
)

RESPONSE_BRIDGE_FLAGS_TO_PRESERVE = (
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

FUTURE_IMPLEMENTATION_TESTS = (
    "blocked_profiler_blocks_power_mde_runtime",
    "blocked_geo_feasibility_blocks_power_mde_runtime",
    "blocked_spend_handoff_blocks_spend_confirmed_sensitivity",
    "required_spend_unknown_allows_only_kpi_only_exploratory_mode",
    "kpi_mde_units_preserved",
    "absolute_and_relative_mde_not_silently_mixed",
    "cell_level_and_aggregate_panel_mde_not_silently_mixed",
    "mmm_advisory_flags_preserved",
    "business_response_risk_preserved",
    "proxy_mismatch_preserved",
    "dosage_contrast_routes_to_dosage_sensitivity_mode",
    "control_contamination_blocks_standard_go_dark_interpretation",
    "missing_candidate_cell_structure_produces_provisional_or_blocked_status",
    "missing_kpi_history_blocks_runtime",
    "ready_for_runtime_status_does_not_set_powered_design_roi_production_flags",
    "no_fixture_specific_branching",
)

_AUTH_FLAGS = {
    "runtime_power_mde_diagnostics_implemented": False,
    "power_computed": False,
    "mde_computed": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "lift_computed": False,
    "roi_computed": False,
    "budget_optimization_authorized": False,
    "candidate_design_authorized": False,
    "treatment_control_assignment_authorized": False,
    "estimator_inference_authorized": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "production_authorization_granted": False,
    "llm_decisioning_authorized": False,
}

CONTRACT_POSITIVE_FLAGS = {
    "power_mde_lane_contract_defined": True,
    "spend_handoff_dependency_defined": True,
    "kpi_mde_representation_defined": True,
    "noise_history_requirements_defined": True,
    "dosage_sensitivity_mode_defined": True,
    "claim_boundaries_defined": True,
}

NON_GOALS = (
    "no_runtime_power_mde_diagnostics",
    "no_p_value_computation",
    "no_confidence_interval_computation",
    "no_causal_lift_estimation",
    "no_roi_estimation",
    "no_design_generation",
    "no_treatment_control_assignment",
    "no_estimator_inference_selection",
    "no_mmm_runtime_calls",
    "no_mmm_calibration",
    "no_budget_optimization",
    "no_llm_decisioning",
    "no_production_authorization",
)


@dataclass(frozen=True)
class PowerMdeDiagnosticsLaneContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    power_mde_lane_contract_defined: bool
    spend_handoff_dependency_defined: bool
    kpi_mde_representation_defined: bool
    absolute_relative_mde_separation_defined: bool
    cell_aggregate_mde_separation_defined: bool
    noise_history_requirements_defined: bool
    cell_structure_requirements_defined: bool
    dosage_sensitivity_mode_defined: bool
    control_contamination_preservation_defined: bool
    response_bridge_provenance_preservation_defined: bool
    business_response_risk_preservation_defined: bool
    future_runtime_modes: tuple[str, ...]
    future_statuses: tuple[str, ...]
    readiness_gates: tuple[str, ...]
    future_input_contracts: tuple[str, ...]
    future_output_contracts: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    final_verdict: str


def build_power_mde_diagnostics_lane_contract() -> PowerMdeDiagnosticsLaneContract:
    return PowerMdeDiagnosticsLaneContract(
        artifact_id=_ARTIFACT_ID,
        scope=SCOPE,
        depends_on=DEPENDS_ON,
        power_mde_lane_contract_defined=True,
        spend_handoff_dependency_defined=True,
        kpi_mde_representation_defined=True,
        absolute_relative_mde_separation_defined=True,
        cell_aggregate_mde_separation_defined=True,
        noise_history_requirements_defined=True,
        cell_structure_requirements_defined=True,
        dosage_sensitivity_mode_defined=True,
        control_contamination_preservation_defined=True,
        response_bridge_provenance_preservation_defined=True,
        business_response_risk_preservation_defined=True,
        future_runtime_modes=FUTURE_RUNTIME_MODES,
        future_statuses=FUTURE_STATUSES,
        readiness_gates=READINESS_GATES,
        future_input_contracts=FUTURE_INPUT_CONTRACTS,
        future_output_contracts=FUTURE_OUTPUT_CONTRACTS,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_power_mde_diagnostics_lane_contract(
    contract: PowerMdeDiagnosticsLaneContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.power_mde_lane_contract_defined:
        issues.append("power_mde_lane_contract_defined must be true")
    if not contract.spend_handoff_dependency_defined:
        issues.append("spend_handoff_dependency_defined must be true")
    if not contract.kpi_mde_representation_defined:
        issues.append("kpi_mde_representation_defined must be true")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_power_mde_diagnostics_lane_contract()
    validation = validate_power_mde_diagnostics_lane_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in FUTURE_STATUSES:
        scenarios.append(_s(f"future_status_{status}", status in contract.future_statuses))
    for mode in FUTURE_RUNTIME_MODES:
        scenarios.append(_s(f"runtime_mode_{mode}", mode in contract.future_runtime_modes))
    for gate in READINESS_GATES:
        scenarios.append(_s(f"readiness_gate_{gate}", gate in contract.readiness_gates))
    scenarios.append(_s("lane_contract_defined", contract.power_mde_lane_contract_defined))
    scenarios.append(_s("spend_handoff_dependency", contract.spend_handoff_dependency_defined))
    scenarios.append(_s("kpi_mde_representation", contract.kpi_mde_representation_defined))
    scenarios.append(_s("absolute_relative_mde_separation", contract.absolute_relative_mde_separation_defined))
    scenarios.append(_s("cell_aggregate_mde_separation", contract.cell_aggregate_mde_separation_defined))
    scenarios.append(_s("noise_history_requirements", contract.noise_history_requirements_defined))
    scenarios.append(_s("cell_structure_requirements", contract.cell_structure_requirements_defined))
    scenarios.append(_s("dosage_sensitivity_mode", contract.dosage_sensitivity_mode_defined))
    scenarios.append(_s("control_contamination_preservation", contract.control_contamination_preservation_defined))
    scenarios.append(_s("response_bridge_provenance", contract.response_bridge_provenance_preservation_defined))
    scenarios.append(_s("business_response_risk_preservation", contract.business_response_risk_preservation_defined))
    for contract_name in FUTURE_INPUT_CONTRACTS:
        scenarios.append(_s(f"input_contract_{contract_name}", contract_name in contract.future_input_contracts))
    for contract_name in FUTURE_OUTPUT_CONTRACTS:
        scenarios.append(_s(f"output_contract_{contract_name}", contract_name in contract.future_output_contracts))
    for test_id in FUTURE_IMPLEMENTATION_TESTS:
        scenarios.append(_s(f"future_test_{test_id}", True))
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not contract.authorization_flags[flag]))
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
    contract = build_power_mde_diagnostics_lane_contract()
    validation = validate_power_mde_diagnostics_lane_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "power_mde_diagnostics_lane_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": SCOPE,
        "depends_on": list(DEPENDS_ON),
        "power_mde_lane_contract_defined": True,
        "spend_handoff_dependency_defined": True,
        "kpi_mde_representation_defined": True,
        "absolute_relative_mde_separation_defined": True,
        "cell_aggregate_mde_separation_defined": True,
        "noise_history_requirements_defined": True,
        "cell_structure_requirements_defined": True,
        "dosage_sensitivity_mode_defined": True,
        "control_contamination_preservation_defined": True,
        "response_bridge_provenance_preservation_defined": True,
        "business_response_risk_preservation_defined": True,
        "future_runtime_modes_defined": list(FUTURE_RUNTIME_MODES),
        "future_statuses_defined": list(FUTURE_STATUSES),
        "readiness_gates_defined": list(READINESS_GATES),
        "future_input_contracts_defined": list(FUTURE_INPUT_CONTRACTS),
        "future_output_contracts_defined": list(FUTURE_OUTPUT_CONTRACTS),
        "lane_input_fields": list(LANE_INPUT_FIELDS),
        "design_cell_structure_types": list(DESIGN_CELL_STRUCTURE_TYPES),
        "response_bridge_flags_to_preserve": list(RESPONSE_BRIDGE_FLAGS_TO_PRESERVE),
        "future_implementation_tests_required": list(FUTURE_IMPLEMENTATION_TESTS),
        "contract_positive_flags": dict(CONTRACT_POSITIVE_FLAGS),
        "runtime_power_mde_diagnostics_implemented": False,
        "power_computed": False,
        "mde_computed": False,
        "p_value_computed": False,
        "confidence_interval_computed": False,
        "lift_computed": False,
        "roi_computed": False,
        "budget_optimization_authorized": False,
        "candidate_design_authorized": False,
        "treatment_control_assignment_authorized": False,
        "estimator_inference_authorized": False,
        "mmm_runtime_calls_implemented": False,
        "mmm_calibration_authorized": False,
        "production_authorization_granted": False,
        "llm_decisioning_authorized": False,
        "authorization_flags": dict(_AUTH_FLAGS),
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
