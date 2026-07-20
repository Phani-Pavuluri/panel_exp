"""Typed boundary for a future non-authorizing policy adapter."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping

class PolicyAdapterFailureCode(str, Enum):
    POLICY_UNKNOWN_METHOD_FAMILY="policy_unknown_method_family"; POLICY_MISSING_REQUIRED_METADATA="policy_missing_required_metadata"; POLICY_RELEASE_GATE_MISSING="policy_release_gate_missing"; POLICY_DOWNSTREAM_EXPORT_REQUESTED="policy_downstream_export_requested"; POLICY_MULTICELL_DEPENDENCE_UNRESOLVED="policy_multicell_dependence_unresolved"; POLICY_MULTIPLICITY_UNRESOLVED="policy_multiplicity_unresolved"; POLICY_METHOD_RESEARCH_ONLY="policy_method_research_only"; POLICY_METHOD_DIAGNOSTIC_ONLY="policy_method_diagnostic_only"; POLICY_METHOD_RETIRED_OR_REPLACED="policy_method_retired_or_replaced"; POLICY_METHOD_REMEDIATION_REQUIRED="policy_method_remediation_required"; POLICY_METHOD_NOT_PRODUCTION_AUTHORIZED="policy_method_not_production_authorized"; POLICY_ASSIGNMENT_NOT_AUTHORIZED="policy_assignment_not_authorized"; POLICY_READOUT_NOT_AUTHORIZED="policy_readout_not_authorized"; POLICY_CALIBRATION_SIGNAL_EXPORT_NOT_AUTHORIZED="policy_calibration_signal_export_not_authorized"; POLICY_MIP_EXPERIMENT_EVIDENCE_EXPORT_NOT_AUTHORIZED="policy_mip_experiment_evidence_export_not_authorized"; POLICY_TRUST_REPORT_PRODUCTION_ASSEMBLY_NOT_AUTHORIZED="policy_trust_report_production_assembly_not_authorized"; POLICY_DECISION_SURFACE_NOT_AUTHORIZED="policy_decision_surface_not_authorized"; POLICY_RECOMMENDATION_CONTRACT_NOT_AUTHORIZED="policy_recommendation_contract_not_authorized"; POLICY_LLM_DECISIONING_NOT_AUTHORIZED="policy_llm_decisioning_not_authorized"; POLICY_BUDGET_OPTIMIZATION_NOT_AUTHORIZED="policy_budget_optimization_not_authorized"; POLICY_UNSUPPORTED_KPI_OUTCOME="policy_unsupported_kpi_outcome"; POLICY_UNSUPPORTED_PANEL_GRAIN="policy_unsupported_panel_grain"; POLICY_UNSAFE_PRODUCTION_CLAIM="policy_unsafe_production_claim"
class PolicyAdapterWarningCode(str, Enum):
    SHADOW_VALIDATION_ONLY="shadow_validation_only"; NO_PRODUCTION_AUTHORIZATION="no_production_authorization"; RELEASE_GATE_REQUIRED_BEFORE_PRODUCTION="release_gate_required_before_production"; METHOD_CANDIDATE_GATED="method_candidate_gated"; DIAGNOSTIC_ONLY_ROUTE="diagnostic_only_route"; RESEARCH_ONLY_ROUTE="research_only_route"; DOWNSTREAM_EXPORT_BLOCKED="downstream_export_blocked"; MULTICELL_VALIDATION_REQUIRED="multicell_validation_required"; METHOD_READINESS_REVIEW_REQUIRED="method_readiness_review_required"
class PolicyRuleId(str, Enum):
    SCM_SINGLE_CELL_CANDIDATE="scm_single_cell_candidate"; DID_ASSUMPTIONS_PRESENT="did_assumptions_present"; DID_ASSUMPTIONS_MISSING="did_assumptions_missing"; AUGSYNTH_REMEDIATION_REQUIRED="augsynth_remediation_required"; TBRRIDGE_DIAGNOSTIC_ONLY="tbrridge_diagnostic_only"; UNKNOWN_METHOD_BLOCKED="unknown_method_blocked"
@dataclass(frozen=True)
class PolicyAdapterInput:
    fixture_id:str; metadata:Mapping[str,Any]; governance_state:Mapping[str,Any]
@dataclass(frozen=True)
class PolicyAdapterDiagnostics:
    fixture_id:str; rule_ids_applied:tuple[str,...]; method_family_status:str; release_gate_state:str; downstream_target:str; metadata_completeness:bool; failure_registry_hits:tuple[str,...]; blocked_reason_codes:tuple[str,...]; warning_codes:tuple[str,...]; next_best_alternative_codes:tuple[str,...]; unsafe_claims:tuple[str,...]; notes:tuple[str,...]=()
@dataclass(frozen=True)
class PolicyAdapterObservedOutcome:
    route_status:str; blocked_reasons:tuple[str,...]; warnings:tuple[str,...]; next_best_alternatives:tuple[str,...]; forbidden_claims:tuple[str,...]; readiness_flags_all_false:bool=True; authorization_flags_all_false:bool=True; diagnostics:PolicyAdapterDiagnostics|None=None
@dataclass(frozen=True)
class PolicyAdapterFailure:
    fixture_id:str; code:str; message:str; recoverable:bool=True
def validate_policy_adapter_input(x): return ("policy_missing_required_metadata",) if not x.fixture_id or not x.metadata else ()
def validate_policy_adapter_observed_outcome(x):
    e=[]
    if not x.readiness_flags_all_false:e.append('unsafe_readiness_flags_not_false')
    if not x.authorization_flags_all_false:e.append('unsafe_authorization_flags_not_false')
    if x.forbidden_claims:e.append(PolicyAdapterFailureCode.POLICY_UNSAFE_PRODUCTION_CLAIM.value)
    return tuple(e)
def serialize_policy_adapter_input(x): return asdict(x)
def serialize_policy_adapter_observed_outcome(x): return asdict(x)
def serialize_policy_adapter_diagnostics(x): return asdict(x)
def serialize_policy_adapter_failure(x): return asdict(x)
def build_safe_policy_adapter_input(fixture_id='fixture_scm_candidate_single_cell'): return PolicyAdapterInput(fixture_id,{'method_family':'scm'}, {'release_gate_state':'present_not_authorized'})
def build_safe_policy_adapter_observed_outcome(): return PolicyAdapterObservedOutcome('shadow_eligible_candidate',(),('shadow_validation_only','no_production_authorization'),('scm',),(),True,True,None)
