"""Tests for power/MDE user contract metadata (no calculation changes)."""

from __future__ import annotations

from panel_exp.artifacts.experiment_card import build_experiment_card
from panel_exp.design.power import (
    MDE_SEMANTICS,
    PowerAnalysis,
    PowerContract,
    attach_power_contract,
    build_power_contract,
)
from panel_exp.methods.tbr import TBRRidge
from tests.power_helpers import make_synthetic_power_panel


def test_power_contract_defaults():
    contract = build_power_contract()
    assert contract["mde_type"] == "simulation_coverage"
    assert contract["classical_power"] is False
    assert contract["simulation_based"] is True
    assert contract["effect_units"] == "percent"
    assert contract["requires_null_calibration"] is True
    assert "compare design alternatives" in contract["recommended_use"]
    assert "guaranteed detectability claims" in contract["not_recommended_for"]
    assert any("simulation-based" in w.lower() for w in contract["warnings"])


def test_power_contract_dataclass_defaults():
    pc = PowerContract()
    d = pc.to_dict()
    assert d["mde_type"] == "simulation_coverage"
    assert d["classical_power"] is False


def test_build_power_contract_includes_default_warnings():
    contract = build_power_contract(MDE_SEMANTICS)
    assert any("effect grid" in w for w in contract["warnings"])
    assert any("Null calibration" in w for w in contract["warnings"])


def test_aa_calibration_incomplete_adds_warning():
    contract = build_power_contract(
        MDE_SEMANTICS,
        aa_calibration={
            "calibration_complete": False,
            "warnings": ["only 5 null replications"],
        },
    )
    assert any("null calibration incomplete" in w.lower() for w in contract["warnings"])


def test_build_power_contract_marks_run_when_semantics_post_analysis():
    contract = build_power_contract(
        {
            **MDE_SEMANTICS,
            "mde_percent": 0.05,
            "effect_grid_size": 49,
        },
        aa_calibration={"n_replications": 10, "calibration_complete": True},
    )
    assert contract["power_analysis_run"] is True


def test_generic_contract_not_marked_as_run():
    contract = build_power_contract()
    assert contract["power_analysis_run"] is False


def test_power_analysis_attaches_contract_after_run():
    panel = make_synthetic_power_panel(seed=4, n_time=20, treat_start=14)
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
        random_state=3,
    )
    pa.run_analysis()
    assert pa.power_contract["classical_power"] is False
    assert pa.power_contract["mde_type"] == "simulation_coverage"
    assert pa.power_contract["power_analysis_run"] is True
    assert pa.mde_semantics["classical_power"] is False


def test_attach_helper_additive():
    results: dict = {"y": [1.0]}
    contract = build_power_contract()
    attach_power_contract(results, contract)
    assert results["y"] == [1.0]
    assert results["power_contract"] == contract


def test_evidence_attach_power_contract_lazy():
    from panel_exp.evidence import attach_power_contract_to_artifacts

    artifacts: dict = {}
    attach_power_contract_to_artifacts(artifacts)
    assert artifacts["power_contract"]["classical_power"] is False


def test_experiment_card_generic_contract_without_implying_power_run():
    artifacts = {"power_contract": build_power_contract()}
    from panel_exp.evidence import DesignEvidence
    from panel_exp.panel_data import TimePeriod
    from panel_exp.spec import spec_from_geo_design

    spec = spec_from_geo_design(
        "pwr-card",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
    )
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["u0"], "test_0": ["u1"]},
        artifacts=artifacts,
        created_at="2026-05-20T12:00:00+00:00",
    )
    card = build_experiment_card(ev)
    assert card.power_results_available is False
    md = card.to_markdown()
    assert "## Power and MDE Contract" in md
    assert "### Interpretation rules" in md
    assert "do **not** mean a power study was run" in md
    assert "**Power results attached:** no" in md
    assert "No simulation-based power analysis results are attached" in md
    assert "### Power results (this run)" not in md


def test_experiment_card_shows_power_results_when_run_attached():
    panel = make_synthetic_power_panel(seed=7, n_time=20, treat_start=14)
    pa = PowerAnalysis(
        panel,
        TBRRidge,
        "Kfold",
        test_length=4,
        train_length=8,
        n_sample_prc=0.2,
        n_jobs=1,
        ci_version=2,
        random_state=4,
    )
    pa.run_analysis()
    artifacts = {
        "power_contract": pa.power_contract,
        "mde_semantics": pa.mde_semantics,
        "aa_calibration": pa.aa_calibration,
    }
    from panel_exp.evidence import DesignEvidence
    from panel_exp.panel_data import TimePeriod
    from panel_exp.spec import spec_from_geo_design

    spec = spec_from_geo_design(
        "pwr-run",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
    )
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["u0"], "test_0": ["u1"]},
        artifacts=artifacts,
        created_at="2026-05-20T12:00:00+00:00",
    )
    card = build_experiment_card(ev)
    assert card.power_results_available is True
    md = card.to_markdown()
    assert "**Power results attached:** yes" in md
    assert "### Power results (this run)" in md
    assert card.power_results_mde_percent is not None


def test_backward_compatible_summary_keys():
    panel = make_synthetic_power_panel(seed=5)
    pa = PowerAnalysis(
        panel,
        TBRRidge,
        "Kfold",
        test_length=4,
        train_length=8,
        n_sample_prc=0.2,
        n_jobs=1,
        ci_version=2,
        random_state=1,
    )
    pa.run_analysis()
    summary = pa.summary()
    assert "MDE Percent" in summary.index
    assert "Power" in summary.index


def test_input_objects_not_mutated():
    panel = make_synthetic_power_panel(seed=6)
    pa = PowerAnalysis(
        panel,
        TBRRidge,
        "Kfold",
        test_length=4,
        train_length=8,
        n_sample_prc=0.2,
        n_jobs=1,
        ci_version=2,
        random_state=2,
    )
    pa.run_analysis()
    out_snapshot = pa.output_df.copy()
    mde_snapshot = dict(pa.mde_semantics)
    contract_snapshot = dict(pa.power_contract)
    artifacts: dict = {"keep": True}
    attach_power_contract(
        artifacts,
        build_power_contract(pa.mde_semantics, aa_calibration=pa.aa_calibration),
    )
    assert pa.output_df.equals(out_snapshot)
    assert pa.mde_semantics == mde_snapshot
    assert pa.power_contract == contract_snapshot
    assert artifacts["keep"] is True
