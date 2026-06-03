"""M2.2 — production TrustReport sidecar on opt-in Geo RunBundle export."""

from __future__ import annotations

import pytest

from panel_exp.artifacts.geo_run_export import export_geo_run_bundle
from panel_exp.artifacts.run_bundle import build_run_artifact_bundle
from panel_exp.track_b.trust_report import TRUST_VERDICT_FIELDS
from tests.track_b.contract_fixtures import iter_all_fixture_cases
from tests.track_b.test_m2_1_representative_bundles import _REP_CASES, _load_rep_cases
from tests.track_b.trust_report_composer import compose_trust_report, trust_report_to_dict

def _gold(case_id: str):
    for case in iter_all_fixture_cases():
        if case.fixture_id == case_id and case.variant_id is None:
            return case
    raise KeyError(case_id)


def _scenarios(case) -> list:
    return list(case.trust_report_expected_output.get("scenarios") or [])


class TestM22TrustReportSidecar:
    def test_gold_001_export_matches_oracle(self) -> None:
        case = _gold("GOLD-001")
        bundle = export_geo_run_bundle(
            evidence={
                "experiment_id": "m22-gold-001",
                "inference_metadata": {},
                "track_b_export_hints": {
                    **case.run_artifacts_stub,
                    "config_alias": case.run_artifacts_stub["config_alias"],
                    "declared_estimand_id": case.spec["declared_estimand_id"],
                    "interval_estimand_expectation_id": case.spec[
                        "interval_estimand_expectation_id"
                    ],
                    "geometry_class": case.spec["geometry_class"],
                },
            },
            include_track_b_views=True,
            include_trust_report=True,
            trust_report_scenarios=_scenarios(case),
            track_b_spec=case.spec,
            track_b_run_stub=case.run_artifacts_stub,
            track_b_calibration_binding=case.calibration_signal_binding,
            alignment_reference_estimand_id=case.trust_report_expected_output[
                "alignment_reference_estimand_id"
            ],
        )
        payload = bundle.to_dict()
        views = payload["track_b_views"]
        assert views["trust_report_present"] is True
        got = views["trust_report_view"]
        expected = trust_report_to_dict(compose_trust_report(case))
        assert got["scenarios"] == expected["scenarios"]
        assert (
            got["alignment_reference_estimand_id"]
            == expected["alignment_reference_estimand_id"]
        )

    def test_verdicts_only_on_trust_report_view(self) -> None:
        case = _gold("GOLD-001")
        bundle = export_geo_run_bundle(
            evidence={"experiment_id": "x", "inference_metadata": {}},
            include_track_b_views=True,
            include_trust_report=True,
            trust_report_scenarios=_scenarios(case),
            track_b_spec=case.spec,
            track_b_run_stub=case.run_artifacts_stub,
            track_b_calibration_binding=case.calibration_signal_binding,
        )
        views = bundle.to_dict()["track_b_views"]
        adapter = views["adapter_output"]
        evidence_view = views["experiment_evidence_view"]
        for field in TRUST_VERDICT_FIELDS:
            assert field not in adapter
            assert field not in evidence_view
        for scenario in views["trust_report_view"]["scenarios"]:
            assert "alignment_verdict" in scenario
            assert "trust_outcome" in scenario

    def test_missing_scenarios_explicit_omit(self) -> None:
        case = _gold("GOLD-001")
        bundle = export_geo_run_bundle(
            evidence={"experiment_id": "x", "inference_metadata": {}},
            include_track_b_views=True,
            include_trust_report=True,
            track_b_spec=case.spec,
            track_b_run_stub=case.run_artifacts_stub,
        )
        views = bundle.to_dict()["track_b_views"]
        assert views["trust_report_present"] is False
        assert views["trust_report_omit_reason"] == "missing_trust_scenarios"
        assert "trust_report_view" not in views

    def test_legacy_bundle_default_unchanged(self) -> None:
        rep = _REP_CASES[0]
        bundle = build_run_artifact_bundle(evidence=rep["bundle"]["evidence"])
        assert "track_b_views" not in bundle.to_dict()

    def test_trust_report_off_leaves_no_trust_keys(self) -> None:
        case = _gold("GOLD-001")
        bundle = export_geo_run_bundle(
            evidence={"experiment_id": "x", "inference_metadata": {}},
            include_track_b_views=True,
            include_trust_report=False,
            track_b_spec=case.spec,
            track_b_run_stub=case.run_artifacts_stub,
        )
        views = bundle.to_dict()["track_b_views"]
        assert "trust_report_present" not in views
        assert "trust_report_view" not in views


@pytest.mark.parametrize("rep", _load_rep_cases(), ids=lambda r: r["case_id"])
class TestM22RepresentativeTrustPaths:
    def test_blocked_adapter_not_assessable(self, rep: dict) -> None:
        if rep["expected_export_status"] != "blocked":
            pytest.skip("blocked path only")
        scenarios = [
            {
                "scenario_id": "lift_launch",
                "intended_use": "business_lift_launch",
                "claim_type": "positive_lift_detection",
            }
        ]
        bundle = export_geo_run_bundle(
            evidence=rep["bundle"]["evidence"],
            include_track_b_views=True,
            include_trust_report=True,
            trust_report_scenarios=scenarios,
        )
        views = bundle.to_dict()["track_b_views"]
        assert views["export_status"] == "blocked"
        assert views["trust_report_present"] is True
        for s in views["trust_report_view"]["scenarios"]:
            assert s["alignment_verdict"] == "not_assessable"
            assert s["trust_outcome"] == "not_assessable"

    def test_partial_export_lift_unsupported(self, rep: dict) -> None:
        if rep["case_id"] != "REP-004":
            pytest.skip("partial geometry case")
        scenarios = [
            {
                "scenario_id": "lift_launch",
                "intended_use": "business_lift_launch",
                "claim_type": "positive_lift_detection",
            }
        ]
        bundle = export_geo_run_bundle(
            evidence=rep["bundle"]["evidence"],
            include_track_b_views=True,
            include_trust_report=True,
            trust_report_scenarios=scenarios,
        )
        views = bundle.to_dict()["track_b_views"]
        assert views["export_status"] == "partial"
        lift = views["trust_report_view"]["scenarios"][0]
        assert lift["alignment_verdict"] == "incompatible"
        assert lift["trust_outcome"] == "unsupported"
