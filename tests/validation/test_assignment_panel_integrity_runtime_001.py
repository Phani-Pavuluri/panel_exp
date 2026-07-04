"""Tests for ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from panel_exp.validation.assignment_panel_integrity_runtime_001 import (
    ASSIGNMENT_PANEL_INTEGRITY_BLOCKED,
    ASSIGNMENT_PANEL_INTEGRITY_FAILED,
    ASSIGNMENT_PANEL_INTEGRITY_NOT_EVALUATED,
    ASSIGNMENT_PANEL_INTEGRITY_PASSED,
    ASSIGNMENT_PANEL_INTEGRITY_PASSED_WITH_WARNINGS,
    AssignmentPanelIntegrityConfig,
    AssignmentPanelIntegrityReport,
    check_assignment_panel_integrity,
    evaluate_assignment_panel_integrity,
    run_validation,
    validate_assignment_panel_integrity,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001_summary.json"


def _allocations(extra: str | None = None) -> list[dict]:
    rows = [
        {"unit_id": "u1", "assigned_cell_id": "C1", "assigned_cell_role": "TREATMENT"},
        {"unit_id": "u2", "assigned_cell_id": "C0", "assigned_cell_role": "CONTROL"},
    ]
    if extra:
        rows.append(
            {"unit_id": extra, "assigned_cell_id": "C2", "assigned_cell_role": "TREATMENT"}
        )
    return rows


def _panel(extra: dict | None = None) -> list[dict]:
    rows = [
        {"unit_id": "u1", "treated": 1, "cell_id": "C1"},
        {"unit_id": "u2", "treated": 0, "cell_id": "C0"},
    ]
    if extra:
        rows.append(extra)
    return rows


def _base_request(**extra: object) -> dict:
    payload = {
        "request_id": "integrity_test_001",
        "assignment_artifact": {"artifact_id": "assign_001"},
        "assignment_artifact_id": "assign_001",
        "unit_allocations": _allocations(),
        "panel_records": _panel(),
    }
    payload.update(extra)
    return payload


def test_public_api_exists() -> None:
    report = evaluate_assignment_panel_integrity(_base_request())
    assert isinstance(report, AssignmentPanelIntegrityReport)
    alias = validate_assignment_panel_integrity(_base_request())
    assert alias.status == ASSIGNMENT_PANEL_INTEGRITY_PASSED
    assert check_assignment_panel_integrity(_base_request()).can_proceed_to_execution is True


def test_passes_when_panel_matches_assignment() -> None:
    report = evaluate_assignment_panel_integrity(_base_request())
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_PASSED
    assert report.matched_unit_count == 2
    assert report.is_blocking is False


def test_passes_with_warnings_when_assigned_units_absent_from_panel() -> None:
    report = evaluate_assignment_panel_integrity(
        _base_request(unit_allocations=_allocations("u3")),
        config={"allow_warnings_for_extra_assigned_units_not_in_panel": True},
    )
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_PASSED_WITH_WARNINGS
    assert "u3" in report.missing_panel_units
    assert report.can_proceed_to_execution is True


def test_fails_when_panel_unit_not_in_assignment() -> None:
    report = evaluate_assignment_panel_integrity(
        _base_request(panel_records=_panel({"unit_id": "u9", "treated": 1, "cell_id": "C9"}))
    )
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_FAILED
    assert "u9" in report.unassigned_panel_units


def test_fails_when_treatment_label_mismatches() -> None:
    panel = [
        {"unit_id": "u1", "treated": 0, "cell_id": "C1"},
        {"unit_id": "u2", "treated": 0, "cell_id": "C0"},
    ]
    report = evaluate_assignment_panel_integrity(_base_request(panel_records=panel))
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_FAILED
    assert "u1" in report.treatment_mismatches


def test_fails_when_cell_label_mismatches() -> None:
    panel = [
        {"unit_id": "u1", "treated": 1, "cell_id": "WRONG"},
        {"unit_id": "u2", "treated": 0, "cell_id": "C0"},
    ]
    report = evaluate_assignment_panel_integrity(_base_request(panel_records=panel))
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_FAILED
    assert "u1" in report.cell_mismatches


def test_fails_on_duplicate_assignment_conflicting_labels() -> None:
    allocations = [
        {"unit_id": "u1", "assigned_cell_id": "C1", "assigned_cell_role": "TREATMENT"},
        {"unit_id": "u1", "assigned_cell_id": "C2", "assigned_cell_role": "CONTROL"},
        {"unit_id": "u2", "assigned_cell_id": "C0", "assigned_cell_role": "CONTROL"},
    ]
    report = evaluate_assignment_panel_integrity(_base_request(unit_allocations=allocations))
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_FAILED
    assert "u1" in report.duplicate_assignment_units


def test_fails_on_invalid_treatment_labels() -> None:
    allocations = [
        {"unit_id": "u1", "assigned_cell_id": "C1", "assigned_cell_role": "UNKNOWN"},
        {"unit_id": "u2", "assigned_cell_id": "C0", "assigned_cell_role": "CONTROL"},
    ]
    report = evaluate_assignment_panel_integrity(
        _base_request(unit_allocations=allocations),
        config={"allowed_treatment_labels": ("TREATED", "CONTROL")},
    )
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_FAILED
    assert report.invalid_treatment_labels


def test_fails_when_treated_group_missing() -> None:
    allocations = [
        {"unit_id": "u1", "assigned_cell_id": "C0", "assigned_cell_role": "CONTROL"},
        {"unit_id": "u2", "assigned_cell_id": "C0", "assigned_cell_role": "CONTROL"},
    ]
    report = evaluate_assignment_panel_integrity(_base_request(unit_allocations=allocations))
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_FAILED


def test_fails_when_control_group_missing() -> None:
    allocations = [
        {"unit_id": "u1", "assigned_cell_id": "C1", "assigned_cell_role": "TREATMENT"},
        {"unit_id": "u2", "assigned_cell_id": "C1", "assigned_cell_role": "TREATMENT"},
    ]
    report = evaluate_assignment_panel_integrity(_base_request(unit_allocations=allocations))
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_FAILED


def test_hash_mismatch_blocks_only_when_required() -> None:
    report = evaluate_assignment_panel_integrity(
        _base_request(
            assignment_hash="hash_a",
            expected_assignment_hash="hash_b",
            require_hash_match=True,
        )
    )
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_FAILED

    ok = evaluate_assignment_panel_integrity(
        _base_request(assignment_hash="hash_a", expected_assignment_hash="hash_b")
    )
    assert ok.status == ASSIGNMENT_PANEL_INTEGRITY_PASSED


def test_list_input_produces_multiple_reports_without_ranking() -> None:
    reports = evaluate_assignment_panel_integrity([_base_request(), _base_request(request_id="r2")])
    assert isinstance(reports, list)
    assert len(reports) == 2
    assert {r.request_id for r in reports} == {"integrity_test_001", "r2"}


@dataclass
class _IntegrityInput:
    assignment_artifact_id: str
    unit_allocations: list[dict]
    panel_records: list[dict]


def test_dataclass_like_input_supported() -> None:
    report = evaluate_assignment_panel_integrity(
        _IntegrityInput(
            assignment_artifact_id="assign_001",
            unit_allocations=_allocations(),
            panel_records=_panel(),
        )
    )
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_PASSED


def test_deterministic_trace_and_provenance_hash() -> None:
    r1 = evaluate_assignment_panel_integrity(_base_request())
    r2 = evaluate_assignment_panel_integrity(_base_request())
    assert isinstance(r1, AssignmentPanelIntegrityReport)
    assert r1.integrity_trace["integrity_hash"] == r2.integrity_trace["integrity_hash"]
    assert r1.provenance["integrity_hash"] == r2.provenance["integrity_hash"]


def test_missing_artifact_blocked() -> None:
    report = evaluate_assignment_panel_integrity({"panel_records": _panel()})
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_BLOCKED


def test_not_evaluated_without_panel_when_no_requirement() -> None:
    report = evaluate_assignment_panel_integrity(
        {},
        config={
            "require_assignment_artifact": False,
            "require_assignment_allocations": False,
            "require_panel_records": False,
        },
    )
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_NOT_EVALUATED


def test_claim_boundary_flags_remain_false() -> None:
    report = evaluate_assignment_panel_integrity(_base_request())
    assert isinstance(report, AssignmentPanelIntegrityReport)
    cb = report.claim_boundary_report
    assert cb["assignment_panel_integrity_runtime_implemented"] is True
    assert cb["claim_authorized"] is False
    assert cb["production_authorization_granted"] is False
    assert cb["assignment_generation_implemented"] is False


def test_run_validation_writes_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["final_verdict"] == (
        "assignment_panel_integrity_runtime_implemented_no_assignment_generation_or_claim_authorization"
    )
    assert _SUMMARY.exists()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["assignment_panel_integrity_runtime_implemented"] is True
