"""D5-INST-AUGSYNTH-003 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.track_d_d5_inst_augsynth_003 import (
    D5InstAugsynth003Config,
    build_d5_inst_augsynth_003,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INST_AUGSYNTH_003_results.json"
)


@pytest.fixture(scope="module")
def cvxpy_available() -> None:
    if cvxpy_osqp_skip_reason():
        pytest.skip(cvxpy_osqp_skip_reason())


class TestD5InstAugsynth003:
    def test_build_structure(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynth003Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_003(cfg)
        assert payload["artifact_id"] == "D5-INST-AUGSYNTH-003"
        assert payload["governance"]["inference"] == "Conformal"
        assert payload["governance"]["no_base_augsynth"] is True
        assert "conformal_interval_semantics" in payload

    def test_conformal_feasible_single_cell(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynth003Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_003(cfg)
        cf = next(
            s
            for s in payload["instrument_summaries_null_single_cell"]
            if s["instrument"] == "augsynth_cvxpy_conformal"
        )
        assert cf["feasibility_rate"] >= 0.5
        assert cf["path_interval_type_mode"] == "conformal_interval"

    def test_no_promotion(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynth003Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_003(cfg)
        assert payload["instrument_status"]["promotion"] is False
        assert payload["instrument_status"]["calibration_signal_ingress"] is False
        assert payload["primary_disposition"] in (
            "characterized_restricted_diagnostic",
            "callable_unverified_interval_semantics",
            "blocked_interface",
        )

    def test_blocked_probes(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynth003Config(n_mc=1, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_003(cfg)
        blocks = payload["governance"]["explicit_blocks"]
        assert blocks["AugSynthCVXPY_Placebo"]["explicit_block"] is True
        assert blocks["AugSynthCVXPY_BlockResidualBootstrap"]["explicit_block"] is True
        assert blocks["AugSynthCVXPY_full_model_true"]["explicit_block"] is True
        assert blocks["pooled_multi_cell_claim"]["explicit_block"] is True

    def test_context_instruments_present(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynth003Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_003(cfg)
        keys = {s["instrument"] for s in payload["instrument_summaries_null_single_cell"]}
        assert "augsynth_cvxpy_jk" in keys
        assert "augsynth_cvxpy_kfold" in keys
        assert "scm_jk_reference" in keys

    def test_p2_roadmap_complete(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynth003Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_003(cfg)
        assert payload["track_f_p2_roadmap"]["p2_complete"] is True
        assert payload["track_f_p2_roadmap"]["next_battery"] is None

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-INST-AUGSYNTH-003 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-INST-AUGSYNTH-003"
        assert loaded["primary_disposition"] in (
            "characterized_restricted_diagnostic",
            "callable_unverified_interval_semantics",
            "blocked_interface",
        )
        assert loaded["overall_verdict"] == "remain_restricted_no_promotion"


def test_write_artifact(tmp_path: Path, cvxpy_available: None) -> None:
    cfg = D5InstAugsynth003Config(n_mc=2, include_multi_cell_k2=False)
    out = write_artifact(tmp_path / "ascf.json", cfg=cfg)
    assert out.is_file()
