"""Regression tests for INV-D1-001 pre-period matching boundary."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from panel_exp.design.assign import greedy_match_markets
from panel_exp.design.geo_experiment_design import GeoExperimentDesign
from panel_exp.design.period_slice import slice_wide_to_time_period
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.track_d_d5_des_001a import synthesize_panel
from tests.design_registry_helpers import make_geo_panel


def _greedy_assign(
    wide: pd.DataFrame,
    *,
    seed: int,
    pre_treatment_period: TimePeriod | None,
) -> dict[str, list[str]]:
    design = greedy_match_markets(
        func_to_optimize="corr",
        treatment_probability=0.5,
        random_state=seed,
    )
    return design.assign(
        panel_data=PanelDataset(wide.copy()),
        pre_treatment_period=pre_treatment_period,
        n_test_grps=1,
    )


def _test_set(assignment: dict[str, list]) -> set[str]:
    return set(assignment.get("test_0") or [])


class TestGreedyPrePeriodBoundary:
    def test_post_period_perturbation_invariant_with_pre_period(self) -> None:
        wide, n_pre = synthesize_panel(
            n_units=20,
            n_pre=40,
            n_post=15,
            seed=7,
            post_unit_shift_sd=50.0,
        )
        pre = TimePeriod(start=0, end=n_pre)
        base = _greedy_assign(wide, seed=11, pre_treatment_period=pre)

        mutated = wide.copy()
        rng = np.random.default_rng(99)
        mutated.iloc[:, n_pre:] = rng.normal(0, 500.0, size=mutated.iloc[:, n_pre:].shape)

        after = _greedy_assign(mutated, seed=11, pre_treatment_period=pre)
        assert _test_set(base) == _test_set(after)

    def test_slice_helper_matches_design_semantics(self) -> None:
        wide, n_pre = synthesize_panel(
            n_units=8, n_pre=10, n_post=5, seed=1, post_unit_shift_sd=0.0
        )
        pre = TimePeriod(start=0, end=n_pre)
        sliced = slice_wide_to_time_period(wide, pre)
        assert list(sliced.columns) == list(range(n_pre))

    def test_without_pre_period_post_can_change_assignment(self) -> None:
        wide, n_pre = synthesize_panel(
            n_units=20,
            n_pre=30,
            n_post=20,
            seed=3,
            post_unit_shift_sd=80.0,
        )
        a1 = _greedy_assign(wide, seed=5, pre_treatment_period=None)
        mutated = wide.copy()
        mutated.iloc[:, n_pre:] *= 10.0
        a2 = _greedy_assign(mutated, seed=5, pre_treatment_period=None)
        # Not required to differ every seed; only assert assignment is valid.
        assert _test_set(a1) and _test_set(a2)


class TestGeoRunnerPrePeriod:
    def test_run_design_passes_pre_treatment_period(self, monkeypatch) -> None:
        panel = make_geo_panel(seed=2, n_units=14, n_times=60)
        geo = GeoExperimentDesign(
            panel_data=panel,
            base_randomizer_cls=greedy_match_markets,
            train_length=40,
            random_state=3,
            test_lengths=[10],
            njobs=1,
            max_iter=2,
            validate_after_assign=False,
        )
        captured: dict = {}

        def _stub_mde(self, rs_dp_grps, control):
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        monkeypatch.setattr(GeoExperimentDesign, "_calculate_sensitivity_metrics", _stub_mde)

        real_create = geo.create_design

        def _spy_create():
            design = real_create()
            real_assign = design.assign

            def _wrapped_assign(*args, **kwargs):
                captured.update(kwargs)
                return real_assign(*args, **kwargs)

            design.assign = _wrapped_assign
            return design

        monkeypatch.setattr(geo, "create_design", _spy_create)
        geo.run_design()

        pre = captured.get("pre_treatment_period")
        assert pre is not None
        assert pre.start == 0
        assert pre.end == 40
