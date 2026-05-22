"""Tests for portable run artifact bundle export."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from panel_exp.artifacts import (
    build_experiment_card,
    build_run_artifact_bundle,
    write_run_artifact_bundle_json,
    write_run_artifact_bundle_markdown,
)
from panel_exp.evidence import DesignEvidence
from panel_exp.method_metadata import EstimatorMaturity, EstimatorMaturityEvidence
from panel_exp.panel_data import TimePeriod
from panel_exp.policy.readiness import ReadinessProfile, build_readiness_assessment
from panel_exp.spec import spec_from_geo_design
from panel_exp.validation.calibration_report import CalibrationReport


def _spec():
    return spec_from_geo_design(
        "bundle-test-1",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
    )


def _evidence(**kwargs):
    spec = _spec()
    defaults = dict(
        validation_summary={"status": "PASS"},
        warnings=["design warn"],
        errors=[],
        created_at="2026-05-20T12:00:00+00:00",
    )
    defaults.update(kwargs)
    return DesignEvidence.from_assignment(
        spec,
        {"control": ["a", "b"], "test_0": ["c"]},
        **defaults,
    )


def test_builds_with_evidence_only():
    ev = _evidence()
    bundle = build_run_artifact_bundle(evidence=ev, created_at="2026-05-20T12:00:00+00:00")
    assert bundle.bundle_version == "1.0"
    assert bundle.experiment_id == "bundle-test-1"
    assert bundle.evidence is not None
    assert bundle.evidence["spec_hash"] == ev.spec_hash
    assert bundle.experiment_card is None
    assert bundle.calibration_report is None


def test_builds_with_all_components():
    ev = _evidence()
    card = build_experiment_card(ev)
    calibration = CalibrationReport(
        false_positive_rate=0.05,
        coverage_under_null=0.93,
        power=0.82,
    )
    maturity = EstimatorMaturityEvidence(
        estimator_name="TBRRidge",
        maturity=EstimatorMaturity.EXPERT_REVIEW,
        false_positive_rate=0.05,
        coverage_under_null=0.93,
    )
    readiness = build_readiness_assessment(
        inference_metadata={"estimator_maturity": "expert_review", "intervals_available": True},
        calibration_report=calibration,
        interference_assumption="no_interference",
        profile=ReadinessProfile.STANDARD,
    )
    bundle = build_run_artifact_bundle(
        evidence=ev,
        experiment_card=card,
        calibration_report=calibration,
        maturity_evidence=maturity,
        readiness_assessment=readiness,
        warnings=["extra warn"],
        errors=["extra err"],
        created_at="2026-05-20T12:00:00+00:00",
    )
    assert bundle.experiment_card is not None
    assert bundle.calibration_report is not None
    assert bundle.maturity_evidence is not None
    assert bundle.readiness_assessment is not None
    assert "extra warn" in bundle.warnings
    assert "design warn" in bundle.warnings
    assert bundle.errors == ("extra err",)
    assert bundle.experiment_card_markdown
    assert "# Experiment Card" in bundle.experiment_card_markdown


def test_missing_optional_components_do_not_crash():
    bundle = build_run_artifact_bundle()
    assert bundle.evidence is None
    assert bundle.experiment_card is None
    assert bundle.calibration_report is None
    assert bundle.maturity_evidence is None
    assert bundle.readiness_assessment is None


def test_to_json_round_trips():
    ev = _evidence()
    bundle = build_run_artifact_bundle(
        evidence=ev,
        created_at="2026-05-20T12:00:00+00:00",
    )
    payload = json.loads(bundle.to_json())
    assert payload["bundle_version"] == "1.0"
    assert payload["experiment_id"] == "bundle-test-1"
    assert payload["evidence"]["assignment_hash"] == ev.assignment_hash


def test_to_markdown_renders_key_sections():
    ev = _evidence()
    card = build_experiment_card(ev)
    readiness = build_readiness_assessment(
        inference_metadata={"estimator_maturity": "expert_review", "intervals_available": True},
        interference_assumption="no_interference",
    )
    bundle = build_run_artifact_bundle(
        evidence=ev,
        experiment_card=card,
        readiness_assessment=readiness,
        created_at="2026-05-20T12:00:00+00:00",
    )
    md = bundle.to_markdown()
    assert "# Run Artifact Bundle" in md
    assert "# Experiment Card" in md
    assert "Decision Readiness" in md
    assert "design warn" in md


def test_write_json_and_markdown_create_files(tmp_path: Path):
    ev = _evidence()
    bundle = build_run_artifact_bundle(
        evidence=ev,
        created_at="2026-05-20T12:00:00+00:00",
    )
    json_path = tmp_path / "nested" / "run_bundle.json"
    md_path = tmp_path / "nested" / "run_bundle.md"
    write_run_artifact_bundle_json(bundle, json_path)
    write_run_artifact_bundle_markdown(bundle, md_path)
    assert json_path.is_file()
    assert md_path.is_file()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["experiment_id"] == "bundle-test-1"
    assert "# Run Artifact Bundle" in md_path.read_text(encoding="utf-8")


def test_input_objects_not_mutated():
    ev = _evidence()
    ev_copy = copy.deepcopy(ev.to_dict())
    cal = CalibrationReport(false_positive_rate=0.04)
    cal_copy = cal.to_dict()
    build_run_artifact_bundle(
        evidence=ev,
        calibration_report=cal,
        warnings=["w"],
        created_at="2026-05-20T12:00:00+00:00",
    )
    assert ev.to_dict() == ev_copy
    assert cal.to_dict() == cal_copy


def test_lineage_includes_hashes_when_evidence_present():
    ev = _evidence()
    bundle = build_run_artifact_bundle(
        evidence=ev,
        created_at="2026-05-20T12:00:00+00:00",
    )
    assert bundle.lineage["spec_hash"] == ev.spec_hash
    assert bundle.lineage["assignment_hash"] == ev.assignment_hash
    assert bundle.lineage["evidence_version"] == ev.evidence_version
    assert bundle.lineage["package_version"] == ev.package_version


def test_deterministic_except_created_at():
    ev = _evidence()
    b1 = build_run_artifact_bundle(evidence=ev, created_at="FIXED")
    b2 = build_run_artifact_bundle(evidence=ev, created_at="FIXED")
    d1 = b1.to_dict()
    d2 = b2.to_dict()
    assert d1 == d2
    b3 = build_run_artifact_bundle(evidence=ev, created_at="OTHER")
    assert b3.to_dict()["created_at"] == "OTHER"
    assert b3.to_dict()["evidence"] == d1["evidence"]


def test_warnings_errors_propagate():
    ev = _evidence(warnings=["a"], errors=["e1"])
    bundle = build_run_artifact_bundle(
        evidence=ev,
        warnings=["b"],
        errors=["e2"],
        created_at="2026-05-20T12:00:00+00:00",
    )
    assert bundle.warnings == ("a", "b")
    assert bundle.errors == ("e1", "e2")


def test_run_artifact_bundle_to_dict_ordered_keys():
    bundle = build_run_artifact_bundle(created_at="T")
    keys = list(bundle.to_dict().keys())
    assert keys[0] == "bundle_version"
    assert "lineage" in keys
    assert keys.index("evidence") < keys.index("readiness_assessment")
