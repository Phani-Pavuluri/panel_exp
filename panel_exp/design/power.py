import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from joblib import Parallel, delayed
from tqdm import tqdm

from panel_exp.panel_data import PanelDataset, TimePeriod

sns.set_style("darkgrid")

# Documented semantics for simulation-based MDE (not classical analytic power).
MDE_SEMANTICS: dict[str, Any] = {
    "mde_method": "simulation_coverage",
    "mde_definition": (
        "Smallest tested effect level on the simulation grid where the "
        "configured interval-coverage criterion falls below the power threshold"
    ),
    "classical_power": False,
    "planning_use": "ranking_and_sensitivity_only",
    "depends_on": [
        "estimator",
        "inference_method",
        "panel_data",
        "alpha",
        "power_threshold",
        "effect_grid",
        "train/test_window_sampling",
    ],
}

_DEFAULT_RECOMMENDED_USE: List[str] = [
    "compare design alternatives",
    "rank sensitivity",
]

_DEFAULT_NOT_RECOMMENDED_FOR: List[str] = [
    "guaranteed detectability claims",
    "financial commitment thresholds",
]

_DEFAULT_POWER_WARNINGS: List[str] = [
    "MDE is simulation-based and estimator-dependent",
    "Power estimates may vary with effect grid and simulation count",
    "Null calibration should be reviewed before decision use",
]


@dataclass(frozen=True)
class PowerContract:
    """
    Explicit planning contract for simulation-based MDE / power outputs.

    Metadata only; does not alter power calculations or MDE selection.
    """

    mde_type: str = "simulation_coverage"
    classical_power: bool = False
    simulation_based: bool = True
    effect_units: str = "percent"
    requires_null_calibration: bool = True
    recommended_use: Tuple[str, ...] = field(default_factory=lambda: tuple(_DEFAULT_RECOMMENDED_USE))
    not_recommended_for: Tuple[str, ...] = field(
        default_factory=lambda: tuple(_DEFAULT_NOT_RECOMMENDED_FOR)
    )
    warnings: Tuple[str, ...] = field(default_factory=lambda: tuple(_DEFAULT_POWER_WARNINGS))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mde_type": self.mde_type,
            "classical_power": self.classical_power,
            "simulation_based": self.simulation_based,
            "effect_units": self.effect_units,
            "requires_null_calibration": self.requires_null_calibration,
            "recommended_use": list(self.recommended_use),
            "not_recommended_for": list(self.not_recommended_for),
            "warnings": list(self.warnings),
        }


def _recommended_use_from_semantics(semantics: Mapping[str, Any]) -> List[str]:
    planning = str(semantics.get("planning_use", "")).strip().lower()
    if planning in ("ranking_and_sensitivity_only", "ranking", "sensitivity"):
        return list(_DEFAULT_RECOMMENDED_USE)
    if planning:
        return [planning.replace("_", " ")]
    return list(_DEFAULT_RECOMMENDED_USE)


def build_power_contract(
    mde_semantics: Optional[Mapping[str, Any]] = None,
    *,
    aa_calibration: Optional[Mapping[str, Any]] = None,
    extra_warnings: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """
    Build a power/MDE user contract from documented semantics (no logic changes).

    Populates defaults from :data:`MDE_SEMANTICS` and optional calibration readout.
    """
    semantics = dict(mde_semantics or MDE_SEMANTICS)
    classical = bool(semantics.get("classical_power", False))
    mde_type = str(semantics.get("mde_method", "simulation_coverage"))

    warnings: List[str] = []
    for w in _DEFAULT_POWER_WARNINGS:
        if w not in warnings:
            warnings.append(w)

    if extra_warnings:
        for w in extra_warnings:
            text = str(w).strip()
            if text and text not in warnings:
                warnings.append(text)

    if aa_calibration is not None:
        if not aa_calibration.get("calibration_complete", True):
            msg = "A/A null calibration incomplete or under-powered for decision use"
            if msg not in warnings:
                warnings.append(msg)
        cal_warns = aa_calibration.get("warnings") or []
        if isinstance(cal_warns, (list, tuple)):
            for w in cal_warns:
                text = str(w).strip()
                if text and text not in warnings:
                    warnings.append(text)

    contract = PowerContract(
        mde_type=mde_type,
        classical_power=classical,
        simulation_based=not classical,
        effect_units="percent",
        requires_null_calibration=True,
        recommended_use=tuple(_recommended_use_from_semantics(semantics)),
        not_recommended_for=tuple(_DEFAULT_NOT_RECOMMENDED_FOR),
        warnings=tuple(warnings),
    )
    return contract.to_dict()


def attach_power_contract(
    results_or_artifacts: Dict[str, Any],
    contract: Mapping[str, Any],
) -> Dict[str, Any]:
    """Attach power contract metadata to a mutable results or artifacts dict (additive)."""
    payload = dict(contract)
    results_or_artifacts["power_contract"] = payload
    return payload


def evaluate_aa_calibration(
    simulation_output: pd.DataFrame,
    *,
    alpha: float = 0.05,
    null_effect_column: str = "prc_effect",
    coverage_column: str = "mean_ss",
    min_replications: int = 30,
) -> dict[str, Any]:
    """
    Lightweight A/A calibration report from null-effect simulation rows.

    Computes false-positive rate (share of null runs where the path interval
    excludes zero) and mean coverage when ``mean_ss`` indicates the interval
    covers zero. Intended for diagnostics only; not wired to production gates.

    :param simulation_output: Power simulation table (e.g. ``PowerAnalysis.output_df``).
    :param alpha: Nominal significance level (reported for context; assumes intervals match ``alpha``).
    :param null_effect_column: Column identifying simulated percent effect (0 = null).
    :param coverage_column: Boolean column where True means the interval covers zero.
    :param min_replications: Minimum rows at null effect before suppressing low-n warnings.
    """
    if simulation_output is None or simulation_output.empty:
        return {
            "false_positive_rate": None,
            "coverage": None,
            "n_replications": 0,
            "warnings": ["no simulation rows provided"],
            "calibration_complete": False,
        }

    null_df = simulation_output.loc[
        np.isclose(simulation_output[null_effect_column].astype(float), 0.0)
    ]
    n_replications = int(len(null_df))
    warnings: list[str] = []
    if n_replications < min_replications:
        warnings.append(
            f"only {n_replications} null replications (recommended >={min_replications})"
        )

    if n_replications == 0:
        return {
            "false_positive_rate": None,
            "coverage": None,
            "n_replications": 0,
            "warnings": warnings + ["no null-effect rows found"],
            "calibration_complete": False,
            "alpha": alpha,
        }

    covers_zero = null_df[coverage_column].astype(bool)
    coverage = float(covers_zero.mean())
    false_positive_rate = float(1.0 - coverage)
    return {
        "false_positive_rate": false_positive_rate,
        "coverage": coverage,
        "n_replications": n_replications,
        "warnings": warnings,
        "calibration_complete": len(warnings) == 0,
        "alpha": alpha,
    }


class PowerAnalysis:
    """
    Simulation-based pre-test power analysis.

    **MDE definition (simulation / coverage-based, not classical):** For each
    effect level on a percent grid, the method estimates the fraction of
    sliding train/test windows where the inference interval covers zero
    (``mean_ss``). The reported MDE is the first grid point where that
    coverage-based "power" drops below ``power`` (default 0.8). This is
    **not** a closed-form t-test or analytic minimum detectable effect.

    **Reproducibility:** When ``random_state`` is an integer, window
    subsampling and per-window inference seeds are deterministic
    (``random_state + iteration`` passed to inference). When
    ``random_state=None``, behavior is stochastic (legacy-compatible).

    **Limitations:** Results depend on estimator choice, inference method,
    panel history, effect grid, and simulation design. Use for planning and
    ranking scenarios, not as sole proof of feasibility.

    :param panel: Required. A PanelDataset
    :param model: Required. The model to use to construct a synthetic control.
    :param inference: Required. Method used to create confidence intervals.
    :param test_length: Required. The length of the test period.
    :param train_length: Default=None. The length of pre-test data to use.
    :param mx_effect: Default = 0.5. Maximum absolute percent effect to simulate.
    :param n_sample_prc: Default = 1. Fraction of train/test windows to sample.
    :param n_jobs: Default = 1. Parallel jobs.
    :param random_state: Integer seed for reproducible runs; ``None`` for stochastic draws.
    :param alpha: Significance level for intervals (default 0.05 → 95% intervals).
    """

    def __init__(
        self,
        panel,
        model,
        inference,
        test_length,
        power=0.8,
        train_length=None,
        alpha=0.05,
        mx_effect=0.5,
        n_sample_prc=1,
        n_jobs=1,
        ci_version=1,
        random_state=42,
        **kw_args,
    ):
        if "njobs" in kw_args:
            n_jobs = kw_args.pop("njobs")
        self.panel = panel
        self.model = model
        self.inference = inference
        self.L = len(panel.times)
        self.test_length = test_length
        self.power = power
        self.train_length = train_length
        self.mx_effect = mx_effect
        self.n_jobs = n_jobs
        self.n_sample_prc = n_sample_prc
        self.alpha = alpha
        self.ci_version = ci_version
        self.random_state = random_state
        self._rng = self._make_rng(random_state)
        self.kw_args = kw_args
        self.mde_semantics: dict[str, Any] = dict(MDE_SEMANTICS)
        self.aa_calibration: dict[str, Any] | None = None
        self.power_contract: dict[str, Any] = build_power_contract(MDE_SEMANTICS)

    @staticmethod
    def _make_rng(random_state: Optional[int]) -> np.random.Generator:
        if random_state is None:
            return np.random.default_rng()
        return np.random.default_rng(random_state)

    def _inference_seed(self, iteration: int) -> Optional[int]:
        if self.random_state is None:
            return None
        return int(self.random_state) + int(iteration)

    def _inference_kwargs(self, iteration: int) -> dict[str, Any]:
        infer_kw = dict(self.kw_args)
        seed = self._inference_seed(iteration)
        if seed is not None:
            infer_kw.setdefault("random_state", seed)
        return infer_kw

    def train_test_indices_f(self):
        """
        This method returns indices for simulated pre-test and test periods.
        """

        if not self.train_length:
            self.train_length = self.L-self.test_length
            
        assert self.train_length + self.test_length <= self.L, "Train + Test Length must be less or equal to available data points "
        train_test_indices = []

        for i in range(self.L):
            train = [(i + j) % self.L for j in range(self.train_length)]
            test = [
                (i + self.train_length + j) % self.L for j in range(self.test_length)
            ]
            train_test_indices.append([train, test])
    
        return train_test_indices

    def fake_effect(self, mod_pds, effect = 0):
        """
        This method returns a modifed PanelDataset that has a 'fake' effect added it to it.
        """
        mod_fe_pds = copy.deepcopy(mod_pds)

        mask = np.tile(~(mod_pds.times>=mod_pds.times[mod_pds.treated_start_idxs[0]])&(mod_pds.times<=mod_pds.times[mod_pds.treated_end_idxs[0]-1])
                , (mod_fe_pds.wide_data.loc[mod_fe_pds.treated_units].shape[0],1) ) 
        
        mod_fe_pds.wide_data.loc[mod_fe_pds.treated_units] = mod_fe_pds.wide_data.loc[mod_fe_pds.treated_units].where(mask
                                                                    , mod_fe_pds.wide_data.loc[mod_fe_pds.treated_units]+effect.reshape(-1,1)
                                                                    )
        return mod_fe_pds


    def effect_sample(self, percent_effect, value_effect, mod_pds, iteration , true_test = None):
        """
        This method returns the results of the estimated causal effect for a specified fake effect.
        """
        mod_fe_pds = self.fake_effect(mod_pds, value_effect)
        est = self.model(self.inference)

        est.run_analysis(mod_fe_pds, **self._inference_kwargs(iteration))
        
        cum_effect = (est.results['y'] - est.results['y_hat'])[-self.test_length:].sum()
        mean_effect = (est.results['y'] - est.results['y_hat'])[-self.test_length:].mean()
        
        cum_effect_low = (est.results['y'] - est.results['y_lower'])[-self.test_length:].sum()
        cum_effect_high = (est.results['y'] - est.results['y_upper'])[-self.test_length:].sum()

        mean_effect_low = (est.results['y'] - est.results['y_lower'])[-self.test_length:].mean()
        mean_effect_high = (est.results['y'] - est.results['y_upper'])[-self.test_length:].mean()
        
        mean_ss = mean_effect_low <= 0 <= mean_effect_high
        cum_ss = cum_effect_low <= 0 <= cum_effect_high
        bias = (est.results['y'] - est.results['y_hat'])[:-self.test_length].mean()
        y_actuals = est.results['y'][-self.test_length:].sum()

        if true_test:
            est.model.predict()

        return [iteration, round(percent_effect,2) , bias, value_effect.mean(), (value_effect * self.test_length).sum() , cum_effect_low, cum_effect, cum_effect_high, mean_effect_low, mean_effect, mean_effect_high, mean_ss, cum_ss, y_actuals]


    def _attach_mde_semantics(self, percent_effect: np.ndarray) -> None:
        self.mde_semantics = {
            **MDE_SEMANTICS,
            "power_threshold": float(self.power),
            "alpha": float(self.alpha),
            "ci_version": int(self.ci_version),
            "random_state": self.random_state,
            "n_sample_prc": float(self.n_sample_prc),
            "effect_grid_size": int(len(percent_effect)),
            "mde_percent": getattr(self, "mde_percent", None),
            "mde_kpi_cumulative": getattr(self, "mde_kpi_cumulative", None),
        }
        self.aa_calibration = evaluate_aa_calibration(
            self.output_df,
            alpha=self.alpha,
        )
        self.power_contract = build_power_contract(
            self.mde_semantics,
            aa_calibration=self.aa_calibration,
        )

    def analysis(self):
        """
        Execute simulation steps and derive coverage-based MDE metrics.

        See class docstring for MDE semantics. Does not use classical
        closed-form power formulas.
        """

        self.tt = self.train_test_indices_f()
        output = []
        iteration = 0 

        if len(self.panel.treated_units) == 1:
            self.mean_value = self.panel.wide_data.loc[self.panel.treated_units].mean().mean()
        elif len(self.panel.treated_units) > 1:
            self.mean_value = self.panel.wide_data.loc[self.panel.treated_units].mean(axis=1).values

        if self.ci_version == 1:
            percent_effect = np.concatenate( [ np.linspace(-self.mx_effect, 0 , 25), np.linspace(0, self.mx_effect , 25)[1:]])
        
        if self.ci_version == 2:
            percent_effect = np.zeros(1)
        
        self.output_df = pd.DataFrame([], columns=['iteration', 'prc_effect', 'bias', 't_effect', 't_cum_effect',  'cum_effect_low', 'cum_effect', 'cum_effect_high', 'mean_effect_low', 'mean_effect', 'mean_effect_high', 'mean_ss', 'cum_ss'])
        
        n_keep = max(1, int(len(self.tt) * self.n_sample_prc))
        idx = self._rng.choice(len(self.tt), size=n_keep, replace=False)
        self.tt = [self.tt[i] for i in sorted(idx)]

        for k in tqdm(self.tt):
            train = k[0]
            test = k[1]
            mod_df = pd.concat([self.panel.wide_data.T.iloc[train], self.panel.wide_data.T.iloc[test]]).reset_index(drop=True)
            mod_pds = PanelDataset(mod_df.T, [TimePeriod(start=self.train_length) for _ in range(len(self.panel.treated_units))], self.panel.treated_units)
            
            output = Parallel(n_jobs=self.n_jobs)(delayed(self.effect_sample)(effect, effect*self.mean_value, mod_pds, iteration) for effect in percent_effect)
            # print(output.columns)
            iteration += 1
            self.output_df = pd.concat([self.output_df, pd.DataFrame(output, columns=['iteration','prc_effect','bias', 't_effect', 't_cum_effect', 'cum_effect_low', 'cum_effect', 'cum_effect_high', 'mean_effect_low', 'mean_effect', 'mean_effect_high', 'mean_ss', 'cum_ss','y_actuals'])])


        prc = (1-pd.pivot_table(self.output_df, index='prc_effect', columns='iteration', values='mean_ss').mean(axis=1))>=self.power
        cum_effect = (1-pd.pivot_table(self.output_df, index='t_cum_effect', columns='iteration', values='mean_ss').mean(axis=1))>=self.power
        self.n_simulations = len(self.tt * len(percent_effect))

                    
        if self.ci_version == 1: 
            
            self.mde_kpi_cumulative = cum_effect.index[min(loc for loc, val in enumerate(cum_effect.values) if not val)-1]
            self.mde_percent = prc.index[min(loc for loc, val in enumerate(prc.values) if not val)-1] 

            # Calculate Standard Error and CI for MDE in CI Version 1
            se_cum_effect = self.output_df[self.output_df.prc_effect == self.mde_percent].cum_effect.std() / np.sqrt(len(self.output_df[self.output_df.prc_effect == self.mde_percent]))
            ci_lower = self.mde_kpi_cumulative - 1.96 * se_cum_effect
            ci_upper = self.mde_kpi_cumulative + 1.96 * se_cum_effect
            self.error_rate = (ci_upper - ci_lower) / 2
                    
        if self.ci_version == 2:
            self.mde_kpi_cumulative =  1.96*(self.output_df[self.output_df.prc_effect == 0].cum_effect.std())
            self.output_df['cum_effect'] = self.output_df['cum_effect'].abs()
            # np.percentile(self.output_df[self.output_df.prc_effect == 0].cum_effect,99) 
            self.mde_percent = round(self.mde_kpi_cumulative /np.mean(self.output_df[self.output_df.prc_effect == 0].y_actuals),2)

            # Calculate Standard Error and CI for MDE in CI Version 2
            se_cum_effect_v2 = self.output_df[self.output_df.prc_effect == 0].cum_effect.std() / np.sqrt(len(self.output_df[self.output_df.prc_effect == 0]))
            ci_lower_v2 = self.mde_kpi_cumulative - 1.96 * se_cum_effect_v2
            ci_upper_v2 = self.mde_kpi_cumulative + 1.96 * se_cum_effect_v2
            self.error_rate = (ci_upper_v2 - ci_lower_v2) / 2

        self._attach_mde_semantics(percent_effect)


    def run_analysis(self):
        """
        Run the full simulation-based power analysis.

        Populates ``output_df``, coverage-based ``mde_percent`` / ``mde_kpi_cumulative``,
        ``mde_semantics``, and ``aa_calibration`` (null-effect diagnostic).
        """
        self.analysis()

    def plot_power_curve(self, x_axis='percent_effect' ):
        """
        Method to plot power curves.
        
        :param: x_axis. Default = percent effect. Expreses effect size as percent. Can be: percent_effect, total_effect, weekly_effect
        """
        # options fo x axis
        assert x_axis in ['percent_effect', 'total_effect', 'weekly_effect']

        # map readable input to abbreviated column name 
        i = ['percent_effect', 'total_effect', 'weekly_effect'].index(x_axis)
        x = ['prc_effect', 't_cum_effect', 't_effect'][i]

        es = (1-pd.pivot_table(self.output_df, index=x, columns='iteration', values='mean_ss').mean(axis=1))>=self.power

        if max(loc for loc, val in enumerate(es.values) if not val)+1 == es.values.shape[0]:
            raise ValueError("No MDE Found. Try Larger Effects and/or Longer Training Period")

        _low = es.index[max(loc for loc, val in enumerate(es.values) if not val)+1]
        high = es.index[min(loc for loc, val in enumerate(es.values) if not val)-1]

        plt.plot(1-pd.pivot_table(self.output_df, index=x, columns='iteration', values='mean_ss').mean(axis=1))
        plt.axhline(self.power)
        # plt.axvline(low, label='Lower MDE: %s' % low)
        # plt.axvline(high, label='Upper MDE: %s' % high)
        plt.title("Power Curve Simulation @ %s" % self.power, fontsize=15,   pad=15)
        plt.suptitle("Test Length: %s days \n MDE: %s" % (self.test_length, np.abs(high)),   y=.05 )

        # plt.axvline(np.percentile(self.output_df[self.output_df.prc_effect == 0].cum_effect, 99), color='red', label='Lower MDE: %s' % low)
        # plt.axvline(np.percentile(self.output_df[self.output_df.prc_effect == 0].cum_effect, 1), color='red', label='Upper MDE: %s' % high)

    def summary(self):
        info_1 = pd.DataFrame({"Parameters": [self.model.__name__, self.inference, self.test_length, self.n_simulations,  'Statistics' , self.mde_percent, self.mde_kpi_cumulative , self.power, (1-self.output_df[self.output_df.prc_effect==0].cum_ss.mean())*2, self.error_rate] }
              , index=['Model', 'Inference', 'Test Length', 'Number of Simulations', ' ', 'MDE Percent', 'MDE KPI', 'Power', 'Type 1 Error Rate', 'Error Rate (CI)']
              )
        
        # from IPython.display import display, HTML

        # display(HTML(info_1.to_html()))

        return info_1


