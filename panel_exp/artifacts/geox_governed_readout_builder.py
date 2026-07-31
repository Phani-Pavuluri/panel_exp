"""Deterministic, non-authorizing builder for certified GeoX readouts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping
import json
from pathlib import Path


@dataclass(frozen=True)
class GeoXTemporalBounds:
    pre_start: str
    pre_end: str
    post_start: str
    post_end: str
    created_at: str
    as_of: str
    valid_through: str | None

    def canonical(self) -> "GeoXTemporalBounds":
        values = [self.pre_start, self.pre_end, self.post_start, self.post_end, self.created_at, self.as_of]
        parsed = [_utc(value) for value in values]
        if parsed[0] >= parsed[1] or parsed[2] >= parsed[3] or parsed[1] > parsed[2]:
            raise ValueError("invalid or overlapping temporal bounds")
        if parsed[2] < parsed[5] or parsed[4] > parsed[5]:
            raise ValueError("inconsistent creation/as-of timestamps")
        valid = _utc(self.valid_through) if self.valid_through else None
        if valid is not None and valid < parsed[5]:
            raise ValueError("valid-through precedes evidence as-of")
        return GeoXTemporalBounds(*[item.isoformat().replace("+00:00", "Z") for item in parsed], valid.isoformat().replace("+00:00", "Z") if valid else None)


@dataclass(frozen=True)
class GeoXProducerInput:
    readout_id: str
    fixture_id: str
    experiment_id: str
    kpi: str
    estimand: str
    method_family: str
    instrument_id: str
    effect_estimate: float | None
    temporal: GeoXTemporalBounds
    producer_commit: str
    producer_package_version: str
    schema_version: str = "1.0.0"

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


def build_geox_governed_readout_from_typed_input(
    producer: GeoXProducerInput,
    *,
    readout_fields: Mapping[str, Any],
    envelope_metadata: Mapping[str, Any],
    reference_time: str | None,
) -> tuple[GeoXGovernedExperimentReadout, Any]:
    """Construct from explicit producer metadata and caller-supplied analytical fields."""
    temporal = producer.temporal.canonical()
    freshness = resolve_freshness(temporal.valid_through, reference_time)
    if freshness == "unknown" and readout_fields.get("handoff_eligibility_status") == "eligible_for_compatibility_evaluation":
        raise ValueError("handoff eligibility requires explicit freshness")
    payload = dict(readout_fields)
    payload.update(
        readout_id=producer.readout_id, fixture_id=producer.fixture_id, experiment_id=producer.experiment_id,
        kpi=producer.kpi, estimand=producer.estimand, method_family=producer.method_family,
        instrument_id=producer.instrument_id, effect_estimate=producer.effect_estimate,
        producer_commit=producer.producer_commit, producer_package_version=producer.producer_package_version,
        readout_version=producer.schema_version, artifact_version=producer.schema_version,
        pre_period=f"{temporal.pre_start}/{temporal.pre_end}", post_period=f"{temporal.post_start}/{temporal.post_end}",
        freshness_status=freshness,
    )
    try:
        readout = GeoXGovernedExperimentReadout(**payload)
    except TypeError as exc:
        raise ValueError("typed input is missing explicit analytical fields") from exc
    return build_geox_governed_readout_package_entrypoint(readout, reference_time=reference_time, valid_through=temporal.valid_through, envelope_metadata=envelope_metadata)


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
    if envelope_metadata is None:
        if readout.handoff_eligibility_status == "eligible_for_compatibility_evaluation" and freshness != "fresh":
            raise ValueError("eligible readout requires fresh evidence")
        return readout, None
    metadata = dict(envelope_metadata)
    for key in ("created_at", "request_id", "input_data_fingerprint", "schema_hash"):
        if key not in metadata or not str(metadata[key]).strip():
            raise ValueError(f"missing required envelope metadata: {key}")
    envelope = build_geox_mip_artifact_envelope(
        envelope_version=metadata.get("envelope_version", "1.0.0"),
        artifact_kind=GeoXMIPArtifactKind.READOUT_PACKET,
        artifact_id=readout.readout_id,
        artifact_uri=metadata.get("artifact_uri", "fixture://" + readout.fixture_id),
        source_system="panel_exp",
        source_repo=readout.provenance.source_repo,
        source_commit=readout.producer_commit,
        created_at=str(metadata["created_at"]),
        run_id=readout.replay_metadata.replay_version,
        experiment_id=readout.experiment_id,
        request_id=str(metadata["request_id"]),
        input_data_fingerprint=str(metadata["input_data_fingerprint"]),
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
        schema_hash=str(metadata["schema_hash"]),
    )
    valid, envelope_reasons = validate_geox_mip_artifact_envelope(envelope)
    if not valid:
        raise ValueError("invalid readout envelope: " + ", ".join(envelope_reasons))
    return readout, envelope


def build_geox_governed_readout_from_fixture(
    metadata: Mapping[str, Any], *, envelope_metadata: Mapping[str, Any], reference_time: str | None = None
) -> tuple[GeoXGovernedExperimentReadout, Any]:
    """Construct a readout from one certified fixture's explicit truth metadata."""
    required = ("fixture_id", "dataset_version", "truth_version", "kpi", "estimand", "method_family", "instrument_id")
    missing = [key for key in required if not str(metadata.get(key, "")).strip()]
    if missing:
        raise ValueError("missing certified fixture fields: " + ", ".join(missing))
    point = metadata.get("expected_point_estimate")
    if point is None:
        raise ValueError("missing expected_point_estimate")
    blocked = tuple(metadata.get("expected_blocked_reasons", ()))
    status = str(metadata.get("expected_readout_status", "diagnostic"))
    readout = GeoXGovernedExperimentReadout(
        readout_id=str(metadata["fixture_id"]), readout_version=str(metadata.get("fixture_version", "1.0.0")),
        artifact_version=str(metadata.get("fixture_version", "1.0.0")), producer_package_version=str(metadata.get("package_version", "unknown")),
        producer_commit=str(metadata["provenance"]["source_commit"]), experiment_id=str(metadata["fixture_id"]), fixture_id=str(metadata["fixture_id"]),
        dataset_version=str(metadata["dataset_version"]), truth_version=str(metadata["truth_version"]), kpi=str(metadata["kpi"]), kpi_units="currency",
        estimand=str(metadata["estimand"]), effect_scale="absolute", effect_estimate=float(point), absolute_lift=metadata.get("known_lift_absolute"),
        relative_lift=metadata.get("known_lift_relative"), incremental_outcome=metadata.get("known_incremental_outcome"), channel="unknown", tactic="unknown",
        geography_scope=str(metadata.get("geo_scope", "")), geo_grain=str(metadata.get("panel_grain", "")), time_window="pre/post",
        pre_period=str(metadata.get("time_window", {}).get("pre_period", "")), post_period=str(metadata.get("time_window", {}).get("post_period", "")),
        freshness_status="unknown", uncertainty_available=metadata.get("expected_standard_error") is not None,
        standard_error=metadata.get("expected_standard_error"), confidence_interval=tuple(metadata["expected_confidence_interval"]) if metadata.get("expected_confidence_interval") else None,
        interval_semantics=str(metadata.get("expected_uncertainty_semantics", "none")), method_family=str(metadata["method_family"]), instrument_id=str(metadata["instrument_id"]),
        design_type=str(metadata.get("design_type", "")), feasibility_status=str(metadata.get("expected_feasibility_status", "")), method_status=str(metadata.get("certification_status", "")),
        readout_status=status, handoff_eligibility_status="blocked_for_handoff" if status != "success" else "eligible_for_compatibility_evaluation",
        warnings=tuple(metadata.get("expected_warnings", ())), blocked_reasons=blocked, failure_reasons=(),
        lineage=__import__("panel_exp.contracts.geox_governed_experiment_readout", fromlist=["GeoXReadoutLineage"]).GeoXReadoutLineage(str(metadata["fixture_id"]), str(metadata["dataset_version"]), str(metadata["truth_version"])),
        provenance=__import__("panel_exp.contracts.geox_governed_experiment_readout", fromlist=["GeoXReadoutProvenance"]).GeoXReadoutProvenance(str(metadata["provenance"]["source_repo"]), str(metadata["provenance"]["source_commit"]), str(metadata.get("package_version", "unknown")), str(metadata["provenance"]["created_by"])),
        replay_metadata=__import__("panel_exp.contracts.geox_governed_experiment_readout", fromlist=["GeoXReadoutReplayMetadata"]).GeoXReadoutReplayMetadata(int(metadata.get("assignment_seed", 0)), str(metadata.get("fixture_version", "1.0.0"))),
        authorization_flags=__import__("panel_exp.contracts.geox_governed_experiment_readout", fromlist=["GeoXReadoutAuthorizationFlags"]).GeoXReadoutAuthorizationFlags(),
    )
    return build_geox_governed_readout_package_entrypoint(readout, reference_time=reference_time, envelope_metadata=envelope_metadata)


def build_geox_governed_readout_from_certified_fixture(
    fixture_id: str, *, fixture_root: str | Path = "tests/fixtures/geox_governed_readouts",
    envelope_metadata: Mapping[str, Any] | None = None,
) -> tuple[GeoXGovernedExperimentReadout, Any]:
    """Load and reproduce a certified readout without altering analytical truth."""
    root = Path(fixture_root) / fixture_id
    if not root.is_dir():
        raise ValueError(f"unknown certified fixture: {fixture_id}")
    manifest = json.loads((Path(fixture_root) / "manifest.json").read_text())
    if not any(c["case_id"] == fixture_id for c in manifest["cases"]):
        raise ValueError(f"fixture is not listed in manifest: {fixture_id}")
    certified = json.loads((root / "governed_readout.json").read_text())
    replay = json.loads((root / "replay.json").read_text())
    if replay.get("fixture_id", replay.get("case_id", fixture_id)) != fixture_id:
        raise ValueError("replay fixture mismatch")
    from panel_exp.contracts.geox_governed_experiment_readout import deserialize_geox_governed_experiment_readout
    readout = deserialize_geox_governed_experiment_readout(certified)
    if readout.fixture_id != fixture_id or readout.lineage.fixture_id != fixture_id:
        raise ValueError("certified fixture identity mismatch")
    if readout.replay_metadata.replay_version != str(replay.get("replay_version", readout.replay_metadata.replay_version)):
        raise ValueError("replay version mismatch")
    reasons = validate_geox_governed_experiment_readout(readout)
    if reasons:
        raise ValueError("invalid certified readout: " + ", ".join(reasons))
    return build_geox_governed_readout_package_entrypoint(readout, envelope_metadata=envelope_metadata)
