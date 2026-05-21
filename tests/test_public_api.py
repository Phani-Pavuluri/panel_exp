"""Public API surface matches documented package behavior."""

from __future__ import annotations

import importlib

import pytest

import panel_exp
from panel_exp.design import (
    GEO_RUN_DESIGN_SUPPORTED,
    MatchedPair,
    QuickBlock,
    get_design_registry,
)
from panel_exp.design.geo_experiment_design import GeoExperimentDesign
from panel_exp.design.registry import LEGACY_GEO_RUN_DESIGN_SUPPORTED
from tests.design_registry_helpers import make_geo_panel


DOCUMENTED_PUBLIC_IMPORTS = (
    "PanelDataset",
    "TimePeriod",
    "long_df_to_paneldataset",
    "DesignSpec",
    "ExperimentSpec",
    "DesignMethod",
    "InterferenceAssumption",
    "EstimatorMaturity",
    "get_method_registry",
    "get_design_registry",
    "GEO_RUN_DESIGN_SUPPORTED",
    "class_name_to_design_method",
    "spec_from_geo_design",
    "InferenceResult",
    "IntervalType",
    "DesignEvidence",
    "InferenceEvidence",
    "ExperimentEvidence",
    "build_experiment_card",
    "attach_experiment_card_markdown",
    "BalancedRandomization",
    "CompleteRandomization",
    "StratifiedRandomization",
    "ThinningDesign",
    "Rerandomization",
    "greedy_match_markets",
    "GeoExperimentDesign",
    "PowerAnalysis",
    "validate_design",
    "DesignValidationResult",
    "ValidationStatus",
)


def test_import_panel_exp_succeeds():
    assert panel_exp.__version__


@pytest.mark.parametrize("name", DOCUMENTED_PUBLIC_IMPORTS)
def test_documented_public_import(name: str):
    getattr(panel_exp, name)


def test_lazy_estimator_imports():
    assert panel_exp.SyntheticControl.__name__ == "SyntheticControl"
    assert panel_exp.TBRRidge.__name__ == "TBRRidge"


def test_geo_run_supported_matches_legacy_allowlist():
    reg = get_design_registry()
    assert {n.lower() for n in reg.geo_supported_names()} == {
        n.lower() for n in LEGACY_GEO_RUN_DESIGN_SUPPORTED
    }
    assert GEO_RUN_DESIGN_SUPPORTED == LEGACY_GEO_RUN_DESIGN_SUPPORTED


def test_documented_geo_supported_set():
    expected = {
        "greedy_match_markets",
        "thinningdesign",
        "balancedrandomization",
        "completerandomization",
        "stratifiedrandomization",
    }
    assert {n.lower() for n in GEO_RUN_DESIGN_SUPPORTED} == expected


@pytest.mark.parametrize(
    "randomizer_cls",
    [QuickBlock, MatchedPair],
)
def test_unsupported_geo_design_fails_at_construction(randomizer_cls):
    panel = make_geo_panel()
    with pytest.raises(ValueError, match="not supported via GeoExperimentDesign"):
        GeoExperimentDesign(
            panel_data=panel,
            base_randomizer_cls=randomizer_cls,
            test_lengths=[28],
            validate_after_assign=False,
        )


def test_quickblock_registered_but_not_geo_supported():
    reg = get_design_registry()
    spec = reg.resolve(QuickBlock)
    assert spec.geo_run_supported is False
    assert "quickblock" in {n.lower() for n in reg.list_names()}


def test_build_experiment_card_top_level_import():
    from panel_exp import build_experiment_card
    from panel_exp.evidence import DesignEvidence
    from panel_exp.panel_data import TimePeriod
    from panel_exp.spec import spec_from_geo_design

    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
    )
    ev = DesignEvidence.from_assignment(
        spec, {"control": ["a"], "test_0": ["b"]}, created_at="2026-01-01T00:00:00+00:00"
    )
    card = build_experiment_card(ev)
    assert "Experiment Card" in card.to_markdown()


def test_estimator_maturity_and_registry_imports():
    from panel_exp import EstimatorMaturity, get_method_registry

    reg = get_method_registry()
    assert EstimatorMaturity.PRODUCTION_SAFE.value == "production_safe"
    assert reg.metadata("TBRRidge").maturity != EstimatorMaturity.PRODUCTION_SAFE


def test_panel_exp_util_not_public():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("panel_exp.util")


def test_pretest_analysis_not_shipped():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("panel_exp.pretest_analysis")


def test_recovery_runner_subpackage_import():
    from panel_exp.validation import RecoveryRunner

    assert RecoveryRunner.__name__ == "RecoveryRunner"
