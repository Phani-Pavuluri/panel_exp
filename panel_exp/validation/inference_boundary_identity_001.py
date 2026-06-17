"""INFERENCE-BOUNDARY-GUARDRAIL-ENFORCEMENT-001 — readout identity normalization."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

IDENTITY_VERSION = "1.0.0"

READOUT_SEMANTICS_VALUES = frozenset(
    {
        "point_estimate",
        "causal_interval",
        "forecast_interval",
        "null_monitor_interval",
        "directional_sign",
        "significance_test",
        "per_cell_point",
        "per_cell_interval",
        "pooled_point",
        "pooled_interval",
        "unknown",
    }
)

INTERVAL_TYPE_VALUES = frozenset(
    {
        "none",
        "jackknife_interval",
        "placebo_interval",
        "bootstrap_interval",
        "brb_interval",
        "kfold_interval",
        "credible_interval",
        "forecast_interval",
        "unknown",
    }
)

ESTIMAND_VALUES = frozenset(
    {
        "unit_level_effect",
        "aggregate_effect",
        "per_cell_effect",
        "pooled_multicell_effect",
        "average_treatment_effect",
        "treated_unit_effect",
        "directional_effect",
        "unknown",
    }
)

_ESTIMATOR_ALIASES: dict[str, str] = {
    "scm": "scm",
    "syntheticcontrol": "scm",
    "synthetic_control": "scm",
    "syntheticcontrolcvxpy": "scm",
    "synthetic_control_cvxpy": "scm",
    "syntheticcontrolcvxpy": "scm",
    "augsynth": "augsynth",
    "augsynthcvxpy": "augsynth",
    "augmentedsyntheticcontrol": "augsynth",
    "augmented_synthetic_control": "augsynth",
    "tbr": "tbr",
    "tbr_aggregate": "tbr",
    "tbrridge": "tbrridge",
    "tbr_ridge": "tbrridge",
    "did": "did",
    "difference_in_differences": "did",
    "differenceindifferences": "did",
}

_INFERENCE_ALIASES: dict[str, str] = {
    "unitjackknife": "unit_jackknife",
    "unit_jackknife": "unit_jackknife",
    "jackknife": "unit_jackknife",
    "unit_jack_knife": "unit_jackknife",
    "bootstrap": "bootstrap",
    "placebo": "placebo",
    "kfold": "kfold",
    "k_fold": "kfold",
    "brb": "brb",
    "point_only": "point_only",
    "point": "point_only",
    "none": "none",
}

_READOUT_ALIASES: dict[str, str] = {
    "point": "point_estimate",
    "point_estimate": "point_estimate",
    "point_only": "point_estimate",
    "causal_interval": "causal_interval",
    "confidence_interval": "causal_interval",
    "forecast_interval": "forecast_interval",
    "null_monitor": "null_monitor_interval",
    "null_monitor_interval": "null_monitor_interval",
    "directional_sign": "directional_sign",
    "significance_test": "significance_test",
    "per_cell_point": "per_cell_point",
    "per_cell_interval": "per_cell_interval",
    "pooled_point": "pooled_point",
    "pooled_interval": "pooled_interval",
}

_INTERVAL_ALIASES: dict[str, str] = {
    "none": "none",
    "unavailable": "none",
    "jackknife": "jackknife_interval",
    "jackknife_interval": "jackknife_interval",
    "unit_jackknife": "jackknife_interval",
    "placebo": "placebo_interval",
    "placebo_band": "placebo_interval",
    "placebo_interval": "placebo_interval",
    "bootstrap": "bootstrap_interval",
    "bootstrap_interval": "bootstrap_interval",
    "brb": "brb_interval",
    "brb_interval": "brb_interval",
    "kfold": "kfold_interval",
    "k_fold": "kfold_interval",
    "kfold_interval": "kfold_interval",
    "credible": "credible_interval",
    "credible_interval": "credible_interval",
    "forecast": "forecast_interval",
    "forecast_interval": "forecast_interval",
    "confidence_interval": "jackknife_interval",
}


def _norm_key(value: str | None) -> str:
    return (value or "").strip().lower().replace("-", "_").replace(" ", "_")


def normalize_estimator_id(value: str | None, *, explicit_registry_id: str | None = None) -> str | None:
    if explicit_registry_id:
        key = _norm_key(explicit_registry_id)
        return _ESTIMATOR_ALIASES.get(key, key if key else None)
    if not value:
        return None
    key = _norm_key(value)
    return _ESTIMATOR_ALIASES.get(key, key)


def normalize_inference_id(value: str | None, *, explicit_registry_id: str | None = None) -> str | None:
    if explicit_registry_id:
        key = _norm_key(explicit_registry_id)
        return _INFERENCE_ALIASES.get(key, key if key else None)
    if not value:
        return None
    key = _norm_key(value)
    return _INFERENCE_ALIASES.get(key, key)


def normalize_readout_semantics(value: str | None) -> str:
    if not value:
        return "unknown"
    key = _norm_key(value)
    mapped = _READOUT_ALIASES.get(key, key)
    return mapped if mapped in READOUT_SEMANTICS_VALUES else "unknown"


def normalize_interval_type(value: str | None) -> str:
    if not value:
        return "none"
    key = _norm_key(value)
    mapped = _INTERVAL_ALIASES.get(key, key)
    return mapped if mapped in INTERVAL_TYPE_VALUES else "unknown"


def normalize_estimand(value: str | None) -> str:
    if not value:
        return "unknown"
    key = _norm_key(value)
    if key in ESTIMAND_VALUES:
        return key
    aliases = {
        "ate": "average_treatment_effect",
        "att": "treated_unit_effect",
        "per_cell": "per_cell_effect",
        "pooled": "pooled_multicell_effect",
        "aggregate": "aggregate_effect",
    }
    return aliases.get(key, "unknown")


@dataclass(frozen=True)
class InferenceBoundaryIdentity:
    design_id: str | None = None
    estimator_id: str | None = None
    inference_id: str | None = None
    instrument_id: str | None = None
    geometry_id: str | None = None
    readout_semantics: str | None = None
    interval_type: str | None = None
    estimand: str | None = None
    cell_id: str | None = None
    pooled: bool = False
    requested_role: str | None = None
    source: str = "readout_boundary"
    identity_version: str = IDENTITY_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def build(
        cls,
        *,
        design_id: str | None = None,
        estimator_id: str | None = None,
        inference_id: str | None = None,
        instrument_id: str | None = None,
        geometry_id: str | None = None,
        readout_semantics: str | None = None,
        interval_type: str | None = None,
        estimand: str | None = None,
        cell_id: str | None = None,
        pooled: bool = False,
        requested_role: str | None = None,
        source: str = "readout_boundary",
        explicit_estimator_registry_id: str | None = None,
        explicit_inference_registry_id: str | None = None,
    ) -> "InferenceBoundaryIdentity":
        est = normalize_estimator_id(estimator_id, explicit_registry_id=explicit_estimator_registry_id)
        inf = normalize_inference_id(inference_id, explicit_registry_id=explicit_inference_registry_id)
        if instrument_id and not est:
            parts = _norm_key(instrument_id).split("_")
            if "augsynth" in _norm_key(instrument_id):
                est = "augsynth"
            elif "scm" in _norm_key(instrument_id) or "synthetic" in _norm_key(instrument_id):
                est = "scm"
            if "jackknife" in _norm_key(instrument_id) or "jk" in parts:
                inf = inf or "unit_jackknife"
            if "kfold" in _norm_key(instrument_id):
                inf = inf or "kfold"
            if "point" in _norm_key(instrument_id):
                inf = inf or "point_only"
        return cls(
            design_id=design_id,
            estimator_id=est,
            inference_id=inf,
            instrument_id=instrument_id,
            geometry_id=geometry_id,
            readout_semantics=normalize_readout_semantics(readout_semantics),
            interval_type=normalize_interval_type(interval_type),
            estimand=normalize_estimand(estimand),
            cell_id=cell_id,
            pooled=bool(pooled),
            requested_role=(requested_role.strip().lower() if requested_role else None),
            source=source,
        )


def identity_from_mapping(payload: Mapping[str, Any]) -> InferenceBoundaryIdentity:
    return InferenceBoundaryIdentity.build(
        design_id=payload.get("design_id"),
        estimator_id=payload.get("estimator_id"),
        inference_id=payload.get("inference_id"),
        instrument_id=payload.get("instrument_id"),
        geometry_id=payload.get("geometry_id"),
        readout_semantics=payload.get("readout_semantics"),
        interval_type=payload.get("interval_type"),
        estimand=payload.get("estimand"),
        cell_id=payload.get("cell_id"),
        pooled=bool(payload.get("pooled", False)),
        requested_role=payload.get("requested_role"),
        source=str(payload.get("source", "mapping")),
        explicit_estimator_registry_id=payload.get("explicit_estimator_registry_id"),
        explicit_inference_registry_id=payload.get("explicit_inference_registry_id"),
    )
