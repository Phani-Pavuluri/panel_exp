"""Tests for TRUSTREPORT-RESEARCH-MODE-RENDERER-001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.validation.trustreport_research_mode_renderer_001 import (
    PROMOTED_ROWS,
    RENDER_BANNER,
    RENDERER_CONTRACT_FIELDS,
    RENDERER_SCOPE,
    REQUIRED_INPUTS,
    ROW_RENDER_WARNINGS,
    build_trustreport_research_mode_renderer_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/TRUSTREPORT_RESEARCH_MODE_RENDERER_001_summary.json"
REPORT = _REPO / "docs/track_d/TRUSTREPORT_RESEARCH_MODE_RENDERER_001_REPORT.md"

REQUIRED_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "input_artifacts",
        "renderer_scope",
        "render_requests",
        "accepted_renders",
        "blocked_renders",
        "accepted_rows",
        "blocked_rows",
        "renderer_contracts",
        "rendered_example_metadata",
        "warning_contracts",
        "restriction_contracts",
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

EXCLUDED_FROM_RENDER_ACCEPT = frozenset(
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
    return build_trustreport_research_mode_renderer_001()


def test_required_inputs_exist():
    for fname in REQUIRED_INPUTS.values():
        assert (_REPO / "docs/track_d/archives" / fname).is_file()


def test_summary_schema(payload: dict):
    assert payload["artifact_id"] == "TRUSTREPORT-RESEARCH-MODE-RENDERER-001"
    assert REQUIRED_KEYS <= set(payload.keys())


def test_renderer_scope(payload: dict):
    assert set(payload["renderer_scope"]) == RENDERER_SCOPE


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


def test_renderer_contracts_complete(payload: dict):
    for row_id, contract in payload["renderer_contracts"].items():
        assert RENDERER_CONTRACT_FIELDS <= set(contract.keys()), row_id
        assert contract["research_mode_only"] is True
        assert contract["dry_run_approval_artifact"]
        assert contract["promotion_artifact"]


def test_row_warnings_present(payload: dict):
    for row_id, warnings in payload["warning_contracts"].items():
        assert warnings == ROW_RENDER_WARNINGS[row_id]


def test_positive_renders_accepted(payload: dict):
    results = {r["request_id"]: r for r in payload["render_results"]}
    for req_id in (
        "pos-dcm001-valid",
        "pos-dcm004-valid",
        "pos-dcm001-placeholder",
        "pos-dcm004-placeholder",
        "pos-dcm001-synthetic",
        "pos-dcm004-synthetic",
    ):
        assert results[req_id]["decision"].startswith("RENDER_ACCEPTED"), req_id


def test_negative_controls_blocked(payload: dict):
    results = {r["request_id"]: r for r in payload["render_results"]}
    assert results["neg-brb"]["decision"] == "RENDER_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-kfold"]["decision"] == "RENDER_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-placebo"]["decision"] == "RENDER_BLOCKED_NULL_MONITOR_CAUSAL_REUSE"
    assert results["neg-dcm006-global"]["decision"] == "RENDER_BLOCKED_NOT_PROMOTED"
    assert results["neg-dcm008-aggregate"]["decision"] == "RENDER_BLOCKED_DIAGNOSTIC_ONLY"
    assert results["neg-cal"]["decision"] == "RENDER_BLOCKED_CALIBRATION_SIGNAL"
    assert results["neg-live"]["decision"] == "RENDER_BLOCKED_LIVE_API"
    assert results["neg-scheduler"]["decision"] == "RENDER_BLOCKED_SCHEDULER"
    assert results["neg-prod"]["decision"] == "RENDER_BLOCKED_PRODUCTION_DECISIONING"
    assert results["neg-budget"]["decision"] == "RENDER_BLOCKED_BUDGET_OPTIMIZATION"
    assert results["neg-unknown"]["decision"] == "RENDER_BLOCKED_UNKNOWN_ROW"


def test_excluded_rows_never_render_accepted(payload: dict):
    for rec in payload["render_results"]:
        if rec["row_id"] in EXCLUDED_FROM_RENDER_ACCEPT:
            assert not rec["decision"].startswith("RENDER_ACCEPTED"), rec["row_id"]


def test_rendered_metadata_has_placeholder_and_synthetic(payload: dict):
    meta = payload["rendered_example_metadata"]
    assert meta["pos-dcm001-placeholder"]["placeholder"] is True
    assert meta["pos-dcm001-synthetic"]["synthetic"] is True
    assert meta["pos-dcm001-synthetic"]["measurement_label"] == "SYNTHETIC_DRY_RUN_PAYLOAD"


def test_audit_records_emitted(payload: dict):
    assert len(payload["audit_records"]) == len(payload["render_requests"])
    for rec in payload["audit_records"]:
        assert rec["research_mode_only"] is True
        assert rec["live_api_authorized"] is False
        assert rec["scheduler_authorized"] is False


def test_render_banners_defined():
    assert "RESEARCH MODE ONLY" in RENDER_BANNER
    assert "NOT FOR PRODUCTION DECISIONING" in RENDER_BANNER


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
    local = tmp_path / "rendered.json"
    write_summary(out, overwrite=True, report_path=rep, render_output_path=local, strict=True)
    assert out.is_file()
    assert local.is_file()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["governance_verdict"] == "trustreport_research_mode_renderer_passed"
    rendered = json.loads(local.read_text(encoding="utf-8"))
    assert "pos-dcm001-valid" in rendered
    assert rendered["pos-dcm001-valid"]["banners"] == RENDER_BANNER


def test_report_required_wording():
    if not REPORT.is_file():
        pytest.skip("report not committed")
    text = REPORT.read_text(encoding="utf-8")
    assert "research mode only" in text.lower()
    assert "does not authorize live APIs" in text
    assert "DCM-001" in text and "DCM-004" in text
