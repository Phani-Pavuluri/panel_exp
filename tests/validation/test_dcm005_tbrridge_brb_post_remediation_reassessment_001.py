"""Tests for DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.validation.dcm005_tbrridge_brb_post_remediation_reassessment_001 import (
    GATES,
    REQUIRED_INPUTS,
    build_dcm005_tbrridge_brb_post_remediation_reassessment_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001_summary.json"
REPORT = _REPO / "docs/track_d/DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001_REPORT.md"

REQUIRED_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "input_artifacts",
        "prior_brb_status",
        "remediation_candidate",
        "candidate_evidence",
        "gate_results",
        "row_decision",
        "allowed_roles",
        "blocked_roles",
        "calibration_signal_implications",
        "trustreport_implications",
        "downstream_authorization_implications",
        "investigation_update",
        "authorization_summary",
        "governance_verdict",
        "limitations",
        "next_artifact",
        "path_decision",
    }
)

ALLOWED_PATH_DECISIONS = frozenset(
    {
        "BRB_REMEDIATED_RESTRICTED",
        "BRB_DIAGNOSTIC_ONLY",
        "BRB_INELIGIBLE_FOR_CAUSAL_INTERVAL",
        "BRB_ADDITIONAL_REMEDIATION_REQUIRED",
        "BRB_SUPERSEDED",
    }
)


@pytest.fixture(scope="module")
def payload() -> dict:
    return build_dcm005_tbrridge_brb_post_remediation_reassessment_001()


def test_required_inputs_exist():
    for fname in REQUIRED_INPUTS.values():
        assert (_REPO / "docs/track_d/archives" / fname).is_file()


def test_summary_schema(payload: dict):
    assert payload["artifact_id"] == "DCM005-TBRRIDGE-BRB-POST-REMEDIATION-REASSESSMENT-001"
    assert REQUIRED_KEYS <= set(payload.keys())


def test_authorization_invariant(payload: dict):
    auth = payload["authorization_summary"]
    assert auth["trust_report_authorized"] is False
    assert auth["trust_report_ready"] is False
    assert auth["calibration_signal_allowed"] is False


def test_null_gates_fail(payload: dict):
    gates = payload["gate_results"].get("gates") or {}
    assert gates.get("null_type_i") is False
    assert gates.get("null_coverage_zero") is False


def test_diagnostic_only_decision(payload: dict):
    assert payload["path_decision"] == "BRB_DIAGNOSTIC_ONLY"
    assert payload["path_decision"] in ALLOWED_PATH_DECISIONS
    assert "sensitivity_diagnostic" in payload["allowed_roles"]


def test_causal_roles_blocked(payload: dict):
    blocked = set(payload["blocked_roles"])
    assert "causal_interval" in blocked
    assert "trust_report" in blocked
    assert "calibration_signal" in blocked


def test_candidate_policy(payload: dict):
    assert payload["remediation_candidate"]["policy"] == "larger_block_length_brb"


def test_investigation_terminal(payload: dict):
    inv = payload["investigation_update"]
    assert inv["terminal_disposition"] == "DIAGNOSTIC_ONLY"
    assert inv["new_status"] == "RESOLVED"


def test_required_wording_in_limitations(payload: dict):
    text = " ".join(payload.get("limitations") or []).lower()
    assert "null type-i" in text or "null type-i remained" in text
    assert "larger-block-length" in text or "larger block" in text


def test_deterministic():
    a = build_dcm005_tbrridge_brb_post_remediation_reassessment_001()
    b = build_dcm005_tbrridge_brb_post_remediation_reassessment_001()
    assert a["path_decision"] == b["path_decision"]


def test_write_summary_atomic(tmp_path: Path):
    out = tmp_path / "summary.json"
    rep = tmp_path / "report.md"
    write_summary(out, overwrite=True, report_path=rep, strict=True)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["authorization_summary"]["trust_report_authorized"] is False


def test_report_required_wording():
    if not REPORT.exists():
        pytest.skip("report not committed")
    text = REPORT.read_text(encoding="utf-8").lower()
    assert "does not authorize trustreport" in text
    assert "failed null calibration" in text


def test_no_trustreport_true(payload: dict):
    blob = json.dumps(payload)
    assert not re.search(r'"trust_report_authorized"\s*:\s*true', blob, re.I)
    assert not re.search(r'"calibration_signal_allowed"\s*:\s*true', blob, re.I)
