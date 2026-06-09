"""D5-STAT-MCELL-PERCELL-001 tests."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.track_d_d5_stat_mcell_percell_001 import (
    D5StatMcellPercell001Config,
    METHOD_COMBINATIONS,
    REQUIRED_WORLD_IDS,
    build_d5_stat_mcell_percell_001,
    write_artifact,
)

_REPO = Path(__file__).resolve().parents[2]
ARTIFACT = _REPO / "docs/track_d/archives/D5_STAT_MCELL_PERCELL_001_results.json"
REPORT = _REPO / "docs/track_d/D5_STAT_MCELL_PERCELL_001_REPORT.md"

ALLOWED_OVERALL = frozenset(
    {
        "characterization_pass_with_caveats",
        "characterization_mixed_requires_followup",
        "characterization_fail_requires_fix",
    }
)

PER_CELL_KEYS = frozenset(
    {
        "world_id",
        "cell_id",
        "replicate_id",
        "seed",
        "method_combination",
        "callable_status",
        "point_estimate",
        "true_effect",
        "bias",
        "absolute_error",
        "squared_error",
        "sign_correct",
        "interval_lower",
        "interval_upper",
        "interval_width",
        "interval_contains_truth",
        "interval_orientation_valid",
        "negative_half_width_detected",
        "finite_outputs",
        "prefit_rmse",
        "donor_count",
        "exception_type",
        "exception_message",
    }
)

AGG_KEYS = frozenset(
    {
        "n_replicates",
        "n_cells",
        "expected_cell_results",
        "observed_cell_results",
        "missing_cell_result_rate",
        "feasible_cell_runs",
        "failed_cell_runs",
        "callable_failure_rate",
        "non_finite_output_rate",
        "mean_absolute_error_by_method",
        "rmse_by_method",
        "sign_error_rate_by_method",
        "cell_identity_preserved_rate",
        "method_identity_preserved_rate",
        "silent_pooling_detected",
        "pooled_effect_emitted",
        "pooled_interval_emitted",
        "cross_cell_shrinkage_detected",
        "notes",
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
    r"\bportfolio effect\b",
    r"\bpooled causal effect\b",
]


def _strip_timestamp(payload: dict) -> dict:
    out = json.loads(json.dumps(payload))
    out.pop("generated_at", None)
    return out


def _fast_cfg() -> D5StatMcellPercell001Config:
    return D5StatMcellPercell001Config(n_replicates=2)


@pytest.fixture(scope="module")
def fast_payload() -> dict:
    if cvxpy_osqp_skip_reason():
        pytest.skip("cvxpy/osqp required")
    return build_d5_stat_mcell_percell_001(_fast_cfg())


@pytest.mark.skipif(cvxpy_osqp_skip_reason() is not None, reason="cvxpy/osqp required")
class TestD5StatMcellPercell001:
    def test_build_deterministic_excluding_timestamp(self) -> None:
        cfg = _fast_cfg()
        assert _strip_timestamp(build_d5_stat_mcell_percell_001(cfg)) == _strip_timestamp(
            build_d5_stat_mcell_percell_001(cfg)
        )

    def test_required_worlds_exist(self, fast_payload: dict) -> None:
        assert set(REQUIRED_WORLD_IDS) <= {w["world_id"] for w in fast_payload["worlds"]}
        assert set(REQUIRED_WORLD_IDS) <= set(fast_payload["aggregate_metrics"])

    def test_per_cell_fields(self, fast_payload: dict) -> None:
        for row in fast_payload["per_cell_results"]:
            assert PER_CELL_KEYS <= set(row)

    def test_aggregate_metrics_per_world(self, fast_payload: dict) -> None:
        for wid in REQUIRED_WORLD_IDS:
            assert AGG_KEYS <= set(fast_payload["aggregate_metrics"][wid])

    def test_every_expected_cell_has_result(self, fast_payload: dict) -> None:
        for wid, agg in fast_payload["aggregate_metrics"].items():
            assert agg["observed_cell_results"] == agg["expected_cell_results"], wid
            assert agg["missing_cell_result_rate"] == 0.0, wid

    def test_no_pooled_effect(self, fast_payload: dict) -> None:
        for agg in fast_payload["aggregate_metrics"].values():
            assert agg["pooled_effect_emitted"] is False

    def test_no_pooled_interval(self, fast_payload: dict) -> None:
        for agg in fast_payload["aggregate_metrics"].values():
            assert agg["pooled_interval_emitted"] is False

    def test_cell_identity_preserved(self, fast_payload: dict) -> None:
        for agg in fast_payload["aggregate_metrics"].values():
            assert agg["cell_identity_preserved_rate"] == 1.0

    def test_method_identity_preserved(self, fast_payload: dict) -> None:
        for agg in fast_payload["aggregate_metrics"].values():
            assert agg["method_identity_preserved_rate"] == 1.0

    def test_failed_cells_not_silently_dropped(self, fast_payload: dict) -> None:
        for agg in fast_payload["aggregate_metrics"].values():
            assert agg["silent_pooling_detected"] is False

    def test_forbidden_flags_false(self, fast_payload: dict) -> None:
        for key, val in fast_payload["forbidden_flags"].items():
            assert val is False, key

    def test_overall_verdict_allowed(self, fast_payload: dict) -> None:
        assert fast_payload["overall_verdict"] in ALLOWED_OVERALL

    def test_report_roadmap_section(self) -> None:
        if not REPORT.is_file():
            pytest.skip("Run generator")
        text = REPORT.read_text(encoding="utf-8")
        assert "Roadmap and audit updates checked" in text or "roadmap" in text.lower()

    def test_report_guardrail_wording(self) -> None:
        if not REPORT.is_file():
            pytest.skip("Run generator")
        text = REPORT.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_REPORT:
            assert re.search(pattern, text, re.I) is None, pattern

    def test_runtime_modest(self) -> None:
        t0 = time.perf_counter()
        build_d5_stat_mcell_percell_001(_fast_cfg())
        assert time.perf_counter() - t0 < 120.0

    def test_committed_artifact_matches_build(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run generator")
        cfg = D5StatMcellPercell001Config(n_replicates=12)
        loaded = _strip_timestamp(json.loads(ARTIFACT.read_text(encoding="utf-8")))
        built = _strip_timestamp(build_d5_stat_mcell_percell_001(cfg))
        assert loaded == built

    def test_methods_used(self, fast_payload: dict) -> None:
        methods = {r["method_combination"] for r in fast_payload["per_cell_results"]}
        assert set(METHOD_COMBINATIONS) <= methods


def test_write_artifact(tmp_path: Path) -> None:
    if cvxpy_osqp_skip_reason():
        pytest.skip("cvxpy/osqp required")
    assert write_artifact(tmp_path / "mcell.json", cfg=_fast_cfg()).is_file()
