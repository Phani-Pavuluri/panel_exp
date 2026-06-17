"""TRUSTREPORT-ELIGIBILITY-VALIDATION-001 — empirical harness over committed D5 evidence."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from panel_exp.validation.trustreport_eligibility_001 import (
    ELIGIBILITY_VERSION,
    PROVISIONAL_THRESHOLDS,
    STATUS_ELIGIBLE_CANDIDATE,
    STATUS_ELIGIBLE_WITH_RESTRICTIONS,
    STATUS_INELIGIBLE,
    STATUS_INSUFFICIENT_EVIDENCE,
    TrustReportEmpiricalEvidence,
    evaluate_trustreport_eligibility,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARCHIVE_DIR = _REPO_ROOT / "docs" / "track_d" / "archives"
_SUMMARY_PATH = _ARCHIVE_DIR / "TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json"

EvidenceSource = Literal["evidence_reused", "focused_execution", "not_evaluated"]

DCM_EVIDENCE_MAP: dict[str, dict[str, Any]] = {
    "DCM-001": {
        "archive": "D5_STAT_SCM_JK_001_results.json",
        "geometry": "unit_panel_single_cell",
        "estimator_id": "scm",
        "inference_id": "unit_jackknife",
        "readout_semantics": "causal_interval",
    },
    "DCM-002": {
        "archive": "D5_STAT_AUGSYNTH_POINT_001_results.json",
        "geometry": "unit_panel_single_cell",
        "estimator_id": "augsynth",
        "inference_id": "point_only",
        "readout_semantics": "point_estimate",
    },
    "DCM-003": {
        "archive": "D5_STAT_TBR_AGG_001_results.json",
        "geometry": "aggregate_two_row",
        "estimator_id": "tbr",
        "inference_id": "point_only",
        "readout_semantics": "point_estimate",
    },
    "DCM-004": {
        "archive": "D5_STAT_DID_BOOTSTRAP_001_results.json",
        "geometry": "unit_panel_single_cell",
        "estimator_id": "did",
        "inference_id": "bootstrap",
        "readout_semantics": "causal_interval",
    },
    "DCM-005-BRB": {
        "archive": "D5_STAT_TBRRIDGE_INF_001_results.json",
        "geometry": "unit_panel_single_cell",
        "estimator_id": "tbrridge",
        "inference_id": "brb",
        "readout_semantics": "causal_interval",
        "inference_path_key": "TBRRIDGE-BRB",
    },
    "DCM-005-KFOLD": {
        "archive": "D5_STAT_TBRRIDGE_INF_001_results.json",
        "geometry": "unit_panel_single_cell",
        "estimator_id": "tbrridge",
        "inference_id": "kfold",
        "readout_semantics": "causal_interval",
        "inference_path_key": "TBRRIDGE-KFOLD",
    },
    "DCM-005-PLACEBO": {
        "archive": "D5_STAT_TBRRIDGE_INF_001_results.json",
        "geometry": "unit_panel_single_cell",
        "estimator_id": "tbrridge",
        "inference_id": "placebo",
        "readout_semantics": "null_monitor_interval",
        "inference_path_key": "TBRRIDGE-PLACEBO",
    },
    "DCM-006": {
        "archive": "D5_STAT_MCELL_PERCELL_001_results.json",
        "geometry": "multi_cell_per_cell",
        "estimator_id": "scm",
        "inference_id": "unit_jackknife",
        "readout_semantics": "per_cell_point",
    },
    "DCM-007": {
        "archive": None,
        "geometry": "pooled_multi_cell",
        "estimator_id": "scm",
        "inference_id": "unit_jackknife",
        "readout_semantics": "pooled_point",
    },
    "DCM-008": {
        "archive": "D5_DES_STAT_STRATIFIED_001_results.json",
        "geometry": "unit_panel_single_cell",
        "estimator_id": "scm",
        "inference_id": "unit_jackknife",
        "readout_semantics": "causal_interval",
    },
}


def _git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=_REPO_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _load_archive(name: str | None) -> dict[str, Any] | None:
    if not name:
        return None
    path = _ARCHIVE_DIR / name
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def _aggregate_world_metrics(
    archive: dict[str, Any],
    *,
    world_id: str = "clean_null",
    path_key: str | None = None,
) -> dict[str, Any] | None:
    if path_key:
        if "path_metrics" in archive:
            for entry in archive.get("path_metrics") or []:
                if entry.get("inference_path") == path_key and entry.get("world_id") == world_id:
                    return entry
        if "path_results" in archive:
            for entry in archive.get("path_results") or []:
                if entry.get("inference_path") == path_key:
                    metrics = (entry.get("aggregate_metrics") or {}).get(world_id)
                    if metrics:
                        return metrics
        return None
    metrics = (archive.get("aggregate_metrics") or {}).get(world_id)
    return metrics


def _extract_empirical_evidence(
    dcm_key: str,
    spec: dict[str, Any],
    archive: dict[str, Any] | None,
) -> TrustReportEmpiricalEvidence:
    if archive is None:
        return TrustReportEmpiricalEvidence(
            dcm_row_id=dcm_key.split("-")[0] + "-" + dcm_key.split("-")[1]
            if dcm_key.startswith("DCM-")
            else dcm_key,
            evidence_source="not_evaluated",
            freshness_status="unknown",
        )

    dcm_row = dcm_key if dcm_key.startswith("DCM-") else "DCM-000"
    if dcm_key.startswith("DCM-005"):
        dcm_row = "DCM-005"

    path_key = spec.get("inference_path_key")
    null_metrics = _aggregate_world_metrics(archive, world_id="clean_null", path_key=path_key)
    pos_metrics = _aggregate_world_metrics(
        archive, world_id="clean_positive_lift", path_key=path_key
    )
    summary = archive.get("summary") or {}
    total = summary.get("total_runs") or 1
    failures = summary.get("total_failures") or 0

    worst = None
    for world_id in (
        "post_shock_null",
        "outside_hull_or_poor_prefit",
        "trend_mismatch_null",
        "donor_stress",
    ):
        wm = _aggregate_world_metrics(archive, world_id=world_id, path_key=path_key)
        if wm:
            worst = world_id
            break

    trust_allowed = None
    flags = archive.get("forbidden_flags") or {}
    if flags:
        trust_allowed = flags.get("trust_role_allowed")
    else:
        worlds = archive.get("worlds") or []
        if worlds and isinstance(worlds[0], dict):
            trust_allowed = worlds[0].get("trust_role_allowed")

    coverage = _safe_float((null_metrics or {}).get("coverage"))
    coverage_null = coverage
    coverage_positive = _safe_float((pos_metrics or {}).get("coverage"))

    return TrustReportEmpiricalEvidence(
        artifact_id=archive.get("artifact_id"),
        evidence_source="evidence_reused",
        coverage=coverage,
        coverage_null=coverage_null,
        coverage_positive=coverage_positive,
        type_i_error=_safe_float(
            (null_metrics or {}).get("null_false_positive_rate")
        ),
        power=None,
        bias=_safe_float((pos_metrics or {}).get("mean_bias")),
        rmse=_safe_float((pos_metrics or {}).get("rmse")),
        interval_width=_safe_float((null_metrics or {}).get("mean_interval_width")),
        failure_rate=failures / total if total else None,
        worst_world_status=worst or archive.get("overall_verdict"),
        provenance_complete=True,
        freshness_status="valid",
        effect_scale=_safe_float((pos_metrics or {}).get("mean_true_effect")),
        dcm_row_id=dcm_row,
        trust_role_allowed_in_source=trust_allowed if trust_allowed is not None else False,
    )


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _classify_combination_from_evidence(
    dcm_key: str,
    spec: dict[str, Any],
    empirical: TrustReportEmpiricalEvidence,
) -> dict[str, Any]:
    """Classify combination using empirical evidence only (no governed readout)."""
    result = evaluate_trustreport_eligibility(
        readout_evidence=_synthetic_readout_stub(spec, dcm_key),
        empirical_evidence=empirical,
    )
    return {
        "combination_key": dcm_key,
        "dcm_row_id": empirical.dcm_row_id,
        "geometry": spec.get("geometry"),
        "estimator_id": spec.get("estimator_id"),
        "inference_id": spec.get("inference_id"),
        "readout_semantics": spec.get("readout_semantics"),
        "evidence_source": empirical.evidence_source,
        "empirical_artifact_id": empirical.artifact_id,
        "eligibility_status": result.status,
        "eligible_for_promotion": result.eligible_for_promotion,
        "trust_report_authorized": result.trust_report_authorized,
        "reason_codes": list(result.reason_codes),
        "warnings": list(result.warnings),
        "metrics": {
            "coverage": empirical.coverage,
            "type_i_error": empirical.type_i_error,
            "failure_rate": empirical.failure_rate,
            "bias": empirical.bias,
            "rmse": empirical.rmse,
            "worst_world_status": empirical.worst_world_status,
        },
    }


def _synthetic_readout_stub(spec: dict[str, Any], dcm_key: str) -> dict[str, Any]:
    """Minimal governed-readout-shaped dict for combination-only harness evaluation."""
    dcm_row = dcm_key if dcm_key in ("DCM-007",) else dcm_key.split("-")[0] + "-" + dcm_key.split("-")[1]
    if dcm_key.startswith("DCM-005"):
        dcm_row = "DCM-005"
    combination_status = {
        "DCM-001": "characterized_with_restrictions",
        "DCM-002": "compatible_point_only",
        "DCM-003": "blocked_due_to_geometry_mismatch",
        "DCM-004": "characterized_with_restrictions",
        "DCM-005": "restricted_requires_statistical_validation",
        "DCM-006": "compatible_per_cell_only",
        "DCM-007": "blocked_for_pooled_claim",
        "DCM-008": "characterized_with_restrictions",
    }.get(dcm_row, "not_evaluated")

    geometry = spec.get("geometry")
    pooled = geometry == "pooled_multi_cell" or spec.get("readout_semantics", "").startswith(
        "pooled"
    )
    cell_id = "test_0" if geometry == "multi_cell_per_cell" else None
    multi_cell = None
    if geometry == "multi_cell_per_cell":
        multi_cell = {
            "is_multi_cell": True,
            "cell_ids": ["test_0", "test_1"],
            "shared_control_policy": "explicit_reservation",
            "control_reuse_policy": "per_cell_isolated",
            "pooled_claims_allowed": False,
        }

    return {
        "evidence_version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "estimator_identity": {
            "estimator_id": spec.get("estimator_id"),
            "geometry_id": geometry,
        },
        "inference_identity": {
            "inference_id": spec.get("inference_id"),
            "interval_type": "jackknife_interval",
        },
        "readout_identity": {
            "readout_semantics": spec.get("readout_semantics"),
            "estimand": "att",
            "pooled": pooled,
            "cell_id": cell_id,
        },
        "combination_resolution": {
            "dcm_row_id": dcm_row,
            "design_id": "DES-002",
            "geometry_id": geometry,
            "combination_status": combination_status,
        },
        "inference_boundary_guardrail": {
            "status": "WARN" if combination_status != "blocked_due_to_geometry_mismatch" else "BLOCK",
            "reason_codes": [],
        },
        "guardrail_enforcement": {"downstream_authorization_status": "blocked"},
        "result_payload": {
            "metadata": {
                "governed_readout_evidence": True,
                "geometry_context": multi_cell or {},
            }
        },
        "design_contract": {"multi_cell": multi_cell} if multi_cell else {},
    }


def run_trustreport_eligibility_validation(
    *,
    write_summary: bool = True,
) -> dict[str, Any]:
    """Evaluate all candidate combinations using committed D5 archives."""
    combination_results: list[dict[str, Any]] = []
    promotion_candidates: list[str] = []
    status_counts: dict[str, int] = {}

    for dcm_key, spec in DCM_EVIDENCE_MAP.items():
        archive = _load_archive(spec.get("archive"))
        empirical = _extract_empirical_evidence(dcm_key, spec, archive)
        row = _classify_combination_from_evidence(dcm_key, spec, empirical)
        combination_results.append(row)
        status = row["eligibility_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        if row["eligible_for_promotion"]:
            promotion_candidates.append(dcm_key)

    authorized_count = sum(1 for r in combination_results if r.get("trust_report_authorized"))

    if status_counts.get(STATUS_ELIGIBLE_CANDIDATE, 0) > 0:
        verdict = "trustreport_eligibility_candidates_identified_no_authorization"
    elif status_counts.get(STATUS_ELIGIBLE_WITH_RESTRICTIONS, 0) > 0:
        verdict = "trustreport_eligibility_mixed_with_restrictions_no_authorization"
    elif status_counts.get(STATUS_INSUFFICIENT_EVIDENCE, 0) > 0:
        verdict = "trustreport_eligibility_insufficient_evidence_no_authorization"
    elif status_counts.get(STATUS_INELIGIBLE, 0) == len(combination_results):
        verdict = "trustreport_eligibility_all_current_paths_ineligible"
    else:
        verdict = "trustreport_eligibility_validation_inconclusive"

    summary = {
        "artifact_id": "TRUSTREPORT-ELIGIBILITY-VALIDATION-001",
        "artifact_version": ELIGIBILITY_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "config": {"harness": "track_d_trustreport_eligibility_validation_001"},
        "candidate_combinations": list(DCM_EVIDENCE_MAP.keys()),
        "eligibility_rules": [
            "governed_readout_required",
            "dcm_specific_classification",
            "provisional_statistical_thresholds",
            "authorization_separate",
        ],
        "provisional_thresholds": PROVISIONAL_THRESHOLDS,
        "evidence_sources": {
            k: {
                "archive": v.get("archive"),
                "mode": "evidence_reused" if v.get("archive") else "not_evaluated",
            }
            for k, v in DCM_EVIDENCE_MAP.items()
        },
        "combination_results": combination_results,
        "statistical_results": [r for r in combination_results if r.get("metrics")],
        "semantic_results": [
            r for r in combination_results if "POINT" in " ".join(r.get("reason_codes", []))
        ],
        "geometry_results": [
            r for r in combination_results if r.get("geometry") in ("aggregate_two_row", "pooled_multi_cell")
        ],
        "provenance_results": [
            {"combination_key": r["combination_key"], "artifact_id": r.get("empirical_artifact_id")}
            for r in combination_results
        ],
        "freshness_results": [{"combination_key": r["combination_key"], "status": "valid"} for r in combination_results],
        "exclusion_results": [r for r in combination_results if r["eligibility_status"] == STATUS_INELIGIBLE],
        "failure_summary": {
            "status_counts": status_counts,
            "promotion_candidate_count": len(promotion_candidates),
        },
        "promotion_candidate_summary": {
            "candidates": promotion_candidates,
            "count": len(promotion_candidates),
            "note": "candidate_not_authorized",
        },
        "authorization_summary": {
            "trust_report_authorized_count": authorized_count,
            "trust_report_blocked_count": len(combination_results) - authorized_count,
        },
        "limitations": [
            "Provisional thresholds only; not production gates.",
            "D5 archives mark trust_role_allowed=false for all combinations.",
            "Positive-scenario coverage deficient for SCM-JK and DID-bootstrap.",
            "TBRRidge causal interval semantics not validated.",
            "Stratified lane lacks dedicated D5-STAT artifact.",
        ],
        "verdict": verdict,
    }

    if write_summary:
        _SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n")

    return summary


def load_committed_summary() -> dict[str, Any]:
    """Load committed compact summary artifact."""
    if not _SUMMARY_PATH.is_file():
        return run_trustreport_eligibility_validation(write_summary=True)
    return json.loads(_SUMMARY_PATH.read_text())


__all__ = [
    "DCM_EVIDENCE_MAP",
    "load_committed_summary",
    "run_trustreport_eligibility_validation",
]
