"""Canonical GeoX RunBundle export (M2.1 / M2.2).

Opt-in Track B sidecar and TrustReport composition. Legacy ``build_run_artifact_bundle``
remains the default for non-geo callers.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union

from panel_exp.artifacts.run_bundle import RunArtifactBundle
from panel_exp.evidence import DesignEvidence, ExperimentEvidence
from panel_exp.track_b.export import build_geo_run_artifact_bundle


def export_geo_run_bundle(
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
    include_trust_report_decision_context: bool = False,
    trust_report_decision_inputs_strict: bool = False,
) -> RunArtifactBundle:
    """
    Export a GeoX run readout bundle with optional governed Track B sidecar.

    Defaults preserve legacy behavior (no ``track_b_views``). Set
    ``include_track_b_views=True`` for adapter sidecar; add
    ``include_trust_report=True`` and ``trust_report_scenarios`` for TrustReport.
    """
    return build_geo_run_artifact_bundle(
        evidence=evidence,
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
        track_b_export_hints=track_b_export_hints,
        trust_report_scenarios=trust_report_scenarios,
        trust_composition_permitted=trust_composition_permitted,
        alignment_reference_estimand_id=alignment_reference_estimand_id,
        include_trust_report_decision_context=include_trust_report_decision_context,
        trust_report_decision_inputs_strict=trust_report_decision_inputs_strict,
    )
