"""Tests for DCM-004 TrustReport eligibility reassessment core logic."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.dcm004_trustreport_eligibility_reassessment_001 import (
    RC_AUTH_BLOCKED,
    RC_CORRECTED_EVIDENCE,
    RC_CUMULATIVE_SCALE,
    RC_ELIGIBLE_RESTRICTIONS,
    RC_POSITIVE_IMPROVED,
    WORLD_TO_CLASS,
    classify_world,
    extract_post_fix_dcm004_evidence,
    reassess_dcm004_trustreport_eligibility,
)
from panel_exp.validation.track_d_d5_stat_did_bootstrap_001 import build_d5_stat_did_bootstrap_001

_REPO = Path(__file__).resolve().parents[2]
_PRIOR = _REPO / "docs/track_d/archives/TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json"
_CORRECTION = _REPO / "docs/track_d/archives/DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001_summary.json"


@pytest.fixture(scope="module")
def post_fix_archive() -> dict:
    return build_d5_stat_did_bootstrap_001()


@pytest.fixture(scope="module")
def correction_summary() -> dict | None:
    if not _CORRECTION.is_file():
        return None
    return json.loads(_CORRECTION.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def prior_dcm004() -> dict:
    prior = json.loads(_PRIOR.read_text(encoding="utf-8"))
    for row in prior["combination_results"]:
        if row["combination_key"] == "DCM-004":
            return row
    raise KeyError("DCM-004")


@pytest.fixture(scope="module")
def metrics(post_fix_archive: dict, correction_summary: dict) -> dict:
    return extract_post_fix_dcm004_evidence(
        post_fix_archive, correction_summary=correction_summary
    )


class TestDCM004ReassessmentCore:
    def test_world_classification_mapping(self) -> None:
        assert classify_world("clean_parallel_null") == "supported_clean_parallel_common_timing"
        assert classify_world("post_shock_null") == "stress_or_outlier"
        assert classify_world("trend_violation_null") == "parallel_trends_violation"
        assert len(WORLD_TO_CLASS) == 7

    def test_extract_post_fix_evidence_scale(self, metrics: dict) -> None:
        assert metrics["effect_scale"] == "cumulative_level"
        assert metrics["positive_coverage_overall"] is not None
        assert metrics["type_i_error_supported"] is not None
        assert "calibration_by_world_class" in metrics

    def test_supported_vs_unsupported_type_i_decomposition(self, metrics: dict) -> None:
        assert metrics["type_i_error_overall"] is not None
        assert metrics["type_i_error_supported"] is not None
        assert metrics["type_i_error_unsupported"] is not None
        assert metrics["type_i_error_supported"] < metrics["type_i_error_overall"]
        assert metrics["post_shock_null_type_i"] == 1.0

    def test_positive_coverage_improved(self, metrics: dict) -> None:
        assert (metrics.get("positive_coverage_overall") or 0) >= 0.5
        if metrics.get("before_positive_coverage") is not None:
            assert metrics["before_positive_coverage"] < 0.25

    def test_reassess_dcm004_eligible_with_restrictions(
        self, prior_dcm004: dict, metrics: dict
    ) -> None:
        result = reassess_dcm004_trustreport_eligibility(
            prior_eligibility_result=prior_dcm004,
            corrected_empirical_evidence=metrics,
        )
        assert result.dcm_row_id == "DCM-004"
        assert result.prior_status == "INSUFFICIENT_EVIDENCE"
        assert result.reassessed_status == "ELIGIBLE_WITH_RESTRICTIONS"
        assert result.trust_report_authorized is False
        assert result.eligible_for_promotion is False
        assert RC_CORRECTED_EVIDENCE in result.reason_codes
        assert RC_CUMULATIVE_SCALE in result.reason_codes
        assert RC_POSITIVE_IMPROVED in result.reason_codes
        assert RC_ELIGIBLE_RESTRICTIONS in result.reason_codes
        assert RC_AUTH_BLOCKED in result.reason_codes

    def test_scale_mismatch_ineligible(self, prior_dcm004: dict, metrics: dict) -> None:
        bad = dict(metrics)
        bad["effect_scale"] = "fractional_percent"
        result = reassess_dcm004_trustreport_eligibility(
            prior_eligibility_result=prior_dcm004,
            corrected_empirical_evidence=bad,
        )
        assert result.reassessed_status == "INELIGIBLE"

    def test_geometry_fail_ineligible(self, prior_dcm004: dict, metrics: dict) -> None:
        bad = dict(metrics)
        bad["n_control_mean"] = 0.0
        result = reassess_dcm004_trustreport_eligibility(
            prior_eligibility_result=prior_dcm004,
            corrected_empirical_evidence=bad,
        )
        assert result.reassessed_status == "INELIGIBLE"

    def test_gate_statuses_recorded(self, prior_dcm004: dict, metrics: dict) -> None:
        result = reassess_dcm004_trustreport_eligibility(
            prior_eligibility_result=prior_dcm004,
            corrected_empirical_evidence=metrics,
        )
        assert result.geometry_gate_status == "pass"
        assert result.scale_gate_status == "pass"
        assert result.timing_gate_status == "pass"
        assert result.parallel_trends_gate_status == "warning_required"
