"""Tests for SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.scm_production_candidate_null_calibration_implementation_001 import (
    BLOCKED_REASONS_SUPPORTED,
    BR_NULL_CALIBRATION_INCOMPLETE,
    BR_NULL_COVERAGE_INCOMPLETE,
    BR_PLACEBO_STATISTIC_MISSING,
    BR_PLACEBO_UNITS_MISSING,
    BR_PLACEBO_WINDOWS_MISSING,
    BR_RELEASE_GATE_REQUIRED,
    BR_TREATED_STATISTIC_MISSING,
    BR_VALIDATION_EVIDENCE_MISSING,
    RF_VALIDATION_EVIDENCE,
    CalibrationArea,
    CalibrationStatus,
    REQUIRED_CALIBRATION_AREAS,
    RF_RELEASE_GATE,
    RF_VALIDATION_EVIDENCE,
    REQUIRED_FOLLOWUPS_SUPPORTED,
    REQUIRED_STATUSES,
    SCMNullCalibrationInput,
    _AUTH_FLAGS,
    _SCM_FLAGS,
    build_scm_null_calibration_area_registry,
    build_scm_null_calibration_evidence,
    build_scenarios,
    run_validation,
    validate_scm_null_calibration_implementation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001_REPORT.md"


def test_all_calibration_areas_present() -> None:
    registry = build_scm_null_calibration_area_registry()
    assert len(registry) == len(REQUIRED_CALIBRATION_AREAS)
    assert {r.calibration_area for r in registry} == set(REQUIRED_CALIBRATION_AREAS)


def test_input_contract_fields() -> None:
    inp = SCMNullCalibrationInput(
        scm_validation_evidence={"input_contract_satisfied": True},
        panel_metadata={"grain": "weekly"},
        treated_units=("a",),
        donor_units=("b", "c"),
        time_index=("t1",),
        pre_period=("t1",),
        post_period=("t2",),
        placebo_units=("b",),
        placebo_windows=("t1",),
    )
    assert inp.scm_validation_evidence["input_contract_satisfied"] is True
    assert len(inp.placebo_units) == 1


def test_evidence_contract_fields() -> None:
    evidence = build_scm_null_calibration_evidence(SCMNullCalibrationInput())
    assert hasattr(evidence, "input_contract_status")
    assert hasattr(evidence, "p_value_calibration_status")
    assert hasattr(evidence, "null_coverage_status")
    assert hasattr(evidence, "authorization_flags")


def test_status_vocabulary_complete() -> None:
    assert len(REQUIRED_STATUSES) == 8
    for status in (
        "eligible",
        "eligible_after_warning",
        "candidate_after_validation",
        "diagnostic_only",
        "research_only",
        "blocked",
        "release_gate_required",
        "not_applicable",
    ):
        assert CalibrationStatus(status) in REQUIRED_STATUSES


def test_all_authorization_flags_false() -> None:
    evidence = build_scm_null_calibration_evidence(SCMNullCalibrationInput())
    for flag in _AUTH_FLAGS:
        assert evidence.authorization_flags[flag] is False
    for flag, expected in _SCM_FLAGS.items():
        assert expected is False


def test_missing_validation_evidence_blocked() -> None:
    evidence = build_scm_null_calibration_evidence(SCMNullCalibrationInput())
    assert BR_VALIDATION_EVIDENCE_MISSING in evidence.blocked_reasons
    assert RF_VALIDATION_EVIDENCE in evidence.required_followups


def test_missing_placebo_metadata_blocked() -> None:
    inp = SCMNullCalibrationInput(
        scm_validation_evidence={"input_contract_satisfied": True},
        panel_metadata={"grain": "weekly"},
        treated_units=("a",),
        donor_units=("b", "c"),
        time_index=("t1",),
        pre_period=("t1",),
        post_period=("t2",),
    )
    evidence = build_scm_null_calibration_evidence(inp)
    assert BR_PLACEBO_UNITS_MISSING in evidence.blocked_reasons
    assert BR_PLACEBO_WINDOWS_MISSING in evidence.blocked_reasons


def test_missing_statistic_contracts_blocked() -> None:
    inp = SCMNullCalibrationInput(
        scm_validation_evidence={"input_contract_satisfied": True},
        panel_metadata={"grain": "weekly"},
        treated_units=("a",),
        donor_units=("b", "c"),
        time_index=("t1",),
        pre_period=("t1",),
        post_period=("t2",),
        placebo_units=("b",),
        placebo_windows=("t1",),
    )
    evidence = build_scm_null_calibration_evidence(inp)
    assert BR_PLACEBO_STATISTIC_MISSING in evidence.blocked_reasons
    assert BR_TREATED_STATISTIC_MISSING in evidence.blocked_reasons


def test_missing_release_gate_produces_release_gate_required() -> None:
    evidence = build_scm_null_calibration_evidence(SCMNullCalibrationInput())
    assert evidence.release_gate_status == CalibrationStatus.RELEASE_GATE_REQUIRED
    assert BR_RELEASE_GATE_REQUIRED in evidence.blocked_reasons


def test_multicell_unvalidated_blocked() -> None:
    inp = SCMNullCalibrationInput(
        scm_validation_evidence={"input_contract_satisfied": True},
        panel_metadata={"grain": "weekly"},
        treated_units=("a",),
        donor_units=("b", "c"),
        time_index=("t1",),
        pre_period=("t1",),
        post_period=("t2",),
        placebo_units=("b",),
        placebo_windows=("t1",),
        multicell_validation_state={
            "multicell_geometry_present": True,
            "dependence_multiplicity_validated": False,
        },
    )
    evidence = build_scm_null_calibration_evidence(inp)
    assert evidence.multicell_status == CalibrationStatus.BLOCKED


def test_null_calibration_incomplete_no_p_value_auth() -> None:
    evidence = build_scm_null_calibration_evidence(SCMNullCalibrationInput())
    assert BR_NULL_CALIBRATION_INCOMPLETE in evidence.blocked_reasons
    assert evidence.authorization_flags["scm_production_p_value_authorized"] is False
    assert evidence.authorization_flags["production_p_value_authorized"] is False


def test_null_coverage_incomplete_no_causal_ci_auth() -> None:
    evidence = build_scm_null_calibration_evidence(SCMNullCalibrationInput())
    assert BR_NULL_COVERAGE_INCOMPLETE in evidence.blocked_reasons
    assert evidence.authorization_flags["scm_causal_confidence_interval_authorized"] is False
    assert evidence.authorization_flags["causal_confidence_interval_authorized"] is False


def test_blocked_reasons_and_followups_supported() -> None:
    assert len(BLOCKED_REASONS_SUPPORTED) >= 10
    assert len(REQUIRED_FOLLOWUPS_SUPPORTED) >= 8


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_validate_implementation() -> None:
    registry = build_scm_null_calibration_area_registry()
    evidence = build_scm_null_calibration_evidence(SCMNullCalibrationInput())
    result = validate_scm_null_calibration_implementation(registry, evidence)
    assert result["valid"]
    assert result["all_areas_covered"]


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001"
    assert data["failed_scenarios"] == []
    assert data["scm_null_calibration_implementation_authorized"] is False
    assert data["scm_null_calibration_completed"] is False
    assert data["scm_production_inference_authorized"] is False
    assert data["final_verdict"] == (
        "scm_production_candidate_null_calibration_metadata_implemented_no_downstream_authorization"
    )
    assert data["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001"
    assert data["implemented_input_contract"] == "SCMNullCalibrationInput"
    assert data["implemented_evidence_contract"] == "SCMNullCalibrationEvidence"
    assert len(data["implemented_calibration_areas"]) == len(REQUIRED_CALIBRATION_AREAS)


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "metadata scaffolding" in text.lower()
    assert "gated production-candidate" in text.lower()
    assert "no placebo" in text.lower() or "does not compute" in text.lower()
    assert "release gate remains required" in text.lower()
