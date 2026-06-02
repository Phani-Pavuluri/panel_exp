"""D5-INST-AUGSYNTH-KFOLD-001 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.track_d_d5_inst_augsynth_kfold_001 import (
    D5InstAugsynthKfold001Config,
    build_d5_inst_augsynth_kfold_001,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INST_AUGSYNTH_KFOLD_001_results.json"
)


@pytest.fixture(scope="module")
def cvxpy_available() -> None:
    if cvxpy_osqp_skip_reason():
        pytest.skip(cvxpy_osqp_skip_reason())


class TestD5InstAugsynthKfold001:
    def test_build_structure(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynthKfold001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_kfold_001(cfg)
        assert payload["artifact_id"] == "D5-INST-AUGSYNTH-KFOLD-001"
        assert payload["governance"]["inference"] == "Kfold"
        assert payload["governance"]["no_base_augsynth"] is True

    def test_kfold_feasible_single_cell(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynthKfold001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_kfold_001(cfg)
        kf = next(
            s
            for s in payload["instrument_summaries_null_single_cell"]
            if s["instrument"] == "augsynth_cvxpy_kfold"
        )
        assert kf["feasibility_rate"] >= 0.5
        assert kf["path_interval_type_mode"] == "confidence_interval"

    def test_no_calibration_signal(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynthKfold001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_kfold_001(cfg)
        assert payload["instrument_status"]["calibration_signal_ingress"] is False
        assert payload["instrument_status"]["estimand_equivalence_claim"] is False

    def test_context_instruments_present(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynthKfold001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_kfold_001(cfg)
        keys = {s["instrument"] for s in payload["instrument_summaries_null_single_cell"]}
        assert "scm_jk_reference" in keys
        assert "augsynth_cvxpy_jk" in keys

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-INST-AUGSYNTH-KFOLD-001 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-INST-AUGSYNTH-KFOLD-001"
        assert loaded["overall_verdict"] in (
            "remain_restricted_diagnostic_comparator",
            "restricted_with_caveats",
            "blocked_low_feasibility",
        )


def test_write_artifact(tmp_path: Path, cvxpy_available: None) -> None:
    cfg = D5InstAugsynthKfold001Config(n_mc=2, include_multi_cell_k2=False)
    out = write_artifact(tmp_path / "askf.json", cfg=cfg)
    assert out.is_file()
