from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
REPORT = ROOT / "docs/track_d/NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_PLAN_001.md"
SUMMARY = ROOT / "docs/track_d/archives/NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_PLAN_001_summary.json"


def test_plan_artifacts_exist_and_parse() -> None:
    assert REPORT.is_file()
    assert SUMMARY.is_file()
    summary = json.loads(SUMMARY.read_text())
    assert summary["artifact_id"] == "NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_PLAN_001"
    assert summary["status"] == "completed"


def test_plan_preserves_non_production_boundaries() -> None:
    summary = json.loads(SUMMARY.read_text())
    for key in (
        "runtime_code_changed", "production_inference_authorized", "assignment_authorized",
        "causal_readout_authorized", "calibration_signal_export_authorized",
        "mip_experiment_evidence_export_authorized", "trust_report_production_assembly_authorized",
        "decision_surface_authorized", "recommendation_contract_authorized", "llm_decisioning_authorized",
        "budget_optimization_authorized", "selector_router_runtime_authorized",
        "multicell_production_claim_authorized", "agent_work_authorized", "mip_repository_modified",
    ):
        assert summary[key] is False


def test_plan_decision_and_cases_are_present() -> None:
    summary = json.loads(SUMMARY.read_text())
    assert summary["decision"] in {
        "PROCEED_TO_GEOX_ARTIFACT_ENVELOPE_RUNTIME_CONTRACT",
        "PROCEED_TO_NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_RUNTIME",
        "BLOCK_DRY_RUN_RUNTIME_PENDING_ENVELOPE_OR_P0_GAPS",
    }
    assert summary["recommended_next_artifact"] in {
        "GEOX_ARTIFACT_ENVELOPE_RUNTIME_CONTRACT_001",
        "NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_RUNTIME_001",
        "REMAINING_P0_GOVERNED_RUNTIME_HARDENING_PLAN_001",
    }
    report = REPORT.read_text()
    for label in ("Case A", "Case B", "Case C", "Case D", "Case E", "Case F"):
        assert label in report
    for field in ("fixture_id", "artifact_kind", "artifact_id", "run_id", "experiment_id", "source_commit", "method_family", "instrument_id", "estimand", "kpi", "geo_scope", "time_window", "authorization_status", "mip_consumption_status", "blocked_reasons", "warnings", "expected_validation_status"):
        assert field in report
    for check in ("required envelope fields", "artifact kind", "blocked reasons", "release gate status", "CalibrationSignal", "ExperimentEvidence", "deterministic"):
        assert check in report


def test_plan_references_prior_artifact_and_roadmap() -> None:
    report = REPORT.read_text()
    assert "GEOX_MIP_PRODUCTION_ALIGNMENT_READINESS_AUDIT_001" in report
    assert "GEOX_MIP_GOVERNED_EXPERIMENT_ARTIFACT_ENVELOPE_AND_COMPATIBILITY_001" in report
    assert "GEOX_ARTIFACT_ENVELOPE_RUNTIME_CONTRACT_001" in report
