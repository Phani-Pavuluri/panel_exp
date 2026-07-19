"""Non-production GeoX-to-MIP artifact-envelope runtime contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping


class _StringEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class GeoXMIPArtifactKind(_StringEnum):
    GEOX_REQUEST = "geox_request"
    GEOX_RESULT = "geox_result"
    ASSIGNMENT_CANDIDATE = "assignment_candidate"
    ASSIGNMENT_MANIFEST = "assignment_manifest"
    RUN_MANIFEST = "run_manifest"
    READOUT_PACKET = "readout_packet"
    FAILURE_PACKET = "failure_packet"
    POST_TEST_SPEND_EVIDENCE = "post_test_spend_evidence"
    TRUSTED_READOUT_SPEND_HANDOFF = "trusted_readout_spend_handoff"
    EXPERIMENT_EVIDENCE_CANDIDATE = "experiment_evidence_candidate"
    CALIBRATION_SIGNAL_CANDIDATE = "calibration_signal_candidate"


class GeoXMIPAuthorizationStatus(_StringEnum):
    NOT_AUTHORIZED = "not_authorized"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    CANDIDATE_GATED = "candidate_gated"
    RELEASE_GATE_REQUIRED = "release_gate_required"
    BLOCKED = "blocked"
    AUTHORIZED_FUTURE_ONLY = "authorized_future_only"


class GeoXMIPConsumptionStatus(_StringEnum):
    NOT_CONSUMABLE = "not_consumable"
    DIAGNOSTIC_CONTEXT_ONLY = "diagnostic_context_only"
    ANSWERABILITY_CONTEXT_ONLY = "answerability_context_only"
    TRUST_REPORT_CANDIDATE = "trust_report_candidate"
    EXPERIMENT_EVIDENCE_CANDIDATE = "experiment_evidence_candidate"
    CALIBRATION_SIGNAL_CANDIDATE = "calibration_signal_candidate"
    BLOCKED = "blocked"


class GeoXMIPDownstreamEligibility(_StringEnum):
    NONE = "none"
    EXPLAIN_ONLY = "explain_only"
    DIAGNOSTIC_SUMMARY = "diagnostic_summary"
    TRUST_REPORT_CANDIDATE_AFTER_GATE = "trust_report_candidate_after_gate"
    EXPERIMENT_EVIDENCE_AFTER_MAPPING = "experiment_evidence_after_mapping"
    CALIBRATION_SIGNAL_AFTER_MAPPING_AND_AUTHORIZATION = "calibration_signal_after_mapping_and_authorization"


@dataclass(frozen=True)
class GeoXMIPArtifactEnvelope:
    envelope_version: str
    artifact_kind: GeoXMIPArtifactKind
    artifact_id: str
    artifact_uri: str
    source_system: str
    source_repo: str
    source_commit: str
    created_at: str
    run_id: str
    experiment_id: str
    request_id: str
    input_data_fingerprint: str
    method_family: str
    instrument_id: str
    estimand: str
    kpi: str
    geo_scope: str
    time_window: str
    assignment_scope: str
    diagnostic_status: str
    method_readiness_status: str
    release_gate_status: str
    authorization_status: GeoXMIPAuthorizationStatus
    blocked_reasons: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    upstream_artifacts: tuple[str, ...] = field(default_factory=tuple)
    downstream_eligibility: GeoXMIPDownstreamEligibility = GeoXMIPDownstreamEligibility.NONE
    mip_consumption_status: GeoXMIPConsumptionStatus = GeoXMIPConsumptionStatus.NOT_CONSUMABLE
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_hash: str = ""


_REQUIRED_STRINGS = (
    "envelope_version", "artifact_id", "artifact_uri", "source_system", "source_repo",
    "source_commit", "created_at", "run_id", "experiment_id", "request_id",
    "input_data_fingerprint", "method_family", "instrument_id", "estimand", "kpi",
    "geo_scope", "time_window", "assignment_scope", "diagnostic_status",
    "method_readiness_status", "release_gate_status", "schema_hash",
)
_PROTECTED_KINDS = {
    GeoXMIPArtifactKind.EXPERIMENT_EVIDENCE_CANDIDATE,
    GeoXMIPArtifactKind.CALIBRATION_SIGNAL_CANDIDATE,
}
_PRODUCTION_ELIGIBILITY = {
    GeoXMIPDownstreamEligibility.EXPERIMENT_EVIDENCE_AFTER_MAPPING,
    GeoXMIPDownstreamEligibility.CALIBRATION_SIGNAL_AFTER_MAPPING_AND_AUTHORIZATION,
}


def build_geox_mip_artifact_envelope(**kwargs: Any) -> GeoXMIPArtifactEnvelope:
    """Build an immutable envelope, coercing supported string enum values."""
    for name, enum_type in (("artifact_kind", GeoXMIPArtifactKind), ("authorization_status", GeoXMIPAuthorizationStatus), ("downstream_eligibility", GeoXMIPDownstreamEligibility), ("mip_consumption_status", GeoXMIPConsumptionStatus)):
        if name in kwargs and not isinstance(kwargs[name], enum_type):
            kwargs[name] = enum_type(kwargs[name])
    for name in ("blocked_reasons", "warnings", "upstream_artifacts"):
        if name in kwargs and not isinstance(kwargs[name], tuple):
            kwargs[name] = tuple(kwargs[name])
    return GeoXMIPArtifactEnvelope(**kwargs)


def validate_geox_mip_artifact_envelope(envelope: GeoXMIPArtifactEnvelope) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    for name in _REQUIRED_STRINGS:
        if not isinstance(getattr(envelope, name), str) or not getattr(envelope, name).strip():
            reasons.append(f"required_field_empty:{name}")
    if not isinstance(envelope.artifact_kind, GeoXMIPArtifactKind):
        reasons.append("invalid_artifact_kind")
    if not isinstance(envelope.authorization_status, GeoXMIPAuthorizationStatus):
        reasons.append("invalid_authorization_status")
    if not isinstance(envelope.mip_consumption_status, GeoXMIPConsumptionStatus):
        reasons.append("invalid_mip_consumption_status")
    if not isinstance(envelope.downstream_eligibility, GeoXMIPDownstreamEligibility):
        reasons.append("invalid_downstream_eligibility")
    if envelope.authorization_status is GeoXMIPAuthorizationStatus.BLOCKED and not envelope.blocked_reasons:
        reasons.append("blocked_requires_blocked_reasons")
    if envelope.artifact_kind in _PROTECTED_KINDS:
        if envelope.authorization_status is not GeoXMIPAuthorizationStatus.BLOCKED:
            reasons.append("candidate_kind_must_be_blocked")
        if envelope.mip_consumption_status is not GeoXMIPConsumptionStatus.BLOCKED:
            reasons.append("candidate_kind_must_not_be_consumable")
    if envelope.artifact_kind is GeoXMIPArtifactKind.ASSIGNMENT_CANDIDATE and envelope.authorization_status is not GeoXMIPAuthorizationStatus.NOT_AUTHORIZED:
        reasons.append("assignment_authorization_blocked")
    if envelope.artifact_kind is GeoXMIPArtifactKind.READOUT_PACKET and envelope.authorization_status is not GeoXMIPAuthorizationStatus.BLOCKED:
        reasons.append("readout_authorization_blocked")
    if envelope.downstream_eligibility in _PRODUCTION_ELIGIBILITY:
        reasons.append("production_downstream_eligibility_blocked")
    if envelope.mip_consumption_status in {GeoXMIPConsumptionStatus.EXPERIMENT_EVIDENCE_CANDIDATE, GeoXMIPConsumptionStatus.CALIBRATION_SIGNAL_CANDIDATE}:
        reasons.append("mip_production_consumption_blocked")
    return not reasons, tuple(reasons)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _json_safe(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    return value


def serialize_geox_mip_artifact_envelope(envelope: GeoXMIPArtifactEnvelope) -> dict[str, Any]:
    """Return deterministic JSON-safe data; validation is intentionally explicit."""
    valid, reasons = validate_geox_mip_artifact_envelope(envelope)
    if not valid:
        raise ValueError("invalid GeoX/MIP artifact envelope: " + ", ".join(reasons))
    return _json_safe(asdict(envelope))
