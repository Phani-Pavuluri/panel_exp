"""Tests for TRUSTREPORT-INTEGRATION-DRY-RUN-001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.validation.trustreport_integration_dry_run_001 import (
    DRY_RUN_SCOPE,
    PROMOTED_ROWS,
    REQUIRED_INPUTS,
    ROW_CONTRACT_FIELDS,
    build_trustreport_integration_dry_run_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/TRUSTREPORT_INTEGRATION_DRY_RUN_001_summary.json"
REPORT = _REPO / "docs/track_d/TRUSTREPORT_INTEGRATION_DRY_RUN_001_REPORT.md"

REQUIRED_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "input_artifacts",
        "dry_run_scope",
        "dry_run_requests",
        "accepted_requests",
        "blocked_requests",
        "accepted_rows",
        "blocked_rows",
        "row_contracts",
        "restriction_contracts",
        "warning_contracts",
        "audit_records",
        "negative_control_results",
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

EXCLUDED_FROM_RESTRICTED_ACCEPT = frozenset(
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
    return build_trustreport_integration_dry_run_001()


def test_required_inputs_exist():
    for fname in REQUIRED_INPUTS.values():
        assert (_REPO / "docs/track_d/archives" / fname).is_file()


def test_summary_schema(payload: dict):
    assert payload["artifact_id"] == "TRUSTREPORT-INTEGRATION-DRY-RUN-001"
    assert REQUIRED_KEYS <= set(payload.keys())


def test_dry_run_scope(payload: dict):
    assert set(payload["dry_run_scope"]) == DRY_RUN_SCOPE


def test_global_authorization_invariant(payload: dict):
    g = payload["global_authorization_summary"]
    assert g["trust_report_platform_authorized"] is False
    assert g["live_api_authorized"] is False
    assert g["scheduler_authorized"] is False


def test_calibration_and_production_blocked(payload: dict):
    assert payload["calibration_signal_summary"]["any_calibration_signal_allowed"] is False
    assert payload["production_decisioning_summary"]["any_production_decisioning_allowed"] is False
    assert payload["budget_optimization_summary"]["any_budget_optimization_allowed"] is False


def test_accepted_rows_only_dcm001_dcm004(payload: dict):
    assert set(payload["accepted_rows"]) == PROMOTED_ROWS


def test_row_contracts_complete(payload: dict):
    for row_id, contract in payload["row_contracts"].items():
        assert ROW_CONTRACT_FIELDS <= set(contract.keys()), row_id
        assert contract["required_warnings"]
        assert contract["audit_artifacts"]


def test_positive_dry_runs_accepted(payload: dict):
    results = {r["request_id"]: r for r in payload["dry_run_results"]}
    for req_id in (
        "pos-dcm001-valid",
        "pos-dcm001-warnings",
        "pos-dcm001-geometry",
        "pos-dcm004-valid",
        "pos-dcm004-warnings",
        "pos-dcm004-geometry",
    ):
        assert results[req_id]["decision"] == "DRY_RUN_ACCEPTED_RESTRICTED_TRUSTREPORT", req_id


def test_negative_controls_blocked(payload: dict):
    results = {r["request_id"]: r for r in payload["dry_run_results"]}
    assert results["neg-brb"]["decision"] == "DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-kfold"]["decision"] == "DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-placebo"]["decision"] == "DRY_RUN_BLOCKED_NULL_MONITOR_CAUSAL_REUSE"
    assert results["neg-dcm006-global"]["decision"] == "DRY_RUN_BLOCKED_NOT_PROMOTED"
    assert results["neg-dcm008-aggregate"]["decision"] == "DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-cal-dcm001"]["decision"] == "DRY_RUN_BLOCKED_CALIBRATION_SIGNAL"
    assert results["neg-live-dcm004"]["decision"] == "DRY_RUN_BLOCKED_LIVE_API"
    assert results["neg-scheduler-dcm001"]["decision"] == "DRY_RUN_BLOCKED_SCHEDULER"
    assert results["neg-prod-dcm004"]["decision"] == "DRY_RUN_BLOCKED_PRODUCTION_DECISIONING"
    assert results["neg-budget-dcm001"]["decision"] == "DRY_RUN_BLOCKED_BUDGET_OPTIMIZATION"
    assert results["neg-unknown"]["decision"] == "DRY_RUN_BLOCKED_UNKNOWN_ROW"


def test_excluded_rows_never_restricted_accepted(payload: dict):
    for rec in payload["dry_run_results"]:
        if rec["row_id"] in EXCLUDED_FROM_RESTRICTED_ACCEPT:
            assert rec["decision"] != "DRY_RUN_ACCEPTED_RESTRICTED_TRUSTREPORT"


def test_audit_records_emitted(payload: dict):
    assert len(payload["audit_records"]) == len(payload["dry_run_requests"])
    for rec in payload["audit_records"]:
        assert rec["dry_run_only"] is True
        assert rec["live_api_authorized"] is False
        assert rec["scheduler_authorized"] is False


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
    write_summary(out, overwrite=True, report_path=rep, strict=True)
    assert out.is_file()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["governance_verdict"] == "trustreport_integration_dry_run_passed"


def test_report_required_wording():
    if not REPORT.is_file():
        pytest.skip("report not committed")
    text = REPORT.read_text(encoding="utf-8")
    assert "dry-run integration check" in text.lower()
    assert "does not authorize live APIs" in text
    assert "DCM-001" in text and "DCM-004" in text
