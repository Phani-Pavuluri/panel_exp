"""B5b — adapter output oracle comparison scaffolding.

Compares adapter-shaped dicts to fixture expectations. Real adapter wiring is
optional and skipped until implemented; oracle self-check proves the comparator.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.track_b.contract_fixtures import (
    FixtureCase,
    compare_adapter_output_to_oracle,
    iter_all_fixture_cases,
    load_fixture_document,
)


def _oracle_adapter_output(case: FixtureCase) -> dict[str, Any]:
    """Fixture truth table — not adapter business logic."""
    return case.adapter_expected_output


def resolve_adapter_output(case: FixtureCase) -> dict[str, Any]:
    """Resolve adapter output via M2 geo adapter (fixture slice = live export input)."""
    from panel_exp.track_b.geo_adapter import resolve_geo_adapter_output

    return resolve_geo_adapter_output(
        spec=case.spec,
        run_artifacts_stub=case.run_artifacts_stub,
        calibration_signal_binding=case.calibration_signal_binding,
    )


@pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
class TestOracleSelfComparison:
    """Comparator sanity: oracle matches itself for every case."""

    def test_oracle_matches_itself(self, case: FixtureCase) -> None:
        oracle = _oracle_adapter_output(case)
        mismatches = compare_adapter_output_to_oracle(oracle, oracle)
        assert mismatches == [], "\n".join(mismatches)


@pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
class TestAdapterOutputMatchesOracle:
    """When adapter is wired, actual output must match fixture oracle exactly."""

    def test_adapter_output_matches_fixture_oracle(self, case: FixtureCase) -> None:
        try:
            actual = resolve_adapter_output(case)
        except NotImplementedError:
            pytest.skip("Track B adapter not implemented")
        oracle = _oracle_adapter_output(case)
        mismatches = compare_adapter_output_to_oracle(actual, oracle)
        assert mismatches == [], "\n".join(mismatches)


class TestGoldenSpecificOracleRules:
    """Normative rules from B5 plan — asserted on fixture oracle, not recomputed."""

    def test_gold_006_blocked_decision_grade(self) -> None:
        case = _case("GOLD-006")
        assert case.export_status == "blocked"
        ev = case.adapter_expected_output["experiment_evidence"]
        assert ev.get("decision_grade_export_permitted") is False

    def test_gold_010_partial_geometry(self) -> None:
        case = _case("GOLD-010")
        assert case.export_status == "partial"
        facts = case.adapter_expected_output["alignment_facts"]
        assert facts["geometry_within_scope"] is False

    def test_gold_003_no_interval_estimand_on_evidence(self) -> None:
        case = _case("GOLD-003")
        ev = case.adapter_expected_output["experiment_evidence"]
        assert "interval_estimand_id" not in ev
        assert ev.get("interval_semantics") == "none"

    def test_gold_005_placebo_band_not_ci(self) -> None:
        case = _case("GOLD-005")
        ev = case.adapter_expected_output["experiment_evidence"]
        assert ev.get("interval_semantics") == "placebo_band"

    def test_gold_001_lift_launch_not_supported_in_trust_fixture(self) -> None:
        case = _case("GOLD-001")
        scenarios = case.trust_report_expected_output["scenarios"]
        lift = next(s for s in scenarios if s["scenario_id"] == "lift_launch")
        assert lift["trust_outcome"] == "inconclusive"
        assert lift["trust_outcome"] != "supported"

    def test_gold_004_mmm_intake_blocked_variants(self) -> None:
        for variant_id in ("no_transform_ref", "transform_ref_incomplete_pipeline"):
            case = _case("GOLD-004", variant_id=variant_id)
            ev = case.adapter_expected_output["experiment_evidence"]
            assert ev.get("mmm_intake_blocked") is True
            assert ev.get("mmm_export_ready") is False


class TestMislabelRegressionVariant:
    def test_gold_005_mislabel_variant_interval_incompatible(self) -> None:
        doc = load_fixture_document("gold_005_placebo_semantics.json")
        variant = doc["mislabel_regression_variant"]
        assert variant["adapter_expected_output"]["alignment_facts"][
            "interval_semantics_compatible"
        ] is False


def _case(fixture_id: str, *, variant_id: str | None = None) -> FixtureCase:
    for case in iter_all_fixture_cases():
        if case.fixture_id == fixture_id and case.variant_id == variant_id:
            return case
    raise KeyError(f"no case {fixture_id} variant={variant_id}")
