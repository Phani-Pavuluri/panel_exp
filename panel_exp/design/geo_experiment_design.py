import copy
from typing import Any, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from panel_exp.design import Rerandomization, greedy_match_markets
from panel_exp.design.power import PowerAnalysis
from panel_exp.design.registry import geo_run_design_supported, get_design_registry
from panel_exp.evidence import ExperimentEvidence
from panel_exp.panel_data import PanelDataset
from panel_exp.spec import InterferenceAssumption

# Legacy export: normalized names for geo-supported designs (tests, docs).
GEO_RUN_DESIGN_SUPPORTED = geo_run_design_supported()


class GeoExperimentDesign:
    """
    Orchestrator for geo-based experiment design with power / MDE analysis.

    **Registered vs geo-supported:** The design registry lists every implemented
    design (including QuickBlock, MatchedPair, etc.). Only a subset is supported
    by this orchestrator — see ``GEO_RUN_DESIGN_SUPPORTED``. Unsupported designs
    fail at construction or before ``run_design`` side effects.

    Supported via ``run_design`` (each wrapped in ``Rerandomization``):
    greedy_match_markets, ThinningDesign, BalancedRandomization,
    CompleteRandomization, StratifiedRandomization.

    Other registered designs must be invoked via their design classes directly.

    Constraints and reproducibility
    -------------------------------
    - ``control_whitelist`` / ``test_whitelist``: units pinned to the declared arm.
    - Blacklists: units excluded from assignment (``control_test_blacklist`` excludes both arms).
    - Conflicting or impossible constraints raise ``ValueError`` during assignment.
    - ``random_state`` on the design / geo orchestrator yields reproducible assignments
      and is forwarded to simulation-based power / MDE analysis.
    - MDE from ``PowerAnalysis`` is simulation/coverage-based (not classical analytic power);
      see ``PowerAnalysis.mde_semantics``.
    - Set ``interference`` explicitly (default ``unknown``). The package does not
      estimate spillovers; optional ``spillover_notes`` / ``exposure_column`` are
      metadata only.
    - When ``validate_after_assign`` and ``block_on_validation_fail`` are enabled (default),
      blocking validation failures prevent evidence and MDE generation.
    """

    def __init__(
        self,
        panel_data: PanelDataset,
        n_test_grps: Optional[int] = 1,
        treatment_probability: Optional[float] = None,
        imbalance_metric: Optional[str] = "l2",
        base_randomizer_cls: Optional[type] = None,
        test_whitelist: Optional[List[str]] = None,
        control_whitelist: Optional[List[str]] = None,
        test_blacklist: Optional[List[str]] = None,
        control_blacklist: Optional[List[str]] = None,
        control_test_blacklist: Optional[List[str]] = None,
        inference: Optional[str] = "Kfold",
        base_cls: Optional[type] = None,
        n_sample_prc: float = 0.3,
        ci_version: int = 1,
        train_length: Optional[int] = None,
        test_lengths: List[int] = None,
        njobs: int = -1,
        random_state: int = 42,
        alpha: float = 0.05,
        interference: InterferenceAssumption = InterferenceAssumption.UNKNOWN,
        spillover_notes: Optional[str] = None,
        exposure_column: Optional[str] = None,
        experiment_id: str = "geo_experiment",
        outcome_column: str = "outcome",
        unit_column: str = "unit",
        time_column: str = "time",
        validate_after_assign: bool = True,
        block_on_validation_fail: bool = True,
        **design_kwargs,
    ):
        if test_lengths is None:
            test_lengths = [28, 56, 91]

        self.panel_data = panel_data
        self.n_test_grps = n_test_grps
        self.treatment_probability = treatment_probability
        self.imbalance_metric = imbalance_metric
        self.base_randomizer_cls = base_randomizer_cls or greedy_match_markets
        self.test_whitelist = test_whitelist or []
        self.control_whitelist = control_whitelist or []
        self.test_blacklist = test_blacklist or []
        self.control_blacklist = control_blacklist or []
        self.control_test_blacklist = control_test_blacklist or []
        self.inference = inference
        self.base_cls = base_cls or greedy_match_markets
        self.n_sample_prc = n_sample_prc
        self.ci_version = ci_version
        self.test_lengths = test_lengths
        self.njobs = njobs
        self.design_kwargs = design_kwargs
        get_design_registry().validate_geo_capabilities(
            get_design_registry().resolve(self.base_randomizer_cls),
            self,
        )
        self.random_state = random_state
        self.last_power_mde_semantics: dict | None = None
        self.alpha = alpha
        self.interference = interference
        self.spillover_notes = spillover_notes
        self.exposure_column = exposure_column
        self.validate_after_assign = validate_after_assign
        self.block_on_validation_fail = block_on_validation_fail
        self.experiment_id = experiment_id
        self.outcome_column = outcome_column
        self.unit_column = unit_column
        self.time_column = time_column
        self.last_validation = None
        self.last_evidence: Optional[ExperimentEvidence] = None
        self._design_spec = get_design_registry().resolve(self.base_randomizer_cls)

        total_days = self.panel_data.wide_data.shape[1]
        max_test_length = max(self.test_lengths)

        if train_length is None:
            suggested_train_length = int(total_days * 0.6)
            if suggested_train_length + max_test_length <= total_days:
                train_length = suggested_train_length
            elif total_days > max_test_length:
                train_length = total_days - max_test_length
            else:
                raise ValueError("Test lengths exceed available data range.")
        else:
            if train_length + max_test_length > total_days:
                if total_days > max_test_length:
                    train_length = total_days - max_test_length
                else:
                    raise ValueError("Test lengths exceed available data range.")

        self.train_length = train_length

    def designs(
        self,
        n_test_grps: int = None,
        treatment_probability: float = None,
        max_iter: Optional[int] = 10000,
        imbalance_metric: Optional[str] = "l2",
        base_randomizer_cls: Optional[type] = None,
        **design_kwargs,
    ) -> Rerandomization:
        if treatment_probability is None:
            treatment_probability = n_test_grps / (n_test_grps + 1)
        base = base_randomizer_cls or self.base_randomizer_cls
        reg = get_design_registry()
        reg.validate_geo_capabilities(reg.resolve(base), self)
        design_kwargs.setdefault("random_state", self.random_state)
        return Rerandomization(
            treatment_probability=treatment_probability,
            max_iter=max_iter,
            base_randomizer_cls=base,
            imbalance_metric=imbalance_metric,
            **design_kwargs,
        )

    def create_design(self) -> Rerandomization:
        return self.designs(
            n_test_grps=self.n_test_grps,
            treatment_probability=self.treatment_probability,
            imbalance_metric=self.imbalance_metric,
            base_randomizer_cls=self.base_randomizer_cls,
            **self.design_kwargs,
        )

    def run_design(self) -> tuple:
        """
        Run design + MDE sensitivity. Returns (mde_prc_df, mde_val_df, power_results_df).

        Raises ValueError for unsupported randomizers.
        """
        return get_design_registry().run(
            self.base_randomizer_cls,
            self,
            self.design_kwargs,
        )

    def _calculate_sensitivity_metrics(self, rs_dp_grps: dict, control: str) -> tuple:
        mde_val_df = pd.DataFrame()
        mde_prc_df = pd.DataFrame()
        power_results_df = pd.DataFrame()

        for grp in [grp for grp in rs_dp_grps.keys() if grp != control]:
            self.pds = copy.deepcopy(self.panel_data)
            self.pds.wide_data = self.pds.wide_data.loc[rs_dp_grps[grp] + rs_dp_grps[control]]
            self.pds.treated_units = rs_dp_grps[grp]

            mde_val, mde_percent, pa_obj1, pa_obj2 = self._run_power_analysis()

            val_columns = [f"{int(length / 7)}wk_val" for length in self.test_lengths] + [
                "control_dmas",
                "test_dmas",
            ]
            percent_columns = [f"{int(length / 7)}wk_percent" for length in self.test_lengths] + [
                "control_dmas",
                "test_dmas",
            ]
            columns_pa = [f"{int(length / 7)}wk_pa_obj1" for length in self.test_lengths] + [
                f"{int(length / 7)}wk_pa_obj2" for length in self.test_lengths
            ] + ["control_dmas", "test_dmas"]

            mde_val.extend([rs_dp_grps[control], rs_dp_grps[grp]])
            mde_percent.extend([rs_dp_grps[control], rs_dp_grps[grp]])

            mde_val_df = pd.concat(
                [mde_val_df, pd.DataFrame([mde_val], columns=val_columns)], axis=0
            )
            mde_prc_df = pd.concat(
                [mde_prc_df, pd.DataFrame([mde_percent], columns=percent_columns)], axis=0
            )

            pa_obj1_list = [pa_obj1[length] for length in self.test_lengths]
            pa_obj2_list = [pa_obj2[length] for length in self.test_lengths]
            pa_obj_combined_list = pa_obj1_list + pa_obj2_list + [
                rs_dp_grps[control],
                rs_dp_grps[grp],
            ]

            power_results_df = pd.concat(
                [
                    power_results_df,
                    pd.DataFrame([pa_obj_combined_list], columns=columns_pa),
                ],
                axis=0,
            )

            mde_prc_df["test_prc"] = mde_prc_df["test_dmas"].apply(
                lambda x: np.round(
                    self.panel_data.wide_data.T[x].sum().sum() * 100
                    / self.panel_data.wide_data.sum().sum(),
                    2,
                )
            )
            mde_prc_df["control_prc"] = mde_prc_df["control_dmas"].apply(
                lambda x: np.round(
                    self.panel_data.wide_data.T[x].sum().sum() * 100
                    / self.panel_data.wide_data.sum().sum(),
                    2,
                )
            )
            mde_val_df["test_prc"] = mde_val_df["test_dmas"].apply(
                lambda x: np.round(
                    self.panel_data.wide_data.T[x].sum().sum() * 100
                    / self.panel_data.wide_data.sum().sum(),
                    2,
                )
            )
            mde_val_df["control_prc"] = mde_val_df["control_dmas"].apply(
                lambda x: np.round(
                    self.panel_data.wide_data.T[x].sum().sum() * 100
                    / self.panel_data.wide_data.sum().sum(),
                    2,
                )
            )
            power_results_df["test_prc"] = power_results_df["test_dmas"].apply(
                lambda x: np.round(
                    self.panel_data.wide_data.T[x].sum().sum() * 100
                    / self.panel_data.wide_data.sum().sum(),
                    2,
                )
            )
            power_results_df["control_prc"] = power_results_df["control_dmas"].apply(
                lambda x: np.round(
                    self.panel_data.wide_data.T[x].sum().sum() * 100
                    / self.panel_data.wide_data.sum().sum(),
                    2,
                )
            )

        return (
            mde_prc_df.reset_index(drop=True),
            mde_val_df.reset_index(drop=True),
            power_results_df.reset_index(drop=True),
        )

    def _run_power_analysis(self) -> tuple:
        mde_val = []
        mde_percent = []
        pa_df_dict = {}
        power_curve_dict = {}

        data = self.pds if hasattr(self, "pds") and self.pds is not None else self.panel_data

        for test_length in self.test_lengths:
            control_units = pd.DataFrame(
                data.wide_data.loc[
                    [unit for unit in data.units if unit not in data.treated_units]
                ].sum(axis=0),
                columns=["control"],
            )
            treated_units = pd.DataFrame(
                data.wide_data.loc[data.treated_units].sum(axis=0), columns=["treated"]
            )
            wide_agg = pd.concat([treated_units, control_units], axis=1)
            self.power_pds = PanelDataset(wide_agg.T, treated_units=["treated"])

            from panel_exp.methods.tbr import TBRRidge

            pa = PowerAnalysis(
                self.power_pds,
                model=TBRRidge,
                inference=self.inference,
                test_length=test_length,
                train_length=self.train_length,
                n_jobs=self.njobs,
                n_sample_prc=self.n_sample_prc,
                ci_version=self.ci_version,
                alpha=self.alpha,
                random_state=self.random_state,
            )
            pa.run_analysis()
            self.last_power_mde_semantics = dict(pa.mde_semantics)

            power_curve_df = (
                1
                - pd.pivot_table(
                    pa.output_df,
                    index="prc_effect",
                    columns="iteration",
                    values="mean_ss",
                ).mean(axis=1)
            ).reset_index()
            power_curve_df.columns = ["prc_effect", "power"]
            power_curve_dict[test_length] = power_curve_df

            result_df = pa.summary().T.copy(deep=True)
            result_df["test_length"] = test_length
            pa_df_dict[test_length] = result_df

            mde_val.append(result_df["MDE KPI"][0])
            mde_percent.append(result_df["MDE Percent"][0])

        return mde_val, mde_percent, pa_df_dict, power_curve_dict

    def export_run_readout_bundle(
        self,
        *,
        experiment_card: Optional[Any] = None,
        include_track_b_views: bool = False,
        include_trust_report: bool = False,
        trust_report_scenarios: Optional[list] = None,
        **bundle_kwargs: Any,
    ):
        """
        Export a portable RunBundle from ``last_evidence`` (opt-in Track B sidecar).

        Requires ``run_design`` to have populated ``last_evidence``. Does not run
        estimators or change scoring; delegates to ``export_geo_run_bundle``.
        """
        from panel_exp.artifacts.geo_run_export import export_geo_run_bundle

        if self.last_evidence is None:
            raise ValueError(
                "No experiment evidence on this design object; run run_design first."
            )
        return export_geo_run_bundle(
            evidence=self.last_evidence,
            experiment_card=experiment_card,
            include_track_b_views=include_track_b_views,
            include_trust_report=include_trust_report,
            trust_report_scenarios=trust_report_scenarios,
            **bundle_kwargs,
        )

    @staticmethod
    def plot_power_curve(pa_df_combined, test_length_label):
        key = f"{test_length_label}_pa_obj2"
        es_og = pa_df_combined.reset_index().loc[0, key]
        mde_values = es_og["prc_effect"].reset_index(drop=True)
        power_values = es_og["power"].reset_index(drop=True)
        neg_mask = (power_values >= 0.8) & (mde_values < 0)
        pos_mask = (power_values >= 0.8) & (mde_values > 0)
        mde_neg = mde_values[neg_mask].iloc[-1] if neg_mask.any() else None
        mde_pos = mde_values[pos_mask].iloc[0] if pos_mask.any() else None
        plt.plot(mde_values, power_values, label="Power Curve", color="blue")
        plt.axhline(0.8, color="red", linestyle="--", label="Power = 0.8")
        if mde_neg is not None:
            plt.axvline(mde_neg, color="green", linestyle="--", label=f"L_MDE: {np.round(mde_neg, 4)}")
        if mde_pos is not None:
            plt.axvline(mde_pos, color="orange", linestyle="--", label=f"H_MDE: {np.round(mde_pos, 4)}")
        plt.title("Power Curve Simulation @ 0.8", fontsize=15, pad=15)
        plt.xlabel("Effect Size (MDE)")
        plt.ylabel("Power")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.show()
