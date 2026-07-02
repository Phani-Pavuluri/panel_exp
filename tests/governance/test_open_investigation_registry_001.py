"""OPEN_INVESTIGATIONS_001 — authoritative investigation registry tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.governance.investigation_lifecycle_contract import (
    DEFAULT_REGISTRY_PATH,
    investigations_by_id,
    load_registry,
    validate_registry,
)

_REPO = Path(__file__).resolve().parents[2]


class TestOpenInvestigationRegistry001:
    def test_registry_file_exists(self) -> None:
        assert DEFAULT_REGISTRY_PATH.is_file()

    def test_registry_is_authoritative_json(self) -> None:
        reg = load_registry()
        assert reg["authoritative"] is True
        assert reg["registry_id"] == "OPEN_INVESTIGATIONS_001"
        assert len(reg["investigations"]) >= 5

    def test_registry_validates_clean(self) -> None:
        issues = validate_registry()
        assert issues == [], "\n".join(f"{i.code}: {i.message}" for i in issues)

    def test_brb_variance_investigation_seeded(self) -> None:
        by_id = investigations_by_id()
        inv = by_id["INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001"]
        assert inv.status == "RESOLVED"
        assert inv.discovered_by == "TBRRIDGE-BRB-INTERVAL-CORRECTION-001"
        assert inv.revisit_trigger is None
        assert inv.decision_checkpoint is not None
        assert inv.blocking_policy is not None
        assert inv.resolution_artifact == "DCM005-TBRRIDGE-BRB-POST-REMEDIATION-REASSESSMENT-001"
        assert inv.current_decision == "DIAGNOSTIC_ONLY"
        assert inv.evidence.get("post_remediation_decision") == "BRB_DIAGNOSTIC_ONLY"

    def test_brb_estimand_alignment_resolved(self) -> None:
        inv = investigations_by_id()["INV-TBRRIDGE-BRB-ESTIMAND-ALIGNMENT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "TBRRIDGE-BRB-INTERVAL-CORRECTION-001"

    def test_investigation_ids_unique(self) -> None:
        reg = load_registry()
        ids = [i["investigation_id"] for i in reg["investigations"]]
        assert len(ids) == len(set(ids))

    def test_complete_lanes_have_next_artifact_when_open_issues(self) -> None:
        reg = load_registry()
        for binding in reg.get("roadmap_lane_bindings", []):
            if binding.get("status") != "complete":
                continue
            if binding.get("open_investigations"):
                assert binding.get("next_artifact"), binding["lane_id"]

    def test_post_remediation_lane_resolves_brb_variance(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DCM005-TBRRIDGE-BRB-POST-REMEDIATION-REASSESSMENT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DCM005-TBRRIDGE-BRB-POST-REMEDIATION-REASSESSMENT-001"
        assert "INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001" in lane["resolved_investigations"]
        assert lane["next_artifact"] == "TRUSTREPORT_DOWNSTREAM_PROMOTION_001"

    def test_downstream_promotion_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TRUSTREPORT-DOWNSTREAM-PROMOTION-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TRUSTREPORT-DOWNSTREAM-PROMOTION-001"
        assert lane["next_artifact"] == "TRUSTREPORT_INTEGRATION_DRY_RUN_001"

    def test_integration_dry_run_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TRUSTREPORT-INTEGRATION-DRY-RUN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TRUSTREPORT-INTEGRATION-DRY-RUN-001"
        assert lane["next_artifact"] == "TRUSTREPORT_RESEARCH_MODE_RENDERER_001"

    def test_research_mode_renderer_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TRUSTREPORT-RESEARCH-MODE-RENDERER-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TRUSTREPORT-RESEARCH-MODE-RENDERER-001"
        assert lane["next_artifact"] == "TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001"

    def test_research_mode_artifact_export_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TRUSTREPORT-RESEARCH-MODE-ARTIFACT-EXPORT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TRUSTREPORT-RESEARCH-MODE-ARTIFACT-EXPORT-001"
        assert lane["next_artifact"] == "TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001"

    def test_research_mode_review_workflow_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TRUSTREPORT-RESEARCH-MODE-REVIEW-WORKFLOW-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TRUSTREPORT-RESEARCH-MODE-REVIEW-WORKFLOW-001"
        assert lane["next_artifact"] == "TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001"

    def test_research_mode_access_control_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TRUSTREPORT-RESEARCH-MODE-ACCESS-CONTROL-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TRUSTREPORT-RESEARCH-MODE-ACCESS-CONTROL-001"
        assert lane["next_artifact"] == "ROADMAP_REFOCUS_METHOD_VALIDATION_001"

    def test_roadmap_refocus_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "ROADMAP-REFOCUS-METHOD-VALIDATION-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "ROADMAP-REFOCUS-METHOD-VALIDATION-001"
        assert lane["next_artifact"] == "INFERENCE_REPLACEMENT_SCOUT_001"
        assert lane.get("trustreport_ops_status") == "freeze_after_research_mode_access_control"

    def test_inference_replacement_scout_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "INFERENCE-REPLACEMENT-SCOUT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "INFERENCE-REPLACEMENT-SCOUT-001"
        assert lane["next_artifact"] == "DESIGN_AWARE_ASSIGNMENT_GENERATORS_001"

    def test_design_aware_assignment_generators_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DESIGN-AWARE-ASSIGNMENT-GENERATORS-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DESIGN-AWARE-ASSIGNMENT-GENERATORS-001"
        assert lane["next_artifact"] == "MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001"
        assert "INV-MULTITREATED-DESIGN-AWARE-PLACEBO-001" not in lane["deferred_investigations"]

    def test_multitreated_treated_set_placebo_framework_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "MULTITREATED-TREATED-SET-PLACEBO-FRAMEWORK-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "MULTITREATED-TREATED-SET-PLACEBO-FRAMEWORK-001"
        assert lane["next_artifact"] == "SCM_PLACEBO_GOVERNED_SEMANTICS_001"
        assert "INV-MULTITREATED-DESIGN-AWARE-PLACEBO-001" not in lane["deferred_investigations"]

    def test_scm_placebo_governed_semantics_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-PLACEBO-GOVERNED-SEMANTICS-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_PLACEBO_GOVERNED_SEMANTICS_001"
        assert lane["next_artifact"] == "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001"
        assert "INV-MULTITREATED-DESIGN-AWARE-PLACEBO-001" in lane["deferred_investigations"]

    def test_method_specific_randomization_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "METHOD-SPECIFIC-RANDOMIZATION-INFERENCE-VALIDATION-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001"
        assert lane["next_artifact"] == "SCM_TREATED_SET_PLACEBO_INTEGRATION_001"
        assert "method_validity" in lane["artifact_tags"]

    def test_scm_treated_set_placebo_integration_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-TREATED-SET-PLACEBO-INTEGRATION-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_TREATED_SET_PLACEBO_INTEGRATION_001"
        assert lane["next_artifact"] == "STUDENTIZED_PLACEBO_RANK_INFERENCE_001"
        assert "scm_integration" in lane["artifact_tags"]

    def test_studentized_placebo_rank_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "STUDENTIZED-PLACEBO-RANK-INFERENCE-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "STUDENTIZED_PLACEBO_RANK_INFERENCE_001"
        assert lane["next_artifact"] == "SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001"
        assert "studentized_placebo_rank" in lane["artifact_tags"]

    def test_scm_studentized_treated_set_placebo_integration_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-STUDENTIZED-TREATED-SET-PLACEBO-INTEGRATION-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001"
        assert lane["next_artifact"] == "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001"
        assert "scm_studentized_integration" in lane["artifact_tags"]

    def test_multicell_shared_control_multiplicity_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "MULTICELL-SHARED-CONTROL-MULTIPLICITY-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001"
        assert lane["next_artifact"] == "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001"
        assert "multicell_multiplicity" in lane["artifact_tags"]

    def test_stratified_pooled_estimand_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "STRATIFIED-POOLED-ESTIMAND-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001"
        assert lane["next_artifact"] == "AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001"
        assert "stratified_estimand" in lane["artifact_tags"]
        assert "pooled_estimand_contract" in lane["artifact_tags"]

    def test_augsynth_point_randomization_integration_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "AUGSYNTH-POINT-RANDOMIZATION-INTEGRATION-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001"
        assert lane["next_artifact"] == "METHOD_READINESS_MATRIX_V2_001"
        assert "augsynth_point" in lane["artifact_tags"]
        assert "randomization_inference" in lane["artifact_tags"]

    def test_method_readiness_matrix_v2_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "METHOD-READINESS-MATRIX-V2-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "METHOD_READINESS_MATRIX_V2_001"
        assert lane["next_artifact"] == "CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001"
        assert "readiness_matrix" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_calibration_signal_method_gate_draft_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "CALIBRATION-SIGNAL-METHOD-GATE-DRAFT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001"
        assert lane["next_artifact"] == "METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001"
        assert "calibration_signal_draft_gate" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_method_accuracy_compatibility_refocus_audit_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "METHOD-ACCURACY-COMPATIBILITY-REFOCUS-AUDIT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001"
        assert lane["next_artifact"] == "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001"
        assert "method_accuracy" in lane["artifact_tags"]
        assert "downstream_pause" in lane["artifact_tags"]

    def test_studentized_randomization_null_calibration_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "STUDENTIZED-RANDOMIZATION-NULL-CALIBRATION-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001"
        assert lane["next_artifact"] == "SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001"
        assert "null_calibration" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_scm_augsynth_statistic_adapter_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-AUGSYNTH-STATISTIC-ADAPTER-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001"
        assert lane["next_artifact"] == "ROADMAP_INFERENCE_AND_METHOD_GAP_CONTROL_REFOCUS_001"
        assert "statistic_adapter" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_roadmap_inference_and_method_gap_control_refocus_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "ROADMAP-INFERENCE-AND-METHOD-GAP-CONTROL-REFOCUS-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "ROADMAP_INFERENCE_AND_METHOD_GAP_CONTROL_REFOCUS_001"
        assert lane["next_artifact"] == "ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001"
        assert "INV-METHOD-GAP-COVERAGE-LITERATURE-ALIGNMENT-001" in lane["open_investigations"]
        assert "INV-ESTIMATOR-DESIGN-INFERENCE-SUITABILITY-MATRIX-001" in lane["resolved_investigations"]
        assert "method_gap_control" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_estimator_design_inference_suitability_matrix_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "ESTIMATOR-DESIGN-INFERENCE-SUITABILITY-MATRIX-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001"
        assert lane["next_artifact"] == "METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001"
        assert "INV-METHOD-GAP-COVERAGE-LITERATURE-ALIGNMENT-001" in lane["open_investigations"]
        assert "inference_suitability" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_method_gap_coverage_literature_alignment_audit_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "METHOD-GAP-COVERAGE-AND-LITERATURE-ALIGNMENT-AUDIT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001"
        assert lane["next_artifact"] == "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001"
        assert "INV-METHOD-GAP-COVERAGE-LITERATURE-ALIGNMENT-001" in lane["resolved_investigations"]
        assert "INV-OBSERVED-PANEL-DIAGNOSTIC-REQUIREMENTS-001" in lane["open_investigations"]
        assert "literature_alignment" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_method_gap_coverage_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-METHOD-GAP-COVERAGE-LITERATURE-ALIGNMENT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001"

    def test_observed_panel_diagnostic_requirements_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "OBSERVED-PANEL-DIAGNOSTIC-REQUIREMENTS-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001"
        assert lane["next_artifact"] == "SIMULATION_DGP_COVERAGE_PLAN_001"
        assert "INV-OBSERVED-PANEL-DIAGNOSTIC-REQUIREMENTS-001" in lane["resolved_investigations"]
        assert "INV-SIMULATION-DGP-COVERAGE-PLAN-001" in lane["open_investigations"]
        assert "observed_data_diagnostics" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_observed_panel_diagnostic_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-OBSERVED-PANEL-DIAGNOSTIC-REQUIREMENTS-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001"

    def test_simulation_dgp_coverage_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SIMULATION-DGP-COVERAGE-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SIMULATION_DGP_COVERAGE_PLAN_001"
        assert lane["next_artifact"] == "METHOD_FAILURE_MODE_REGISTRY_001"
        assert "INV-SIMULATION-DGP-COVERAGE-PLAN-001" in lane["resolved_investigations"]
        assert "INV-METHOD-FAILURE-MODE-REGISTRY-001" in lane["open_investigations"]
        assert "simulation_coverage" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_simulation_dgp_coverage_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SIMULATION-DGP-COVERAGE-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SIMULATION_DGP_COVERAGE_PLAN_001"

    def test_method_failure_mode_registry_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "METHOD-FAILURE-MODE-REGISTRY-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "METHOD_FAILURE_MODE_REGISTRY_001"
        assert lane["next_artifact"] == "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001"
        assert "INV-METHOD-FAILURE-MODE-REGISTRY-001" in lane["resolved_investigations"]
        assert "INV-DESIGN-ASSIGNMENT-GENERATOR-STRESS-TESTS-001" in lane["open_investigations"]
        assert "failure_registry" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_method_failure_mode_registry_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-METHOD-FAILURE-MODE-REGISTRY-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "METHOD_FAILURE_MODE_REGISTRY_001"

    def test_design_assignment_generator_stress_tests_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DESIGN-ASSIGNMENT-GENERATOR-STRESS-TESTS-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001"
        assert lane["next_artifact"] == "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"
        assert "INV-DESIGN-ASSIGNMENT-GENERATOR-STRESS-TESTS-001" in lane["resolved_investigations"]
        assert "INV-TBRRIDGE-INFERENCE-REMEDIATION-OR-RETIREMENT-AUDIT-001" in lane["open_investigations"]
        assert "assignment_generator_stress" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_design_assignment_generator_stress_tests_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-DESIGN-ASSIGNMENT-GENERATOR-STRESS-TESTS-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001"

    def test_tbrridge_inference_remediation_or_retirement_audit_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TBRRIDGE-INFERENCE-REMEDIATION-OR-RETIREMENT-AUDIT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"
        assert lane["next_artifact"] == "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001"
        assert "INV-TBRRIDGE-INFERENCE-REMEDIATION-OR-RETIREMENT-AUDIT-001" in lane["resolved_investigations"]
        assert "INV-DID-RANDOMIZATION-BOOTSTRAP-SUITABILITY-001" in lane["open_investigations"]
        assert "tbrridge_inference" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_tbrridge_inference_remediation_or_retirement_audit_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-TBRRIDGE-INFERENCE-REMEDIATION-OR-RETIREMENT-AUDIT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"

    def test_did_randomization_bootstrap_suitability_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DID-RANDOMIZATION-BOOTSTRAP-SUITABILITY-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001"
        assert lane["next_artifact"] == "METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001"
        assert "INV-DID-RANDOMIZATION-BOOTSTRAP-SUITABILITY-001" in lane["resolved_investigations"]
        assert "INV-METHOD-FAMILY-PRODUCTION-COMPATIBILITY-REMEDIATION-ROADMAP-001" in lane["open_investigations"]
        assert "did_inference" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_did_randomization_bootstrap_suitability_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-DID-RANDOMIZATION-BOOTSTRAP-SUITABILITY-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001"

    def test_method_family_production_compatibility_remediation_roadmap_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "METHOD-FAMILY-PRODUCTION-COMPATIBILITY-REMEDIATION-ROADMAP-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001"
        assert lane["next_artifact"] == "MULTICELL_MAX_T_RESEARCH_SCOUT_001"
        assert "INV-METHOD-FAMILY-PRODUCTION-COMPATIBILITY-REMEDIATION-ROADMAP-001" in lane["resolved_investigations"]
        assert "production_compatibility" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_method_family_production_compatibility_remediation_roadmap_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-METHOD-FAMILY-PRODUCTION-COMPATIBILITY-REMEDIATION-ROADMAP-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001"

    def test_multicell_max_t_research_scout_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "MULTICELL-MAX-T-RESEARCH-SCOUT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "MULTICELL_MAX_T_RESEARCH_SCOUT_001"
        assert lane["next_artifact"] == "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001"
        assert "INV-MULTICELL-MAX-T-RESEARCH-SCOUT-001" in lane["resolved_investigations"]
        assert "INV-SCM-AUGSYNTH-INFERENCE-PROMOTION-GATE-AUDIT-001" in lane["open_investigations"]
        assert "multicell_multiplicity" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_multicell_max_t_research_scout_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-MULTICELL-MAX-T-RESEARCH-SCOUT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "MULTICELL_MAX_T_RESEARCH_SCOUT_001"

    def test_scm_augsynth_inference_promotion_gate_audit_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-AUGSYNTH-INFERENCE-PROMOTION-GATE-AUDIT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001"
        assert lane["next_artifact"] == "SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001"
        assert "INV-SCM-AUGSYNTH-INFERENCE-PROMOTION-GATE-AUDIT-001" in lane["resolved_investigations"]
        assert "INV-SYNTHETIC-DID-METHOD-SCOUT-AND-SUITABILITY-001" in lane["open_investigations"]
        assert "promotion_gate" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_scm_augsynth_inference_promotion_gate_audit_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SCM-AUGSYNTH-INFERENCE-PROMOTION-GATE-AUDIT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001"

    def test_bayesian_tbr_retirement_boundary_audit_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "BAYESIAN-TBR-AND-TBR-RETIREMENT-BOUNDARY-AUDIT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001"
        assert lane["next_artifact"] == "TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001"
        assert "INV-BAYESIAN-TBR-AND-TBR-RETIREMENT-BOUNDARY-AUDIT-001" in lane["resolved_investigations"]
        assert "INV-TROP-RESEARCH-ONLY-BOUNDARY-AUDIT-001" in lane["open_investigations"]
        assert "tbr_retirement" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_bayesian_tbr_retirement_boundary_audit_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-BAYESIAN-TBR-AND-TBR-RETIREMENT-BOUNDARY-AUDIT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001"

    def test_synthetic_did_method_scout_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SYNTHETIC-DID-METHOD-SCOUT-AND-SUITABILITY-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001"
        assert lane["next_artifact"] == "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001"
        assert "INV-SYNTHETIC-DID-METHOD-SCOUT-AND-SUITABILITY-001" in lane["resolved_investigations"]
        assert "INV-BAYESIAN-TBR-AND-TBR-RETIREMENT-BOUNDARY-AUDIT-001" in lane["open_investigations"]
        assert "synthetic_did" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_synthetic_did_method_scout_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SYNTHETIC-DID-METHOD-SCOUT-AND-SUITABILITY-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001"

    def test_trop_research_only_boundary_audit_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TROP-RESEARCH-ONLY-BOUNDARY-AUDIT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001"
        assert lane["next_artifact"] == "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001"
        assert "INV-TROP-RESEARCH-ONLY-BOUNDARY-AUDIT-001" in lane["resolved_investigations"]
        assert "INV-METHOD-FAMILY-PROMOTION-CRITERIA-MATRIX-001" in lane["open_investigations"]
        assert "trop" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_trop_research_only_boundary_audit_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-TROP-RESEARCH-ONLY-BOUNDARY-AUDIT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001"

    def test_method_family_promotion_criteria_matrix_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "METHOD-FAMILY-PROMOTION-CRITERIA-MATRIX-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001"
        assert lane["next_artifact"] == "PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001"
        assert "INV-METHOD-FAMILY-PROMOTION-CRITERIA-MATRIX-001" in lane["resolved_investigations"]
        assert "INV-PRODUCTION-COMPATIBILITY-PROMOTION-WORKPLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "promotion_criteria" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_method_family_promotion_criteria_matrix_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-METHOD-FAMILY-PROMOTION-CRITERIA-MATRIX-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001"

    def test_production_compatibility_promotion_workplan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "PRODUCTION-COMPATIBILITY-PROMOTION-WORKPLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"
        assert "INV-PRODUCTION-COMPATIBILITY-PROMOTION-WORKPLAN-001" in lane["resolved_investigations"]
        assert "INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "promotion_workplan" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_production_compatibility_promotion_workplan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-PRODUCTION-COMPATIBILITY-PROMOTION-WORKPLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001"

    def test_multicell_dependence_multiplicity_validation_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-MULTICELL-DEPENDENCE-AND-MULTIPLICITY-VALIDATION-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001"

    def test_augsynth_remediation_diagnostic_validation_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-AUGSYNTH-REMEDIATION-AND-DIAGNOSTIC-VALIDATION-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001"

    def test_scm_production_candidate_validation_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"
        assert lane["next_artifact"] == "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001"
        assert "INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001" in lane["resolved_investigations"]
        assert "INV-MULTICELL-DEPENDENCE-AND-MULTIPLICITY-VALIDATION-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "scm" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_multicell_dependence_multiplicity_validation_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "MULTICELL-DEPENDENCE-AND-MULTIPLICITY-VALIDATION-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001"
        assert lane["next_artifact"] == "PRODUCTION_READINESS_BACKLOG_LEDGER_001"
        assert "INV-MULTICELL-DEPENDENCE-AND-MULTIPLICITY-VALIDATION-PLAN-001" in lane["resolved_investigations"]
        assert "INV-PRODUCTION-READINESS-BACKLOG-LEDGER-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "multicell" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_production_readiness_backlog_ledger_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-PRODUCTION-READINESS-BACKLOG-LEDGER-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "PRODUCTION_READINESS_BACKLOG_LEDGER_001"

    def test_data_driven_selection_gate_requirements_investigation_resolved(self) -> None:
        inv = investigations_by_id()[
            "INV-DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-REQUIREMENTS-001"
        ]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == (
            "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001"
        )

    def test_data_driven_selection_gate_implementation_plan_investigation_resolved_early(self) -> None:
        inv = investigations_by_id()[
            "INV-DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-IMPLEMENTATION-PLAN-001"
        ]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == (
            "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001"
        )

    def test_production_readiness_backlog_ledger_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "PRODUCTION-READINESS-BACKLOG-LEDGER-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "PRODUCTION_READINESS_BACKLOG_LEDGER_001"
        assert lane["next_artifact"] == (
            "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001"
        )
        assert "INV-PRODUCTION-READINESS-BACKLOG-LEDGER-001" in lane["resolved_investigations"]
        assert (
            "INV-DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-REQUIREMENTS-001"
            in lane["resolved_investigations"]
        )
        assert lane["open_investigations"] == []
        assert "backlog" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_data_driven_selection_gate_requirements_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-REQUIREMENTS-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == (
            "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001"
        )
        assert lane["next_artifact"] == "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001"
        assert (
            "INV-DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-REQUIREMENTS-001"
            in lane["resolved_investigations"]
        )
        assert "INV-AUGSYNTH-REMEDIATION-AND-DIAGNOSTIC-VALIDATION-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "selection_gate" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_augsynth_remediation_diagnostic_validation_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "AUGSYNTH-REMEDIATION-AND-DIAGNOSTIC-VALIDATION-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001"
        assert lane["next_artifact"] == "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"
        assert "INV-AUGSYNTH-REMEDIATION-AND-DIAGNOSTIC-VALIDATION-PLAN-001" in lane["resolved_investigations"]
        assert "INV-DID-CONDITIONAL-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "augsynth" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_did_conditional_production_candidate_validation_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DID-CONDITIONAL-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"
        assert lane["next_artifact"] == "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001"
        assert "INV-DID-CONDITIONAL-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001" in lane["resolved_investigations"]
        assert "INV-SYNTHETIC-DID-IMPLEMENTATION-READINESS-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "did" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_synthetic_did_implementation_readiness_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SYNTHETIC-DID-IMPLEMENTATION-READINESS-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001"
        assert lane["next_artifact"] == "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001"
        assert "INV-SYNTHETIC-DID-IMPLEMENTATION-READINESS-PLAN-001" in lane["resolved_investigations"]
        assert "INV-METHOD-FAMILY-RETIRE-REPLACE-EXECUTION-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "synthetic_did" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_method_family_retire_replace_execution_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "METHOD-FAMILY-RETIRE-REPLACE-EXECUTION-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001"
        assert lane["next_artifact"] == (
            "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001"
        )
        assert "INV-METHOD-FAMILY-RETIRE-REPLACE-EXECUTION-PLAN-001" in lane["resolved_investigations"]
        assert (
            "INV-DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-IMPLEMENTATION-PLAN-001"
            in lane["resolved_investigations"]
        )
        assert lane["open_investigations"] == []
        assert "retire_replace" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_selection_gate_implementation_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-IMPLEMENTATION-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == (
            "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001"
        )
        assert lane["next_artifact"] == "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001"
        assert (
            "INV-DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-IMPLEMENTATION-PLAN-001"
            in lane["resolved_investigations"]
        )
        assert "INV-PRODUCTION-AUTHORIZATION-RELEASE-GATE-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "selection_gate" in lane["artifact_tags"]
        assert "implementation_plan" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_production_authorization_release_gate_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "PRODUCTION-AUTHORIZATION-RELEASE-GATE-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001"
        assert "INV-PRODUCTION-AUTHORIZATION-RELEASE-GATE-PLAN-001" in lane["resolved_investigations"]
        assert "INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "release_gate" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_scm_production_candidate_validation_implementation_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001"
        assert "INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "scm" in lane["artifact_tags"]
        assert "production_candidate_gated" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_scm_production_candidate_validation_implementation_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001"
        assert "INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "scm" in lane["artifact_tags"]
        assert "validation_metadata_implementation" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_scm_production_candidate_validation_implementation_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001"

    def test_scm_production_candidate_null_calibration_implementation_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-NULL-CALIBRATION-IMPLEMENTATION-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001"
        assert "INV-SCM-PRODUCTION-CANDIDATE-NULL-CALIBRATION-IMPLEMENTATION-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "scm" in lane["artifact_tags"]
        assert "null_calibration_implementation_plan" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_scm_production_candidate_null_calibration_implementation_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-NULL-CALIBRATION-IMPLEMENTATION-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001"

    def test_scm_production_candidate_null_calibration_implementation_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-NULL-CALIBRATION-IMPLEMENTATION-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001"
        assert "INV-SCM-PRODUCTION-CANDIDATE-NULL-CALIBRATION-IMPLEMENTATION-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "scm" in lane["artifact_tags"]
        assert "null_calibration_metadata_implementation" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_scm_production_candidate_null_calibration_implementation_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-NULL-CALIBRATION-IMPLEMENTATION-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001"

    def test_scm_production_candidate_jackknife_sensitivity_implementation_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-JACKKNIFE-SENSITIVITY-IMPLEMENTATION-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001"
        assert "INV-SCM-PRODUCTION-CANDIDATE-JACKKNIFE-SENSITIVITY-IMPLEMENTATION-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "scm" in lane["artifact_tags"]
        assert "jackknife_sensitivity_implementation_plan" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_scm_production_candidate_jackknife_sensitivity_implementation_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-JACKKNIFE-SENSITIVITY-IMPLEMENTATION-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001"

    def test_scm_production_candidate_jackknife_sensitivity_implementation_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-JACKKNIFE-SENSITIVITY-IMPLEMENTATION-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001"
        assert "INV-SCM-PRODUCTION-CANDIDATE-JACKKNIFE-SENSITIVITY-IMPLEMENTATION-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "scm" in lane["artifact_tags"]
        assert "jackknife_sensitivity_metadata_implementation" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_scm_production_candidate_jackknife_sensitivity_implementation_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-JACKKNIFE-SENSITIVITY-IMPLEMENTATION-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001"

    def test_scm_production_candidate_release_gate_review_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-REVIEW-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001"
        assert "INV-SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-REVIEW-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "scm" in lane["artifact_tags"]
        assert "release_gate_review_plan" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_scm_production_candidate_release_gate_review_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-REVIEW-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001"

    def test_scm_production_candidate_release_gate_review_packet_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-REVIEW-PACKET-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001"
        assert "INV-SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-REVIEW-PACKET-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "scm" in lane["artifact_tags"]
        assert "release_gate_review_packet" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]

    def test_scm_production_candidate_release_gate_review_packet_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-REVIEW-PACKET-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001"

    def test_scm_production_candidate_release_gate_decision_plan_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-DECISION-PLAN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001"
        assert "INV-SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-DECISION-PLAN-001" in lane["resolved_investigations"]
        assert lane["open_investigations"] == []
        assert "scm" in lane["artifact_tags"]
        assert "release_gate_decision_plan" in lane["artifact_tags"]
        assert "defer_pending_empirical_validation" in lane["artifact_tags"]

    def test_scm_production_candidate_release_gate_decision_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-DECISION-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001"

    def test_method_portfolio_prioritization_checkpoint_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "METHOD-PORTFOLIO-PRIORITIZATION-CHECKPOINT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001"
        assert "INV-METHOD-PORTFOLIO-PRIORITIZATION-CHECKPOINT-001" in lane["resolved_investigations"]
        assert "augsynth_primary_after_closeout" in lane["artifact_tags"]

    def test_method_portfolio_prioritization_checkpoint_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-METHOD-PORTFOLIO-PRIORITIZATION-CHECKPOINT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001"

    def test_experiment_portfolio_planner_agent_roadmap_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "EXPERIMENT-PORTFOLIO-PLANNER-AGENT-ROADMAP-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001"
        assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001"
        assert "INV-EXPERIMENT-PORTFOLIO-PLANNER-AGENT-ROADMAP-001" in lane["resolved_investigations"]
        assert "design_before_estimator" in lane["artifact_tags"]

    def test_experiment_portfolio_planner_agent_roadmap_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-EXPERIMENT-PORTFOLIO-PLANNER-AGENT-ROADMAP-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001"

    def test_experiment_portfolio_planner_agent_tooling_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "EXPERIMENT-PORTFOLIO-PLANNER-AGENT-TOOLING-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001"
        assert lane["next_artifact"] == "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"
        assert "INV-EXPERIMENT-PORTFOLIO-PLANNER-AGENT-TOOLING-CONTRACT-001" in lane["resolved_investigations"]
        assert "no_tool_no_claim" in lane["artifact_tags"]

    def test_experiment_portfolio_planner_agent_tooling_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-EXPERIMENT-PORTFOLIO-PLANNER-AGENT-TOOLING-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001"

    def test_roadmap_implementation_detail_gap_audit_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "ROADMAP-IMPLEMENTATION-DETAIL-GAP-AUDIT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001"
        assert lane["next_artifact"] == "GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001"
        assert "INV-ROADMAP-IMPLEMENTATION-DETAIL-GAP-AUDIT-001" in lane["resolved_investigations"]

    def test_roadmap_implementation_detail_gap_audit_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-ROADMAP-IMPLEMENTATION-DETAIL-GAP-AUDIT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001"

    def test_geo_kpi_spend_data_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "GEO-KPI-SPEND-DATA-CONTRACT-AND-PROFILER-SPEC-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001"
        assert lane["next_artifact"] == "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"
        assert "INV-GEO-KPI-SPEND-DATA-CONTRACT-AND-PROFILER-SPEC-001" in lane["resolved_investigations"]

    def test_geo_kpi_spend_data_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-GEO-KPI-SPEND-DATA-CONTRACT-AND-PROFILER-SPEC-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001"

    def test_experiment_portfolio_intake_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "EXPERIMENT-PORTFOLIO-INTAKE-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"
        assert lane["next_artifact"] == "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001"
        assert "INV-EXPERIMENT-PORTFOLIO-INTAKE-CONTRACT-001" in lane["resolved_investigations"]

    def test_experiment_portfolio_intake_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-EXPERIMENT-PORTFOLIO-INTAKE-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"

    def test_panel_exp_agent_run_packet_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "PANEL-EXP-AGENT-RUN-PACKET-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001"
        assert lane["next_artifact"] == "PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001"
        assert "INV-PANEL-EXP-AGENT-RUN-PACKET-CONTRACT-001" in lane["resolved_investigations"]

    def test_panel_exp_agent_run_packet_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-PANEL-EXP-AGENT-RUN-PACKET-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001"

    def test_panel_exp_artifact_registry_provenance_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "PANEL-EXP-ARTIFACT-REGISTRY-AND-PROVENANCE-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001"
        assert lane["next_artifact"] == "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001"
        assert "INV-PANEL-EXP-ARTIFACT-REGISTRY-AND-PROVENANCE-CONTRACT-001" in lane["resolved_investigations"]

    def test_panel_exp_artifact_registry_provenance_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-PANEL-EXP-ARTIFACT-REGISTRY-AND-PROVENANCE-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001"

    def test_panel_exp_golden_path_acceptance_tests_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "PANEL-EXP-GOLDEN-PATH-ACCEPTANCE-TESTS-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001"
        assert lane["next_artifact"] == "GEO_KPI_SPEND_DATA_PROFILER_001"
        assert "INV-PANEL-EXP-GOLDEN-PATH-ACCEPTANCE-TESTS-001" in lane["resolved_investigations"]

    def test_panel_exp_golden_path_acceptance_tests_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-PANEL-EXP-GOLDEN-PATH-ACCEPTANCE-TESTS-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001"

    def test_geo_kpi_spend_data_profiler_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "GEO-KPI-SPEND-DATA-PROFILER-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "GEO_KPI_SPEND_DATA_PROFILER_001"
        assert lane["next_artifact"] == "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001"
        assert "INV-GEO-KPI-SPEND-DATA-PROFILER-001" in lane["resolved_investigations"]

    def test_geo_kpi_spend_data_profiler_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-GEO-KPI-SPEND-DATA-PROFILER-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "GEO_KPI_SPEND_DATA_PROFILER_001"

    def test_geo_unit_market_feasibility_diagnostics_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "GEO-UNIT-AND-MARKET-FEASIBILITY-DIAGNOSTICS-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001"
        assert lane["next_artifact"] == "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001"
        assert "INV-GEO-UNIT-AND-MARKET-FEASIBILITY-DIAGNOSTICS-001" in lane["resolved_investigations"]

    def test_geo_unit_market_feasibility_diagnostics_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-GEO-UNIT-AND-MARKET-FEASIBILITY-DIAGNOSTICS-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001"

    def test_spend_contrast_feasibility_tooling_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SPEND-CONTRAST-FEASIBILITY-TOOLING-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001"
        assert lane["next_artifact"] == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001"
        assert "INV-SPEND-CONTRAST-FEASIBILITY-TOOLING-CONTRACT-001" in lane["resolved_investigations"]

    def test_spend_contrast_feasibility_tooling_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SPEND-CONTRAST-FEASIBILITY-TOOLING-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001"

    def test_spend_requirement_manipulation_feasibility_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SPEND-REQUIREMENT-AND-MANIPULATION-FEASIBILITY-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001"
        assert lane["next_artifact"] == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001"
        assert "INV-SPEND-REQUIREMENT-AND-MANIPULATION-FEASIBILITY-CONTRACT-001" in lane["resolved_investigations"]

    def test_spend_requirement_manipulation_feasibility_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SPEND-REQUIREMENT-AND-MANIPULATION-FEASIBILITY-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001"

    def test_spend_requirement_manipulation_feasibility_diagnostics_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SPEND-REQUIREMENT-AND-MANIPULATION-FEASIBILITY-DIAGNOSTICS-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001"
        assert lane["next_artifact"] == "POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001"
        assert "INV-SPEND-REQUIREMENT-AND-MANIPULATION-FEASIBILITY-DIAGNOSTICS-001" in lane["resolved_investigations"]

    def test_spend_requirement_manipulation_feasibility_diagnostics_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SPEND-REQUIREMENT-AND-MANIPULATION-FEASIBILITY-DIAGNOSTICS-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001"

    def test_power_mde_spend_feasibility_handoff_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "POWER-MDE-REQUIREMENT-AND-SPEND-FEASIBILITY-HANDOFF-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001"
        assert lane["next_artifact"] == "POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001"
        assert "INV-POWER-MDE-REQUIREMENT-AND-SPEND-FEASIBILITY-HANDOFF-CONTRACT-001" in lane["resolved_investigations"]

    def test_power_mde_spend_feasibility_handoff_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-POWER-MDE-REQUIREMENT-AND-SPEND-FEASIBILITY-HANDOFF-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001"

    def test_power_mde_diagnostics_lane_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "POWER-MDE-DIAGNOSTICS-LANE-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001"
        assert lane["next_artifact"] == "POWER_MDE_DIAGNOSTICS_RUNTIME_001"
        assert "INV-POWER-MDE-DIAGNOSTICS-LANE-CONTRACT-001" in lane["resolved_investigations"]

    def test_power_mde_diagnostics_lane_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-POWER-MDE-DIAGNOSTICS-LANE-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001"

    def test_power_mde_diagnostics_runtime_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "POWER-MDE-DIAGNOSTICS-RUNTIME-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "POWER_MDE_DIAGNOSTICS_RUNTIME_001"
        assert lane["next_artifact"] == "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001"
        assert "INV-POWER-MDE-DIAGNOSTICS-RUNTIME-001" in lane["resolved_investigations"]

    def test_power_mde_diagnostics_runtime_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-POWER-MDE-DIAGNOSTICS-RUNTIME-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "POWER_MDE_DIAGNOSTICS_RUNTIME_001"

    def test_design_cell_structure_assignment_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DESIGN-CELL-STRUCTURE-AND-ASSIGNMENT-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001"
        assert lane["next_artifact"] == "DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001"
        assert "INV-DESIGN-CELL-STRUCTURE-AND-ASSIGNMENT-CONTRACT-001" in lane["resolved_investigations"]

    def test_design_cell_structure_assignment_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-DESIGN-CELL-STRUCTURE-AND-ASSIGNMENT-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001"
        assert inv.current_decision == (
            "DESIGN_CELL_CONTRAST_AND_SCENARIO_CONTRACT_DEFINED_NO_RUNTIME_ASSIGNMENT_OR_SCENARIO_OPTIMIZATION"
        )

    def test_design_scenario_policy_feasibility_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DESIGN-SCENARIO-POLICY-FEASIBILITY-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001"
        assert lane["next_artifact"] == "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001"
        assert "INV-DESIGN-SCENARIO-POLICY-FEASIBILITY-CONTRACT-001" in lane["resolved_investigations"]

    def test_design_scenario_policy_feasibility_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-DESIGN-SCENARIO-POLICY-FEASIBILITY-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001"
        assert inv.current_decision == (
            "DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_DEFINED_NO_RUNTIME_SCENARIO_PLANNER_OR_OPTIMIZATION"
        )

    def test_design_scenario_policy_feasibility_runtime_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DESIGN-SCENARIO-POLICY-FEASIBILITY-RUNTIME-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001"
        assert lane["next_artifact"] == "DESIGN_CELL_STRUCTURE_RUNTIME_001"
        assert "INV-DESIGN-SCENARIO-POLICY-FEASIBILITY-RUNTIME-001" in lane["resolved_investigations"]

    def test_design_scenario_policy_feasibility_runtime_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-DESIGN-SCENARIO-POLICY-FEASIBILITY-RUNTIME-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001"
        assert inv.current_decision == (
            "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_IMPLEMENTED_FOR_PROVIDED_SCENARIOS_NO_ENUMERATION_OR_OPTIMIZATION"
        )

    def test_design_cell_structure_runtime_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DESIGN-CELL-STRUCTURE-RUNTIME-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DESIGN_CELL_STRUCTURE_RUNTIME_001"
        assert lane["next_artifact"] == "DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001"
        assert "INV-DESIGN-CELL-STRUCTURE-RUNTIME-001" in lane["resolved_investigations"]

    def test_design_cell_structure_runtime_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-DESIGN-CELL-STRUCTURE-RUNTIME-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "DESIGN_CELL_STRUCTURE_RUNTIME_001"
        assert inv.current_decision == (
            "DESIGN_CELL_STRUCTURE_RUNTIME_IMPLEMENTED_FOR_DECLARED_STRUCTURES_NO_ASSIGNMENT_OR_SCENARIO_FEASIBILITY_COMPUTATION"
        )

    def test_design_assignment_feasibility_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DESIGN-ASSIGNMENT-FEASIBILITY-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001"
        assert lane["next_artifact"] == "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001"
        assert "INV-DESIGN-ASSIGNMENT-FEASIBILITY-CONTRACT-001" in lane["resolved_investigations"]

    def test_design_assignment_feasibility_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-DESIGN-ASSIGNMENT-FEASIBILITY-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001"
        assert inv.current_decision == (
            "DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_DEFINED_NO_RUNTIME_ASSIGNMENT_OR_MATCHING"
        )

    def test_design_assignment_feasibility_runtime_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DESIGN-ASSIGNMENT-FEASIBILITY-RUNTIME-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001"
        assert lane["next_artifact"] == "METHOD_SUITABILITY_HANDOFF_CONTRACT_001"
        assert "INV-DESIGN-ASSIGNMENT-FEASIBILITY-RUNTIME-001" in lane["resolved_investigations"]

    def test_design_assignment_feasibility_runtime_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-DESIGN-ASSIGNMENT-FEASIBILITY-RUNTIME-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001"
        assert inv.current_decision == (
            "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_IMPLEMENTED_NO_ASSIGNMENT_OR_MATCHING"
        )

    def test_method_suitability_handoff_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "METHOD-SUITABILITY-HANDOFF-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "METHOD_SUITABILITY_HANDOFF_CONTRACT_001"
        assert lane["next_artifact"] == "METHOD_SUITABILITY_RUNTIME_001"
        assert "INV-METHOD-SUITABILITY-HANDOFF-CONTRACT-001" in lane["resolved_investigations"]

    def test_method_suitability_handoff_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-METHOD-SUITABILITY-HANDOFF-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "METHOD_SUITABILITY_HANDOFF_CONTRACT_001"
        assert inv.current_decision == (
            "METHOD_SUITABILITY_HANDOFF_CONTRACT_DEFINED_NO_METHOD_SELECTION_OR_INFERENCE_AUTHORIZATION"
        )

    def test_method_suitability_runtime_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "METHOD-SUITABILITY-RUNTIME-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "METHOD_SUITABILITY_RUNTIME_001"
        assert lane["next_artifact"] == "DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001"
        assert "INV-METHOD-SUITABILITY-RUNTIME-001" in lane["resolved_investigations"]

    def test_method_suitability_runtime_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-METHOD-SUITABILITY-RUNTIME-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "METHOD_SUITABILITY_RUNTIME_001"
        assert inv.current_decision == (
            "METHOD_SUITABILITY_RUNTIME_IMPLEMENTED_REVIEW_CLASSIFICATION_ONLY_NO_ESTIMATOR_OR_INFERENCE_AUTHORIZATION"
        )

    def test_design_assignment_runtime_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DESIGN-ASSIGNMENT-RUNTIME-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001"
        assert lane["next_artifact"] == "DESIGN_ASSIGNMENT_RUNTIME_001"
        assert "INV-DESIGN-ASSIGNMENT-RUNTIME-CONTRACT-001" in lane["resolved_investigations"]

    def test_design_assignment_runtime_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-DESIGN-ASSIGNMENT-RUNTIME-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001"
        assert inv.current_decision == (
            "DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_DEFINED_NO_ASSIGNMENT_GENERATION_OR_RANDOMIZATION"
        )

    def test_design_assignment_runtime_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DESIGN-ASSIGNMENT-RUNTIME-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DESIGN_ASSIGNMENT_RUNTIME_001"
        assert lane["next_artifact"] == "READOUT_METHOD_GOVERNANCE_CONTRACT_001"
        assert "INV-DESIGN-ASSIGNMENT-RUNTIME-001" in lane["resolved_investigations"]

    def test_design_assignment_runtime_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-DESIGN-ASSIGNMENT-RUNTIME-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "DESIGN_ASSIGNMENT_RUNTIME_001"
        assert inv.current_decision == (
            "DESIGN_ASSIGNMENT_RUNTIME_IMPLEMENTED_DETERMINISTIC_EXPLICIT_POOL_ASSIGNMENT_ONLY_NO_MATCHING_OR_RANDOMIZATION"
        )

    def test_readout_method_governance_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "READOUT-METHOD-GOVERNANCE-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "READOUT_METHOD_GOVERNANCE_CONTRACT_001"
        assert lane["next_artifact"] == "READOUT_PLAN_CONTRACT_001"
        assert "INV-READOUT-METHOD-GOVERNANCE-CONTRACT-001" in lane["resolved_investigations"]

    def test_readout_method_governance_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-READOUT-METHOD-GOVERNANCE-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "READOUT_METHOD_GOVERNANCE_CONTRACT_001"
        assert inv.current_decision == (
            "READOUT_METHOD_GOVERNANCE_CONTRACT_DEFINED_NO_ESTIMATOR_EXECUTION_OR_CAUSAL_CLAIM_AUTHORIZATION"
        )

    def test_readout_plan_contract_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "READOUT-PLAN-CONTRACT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "READOUT_PLAN_CONTRACT_001"
        assert lane["next_artifact"] == "READOUT_PLAN_RUNTIME_001"
        assert "INV-READOUT-PLAN-CONTRACT-001" in lane["resolved_investigations"]

    def test_readout_plan_contract_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-READOUT-PLAN-CONTRACT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "READOUT_PLAN_CONTRACT_001"
        assert inv.current_decision == (
            "READOUT_PLAN_CONTRACT_DEFINED_NO_ESTIMATOR_EXECUTION_OR_CLAIM_AUTHORIZATION"
        )

    def test_readout_plan_runtime_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "READOUT-PLAN-RUNTIME-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "READOUT_PLAN_RUNTIME_001"
        assert lane["next_artifact"] == "ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001"
        assert "INV-READOUT-PLAN-RUNTIME-001" in lane["resolved_investigations"]

    def test_readout_plan_runtime_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-READOUT-PLAN-RUNTIME-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "READOUT_PLAN_RUNTIME_001"
        assert inv.current_decision == (
            "READOUT_PLAN_RUNTIME_IMPLEMENTED_PLANNING_ONLY_NO_ESTIMATOR_EXECUTION_OR_CLAIM_AUTHORIZATION"
        )

    def test_production_authorization_release_gate_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-PRODUCTION-AUTHORIZATION-RELEASE-GATE-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001"

    def test_scm_production_candidate_validation_implementation_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001"

    def test_scm_production_candidate_validation_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"

    def test_did_conditional_validation_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-DID-CONDITIONAL-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"

    def test_synthetic_did_implementation_readiness_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-SYNTHETIC-DID-IMPLEMENTATION-READINESS-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001"

    def test_method_family_retire_replace_execution_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()["INV-METHOD-FAMILY-RETIRE-REPLACE-EXECUTION-PLAN-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001"

    def test_selection_gate_implementation_plan_investigation_resolved(self) -> None:
        inv = investigations_by_id()[
            "INV-DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-IMPLEMENTATION-PLAN-001"
        ]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == (
            "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001"
        )

    def test_scm_treated_set_placebo_null_calibration_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "SCM-TREATED-SET-PLACEBO-NULL-CALIBRATION-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001"
        assert lane["next_artifact"] == "SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001"
        assert "scm_treated_set_placebo" in lane["artifact_tags"]
        assert "no_downstream_authorization" in lane["artifact_tags"]
