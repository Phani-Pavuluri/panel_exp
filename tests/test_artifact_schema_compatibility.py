"""
Artifact schema compatibility contracts.

Compares canonicalized exports against committed fixtures. A major version bump
is required when removing, renaming, or changing field semantics — not for
additive optional fields.

See ``tests/fixtures/artifact_schemas/`` and ``tests/artifact_test_helpers.py``.
"""

from __future__ import annotations

import json

from panel_exp.evidence import DesignEvidence
from panel_exp.policy.readiness import ReadinessAssessment, ReadinessStatus
from tests.artifact_test_helpers import (
    EXPECTED_BUNDLE_VERSION,
    EXPECTED_CARD_VERSION,
    assert_schema_matches_fixture,
    build_fixture_calibration_report,
    build_fixture_evidence,
    build_fixture_experiment_card,
    build_fixture_maturity_evidence,
    build_fixture_readiness_assessment,
    build_fixture_run_bundle,
    canonicalize_artifact,
    load_schema_fixture,
)


# ---------------------------------------------------------------------------
# Schema stability (shape + stable fields; timestamps stripped)
# ---------------------------------------------------------------------------


def test_experiment_card_schema_stable():
    card = build_fixture_experiment_card()
    assert_schema_matches_fixture(card.to_dict(), "experiment_card_v1")


def test_calibration_report_schema_stable():
    report = build_fixture_calibration_report()
    assert_schema_matches_fixture(report.to_dict(), "calibration_report_v1")


def test_maturity_evidence_schema_stable():
    maturity = build_fixture_maturity_evidence()
    assert_schema_matches_fixture(maturity.to_dict(), "maturity_evidence_v1")


def test_readiness_schema_stable():
    assessment = build_fixture_readiness_assessment()
    assert_schema_matches_fixture(assessment.to_dict(), "readiness_assessment_v1")


def test_run_bundle_schema_stable():
    bundle = build_fixture_run_bundle()
    assert_schema_matches_fixture(bundle.to_dict(), "run_bundle_v1")


# ---------------------------------------------------------------------------
# Version contracts
# ---------------------------------------------------------------------------


def test_bundle_version_contract():
    """``bundle_version`` must exist; bump major on breaking bundle schema changes."""
    bundle = build_fixture_run_bundle()
    payload = bundle.to_dict()
    assert payload["bundle_version"] == EXPECTED_BUNDLE_VERSION
    fixture = load_schema_fixture("run_bundle_v1")
    assert fixture["bundle_version"] == EXPECTED_BUNDLE_VERSION


def test_card_version_contract():
    """``card_version`` must exist; bump major on breaking card schema changes."""
    card = build_fixture_experiment_card()
    payload = card.to_dict()
    assert payload["card_version"] == EXPECTED_CARD_VERSION
    fixture = load_schema_fixture("experiment_card_v1")
    assert fixture["card_version"] == EXPECTED_CARD_VERSION


# ---------------------------------------------------------------------------
# Forward compatibility (unknown / missing optional fields)
# ---------------------------------------------------------------------------


def test_evidence_unknown_fields_do_not_break_from_dict():
    data = build_fixture_evidence().to_dict()
    data["unknown_future_field"] = "allowed_extra"
    restored = DesignEvidence.from_dict(data)
    assert restored.experiment_id == "schema-fixture-exp"
    assert restored.spec_hash == data["spec_hash"]


def test_readiness_missing_warnings_does_not_crash():
    assessment = build_fixture_readiness_assessment()
    payload = assessment.to_dict()
    payload.pop("warnings", None)
    # Reconstruct as experiment_card does for markdown export
    ReadinessAssessment(
        status=ReadinessStatus(payload["status"]),
        reasons=tuple(payload.get("reasons") or ()),
        warnings=tuple(payload.get("warnings") or ()),
        recommended_actions=tuple(payload.get("recommended_actions") or ()),
        inputs_used=tuple(payload.get("inputs_used") or ()),
        profile_name=str(payload.get("profile_name") or "standard"),
        thresholds_used=tuple((payload.get("thresholds_used") or {}).items()),
    )


def test_calibration_report_missing_warnings_does_not_crash():
    report = build_fixture_calibration_report()
    data = report.to_dict()
    data.pop("warnings", None)
    from panel_exp.validation.calibration_report import CalibrationReport

    filtered = {
        k: data[k]
        for k in CalibrationReport.__dataclass_fields__
        if k in data
    }
    CalibrationReport(**filtered)


def test_run_bundle_unknown_nested_fields_canonicalize():
    bundle = build_fixture_run_bundle()
    data = bundle.to_dict()
    data["future_top_level"] = {"nested": True}
    data["readiness_assessment"]["future_readiness_field"] = 1
    canonical = canonicalize_artifact(data)
    assert "future_top_level" in canonical
    assert canonical["future_top_level"]["nested"] is True


def test_build_run_bundle_with_minimal_readiness_dict():
    from panel_exp.artifacts import build_run_artifact_bundle

    minimal = {
        "status": "ready_with_review",
        "profile_name": "standard",
        "thresholds_used": {},
    }
    bundle = build_run_artifact_bundle(
        evidence=build_fixture_evidence(),
        readiness_assessment=minimal,
        created_at="2020-01-01T00:00:00+00:00",
    )
    assert bundle.readiness_assessment is not None
    assert bundle.readiness_assessment["status"] == "ready_with_review"


def test_canonicalize_strips_nondeterministic_fields():
    payload = {
        "created_at": "2026-05-20T12:00:00+00:00",
        "timestamp": "2026-05-20T12:00:00+00:00",
        "runtime_seconds": 1.5,
        "stable": "yes",
    }
    assert canonicalize_artifact(payload) == {"stable": "yes"}


def test_canonicalize_nan_to_null():
    payload = {"false_positive_rate": float("nan"), "power": 0.8}
    assert canonicalize_artifact(payload) == {
        "false_positive_rate": None,
        "power": 0.8,
    }


def test_fixture_evidence_hashes_stable_across_runs():
    h1 = build_fixture_evidence().spec_hash
    h2 = build_fixture_evidence().spec_hash
    assert h1 == h2


def test_schema_fixtures_are_valid_json_objects():
    for name in (
        "experiment_card_v1",
        "calibration_report_v1",
        "maturity_evidence_v1",
        "readiness_assessment_v1",
        "run_bundle_v1",
    ):
        data = load_schema_fixture(name)
        assert isinstance(data, dict)
        json.dumps(data)
