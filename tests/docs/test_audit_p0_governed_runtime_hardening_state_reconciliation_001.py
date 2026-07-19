from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
REPORT = ROOT / "docs/track_d/AUDIT_P0_GOVERNED_RUNTIME_HARDENING_STATE_RECONCILIATION_001.md"
SUMMARY = ROOT / "docs/track_d/archives/AUDIT_P0_GOVERNED_RUNTIME_HARDENING_STATE_RECONCILIATION_001_summary.json"


def test_reconciliation_artifacts_exist_and_parse() -> None:
    assert REPORT.is_file()
    assert SUMMARY.is_file()
    summary = json.loads(SUMMARY.read_text())
    assert summary["artifact_id"] == "AUDIT_P0_GOVERNED_RUNTIME_HARDENING_STATE_RECONCILIATION_001"
    assert summary["status"] == "completed"


def test_forbidden_authorizations_are_false() -> None:
    summary = json.loads(SUMMARY.read_text())
    for key in (
        "production_inference_authorized",
        "assignment_authorized",
        "causal_readout_authorized",
        "calibration_signal_export_authorized",
        "mip_experiment_evidence_export_authorized",
        "selector_router_runtime_authorized",
        "multicell_production_claim_authorized",
        "agent_work_authorized",
    ):
        assert summary[key] is False


def test_decision_and_reconciliation_table_are_valid() -> None:
    summary = json.loads(SUMMARY.read_text())
    assert summary["decision"] in {
        "PROCEED_TO_GEOX_MIP_GOVERNED_EXPERIMENT_ARTIFACT_ENVELOPE_AND_COMPATIBILITY",
        "PROCEED_TO_REMAINING_P0_GOVERNED_RUNTIME_HARDENING_PLAN",
        "BLOCK_NEXT_GEOX_WORK_PENDING_REPOSITORY_STATE_REVIEW",
    }
    assert summary["recommended_next_artifact"] in {
        "GEOX_MIP_GOVERNED_EXPERIMENT_ARTIFACT_ENVELOPE_AND_COMPATIBILITY_001",
        "REMAINING_P0_GOVERNED_RUNTIME_HARDENING_PLAN_001",
        "REPOSITORY_STATE_REVIEW_BEFORE_GEOX_NEXT_WORK_001",
    }
    report = REPORT.read_text()
    for keyword in (
        "production blocklist enforcement",
        "DID instrument/estimand alignment",
        "assignment-panel integrity",
        "run manifest lifecycle",
        "MIP-compatible ExperimentEvidence mapping",
        "CalibrationSignal eligibility/export",
        "production selector/router authorization",
    ):
        assert keyword in report


def test_alignment_dependency_is_referenced() -> None:
    report = REPORT.read_text()
    assert "GEOX_MIP_PRODUCTION_ALIGNMENT_READINESS_AUDIT_001" in report
    assert "GEOX_MIP_GOVERNED_EXPERIMENT_ARTIFACT_ENVELOPE_AND_COMPATIBILITY_001" in report
