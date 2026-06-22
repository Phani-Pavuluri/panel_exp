"""Tests for FULL-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.governance.investigation_lifecycle_contract import load_registry
from panel_exp.validation.full_trustreport_eligibility_reassessment_001 import (
    DEFERRED_INVESTIGATIONS,
    REQUIRED_INPUT_ARTIFACTS,
    build_full_trustreport_eligibility_reassessment_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json"
REPORT = _REPO / "docs/track_d/FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md"

REQUIRED_SUMMARY_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "input_artifacts",
        "dcm_rows",
        "row_decisions",
        "eligibility_matrix",
        "authorization_matrix",
        "calibration_signal_matrix",
        "open_investigation_consumption",
        "resolved_investigations",
        "deferred_investigations",
        "blocking_investigations",
        "trustreport_authorization_summary",
        "downstream_authorization_summary",
        "promotion_candidates",
        "blocked_candidates",
        "diagnostic_only_rows",
        "null_monitor_only_rows",
        "ineligible_rows",
        "deferred_remediation_rows",
        "insufficient_evidence_rows",
        "governance_verdict",
        "investigation_handoff",
        "limitations",
        "next_artifact",
        "verdict",
    }
)

ALLOWED_ELIGIBILITY = frozenset(
    {
        "TRUSTREPORT_ELIGIBLE",
        "ELIGIBLE_WITH_RESTRICTIONS",
        "DIAGNOSTIC_ONLY",
        "NULL_MONITOR_ONLY",
        "INELIGIBLE",
        "DEFERRED_REMEDIATION",
        "INSUFFICIENT_EVIDENCE",
        "SUPERSEDED",
    }
)


@pytest.fixture(scope="module")
def payload() -> dict:
    return build_full_trustreport_eligibility_reassessment_001()


def test_required_input_artifacts_exist():
    archive = _REPO / "docs/track_d/archives"
    for fname in REQUIRED_INPUT_ARTIFACTS.values():
        assert (archive / fname).is_file(), fname


def test_summary_schema(payload: dict):
    assert payload["artifact_id"] == "FULL-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001"
    assert REQUIRED_SUMMARY_KEYS <= set(payload.keys())


def test_global_trustreport_not_authorized(payload: dict):
    auth = payload["trustreport_authorization_summary"]
    assert auth["trust_report_authorized"] is False
    assert auth.get("trust_report_ready") is False


def test_all_rows_have_decisions(payload: dict):
    for row in payload["row_decisions"]:
        assert row["trustreport_eligibility"] in ALLOWED_ELIGIBILITY
        assert row["row_id"]


def test_dcm001_eligible_with_restrictions(payload: dict):
    row = next(r for r in payload["row_decisions"] if r["row_id"] == "DCM-001")
    assert row["trustreport_eligibility"] == "ELIGIBLE_WITH_RESTRICTIONS"
    assert row["trust_report_authorized"] is False


def test_dcm004_eligible_with_restrictions(payload: dict):
    row = next(r for r in payload["row_decisions"] if r["row_id"] == "DCM-004")
    assert row["trustreport_eligibility"] == "ELIGIBLE_WITH_RESTRICTIONS"


def test_dcm005_paths(payload: dict):
    by_id = {r["row_id"]: r for r in payload["row_decisions"]}
    assert by_id["DCM-005-BRB"]["trustreport_eligibility"] == "DEFERRED_REMEDIATION"
    assert by_id["DCM-005-KFOLD"]["trustreport_eligibility"] == "DIAGNOSTIC_ONLY"
    assert by_id["DCM-005-PLACEBO"]["trustreport_eligibility"] == "NULL_MONITOR_ONLY"


def test_dcm006_per_cell_restricted(payload: dict):
    row = next(r for r in payload["row_decisions"] if r["row_id"] == "DCM-006")
    assert row["trustreport_eligibility"] == "ELIGIBLE_WITH_RESTRICTIONS"
    assert "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001" in row["deferred_investigations"]


def test_dcm008_diagnostic_only(payload: dict):
    row = next(r for r in payload["row_decisions"] if r["row_id"] == "DCM-008")
    assert row["trustreport_eligibility"] == "DIAGNOSTIC_ONLY"
    assert any("characterization_only" in s for s in row["restrictions"])


def test_scm_placebo_null_monitor(payload: dict):
    row = next(r for r in payload["row_decisions"] if r["row_id"] == "SCM-PLACEBO")
    assert row["trustreport_eligibility"] == "NULL_MONITOR_ONLY"


def test_augsynth_diagnostic_only(payload: dict):
    row = next(r for r in payload["row_decisions"] if r["row_id"] == "DCM-002")
    assert row["trustreport_eligibility"] == "DIAGNOSTIC_ONLY"


def test_deferred_investigations(payload: dict):
    assert set(payload["deferred_investigations"]) == set(DEFERRED_INVESTIGATIONS)


def test_resolved_includes_scm_placebo_and_augsynth(payload: dict):
    resolved = set(payload["resolved_investigations"])
    assert "INV-SCM-PLACEBO-GOVERNED-SEMANTICS-001" in resolved
    assert "INV-AUGSYNTH-JK-TRUSTREPORT-DISPOSITION-001" in resolved


def test_promotion_candidates_empty(payload: dict):
    assert payload["promotion_candidates"] == []


def test_calibration_signal_blocked(payload: dict):
    matrix = payload["calibration_signal_matrix"]
    assert not any(matrix.values())


def test_investigation_handoff(payload: dict):
    handoff = payload["investigation_handoff"]
    assert handoff.get("next_artifact") in (
        "TRUSTREPORT_DOWNSTREAM_PROMOTION_001",
        "TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001",
    )


def test_deterministic_build():
    a = build_full_trustreport_eligibility_reassessment_001()
    b = build_full_trustreport_eligibility_reassessment_001()
    assert a["governance_verdict"] == b["governance_verdict"]
    assert len(a["row_decisions"]) == len(b["row_decisions"])


def test_write_summary_atomic(tmp_path: Path):
    out = tmp_path / "summary.json"
    rep = tmp_path / "report.md"
    write_summary(out, overwrite=True, report_path=rep)
    assert out.exists()
    assert rep.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["trustreport_authorization_summary"]["trust_report_authorized"] is False


def test_registry_lane_after_write():
    if not SUMMARY.exists():
        pytest.skip("summary not committed")
    reg = load_registry()
    lane = next(
        (l for l in reg["roadmap_lane_bindings"] if l["lane_id"] == "FULL-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001"),
        None,
    )
    assert lane is not None
    assert lane["status"] == "complete"


def test_report_required_wording():
    if not REPORT.exists():
        pytest.skip("report not committed")
    text = REPORT.read_text(encoding="utf-8").lower()
    assert "does not authorize trustreport unless every required" in text
    assert "does not remediate deferred statistical defects" in text


def test_report_handoff_section():
    if not REPORT.exists():
        pytest.skip("report not committed")
    assert "## Residual Issues and Handoff" in REPORT.read_text(encoding="utf-8")


def test_no_trustreport_true_in_summary(payload: dict):
    blob = json.dumps(payload)
    assert not re.search(r'"trust_report_authorized"\s*:\s*true', blob, re.I)
