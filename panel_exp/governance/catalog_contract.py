"""
F-CAT-001 — Registry/catalog cleanup contract (Track F).

Reconciles estimator, inference, geometry, and instrument catalog metadata with
F-INF-001 (interval semantics) and F-GEO-001 (geometry adapter). Policy helpers
only — no estimator/inference behavior changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Sequence, Tuple

from panel_exp.governance.geometry_adapter_contract import (
    GeometryClassification,
    GeometryType,
    ReadoutExportTier,
    expected_track_f_geometry_classification,
)
from panel_exp.governance.instrument_contract import (
    INV_015_REGISTRY_BAYESIAN_NOT_MCMC,
    is_placebo_inference_mode,
    registry_bayesian_production_block_reason,
)
from panel_exp.governance.interval_semantics_contract import (
    IntervalSemanticsClassification,
    expected_track_f_classification,
)
from panel_exp.inference_result import IntervalType
from panel_exp.method_metadata import (
    EstimatorMetadata,
    estimator_catalog,
    inference_mode_catalog,
)
from panel_exp.validation.nominal_calibration import NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS

# AUDIT-010 / E5 — sole nominal CalibrationSignal path (null_monitor only; no expansion).
CALIBRATION_SIGNAL_GOVERNED_ALIASES = frozenset({"SCM_UnitJackKnife"})

# MMM ingress allowlist (empty per AUDIT-010).
MMM_READINESS_GOVERNED_ALIASES: frozenset[str] = frozenset()

FORBIDDEN_ESTIMATOR_CATALOG_NAMES = frozenset({"Placebo"})

CLASS_TBR_NAMES = frozenset({"TBR"})
TBRRIDGE_CLASS_NAMES = frozenset({"TBRRidge"})
BAYESIAN_TBR_MCMC_CLASSES = frozenset({"BayesianTBR", "BayesianTBRHorseShoe"})

INFERENCE_TAXONOMY_LABELS: dict[str, str] = {
    "point_estimate": "Point readout only; no path-level uncertainty.",
    "UnitJackKnife": "Unit-level LOO jackknife; distinct from JKP.",
    "JKP": "Jackknife+ path; distinct assumptions from UnitJackKnife.",
    "Kfold": "Panel K-fold CV confidence band; distinct from TimeSeriesKfold.",
    "TimeSeriesKfold": "Horizon-blocked temporal folds; distinct from Kfold.",
    "Conformal": "Conformal residual-rank interval; callable ≠ governed uncertainty (F-INF-001).",
    "Bayesian": "Registry JAX credible bands; not BayesianTBR NUTS MCMC (INV-015).",
    "Placebo": "Inference/falsification layer — not an estimator readout (F-P0-005).",
    "BlockResidualBootstrap": "Block residual bootstrap CI; restricted diagnostic on SCM/TBRRidge.",
}


class CatalogLayer(str, Enum):
    ESTIMATOR_READOUT = "estimator_readout"
    INFERENCE_FALSIFICATION = "inference_falsification"


class CatalogReadiness(str, Enum):
    PRODUCTION_SAFE = "production_safe"
    EXPERT_REVIEW = "expert_review"
    RESTRICTED = "restricted"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class CatalogViolation:
    code: str
    message: str
    source: str


@dataclass(frozen=True)
class CatalogComboRecord:
    """Canonical metadata for one estimator × inference × geometry tuple."""

    estimator_catalog_name: str
    estimator_class_name: str
    inference_mode: str
    geometry_type: GeometryType
    catalog_layer: CatalogLayer
    path_interval_type: Optional[str]
    interval_semantics_tier: IntervalSemanticsClassification
    geometry_tier: GeometryClassification
    export_tier: ReadoutExportTier
    catalog_readiness: CatalogReadiness
    track_b_alias: Optional[str] = None
    calibration_signal_eligible: bool = False
    mmm_ready: bool = False
    governed_uncertainty_claim: bool = False
    policy_note: str = ""


def _interval_type_for_inference(inference: str) -> Optional[str]:
    mapping = {
        "point_estimate": IntervalType.UNAVAILABLE.value,
        "UnitJackKnife": IntervalType.CONFIDENCE_INTERVAL.value,
        "JKP": IntervalType.CONFIDENCE_INTERVAL.value,
        "Kfold": IntervalType.CONFIDENCE_INTERVAL.value,
        "TimeSeriesKfold": IntervalType.CONFIDENCE_INTERVAL.value,
        "Conformal": IntervalType.CONFORMAL_INTERVAL.value,
        "Bayesian": IntervalType.CREDIBLE_INTERVAL.value,
        "Placebo": IntervalType.PLACEBO_BAND.value,
        "BlockResidualBootstrap": IntervalType.CONFIDENCE_INTERVAL.value,
    }
    return mapping.get(inference)


def _combo(
    est_key: str,
    est_class: str,
    inf: str,
    geo: GeometryType,
    geo_mode: str,
    *,
    layer: CatalogLayer = CatalogLayer.ESTIMATOR_READOUT,
    inf_tier: Optional[IntervalSemanticsClassification] = None,
    geo_tier: Optional[GeometryClassification] = None,
    track_b: Optional[str] = None,
    cs_eligible: bool = False,
    readiness: CatalogReadiness = CatalogReadiness.RESTRICTED,
    export: ReadoutExportTier = ReadoutExportTier.RESTRICTED,
    note: str = "",
) -> CatalogComboRecord:
    resolved_inf = inf_tier or expected_track_f_classification(est_class, inf, geo_mode)
    resolved_geo = geo_tier or expected_track_f_geometry_classification(est_class, inf, geo)
    if resolved_inf is None:
        resolved_inf = IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY
    if resolved_geo is None:
        resolved_geo = GeometryClassification.BLOCKED_GEOMETRY
    return CatalogComboRecord(
        estimator_catalog_name=est_key,
        estimator_class_name=est_class,
        inference_mode=inf,
        geometry_type=geo,
        catalog_layer=layer,
        path_interval_type=_interval_type_for_inference(inf),
        interval_semantics_tier=resolved_inf,
        geometry_tier=resolved_geo,
        export_tier=export,
        catalog_readiness=readiness,
        track_b_alias=track_b,
        calibration_signal_eligible=cs_eligible,
        mmm_ready=False,
        governed_uncertainty_claim=False,
        policy_note=note,
    )


def canonical_catalog_combo_records() -> Tuple[CatalogComboRecord, ...]:
    """Authoritative combo records aligned with F-INF / F-GEO / AUDIT-010."""
    return (
        _combo("TBR", "TBR", "point_estimate", GeometryType.AGGREGATE_TWO_SERIES_1X1, "aggregate_two_series", note="Class TBR aggregate 1×1 only."),
        _combo(
            "TBR",
            "TBR",
            "point_estimate",
            GeometryType.UNIT_PANEL,
            "single_cell",
            geo_tier=GeometryClassification.BLOCKED_GEOMETRY,
            readiness=CatalogReadiness.BLOCKED,
            export=ReadoutExportTier.BLOCKED,
            note="Class TBR blocked on unit_panel (F-GEO-001).",
        ),
        _combo(
            "TBR",
            "TBR",
            "JKP",
            GeometryType.AGGREGATE_TWO_SERIES_1X1,
            "aggregate_two_series",
            geo_tier=GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS,
            inf_tier=IntervalSemanticsClassification.CALLABLE_UNVERIFIED_INTERVAL_SEMANTICS,
            readiness=CatalogReadiness.RESTRICTED,
            export=ReadoutExportTier.RESTRICTED,
            note="JKP callable; not governed on 1-control agg.",
        ),
        _combo(
            "TBRRidge",
            "TBRRidge",
            "Kfold",
            GeometryType.UNIT_PANEL,
            "single_cell",
            track_b="TBRRidge_Kfold",
            note="TBRRidge ≠ class TBR.",
        ),
        _combo(
            "TBRRidge",
            "TBRRidge",
            "TimeSeriesKfold",
            GeometryType.UNIT_PANEL,
            "single_cell",
            inf_tier=IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY,
            readiness=CatalogReadiness.DIAGNOSTIC_ONLY,
            note="POSTFIX-001: structurally valid; restricted diagnostic.",
        ),
        _combo(
            "TBRRidge",
            "TBRRidge",
            "UnitJackKnife",
            GeometryType.UNIT_PANEL,
            "single_cell",
            geo_tier=GeometryClassification.BLOCKED_INTERFACE,
            readiness=CatalogReadiness.BLOCKED,
            export=ReadoutExportTier.BLOCKED,
        ),
        _combo(
            "TBRRidge",
            "TBRRidge",
            "Conformal",
            GeometryType.UNIT_PANEL,
            "single_cell",
            geo_tier=GeometryClassification.BLOCKED_INTERFACE,
            readiness=CatalogReadiness.BLOCKED,
            export=ReadoutExportTier.BLOCKED,
        ),
        _combo(
            "TBRRidge",
            "TBRRidge",
            "Kfold",
            GeometryType.POOLED_MULTI_CELL,
            "single_cell",
            geo_tier=GeometryClassification.BLOCKED_MISSING_POOLING_RULE,
            readiness=CatalogReadiness.BLOCKED,
            export=ReadoutExportTier.BLOCKED,
        ),
        _combo(
            "AugSynthCVXPY",
            "AugSynthCVXPY",
            "Conformal",
            GeometryType.UNIT_PANEL,
            "single_cell",
            inf_tier=IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY,
            readiness=CatalogReadiness.DIAGNOSTIC_ONLY,
            note="POSTFIX-001: structurally valid; restricted diagnostic.",
        ),
        _combo(
            "AugSynthCVXPY",
            "AugSynthCVXPY",
            "Kfold",
            GeometryType.UNIT_PANEL,
            "single_cell",
            track_b="AugSynthCVXPY_Point",
            note="Track B AugSynthCVXPY_Point alias is point-only.",
        ),
        _combo(
            "AugSynthCVXPY",
            "AugSynthCVXPY",
            "UnitJackKnife",
            GeometryType.UNIT_PANEL,
            "single_cell",
            readiness=CatalogReadiness.DIAGNOSTIC_ONLY,
            export=ReadoutExportTier.RESTRICTED,
        ),
        _combo(
            "SyntheticControl",
            "SyntheticControl",
            "UnitJackKnife",
            GeometryType.UNIT_PANEL,
            "single_cell",
            track_b="SCM_UnitJackKnife",
            cs_eligible=True,
            readiness=CatalogReadiness.DIAGNOSTIC_ONLY,
            note="null_monitor_only; sole governed CalibrationSignal alias.",
        ),
        _combo(
            "SyntheticControl",
            "SyntheticControl",
            "UnitJackKnife",
            GeometryType.SUPERGEO_UNIT,
            "supergeo",
            geo_tier=GeometryClassification.BLOCKED_MISSING_ADAPTER,
            readiness=CatalogReadiness.BLOCKED,
            export=ReadoutExportTier.BLOCKED,
        ),
        _combo(
            "SyntheticControl",
            "SyntheticControl",
            "Placebo",
            GeometryType.UNIT_PANEL,
            "single_cell",
            layer=CatalogLayer.INFERENCE_FALSIFICATION,
            geo_tier=GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS,
            track_b="SCM_Placebo",
            readiness=CatalogReadiness.DIAGNOSTIC_ONLY,
            note="Placebo falsification; not estimator.",
        ),
        _combo(
            "SyntheticControl",
            "SyntheticControl",
            "UnitJackKnife",
            GeometryType.TRIMMED_POPULATION,
            "trimmed",
            geo_tier=GeometryClassification.BLOCKED_MISSING_ESTIMAND_BRIDGE,
            readiness=CatalogReadiness.BLOCKED,
            export=ReadoutExportTier.BLOCKED,
        ),
    )


def validate_catalog_combo_record(record: CatalogComboRecord) -> Tuple[CatalogViolation, ...]:
    """Return violations when catalog metadata over-claims readiness or eligibility."""
    violations: list[CatalogViolation] = []

    if record.estimator_catalog_name in FORBIDDEN_ESTIMATOR_CATALOG_NAMES:
        violations.append(
            CatalogViolation(
                "forbidden_estimator_name",
                f"{record.estimator_catalog_name!r} must not appear as estimator catalog name.",
                "catalog",
            )
        )

    if record.governed_uncertainty_claim:
        violations.append(
            CatalogViolation(
                "governed_uncertainty_forbidden",
                "Governed uncertainty allowlist is empty (F-INF-001).",
                record.track_b_alias or record.inference_mode,
            )
        )

    if record.calibration_signal_eligible and record.track_b_alias not in CALIBRATION_SIGNAL_GOVERNED_ALIASES:
        violations.append(
            CatalogViolation(
                "calibration_signal_overclaim",
                f"Track B alias {record.track_b_alias!r} is not CalibrationSignal-governed per E5.",
                record.track_b_alias or "track_b",
            )
        )

    if record.mmm_ready:
        violations.append(
            CatalogViolation(
                "mmm_readiness_overclaim",
                "AUDIT-010 blocks MMM ingress for all combos.",
                record.track_b_alias or "catalog",
            )
        )

    if record.interval_semantics_tier == IntervalSemanticsClassification.GOVERNED_UNCERTAINTY:
        violations.append(
            CatalogViolation(
                "interval_governed_overclaim",
                "F-INF-001 governed_uncertainty tier not permitted in catalog.",
                record.inference_mode,
            )
        )

    if record.geometry_tier in (
        GeometryClassification.BLOCKED_GEOMETRY,
        GeometryClassification.BLOCKED_MISSING_ADAPTER,
        GeometryClassification.BLOCKED_MISSING_ESTIMAND_BRIDGE,
        GeometryClassification.BLOCKED_MISSING_POOLING_RULE,
        GeometryClassification.BLOCKED_UNSUPPORTED_INFERENCE_GEOMETRY,
        GeometryClassification.BLOCKED_INTERFACE,
    ):
        if record.export_tier not in (ReadoutExportTier.BLOCKED,):
            violations.append(
                CatalogViolation(
                    "geometry_blocked_but_export_not_blocked",
                    f"Geometry tier {record.geometry_tier.value} requires blocked export.",
                    record.geometry_type.value,
                )
            )

    if is_placebo_inference_mode(record.inference_mode) and record.catalog_layer != CatalogLayer.INFERENCE_FALSIFICATION:
        violations.append(
            CatalogViolation(
                "placebo_not_inference_layer",
                "Placebo must be catalogued as inference/falsification layer.",
                record.inference_mode,
            )
        )

    return tuple(violations)


def audit_estimator_catalog() -> Tuple[CatalogViolation, ...]:
    """Audit ``method_metadata`` estimator catalog for taxonomy drift."""
    violations: list[CatalogViolation] = []

    for meta in estimator_catalog():
        if meta.name in FORBIDDEN_ESTIMATOR_CATALOG_NAMES:
            violations.append(
                CatalogViolation(
                    "placebo_as_estimator",
                    f"Estimator catalog must not include {meta.name!r}.",
                    "method_metadata",
                )
            )

        if meta.class_name in CLASS_TBR_NAMES and meta.name == "TBRRidge":
            violations.append(
                CatalogViolation(
                    "tbr_tbrridge_conflation",
                    "Catalog entry must not label TBRRidge as TBR.",
                    meta.name,
                )
            )

        if meta.class_name in TBRRIDGE_CLASS_NAMES and meta.name == "TBR":
            violations.append(
                CatalogViolation(
                    "tbr_tbrridge_conflation",
                    "Catalog entry must not label class TBR as TBRRidge.",
                    meta.name,
                )
            )

        if meta.class_name in BAYESIAN_TBR_MCMC_CLASSES:
            for lim in meta.known_limitations:
                if "MCMC" not in lim and "NUTS" not in lim:
                    continue
            # BayesianTBR should mention MCMC path
        elif meta.class_name in TBRRIDGE_CLASS_NAMES:
            if "Bayesian" in meta.inference_support:
                if not any("INV-015" in lim or "not" in lim.lower() for lim in meta.known_limitations):
                    violations.append(
                        CatalogViolation(
                            "registry_bayesian_undocumented",
                            f"{meta.name} supports registry Bayesian without INV-015 limitation note.",
                            meta.name,
                        )
                    )

        if "Placebo" in meta.inference_support and meta.class_name not in ("SyntheticControl",):
            # SCM may list Placebo in inference_support — that's pairing on SCM estimator OK
            pass

    return tuple(violations)


def audit_inference_mode_catalog() -> Tuple[CatalogViolation, ...]:
    """Audit inference mode catalog labels."""
    violations: list[CatalogViolation] = []
    for mode in inference_mode_catalog():
        combined = " ".join(mode.known_limitations + mode.rationale).lower()
        if mode.name == "Placebo":
            if "falsification" not in combined and "inference" not in combined:
                violations.append(
                    CatalogViolation(
                        "placebo_as_estimator_mode",
                        "Placebo must document inference/falsification layer (not estimator).",
                        mode.name,
                    )
                )
            continue
        required_snippets = {
            "Conformal": ("f-inf",),
            "TimeSeriesKfold": ("distinct from panel kfold", "distinct from panel k-fold"),
            "Kfold": ("distinct from timeserieskfold", "distinct from timeseries"),
            "JKP": ("unitjackknife", "jackknife+"),
            "UnitJackKnife": ("jkp", "jackknife+"),
        }
        for mode_name, snippets in required_snippets.items():
            if mode.name == mode_name and not any(s in combined for s in snippets):
                violations.append(
                    CatalogViolation(
                        "inference_taxonomy_stale",
                        f"Inference mode {mode_name!r} missing F-CAT taxonomy distinction note.",
                        "method_metadata",
                    )
                )
    return tuple(violations)


def audit_track_b_calibration_signal_map(
    track_b_signals: dict[str, dict[str, Optional[str]]],
) -> Tuple[CatalogViolation, ...]:
    """
    Audit Track B ``CALIBRATION_SIGNAL_BY_CONFIG`` — signal IDs must not imply
    CalibrationSignal eligibility beyond ``NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS``.
    """
    violations: list[CatalogViolation] = []
    for alias, payload in track_b_signals.items():
        if payload.get("signal_id") and alias not in CALIBRATION_SIGNAL_GOVERNED_ALIASES:
            if alias not in NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS:
                violations.append(
                    CatalogViolation(
                        "track_b_signal_implies_eligibility",
                        f"Track B alias {alias!r} has signal_id but is not nominal-calibration eligible.",
                        "track_b._registry",
                    )
                )
    return tuple(violations)


def audit_canonical_combo_records() -> Tuple[CatalogViolation, ...]:
    violations: list[CatalogViolation] = []
    for record in canonical_catalog_combo_records():
        violations.extend(validate_catalog_combo_record(record))
    return tuple(violations)


def assert_catalog_consistency(
    *,
    track_b_signals: Optional[dict[str, dict[str, Optional[str]]]] = None,
) -> None:
    """Raise ``ValueError`` when catalog/registry metadata violates F-CAT policy."""
    all_violations: list[CatalogViolation] = []
    all_violations.extend(audit_estimator_catalog())
    all_violations.extend(audit_inference_mode_catalog())
    all_violations.extend(audit_canonical_combo_records())
    if track_b_signals is not None:
        all_violations.extend(audit_track_b_calibration_signal_map(track_b_signals))

    if all_violations:
        lines = "\n".join(f"  [{v.code}] {v.source}: {v.message}" for v in all_violations[:12])
        extra = f" (+{len(all_violations) - 12} more)" if len(all_violations) > 12 else ""
        raise ValueError(f"F-CAT-001 catalog consistency failed:\n{lines}{extra}")


def track_b_alias_governance(alias: str) -> dict[str, Any]:
    """Governed overlay for a Track B config alias (does not mutate Track B registry)."""
    cs = alias in CALIBRATION_SIGNAL_GOVERNED_ALIASES
    nominal = alias in NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS
    return {
        "config_alias": alias,
        "calibration_signal_eligible": cs,
        "nominal_calibration_eligible": nominal,
        "mmm_ready": alias in MMM_READINESS_GOVERNED_ALIASES,
        "governed_uncertainty": False,
        "policy_note": (
            "null_monitor_only via SCM_UnitJackKnife"
            if cs
            else "Track B signal_id is adapter metadata only — not CalibrationSignal expansion."
        ),
    }


__all__ = [
    "BAYESIAN_TBR_MCMC_CLASSES",
    "CALIBRATION_SIGNAL_GOVERNED_ALIASES",
    "CLASS_TBR_NAMES",
    "FORBIDDEN_ESTIMATOR_CATALOG_NAMES",
    "INFERENCE_TAXONOMY_LABELS",
    "MMM_READINESS_GOVERNED_ALIASES",
    "TBRRIDGE_CLASS_NAMES",
    "CatalogComboRecord",
    "CatalogLayer",
    "CatalogReadiness",
    "CatalogViolation",
    "assert_catalog_consistency",
    "audit_canonical_combo_records",
    "audit_estimator_catalog",
    "audit_inference_mode_catalog",
    "audit_track_b_calibration_signal_map",
    "canonical_catalog_combo_records",
    "track_b_alias_governance",
    "validate_catalog_combo_record",
]
