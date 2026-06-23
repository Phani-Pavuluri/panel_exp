"""Tests for TRUSTREPORT-RESEARCH-MODE-ACCESS-CONTROL-001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.validation.trustreport_research_mode_access_control_001 import (
    ACCESS_CONTRACT_FIELDS,
    ACCESS_SCOPE,
    ALL_BLOCKED_MODES,
    PROMOTED_ROWS,
    REQUIRED_INPUTS,
    ROLE_PERMISSIONS,
    build_trustreport_research_mode_access_control_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001_summary.json"
REPORT = _REPO / "docs/track_d/TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001_REPORT.md"

REQUIRED_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "input_artifacts",
        "access_scope",
        "role_permission_matrix",
        "access_requests",
        "granted_access",
        "blocked_access",
        "accepted_rows",
        "blocked_rows",
        "access_contracts",
        "access_decision_records",
        "audit_records",
        "negative_control_results",
        "manifest_verification_results",
        "hash_verification_results",
        "sanitization_results",
        "review_status_check",
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

POSITIVE_REQUEST_IDS = frozenset(
    {
        "pos-view-dcm001",
        "pos-view-dcm004",
        "pos-export-dcm001",
        "pos-export-dcm004",
        "pos-review-dcm001",
        "pos-review-dcm004",
        "pos-approve-causal-dcm001",
        "pos-approve-causal-dcm004",
        "pos-approve-gov-dcm001",
        "pos-approve-gov-dcm004",
        "pos-manifest-dcm001",
        "pos-manifest-dcm004",
        "pos-audit-dcm001",
        "pos-audit-dcm004",
        "pos-admin-view-dcm001",
        "pos-admin-export-dcm004",
    }
)

EXCLUDED_FROM_ACCESS_GRANT = frozenset(
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
    return build_trustreport_research_mode_access_control_001()


def test_required_inputs_exist():
    for fname in REQUIRED_INPUTS.values():
        assert (_REPO / "docs/track_d/archives" / fname).is_file()
    assert (_REPO / "docs/track_d/examples/TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_manifest.json").is_file()


def test_summary_schema(payload: dict):
    assert payload["artifact_id"] == "TRUSTREPORT-RESEARCH-MODE-ACCESS-CONTROL-001"
    assert REQUIRED_KEYS <= set(payload.keys())


def test_access_scope(payload: dict):
    assert set(payload["access_scope"]) == ACCESS_SCOPE


def test_global_authorization_invariant(payload: dict):
    g = payload["global_authorization_summary"]
    assert g["trust_report_platform_authorized"] is False
    assert g["live_api_authorized"] is False
    assert g["scheduler_authorized"] is False


def test_boundaries_blocked(payload: dict):
    assert payload["calibration_signal_summary"]["any_calibration_signal_allowed"] is False
    assert payload["production_decisioning_summary"]["any_production_decisioning_allowed"] is False
    assert payload["budget_optimization_summary"]["any_budget_optimization_allowed"] is False


def test_role_matrix_no_production_permissions(payload: dict):
    for role, perms in payload["role_permission_matrix"].items():
        assert not set(perms) & ALL_BLOCKED_MODES, role


def test_accepted_rows_only_promoted(payload: dict):
    assert set(payload["accepted_rows"]) == PROMOTED_ROWS


def test_access_contracts_complete(payload: dict):
    for req_id, contract in payload["access_contracts"].items():
        assert ACCESS_CONTRACT_FIELDS <= set(contract.keys()), req_id
        assert contract["research_mode_only"] is True
        assert contract["audit_record"]["live_api_authorized"] is False


def test_positive_access_granted(payload: dict):
    results = {r["request_id"]: r for r in payload["access_results"]}
    for req_id in POSITIVE_REQUEST_IDS:
        assert results[req_id]["decision"].startswith("ACCESS_GRANTED"), req_id
        assert results[req_id]["granted"] is True


def test_negative_controls_blocked(payload: dict):
    results = {r["request_id"]: r for r in payload["access_results"]}
    assert results["neg-viewer-export"]["decision"] == "ACCESS_BLOCKED_ROLE_NOT_PERMITTED"
    assert results["neg-exporter-approve"]["decision"] == "ACCESS_BLOCKED_ROLE_NOT_PERMITTED"
    assert results["neg-reviewer-approve"]["decision"] == "ACCESS_BLOCKED_ROLE_NOT_PERMITTED"
    assert results["neg-audit-export"]["decision"] == "ACCESS_BLOCKED_ROLE_NOT_PERMITTED"
    assert results["neg-invalid-role"]["decision"] == "ACCESS_BLOCKED_INVALID_ROLE"
    assert results["neg-unknown"]["decision"] == "ACCESS_BLOCKED_UNKNOWN_ROW"
    assert results["neg-brb"]["decision"] == "ACCESS_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-kfold"]["decision"] == "ACCESS_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-placebo"]["decision"] == "ACCESS_BLOCKED_NULL_MONITOR_CAUSAL_REUSE"
    assert results["neg-dcm006"]["decision"] == "ACCESS_BLOCKED_NOT_PROMOTED"
    assert results["neg-dcm008"]["decision"] == "ACCESS_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-cal"]["decision"] == "ACCESS_BLOCKED_CALIBRATION_SIGNAL"
    assert results["neg-live-api"]["decision"] == "ACCESS_BLOCKED_LIVE_API"
    assert results["neg-scheduler"]["decision"] == "ACCESS_BLOCKED_SCHEDULER"
    assert results["neg-prod"]["decision"] == "ACCESS_BLOCKED_PRODUCTION_DECISIONING"
    assert results["neg-budget"]["decision"] == "ACCESS_BLOCKED_BUDGET_OPTIMIZATION"
    assert results["neg-global-admin"]["decision"] == "ACCESS_BLOCKED_GLOBAL_PLATFORM"
    assert results["neg-unsanitized"]["decision"] == "ACCESS_BLOCKED_UNSANITIZED_ARTIFACT"
    assert results["neg-hash"]["decision"] == "ACCESS_BLOCKED_HASH_MISMATCH"
    assert results["neg-manifest"]["decision"] == "ACCESS_BLOCKED_MANIFEST_MISMATCH"
    assert results["neg-unreviewed"]["decision"] == "ACCESS_BLOCKED_UNREVIEWED_ARTIFACT"


def test_excluded_rows_never_access_granted(payload: dict):
    for rec in payload["access_results"]:
        if rec["row_id"] in EXCLUDED_FROM_ACCESS_GRANT:
            assert not rec["decision"].startswith("ACCESS_GRANTED"), rec["row_id"]


def test_verification_gates(payload: dict):
    for h in payload["hash_verification_results"]:
        assert h["verified"] is True
    for m in payload["manifest_verification_results"]:
        assert m["verified"] is True
    for s in payload["sanitization_results"]:
        assert s["sanitized"] is True


def test_research_mode_admin_has_all_research_permissions():
    admin_perms = ROLE_PERMISSIONS["research_mode_admin"]
    assert "RESEARCH_VIEW" in admin_perms
    assert "RESEARCH_EXPORT" in admin_perms
    assert "RESEARCH_REVIEW_APPROVE" in admin_perms
    assert not admin_perms & ALL_BLOCKED_MODES


def test_audit_records_no_production_approval(payload: dict):
    assert len(payload["audit_records"]) == len(payload["access_requests"])
    for rec in payload["audit_records"]:
        assert rec["production_approval"] is False
        assert rec["research_mode_only"] is True


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
    local = tmp_path / "decisions.json"
    write_summary(out, overwrite=True, report_path=rep, access_output_path=local, strict=True)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["governance_verdict"] == "trustreport_research_mode_access_control_passed"
    assert local.is_file()


def test_report_required_wording():
    if not REPORT.is_file():
        pytest.skip("report not committed")
    text = REPORT.read_text(encoding="utf-8")
    assert "research-mode access control" in text.lower()
    assert "does not authorize live APIs" in text
    assert "research-mode access approval only" in text.lower()
    assert "DCM-001" in text and "DCM-004" in text
