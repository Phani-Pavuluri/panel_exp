"""METHOD-STATISTICAL-VALIDATION-PROTOCOL-001 — Layer 4 OC protocol register.

Defines validation plans from Layer 3 rows; does not run heavy OC or assign roles.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LAYER3_JSON = _REPO_ROOT / "docs/track_d/archives/METHOD_IMPLEMENTATION_VALIDATION_001.json"

EligibilityStatus = Literal[
    "ready_for_protocol",
    "ready_with_caveats",
    "blocked_by_implementation_gap",
    "blocked_by_architecture_gap",
    "blocked_by_geometry",
    "research_only_protocol",
    "deprecated_or_quarantine",
    "not_applicable",
]

BatteryLevel = Literal["A", "B", "C", "D", "E"]
ConfirmatoryMode = Literal["characterization", "confirmatory", "falsification_only", "blocked"]
AcceptanceClass = Literal[
    "hard_gate",
    "soft_gate",
    "diagnostic_threshold",
    "research_characterization_only",
    "not_thresholded_yet",
]

MethodType = Literal["design", "estimator", "inference", "wrapper", "orchestration", "combination"]


DGP_WORLD_CATALOG: tuple[str, ...] = (
    "clean_linear_additive",
    "weak_signal",
    "noisy_low_signal",
    "correlated_controls_collinearity",
    "treated_outside_donor_hull",
    "post_period_shock",
    "pre_period_trend_mismatch",
    "sparse_geo_low_donor_count",
    "multi_treated_multi_cell",
    "aggregate_two_row",
    "supergeo_geometry",
    "trimmed_pair_geometry",
    "null_no_effect",
    "positive_injected_lift",
    "negative_injected_lift",
    "heterogeneous_treatment_effects",
    "delayed_ramp_effect",
)

METRIC_CATALOG: tuple[str, ...] = (
    "null_false_positive_rate",
    "empirical_coverage",
    "bias",
    "mae",
    "rmse",
    "interval_width",
    "interval_orientation_validity",
    "lower_le_upper_rate",
    "negative_half_width_rate",
    "degenerate_interval_rate",
    "over_wide_interval_rate",
    "point_recovery_slope",
    "point_injected_ratio",
    "donor_stability",
    "treated_control_prefit_quality",
    "placebo_distribution_sanity",
    "fold_stability",
    "shock_sensitivity",
    "donor_count_sensitivity",
    "outside_hull_sensitivity",
    "uncertainty_band_calibration",
    "sign_error_rate",
    "abstention_blocked_rate",
)

BATTERY_LEVELS: tuple[str, ...] = ("A", "B", "C", "D", "E")

L3_TO_ELIGIBILITY: dict[str, EligibilityStatus] = {
    "implementation_validated": "ready_for_protocol",
    "implementation_validated_with_caveats": "ready_with_caveats",
    "implementation_gap": "blocked_by_implementation_gap",
    "architecture_gap": "blocked_by_architecture_gap",
    "identity_collision": "ready_with_caveats",
    "unsupported_geometry_not_blocked": "blocked_by_geometry",
    "requires_code_review": "blocked_by_implementation_gap",
    "research_only_not_validated": "research_only_protocol",
    "deprecated_or_quarantine_candidate": "deprecated_or_quarantine",
}


@dataclass
class ProtocolRow:
    protocol_id: str
    method_family: str
    combination_id: str
    method_type: MethodType
    eligible_for_layer4: bool
    eligibility_status: EligibilityStatus
    blocked_by: list[str]
    required_worlds: list[str]
    required_metrics: list[str]
    acceptance_criteria: list[dict[str, str]]
    battery_level: BatteryLevel
    minimum_mc_replicates: int
    confirmatory_or_characterization: ConfirmatoryMode
    layer3_dependencies: list[str]
    expected_outputs: list[str]
    promotion_allowed: bool = False
    trust_role_allowed: bool = False
    calibration_signal_allowed: bool = False
    mmm_allowed: bool = False
    layer3_implementation_name: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_layer3() -> dict[str, Any]:
    return json.loads(_LAYER3_JSON.read_text(encoding="utf-8"))


def _acceptance(
    metric: str,
    cls: AcceptanceClass,
    proposed: str,
) -> dict[str, str]:
    return {"metric": metric, "class": cls, "proposed_threshold": proposed}


def _default_metrics_for_type(
    method_type: MethodType, *, inference: bool = False
) -> list[str]:
    base = [
        "null_false_positive_rate",
        "bias",
        "mae",
        "abstention_blocked_rate",
    ]
    if inference or method_type == "inference":
        base.extend(
            [
                "empirical_coverage",
                "interval_width",
                "interval_orientation_validity",
                "lower_le_upper_rate",
                "negative_half_width_rate",
                "degenerate_interval_rate",
            ]
        )
    if method_type in ("estimator", "combination"):
        base.extend(
            [
                "point_recovery_slope",
                "point_injected_ratio",
                "treated_control_prefit_quality",
                "donor_stability",
                "shock_sensitivity",
                "outside_hull_sensitivity",
                "donor_count_sensitivity",
            ]
        )
    if method_type == "design":
        base.extend(["treated_control_prefit_quality", "donor_count_sensitivity"])
    return list(dict.fromkeys(base))


def _worlds_for_family(family_id: str, method_type: MethodType) -> list[str]:
    common = ["null_no_effect", "positive_injected_lift"]
    if family_id.startswith("DES-"):
        return common + [
            "pre_period_trend_mismatch",
            "sparse_geo_low_donor_count",
            "multi_treated_multi_cell",
        ]
    if family_id == "DES-SUPERGEO-001":
        return ["supergeo_geometry", "null_no_effect"]
    if family_id == "DES-TRIM-001":
        return ["trimmed_pair_geometry", "null_no_effect"]
    if family_id == "EST-TBR-001":
        return common + ["aggregate_two_row", "weak_signal"]
    if family_id.startswith("EST-"):
        worlds = common + [
            "clean_linear_additive",
            "weak_signal",
            "correlated_controls_collinearity",
            "treated_outside_donor_hull",
            "post_period_shock",
            "sparse_geo_low_donor_count",
        ]
        if "AUGSYNTH" in family_id:
            worlds += ["multi_treated_multi_cell", "outside_hull_sensitivity"]
        return worlds
    if family_id.startswith("INF-"):
        return common + [
            "clean_linear_additive",
            "noisy_low_signal",
            "post_period_shock",
        ]
    return common


def _battery_for_eligibility(status: EligibilityStatus) -> BatteryLevel:
    if status in ("blocked_by_implementation_gap", "blocked_by_architecture_gap", "blocked_by_geometry"):
        return "A"
    if status == "research_only_protocol":
        return "B"
    if status == "deprecated_or_quarantine":
        return "A"
    if status == "ready_with_caveats":
        return "B"
    return "C"


def _row_from_layer3(l3: dict[str, Any]) -> ProtocolRow:
    impl_status = l3["implementation_validation_status"]
    eligibility = L3_TO_ELIGIBILITY.get(impl_status, "blocked_by_implementation_gap")
    family = l3["method_family"]
    impl_name = l3["implementation_name"]
    mtype: MethodType = l3["method_type"]
    if mtype == "registry":
        mtype = "orchestration"
    blocked = not eligibility.startswith("ready")
    blocked_by: list[str] = []
    if blocked:
        blocked_by = list(l3.get("known_gaps", []))[:5]
        if impl_status == "unsupported_geometry_not_blocked":
            blocked_by.append("geometry_bridge_required")
    protocol_id = f"STAT-FAM-{family}-{impl_name}".upper().replace(" ", "_")[:64]
    battery = _battery_for_eligibility(eligibility)
    mc = 50 if battery == "A" else 200 if battery == "B" else 500
    confirm: ConfirmatoryMode = "blocked" if blocked else "characterization"
    if eligibility == "ready_for_protocol" and family in ("INF-PLACEBO-001",):
        confirm = "falsification_only"
    worlds = _worlds_for_family(family, mtype)
    metrics = _default_metrics_for_type(mtype, inference=mtype == "inference")
    acceptance = [
        _acceptance("lower_le_upper_rate", "hard_gate", "1.0"),
        _acceptance("negative_half_width_rate", "hard_gate", "0.0"),
        _acceptance("null_false_positive_rate", "not_thresholded_yet", "nominal_alpha (proposed)"),
        _acceptance("empirical_coverage", "not_thresholded_yet", "nominal_level (proposed)"),
    ]
    if blocked:
        acceptance.append(
            _acceptance("abstention_blocked_rate", "diagnostic_threshold", "must_block_or_document")
        )
    outputs = []
    if not blocked:
        outputs.append(f"D5-STAT-{family}-001")
    return ProtocolRow(
        protocol_id=protocol_id,
        method_family=family,
        combination_id="",
        method_type=mtype,
        eligible_for_layer4=not blocked,
        eligibility_status=eligibility,
        blocked_by=blocked_by,
        required_worlds=worlds,
        required_metrics=metrics,
        acceptance_criteria=acceptance,
        battery_level=battery,
        minimum_mc_replicates=mc,
        confirmatory_or_characterization=confirm,
        layer3_dependencies=[f"{family}:{impl_name}"],
        expected_outputs=outputs,
        layer3_implementation_name=impl_name,
        notes="Auto-mapped from Layer 3 row; protocol plan only — not statistical proof.",
    )


def _combo(
    combo_id: str,
    design: str,
    estimator: str,
    inference: str,
    geometry: str,
    eligibility: EligibilityStatus,
    blocked_by: list[str],
    worlds: list[str],
    battery: BatteryLevel,
    mc: int,
    confirm: ConfirmatoryMode,
    artifact: str,
    extra_metrics: list[str] | None = None,
) -> ProtocolRow:
    blocked = eligibility not in ("ready_for_protocol", "ready_with_caveats")
    metrics = _default_metrics_for_type("combination", inference=True)
    if extra_metrics:
        metrics = list(dict.fromkeys(metrics + extra_metrics))
    return ProtocolRow(
        protocol_id=f"STAT-COMBO-{combo_id}",
        method_family="COMBINATION",
        combination_id=combo_id,
        method_type="combination",
        eligible_for_layer4=not blocked,
        eligibility_status=eligibility,
        blocked_by=blocked_by,
        required_worlds=worlds,
        required_metrics=metrics,
        acceptance_criteria=[
            _acceptance("null_false_positive_rate", "not_thresholded_yet", "nominal (proposed)"),
            _acceptance("empirical_coverage", "not_thresholded_yet", "nominal (proposed)"),
            _acceptance("lower_le_upper_rate", "hard_gate", "1.0"),
            _acceptance("negative_half_width_rate", "hard_gate", "0.0"),
            _acceptance("point_recovery_slope", "soft_gate", "~1.0 clean world (proposed)"),
        ],
        battery_level=battery,
        minimum_mc_replicates=mc,
        confirmatory_or_characterization=confirm,
        layer3_dependencies=[design, estimator, inference, geometry],
        expected_outputs=[artifact] if not blocked else [],
        notes=f"{design} + {estimator} + {inference} @ {geometry}",
    )


def combination_protocol_rows() -> list[ProtocolRow]:
    null_worlds = ["null_no_effect", "positive_injected_lift", "clean_linear_additive"]
    unit_worlds = null_worlds + [
        "weak_signal",
        "sparse_geo_low_donor_count",
        "treated_outside_donor_hull",
    ]
    agg_worlds = ["null_no_effect", "positive_injected_lift", "aggregate_two_row"]
    return [
        _combo(
            "SCM-JK",
            "DES-GMM-001|DES-TIER1-RAND-001",
            "SCM/SyntheticControlCVXPY",
            "UnitJackKnife",
            "single_cell_unit",
            "ready_with_caveats",
            ["MAT-004 design-donor bridge", "INV-D1-001 caller audit"],
            unit_worlds,
            "C",
            500,
            "characterization",
            "D5-STAT-SCM-JK-001",
        ),
        _combo(
            "SCM-PLACEBO",
            "DES-*",
            "SCM",
            "Placebo",
            "single_treated",
            "ready_with_caveats",
            ["multi-treated scope limited"],
            unit_worlds + ["placebo_distribution_sanity"],
            "B",
            200,
            "falsification_only",
            "D5-STAT-SCM-PLACEBO-001",
            ["placebo_distribution_sanity"],
        ),
        _combo(
            "AUGSYNTH-POINT",
            "DES-*",
            "AugSynthCVXPY",
            "point_estimate",
            "single_cell_unit",
            "ready_with_caveats",
            ["G1-G8 fidelity open"],
            unit_worlds + ["outside_hull_sensitivity"],
            "B",
            300,
            "characterization",
            "D5-STAT-AUGSYNTH-POINT-001",
        ),
        _combo(
            "AUGSYNTH-JK",
            "DES-*",
            "AugSynthCVXPY",
            "UnitJackKnife",
            "single_cell_unit",
            "blocked_by_implementation_gap",
            ["IMPL-JK-001 unsafe strata", "JK not literature-default for ASCM"],
            unit_worlds,
            "A",
            50,
            "blocked",
            "D5-STAT-AUGSYNTH-JK-001",
        ),
        _combo(
            "AUGSYNTH-CONFORMAL",
            "DES-*",
            "AugSynthCVXPY",
            "Conformal",
            "single_cell_unit",
            "blocked_by_implementation_gap",
            ["IMPL-CONF-001", "new interval design required"],
            unit_worlds,
            "A",
            50,
            "blocked",
            "D5-STAT-AUGSYNTH-CONFORMAL-001",
        ),
        _combo(
            "AUGSYNTH-KFOLD",
            "DES-*",
            "AugSynthCVXPY",
            "Kfold",
            "single_cell_unit",
            "ready_with_caveats",
            ["diagnostic band only — not confirmatory CI"],
            unit_worlds,
            "B",
            200,
            "characterization",
            "D5-STAT-AUGSYNTH-KFOLD-001",
            ["fold_stability"],
        ),
        _combo(
            "TBR-AGG-POINT",
            "DES-GMM-001",
            "TBR",
            "point_estimate",
            "aggregate_two_row",
            "ready_with_caveats",
            ["design-analysis alignment", "INV-003 estimand"],
            agg_worlds,
            "B",
            200,
            "characterization",
            "D5-STAT-TBR-AGG-001",
        ),
        _combo(
            "TBR-UNIT-JK",
            "DES-*",
            "TBR",
            "UnitJackKnife",
            "single_cell_unit",
            "blocked_by_geometry",
            ["TBR asserts aggregate only — invalid on unit panel"],
            unit_worlds,
            "A",
            50,
            "blocked",
            "D5-STAT-TBR-UNIT-JK-001",
        ),
        _combo(
            "TBRRIDGE-KFOLD",
            "DES-*",
            "TBRRidge",
            "Kfold",
            "single_cell_unit",
            "ready_with_caveats",
            ["scale != SCM+JK", "diagnostic only"],
            unit_worlds,
            "B",
            200,
            "characterization",
            "D5-STAT-TBRRIDGE-KFOLD-001",
        ),
        _combo(
            "TBRRIDGE-TSKFOLD",
            "DES-*",
            "TBRRidge",
            "TimeSeriesKfold",
            "single_cell_unit",
            "ready_with_caveats",
            ["F-INF-003 re-verify exports"],
            unit_worlds + ["post_period_shock"],
            "B",
            200,
            "characterization",
            "D5-STAT-TBRRIDGE-TSKFOLD-001",
        ),
        _combo(
            "TBRRIDGE-BRB",
            "DES-*",
            "TBRRidge",
            "BlockResidualBootstrap",
            "single_cell_unit",
            "ready_with_caveats",
            ["DEF-002 bound ordering verified in prior OC"],
            unit_worlds,
            "C",
            500,
            "characterization",
            "D5-STAT-TBRRIDGE-BRB-001",
        ),
        _combo(
            "TBRRIDGE-JK",
            "DES-*",
            "TBRRidge",
            "UnitJackKnife",
            "single_cell_unit",
            "blocked_by_implementation_gap",
            ["high null FPR A16 — pivot calibration required"],
            unit_worlds,
            "B",
            300,
            "characterization",
            "D5-STAT-TBRRIDGE-JK-001",
        ),
        _combo(
            "TBRRIDGE-CONFORMAL",
            "DES-*",
            "TBRRidge",
            "Conformal",
            "single_cell_unit",
            "ready_with_caveats",
            ["exchangeability caveat on panels"],
            unit_worlds,
            "B",
            200,
            "characterization",
            "D5-STAT-TBRRIDGE-CONFORMAL-001",
        ),
        _combo(
            "DID-BOOTSTRAP",
            "DES-*",
            "DID",
            "DID_native_bootstrap",
            "single_cell_unit",
            "ready_with_caveats",
            ["relative CI policy deferred DEF-003"],
            unit_worlds + ["pre_period_trend_mismatch"],
            "B",
            200,
            "characterization",
            "D5-STAT-DID-BOOTSTRAP-001",
        ),
        _combo(
            "TBRRIDGE-BAYESIAN-REG",
            "DES-*",
            "TBRRidge",
            "Bayesian",
            "single_cell_unit",
            "blocked_by_architecture_gap",
            ["INV-015 registry Bayesian != MCMC"],
            unit_worlds,
            "A",
            50,
            "blocked",
            "D5-STAT-TBRRIDGE-BAYESIAN-001",
        ),
        _combo(
            "BAYESIANTBR-MCMC",
            "DES-*",
            "BayesianTBR",
            "Bayesian",
            "aggregate_or_unit",
            "research_only_protocol",
            ["RTP charter only"],
            unit_worlds,
            "B",
            100,
            "characterization",
            "D5-STAT-BAYESIANTBR-001",
        ),
        _combo(
            "TROP-RESEARCH",
            "n/a",
            "TROP",
            "point_estimate",
            "research",
            "research_only_protocol",
            ["not_literature_backed product path"],
            ["clean_linear_additive"],
            "B",
            50,
            "characterization",
            "D5-STAT-TROP-001",
        ),
        _combo(
            "MTGP-RESEARCH",
            "n/a",
            "MTGP",
            "Bayesian",
            "research",
            "research_only_protocol",
            ["optional JAX"],
            ["clean_linear_additive"],
            "B",
            50,
            "characterization",
            "D5-STAT-MTGP-001",
        ),
        _combo(
            "MCELL-PERCELL-SCM-JK",
            "DES-* multi_cell",
            "SCM",
            "UnitJackKnife",
            "multi_cell_per_cell",
            "ready_with_caveats",
            ["per-cell only — pooling ADR semantic guardrail"],
            unit_worlds + ["multi_treated_multi_cell"],
            "C",
            400,
            "characterization",
            "D5-STAT-MCELL-PERCELL-001",
        ),
        _combo(
            "MCELL-POOLED-AUGSYNTH",
            "DES-* multi_cell",
            "AugSynthCVXPY",
            "point_estimate",
            "pooled_multi_cell",
            "blocked_by_geometry",
            ["pooled causal lift not literature-backed", "ADR blocks semantics"],
            ["multi_treated_multi_cell"],
            "A",
            50,
            "blocked",
            "D5-STAT-MCELL-POOLED-001",
        ),
        _combo(
            "SUPERGEO-SCM-JK",
            "DES-SUPERGEO-001",
            "SCM",
            "UnitJackKnife",
            "supergeo",
            "blocked_by_geometry",
            ["F-GEO-003 bridge required", "A29 invalid flat readout"],
            ["supergeo_geometry"],
            "A",
            50,
            "blocked",
            "D5-STAT-SUPERGEO-BRIDGE-001",
        ),
        _combo(
            "TRIM-SCM-JK",
            "DES-TRIM-001",
            "SCM",
            "UnitJackKnife",
            "trimmed_pair",
            "blocked_by_geometry",
            ["F-GEO-004 bridge required", "A30 invalid flat readout"],
            ["trimmed_pair_geometry"],
            "A",
            50,
            "blocked",
            "D5-STAT-TRIM-BRIDGE-001",
        ),
    ]


def protocol_rows() -> list[ProtocolRow]:
    l3 = load_layer3()
    rows = [_row_from_layer3(r) for r in l3["rows"]]
    rows.extend(combination_protocol_rows())
    return rows


def assert_layer3_coverage(payload: dict[str, Any]) -> None:
    l3 = load_layer3()
    covered: set[str] = set()
    for row in payload["rows"]:
        for dep in row.get("layer3_dependencies", []):
            if ":" in dep:
                covered.add(dep)
    for l3_row in l3["rows"]:
        key = f"{l3_row['method_family']}:{l3_row['implementation_name']}"
        if key not in covered:
            # orchestration / combo-only coverage via COMBINATION family deps
            fam = l3_row["method_family"]
            if not any(fam in d for r in payload["rows"] for d in r["layer3_dependencies"]):
                if l3_row["method_family"] not in ("ORCH-001", "ORCH-002"):
                    raise ValueError(f"Layer 3 row not mapped: {key}")


def build_statistical_validation_protocol() -> dict[str, Any]:
    rows = protocol_rows()
    by_eligibility: dict[str, int] = {}
    by_battery: dict[str, int] = {}
    for r in rows:
        by_eligibility[r.eligibility_status] = by_eligibility.get(r.eligibility_status, 0) + 1
        by_battery[r.battery_level] = by_battery.get(r.battery_level, 0) + 1
    payload = {
        "document_id": "METHOD-STATISTICAL-VALIDATION-PROTOCOL-001",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "panel_exp/validation/method_statistical_validation_protocol_001.py",
        "parent_artifact": "METHOD-IMPLEMENTATION-VALIDATION-001",
        "dgp_world_catalog": list(DGP_WORLD_CATALOG),
        "metric_catalog": list(METRIC_CATALOG),
        "battery_levels": list(BATTERY_LEVELS),
        "eligibility_status_values": list(L3_TO_ELIGIBILITY.values()),
        "acceptance_classes": [
            "hard_gate",
            "soft_gate",
            "diagnostic_threshold",
            "research_characterization_only",
            "not_thresholded_yet",
        ],
        "battery_level_definitions": {
            "A": "smoke — callable path, schema, orientation, geometry guards",
            "B": "characterization — moderate MC null/injected; not promotion",
            "C": "calibration — larger MC FPR/coverage/interval semantics",
            "D": "stress — shocks, donor stress, hull, multi-cell, trim/supergeo",
            "E": "promotion-candidate — not authorized by this artifact",
        },
        "counts": {
            "rows_total": len(rows),
            "family_rows": sum(1 for r in rows if r.method_type != "combination"),
            "combination_rows": sum(1 for r in rows if r.method_type == "combination"),
            "by_eligibility": by_eligibility,
            "by_battery": by_battery,
        },
        "known_blocked_combos": [
            "AUGSYNTH-CONFORMAL",
            "AUGSYNTH-JK",
            "MCELL-POOLED-AUGSYNTH",
            "SUPERGEO-SCM-JK",
            "TRIM-SCM-JK",
            "TBR-UNIT-JK",
            "TBRRIDGE-BAYESIAN-REG",
        ],
        "rows": [r.to_dict() for r in rows],
    }
    assert_layer3_coverage(payload)
    return payload


def write_archive(path: Path | None = None) -> Path:
    payload = build_statistical_validation_protocol()
    if path is None:
        path = (
            _REPO_ROOT
            / "docs"
            / "track_d"
            / "archives"
            / "METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.json"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    out = write_archive()
    n = build_statistical_validation_protocol()["counts"]["rows_total"]
    print(f"Wrote {out} ({n} protocol rows)")


if __name__ == "__main__":
    main()
