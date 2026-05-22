"""Tests for estimand and uncertainty prespecification contracts."""

from __future__ import annotations

import copy

import pytest

from panel_exp.artifacts.experiment_card import build_experiment_card
from panel_exp.design.validation import ValidationCheck, ValidationStatus
from panel_exp.evidence import (
    DesignEvidence,
    ExperimentEvidence,
    build_analysis_contract,
)
from panel_exp.inference_result import InferenceResult, IntervalType
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import (
    TargetEstimand,
    UncertaintyContract,
    spec_from_geo_design,
)


def _spec(**kwargs):
    defaults = dict(
        experiment_id="estimand-contract-1",
        outcome_column="y",
        unit_column="u",
        time_column="t",
        pre_period=TimePeriod(0, 10),
        experiment_period=TimePeriod(10, 30),
        design_method="balancedrandomization",
        random_state=3,
    )
    defaults.update(kwargs)
    return spec_from_geo_design(**defaults)


def _validation_summary() -> dict:
    check = ValidationCheck(
        metric="interference_assumption",
        status=ValidationStatus.PASS,
        threshold=None,
        value=None,
        message="Declared.",
        blocking=False,
    )
    return {"status": "PASS", "blocking_failures": [], "checks": [check.to_dict()]}


def test_design_spec_defaults_unknown():
    spec = _spec()
    assert spec.target_estimand == TargetEstimand.UNKNOWN
    assert spec.uncertainty_contract == UncertaintyContract.UNKNOWN


def test_explicit_spec_values_propagate_to_contract():
    spec = _spec(
        target_estimand=TargetEstimand.RELATIVE_ATT_POST,
        uncertainty_contract=UncertaintyContract.PLACEBO_BAND,
    )
    contract = build_analysis_contract(spec=spec)
    assert contract["target_estimand"] == "relative_att_post"
    assert contract["uncertainty_contract"] == "placebo_band"
    assert contract["target_estimand_label"] == "Relative post-period ATT"
    assert contract["uncertainty_contract_label"] == "Placebo band"
    assert not any("not explicitly declared" in n for n in contract["notes"])


def test_build_analysis_contract_infers_pooled_did():
    contract = build_analysis_contract(estimator_name="DID")
    assert contract["target_estimand"] == "pooled_att"
    assert "Effect interpretation not explicitly declared" not in " ".join(
        contract["notes"]
    )


def test_build_analysis_contract_infers_uncertainty_from_inference_result():
    ir = InferenceResult.for_path_intervals(
        method="UnitJackKnife",
        alpha=0.05,
        path_interval_type=IntervalType.CONFIDENCE_INTERVAL,
    )
    contract = build_analysis_contract(inference_result=ir)
    assert contract["uncertainty_contract"] == "confidence_interval"
    assert contract["uncertainty_contract_label"] == "Confidence interval"


def test_unknown_contract_emits_warnings():
    contract = build_analysis_contract()
    assert contract["target_estimand"] == "unknown"
    assert contract["uncertainty_contract"] == "unknown"
    assert any("Effect interpretation" in n for n in contract["notes"])
    assert any("Uncertainty interpretation" in n for n in contract["notes"])


def test_experiment_evidence_attaches_analysis_contract():
    spec = _spec(
        target_estimand=TargetEstimand.RELATIVE_ATT_POST,
        uncertainty_contract=UncertaintyContract.CONFIDENCE_INTERVAL,
    )
    ir = InferenceResult.for_path_intervals(
        method="UnitJackKnife",
        alpha=0.05,
        path_interval_type=IntervalType.CONFIDENCE_INTERVAL,
    )
    ev = ExperimentEvidence.build(
        spec,
        {"control": ["u0"], "test_0": ["u1"]},
        validation_summary=_validation_summary(),
        inference_result=ir,
        inference_method="UnitJackKnife",
        created_at="2026-05-20T12:00:00+00:00",
    )
    ac = dict(ev.inference_metadata)["analysis_contract"]
    assert ac["target_estimand"] == "relative_att_post"
    assert ac["uncertainty_contract"] == "confidence_interval"


def test_card_renders_estimand_contract_section():
    spec = _spec(
        target_estimand=TargetEstimand.RELATIVE_ATT_POST,
        uncertainty_contract=UncertaintyContract.PLACEBO_BAND,
    )
    ev = ExperimentEvidence.build(
        spec,
        {"control": ["u0"], "test_0": ["u1"]},
        validation_summary=_validation_summary(),
        created_at="2026-05-20T12:00:00+00:00",
    )
    md = build_experiment_card(ev).to_markdown()
    assert "## Estimand and Uncertainty Contract" in md
    assert "Target estimand:" in md
    assert "Relative post-period ATT" in md
    assert "Uncertainty:" in md
    assert "Placebo band" in md


def test_card_warns_when_estimand_unknown():
    spec = _spec()
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["u0"], "test_0": ["u1"]},
        validation_summary=_validation_summary(),
        created_at="2026-05-20T12:00:00+00:00",
    )
    card = build_experiment_card(ev)
    assert card.target_estimand_label != ""
    md = card.to_markdown()
    assert "Warning:" in md
    assert "Effect interpretation not explicitly declared" in md


def test_old_spec_constructor_without_new_fields_still_works():
    spec = _spec()
    payload = spec.content_hash()
    assert isinstance(payload, str) and len(payload) > 8


def test_input_objects_not_mutated():
    spec = _spec()
    assignment = {"control": ["u0"], "test_0": ["u1"]}
    assignment_copy = copy.deepcopy(assignment)
    spec_assumptions_copy = dict(spec.assumptions)
    ir = InferenceResult.for_path_intervals(
        method="Placebo",
        alpha=0.05,
        path_interval_type=IntervalType.PLACEBO_BAND,
    )
    meta_before = ir.to_dict()
    ev_before = ExperimentEvidence.build(
        spec,
        assignment,
        validation_summary=_validation_summary(),
        inference_result=ir,
        created_at="2026-05-20T12:00:00+00:00",
    )
    meta_snapshot = dict(ev_before.inference_metadata)
    build_analysis_contract(spec=spec, inference_result=ir)
    assert assignment == assignment_copy
    assert dict(spec.assumptions) == spec_assumptions_copy
    assert ir.to_dict() == meta_before
    assert dict(ev_before.inference_metadata) == meta_snapshot


@pytest.mark.parametrize(
    "interval_type,expected_contract",
    [
        (IntervalType.PLACEBO_BAND, "placebo_band"),
        (IntervalType.CREDIBLE_INTERVAL, "credible_interval"),
        (IntervalType.CONFORMAL_INTERVAL, "conformal_interval"),
        (IntervalType.UNAVAILABLE, "none"),
    ],
)
def test_interval_type_maps_to_uncertainty_contract(interval_type, expected_contract):
    ir = InferenceResult.for_path_intervals(
        method="test",
        alpha=0.05,
        path_interval_type=interval_type,
    )
    contract = build_analysis_contract(inference_result=ir)
    assert contract["uncertainty_contract"] == expected_contract
