"""ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "roadmap_implementation_detail_gap_audit_logged_contracts_required_no_runtime_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001_summary.json"

AUDIT_RESULT = "implementation_detail_contracts_required_before_planner_runtime_work"
SCM_ESTIMATOR_CLAIM_LANE_STATUS = (
    "dedicated_scm_validation_release_gate_lane_exists_no_generic_estimator_claim_detour_now"
)
RECOMMENDED_NEXT_ARTIFACT = "GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001"

REQUIRED_CONTRACT_ARTIFACTS = (
    "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001",
    "DESIGN_BASED_INFERENCE_TOOLING_CONTRACT_001",
    "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001",
    "GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001",
    "SHARED_CONTROL_AND_MULTICELL_INFERENCE_CONTRACT_001",
    "BALLPARK_FEASIBILITY_MODE_CONTRACT_001",
    "LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001",
)

COMPLETED_CONTRACT_ARTIFACTS = (
    "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001",
)

PENDING_CONTRACT_ARTIFACTS = tuple(
    a for a in REQUIRED_CONTRACT_ARTIFACTS if a not in COMPLETED_CONTRACT_ARTIFACTS
)

HIGH_RISK_GAP_AREAS = (
    "agents_without_tool_contracts",
    "design_based_inference_without_exact_tooling_contract",
    "spend_feasibility_without_budget_optimization_boundary",
    "geo_kpi_spend_data_without_schema_semantics_contract",
    "shared_control_multicell_without_covariance_multiplicity_contract",
    "ballpark_mode_without_provisional_claim_boundaries",
    "llm_explanation_without_report_grounding_rules",
)

RISK_IF_SKIPPED = (
    "build_plausible_but_unsafe_scaffolding",
    "treat_roadmap_names_as_implementation_detail",
    "invent_diagnostic_outputs",
    "overclaim_design_feasibility",
    "overclaim_p_values_and_cis",
    "blur_spend_feasibility_with_budget_optimization",
    "treat_ballpark_mode_as_precise",
    "treat_shared_control_readouts_as_independent",
    "generate_llm_explanations_not_grounded_in_evidence_packets",
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

_AUTH_FLAGS = {
    "roadmap_gap_audit_runtime_authorized": False,
    "planner_agent_tooling_contract_runtime_authorized": False,
    "design_based_inference_production_authorized": False,
    "spend_budget_reallocation_runtime_authorized": False,
    "geo_kpi_spend_profiler_runtime_authorized": False,
    "shared_control_multicell_inference_authorized": False,
    "ballpark_feasibility_production_authorized": False,
    "llm_report_grounding_runtime_authorized": False,
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
    "no_runtime_agents",
    "no_estimator_implementation",
    "no_design_algorithms",
    "no_inference_logic",
    "no_production_recommendations",
    "no_budget_optimization",
    "no_downstream_integrations",
)


@dataclass(frozen=True)
class RoadmapImplementationDetailGapAudit:
    artifact_id: str
    audit_result: str
    scm_estimator_claim_lane_status: str
    required_contract_artifacts: tuple[str, ...]
    high_risk_gap_areas: tuple[str, ...]
    revised_roadmap_sequence: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    final_verdict: str


def build_roadmap_implementation_detail_gap_audit() -> RoadmapImplementationDetailGapAudit:
    """Return deterministic roadmap implementation detail gap audit."""
    return RoadmapImplementationDetailGapAudit(
        artifact_id=_ARTIFACT_ID,
        audit_result=AUDIT_RESULT,
        scm_estimator_claim_lane_status=SCM_ESTIMATOR_CLAIM_LANE_STATUS,
        required_contract_artifacts=REQUIRED_CONTRACT_ARTIFACTS,
        high_risk_gap_areas=HIGH_RISK_GAP_AREAS,
        revised_roadmap_sequence=REVISED_ROADMAP_SEQUENCE,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_roadmap_implementation_detail_gap_audit(
    audit: RoadmapImplementationDetailGapAudit,
) -> dict[str, Any]:
    issues: list[str] = []
    if audit.audit_result != AUDIT_RESULT:
        issues.append("audit_result mismatch")
    if "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001" not in audit.required_contract_artifacts:
        issues.append("planner tooling contract must be required")
    idx = audit.revised_roadmap_sequence.index("ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001")
    if audit.revised_roadmap_sequence[idx - 1] != "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001":
        issues.append("gap audit must follow planner tooling contract")
    for flag, expected in _AUTH_FLAGS.items():
        if audit.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    audit = build_roadmap_implementation_detail_gap_audit()
    validation = validate_roadmap_implementation_detail_gap_audit(audit)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    scenarios.append(_s("audit_result_present", audit.audit_result == AUDIT_RESULT))
    scenarios.append(
        _s(
            "scm_dedicated_lane_no_generic_detour",
            "dedicated_scm" in audit.scm_estimator_claim_lane_status,
        )
    )
    scenarios.append(
        _s(
            "required_contracts_present",
            audit.required_contract_artifacts == REQUIRED_CONTRACT_ARTIFACTS,
        )
    )
    scenarios.append(_s("high_risk_gaps_present", audit.high_risk_gap_areas == HIGH_RISK_GAP_AREAS))
    scenarios.append(_s("revised_sequence_present", bool(audit.revised_roadmap_sequence)))
    idx = audit.revised_roadmap_sequence.index("ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001")
    scenarios.append(
        _s(
            "gap_audit_after_tooling_contract",
            audit.revised_roadmap_sequence[idx - 1]
            == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001",
        )
    )
    scenarios.append(
        _s(
            "next_contract_geo_kpi_spec",
            audit.revised_roadmap_sequence[idx + 1] == RECOMMENDED_NEXT_ARTIFACT,
        )
    )
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not audit.authorization_flags[flag]))
    scenarios.append(_s("recommended_next_artifact_present", bool(audit.recommended_next_artifact)))
    scenarios.append(_s("final_verdict_matches", audit.final_verdict == _VERDICT))
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
    audit = build_roadmap_implementation_detail_gap_audit()
    validation = validate_roadmap_implementation_detail_gap_audit(audit)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "roadmap_implementation_detail_gap_audit",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "audit_result": AUDIT_RESULT,
        "scm_estimator_claim_lane_status": SCM_ESTIMATOR_CLAIM_LANE_STATUS,
        "required_contract_artifacts": list(REQUIRED_CONTRACT_ARTIFACTS),
        "completed_contract_artifacts": list(COMPLETED_CONTRACT_ARTIFACTS),
        "pending_contract_artifacts": list(PENDING_CONTRACT_ARTIFACTS),
        "high_risk_gap_areas": list(HIGH_RISK_GAP_AREAS),
        "risk_if_skipped": list(RISK_IF_SKIPPED),
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
