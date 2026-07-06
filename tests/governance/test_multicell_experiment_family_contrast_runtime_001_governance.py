"""Governance registry tests for MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_summary_runtime_complete() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001"
    assert data["runtime_implemented"] is True
    assert data["multiplicity_correction_computed"] is False


def test_governance_registry_references_runtime() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-MULTICELL-EXPERIMENT-FAMILY-CONTRAST-RUNTIME-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "MULTICELL-EXPERIMENT-FAMILY-CONTRAST-RUNTIME-001" in lane_ids
