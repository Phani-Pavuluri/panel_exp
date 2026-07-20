"""Typed, non-executing contracts for future shadow-validation harness output."""
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping

class ShadowValidationFailureClassification(str, Enum):
    CONTRACT_VALIDATION_FAILURE="contract_validation_failure"; SELECTION_POLICY_MISMATCH="selection_policy_mismatch"; FIXTURE_EXPECTATION_MISMATCH="fixture_expectation_mismatch"; MISSING_REQUIRED_FIXTURE="missing_required_fixture"; FORBIDDEN_CLAIM_EMITTED="forbidden_claim_emitted"; READINESS_FLAG_VIOLATION="readiness_flag_violation"; AUTHORIZATION_FLAG_VIOLATION="authorization_flag_violation"; RELEASE_GATE_VIOLATION="release_gate_violation"; METHOD_READINESS_VIOLATION="method_readiness_violation"; ENVIRONMENT_EXECUTION_FAILURE="environment_execution_failure"; SERIALIZATION_FAILURE="serialization_failure"; NONE="none"
@dataclass(frozen=True)
class ShadowValidationResultRecord:
    fixture_id:str; requested_method_family:str; requested_estimator:str; requested_inference:str; downstream_use_target:str; expected_route_status:str; observed_route_status:str; route_status_match:bool; expected_blocked_reasons:tuple[str,...]; observed_blocked_reasons:tuple[str,...]; blocked_reasons_match:bool; expected_warnings:tuple[str,...]; observed_warnings:tuple[str,...]; warnings_match:bool; expected_next_best_alternatives:tuple[str,...]; observed_next_best_alternatives:tuple[str,...]; next_best_alternatives_match:bool; expected_forbidden_claims:tuple[str,...]; observed_forbidden_claims:tuple[str,...]; forbidden_claims_absent:bool; readiness_flags_all_false:bool; authorization_flags_all_false:bool; validation_errors:tuple[str,...]; failure_classification:str; passed:bool; notes:tuple[str,...]=()
@dataclass(frozen=True)
class ShadowValidationAggregateSummary:
    artifact_id:str; fixture_count:int; passed_count:int; failed_count:int; contract_failure_count:int; selection_policy_failure_count:int; fixture_expectation_failure_count:int; environment_failure_count:int; forbidden_claim_failure_count:int; readiness_flag_failure_count:int; authorization_flag_failure_count:int; all_required_fixtures_present:bool; all_forbidden_claims_absent:bool; all_readiness_flags_false:bool; all_authorization_flags_false:bool; safe_to_proceed_to_harness_runtime:bool; safe_to_authorize_production_selector_router:bool=False
@dataclass(frozen=True)
class ShadowValidationFailurePacket:
    fixture_id:str; failure_classification:str; severity:str; expected:Mapping[str,Any]; observed:Mapping[str,Any]; blocked_reasons:tuple[str,...]; warnings:tuple[str,...]; unsafe_claims:tuple[str,...]; recommended_resolution:str; next_safe_artifact:str
@dataclass(frozen=True)
class ShadowValidationHarnessRunManifest:
    artifact_id:str; fixture_contract_artifact_id:str; harness_contract_artifact_id:str; fixture_count:int; run_mode:str; production_authorization:bool=False; selector_runtime_authorized:bool=False; estimator_execution_authorized:bool=False; mip_integration_authorized:bool=False
def _errors(d):
    e=[]
    if not d.get('fixture_id',d.get('artifact_id')): e.append('missing_fixture_id' if 'fixture_id' in d else 'missing_artifact_id')
    return e
def validate_shadow_validation_result_record(r):
    e=_errors(asdict(r))
    if r.failure_classification not in {x.value for x in ShadowValidationFailureClassification}: e.append('invalid_failure_classification')
    if not r.forbidden_claims_absent: e.append('unsafe_forbidden_claims_present')
    if not r.readiness_flags_all_false: e.append('unsafe_readiness_flags_not_false')
    if not r.authorization_flags_all_false: e.append('unsafe_authorization_flags_not_false')
    return tuple(e)
def validate_shadow_validation_aggregate_summary(s):
    e=_errors(asdict(s));
    if s.fixture_count<0: e.append('invalid_fixture_count')
    if s.passed_count+s.failed_count!=s.fixture_count: e.append('invalid_pass_fail_counts')
    if not s.all_readiness_flags_false: e.append('unsafe_readiness_flags_not_false')
    if not s.all_authorization_flags_false: e.append('unsafe_authorization_flags_not_false')
    if s.safe_to_authorize_production_selector_router: e.append('unsafe_safe_to_authorize_production_selector_router')
    return tuple(e)
def validate_shadow_validation_failure_packet(p):
    e=_errors(asdict(p));
    if p.failure_classification not in {x.value for x in ShadowValidationFailureClassification}: e.append('invalid_failure_classification')
    if not p.recommended_resolution: e.append('missing_recommended_resolution')
    if not p.next_safe_artifact: e.append('missing_next_safe_artifact')
    if p.unsafe_claims: e.append('unsafe_forbidden_claims_present')
    return tuple(e)
def validate_shadow_validation_harness_run_manifest(m):
    e=_errors(asdict(m));
    if m.fixture_count<0: e.append('invalid_fixture_count')
    for field,code in [('production_authorization','unsafe_production_authorization_true'),('selector_runtime_authorized','unsafe_selector_runtime_authorized_true'),('estimator_execution_authorized','unsafe_estimator_execution_authorized_true'),('mip_integration_authorized','unsafe_mip_integration_authorized_true')]:
        if getattr(m,field): e.append(code)
    return tuple(e)
def _ser(x): return asdict(x)
serialize_shadow_validation_result_record=_ser; serialize_shadow_validation_aggregate_summary=_ser; serialize_shadow_validation_failure_packet=_ser; serialize_shadow_validation_harness_run_manifest=_ser
def build_passing_shadow_validation_result_record(fixture_id='fixture_scm_candidate_single_cell'):
    return ShadowValidationResultRecord(fixture_id,'scm','default','design_based','diagnostic','shadow_eligible_candidate','shadow_eligible_candidate',True,(),(),True,(),(),True,('scm',),('scm',),True,('lift',),(),True,True,True,(), 'none', True)
def build_valid_shadow_validation_aggregate_summary(fixture_count=12): return ShadowValidationAggregateSummary('shadow-run-001',fixture_count,fixture_count,0,0,0,0,0,0,0,0,True,True,True,True,True,False)
def build_shadow_validation_failure_packet(fixture_id='fixture_aug_synth_remediation_required'): return ShadowValidationFailurePacket(fixture_id,'method_readiness_violation','error',{}, {},('remediation_required',),(),(), 'remediate method', 'METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_RUNTIME_001')
def build_shadow_validation_harness_run_manifest(fixture_count=12): return ShadowValidationHarnessRunManifest('shadow-run-001','METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_FIXTURE_CONTRACT_001','METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_CONTRACT_001',fixture_count,'fixture_only')
