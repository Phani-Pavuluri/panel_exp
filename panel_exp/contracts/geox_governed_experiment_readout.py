"""Canonical non-authorizing GeoX analytical readout contract."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any
class GeoXGovernedReadoutStatus(str,Enum): SUCCESS='success'; WARNING='warning'; STALE='stale'; INCOMPATIBLE='incompatible'; BLOCKED='blocked'; FAILED='failed'
class GeoXHandoffEligibilityStatus(str,Enum): ELIGIBLE='eligible_for_compatibility_evaluation'; INELIGIBLE='ineligible_for_calibration_handoff'; BLOCKED='blocked_for_handoff'
class GeoXFreshnessStatus(str,Enum): FRESH='fresh'; STALE='stale'; UNKNOWN='unknown'
class GeoXUncertaintySemantics(str,Enum): STANDARD_ERROR='standard_error'; CONFIDENCE_INTERVAL='confidence_interval'; NONE='none'
@dataclass(frozen=True)
class GeoXReadoutAuthorizationFlags: production_inference:bool=False; assignment:bool=False; causal_readout:bool=False; calibration_signal_export:bool=False; experiment_evidence_export:bool=False; trust_report:bool=False; decision_surface:bool=False; recommendation_contract:bool=False; llm_decisioning:bool=False; budget_optimization:bool=False
@dataclass(frozen=True)
class GeoXReadoutLineage: fixture_id:str; dataset_version:str; truth_version:str; upstream_artifacts:tuple[str,...]=()
@dataclass(frozen=True)
class GeoXReadoutProvenance: source_repo:str; source_commit:str; producer_package_version:str; created_by:str
@dataclass(frozen=True)
class GeoXReadoutReplayMetadata: assignment_seed:int; replay_version:str; deterministic:bool=True
@dataclass(frozen=True)
class GeoXGovernedExperimentReadout:
 readout_id:str; readout_version:str; artifact_version:str; producer_package_version:str; producer_commit:str; experiment_id:str; fixture_id:str; dataset_version:str; truth_version:str; kpi:str; kpi_units:str; estimand:str; effect_scale:str; effect_estimate:float|None; absolute_lift:float|None; relative_lift:float|None; incremental_outcome:float|None; channel:str; tactic:str; geography_scope:str; geo_grain:str; time_window:str; pre_period:str; post_period:str; freshness_status:str; uncertainty_available:bool; standard_error:float|None; confidence_interval:tuple[float,float]|None; interval_semantics:str; method_family:str; instrument_id:str; design_type:str; feasibility_status:str; method_status:str; readout_status:str; handoff_eligibility_status:str; warnings:tuple[str,...]; blocked_reasons:tuple[str,...]; failure_reasons:tuple[str,...]; lineage:GeoXReadoutLineage; provenance:GeoXReadoutProvenance; replay_metadata:GeoXReadoutReplayMetadata; authorization_flags:GeoXReadoutAuthorizationFlags
def validate_geox_governed_experiment_readout(r):
 e=[]
 for n in ('readout_id','readout_version','artifact_version','experiment_id','fixture_id','dataset_version','truth_version','kpi','estimand','effect_scale'): 
  if not getattr(r,n): e.append('missing_'+n)
 if r.readout_status not in {x.value for x in GeoXGovernedReadoutStatus}: e.append('invalid_readout_status')
 if r.handoff_eligibility_status not in {x.value for x in GeoXHandoffEligibilityStatus}: e.append('invalid_handoff_eligibility_status')
 if r.readout_status in {'blocked','failed'} and not (r.blocked_reasons or r.failure_reasons): e.append('missing_blocked_or_failure_reasons')
 if r.confidence_interval is not None and len(r.confidence_interval)!=2: e.append('invalid_confidence_interval')
 if any(asdict(r.authorization_flags).values()): e.append('unsafe_production_authorization_claim')
 return tuple(e)
def serialize_geox_governed_experiment_readout(r): return asdict(r)
def deserialize_geox_governed_experiment_readout(p):
 d=dict(p); d['lineage']=GeoXReadoutLineage(**d['lineage']); d['provenance']=GeoXReadoutProvenance(**d['provenance']); d['replay_metadata']=GeoXReadoutReplayMetadata(**d['replay_metadata']); d['authorization_flags']=GeoXReadoutAuthorizationFlags(**d['authorization_flags']); return GeoXGovernedExperimentReadout(**d)
def _example(status):
 blocked=() if status not in ('blocked','failed') else ('governed_blocker',); return GeoXGovernedExperimentReadout('readout-'+status,'1.0','1.0','1.0','commit','experiment-1','fixture-1','dataset-1','truth-1','revenue','currency','ATT','absolute',None if blocked else .1,None if blocked else .1,None if blocked else .01,None if blocked else 10,'channel','tactic','fixture_geos','geo','pre-post','pre','post','stale' if status=='stale' else 'fresh',not bool(blocked),None if blocked else .02,None if blocked else (.05,.15),'standard_error','SCM','instrument','geo_experiment','feasible','candidate',status,'blocked_for_handoff' if blocked else 'eligible_for_compatibility_evaluation',(),blocked,blocked,GeoXReadoutLineage('fixture-1','dataset-1','truth-1'),GeoXReadoutProvenance('panel_exp','commit','1.0','contract'),GeoXReadoutReplayMetadata(1,'1.0'),GeoXReadoutAuthorizationFlags())
def build_example_geox_success_readout(): return _example('success')
def build_example_geox_warning_readout(): return _example('warning')
def build_example_geox_stale_readout(): return _example('stale')
def build_example_geox_incompatible_readout(): return _example('incompatible')
def build_example_geox_blocked_readout(): return _example('blocked')
def build_example_geox_failed_readout(): return _example('failed')
