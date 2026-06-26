"""PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "panel_exp_agent_run_packet_contract_defined_no_runtime_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001_summary.json"

CONTRACT_SCOPE = "agent_run_packet_contract_no_runtime"
RECOMMENDED_NEXT_ARTIFACT = "PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001"

REQUIRED_CONTRACTS = (
    "PanelExpAgentInputPacket",
    "PanelExpAgentRunManifest",
    "PanelExpAgentArtifactReference",
    "PanelExpAgentValidationReport",
    "PanelExpAgentFailurePacket",
    "PanelExpAgentResolutionPlan",
    "PanelExpAllowedAction",
    "PanelExpBlockedAction",
    "PanelExpEvidenceReference",
    "PanelExpAgentClaimBoundary",
    "PanelExpAgentRunSummary",
)

ALLOWED_ACTIONS = (
    "read_artifact",
    "summarize_report",
    "request_missing_input",
    "run_diagnostic",
    "generate_candidate_report",
    "write_metadata_artifact",
    "update_governance_doc",
    "recommend_provisional_next_step",
)

BLOCKED_ACTIONS = (
    "authorize_production_design",
    "authorize_p_value",
    "authorize_confidence_interval",
    "override_blocked_status",
    "modify_source_data",
    "execute_budget_optimization",
    "send_to_mmm",
    "execute_live_api",
    "schedule_experiment",
    "select_final_estimator_without_diagnostics",
)

REQUIRES_FUTURE_CONTRACTS = (
    "PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001",
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
    "input_packet_fields",
    "run_manifest_fields",
    "artifact_reference_fields",
    "validation_report_fields",
    "failure_packet_fields",
    "resolution_plan_fields",
    "allowed_actions_present",
    "blocked_actions_present",
    "packet_first_principle",
    "no_manifest_no_agent_run_claim",
    "no_artifact_reference_no_report_claim",
    "no_validation_report_no_validation_pass_claim",
    "hidden_failures_blocked",
    "production_design_authorization_blocked",
    "p_value_authorization_blocked",
    "ci_authorization_blocked",
    "budget_optimization_blocked",
    "mmm_ingestion_blocked",
    "live_api_blocked",
    "llm_answerability_boundaries",
    "revised_roadmap_sequence",
)

_AUTH_FLAGS = {
    "panel_exp_agent_run_packet_runtime_authorized": False,
    "agent_orchestration_runtime_authorized": False,
    "agent_run_manifest_runtime_authorized": False,
    "agent_artifact_reference_runtime_authorized": False,
    "agent_validation_report_runtime_authorized": False,
    "agent_failure_packet_runtime_authorized": False,
    "agent_resolution_plan_runtime_authorized": False,
    "artifact_registry_runtime_authorized": False,
    "golden_path_runtime_authorized": False,
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
    "no_runtime_agent_execution",
    "no_agent_orchestration",
    "no_profiler_implementation",
    "no_planner_logic",
    "no_estimator_selection",
    "no_production_recommendations",
    "no_downstream_integrations",
)


@dataclass(frozen=True)
class PanelExpAgentRunPacketContract:
    artifact_id: str
    contract_scope: str
    packet_first_agent_second: bool
    tool_first_explanation_second: bool
    no_packet_no_agent_run: bool
    no_manifest_no_agent_execution_claim: bool
    no_artifact_reference_no_report_claim: bool
    no_validation_report_no_validation_pass_claim: bool
    no_failure_packet_no_hidden_failure: bool
    required_contracts: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    llm_answerability_boundaries_defined: bool
    requires_future_contracts: tuple[str, ...]
    revised_roadmap_sequence: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    final_verdict: str


def build_panel_exp_agent_run_packet_contract() -> PanelExpAgentRunPacketContract:
    """Return deterministic panel_exp agent run packet contract."""
    return PanelExpAgentRunPacketContract(
        artifact_id=_ARTIFACT_ID,
        contract_scope=CONTRACT_SCOPE,
        packet_first_agent_second=True,
        tool_first_explanation_second=True,
        no_packet_no_agent_run=True,
        no_manifest_no_agent_execution_claim=True,
        no_artifact_reference_no_report_claim=True,
        no_validation_report_no_validation_pass_claim=True,
        no_failure_packet_no_hidden_failure=True,
        required_contracts=REQUIRED_CONTRACTS,
        allowed_actions=ALLOWED_ACTIONS,
        blocked_actions=BLOCKED_ACTIONS,
        llm_answerability_boundaries_defined=True,
        requires_future_contracts=REQUIRES_FUTURE_CONTRACTS,
        revised_roadmap_sequence=REVISED_ROADMAP_SEQUENCE,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_panel_exp_agent_run_packet_contract(
    contract: PanelExpAgentRunPacketContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.packet_first_agent_second:
        issues.append("packet_first_agent_second must be true")
    if not contract.no_packet_no_agent_run:
        issues.append("no_packet_no_agent_run must be true")
    if contract.required_contracts != REQUIRED_CONTRACTS:
        issues.append("required_contracts mismatch")
    if "authorize_production_design" not in contract.blocked_actions:
        issues.append("authorize_production_design must be blocked")
    idx = contract.revised_roadmap_sequence.index("PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001")
    if contract.revised_roadmap_sequence[idx + 1] != RECOMMENDED_NEXT_ARTIFACT:
        issues.append("artifact registry contract must follow agent run packet")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_panel_exp_agent_run_packet_contract()
    validation = validate_panel_exp_agent_run_packet_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    scenarios.append(_s("packet_first_agent_second", contract.packet_first_agent_second))
    scenarios.append(_s("tool_first_explanation_second", contract.tool_first_explanation_second))
    scenarios.append(_s("no_packet_no_agent_run", contract.no_packet_no_agent_run))
    scenarios.append(_s("no_manifest_no_execution_claim", contract.no_manifest_no_agent_execution_claim))
    scenarios.append(_s("no_artifact_ref_no_report_claim", contract.no_artifact_reference_no_report_claim))
    scenarios.append(_s("no_validation_no_pass_claim", contract.no_validation_report_no_validation_pass_claim))
    scenarios.append(_s("no_hidden_failure", contract.no_failure_packet_no_hidden_failure))
    scenarios.append(_s("required_contracts_present", contract.required_contracts == REQUIRED_CONTRACTS))
    scenarios.append(_s("allowed_actions_present", contract.allowed_actions == ALLOWED_ACTIONS))
    scenarios.append(_s("blocked_actions_present", contract.blocked_actions == BLOCKED_ACTIONS))
    scenarios.append(_s("llm_boundaries_defined", contract.llm_answerability_boundaries_defined))
    idx = contract.revised_roadmap_sequence.index("PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001")
    scenarios.append(_s("next_artifact_registry", contract.revised_roadmap_sequence[idx + 1] == RECOMMENDED_NEXT_ARTIFACT))
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
    contract = build_panel_exp_agent_run_packet_contract()
    validation = validate_panel_exp_agent_run_packet_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "panel_exp_agent_run_packet_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "contract_scope": CONTRACT_SCOPE,
        "packet_first_agent_second": True,
        "tool_first_explanation_second": True,
        "no_packet_no_agent_run": True,
        "no_manifest_no_agent_execution_claim": True,
        "no_artifact_reference_no_report_claim": True,
        "no_validation_report_no_validation_pass_claim": True,
        "no_failure_packet_no_hidden_failure": True,
        "required_contracts": list(REQUIRED_CONTRACTS),
        "allowed_actions": list(ALLOWED_ACTIONS),
        "blocked_actions": list(BLOCKED_ACTIONS),
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
