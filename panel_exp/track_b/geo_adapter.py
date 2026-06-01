"""Geo modality Track B adapter (M2).

Resolves ``adapter_expected_output``-shaped dicts from declarative spec slices
and run metadata. Does not emit trust verdicts or change estimator behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from panel_exp.track_b._registry import (
    CALIBRATION_SIGNAL_BY_CONFIG,
    CONFIG_RESOLUTION,
    LEGACY_ESTIMAND_MAP,
    PLACEBO_NULL_ENVELOPE_ID,
    POOLED_RELATIVE_ATT_ID,
)

_BLOCK = object()


@dataclass(frozen=True)
class GeoAdapterResolveInput:
    """Inputs for adapter resolution (fixture slice or bundle extraction)."""

    spec: Mapping[str, Any]
    run_artifacts_stub: Mapping[str, Any]
    calibration_signal_binding: Optional[Mapping[str, Any]] = None


def resolve_geo_adapter_output(
    *,
    spec: Mapping[str, Any],
    run_artifacts_stub: Mapping[str, Any],
    calibration_signal_binding: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Resolve Track B adapter output from spec + run stub (B4 rules)."""
    return resolve_geo_adapter_input(
        GeoAdapterResolveInput(
            spec=spec,
            run_artifacts_stub=run_artifacts_stub,
            calibration_signal_binding=calibration_signal_binding,
        )
    )


def resolve_geo_adapter_input(inp: GeoAdapterResolveInput) -> dict[str, Any]:
    spec = dict(inp.spec)
    stub = dict(inp.run_artifacts_stub)

    legacy_applied, declared_id, block_reason = _resolve_declaration(spec)
    if block_reason:
        return _blocked_output(spec, stub, block_reason, legacy_applied=legacy_applied)

    config_alias = str(stub.get("config_alias") or "")
    resolution = CONFIG_RESOLUTION.get(config_alias)
    if resolution is None:
        return _blocked_output(
            spec,
            stub,
            f"unmapped_config_alias:{config_alias or 'missing'}",
            legacy_applied=False,
        )

    geometry_class = str(spec.get("geometry_class") or "multi_treated_default")
    instrument_id = resolution.instrument_id_template.format(geometry=geometry_class)

    partial = _partial_export_if_needed(spec, stub, resolution, instrument_id)
    if partial is not None:
        return partial

    exported_id = _exported_estimand_id(spec, stub, declared_id)
    interval_id, interval_sem = _interval_layer(spec, stub, resolution, exported_id)
    evidence = _build_evidence(
        spec=spec,
        stub=stub,
        resolution=resolution,
        declared_id=declared_id,
        exported_id=exported_id,
        interval_id=interval_id,
        interval_sem=interval_sem,
        instrument_id=instrument_id,
        geometry_class=geometry_class,
        legacy_applied=legacy_applied,
    )
    facts = _build_alignment_facts(
        spec=spec,
        stub=stub,
        resolution=resolution,
        declared_id=declared_id,
        exported_id=exported_id,
        interval_id=interval_id,
        interval_sem=interval_sem,
        evidence=evidence,
    )
    diag = _build_diagnostic_summary(
        export_status="complete",
        declared_id=declared_id,
        exported_id=exported_id,
        interval_id=interval_id,
        instrument_id=instrument_id,
        facts=facts,
        stub=stub,
        spec=spec,
        resolution=resolution,
    )
    must_not = ["trust_outcome", "alignment_verdict"]
    if resolution.interval_semantics == "none":
        must_not.append("interval_estimand_id")

    out: dict[str, Any] = {
        "export_status": "complete",
        "experiment_evidence": evidence,
        "alignment_facts": facts,
        "diagnostic_summary": diag,
        "must_not_contain_on_evidence": must_not,
    }
    if legacy_applied:
        out["legacy_mapping_applied"] = True
    return out


def resolve_geo_adapter_output_from_bundle(
    bundle: Mapping[str, Any],
) -> dict[str, Any]:
    """Resolve adapter output from a RunBundle-shaped mapping (legacy evidence path)."""
    inp = extract_resolve_input_from_bundle(bundle)
    return resolve_geo_adapter_input(inp)


def extract_resolve_input_from_bundle(
    bundle: Mapping[str, Any],
) -> GeoAdapterResolveInput:
    """Build resolve input from bundle legacy ``evidence`` (best-effort)."""
    evidence = bundle.get("evidence") or {}
    meta = evidence.get("inference_metadata") or {}
    design = evidence.get("design") or {}

    spec: dict[str, Any] = {
        "study_id": evidence.get("experiment_id") or bundle.get("experiment_id") or "",
        "spec_version": "1",
        "modality": "geo",
        "study_purpose": "business",
        "geometry_class": meta.get("geometry_class") or "multi_treated_default",
        "mmm_calibration_intent": bool(meta.get("mmm_calibration_intent")),
    }

    declared = meta.get("declared_estimand_id") or design.get("declared_estimand_id")
    if declared:
        spec["declared_estimand_id"] = declared
    else:
        target = design.get("target_estimand") or meta.get("target_estimand")
        legacy_policy = meta.get("legacy_aggregation_policy") or meta.get(
            "aggregation_policy"
        )
        if target:
            spec["legacy_target_estimand"] = str(target)
        if legacy_policy:
            spec["legacy_aggregation_policy"] = str(legacy_policy)

    interval_exp = meta.get("interval_estimand_expectation_id")
    if interval_exp:
        spec["interval_estimand_expectation_id"] = interval_exp

    transform_ref = meta.get("estimand_transform_ref")
    if transform_ref:
        spec["estimand_transform_ref"] = transform_ref

    config_alias = meta.get("config_alias") or _config_alias_from_metadata(meta)
    stub: dict[str, Any] = {
        "config_alias": config_alias,
        "estimator_family": meta.get("estimator_family") or meta.get("estimator_name"),
        "inference_method": meta.get("inference_method"),
        "n_treated": meta.get("n_treated"),
        "geometry_observed": meta.get("geometry_observed"),
        "run_status": meta.get("run_status") or "success",
        "path_interval_type_legacy": meta.get("path_interval_type")
        or meta.get("interval_type"),
        "has_path_intervals": meta.get("has_path_intervals"),
        "export_resolver_default": meta.get("export_resolver_default"),
        "transform_pipeline_attested": meta.get("transform_pipeline_attested"),
    }
    return GeoAdapterResolveInput(spec=spec, run_artifacts_stub=stub)


def _config_alias_from_metadata(meta: Mapping[str, Any]) -> str:
    estimator = str(meta.get("estimator_name") or meta.get("estimator_family") or "")
    inference = str(meta.get("inference_method") or meta.get("inference_mode") or "")
    mapping = {
        ("SCM", "unit_jackknife"): "SCM_UnitJackKnife",
        ("synthetic_control", "unit_jackknife"): "SCM_UnitJackKnife",
        ("TBRRidge", "kfold"): "TBRRidge_Kfold",
        ("tbrridge", "kfold"): "TBRRidge_Kfold",
        ("TBRRidge", "block_residual_bootstrap"): "TBRRidge_BlockResidualBootstrap",
        ("tbrridge", "block_residual_bootstrap"): "TBRRidge_BlockResidualBootstrap",
        ("AugSynthCVXPY", "point_only"): "AugSynthCVXPY_Point",
        ("augsynth_cvxpy", "point_only"): "AugSynthCVXPY_Point",
        ("DID", "bootstrap"): "DID_Bootstrap",
        ("did", "bootstrap"): "DID_Bootstrap",
        ("SCM", "placebo"): "SCM_Placebo",
        ("synthetic_control", "placebo"): "SCM_Placebo",
    }
    return mapping.get((estimator, inference), "")


def _resolve_declaration(
    spec: Mapping[str, Any],
) -> tuple[bool, Optional[str], Optional[str]]:
    declared = spec.get("declared_estimand_id")
    if declared:
        return False, str(declared), None

    legacy = str(spec.get("legacy_target_estimand") or "")
    if legacy in ("", "null", "None"):
        return False, None, "missing_declared_estimand_id"

    if legacy == "unknown":
        return False, None, "legacy_target_estimand_unknown"

    policy = str(spec.get("legacy_aggregation_policy") or "pooled_path")
    key = (legacy, policy)
    mapped = LEGACY_ESTIMAND_MAP.get(key)
    if mapped is _BLOCK or mapped is None:
        if legacy == "cumulative_att":
            mapped = LEGACY_ESTIMAND_MAP.get(("cumulative_att", ""))
        if mapped is _BLOCK or mapped is None:
            return False, None, f"legacy_estimand_unmapped:{legacy}+{policy}"

    return True, str(mapped), None


def _blocked_output(
    spec: Mapping[str, Any],
    stub: Mapping[str, Any],
    block_reason: str,
    *,
    legacy_applied: bool,
) -> dict[str, Any]:
    config_alias = str(stub.get("config_alias") or "")
    resolution = CONFIG_RESOLUTION.get(config_alias)
    geometry_class = str(spec.get("geometry_class") or "multi_treated_default")
    evidence: dict[str, Any] = {
        "declared_estimand_id": None,
        "exported_estimand_id": "unknown",
        "decision_grade_export_permitted": False,
    }
    if block_reason == "missing_declared_estimand_id" and resolution:
        evidence["measurement_instrument_id"] = resolution.instrument_id_template.format(
            geometry=geometry_class
        )
    if block_reason == "legacy_target_estimand_unknown":
        evidence["declared_estimand_id"] = None

    out: dict[str, Any] = {
        "export_status": "blocked",
        "block_reason": block_reason,
        "legacy_mapping_applied": legacy_applied,
        "experiment_evidence": evidence,
        "diagnostic_summary": {
            "export_status": "blocked",
            "primary_context_estimand_id": None,
            "measurement_instrument_id": None,
            "must_not_contain_trust_outcome": True,
        },
        "must_not_contain_on_evidence": [
            "trust_outcome",
            "alignment_verdict",
            "declared_exported_aligned",
        ],
    }
    if block_reason == "missing_declared_estimand_id":
        out["alignment_facts"] = None
    return out


def _partial_export_if_needed(
    spec: Mapping[str, Any],
    stub: Mapping[str, Any],
    resolution: Any,
    instrument_id: str,
) -> Optional[dict[str, Any]]:
    if resolution.config_alias != "SCM_Placebo":
        return None

    instrument_geometry = resolution.instrument_geometry_scope
    spec_geometry = str(spec.get("geometry_class") or "")
    observed = stub.get("geometry_observed") or spec_geometry
    run_status = str(stub.get("run_status") or "success")

    geometry_ok = (
        instrument_geometry == spec_geometry
        and observed == instrument_geometry
        and run_status == "success"
    )
    if geometry_ok and stub.get("failure_type") is None:
        return None

    declared_id = str(spec.get("declared_estimand_id") or POOLED_RELATIVE_ATT_ID)
    evidence: dict[str, Any] = {
        "declared_estimand_id": declared_id,
        "exported_estimand_id": "unknown",
        "scored_estimand_id": None,
        "interval_estimand_id": None,
        "measurement_instrument_id": instrument_id,
        "instrument_family": resolution.instrument_family,
        "inference_method": resolution.inference_method,
        "geometry_class": spec_geometry,
        "geometry_observed": observed,
        "interval_semantics": resolution.interval_semantics,
        "config_alias": resolution.config_alias,
        "instrument_plan_violation": True,
        "run_status": run_status,
        "calibration_signal_id": CALIBRATION_SIGNAL_BY_CONFIG.get(
            resolution.config_alias, {}
        ).get("signal_id"),
        "calibration_signal_version": CALIBRATION_SIGNAL_BY_CONFIG.get(
            resolution.config_alias, {}
        ).get("signal_version"),
        "calibration_signal_missing": False,
        "decision_grade_export_permitted": False,
        "mmm_intake_blocked": False,
        "mmm_export_ready": False,
    }
    facts = {
        "declared_exported_aligned": False,
        "declared_interval_aligned": False,
        "exported_interval_aligned": False,
        "scale_compatible": None,
        "aggregation_divergence_detected": False,
        "geometry_within_scope": False,
        "interval_semantics_compatible": None,
        "transform_declared": False,
    }
    diag = {
        "export_status": "partial",
        "primary_context_estimand_id": declared_id,
        "diagnostic_estimand_id": None,
        "measurement_instrument_id": instrument_id,
        "estimand_diagnostic_facets": [
            {
                "facet_id": "geometry_out_of_scope",
                "severity": "blocking",
                "modifier_class": "trust_modifier",
                "notes": (
                    f"Placebo instrument {instrument_geometry}; "
                    f"run n_treated={stub.get('n_treated')}"
                ),
            }
        ],
        "must_not_contain_trust_outcome": True,
    }
    return {
        "export_status": "partial",
        "partial_reason": "geometry_out_of_scope_for_placebo_instrument",
        "experiment_evidence": evidence,
        "alignment_facts": facts,
        "diagnostic_summary": diag,
        "must_not_contain_on_evidence": [
            "trust_outcome",
            "alignment_verdict",
        ],
    }


def _exported_estimand_id(
    spec: Mapping[str, Any],
    stub: Mapping[str, Any],
    declared_id: str,
) -> str:
    if stub.get("export_resolver_default") == "pooled_path":
        if "cell_mean" in declared_id:
            return POOLED_RELATIVE_ATT_ID
    return declared_id


def _interval_layer(
    spec: Mapping[str, Any],
    stub: Mapping[str, Any],
    resolution: Any,
    exported_id: str,
) -> tuple[Optional[str], str]:
    sem = resolution.interval_semantics
    if sem == "none":
        return None, sem
    if sem == "placebo_band":
        return str(spec.get("interval_estimand_expectation_id") or PLACEBO_NULL_ENVELOPE_ID), sem
    if sem == "cumulative_att_interval":
        return "geo.cumulative_att.did_bootstrap.absolute", sem
    interval_exp = spec.get("interval_estimand_expectation_id")
    if interval_exp and stub.get("export_resolver_default") == "pooled_path":
        return str(exported_id), sem
    if interval_exp:
        return str(interval_exp), sem
    return exported_id, sem


def _build_evidence(
    *,
    spec: Mapping[str, Any],
    stub: Mapping[str, Any],
    resolution: Any,
    declared_id: str,
    exported_id: str,
    interval_id: Optional[str],
    interval_sem: str,
    instrument_id: str,
    geometry_class: str,
    legacy_applied: bool,
) -> dict[str, Any]:
    signal = CALIBRATION_SIGNAL_BY_CONFIG.get(resolution.config_alias, {})
    evidence: dict[str, Any] = {
        "declared_estimand_id": declared_id,
        "exported_estimand_id": exported_id,
        "scored_estimand_id": None,
        "measurement_instrument_id": instrument_id,
        "instrument_family": resolution.instrument_family,
        "inference_method": resolution.inference_method,
        "geometry_class": geometry_class,
        "interval_semantics": interval_sem,
        "config_alias": resolution.config_alias,
        "measurement_instrument_id_resolved_from": "config_hash",
        "instrument_plan_violation": False,
        "calibration_signal_id": signal.get("signal_id"),
        "calibration_signal_version": signal.get("signal_version"),
        "calibration_signal_missing": False,
        "calibration_signal_stale": False,
        "mmm_intake_blocked": False,
        "mmm_export_ready": False,
    }
    if interval_id is not None:
        evidence["interval_estimand_id"] = interval_id
    if legacy_applied:
        evidence["estimand_family_legacy"] = spec.get("legacy_target_estimand")

    _apply_mmm_fields(spec, stub, evidence)
    return evidence


def _apply_mmm_fields(
    spec: Mapping[str, Any],
    stub: Mapping[str, Any],
    evidence: dict[str, Any],
) -> None:
    if not spec.get("mmm_calibration_intent"):
        return
    transform_ref = spec.get("estimand_transform_ref")
    pipeline_ok = stub.get("transform_pipeline_attested") is True
    evidence["transform_source_estimand_id"] = evidence.get("declared_estimand_id")
    if transform_ref:
        evidence["transform_target_estimand_id"] = (
            "mmm.delta_mu.simulated_response.absolute"
        )
        evidence["transform_evidence_complete"] = pipeline_ok
    else:
        evidence["transform_target_estimand_id"] = None
        evidence["transform_evidence_complete"] = False
    evidence["mmm_intake_blocked"] = True
    evidence["mmm_export_ready"] = False


def _build_alignment_facts(
    *,
    spec: Mapping[str, Any],
    stub: Mapping[str, Any],
    resolution: Any,
    declared_id: str,
    exported_id: str,
    interval_id: Optional[str],
    interval_sem: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    interval_exp = spec.get("interval_estimand_expectation_id")
    declared_interval_aligned = (
        interval_id is not None
        and interval_exp is not None
        and interval_id == interval_exp
    )
    if interval_sem == "none":
        declared_interval_aligned = False
    if interval_sem == "cumulative_att_interval":
        declared_interval_aligned = False

    declared_exported_aligned = declared_id == exported_id
    aggregation_divergence = (
        not declared_exported_aligned
        and stub.get("export_resolver_default") == "pooled_path"
        and "cell_mean" in declared_id
    )

    scale_compatible: Any
    if interval_sem == "cumulative_att_interval":
        scale_compatible = False
    else:
        scale_compatible = True

    exported_interval_aligned: Any
    if resolution.interval_semantics == "placebo_band":
        exported_interval_aligned = True
    elif interval_id and exported_id:
        exported_interval_aligned = interval_id == exported_id
    else:
        exported_interval_aligned = None

    facts: dict[str, Any] = {
        "declared_exported_aligned": declared_exported_aligned,
        "declared_interval_aligned": declared_interval_aligned,
        "exported_interval_aligned": exported_interval_aligned,
        "scored_exported_aligned": None,
        "scale_compatible": scale_compatible,
        "aggregation_divergence_detected": aggregation_divergence,
        "geometry_within_scope": True,
        "interval_semantics_compatible": interval_sem != "placebo_band"
        or resolution.interval_semantics == "placebo_band",
        "transform_declared": bool(spec.get("estimand_transform_ref")),
        "transform_evidence_complete": evidence.get("transform_evidence_complete"),
    }
    if spec.get("mmm_calibration_intent"):
        facts["mmm_intake_blocked"] = evidence.get("mmm_intake_blocked")
        if not spec.get("estimand_transform_ref"):
            facts["transform_declared"] = False
            facts["transform_evidence_complete"] = False
    return facts


def _build_diagnostic_summary(
    *,
    export_status: str,
    declared_id: str,
    exported_id: str,
    interval_id: Optional[str],
    instrument_id: str,
    facts: Mapping[str, Any],
    stub: Mapping[str, Any],
    spec: Mapping[str, Any],
    resolution: Any,
) -> dict[str, Any]:
    diag: dict[str, Any] = {
        "export_status": export_status,
        "primary_context_estimand_id": declared_id,
        "diagnostic_estimand_id": None,
        "measurement_instrument_id": instrument_id,
        "must_not_contain_trust_outcome": True,
    }
    if resolution.interval_semantics in ("placebo_band", "cumulative_att_interval"):
        diag["diagnostic_estimand_id"] = interval_id
    elif facts.get("aggregation_divergence_detected"):
        diag["diagnostic_estimand_id"] = exported_id
        diag["estimand_diagnostic_facets"] = [
            {
                "facet_id": "aggregation_mismatch",
                "severity": "moderate",
                "modifier_class": "trust_modifier",
                "declared_id": declared_id,
                "exported_id": exported_id,
            }
        ]
    return diag
