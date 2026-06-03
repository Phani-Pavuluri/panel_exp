"""GeoX RunBundle export with opt-in Track B dual-write (M2.1)."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union

from panel_exp.artifacts.run_bundle import RunArtifactBundle, build_run_artifact_bundle
from panel_exp.evidence import DesignEvidence, ExperimentEvidence


def build_geo_run_artifact_bundle(
    *,
    evidence: Optional[
        Union[DesignEvidence, ExperimentEvidence, Mapping[str, Any]]
    ] = None,
    experiment_card: Optional[Any] = None,
    calibration_report: Optional[Any] = None,
    maturity_evidence: Optional[Any] = None,
    readiness_assessment: Optional[Any] = None,
    interference_review: Optional[Mapping[str, Any]] = None,
    warnings: Optional[Any] = None,
    errors: Optional[Any] = None,
    created_at: Optional[str] = None,
    include_track_b_views: bool = False,
    include_trust_report: bool = False,
    track_b_spec: Optional[Mapping[str, Any]] = None,
    track_b_run_stub: Optional[Mapping[str, Any]] = None,
    track_b_calibration_binding: Optional[Mapping[str, Any]] = None,
    track_b_export_hints: Optional[Mapping[str, Any]] = None,
    trust_report_scenarios: Optional[Sequence[Mapping[str, Any]]] = None,
    trust_composition_permitted: bool = True,
    alignment_reference_estimand_id: Optional[str] = None,
) -> RunArtifactBundle:
    """
    Build a Geo RunBundle with optional ``track_b_views`` / TrustReport sidecar.

    Both sidecars are opt-in (default off). When ``track_b_spec`` /
    ``track_b_run_stub`` are omitted, resolves from ``evidence`` (including
    ``track_b_export_hints``). Trust scenarios may be passed explicitly or via
    hints ``trust_scenarios`` / ``track_b_trust_scenarios``.
    Does not change legacy bundle fields or estimator behavior.
    """
    evidence_payload = evidence
    if track_b_export_hints and isinstance(evidence, Mapping):
        merged = dict(evidence)
        hints = dict(merged.get("track_b_export_hints") or {})
        hints.update(track_b_export_hints)
        merged["track_b_export_hints"] = hints
        evidence_payload = merged
    elif track_b_export_hints and hasattr(evidence, "to_dict"):
        d = evidence.to_dict()
        hints = dict(d.get("track_b_export_hints") or {})
        hints.update(track_b_export_hints)
        d["track_b_export_hints"] = hints
        evidence_payload = d

    return build_run_artifact_bundle(
        evidence=evidence_payload,
        experiment_card=experiment_card,
        calibration_report=calibration_report,
        maturity_evidence=maturity_evidence,
        readiness_assessment=readiness_assessment,
        interference_review=interference_review,
        warnings=warnings,
        errors=errors,
        created_at=created_at,
        include_track_b_views=include_track_b_views,
        include_trust_report=include_trust_report,
        track_b_spec=track_b_spec,
        track_b_run_stub=track_b_run_stub,
        track_b_calibration_binding=track_b_calibration_binding,
        trust_report_scenarios=trust_report_scenarios,
        trust_composition_permitted=trust_composition_permitted,
        alignment_reference_estimand_id=alignment_reference_estimand_id,
    )
