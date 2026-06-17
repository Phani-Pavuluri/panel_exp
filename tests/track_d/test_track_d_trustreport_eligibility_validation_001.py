"""Track D harness tests for TRUSTREPORT-ELIGIBILITY-VALIDATION-001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.track_d_trustreport_eligibility_validation_001 import (
    load_committed_summary,
    run_trustreport_eligibility_validation,
)

_SUMMARY = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json"
)


class TestTrustReportEligibilityHarness:
    def test_harness_runs(self) -> None:
        summary = run_trustreport_eligibility_validation(write_summary=False)
        assert summary["authorization_summary"]["trust_report_authorized_count"] == 0
        assert summary["verdict"].endswith("_no_authorization")

    def test_committed_summary_schema(self) -> None:
        if not _SUMMARY.is_file():
            run_trustreport_eligibility_validation(write_summary=True)
        summary = load_committed_summary()
        required = {
            "artifact_id",
            "combination_results",
            "provisional_thresholds",
            "authorization_summary",
            "verdict",
        }
        assert required.issubset(summary.keys())
        assert summary["authorization_summary"]["trust_report_authorized_count"] == 0

    def test_lane_a_candidates_classified(self) -> None:
        summary = load_committed_summary()
        by_key = {r["combination_key"]: r for r in summary["combination_results"]}
        assert by_key["DCM-001"]["eligibility_status"] == "ELIGIBLE_WITH_RESTRICTIONS"
        assert by_key["DCM-006"]["eligibility_status"] == "ELIGIBLE_WITH_RESTRICTIONS"

    def test_lane_b_ineligible_controls(self) -> None:
        summary = load_committed_summary()
        by_key = {r["combination_key"]: r for r in summary["combination_results"]}
        assert by_key["DCM-003"]["eligibility_status"] == "INELIGIBLE"
        assert by_key["DCM-007"]["eligibility_status"] == "INELIGIBLE"

    def test_no_promotion_candidates_required(self) -> None:
        summary = load_committed_summary()
        assert summary["promotion_candidate_summary"]["count"] == 0

    def test_summary_json_roundtrip(self) -> None:
        summary = load_committed_summary()
        roundtrip = json.loads(json.dumps(summary))
        assert roundtrip["artifact_id"] == "TRUSTREPORT-ELIGIBILITY-VALIDATION-001"
