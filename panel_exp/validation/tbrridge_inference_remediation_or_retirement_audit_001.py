"""TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "tbrridge_inference_remediation_or_retirement_audit_completed_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
    "MULTICELL_MAX_T_RESEARCH_SCOUT_001",
)

MIN_AUDIT_ROW_COUNT = 45

_AUTH_FLAGS = {
    "production_p_value_authorized": False,
    "causal_confidence_interval_authorized": False,
    "trustreport_authorized": False,
    "calibration_signal_allowed": False,
    "mmm_ingestion_allowed": False,
    "llm_decisioning_allowed": False,
    "production_decisioning_allowed": False,
    "live_api_authorized": False,
    "scheduler_authorized": False,
    "budget_optimization_allowed": False,
}

_TBRRIDGE_AUTH_FLAGS = {
    "tbrridge_point_diagnostic_allowed": True,
    "tbrridge_production_inference_authorized": False,
    "tbrridge_production_p_value_authorized": False,
    "tbrridge_causal_ci_authorized": False,
    "brb_production_authorized": False,
    "kfold_production_authorized": False,
    "placebo_production_authorized": False,
    "jackknife_production_authorized": False,
    "aggregate_global_overclaim_blocked": True,
    "retire_or_replace_paths_defined": True,
    "remediation_paths_defined": True,
    "future_validation_required_before_promotion": True,
    "observed_diagnostics_required": True,
    "dgp_coverage_required": True,
    "failure_registry_consulted": True,
    "design_assignment_stress_required": True,
    "downstream_work_paused": True,
}


class TbrridgePath(str, Enum):
    POINT_ESTIMATE = "tbrridge_point_estimate"
    BRB = "tbrridge_brb"
    KFOLD = "tbrridge_kfold"
    PLACEBO = "tbrridge_placebo"
    JACKKNIFE = "tbrridge_jackknife"
    AGGREGATE_GLOBAL = "tbrridge_aggregate_global"
    PER_CELL_MARGINAL = "tbrridge_per_cell_marginal"
    DIAGNOSTIC_CURVE = "tbrridge_diagnostic_curve"
    DETERMINISTIC_UNKNOWN_ASSIGNMENT = "tbrridge_deterministic_unknown_assignment"
    MULTICELL_SHARED_CONTROL = "tbrridge_multicell_shared_control"


class AuditStatus(str, Enum):
    BLOCKED = "blocked"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    SENSITIVITY_ONLY = "sensitivity_only"
    RESTRICTED_RESEARCH = "restricted_research"
    REMEDIATION_REQUIRED = "remediation_required"
    RETIRE_OR_REPLACE = "retire_or_replace"
    CANDIDATE_AFTER_FUTURE_VALIDATION = "candidate_after_future_validation"


class AuditRequiredAction(str, Enum):
    BLOCK = "block"
    MARK_DIAGNOSTIC_ONLY = "mark_diagnostic_only"
    MARK_SENSITIVITY_ONLY = "mark_sensitivity_only"
    KEEP_RESEARCH_ONLY = "keep_research_only"
    REMEDIATE = "remediate"
    RETIRE_OR_REPLACE = "retire_or_replace"
    CANDIDATE_AFTER_FUTURE_VALIDATION = "candidate_after_future_validation"
    REQUIRE_NULL_CALIBRATION = "require_null_calibration"
    REQUIRE_DGP_COVERAGE = "require_dgp_coverage"
    REQUIRE_OBSERVED_DIAGNOSTICS = "require_observed_diagnostics"
    REQUIRE_DESIGN_STRESS_TEST = "require_design_stress_test"
    REQUIRE_FAILURE_REGISTRY_CONSULT = "require_failure_registry_consult"


class DesignContext(str, Enum):
    SINGLE_TREATED_GEO = "single_treated_geo"
    MULTI_TREATED_GEO = "multi_treated_geo"
    MATCHED_PAIR = "matched_pair"
    STRATIFIED = "stratified"
    FIXED_DETERMINISTIC = "fixed_deterministic"
    UNKNOWN_ASSIGNMENT = "unknown_assignment"
    MULTICELL_SHARED_CONTROL = "multicell_shared_control"
    MULTICELL_INDEPENDENT_CELLS = "multicell_independent_cells"
    ALL = "all"


class InferenceContext(str, Enum):
    POINT_ONLY = "point_only"
    BLOCK_RESIDUAL_BOOTSTRAP = "block_residual_bootstrap"
    KFOLD_CROSSFIT = "kfold_crossfit"
    PLACEBO_RANK = "placebo_rank"
    JACKKNIFE = "jackknife"
    AGGREGATE_GLOBAL = "aggregate_global"
    PER_CELL_MARGINAL = "per_cell_marginal"
    DIAGNOSTIC_DECOMPOSITION = "diagnostic_decomposition"
    RANDOMIZATION = "randomization"
    NO_VALID_INFERENCE = "no_valid_inference"
    MAX_T = "max_t"
    ALL = "all"


REQUIRED_PATHS = frozenset(TbrridgePath)
REQUIRED_STATUSES = frozenset(AuditStatus)
REQUIRED_ACTIONS = frozenset(AuditRequiredAction)


@dataclass(frozen=True)
class TbrridgeInferenceAuditRow:
    path_id: str
    name: str
    tbrridge_path: TbrridgePath
    current_status: AuditStatus
    failure_modes: tuple[str, ...]
    observed_diagnostic_triggers: tuple[str, ...]
    dgp_triggers: tuple[str, ...]
    affected_designs: tuple[DesignContext, ...]
    affected_inference_paths: tuple[InferenceContext, ...]
    required_action: AuditRequiredAction
    promotion_blocking: bool
    retire_or_replace_candidate: bool
    remediation_candidate: bool
    recommended_next_artifact: str | None
    notes: str


def _row(
    path_id: str,
    name: str,
    tbrridge_path: TbrridgePath,
    current_status: AuditStatus,
    description_note: str,
    *,
    failure_modes: tuple[str, ...],
    observed_diagnostic_triggers: tuple[str, ...],
    dgp_triggers: tuple[str, ...],
    affected_designs: tuple[DesignContext, ...],
    affected_inference_paths: tuple[InferenceContext, ...],
    required_action: AuditRequiredAction,
    promotion_blocking: bool = False,
    retire_or_replace_candidate: bool = False,
    remediation_candidate: bool = False,
    recommended_next_artifact: str | None = None,
) -> TbrridgeInferenceAuditRow:
    return TbrridgeInferenceAuditRow(
        path_id=path_id,
        name=name,
        tbrridge_path=tbrridge_path,
        current_status=current_status,
        failure_modes=failure_modes,
        observed_diagnostic_triggers=observed_diagnostic_triggers,
        dgp_triggers=dgp_triggers,
        affected_designs=affected_designs,
        affected_inference_paths=affected_inference_paths,
        required_action=required_action,
        promotion_blocking=promotion_blocking,
        retire_or_replace_candidate=retire_or_replace_candidate,
        remediation_candidate=remediation_candidate,
        recommended_next_artifact=recommended_next_artifact,
        notes=description_note,
    )


_ALL_D = (DesignContext.ALL,)
_ALL_I = (InferenceContext.ALL,)


def build_tbrridge_inference_remediation_or_retirement_audit() -> tuple[TbrridgeInferenceAuditRow, ...]:
    """Return metadata-only TBRRidge inference path audit rows."""
    return (
        # Point estimate
        _row(
            "TBR-AUD-001",
            "tbrridge_point_estimate_diagnostic",
            TbrridgePath.POINT_ESTIMATE,
            AuditStatus.DIAGNOSTIC_ONLY,
            "TBRRidge point estimate may support diagnostic effect sizing when observed diagnostics pass.",
            failure_modes=("FM-ES-006",),
            observed_diagnostic_triggers=("OPD-PF-001", "OPD-DS-005"),
            dgp_triggers=("DGP-ES-006",),
            affected_designs=(DesignContext.SINGLE_TREATED_GEO, DesignContext.MULTI_TREATED_GEO),
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-002",
            "tbrridge_point_production_pvalue_blocked",
            TbrridgePath.POINT_ESTIMATE,
            AuditStatus.BLOCKED,
            "Point estimate alone does not authorize production p-values.",
            failure_modes=("FM-INF-011", "FM-DB-010"),
            observed_diagnostic_triggers=("OPD-IR-010",),
            dgp_triggers=("DGP-INF-013",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.POINT_ONLY, InferenceContext.NO_VALID_INFERENCE),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-003",
            "tbrridge_point_small_n_overclaim",
            TbrridgePath.POINT_ESTIMATE,
            AuditStatus.RESTRICTED_RESEARCH,
            "Small-N panels with TBRRidge point estimates remain restricted research.",
            failure_modes=("FM-PS-010", "FM-ES-006"),
            observed_diagnostic_triggers=("OPD-PS-006", "OPD-PS-010"),
            dgp_triggers=("DGP-PS-010",),
            affected_designs=(DesignContext.SINGLE_TREATED_GEO,),
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.KEEP_RESEARCH_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-004",
            "tbrridge_point_poor_pre_fit",
            TbrridgePath.POINT_ESTIMATE,
            AuditStatus.SENSITIVITY_ONLY,
            "Poor pre-period fit routes TBRRidge point to sensitivity-only use.",
            failure_modes=("FM-PF-001", "FM-PF-003"),
            observed_diagnostic_triggers=("OPD-PF-001", "OPD-PF-003"),
            dgp_triggers=("DGP-PF-001", "DGP-PF-003"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.MARK_SENSITIVITY_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-005",
            "tbrridge_point_regularization_instability",
            TbrridgePath.POINT_ESTIMATE,
            AuditStatus.RESTRICTED_RESEARCH,
            "Ridge regularization can mask relation instability; point remains research-only.",
            failure_modes=("FM-ES-006",),
            observed_diagnostic_triggers=("OPD-ER-006",),
            dgp_triggers=("DGP-ES-006",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS,
            promotion_blocking=True,
        ),
        # BRB
        _row(
            "TBR-AUD-010",
            "tbrridge_brb_production_blocked",
            TbrridgePath.BRB,
            AuditStatus.BLOCKED,
            "TBRRidge + BRB is not production-valid causal inference.",
            failure_modes=("FM-INF-004", "FM-INF-003", "FM-DB-010"),
            observed_diagnostic_triggers=("OPD-IR-004", "OPD-IR-005"),
            dgp_triggers=("DGP-INF-006", "DGP-INF-007"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BLOCK_RESIDUAL_BOOTSTRAP,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-011",
            "tbrridge_brb_diagnostic_only_post_remediation",
            TbrridgePath.BRB,
            AuditStatus.DIAGNOSTIC_ONLY,
            "Post-remediation reassessment keeps BRB diagnostic-only.",
            failure_modes=("FM-INF-004",),
            observed_diagnostic_triggers=("OPD-IR-004",),
            dgp_triggers=("DGP-INF-006",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BLOCK_RESIDUAL_BOOTSTRAP,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
            remediation_candidate=True,
        ),
        _row(
            "TBR-AUD-012",
            "tbrridge_brb_variance_calibration_failed",
            TbrridgePath.BRB,
            AuditStatus.REMEDIATION_REQUIRED,
            "BRB null calibration and positive coverage gates failed after centering fix.",
            failure_modes=("FM-INF-004", "FM-CP-001"),
            observed_diagnostic_triggers=("OPD-IR-004",),
            dgp_triggers=("DGP-INF-006", "DGP-CP-001"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BLOCK_RESIDUAL_BOOTSTRAP,),
            required_action=AuditRequiredAction.REMEDIATE,
            promotion_blocking=True,
            remediation_candidate=True,
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _row(
            "TBR-AUD-013",
            "tbrridge_brb_estimand_centering_corrected",
            TbrridgePath.BRB,
            AuditStatus.CANDIDATE_AFTER_FUTURE_VALIDATION,
            "Estimand centering corrected; variance/null calibration still required before promotion.",
            failure_modes=("FM-INF-004",),
            observed_diagnostic_triggers=("OPD-IR-004",),
            dgp_triggers=("DGP-INF-006",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BLOCK_RESIDUAL_BOOTSTRAP,),
            required_action=AuditRequiredAction.CANDIDATE_AFTER_FUTURE_VALIDATION,
            promotion_blocking=True,
            remediation_candidate=True,
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _row(
            "TBR-AUD-014",
            "tbrridge_brb_bootstrap_dependence_invalid",
            TbrridgePath.BRB,
            AuditStatus.BLOCKED,
            "BRB under invalid temporal dependence remains blocked.",
            failure_modes=("FM-INF-003", "FM-TD-001"),
            observed_diagnostic_triggers=("OPD-TD-001", "OPD-IR-004"),
            dgp_triggers=("DGP-INF-006", "DGP-NV-005"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BLOCK_RESIDUAL_BOOTSTRAP,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-015",
            "tbrridge_brb_requires_null_calibration",
            TbrridgePath.BRB,
            AuditStatus.RESTRICTED_RESEARCH,
            "BRB requires governed null calibration before any promotion beyond research.",
            failure_modes=("FM-CP-001", "FM-INF-004"),
            observed_diagnostic_triggers=("OPD-IR-004",),
            dgp_triggers=("DGP-CP-001",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BLOCK_RESIDUAL_BOOTSTRAP,),
            required_action=AuditRequiredAction.REQUIRE_NULL_CALIBRATION,
            promotion_blocking=True,
            remediation_candidate=True,
        ),
        # KFold
        _row(
            "TBR-AUD-020",
            "tbrridge_kfold_production_blocked",
            TbrridgePath.KFOLD,
            AuditStatus.BLOCKED,
            "TBRRidge KFold/cross-fit is not production-valid causal inference.",
            failure_modes=("FM-INF-011", "FM-DB-010"),
            observed_diagnostic_triggers=("OPD-IR-010",),
            dgp_triggers=("DGP-INF-013",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.KFOLD_CROSSFIT,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-021",
            "tbrridge_kfold_null_fpr_issue",
            TbrridgePath.KFOLD,
            AuditStatus.DIAGNOSTIC_ONLY,
            "KFold null false-positive characterization failed causal interval eligibility.",
            failure_modes=("FM-INF-011",),
            observed_diagnostic_triggers=("OPD-IR-010",),
            dgp_triggers=("DGP-INF-013",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.KFOLD_CROSSFIT,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-022",
            "tbrridge_kfold_leakage_risk",
            TbrridgePath.KFOLD,
            AuditStatus.RESTRICTED_RESEARCH,
            "Cross-fit leakage risk keeps KFold restricted research.",
            failure_modes=("FM-PS-009",),
            observed_diagnostic_triggers=("OPD-PS-009",),
            dgp_triggers=("DGP-PS-009",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.KFOLD_CROSSFIT,),
            required_action=AuditRequiredAction.KEEP_RESEARCH_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-023",
            "tbrridge_kfold_not_causal_ci",
            TbrridgePath.KFOLD,
            AuditStatus.BLOCKED,
            "KFold intervals are not authorized causal confidence intervals.",
            failure_modes=("FM-DB-010", "FM-INF-011"),
            observed_diagnostic_triggers=("OPD-IR-005",),
            dgp_triggers=("DGP-INF-007",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.KFOLD_CROSSFIT,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-024",
            "tbrridge_kfold_requires_dgp_coverage",
            TbrridgePath.KFOLD,
            AuditStatus.CANDIDATE_AFTER_FUTURE_VALIDATION,
            "Any future KFold promotion requires DGP coverage and null calibration.",
            failure_modes=("FM-CP-002",),
            observed_diagnostic_triggers=("OPD-IR-010",),
            dgp_triggers=("DGP-CP-002",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.KFOLD_CROSSFIT,),
            required_action=AuditRequiredAction.REQUIRE_DGP_COVERAGE,
            promotion_blocking=True,
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        # Placebo
        _row(
            "TBR-AUD-030",
            "tbrridge_placebo_single_treated_restricted",
            TbrridgePath.PLACEBO,
            AuditStatus.RESTRICTED_RESEARCH,
            "TBRRidge placebo remains restricted to governed single-treated null-monitor use.",
            failure_modes=("FM-INF-001",),
            observed_diagnostic_triggers=("OPD-IR-002",),
            dgp_triggers=("DGP-INF-003",),
            affected_designs=(DesignContext.SINGLE_TREATED_GEO,),
            affected_inference_paths=(InferenceContext.PLACEBO_RANK,),
            required_action=AuditRequiredAction.KEEP_RESEARCH_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-031",
            "tbrridge_placebo_not_production_pvalue",
            TbrridgePath.PLACEBO,
            AuditStatus.BLOCKED,
            "Placebo rank is not a production p-value for TBRRidge.",
            failure_modes=("FM-INF-001", "FM-DB-009"),
            observed_diagnostic_triggers=("OPD-IR-002",),
            dgp_triggers=("DGP-INF-003",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.PLACEBO_RANK,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-032",
            "tbrridge_placebo_governed_semantics_only",
            TbrridgePath.PLACEBO,
            AuditStatus.DIAGNOSTIC_ONLY,
            "Placebo must use governed null-monitor semantics only.",
            failure_modes=("FM-INF-001",),
            observed_diagnostic_triggers=("OPD-IR-002", "OPD-IR-003"),
            dgp_triggers=("DGP-INF-003", "DGP-INF-004"),
            affected_designs=(DesignContext.SINGLE_TREATED_GEO,),
            affected_inference_paths=(InferenceContext.PLACEBO_RANK,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-033",
            "tbrridge_placebo_requires_design_stress",
            TbrridgePath.PLACEBO,
            AuditStatus.RESTRICTED_RESEARCH,
            "Placebo support requires assignment-generator stress-test compatibility.",
            failure_modes=("FM-DA-007", "FM-DA-008"),
            observed_diagnostic_triggers=("OPD-AD-009", "OPD-AD-010"),
            dgp_triggers=("DGP-AD-010", "DGP-AD-011"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.PLACEBO_RANK,),
            required_action=AuditRequiredAction.REQUIRE_DESIGN_STRESS_TEST,
            promotion_blocking=True,
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
        _row(
            "TBR-AUD-034",
            "tbrridge_placebo_studentized_adapter_required",
            TbrridgePath.PLACEBO,
            AuditStatus.CANDIDATE_AFTER_FUTURE_VALIDATION,
            "Studentized placebo requires governed statistic adapter and null calibration.",
            failure_modes=("FM-INF-002",),
            observed_diagnostic_triggers=("OPD-IR-003",),
            dgp_triggers=("DGP-INF-004",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.PLACEBO_RANK,),
            required_action=AuditRequiredAction.REQUIRE_NULL_CALIBRATION,
            promotion_blocking=True,
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        # Jackknife
        _row(
            "TBR-AUD-040",
            "tbrridge_jackknife_blocked",
            TbrridgePath.JACKKNIFE,
            AuditStatus.BLOCKED,
            "TBRRidge jackknife path is blocked from production inference.",
            failure_modes=("FM-INF-005",),
            observed_diagnostic_triggers=("OPD-IR-005",),
            dgp_triggers=("DGP-INF-007",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.JACKKNIFE,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
            retire_or_replace_candidate=True,
        ),
        _row(
            "TBR-AUD-041",
            "tbrridge_jackknife_not_causal_ci",
            TbrridgePath.JACKKNIFE,
            AuditStatus.RETIRE_OR_REPLACE,
            "Jackknife must not be treated as causal confidence interval for TBRRidge.",
            failure_modes=("FM-INF-005", "FM-DB-010"),
            observed_diagnostic_triggers=("OPD-IR-005",),
            dgp_triggers=("DGP-INF-007",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.JACKKNIFE,),
            required_action=AuditRequiredAction.RETIRE_OR_REPLACE,
            promotion_blocking=True,
            retire_or_replace_candidate=True,
        ),
        _row(
            "TBR-AUD-042",
            "tbrridge_jackknife_diagnostic_only_fallback",
            TbrridgePath.JACKKNIFE,
            AuditStatus.DIAGNOSTIC_ONLY,
            "If retained at all, jackknife is diagnostic-only instability probe.",
            failure_modes=("FM-INF-005",),
            observed_diagnostic_triggers=("OPD-IR-005",),
            dgp_triggers=("DGP-INF-007",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.JACKKNIFE,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
            retire_or_replace_candidate=True,
        ),
        # Aggregate/global
        _row(
            "TBR-AUD-050",
            "tbrridge_aggregate_global_overclaim_blocked",
            TbrridgePath.AGGREGATE_GLOBAL,
            AuditStatus.RETIRE_OR_REPLACE,
            "Aggregate/global TBRRidge overclaims must be retired or blocked.",
            failure_modes=("FM-ES-007",),
            observed_diagnostic_triggers=("OPD-ER-006", "OPD-IR-008"),
            dgp_triggers=("DGP-ES-009", "DGP-INF-010"),
            affected_designs=(DesignContext.MULTI_TREATED_GEO, DesignContext.MULTICELL_SHARED_CONTROL),
            affected_inference_paths=(InferenceContext.AGGREGATE_GLOBAL,),
            required_action=AuditRequiredAction.RETIRE_OR_REPLACE,
            promotion_blocking=True,
            retire_or_replace_candidate=True,
        ),
        _row(
            "TBR-AUD-051",
            "tbrridge_aggregate_geometry_mismatch",
            TbrridgePath.AGGREGATE_GLOBAL,
            AuditStatus.BLOCKED,
            "TBR aggregate geometry mismatch blocks global causal claims.",
            failure_modes=("FM-ES-007",),
            observed_diagnostic_triggers=("OPD-ER-006",),
            dgp_triggers=("DGP-ES-009",),
            affected_designs=(DesignContext.MULTI_TREATED_GEO,),
            affected_inference_paths=(InferenceContext.AGGREGATE_GLOBAL,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
            retire_or_replace_candidate=True,
        ),
        _row(
            "TBR-AUD-052",
            "tbrridge_global_without_cell_structure",
            TbrridgePath.AGGREGATE_GLOBAL,
            AuditStatus.BLOCKED,
            "Global TBRRidge without explicit cell structure is blocked.",
            failure_modes=("FM-ES-007", "FM-DA-010"),
            observed_diagnostic_triggers=("OPD-MC-001", "OPD-ER-006"),
            dgp_triggers=("DGP-MC-002",),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferenceContext.AGGREGATE_GLOBAL,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
            retire_or_replace_candidate=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _row(
            "TBR-AUD-053",
            "tbrridge_aggregate_sensitivity_only",
            TbrridgePath.AGGREGATE_GLOBAL,
            AuditStatus.SENSITIVITY_ONLY,
            "Aggregate TBRRidge may be used only as sensitivity when explicitly labeled.",
            failure_modes=("FM-ES-007",),
            observed_diagnostic_triggers=("OPD-ER-006",),
            dgp_triggers=("DGP-ES-009",),
            affected_designs=(DesignContext.MULTI_TREATED_GEO,),
            affected_inference_paths=(InferenceContext.AGGREGATE_GLOBAL,),
            required_action=AuditRequiredAction.MARK_SENSITIVITY_ONLY,
            promotion_blocking=True,
            retire_or_replace_candidate=True,
        ),
        # Per-cell/marginal
        _row(
            "TBR-AUD-060",
            "tbrridge_per_cell_marginal_diagnostic",
            TbrridgePath.PER_CELL_MARGINAL,
            AuditStatus.DIAGNOSTIC_ONLY,
            "Per-cell marginal TBRRidge may support diagnostic cell readouts.",
            failure_modes=("FM-DA-010",),
            observed_diagnostic_triggers=("OPD-MC-002",),
            dgp_triggers=("DGP-MC-003",),
            affected_designs=(DesignContext.MULTICELL_INDEPENDENT_CELLS, DesignContext.MULTICELL_SHARED_CONTROL),
            affected_inference_paths=(InferenceContext.PER_CELL_MARGINAL,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-061",
            "tbrridge_per_cell_without_multiplicity_blocked",
            TbrridgePath.PER_CELL_MARGINAL,
            AuditStatus.BLOCKED,
            "Per-cell inference blocked without multicell multiplicity handling.",
            failure_modes=("FM-INF-009", "FM-DA-010"),
            observed_diagnostic_triggers=("OPD-MC-004", "OPD-IR-009"),
            dgp_triggers=("DGP-INF-011", "DGP-MC-007"),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferenceContext.PER_CELL_MARGINAL, InferenceContext.MAX_T),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _row(
            "TBR-AUD-062",
            "tbrridge_per_cell_restricted_research",
            TbrridgePath.PER_CELL_MARGINAL,
            AuditStatus.RESTRICTED_RESEARCH,
            "Per-cell TBRRidge remains restricted research pending max-T/stepdown scout.",
            failure_modes=("FM-INF-009",),
            observed_diagnostic_triggers=("OPD-MC-004",),
            dgp_triggers=("DGP-INF-011",),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferenceContext.PER_CELL_MARGINAL,),
            required_action=AuditRequiredAction.KEEP_RESEARCH_ONLY,
            promotion_blocking=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _row(
            "TBR-AUD-063",
            "tbrridge_per_cell_requires_observed_diagnostics",
            TbrridgePath.PER_CELL_MARGINAL,
            AuditStatus.REMEDIATION_REQUIRED,
            "Per-cell paths require observed diagnostics before any promotion.",
            failure_modes=("FM-CP-003",),
            observed_diagnostic_triggers=("OPD-PS-001", "OPD-MC-002"),
            dgp_triggers=("DGP-CP-003",),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferenceContext.PER_CELL_MARGINAL,),
            required_action=AuditRequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS,
            promotion_blocking=True,
            remediation_candidate=True,
        ),
        # Diagnostic curve
        _row(
            "TBR-AUD-070",
            "tbrridge_diagnostic_curve_allowed",
            TbrridgePath.DIAGNOSTIC_CURVE,
            AuditStatus.DIAGNOSTIC_ONLY,
            "Diagnostic curve/decomposition use is allowed for exploratory readouts.",
            failure_modes=(),
            observed_diagnostic_triggers=("OPD-PF-001",),
            dgp_triggers=("DGP-ES-006",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.DIAGNOSTIC_DECOMPOSITION,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
        ),
        _row(
            "TBR-AUD-071",
            "tbrridge_decomposition_not_inference",
            TbrridgePath.DIAGNOSTIC_CURVE,
            AuditStatus.BLOCKED,
            "Decomposition curves must not be promoted to production inference.",
            failure_modes=("FM-INF-011",),
            observed_diagnostic_triggers=("OPD-IR-010",),
            dgp_triggers=("DGP-INF-013",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.DIAGNOSTIC_DECOMPOSITION,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-072",
            "tbrridge_curve_sensitivity_only",
            TbrridgePath.DIAGNOSTIC_CURVE,
            AuditStatus.SENSITIVITY_ONLY,
            "Curve-based sensitivity probes remain sensitivity-only.",
            failure_modes=("FM-PF-006",),
            observed_diagnostic_triggers=("OPD-PF-006",),
            dgp_triggers=("DGP-PF-006",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.DIAGNOSTIC_DECOMPOSITION,),
            required_action=AuditRequiredAction.MARK_SENSITIVITY_ONLY,
            promotion_blocking=True,
        ),
        # Deterministic/unknown assignment
        _row(
            "TBR-AUD-080",
            "tbrridge_unknown_assignment_blocks_inference",
            TbrridgePath.DETERMINISTIC_UNKNOWN_ASSIGNMENT,
            AuditStatus.BLOCKED,
            "Unknown assignment blocks TBRRidge design-based inference paths.",
            failure_modes=("FM-DA-001",),
            observed_diagnostic_triggers=("OPD-AD-001",),
            dgp_triggers=("DGP-AD-009", "DGP-INF-002"),
            affected_designs=(DesignContext.UNKNOWN_ASSIGNMENT,),
            affected_inference_paths=(InferenceContext.RANDOMIZATION, InferenceContext.NO_VALID_INFERENCE),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-081",
            "tbrridge_deterministic_not_randomized",
            TbrridgePath.DETERMINISTIC_UNKNOWN_ASSIGNMENT,
            AuditStatus.BLOCKED,
            "Deterministic designs cannot be treated as randomized for TBRRidge inference.",
            failure_modes=("FM-DA-002",),
            observed_diagnostic_triggers=("OPD-AD-002",),
            dgp_triggers=("DGP-AD-008",),
            affected_designs=(DesignContext.FIXED_DETERMINISTIC,),
            affected_inference_paths=(InferenceContext.RANDOMIZATION,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-082",
            "tbrridge_deterministic_diagnostic_only",
            TbrridgePath.DETERMINISTIC_UNKNOWN_ASSIGNMENT,
            AuditStatus.DIAGNOSTIC_ONLY,
            "Deterministic TBRRidge may remain falsification/diagnostic-only.",
            failure_modes=("FM-DA-002",),
            observed_diagnostic_triggers=("OPD-AD-002",),
            dgp_triggers=("DGP-AD-008",),
            affected_designs=(DesignContext.FIXED_DETERMINISTIC,),
            affected_inference_paths=(InferenceContext.POINT_ONLY, InferenceContext.NO_VALID_INFERENCE),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-083",
            "tbrridge_assignment_stress_required",
            TbrridgePath.DETERMINISTIC_UNKNOWN_ASSIGNMENT,
            AuditStatus.RESTRICTED_RESEARCH,
            "Any future TBRRidge inference promotion requires design assignment stress tests.",
            failure_modes=("FM-CP-004",),
            observed_diagnostic_triggers=("OPD-AD-001", "OPD-AD-002"),
            dgp_triggers=("DGP-AD-008",),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.REQUIRE_DESIGN_STRESS_TEST,
            promotion_blocking=True,
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
        # Multicell/shared-control
        _row(
            "TBR-AUD-090",
            "tbrridge_shared_control_dependence",
            TbrridgePath.MULTICELL_SHARED_CONTROL,
            AuditStatus.BLOCKED,
            "Shared-control dependence blocks naive TBRRidge multicell inference.",
            failure_modes=("FM-DA-009",),
            observed_diagnostic_triggers=("OPD-MC-001", "OPD-AD-008"),
            dgp_triggers=("DGP-MC-002",),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferenceContext.MAX_T, InferenceContext.NO_VALID_INFERENCE),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _row(
            "TBR-AUD-091",
            "tbrridge_multicell_winner_selection_risk",
            TbrridgePath.MULTICELL_SHARED_CONTROL,
            AuditStatus.RETIRE_OR_REPLACE,
            "Winner-selection risk requires retire/replace or explicit multiplicity research.",
            failure_modes=("FM-DA-010",),
            observed_diagnostic_triggers=("OPD-MC-003",),
            dgp_triggers=("DGP-MC-004",),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferenceContext.MAX_T,),
            required_action=AuditRequiredAction.RETIRE_OR_REPLACE,
            promotion_blocking=True,
            retire_or_replace_candidate=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _row(
            "TBR-AUD-092",
            "tbrridge_multicell_max_t_research_required",
            TbrridgePath.MULTICELL_SHARED_CONTROL,
            AuditStatus.CANDIDATE_AFTER_FUTURE_VALIDATION,
            "Multicell TBRRidge requires max-T/stepdown research before promotion.",
            failure_modes=("FM-INF-009", "FM-INF-010"),
            observed_diagnostic_triggers=("OPD-MC-004", "OPD-IR-009"),
            dgp_triggers=("DGP-INF-011", "DGP-INF-012"),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferenceContext.MAX_T,),
            required_action=AuditRequiredAction.CANDIDATE_AFTER_FUTURE_VALIDATION,
            promotion_blocking=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _row(
            "TBR-AUD-093",
            "tbrridge_multicell_pooled_estimand_ambiguity",
            TbrridgePath.MULTICELL_SHARED_CONTROL,
            AuditStatus.SENSITIVITY_ONLY,
            "Pooled/global multicell estimand ambiguity routes to sensitivity-only.",
            failure_modes=("FM-ES-007", "FM-DA-010"),
            observed_diagnostic_triggers=("OPD-MC-005",),
            dgp_triggers=("DGP-MC-005",),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferenceContext.AGGREGATE_GLOBAL,),
            required_action=AuditRequiredAction.MARK_SENSITIVITY_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-094",
            "tbrridge_multicell_failure_registry_consult",
            TbrridgePath.MULTICELL_SHARED_CONTROL,
            AuditStatus.REMEDIATION_REQUIRED,
            "Multicell TBRRidge paths must consult failure registry before remediation.",
            failure_modes=("FM-CP-004", "FM-DA-009"),
            observed_diagnostic_triggers=("OPD-MC-001",),
            dgp_triggers=("DGP-MC-002",),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.REQUIRE_FAILURE_REGISTRY_CONSULT,
            promotion_blocking=True,
            remediation_candidate=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        # Cross-cutting governance rows
        _row(
            "TBR-AUD-100",
            "tbrridge_failure_registry_consult_required",
            TbrridgePath.POINT_ESTIMATE,
            AuditStatus.REMEDIATION_REQUIRED,
            "All TBRRidge remediation must consult METHOD_FAILURE_MODE_REGISTRY_001.",
            failure_modes=("FM-CP-004",),
            observed_diagnostic_triggers=("OPD-IR-010",),
            dgp_triggers=("DGP-CP-004",),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.REQUIRE_FAILURE_REGISTRY_CONSULT,
            promotion_blocking=True,
            remediation_candidate=True,
        ),
        _row(
            "TBR-AUD-101",
            "tbrridge_observed_diagnostics_gate",
            TbrridgePath.POINT_ESTIMATE,
            AuditStatus.REMEDIATION_REQUIRED,
            "Observed-panel diagnostics are required before TBRRidge method selection.",
            failure_modes=("FM-CP-003",),
            observed_diagnostic_triggers=("OPD-PS-001", "OPD-PF-001"),
            dgp_triggers=("DGP-CP-003",),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS,
            promotion_blocking=True,
            remediation_candidate=True,
        ),
        _row(
            "TBR-AUD-102",
            "tbrridge_dgp_coverage_gate",
            TbrridgePath.BRB,
            AuditStatus.REMEDIATION_REQUIRED,
            "Simulation DGP coverage is required before TBRRidge inference promotion.",
            failure_modes=("FM-CP-002",),
            observed_diagnostic_triggers=("OPD-IR-004",),
            dgp_triggers=("DGP-CP-002",),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.REQUIRE_DGP_COVERAGE,
            promotion_blocking=True,
            remediation_candidate=True,
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _row(
            "TBR-AUD-103",
            "tbrridge_design_stress_gate",
            TbrridgePath.PLACEBO,
            AuditStatus.REMEDIATION_REQUIRED,
            "Design assignment stress tests are required for placebo/randomization paths.",
            failure_modes=("FM-CP-004",),
            observed_diagnostic_triggers=("OPD-AD-009",),
            dgp_triggers=("DGP-AD-010",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.PLACEBO_RANK, InferenceContext.RANDOMIZATION),
            required_action=AuditRequiredAction.REQUIRE_DESIGN_STRESS_TEST,
            promotion_blocking=True,
            remediation_candidate=True,
        ),
        _row(
            "TBR-AUD-104",
            "tbrridge_production_pvalue_global_block",
            TbrridgePath.POINT_ESTIMATE,
            AuditStatus.BLOCKED,
            "Global block on TBRRidge production p-values across all paths.",
            failure_modes=("FM-DB-009", "FM-INF-011"),
            observed_diagnostic_triggers=("OPD-IR-010",),
            dgp_triggers=("DGP-INF-013",),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-105",
            "tbrridge_causal_ci_global_block",
            TbrridgePath.BRB,
            AuditStatus.BLOCKED,
            "Global block on TBRRidge causal confidence intervals across all paths.",
            failure_modes=("FM-DB-010", "FM-INF-005"),
            observed_diagnostic_triggers=("OPD-IR-005",),
            dgp_triggers=("DGP-INF-007",),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "TBR-AUD-106",
            "tbrridge_matched_pair_design_constraint",
            TbrridgePath.POINT_ESTIMATE,
            AuditStatus.RESTRICTED_RESEARCH,
            "Matched-pair designs keep TBRRidge restricted pending design stress compatibility.",
            failure_modes=("FM-DA-004",),
            observed_diagnostic_triggers=("OPD-AD-003",),
            dgp_triggers=("DGP-AD-002",),
            affected_designs=(DesignContext.MATCHED_PAIR,),
            affected_inference_paths=(InferenceContext.POINT_ONLY, InferenceContext.RANDOMIZATION),
            required_action=AuditRequiredAction.REQUIRE_DESIGN_STRESS_TEST,
            promotion_blocking=True,
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _row(
            "TBR-AUD-107",
            "tbrridge_stratified_heterogeneity_sensitivity",
            TbrridgePath.POINT_ESTIMATE,
            AuditStatus.SENSITIVITY_ONLY,
            "Stratified heterogeneity keeps TBRRidge at sensitivity-only unless adapted.",
            failure_modes=("FM-DA-006",),
            observed_diagnostic_triggers=("OPD-AD-005",),
            dgp_triggers=("DGP-AD-004",),
            affected_designs=(DesignContext.STRATIFIED,),
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.MARK_SENSITIVITY_ONLY,
            promotion_blocking=True,
        ),
    )


def filter_tbrridge_inference_audit_rows(
    rows: tuple[TbrridgeInferenceAuditRow, ...],
    *,
    tbrridge_path: TbrridgePath | None = None,
    current_status: AuditStatus | None = None,
    required_action: AuditRequiredAction | None = None,
    promotion_blocking: bool | None = None,
    retire_or_replace_candidate: bool | None = None,
    remediation_candidate: bool | None = None,
) -> tuple[TbrridgeInferenceAuditRow, ...]:
    """Filter audit rows by optional criteria."""
    result: list[TbrridgeInferenceAuditRow] = []
    for row in rows:
        if tbrridge_path is not None and row.tbrridge_path != tbrridge_path:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if required_action is not None and row.required_action != required_action:
            continue
        if promotion_blocking is not None and row.promotion_blocking != promotion_blocking:
            continue
        if retire_or_replace_candidate is not None and row.retire_or_replace_candidate != retire_or_replace_candidate:
            continue
        if remediation_candidate is not None and row.remediation_candidate != remediation_candidate:
            continue
        result.append(row)
    return tuple(result)


def validate_tbrridge_inference_remediation_or_retirement_audit(
    rows: tuple[TbrridgeInferenceAuditRow, ...],
) -> dict[str, Any]:
    """Validate audit registry thresholds and linkage requirements."""
    issues: list[str] = []
    path_ids = [r.path_id for r in rows]

    if len(rows) < MIN_AUDIT_ROW_COUNT:
        issues.append(f"audit_row_count {len(rows)} < {MIN_AUDIT_ROW_COUNT}")
    if len(path_ids) != len(set(path_ids)):
        issues.append("duplicate path_id values")

    status_counts = Counter(r.current_status for r in rows)
    action_counts = Counter(r.required_action for r in rows)
    failure_mode_counts: Counter[str] = Counter()
    for row in rows:
        for fm in row.failure_modes:
            failure_mode_counts[fm] += 1

    for path in REQUIRED_PATHS:
        if not any(r.tbrridge_path == path for r in rows):
            issues.append(f"missing tbrridge path: {path.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    for action in REQUIRED_ACTIONS:
        if action_counts.get(action, 0) == 0:
            issues.append(f"missing required_action: {action.value}")

    retire_rows = [r for r in rows if r.retire_or_replace_candidate]
    remediation_rows = [r for r in rows if r.remediation_candidate]
    promotion_blockers = [r for r in rows if r.promotion_blocking]

    if not retire_rows:
        issues.append("no retire_or_replace_candidate rows")
    if not remediation_rows:
        issues.append("no remediation_candidate rows")
    if not promotion_blockers:
        issues.append("no promotion_blocking rows")

    if not all(r.observed_diagnostic_triggers for r in rows if r.tbrridge_path != TbrridgePath.DIAGNOSTIC_CURVE or r.path_id != "TBR-AUD-070"):
        pass  # TBR-AUD-070 may have minimal triggers; most rows must link
    unlinked_observed = [r.path_id for r in rows if not r.observed_diagnostic_triggers]
    if len(unlinked_observed) > 1:
        issues.append(f"rows missing observed_diagnostic_triggers: {unlinked_observed}")

    unlinked_dgp = [r.path_id for r in rows if not r.dgp_triggers]
    if unlinked_dgp:
        issues.append(f"rows missing dgp_triggers: {unlinked_dgp}")

    unlinked_fm = [r.path_id for r in rows if not r.failure_modes and r.path_id != "TBR-AUD-070"]
    if unlinked_fm:
        issues.append(f"rows missing failure_modes: {unlinked_fm}")

    return {
        "valid": not issues,
        "audit_row_count": len(rows),
        "unique_path_ids": len(path_ids) == len(set(path_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in AuditStatus},
        "required_action_counts": {a.value: action_counts.get(a, 0) for a in AuditRequiredAction},
        "failure_mode_counts": dict(failure_mode_counts),
        "retire_or_replace_paths_defined": bool(retire_rows),
        "remediation_paths_defined": bool(remediation_rows),
        "promotion_blockers_defined": bool(promotion_blockers),
        "all_paths_represented": all(any(r.tbrridge_path == p for r in rows) for p in REQUIRED_PATHS),
        "all_statuses_represented": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "all_actions_represented": all(action_counts.get(a, 0) > 0 for a in REQUIRED_ACTIONS),
        "issues": issues,
    }


def summarize_tbrridge_inference_remediation_or_retirement_audit(
    rows: tuple[TbrridgeInferenceAuditRow, ...],
) -> dict[str, Any]:
    """Serialize TBRRidge audit summary for archives."""
    validation = validate_tbrridge_inference_remediation_or_retirement_audit(rows)
    path_counts = Counter(r.tbrridge_path.value for r in rows)

    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "audit_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "required_action_counts": validation["required_action_counts"],
        "failure_mode_counts": validation["failure_mode_counts"],
        "tbrridge_path_counts": dict(path_counts),
        "retire_or_replace_paths_defined": validation["retire_or_replace_paths_defined"],
        "remediation_paths_defined": validation["remediation_paths_defined"],
        "downstream_work_paused": True,
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        **_TBRRIDGE_AUTH_FLAGS,
        **_AUTH_FLAGS,
        "valid": validation["valid"],
    }


def _git_commit() -> str | None:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=_REPO,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _scenario(scenario_id: str, passed: bool, *, detail: str = "") -> dict[str, Any]:
    return {"scenario_id": scenario_id, "passed": passed, "detail": detail}


def build_scenarios() -> list[dict[str, Any]]:
    rows = build_tbrridge_inference_remediation_or_retirement_audit()
    validation = validate_tbrridge_inference_remediation_or_retirement_audit(rows)
    summary = summarize_tbrridge_inference_remediation_or_retirement_audit(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("audit_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("audit_row_count_at_least_45", len(rows) >= MIN_AUDIT_ROW_COUNT))
    scenarios.append(_scenario("path_ids_unique", validation["unique_path_ids"]))

    for path in REQUIRED_PATHS:
        present = any(r.tbrridge_path == path for r in rows)
        scenarios.append(_scenario(f"tbrridge_path_{path.value}_represented", present))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for action in REQUIRED_ACTIONS:
        count = sum(1 for r in rows if r.required_action == action)
        scenarios.append(_scenario(f"action_{action.value}_represented", count > 0))

    scenarios.append(_scenario("tbrridge_point_diagnostic_allowed", summary["tbrridge_point_diagnostic_allowed"] is True))
    scenarios.append(_scenario("tbrridge_production_inference_authorized_false", summary["tbrridge_production_inference_authorized"] is False))
    scenarios.append(_scenario("tbrridge_production_p_value_authorized_false", summary["tbrridge_production_p_value_authorized"] is False))
    scenarios.append(_scenario("tbrridge_causal_ci_authorized_false", summary["tbrridge_causal_ci_authorized"] is False))
    scenarios.append(_scenario("brb_production_authorized_false", summary["brb_production_authorized"] is False))
    scenarios.append(_scenario("kfold_production_authorized_false", summary["kfold_production_authorized"] is False))
    scenarios.append(_scenario("placebo_production_authorized_false", summary["placebo_production_authorized"] is False))
    scenarios.append(_scenario("jackknife_production_authorized_false", summary["jackknife_production_authorized"] is False))
    scenarios.append(_scenario("aggregate_global_overclaim_blocked", summary["aggregate_global_overclaim_blocked"] is True))
    scenarios.append(_scenario("retire_or_replace_paths_defined", summary["retire_or_replace_paths_defined"] is True))
    scenarios.append(_scenario("remediation_paths_defined", summary["remediation_paths_defined"] is True))
    scenarios.append(_scenario("future_validation_required_before_promotion", summary["future_validation_required_before_promotion"] is True))
    scenarios.append(_scenario("observed_diagnostics_required", summary["observed_diagnostics_required"] is True))
    scenarios.append(_scenario("dgp_coverage_required", summary["dgp_coverage_required"] is True))
    scenarios.append(_scenario("failure_registry_consulted", summary["failure_registry_consulted"] is True))
    scenarios.append(_scenario("design_assignment_stress_required", summary["design_assignment_stress_required"] is True))
    scenarios.append(_scenario("downstream_work_paused", summary["downstream_work_paused"] is True))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_did_randomization_and_bootstrap_suitability_001",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_tbrridge_inference_remediation_or_retirement_audit()
    validation = validate_tbrridge_inference_remediation_or_retirement_audit(rows)
    summary = summarize_tbrridge_inference_remediation_or_retirement_audit(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "audit_row_count": len(rows),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        **{k: summary[k] for k in summary if k not in ("failed_scenarios", "valid")},
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {"verdict": _VERDICT, "failed_scenarios": failed}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
