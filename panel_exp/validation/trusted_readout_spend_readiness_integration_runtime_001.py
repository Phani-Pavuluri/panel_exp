"""GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001 — spend readiness integration."""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from panel_exp.validation.post_test_spend_readiness_adapter_runtime_001 import (
    SOURCE_ARTIFACT as _SPEND_ADAPTER_ARTIFACT,
    PostTestSpendEvidence,
    PostTestSpendReadinessStatus,
    build_trusted_readout_spend_handoff,
)
from panel_exp.validation.trusted_readout_report_runtime_001 import (
    TrustedReadoutReportRuntimeReport,
    generate_trusted_readout_report,
)

_ARTIFACT_ID = "GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001"
_SCOPE = "trusted_readout_spend_readiness_integration_no_roi_calculator_or_claim_authorization"
_VERDICT = "trusted_readout_spend_readiness_integrated_no_roi_calculator_or_claim_authorization"
_RECOMMENDED_NEXT = "GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001"
_RETURN_TO_LANE_A = "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001"
_CLAIM_AUTHORIZATION_OWNER = "CLAIM_AUTHORIZATION_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001_summary.json"
)

SPEND_READINESS_NOT_REQUESTED = "NOT_REQUESTED"
SPEND_HANDOFF_MALFORMED = "BLOCKED_MALFORMED_SPEND_HANDOFF"

_SPEND_EXTENSION_KEYS = (
    "spend_readiness_summary",
    "post_test_spend_evidence",
    "efficiency_metric_readiness",
    "blocked_efficiency_metrics",
    "diagnostic_efficiency_metrics",
    "roi_claim_authorization_status",
    "spend_lineage",
    "spend_warnings",
    "spend_readiness_integrated",
    "spend_readiness_source_artifact",
    "claim_authorization_owner",
    "mip_post_test_spend_readiness_result",
    "mip_observed_spend_delta_readiness",
)


def _trusted_readout_as_dict(trusted_readout: Any) -> dict[str, Any]:
    if isinstance(trusted_readout, dict):
        return copy.deepcopy(trusted_readout)
    if isinstance(trusted_readout, TrustedReadoutReportRuntimeReport):
        return asdict(trusted_readout)
    if is_dataclass(trusted_readout):
        return asdict(trusted_readout)
    raise TypeError(
        "trusted_readout must be a dict or TrustedReadoutReportRuntimeReport-like dataclass"
    )


def _not_requested_spend_section() -> dict[str, Any]:
    return {
        "spend_readiness_summary": {
            "readiness_status": SPEND_READINESS_NOT_REQUESTED,
            "spend_delta_ready": False,
        },
        "post_test_spend_evidence": None,
        "efficiency_metric_readiness": {
            "cost_per_incremental_kpi": "NOT_COMPUTED",
            "roas": "NOT_COMPUTED",
            "profit_roi": "NOT_COMPUTED",
        },
        "blocked_efficiency_metrics": [],
        "diagnostic_efficiency_metrics": [],
        "roi_claim_authorization_status": "NOT_EVALUATED",
        "spend_lineage": {},
        "spend_warnings": [],
        "spend_readiness_integrated": False,
        "spend_readiness_source_artifact": None,
        "claim_authorization_owner": _CLAIM_AUTHORIZATION_OWNER,
        "mip_post_test_spend_readiness_result": SPEND_READINESS_NOT_REQUESTED,
        "mip_observed_spend_delta_readiness": False,
    }


def _malformed_spend_section(reason: str) -> dict[str, Any]:
    return {
        "spend_readiness_summary": {
            "readiness_status": SPEND_HANDOFF_MALFORMED,
            "spend_delta_ready": False,
        },
        "post_test_spend_evidence": None,
        "efficiency_metric_readiness": {
            "cost_per_incremental_kpi": "NOT_COMPUTED",
            "roas": "NOT_COMPUTED",
            "profit_roi": "NOT_COMPUTED",
        },
        "blocked_efficiency_metrics": [SPEND_HANDOFF_MALFORMED, reason],
        "diagnostic_efficiency_metrics": [],
        "roi_claim_authorization_status": "NOT_EVALUATED",
        "spend_lineage": {},
        "spend_warnings": [reason],
        "spend_readiness_integrated": False,
        "spend_readiness_source_artifact": _SPEND_ADAPTER_ARTIFACT,
        "claim_authorization_owner": _CLAIM_AUTHORIZATION_OWNER,
        "mip_post_test_spend_readiness_result": SPEND_HANDOFF_MALFORMED,
        "mip_observed_spend_delta_readiness": False,
    }


def _validate_spend_handoff(spend_handoff: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not isinstance(spend_handoff, dict):
        return ["SPEND_HANDOFF_NOT_A_DICT"]
    if "spend_readiness_summary" not in spend_handoff:
        issues.append("MISSING_SPEND_READINESS_SUMMARY")
    if "post_test_spend_evidence" not in spend_handoff:
        issues.append("MISSING_POST_TEST_SPEND_EVIDENCE")
    return issues


def _resolve_spend_handoff(
    *,
    spend_evidence: PostTestSpendEvidence | None,
    spend_handoff: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    if spend_handoff is not None and spend_evidence is not None:
        return None, ["SPEND_EVIDENCE_AND_HANDOFF_BOTH_PROVIDED"]
    if spend_evidence is not None:
        return build_trusted_readout_spend_handoff(spend_evidence), []
    if spend_handoff is not None:
        issues = _validate_spend_handoff(spend_handoff)
        if issues:
            return None, issues
        return copy.deepcopy(spend_handoff), []
    return None, []


def _mip_fields_from_handoff(handoff: dict[str, Any]) -> dict[str, Any]:
    summary = handoff.get("spend_readiness_summary") or {}
    evidence = handoff.get("post_test_spend_evidence") or {}
    readiness_status = summary.get("readiness_status", SPEND_READINESS_NOT_REQUESTED)
    spend_delta_ready = bool(summary.get("spend_delta_ready"))
    if not spend_delta_ready and isinstance(evidence, dict):
        spend_delta_ready = evidence.get("spend_delta") is not None and readiness_status == "READY"
    return {
        "mip_post_test_spend_readiness_result": readiness_status,
        "mip_observed_spend_delta_readiness": spend_delta_ready,
    }


def _attach_spend_extensions(
    trusted_readout: dict[str, Any],
    handoff: dict[str, Any],
) -> dict[str, Any]:
    merged = copy.deepcopy(trusted_readout)
    roi_status = handoff.get("roi_claim_authorization_status")
    if roi_status is None:
        roi_status = merged.get("roi_claim_authorization_status", "NOT_EVALUATED")
    extensions = {
        "spend_readiness_summary": handoff.get("spend_readiness_summary"),
        "post_test_spend_evidence": handoff.get("post_test_spend_evidence"),
        "efficiency_metric_readiness": handoff.get("efficiency_metric_readiness")
        or {
            "cost_per_incremental_kpi": "NOT_COMPUTED",
            "roas": "NOT_COMPUTED",
            "profit_roi": "NOT_COMPUTED",
        },
        "blocked_efficiency_metrics": list(handoff.get("blocked_efficiency_metrics") or []),
        "diagnostic_efficiency_metrics": list(handoff.get("diagnostic_efficiency_metrics") or []),
        "roi_claim_authorization_status": roi_status,
        "spend_lineage": dict(handoff.get("spend_lineage") or {}),
        "spend_warnings": list(handoff.get("spend_warnings") or []),
        "spend_readiness_integrated": True,
        "spend_readiness_source_artifact": _SPEND_ADAPTER_ARTIFACT,
        "claim_authorization_owner": merged.get("claim_authorization_owner")
        or _CLAIM_AUTHORIZATION_OWNER,
    }
    extensions.update(_mip_fields_from_handoff(handoff))
    merged.update(extensions)
    return merged


def integrate_spend_readiness_into_trusted_readout(
    trusted_readout: dict[str, Any] | TrustedReadoutReportRuntimeReport,
    *,
    spend_evidence: PostTestSpendEvidence | None = None,
    spend_handoff: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Attach post-test spend readiness sections to an existing trusted readout packet."""
    base = _trusted_readout_as_dict(trusted_readout)
    resolved, issues = _resolve_spend_handoff(
        spend_evidence=spend_evidence,
        spend_handoff=spend_handoff,
    )
    if issues:
        if any(
            issue in {"SPEND_EVIDENCE_AND_HANDOFF_BOTH_PROVIDED", "SPEND_HANDOFF_NOT_A_DICT"}
            or issue.startswith("MISSING_")
            for issue in issues
        ):
            merged = copy.deepcopy(base)
            merged.update(_malformed_spend_section(";".join(issues)))
            return merged
    if resolved is None:
        merged = copy.deepcopy(base)
        merged.update(_not_requested_spend_section())
        return merged
    return _attach_spend_extensions(base, resolved)


def generate_trusted_readout_report_with_spend_readiness(
    input_data: Any,
    *,
    spend_evidence: PostTestSpendEvidence | None = None,
    spend_handoff: dict[str, Any] | None = None,
    config: Any = None,
) -> dict[str, Any]:
    """Generate trusted readout report and integrate optional spend readiness."""
    report = generate_trusted_readout_report(input_data, config)
    if isinstance(report, list):
        raise ValueError("batch trusted readout generation is not supported for spend integration")
    return integrate_spend_readiness_into_trusted_readout(
        report,
        spend_evidence=spend_evidence,
        spend_handoff=spend_handoff,
    )


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=_REPO)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    from panel_exp.validation.assignment_panel_integrity_runtime_001 import ASSIGNMENT_PANEL_INTEGRITY_PASSED
    from panel_exp.validation.estimator_inference_did_executor_003 import EFFECT_ESTIMATE_COMPUTED_POINT_ONLY
    from panel_exp.validation.post_test_spend_readiness_adapter_runtime_001 import (
        PostTestExperimentType,
        PostTestSpendInput,
        build_post_test_spend_evidence,
    )
    from panel_exp.validation.readout_diagnostics_sensitivity_runtime_001 import (
        EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW,
    )
    from panel_exp.validation.srm_balance_readout_diagnostic_001 import SRM_BALANCE_DIAGNOSTIC_PASSED
    from panel_exp.validation.statistical_promotion_thresholds_001 import STATISTICAL_PROMOTION_PASSED

    claim_scope = {"estimand": "STANDARD_INCREMENTALITY", "metric_kpi": "sales"}
    base_input = {
        "request_id": "spend_integration_validation",
        "design_id": "design_spend_integration",
        "claim_scope": claim_scope,
        "claim_requests": [{"claim_type": "POINT_ESTIMATE_DESCRIPTION", "claim_scope": claim_scope}],
        "assignment_panel_integrity_report": {"status": ASSIGNMENT_PANEL_INTEGRITY_PASSED},
        "srm_balance_diagnostic_report": {"status": SRM_BALANCE_DIAGNOSTIC_PASSED},
        "diagnostics_sensitivity_report": {"evidence_sufficiency_status": EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW},
        "statistical_promotion_report": {"status": STATISTICAL_PROMOTION_PASSED},
        "instrument_execution_results": [
            {
                "instrument_id": "DID_2X2_POINT_ESTIMATE",
                "effect_estimate_report": {
                    "estimation_status": EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
                    "point_estimate": 1.0,
                },
                "uncertainty_report": {"uncertainty_report_status": "NOT_COMPUTED"},
            }
        ],
        "execution_result": {"execution_status": "INSTRUMENT_EXECUTION_COMPLETED"},
    }
    evidence = build_post_test_spend_evidence(
        PostTestSpendInput(
            experiment_id="spend_integration_validation",
            spend_rows=[
                {
                    "geo_unit_id": "g1",
                    "date": "2025-03-01",
                    "spend_value": 100.0,
                    "cell_id": "T1",
                    "cell_role": "treatment",
                }
            ],
            post_period_start="2025-03-01",
            post_period_end="2025-03-31",
            experiment_type=PostTestExperimentType.GO_DARK,
            counterfactual_or_bau_spend=200.0,
        )
    )
    integrated = generate_trusted_readout_report_with_spend_readiness(
        base_input,
        spend_evidence=evidence,
    )
    assert integrated["report_status"]
    assert integrated["spend_readiness_integrated"] is True

    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "geox_trusted_readout_spend_readiness_integration_runtime",
        "lane": "Lane B - Final trusted readout spend ROI readiness",
        "status": "completed",
        "scope": _SCOPE,
        "base_commit": _git_commit(),
        "depends_on": [
            "GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001",
            "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001",
            "TRUSTED_READOUT_REPORT_RUNTIME_001",
            "CLAIM_AUTHORIZATION_RUNTIME_001",
            "MIP_GEOX_READOUT_INPUT_REQUIREMENTS_AND_HANDOFF_CONTRACT_001",
        ],
        "trusted_readout_spend_readiness_integration_completed": True,
        "post_test_spend_handoff_consumed": True,
        "trusted_readout_extension_fields_added": True,
        "spend_readiness_summary_integrated": True,
        "post_test_spend_evidence_integrated": True,
        "blocked_efficiency_metrics_integrated": True,
        "spend_lineage_integrated": True,
        "spend_warnings_integrated": True,
        "roi_claim_authorization_delegated": True,
        "mip_expected_output_fields_supported": True,
        "kpi_readout_not_blocked_by_missing_spend": True,
        "runtime_implemented": True,
        "spend_delta_recomputed": False,
        "cost_per_incremental_kpi_computed": False,
        "roi_roas_computed": False,
        "roi_calculator_runtime_created": False,
        "spend_ingestion_system_created": False,
        "final_results_module_created": False,
        "claim_authorization_duplicated": False,
        "roi_claim_authorized": False,
        "roas_claim_authorized": False,
        "business_lift_claim_authorized": False,
        "decision_recommendation_authorized": False,
        "production_readout_authorized": False,
        "method_promoted": False,
        "instrument_promoted": False,
        "catalog_unblocked": False,
        "mip_orchestration_implemented": False,
        "dataset_loading_implemented": False,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "return_to_lane_a_after": _RETURN_TO_LANE_A,
        "final_verdict": _VERDICT,
        "validation_sample_report_status": integrated.get("report_status"),
        "validation_sample_spend_readiness_status": integrated["spend_readiness_summary"][
            "readiness_status"
        ],
    }
    if write_summary:
        path = summary_path or _DEFAULT_SUMMARY
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GEOX trusted readout spend readiness integration validation"
    )
    parser.add_argument("--write-summary", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    summary = run_validation(write_summary=args.write_summary, summary_path=args.summary_path)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
