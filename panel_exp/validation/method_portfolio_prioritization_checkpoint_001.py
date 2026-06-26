"""METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "method_portfolio_prioritization_checkpoint_logged_no_production_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001_summary.json"

STRATEGIC_DECISION = "shift_primary_method_focus_from_scm_to_augsynth_ascm_after_scm_closeout"
SCM_FUTURE_ROLE = "governed_reference_candidate_and_validation_baseline"

RECOMMENDED_NEXT_SCM_ARTIFACT = "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001"
POST_SCM_HANDOFF_ARTIFACT = "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001"
FIRST_POST_SCM_METHOD_LANE = "AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001"

PRIORITY_ORDER = (
    "complete_scm_decision_plan_and_closeout_without_production_approval",
    "augsynth_ascm_point_estimate_production_candidate_validation",
    "tbrridge_point_estimate_validation",
    "shared_inference_validation_framework_for_pvalues_and_cis",
    "bayesian_tbr_governed_prior_posterior_lane",
    "trop_deferred_until_decisioning_governance_mature",
)

METHOD_STANCES = {
    "SCM": "reference_candidate_not_primary_focus",
    "AugSynth_ASCM": "next_primary_candidate_lane",
    "TBRRidge": "later_practical_point_estimate_lane",
    "Bayesian_TBR": "governed_prior_research_calibration_lane",
    "TROP": "deferred_research_decisioning_lane",
}

SEPARATED_AUTHORIZATION_MODEL = {
    "point_estimates_separate_from_p_values": True,
    "p_values_separate_from_causal_cis": True,
    "causal_cis_separate_from_selector_router": True,
    "selector_router_separate_from_downstream_decisioning": True,
}

_AUTH_FLAGS = {
    "scm_production_inference_authorized": False,
    "scm_production_p_value_authorized": False,
    "scm_causal_confidence_interval_authorized": False,
    "augsynth_production_inference_authorized": False,
    "augsynth_production_p_value_authorized": False,
    "augsynth_causal_confidence_interval_authorized": False,
    "tbrridge_production_inference_authorized": False,
    "tbrridge_production_p_value_authorized": False,
    "tbrridge_causal_confidence_interval_authorized": False,
    "bayesian_tbr_production_inference_authorized": False,
    "bayesian_tbr_production_p_value_authorized": False,
    "bayesian_tbr_causal_confidence_interval_authorized": False,
    "trop_production_decisioning_authorized": False,
    "production_authorization_granted": False,
    "production_p_value_authorized": False,
    "causal_confidence_interval_authorized": False,
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

DEPENDENCIES_RECONCILED = (
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001",
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001",
    "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001",
    "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
    "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",
    "TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001",
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
)

NON_GOALS = (
    "no_estimator_implementation",
    "no_method_production_approval",
    "no_runtime_behavior_change",
    "no_scm_production_approval_from_metadata",
    "no_augsynth_tbrridge_bayesian_tbr_trop_authorization",
    "no_downstream_integration_authorization",
)


@dataclass(frozen=True)
class MethodPortfolioPrioritizationCheckpoint:
    artifact_id: str
    strategic_decision: str
    scm_future_role: str
    scm_production_approval_recommended: bool
    priority_order: tuple[str, ...]
    method_stances: dict[str, str]
    separated_authorization_model: dict[str, bool]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    post_scm_handoff_artifact: str
    first_post_scm_method_lane: str
    final_verdict: str


def build_method_portfolio_prioritization_checkpoint() -> MethodPortfolioPrioritizationCheckpoint:
    """Return deterministic method portfolio prioritization checkpoint."""
    return MethodPortfolioPrioritizationCheckpoint(
        artifact_id=_ARTIFACT_ID,
        strategic_decision=STRATEGIC_DECISION,
        scm_future_role=SCM_FUTURE_ROLE,
        scm_production_approval_recommended=False,
        priority_order=PRIORITY_ORDER,
        method_stances=dict(METHOD_STANCES),
        separated_authorization_model=dict(SEPARATED_AUTHORIZATION_MODEL),
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_SCM_ARTIFACT,
        post_scm_handoff_artifact=POST_SCM_HANDOFF_ARTIFACT,
        first_post_scm_method_lane=FIRST_POST_SCM_METHOD_LANE,
        final_verdict=_VERDICT,
    )


def validate_method_portfolio_prioritization_checkpoint(
    checkpoint: MethodPortfolioPrioritizationCheckpoint,
) -> dict[str, Any]:
    issues: list[str] = []
    if checkpoint.scm_production_approval_recommended:
        issues.append("scm_production_approval_recommended must be false")
    if checkpoint.method_stances.get("SCM") != "reference_candidate_not_primary_focus":
        issues.append("SCM stance must be reference_candidate_not_primary_focus")
    if checkpoint.method_stances.get("AugSynth_ASCM") != "next_primary_candidate_lane":
        issues.append("AugSynth_ASCM must be next_primary_candidate_lane")
    if checkpoint.priority_order[0] != PRIORITY_ORDER[0]:
        issues.append("priority 0 must be SCM closeout without production approval")
    for flag, expected in _AUTH_FLAGS.items():
        if checkpoint.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    cp = build_method_portfolio_prioritization_checkpoint()
    validation = validate_method_portfolio_prioritization_checkpoint(cp)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for idx, _ in enumerate(PRIORITY_ORDER):
        scenarios.append(_s(f"priority_{idx}_present", idx < len(cp.priority_order)))

    scenarios.append(_s("scm_reference_not_primary", cp.method_stances["SCM"] == "reference_candidate_not_primary_focus"))
    scenarios.append(_s("augsynth_next_primary", cp.method_stances["AugSynth_ASCM"] == "next_primary_candidate_lane"))
    scenarios.append(_s("tbrridge_later_lane", cp.method_stances["TBRRidge"] == "later_practical_point_estimate_lane"))
    scenarios.append(_s("bayesian_tbr_research_lane", cp.method_stances["Bayesian_TBR"] == "governed_prior_research_calibration_lane"))
    scenarios.append(_s("trop_deferred", cp.method_stances["TROP"] == "deferred_research_decisioning_lane"))
    scenarios.append(_s("separated_auth_model", all(cp.separated_authorization_model.values())))
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not cp.authorization_flags[flag]))
    scenarios.append(_s("recommended_next_scm_artifact", bool(cp.recommended_next_artifact)))
    scenarios.append(_s("first_post_scm_augsynth", cp.first_post_scm_method_lane == FIRST_POST_SCM_METHOD_LANE))
    scenarios.append(_s("scm_production_approval_not_recommended", not cp.scm_production_approval_recommended))
    scenarios.append(_s("final_verdict_matches", cp.final_verdict == _VERDICT))
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
    cp = build_method_portfolio_prioritization_checkpoint()
    validation = validate_method_portfolio_prioritization_checkpoint(cp)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "method_portfolio_prioritization_checkpoint",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "strategic_decision": STRATEGIC_DECISION,
        "scm_future_role": SCM_FUTURE_ROLE,
        "scm_production_approval_recommended": False,
        "priority_order": list(PRIORITY_ORDER),
        "separated_authorization_model": dict(SEPARATED_AUTHORIZATION_MODEL),
        "method_stances": dict(METHOD_STANCES),
        "authorization_flags": dict(_AUTH_FLAGS),
        "recommended_next_artifact": RECOMMENDED_NEXT_SCM_ARTIFACT,
        "post_scm_handoff_artifact": POST_SCM_HANDOFF_ARTIFACT,
        "first_post_scm_method_lane": FIRST_POST_SCM_METHOD_LANE,
        "scm_decision_plan_completed": True,
        "scm_decision_plan_artifact": "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
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
