"""
Helpers for artifact schema compatibility tests.

Canonicalizes exported artifacts for deterministic comparison against fixtures.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, Mapping

from panel_exp.artifacts.experiment_card import CARD_VERSION, build_experiment_card
from panel_exp.artifacts.run_bundle import BUNDLE_VERSION, build_run_artifact_bundle
from panel_exp.evidence import DesignEvidence
from panel_exp.method_metadata import EstimatorMaturity, EstimatorMaturityEvidence
from panel_exp.panel_data import TimePeriod
from panel_exp.policy.readiness import ReadinessProfile, build_readiness_assessment
from panel_exp.spec import InterferenceAssumption, spec_from_geo_design
from panel_exp.validation.calibration_report import CalibrationReport

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "artifact_schemas"

# Fields stripped before schema snapshot comparison (non-deterministic or prose-heavy).
NONDETERMINISTIC_FIELDS = frozenset(
    {
        "created_at",
        "timestamp",
        "runtime_seconds",
        "package_version",
        "code_version",
        "experiment_card_markdown",
        "calibration_summary",
        "maturity_evidence_summary",
        "readiness_assessment_summary",
        "evidence_summary",
    }
)

FIXTURE_CREATED_AT = "2020-01-01T00:00:00+00:00"
FIXTURE_EXPERIMENT_ID = "schema-fixture-exp"


def canonicalize_artifact(obj: Any) -> Any:
    """
    Recursively canonicalize an artifact for schema comparison.

    - Sorts dict keys
    - Removes nondeterministic / prose-heavy fields (see ``NONDETERMINISTIC_FIELDS``)
    - Converts NaN / inf floats to ``None``
    - Preserves list order and schema version fields
    """
    if obj is None:
        return None
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, (int,)):
        return int(obj)
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    if isinstance(obj, Mapping):
        out: Dict[str, Any] = {}
        for key in sorted(obj.keys(), key=lambda k: str(k)):
            if key in NONDETERMINISTIC_FIELDS:
                continue
            out[str(key)] = canonicalize_artifact(obj[key])
        return out
    if isinstance(obj, (list, tuple)):
        return [canonicalize_artifact(v) for v in obj]
    return obj


def _fixture_spec():
    return spec_from_geo_design(
        FIXTURE_EXPERIMENT_ID,
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
        random_state=0,
        interference=InterferenceAssumption.NO_INTERFERENCE,
    )


def build_fixture_evidence() -> DesignEvidence:
    """Fixed design evidence for schema fixtures (seed 0, fixed timestamp)."""
    spec = _fixture_spec()
    return DesignEvidence.from_assignment(
        spec,
        {"control": ["u0", "u1"], "test_0": ["u2"]},
        validation_summary={"status": "PASS", "blocking_failures": []},
        inference_metadata={
            "estimator_maturity": "expert_review",
            "inference_mode_maturity": "expert_review",
            "estimator_name": "TBRRidge",
            "intervals_available": True,
            "path_interval_type": "confidence_interval",
        },
        warnings=["fixture-warning"],
        created_at=FIXTURE_CREATED_AT,
    )


def build_fixture_calibration_report() -> CalibrationReport:
    return CalibrationReport(
        false_positive_rate=0.05,
        coverage_under_null=0.92,
        power=0.81,
        recovery_success_rate=0.90,
        n_replications=10,
        null_replications=5,
        positive_replications=5,
        warnings=["cal-warn"],
    )


def build_fixture_maturity_evidence() -> EstimatorMaturityEvidence:
    return EstimatorMaturityEvidence(
        estimator_name="TBRRidge",
        maturity=EstimatorMaturity.EXPERT_REVIEW,
        synthetic_validation_available=True,
        scenarios_run=("recovery_null_effect",),
        calibration_available=True,
        false_positive_rate=0.05,
        coverage_under_null=0.92,
        power=0.81,
        recovery_success_rate=0.90,
    )


def build_fixture_readiness_assessment():
    ev = build_fixture_evidence()
    cal = build_fixture_calibration_report()
    mat = build_fixture_maturity_evidence()
    return build_readiness_assessment(
        inference_metadata=dict(ev.inference_metadata),
        calibration_report=cal,
        maturity_evidence=mat,
        interference_assumption="no_interference",
        profile=ReadinessProfile.STANDARD,
    )


def build_fixture_experiment_card():
    return build_experiment_card(build_fixture_evidence())


def build_fixture_run_bundle():
    ev = build_fixture_evidence()
    return build_run_artifact_bundle(
        evidence=ev,
        experiment_card=build_fixture_experiment_card(),
        calibration_report=build_fixture_calibration_report(),
        maturity_evidence=build_fixture_maturity_evidence(),
        readiness_assessment=build_fixture_readiness_assessment(),
        created_at=FIXTURE_CREATED_AT,
    )


def load_schema_fixture(name: str) -> Dict[str, Any]:
    """Load ``{name}.json`` from ``tests/fixtures/artifact_schemas/``."""
    import json

    path = FIXTURE_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def assert_schema_matches_fixture(
    actual: Any,
    fixture_name: str,
) -> None:
    """Compare canonicalized artifact to a committed schema fixture."""
    import json

    expected = load_schema_fixture(fixture_name)
    got = canonicalize_artifact(actual)
    assert got == expected, (
        f"Schema drift for {fixture_name}:\n"
        f"expected: {json.dumps(expected, indent=2, sort_keys=True)}\n"
        f"got: {json.dumps(got, indent=2, sort_keys=True)}"
    )


# Version contract constants (documented for reviewers).
EXPECTED_CARD_VERSION = CARD_VERSION
EXPECTED_BUNDLE_VERSION = BUNDLE_VERSION
