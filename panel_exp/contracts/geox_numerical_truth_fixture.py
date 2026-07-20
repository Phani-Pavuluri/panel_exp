"""Typed, non-authorizing GeoX numerical-truth fixture contracts."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping
class GeoXTruthCertificationStatus(str,Enum): CERTIFIED='certified'; CANDIDATE='candidate'; DIAGNOSTIC_ONLY='diagnostic_only'; RESEARCH_ONLY='research_only'; BLOCKED='blocked'; UNSUPPORTED='unsupported'; STALE='stale'; SUPERSEDED='superseded'
class GeoXTruthFixtureClass(str,Enum):
 SUCCESSFUL_GOVERNED_CANDIDATE_READOUT='successful_governed_candidate_readout'; SUCCESSFUL_CANDIDATE_READOUT_WITH_WARNING='successful_candidate_readout_with_warning'; INFEASIBLE_DESIGN='infeasible_design'; WEAK_MATCHABILITY_DIAGNOSTIC='weak_matchability_diagnostic'; UNSUPPORTED_INFERENCE='unsupported_inference'; DIAGNOSTIC_ONLY_METHOD='diagnostic_only_method'; RESEARCH_ONLY_METHOD='research_only_method'; STALE_OR_INCOMPATIBLE_EVIDENCE='stale_or_incompatible_evidence'; CONFLICTING_EVIDENCE='conflicting_evidence'; MULTICELL_SHARED_CONTROL_BLOCK='multicell_shared_control_block'; CALIBRATION_INCOMPATIBLE_RESULT='calibration_incompatible_result'; SAFE_BLOCKED_READOUT_PACKET='safe_blocked_readout_packet'
@dataclass(frozen=True)
class GeoXTruthTimeWindow: pre_period:str; post_period:str
@dataclass(frozen=True)
class GeoXTruthTolerance: estimate_abs:float=0.01; standard_error_abs:float=0.01; interval_abs:float=0.02
@dataclass(frozen=True)
class GeoXTruthProvenance: source_repo:str; source_commit:str; created_by:str; schema_version:str='1.0.0'
@dataclass(frozen=True)
class GeoXTruthDatasetSpec: dataset_version:str; panel_grain:str; geo_scope:str; treatment_units:tuple[str,...]; control_units:tuple[str,...]
@dataclass(frozen=True)
class GeoXTruthReadoutExpectation: point_estimate:float|None; standard_error:float|None; confidence_interval:tuple[float,float]|None; uncertainty_semantics:str; feasibility_status:str; design_status:str; assignment_status:str; readout_status:str; blocked_reasons:tuple[str,...]; warnings:tuple[str,...]
@dataclass(frozen=True)
class GeoXTruthCalibrationCompatibility: status:str; reasons:tuple[str,...]=()
@dataclass(frozen=True)
class GeoXMIPHandoffExpectation: status:str; artifact_kind:str; required_fields:tuple[str,...]=()
@dataclass(frozen=True)
class GeoXNumericalTruthFixture:
    fixture_id:str; fixture_version:str; dataset_version:str; truth_version:str; fixture_class:str; certification_status:str; design_type:str; method_family:str; instrument_id:str; assignment_seed:int; panel_grain:str; geo_scope:str; time_window:GeoXTruthTimeWindow; kpi:str; estimand:str; treatment_units:tuple[str,...]; control_units:tuple[str,...]; known_lift_absolute:float|None; known_lift_relative:float|None; known_incremental_outcome:float|None; expected_point_estimate:float|None; expected_standard_error:float|None; expected_confidence_interval:tuple[float,float]|None; expected_uncertainty_semantics:str; expected_feasibility_status:str; expected_design_status:str; expected_assignment_status:str; expected_readout_status:str; expected_blocked_reasons:tuple[str,...]; expected_warnings:tuple[str,...]; calibration_compatibility:GeoXTruthCalibrationCompatibility; mip_handoff_expectation:GeoXMIPHandoffExpectation; tolerances:GeoXTruthTolerance; provenance:GeoXTruthProvenance
def validate_geox_numerical_truth_fixture(f):
 e=[]
 for n in ('fixture_id','fixture_version','dataset_version','truth_version','design_type','method_family','instrument_id','panel_grain','kpi','estimand'):
  if not getattr(f,n): e.append('missing_'+n)
 if f.fixture_class not in {x.value for x in GeoXTruthFixtureClass}:e.append('invalid_fixture_class')
 if f.certification_status not in {x.value for x in GeoXTruthCertificationStatus}:e.append('invalid_certification_status')
 if not f.time_window:e.append('missing_time_window')
 if f.expected_confidence_interval is not None and (len(f.expected_confidence_interval)!=2 or f.expected_confidence_interval[0]>f.expected_confidence_interval[1]):e.append('invalid_confidence_interval')
 if min(f.tolerances.estimate_abs,f.tolerances.standard_error_abs,f.tolerances.interval_abs)<0:e.append('invalid_tolerance')
 if not f.provenance:e.append('missing_provenance')
 if not f.calibration_compatibility:e.append('missing_calibration_compatibility')
 if not f.mip_handoff_expectation:e.append('missing_mip_handoff_expectation')
 return tuple(e)
def serialize_geox_numerical_truth_fixture(f):return asdict(f)
def deserialize_geox_numerical_truth_fixture(p):
 d=dict(p); d['time_window']=GeoXTruthTimeWindow(**d['time_window']); d['tolerances']=GeoXTruthTolerance(**d['tolerances']); d['provenance']=GeoXTruthProvenance(**d['provenance']); d['calibration_compatibility']=GeoXTruthCalibrationCompatibility(**d['calibration_compatibility']); d['mip_handoff_expectation']=GeoXMIPHandoffExpectation(**d['mip_handoff_expectation']); return GeoXNumericalTruthFixture(**d)
def _build(cls,i):return GeoXNumericalTruthFixture(i,'1.0','dataset-1','truth-1',cls.value,'candidate','geo_experiment','SCM','SCM_UNIT_JACKKNIFE',i, 'geo_time','fixture_geos',GeoXTruthTimeWindow('pre','post'),'revenue','ATT',('treated',),('control',),0.1,0.01,10.0,0.1,0.02,(0.05,0.15),'standard_error','feasible','ready','not_authorized','diagnostic',(),(),GeoXTruthCalibrationCompatibility('compatible'),GeoXMIPHandoffExpectation('diagnostic_only','readout_packet'),GeoXTruthTolerance(),GeoXTruthProvenance('panel_exp','fixture','certification_plan'))
def build_minimum_geox_truth_fixture_catalog():return tuple(_build(c,i+1) for i,c in enumerate(GeoXTruthFixtureClass))
