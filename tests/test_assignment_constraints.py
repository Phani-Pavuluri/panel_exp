"""Whitelist/blacklist constraint enforcement for geo-supported designs."""

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


def _assign(cls, panel, *, seed: int = 7, **kwargs):
    design = cls(treatment_probability=0.35, random_state=seed)
    return design.assign(panel_data=panel, n_test_grps=1, **kwargs)


@pytest.mark.parametrize("label,cls", GEO_SUPPORTED)
def test_whitelist_honored(label: str, cls: type):
    panel = make_geo_panel(seed=1, n_units=12)
    out = _assign(
        cls,
        panel,
        control_whitelist=["u0"],
        test_whitelist=["u1"],
    )
    assert "u0" in out["control"]
    assert "u1" in out["test_0"]


@pytest.mark.parametrize("label,cls", GEO_SUPPORTED)
def test_blacklist_excluded(label: str, cls: type):
    panel = make_geo_panel(seed=2, n_units=12)
    out = _assign(
        cls,
        panel,
        control_blacklist=["u2"],
        test_blacklist=["u3"],
        control_test_blacklist=["u4"],
    )
    assigned = set(out["control"]) | set(out["test_0"])
    assert "u2" not in out["control"]
    assert "u3" not in out["test_0"]
    assert "u4" not in assigned


@pytest.mark.parametrize("label,cls", GEO_SUPPORTED)
def test_whitelist_conflict_fails(label: str, cls: type):
    panel = make_geo_panel(seed=3, n_units=10)
    with pytest.raises(ValueError, match="both control and test whitelist"):
        _assign(cls, panel, control_whitelist=["u0"], test_whitelist=["u0"])


@pytest.mark.parametrize("label,cls", GEO_SUPPORTED)
def test_unknown_geo_in_constraint_fails(label: str, cls: type):
    panel = make_geo_panel(seed=4, n_units=8)
    with pytest.raises(ValueError, match="unknown units"):
        _assign(cls, panel, control_whitelist=["not_a_unit"])


def test_impossible_test_whitelist_capacity_fails():
    panel = make_geo_panel(seed=5, n_units=8)
    br = BalancedRandomization(treatment_probability=0.0, random_state=1)
    with pytest.raises(ValueError, match="test_whitelist pins"):
        br.assign(
            panel_data=panel,
            test_whitelist=["u0"],
            n_test_grps=1,
        )


def test_too_many_blacklisted_fails():
    panel = make_geo_panel(seed=6, n_units=6)
    br = BalancedRandomization(treatment_probability=0.5, random_state=1)
    with pytest.raises(ValueError, match="not enough geos"):
        br.assign(
            panel_data=panel,
            control_test_blacklist=["u0", "u1", "u2", "u3", "u4", "u5"],
            n_test_grps=1,
        )


def test_constraint_failure_before_geo_evidence(monkeypatch):
    """Impossible constraints fail at assign, before validate/evidence/MDE."""
    from panel_exp.design.geo_experiment_design import GeoExperimentDesign

    panel = make_geo_panel(seed=7, n_units=8)
    geo = GeoExperimentDesign(
        panel_data=panel,
        base_randomizer_cls=BalancedRandomization,
        random_state=1,
        validate_after_assign=True,
        test_lengths=[28],
    )
    mde_called = []

    def _mde(self, *args, **kwargs):
        mde_called.append(True)
        raise AssertionError("MDE should not run when assign fails")

    monkeypatch.setattr(GeoExperimentDesign, "_calculate_sensitivity_metrics", _mde)
    geo.control_whitelist = ["u0"]
    geo.test_whitelist = ["u0"]
    with pytest.raises(ValueError):
        geo.run_design()
    assert mde_called == []
    assert geo.last_evidence is None
