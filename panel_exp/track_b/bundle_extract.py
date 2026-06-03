"""Extract Track B adapter inputs from legacy RunBundle / evidence (M2.1).

Reads explicit ``track_b_export_hints`` and structured ``inference_metadata`` only.
Does not infer ``declared_estimand_id`` from estimator names.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Optional

from panel_exp.track_b.geo_adapter import GeoAdapterResolveInput

ExtractionCompleteness = Literal["complete", "partial", "blocked"]


@dataclass(frozen=True)
class BundleExtractionResult:
    """Outcome of mapping legacy bundle evidence → adapter resolve input."""

    input: GeoAdapterResolveInput
    completeness: ExtractionCompleteness
    notes: tuple[str, ...] = ()
    missing_fields: tuple[str, ...] = ()
    config_alias_source: str = ""

    @property
    def ok_for_resolution(self) -> bool:
        return self.completeness in ("complete", "partial")


# Explicit config_alias only when estimator + inference mode are both known.
_ESTIMATOR_INFERENCE_TO_CONFIG: dict[tuple[str, str], str] = {
    ("SCM", "unit_jackknife"): "SCM_UnitJackKnife",
    ("SCM", "UnitJackKnife"): "SCM_UnitJackKnife",
    ("synthetic_control", "unit_jackknife"): "SCM_UnitJackKnife",
    ("SCM", "placebo"): "SCM_Placebo",
    ("SCM", "Placebo"): "SCM_Placebo",
    ("synthetic_control", "placebo"): "SCM_Placebo",
    ("TBRRidge", "kfold"): "TBRRidge_Kfold",
    ("TBRRidge", "Kfold"): "TBRRidge_Kfold",
    ("tbrridge", "kfold"): "TBRRidge_Kfold",
    ("TBRRidge", "block_residual_bootstrap"): "TBRRidge_BlockResidualBootstrap",
    ("TBRRidge", "BlockResidualBootstrap"): "TBRRidge_BlockResidualBootstrap",
    ("tbrridge", "block_residual_bootstrap"): "TBRRidge_BlockResidualBootstrap",
    ("AugSynthCVXPY", "point_only"): "AugSynthCVXPY_Point",
    ("AugSynthCVXPY", "point_estimate"): "AugSynthCVXPY_Point",
    ("augsynth_cvxpy", "point_only"): "AugSynthCVXPY_Point",
    ("DID", "bootstrap"): "DID_Bootstrap",
    ("did", "bootstrap"): "DID_Bootstrap",
}


def extract_resolve_input_from_bundle(
    bundle: Mapping[str, Any],
) -> BundleExtractionResult:
    """Build adapter resolve input from a RunBundle-shaped mapping."""
    evidence = bundle.get("evidence") or {}
    hints = _merge_hints(evidence)
    meta = evidence.get("inference_metadata") or {}
    design = evidence.get("design") or {}
    analysis = meta.get("analysis_contract") or {}

    notes: list[str] = []
    missing: list[str] = []

    spec: dict[str, Any] = {
        "study_id": (
            hints.get("study_id")
            or evidence.get("experiment_id")
            or bundle.get("experiment_id")
            or ""
        ),
        "spec_version": str(hints.get("spec_version") or "1"),
        "modality": str(hints.get("modality") or "geo"),
        "study_purpose": str(hints.get("study_purpose") or "business"),
        "geometry_class": str(
            hints.get("geometry_class")
            or meta.get("geometry_class")
            or "multi_treated_default"
        ),
        "mmm_calibration_intent": bool(
            hints.get("mmm_calibration_intent") or meta.get("mmm_calibration_intent")
        ),
    }

    declared = (
        hints.get("declared_estimand_id")
        or meta.get("declared_estimand_id")
        or design.get("declared_estimand_id")
    )
    if declared:
        spec["declared_estimand_id"] = declared
    else:
        target = (
            hints.get("legacy_target_estimand")
            or hints.get("target_estimand")
            or design.get("target_estimand")
            or meta.get("target_estimand")
            or analysis.get("target_estimand")
        )
        if target:
            spec["legacy_target_estimand"] = str(target)
        policy = (
            hints.get("legacy_aggregation_policy")
            or meta.get("legacy_aggregation_policy")
            or meta.get("aggregation_policy")
        )
        if policy:
            spec["legacy_aggregation_policy"] = str(policy)
        if not target and not spec.get("declared_estimand_id"):
            missing.append("declared_estimand_id")

    interval_exp = (
        hints.get("interval_estimand_expectation_id")
        or meta.get("interval_estimand_expectation_id")
    )
    if interval_exp:
        spec["interval_estimand_expectation_id"] = interval_exp

    transform_ref = hints.get("estimand_transform_ref") or meta.get("estimand_transform_ref")
    if transform_ref:
        spec["estimand_transform_ref"] = transform_ref

    config_alias, alias_source = _resolve_config_alias(hints, meta)
    if not config_alias:
        missing.append("config_alias")
        notes.append(
            "No explicit config_alias and no estimator+inference_mode pair in catalog"
        )

    stub: dict[str, Any] = {
        "config_alias": config_alias,
        "estimator_family": meta.get("estimator_family")
        or hints.get("estimator_family"),
        "inference_method": _inference_method(meta, hints),
        "n_treated": hints.get("n_treated") or meta.get("n_treated"),
        "geometry_observed": hints.get("geometry_observed") or meta.get("geometry_observed"),
        "run_status": str(hints.get("run_status") or meta.get("run_status") or "success"),
        "path_interval_type_legacy": (
            hints.get("path_interval_type_legacy")
            or meta.get("path_interval_type")
            or meta.get("interval_type")
            or meta.get("effect_interval_type")
        ),
        "has_path_intervals": hints.get("has_path_intervals")
        if hints.get("has_path_intervals") is not None
        else meta.get("has_path_intervals"),
        "export_resolver_default": hints.get("export_resolver_default")
        or meta.get("export_resolver_default"),
        "transform_pipeline_attested": hints.get("transform_pipeline_attested")
        if hints.get("transform_pipeline_attested") is not None
        else meta.get("transform_pipeline_attested"),
        "failure_type": hints.get("failure_type") or meta.get("failure_type"),
    }
    if hints.get("heterogeneity_context"):
        spec["heterogeneity_context"] = hints["heterogeneity_context"]
    elif meta.get("heterogeneity_context"):
        spec["heterogeneity_context"] = meta["heterogeneity_context"]

    completeness = _assess_completeness(spec, stub, config_alias, missing)
    if alias_source:
        notes.append(f"config_alias from {alias_source}")

    return BundleExtractionResult(
        input=GeoAdapterResolveInput(spec=spec, run_artifacts_stub=stub),
        completeness=completeness,
        notes=tuple(notes),
        missing_fields=tuple(missing),
        config_alias_source=alias_source,
    )


def extraction_to_sidecar_dict(result: BundleExtractionResult) -> dict[str, Any]:
    """Serialize extraction provenance for ``track_b_views.extraction``."""
    return {
        "completeness": result.completeness,
        "notes": list(result.notes),
        "missing_fields": list(result.missing_fields),
        "config_alias_source": result.config_alias_source,
        "resolved_config_alias": result.input.run_artifacts_stub.get("config_alias"),
    }


def _merge_hints(evidence: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in ("track_b_export_hints",):
        block = evidence.get(key)
        if isinstance(block, Mapping):
            out.update(block)
    artifacts = evidence.get("artifacts")
    if isinstance(artifacts, Mapping):
        nested = artifacts.get("track_b_export_hints")
        if isinstance(nested, Mapping):
            out.update(nested)
    return out


def _inference_method(meta: Mapping[str, Any], hints: Mapping[str, Any]) -> Optional[str]:
    for key in (
        "inference_method",
        "inference_mode",
        "inference_mode_name",
        "inference",
    ):
        val = hints.get(key) or meta.get(key)
        if val:
            return str(val)
    return None


def _resolve_config_alias(
    hints: Mapping[str, Any], meta: Mapping[str, Any]
) -> tuple[str, str]:
    explicit = hints.get("config_alias") or meta.get("config_alias")
    if explicit:
        return str(explicit), "explicit"

    estimator = str(
        hints.get("estimator_name")
        or meta.get("estimator_name")
        or meta.get("estimator_family")
        or ""
    ).strip()
    inference = _inference_method(meta, hints) or ""
    if not estimator or not inference:
        return "", ""

    key = (estimator, inference)
    if key in _ESTIMATOR_INFERENCE_TO_CONFIG:
        return _ESTIMATOR_INFERENCE_TO_CONFIG[key], "estimator+inference_mode"

    norm_inf = inference.replace(" ", "_").lower()
    for (est, inf), alias in _ESTIMATOR_INFERENCE_TO_CONFIG.items():
        if est.lower() == estimator.lower() and inf.lower() == norm_inf:
            return alias, "estimator+inference_mode_normalized"

    return "", ""


def _assess_completeness(
    spec: Mapping[str, Any],
    stub: Mapping[str, Any],
    config_alias: str,
    missing: list[str],
) -> ExtractionCompleteness:
    if not config_alias:
        return "blocked"
    if missing and not spec.get("declared_estimand_id") and not spec.get(
        "legacy_target_estimand"
    ):
        return "blocked"
    if stub.get("config_alias") == "SCM_Placebo":
        inst_geo = "single_treated_only"
        spec_geo = spec.get("geometry_class")
        observed = stub.get("geometry_observed") or spec_geo
        if observed != inst_geo or stub.get("run_status") != "success":
            return "partial"
    return "complete"
