"""
Core: impact
============

This module houses the abstract base class and procedures for running panel
modeling and inference.

Inference dispatch is handled by ``panel_exp.inference.registry``; each mode
registers name, aliases, estimator checks, run handler, output keys, defaults,
and failure behavior. ``run_analysis`` delegates to the registry.
"""

from __future__ import annotations
import numpy as np
import pandas as pd

from panel_exp.inference.registry import get_inference_registry
from panel_exp.panel_data import PanelDataset

from matplotlib import pyplot as plt
from typing import Dict
from abc import ABC, abstractmethod

class ImpactAnalyzer(ABC):
    """
    Abstract Base Class for running various methods SCM, ASynth, TBR with various inference methods i.e. JK, JK+
    This class will assume there is only one treatment time period.

    Estimator maturity (validation readiness, not statistical superiority) is
    available via ``estimator_metadata`` after ``run_analysis`` and in
    ``results['inference_metadata']`` when inference runs.

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
        get_inference_registry().run(
            self.inference,
            self,
            panel_data,
            inference_kwargs,
        )
        return self.results

    @property
    def estimator_metadata(self):
        """Read-only maturity metadata for this estimator class (does not block runs)."""
        from panel_exp.method_registry import get_method_registry

        return get_method_registry().metadata_for_class(self.__class__.__name__)

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

        if self.inference is not None and self.results.get("intervals_available", True):
          if "y_lower" not in self.results or "y_upper" not in self.results:
            pass
          elif len(self.panel_data.treated_units) == 1:
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
        