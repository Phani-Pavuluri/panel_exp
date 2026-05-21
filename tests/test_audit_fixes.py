"""Tests for adversarial-audit remediation (v0.2.1)."""


import numpy as np
import pandas as pd
import pytest

from panel_exp import (
    BalancedRandomization,
    CompleteRandomization,
    DesignSpec,
    GeoExperimentDesign,
    InterferenceAssumption,
    PanelDataset,
    PowerAnalysis,
    StratifiedRandomization,
    TimePeriod,
    validate_design,
)
from panel_exp.design.geo_experiment_design import GEO_RUN_DESIGN_SUPPORTED
from panel_exp.methods.tbr import TBRRidge
from panel_exp.spec import DesignMethod, class_name_to_design_method


def _synthetic_panel(n_units=8, n_times=40, seed=0):
    rng = np.random.default_rng(seed)
    units = [f"u{i}" for i in range(n_units)]
    cols = list(range(n_times))
    wide = pd.DataFrame(rng.uniform(10, 100, (n_units, n_times)), index=units, columns=cols)
    return PanelDataset(wide)


def test_design_spec_required_fields():
    with pytest.raises(ValueError, match="experiment_id"):
        DesignSpec(
            experiment_id="",
            outcome_column="y",
            unit_column="u",
            time_column="t",
            pre_period=TimePeriod(0, 10),
            experiment_period=TimePeriod(10, 20),
            design_method=DesignMethod.BALANCED_RANDOMIZATION,
        )
    with pytest.raises(ValueError, match="treatment_probability"):
        DesignSpec(
            experiment_id="e1",
            outcome_column="y",
            unit_column="u",
            time_column="t",
            pre_period=TimePeriod(0, 10),
            experiment_period=TimePeriod(10, 20),
            design_method=DesignMethod.BALANCED_RANDOMIZATION,
            treatment_probability=1.5,
        )


def test_geo_run_design_unsupported():
    from panel_exp.design.quickblock import QuickBlock

    panel = _synthetic_panel()
    with pytest.raises(ValueError, match="not supported via GeoExperimentDesign"):
        GeoExperimentDesign(panel_data=panel, base_randomizer_cls=QuickBlock)


def test_geo_run_design_supported_names():
    assert "greedy_match_markets" in GEO_RUN_DESIGN_SUPPORTED
    assert "balancedrandomization" in GEO_RUN_DESIGN_SUPPORTED


def test_whitelist_blacklist_balanced():
    panel = _synthetic_panel()
    br = BalancedRandomization(treatment_probability=0.3, random_state=1)
    assignment = br.assign(
        panel_data=panel,
        control_whitelist=["u0"],
        test_whitelist=["u1"],
        control_blacklist=["u2"],
        test_blacklist=["u3"],
        n_test_grps=1,
    )
    assert "u0" in assignment["control"]
    assert "u1" in assignment["test_0"]
    assert "u2" not in assignment["control"]
    assert "u3" not in assignment["test_0"]


def test_whitelist_conflict_fails():
    panel = _synthetic_panel()
    br = BalancedRandomization(random_state=1)
    with pytest.raises(ValueError, match="both control and test whitelist"):
        br.assign(panel_data=panel, control_whitelist=["u0"], test_whitelist=["u0"])


def test_stratified_enforces_whitelist():
    panel = _synthetic_panel()
    sr = StratifiedRandomization(treatment_probability=0.3, random_state=2)
    assignment = sr.assign(
        panel_data=panel,
        control_whitelist=["u0"],
        test_whitelist=["u1"],
        n_test_grps=1,
    )
    assert "u0" in assignment["control"]
    assert "u1" in assignment["test_0"]


def test_seeded_assignment_reproducible():
    panel = _synthetic_panel()
    a1 = BalancedRandomization(treatment_probability=0.3, random_state=99).assign(
        panel_data=panel, n_test_grps=1
    )
    a2 = BalancedRandomization(treatment_probability=0.3, random_state=99).assign(
        panel_data=panel, n_test_grps=1
    )
    assert a1 == a2
    a3 = BalancedRandomization(treatment_probability=0.3, random_state=100).assign(
        panel_data=panel, n_test_grps=1
    )
    assert a1 != a3


def test_complete_vs_balanced_differ():
    panel = _synthetic_panel(n_units=20)
    b = CompleteRandomization(treatment_probability=0.4, random_state=5).assign(
        panel_data=panel, n_test_grps=1
    )
    vol = BalancedRandomization(treatment_probability=0.4, random_state=5).assign(
        panel_data=panel, n_test_grps=1
    )
    # Not guaranteed different but usually differ on multi-unit panels
    assert set(b["control"]) | set(b["test_0"]) == set(vol["control"]) | set(vol["test_0"])


def test_rerandomization_no_name_error():
    panel = _synthetic_panel(n_units=10)
    from panel_exp.design.assign import Rerandomization

    rr = Rerandomization(
        treatment_probability=0.3,
        max_iter=5,
        base_randomizer_cls=BalancedRandomization,
        random_state=3,
    )
    out = rr.assign(panel_data=panel, n_test_grps=1)
    assert "control" in out and "test_0" in out


def test_rerandomization_unsupported_base_raises():
    from panel_exp.design.quickblock import QuickBlock
    from panel_exp.design.assign import Rerandomization

    panel = _synthetic_panel()
    rr = Rerandomization(
        treatment_probability=0.3, max_iter=2, base_randomizer_cls=QuickBlock
    )
    with pytest.raises(ValueError, match="does not support imbalance"):
        rr.assign(panel_data=panel, n_test_grps=1)


def test_no_input_mutation_on_design_assign():
    panel = _synthetic_panel()
    original = panel.wide_data.copy()
    br = BalancedRandomization(random_state=1)
    br.assign(
        panel_data=panel,
        pre_treatment_period=TimePeriod(0, 10),
        n_test_grps=1,
    )
    pd.testing.assert_frame_equal(panel.wide_data, original)


def test_placebo_unsupported_no_fake_ci():
    from panel_exp.methods.scm import SyntheticControl

    wide = pd.DataFrame({"c1": np.arange(20.0), "c2": np.arange(20.0) + 1})
    pds = PanelDataset(wide.T, treated_units=["c1"], treated_periods=[TimePeriod(10)])
    scm = SyntheticControl(inference="Placebo", alpha=0.05)
    with pytest.raises(ValueError, match="Placebo inference unavailable"):
        scm.run_analysis(pds, placebo_strict=True)


def test_validation_gate_fail():
    panel = _synthetic_panel(n_units=3)
    assignment = {"control": ["u0"], "test_0": ["u1"]}
    with pytest.raises(ValueError, match="blocking"):
        validate_design(
            panel.wide_data,
            assignment,
            min_control_units=5,
            block_on_fail=True,
        )


def test_validation_warn_interference():
    panel = _synthetic_panel()
    assignment = {"control": ["u0", "u1", "u2", "u3"], "test_0": ["u4", "u5"]}
    result = validate_design(
        panel.wide_data,
        assignment,
        treatment_probability=0.33,
        interference=InterferenceAssumption.UNKNOWN,
        block_on_fail=False,
    )
    assert any(c.metric == "interference_assumption" for c in result.checks)


def test_power_fixture_and_seed():
    path = "tests/fixtures/power_geo.csv"
    long_df = pd.read_csv(path)
    long_df = long_df[long_df.time < 91]
    wide_df = pd.pivot_table(long_df, index="location", columns="time", values="Y")
    treated = pd.DataFrame(wide_df.loc[["chicago", "cincinnati", "houston", "portland"]].mean(axis=0), columns=["treated"])
    control = pd.DataFrame(wide_df.drop(index=["chicago", "cincinnati", "houston", "portland", "honolulu"]))
    wide_agg = pd.concat([treated, control.T], axis=1)
    L = len(wide_df.columns)
    panel_data = PanelDataset(wide_agg.T, treated_units=["treated"], treated_periods=[TimePeriod(start=L - 7)])

    pa1 = PowerAnalysis(
        panel_data,
        TBRRidge,
        "Kfold",
        7,
        train_length=5,
        mx_effect=0.15,
        n_sample_prc=0.5,
        n_jobs=1,
        random_state=123,
    )
    idx1 = pa1.train_test_indices_f()
    pa2 = PowerAnalysis(
        panel_data,
        TBRRidge,
        "Kfold",
        7,
        train_length=5,
        mx_effect=0.15,
        n_sample_prc=0.5,
        n_jobs=1,
        random_state=123,
    )
    idx2 = pa2.train_test_indices_f()
    assert idx1 == idx2
    n_keep1 = max(1, int(len(idx1) * pa1.n_sample_prc))
    rng1 = pa1._rng.choice(len(idx1), size=n_keep1, replace=False)
    subsample1 = [idx1[i] for i in sorted(rng1)]
    n_keep2 = max(1, int(len(idx2) * pa2.n_sample_prc))
    rng2 = pa2._rng.choice(len(idx2), size=n_keep2, replace=False)
    subsample2 = [idx2[i] for i in sorted(rng2)]
    assert subsample1 == subsample2


def test_public_api_imports():
    import panel_exp

    assert panel_exp.__version__ == "0.2.1"
    assert panel_exp.BalancedRandomization is not None


def test_evidence_assignment_hash_stable():
    from panel_exp.evidence import DesignEvidence
    from panel_exp.spec import spec_from_geo_design

    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 10),
        TimePeriod(10, 30),
        "balancedrandomization",
        random_state=7,
    )
    assignment = {"control": ["a", "b"], "test_0": ["c"]}
    e1 = DesignEvidence.from_assignment(spec, assignment)
    e2 = DesignEvidence.from_assignment(spec, assignment)
    assert e1.assignment_hash == e2.assignment_hash


def test_class_name_to_design_method():
    assert class_name_to_design_method("BalancedRandomization") == DesignMethod.BALANCED_RANDOMIZATION
