"""D5-POW-001d window sensitivity tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from panel_exp.design.assign import greedy_match_markets
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

from panel_exp.validation.track_d_d5_pow_001d import (
    D5Pow001dConfig,
    TRACK_E_SUITABILITY_DIAGNOSTICS,
    WindowSpec,
    run_d5_pow_001d,
    run_one_replicate,
    write_artifact,
    _assign_greedy,
)

ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_POW_001d_results.json"
)


class TestD5Pow001dWindows:
    def test_assignment_uses_production_contract(self) -> None:
        cfg = D5Pow001dConfig()
        wide = SyntheticWorld.generate(RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name]).to_panel_dataset().wide_data
        helper_treated = _assign_greedy(wide, n_pre=cfg.baseline_window.train_length, seed=cfg.random_state_base, treatment_probability=cfg.treatment_probability)
        design = greedy_match_markets(func_to_optimize="corr", treatment_probability=cfg.treatment_probability, random_state=cfg.random_state_base)
        assigned_panel = design.assign(panel_data=PanelDataset(wide.copy()), pre_treatment_period=TimePeriod(0, cfg.baseline_window.train_length), n_test_grps=1)
        assert helper_treated == list(assigned_panel.treated_units)
        assert len(helper_treated) >= 1
        assert len(helper_treated) < len(wide.index)
        assert len(wide.index) - len(helper_treated) >= cfg.min_control_units

    def test_track_e_diagnostics_defined(self) -> None:
        assert len(TRACK_E_SUITABILITY_DIAGNOSTICS) >= 5

    def test_one_replicate_multi_window(self) -> None:
        row = run_one_replicate(
            D5Pow001dConfig(
                n_mc=2,
                window_grid=(WindowSpec(24, 8), WindowSpec(28, 8)),
                effect_grid=(0.0, 0.08),
            ),
            seed=20260604,
        )
        assert len(row["windows"]) >= 2
        assert row["windows"][0]["design_context"]["design_method_id"] == "greedy_match_markets"
        assert all(window["design_context"]["n_control_markets"] >= 2 for window in row["windows"])

    def test_characterization_runs(self) -> None:
        payload = run_d5_pow_001d(
            D5Pow001dConfig(
                n_mc=4,
                window_grid=(WindowSpec(24, 6), WindowSpec(28, 8)),
                effect_grid=(0.0, 0.08),
            )
        )
        assert payload["artifact_id"] == "D5-POW-001d"
        assert payload["window_sensitivity_verdict"] in {
            "stable",
            "moderately_sensitive",
            "unstable",
            "fixed_window_preferred",
        }
        assert payload["calibration_eligibility_changed"] is False

    def test_committed_artifact_schema(self) -> None:
        if not ARTIFACT_PATH.is_file():
            pytest.skip("Run D5-POW-001d generator to create committed artifact")
        loaded = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-POW-001d"
        assert "by_window_summary" in loaded
        assert "track_e_suitability_diagnostics" in loaded
