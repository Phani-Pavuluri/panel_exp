"""SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

_ARTIFACT_ID = "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "scm_release_gate_decision_plan_defined_defer_no_authorization_granted"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001",
)

METHOD_FAMILY = "SCM"
METHOD_FAMILY_STATUS = "production_candidate_gated"
INPUT_CONTRACT = "SCMReleaseGateDecisionInput"
DECISION_CONTRACT = "SCMReleaseGateDecisionPlan"

RECOMMENDED_DECISION_DIRECTION = "defer_pending_empirical_validation"
PLANNED_CLOSEOUT_DIRECTION = "closeout_as_reference_candidate"
PORTFOLIO_HANDOFF_RECOMMENDATION = "handoff_to_method_portfolio"

_AUTH_FLAGS = {
    "scm_production_p_value_authorized": False,
    "scm_causal_confidence_interval_authorized": False,
    "production_authorization_granted": False,
    "production_p_value_authorized": False,
    "causal_confidence_interval_authorized": False,
    "trustreport_authorized": False,
    "calibration_signal_allowed": False,
    "mmm_ingestion_allowed": False,
    "llm_decisioning_allowed": False,
    "production_decisioning_allowed": False,
    "live_api_authorized": False,
    "scheduler_authorized": False,
    "budget_optimization_allowed": False,
    "data_driven_selection_gate_implementation_authorized": False,
    "selector_implementation_authorized": False,
    "production_selection_router_authorized": False,
    "scm_production_inference_authorized": False,
    "multicell_production_claim_authorized": False,
    "package_side_agents_authorized": False,
    "augsynth_production_inference_authorized": False,
    "tbrridge_production_inference_authorized": False,
    "bayesian_tbr_production_inference_authorized": False,
}

_SCM_FLAGS = {
    "scm_release_gate_decision_plan_completed": False,
    "scm_release_gate_approval_granted": False,
    "scm_production_inference_authorized": False,
}

DECISION_OPTIONS = (
    "approve_limited_production",
    "approve_shadow_only",
    "defer_pending_empirical_validation",
    "reject_production_authorization",
    "closeout_as_reference_candidate",
    "handoff_to_method_portfolio",
)

DECISION_STATUSES = DECISION_OPTIONS

INPUT_FIELDS = (
    "review_packet",
    "method_family_status",
    "evidence_stack_status",
    "empirical_validation_state",
    "null_calibration_state",
    "jackknife_sensitivity_state",
    "simulation_dgp_state",
    "failure_registry_state",
    "assignment_design_validity_state",
    "multicell_validation_state",
    "selector_shadow_validation_state",
    "human_review_state",
    "rollback_revocation_policy_state",
    "portfolio_handoff_state",
    "audit_context",
)

DECISION_PLAN_FIELDS = (
    "planned_decision_options",
    "recommended_decision_direction",
    "blocked_approval_reasons",
    "required_empirical_evidence",
    "current_allowed_use",
    "current_forbidden_use",
    "portfolio_handoff_recommendation",
    "next_artifact",
    "authorization_flags",
    "audit_references",
    "final_verdict",
)

REQUIRED_EMPIRICAL_EVIDENCE_BEFORE_APPROVAL = (
    "observed_panel_validation_results",
    "empirical_placebo_null_calibration_results",
    "jackknife_sensitivity_results",
    "donor_support_and_convex_hull_results",
    "pre_period_fit_and_trend_results",
    "failure_registry_review_results",
    "simulation_dgp_coverage_results",
    "assignment_design_validity_results",
    "multicell_dependence_multiplicity_results_where_applicable",
    "selector_shadow_validation_results_where_applicable",
    "human_governance_review_result",
    "rollback_revocation_expiration_policy",
)

BLOCKED_APPROVAL_REASONS = (
    "SCM-RG-DEC-BR-METADATA-ONLY-EVIDENCE",
    "SCM-RG-DEC-BR-NO-EMPIRICAL-VALIDATION",
    "SCM-RG-DEC-BR-NO-EMPIRICAL-NULL-CALIBRATION",
    "SCM-RG-DEC-BR-NO-EMPIRICAL-JACKKNIFE",
    "SCM-RG-DEC-BR-P-VALUE-NOT-AUTHORIZED",
    "SCM-RG-DEC-BR-CAUSAL-CI-NOT-AUTHORIZED",
    "SCM-RG-DEC-BR-PRODUCTION-INFERENCE-NOT-AUTHORIZED",
    "SCM-RG-DEC-BR-MULTICELL-BLOCKED",
    "SCM-RG-DEC-BR-SELECTOR-ROUTER-NOT-AUTHORIZED",
    "SCM-RG-DEC-BR-DOWNSTREAM-NOT-AUTHORIZED",
    "SCM-RG-DEC-BR-HUMAN-GOVERNANCE-INCOMPLETE",
    "SCM-RG-DEC-BR-ROLLBACK-POLICY-INCOMPLETE",
    "SCM-RG-DEC-BR-PORTFOLIO-HANDOFF-REQUIRED",
)

METHOD_PORTFOLIO_HANDOFF_TARGETS = (
    "AugSynth/ASCM",
    "TBRRidge",
    "Bayesian TBR",
)

PORTFOLIO_HANDOFF_RATIONALE = {
    "AugSynth/ASCM": (
        "stronger_candidate_residual_correction",
        "needs_residual_model_governance_and_remediation_validation",
        "not_production_authorized",
    ),
    "TBRRidge": (
        "practical_geo_diagnostic_restricted_workhorse",
        "inference_validity_unresolved",
        "not_production_authorized",
    ),
    "Bayesian TBR": (
        "useful_when_governed_priors_exist",
        "posterior_intervals_not_causal_cis",
        "prior_compatibility_must_be_governed",
        "not_production_authorized",
    ),
}

CURRENT_ALLOWED_USE = (
    "governed_reference_candidate",
    "validation_baseline_metadata",
    "release_gate_review_input",
    "selector_shadow_non_authorizing_input",
    "audit_traceability",
    "method_portfolio_comparison_baseline",
)

CURRENT_FORBIDDEN_USE = (
    "production_inference",
    "production_p_values",
    "causal_confidence_intervals",
    "release_gate_approval",
    "approve_limited_production",
    "selector_router_production_routing",
    "multicell_production_claims",
    "trustreport_authorization",
    "calibration_signal_authorization",
    "mmm_ingestion_authorization",
    "llm_decisioning_authorization",
    "live_api_authorization",
    "scheduler_authorization",
    "budget_optimization_authorization",
    "package_side_agent_authorization",
)

DEPENDENCIES_RECONCILED = (
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001",
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001",
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
    "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001",
    "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
    "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",
    "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
    "PRODUCTION_READINESS_BACKLOG_LEDGER_001",
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
    "FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001",
)

NON_GOALS = (
    "no_release_gate_approval_granted",
    "no_release_gate_decision_execution",
    "no_scm_production_inference_authorization",
    "no_production_p_values_or_causal_cis",
    "no_approve_limited_production_for_current_evidence",
    "no_selector_router_production_use",
    "no_multicell_scm_production_claims",
    "no_trustreport_calibration_signal_mmm",
    "no_live_api_scheduler_budget",
    "no_package_side_agent_authorization",
    "no_augsynth_tbrridge_bayesian_tbr_production_authorization",
    "no_automatic_authorization_from_decision_plan",
)

_BOUNDARY_FLAGS = {
    "prior_work_reconciled": True,
    "scm_remains_gated_production_candidate": True,
    "decision_plan_not_release_gate_approval": True,
    "evidence_stack_metadata_only": True,
    "defer_pending_empirical_validation": True,
    "closeout_as_reference_candidate_planned": True,
    "portfolio_handoff_required": True,
    "human_governance_review_required": True,
    "revocation_expiration_rollback_required_before_authorization": True,
    "package_side_agents_deferred": True,
    "resolved_artifacts_do_not_mean_production_ready": True,
    "decision_plan_only_no_runtime": True,
    "downstream_work_paused": True,
}


class DecisionOption(str, Enum):
    APPROVE_LIMITED_PRODUCTION = "approve_limited_production"
    APPROVE_SHADOW_ONLY = "approve_shadow_only"
    DEFER_PENDING_EMPIRICAL_VALIDATION = "defer_pending_empirical_validation"
    REJECT_PRODUCTION_AUTHORIZATION = "reject_production_authorization"
    CLOSEOUT_AS_REFERENCE_CANDIDATE = "closeout_as_reference_candidate"
    HANDOFF_TO_METHOD_PORTFOLIO = "handoff_to_method_portfolio"


@dataclass(frozen=True)
class SCMReleaseGateDecisionInput:
    review_packet: Mapping[str, Any] = field(default_factory=dict)
    method_family_status: str = METHOD_FAMILY_STATUS
    evidence_stack_status: str = "metadata_scaffold_present"
    empirical_validation_state: Mapping[str, Any] = field(default_factory=dict)
    null_calibration_state: Mapping[str, Any] = field(default_factory=dict)
    jackknife_sensitivity_state: Mapping[str, Any] = field(default_factory=dict)
    simulation_dgp_state: Mapping[str, Any] = field(default_factory=dict)
    failure_registry_state: Mapping[str, Any] = field(default_factory=dict)
    assignment_design_validity_state: Mapping[str, Any] = field(default_factory=dict)
    multicell_validation_state: Mapping[str, Any] = field(default_factory=dict)
    selector_shadow_validation_state: Mapping[str, Any] = field(default_factory=dict)
    human_review_state: Mapping[str, Any] = field(default_factory=dict)
    rollback_revocation_policy_state: Mapping[str, Any] = field(default_factory=dict)
    portfolio_handoff_state: Mapping[str, Any] = field(default_factory=dict)
    audit_context: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SCMReleaseGateDecisionPlan:
    planned_decision_options: tuple[str, ...]
    recommended_decision_direction: str
    planned_closeout_direction: str
    portfolio_handoff_recommendation: str
    blocked_approval_reasons: tuple[str, ...]
    required_empirical_evidence: tuple[str, ...]
    current_allowed_use: tuple[str, ...]
    current_forbidden_use: tuple[str, ...]
    method_portfolio_handoff_targets: tuple[str, ...]
    portfolio_handoff_rationale: dict[str, tuple[str, ...]]
    next_artifact: str
    authorization_flags: dict[str, bool]
    audit_references: tuple[str, ...]
    final_verdict: str


def build_scm_release_gate_decision_plan(
    inp: SCMReleaseGateDecisionInput | None = None,
) -> SCMReleaseGateDecisionPlan:
    """Build deterministic SCM release-gate decision plan (non-authorizing)."""
    inp = inp or SCMReleaseGateDecisionInput()
    blocked = list(BLOCKED_APPROVAL_REASONS)

    if inp.evidence_stack_status == "metadata_scaffold_present":
        blocked.append("SCM-RG-DEC-BR-METADATA-ONLY-EVIDENCE")
    if not inp.empirical_validation_state.get("complete", False):
        blocked.append("SCM-RG-DEC-BR-NO-EMPIRICAL-VALIDATION")
    if not inp.null_calibration_state.get("empirical_complete", False):
        blocked.append("SCM-RG-DEC-BR-NO-EMPIRICAL-NULL-CALIBRATION")
    if not inp.jackknife_sensitivity_state.get("empirical_complete", False):
        blocked.append("SCM-RG-DEC-BR-NO-EMPIRICAL-JACKKNIFE")

    audit_refs = (
        "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001",
        "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001",
        "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",
        "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",
        "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001",
        _ARTIFACT_ID,
    )

    return SCMReleaseGateDecisionPlan(
        planned_decision_options=DECISION_OPTIONS,
        recommended_decision_direction=RECOMMENDED_DECISION_DIRECTION,
        planned_closeout_direction=PLANNED_CLOSEOUT_DIRECTION,
        portfolio_handoff_recommendation=PORTFOLIO_HANDOFF_RECOMMENDATION,
        blocked_approval_reasons=tuple(dict.fromkeys(blocked)),
        required_empirical_evidence=REQUIRED_EMPIRICAL_EVIDENCE_BEFORE_APPROVAL,
        current_allowed_use=CURRENT_ALLOWED_USE,
        current_forbidden_use=CURRENT_FORBIDDEN_USE,
        method_portfolio_handoff_targets=METHOD_PORTFOLIO_HANDOFF_TARGETS,
        portfolio_handoff_rationale=PORTFOLIO_HANDOFF_RATIONALE,
        next_artifact=RECOMMENDED_NEXT_ARTIFACTS[0],
        authorization_flags=dict(_AUTH_FLAGS),
        audit_references=audit_refs,
        final_verdict=_VERDICT,
    )


def validate_scm_release_gate_decision_plan(plan: SCMReleaseGateDecisionPlan) -> dict[str, Any]:
    """Validate decision plan coverage and authorization boundary."""
    issues: list[str] = []

    if set(plan.planned_decision_options) != set(DECISION_OPTIONS):
        issues.append("planned_decision_options mismatch")
    if plan.recommended_decision_direction != RECOMMENDED_DECISION_DIRECTION:
        issues.append("recommended_decision_direction must be defer_pending_empirical_validation")
    if plan.planned_closeout_direction != PLANNED_CLOSEOUT_DIRECTION:
        issues.append("planned_closeout_direction must be closeout_as_reference_candidate")
    if plan.portfolio_handoff_recommendation != PORTFOLIO_HANDOFF_RECOMMENDATION:
        issues.append("portfolio_handoff_recommendation mismatch")
    for evidence in REQUIRED_EMPIRICAL_EVIDENCE_BEFORE_APPROVAL:
        if evidence not in plan.required_empirical_evidence:
            issues.append(f"missing required empirical evidence: {evidence}")
    for reason in BLOCKED_APPROVAL_REASONS:
        if reason not in plan.blocked_approval_reasons:
            issues.append(f"missing blocked approval reason: {reason}")
    for flag, expected in _AUTH_FLAGS.items():
        if plan.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    if RECOMMENDED_DECISION_DIRECTION == "approve_limited_production":
        issues.append("must not recommend approve_limited_production for current evidence")

    return {
        "valid": not issues,
        "decision_option_count": len(plan.planned_decision_options),
        "empirical_evidence_count": len(plan.required_empirical_evidence),
        "blocked_reason_count": len(plan.blocked_approval_reasons),
        "all_decision_options_present": set(plan.planned_decision_options) == set(DECISION_OPTIONS),
        "issues": issues,
    }


def build_scenarios() -> list[dict[str, Any]]:
    plan = build_scm_release_gate_decision_plan()
    validation = validate_scm_release_gate_decision_plan(plan)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool, detail: str = "") -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": detail}

    for option in DECISION_OPTIONS:
        scenarios.append(_s(f"decision_option_{option}_defined", option in plan.planned_decision_options))

    for field_name in INPUT_FIELDS:
        scenarios.append(_s(f"input_field_{field_name}_defined", field_name in INPUT_FIELDS))

    for field_name in DECISION_PLAN_FIELDS:
        scenarios.append(_s(f"decision_plan_field_{field_name}_defined", hasattr(plan, field_name)))

    for evidence in REQUIRED_EMPIRICAL_EVIDENCE_BEFORE_APPROVAL:
        scenarios.append(_s(
            f"empirical_evidence_{evidence}_required",
            evidence in plan.required_empirical_evidence,
        ))

    for reason in BLOCKED_APPROVAL_REASONS:
        scenarios.append(_s(f"blocked_reason_{reason}_present", reason in plan.blocked_approval_reasons))

    scenarios.append(_s(
        "recommended_direction_defer",
        plan.recommended_decision_direction == "defer_pending_empirical_validation",
    ))
    scenarios.append(_s(
        "closeout_reference_candidate",
        plan.planned_closeout_direction == "closeout_as_reference_candidate",
    ))
    scenarios.append(_s(
        "portfolio_handoff_present",
        plan.portfolio_handoff_recommendation == "handoff_to_method_portfolio",
    ))
    scenarios.append(_s("release_gate_approval_false", _SCM_FLAGS["scm_release_gate_approval_granted"] is False))
    scenarios.append(_s("production_inference_false", not plan.authorization_flags["scm_production_inference_authorized"]))
    scenarios.append(_s("p_value_false", not plan.authorization_flags["scm_production_p_value_authorized"]))
    scenarios.append(_s("causal_ci_false", not plan.authorization_flags["scm_causal_confidence_interval_authorized"]))
    scenarios.append(_s("selector_router_false", not plan.authorization_flags["selector_implementation_authorized"]))
    scenarios.append(_s("multicell_false", not plan.authorization_flags["multicell_production_claim_authorized"]))
    scenarios.append(_s("downstream_false", not plan.authorization_flags["trustreport_authorized"]))
    scenarios.append(_s("augsynth_false", not plan.authorization_flags["augsynth_production_inference_authorized"]))
    scenarios.append(_s("tbrridge_false", not plan.authorization_flags["tbrridge_production_inference_authorized"]))
    scenarios.append(_s("bayesian_tbr_false", not plan.authorization_flags["bayesian_tbr_production_inference_authorized"]))
    scenarios.append(_s("not_approve_limited_production", plan.recommended_decision_direction != "approve_limited_production"))
    scenarios.append(_s("final_verdict_matches", plan.final_verdict == _VERDICT))
    scenarios.append(_s("validation_valid", validation["valid"]))
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not plan.authorization_flags[flag]))
    scenarios.append(_s("failed_scenarios_empty", all(x["passed"] for x in scenarios)))
    return scenarios


def _git_commit() -> str | None:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=_REPO,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    plan = build_scm_release_gate_decision_plan()
    validation = validate_scm_release_gate_decision_plan(plan)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "scm_release_gate_decision_plan_metadata_only",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "method_family": METHOD_FAMILY,
        "method_family_status": METHOD_FAMILY_STATUS,
        "recommended_decision_direction": RECOMMENDED_DECISION_DIRECTION,
        "planned_closeout_direction": PLANNED_CLOSEOUT_DIRECTION,
        "portfolio_handoff_recommendation": PORTFOLIO_HANDOFF_RECOMMENDATION,
        "next_artifact": RECOMMENDED_NEXT_ARTIFACTS[0],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        "planned_decision_options": list(DECISION_OPTIONS),
        "required_empirical_evidence_before_approval": list(REQUIRED_EMPIRICAL_EVIDENCE_BEFORE_APPROVAL),
        "blocked_approval_reasons": list(plan.blocked_approval_reasons),
        "method_portfolio_handoff_targets": list(METHOD_PORTFOLIO_HANDOFF_TARGETS),
        "planned_input_contract": INPUT_CONTRACT,
        "planned_decision_contract": DECISION_CONTRACT,
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
        "scm_release_gate_decision_plan_completed": False,
        "scm_release_gate_approval_granted": False,
        "scm_production_inference_authorized": False,
        "authorization_flags": dict(_AUTH_FLAGS),
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
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
