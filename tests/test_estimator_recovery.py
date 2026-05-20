"""Integration tests: estimators recover synthetic truth."""

import json

import pytest

from panel_exp.validation.runner import run_estimator_validation, run_scenario_validation
from panel_exp.validation.scenarios import get_scenario


@pytest.mark.parametrize("estimator", ["SCM", "TBR", "DID"])
def test_positive_effect_recovered_approximately(estimator):
    scenario = get_scenario("constant_positive_10pct")
    results = run_scenario_validation(
        scenario, estimators=[estimator], n_replications=1
    )
    assert len(results) == 1
    r = results[0]
    assert abs(r.bias) < 0.08
    assert abs(r.truth - 0.10) < 0.02


def test_aa_bias_near_zero_scm():
    scenario = get_scenario("aa_zero_effect")
    results = run_scenario_validation(
        scenario, estimators=["SCM"], n_replications=1
    )
    r = results[0]
    assert abs(r.truth) < 1e-10
    assert abs(r.bias) < 0.15


@pytest.mark.parametrize("estimator", ["DID"])
def test_coverage_in_valid_range(estimator):
    scenario = get_scenario("constant_positive_10pct")
    results = run_scenario_validation(
        scenario,
        estimators=[estimator],
        n_replications=8,
        replication_seed_step=3,
    )
    r = results[0]
    if not (r.coverage == r.coverage):  # nan check
        pytest.skip("No intervals returned for coverage check")
    assert 0.0 <= r.coverage <= 1.0


def test_deterministic_validation_with_seed():
    scenario = get_scenario("constant_positive_10pct")
    r1 = run_scenario_validation(
        scenario, estimators=["SCM"], n_replications=1
    )[0]
    r2 = run_scenario_validation(
        scenario, estimators=["SCM"], n_replications=1
    )[0]
    assert r1.bias == r2.bias
    assert r1.rmse == r2.rmse


def test_report_serializes_end_to_end():
    report = run_estimator_validation(
        scenario_names=["aa_zero_effect", "constant_positive_10pct"],
        estimators=["SCM", "DID"],
        n_replications=2,
    )
    payload = json.loads(report.to_json())
    assert payload["evidence_version"]
    assert len(payload["results"]) >= 2
    assert "recovery_statement" in payload
    assert "correct" not in payload["recovery_statement"].lower() or "recovery" in payload["recovery_statement"].lower()


@pytest.mark.slow
def test_sdid_runs_when_stable():
    scenario = get_scenario("small_geo")
    results = run_scenario_validation(
        scenario, estimators=["SDID"], n_replications=1
    )
    r = results[0]
    assert r.n_replications == 1
    assert r.rmse == r.rmse  # not nan
