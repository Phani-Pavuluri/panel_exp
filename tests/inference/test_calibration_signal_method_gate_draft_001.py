"""Tests for CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001."""

from __future__ import annotations

from panel_exp.inference.calibration_signal_method_gate_draft import (
    CalibrationSignalGateStatus,
    build_calibration_signal_method_gate_draft,
    filter_calibration_gate_rows,
    find_calibration_gate_row,
    map_readiness_tier_to_calibration_gate_status,
    validate_calibration_signal_method_gate_draft,
)
from panel_exp.inference.method_readiness_matrix_v2 import (
    ReadinessTier,
    build_method_readiness_matrix_v2,
)

DOWNSTREAM_KEYS = (
    "calibration_signal_allowed",
    "calibration_signal_authorized",
    "trustreport_authorized",
    "mmm_ingestion_allowed",
    "llm_decisioning_allowed",
    "production_decisioning_allowed",
    "live_api_authorized",
    "scheduler_authorized",
    "budget_optimization_allowed",
)


def test_draft_builds_from_matrix() -> None:
    matrix = build_method_readiness_matrix_v2()
    draft = build_calibration_signal_method_gate_draft(matrix)
    assert draft.artifact_id == "CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001"
    assert len(draft.rows) == len(matrix.rows)


def test_row_count_matches_source() -> None:
    draft = build_calibration_signal_method_gate_draft()
    validation = validate_calibration_signal_method_gate_draft(draft)
    assert validation["row_count"] == validation["source_row_count"] == 25
    assert validation["method_ids_match_source_matrix"]


def test_method_ids_unique() -> None:
    draft = build_calibration_signal_method_gate_draft()
    ids = [r.method_id for r in draft.rows]
    assert len(ids) == len(set(ids))


def test_restricted_research_eligible_future_review() -> None:
    draft = build_calibration_signal_method_gate_draft()
    rows = [r for r in draft.rows if r.readiness_tier == ReadinessTier.RESTRICTED_RESEARCH_MODE_USABLE.value]
    assert len(rows) == 2
    assert all(r.gate_status == CalibrationSignalGateStatus.ELIGIBLE_FOR_FUTURE_REVIEW for r in rows)
    assert all(r.required_evidence_before_review for r in rows)


def test_framework_candidates_conditionally_reviewable() -> None:
    draft = build_calibration_signal_method_gate_draft()
    rows = [
        r
        for r in draft.rows
        if r.readiness_tier == ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE.value
    ]
    assert len(rows) == 3
    assert all(
        r.gate_status == CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE
        for r in rows
    )


def test_per_cell_marginal_conditionally_reviewable() -> None:
    draft = build_calibration_signal_method_gate_draft()
    row = find_calibration_gate_row(draft, "multicell_per_cell_marginal_only")
    assert row is not None
    assert row.gate_status == CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE
    assert "per_cell_only_calibration_signal_scope_rule" in row.categorical_exclusion_reasons


def test_contract_candidate_not_eligible() -> None:
    draft = build_calibration_signal_method_gate_draft()
    row = find_calibration_gate_row(draft, "stratified_pooled_estimand_contract_candidate")
    assert row is not None
    assert row.gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_CONTRACT_ONLY


def test_diagnostic_sensitivity_excluded() -> None:
    draft = build_calibration_signal_method_gate_draft()
    for r in draft.rows:
        if r.readiness_tier == ReadinessTier.DIAGNOSTIC_ONLY.value:
            assert r.gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_DIAGNOSTIC_ONLY
    sens = find_calibration_gate_row(draft, "scm_leave_one_treated_out_sensitivity_only")
    assert sens is not None
    assert sens.gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_SENSITIVITY_ONLY


def test_blocked_and_deferred_excluded() -> None:
    draft = build_calibration_signal_method_gate_draft()
    deferred = find_calibration_gate_row(draft, "dcm_009_019_adapters_research_deferred")
    assert deferred is not None
    assert deferred.gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_RESEARCH_DEFERRED
    for r in draft.rows:
        if r.readiness_tier == ReadinessTier.BLOCKED.value:
            assert r.gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_BLOCKED


def test_all_downstream_flags_false() -> None:
    draft = build_calibration_signal_method_gate_draft()
    for row in draft.rows:
        for key in DOWNSTREAM_KEYS:
            assert getattr(row, key) is False
    for key in DOWNSTREAM_KEYS:
        assert draft.downstream_authorization_flags[key] is False


def test_forbidden_outputs_on_all_rows() -> None:
    draft = build_calibration_signal_method_gate_draft()
    for row in draft.rows:
        assert "actual_calibration_signal_creation" in row.forbidden_outputs
        assert "calibration_signal_export" in row.forbidden_outputs
        assert "mmm_ingestion" in row.forbidden_outputs


def test_find_and_filter_helpers() -> None:
    draft = build_calibration_signal_method_gate_draft()
    assert find_calibration_gate_row(draft, "nonexistent") is None
    blocked = filter_calibration_gate_rows(
        draft, gate_status=CalibrationSignalGateStatus.NOT_ELIGIBLE_BLOCKED
    )
    assert len(blocked) == 7
    scm = filter_calibration_gate_rows(draft, method_family="scm")
    assert len(scm) >= 3


def test_tier_mapping() -> None:
    assert (
        map_readiness_tier_to_calibration_gate_status(
            ReadinessTier.RESTRICTED_RESEARCH_MODE_USABLE.value
        )
        == CalibrationSignalGateStatus.ELIGIBLE_FOR_FUTURE_REVIEW
    )
    assert (
        map_readiness_tier_to_calibration_gate_status(ReadinessTier.BLOCKED.value)
        == CalibrationSignalGateStatus.NOT_ELIGIBLE_BLOCKED
    )


def test_validation_passes() -> None:
    draft = build_calibration_signal_method_gate_draft()
    result = validate_calibration_signal_method_gate_draft(draft)
    assert result["valid"]
    assert sum(result["gate_status_counts"].values()) == result["row_count"]
