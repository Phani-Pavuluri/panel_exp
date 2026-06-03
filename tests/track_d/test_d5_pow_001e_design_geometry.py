"""D5-POW-001e design-method × geometry SCM+JK null FPR tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_pow_001e import (
    CONFIRMED_METHOD_IDS,
    D5Pow001eConfig,
    EXCLUDED_FROM_001E,
    METHOD_SPECS,
    run_d5_pow_001e,
    run_one_replicate,
    write_artifact,
)

ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_POW_001e_results.json"
)


class TestD5Pow001eDesignGeometry:
    def test_confirmed_methods_only(self) -> None:
        assert tuple(s.method_id for s in METHOD_SPECS) == CONFIRMED_METHOD_IDS
        assert "supergeos" in EXCLUDED_FROM_001E
        assert "trimmedmatch" in EXCLUDED_FROM_001E
        assert "multi_cell_multi_treated" not in CONFIRMED_METHOD_IDS

    def test_one_replicate_contract(self) -> None:
        cfg = D5Pow001eConfig(
            n_mc=2,
            rerandomization_max_iter=30,
            geometry_modes=("single_cell",),
        )
        rep = run_one_replicate(cfg, seed=cfg.random_state_base)
        assert len(rep["method_geometry_rows"]) == len(METHOD_SPECS)
        greedy = next(
            r for r in rep["method_geometry_rows"] if r["method_id"] == "greedy_match_markets"
        )
        assert greedy["geometry_mode"] == "single_cell"
        assert greedy["n_test_grps"] == 1
        assert greedy.get("per_cell")
        assert greedy["per_cell"][0]["unit_jackknife_feasible"] is True

    def test_multi_cell_per_cell_no_pooling(self) -> None:
        cfg = D5Pow001eConfig(
            n_mc=2,
            rerandomization_max_iter=30,
            geometry_modes=("multi_cell",),
        )
        rep = run_one_replicate(cfg, seed=cfg.random_state_base + 1)
        row = next(
            r
            for r in rep["method_geometry_rows"]
            if r["method_id"] == "greedy_match_markets" and r["geometry_mode"] == "multi_cell"
        )
        assert row["n_test_grps"] == 2
        assert len(row["per_cell"]) == 2
        assert row["per_cell"][0]["cell_id"] == "test_0"
        assert row["per_cell"][1]["cell_id"] == "test_1"

    def test_characterization_runs(self) -> None:
        payload = run_d5_pow_001e(
            D5Pow001eConfig(
                n_mc=6,
                rerandomization_max_iter=40,
                geometry_modes=("single_cell", "multi_cell"),
            )
        )
        assert payload["artifact_id"] == "D5-POW-001e"
        assert payload["governance"]["no_pooled_multi_cell_claim"] is True
        assert payload["calibration_eligibility_changed"] is False
        assert len(payload["method_geometry_summary"]) == len(METHOD_SPECS) * 2
        assert "greedy_vs_rerandomization_wrapper" in payload
        assert payload["overall_verdict"] in {
            "acceptable_with_caveats",
            "mixed_methods",
            "concerning_null_behavior",
            "insufficient_coverage",
        }

    def test_committed_artifact_schema(self) -> None:
        if not ARTIFACT_PATH.is_file():
            pytest.skip("Run D5-POW-001e generator to create committed artifact")
        loaded = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-POW-001e"
        assert loaded["governance"]["readout_branch"] == "SCM+UnitJackKnife_reference_null_monitor_only"
        assert len(loaded["method_geometry_summary"]) >= len(CONFIRMED_METHOD_IDS)
