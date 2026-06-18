"""Tests for D5-TRUST-SCM-JK-COVERAGE-REMEDIATION-001."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.track_d_d5_trust_scm_jk_coverage_remediation_001 import (
    DIAGNOSTIC_WORLDS,
    RemediationConfig,
    _assign_greedy,
    build_d5_trust_scm_jk_coverage_remediation_001,
    write_summary,
)
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from dataclasses import replace

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/D5_TRUST_SCM_JK_COVERAGE_REMEDIATION_001_summary.json"
REPORT = _REPO / "docs/track_d/D5_TRUST_SCM_JK_COVERAGE_REMEDIATION_001_REPORT.md"

ALLOWED_VERDICTS = frozenset(
    {
        "scm_jk_causal_interval_remediated_requires_reassessment",
        "scm_jk_eligible_as_null_monitor_only",
        "scm_jk_diagnostic_only_not_interval_eligible",
        "scm_jk_support_gated_restricted",
        "scm_jk_remediation_inconclusive",
        "scm_jk_remediation_failed",
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
        "donor_regimes",
        "run_counts",
        "point_estimate_results",
        "interval_results",
        "coverage_by_effect",
        "coverage_by_world",
        "coverage_by_donor_regime",
        "bias_decomposition",
        "variance_decomposition",
        "pre_fit_relationships",
        "failure_summary",
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


@pytest.mark.skipif(cvxpy_osqp_skip_reason() is not None, reason="cvxpy/osqp required")
class TestD5TrustScmJkCoverageRemediation001:
    def test_build_deterministic_excluding_timestamp(self) -> None:
        a = build_d5_trust_scm_jk_coverage_remediation_001(_fast_cfg())
        b = build_d5_trust_scm_jk_coverage_remediation_001(_fast_cfg())
        a.pop("generated_at", None)
        b.pop("generated_at", None)
        assert a == b

    def test_required_world_count_full(self) -> None:
        assert len(DIAGNOSTIC_WORLDS) >= 18

    def test_assignment_uses_test_group_only(self) -> None:
        spec = DIAGNOSTIC_WORLDS[0]
        base = RECOVERY_SCENARIO_REGISTRY[spec.scenario_name]
        scenario = replace(
            base,
            random_state=20260617,
            n_geos=spec.n_geos,
            n_periods=spec.n_periods,
            treatment_start=spec.treatment_start,
            true_effect=0.0,
        )
        wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
        treated = _assign_greedy(wide, n_pre=28, seed=20260617, treatment_probability=0.35)
        assert 0 < len(treated) < wide.shape[0]

    def test_fast_mode_has_feasible_runs(self) -> None:
        payload = build_d5_trust_scm_jk_coverage_remediation_001(_fast_cfg())
        assert payload["failure_summary"]["failed_runs"] < payload["failure_summary"]["total_runs"]

    def test_effect_sweep_separate_null_positive(self) -> None:
        payload = build_d5_trust_scm_jk_coverage_remediation_001(_fast_cfg())
        by_eff = payload["coverage_by_effect"]
        assert "0.0" in by_eff
        assert "0.08" in by_eff
        assert "coverage_level" in by_eff["0.0"]
        assert "coverage_level" in by_eff["0.08"]

    def test_authorization_remains_false(self) -> None:
        payload = build_d5_trust_scm_jk_coverage_remediation_001(_fast_cfg())
        assert payload["authorization_summary"]["trust_report_authorized"] is False
        assert payload["trustreport_eligibility_implications"]["eligible_for_promotion"] is False

    def test_bias_decomposition_present(self) -> None:
        payload = build_d5_trust_scm_jk_coverage_remediation_001(_fast_cfg())
        decomp = payload["bias_decomposition"]
        assert "undercoverage_driver_hypothesis" in decomp
        assert "percent_scale_mismatch_dominant" in decomp

    def test_policy_comparisons_include_oracle_diagnostic(self) -> None:
        payload = build_d5_trust_scm_jk_coverage_remediation_001(_fast_cfg())
        policies = payload["policy_comparisons"]
        assert "A_current_unit_jackknife" in policies
        assert "oracle_centered_diagnostic" in policies

    def test_verdict_in_taxonomy(self) -> None:
        payload = build_d5_trust_scm_jk_coverage_remediation_001(_fast_cfg())
        assert payload["verdict"] in ALLOWED_VERDICTS

    def test_compact_summary_schema(self) -> None:
        payload = build_d5_trust_scm_jk_coverage_remediation_001(_fast_cfg())
        assert REQUIRED_SUMMARY_KEYS <= set(payload.keys())

    def test_no_full_archive_in_repo_after_write(self) -> None:
        write_summary(SUMMARY, cfg=_fast_cfg())
        data = json.loads(SUMMARY.read_text())
        assert "run_results" not in data
        assert data["authorization_summary"]["trust_report_authorized"] is False

    def test_atomic_summary_write(self, tmp_path: Path) -> None:
        target = tmp_path / "summary.json"
        write_summary(target, cfg=_fast_cfg())
        assert target.is_file()
        assert json.loads(target.read_text())["artifact_id"] == "D5-TRUST-SCM-JK-COVERAGE-REMEDIATION-001"

    def test_report_exists(self) -> None:
        assert REPORT.is_file()
