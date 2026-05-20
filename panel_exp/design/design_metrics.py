import numpy as np

def imbalance(panel, metric="l2", period="full") -> float:
    """
    Calculate the imbalance of the proposed design.
    Options are:
        "l2" for mean squared error
        "l1" for mean absolute error
        "l_inf" for the L_infinity norm
        "rmse" for root mean squared error
        "mape" for mean absolute percentage error
        "smape" for symmetric mean absolute percentage error
        "wmae" for weighted mean absolute error
        "cosine" for cosine similarity distance
        "hellinger" for Hellinger distance
        "variance_ratio" for variance ratio
    """
    control_df, test_df = panel.split_control_test_units(
        treated_units=panel.treated_units, period=period
    )
    control_mean = control_df.mean(0)
    test_mean = test_df.mean(0)

    if metric == "l2":
        return np.mean(np.square(control_mean - test_mean))
    elif metric == "l1":
        return np.mean(np.abs(control_mean - test_mean))
    elif metric == "l_inf":
        return np.max(np.abs(control_mean - test_mean))
    elif metric == "rmse":
        return np.sqrt(np.mean(np.square(control_mean - test_mean)))
    elif metric == "mape":
        return np.mean(np.abs((control_mean - test_mean) / control_mean)) * 100
    elif metric == "smape":
        return np.mean(2 * np.abs(control_mean - test_mean) / (np.abs(control_mean) + np.abs(test_mean))) * 100
    elif metric == "wmae":
        weights = np.abs(control_mean)  # Example: using absolute values of control_mean as weights
        return np.sum(weights * np.abs(control_mean - test_mean)) / np.sum(weights)
    elif metric == "cosine":
        dot_product = np.dot(control_mean, test_mean)
        norm_control = np.linalg.norm(control_mean)
        norm_test = np.linalg.norm(test_mean)
        return 1 - (dot_product / (norm_control * norm_test))
    elif metric == "hellinger":
        control_mean = np.clip(control_mean, 1e-10, None)
        test_mean = np.clip(test_mean, 1e-10, None)
        return np.sqrt(np.sum((np.sqrt(control_mean) - np.sqrt(test_mean))**2)) / np.sqrt(2)
    elif metric == "variance_ratio":
        control_var = np.var(control_df, axis=0)
        test_var = np.var(test_df, axis=0)
        return np.mean(control_var / test_var)
    else:
        raise NotImplementedError(f"{metric} is not an implemented imbalance metric")

