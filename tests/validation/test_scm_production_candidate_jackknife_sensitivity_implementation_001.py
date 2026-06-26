"""Tests for SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.scm_production_candidate_jackknife_sensitivity_implementation_001 import (
    BLOCKED_REASONS_SUPPORTED,
    BR_DONOR_WEIGHT_METADATA_MISSING,
    BR_JACKKNIFE_INCOMPLETE,
    BR_NULL_CALIBRATION_EVIDENCE_MISSING,
    BR_RELEASE_GATE_REQUIRED,
    BR_UNIT_DELETION_MISSING,
    BR_VALIDATION_EVIDENCE_MISSING,
    REQUIRED_FOLLOWUPS_SUPPORTED,
    REQUIRED_SENSITIVITY_AREAS,
    REQUIRED_STATUSES,
    RF_DONOR_WEIGHT,
    SCMJackknifeSensitivityInput,
    SensitivityArea,
    SensitivityStatus,
    _AUTH_FLAGS,
    _SCM_FLAGS,
    build_scm_jackknife_sensitivity_area_registry,
    build_scm_jackknife_sensitivity_evidence,
    build_scenarios,
    run_validation,
    validate_scm_jackknife_sensitivity_implementation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001_REPORT.md"


def test_all_sensitivity_areas_present() -> None:
    registry = build_scm_jackknife_sensitivity_area_registry()
    assert len(registry) == len(REQUIRED_SENSITIVITY_AREAS)
    assert {r.sensitivity_area for r in registry} == set(REQUIRED_SENSITIVITY_AREAS)


def test_input_contract_fields() -> None:
    inp = SCMJackknifeSensitivityInput(
        scm_validation_evidence={"input_contract_satisfied": True},
        scm_null_calibration_evidence={"input_contract_satisfied": True},
        panel_metadata={"grain": "weekly"},
        treated_units=("a",),
        donor_units=("b", "c"),
        time_index=("t1",),
        pre_period=("t1",),
        post_period=("t2",),
        donor_weight_metadata={"weights_defined": True},
        treated_set_metadata={"treated_set_id": "set_a"},
    )
    assert inp.scm_validation_evidence["input_contract_satisfied"] is True
    assert len(inp.treated_units) == 1


def test_evidence_contract_fields() -> None:
    evidence = build_scm_jackknife_sensitivity_evidence(SCMJackknifeSensitivityInput())
    assert hasattr(evidence, "input_contract_status")
    assert hasattr(evidence, "causal_ci_boundary_status")
    assert hasattr(evidence, "p_value_boundary_status")
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
        assert SensitivityStatus(status) in REQUIRED_STATUSES


def test_all_authorization_flags_false() -> None:
    evidence = build_scm_jackknife_sensitivity_evidence(SCMJackknifeSensitivityInput())
    for flag in _AUTH_FLAGS:
        assert evidence.authorization_flags[flag] is False
    for flag, expected in _SCM_FLAGS.items():
        assert expected is False


def test_missing_validation_evidence_blocked() -> None:
    evidence = build_scm_jackknife_sensitivity_evidence(SCMJackknifeSensitivityInput())
    assert BR_VALIDATION_EVIDENCE_MISSING in evidence.blocked_reasons


def test_missing_null_calibration_evidence_blocked() -> None:
    inp = SCMJackknifeSensitivityInput(
        scm_validation_evidence={"input_contract_satisfied": True},
        panel_metadata={"grain": "weekly"},
        treated_units=("a",),
        donor_units=("b", "c"),
        time_index=("t1",),
        pre_period=("t1",),
        post_period=("t2",),
    )
    evidence = build_scm_jackknife_sensitivity_evidence(inp)
    assert BR_NULL_CALIBRATION_EVIDENCE_MISSING in evidence.blocked_reasons


def test_missing_deletion_metadata_blocked() -> None:
    inp = SCMJackknifeSensitivityInput(
        scm_validation_evidence={"input_contract_satisfied": True},
        scm_null_calibration_evidence={"input_contract_satisfied": True},
        panel_metadata={"grain": "weekly"},
        treated_units=("a",),
        donor_units=("b", "c"),
        time_index=("t1",),
        pre_period=("t1",),
        post_period=("t2",),
        treated_set_metadata={"treated_set_id": "set_a"},
        donor_weight_metadata={"weights_defined": True},
    )
    evidence = build_scm_jackknife_sensitivity_evidence(inp)
    assert BR_UNIT_DELETION_MISSING in evidence.blocked_reasons


def test_missing_donor_weight_produces_followup() -> None:
    inp = SCMJackknifeSensitivityInput(
        scm_validation_evidence={"input_contract_satisfied": True},
        scm_null_calibration_evidence={"input_contract_satisfied": True},
        panel_metadata={"grain": "weekly"},
        treated_units=("a",),
        donor_units=("b", "c"),
        time_index=("t1",),
        pre_period=("t1",),
        post_period=("t2",),
        treated_set_metadata={"treated_set_id": "set_a"},
    )
    evidence = build_scm_jackknife_sensitivity_evidence(inp)
    assert BR_DONOR_WEIGHT_METADATA_MISSING in evidence.blocked_reasons
    assert RF_DONOR_WEIGHT in evidence.required_followups


def test_missing_release_gate_produces_release_gate_required() -> None:
    evidence = build_scm_jackknife_sensitivity_evidence(SCMJackknifeSensitivityInput())
    assert evidence.release_gate_status == SensitivityStatus.RELEASE_GATE_REQUIRED
    assert BR_RELEASE_GATE_REQUIRED in evidence.blocked_reasons


def test_multicell_unvalidated_blocked() -> None:
    inp = SCMJackknifeSensitivityInput(
        scm_validation_evidence={"input_contract_satisfied": True},
        scm_null_calibration_evidence={"input_contract_satisfied": True},
        panel_metadata={"grain": "weekly"},
        treated_units=("a",),
        donor_units=("b", "c"),
        time_index=("t1",),
        pre_period=("t1",),
        post_period=("t2",),
        treated_set_metadata={"treated_set_id": "set_a"},
        donor_weight_metadata={"weights_defined": True},
        multicell_validation_state={
            "multicell_geometry_present": True,
            "dependence_multiplicity_validated": False,
        },
    )
    evidence = build_scm_jackknife_sensitivity_evidence(inp)
    assert evidence.multicell_status == SensitivityStatus.BLOCKED


def test_jackknife_incomplete_no_causal_ci_auth() -> None:
    evidence = build_scm_jackknife_sensitivity_evidence(SCMJackknifeSensitivityInput())
    assert BR_JACKKNIFE_INCOMPLETE in evidence.blocked_reasons
    assert evidence.authorization_flags["scm_causal_confidence_interval_authorized"] is False
    assert evidence.causal_ci_boundary_status == SensitivityStatus.BLOCKED


def test_p_value_boundary_unauthorized() -> None:
    evidence = build_scm_jackknife_sensitivity_evidence(SCMJackknifeSensitivityInput())
    assert evidence.authorization_flags["scm_production_p_value_authorized"] is False
    assert evidence.p_value_boundary_status == SensitivityStatus.BLOCKED


def test_blocked_reasons_and_followups_supported() -> None:
    assert len(BLOCKED_REASONS_SUPPORTED) >= 10
    assert len(REQUIRED_FOLLOWUPS_SUPPORTED) >= 8


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_validate_implementation() -> None:
    registry = build_scm_jackknife_sensitivity_area_registry()
    evidence = build_scm_jackknife_sensitivity_evidence(SCMJackknifeSensitivityInput())
    result = validate_scm_jackknife_sensitivity_implementation(registry, evidence)
    assert result["valid"]
    assert result["all_areas_covered"]


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001"
    assert data["failed_scenarios"] == []
    assert data["scm_jackknife_sensitivity_implementation_authorized"] is False
    assert data["scm_jackknife_sensitivity_completed"] is False
    assert data["scm_production_inference_authorized"] is False
    assert data["final_verdict"] == (
        "scm_production_candidate_jackknife_sensitivity_metadata_implemented_no_downstream_authorization"
    )
    assert data["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001"
    assert data["implemented_input_contract"] == "SCMJackknifeSensitivityInput"
    assert data["implemented_evidence_contract"] == "SCMJackknifeSensitivityEvidence"
    assert len(data["implemented_sensitivity_areas"]) == len(REQUIRED_SENSITIVITY_AREAS)


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "metadata scaffolding" in text.lower()
    assert "gated production-candidate" in text.lower()
    assert "not a causal confidence interval" in text.lower() or "does not compute" in text.lower()
    assert "release gate remains required" in text.lower()
