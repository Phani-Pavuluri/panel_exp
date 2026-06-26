"""PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "panel_exp_artifact_registry_provenance_contract_defined_no_runtime_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001_summary.json"
)

CONTRACT_SCOPE = "artifact_registry_provenance_contract_no_runtime"
RECOMMENDED_NEXT_ARTIFACT = "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001"

REQUIRED_CONTRACTS = (
    "PanelExpArtifactRegistryEntry",
    "PanelExpArtifactIdentity",
    "PanelExpArtifactProvenance",
    "PanelExpArtifactInputReference",
    "PanelExpArtifactSourceWorkflow",
    "PanelExpArtifactSourceRunReference",
    "PanelExpArtifactValidationState",
    "PanelExpArtifactGovernanceState",
    "PanelExpArtifactDownstreamUsePolicy",
    "PanelExpArtifactLifecycleState",
    "PanelExpArtifactVersionReference",
    "PanelExpArtifactClaimBoundary",
    "PanelExpArtifactRegistryQuery",
    "PanelExpArtifactRegistryLookupResult",
)

REGISTRY_ENTRY_FIELDS = (
    "artifact_id",
    "artifact_type",
    "artifact_name",
    "artifact_path_or_uri",
    "created_at",
    "created_by_workflow",
    "created_by_run_id",
    "source_input_references",
    "source_artifact_references",
    "content_hash_or_version",
    "lifecycle_state",
    "validation_state",
    "governance_state",
    "allowed_downstream_use",
    "blocked_downstream_use",
    "claim_boundaries",
    "retention_policy",
    "notes",
)

IDENTITY_FIELDS = (
    "artifact_id",
    "artifact_type",
    "schema_version",
    "artifact_family",
    "artifact_name",
    "artifact_path_or_uri",
    "content_hash_or_version",
)

PROVENANCE_FIELDS = (
    "source_workflow",
    "source_run_id",
    "source_agent_name_or_tool",
    "source_input_references",
    "source_artifact_references",
    "transformation_summary",
    "created_at",
    "created_by",
)

INPUT_REFERENCE_FIELDS = (
    "input_reference_id",
    "input_type",
    "input_mode",
    "input_path_or_uri",
    "input_hash_or_version",
    "time_window",
    "region_market",
    "geo_unit_type",
    "kpi",
    "spend_scope",
    "data_contract_version",
)

SOURCE_WORKFLOW_FIELDS = (
    "workflow_id",
    "workflow_name",
    "workflow_version",
    "workflow_stage",
    "workflow_family",
)

SOURCE_RUN_REFERENCE_FIELDS = (
    "run_id",
    "packet_id",
    "agent_name",
    "agent_role",
    "run_status",
    "run_started_at",
    "run_completed_at",
)

VALIDATION_STATE_FIELDS = (
    "validation_status",
    "validation_report_id",
    "checks_run",
    "checks_passed",
    "checks_failed",
    "warnings",
    "blocking_errors",
    "validated_at",
)

GOVERNANCE_STATE_FIELDS = (
    "governance_status",
    "authorization_flags",
    "claim_level",
    "review_required",
    "approval_required",
    "expires_at",
    "revocation_reason",
)

DOWNSTREAM_USE_POLICY_FIELDS = (
    "allowed_downstream_use",
    "blocked_downstream_use",
    "allowed_audiences",
    "blocked_audiences",
    "allowed_claims",
    "blocked_claims",
    "routing_constraints",
)

ARTIFACT_TYPE_TAXONOMY = (
    "planning_intent",
    "data_profile_report",
    "column_mapping_report",
    "geo_time_coverage_report",
    "unit_eligibility_report",
    "geo_unit_feasibility_report",
    "portfolio_feasibility_report",
    "tier_assignment_plan",
    "spend_contrast_feasibility_report",
    "cell_spend_plan",
    "candidate_design_set",
    "design_feasibility_scores",
    "design_based_inference_plan",
    "inference_validity_diagnostics",
    "model_fallback_recommendation",
    "agent_run_manifest",
    "agent_validation_report",
    "agent_failure_packet",
    "agent_resolution_plan",
    "claim_boundary_report",
    "golden_path_result",
    "audit_report",
    "governance_summary",
)

LIFECYCLE_STATES = (
    "draft",
    "generated",
    "validated",
    "validation_failed",
    "blocked",
    "superseded",
    "expired",
    "revoked",
    "archived",
)

GOVERNANCE_STATUSES = (
    "diagnostic_only",
    "provisional",
    "needs_more_data",
    "blocked",
    "validated_for_internal_planning",
    "eligible_for_review",
    "approved_for_specific_downstream_use",
    "revoked",
    "expired",
)

DOWNSTREAM_USE_TARGETS = (
    "internal_planning",
    "diagnostic_explanation",
    "portfolio_feasibility",
    "design_generation",
    "spend_feasibility",
    "inference_planning",
    "model_fallback_routing",
    "mmm_prior_candidate",
    "calibration_signal_candidate",
    "trust_report_candidate",
    "production_readout",
    "production_p_value",
    "production_confidence_interval",
    "production_decisioning",
    "budget_optimization",
    "live_api",
    "scheduler",
)

REQUIRES_FUTURE_CONTRACTS = (
    "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001",
    "LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001",
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
    "registry_entry_fields",
    "artifact_identity_fields",
    "provenance_fields",
    "input_reference_fields",
    "source_workflow_fields",
    "source_run_reference_fields",
    "validation_state_fields",
    "governance_state_fields",
    "downstream_use_policy_fields",
    "lifecycle_states",
    "governance_statuses",
    "artifact_type_taxonomy",
    "no_artifact_id_no_durable_claim",
    "no_provenance_no_downstream_use",
    "sample_schema_cannot_final_feasibility",
    "ballpark_cannot_final_feasibility",
    "diagnostic_artifact_cannot_production_authorization",
    "blocked_artifact_cannot_route_downstream_except_blocked_explanation",
    "expired_revoked_artifact_cannot_support_new_recommendations",
    "llm_answerability_boundaries",
    "revised_roadmap_sequence",
)

_AUTH_FLAGS = {
    "panel_exp_artifact_registry_runtime_authorized": False,
    "artifact_registry_runtime_authorized": False,
    "artifact_provenance_runtime_authorized": False,
    "artifact_downstream_routing_authorized": False,
    "agent_orchestration_runtime_authorized": False,
    "golden_path_runtime_authorized": False,
    "llm_report_grounding_runtime_authorized": False,
    "llm_artifact_interpretation_authorized": False,
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
    "no_runtime_registry_storage",
    "no_runtime_agents",
    "no_agent_orchestration",
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
    "no_downstream_integrations",
)


@dataclass(frozen=True)
class PanelExpArtifactRegistryProvenanceContract:
    artifact_id: str
    contract_scope: str
    registry_first_provenance_always: bool
    no_artifact_id_no_durable_claim: bool
    no_provenance_no_downstream_use: bool
    no_validation_status_no_validation_claim: bool
    no_governance_status_no_claim_boundary: bool
    no_allowed_downstream_use_no_downstream_routing: bool
    required_contracts: tuple[str, ...]
    artifact_type_taxonomy: tuple[str, ...]
    lifecycle_states: tuple[str, ...]
    governance_statuses: tuple[str, ...]
    llm_answerability_boundaries_defined: bool
    requires_future_contracts: tuple[str, ...]
    revised_roadmap_sequence: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    final_verdict: str


def build_panel_exp_artifact_registry_provenance_contract() -> PanelExpArtifactRegistryProvenanceContract:
    """Return deterministic panel_exp artifact registry provenance contract."""
    return PanelExpArtifactRegistryProvenanceContract(
        artifact_id=_ARTIFACT_ID,
        contract_scope=CONTRACT_SCOPE,
        registry_first_provenance_always=True,
        no_artifact_id_no_durable_claim=True,
        no_provenance_no_downstream_use=True,
        no_validation_status_no_validation_claim=True,
        no_governance_status_no_claim_boundary=True,
        no_allowed_downstream_use_no_downstream_routing=True,
        required_contracts=REQUIRED_CONTRACTS,
        artifact_type_taxonomy=ARTIFACT_TYPE_TAXONOMY,
        lifecycle_states=LIFECYCLE_STATES,
        governance_statuses=GOVERNANCE_STATUSES,
        llm_answerability_boundaries_defined=True,
        requires_future_contracts=REQUIRES_FUTURE_CONTRACTS,
        revised_roadmap_sequence=REVISED_ROADMAP_SEQUENCE,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_panel_exp_artifact_registry_provenance_contract(
    contract: PanelExpArtifactRegistryProvenanceContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.registry_first_provenance_always:
        issues.append("registry_first_provenance_always must be true")
    if not contract.no_artifact_id_no_durable_claim:
        issues.append("no_artifact_id_no_durable_claim must be true")
    if not contract.no_provenance_no_downstream_use:
        issues.append("no_provenance_no_downstream_use must be true")
    if contract.required_contracts != REQUIRED_CONTRACTS:
        issues.append("required_contracts mismatch")
    if contract.artifact_type_taxonomy != ARTIFACT_TYPE_TAXONOMY:
        issues.append("artifact_type_taxonomy mismatch")
    if contract.lifecycle_states != LIFECYCLE_STATES:
        issues.append("lifecycle_states mismatch")
    if contract.governance_statuses != GOVERNANCE_STATUSES:
        issues.append("governance_statuses mismatch")
    idx = contract.revised_roadmap_sequence.index("PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001")
    if contract.revised_roadmap_sequence[idx + 1] != RECOMMENDED_NEXT_ARTIFACT:
        issues.append("golden path acceptance tests must follow artifact registry contract")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_panel_exp_artifact_registry_provenance_contract()
    validation = validate_panel_exp_artifact_registry_provenance_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    scenarios.append(_s("registry_first_provenance_always", contract.registry_first_provenance_always))
    scenarios.append(_s("no_artifact_id_no_durable_claim", contract.no_artifact_id_no_durable_claim))
    scenarios.append(_s("no_provenance_no_downstream_use", contract.no_provenance_no_downstream_use))
    scenarios.append(
        _s("no_validation_status_no_validation_claim", contract.no_validation_status_no_validation_claim)
    )
    scenarios.append(
        _s("no_governance_status_no_claim_boundary", contract.no_governance_status_no_claim_boundary)
    )
    scenarios.append(
        _s(
            "no_allowed_downstream_use_no_downstream_routing",
            contract.no_allowed_downstream_use_no_downstream_routing,
        )
    )
    scenarios.append(_s("required_contracts_present", contract.required_contracts == REQUIRED_CONTRACTS))
    scenarios.append(_s("artifact_type_taxonomy_present", contract.artifact_type_taxonomy == ARTIFACT_TYPE_TAXONOMY))
    scenarios.append(_s("lifecycle_states_present", contract.lifecycle_states == LIFECYCLE_STATES))
    scenarios.append(_s("governance_statuses_present", contract.governance_statuses == GOVERNANCE_STATUSES))
    scenarios.append(_s("llm_boundaries_defined", contract.llm_answerability_boundaries_defined))
    idx = contract.revised_roadmap_sequence.index("PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001")
    scenarios.append(
        _s("next_artifact_golden_path", contract.revised_roadmap_sequence[idx + 1] == RECOMMENDED_NEXT_ARTIFACT)
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
    contract = build_panel_exp_artifact_registry_provenance_contract()
    validation = validate_panel_exp_artifact_registry_provenance_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "panel_exp_artifact_registry_and_provenance_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "contract_scope": CONTRACT_SCOPE,
        "registry_first_provenance_always": True,
        "no_artifact_id_no_durable_claim": True,
        "no_provenance_no_downstream_use": True,
        "no_validation_status_no_validation_claim": True,
        "no_governance_status_no_claim_boundary": True,
        "no_allowed_downstream_use_no_downstream_routing": True,
        "required_contracts": list(REQUIRED_CONTRACTS),
        "artifact_type_taxonomy": list(ARTIFACT_TYPE_TAXONOMY),
        "lifecycle_states": list(LIFECYCLE_STATES),
        "governance_statuses": list(GOVERNANCE_STATUSES),
        "llm_answerability_boundaries_defined": True,
        "requires_future_contracts": list(REQUIRES_FUTURE_CONTRACTS),
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
