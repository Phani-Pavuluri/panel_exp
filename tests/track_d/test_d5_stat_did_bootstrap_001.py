"""D5-STAT-DID-BOOTSTRAP-001 tests."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import pytest
from dataclasses import replace

from panel_exp.validation.track_d_d5_stat_did_bootstrap_001 import (
    D5StatDidBootstrap001Config,
    ESTIMAND_CONTRACT,
    REQUIRED_WORLD_IDS,
    _HISTORICAL_ARCHIVE,
    _assign_greedy_pre_period,
    build_d5_stat_did_bootstrap_001,
    preserve_historical_archive,
    write_artifact,
)
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

_REPO = Path(__file__).resolve().parents[2]
ARTIFACT = _REPO / "docs/track_d/archives/D5_STAT_DID_BOOTSTRAP_001_results.json"
REPORT = _REPO / "docs/track_d/D5_STAT_DID_BOOTSTRAP_001_REPORT.md"
HARNESS_SOURCE = _REPO / "panel_exp/validation/track_d_d5_stat_did_bootstrap_001.py"
CORRECTION_REPORT = _REPO / "docs/track_d/D5_STAT_DID_BOOTSTRAP_001_HARNESS_CORRECTION_REPORT.md"
DID_SOURCE = _REPO / "panel_exp/methods/DID.py"

ALLOWED_OVERALL = frozenset(
    {
        "characterization_pass_with_caveats",
        "characterization_mixed_requires_followup",
        "characterization_fail_requires_fix",
    }
)

ALLOWED_HARNESS_VERDICTS = frozenset(
    {
        "did_bootstrap_harness_corrected_canonical_baseline_established",
        "did_bootstrap_harness_corrected_production_miscoverage_confirmed",
        "did_bootstrap_harness_correction_inconclusive",
        "did_bootstrap_harness_correction_failed",
    }
)

AGG_KEYS = frozenset(
    {
        "n_replicates",
        "feasible_runs",
        "failed_runs",
        "callable_failure_rate",
        "effect_scale",
        "timing_regime",
        "parallel_trends_status",
        "serial_dependence_regime",
        "mean_point_estimate",
        "median_point_estimate",
        "mean_true_effect",
        "mean_bias",
        "mean_absolute_error",
        "rmse",
        "median_absolute_error",
        "sign_error_rate",
        "sign_accuracy",
        "null_false_positive_rate",
        "type_i_error",
        "coverage",
        "null_coverage",
        "positive_coverage",
        "negative_coverage",
        "mean_interval_width",
        "median_interval_width",
        "mean_bootstrap_center",
        "point_in_interval_rate",
        "interval_orientation_failure_rate",
        "negative_half_width_rate",
        "degenerate_interval_rate",
        "non_finite_output_rate",
        "notes",
    }
)

RUN_KEYS = frozenset(
    {
        "run_id",
        "world_id",
        "replicate_id",
        "replicate",
        "seed",
        "effect_size",
        "percent_effect",
        "effect_scale",
        "timing_regime",
        "parallel_trends_status",
        "serial_dependence_regime",
        "estimand_id",
        "callable_status",
        "failure_status",
        "failure_reason",
        "n_treated",
        "n_control",
        "assignment_valid",
        "assignment_failure_reason",
        "point_estimate",
        "true_effect",
        "bias",
        "absolute_error",
        "squared_error",
        "sign_correct",
        "interval_lower",
        "interval_upper",
        "interval_center",
        "interval_width",
        "interval_contains_truth",
        "contains_truth",
        "contains_zero",
        "interval_orientation_valid",
        "negative_half_width_detected",
        "finite_outputs",
        "bootstrap_mean",
        "bootstrap_median",
        "bootstrap_standard_error",
        "bootstrap_replicate_count",
        "point_minus_bootstrap_center",
        "exception_type",
        "exception_message",
    }
)

FORBIDDEN_REPORT = [
    r"\bis production-ready\b",
    r"\bis promoted\b",
    r"\bis trusted\b",
    r"\bgoverned uncertainty eligible\b",
    r"\bCalibrationSignal eligible\b",
    r"\bMMM ready for production\b",
    r"\bprimary evidence role\b",
    r"\bsecondary evidence role\b",
    r"\bis suitable for production\b",
]


def _strip_timestamp(payload: dict) -> dict:
    out = json.loads(json.dumps(payload))
    out.pop("generated_at", None)
    return out


def _fast_cfg() -> D5StatDidBootstrap001Config:
    return D5StatDidBootstrap001Config(fast=True)


@pytest.fixture(scope="module")
def fast_payload() -> dict:
    return build_d5_stat_did_bootstrap_001(_fast_cfg())


class TestD5StatDidBootstrap001:
    def test_no_groups_values_in_harness(self) -> None:
        text = HARNESS_SOURCE.read_text(encoding="utf-8")
        assert "for u in groups.values()" not in text
        assert "[u for units in groups.values()" not in text
        assert 'groups.get("test_0")' in text
        assert 'groups.get("control")' in text

    def test_assignment_explicit_test_and_control(self) -> None:
        scenario = replace(
            RECOVERY_SCENARIO_REGISTRY["did_parallel_trends_holds"],
            random_state=1,
            n_geos=16,
            n_periods=44,
            treatment_start=28,
            true_effect=0.0,
        )
        wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
        assignment = _assign_greedy_pre_period(
            wide, n_pre=28, seed=1, treatment_probability=0.35
        )
        assert assignment["n_treated"] > 0
        assert assignment["n_control"] > 0
        assert assignment["assignment_valid"] is True
        assert assignment["assignment_failure_reason"] is None
        assert not set(assignment["treated_units"]) & set(assignment["control_units"])

    def test_invalid_assignment_fails_explicitly(self) -> None:
        assignment = _assign_greedy_pre_period(
            __import__("pandas").DataFrame({"a": [1, 2]}),
            n_pre=1,
            seed=1,
            treatment_probability=0.35,
        )
        assert assignment["assignment_valid"] is False
        assert assignment["assignment_failure_reason"] is not None

    def test_estimand_contract_declared(self, fast_payload: dict) -> None:
        assert fast_payload["estimand_contract"] == ESTIMAND_CONTRACT
        assert ESTIMAND_CONTRACT["truth_scale"] == "cumulative_level"
        assert ESTIMAND_CONTRACT["point_estimate_scale"] == "cumulative_level"
        assert ESTIMAND_CONTRACT["interval_scale"] == "cumulative_level"

    def test_point_and_interval_scale_match_truth(self, fast_payload: dict) -> None:
        for row in fast_payload["run_results"]:
            if row.get("callable_status") != "callable_pass":
                continue
            assert row["effect_scale"] == "cumulative_level"
            assert row["estimand_id"] == ESTIMAND_CONTRACT["estimand_id"]
            assert row["true_effect"] is not None
            assert row["point_estimate"] is not None

    def test_common_timing_recorded(self, fast_payload: dict) -> None:
        for row in fast_payload["run_results"]:
            assert row["timing_regime"] == "common_simultaneous_adoption"
        assert fast_payload["summary"]["timing_regime"] == "common_simultaneous_adoption"

    def test_build_deterministic_excluding_timestamp(self) -> None:
        cfg = _fast_cfg()
        assert _strip_timestamp(build_d5_stat_did_bootstrap_001(cfg)) == _strip_timestamp(
            build_d5_stat_did_bootstrap_001(cfg)
        )

    def test_required_worlds_exist(self, fast_payload: dict) -> None:
        assert set(REQUIRED_WORLD_IDS) <= {w["world_id"] for w in fast_payload["worlds"]}
        assert set(REQUIRED_WORLD_IDS) <= set(fast_payload["aggregate_metrics"])

    def test_aggregate_metrics_per_world(self, fast_payload: dict) -> None:
        for wid in REQUIRED_WORLD_IDS:
            assert AGG_KEYS <= set(fast_payload["aggregate_metrics"][wid])

    def test_run_results_fields(self, fast_payload: dict) -> None:
        for row in fast_payload["run_results"]:
            assert RUN_KEYS <= set(row)
            if row.get("callable_status") == "callable_pass":
                assert row["n_treated"] > 0
                assert row["n_control"] > 0
                assert row["assignment_valid"] is True

    def test_null_and_positive_coverage_separate(self, fast_payload: dict) -> None:
        summary = fast_payload["summary"]
        assert "null_coverage" in summary
        assert "positive_coverage" in summary
        assert summary["null_coverage"] is not None
        assert summary["positive_coverage"] is not None
        null_world = fast_payload["aggregate_metrics"]["clean_parallel_null"]
        pos_world = fast_payload["aggregate_metrics"]["clean_parallel_positive_lift"]
        assert null_world["null_coverage"] is not None
        assert null_world["positive_coverage"] is None
        assert pos_world["positive_coverage"] is not None
        assert pos_world["null_coverage"] is None

    def test_bootstrap_center_metrics_recorded(self, fast_payload: dict) -> None:
        ok = [
            r
            for r in fast_payload["run_results"]
            if r.get("callable_status") == "callable_pass"
        ]
        assert ok
        for row in ok:
            assert row.get("bootstrap_replicate_count") is not None
            assert row.get("bootstrap_mean") is not None

    def test_failed_runs_preserved(self, fast_payload: dict) -> None:
        failed = [r for r in fast_payload["run_results"] if r["callable_status"] != "callable_pass"]
        assert len(fast_payload["failure_register"]) == len(failed)

    def test_harness_correction_metadata(self, fast_payload: dict) -> None:
        hc = fast_payload["harness_correction"]
        assert hc["correction_artifact_id"] == "D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION"
        assert hc["historical_evidence_retained"] is True
        assert "groups.values()" in hc["assignment_fix"]
        assert hc["does_not_supersede_production_bootstrap_behavior"] is True
        assert fast_payload["harness_correction_verdict"] in ALLOWED_HARNESS_VERDICTS

    def test_forbidden_flags_false(self, fast_payload: dict) -> None:
        for key, val in fast_payload["forbidden_flags"].items():
            assert val is False, key

    def test_interval_orientation_sane(self, fast_payload: dict) -> None:
        for row in fast_payload["run_results"]:
            lo = row.get("interval_lower")
            hi = row.get("interval_upper")
            if lo is not None and hi is not None:
                assert lo <= hi, row

    def test_no_negative_half_width(self, fast_payload: dict) -> None:
        for row in fast_payload["run_results"]:
            assert row.get("negative_half_width_detected") is not True

    def test_non_finite_rate_tracked(self, fast_payload: dict) -> None:
        for m in fast_payload["aggregate_metrics"].values():
            assert "non_finite_output_rate" in m

    def test_overall_verdict_allowed(self, fast_payload: dict) -> None:
        assert fast_payload["overall_verdict"] in ALLOWED_OVERALL

    def test_report_guardrail_wording(self) -> None:
        if not REPORT.is_file():
            pytest.skip("Run generator")
        text = REPORT.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_REPORT:
            assert re.search(pattern, text, re.I) is None, pattern

    def test_runtime_modest(self) -> None:
        t0 = time.perf_counter()
        build_d5_stat_did_bootstrap_001(_fast_cfg())
        assert time.perf_counter() - t0 < 180.0

    def test_historical_archive_preserved(self) -> None:
        preserve_historical_archive()
        assert _HISTORICAL_ARCHIVE.is_file()

    def test_pre_fix_canonical_archive_documents_production_miscoverage(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert (
            loaded["harness_correction_verdict"]
            == "did_bootstrap_harness_corrected_production_miscoverage_confirmed"
        )
        assert (loaded["summary"].get("positive_coverage") or 1.0) < 0.25

    def test_post_fix_build_improves_coverage(self) -> None:
        payload = build_d5_stat_did_bootstrap_001(_fast_cfg())
        assert (payload["summary"].get("positive_coverage") or 0) >= 0.5
        clean_null = payload["aggregate_metrics"]["clean_parallel_null"]
        assert (clean_null.get("null_coverage") or 0) >= 0.5

    def test_correction_report_exists(self) -> None:
        assert CORRECTION_REPORT.is_file()


def test_write_artifact_atomic_and_overwrite(tmp_path: Path) -> None:
    out = tmp_path / "did.json"
    write_artifact(out, cfg=_fast_cfg(), overwrite=True)
    assert out.is_file()
    with pytest.raises(FileExistsError):
        write_artifact(out, cfg=_fast_cfg(), overwrite=False)
