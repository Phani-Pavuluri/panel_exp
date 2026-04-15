"""
Validate estimators and inference methods using Kansas (tax cuts) and California Prop 99 (smoking) datasets.

Tests:
1. Estimator × inference grid (AugSynthCVXPY, TBR, TBRRidge × KFold, BRB post_only, Placebo)
2. Placebo treated units (one fake treated control at a time; expect estimates ≈ 0)
3. Pre-period placebo (shift treatment into pre-period; expect ≈ 0)
4. Subsample stability (drop 20-30% controls; expect stable estimates)
5. Noise injection (add synthetic effect; expect recovery)
6. BRB-specific checks (residual pool, block length, failure rate, CI width)
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# Add panel_exp to path
_panel_exp = os.path.join(os.path.dirname(__file__), "..", "..", "..", "latest_pxp", "panel_exp")
if os.path.isdir(_panel_exp):
    sys.path.insert(0, os.path.dirname(_panel_exp))

from panel_exp.panel_data import PanelDataset, TimePeriod, long_df_to_paneldataset
from panel_exp.methods.tbr import TBR, TBRRidge
from panel_exp.methods.scm import AugSynthCVXPY

# -----------------------------------------------------------------------------
# Data paths
# -----------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent / ".." / ".." / ".." / "latest_pxp" / "panel_exp" / "examples" / "data"
if not DATA_DIR.exists():
    DATA_DIR = Path(__file__).resolve().parent / ".." / ".." / ".." / "panel_exp" / "examples" / "data"
KANSAS_PATH = DATA_DIR / "kansas_parsed.csv"
SMOKING_PATH = DATA_DIR / "smoking.csv"
OUTPUT_DIR = Path("/Users/ppavuluri/Desktop/FY26/Q1/Reddit/estimators_inference_grid_v1") / "validation_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# Dataset configs
# -----------------------------------------------------------------------------
@dataclass
class DatasetConfig:
    name: str
    path: Path
    time_col: str
    unit_col: str
    value_col: str
    treated_unit: str
    treatment_start: float  # year or year_qtr
    treatment_end: Optional[float] = None


KANSAS_CONFIG = DatasetConfig(
    name="Kansas",
    path=KANSAS_PATH,
    time_col="year_qtr",
    unit_col="state",
    value_col="lngdp",
    treated_unit="Kansas",
    treatment_start=2012.0,
)

SMOKING_CONFIG = DatasetConfig(
    name="Smoking",
    path=SMOKING_PATH,
    time_col="year",
    unit_col="state",
    value_col="cigsale",
    treated_unit="California",
    treatment_start=1988.0,
)


def load_dataset(cfg: DatasetConfig) -> pd.DataFrame:
    """Load and standardize dataset for panel format."""
    if not cfg.path.exists():
        raise FileNotFoundError(f"Dataset not found: {cfg.path}")
    df = pd.read_csv(cfg.path)
    # Drop unnamed index column if present
    if df.columns[0] == "" or "Unnamed" in str(df.columns[0]):
        df = df.drop(columns=[df.columns[0]], errors="ignore")
    df[cfg.unit_col] = df[cfg.unit_col].astype(str)
    df[cfg.time_col] = pd.to_numeric(df[cfg.time_col], errors="coerce")
    df = df.dropna(subset=[cfg.time_col, cfg.unit_col, cfg.value_col])
    return df


def build_panel(
    df: pd.DataFrame,
    cfg: DatasetConfig,
    treated_units: Optional[List[str]] = None,
    treatment_start: Optional[float] = None,
    treatment_end: Optional[float] = None,
    drop_control_frac: Optional[float] = None,
    rng: Optional[np.random.Generator] = None,
) -> PanelDataset:
    """Build PanelDataset from long df. Optionally subsample controls."""
    treated = treated_units or [cfg.treated_unit]
    treated = [str(t) for t in treated]
    start = treatment_start if treatment_start is not None else cfg.treatment_start
    end = treatment_end if treatment_end is not None else cfg.treatment_end

    if drop_control_frac is not None and drop_control_frac > 0:
        rng = rng or np.random.default_rng(42)
        all_units = df[cfg.unit_col].unique().tolist()
        controls = [u for u in all_units if u not in treated]
        n_drop = max(1, int(len(controls) * drop_control_frac))
        drop = rng.choice(controls, size=min(n_drop, len(controls) - 1), replace=False)
        df = df[~df[cfg.unit_col].isin(drop)]

    if end is None:
        pds = long_df_to_paneldataset(
            df, cfg.time_col, cfg.unit_col, cfg.value_col,
            treated_units=treated,
            treated_start_times=[start] * len(treated),
        )
    else:
        pds = long_df_to_paneldataset(
            df, cfg.time_col, cfg.unit_col, cfg.value_col,
            treated_units=treated,
            treated_start_times=[start] * len(treated),
            treated_end_times=[end] * len(treated),
        )
    pds.wide_data = pds.wide_data.fillna(0)
    return pds


def build_aggregated_panel_for_tbr(
    df: pd.DataFrame, cfg: DatasetConfig, treated: List[str], start: float, end: Optional[float] = None
) -> PanelDataset:
    """Build panel with aggregated control for TBR (requires 1 control unit)."""
    wide = df.pivot(index=cfg.unit_col, columns=cfg.time_col, values=cfg.value_col).fillna(0)
    control_units = [u for u in wide.index if u not in treated]
    if len(control_units) < 2:
        raise ValueError("Need at least 2 control units for aggregation")
    control_agg = wide.loc[control_units].sum(axis=0)
    treated_df = wide.loc[treated]
    if len(treated) > 1:
        treated_agg = treated_df.sum(axis=0)
    else:
        treated_agg = treated_df.iloc[0]
    agg_wide = pd.DataFrame({"treated": treated_agg, "control": control_agg}).T
    times = list(agg_wide.columns)
    start_idx = next((i for i, t in enumerate(times) if t >= start), 0)
    end_idx = len(times) - 1 if end is None else next((i for i, t in enumerate(times) if t <= end), len(times) - 1)
    if end is not None:
        periods = [TimePeriod(times[start_idx], times[end_idx])]
    else:
        periods = [TimePeriod(times[start_idx])]
    return PanelDataset(agg_wide, treated_periods=periods, treated_units=["treated"])


@dataclass
class RunResult:
    dataset: str
    test_name: str
    estimator: str
    inference: str
    estimate: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    ci_width: Optional[float] = None
    sign: Optional[int] = None
    error: Optional[str] = None
    brb_stats: Optional[Dict] = None
    placebo_fake_treated: Optional[List[str]] = None
    injected_effect: Optional[float] = None


def run_single(
    pds: PanelDataset,
    estimator_cls: type,
    inference: str,
    dataset_name: str,
    test_name: str,
    alpha: float = 0.1,
) -> RunResult:
    """Run one estimator × inference combination."""
    res = RunResult(dataset=dataset_name, test_name=test_name, estimator=estimator_cls.__name__, inference=inference)
    try:
        model = estimator_cls(inference=inference, alpha=alpha)
        inference_kwargs = {}
        if inference == "BlockResidualBootstrap":
            inference_kwargs = {
                "n_bootstrap": 100,
                "block_length": 7,
                "min_train_periods": 12,
                "refit_in_bootstrap": False,
                "refit_mode": "post_only",
                "ci_method": "bca",
            }
        model.run_analysis(pds, **inference_kwargs)

        y = np.asarray(model.results["y"])
        y_hat = np.asarray(model.results["y_hat"])
        if y.ndim > 1:
            y = y.sum(axis=1)
        if y_hat.ndim > 1:
            y_hat = y_hat.sum(axis=1)
        start_idx = pds.treated_start_idxs[0]
        end_idx = pds.treated_end_idxs[0] if hasattr(pds, "treated_end_idxs") else len(y) - 1
        effect = (y[start_idx : end_idx + 1] - y_hat[start_idx : end_idx + 1]).sum()
        res.estimate = float(effect)
        res.sign = 1 if effect > 0 else (-1 if effect < 0 else 0)

        if "y_lower" in model.results and "y_upper" in model.results:
            y_lo = np.asarray(model.results["y_lower"])
            y_hi = np.asarray(model.results["y_upper"])
            if y_lo.ndim > 1:
                y_lo, y_hi = y_lo.sum(axis=1), y_hi.sum(axis=1)
            cf_a = (y[start_idx : end_idx + 1] - y_hi[start_idx : end_idx + 1]).sum()
            cf_b = (y[start_idx : end_idx + 1] - y_lo[start_idx : end_idx + 1]).sum()
            ci_lower, ci_upper = sorted([float(cf_a), float(cf_b)])
            res.ci_lower = ci_lower
            res.ci_upper = ci_upper
            res.ci_width = float(ci_upper - ci_lower)

        if inference == "BlockResidualBootstrap" and "block_residual_bootstrap_stats" in model.results:
            brb = model.results["block_residual_bootstrap_stats"]
            res.brb_stats = dict(brb) if hasattr(brb, "items") else {}
            # Normalize commonly used BRB diagnostics for downstream checks.
            if "bootstrap_std" not in res.brb_stats:
                res.brb_stats["bootstrap_std"] = res.brb_stats.get("bootstrap_cumulative_std")
            if "bootstrap_failure_rate" not in res.brb_stats:
                fail = res.brb_stats.get("bootstrap_failed_draws", 0) or 0
                ok = res.brb_stats.get("bootstrap_successful_draws", 0) or 0
                total = fail + ok
                res.brb_stats["bootstrap_failure_rate"] = (fail / total) if total > 0 else None
    except Exception as e:
        res.error = str(e)
    return res


def main_grid(cfg: DatasetConfig, df: pd.DataFrame) -> List[RunResult]:
    """Run estimator × inference grid."""
    results = []
    pds = build_panel(df, cfg)
    estimators = [(TBRRidge, "TBRRidge"), (AugSynth, "AugSynth")]
    pds_tbr = None
    try:
        pds_tbr = build_aggregated_panel_for_tbr(df, cfg, [cfg.treated_unit], cfg.treatment_start)
        estimators.append((TBR, "TBR"))
    except Exception as e:
        print(f"  TBR skipped (aggregation): {e}")

    for est_cls, est_name in estimators:
        use_pds = pds_tbr if est_cls == TBR and pds_tbr is not None else pds
        for inf in ["Kfold", "BlockResidualBootstrap", "Placebo"]:
            if est_cls == TBR and inf == "Placebo":
                continue
            r = run_single(use_pds, est_cls, inf, cfg.name, "main_grid")
            results.append(r)
            status = "OK" if r.error is None else f"FAIL: {r.error}"
            print(f"  {est_name} + {inf}: estimate={r.estimate}, CI_width={r.ci_width} [{status}]")
    return results


def main_placebo_units(cfg: DatasetConfig, df: pd.DataFrame, n_trials: int = 5) -> List[RunResult]:
    """Placebo treated units: use one fake treated control at a time."""
    results = []
    rng = np.random.default_rng(42)
    all_units = df[cfg.unit_col].unique().tolist()
    controls = [u for u in all_units if u != cfg.treated_unit]
    if not controls:
        return results

    n_trials = min(n_trials, len(controls))
    fake_units = list(rng.choice(controls, size=n_trials, replace=False))

    for fake in fake_units:
        pds = build_panel(df, cfg, treated_units=[fake], rng=rng)
        for est_cls, est_name in [(TBRRidge, "TBRRidge"), (AugSynthCVXPY, "AugSynthCVXPY")]:
            for inf in ["Kfold", "BlockResidualBootstrap", "Placebo"]:
                r = run_single(pds, est_cls, inf, cfg.name, "placebo_units")
                r.placebo_fake_treated = [fake]
                results.append(r)
    return results


def main_pre_period_placebo(cfg: DatasetConfig, df: pd.DataFrame) -> List[RunResult]:
    """Pre-period placebo: choose an actual observed pre-period time from the dataset."""
    times = sorted(df[cfg.time_col].unique())
    pre_times = [t for t in times if t < cfg.treatment_start]
    if len(pre_times) < 12:
        return []

    # Choose fake_start by indexing directly into pre_times (never interpolate)
    fake_idx = min(max(int(round(0.7 * len(pre_times))) - 1, 4), len(pre_times) - 5)
    fake_start = pre_times[fake_idx]

    times_set = set(times)
    if fake_start not in times_set:
        nearest = sorted(times_set, key=lambda t: abs(t - fake_start))[:5]
        raise ValueError(
            f"Pre-period placebo: fake_start={fake_start!r} is not an observed time. "
            f"Nearest observed times: {nearest}. Dataset={cfg.name}"
        )

    pds = build_panel(df, cfg, treatment_start=fake_start)
    results = []
    for est_cls, est_name in [(TBRRidge, "TBRRidge"), (AugSynthCVXPY, "AugSynthCVXPY")]:
        for inf in ["Kfold", "BlockResidualBootstrap", "Placebo"]:
            r = run_single(pds, est_cls, inf, cfg.name, "pre_period_placebo")
            results.append(r)
    return results


def main_subsample(cfg: DatasetConfig, df: pd.DataFrame, drop_frac: float = 0.25, n_trials: int = 3) -> List[RunResult]:
    """Subsample stability: drop random controls."""
    results = []
    rng = np.random.default_rng(43)
    for trial in range(n_trials):
        pds = build_panel(df, cfg, drop_control_frac=drop_frac, rng=rng)
        for est_cls, est_name in [(TBRRidge, "TBRRidge"), (AugSynthCVXPY, "AugSynthCVXPY")]:
            for inf in ["Kfold", "BlockResidualBootstrap"]:
                r = run_single(pds, est_cls, inf, cfg.name, "subsample")
                results.append(r)
    return results


def main_noise_injection(
    cfg: DatasetConfig, df: pd.DataFrame, effect_pcts: Optional[List[float]] = None
) -> List[RunResult]:
    """Inject synthetic effect into post-period treated outcomes."""
    effect_pcts = effect_pcts or [0.05, 0.10, -0.10]
    results = []

    for effect_pct in effect_pcts:
        df_i = df.copy()
        start = cfg.treatment_start
        mask = (df_i[cfg.unit_col] == cfg.treated_unit) & (df_i[cfg.time_col] >= start)
        baseline = df_i.loc[mask, cfg.value_col]
        if baseline.empty:
            continue
        injected = baseline * (1 + effect_pct)
        df_i.loc[mask, cfg.value_col] = injected.values
        pds = build_panel(df_i, cfg)
        true_effect = float((injected - baseline).sum())

        for est_cls, est_name in [(TBRRidge, "TBRRidge"), (AugSynthCVXPY, "AugSynthCVXPY")]:
            for inf in ["Kfold", "BlockResidualBootstrap"]:
                r = run_single(pds, est_cls, inf, cfg.name, "noise_injection")
                r.injected_effect = true_effect
                results.append(r)
    return results


def compute_metrics(results: List[RunResult]) -> Dict[str, Any]:
    """Compute aggregate metrics."""
    ok = [r for r in results if r.error is None]
    placebo_units = [r for r in ok if r.test_name == "placebo_units"]
    pre_placebo = [r for r in ok if r.test_name == "pre_period_placebo"]
    noise = [r for r in ok if r.test_name == "noise_injection"]

    metrics = {
        "n_total": len(results),
        "n_ok": len(ok),
        "n_failed": len(results) - len(ok),
    }
    if placebo_units:
        excludes_zero = sum(1 for r in placebo_units if r.ci_lower is not None and r.ci_upper is not None and (r.ci_lower > 0 or r.ci_upper < 0))
        metrics["placebo_false_positive_rate"] = excludes_zero / len(placebo_units)
        metrics["placebo_estimate_mean"] = np.mean([r.estimate for r in placebo_units if r.estimate is not None])
        metrics["placebo_estimate_std"] = np.std([r.estimate for r in placebo_units if r.estimate is not None])
    if pre_placebo:
        excludes_zero = sum(1 for r in pre_placebo if r.ci_lower is not None and r.ci_upper is not None and (r.ci_lower > 0 or r.ci_upper < 0))
        metrics["pre_placebo_false_positive_rate"] = excludes_zero / len(pre_placebo)
        metrics["pre_placebo_estimate_mean"] = np.mean([r.estimate for r in pre_placebo if r.estimate is not None])
        metrics["pre_placebo_estimate_std"] = np.std([r.estimate for r in pre_placebo if r.estimate is not None])
    if noise:
        with_injected = [r for r in noise if r.injected_effect is not None and r.estimate is not None]
        if with_injected:
            biases = [r.estimate - r.injected_effect for r in with_injected]
            coverage = sum(1 for r in with_injected if r.ci_lower is not None and r.ci_upper is not None and r.ci_lower <= r.injected_effect <= r.ci_upper)
            metrics["injected_bias_mean"] = np.mean(biases)
            metrics["injected_coverage"] = coverage / len(with_injected)
    return metrics


def print_brb_checks(results: List[RunResult]) -> None:
    """Print BRB-specific validation checks."""
    brb_results = [r for r in results if r.inference == "BlockResidualBootstrap" and r.brb_stats]
    if not brb_results:
        return
    print("\n--- BRB-specific checks ---")
    for r in brb_results[:5]:
        s = r.brb_stats
        pool = s.get("residual_pool_size")
        bl = s.get("block_length")
        fail = s.get("bootstrap_failed_draws", 0)
        ok = s.get("bootstrap_successful_draws", 0)
        bstd = s.get("bootstrap_cumulative_std", s.get("bootstrap_std"))
        fail_rate = s.get("bootstrap_failure_rate")
        print(f"  {r.estimator} {r.dataset}: pool={pool}, block_len={bl}, fail_rate={fail_rate}, bootstrap_std={bstd}")
    # Compare CI widths
    kfold_results = {r.estimator: r for r in results if r.inference == "Kfold" and r.ci_width}
    for r in brb_results:
        kf = kfold_results.get(r.estimator)
        if kf and r.ci_width is not None and kf.ci_width is not None and kf.ci_width != 0:
            ratio = abs(r.ci_width) / abs(kf.ci_width)
            flag = "⚠" if ratio > 5 else "✓"
            print(f"  BRB/KFold CI width ratio ({r.estimator}): {ratio:.2f}x {flag}")


def main():
    print("=" * 70)
    print("Estimator × Inference Validation (Kansas + Smoking)")
    print("=" * 70)

    all_results = []
    configs = [KANSAS_CONFIG, SMOKING_CONFIG]

    for cfg in configs:
        if not cfg.path.exists():
            print(f"\n[SKIP] {cfg.name}: file not found at {cfg.path}")
            continue
        print(f"\n--- {cfg.name} ---")
        df = load_dataset(cfg)

        print("\n1. Main grid (estimator × inference)")
        all_results.extend(main_grid(cfg, df))

        print("\n2. Placebo treated units (one fake treated control at a time)")
        all_results.extend(main_placebo_units(cfg, df))

        print("\n3. Pre-period placebo (treatment in pre-period)")
        all_results.extend(main_pre_period_placebo(cfg, df))

        print("\n4. Subsample stability (drop 25% controls)")
        all_results.extend(main_subsample(cfg, df))

        print("\n5. Noise injection (+5%, +10%, -10%)")
        all_results.extend(main_noise_injection(cfg, df, effect_pcts=[0.05, 0.10, -0.10]))

    metrics = compute_metrics(all_results)
    print("\n" + "=" * 70)
    print("Metrics")
    print("=" * 70)
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    print_brb_checks(all_results)

    # Save results
    out_path = OUTPUT_DIR / "validation_results.jsonl"
    with open(out_path, "w") as f:
        for r in all_results:
            d = {
                "dataset": r.dataset,
                "test_name": r.test_name,
                "estimator": r.estimator,
                "inference": r.inference,
                "estimate": r.estimate,
                "ci_lower": r.ci_lower,
                "ci_upper": r.ci_upper,
                "ci_width": r.ci_width,
                "error": r.error,
            }
            if r.brb_stats:
                d["brb_residual_pool_size"] = r.brb_stats.get("residual_pool_size")
                d["brb_block_length"] = r.brb_stats.get("block_length")
                d["brb_bootstrap_failed_draws"] = r.brb_stats.get("bootstrap_failed_draws")
                d["brb_bootstrap_successful_draws"] = r.brb_stats.get("bootstrap_successful_draws")
                d["brb_bootstrap_failure_rate"] = r.brb_stats.get("bootstrap_failure_rate")
                d["brb_bootstrap_std"] = r.brb_stats.get("bootstrap_cumulative_std", r.brb_stats.get("bootstrap_std"))
                d["brb_ci_method"] = r.brb_stats.get("ci_method")
                d["brb_bootstrap_type"] = r.brb_stats.get("bootstrap_type")
            f.write(json.dumps(d) + "\n")
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
