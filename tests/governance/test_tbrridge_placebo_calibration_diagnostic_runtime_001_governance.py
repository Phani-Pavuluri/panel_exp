"""Governance registry tests for TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_summary_runtime_complete() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001"
    assert data["placebo_calibration_runtime_implemented"] is True
    assert data["placebo_inference_implemented"] is False


def test_governance_registry_references_runtime() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-PLACEBO-CALIBRATION-DIAGNOSTIC-RUNTIME-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-PLACEBO-CALIBRATION-DIAGNOSTIC-RUNTIME-001" in lane_ids
