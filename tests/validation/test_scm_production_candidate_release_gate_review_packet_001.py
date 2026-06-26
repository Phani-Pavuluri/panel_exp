"""Tests for SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.scm_production_candidate_release_gate_review_packet_001 import (
    BLOCKED_REASONS_SUPPORTED,
    BR_MISSING_SOURCE_ARTIFACT,
    EVIDENCE_PREREQUISITES,
    FUTURE_DECISION_INPUTS,
    NON_GOALS,
    PACKET_CONTRACT,
    PACKET_SECTIONS,
    PACKET_STATUSES,
    RELEASE_GATE_DOMAINS,
    REQUIRED_SOURCE_ARTIFACTS,
    SCMReleaseGateReviewPacketInput,
    _AUTH_FLAGS,
    _SCM_FLAGS,
    build_scm_release_gate_review_packet,
    build_scenarios,
    run_validation,
    validate_scm_release_gate_review_packet,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001_summary.json"
_REPORT = _REPO / "docs/track_d/SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001_REPORT.md"


def test_all_packet_sections_present() -> None:
    packet = build_scm_release_gate_review_packet()
    for section in PACKET_SECTIONS:
        assert section in packet.packet_sections


def test_all_source_artifacts_referenced() -> None:
    packet = build_scm_release_gate_review_packet()
    for artifact in REQUIRED_SOURCE_ARTIFACTS:
        assert artifact in packet.source_artifacts


def test_all_domains_and_prerequisites_present() -> None:
    packet = build_scm_release_gate_review_packet()
    assert set(packet.release_gate_domains) == set(RELEASE_GATE_DOMAINS)
    assert set(packet.evidence_prerequisites) == set(EVIDENCE_PREREQUISITES)


def test_packet_contract_fields_present() -> None:
    packet = build_scm_release_gate_review_packet()
    assert packet.packet_id
    assert packet.artifact_id == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001"
    assert packet.packet_status == "assembled_for_review"
    assert packet.method_family == "SCM"
    assert packet.evidence_stack
    assert packet.authorization_flags
    assert packet.final_verdict


def test_status_vocabulary_complete() -> None:
    assert len(PACKET_STATUSES) == 7


def test_blocked_authorization_domains_cover_critical_areas() -> None:
    packet = build_scm_release_gate_review_packet()
    for domain in (
        "production_p_value_authorization",
        "causal_uncertainty_authorization",
        "inference_authorization",
        "multicell_claim_authorization",
        "selector_router_authorization",
        "trustreport_authorization",
    ):
        assert domain in packet.blocked_authorization_domains


def test_human_and_rollback_requirements() -> None:
    packet = build_scm_release_gate_review_packet()
    assert packet.human_review_required is True
    assert packet.expiration_review_required is True
    assert packet.revocation_triggers_required is True
    assert packet.rollback_plan_required is True
    assert packet.packet_sections["human_review_requirements"]
    assert packet.packet_sections["rollback_requirements"]["required"] is True


def test_no_authorization_granted() -> None:
    packet = build_scm_release_gate_review_packet()
    assert _SCM_FLAGS["scm_release_gate_approval_granted"] is False
    for flag in _AUTH_FLAGS:
        assert packet.authorization_flags[flag] is False


def test_missing_source_artifact_blocked() -> None:
    packet = build_scm_release_gate_review_packet(
        SCMReleaseGateReviewPacketInput(
            source_artifact_state={
                "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001": {"present": False},
            }
        )
    )
    assert BR_MISSING_SOURCE_ARTIFACT in packet.blocked_reasons


def test_validate_packet() -> None:
    packet = build_scm_release_gate_review_packet()
    result = validate_scm_release_gate_review_packet(packet)
    assert result["valid"]
    assert result["all_packet_sections_present"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001"
    assert data["packet_status"] == "assembled_for_review"
    assert data["failed_scenarios"] == []
    assert data["scm_release_gate_approval_granted"] is False
    assert data["scm_release_gate_review_packet_assembled"] is False
    assert data["scm_production_inference_authorized"] is False
    assert data["packet_contract"] == PACKET_CONTRACT
    assert data["final_verdict"] == (
        "scm_production_candidate_release_gate_review_packet_assembled_no_authorization_granted"
    )
    assert data["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001"
    assert len(data["packet_sections"]) == len(PACKET_SECTIONS)
    assert len(data["future_decision_inputs"]) == len(FUTURE_DECISION_INPUTS)


def test_report_states_packet_not_approval() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "assembled_for_review" in text.lower() or "assembles a release-gate review packet" in text.lower()
    assert "not a release-gate decision" in text.lower() or "not a release-gate approval" in text.lower()
    assert "metadata scaffold" in text.lower() or "metadata scaffolding" in text.lower()
    assert "human governance review" in text.lower()
