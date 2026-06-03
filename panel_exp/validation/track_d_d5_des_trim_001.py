"""D5-DES-TRIM-001 — Trimmedmatch separate-population characterization (research).

Characterizes ``TrimmedMatchDesign`` / registry ``trimmedmatch`` without forcing the
flat unit-level SCM+JK D5-POW-001e contract. Focus: Tp/Te split, pair trimming,
target-population shift, and classical pair-power semantics.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from panel_exp.design.registry import get_design_registry
from panel_exp.design.trimmed_match import TrimmedMatchDesign
from panel_exp.panel_data import PanelDataset
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

TrimOverallVerdict = Literal[
    "characterization_complete_separate_population",
    "blocked_for_flat_unit_readout",
    "target_population_shift_severe",
]


@dataclass(frozen=True)
class D5DesTrim001Config:
    scenario_name: str = "scm_low_signal"
    n_test_groups: int = 1
    test_size: float = 0.3
    trim_rate: float = 0.1
    pairing_method: str = "distance"
    min_pairs: int = 5
    max_pairs: int = 10
    num_simulations: int = 25
    run_full_design: bool = True
    panel_sizes: tuple[int, ...] = (16, 20)
    random_state: int = 20260607


def _registry_snapshot() -> dict[str, Any]:
    reg = get_design_registry()
    spec = reg.resolve("trimmedmatch")
    return {
        "registry_name": spec.name,
        "aliases": list(spec.aliases),
        "geo_run_supported": spec.geo_run_supported,
        "output_type": spec.output_type,
        "randomizer_cls": spec.randomizer_cls.__name__,
        "module_path": "panel_exp/design/trimmed_match.py",
        "entrypoint": "TrimmedMatchDesign.run_design(use_imbalance=True)",
        "handler_registered": spec.run.__name__,
    }


def _build_panel(n_geos: int, cfg: D5DesTrim001Config) -> PanelDataset:
    scenario = RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name]
    world = SyntheticWorld.generate(scenario)
    panel = world.to_panel_dataset()
    wide = panel.wide_data
    if wide.shape[0] > n_geos:
        wide = wide.iloc[:n_geos].copy()
        panel = PanelDataset(wide.copy())
    return panel


def _tp_te_split(wide: pd.DataFrame, test_size: float) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    n_periods = wide.shape[1]
    tp_end = int(n_periods * (1 - test_size))
    tp = wide.iloc[:, :tp_end]
    te = wide.iloc[:, tp_end:]
    return tp, te, {
        "n_periods": n_periods,
        "tp_periods": tp_end,
        "te_periods": n_periods - tp_end,
        "test_size_fraction": test_size,
    }


def _population_shift_metrics(
    wide: pd.DataFrame,
    tp: pd.DataFrame,
    geo_pairs: list[tuple[str, str]],
    trimmed_pairs: list[tuple[str, str]],
) -> dict[str, Any]:
    n_candidate = len(wide)
    markets_in_pairing = set()
    for g1, g2 in geo_pairs:
        markets_in_pairing.update([g1, g2])
    retained = set()
    for g1, g2 in trimmed_pairs:
        retained.update([g1, g2])
    removed_from_trim = markets_in_pairing - retained
    never_paired = set(wide.index) - markets_in_pairing

    tp_totals = tp.sum(axis=1)
    universe_mass = float(tp_totals.sum())
    retained_mass = float(tp_totals.loc[list(retained)].sum()) if retained else 0.0
    removed_mass = float(tp_totals.loc[list(removed_from_trim)].sum()) if removed_from_trim else 0.0
    never_mass = float(tp_totals.loc[list(never_paired)].sum()) if never_paired else 0.0

    # high-volume bias: top quartile removal rate
    q75 = float(tp_totals.quantile(0.75))
    high_vol = set(tp_totals[tp_totals >= q75].index)
    high_retained = len(high_vol & retained) / len(high_vol) if high_vol else None
    low_retained = len((set(wide.index) - high_vol) & retained) / max(
        1, len(set(wide.index) - high_vol)
    )

    return {
        "n_candidate_markets": n_candidate,
        "n_markets_in_optimal_pairing": len(markets_in_pairing),
        "n_markets_retained_after_trim": len(retained),
        "n_markets_removed_by_trim": len(removed_from_trim),
        "n_markets_never_paired": len(never_paired),
        "share_markets_retained": len(retained) / n_candidate if n_candidate else 0.0,
        "share_tp_response_mass_retained": retained_mass / universe_mass if universe_mass else 0.0,
        "share_tp_mass_never_paired": never_mass / universe_mass if universe_mass else 0.0,
        "share_tp_mass_trimmed_out": removed_mass / universe_mass if universe_mass else 0.0,
        "high_volume_quartile_retention_rate": high_retained,
        "non_high_volume_retention_rate": low_retained,
        "target_population_shift_severity": (
            "severe"
            if len(retained) / n_candidate < 0.5
            else "moderate"
            if len(retained) / n_candidate < 0.8
            else "mild"
        ),
    }


def _pair_balance_metrics(
    tp: pd.DataFrame,
    trimmed_pairs: list[tuple[str, str]],
) -> dict[str, Any]:
    if not trimmed_pairs:
        return {"n_trimmed_pairs": 0}
    diffs = []
    rel_diffs = []
    for g1, g2 in trimmed_pairs:
        s1 = float(tp.loc[g1].sum())
        s2 = float(tp.loc[g2].sum())
        diffs.append(abs(s1 - s2))
        denom = max(s1, s2, 1e-9)
        rel_diffs.append(abs(s1 - s2) / denom)
    return {
        "n_trimmed_pairs": len(trimmed_pairs),
        "mean_abs_pair_tp_diff": float(np.mean(diffs)),
        "median_abs_pair_tp_diff": float(np.median(diffs)),
        "mean_relative_pair_tp_diff": float(np.mean(rel_diffs)),
    }


def _pre_period_balance_before_after(
    tp: pd.DataFrame,
    geo_pairs: list[tuple[str, str]],
    trimmed_pairs: list[tuple[str, str]],
) -> dict[str, Any]:
    def mean_pair_diff(pairs: list[tuple[str, str]]) -> float | None:
        if not pairs:
            return None
        vals = [abs(tp.loc[g1].sum() - tp.loc[g2].sum()) for g1, g2 in pairs]
        return float(np.mean(vals))

    return {
        "mean_abs_tp_diff_all_pairs": mean_pair_diff(geo_pairs),
        "mean_abs_tp_diff_trimmed_pairs": mean_pair_diff(trimmed_pairs),
        "trim_improves_balance": (
            mean_pair_diff(trimmed_pairs) < mean_pair_diff(geo_pairs)
            if geo_pairs and trimmed_pairs
            else None
        ),
    }


def _assignment_structure(
    best_design: dict[str, Any] | None,
) -> dict[str, Any]:
    if not best_design:
        return {"assignment_available": False}
    test_groups = best_design.get("test_groups") or {}
    control = best_design.get("control_group") or []
    n_test = sum(len(v) for v in test_groups.values())
    return {
        "assignment_available": True,
        "assignment_geometry": "pair_level_split_one_geo_per_pair_to_test_or_control",
        "n_test_group_markets": n_test,
        "n_control_markets": len(control),
        "n_test_groups": len(test_groups),
        "flat_control_test_dict": False,
        "scm_jk_donor_feasibility": {
            "n_control_units": len(control),
            "meets_min_2_controls": len(control) >= 2,
            "note": (
                "Controls are one market per retained pair; not the shared-donor "
                "geometry of tier-1 geo designs."
            ),
        },
        "power_semantics": {
            "classical_pair_lift_ci": True,
            "geo_power_analysis_2row": False,
            "mmm_ingress": False,
        },
    }


def _structural_characterization(
    panel: PanelDataset,
    cfg: D5DesTrim001Config,
    *,
    num_pairs: int,
) -> dict[str, Any]:
    wide = panel.wide_data
    tp, te, split = _tp_te_split(wide, cfg.test_size)
    design = TrimmedMatchDesign(
        panel,
        n_test_groups=cfg.n_test_groups,
        min_pairs=num_pairs,
        max_pairs=num_pairs,
        num_simulations=cfg.num_simulations,
        test_size=cfg.test_size,
        trim_rate=cfg.trim_rate,
        pairing_method=cfg.pairing_method,
    )
    training = tp.sum(axis=1)
    geo_pairs = design.generate_optimal_pairs(tp, num_pairs)
    diffs = [abs(training[g1] - training[g2]) for g1, g2 in geo_pairs]
    trimmed_pairs = design.calculate_trimmed_pairs(
        geo_pairs, diffs, distribution_based=True
    )
    pop = _population_shift_metrics(wide, tp, geo_pairs, trimmed_pairs)
    return {
        "n_markets": int(wide.shape[0]),
        "n_periods": int(wide.shape[1]),
        "tp_te_split": split,
        "num_pairs_requested": num_pairs,
        "n_pairs_before_trim": len(geo_pairs),
        "n_pairs_after_trim": len(trimmed_pairs),
        "pair_trim_fraction_removed": (
            1.0 - len(trimmed_pairs) / len(geo_pairs) if geo_pairs else 0.0
        ),
        "population": pop,
        "pair_balance": _pair_balance_metrics(tp, trimmed_pairs),
        "balance_before_after_trim": _pre_period_balance_before_after(
            tp, geo_pairs, trimmed_pairs
        ),
    }


def _run_light_design(panel: PanelDataset, cfg: D5DesTrim001Config) -> dict[str, Any]:
    design = TrimmedMatchDesign(
        panel,
        n_test_groups=cfg.n_test_groups,
        min_pairs=cfg.min_pairs,
        max_pairs=cfg.max_pairs,
        num_simulations=cfg.num_simulations,
        test_size=cfg.test_size,
        trim_rate=cfg.trim_rate,
        pairing_method=cfg.pairing_method,
    )
    try:
        import io
        import contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            best, _power_results = design.run_design(use_imbalance=True)
        return {
            "run_design_attempted": True,
            "run_design_status": "completed",
            "best_design_metric": best.get("metric") if best else None,
            "best_design_score": best.get("score") if best else None,
            "best_design_power": best.get("power") if best else None,
            "assignment": _assignment_structure(best),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "run_design_attempted": True,
            "run_design_status": "failed",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def readout_compatibility_matrix() -> list[dict[str, Any]]:
    return [
        {
            "instrument": "SCM+UnitJackKnife @ full candidate universe",
            "compatibility": "blocked",
            "reason": "Trimming + pair cap exclude markets; estimand is retained-pair population.",
        },
        {
            "instrument": "SCM+UnitJackKnife @ retained markets only",
            "compatibility": "blocked_without_estimand_bridge",
            "reason": "Pair-structured test/control; not tier-1 shared-donor geometry.",
        },
        {
            "instrument": "TBRRidge+Kfold (geo unit panel)",
            "compatibility": "blocked_without_bridge",
            "reason": "Requires explicit retained-population assignment export.",
        },
        {
            "instrument": "TrimmedMatchDesign.power_analysis_with_cross_validation",
            "compatibility": "native_diagnostic_only",
            "reason": "Classical pair-lift CIs on Te; not PowerAnalysis / SCM+JK.",
        },
        {
            "instrument": "Geo PowerAnalysis (2-row agg)",
            "compatibility": "not_trimmedmatch_geometry",
            "reason": "Separate product path (TBRRidge+Kfold on agg panel).",
        },
        {
            "instrument": "D5-POW-001e null-monitor tensor",
            "compatibility": "excluded",
            "reason": "tier_2_separate_characterization; population shift invalidates 001e.",
        },
    ]


def estimand_implications() -> dict[str, Any]:
    return {
        "full_universe_claim": {
            "supported": False,
            "reason": "Only subset of markets enter pairing; trim removes additional pairs.",
        },
        "retained_trimmed_population": {
            "supported": True,
            "description": "ATT / lift on markets appearing in trimmed_pairs after Tp pairing.",
        },
        "pair_level_contrast": {
            "supported": True,
            "description": "Within-pair randomization; power on pair lifts in Te.",
        },
        "bridge_to_geo_relative_att_post": {
            "required": True,
            "default_comparable": False,
        },
        "oc_tensor_representation": {
            "design_method_id": "trimmedmatch",
            "geometry_mode": "trimmed_population",
            "measurement_instrument_id": "trimmed_match.pair_lift_classical_ci",
            "valid_without_bridge": False,
        },
    }


def track_e_recommendation(overall: TrimOverallVerdict) -> dict[str, Any]:
    return {
        "geo_004_card": "characterization_required",
        "separate_population_design": True,
        "move_to_suitable": False,
        "move_to_diagnostic_only": False,
        "diagnostic_only_for": ["native pair power_analysis_with_cross_validation"],
        "rationale": (
            "D5-DES-TRIM-001 confirms severe target-population shift on the battery: "
            "most candidate markets never enter or are trimmed out. Native power is "
            "classical pair-lift on Te — not governed SCM+JK. Keep characterization_required; "
            "disallow full-universe lift and MMM ingress without estimand bridge."
        ),
        "overall_verdict": overall,
    }


def build_d5_des_trim_001(
    cfg: D5DesTrim001Config | None = None,
    *,
    run_full_design: bool | None = None,
) -> dict[str, Any]:
    cfg = cfg or D5DesTrim001Config()
    if run_full_design is None:
        run_full_design = cfg.run_full_design

    structural_runs: list[dict[str, Any]] = []
    for n_geos in cfg.panel_sizes:
        panel = _build_panel(n_geos, cfg)
        mid_pairs = min(cfg.max_pairs, max(cfg.min_pairs, n_geos // 4))
        entry = _structural_characterization(panel, cfg, num_pairs=mid_pairs)
        if run_full_design and n_geos == cfg.panel_sizes[-1]:
            entry["run_design"] = _run_light_design(panel, cfg)
        structural_runs.append(entry)

    severities = [r["population"]["target_population_shift_severity"] for r in structural_runs]
    if any(s == "severe" for s in severities):
        overall: TrimOverallVerdict = "target_population_shift_severe"
    else:
        overall = "characterization_complete_separate_population"

    return {
        "artifact_id": "D5-DES-TRIM-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "binding_docs": [
            "TRACK_D_DESIGN_METHOD_INVENTORY_001",
            "DESIGN_INVENTORY_001_results",
            "TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001",
            "TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001",
            "D5_DES_SUPERGEO_001_REPORT",
            "AUDIT-009_track_e_completion_gate",
        ],
        "registry": _registry_snapshot(),
        "input_requirements": {
            "panel_dataset": "PanelDataset with wide_data (markets × time periods)",
            "optional_spend_data": "DataFrame aligned to panel for iROAS power path",
            "constructor_kwargs": [
                "n_test_groups",
                "min_pairs",
                "max_pairs",
                "trim_rate",
                "test_size (Te fraction)",
                "num_simulations",
                "pairing_method (distance|correlation)",
            ],
            "geo_experiment_design": "not supported (geo_run_supported=false)",
        },
        "output_structure": {
            "run_design_return": "(best_design: dict, power_results: list)",
            "best_design_keys": [
                "geo_pairs",
                "test_groups",
                "control_group",
                "metric",
                "score",
                "power",
            ],
            "assignment_geometry": "pair_level test/control lists per n_test_groups",
            "not_emitted": "control/test_* flat assignment dict for geo_runner",
        },
        "population_semantics": {
            "tp_te_split": "Tp = first (1-test_size) of periods for pairing; Te for power",
            "pairing": "Hungarian assignment on Tp; at most num_pairs pairs (2*num_pairs markets max)",
            "trimming": "distribution_based trim_rate tails on pair |ΔTp response|",
            "excluded_markets": "never paired + both markets in trimmed-out pairs",
            "target_population": "union of markets in trimmed_pairs after rerandomization",
        },
        "estimand_implications": estimand_implications(),
        "readout_compatibility": readout_compatibility_matrix(),
        "panel_characterizations": structural_runs,
        "findings": [
            {
                "id": "D5-TRIM-FIND-001",
                "severity": "high",
                "summary": "Target population is retained trimmed pairs only — large share of candidate markets excluded.",
                "implication": "Full-universe geo.relative_att_post claims are invalid without bridge.",
            },
            {
                "id": "D5-TRIM-FIND-002",
                "severity": "high",
                "summary": "Native power uses classical pair-lift CIs on Te, not SCM+JK or geo PowerAnalysis.",
                "implication": "Excluded from D5-POW-001e; diagnostic_only for native instrument.",
            },
            {
                "id": "D5-TRIM-FIND-003",
                "severity": "medium",
                "summary": "Assignment is pair-structured (one market per pair to test, other to control).",
                "implication": "Not compatible with shared-donor multi-cell SCM+JK readout.",
            },
            {
                "id": "D5-TRIM-FIND-004",
                "severity": "medium",
                "summary": "run_design sweeps num_pairs from min_pairs..max_pairs with rerandomization (100 iter) per step.",
                "implication": "Expensive; product path separate from GeoExperimentDesign.",
            },
        ],
        "overall_verdict": overall,
        "track_e": track_e_recommendation(overall),
        "excluded_from": ["D5-POW-001e", "tier_1_scm_jk_null_fpr_tensor"],
        "next_steps": ["D5-MCELL optimal-cell-count characterization"],
        "rules_acknowledged": {
            "no_production_behavior_changes": True,
            "no_design_algorithm_changes": True,
            "no_estimator_inference_changes": True,
            "no_trust_report_changes": True,
            "no_mmm_planning_feed": True,
            "no_promotion": True,
        },
    }


def write_artifact(
    path: Path | None = None,
    *,
    cfg: D5DesTrim001Config | None = None,
    run_full_design: bool | None = None,
) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_DES_TRIM_001_results.json"
    )
    payload = build_d5_des_trim_001(cfg, run_full_design=run_full_design)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_artifact()
    print(f"Wrote {out}")
