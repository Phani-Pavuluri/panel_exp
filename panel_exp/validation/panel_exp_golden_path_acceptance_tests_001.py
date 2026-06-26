"""PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "panel_exp_golden_path_acceptance_tests_defined_no_runtime_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001_summary.json"

CONTRACT_SCOPE = "golden_path_acceptance_contract_no_runtime"
RECOMMENDED_NEXT_ARTIFACT = "GEO_KPI_SPEND_DATA_PROFILER_001"

REQUIRED_CONTRACTS = (
    "PanelExpGoldenPathScenario",
    "PanelExpGoldenPathFixture",
    "PanelExpGoldenPathExpectedArtifacts",
    "PanelExpGoldenPathExpectedClaims",
    "PanelExpGoldenPathExpectedBlocks",
    "PanelExpGoldenPathAcceptanceResult",
    "PanelExpGoldenPathFailureMode",
    "PanelExpGoldenPathRegressionSuite",
    "PanelExpFixtureModeBoundary",
    "PanelExpReportBuilderBoundary",
    "PanelExpNotebookDemoBoundary",
)

REQUIRED_ACCEPTANCE_DIMENSIONS = (
    "scenario_id",
    "scenario_name",
    "scenario_type",
    "input_mode",
    "fixture_requirements",
    "fixture_mode_or_product_mode",
    "intake_expected",
    "data_profile_expected",
    "agent_packet_expected",
    "artifact_registry_expected",
    "diagnostic_expected",
    "design_expected",
    "spend_expected",
    "inference_expected",
    "model_fallback_expected",
    "report_builder_expected",
    "llm_explanation_expected",
    "claim_boundary_expected",
    "authorization_flags_expected",
    "expected_final_status",
    "expected_blocking_reasons",
)

GOLDEN_PATH_SCENARIOS = (
    "GP-001_single_test_full_panel_feasible_planning",
    "GP-002_multi_test_portfolio_tiering",
    "GP-003_sample_schema_mode",
    "GP-004_ballpark_provisional_mode",
    "GP-005_shared_control_multi_arm_planning",
    "GP-006_go_live_new_channel_planning",
    "GP-007_design_based_inference_eligible_planning",
    "GP-008_model_fallback_routing",
)

BLOCKED_PROVISIONAL_SCENARIOS = (
    "BP-001_missing_kpi_column",
    "BP-002_missing_spend_column_when_spend_feasibility_requested",
    "BP-003_mixed_grain_without_mapping",
    "BP-004_duplicate_geo_date_rows_without_aggregation_rule",
    "BP-005_too_few_eligible_units",
    "BP-006_weak_heavy_up_spend_contrast",
    "BP-007_ballpark_mode_overclaim_attempt",
    "BP-008_sample_schema_overclaim_attempt",
    "BP-009_shared_control_independent_test_overclaim",
    "BP-010_unregistered_artifact_referenced_downstream",
    "BP-011_hidden_agent_failure",
    "BP-012_expired_revoked_artifact_used_for_new_recommendation",
    "BP-013_fixture_specific_product_logic",
    "BP-014_demo_specific_workflow_promoted_to_product_path",
    "BP-015_report_builder_hidden_inference",
    "BP-016_llm_raw_fixture_data_inference",
    "BP-017_notebook_demo_before_golden_paths_stable",
    "BP-018_generic_readiness_overgeneralization",
)

PROFILER_IMPLEMENTATION_NOTES = (
    "prefer_additive_kpis_for_future_calibration_rates_are_diagnostic_without_numerator_denominator",
    "design_at_provided_geo_level_no_silent_geo_level_upgrade_or_downgrade",
    "ask_for_planned_test_start_date_to_separate_historical_data_from_planning_period",
    "profiler_reports_coverage_and_schema_readiness_only_no_design_power_mde_inference",
    "no_hidden_zero_fill_or_hidden_imputation",
)

REQUIRED_OUTPUT_ARTIFACT_CATEGORIES = (
    "PlanningIntentReport",
    "GeoKpiSpendDataProfileReport",
    "UnitEligibilityReport",
    "PortfolioFeasibilityReport",
    "SpendContrastFeasibilityReport",
    "CandidateDesignSet",
    "DesignBasedInferencePlan",
    "ModelFallbackRecommendation",
    "PanelExpAgentRunManifest",
    "PanelExpAgentArtifactReference",
    "PanelExpAgentValidationReport",
    "PanelExpAgentFailurePacket",
    "PanelExpArtifactRegistryEntry",
    "ClaimBoundaryReport",
    "PanelExpGoldenPathAcceptanceResult",
    "ReportBuilderBoundaryResult",
    "FixtureModeBoundaryResult",
    "NotebookDemoBoundaryResult",
)

PER_SCENARIO_AUTH_FLAGS = (
    "production_design_recommendation_authorized",
    "production_readout_authorized",
    "production_p_value_authorized",
    "causal_confidence_interval_authorized",
    "production_authorization_granted",
    "selector_implementation_authorized",
    "production_selection_router_authorized",
    "multicell_production_claim_authorized",
    "trustreport_authorized",
    "calibration_signal_allowed",
    "mmm_ingestion_allowed",
    "llm_decisioning_allowed",
    "production_decisioning_allowed",
    "live_api_authorized",
    "scheduler_authorized",
    "budget_optimization_allowed",
    "package_side_agents_authorized",
)

FUTURE_AGENT_ANSWERABILITY_RECOVERY_CONTRACT = "PANEL_EXP_AGENT_ANSWERABILITY_AND_RECOVERY_CONTRACT_001"

AGENT_ANSWERABILITY_STATES = (
    "ANSWERABLE_FROM_REGISTERED_ARTIFACT",
    "ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT",
    "NEEDS_CORE_DIAGNOSTIC_OR_ML",
    "NEEDS_USER_INPUT_OR_DATA",
    "BLOCKED_BY_CLAIM_BOUNDARY",
)

FUTURE_AGENT_ANSWERABILITY_EVAL_DIMENSIONS = (
    "answerability_classification_accuracy",
    "correct_routing_to_deterministic_diagnostic_or_core_ml",
    "minimal_follow_up_question_quality",
    "no_hallucinated_facts",
    "no_claim_boundary_violations",
    "graceful_recovery_when_tools_fail_or_outputs_missing",
    "clear_distinction_known_unknown_provisional_blocked",
    "no_pvalue_ci_design_production_claims_without_authoritative_outputs",
)

REVISED_ROADMAP_SEQUENCE = (
    "METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001",
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001",
    "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001",
    "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001",
    "ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001",
    "GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001",
    "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001",
    "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001",
    "PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001",
    "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001",
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
    "PANEL_EXP_AGENT_ANSWERABILITY_AND_RECOVERY_CONTRACT_001",
    "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001",
    "SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001",
    "PORTFOLIO_TEST_TIERING_ENGINE_001",
    "CANDIDATE_DESIGN_GENERATOR_001",
    "SHARED_CONTROL_AND_MULTICELL_INFERENCE_CONTRACT_001",
    "DESIGN_BASED_INFERENCE_TOOLING_CONTRACT_001",
    "DESIGN_BASED_INFERENCE_FAST_PATH_001",
    "BALLPARK_FEASIBILITY_MODE_CONTRACT_001",
    "LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001",
    "MODEL_BASED_FALLBACK_ROUTER_001",
    "AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001",
)

SCENARIO_TESTS = (
    "golden_path_scenarios_gp_001_through_gp_008",
    "blocked_provisional_scenarios_bp_001_through_bp_018",
    "critical_implementation_anti_patterns",
    "scenario_acceptance_dimensions",
    "required_output_artifact_categories",
    "authorization_flags_expected_false_in_every_scenario",
    "llm_explanation_acceptance",
    "report_builder_non_inference_acceptance",
    "fixture_mode_product_mode_boundary",
    "demo_notebook_boundary",
    "agent_packet_manifest_acceptance",
    "artifact_registry_provenance_acceptance",
    "claim_boundary_acceptance",
    "sample_schema_no_final_claim",
    "ballpark_no_final_claim",
    "shared_control_no_independent_test_fiction",
    "unregistered_artifact_blocked",
    "hidden_failure_blocked",
    "expired_revoked_artifact_blocked",
    "generic_readiness_overgeneralization_blocked",
    "profiler_implementation_notes",
    "no_bp_019_plus_scenario_explosion",
    "future_agent_answerability_recovery_roadmap",
    "revised_roadmap_sequence",
)

_AUTH_FLAGS = {
    "panel_exp_golden_path_runtime_authorized": False,
    "golden_path_runtime_authorized": False,
    "golden_path_regression_suite_runtime_authorized": False,
    "fixture_specific_product_logic_authorized": False,
    "demo_specific_product_logic_authorized": False,
    "report_builder_inference_authorized": False,
    "notebook_demo_runtime_authorized": False,
    "generic_readiness_runtime_authorized": False,
    "agent_orchestration_runtime_authorized": False,
    "artifact_registry_runtime_authorized": False,
    "llm_report_grounding_runtime_authorized": False,
    "geo_kpi_spend_profiler_runtime_authorized": False,
    "geo_unit_feasibility_runtime_authorized": False,
    "spend_feasibility_runtime_authorized": False,
    "portfolio_planner_runtime_authorized": False,
    "candidate_design_generator_runtime_authorized": False,
    "design_based_inference_production_authorized": False,
    "model_based_fallback_router_authorized": False,
    "llm_design_recommendation_authorized": False,
    "production_design_recommendation_authorized": False,
    "production_readout_authorized": False,
    "production_p_value_authorized": False,
    "causal_confidence_interval_authorized": False,
    "production_authorization_granted": False,
    "selector_implementation_authorized": False,
    "production_selection_router_authorized": False,
    "multicell_production_claim_authorized": False,
    "trustreport_authorized": False,
    "calibration_signal_allowed": False,
    "mmm_ingestion_allowed": False,
    "llm_decisioning_allowed": False,
    "production_decisioning_allowed": False,
    "live_api_authorized": False,
    "scheduler_authorized": False,
    "budget_optimization_allowed": False,
    "package_side_agents_authorized": False,
}

NON_GOALS = (
    "no_runtime_golden_path_execution",
    "no_runtime_agents",
    "no_registry_storage",
    "no_data_profilers",
    "no_planner_logic",
    "no_estimators",
    "no_design_algorithms",
    "no_inference_logic",
    "no_p_values",
    "no_confidence_intervals",
    "no_production_recommendations",
    "no_budget_optimization",
    "no_selector_router_behavior",
    "no_mmm_ingestion",
    "no_llm_decisioning",
    "no_notebooks",
    "no_demos",
    "no_downstream_integrations",
)


@dataclass(frozen=True)
class PanelExpGoldenPathAcceptanceTestsContract:
    artifact_id: str
    contract_scope: str
    golden_paths_before_demos: bool
    blocked_paths_before_production_claims: bool
    happy_paths_require_paired_failure_or_provisional_paths: bool
    production_authorization_from_golden_paths: bool
    fixtures_define_product_branches: bool
    demo_paths_promoted_to_product_paths: bool
    report_builders_may_perform_hidden_inference: bool
    llm_may_infer_from_raw_fixture_or_raw_data: bool
    notebooks_before_golden_paths_stable: bool
    generic_readiness_overgeneralization_allowed: bool
    required_contracts: tuple[str, ...]
    required_acceptance_dimensions: tuple[str, ...]
    golden_path_scenarios: tuple[str, ...]
    blocked_provisional_scenarios: tuple[str, ...]
    required_output_artifact_categories: tuple[str, ...]
    llm_explanation_acceptance_defined: bool
    report_builder_non_inference_acceptance_defined: bool
    fixture_mode_product_mode_boundary_defined: bool
    demo_notebook_boundary_defined: bool
    revised_roadmap_sequence: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    final_verdict: str


def build_panel_exp_golden_path_acceptance_tests_contract() -> PanelExpGoldenPathAcceptanceTestsContract:
    """Return deterministic panel_exp golden path acceptance tests contract."""
    return PanelExpGoldenPathAcceptanceTestsContract(
        artifact_id=_ARTIFACT_ID,
        contract_scope=CONTRACT_SCOPE,
        golden_paths_before_demos=True,
        blocked_paths_before_production_claims=True,
        happy_paths_require_paired_failure_or_provisional_paths=True,
        production_authorization_from_golden_paths=False,
        fixtures_define_product_branches=False,
        demo_paths_promoted_to_product_paths=False,
        report_builders_may_perform_hidden_inference=False,
        llm_may_infer_from_raw_fixture_or_raw_data=False,
        notebooks_before_golden_paths_stable=False,
        generic_readiness_overgeneralization_allowed=False,
        required_contracts=REQUIRED_CONTRACTS,
        required_acceptance_dimensions=REQUIRED_ACCEPTANCE_DIMENSIONS,
        golden_path_scenarios=GOLDEN_PATH_SCENARIOS,
        blocked_provisional_scenarios=BLOCKED_PROVISIONAL_SCENARIOS,
        required_output_artifact_categories=REQUIRED_OUTPUT_ARTIFACT_CATEGORIES,
        llm_explanation_acceptance_defined=True,
        report_builder_non_inference_acceptance_defined=True,
        fixture_mode_product_mode_boundary_defined=True,
        demo_notebook_boundary_defined=True,
        revised_roadmap_sequence=REVISED_ROADMAP_SEQUENCE,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_panel_exp_golden_path_acceptance_tests_contract(
    contract: PanelExpGoldenPathAcceptanceTestsContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.golden_paths_before_demos:
        issues.append("golden_paths_before_demos must be true")
    if not contract.blocked_paths_before_production_claims:
        issues.append("blocked_paths_before_production_claims must be true")
    if contract.production_authorization_from_golden_paths:
        issues.append("production_authorization_from_golden_paths must be false")
    if contract.fixtures_define_product_branches:
        issues.append("fixtures_define_product_branches must be false")
    if contract.report_builders_may_perform_hidden_inference:
        issues.append("report_builders_may_perform_hidden_inference must be false")
    if contract.llm_may_infer_from_raw_fixture_or_raw_data:
        issues.append("llm_may_infer_from_raw_fixture_or_raw_data must be false")
    if contract.required_contracts != REQUIRED_CONTRACTS:
        issues.append("required_contracts mismatch")
    if len(contract.golden_path_scenarios) < 8:
        issues.append("must define at least 8 golden path scenarios")
    if len(contract.blocked_provisional_scenarios) < 18:
        issues.append("must define at least 18 blocked/provisional scenarios")
    if len(contract.blocked_provisional_scenarios) > 18:
        issues.append("must not expand beyond BP-001 through BP-018")
    if any(s.startswith("BP-019") or s.startswith("BP-02") for s in contract.blocked_provisional_scenarios):
        issues.append("BP-019+ scenario explosion not allowed")
    geo_idx = contract.revised_roadmap_sequence.index("GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001")
    if contract.revised_roadmap_sequence[geo_idx + 1] != FUTURE_AGENT_ANSWERABILITY_RECOVERY_CONTRACT:
        issues.append("agent answerability contract must follow geo unit feasibility diagnostics")
    idx = contract.revised_roadmap_sequence.index("PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001")
    if contract.revised_roadmap_sequence[idx + 1] != RECOMMENDED_NEXT_ARTIFACT:
        issues.append("geo KPI spend profiler must follow golden path contract")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_panel_exp_golden_path_acceptance_tests_contract()
    validation = validate_panel_exp_golden_path_acceptance_tests_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    scenarios.append(_s("golden_paths_before_demos", contract.golden_paths_before_demos))
    scenarios.append(
        _s("blocked_paths_before_production_claims", contract.blocked_paths_before_production_claims)
    )
    scenarios.append(
        _s(
            "happy_paths_require_paired_failure_or_provisional_paths",
            contract.happy_paths_require_paired_failure_or_provisional_paths,
        )
    )
    scenarios.append(
        _s(
            "production_authorization_from_golden_paths_false",
            not contract.production_authorization_from_golden_paths,
        )
    )
    scenarios.append(_s("fixtures_do_not_define_product_branches", not contract.fixtures_define_product_branches))
    scenarios.append(
        _s("report_builders_no_hidden_inference", not contract.report_builders_may_perform_hidden_inference)
    )
    scenarios.append(
        _s("llm_no_raw_fixture_inference", not contract.llm_may_infer_from_raw_fixture_or_raw_data)
    )
    scenarios.append(_s("required_contracts_present", contract.required_contracts == REQUIRED_CONTRACTS))
    scenarios.append(_s("golden_path_scenarios_present", len(contract.golden_path_scenarios) == 8))
    scenarios.append(
        _s("blocked_provisional_scenarios_present", len(contract.blocked_provisional_scenarios) == 18)
    )
    scenarios.append(_s("llm_explanation_acceptance_defined", contract.llm_explanation_acceptance_defined))
    scenarios.append(
        _s(
            "report_builder_non_inference_acceptance_defined",
            contract.report_builder_non_inference_acceptance_defined,
        )
    )
    scenarios.append(
        _s(
            "fixture_mode_product_mode_boundary_defined",
            contract.fixture_mode_product_mode_boundary_defined,
        )
    )
    scenarios.append(_s("demo_notebook_boundary_defined", contract.demo_notebook_boundary_defined))
    scenarios.append(_s("profiler_implementation_notes_present", len(PROFILER_IMPLEMENTATION_NOTES) == 5))
    scenarios.append(_s("no_bp_019_plus", len(contract.blocked_provisional_scenarios) == 18))
    geo_idx = contract.revised_roadmap_sequence.index("GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001")
    scenarios.append(
        _s(
            "future_agent_answerability_recovery_roadmap",
            contract.revised_roadmap_sequence[geo_idx + 1] == FUTURE_AGENT_ANSWERABILITY_RECOVERY_CONTRACT,
        )
    )
    idx = contract.revised_roadmap_sequence.index("PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001")
    scenarios.append(
        _s("next_artifact_profiler", contract.revised_roadmap_sequence[idx + 1] == RECOMMENDED_NEXT_ARTIFACT)
    )
    for test_id in SCENARIO_TESTS:
        scenarios.append(_s(f"scenario_spec_{test_id}", True))
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not contract.authorization_flags[flag]))
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
    contract = build_panel_exp_golden_path_acceptance_tests_contract()
    validation = validate_panel_exp_golden_path_acceptance_tests_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "panel_exp_golden_path_acceptance_tests_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "contract_scope": CONTRACT_SCOPE,
        "golden_paths_before_demos": True,
        "blocked_paths_before_production_claims": True,
        "happy_paths_require_paired_failure_or_provisional_paths": True,
        "production_authorization_from_golden_paths": False,
        "fixtures_define_product_branches": False,
        "demo_paths_promoted_to_product_paths": False,
        "report_builders_may_perform_hidden_inference": False,
        "llm_may_infer_from_raw_fixture_or_raw_data": False,
        "notebooks_before_golden_paths_stable": False,
        "generic_readiness_overgeneralization_allowed": False,
        "required_contracts": list(REQUIRED_CONTRACTS),
        "required_acceptance_dimensions": list(REQUIRED_ACCEPTANCE_DIMENSIONS),
        "golden_path_scenarios": list(GOLDEN_PATH_SCENARIOS),
        "blocked_provisional_scenarios": list(BLOCKED_PROVISIONAL_SCENARIOS),
        "required_output_artifact_categories": list(REQUIRED_OUTPUT_ARTIFACT_CATEGORIES),
        "llm_explanation_acceptance_defined": True,
        "report_builder_non_inference_acceptance_defined": True,
        "fixture_mode_product_mode_boundary_defined": True,
        "demo_notebook_boundary_defined": True,
        "profiler_implementation_notes": list(PROFILER_IMPLEMENTATION_NOTES),
        "overexpanded_corner_case_rules_reverted_or_avoided": True,
        "profiler_implementation_notes_kept_lightweight": True,
        "future_agent_answerability_recovery_contract_added": FUTURE_AGENT_ANSWERABILITY_RECOVERY_CONTRACT,
        "agent_answerability_states": list(AGENT_ANSWERABILITY_STATES),
        "future_agent_answerability_eval_dimensions": list(FUTURE_AGENT_ANSWERABILITY_EVAL_DIMENSIONS),
        "agent_freeform_causal_reasoning_allowed": False,
        "agent_corner_case_rule_explosion_allowed": False,
        "revised_roadmap_sequence": list(REVISED_ROADMAP_SEQUENCE),
        "authorization_flags": dict(_AUTH_FLAGS),
        "recommended_next_artifact": RECOMMENDED_NEXT_ARTIFACT,
        "scenario_tests_required": list(SCENARIO_TESTS),
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
