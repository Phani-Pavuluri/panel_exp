"""EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "experiment_portfolio_planner_agent_tooling_contract_defined_no_runtime_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001_summary.json"
)

CORE_PRINCIPLE = "tool_first_agent_second"
RECOMMENDED_NEXT_ARTIFACT = "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"

PLANNED_AGENTS = (
    "intake_goal_clarifier_agent",
    "data_profiler_cleaner_agent",
    "geo_unit_market_feasibility_agent",
    "portfolio_planner_agent",
    "spend_contrast_budget_reallocation_agent",
    "candidate_design_generator",
    "design_based_inference_fast_path",
    "model_based_fallback_router",
    "llm_explanation_layer",
)

REQUIRED_REPORT_TYPES = (
    "PlanningIntentReport",
    "DataProfileReport",
    "ColumnMappingReport",
    "GeoTimeCoverageReport",
    "UsablePanelSummary",
    "GeoUnitFeasibilityReport",
    "MatchabilityReport",
    "MarketConcentrationReport",
    "PortfolioFeasibilityReport",
    "TierAssignmentPlan",
    "SpendContrastFeasibilityReport",
    "CellSpendPlan",
    "EffectSizeSensitivityTable",
    "CandidateDesignSet",
    "DesignFeasibilityScores",
    "DesignBasedInferencePlan",
    "InferenceValidityDiagnostics",
    "ModelFallbackRecommendation",
    "EstimatorEligibilityReport",
    "ClaimBoundaryReport",
)

REQUIRED_READINESS_GATES = (
    "typed_input_contract",
    "typed_output_report",
    "deterministic_implementation",
    "failure_mode_behavior",
    "unit_tests",
    "scenario_tests",
    "fixture_coverage",
    "claim_boundary_tests",
    "summary_json_report_generation_tests",
)

REVISED_ROADMAP_SEQUENCE = (
    "METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001",
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001",
    "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001",
    "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001",
    "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001",
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
    "PORTFOLIO_TEST_TIERING_ENGINE_001",
    "SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001",
    "CANDIDATE_DESIGN_GENERATOR_001",
    "DESIGN_BASED_INFERENCE_FAST_PATH_001",
    "MODEL_BASED_FALLBACK_ROUTER_001",
    "AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001",
)

AGENT_TOOLING: dict[str, dict[str, tuple[str, ...]]] = {
    "intake_goal_clarifier_agent": {
        "contracts": (
            "ExperimentPlanningIntent",
            "ExperimentGoal",
            "ReadoutTierRequest",
            "PlanningWindow",
            "KPISelection",
            "DataAvailabilityState",
            "MissingCriticalFieldReport",
        ),
        "output_reports": (
            "PlanningIntentReport",
            "MissingInputReport",
            "RecommendedDataRequest",
        ),
    },
    "data_profiler_cleaner_agent": {
        "modules": (
            "schema_detector",
            "column_mapper",
            "time_grain_detector",
            "geo_unit_detector",
            "duplicate_detector",
            "missingness_profiler",
            "coverage_profiler",
            "outlier_detector",
            "low_volume_unit_detector",
            "spend_kpi_summary_profiler",
            "channel_campaign_availability_detector",
        ),
        "output_reports": (
            "DataProfileReport",
            "ColumnMappingReport",
            "GeoTimeCoverageReport",
            "DataQualityWarningReport",
            "UsablePanelSummary",
        ),
    },
    "geo_unit_market_feasibility_agent": {
        "modules": (
            "eligible_unit_filter",
            "geo_size_concentration_diagnostic",
            "pre_period_kpi_variation_diagnostic",
            "pair_block_matchability_diagnostic",
            "trend_similarity_diagnostic",
            "interference_spillover_risk_checklist",
            "minimum_cell_size_diagnostic",
            "unit_count_sufficiency_diagnostic",
            "dma_gma_state_province_custom_unit_mapper",
        ),
        "output_reports": (
            "GeoUnitFeasibilityReport",
            "MatchabilityReport",
            "MarketConcentrationReport",
            "DesignUnitInventory",
            "FeasibilityStatusReport",
        ),
    },
    "portfolio_planner_agent": {
        "modules": (
            "test_request_parser",
            "priority_scorer",
            "tier_assignment_feasibility_checker",
            "multi_test_capacity_checker",
            "claim_level_feasibility_checker",
            "portfolio_alternative_generator",
        ),
        "output_reports": (
            "PortfolioFeasibilityReport",
            "TierAssignmentPlan",
            "PortfolioDesignAlternatives",
            "BlockedRequestedTests",
            "DowngradeRecommendations",
        ),
    },
    "spend_contrast_budget_reallocation_agent": {
        "modules": (
            "spend_baseline_profiler",
            "cell_level_spend_simulator",
            "go_dark_contrast_calculator",
            "heavy_up_contrast_calculator",
            "go_live_contrast_calculator",
            "budget_sufficiency_checker",
            "effect_size_mde_sensitivity_calculator",
            "budget_reallocation_searcher",
            "business_cost_summary_generator",
        ),
        "output_reports": (
            "SpendContrastFeasibilityReport",
            "CellSpendPlan",
            "EffectSizeSensitivityTable",
            "BudgetGapReport",
            "SpendReallocationRecommendations",
        ),
    },
    "candidate_design_generator": {
        "modules": (
            "single_test_design_generator",
            "dedicated_control_design_generator",
            "shared_control_multi_arm_generator",
            "mutually_exclusive_multi_arm_generator",
            "blocked_matched_design_generator",
            "prioritized_full_power_plus_shadow_generator",
            "factorial_fractional_factorial_generator",
            "rotating_staggered_restricted_generator",
            "design_scoring_function",
            "design_feasibility_comparator",
        ),
        "output_reports": (
            "CandidateDesignSet",
            "DesignFeasibilityScores",
            "RecommendedDesignCandidate",
            "RejectedDesignsWithReasons",
            "DesignAssumptionReport",
        ),
    },
    "design_based_inference_fast_path": {
        "modules": (
            "blocked_difference_estimator",
            "matched_pair_estimator",
            "cuped_ancova_adjusted_estimator",
            "randomization_permutation_inference",
            "shared_control_covariance_handler",
            "multiplicity_correction",
            "small_sample_warning_system",
            "ci_construction_diagnostics",
        ),
        "output_reports": (
            "DesignBasedInferencePlan",
            "AllowedClaimLevel",
            "InferenceValidityDiagnostics",
            "PValueAuthorizationRecommendation",
            "CIValidityRecommendation",
        ),
    },
    "model_based_fallback_router": {
        "modules": (
            "tbrridge_eligibility_checker",
            "synthetic_did_eligibility_checker",
            "augsynth_ascm_eligibility_checker",
            "bayesian_tbr_eligibility_checker",
            "method_claim_boundary_checker",
            "method_specific_diagnostics_availability_checker",
        ),
        "output_reports": (
            "ModelFallbackRecommendation",
            "EstimatorEligibilityReport",
            "AllowedClaimsByEstimator",
            "RequiredValidationBeforeProduction",
        ),
    },
    "llm_explanation_layer": {
        "required_inputs": (
            "PlanningIntentReport",
            "DataProfileReport",
            "GeoUnitFeasibilityReport",
            "PortfolioFeasibilityReport",
            "SpendContrastFeasibilityReport",
            "CandidateDesignSet",
            "DesignBasedInferencePlan",
            "ModelFallbackRecommendation",
            "ClaimBoundaryReport",
        ),
        "output_reports": ("LLMExplanationSummary",),
    },
}

ANSWERABILITY_MATRIX: dict[str, str] = {
    "Can I run 5 tests?": "PortfolioFeasibilityReport",
    "How many should be Tier 1?": "TierAssignmentPlan",
    "Do I have enough geos?": "GeoUnitFeasibilityReport",
    "Should I use shared control?": "CandidateDesignReport plus shared-control diagnostics",
    "How much spend do I need?": "SpendContrastFeasibilityReport",
    "Can I get valid p-values?": "InferenceValidityDiagnostics plus release-gate state",
    "Can I get valid CIs?": "CIValidityRecommendation plus release-gate state",
    "Should I use AugSynth?": "ModelFallbackRecommendation plus method eligibility diagnostics",
    "Can this feed MMM?": "ClaimBoundaryReport or CalibrationSignal readiness",
}

SCENARIO_TESTS_REQUIRED = (
    "single_test_with_enough_units_and_spend",
    "single_test_with_too_few_units",
    "five_test_portfolio_insufficient_units",
    "five_test_portfolio_2_tier1_2_tier2_1_tier3",
    "shared_control_feasible_correlated_contrasts_warning",
    "mutually_exclusive_multi_arm_infeasible_too_few_cells",
    "heavy_up_spend_contrast_too_weak",
    "go_dark_business_cost_warning",
    "go_live_ramp_up_warning",
    "rotating_staggered_restricted_carryover_risk",
    "missing_kpi_column",
    "missing_spend_column",
    "daily_data_detected",
    "weekly_data_detected",
    "province_state_unit_count_too_small",
    "dma_gma_custom_unit_mapping_needed",
)

_AUTH_FLAGS = {
    "experiment_portfolio_planner_runtime_authorized": False,
    "planner_agent_tooling_contract_runtime_authorized": False,
    "intake_goal_clarifier_runtime_authorized": False,
    "data_profiler_cleaner_runtime_authorized": False,
    "geo_unit_market_feasibility_runtime_authorized": False,
    "portfolio_planner_runtime_authorized": False,
    "spend_contrast_budget_reallocation_runtime_authorized": False,
    "candidate_design_generator_runtime_authorized": False,
    "design_based_inference_production_authorized": False,
    "model_based_fallback_router_authorized": False,
    "llm_explanation_layer_production_authorized": False,
    "llm_design_recommendation_authorized": False,
    "production_design_recommendation_authorized": False,
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
    "no_runtime_planner_agent",
    "no_agent_execution",
    "no_estimator_implementation",
    "no_inference_engine",
    "no_design_assignment_algorithms",
    "no_budget_optimization",
    "no_production_recommendations",
    "no_downstream_integrations",
)


@dataclass(frozen=True)
class ExperimentPortfolioPlannerAgentToolingContract:
    artifact_id: str
    core_principle: str
    no_tool_no_claim_rule: bool
    llm_may_explain_but_not_invent_diagnostics: bool
    planned_agents: tuple[str, ...]
    required_report_types: tuple[str, ...]
    required_readiness_gates: tuple[str, ...]
    answerability_matrix_defined: bool
    scenario_tests_required: bool
    revised_roadmap_sequence: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    final_verdict: str


def build_experiment_portfolio_planner_agent_tooling_contract() -> ExperimentPortfolioPlannerAgentToolingContract:
    """Return deterministic planner agent tooling contract."""
    return ExperimentPortfolioPlannerAgentToolingContract(
        artifact_id=_ARTIFACT_ID,
        core_principle=CORE_PRINCIPLE,
        no_tool_no_claim_rule=True,
        llm_may_explain_but_not_invent_diagnostics=True,
        planned_agents=PLANNED_AGENTS,
        required_report_types=REQUIRED_REPORT_TYPES,
        required_readiness_gates=REQUIRED_READINESS_GATES,
        answerability_matrix_defined=True,
        scenario_tests_required=True,
        revised_roadmap_sequence=REVISED_ROADMAP_SEQUENCE,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_experiment_portfolio_planner_agent_tooling_contract(
    contract: ExperimentPortfolioPlannerAgentToolingContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if contract.core_principle != CORE_PRINCIPLE:
        issues.append("core_principle must be tool_first_agent_second")
    if not contract.no_tool_no_claim_rule:
        issues.append("no_tool_no_claim_rule must be true")
    if not contract.llm_may_explain_but_not_invent_diagnostics:
        issues.append("llm_may_explain_but_not_invent_diagnostics must be true")
    if contract.planned_agents != PLANNED_AGENTS:
        issues.append("planned_agents mismatch")
    for agent in PLANNED_AGENTS:
        if agent not in AGENT_TOOLING:
            issues.append(f"missing tooling spec for {agent}")
    idx = contract.revised_roadmap_sequence.index("EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001")
    tooling_idx = contract.revised_roadmap_sequence.index("EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001")
    if tooling_idx != idx + 1:
        issues.append("tooling contract must follow planner roadmap")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_experiment_portfolio_planner_agent_tooling_contract()
    validation = validate_experiment_portfolio_planner_agent_tooling_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    scenarios.append(_s("tool_first_agent_second", contract.core_principle == CORE_PRINCIPLE))
    scenarios.append(_s("no_tool_no_claim_rule", contract.no_tool_no_claim_rule))
    scenarios.append(_s("all_planned_agents_present", contract.planned_agents == PLANNED_AGENTS))
    for agent in PLANNED_AGENTS:
        scenarios.append(_s(f"agent_tooling_{agent}", agent in AGENT_TOOLING))
    scenarios.append(_s("required_report_types_present", contract.required_report_types == REQUIRED_REPORT_TYPES))
    scenarios.append(_s("answerability_matrix_defined", contract.answerability_matrix_defined))
    scenarios.append(_s("readiness_gates_present", contract.required_readiness_gates == REQUIRED_READINESS_GATES))
    scenarios.append(_s("scenario_tests_listed", contract.scenario_tests_required))
    idx = contract.revised_roadmap_sequence.index("EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001")
    tooling_idx = contract.revised_roadmap_sequence.index("EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001")
    scenarios.append(_s("tooling_after_roadmap", tooling_idx == idx + 1))
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
    contract = build_experiment_portfolio_planner_agent_tooling_contract()
    validation = validate_experiment_portfolio_planner_agent_tooling_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "experiment_portfolio_planner_agent_tooling_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "core_principle": CORE_PRINCIPLE,
        "no_tool_no_claim_rule": True,
        "llm_may_explain_but_not_invent_diagnostics": True,
        "planned_agents": list(PLANNED_AGENTS),
        "agent_tooling": {k: {kk: list(vv) for kk, vv in v.items()} for k, v in AGENT_TOOLING.items()},
        "required_report_types": list(REQUIRED_REPORT_TYPES),
        "required_readiness_gates": list(REQUIRED_READINESS_GATES),
        "answerability_matrix": dict(ANSWERABILITY_MATRIX),
        "answerability_matrix_defined": True,
        "scenario_tests_required": list(SCENARIO_TESTS_REQUIRED),
        "revised_roadmap_sequence": list(REVISED_ROADMAP_SEQUENCE),
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
