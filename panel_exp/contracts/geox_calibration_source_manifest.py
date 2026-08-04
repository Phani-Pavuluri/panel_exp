from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from .geox_governed_experiment_readout import (
    deserialize_geox_governed_experiment_readout,
    serialize_geox_governed_experiment_readout,
    validate_geox_governed_experiment_readout,
)

TOP_KEYS = {'schema_version','record_version','case_count','source_repository','source_fixture_checkpoint_sha','source_tree_base_sha','synthetic_fixture_time_scope','mmm_compatibility_emitted','calibration_signal_emitted','production_authorized','records'}
RECORD_KEYS = {'fixture_id','evidence_artifact_id','source_readout_id','experiment_id','dataset_version','truth_version','governed_readout_path','governed_readout_sha256','source_truth_path','source_truth_sha256','replay_path','replay_sha256','fixture_class','certification_status','mip_handoff_expectation','kpi','kpi_units','estimand','effect_scale','channel','tactic','geography_scope','geo_grain','time_window','pre_period','post_period','effect_estimate','absolute_lift','relative_lift','incremental_outcome','uncertainty_available','standard_error','confidence_interval','interval_semantics','method_family','method_status','instrument_id','design_type','feasibility_status','readout_status','freshness_status','handoff_eligibility_status','warnings','blocked_reasons','failure_reasons','lineage','provenance','replay_metadata','producer_package_version','producer_commit','authorization_flags','time_window_start','time_window_end','produced_at','freshness_evaluated_at','synthetic_fixture_time_scope'}
AUTH_KEYS = {'production_inference','assignment','causal_readout','calibration_signal_export','experiment_evidence_export','trust_report','decision_surface','recommendation_contract','llm_decisioning','budget_optimization'}
CASES = {'geox_truth_bayesian_tbr_research_only_001','geox_truth_calibration_incompatible_001','geox_truth_conflicting_evidence_001','geox_truth_did_candidate_warning_001','geox_truth_infeasible_preperiod_001','geox_truth_multicell_shared_control_block_001','geox_truth_safe_blocked_readout_001','geox_truth_scm_candidate_clean_001','geox_truth_stale_incompatible_evidence_001','geox_truth_tbrridge_diagnostic_only_001','geox_truth_unsupported_inference_001','geox_truth_weak_matchability_001'}
SHA = re.compile(r'^[0-9a-f]{64}$')
PROHIBITED = {'source_readout','source_replay','calibration_compatibility','method_eligibility_status','compatibility_status','target_model_id','calibration_weight','calibration_signal','CalibrationSignal','experiment_evidence','ExperimentEvidence','trust_report','TrustReport','decision_surface','DecisionSurface','recommendation','optimization'}

class GeoXCalibrationSourceManifestValidationError(ValueError):
    def __init__(self, errors: tuple[str, ...]):
        self.errors = errors
        super().__init__('; '.join(errors))

def _string(value: object) -> bool:
    return isinstance(value, str) and bool(value)

def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ', value): return None
    try: return datetime.fromisoformat(value[:-1] + '+00:00')
    except ValueError: return None

def validate_geox_calibration_source_manifest(payload: object) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(payload, dict): return ('manifest:not_object',)
    errors += [f'manifest:missing_key:{k}' for k in sorted(TOP_KEYS - payload.keys())]
    errors += [f'manifest:extra_key:{k}' for k in sorted(payload.keys() - TOP_KEYS)]
    expected = {'schema_version':'geox_calibration_source_manifest_v1','record_version':'1.0.0','case_count':12,'source_repository':'Phani-Pavuluri/panel_exp','source_fixture_checkpoint_sha':'860182386c39f487747de5f43e67a31e9978e57c','source_tree_base_sha':'7f829395bc305550ea1311421a4181dafed795b8','synthetic_fixture_time_scope':True,'mmm_compatibility_emitted':False,'calibration_signal_emitted':False,'production_authorized':False}
    for key, value in expected.items():
        if key in payload and payload[key] != value: errors.append(f'manifest:invalid_value:{key}')
    records = payload.get('records')
    if not isinstance(records, list): return tuple(errors + ['manifest:invalid_type:records'])
    ids = [r.get('fixture_id') if isinstance(r, dict) else None for r in records]
    if len(records) != 12 or set(ids) != CASES or len(set(ids)) != 12: errors.append('manifest:case_set_mismatch')
    if all(isinstance(value, str) for value in ids) and ids != sorted(ids): errors.append('manifest:records_not_sorted')
    for index, record in enumerate(records):
        if not isinstance(record, dict): errors.append(f'record:{index}:invalid_type'); continue
        fid = record.get('fixture_id', str(index))
        errors += [f'record:{index}:missing_key:{k}' for k in sorted(RECORD_KEYS-record.keys())]
        errors += [f'record:{fid}:extra_key:{k}' for k in sorted(record.keys()-RECORD_KEYS)]
        if set(record) != RECORD_KEYS: continue
        for key in ('fixture_id','evidence_artifact_id','source_readout_id','experiment_id','dataset_version','truth_version','fixture_class','certification_status','kpi','kpi_units','estimand','effect_scale','channel','tactic','geography_scope','geo_grain','time_window','pre_period','post_period','interval_semantics','method_family','method_status','instrument_id','design_type','feasibility_status','readout_status','freshness_status','handoff_eligibility_status','producer_package_version','producer_commit','governed_readout_path','source_truth_path','replay_path','time_window_start','time_window_end','produced_at','freshness_evaluated_at'):
            if not _string(record[key]): errors.append(f'record:{fid}:invalid_type:{key}')
        if record['evidence_artifact_id'] != f'geox-evidence-{fid}-v1' or record['experiment_id'] != fid: errors.append(f'record:{fid}:invalid_identity')
        for key in ('governed_readout_sha256','source_truth_sha256','replay_sha256'):
            if not isinstance(record[key], str) or not SHA.fullmatch(record[key]): errors.append(f'record:{fid}:invalid_type:{key}')
        for key in ('warnings','blocked_reasons','failure_reasons'):
            if not isinstance(record[key], list) or not all(isinstance(v,str) for v in record[key]): errors.append(f'record:{fid}:invalid_type:{key}')
        for key in ('mip_handoff_expectation','lineage','provenance','replay_metadata','authorization_flags'):
            if not isinstance(record[key], dict): errors.append(f'record:{fid}:invalid_type:{key}')
        if isinstance(record['authorization_flags'], dict) and (set(record['authorization_flags']) != AUTH_KEYS or any(v is not False for v in record['authorization_flags'].values())): errors.append(f'record:{fid}:unsafe_authorization')
        if record['freshness_status'] not in {'fresh','stale'}: errors.append(f'record:{fid}:invalid_value:freshness_status')
        times = [_timestamp(record[k]) for k in ('time_window_start','time_window_end','produced_at','freshness_evaluated_at')]
        if any(t is None for t in times): errors.append(f'record:{fid}:invalid_timestamp')
        elif not (times[0] < times[1] <= times[2] <= times[3]): errors.append(f'record:{fid}:invalid_timestamp_order')
        if any(k in record for k in PROHIBITED): errors.append(f'record:{fid}:prohibited_key')
    return tuple(errors)

def _file(root: Path, rel: object, fid: str, kind: str) -> tuple[Path | None, str | None]:
    if not isinstance(rel, str) or not rel or '\\' in rel: return None, f'source:{fid}:unsafe_path:{kind}'
    path = Path(rel)
    if path.is_absolute() or '..' in path.parts: return None, f'source:{fid}:unsafe_path:{kind}'
    resolved = (root / path).resolve()
    if root.resolve() not in resolved.parents or not resolved.is_file(): return None, f'source:{fid}:missing_file:{kind}'
    return resolved, None

def validate_geox_calibration_source_manifest_sources(payload: object, *, source_root: Path) -> tuple[str, ...]:
    errors = list(validate_geox_calibration_source_manifest(payload))
    if errors or not isinstance(payload, dict): return tuple(errors)
    try: source_manifest = json.loads((source_root/'manifest.json').read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError): return tuple(errors + ['source:manifest:invalid_json'])
    cases = {c.get('case_id'): c for c in source_manifest.get('cases', [])} if isinstance(source_manifest, dict) else {}
    for record in payload['records']:
        fid = record['fixture_id']; case = cases.get(fid)
        if case is None: errors.append(f'source:{fid}:case_missing'); continue
        for kind in ('governed_readout','source_truth','replay'):
            path, reason = _file(source_root, record[f'{kind}_path'], fid, kind)
            if reason: errors.append(reason); continue
            if record[f'{kind}_path'] != case[kind]: errors.append(f'source:{fid}:field_mismatch:{kind}_path')
            if hashlib.sha256(path.read_bytes()).hexdigest() != record[f'{kind}_sha256']: errors.append(f'source:{fid}:checksum_mismatch:{kind}')
        try:
            readout = json.loads((source_root/record['governed_readout_path']).read_text(encoding='utf-8'))
            truth = json.loads((source_root/record['source_truth_path']).read_text(encoding='utf-8'))
            replay = json.loads((source_root/record['replay_path']).read_text(encoding='utf-8'))
            parsed = deserialize_geox_governed_experiment_readout(readout)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, KeyError):
            errors.append(f'source:{fid}:invalid_json'); continue
        if validate_geox_governed_experiment_readout(parsed): errors.append(f'source:{fid}:invalid_governed_readout')
        canonical = serialize_geox_governed_experiment_readout(parsed)
        for key in ('readout_id','experiment_id','dataset_version','truth_version','kpi','kpi_units','estimand','effect_scale','channel','tactic','geography_scope','geo_grain','time_window','pre_period','post_period','effect_estimate','absolute_lift','relative_lift','incremental_outcome','uncertainty_available','standard_error','confidence_interval','interval_semantics','method_family','method_status','instrument_id','design_type','feasibility_status','readout_status','freshness_status','handoff_eligibility_status','warnings','blocked_reasons','failure_reasons','lineage','provenance','replay_metadata','producer_package_version','producer_commit','authorization_flags'):
            target = 'source_readout_id' if key == 'readout_id' else key
            if record[target] != canonical[key]: errors.append(f'source:{fid}:field_mismatch:{target}')
        for key in ('fixture_id','fixture_class','certification_status','mip_handoff_expectation'):
            if record[key] != truth.get(key): errors.append(f'source:{fid}:source_truth_mismatch:{key}')
        if replay.get('case_id') != fid or replay.get('deterministic') is not True: errors.append(f'source:{fid}:replay_mismatch:case_id')
    return tuple(errors)

def load_and_validate_geox_calibration_source_manifest(manifest_path: Path, *, source_root: Path) -> dict[str, object]:
    try: payload = json.loads(manifest_path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc: raise GeoXCalibrationSourceManifestValidationError(('manifest:invalid_json',)) from exc
    errors = validate_geox_calibration_source_manifest_sources(payload, source_root=source_root)
    if errors: raise GeoXCalibrationSourceManifestValidationError(errors)
    return payload
