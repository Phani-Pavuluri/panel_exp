from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
REPORT = ROOT / "docs/track_d/GEOX_MIP_GOVERNED_EXPERIMENT_ARTIFACT_ENVELOPE_AND_COMPATIBILITY_001.md"
SUMMARY = ROOT / "docs/track_d/archives/GEOX_MIP_GOVERNED_EXPERIMENT_ARTIFACT_ENVELOPE_AND_COMPATIBILITY_001_summary.json"


def test_contract_artifacts_exist_and_parse() -> None:
    assert REPORT.is_file()
    assert SUMMARY.is_file()
    summary = json.loads(SUMMARY.read_text())
    assert summary["artifact_id"] == "GEOX_MIP_GOVERNED_EXPERIMENT_ARTIFACT_ENVELOPE_AND_COMPATIBILITY_001"
    assert summary["status"] == "completed"


def test_contract_preserves_non_authorization_boundaries() -> None:
    summary = json.loads(SUMMARY.read_text())
    for key in (
        "runtime_code_changed",
        "production_inference_authorized",
        "assignment_authorized",
        "causal_readout_authorized",
        "calibration_signal_export_authorized",
        "mip_experiment_evidence_export_authorized",
        "selector_router_runtime_authorized",
        "multicell_production_claim_authorized",
        "agent_work_authorized",
        "mip_repository_modified",
    ):
        assert summary[key] is False


def test_contract_decision_and_required_fields_are_present() -> None:
    summary = json.loads(SUMMARY.read_text())
    assert summary["decision"] in {
        "PROCEED_TO_NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_PLAN",
        "PROCEED_TO_GEOX_ARTIFACT_ENVELOPE_RUNTIME_CONTRACT",
        "BLOCK_GEOX_MIP_ENVELOPE_WORK_PENDING_P0_HARDENING",
    }
    assert summary["recommended_next_artifact"] in {
        "NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_PLAN_001",
        "GEOX_ARTIFACT_ENVELOPE_RUNTIME_CONTRACT_001",
        "REMAINING_P0_GOVERNED_RUNTIME_HARDENING_PLAN_001",
    }
    report = REPORT.read_text()
    for field in (
        "envelope_version",
        "artifact_kind",
        "artifact_id",
        "artifact_uri",
        "source_system",
        "source_repo",
        "source_commit",
        "created_at",
        "run_id",
        "experiment_id",
        "request_id",
        "input_data_fingerprint",
        "method_family",
        "instrument_id",
        "estimand",
        "kpi",
        "geo_scope",
        "time_window",
        "assignment_scope",
        "diagnostic_status",
        "method_readiness_status",
        "release_gate_status",
        "authorization_status",
        "blocked_reasons",
        "warnings",
        "upstream_artifacts",
        "downstream_eligibility",
        "mip_consumption_status",
        "provenance",
        "schema_hash",
    ):
        assert field in report


def test_artifact_kinds_and_compatibility_matrix_are_present() -> None:
    report = REPORT.read_text()
    for kind in (
        "geox_request",
        "geox_result",
        "assignment_candidate",
        "assignment_manifest",
        "run_manifest",
        "readout_packet",
        "failure_packet",
        "post-test spend evidence",
        "trusted readout spend handoff",
        "experiment_evidence_candidate",
        "calibration_signal_candidate",
    ):
        assert kind in report
    for keyword in (
        "Current MIP compatibility",
        "Missing/next work",
        "Allowed use now",
        "Blocked use",
        "MIP-compatible ExperimentEvidence",
        "CalibrationSignal",
    ):
        assert keyword in report
