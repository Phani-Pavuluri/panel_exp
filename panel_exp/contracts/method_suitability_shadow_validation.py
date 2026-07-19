"""Stdlib-only fixture contract for method-suitability shadow validation."""
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping

class ShadowRouteStatus(str, Enum):
    SHADOW_ELIGIBLE_CANDIDATE="shadow_eligible_candidate"; SHADOW_ELIGIBLE_AFTER_WARNING="shadow_eligible_after_warning"; SHADOW_DIAGNOSTIC_ONLY="shadow_diagnostic_only"; SHADOW_RESEARCH_ONLY="shadow_research_only"; SHADOW_BLOCKED="shadow_blocked"; SHADOW_RELEASE_GATE_REQUIRED="shadow_release_gate_required"; SHADOW_REMEDIATION_REQUIRED="shadow_remediation_required"; SHADOW_RETIRED_OR_REPLACED="shadow_retired_or_replaced"
class MethodFamily(str, Enum):
    SCM="scm"; DID="did"; SYNTHETIC_DID="synthetic_did"; AUGSYNTH_CVXPY="augsynth_cvxpy"; TBRRIDGE="tbrridge"; CLASSIC_AGGREGATE_TBR="classic_aggregate_tbr"; BAYESIAN_TBR="bayesian_tbr"; TROP="trop"; MULTICELL_SHARED_CONTROL="multicell_shared_control"; UNKNOWN="unknown"
class ReleaseGateState(str, Enum): MISSING="missing"; PRESENT_NOT_AUTHORIZED="present_not_authorized"; AUTHORIZED="authorized"
class DownstreamUseTarget(str, Enum):
    DIAGNOSTIC="diagnostic"; METHOD_SELECTION_SHADOW_VALIDATION="method_selection_shadow_validation"; ASSIGNMENT="assignment"; CAUSAL_READOUT="causal_readout"; CALIBRATION_SIGNAL="calibration_signal"; MIP_EXPERIMENT_EVIDENCE="mip_experiment_evidence"; TRUST_REPORT="trust_report"; DECISION_SURFACE="decision_surface"; RECOMMENDATION_CONTRACT="recommendation_contract"; LLM_DECISIONING="llm_decisioning"; BUDGET_OPTIMIZATION="budget_optimization"

@dataclass(frozen=True)
class ShadowValidationFixtureInput:
    fixture_id:str; design_type:str; experiment_geometry:str; number_of_cells:int; shared_control:bool; assignment_mechanism:str; kpi_outcome_type:str; panel_grain:str; pre_period_adequacy:str; post_period_adequacy:str; donor_control_pool_adequacy:str; observed_diagnostics:Mapping[str,Any]; requested_method_family:str; requested_estimator:str; requested_inference:str; method_promotion_status:str; release_gate_state:str; failure_registry_hits:tuple[str,...]; downstream_use_target:str
@dataclass(frozen=True)
class ExpectedShadowValidationOutcome:
    expected_route_status:str; expected_blocked_reasons:tuple[str,...]; expected_warnings:tuple[str,...]; expected_next_best_alternatives:tuple[str,...]; expected_forbidden_claims:tuple[str,...]; ready_for_production_selector_router:bool=False; ready_for_production_inference:bool=False; ready_for_assignment_authorization:bool=False; ready_for_causal_readout:bool=False; ready_for_calibration_signal_export:bool=False; ready_for_mip_experiment_evidence_export:bool=False; ready_for_trust_report_production_assembly:bool=False; ready_for_decision_surface:bool=False; ready_for_recommendation_contract:bool=False; ready_for_llm_decisioning:bool=False; ready_for_budget_optimization:bool=False
@dataclass(frozen=True)
class ShadowValidationFixture: input:ShadowValidationFixtureInput; expected:ExpectedShadowValidationOutcome

_ROUTES={x.value for x in ShadowRouteStatus}; _EXPORTS={"calibration_signal","mip_experiment_evidence","trust_report","decision_surface","recommendation_contract","llm_decisioning","budget_optimization"}
_READY=("ready_for_production_selector_router","ready_for_production_inference","ready_for_assignment_authorization","ready_for_causal_readout","ready_for_calibration_signal_export","ready_for_mip_experiment_evidence_export","ready_for_trust_report_production_assembly","ready_for_decision_surface","ready_for_recommendation_contract","ready_for_llm_decisioning","ready_for_budget_optimization")
def validate_shadow_validation_fixture(fixture):
    i,e=fixture.input,fixture.expected; errs=[]
    if not i.fixture_id: errs.append("missing_fixture_id")
    if i.number_of_cells<1: errs.append("invalid_number_of_cells")
    if not i.requested_method_family: errs.append("missing_requested_method_family")
    if not e.expected_route_status: errs.append("missing_expected_route_status")
    if e.expected_route_status not in _ROUTES: errs.append("invalid_expected_route_status")
    for f in _READY:
        if getattr(e,f): errs.append("unsafe_"+f)
    if i.downstream_use_target in _EXPORTS and not e.expected_blocked_reasons: errs.append("unsafe_downstream_export_target_requires_blocker")
    return tuple(errs)
def serialize_shadow_validation_fixture(fixture):
    return {"input":asdict(fixture.input),"expected":asdict(fixture.expected)}
def deserialize_shadow_validation_fixture(payload):
    return ShadowValidationFixture(ShadowValidationFixtureInput(**payload["input"]),ExpectedShadowValidationOutcome(**payload["expected"]))
def _fixture(n, family, route, target="diagnostic", blocked=(), warnings=()):
    i=ShadowValidationFixtureInput(n,"panel","single_cell",1,False,"observational","revenue","geo_time","adequate","adequate","adequate",{},family.value,"default","design_based","candidate_gated","present_not_authorized",(),target)
    e=ExpectedShadowValidationOutcome(route.value,blocked,warnings,("scm",),("production_lift","assignment","causal_readout"))
    return ShadowValidationFixture(i,e)
def build_default_shadow_validation_fixtures():
    specs=[("scm_candidate",MethodFamily.SCM,ShadowRouteStatus.SHADOW_ELIGIBLE_CANDIDATE),("did_conditional",MethodFamily.DID,ShadowRouteStatus.SHADOW_ELIGIBLE_AFTER_WARNING),("did_missing",MethodFamily.DID,ShadowRouteStatus.SHADOW_BLOCKED),("augsynth_remediation",MethodFamily.AUGSYNTH_CVXPY,ShadowRouteStatus.SHADOW_REMEDIATION_REQUIRED),("tbrridge_diag",MethodFamily.TBRRIDGE,ShadowRouteStatus.SHADOW_DIAGNOSTIC_ONLY),("classic_retired",MethodFamily.CLASSIC_AGGREGATE_TBR,ShadowRouteStatus.SHADOW_RETIRED_OR_REPLACED),("bayesian_research",MethodFamily.BAYESIAN_TBR,ShadowRouteStatus.SHADOW_RESEARCH_ONLY),("trop_research",MethodFamily.TROP,ShadowRouteStatus.SHADOW_RESEARCH_ONLY),("synthetic_did",MethodFamily.SYNTHETIC_DID,ShadowRouteStatus.SHADOW_RESEARCH_ONLY),("multicell_blocked",MethodFamily.MULTICELL_SHARED_CONTROL,ShadowRouteStatus.SHADOW_BLOCKED),("unknown_method",MethodFamily.UNKNOWN,ShadowRouteStatus.SHADOW_BLOCKED),("downstream_export",MethodFamily.SCM,ShadowRouteStatus.SHADOW_BLOCKED)]
    return tuple(_fixture(*s) for s in specs)
