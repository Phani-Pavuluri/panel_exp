"""
TRUSTREPORT-DECISION-INPUTS-WIRING-001 — Build TrustReportDecisionInputs from run bundles.

Maps explicit bundle metadata (inference_metadata, track_b_export_hints) to
F-DECISION readout evidence records. Does not infer missing scientific facts.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

from panel_exp.governance.decision_policy import (
    DataProfile,
    DesignProfile,
    EstimandProfile,
    GeometryProfile,
)
from panel_exp.governance.geometry_adapter_contract import GeometryType
from panel_exp.governance.interval_semantics_contract import IntervalReadout
from panel_exp.track_b.bundle_extract import (
    _ESTIMATOR_INFERENCE_TO_CONFIG,
    _inference_method,
    extract_resolve_input_from_bundle,
)
from panel_exp.track_b.f_decision_context import TrustReportDecisionInputs

ReadoutEvidenceMapping = dict[str, Any]

_CONFIG_ALIAS_TO_PAIR: dict[str, tuple[str, str]] = {}
for (est, inf), alias in _ESTIMATOR_INFERENCE_TO_CONFIG.items():
    _CONFIG_ALIAS_TO_PAIR.setdefault(alias, (est, inf))

_INFERENCE_CANONICAL: dict[str, str] = {
    "unit_jackknife": "UnitJackKnife",
    "unitjackknife": "UnitJackKnife",
    "kfold": "Kfold",
    "placebo": "Placebo",
    "conformal": "Conformal",
    "timeserieskfold": "TimeSeriesKfold",
    "time_series_kfold": "TimeSeriesKfold",
    "jkp": "JKP",
    "block_residual_bootstrap": "BlockResidualBootstrap",
    "point_estimate": "point_estimate",
    "point_only": "point_estimate",
    "bootstrap": "bootstrap",
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


def _canonical_inference(mode: str) -> str:
    key = mode.strip().replace(" ", "_")
    if key in _INFERENCE_CANONICAL:
        return _INFERENCE_CANONICAL[key]
    if key in _INFERENCE_CANONICAL.values():
        return key
    # Title-case heuristic for registry modes (UnitJackKnife, TimeSeriesKfold)
    if "_" in key:
        parts = key.split("_")
        return "".join(p[:1].upper() + p[1:].lower() for p in parts if p)
    return key[:1].upper() + key[1:] if key else key


def _point_effect_from_mapping(m: Mapping[str, Any]) -> Optional[float]:
    for key in (
        "point_effect",
        "point_estimate",
        "att_post",
        "cumulative_att_post",
        "effect_post_test",
        "relative_att_post",
        "lift_point",
    ):
        val = m.get(key)
        if val is None:
            continue
        try:
            return float(val)
        except (TypeError, ValueError):
            continue
    return None


def _interval_readout_from_mapping(m: Mapping[str, Any]) -> Optional[IntervalReadout]:
    raw = m.get("interval_readout")
    if isinstance(raw, IntervalReadout):
        return raw
    snap = m.get("interval_readout_snapshot")
    if not isinstance(snap, Mapping):
        return None
    try:
        import numpy as np

        y = np.asarray(snap.get("y"), dtype=float)
        y_hat = np.asarray(snap.get("y_hat"), dtype=float)
        y_lower = np.asarray(snap.get("y_lower"), dtype=float)
        y_upper = np.asarray(snap.get("y_upper"), dtype=float)
        if y.size == 0:
            return None
        return IntervalReadout(
            estimator_name=str(m.get("estimator_name", "")),
            inference_mode=str(m.get("inference_mode", "")),
            geometry_mode=str(snap.get("geometry_mode") or m.get("geometry_mode") or ""),
            path_interval_type=snap.get("path_interval_type"),
            y=y,
            y_hat=y_hat,
            y_lower=y_lower,
            y_upper=y_upper,
            test_length=int(snap.get("test_length") or y.size),
            null_interval_exclusion_rate=float(snap.get("null_interval_exclusion_rate") or 0.0),
        )
    except (TypeError, ValueError):
        return None


def normalize_readout_evidence_record(m: Mapping[str, Any]) -> tuple[Optional[ReadoutEvidenceMapping], list[str]]:
    """Normalize one readout evidence mapping; warn on missing required keys."""
    warnings: list[str] = []
    est = m.get("estimator_name")
    inf = m.get("inference_mode")
    alias = m.get("track_b_config_alias") or m.get("config_alias")

    if (not est or not inf) and alias:
        pair = _CONFIG_ALIAS_TO_PAIR.get(str(alias))
        if pair:
            est, inf = pair
        else:
            warnings.append(
                f"decision_context_incomplete: unmapped config_alias {alias!r}"
            )

    if not est or not inf:
        warnings.append(
            "decision_context_incomplete: missing estimator_name or inference_mode"
        )
        return None, warnings

    record: ReadoutEvidenceMapping = {
        "estimator_name": str(est),
        "inference_mode": _canonical_inference(str(inf)),
        "callable": bool(m.get("callable", m.get("run_status", "success") == "success")),
    }
    if m.get("geometry_mode"):
        record["geometry_mode"] = str(m["geometry_mode"])
    if m.get("audit_010_primary_bucket"):
        record["audit_010_primary_bucket"] = str(m["audit_010_primary_bucket"])
    if alias:
        record["track_b_config_alias"] = str(alias)
    pe = _point_effect_from_mapping(m)
    if pe is not None:
        record["point_effect"] = pe
    if m.get("falsification_passed") is not None:
        record["falsification_passed"] = bool(m["falsification_passed"])
    if m.get("research_only") is not None:
        record["research_only"] = bool(m["research_only"])
    ir = _interval_readout_from_mapping(m)
    if ir is not None:
        record["interval_readout"] = ir
    return record, warnings


def _explicit_readout_lists(
    hints: Mapping[str, Any],
    meta: Mapping[str, Any],
    artifacts: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    out: list[Mapping[str, Any]] = []
    for container in (hints, meta, artifacts):
        for key in ("readout_evidence", "decision_readout_evidence"):
            raw = container.get(key)
            if isinstance(raw, list):
                for item in raw:
                    if isinstance(item, Mapping):
                        out.append(item)
    return out


def _primary_readout_record(
    hints: Mapping[str, Any],
    meta: Mapping[str, Any],
    stub: Mapping[str, Any],
) -> tuple[Optional[ReadoutEvidenceMapping], list[str]]:
    warnings: list[str] = []
    alias = hints.get("config_alias") or meta.get("config_alias") or stub.get("config_alias")
    est: Optional[str] = None
    inf: Optional[str] = None
    if alias and str(alias) in _CONFIG_ALIAS_TO_PAIR:
        est, inf = _CONFIG_ALIAS_TO_PAIR[str(alias)]
    if not est or not inf:
        est = (
            hints.get("estimator_name")
            or meta.get("estimator_name")
            or meta.get("estimator_family")
            or stub.get("estimator_family")
        )
        inf = _inference_method(meta, hints) or stub.get("inference_method")
    if (not est or not inf) and alias:
        pair = _CONFIG_ALIAS_TO_PAIR.get(str(alias))
        if pair:
            est, inf = pair

    if not est or not inf:
        return None, warnings

    record: ReadoutEvidenceMapping = {
        "estimator_name": str(est),
        "inference_mode": _canonical_inference(str(inf)),
        "callable": str(hints.get("run_status") or meta.get("run_status") or stub.get("run_status") or "success")
        == "success",
    }
    if alias:
        record["track_b_config_alias"] = str(alias)
    for key in ("audit_010_primary_bucket", "audit_010_bucket", "governance_bucket"):
        if hints.get(key) or meta.get(key):
            record["audit_010_primary_bucket"] = str(hints.get(key) or meta.get(key))
            break
    if hints.get("geometry_observed") or meta.get("geometry_observed"):
        record["geometry_mode"] = str(hints.get("geometry_observed") or meta.get("geometry_observed"))
    pe = _point_effect_from_mapping(hints) or _point_effect_from_mapping(meta)
    if pe is not None:
        record["point_effect"] = pe
    for key in ("falsification_passed", "placebo_passed"):
        if hints.get(key) is not None:
            record["falsification_passed"] = bool(hints[key])
            break
        if meta.get(key) is not None:
            record["falsification_passed"] = bool(meta[key])
            break
    ir = _interval_readout_from_mapping(hints) or _interval_readout_from_mapping(meta)
    if ir is not None:
        record["interval_readout"] = ir
    return record, warnings


def _geometry_type_from_hints(
    hints: Mapping[str, Any],
    meta: Mapping[str, Any],
    data: DataProfile,
) -> GeometryType:
    if hints.get("pooled_multi_cell") or hints.get("pooled_claim"):
        return GeometryType.POOLED_MULTI_CELL
    geo = str(
        hints.get("geometry_type")
        or hints.get("geometry_observed")
        or meta.get("geometry_type")
        or hints.get("geometry_class")
        or meta.get("geometry_class")
        or ""
    ).lower()
    if "supergeo" in geo:
        return GeometryType.SUPERGEO_UNIT
    if "trim" in geo:
        return GeometryType.TRIMMED_POPULATION
    if "aggregate" in geo and data.n_treated == 1 and data.n_control == 1:
        return GeometryType.AGGREGATE_TWO_SERIES_1X1
    if data.n_test_grps > 1:
        return GeometryType.MULTI_CELL_PER_CELL
    return GeometryType.UNIT_PANEL


def extract_readout_evidence_from_bundle(
    bundle: Mapping[str, Any],
) -> tuple[list[ReadoutEvidenceMapping], list[str]]:
    """
    Extract readout evidence dicts from a RunBundle-shaped mapping.

    Sources (in order): explicit ``readout_evidence`` lists in hints/meta/artifacts,
    then primary run metadata from inference_metadata + export hints.
    """
    evidence = bundle.get("evidence") or {}
    hints = _merge_hints(evidence)
    meta = evidence.get("inference_metadata") or {}
    if not isinstance(meta, Mapping):
        meta = {}
    artifacts = evidence.get("artifacts") or {}
    if not isinstance(artifacts, Mapping):
        artifacts = {}

    warnings: list[str] = []
    specs: list[ReadoutEvidenceMapping] = []
    seen: set[tuple[str, str]] = set()
    explicit_raw = _explicit_readout_lists(hints, meta, artifacts)

    for raw in explicit_raw:
        rec, rec_warns = normalize_readout_evidence_record(raw)
        warnings.extend(rec_warns)
        if rec is None:
            continue
        key = (rec["estimator_name"], rec["inference_mode"])
        if key in seen:
            continue
        seen.add(key)
        specs.append(rec)

    if not explicit_raw:
        extracted = extract_resolve_input_from_bundle(bundle)
        stub = extracted.input.run_artifacts_stub
        primary, prim_warns = _primary_readout_record(hints, meta, stub)
        warnings.extend(prim_warns)
        if primary is not None:
            key = (primary["estimator_name"], primary["inference_mode"])
            if key not in seen:
                seen.add(key)
                specs.append(primary)
            pair = _CONFIG_ALIAS_TO_PAIR.get(
                str(primary.get("track_b_config_alias") or "")
            )
            if pair is None and not primary.get("track_b_config_alias"):
                warnings.append(
                    "decision_context_incomplete: unmapped estimator+inference pair"
                )

    if not specs:
        warnings.append(
            "decision_context_incomplete: no readout_evidence from bundle metadata"
        )
    return specs, warnings


def build_decision_profiles_from_bundle(
    bundle: Mapping[str, Any],
) -> tuple[DesignProfile, DataProfile, GeometryProfile, EstimandProfile, list[str]]:
    """Build F-DECISION profiles from bundle extraction (no inference)."""
    warnings: list[str] = []
    evidence = bundle.get("evidence") or {}
    hints = _merge_hints(evidence)
    meta = evidence.get("inference_metadata") or {}
    if not isinstance(meta, Mapping):
        meta = {}

    extracted = extract_resolve_input_from_bundle(bundle)
    spec = extracted.input.spec
    stub = extracted.input.run_artifacts_stub

    n_treated = hints.get("n_treated") or meta.get("n_treated") or stub.get("n_treated")
    n_control = hints.get("n_control") or meta.get("n_control")
    n_test_grps = hints.get("n_test_grps") or meta.get("n_test_grps") or 1

    try:
        nt = int(n_treated) if n_treated is not None else 1
    except (TypeError, ValueError):
        nt = 1
        warnings.append("decision_context_incomplete: invalid n_treated")
    try:
        nc = int(n_control) if n_control is not None else 8
    except (TypeError, ValueError):
        nc = 8
        warnings.append("decision_context_incomplete: invalid n_control")
    if n_control is None:
        warnings.append("decision_context_incomplete: n_control not in bundle — using default 8")
    try:
        ngrp = int(n_test_grps)
    except (TypeError, ValueError):
        ngrp = 1

    data = DataProfile(n_treated=nt, n_control=nc, n_test_grps=ngrp)
    geometry_type = _geometry_type_from_hints(hints, meta, data)
    geometry = GeometryProfile(
        geometry_type=geometry_type,
        supergeo_adapter_id=hints.get("supergeo_adapter_id") or meta.get("supergeo_adapter_id"),
        trim_estimand_bridge_id=hints.get("trim_estimand_bridge_id")
        or meta.get("trim_estimand_bridge_id"),
        pooled_claim=bool(hints.get("pooled_claim") or hints.get("pooled_multi_cell")),
        single_treated_geometry=bool(hints.get("single_treated_geometry"))
        or nt == 1,
    )

    design = DesignProfile(
        design_method_id=str(
            hints.get("design_method_id") or meta.get("design_method_id") or "unknown"
        ),
        track_b_allows_primary_null_monitor=bool(
            hints.get("track_b_allows_primary_null_monitor", True)
        ),
        pooling_rule_id=hints.get("pooling_rule_id") or meta.get("pooling_rule_id"),
    )

    estimand_id = (
        spec.get("declared_estimand_id")
        or hints.get("declared_estimand_id")
        or meta.get("declared_estimand_id")
        or "unit_level_att"
    )
    estimand = EstimandProfile(target_estimand=str(estimand_id))

    return design, data, geometry, estimand, warnings


def build_trust_report_decision_inputs_from_bundle(
    bundle: Mapping[str, Any],
    *,
    strict: bool = False,
    allow_sensitivity_in_comparison: bool = False,
) -> TrustReportDecisionInputs:
    """Assemble ``TrustReportDecisionInputs`` from bundle metadata."""
    readouts, readout_warnings = extract_readout_evidence_from_bundle(bundle)
    design, data, geometry, estimand, profile_warnings = build_decision_profiles_from_bundle(
        bundle
    )
    extraction_warnings = tuple(readout_warnings + profile_warnings)
    return TrustReportDecisionInputs(
        readout_evidence=readouts,
        design=design,
        data=data,
        geometry=geometry,
        estimand=estimand,
        strict=strict,
        allow_sensitivity_in_comparison=allow_sensitivity_in_comparison,
        extraction_warnings=extraction_warnings,
    )
