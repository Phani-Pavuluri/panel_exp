"""D5-POW-001b SCM+JK null-monitor and detection semantics tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_pow_001b import (
    D5Pow001bConfig,
    _scm_jk_readout_metrics,
    run_d5_pow_001b,
    run_one_replicate,
    write_artifact,
)
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.track_d_d5_pow_001b import (
    _assign_greedy_pre_period,
    _mean_treated_baseline,
)

ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_POW_001b_results.json"
)


class TestD5Pow001bScmJkNullMonitor:
    def test_wrong_vs_correct_detection_differ(self) -> None:
        scenario = RECOVERY_SCENARIO_REGISTRY["scm_low_signal"]
        world = SyntheticWorld.generate(scenario)
        wide = world.to_panel_dataset().wide_data
        treated = _assign_greedy_pre_period(wide, n_pre=28, seed=1, treatment_probability=0.35)
        end = 36
        panel = PanelDataset(
            wide.iloc[:, :end],
            treated_periods=[TimePeriod(28, 35) for _ in treated],
            treated_units=treated,
        )
        mv = _mean_treated_baseline(panel)
        m = _scm_jk_readout_metrics(panel, percent_effect=0.0, mean_value=mv, alpha=0.05, test_length=8)
        assert m["detected_wrong_001a"] != m["detected_correct"] or (
            m["covers_zero_wrong_001a"] != m["covers_zero_correct"]
        )

    def test_one_replicate_runs(self) -> None:
        cfg = D5Pow001bConfig(n_mc=2, effect_grid=(0.0, 0.04, 0.08))
        row = run_one_replicate(cfg, seed=cfg.random_state_base)
        assert "by_effect" in row
        assert 0.0 in row["by_effect"]

    def test_characterization_runs(self) -> None:
        payload = run_d5_pow_001b(D5Pow001bConfig(n_mc=4, effect_grid=(0.0, 0.04, 0.08)))
        assert payload["artifact_id"] == "D5-POW-001b"
        assert payload["pow_verdict"] in {
            "null_monitor_only",
            "requires_readout_aligned_power_metric",
            "supports_mde_with_caveats",
            "invalid_interval_detection_criterion",
        }
        assert payload["calibration_eligibility_changed"] is False
        assert payload["interval_excludes_zero_valid_for_scm_jk"] is False

    def test_committed_artifact_schema(self) -> None:
        if not ARTIFACT_PATH.is_file():
            pytest.skip("Run D5-POW-001b generator to create committed artifact")
        loaded = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-POW-001b"
        assert "degeneracy_attribution" in loaded
        assert "pooled_by_effect" in loaded
