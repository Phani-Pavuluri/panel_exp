"""MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001 — surface eligibility gate runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any

from panel_exp.validation.multicell_experiment_family_contrast_contract_001 import (
    ALLOWED_SURFACES,
    CONDITIONAL_SURFACES,
    EXPERIMENT_FAMILY_TYPES,
    FAMILY_APPLICABILITY_RULES,
    PROHIBITED_SURFACES_UNLESS_GOVERNED,
    SURFACE_EVIDENCE_REQUIREMENTS,
    evaluate_readout_surface,
)

_ARTIFACT_ID = "MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_POLICY_VERSION = "1.0.0"
_SCOPE = "multicell_experiment_family_and_contrast_runtime_implemented_no_multiplicity_or_inference_computation"
_VERDICT = "multicell_experiment_family_and_contrast_runtime_implemented_no_multiplicity_or_inference_computation"
_RECOMMENDED_NEXT = "TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001"
_ALTERNATIVE_NEXT = "MULTICELL_CONTRAST_MULTIPLICITY_RUNTIME_INTEGRATION_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001_summary.json"
)

DEPENDS_ON = (
    "MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001",
    "SOPHISTICATED_METHOD_EVIDENCE_LADDER_001",
)

_SURFACE_ALLOWED = "SURFACE_ALLOWED"
_SURFACE_BLOCKED = "SURFACE_BLOCKED"

_POSITIVE_FLAGS = {
    "runtime_implemented": True,
    "surface_eligibility_packet_generated": True,
    "experiment_family_classification_enforced": True,
    "independent_experiment_exemption_enforced": True,
    "contrast_requirement_enforced": True,
    "multiplicity_applicability_enforced": True,
    "shared_control_covariance_requirement_enforced": True,
    "pooled_global_surface_rules_enforced": True,
    "winner_claim_blocking_enforced": True,
}

_AUTH_FALSE = {
    "multiplicity_correction_computed": False,
    "covariance_computed": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "effect_estimate_computed_new": False,
    "lift_computed_new": False,
    "roi_computed_new": False,
    "winner_claim_authorized": False,
    "budget_scale_claim_authorized": False,
    "production_recommendation_authorized": False,
    "production_authorization_granted": False,
    "method_promoted": False,
    "method_unblocked": False,
    "production_catalog_unblocked": False,
    "mmm_runtime_calls_implemented": False,
    "llm_decisioning_authorized": False,
}


@dataclass(frozen=True)
class MulticellExperimentFamilyContrastRuntimeConfig:
    allow_explicit_family_override: bool = True
    require_lineage_manifest: bool = False


@dataclass(frozen=True)
class MulticellExperimentFamilyContrastReviewPacket:
    request_id: str
    review_id: str
    experiment_family: str
    requested_surface: str
    surface_status: str
    allowed_surface: bool
    blocked_surface: bool
    required_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    required_caveats: tuple[str, ...]
    contrast_type: str | None
    contrast_definitions_present: bool
    multiplicity_required: bool
    multiplicity_policy_present: bool
    covariance_semantics_required: bool
    covariance_semantics_present: bool
    family_classification_reason: str
    lineage_manifest: dict[str, Any]
    provenance_hash: str
    policy_version: str
    failure_packet: dict[str, Any] | None
    authorization_boundary_report: dict[str, Any]


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _unique_str(values: list[Any]) -> list[str]:
    seen: list[str] = []
    for v in values:
        s = str(v).strip()
        if s and s not in seen:
            seen.append(s)
    return seen


def _hash_payload(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _resolve_config(
    config: MulticellExperimentFamilyContrastRuntimeConfig | dict[str, Any] | None,
) -> MulticellExperimentFamilyContrastRuntimeConfig:
    if config is None:
        return MulticellExperimentFamilyContrastRuntimeConfig()
    if isinstance(config, MulticellExperimentFamilyContrastRuntimeConfig):
        return config
    base = MulticellExperimentFamilyContrastRuntimeConfig()
    merged = {**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    return MulticellExperimentFamilyContrastRuntimeConfig(**merged)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return True


def classify_experiment_family(data: dict[str, Any]) -> tuple[str, str]:
    """Classify experiment family type from identity signals."""
    explicit = data.get("experiment_family")
    if explicit and str(explicit) in EXPERIMENT_FAMILY_TYPES:
        return str(explicit), "explicit experiment_family provided"

    if data.get("pooling_requested") or data.get("global_summary_requested"):
        return "POOLED_AGGREGATE_FAMILY", "pooling or global summary requested"

    dose_sem = data.get("dose_response_semantics")
    contrast_type = data.get("contrast_type")
    if _present(dose_sem) or contrast_type in ("DOSE_LINEAR_TREND", "DOSE_NONLINEAR_RESPONSE"):
        return "DOSE_RESPONSE_FAMILY", "dose-response semantics or contrast declared"

    experiment_ids = _unique_str(_as_list(data.get("experiment_ids")))
    platforms = _unique_str(_as_list(data.get("platform")))
    channels = _unique_str(_as_list(data.get("channel")))
    if data.get("decision_family_id") and (len(experiment_ids) > 1 or len(platforms) > 1 or len(channels) > 1):
        return (
            "PORTFOLIO_DECISION_FAMILY",
            "decision family spans multiple experiments/platforms/channels",
        )

    if _present(data.get("shared_control_group")) or _present(data.get("overlapping_units")):
        return "SHARED_CONTROL_MULTI_ARM", "shared control group or overlapping units declared"

    arm_ids = _unique_str(_as_list(data.get("arm_ids")))
    planned = _present(data.get("planned_cross_arm_comparisons")) or _present(
        data.get("implied_comparison_surface")
    )
    if planned and len(arm_ids) > 1:
        return "RELATED_PARALLEL_ARMS", "planned cross-arm comparisons within shared context"

    if len(experiment_ids) > 1 or len(platforms) > 1:
        if not _present(data.get("shared_budget_pool")) and not _present(data.get("shared_control_group")):
            return (
                "INDEPENDENT_EXPERIMENTS",
                "multiple experiments/platforms without shared comparison family",
            )

    if len(arm_ids) > 1:
        return "RELATED_PARALLEL_ARMS", "multiple arms in same experiment context"

    if _present(data.get("experiment_family_id")) or experiment_ids or arm_ids:
        return "INDEPENDENT_EXPERIMENTS", "standalone experiment without cross-arm comparison family"

    return "UNKNOWN_FAMILY_REQUIRES_REVIEW", "insufficient family identity signals"


def build_evidence_flags(data: dict[str, Any]) -> dict[str, bool]:
    """Map runtime input fields to contract evidence keys."""
    dose_sem = data.get("dose_response_semantics") or {}
    if not isinstance(dose_sem, dict):
        dose_sem = {"declared": dose_sem}

    estimand_align = data.get("estimand_alignment_evidence") or {}
    if not isinstance(estimand_align, dict):
        estimand_align = {"declared": estimand_align}

    flags: dict[str, bool] = {
        "arm_identity": bool(_unique_str(_as_list(data.get("arm_ids")))),
        "estimand_definition": _present(data.get("common_estimand")),
        "execution_readout_evidence": _present(data.get("trusted_readout_report"))
        or _present(data.get("claim_authorization_report")),
        "contrast_definition": _present(data.get("contrast_definitions")),
        "shared_experiment_family": _present(data.get("experiment_family_id")),
        "comparable_metrics": _present(data.get("shared_metric")) and _present(data.get("common_estimand")),
        "multiplicity_policy": _present(data.get("multiplicity_policy")),
        "shared_control_covariance_semantics": _present(data.get("shared_control_covariance_semantics")),
        "dose_ordering": _present(dose_sem.get("dose_ordering") or dose_sem.get("ordering")),
        "dose_units": _present(dose_sem.get("dose_units") or dose_sem.get("units")),
        "monotonic_or_nonlinear_policy": _present(
            dose_sem.get("monotonic_or_nonlinear_policy") or dose_sem.get("policy")
        ),
        "pooling_weights": _present(data.get("pooling_weights")),
        "heterogeneity_diagnostics": _present(data.get("heterogeneity_diagnostics")),
        "covariance_or_variance_semantics": _present(data.get("shared_control_covariance_semantics"))
        or _present(estimand_align.get("covariance_or_variance_semantics")),
        "estimand_alignment": _present(estimand_align) or _present(data.get("common_estimand")),
        "comparable_estimands": _present(estimand_align.get("comparable_estimands"))
        or _present(data.get("common_estimand")),
        "per_source_caveats": _present(estimand_align.get("per_source_caveats"))
        or _present(data.get("lineage_manifest")),
        "decision_family_declaration": _present(data.get("decision_family_id")),
        "production_recommendation_authorization": bool(
            data.get("production_recommendation_authorization")
        ),
    }
    return flags


def _required_evidence_for_surface(family: str, surface: str) -> tuple[str, ...]:
    if surface in SURFACE_EVIDENCE_REQUIREMENTS:
        return SURFACE_EVIDENCE_REQUIREMENTS[surface]
    rules = FAMILY_APPLICABILITY_RULES.get(family, {})
    if surface == "ARM_COMPARISON" and rules.get("shared_covariance_required"):
        return SURFACE_EVIDENCE_REQUIREMENTS.get("SHARED_CONTROL_COMPARISON", ())
    if surface == "PORTFOLIO_RANKING_REVIEW":
        return (
            "comparable_estimands",
            "per_source_caveats",
            "decision_family_declaration",
        )
    if surface in ("POOLED_EFFECT_SUMMARY", "GLOBAL_EFFECT_SUMMARY"):
        return SURFACE_EVIDENCE_REQUIREMENTS.get("POOLED_EFFECT_SUMMARY", ())
    if surface == "DOSE_RESPONSE_SUMMARY":
        return SURFACE_EVIDENCE_REQUIREMENTS.get("DOSE_RESPONSE_SUMMARY", ())
    return SURFACE_EVIDENCE_REQUIREMENTS.get(surface, ())


def _build_caveats(family: str, data: dict[str, Any]) -> tuple[str, ...]:
    caveats: list[str] = []
    rules = FAMILY_APPLICABILITY_RULES.get(family, {})
    if family == "INDEPENDENT_EXPERIMENTS":
        caveats.append(
            "Independent experiment: no shared multiplicity/covariance required for standalone readout."
        )
    if rules.get("shared_covariance_required"):
        caveats.append("Shared-control family: comparative claims require covariance semantics.")
    if family == "PORTFOLIO_DECISION_FAMILY":
        caveats.append("Portfolio decision synthesis: not a single statistical experiment.")
    if data.get("shared_control_group"):
        caveats.append("Cells may share control/donor references; estimates are dependent evidence streams.")
    return tuple(caveats)


def _build_review_id(data: dict[str, Any], family: str, surface: str) -> str:
    canonical = {
        "request_id": data.get("request_id"),
        "experiment_family": family,
        "requested_surface": surface,
        "experiment_family_id": data.get("experiment_family_id"),
        "decision_family_id": data.get("decision_family_id"),
        "experiment_ids": sorted(_unique_str(_as_list(data.get("experiment_ids")))),
        "arm_ids": sorted(_unique_str(_as_list(data.get("arm_ids")))),
        "contrast_type": data.get("contrast_type"),
    }
    digest = _hash_payload(canonical)[:16]
    return f"mefcr-{digest}"


def _authorization_boundary_report() -> dict[str, Any]:
    return {
        "runtime_scope": "surface_eligibility_gate_only",
        "computes_multiplicity_correction": False,
        "computes_covariance": False,
        "computes_inference": False,
        "authorizes_winner_claims": False,
        "authorizes_production_recommendation": False,
        "authorizes_method_promotion": False,
        "authorizes_catalog_changes": False,
        **_AUTH_FALSE,
    }


def build_multicell_contrast_eligibility_packet(
    input_data: dict[str, Any] | Any,
    *,
    config: MulticellExperimentFamilyContrastRuntimeConfig | dict[str, Any] | None = None,
) -> MulticellExperimentFamilyContrastReviewPacket:
    """Build a single surface eligibility packet from input."""
    cfg = _resolve_config(config)
    data = _to_dict(input_data)
    requested_surface = str(
        data.get("requested_surface") or "STANDALONE_ARM_READOUT"
    ).strip()
    family, reason = classify_experiment_family(data)
    if cfg.allow_explicit_family_override and data.get("experiment_family"):
        family = str(data["experiment_family"])

    evidence = build_evidence_flags(data)
    evaluation = evaluate_readout_surface(family, requested_surface, evidence=evidence)
    rules = FAMILY_APPLICABILITY_RULES.get(family, {})

    required = _required_evidence_for_surface(family, requested_surface)
    missing = evaluation.missing_evidence or tuple(
        k for k in required if not evidence.get(k, False)
    )

    allowed = evaluation.authorized
    surface_status = _SURFACE_ALLOWED if allowed else _SURFACE_BLOCKED
    blockers: list[str] = []
    if not allowed and evaluation.failure_reason:
        blockers.append(evaluation.failure_reason)

    request_id = str(data.get("request_id") or "mefcr_request_unspecified")
    review_id = _build_review_id(data, family, requested_surface)
    lineage = dict(data.get("lineage_manifest") or {})

    packet_body = {
        "request_id": request_id,
        "review_id": review_id,
        "experiment_family": family,
        "requested_surface": requested_surface,
        "surface_status": surface_status,
        "allowed_surface": allowed,
        "blocked_surface": not allowed,
        "required_evidence": list(required),
        "missing_evidence": list(missing),
        "blockers": blockers,
        "required_caveats": list(_build_caveats(family, data)),
        "contrast_type": data.get("contrast_type"),
        "contrast_definitions_present": bool(evidence.get("contrast_definition")),
        "multiplicity_required": bool(rules.get("multiplicity_required")),
        "multiplicity_policy_present": bool(evidence.get("multiplicity_policy")),
        "covariance_semantics_required": bool(rules.get("shared_covariance_required")),
        "covariance_semantics_present": bool(evidence.get("shared_control_covariance_semantics")),
        "family_classification_reason": reason,
        "lineage_manifest": lineage,
        "policy_version": _POLICY_VERSION,
        "failure_packet": evaluation.to_failure_packet(),
        "authorization_boundary_report": _authorization_boundary_report(),
    }
    provenance_hash = _hash_payload(packet_body)

    return MulticellExperimentFamilyContrastReviewPacket(
        request_id=request_id,
        review_id=review_id,
        experiment_family=family,
        requested_surface=requested_surface,
        surface_status=surface_status,
        allowed_surface=allowed,
        blocked_surface=not allowed,
        required_evidence=required,
        missing_evidence=missing,
        blockers=tuple(blockers),
        required_caveats=_build_caveats(family, data),
        contrast_type=data.get("contrast_type"),
        contrast_definitions_present=bool(evidence.get("contrast_definition")),
        multiplicity_required=bool(rules.get("multiplicity_required")),
        multiplicity_policy_present=bool(evidence.get("multiplicity_policy")),
        covariance_semantics_required=bool(rules.get("shared_covariance_required")),
        covariance_semantics_present=bool(evidence.get("shared_control_covariance_semantics")),
        family_classification_reason=reason,
        lineage_manifest=lineage,
        provenance_hash=provenance_hash,
        policy_version=_POLICY_VERSION,
        failure_packet=evaluation.to_failure_packet(),
        authorization_boundary_report={**packet_body["authorization_boundary_report"], "provenance_hash": provenance_hash},
    )


def evaluate_multicell_readout_surface(
    input_data: dict[str, Any] | Any,
    *,
    config: MulticellExperimentFamilyContrastRuntimeConfig | dict[str, Any] | None = None,
) -> MulticellExperimentFamilyContrastReviewPacket:
    """Alias for single-surface eligibility evaluation."""
    return build_multicell_contrast_eligibility_packet(input_data, config=config)


def generate_multicell_experiment_family_contrast_review(
    input_data: dict[str, Any] | Any | list[Any],
    config: MulticellExperimentFamilyContrastRuntimeConfig | dict[str, Any] | None = None,
) -> MulticellExperimentFamilyContrastReviewPacket | list[MulticellExperimentFamilyContrastReviewPacket]:
    """Generate one or more independent surface eligibility packets (no ranking)."""
    if isinstance(input_data, list):
        return [
            build_multicell_contrast_eligibility_packet(item, config=config)
            for item in input_data
        ]
    return build_multicell_contrast_eligibility_packet(input_data, config=config)


def packet_to_dict(packet: MulticellExperimentFamilyContrastReviewPacket) -> dict[str, Any]:
    return asdict(packet)


def get_runtime_metadata() -> dict[str, Any]:
    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "scope": _SCOPE,
        "depends_on": list(DEPENDS_ON),
        "final_verdict": _VERDICT,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "allowed_surfaces": list(ALLOWED_SURFACES),
        "conditional_surfaces": list(CONDITIONAL_SURFACES),
        "prohibited_surfaces": list(PROHIBITED_SURFACES_UNLESS_GOVERNED),
        **_POSITIVE_FLAGS,
        **_AUTH_FALSE,
    }


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = False, summary_path: Path | None = None) -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> None:
        scenarios.append({"scenario_id": sid, "passed": passed})

    indep = build_multicell_contrast_eligibility_packet(
        {
            "request_id": "indep_001",
            "experiment_ids": ["exp_a", "exp_b"],
            "platform": ["meta", "google"],
            "arm_ids": ["arm_a"],
            "common_estimand": "geo.relative_att_post",
            "requested_surface": "STANDALONE_ARM_READOUT",
            "trusted_readout_report": {"status": "ready"},
        }
    )
    _s("independent_standalone_allowed", indep.allowed_surface)
    _s("independent_no_multiplicity_required", not indep.multiplicity_required)

    indep_winner = build_multicell_contrast_eligibility_packet(
        {
            "request_id": "indep_winner",
            "experiment_ids": ["exp_a", "exp_b"],
            "platform": ["meta", "google"],
            "requested_surface": "WINNER_CLAIM",
        }
    )
    _s("independent_winner_blocked", indep_winner.blocked_surface)

    related = build_multicell_contrast_eligibility_packet(
        {
            "request_id": "related_001",
            "arm_ids": ["arm_a", "arm_b"],
            "planned_cross_arm_comparisons": ["arm_a_vs_arm_b"],
            "requested_surface": "ARM_COMPARISON",
        }
    )
    _s("related_missing_contrast_blocked", related.blocked_surface)

    related_ok = build_multicell_contrast_eligibility_packet(
        {
            "request_id": "related_ok",
            "arm_ids": ["arm_a", "arm_b"],
            "planned_cross_arm_comparisons": ["arm_a_vs_arm_b"],
            "experiment_family_id": "fam_001",
            "common_estimand": "att",
            "shared_metric": "revenue",
            "contrast_definitions": {"arm_a_vs_arm_b": {}},
            "multiplicity_policy": {"family": "holm"},
            "requested_surface": "ARM_COMPARISON",
            "trusted_readout_report": {"status": "ready"},
        }
    )
    _s("related_arm_comparison_allowed", related_ok.allowed_surface)

    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "multicell_experiment_family_contrast_runtime",
        "base_commit": _git_commit(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": list(DEPENDS_ON),
        "failed_scenarios": failed,
        "final_verdict": _VERDICT,
        **_POSITIVE_FLAGS,
        **_AUTH_FALSE,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
    }
    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"verdict": _VERDICT, "failed_scenarios": failed}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=args.write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
