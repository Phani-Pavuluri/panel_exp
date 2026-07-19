"""Deterministic fixture-only GeoX/MIP envelope dry-run runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .geox_mip_artifact_envelope import (
    GeoXMIPArtifactEnvelope,
    GeoXMIPArtifactKind,
    GeoXMIPAuthorizationStatus,
    GeoXMIPConsumptionStatus,
    GeoXMIPDownstreamEligibility,
    build_geox_mip_artifact_envelope,
    serialize_geox_mip_artifact_envelope,
    validate_geox_mip_artifact_envelope,
)


@dataclass(frozen=True)
class GeoXMIPArtifactEnvelopeDryRunCase:
    case_id: str
    case_name: str
    fixture_id: str
    envelope: GeoXMIPArtifactEnvelope
    validation_passed: bool
    validation_errors: tuple[str, ...]


@dataclass(frozen=True)
class GeoXMIPArtifactEnvelopeDryRunResult:
    dry_run_id: str
    envelope_version: str
    cases: tuple[GeoXMIPArtifactEnvelopeDryRunCase, ...]
    serialized_cases: tuple[dict[str, Any], ...]
    all_cases_valid: bool
    production_authorization_preserved: bool
    mip_repository_modified: bool
    summary: dict[str, Any]


_FORBIDDEN_FLAGS = {
    "production_inference_authorized": False,
    "assignment_authorized": False,
    "causal_readout_authorized": False,
    "calibration_signal_export_authorized": False,
    "mip_experiment_evidence_export_authorized": False,
    "trust_report_production_assembly_authorized": False,
    "decision_surface_authorized": False,
    "recommendation_contract_authorized": False,
    "llm_decisioning_authorized": False,
    "budget_optimization_authorized": False,
    "selector_router_runtime_authorized": False,
    "multicell_production_claim_authorized": False,
    "agent_work_authorized": False,
}


def _fixture_envelope(kind: GeoXMIPArtifactKind, fixture_id: str, *, authorization: str = "not_authorized", consumption: str, blocked_reasons: tuple[str, ...] = (), warnings: tuple[str, ...] = ()) -> GeoXMIPArtifactEnvelope:
    return build_geox_mip_artifact_envelope(
        envelope_version="1.0.0",
        artifact_kind=kind,
        artifact_id=f"artifact-{fixture_id}",
        artifact_uri=f"fixture://geox-mip/{fixture_id}",
        source_system="panel_exp",
        source_repo="/Users/phani/Desktop/panel_exp",
        source_commit="827a5b8",
        created_at="2026-07-19T00:00:00Z",
        run_id=f"dry-run-{fixture_id}",
        experiment_id="fixture-experiment-001",
        request_id=f"request-{fixture_id}",
        input_data_fingerprint=f"sha256:fixture-{fixture_id}",
        method_family="SCM",
        instrument_id="SCM_UNIT_JACKKNIFE",
        estimand="ATT",
        kpi="revenue",
        geo_scope="fixture_geos",
        time_window="pre:2025-01;post:2025-02",
        assignment_scope="fixture_scope",
        diagnostic_status="diagnostic",
        method_readiness_status="candidate_gated",
        release_gate_status="required",
        authorization_status=authorization,
        blocked_reasons=blocked_reasons,
        warnings=warnings,
        upstream_artifacts=("fixture://geox-mip/source-fixture-001",),
        downstream_eligibility=GeoXMIPDownstreamEligibility.EXPLAIN_ONLY,
        mip_consumption_status=consumption,
        provenance={"fixture_id": fixture_id, "non_production": True},
        schema_hash="sha256:geox-mip-envelope-v1",
    )


def _cases() -> tuple[tuple[str, str, str, GeoXMIPArtifactEnvelope], ...]:
    return (
        ("A", "diagnostic_only_assignment_candidate", "case-a-assignment", _fixture_envelope(GeoXMIPArtifactKind.ASSIGNMENT_CANDIDATE, "case-a-assignment", consumption="diagnostic_context_only", warnings=("fixture_only",))),
        ("B", "blocked_readout_packet", "case-b-readout", _fixture_envelope(GeoXMIPArtifactKind.READOUT_PACKET, "case-b-readout", authorization="blocked", consumption="blocked", blocked_reasons=("authorization_missing", "release_gate_required"))),
        ("C", "failure_packet_propagation", "case-c-failure", _fixture_envelope(GeoXMIPArtifactKind.FAILURE_PACKET, "case-c-failure", consumption="answerability_context_only", blocked_reasons=("panel_validation_failed",), warnings=("no_recommendation_generated",))),
        ("D", "post_test_spend_diagnostic_handoff", "case-d-spend", _fixture_envelope(GeoXMIPArtifactKind.POST_TEST_SPEND_EVIDENCE, "case-d-spend", consumption="diagnostic_context_only", warnings=("no_calibration_export",))),
        ("E", "calibration_signal_candidate_blocked", "case-e-calibration", _fixture_envelope(GeoXMIPArtifactKind.CALIBRATION_SIGNAL_CANDIDATE, "case-e-calibration", authorization="blocked", consumption="blocked", blocked_reasons=("calibration_mapping_missing", "authorization_missing"))),
        ("F", "experiment_evidence_candidate_blocked", "case-f-evidence", _fixture_envelope(GeoXMIPArtifactKind.EXPERIMENT_EVIDENCE_CANDIDATE, "case-f-evidence", authorization="blocked", consumption="blocked", blocked_reasons=("evidence_mapping_missing", "authorization_missing"))),
    )


def build_non_production_geox_mip_artifact_envelope_dry_run(*, dry_run_id: str = "geox-mip-dry-run-001") -> GeoXMIPArtifactEnvelopeDryRunResult:
    cases = []
    serialized = []
    for case_id, case_name, fixture_id, envelope in _cases():
        valid, errors = validate_geox_mip_artifact_envelope(envelope)
        case = GeoXMIPArtifactEnvelopeDryRunCase(case_id, case_name, fixture_id, envelope, valid, errors)
        cases.append(case)
        serialized.append(serialize_geox_mip_artifact_envelope(envelope))
    all_valid = all(case.validation_passed for case in cases)
    summary = {
        "dry_run_id": dry_run_id,
        "case_count": len(cases),
        "case_ids": [case.case_id for case in cases],
        "artifact_kinds": [item["artifact_kind"] for item in serialized],
        "all_cases_valid": all_valid,
        "production_authorization_preserved": True,
        "runtime_code_changed": True,
        "dry_run_runtime_added": True,
        "non_production_fixture_only": True,
        "mip_repository_modified": False,
        **_FORBIDDEN_FLAGS,
    }
    return GeoXMIPArtifactEnvelopeDryRunResult(dry_run_id, "1.0.0", tuple(cases), tuple(serialized), all_valid, True, False, summary)


def serialize_geox_mip_artifact_envelope_dry_run_result(result: GeoXMIPArtifactEnvelopeDryRunResult) -> dict[str, Any]:
    """Return deterministic JSON-safe dry-run output."""
    return {
        "dry_run_id": result.dry_run_id,
        "envelope_version": result.envelope_version,
        "cases": [
            {
                "case_id": case.case_id,
                "case_name": case.case_name,
                "fixture_id": case.fixture_id,
                "envelope": dict(result.serialized_cases[index]),
                "validation_passed": case.validation_passed,
                "validation_errors": list(case.validation_errors),
            }
            for index, case in enumerate(result.cases)
        ],
        "all_cases_valid": result.all_cases_valid,
        "production_authorization_preserved": result.production_authorization_preserved,
        "mip_repository_modified": result.mip_repository_modified,
        "summary": dict(result.summary),
    }
