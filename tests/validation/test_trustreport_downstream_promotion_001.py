"""Tests for TRUSTREPORT-DOWNSTREAM-PROMOTION-001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.validation.trustreport_downstream_promotion_001 import (
    BRB_EXCLUSION_TEXT,
    CANDIDATE_UNIVERSE,
    DCM006_EXCLUSION_TEXT,
    DCM008_EXCLUSION_TEXT,
    REQUIRED_INPUTS,
    build_trustreport_downstream_promotion_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/TRUSTREPORT_DOWNSTREAM_PROMOTION_001_summary.json"
REPORT = _REPO / "docs/track_d/TRUSTREPORT_DOWNSTREAM_PROMOTION_001_REPORT.md"

REQUIRED_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "input_artifacts",
        "candidate_universe",
        "reviewed_rows",
        "promotion_decisions",
        "promoted_rows",
        "excluded_rows",
        "blocked_rows",
        "diagnostic_only_rows",
        "null_monitor_only_rows",
        "deferred_rows",
        "promotion_gates",
        "row_level_authorization_matrix",
        "calibration_signal_matrix",
        "downstream_role_matrix",
        "required_warnings",
        "required_restrictions",
        "global_authorization_summary",
        "live_api_authorization_summary",
        "scheduler_authorization_summary",
        "investigation_status",
        "governance_verdict",
        "limitations",
        "next_artifact",
        "row_level_restricted_promotion_allowed",
    }
)

FORBIDDEN_PROMOTED = frozenset(
    {
        "DCM-005-BRB",
        "DCM-005-KFOLD",
        "DCM-005-PLACEBO",
        "DCM-006",
        "DCM-008",
        "DCM-002",
    }
)


@pytest.fixture(scope="module")
def payload() -> dict:
    return build_trustreport_downstream_promotion_001()


def test_required_inputs_exist():
    for fname in REQUIRED_INPUTS.values():
        assert (_REPO / "docs/track_d/archives" / fname).is_file()


def test_summary_schema(payload: dict):
    assert payload["artifact_id"] == "TRUSTREPORT-DOWNSTREAM-PROMOTION-001"
    assert REQUIRED_KEYS <= set(payload.keys())


def test_candidate_universe(payload: dict):
    assert set(payload["candidate_universe"]) == CANDIDATE_UNIVERSE


def test_global_authorization_invariant(payload: dict):
    global_auth = payload["global_authorization_summary"]
    assert global_auth["trust_report_platform_authorized"] is False
    assert global_auth["live_api_authorized"] is False
    assert global_auth["scheduler_authorized"] is False


def test_live_and_scheduler_blocked(payload: dict):
    assert payload["live_api_authorization_summary"]["live_api_authorized"] is False
    assert payload["scheduler_authorization_summary"]["scheduler_authorized"] is False


def test_brb_not_promoted(payload: dict):
    decisions = payload["promotion_decisions"]
    assert decisions["DCM-005-BRB"] != "PROMOTE_RESTRICTED_TRUSTREPORT"
    assert "DCM-005-BRB" in payload["excluded_rows"]
    assert "DCM-005-BRB" not in payload["promoted_rows"]


def test_diagnostic_and_null_monitor_paths_not_restricted_promoted(payload: dict):
    decisions = payload["promotion_decisions"]
    for row_id in FORBIDDEN_PROMOTED:
        assert decisions[row_id] != "PROMOTE_RESTRICTED_TRUSTREPORT", row_id


def test_calibration_signal_false_everywhere(payload: dict):
    cal = payload["calibration_signal_matrix"]
    assert all(v is False for v in cal.values())


def test_dcm001_dcm004_reviewed(payload: dict):
    reviewed_ids = {r["row_id"] for r in payload["reviewed_rows"]}
    assert reviewed_ids == CANDIDATE_UNIVERSE


def test_promoted_rows_have_restriction_contract(payload: dict):
    for row in payload["reviewed_rows"]:
        if row["decision"] == "PROMOTE_RESTRICTED_TRUSTREPORT":
            contract = row["restriction_contract"]
            assert contract.get("required_warnings")
            assert contract.get("blocked_downstream_uses")
            assert contract.get("calibration_signal_allowed") is False
            assert contract.get("trustreport_role") == "restricted_trustreport_research_only"


def test_required_exclusion_wording_in_limitations(payload: dict):
    limitations = "\n".join(payload.get("limitations") or [])
    assert "TBRRidge + BRB is excluded" in limitations
    assert "PARALLEL_MARGINAL_CELLS" in limitations or "marginal per-cell" in limitations
    assert "diagnostic-only" in limitations.lower() or "characterization only" in limitations


def test_committed_summary_no_live_auth_true():
    if not SUMMARY.is_file():
        pytest.skip("summary not committed")
    blob = SUMMARY.read_text(encoding="utf-8")
    assert not re.search(r'"live_api_authorized"\s*:\s*true', blob, re.I)
    assert not re.search(r'"scheduler_authorized"\s*:\s*true', blob, re.I)
    assert not re.search(r'"trust_report_platform_authorized"\s*:\s*true', blob, re.I)


def test_committed_summary_no_brb_promotion():
    if not SUMMARY.is_file():
        pytest.skip("summary not committed")
    blob = SUMMARY.read_text(encoding="utf-8")
    assert "DCM-005-BRB" not in re.findall(
        r'"promoted_rows"\s*:\s*\[[^\]]*"DCM-005-BRB"',
        blob,
    )
    assert not re.search(
        r'"DCM-005-BRB"\s*:\s*"PROMOTE_RESTRICTED_TRUSTREPORT"',
        blob,
    )


def test_write_summary_roundtrip(tmp_path: Path):
    out = tmp_path / "summary.json"
    rep = tmp_path / "report.md"
    result = write_summary(out, overwrite=True, report_path=rep, strict=True)
    assert out.is_file()
    assert rep.is_file()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["artifact_id"] == result["artifact_id"]


def test_report_contains_required_wording():
    if not REPORT.is_file():
        pytest.skip("report not committed")
    text = REPORT.read_text(encoding="utf-8")
    assert "does not authorize live APIs" in text.lower() or "live API" in text
    assert BRB_EXCLUSION_TEXT.split(".")[0] in text or "BRB is excluded" in text
    assert DCM006_EXCLUSION_TEXT.split(".")[0][:40] in text or "DCM-006" in text
    assert DCM008_EXCLUSION_TEXT.split(".")[0][:40] in text or "DCM-008" in text
