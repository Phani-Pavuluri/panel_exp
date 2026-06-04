"""METHOD-COMBINATION-VALIDATION-MATRIX-001 — Layer 5 pre-suitability combination matrix.

Maps Layer 4 protocol combinations to OC-ready / blocked / bridge / research status.
Does not assign trust roles or run OC.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LAYER4_JSON = _REPO_ROOT / "docs/track_d/archives/METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.json"

ValidationMatrixStatus = Literal[
    "ready_for_oc_execution",
    "ready_for_oc_with_caveats",
    "blocked_before_oc",
    "blocked_needs_bridge",
    "research_only_oc",
    "quarantine_or_deprecate",
    "not_applicable",
]

AllowedNextAction = Literal[
    "run_smoke_protocol",
    "run_characterization_protocol",
    "run_calibration_protocol",
    "write_bridge_adr",
    "fix_implementation_gap",
    "quarantine_or_deprecate",
    "research_only",
    "no_action",
]

# Fields that must never encode suitability / trust authorization labels.
FORBIDDEN_AUTHORIZATION_SUBSTRINGS = (
    "primary",
    "secondary",
    "directional",
    "trusted",
    "production_ready",
    "production-ready",
)

D5_STAT_EXECUTION_QUEUE: tuple[str, ...] = (
    "D5-STAT-SMOKE-CALLABLE-001",
    "D5-STAT-SCM-JK-001",
    "D5-STAT-AUGSYNTH-POINT-001",
    "D5-STAT-AUGSYNTH-JK-001",
    "D5-STAT-TBR-AGG-001",
    "D5-STAT-TBRRIDGE-INF-001",
    "D5-STAT-DID-BOOTSTRAP-001",
    "D5-STAT-MCELL-PERCELL-001",
)

D5_STAT_BLOCKED_QUEUE: tuple[str, ...] = (
    "D5-STAT-MCELL-POOLED-001",
    "D5-STAT-SUPERGEO-BRIDGE-001",
    "D5-STAT-TRIM-BRIDGE-001",
    "D5-STAT-AUGSYNTH-CONFORMAL-001",
    "D5-STAT-TBR-UNIT-JK-001",
    "D5-STAT-TBRRIDGE-BAYESIAN-001",
)

BRIDGE_ADR_QUEUE: tuple[str, ...] = (
    "F-GEO-003 supergeo unit-panel bridge",
    "F-GEO-004 trimmedmatch flat readout bridge",
    "multicell causal pooling ADR",
)

IMPLEMENTATION_FIX_QUEUE: tuple[str, ...] = (
    "G1-G8 AugSynthCVXPY fidelity",
    "IMPL-JK-001 AugSynth strata",
    "IMPL-CONF-001 Conformal interval redesign",
    "TBRRidge JK/JKP pivot calibration",
    "INV-015 registry Bayesian vs MCMC",
    "SyntheticControl scipy parity vs CVXPY",
)


@dataclass
class MatrixRow:
    combination_id: str
    design_family: str
    estimator_family: str
    inference_family: str
    geometry: str
    treatment_structure: str
    estimand: str
    effect_scale: str
    interval_semantics: str
    data_level: str
    supported_by_literature: str
    implementation_status: str
    statistical_protocol_status: str
    validation_matrix_status: ValidationMatrixStatus
    blocked_by: list[str]
    required_bridge: str
    required_d5_stat_artifact: str
    minimum_battery_level: str
    required_metrics: list[str]
    known_failure_modes: list[str]
    allowed_next_action: AllowedNextAction
    promotion_allowed: bool = False
    trust_role_allowed: bool = False
    calibration_signal_allowed: bool = False
    mmm_allowed: bool = False
    layer4_protocol_id: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Extended dimensions for combinations required by Layer 5 coverage (beyond L4 ids).
COMBO_DIMENSIONS: dict[str, dict[str, Any]] = {
    "SCM-JK": {
        "design_family": "DES-GMM-001",
        "estimator_family": "EST-SCM-001 / SyntheticControlCVXPY",
        "inference_family": "INF-JK-001 / UnitJackKnife",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "single_treated_unit",
        "estimand": "ATT_counterfactual_gap",
        "effect_scale": "level_or_relative_export_dependent",
        "interval_semantics": "jackknife_null_monitor",
        "data_level": "unit_panel_wide",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_validated_with_caveats",
    },
    "TIER1-SCM-JK": {
        "design_family": "DES-TIER1-RAND-001",
        "estimator_family": "EST-SCM-001 / SyntheticControlCVXPY",
        "inference_family": "INF-JK-001 / UnitJackKnife",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "probabilistic_assignment",
        "estimand": "ATT_counterfactual_gap",
        "effect_scale": "level_or_relative",
        "interval_semantics": "jackknife_null_monitor",
        "data_level": "unit_panel_wide",
        "supported_by_literature": "aligned_pending_validation",
        "implementation_status": "implementation_validated_with_caveats",
    },
    "SCM-PLACEBO": {
        "design_family": "DES-GMM-001|DES-TIER1-RAND-001",
        "estimator_family": "EST-SCM-001",
        "inference_family": "INF-PLACEBO-001 / Placebo",
        "geometry": "unit_panel_single_treated",
        "treatment_structure": "single_treated_scope",
        "estimand": "falsification_placebo",
        "effect_scale": "level",
        "interval_semantics": "falsification_not_CI",
        "data_level": "unit_panel_wide",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_validated_with_caveats",
    },
    "MCELL-PERCELL-SCM-JK": {
        "design_family": "DES-* multi_cell",
        "estimator_family": "EST-SCM-001",
        "inference_family": "INF-JK-001",
        "geometry": "multi_cell_per_cell",
        "treatment_structure": "multi_cell_per_cell_only",
        "estimand": "per_cell_ATT",
        "effect_scale": "per_cell_level",
        "interval_semantics": "jackknife_per_cell",
        "data_level": "unit_panel_per_cell",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_validated_with_caveats",
    },
    "MCELL-POOLED-SCM-JK": {
        "design_family": "DES-* multi_cell",
        "estimator_family": "EST-SCM-001",
        "inference_family": "INF-JK-001",
        "geometry": "pooled_multi_cell",
        "treatment_structure": "pooled_cells",
        "estimand": "pooled_lift_blocked",
        "effect_scale": "undefined_without_ADR",
        "interval_semantics": "blocked",
        "data_level": "unit_panel_pooled",
        "supported_by_literature": "literature_mismatch",
        "implementation_status": "unsupported_geometry_not_blocked",
    },
    "AUGSYNTH-POINT": {
        "design_family": "DES-GMM-001",
        "estimator_family": "EST-AUGSYNTH-001 / AugSynthCVXPY",
        "inference_family": "INF-POINT-001 / point_estimate",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "single_cell",
        "estimand": "augmented_gap",
        "effect_scale": "level_vs_relative_G7",
        "interval_semantics": "point_only",
        "data_level": "unit_panel_wide",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_gap",
    },
    "AUGSYNTH-JK": {
        "design_family": "DES-GMM-001",
        "estimator_family": "EST-AUGSYNTH-001 / AugSynthCVXPY",
        "inference_family": "INF-JK-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "single_cell",
        "estimand": "augmented_gap",
        "effect_scale": "level_vs_relative",
        "interval_semantics": "jackknife_unsafe_strata",
        "data_level": "unit_panel_wide",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_gap",
    },
    "AUGSYNTH-CONFORMAL": {
        "design_family": "DES-GMM-001",
        "estimator_family": "EST-AUGSYNTH-001",
        "inference_family": "INF-CONFORMAL-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "single_cell",
        "estimand": "augmented_gap",
        "effect_scale": "level",
        "interval_semantics": "conformal_blocked_IMPL-CONF-001",
        "data_level": "unit_panel_wide",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_gap",
    },
    "AUGSYNTH-KFOLD": {
        "design_family": "DES-GMM-001",
        "estimator_family": "EST-AUGSYNTH-001",
        "inference_family": "INF-KFOLD-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "single_cell",
        "estimand": "augmented_gap",
        "effect_scale": "level",
        "interval_semantics": "diagnostic_kfold_band",
        "data_level": "unit_panel_wide",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_gap",
    },
    "MCELL-AUGSYNTH-POINT": {
        "design_family": "DES-* multi_cell",
        "estimator_family": "EST-AUGSYNTH-001",
        "inference_family": "INF-POINT-001",
        "geometry": "multi_cell_per_cell",
        "treatment_structure": "per_cell",
        "estimand": "per_cell_augmented_gap",
        "effect_scale": "per_cell",
        "interval_semantics": "point_only",
        "data_level": "unit_panel_per_cell",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_gap",
    },
    "MCELL-POOLED-AUGSYNTH": {
        "design_family": "DES-* multi_cell",
        "estimator_family": "EST-AUGSYNTH-001",
        "inference_family": "INF-POINT-001",
        "geometry": "pooled_multi_cell",
        "treatment_structure": "pooled",
        "estimand": "pooled_causal_lift_blocked",
        "effect_scale": "blocked_ADR",
        "interval_semantics": "blocked",
        "data_level": "pooled_panel",
        "supported_by_literature": "literature_mismatch",
        "implementation_status": "implementation_gap",
    },
    "SUPERGEO-AUGSYNTH-POINT": {
        "design_family": "DES-SUPERGEO-001",
        "estimator_family": "EST-AUGSYNTH-001",
        "inference_family": "INF-POINT-001",
        "geometry": "supergeo_cluster",
        "treatment_structure": "cluster_assignment",
        "estimand": "undefined_flat_readout",
        "effect_scale": "n/a",
        "interval_semantics": "blocked",
        "data_level": "cluster_geometry",
        "supported_by_literature": "literature_mismatch",
        "implementation_status": "unsupported_geometry_not_blocked",
    },
    "TRIM-AUGSYNTH-POINT": {
        "design_family": "DES-TRIM-001",
        "estimator_family": "EST-AUGSYNTH-001",
        "inference_family": "INF-POINT-001",
        "geometry": "trimmed_pair",
        "treatment_structure": "pair_Tp_Te",
        "estimand": "undefined_flat_readout",
        "effect_scale": "n/a",
        "interval_semantics": "blocked",
        "data_level": "pair_geometry",
        "supported_by_literature": "literature_mismatch",
        "implementation_status": "unsupported_geometry_not_blocked",
    },
    "TBR-AGG-POINT": {
        "design_family": "DES-GMM-001",
        "estimator_family": "EST-TBR-001",
        "inference_family": "INF-POINT-001",
        "geometry": "aggregate_two_row",
        "treatment_structure": "single_aggregate_treated",
        "estimand": "aggregate_ATT",
        "effect_scale": "aggregate_level",
        "interval_semantics": "point_only",
        "data_level": "aggregate_2_row",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_validated_with_caveats",
    },
    "TBR-AGG-KFOLD": {
        "design_family": "DES-GMM-001",
        "estimator_family": "EST-TBR-001",
        "inference_family": "INF-KFOLD-001",
        "geometry": "aggregate_two_row",
        "treatment_structure": "single_aggregate",
        "estimand": "aggregate_ATT",
        "effect_scale": "aggregate",
        "interval_semantics": "diagnostic_kfold",
        "data_level": "aggregate_2_row",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_validated_with_caveats",
    },
    "TBR-UNIT-JK": {
        "design_family": "DES-*",
        "estimator_family": "EST-TBR-001",
        "inference_family": "INF-JK-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "unit_panel",
        "estimand": "invalid_geometry",
        "effect_scale": "n/a",
        "interval_semantics": "blocked",
        "data_level": "unit_panel",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_validated_with_caveats",
    },
    "TBRRIDGE-KFOLD": {
        "design_family": "DES-*",
        "estimator_family": "EST-TBRRIDGE-001",
        "inference_family": "INF-KFOLD-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "unit_panel",
        "estimand": "ridge_penalized_gap",
        "effect_scale": "unit_level",
        "interval_semantics": "diagnostic_kfold",
        "data_level": "unit_panel",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_gap",
    },
    "TBRRIDGE-TSKFOLD": {
        "design_family": "DES-*",
        "estimator_family": "EST-TBRRIDGE-001",
        "inference_family": "INF-TSKFOLD-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "unit_panel",
        "estimand": "ridge_penalized_gap",
        "effect_scale": "unit_level",
        "interval_semantics": "time_series_kfold_diagnostic",
        "data_level": "unit_panel",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_gap",
    },
    "TBRRIDGE-BRB": {
        "design_family": "DES-*",
        "estimator_family": "EST-TBRRIDGE-001",
        "inference_family": "INF-BRB-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "unit_panel",
        "estimand": "ridge_penalized_gap",
        "effect_scale": "unit_level",
        "interval_semantics": "block_residual_bootstrap",
        "data_level": "unit_panel",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_gap",
    },
    "TBRRIDGE-CONFORMAL": {
        "design_family": "DES-*",
        "estimator_family": "EST-TBRRIDGE-001",
        "inference_family": "INF-CONFORMAL-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "unit_panel",
        "estimand": "ridge_penalized_gap",
        "effect_scale": "unit_level",
        "interval_semantics": "conformal_exchangeability_caveat",
        "data_level": "unit_panel",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_gap",
    },
    "TBRRIDGE-JK": {
        "design_family": "DES-*",
        "estimator_family": "EST-TBRRIDGE-001",
        "inference_family": "INF-JK-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "unit_panel",
        "estimand": "ridge_penalized_gap",
        "effect_scale": "unit_level",
        "interval_semantics": "jackknife_miscalibrated",
        "data_level": "unit_panel",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_gap",
    },
    "TBRRIDGE-PLACEBO": {
        "design_family": "DES-*",
        "estimator_family": "EST-TBRRIDGE-001",
        "inference_family": "INF-PLACEBO-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "single_treated",
        "estimand": "falsification",
        "effect_scale": "unit_level",
        "interval_semantics": "placebo_not_wired",
        "data_level": "unit_panel",
        "supported_by_literature": "unclear_requires_review",
        "implementation_status": "implementation_gap",
    },
    "DID-BOOTSTRAP": {
        "design_family": "DES-*",
        "estimator_family": "EST-DID-001",
        "inference_family": "INF-DID-BOOT-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "panel_diD",
        "estimand": "ATT_DiD",
        "effect_scale": "relative_CI_policy_open",
        "interval_semantics": "embedded_bootstrap_native",
        "data_level": "unit_panel",
        "supported_by_literature": "partially_aligned",
        "implementation_status": "implementation_validated_with_caveats",
    },
    "SDID-POINT": {
        "design_family": "DES-*",
        "estimator_family": "EST-SDID-001",
        "inference_family": "INF-POINT-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "panel",
        "estimand": "SDID_ATT",
        "effect_scale": "level",
        "interval_semantics": "point_or_runner_skip",
        "data_level": "unit_panel",
        "supported_by_literature": "research_path",
        "implementation_status": "research_only_not_validated",
    },
    "TBRRIDGE-BAYESIAN-REG": {
        "design_family": "DES-*",
        "estimator_family": "EST-TBRRIDGE-001",
        "inference_family": "INF-BAYES-REG-001",
        "geometry": "unit_panel_single_cell",
        "treatment_structure": "unit_panel",
        "estimand": "ridge_gap",
        "effect_scale": "unit_level",
        "interval_semantics": "registry_bayesian_handler",
        "data_level": "unit_panel",
        "supported_by_literature": "architecture_mismatch",
        "implementation_status": "architecture_gap",
    },
    "BAYESIANTBR-MCMC": {
        "design_family": "DES-*",
        "estimator_family": "EST-RESEARCH-BAYESIANTBR",
        "inference_family": "INF-BAYES-REG-001",
        "geometry": "aggregate_or_unit",
        "treatment_structure": "research",
        "estimand": "bayesian_TBR_posterior",
        "effect_scale": "research",
        "interval_semantics": "mcmc_posterior",
        "data_level": "research",
        "supported_by_literature": "research_only",
        "implementation_status": "research_only_not_validated",
    },
    "TROP-RESEARCH": {
        "design_family": "n/a",
        "estimator_family": "EST-RESEARCH-TROP",
        "inference_family": "INF-POINT-001",
        "geometry": "research",
        "treatment_structure": "research",
        "estimand": "research",
        "effect_scale": "research",
        "interval_semantics": "point",
        "data_level": "research",
        "supported_by_literature": "not_literature_backed",
        "implementation_status": "research_only_not_validated",
    },
    "MTGP-RESEARCH": {
        "design_family": "n/a",
        "estimator_family": "EST-RESEARCH-MTGP",
        "inference_family": "INF-BAYES-REG-001",
        "geometry": "research",
        "treatment_structure": "research",
        "estimand": "research",
        "effect_scale": "research",
        "interval_semantics": "bayesian",
        "data_level": "research",
        "supported_by_literature": "research_only",
        "implementation_status": "research_only_not_validated",
    },
    "SUPERGEO-SCM-JK": {
        "design_family": "DES-SUPERGEO-001",
        "estimator_family": "EST-SCM-001",
        "inference_family": "INF-JK-001",
        "geometry": "supergeo_cluster",
        "treatment_structure": "cluster",
        "estimand": "flat_readout_invalid",
        "effect_scale": "n/a",
        "interval_semantics": "blocked",
        "data_level": "cluster",
        "supported_by_literature": "literature_mismatch",
        "implementation_status": "unsupported_geometry_not_blocked",
    },
    "TRIM-SCM-JK": {
        "design_family": "DES-TRIM-001",
        "estimator_family": "EST-SCM-001",
        "inference_family": "INF-JK-001",
        "geometry": "trimmed_pair",
        "treatment_structure": "pair",
        "estimand": "flat_readout_invalid",
        "effect_scale": "n/a",
        "interval_semantics": "blocked",
        "data_level": "pair",
        "supported_by_literature": "literature_mismatch",
        "implementation_status": "unsupported_geometry_not_blocked",
    },
}


def load_layer4() -> dict[str, Any]:
    return json.loads(_LAYER4_JSON.read_text(encoding="utf-8"))


def _layer4_combo_rows(l4: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        r["combination_id"]: r
        for r in l4["rows"]
        if r.get("combination_id")
    }


def _matrix_status_from_protocol(proto: dict[str, Any]) -> ValidationMatrixStatus:
    elig = proto["eligibility_status"]
    blocked = proto.get("blocked_by", [])
    blob = " ".join(blocked).lower()
    if elig == "deprecated_or_quarantine":
        return "quarantine_or_deprecate"
    if elig == "research_only_protocol":
        return "research_only_oc"
    if elig == "blocked_by_geometry":
        if any(x in blob for x in ("bridge", "f-geo", "a29", "a30", "pooled", "adr")):
            return "blocked_needs_bridge"
        return "blocked_needs_bridge"
    if elig in ("blocked_by_implementation_gap", "blocked_by_architecture_gap"):
        return "blocked_before_oc"
    if not proto.get("eligible_for_layer4", False):
        if "bridge" in blob or "f-geo" in blob:
            return "blocked_needs_bridge"
        return "blocked_before_oc"
    if elig == "ready_for_protocol":
        return "ready_for_oc_execution"
    return "ready_for_oc_with_caveats"


def _next_action(
    matrix_status: ValidationMatrixStatus,
    battery: str,
    blocked_by: list[str],
) -> AllowedNextAction:
    if matrix_status == "quarantine_or_deprecate":
        return "quarantine_or_deprecate"
    if matrix_status == "research_only_oc":
        return "research_only"
    if matrix_status == "blocked_needs_bridge":
        return "write_bridge_adr"
    if matrix_status == "blocked_before_oc":
        if any("impl" in b.lower() or "g1" in b.lower() or "jk" in b.lower() for b in blocked_by):
            return "fix_implementation_gap"
        return "no_action"
    if matrix_status == "not_applicable":
        return "no_action"
    if battery == "A":
        return "run_smoke_protocol"
    if battery == "C":
        return "run_calibration_protocol"
    if battery in ("B", "D"):
        return "run_characterization_protocol"
    return "run_characterization_protocol"


def _required_bridge(matrix_status: ValidationMatrixStatus, combo_id: str, blocked_by: list[str]) -> str:
    if matrix_status != "blocked_needs_bridge":
        return ""
    if "SUPERGEO" in combo_id or "F-GEO-003" in " ".join(blocked_by):
        return "F-GEO-003 supergeo flat readout bridge"
    if "TRIM" in combo_id or "F-GEO-004" in " ".join(blocked_by):
        return "F-GEO-004 trimmedmatch adapter"
    if "POOLED" in combo_id or "pooled" in " ".join(blocked_by).lower():
        return "multicell causal pooling ADR"
    return "geometry_or_estimand_bridge_ADR"


def _dims_from_protocol(proto: dict[str, Any]) -> dict[str, Any]:
    cid = proto["combination_id"]
    if cid in COMBO_DIMENSIONS:
        return dict(COMBO_DIMENSIONS[cid])
    deps = proto.get("layer3_dependencies", [])
    design = deps[0] if len(deps) > 0 else "DES-*"
    estimator = deps[1] if len(deps) > 1 else "estimator"
    inference = deps[2] if len(deps) > 2 else "inference"
    geometry = deps[3] if len(deps) > 3 else "geometry"
    return {
        "design_family": design,
        "estimator_family": estimator,
        "inference_family": inference,
        "geometry": geometry.replace("_", " "),
        "treatment_structure": "see_layer4_notes",
        "estimand": "see_literature_alignment",
        "effect_scale": "see_export_path",
        "interval_semantics": inference,
        "data_level": geometry,
        "supported_by_literature": "see_layer2",
        "implementation_status": "see_layer3",
    }


def _row_from_protocol(proto: dict[str, Any]) -> MatrixRow:
    cid = proto["combination_id"]
    dims = _dims_from_protocol(proto)
    matrix_status = _matrix_status_from_protocol(proto)
    battery = proto.get("battery_level", "B")
    blocked = list(proto.get("blocked_by", []))
    artifact = (proto.get("expected_outputs") or [""])[0]
    return MatrixRow(
        combination_id=cid,
        design_family=dims["design_family"],
        estimator_family=dims["estimator_family"],
        inference_family=dims["inference_family"],
        geometry=dims["geometry"],
        treatment_structure=dims["treatment_structure"],
        estimand=dims["estimand"],
        effect_scale=dims["effect_scale"],
        interval_semantics=dims["interval_semantics"],
        data_level=dims["data_level"],
        supported_by_literature=dims["supported_by_literature"],
        implementation_status=dims["implementation_status"],
        statistical_protocol_status=proto["eligibility_status"],
        validation_matrix_status=matrix_status,
        blocked_by=blocked,
        required_bridge=_required_bridge(matrix_status, cid, blocked),
        required_d5_stat_artifact=artifact,
        minimum_battery_level=battery,
        required_metrics=list(proto.get("required_metrics", [])),
        known_failure_modes=blocked[:6],
        allowed_next_action=_next_action(matrix_status, battery, blocked),
        layer4_protocol_id=proto["protocol_id"],
        notes=proto.get("notes", "Mapped from Layer 4 protocol; ready for OC is not statistical proof."),
    )


def _extended_row(combo_id: str, proto_override: dict[str, Any] | None = None) -> MatrixRow:
    """Build matrix row for extended coverage; optional synthetic protocol dict."""
    dims = COMBO_DIMENSIONS[combo_id]
    if proto_override:
        proto = proto_override
    else:
        # Synthesize protocol-like dict from dimensions + known blockers
        blocked: list[str] = []
        elig = "ready_with_caveats"
        eligible = True
        battery = "B"
        outputs: list[str] = []
        if combo_id in (
            "AUGSYNTH-CONFORMAL",
            "AUGSYNTH-JK",
            "MCELL-POOLED-AUGSYNTH",
            "MCELL-POOLED-SCM-JK",
            "SUPERGEO-SCM-JK",
            "TRIM-SCM-JK",
            "TBR-UNIT-JK",
            "TBRRIDGE-BAYESIAN-REG",
            "SUPERGEO-AUGSYNTH-POINT",
            "TRIM-AUGSYNTH-POINT",
        ):
            eligible = False
            if "POOLED" in combo_id or "SUPERGEO" in combo_id or "TRIM" in combo_id:
                elig = "blocked_by_geometry"
                blocked = ["geometry_bridge_required"]
            elif combo_id in ("TBRRIDGE-BAYESIAN-REG",):
                elig = "blocked_by_architecture_gap"
                blocked = ["INV-015"]
            else:
                elig = "blocked_by_implementation_gap"
                blocked = ["layer5_extended_blocker"]
            battery = "A"
        elif combo_id in ("TROP-RESEARCH", "MTGP-RESEARCH", "BAYESIANTBR-MCMC", "SDID-POINT"):
            elig = "research_only_protocol"
            eligible = False
            battery = "B"
        elif combo_id == "TBRRIDGE-PLACEBO":
            elig = "blocked_by_implementation_gap"
            eligible = False
            blocked = ["placebo_not_wired_for_TBRRidge"]
            battery = "A"
        if combo_id == "TIER1-SCM-JK":
            outputs = ["D5-STAT-SCM-JK-001"]
        elif combo_id == "TBR-AGG-KFOLD":
            outputs = ["D5-STAT-TBR-AGG-001"]
        elif combo_id == "MCELL-AUGSYNTH-POINT":
            outputs = ["D5-STAT-AUGSYNTH-POINT-001"]
        elif combo_id == "MCELL-POOLED-SCM-JK":
            outputs = ["D5-STAT-MCELL-POOLED-001"]
        proto = {
            "combination_id": combo_id,
            "protocol_id": f"STAT-COMBO-{combo_id}",
            "eligibility_status": elig,
            "eligible_for_layer4": eligible,
            "blocked_by": blocked,
            "battery_level": battery,
            "expected_outputs": outputs,
            "required_metrics": [],
            "notes": "Layer 5 extended matrix row",
            "layer3_dependencies": [
                dims["design_family"],
                dims["estimator_family"],
                dims["inference_family"],
                dims["geometry"],
            ],
        }
    row = _row_from_protocol(proto)
    row.design_family = dims["design_family"]
    row.estimator_family = dims["estimator_family"]
    row.inference_family = dims["inference_family"]
    row.geometry = dims["geometry"]
    row.treatment_structure = dims["treatment_structure"]
    row.estimand = dims["estimand"]
    row.effect_scale = dims["effect_scale"]
    row.interval_semantics = dims["interval_semantics"]
    row.data_level = dims["data_level"]
    row.supported_by_literature = dims["supported_by_literature"]
    row.implementation_status = dims["implementation_status"]
    return row


def matrix_rows() -> list[MatrixRow]:
    l4 = load_layer4()
    combos = _layer4_combo_rows(l4)
    rows: list[MatrixRow] = []
    seen: set[str] = set()

    for cid, proto in sorted(combos.items()):
        rows.append(_row_from_protocol(proto))
        seen.add(cid)

    extended_ids = [
        "TIER1-SCM-JK",
        "MCELL-POOLED-SCM-JK",
        "MCELL-AUGSYNTH-POINT",
        "SUPERGEO-AUGSYNTH-POINT",
        "TRIM-AUGSYNTH-POINT",
        "TBR-AGG-KFOLD",
        "TBRRIDGE-PLACEBO",
        "SDID-POINT",
    ]
    for cid in extended_ids:
        if cid not in seen:
            rows.append(_extended_row(cid))
            seen.add(cid)

    return rows


def assert_layer4_combo_coverage(payload: dict[str, Any]) -> None:
    l4 = load_layer4()
    combo_ids = {r["combination_id"] for r in l4["rows"] if r.get("combination_id")}
    matrix_ids = {r["combination_id"] for r in payload["rows"]}
    missing = combo_ids - matrix_ids
    if missing:
        raise ValueError(f"Layer 4 combination protocols not in matrix: {missing}")


def build_combination_validation_matrix() -> dict[str, Any]:
    rows = matrix_rows()
    by_status: dict[str, int] = {}
    by_action: dict[str, int] = {}
    for r in rows:
        by_status[r.validation_matrix_status] = by_status.get(r.validation_matrix_status, 0) + 1
        by_action[r.allowed_next_action] = by_action.get(r.allowed_next_action, 0) + 1

    ready_ids = [
        r.combination_id
        for r in rows
        if r.validation_matrix_status
        in ("ready_for_oc_execution", "ready_for_oc_with_caveats")
    ]
    blocked_ids = [
        r.combination_id
        for r in rows
        if r.validation_matrix_status.startswith("blocked")
    ]

    payload = {
        "document_id": "METHOD-COMBINATION-VALIDATION-MATRIX-001",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "panel_exp/validation/method_combination_validation_matrix_001.py",
        "parent_artifact": "METHOD-STATISTICAL-VALIDATION-PROTOCOL-001",
        "validation_matrix_status_values": [
            "ready_for_oc_execution",
            "ready_for_oc_with_caveats",
            "blocked_before_oc",
            "blocked_needs_bridge",
            "research_only_oc",
            "quarantine_or_deprecate",
            "not_applicable",
        ],
        "allowed_next_action_values": list(
            {
                "run_smoke_protocol",
                "run_characterization_protocol",
                "run_calibration_protocol",
                "write_bridge_adr",
                "fix_implementation_gap",
                "quarantine_or_deprecate",
                "research_only",
                "no_action",
            }
        ),
        "d5_stat_execution_queue": list(D5_STAT_EXECUTION_QUEUE),
        "d5_stat_blocked_queue": list(D5_STAT_BLOCKED_QUEUE),
        "bridge_adr_queue": list(BRIDGE_ADR_QUEUE),
        "implementation_fix_queue": list(IMPLEMENTATION_FIX_QUEUE),
        "counts": {
            "rows_total": len(rows),
            "by_validation_matrix_status": by_status,
            "by_allowed_next_action": by_action,
            "ready_for_oc_count": len(ready_ids),
            "blocked_count": len(blocked_ids),
            "layer4_combo_rows_mapped": len(
                [r for r in load_layer4()["rows"] if r.get("combination_id")]
            ),
        },
        "known_blocked_combos": [
            "AUGSYNTH-CONFORMAL",
            "AUGSYNTH-JK",
            "MCELL-POOLED-AUGSYNTH",
            "MCELL-POOLED-SCM-JK",
            "SUPERGEO-SCM-JK",
            "TRIM-SCM-JK",
            "TBR-UNIT-JK",
            "TBRRIDGE-BAYESIAN-REG",
            "SUPERGEO-AUGSYNTH-POINT",
            "TRIM-AUGSYNTH-POINT",
        ],
        "known_ready_for_oc_combos": [
            "SCM-JK",
            "AUGSYNTH-POINT",
            "TBR-AGG-POINT",
            "DID-BOOTSTRAP",
        ],
        "rows": [r.to_dict() for r in rows],
    }
    assert_layer4_combo_coverage(payload)
    return payload


def write_archive(path: Path | None = None) -> Path:
    payload = build_combination_validation_matrix()
    if path is None:
        path = (
            _REPO_ROOT
            / "docs"
            / "track_d"
            / "archives"
            / "METHOD_COMBINATION_VALIDATION_MATRIX_001.json"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    out = write_archive()
    n = build_combination_validation_matrix()["counts"]["rows_total"]
    print(f"Wrote {out} ({n} matrix rows)")


if __name__ == "__main__":
    main()
