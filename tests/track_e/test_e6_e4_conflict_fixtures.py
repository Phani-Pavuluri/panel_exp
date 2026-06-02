"""Track E E6 — TrustReport / CalibrationSignal contract tests for E4 fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.track_e.triangulation_contract import (
    FIXTURES_DIR,
    apply_e5_calibration_policy,
    assert_forbidden_actions,
    evaluate_e4_fixture,
    evaluate_triangulation,
    load_all_e4_fixtures,
    load_e4_fixture,
    load_manifest,
)

MANIFEST = FIXTURES_DIR / "manifest.json"


class TestE4Manifest:
    def test_manifest_lists_ten_fixtures(self) -> None:
        manifest = load_manifest()
        assert len(manifest["fixtures"]) == 10
        for entry in manifest["fixtures"]:
            path = FIXTURES_DIR / entry["file"]
            assert path.is_file(), entry["file"]


class TestE6TriangulationContract:
    @pytest.fixture(params=[e["file"] for e in json.loads(MANIFEST.read_text())["fixtures"]])
    def fixture(self, request: pytest.FixtureRequest) -> dict:
        return load_e4_fixture(request.param)

    def test_disposition_matches_fixture_oracle(self, fixture: dict) -> None:
        outcome = evaluate_e4_fixture(fixture)
        expected = fixture["expected"]
        assert outcome.trust_report_disposition == expected["trust_report_disposition"]
        assert outcome.agreement_state == expected["agreement_state"]
        assert outcome.conflict_class == expected["conflict_class"]

    def test_trust_outcome_hint(self, fixture: dict) -> None:
        outcome = evaluate_e4_fixture(fixture)
        assert outcome.trust_outcome_hint == fixture["expected"]["trust_outcome_hint"]

    def test_calibration_signal_eligibility_policy(self, fixture: dict) -> None:
        outcome = evaluate_e4_fixture(fixture)
        expected_cs = fixture["expected"]["calibration_signal_eligibility"]
        actual_cs = outcome.calibration_signal_eligibility
        for key, val in expected_cs.items():
            assert actual_cs.get(key) == val, f"{fixture['fixture_id']} cs.{key}"

    def test_no_mmm_ingress_outside_calibration_signal(self, fixture: dict) -> None:
        outcome = evaluate_e4_fixture(fixture)
        cs = outcome.calibration_signal_eligibility
        assert cs.get("mmm_ingress_allowed") is not True
        if not cs.get("eligible"):
            assert cs.get("lift_mmm_allowed") is not True

    def test_forbidden_actions_not_violated(self, fixture: dict) -> None:
        outcome = evaluate_e4_fixture(fixture)
        assert outcome.forbidden_violations == ()

    def test_no_silent_averaging(self, fixture: dict) -> None:
        outcome = evaluate_e4_fixture(fixture)
        assert "combined_point_estimate" not in outcome.calibration_signal_eligibility
        profile = fixture["triangulation_profile"]
        if profile.get("geometry_mode") == "multi_cell" and not profile.get("pooling_rule_id"):
            assert outcome.calibration_signal_eligibility.get("pooled_allowed") is not True

    def test_per_cell_dispositions_when_expected(self, fixture: dict) -> None:
        expected = fixture["expected"]
        if "per_cell_dispositions" not in expected:
            pytest.skip("no per_cell_dispositions in fixture")
        outcome = evaluate_e4_fixture(fixture)
        assert outcome.per_cell_dispositions == expected["per_cell_dispositions"]


class TestE6SpecificGovernanceRules:
    def test_e4_002_no_lift_calibration(self) -> None:
        fx = load_e4_fixture("e4_002_primary_null_restricted_tbr_positive.json")
        outcome = evaluate_e4_fixture(fx)
        assert outcome.trust_report_disposition == "restricted_method_positive_but_primary_null_compatible"
        assert outcome.calibration_signal_eligibility["eligible"] is False

    def test_e4_003_conflict_fail_closed(self) -> None:
        fx = load_e4_fixture("e4_003_scm_did_opposite_sign.json")
        outcome = evaluate_e4_fixture(fx)
        assert outcome.trust_report_disposition == "method_conflict_warning"
        assert outcome.calibration_signal_eligibility.get("lift_mmm_allowed") is not True

    def test_e4_007_geo_power_no_mmm(self) -> None:
        fx = load_e4_fixture("e4_007_geo_power_planning_only.json")
        outcome = evaluate_e4_fixture(fx)
        assert outcome.trust_report_disposition == "planning_diagnostic_only"
        assert outcome.calibration_signal_eligibility["eligible"] is False
        assert outcome.calibration_signal_eligibility.get("mmm_mde_feed_forbidden") is True

    def test_e4_005_multi_cell_no_pool(self) -> None:
        fx = load_e4_fixture("e4_005_multi_cell_cell_conflict.json")
        outcome = evaluate_e4_fixture(fx)
        assert outcome.calibration_signal_eligibility.get("pooled_allowed") is False
        violations = assert_forbidden_actions(
            outcome,
            fx["triangulation_profile"],
            fx["forbidden_actions"],
        )
        assert violations == []

    def test_restricted_cannot_override_primary(self) -> None:
        fx = load_e4_fixture("e4_002_primary_null_restricted_tbr_positive.json")
        profile = fx["triangulation_profile"]
        outcome = evaluate_triangulation(profile)
        cs = apply_e5_calibration_policy(outcome)
        assert outcome.trust_outcome_hint != "supported"
        assert cs["eligible"] is False

    def test_diagnostic_only_no_lift_promotion(self) -> None:
        fx = load_e4_fixture("e4_001_scm_jk_tbr_same_direction.json")
        outcome = evaluate_e4_fixture(fx)
        assert outcome.trust_outcome_hint in {"supported_with_limitations", "inconclusive"}
        assert outcome.calibration_signal_eligibility.get("lift_mmm_allowed") is False

    def test_all_fixtures_load_and_evaluate(self) -> None:
        for fx in load_all_e4_fixtures():
            outcome = evaluate_e4_fixture(fx)
            assert outcome.trust_report_disposition
            assert outcome.forbidden_violations == ()
