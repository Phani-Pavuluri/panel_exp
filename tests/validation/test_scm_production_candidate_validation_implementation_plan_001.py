"""Tests for SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.scm_production_candidate_validation_implementation_plan_001 import (
    EVIDENCE_CONTRACT,
    EVIDENCE_FIELDS,
    INPUT_CONTRACT,
    INPUT_FIELDS,
    MIN_PLAN_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    VALIDATION_AREAS,
    STAGES,
    PlanSection,
    _AUTH_FLAGS,
    _BOUNDARY_FLAGS,
    _SCM_FLAGS,
    build_scm_production_candidate_validation_implementation_plan,
    build_scenarios,
    filter_scm_production_candidate_validation_implementation_plan,
    run_validation,
    summarize_scm_production_candidate_validation_implementation_plan,
    validate_scm_production_candidate_validation_implementation_plan,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001_REPORT.md"


def test_plan_rows_build_and_minimum_count() -> None:
    rows = build_scm_production_candidate_validation_implementation_plan()
    assert len(rows) >= MIN_PLAN_ROW_COUNT
    assert len({r.plan_id for r in rows}) == len(rows)


def test_all_areas_fields_and_stages_represented() -> None:
    rows = build_scm_production_candidate_validation_implementation_plan()
    validation = validate_scm_production_candidate_validation_implementation_plan(rows)
    assert validation["valid"]
    assert validation["all_validation_areas_covered"]
    assert validation["all_input_fields_covered"]
    assert validation["all_evidence_fields_covered"]
    assert validation["all_stages_present"]


def test_summary_flags() -> None:
    rows = build_scm_production_candidate_validation_implementation_plan()
    summary = summarize_scm_production_candidate_validation_implementation_plan(rows)
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert summary[flag] == expected
    for flag, expected in _SCM_FLAGS.items():
        assert summary[flag] is expected
    assert summary["method_family"] == "SCM"
    assert summary["method_family_status"] == "production_candidate_gated"
    assert summary["next_artifact"] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["final_verdict"] == (
        "scm_production_candidate_validation_implementation_plan_defined_no_downstream_authorization"
    )


def test_no_downstream_authorization() -> None:
    rows = build_scm_production_candidate_validation_implementation_plan()
    summary = summarize_scm_production_candidate_validation_implementation_plan(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False
    for flag in summary["authorization_flags"].values():
        assert flag is False


def test_contract_fields_defined() -> None:
    rows = build_scm_production_candidate_validation_implementation_plan()
    areas = filter_scm_production_candidate_validation_implementation_plan(
        rows, plan_section=PlanSection.VALIDATION_AREA
    )
    inputs = filter_scm_production_candidate_validation_implementation_plan(
        rows, plan_section=PlanSection.INPUT_CONTRACT
    )
    evidence = filter_scm_production_candidate_validation_implementation_plan(
        rows, plan_section=PlanSection.EVIDENCE_CONTRACT
    )
    assert {r.field_or_component for r in areas} == set(VALIDATION_AREAS)
    assert {r.field_or_component for r in inputs} == set(INPUT_FIELDS)
    assert {r.field_or_component for r in evidence} == set(EVIDENCE_FIELDS)
    summary = summarize_scm_production_candidate_validation_implementation_plan(rows)
    assert summary["planned_input_contract"] == INPUT_CONTRACT
    assert summary["planned_evidence_contract"] == EVIDENCE_CONTRACT


def test_multicell_and_uncertainty_blocked() -> None:
    rows = build_scm_production_candidate_validation_implementation_plan()
    summary = summarize_scm_production_candidate_validation_implementation_plan(rows)
    assert summary["validation_area_planned_statuses"]["multicell_shared_control_blocker"] == "blocked"
    assert summary["validation_area_planned_statuses"]["uncertainty_boundary"] == "blocked"
    assert summary["validation_area_planned_statuses"]["release_gate_dependency"] == "release_gate_required"


def test_required_fields_nonempty() -> None:
    rows = build_scm_production_candidate_validation_implementation_plan()
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
    assert data["artifact_id"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001"
    assert data["failed_scenarios"] == []
    assert data["scm_validation_implementation_authorized"] is False
    assert data["scm_production_inference_authorized"] is False
    assert data["validation_areas"] == list(VALIDATION_AREAS)
    assert data["stages"] == list(STAGES)


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "scm validation implementation plan only" in text.lower()
    assert "gated production-candidate" in text.lower()
    assert "no scm validation runtime" in text.lower()
    assert "no scm production inference" in text.lower()
    assert "release gate remains required" in text.lower()
    assert "multicell" in text.lower()
