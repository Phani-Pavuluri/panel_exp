"""Tests for SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.scm_production_candidate_release_gate_review_plan_001 import (
    DECISION_CONTRACT,
    DECISION_FIELDS,
    EVIDENCE_PREREQUISITES,
    INPUT_CONTRACT,
    INPUT_FIELDS,
    MIN_PLAN_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    RELEASE_GATE_DOMAINS,
    REVIEW_STATUSES,
    STAGES,
    PlanSection,
    _AUTH_FLAGS,
    _BOUNDARY_FLAGS,
    _SCM_FLAGS,
    build_scm_production_candidate_release_gate_review_plan,
    build_scenarios,
    filter_scm_production_candidate_release_gate_review_plan,
    run_validation,
    summarize_scm_production_candidate_release_gate_review_plan,
    validate_scm_production_candidate_release_gate_review_plan,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001_summary.json"
_REPORT = _REPO / "docs/track_d/SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001_REPORT.md"


def test_plan_rows_build_and_minimum_count() -> None:
    rows = build_scm_production_candidate_release_gate_review_plan()
    assert len(rows) >= MIN_PLAN_ROW_COUNT
    assert len({r.plan_id for r in rows}) == len(rows)


def test_all_domains_prerequisites_contracts_and_stages_represented() -> None:
    rows = build_scm_production_candidate_release_gate_review_plan()
    validation = validate_scm_production_candidate_release_gate_review_plan(rows)
    assert validation["valid"]
    assert validation["all_release_gate_domains_covered"]
    assert validation["all_evidence_prerequisites_covered"]
    assert validation["all_input_fields_covered"]
    assert validation["all_decision_fields_covered"]
    assert validation["all_stages_present"]


def test_status_vocabulary_complete() -> None:
    assert len(REVIEW_STATUSES) == 7
    for status in (
        "metadata_scaffold_present",
        "review_required",
        "eligible_for_review",
        "blocked",
        "not_authorized",
        "release_gate_required",
        "not_applicable",
    ):
        assert status in REVIEW_STATUSES


def test_summary_flags() -> None:
    rows = build_scm_production_candidate_release_gate_review_plan()
    summary = summarize_scm_production_candidate_release_gate_review_plan(rows)
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert summary[flag] == expected
    for flag, expected in _SCM_FLAGS.items():
        assert summary[flag] is expected
    assert summary["next_artifact"] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["final_verdict"] == (
        "scm_production_candidate_release_gate_review_plan_defined_no_authorization_granted"
    )


def test_no_downstream_authorization() -> None:
    rows = build_scm_production_candidate_release_gate_review_plan()
    summary = summarize_scm_production_candidate_release_gate_review_plan(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False
    for flag in summary["authorization_flags"].values():
        assert flag is False


def test_release_gate_approval_not_granted() -> None:
    rows = build_scm_production_candidate_release_gate_review_plan()
    summary = summarize_scm_production_candidate_release_gate_review_plan(rows)
    assert summary["scm_release_gate_approval_granted"] is False
    assert summary["scm_production_inference_authorized"] is False
    assert summary["scm_production_p_value_authorized"] is False
    assert summary["scm_causal_confidence_interval_authorized"] is False


def test_selector_router_and_multicell_unauthorized() -> None:
    rows = build_scm_production_candidate_release_gate_review_plan()
    summary = summarize_scm_production_candidate_release_gate_review_plan(rows)
    assert summary["selector_implementation_authorized"] is False
    assert summary["production_selection_router_authorized"] is False
    assert summary["multicell_production_claim_authorized"] is False


def test_downstream_authorization_false() -> None:
    rows = build_scm_production_candidate_release_gate_review_plan()
    summary = summarize_scm_production_candidate_release_gate_review_plan(rows)
    assert summary["trustreport_authorized"] is False
    assert summary["package_side_agents_authorized"] is False
    assert summary["live_api_authorized"] is False


def test_contracts_and_components_defined() -> None:
    rows = build_scm_production_candidate_release_gate_review_plan()
    domain_rows = filter_scm_production_candidate_release_gate_review_plan(
        rows, plan_section=PlanSection.RELEASE_GATE_DOMAIN
    )
    prereq_rows = filter_scm_production_candidate_release_gate_review_plan(
        rows, plan_section=PlanSection.EVIDENCE_PREREQUISITE
    )
    input_rows = filter_scm_production_candidate_release_gate_review_plan(
        rows, plan_section=PlanSection.INPUT_CONTRACT
    )
    decision_rows = filter_scm_production_candidate_release_gate_review_plan(
        rows, plan_section=PlanSection.DECISION_CONTRACT
    )
    assert {r.field_or_component for r in domain_rows} == set(RELEASE_GATE_DOMAINS)
    assert {r.field_or_component for r in prereq_rows} == set(EVIDENCE_PREREQUISITES)
    assert {r.field_or_component for r in input_rows} == set(INPUT_FIELDS)
    assert {r.field_or_component for r in decision_rows} == set(DECISION_FIELDS)
    summary = summarize_scm_production_candidate_release_gate_review_plan(rows)
    assert summary["planned_input_contract"] == INPUT_CONTRACT
    assert summary["planned_decision_contract"] == DECISION_CONTRACT
    assert summary["planned_stages"] == list(STAGES)


def test_required_fields_nonempty() -> None:
    rows = build_scm_production_candidate_release_gate_review_plan()
    for row in rows:
        assert row.purpose
        assert row.authorization_boundary
        assert row.required_prior_artifacts


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001"
    assert data["failed_scenarios"] == []
    assert data["plan_row_count"] >= MIN_PLAN_ROW_COUNT
    assert data["scm_release_gate_approval_granted"] is False
    assert data["scm_release_gate_review_plan_completed"] is False
    assert data["scm_production_inference_authorized"] is False
    assert data["planned_input_contract"] == INPUT_CONTRACT
    assert data["planned_decision_contract"] == DECISION_CONTRACT
    assert data["review_domains"] == list(RELEASE_GATE_DOMAINS)
    assert data["planned_stages"] == list(STAGES)
    assert data["final_verdict"] == (
        "scm_production_candidate_release_gate_review_plan_defined_no_authorization_granted"
    )
    assert data["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001"


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "review plan only" in text.lower()
    assert "no release-gate approval" in text.lower() or "not a release-gate approval" in text.lower()
    assert "production_candidate_gated" in text.lower()
    assert "metadata scaffold" in text.lower() or "metadata scaffolding" in text.lower()
    assert "human governance review" in text.lower()
