"""TRUSTREPORT-F-DECISION-INTEGRATION-001 — TrustReport F-DECISION context tests."""

from __future__ import annotations

import numpy as np
import pytest

from panel_exp.governance.decision_policy import (
    AgreementStatus,
    CalibrationSignalAction,
    DataProfile,
    DecisionPosture,
    DesignProfile,
    EstimandProfile,
    GeometryProfile,
    MmmAction,
)
from panel_exp.governance.geometry_adapter_contract import GeometryType
from panel_exp.governance.interval_semantics_contract import IntervalReadout
from panel_exp.inference_result import IntervalType
from panel_exp.track_b.f_decision_context import (
    TrustReportDecisionInputs,
    build_trust_report_f_decision_context,
)
from panel_exp.track_b.trust_report import (
    TrustComposeContext,
    compose_trust_report,
    trust_report_to_dict,
)
from tests.track_b.contract_fixtures import iter_all_fixture_cases


def _valid_band_readout(
    *,
    estimator: str,
    inference: str,
    n: int = 8,
) -> IntervalReadout:
    y = np.linspace(100.0, 108.0, n)
    hw = 2.0
    return IntervalReadout(
        estimator_name=estimator,
        inference_mode=inference,
        geometry_mode="single_cell",
        path_interval_type=IntervalType.CONFIDENCE_INTERVAL.value,
        y=y,
        y_hat=y,
        y_lower=y - hw,
        y_upper=y + hw,
        test_length=n,
        null_interval_exclusion_rate=0.0,
    )


def _unit_inputs(*, readout_evidence: list) -> TrustReportDecisionInputs:
    return TrustReportDecisionInputs(
        readout_evidence=readout_evidence,
        design=DesignProfile(design_method_id="greedy_match_markets"),
        data=DataProfile(n_treated=4, n_control=8, n_test_grps=1),
        geometry=GeometryProfile(geometry_type=GeometryType.UNIT_PANEL),
        estimand=EstimandProfile(target_estimand="unit_level_att"),
    )


def _a26_a05_a18_a19_panel(*, tbrridge_conformal_effect: float = 0.03) -> TrustReportDecisionInputs:
    return _unit_inputs(
        readout_evidence=[
            {
                "estimator_name": "SyntheticControl",
                "inference_mode": "UnitJackKnife",
                "track_b_config_alias": "SCM_UnitJackKnife",
                "interval_readout": _valid_band_readout(
                    estimator="SyntheticControl", inference="UnitJackKnife"
                ),
                "point_effect": 0.05,
            },
            {
                "estimator_name": "AugSynthCVXPY",
                "inference_mode": "Conformal",
                "audit_010_primary_bucket": "characterized_restricted",
                "interval_readout": _valid_band_readout(
                    estimator="AugSynthCVXPY",
                    inference="Conformal",
                ),
                "point_effect": 0.04,
            },
            {
                "estimator_name": "TBRRidge",
                "inference_mode": "Conformal",
                "audit_010_primary_bucket": "characterized_restricted",
                "interval_readout": _valid_band_readout(
                    estimator="TBRRidge",
                    inference="Conformal",
                ),
                "point_effect": tbrridge_conformal_effect,
            },
            {
                "estimator_name": "TBRRidge",
                "inference_mode": "TimeSeriesKfold",
                "audit_010_primary_bucket": "characterized_restricted",
                "interval_readout": _valid_band_readout(
                    estimator="TBRRidge", inference="TimeSeriesKfold"
                ),
                "point_effect": 0.02,
            },
        ]
    )


def _minimal_adapter() -> dict:
    return {
        "export_status": "complete",
        "experiment_evidence": {
            "declared_estimand_id": "unit_level_att",
            "exported_estimand_id": "unit_level_att",
        },
        "alignment_facts": {},
    }


def _compose_with_decision(
    inputs: TrustReportDecisionInputs,
    *,
    scenarios: list | None = None,
) -> dict:
    ctx = TrustComposeContext(
        spec={"declared_estimand_id": "unit_level_att"},
        adapter_output=_minimal_adapter(),
        decision_inputs=inputs,
    )
    scenarios = scenarios or [
        {
            "scenario_id": "null_viability",
            "intended_use": "null_screen",
            "claim_type": "null_viability",
        }
    ]
    return trust_report_to_dict(compose_trust_report(ctx, scenarios))


class TestBackwardCompatibility:
    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_trust_report_without_decision_unchanged(self, case) -> None:
        from tests.track_b.trust_report_composer import (
            compose_trust_report,
            trust_report_to_dict,
        )

        baseline = trust_report_to_dict(compose_trust_report(case))
        assert "f_decision_context" not in baseline

    def test_compose_without_decision_omits_f_decision_block(self) -> None:
        ctx = TrustComposeContext(
            spec={"declared_estimand_id": "unit_level_att"},
            adapter_output=_minimal_adapter(),
        )
        out = trust_report_to_dict(
            compose_trust_report(
                ctx,
                [{"scenario_id": "s1", "claim_type": "null_viability"}],
            )
        )
        assert "f_decision_context" not in out
        assert "scenarios" in out


class TestDecisionContextPresent:
    def test_includes_roles_and_posture(self) -> None:
        out = _compose_with_decision(_a26_a05_a18_a19_panel())
        assert "f_decision_context" in out
        fdc = out["f_decision_context"]
        assert fdc["primary_readout"]["inference"] == "UnitJackKnife"
        assert fdc["primary_readout"]["assigned_role"] == "primary_null_monitor"
        roles = {d["inference"]: d["assigned_role"] for d in fdc["diagnostic_comparators"]}
        assert roles["Conformal"] == "diagnostic_comparator"
        assert roles["TimeSeriesKfold"] == "diagnostic_comparator"
        assert fdc["final_decision_posture"] in (
            "proceed_with_confidence",
            "proceed_with_caveats",
            "trust_report_only",
        )
        assert fdc["promotion_candidates"] == []

    def test_scenarios_unchanged_when_decision_attached(self) -> None:
        ctx_base = TrustComposeContext(
            spec={"declared_estimand_id": "unit_level_att"},
            adapter_output=_minimal_adapter(),
        )
        scenarios = [{"scenario_id": "s1", "claim_type": "null_viability"}]
        base = trust_report_to_dict(compose_trust_report(ctx_base, scenarios))
        with_dec = _compose_with_decision(_a26_a05_a18_a19_panel(), scenarios=scenarios)
        assert base["scenarios"] == with_dec["scenarios"]


class TestRoleAssignments:
    def test_a16_a21_excluded(self) -> None:
        inputs = _unit_inputs(
            readout_evidence=[
                {
                    "estimator_name": "TBRRidge",
                    "inference_mode": "UnitJackKnife",
                    "audit_010_primary_bucket": "callable_unverified_interval_semantics",
                    "interval_readout": _valid_band_readout(
                        estimator="TBRRidge", inference="UnitJackKnife"
                    ),
                },
                {
                    "estimator_name": "TBRRidge",
                    "inference_mode": "JKP",
                    "audit_010_primary_bucket": "callable_unverified_interval_semantics",
                    "interval_readout": _valid_band_readout(
                        estimator="TBRRidge", inference="JKP"
                    ),
                },
            ]
        )
        fdc = _compose_with_decision(inputs)["f_decision_context"]
        excluded = {(r["estimator"], r["inference"]) for r in fdc["excluded_readouts"]}
        assert ("TBRRidge", "UnitJackKnife") in excluded
        assert ("TBRRidge", "JKP") in excluded

    def test_placebo_falsification_check(self) -> None:
        inputs = TrustReportDecisionInputs(
            readout_evidence=[
                {
                    "estimator_name": "SyntheticControl",
                    "inference_mode": "Placebo",
                },
            ],
            design=DesignProfile(),
            data=DataProfile(n_treated=1, n_control=8, n_test_grps=1),
            geometry=GeometryProfile(
                geometry_type=GeometryType.UNIT_PANEL,
                single_treated_geometry=True,
            ),
            estimand=EstimandProfile(),
        )
        fdc = _compose_with_decision(inputs)["f_decision_context"]
        assert len(fdc["falsification_checks"]) == 1
        assert fdc["falsification_checks"][0]["assigned_role"] == "falsification_check"

    def test_tbr_unit_panel_blocked(self) -> None:
        inputs = _unit_inputs(
            readout_evidence=[
                {
                    "estimator_name": "TBR",
                    "inference_mode": "Kfold",
                    "interval_readout": _valid_band_readout(estimator="TBR", inference="Kfold"),
                },
            ]
        )
        fdc = _compose_with_decision(inputs)["f_decision_context"]
        blocked = {(r["estimator"], r["inference"]) for r in fdc["blocked_readouts"]}
        assert ("TBR", "Kfold") in blocked


class TestEvidencePosture:
    def test_conflicting_signs_warning_not_averaging(self) -> None:
        inputs = _a26_a05_a18_a19_panel(tbrridge_conformal_effect=-0.08)
        fdc = _compose_with_decision(inputs)["f_decision_context"]
        assert fdc["agreement_status"] == AgreementStatus.DIAGNOSTIC_DISAGREEMENT.value
        assert fdc["trust_report_action"] == "emit_warning"
        assert any("no silent averaging" in w.lower() for w in fdc["required_warnings"])

    def test_falsification_failure_blocks_posture(self) -> None:
        inputs = TrustReportDecisionInputs(
            readout_evidence=[
                {
                    "estimator_name": "SyntheticControl",
                    "inference_mode": "UnitJackKnife",
                    "track_b_config_alias": "SCM_UnitJackKnife",
                    "interval_readout": _valid_band_readout(
                        estimator="SyntheticControl", inference="UnitJackKnife"
                    ),
                    "point_effect": 0.05,
                },
                {
                    "estimator_name": "SyntheticControl",
                    "inference_mode": "Placebo",
                    "falsification_passed": False,
                },
            ],
            design=DesignProfile(),
            data=DataProfile(n_treated=1, n_control=8, n_test_grps=1),
            geometry=GeometryProfile(
                geometry_type=GeometryType.UNIT_PANEL,
                single_treated_geometry=True,
            ),
            estimand=EstimandProfile(),
        )
        fdc = _compose_with_decision(inputs)["f_decision_context"]
        assert fdc["agreement_status"] == AgreementStatus.FALSIFICATION_FAILURE.value
        assert fdc["final_decision_posture"] == DecisionPosture.BLOCKED_FOR_DECISION_USE.value


class TestGuardrails:
    def test_calibration_signal_only_primary(self) -> None:
        fdc = _compose_with_decision(_a26_a05_a18_a19_panel())["f_decision_context"]
        assert fdc["calibration_signal_action"] == (
            CalibrationSignalAction.EXPORT_CALIBRATION_SIGNAL.value
        )
        for d in fdc["diagnostic_comparators"]:
            assert d["calibration_signal_eligible"] is False

    def test_mmm_exclude(self) -> None:
        fdc = _compose_with_decision(_a26_a05_a18_a19_panel())["f_decision_context"]
        assert fdc["mmm_action"] == MmmAction.EXCLUDE_FROM_MMM.value
        assert fdc["mmm_status"] == "not_ready_continue_track_f"

    def test_no_governed_uncertainty(self) -> None:
        fdc = _compose_with_decision(_a26_a05_a18_a19_panel())["f_decision_context"]
        for p in fdc["eligible_readout_profiles"]:
            assert p["is_governed_uncertainty"] is False


class TestIncompleteMetadata:
    def test_incomplete_emits_warning_not_strict(self) -> None:
        inputs = _unit_inputs(
            readout_evidence=[
                {"estimator_name": "TBRRidge"},
            ]
        )
        fdc = _compose_with_decision(inputs)["f_decision_context"]
        assert fdc["decision_context_complete"] is False
        assert any("decision_context_incomplete" in w for w in fdc["required_warnings"])

    def test_strict_raises_on_incomplete(self) -> None:
        inputs = _unit_inputs(
            readout_evidence=[{"estimator_name": "TBRRidge"}],
        )
        inputs = TrustReportDecisionInputs(
            readout_evidence=inputs.readout_evidence,
            design=inputs.design,
            data=inputs.data,
            geometry=inputs.geometry,
            estimand=inputs.estimand,
            strict=True,
        )
        with pytest.raises(ValueError, match="decision_context_incomplete"):
            build_trust_report_f_decision_context(inputs)


class TestPooledAndGeometryBlocks:
    def test_pooled_multi_cell_blocked(self) -> None:
        inputs = TrustReportDecisionInputs(
            readout_evidence=[
                {
                    "estimator_name": "TBRRidge",
                    "inference_mode": "Kfold",
                },
            ],
            design=DesignProfile(pooling_rule_id=None),
            data=DataProfile(n_treated=2, n_control=8, n_test_grps=2),
            geometry=GeometryProfile(
                geometry_type=GeometryType.POOLED_MULTI_CELL,
                pooled_claim=True,
            ),
            estimand=EstimandProfile(),
        )
        fdc = _compose_with_decision(inputs)["f_decision_context"]
        assert any(r["assigned_role"] == "blocked" for r in fdc["blocked_readouts"])
