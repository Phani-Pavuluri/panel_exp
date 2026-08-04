# Active Task

**Status:** blocked
**Owner:** GeoX governed-readout producer and certified-fixture owner
**Last updated:** 2026-08-04
**Last verified:** 2026-08-04

## Identity and correction authority

- **Task ID:** `GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Feature branch:** `feat/geox-certified-calibration-source-manifest-001`
- **Pre-authoring base:** `80dbe14c6b2ce74b33a2b776c5e567afba582bf5`
- **Authorized branch baseline:** `d12a46d191eb7998870a6f040af9c424f18a4e31`
- **Rejected exact remote head:** `6860d54796ae999184b9ffe3ac5bd16b69e5d745`
- **Rejected implementation commit:** `8002e83556c324a73b9b51e8cbcb2038a9a2888f`
- **Correction cycles:** 1 used of 1; 0 remain after this correction
- **Risk tier:** Tier 3 certified cross-repository producer fixture
- **Capability authorizations changed:** `false`

The rejected head is not mergeable and its published `blocked` state is not accepted. This is the only authorized correction cycle. A second failed exact-head review supersedes the task without merge.

## Primary outcome remains unchanged

Publish one strict, deterministic, non-authorizing GeoX calibration-handoff source manifest over exactly the 12 existing certified `GeoXGovernedExperimentReadout` fixtures.

The source manifest adds only producer-owned evidence identity, exact source paths and checksums, deterministic synthetic fixture timestamps, freshness provenance, and exact copied producer fields. It must not derive method eligibility, emit or calculate MMM compatibility, construct `CalibrationSignal`, alter experiment/readout truth, or authorize MIP/MMM/runtime/planning/recommendation behavior.

## Rejected-head findings that must be corrected

1. `docs/execution/EXECUTION_STATE.json` is invalid JSON because the `blockers` array is missing a trailing comma before `dependencies`. The claimed changed-JSON parse therefore cannot be true.
2. The source contract is a compressed 28-line implementation with broad `dict`, `list`, and `object` fields. It does not strictly validate field types, nested shapes, nullable fields, closed status vocabularies, exact `Z` UTC form, exact IDs, paths, checksums, source equality, or prohibited fields.
3. `parse()` accepts non-`Z` UTC strings by replacing `Z` and compares original timestamp strings rather than parsed datetimes. `validate()` returns errors but is not enforced by parsing or generation.
4. No contextual validator exists. Path containment, file existence, actual SHA-256 equality, identity equality, canonical readout validation, field preservation, source-tree immutability, and prohibited-field rejection are absent.
5. The builder does not require the exact 12 case IDs, does not reject duplicates/omissions, ignores source-manifest paths, does not support an isolated output path, does not sort records explicitly, does not validate through `deserialize_geox_governed_experiment_readout` plus `validate_geox_governed_experiment_readout`, and does not contextually validate generated records.
6. `certification_status` is incorrectly copied from governed-readout `method_status` rather than `source_truth.json.certification_status`.
7. All records receive fresh timestamps. The required stale mapping is absent, and fresh `freshness_evaluated_at` is incorrectly `2025-03-31T00:00:00Z` instead of `2025-04-01T00:00:00Z`.
8. The committed manifest lacks required top-level `case_count`, `source_repository`, source checkpoint, source-tree base, synthetic-scope marker, `mmm_compatibility_emitted`, `calibration_signal_emitted`, and `production_authorized` fields. Its top-level schema is also the record schema rather than `geox_calibration_handoff_source_manifest_v1`.
9. Only three broad tests exist. They mutate the committed manifest, do not run two isolated builds, and do not prove the named acceptance contract.
10. The Track-D document and archive summary are placeholders and do not record the required evidence, limitations, consumer boundary, or validation.
11. The `blocked` report gives no exact Docker command transcript, elapsed/stall evidence, failing dependency, attempted remediation, timeout, Docker/build state, or live resolution condition. Even a genuine Docker obstruction cannot excuse the task-owned implementation failures above.
12. Ruff, exact owned-path evidence, two-run replay, source-tree immutability, manifest SHA-256, exact validation-category dispositions, exact-tree receipt, and clean/local-remote evidence are absent.

## Exact source cases

The correction must cover exactly these IDs and no others:

1. `geox_truth_bayesian_tbr_research_only_001`
2. `geox_truth_calibration_incompatible_001`
3. `geox_truth_conflicting_evidence_001`
4. `geox_truth_did_candidate_warning_001`
5. `geox_truth_infeasible_preperiod_001`
6. `geox_truth_multicell_shared_control_block_001`
7. `geox_truth_safe_blocked_readout_001`
8. `geox_truth_scm_candidate_clean_001`
9. `geox_truth_stale_incompatible_evidence_001`
10. `geox_truth_tbrridge_diagnostic_only_001`
11. `geox_truth_unsupported_inference_001`
12. `geox_truth_weak_matchability_001`

## Owned and prohibited paths

Correction may modify only:

1. `panel_exp/contracts/geox_calibration_handoff_source.py`
2. `scripts/build_geox_calibration_handoff_source_manifest.py`
3. `tests/contracts/test_geox_calibration_handoff_source.py`
4. `tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json`
5. `docs/track_d/GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001.md`
6. `docs/track_d/archives/GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001_summary.json`
7. `docs/execution/ACTIVE_TASK.md`
8. `docs/execution/EXECUTION_STATE.json`
9. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify `panel_exp/contracts/__init__.py`, any file below `tests/fixtures/geox_governed_readouts/`, MIP, MMM, or unrelated paths. Do not reuse or cherry-pick the superseded prior branch.

## Required corrected source contract

Implement readable typed code with:

- `GeoXCalibrationHandoffSourceRecord`;
- strict intrinsic parser;
- normalized serializer;
- explicit validation error type or deterministic error codes;
- contextual validator against the certified source root;
- manifest parser/validator for `geox_calibration_handoff_source_manifest_v1`.

Use explicit scalar, nullable, tuple/list, mapping, and nested-record types. Do not use `object`, unparameterized `dict`/`list`, blind `cls(**payload)` as the validation boundary, semicolon-compressed declarations, or one-line implementation blocks.

Intrinsic validation must enforce exact keys, schema/record versions, field types, nested shapes, closed source status vocabularies, exact ID formulas, exact 40-character pins, `synthetic_fixture_time_scope is True`, all authorization flags false, and exact `Z` UTC timestamps parsed as aware UTC datetimes with correct ordering.

Contextual validation must:

- resolve each repository-relative path exactly once under `tests/fixtures/geox_governed_readouts/`;
- reject absolute paths, `..`, root escape, missing paths, and non-files;
- recompute SHA-256 from exact bytes and compare it;
- deserialize the governed readout with `deserialize_geox_governed_experiment_readout` and require `validate_geox_governed_experiment_readout(...) == ()`;
- parse source truth and replay as objects;
- require readout, experiment, fixture, dataset, truth, version, analytical, uncertainty, method, instrument, status, warning, blocker, failure, lineage, provenance, replay, producer, and authorization values to match exactly;
- require `fixture_class`, `certification_status`, and complete `mip_handoff_expectation` to match `source_truth.json` exactly;
- reject `source_truth.calibration_compatibility` or any equivalent MMM result in the output envelope;
- reject `method_eligibility_status` and every prohibited downstream field.

## Required corrected builder and manifest

The builder must read the existing source manifest and use its declared relative paths rather than reconstructing them. It must require the exact 12 IDs, one occurrence each, and `case_count == 12`; reject every mismatch; validate each canonical readout; read source truth and replay; build and contextually validate records; sort by `fixture_id`; and support both the committed default output and a caller-supplied isolated output path.

Use these exact timestamps:

For `fresh`:

- `time_window_start = 2025-01-06T00:00:00Z`
- `time_window_end = 2025-03-30T23:59:59Z`
- `produced_at = 2025-03-31T00:00:00Z`
- `freshness_evaluated_at = 2025-04-01T00:00:00Z`

For `stale`:

- `time_window_start = 2024-01-08T00:00:00Z`
- `time_window_end = 2024-03-31T23:59:59Z`
- `produced_at = 2024-04-01T00:00:00Z`
- `freshness_evaluated_at = 2025-04-01T00:00:00Z`

Reject every other freshness status.

The committed manifest must contain:

- `schema_version: geox_calibration_handoff_source_manifest_v1`;
- `record_version: 1.0.0`;
- `case_count: 12`;
- `source_repository: Phani-Pavuluri/panel_exp`;
- `source_fixture_checkpoint_sha: 860182386c39f487747de5f43e67a31e9978e57c`;
- `task_source_tree_base_sha: 80dbe14c6b2ce74b33a2b776c5e567afba582bf5`;
- `synthetic_fixture_time_scope: true`;
- `mmm_compatibility_emitted: false`;
- `calibration_signal_emitted: false`;
- `production_authorized: false`;
- exactly 12 records sorted by fixture ID.

Normalized output uses UTF-8, sorted keys, two-space indentation, and one trailing newline. Two isolated runs must be byte-identical and equal the committed manifest. The existing governed-readout fixture tree must remain byte-identical.

## Required behavioral acceptance evidence

Replace the three broad tests with separate tests proving at least:

1. supported-version parse/serialize round trip;
2. missing, extra, wrong scalar, wrong nullable, wrong sequence, wrong mapping, malformed nested, and unsupported-version rejection;
3. exact ID formulas, uniqueness, and source-readout identity;
4. exact 12-case coverage and duplicate/omission/addition rejection;
5. exact source pins and manifest shape;
6. canonical readout validation for all 12 sources;
7. safe path resolution plus absolute, traversal, escape, missing-file, and non-file rejection;
8. actual checksum equality and mismatch rejection for all three referenced files;
9. exact field-by-field analytical and uncertainty preservation, including nulls;
10. exact method/instrument/status/warnings/blockers/failures/lineage/provenance/replay/authorization preservation;
11. exact source-truth `fixture_class`, `certification_status`, and complete `mip_handoff_expectation` preservation;
12. exact fresh and stale timestamp mapping, strict `Z` UTC parsing, and ordering failures;
13. absence and rejection of `source_truth.calibration_compatibility`, derived method eligibility, MMM compatibility, `CalibrationSignal`, TrustReport, DecisionSurface, recommendation, optimization, assignment, LLM, planning, and production fields;
14. all authorization flags false and true-flag rejection;
15. two isolated builder runs equal each other and the committed manifest byte for byte;
16. source-tree hashes unchanged before and after both runs.

Tests must use actual fixtures and must not rewrite the committed manifest during ordinary focused execution.

## Documentation and evidence

Expand the Track-D document and archive summary to record the exact task/source pins, all 12 cases, paths, identity rules, copied fields, timestamp semantics, checksum/path behavior, prohibited outputs, immutable-source rule, validation results, limitations, debt, MIP/MMM impact, consumer verification, and unchanged authority.

## Correction validation gate

Run on the final frozen task-owned tree:

1. `poetry install --with dev --no-interaction`.
2. Parse every changed JSON file, including `docs/execution/EXECUTION_STATE.json`.
3. Compile all changed Python files.
4. `git diff --check`.
5. Verify exact changed paths against `80dbe14c6b2ce74b33a2b776c5e567afba582bf5`.
6. `poetry run pytest -q tests/contracts/test_geox_calibration_handoff_source.py` with exact counts.
7. `poetry run pytest -q tests/fixtures/test_geox_certified_governed_readout_fixtures.py tests/contracts/test_geox_governed_experiment_readout.py` with exact counts.
8. `poetry run ruff check panel_exp/contracts/geox_calibration_handoff_source.py scripts/build_geox_calibration_handoff_source_manifest.py tests/contracts/test_geox_calibration_handoff_source.py`.
9. Mypy remains `not_required`.
10. Two isolated builder replays, committed-manifest byte equality, manifest SHA-256, and complete source-tree immutability proof.
11. `make validate-docker` through the fresh repository-authored path, with exact final results.
12. Clean task-owned worktree and exact local/remote branch-head equality after push.

Task-owned failures are unfinished and must be fixed. A Docker blocker is acceptable only after the corrected code and all non-Docker gates pass, and only with the exact command, timestamps or elapsed time, final output/diagnostics, stall/failure location, Docker/build state, attempted remediation, validation-category dispositions, and a live resolution condition. A vague stall statement is invalid.

## Correction publication contract

Create one corrected implementation commit. Then update all three execution files with the rejected-head lineage and either:

- `ready_for_review` after the entire gate passes; or
- a genuine external `blocked` state satisfying the evidence contract above.

For `ready_for_review`, record exactly one corrected implementation SHA, exact counts/results, manifest SHA-256, all paths/cases/pins, limitations, debt, sibling impact, consumer verification, task execution true, correction execution false, merge/PR false, and unchanged authority.

Freeze the final tree, rerun the complete gate, and create one exact-tree receipt commit identifying task ID, corrected implementation parent, commands, exact results, evidence source, worktree state, and authority impact. Do not modify task-owned files after the receipt. Push only the declared branch, fetch it again, and prove exact local/remote equality.

## Terminal condition

Progress is non-terminal. Stop only when the exact remote branch durably records a new fully evidenced `ready_for_review` head or a genuine external `blocked` head. Do not create a PR, merge, squash, rebase, force-push, merge commit, modify siblings, emit compatibility, construct `CalibrationSignal`, alter experiment truth, or change capability authority.

**Unresolved execution-blocking design questions: none.**
