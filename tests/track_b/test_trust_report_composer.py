"""B5c — TrustReport composer contract tests.

Golden fixtures are the oracle for ``alignment_verdict`` and ``trust_outcome``.
The contract composer interprets adapter facts; tests prove it matches B5a.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.track_b.contract_fixtures import (
    TRUST_VERDICT_FIELDS,
    compare_adapter_output_to_oracle,
    iter_all_fixture_cases,
)
from tests.track_b.trust_report_composer import (
    compose_trust_report,
    compose_trust_scenario_verdict,
    trust_report_to_dict,
)


def _iter_trust_scenarios():
    for case in iter_all_fixture_cases():
        for scenario in case.trust_report_expected_output.get("scenarios") or []:
            yield case, scenario


class TestTrustBoundaryNoVerdictsOnLowerLayers:
    """Verdict fields exist only on TrustReport composition output."""

    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_adapter_evidence_has_no_trust_verdicts(self, case) -> None:
        evidence = case.adapter_expected_output.get("experiment_evidence") or {}
        for field in TRUST_VERDICT_FIELDS:
            assert field not in evidence, f"{case.case_key}: evidence has {field}"

    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_adapter_output_root_has_no_trust_verdicts(self, case) -> None:
        adapter = case.adapter_expected_output
        for field in TRUST_VERDICT_FIELDS:
            assert field not in adapter, f"{case.case_key}: adapter root has {field}"

    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_diagnostic_summary_has_no_trust_verdicts(self, case) -> None:
        diag = case.adapter_expected_output.get("diagnostic_summary")
        if not isinstance(diag, dict):
            return
        for field in TRUST_VERDICT_FIELDS:
            assert field not in diag, f"{case.case_key}: diagnostic has {field}"

    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_calibration_signal_binding_has_no_trust_verdicts(self, case) -> None:
        signal = case.calibration_signal_binding
        if not signal:
            return
        for field in TRUST_VERDICT_FIELDS:
            assert field not in signal, f"{case.case_key}: signal binding has {field}"


_TRUST_SCENARIO_PARAMS = [
    pytest.param(
        case,
        scenario,
        id=f"{case.case_key}:{scenario['scenario_id']}",
    )
    for case, scenario in _iter_trust_scenarios()
]


class TestTrustReportComposerMatchesGoldenOracle:
    @pytest.mark.parametrize("case,scenario", _TRUST_SCENARIO_PARAMS)
    def test_scenario_verdict_matches_fixture(
        self, case, scenario: dict[str, Any]
    ) -> None:
        composed = compose_trust_scenario_verdict(case, scenario)
        assert composed.alignment_verdict == scenario["alignment_verdict"], (
            f"{case.case_key}/{scenario['scenario_id']}: alignment_verdict "
            f"got {composed.alignment_verdict!r}, "
            f"oracle {scenario['alignment_verdict']!r}"
        )
        assert composed.trust_outcome == scenario["trust_outcome"], (
            f"{case.case_key}/{scenario['scenario_id']}: trust_outcome "
            f"got {composed.trust_outcome!r}, oracle {scenario['trust_outcome']!r}"
        )

    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_full_composition_scenarios_match_fixture(self, case) -> None:
        composed = trust_report_to_dict(compose_trust_report(case))
        oracle_scenarios = {
            s["scenario_id"]: s
            for s in case.trust_report_expected_output.get("scenarios") or []
        }
        for scenario in composed["scenarios"]:
            sid = scenario["scenario_id"]
            assert sid in oracle_scenarios, f"missing oracle for {sid}"
            oracle = oracle_scenarios[sid]
            assert scenario["alignment_verdict"] == oracle["alignment_verdict"]
            assert scenario["trust_outcome"] == oracle["trust_outcome"]

    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_alignment_reference_estimand_from_fixture(self, case) -> None:
        composed = compose_trust_report(case)
        expected = case.trust_report_expected_output.get(
            "alignment_reference_estimand_id"
        )
        if expected:
            assert composed.alignment_reference_estimand_id == expected


class TestTrustReportGoldenThemes:
    """Named regression themes from B5 plan — explicit fixture IDs."""

    def test_gold_001_null_supported_lift_inconclusive(self) -> None:
        case = _case("GOLD-001")
        null_s = _scenario(case, "null_screen")
        lift_s = _scenario(case, "lift_launch")
        assert compose_trust_scenario_verdict(case, null_s).trust_outcome == "supported"
        assert (
            compose_trust_scenario_verdict(case, lift_s).trust_outcome == "inconclusive"
        )

    def test_gold_002_restricted_not_supported_for_cal_lift(self) -> None:
        case = _case("GOLD-002")
        s = _scenario(case, "calibration_backed_lift")
        outcome = compose_trust_scenario_verdict(case, s).trust_outcome
        assert outcome in ("inconclusive", "not_assessable")
        assert outcome != "supported"

    def test_gold_003_no_fake_ci_for_interval_lift(self) -> None:
        case = _case("GOLD-003")
        s = _scenario(case, "interval_lift_claim")
        v = compose_trust_scenario_verdict(case, s)
        assert v.trust_outcome == "unsupported"
        assert v.alignment_verdict == "incompatible"

    def test_gold_004_mmm_blocked_without_transform(self) -> None:
        case = _case("GOLD-004", "no_transform_ref")
        s = _scenario(case, "mmm_intake")
        v = compose_trust_scenario_verdict(case, s)
        assert v.trust_outcome == "unsupported"

    def test_gold_005_placebo_not_ci_for_lift(self) -> None:
        case = _case("GOLD-005")
        s = _scenario(case, "lift_via_placebo_band")
        assert compose_trust_scenario_verdict(case, s).trust_outcome == "unsupported"

    def test_gold_006_blocked_not_assessable(self) -> None:
        case = _case("GOLD-006")
        s = _scenario(case, "any_claim")
        v = compose_trust_scenario_verdict(case, s)
        assert v.trust_outcome == "not_assessable"
        assert v.alignment_verdict == "not_assessable"

    def test_gold_008_cumulative_not_relative_lift(self) -> None:
        case = _case("GOLD-008")
        s = _scenario(case, "relative_lift_via_did_interval")
        assert compose_trust_scenario_verdict(case, s).trust_outcome == "unsupported"

    def test_gold_009_ab_drift_divergent_inconclusive(self) -> None:
        case = _case("GOLD-009")
        s = _scenario(case, "business_claim_cell_mean")
        v = compose_trust_scenario_verdict(case, s)
        assert v.alignment_verdict == "divergent"
        assert v.trust_outcome == "inconclusive"

    def test_gold_010_partial_geometry_not_assessable_or_unsupported(self) -> None:
        case = _case("GOLD-010")
        null_v = compose_trust_scenario_verdict(case, _scenario(case, "placebo_null_reference"))
        lift_v = compose_trust_scenario_verdict(case, _scenario(case, "any_lift"))
        assert null_v.trust_outcome == "not_assessable"
        assert lift_v.trust_outcome == "unsupported"


class TestComposerUsesAdapterFactsNotRecomputedBusinessLogic:
    def test_changing_oracle_fact_changes_verdict(self) -> None:
        """Composer reads alignment facts from adapter output dict only."""
        case = _case("GOLD-001")
        scenario = _scenario(case, "lift_launch")
        base = compose_trust_scenario_verdict(case, scenario)
        assert base.trust_outcome == "inconclusive"

    def test_compare_helper_still_oracle_driven_for_adapter(self) -> None:
        case = _case("GOLD-001")
        oracle = case.adapter_expected_output
        assert compare_adapter_output_to_oracle(oracle, oracle) == []


def _case(fixture_id: str, variant_id: str | None = None):
    for case in iter_all_fixture_cases():
        if case.fixture_id == fixture_id and case.variant_id == variant_id:
            return case
    raise KeyError(fixture_id)


def _scenario(case, scenario_id: str) -> dict[str, Any]:
    for s in case.trust_report_expected_output.get("scenarios") or []:
        if s["scenario_id"] == scenario_id:
            return s
    raise KeyError(scenario_id)
