"""

Methods: SCM
=================

Implementations of Synthetic Control and Augmented Synthetic Control.

"""
from __future__ import annotations
import numpy as np
import pandas as pd
import scipy.stats as st
from dataclasses import dataclass

from matplotlib import pyplot as plt
from typing import Callable, Dict, Optional
from abc import (
    ABC,
    abstractmethod,
    )

from ..impact import ImpactAnalyzer
from ..inference.unit_jackknife import unit_jk

from scipy.optimize import minimize
from sklearn.linear_model import RidgeCV, Ridge
import warnings
 
import itertools

class SyntheticControl(ImpactAnalyzer):
    """
    Implements the Synthetic Control Method (SCM) for causal inference.
    
    
    ----------
    :param inference callable: 
        the inference method to use, if any
    :param penalty str: 
        the penalty to use for the optimization problem
    :param penalty_strength float: 
        the strength of the penalty to use
    :param alpha: 
        controls type 1 error
    :param full_model: 
        used internally for conformal inference
    :param opt_package: 
        Defauls is SciPy can select CVXPY as well. 
    
    methods
    -------
    fit_data(panel_data):
        Take a PanelDataset and return X, y for the model
    fit_model():
        Internal method to fit the model
    """

    def __init__(
        self,
        inference: Optional[Callable] = None,
        penalty: str = "l1",
        penalty_strength: float = 0.05,
        alpha: float = 0.05,
        full_model = False ,
        method = 'SLSQP'): 

        self.penalty = penalty
        self.penalty_strength = penalty_strength
        self.inference = inference
        self.alpha = alpha
        #self.model_args = model_args
        self.full_model = full_model
        # changes method if there is one, else return SLSQP
        #self.method = self.opt_args.get("method", None)
        #self.x0 = self.opt_args.get('x0_init', None)
        self.method = method 



    def copy(self):
        import copy 
        return copy.deepcopy(self)



    def fit_data(self, panel_data):
        # no need to change anything from panel dataset
        self.panel_data = panel_data
        
    def fit_model(self):
        
        if self.full_model:
            control, test = self.panel_data.split_control_test_units( self.panel_data.treated_units, period='full')

        if not self.full_model:
            control, test = self.panel_data.split_control_test_units(treated_units = self.panel_data.treated_units)


        control=control.T.values
        test = test.values

        def balance_objective(x):
            x = x.reshape((control.shape[1], test.shape[0]))
            imbalance = np.sum(np.square(test.T - control @ x))
            if self.penalty == "entropy":
                imbalance += self.penalty_strength * -np.sum(x * np.log(x))
            elif self.penalty == "l1":
                imbalance += self.penalty_strength * np.sum(np.abs(x))
            elif self.penalty == "l2":
                imbalance += self.penalty_strength * np.sum(np.square(x))
            elif self.penalty == "none":
                imbalance += self.penalty_strength  
            else:
                #raise NotImplemented(f"Unknown penalty {penalty}")
                imbalance += np.sum(np.square(x))
            return imbalance 
        
        # we see a lot of failures, so following attempts to try a few different things: 
        simplex_bounds = [(0, 1) for _ in range((control.shape[1] * test.shape[0]))]

        x0 = (np.ones((control.shape[1], test.shape[0])) / control.shape[1]).flatten()
        #x0 = self.x0
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            res = minimize(
                        balance_objective,
                        x0,
                        method=self.method,
                        bounds=simplex_bounds,
                        constraints={'type':'eq', 'fun': lambda x: np.sum(x.reshape(control.shape[1], test.shape[0]), axis=0) - 1} )
            _status = res.status

        self.weights = res.x

        class Model:
            def __init__(self, weights):
                self.weights = weights.reshape(control.shape[1], test.shape[0])

            def predict(self, x):
                return x @ self.weights

        model = Model(self.weights)
        return model




class AugSynth(ImpactAnalyzer):
    """
    Implements the Augmented Synthetic Control Method (SCM) for causal inference.

    
    ----------
    :param inference: 
        Required. A n_units x n_time dataframe
    :param penalty: 
        Type of penalty used in the optimization problem. Options are entropy, l1, l2
    :param penalty_strength: 
        Optional[List[TimePeriod]] = None
    :param covariates: 
        Optional[List[TimePeriod]] = None
    :param alpha: 
        Optional[List[TimePeriod]] = None
    :param outcome_model: 
        Optional[List[TimePeriod]] = None
    :param full_model: 
        Optional[List[TimePeriod]] = None
    
    methods
    -------
    fit_data(panel_data):
        Take a PanelDataset and return X, y for the model 
    fit_model():
        Internal method to fit the model
    """

    def __init__(self,
        inference: Optional[Callable] = None,
        penalty: str = "entropy", 
        penalty_strength: float = 0.01,
        alpha: float = 0.05,
        outcome_model:Callable = Ridge,
        full_model = False 
        , model_args = {}
        , **opt_args ):
   
        self.inference = inference
        self.penalty = penalty
        self.penalty_strength = penalty_strength
        self.alpha = alpha 
        self.outcome_model = outcome_model(**model_args)
        #self.model_args = model_args
        self.full_model = full_model
        self.opt_args = opt_args
        self.method = self.opt_args.get("method", None)
        self.x0 = self.opt_args.get('x0_init', None)

    def fit_data(self, panel_data):
        self.panel_data = panel_data

    def fit_model(self):
        
        if self.full_model:
            # fit SCM 
            X_ctrl, X_test = self.panel_data.split_control_test_units(self.panel_data.treated_units, period='full')
            tunits = X_test.index.shape[0]
            ttimes = X_test.columns.shape[0]
            self.scm = SyntheticControlCVXPY(penalty=self.penalty, penalty_strength=self.penalty_strength, full_model=True)
            self.scm.run_analysis(self.panel_data)
            w_scm = self.scm.model.weights

            residuals = X_test.values.T.reshape(ttimes, tunits) -  self.scm.y_hat.reshape(ttimes, tunits)
            outcome_model_fitted = self.outcome_model.fit(X_ctrl.values.T, residuals)

        if not self.full_model:
            X_ctrl, X_test = self.panel_data.split_control_test_units(treated_units = self.panel_data.treated_units)
            tunits = X_test.index.shape[0]
            ttimes = X_test.columns.shape[0]

            # fit SCM 
            self.scm = SyntheticControlCVXPY(penalty=self.penalty, penalty_strength=self.penalty_strength)
            self.scm.run_analysis(self.panel_data)
            w_scm = self.scm.model.weights


            residuals = X_test.values.T.reshape(ttimes, tunits) -  self.scm.y_hat[:self.panel_data.treated_start_idxs[0]].reshape(ttimes, tunits)
            outcome_model_fitted = self.outcome_model.fit(X_ctrl.values.T, residuals)

        ttimes = self.panel_data.num_timepoints

        class Model:
            def __init__(self, scm_weights, outcome_model_fitted):
                self.scm_weights = scm_weights
                self.outcome_model_fitted = outcome_model_fitted
            def predict(self, X):
                return X @ self.scm_weights + self.outcome_model_fitted.predict(X).reshape(X.shape[0], tunits)


        model = Model(w_scm, outcome_model_fitted)

        return model



class SyntheticControlCVXPY(ImpactAnalyzer):
    """
    Implements the Synthetic Control Method (SCM) for causal inference
    using OSQP directly (bypasses CVXPY to avoid scipy 1.17 incompatibility).

    Parameters
    ----------
    inference : callable, optional
        Inference method to use.
    penalty : str
        Stored for API compatibility; not used in the OSQP solve.
    penalty_strength : float
        Stored for API compatibility; not used in the OSQP solve.
    alpha : float
        Controls type I error for inference.
    full_model : bool
        If True, SCM is fit on the full time series (used by AugSynth internally).
    donor_correlation_threshold : float
        Pre-filter donors whose pre-period correlation with the treated series
        is below this threshold. Default 0.0 means no filtering (backward
        compatible). Recommended for geo panels: 0.5–0.7.
    min_donors : int
        Minimum donors to keep after correlation filtering. If fewer than
        min_donors pass the threshold, the top min_donors by correlation are
        kept regardless. Prevents degenerate cases with strict thresholds.
    lambda_reg : float
        L2 regularisation added to the QP objective (lambda_reg * I added to P).
        Spreads weights across more donors. Default 0.0 means no regularisation.
        Recommended range for geo panels: 0.01–0.1.
    """

    def __init__(
        self,
        inference: Optional[Callable] = None,
        penalty: str = "entropy",
        penalty_strength: float = 0.01,
        alpha: float = 0.05,
        full_model: bool = False,
        donor_correlation_threshold: float = 0.0,
        min_donors: int = 5,
        lambda_reg: float = 0.0,
    ):
        self.penalty = penalty
        self.penalty_strength = penalty_strength
        self.inference = inference
        self.alpha = alpha
        self.full_model = full_model
        self.donor_correlation_threshold = donor_correlation_threshold
        self.min_donors = min_donors
        self.lambda_reg = lambda_reg

    def fit_data(self, panel_data):
        self.panel_data = panel_data

    def fit_model(self):
        import osqp
        import scipy.sparse as sp

        if self.full_model:
            control, test = self.panel_data.split_control_test_units(
                self.panel_data.treated_units, period='full')
        else:
            control, test = self.panel_data.split_control_test_units(
                treated_units=self.panel_data.treated_units)

        C = control.T.values.astype(float)  # (T, n_ctrl)
        Y = test.values.astype(float)        # (n_treated, T)
        n_ctrl = C.shape[1]
        n_treated = Y.shape[0]

        # ---- Donor correlation pre-filtering --------------------------------
        # Always compute correlation on the pre-period only.
        if self.full_model:
            start = self.panel_data.treated_start_idxs[0]
            C_pre = C[:start]
            y_ref = Y[:, :start].mean(axis=0)   # (T_pre,)
        else:
            C_pre = C                            # already pre-period
            y_ref = Y.mean(axis=0)              # (T_pre,)

        correlations = np.array([
            float(np.corrcoef(C_pre[:, j], y_ref)[0, 1])
            if np.std(C_pre[:, j]) > 1e-10
            else 0.0
            for j in range(n_ctrl)
        ])
        self._donor_correlations = correlations

        if self.donor_correlation_threshold > 0.0:
            keep_mask = correlations >= self.donor_correlation_threshold
            n_keep = int(keep_mask.sum())

            if n_keep < self.min_donors:
                n_below = n_keep  # count before fallback, used in warning
                top_idx = np.argsort(correlations)[::-1][:self.min_donors]
                keep_mask = np.zeros(len(correlations), dtype=bool)
                keep_mask[top_idx] = True
                n_keep = self.min_donors
                warnings.warn(
                    f"Only {n_below} donors passed correlation threshold "
                    f"{self.donor_correlation_threshold}. "
                    f"Keeping top {self.min_donors} donors by correlation.",
                    UserWarning,
                    stacklevel=2,
                )

            kept_indices = np.where(keep_mask)[0]
            n_filtered_out = n_ctrl - len(kept_indices)
            if n_filtered_out > 0:
                print(
                    f"[SCM] Correlation filter: kept {len(kept_indices)}/{n_ctrl} "
                    f"donors (threshold={self.donor_correlation_threshold}, "
                    f"top corr={correlations[kept_indices].max():.3f}, "
                    f"min corr={correlations[kept_indices].min():.3f})"
                )
            C_filtered = C[:, kept_indices]
        else:
            kept_indices = np.arange(n_ctrl)
            C_filtered = C

        self._kept_donor_indices = kept_indices
        self._n_donors_filtered = n_ctrl - len(kept_indices)

        # ---- Build OSQP QP --------------------------------------------------
        # QP: min ||C_filtered @ w_j - y_j||^2  s.t. sum(w_j)=1, w_j>=0
        # OSQP: min 0.5 w'Pw + q'w  s.t. l <= Aw <= u
        # P = 2*(C'C + lambda_reg*I),  q = -2*C'y_j
        # A = [1'; I],  l=[1;0...],  u=[1;inf...]
        n_donors = C_filtered.shape[1]
        CtC = C_filtered.T @ C_filtered
        if self.lambda_reg > 0.0:
            P = sp.csc_matrix(2.0 * (CtC + self.lambda_reg * np.eye(n_donors)))
        else:
            P = sp.csc_matrix(2.0 * CtC)
        self._lambda_reg_used = self.lambda_reg

        ones_row = sp.csc_matrix(np.ones((1, n_donors)))
        eye_donors = sp.eye(n_donors, format='csc')
        A_cstr = sp.vstack([ones_row, eye_donors], format='csc')
        l_cstr = np.concatenate([[1.0], np.zeros(n_donors)])
        u_cstr = np.concatenate([[1.0], np.full(n_donors, np.inf)])

        solver = osqp.OSQP()
        solver.setup(
            P, np.zeros(n_donors),
            A_cstr, l_cstr, u_cstr,
            verbose=False,
            eps_abs=1e-6,
            eps_rel=1e-6,
            max_iter=10000,
            polish=True,
        )

        # ---- Solve per treated unit, map back to full donor space -----------
        weights_filtered = np.zeros((n_donors, n_treated))
        for j in range(n_treated):
            y_j = Y[j]
            q_j = -2.0 * (C_filtered.T @ y_j)
            solver.update(q=q_j)
            result = solver.solve()
            w_j = result.x
            if w_j is None:
                w_j = np.full(n_donors, 1.0 / n_donors)
            w_j = np.clip(w_j, 0.0, None)
            w_sum = w_j.sum()
            if w_sum > 1e-12:
                w_j = w_j / w_sum
            else:
                w_j = np.full(n_donors, 1.0 / n_donors)
            weights_filtered[:, j] = w_j

        weights_full = np.zeros((n_ctrl, n_treated))
        weights_full[kept_indices, :] = weights_filtered
        self.weights = weights_full

        class Model:
            def __init__(self, weights):
                self.weights = weights  # (n_ctrl, n_treated)

            def predict(self, x):
                return x @ self.weights

        return Model(self.weights)

class AugSynthCVXPY(ImpactAnalyzer):
    """
    Implements the Augmented Synthetic Control Method for causal inference.
    Uses SyntheticControlCVXPY (OSQP-based) as the inner SCM solver.

    Parameters
    ----------
    inference : callable, optional
        Inference method to use.
    penalty : str
        Passed to inner SyntheticControlCVXPY (stored, not currently used in solve).
    penalty_strength : float
        Passed to inner SyntheticControlCVXPY (stored, not currently used in solve).
    alpha : float
        Controls type I error for inference.
    outcome_model : callable
        Sklearn-compatible regression class for the Ridge augmentation step.
        Default is Ridge. Use RidgeCV only if cross-validating alpha is desired.
    full_model : bool
        If True, SCM and Ridge are fit on the full time series.
    model_args : dict
        Kwargs passed to outcome_model constructor.
    donor_correlation_threshold : float
        Pre-filter donors by pre-period correlation with treated series.
        Passed through to SyntheticControlCVXPY. Default 0.0 (no filtering).
    min_donors : int
        Minimum donors to keep after correlation filtering. Default 5.
    lambda_reg : float
        L2 regularisation on SCM weights. Passed through to SyntheticControlCVXPY.
        Default 0.0 (no regularisation).
    """

    def __init__(self,
        inference: Optional[Callable] = None,
        penalty: str = "entropy",
        penalty_strength: float = 0.01,
        alpha: float = 0.05,
        outcome_model: Callable = Ridge,
        full_model: bool = False,
        model_args: dict = {},
        donor_correlation_threshold: float = 0.0,
        min_donors: int = 5,
        lambda_reg: float = 0.0,
        **opt_args,
    ):
        self.inference = inference
        self.penalty = penalty
        self.penalty_strength = penalty_strength
        self.alpha = alpha
        self.outcome_model = outcome_model(**model_args)
        self.full_model = full_model
        self.opt_args = opt_args
        self.method = self.opt_args.get("method", None)
        self.x0 = self.opt_args.get('x0_init', None)
        self.donor_correlation_threshold = donor_correlation_threshold
        self.min_donors = min_donors
        self.lambda_reg = lambda_reg

    def fit_data(self, panel_data):
        self.panel_data = panel_data

    def fit_model(self):
        scm_kwargs = dict(
            penalty=self.penalty,
            penalty_strength=self.penalty_strength,
            donor_correlation_threshold=self.donor_correlation_threshold,
            min_donors=self.min_donors,
            lambda_reg=self.lambda_reg,
        )

        if self.full_model:
            X_ctrl, X_test = self.panel_data.split_control_test_units(
                self.panel_data.treated_units, period='full')
            tunits = X_test.index.shape[0]
            ttimes = X_test.columns.shape[0]
            self.scm = SyntheticControlCVXPY(full_model=True, **scm_kwargs)
            self.scm.run_analysis(self.panel_data)
            w_scm = self.scm.model.weights
            residuals = (X_test.values.T.reshape(ttimes, tunits)
                         - self.scm.y_hat.reshape(ttimes, tunits))
            outcome_model_fitted = self.outcome_model.fit(X_ctrl.values.T, residuals)

        if not self.full_model:
            X_ctrl, X_test = self.panel_data.split_control_test_units(
                treated_units=self.panel_data.treated_units)
            tunits = X_test.index.shape[0]
            ttimes = X_test.columns.shape[0]
            self.scm = SyntheticControlCVXPY(full_model=False, **scm_kwargs)
            self.scm.run_analysis(self.panel_data)
            w_scm = self.scm.model.weights
            start = self.panel_data.treated_start_idxs[0]
            residuals = (X_test.values.T.reshape(ttimes, tunits)
                         - self.scm.y_hat[:start].reshape(ttimes, tunits))
            outcome_model_fitted = self.outcome_model.fit(X_ctrl.values.T, residuals)

        # Expose donor filtering metadata from the inner SCM
        self._donor_correlations = getattr(self.scm, '_donor_correlations', None)
        self._kept_donor_indices = getattr(self.scm, '_kept_donor_indices', None)
        self._n_donors_filtered = getattr(self.scm, '_n_donors_filtered', 0)

        ttimes = self.panel_data.num_timepoints

        class Model:
            def __init__(self, scm_weights, outcome_model_fitted):
                self.scm_weights = scm_weights
                self.outcome_model_fitted = outcome_model_fitted

            def predict(self, X):
                return (X @ self.scm_weights
                        + self.outcome_model_fitted.predict(X).reshape(X.shape[0], tunits))

        return Model(w_scm, outcome_model_fitted)