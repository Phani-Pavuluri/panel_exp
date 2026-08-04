"""Strict producer-owned calibration source manifest records."""
from dataclasses import dataclass, fields, asdict
from datetime import datetime
import hashlib, json
from pathlib import Path
from typing import Any, Mapping, Tuple, Optional
SCHEMA="geox_calibration_handoff_source_v1"; VERSION="1.0.0"; CHECKPOINT="860182386c39f487747de5f43e67a31e9978e57c"; BASE="80dbe14c6b2ce74b33a2b776c5e567afba582bf5"
@dataclass(frozen=True)
class GeoXCalibrationHandoffSourceRecord:
 schema_version:str; record_version:str; handoff_source_id:str; evidence_artifact_id:str; source_readout_id:str; source_readout_version:str; source_artifact_version:str; experiment_id:str; fixture_id:str; dataset_version:str; truth_version:str; source_repository:str; source_fixture_checkpoint_sha:str; task_source_tree_base_sha:str; governed_readout_path:str; governed_readout_sha256:str; source_truth_path:str; source_truth_sha256:str; replay_path:str; replay_sha256:str; fixture_class:str; certification_status:str; mip_handoff_expectation:dict; kpi:str; kpi_units:str; estimand:str; effect_scale:str; channel:str; tactic:str; geography_scope:str; geo_grain:str; time_window:str; pre_period:str; post_period:str; effect_estimate:object; absolute_lift:object; relative_lift:object; incremental_outcome:object; uncertainty_available:bool; standard_error:object; confidence_interval:object; interval_semantics:str; time_window_start:str; time_window_end:str; produced_at:str; freshness_evaluated_at:str; synthetic_fixture_time_scope:bool; method_family:str; source_method_status:str; instrument_id:str; design_type:str; feasibility_status:str; readout_status:str; freshness_status:str; handoff_eligibility_status:str; warnings:list; blocked_reasons:list; failure_reasons:list; lineage:dict; provenance:dict; replay_metadata:dict; producer_package_version:str; embedded_producer_commit:str; authorization_flags:dict
 @classmethod
 def parse(cls,data):
  if not isinstance(data,dict): raise ValueError('record must be object')
  names={f.name for f in fields(cls)}; missing=names-data.keys(); extra=set(data)-names
  if missing or extra: raise ValueError('missing/extra fields')
  if data['schema_version']!=SCHEMA or data['record_version']!=VERSION: raise ValueError('unsupported version')
  for key in ('time_window_start','time_window_end','produced_at','freshness_evaluated_at'):
   dt=datetime.fromisoformat(data[key].replace('Z','+00:00'))
   if dt.tzinfo is None or dt.utcoffset().total_seconds()!=0: raise ValueError('timestamp must be UTC')
  if not (data['time_window_start']<data['time_window_end']<=data['produced_at']<=data['freshness_evaluated_at']): raise ValueError('temporal ordering')
  return cls(**data)
 def validate(self):
  if self.source_fixture_checkpoint_sha!=CHECKPOINT or self.task_source_tree_base_sha!=BASE: return ('invalid provenance',)
  if any(self.authorization_flags.values()): return ('unsafe authorization',)
  return ()
 def to_dict(self): return asdict(self)
def serialize(record): return record.to_dict()
def deserialize(data): return GeoXCalibrationHandoffSourceRecord.parse(data)
def checksum(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
