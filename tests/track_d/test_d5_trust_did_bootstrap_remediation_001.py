"""Tests for D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_trust_did_bootstrap_remediation_001 import (
    DIAGNOSTIC_WORLDS,
    RemediationConfig,
    _assign_units,
    _run_diagnostic,
    build_d5_trust_did_bootstrap_remediation_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_summary.json"
REPORT = _REPO / "docs/track_d/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_REPORT.md"

ALLOWED_VERDICTS = frozenset(
    {
        "did_bootstrap_production_miscentering_confirmed",
        "did_bootstrap_causal_interval_remediated_requires_reassessment",
        "did_bootstrap_parallel_trends_gated_restricted",
        "did_bootstrap_common_timing_only",
        "did_bootstrap_diagnostic_only",
        "did_bootstrap_not_interval_eligible",
        "did_bootstrap_remediation_inconclusive",
        "did_bootstrap_remediation_failed",
    }
)

REQUIRED_SUMMARY_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "config",
        "worlds",
        "effect_sizes",
        "timing_regimes",
        "parallel_trends_regimes",
        "serial_dependence_regimes",
        "bootstrap_policies",
        "run_counts",
        "point_estimate_results",
        "interval_results",
        "coverage_by_effect",
        "coverage_by_world",
        "coverage_by_timing",
        "coverage_by_parallel_trends_status",
        "coverage_by_serial_dependence",
        "bias_decomposition",
        "variance_decomposition",
        "bootstrap_centering_diagnostics",
        "bootstrap_diagnostics",
        "production_defect_assessment",
        "harness_defect_assessment",
        "policy_comparisons",
        "semantic_classification",
        "trustreport_eligibility_implications",
        "authorization_summary",
        "limitations",
        "verdict",
    }
)


def _fast_cfg() -> RemediationConfig:
    return RemediationConfig(fast=True, write_full_results_path=None)


@pytest.fixture(scope="module")
def fast_payload() -> dict:
    return build_d5_trust_did_bootstrap_remediation_001(_fast_cfg())


class TestD5TrustDidBootstrapRemediation001:
    def test_build_deterministic_excluding_timestamp(self, fast_payload: dict) -> None:
        a = dict(fast_payload)
        b = build_d5_trust_did_bootstrap_remediation_001(_fast_cfg())
        for payload in (a, b):
            payload.pop("generated_at", None)
            payload.pop("git_commit", None)
        assert a == b

    def test_required_world_count_full(self) -> None:
        assert len(DIAGNOSTIC_WORLDS) >= 18

    def test_assignment_correct_geometry(self) -> None:
        spec = DIAGNOSTIC_WORLDS[0]
        base = RECOVERY_SCENARIO_REGISTRY[spec.scenario_name]
        scenario = replace(
            base,
            random_state=20260619,
            n_geos=spec.n_geos,
            n_periods=spec.n_periods,
            treatment_start=spec.treatment_start,
            true_effect=0.0,
        )
        wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
        treated = _assign_units(
            wide, n_pre=28, seed=20260619, treatment_probability=0.35, mode="corrected_test_0"
        )
        assert 0 < len(treated) < wide.shape[0]

    def test_broken_assignment_all_treated(self) -> None:
        spec = DIAGNOSTIC_WORLDS[0]
        base = RECOVERY_SCENARIO_REGISTRY[spec.scenario_name]
        scenario = replace(
            base,
            random_state=20260619,
            n_geos=spec.n_geos,
            n_periods=spec.n_periods,
            treatment_start=spec.treatment_start,
            true_effect=0.0,
        )
        wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
        treated = _assign_units(
            wide, n_pre=28, seed=20260619, treatment_probability=0.35, mode="broken_groups_values"
        )
        control_units = [u for u in wide.index if u not in treated]
        assert len(treated) == wide.shape[0]
        assert len(control_units) == 0

    def test_remediation_harness_no_groups_values_collapse(self) -> None:
        cfg = _fast_cfg()
        assert cfg.assignment_mode == "corrected_test_0"

    def test_point_recovery_clean_parallel_trends(self) -> None:
        world = DIAGNOSTIC_WORLDS[0]
        row = _run_diagnostic(world, _fast_cfg(), replicate_id=0, seed=20260619, percent_effect=0.08)
        assert row.get("callable_status") == "callable_pass"
        assert row.get("sign_correct") is True
        assert row.get("control_count", 0) >= 4

    def test_fast_mode_has_feasible_runs(self, fast_payload: dict) -> None:
        total = fast_payload["failure_summary"]["total_runs"]
        failed = fast_payload["failure_summary"]["failed_runs"]
        assert failed < total

    def test_effect_sweep_separate_null_positive(self, fast_payload: dict) -> None:
        by_eff = fast_payload["coverage_by_effect"]
        assert "0.0" in by_eff
        assert "0.08" in by_eff

    def test_truth_scale_cumulative_level(self, fast_payload: dict) -> None:
        assert fast_payload["bias_decomposition"]["truth_scale_mismatch"] is False
        center = fast_payload["bootstrap_centering_diagnostics"]
        assert center["truth_scale"] == "cumulative_level"
        assert center["point_estimate_scale"] == "cumulative_level"

    def test_bootstrap_center_recorded(self, fast_payload: dict) -> None:
        center = fast_payload["bootstrap_centering_diagnostics"]
        assert center.get("bootstrap_mean_positive") is not None
        assert center.get("point_estimate_mean_positive") is not None

    def test_interval_center_recorded(self, fast_payload: dict) -> None:
        assert "mean_interval_center_error" in fast_payload["interval_results"]

    def test_production_miscentering_reproducible(self, fast_payload: dict) -> None:
        prod = fast_payload["production_defect_assessment"]
        assert prod["decision"] in (
            "production_defect_confirmed",
            "production_defect_not_confirmed",
            "production_defect_indeterminate",
        )
        if prod["decision"] == "production_defect_confirmed":
            assert fast_payload["variance_decomposition"]["oracle_recentered_positive_coverage"] >= 0.75

    def test_diagnostic_recenter_improves_when_defect_confirmed(self, fast_payload: dict) -> None:
        prod = fast_payload["production_defect_assessment"]
        oracle = fast_payload["policy_comparisons"]["B_diagnostic_recentered_interval"]["positive_coverage"]
        current = fast_payload["policy_comparisons"]["A_current_production_interval"]["positive_coverage"]
        if prod["decision"] == "production_defect_confirmed":
            assert oracle is not None and current is not None
            assert oracle > current

    def test_empirical_variance_recorded(self, fast_payload: dict) -> None:
        assert fast_payload["variance_decomposition"].get("mean_bootstrap_se") is not None

    def test_common_vs_staggered_timing(self, fast_payload: dict) -> None:
        assert "common" in fast_payload["coverage_by_timing"]
        staggered = next(w for w in DIAGNOSTIC_WORLDS if w.timing_pattern == "staggered")
        row = _run_diagnostic(staggered, _fast_cfg(), replicate_id=0, seed=20260619)
        assert row.get("callable_status") == "timing_blocked"

    def test_pretrend_regimes_separated(self, fast_payload: dict) -> None:
        by_pt = fast_payload["coverage_by_parallel_trends_status"]
        assert "holds" in by_pt
        assert "severe_violation" in by_pt

    def test_serial_dependence_separated(self, fast_payload: dict) -> None:
        by_serial = fast_payload["coverage_by_serial_dependence"]
        assert "clean_iid" in by_serial
        assert "serial_correlation" in by_serial

    def test_failures_preserved(self, fast_payload: dict) -> None:
        assert "failed_runs" in fast_payload["failure_summary"]

    def test_bootstrap_unit_recorded(self, fast_payload: dict) -> None:
        assert fast_payload["bootstrap_diagnostics"]["bootstrap_unit"] == "time_period_moving_block"

    def test_authorization_remains_false(self, fast_payload: dict) -> None:
        assert fast_payload["authorization_summary"]["trust_report_authorized"] is False
        assert fast_payload["authorization_summary"]["trust_report_authorized_count"] == 0
        assert fast_payload["authorization_summary"]["trust_report_ready"] is False
        assert fast_payload["trustreport_eligibility_implications"]["eligible_for_promotion"] is False

    def test_bias_decomposition_present(self, fast_payload: dict) -> None:
        decomp = fast_payload["bias_decomposition"]
        assert "undercoverage_driver_hypothesis" in decomp
        assert "components" in decomp

    def test_policy_comparisons_required(self, fast_payload: dict) -> None:
        policies = fast_payload["policy_comparisons"]
        for key in (
            "A_current_production_interval",
            "B_diagnostic_recentered_interval",
            "C_oracle_empirical_interval",
            "D_valid_parallel_trends_only",
            "E_common_timing_only",
            "F_serial_dependence_restricted",
        ):
            assert key in policies

    def test_verdict_in_taxonomy(self, fast_payload: dict) -> None:
        assert fast_payload["verdict"] in ALLOWED_VERDICTS

    def test_compact_summary_schema(self, fast_payload: dict) -> None:
        assert REQUIRED_SUMMARY_KEYS <= set(fast_payload.keys())

    def test_no_full_archive_in_summary(self, fast_payload: dict) -> None:
        assert "run_results" not in fast_payload

    def test_atomic_summary_write(self, tmp_path: Path) -> None:
        target = tmp_path / "summary.json"
        write_summary(target, cfg=_fast_cfg(), overwrite=True)
        assert target.is_file()
        assert json.loads(target.read_text())["artifact_id"] == "D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001"

    def test_overwrite_protection(self, tmp_path: Path) -> None:
        target = tmp_path / "summary.json"
        write_summary(target, cfg=_fast_cfg(), overwrite=True)
        with pytest.raises(FileExistsError):
            write_summary(target, cfg=_fast_cfg(), overwrite=False)

    def test_staggered_timing_blocked(self) -> None:
        staggered = next(w for w in DIAGNOSTIC_WORLDS if w.timing_pattern == "staggered")
        row = _run_diagnostic(staggered, _fast_cfg(), replicate_id=0, seed=20260619)
        assert row.get("callable_status") == "timing_blocked"

    def test_harness_defect_documented(self, fast_payload: dict) -> None:
        harness = fast_payload["harness_defect_assessment"]
        assert harness["harness_defect_confirmed"] is True
        assert harness["canonical_fix_artifact"] == "D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION"

    def test_harness_defect_separate_from_production(self, fast_payload: dict) -> None:
        assert fast_payload["harness_defect_assessment"]["fixed_in_this_branch"] is False
