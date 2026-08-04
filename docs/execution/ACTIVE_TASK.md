# Active Task

**Status:** ready_for_review
**Owner:** GeoX governed-readout producer contract and certified-fixture owner
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `GEOX_CERTIFIED_CALIBRATION_HANDOFF_SOURCE_FIXTURE_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Pre-authoring base:** `e9b7d311ecaf5a90e227d8299f745a0e8f332368`
- **Feature branch:** `feat/geox-certified-calibration-handoff-source-fixture-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 3 — producer contract and certified cross-repository source fixture
- **Coordination workstream:** `WS-GEOX-CALIBRATION-HANDOFF-SOURCE-FIXTURE-001`
- **Capability authorizations changed:** `false`

## Primary independently mergeable outcome

Publish a provenance-complete, non-authorizing GeoX calibration-handoff **source fixture** over the existing 12 certified `GeoXGovernedExperimentReadout` fixtures.

The artifact must give MIP and MMM a stable producer-owned evidence identity, exact fixture time scope, freshness provenance, governed method eligibility, source paths, and checksums without changing any existing experiment estimate, uncertainty value, readout status, handoff decision, or other analytical truth.

This task resolves only the GeoX producer-source portion of MIP blocker `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`. It does not produce the linked MMM compatibility result and does not by itself resolve MIP consumer verification.

## Live prerequisite evidence

Connected GitHub verification before authorization established:

- GeoX `main`: `e9b7d311ecaf5a90e227d8299f745a0e8f332368`.
- The prior GeoX branch-binding reauthoring task is superseded without merge, with no remaining execution, correction, merge, PR, analytical, or capability authority.
- The certified governed-readout fixture checkpoint is merged at `860182386c39f487747de5f43e67a31e9978e57c` and remains an ancestor of live GeoX `main`.
- Canonical source contract: `panel_exp/contracts/geox_governed_experiment_readout.py`.
- Canonical source fixture root: `tests/fixtures/geox_governed_readouts/`.
- The source manifest contains 12 cases and explicitly records `mmm_compatibility_emitted: false` and `production_authorized: false`.
- MIP `main`: `0b4cd1fca73716e4968c2ceb70c594ad8aadd8ca`.
- MIP task `MIP_P2_GEOX_MMM_COMPATIBILITY_FIXTURE_BRIDGE_001` is durably blocked on remote branch head `480b32040ce185b8ff091435121c4bea6fc6c453` by `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`.
- MMM `main`: `f2e0eade0ad917c1b28ab5521e6d35a35047d988`; its current task is a non-executable proposed governance task and does not overlap this GeoX producer surface.
- No existing active, authorized, review-ready, blocked, or recently completed GeoX task publishes this calibration-handoff source fixture.

Before implementation, re-fetch all three repositories and fail closed if these mains, source paths, ownership boundaries, blocker identity, or sibling task states have materially changed.

## Exact observable behavior

### 1. Add a producer-owned source contract

Add `GeoXCalibrationHandoffSourceRecord` and its strict parser, serializer, and validator.

The record is a certified metadata envelope over one existing governed-readout fixture. It must preserve or reference producer truth; it must not calculate new analytical values.

Each record must contain at least:

- source schema version and record version;
- deterministic `handoff_source_id`;
- deterministic `evidence_artifact_id`;
- source `readout_id`, readout version, artifact version, experiment ID, fixture ID, dataset version, and truth version;
- exact source repository;
- exact 40-character merged source-fixture commit `860182386c39f487747de5f43e67a31e9978e57c`;
- task authorization base pin for the contract and fixture layout;
- producer package version and the source readout's embedded producer/provenance fields verbatim;
- exact repository-relative paths to `governed_readout.json`, `source_truth.json`, and `replay.json`;
- SHA-256 checksum for each referenced source file;
- KPI, KPI units, estimand, effect scale, channel, tactic, geography scope, and geo grain copied exactly from the source readout;
- effect estimate and all uncertainty fields copied exactly, including null values;
- exact UTC `time_window_start` and `time_window_end` for the synthetic fixture scope;
- exact UTC `produced_at` and `freshness_evaluated_at` metadata;
- an explicit `synthetic_fixture_time_scope: true` marker;
- freshness status copied from the source readout;
- method family, instrument ID, design type, feasibility status, and source method status copied verbatim;
- a closed `method_eligibility_status` with values limited to `candidate`, `diagnostic_only`, `research_only`, `blocked`, or `unsupported`;
- readout status, handoff eligibility, warnings, blocked reasons, and failure reasons copied exactly;
- lineage linking the fixture, dataset, truth, source readout, source-truth file, and replay file;
- replay metadata copied exactly;
- all source authorization flags copied verbatim and all false.

### 2. Stable identity rules

For each source fixture:

- `handoff_source_id` must be exactly `geox-calibration-handoff-<fixture_id>-v1`.
- `evidence_artifact_id` must be exactly `geox-evidence-<fixture_id>-v1`.
- `source_readout_id` must equal the referenced governed readout's `readout_id`.
- IDs must be unique across the manifest and deterministic across repeated generation.
- No record may use a branch head, unmerged commit, placeholder, short SHA, or generated-at-runtime random identity as producer provenance.

### 3. Exact synthetic temporal and freshness semantics

The existing symbolic values `pre`, `post`, and `pre-post` are insufficient for strict consumer mapping. GeoX therefore owns explicit temporal metadata for these synthetic fixtures.

- Each record must declare UTC datetimes with `time_window_start < time_window_end`.
- The datetimes are synthetic fixture scope only and must be labeled as such.
- They must not be presented as dates of a real experiment.
- `produced_at` must be on or after `time_window_end`.
- `freshness_evaluated_at` must be on or after `produced_at`.
- Fresh and stale records must remain consistent with the source readout's `freshness_status`.
- Generation must use committed deterministic values, not the current clock.

### 4. Governed method eligibility

The new envelope must not reinterpret `method_family` as eligibility.

`method_eligibility_status` must be derived deterministically from existing certified source-truth fields, especially `certification_status`, `mip_handoff_expectation.status`, readout status, feasibility status, and existing handoff eligibility.

Required precedence:

1. failed, blocked, infeasible, or handoff-blocked source evidence maps to `blocked` unless the source explicitly marks the method unsupported;
2. unsupported inference maps to `unsupported`;
3. research-only source evidence maps to `research_only`;
4. diagnostic-only source evidence maps to `diagnostic_only`;
5. only otherwise eligible candidate evidence maps to `candidate`.

The mapping must be exhaustively tested over all 12 existing source cases. Unknown or contradictory source combinations must fail closed rather than defaulting to `candidate`.

### 5. Certified manifest and deterministic builder

Add one committed manifest under:

`tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json`

The manifest must contain exactly 12 records, one for each case in `tests/fixtures/geox_governed_readouts/manifest.json`.

Add a deterministic fixture-generation script that:

- reads only the existing certified GeoX source fixtures;
- validates every governed readout through the canonical contract;
- computes source-file checksums;
- constructs the new source records under the frozen rules;
- writes normalized JSON with stable ordering and formatting;
- never modifies the existing governed-readout fixture tree.

Running the generator twice from the same synchronized tree must produce byte-identical output. The committed manifest must equal regenerated output byte for byte.

### 6. Supported cases

The manifest must retain all 12 certified cases and demonstrate at least:

- eligible clean candidate evidence;
- eligible candidate evidence with warnings;
- stale evidence;
- incompatible/blocked calibration-handoff source evidence;
- failed or conflicting source evidence;
- infeasible design evidence;
- multicell blocked evidence;
- safe blocked evidence;
- diagnostic-only evidence;
- research-only evidence;
- unsupported inference evidence;
- weak-matchability blocked evidence.

This is source-evidence coverage only. Do not label any case MMM-compatible or MMM-incompatible in the new contract or manifest.

### 7. Fail-closed validation

Validation must reject:

- missing or duplicate identities;
- unsupported schema or record versions;
- missing, short, or non-merged source fixture SHA;
- path traversal or a source path outside the certified fixture root;
- missing referenced files;
- checksum mismatch;
- source/readout identity mismatch;
- analytical-field mismatch between the envelope and source readout;
- invalid or non-deterministic timestamps;
- invalid method eligibility or contradictory eligibility mapping;
- unknown terminal states;
- any true source authorization flag;
- any MMM compatibility, `CalibrationSignal`, target-model, calibration-weight, TrustReport, DecisionSurface, recommendation, optimization, assignment, or LLM-decision field.

## Ownership and authority boundaries

GeoX owns this source record because it certifies experiment/readout identity, temporal scope, method/instrument status, handoff eligibility, and producer lineage.

MIP owns construction of its canonical `CalibrationSignal`, consumer reconciliation, orchestration, and trust/reporting behavior.

MMM owns normalization and final calibration-compatibility truth.

This task does not authorize or implement:

- MMM compatibility evaluation or compatibility fixtures;
- a `CalibrationSignal` or MIP evidence artifact;
- changes to experiment estimates, uncertainty, design, assignment, or inference;
- package runtime integration with MIP or MMM;
- TrustReport, DecisionSurface, simulation, optimization, planning, recommendation, LLM, real-data, pilot, or production behavior;
- changes in MIP or MMM repositories.

## Owned paths

Implementation may modify only:

1. `panel_exp/contracts/geox_calibration_handoff_source.py`
2. `panel_exp/contracts/__init__.py`
3. `scripts/build_geox_calibration_handoff_source_fixtures.py`
4. `tests/contracts/test_geox_calibration_handoff_source.py`
5. `tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json`
6. `docs/track_d/GEOX_CERTIFIED_CALIBRATION_HANDOFF_SOURCE_FIXTURE_001.md`
7. `docs/track_d/archives/GEOX_CERTIFIED_CALIBRATION_HANDOFF_SOURCE_FIXTURE_001_summary.json`
8. `docs/execution/ACTIVE_TASK.md`
9. `docs/execution/EXECUTION_STATE.json`
10. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify the existing `tests/fixtures/geox_governed_readouts/**` files.

## Named acceptance evidence

Focused tests must separately prove:

1. strict record parsing, serialization, and supported versions;
2. exactly 12 manifest records and one-to-one source-manifest coverage;
3. stable exact identity rules and uniqueness;
4. exact source paths, 40-character merged source-fixture pin, and SHA-256 checksums;
5. analytical and governance fields match the source readout exactly, including nulls;
6. exact UTC temporal ordering and deterministic freshness metadata;
7. exhaustive method-eligibility mapping and fail-closed contradictory cases;
8. warning, stale, blocked, failed, diagnostic-only, research-only, unsupported, and candidate coverage;
9. all authorization flags remain false and prohibited fields remain absent;
10. generator replay twice is byte-identical and equals the committed manifest;
11. existing governed-readout fixture files remain unchanged;
12. no MMM compatibility is emitted or calculated.

Tests must parse actual fixture payloads and compare actual values. Documentation-text searches are not acceptance evidence.

## Validation gate

This Tier-3 task requires, on the frozen final task-owned tree:

- parse every changed JSON file;
- Python compilation for changed Python files;
- `git diff --check`;
- exact owned-path verification;
- focused pytest for `tests/contracts/test_geox_calibration_handoff_source.py`, with exact pass/fail/skip/xfail counts;
- existing adjacent governed-readout fixture and contract tests;
- configured Ruff and mypy for all changed Python files;
- deterministic fixture generation twice with byte-identical output;
- Docker-backed full repository validation through `make validate-docker`, with exact counts and warnings;
- exact-tree publication receipt;
- clean worktree except permitted local-only `.codex/` and `docs/tasks/` content;
- exact local/remote feature-branch equality after push.

Focused-test success cannot hide full-suite debt. If Docker-backed full validation cannot complete, publish a truthful Git-durable `blocked` state with exact diagnostics and a live resolution condition.

Task-owned implementation or focused-test failures are unfinished work and must be corrected within scope; they are not an acceptable external blocker.

## Task-authoring and authorization boundary

- Pre-authoring base: `e9b7d311ecaf5a90e227d8299f745a0e8f332368`.
- The task-authoring range may change only `docs/execution/ACTIVE_TASK.md` and `docs/execution/LATEST_COMPLETION_REPORT.md`.
- The commit containing the authorization report is the final task-authoring head.
- The immediate next commit must change only `docs/execution/EXECUTION_STATE.json`, record that exact task-authoring head as `authorization_head_sha`, and authorize the exact feature branch.
- Create the feature branch from the resulting synchronized state-only main head.

## Publication contract

On successful execution, publish one exact remote `ready_for_review` head containing:

- one implementation SHA and one exact-tree publication receipt;
- exact source fixture pin, paths, checksums, supported cases, and consumer-use boundary;
- exact changed paths;
- focused, adjacent, and full validation counts;
- JSON, compilation, diff-check, Ruff, mypy, deterministic replay, and Docker results;
- GitHub-observed evidence separated from locally reported validation;
- blockers, limitations, validation debt, sibling impact, and consumer verification still required;
- task execution true, correction execution false, merge and PR authority false;
- no capability-authority change;
- exact local/remote branch-head equality.

Stop without PR or merge.

## Cross-repository resolution condition

GeoX completion advances but does not resolve `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`.

Resolution still requires:

1. this task merged on GeoX `main` at an exact approved SHA;
2. MMM separately publishing a certified compatibility fixture whose source readout and evidence lineage point to this exact GeoX source record;
3. MIP consumer verification of both merged producer pins and paths;
4. a MIP-owned blocker transition and separate authorization to resume its bridge.

GeoX does not authorize the MMM or MIP steps.

## Correction limit

At most one externally directed correction cycle is permitted. A second failed exact-head review supersedes this task without merge.

**Unresolved execution-blocking design questions: none.**
