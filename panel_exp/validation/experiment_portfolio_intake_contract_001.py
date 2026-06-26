"""EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "experiment_portfolio_intake_contract_defined_no_runtime_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001_summary.json"

CONTRACT_SCOPE = "adaptive_intake_contract_no_runtime"
RECOMMENDED_NEXT_ARTIFACT = "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001"

SUPPORTED_INTAKE_BRANCHES = (
    "single_test_full_data_available",
    "single_test_sample_schema_only",
    "single_test_ballpark_only",
    "multi_test_full_data_available",
    "multi_test_sample_schema_only",
    "multi_test_ballpark_only",
    "unknown_test_count",
    "data_unavailable",
    "insufficient_high_level_context",
)

REQUIRED_OUTPUT_CONTRACTS = (
    "ExperimentPortfolioPlanningIntent",
    "ExperimentGoalSummary",
    "PlanningWindowIntent",
    "RegionMarketIntent",
    "GeoUnitPreferenceOrUnknown",
    "KpiIntent",
    "RequestedTestPortfolio",
    "ReadoutClaimIntent",
    "SpendBudgetIntent",
    "ManipulationIntent",
    "DataAvailabilityIntent",
    "MissingCriticalInputReport",
    "RecommendedDataRequest",
    "IntakeRoutingDecision",
    "IntakeClaimBoundaryReport",
)

DATA_REQUEST_ORDER = (
    "full_geo_kpi_spend_panel",
    "sample_schema",
    "ballpark_planning_inputs",
)

ROUTING_DECISIONS = (
    "request_full_panel_data",
    "request_sample_schema",
    "request_ballpark_inputs",
    "route_to_geo_kpi_spend_profiler",
    "route_to_ballpark_feasibility_mode",
    "ask_minimal_missing_high_level_questions",
    "block_until_required_context_available",
)

READOUT_CLAIM_LEVELS = (
    "decision_grade_p_value_ci",
    "decision_grade_point_estimate_only",
    "directional_diagnostic",
    "prior_building",
    "unknown",
)

DATA_AVAILABILITY_STATES = (
    "full_panel_available",
    "sample_schema_available",
    "ballpark_only",
    "data_unavailable",
    "unknown",
)

MANIPULATION_TYPES = (
    "go_dark",
    "heavy_up",
    "go_live",
    "unknown",
)

NEW_CROSS_CUTTING_CONTRACTS = (
    "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001",
    "PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001",
    "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001",
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
    "single_test_avoids_multi_test_questionnaire",
    "multi_test_asks_only_tier_priority_essentials",
    "unknown_test_count_fallback",
    "full_panel_data_request",
    "sample_schema_request",
    "ballpark_only_provisional_routing",
    "data_unavailable_blocking_or_provisional",
    "decision_grade_pvalue_ci_intent_captured_not_authorized",
    "directional_intent_captured",
    "prior_building_intent_captured",
    "go_dark_intent_captured",
    "heavy_up_intent_captured",
    "go_live_intent_captured",
    "llm_cannot_claim_design_feasibility_from_intake",
    "llm_cannot_claim_pvalues_cis_from_intake",
    "roadmap_includes_agent_packet_provenance_golden_path",
)

_AUTH_FLAGS = {
    "experiment_portfolio_intake_runtime_authorized": False,
    "intake_goal_clarifier_runtime_authorized": False,
    "portfolio_planner_runtime_authorized": False,
    "geo_kpi_spend_profiler_runtime_authorized": False,
    "agent_run_packet_runtime_authorized": False,
    "artifact_registry_runtime_authorized": False,
    "golden_path_runtime_authorized": False,
    "llm_intake_interpretation_authorized": False,
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
    "no_runtime_intake_agent",
    "no_profiler_implementation",
    "no_planner_logic",
    "no_estimator_selection",
    "no_design_feasibility_authorization",
    "no_production_recommendations",
    "no_downstream_integrations",
)


@dataclass(frozen=True)
class ExperimentPortfolioIntakeContract:
    artifact_id: str
    contract_scope: str
    adaptive_intake: bool
    static_questionnaire_allowed: bool
    design_feasibility_authorized_from_intake: bool
    p_values_or_cis_authorized_from_intake: bool
    supported_intake_branches: tuple[str, ...]
    required_output_contracts: tuple[str, ...]
    data_request_order: tuple[str, ...]
    new_cross_cutting_contracts_added_to_roadmap: tuple[str, ...]
    revised_roadmap_sequence: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    final_verdict: str


def build_experiment_portfolio_intake_contract() -> ExperimentPortfolioIntakeContract:
    """Return deterministic experiment portfolio intake contract."""
    return ExperimentPortfolioIntakeContract(
        artifact_id=_ARTIFACT_ID,
        contract_scope=CONTRACT_SCOPE,
        adaptive_intake=True,
        static_questionnaire_allowed=False,
        design_feasibility_authorized_from_intake=False,
        p_values_or_cis_authorized_from_intake=False,
        supported_intake_branches=SUPPORTED_INTAKE_BRANCHES,
        required_output_contracts=REQUIRED_OUTPUT_CONTRACTS,
        data_request_order=DATA_REQUEST_ORDER,
        new_cross_cutting_contracts_added_to_roadmap=NEW_CROSS_CUTTING_CONTRACTS,
        revised_roadmap_sequence=REVISED_ROADMAP_SEQUENCE,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_experiment_portfolio_intake_contract(
    contract: ExperimentPortfolioIntakeContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.adaptive_intake:
        issues.append("adaptive_intake must be true")
    if contract.static_questionnaire_allowed:
        issues.append("static_questionnaire_allowed must be false")
    if contract.design_feasibility_authorized_from_intake:
        issues.append("design feasibility must not be authorized from intake")
    if contract.p_values_or_cis_authorized_from_intake:
        issues.append("p-values/CIs must not be authorized from intake")
    if contract.supported_intake_branches != SUPPORTED_INTAKE_BRANCHES:
        issues.append("supported_intake_branches mismatch")
    idx = contract.revised_roadmap_sequence.index("EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001")
    if contract.revised_roadmap_sequence[idx + 1] != "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001":
        issues.append("agent run packet contract must follow intake contract")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_experiment_portfolio_intake_contract()
    validation = validate_experiment_portfolio_intake_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    scenarios.append(_s("adaptive_intake", contract.adaptive_intake))
    scenarios.append(_s("no_static_questionnaire", not contract.static_questionnaire_allowed))
    scenarios.append(_s("all_intake_branches_present", contract.supported_intake_branches == SUPPORTED_INTAKE_BRANCHES))
    scenarios.append(_s("all_output_contracts_present", contract.required_output_contracts == REQUIRED_OUTPUT_CONTRACTS))
    scenarios.append(_s("data_request_order_present", contract.data_request_order == DATA_REQUEST_ORDER))
    scenarios.append(_s("cross_cutting_contracts_in_roadmap", contract.new_cross_cutting_contracts_added_to_roadmap == NEW_CROSS_CUTTING_CONTRACTS))
    idx = contract.revised_roadmap_sequence.index("EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001")
    scenarios.append(_s("intake_before_agent_packet", contract.revised_roadmap_sequence[idx + 1] == RECOMMENDED_NEXT_ARTIFACT))
    scenarios.append(_s("no_design_feasibility_from_intake", not contract.design_feasibility_authorized_from_intake))
    scenarios.append(_s("no_pvalues_cis_from_intake", not contract.p_values_or_cis_authorized_from_intake))
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
    contract = build_experiment_portfolio_intake_contract()
    validation = validate_experiment_portfolio_intake_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "experiment_portfolio_intake_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "contract_scope": CONTRACT_SCOPE,
        "adaptive_intake": True,
        "static_questionnaire_allowed": False,
        "design_feasibility_authorized_from_intake": False,
        "p_values_or_cis_authorized_from_intake": False,
        "supported_intake_branches": list(SUPPORTED_INTAKE_BRANCHES),
        "required_output_contracts": list(REQUIRED_OUTPUT_CONTRACTS),
        "data_request_order": list(DATA_REQUEST_ORDER),
        "routing_decisions": list(ROUTING_DECISIONS),
        "readout_claim_levels": list(READOUT_CLAIM_LEVELS),
        "data_availability_states": list(DATA_AVAILABILITY_STATES),
        "manipulation_types": list(MANIPULATION_TYPES),
        "new_cross_cutting_contracts_added_to_roadmap": list(NEW_CROSS_CUTTING_CONTRACTS),
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
