"""D5-POW-001a power vs SCM JK readout alignment tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_pow_001a import (
    D5Pow001aConfig,
    _aggregated_power_panel,
    _assign_greedy_pre_period,
    run_d5_pow_001a,
    run_one_replicate,
    write_artifact,
)
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_POW_001a_results.json"
)


class TestD5Pow001aPowerReadoutAlignment:
    def test_assignment_and_aggregate(self) -> None:
        scenario = RECOVERY_SCENARIO_REGISTRY["scm_low_signal"]
        world = SyntheticWorld.generate(scenario)
        wide = world.to_panel_dataset().wide_data
        treated = _assign_greedy_pre_period(wide, n_pre=30, seed=1, treatment_probability=0.4)
        agg = _aggregated_power_panel(wide, treated)
        assert list(agg.wide_data.index) == ["treated", "control"]
        assert agg.treated_units == ["treated"]

    def test_one_replicate_runs(self) -> None:
        cfg = D5Pow001aConfig(
            n_mc=2,
            effect_grid=(-0.08, 0.0, 0.08),
            include_power_analysis_mde=False,
        )
        row = run_one_replicate(cfg, seed=cfg.random_state_base)
        assert row["n_treated"] >= 1
        assert "effect_grid_corr_tbr" in row
        assert "tbr_curve" in row

    def test_characterization_runs(self) -> None:
        payload = run_d5_pow_001a(
            D5Pow001aConfig(
                n_mc=4,
                effect_grid=(-0.08, 0.0, 0.08),
                include_power_analysis_mde=False,
            )
        )
        assert payload["artifact_id"] == "D5-POW-001a"
        assert payload["proxy_verdict"] in {
            "rough_proxy",
            "conservative_proxy",
            "optimistic_proxy",
            "unrelated_misleading",
            "narrow_diagnostics_only",
        }
        assert payload["calibration_eligibility_changed"] is False

    def test_committed_artifact_schema(self) -> None:
        if not ARTIFACT_PATH.is_file():
            pytest.skip("Run D5-POW-001a generator to create committed artifact")
        loaded = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-POW-001a"
        assert "proxy_verdict" in loaded
        assert "pooled_detection_curves" in loaded
        assert "effect_response_8pct_tbr" in loaded["primary_metrics"]
