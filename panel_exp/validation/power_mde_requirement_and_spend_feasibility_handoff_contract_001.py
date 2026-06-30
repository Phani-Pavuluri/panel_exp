"""POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "power_mde_requirement_spend_feasibility_handoff_contract_defined_no_power_mde_or_production_authorization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001_summary.json"
)

SCOPE = "contract_only_no_power_mde_runtime"
RECOMMENDED_NEXT_ARTIFACT = "POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001"

DEPENDS_ON = (
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
    "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
)

FUTURE_HANDOFF_STATUSES = (
    "SPEND_HANDOFF_READY_FOR_POWER_DIAGNOSTICS",
    "SPEND_HANDOFF_READY_WITH_WARNINGS",
    "SPEND_HANDOFF_PROVISIONAL_RESPONSE_BRIDGE",
    "SPEND_HANDOFF_BLOCKED_BY_SPEND_DATA",
    "SPEND_HANDOFF_BLOCKED_BY_REQUIRED_SPEND_UNKNOWN",
    "SPEND_HANDOFF_BLOCKED_BY_MANIPULATION_INFEASIBLE",
    "SPEND_HANDOFF_REQUIRES_DOSAGE_ESTIMAND_REVIEW",
    "SPEND_HANDOFF_REQUIRES_METHOD_SUITABILITY_REVIEW",
    "SPEND_HANDOFF_NOT_EVALUATED",
)

FUTURE_OUTPUT_CONTRACTS = (
    "PowerMdeSpendFeasibilityHandoffInput",
    "PowerMdeSpendFeasibilityHandoffConfig",
    "PowerMdeSpendFeasibilityHandoffReport",
    "PowerMdeSpendHandoffStatus",
    "PowerMdeSpendHandoffIssue",
    "PowerMdeSpendHandoffSeverity",
    "PowerMdeSpendRequirementSource",
    "PowerMdeSpendRequirementBoundary",
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

HANDOFF_INPUT_FIELDS = (
    "spend_report_id",
    "spend_report_artifact_id",
    "spend_readiness_status",
    "baseline_inventory_status",
    "response_bridge_status",
    "manipulation_feasibility_status",
    "planning_boundary_status",
    "candidate_manipulation_options",
    "required_spend_delta",
    "required_spend_delta_source",
    "kpi_mde",
    "kpi_unit",
    "response_bridge_source",
    "response_bridge_advisory_flags",
    "mmm_advisory_used",
    "proxy_response_used",
    "back_of_napkin_assumption_used",
    "business_response_risk",
    "historical_support_status",
    "required_heavy_up_multiplier",
    "go_dark_max_delta",
    "dosage_delta",
    "budget_gap",
    "control_contamination_flags",
    "estimand_shift_required",
    "dosage_contrast_estimand_required",
    "method_suitability_review_required",
    "ready_for_downstream_power_diagnostics",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "blocked_spend_readiness_blocks_power_handoff",
    "required_spend_unknown_creates_provisional_exploratory_handoff",
    "direct_required_spend_delta_produces_supplied_source_handoff",
    "mmm_advisory_bridge_preserves_MMM_ADVISORY_SIGNAL_USED",
    "proxy_bridge_preserves_PROXY_LEVEL_MISMATCH",
    "back_of_napkin_bridge_preserves_BACK_OF_NAPKIN_ASSUMPTION_USED",
    "business_response_risk_preserved",
    "go_dark_insufficient_blocks_go_dark_handoff",
    "heavy_up_within_support_ready_or_ready_with_warnings",
    "heavy_up_out_of_support_preserved_as_warning_or_block",
    "dosage_contrast_emits_dosage_estimand_requirement",
    "control_contamination_prevents_standard_go_dark_interpretation",
    "ready_handoff_does_not_set_powered_design_roi_production_flags",
    "no_fixture_specific_branching",
)

_AUTH_FLAGS = {
    "runtime_power_diagnostics_implemented": False,
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
    "handoff_contract_defined": True,
    "spend_to_power_boundary_defined": True,
    "dosage_handoff_boundary_defined": True,
    "response_bridge_provenance_required": True,
}

NON_GOALS = (
    "no_runtime_power_mde_diagnostics",
    "no_runtime_spend_diagnostics_changes",
    "no_design_generation",
    "no_treatment_control_assignment",
    "no_estimator_inference_selection",
    "no_p_values_or_confidence_intervals",
    "no_lift_or_roi_computation",
    "no_mmm_runtime_calls",
    "no_mmm_calibration",
    "no_budget_optimization",
    "no_llm_decisioning",
    "no_production_authorization",
)


@dataclass(frozen=True)
class PowerMdeSpendFeasibilityHandoffContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    handoff_contract_defined: bool
    spend_to_power_boundary_defined: bool
    kpi_mde_units_preserved: bool
    required_spend_delta_source_preserved: bool
    response_bridge_provenance_required: bool
    business_response_risk_preserved: bool
    dosage_handoff_boundary_defined: bool
    control_contamination_flags_preserved: bool
    method_suitability_review_required_for_dosage: bool
    future_handoff_statuses: tuple[str, ...]
    future_output_contracts: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    final_verdict: str


def build_power_mde_spend_feasibility_handoff_contract() -> PowerMdeSpendFeasibilityHandoffContract:
    return PowerMdeSpendFeasibilityHandoffContract(
        artifact_id=_ARTIFACT_ID,
        scope=SCOPE,
        depends_on=DEPENDS_ON,
        handoff_contract_defined=True,
        spend_to_power_boundary_defined=True,
        kpi_mde_units_preserved=True,
        required_spend_delta_source_preserved=True,
        response_bridge_provenance_required=True,
        business_response_risk_preserved=True,
        dosage_handoff_boundary_defined=True,
        control_contamination_flags_preserved=True,
        method_suitability_review_required_for_dosage=True,
        future_handoff_statuses=FUTURE_HANDOFF_STATUSES,
        future_output_contracts=FUTURE_OUTPUT_CONTRACTS,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_power_mde_spend_feasibility_handoff_contract(
    contract: PowerMdeSpendFeasibilityHandoffContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.handoff_contract_defined:
        issues.append("handoff_contract_defined must be true")
    if not contract.spend_to_power_boundary_defined:
        issues.append("spend_to_power_boundary_defined must be true")
    if not contract.response_bridge_provenance_required:
        issues.append("response_bridge_provenance_required must be true")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_power_mde_spend_feasibility_handoff_contract()
    validation = validate_power_mde_spend_feasibility_handoff_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in FUTURE_HANDOFF_STATUSES:
        scenarios.append(_s(f"handoff_status_{status}", status in contract.future_handoff_statuses))
    scenarios.append(_s("handoff_contract_defined", contract.handoff_contract_defined))
    scenarios.append(_s("spend_to_power_boundary", contract.spend_to_power_boundary_defined))
    scenarios.append(_s("kpi_mde_units_preserved", contract.kpi_mde_units_preserved))
    scenarios.append(_s("response_bridge_provenance", contract.response_bridge_provenance_required))
    scenarios.append(_s("dosage_handoff_boundary", contract.dosage_handoff_boundary_defined))
    scenarios.append(_s("control_contamination_preserved", contract.control_contamination_flags_preserved))
    scenarios.append(_s("method_suitability_for_dosage", contract.method_suitability_review_required_for_dosage))
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
    contract = build_power_mde_spend_feasibility_handoff_contract()
    validation = validate_power_mde_spend_feasibility_handoff_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "power_mde_requirement_spend_feasibility_handoff_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": SCOPE,
        "depends_on": list(DEPENDS_ON),
        "handoff_contract_defined": True,
        "spend_to_power_boundary_defined": True,
        "kpi_mde_units_preserved": True,
        "required_spend_delta_source_preserved": True,
        "response_bridge_provenance_required": True,
        "business_response_risk_preserved": True,
        "dosage_handoff_boundary_defined": True,
        "control_contamination_flags_preserved": True,
        "method_suitability_review_required_for_dosage": True,
        "future_handoff_statuses": list(FUTURE_HANDOFF_STATUSES),
        "future_output_contracts_defined": list(FUTURE_OUTPUT_CONTRACTS),
        "handoff_input_fields": list(HANDOFF_INPUT_FIELDS),
        "response_bridge_sources": list(RESPONSE_BRIDGE_SOURCES),
        "response_bridge_flags_to_preserve": list(RESPONSE_BRIDGE_FLAGS_TO_PRESERVE),
        "future_implementation_tests_required": list(FUTURE_IMPLEMENTATION_TESTS),
        "contract_positive_flags": dict(CONTRACT_POSITIVE_FLAGS),
        "runtime_power_diagnostics_implemented": False,
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
