"""Validation harness tests for ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.estimator_design_inference_suitability_matrix_001 import (
    ROADMAP_SPINE,
    _AUTH_FLAGS,
    build_scenarios,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001_summary.json"


def test_harness_scenarios_all_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_harness_run_validation_no_failures() -> None:
    result = run_validation(write_summary=False)
    assert result["failed_scenarios"] == []
    assert result["verdict"] == (
        "estimator_design_inference_suitability_matrix_defined_no_downstream_authorization"
    )
    assert result["row_count"] >= 35


def test_summary_json_exists_and_flags_false() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001"
    assert data["failed_scenarios"] == []
    assert data["placebo_is_only_inference_layer"] is False
    assert data["downstream_work_paused"] is True
    for flag in _AUTH_FLAGS:
        assert data[flag] is False


def test_roadmap_spine_includes_artifact() -> None:
    assert "ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001" in ROADMAP_SPINE
