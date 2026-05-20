"""Estimator maturity metadata registry and evidence integration."""

from __future__ import annotations

import json

import pytest

from panel_exp.evidence import DesignEvidence
from panel_exp.inference.registry import get_inference_registry
from panel_exp.method_metadata import EstimatorMaturity, MATURITY_DOC
from panel_exp.method_registry import get_method_registry
from panel_exp.methods.scm import SyntheticControl
from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import spec_from_geo_design
from tests.inference_registry_helpers import make_tbr_panel


def test_maturity_enum_values():
    assert EstimatorMaturity.PRODUCTION_SAFE.value == "production_safe"
    assert EstimatorMaturity.UNVALIDATED.value == "unvalidated"


def test_maturity_doc_states_not_superiority():
    assert "not statistical superiority" in MATURITY_DOC.lower()


def test_every_catalog_estimator_has_metadata():
    reg = get_method_registry()
    names = reg.list_estimator_names()
    assert "SCM" in names
    assert "TBRRidge" in names
    assert len(names) >= 12
    for name in names:
        meta = reg.metadata(name)
        assert meta.rationale
        assert meta.assumptions


def test_every_inference_mode_has_metadata():
    reg = get_method_registry()
    inf_reg = get_inference_registry()
    for mode in inf_reg.list_mode_names():
        meta = reg.inference_metadata(mode)
        assert meta.maturity in EstimatorMaturity


def test_unknown_estimator_name_fails_loudly():
    with pytest.raises(KeyError, match="Unknown estimator"):
        get_method_registry().metadata("NotARealEstimator")


def test_unknown_inference_mode_fails_loudly():
    with pytest.raises(KeyError, match="Unknown inference mode"):
        get_method_registry().inference_metadata("NotARealInference")


def test_tbrridge_production_safe_scm_expert_review():
    reg = get_method_registry()
    assert reg.metadata("TBRRidge").maturity == EstimatorMaturity.PRODUCTION_SAFE
    assert reg.metadata("TBRRidge").synthetic_validation is True
    assert reg.metadata("SCM").maturity == EstimatorMaturity.EXPERT_REVIEW
    assert reg.metadata("BayesianTBR").maturity == EstimatorMaturity.RESEARCH_ONLY


def test_estimator_metadata_property_on_analyzer():
    est = TBRRidge(inference=None)
    meta = est.estimator_metadata
    assert meta.name == "TBRRidge"
    assert meta.maturity == EstimatorMaturity.PRODUCTION_SAFE


def test_evidence_includes_maturity_fields():
    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 10),
        TimePeriod(10, 30),
        "balancedrandomization",
        estimator="TBRRidge",
    )
    ev = DesignEvidence.from_assignment(spec, {"control": ["a"], "test_0": ["b"]})
    assert "interference_assumption" in ev.inference_metadata


def test_run_analysis_attaches_estimator_maturity_metadata():
    pds = make_tbr_panel(seed=0, n_time=24, treat_start=18)
    est = TBRRidge(inference=None, alpha=0.05)
    est.run_analysis(pds)
    meta = est.results.get("inference_metadata") or {}
    assert meta.get("estimator_maturity") == "production_safe"
    assert meta.get("inference_mode_maturity") == "production_safe"
    assert meta.get("estimator_rationale")


def test_estimator_outputs_unchanged_numeric_path():
    pds = make_tbr_panel(seed=1, n_time=24, treat_start=18)
    est1 = TBRRidge(inference=None)
    est1.run_analysis(pds)
    y_hat1 = est1.results["y_hat"].copy()

    est2 = SyntheticControl(inference=None)
    est2.run_analysis(pds)
    assert "y_hat" in est2.results
    assert len(est2.results["y_hat"]) == len(y_hat1)


def test_metadata_survives_evidence_json_roundtrip():
    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
    )
    pds = make_tbr_panel()
    est = TBRRidge(inference="Kfold", alpha=0.05)
    est.run_analysis(pds, k=3, show_progress=False, n_jobs=1, random_state=0)
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["ctrl_0", "ctrl_1"], "test_0": ["treated"]},
        inference_metadata=dict(est.results.get("inference_metadata", {})),
    )
    payload = json.loads(ev.to_json())
    assert payload["inference_metadata"]["estimator_maturity"] == "production_safe"
    assert payload["inference_metadata"]["inference_mode_maturity"] == "expert_review"
