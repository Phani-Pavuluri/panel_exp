"""Tests for TRUSTREPORT-RESEARCH-MODE-ARTIFACT-EXPORT-001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.validation.trustreport_research_mode_artifact_export_001 import (
    EXPORT_BANNER,
    EXPORT_CONTRACT_FIELDS,
    EXPORT_SCOPE,
    PROMOTED_ROWS,
    REQUIRED_INPUTS,
    ROW_EXPORT_WARNINGS,
    build_trustreport_research_mode_artifact_export_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_summary.json"
REPORT = _REPO / "docs/track_d/TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_REPORT.md"
MANIFEST = _REPO / "docs/track_d/examples/TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_manifest.json"

REQUIRED_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "input_artifacts",
        "export_scope",
        "export_requests",
        "accepted_exports",
        "blocked_exports",
        "accepted_rows",
        "blocked_rows",
        "export_contracts",
        "export_manifest_metadata",
        "content_hashes",
        "warning_contracts",
        "restriction_contracts",
        "audit_records",
        "negative_control_results",
        "sanitization_results",
        "global_authorization_summary",
        "live_api_authorization_summary",
        "scheduler_authorization_summary",
        "calibration_signal_summary",
        "production_decisioning_summary",
        "budget_optimization_summary",
        "open_investigation_check",
        "governance_verdict",
        "limitations",
        "next_artifact",
    }
)

EXCLUDED_FROM_EXPORT_ACCEPT = frozenset(
    {
        "DCM-005-BRB",
        "DCM-005-KFOLD",
        "DCM-005-PLACEBO",
        "DCM-006",
        "DCM-008",
    }
)


@pytest.fixture(scope="module")
def payload() -> dict:
    return build_trustreport_research_mode_artifact_export_001()


def test_required_inputs_exist():
    for fname in REQUIRED_INPUTS.values():
        assert (_REPO / "docs/track_d/archives" / fname).is_file()


def test_summary_schema(payload: dict):
    assert payload["artifact_id"] == "TRUSTREPORT-RESEARCH-MODE-ARTIFACT-EXPORT-001"
    assert REQUIRED_KEYS <= set(payload.keys())


def test_export_scope(payload: dict):
    assert set(payload["export_scope"]) == EXPORT_SCOPE


def test_global_authorization_invariant(payload: dict):
    g = payload["global_authorization_summary"]
    assert g["trust_report_platform_authorized"] is False
    assert g["live_api_authorized"] is False
    assert g["scheduler_authorized"] is False


def test_boundaries_blocked(payload: dict):
    assert payload["calibration_signal_summary"]["any_calibration_signal_allowed"] is False
    assert payload["production_decisioning_summary"]["any_production_decisioning_allowed"] is False
    assert payload["budget_optimization_summary"]["any_budget_optimization_allowed"] is False


def test_accepted_rows_only_promoted(payload: dict):
    assert set(payload["accepted_rows"]) == PROMOTED_ROWS


def test_export_contracts_complete(payload: dict):
    for export_id, contract in payload["export_contracts"].items():
        assert EXPORT_CONTRACT_FIELDS <= set(contract.keys()), export_id
        assert contract["research_mode_only"] is True
        assert contract["content_hash"]
        assert contract["export_manifest"]


def test_row_warnings_present(payload: dict):
    for row_id, warnings in payload["warning_contracts"].items():
        assert warnings == ROW_EXPORT_WARNINGS[row_id]


def test_positive_exports_accepted(payload: dict):
    results = {r["request_id"]: r for r in payload["export_results"]}
    for req_id in (
        "pos-dcm001-placeholder",
        "pos-dcm004-placeholder",
        "pos-dcm001-synthetic",
        "pos-dcm004-synthetic",
        "pos-dcm001-manifest",
        "pos-dcm004-manifest",
    ):
        assert results[req_id]["decision"].startswith("EXPORT_ACCEPTED"), req_id


def test_negative_controls_blocked(payload: dict):
    results = {r["request_id"]: r for r in payload["export_results"]}
    assert results["neg-brb"]["decision"] == "EXPORT_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-kfold"]["decision"] == "EXPORT_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-placebo"]["decision"] == "EXPORT_BLOCKED_NULL_MONITOR_CAUSAL_REUSE"
    assert results["neg-dcm006-global"]["decision"] == "EXPORT_BLOCKED_NOT_PROMOTED"
    assert results["neg-dcm008-aggregate"]["decision"] == "EXPORT_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-cal"]["decision"] == "EXPORT_BLOCKED_CALIBRATION_SIGNAL"
    assert results["neg-live"]["decision"] == "EXPORT_BLOCKED_LIVE_API"
    assert results["neg-scheduler"]["decision"] == "EXPORT_BLOCKED_SCHEDULER"
    assert results["neg-prod"]["decision"] == "EXPORT_BLOCKED_PRODUCTION_DECISIONING"
    assert results["neg-budget"]["decision"] == "EXPORT_BLOCKED_BUDGET_OPTIMIZATION"
    assert results["neg-unknown"]["decision"] == "EXPORT_BLOCKED_UNKNOWN_ROW"
    assert results["neg-unsanitized"]["decision"] == "EXPORT_BLOCKED_UNSANITIZED_PAYLOAD"
    assert results["neg-missing-audit"]["decision"] == "EXPORT_BLOCKED_MISSING_AUDIT_TRAIL"


def test_excluded_rows_never_export_accepted(payload: dict):
    for rec in payload["export_results"]:
        if rec["row_id"] in EXCLUDED_FROM_EXPORT_ACCEPT:
            assert not rec["decision"].startswith("EXPORT_ACCEPTED"), rec["row_id"]


def test_sanitization_results_all_pass(payload: dict):
    for s in payload["sanitization_results"]:
        assert s["sanitized"] is True
        assert s["content_hash"]


def test_content_hashes_match_exports(payload: dict):
    for req_id, h in payload["content_hashes"].items():
        contract = next(
            c for c in payload["export_contracts"].values()
            if c["export_manifest"]["export_id"] == f"export-{req_id}"
        )
        assert contract["content_hash"] == h


def test_audit_records_emitted(payload: dict):
    assert len(payload["audit_records"]) == len(payload["export_requests"])
    for rec in payload["audit_records"]:
        assert rec["research_mode_only"] is True
        assert rec["live_api_authorized"] is False
        assert rec["scheduler_authorized"] is False


def test_export_banners_defined():
    assert "RESEARCH MODE ONLY" in EXPORT_BANNER
    assert "SANITIZED ARTIFACT EXPORT" in EXPORT_BANNER
    assert "NOT FOR PRODUCTION DECISIONING" in EXPORT_BANNER


def test_committed_summary_no_live_auth_true():
    if not SUMMARY.is_file():
        pytest.skip("summary not committed")
    blob = SUMMARY.read_text(encoding="utf-8")
    assert not re.search(r'"live_api_authorized"\s*:\s*true', blob, re.I)
    assert not re.search(r'"scheduler_authorized"\s*:\s*true', blob, re.I)
    assert not re.search(r'"trust_report_platform_authorized"\s*:\s*true', blob, re.I)
    assert not re.search(r'"any_calibration_signal_allowed"\s*:\s*true', blob, re.I)


def test_write_summary_roundtrip(tmp_path: Path):
    out = tmp_path / "summary.json"
    rep = tmp_path / "report.md"
    export_dir = tmp_path / "exports"
    manifest = tmp_path / "manifest.json"
    write_summary(
        out,
        overwrite=True,
        report_path=rep,
        export_output_path=export_dir,
        manifest_path=manifest,
        strict=True,
    )
    assert out.is_file()
    assert export_dir.is_dir()
    assert len(list(export_dir.glob("*.json"))) == 6
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["governance_verdict"] == "trustreport_research_mode_artifact_export_passed"
    manifest_doc = json.loads(manifest.read_text(encoding="utf-8"))
    assert manifest_doc["research_mode_only"] is True
    assert manifest_doc["sanitized"] is True


def test_report_required_wording():
    if not REPORT.is_file():
        pytest.skip("report not committed")
    text = REPORT.read_text(encoding="utf-8")
    assert "research-mode artifacts only" in text.lower()
    assert "does not authorize live APIs" in text
    assert "DCM-001" in text and "DCM-004" in text
    assert "Sanitization rules" in text


def test_manifest_committed_if_present():
    if not MANIFEST.is_file():
        pytest.skip("manifest not committed")
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert doc["artifact_id"] == "TRUSTREPORT-RESEARCH-MODE-ARTIFACT-EXPORT-001"
    assert len(doc["exports"]) == 6
