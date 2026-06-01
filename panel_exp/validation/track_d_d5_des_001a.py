"""D5-DES-001a — pre-period vs full-panel greedy matching characterization (research).

Compares ``greedy_match_markets`` assignment when balancing on full ``wide_data``
vs pre-period columns only. Does not modify production assignment paths.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from panel_exp.design.assign import greedy_match_markets
from panel_exp.design.validation import standardized_mean_difference
from panel_exp.panel_data import PanelDataset

Recommendation = Literal[
    "fix",
    "restrict",
    "accepted_deviation",
    "continue_investigation",
]


@dataclass(frozen=True)
class D5Des001aConfig:
    n_mc: int = 120
    n_units: int = 24
    n_pre: int = 50
    n_post: int = 20
    post_unit_shift_sd: float = 12.0
    treatment_probability: float = 0.5
    random_state_base: int = 20260528


def synthesize_panel(
    *,
    n_units: int,
    n_pre: int,
    n_post: int,
    seed: int,
    post_unit_shift_sd: float,
) -> tuple[pd.DataFrame, int]:
    """Unit x time panel with optional post-period unit-specific level shifts."""
    rng = np.random.default_rng(seed)
    units = [f"u{i}" for i in range(n_units)]
    factor_pre = rng.normal(0, 1.0, n_pre)
    factor_post = rng.normal(0, 1.0, n_post)
    post_shifts = rng.normal(0, post_unit_shift_sd, n_units) if post_unit_shift_sd else np.zeros(n_units)
    rows: list[np.ndarray] = []
    for i in range(n_units):
        level = rng.normal(100.0, 15.0)
        pre = (
            level
            + np.linspace(0, 1, n_pre) * rng.normal(0, 3.0)
            + factor_pre * 8.0
            + rng.normal(0, 2.0, n_pre)
        )
        post = (
            level
            + post_shifts[i]
            + np.linspace(0, 1, n_post) * rng.normal(0, 3.0)
            + factor_post * 8.0
            + rng.normal(0, 2.0, n_post)
        )
        rows.append(np.concatenate([pre, post]))
    wide = pd.DataFrame(
        rows,
        index=units,
        columns=list(range(n_pre + n_post)),
    )
    return wide, n_pre


def _assign_greedy(
    wide: pd.DataFrame,
    *,
    seed: int,
    pre_only: bool,
    n_pre: int,
    treatment_probability: float,
) -> dict[str, list[str]]:
    use_wide = wide.iloc[:, :n_pre] if pre_only else wide
    panel = PanelDataset(use_wide.copy())
    design = greedy_match_markets(
        func_to_optimize="corr",
        treatment_probability=treatment_probability,
        random_state=seed,
    )
    return design.assign(panel_data=panel, n_test_grps=1)


def _test_units(assignment: dict[str, list]) -> set[str]:
    return set(assignment.get("test_0") or [])


def _period_means(wide: pd.DataFrame, units: list[str], col_slice: slice) -> np.ndarray:
    sub = wide.loc[units, wide.columns[col_slice]]
    return sub.mean(axis=1).to_numpy(dtype=float)


def _post_assignment_correlation(
    wide: pd.DataFrame, assignment: dict[str, list], n_pre: int
) -> float:
    units = list(wide.index)
    post_means = wide.loc[units, wide.columns[n_pre:]].mean(axis=1).to_numpy()
    flags = np.array([1.0 if u in _test_units(assignment) else 0.0 for u in units])
    if np.std(flags) < 1e-9 or np.std(post_means) < 1e-9:
        return 0.0
    return float(np.corrcoef(flags, post_means)[0, 1])


def _balance_corr_pre(
    wide: pd.DataFrame, assignment: dict[str, list], n_pre: int
) -> float:
    control = assignment.get("control") or []
    test = assignment.get("test_0") or []
    if not control or not test:
        return float("nan")
    c_pre = wide.loc[control, wide.columns[:n_pre]].sum(axis=0).to_numpy()
    t_pre = wide.loc[test, wide.columns[:n_pre]].sum(axis=0).to_numpy()
    if np.std(c_pre) < 1e-9 or np.std(t_pre) < 1e-9:
        return 0.0
    return float(np.corrcoef(c_pre, t_pre)[0, 1])


def _balance_corr_post(
    wide: pd.DataFrame, assignment: dict[str, list], n_pre: int
) -> float:
    control = assignment.get("control") or []
    test = assignment.get("test_0") or []
    if not control or not test:
        return float("nan")
    c_post = wide.loc[control, wide.columns[n_pre:]].sum(axis=0).to_numpy()
    t_post = wide.loc[test, wide.columns[n_pre:]].sum(axis=0).to_numpy()
    if np.std(c_post) < 1e-9 or np.std(t_post) < 1e-9:
        return 0.0
    return float(np.corrcoef(c_post, t_post)[0, 1])


def _smd_pre_post(
    wide: pd.DataFrame, assignment: dict[str, list], n_pre: int
) -> tuple[float, float]:
    control = assignment.get("control") or []
    test = assignment.get("test_0") or []
    if not control or not test:
        return float("nan"), float("nan")
    c_pre = _period_means(wide, control, slice(0, n_pre))
    t_pre = _period_means(wide, test, slice(0, n_pre))
    c_post = _period_means(wide, control, slice(n_pre, None))
    t_post = _period_means(wide, test, slice(n_pre, None))
    return standardized_mean_difference(c_pre, t_pre), standardized_mean_difference(
        c_post, t_post
    )


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def _simple_att_proxy(
    wide: pd.DataFrame, assignment: dict[str, list], n_pre: int
) -> float:
    """Naive post-period mean difference (test minus control), not causal."""
    control = assignment.get("control") or []
    test = assignment.get("test_0") or []
    if not control or not test:
        return float("nan")
    c = wide.loc[control, wide.columns[n_pre:]].values.mean()
    t = wide.loc[test, wide.columns[n_pre:]].values.mean()
    return float(t - c)


def run_one_replicate(
    wide: pd.DataFrame,
    n_pre: int,
    *,
    seed: int,
    treatment_probability: float,
) -> dict[str, float]:
    full = _assign_greedy(
        wide,
        seed=seed,
        pre_only=False,
        n_pre=n_pre,
        treatment_probability=treatment_probability,
    )
    pre_only = _assign_greedy(
        wide,
        seed=seed,
        pre_only=True,
        n_pre=n_pre,
        treatment_probability=treatment_probability,
    )
    smd_pre_f, smd_post_f = _smd_pre_post(wide, full, n_pre)
    smd_pre_p, smd_post_p = _smd_pre_post(wide, pre_only, n_pre)
    return {
        "jaccard_test_sets": _jaccard(_test_units(full), _test_units(pre_only)),
        "post_corr_full": _post_assignment_correlation(wide, full, n_pre),
        "post_corr_pre_only": _post_assignment_correlation(wide, pre_only, n_pre),
        "balance_corr_pre_full": _balance_corr_pre(wide, full, n_pre),
        "balance_corr_pre_pre_only": _balance_corr_pre(wide, pre_only, n_pre),
        "balance_corr_post_full": _balance_corr_post(wide, full, n_pre),
        "balance_corr_post_pre_only": _balance_corr_post(wide, pre_only, n_pre),
        "smd_pre_full": smd_pre_f,
        "smd_post_full": smd_post_f,
        "smd_pre_pre_only": smd_pre_p,
        "smd_post_pre_only": smd_post_p,
        "att_proxy_full": _simple_att_proxy(wide, full, n_pre),
        "att_proxy_pre_only": _simple_att_proxy(wide, pre_only, n_pre),
    }


def _summarize(samples: list[float]) -> dict[str, float]:
    arr = np.array([x for x in samples if np.isfinite(x)], dtype=float)
    if arr.size == 0:
        return {"mean": float("nan"), "std": float("nan"), "p95": float("nan")}
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "p95": float(np.percentile(np.abs(arr), 95)),
    }


def run_d5_des_001a(config: D5Des001aConfig | None = None) -> dict[str, Any]:
    cfg = config or D5Des001aConfig()
    rows: list[dict[str, float]] = []
    for i in range(cfg.n_mc):
        seed = cfg.random_state_base + i
        wide, n_pre = synthesize_panel(
            n_units=cfg.n_units,
            n_pre=cfg.n_pre,
            n_post=cfg.n_post,
            seed=seed,
            post_unit_shift_sd=cfg.post_unit_shift_sd,
        )
        rows.append(
            run_one_replicate(
                wide,
                n_pre,
                seed=seed,
                treatment_probability=cfg.treatment_probability,
            )
        )

    null_rows: list[dict[str, float]] = []
    for i in range(cfg.n_mc):
        seed = cfg.random_state_base + 10_000 + i
        wide, n_pre = synthesize_panel(
            n_units=cfg.n_units,
            n_pre=cfg.n_pre,
            n_post=cfg.n_post,
            seed=seed,
            post_unit_shift_sd=0.0,
        )
        null_rows.append(
            run_one_replicate(
                wide,
                n_pre,
                seed=seed,
                treatment_probability=cfg.treatment_probability,
            )
        )

    post_corr_full = [r["post_corr_full"] for r in rows]
    post_corr_pre = [r["post_corr_pre_only"] for r in rows]
    jaccard = [r["jaccard_test_sets"] for r in rows]
    post_balance_full = [r["balance_corr_post_full"] for r in rows]
    post_balance_pre = [r["balance_corr_post_pre_only"] for r in rows]

    mean_abs_post_corr_full = _summarize([abs(x) for x in post_corr_full])["mean"]
    mean_abs_post_corr_pre = _summarize([abs(x) for x in post_corr_pre])["mean"]
    mean_jaccard = _summarize(jaccard)["mean"]

    leakage_signal = mean_abs_post_corr_full - mean_abs_post_corr_pre
    post_balance_inflation = (
        _summarize(post_balance_full)["mean"] - _summarize(post_balance_pre)["mean"]
    )

    null_post_corr_full = [abs(r["post_corr_full"]) for r in null_rows]
    fp_rate_03 = float(np.mean([x > 0.3 for x in null_post_corr_full]))

    recommendation, rationale = _decide(
        leakage_signal=leakage_signal,
        mean_jaccard=mean_jaccard,
        post_balance_inflation=post_balance_inflation,
        fp_rate_03=fp_rate_03,
    )

    return {
        "artifact_id": "D5-DES-001a",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "lane": "research",
        "investigation_id": "INV-D1-001",
        "config": asdict(cfg),
        "hypothesis": (
            "Full-panel greedy matching uses post-treatment columns when present, "
            "increasing |corr(test, post_mean)| and post-period balance vs pre-only matching."
        ),
        "primary_metrics": {
            "post_assignment_corr_abs_full": _summarize([abs(x) for x in post_corr_full]),
            "post_assignment_corr_abs_pre_only": _summarize(
                [abs(x) for x in post_corr_pre]
            ),
            "leakage_signal_mean_abs_diff": leakage_signal,
            "test_set_jaccard_full_vs_pre_only": _summarize(jaccard),
            "balance_corr_post_full": _summarize(post_balance_full),
            "balance_corr_post_pre_only": _summarize(post_balance_pre),
            "post_balance_inflation": post_balance_inflation,
            "smd_pre_full": _summarize([r["smd_pre_full"] for r in rows]),
            "smd_post_full": _summarize([r["smd_post_full"] for r in rows]),
            "smd_pre_pre_only": _summarize([r["smd_pre_pre_only"] for r in rows]),
            "smd_post_pre_only": _summarize([r["smd_post_pre_only"] for r in rows]),
            "att_proxy_full": _summarize([r["att_proxy_full"] for r in rows]),
            "att_proxy_pre_only": _summarize([r["att_proxy_pre_only"] for r in rows]),
        },
        "null_dgp": {
            "post_unit_shift_sd": 0.0,
            "post_assignment_corr_abs_full": _summarize(null_post_corr_full),
            "false_positive_rate_abs_post_corr_gt_0.3": fp_rate_03,
        },
        "recommendation": recommendation,
        "rationale": rationale,
        "affected_pathways": [
            "panel_exp.design.geo_runner.run_geo_experiment_design",
            "panel_exp.design.geo_experiment_design.GeoExperimentDesign.run_design",
            "panel_exp.design.assign.greedy_match_markets.assign",
            "panel_exp.design.assign.Rerandomization (wraps base design)",
        ],
        "disposition_d1_find_001": _disposition_for_recommendation(recommendation),
    }


def _decide(
    *,
    leakage_signal: float,
    mean_jaccard: float,
    post_balance_inflation: float,
    fp_rate_03: float,
) -> tuple[Recommendation, str]:
    if mean_jaccard < 0.75:
        return (
            "restrict",
            "Full-panel vs pre-only matching produce materially different test sets "
            f"(mean Jaccard {mean_jaccard:.2f}); geo design should not balance on "
            "post-treatment columns when pre-period is defined.",
        )
    if leakage_signal > 0.12 and mean_jaccard < 0.85:
        return (
            "fix",
            "Full-panel matching materially changes assignments and increases "
            "post-outcome correlation with test arm vs pre-only matching.",
        )
    if leakage_signal > 0.08 or post_balance_inflation > 0.05:
        return (
            "restrict",
            "Moderate leakage signal: restrict geo greedy matching to pre-period "
            "columns or require explicit pre_treatment_period until fixed.",
        )
    if mean_jaccard > 0.92 and leakage_signal < 0.05 and fp_rate_03 < 0.15:
        return (
            "accepted_deviation",
            "Assignments stable and post-assignment correlation gap small under "
            "tested DGPs; document geo runner period contract.",
        )
    return (
        "continue_investigation",
        "Results ambiguous under tested DGPs; extend OC to production-like panels.",
    )


def _disposition_for_recommendation(rec: Recommendation) -> str:
    return {
        "fix": "investigating",
        "restrict": "restricted",
        "accepted_deviation": "accepted_deviation",
        "continue_investigation": "investigating",
    }[rec]


def write_artifact(payload: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
