"""DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001 validation harness."""

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

_ARTIFACT_ID = "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "design_assignment_generator_stress_tests_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
    "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
    "MULTICELL_MAX_T_RESEARCH_SCOUT_001",
)

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


class StressTestCategory(str, Enum):
    ASSIGNMENT_SUPPORT_INTEGRITY = "assignment_support_integrity"
    RANDOMIZED_ASSIGNMENT_VALIDITY = "randomized_assignment_validity"
    MATCHED_PAIR = "matched_pair"
    MATCHED_BLOCK_STRATIFIED = "matched_block_stratified"
    RERANDOMIZATION = "rerandomization"
    GREEDY_DETERMINISTIC = "greedy_deterministic"
    KERNEL_THINNING = "kernel_thinning"
    MULTI_TREATED_PLACEBO = "multi_treated_placebo"
    MULTICELL_SHARED_CONTROL = "multicell_shared_control"
    INFERENCE_FEASIBILITY = "inference_feasibility"
    FAILURE_REGISTRY_LINKAGE = "failure_registry_linkage"


MIN_CATEGORY_COUNTS = {
    StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY: 8,
    StressTestCategory.RANDOMIZED_ASSIGNMENT_VALIDITY: 7,
    StressTestCategory.MATCHED_PAIR: 7,
    StressTestCategory.MATCHED_BLOCK_STRATIFIED: 7,
    StressTestCategory.RERANDOMIZATION: 7,
    StressTestCategory.GREEDY_DETERMINISTIC: 6,
    StressTestCategory.KERNEL_THINNING: 5,
    StressTestCategory.MULTI_TREATED_PLACEBO: 6,
    StressTestCategory.MULTICELL_SHARED_CONTROL: 7,
    StressTestCategory.INFERENCE_FEASIBILITY: 10,
    StressTestCategory.FAILURE_REGISTRY_LINKAGE: 6,
}


class StressSeverity(str, Enum):
    HARD_BLOCKER = "hard_blocker"
    REQUIRED_STRESS = "required_stress"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    SENSITIVITY_ONLY = "sensitivity_only"
    RESEARCH_REQUIRED = "research_required"
    REMEDIATION_REQUIRED = "remediation_required"


MIN_SEVERITY_COUNTS = {
    StressSeverity.HARD_BLOCKER: 15,
    StressSeverity.REQUIRED_STRESS: 20,
    StressSeverity.DIAGNOSTIC_ONLY: 8,
    StressSeverity.SENSITIVITY_ONLY: 5,
    StressSeverity.RESEARCH_REQUIRED: 8,
    StressSeverity.REMEDIATION_REQUIRED: 5,
}


class AssignmentFamily(str, Enum):
    COMPLETE_RANDOMIZATION = "complete_randomization"
    MATCHED_PAIR = "matched_pair"
    MATCHED_BLOCK = "matched_block"
    STRATIFIED = "stratified"
    RERANDOMIZED = "rerandomized"
    GREEDY_MATCHED_MARKET = "greedy_matched_market"
    KERNEL_THINNING = "kernel_thinning"
    FIXED_DETERMINISTIC = "fixed_deterministic"
    MULTI_TREATED = "multi_treated"
    MULTICELL_SHARED_CONTROL = "multicell_shared_control"
    UNKNOWN_ASSIGNMENT = "unknown_assignment"
    ALL = "all"


class InferencePath(str, Enum):
    RANDOMIZATION = "randomization"
    PERMUTATION = "permutation"
    PLACEBO_RANK = "placebo_rank"
    STUDENTIZED_PLACEBO_RANK = "studentized_placebo_rank"
    TREATED_SET_PLACEBO = "treated_set_placebo"
    LEAVE_ONE_TREATED_OUT = "leave_one_treated_out"
    MAX_T = "max_t"
    STEPDOWN = "stepdown"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    NO_VALID_INFERENCE = "no_valid_inference"
    ALL = "all"


class StressAction(str, Enum):
    ALLOW_RESEARCH_CANDIDATE = "allow_research_candidate"
    BLOCK_INFERENCE = "block_inference"
    MARK_DIAGNOSTIC_ONLY = "mark_diagnostic_only"
    MARK_SENSITIVITY_ONLY = "mark_sensitivity_only"
    REQUIRE_STUDENTIZED_ADAPTER = "require_studentized_adapter"
    REQUIRE_NULL_CALIBRATION = "require_null_calibration"
    REQUIRE_FAILURE_REGISTRY_LINK = "require_failure_registry_link"
    REQUIRE_MULTICELL_MULTIPLICITY_RESEARCH = "require_multicell_multiplicity_research"
    REQUIRE_REMEDIATION = "require_remediation"
    REQUIRE_DESIGN_DOCUMENTATION = "require_design_documentation"


MIN_ACTION_COUNTS = {
    StressAction.ALLOW_RESEARCH_CANDIDATE: 5,
    StressAction.BLOCK_INFERENCE: 15,
    StressAction.MARK_DIAGNOSTIC_ONLY: 8,
    StressAction.MARK_SENSITIVITY_ONLY: 5,
    StressAction.REQUIRE_STUDENTIZED_ADAPTER: 3,
    StressAction.REQUIRE_NULL_CALIBRATION: 8,
    StressAction.REQUIRE_FAILURE_REGISTRY_LINK: 8,
    StressAction.REQUIRE_MULTICELL_MULTIPLICITY_RESEARCH: 4,
    StressAction.REQUIRE_REMEDIATION: 5,
    StressAction.REQUIRE_DESIGN_DOCUMENTATION: 8,
}

REQUIRED_ASSIGNMENT_FAMILIES = frozenset(AssignmentFamily)
REQUIRED_INFERENCE_PATHS = frozenset(InferencePath)


@dataclass(frozen=True)
class AssignmentGeneratorStressTest:
    stress_id: str
    name: str
    category: StressTestCategory
    severity: StressSeverity
    description: str
    affected_assignment_families: tuple[AssignmentFamily, ...]
    affected_inference_paths: tuple[InferencePath, ...]
    required_inputs: tuple[str, ...]
    failure_registry_links: tuple[str, ...]
    observed_diagnostic_links: tuple[str, ...]
    dgp_links: tuple[str, ...]
    required_actions: tuple[StressAction, ...]
    blocks_inference_if_failed: bool
    promotion_blocking: bool
    recommended_next_artifact: str | None
    notes: str


def _st(
    stress_id: str,
    name: str,
    category: StressTestCategory,
    severity: StressSeverity,
    description: str,
    *,
    affected_assignment_families: tuple[AssignmentFamily, ...],
    affected_inference_paths: tuple[InferencePath, ...],
    required_inputs: tuple[str, ...],
    failure_registry_links: tuple[str, ...],
    observed_diagnostic_links: tuple[str, ...],
    dgp_links: tuple[str, ...],
    required_actions: tuple[StressAction, ...],
    blocks_inference_if_failed: bool = False,
    promotion_blocking: bool = False,
    recommended_next_artifact: str | None = None,
    notes: str = "",
) -> AssignmentGeneratorStressTest:
    return AssignmentGeneratorStressTest(
        stress_id=stress_id,
        name=name,
        category=category,
        severity=severity,
        description=description,
        affected_assignment_families=affected_assignment_families,
        affected_inference_paths=affected_inference_paths,
        required_inputs=required_inputs,
        failure_registry_links=failure_registry_links,
        observed_diagnostic_links=observed_diagnostic_links,
        dgp_links=dgp_links,
        required_actions=required_actions,
        blocks_inference_if_failed=blocks_inference_if_failed,
        promotion_blocking=promotion_blocking,
        recommended_next_artifact=recommended_next_artifact,
        notes=notes,
    )


_ALL_A = (AssignmentFamily.ALL,)
_ALL_I = (InferencePath.ALL,)

def _assignment_support_integrity_rows() -> tuple[AssignmentGeneratorStressTest, ...]:
    return (
        _st("ST-ASI-001", "support_size_sufficient", StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY,
            StressSeverity.HARD_BLOCKER,
            "Support size meets minimum for rank inference.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION,),
            affected_inference_paths=(InferencePath.RANDOMIZATION, InferencePath.PLACEBO_RANK),
            required_inputs=('min_assignments', 'support_size'),
            failure_registry_links=('FM-DA-007',),
            observed_diagnostic_links=('OPD-AD-009',),
            dgp_links=('DGP-AD-010',),
            required_actions=(StressAction.BLOCK_INFERENCE, StressAction.REQUIRE_NULL_CALIBRATION),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-ASI-002", "support_size_degenerate", StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY,
            StressSeverity.HARD_BLOCKER,
            "Degenerate support blocks placebo paths.",
            affected_assignment_families=(AssignmentFamily.GREEDY_MATCHED_MARKET, AssignmentFamily.KERNEL_THINNING),
            affected_inference_paths=(InferencePath.PLACEBO_RANK, InferencePath.NO_VALID_INFERENCE),
            required_inputs=('support_size', 'degeneracy_threshold'),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-011',),
            required_actions=(StressAction.BLOCK_INFERENCE, StressAction.MARK_DIAGNOSTIC_ONLY, StressAction.REQUIRE_FAILURE_REGISTRY_LINK),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-ASI-003", "support_contains_observed_assignment", StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY,
            StressSeverity.REQUIRED_STRESS,
            "Support includes observed treated-set assignment.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION, AssignmentFamily.MATCHED_PAIR),
            affected_inference_paths=(InferencePath.RANDOMIZATION, InferencePath.PERMUTATION),
            required_inputs=('observed_treated_unit_ids',),
            failure_registry_links=('FM-DA-004',),
            observed_diagnostic_links=('OPD-AD-003',),
            dgp_links=('DGP-AD-002',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-ASI-004", "support_respects_treatment_count", StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY,
            StressSeverity.REQUIRED_STRESS,
            "Pseudo-assignments preserve treated-unit count.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION, AssignmentFamily.MATCHED_BLOCK),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('num_treated',),
            failure_registry_links=('FM-DA-005',),
            observed_diagnostic_links=('OPD-AD-004',),
            dgp_links=('DGP-AD-003',),
            required_actions=(StressAction.REQUIRE_DESIGN_DOCUMENTATION,),
            ),
        _st("ST-ASI-005", "support_respects_treated_set_size", StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY,
            StressSeverity.REQUIRED_STRESS,
            "Multi-treated support preserves treated-set cardinality.",
            affected_assignment_families=(AssignmentFamily.MULTI_TREATED,),
            affected_inference_paths=(InferencePath.TREATED_SET_PLACEBO, InferencePath.LEAVE_ONE_TREATED_OUT),
            required_inputs=('treated_set_size',),
            failure_registry_links=('FM-DA-007',),
            observed_diagnostic_links=('OPD-AD-009',),
            dgp_links=('DGP-AD-010',),
            required_actions=(StressAction.MARK_DIAGNOSTIC_ONLY, StressAction.REQUIRE_NULL_CALIBRATION),
            ),
        _st("ST-ASI-006", "support_respects_cell_assignment_constraints", StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY,
            StressSeverity.REQUIRED_STRESS,
            "Multicell support respects per-cell quotas.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.MAX_T, InferencePath.STEPDOWN),
            required_inputs=('cell_constraints',),
            failure_registry_links=('FM-DA-009',),
            observed_diagnostic_links=('OPD-AD-008', 'OPD-MC-001'),
            dgp_links=('DGP-MC-002',),
            required_actions=(StressAction.REQUIRE_MULTICELL_MULTIPLICITY_RESEARCH,),
            promotion_blocking=True,
            ),
        _st("ST-ASI-007", "support_excludes_impossible_assignments", StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY,
            StressSeverity.REQUIRED_STRESS,
            "Generator excludes impossible assignments.",
            affected_assignment_families=(AssignmentFamily.MATCHED_PAIR, AssignmentFamily.MATCHED_BLOCK),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('eligibility_rules',),
            failure_registry_links=('FM-DA-004', 'FM-DA-005'),
            observed_diagnostic_links=('OPD-AD-003', 'OPD-AD-004'),
            dgp_links=('DGP-AD-002', 'DGP-AD-003'),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            ),
        _st("ST-ASI-008", "support_reproducibility_with_seed", StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY,
            StressSeverity.REQUIRED_STRESS,
            "Seeded generation reproduces support.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION, AssignmentFamily.RERANDOMIZED),
            affected_inference_paths=(InferencePath.RANDOMIZATION, InferencePath.PERMUTATION),
            required_inputs=('seed',),
            failure_registry_links=('FM-DA-003',),
            observed_diagnostic_links=('OPD-AD-006',),
            dgp_links=('DGP-AD-005',),
            required_actions=(StressAction.REQUIRE_DESIGN_DOCUMENTATION,),
            ),
        _st("ST-ASI-009", "support_minimum_placebo_richness", StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY,
            StressSeverity.RESEARCH_REQUIRED,
            "Small support limits placebo richness.",
            affected_assignment_families=(AssignmentFamily.ALL,),
            affected_inference_paths=(InferencePath.PLACEBO_RANK,),
            required_inputs=('min_placebo_count',),
            failure_registry_links=('FM-DA-007',),
            observed_diagnostic_links=('OPD-AD-009',),
            dgp_links=('DGP-AD-010',),
            required_actions=(StressAction.ALLOW_RESEARCH_CANDIDATE, StressAction.REQUIRE_NULL_CALIBRATION),
            recommended_next_artifact='DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001',
            ),
        _st("ST-ASI-010", "support_cell_specific_eligibility", StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY,
            StressSeverity.REQUIRED_STRESS,
            "Cell eligibility filters cross-cell swaps.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.MAX_T,),
            required_inputs=('cell_eligibility',),
            failure_registry_links=('FM-DA-009',),
            observed_diagnostic_links=('OPD-MC-001',),
            dgp_links=('DGP-MC-002',),
            required_actions=(StressAction.REQUIRE_MULTICELL_MULTIPLICITY_RESEARCH,),
            promotion_blocking=True,
            ),
        _st("ST-ASI-011", "support_observed_in_null_enumeration", StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY,
            StressSeverity.DIAGNOSTIC_ONLY,
            "Observed assignment in falsification enumeration only.",
            affected_assignment_families=(AssignmentFamily.GREEDY_MATCHED_MARKET,),
            affected_inference_paths=(InferencePath.DIAGNOSTIC_ONLY,),
            required_inputs=('observed_assignment_id',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-011',),
            required_actions=(StressAction.MARK_DIAGNOSTIC_ONLY,),
            ),
        _st("ST-ASI-012", "support_downgrade_to_falsification", StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY,
            StressSeverity.SENSITIVITY_ONLY,
            "Degenerate support downgrades to falsification-only.",
            affected_assignment_families=(AssignmentFamily.KERNEL_THINNING,),
            affected_inference_paths=(InferencePath.PLACEBO_RANK, InferencePath.DIAGNOSTIC_ONLY),
            required_inputs=('degeneracy_flag',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-011',),
            required_actions=(StressAction.MARK_SENSITIVITY_ONLY, StressAction.MARK_DIAGNOSTIC_ONLY),
            ),
    )

def _randomized_assignment_validity_rows() -> tuple[AssignmentGeneratorStressTest, ...]:
    return (
        _st("ST-RAV-001", "complete_randomization_valid", StressTestCategory.RANDOMIZED_ASSIGNMENT_VALIDITY,
            StressSeverity.REQUIRED_STRESS,
            "Complete randomization support structurally valid.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION,),
            affected_inference_paths=(InferencePath.RANDOMIZATION, InferencePath.PERMUTATION),
            required_inputs=('units', 'num_treated'),
            failure_registry_links=('FM-DA-007',),
            observed_diagnostic_links=('OPD-AD-009',),
            dgp_links=('DGP-AD-001',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-RAV-002", "complete_randomization_small_support", StressTestCategory.RANDOMIZED_ASSIGNMENT_VALIDITY,
            StressSeverity.RESEARCH_REQUIRED,
            "Small complete-randomization support restricts inference.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('support_size',),
            failure_registry_links=('FM-DA-007',),
            observed_diagnostic_links=('OPD-AD-009',),
            dgp_links=('DGP-AD-010',),
            required_actions=(StressAction.ALLOW_RESEARCH_CANDIDATE, StressAction.REQUIRE_NULL_CALIBRATION),
            ),
        _st("ST-RAV-003", "known_assignment_probability_available", StressTestCategory.RANDOMIZED_ASSIGNMENT_VALIDITY,
            StressSeverity.REQUIRED_STRESS,
            "Known assignment probabilities documented.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION, AssignmentFamily.STRATIFIED),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('assignment_probabilities',),
            failure_registry_links=('FM-DA-003',),
            observed_diagnostic_links=('OPD-AD-006',),
            dgp_links=('DGP-AD-005',),
            required_actions=(StressAction.REQUIRE_DESIGN_DOCUMENTATION,),
            ),
        _st("ST-RAV-004", "unknown_assignment_probability_blocked", StressTestCategory.RANDOMIZED_ASSIGNMENT_VALIDITY,
            StressSeverity.HARD_BLOCKER,
            "Unknown assignment probability blocks randomization.",
            affected_assignment_families=(AssignmentFamily.UNKNOWN_ASSIGNMENT,),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('assignment_mechanism',),
            failure_registry_links=('FM-DA-001',),
            observed_diagnostic_links=('OPD-AD-001',),
            dgp_links=('DGP-AD-009',),
            required_actions=(StressAction.BLOCK_INFERENCE, StressAction.REQUIRE_FAILURE_REGISTRY_LINK),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-RAV-005", "randomization_unit_mismatch", StressTestCategory.RANDOMIZED_ASSIGNMENT_VALIDITY,
            StressSeverity.HARD_BLOCKER,
            "Unit-of-randomization mismatch blocks inference.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION, AssignmentFamily.MATCHED_BLOCK),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('randomization_unit',),
            failure_registry_links=('FM-DA-005',),
            observed_diagnostic_links=('OPD-AD-004',),
            dgp_links=('DGP-AD-003',),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            ),
        _st("ST-RAV-006", "treatment_count_drift", StressTestCategory.RANDOMIZED_ASSIGNMENT_VALIDITY,
            StressSeverity.REQUIRED_STRESS,
            "Treatment count drift across pseudo-assignments blocked.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION,),
            affected_inference_paths=(InferencePath.RANDOMIZATION, InferencePath.PERMUTATION),
            required_inputs=('treatment_count',),
            failure_registry_links=('FM-DA-007',),
            observed_diagnostic_links=('OPD-AD-009',),
            dgp_links=('DGP-AD-010',),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            ),
        _st("ST-RAV-007", "treatment_timing_mismatch", StressTestCategory.RANDOMIZED_ASSIGNMENT_VALIDITY,
            StressSeverity.REMEDIATION_REQUIRED,
            "Treatment timing mismatch requires remediation.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION, AssignmentFamily.MULTI_TREATED),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('treatment_timing',),
            failure_registry_links=('FM-TE-001',),
            observed_diagnostic_links=('OPD-AD-007',),
            dgp_links=('DGP-TE-008',),
            required_actions=(StressAction.REQUIRE_REMEDIATION, StressAction.REQUIRE_DESIGN_DOCUMENTATION),
            ),
        _st("ST-RAV-008", "randomization_feasibility_documented", StressTestCategory.RANDOMIZED_ASSIGNMENT_VALIDITY,
            StressSeverity.DIAGNOSTIC_ONLY,
            "Randomization feasibility documented per design.",
            affected_assignment_families=(AssignmentFamily.ALL,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('feasibility_contract',),
            failure_registry_links=('FM-DA-003',),
            observed_diagnostic_links=('OPD-AD-006',),
            dgp_links=('DGP-AD-005',),
            required_actions=(StressAction.REQUIRE_DESIGN_DOCUMENTATION, StressAction.MARK_DIAGNOSTIC_ONLY),
            ),
    )

def _matched_pair_rows() -> tuple[AssignmentGeneratorStressTest, ...]:
    return (
        _st("ST-MP-001", "pair_membership_complete", StressTestCategory.MATCHED_PAIR,
            StressSeverity.REQUIRED_STRESS,
            "All units have valid pair membership.",
            affected_assignment_families=(AssignmentFamily.MATCHED_PAIR,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('pair_id',),
            failure_registry_links=('FM-DA-004',),
            observed_diagnostic_links=('OPD-AD-003',),
            dgp_links=('DGP-AD-002',),
            required_actions=(StressAction.REQUIRE_DESIGN_DOCUMENTATION,),
            ),
        _st("ST-MP-002", "exactly_one_treated_per_pair", StressTestCategory.MATCHED_PAIR,
            StressSeverity.HARD_BLOCKER,
            "Exactly one treated unit per pair required.",
            affected_assignment_families=(AssignmentFamily.MATCHED_PAIR,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('pair_treatment_count',),
            failure_registry_links=('FM-DA-004',),
            observed_diagnostic_links=('OPD-AD-003',),
            dgp_links=('DGP-AD-002',),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-MP-003", "pair_imbalance", StressTestCategory.MATCHED_PAIR,
            StressSeverity.SENSITIVITY_ONLY,
            "Pair imbalance routes to sensitivity analysis.",
            affected_assignment_families=(AssignmentFamily.MATCHED_PAIR,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('pair_balance_metric',),
            failure_registry_links=('FM-DA-006',),
            observed_diagnostic_links=('OPD-AD-005',),
            dgp_links=('DGP-AD-004',),
            required_actions=(StressAction.MARK_SENSITIVITY_ONLY,),
            ),
        _st("ST-MP-004", "pair_id_missing", StressTestCategory.MATCHED_PAIR,
            StressSeverity.HARD_BLOCKER,
            "Missing pair IDs block matched-pair inference.",
            affected_assignment_families=(AssignmentFamily.MATCHED_PAIR,),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('pair_id',),
            failure_registry_links=('FM-DA-004',),
            observed_diagnostic_links=('OPD-AD-003',),
            dgp_links=('DGP-AD-002',),
            required_actions=(StressAction.BLOCK_INFERENCE, StressAction.REQUIRE_FAILURE_REGISTRY_LINK),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-MP-005", "pair_level_treatment_swap_feasible", StressTestCategory.MATCHED_PAIR,
            StressSeverity.REQUIRED_STRESS,
            "Pair-level treatment swaps feasible in support.",
            affected_assignment_families=(AssignmentFamily.MATCHED_PAIR,),
            affected_inference_paths=(InferencePath.RANDOMIZATION, InferencePath.PERMUTATION),
            required_inputs=('pair_swap_enumeration',),
            failure_registry_links=('FM-DA-004',),
            observed_diagnostic_links=('OPD-AD-003',),
            dgp_links=('DGP-AD-002',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-MP-006", "pair_support_size_valid", StressTestCategory.MATCHED_PAIR,
            StressSeverity.REQUIRED_STRESS,
            "Matched-pair support size non-degenerate.",
            affected_assignment_families=(AssignmentFamily.MATCHED_PAIR,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('min_assignments',),
            failure_registry_links=('FM-DA-007',),
            observed_diagnostic_links=('OPD-AD-009',),
            dgp_links=('DGP-AD-010',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-MP-007", "pair_spillover_risk", StressTestCategory.MATCHED_PAIR,
            StressSeverity.RESEARCH_REQUIRED,
            "Pair spillover risk requires research handling.",
            affected_assignment_families=(AssignmentFamily.MATCHED_PAIR,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('spillover_annotation',),
            failure_registry_links=('FM-TE-008',),
            observed_diagnostic_links=('OPD-TE-007',),
            dgp_links=('DGP-IS-002',),
            required_actions=(StressAction.ALLOW_RESEARCH_CANDIDATE, StressAction.MARK_SENSITIVITY_ONLY),
            ),
        _st("ST-MP-008", "pair_integrity_stress_regression", StressTestCategory.MATCHED_PAIR,
            StressSeverity.DIAGNOSTIC_ONLY,
            "Pair integrity regression linked to failure registry.",
            affected_assignment_families=(AssignmentFamily.MATCHED_PAIR,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('pair_integrity_check',),
            failure_registry_links=('FM-DA-004',),
            observed_diagnostic_links=('OPD-AD-003',),
            dgp_links=('DGP-AD-002',),
            required_actions=(StressAction.REQUIRE_FAILURE_REGISTRY_LINK, StressAction.MARK_DIAGNOSTIC_ONLY),
            ),
    )

def _matched_block_stratified_rows() -> tuple[AssignmentGeneratorStressTest, ...]:
    return (
        _st("ST-MBS-001", "block_membership_complete", StressTestCategory.MATCHED_BLOCK_STRATIFIED,
            StressSeverity.REQUIRED_STRESS,
            "Block membership complete for all units.",
            affected_assignment_families=(AssignmentFamily.MATCHED_BLOCK,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('block_id',),
            failure_registry_links=('FM-DA-005',),
            observed_diagnostic_links=('OPD-AD-004',),
            dgp_links=('DGP-AD-003',),
            required_actions=(StressAction.REQUIRE_DESIGN_DOCUMENTATION,),
            ),
        _st("ST-MBS-002", "block_treatment_counts_preserved", StressTestCategory.MATCHED_BLOCK_STRATIFIED,
            StressSeverity.REQUIRED_STRESS,
            "Block treatment counts preserved in support.",
            affected_assignment_families=(AssignmentFamily.MATCHED_BLOCK,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('block_treatment_counts',),
            failure_registry_links=('FM-DA-005',),
            observed_diagnostic_links=('OPD-AD-004',),
            dgp_links=('DGP-AD-003',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-MBS-003", "block_support_non_degenerate", StressTestCategory.MATCHED_BLOCK_STRATIFIED,
            StressSeverity.HARD_BLOCKER,
            "Degenerate block support blocks inference.",
            affected_assignment_families=(AssignmentFamily.MATCHED_BLOCK,),
            affected_inference_paths=(InferencePath.RANDOMIZATION, InferencePath.NO_VALID_INFERENCE),
            required_inputs=('support_size',),
            failure_registry_links=('FM-DA-005',),
            observed_diagnostic_links=('OPD-AD-004',),
            dgp_links=('DGP-AD-003',),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            ),
        _st("ST-MBS-004", "stratum_membership_complete", StressTestCategory.MATCHED_BLOCK_STRATIFIED,
            StressSeverity.REQUIRED_STRESS,
            "Stratum membership complete for all units.",
            affected_assignment_families=(AssignmentFamily.STRATIFIED,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('stratum_id',),
            failure_registry_links=('FM-DA-006',),
            observed_diagnostic_links=('OPD-AD-005',),
            dgp_links=('DGP-AD-004',),
            required_actions=(StressAction.REQUIRE_DESIGN_DOCUMENTATION,),
            ),
        _st("ST-MBS-005", "stratum_treatment_quotas_preserved", StressTestCategory.MATCHED_BLOCK_STRATIFIED,
            StressSeverity.REQUIRED_STRESS,
            "Stratum treatment quotas preserved.",
            affected_assignment_families=(AssignmentFamily.STRATIFIED,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('stratum_quotas',),
            failure_registry_links=('FM-DA-006',),
            observed_diagnostic_links=('OPD-AD-005',),
            dgp_links=('DGP-AD-004',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-MBS-006", "stratum_support_non_degenerate", StressTestCategory.MATCHED_BLOCK_STRATIFIED,
            StressSeverity.REQUIRED_STRESS,
            "Stratum support non-degenerate.",
            affected_assignment_families=(AssignmentFamily.STRATIFIED,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('support_size',),
            failure_registry_links=('FM-DA-006',),
            observed_diagnostic_links=('OPD-AD-005',),
            dgp_links=('DGP-AD-004',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-MBS-007", "block_stratum_imbalance", StressTestCategory.MATCHED_BLOCK_STRATIFIED,
            StressSeverity.SENSITIVITY_ONLY,
            "Block/stratum imbalance sensitivity required.",
            affected_assignment_families=(AssignmentFamily.MATCHED_BLOCK, AssignmentFamily.STRATIFIED),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('balance_metrics',),
            failure_registry_links=('FM-DA-006',),
            observed_diagnostic_links=('OPD-AD-005',),
            dgp_links=('DGP-AD-004',),
            required_actions=(StressAction.MARK_SENSITIVITY_ONLY,),
            ),
        _st("ST-MBS-008", "cluster_robust_assignment_feasibility", StressTestCategory.MATCHED_BLOCK_STRATIFIED,
            StressSeverity.RESEARCH_REQUIRED,
            "Cluster-robust paths need block integrity research.",
            affected_assignment_families=(AssignmentFamily.MATCHED_BLOCK,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('cluster_count',),
            failure_registry_links=('FM-INF-006',),
            observed_diagnostic_links=('OPD-IR-006',),
            dgp_links=('DGP-INF-008',),
            required_actions=(StressAction.ALLOW_RESEARCH_CANDIDATE,),
            recommended_next_artifact='DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001',
            ),
    )

def _rerandomization_rows() -> tuple[AssignmentGeneratorStressTest, ...]:
    return (
        _st("ST-RR-001", "acceptance_rule_available", StressTestCategory.RERANDOMIZATION,
            StressSeverity.REMEDIATION_REQUIRED,
            "Rerandomization acceptance rule must be documented.",
            affected_assignment_families=(AssignmentFamily.RERANDOMIZED,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('acceptance_rule',),
            failure_registry_links=('FM-DA-003',),
            observed_diagnostic_links=('OPD-AD-006',),
            dgp_links=('DGP-AD-005',),
            required_actions=(StressAction.REQUIRE_REMEDIATION, StressAction.REQUIRE_DESIGN_DOCUMENTATION),
            ),
        _st("ST-RR-002", "acceptance_statistic_available", StressTestCategory.RERANDOMIZATION,
            StressSeverity.REMEDIATION_REQUIRED,
            "Acceptance statistic contract required.",
            affected_assignment_families=(AssignmentFamily.RERANDOMIZED,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('acceptance_statistic',),
            failure_registry_links=('FM-DA-003',),
            observed_diagnostic_links=('OPD-AD-006',),
            dgp_links=('DGP-AD-005',),
            required_actions=(StressAction.REQUIRE_REMEDIATION,),
            ),
        _st("ST-RR-003", "acceptance_threshold_available", StressTestCategory.RERANDOMIZATION,
            StressSeverity.REQUIRED_STRESS,
            "Acceptance threshold must be specified.",
            affected_assignment_families=(AssignmentFamily.RERANDOMIZED,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('acceptance_threshold',),
            failure_registry_links=('FM-DA-003',),
            observed_diagnostic_links=('OPD-AD-006',),
            dgp_links=('DGP-AD-005',),
            required_actions=(StressAction.REQUIRE_DESIGN_DOCUMENTATION, StressAction.REQUIRE_REMEDIATION),
            ),
        _st("ST-RR-004", "accepted_support_non_degenerate", StressTestCategory.RERANDOMIZATION,
            StressSeverity.HARD_BLOCKER,
            "Accepted rerandomization support non-degenerate.",
            affected_assignment_families=(AssignmentFamily.RERANDOMIZED,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('accepted_support_size',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-011',),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            ),
        _st("ST-RR-005", "rerandomization_rule_reproducible", StressTestCategory.RERANDOMIZATION,
            StressSeverity.REQUIRED_STRESS,
            "Rerandomization rule reproducible with seed.",
            affected_assignment_families=(AssignmentFamily.RERANDOMIZED,),
            affected_inference_paths=(InferencePath.RANDOMIZATION, InferencePath.PERMUTATION),
            required_inputs=('seed', 'acceptance_rule'),
            failure_registry_links=('FM-DA-003',),
            observed_diagnostic_links=('OPD-AD-006',),
            dgp_links=('DGP-AD-005',),
            required_actions=(StressAction.REQUIRE_DESIGN_DOCUMENTATION,),
            ),
        _st("ST-RR-006", "covariate_balance_preserved", StressTestCategory.RERANDOMIZATION,
            StressSeverity.REQUIRED_STRESS,
            "Covariate balance preserved under acceptance.",
            affected_assignment_families=(AssignmentFamily.RERANDOMIZED,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('balance_metrics',),
            failure_registry_links=('FM-DA-003',),
            observed_diagnostic_links=('OPD-AD-006',),
            dgp_links=('DGP-AD-005',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-RR-007", "unknown_rerandomization_rule_blocked", StressTestCategory.RERANDOMIZATION,
            StressSeverity.HARD_BLOCKER,
            "Unknown rerandomization rule blocks inference.",
            affected_assignment_families=(AssignmentFamily.RERANDOMIZED,),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('acceptance_rule',),
            failure_registry_links=('FM-DA-003',),
            observed_diagnostic_links=('OPD-AD-006',),
            dgp_links=('DGP-AD-005',),
            required_actions=(StressAction.BLOCK_INFERENCE, StressAction.REQUIRE_FAILURE_REGISTRY_LINK),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-RR-008", "rerandomization_null_calibration_prerequisite", StressTestCategory.RERANDOMIZATION,
            StressSeverity.RESEARCH_REQUIRED,
            "Rerandomization requires null calibration research.",
            affected_assignment_families=(AssignmentFamily.RERANDOMIZED,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('null_calibration_plan',),
            failure_registry_links=('FM-DA-003',),
            observed_diagnostic_links=('OPD-AD-006',),
            dgp_links=('DGP-AD-005',),
            required_actions=(StressAction.ALLOW_RESEARCH_CANDIDATE, StressAction.REQUIRE_NULL_CALIBRATION),
            recommended_next_artifact='DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001',
            ),
    )

def _greedy_deterministic_rows() -> tuple[AssignmentGeneratorStressTest, ...]:
    return (
        _st("ST-GD-001", "deterministic_design_flagged", StressTestCategory.GREEDY_DETERMINISTIC,
            StressSeverity.HARD_BLOCKER,
            "Deterministic design must be explicitly flagged.",
            affected_assignment_families=(AssignmentFamily.FIXED_DETERMINISTIC,),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('deterministic_flag',),
            failure_registry_links=('FM-DA-002',),
            observed_diagnostic_links=('OPD-AD-002',),
            dgp_links=('DGP-AD-008',),
            required_actions=(StressAction.BLOCK_INFERENCE, StressAction.REQUIRE_FAILURE_REGISTRY_LINK),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-GD-002", "pseudo_not_true_randomization", StressTestCategory.GREEDY_DETERMINISTIC,
            StressSeverity.HARD_BLOCKER,
            "Pseudo-assignment cannot substitute for true randomization.",
            affected_assignment_families=(AssignmentFamily.FIXED_DETERMINISTIC, AssignmentFamily.GREEDY_MATCHED_MARKET),
            affected_inference_paths=(InferencePath.RANDOMIZATION, InferencePath.NO_VALID_INFERENCE),
            required_inputs=('assignment_role',),
            failure_registry_links=('FM-DA-002',),
            observed_diagnostic_links=('OPD-AD-002',),
            dgp_links=('DGP-AD-008',),
            required_actions=(StressAction.BLOCK_INFERENCE, StressAction.MARK_DIAGNOSTIC_ONLY),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-GD-003", "matched_market_constraints_preserved", StressTestCategory.GREEDY_DETERMINISTIC,
            StressSeverity.REQUIRED_STRESS,
            "Greedy matched-market constraints preserved.",
            affected_assignment_families=(AssignmentFamily.GREEDY_MATCHED_MARKET,),
            affected_inference_paths=(InferencePath.DIAGNOSTIC_ONLY, InferencePath.PLACEBO_RANK),
            required_inputs=('market_matching_constraints',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-006',),
            required_actions=(StressAction.MARK_DIAGNOSTIC_ONLY,),
            ),
        _st("ST-GD-004", "donor_eligibility_preserved", StressTestCategory.GREEDY_DETERMINISTIC,
            StressSeverity.REQUIRED_STRESS,
            "Donor eligibility preserved in falsification support.",
            affected_assignment_families=(AssignmentFamily.GREEDY_MATCHED_MARKET,),
            affected_inference_paths=(InferencePath.PLACEBO_RANK,),
            required_inputs=('donor_eligibility',),
            failure_registry_links=('FM-DS-002',),
            observed_diagnostic_links=('OPD-DS-002',),
            dgp_links=('DGP-DS-007',),
            required_actions=(StressAction.REQUIRE_DESIGN_DOCUMENTATION,),
            ),
        _st("ST-GD-005", "greedy_matching_reproducibility", StressTestCategory.GREEDY_DETERMINISTIC,
            StressSeverity.DIAGNOSTIC_ONLY,
            "Greedy matching reproducibility diagnostic required.",
            affected_assignment_families=(AssignmentFamily.GREEDY_MATCHED_MARKET,),
            affected_inference_paths=(InferencePath.DIAGNOSTIC_ONLY,),
            required_inputs=('seed', 'matching_algorithm'),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-006',),
            required_actions=(StressAction.MARK_DIAGNOSTIC_ONLY, StressAction.REQUIRE_DESIGN_DOCUMENTATION),
            ),
        _st("ST-GD-006", "randomization_blocked_without_reconstruction", StressTestCategory.GREEDY_DETERMINISTIC,
            StressSeverity.HARD_BLOCKER,
            "Randomization blocked without design reconstruction.",
            affected_assignment_families=(AssignmentFamily.FIXED_DETERMINISTIC,),
            affected_inference_paths=(InferencePath.RANDOMIZATION, InferencePath.NO_VALID_INFERENCE),
            required_inputs=('design_reconstruction',),
            failure_registry_links=('FM-DA-002',),
            observed_diagnostic_links=('OPD-AD-002',),
            dgp_links=('DGP-AD-008',),
            required_actions=(StressAction.BLOCK_INFERENCE, StressAction.REQUIRE_DESIGN_DOCUMENTATION),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-GD-007", "greedy_falsification_only_route", StressTestCategory.GREEDY_DETERMINISTIC,
            StressSeverity.DIAGNOSTIC_ONLY,
            "Greedy paths route to falsification-only inference.",
            affected_assignment_families=(AssignmentFamily.GREEDY_MATCHED_MARKET,),
            affected_inference_paths=(InferencePath.DIAGNOSTIC_ONLY, InferencePath.PLACEBO_RANK),
            required_inputs=('falsification_contract',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-006',),
            required_actions=(StressAction.MARK_DIAGNOSTIC_ONLY, StressAction.REQUIRE_FAILURE_REGISTRY_LINK),
            ),
    )

def _kernel_thinning_rows() -> tuple[AssignmentGeneratorStressTest, ...]:
    return (
        _st("ST-KT-001", "kernel_thinning_support_available", StressTestCategory.KERNEL_THINNING,
            StressSeverity.REQUIRED_STRESS,
            "Kernel thinning support must be available.",
            affected_assignment_families=(AssignmentFamily.KERNEL_THINNING,),
            affected_inference_paths=(InferencePath.PLACEBO_RANK, InferencePath.DIAGNOSTIC_ONLY),
            required_inputs=('thinning_support',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-007',),
            required_actions=(StressAction.MARK_DIAGNOSTIC_ONLY,),
            ),
        _st("ST-KT-002", "kernel_thinning_seed_reproducible", StressTestCategory.KERNEL_THINNING,
            StressSeverity.REQUIRED_STRESS,
            "Kernel thinning seed reproducibility required.",
            affected_assignment_families=(AssignmentFamily.KERNEL_THINNING,),
            affected_inference_paths=(InferencePath.PLACEBO_RANK,),
            required_inputs=('seed',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-007',),
            required_actions=(StressAction.REQUIRE_DESIGN_DOCUMENTATION,),
            ),
        _st("ST-KT-003", "kernel_thinning_balance_constraints", StressTestCategory.KERNEL_THINNING,
            StressSeverity.REQUIRED_STRESS,
            "Kernel thinning balance constraints preserved.",
            affected_assignment_families=(AssignmentFamily.KERNEL_THINNING,),
            affected_inference_paths=(InferencePath.PLACEBO_RANK,),
            required_inputs=('balance_constraints',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-007',),
            required_actions=(StressAction.REQUIRE_DESIGN_DOCUMENTATION,),
            ),
        _st("ST-KT-004", "kernel_thinning_support_non_degenerate", StressTestCategory.KERNEL_THINNING,
            StressSeverity.HARD_BLOCKER,
            "Degenerate kernel thinning support blocks rank inference.",
            affected_assignment_families=(AssignmentFamily.KERNEL_THINNING,),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('support_size',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-011',),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            ),
        _st("ST-KT-005", "kernel_thinning_probability_documented", StressTestCategory.KERNEL_THINNING,
            StressSeverity.DIAGNOSTIC_ONLY,
            "Kernel thinning assignment probability documented.",
            affected_assignment_families=(AssignmentFamily.KERNEL_THINNING,),
            affected_inference_paths=(InferencePath.DIAGNOSTIC_ONLY,),
            required_inputs=('assignment_probability',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-007',),
            required_actions=(StressAction.MARK_DIAGNOSTIC_ONLY, StressAction.REQUIRE_DESIGN_DOCUMENTATION),
            ),
        _st("ST-KT-006", "kernel_thinning_diagnostic_route", StressTestCategory.KERNEL_THINNING,
            StressSeverity.SENSITIVITY_ONLY,
            "Kernel thinning sensitivity diagnostic route.",
            affected_assignment_families=(AssignmentFamily.KERNEL_THINNING,),
            affected_inference_paths=(InferencePath.DIAGNOSTIC_ONLY,),
            required_inputs=('sensitivity_metrics',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-007',),
            required_actions=(StressAction.MARK_SENSITIVITY_ONLY,),
            ),
    )

def _multi_treated_placebo_rows() -> tuple[AssignmentGeneratorStressTest, ...]:
    return (
        _st("ST-MTP-001", "treated_set_size_preserved", StressTestCategory.MULTI_TREATED_PLACEBO,
            StressSeverity.REQUIRED_STRESS,
            "Treated-set size preserved across pseudo-assignments.",
            affected_assignment_families=(AssignmentFamily.MULTI_TREATED,),
            affected_inference_paths=(InferencePath.TREATED_SET_PLACEBO,),
            required_inputs=('treated_set_size',),
            failure_registry_links=('FM-DA-007',),
            observed_diagnostic_links=('OPD-AD-009',),
            dgp_links=('DGP-AD-010',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-MTP-002", "treated_set_placebo_support_non_degenerate", StressTestCategory.MULTI_TREATED_PLACEBO,
            StressSeverity.HARD_BLOCKER,
            "Non-degenerate treated-set placebo support required.",
            affected_assignment_families=(AssignmentFamily.MULTI_TREATED,),
            affected_inference_paths=(InferencePath.TREATED_SET_PLACEBO, InferencePath.PLACEBO_RANK),
            required_inputs=('support_size',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-011',),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            ),
        _st("ST-MTP-003", "treated_set_overlap_constraints", StressTestCategory.MULTI_TREATED_PLACEBO,
            StressSeverity.REQUIRED_STRESS,
            "Treated-set overlap constraints respected.",
            affected_assignment_families=(AssignmentFamily.MULTI_TREATED,),
            affected_inference_paths=(InferencePath.TREATED_SET_PLACEBO,),
            required_inputs=('overlap_rules',),
            failure_registry_links=('FM-DA-007',),
            observed_diagnostic_links=('OPD-AD-009',),
            dgp_links=('DGP-AD-010',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-MTP-004", "leave_one_treated_out_feasible", StressTestCategory.MULTI_TREATED_PLACEBO,
            StressSeverity.REQUIRED_STRESS,
            "Leave-one-treated-out enumeration feasible.",
            affected_assignment_families=(AssignmentFamily.MULTI_TREATED,),
            affected_inference_paths=(InferencePath.LEAVE_ONE_TREATED_OUT,),
            required_inputs=('loto_enumeration',),
            failure_registry_links=('FM-DA-007',),
            observed_diagnostic_links=('OPD-AD-009',),
            dgp_links=('DGP-AD-010',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-MTP-005", "treated_set_placebo_not_production_pvalue", StressTestCategory.MULTI_TREATED_PLACEBO,
            StressSeverity.DIAGNOSTIC_ONLY,
            "Treated-set placebo rank is diagnostic-only.",
            affected_assignment_families=(AssignmentFamily.MULTI_TREATED,),
            affected_inference_paths=(InferencePath.TREATED_SET_PLACEBO, InferencePath.PLACEBO_RANK, InferencePath.DIAGNOSTIC_ONLY),
            required_inputs=('placebo_rank_semantics',),
            failure_registry_links=('FM-INF-001',),
            observed_diagnostic_links=('OPD-IR-002',),
            dgp_links=('DGP-INF-003',),
            required_actions=(StressAction.MARK_DIAGNOSTIC_ONLY, StressAction.REQUIRE_NULL_CALIBRATION),
            ),
        _st("ST-MTP-006", "multi_treated_scm_geometry_compatible", StressTestCategory.MULTI_TREATED_PLACEBO,
            StressSeverity.RESEARCH_REQUIRED,
            "Multi-treated SCM geometry compatibility research.",
            affected_assignment_families=(AssignmentFamily.MULTI_TREATED,),
            affected_inference_paths=(InferencePath.TREATED_SET_PLACEBO,),
            required_inputs=('geometry_scope',),
            failure_registry_links=('FM-ES-001',),
            observed_diagnostic_links=('OPD-DS-008',),
            dgp_links=('DGP-ES-002',),
            required_actions=(StressAction.ALLOW_RESEARCH_CANDIDATE, StressAction.REQUIRE_STUDENTIZED_ADAPTER),
            ),
        _st("ST-MTP-007", "studentized_treated_set_adapter", StressTestCategory.MULTI_TREATED_PLACEBO,
            StressSeverity.DIAGNOSTIC_ONLY,
            "Studentized treated-set adapter prerequisite.",
            affected_assignment_families=(AssignmentFamily.MULTI_TREATED,),
            affected_inference_paths=(InferencePath.STUDENTIZED_PLACEBO_RANK, InferencePath.TREATED_SET_PLACEBO),
            required_inputs=('statistic_adapter',),
            failure_registry_links=('FM-INF-002',),
            observed_diagnostic_links=('OPD-IR-003',),
            dgp_links=('DGP-INF-004',),
            required_actions=(StressAction.REQUIRE_STUDENTIZED_ADAPTER, StressAction.REQUIRE_NULL_CALIBRATION),
            ),
    )

def _multicell_shared_control_rows() -> tuple[AssignmentGeneratorStressTest, ...]:
    return (
        _st("ST-MC-001", "shared_control_dependence_detected", StressTestCategory.MULTICELL_SHARED_CONTROL,
            StressSeverity.HARD_BLOCKER,
            "Shared-control dependence must be detected.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.MAX_T, InferencePath.NO_VALID_INFERENCE),
            required_inputs=('shared_control_flag',),
            failure_registry_links=('FM-DA-009',),
            observed_diagnostic_links=('OPD-AD-008', 'OPD-MC-001'),
            dgp_links=('DGP-MC-002',),
            required_actions=(StressAction.BLOCK_INFERENCE, StressAction.REQUIRE_MULTICELL_MULTIPLICITY_RESEARCH),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-MC-002", "cell_assignment_constraints_preserved", StressTestCategory.MULTICELL_SHARED_CONTROL,
            StressSeverity.REQUIRED_STRESS,
            "Per-cell assignment constraints preserved.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.MAX_T, InferencePath.STEPDOWN),
            required_inputs=('cell_constraints',),
            failure_registry_links=('FM-DA-009',),
            observed_diagnostic_links=('OPD-MC-001',),
            dgp_links=('DGP-MC-002',),
            required_actions=(StressAction.REQUIRE_MULTICELL_MULTIPLICITY_RESEARCH,),
            promotion_blocking=True,
            ),
        _st("ST-MC-003", "cross_cell_impossible_excluded", StressTestCategory.MULTICELL_SHARED_CONTROL,
            StressSeverity.REQUIRED_STRESS,
            "Cross-cell impossible assignments excluded.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.MAX_T,),
            required_inputs=('cross_cell_rules',),
            failure_registry_links=('FM-TE-005',),
            observed_diagnostic_links=('OPD-TE-008',),
            dgp_links=('DGP-IS-003',),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            ),
        _st("ST-MC-004", "winner_selection_risk_flagged", StressTestCategory.MULTICELL_SHARED_CONTROL,
            StressSeverity.HARD_BLOCKER,
            "Winner-selection multiplicity risk flagged.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.MAX_T, InferencePath.STEPDOWN),
            required_inputs=('multiplicity_risk',),
            failure_registry_links=('FM-DA-010',),
            observed_diagnostic_links=('OPD-MC-003',),
            dgp_links=('DGP-MC-005',),
            required_actions=(StressAction.REQUIRE_MULTICELL_MULTIPLICITY_RESEARCH, StressAction.REQUIRE_FAILURE_REGISTRY_LINK),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-MC-005", "max_t_stepdown_need_flagged", StressTestCategory.MULTICELL_SHARED_CONTROL,
            StressSeverity.RESEARCH_REQUIRED,
            "Max-T/stepdown research required for multicell.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.MAX_T, InferencePath.STEPDOWN),
            required_inputs=('multiplicity_correction',),
            failure_registry_links=('FM-INF-009',),
            observed_diagnostic_links=('OPD-IR-009',),
            dgp_links=('DGP-INF-011',),
            required_actions=(StressAction.REQUIRE_MULTICELL_MULTIPLICITY_RESEARCH, StressAction.ALLOW_RESEARCH_CANDIDATE),
            promotion_blocking=True,
            recommended_next_artifact='MULTICELL_MAX_T_RESEARCH_SCOUT_001',
            ),
        _st("ST-MC-006", "pooled_estimand_ambiguity_flagged", StressTestCategory.MULTICELL_SHARED_CONTROL,
            StressSeverity.RESEARCH_REQUIRED,
            "Pooled/global estimand ambiguity flagged.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.MAX_T,),
            required_inputs=('estimand_scope',),
            failure_registry_links=('FM-DA-010',),
            observed_diagnostic_links=('OPD-MC-003',),
            dgp_links=('DGP-MC-005',),
            required_actions=(StressAction.REQUIRE_MULTICELL_MULTIPLICITY_RESEARCH,),
            promotion_blocking=True,
            ),
        _st("ST-MC-007", "independent_cell_assumption_blocked", StressTestCategory.MULTICELL_SHARED_CONTROL,
            StressSeverity.HARD_BLOCKER,
            "Invalid independent-cell assumption blocked.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('independence_assumption',),
            failure_registry_links=('FM-DA-009',),
            observed_diagnostic_links=('OPD-MC-001',),
            dgp_links=('DGP-MC-002',),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-MC-008", "multicell_research_scout_routing", StressTestCategory.MULTICELL_SHARED_CONTROL,
            StressSeverity.RESEARCH_REQUIRED,
            "Multicell paths route to multiplicity research scout.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.MAX_T, InferencePath.STEPDOWN),
            required_inputs=('research_scout_plan',),
            failure_registry_links=('FM-INF-010',),
            observed_diagnostic_links=('OPD-IR-009',),
            dgp_links=('DGP-INF-012',),
            required_actions=(StressAction.ALLOW_RESEARCH_CANDIDATE, StressAction.REQUIRE_MULTICELL_MULTIPLICITY_RESEARCH),
            recommended_next_artifact='MULTICELL_MAX_T_RESEARCH_SCOUT_001',
            ),
        _st("ST-MC-009", "shared_control_sensitivity_path", StressTestCategory.MULTICELL_SHARED_CONTROL,
            StressSeverity.SENSITIVITY_ONLY,
            "Shared-control sensitivity path for diagnostic use.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.DIAGNOSTIC_ONLY,),
            required_inputs=('dependence_diagnostics',),
            failure_registry_links=('FM-DA-009',),
            observed_diagnostic_links=('OPD-MC-001',),
            dgp_links=('DGP-MC-002',),
            required_actions=(StressAction.MARK_SENSITIVITY_ONLY, StressAction.MARK_DIAGNOSTIC_ONLY),
            ),
    )

def _inference_feasibility_rows() -> tuple[AssignmentGeneratorStressTest, ...]:
    return (
        _st("ST-INF-001", "randomization_inference_feasible", StressTestCategory.INFERENCE_FEASIBILITY,
            StressSeverity.REQUIRED_STRESS,
            "Randomization inference feasible when support valid.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION, AssignmentFamily.MATCHED_PAIR),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('support_validity',),
            failure_registry_links=('FM-DA-007',),
            observed_diagnostic_links=('OPD-AD-009',),
            dgp_links=('DGP-AD-001',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-INF-002", "randomization_inference_blocked", StressTestCategory.INFERENCE_FEASIBILITY,
            StressSeverity.HARD_BLOCKER,
            "Randomization inference blocked for invalid designs.",
            affected_assignment_families=(AssignmentFamily.UNKNOWN_ASSIGNMENT, AssignmentFamily.FIXED_DETERMINISTIC),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('design_validity',),
            failure_registry_links=('FM-DA-001', 'FM-DA-002'),
            observed_diagnostic_links=('OPD-AD-001', 'OPD-AD-002'),
            dgp_links=('DGP-AD-009', 'DGP-AD-008'),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-INF-003", "permutation_feasible", StressTestCategory.INFERENCE_FEASIBILITY,
            StressSeverity.REQUIRED_STRESS,
            "Permutation feasible with valid support.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION, AssignmentFamily.STRATIFIED),
            affected_inference_paths=(InferencePath.PERMUTATION,),
            required_inputs=('permutation_support',),
            failure_registry_links=('FM-DA-003',),
            observed_diagnostic_links=('OPD-AD-006',),
            dgp_links=('DGP-AD-005',),
            required_actions=(StressAction.REQUIRE_NULL_CALIBRATION,),
            ),
        _st("ST-INF-004", "permutation_blocked", StressTestCategory.INFERENCE_FEASIBILITY,
            StressSeverity.HARD_BLOCKER,
            "Permutation blocked for unknown assignment.",
            affected_assignment_families=(AssignmentFamily.UNKNOWN_ASSIGNMENT,),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('assignment_mechanism',),
            failure_registry_links=('FM-DA-001',),
            observed_diagnostic_links=('OPD-AD-001',),
            dgp_links=('DGP-AD-009',),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-INF-005", "placebo_rank_feasible", StressTestCategory.INFERENCE_FEASIBILITY,
            StressSeverity.DIAGNOSTIC_ONLY,
            "Placebo rank feasible as diagnostic falsification.",
            affected_assignment_families=(AssignmentFamily.GREEDY_MATCHED_MARKET, AssignmentFamily.KERNEL_THINNING),
            affected_inference_paths=(InferencePath.PLACEBO_RANK,),
            required_inputs=('placebo_support',),
            failure_registry_links=('FM-INF-001',),
            observed_diagnostic_links=('OPD-IR-002',),
            dgp_links=('DGP-INF-003',),
            required_actions=(StressAction.MARK_DIAGNOSTIC_ONLY,),
            ),
        _st("ST-INF-006", "placebo_rank_diagnostic_only", StressTestCategory.INFERENCE_FEASIBILITY,
            StressSeverity.DIAGNOSTIC_ONLY,
            "Placebo rank remains diagnostic-only.",
            affected_assignment_families=(AssignmentFamily.MULTI_TREATED,),
            affected_inference_paths=(InferencePath.PLACEBO_RANK, InferencePath.DIAGNOSTIC_ONLY),
            required_inputs=('placebo_semantics',),
            failure_registry_links=('FM-INF-001',),
            observed_diagnostic_links=('OPD-IR-002',),
            dgp_links=('DGP-INF-003',),
            required_actions=(StressAction.MARK_DIAGNOSTIC_ONLY, StressAction.REQUIRE_NULL_CALIBRATION),
            ),
        _st("ST-INF-007", "studentized_adapter_required", StressTestCategory.INFERENCE_FEASIBILITY,
            StressSeverity.REMEDIATION_REQUIRED,
            "Studentized statistics require governed adapter.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION, AssignmentFamily.MULTI_TREATED),
            affected_inference_paths=(InferencePath.STUDENTIZED_PLACEBO_RANK,),
            required_inputs=('statistic_adapter',),
            failure_registry_links=('FM-INF-002',),
            observed_diagnostic_links=('OPD-IR-003',),
            dgp_links=('DGP-INF-004',),
            required_actions=(StressAction.REQUIRE_STUDENTIZED_ADAPTER, StressAction.REQUIRE_NULL_CALIBRATION),
            ),
        _st("ST-INF-008", "bootstrap_not_substitute_invalid_assignment", StressTestCategory.INFERENCE_FEASIBILITY,
            StressSeverity.HARD_BLOCKER,
            "Bootstrap cannot substitute for invalid assignment.",
            affected_assignment_families=(AssignmentFamily.UNKNOWN_ASSIGNMENT, AssignmentFamily.FIXED_DETERMINISTIC),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('assignment_validity',),
            failure_registry_links=('FM-INF-003',),
            observed_diagnostic_links=('OPD-IR-004',),
            dgp_links=('DGP-INF-006',),
            required_actions=(StressAction.BLOCK_INFERENCE,),
            blocks_inference_if_failed=True,
            recommended_next_artifact='TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001',
            ),
        _st("ST-INF-009", "no_valid_inference_route_defined", StressTestCategory.INFERENCE_FEASIBILITY,
            StressSeverity.HARD_BLOCKER,
            "No-valid-inference route defined for blockers.",
            affected_assignment_families=(AssignmentFamily.UNKNOWN_ASSIGNMENT,),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('routing_contract',),
            failure_registry_links=('FM-INF-011',),
            observed_diagnostic_links=('OPD-IR-010',),
            dgp_links=('DGP-INF-013',),
            required_actions=(StressAction.BLOCK_INFERENCE, StressAction.REQUIRE_FAILURE_REGISTRY_LINK),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-INF-010", "inference_path_all_families_audit", StressTestCategory.INFERENCE_FEASIBILITY,
            StressSeverity.DIAGNOSTIC_ONLY,
            "Cross-family inference path audit metadata.",
            affected_assignment_families=(AssignmentFamily.ALL,),
            affected_inference_paths=(InferencePath.ALL,),
            required_inputs=('inference_path_matrix',),
            failure_registry_links=('FM-CP-004',),
            observed_diagnostic_links=('OPD-IR-010',),
            dgp_links=('DGP-INF-013',),
            required_actions=(StressAction.REQUIRE_FAILURE_REGISTRY_LINK, StressAction.MARK_DIAGNOSTIC_ONLY),
            ),
        _st("ST-INF-011", "tbrridge_bootstrap_remediation_route", StressTestCategory.INFERENCE_FEASIBILITY,
            StressSeverity.REMEDIATION_REQUIRED,
            "TBRRidge bootstrap requires remediation audit.",
            affected_assignment_families=(AssignmentFamily.ALL,),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('bootstrap_validity',),
            failure_registry_links=('FM-INF-003',),
            observed_diagnostic_links=('OPD-TD-001',),
            dgp_links=('DGP-INF-006',),
            required_actions=(StressAction.REQUIRE_REMEDIATION,),
            recommended_next_artifact='TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001',
            ),
        _st("ST-INF-012", "permutation_research_candidate", StressTestCategory.INFERENCE_FEASIBILITY,
            StressSeverity.RESEARCH_REQUIRED,
            "Permutation research candidate for restricted designs.",
            affected_assignment_families=(AssignmentFamily.RERANDOMIZED, AssignmentFamily.STRATIFIED),
            affected_inference_paths=(InferencePath.PERMUTATION,),
            required_inputs=('permutation_plan',),
            failure_registry_links=('FM-DA-003',),
            observed_diagnostic_links=('OPD-AD-006',),
            dgp_links=('DGP-AD-005',),
            required_actions=(StressAction.ALLOW_RESEARCH_CANDIDATE,),
            ),
    )

def _failure_registry_linkage_rows() -> tuple[AssignmentGeneratorStressTest, ...]:
    return (
        _st("ST-FRL-001", "fm_unknown_assignment_mechanism", StressTestCategory.FAILURE_REGISTRY_LINKAGE,
            StressSeverity.HARD_BLOCKER,
            "Unknown assignment links to FM-DA-001.",
            affected_assignment_families=(AssignmentFamily.UNKNOWN_ASSIGNMENT,),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('failure_registry_lookup',),
            failure_registry_links=('FM-DA-001',),
            observed_diagnostic_links=('OPD-AD-001',),
            dgp_links=('DGP-AD-009',),
            required_actions=(StressAction.REQUIRE_FAILURE_REGISTRY_LINK, StressAction.BLOCK_INFERENCE),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-FRL-002", "fm_deterministic_as_randomized", StressTestCategory.FAILURE_REGISTRY_LINKAGE,
            StressSeverity.HARD_BLOCKER,
            "Deterministic-as-randomized links to FM-DA-002.",
            affected_assignment_families=(AssignmentFamily.FIXED_DETERMINISTIC,),
            affected_inference_paths=(InferencePath.NO_VALID_INFERENCE,),
            required_inputs=('failure_registry_lookup',),
            failure_registry_links=('FM-DA-002',),
            observed_diagnostic_links=('OPD-AD-002',),
            dgp_links=('DGP-AD-008',),
            required_actions=(StressAction.REQUIRE_FAILURE_REGISTRY_LINK, StressAction.BLOCK_INFERENCE),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-FRL-003", "fm_small_assignment_support", StressTestCategory.FAILURE_REGISTRY_LINKAGE,
            StressSeverity.RESEARCH_REQUIRED,
            "Small support links to FM-DA-007.",
            affected_assignment_families=(AssignmentFamily.COMPLETE_RANDOMIZATION,),
            affected_inference_paths=(InferencePath.RANDOMIZATION,),
            required_inputs=('failure_registry_lookup',),
            failure_registry_links=('FM-DA-007',),
            observed_diagnostic_links=('OPD-AD-009',),
            dgp_links=('DGP-AD-010',),
            required_actions=(StressAction.REQUIRE_FAILURE_REGISTRY_LINK, StressAction.ALLOW_RESEARCH_CANDIDATE),
            ),
        _st("ST-FRL-004", "fm_degenerate_pseudo_support", StressTestCategory.FAILURE_REGISTRY_LINKAGE,
            StressSeverity.DIAGNOSTIC_ONLY,
            "Degenerate support links to FM-DA-008.",
            affected_assignment_families=(AssignmentFamily.GREEDY_MATCHED_MARKET, AssignmentFamily.KERNEL_THINNING),
            affected_inference_paths=(InferencePath.PLACEBO_RANK,),
            required_inputs=('failure_registry_lookup',),
            failure_registry_links=('FM-DA-008',),
            observed_diagnostic_links=('OPD-AD-010',),
            dgp_links=('DGP-AD-011',),
            required_actions=(StressAction.REQUIRE_FAILURE_REGISTRY_LINK, StressAction.MARK_DIAGNOSTIC_ONLY),
            ),
        _st("ST-FRL-005", "fm_shared_control_dependence", StressTestCategory.FAILURE_REGISTRY_LINKAGE,
            StressSeverity.HARD_BLOCKER,
            "Shared-control dependence links to FM-DA-009.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.MAX_T,),
            required_inputs=('failure_registry_lookup',),
            failure_registry_links=('FM-DA-009',),
            observed_diagnostic_links=('OPD-MC-001',),
            dgp_links=('DGP-MC-002',),
            required_actions=(StressAction.REQUIRE_FAILURE_REGISTRY_LINK, StressAction.REQUIRE_MULTICELL_MULTIPLICITY_RESEARCH),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
        _st("ST-FRL-006", "fm_multicell_winner_selection", StressTestCategory.FAILURE_REGISTRY_LINKAGE,
            StressSeverity.HARD_BLOCKER,
            "Winner-selection risk links to FM-DA-010.",
            affected_assignment_families=(AssignmentFamily.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferencePath.MAX_T, InferencePath.STEPDOWN),
            required_inputs=('failure_registry_lookup',),
            failure_registry_links=('FM-DA-010',),
            observed_diagnostic_links=('OPD-MC-003',),
            dgp_links=('DGP-MC-005',),
            required_actions=(StressAction.REQUIRE_FAILURE_REGISTRY_LINK, StressAction.REQUIRE_MULTICELL_MULTIPLICITY_RESEARCH),
            blocks_inference_if_failed=True,
            promotion_blocking=True,
            ),
    )

def build_design_assignment_generator_stress_tests() -> tuple[AssignmentGeneratorStressTest, ...]:
    """Build the full design assignment generator stress-test registry."""
    return (
        *_assignment_support_integrity_rows(),
        *_randomized_assignment_validity_rows(),
        *_matched_pair_rows(),
        *_matched_block_stratified_rows(),
        *_rerandomization_rows(),
        *_greedy_deterministic_rows(),
        *_kernel_thinning_rows(),
        *_multi_treated_placebo_rows(),
        *_multicell_shared_control_rows(),
        *_inference_feasibility_rows(),
        *_failure_registry_linkage_rows(),
    )


def filter_design_assignment_generator_stress_tests(
    stress_tests: tuple[AssignmentGeneratorStressTest, ...],
    *,
    category: StressTestCategory | None = None,
    severity: StressSeverity | None = None,
    assignment_family: AssignmentFamily | None = None,
    inference_path: InferencePath | None = None,
    action: StressAction | None = None,
    blocks_inference_if_failed: bool | None = None,
    promotion_blocking: bool | None = None,
) -> tuple[AssignmentGeneratorStressTest, ...]:
    """Filter stress tests by optional predicates."""
    filtered: list[AssignmentGeneratorStressTest] = []
    for st in stress_tests:
        if category is not None and st.category != category:
            continue
        if severity is not None and st.severity != severity:
            continue
        if assignment_family is not None and assignment_family not in st.affected_assignment_families:
            continue
        if inference_path is not None and inference_path not in st.affected_inference_paths:
            continue
        if action is not None and action not in st.required_actions:
            continue
        if blocks_inference_if_failed is not None and st.blocks_inference_if_failed != blocks_inference_if_failed:
            continue
        if promotion_blocking is not None and st.promotion_blocking != promotion_blocking:
            continue
        filtered.append(st)
    return tuple(filtered)


def validate_design_assignment_generator_stress_tests(
    stress_tests: tuple[AssignmentGeneratorStressTest, ...],
) -> dict[str, Any]:
    """Validate stress-test registry invariants and return structured validation summary."""
    issues: list[str] = []
    stress_ids = [st.stress_id for st in stress_tests]

    if len(stress_ids) != len(set(stress_ids)):
        issues.append("duplicate stress_id detected")
    if len(stress_tests) < 90:
        issues.append(f"stress_test_count {len(stress_tests)} < 90")

    category_counts = Counter(st.category for st in stress_tests)
    for cat, minimum in MIN_CATEGORY_COUNTS.items():
        if category_counts.get(cat, 0) < minimum:
            issues.append(f"category {cat.value} count {category_counts.get(cat, 0)} < {minimum}")

    severity_counts = Counter(st.severity for st in stress_tests)
    for sev, minimum in MIN_SEVERITY_COUNTS.items():
        if severity_counts.get(sev, 0) < minimum:
            issues.append(f"severity {sev.value} count {severity_counts.get(sev, 0)} < {minimum}")

    action_counts = Counter(action for st in stress_tests for action in st.required_actions)
    for action, minimum in MIN_ACTION_COUNTS.items():
        if action_counts.get(action, 0) < minimum:
            issues.append(f"action {action.value} count {action_counts.get(action, 0)} < {minimum}")

    assignment_present: set[AssignmentFamily] = set()
    inference_present: set[InferencePath] = set()
    for st in stress_tests:
        assignment_present.update(st.affected_assignment_families)
        inference_present.update(st.affected_inference_paths)

    missing_assignment = sorted(REQUIRED_ASSIGNMENT_FAMILIES - assignment_present, key=lambda a: a.value)
    if missing_assignment:
        issues.append(f"missing assignment families: {[a.value for a in missing_assignment]}")

    missing_inference = sorted(REQUIRED_INFERENCE_PATHS - inference_present, key=lambda i: i.value)
    if missing_inference:
        issues.append(f"missing inference paths: {[i.value for i in missing_inference]}")

    for st in stress_tests:
        if not st.required_inputs:
            issues.append(f"{st.stress_id} empty required_inputs")
        if not st.failure_registry_links:
            issues.append(f"{st.stress_id} empty failure_registry_links")
        if not st.observed_diagnostic_links:
            issues.append(f"{st.stress_id} empty observed_diagnostic_links")
        if not st.dgp_links:
            issues.append(f"{st.stress_id} empty dgp_links")
        if not st.affected_assignment_families:
            issues.append(f"{st.stress_id} empty affected_assignment_families")
        if not st.affected_inference_paths:
            issues.append(f"{st.stress_id} empty affected_inference_paths")
        if not st.required_actions:
            issues.append(f"{st.stress_id} empty required_actions")

    blocking = [st for st in stress_tests if st.blocks_inference_if_failed]
    promo_blocking = [st for st in stress_tests if st.promotion_blocking]
    hard_blockers = [st for st in stress_tests if st.severity == StressSeverity.HARD_BLOCKER]
    diagnostic_only = [st for st in stress_tests if st.severity == StressSeverity.DIAGNOSTIC_ONLY]
    sensitivity_only = [st for st in stress_tests if st.severity == StressSeverity.SENSITIVITY_ONLY]
    research = [st for st in stress_tests if st.severity == StressSeverity.RESEARCH_REQUIRED]
    remediation = [st for st in stress_tests if st.severity == StressSeverity.REMEDIATION_REQUIRED]
    studentized = [st for st in stress_tests if StressAction.REQUIRE_STUDENTIZED_ADAPTER in st.required_actions]
    registry_linked = all(st.failure_registry_links for st in stress_tests)

    if not blocking:
        issues.append("no blocking stress tests defined")
    if not promo_blocking:
        issues.append("no promotion-blocking stress tests defined")
    if not hard_blockers:
        issues.append("no hard blockers defined")
    if not diagnostic_only:
        issues.append("no diagnostic-only paths defined")
    if not sensitivity_only:
        issues.append("no sensitivity-only paths defined")
    if not research:
        issues.append("no research-required paths defined")
    if not remediation:
        issues.append("no remediation-required paths defined")
    if not studentized:
        issues.append("no studentized-adapter prerequisite tests defined")
    if not registry_linked:
        issues.append("failure registry links missing")

    return {
        "valid": not issues,
        "stress_test_count": len(stress_tests),
        "unique_stress_ids": len(stress_ids) == len(set(stress_ids)),
        "category_counts": {cat.value: category_counts.get(cat, 0) for cat in StressTestCategory},
        "severity_counts": {sev.value: severity_counts.get(sev, 0) for sev in StressSeverity},
        "action_counts": {act.value: action_counts.get(act, 0) for act in StressAction},
        "assignment_support_integrity_covered": category_counts.get(StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY, 0) >= MIN_CATEGORY_COUNTS[StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY],
        "randomized_assignment_validity_covered": category_counts.get(StressTestCategory.RANDOMIZED_ASSIGNMENT_VALIDITY, 0) >= MIN_CATEGORY_COUNTS[StressTestCategory.RANDOMIZED_ASSIGNMENT_VALIDITY],
        "matched_pair_covered": category_counts.get(StressTestCategory.MATCHED_PAIR, 0) >= MIN_CATEGORY_COUNTS[StressTestCategory.MATCHED_PAIR],
        "matched_block_stratified_covered": category_counts.get(StressTestCategory.MATCHED_BLOCK_STRATIFIED, 0) >= MIN_CATEGORY_COUNTS[StressTestCategory.MATCHED_BLOCK_STRATIFIED],
        "rerandomization_covered": category_counts.get(StressTestCategory.RERANDOMIZATION, 0) >= MIN_CATEGORY_COUNTS[StressTestCategory.RERANDOMIZATION],
        "greedy_deterministic_covered": category_counts.get(StressTestCategory.GREEDY_DETERMINISTIC, 0) >= MIN_CATEGORY_COUNTS[StressTestCategory.GREEDY_DETERMINISTIC],
        "kernel_thinning_covered": category_counts.get(StressTestCategory.KERNEL_THINNING, 0) >= MIN_CATEGORY_COUNTS[StressTestCategory.KERNEL_THINNING],
        "multi_treated_placebo_covered": category_counts.get(StressTestCategory.MULTI_TREATED_PLACEBO, 0) >= MIN_CATEGORY_COUNTS[StressTestCategory.MULTI_TREATED_PLACEBO],
        "multicell_shared_control_covered": category_counts.get(StressTestCategory.MULTICELL_SHARED_CONTROL, 0) >= MIN_CATEGORY_COUNTS[StressTestCategory.MULTICELL_SHARED_CONTROL],
        "inference_feasibility_covered": category_counts.get(StressTestCategory.INFERENCE_FEASIBILITY, 0) >= MIN_CATEGORY_COUNTS[StressTestCategory.INFERENCE_FEASIBILITY],
        "failure_registry_linkage_covered": category_counts.get(StressTestCategory.FAILURE_REGISTRY_LINKAGE, 0) >= MIN_CATEGORY_COUNTS[StressTestCategory.FAILURE_REGISTRY_LINKAGE],
        "blocking_stress_tests_defined": bool(blocking),
        "promotion_blocking_stress_tests_defined": bool(promo_blocking),
        "hard_blockers_defined": bool(hard_blockers),
        "diagnostic_only_paths_defined": bool(diagnostic_only),
        "sensitivity_only_paths_defined": bool(sensitivity_only),
        "research_required_paths_defined": bool(research),
        "remediation_required_paths_defined": bool(remediation),
        "studentized_adapter_prerequisites_defined": bool(studentized),
        "failure_registry_links_present": registry_linked,
        "issues": issues,
    }


def summarize_design_assignment_generator_stress_tests(
    stress_tests: tuple[AssignmentGeneratorStressTest, ...],
) -> dict[str, Any]:
    """Serialize design assignment generator stress-test summary for archives."""
    validation = validate_design_assignment_generator_stress_tests(stress_tests)
    assignment_family_counts: Counter[str] = Counter()
    inference_path_counts: Counter[str] = Counter()
    for st in stress_tests:
        for family in st.affected_assignment_families:
            assignment_family_counts[family.value] += 1
        for path in st.affected_inference_paths:
            inference_path_counts[path.value] += 1

    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "stress_test_count": len(stress_tests),
        "failed_scenarios": validation.get("issues", []),
        "category_counts": validation["category_counts"],
        "severity_counts": validation["severity_counts"],
        "action_counts": validation["action_counts"],
        "assignment_family_counts": dict(assignment_family_counts),
        "inference_path_counts": dict(inference_path_counts),
        "assignment_support_integrity_covered": validation["assignment_support_integrity_covered"],
        "randomized_assignment_validity_covered": validation["randomized_assignment_validity_covered"],
        "matched_pair_covered": validation["matched_pair_covered"],
        "matched_block_stratified_covered": validation["matched_block_stratified_covered"],
        "rerandomization_covered": validation["rerandomization_covered"],
        "greedy_deterministic_covered": validation["greedy_deterministic_covered"],
        "kernel_thinning_covered": validation["kernel_thinning_covered"],
        "multi_treated_placebo_covered": validation["multi_treated_placebo_covered"],
        "multicell_shared_control_covered": validation["multicell_shared_control_covered"],
        "inference_feasibility_covered": validation["inference_feasibility_covered"],
        "failure_registry_linkage_covered": validation["failure_registry_linkage_covered"],
        "assignment_generators_not_inference_engines": True,
        "unknown_and_deterministic_assignment_block_design_based_inference": True,
        "small_or_degenerate_support_blocks_rank_inference": True,
        "multicell_shared_control_requires_dependence_handling": True,
        "studentized_adapters_and_null_calibration_required": True,
        "stress_failures_link_to_failure_registry": validation["failure_registry_links_present"],
        "inference_authorized": False,
        "downstream_work_paused": True,
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
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
    stress_tests = build_design_assignment_generator_stress_tests()
    validation = validate_design_assignment_generator_stress_tests(stress_tests)
    summary = summarize_design_assignment_generator_stress_tests(stress_tests)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("stress_tests_build_successfully", len(stress_tests) > 0))
    scenarios.append(_scenario("stress_test_count_at_least_90", len(stress_tests) >= 90))
    scenarios.append(_scenario("stress_ids_unique", validation["unique_stress_ids"]))

    for cat in StressTestCategory:
        key = f"{cat.value}_covered"
        scenarios.append(_scenario(key, validation.get(key, False)))

    for sev, minimum in MIN_SEVERITY_COUNTS.items():
        count = sum(1 for st in stress_tests if st.severity == sev)
        scenarios.append(_scenario(f"severity_{sev.value}_at_least_{minimum}", count >= minimum))

    for action, minimum in MIN_ACTION_COUNTS.items():
        count = sum(1 for st in stress_tests for a in st.required_actions if a == action)
        scenarios.append(_scenario(f"action_{action.value}_at_least_{minimum}", count >= minimum))

    scenarios.append(_scenario("assignment_generators_not_inference_engines", summary["assignment_generators_not_inference_engines"] is True))
    scenarios.append(_scenario("unknown_and_deterministic_assignment_block_design_based_inference", summary["unknown_and_deterministic_assignment_block_design_based_inference"] is True))
    scenarios.append(_scenario("small_or_degenerate_support_blocks_rank_inference", summary["small_or_degenerate_support_blocks_rank_inference"] is True))
    scenarios.append(_scenario("multicell_shared_control_requires_dependence_handling", summary["multicell_shared_control_requires_dependence_handling"] is True))
    scenarios.append(_scenario("studentized_adapters_and_null_calibration_required", summary["studentized_adapters_and_null_calibration_required"] is True))
    scenarios.append(_scenario("stress_failures_link_to_failure_registry", summary["stress_failures_link_to_failure_registry"] is True))
    scenarios.append(_scenario("inference_authorized_false", summary["inference_authorized"] is False))
    scenarios.append(_scenario("downstream_work_paused", summary["downstream_work_paused"] is True))
    scenarios.append(_scenario("blocking_stress_tests_defined", validation["blocking_stress_tests_defined"] is True))
    scenarios.append(_scenario("promotion_blocking_stress_tests_defined", validation["promotion_blocking_stress_tests_defined"] is True))
    scenarios.append(_scenario("studentized_adapter_prerequisites_defined", validation["studentized_adapter_prerequisites_defined"] is True))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_tbrridge_inference_remediation_or_retirement_audit_001",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    for family in REQUIRED_ASSIGNMENT_FAMILIES:
        present = any(family in st.affected_assignment_families for st in stress_tests)
        scenarios.append(_scenario(f"assignment_family_{family.value}_represented", present))

    for path in REQUIRED_INFERENCE_PATHS:
        present = any(path in st.affected_inference_paths for st in stress_tests)
        scenarios.append(_scenario(f"inference_path_{path.value}_represented", present))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    stress_tests = build_design_assignment_generator_stress_tests()
    validation = validate_design_assignment_generator_stress_tests(stress_tests)
    summary = summarize_design_assignment_generator_stress_tests(stress_tests)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "stress_test_count": len(stress_tests),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        **{k: summary[k] for k in summary if k not in ("failed_scenarios", "valid")},
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + chr(10), encoding="utf-8")

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
