# Active Task

**Status:** authorized
**Owner:** GeoX repository governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Current verified main before this authorization:** `ee9673c13e69082367c1727568946ac4c1a01015`
- **Feature branch:** `feat/geox-governed-readout-builder-package-entrypoint-001`
- **Execution mode:** `branch_and_fast_forward`
- **Canonical MIP V2 pin:** `Phani-Pavuluri/marketing_intelligence_platform@38f88467f55d5bc4cc64e5a58b0f08f1639a40d0`
- **Canonical MMM workflow pin:** `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Prior GeoX closure:** `GEOX_REPO_NATIVE_EXECUTION_HANDOFF_V2_ADOPTION_RECOVERY_001@e0cef94c063b03b29e1e1760fb1c2320ce497b56`
- **Capability authorizations changed:** `false`

## Purpose

Complete the deterministic, non-production package entrypoint that constructs the
canonical `GeoXGovernedExperimentReadout` and optional blocked transport envelope
from explicit typed producer inputs or certified fixture metadata.

The LLM or transport layer must not calculate experiment truth. This task must not
run estimators or inference, select methods or assignments, recalculate supplied
analytical values, determine MMM compatibility, or authorize downstream use.
GeoX owns experiment readout truth and handoff eligibility. MMM owns calibration
compatibility. MIP owns orchestration and consumer governance.

## Repository bootstrap and fail-closed checks

Before modifying files:

1. classify the complete worktree; only `.codex/` and `docs/tasks/` may remain
   local-only untracked;
2. run `git fetch --prune origin`, switch to `main`, pull with `--ff-only`, and
   prove local `main == origin/main`;
3. read root `AGENTS.md`, all four `docs/execution/` orientation files, the live
   MIP and MMM pins, the governed-readout contract, fixture manifest, existing
   fixtures, and the prior rejected implementation;
4. verify the existing feature branch descends from current `main`, has no
   duplicate owner, unrelated commits, or unauthorized paths; and
5. stop with an accurate blocked result on stale evidence, changed pins,
   overlapping ownership, unresolved ancestry, or unclear authority.

Do not create a replacement task or branch.

## Audit history and current authorization boundary

The following remote heads are retained as audit evidence and are not approved:

- `ce672f348b5ac45dda3935597689fa1c7f5ddb12` — initial prebuilt-readout wrapper;
- `380e2034410fabeb5a9f90f92ec31e3875938a49` — partial fixture constructor and
  envelope metadata remediation;
- `a9890e6d62c5e5e5a0c69801ca1c26d960267418` — two-test correction;
- `955ee991fa485e5bbd803e6446472e00520ddacb` — metadata-only blocked report after
  a locally reported Docker run stalled around 29%.

This third remediation cycle is authorized on the same feature branch. It must
produce substantive implementation, tests, fixture conformance evidence, and
Track-D evidence beyond `955ee991...`. Another prose-only, state-only, or
validation-only commit is not completion.

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
- `tests/fixtures/geox_governed_readouts/manifest.json`
- `tests/fixtures/geox_governed_readouts/*/governed_readout.json`
- `tests/fixtures/geox_governed_readouts/*/replay.json`
- `docs/track_d/GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001.md`
- `docs/track_d/archives/GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001_summary.json`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Every `tests/fixtures/geox_governed_readouts/*/source_truth.json` file is an
immutable input. No roadmap, investigation ledger, estimator, design, assignment,
inference, readout-policy, MIP, or MMM file is authorized.

## Required implementation

### 1. Typed construction contract

Define explicit serialization-safe typed structures for producer metadata,
analytical identity, temporal boundaries, provenance, replay, and transport
metadata. The primary public builder must construct a governed readout from:

- explicit validated typed producer inputs; or
- a validated certified fixture record and manifest context.

A helper may validate/envelope an already-created readout, but it must be clearly
named and cannot remain the primary construction contract. Do not fabricate or
hard-code absent KPI units, channel, tactic, geography, time-window labels,
statuses, request IDs, fingerprints, package versions, commits, or schema hashes.

### 2. Temporal and freshness semantics

Require timezone-aware timestamps and canonical UTC serialization for:

- pre-period start and end;
- post-period start and end;
- artifact creation time;
- evidence/as-of time;
- valid-through or expiry time; and
- caller-supplied reference time.

Validate ordering, prohibit pre/post overlap, and enforce internal consistency
among creation, as-of, and validity timestamps. Freshness is deterministic:

- `reference_time <= valid_through` is `fresh`;
- `reference_time > valid_through` is `stale`.

Missing reference or validity metadata may produce `unknown` only for explicitly
diagnostic, blocked records. Unknown or stale evidence must fail closed for any
handoff-eligible result. Never read the wall clock or silently refresh evidence.

### 3. Schema, kind, package, provenance, replay, and manifest agreement

Define supported values for analytical schema identity/version, record kind,
envelope version, producer package version, producer commit, provenance package
version, replay version, and fixture-manifest version. Enforce required agreement
across producer input, readout, provenance/lineage, replay metadata, envelope, and
manifest. Reject empty, malformed, `unknown`, unsupported, or contradictory
values. A schema hash must be explicitly supplied or deterministically computed
from the schema; it must never be a renamed version string.

### 4. Preserve analytical truth and authority

Preserve every supplied identifier, effect value, uncertainty value and semantics,
method family, instrument identity, status, warning, blocker, failure, lineage,
replay field, and provenance field. Do not recalculate any estimate or uncertainty.

GeoX handoff eligibility remains limited to:

- `eligible_for_compatibility_evaluation`;
- `ineligible_for_calibration_handoff`; and
- `blocked_for_handoff`.

All authorization flags and the transport envelope remain non-production and
blocked. No MMM compatibility verdict may be emitted.

### 5. Certified fixture conformance

Load all 12 cases through the manifest. For each case:

- construct the governed readout using the public fixture construction path;
- validate the readout and optional envelope;
- preserve source numerical truth and the recorded disposition;
- prove deterministic canonical JSON serialization and replay;
- prove manifest/readout/replay/envelope version agreement; and
- leave `source_truth.json` unchanged.

Fixture files may be migrated only when required by the finalized schema and only
within the owned fixture paths. Record an explicit per-fixture result in evidence.

### 6. Test matrix

Add comprehensive tests covering:

- direct typed construction;
- all 12 fixture cases;
- expiry equality and stale transition;
- UTC normalization;
- missing, naive, and malformed timestamps;
- reversed and overlapping periods;
- invalid creation/as-of/valid-through ordering;
- unknown freshness restrictions;
- unsupported schema, envelope, package, provenance, replay, and manifest versions;
- contradictory producer commit and package/provenance metadata;
- missing or fake metadata and invalid schema hashes;
- unsafe authorization flags;
- deterministic serialization and replay;
- manifest/readout/replay/envelope agreement; and
- imports from package root and `panel_exp.artifacts` without circular or shadowed
  imports.

Two example tests are not sufficient.

### 7. Evidence

Complete the Track-D report and machine-readable summary with:

- exact input/output contracts and supported versions;
- temporal and freshness rules;
- all 12 fixture outcomes;
- exact changed paths;
- command-level validation evidence and counts;
- GitHub-observed versus locally reported evidence;
- blockers, limitations, and validation debt;
- sibling and MIP consumer impact;
- required consumer verification;
- remaining D6/MIP/MMM blockers;
- newly eligible work and recommended next artifact; and
- unchanged capability authority.

## Validation sequence

Implementation and focused validation come before the complete repository gate.
Do not spend a cycle running only the full suite against the rejected partial
implementation.

1. Commit substantive code, fixture, test, and evidence changes.
2. Run focused isolated-Docker/Poetry tests for the governed-readout contract,
   builder, all 12 fixtures, envelope, numerical-truth preservation, import
   health, and execution-handoff state.
3. Run Ruff for every changed Python file, configured mypy if present, JSON and
   version checks, deterministic replay checks, `git diff --check`, and exact
   changed-path verification.
4. Run the complete canonical `make validate-docker` gate or current
   repository-defined equivalent.

No host-only substitute or inherited validation exception is authorized.

If the full Docker gate appears stalled, do not report only a percentage. Capture
and report the exact command, start/end time or elapsed duration, exit/timeout
status, container/process state, last completed test or last output, log path,
and exact passed/failed/skipped/unexecuted counts available. Distinguish a slow
run, an infrastructure failure, a test hang, and a test failure. Preserve the
full-suite debt if no successful final summary is produced.

## Required publication

### Success

Publish `ready_for_review` only after all requirements and validation succeed.
Record exactly one implementation SHA, exact validation commands and counts,
empty blockers, `task_execution_authorized: true`, `merge_authorized: false`,
null reviewed/approval SHAs, and unchanged capability authority. Push the exact
branch head, prove local/remote equality, and stop.

### Failure

After substantive work is committed, publish an accurate `blocked` state with:

- the exact latest substantive implementation SHA;
- the exact remote branch head reported externally after push;
- every completed and failed command with counts;
- precise remaining code and validation blockers; and
- unchanged merge and capability authority.

Do not claim no implementation commit exists when committed implementation work
is present.

## Prohibited operations and authority

Do not create a PR, merge, squash, rebase, force-push, rewrite history, delete the
branch, or expand owned files. This task does not authorize production inference,
method selection, design or assignment, causal-readout production status,
multicell/shared-control claims, MMM compatibility, `ExperimentEvidence`,
`CalibrationSignal`, `TrustReport`, `DecisionSurface`, recommendations,
optimization, LLM decisioning, scheduling, live integration, real data, pilot,
production, or package-side agents.
