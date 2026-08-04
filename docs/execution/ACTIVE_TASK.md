# Active Task

**Status:** blocked
**Owner:** GeoX governed-readout producer and certified-fixture owner
**Last updated:** 2026-08-04
**Last verified:** 2026-08-04

## Identity

- **Task ID:** `GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Pre-authoring base:** `80dbe14c6b2ce74b33a2b776c5e567afba582bf5`
- **Intended feature branch:** `feat/geox-certified-calibration-source-manifest-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 3 — certified cross-repository producer fixture
- **Coordination workstream:** `WS-GEOX-CERTIFIED-CALIBRATION-SOURCE-MANIFEST-001`
- **Capability authorizations changed:** `false`

## Primary independently mergeable outcome

Publish one strict, deterministic, non-authorizing GeoX calibration-handoff **source manifest** over the 12 existing certified `GeoXGovernedExperimentReadout` fixtures.

The manifest supplies only producer-owned source evidence that is currently missing for cross-repository consumption:

- stable evidence identity;
- exact source paths and SHA-256 checksums;
- exact synthetic fixture time scope;
- freshness provenance;
- exact method, instrument, certification, handoff, and lineage fields copied from existing certified sources.

It must not derive a new method-eligibility verdict, emit or calculate MMM compatibility, construct `CalibrationSignal`, or change experiment/readout truth.

## Live prerequisite evidence

Connected GitHub verification before authoring established:

- GeoX `main`: `80dbe14c6b2ce74b33a2b776c5e567afba582bf5`.
- Prior task `GEOX_CERTIFIED_CALIBRATION_HANDOFF_SOURCE_FIXTURE_001` is superseded without merge. Its preserved branch `feat/geox-certified-calibration-handoff-source-fixture-001` at `a84d85277f9bbc35c08a40308d65858adbd36713` is historical failed-attempt evidence only and must not be resumed, cherry-picked, merged, rebased, or copied as approved implementation.
- Certified governed-readout fixtures were introduced at merged checkpoint `860182386c39f487747de5f43e67a31e9978e57c` and remain available under `tests/fixtures/geox_governed_readouts/`.
- Canonical readout contract: `panel_exp/contracts/geox_governed_experiment_readout.py`.
- Canonical source manifest: `tests/fixtures/geox_governed_readouts/manifest.json`, with exactly 12 cases and `mmm_compatibility_emitted: false`.
- MIP `main`: `0b4cd1fca73716e4968c2ceb70c594ad8aadd8ca`.
- MIP feature branch `feat/mip-p2-geox-mmm-compatibility-fixture-bridge-001` is blocked at `480b32040ce185b8ff091435121c4bea6fc6c453` by `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001` because no certified provenance-linked GeoX/MMM producer pair exists.
- MMM `main`: `f2e0eade0ad917c1b28ab5521e6d35a35047d988`; its current task is an unrelated non-executable governance proposal. No MMM technical fixture task is authorized.
- No active, authorized, review-ready, blocked, or recently completed GeoX task owns this exact source-manifest outcome.

Before implementation, re-fetch all three repositories and stop if live ownership, blocker identity, fixture paths, source contract, or sibling task overlap has materially changed.

## Exact source cases

The successor must cover exactly these 12 existing fixture IDs:

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

## Exact observable behavior

### 1. Add one narrow source-record contract

Add `panel_exp/contracts/geox_calibration_handoff_source.py` with a readable typed record, strict parser, normalized serializer, and contextual validator for one manifest record.

Do not export it through `panel_exp/contracts/__init__.py` in this task. This checkpoint is a certified fixture contract, not a new public runtime entrypoint.

Each record must explicitly contain:

- `schema_version` fixed to `geox_calibration_handoff_source_v1`;
- `record_version` fixed to `1.0.0`;
- deterministic `handoff_source_id` exactly `geox-calibration-source-<fixture_id>-v1`;
- deterministic `evidence_artifact_id` exactly `geox-evidence-<fixture_id>-v1`;
- `source_readout_id`, readout version, artifact version, experiment ID, fixture ID, dataset version, and truth version;
- source repository `Phani-Pavuluri/panel_exp`;
- source-fixture checkpoint `860182386c39f487747de5f43e67a31e9978e57c`;
- task source-tree base `80dbe14c6b2ce74b33a2b776c5e567afba582bf5`;
- exact repository-relative paths and SHA-256 checksums for `governed_readout.json`, `source_truth.json`, and `replay.json`;
- `fixture_class`, `certification_status`, and the complete `mip_handoff_expectation` object copied exactly from `source_truth.json`;
- KPI, KPI units, estimand, effect scale, channel, tactic, geography scope, geo grain, symbolic time window, pre-period, and post-period copied exactly from the governed readout;
- effect estimate, absolute lift, relative lift, incremental outcome, uncertainty availability, standard error, confidence interval, and interval semantics copied exactly, including nulls;
- deterministic synthetic `time_window_start`, `time_window_end`, `produced_at`, and `freshness_evaluated_at`;
- `synthetic_fixture_time_scope: true`;
- method family, source method status, instrument ID, design type, feasibility status, readout status, freshness status, and handoff eligibility copied exactly;
- warnings, blocked reasons, failure reasons, lineage, provenance, replay metadata, producer package version, embedded producer commit, and all source authorization flags copied exactly.

Do not add a derived `method_eligibility_status`. The existing source fields intentionally represent distinct concepts and must remain distinct.

### 2. Exact temporal values

Use committed deterministic UTC values only.

For records with source `freshness_status == "fresh"`:

- `time_window_start`: `2025-01-06T00:00:00Z`
- `time_window_end`: `2025-03-30T23:59:59Z`
- `produced_at`: `2025-03-31T00:00:00Z`
- `freshness_evaluated_at`: `2025-04-01T00:00:00Z`

For records with source `freshness_status == "stale"`:

- `time_window_start`: `2024-01-08T00:00:00Z`
- `time_window_end`: `2024-03-31T23:59:59Z`
- `produced_at`: `2024-04-01T00:00:00Z`
- `freshness_evaluated_at`: `2025-04-01T00:00:00Z`

Reject any other freshness status. These are synthetic fixture timestamps, not real experiment dates.

### 3. Strict parsing and contextual validation

The parser must reject:

- non-object records;
- missing or extra keys;
- unsupported schema or record versions;
- wrong scalar, list, object, nullable, or nested field types;
- malformed, non-`Z`, non-UTC, or incorrectly ordered timestamps;
- false `synthetic_fixture_time_scope`;
- malformed IDs or IDs inconsistent with `fixture_id`;
- short, malformed, or incorrect source pins;
- absolute paths, `..` traversal, or paths outside `tests/fixtures/geox_governed_readouts/`;
- missing files or checksum mismatch;
- source/readout identity mismatch;
- any copied analytical, governance, lineage, provenance, replay, or authorization value that differs from the referenced certified source;
- any true authorization flag;
- any MMM compatibility, target-model, calibration-weight, `CalibrationSignal`, TrustReport, DecisionSurface, recommendation, optimization, assignment, LLM-decision, or equivalent downstream field.

The strict record parser may validate intrinsic shape without filesystem access. A separate contextual validator must resolve and compare the record against the certified source tree.

### 4. Deterministic builder

Add `scripts/build_geox_calibration_handoff_source_manifest.py`.

The builder must:

- start from repository root and read `tests/fixtures/geox_governed_readouts/manifest.json`;
- require exactly the 12 declared case IDs and reject duplicates or omissions;
- resolve each manifest path exactly once from `tests/fixtures/geox_governed_readouts/`;
- prove each resolved path stays within that root;
- deserialize and validate every governed readout through the canonical GeoX readout contract;
- read `source_truth.json` and `replay.json` as source inputs;
- copy only the authorized source-truth fields named above;
- never copy or expose `source_truth.calibration_compatibility`;
- compute checksums from exact file bytes;
- construct and contextually validate every source record;
- write normalized JSON with sorted keys, two-space indentation, UTF-8, and one trailing newline;
- sort records by `fixture_id`;
- write by default to `tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json`;
- support an explicit output path for isolated replay tests;
- never modify `tests/fixtures/geox_governed_readouts/**`.

Two runs from the same synchronized tree must produce byte-identical output.

### 5. Manifest shape

The committed manifest must be one object with:

- `schema_version: geox_calibration_handoff_source_manifest_v1`;
- `record_version: 1.0.0`;
- `case_count: 12`;
- `source_repository`;
- exact source-fixture checkpoint;
- exact task source-tree base;
- `synthetic_fixture_time_scope: true`;
- `mmm_compatibility_emitted: false`;
- `calibration_signal_emitted: false`;
- `production_authorized: false`;
- `records`: the 12 normalized records.

No analytical value may be invented or changed.

## Ownership and authority boundaries

GeoX owns governed experiment/readout identity, producer provenance, fixture time scope, method/instrument status, certification fields, handoff eligibility, and experiment truth.

MMM retains exclusive ownership of calibration compatibility. MIP retains exclusive ownership of consumer reconciliation and canonical `CalibrationSignal` construction.

This task does not authorize or implement:

- MMM compatibility evaluation or fixtures;
- `CalibrationSignal` or MIP evidence construction;
- changes to experiment design, assignment, inference, estimates, uncertainty, statuses, or handoff truth;
- runtime MIP/MMM integration;
- TrustReport, DecisionSurface, simulation, optimization, planning, recommendation, LLM, real-data, pilot, or production behavior;
- changes in MIP or MMM repositories.

## Owned paths

Implementation may modify only:

1. `panel_exp/contracts/geox_calibration_handoff_source.py`
2. `scripts/build_geox_calibration_handoff_source_manifest.py`
3. `tests/contracts/test_geox_calibration_handoff_source.py`
4. `tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json`
5. `docs/track_d/GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001.md`
6. `docs/track_d/archives/GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001_summary.json`
7. `docs/execution/ACTIVE_TASK.md`
8. `docs/execution/EXECUTION_STATE.json`
9. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify `panel_exp/contracts/__init__.py` or any file below `tests/fixtures/geox_governed_readouts/`.

## Named acceptance evidence

`tests/contracts/test_geox_calibration_handoff_source.py` must separately prove:

1. strict supported-version parsing and normalized round trip;
2. missing, extra, wrong-type, malformed nested, and unsupported-version failures;
3. exactly 12 records and exact one-to-one source-case coverage;
4. exact ID formulas, source-readout identity, uniqueness, and deterministic replay;
5. exact source paths, path containment, file existence, and SHA-256 equality;
6. path traversal, missing-file, and checksum-mismatch failures;
7. canonical governed-readout validation for every source;
8. exact field-by-field analytical and governance preservation for all 12 cases, including nulls;
9. exact `fixture_class`, `certification_status`, and `mip_handoff_expectation` preservation;
10. absence of copied `source_truth.calibration_compatibility` and all prohibited downstream fields;
11. strict UTC timestamps, exact fresh/stale date mapping, and temporal ordering;
12. exact method, instrument, readout, feasibility, freshness, and handoff status preservation without a derived eligibility field;
13. all authorization flags remain false;
14. two isolated builder runs are byte-identical and equal the committed manifest byte for byte;
15. the complete governed-readout source tree is byte-identical before and after both runs;
16. no MMM compatibility or `CalibrationSignal` is emitted or calculated.

Tests must parse and compare actual fixture payloads. Documentation-text searches are not acceptance evidence.

## Validation gate

Run on the frozen final task-owned tree:

1. Install the repository environment through the declared dependency manager:

   `poetry install --with dev --no-interaction`

2. Parse every changed JSON file with Python's JSON parser.
3. Compile all changed Python files with `python -m py_compile`.
4. Run `git diff --check`.
5. Verify exact changed paths against pre-authoring base `80dbe14c6b2ce74b33a2b776c5e567afba582bf5`.
6. Run focused tests:

   `poetry run pytest -q tests/contracts/test_geox_calibration_handoff_source.py`

7. Run adjacent certified-readout tests:

   `poetry run pytest -q tests/fixtures/test_geox_certified_governed_readout_fixtures.py tests/contracts/test_geox_governed_experiment_readout.py`

8. Run Ruff:

   `poetry run ruff check panel_exp/contracts/geox_calibration_handoff_source.py scripts/build_geox_calibration_handoff_source_manifest.py tests/contracts/test_geox_calibration_handoff_source.py`

9. Mypy is `not_required`: the synchronized repository has no configured mypy dependency or gate. Do not add or install mypy in this task.
10. Run the builder twice to isolated temporary outputs; prove byte equality with each other and with the committed manifest, record the manifest SHA-256, and prove the source fixture tree is unchanged.
11. Run the repository-authored Docker full gate:

   `make validate-docker`

The Docker gate must build a fresh image and install Poetry plus runtime/dev dependencies. Host `ModuleNotFoundError` or a stale prebuilt image is not a blocker unless the repository-authored command itself fails.

Record exact passed, failed, skipped, deselected, xfailed, xpassed, and warning counts for every pytest gate. Record Ruff, JSON, compilation, diff, owned-path, deterministic replay, source-tree immutability, Docker, worktree, push/fetch, and local/remote equality results.

Task-owned implementation or focused-test failures are unfinished work. A genuine external blocker requires the exact failing repository-authored command, full diagnostics, attempted remediation, and a live resolution condition.

## Publication contract

On success:

1. Create one implementation commit containing the source contract, builder, manifest, tests, and producer documentation.
2. Update the three execution files to `ready_for_review` with exactly one implementation SHA, exact validation counts, source pins, paths, checksums, all 12 cases, limitations, validation debt, sibling impact, consumer verification, and unchanged authority.
3. Freeze the complete task-owned tree and rerun the entire required gate.
4. Create one exact-tree publication receipt commit whose message identifies:
   - task ID;
   - implementation parent SHA;
   - validation commands and exact results;
   - evidence source;
   - worktree state;
   - authority impact.
5. Do not modify task-owned files after the receipt.
6. Push only the declared feature branch, fetch it again, and prove local/remote exact-head equality.

Successful publication must preserve:

- task execution true;
- correction execution false;
- merge authority false;
- PR authority false;
- capability authority unchanged;
- `mmm_compatibility_emitted: false`;
- `calibration_signal_emitted: false`.

Stop without PR or merge.

## Cross-repository resolution condition

GeoX completion advances but does not resolve `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`.

Resolution still requires:

1. this source manifest externally approved and merged on GeoX `main` at an exact SHA;
2. a separately authorized and merged MMM producer task publishing compatibility fixtures linked to the exact GeoX evidence identities and merged pin;
3. MIP consumer verification of both producer artifacts;
4. a MIP-owned blocker transition and separate authorization to resume its bridge.

GeoX does not authorize the MMM or MIP steps.

## Correction limit and terminal condition

At most one externally directed correction cycle is permitted.

Progress reports are non-terminal. Execution stops only when the exact remote feature branch durably records:

1. fully validated `ready_for_review`; or
2. a genuine external `blocked` state with complete diagnostics and a live resolution condition.

No PR, merge, squash, rebase, force-push, merge commit, analytical change, sibling implementation, or capability change is authorized.

**Unresolved execution-blocking design questions: none.**
