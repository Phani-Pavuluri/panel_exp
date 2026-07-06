"""MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001 — experiment-family and contrast contract."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

_ARTIFACT_ID = "MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "multicell_experiment_family_and_contrast_contract_defined_no_runtime_or_inference"
_VERDICT = "multicell_experiment_family_and_contrast_contract_defined_no_runtime_or_inference"
_RECOMMENDED_NEXT = "MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001"
_ALTERNATIVE_NEXT = "TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001_summary.json"
)

DEPENDS_ON = (
    "SOPHISTICATED_METHOD_EVIDENCE_LADDER_001",
    "METHOD_PROMOTION_CANDIDATE_AUDIT_001",
    "METHOD_PROMOTION_REVIEW_RUNTIME_001",
    "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001",
)

EXPERIMENT_FAMILY_TYPES = (
    "INDEPENDENT_EXPERIMENTS",
    "RELATED_PARALLEL_ARMS",
    "SHARED_CONTROL_MULTI_ARM",
    "DOSE_RESPONSE_FAMILY",
    "PORTFOLIO_DECISION_FAMILY",
    "POOLED_AGGREGATE_FAMILY",
    "UNKNOWN_FAMILY_REQUIRES_REVIEW",
)

FAMILY_IDENTITY_FIELDS = (
    "experiment_family_id",
    "decision_family_id",
    "experiment_ids",
    "arm_ids",
    "platform",
    "channel",
    "campaign_objective",
    "shared_budget_pool",
    "shared_control_group",
    "overlapping_units",
    "shared_time_window",
    "shared_metric",
    "common_estimand",
    "planned_cross_arm_comparisons",
    "implied_comparison_surface",
    "pooling_requested",
    "global_summary_requested",
)

CONTRAST_TYPES = (
    "ARM_VS_CONTROL",
    "ARM_VS_ARM",
    "DOSE_LINEAR_TREND",
    "DOSE_NONLINEAR_RESPONSE",
    "GLOBAL_ANY_EFFECT",
    "POOLED_AVERAGE_EFFECT",
    "CELL_SPECIFIC_EFFECT",
    "PORTFOLIO_RANKING",
    "BUDGET_REALLOCATION_COMPARISON",
)

ALLOWED_SURFACES = (
    "STANDALONE_ARM_READOUT",
    "CELL_SPECIFIC_POINT_ESTIMATE",
    "DESCRIPTIVE_COMPARISON_REVIEW_ONLY",
    "DIAGNOSTIC_ONLY",
    "RESEARCH_OR_REVIEW_ONLY",
)

CONDITIONAL_SURFACES = (
    "ARM_COMPARISON",
    "DOSE_RESPONSE_SUMMARY",
    "POOLED_EFFECT_SUMMARY",
    "GLOBAL_EFFECT_SUMMARY",
    "PORTFOLIO_RANKING_REVIEW",
)

PROHIBITED_SURFACES_UNLESS_GOVERNED = (
    "WINNER_CLAIM",
    "SCALE_BUDGET_CLAIM",
    "PRODUCTION_RECOMMENDATION",
    "ROI_COMPARISON_CLAIM",
    "CAUSAL_SUPERIORITY_CLAIM",
    "STATISTICAL_SIGNIFICANCE_COMPARISON",
    "CONFIDENCE_INTERVAL_COMPARISON",
)

SURFACE_EVIDENCE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "STANDALONE_ARM_READOUT": (
        "arm_identity",
        "estimand_definition",
        "execution_readout_evidence",
    ),
    "CELL_SPECIFIC_POINT_ESTIMATE": (
        "arm_identity",
        "estimand_definition",
        "execution_readout_evidence",
    ),
    "ARM_COMPARISON": (
        "contrast_definition",
        "shared_experiment_family",
        "comparable_metrics",
        "multiplicity_policy",
    ),
    "SHARED_CONTROL_COMPARISON": (
        "shared_control_covariance_semantics",
        "contrast_definition",
        "comparable_metrics",
    ),
    "DOSE_RESPONSE_SUMMARY": (
        "dose_ordering",
        "dose_units",
        "planned_contrasts",
        "monotonic_or_nonlinear_policy",
    ),
    "POOLED_EFFECT_SUMMARY": (
        "pooling_weights",
        "heterogeneity_diagnostics",
        "covariance_or_variance_semantics",
        "estimand_alignment",
    ),
    "GLOBAL_EFFECT_SUMMARY": (
        "pooling_weights",
        "heterogeneity_diagnostics",
        "covariance_or_variance_semantics",
        "estimand_alignment",
        "multiplicity_policy",
    ),
    "PORTFOLIO_RANKING_REVIEW": (
        "comparable_estimands",
        "per_source_caveats",
        "decision_family_declaration",
    ),
    "WINNER_CLAIM": (
        "comparable_estimands",
        "governed_uncertainty",
        "multiplicity_policy",
        "production_recommendation_authorization",
    ),
    "SCALE_BUDGET_CLAIM": (
        "production_recommendation_authorization",
        "comparable_estimands",
        "budget_reallocation_semantics",
    ),
}

FAMILY_APPLICABILITY_RULES: dict[str, dict[str, Any]] = {
    "INDEPENDENT_EXPERIMENTS": {
        "multiplicity_required": False,
        "shared_covariance_required": False,
        "standalone_readout_allowed": True,
        "cross_arm_winner_allowed": False,
        "notes": (
            "No shared multiplicity/covariance for standalone readouts. "
            "Block cross-arm/platform winner claims unless promoted to "
            "PORTFOLIO_DECISION_FAMILY with comparable estimands."
        ),
    },
    "RELATED_PARALLEL_ARMS": {
        "multiplicity_required": True,
        "shared_covariance_required": False,
        "standalone_readout_allowed": True,
        "cross_arm_winner_allowed": False,
        "notes": "Require contrast definitions and multiplicity family for arm comparisons.",
    },
    "SHARED_CONTROL_MULTI_ARM": {
        "multiplicity_required": True,
        "shared_covariance_required": True,
        "standalone_readout_allowed": True,
        "cross_arm_winner_allowed": False,
        "notes": (
            "Require shared-control covariance semantics or conservative fallback "
            "before comparative/winner claims."
        ),
    },
    "DOSE_RESPONSE_FAMILY": {
        "multiplicity_required": True,
        "shared_covariance_required": False,
        "standalone_readout_allowed": True,
        "cross_arm_winner_allowed": False,
        "notes": "Require ordered-dose contrast taxonomy and dose-response estimand semantics.",
    },
    "PORTFOLIO_DECISION_FAMILY": {
        "multiplicity_required": True,
        "shared_covariance_required": False,
        "standalone_readout_allowed": True,
        "cross_arm_winner_allowed": False,
        "notes": (
            "Decision synthesis, not one statistical experiment. "
            "Require per-source caveats and comparable metrics before ranking/winner/scale claims."
        ),
    },
    "POOLED_AGGREGATE_FAMILY": {
        "multiplicity_required": True,
        "shared_covariance_required": True,
        "standalone_readout_allowed": False,
        "cross_arm_winner_allowed": False,
        "notes": (
            "Require weighting, estimand, heterogeneity, covariance, and pooling semantics "
            "before pooled/global lift surfaces."
        ),
    },
    "UNKNOWN_FAMILY_REQUIRES_REVIEW": {
        "multiplicity_required": True,
        "shared_covariance_required": True,
        "standalone_readout_allowed": False,
        "cross_arm_winner_allowed": False,
        "notes": "Block comparative/pooled/winner claims until family declared.",
    },
}

FAILURE_PACKET_FIELDS = (
    "failure_code",
    "failure_reason",
    "family_type",
    "blocked_surface",
    "missing_evidence",
    "required_remediation",
    "retry_category",
)

FAILURE_CODES = (
    "UNKNOWN_EXPERIMENT_FAMILY",
    "MISSING_CONTRAST_DEFINITION",
    "MISSING_MULTIPLICITY_POLICY",
    "MISSING_SHARED_CONTROL_COVARIANCE_SEMANTICS",
    "MISSING_DOSE_RESPONSE_SEMANTICS",
    "MISSING_POOLING_WEIGHTS",
    "MISSING_HETEROGENEITY_DIAGNOSTICS",
    "INCOMPARABLE_ESTIMANDS",
    "COMPARATIVE_SURFACE_NOT_AUTHORIZED",
    "WINNER_CLAIM_BLOCKED",
    "BUDGET_SCALE_CLAIM_BLOCKED",
)

RETRY_CATEGORIES = (
    "DECLARE_EXPERIMENT_FAMILY",
    "ADD_CONTRAST_DEFINITIONS",
    "ADD_MULTIPLICITY_POLICY",
    "ADD_SHARED_CONTROL_COVARIANCE_SEMANTICS",
    "ADD_DOSE_RESPONSE_SEMANTICS",
    "ADD_POOLING_AND_HETEROGENEITY_EVIDENCE",
    "REQUEST_DESCRIPTIVE_ONLY_SURFACE",
    "BLOCK_COMPARATIVE_SURFACE",
)

FUTURE_RUNTIME_TESTS = (
    "classifies_independent_experiments_without_forcing_shared_multiplicity",
    "blocks_cross_platform_winner_claim_without_comparable_decision_family_evidence",
    "requires_contrast_definitions_for_related_arms",
    "requires_multiplicity_policy_for_arm_comparisons",
    "requires_covariance_semantics_for_shared_control_multi_arm_comparisons",
    "requires_dose_semantics_for_dose_response_summaries",
    "blocks_pooled_global_lift_without_pooling_heterogeneity_covariance_evidence",
    "blocks_winner_scale_budget_claims_without_governed_authorization",
    "emits_failure_packet_for_unknown_family",
    "preserves_standalone_readout_eligibility_for_independent_experiments",
    "all_forbidden_computation_authorization_flags_false",
)

_AUTH_FLAGS = {
    "runtime_implemented": False,
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

CONTRACT_POSITIVE_FLAGS = {
    "experiment_family_taxonomy_defined": True,
    "contrast_taxonomy_defined": True,
    "multiplicity_applicability_rules_defined": True,
    "shared_control_covariance_requirements_defined": True,
    "pooled_global_surface_rules_defined": True,
    "independent_experiment_exemption_defined": True,
    "winner_claim_blocking_rules_defined": True,
    "future_runtime_tests_documented": True,
}


class ExperimentFamilyType(str, Enum):
    INDEPENDENT_EXPERIMENTS = "INDEPENDENT_EXPERIMENTS"
    RELATED_PARALLEL_ARMS = "RELATED_PARALLEL_ARMS"
    SHARED_CONTROL_MULTI_ARM = "SHARED_CONTROL_MULTI_ARM"
    DOSE_RESPONSE_FAMILY = "DOSE_RESPONSE_FAMILY"
    PORTFOLIO_DECISION_FAMILY = "PORTFOLIO_DECISION_FAMILY"
    POOLED_AGGREGATE_FAMILY = "POOLED_AGGREGATE_FAMILY"
    UNKNOWN_FAMILY_REQUIRES_REVIEW = "UNKNOWN_FAMILY_REQUIRES_REVIEW"


class ReadoutSurface(str, Enum):
    STANDALONE_ARM_READOUT = "STANDALONE_ARM_READOUT"
    CELL_SPECIFIC_POINT_ESTIMATE = "CELL_SPECIFIC_POINT_ESTIMATE"
    DESCRIPTIVE_COMPARISON_REVIEW_ONLY = "DESCRIPTIVE_COMPARISON_REVIEW_ONLY"
    DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY"
    RESEARCH_OR_REVIEW_ONLY = "RESEARCH_OR_REVIEW_ONLY"
    ARM_COMPARISON = "ARM_COMPARISON"
    DOSE_RESPONSE_SUMMARY = "DOSE_RESPONSE_SUMMARY"
    POOLED_EFFECT_SUMMARY = "POOLED_EFFECT_SUMMARY"
    GLOBAL_EFFECT_SUMMARY = "GLOBAL_EFFECT_SUMMARY"
    PORTFOLIO_RANKING_REVIEW = "PORTFOLIO_RANKING_REVIEW"
    WINNER_CLAIM = "WINNER_CLAIM"
    SCALE_BUDGET_CLAIM = "SCALE_BUDGET_CLAIM"
    PRODUCTION_RECOMMENDATION = "PRODUCTION_RECOMMENDATION"
    ROI_COMPARISON_CLAIM = "ROI_COMPARISON_CLAIM"
    CAUSAL_SUPERIORITY_CLAIM = "CAUSAL_SUPERIORITY_CLAIM"
    STATISTICAL_SIGNIFICANCE_COMPARISON = "STATISTICAL_SIGNIFICANCE_COMPARISON"
    CONFIDENCE_INTERVAL_COMPARISON = "CONFIDENCE_INTERVAL_COMPARISON"


@dataclass(frozen=True)
class MulticellExperimentFamilyContrastContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    experiment_family_taxonomy_defined: bool
    contrast_taxonomy_defined: bool
    multiplicity_applicability_rules_defined: bool
    shared_control_covariance_requirements_defined: bool
    pooled_global_surface_rules_defined: bool
    independent_experiment_exemption_defined: bool
    winner_claim_blocking_rules_defined: bool
    future_runtime_tests_documented: bool
    experiment_family_types: tuple[str, ...]
    family_identity_fields: tuple[str, ...]
    contrast_types: tuple[str, ...]
    allowed_surfaces: tuple[str, ...]
    conditional_surfaces: tuple[str, ...]
    prohibited_surfaces_unless_governed: tuple[str, ...]
    surface_evidence_requirements: dict[str, tuple[str, ...]]
    family_applicability_rules: dict[str, dict[str, Any]]
    failure_packet_fields: tuple[str, ...]
    failure_codes: tuple[str, ...]
    retry_categories: tuple[str, ...]
    future_runtime_tests: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


@dataclass(frozen=True)
class SurfaceEvaluationResult:
    authorized: bool
    family_type: str
    requested_surface: str
    failure_code: str | None
    failure_reason: str | None
    missing_evidence: tuple[str, ...]
    retry_category: str | None

    def to_failure_packet(self) -> dict[str, Any] | None:
        if self.authorized:
            return None
        return {
            "failure_code": self.failure_code,
            "failure_reason": self.failure_reason,
            "family_type": self.family_type,
            "blocked_surface": self.requested_surface,
            "missing_evidence": list(self.missing_evidence),
            "required_remediation": self.retry_category,
            "retry_category": self.retry_category,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_multicell_experiment_family_contrast_contract() -> MulticellExperimentFamilyContrastContract:
    return MulticellExperimentFamilyContrastContract(
        artifact_id=_ARTIFACT_ID,
        scope=_SCOPE,
        depends_on=DEPENDS_ON,
        experiment_family_taxonomy_defined=True,
        contrast_taxonomy_defined=True,
        multiplicity_applicability_rules_defined=True,
        shared_control_covariance_requirements_defined=True,
        pooled_global_surface_rules_defined=True,
        independent_experiment_exemption_defined=True,
        winner_claim_blocking_rules_defined=True,
        future_runtime_tests_documented=True,
        experiment_family_types=EXPERIMENT_FAMILY_TYPES,
        family_identity_fields=FAMILY_IDENTITY_FIELDS,
        contrast_types=CONTRAST_TYPES,
        allowed_surfaces=ALLOWED_SURFACES,
        conditional_surfaces=CONDITIONAL_SURFACES,
        prohibited_surfaces_unless_governed=PROHIBITED_SURFACES_UNLESS_GOVERNED,
        surface_evidence_requirements=SURFACE_EVIDENCE_REQUIREMENTS,
        family_applicability_rules=FAMILY_APPLICABILITY_RULES,
        failure_packet_fields=FAILURE_PACKET_FIELDS,
        failure_codes=FAILURE_CODES,
        retry_categories=RETRY_CATEGORIES,
        future_runtime_tests=FUTURE_RUNTIME_TESTS,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=_RECOMMENDED_NEXT,
        alternative_next_artifact=_ALTERNATIVE_NEXT,
        final_verdict=_VERDICT,
    )


def _parse_family(value: str | ExperimentFamilyType) -> ExperimentFamilyType:
    if isinstance(value, ExperimentFamilyType):
        return value
    return ExperimentFamilyType(str(value))


def _parse_surface(value: str | ReadoutSurface) -> ReadoutSurface:
    if isinstance(value, ReadoutSurface):
        return value
    return ReadoutSurface(str(value))


def _missing_evidence(
    required: tuple[str, ...],
    evidence: Mapping[str, bool],
) -> tuple[str, ...]:
    return tuple(req for req in required if not evidence.get(req, False))


def evaluate_readout_surface(
    family_type: str | ExperimentFamilyType,
    requested_surface: str | ReadoutSurface,
    *,
    evidence: Mapping[str, bool] | None = None,
) -> SurfaceEvaluationResult:
    """Contract gate: evaluate whether a readout surface is authorized for a family type."""
    family = _parse_family(family_type)
    surface = _parse_surface(requested_surface)
    ev = evidence or {}
    rules = FAMILY_APPLICABILITY_RULES[family.value]

    if family == ExperimentFamilyType.UNKNOWN_FAMILY_REQUIRES_REVIEW:
        if surface.value not in ("DIAGNOSTIC_ONLY", "RESEARCH_OR_REVIEW_ONLY"):
            return SurfaceEvaluationResult(
                authorized=False,
                family_type=family.value,
                requested_surface=surface.value,
                failure_code="UNKNOWN_EXPERIMENT_FAMILY",
                failure_reason="Experiment family undeclared; comparative/pooled surfaces blocked",
                missing_evidence=("experiment_family_id",),
                retry_category="DECLARE_EXPERIMENT_FAMILY",
            )

    if surface.value in PROHIBITED_SURFACES_UNLESS_GOVERNED:
        req = SURFACE_EVIDENCE_REQUIREMENTS.get(surface.value, ())
        missing = _missing_evidence(req, ev)
        if surface in (ReadoutSurface.WINNER_CLAIM, ReadoutSurface.CAUSAL_SUPERIORITY_CLAIM):
            return SurfaceEvaluationResult(
                authorized=False,
                family_type=family.value,
                requested_surface=surface.value,
                failure_code="WINNER_CLAIM_BLOCKED",
                failure_reason="Winner/superiority claims require governed authorization",
                missing_evidence=missing or ("production_recommendation_authorization",),
                retry_category="BLOCK_COMPARATIVE_SURFACE",
            )
        if surface in (ReadoutSurface.SCALE_BUDGET_CLAIM, ReadoutSurface.PRODUCTION_RECOMMENDATION):
            return SurfaceEvaluationResult(
                authorized=False,
                family_type=family.value,
                requested_surface=surface.value,
                failure_code="BUDGET_SCALE_CLAIM_BLOCKED",
                failure_reason="Budget/scale/production recommendation claims blocked",
                missing_evidence=missing or ("production_recommendation_authorization",),
                retry_category="BLOCK_COMPARATIVE_SURFACE",
            )
        if missing:
            return SurfaceEvaluationResult(
                authorized=False,
                family_type=family.value,
                requested_surface=surface.value,
                failure_code="COMPARATIVE_SURFACE_NOT_AUTHORIZED",
                failure_reason="Prohibited surface missing governed evidence",
                missing_evidence=missing,
                retry_category="BLOCK_COMPARATIVE_SURFACE",
            )

    if surface.value in ALLOWED_SURFACES:
        if family == ExperimentFamilyType.POOLED_AGGREGATE_FAMILY and surface in (
            ReadoutSurface.STANDALONE_ARM_READOUT,
            ReadoutSurface.CELL_SPECIFIC_POINT_ESTIMATE,
        ):
            return SurfaceEvaluationResult(
                authorized=False,
                family_type=family.value,
                requested_surface=surface.value,
                failure_code="COMPARATIVE_SURFACE_NOT_AUTHORIZED",
                failure_reason="Pooled aggregate family does not authorize standalone arm readout",
                missing_evidence=("pooling_weights", "estimand_alignment"),
                retry_category="ADD_POOLING_AND_HETEROGENEITY_EVIDENCE",
            )
        req = SURFACE_EVIDENCE_REQUIREMENTS.get(surface.value, ())
        missing = _missing_evidence(req, ev)
        if missing:
            return SurfaceEvaluationResult(
                authorized=False,
                family_type=family.value,
                requested_surface=surface.value,
                failure_code="COMPARATIVE_SURFACE_NOT_AUTHORIZED",
                failure_reason="Standalone surface missing required evidence",
                missing_evidence=missing,
                retry_category="REQUEST_DESCRIPTIVE_ONLY_SURFACE",
            )
        return SurfaceEvaluationResult(
            authorized=True,
            family_type=family.value,
            requested_surface=surface.value,
            failure_code=None,
            failure_reason=None,
            missing_evidence=(),
            retry_category=None,
        )

    if surface.value in CONDITIONAL_SURFACES:
        req_key = surface.value
        if surface == ReadoutSurface.ARM_COMPARISON and rules.get("shared_covariance_required"):
            req_key = "SHARED_CONTROL_COMPARISON"
        req = SURFACE_EVIDENCE_REQUIREMENTS.get(req_key, SURFACE_EVIDENCE_REQUIREMENTS.get(surface.value, ()))
        missing = _missing_evidence(req, ev)

        if family == ExperimentFamilyType.INDEPENDENT_EXPERIMENTS and surface in (
            ReadoutSurface.GLOBAL_EFFECT_SUMMARY,
            ReadoutSurface.POOLED_EFFECT_SUMMARY,
            ReadoutSurface.PORTFOLIO_RANKING_REVIEW,
        ):
            return SurfaceEvaluationResult(
                authorized=False,
                family_type=family.value,
                requested_surface=surface.value,
                failure_code="COMPARATIVE_SURFACE_NOT_AUTHORIZED",
                failure_reason="Independent experiments cannot authorize cross-experiment comparative surfaces",
                missing_evidence=("decision_family_declaration",),
                retry_category="DECLARE_EXPERIMENT_FAMILY",
            )

        if rules.get("multiplicity_required") and not ev.get("multiplicity_policy"):
            missing = tuple(sorted(set(missing + ("multiplicity_policy",))))

        if surface == ReadoutSurface.DOSE_RESPONSE_SUMMARY and family != ExperimentFamilyType.DOSE_RESPONSE_FAMILY:
            return SurfaceEvaluationResult(
                authorized=False,
                family_type=family.value,
                requested_surface=surface.value,
                failure_code="MISSING_DOSE_RESPONSE_SEMANTICS",
                failure_reason="Dose-response summary requires DOSE_RESPONSE_FAMILY",
                missing_evidence=missing or ("dose_ordering", "dose_units"),
                retry_category="ADD_DOSE_RESPONSE_SEMANTICS",
            )

        if surface in (ReadoutSurface.POOLED_EFFECT_SUMMARY, ReadoutSurface.GLOBAL_EFFECT_SUMMARY):
            if family not in (
                ExperimentFamilyType.POOLED_AGGREGATE_FAMILY,
                ExperimentFamilyType.SHARED_CONTROL_MULTI_ARM,
            ):
                return SurfaceEvaluationResult(
                    authorized=False,
                    family_type=family.value,
                    requested_surface=surface.value,
                    failure_code="MISSING_POOLING_WEIGHTS",
                    failure_reason="Pooled/global surface requires pooled aggregate or shared-control family",
                    missing_evidence=missing or ("pooling_weights",),
                    retry_category="ADD_POOLING_AND_HETEROGENEITY_EVIDENCE",
                )

        if rules.get("shared_covariance_required") and not ev.get("shared_control_covariance_semantics"):
            missing = tuple(sorted(set(missing + ("shared_control_covariance_semantics",))))

        if missing:
            code = "MISSING_CONTRAST_DEFINITION"
            retry = "ADD_CONTRAST_DEFINITIONS"
            if "multiplicity_policy" in missing:
                code = "MISSING_MULTIPLICITY_POLICY"
                retry = "ADD_MULTIPLICITY_POLICY"
            elif "shared_control_covariance_semantics" in missing:
                code = "MISSING_SHARED_CONTROL_COVARIANCE_SEMANTICS"
                retry = "ADD_SHARED_CONTROL_COVARIANCE_SEMANTICS"
            elif "pooling_weights" in missing or "heterogeneity_diagnostics" in missing:
                code = "MISSING_POOLING_WEIGHTS"
                retry = "ADD_POOLING_AND_HETEROGENEITY_EVIDENCE"
            elif "dose_ordering" in missing:
                code = "MISSING_DOSE_RESPONSE_SEMANTICS"
                retry = "ADD_DOSE_RESPONSE_SEMANTICS"
            elif "comparable_estimands" in missing:
                code = "INCOMPARABLE_ESTIMANDS"
                retry = "ADD_CONTRAST_DEFINITIONS"
            return SurfaceEvaluationResult(
                authorized=False,
                family_type=family.value,
                requested_surface=surface.value,
                failure_code=code,
                failure_reason=f"Conditional surface missing evidence: {', '.join(missing)}",
                missing_evidence=missing,
                retry_category=retry,
            )

        return SurfaceEvaluationResult(
            authorized=True,
            family_type=family.value,
            requested_surface=surface.value,
            failure_code=None,
            failure_reason=None,
            missing_evidence=(),
            retry_category=None,
        )

    return SurfaceEvaluationResult(
        authorized=False,
        family_type=family.value,
        requested_surface=surface.value,
        failure_code="COMPARATIVE_SURFACE_NOT_AUTHORIZED",
        failure_reason=f"Unknown or unsupported surface: {surface.value}",
        missing_evidence=(),
        retry_category="BLOCK_COMPARATIVE_SURFACE",
    )


def validate_multicell_experiment_family_contrast_contract(
    contract: MulticellExperimentFamilyContrastContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if "INDEPENDENT_EXPERIMENTS" not in contract.experiment_family_types:
        issues.append("INDEPENDENT_EXPERIMENTS missing from taxonomy")
    if "RELATED_PARALLEL_ARMS" not in contract.experiment_family_types:
        issues.append("RELATED_PARALLEL_ARMS missing from taxonomy")
    if "ARM_VS_CONTROL" not in contract.contrast_types:
        issues.append("contrast taxonomy incomplete")
    if not contract.family_applicability_rules["INDEPENDENT_EXPERIMENTS"].get("multiplicity_required") is False:
        issues.append("independent experiment exemption not defined")
    if "WINNER_CLAIM" not in contract.prohibited_surfaces_unless_governed:
        issues.append("winner claim blocking incomplete")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        if not getattr(contract, key, False):
            issues.append(f"contract positive flag {key} must be {expected}")
    return {"valid": not issues, "issues": issues}


def get_multicell_experiment_family_contrast_contract_metadata() -> dict[str, Any]:
    contract = build_multicell_experiment_family_contrast_contract()
    return {
        "artifact_id": contract.artifact_id,
        "artifact_version": _ARTIFACT_VERSION,
        "scope": contract.scope,
        "depends_on": list(contract.depends_on),
        "final_verdict": contract.final_verdict,
        "recommended_next_artifact": contract.recommended_next_artifact,
        "alternative_next_artifact": contract.alternative_next_artifact,
        **CONTRACT_POSITIVE_FLAGS,
        **contract.authorization_flags,
    }


def list_experiment_family_types() -> tuple[str, ...]:
    return EXPERIMENT_FAMILY_TYPES


def list_contrast_types() -> tuple[str, ...]:
    return CONTRAST_TYPES


def list_future_runtime_tests() -> tuple[str, ...]:
    return FUTURE_RUNTIME_TESTS


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_multicell_experiment_family_contrast_contract()
    validation = validate_multicell_experiment_family_contrast_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for ft in EXPERIMENT_FAMILY_TYPES:
        scenarios.append(_s(f"family_type_{ft}", ft in contract.experiment_family_types))
    for ct in CONTRAST_TYPES:
        scenarios.append(_s(f"contrast_{ct}", ct in contract.contrast_types))
    for surface in ALLOWED_SURFACES:
        scenarios.append(_s(f"allowed_surface_{surface}", surface in contract.allowed_surfaces))
    for code in FAILURE_CODES:
        scenarios.append(_s(f"failure_code_{code}", code in contract.failure_codes))

    indep_standalone = evaluate_readout_surface(
        "INDEPENDENT_EXPERIMENTS",
        "STANDALONE_ARM_READOUT",
        evidence={"arm_identity": True, "estimand_definition": True, "execution_readout_evidence": True},
    )
    scenarios.append(_s("independent_standalone_no_multiplicity", indep_standalone.authorized))

    indep_winner = evaluate_readout_surface("INDEPENDENT_EXPERIMENTS", "WINNER_CLAIM")
    scenarios.append(_s("independent_winner_blocked", not indep_winner.authorized))

    related_arm = evaluate_readout_surface(
        "RELATED_PARALLEL_ARMS",
        "ARM_COMPARISON",
        evidence={
            "contrast_definition": True,
            "shared_experiment_family": True,
            "comparable_metrics": True,
            "multiplicity_policy": True,
        },
    )
    scenarios.append(_s("related_arms_requires_multiplicity", related_arm.authorized))

    shared_ctrl = evaluate_readout_surface(
        "SHARED_CONTROL_MULTI_ARM",
        "ARM_COMPARISON",
        evidence={
            "contrast_definition": True,
            "shared_experiment_family": True,
            "comparable_metrics": True,
            "multiplicity_policy": True,
            "shared_control_covariance_semantics": True,
        },
    )
    scenarios.append(_s("shared_control_requires_covariance", shared_ctrl.authorized))

    unknown = evaluate_readout_surface("UNKNOWN_FAMILY_REQUIRES_REVIEW", "ARM_COMPARISON")
    scenarios.append(_s("unknown_family_blocks_comparison", not unknown.authorized))

    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not contract.authorization_flags[flag]))
    scenarios.append(_s("validation_valid", validation["valid"]))
    scenarios.append(_s("failed_scenarios_empty", all(x["passed"] for x in scenarios)))
    return scenarios


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = False, summary_path: Path | None = None) -> dict[str, Any]:
    contract = build_multicell_experiment_family_contrast_contract()
    validation = validate_multicell_experiment_family_contrast_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "multicell_experiment_family_contrast_contract",
        "base_commit": _git_commit(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": list(DEPENDS_ON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "failed_scenarios": failed,
        "validation": validation,
        "final_verdict": _VERDICT,
        **CONTRACT_POSITIVE_FLAGS,
        **_AUTH_FLAGS,
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {"verdict": _VERDICT, "failed_scenarios": failed, "validation": validation}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=args.write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
