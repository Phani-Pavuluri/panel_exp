"""DID interval policy — explicit unsupported relative-ATT calibration contract."""

from __future__ import annotations

import pytest

from panel_exp.validation.did_interval_policy import (
    DID_INTERVAL_POLICY,
    DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED,
    build_did_interval_policy,
    is_did_recovery_config,
    nominal_calibration_ineligible_reason,
)
from panel_exp.validation.nominal_calibration import (
    is_nominal_calibration_eligible_config,
    payload_eligible_for_nominal_calibration,
    run_nominal_calibration_check,
)
from panel_exp.validation.production_nominal_calibration import (
    run_production_nominal_calibration,
)
from panel_exp.validation.recovery_intervals import (
    INTERVAL_ESTIMAND_CUMULATIVE_ATT,
    extract_recovery_interval,
)
from panel_exp.validation.recovery_runner import RecoveryRunner
from panel_exp.validation.runner import _relative_ci


def test_policy_metadata_fields():
    policy = build_did_interval_policy()
    assert policy["point_estimand"] == "relative_att_post"
    assert policy["interval_estimand"] == INTERVAL_ESTIMAND_CUMULATIVE_ATT
    assert policy["relative_att_interval_supported"] is False
    assert "cumulative" in policy["reason"].lower() or "absolute" in policy["reason"].lower()
    assert policy["comparable_to_relative_att_post"]["treatment_ci"] is False


def test_did_results_include_policy_on_run_analysis():
    from panel_exp.methods.DID import DID
    from panel_exp.panel_data import PanelDataset, TimePeriod

    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(0)
    wide = rng.normal(100, 5, size=(8, 24))
    df = pd.DataFrame(
        wide,
        index=[f"u{i}" for i in range(8)],
        columns=pd.date_range("2020-01-01", periods=24, freq="W"),
    )
    t0 = 18
    panel = PanelDataset(
        df,
        treated_periods=[TimePeriod(df.columns[t0], df.columns[-1])],
        treated_units=["u0"],
    )
    did = DID()
    did.n_bootstrap = 15
    results = did.run_analysis(panel, multiple_treated="pooled")
    assert "did_interval_policy" in results
    assert results["did_interval_policy"]["relative_att_interval_supported"] is False


def test_inference_metadata_includes_policy():
    from panel_exp.methods.DID import DID
    from panel_exp.panel_data import PanelDataset, TimePeriod

    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(1)
    wide = rng.normal(50, 3, size=(6, 20))
    df = pd.DataFrame(
        wide,
        index=[f"u{i}" for i in range(6)],
        columns=pd.date_range("2021-01-01", periods=20, freq="W"),
    )
    panel = PanelDataset(
        df,
        treated_periods=[TimePeriod(df.columns[14], df.columns[-1])],
        treated_units=["u0"],
    )
    did = DID()
    did.run_analysis(panel, multiple_treated="pooled")
    meta = did.get_detailed_results()
    assert "did_interval_policy" in meta
    assert meta["did_interval_policy"]["relative_att_interval_supported"] is False


def test_recovery_interval_did_unsupported_reason():
    from panel_exp.methods.DID import DID
    from panel_exp.panel_data import PanelDataset, TimePeriod

    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(2)
    wide = rng.normal(80, 4, size=(8, 22))
    df = pd.DataFrame(
        wide,
        index=[f"u{i}" for i in range(8)],
        columns=pd.date_range("2020-06-01", periods=22, freq="W"),
    )
    panel = PanelDataset(
        df,
        treated_periods=[TimePeriod(df.columns[16], df.columns[-1])],
        treated_units=["u0"],
    )
    did = DID()
    did.n_bootstrap = 12
    did.run_analysis(panel, multiple_treated="pooled")
    ext = extract_recovery_interval(
        did,
        panel,
        alpha=0.05,
        significance_from_ci=False,
        supports_significance=True,
    )
    assert ext.unavailable_reason == DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED
    assert ext.interval_aligned is False
    assert ext.ci_lower is None and ext.ci_upper is None


@pytest.mark.slow
def test_did_bootstrap_nominal_calibration_ineligible():
    out = run_nominal_calibration_check(
        "DID_Bootstrap",
        "recovery_null_effect",
        n_simulations=2,
        random_state=0,
    )
    assert out["eligible_for_nominal_calibration"] is False
    assert is_nominal_calibration_eligible_config("DID_Bootstrap") is False
    reason = nominal_calibration_ineligible_reason(
        "DID_Bootstrap",
        {
            "interval_estimand": INTERVAL_ESTIMAND_CUMULATIVE_ATT,
            "intervals_expected": True,
            "coverage_unavailable_reason": DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED,
        },
    )
    assert reason == DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED


@pytest.mark.slow
def test_production_calibration_skips_did_bootstrap():
    report = run_production_nominal_calibration(
        estimator_configs=("DID_Bootstrap",),
        scenarios=("recovery_null_effect",),
        n_simulations=2,
        random_seeds=(0,),
    )
    assert report["per_seed_runs"] == []
    assert report["skipped"][0]["ineligible_reason"] == DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED


def test_no_relative_ci_scaling_used_in_recovery_path():
    """``runner._relative_ci`` exists for legacy validation only; recovery uses extract_recovery_interval."""
    from panel_exp.methods.DID import DID
    from panel_exp.panel_data import PanelDataset, TimePeriod

    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(3)
    wide = rng.normal(90, 2, size=(6, 18))
    df = pd.DataFrame(
        wide,
        index=[f"u{i}" for i in range(6)],
        columns=pd.date_range("2020-01-01", periods=18, freq="W"),
    )
    panel = PanelDataset(
        df,
        treated_periods=[TimePeriod(df.columns[12], df.columns[-1])],
        treated_units=["u0"],
    )
    did = DID()
    did.run_analysis(panel, multiple_treated="pooled")
    lo, hi = _relative_ci(did, panel)
    assert lo is not None and hi is not None
    ext = extract_recovery_interval(
        did,
        panel,
        alpha=0.05,
        significance_from_ci=False,
        supports_significance=True,
    )
    assert ext.ci_lower is None
    assert ext.unavailable_reason == DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED


def test_recovery_runner_payload_marks_did_interval_estimand():
    payload = RecoveryRunner(
        "DID_Bootstrap",
        "recovery_null_effect",
        n_simulations=2,
        random_state=4,
    ).run()
    assert payload["interval_estimand"] == INTERVAL_ESTIMAND_CUMULATIVE_ATT
    assert not payload_eligible_for_nominal_calibration("DID_Bootstrap", payload)
    assert is_did_recovery_config("DID_Bootstrap")


def test_validation_coverage_doc_mentions_unsupported_relative_interval():
    from pathlib import Path

    text = Path("docs/VALIDATION_COVERAGE.md").read_text(encoding="utf-8")
    assert "Relative ATT interval calibration" in text
    assert "unsupported" in text.lower()
    assert "did_relative_att_interval_unsupported" in text or "did_interval_policy" in text


def test_roadmap_phase6_resolved_in_docs():
    from pathlib import Path

    text = Path("docs/ROADMAP_V3.md").read_text(encoding="utf-8")
    assert "Phase 6 status" in text
    assert "unsupported contract" in text.lower() or "explicit unsupported" in text.lower()


def test_policy_constant_matches_builder():
    assert build_did_interval_policy() == dict(DID_INTERVAL_POLICY)
