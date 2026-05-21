"""Unit tests for design registry."""

import pytest

from panel_exp.design.assign import BalancedRandomization
from panel_exp.design.modes import register_builtin_designs
from panel_exp.design.registry import DesignRegistry, get_design_registry


def test_duplicate_design_name_raises():
    from panel_exp.design.registry import DesignSpec
    from panel_exp.design.geo_runner import run_geo_experiment_design

    reg = DesignRegistry()
    register_builtin_designs(reg)
    with pytest.raises(ValueError, match="already registered"):
        reg.register(
            DesignSpec(
                name="balancedrandomization",
                randomizer_cls=BalancedRandomization,
                run=run_geo_experiment_design,
            )
        )


def test_duplicate_alias_raises():
    reg = DesignRegistry()
    register_builtin_designs(reg)
    spec = reg.resolve("greedy_match_markets")
    dup = type(spec)(
        name="other_gmm",
        randomizer_cls=spec.randomizer_cls,
        aliases=("gmm",),
        run=spec.run,
    )
    with pytest.raises(ValueError, match="alias already registered"):
        reg.register(dup)


def test_deterministic_ordering():
    reg_a = DesignRegistry()
    reg_b = DesignRegistry()
    register_builtin_designs(reg_a)
    register_builtin_designs(reg_b)
    assert reg_a.list_names() == reg_b.list_names()
    assert get_design_registry().list_names() == reg_a.list_names()


def test_alias_resolution_gmm():
    reg = get_design_registry()
    assert reg.resolve("gmm") is reg.resolve("greedy_match_markets")


def test_unknown_design_raises():
    reg = get_design_registry()
    with pytest.raises(ValueError, match="Unsupported design"):
        reg.resolve("not_a_real_design")


def test_unknown_class_raises_lists_supported():
    class FakeDesign:
        pass

    reg = get_design_registry()
    with pytest.raises(ValueError, match="Supported designs"):
        reg.resolve(FakeDesign)


def test_geo_supported_names_include_balanced():
    from panel_exp.design.registry import LEGACY_GEO_RUN_DESIGN_SUPPORTED

    reg = get_design_registry()
    assert "balancedrandomization" in reg.geo_supported_names()
    assert {n.lower() for n in reg.geo_supported_names()} == {
        n.lower() for n in LEGACY_GEO_RUN_DESIGN_SUPPORTED
    }


def test_registry_run_returns_non_none():
    from panel_exp.design.geo_experiment_design import GeoExperimentDesign
    from tests.design_registry_helpers import make_geo_panel

    panel = make_geo_panel()
    geo = GeoExperimentDesign(
        panel_data=panel,
        base_randomizer_cls=BalancedRandomization,
        test_lengths=[28],
        validate_after_assign=False,
        max_iter=3,
    )
    design = geo.create_design()
    assignment = design.assign(panel_data=panel, n_test_grps=1)
    assert assignment is not None
    assert "control" in assignment
