"""Non-authorizing, provenance-complete GeoX calibration source fixture."""
from dataclasses import asdict, dataclass
import hashlib, json, re
from pathlib import Path
from typing import Any

SOURCE_COMMIT="860182386c39f487747de5f43e67a31e9978e57c"
ELIGIBILITY={"candidate","diagnostic_only","research_only","blocked","unsupported"}
@dataclass(frozen=True)
class GeoXCalibrationHandoffSourceRecord:
 schema_version:str; record_version:str; handoff_source_id:str; evidence_artifact_id:str
 fixture_id:str; readout_id:str; experiment_id:str; dataset_version:str; truth_version:str
 source_commit:str; source_repository:str; task_authorization_base:str
 governed_readout_path:str; source_truth_path:str; replay_path:str
 governed_readout_sha256:str; source_truth_sha256:str; replay_sha256:str
 method_family:str; method_status:str; instrument_id:str; design_type:str; feasibility_status:str
 method_eligibility_status:str; readout_status:str; handoff_eligibility_status:str
 freshness_status:str; time_window_start:str; time_window_end:str; produced_at:str; freshness_evaluated_at:str
 synthetic_fixture_time_scope:bool; payload:dict[str,Any]
 def to_dict(self): return asdict(self)
 @classmethod
 def from_dict(cls,d): return cls(**d)
 def validate(self):
  errors=[]
  if self.source_commit!=SOURCE_COMMIT or not re.fullmatch(r'[0-9a-f]{40}',self.source_commit): errors.append('invalid_source_commit')
  if self.method_eligibility_status not in ELIGIBILITY: errors.append('invalid_method_eligibility')
  for p,h in ((self.governed_readout_path,self.governed_readout_sha256),(self.source_truth_path,self.source_truth_sha256),(self.replay_path,self.replay_sha256)):
   if not re.fullmatch(r'[0-9a-f]{64}',h): errors.append('invalid_checksum')
  if not self.synthetic_fixture_time_scope: errors.append('not_synthetic_fixture_scope')
  if self.time_window_start>=self.time_window_end or self.produced_at<self.time_window_end or self.freshness_evaluated_at<self.produced_at: errors.append('invalid_temporal_order')
  if any(self.payload.get('authorization_flags',{}).values()): errors.append('unsafe_authorization')
  return tuple(errors)
def checksum(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def serialize(record): return record.to_dict()
def deserialize(data): return GeoXCalibrationHandoffSourceRecord.from_dict(data)
