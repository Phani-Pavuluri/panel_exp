"""Tests for readiness policy profiles (exploratory / standard / strict)."""

from __future__ import annotations

import copy

from panel_exp.artifacts.experiment_card import build_experiment_card
from panel_exp.evidence import DesignEvidence
from panel_exp.panel_data import TimePeriod
from panel_exp.policy.readiness import (
    EXPLORATORY_POLICY,
    STANDARD_POLICY,
    STRICT_POLICY,
    ReadinessProfile,
    ReadinessStatus,
    build_readiness_assessment,
    resolve_readiness_policy,
)
from panel_exp.spec import spec_from_geo_design
from panel_exp.validation.calibration_report import CalibrationReport


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


def test_exploratory_allows_unknown_interference():
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(intervals_available=False),
        interference_assumption="unknown",
        profile=ReadinessProfile.EXPLORATORY,
    )
    assert assessment.status == ReadinessStatus.READY_WITH_REVIEW
    assert assessment.profile_name == "exploratory"


def test_standard_rejects_unknown_interference():
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        interference_assumption="unknown",
        profile=ReadinessProfile.STANDARD,
    )
    assert assessment.status == ReadinessStatus.NOT_READY_INTERFERENCE_UNKNOWN


def test_exploratory_allows_no_intervals():
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(intervals_available=False),
        interference_assumption="no_interference",
        profile=ReadinessProfile.EXPLORATORY,
    )
    assert assessment.status != ReadinessStatus.NOT_READY_NO_INTERVALS


def test_strict_rejects_weaker_calibration_fpr():
    report = CalibrationReport(
        false_positive_rate=0.08,
        coverage_under_null=0.96,
        power=0.92,
        recovery_success_rate=0.96,
    )
    standard = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        calibration_report=report,
        interference_assumption="no_interference",
        profile=ReadinessProfile.STANDARD,
    )
    strict = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        calibration_report=report,
        interference_assumption="no_interference",
        profile=ReadinessProfile.STRICT,
    )
    assert standard.status == ReadinessStatus.READY_WITH_REVIEW
    assert strict.status == ReadinessStatus.NOT_READY_HIGH_FPR


def test_strict_rejects_weaker_calibration_coverage():
    report = CalibrationReport(
        false_positive_rate=0.03,
        coverage_under_null=0.92,
        power=0.92,
        recovery_success_rate=0.96,
    )
    strict = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        calibration_report=report,
        interference_assumption="no_interference",
        profile=ReadinessProfile.STRICT,
    )
    assert strict.status == ReadinessStatus.NOT_READY_LOW_COVERAGE


def test_strict_threshold_stricter_than_standard():
    assert STRICT_POLICY.max_false_positive_rate < STANDARD_POLICY.max_false_positive_rate
    assert STRICT_POLICY.min_coverage_under_null > STANDARD_POLICY.min_coverage_under_null
    assert STRICT_POLICY.min_power > STANDARD_POLICY.min_power


def test_default_profile_is_standard():
    config = resolve_readiness_policy(None)
    assert config.name == STANDARD_POLICY.name
    assessment = build_readiness_assessment(inference_metadata=_ready_meta())
    assert assessment.profile_name == "standard"


def test_threshold_metadata_populated():
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        profile=ReadinessProfile.STRICT,
    )
    payload = assessment.to_dict()
    assert payload["profile_name"] == "strict"
    assert payload["thresholds_used"]["max_false_positive_rate"] == 0.05
    assert payload["thresholds_used"]["minimum_recovery_success_rate"] == 0.95


def test_markdown_renders_profile():
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        profile=ReadinessProfile.STRICT,
    )
    md = assessment.to_markdown()
    assert "**Profile:** strict" in md
    assert "max_false_positive_rate" in md


def test_experiment_card_displays_profile():
    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
    )
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(),
        profile=ReadinessProfile.STRICT,
    )
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["a"], "test_0": ["b"]},
        artifacts={"readiness_assessment": assessment.to_dict()},
    )
    md = build_experiment_card(ev).to_markdown()
    assert "**Profile:** strict" in md


def test_exploratory_allows_research_only_maturity():
    assessment = build_readiness_assessment(
        inference_metadata=_ready_meta(
            estimator_maturity="research_only",
            inference_mode_maturity="expert_review",
        ),
        profile=ReadinessProfile.EXPLORATORY,
        interference_assumption="no_interference",
    )
    assert assessment.status != ReadinessStatus.NOT_READY_INSUFFICIENT_EVIDENCE


def test_input_objects_not_mutated():
    meta = _ready_meta()
    meta_copy = copy.deepcopy(meta)
    report = CalibrationReport(false_positive_rate=0.04, coverage_under_null=0.93)
    report_copy = copy.deepcopy(report.to_dict())
    build_readiness_assessment(
        inference_metadata=meta,
        calibration_report=report,
        profile=ReadinessProfile.STRICT,
    )
    assert meta == meta_copy
    assert report.to_dict() == report_copy


def test_custom_policy_config_constants():
    assert EXPLORATORY_POLICY.allow_unknown_interference is True
    assert STANDARD_POLICY.require_intervals is True
    assert STRICT_POLICY.minimum_recovery_success_rate == 0.95
