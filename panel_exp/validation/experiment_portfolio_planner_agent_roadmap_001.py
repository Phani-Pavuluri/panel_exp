"""EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "experiment_portfolio_planner_agent_roadmap_defined_no_runtime_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001_summary.json"

PRODUCT_PRINCIPLE = "minimize_questions_maximize_data_inference_return_feasible_design_alternatives"

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

READOUT_TIERS = (
    "tier_1_production_grade_causal_readout",
    "tier_2_directional_diagnostic_readout",
    "tier_3_prior_building_shadow_readout",
)

DESIGN_OPTIONS = (
    "single_full_power_test",
    "dedicated_control_design",
    "shared_control_multi_arm_design",
    "mutually_exclusive_multi_arm_design",
    "blocked_matched_multi_arm_design",
    "factorial_fractional_factorial_design",
    "prioritized_full_power_plus_shadow_design",
    "rotating_staggered_design_restricted",
)

SPEND_MANIPULATION_TYPES = (
    "go_dark",
    "heavy_up",
    "go_live",
)

REVISED_ROADMAP_SEQUENCE = (
    "METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001",
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001",
    "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001",
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

RECOMMENDED_NEXT_ARTIFACT = "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001"
FIRST_PLANNER_LANE_ARTIFACT = "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"

_AUTH_FLAGS = {
    "experiment_portfolio_planner_runtime_authorized": False,
    "geo_kpi_spend_data_profiler_runtime_authorized": False,
    "geo_unit_feasibility_runtime_authorized": False,
    "portfolio_test_tiering_runtime_authorized": False,
    "spend_budget_reallocation_runtime_authorized": False,
    "candidate_design_generator_runtime_authorized": False,
    "design_based_inference_production_authorized": False,
    "model_based_fallback_router_authorized": False,
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
    "no_estimator_implementation",
    "no_inference_engine",
    "no_production_authorization",
    "no_selector_router_runtime",
    "no_mmm_ingestion",
    "no_llm_decisioning",
    "no_budget_optimization",
)


@dataclass(frozen=True)
class ExperimentPortfolioPlannerAgentRoadmap:
    artifact_id: str
    product_principle: str
    design_selection_before_estimator_selection: bool
    data_first_planning: bool
    adaptive_intake_not_static_questionnaire: bool
    planned_agents: tuple[str, ...]
    readout_tiers: tuple[str, ...]
    design_options: tuple[str, ...]
    spend_manipulation_types: tuple[str, ...]
    revised_roadmap_sequence: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    first_planner_lane_artifact: str
    final_verdict: str


def build_experiment_portfolio_planner_agent_roadmap() -> ExperimentPortfolioPlannerAgentRoadmap:
    """Return deterministic experiment portfolio planner agent roadmap."""
    return ExperimentPortfolioPlannerAgentRoadmap(
        artifact_id=_ARTIFACT_ID,
        product_principle=PRODUCT_PRINCIPLE,
        design_selection_before_estimator_selection=True,
        data_first_planning=True,
        adaptive_intake_not_static_questionnaire=True,
        planned_agents=PLANNED_AGENTS,
        readout_tiers=READOUT_TIERS,
        design_options=DESIGN_OPTIONS,
        spend_manipulation_types=SPEND_MANIPULATION_TYPES,
        revised_roadmap_sequence=REVISED_ROADMAP_SEQUENCE,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        first_planner_lane_artifact=FIRST_PLANNER_LANE_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_experiment_portfolio_planner_agent_roadmap(
    roadmap: ExperimentPortfolioPlannerAgentRoadmap,
) -> dict[str, Any]:
    issues: list[str] = []
    if not roadmap.design_selection_before_estimator_selection:
        issues.append("design_selection_before_estimator_selection must be true")
    if not roadmap.data_first_planning:
        issues.append("data_first_planning must be true")
    if not roadmap.adaptive_intake_not_static_questionnaire:
        issues.append("adaptive_intake_not_static_questionnaire must be true")
    if roadmap.planned_agents != PLANNED_AGENTS:
        issues.append("planned_agents mismatch")
    if "shared_control_multi_arm_design" not in roadmap.design_options:
        issues.append("shared_control_multi_arm_design required")
    if "mutually_exclusive_multi_arm_design" not in roadmap.design_options:
        issues.append("mutually_exclusive_multi_arm_design required")
    if "rotating_staggered_design_restricted" not in roadmap.design_options:
        issues.append("rotating_staggered_design_restricted required")
    for flag, expected in _AUTH_FLAGS.items():
        if roadmap.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    roadmap = build_experiment_portfolio_planner_agent_roadmap()
    validation = validate_experiment_portfolio_planner_agent_roadmap(roadmap)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    scenarios.append(_s("product_principle_present", bool(roadmap.product_principle)))
    scenarios.append(_s("adaptive_intake_present", roadmap.adaptive_intake_not_static_questionnaire))
    scenarios.append(_s("data_first_planning_present", roadmap.data_first_planning))
    scenarios.append(_s("all_planned_agents_present", roadmap.planned_agents == PLANNED_AGENTS))
    scenarios.append(_s("all_readout_tiers_present", roadmap.readout_tiers == READOUT_TIERS))
    scenarios.append(_s("all_design_options_present", roadmap.design_options == DESIGN_OPTIONS))
    scenarios.append(
        _s(
            "mutually_exclusive_and_shared_control_distinguished",
            "mutually_exclusive_multi_arm_design" in roadmap.design_options
            and "shared_control_multi_arm_design" in roadmap.design_options,
        )
    )
    scenarios.append(
        _s(
            "rotating_staggered_restricted",
            "rotating_staggered_design_restricted" in roadmap.design_options,
        )
    )
    scenarios.append(_s("spend_manipulation_types_present", roadmap.spend_manipulation_types == SPEND_MANIPULATION_TYPES))
    scenarios.append(_s("revised_roadmap_sequence_present", bool(roadmap.revised_roadmap_sequence)))
    scenarios.append(
        _s(
            "design_before_estimator",
            roadmap.design_selection_before_estimator_selection,
        )
    )
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not roadmap.authorization_flags[flag]))
    scenarios.append(_s("recommended_next_artifact_present", bool(roadmap.recommended_next_artifact)))
    scenarios.append(
        _s(
            "first_planner_lane_augsynth_not_first",
            roadmap.first_planner_lane_artifact == FIRST_PLANNER_LANE_ARTIFACT,
        )
    )
    scenarios.append(_s("final_verdict_matches", roadmap.final_verdict == _VERDICT))
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
    roadmap = build_experiment_portfolio_planner_agent_roadmap()
    validation = validate_experiment_portfolio_planner_agent_roadmap(roadmap)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "experiment_portfolio_planner_agent_roadmap",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "product_principle": PRODUCT_PRINCIPLE,
        "design_selection_before_estimator_selection": True,
        "data_first_planning": True,
        "adaptive_intake_not_static_questionnaire": True,
        "planned_agents": list(PLANNED_AGENTS),
        "readout_tiers": list(READOUT_TIERS),
        "design_options": list(DESIGN_OPTIONS),
        "spend_manipulation_types": list(SPEND_MANIPULATION_TYPES),
        "revised_roadmap_sequence": list(REVISED_ROADMAP_SEQUENCE),
        "authorization_flags": dict(_AUTH_FLAGS),
        "recommended_next_artifact": RECOMMENDED_NEXT_ARTIFACT,
        "first_planner_lane_artifact": FIRST_PLANNER_LANE_ARTIFACT,
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
