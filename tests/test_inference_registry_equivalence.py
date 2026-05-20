"""
Equivalence tests for ImpactAnalyzer inference registry refactor.

Covers legacy output keys, alias resolution, kwargs mutation, registry ordering,
failure behavior, and numerical regression against committed golden fixtures.
"""

from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import pytest

from panel_exp.inference.modes import register_builtin_inference_modes
from panel_exp.inference.registry import InferenceRegistry, get_inference_registry
from panel_exp.methods.scm import SyntheticControl
from panel_exp.methods.tbr import TBRRidge, TBR
from panel_exp.panel_data import PanelDataset, TimePeriod

from tests.inference_registry_helpers import (
    GOLDEN_DIR,
    GOLDEN_NUMERIC_KEYS,
    LEGACY_RESULTS_KEYS,
    PLACEBO_OPTIONAL_KEYS,
    assert_arrays_allclose,
    load_golden,
    make_scm_panel,
    make_tbr_panel,
)

EXPECTED_MODE_KEYS = [
    None,
    "UnitJackKnife",
    "JKP",
    "Bayesian",
    "BlockResidualBootstrap",
    "Conformal",
    "Kfold",
    "Placebo",
    "TimeSeriesKfold",
]

EXPECTED_MODE_NAMES = [
    "point_estimate",
    "UnitJackKnife",
    "JKP",
    "Bayesian",
    "BlockResidualBootstrap",
    "Conformal",
    "Kfold",
    "Placebo",
    "TimeSeriesKfold",
]

# kwargs used when generating tests/fixtures/inference_golden/*.npz
GOLDEN_RUN_KWARGS: dict[str, dict] = {
    "point_estimate": {},
    "UnitJackKnife": {},
    "JKP": {},
    "Kfold": {},
    "Conformal": {},
    "BlockResidualBootstrap": {
        "n_bootstrap": 25,
        "block_length": 4,
        "show_progress": False,
        "random_state": 42,
    },
    "TimeSeriesKfold": {"k": 3, "show_progress": False, "n_jobs": 1},
    "Placebo": {},
}

GOLDEN_PANEL_BUILDERS = {
    "point_estimate": lambda: make_tbr_panel(seed=42),
    "UnitJackKnife": lambda: make_tbr_panel(seed=42),
    "JKP": lambda: make_tbr_panel(seed=42, n_time=35, treat_start=20),
    "Kfold": lambda: make_tbr_panel(seed=42),
    "Conformal": lambda: make_tbr_panel(seed=42),
    "BlockResidualBootstrap": lambda: make_tbr_panel(seed=42),
    "TimeSeriesKfold": lambda: make_tbr_panel(seed=42),
    "Placebo": lambda: make_scm_panel(seed=42, n_ctrl=6),
    "Bayesian": lambda: make_tbr_panel(seed=99),
}


@pytest.fixture
def fresh_registry() -> InferenceRegistry:
    reg = InferenceRegistry()
    register_builtin_inference_modes(reg)
    return reg


def _run_mode(mode: str, panel: PanelDataset | None = None, **extra_kwargs):
    inference = None if mode == "point_estimate" else mode
    kwargs = {**GOLDEN_RUN_KWARGS.get(mode, {}), **extra_kwargs}
    if mode == "Placebo":
        est = SyntheticControl(inference="Placebo", alpha=0.05)
        pds = panel or GOLDEN_PANEL_BUILDERS[mode]()
    else:
        est = TBRRidge(inference=inference, alpha=0.05)
        pds = panel or GOLDEN_PANEL_BUILDERS[mode]()
    est.run_analysis(pds, **kwargs)
    return est


# ---------------------------------------------------------------------------
# 1. Legacy output key equivalence
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", [m for m in EXPECTED_MODE_KEYS if m is not None])
def test_legacy_results_keys_match_contract(mode: str):
    if mode == "Bayesian":
        pytest.importorskip("jax")
    est = _run_mode(mode)
    expected = LEGACY_RESULTS_KEYS[mode]
    actual_keys = set(est.results.keys())
    assert expected <= actual_keys, (
        f"{mode}: missing keys {expected - actual_keys}; got {sorted(actual_keys)}"
    )
    if mode == "Placebo":
        extra = actual_keys - expected - PLACEBO_OPTIONAL_KEYS
        assert not extra, f"unexpected Placebo keys: {extra}"


def test_point_estimate_legacy_keys():
    est = _run_mode("point_estimate")
    assert set(est.results.keys()) == LEGACY_RESULTS_KEYS[None]


def test_placebo_unsupported_legacy_keys_no_fake_bands():
    wide = pd.DataFrame({"c1": np.arange(20.0), "c2": np.arange(20.0) + 1})
    pds = PanelDataset(wide.T, treated_units=["c1"], treated_periods=[TimePeriod(10)])
    scm = SyntheticControl(inference="Placebo", alpha=0.05)
    with pytest.raises(ValueError, match="Placebo inference unavailable"):
        scm.run_analysis(pds, placebo_strict=True)
    assert set(scm.results.keys()) == LEGACY_RESULTS_KEYS["Placebo_unsupported"]
    assert "y_lower" not in scm.results
    assert "y_upper" not in scm.results


# ---------------------------------------------------------------------------
# 2. Alias equivalence
# ---------------------------------------------------------------------------


def test_unit_jackknife_aliases_resolve_to_same_spec(fresh_registry):
    spec = fresh_registry.resolve("UnitJackKnife")
    for alias in spec.aliases:
        assert fresh_registry.resolve(alias) is spec


def test_jkp_is_distinct_from_unit_jackknife(fresh_registry):
    jkp = fresh_registry.resolve("JKP")
    ujk = fresh_registry.resolve("UnitJackKnife")
    assert jkp.name == "JKP"
    assert ujk.name == "UnitJackKnife"
    assert jkp.run is not ujk.run


def test_alias_registry_resolution_matches_canonical_key():
    reg = InferenceRegistry()
    from panel_exp.inference.modes.impl import run_unit_jackknife
    from panel_exp.inference.registry import InferenceModeSpec

    reg.register(
        InferenceModeSpec(
            name="UnitJackKnife",
            aliases=("unit_jk",),
            run=run_unit_jackknife,
            output_keys=LEGACY_RESULTS_KEYS["UnitJackKnife"],
        )
    )
    assert reg.resolve("unit_jk") is reg.resolve("UnitJackKnife")


# ---------------------------------------------------------------------------
# 3. Mutation compatibility (BRB pops; TimeSeriesKfold does not)
# ---------------------------------------------------------------------------


def test_brb_run_analysis_does_not_mutate_caller_kwargs_dict():
    """``run_analysis(pds, **kw)`` unpacks kwargs; caller dict stays unchanged (legacy)."""
    pds = make_tbr_panel(seed=42)
    kw = {
        "n_bootstrap": 25,
        "block_length": 4,
        "show_progress": False,
        "random_state": 42,
    }
    snapshot = kw.copy()
    est = TBRRidge(inference="BlockResidualBootstrap", alpha=0.05)
    est.run_analysis(pds, **kw)
    assert kw == snapshot


def test_brb_registry_run_mutates_passed_inference_kwargs_dict():
    """Direct registry dispatch pops consumed keys on the shared kwargs dict."""
    pds = make_tbr_panel(seed=42)
    kw = {
        "n_bootstrap": 25,
        "block_length": 4,
        "show_progress": False,
        "random_state": 42,
    }
    est = TBRRidge(inference="BlockResidualBootstrap", alpha=0.05)
    est.panel_data = pds
    get_inference_registry().run("BlockResidualBootstrap", est, pds, kw)
    for key in (
        "n_bootstrap",
        "block_length",
        "show_progress",
        "random_state",
        "center_residuals",
        "refit_in_bootstrap",
    ):
        assert key not in kw


def test_timeseries_kfold_inference_kwargs_not_popped():
    pds = make_tbr_panel(seed=42)
    kw = {"k": 3, "debias_flag": True, "block_scheme": "expanding", "show_progress": False}
    snapshot = copy.deepcopy(kw)
    est = TBRRidge(inference="TimeSeriesKfold", alpha=0.05)
    est.run_analysis(pds, **kw)
    assert kw == snapshot


# ---------------------------------------------------------------------------
# 4. Ordering / determinism
# ---------------------------------------------------------------------------


def test_registry_mode_listing_stable_across_instances():
    reg_a = InferenceRegistry()
    reg_b = InferenceRegistry()
    register_builtin_inference_modes(reg_a)
    register_builtin_inference_modes(reg_b)
    assert reg_a.list_mode_keys() == reg_b.list_mode_keys()
    assert reg_a.list_mode_names() == reg_b.list_mode_names()


def test_builtin_registry_keys_and_names_order():
    reg = get_inference_registry()
    assert reg.list_mode_keys() == EXPECTED_MODE_KEYS
    assert reg.list_mode_names() == EXPECTED_MODE_NAMES


@pytest.mark.parametrize("mode", list(GOLDEN_NUMERIC_KEYS))
def test_repeat_run_produces_identical_outputs(mode: str):
    if mode == "Bayesian":
        pytest.importorskip("jax")
    if mode == "Placebo":
        est1 = _run_mode(mode)
        est2 = _run_mode(mode)
    else:
        est1 = _run_mode(mode)
        est2 = _run_mode(mode)
    for key in GOLDEN_NUMERIC_KEYS[mode]:
        if key in est1.results and key in est2.results:
            assert_arrays_allclose(est1.results[key], est2.results[key], label=key)


# ---------------------------------------------------------------------------
# 5. Failure behavior
# ---------------------------------------------------------------------------


def test_unknown_inference_raises_not_implemented():
    est = TBRRidge(inference="NotAMode", alpha=0.05)
    with pytest.raises(NotImplementedError, match="not a supported inference method"):
        est.run_analysis(make_tbr_panel())


def test_unit_jackknife_insufficient_controls_raises():
    wide = pd.DataFrame({"c1": np.arange(20.0)})
    pds = PanelDataset(wide.T, treated_units=["c1"], treated_periods=[TimePeriod(10)])
    est = TBRRidge(inference="UnitJackKnife", alpha=0.05)
    with pytest.raises(ValueError, match="at least 2 control units"):
        est.run_analysis(pds)


def test_placebo_strict_raises_with_legacy_message():
    wide = pd.DataFrame({"c1": np.arange(20.0), "c2": np.arange(20.0) + 1})
    pds = PanelDataset(wide.T, treated_units=["c1"], treated_periods=[TimePeriod(10)])
    scm = SyntheticControl(inference="Placebo", alpha=0.05)
    with pytest.raises(ValueError, match="Placebo inference unavailable"):
        scm.run_analysis(pds, placebo_strict=True)


def test_placebo_tbr_unsupported_message():
    rng = np.random.default_rng(0)
    n = 25
    wide = pd.DataFrame(
        {
            "treated": np.linspace(1000, 1200, n) + rng.normal(0, 30, n),
            "control": np.linspace(800, 960, n) + rng.normal(0, 20, n),
        },
    ).T
    wide.columns = range(n)
    pds = PanelDataset(wide, [TimePeriod(20, None)], ["treated"])
    est = TBR(inference="Placebo", alpha=0.05)
    with pytest.raises(ValueError, match="TBR requires aggregated control"):
        est.run_analysis(pds, placebo_strict=True)
    assert est.results["placebo_unsupported"] == (
        "TBR requires aggregated control; placebo-in-space excluded"
    )


def test_placebo_few_controls_message():
    wide = pd.DataFrame({f"c{i}": np.arange(20.0) + i for i in range(4)})
    pds = PanelDataset(wide.T, treated_units=["c0"], treated_periods=[TimePeriod(10)])
    scm = SyntheticControl(inference="Placebo", alpha=0.05)
    with pytest.raises(ValueError, match=">=5 control units"):
        scm.run_analysis(pds, placebo_strict=True)


# ---------------------------------------------------------------------------
# 6. No statistical drift (golden fixtures)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", list(GOLDEN_NUMERIC_KEYS))
def test_numeric_outputs_match_golden_fixture(mode: str):
    if not (GOLDEN_DIR / f"{mode}.npz").exists():
        pytest.skip(f"golden fixture missing for {mode}")
    if mode == "Bayesian":
        pytest.importorskip("jax")
    golden = load_golden(mode)
    est = _run_mode(mode)
    for key, expected in golden.items():
        assert key in est.results, f"{mode}: missing {key} in results"
        assert_arrays_allclose(
            est.results[key],
            expected,
            rtol=1e-10,
            atol=1e-10,
            label=f"{mode}.{key}",
        )
