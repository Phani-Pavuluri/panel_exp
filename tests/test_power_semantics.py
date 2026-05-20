"""MDE semantics and backward-compatible power outputs."""

from __future__ import annotations

import inspect

from panel_exp.design.power import MDE_SEMANTICS, PowerAnalysis, evaluate_aa_calibration
from panel_exp.methods.tbr import TBRRidge
from tests.power_helpers import make_synthetic_power_panel


def test_mde_semantics_module_constants():
    assert MDE_SEMANTICS["mde_method"] == "simulation_coverage"
    assert MDE_SEMANTICS["classical_power"] is False
    assert "effect" in MDE_SEMANTICS["mde_definition"].lower()


def test_power_analysis_docstring_states_simulation_mde():
    doc = inspect.getdoc(PowerAnalysis) or ""
    assert "simulation" in doc.lower() or "coverage" in doc.lower()
    assert "not" in doc.lower() and "closed-form" in doc.lower()


def test_run_analysis_attaches_mde_semantics_and_aa_calibration():
    panel = make_synthetic_power_panel(seed=1, n_time=20, treat_start=14)
    pa = PowerAnalysis(
        panel,
        TBRRidge,
        "Kfold",
        test_length=4,
        train_length=8,
        mx_effect=0.1,
        n_sample_prc=0.25,
        n_jobs=1,
        ci_version=2,
        random_state=11,
    )
    pa.run_analysis()
    assert pa.mde_semantics["classical_power"] is False
    assert pa.mde_semantics["mde_method"] == "simulation_coverage"
    assert pa.mde_semantics["random_state"] == 11
    assert pa.aa_calibration is not None
    assert "n_replications" in pa.aa_calibration


def test_summary_output_keys_backward_compatible():
    panel = make_synthetic_power_panel(seed=2)
    pa = PowerAnalysis(
        panel,
        TBRRidge,
        "Kfold",
        test_length=4,
        train_length=8,
        mx_effect=0.1,
        n_sample_prc=0.2,
        n_jobs=1,
        ci_version=2,
        random_state=5,
    )
    pa.run_analysis()
    summary = pa.summary()
    assert "MDE Percent" in summary.index
    assert "MDE KPI" in summary.index
    assert "Power" in summary.index
    assert "Type 1 Error Rate" in summary.index


def test_evaluate_aa_calibration_null_rows():
    panel = make_synthetic_power_panel(seed=3)
    pa = PowerAnalysis(
        panel,
        TBRRidge,
        "Kfold",
        test_length=4,
        train_length=8,
        n_sample_prc=0.2,
        n_jobs=1,
        ci_version=2,
        random_state=7,
    )
    pa.run_analysis()
    report = evaluate_aa_calibration(pa.output_df, min_replications=1)
    assert report["n_replications"] > 0
    assert report["coverage"] is not None
    assert report["false_positive_rate"] is not None
    assert report["calibration_complete"] in (True, False)


def test_geo_power_path_forwards_random_state():
    from panel_exp.design.geo_experiment_design import GeoExperimentDesign

    panel = make_synthetic_power_panel()
    geo = GeoExperimentDesign(
        panel,
        test_lengths=[4],
        train_length=8,
        n_sample_prc=0.2,
        random_state=99,
        njobs=2,
    )
    pa = PowerAnalysis(
        panel,
        TBRRidge,
        geo.inference,
        test_length=4,
        train_length=geo.train_length,
        n_jobs=geo.njobs,
        n_sample_prc=geo.n_sample_prc,
        ci_version=geo.ci_version,
        alpha=geo.alpha,
        random_state=geo.random_state,
    )
    assert pa.random_state == 99
    assert pa.n_jobs == 2
