"""
TRUSTREPORT-DECISION-CONTEXT-SMOKE-001 — end-to-end export smoke for f_decision_context.

Proves the opt-in TrustReport decision-context path on a realistic Geo RunBundle
export. No estimator/inference/OC changes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from panel_exp.artifacts.geo_run_export import export_geo_run_bundle

SMOKE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "trustreport_decision_context_smoke"
ARCHIVE_DIR = Path(__file__).resolve().parents[2] / "docs" / "track_b" / "archives"
GOLDEN_PATH = ARCHIVE_DIR / "TRUSTREPORT_DECISION_CONTEXT_SMOKE_001_export.json"


def _load_smoke(name: str) -> dict[str, Any]:
    return json.loads((SMOKE_DIR / name).read_text(encoding="utf-8"))


def _export(
    smoke: dict[str, Any],
    *,
    include_decision_context: bool,
) -> dict[str, Any]:
    bundle = export_geo_run_bundle(
        evidence=smoke["evidence"],
        include_track_b_views=True,
        include_trust_report=True,
        include_trust_report_decision_context=include_decision_context,
        trust_report_scenarios=smoke["trust_scenarios"],
    )
    return bundle.to_dict()


def _fdc(payload: dict[str, Any]) -> dict[str, Any]:
    views = payload["track_b_views"]
    assert views.get("trust_report_present") is True
    view = views["trust_report_view"]
    assert "f_decision_context" in view
    return view["f_decision_context"]


class TestSmoke001OptInExport:
    """SMOKE-001: full geo export with explicit readout_evidence comparators."""

    @pytest.fixture(scope="class")
    def smoke_doc(self) -> dict[str, Any]:
        return _load_smoke("smoke_001_geo_rep_with_comparators.json")

    @pytest.fixture(scope="class")
    def payload_on(self, smoke_doc: dict[str, Any]) -> dict[str, Any]:
        return _export(smoke_doc, include_decision_context=True)

    @pytest.fixture(scope="class")
    def payload_off(self, smoke_doc: dict[str, Any]) -> dict[str, Any]:
        return _export(smoke_doc, include_decision_context=False)

    def test_track_b_export_status_complete(self, payload_on: dict[str, Any], smoke_doc: dict) -> None:
        assert payload_on["track_b_views"]["export_status"] == smoke_doc["expected_export_status"]

    def test_f_decision_context_present_when_opted_in(self, payload_on: dict[str, Any]) -> None:
        fdc = _fdc(payload_on)
        assert fdc["decision_context_complete"] is True
        assert fdc["promotion_candidates"] == []

    def test_f_decision_context_absent_when_opted_out(self, payload_off: dict[str, Any]) -> None:
        view = payload_off["track_b_views"]["trust_report_view"]
        assert "f_decision_context" not in view
        assert payload_off["track_b_views"]["trust_report_present"] is True

    def test_legacy_scenarios_unchanged_between_on_and_off(
        self, payload_on: dict[str, Any], payload_off: dict[str, Any]
    ) -> None:
        on_s = payload_on["track_b_views"]["trust_report_view"]["scenarios"]
        off_s = payload_off["track_b_views"]["trust_report_view"]["scenarios"]
        assert on_s == off_s

    def test_guardrails_mmm_and_promotion(self, payload_on: dict[str, Any], smoke_doc: dict) -> None:
        fdc = _fdc(payload_on)
        exp = smoke_doc["expected_f_decision"]
        assert fdc["mmm_action"] == exp["mmm_action"]
        assert fdc["mmm_status"] == exp["mmm_status"]
        assert fdc["promotion_candidates"] == exp["promotion_candidates"]

    def test_primary_null_monitor_role(self, payload_on: dict[str, Any], smoke_doc: dict) -> None:
        fdc = _fdc(payload_on)
        exp = smoke_doc["expected_f_decision"]
        primary = fdc["primary_readout"]
        assert primary is not None
        assert primary["assigned_role"] == exp["primary_role"]
        assert primary["inference"] == exp["primary_inference"]
        assert primary["calibration_signal_eligible"] is True

    def test_calibration_signal_action_primary_only(
        self, payload_on: dict[str, Any], smoke_doc: dict
    ) -> None:
        fdc = _fdc(payload_on)
        assert fdc["calibration_signal_action"] == smoke_doc["expected_f_decision"][
            "calibration_signal_action"
        ]
        for d in fdc["diagnostic_comparators"]:
            assert d["assigned_role"] == "diagnostic_comparator"
            assert d["calibration_signal_eligible"] is False

    def test_diagnostic_comparators_visible(self, payload_on: dict[str, Any]) -> None:
        fdc = _fdc(payload_on)
        assert len(fdc["diagnostic_comparators"]) >= 2
        diag_infs = {d["inference"] for d in fdc["diagnostic_comparators"]}
        assert "Conformal" in diag_infs

    def test_matches_committed_golden_excerpt(self, payload_on: dict[str, Any]) -> None:
        if not GOLDEN_PATH.is_file():
            pytest.skip("golden archive not committed")
        golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
        fdc = _fdc(payload_on)
        for key in golden["f_decision_context_keys"]:
            assert key in fdc
        assert fdc["primary_readout"]["assigned_role"] == golden["primary_readout"]["assigned_role"]
        assert fdc["mmm_action"] == golden["mmm_action"]
        assert fdc["promotion_candidates"] == golden["promotion_candidates"]


class TestSmoke002IncompleteMetadata:
    def test_incomplete_warning_when_unmapped_pair(self) -> None:
        smoke = _load_smoke("smoke_002_incomplete_metadata.json")
        payload = _export(smoke, include_decision_context=True)
        views = payload["track_b_views"]
        if not views.get("trust_report_present"):
            assert views.get("export_status") == "blocked"
            return
        fdc = views["trust_report_view"].get("f_decision_context")
        if fdc is None:
            return
        assert any("decision_context_incomplete" in w for w in fdc["required_warnings"])


def _write_golden_archive() -> None:
    """Regenerate docs/track_b/archives/TRUSTREPORT_DECISION_CONTEXT_SMOKE_001_export.json."""
    smoke = _load_smoke("smoke_001_geo_rep_with_comparators.json")
    payload = _export(smoke, include_decision_context=True)
    fdc = _fdc(payload)
    excerpt = {
        "smoke_id": "SMOKE-001",
        "document_id": "TRUSTREPORT-DECISION-CONTEXT-SMOKE-001",
        "experiment_id": smoke["evidence"]["experiment_id"],
        "export_flags": {
            "include_track_b_views": True,
            "include_trust_report": True,
            "include_trust_report_decision_context": True,
        },
        "f_decision_context_keys": sorted(fdc.keys()),
        "primary_readout": {
            "estimator": fdc["primary_readout"]["estimator"],
            "inference": fdc["primary_readout"]["inference"],
            "assigned_role": fdc["primary_readout"]["assigned_role"],
            "calibration_signal_eligible": fdc["primary_readout"]["calibration_signal_eligible"],
        },
        "diagnostic_comparators": [
            {"estimator": d["estimator"], "inference": d["inference"], "assigned_role": d["assigned_role"]}
            for d in fdc["diagnostic_comparators"]
        ],
        "agreement_status": fdc["agreement_status"],
        "final_decision_posture": fdc["final_decision_posture"],
        "calibration_signal_action": fdc["calibration_signal_action"],
        "mmm_action": fdc["mmm_action"],
        "mmm_status": fdc["mmm_status"],
        "promotion_candidates": fdc["promotion_candidates"],
        "decision_context_complete": fdc["decision_context_complete"],
        "required_warnings_sample": fdc["required_warnings"][:3],
    }
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    GOLDEN_PATH.write_text(json.dumps(excerpt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    _write_golden_archive()
    print(f"wrote {GOLDEN_PATH}")
