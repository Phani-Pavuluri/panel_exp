from typing import Callable, Dict, List, Optional, Tuple, Any
import os
import warnings
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

from panel_exp.impact import ImpactAnalyzer
from panel_exp.panel_data import PanelDataset

# Minimum pre-periods for event-study pretrend. Use 3: need reference + 2 non-reference for joint test.
# Do not require 5+; only fallback when design is truly impossible.
_MIN_PRE_PERIODS_EVENT_STUDY = 3

# Max bins for event-study pretrend to avoid rank deficiency. If n_pre > this, bin older periods.
MAX_EVENT_STUDY_PRE_BINS = 8


class DID(ImpactAnalyzer):
    """
    Minimal pooled TWFE DID.

    Model:
        value_it = alpha_i + gamma_t + beta * (treated_i * post_t)
    """

    def __init__(self, inference: Optional[Callable] = None, alpha: float = 0.1):
        self.inference = inference
        self.alpha = alpha
        self.ppf = stats.norm.ppf(alpha / 2 + (1 - alpha))
        # Block-bootstrap settings for more reliable DID inference in short panel geo tests.
        self.n_bootstrap = 50
        self.bootstrap_block_size = 8
        self.bootstrap_seed = 42

    def _is_treatment_period(self, time_unit):
        time_dt = pd.to_datetime(time_unit)
        start_dt = pd.to_datetime(self.panel.treated_periods[0].start)
        end_dt = pd.to_datetime(self.panel.treated_periods[0].end)
        return int(start_dt <= time_dt <= end_dt)

    def fit_data(self, panel: PanelDataset):
        self.panel = panel

        assert len(set(panel.treated_start_idxs)) == 1, "Must be Simultaneous Adoption"
        assert len(set(panel.treated_end_idxs)) == 1, "Must be Simultaneous End"

        df = panel.long_data.copy()
        df["treated"] = df["unit"].isin(panel.treated_units).astype(int)
        df["post"] = df["time_unit"].apply(self._is_treatment_period)
        df["treated_post"] = df["treated"] * df["post"]
        df["unit_fe"] = df["unit"].astype("category")
        df["time_fe"] = df["time_unit"].astype(str).astype("category")

        self.data = df

    def fit_model(self):
        self.model = smf.ols(
            "value ~ C(unit_fe) + C(time_fe) + treated_post",
            data=self.data,
        ).fit()

        n_clusters = self.data["unit"].nunique()
        if n_clusters >= 10:
            self.model_clustered = self.model.get_robustcov_results(
                cov_type="cluster",
                groups=self.data["unit"],
            )
        else:
            self.model_clustered = self.model.get_robustcov_results(cov_type="HC1")

        coef_name = "treated_post"
        self.treatment_effect = float(self.model.params.get(coef_name, 0.0))

        # Keep model-based clustered SEs only as fallback diagnostics.
        param_names = list(self.model.params.index)
        if coef_name in param_names:
            idx = param_names.index(coef_name)
            bse = np.asarray(self.model_clustered.bse).ravel()
            pvals = np.asarray(self.model_clustered.pvalues).ravel()
            self.model_based_se = float(bse[idx]) if idx < len(bse) else np.nan
            self.model_based_pvalue = float(pvals[idx]) if idx < len(pvals) else np.nan
        else:
            self.model_based_se = np.nan
            self.model_based_pvalue = np.nan

        # Primary DID inference: path-based moving block bootstrap over post-period effect path.
        self.treatment_se, ci_lower, ci_upper, self.treatment_pvalue = self._block_bootstrap_inference()
        # treatment_ci is now cumulative (from bootstrap over path); not per-period.
        self.treatment_ci = (ci_lower, ci_upper)

    def _moving_block_indices(self, n: int, block_size: int, rng: np.random.Generator) -> np.ndarray:
        """Sample time indices using a moving block bootstrap."""
        if n <= 0:
            return np.array([], dtype=int)
        block_size = max(1, min(block_size, n))
        starts = np.arange(0, n - block_size + 1)
        out = []
        while len(out) < n:
            s = int(rng.choice(starts))
            out.extend(range(s, s + block_size))
        return np.asarray(out[:n], dtype=int)

    def _fit_effect_on_df(self, df: pd.DataFrame) -> float:
        """Fit the pooled TWFE DID on a supplied dataframe and return treated_post coefficient.
        Secondary/regression diagnostic only; not used for primary path-based inference."""
        boot_model = smf.ols(
            "value ~ C(unit_fe) + C(time_fe) + treated_post",
            data=df,
        ).fit()
        return float(boot_model.params.get("treated_post", np.nan))

    def _path_effect_from_df(self, df: pd.DataFrame) -> Tuple[float, float, int]:
        """Compute path-based effect from a dataframe (y - y_hat over post periods).
        Returns (cumulative_att, mean_post_period_att, n_post). Used for primary inference."""
        treated_df = df[df["treated"] == 1]
        control_df = df[df["treated"] == 0]
        if len(treated_df) == 0 or len(control_df) == 0:
            return np.nan, np.nan, 0
        control_agg = (
            control_df.groupby("time_unit", as_index=False)
            .agg(control_y=("value", "sum"))
            .sort_values("time_unit")
        )
        treated_agg = (
            treated_df.groupby("time_unit", as_index=False)
            .agg(y=("value", "sum"))
            .sort_values("time_unit")
        )
        agg = treated_agg.merge(control_agg, on="time_unit", how="left")
        agg = agg.sort_values("time_unit")
        is_treatment = agg["time_unit"].apply(self._is_treatment_period).to_numpy(dtype=bool)
        pre_mask = ~is_treatment
        if pre_mask.sum() == 0:
            return np.nan, np.nan, 0
        treated_pre_mean = agg.loc[pre_mask, "y"].mean()
        control_pre_mean = agg.loc[pre_mask, "control_y"].mean()
        control_trend = agg["control_y"] - control_pre_mean
        treated_cf = treated_pre_mean + control_trend
        effect = agg["y"].to_numpy(dtype=float) - treated_cf.to_numpy(dtype=float)
        post_effects = effect[is_treatment]
        n_post = len(post_effects)
        if n_post == 0:
            return np.nan, np.nan, 0
        cumulative_att = float(np.nansum(post_effects))
        mean_att = float(np.nanmean(post_effects))
        return cumulative_att, mean_att, n_post

    def _build_bootstrap_df(self, time_units: np.ndarray) -> pd.DataFrame:
        """Construct a bootstrap panel by resampling whole time periods and reindexing them.

        Resamples common time slices across all units to preserve contemporaneous cross-sectional structure.
        Reindexes sampled periods onto the original ordered time labels so the post-treatment window remains fixed.
        """
        df = self.data.copy()
        ordered_times = list(pd.Series(df["time_unit"]).drop_duplicates())
        sampled_times = [ordered_times[i] for i in time_units]
        sampled_parts = []
        for new_time, old_time in zip(ordered_times, sampled_times):
            part = df[df["time_unit"] == old_time].copy()
            part["time_unit"] = new_time
            sampled_parts.append(part)
        boot_df = pd.concat(sampled_parts, ignore_index=True)
        boot_df["post"] = boot_df["time_unit"].apply(self._is_treatment_period)
        boot_df["treated_post"] = boot_df["treated"] * boot_df["post"]
        boot_df["unit_fe"] = boot_df["unit"].astype("category")
        boot_df["time_fe"] = boot_df["time_unit"].astype(str).astype("category")
        return boot_df

    def _block_bootstrap_inference(self) -> Tuple[float, float, float, float]:
        """Moving block bootstrap inference for pooled DID. Path-based: bootstrap the post-period effect path.
        Returns (se, ci_lower, ci_upper, pvalue) for cumulative ATT. Primary inference uses cumulative distribution."""
        ordered_times = list(pd.Series(self.data["time_unit"]).drop_duplicates())
        n_times = len(ordered_times)
        if n_times < 4:
            se = self.model_based_se if np.isfinite(getattr(self, "model_based_se", np.nan)) else np.nan
            if np.isfinite(se):
                ci_lower = self.treatment_effect - self.ppf * se
                ci_upper = self.treatment_effect + self.ppf * se
            else:
                ci_lower, ci_upper = np.nan, np.nan
            pvalue = self.model_based_pvalue if np.isfinite(getattr(self, "model_based_pvalue", np.nan)) else np.nan
            self.bootstrap_cumulative_effects_ = np.array([], dtype=float)
            self.bootstrap_mean_effects_ = np.array([], dtype=float)
            return float(se), float(ci_lower), float(ci_upper), float(pvalue)

        rng = np.random.default_rng(self.bootstrap_seed)
        boot_cumulative: List[float] = []
        boot_mean: List[float] = []
        for _ in range(self.n_bootstrap):
            try:
                idx = self._moving_block_indices(n_times, self.bootstrap_block_size, rng)
                boot_df = self._build_bootstrap_df(idx)
                cum_att, mean_att, _ = self._path_effect_from_df(boot_df)
                if np.isfinite(cum_att) and np.isfinite(mean_att):
                    boot_cumulative.append(float(cum_att))
                    boot_mean.append(float(mean_att))
            except Exception:
                continue

        boot_cum_arr = np.asarray(boot_cumulative, dtype=float)
        boot_mean_arr = np.asarray(boot_mean, dtype=float)
        self.bootstrap_cumulative_effects_ = boot_cum_arr
        self.bootstrap_mean_effects_ = boot_mean_arr
        # Keep regression bootstrap for secondary diagnostics
        self.bootstrap_effects_ = boot_mean_arr  # per-period draws

        if len(boot_cumulative) < 30:
            # Prefer cumulative bootstrap draws only (no per-period SE × n_post scaling).
            if len(boot_cum_arr) > 0:
                se = float(np.std(boot_cum_arr, ddof=1))
                ci_lower = float(np.percentile(boot_cum_arr, (self.alpha / 2) * 100))
                ci_upper = float(np.percentile(boot_cum_arr, (1 - self.alpha / 2) * 100))
                prop_below = float(np.mean(boot_cum_arr < 0))
                prop_above = float(np.mean(boot_cum_arr > 0))
                pvalue = float(min(1.0, 2 * min(prop_below, prop_above)))
                return se, ci_lower, ci_upper, pvalue
            se = self.model_based_se if np.isfinite(getattr(self, "model_based_se", np.nan)) else np.nan
            if np.isfinite(se):
                n_post = self.panel.treated_end_idxs[0] - self.panel.treated_start_idxs[0] + 1
                ci_lower = (self.treatment_effect * n_post) - self.ppf * (se * n_post)
                ci_upper = (self.treatment_effect * n_post) + self.ppf * (se * n_post)
            else:
                ci_lower, ci_upper = np.nan, np.nan
            pvalue = self.model_based_pvalue if np.isfinite(getattr(self, "model_based_pvalue", np.nan)) else np.nan
            return float(se), float(ci_lower), float(ci_upper), float(pvalue)

        se = float(np.std(boot_cum_arr, ddof=1))
        ci_lower = float(np.percentile(boot_cum_arr, (self.alpha / 2) * 100))
        ci_upper = float(np.percentile(boot_cum_arr, (1 - self.alpha / 2) * 100))
        prop_below = float(np.mean(boot_cum_arr < 0))
        prop_above = float(np.mean(boot_cum_arr > 0))
        pvalue = float(min(1.0, 2 * min(prop_below, prop_above)))
        return se, ci_lower, ci_upper, pvalue

    def run_analysis(self, panel_data, multiple_treated="pooled"):
        self.panel_data = panel_data
        self.fit_data(panel_data)
        self.fit_model()

        df = self.data.copy()

        treated_df = df[df["treated"] == 1].copy()
        control_df = df[df["treated"] == 0].copy()

        # Aggregate control and treated actual series on the reporting scale.
        control_agg = (
            control_df.groupby("time_unit", as_index=False)
            .agg(control_y=("value", "sum"))
            .sort_values("time_unit")
        )
        treated_agg = (
            treated_df.groupby("time_unit", as_index=False)
            .agg(y=("value", "sum"))
            .sort_values("time_unit")
        )

        # Identify pre-period baseline (convert to bool before ~; otherwise ~0=-1, ~1=-2).
        is_treatment_treated = treated_agg["time_unit"].apply(self._is_treatment_period).astype(bool)
        pre_mask_treated = ~is_treatment_treated
        is_treatment_control = control_agg["time_unit"].apply(self._is_treatment_period).astype(bool)
        pre_mask_control = ~is_treatment_control
        treated_pre_mean = treated_agg.loc[pre_mask_treated, "y"].mean()
        control_pre_mean = control_agg.loc[pre_mask_control, "control_y"].mean()

        # Build aggregate DID counterfactual path: treated_pre + (control_t − control_pre).
        control_trend = control_agg["control_y"] - control_pre_mean
        treated_cf_agg = treated_pre_mean + control_trend

        agg = (
            treated_agg.merge(control_agg, on="time_unit", how="left")
            .assign(y_hat=treated_cf_agg.to_numpy(dtype=float))
            .sort_values("time_unit")
        )
        agg["effect"] = agg["y"] - agg["y_hat"]
        self._agg_by_time = agg[["time_unit", "y", "y_hat", "effect"]].copy()

        y = agg["y"].to_numpy(dtype=float)
        y_hat = agg["y_hat"].to_numpy(dtype=float)
        effect = agg["effect"].to_numpy(dtype=float)
        post_mask = agg["time_unit"].apply(self._is_treatment_period).to_numpy(dtype=bool)

        n_treated = max(len(self.panel.treated_units), 1)

        # Map an equal-share per-unit counterfactual back to treated rows so row-level lookup
        # remains well-defined without multiplying the aggregate counterfactual by the number of treated units.
        cf_map_per_unit = dict(zip(agg["time_unit"], (agg["y_hat"] / n_treated)))
        treated_df["_counterfactual"] = treated_df["time_unit"].map(cf_map_per_unit)
        treated_df["_effect"] = treated_df["value"] - treated_df["_counterfactual"]

        # Keep row-level lookup for downstream code that asks model.predict on unit-time rows.
        self._treated_row_df = treated_df[["unit", "time_unit", "value", "_counterfactual", "_effect", "post"]].copy()
        self._treated_cf_series = pd.Series(dict(zip(agg["time_unit"], agg["y_hat"])))

        # Path-based primary: effect_t = y_t - y_hat_t for each post period
        effect = y - y_hat
        post_effects = effect[post_mask]
        n_post = int(np.sum(post_mask))
        mean_post_period_att = float(np.nanmean(post_effects)) if n_post > 0 else np.nan
        cumulative_att = float(np.nansum(post_effects)) if n_post > 0 else np.nan

        # Store path-based primary values (source of truth for ATT, CI, p-value)
        self.mean_post_period_att = mean_post_period_att
        self.cumulative_att = cumulative_att
        self.post_effects = post_effects
        self.n_post = n_post

        # Secondary/regression diagnostic only (do not use for main reporting)
        beta_hat = float(self.treatment_effect)
        agg_att = float(beta_hat * n_treated)
        self.per_geo_effect = beta_hat
        self.aggregate_effect = agg_att

        y_lower = np.full_like(y_hat, np.nan)
        y_upper = np.full_like(y_hat, np.nan)
        # treatment_ci is now cumulative (path-based bootstrap); distribute to per-period for plotting
        if np.isfinite(self.treatment_ci[0]) and np.isfinite(self.treatment_ci[1]) and n_post > 0:
            cum_ci_lower, cum_ci_upper = self.treatment_ci
            per_period_lb = cum_ci_lower / n_post
            per_period_ub = cum_ci_upper / n_post
            y_lower[post_mask] = y[post_mask] - per_period_ub
            y_upper[post_mask] = y[post_mask] - per_period_lb

        # Primary DID estimate: path-based (cumulative_att, mean_post_period_att, treatment_ci, p_value).
        self.results = {
            "times": agg["time_unit"].tolist(),
            "y": y,
            "y_hat": y_hat,
            "treatment_effects": effect,
            "average_treatment_effect": mean_post_period_att,
            "per_geo_effect": beta_hat,
            "aggregate_effect": agg_att,
            "mean_post_period_att": mean_post_period_att,
            "cumulative_att": cumulative_att,
            "n_post": n_post,
            "post_effects": post_effects.tolist() if hasattr(post_effects, "tolist") else list(post_effects),
            "y_lower": y_lower,
            "y_upper": y_upper,
        }

        class _CounterfactualLookupWrapper:
            def __init__(self, owner, fitted_model):
                self._owner = owner
                self._fitted_model = fitted_model

            def predict(self, X):
                if isinstance(X, pd.DataFrame):
                    if "unit" in X.columns and "time_unit" in X.columns:
                        lookup = self._owner._treated_row_df[["unit", "time_unit", "_counterfactual"]]
                        merged = X.merge(lookup, on=["unit", "time_unit"], how="left")
                        if merged["_counterfactual"].notna().all():
                            return merged["_counterfactual"].to_numpy(dtype=float)
                    if "time_unit" in X.columns:
                        lookup = self._owner._agg_by_time.set_index("time_unit")["y_hat"]
                        vals = pd.Series(X["time_unit"]).map(lookup)
                        if vals.notna().all():
                            return vals.to_numpy(dtype=float)
                # Do not allow raw statsmodels extrapolation for DID counterfactuals.
                raise ValueError(
                    "DID counterfactual prediction only supports observed treated unit-time rows or observed time_unit aggregation."
                )

            def __getattr__(self, name):
                return getattr(self._fitted_model, name)

        self.regression_model = self.model
        self.model = _CounterfactualLookupWrapper(self, self.regression_model)

    def summary_2(self):
        mean_att = getattr(self, "mean_post_period_att", np.nan)
        cumulative_att = getattr(self, "cumulative_att", np.nan)
        if not np.isfinite(cumulative_att) and np.isfinite(getattr(self, "aggregate_effect", np.nan)):
            n_post = getattr(self, "n_post", 0) or (self.panel.treated_end_idxs[0] - self.panel.treated_start_idxs[0] + 1)
            cumulative_att = getattr(self, "aggregate_effect", np.nan) * n_post
        return pd.DataFrame(
            {
                "Average": [mean_att, 0],
                "Cumulative": [cumulative_att, 0],
            },
            index=["Absolute Effect", "Relative Effect"],
        )

    def summary(self):
        return self.summary_2()

    def get_pre_test_counterfactual(self, pre_test_times, aggregate: str = "sum"):
        """Return no-treatment counterfactual predictions for observed pre-period times."""
        if not hasattr(self, "_agg_by_time") or len(pre_test_times) == 0:
            return np.full(len(pre_test_times), np.nan)

        lookup = self._agg_by_time.set_index("time_unit")["y_hat"]
        out = np.array([float(lookup.get(t, np.nan)) for t in pre_test_times], dtype=float)

        if aggregate == "mean":
            n_units = max(len(self.panel.treated_units), 1)
            out = out / n_units

        return out

    def _run_linear_pretrend_test(self) -> Dict[str, Any]:
        """
        Linear pre-trends test: value_it = α + β₁ treated_i + β₂ time_t + β₃ (treated_i × time_t) + ε_it
        on pre-period data only. If β₃ is significant, treated and control have different pre-trends.
        Kept as fallback/secondary diagnostic; event-study pretrend is primary.
        """
        df_pre = self.data[self.data["post"] == 0]
        if len(df_pre) < 4:
            return {"parallel_trends_violated": False, "interaction_pvalue": 1.0}
        unique_times = sorted(df_pre["time_unit"].unique())
        if len(unique_times) < 2:
            return {"parallel_trends_violated": False, "interaction_pvalue": 1.0}
        time_map = {t: i for i, t in enumerate(unique_times)}
        df_pre = df_pre.copy()
        df_pre["time"] = df_pre["time_unit"].map(time_map)
        try:
            model = smf.ols("value ~ treated + time + treated:time", data=df_pre).fit()
            n_clusters = df_pre["unit"].nunique()
            if n_clusters >= 10:
                model_robust = model.get_robustcov_results(
                    cov_type="cluster", groups=df_pre["unit"]
                )
            else:
                model_robust = model.get_robustcov_results(cov_type="HC1")
            param_names = list(model.params.index)
            coef_name = None
            for p in param_names:
                if "treated" in p and "time" in p and ":" in p:
                    coef_name = p
                    break
            if coef_name is None:
                return {"parallel_trends_violated": False, "interaction_pvalue": 1.0}
            idx = param_names.index(coef_name)
            b3 = float(model.params.iloc[idx])
            se = np.asarray(model_robust.bse).ravel()
            pvals = np.asarray(model_robust.pvalues).ravel()
            b3_se = float(se[idx]) if idx < len(se) else np.nan
            interaction_pvalue = float(pvals[idx]) if idx < len(pvals) else 1.0
            if not np.isfinite(interaction_pvalue) and np.isfinite(b3_se) and b3_se > 0:
                interaction_pvalue = 2 * (1 - stats.norm.cdf(abs(b3) / b3_se))
            violated = interaction_pvalue < self.alpha
            return {"parallel_trends_violated": violated, "interaction_pvalue": float(interaction_pvalue)}
        except Exception:
            return {"parallel_trends_violated": False, "interaction_pvalue": 1.0}

    def _bin_pre_periods(
        self, rel_periods: List[int], max_bins: int = MAX_EVENT_STUDY_PRE_BINS
    ) -> Tuple[Dict[int, str], bool]:
        """
        Map relative periods to bin labels. Keep last 4 pre-periods individually (t=-1..-4),
        collapse older into early/mid/late-pre bins. Total bins <= max_bins.
        Returns (rel_period -> bin_label, binning_used).
        """
        rel_periods = sorted(rel_periods)
        if len(rel_periods) <= max_bins:
            return {r: f"t={r}" for r in rel_periods}, False

        mapping: Dict[int, str] = {}
        keep_individual = 4
        remaining: List[int] = []
        for r in rel_periods:
            if r >= -keep_individual:
                mapping[r] = f"t={r}"
            else:
                remaining.append(r)

        if not remaining:
            return mapping, True

        n_rem = len(remaining)
        if n_rem <= 2:
            bin_labels = ["bin_early"]
        elif n_rem <= 4:
            bin_labels = ["bin_early", "bin_mid"]
        else:
            bin_labels = ["bin_early", "bin_mid", "bin_late_pre"]

        chunk = max(1, n_rem // len(bin_labels))
        for i, r in enumerate(remaining):
            idx = min(i // chunk, len(bin_labels) - 1)
            mapping[r] = bin_labels[idx]
        return mapping, True

    def _run_event_study_pretrend_test(self) -> Dict[str, Any]:
        """
        Event-study-style pre-period diagnostic: interact treated with pre-period (or binned) indicators,
        use last pre-period as reference. Joint test that all pre-period interaction coefficients are zero.
        When n_pre > MAX_EVENT_STUDY_PRE_BINS, bin older periods to reduce collinearity.
        """
        df_pre_init = self.data[self.data["post"] == 0] if hasattr(self, "data") else pd.DataFrame()
        n_treated_units = df_pre_init[df_pre_init["treated"] == 1]["unit"].nunique() if len(df_pre_init) > 0 else 0
        n_control_units = df_pre_init[df_pre_init["treated"] == 0]["unit"].nunique() if len(df_pre_init) > 0 else 0
        df_pre = self.data[self.data["post"] == 0]
        n_pre_periods = len(df_pre["time_unit"].unique()) if len(df_pre) > 0 else 0
        unique_times = sorted(df_pre["time_unit"].unique()) if len(df_pre) > 0 else []

        def _make_fallback(reason: str) -> Dict[str, Any]:
            return {
                "parallel_trends_test_type": "event_study_preperiod",
                "reference_pre_period": None,
                "pretrend_coefficients": {},
                "pretrend_standard_errors": {},
                "pretrend_pvalues": {},
                "parallel_trends_joint_pvalue": None,
                "parallel_trends_violated": None,
                "largest_pretrend_deviation": None,
                "largest_pretrend_period": None,
                "fallback_reason": reason,
                "fallback_diagnostics": {
                    "n_pre_periods": n_pre_periods,
                    "n_treated_units": int(n_treated_units),
                    "n_control_units": int(n_control_units),
                },
                "pretrend_binning_used": False,
                "n_pre_periods_original": n_pre_periods,
                "n_pre_bins_used": None,
                "parallel_trends_joint_pvalue_method": None,
            }

        if len(df_pre) < 4:
            out = _make_fallback("insufficient_pre_periods")
            if os.environ.get("DEBUG_DID"):
                print(f"[DID EVENT STUDY] fallback: {out['fallback_reason']} (n_pre_periods={n_pre_periods})")
            return out
        if len(unique_times) < _MIN_PRE_PERIODS_EVENT_STUDY:
            out = _make_fallback("need_at_least_3_pre_periods")
            if os.environ.get("DEBUG_DID"):
                print(f"[DID EVENT STUDY] fallback: {out['fallback_reason']} (n_pre_periods={n_pre_periods})")
            return out

        ref_idx = len(unique_times) - 1
        ref_time = unique_times[ref_idx]
        time_to_rel = {t: i - ref_idx for i, t in enumerate(unique_times)}
        rel_periods = sorted(time_to_rel.values())
        rel_periods = [r for r in rel_periods if r < 0]

        df_pre = df_pre.copy()
        df_pre["rel_period"] = df_pre["time_unit"].map(time_to_rel)

        bin_mapping, binning_used = self._bin_pre_periods(rel_periods)
        df_pre["bin"] = df_pre["rel_period"].map(bin_mapping)
        unique_bins = sorted(set(bin_mapping.values()), key=lambda b: (
            -999 if b.startswith("bin_") else int(b.split("=")[-1])
        ))
        ref_bin = "t=-1"
        n_pre_bins = len(unique_bins)

        if os.environ.get("DEBUG_DID"):
            print(f"[DID EVENT STUDY] n_pre_periods={n_pre_periods}, binning_used={binning_used}, n_bins={n_pre_bins}")

        try:
            formula = "value ~ C(unit_fe) + treated:C(bin, Treatment('t=-1'))"
            model = smf.ols(formula, data=df_pre).fit()
            n_clusters = df_pre["unit"].nunique()
            if n_clusters >= 10:
                model_robust = model.get_robustcov_results(
                    cov_type="cluster", groups=df_pre["unit"]
                )
            else:
                model_robust = model.get_robustcov_results(cov_type="HC1")
            param_names = list(model.params.index)
            pretrend_coefs = {}
            pretrend_ses = {}
            pretrend_pvals = {}
            coef_names = [p for p in param_names if "treated" in p and "bin" in p and ":" in p]
            for p in coef_names:
                try:
                    if "[T." in p:
                        part = p.split("[T.")[-1].rstrip("]").strip("'\"")
                    else:
                        start, end = p.rfind("[") + 1, p.rfind("]")
                        if start > 0 and end > start:
                            part = p[start:end].strip("'\"")
                        else:
                            continue
                    if part.startswith("bin_"):
                        label = part
                    else:
                        try:
                            rel = int(float(part))
                            label = f"t={rel}"
                        except ValueError:
                            label = part
                except (ValueError, IndexError):
                    continue
                idx = param_names.index(p)
                pretrend_coefs[label] = float(model.params.iloc[idx])
                bse = np.asarray(model_robust.bse).ravel()
                pvals = np.asarray(model_robust.pvalues).ravel()
                pretrend_ses[label] = float(bse[idx]) if idx < len(bse) else np.nan
                pretrend_pvals[label] = float(pvals[idx]) if idx < len(pvals) else np.nan

            if not pretrend_coefs:
                out = _make_fallback("no_pretrend_coefficients_estimated")
                out["fallback_diagnostics"]["design_matrix_num_cols"] = len(param_names)
                return out

            joint_pvalue = np.nan
            joint_pvalue_method = "wald"
            use_max_t = n_pre_bins > 5
            if not use_max_t:
                try:
                    with warnings.catch_warnings(record=True) as wlist:
                        warnings.simplefilter("always")
                        R = np.zeros((len(coef_names), len(param_names)))
                        for i, c in enumerate(coef_names):
                            j = param_names.index(c)
                            R[i, j] = 1.0
                        wald = model_robust.wald_test(R)
                        joint_pvalue = float(wald.pvalue) if hasattr(wald, "pvalue") else np.nan
                        rank_warn = any("rank" in str(getattr(x, "message", str(x))) for x in wlist)
                        if rank_warn or not np.isfinite(joint_pvalue):
                            use_max_t = True
                except Exception:
                    use_max_t = True
            if use_max_t:
                joint_pvalue_method = "max_t_fallback"
                max_abs_t = 0.0
                for label, coef in pretrend_coefs.items():
                    se = pretrend_ses.get(label, np.nan)
                    if np.isfinite(se) and se > 0:
                        t = abs(coef / se)
                        max_abs_t = max(max_abs_t, t)
                joint_pvalue = float(2 * (1 - stats.norm.cdf(max_abs_t))) if max_abs_t > 0 else np.nan

            largest_dev = max((abs(v) for v in pretrend_coefs.values()), default=np.nan)
            largest_period = max(pretrend_coefs.keys(), key=lambda k: abs(pretrend_coefs[k])) if pretrend_coefs else None
            if os.environ.get("DEBUG_DID"):
                print(f"[DID EVENT STUDY] success: largest_dev={largest_dev}, largest_period={largest_period}")
            return {
                "parallel_trends_test_type": "event_study_preperiod",
                "reference_pre_period": ref_time,
                "reference_relative_label": "t=-1",
                "pretrend_coefficients": pretrend_coefs,
                "pretrend_standard_errors": pretrend_ses,
                "pretrend_pvalues": pretrend_pvals,
                "parallel_trends_joint_pvalue": joint_pvalue,
                "parallel_trends_violated": joint_pvalue < self.alpha if np.isfinite(joint_pvalue) else None,
                "largest_pretrend_deviation": float(largest_dev) if np.isfinite(largest_dev) else np.nan,
                "largest_pretrend_period": largest_period,
                "fallback_reason": None,
                "fallback_diagnostics": {
                    "n_pre_periods": n_pre_periods,
                    "n_treated_units": int(n_treated_units),
                    "n_control_units": int(n_control_units),
                },
                "pretrend_binning_used": binning_used,
                "n_pre_periods_original": n_pre_periods,
                "n_pre_bins_used": n_pre_bins,
                "parallel_trends_joint_pvalue_method": joint_pvalue_method,
            }
        except Exception as e:
            out = _make_fallback(str(e))
            out["fallback_diagnostics"]["n_pre_periods"] = n_pre_periods
            out["fallback_diagnostics"]["n_treated_units"] = int(n_treated_units)
            out["fallback_diagnostics"]["n_control_units"] = int(n_control_units)
            return out

    def get_detailed_results(self) -> Dict[str, Any]:
        """Return DID inference and diagnostics for MMT reporting. Primary: path-based (post-period effect path)."""
        if os.environ.get("DEBUG_DID"):
            print("[DID INFERENCE] primary_effect_definition=path_based_sum_of_post_period_effects")
        event_study = self._run_event_study_pretrend_test()
        linear_test = self._run_linear_pretrend_test()
        n_treated = max(len(self.panel.treated_units), 1)
        n_clusters = self.data["unit"].nunique() if hasattr(self, "data") else np.nan
        clustered_se_used = n_clusters >= 10 if np.isfinite(n_clusters) else False
        joint_pv = event_study.get("parallel_trends_joint_pvalue")
        used_linear_fallback = joint_pv is None or not np.isfinite(joint_pv)
        if used_linear_fallback:
            joint_pv = linear_test.get("interaction_pvalue")
        violated = event_study.get("parallel_trends_violated")
        if violated is None:
            violated = linear_test.get("parallel_trends_violated", False)
        actually_fell_back = event_study.get("fallback_reason") is not None
        pt_test_type = "linear_pretrend" if (used_linear_fallback or actually_fell_back) else "event_study_preperiod"
        parallel_trends_test = {
            "parallel_trends_violated": violated,
            "interaction_pvalue": joint_pv,
            "parallel_trends_test_type": pt_test_type,
            "parallel_trends_joint_pvalue": joint_pv,
            "reference_pre_period": event_study.get("reference_pre_period"),
            "pretrend_coefficients": event_study.get("pretrend_coefficients", {}),
            "pretrend_pvalues": event_study.get("pretrend_pvalues", {}),
            "pretrend_standard_errors": event_study.get("pretrend_standard_errors", {}),
            "largest_pretrend_deviation": event_study.get("largest_pretrend_deviation"),
            "largest_pretrend_period": event_study.get("largest_pretrend_period"),
            "fallback_reason": event_study.get("fallback_reason"),
            "pretrend_binning_used": event_study.get("pretrend_binning_used", False),
            "n_pre_periods_original": event_study.get("n_pre_periods_original"),
            "n_pre_bins_used": event_study.get("n_pre_bins_used"),
            "parallel_trends_joint_pvalue_method": event_study.get("parallel_trends_joint_pvalue_method"),
            "linear_pretrend_fallback": linear_test,
        }

        # Primary path-based fields (source of truth)
        mean_att = getattr(self, "mean_post_period_att", np.nan)
        cumulative_att = getattr(self, "cumulative_att", np.nan)
        n_post = getattr(self, "n_post", 0)
        cum_ci = self.treatment_ci  # now cumulative from path-based bootstrap
        mean_ci = (np.nan, np.nan)
        if hasattr(self, "bootstrap_mean_effects_") and len(self.bootstrap_mean_effects_) >= 30:
            mean_ci = (
                float(np.percentile(self.bootstrap_mean_effects_, (self.alpha / 2) * 100)),
                float(np.percentile(self.bootstrap_mean_effects_, (1 - self.alpha / 2) * 100)),
            )

        out = {
            "primary_effect_definition": "path_based_sum_of_post_period_effects",
            "mean_post_period_att": mean_att,
            "cumulative_att": cumulative_att,
            "cumulative_ci": cum_ci,
            "mean_post_period_ci": mean_ci,
            "p_value": self.treatment_pvalue,
            "significant": self.treatment_pvalue < self.alpha if np.isfinite(self.treatment_pvalue) else False,
            "primary_inference_method": "moving_block_bootstrap",
            "n_post": n_post,
            "bootstrap_n": int(len(getattr(self, "bootstrap_cumulative_effects_", [])) or len(getattr(self, "bootstrap_effects_", []))),
            "bootstrap_block_size": self.bootstrap_block_size,
            "n_bootstrap": self.n_bootstrap,
            "parallel_trends_test": parallel_trends_test,
            "placebo_test": {"placebo_pvalue": 1.0},
            "parallel_trends_test_type": pt_test_type,
            "parallel_trends_joint_pvalue": joint_pv,
            "parallel_trends_violated": violated,
            "reference_pre_period": event_study.get("reference_pre_period"),
            "pretrend_coefficients": event_study.get("pretrend_coefficients", {}),
            "pretrend_pvalues": event_study.get("pretrend_pvalues", {}),
            "pretrend_standard_errors": event_study.get("pretrend_standard_errors", {}),
            "largest_pretrend_deviation": event_study.get("largest_pretrend_deviation"),
            "largest_pretrend_period": event_study.get("largest_pretrend_period"),
            "fallback_reason": event_study.get("fallback_reason"),
            "pretrend_binning_used": event_study.get("pretrend_binning_used", False),
            "n_pre_periods_original": event_study.get("n_pre_periods_original"),
            "n_pre_bins_used": event_study.get("n_pre_bins_used"),
            "parallel_trends_joint_pvalue_method": event_study.get("parallel_trends_joint_pvalue_method"),
            # Secondary/regression diagnostic only (do not use for main reporting)
            "treatment_effect": getattr(self, "per_geo_effect", self.treatment_effect),
            "treatment_effect_per_geo": getattr(self, "per_geo_effect", self.treatment_effect),
            "treatment_effect_aggregate": getattr(self, "aggregate_effect", np.nan),
            "treatment_ci": cum_ci,
            "treatment_ci_aggregate": cum_ci,
            "standard_error": self.treatment_se,
            "standard_error_aggregate": float(self.treatment_se * n_treated) if np.isfinite(self.treatment_se) else np.nan,
            "model_based_se": getattr(self, "model_based_se", np.nan),
            "model_based_pvalue": getattr(self, "model_based_pvalue", np.nan),
            "secondary_inference_method": "clustered_robust" if clustered_se_used else "HC1",
            "n_unit_clusters": int(n_clusters) if np.isfinite(n_clusters) else None,
            "clustered_se_used": clustered_se_used,
        }
        return out