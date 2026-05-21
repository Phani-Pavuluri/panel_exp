"""Tests for non-blocking decision readiness policy."""

from __future__ import annotations

import copy

from panel_exp.artifacts.experiment_card import build_experiment_card
from panel_exp.evidence import DesignEvidence
from panel_exp.panel_data import TimePeriod
from panel_exp.policy.readiness import (
    ReadinessAssessment,
    ReadinessStatus,
    attach_readiness_assessment,
    build_readiness_assessment,
)
from panel_exp.spec import InterferenceAssumption, spec_from_geo_design
from panel_exp.validation.calibration_report import (
    MAX_FALSE_POSITIVE_RATE,
    MIN_COVERAGE_UNDER_NULL,
    CalibrationReport,
)


def _ready_meta(**overrides) -> dict:
    base = {
        "estimator_maturity": "expert_review",
        "inference_mode_maturity": "expert_review",
        "intervals_available": True,
        "path_interval_type": "confidence_interval",
        "interference_assumption": "no_interference",
    }
    base.update(overrides)
    return base


def test_validation_errors_dominate():
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        validation_summary={"status": "FAIL", "blocking_failures": ["overlap"]},
        evidence_errors=["blocking gate failed"],
    )
    assert assessment.status == ReadinessStatus.NOT_READY_VALIDATION_ERRORS
    assert any("overlap" in r for r in assessment.reasons)


def test_no_intervals_status():
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(intervals_available=False),
    )
    assert assessment.status == ReadinessStatus.NOT_READY_NO_INTERVALS


def test_research_only_maturity_status():
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(
            estimator_maturity="research_only",
            inference_mode_maturity="expert_review",
        ),
    )
    assert assessment.status == ReadinessStatus.NOT_READY_INSUFFICIENT_EVIDENCE


def test_high_fpr_status():
    report = CalibrationReport(
        false_positive_rate=MAX_FALSE_POSITIVE_RATE + 0.05,
        coverage_under_null=0.95,
    )
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        calibration_report=report,
        interference_assumption="no_interference",
    )
    assert assessment.status == ReadinessStatus.NOT_READY_HIGH_FPR


def test_low_coverage_status():
    report = CalibrationReport(
        false_positive_rate=0.05,
        coverage_under_null=MIN_COVERAGE_UNDER_NULL - 0.05,
    )
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        calibration_report=report,
        interference_assumption="no_interference",
    )
    assert assessment.status == ReadinessStatus.NOT_READY_LOW_COVERAGE


def test_unknown_interference_status():
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        interference_assumption="unknown",
    )
    assert assessment.status == ReadinessStatus.NOT_READY_INTERFERENCE_UNKNOWN


def test_ready_with_review_status():
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        calibration_report=CalibrationReport(
            false_positive_rate=0.05,
            coverage_under_null=0.92,
        ),
        interference_assumption="no_interference",
    )
    assert assessment.status == ReadinessStatus.READY_WITH_REVIEW
    assert assessment.recommended_actions


def test_attach_helper_additive():
    results = {"y": [1.0], "inference_metadata": {"alpha": 0.05}}
    snapshot = copy.deepcopy(results)
    assessment = build_readiness_assessment(inference_metadata=_ready_meta())
    attach_readiness_assessment(results, assessment)
    assert results["readiness_assessment"]["status"] == assessment.status.value
    assert "readiness_assessment" not in snapshot


def test_markdown_renders_advisory_notice():
    assessment = build_readiness_assessment(inference_metadata=_ready_meta())
    md = assessment.to_markdown()
    assert "## Decision Readiness" in md
    assert "Advisory only" in md
    assert "does not block" in md


def test_experiment_card_displays_readiness_section():
    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
        interference=InterferenceAssumption.NO_INTERFERENCE,
    )
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        interference_assumption="no_interference",
    )
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["a"], "test_0": ["b"]},
        inference_metadata=_ready_meta(),
        artifacts={"readiness_assessment": assessment.to_dict()},
    )
    md = build_experiment_card(ev).to_markdown()
    assert "## Decision Readiness" in md
    assert "ready_with_review" in md


def test_experiment_card_omits_readiness_when_absent():
    spec = spec_from_geo_design(
        "e2",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
    )
    ev = DesignEvidence.from_assignment(spec, {"control": ["a"], "test_0": ["b"]})
    md = build_experiment_card(ev).to_markdown()
    assert "## Decision Readiness" not in md


def test_input_dicts_not_mutated():
    meta = _ready_meta()
    meta_copy = copy.deepcopy(meta)
    validation = {"status": "PASS", "checks": []}
    val_copy = copy.deepcopy(validation)
    report = CalibrationReport(false_positive_rate=0.04, coverage_under_null=0.93)
    build_readiness_assessment(
        inference_metadata=meta,
        validation_summary=validation,
        calibration_report=report,
        evidence_warnings=["warn"],
        evidence_errors=[],
        interference_assumption="no_interference",
    )
    assert meta == meta_copy
    assert validation == val_copy


def test_to_dict_roundtrip():
    assessment = ReadinessAssessment(
        status=ReadinessStatus.NOT_READY_HIGH_FPR,
        reasons=("high fpr",),
        warnings=("w",),
        recommended_actions=("review",),
        inputs_used=("calibration_report",),
    )
    payload = assessment.to_dict()
    assert payload["status"] == "not_ready_high_fpr"
    assert payload["status_label"]
