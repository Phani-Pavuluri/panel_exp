"""Tests for ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.roadmap_implementation_detail_gap_audit_001 import (
    AUDIT_RESULT,
    HIGH_RISK_GAP_AREAS,
    RECOMMENDED_NEXT_ARTIFACT,
    REQUIRED_CONTRACT_ARTIFACTS,
    REVISED_ROADMAP_SEQUENCE,
    SCM_ESTIMATOR_CLAIM_LANE_STATUS,
    _AUTH_FLAGS,
    build_roadmap_implementation_detail_gap_audit,
    build_scenarios,
    run_validation,
    validate_roadmap_implementation_detail_gap_audit,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001_summary.json"
_REPORT = _REPO / "docs/track_d/ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001_REPORT.md"


def test_audit_result_and_scm_lane() -> None:
    audit = build_roadmap_implementation_detail_gap_audit()
    assert audit.audit_result == AUDIT_RESULT
    assert "dedicated_scm" in audit.scm_estimator_claim_lane_status


def test_required_contract_artifacts() -> None:
    audit = build_roadmap_implementation_detail_gap_audit()
    assert audit.required_contract_artifacts == REQUIRED_CONTRACT_ARTIFACTS
    assert "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001" in audit.required_contract_artifacts
    assert "DESIGN_BASED_INFERENCE_TOOLING_CONTRACT_001" in audit.required_contract_artifacts
    assert "LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001" in audit.required_contract_artifacts


def test_high_risk_gap_areas() -> None:
    audit = build_roadmap_implementation_detail_gap_audit()
    assert audit.high_risk_gap_areas == HIGH_RISK_GAP_AREAS
    assert len(audit.high_risk_gap_areas) == 7


def test_revised_roadmap_sequence() -> None:
    audit = build_roadmap_implementation_detail_gap_audit()
    assert audit.revised_roadmap_sequence == REVISED_ROADMAP_SEQUENCE
    idx = audit.revised_roadmap_sequence.index("ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001")
    assert audit.revised_roadmap_sequence[idx - 1] == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001"
    assert audit.revised_roadmap_sequence[idx + 1] == RECOMMENDED_NEXT_ARTIFACT


def test_all_authorization_flags_false() -> None:
    audit = build_roadmap_implementation_detail_gap_audit()
    for flag, expected in _AUTH_FLAGS.items():
        assert audit.authorization_flags[flag] is expected


def test_validate_audit() -> None:
    audit = build_roadmap_implementation_detail_gap_audit()
    result = validate_roadmap_implementation_detail_gap_audit(audit)
    assert result["valid"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001"
    assert data["failed_scenarios"] == []
    assert data["audit_result"] == AUDIT_RESULT
    assert data["scm_estimator_claim_lane_status"] == SCM_ESTIMATOR_CLAIM_LANE_STATUS
    assert data["recommended_next_artifact"] == "GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001"
    assert data["final_verdict"] == "roadmap_implementation_detail_gap_audit_logged_contracts_required_no_runtime_authorization"


def test_report_states_no_runtime_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "implementation detail" in text.lower() or "implementation-detail" in text.lower()
    assert "scm" in text.lower()
    assert "no runtime authorization" in text.lower() or "no runtime" in text.lower()
    assert "ballpark" in text.lower()
    assert "shared-control" in text.lower() or "shared control" in text.lower()
