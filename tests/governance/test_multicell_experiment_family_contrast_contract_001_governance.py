"""Governance registry tests for MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001_REPORT.md"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_implemented",
    "multiplicity_correction_computed",
    "covariance_computed",
    "winner_claim_authorized",
    "production_recommendation_authorized",
    "method_promoted",
    "production_catalog_unblocked",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_report_and_summary_exist() -> None:
    assert _REPORT.exists()
    assert _SUMMARY.exists()
    data = _load_summary()
    assert data["artifact_id"] == "MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001"
    assert data["status"] == "completed"


def test_independent_experiment_exemption_in_report() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "INDEPENDENT_EXPERIMENTS" in text
    assert "independent experiments are exempt" in text.lower()


def test_forbidden_flags_false_in_summary() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data[flag] is False, flag


def test_recommended_next_artifact_present() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001"
    assert data["final_verdict"] == "multicell_experiment_family_and_contrast_contract_defined_no_runtime_or_inference"


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-MULTICELL-EXPERIMENT-FAMILY-CONTRAST-CONTRACT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "MULTICELL-EXPERIMENT-FAMILY-CONTRAST-CONTRACT-001" in lane_ids
    inv = next(
        i for i in reg["investigations"]
        if i["investigation_id"] == "INV-MULTICELL-EXPERIMENT-FAMILY-CONTRAST-CONTRACT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001"
