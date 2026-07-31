# Active Task

**Status:** authorized
**Owner:** GeoX repository governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Current verified GeoX main:** `ee9673c13e69082367c1727568946ac4c1a01015`
- **Existing feature branch:** `feat/geox-governed-readout-builder-package-entrypoint-001`
- **Pre-authorization branch head:** `69b792bc0dfbae8cd6e8185b9aff5441c558689a`
- **Execution mode:** `branch_and_fast_forward`
- **Latest rejected remote execution head:** `5fd97f87ef19378001fa5f92e6adf17bb00abe25`
- **Latest rejected substantive implementation:** `865d8641ae44b8b47ec64d62825a29e23490d0d6`
- **Canonical MIP coordination closure:** `Phani-Pavuluri/marketing_intelligence_platform@3520176126d129e9288a9ce37591299ec856650a`
- **Live MIP main observed at authorization:** `8655520d895128c0defccf76e632cdb4d1efe891`
- **Current MMM workflow checkpoint:** `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Prior GeoX closure:** `GEOX_REPO_NATIVE_EXECUTION_HANDOFF_V2_ADOPTION_RECOVERY_001@e0cef94c063b03b29e1e1760fb1c2320ce497b56`
- **Capability authorizations changed:** `false`

## Authorization decision

The user authorized continuation of this existing GeoX task on 2026-07-31.
Continue on the same feature branch and preserve all history. Do not merge the
current branch, create a replacement task, create a replacement branch, or open
a pull request.

This authorization requires a new substantive implementation commit after
`865d8641ae44b8b47ec64d62825a29e23490d0d6`. A context-only,
execution-metadata-only, validation-only, or report-only cycle is not execution
of this task.

## Purpose

Complete the deterministic, non-production package entrypoint that constructs
the canonical `GeoXGovernedExperimentReadout` and optional blocked transport
envelope from explicit typed producer inputs or certified fixture metadata.

The task also absorbs the minimum GeoX execution-handoff correction required to
make `REPOSITORY_CONTEXT_INDEX.md` a stable navigation source under the merged
MIP execution model. It does not complete or claim the broader proposed
`GEOX_CROSS_REPOSITORY_COORDINATION_PROTOCOL_ADOPTION_001` workstream.

The LLM or transport layer must not calculate experiment truth. This task must
not run estimators or inference, select methods or assignments, recalculate
supplied analytical values, determine MMM compatibility, or authorize downstream
use. GeoX owns experiment readout truth and handoff eligibility. MMM owns
calibration compatibility. MIP owns orchestration, coordination governance,
consumer contracts, reporting, and approval boundaries.

## Repository bootstrap and live-overlay rule

Before modifying files:

1. Classify the complete worktree. Only `.codex/` and `docs/tasks/` may remain
   local-only untracked; stop on unrelated tracked changes or other unexpected
   untracked paths.
2. Run `git fetch --prune origin`, hydrate required history, switch to `main`,
   pull with `--ff-only`, and prove local `main == origin/main ==
   ee9673c13e69082367c1727568946ac4c1a01015`.
3. Verify MMM `origin/main ==
   1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`.
4. Fetch live MIP `origin/main`. Do not require it to equal a permanently frozen
   current-main SHA. Instead prove canonical coordination closure
   `3520176126d129e9288a9ce37591299ec856650a` is an ancestor of live MIP main,
   then read live MIP `AGENTS.md`, execution state, active task, completion
   report, coordination protocol, coordination state, and coordination history.
5. Apply the MIP live-overlay rule: later MIP governance commits are not a GeoX
   blocker unless live evidence changes GeoX ownership, adds a repository-owned
   dependency, invalidates this task's authority, or changes an applicable
   contract requirement. MIP cannot authorize, split, rename, or implement this
   GeoX task.
6. Read root GeoX `AGENTS.md`, all four GeoX `docs/execution/` files, relevant
   builder/contract/fixture evidence, and the pinned MMM evidence.
7. Verify the existing feature branch descends from current GeoX `main`, includes
   pre-authorization head `69b792bc0dfbae8cd6e8185b9aff5441c558689a`,
   and has no unrelated or unexplained tracked changes.
8. Stop with an accurate `blocked` result on stale GeoX/MMM evidence, overlapping
   ownership, unresolved ancestry, duplicate implementation, unclear authority,
   or a material live MIP change affecting GeoX.

## Review lineage

The following commits remain rejected audit evidence and are not approved:

- `ce672f348b5ac45dda3935597689fa1c7f5ddb12` — initial prebuilt-readout wrapper;
- `380e2034410fabeb5a9f90f92ec31e3875938a49` — partial fixture constructor and
  envelope metadata remediation;
- `a9890e6d62c5e5e5a0c69801ca1c26d960267418` — narrow two-test correction;
- `955ee991fa485e5bbd803e6446472e00520ddacb` — metadata-only blocked report;
- `865d8641ae44b8b47ec64d62825a29e23490d0d6` — partial typed producer and
  temporal construction;
- `abb94ef8341cc32d4b1c71a2970286c6be7081c5` — rejected third-cycle blocked
  review head; and
- `5fd97f87ef19378001fa5f92e6adf17bb00abe25` — rejected fourth-cycle head that
  changed only execution metadata and the context index, passed five narrow
  tests, and attempted a full gate before substantive remediation.

Branch head `69b792bc0dfbae8cd6e8185b9aff5441c558689a` records the external
`CHANGES_REQUIRED` decision. Add new commits; do not rewrite or discard history.

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

Every `tests/fixtures/geox_governed_readouts/*/source_truth.json` file is an
immutable input. No roadmap, investigation ledger, estimator, design,
assignment, inference, readout-policy, MIP, or MMM file is authorized.

## Required implementation

### 1. Complete typed construction contracts

Define explicit serialization-safe typed structures for producer metadata,
analytical identity and values, uncertainty, disposition, temporal boundaries,
lineage, provenance, replay, schema/version identity, and optional transport
metadata.

The primary public builder must construct a governed readout from either:

- explicit validated typed producer inputs; or
- a validated certified fixture readout with manifest and replay context.

A broad `Mapping[str, Any]` cannot remain the primary producer contract. An
already-created-readout helper may remain only as a clearly named validation or
optional-envelope helper. Do not fabricate or hard-code absent KPI units,
channel, tactic, geography, time-window labels, statuses, request IDs,
fingerprints, package versions, commits, schema hashes, or analytical
dispositions.

The envelope must be genuinely optional. When requested, every envelope field
must be explicit, validated, non-fabricated, and blocked for downstream
consumption.

### 2. Preserve complete temporal semantics

Represent and deterministically serialize timezone-aware UTC values for:

- pre-period start and end;
- post-period start and end;
- artifact creation time;
- evidence/as-of time;
- valid-through or expiry time; and
- caller-supplied reference time used for freshness evaluation.

Do not parse then discard creation, as-of, or validity semantics. Validate
pre/post ordering and overlap plus defensible creation/as-of/valid-through
chronology. Correct the prior positional ordering error and test every rule.

Freshness is deterministic:

- `reference_time <= valid_through` is `fresh`;
- `reference_time > valid_through` is `stale`.

Missing reference or validity data may produce `unknown` only for explicitly
diagnostic or blocked records. `unknown` or `stale` evidence must fail closed for
`eligible_for_compatibility_evaluation`. Computed freshness, readout status, and
handoff eligibility must agree. Never read the wall clock or silently refresh
evidence.

### 3. Enforce schema, kind, package, provenance, replay, and manifest agreement

Define and enforce supported analytical schema identity/version, record kind,
envelope version, producer package version, producer commit, provenance package
version/commit, replay version, fixture-manifest version, and schema hash.

Enforce required equality and compatibility across producer input, governed
readout, lineage/provenance, replay metadata, envelope, fixture manifest,
certified readout, and replay record. Reject empty, malformed, `unknown`,
unsupported, fake, or contradictory values. A schema hash must be explicitly
supplied or deterministically computed from the schema; it must not be a renamed
version string.

### 4. Preserve certified analytical truth and authority

Preserve every certified identifier, effect value, uncertainty value and
semantics, method family, instrument identity, readout status, handoff
eligibility, warning, blocker, failure, lineage, replay field, and provenance
field. The public fixture path must reproduce the certified governed readout,
not derive a different artifact from differently interpreted source-truth
fields.

Do not replace certified values with `unknown`, `currency`, `pre/post`, fixture
IDs, inferred statuses, guessed commits, or other defaults unless those exact
values are certified inputs.

GeoX handoff eligibility remains limited to:

- `eligible_for_compatibility_evaluation`;
- `ineligible_for_calibration_handoff`; and
- `blocked_for_handoff`.

All authorization flags and transport envelopes remain non-production and
blocked. No MMM compatibility verdict may be calculated or emitted.

### 5. Conform all 12 certified fixtures

Load every manifest case through one deterministic public fixture path. For each
case:

- load immutable `source_truth.json`, certified `governed_readout.json`, and
  `replay.json`;
- validate manifest and version context;
- reproduce the governed readout without changing certified analytical truth or
  disposition;
- validate the optional envelope when requested;
- prove canonical deterministic JSON round-trip and replay;
- prove manifest/readout/replay/envelope version and provenance agreement; and
- leave every `source_truth.json` unchanged.

Record an explicit per-fixture result in both Track-D evidence artifacts.

### 6. Correct the stable execution-handoff contract

Convert `docs/execution/REPOSITORY_CONTEXT_INDEX.md` from a stale active-task
mirror into a stable navigation index. It must:

- point to `ACTIVE_TASK.md`, `EXECUTION_STATE.json`, and
  `LATEST_COMPLETION_REPORT.md` as mutable execution sources;
- record canonical MIP coordination closure separately from the live MIP
  observation rule;
- retain the live MMM checkpoint;
- preserve GeoX, MMM, and MIP authority boundaries; and
- not claim to be the mutable active-task source.

Strengthen `tests/test_repo_native_execution_handoff.py` to enforce those
invariants. The current task ID must appear in the active task and completion
report, but need not appear in the stable context index. Do not weaken any other
bootstrap, synchronization, closure, validation, status, or authority invariant.

### 7. Complete the test matrix and evidence

Add tests for fully typed direct construction, optional envelope behavior, all 12
fixtures, exact certified equality, deterministic serialization/replay, UTC
normalization, expiry equality and stale transition, missing/naive/malformed
timestamps, reversed/overlapping periods, creation/as-of/valid-through
chronology, stale/unknown restrictions, status/freshness/eligibility consistency,
unsupported versions, contradictory commits/package versions, fake metadata,
invalid schema hashes, unsafe authorization flags, manifest/readout/replay/
envelope agreement, and package-root/import health.

Expand both Track-D artifacts with contracts, supported versions, temporal and
freshness rules, all 12 fixture outcomes, exact changed paths, command-level
validation evidence and counts, GitHub-observed versus locally reported
evidence, blockers, limitations, validation debt, workstream and blocker IDs,
sibling impact, consumer verification, remaining MMM/D6 blockers, newly eligible
work, recommended next artifact, and unchanged capability authority.

Producer completion does not resolve consumer blockers. Do not claim MMM or MIP
acceptance.

## Validation sequence

Implementation and focused validation must precede the complete repository gate.

1. Commit substantive contract, builder, fixture, test, context-index, and
   evidence changes.
2. Prove the changed paths include substantive builder/contract/test/evidence
   work beyond execution metadata and the context index.
3. Run focused isolated-Docker/Poetry tests for the governed-readout contract,
   builder, all 12 fixtures, envelope, numerical-truth preservation, imports, and
   repository-native execution handoff.
4. Run Ruff for every changed Python file, configured mypy if present, JSON and
   version checks, deterministic replay checks, `git diff --check`, and exact
   changed-path verification.
5. Run the complete canonical `make validate-docker` gate or current
   repository-defined equivalent only after all preceding checks pass.

No host-only substitute or inherited validation exception is authorized.

If Docker is unavailable or the full gate stalls, report the exact command,
elapsed duration, exit/timeout state, last completed test/output,
container/process diagnostics, durable log path, and available
passed/failed/skipped/unexecuted counts. A percentage alone is not evidence.

## Required publication

### Success

Publish `ready_for_review` only after all requirements and validation succeed.
Record exactly one new substantive implementation SHA after
`865d8641ae44b8b47ec64d62825a29e23490d0d6`, exact validation commands and
counts, empty blockers, `task_execution_authorized: true`,
`merge_authorized: false`, null reviewed/approval SHAs, and unchanged capability
authority. Push the exact branch head, prove local/remote equality, and stop.

### Failure

After new substantive work is committed, publish an accurate `blocked` state
with the exact latest substantive implementation SHA, exact pushed remote branch
head reported externally, completed and failed commands with counts, precise
remaining code/validation blockers, all fixture outcomes reached, and unchanged
merge/capability authority.

A context-only, execution-metadata-only, validation-only, or report-only result
must remain `changes_requested`; it is not a valid blocked completion.

## Prohibited operations and authority

Do not create a PR, merge, squash, rebase, force-push, rewrite history, delete the
branch, or expand owned files. This task does not authorize production inference,
method selection, design or assignment, causal-readout production status,
multicell/shared-control claims, MMM compatibility, `ExperimentEvidence`,
`CalibrationSignal`, `TrustReport`, `DecisionSurface`, recommendations,
optimization, LLM decisioning, scheduling, live integration, real data, pilot,
production, or package-side agents.
