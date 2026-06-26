"""Tests for PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.production_authorization_release_gate_plan_001 import (
    DECISION_RECORD_CONTRACT,
    DECISION_RECORD_FIELDS,
    EVIDENCE_PREREQUISITES,
    MIN_PLAN_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    RELEASE_GATE_DOMAINS,
    STAGES,
    PlanSection,
    _AUTH_FLAGS,
    _BOUNDARY_FLAGS,
    _GATE_FLAGS,
    build_production_authorization_release_gate_plan,
    build_scenarios,
    filter_production_authorization_release_gate_plan,
    run_validation,
    summarize_production_authorization_release_gate_plan,
    validate_production_authorization_release_gate_plan,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001_summary.json"
_REPORT = _REPO / "docs/track_d/PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001_REPORT.md"


def test_plan_rows_build_and_minimum_count() -> None:
    rows = build_production_authorization_release_gate_plan()
    assert len(rows) >= MIN_PLAN_ROW_COUNT
    assert len({r.plan_id for r in rows}) == len(rows)


def test_all_domains_evidence_fields_and_stages_represented() -> None:
    rows = build_production_authorization_release_gate_plan()
    validation = validate_production_authorization_release_gate_plan(rows)
    assert validation["valid"]
    assert validation["all_release_gate_domains_covered"]
    assert validation["all_evidence_prerequisites_covered"]
    assert validation["all_decision_record_fields_covered"]
    assert validation["all_stages_present"]


def test_summary_flags() -> None:
    rows = build_production_authorization_release_gate_plan()
    summary = summarize_production_authorization_release_gate_plan(rows)
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert summary[flag] == expected
    for flag, expected in _GATE_FLAGS.items():
        assert summary[flag] is expected
    assert summary["next_artifact"] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["final_verdict"] == (
        "production_authorization_release_gate_plan_defined_no_downstream_authorization"
    )


def test_no_downstream_authorization() -> None:
    rows = build_production_authorization_release_gate_plan()
    summary = summarize_production_authorization_release_gate_plan(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False
    for flag in summary["authorization_flags"].values():
        assert flag is False


def test_all_domains_not_authorized_or_blocked() -> None:
    rows = build_production_authorization_release_gate_plan()
    summary = summarize_production_authorization_release_gate_plan(rows)
    for domain in RELEASE_GATE_DOMAINS:
        state = summary["release_gate_domain_current_states"][domain]
        assert state in ("not_authorized", "blocked")


def test_contract_and_components_defined() -> None:
    rows = build_production_authorization_release_gate_plan()
    domain_rows = filter_production_authorization_release_gate_plan(
        rows, plan_section=PlanSection.RELEASE_GATE_DOMAIN
    )
    evidence_rows = filter_production_authorization_release_gate_plan(
        rows, plan_section=PlanSection.EVIDENCE_PREREQUISITE
    )
    record_rows = filter_production_authorization_release_gate_plan(
        rows, plan_section=PlanSection.DECISION_RECORD_FIELD
    )
    assert {r.field_or_component for r in domain_rows} == set(RELEASE_GATE_DOMAINS)
    assert {r.field_or_component for r in evidence_rows} == set(EVIDENCE_PREREQUISITES)
    assert {r.field_or_component for r in record_rows} == set(DECISION_RECORD_FIELDS)
    summary = summarize_production_authorization_release_gate_plan(rows)
    assert summary["decision_record_contract"] == DECISION_RECORD_CONTRACT


def test_required_fields_nonempty() -> None:
    rows = build_production_authorization_release_gate_plan()
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
    assert data["artifact_id"] == "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001"
    assert data["failed_scenarios"] == []
    assert data["plan_row_count"] >= MIN_PLAN_ROW_COUNT
    assert data["production_authorization_release_gate_implemented"] is False
    assert data["production_authorization_granted"] is False
    assert data["decision_record_contract"] == DECISION_RECORD_CONTRACT
    assert data["release_gate_domains"] == list(RELEASE_GATE_DOMAINS)
    assert data["stages"] == list(STAGES)


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "release-gate plan only" in text.lower()
    assert "no release-gate runtime" in text.lower()
    assert "no production authorization was granted" in text.lower()
    assert "production p-values" in text.lower()
    assert "causal confidence intervals" in text.lower() or "causal cis" in text.lower()
    assert "all downstream integrations remain blocked" in text.lower()
