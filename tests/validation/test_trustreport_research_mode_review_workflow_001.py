"""Tests for TRUSTREPORT-RESEARCH-MODE-REVIEW-WORKFLOW-001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.validation.trustreport_research_mode_review_workflow_001 import (
    EXPORT_REQUEST_MAP,
    REVIEW_CHECKLIST_ITEMS,
    REVIEW_CONTRACT_FIELDS,
    REVIEW_SCOPE,
    REQUIRED_INPUTS,
    VALID_REVIEWER_ROLES,
    build_trustreport_research_mode_review_workflow_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001_summary.json"
REPORT = _REPO / "docs/track_d/TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001_REPORT.md"

REQUIRED_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "input_artifacts",
        "review_scope",
        "review_requests",
        "accepted_reviews",
        "blocked_reviews",
        "accepted_rows",
        "blocked_rows",
        "review_contracts",
        "review_checklists",
        "review_decision_records",
        "audit_records",
        "negative_control_results",
        "hash_verification_results",
        "manifest_verification_results",
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

EXCLUDED_FROM_REVIEW_ACCEPT = frozenset(
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
    return build_trustreport_research_mode_review_workflow_001()


def test_required_inputs_exist():
    for fname in REQUIRED_INPUTS.values():
        assert (_REPO / "docs/track_d/archives" / fname).is_file()
    assert (_REPO / "docs/track_d/examples/TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_manifest.json").is_file()


def test_summary_schema(payload: dict):
    assert payload["artifact_id"] == "TRUSTREPORT-RESEARCH-MODE-REVIEW-WORKFLOW-001"
    assert REQUIRED_KEYS <= set(payload.keys())


def test_review_scope(payload: dict):
    assert set(payload["review_scope"]) == REVIEW_SCOPE


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
    assert set(payload["accepted_rows"]) == {"DCM-001", "DCM-004"}


def test_review_contracts_complete(payload: dict):
    for review_id, contract in payload["review_contracts"].items():
        assert REVIEW_CONTRACT_FIELDS <= set(contract.keys()), review_id
        assert contract["decision_record"]["production_approval"] is False
        assert contract["decision_record"]["research_mode_review_only"] is True


def test_positive_reviews_accepted(payload: dict):
    results = {r["request_id"]: r for r in payload["review_results"]}
    for req_id in EXPORT_REQUEST_MAP:
        assert results[req_id]["decision"].startswith("REVIEW_ACCEPTED"), req_id
        assert results[req_id]["review_status"] == "RESEARCH_REVIEW_APPROVED"


def test_negative_controls_blocked(payload: dict):
    results = {r["request_id"]: r for r in payload["review_results"]}
    assert results["neg-missing-banner"]["decision"] == "REVIEW_BLOCKED_MISSING_BANNER"
    assert results["neg-missing-warnings"]["decision"] == "REVIEW_BLOCKED_MISSING_WARNING"
    assert results["neg-missing-restrictions"]["decision"] == "REVIEW_BLOCKED_MISSING_RESTRICTION"
    assert results["neg-missing-audit"]["decision"] == "REVIEW_BLOCKED_MISSING_AUDIT_TRAIL"
    assert results["neg-hash-mismatch"]["decision"] == "REVIEW_BLOCKED_HASH_MISMATCH"
    assert results["neg-manifest-mismatch"]["decision"] == "REVIEW_BLOCKED_MANIFEST_MISMATCH"
    assert results["neg-unsanitized"]["decision"] == "REVIEW_BLOCKED_UNSANITIZED_PAYLOAD"
    assert results["neg-live-payload"]["decision"] == "REVIEW_BLOCKED_LIVE_MEASUREMENT_PAYLOAD"
    assert results["neg-prod-rec"]["decision"] == "REVIEW_BLOCKED_PRODUCTION_RECOMMENDATION"
    assert results["neg-budget-rec"]["decision"] == "REVIEW_BLOCKED_BUDGET_RECOMMENDATION"
    assert results["neg-invalid-role"]["decision"] == "REVIEW_BLOCKED_INVALID_REVIEWER_ROLE"
    assert results["neg-brb"]["decision"] == "REVIEW_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-kfold"]["decision"] == "REVIEW_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-placebo"]["decision"] == "REVIEW_BLOCKED_NULL_MONITOR_CAUSAL_REUSE"
    assert results["neg-dcm006"]["decision"] == "REVIEW_BLOCKED_NOT_PROMOTED"
    assert results["neg-dcm008"]["decision"] == "REVIEW_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-cal"]["decision"] == "REVIEW_BLOCKED_CALIBRATION_SIGNAL"
    assert results["neg-live"]["decision"] == "REVIEW_BLOCKED_LIVE_API"
    assert results["neg-scheduler"]["decision"] == "REVIEW_BLOCKED_SCHEDULER"
    assert results["neg-prod"]["decision"] == "REVIEW_BLOCKED_PRODUCTION_DECISIONING"
    assert results["neg-budget"]["decision"] == "REVIEW_BLOCKED_BUDGET_OPTIMIZATION"
    assert results["neg-unknown"]["decision"] == "REVIEW_BLOCKED_UNKNOWN_ROW"


def test_excluded_rows_never_review_accepted(payload: dict):
    for rec in payload["review_results"]:
        if rec["row_id"] in EXCLUDED_FROM_REVIEW_ACCEPT:
            assert not rec["decision"].startswith("REVIEW_ACCEPTED"), rec["row_id"]


def test_hash_and_manifest_verification(payload: dict):
    for h in payload["hash_verification_results"]:
        assert h["verified"] is True
    for m in payload["manifest_verification_results"]:
        assert m["verified"] is True


def test_sanitization_results(payload: dict):
    for s in payload["sanitization_results"]:
        assert s["sanitized"] is True


def test_checklist_complete_for_accepted(payload: dict):
    for contract in payload["review_contracts"].values():
        checklist = contract["review_checklist"]
        for item in REVIEW_CHECKLIST_ITEMS:
            if item in checklist:
                assert checklist[item] is True, item


def test_audit_records_no_production_approval(payload: dict):
    assert len(payload["audit_records"]) == len(payload["review_requests"])
    for rec in payload["audit_records"]:
        assert rec["production_approval"] is False
        assert rec["research_mode_review_only"] is True


def test_valid_reviewer_roles(payload: dict):
    assert set(payload["reviewer_role_model"]["valid_roles"]) == VALID_REVIEWER_ROLES


def test_committed_summary_no_live_auth_true():
    if not SUMMARY.is_file():
        pytest.skip("summary not committed")
    blob = SUMMARY.read_text(encoding="utf-8")
    assert not re.search(r'"live_api_authorized"\s*:\s*true', blob, re.I)
    assert not re.search(r'"scheduler_authorized"\s*:\s*true', blob, re.I)
    assert not re.search(r'"trust_report_platform_authorized"\s*:\s*true', blob, re.I)
    assert not re.search(r'"any_calibration_signal_allowed"\s*:\s*true', blob, re.I)
    assert not re.search(r'"production_approval"\s*:\s*true', blob, re.I)


def test_write_summary_roundtrip(tmp_path: Path):
    out = tmp_path / "summary.json"
    rep = tmp_path / "report.md"
    local = tmp_path / "reviews.json"
    write_summary(out, overwrite=True, report_path=rep, review_output_path=local, strict=True)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["governance_verdict"] == "trustreport_research_mode_review_workflow_passed"
    assert local.is_file()


def test_report_required_wording():
    if not REPORT.is_file():
        pytest.skip("report not committed")
    text = REPORT.read_text(encoding="utf-8")
    assert "research-mode human-review workflow" in text.lower()
    assert "does not authorize live APIs" in text
    assert "research-mode review approval only" in text.lower()
    assert "DCM-001" in text and "DCM-004" in text
