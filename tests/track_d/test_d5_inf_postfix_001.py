"""D5-INF-POSTFIX-001 — post F-INF-003 targeted OC (A05, A19)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.track_d_d5_inf_postfix_001 import (
    D5InfPostfix001Config,
    PRE_FIX_A05,
    PRE_FIX_A19,
    build_d5_inf_postfix_001,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INF_POSTFIX_001_results.json"
)


@pytest.fixture(scope="module")
def cvxpy_available() -> None:
    if cvxpy_osqp_skip_reason():
        pytest.skip(cvxpy_osqp_skip_reason())


class TestD5InfPostfix001:
    def test_build_structure(self, cvxpy_available: None) -> None:
        cfg = D5InfPostfix001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inf_postfix_001(cfg)
        assert payload["artifact_id"] == "D5-INF-POSTFIX-001"
        assert payload["prerequisite"] == "F-INF-003"
        assert "A05" in payload["tuples"]
        assert "A19" in payload["tuples"]

    def test_a05_structural_interval_fixed(self, cvxpy_available: None) -> None:
        cfg = D5InfPostfix001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inf_postfix_001(cfg)
        a05 = payload["tuples"]["A05"]
        post = a05["post_fix"]["single_cell"]
        assert post["negative_halfwidth_rate"] == 0.0
        assert post["inverted_bound_rate"] == 0.0
        assert a05["comparison_single_cell"]["structural_interval_fixed"] is True
        assert PRE_FIX_A05["single_cell"]["negative_halfwidth_rate"] == 1.0

    def test_a19_structural_interval_fixed(self) -> None:
        cfg = D5InfPostfix001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inf_postfix_001(cfg)
        a19 = payload["tuples"]["A19"]
        post = a19["post_fix"]["single_cell"]
        assert post["negative_halfwidth_rate"] == 0.0
        assert post["inverted_bound_rate"] == 0.0
        assert a19["comparison_single_cell"]["structural_interval_fixed"] is True
        assert PRE_FIX_A19["single_cell"]["negative_halfwidth_rate"] == 1.0

    def test_no_promotion_or_governed_uncertainty(self, cvxpy_available: None) -> None:
        cfg = D5InfPostfix001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inf_postfix_001(cfg)
        assert payload["governance"]["no_promotion"] is True
        assert payload["governance"]["no_governed_uncertainty_claim"] is True
        for key in ("A05", "A19"):
            assert payload["tuples"][key]["promotion"] is False
            assert payload["tuples"][key]["calibration_signal_eligible"] is False
            assert payload["tuples"][key]["f_inf_classification"]["is_governed_uncertainty"] is False

    def test_postfix_disposition_restricted_or_unverified(self, cvxpy_available: None) -> None:
        cfg = D5InfPostfix001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inf_postfix_001(cfg)
        for key in ("A05", "A19"):
            disp = payload["tuples"][key]["postfix_disposition"]
            assert disp in (
                "callable_unverified_interval_semantics",
                "diagnostic_interval_only",
                "restricted_no_promotion",
            )
            assert disp != "blocked_invalid_interval"
        assert payload["overall_verdict"] == "remain_restricted_no_promotion"

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run write_artifact() to generate D5_INF_POSTFIX_001_results.json")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-INF-POSTFIX-001"
        assert loaded["overall_verdict"] == "remain_restricted_no_promotion"


def test_write_artifact_smoke(cvxpy_available: None) -> None:
    path = write_artifact(cfg=D5InfPostfix001Config(n_mc=2, include_multi_cell_k2=False))
    assert path.is_file()
