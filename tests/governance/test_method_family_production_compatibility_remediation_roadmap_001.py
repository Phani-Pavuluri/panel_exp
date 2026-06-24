"""Tests for METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.governance.investigation_lifecycle_contract import load_registry

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001_summary.json"
_REPORT = _REPO / "docs/track_d/METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001.md"

_REQUIRED_FAMILIES = frozenset({
    "scm",
    "augsynth_cvxpy",
    "did",
    "synthetic_did",
    "tbrridge",
    "tbr_aggregate",
    "bayesian_tbr",
    "trop",
    "multicell_shared_control",
})

_AUTH_FLAGS = (
    "production_p_value_authorized",
    "causal_confidence_interval_authorized",
    "trustreport_authorized",
    "calibration_signal_allowed",
    "mmm_ingestion_allowed",
    "llm_decisioning_allowed",
    "production_decisioning_allowed",
    "live_api_authorized",
    "scheduler_authorized",
    "budget_optimization_allowed",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_summary_json_and_report_exist() -> None:
    assert _SUMMARY.is_file()
    assert _REPORT.is_file()
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001"


def test_all_required_families_covered() -> None:
    data = _load_summary()
    covered = set(data["families_covered"])
    assert _REQUIRED_FAMILIES <= covered
    assert data["estimator_family_count"] == len(data["families"])
    assert data["all_required_families_covered"] is True


def test_failed_scenarios_empty_and_flags() -> None:
    data = _load_summary()
    assert data["failed_scenarios"] == []
    assert data["non_production_methods_have_remediation_or_exit_paths"] is True
    assert data["research_only_does_not_mean_abandoned"] is True
    assert data["diagnostic_only_does_not_mean_abandoned"] is True
    assert data["promotion_evidence_required_for_all_candidates"] is True
    assert data["retirement_criteria_defined"] is True
    assert data["multicell_shared_control_identified_as_cross_cutting_blocker"] is True
    assert data["downstream_work_paused"] is True
    assert data["next_artifact"] == "MULTICELL_MAX_T_RESEARCH_SCOUT_001"


def test_family_records_have_exit_paths() -> None:
    data = _load_summary()
    for family in data["families"]:
        assert family["has_remediation_or_exit_path"] is True
        assert family["promotion_evidence_required"] is True
        assert family["retirement_criteria_defined"] is True
        assert family["research_only_not_abandoned"] is True
        assert family["diagnostic_only_not_abandoned"] is True
        assert family["downstream_authorization_status"] == "paused"


def test_no_downstream_authorization() -> None:
    data = _load_summary()
    for flag in _AUTH_FLAGS:
        assert data[flag] is False


def test_forward_sequence_documented() -> None:
    data = _load_summary()
    assert data["recommended_forward_sequence"][0] == "MULTICELL_MAX_T_RESEARCH_SCOUT_001"
    assert "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001" in data["recommended_forward_sequence"]


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "does not authorize production inference" in text
    assert "does not authorize production p-values" in text
    assert "does not authorize causal confidence intervals" in text
    assert "TrustReport" in text
