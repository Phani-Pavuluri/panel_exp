"""Tests for DESIGN-AWARE-ASSIGNMENT-GENERATORS-001 validation harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.design_aware_assignment_generators_001 import (
    _ARTIFACT_ID,
    build_summary,
    run_validation,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY_PATH = _REPO / "docs/track_d/archives/DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_summary.json"
REPORT_PATH = _REPO / "docs/track_d/DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_REPORT.md"


def test_build_summary_contract():
    summary = build_summary()
    assert summary["artifact_id"] == _ARTIFACT_ID
    assert summary["trustreport_authorized"] is False
    assert summary["calibration_signal_allowed"] is False
    assert summary["production_decisioning_allowed"] is False
    assert summary["governance_verdict"] == (
        "design_aware_assignment_generators_defined_no_inference_authorization"
    )
    assert summary["next_artifact"] == "MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001"
    assert summary["determinism_checks"]["passed"] is True
    assert not summary["failed_scenarios"]


def test_run_validation_strict_passes():
    run_validation(strict=True)


def test_write_summary_roundtrip(tmp_path: Path):
    summary = build_summary()
    out = tmp_path / "summary.json"
    write_summary(out, summary, overwrite=True)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["artifact_id"] == _ARTIFACT_ID


def test_report_exists():
    assert REPORT_PATH.is_file()


def test_summary_file_matches_harness_when_present():
    if not SUMMARY_PATH.is_file():
        pytest.skip("committed summary not generated in this workspace")
    on_disk = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    assert on_disk["governance_verdict"] == (
        "design_aware_assignment_generators_defined_no_inference_authorization"
    )
