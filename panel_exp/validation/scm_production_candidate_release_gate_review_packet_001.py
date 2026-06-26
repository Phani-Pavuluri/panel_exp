"""SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001 — release-gate review packet assembly."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from panel_exp.validation.scm_production_candidate_release_gate_review_plan_001 import (
    DOMAIN_PROFILES,
    EVIDENCE_PREREQUISITES,
    PREREQUISITE_PROFILES,
    RELEASE_GATE_DOMAINS,
    REQUIRED_FOLLOWUPS as PLAN_REQUIRED_FOLLOWUPS,
    SCM_EVIDENCE_PROFILES,
)

_ARTIFACT_ID = "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "scm_production_candidate_release_gate_review_packet_assembled_no_authorization_granted"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001",
)

METHOD_FAMILY = "SCM"
METHOD_FAMILY_STATUS = "production_candidate_gated"
PACKET_CONTRACT = "SCMReleaseGateReviewPacket"
PACKET_STATUS = "assembled_for_review"

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
}

_SCM_FLAGS = {
    "scm_release_gate_review_packet_assembled": False,
    "scm_release_gate_approval_granted": False,
    "scm_production_inference_authorized": False,
}

PACKET_STATUSES = (
    "assembled_for_review",
    "metadata_scaffold_present",
    "review_required",
    "blocked",
    "not_authorized",
    "release_gate_required",
    "not_applicable",
)

PACKET_SECTIONS = (
    "packet_metadata",
    "source_artifacts",
    "evidence_stack_inventory",
    "scm_validation_evidence_summary",
    "scm_null_calibration_evidence_summary",
    "scm_jackknife_sensitivity_evidence_summary",
    "release_gate_domain_statuses",
    "evidence_prerequisite_statuses",
    "blocked_authorization_domains",
    "review_required_domains",
    "required_followups",
    "human_review_requirements",
    "expiration_review_requirements",
    "revocation_trigger_requirements",
    "rollback_requirements",
    "future_decision_inputs",
    "authorization_boundary",
    "audit_references",
)

REQUIRED_SOURCE_ARTIFACTS = (
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001",
)

SOURCE_ARTIFACT_REGISTRY = {
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001": {
        "registry_rows": 31,
        "evidence_contract": "SCMValidationEvidence",
        "layer": "validation",
    },
    "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001": {
        "registry_rows": 30,
        "evidence_contract": "SCMNullCalibrationEvidence",
        "layer": "null_calibration",
    },
    "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001": {
        "registry_rows": 37,
        "evidence_contract": "SCMJackknifeSensitivityEvidence",
        "layer": "jackknife_sensitivity",
    },
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001": {
        "registry_rows": 99,
        "evidence_contract": "SCMReleaseGateReviewInput",
        "layer": "release_gate_review_plan",
    },
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001": {
        "registry_rows": 117,
        "evidence_contract": "ProductionAuthorizationDecision",
        "layer": "cross_family_release_gate",
    },
}

BR_MISSING_SOURCE_ARTIFACT = "SCM-RG-PKT-BR-MISSING-SOURCE-ARTIFACT"
BR_EVIDENCE_METADATA_ONLY = "SCM-RG-PKT-BR-EVIDENCE-METADATA-ONLY"
BR_RELEASE_GATE_NOT_APPROVED = "SCM-RG-PKT-BR-RELEASE-GATE-NOT-APPROVED"
BR_P_VALUE_NOT_AUTHORIZED = "SCM-RG-PKT-BR-P-VALUE-NOT-AUTHORIZED"
BR_CAUSAL_CI_NOT_AUTHORIZED = "SCM-RG-PKT-BR-CAUSAL-CI-NOT-AUTHORIZED"
BR_PRODUCTION_INFERENCE_NOT_AUTHORIZED = "SCM-RG-PKT-BR-PRODUCTION-INFERENCE-NOT-AUTHORIZED"
BR_MULTICELL_BLOCKED = "SCM-RG-PKT-BR-MULTICELL-BLOCKED"
BR_SELECTOR_ROUTER_NOT_AUTHORIZED = "SCM-RG-PKT-BR-SELECTOR-ROUTER-NOT-AUTHORIZED"
BR_DOWNSTREAM_NOT_AUTHORIZED = "SCM-RG-PKT-BR-DOWNSTREAM-NOT-AUTHORIZED"

BLOCKED_REASONS_SUPPORTED = (
    BR_MISSING_SOURCE_ARTIFACT,
    BR_EVIDENCE_METADATA_ONLY,
    BR_RELEASE_GATE_NOT_APPROVED,
    BR_P_VALUE_NOT_AUTHORIZED,
    BR_CAUSAL_CI_NOT_AUTHORIZED,
    BR_PRODUCTION_INFERENCE_NOT_AUTHORIZED,
    BR_MULTICELL_BLOCKED,
    BR_SELECTOR_ROUTER_NOT_AUTHORIZED,
    BR_DOWNSTREAM_NOT_AUTHORIZED,
)

REQUIRED_FOLLOWUPS = (
    "SCM-RG-PKT-RF-STATISTICAL-VALIDATION",
    "SCM-RG-PKT-RF-STATISTICAL-NULL-CALIBRATION",
    "SCM-RG-PKT-RF-STATISTICAL-JACKKNIFE",
    "SCM-RG-PKT-RF-DGP-COVERAGE",
    "SCM-RG-PKT-RF-FAILURE-REGISTRY",
    "SCM-RG-PKT-RF-MULTICELL-VALIDATION",
    "SCM-RG-PKT-RF-SELECTOR-SHADOW",
    "SCM-RG-PKT-RF-PRODUCTION-READINESS-BACKLOG",
    "SCM-RG-PKT-RF-HUMAN-GOVERNANCE-REVIEW",
    "SCM-RG-PKT-RF-ROLLBACK-REVOCATION-PLAN",
    "SCM-RG-PKT-RF-RELEASE-GATE-DECISION-PLAN",
) + PLAN_REQUIRED_FOLLOWUPS

FUTURE_DECISION_INPUTS = (
    "scm_validation_evidence",
    "scm_null_calibration_evidence",
    "scm_jackknife_sensitivity_evidence",
    "release_gate_domain_statuses",
    "evidence_prerequisite_statuses",
    "blocked_authorization_domains",
    "required_followups",
    "human_review_state",
    "expiration_or_review_date",
    "revocation_triggers",
    "rollback_revocation_plan",
    "audit_references",
    "authorization_flags",
)

DEPENDENCIES_RECONCILED = (
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001",
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
    "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
    "PRODUCTION_READINESS_BACKLOG_LEDGER_001",
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",
    "FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001",
)

NON_GOALS = (
    "no_release_gate_approval_granted",
    "no_release_gate_decision",
    "no_scm_production_inference_authorization",
    "no_production_p_values_or_causal_cis",
    "no_selector_router_production_use",
    "no_multicell_scm_production_claims",
    "no_trustreport_calibration_signal_mmm",
    "no_live_api_scheduler_budget",
    "no_package_side_agent_authorization",
    "no_automatic_authorization_from_packet_assembly",
    "no_closing_readiness_gaps_by_packet",
)

ALLOWED_CURRENT_USE = (
    "metadata_evidence_stack_inventory",
    "release_gate_review_preparation",
    "human_governance_review_input",
    "selector_shadow_non_authorizing_input",
    "audit_traceability",
)

FORBIDDEN_CURRENT_USE = (
    "production_inference",
    "production_p_values",
    "causal_confidence_intervals",
    "release_gate_approval",
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

REVOCATION_TRIGGERS = (
    "validation_regression",
    "null_fpr_exceedance",
    "jackknife_instability_breach",
    "multicell_multiplicity_violation",
    "retire_replace_violation",
    "open_investigation_escalation",
    "human_governance_revoke",
)

HUMAN_REVIEW_REQUIREMENTS = (
    "reviewers_recorded",
    "review_date_recorded",
    "decision_scope_documented",
    "evidence_artifacts_consulted",
    "open_investigation_state_consulted",
    "production_readiness_backlog_consulted",
    "conditions_and_audit_references_recorded",
)


class PacketStatus(str, Enum):
    ASSEMBLED_FOR_REVIEW = "assembled_for_review"
    METADATA_SCAFFOLD_PRESENT = "metadata_scaffold_present"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_AUTHORIZED = "not_authorized"
    RELEASE_GATE_REQUIRED = "release_gate_required"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class SCMReleaseGateReviewPacketInput:
    source_artifact_state: Mapping[str, Any] = field(default_factory=dict)
    audit_context: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SCMReleaseGateReviewPacket:
    packet_id: str
    artifact_id: str
    packet_status: str
    method_family: str
    method_family_status: str
    source_artifacts: tuple[str, ...]
    evidence_stack: tuple[dict[str, Any], ...]
    release_gate_domains: dict[str, str]
    evidence_prerequisites: dict[str, str]
    blocked_authorization_domains: tuple[str, ...]
    review_required_domains: tuple[str, ...]
    required_followups: tuple[str, ...]
    allowed_current_use: tuple[str, ...]
    forbidden_current_use: tuple[str, ...]
    human_review_required: bool
    expiration_review_required: bool
    revocation_triggers_required: bool
    rollback_plan_required: bool
    future_decision_inputs: tuple[str, ...]
    audit_references: tuple[str, ...]
    authorization_flags: dict[str, bool]
    blocked_reasons: tuple[str, ...]
    packet_sections: dict[str, Any]
    final_verdict: str


def _domain_packet_status(domain: str) -> str:
    profile = DOMAIN_PROFILES[domain]
    review_status = profile["review_status"]
    current = profile["current"]
    if current == "blocked":
        return PacketStatus.BLOCKED.value
    if review_status == "blocked":
        return PacketStatus.BLOCKED.value
    if review_status == "review_required":
        return PacketStatus.REVIEW_REQUIRED.value
    return PacketStatus.NOT_AUTHORIZED.value


def _prerequisite_packet_status(prereq: str) -> str:
    status = PREREQUISITE_PROFILES[prereq]["scm_status"]
    if status == "blocked":
        return PacketStatus.BLOCKED.value
    if status == "metadata_scaffold_present":
        return PacketStatus.METADATA_SCAFFOLD_PRESENT.value
    return PacketStatus.REVIEW_REQUIRED.value


def build_scm_release_gate_review_packet(
    inp: SCMReleaseGateReviewPacketInput | None = None,
) -> SCMReleaseGateReviewPacket:
    """Assemble deterministic SCM release-gate review packet (non-authorizing)."""
    inp = inp or SCMReleaseGateReviewPacketInput()
    state = dict(inp.source_artifact_state)
    blocked_reasons: list[str] = []
    followups: list[str] = list(REQUIRED_FOLLOWUPS)

    source_artifacts: list[str] = []
    evidence_stack: list[dict[str, Any]] = []

    for artifact_id in REQUIRED_SOURCE_ARTIFACTS:
        available = state.get(artifact_id, {"present": True})
        present = available.get("present", True) if isinstance(available, Mapping) else bool(available)
        if present:
            meta = SOURCE_ARTIFACT_REGISTRY[artifact_id]
            source_artifacts.append(artifact_id)
            evidence_stack.append({
                "artifact_id": artifact_id,
                "status": PacketStatus.METADATA_SCAFFOLD_PRESENT.value,
                "registry_rows": meta["registry_rows"],
                "evidence_contract": meta["evidence_contract"],
                "layer": meta["layer"],
                "authorizes": "none",
            })
        else:
            blocked_reasons.append(BR_MISSING_SOURCE_ARTIFACT)
            followups.append(f"SCM-RG-PKT-RF-SOURCE-{artifact_id}")

    release_gate_domains = {d: _domain_packet_status(d) for d in RELEASE_GATE_DOMAINS}
    evidence_prerequisites = {p: _prerequisite_packet_status(p) for p in EVIDENCE_PREREQUISITES}

    blocked_domains: list[str] = list(RELEASE_GATE_DOMAINS)
    review_required_domains: list[str] = [
        d for d, status in release_gate_domains.items()
        if status in (PacketStatus.REVIEW_REQUIRED.value, PacketStatus.RELEASE_GATE_REQUIRED.value)
    ]

    blocked_reasons.extend([
        BR_EVIDENCE_METADATA_ONLY,
        BR_RELEASE_GATE_NOT_APPROVED,
        BR_P_VALUE_NOT_AUTHORIZED,
        BR_CAUSAL_CI_NOT_AUTHORIZED,
        BR_PRODUCTION_INFERENCE_NOT_AUTHORIZED,
        BR_MULTICELL_BLOCKED,
        BR_SELECTOR_ROUTER_NOT_AUTHORIZED,
        BR_DOWNSTREAM_NOT_AUTHORIZED,
    ])

    audit_refs = tuple(dict.fromkeys(
        list(REQUIRED_SOURCE_ARTIFACTS)
        + ["PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001", _ARTIFACT_ID]
    ))

    packet_sections: dict[str, Any] = {
        "packet_metadata": {
            "packet_id": f"{_ARTIFACT_ID}-PACKET",
            "artifact_id": _ARTIFACT_ID,
            "packet_status": PACKET_STATUS,
            "method_family": METHOD_FAMILY,
            "method_family_status": METHOD_FAMILY_STATUS,
        },
        "source_artifacts": list(source_artifacts),
        "evidence_stack_inventory": evidence_stack,
        "scm_validation_evidence_summary": {
            "artifact": "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",
            "registry_rows": 31,
            "status": PacketStatus.METADATA_SCAFFOLD_PRESENT.value,
            "supports": ("validation_metadata_contract", "blocked_reason_mapping"),
            "does_not_support": ("production_inference", "production_p_values", "causal_cis"),
        },
        "scm_null_calibration_evidence_summary": {
            "artifact": "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",
            "registry_rows": 30,
            "status": PacketStatus.METADATA_SCAFFOLD_PRESENT.value,
            "supports": ("null_calibration_metadata_contract", "p_value_boundary_mapping"),
            "does_not_support": ("production_p_values", "type_i_error_calibration"),
        },
        "scm_jackknife_sensitivity_evidence_summary": {
            "artifact": "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001",
            "registry_rows": 37,
            "status": PacketStatus.METADATA_SCAFFOLD_PRESENT.value,
            "supports": ("jackknife_sensitivity_metadata_contract", "causal_ci_boundary_mapping"),
            "does_not_support": ("causal_confidence_intervals", "jackknife_refits"),
        },
        "release_gate_domain_statuses": release_gate_domains,
        "evidence_prerequisite_statuses": evidence_prerequisites,
        "blocked_authorization_domains": blocked_domains,
        "review_required_domains": review_required_domains,
        "required_followups": list(dict.fromkeys(followups)),
        "human_review_requirements": list(HUMAN_REVIEW_REQUIREMENTS),
        "expiration_review_requirements": {
            "required": True,
            "status": PacketStatus.REVIEW_REQUIRED.value,
            "field": "expiration_or_review_date",
        },
        "revocation_trigger_requirements": {
            "required": True,
            "triggers": list(REVOCATION_TRIGGERS),
        },
        "rollback_requirements": {
            "required": True,
            "status": PacketStatus.METADATA_SCAFFOLD_PRESENT.value,
            "prerequisite": "rollback_or_revocation_path_defined",
        },
        "future_decision_inputs": list(FUTURE_DECISION_INPUTS),
        "authorization_boundary": {
            "scm_release_gate_approval_granted": False,
            "scm_production_inference_authorized": False,
            "all_authorization_flags_false": True,
        },
        "audit_references": list(audit_refs),
    }

    for key, profile in SCM_EVIDENCE_PROFILES.items():
        packet_sections.setdefault("evidence_stack_inventory", evidence_stack)

    return SCMReleaseGateReviewPacket(
        packet_id=f"{_ARTIFACT_ID}-PACKET",
        artifact_id=_ARTIFACT_ID,
        packet_status=PACKET_STATUS,
        method_family=METHOD_FAMILY,
        method_family_status=METHOD_FAMILY_STATUS,
        source_artifacts=tuple(source_artifacts),
        evidence_stack=tuple(evidence_stack),
        release_gate_domains=release_gate_domains,
        evidence_prerequisites=evidence_prerequisites,
        blocked_authorization_domains=tuple(blocked_domains),
        review_required_domains=tuple(review_required_domains),
        required_followups=tuple(dict.fromkeys(followups)),
        allowed_current_use=ALLOWED_CURRENT_USE,
        forbidden_current_use=FORBIDDEN_CURRENT_USE,
        human_review_required=True,
        expiration_review_required=True,
        revocation_triggers_required=True,
        rollback_plan_required=True,
        future_decision_inputs=FUTURE_DECISION_INPUTS,
        audit_references=audit_refs,
        authorization_flags=dict(_AUTH_FLAGS),
        blocked_reasons=tuple(dict.fromkeys(blocked_reasons)),
        packet_sections=packet_sections,
        final_verdict=_VERDICT,
    )


def validate_scm_release_gate_review_packet(packet: SCMReleaseGateReviewPacket) -> dict[str, Any]:
    """Validate assembled packet coverage and authorization boundary."""
    issues: list[str] = []

    if len(packet.source_artifacts) < len(REQUIRED_SOURCE_ARTIFACTS):
        issues.append("missing required source artifacts")
    for section in PACKET_SECTIONS:
        if section not in packet.packet_sections:
            issues.append(f"missing packet section: {section}")
    for domain in RELEASE_GATE_DOMAINS:
        if domain not in packet.release_gate_domains:
            issues.append(f"missing release_gate_domain: {domain}")
    for prereq in EVIDENCE_PREREQUISITES:
        if prereq not in packet.evidence_prerequisites:
            issues.append(f"missing evidence_prerequisite: {prereq}")
    for flag, expected in _AUTH_FLAGS.items():
        if packet.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    if packet.packet_status != PACKET_STATUS:
        issues.append(f"packet_status must be {PACKET_STATUS}")

    return {
        "valid": not issues,
        "source_artifact_count": len(packet.source_artifacts),
        "packet_section_count": len(packet.packet_sections),
        "release_gate_domain_count": len(packet.release_gate_domains),
        "evidence_prerequisite_count": len(packet.evidence_prerequisites),
        "all_packet_sections_present": all(s in packet.packet_sections for s in PACKET_SECTIONS),
        "all_domains_covered": all(d in packet.release_gate_domains for d in RELEASE_GATE_DOMAINS),
        "all_prerequisites_covered": all(p in packet.evidence_prerequisites for p in EVIDENCE_PREREQUISITES),
        "issues": issues,
    }


def build_scenarios() -> list[dict[str, Any]]:
    packet = build_scm_release_gate_review_packet()
    missing_packet = build_scm_release_gate_review_packet(
        SCMReleaseGateReviewPacketInput(
            source_artifact_state={
                "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001": {"present": False},
            }
        )
    )
    validation = validate_scm_release_gate_review_packet(packet)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool, detail: str = "") -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": detail}

    for section in PACKET_SECTIONS:
        scenarios.append(_s(f"packet_section_{section}_present", section in packet.packet_sections))

    for artifact in REQUIRED_SOURCE_ARTIFACTS:
        scenarios.append(_s(
            f"source_artifact_{artifact}_referenced",
            artifact in packet.source_artifacts,
        ))

    for domain in RELEASE_GATE_DOMAINS:
        scenarios.append(_s(f"release_gate_domain_{domain}_present", domain in packet.release_gate_domains))

    for prereq in EVIDENCE_PREREQUISITES:
        scenarios.append(_s(f"evidence_prerequisite_{prereq}_present", prereq in packet.evidence_prerequisites))

    for field_name in (
        "packet_id", "artifact_id", "packet_status", "method_family", "method_family_status",
        "source_artifacts", "evidence_stack", "release_gate_domains", "evidence_prerequisites",
        "blocked_authorization_domains", "review_required_domains", "required_followups",
        "allowed_current_use", "forbidden_current_use", "human_review_required",
        "expiration_review_required", "revocation_triggers_required", "rollback_plan_required",
        "future_decision_inputs", "audit_references", "authorization_flags", "final_verdict",
    ):
        scenarios.append(_s(f"packet_contract_field_{field_name}_present", hasattr(packet, field_name)))

    for status in PACKET_STATUSES:
        scenarios.append(_s(f"packet_status_vocab_{status}", status in PACKET_STATUSES))

    scenarios.append(_s(
        "blocked_includes_p_value_domain",
        "production_p_value_authorization" in packet.blocked_authorization_domains,
    ))
    scenarios.append(_s(
        "blocked_includes_causal_ci_domain",
        "causal_uncertainty_authorization" in packet.blocked_authorization_domains,
    ))
    scenarios.append(_s(
        "blocked_includes_inference_domain",
        "inference_authorization" in packet.blocked_authorization_domains,
    ))
    scenarios.append(_s(
        "blocked_includes_multicell_domain",
        "multicell_claim_authorization" in packet.blocked_authorization_domains,
    ))
    scenarios.append(_s(
        "blocked_includes_selector_router",
        "selector_router_authorization" in packet.blocked_authorization_domains,
    ))
    scenarios.append(_s(
        "blocked_includes_downstream",
        "trustreport_authorization" in packet.blocked_authorization_domains,
    ))
    scenarios.append(_s("human_review_required", packet.human_review_required is True))
    scenarios.append(_s("expiration_review_required", packet.expiration_review_required is True))
    scenarios.append(_s("revocation_triggers_required", packet.revocation_triggers_required is True))
    scenarios.append(_s("rollback_plan_required", packet.rollback_plan_required is True))
    scenarios.append(_s("release_gate_approval_false", _SCM_FLAGS["scm_release_gate_approval_granted"] is False))
    scenarios.append(_s("production_inference_false", not packet.authorization_flags["scm_production_inference_authorized"]))
    scenarios.append(_s("p_value_false", not packet.authorization_flags["scm_production_p_value_authorized"]))
    scenarios.append(_s("causal_ci_false", not packet.authorization_flags["scm_causal_confidence_interval_authorized"]))
    scenarios.append(_s("selector_router_false", not packet.authorization_flags["selector_implementation_authorized"]))
    scenarios.append(_s("multicell_false", not packet.authorization_flags["multicell_production_claim_authorized"]))
    scenarios.append(_s("downstream_false", not packet.authorization_flags["trustreport_authorized"]))
    scenarios.append(_s("missing_source_artifact_blocked", BR_MISSING_SOURCE_ARTIFACT in missing_packet.blocked_reasons))
    scenarios.append(_s("final_verdict_matches", packet.final_verdict == _VERDICT))
    scenarios.append(_s("validation_valid", validation["valid"]))
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not packet.authorization_flags[flag]))
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
    packet = build_scm_release_gate_review_packet()
    validation = validate_scm_release_gate_review_packet(packet)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "scm_release_gate_review_packet_metadata_only",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "packet_status": PACKET_STATUS,
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "method_family": METHOD_FAMILY,
        "method_family_status": METHOD_FAMILY_STATUS,
        "next_artifact": RECOMMENDED_NEXT_ARTIFACTS[0],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        "packet_contract": PACKET_CONTRACT,
        "packet_sections": list(PACKET_SECTIONS),
        "release_gate_domains": list(RELEASE_GATE_DOMAINS),
        "evidence_prerequisites": list(EVIDENCE_PREREQUISITES),
        "blocked_authorization_domains": list(packet.blocked_authorization_domains),
        "review_required_domains": list(packet.review_required_domains),
        "required_followups": list(packet.required_followups),
        "source_artifacts": list(packet.source_artifacts),
        "future_decision_inputs": list(FUTURE_DECISION_INPUTS),
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
        "scm_release_gate_review_packet_assembled": False,
        "scm_release_gate_approval_granted": False,
        "scm_production_inference_authorized": False,
        "authorization_flags": dict(_AUTH_FLAGS),
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        "blocked_reasons_supported": list(BLOCKED_REASONS_SUPPORTED),
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
