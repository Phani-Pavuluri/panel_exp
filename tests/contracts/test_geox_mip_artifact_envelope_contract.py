from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).parents[2] / "panel_exp/contracts/geox_mip_artifact_envelope.py"
_SPEC = importlib.util.spec_from_file_location("geox_mip_artifact_envelope", _MODULE_PATH)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)

(
    GeoXMIPArtifactKind,
    GeoXMIPAuthorizationStatus,
    GeoXMIPConsumptionStatus,
    GeoXMIPDownstreamEligibility,
    build_geox_mip_artifact_envelope,
    serialize_geox_mip_artifact_envelope,
    validate_geox_mip_artifact_envelope,
) = (getattr(_MODULE, name) for name in (
    "GeoXMIPArtifactKind",
    "GeoXMIPAuthorizationStatus",
    "GeoXMIPConsumptionStatus",
    "GeoXMIPDownstreamEligibility",
    "build_geox_mip_artifact_envelope",
    "serialize_geox_mip_artifact_envelope",
    "validate_geox_mip_artifact_envelope",
))


def envelope(**overrides):
    values = dict(
        envelope_version="1.0.0",
        artifact_kind=GeoXMIPArtifactKind.ASSIGNMENT_CANDIDATE,
        artifact_id="fixture-assignment-001",
        artifact_uri="fixture://assignment-001",
        source_system="panel_exp",
        source_repo="/workspace/panel_exp",
        source_commit="abc1234",
        created_at="2026-07-19T00:00:00Z",
        run_id="run-001",
        experiment_id="experiment-001",
        request_id="request-001",
        input_data_fingerprint="sha256:input",
        method_family="SCM",
        instrument_id="SCM_UNIT_JACKKNIFE",
        estimand="ATT",
        kpi="revenue",
        geo_scope="fixture_geos",
        time_window="pre:2025-01;post:2025-02",
        assignment_scope="candidate_pool",
        diagnostic_status="diagnostic",
        method_readiness_status="candidate_gated",
        release_gate_status="required",
        authorization_status=GeoXMIPAuthorizationStatus.NOT_AUTHORIZED,
        blocked_reasons=(),
        warnings=("fixture_only",),
        downstream_eligibility=GeoXMIPDownstreamEligibility.DIAGNOSTIC_SUMMARY,
        mip_consumption_status=GeoXMIPConsumptionStatus.DIAGNOSTIC_CONTEXT_ONLY,
        provenance={"fixture": True, "source": "test"},
        schema_hash="sha256:schema",
    )
    values.update(overrides)
    return build_geox_mip_artifact_envelope(**values)


def test_valid_diagnostic_assignment_candidate() -> None:
    valid, reasons = validate_geox_mip_artifact_envelope(envelope())
    assert valid and reasons == ()


def test_blocked_readout_requires_reason() -> None:
    packet = envelope(artifact_kind="readout_packet", authorization_status="blocked", mip_consumption_status="blocked")
    assert validate_geox_mip_artifact_envelope(packet)[0] is False
    assert "blocked_requires_blocked_reasons" in validate_geox_mip_artifact_envelope(packet)[1]


def test_failure_packet_answerability_context_serializes() -> None:
    packet = envelope(artifact_kind="failure_packet", mip_consumption_status="answerability_context_only", warnings=("failed_panel_check",))
    assert serialize_geox_mip_artifact_envelope(packet)["mip_consumption_status"] == "answerability_context_only"


def test_post_test_spend_remains_non_calibration() -> None:
    packet = envelope(artifact_kind="post_test_spend_evidence", mip_consumption_status="diagnostic_context_only")
    assert validate_geox_mip_artifact_envelope(packet)[0]


def test_calibration_signal_candidate_is_blocked() -> None:
    packet = envelope(artifact_kind="calibration_signal_candidate", authorization_status="blocked", mip_consumption_status="blocked", blocked_reasons=("mapping_missing",))
    assert validate_geox_mip_artifact_envelope(packet)[0]


def test_experiment_evidence_candidate_is_blocked() -> None:
    packet = envelope(artifact_kind="experiment_evidence_candidate", authorization_status="blocked", mip_consumption_status="blocked", blocked_reasons=("authorization_missing",))
    assert validate_geox_mip_artifact_envelope(packet)[0]


def test_deterministic_json_serialization() -> None:
    first = serialize_geox_mip_artifact_envelope(envelope())
    second = serialize_geox_mip_artifact_envelope(envelope())
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert isinstance(first["created_at"], str)


def test_empty_required_field_rejected() -> None:
    valid, reasons = validate_geox_mip_artifact_envelope(envelope(artifact_id=""))
    assert not valid and "required_field_empty:artifact_id" in reasons


def test_invalid_authorization_consumption_combination_rejected() -> None:
    packet = envelope(artifact_kind="assignment_candidate", authorization_status="candidate_gated")
    valid, reasons = validate_geox_mip_artifact_envelope(packet)
    assert not valid and "assignment_authorization_blocked" in reasons


def test_no_production_eligibility_exposed() -> None:
    packet = envelope(downstream_eligibility="experiment_evidence_after_mapping")
    valid, reasons = validate_geox_mip_artifact_envelope(packet)
    assert not valid and "production_downstream_eligibility_blocked" in reasons
    with pytest.raises(ValueError):
        serialize_geox_mip_artifact_envelope(packet)
