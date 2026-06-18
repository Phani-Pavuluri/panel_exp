"""Track D tests for TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001 harness."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.track_d_trustreport_eligibility_reassessment_001 import (
    build_trustreport_eligibility_reassessment_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]


class TestTrackDTrustReportEligibilityReassessment001:
    def test_summary_write_produces_valid_payload(self, tmp_path: Path) -> None:
        out = write_summary(tmp_path / "summary.json")
        data = json.loads(out.read_text())
        assert data["artifact_id"] == "TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001"
        assert data["reassessment_scope"] == ["DCM-001"]

    def test_build_deterministic_excluding_timestamps(self) -> None:
        a = build_trustreport_eligibility_reassessment_001()
        b = build_trustreport_eligibility_reassessment_001()
        for payload in (a, b):
            payload.pop("generated_at", None)
            payload.pop("git_commit", None)
        assert a == b

    def test_dcm001_metrics_use_level_scale(self) -> None:
        payload = build_trustreport_eligibility_reassessment_001()
        m = payload["dcm_001_metrics"]
        assert m["positive_coverage_level"] > 0.5
        assert m["positive_coverage_fractional_percent_excluded"] == 0.0

    def test_reassessment_scope_is_dcm001_only(self) -> None:
        payload = build_trustreport_eligibility_reassessment_001()
        assert payload["reassessment_scope"] == ["DCM-001"]
