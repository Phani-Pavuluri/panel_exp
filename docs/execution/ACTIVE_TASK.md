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
- **Latest rejected remote head:** `abb94ef8341cc32d4b1c71a2970286c6be7081c5`
- **Latest rejected substantive implementation:** `865d8641ae44b8b47ec64d62825a29e23490d0d6`
- **Current MIP execution/coordination standard:** `Phani-Pavuluri/marketing_intelligence_platform@3520176126d129e9288a9ce37591299ec856650a`
- **Current MMM workflow checkpoint:** `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Prior GeoX closure:** `GEOX_REPO_NATIVE_EXECUTION_HANDOFF_V2_ADOPTION_RECOVERY_001@e0cef94c063b03b29e1e1760fb1c2320ce497b56`
- **Capability authorizations changed:** `false`

## Purpose

Complete the deterministic, non-production package entrypoint that constructs the
canonical `GeoXGovernedExperimentReadout` and optional blocked transport envelope
from explicit typed producer inputs or certified fixture metadata.

This fourth remediation cycle also absorbs the smallest GeoX execution-handoff
correction required to validate the builder task under the merged MIP execution
model. It does not complete or claim the broader proposed
`GEOX_CROSS_REPOSITORY_COORDINATION_PROTOCOL_ADOPTION_001` workstream.

The LLM or transport layer must not calculate experiment truth. This task must not
run estimators or inference, select methods or assignments, recalculate supplied
analytical values, determine MMM compatibility, or authorize downstream use.
GeoX owns experiment readout truth and handoff eligibility. MMM owns calibration
compatibility. MIP owns orchestration, coordination governance, and consumer
approval boundaries.

## Repository bootstrap and fail-closed checks

Before modifying files:

1. classify the complete worktree; only `.codex/` and `docs/tasks/` may remain
   local-only untracked;
2. run `git fetch --prune origin`, switch to `main`, pull with `--ff-only`, and
   prove local `main == origin/main == ee9673c13e69082367c1727568946ac4c1a01015`;
3. verify MIP `origin/main == 3520176126d129e9288a9ce37591299ec856650a`
   and MMM `origin/main == 1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`;
4. read root `AGENTS.md`, all four GeoX `docs/execution/` orientation files,
   MIP `AGENTS.md`, `TASK_EXECUTION_STANDARD.md`, and the three MIP
   cross-repository coordination files at the exact MIP pin;
5. verify the existing feature branch descends from current GeoX `main`, is
   exactly at or beyond the authorized amendment head, and has no unrelated or
   unexplained tracked changes; and
6. stop with an accurate blocked result on stale pins, overlapping ownership,
   unresolved ancestry, duplicate implementation, or unclear authority.

Do not create a replacement task or branch.

## Review lineage

The following commits remain audit evidence and are not approved:

- `ce672f348b5ac45dda3935597689fa1c7f5ddb12` — initial prebuilt-readout wrapper;
- `380e2034410fabeb5a9f90f92ec31e3875938a49` — partial fixture constructor and
  envelope metadata remediation;
- `a9890e6d62c5e5e5a0c69801ca1c26d960267418` — narrow two-test correction;
- `955ee991fa485e5bbd803e6446472e00520ddacb` — metadata-only blocked report;
- `865d8641ae44b8b47ec64d62825a29e23490d0d6` — partial typed producer and
  temporal construction; and
- `abb94ef8341cc32d4b1c71a2970286c6be7081c5` — rejected blocked review head.

External review of `abb94ef...` returned `CHANGES_REQUIRED`. The branch contains
useful partial work, but it is not approvable or mergeable. Continue by adding new
commits; do not rewrite or discard history.

## Narrow execution-handoff scope amendment

The earlier GeoX workflow-recovery commit
`698dbb36d8e5001d8cda6002e14369b732cb8802` coupled the repository context index
to the mutable active task through this assertion:

```python
assert all(state["task_id"] in text for text in (task, report, context))
```

The merged MIP standard at `3520176...` defines the repository context index as a
stable navigation/bootstrap index. Mutable task identity and review state belong
in `ACTIVE_TASK.md`, `EXECUTION_STATE.json`, and
`LATEST_COMPLETION_REPORT.md`. The one-line correction already present on the
GeoX feature branch is semantically aligned with that standard, but it was not in
the builder task's prior owned-file boundary.

This amendment explicitly authorizes the minimal GeoX correction:

1. convert `docs/execution/REPOSITORY_CONTEXT_INDEX.md` from a stale active-task
   mirror into a stable navigation index;
2. update its MIP pin to `3520176126d129e9288a9ce37591299ec856650a`, retain the
   live MMM pin, point to all three mutable execution files, and preserve GeoX,
   MMM, and MIP authority boundaries;
3. retain the rule that the current task ID must appear in the active task and
   completion report, not necessarily in the stable context index;
4. strengthen `tests/test_repo_native_execution_handoff.py` to verify that the
   context index points to `ACTIVE_TASK.md`, `EXECUTION_STATE.json`, and
   `LATEST_COMPLETION_REPORT.md`, does not claim to be the mutable active-task
   source, and retains current canonical pins; and
5. record this as a narrow prerequisite absorbed by this builder task, not as
   completion of the broader GeoX coordination-protocol adoption proposal.

Do not weaken any other bootstrap, synchronization, status, closure, pin,
validation, or authority invariant.

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
immutable input. No roadmap, investigation ledger, estimator, design, assignment,
inference, readout-policy, MIP, or MMM file is authorized.

## Required builder corrections

### 1. Complete typed construction contracts

Define explicit serialization-safe typed structures for producer metadata,
analytical identity and values, uncertainty, disposition, temporal boundaries,
lineage, provenance, replay, schema/version identity, and transport metadata.

The primary public builder must construct a governed readout from:

- explicit validated typed producer inputs; or
- a validated certified fixture readout and manifest/replay context.

An already-created-readout helper may remain only as a clearly named validation
or optional-envelope helper. A broad `Mapping[str, Any]` cannot remain the main
producer contract. Do not fabricate or hard-code absent KPI units, channel,
tactic, geography, time-window labels, statuses, request IDs, fingerprints,
package versions, commits, schema hashes, or analytical dispositions.

The optional envelope must actually be optional. When requested, all envelope
metadata must be explicit, validated, non-fabricated, and blocked for downstream
consumption.

### 2. Preserve temporal semantics in the governed artifact

Represent and deterministically serialize timezone-aware UTC values for:

- pre-period start and end;
- post-period start and end;
- artifact creation time;
- evidence/as-of time;
- valid-through or expiry time; and
- caller-supplied reference time used for freshness evaluation.

Do not parse these values and then discard creation, as-of, or validity semantics.
Validate pre/post ordering and overlap, and define defensible creation/as-of/
valid-through chronology. Add tests that prove each rule rather than relying on
untested positional comparisons.

Freshness is deterministic:

- `reference_time <= valid_through` is `fresh`;
- `reference_time > valid_through` is `stale`.

Missing reference or validity data may produce `unknown` only for explicitly
diagnostic or blocked records. `unknown` or `stale` evidence must fail closed for
`eligible_for_compatibility_evaluation`. Computed freshness, declared readout
status, and handoff eligibility must agree. Never read the wall clock or silently
refresh evidence.

### 3. Enforce schema, kind, package, provenance, replay, and manifest agreement

Define supported values for analytical schema identity/version, record kind,
envelope version, producer package version, producer commit, provenance package
version/commit, replay version, and fixture-manifest version.

Enforce required equality and compatibility across producer input, readout,
lineage/provenance, replay metadata, envelope, fixture manifest, certified
readout, and replay record. Reject empty, malformed, `unknown`, unsupported, or
contradictory values. A schema hash must be explicitly supplied or
deterministically computed from the schema; it must never be a renamed version
string.

### 4. Preserve certified analytical truth and authority

Preserve every certified identifier, effect value, uncertainty value and
semantics, method family, instrument identity, readout status, handoff
eligibility, warning, blocker, failure, lineage, replay field, and provenance
field. The public fixture path must reproduce the certified governed readout,
not derive a different artifact from differently interpreted source-truth fields.

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
- construct or reproduce the governed readout without changing certified
  analytical truth or disposition;
- validate the optional envelope when requested;
- prove canonical deterministic JSON round-trip and replay;
- prove manifest/readout/replay/envelope version and provenance agreement; and
- leave every `source_truth.json` unchanged.

Record an explicit per-fixture outcome in both Track-D evidence artifacts.

### 6. Complete the test matrix

Add tests for:

- direct fully typed construction;
- optional envelope behavior;
- all 12 fixture cases;
- exact equality with certified governed readouts where required;
- expiry equality and stale transition;
- UTC normalization;
- missing, naive, and malformed timestamps;
- reversed and overlapping periods;
- creation/as-of/valid-through chronology;
- stale and unknown freshness restrictions;
- readout-status/freshness/eligibility consistency;
- unsupported schema, envelope, package, provenance, replay, and manifest
  versions;
- contradictory producer/provenance commits and package versions;
- missing or fake metadata and invalid schema hashes;
- unsafe authorization flags;
- deterministic serialization and replay;
- manifest/readout/replay/envelope agreement;
- package-root and `panel_exp.artifacts` imports without circular or shadowed
  imports; and
- the corrected stable-context-index execution-handoff contract.

Two example tests are not sufficient.

### 7. Complete evidence

Expand the Track-D report and machine-readable summary with:

- exact typed input/output contracts and supported versions;
- temporal and freshness rules;
- all 12 fixture outcomes;
- context-index adoption scope and MIP source pin;
- exact changed paths;
- command-level validation evidence and counts;
- GitHub-observed versus locally reported evidence;
- blockers, limitations, and validation debt;
- affected workstream `WS-GEOX-READOUT-BUILDER-001`;
- blockers advanced but not resolved: `P2-GEOX-TEMPORAL-VERSION-SEMANTICS` and
  `P2-GEOX-READOUT-BUILDER-ENTRYPOINT`;
- sibling and MIP/MMM consumer impact;
- required consumer verification;
- remaining MMM normalization and D6 blockers;
- newly eligible work and recommended next artifact; and
- unchanged capability authority.

Producer completion does not resolve consumer blockers. Do not claim MMM or MIP
acceptance.

## Validation sequence

Implementation and focused validation come before the complete repository gate.

1. Commit substantive contract, builder, fixture, test, context-index, and
   evidence changes.
2. Run focused isolated-Docker/Poetry tests for the governed-readout contract,
   builder, all 12 fixtures, envelope, numerical-truth preservation, imports, and
   repository-native execution handoff.
3. Run Ruff for every changed Python file, configured mypy if present, JSON and
   version checks, deterministic replay checks, `git diff --check`, and exact
   changed-path verification.
4. Run the complete canonical `make validate-docker` gate or current
   repository-defined equivalent.

No host-only substitute or inherited validation exception is authorized.

If Docker is unavailable or a full gate is slow/stalled, report the exact command,
elapsed duration, exit/timeout state, last completed test/output,
container/process diagnostics, durable log path, and available
passed/failed/skipped/unexecuted counts. A percentage alone is not evidence.

## Required publication

### Success

Publish `ready_for_review` only after all requirements and validation succeed.
Record exactly one new implementation SHA, exact validation commands and counts,
empty blockers, `task_execution_authorized: true`, `merge_authorized: false`,
null reviewed/approval SHAs, and unchanged capability authority. Push the exact
branch head, prove local/remote equality, and stop.

### Failure

After substantive work is committed, publish an accurate `blocked` state with:

- the exact latest substantive implementation SHA;
- the exact pushed remote branch head reported externally;
- every completed and failed command with counts;
- precise remaining code and validation blockers; and
- unchanged merge and capability authority.

Do not claim no implementation commit exists when committed implementation work
is present.

## Prohibited operations and authority

Do not create a PR, merge, squash, rebase, force-push, rewrite history, delete the
branch, or expand owned files again. This task does not authorize production
inference, method selection, design or assignment, causal-readout production
status, multicell/shared-control claims, MMM compatibility,
`ExperimentEvidence`, `CalibrationSignal`, `TrustReport`, `DecisionSurface`,
recommendations, optimization, LLM decisioning, scheduling, live integration,
real data, pilot, production, or package-side agents.
