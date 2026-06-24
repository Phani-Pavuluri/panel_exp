"""Tests for TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.tbrridge_inference_remediation_or_retirement_audit_001 import (
    MIN_AUDIT_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    AuditRequiredAction,
    AuditStatus,
    TbrridgePath,
    _AUTH_FLAGS,
    _TBRRIDGE_AUTH_FLAGS,
    build_scenarios,
    build_tbrridge_inference_remediation_or_retirement_audit,
    filter_tbrridge_inference_audit_rows,
    run_validation,
    summarize_tbrridge_inference_remediation_or_retirement_audit,
    validate_tbrridge_inference_remediation_or_retirement_audit,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001_summary.json"
_REPORT = _REPO / "docs/track_d/TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001_REPORT.md"


def test_audit_rows_build_and_minimum_count() -> None:
    rows = build_tbrridge_inference_remediation_or_retirement_audit()
    assert len(rows) >= MIN_AUDIT_ROW_COUNT
    assert len({r.path_id for r in rows}) == len(rows)


def test_all_paths_statuses_and_actions_represented() -> None:
    rows = build_tbrridge_inference_remediation_or_retirement_audit()
    validation = validate_tbrridge_inference_remediation_or_retirement_audit(rows)
    assert validation["valid"]
    assert validation["all_paths_represented"]
    assert validation["all_statuses_represented"]
    assert validation["all_actions_represented"]


def test_summary_flags() -> None:
    rows = build_tbrridge_inference_remediation_or_retirement_audit()
    summary = summarize_tbrridge_inference_remediation_or_retirement_audit(rows)
    assert summary["tbrridge_point_diagnostic_allowed"] is True
    assert summary["tbrridge_production_inference_authorized"] is False
    assert summary["tbrridge_production_p_value_authorized"] is False
    assert summary["tbrridge_causal_ci_authorized"] is False
    assert summary["brb_production_authorized"] is False
    assert summary["kfold_production_authorized"] is False
    assert summary["placebo_production_authorized"] is False
    assert summary["jackknife_production_authorized"] is False
    assert summary["aggregate_global_overclaim_blocked"] is True
    assert summary["retire_or_replace_paths_defined"] is True
    assert summary["remediation_paths_defined"] is True
    assert summary["future_validation_required_before_promotion"] is True
    assert summary["observed_diagnostics_required"] is True
    assert summary["dgp_coverage_required"] is True
    assert summary["failure_registry_consulted"] is True
    assert summary["design_assignment_stress_required"] is True
    assert summary["downstream_work_paused"] is True
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]


def test_no_downstream_authorization() -> None:
    rows = build_tbrridge_inference_remediation_or_retirement_audit()
    summary = summarize_tbrridge_inference_remediation_or_retirement_audit(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False
    for flag in _TBRRIDGE_AUTH_FLAGS:
        if flag.endswith("_authorized") or flag.endswith("_allowed"):
            if flag in (
                "tbrridge_point_diagnostic_allowed",
            ):
                assert summary[flag] is True
            else:
                assert summary[flag] is False
        elif flag.endswith("_blocked") or flag.endswith("_defined") or flag.endswith("_required") or flag.endswith("_consulted") or flag.endswith("_paused"):
            assert summary[flag] is True


def test_filter_helpers() -> None:
    rows = build_tbrridge_inference_remediation_or_retirement_audit()
    brb = filter_tbrridge_inference_audit_rows(rows, tbrridge_path=TbrridgePath.BRB)
    assert brb
    blocked = filter_tbrridge_inference_audit_rows(rows, current_status=AuditStatus.BLOCKED)
    assert len(blocked) >= 5
    retire = filter_tbrridge_inference_audit_rows(rows, retire_or_replace_candidate=True)
    assert retire
    remediate = filter_tbrridge_inference_audit_rows(rows, remediation_candidate=True)
    assert remediate
    promotion = filter_tbrridge_inference_audit_rows(rows, promotion_blocking=True)
    assert promotion
    action = filter_tbrridge_inference_audit_rows(rows, required_action=AuditRequiredAction.BLOCK)
    assert action


def test_required_fields_nonempty() -> None:
    rows = build_tbrridge_inference_remediation_or_retirement_audit()
    for row in rows:
        assert row.affected_designs
        assert row.affected_inference_paths
        assert row.dgp_triggers
        if row.path_id != "TBR-AUD-070":
            assert row.observed_diagnostic_triggers
            assert row.failure_modes


def test_summary_count_consistency() -> None:
    rows = build_tbrridge_inference_remediation_or_retirement_audit()
    summary = summarize_tbrridge_inference_remediation_or_retirement_audit(rows)
    validation = validate_tbrridge_inference_remediation_or_retirement_audit(rows)
    assert summary["audit_row_count"] == len(rows)
    assert summary["status_counts"] == validation["status_counts"]
    assert summary["required_action_counts"] == validation["required_action_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"
    assert data["failed_scenarios"] == []
    assert data["audit_row_count"] >= MIN_AUDIT_ROW_COUNT
