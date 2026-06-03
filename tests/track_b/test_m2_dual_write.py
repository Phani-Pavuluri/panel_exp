"""M2 — RunBundle dual-write and live adapter export tests."""

from __future__ import annotations

import pytest

from panel_exp.artifacts.run_bundle import build_run_artifact_bundle
from tests.track_b.contract_fixtures import (
    FixtureCase,
    compare_adapter_output_to_oracle,
    iter_all_fixture_cases,
)
from dataclasses import replace

from tests.track_b.contract_validator import _validate_adapter_layer
from panel_exp.track_b.dual_write import (
    ADAPTER_VERSION,
    CONTRACT_STACK_VERSION,
    attach_track_b_views,
    build_track_b_views,
)
from tests.track_b.test_adapter_identity_resolution import resolve_adapter_output


def _case(fixture_id: str, variant_id: str | None = None) -> FixtureCase:
    for case in iter_all_fixture_cases():
        if case.fixture_id == fixture_id and case.variant_id == variant_id:
            return case
    raise KeyError(fixture_id)


class TestM2DualWriteSidecar:
    def test_build_track_b_views_metadata(self) -> None:
        case = _case("GOLD-001")
        views = build_track_b_views(
            spec=case.spec,
            run_artifacts_stub=case.run_artifacts_stub,
            calibration_signal_binding=case.calibration_signal_binding,
        )
        assert views["contract_stack_version"] == CONTRACT_STACK_VERSION
        assert views["adapter_version"] == ADAPTER_VERSION
        assert views["track_b_views_present"] is True
        assert views["export_status"] == "complete"
        assert "experiment_evidence_view" in views

    def test_bundle_dual_write_preserves_legacy_keys(self) -> None:
        case = _case("GOLD-001")
        legacy_bundle = build_run_artifact_bundle(
            evidence={"experiment_id": "legacy-only", "inference_metadata": {}},
        )
        legacy_keys = set(legacy_bundle.to_dict().keys())
        dual = build_run_artifact_bundle(
            evidence={"experiment_id": "legacy-only", "inference_metadata": {}},
            include_track_b_views=True,
            track_b_spec=case.spec,
            track_b_run_stub=case.run_artifacts_stub,
            track_b_calibration_binding=case.calibration_signal_binding,
        )
        dual_dict = dual.to_dict()
        assert "track_b_views" in dual_dict
        for key in legacy_keys:
            assert key in dual_dict
        assert dual_dict["evidence"]["experiment_id"] == "legacy-only"

    def test_attach_track_b_views_non_mutating(self) -> None:
        case = _case("GOLD-001")
        base = {"bundle_version": "1.0", "evidence": {}}
        out = attach_track_b_views(
            base,
            spec=case.spec,
            run_artifacts_stub=case.run_artifacts_stub,
        )
        assert "track_b_views" not in base
        assert out["track_b_views"]["export_status"] == "complete"

    def test_sidecar_adapter_matches_oracle(self) -> None:
        case = _case("GOLD-001")
        views = build_track_b_views(
            spec=case.spec,
            run_artifacts_stub=case.run_artifacts_stub,
            calibration_signal_binding=case.calibration_signal_binding,
        )
        mismatches = compare_adapter_output_to_oracle(
            views["adapter_output"],
            case.adapter_expected_output,
        )
        assert mismatches == [], "\n".join(mismatches)


class TestM2LiveAdapterCompare:
    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_resolve_adapter_output_matches_fixture_oracle(self, case: FixtureCase) -> None:
        actual = resolve_adapter_output(case)
        mismatches = compare_adapter_output_to_oracle(
            actual, case.adapter_expected_output
        )
        assert mismatches == [], "\n".join(mismatches)

    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_resolved_adapter_passes_structural_validator_rules(self, case: FixtureCase) -> None:
        resolved = resolve_adapter_output(case)
        synthetic = replace(case, adapter_expected_output=resolved)
        issues = _validate_adapter_layer(synthetic, case.case_key)
        assert not issues, "\n".join(str(i) for i in issues)
        for field in ("trust_outcome", "alignment_verdict"):
            assert field not in resolved.get("experiment_evidence", {})
            assert field not in (resolved.get("diagnostic_summary") or {})


class TestM2RepresentativeRunBundle:
    def test_gold_001_representative_bundle_carries_track_b_views(self) -> None:
        case = _case("GOLD-001")
        bundle = build_run_artifact_bundle(
            evidence={
                "experiment_id": case.spec["study_id"],
                "inference_metadata": {
                    **case.run_artifacts_stub,
                    "declared_estimand_id": case.spec["declared_estimand_id"],
                    "interval_estimand_expectation_id": case.spec.get(
                        "interval_estimand_expectation_id"
                    ),
                },
            },
            include_track_b_views=True,
            track_b_spec=case.spec,
            track_b_run_stub=case.run_artifacts_stub,
            track_b_calibration_binding=case.calibration_signal_binding,
        )
        payload = bundle.to_dict()
        assert payload.get("track_b_views")
        views = payload["track_b_views"]
        assert views["export_status"] == "complete"
        mismatches = compare_adapter_output_to_oracle(
            views["adapter_output"],
            case.adapter_expected_output,
        )
        assert mismatches == [], "\n".join(mismatches)

