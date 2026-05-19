"""Seeded assignment reproducibility for geo-supported designs."""

from __future__ import annotations

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
    ("balanced", BalancedRandomization),
    ("complete", CompleteRandomization),
    ("stratified", StratifiedRandomization),
    ("thinning", ThinningDesign),
    ("greedy", greedy_match_markets),
)


@pytest.mark.parametrize("label,cls", GEO_SUPPORTED)
def test_same_seed_identical_assignment(label: str, cls: type):
    panel = make_geo_panel(seed=42, n_units=14)
    kwargs = dict(panel_data=panel, n_test_grps=1)
    a1 = cls(treatment_probability=0.4, random_state=99).assign(**kwargs)
    a2 = cls(treatment_probability=0.4, random_state=99).assign(**kwargs)
    assert a1 == a2


@pytest.mark.parametrize("label,cls", GEO_SUPPORTED)
def test_different_seed_may_differ(label: str, cls: type):
    panel = make_geo_panel(seed=43, n_units=14)
    kwargs = dict(panel_data=panel, n_test_grps=1)
    a1 = cls(treatment_probability=0.4, random_state=1).assign(**kwargs)
    a2 = cls(treatment_probability=0.4, random_state=2).assign(**kwargs)
    # Stochastic designs should usually differ on this panel; allow rare equality.
    if label in ("balanced", "stratified"):
        # Deterministic given seed; different seeds should differ when possible.
        assert a1 != a2 or panel.num_units < 3
