"""Audit invariants for AUGSYNTH-ASCM-IMPLEMENTATION-FIDELITY-AUDIT-001."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from panel_exp.methods.scm import AugSynthCVXPY, SyntheticControlCVXPY
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason


def _panel(n_ctrl: int = 10, seed: int = 0) -> PanelDataset:
    rng = np.random.default_rng(seed)
    control = [f"c{i}" for i in range(n_ctrl)]
    treated = ["t0"]
    n_periods = 20
    rows = {u: rng.normal(0, 1, n_periods) for u in control}
    rows["t0"] = rng.normal(0.2, 1.1, n_periods)
    wide = pd.DataFrame(rows).T
    return PanelDataset(
        wide,
        treated_units=treated,
        treated_periods=[TimePeriod(14, n_periods - 1)],
    )


@pytest.fixture(scope="module")
def cvxpy_available() -> None:
    reason = cvxpy_osqp_skip_reason()
    if reason:
        pytest.skip(reason)


class TestAugSynthAscmFidelityInvariants:
    def test_inner_scm_weights_simplex(self, cvxpy_available: None) -> None:
        pds = _panel()
        est = AugSynthCVXPY(inference=None, min_donors=3)
        est.fit_data(pds)
        model = est.fit_model()
        w = np.asarray(model.scm_weights, dtype=float).reshape(-1)
        assert np.all(w >= -1e-6)
        assert abs(w.sum() - 1.0) < 1e-4

    def test_outcome_model_is_ridge_by_default(self, cvxpy_available: None) -> None:
        est = AugSynthCVXPY(inference=None)
        assert est.outcome_model.__class__.__name__ == "Ridge"

    def test_penalty_params_stored_not_required_for_solve(
        self, cvxpy_available: None
    ) -> None:
        pds = _panel()
        scm = SyntheticControlCVXPY(penalty="entropy", penalty_strength=0.99)
        scm.fit_data(pds)
        fitted = scm.fit_model()
        w = np.asarray(fitted.weights, dtype=float).reshape(-1)
        assert abs(w.sum() - 1.0) < 1e-4
        assert scm.penalty == "entropy"

    def test_donor_filter_metadata_exposed(self, cvxpy_available: None) -> None:
        pds = _panel(n_ctrl=12)
        est = AugSynthCVXPY(
            inference=None,
            donor_correlation_threshold=0.3,
            min_donors=4,
        )
        est.fit_data(pds)
        est.fit_model()
        assert est._donor_correlations is not None
        assert est._kept_donor_indices is not None
        assert est._n_donors_filtered >= 0
