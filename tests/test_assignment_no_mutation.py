"""Caller-owned inputs must not be mutated by design assign paths."""

from __future__ import annotations

import copy

import pandas as pd
import pytest

from panel_exp.design.assign import (
    BalancedRandomization,
    CompleteRandomization,
    StratifiedRandomization,
    ThinningDesign,
    greedy_match_markets,
)
from tests.design_registry_helpers import make_geo_panel

GEO_SUPPORTED = (
    BalancedRandomization,
    CompleteRandomization,
    StratifiedRandomization,
    ThinningDesign,
    greedy_match_markets,
)


@pytest.mark.parametrize("cls", GEO_SUPPORTED)
def test_wide_data_unchanged(cls: type):
    panel = make_geo_panel(seed=10, n_units=10)
    before = panel.wide_data.copy()
    cls(treatment_probability=0.35, random_state=5).assign(
        panel_data=panel,
        n_test_grps=1,
        control_whitelist=["u0"],
        test_whitelist=["u1"],
    )
    pd.testing.assert_frame_equal(panel.wide_data, before)


@pytest.mark.parametrize("cls", GEO_SUPPORTED)
def test_constraint_lists_unchanged(cls: type):
    panel = make_geo_panel(seed=11, n_units=10)
    cw = ["u0"]
    tw = ["u1"]
    cb = ["u2"]
    tb = ["u3"]
    ctb = ["u4"]
    snap = (
        copy.deepcopy(cw),
        copy.deepcopy(tw),
        copy.deepcopy(cb),
        copy.deepcopy(tb),
        copy.deepcopy(ctb),
    )
    cls(treatment_probability=0.35, random_state=6).assign(
        panel_data=panel,
        n_test_grps=1,
        control_whitelist=cw,
        test_whitelist=tw,
        control_blacklist=cb,
        test_blacklist=tb,
        control_test_blacklist=ctb,
    )
    assert (cw, tw, cb, tb, ctb) == snap
