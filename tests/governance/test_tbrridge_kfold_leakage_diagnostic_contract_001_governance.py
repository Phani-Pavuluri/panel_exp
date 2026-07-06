"""Governance registry tests for TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_summary_complete() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001"
    assert data["kfold_leakage_diagnostic_contract_defined"] is True
    assert data["kfold_inference_implemented"] is False


def test_governance_registry_references_contract() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-KFOLD-LEAKAGE-DIAGNOSTIC-CONTRACT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-KFOLD-LEAKAGE-DIAGNOSTIC-CONTRACT-001" in lane_ids
