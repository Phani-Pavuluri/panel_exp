"""Tests for GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001."""

from __future__ import annotations

from panel_exp.validation.assignment_panel_integrity_runtime_001 import ASSIGNMENT_PANEL_INTEGRITY_PASSED
from panel_exp.validation.estimator_inference_did_executor_003 import EFFECT_ESTIMATE_COMPUTED_POINT_ONLY
from panel_exp.validation.post_test_spend_readiness_adapter_runtime_001 import (
    PostTestExperimentType,
    PostTestSpendInput,
    PostTestSpendReadinessStatus,
    build_post_test_spend_evidence,
    build_trusted_readout_spend_handoff,
)
from panel_exp.validation.readout_diagnostics_sensitivity_runtime_001 import (
    EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW,
)
from panel_exp.validation.srm_balance_readout_diagnostic_001 import SRM_BALANCE_DIAGNOSTIC_PASSED
from panel_exp.validation.statistical_promotion_thresholds_001 import STATISTICAL_PROMOTION_PASSED
from panel_exp.validation.trusted_readout_report_runtime_001 import (
    TRUSTED_REPORT_BLOCKED_BY_CLAIM_AUTHORIZATION,
    TRUSTED_REPORT_READY,
    TRUSTED_REPORT_READY_WITH_REDACTIONS,
    generate_trusted_readout_report,
)
from panel_exp.validation.trusted_readout_spend_readiness_integration_runtime_001 import (
    SPEND_READINESS_NOT_REQUESTED,
    generate_trusted_readout_report_with_spend_readiness,
    integrate_spend_readiness_into_trusted_readout,
)


def _claim_scope() -> dict:
    return {"estimand": "STANDARD_INCREMENTALITY", "metric_kpi": "sales"}


def _trusted_readout_input(**extra: object) -> dict:
    payload = {
        "request_id": "integration_test_001",
        "design_id": "design_integration_001",
        "claim_scope": _claim_scope(),
        "claim_requests": [{"claim_type": "POINT_ESTIMATE_DESCRIPTION", "claim_scope": _claim_scope()}],
        "assignment_panel_integrity_report": {"status": ASSIGNMENT_PANEL_INTEGRITY_PASSED},
        "srm_balance_diagnostic_report": {"status": SRM_BALANCE_DIAGNOSTIC_PASSED},
        "diagnostics_sensitivity_report": {
            "evidence_sufficiency_status": EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW,
        },
        "statistical_promotion_report": {"status": STATISTICAL_PROMOTION_PASSED},
        "instrument_execution_results": [
            {
                "instrument_id": "DID_2X2_POINT_ESTIMATE",
                "effect_estimate_report": {
                    "estimation_status": EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
                    "point_estimate": 12.5,
                },
                "uncertainty_report": {"uncertainty_report_status": "NOT_COMPUTED"},
            }
        ],
        "execution_result": {"execution_status": "INSTRUMENT_EXECUTION_COMPLETED"},
    }
    payload.update(extra)
    return payload


def _ready_evidence():
    return build_post_test_spend_evidence(
        PostTestSpendInput(
            experiment_id="integration_test_001",
            spend_rows=[
                {
                    "geo_unit_id": "g1",
                    "date": "2025-03-01",
                    "spend_value": 100.0,
                    "cell_id": "T1",
                    "cell_role": "treatment",
                },
                {
                    "geo_unit_id": "g2",
                    "date": "2025-03-01",
                    "spend_value": 80.0,
                    "cell_id": "C1",
                    "cell_role": "control",
                },
            ],
            post_period_start="2025-03-01",
            post_period_end="2025-03-31",
            experiment_type=PostTestExperimentType.HOLDOUT,
            source_lineage={"profiler": "GEO_KPI_SPEND_DATA_PROFILER_001"},
        )
    )


def _blocked_evidence():
    return build_post_test_spend_evidence(
        PostTestSpendInput(
            experiment_id="integration_test_blocked",
            spend_rows=[],
            post_period_start="2025-03-01",
            post_period_end="2025-03-31",
            experiment_type=PostTestExperimentType.GO_DARK,
        )
    )


def _assert_kpi_readout_not_blocked(integrated: dict) -> None:
    assert integrated["report_status"] in {
        TRUSTED_REPORT_READY,
        TRUSTED_REPORT_READY_WITH_REDACTIONS,
    }
    assert integrated["report_status"] != TRUSTED_REPORT_BLOCKED_BY_CLAIM_AUTHORIZATION


def test_integrate_ready_spend_evidence_into_trusted_readout() -> None:
    report = generate_trusted_readout_report(_trusted_readout_input())
    evidence = _ready_evidence()
    integrated = integrate_spend_readiness_into_trusted_readout(report, spend_evidence=evidence)
    _assert_kpi_readout_not_blocked(integrated)
    assert integrated["spend_readiness_integrated"] is True
    assert integrated["spend_readiness_summary"]["readiness_status"] == "READY"
    assert integrated["post_test_spend_evidence"]["spend_delta"] == 20.0


def test_output_includes_spend_readiness_summary_and_evidence() -> None:
    report = generate_trusted_readout_report(_trusted_readout_input())
    handoff = build_trusted_readout_spend_handoff(_ready_evidence())
    integrated = integrate_spend_readiness_into_trusted_readout(report, spend_handoff=handoff)
    assert "spend_readiness_summary" in integrated
    assert "post_test_spend_evidence" in integrated
    assert integrated["post_test_spend_evidence"]["experiment_id"] == "integration_test_001"


def test_does_not_recompute_spend_delta() -> None:
    evidence = _ready_evidence()
    handoff = build_trusted_readout_spend_handoff(evidence)
    original_delta = handoff["post_test_spend_evidence"]["spend_delta"]
    report = generate_trusted_readout_report(_trusted_readout_input())
    integrated = integrate_spend_readiness_into_trusted_readout(report, spend_handoff=handoff)
    assert integrated["post_test_spend_evidence"]["spend_delta"] == original_delta


def test_preserves_existing_trusted_readout_fields() -> None:
    report = generate_trusted_readout_report(_trusted_readout_input())
    integrated = integrate_spend_readiness_into_trusted_readout(report, spend_evidence=_ready_evidence())
    assert integrated["request_id"] == "integration_test_001"
    assert integrated["design_id"] == "design_integration_001"
    _assert_kpi_readout_not_blocked(integrated)
    assert integrated["sections"]


def test_blocked_spend_evidence_attaches_blockers_without_blocking_kpi_readout() -> None:
    report = generate_trusted_readout_report(_trusted_readout_input())
    integrated = integrate_spend_readiness_into_trusted_readout(
        report,
        spend_evidence=_blocked_evidence(),
    )
    _assert_kpi_readout_not_blocked(integrated)
    assert integrated["spend_readiness_summary"]["readiness_status"] == "BLOCKED_MISSING_SPEND_SOURCE"
    assert integrated["blocked_efficiency_metrics"]
    assert "EFFICIENCY_METRICS_NOT_READY" in integrated["blocked_efficiency_metrics"]


def test_missing_spend_evidence_marks_not_requested() -> None:
    report = generate_trusted_readout_report(_trusted_readout_input())
    integrated = integrate_spend_readiness_into_trusted_readout(report)
    _assert_kpi_readout_not_blocked(integrated)
    assert integrated["spend_readiness_summary"]["readiness_status"] == SPEND_READINESS_NOT_REQUESTED
    assert integrated["spend_readiness_integrated"] is False
    assert integrated["post_test_spend_evidence"] is None


def test_missing_spend_preserves_kpi_fields() -> None:
    report = generate_trusted_readout_report(_trusted_readout_input())
    integrated = integrate_spend_readiness_into_trusted_readout(report)
    point_section = next(s for s in integrated["sections"] if s["section_type"] == "POINT_ESTIMATE_SUMMARY")
    assert point_section["section_status"] != "SECTION_BLOCKED"


def test_does_not_compute_efficiency_metrics() -> None:
    integrated = integrate_spend_readiness_into_trusted_readout(
        generate_trusted_readout_report(_trusted_readout_input()),
        spend_evidence=_ready_evidence(),
    )
    metrics = integrated["efficiency_metric_readiness"]
    assert metrics["cost_per_incremental_kpi"] == "NOT_COMPUTED"
    assert metrics["roas"] == "NOT_COMPUTED"
    assert metrics["profit_roi"] == "NOT_COMPUTED"


def test_roi_claim_authorization_delegated_not_evaluated() -> None:
    integrated = integrate_spend_readiness_into_trusted_readout(
        generate_trusted_readout_report(_trusted_readout_input()),
        spend_evidence=_ready_evidence(),
    )
    assert integrated["roi_claim_authorization_status"] == "NOT_EVALUATED"
    assert integrated["claim_authorization_owner"] == "CLAIM_AUTHORIZATION_RUNTIME_001"


def test_mip_compatibility_fields_present() -> None:
    integrated = integrate_spend_readiness_into_trusted_readout(
        generate_trusted_readout_report(_trusted_readout_input()),
        spend_evidence=_ready_evidence(),
    )
    assert integrated["mip_post_test_spend_readiness_result"] == "READY"
    assert integrated["mip_observed_spend_delta_readiness"] is True
    assert integrated["spend_lineage"]
    assert isinstance(integrated["spend_warnings"], list)
    assert "blocked_efficiency_metrics" in integrated


def test_malformed_spend_handoff_returns_blocked_section() -> None:
    report = generate_trusted_readout_report(_trusted_readout_input())
    integrated = integrate_spend_readiness_into_trusted_readout(report, spend_handoff={"invalid": True})
    _assert_kpi_readout_not_blocked(integrated)
    assert integrated["spend_readiness_summary"]["readiness_status"] == "BLOCKED_MALFORMED_SPEND_HANDOFF"


def test_generate_trusted_readout_report_with_spend_readiness() -> None:
    integrated = generate_trusted_readout_report_with_spend_readiness(
        _trusted_readout_input(),
        spend_evidence=_ready_evidence(),
    )
    assert integrated["spend_readiness_integrated"] is True
    _assert_kpi_readout_not_blocked(integrated)


def test_blocked_evidence_readiness_status_preserved() -> None:
    evidence = _blocked_evidence()
    assert evidence.readiness_status == PostTestSpendReadinessStatus.BLOCKED_MISSING_SPEND_SOURCE
    integrated = integrate_spend_readiness_into_trusted_readout(
        generate_trusted_readout_report(_trusted_readout_input()),
        spend_evidence=evidence,
    )
    assert integrated["post_test_spend_evidence"]["readiness_status"] == "BLOCKED_MISSING_SPEND_SOURCE"
