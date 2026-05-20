"""

Methods: TBR, TBRRidge, TBRAutoSARIMAX
======================================

Implementations of Time-Based Regression

"""

from functools import partial
from typing import Callable, Optional
import numpy as np

from panel_exp.panel_data import PanelDataset
from panel_exp.impact import ImpactAnalyzer
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import RidgeCV
import pmdarima as pm
from scipy import stats
from statsmodels.tsa.statespace.sarimax import SARIMAX

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import warnings

from sklearn.decomposition import PCA
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_selection import VarianceThreshold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

@dataclass
class _ReducedExogState:
    kept_columns: List[int]
    reducer_type: str
    scaler: Optional[StandardScaler]
    pca: Optional[PCA]
    ridge: Optional[RidgeCV]
    synthetic_weights: Optional[np.ndarray]

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(-1, 1)

        X2 = X[:, self.kept_columns] if self.kept_columns else np.empty((X.shape[0], 0))
        if X2.size == 0:
            return X2

        if self.scaler is not None:
            X2 = self.scaler.transform(X2)

        if self.reducer_type == "pca":
            return self.pca.transform(X2)
        if self.reducer_type == "synthetic_ridge":
            return X2 @ self.synthetic_weights.reshape(-1, 1)
        return X2



class TBR(ImpactAnalyzer):

    """
    Implementation of TBR

    Paper: https://storage.googleapis.com/pub-tools-public-publication-data/pdf/45950.pdf

    Notes
    
    - Right not this assumes there is only one treated series that has been pre-aggregated.
    - It can handle multiple controls, if you use TBRRidge
    - This method does extrapolate
    - No Inference has been checked.
    
    Parameters
    ----------
    
    inference: 
        Inference method to use
    alpha: 
        alpha level for inference
    full_model: 
        If True, the model will be fit on the full data, if False, the model will be fit on the pre-treatment data
    
    Methods
    ------- 
    
    fit_data(panel):
        Take a PanelDataset and return X, y for the model
    fit_model():
        Internal method to fit the model.
    

    """
    def __init__(self
            , inference: Optional[Callable] = None
            , alpha: float = 0.05
            , full_model = False ):

        self.inference = inference
        self.alpha = alpha
        self.ppf = stats.norm.ppf(alpha / 2 + (1 - alpha))  # two-sided
        self.full_model = full_model
        

    def fit_data(self, panel: PanelDataset):
        """Take a PanelDataset and return X, y for the model

        :param panel: 
            (PanelDataset) PanelDataset object

        :returns: 
            np.arrays X, y for the model
        """
        self.panel_data = panel

        assert (
            len(self.panel_data.treated_units) == 1 
        ), "TBR requires treated units to be pre-aggregated. Try TBRRidge or aggregate treated units"
        assert (
            self.panel_data.num_control_units == 1
        ), "TBR requires control units to be pre-aggregated. Try TBRRidge or aggregate control units"

        if self.full_model:
            y = self.panel_data.treated_series(treated_units = self.panel_data.treated_units , period='full').values.T.flatten()
            X = self.panel_data.control_series(treated_units = self.panel_data.treated_units , period='full').values.T


        if not self.full_model:
            y = self.panel_data.treated_series(treated_units = self.panel_data.treated_units ).values.T.flatten()
            X = self.panel_data.control_series(treated_units = self.panel_data.treated_units ).values.T

        return X, y.flatten()

    def fit_model(self):
        """Internal method to fit the model. 

        
        :returns:
            object: returns fitted model
        """
        X, y = self.fit_data(self.panel_data)
        if self.full_model:
            y_pre = y
            X_pre = X

        if not self.full_model:
            y_pre = y[: self.panel_data.treated_start_idxs[0]]
            X_pre = X[: self.panel_data.treated_start_idxs[0]]

        model = LinearRegression().fit(X_pre, y_pre)

        return model


class TBRRidge(ImpactAnalyzer):
    """
    Modification of TBR that uses Ridge Regression. In this method, we don't pre-aggregate the control units. 

    Paper: https://storage.googleapis.com/pub-tools-public-publication-data/pdf/45950.pdf

    ----------
    
    :param inference: Inference method to use
    :param alpha: alpha level for inference
    :param full_model: If True, the model will be fit on the full data, if False, the model will be fit on the pre-treatment data
    
    Methods
    -------
    fit_data(panel):
        Take a PanelDataset and return X, y for the model
    fit_model():
        Internal method to fit the model.
    """
    def __init__(self, inference: Optional[Callable] = None, alpha: float = 0.05, full_model=False):
        self.inference = inference
        self.alpha = alpha
        self.ppf = stats.norm.ppf(self.alpha / 2 + (1 - self.alpha))  # two-sided
        self.full_model = full_model

    def fit_data(self, panel: PanelDataset):
        """Take a PanelDataset and return X, y for the model"""
        self.panel_data = panel
        if self.full_model:
            y = self.panel_data.treated_series(
                treated_units=self.panel_data.treated_units,
                period='full'
            ).values.T.flatten()
            X = self.panel_data.control_series(
                treated_units=self.panel_data.treated_units,
                period='full'
            ).values.T
        else:
            y = self.panel_data.treated_series(
                self.panel_data.treated_units
            ).values.T.flatten()
            X = self.panel_data.control_series(
                self.panel_data.treated_units
            ).values.T

        return X, np.asarray(y).flatten()

    def fit_model(self):
        """Fit Ridge regression with pre-period mean normalisation.

        Normalisation removes scale mismatch between the treated aggregate
        and individual control units, preventing Ridge's L2 penalty from
        creating a systematic intercept bias.

        The returned NormalisedModel wraps predict() to apply the same
        normalisation to inputs and inverse-transform outputs back to
        original scale, so ImpactAnalyzer.run_analysis() requires no
        changes.
        """
        X, y = self.fit_data(self.panel_data)

        if self.full_model:
            y_pre = y
            X_pre = X
        else:
            start = self.panel_data.treated_start_idxs[0]
            y_pre = y[:start]
            X_pre = X[:start]

        # Compute pre-period means as normalisation constants.
        # Add epsilon to avoid division by zero for constant series.
        y_mean = float(np.mean(y_pre)) if y_pre.size > 0 else 1.0
        if abs(y_mean) < 1e-12:
            y_mean = 1.0
        X_mean = np.mean(X_pre, axis=0) if X_pre.size > 0 else np.ones(X_pre.shape[1])
        X_mean = np.where(np.abs(X_mean) < 1e-12, 1.0, X_mean)

        # Normalise to pre-period mean = 1 for both series
        y_pre_norm = y_pre / y_mean
        X_pre_norm = X_pre / X_mean

        ridge = RidgeCV(alphas=[1e-3, 1e-2, 1e-1, 1]).fit(X_pre_norm, y_pre_norm)

        # Store normalisation constants on self for diagnostics
        self._normalisation_y_mean = y_mean
        self._normalisation_X_mean = X_mean.copy()
        self._normalisation_applied = True

        X_mean_captured = X_mean.copy()
        y_mean_captured = y_mean

        class NormalisedModel:
            """Wraps RidgeCV to normalise inputs and inverse-transform outputs.

            Exposes the same interface as a fitted sklearn estimator so
            ImpactAnalyzer.run_analysis() works without modification:
              - predict(X) -> original-scale predictions
              - coef_ -> Ridge coefficients (normalised scale)
              - alpha_ -> selected Ridge penalty
              - intercept_ -> Ridge intercept (normalised scale)
            """
            def __init__(self, ridge, X_mean, y_mean):
                self.ridge = ridge
                self.X_mean = X_mean
                self.y_mean = y_mean
                self.coef_ = ridge.coef_
                self.alpha_ = ridge.alpha_
                self.intercept_ = ridge.intercept_

            def predict(self, X):
                X_arr = np.asarray(X, dtype=float)
                # Apply same normalisation as training
                X_norm = X_arr / (self.X_mean + 1e-12)
                y_hat_norm = self.ridge.predict(X_norm)
                # Inverse transform back to original scale
                return y_hat_norm * self.y_mean

        return NormalisedModel(ridge, X_mean_captured, y_mean_captured)



class SARIMAXWrapper:
    """
    Wrapper to make SARIMAX compatible with scikit-learn interface
    Required for inference methods (k-fold, jackknife, etc.)
    """
    def __init__(
        self,
        sarimax_result,
        order,
        seasonal_order,
        exog_state: Optional[_ReducedExogState] = None,
        ridge_fallback=None,
        used_fallback: bool = False,
        fit_metadata: Optional[Dict[str, Any]] = None,
    ):
        self.result = sarimax_result
        self.order = order
        self.seasonal_order = seasonal_order
        self.params = None if sarimax_result is None else sarimax_result.params
        self.exog_state = exog_state
        self.ridge_fallback = ridge_fallback
        self.used_fallback = used_fallback
        self.fit_metadata = fit_metadata or {}

    def _safe_array(self, X):
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        return X

    def predict(self, X):
        X = self._safe_array(X)

        if self.used_fallback:
            preds = self.ridge_fallback.predict(X)
            return preds.flatten() if hasattr(preds, "flatten") else preds

        X_red = self.exog_state.transform(X) if self.exog_state is not None else X

        n_samples = X_red.shape[0]
        n_pre = self.result.model.nobs

        if n_samples > n_pre:
            # In-sample: predict 0..n_pre-1 (no exog needed)
            pred_in = self.result.predict(start=0, end=n_pre - 1)
            pred_in_arr = pred_in.values if hasattr(pred_in, "values") else np.asarray(pred_in)
            # Out-of-sample: use get_forecast (proper OOS API) with exog for post period
            exog_oos = X_red[n_pre:]
            n_oos = exog_oos.shape[0]
            if n_oos > 0:
                fc = self.result.get_forecast(
                    steps=n_oos,
                    exog=exog_oos if exog_oos.shape[1] > 0 else None,
                )
                pred_oos = fc.predicted_mean
                pred_oos_arr = pred_oos.values if hasattr(pred_oos, "values") else np.asarray(pred_oos)
                predictions = np.concatenate([pred_in_arr, pred_oos_arr])
            else:
                predictions = pred_in_arr
        elif n_samples < n_pre:
            predictions = self.result.predict(
                start=n_pre,
                end=n_pre + n_samples - 1,
                exog=X_red if X_red.shape[1] > 0 else None,
            )
        else:
            predictions = self.result.predict(
                start=0,
                end=n_samples - 1,
                exog=None,
            )

        return predictions.values if hasattr(predictions, "values") else predictions


class TBRAutoSARIMAX(ImpactAnalyzer):
    """
    TBR with automatic SARIMAX - COMPATIBLE WITH INFERENCE!

    Works with k-fold, jackknife, conformal, and other inference methods.
    Exogenous controls are screened and reduced before SARIMAX fitting.
    """

    def __init__(
        self,
        seasonal: bool = False,
        seasonal_period: int = 7,
        max_p: int = 1,
        max_q: int = 1,
        max_P: int = 0,
        max_Q: int = 0,
        max_d: int = 1,
        max_D: int = 0,
        information_criterion: str = "bic",
        stepwise: bool = True,
        trace: bool = False,
        inference: Optional[Callable] = None,
        alpha: float = 0.1,
        full_model: bool = False,
        max_controls: int = 20,
        exog_reduction: str = "synthetic_ridge",   # {"pca", "synthetic_ridge", "none"}
        pca_n_components: int = 5,
        ridge_alphas: Optional[np.ndarray] = None,
        corr_screen: bool = True,
        collinearity_threshold: float = 0.95,
        fallback_to_ridge: bool = True,
        retry_without_seasonality: bool = True,
        retry_with_fewer_factors: bool = True,
        suppress_future_warnings: bool = True,
        sarimax_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self.seasonal = seasonal
        self.seasonal_period = seasonal_period
        self.max_p = max_p
        self.max_q = max_q
        self.max_P = max_P
        self.max_Q = max_Q
        self.max_d = max_d
        self.max_D = max_D
        self.information_criterion = information_criterion
        self.stepwise = stepwise
        self.n_jobs = 1 if stepwise else kwargs.get("n_jobs", 1)
        self.trace = trace
        self.inference = inference
        self.alpha = alpha
        self.full_model = full_model
        self.ppf = stats.norm.ppf(alpha / 2 + (1 - alpha))

        self.max_controls = max_controls
        self.exog_reduction = exog_reduction
        self.pca_n_components = pca_n_components
        self.ridge_alphas = ridge_alphas if ridge_alphas is not None else np.logspace(-3, 3, 25)
        self.corr_screen = corr_screen
        self.collinearity_threshold = collinearity_threshold
        self.fallback_to_ridge = fallback_to_ridge
        self.retry_without_seasonality = retry_without_seasonality
        self.retry_with_fewer_factors = retry_with_fewer_factors
        self.suppress_future_warnings = suppress_future_warnings
        self.sarimax_kwargs = sarimax_kwargs or {}

        self.best_order = None
        self.best_seasonal_order = None
        self.auto_model = None

        self.model_ = None
        self.results_ = None
        self.auto_arima_model_ = None
        self.exog_state_ = None
        self.ridge_fallback_ = None
        self.pre_period_mean_ = None
        self.used_fallback_ = False
        self.fit_metadata_ = {}

    def _safe_array(self, x: np.ndarray) -> np.ndarray:
        arr = np.asarray(x, dtype=float)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        return arr

    def _drop_constant_columns(self, X: np.ndarray) -> Tuple[np.ndarray, List[int]]:
        if X.shape[1] == 0:
            return X, []
        selector = VarianceThreshold(threshold=0.0)
        X2 = selector.fit_transform(X)
        kept = np.where(selector.get_support())[0].tolist()
        return X2, kept

    def _screen_by_correlation(self, y: np.ndarray, X: np.ndarray) -> List[int]:
        if X.shape[1] <= self.max_controls:
            return list(range(X.shape[1]))

        scores = []
        y = np.asarray(y, dtype=float).reshape(-1)
        y_std = np.std(y)

        for j in range(X.shape[1]):
            xj = X[:, j]
            x_std = np.std(xj)
            if y_std == 0 or x_std == 0:
                corr = 0.0
            else:
                corr = np.corrcoef(y, xj)[0, 1]
                if not np.isfinite(corr):
                    corr = 0.0
            scores.append((j, abs(corr)))

        scores.sort(key=lambda t: t[1], reverse=True)
        return [j for j, _ in scores[: self.max_controls]]

    def _drop_highly_collinear(self, X: np.ndarray, columns: List[int]) -> List[int]:
        if X.shape[1] <= 1:
            return columns

        corr = np.corrcoef(X, rowvar=False)
        keep_mask = np.ones(X.shape[1], dtype=bool)

        for i in range(X.shape[1]):
            if not keep_mask[i]:
                continue
            for j in range(i + 1, X.shape[1]):
                if keep_mask[j] and np.isfinite(corr[i, j]) and abs(corr[i, j]) >= self.collinearity_threshold:
                    keep_mask[j] = False

        kept_local = np.where(keep_mask)[0].tolist()
        return [columns[i] for i in kept_local]

    def _reduce_exog(self, y_pre: np.ndarray, X_pre: np.ndarray) -> Tuple[np.ndarray, _ReducedExogState]:
        X_pre = self._safe_array(X_pre)
        y_pre = np.asarray(y_pre, dtype=float).reshape(-1)

        if X_pre.shape[1] == 0:
            state = _ReducedExogState([], "none", None, None, None, None)
            return X_pre, state

        X_nonconst, kept0 = self._drop_constant_columns(X_pre)
        if X_nonconst.shape[1] == 0:
            state = _ReducedExogState([], "none", None, None, None, None)
            return np.empty((X_pre.shape[0], 0)), state

        selected_local = self._screen_by_correlation(y_pre, X_nonconst) if self.corr_screen else list(range(X_nonconst.shape[1]))
        kept1 = [kept0[j] for j in selected_local]
        X_sel = X_pre[:, kept1]

        if X_sel.shape[1] > 1:
            kept2 = self._drop_highly_collinear(X_sel, kept1)
            X_sel = X_pre[:, kept2]
        else:
            kept2 = kept1

        if X_sel.shape[1] == 0:
            state = _ReducedExogState([], "none", None, None, None, None)
            return np.empty((X_pre.shape[0], 0)), state

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_sel)

        if self.exog_reduction == "synthetic_ridge":
            ridge = RidgeCV(alphas=self.ridge_alphas)
            ridge.fit(X_scaled, y_pre)
            w = ridge.coef_.reshape(-1)
            if not np.any(np.isfinite(w)):
                w = np.zeros(X_scaled.shape[1])
            X_red = X_scaled @ w.reshape(-1, 1)
            state = _ReducedExogState(
                kept_columns=kept2,
                reducer_type="synthetic_ridge",
                scaler=scaler,
                pca=None,
                ridge=ridge,
                synthetic_weights=w,
            )
            return X_red, state

        if self.exog_reduction == "none":
            state = _ReducedExogState(
                kept_columns=kept2,
                reducer_type="none",
                scaler=scaler,
                pca=None,
                ridge=None,
                synthetic_weights=None,
            )
            return X_scaled, state

        n_comp = min(self.pca_n_components, X_scaled.shape[0], X_scaled.shape[1])
        n_comp = max(1, n_comp)
        pca = PCA(n_components=n_comp)
        X_red = pca.fit_transform(X_scaled)
        state = _ReducedExogState(
            kept_columns=kept2,
            reducer_type="pca",
            scaler=scaler,
            pca=pca,
            ridge=None,
            synthetic_weights=None,
        )
        return X_red, state

    def _fit_ridge_fallback(self, y_pre: np.ndarray, X_pre: np.ndarray) -> None:
        X_pre = self._safe_array(X_pre)
        y_pre = np.asarray(y_pre, dtype=float).reshape(-1)

        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("ridge", RidgeCV(alphas=self.ridge_alphas)),
        ])
        pipe.fit(X_pre, y_pre)

        self.ridge_fallback_ = pipe
        self.used_fallback_ = True
        self.fit_metadata_["fallback_reason"] = "sarimax_nonconvergence"

    def _sarimax_converged(self, results) -> bool:
        if results is None:
            return False
        mle_retvals = getattr(results, "mle_retvals", None)
        if isinstance(mle_retvals, dict):
            return bool(mle_retvals.get("converged", False))
        return bool(getattr(results, "converged", False))

    def _candidate_orders(
        self,
        base_order: Tuple[int, int, int],
        base_seasonal_order: Tuple[int, int, int, int],
    ) -> List[Tuple[Tuple[int, int, int], Tuple[int, int, int, int], bool]]:
        candidates = [(base_order, base_seasonal_order, self.seasonal)]

        if self.retry_without_seasonality and self.seasonal:
            candidates.append((base_order, (0, 0, 0, 0), False))

        simple_order = (min(base_order[0], 1), min(base_order[1], 1), min(base_order[2], 1))
        candidates.append((simple_order, (0, 0, 0, 0), False))

        deduped = []
        seen = set()
        for cand in candidates:
            key = (cand[0], cand[1], cand[2])
            if key not in seen:
                seen.add(key)
                deduped.append(cand)
        return deduped

    def fit_data(self, panel: PanelDataset):
        """Extract data from PanelDataset"""
        self.panel_data = panel

        period = 'full' if self.full_model else None
        kw = dict(treated_units=panel.treated_units)
        if period is not None:
            kw['period'] = period

        y = panel.treated_series(**kw).values.T
        if y.ndim > 1:
            y = y.sum(axis=1)
            if self.trace:
                print(f"Multiple treated units detected, aggregating to a single treated series over {y.shape[0]} periods")
        else:
            y = y.flatten()

        X = panel.control_series(**kw).values.T
        return X, y

    def fit_model(self):
        """
        Automatically find best SARIMAX and return wrapped model
        """
        X, y = self.fit_data(self.panel_data)
        X = self._safe_array(X)
        y = np.asarray(y, dtype=float).reshape(-1)

        if self.full_model:
            y_pre = y
            X_pre = X
        else:
            treatment_idx = self.panel_data.treated_start_idxs[0]
            y_pre = y[:treatment_idx]
            X_pre = X[:treatment_idx]

        y_pre = np.asarray(y_pre, dtype=float).reshape(-1)
        X_pre = self._safe_array(X_pre)

        self.pre_period_mean_ = float(np.mean(y_pre))

        if self.trace:
            print("=" * 70)
            print("AUTOMATIC ARIMA PARAMETER SEARCH")
            print("=" * 70)
            print(f"Pre-treatment periods: {len(y_pre)}")
            print(f"Raw control variables: {X_pre.shape[1]}")
            print(f"Seasonal period: {self.seasonal_period}")
            print(f"Exog reduction: {self.exog_reduction}")
            print("-" * 70)

        X_pre_red, self.exog_state_ = self._reduce_exog(y_pre, X_pre)

        self.auto_arima_model_ = pm.auto_arima(
            y=y_pre,
            X=X_pre_red if X_pre_red.shape[1] > 0 else None,
            seasonal=self.seasonal,
            m=self.seasonal_period if self.seasonal else 1,
            start_p=0,
            start_q=0,
            max_p=self.max_p,
            max_q=self.max_q,
            max_d=self.max_d,
            start_P=0,
            start_Q=0,
            max_P=self.max_P,
            max_Q=self.max_Q,
            max_D=self.max_D,
            information_criterion=self.information_criterion,
            stepwise=self.stepwise,
            n_jobs=self.n_jobs,
            error_action="ignore",
            suppress_warnings=True,
            trace=self.trace,
        )
        self.auto_model = self.auto_arima_model_

        order = self.auto_arima_model_.order
        seasonal_order = self.auto_arima_model_.seasonal_order
        self.best_order = order
        self.best_seasonal_order = seasonal_order

        if self.trace:
            print("=" * 70)
            print("BEST MODEL FOUND:")
            print(f"  ARIMA{order} x SARIMA{seasonal_order}")
            print(f"  AIC: {self.auto_arima_model_.aic():.2f}")
            print(f"  BIC: {self.auto_arima_model_.bic():.2f}")
            print(f"  Reduced control dimensions: {X_pre_red.shape[1]}")
            print("=" * 70)

        candidate_specs = self._candidate_orders(order, seasonal_order)

        exog_candidates = [(X_pre_red, "full_factors")]
        if self.retry_with_fewer_factors and self.exog_reduction == "pca" and X_pre_red.shape[1] > 2:
            smaller_dim = max(1, min(2, X_pre_red.shape[1] - 1))
            exog_candidates = [(X_pre_red[:, :smaller_dim], "reduced_factors"), (X_pre_red, "full_factors")]

        selected_results = None
        selected_model = None
        selected_order = None
        selected_seasonal = None
        selected_exog = None
        selected_exog_label = None

        for X_pre_candidate, exog_label in exog_candidates:
            for order_candidate, seasonal_candidate, _ in candidate_specs:
                try:
                    candidate_model = SARIMAX(
                        endog=y_pre,
                        exog=X_pre_candidate if X_pre_candidate.shape[1] > 0 else None,
                        order=order_candidate,
                        seasonal_order=seasonal_candidate,
                        trend="c",
                        enforce_stationarity=False,
                        enforce_invertibility=False,
                        **self.sarimax_kwargs,
                    )

                    with warnings.catch_warnings():
                        if self.suppress_future_warnings:
                            warnings.filterwarnings("ignore", category=FutureWarning)
                        warnings.filterwarnings("ignore", category=ConvergenceWarning)
                        warnings.filterwarnings("ignore", category=UserWarning, message="stepwise model cannot be fit in parallel.*")
                        candidate_results = candidate_model.fit(disp=False)

                    if self._sarimax_converged(candidate_results):
                        pred_pre = candidate_results.predict(
                            start=0,
                            end=len(y_pre) - 1,
                            exog=None,
                        )
                        pred_pre = pred_pre.values if hasattr(pred_pre, "values") else np.asarray(pred_pre)
                        pred_pre = np.asarray(pred_pre, dtype=float).reshape(-1)

                        pre_mean = float(np.mean(y_pre))
                        pred_pre_mean = float(np.mean(pred_pre))
                        pre_rmse = float(np.sqrt(np.mean((y_pre - pred_pre) ** 2)))
                        rmse_pct = pre_rmse / max(abs(pre_mean), 1e-8)
                        mean_ratio = pred_pre_mean / max(abs(pre_mean), 1e-8)

                        # Reject clearly misspecified level fits: this commonly happens when
                        # reduced/standardized exog + SARIMAX dynamics converge numerically but
                        # still fail to recover the treated-series scale.
                        if (mean_ratio < 0.5 or mean_ratio > 1.5 or rmse_pct > 0.15):
                            if self.trace:
                                print(
                                    "Rejecting converged SARIMAX candidate due to poor pre-fit: "
                                    f"pred_pre_mean={pred_pre_mean:.2f}, pre_mean={pre_mean:.2f}, "
                                    f"mean_ratio={mean_ratio:.3f}, pre_rmse={pre_rmse:.2f}, rmse_pct={rmse_pct:.3f}"
                                )
                            continue

                        selected_model = candidate_model
                        selected_results = candidate_results
                        selected_order = order_candidate
                        selected_seasonal = seasonal_candidate
                        selected_exog = X_pre_candidate
                        selected_exog_label = exog_label
                        self.fit_metadata_["pred_pre_mean"] = pred_pre_mean
                        self.fit_metadata_["pre_mean"] = pre_mean
                        self.fit_metadata_["pre_rmse"] = pre_rmse
                        self.fit_metadata_["pre_rmse_pct"] = rmse_pct
                        break
                except Exception as exc:
                    if self.trace:
                        print(f"SARIMAX retry failed for order={order_candidate}, seasonal={seasonal_candidate}: {exc}")
                    continue
            if selected_results is not None:
                break

        if selected_results is None:
            if self.fallback_to_ridge:
                self._fit_ridge_fallback(y_pre, X_pre)
                self.best_order = None
                self.best_seasonal_order = None
                self.model_ = None
                self.results_ = None
                self.fit_metadata_.update({
                    "used_fallback": self.used_fallback_,
                    "exog_reduction": None if self.exog_state_ is None else self.exog_state_.reducer_type,
                    "reduced_exog_dim": int(X_pre_red.shape[1]),
                    "sarimax_converged": False,
                    "exog_dim_raw": int(X_pre.shape[1]),
                    "exog_dim_reduced": int(X_pre_red.shape[1]),
                    "pred_pre_mean": None,
                    "pre_mean": float(np.mean(y_pre)),
                    "pre_rmse": None,
                    "pre_rmse_pct": None,
                })
                return SARIMAXWrapper(
                    sarimax_result=None,
                    order=None,
                    seasonal_order=None,
                    exog_state=self.exog_state_,
                    ridge_fallback=self.ridge_fallback_,
                    used_fallback=True,
                    fit_metadata=self.fit_metadata_.copy(),
                )
            raise RuntimeError("SARIMAX failed to converge for all retry candidates.")

        self.model_ = selected_model
        self.results_ = selected_results
        self.used_fallback_ = False
        self.best_order = selected_order
        self.best_seasonal_order = selected_seasonal
        self.fit_metadata_.update({
            "order": selected_order,
            "seasonal_order": selected_seasonal,
            "used_fallback": self.used_fallback_,
            "exog_reduction": None if self.exog_state_ is None else self.exog_state_.reducer_type,
            "reduced_exog_dim": int(selected_exog.shape[1]),
            "sarimax_converged": self._sarimax_converged(self.results_),
            "exog_dim_raw": int(X_pre.shape[1]),
            "exog_dim_reduced": int(selected_exog.shape[1]),
            "selected_exog_variant": selected_exog_label,
            "pred_pre_mean": self.fit_metadata_.get("pred_pre_mean"),
            "pre_mean": self.fit_metadata_.get("pre_mean", float(np.mean(y_pre))),
            "pre_rmse": self.fit_metadata_.get("pre_rmse"),
            "pre_rmse_pct": self.fit_metadata_.get("pre_rmse_pct"),
        })

        return SARIMAXWrapper(
            self.results_,
            self.best_order,
            self.best_seasonal_order,
            exog_state=self.exog_state_,
            ridge_fallback=self.ridge_fallback_,
            used_fallback=self.used_fallback_,
            fit_metadata=self.fit_metadata_.copy(),
        )

    def predict_counterfactual(self, X_post, return_intervals: bool = False):
        X_post = self._safe_array(X_post)

        if self.used_fallback_:
            preds = self.ridge_fallback_.predict(X_post)
            if return_intervals:
                return preds, None
            return preds

        X_post_red = self.exog_state_.transform(X_post) if self.exog_state_ is not None else X_post
        pred = self.results_.get_forecast(
            steps=X_post_red.shape[0],
            exog=X_post_red if X_post_red.shape[1] > 0 else None,
        )

        predicted_mean = pred.predicted_mean
        if return_intervals:
            return predicted_mean, pred.conf_int()
        return predicted_mean

    def get_model_summary(self):
        """Print detailed model summary"""
        if self.auto_model is None:
            print("Model not fitted yet. Run fit_model() first.")
            return

        print("\n" + "=" * 70)
        print("MODEL PARAMETERS")
        print("=" * 70)

        if self.used_fallback_:
            print("Fell back to RidgeCV because SARIMAX failed to converge.")
            print(f"Exog reduction: {None if self.exog_state_ is None else self.exog_state_.reducer_type}")
            print(f"Reduced exog dim: {self.fit_metadata_.get('reduced_exog_dim')}")
            print("=" * 70)
            return

        p, d, q = self.best_order
        P, D, Q, s = self.best_seasonal_order

        print(f"ARIMA({p},{d},{q}) x ({P},{D},{Q})[{s}]")
        print(f"\n  p={p}: AR lags (uses {p} past values)")
        print(f"  d={d}: Differencing ({d}x differenced)")
        print(f"  q={q}: MA lags (uses {q} past errors)")
        print(f"  P={P}: Seasonal AR lags")
        print(f"  D={D}: Seasonal differencing")
        print(f"  Q={Q}: Seasonal MA lags")
        print(f"  s={s}: Seasonal period")
        print(f"  used_fallback: {self.used_fallback_}")
        print(f"  exog_reduction: {None if self.exog_state_ is None else self.exog_state_.reducer_type}")
        print(f"  reduced_exog_dim: {self.fit_metadata_.get('reduced_exog_dim')}")
        print(f"  sarimax_converged: {self._sarimax_converged(self.results_)}")
        print(f"  pre_mean: {self.fit_metadata_.get('pre_mean')}")
        print(f"  pred_pre_mean: {self.fit_metadata_.get('pred_pre_mean')}")
        print(f"  pre_rmse: {self.fit_metadata_.get('pre_rmse')}")
        print(f"  pre_rmse_pct: {self.fit_metadata_.get('pre_rmse_pct')}")
        print("=" * 70)