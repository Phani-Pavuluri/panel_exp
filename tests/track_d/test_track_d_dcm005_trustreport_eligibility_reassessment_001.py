"""Tests for DCM-005 TrustReport eligibility reassessment Track D harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.governance.investigation_lifecycle_contract import (
    REQUIRED_HANDOFF_KEYS,
    validate_artifact_handoff,
    validate_report_handoff_section,
)
from panel_exp.validation.track_d_dcm005_trustreport_eligibility_reassessment_001 import (
    build_dcm005_trustreport_eligibility_reassessment_001,
    write_report,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/DCM005_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json"
REPORT = _REPO / "docs/track_d/DCM005_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md"

ALLOWED_VERDICTS = frozenset(
    {
        "dcm005_mixed_path_specific_restrictions_no_authorization",
        "dcm005_all_paths_ineligible_no_authorization",
        "dcm005_diagnostic_paths_only_no_authorization",
        "dcm005_insufficient_evidence_no_authorization",
        "dcm005_reassessment_inconclusive",
        "dcm005_reassessment_failed",
    }
)

REQUIRED_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "reassessment_scope",
        "prior_dcm005_status",
        "evidence_sources",
        "path_decisions",
        "aggregate_dcm005_status",
        "promotion_candidate_summary",
        "investigation_consumption",
        "investigation_handoff",
        "unchanged_combination_results",
        "authorization_summary",
        "limitations",
        "verdict",
    }
)


@pytest.fixture(scope="module")
def payload() -> dict:
    return build_dcm005_trustreport_eligibility_reassessment_001()


class TestTrackDDCM005Reassessment:
    def test_build_payload_schema(self, payload: dict) -> None:
        assert REQUIRED_KEYS <= set(payload.keys())
        assert payload["artifact_id"] == "DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001"
        assert len(payload["reassessment_scope"]) == 3

    def test_verdict_allowed(self, payload: dict) -> None:
        assert payload["verdict"] in ALLOWED_VERDICTS
        assert payload["verdict"] == "dcm005_mixed_path_specific_restrictions_no_authorization"

    def test_authorization_blocked(self, payload: dict) -> None:
        auth = payload["authorization_summary"]
        assert auth["trust_report_authorized"] is False
        assert auth["trust_report_authorized_count"] == 0
        assert auth["trust_report_ready"] is False

    def test_promotion_blocked(self, payload: dict) -> None:
        promo = payload["promotion_candidate_summary"]
        assert promo["count"] == 0
        assert promo["promotion_candidate_count"] == 0

    def test_path_decisions_three_rows(self, payload: dict) -> None:
        paths = payload["path_decisions"]
        assert len(paths) == 3
        ids = {p["path_id"] for p in paths}
        assert ids == {"DCM-005-BRB", "DCM-005-KFOLD", "DCM-005-PLACEBO"}

    def test_aggregate_mixed_status(self, payload: dict) -> None:
        assert payload["aggregate_dcm005_status"] == "MIXED_WITH_TERMINAL_PATH_DECISIONS"

    def test_other_dcm_rows_unchanged(self, payload: dict) -> None:
        unchanged = payload["unchanged_combination_results"]
        keys = {r["combination_key"] for r in unchanged}
        assert "DCM-001" in keys
        assert "DCM-005-BRB" not in keys
        assert all(r.get("unchanged_due_to_no_new_evidence") for r in unchanged)

    def test_investigation_handoff_complete(self, payload: dict) -> None:
        handoff = payload["investigation_handoff"]
        assert REQUIRED_HANDOFF_KEYS <= set(handoff.keys())
        issues = validate_artifact_handoff(payload)
        assert issues == [], "\n".join(i.message for i in issues)

    def test_investigation_consumption_all_three(self, payload: dict) -> None:
        consumption = payload["investigation_consumption"]
        assert len(consumption) == 3

    def test_write_summary_and_report(self, tmp_path: Path) -> None:
        out = tmp_path / "summary.json"
        write_summary(out)
        data = json.loads(out.read_text())
        assert data["verdict"] in ALLOWED_VERDICTS
        rep = tmp_path / "report.md"
        write_report(rep)
        text = rep.read_text()
        assert "path-specific decisions for DCM-005" in text
        assert "## Residual Issues and Handoff" in text
        issues = validate_report_handoff_section(text)
        assert issues == []

    def test_committed_artifacts_when_present(self) -> None:
        if not SUMMARY.is_file():
            pytest.skip("summary not committed yet")
        data = json.loads(SUMMARY.read_text())
        assert REQUIRED_KEYS <= set(data.keys())
