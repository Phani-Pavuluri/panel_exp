"""Tests for DCM-004 TrustReport eligibility reassessment Track D harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_dcm004_trustreport_eligibility_reassessment_001 import (
    build_dcm004_trustreport_eligibility_reassessment_001,
    write_report,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/DCM004_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json"
REPORT = _REPO / "docs/track_d/DCM004_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md"
PRIOR = _REPO / "docs/track_d/archives/TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json"

ALLOWED_VERDICTS = frozenset(
    {
        "dcm004_eligible_with_restrictions_no_authorization",
        "dcm004_insufficient_evidence_no_authorization",
        "dcm004_ineligible_no_authorization",
        "dcm004_reassessment_inconclusive",
        "dcm004_reassessment_failed",
    }
)

REQUIRED_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "reassessment_scope",
        "prior_dcm004_status",
        "corrected_evidence_sources",
        "supported_contract",
        "world_classification",
        "null_metrics_overall",
        "null_metrics_supported",
        "null_metrics_unsupported",
        "positive_metrics",
        "negative_metrics",
        "type_i_decomposition",
        "coverage_decomposition",
        "gate_results",
        "reassessed_status",
        "promotion_candidate_summary",
        "unchanged_combination_results",
        "authorization_summary",
        "limitations",
        "verdict",
    }
)


@pytest.fixture(scope="module")
def payload() -> dict:
    return build_dcm004_trustreport_eligibility_reassessment_001(fast=False)


@pytest.fixture(scope="module")
def fast_payload() -> dict:
    return build_dcm004_trustreport_eligibility_reassessment_001(fast=True)


class TestTrackDDCM004Reassessment:
    def test_build_fast_payload_schema(self, fast_payload: dict) -> None:
        assert REQUIRED_KEYS <= set(fast_payload)
        assert fast_payload["artifact_id"] == "DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001"
        assert fast_payload["reassessment_scope"] == ["DCM-004"]

    def test_verdict_allowed(self, fast_payload: dict) -> None:
        assert fast_payload["verdict"] in ALLOWED_VERDICTS

    def test_authorization_blocked(self, fast_payload: dict) -> None:
        auth = fast_payload["authorization_summary"]
        assert auth["trust_report_authorized"] is False
        assert auth["trust_report_authorized_count"] == 0
        assert auth["trust_report_ready"] is False

    def test_promotion_blocked(self, fast_payload: dict) -> None:
        promo = fast_payload["promotion_candidate_summary"]
        assert promo["promotion_candidate_count"] == 0
        assert promo["dcm004_eligible_for_promotion"] is False

    def test_other_dcm_rows_unchanged(self, fast_payload: dict) -> None:
        unchanged = fast_payload["unchanged_combination_results"]
        keys = {r["combination_key"] for r in unchanged}
        assert "DCM-001" in keys
        assert "DCM-004" not in keys
        assert all(r.get("unchanged_due_to_no_new_evidence") for r in unchanged)

    def test_type_i_decomposition_present(self, fast_payload: dict) -> None:
        ti = fast_payload["type_i_decomposition"]
        assert ti.get("supported_worlds") is not None
        assert ti.get("unsupported_worlds") is not None

    def test_dcm004_reassessment_status(self, payload: dict) -> None:
        assert payload["reassessed_status"] == "ELIGIBLE_WITH_RESTRICTIONS"
        assert payload["dcm004_reassessment"]["trust_report_authorized"] is False

    def test_write_summary_and_report(self, tmp_path: Path) -> None:
        out = tmp_path / "summary.json"
        write_summary(out, fast=True)
        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["verdict"] in ALLOWED_VERDICTS
        rep = tmp_path / "report.md"
        write_report(rep, fast=True)
        assert "DCM-004" in rep.read_text(encoding="utf-8")

    def test_committed_artifacts_exist(self) -> None:
        assert SUMMARY.is_file()
        assert REPORT.is_file()

    def test_prior_dcm004_was_insufficient(self) -> None:
        prior = json.loads(PRIOR.read_text(encoding="utf-8"))
        dcm004 = next(
            r for r in prior["combination_results"] if r["combination_key"] == "DCM-004"
        )
        assert dcm004["eligibility_status"] == "INSUFFICIENT_EVIDENCE"
