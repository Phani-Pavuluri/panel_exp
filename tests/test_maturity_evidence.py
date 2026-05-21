"""Tests for validation-backed maturity evidence (additive; no auto re-rating)."""

from __future__ import annotations

import copy
import math

import pytest

from panel_exp.artifacts.experiment_card import build_experiment_card
from panel_exp.evidence import DesignEvidence
from panel_exp.method_metadata import (
    EstimatorMaturity,
    EstimatorMaturityEvidence,
    EstimatorMetadata,
)
from panel_exp.method_registry import get_method_registry
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import spec_from_geo_design
from panel_exp.validation.calibration_report import build_calibration_report
from panel_exp.validation.maturity_evidence import (
    attach_maturity_evidence,
    build_maturity_evidence,
)


def _recovery_payloads_did() -> list:
    return [
        {
            "estimator": "DID",
            "scenario": "recovery_null_effect",
            "false_positive_rate": 0.04,
            "coverage": 0.93,
            "power": float("nan"),
            "recovery_success_rate": 0.91,
            "n_simulations": 5,
        },
        {
            "estimator": "DID",
            "scenario": "recovery_positive_effect",
            "false_positive_rate": float("nan"),
            "coverage": 0.90,
            "power": 0.81,
            "recovery_success_rate": 0.88,
            "n_simulations": 5,
        },
        {
            "estimator": "SCM",
            "scenario": "scm_low_signal",
            "false_positive_rate": 0.10,
            "coverage": 0.85,
            "power": 0.70,
            "recovery_success_rate": 0.80,
            "n_simulations": 3,
        },
    ]


def test_builds_without_calibration_or_recovery():
    meta = get_method_registry().metadata("TBRRidge")
    catalog_maturity = meta.maturity
    evidence = build_maturity_evidence("TBRRidge", meta)
    assert evidence.estimator_name == "TBRRidge"
    assert evidence.maturity == catalog_maturity
    assert evidence.calibration_available is False
    assert evidence.scenarios_run == ()
    assert "catalog policy" in evidence.evidence_summary.lower()
    assert evidence.maturity == EstimatorMaturity.EXPERT_REVIEW


def test_builds_with_calibration_report():
    recovery = _recovery_payloads_did()
    report = build_calibration_report(
        recovery_outputs=recovery, estimator="DID"
    )
    meta = get_method_registry().metadata("DID")
    evidence = build_maturity_evidence(
        "DID", meta, calibration_report=report
    )
    assert evidence.calibration_available is True
    assert evidence.false_positive_rate == pytest.approx(0.04)
    assert evidence.coverage_under_null == pytest.approx(0.93)
    assert evidence.power == pytest.approx(0.81)
    assert evidence.maturity == meta.maturity
    assert evidence.warnings == tuple(report.warnings)


def test_builds_with_recovery_outputs_only():
    recovery = _recovery_payloads_did()
    raw = copy.deepcopy(recovery)
    evidence = build_maturity_evidence(
        "DID",
        {"estimator_maturity": "expert_review", "estimator_synthetic_validation": True},
        recovery_outputs=recovery,
    )
    assert evidence.scenarios_run == (
        "recovery_null_effect",
        "recovery_positive_effect",
    )
    assert evidence.synthetic_validation_available is True
    assert evidence.false_positive_rate == pytest.approx(0.04)
    assert "recovery outputs" in evidence.evidence_summary.lower()
    assert raw == recovery


def test_warnings_propagate_from_calibration():
    recovery = _recovery_payloads_did()
    report = build_calibration_report(
        recovery_outputs=recovery, estimator="DID"
    )
    report_dict = report.to_dict()
    report_dict["warnings"] = list(report.warnings) + ["custom diagnostic"]
    from panel_exp.validation.calibration_report import CalibrationReport

    patched = CalibrationReport(**{
        k: report_dict[k]
        for k in CalibrationReport.__dataclass_fields__
    })
    evidence = build_maturity_evidence(
        "DID", calibration_report=patched
    )
    assert "custom diagnostic" in evidence.warnings


def test_maturity_rating_not_changed_by_evidence():
    meta = get_method_registry().metadata("SCM")
    catalog_maturity = meta.maturity
    recovery = _recovery_payloads_did()
    evidence = build_maturity_evidence(
        "SCM",
        meta,
        recovery_outputs=recovery,
        calibration_report=build_calibration_report(
            recovery_outputs=recovery, estimator="SCM"
        ),
    )
    assert evidence.maturity == catalog_maturity
    assert get_method_registry().metadata("SCM").maturity == catalog_maturity


def test_attach_helper_additive():
    results = {"y": [1.0], "inference_metadata": {"alpha": 0.05}}
    snapshot = copy.deepcopy(results)
    meta = get_method_registry().metadata("TBRRidge")
    evidence = build_maturity_evidence("TBRRidge", meta)
    attach_maturity_evidence(results, evidence)
    assert "maturity_evidence" in results
    assert results["maturity_evidence"]["estimator_name"] == "TBRRidge"
    assert results["maturity_evidence"]["maturity"] == "expert_review"
    assert snapshot["inference_metadata"] == results["inference_metadata"]
    assert "maturity_evidence" not in snapshot


def test_input_metadata_not_mutated():
    meta = get_method_registry().metadata("DID")
    meta_copy = EstimatorMetadata(
        name=meta.name,
        maturity=meta.maturity,
        rationale=meta.rationale,
        assumptions=meta.assumptions,
        class_name=meta.class_name,
        module_path=meta.module_path,
        synthetic_validation=meta.synthetic_validation,
        optional_dependencies=meta.optional_dependencies,
        inference_support=meta.inference_support,
        known_limitations=meta.known_limitations,
    )
    recovery = _recovery_payloads_did()
    recovery_copy = copy.deepcopy(recovery)
    report = build_calibration_report(recovery_outputs=recovery, estimator="DID")
    build_maturity_evidence(
        "DID",
        meta_copy,
        calibration_report=report,
        recovery_outputs=recovery,
    )
    assert meta_copy.maturity == meta.maturity
    assert recovery == recovery_copy


def test_experiment_card_renders_maturity_evidence_section():
    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
        estimator="DID",
    )
    meta = get_method_registry().metadata("DID")
    recovery = _recovery_payloads_did()
    me = build_maturity_evidence(
        "DID",
        meta,
        recovery_outputs=recovery,
        calibration_report=build_calibration_report(
            recovery_outputs=recovery, estimator="DID"
        ),
    )
    artifacts = {"maturity_evidence": me.to_dict()}
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["a"], "test_0": ["b"]},
        inference_metadata={"estimator_maturity": "expert_review"},
        artifacts=artifacts,
    )
    md = build_experiment_card(ev).to_markdown()
    assert "## Maturity Evidence" in md
    assert "recovery_null_effect" in md
    assert "False positive rate" in md
    assert "Catalog maturity (unchanged)" in md


def test_experiment_card_omits_section_when_absent():
    spec = spec_from_geo_design(
        "e2",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
    )
    ev = DesignEvidence.from_assignment(
        spec, {"control": ["a"], "test_0": ["b"]}
    )
    md = build_experiment_card(ev).to_markdown()
    assert "## Maturity Evidence" not in md


def test_estimator_maturity_evidence_to_dict_serializable():
    evidence = EstimatorMaturityEvidence(
        estimator_name="TBR",
        maturity=EstimatorMaturity.EXPERT_REVIEW,
        false_positive_rate=0.05,
    )
    payload = evidence.to_dict()
    assert payload["maturity"] == "expert_review"
    assert math.isnan(payload["coverage_under_null"])
