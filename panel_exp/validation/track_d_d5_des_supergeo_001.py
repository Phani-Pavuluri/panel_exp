"""D5-DES-SUPERGEO-001 — Supergeos separate-geometry characterization (research).

Characterizes ``SupergeoModel`` / registry ``supergeos`` without forcing the flat
unit-level SCM+JK D5-POW-001e contract. Emits structural geometry, estimand,
and readout-compatibility findings for Track E GEO-003.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from panel_exp.design.registry import get_design_registry
from panel_exp.design.supergeos import SupergeoModel
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

SupergeoOverallVerdict = Literal[
    "characterization_complete_separate_geometry",
    "blocked_for_flat_unit_readout",
    "requires_implementation_fix_before_oc",
]

TrackEStatusRecommendation = Literal[
    "characterization_required",
    "diagnostic_only",
    "blocked",
]


@dataclass(frozen=True)
class D5DesSupergeo001Config:
    scenario_name: str = "scm_low_signal"
    n_clusters: int = 5
    weight_method: str = "correlation"
    combo_min_size: int = 2
    combo_max_size: int = 5
    train_length: int = 28
    panel_sizes: tuple[int, ...] = (12, 16, 20)
    random_state: int = 20260606
    run_milp: bool = True


def _registry_snapshot() -> dict[str, Any]:
    reg = get_design_registry()
    spec = reg.resolve("supergeos")
    return {
        "registry_name": spec.name,
        "aliases": list(spec.aliases),
        "geo_run_supported": spec.geo_run_supported,
        "output_type": spec.output_type,
        "randomizer_cls": spec.randomizer_cls.__name__,
        "module_path": "panel_exp/design/supergeos.py",
        "entrypoint_documented": "SupergeoModel.run_design()",
        "entrypoint_inventory_typo": "SupergeoModel.run_model() noted in DESIGN-INVENTORY-001",
        "handler_registered": spec.run.__name__,
    }


def _build_wide_panel(n_geos: int, cfg: D5DesSupergeo001Config) -> pd.DataFrame:
    scenario = RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name]
    world = SyntheticWorld.generate(scenario)
    wide = world.to_panel_dataset().wide_data
    if wide.shape[0] > n_geos:
        wide = wide.iloc[:n_geos].copy()
    return wide


def _cluster_stats(model: SupergeoModel) -> dict[str, Any]:
    clusters = model.partitioning_heuristic()
    sizes = {int(k): len(v) for k, v in clusters.items()}
    largest = model.find_largest_cluster(clusters)
    return {
        "n_clusters_requested": model.n_clusters,
        "cluster_sizes": sizes,
        "largest_cluster_indices": list(largest),
        "largest_cluster_size": len(largest),
    }


def _combo_stats(
    model: SupergeoModel,
    cluster_indices: list[int],
    *,
    min_size: int,
    max_size: int,
) -> dict[str, Any]:
    combos = list(
        model.generate_combinations(cluster_indices, min_size, max_size, seed=42)
    )
    sizes = [len(c) for c in combos]
    covered = set()
    for c in combos:
        covered.update(c)
    return {
        "combo_min_size": min_size,
        "combo_max_size": max_size,
        "n_supergeo_combos": len(combos),
        "combo_size_distribution": {
            str(s): sizes.count(s) for s in sorted(set(sizes))
        },
        "markets_in_largest_cluster_covered_by_any_combo": len(covered),
        "largest_cluster_coverage_fraction": (
            len(covered) / len(cluster_indices) if cluster_indices else 0.0
        ),
    }


def _pre_period_balance(
    wide: pd.DataFrame,
    cluster_indices: list[int],
    train_length: int,
) -> dict[str, Any]:
    pre = wide.iloc[:, :train_length]
    market_means = pre.mean(axis=1)
    cluster_mean = float(market_means.iloc[cluster_indices].mean())
    other = [i for i in range(len(wide)) if i not in cluster_indices]
    other_mean = float(market_means.iloc[other].mean()) if other else float("nan")
    return {
        "train_length": train_length,
        "mean_pre_period_level_largest_cluster": cluster_mean,
        "mean_pre_period_level_other_markets": other_mean,
        "relative_level_ratio_cluster_vs_other": (
            cluster_mean / other_mean if other_mean and not math.isnan(other_mean) else None
        ),
    }


def _heterogeneity_within_cluster(
    wide: pd.DataFrame,
    cluster_indices: list[int],
    train_length: int,
) -> dict[str, Any]:
    pre = wide.iloc[cluster_indices, :train_length]
    row_means = pre.mean(axis=1)
    return {
        "within_cluster_pre_period_mean_cv": float(row_means.std() / row_means.mean())
        if row_means.mean() != 0
        else None,
        "within_cluster_pre_period_corr_mean": float(
            np.nanmean(pre.T.corr().values[np.triu_indices(len(cluster_indices), k=1)])
        )
        if len(cluster_indices) > 1
        else None,
    }


def _milp_coverage_mismatch(n_markets: int, cluster_indices: list[int]) -> dict[str, Any]:
    uncovered = sorted(set(range(n_markets)) - set(cluster_indices))
    return {
        "constraint_requires_each_market_index_assigned": True,
        "combo_generation_scope": "largest_kmeans_cluster_only",
        "n_markets_total": n_markets,
        "n_markets_in_combo_scope": len(cluster_indices),
        "n_markets_outside_combo_scope": len(uncovered),
        "outside_scope_indices": uncovered,
        "feasibility_note": (
            "run_design() adds sum(supergeo_vars[combo containing city]) == 1 for every "
            "market index 0..N-1, but supergeo combos are generated only from the largest "
            "cluster — MILP is structurally over-constrained when largest_cluster_size < N."
        ),
    }


def _run_milp_snapshot(model: SupergeoModel) -> dict[str, Any]:
    try:
        result_df = model.run_design()
        n_pairs = len(result_df)
        return {
            "milp_attempted": True,
            "milp_status": "completed",
            "n_selected_pairs": n_pairs,
            "output_columns": list(result_df.columns),
            "sample_output": result_df.head(3).to_dict(orient="records"),
        }
    except Exception as exc:  # noqa: BLE001 — research harness
        return {
            "milp_attempted": True,
            "milp_status": "failed",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "n_selected_pairs": 0,
        }


def _scale_comparison(
    wide: pd.DataFrame,
    cluster_indices: list[int],
) -> dict[str, Any]:
    market_totals = wide.sum(axis=1)
    k = min(3, len(cluster_indices))
    supergeo_example = wide.iloc[list(cluster_indices[:k])].sum(axis=0)
    market_mean = float(market_totals.mean())
    super_sum = float(supergeo_example.sum())
    return {
        "mean_market_total_outcome": market_mean,
        "mean_kmarket_supergeo_aggregate_total": super_sum,
        "k_markets_in_example_aggregate": k,
        "scale_ratio_supergeo_k_vs_single_market": (
            super_sum / market_mean if market_mean else None
        ),
    }


def _jk_feasibility_heuristic(
    combo_stats: dict[str, Any],
    milp: dict[str, Any],
) -> dict[str, Any]:
    n_combos = combo_stats["n_supergeo_combos"]
    n_pairs = milp.get("n_selected_pairs", 0)
    return {
        "flat_market_panel_jk": {
            "feasible": False,
            "reason": "Design output is supergeo pairs, not control/test_* assignment dict.",
        },
        "supergeo_unit_panel_jk": {
            "feasible": "unknown_requires_explicit_supergeo_unit_construction",
            "min_control_supergeo_units_for_jk": 2,
            "n_candidate_supergeo_combos": n_combos,
            "n_milp_selected_pairs": n_pairs,
            "note": (
                "Selected MILP rows are pairs of combos, not a partition into test/control "
                "supergeo units; JK readout needs a defined supergeo-unit panel and arm labels."
            ),
        },
    }


def readout_compatibility_matrix() -> list[dict[str, Any]]:
    return [
        {
            "instrument": "SCM+UnitJackKnife @ original market level",
            "geometry_mode": "single_cell (flat unit dict)",
            "compatibility": "blocked",
            "reason": "Supergeos does not emit market-level control/test_* assignment.",
        },
        {
            "instrument": "SCM+UnitJackKnife @ supergeo-unit level",
            "geometry_mode": "supergeo",
            "compatibility": "uncharacterized_requires_panel_builder",
            "reason": "No production path from SupergeoModel output to PanelDataset arms.",
        },
        {
            "instrument": "TBRRidge+Kfold @ market level",
            "geometry_mode": "single_cell",
            "compatibility": "blocked_without_assignment_bridge",
            "reason": "Same as 001c unit vs agg — needs explicit supergeo aggregation spec.",
        },
        {
            "instrument": "Geo PowerAnalysis (2-row agg)",
            "geometry_mode": "aggregated",
            "compatibility": "diagnostic_only_not_governed",
            "reason": "PowerAnalysis uses TBRRidge+Kfold on 2-row panel; not supergeo geometry.",
        },
        {
            "instrument": "D5-POW-001e null-monitor tensor",
            "geometry_mode": "design_method × single_cell/multi_cell",
            "compatibility": "excluded",
            "reason": "001e contract requires tier-1 assignment dict; supergeos blocked_for_scm_jk_oc.",
        },
    ]


def estimand_implications() -> dict[str, Any]:
    return {
        "declared_population": "Markets (DMAs) merged into supergeo aggregates; target population changes.",
        "primary_estimand_candidates": [
            {
                "id": "supergeo_pair_sales_contrast",
                "description": "Contrast between two selected supergeo aggregate sales trajectories (MILP pair output).",
                "comparable_to_geo.relative_att_post": False,
            },
            {
                "id": "supergeo_unit_att",
                "description": "ATT on a constructed supergeo-unit panel after explicit test/control labeling.",
                "comparable_to_geo.relative_att_post": False,
                "bridge_required": True,
            },
            {
                "id": "market_level_att",
                "description": "Standard geo unit-level ATT.",
                "comparable_to_geo.relative_att_post": True,
                "blocked_by_design_output": True,
            },
        ],
        "oc_tensor_representation": {
            "design_method_id": "supergeos",
            "geometry_mode": "supergeo",
            "measurement_instrument_id": "TBD_after_supergeo_panel_builder",
            "valid_without_bridge": False,
        },
    }


def track_e_status_recommendation(
    overall: SupergeoOverallVerdict,
) -> dict[str, Any]:
    return {
        "geo_003_card": "characterization_required",
        "refined_after_001": "characterization_required",
        "separate_geometry_design": True,
        "move_to_suitable": False,
        "move_to_diagnostic_only": False,
        "rationale": (
            "D5-DES-SUPERGEO-001 confirms separate geometry and blocks flat 001e readout. "
            "Supergeo-unit readout and estimand bridge are not implemented; MILP output is "
            "pair-selection not geo experiment assignment. Keep characterization_required "
            "until a supergeo panel builder + instrument OC exist (not MMM/promotion)."
        ),
        "e4_008_fixture": "Still valid — row may cite D5-DES-SUPERGEO-001 artifact.",
        "overall_verdict": overall,
    }


def characterize_panel(
    wide: pd.DataFrame,
    cfg: D5DesSupergeo001Config,
    *,
    run_milp: bool,
) -> dict[str, Any]:
    model = SupergeoModel(
        wide,
        n_clusters=cfg.n_clusters,
        weight_method=cfg.weight_method,
    )
    cluster = _cluster_stats(model)
    largest = cluster["largest_cluster_indices"]
    combo = _combo_stats(
        model,
        largest,
        min_size=cfg.combo_min_size,
        max_size=cfg.combo_max_size,
    )
    milp: dict[str, Any] = {"milp_attempted": False}
    if run_milp:
        milp = _run_milp_snapshot(
            SupergeoModel(
                wide.copy(),
                n_clusters=cfg.n_clusters,
                weight_method=cfg.weight_method,
            )
        )
    return {
        "n_markets": int(wide.shape[0]),
        "n_periods": int(wide.shape[1]),
        "market_ids_sample": list(wide.index[:5]),
        "clustering": cluster,
        "supergeo_combos": combo,
        "milp_coverage_mismatch": _milp_coverage_mismatch(len(wide), largest),
        "pre_period_balance": _pre_period_balance(wide, largest, cfg.train_length),
        "within_cluster_heterogeneity": _heterogeneity_within_cluster(
            wide, largest, cfg.train_length
        ),
        "scale": _scale_comparison(wide, largest),
        "jk_feasibility": _jk_feasibility_heuristic(combo, milp),
        "milp_run": milp,
    }


def build_d5_des_supergeo_001(
    cfg: D5DesSupergeo001Config | None = None,
    *,
    run_milp: bool | None = None,
) -> dict[str, Any]:
    cfg = cfg or D5DesSupergeo001Config()
    if run_milp is None:
        run_milp = cfg.run_milp

    panels: list[dict[str, Any]] = []
    for n in cfg.panel_sizes:
        wide = _build_wide_panel(n, cfg)
        panels.append(
            characterize_panel(wide, cfg, run_milp=run_milp)
        )

    milp_zero_rows = all(
        p.get("milp_run", {}).get("n_selected_pairs", 0) == 0 for p in panels
    )
    coverage_issues = all(
        p["milp_coverage_mismatch"]["n_markets_outside_combo_scope"] > 0 for p in panels
    )

    if coverage_issues:
        overall: SupergeoOverallVerdict = "requires_implementation_fix_before_oc"
    else:
        overall = "characterization_complete_separate_geometry"

    return {
        "artifact_id": "D5-DES-SUPERGEO-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "binding_docs": [
            "TRACK_D_DESIGN_METHOD_INVENTORY_001",
            "ROADMAP_DESIGN_READOUT_UPDATE_001",
            "TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001",
            "TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001",
            "AUDIT-009_track_e_completion_gate",
        ],
        "registry": _registry_snapshot(),
        "input_requirements": {
            "panel_data": "pd.DataFrame, index=market/DMA ids, columns=time periods, outcome values",
            "constructor_kwargs": ["n_clusters (default 5)", "weight_method (euclidean|correlation|dtw|cosine)"],
            "geo_experiment_design": "not supported (geo_run_supported=false)",
        },
        "output_structure": {
            "type": "pd.DataFrame",
            "columns": ["Supergeo_1", "Supergeo_2", "Total_Sales_1", "Total_Sales_2"],
            "semantics": "Selected supergeo combo pairs from MILP (not control/test_* dict)",
            "assignment_geometry": "supergeo clusters / MILP pairs",
        },
        "geometry_characterization": {
            "market_level_input": True,
            "supergeo_cluster_output": True,
            "original_markets_preserved_in_output": False,
            "markets_aggregated_within_supergeo": True,
            "pairing_semantics": "MILP selects low-weight supergeo pairs; not geo lift arms",
            "hardcoded_combo_bounds_in_run_design": [2, 5],
            "overrides_calculate_min_max_sizes": True,
        },
        "estimand_implications": estimand_implications(),
        "readout_compatibility": readout_compatibility_matrix(),
        "panel_characterizations": panels,
        "findings": [
            {
                "id": "D5-SUPERGEO-FIND-001",
                "severity": "high",
                "summary": "MILP assigns every market index but combos generated only from largest KMeans cluster.",
                "implication": "Structural mismatch; empty or meaningless pair selections on standard panels.",
            },
            {
                "id": "D5-SUPERGEO-FIND-002",
                "severity": "medium",
                "summary": "Output is supergeo pair DataFrame, not geo_runner assignment dict.",
                "implication": "Incompatible with D5-POW-001e and flat SCM+JK null-monitor contract.",
            },
            {
                "id": "D5-SUPERGEO-FIND-003",
                "severity": "medium",
                "summary": "run_design hardcodes combo sizes 2–5 and uses only largest cluster.",
                "implication": "Documented geometry differs from full-market supergeo design intent in module docstring.",
            },
            {
                "id": "D5-SUPERGEO-FIND-004",
                "severity": "low",
                "summary": "DESIGN-INVENTORY-001 lists entrypoint run_model(); implementation is run_design().",
                "implication": "Doc/inventory correction only.",
            },
        ],
        "milp_zero_selected_pairs_on_battery": milp_zero_rows,
        "overall_verdict": overall,
        "track_e": track_e_status_recommendation(overall),
        "excluded_from": ["D5-POW-001e", "tier_1_scm_jk_null_fpr_tensor"],
        "next_steps": [
            "D5-DES-TRIM-001",
            "D5-MCELL optimal-cell-count characterization",
            "Future: supergeo panel builder + supergeo-unit instrument OC (research)",
        ],
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
    cfg: D5DesSupergeo001Config | None = None,
    run_milp: bool | None = None,
) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_DES_SUPERGEO_001_results.json"
    )
    payload = build_d5_des_supergeo_001(cfg, run_milp=run_milp)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_artifact()
    print(f"Wrote {out}")
