"""Tests for D5-DES-STAT-TIER1-RECHARACTERIZATION-001."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.design.assign import CompleteRandomization, StratifiedRandomization, greedy_match_markets
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.track_d_d5_des_stat_tier1_001 import ALL_WORLD_IDS, _world_context
from panel_exp.validation.track_d_d5_des_stat_tier1_recharacterization_001 import (
    ARTIFACT_ID,
    CORRECTED_DESIGNS,
    LEGACY_DESIGNS,
    MULTICELL_DESIGNS,
    MULTICELL_WORLD_IDS,
    RecharConfig,
    build_d5_des_stat_tier1_recharacterization_001,
    build_summary_payload,
    expected_run_matrix_size,
    write_artifact_atomic,
)

ALLOWED = {
    "tier1_recharacterized_corrected_defaults_no_promotion",
    "tier1_recharacterized_mixed_method_specific_restrictions",
    "tier1_recharacterized_with_remaining_blocking_failures",
    "tier1_recharacterization_inconclusive",
    "tier1_recharacterization_failed",
}

REPO = Path(__file__).resolve().parents[2]
SUMMARY = REPO / "docs/track_d/archives/D5_DES_STAT_TIER1_RECHARACTERIZATION_001_summary.json"


@pytest.fixture
def fast_cfg() -> RecharConfig:
    return RecharConfig(fast=True)


class TestRecharHarness:
    def test_fast_build_verdict(self, fast_cfg: RecharConfig) -> None:
        payload = build_d5_des_stat_tier1_recharacterization_001(fast_cfg)
        assert payload["artifact_id"] == ARTIFACT_ID
        assert payload["verdict"] in ALLOWED
        assert payload["runtime"]["total_attempted_runs"] == payload["runtime"]["expected_attempted_runs"]

    def test_full_run_count_matches_matrix(self) -> None:
        cfg = RecharConfig(fast=False)
        expected = expected_run_matrix_size(cfg)
        assert expected["total"] == 6500
        assert expected["single_cell_tier1"] == 4700
        assert expected["legacy_reference"] == 900
        assert expected["multicell_per_cell_only"] == 900
        payload = build_d5_des_stat_tier1_recharacterization_001(cfg)
        assert payload["runtime"]["total_attempted_runs"] == expected["total"]

    def test_all_corrected_designs_represented(self, fast_cfg: RecharConfig) -> None:
        payload = build_d5_des_stat_tier1_recharacterization_001(fast_cfg)
        labels = {r["design_label"] for r in payload["run_records"] if r["lane"] == "single_cell_tier1"}
        for spec in CORRECTED_DESIGNS:
            assert spec.label in labels

    def test_legacy_lanes_represented(self, fast_cfg: RecharConfig) -> None:
        payload = build_d5_des_stat_tier1_recharacterization_001(fast_cfg)
        labels = {r["design_label"] for r in payload["run_records"] if r["lane"] == "legacy_reference"}
        assert "greedy_legacy" in labels
        assert "stratified_legacy" in labels

    def test_multicell_lane_separate(self, fast_cfg: RecharConfig) -> None:
        payload = build_d5_des_stat_tier1_recharacterization_001(fast_cfg)
        mc = [r for r in payload["run_records"] if r["lane"] == "multicell_per_cell_only"]
        assert mc
        assert all(r["n_test_grps"] >= 2 for r in mc)
        sc = [r for r in payload["run_records"] if r["lane"] == "single_cell_tier1"]
        assert all(r["n_test_grps"] == 1 for r in sc)

    def test_world_ids_present(self, fast_cfg: RecharConfig) -> None:
        payload = build_d5_des_stat_tier1_recharacterization_001(fast_cfg)
        worlds = {r["world_id"] for r in payload["run_records"]}
        assert "balanced_markets" in worlds or "weak_donor_pool" in worlds
        assert any(w in worlds for w in MULTICELL_WORLD_IDS[:2])

    def test_pairwise_comparisons_generated(self, fast_cfg: RecharConfig) -> None:
        payload = build_d5_des_stat_tier1_recharacterization_001(fast_cfg)
        assert len(payload["pairwise_comparisons"]) >= 1

    def test_legacy_vs_corrected_generated(self, fast_cfg: RecharConfig) -> None:
        payload = build_d5_des_stat_tier1_recharacterization_001(fast_cfg)
        assert "DES-001" in payload["legacy_vs_corrected"] or payload["legacy_vs_corrected"]

    def test_summary_schema(self, fast_cfg: RecharConfig) -> None:
        payload = build_d5_des_stat_tier1_recharacterization_001(fast_cfg)
        summary = build_summary_payload(payload)
        for key in (
            "artifact_id",
            "lanes",
            "aggregate_results",
            "legacy_vs_corrected",
            "pairwise_comparisons",
            "failure_summary",
            "balance_summary",
            "multicell_summary",
            "contract_guardrail_summary",
            "supersession",
            "verdict",
            "limitations",
        ):
            assert key in summary
        assert "run_records" not in summary

    def test_pooled_claims_blocked_multicell(self, fast_cfg: RecharConfig) -> None:
        payload = build_d5_des_stat_tier1_recharacterization_001(fast_cfg)
        assert payload["multicell_summary"]["pooled_claims_blocked"] is True

    def test_supersession_statement(self, fast_cfg: RecharConfig) -> None:
        payload = build_d5_des_stat_tier1_recharacterization_001(fast_cfg)
        assert payload["supersession"]["historical_evidence_retained"] is True
        assert "DES-001" in payload["supersession"]["supersedes_default_comparisons_for"]

    def test_failed_runs_preserved(self, fast_cfg: RecharConfig) -> None:
        payload = build_d5_des_stat_tier1_recharacterization_001(fast_cfg)
        failed = [r for r in payload["run_records"] if r["assignment_status"] == "failed"]
        assert payload["runtime"]["failed_runs"] == len(failed)

    def test_atomic_summary_write(self, fast_cfg: RecharConfig, tmp_path: Path) -> None:
        payload = build_d5_des_stat_tier1_recharacterization_001(fast_cfg)
        out = tmp_path / "summary.json"
        write_artifact_atomic(out, build_summary_payload(payload), overwrite=False)
        loaded = json.loads(out.read_text())
        assert loaded["verdict"] in ALLOWED

    @pytest.mark.skipif(not SUMMARY.exists(), reason="summary not generated")
    def test_committed_summary(self) -> None:
        summary = json.loads(SUMMARY.read_text())
        assert summary["artifact_id"] == ARTIFACT_ID


class TestRecharReproduction:
    def test_corrected_greedy_preserves_controls(self) -> None:
        from panel_exp.validation.track_d_d5_des_stat_tier1_001 import synthesize_panel

        ctx = _world_context("treatment_pool_exhaustion_world", RecharConfig(fast=True), treatment_probability=0.35)
        wide = synthesize_panel(ctx, 101)
        panel = PanelDataset(wide.copy())
        design = greedy_match_markets(
            treatment_probability=0.35,
            random_state=101,
            feasibility_policy="control_reservation",
            min_control_units=3,
        )
        assignment = design.assign(panel_data=panel, pre_treatment_period=TimePeriod(0, 30), n_test_grps=1)
        assert len(assignment["control"]) >= 3

    def test_legacy_greedy_may_violate_controls(self) -> None:
        from panel_exp.validation.track_d_d5_des_stat_tier1_001 import synthesize_panel

        ctx = _world_context("treatment_pool_exhaustion_world", RecharConfig(fast=True), treatment_probability=0.35)
        wide = synthesize_panel(ctx, 101)
        panel = PanelDataset(wide.copy())
        design = greedy_match_markets(
            treatment_probability=0.35,
            random_state=101,
            feasibility_policy="legacy",
            min_control_units=3,
        )
        assignment = design.assign(panel_data=panel, pre_treatment_period=TimePeriod(0, 30), n_test_grps=1)
        n_control = len(assignment["control"])
        n_units = panel.wide_data.shape[0]
        n_treated = len(assignment["test_0"])
        assert n_control < 3 or (n_units - n_control - n_treated) > 0

    def test_stratified_adaptive_on_poor_strata_world(self) -> None:
        from panel_exp.validation.track_d_d5_des_stat_tier1_001 import synthesize_panel

        cfg = RecharConfig(fast=True)
        from panel_exp.validation.track_d_d5_des_stat_tier1_001 import D5DesStatTier1Config

        tier1 = D5DesStatTier1Config(fast=True, n_pre=30, n_post=10, n_units=12)
        ctx = _world_context("stratification_poor_strata_world", tier1)
        wide = synthesize_panel(ctx, 202)
        panel = PanelDataset(wide.copy())
        design = StratifiedRandomization(
            treatment_probability=0.35, random_state=202, stratification_policy="adaptive_strata"
        )
        assignment = design.assign(
            panel_data=panel,
            pre_treatment_period=TimePeriod(0, 30),
            n_test_grps=1,
            n_percentiles=12,
        )
        assert design.last_stratification_metadata is not None
        assert assignment["control"]

    def test_multicell_pooled_blocked_metadata(self) -> None:
        from panel_exp.validation.track_d_d5_des_stat_tier1_001 import synthesize_panel

        wide = synthesize_panel(_world_context("balanced_markets", RecharConfig(fast=True)), 303)
        panel = PanelDataset(wide.copy())
        design = CompleteRandomization(
            treatment_probability=0.35,
            random_state=303,
            multicell_policy="control_reservation",
            min_control_units=3,
        )
        design.assign(panel_data=panel, pre_treatment_period=TimePeriod(0, 30), n_test_grps=2)
        meta = design.last_multicell_metadata
        assert meta is not None
        assert meta["pooled_claims_allowed"] is False
