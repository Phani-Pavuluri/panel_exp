"""F-DECISION-001 — method eligibility resolver and evidence decision policy."""

from __future__ import annotations

import numpy as np
import pytest

from panel_exp.governance.decision_policy import (
    AgreementStatus,
    CalibrationSignalAction,
    CandidateReadout,
    DataProfile,
    DecisionPosture,
    DecisionRole,
    DesignProfile,
    EstimandProfile,
    EvidenceDecisionProfile,
    GeometryProfile,
    MmmAction,
    MMM_DEFAULT_STATUS,
    TrustReportAction,
    build_evidence_decision,
    resolve_eligible_readout,
    resolve_eligible_readouts,
)
from panel_exp.governance.geometry_adapter_contract import GeometryType
from panel_exp.governance.interval_semantics_contract import IntervalReadout
from panel_exp.inference_result import IntervalType


def _valid_band_readout(
    *,
    estimator: str,
    inference: str,
    geometry: str = "single_cell",
    n: int = 8,
    path_interval_type: str = IntervalType.CONFIDENCE_INTERVAL.value,
) -> IntervalReadout:
    y = np.linspace(100.0, 108.0, n)
    hw = 2.0
    return IntervalReadout(
        estimator_name=estimator,
        inference_mode=inference,
        geometry_mode=geometry,
        path_interval_type=path_interval_type,
        y=y,
        y_hat=y,
        y_lower=y - hw,
        y_upper=y + hw,
        test_length=n,
        null_interval_exclusion_rate=0.0,
    )


def _unit_panel_profiles(*, n_treated: int = 4) -> tuple:
    return (
        DesignProfile(design_method_id="greedy_match_markets"),
        DataProfile(n_treated=n_treated, n_control=8, n_test_grps=1),
        GeometryProfile(geometry_type=GeometryType.UNIT_PANEL),
        EstimandProfile(target_estimand="unit_level_att"),
    )


class TestPrimaryAndDiagnosticRoles:
    def test_scm_jk_primary_restricted_diagnostics(self) -> None:
        design, data, geometry, estimand = _unit_panel_profiles()
        candidates = [
            CandidateReadout(
                estimator_name="SyntheticControl",
                inference_mode="UnitJackKnife",
                interval_readout=_valid_band_readout(
                    estimator="SyntheticControl", inference="UnitJackKnife"
                ),
                track_b_config_alias="SCM_UnitJackKnife",
                point_effect=0.05,
            ),
            CandidateReadout(
                estimator_name="AugSynthCVXPY",
                inference_mode="Conformal",
                audit_010_primary_bucket="characterized_restricted",
                interval_readout=_valid_band_readout(
                    estimator="AugSynthCVXPY",
                    inference="Conformal",
                    path_interval_type=IntervalType.CONFORMAL_INTERVAL.value,
                ),
                point_effect=0.04,
            ),
            CandidateReadout(
                estimator_name="TBRRidge",
                inference_mode="Conformal",
                audit_010_primary_bucket="characterized_restricted",
                interval_readout=_valid_band_readout(
                    estimator="TBRRidge",
                    inference="Conformal",
                    path_interval_type=IntervalType.CONFORMAL_INTERVAL.value,
                ),
                point_effect=0.03,
            ),
        ]
        profiles = resolve_eligible_readouts(
            candidates, design=design, data=data, geometry=geometry, estimand=estimand
        )
        roles = {p.inference: p.assigned_role for p in profiles}
        assert roles["UnitJackKnife"] == DecisionRole.PRIMARY_NULL_MONITOR
        assert roles["Conformal"] in (
            DecisionRole.DIAGNOSTIC_COMPARATOR,
            DecisionRole.DIAGNOSTIC_COMPARATOR,
        )

        decision = build_evidence_decision(
            profiles,
            point_effects={
                ("SyntheticControl", "UnitJackKnife"): 0.05,
                ("AugSynthCVXPY", "Conformal"): 0.04,
                ("TBRRidge", "Conformal"): 0.03,
            },
        )
        assert decision.primary_readout is not None
        assert decision.primary_readout.inference == "UnitJackKnife"
        assert len(decision.diagnostic_comparators) >= 2
        assert decision.calibration_signal_action == CalibrationSignalAction.EXPORT_CALIBRATION_SIGNAL
        assert decision.mmm_action == MmmAction.EXCLUDE_FROM_MMM
        assert decision.mmm_status == MMM_DEFAULT_STATUS

    def test_a05_a18_a19_never_governed(self) -> None:
        design, data, geometry, estimand = _unit_panel_profiles()
        for est, inf, bucket in (
            ("AugSynthCVXPY", "Conformal", "characterized_restricted"),
            ("TBRRidge", "Conformal", "characterized_restricted"),
            ("TBRRidge", "TimeSeriesKfold", "characterized_restricted"),
        ):
            p = resolve_eligible_readout(
                CandidateReadout(
                    estimator_name=est,
                    inference_mode=inf,
                    audit_010_primary_bucket=bucket,
                    interval_readout=_valid_band_readout(estimator=est, inference=inf),
                ),
                design=design,
                data=data,
                geometry=geometry,
                estimand=estimand,
            )
            assert p.assigned_role == DecisionRole.DIAGNOSTIC_COMPARATOR
            assert p.is_governed_uncertainty is False
            assert p.calibration_signal_eligible is False

    def test_a16_a21_excluded_from_comparison_by_default(self) -> None:
        design, data, geometry, estimand = _unit_panel_profiles()
        for inf in ("UnitJackKnife", "JKP"):
            p = resolve_eligible_readout(
                CandidateReadout(
                    estimator_name="TBRRidge",
                    inference_mode=inf,
                    audit_010_primary_bucket="callable_unverified_interval_semantics",
                    interval_readout=_valid_band_readout(estimator="TBRRidge", inference=inf),
                ),
                design=design,
                data=data,
                geometry=geometry,
                estimand=estimand,
            )
            assert p.governance_bucket == "callable_unverified_interval_semantics"
            assert p.assigned_role == DecisionRole.EXCLUDED
            assert p.is_governed_uncertainty is False


class TestGeometryAndCatalogBlocks:
    def test_tbr_unit_panel_blocked(self) -> None:
        design, data, _, estimand = _unit_panel_profiles()
        geometry = GeometryProfile(geometry_type=GeometryType.UNIT_PANEL)
        p = resolve_eligible_readout(
            CandidateReadout(
                estimator_name="TBR",
                inference_mode="Kfold",
                interval_readout=_valid_band_readout(estimator="TBR", inference="Kfold"),
            ),
            design=design,
            data=data,
            geometry=geometry,
            estimand=estimand,
        )
        assert p.assigned_role == DecisionRole.BLOCKED
        assert "aggregate" in (p.exclusion_reason or "").lower() or p.geometry_status.startswith("blocked")

    def test_placebo_is_falsification_not_estimator(self) -> None:
        design, data, geometry, estimand = _unit_panel_profiles(n_treated=1)
        geometry = GeometryProfile(
            geometry_type=GeometryType.UNIT_PANEL,
            single_treated_geometry=True,
        )
        p = resolve_eligible_readout(
            CandidateReadout(
                estimator_name="SyntheticControl",
                inference_mode="Placebo",
                callable=True,
            ),
            design=design,
            data=DataProfile(n_treated=1, n_control=8, n_test_grps=1),
            geometry=geometry,
            estimand=estimand,
        )
        assert p.assigned_role == DecisionRole.FALSIFICATION_CHECK
        assert p.catalog_status == "inference_falsification_layer"

    def test_pooled_multi_cell_blocked_without_pooling_rule(self) -> None:
        design = DesignProfile(pooling_rule_id=None)
        data = DataProfile(n_treated=2, n_control=8, n_test_grps=2)
        geometry = GeometryProfile(geometry_type=GeometryType.POOLED_MULTI_CELL, pooled_claim=True)
        p = resolve_eligible_readout(
            CandidateReadout(
                estimator_name="TBRRidge",
                inference_mode="Kfold",
            ),
            design=design,
            data=data,
            geometry=geometry,
            estimand=EstimandProfile(),
        )
        assert p.assigned_role == DecisionRole.BLOCKED

    def test_supergeo_blocked_without_adapter(self) -> None:
        p = resolve_eligible_readout(
            CandidateReadout(
                estimator_name="SyntheticControl",
                inference_mode="UnitJackKnife",
            ),
            design=DesignProfile(),
            data=DataProfile(),
            geometry=GeometryProfile(geometry_type=GeometryType.SUPERGEO_UNIT),
            estimand=EstimandProfile(),
        )
        assert p.assigned_role == DecisionRole.BLOCKED

    def test_trim_blocked_without_estimand_bridge(self) -> None:
        p = resolve_eligible_readout(
            CandidateReadout(
                estimator_name="SyntheticControl",
                inference_mode="UnitJackKnife",
            ),
            design=DesignProfile(),
            data=DataProfile(),
            geometry=GeometryProfile(geometry_type=GeometryType.TRIMMED_POPULATION),
            estimand=EstimandProfile(),
        )
        assert p.assigned_role == DecisionRole.BLOCKED


class TestEvidenceComparison:
    def test_conflicting_directions_emit_warning_no_averaging(self) -> None:
        design, data, geometry, estimand = _unit_panel_profiles()
        profiles = resolve_eligible_readouts(
            [
                CandidateReadout(
                    estimator_name="SyntheticControl",
                    inference_mode="UnitJackKnife",
                    interval_readout=_valid_band_readout(
                        estimator="SyntheticControl", inference="UnitJackKnife"
                    ),
                    track_b_config_alias="SCM_UnitJackKnife",
                ),
                CandidateReadout(
                    estimator_name="TBRRidge",
                    inference_mode="Conformal",
                    audit_010_primary_bucket="characterized_restricted",
                    interval_readout=_valid_band_readout(
                        estimator="TBRRidge", inference="Conformal"
                    ),
                ),
            ],
            design=design,
            data=data,
            geometry=geometry,
            estimand=estimand,
        )
        decision = build_evidence_decision(
            profiles,
            point_effects={
                ("SyntheticControl", "UnitJackKnife"): 0.10,
                ("TBRRidge", "Conformal"): -0.08,
            },
        )
        assert decision.agreement_status == AgreementStatus.DIAGNOSTIC_DISAGREEMENT
        assert decision.trust_report_action == TrustReportAction.EMIT_WARNING
        assert any("no silent averaging" in w.lower() for w in decision.required_warnings)

    def test_falsification_failure_blocks_posture(self) -> None:
        design, data, geometry, estimand = _unit_panel_profiles(n_treated=1)
        geometry = GeometryProfile(
            geometry_type=GeometryType.UNIT_PANEL,
            single_treated_geometry=True,
        )
        profiles = resolve_eligible_readouts(
            [
                CandidateReadout(
                    estimator_name="SyntheticControl",
                    inference_mode="UnitJackKnife",
                    interval_readout=_valid_band_readout(
                        estimator="SyntheticControl", inference="UnitJackKnife"
                    ),
                    track_b_config_alias="SCM_UnitJackKnife",
                ),
                CandidateReadout(
                    estimator_name="SyntheticControl",
                    inference_mode="Placebo",
                ),
            ],
            design=design,
            data=DataProfile(n_treated=1, n_control=8, n_test_grps=1),
            geometry=geometry,
            estimand=estimand,
        )
        decision = build_evidence_decision(
            profiles,
            point_effects={("SyntheticControl", "UnitJackKnife"): 0.05},
            falsification_outcomes={("SyntheticControl", "Placebo"): False},
        )
        assert decision.agreement_status == AgreementStatus.FALSIFICATION_FAILURE
        assert decision.final_decision_posture == DecisionPosture.BLOCKED_FOR_DECISION_USE

    def test_no_calibration_signal_except_scm_jk_path(self) -> None:
        design, data, geometry, estimand = _unit_panel_profiles()
        profiles = resolve_eligible_readouts(
            [
                CandidateReadout(
                    estimator_name="TBRRidge",
                    inference_mode="Conformal",
                    audit_010_primary_bucket="characterized_restricted",
                    interval_readout=_valid_band_readout(
                        estimator="TBRRidge", inference="Conformal"
                    ),
                ),
            ],
            design=design,
            data=data,
            geometry=geometry,
            estimand=estimand,
        )
        decision = build_evidence_decision(
            profiles,
            point_effects={("TBRRidge", "Conformal"): 0.02},
        )
        assert decision.calibration_signal_action != CalibrationSignalAction.EXPORT_CALIBRATION_SIGNAL
        assert decision.mmm_action == MmmAction.EXCLUDE_FROM_MMM
