"""D5-INF-002b — post-fix validation for INV-D3-001 unit jackknife LOO target."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.validation.track_d_d5_inf_002a import (
    D5Inf002aConfig,
    _summarize,
    run_one_replicate,
    write_artifact,
)

PostFixRecommendation = Literal[
    "accepted_deviation",
    "characterization_required",
    "restricted",
    "regression_open_inv",
]


@dataclass(frozen=True)
class D5Inf002bConfig(D5Inf002aConfig):
    """Same battery as D5-INF-002a; post-fix acceptance thresholds differ."""


def _decide_post_fix(
    *,
    mean_treated_noise_prod: float,
    mean_hw_ratio: float,
    mean_corr: float,
) -> tuple[PostFixRecommendation, str, str]:
    if (
        np.isfinite(mean_corr)
        and mean_corr > 0.995
        and np.isfinite(mean_hw_ratio)
        and 0.95 <= mean_hw_ratio <= 1.05
        and np.isfinite(mean_treated_noise_prod)
        and mean_treated_noise_prod < 0.05
    ):
        return (
            "accepted_deviation",
            "Post-fix production unit_jk matches literature reference and is stable "
            "under treated post-outcome noise.",
            "fix_accepted",
        )
    if (
        np.isfinite(mean_treated_noise_prod)
        and mean_treated_noise_prod < 0.10
        and np.isfinite(mean_hw_ratio)
        and mean_hw_ratio < 1.25
    ):
        return (
            "characterization_required",
            "Fix improved LOO target behavior; retain null-monitor-only pending broader OC.",
            "characterization_required",
        )
    return (
        "regression_open_inv",
        "Post-fix battery did not meet acceptance thresholds; keep INV-D3-001 open.",
        "continue_investigation",
    )


def run_d5_inf_002b(config: D5Inf002bConfig | None = None) -> dict[str, Any]:
    from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
    from panel_exp.validation.synthetic_world import SyntheticWorld

    cfg = config or D5Inf002bConfig()
    rows: list[dict[str, float | str]] = []

    for scenario_name in cfg.scenarios:
        base_scenario = RECOVERY_SCENARIO_REGISTRY[scenario_name]
        for i in range(cfg.n_mc):
            seed = cfg.random_state_base + i + (hash(scenario_name) % 10_000)
            from dataclasses import replace

            scenario = (
                base_scenario
                if base_scenario.random_state == seed
                else replace(base_scenario, random_state=seed)
            )
            panel = SyntheticWorld.generate(scenario).to_panel_dataset()
            if panel.num_control_units < 2:
                continue
            rows.append(
                {
                    **run_one_replicate(
                        panel,
                        alpha=cfg.alpha,
                        treated_post_noise_sd=cfg.treated_post_noise_sd,
                        control_post_noise_sd=cfg.control_post_noise_sd,
                        seed=seed,
                    ),
                    "scenario_name": scenario_name,
                }
            )

    treated_prod = [float(r["treated_noise_rel_change_production"]) for r in rows]
    hw_ratio = [float(r["post_hw_ratio_prod_over_ref"]) for r in rows]
    corr = [float(r["post_hw_corr"]) for r in rows]

    mean_treated_prod = _summarize(treated_prod)["mean"]
    mean_hw_ratio = _summarize(hw_ratio)["mean"]
    mean_corr = _summarize(corr)["mean"]

    recommendation, rationale, inv_disp = _decide_post_fix(
        mean_treated_noise_prod=mean_treated_prod,
        mean_hw_ratio=mean_hw_ratio,
        mean_corr=mean_corr,
    )

    return {
        "artifact_id": "D5-INF-002b",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "lane": "research",
        "investigation_id": "INV-D3-001",
        "finding_id": "D3-FIND-001",
        "inv_d3_001_fix_applied": True,
        "pre_fix_artifact": "docs/track_d/archives/D5_INF_002a_results.json",
        "config": asdict(cfg),
        "primary_metrics": {
            "post_hw_ratio_prod_over_ref": _summarize(hw_ratio),
            "post_hw_corr_prod_vs_ref": _summarize(corr),
            "treated_post_noise_rel_change_production": _summarize(treated_prod),
            "treated_post_noise_rel_change_reference": _summarize(
                [float(r["treated_noise_rel_change_reference"]) for r in rows]
            ),
        },
        "n_replicates": len(rows),
        "recommendation": recommendation,
        "rationale": rationale,
        "inv_d3_001_disposition": inv_disp,
        "d3_find_001_disposition": inv_disp,
        "calibration_eligibility_changed": False,
        "scm_unit_jackknife_governance": "calibration_eligible_null_monitor_only",
        "notes": [
            "Other estimator + UnitJackKnife pairings unchanged in governance.",
            "No TrustReport, Track B, or eligibility registry changes.",
        ],
    }
