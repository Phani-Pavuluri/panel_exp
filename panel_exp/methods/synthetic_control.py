from ..panel_data import PanelDataset
import numpy as np
from scipy.optimize import minimize
from typing import Dict


def synthetic_control(
    panel: PanelDataset, treated_unit=None, treatment_aggregation_fun=None, penalty="entropy", penalty_strength=0.01
) -> Dict:
    """
    Solves the synthetic control problem for a treated unit using SLSQP
    """
    control, test = panel.split_control_test_units(treated_unit,treatment_aggregation_fun=treatment_aggregation_fun)
    # transform the data into numpy arrays
    # transpose so that each row is a time perid
    control = control.values.T
    test = test.values.reshape(-1)

    def balance_objective(x):
        # minimize the sum of squared errors
        # subject to an entropy penalty
        imbalance = np.sum(np.square(test - control @ x))
        if penalty == "entropy":
            imbalance += penalty_strength * -np.sum(x * np.log(x))
        elif penalty == "l1":
            imbalance += penalty_strength * np.sum(np.abs(x))
        elif penalty == "l2":
            imbalance += penalty_strength * np.sum(np.square(x))
        else:
            raise NotImplemented(f"Unknown penalty {penalty}")
        return imbalance

    x0 = np.ones(control.shape[1]) / control.shape[1]
    simplex_bounds = [(0, 1) for _ in range(control.shape[1])]
    simplex_constraints = [{"type": "eq", "fun": lambda x: np.sum(x) - 1}]
    res = minimize(
        balance_objective,
        x0,
        method="SLSQP",
        bounds=simplex_bounds,
        constraints=simplex_constraints,
    )
    weights = res.x
    # construct the synthetic control
    synthetic_control_full = panel.control_series(treated_unit).values.T @ weights
    synthetic_control_pre = control @ weights
    return {
        "weights": weights,
        "Y_0": synthetic_control_full,
        "Y_0_pre": synthetic_control_pre,
    }

def ridge_augsynth(
    panel: PanelDataset,
    treated_unit=None,
    treatment_aggregation_fun=None,
    penalty="entropy",
    penalty_strength=0.01,
    ridge_penalty=0.01,
    CV=False
) -> Dict:
    """
    Implementes ridge augmented synthetic control, following equation (13)
    of the Augmente Synthetic Control paper:
        w_aug_i = w_scm_i + (X_1 - X_0'w_scm)'(X_0'X_0 + ridge_penalty*I)^{-1}X_i
    """
    if CV:
        raise NotImplemented()
    synth_results = synthetic_control(
        panel,
        treated_unit=treated_unit,
        treatment_aggregation_fun=treatment_aggregation_fun,
        penalty=penalty,
        penalty_strength=penalty_strength,
    )
    X_ctrl, X_test =  panel.split_control_test_units(treated_unit,treatment_aggregation_fun=treatment_aggregation_fun)
    w_scm = synth_results['weights']
    residuals = (X_test.values.reshape(-1) - synth_results['Y_0_pre'].reshape(-1))[None, :]
    ridge_weights = residuals @ np.linalg.inv(X_ctrl.values.T @ X_ctrl.values + ridge_penalty * np.eye(X_ctrl.shape[1])) @ X_ctrl.values.T
    weights = w_scm.reshape(-1) + ridge_weights.reshape(-1)

    synthetic_control_full = panel.control_series(treated_unit).values.T @ weights
    synthetic_control_pre = X_ctrl.values.T @ weights
    return {
        "weights": weights,
        "Y_0": synthetic_control_full,
        "Y_0_pre": synthetic_control_pre,
    }
