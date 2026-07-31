"""Deterministic, non-authorizing builder for certified GeoX readouts."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from panel_exp.contracts.geox_governed_experiment_readout import (
    GeoXGovernedExperimentReadout,
    validate_geox_governed_experiment_readout,
)
from panel_exp.contracts.geox_mip_artifact_envelope import (
    GeoXMIPArtifactKind,
    GeoXMIPAuthorizationStatus,
    GeoXMIPConsumptionStatus,
    GeoXMIPDownstreamEligibility,
    build_geox_mip_artifact_envelope,
    validate_geox_mip_artifact_envelope,
)


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include an explicit timezone")
    return parsed.astimezone(timezone.utc)


def resolve_freshness(valid_through: str | None, reference_time: str | None) -> str:
    if valid_through is None or reference_time is None:
        return "unknown"
    return "fresh" if _utc(reference_time) <= _utc(valid_through) else "stale"


def build_geox_governed_readout_package_entrypoint(
    readout: GeoXGovernedExperimentReadout,
    *,
    reference_time: str | None = None,
    valid_through: str | None = None,
    envelope_metadata: Mapping[str, Any] | None = None,
):
    """Validate and return the supplied readout plus an optional transport envelope."""
    freshness = resolve_freshness(valid_through, reference_time)
    if freshness == "stale" and readout.freshness_status != "stale":
        raise ValueError("stale evidence cannot be silently refreshed")
    reasons = validate_geox_governed_experiment_readout(readout)
    if reasons:
        raise ValueError("invalid governed readout: " + ", ".join(reasons))
    metadata = dict(envelope_metadata or {})
    envelope = build_geox_mip_artifact_envelope(
        envelope_version=metadata.get("envelope_version", "1.0.0"),
        artifact_kind=GeoXMIPArtifactKind.READOUT_PACKET,
        artifact_id=readout.readout_id,
        artifact_uri=metadata.get("artifact_uri", "fixture://" + readout.fixture_id),
        source_system="panel_exp",
        source_repo=readout.provenance.source_repo,
        source_commit=readout.producer_commit,
        created_at=metadata.get("created_at", "1970-01-01T00:00:00+00:00"),
        run_id=readout.replay_metadata.replay_version,
        experiment_id=readout.experiment_id,
        request_id=metadata.get("request_id", readout.readout_id),
        input_data_fingerprint=metadata.get("input_data_fingerprint", readout.fixture_id),
        method_family=readout.method_family,
        instrument_id=readout.instrument_id,
        estimand=readout.estimand,
        kpi=readout.kpi,
        geo_scope=readout.geography_scope,
        time_window=readout.time_window,
        assignment_scope=metadata.get("assignment_scope", "readout_only"),
        diagnostic_status=readout.readout_status,
        method_readiness_status=readout.method_status,
        release_gate_status=metadata.get("release_gate_status", "required"),
        authorization_status=GeoXMIPAuthorizationStatus.BLOCKED,
        downstream_eligibility=GeoXMIPDownstreamEligibility.NONE,
        mip_consumption_status=GeoXMIPConsumptionStatus.BLOCKED,
        blocked_reasons=("non_production_readout_transport",),
        provenance={"producer_package_version": readout.producer_package_version},
        schema_hash=readout.readout_version,
    )
    valid, envelope_reasons = validate_geox_mip_artifact_envelope(envelope)
    if not valid:
        raise ValueError("invalid readout envelope: " + ", ".join(envelope_reasons))
    return readout, envelope
