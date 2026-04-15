"""
Core: impact
============

This module houses the abstract base class and procedures for running panel
modeling and inference.

Summary of recent inference changes
-----------------------------------
- Added a dedicated `Placebo` inference branch to `run_analysis`.
- Wired placebo inference to `placebo_with_ci_inversion(...)` so the main
  package path uses an estimate-centered CI band rather than only a placebo
  null envelope.
- Stored placebo inversion outputs in `self.results`, including cumulative
  effect-scale inversion bounds when available.
- Added imports for both `placebo(...)` and
  `placebo_with_ci_inversion(...)` to support diagnostic and CI-producing
  placebo workflows.
- Preserved existing `Kfold`, `TimeSeriesKfold`, `Conformal`, `JKP`, and
  `UnitJackKnife` branches without changing their main dispatch structure.
"""

from __future__ import annotations
import numpy as np
import pandas as pd

from panel_exp.inference.unit_jackknife import unit_jk, jkp
from panel_exp.inference.conformal import conformal
from panel_exp.inference.k_fold import kfold, panel_timeseries_kfold, panel_timeseries_kfold_cumulative
from panel_exp.inference.placebo import placebo, placebo_with_ci_inversion
from panel_exp.inference.block_residual_bootstrap import block_residual_bootstrap

from panel_exp import *

from matplotlib import pyplot as plt
from typing import Dict
from abc import (
	ABC,
	abstractmethod,
	)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import jax.numpy as jnp

class ImpactAnalyzer(ABC):
    """
    Abstract Base Class for running various methods SCM, ASynth, TBR with various inference methods i.e. JK, JK+
    This class will assume there is only one treatment time period.
    
    
    methods
    -------
    fit_data(panel_data):
        Prepares the data for the specific method being used.
    fit_model():
        Fits a model on the pre-treatment data.
    run_analysis(panel_data, inference_kwargs):
        Performs a full analysis including data preparation, model fitting, prediction, and inference.
    """

    @abstractmethod
    def fit_data(self, panel_data: PanelDataset) -> PanelDataset:
        """
        Prepares the data for the specific method being used.

        Some methods require different data formats. This function prepares the data accordingly.

        :param panel_data: PanelDataset
            The panel data to be prepared.
        
        :returns: PanelDataset
            The prepared panel data.
        """
        pass

    @abstractmethod
    def fit_model(self) -> object:
        """
        Fits a model on the pre-treatment data.

        Takes in the panel dataset and fits a model on the pre-treatment data.

        :returns: object
            A model object with a predict function.
        """
        pass

    def run_analysis(
        self,
        panel_data: PanelDataset,
        **inference_kwargs,
    ) -> Dict:
        """
        Performs a full analysis including data preparation, model fitting, prediction, and inference.

        This method performs the full analysis pipeline: fit_data -> fit_model -> predict -> inference.

        :param panel_data: PanelDataset
            The panel data to be analyzed.
        :param inference_kwargs: dict
            Additional arguments for inference.
        
        :returns: dict
            A dictionary containing the results of the analysis.
        """

        self.panel_data = panel_data

        if self.inference is None:
            self.fit_data(panel_data)
            self.model = self.fit_model()
            self.y_hat = self.model.predict(self.panel_data.control_series(self.panel_data.treated_units).values.T)

            y = self.panel_data.treated_series(self.panel_data.treated_units).values.T
            if y.shape[0] == self.panel_data.num_timepoints and y.shape[1] == 1:
              y = y.reshape(-1)

            if len(self.y_hat.shape) == 2 and self.y_hat.shape[0] == self.panel_data.num_timepoints and self.y_hat.shape[1] == 1:
              self.y_hat = self.y_hat.reshape(-1)

            self.results = {
                "times": self.panel_data.times,
                "y": y,
                "y_hat": self.y_hat,
            }

        elif self.inference in ["UnitJackKnife", "JKP"]:
            if self.inference == "UnitJackKnife":
                if self.panel_data.num_control_units < 2:
                    raise ValueError("UnitJackKnife requires at least 2 control units")
            self.fit_data(self.panel_data)
            self.model = self.fit_model()
            self.y_hat = self.model.predict(self.panel_data.control_series(self.panel_data.treated_units).values.T)

            y = self.panel_data.treated_series(self.panel_data.treated_units).values.T
            if y.shape[0] == self.panel_data.num_timepoints and y.shape[1] == 1:
              y = y.reshape(-1)

            if len(self.y_hat.shape) == 2 and self.y_hat.shape[0] == self.panel_data.num_timepoints and self.y_hat.shape[1] == 1:
              self.y_hat = self.y_hat.reshape(-1)

            self.results = {
                "times": self.panel_data.times,
                "y": y,
                "y_hat": self.y_hat,
            }

            if self.inference == "UnitJackKnife":
                self.errors = unit_jk(
                    self.panel_data, self.__class__, alpha=self.alpha, **inference_kwargs
                )

                self.results["y_upper"] = self.results["y_hat"] + self.errors
                self.results["y_lower"] = self.results["y_hat"] - self.errors


            if self.inference == "JKP":
                pre_t_time = self.panel_data.treated_start_idxs[0]-1
                n_treated_units = len(self.panel_data.treated_units)

                self.lower, self.upper, self.y_hat_median = jkp(
                    self.panel_data, self.__class__, alpha=self.alpha, **inference_kwargs
                )

                self.results["y_lower"] = np.zeros_like(self.results['y'])
                self.results["y_upper"] = np.zeros_like(self.results['y'])

                self.results["y_lower"][-len(self.lower):,] = self.results["y"][self.panel_data.treated_start_idxs[0]:] -self.lower
                self.results["y_upper"][-len(self.upper):,] = self.results["y"][self.panel_data.treated_start_idxs[0]:] -self.upper
                #self.results['y_hat'][-len(self.y_hat_median):,] = self.results["y"][self.panel_data.treated_start_idxs[0]:] - self.y_hat_median

        elif self.inference == "Bayesian":
            self.fit_data(self.panel_data)
            self.model = self.fit_model()
            self.y_hat = self.model.predict(self.panel_data.control_series(self.panel_data.treated_units).values.T)

            y_mu = jnp.mean(self.y_hat, axis=0) 

            y_lower = jnp.quantile(self.y_hat, self.alpha, axis=0)
            y_upper = jnp.quantile(self.y_hat, 1-self.alpha, axis=0)

            # y_lower = hpdi(self.y_hat, 1-self.alpha, axis=0)[0]
            # y_upper = hpdi(self.y_hat, 1-self.alpha, axis=0)[1]

            # y_lower = jnp.mean(self.y_hat, axis=0) - 1.96 * jnp.std(self.y_hat, axis=0) 
            # y_upper = jnp.mean(self.y_hat, axis=0) + 1.96 * jnp.std(self.y_hat, axis=0) 

            y = self.panel_data.treated_series(self.panel_data.treated_units).values.T
            if y.shape[0] == self.panel_data.num_timepoints and y.shape[1] == 1:
              y = y.reshape(-1)

            self.results = {
                "times": self.panel_data.times,
                "y": y,
                "y_hat": y_mu,
            }
            self.results["y_upper"] = y_upper
            self.results["y_lower"] = y_lower

        elif self.inference == 'BlockResidualBootstrap':
          self.fit_data(self.panel_data)
          self.model = self.fit_model()
          self.y_hat = self.model.predict(self.panel_data.control_series(self.panel_data.treated_units).values.T)

          y = self.panel_data.treated_series(self.panel_data.treated_units).values.T
          if y.shape[0] == self.panel_data.num_timepoints and y.shape[1] == 1:
            y = y.reshape(-1)

          if len(self.y_hat.shape) == 2 and self.y_hat.shape[0] == self.panel_data.num_timepoints and self.y_hat.shape[1] == 1:
            self.y_hat = self.y_hat.reshape(-1)

          self.results = {
                "times": self.panel_data.times,
                "y": y,
                "y_hat": self.y_hat,
            }

          _is_scm = self.__class__.__name__ in (
              "AugSynth",
              "AugSynthCVXPY",
              "SyntheticControlCVXPY",
          )
          _def_n, _def_bl, _def_mtp = (100, 8, 16) if _is_scm else (200, 7, 12)
          n_bootstrap = inference_kwargs.pop("n_bootstrap", _def_n)
          block_length = inference_kwargs.pop("block_length", _def_bl)
          min_train_periods = inference_kwargs.pop("min_train_periods", _def_mtp)
          pool_donor_residuals = inference_kwargs.pop("pool_donor_residuals", False)
          _sp = inference_kwargs.pop("show_progress", None)
          show_progress = _sp if _sp is not None else _is_scm
          random_state = inference_kwargs.get("random_state", None)
          center_residuals = inference_kwargs.pop("center_residuals", True)
          refit_in_bootstrap = inference_kwargs.pop("refit_in_bootstrap", False)
          refit_mode = inference_kwargs.pop("refit_mode", "post_only")
          ci_method = inference_kwargs.pop("ci_method", "percentile")
          bootstrap_type = inference_kwargs.pop("bootstrap_type", "block")

          self.bounds, brb_stats = block_residual_bootstrap(
              self.panel_data,
              self.__class__,
              alpha=self.alpha,
              n_bootstrap=n_bootstrap,
              block_length=block_length,
              min_train_periods=min_train_periods,
              pool_donor_residuals=pool_donor_residuals,
              show_progress=show_progress,
              random_state=random_state,
              center_residuals=center_residuals,
              refit_in_bootstrap=refit_in_bootstrap,
              refit_mode=refit_mode,
              ci_method=ci_method,
              bootstrap_type=bootstrap_type,
              return_stats=True,
              **inference_kwargs,
          )
          self.results["block_residual_bootstrap_stats"] = brb_stats

          self.results["y_upper"] = -self.bounds[:, :, 2].T + self.results["y"].reshape(self.bounds[:, :, 2].T.shape)
          self.results["y_hat"] = -self.bounds[:, :, 1].T + self.results["y"].reshape(self.bounds[:, :, 1].T.shape)
          self.results["y_lower"] = -self.bounds[:, :, 0].T + self.results["y"].reshape(self.bounds[:, :, 0].T.shape)

          if len(self.panel_data.treated_units) == 1:
            self.results["y_upper"] = self.results["y_upper"].flatten()
            self.results["y_hat"] = self.results["y_hat"].flatten()
            self.results["y_lower"] = self.results["y_lower"].flatten()

          self.results["effect_cumulative_brb"] = brb_stats.get("effect_cumulative_brb", np.nan)
          self.results["effect_ci_lower_cumulative_brb"] = brb_stats.get("effect_ci_lower_cumulative_brb", np.nan)
          self.results["effect_ci_upper_cumulative_brb"] = brb_stats.get("effect_ci_upper_cumulative_brb", np.nan)

        elif self.inference == "Conformal":
            self.fit_data(self.panel_data)
            self.model = self.fit_model()
            self.y_hat = self.model.predict(self.panel_data.control_series(self.panel_data.treated_units).values.T)

            y = self.panel_data.treated_series(self.panel_data.treated_units).values.T
            if y.shape[0] == self.panel_data.num_timepoints and y.shape[1] == 1:
                y = y.reshape(-1)

            if len(self.y_hat.shape) == 2 and self.y_hat.shape[0] == self.panel_data.num_timepoints and self.y_hat.shape[1] == 1:
                self.y_hat = self.y_hat.reshape(-1)

            self.results = {
                "times": self.panel_data.times,
                "y": y,
                "y_hat": self.y_hat,
                }

            # auto-generate potential nulls
            post_mean = (self.results['y']-self.results['y_hat'])[self.panel_data.treated_start_idxs[0]:].std()
            post_mean = np.max(np.abs((self.results['y']-self.results['y_hat'])[self.panel_data.treated_start_idxs[0]:]))


            lower, upper = conformal(self.panel_data,
                                                             self.__class__, 
                                                             alpha=self.alpha, 
                                                             nulls=np.linspace(-post_mean*10, post_mean*10, 100), 
                                                             **inference_kwargs  )

            self.lower = lower 
            self.upper = upper
            self.results["y_upper"] = -upper + self.results["y"]
            self.results["y_lower"] = -lower + self.results["y"]

        elif self.inference == 'Kfold':
          self.fit_data(self.panel_data)
          self.model = self.fit_model()
          self.y_hat = self.model.predict(self.panel_data.control_series(self.panel_data.treated_units).values.T)
          y = self.panel_data.treated_series(self.panel_data.treated_units).values.T

          if y.shape[0] == self.panel_data.num_timepoints and y.shape[1] == 1:
            y = y.reshape(-1)

          if len(self.y_hat.shape) == 2 and self.y_hat.shape[0] == self.panel_data.num_timepoints and self.y_hat.shape[1] == 1:
            self.y_hat = self.y_hat.reshape(-1)

          self.results = {
                "times": self.panel_data.times,
                "y": y,
                "y_hat": self.y_hat,
            }
          
          self.bounds = kfold(self.panel_data, self.__class__)

          self.results["y_upper"] = -self.bounds[:, :, 2].T + self.results["y"].reshape(self.bounds[:, :, 2].T.shape)
          self.results["y_hat"] = -self.bounds[:, :, 1].T + self.results["y"].reshape(self.bounds[:, :, 1].T.shape)
          self.results["y_lower"] = -self.bounds[:, :, 0].T + self.results["y"].reshape(self.bounds[:, :, 0].T.shape)

          if len(self.panel_data.treated_units) == 1:
            # not the best way to do this -- we should adjust all result ndarrays to be in shape of (time_units, treated_units). Right now 1 treated unit will be (time_units,)
            self.results["y_upper"] = self.results["y_upper"].flatten()
            self.results["y_hat"] = self.results["y_hat"].flatten()
            self.results["y_lower"] = self.results["y_lower"].flatten()

        elif self.inference == 'Placebo':
          self.fit_data(self.panel_data)
          self.model = self.fit_model()
          self.y_hat = self.model.predict(self.panel_data.control_series(self.panel_data.treated_units).values.T)

          y = self.panel_data.treated_series(self.panel_data.treated_units).values.T
          if y.shape[0] == self.panel_data.num_timepoints and y.shape[1] == 1:
            y = y.reshape(-1)

          if len(self.y_hat.shape) == 2 and self.y_hat.shape[0] == self.panel_data.num_timepoints and self.y_hat.shape[1] == 1:
            self.y_hat = self.y_hat.reshape(-1)

          self.results = {
                "times": self.panel_data.times,
                "y": y,
                "y_hat": self.y_hat,
            }

          n_control = len(self.panel_data.control_units)
          is_tbr = self.__class__.__name__ == "TBR"

          if is_tbr:
            self.results["placebo_unsupported"] = "TBR requires aggregated control; placebo-in-space excluded"
          elif n_control <= 1:
            self.results["placebo_unsupported"] = f"Placebo requires >1 control units (got {n_control})"
          elif n_control < 5:
            self.results["placebo_unsupported"] = f"Placebo requires >=5 control units (got {n_control})"

          if self.results.get("placebo_unsupported"):
            n_treated = len(self.panel_data.treated_units)
            n_times = self.panel_data.num_timepoints
            effect = np.asarray(self.results["y"]) - np.asarray(self.results["y_hat"])
            if effect.ndim == 1:
              effect = effect.reshape(1, -1)
            bounds = np.stack([effect, effect, effect], axis=-1)
            self.bounds = bounds
            self.results["y_upper"] = np.asarray(self.results["y_hat"]).copy()
            self.results["y_lower"] = np.asarray(self.results["y_hat"]).copy()
          else:
            self.bounds, placebo_stats_dict = placebo_with_ci_inversion(
                self.panel_data, self.__class__, alpha=self.alpha, **inference_kwargs
            )
            self.results["placebo_stats"] = placebo_stats_dict

            self.results["y_upper"] = -self.bounds[:, :, 2].T + self.results["y"].reshape(self.bounds[:, :, 2].T.shape)
            self.results["y_hat"] = -self.bounds[:, :, 1].T + self.results["y"].reshape(self.bounds[:, :, 1].T.shape)
            self.results["y_lower"] = -self.bounds[:, :, 0].T + self.results["y"].reshape(self.bounds[:, :, 0].T.shape)

            if len(self.panel_data.treated_units) == 1:
              self.results["y_upper"] = self.results["y_upper"].flatten()
              self.results["y_hat"] = self.results["y_hat"].flatten()
              self.results["y_lower"] = self.results["y_lower"].flatten()

            ci_low = placebo_stats_dict.get("ci_low_inversion")
            ci_high = placebo_stats_dict.get("ci_high_inversion")
            if ci_low is not None and ci_high is not None and np.isfinite(ci_low) and np.isfinite(ci_high):
              self.results["effect_ci_lower_inversion"] = float(ci_low)
              self.results["effect_ci_upper_inversion"] = float(ci_high)

        elif self.inference == 'TimeSeriesKfold':
          # Get parameters from inference_kwargs or use defaults
          k = inference_kwargs.get('k', 5)
          debias_flag = inference_kwargs.get('debias_flag', True)
          block_scheme = inference_kwargs.get('block_scheme', 'expanding')
          n_jobs = inference_kwargs.get('n_jobs', 1)
          random_state = inference_kwargs.get('random_state', None)
          show_progress = inference_kwargs.get('show_progress', True)
          diagnostics_path = inference_kwargs.get('diagnostics_path', None) or getattr(self, 'tsk_diagnostics_path', None)
          
          # Fit the model for the full dataset (needed for notebook access)
          self.fit_data(self.panel_data)
          self.model = self.fit_model()
          
          y = self.panel_data.treated_series(self.panel_data.treated_units).values.T
          if y.shape[0] == self.panel_data.num_timepoints and y.shape[1] == 1:
              y = y.reshape(-1)

          self.results = {
              "times": self.panel_data.times,
              "y": y,
              "y_hat": None,  # Will be set by k-fold function
          }

          if self.full_model:
              # When full_model=True, get pre-test counterfactuals directly from model
              # and only use k-fold for treatment period
              self.y_hat = self.model.predict(self.panel_data.control_series(self.panel_data.treated_units).values.T)
              
              if len(self.y_hat.shape) == 2 and self.y_hat.shape[0] == self.panel_data.num_timepoints and self.y_hat.shape[1] == 1:
                  self.y_hat = self.y_hat.reshape(-1)
              
              # Set pre-test predictions from full model
              self.results["y_hat"] = self.y_hat
              
              # Use k-fold only for treatment period confidence intervals
              treatment_bounds = panel_timeseries_kfold(
                  self.panel_data, self.__class__, alpha=self.alpha, k=k, debias_flag=debias_flag,
                  block_scheme=block_scheme, n_jobs=n_jobs, random_state=random_state,
                  show_progress=show_progress, diagnostics_path=diagnostics_path
              )
              
              # Combine pre-test predictions from full model with treatment period bounds
              pre_t = self.panel_data.treated_start_idxs[0]
              
              # Pre-test: use full model predictions
              self.results["y_hat"][:pre_t] = self.y_hat[:pre_t]
              
              # Treatment period: use k-fold results
              treatment_predictions = -treatment_bounds[:, pre_t:, 1].T + self.results["y"][pre_t:].reshape(treatment_bounds[:, pre_t:, 1].T.shape)
              # Ensure proper shape - flatten if needed
              if treatment_predictions.shape[1] == 1:
                  treatment_predictions = treatment_predictions.flatten()
              self.results["y_hat"][pre_t:] = treatment_predictions
              
              self.results["y_upper"] = np.zeros_like(self.results["y"])
              self.results["y_lower"] = np.zeros_like(self.results["y"])
              
              treatment_upper = -treatment_bounds[:, pre_t:, 2].T + self.results["y"][pre_t:].reshape(treatment_bounds[:, pre_t:, 2].T.shape)
              treatment_lower = -treatment_bounds[:, pre_t:, 0].T + self.results["y"][pre_t:].reshape(treatment_bounds[:, pre_t:, 0].T.shape)
              
              # Ensure proper shape - flatten if needed
              if treatment_upper.shape[1] == 1:
                  treatment_upper = treatment_upper.flatten()
              if treatment_lower.shape[1] == 1:
                  treatment_lower = treatment_lower.flatten()
                  
              self.results["y_upper"][pre_t:] = treatment_upper
              self.results["y_lower"][pre_t:] = treatment_lower

          else:
              # Use k-fold for both pre-test and treatment period
              self.bounds = panel_timeseries_kfold(
                  self.panel_data, self.__class__, alpha=self.alpha, k=k, debias_flag=debias_flag,
                  block_scheme=block_scheme, n_jobs=n_jobs, random_state=random_state,
                  show_progress=show_progress, diagnostics_path=diagnostics_path
              )

              # Set y_hat from bounds (mean predictions)
              y_hat_from_bounds = -self.bounds[:, :, 1].T + self.results["y"].reshape(self.bounds[:, :, 1].T.shape)
              # Ensure proper shape - flatten if needed
              if y_hat_from_bounds.shape[1] == 1:
                  y_hat_from_bounds = y_hat_from_bounds.flatten()
              self.results["y_hat"] = y_hat_from_bounds
              
              # Set confidence intervals
              y_upper_from_bounds = -self.bounds[:, :, 2].T + self.results["y"].reshape(self.bounds[:, :, 2].T.shape)
              y_lower_from_bounds = -self.bounds[:, :, 0].T + self.results["y"].reshape(self.bounds[:, :, 0].T.shape)
              
              # Ensure proper shape - flatten if needed
              if y_upper_from_bounds.shape[1] == 1:
                  y_upper_from_bounds = y_upper_from_bounds.flatten()
              if y_lower_from_bounds.shape[1] == 1:
                  y_lower_from_bounds = y_lower_from_bounds.flatten()
                  
              self.results["y_upper"] = y_upper_from_bounds
              self.results["y_lower"] = y_lower_from_bounds

          if len(self.panel_data.treated_units) == 1:
              self.results["y_upper"] = self.results["y_upper"].flatten()
              self.results["y_hat"] = self.results["y_hat"].flatten()
              self.results["y_lower"] = self.results["y_lower"].flatten()

          # Store direct cumulative TSK outputs for aggregate reporting (avoid summing weekly bounds)
          cumulative_bounds = panel_timeseries_kfold_cumulative(
              self.panel_data, self.__class__, alpha=self.alpha, k=k, debias_flag=debias_flag,
              block_scheme=block_scheme, n_jobs=n_jobs, random_state=random_state,
              show_progress=show_progress
          )
          pre_t = self.panel_data.treated_start_idxs[0]
          n_treated = self.panel_data.num_treated_time_periods[0]
          # cumulative_bounds shape: (n_units, n_timepoints, 3) with [lower, mean, upper]
          # Last treatment-period row = cumulative effect over full window
          if n_treated > 0 and cumulative_bounds.shape[1] >= pre_t + n_treated:
              last_idx = pre_t + n_treated - 1
              cum_lo = cumulative_bounds[:, last_idx, 0]
              cum_mu = cumulative_bounds[:, last_idx, 1]
              cum_hi = cumulative_bounds[:, last_idx, 2]
              self.results["effect_cumulative_tsk"] = float(np.nanmean(cum_mu))
              self.results["effect_ci_lower_cumulative_tsk"] = float(np.nanmean(cum_lo))
              self.results["effect_ci_upper_cumulative_tsk"] = float(np.nanmean(cum_hi))

        else:
            raise NotImplementedError(f"{self.inference} is not a supported inference method")

    def summary(self):
        """
        This function takes uses self.results and provides a summary of outcomes.
        
        :returns: pd.DataFrame
            A DataFrame containing the summary statistics.
        """
        post_actual = self.results["y"][self.panel_data.treated_start_idxs[0] :self.panel_data.treated_end_idxs[0]+1]
        post_predicted = self.results["y_hat"][self.panel_data.treated_start_idxs[0] :self.panel_data.treated_end_idxs[0]+1]
        # post_predicted = self.y_hat[self.panel_data.treated_start_idxs[0] :self.panel_data.treated_end_idxs[0]]
        pointwise_diff = post_actual - post_predicted

        cumulative_diff_mean = np.mean(pointwise_diff)
        cumulative_diff_sum = np.sum(pointwise_diff)

        rel_effect_mean = cumulative_diff_mean / np.mean(post_predicted) * 100
        rel_effect_sum = cumulative_diff_sum / np.sum(post_predicted) * 100

        return pd.DataFrame(
                {
                    "Average": [
                        np.mean(post_actual),
                        np.mean(post_predicted),
                        "",
                        cumulative_diff_mean,
                        "",
                        rel_effect_mean,
                    ],
                    "Cumulative": [
                        np.sum(post_actual),
                        np.sum(post_predicted),
                        "",
                        cumulative_diff_sum,
                        "",
                        rel_effect_sum,
                    ],
                },
                index=[
                    "Actual",
                    "Predicted",
                    " ",
                    "Absolute Effect",
                    " ",
                    "Relative Effect",
                ],
            )
 

    def plot(self, legend=True, figsize=(15, 12)):
        """
        This function takes uses self.results and provides a summary of outcomes. 
        
        :param legend: If True, legend will be displayed
        :param figsize: Size of the figure
        
        :returns: None
            Show a plot of the calculated results. 

        """

        fig, axs = plt.subplots(3, 1, figsize=figsize)
        treatment_mask = np.arange(self.panel_data.num_timepoints) >= self.panel_data.treated_start_idxs[0]

        ### plot model vs actual.
        # actual
        axs[0].plot(self.results["y"], color="black", linewidth=2, label="Observed")

        # model
        axs[0].plot(self.results["y_hat"], "r--", linewidth=2, label="Inferred")
        # axs[0].plot(self.y_hat, "r--", linewidth=2, label="Inferred")

        if self.inference is not None:
          if len(self.panel_data.treated_units) == 1:
            axs[0].fill_between(
                np.arange(self.panel_data.num_timepoints)[treatment_mask],
                np.asarray(self.results["y_lower"])[treatment_mask],
                np.asarray(self.results["y_upper"])[treatment_mask],
                facecolor="gray",
                interpolate=True,
                alpha=0.25,
            )
          if len(self.panel_data.treated_units) > 1:
            for _ in range(self.results['y_lower'].shape[1]):
              axs[0].fill_between(
                np.arange(self.panel_data.num_timepoints)[treatment_mask],
                np.asarray(self.results["y_lower"])[treatment_mask, _],
                np.asarray(self.results["y_upper"])[treatment_mask, _],
                facecolor="gray",
                interpolate=True,
                alpha=0.25,
            )


        axs[0].set_title("Observation vs Prediction")
        axs[0].axvline(
            self.panel_data.treated_start_idxs[0] , color="black", linestyle="--"
        )

        axs[0].axvline(
            self.panel_data.treated_end_idxs[0] , color="black", linestyle="--"
        )

        if legend:
          axs[0].legend(loc="upper left")

        ### Pointwise Difference
        pointwise = self.results["y"] - self.results["y_hat"]
        # pointwise = self.results["y"] - self.y_hat

        axs[1].plot(pointwise, "r--", linewidth=2, label="Pointwise Difference")
        axs[1].axvline(
            self.panel_data.treated_start_idxs[0] , color="black", linestyle="--"
        )
        axs[1].axvline(
            self.panel_data.treated_end_idxs[0] , color="black", linestyle="--"
        )

        axs[1].axhline(0, color="black", linewidth=2)

        if self.inference is not None:
          if len(self.panel_data.treated_units) == 1:
            effect_lower = self.results["y"].flatten() - np.asarray(self.results["y_upper"])
            effect_upper = self.results["y"].flatten() - np.asarray(self.results["y_lower"])
            axs[1].fill_between(
                np.arange(self.panel_data.num_timepoints)[treatment_mask],
                effect_lower[treatment_mask],
                effect_upper[treatment_mask],
                facecolor="gray",
                interpolate=True,
                alpha=0.25,
            )

          if len(self.panel_data.treated_units) > 1:
            for _ in range(self.results['y_lower'].shape[1]):
              effect_lower = np.asarray(self.results["y"])[:, _].flatten() - np.asarray(self.results["y_upper"])[:, _]
              effect_upper = np.asarray(self.results["y"])[:, _].flatten() - np.asarray(self.results["y_lower"])[:, _]
              axs[1].fill_between(
                np.arange(self.panel_data.num_timepoints)[treatment_mask],
                effect_lower[treatment_mask],
                effect_upper[treatment_mask],
                facecolor="gray",
                interpolate=True,
                alpha=0.25,
            )


        axs[1].set_title("Pointwise Difference")
        if legend:
          axs[1].legend(loc="upper left")

        ### Cumulative Difference


        if len(self.results["y"].shape) == 1:
          self.cumulative_diff_post = (self.results["y"] - self.results["y_hat"])[
              self.panel_data.treated_start_idxs[0] : #self.panel_data.treated_end_idxs[0] #1/22
          ].cumsum()

          # cumulative_diff_post = (self.results["y"] - self.y_hat)[
          #     self.panel_data.treated_start_idxs[0] : #self.panel_data.treated_end_idxs[0] #1/22
          # ].cumsum()

        elif len(self.results["y"].shape) == 2:
          self.cumulative_diff_post = (self.results["y"] - self.results["y_hat"])[
              self.panel_data.treated_start_idxs[0] : #self.panel_data.treated_end_idxs[0] #1/22
          ].cumsum(axis=0)

        # elif len(self.results["y"].shape) == 2:
        #   cumulative_diff_post = (self.results["y"] - self.y_hat)[
        #       self.panel_data.treated_start_idxs[0] : #self.panel_data.treated_end_idxs[0] #1/22
        #   ].cumsum(axis=0)

        if len(self.results["y"].shape) == 2:
          self.cumulative_diff_pre = np.zeros((self.panel_data.treated_start_idxs[0] - 1, len(self.panel_data.treated_units)))

        else:
          self.cumulative_diff_pre = np.zeros(self.panel_data.treated_start_idxs[0] - 1 )

        self.cumulative_diff = np.concatenate([self.cumulative_diff_pre, self.cumulative_diff_post])

        axs[2].plot(self.cumulative_diff, "r--", linewidth=2, label="Cumulative Difference")

        if self.inference is not None:
            if len(self.results["y"].shape) == 1:
              self.low_cumulative_diff_post = (self.results["y"] - self.results["y_lower"])[
                self.panel_data.treated_start_idxs[0] : #self.panel_data.treated_end_idxs[0] #1/22
              ].cumsum()

              self.high_cumulative_diff_post = (self.results["y"] - self.results["y_upper"])[
                self.panel_data.treated_start_idxs[0] : #self.panel_data.treated_end_idxs[0] #1/22
              ].cumsum()

            elif len(self.results["y"].shape) == 2:
              self.low_cumulative_diff_post = (self.results["y"] - self.results["y_lower"])[
                self.panel_data.treated_start_idxs[0] : #self.panel_data.treated_end_idxs[0] #1/22
              ].cumsum(axis=0)

              self.high_cumulative_diff_post = (self.results["y"] - self.results["y_upper"])[
                self.panel_data.treated_start_idxs[0] : #self.panel_data.treated_end_idxs[0] #1/22
              ].cumsum(axis=0)

            if len(self.results["y"].shape) == 2:
              self.low_cumulative_diff_pre = np.zeros((self.panel_data.treated_start_idxs[0]-1,  len(self.panel_data.treated_units)))
              self.high_cumulative_diff_pre = np.zeros((self.panel_data.treated_start_idxs[0]-1, len(self.panel_data.treated_units)))

            else:
              self.low_cumulative_diff_pre = np.zeros(self.panel_data.treated_start_idxs[0]-1)
              self.high_cumulative_diff_pre = np.zeros(self.panel_data.treated_start_idxs[0]-1)


            self.low_cumulative_diff = np.concatenate(
                [self.cumulative_diff_pre, self.low_cumulative_diff_post]
            )

            self.high_cumulative_diff = np.concatenate(
                [self.cumulative_diff_pre, self.high_cumulative_diff_post]
            )
            if len(self.results["y"].shape) == 1:
              cumulative_mask = np.arange(self.panel_data.num_timepoints - 1) >= (self.panel_data.treated_start_idxs[0] - 1)
              axs[2].fill_between(
                np.arange(self.panel_data.num_timepoints - 1)[cumulative_mask],
                np.asarray(self.low_cumulative_diff)[cumulative_mask],
                np.asarray(self.high_cumulative_diff)[cumulative_mask],
                facecolor="gray",
                interpolate=True,
                alpha=0.25,
              )

            elif len(self.results["y"].shape) > 1:
              if len(self.panel_data.treated_units) > 1:
                for _ in range(self.results['y_lower'].shape[1]):
                  cumulative_mask = np.arange(self.panel_data.num_timepoints - 1) >= (self.panel_data.treated_start_idxs[0] - 1)
                  axs[2].fill_between(
                    np.arange(self.panel_data.num_timepoints - 1)[cumulative_mask],
                    np.asarray(self.low_cumulative_diff)[cumulative_mask, _],
                    np.asarray(self.high_cumulative_diff)[cumulative_mask, _],
                    facecolor="gray",
                    interpolate=True,
                    alpha=0.25,
                    )


        axs[2].axvline(
            self.panel_data.treated_start_idxs[0] , color="black", linestyle="--"
        )

        axs[2].axvline(
            self.panel_data.treated_end_idxs[0] , color="black", linestyle="--"
        )

        axs[2].axhline(0, color="black", linewidth=2)
        axs[2].set_title("Cumulative Difference")
        if legend:
          axs[2].legend(loc="upper left")
        plt.show()
        