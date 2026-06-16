"""Tests for D5-DES-STAT-GREEDY-FEASIBILITY-001."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.design.assign import greedy_match_markets
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.track_d_d5_des_stat_greedy_feasibility_001 import (
    ARTIFACT_ID,
    MIN_CONTROL_THRESHOLD,
    POLICY_SPECS,
    WORLD_IDS,
    GreedyFeasibilityConfig,
    build_d5_des_stat_greedy_feasibility_001,
    synthesize_panel,
    write_artifact_atomic,
    _world_spec,
)

ALLOWED_VERDICTS = {
    "greedy_feasibility_fixed_requires_statistical_followup",
    "greedy_feasibility_partially_fixed_with_restrictions",
    "greedy_infeasible_regimes_explicitly_blocked",
    "greedy_feasibility_characterized_no_safe_fix",
    "greedy_feasibility_harness_inconclusive",
    "greedy_feasibility_harness_failed",
}

REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_PATH = (
    REPO_ROOT / "docs" / "track_d" / "archives" / "D5_DES_STAT_GREEDY_FEASIBILITY_001_results.json"
)


@pytest.fixture
def fast_cfg() -> GreedyFeasibilityConfig:
    return GreedyFeasibilityConfig(fast=True)


def _tier1_exhaustion_panel(seed: int = 101) -> PanelDataset:
    spec = _world_spec("treatment_pool_exhaustion", 10, 0.35)
    wide = synthesize_panel(spec, seed)
    return PanelDataset(wide.copy())


class TestGreedyFeasibilityReproduction:
    def test_legacy_reproduces_control_floor_violation_at_tp_0_35(self) -> None:
        panel = _tier1_exhaustion_panel(101)
        design = greedy_match_markets(
            treatment_probability=0.35,
            random_state=101,
            min_control_units=MIN_CONTROL_THRESHOLD,
            feasibility_policy="legacy",
        )
        assignment = design.assign(
            panel_data=panel, pre_treatment_period=TimePeriod(0, 30), n_test_grps=1
        )
        n_control = len(assignment["control"])
        n_treated = len(assignment["test_0"])
        n_units = panel.wide_data.shape[0]
        unassigned = n_units - n_control - n_treated
        assert n_control < MIN_CONTROL_THRESHOLD or unassigned > 0

    def test_fixed_policy_preserves_minimum_controls(self) -> None:
        panel = _tier1_exhaustion_panel(101)
        design = greedy_match_markets(
            treatment_probability=0.35,
            random_state=101,
            min_control_units=MIN_CONTROL_THRESHOLD,
            feasibility_policy="control_reservation",
        )
        assignment = design.assign(
            panel_data=panel, pre_treatment_period=TimePeriod(0, 30), n_test_grps=1
        )
        assert len(assignment["control"]) >= MIN_CONTROL_THRESHOLD
        assert design.last_feasibility_metadata is not None
        assert design.last_feasibility_metadata["realized_n_control"] >= MIN_CONTROL_THRESHOLD

    @pytest.mark.parametrize("tp", [0.20, 0.35, 0.50])
    def test_fixed_no_silent_control_floor_violation(self, tp: float) -> None:
        spec = _world_spec("treatment_pool_exhaustion", 10, tp)
        wide = synthesize_panel(spec, 101)
        panel = PanelDataset(wide.copy())
        design = greedy_match_markets(
            treatment_probability=tp,
            random_state=101,
            min_control_units=MIN_CONTROL_THRESHOLD,
            feasibility_policy="control_reservation",
        )
        assignment = design.assign(
            panel_data=panel, pre_treatment_period=TimePeriod(0, 30), n_test_grps=1
        )
        assert len(assignment["control"]) >= MIN_CONTROL_THRESHOLD
        assert not (set(assignment["control"]) & set(assignment["test_0"]))

    def test_preflight_fail_rejects_infeasible(self) -> None:
        spec = _world_spec("balanced_feasible", 4, 0.50)
        wide = synthesize_panel(spec, 303)
        panel = PanelDataset(wide.copy())
        design = greedy_match_markets(
            treatment_probability=0.50,
            random_state=303,
            min_control_units=MIN_CONTROL_THRESHOLD,
            feasibility_policy="preflight_fail",
        )
        with pytest.raises(ValueError, match="infeasible"):
            design.assign(
                panel_data=panel, pre_treatment_period=TimePeriod(0, 30), n_test_grps=1
            )

    def test_feasibility_metadata_requested_vs_realized(self) -> None:
        panel = _tier1_exhaustion_panel(202)
        design = greedy_match_markets(
            treatment_probability=0.35,
            random_state=202,
            min_control_units=MIN_CONTROL_THRESHOLD,
            feasibility_policy="control_reservation",
        )
        design.assign(
            panel_data=panel, pre_treatment_period=TimePeriod(0, 30), n_test_grps=1
        )
        meta = design.last_feasibility_metadata
        assert meta is not None
        assert "requested_n_treated" in meta
        assert "realized_n_treated" in meta
        assert "realized_n_control" in meta
        assert "feasibility_policy" in meta

    def test_deterministic_fixed_seed_output(self) -> None:
        panel = _tier1_exhaustion_panel(404)
        kwargs = dict(
            treatment_probability=0.35,
            random_state=404,
            min_control_units=MIN_CONTROL_THRESHOLD,
            feasibility_policy="control_reservation",
        )
        a1 = greedy_match_markets(**kwargs).assign(
            panel_data=panel, pre_treatment_period=TimePeriod(0, 30), n_test_grps=1
        )
        a2 = greedy_match_markets(**kwargs).assign(
            panel_data=panel, pre_treatment_period=TimePeriod(0, 30), n_test_grps=1
        )
        assert {k: sorted(v) for k, v in a1.items()} == {k: sorted(v) for k, v in a2.items()}


class TestGreedyFeasibilityHarness:
    def test_fast_payload_schema(self, fast_cfg: GreedyFeasibilityConfig) -> None:
        payload = build_d5_des_stat_greedy_feasibility_001(fast_cfg)
        required = {
            "artifact_id",
            "artifact_version",
            "generated_at",
            "git_commit",
            "baseline_implementation",
            "candidate_policies",
            "config",
            "worlds",
            "seeds",
            "replicates",
            "run_records",
            "aggregate_results",
            "policy_comparisons",
            "failure_summary",
            "feasibility_summary",
            "contract_guardrail_summary",
            "selected_policy",
            "verdict",
            "limitations",
        }
        assert required <= set(payload.keys())
        assert payload["artifact_id"] == ARTIFACT_ID
        assert payload["verdict"] in ALLOWED_VERDICTS

    def test_all_policies_worlds_tps_represented(self, fast_cfg: GreedyFeasibilityConfig) -> None:
        payload = build_d5_des_stat_greedy_feasibility_001(fast_cfg)
        records = payload["run_records"]
        policies = {r["policy"] for r in records}
        worlds = {r["world_id"] for r in records}
        tps = {round(r["requested_tp"], 2) for r in records}
        assert policies == {p[1] for p in POLICY_SPECS}
        assert worlds >= set(WORLD_IDS[:3])
        assert len(tps) >= 2

    def test_failed_runs_preserved(self, fast_cfg: GreedyFeasibilityConfig) -> None:
        payload = build_d5_des_stat_greedy_feasibility_001(fast_cfg)
        failed = [r for r in payload["run_records"] if r["assignment_status"] == "failed"]
        assert payload["runtime"]["failed_runs"] == len(failed)

    def test_policy_comparisons_generated(self, fast_cfg: GreedyFeasibilityConfig) -> None:
        payload = build_d5_des_stat_greedy_feasibility_001(fast_cfg)
        assert isinstance(payload["policy_comparisons"], list)
        assert len(payload["policy_comparisons"]) >= 1

    def test_atomic_archive_write(self, fast_cfg: GreedyFeasibilityConfig, tmp_path: Path) -> None:
        payload = build_d5_des_stat_greedy_feasibility_001(fast_cfg)
        out = tmp_path / "test_archive.json"
        write_artifact_atomic(out, payload, overwrite=False)
        assert out.exists()
        loaded = json.loads(out.read_text())
        assert loaded["artifact_id"] == ARTIFACT_ID
        with pytest.raises(FileExistsError):
            write_artifact_atomic(out, payload, overwrite=False)

    def test_contract_guardrail_fields(self, fast_cfg: GreedyFeasibilityConfig) -> None:
        payload = build_d5_des_stat_greedy_feasibility_001(fast_cfg)
        ok = [r for r in payload["run_records"] if r["assignment_status"] == "success"]
        assert ok
        sample = ok[0]
        assert sample.get("contract_status") is not None
        assert sample.get("guardrail_status") is not None
        assert payload["contract_guardrail_summary"]["downstream_may_proceed"] is False

    @pytest.mark.skipif(not ARCHIVE_PATH.exists(), reason="Full archive not generated")
    def test_committed_archive_valid(self) -> None:
        payload = json.loads(ARCHIVE_PATH.read_text())
        assert payload["artifact_id"] == ARTIFACT_ID
        assert payload["verdict"] in ALLOWED_VERDICTS
        assert len(payload["run_records"]) > 100
        assert payload["failure_summary"].get("legacy_control_floor_violations", 0) > 0
