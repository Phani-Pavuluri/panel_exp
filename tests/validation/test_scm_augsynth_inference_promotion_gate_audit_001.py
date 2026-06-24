"""Tests for SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.scm_augsynth_inference_promotion_gate_audit_001 import (
    MIN_GATE_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    REQUIRED_PATHS,
    REQUIRED_STATUSES,
    EstimatorFamily,
    GateStatus,
    InferencePath,
    _AUTH_FLAGS,
    _GATE_FLAGS,
    build_scm_augsynth_inference_promotion_gate_audit,
    build_scenarios,
    filter_scm_augsynth_inference_promotion_gate_audit,
    run_validation,
    summarize_scm_augsynth_inference_promotion_gate_audit,
    validate_scm_augsynth_inference_promotion_gate_audit,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001_summary.json"
_REPORT = _REPO / "docs/track_d/SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001_REPORT.md"


def test_gate_rows_build_and_minimum_count() -> None:
    rows = build_scm_augsynth_inference_promotion_gate_audit()
    assert len(rows) >= MIN_GATE_ROW_COUNT
    assert len({r.gate_id for r in rows}) == len(rows)


def test_all_paths_and_statuses_represented() -> None:
    rows = build_scm_augsynth_inference_promotion_gate_audit()
    validation = validate_scm_augsynth_inference_promotion_gate_audit(rows)
    assert validation["valid"]
    assert validation["all_required_paths_covered"]
    assert validation["all_statuses_represented"]


def test_summary_flags() -> None:
    rows = build_scm_augsynth_inference_promotion_gate_audit()
    summary = summarize_scm_augsynth_inference_promotion_gate_audit(rows)
    for flag, expected in _GATE_FLAGS.items():
        assert summary[flag] is expected
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["verdict"] == "scm_augsynth_inference_promotion_gate_audit_completed_no_downstream_authorization"


def test_no_downstream_authorization() -> None:
    rows = build_scm_augsynth_inference_promotion_gate_audit()
    summary = summarize_scm_augsynth_inference_promotion_gate_audit(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False


def test_filter_helpers() -> None:
    rows = build_scm_augsynth_inference_promotion_gate_audit()
    scm_point = filter_scm_augsynth_inference_promotion_gate_audit(
        rows, inference_path=InferencePath.SCM_POINT_ESTIMATE
    )
    assert scm_point
    blocked = filter_scm_augsynth_inference_promotion_gate_audit(
        rows, current_status=GateStatus.BLOCKED
    )
    assert len(blocked) >= 5
    augsynth = filter_scm_augsynth_inference_promotion_gate_audit(
        rows, estimator_family=EstimatorFamily.AUGSYNTH_CVXPY
    )
    assert augsynth
    disagreement = filter_scm_augsynth_inference_promotion_gate_audit(
        rows, inference_path=InferencePath.SCM_AUGSYNTH_DISAGREEMENT_GATE
    )
    assert disagreement


def test_required_fields_nonempty() -> None:
    rows = build_scm_augsynth_inference_promotion_gate_audit()
    for row in rows:
        assert row.required_design_conditions
        assert row.required_observed_diagnostics
        assert row.required_dgp_coverage
        assert row.required_failure_registry_checks
        assert row.promotion_evidence_required
        assert row.forbidden_current_use


def test_summary_count_consistency() -> None:
    rows = build_scm_augsynth_inference_promotion_gate_audit()
    summary = summarize_scm_augsynth_inference_promotion_gate_audit(rows)
    validation = validate_scm_augsynth_inference_promotion_gate_audit(rows)
    assert summary["gate_row_count"] == len(rows)
    assert summary["status_counts"] == validation["status_counts"]
    assert summary["estimator_family_counts"] == validation["estimator_family_counts"]
    assert summary["inference_path_counts"] == validation["inference_path_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001"
    assert data["failed_scenarios"] == []
    assert data["gate_row_count"] >= MIN_GATE_ROW_COUNT
    assert data["all_required_paths_covered"] is True
    for path in REQUIRED_PATHS:
        assert data["inference_path_counts"].get(path.value, 0) > 0
    for status in REQUIRED_STATUSES:
        assert data["status_counts"].get(status.value, 0) > 0


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "does not authorize production inference" in text
    assert "does not authorize production p-values" in text
    assert "does not authorize causal confidence intervals" in text
    assert "TrustReport" in text
