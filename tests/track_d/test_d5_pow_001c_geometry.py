"""D5-POW-001c unit vs 2-row aggregation geometry tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from panel_exp.design.assign import greedy_match_markets
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

from panel_exp.validation.track_d_d5_pow_001c import (
    D5Pow001cConfig,
    DESIGN_METHODS_FOR_001E,
    _assign_greedy_pre_period,
    run_d5_pow_001c,
    run_one_replicate,
)

ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_POW_001c_results.json"
)


class TestD5Pow001cGeometry:
    def test_design_methods_table_present(self) -> None:
        assert any(m["design_method_id"] == "greedy_match_markets" for m in DESIGN_METHODS_FOR_001E)
        greedy = next(m for m in DESIGN_METHODS_FOR_001E if m["design_method_id"] == "greedy_match_markets")
        assert greedy["in_d5_pow_001c"] is True

    def test_one_replicate_design_aware(self) -> None:
        row = run_one_replicate(
            D5Pow001cConfig(n_mc=2, effect_grid=(0.0, 0.08)),
            seed=20260603,
        )
        assert row["design_context"]["design_method_id"] == "greedy_match_markets"
        assert row["geometry_loss"]["n_markets_collapsed"] >= 1
        cfg = D5Pow001cConfig(n_mc=2, effect_grid=(0.0, 0.08))
        assert row["design_context"]["n_control_markets"] >= cfg.min_control_units
        assert "unit_scm_jk" in row
        assert "agg2_tbr_kfold" in row

    def test_assignment_uses_production_contract(self) -> None:
        cfg = D5Pow001cConfig()
        wide = SyntheticWorld.generate(RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name]).to_panel_dataset().wide_data
        helper_treated = _assign_greedy_pre_period(
            wide, n_pre=cfg.train_length, seed=cfg.random_state_base, treatment_probability=cfg.treatment_probability
        )
        design = greedy_match_markets(func_to_optimize="corr", treatment_probability=cfg.treatment_probability, random_state=cfg.random_state_base)
        assignment = design.assign(panel_data=PanelDataset(wide.copy()), pre_treatment_period=TimePeriod(0, cfg.train_length), n_test_grps=1)
        assert helper_treated == list(assignment["test_0"])
        assert len(helper_treated) >= 1
        assert len(helper_treated) < len(wide.index)
        assert len(assignment["control"]) >= cfg.min_control_units
        assert set(helper_treated).isdisjoint(assignment["control"])

    def test_characterization_runs(self) -> None:
        payload = run_d5_pow_001c(D5Pow001cConfig(n_mc=4, effect_grid=(0.0, 0.08)))
        assert payload["artifact_id"] == "D5-POW-001c"
        assert payload["aggregation_proxy_verdict"] in {
            "acceptable",
            "optimistic",
            "conservative",
            "invalid",
            "narrow_diagnostics_only",
        }
        assert payload["calibration_eligibility_changed"] is False
        assert len(payload["design_methods_for_001e"]) >= 3

    def test_committed_artifact_schema(self) -> None:
        if not ARTIFACT_PATH.is_file():
            pytest.skip("Run D5-POW-001c generator to create committed artifact")
        loaded = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-POW-001c"
        assert "design_context_reference" in loaded
        assert "design_methods_for_001e" in loaded
