# Active Task

**Status:** blocked
**Owner:** GeoX repository governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Current verified GeoX main:** `ee9673c13e69082367c1727568946ac4c1a01015`
- **Existing feature branch:** `feat/geox-governed-readout-builder-package-entrypoint-001`
- **Execution mode:** `branch_and_fast_forward`
- **Exact rejected review head:** `593522bc6c2d62872d9bc11f68c312321539266f`
- **Correction authorization prewrite head:** `69b792bc0dfbae8cd6e8185b9aff5441c558689a`
- **Prior authorization metadata head:** `548248f0a057cb7db1abba569f935c5e7e24bf3f`
- **Latest rejected substantive implementation:** `865d8641ae44b8b47ec64d62825a29e23490d0d6`
- **Canonical MIP coordination closure:** `Phani-Pavuluri/marketing_intelligence_platform@3520176126d129e9288a9ce37591299ec856650a`
- **Live MIP main at review:** `11c062eb785b3518d531992aa554d0a3a4c0b84b`
- **Live MIP resolver review head:** `abf57a6fb0c08d23fb51c56a5ea744445b3ab82c`
- **Current MMM workflow checkpoint:** `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Capability authorizations changed:** `false`

## External review decision

Exact remote head `593522bc6c2d62872d9bc11f68c312321539266f`
receives **CHANGES_REQUIRED**.

That head changed only:

- `docs/execution/ACTIVE_TASK.md`;
- `docs/execution/EXECUTION_STATE.json`; and
- `docs/execution/LATEST_COMPLETION_REPORT.md`.

It did not add a new substantive implementation after
`865d8641ae44b8b47ec64d62825a29e23490d0d6`, did not modify the builder or
contracts, did not conform the 12 certified fixtures, did not complete the test
matrix or Track-D evidence, and did not correct the stale context index.

The head also published `blocked` after another metadata-only and validation-only
cycle. This contradicts this task's explicit publication rule: a valid blocked
completion requires a new substantive implementation commit and exact
implementation evidence. A metadata-only cycle must remain `changes_requested`.

The complete Docker gate was again attempted before substantive implementation
and the required focused implementation matrix. The reported stall near 29%
without elapsed duration, exit or timeout state, last completed test, process or
container diagnostics, durable log path, or passed/failed/skipped/unexecuted
counts is not sufficient validation evidence.

Continue on the same feature branch and preserve all history. Do not merge,
replace the task, replace the branch, create a pull request, or rerun the full
repository gate before substantive focused implementation and validation pass.

## Parallel-work and authority boundary

The live MIP branch implements only the MIP-owned active-task resolver and is
`ready_for_review` at `abf57a6fb0c08d23fb51c56a5ea744445b3ab82c`.
It does not modify GeoX, authorize GeoX resolver adoption, implement experiment
readout truth, or absorb this builder task.

MMM `main` remains merged and idle for implementation at
`1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`. MMM normalization and certified
cross-repository compatibility fixtures remain separate future MMM-owned work.

This GeoX task must implement only GeoX producer responsibilities:

- governed experiment readout construction;
- GeoX temporal and deterministic freshness semantics;
- schema, producer, provenance, replay, and fixture-manifest agreement;
- certified GeoX fixture reproduction;
- GeoX handoff eligibility; and
- GeoX producer validation and evidence.

Do not implement MIP resolver logic, MIP consumer contracts or orchestration,
MMM normalization or compatibility truth, `CalibrationSignal`, `TrustReport`,
`DecisionSurface`, recommendations, runtime integration, or consumer acceptance.

## Repository bootstrap and live-overlay rule

Before modifying files:

1. Classify the worktree. Only `.codex/` and `docs/tasks/` may remain local-only
   untracked. Stop on unrelated tracked changes or other unexpected untracked
   paths.
2. Run `git fetch --prune origin`, hydrate required history, switch to `main`,
   pull with `--ff-only`, and prove local `main == origin/main ==
   ee9673c13e69082367c1727568946ac4c1a01015`.
3. Verify MMM `origin/main ==
   1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421` and read its live execution
   state before dependent work.
4. Fetch live MIP `origin/main`. Prove canonical coordination closure
   `3520176126d129e9288a9ce37591299ec856650a` remains an ancestor, then read
   live MIP execution and coordination evidence. Do not require live MIP main to
   equal a frozen current-main SHA.
5. Apply the live-overlay rule: later MIP governance work is not a GeoX blocker
   unless it changes GeoX ownership, creates a GeoX-recorded dependency,
   invalidates this task's authority, or changes an applicable contract.
6. Read root GeoX `AGENTS.md`, all four execution files, the exact rejected head,
   the full branch diff, builder/contracts, manifest and all fixture evidence,
   tests, and Track-D artifacts.
7. Verify this branch descends from current GeoX main and contains rejected head
   `593522bc6c2d62872d9bc11f68c312321539266f` without rewritten history.
8. Stop with accurate `blocked` state only after new substantive work exists and
   a genuine implementation or validation blocker remains.

## Owned files

Execution may modify only:

- `panel_exp/contracts/geox_governed_experiment_readout.py`
- `panel_exp/contracts/geox_mip_artifact_envelope.py`
- `panel_exp/contracts/__init__.py`
- `panel_exp/artifacts/geox_governed_readout_builder.py`
- `panel_exp/artifacts/__init__.py`
- `panel_exp/__init__.py`
- `tests/contracts/test_geox_governed_experiment_readout.py`
- `tests/contracts/test_geox_governed_readout_builder_package_entrypoint.py`
- `tests/test_repo_native_execution_handoff.py`
- `tests/fixtures/geox_governed_readouts/manifest.json`
- `tests/fixtures/geox_governed_readouts/*/governed_readout.json`
- `tests/fixtures/geox_governed_readouts/*/replay.json`
- `docs/track_d/GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001.md`
- `docs/track_d/archives/GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001_summary.json`
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Every `tests/fixtures/geox_governed_readouts/*/source_truth.json` is immutable.
No estimator, design, assignment, inference, roadmap, investigation ledger,
readout policy, MIP, or MMM file is authorized.

## Required correction

### 1. Produce a new substantive implementation

Create a new implementation commit after
`865d8641ae44b8b47ec64d62825a29e23490d0d6` that changes substantive
builder/contract/test/fixture/evidence paths. The implementation SHA must be a
real commit object and an ancestor of the eventual review head.

### 2. Complete typed construction contracts

Define serialization-safe typed structures for producer metadata, analytical
identity and values, uncertainty, disposition, temporal boundaries, lineage,
provenance, replay, schema/version identity, and optional transport metadata.

The primary builder must accept explicit typed producer inputs or a validated
certified readout with manifest and replay context. Broad `Mapping[str, Any]`
objects may not remain the primary producer contract. An already-created-readout
helper may remain only as a clearly named validation or optional-envelope helper.

Do not fabricate absent KPI units, channel, tactic, geography, time windows,
statuses, identifiers, package versions, commits, schema hashes, or analytical
dispositions. The transport envelope must be truly optional; when requested,
all metadata must be explicit, validated, non-fabricated, and downstream-blocked.

### 3. Preserve complete temporal and freshness semantics

Represent and deterministically serialize timezone-aware UTC values for:

- pre-period start and end;
- post-period start and end;
- artifact creation time;
- evidence/as-of time;
- valid-through or expiry time; and
- caller-supplied freshness reference time.

Do not parse then discard creation, as-of, or validity timestamps. Correct the
existing chronology comparison, validate ordering and overlap, and test all
boundary and negative cases.

Freshness must follow:

- `reference_time <= valid_through` → `fresh`;
- `reference_time > valid_through` → `stale`.

`unknown` or `stale` evidence must fail closed for
`eligible_for_compatibility_evaluation`. Freshness, readout status, and handoff
eligibility must agree. Never read the wall clock or silently refresh evidence.

### 4. Enforce version, provenance, replay, and manifest agreement

Define supported analytical schema identity/version, record kind, envelope
version, producer package version and commit, provenance package version and
commit, replay version, fixture-manifest version, and schema hash.

Enforce required agreement across producer input, readout, provenance, replay,
envelope, fixture manifest, certified readout, and replay record. Reject empty,
malformed, `unknown`, unsupported, fake, or contradictory values. A schema hash
must be explicitly supplied or deterministically derived from the schema; it may
not be a renamed version string.

### 5. Preserve certified analytical truth and conform all 12 fixtures

The public fixture path must load immutable `source_truth.json`, certified
`governed_readout.json`, `replay.json`, and manifest context, then reproduce the
certified governed readout exactly without changing analytical truth or
certified disposition.

Preserve identifiers, effect and uncertainty values and semantics, method
family, instrument identity, readout status, handoff eligibility, warnings,
blockers, failures, lineage, replay, and provenance. Do not replace certified
values with `unknown`, `currency`, `pre/post`, fixture IDs, inferred statuses,
guessed commits, or other defaults.

For all 12 cases, prove canonical JSON round-trip, deterministic replay,
manifest/readout/replay/envelope agreement, optional envelope behavior, and
unchanged immutable source truth. Record each fixture outcome in both Track-D
artifacts.

### 6. Correct the stable execution handoff

Convert `REPOSITORY_CONTEXT_INDEX.md` from a stale mutable task mirror into a
stable navigation index. It must point to `ACTIVE_TASK.md`,
`EXECUTION_STATE.json`, and `LATEST_COMPLETION_REPORT.md`, distinguish canonical
MIP closure from live overlay, retain the live MMM checkpoint, preserve authority
boundaries, and not claim to be the current-task source.

Strengthen `tests/test_repo_native_execution_handoff.py` semantically. Do not
copy or implement the MIP resolver in GeoX under this task.

### 7. Complete tests and Track-D evidence

Add the complete positive, boundary, negative, fixture, replay, version,
provenance, authorization, import, and deterministic serialization matrix.
Two builder tests and five focused tests are insufficient.

Expand both Track-D artifacts with exact contracts and supported versions,
temporal/freshness rules, all 12 fixture results, exact changed paths, validation
commands and counts, GitHub-observed versus locally reported evidence, blockers,
limitations, validation debt, workstream/blocker IDs, sibling impact, consumer
verification, remaining MMM and D6 blockers, newly eligible work, recommended
next artifact, and unchanged capability authority.

## Validation sequence

Implementation and substantive focused validation must precede the full gate:

1. Commit substantive builder, contract, fixture, test, context-index, and
   evidence changes.
2. Prove changed paths include substantive work beyond execution metadata and
   the context index.
3. Run focused isolated-Docker/Poetry tests for the contract, builder, all 12
   fixtures, optional envelope, numerical-truth preservation, imports, replay,
   version/provenance agreement, and execution handoff.
4. Run Ruff on all changed Python files, configured mypy if present, JSON and
   version checks, deterministic replay checks, `git diff --check`, and exact
   changed-path verification.
5. Only after all focused checks pass, run the complete canonical
   `make validate-docker` gate or current repository-defined equivalent.

No host-only substitute or inherited validation exception is authorized.

If the full gate stalls, record the exact command, elapsed duration, exit or
timeout state, last completed test/output, process and container diagnostics,
durable log path, and available passed/failed/skipped/unexecuted counts. A
percentage alone is not evidence.

## Required publication

### Success

Publish `ready_for_review` only after implementation and all validation succeed.
Record exactly one new substantive implementation SHA after `865d8641...`, exact
commands and counts, empty blockers, task execution authorization true, merge
and PR authorization false, null reviewed/approval SHAs, and unchanged capability
authority. Push the exact branch head and stop.

### Failure

Only after new substantive work is committed may execution publish `blocked`.
Record the exact implementation SHA, exact remote head, completed and failed
commands and counts, per-fixture outcomes reached, precise code and validation
blockers, and unchanged authority.

A context-only, metadata-only, report-only, or validation-only result remains
`changes_requested`.

## Prohibited operations and authority

Do not create a PR, merge, squash, rebase, force-push, rewrite history, delete the
branch, expand owned files, or change capabilities. This task does not authorize
production inference, method selection, design or assignment, causal-readout
production status, multicell/shared-control claims, MMM compatibility,
`ExperimentEvidence`, `CalibrationSignal`, `TrustReport`, `DecisionSurface`,
recommendations, optimization, LLM decisioning, scheduling, live integration,
real data, pilot, production, or package-side agents.
