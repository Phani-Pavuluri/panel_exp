"""
F-GEO-001 — Geometry adapter contract (Track F).

Defines governed geometry support rules so estimator × inference readouts cannot
be used on unsupported geometries. Callable inference (F-INF-001) does **not**
imply geometry support; interval semantics never override geometry blocking.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Tuple

from panel_exp.governance.instrument_contract import (
    MULTI_CELL_POOLED_WITHOUT_RULE,
    is_placebo_inference_mode,
    multi_cell_pooling_block_reason,
)
from panel_exp.governance.interval_semantics_contract import (
    IntervalSemanticsClassification,
    IntervalSemanticsVerdict,
)

# Stable issue / reason codes.
GEOMETRY_UNIT_PANEL_REQUIRED = "geometry_unit_panel_required"
GEOMETRY_AGGREGATE_1X1_REQUIRED = "geometry_aggregate_1x1_required"
GEOMETRY_SINGLE_TREATED_REQUIRED = "geometry_single_treated_required"
GEOMETRY_PER_CELL_ONLY = "geometry_per_cell_only"
GEOMETRY_SUPERGEO_ADAPTER_REQUIRED = "geometry_supergeo_adapter_required"
GEOMETRY_TRIM_ESTIMAND_BRIDGE_REQUIRED = "geometry_trim_estimand_bridge_required"
GEOMETRY_DID_POLICY_DEFERRED = "geometry_did_policy_deferred"
GEOMETRY_PLACEBO_INFERENCE_LAYER = "geometry_placebo_inference_layer"
CALLABLE_DOES_NOT_IMPLY_GEOMETRY = "callable_does_not_imply_geometry_support"


class GeometryType(str, Enum):
    """Governed geometry types for readout classification."""

    UNIT_PANEL = "unit_panel"
    AGGREGATE_TWO_SERIES_1X1 = "aggregate_two_series_1x1"
    AGGREGATE_TWO_SERIES_PER_CELL = "aggregate_two_series_per_cell"
    MULTI_CELL_PER_CELL = "multi_cell_per_cell"
    POOLED_MULTI_CELL = "pooled_multi_cell"
    SUPERGEO_UNIT = "supergeo_unit"
    TRIMMED_POPULATION = "trimmed_population"


class GeometryClassification(str, Enum):
    """Geometry adapter disposition."""

    GEOMETRY_SUPPORTED = "geometry_supported"
    GEOMETRY_SUPPORTED_WITH_CAVEATS = "geometry_supported_with_caveats"
    BLOCKED_GEOMETRY = "blocked_geometry"
    BLOCKED_MISSING_POOLING_RULE = "blocked_missing_pooling_rule"
    BLOCKED_MISSING_ESTIMAND_BRIDGE = "blocked_missing_estimand_bridge"
    BLOCKED_MISSING_ADAPTER = "blocked_missing_adapter"
    BLOCKED_UNSUPPORTED_INFERENCE_GEOMETRY = "blocked_unsupported_inference_geometry"


class ReadoutExportTier(str, Enum):
    """Effective export tier after geometry (and optional interval) gates."""

    RESTRICTED = "restricted"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    BLOCKED = "blocked"
    FUTURE_CALIBRATION_SIGNAL_ELIGIBLE = "future_calibration_signal_eligible"


@dataclass(frozen=True)
class GeometryReadoutRequest:
    """Inputs for geometry support classification."""

    estimator_name: str
    inference_mode: Optional[str]
    geometry_type: GeometryType
    n_treated: int = 0
    n_control: int = 0
    n_test_grps: int = 1
    pooling_rule_id: Optional[str] = None
    pooled_claim: bool = False
    supergeo_adapter_id: Optional[str] = None
    trim_estimand_bridge_id: Optional[str] = None
    callable: bool = True
    single_treated_geometry: bool = False


@dataclass(frozen=True)
class GeometryAdapterIssue:
    code: str
    message: str


@dataclass(frozen=True)
class GeometryAdapterVerdict:
    classification: GeometryClassification
    export_tier: ReadoutExportTier
    issues: Tuple[GeometryAdapterIssue, ...] = ()
    geometry_supported: bool = False
    policy_note: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification": self.classification.value,
            "export_tier": self.export_tier.value,
            "geometry_supported": self.geometry_supported,
            "issues": [{"code": i.code, "message": i.message} for i in self.issues],
            "policy_note": self.policy_note,
        }


@dataclass(frozen=True)
class CombinedReadoutVerdict:
    """Geometry + interval combined gate (geometry blocks first)."""

    export_tier: ReadoutExportTier
    geometry: GeometryAdapterVerdict
    interval: Optional[IntervalSemanticsVerdict]
    geometry_blocks: bool
    interval_blocks: bool
    governed_export: bool
    policy_note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "export_tier": self.export_tier.value,
            "geometry_blocks": self.geometry_blocks,
            "interval_blocks": self.interval_blocks,
            "governed_export": self.governed_export,
            "policy_note": self.policy_note,
            "geometry": self.geometry.to_dict(),
            "interval": self.interval.to_dict() if self.interval else None,
        }


# Regression registry aligned with AUDIT-010 / P2 batteries.
TRACK_F_KNOWN_GEOMETRY_DISPOSITIONS: dict[
    Tuple[str, str, GeometryType], GeometryClassification
] = {
    ("TBR", "point_estimate", GeometryType.UNIT_PANEL): GeometryClassification.BLOCKED_GEOMETRY,
    ("TBR", "point_estimate", GeometryType.AGGREGATE_TWO_SERIES_1X1): (
        GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS
    ),
    ("TBRRidge", "Kfold", GeometryType.UNIT_PANEL): (
        GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS
    ),
    ("TBRRidge", "Kfold", GeometryType.POOLED_MULTI_CELL): (
        GeometryClassification.BLOCKED_MISSING_POOLING_RULE
    ),
    ("SyntheticControl", "UnitJackKnife", GeometryType.UNIT_PANEL): (
        GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS
    ),
    ("SyntheticControl", "UnitJackKnife", GeometryType.SUPERGEO_UNIT): (
        GeometryClassification.BLOCKED_MISSING_ADAPTER
    ),
    ("SyntheticControl", "UnitJackKnife", GeometryType.TRIMMED_POPULATION): (
        GeometryClassification.BLOCKED_MISSING_ESTIMAND_BRIDGE
    ),
    ("AugSynthCVXPY", "Kfold", GeometryType.UNIT_PANEL): (
        GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS
    ),
    ("AugSynthCVXPY", "Kfold", GeometryType.MULTI_CELL_PER_CELL): (
        GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS
    ),
    ("DID", "estimator_native_bootstrap", GeometryType.UNIT_PANEL): (
        GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS
    ),
}


def _normalize_estimator(name: str) -> str:
    aliases = {
        "SCM": "SyntheticControl",
        "class TBR": "TBR",
    }
    return aliases.get(name, name)


def _is_blocked_classification(classification: GeometryClassification) -> bool:
    return classification not in (
        GeometryClassification.GEOMETRY_SUPPORTED,
        GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS,
    )


def _pooling_block(request: GeometryReadoutRequest) -> Optional[GeometryAdapterIssue]:
    if request.geometry_type == GeometryType.POOLED_MULTI_CELL or request.pooled_claim:
        reason = multi_cell_pooling_block_reason(
            max(request.n_test_grps, 2),
            request.pooling_rule_id,
            pooled_aggregation_requested=True,
        )
        if reason:
            return GeometryAdapterIssue(
                reason,
                "Pooled multi-cell readout requires governed pooling_rule_id.",
            )
    return None


def classify_geometry_support(request: GeometryReadoutRequest) -> GeometryAdapterVerdict:
    """
    Classify geometry adapter support.

    ``request.callable`` records that the estimator ran; it does **not** grant
    geometry support.
    """
    est = _normalize_estimator(request.estimator_name)
    inf = str(request.inference_mode or "")
    geo = request.geometry_type
    issues: list[GeometryAdapterIssue] = []

    pool_block = _pooling_block(request)
    if pool_block:
        return GeometryAdapterVerdict(
            classification=GeometryClassification.BLOCKED_MISSING_POOLING_RULE,
            export_tier=ReadoutExportTier.BLOCKED,
            issues=(pool_block,),
            geometry_supported=False,
            policy_note="Per-cell only unless pooling_rule_id is defined (F-P0-006).",
        )

    if is_placebo_inference_mode(inf):
        if not request.single_treated_geometry and geo not in (
            GeometryType.UNIT_PANEL,
            GeometryType.AGGREGATE_TWO_SERIES_1X1,
        ):
            return GeometryAdapterVerdict(
                classification=GeometryClassification.BLOCKED_UNSUPPORTED_INFERENCE_GEOMETRY,
                export_tier=ReadoutExportTier.BLOCKED,
                issues=(
                    GeometryAdapterIssue(
                        GEOMETRY_PLACEBO_INFERENCE_LAYER,
                        "Placebo is inference/falsification — single-treated geometry only.",
                    ),
                ),
                geometry_supported=False,
            )
        if request.n_treated > 1 and not request.single_treated_geometry:
            return GeometryAdapterVerdict(
                classification=GeometryClassification.BLOCKED_GEOMETRY,
                export_tier=ReadoutExportTier.BLOCKED,
                issues=(
                    GeometryAdapterIssue(
                        GEOMETRY_SINGLE_TREATED_REQUIRED,
                        "Placebo falsification blocked on multi-treated geometry.",
                    ),
                ),
                geometry_supported=False,
            )

    if geo == GeometryType.SUPERGEO_UNIT:
        if not request.supergeo_adapter_id:
            return GeometryAdapterVerdict(
                classification=GeometryClassification.BLOCKED_MISSING_ADAPTER,
                export_tier=ReadoutExportTier.BLOCKED,
                issues=(
                    GeometryAdapterIssue(
                        GEOMETRY_SUPERGEO_ADAPTER_REQUIRED,
                        "Supergeo readout requires explicit supergeo panel/readout adapter.",
                    ),
                ),
                geometry_supported=False,
            )

    if geo == GeometryType.TRIMMED_POPULATION:
        if not request.trim_estimand_bridge_id:
            return GeometryAdapterVerdict(
                classification=GeometryClassification.BLOCKED_MISSING_ESTIMAND_BRIDGE,
                export_tier=ReadoutExportTier.BLOCKED,
                issues=(
                    GeometryAdapterIssue(
                        GEOMETRY_TRIM_ESTIMAND_BRIDGE_REQUIRED,
                        "Trimmed population readout requires retained-population estimand bridge.",
                    ),
                ),
                geometry_supported=False,
            )

    if geo == GeometryType.MULTI_CELL_PER_CELL and request.n_test_grps > 1:
        issues.append(
            GeometryAdapterIssue(
                GEOMETRY_PER_CELL_ONLY,
                "Multi-cell readout is per-cell diagnostic/restricted only — no pooling claim.",
            )
        )

    if est == "TBR":
        if geo == GeometryType.UNIT_PANEL:
            return GeometryAdapterVerdict(
                classification=GeometryClassification.BLOCKED_GEOMETRY,
                export_tier=ReadoutExportTier.BLOCKED,
                issues=(
                    GeometryAdapterIssue(
                        GEOMETRY_AGGREGATE_1X1_REQUIRED,
                        "Class TBR requires aggregate 1 treated + 1 control row (1×1).",
                    ),
                ),
                geometry_supported=False,
            )
        if geo == GeometryType.AGGREGATE_TWO_SERIES_1X1:
            if request.n_treated != 1 or request.n_control != 1:
                issues.append(
                    GeometryAdapterIssue(
                        GEOMETRY_AGGREGATE_1X1_REQUIRED,
                        f"Class TBR aggregate requires n_treated=1 and n_control=1 "
                        f"(got {request.n_treated}/{request.n_control}).",
                    )
                )
                return GeometryAdapterVerdict(
                    classification=GeometryClassification.BLOCKED_GEOMETRY,
                    export_tier=ReadoutExportTier.BLOCKED,
                    issues=tuple(issues),
                    geometry_supported=False,
                )
            return GeometryAdapterVerdict(
                classification=GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS,
                export_tier=ReadoutExportTier.RESTRICTED,
                issues=tuple(issues),
                geometry_supported=True,
                policy_note="Aggregate class TBR — restricted diagnostic; not TBRRidge; not MMM.",
            )
        if geo == GeometryType.AGGREGATE_TWO_SERIES_PER_CELL:
            return GeometryAdapterVerdict(
                classification=GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS,
                export_tier=ReadoutExportTier.RESTRICTED,
                issues=(
                    GeometryAdapterIssue(
                        GEOMETRY_PER_CELL_ONLY,
                        "Per-cell aggregate 1×1 only; no pooled multi-cell claim.",
                    ),
                ),
                geometry_supported=True,
                policy_note="Multi-cell class TBR per-cell aggregate — restricted diagnostic only.",
            )
        return GeometryAdapterVerdict(
            classification=GeometryClassification.BLOCKED_GEOMETRY,
            export_tier=ReadoutExportTier.BLOCKED,
            issues=(
                GeometryAdapterIssue(
                    GEOMETRY_AGGREGATE_1X1_REQUIRED,
                    f"Class TBR unsupported on geometry {geo.value}.",
                ),
            ),
            geometry_supported=False,
        )

    if est == "TBRRidge":
        if geo != GeometryType.UNIT_PANEL:
            return GeometryAdapterVerdict(
                classification=GeometryClassification.BLOCKED_GEOMETRY,
                export_tier=ReadoutExportTier.BLOCKED,
                issues=(
                    GeometryAdapterIssue(
                        GEOMETRY_UNIT_PANEL_REQUIRED,
                        "TBRRidge unit-panel restricted diagnostics only on this contract.",
                    ),
                ),
                geometry_supported=False,
            )
        return GeometryAdapterVerdict(
            classification=GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS,
            export_tier=ReadoutExportTier.RESTRICTED,
            issues=tuple(issues),
            geometry_supported=True,
            policy_note="TBRRidge unit panel — restricted diagnostic; scale ≠ SCM+JK.",
        )

    if est == "SyntheticControl":
        if geo in (GeometryType.UNIT_PANEL, GeometryType.MULTI_CELL_PER_CELL):
            tier = ReadoutExportTier.DIAGNOSTIC_ONLY
            if inf == "UnitJackKnife":
                tier = ReadoutExportTier.FUTURE_CALIBRATION_SIGNAL_ELIGIBLE
            return GeometryAdapterVerdict(
                classification=GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS,
                export_tier=tier,
                issues=tuple(issues),
                geometry_supported=True,
                policy_note="SCM unit-panel null-monitor / diagnostic — not flat supergeo/trim readout.",
            )
        return GeometryAdapterVerdict(
            classification=GeometryClassification.BLOCKED_GEOMETRY,
            export_tier=ReadoutExportTier.BLOCKED,
            issues=(
                GeometryAdapterIssue(
                    GEOMETRY_UNIT_PANEL_REQUIRED,
                    f"SCM readout unsupported on geometry {geo.value} without adapter.",
                ),
            ),
            geometry_supported=False,
        )

    if est == "AugSynthCVXPY":
        if geo in (GeometryType.UNIT_PANEL, GeometryType.MULTI_CELL_PER_CELL):
            return GeometryAdapterVerdict(
                classification=GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS,
                export_tier=ReadoutExportTier.RESTRICTED,
                issues=tuple(issues),
                geometry_supported=True,
                policy_note="AugSynthCVXPY unit / per-cell diagnostic restricted only.",
            )
        return GeometryAdapterVerdict(
            classification=GeometryClassification.BLOCKED_GEOMETRY,
            export_tier=ReadoutExportTier.BLOCKED,
            issues=(
                GeometryAdapterIssue(
                    GEOMETRY_UNIT_PANEL_REQUIRED,
                    f"AugSynthCVXPY unsupported on geometry {geo.value}.",
                ),
            ),
            geometry_supported=False,
        )

    if est == "DID":
        return GeometryAdapterVerdict(
            classification=GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS,
            export_tier=ReadoutExportTier.RESTRICTED,
            issues=(
                GeometryAdapterIssue(
                    GEOMETRY_DID_POLICY_DEFERRED,
                    "DID readout restricted/deferred unless estimand and scale policy satisfied (DEF-003).",
                ),
            ),
            geometry_supported=True,
            policy_note="DID — restricted; relative ATT CI policy applies separately.",
        )

    if request.callable and not issues:
        issues.append(
            GeometryAdapterIssue(
                CALLABLE_DOES_NOT_IMPLY_GEOMETRY,
                "Callable estimator/inference does not imply geometry support — explicit classification required.",
            )
        )

    return GeometryAdapterVerdict(
        classification=GeometryClassification.BLOCKED_UNSUPPORTED_INFERENCE_GEOMETRY,
        export_tier=ReadoutExportTier.BLOCKED,
        issues=tuple(issues) if issues else (
            GeometryAdapterIssue(
                GEOMETRY_UNIT_PANEL_REQUIRED,
                f"No geometry rule for estimator={est!r} on {geo.value}.",
            ),
        ),
        geometry_supported=False,
    )


def classify_combined_readout(
    geometry_request: GeometryReadoutRequest,
    interval_verdict: Optional[IntervalSemanticsVerdict] = None,
) -> CombinedReadoutVerdict:
    """
    Apply geometry gate first; F-INF interval status never overrides geometry blocking.
    """
    geometry = classify_geometry_support(geometry_request)
    geometry_blocks = _is_blocked_classification(geometry.classification)

    interval_blocks = False
    if interval_verdict is not None:
        interval_blocks = interval_verdict.classification in (
            IntervalSemanticsClassification.BLOCKED_INTERFACE,
            IntervalSemanticsClassification.BLOCKED_INVALID_INTERVAL,
            IntervalSemanticsClassification.CALLABLE_UNVERIFIED_INTERVAL_SEMANTICS,
        ) or not interval_verdict.is_governed_uncertainty

    if geometry_blocks:
        return CombinedReadoutVerdict(
            export_tier=ReadoutExportTier.BLOCKED,
            geometry=geometry,
            interval=interval_verdict,
            geometry_blocks=True,
            interval_blocks=interval_blocks,
            governed_export=False,
            policy_note=(
                "Geometry blocking takes precedence over interval semantics (F-GEO-001); "
                "valid-looking intervals do not rescue unsupported geometry."
            ),
        )

    if interval_verdict is not None and interval_verdict.is_governed_uncertainty:
        export_tier = ReadoutExportTier.RESTRICTED
        governed = True
        note = "Governed uncertainty requires both geometry support and F-INF semantics pass."
    elif interval_verdict is not None and interval_blocks:
        export_tier = geometry.export_tier
        governed = False
        note = "Geometry supported; interval semantics restrict export tier."
    else:
        export_tier = geometry.export_tier
        governed = False
        note = "Geometry-supported readout; interval tier applied separately when present."

    return CombinedReadoutVerdict(
        export_tier=export_tier,
        geometry=geometry,
        interval=interval_verdict,
        geometry_blocks=False,
        interval_blocks=interval_blocks,
        governed_export=governed,
        policy_note=note,
    )


def expected_track_f_geometry_classification(
    estimator_name: str,
    inference_mode: str,
    geometry_type: GeometryType,
) -> Optional[GeometryClassification]:
    est = _normalize_estimator(estimator_name)
    return TRACK_F_KNOWN_GEOMETRY_DISPOSITIONS.get((est, inference_mode, geometry_type))


__all__ = [
    "CALLABLE_DOES_NOT_IMPLY_GEOMETRY",
    "GeometryAdapterIssue",
    "GeometryAdapterVerdict",
    "GeometryClassification",
    "GeometryReadoutRequest",
    "GeometryType",
    "ReadoutExportTier",
    "CombinedReadoutVerdict",
    "TRACK_F_KNOWN_GEOMETRY_DISPOSITIONS",
    "classify_combined_readout",
    "classify_geometry_support",
    "expected_track_f_geometry_classification",
]
