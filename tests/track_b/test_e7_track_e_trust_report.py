"""Track E E7 — production TrustReport composer + E4 fixture integration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.track_b.trust_report import (
    TrustComposeContext,
    compose_trust_report,
    trust_report_to_dict,
)
from panel_exp.track_b.triangulation import trust_verdicts_from_triangulation
from tests.track_e.triangulation_contract import (
    FIXTURES_DIR,
    evaluate_e4_fixture,
    evaluate_triangulation_fixture,
    load_e4_fixture,
    load_manifest,
)

MANIFEST = FIXTURES_DIR / "manifest.json"


def _minimal_adapter(profile: dict) -> dict:
    return {
        "export_status": "complete",
        "experiment_evidence": {
            "declared_estimand_id": profile.get("declared_estimand_id"),
            "exported_estimand_id": profile.get("declared_estimand_id"),
        },
        "alignment_facts": {},
    }


def _compose_e4_fixture(fixture: dict) -> dict:
    profile = fixture["triangulation_profile"]
    claim = fixture.get("declared_claim_type") or profile.get("declared_claim_type", "any")
    ctx = TrustComposeContext(
        spec={"declared_estimand_id": profile.get("declared_estimand_id")},
        adapter_output=_minimal_adapter(profile),
        triangulation_profile=profile,
        triangulation_forbidden_actions=fixture.get("forbidden_actions") or [],
    )
    scenarios = [
        {
            "scenario_id": fixture["fixture_id"],
            "intended_use": "track_e_e4",
            "claim_type": claim,
        }
    ]
    return trust_report_to_dict(compose_trust_report(ctx, scenarios))


class TestE7ProductionComposer:
    @pytest.fixture(params=[e["file"] for e in json.loads(MANIFEST.read_text())["fixtures"]])
    def fixture(self, request: pytest.FixtureRequest) -> dict:
        return load_e4_fixture(request.param)

    def test_track_e_triangulation_block_matches_oracle(self, fixture: dict) -> None:
        got = _compose_e4_fixture(fixture)
        oracle = evaluate_e4_fixture(fixture)
        expected = fixture["expected"]
        te = got["track_e_triangulation"]
        assert te["agreement_state"] == expected["agreement_state"]
        assert te["trust_report_disposition"] == expected["trust_report_disposition"]
        assert te["conflict_class"] == expected["conflict_class"]
        for key, val in expected["calibration_signal_eligibility"].items():
            assert te["calibration_signal_eligibility"].get(key) == val, (
                f"{fixture['fixture_id']} cs.{key}"
            )
        assert te["forbidden_violations"] == list(oracle.forbidden_violations)

    def test_scenario_trust_outcome_matches_hint_with_claim_caps(self, fixture: dict) -> None:
        got = _compose_e4_fixture(fixture)
        oracle = evaluate_e4_fixture(fixture)
        profile = fixture["triangulation_profile"]
        claim = fixture.get("declared_claim_type") or profile.get("declared_claim_type", "any")
        expected_alignment, expected_outcome = trust_verdicts_from_triangulation(oracle, claim)
        scenario = got["scenarios"][0]
        assert scenario["alignment_verdict"] == expected_alignment
        assert scenario["trust_outcome"] == expected_outcome
        assert scenario["trust_outcome"] == fixture["expected"]["trust_outcome_hint"]

    def test_forbidden_action_flags_no_violations(self, fixture: dict) -> None:
        got = _compose_e4_fixture(fixture)
        te = got["track_e_triangulation"]
        assert te["forbidden_violations"] == []
        for action, violated in te["forbidden_action_flags"].items():
            assert violated is False, action

    def test_no_mmm_ingress_on_track_e_block(self, fixture: dict) -> None:
        cs = _compose_e4_fixture(fixture)["track_e_triangulation"]["calibration_signal_eligibility"]
        assert cs.get("mmm_ingress_allowed") is not True
        if not cs.get("eligible"):
            assert cs.get("lift_mmm_allowed") is not True

    def test_per_cell_dispositions_when_expected(self, fixture: dict) -> None:
        expected = fixture["expected"]
        if "per_cell_dispositions" not in expected:
            pytest.skip("no per_cell_dispositions in fixture")
        te = _compose_e4_fixture(fixture)["track_e_triangulation"]
        assert te["per_cell_dispositions"] == expected["per_cell_dispositions"]


class TestE7BackwardCompatibility:
    def test_compose_without_triangulation_unchanged_shape(self) -> None:
        ctx = TrustComposeContext(
            spec={"declared_estimand_id": "geo.relative_att_post.pooled_path.relative"},
            adapter_output={
                "export_status": "complete",
                "experiment_evidence": {
                    "declared_estimand_id": "geo.relative_att_post.pooled_path.relative",
                    "exported_estimand_id": "geo.relative_att_post.pooled_path.relative",
                },
                "alignment_facts": {"declared_exported_aligned": True},
            },
            calibration_signal_binding={
                "expected_usage_boundary": "null_monitor_only",
            },
        )
        d = trust_report_to_dict(
            compose_trust_report(
                ctx,
                [
                    {
                        "scenario_id": "null",
                        "claim_type": "null_viability",
                        "intended_use": "test",
                    }
                ],
            )
        )
        assert "track_e_triangulation" not in d
        assert d["scenarios"][0]["trust_outcome"] == "supported"


class TestE7GovernanceSpotChecks:
    def test_e4_002_restricted_no_lift(self) -> None:
        fx = load_e4_fixture("e4_002_primary_null_restricted_tbr_positive.json")
        got = _compose_e4_fixture(fx)
        assert (
            got["track_e_triangulation"]["trust_report_disposition"]
            == "restricted_method_positive_but_primary_null_compatible"
        )
        assert got["track_e_triangulation"]["calibration_signal_eligibility"]["eligible"] is False
        assert got["scenarios"][0]["trust_outcome"] == "inconclusive"

    def test_e4_003_method_conflict_divergent(self) -> None:
        fx = load_e4_fixture("e4_003_scm_did_opposite_sign.json")
        got = _compose_e4_fixture(fx)
        assert got["scenarios"][0]["trust_outcome"] == "divergent"

    def test_all_fixtures_compose(self) -> None:
        manifest = load_manifest()
        for entry in manifest["fixtures"]:
            fx = load_e4_fixture(entry["file"])
            got = _compose_e4_fixture(fx)
            assert "track_e_triangulation" in got
            evaluate_triangulation_fixture(fx)
