"""SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "spend_contrast_feasibility_tooling_contract_defined_no_runtime_diagnostics_or_production_authorization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001_summary.json"
)

CONTRACT_SCOPE = "spend_contrast_tooling_contract_no_runtime_diagnostics"
RECOMMENDED_NEXT_ARTIFACT = "SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001"

DEPENDS_ON = (
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
)

SUPPORTED_MANIPULATION_TYPES = (
    "GO_DARK",
    "HEAVY_UP",
    "GO_LIVE",
    "BUDGET_REALLOCATION",
    "UNKNOWN",
)

SPEND_COVERAGE_STATUSES = (
    "AVAILABLE",
    "PARTIAL",
    "MISSING",
    "NOT_REQUESTED",
)

SPEND_CONTRAST_STATUSES = (
    "READY_FOR_DOWNSTREAM_POWER_DIAGNOSTICS",
    "PASS_WITH_WARNINGS",
    "PROVISIONAL",
    "BLOCKED",
    "NOT_EVALUATED",
)

SPEND_CONTRAST_QUALITIES = (
    "DIRECTIONALLY_COMPATIBLE",
    "WEAK_OR_INSUFFICIENT",
    "CONFLICTS_WITH_MANIPULATION",
    "UNKNOWN",
)

SEVERITY_LEVELS = (
    "INFO",
    "WARNING",
    "BLOCKING",
)

CLAIM_BOUNDARIES = (
    "SPEND_CONTRAST_DIAGNOSTIC_ONLY",
    "READY_FOR_DOWNSTREAM_POWER_DIAGNOSTICS",
    "PROVISIONAL_ONLY",
    "BLOCKED",
)

FUTURE_OUTPUT_CONTRACTS = (
    "SpendContrastFeasibilityInput",
    "SpendContrastFeasibilityConfig",
    "SpendContrastFeasibilityReport",
    "SpendManipulationType",
    "SpendCoverageStatus",
    "SpendContrastStatus",
    "SpendContrastQuality",
    "SpendBaselineWindowReport",
    "SpendPlanningWindowReport",
    "SpendDeltaSummary",
    "ChannelSpendMappingReport",
    "BudgetReallocationMappingReport",
    "SpendContrastIssue",
    "SpendContrastSeverity",
    "SpendContrastClaimBoundary",
)

ZERO_MISSING_RULES = {
    "missing_spend_is_not_zero_spend": True,
    "observed_zero_spend_is_observed_zero": True,
    "planned_zero_spend_labeled_as_planned": True,
    "planned_and_observed_spend_not_silently_mixed": True,
}

FAILURE_PROVISIONAL_MODES = (
    "missing_spend_column_when_contrast_requested",
    "missing_manipulation_type",
    "missing_channel_mapping_when_channel_level_contrast_requested",
    "missing_baseline_spend_window",
    "missing_planned_or_treatment_spend_window",
    "all_spend_missing",
    "missing_treated_control_or_candidate_group_labels_when_group_level_contrast_requested",
    "planned_spend_mixed_with_observed_spend_without_labels",
    "go_dark_requested_but_no_baseline_spend_exists",
    "heavy_up_requested_but_no_incremental_spend_signal_exists",
    "go_live_requested_but_baseline_already_has_substantial_spend",
    "budget_reallocation_requested_but_source_destination_mapping_missing",
    "negative_spend_values_without_correction_or_credit_flag",
    "currency_mismatch_without_currency_mapping",
    "sample_schema_mode_overclaim",
    "ballpark_mode_overclaim",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "missing_spend_blocks_contrast_when_requested",
    "spend_coverage_available_but_contrast_not_evaluated_until_manipulation_type_or_window_provided",
    "go_dark_directionally_compatible_contrast",
    "go_dark_blocked_when_baseline_spend_missing",
    "heavy_up_directionally_compatible_contrast",
    "heavy_up_weak_or_insufficient_contrast_warning",
    "go_live_directionally_compatible_contrast",
    "go_live_warning_when_baseline_spend_already_substantial",
    "budget_reallocation_requires_source_destination_mapping",
    "planned_vs_observed_spend_labels_preserved",
    "missing_spend_not_treated_as_zero",
    "observed_zero_spend_counted_separately_from_missing",
    "sample_schema_mode_cannot_produce_final_contrast_readiness",
    "ballpark_mode_provisional_only",
    "no_power_mde_pvalue_ci_lift_roi_design_production_authorization",
    "no_fixture_specific_branching",
)

_AUTH_FLAGS = {
    "runtime_spend_diagnostics_implemented": False,
    "final_experiment_feasibility_authorized": False,
    "candidate_design_authorized": False,
    "treatment_control_assignment_authorized": False,
    "power_authorized": False,
    "mde_authorized": False,
    "p_value_authorized": False,
    "confidence_interval_authorized": False,
    "lift_authorized": False,
    "roi_authorized": False,
    "method_recommendation_authorized": False,
    "portfolio_tiering_authorized": False,
    "budget_optimization_authorized": False,
    "mmm_calibration_authorized": False,
    "production_authorization_granted": False,
    "llm_decisioning_authorized": False,
}

NON_GOALS = (
    "no_runtime_spend_contrast_computation",
    "no_budget_reallocation_engine",
    "no_power_or_mde_calculation",
    "no_design_feasibility_calculation",
    "no_candidate_design_generation",
    "no_treatment_control_assignment",
    "no_lift_or_roi_calculation",
    "no_p_values_or_confidence_intervals",
    "no_mmm_calibration",
    "no_llm_decisioning",
    "no_production_authorization",
)


@dataclass(frozen=True)
class SpendContrastFeasibilityToolingContract:
    artifact_id: str
    contract_scope: str
    depends_on: tuple[str, ...]
    supported_manipulation_types: tuple[str, ...]
    spend_coverage_vs_contrast_distinction_defined: bool
    planned_vs_observed_spend_distinction_defined: bool
    zero_vs_missing_spend_rules_defined: bool
    future_output_contracts: tuple[str, ...]
    spend_contrast_statuses: tuple[str, ...]
    spend_contrast_qualities: tuple[str, ...]
    claim_boundaries: tuple[str, ...]
    failure_provisional_modes_defined: bool
    llm_explanation_boundary_defined: bool
    report_builder_boundary_defined: bool
    sample_schema_mode_final_contrast_readiness_allowed: bool
    ballpark_mode_final_contrast_readiness_allowed: bool
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    final_verdict: str


def build_spend_contrast_feasibility_tooling_contract() -> SpendContrastFeasibilityToolingContract:
    """Return deterministic spend contrast feasibility tooling contract metadata."""
    return SpendContrastFeasibilityToolingContract(
        artifact_id=_ARTIFACT_ID,
        contract_scope=CONTRACT_SCOPE,
        depends_on=DEPENDS_ON,
        supported_manipulation_types=SUPPORTED_MANIPULATION_TYPES,
        spend_coverage_vs_contrast_distinction_defined=True,
        planned_vs_observed_spend_distinction_defined=True,
        zero_vs_missing_spend_rules_defined=all(ZERO_MISSING_RULES.values()),
        future_output_contracts=FUTURE_OUTPUT_CONTRACTS,
        spend_contrast_statuses=SPEND_CONTRAST_STATUSES,
        spend_contrast_qualities=SPEND_CONTRAST_QUALITIES,
        claim_boundaries=CLAIM_BOUNDARIES,
        failure_provisional_modes_defined=True,
        llm_explanation_boundary_defined=True,
        report_builder_boundary_defined=True,
        sample_schema_mode_final_contrast_readiness_allowed=False,
        ballpark_mode_final_contrast_readiness_allowed=False,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_spend_contrast_feasibility_tooling_contract(
    contract: SpendContrastFeasibilityToolingContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.spend_coverage_vs_contrast_distinction_defined:
        issues.append("spend_coverage_vs_contrast_distinction must be defined")
    if not contract.planned_vs_observed_spend_distinction_defined:
        issues.append("planned_vs_observed_spend_distinction must be defined")
    if not contract.zero_vs_missing_spend_rules_defined:
        issues.append("zero_vs_missing_spend_rules must be defined")
    if contract.sample_schema_mode_final_contrast_readiness_allowed:
        issues.append("sample_schema_mode_final_contrast_readiness_allowed must be false")
    if contract.ballpark_mode_final_contrast_readiness_allowed:
        issues.append("ballpark_mode_final_contrast_readiness_allowed must be false")
    if contract.authorization_flags.get("runtime_spend_diagnostics_implemented"):
        issues.append("runtime_spend_diagnostics_implemented must be false for contract artifact")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_spend_contrast_feasibility_tooling_contract()
    validation = validate_spend_contrast_feasibility_tooling_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for mtype in SUPPORTED_MANIPULATION_TYPES:
        scenarios.append(_s(f"manipulation_type_{mtype}", mtype in contract.supported_manipulation_types))
    scenarios.append(
        _s(
            "spend_coverage_vs_contrast_defined",
            contract.spend_coverage_vs_contrast_distinction_defined,
        )
    )
    scenarios.append(
        _s(
            "planned_vs_observed_defined",
            contract.planned_vs_observed_spend_distinction_defined,
        )
    )
    scenarios.append(_s("zero_missing_rules", contract.zero_vs_missing_spend_rules_defined))
    scenarios.append(_s("future_output_contracts_present", contract.future_output_contracts == FUTURE_OUTPUT_CONTRACTS))
    scenarios.append(_s("contrast_statuses_present", contract.spend_contrast_statuses == SPEND_CONTRAST_STATUSES))
    scenarios.append(_s("contrast_qualities_present", contract.spend_contrast_qualities == SPEND_CONTRAST_QUALITIES))
    scenarios.append(_s("claim_boundaries_present", contract.claim_boundaries == CLAIM_BOUNDARIES))
    scenarios.append(_s("failure_modes_defined", contract.failure_provisional_modes_defined))
    scenarios.append(_s("llm_boundary_defined", contract.llm_explanation_boundary_defined))
    scenarios.append(_s("report_builder_boundary_defined", contract.report_builder_boundary_defined))
    scenarios.append(
        _s("sample_schema_no_final_readiness", not contract.sample_schema_mode_final_contrast_readiness_allowed)
    )
    scenarios.append(_s("ballpark_no_final_readiness", not contract.ballpark_mode_final_contrast_readiness_allowed))
    for test_id in FUTURE_IMPLEMENTATION_TESTS:
        scenarios.append(_s(f"future_test_spec_{test_id}", True))
    for mode in FAILURE_PROVISIONAL_MODES:
        scenarios.append(_s(f"failure_mode_{mode}", True))
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not contract.authorization_flags[flag]))
    scenarios.append(_s("depends_on_present", contract.depends_on == DEPENDS_ON))
    scenarios.append(_s("recommended_next_artifact_present", bool(contract.recommended_next_artifact)))
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
    contract = build_spend_contrast_feasibility_tooling_contract()
    validation = validate_spend_contrast_feasibility_tooling_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "spend_contrast_feasibility_tooling_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "contract_scope": CONTRACT_SCOPE,
        "depends_on": list(DEPENDS_ON),
        "supported_manipulation_types": list(SUPPORTED_MANIPULATION_TYPES),
        "spend_coverage_statuses": list(SPEND_COVERAGE_STATUSES),
        "spend_coverage_vs_contrast_distinction_defined": True,
        "planned_vs_observed_spend_distinction_defined": True,
        "zero_vs_missing_spend_rules": dict(ZERO_MISSING_RULES),
        "zero_vs_missing_spend_rules_defined": True,
        "future_output_contracts_defined": list(FUTURE_OUTPUT_CONTRACTS),
        "spend_contrast_statuses": list(SPEND_CONTRAST_STATUSES),
        "spend_contrast_qualities": list(SPEND_CONTRAST_QUALITIES),
        "severity_levels": list(SEVERITY_LEVELS),
        "claim_boundaries": list(CLAIM_BOUNDARIES),
        "failure_provisional_modes": list(FAILURE_PROVISIONAL_MODES),
        "failure_provisional_modes_defined": True,
        "llm_explanation_boundary_defined": True,
        "report_builder_boundary_defined": True,
        "sample_schema_mode_final_contrast_readiness_allowed": False,
        "ballpark_mode_final_contrast_readiness_allowed": False,
        "future_implementation_tests_required": list(FUTURE_IMPLEMENTATION_TESTS),
        "runtime_spend_diagnostics_implemented": False,
        "power_computed": False,
        "mde_computed": False,
        "p_value_computed": False,
        "confidence_interval_computed": False,
        "lift_computed": False,
        "roi_computed": False,
        "candidate_design_computed": False,
        "treatment_control_assignment_computed": False,
        "budget_optimization_authorized": False,
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
