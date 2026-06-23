"""Tests for METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.method_accuracy_compatibility_refocus_audit_001 import (
    AccuracyCompatibilityWorkBucket,
    RefocusPriority,
    build_method_accuracy_compatibility_backlog,
    run_method_accuracy_compatibility_refocus_audit,
    validate_method_accuracy_compatibility_refocus_audit,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001_summary.json"


def test_backlog_builds() -> None:
    backlog = build_method_accuracy_compatibility_backlog()
    assert len(backlog) >= 10


def test_p0_null_calibration_items() -> None:
    backlog = build_method_accuracy_compatibility_backlog()
    by_id = {i.item_id: i for i in backlog}
    for item_id in (
        "studentized_randomization_null_calibration",
        "scm_treated_set_placebo_null_calibration",
        "scm_augsynth_statistic_adapter_contract",
    ):
        assert by_id[item_id].priority == RefocusPriority.P0


def test_p1_items_exist() -> None:
    backlog = build_method_accuracy_compatibility_backlog()
    by_id = {i.item_id: i for i in backlog}
    assert by_id["multicell_max_t_research_scout"].work_bucket == (
        AccuracyCompatibilityWorkBucket.MULTICELL_DEPENDENCE_RESEARCH
    )
    assert by_id["tbrridge_inference_remediation_or_retirement"].priority == RefocusPriority.P1
    assert by_id["augsynth_jk_retirement_or_replacement"].priority == RefocusPriority.P1


def test_p2_and_p3_items() -> None:
    backlog = build_method_accuracy_compatibility_backlog()
    by_id = {i.item_id: i for i in backlog}
    assert by_id["stratified_pooling_inference_scout"].priority == RefocusPriority.P2
    assert by_id["design_assignment_generator_stress_tests"].priority == RefocusPriority.P2
    assert by_id["dcm_009_019_adapter_disposition"].priority == RefocusPriority.P3


def test_downstream_pause_exists() -> None:
    backlog = build_method_accuracy_compatibility_backlog()
    pause = [i for i in backlog if i.work_bucket == AccuracyCompatibilityWorkBucket.DOWNSTREAM_PAUSE]
    assert len(pause) == 1


def test_non_pause_items_have_evidence() -> None:
    backlog = build_method_accuracy_compatibility_backlog()
    for item in backlog:
        if item.work_bucket != AccuracyCompatibilityWorkBucket.DOWNSTREAM_PAUSE:
            assert item.required_evidence
        assert item.root_issue
        assert item.stop_go_criteria
        assert "calibration_signal_authorization" in item.forbidden_outputs


def test_validation_passes() -> None:
    backlog = build_method_accuracy_compatibility_backlog()
    result = validate_method_accuracy_compatibility_refocus_audit(backlog)
    assert result["valid"]
    assert result["downstream_work_paused"]
    assert (
        result["recommended_first_implementation_artifact"]
        == "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001"
    )


def test_harness_no_failed_scenarios() -> None:
    summary = run_method_accuracy_compatibility_refocus_audit()
    assert summary["failed_scenarios"] == []
    assert summary["verdict"] == "refocus_on_method_accuracy_and_compatibility"


def test_harness_authorization_flags_false() -> None:
    summary = run_method_accuracy_compatibility_refocus_audit()
    for key in (
        "calibration_signal_allowed",
        "trustreport_authorized",
        "mmm_ingestion_allowed",
        "llm_decisioning_allowed",
        "production_decisioning_allowed",
        "live_api_authorized",
        "scheduler_authorized",
        "budget_optimization_allowed",
    ):
        assert summary[key] is False


def test_summary_json_flags_false() -> None:
    if not _SUMMARY.exists():
        return
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["downstream_work_paused"] is True
    for key in (
        "calibration_signal_allowed",
        "trustreport_authorized",
        "mmm_ingestion_allowed",
    ):
        assert data[key] is False
