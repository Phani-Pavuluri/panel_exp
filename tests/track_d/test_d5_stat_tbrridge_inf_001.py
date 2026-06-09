"""D5-STAT-TBRRIDGE-INF-001 tests."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_stat_tbrridge_inf_001 import (
    D5StatTbrridgeInf001Config,
    INFERENCE_PATHS,
    REQUIRED_WORLD_IDS,
    build_d5_stat_tbrridge_inf_001,
    write_artifact,
)

_REPO = Path(__file__).resolve().parents[2]
ARTIFACT = _REPO / "docs/track_d/archives/D5_STAT_TBRRIDGE_INF_001_results.json"
REPORT = _REPO / "docs/track_d/D5_STAT_TBRRIDGE_INF_001_REPORT.md"

ALLOWED_OVERALL = frozenset(
    {
        "characterization_pass_with_caveats",
        "characterization_mixed_requires_followup",
        "characterization_fail_requires_fix",
    }
)

PATH_METRIC_KEYS = frozenset(
    {
        "method_combination",
        "inference_path",
        "geometry",
        "n_replicates",
        "feasible_runs",
        "failed_runs",
        "skipped_runs",
        "callable_failure_rate",
        "mean_point_estimate",
        "median_point_estimate",
        "mean_true_effect",
        "mean_bias",
        "mean_absolute_error",
        "rmse",
        "median_absolute_error",
        "sign_error_rate",
        "null_false_positive_rate",
        "directional_false_signal_rate",
        "coverage",
        "mean_interval_width",
        "median_interval_width",
        "interval_orientation_failure_rate",
        "negative_half_width_rate",
        "degenerate_interval_rate",
        "non_finite_output_rate",
        "split_policy_recorded",
        "leakage_guard_status",
        "notes",
    }
)

RUN_KEYS = frozenset(
    {
        "world_id",
        "replicate_id",
        "seed",
        "method_combination",
        "inference_path",
        "geometry",
        "callable_status",
        "skip_reason",
        "point_estimate",
        "true_effect",
        "bias",
        "absolute_error",
        "squared_error",
        "sign_correct",
        "interval_present",
        "interval_lower",
        "interval_upper",
        "interval_width",
        "interval_contains_truth",
        "interval_orientation_valid",
        "negative_half_width_detected",
        "finite_outputs",
        "split_policy",
        "leakage_warning",
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
    r"\bgoverned uncertainty\b",
    r"\bsuitable\b",
]


def _strip_timestamp(payload: dict) -> dict:
    out = json.loads(json.dumps(payload))
    out.pop("generated_at", None)
    return out


def _fast_cfg() -> D5StatTbrridgeInf001Config:
    return D5StatTbrridgeInf001Config(n_replicates=2, n_replicates_slow=2)


@pytest.fixture(scope="module")
def fast_payload() -> dict:
    return build_d5_stat_tbrridge_inf_001(_fast_cfg())


class TestD5StatTbrridgeInf001:
    def test_build_deterministic_excluding_timestamp(self) -> None:
        cfg = _fast_cfg()
        assert _strip_timestamp(build_d5_stat_tbrridge_inf_001(cfg)) == _strip_timestamp(
            build_d5_stat_tbrridge_inf_001(cfg)
        )

    def test_required_worlds_exist(self, fast_payload: dict) -> None:
        assert set(REQUIRED_WORLD_IDS) <= {w["world_id"] for w in fast_payload["worlds"]}
        worlds_in_metrics = {m["world_id"] for m in fast_payload["path_metrics"]}
        assert set(REQUIRED_WORLD_IDS) <= worlds_in_metrics

    def test_inference_path_records_exist(self, fast_payload: dict) -> None:
        paths = {p.path_id for p in INFERENCE_PATHS}
        metrics_paths = {m["inference_path"] for m in fast_payload["path_metrics"]}
        assert paths <= metrics_paths
        assert fast_payload["skip_register"]
        for entry in fast_payload["skip_register"]:
            assert entry.get("skip_reason") is not None or entry.get("smoke_status") == "callable_pass"

    def test_run_results_fields(self, fast_payload: dict) -> None:
        for row in fast_payload["run_results"]:
            assert RUN_KEYS <= set(row)

    def test_forbidden_flags_false(self, fast_payload: dict) -> None:
        for key, val in fast_payload["forbidden_flags"].items():
            assert val is False, key

    def test_no_governed_uncertainty_claim(self, fast_payload: dict) -> None:
        assert fast_payload["forbidden_flags"]["governed_uncertainty_allowed"] is False
        assert fast_payload["forbidden_flags"]["causal_uncertainty_claim_allowed"] is False
        blob = json.dumps(fast_payload)
        assert "governed uncertainty" not in blob.lower()

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
        for m in fast_payload["path_metrics"]:
            assert "non_finite_output_rate" in m

    def test_leakage_register_exists(self, fast_payload: dict) -> None:
        assert fast_payload["leakage_register"]
        for entry in fast_payload["leakage_register"]:
            assert entry.get("inference_path")
            assert entry.get("split_policy_recorded")

    def test_skipped_paths_have_reasons(self, fast_payload: dict) -> None:
        for entry in fast_payload["skip_register"]:
            if entry.get("smoke_status") == "skipped":
                assert entry.get("skip_reason")

    def test_overall_verdict_allowed(self, fast_payload: dict) -> None:
        assert fast_payload["overall_verdict"] in ALLOWED_OVERALL

    def test_path_metrics_keys(self, fast_payload: dict) -> None:
        for m in fast_payload["path_metrics"]:
            assert PATH_METRIC_KEYS <= set(m)

    def test_report_guardrail_wording(self) -> None:
        if not REPORT.exists():
            pytest.skip("report not generated yet")
        text = REPORT.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_REPORT:
            assert re.search(pattern, text, re.I) is None, pattern
        assert "roadmap and audit updates checked" in text.lower()

    def test_runtime_modest(self) -> None:
        cfg = _fast_cfg()
        t0 = time.perf_counter()
        build_d5_stat_tbrridge_inf_001(cfg)
        elapsed = time.perf_counter() - t0
        assert elapsed < 180.0

    def test_committed_artifact_matches_build(self) -> None:
        if not ARTIFACT.exists():
            pytest.skip("Run generator")
        cfg = D5StatTbrridgeInf001Config()
        loaded = _strip_timestamp(json.loads(ARTIFACT.read_text(encoding="utf-8")))
        built = _strip_timestamp(build_d5_stat_tbrridge_inf_001(cfg))
        assert loaded == built
