"""Tests for TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001 core logic."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.trustreport_eligibility_reassessment_001 import (
    RC_AUTH_BLOCKED,
    RC_CORRECTED_EVIDENCE,
    RC_HISTORICAL_SUPERSEDED,
    RC_LEVEL_SCALE,
    RC_NOISY_WORLD_CAVEAT,
    RC_TYPE_I_CAVEAT,
    extract_corrected_dcm001_evidence,
    reassess_trustreport_eligibility,
)
from panel_exp.validation.trustreport_eligibility_001 import (
    STATUS_ELIGIBLE_CANDIDATE,
    STATUS_ELIGIBLE_WITH_RESTRICTIONS,
)

_REPO = Path(__file__).resolve().parents[2]
_CORRECTED = _REPO / "docs/track_d/archives/D5_STAT_SCM_JK_001_results.json"
_HISTORICAL = (
    _REPO / "docs/track_d/archives/D5_STAT_SCM_JK_001_results_historical_pre_harness_correction.json"
)
_PRIOR = _REPO / "docs/track_d/archives/TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json"

ALLOWED_VERDICTS = frozenset(
    {
        "trustreport_dcm001_eligible_with_restrictions_no_authorization",
        "trustreport_dcm001_promotion_candidate_no_authorization",
        "trustreport_dcm001_insufficient_evidence_no_authorization",
        "trustreport_dcm001_ineligible_no_authorization",
        "trustreport_reassessment_inconclusive",
        "trustreport_reassessment_failed",
    }
)

REQUIRED_SUMMARY_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "prior_eligibility_artifact",
        "corrected_evidence_artifact",
        "reassessment_scope",
        "provisional_gates",
        "dcm_001_prior_status",
        "dcm_001_reassessed_status",
        "dcm_001_metrics",
        "support_gate_results",
        "semantic_gate_results",
        "unchanged_combination_results",
        "promotion_candidate_summary",
        "authorization_summary",
        "limitations",
        "verdict",
    }
)


@pytest.fixture(scope="module")
def corrected_archive() -> dict:
    assert _CORRECTED.is_file()
    return json.loads(_CORRECTED.read_text())


@pytest.fixture(scope="module")
def historical_archive() -> dict:
    assert _HISTORICAL.is_file()
    return json.loads(_HISTORICAL.read_text())


@pytest.fixture(scope="module")
def prior_dcm001() -> dict:
    summary = json.loads(_PRIOR.read_text())
    for row in summary["combination_results"]:
        if row["combination_key"] == "DCM-001":
            return row
    raise AssertionError("DCM-001 missing")


class TestTrustReportEligibilityReassessmentCore:
    def test_corrected_archive_used(self, corrected_archive: dict) -> None:
        metrics = extract_corrected_dcm001_evidence(corrected_archive)
        assert metrics["evidence_source"] == "corrected_canonical_archive"
        assert metrics["effect_scale"] == "level_effect"

    def test_historical_excluded_from_canonical_metrics(
        self, corrected_archive: dict, historical_archive: dict
    ) -> None:
        metrics = extract_corrected_dcm001_evidence(
            corrected_archive, historical_archive=historical_archive
        )
        hist_pos = (
            historical_archive.get("aggregate_metrics", {})
            .get("clean_positive_lift", {})
            .get("coverage")
        )
        assert metrics["positive_coverage_level"] != hist_pos or hist_pos is None
        assert metrics["positive_coverage_level"] is not None
        assert metrics["positive_coverage_level"] > 0.5

    def test_level_scale_not_fractional_for_reassessment(
        self, corrected_archive: dict, prior_dcm001: dict
    ) -> None:
        metrics = extract_corrected_dcm001_evidence(corrected_archive)
        result = reassess_trustreport_eligibility(
            prior_eligibility_result=prior_dcm001,
            corrected_empirical_evidence=metrics,
        )
        assert result.positive_coverage == metrics["positive_coverage_level"]
        assert metrics["positive_coverage_fractional_percent"] == 0.0
        assert result.positive_coverage != metrics["positive_coverage_fractional_percent"]

    def test_prior_status_loaded(self, corrected_archive: dict, prior_dcm001: dict) -> None:
        metrics = extract_corrected_dcm001_evidence(corrected_archive)
        result = reassess_trustreport_eligibility(
            prior_eligibility_result=prior_dcm001,
            corrected_empirical_evidence=metrics,
        )
        assert result.prior_status == "ELIGIBLE_WITH_RESTRICTIONS"

    def test_null_and_positive_separate(self, corrected_archive: dict) -> None:
        metrics = extract_corrected_dcm001_evidence(corrected_archive)
        assert metrics["null_coverage_level"] is not None
        assert metrics["positive_coverage_level"] is not None
        assert metrics["null_coverage_level"] != metrics["positive_coverage_fractional_percent"]

    def test_type_i_caveat_preserved(self, corrected_archive: dict, prior_dcm001: dict) -> None:
        metrics = extract_corrected_dcm001_evidence(corrected_archive)
        result = reassess_trustreport_eligibility(
            prior_eligibility_result=prior_dcm001,
            corrected_empirical_evidence=metrics,
        )
        assert RC_TYPE_I_CAVEAT in result.reason_codes
        assert result.type_i_error is not None
        assert result.type_i_error > 0.10

    def test_noisy_world_caveat_preserved(self, corrected_archive: dict, prior_dcm001: dict) -> None:
        metrics = extract_corrected_dcm001_evidence(corrected_archive)
        result = reassess_trustreport_eligibility(
            prior_eligibility_result=prior_dcm001,
            corrected_empirical_evidence=metrics,
        )
        assert RC_NOISY_WORLD_CAVEAT in result.reason_codes
        assert metrics["noisy_positive_coverage"] == 0.8

    def test_support_gates_serialized(self, corrected_archive: dict, prior_dcm001: dict) -> None:
        metrics = extract_corrected_dcm001_evidence(corrected_archive)
        result = reassess_trustreport_eligibility(
            prior_eligibility_result=prior_dcm001,
            corrected_empirical_evidence=metrics,
        )
        assert result.support_gate_status in {"pass", "support_gated"}
        assert result.prefit_gate_status in {"pass", "warning_required"}
        assert result.donor_gate_status in {"pass", "warning_required"}

    def test_authorization_always_false(self, corrected_archive: dict, prior_dcm001: dict) -> None:
        metrics = extract_corrected_dcm001_evidence(corrected_archive)
        result = reassess_trustreport_eligibility(
            prior_eligibility_result=prior_dcm001,
            corrected_empirical_evidence=metrics,
        )
        assert result.trust_report_authorized is False

    def test_reason_codes_include_supersession(
        self, corrected_archive: dict, prior_dcm001: dict
    ) -> None:
        metrics = extract_corrected_dcm001_evidence(corrected_archive)
        result = reassess_trustreport_eligibility(
            prior_eligibility_result=prior_dcm001,
            corrected_empirical_evidence=metrics,
        )
        assert RC_CORRECTED_EVIDENCE in result.reason_codes
        assert RC_HISTORICAL_SUPERSEDED in result.reason_codes
        assert RC_LEVEL_SCALE in result.reason_codes
        assert RC_AUTH_BLOCKED in result.reason_codes

    def test_reassessed_status_eligible_with_restrictions_or_candidate(
        self, corrected_archive: dict, prior_dcm001: dict
    ) -> None:
        metrics = extract_corrected_dcm001_evidence(corrected_archive)
        result = reassess_trustreport_eligibility(
            prior_eligibility_result=prior_dcm001,
            corrected_empirical_evidence=metrics,
        )
        assert result.reassessed_status in {
            STATUS_ELIGIBLE_WITH_RESTRICTIONS,
            STATUS_ELIGIBLE_CANDIDATE,
        }

    def test_deterministic_reassessment(self, corrected_archive: dict, prior_dcm001: dict) -> None:
        metrics = extract_corrected_dcm001_evidence(corrected_archive)
        a = reassess_trustreport_eligibility(
            prior_eligibility_result=prior_dcm001,
            corrected_empirical_evidence=metrics,
        )
        b = reassess_trustreport_eligibility(
            prior_eligibility_result=prior_dcm001,
            corrected_empirical_evidence=metrics,
        )
        assert a == b


class TestTrustReportEligibilityReassessmentHarness:
    def test_build_summary_schema(self) -> None:
        from panel_exp.validation.track_d_trustreport_eligibility_reassessment_001 import (
            build_trustreport_eligibility_reassessment_001,
        )

        payload = build_trustreport_eligibility_reassessment_001()
        assert REQUIRED_SUMMARY_KEYS <= set(payload.keys())

    def test_other_dcm_rows_unchanged(self) -> None:
        from panel_exp.validation.track_d_trustreport_eligibility_reassessment_001 import (
            build_trustreport_eligibility_reassessment_001,
        )

        prior = json.loads(_PRIOR.read_text())
        payload = build_trustreport_eligibility_reassessment_001()
        unchanged_keys = {
            r["combination_key"] for r in payload["unchanged_combination_results"]
        }
        prior_keys = {
            r["combination_key"]
            for r in prior["combination_results"]
            if r["combination_key"] != "DCM-001"
        }
        assert unchanged_keys == prior_keys
        for row in payload["unchanged_combination_results"]:
            assert row["unchanged_due_to_no_new_evidence"] is True

    def test_authorization_summary_invariant(self) -> None:
        from panel_exp.validation.track_d_trustreport_eligibility_reassessment_001 import (
            build_trustreport_eligibility_reassessment_001,
        )

        payload = build_trustreport_eligibility_reassessment_001()
        assert payload["authorization_summary"]["trust_report_authorized"] is False
        assert payload["authorization_summary"]["trust_report_authorized_count"] == 0
        assert payload["authorization_summary"]["trust_report_ready"] is False

    def test_verdict_in_taxonomy(self) -> None:
        from panel_exp.validation.track_d_trustreport_eligibility_reassessment_001 import (
            build_trustreport_eligibility_reassessment_001,
        )

        payload = build_trustreport_eligibility_reassessment_001()
        assert payload["verdict"] in ALLOWED_VERDICTS

    def test_no_run_results_in_summary(self, tmp_path: Path) -> None:
        from panel_exp.validation.track_d_trustreport_eligibility_reassessment_001 import (
            write_summary,
        )

        out = write_summary(tmp_path / "summary.json")
        data = json.loads(out.read_text())
        assert "run_results" not in data

    def test_report_exists_after_write(self, tmp_path: Path) -> None:
        from panel_exp.validation.track_d_trustreport_eligibility_reassessment_001 import (
            write_report,
        )

        report = write_report(tmp_path / "report.md")
        assert report.is_file()
        assert "DCM-001" in report.read_text()
