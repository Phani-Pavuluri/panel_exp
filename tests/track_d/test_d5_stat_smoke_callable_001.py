"""D5-STAT-SMOKE-CALLABLE-001 tests."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_stat_smoke_callable_001 import (
    MINIMUM_COMBO_IDS,
    build_d5_stat_smoke_callable_001,
    write_artifact,
)

_REPO = Path(__file__).resolve().parents[2]
ARTIFACT = _REPO / "docs/track_d/archives/D5_STAT_SMOKE_CALLABLE_001_results.json"
REPORT = _REPO / "docs/track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md"

ALLOWED_OVERALL = frozenset(
    {
        "smoke_pass_with_expected_blocks",
        "smoke_pass_with_caveats",
        "smoke_fail_requires_fix",
    }
)

BLOCKED_MUST_NOT_EXECUTE = frozenset(
    {
        "AUGSYNTH-CONFORMAL",
        "MCELL-POOLED-AUGSYNTH",
        "MCELL-POOLED-SCM-JK",
        "SUPERGEO-SCM-JK",
        "TRIM-SCM-JK",
        "SUPERGEO-AUGSYNTH-POINT",
        "TRIM-AUGSYNTH-POINT",
        "TBR-UNIT-JK",
        "TBRRIDGE-BAYESIAN-REG",
    }
)

FORBIDDEN_REPORT_PHRASES = [
    r"\bis statistically validated\b",
    r"\bclaims suitability\b",
    r"\bis production[- ]ready\b",
    r"\bis promoted\b",
    r"\bTrustReport eligible\b",
    r"\bCalibrationSignal eligible\b",
    r"\bMMM ready for production\b",
    r"\bLLM recommendation ready\b",
    r"\bprimary evidence role\b",
    r"\bsecondary evidence role\b",
    r"\bdirectional evidence role\b",
]


def _strip_timestamp(payload: dict) -> dict:
    out = json.loads(json.dumps(payload))
    out.pop("generated_at", None)
    return out


def _row_by_id(payload: dict, combo_id: str) -> dict:
    for row in payload["rows"]:
        if row["combination_id"] == combo_id:
            return row
    raise KeyError(combo_id)


class TestD5StatSmokeCallable001:
    def test_build_deterministic_excluding_timestamp(self) -> None:
        a = _strip_timestamp(build_d5_stat_smoke_callable_001())
        b = _strip_timestamp(build_d5_stat_smoke_callable_001())
        assert a == b

    def test_minimum_combos_present(self) -> None:
        payload = build_d5_stat_smoke_callable_001()
        ids = {r["combination_id"] for r in payload["rows"]}
        assert MINIMUM_COMBO_IDS <= ids
        for cid in MINIMUM_COMBO_IDS:
            row = _row_by_id(payload, cid)
            assert row["callable_status"] in (
                "callable_pass",
                "callable_fail",
                "blocked_expected",
                "skipped_not_smoke_safe",
            )

    def test_blocked_combos_not_executed(self) -> None:
        payload = build_d5_stat_smoke_callable_001()
        for cid in BLOCKED_MUST_NOT_EXECUTE:
            row = _row_by_id(payload, cid)
            assert row["callable_status"] == "blocked_expected"
            assert row["smoke_verdict"] == "expected_block"
            assert "probe_spec" not in row

    def test_augsynth_jk_implementation_fix_blocked(self) -> None:
        row = _row_by_id(build_d5_stat_smoke_callable_001(), "AUGSYNTH-JK")
        assert row["callable_status"] == "blocked_expected"
        assert row["smoke_verdict"] == "expected_block"

    def test_forbidden_flags_false(self) -> None:
        payload = build_d5_stat_smoke_callable_001()
        assert payload["forbidden_flags"]["promotion_allowed"] is False
        for row in payload["rows"]:
            assert row["promotion_allowed"] is False
            assert row["trust_role_allowed"] is False
            assert row["calibration_signal_allowed"] is False
            assert row["mmm_allowed"] is False
            assert row["llm_recommendation_allowed"] is False

    def test_interval_orientation_on_executed(self) -> None:
        payload = build_d5_stat_smoke_callable_001()
        for row in payload["rows"]:
            if row["callable_status"] != "callable_pass":
                continue
            if row.get("interval_present"):
                assert row["interval_orientation_valid"] is True
                assert row["negative_half_width_detected"] is not True

    def test_no_silent_geometry_on_executed(self) -> None:
        payload = build_d5_stat_smoke_callable_001()
        for row in payload["rows"]:
            if row["callable_status"] == "callable_pass":
                assert row["unsupported_geometry_silently_allowed"] is False

    def test_overall_verdict_allowed(self) -> None:
        payload = build_d5_stat_smoke_callable_001()
        assert payload["overall_verdict"] in ALLOWED_OVERALL

    def test_report_guardrail_wording(self) -> None:
        if not REPORT.is_file():
            pytest.skip("Run smoke generator to write report")
        text = REPORT.read_text(encoding="utf-8").lower()
        for pattern in FORBIDDEN_REPORT_PHRASES:
            assert re.search(pattern, text, re.I) is None, pattern

    def test_committed_artifact_matches_build(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run smoke generator")
        loaded = _strip_timestamp(json.loads(ARTIFACT.read_text(encoding="utf-8")))
        built = _strip_timestamp(build_d5_stat_smoke_callable_001())
        assert loaded == built


def test_write_artifact(tmp_path: Path) -> None:
    out = write_artifact(tmp_path / "smoke.json")
    assert out.is_file()
