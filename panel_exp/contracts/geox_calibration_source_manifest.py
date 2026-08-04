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

TOP_KEYS = {'schema_version', 'record_version', 'case_count', 'source_repository', 'source_fixture_checkpoint_sha', 'source_tree_base_sha', 'synthetic_fixture_time_scope', 'mmm_compatibility_emitted', 'calibration_signal_emitted', 'production_authorized', 'records'}
AUTH_KEYS = {'production_inference', 'assignment', 'causal_readout', 'calibration_signal_export', 'experiment_evidence_export', 'trust_report', 'decision_surface', 'recommendation_contract', 'llm_decisioning', 'budget_optimization'}
RECORD_KEYS = {'fixture_id', 'evidence_artifact_id', 'source_readout_id', 'experiment_id', 'dataset_version', 'truth_version', 'governed_readout_path', 'governed_readout_sha256', 'source_truth_path', 'source_truth_sha256', 'replay_path', 'replay_sha256', 'fixture_class', 'certification_status', 'mip_handoff_expectation', 'kpi', 'kpi_units', 'estimand', 'effect_scale', 'channel', 'tactic', 'geography_scope', 'geo_grain', 'time_window', 'pre_period', 'post_period', 'effect_estimate', 'absolute_lift', 'relative_lift', 'incremental_outcome', 'uncertainty_available', 'standard_error', 'confidence_interval', 'interval_semantics', 'method_family', 'method_status', 'instrument_id', 'design_type', 'feasibility_status', 'readout_status', 'freshness_status', 'handoff_eligibility_status', 'warnings', 'blocked_reasons', 'failure_reasons', 'lineage', 'provenance', 'replay_metadata', 'producer_package_version', 'producer_commit', 'authorization_flags', 'time_window_start', 'time_window_end', 'produced_at', 'freshness_evaluated_at', 'synthetic_fixture_time_scope'}
CASES = {'geox_truth_bayesian_tbr_research_only_001', 'geox_truth_calibration_incompatible_001', 'geox_truth_conflicting_evidence_001', 'geox_truth_did_candidate_warning_001', 'geox_truth_infeasible_preperiod_001', 'geox_truth_multicell_shared_control_block_001', 'geox_truth_safe_blocked_readout_001', 'geox_truth_scm_candidate_clean_001', 'geox_truth_stale_incompatible_evidence_001', 'geox_truth_tbrridge_diagnostic_only_001', 'geox_truth_unsupported_inference_001', 'geox_truth_weak_matchability_001'}
PROHIBITED = {'source_readout', 'source_replay', 'calibration_compatibility', 'method_eligibility_status', 'compatibility_status', 'target_model_id', 'calibration_weight', 'calibration_signal', 'CalibrationSignal', 'experiment_evidence', 'ExperimentEvidence', 'trust_report', 'TrustReport', 'decision_surface', 'DecisionSurface', 'recommendation', 'optimization'}
SHA256 = re.compile(r'^[0-9a-f]{64}$')


class GeoXCalibrationSourceManifestValidationError(ValueError):
    def __init__(self, errors: tuple[str, ...]):
        self.errors = errors
        super().__init__('; '.join(errors))


def _string(value: object) -> bool:
    return isinstance(value, str) and bool(value)


def _number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value):
        return None
    try:
        return datetime.fromisoformat(value[:-1] + '+00:00')
    except ValueError:
        return None


def _nested(record: dict[str, object], key: str, expected: set[str], fid: object, errors: list[str]) -> dict[str, object] | None:
    value = record.get(key)
    if not isinstance(value, dict):
        errors.append(f'record:{fid}:invalid_type:{key}')
        return None
    missing = expected - set(value)
    extra = set(value) - expected
    errors.extend(f'record:{fid}:invalid_type:{key}' for _ in missing)
    errors.extend(f'record:{fid}:prohibited_key:{item}' for item in sorted(extra))
    return value


def validate_geox_calibration_source_manifest(payload: object) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ('manifest:not_object',)
    errors.extend(f'manifest:missing_key:{key}' for key in sorted(TOP_KEYS - set(payload)))
    errors.extend(f'manifest:extra_key:{key}' for key in sorted(set(payload) - TOP_KEYS))
    expected = {'schema_version': 'geox_calibration_source_manifest_v1', 'record_version': '1.0.0', 'case_count': 12, 'source_repository': 'Phani-Pavuluri/panel_exp', 'source_fixture_checkpoint_sha': '860182386c39f487747de5f43e67a31e9978e57c', 'source_tree_base_sha': '7f829395bc305550ea1311421a4181dafed795b8', 'synthetic_fixture_time_scope': True, 'mmm_compatibility_emitted': False, 'calibration_signal_emitted': False, 'production_authorized': False}
    for key, value in expected.items():
        if key in payload and (type(payload[key]) is not type(value) or payload[key] != value):
            errors.append(f'manifest:invalid_value:{key}')
    records = payload.get('records')
    if not isinstance(records, list):
        errors.append('manifest:invalid_type:records')
        return tuple(errors)
    ids = [item.get('fixture_id') if isinstance(item, dict) else None for item in records]
    valid_ids = [item for item in ids if isinstance(item, str)]
    if len(records) != 12 or len(valid_ids) != 12 or set(valid_ids) != CASES or len(set(valid_ids)) != 12:
        errors.append('manifest:case_set_mismatch')
    if len(valid_ids) == len(ids) and valid_ids != sorted(valid_ids):
        errors.append('manifest:records_not_sorted')
    evidence: list[str] = []
    readouts: list[str] = []
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            errors.append(f'record:{index}:invalid_type')
            continue
        fid = item.get('fixture_id', index)
        errors.extend(f'record:{index}:missing_key:{key}' for key in sorted(RECORD_KEYS - set(item)))
        for key in sorted(set(item) - RECORD_KEYS):
            code = f'record:{fid}:prohibited_key:{key}' if key in PROHIBITED else f'record:{fid}:extra_key:{key}'
            errors.append(code)
        if set(item) != RECORD_KEYS:
            continue
        for key in ('fixture_id', 'evidence_artifact_id', 'source_readout_id', 'experiment_id', 'dataset_version', 'truth_version', 'fixture_class', 'certification_status', 'kpi', 'kpi_units', 'estimand', 'effect_scale', 'channel', 'tactic', 'geography_scope', 'geo_grain', 'time_window', 'pre_period', 'post_period', 'interval_semantics', 'method_family', 'method_status', 'instrument_id', 'design_type', 'feasibility_status', 'readout_status', 'freshness_status', 'handoff_eligibility_status', 'producer_package_version', 'producer_commit', 'governed_readout_path', 'source_truth_path', 'replay_path'):
            if not _string(item[key]):
                errors.append(f'record:{fid}:invalid_type:{key}')
        if isinstance(fid, str) and (item['evidence_artifact_id'] != f'geox-evidence-{fid}-v1' or item['experiment_id'] != fid):
            errors.append(f'record:{fid}:invalid_identity')
        if isinstance(item['source_readout_id'], str):
            readouts.append(item['source_readout_id'])
        if isinstance(item['evidence_artifact_id'], str):
            evidence.append(item['evidence_artifact_id'])
        for key in ('governed_readout_sha256', 'source_truth_sha256', 'replay_sha256'):
            if not isinstance(item[key], str) or not SHA256.fullmatch(item[key]):
                errors.append(f'record:{fid}:invalid_type:{key}')
        for key in ('effect_estimate', 'absolute_lift', 'relative_lift', 'incremental_outcome', 'standard_error'):
            if item[key] is not None and not _number(item[key]):
                errors.append(f'record:{fid}:invalid_type:{key}')
        if item['confidence_interval'] is not None and (not isinstance(item['confidence_interval'], list) or len(item['confidence_interval']) != 2 or not all(_number(v) for v in item['confidence_interval'])):
            errors.append(f'record:{fid}:invalid_type:confidence_interval')
        if not isinstance(item['uncertainty_available'], bool):
            errors.append(f'record:{fid}:invalid_type:uncertainty_available')
        for key in ('warnings', 'blocked_reasons', 'failure_reasons'):
            if not isinstance(item[key], list) or not all(isinstance(v, str) for v in item[key]):
                errors.append(f'record:{fid}:invalid_type:{key}')
        handoff = _nested(item, 'mip_handoff_expectation', {'artifact_kind', 'status'}, fid, errors)
        lineage = _nested(item, 'lineage', {'fixture_id', 'dataset_version', 'truth_version', 'upstream_artifacts'}, fid, errors)
        provenance = _nested(item, 'provenance', {'source_repo', 'source_commit', 'producer_package_version', 'created_by'}, fid, errors)
        replay = _nested(item, 'replay_metadata', {'assignment_seed', 'replay_version', 'deterministic'}, fid, errors)
        auth = _nested(item, 'authorization_flags', AUTH_KEYS, fid, errors)
        if handoff and (not _string(handoff.get('artifact_kind')) or not _string(handoff.get('status'))): errors.append(f'record:{fid}:invalid_type:mip_handoff_expectation')
        if lineage and (lineage.get('fixture_id') != fid or lineage.get('dataset_version') != item['dataset_version'] or lineage.get('truth_version') != item['truth_version'] or not isinstance(lineage.get('upstream_artifacts'), list) or not all(isinstance(v, str) for v in lineage.get('upstream_artifacts', []))): errors.append(f'record:{fid}:invalid_identity:lineage')
        if provenance and not all(_string(provenance.get(key)) for key in ('source_repo', 'source_commit', 'producer_package_version', 'created_by')): errors.append(f'record:{fid}:invalid_type:provenance')
        if replay and (isinstance(replay.get('assignment_seed'), bool) or not isinstance(replay.get('assignment_seed'), int) or not _string(replay.get('replay_version')) or not isinstance(replay.get('deterministic'), bool)): errors.append(f'record:{fid}:invalid_type:replay_metadata')
        if auth and (set(auth) != AUTH_KEYS or any(value is not False for value in auth.values())): errors.append(f'record:{fid}:unsafe_authorization')
        freshness = item['freshness_status']
        if not isinstance(freshness, str):
            errors.append(f'record:{fid}:invalid_type:freshness_status')
        elif freshness not in {'fresh', 'stale'}:
            errors.append(f'record:{fid}:invalid_value:freshness_status')
        if type(item['synthetic_fixture_time_scope']) is not bool or item['synthetic_fixture_time_scope'] is not True:
            errors.append(f'record:{fid}:invalid_type:synthetic_fixture_time_scope')
        parsed = [_timestamp(item[key]) for key in ('time_window_start', 'time_window_end', 'produced_at', 'freshness_evaluated_at')]
        if any(value is None for value in parsed): errors.append(f'record:{fid}:invalid_timestamp')
        elif not (parsed[0] < parsed[1] <= parsed[2] <= parsed[3]): errors.append(f'record:{fid}:invalid_timestamp_order')
        if freshness == 'fresh':
            expected_times = ('2025-01-06T00:00:00Z', '2025-03-30T23:59:59Z', '2025-03-31T00:00:00Z', '2025-04-01T00:00:00Z')
        elif freshness == 'stale':
            expected_times = ('2024-01-08T00:00:00Z', '2024-03-31T23:59:59Z', '2024-04-01T00:00:00Z', '2025-04-01T00:00:00Z')
        else:
            expected_times = ()
        for field, expected_time in zip(('time_window_start', 'time_window_end', 'produced_at', 'freshness_evaluated_at'), expected_times):
            if item[field] != expected_time: errors.append(f'record:{fid}:invalid_timestamp:{field}')
    if len(evidence) != len(set(evidence)): errors.append('manifest:duplicate_evidence_artifact_id')
    if len(readouts) != len(set(readouts)): errors.append('manifest:duplicate_source_readout_id')
    return tuple(errors)


def _safe_path(root: Path, value: object, fid: str, kind: str) -> tuple[Path | None, str | None]:
    if not isinstance(value, str) or not value or '\\' in value:
        return None, f'source:{fid}:unsafe_path:{kind}'
    relative = Path(value)
    if relative.is_absolute() or '..' in relative.parts:
        return None, f'source:{fid}:unsafe_path:{kind}'
    resolved = (root / relative).resolve()
    if root.resolve() not in resolved.parents:
        return None, f'source:{fid}:unsafe_path:{kind}'
    if not resolved.exists() or not resolved.is_file():
        return None, f'source:{fid}:missing_file:{kind}'
    return resolved, None


def validate_geox_calibration_source_manifest_sources(payload: object, *, source_root: Path) -> tuple[str, ...]:
    errors = list(validate_geox_calibration_source_manifest(payload))
    if errors or not isinstance(payload, dict):
        return tuple(errors)
    try:
        source_manifest = json.loads((source_root / 'manifest.json').read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return tuple(errors + ['source:manifest:invalid_json'])
    if not isinstance(source_manifest, dict) or not isinstance(source_manifest.get('cases'), list):
        return tuple(errors + ['source:manifest:invalid_cases'])
    raw_cases = source_manifest['cases']
    valid_case_ids = [case.get('case_id') for case in raw_cases if isinstance(case, dict) and isinstance(case.get('case_id'), str)]
    if type(source_manifest.get('case_count')) is not int or source_manifest.get('case_count') != 12 or type(source_manifest.get('mmm_compatibility_emitted')) is not bool or source_manifest.get('mmm_compatibility_emitted') is not False or type(source_manifest.get('production_authorized')) is not bool or source_manifest.get('production_authorized') is not False or len(raw_cases) != 12 or len(valid_case_ids) != 12 or set(valid_case_ids) != CASES or len(set(valid_case_ids)) != 12:
        errors.append('source:manifest:case_set_mismatch')
    cases = {}
    for case in raw_cases:
        if not isinstance(case, dict):
            errors.append('source:manifest:invalid_case')
            continue
        if set(case) != {'case_id', 'governed_readout', 'source_truth', 'replay'}:
            errors.append('source:manifest:invalid_case')
            continue
        if not all(_string(case.get(key)) for key in ('case_id', 'governed_readout', 'source_truth', 'replay')):
            errors.append('source:manifest:invalid_case')
            continue
        if case['case_id'] not in cases: cases[case['case_id']] = case
    for record in payload['records']:
        fid = record['fixture_id']; case = cases.get(fid)
        if not isinstance(case, dict):
            errors.append(f'source:{fid}:case_missing')
            continue
        paths: dict[str, Path] = {}
        unsafe = False
        mismatched = False
        for kind in ('governed_readout', 'source_truth', 'replay'):
            if record[f'{kind}_path'] != case.get(kind):
                errors.append(f'source:{fid}:field_mismatch:{kind}_path')
                mismatched = True
        if mismatched:
            continue
        for kind in ('governed_readout', 'source_truth', 'replay'):
            path, reason = _safe_path(source_root, case[kind], fid, kind)
            if reason:
                errors.append(reason); unsafe = True
            else:
                paths[kind] = path
        if unsafe:
            continue
        values: dict[str, object] = {}
        parse_failed = False
        for kind, path in paths.items():
            try:
                value = json.loads(path.read_text(encoding='utf-8'))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                errors.append(f'source:{fid}:invalid_json:{kind}')
                parse_failed = True
                continue
            if not isinstance(value, dict):
                errors.append(f'source:{fid}:non_object_json:{kind}')
                parse_failed = True
                continue
            values[kind] = value
        if parse_failed:
            continue
        for kind, path in paths.items():
            if hashlib.sha256(path.read_bytes()).hexdigest() != record[f'{kind}_sha256']:
                errors.append(f'source:{fid}:checksum_mismatch:{kind}')
        try:
            parsed = deserialize_geox_governed_experiment_readout(values['governed_readout'])
        except (TypeError, KeyError, ValueError):
            errors.append(f'source:{fid}:deserialization_failure')
            continue
        if validate_geox_governed_experiment_readout(parsed):
            errors.append(f'source:{fid}:invalid_governed_readout')
        canonical = serialize_geox_governed_experiment_readout(parsed)
        for key in ('readout_id', 'experiment_id', 'dataset_version', 'truth_version', 'kpi', 'kpi_units', 'estimand', 'effect_scale', 'channel', 'tactic', 'geography_scope', 'geo_grain', 'time_window', 'pre_period', 'post_period', 'effect_estimate', 'absolute_lift', 'relative_lift', 'incremental_outcome', 'uncertainty_available', 'standard_error', 'confidence_interval', 'interval_semantics', 'method_family', 'method_status', 'instrument_id', 'design_type', 'feasibility_status', 'readout_status', 'freshness_status', 'handoff_eligibility_status', 'warnings', 'blocked_reasons', 'failure_reasons', 'lineage', 'provenance', 'replay_metadata', 'producer_package_version', 'producer_commit', 'authorization_flags'):
            target = 'source_readout_id' if key == 'readout_id' else key
            if record[target] != canonical[key]: errors.append(f'source:{fid}:field_mismatch:{target}')
        truth = values['source_truth']; replay = values['replay']
        for key in ('fixture_id', 'fixture_class', 'certification_status', 'mip_handoff_expectation'):
            if record[key] != truth.get(key): errors.append(f'source:{fid}:source_truth_mismatch:{key}')
        if 'dataset_version' in truth and truth['dataset_version'] != record['dataset_version']:
            errors.append(f'source:{fid}:source_truth_mismatch:dataset_version')
        if 'truth_version' in truth and truth['truth_version'] != record['truth_version']:
            errors.append(f'source:{fid}:source_truth_mismatch:truth_version')
        if replay.get('case_id') != fid: errors.append(f'source:{fid}:replay_mismatch:case_id')
        if replay.get('deterministic') is not True: errors.append(f'source:{fid}:replay_mismatch:deterministic')
    return tuple(errors)


def load_and_validate_geox_calibration_source_manifest(manifest_path: Path, *, source_root: Path) -> dict[str, object]:
    try:
        payload = json.loads(manifest_path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GeoXCalibrationSourceManifestValidationError(('manifest:invalid_json',)) from exc
    errors = validate_geox_calibration_source_manifest_sources(payload, source_root=source_root)
    if errors:
        raise GeoXCalibrationSourceManifestValidationError(errors)
    return payload
