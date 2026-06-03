"""TRUSTREPORT-DECISION-INPUTS-WIRING-001 — bundle → TrustReportDecisionInputs wiring."""

from __future__ import annotations

import copy

import pytest

from panel_exp.artifacts.geo_run_export import export_geo_run_bundle
from panel_exp.track_b.readout_evidence_wiring import (
    build_trust_report_decision_inputs_from_bundle,
    extract_readout_evidence_from_bundle,
)
from tests.track_b.contract_fixtures import iter_all_fixture_cases
from tests.track_b.test_m2_1_representative_bundles import _load_rep_cases


def _rep(case_id: str) -> dict:
    for r in _load_rep_cases():
        if r["case_id"] == case_id:
            return r
    raise KeyError(case_id)


def _gold(case_id: str):
    for case in iter_all_fixture_cases():
        if case.fixture_id == case_id and case.variant_id is None:
            return case
    raise KeyError(case_id)


def _scenarios(case) -> list:
    return list(case.trust_report_expected_output.get("scenarios") or [])


class TestReadoutEvidenceExtraction:
    def test_rep_001_primary_from_config_alias(self) -> None:
        specs, warnings = extract_readout_evidence_from_bundle(_rep("REP-001")["bundle"])
        assert len(specs) >= 1
        assert specs[0]["track_b_config_alias"] == "SCM_UnitJackKnife"
        assert specs[0]["estimator_name"] == "SCM"
        assert specs[0]["inference_mode"] == "UnitJackKnife"

    def test_rep_002_estimator_inference_from_metadata(self) -> None:
        specs, _ = extract_readout_evidence_from_bundle(_rep("REP-002")["bundle"])
        assert any(s["estimator_name"] == "TBRRidge" and s["inference_mode"] == "Kfold" for s in specs)

    def test_rep_003_unmapped_pair_incomplete_warning(self) -> None:
        specs, warnings = extract_readout_evidence_from_bundle(_rep("REP-003")["bundle"])
        assert len(specs) == 1
        assert specs[0]["estimator_name"] == "TBR"
        assert any("decision_context_incomplete" in w for w in warnings)

    def test_explicit_readout_evidence_list(self) -> None:
        bundle = copy.deepcopy(_rep("REP-001")["bundle"])
        bundle["evidence"]["track_b_export_hints"]["readout_evidence"] = [
            {
                "estimator_name": "SyntheticControl",
                "inference_mode": "UnitJackKnife",
                "track_b_config_alias": "SCM_UnitJackKnife",
                "point_effect": 0.05,
            },
            {
                "estimator_name": "AugSynthCVXPY",
                "inference_mode": "Conformal",
                "audit_010_primary_bucket": "characterized_restricted",
                "point_effect": 0.04,
            },
        ]
        specs, _ = extract_readout_evidence_from_bundle(bundle)
        assert len(specs) == 2
        infs = {s["inference_mode"] for s in specs}
        assert "UnitJackKnife" in infs
        assert "Conformal" in infs


class TestRepresentativeExportDecisionContext:
    def test_opt_in_includes_f_decision_context(self) -> None:
        rep = _rep("REP-001")
        scenarios = [
            {
                "scenario_id": "null_viability",
                "intended_use": "null_screen",
                "claim_type": "null_viability",
            }
        ]
        bundle = export_geo_run_bundle(
            evidence=rep["bundle"]["evidence"],
            include_track_b_views=True,
            include_trust_report=True,
            include_trust_report_decision_context=True,
            trust_report_scenarios=scenarios,
        )
        view = bundle.to_dict()["track_b_views"]["trust_report_view"]
        assert "f_decision_context" in view
        fdc = view["f_decision_context"]
        assert fdc["primary_readout"] is not None
        assert fdc["primary_readout"]["assigned_role"] == "primary_null_monitor"
        assert fdc["promotion_candidates"] == []
        assert fdc["mmm_action"] == "exclude_from_mmm"

    def test_default_off_omits_f_decision_context(self) -> None:
        rep = _rep("REP-001")
        scenarios = [
            {
                "scenario_id": "null_viability",
                "intended_use": "null_screen",
                "claim_type": "null_viability",
            }
        ]
        bundle = export_geo_run_bundle(
            evidence=rep["bundle"]["evidence"],
            include_track_b_views=True,
            include_trust_report=True,
            trust_report_scenarios=scenarios,
        )
        view = bundle.to_dict()["track_b_views"]["trust_report_view"]
        assert "f_decision_context" not in view

    def test_decision_context_off_when_trust_report_off(self) -> None:
        rep = _rep("REP-001")
        bundle = export_geo_run_bundle(
            evidence=rep["bundle"]["evidence"],
            include_track_b_views=True,
            include_trust_report=False,
            include_trust_report_decision_context=True,
        )
        views = bundle.to_dict()["track_b_views"]
        assert "trust_report_view" not in views

    def test_incomplete_metadata_warning_on_blocked_bundle(self) -> None:
        rep = _rep("REP-003")
        scenarios = [{"scenario_id": "s1", "claim_type": "null_viability"}]
        bundle = export_geo_run_bundle(
            evidence=rep["bundle"]["evidence"],
            include_track_b_views=True,
            include_trust_report=True,
            include_trust_report_decision_context=True,
            trust_report_scenarios=scenarios,
        )
        views = bundle.to_dict()["track_b_views"]
        if views.get("trust_report_present"):
            fdc = views["trust_report_view"].get("f_decision_context")
            assert fdc is not None
            assert any(
                "decision_context_incomplete" in w for w in fdc["required_warnings"]
            )

    def test_multi_readout_diagnostic_roles(self) -> None:
        rep = copy.deepcopy(_rep("REP-001"))
        hints = rep["bundle"]["evidence"]["track_b_export_hints"]
        hints["readout_evidence"] = [
            {
                "estimator_name": "SyntheticControl",
                "inference_mode": "UnitJackKnife",
                "track_b_config_alias": "SCM_UnitJackKnife",
                "point_effect": 0.05,
            },
            {
                "estimator_name": "AugSynthCVXPY",
                "inference_mode": "Conformal",
                "audit_010_primary_bucket": "characterized_restricted",
                "point_effect": 0.04,
            },
            {
                "estimator_name": "TBRRidge",
                "inference_mode": "Conformal",
                "audit_010_primary_bucket": "characterized_restricted",
                "point_effect": 0.03,
            },
        ]
        inputs = build_trust_report_decision_inputs_from_bundle(rep["bundle"])
        from panel_exp.track_b.f_decision_context import build_trust_report_f_decision_context

        ctx = build_trust_report_f_decision_context(inputs)
        roles = {
            p["inference"]: p["assigned_role"] for p in ctx.eligible_readout_profiles
        }
        assert roles["UnitJackKnife"] == "primary_null_monitor"
        assert roles["Conformal"] == "diagnostic_comparator"


class TestGoldFixtureShimPath:
    def test_gold_001_spec_stub_export_with_decision_context(self) -> None:
        case = _gold("GOLD-001")
        bundle = export_geo_run_bundle(
            evidence={"experiment_id": "gold-wiring", "inference_metadata": {}},
            include_track_b_views=True,
            include_trust_report=True,
            include_trust_report_decision_context=True,
            trust_report_scenarios=_scenarios(case),
            track_b_spec=case.spec,
            track_b_run_stub=case.run_artifacts_stub,
            track_b_calibration_binding=case.calibration_signal_binding,
        )
        view = bundle.to_dict()["track_b_views"]["trust_report_view"]
        assert "f_decision_context" in view
        assert view["f_decision_context"]["primary_readout"] is not None
