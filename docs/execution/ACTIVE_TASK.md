# Active Task

**Status:** changes_requested
**Owner:** GeoX repository governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Current verified GeoX main:** `ee9673c13e69082367c1727568946ac4c1a01015`
- **Feature branch:** `feat/geox-governed-readout-builder-package-entrypoint-001`
- **Execution mode:** `branch_and_fast_forward`
- **Latest partial substantive implementation:** `722090d03b10eb0864337815c80b8e01f00cdfae`
- **Latest rejected review head:** `593522bc6c2d62872d9bc11f68c312321539266f`
- **Prior rejected substantive implementation:** `865d8641ae44b8b47ec64d62825a29e23490d0d6`
- **Canonical MIP coordination closure:** `Phani-Pavuluri/marketing_intelligence_platform@3520176126d129e9288a9ce37591299ec856650a`
- **Live MIP main observed at review:** `11c062eb785b3518d531992aa554d0a3a4c0b84b`
- **MIP resolver review head observed:** `abf57a6fb0c08d23fb51c56a5ea744445b3ab82c`
- **MMM checkpoint:** `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Capability authorizations changed:** `false`

## Current review decision

The latest completion report is not accepted as a valid blocked completion.
Commit `722090d03b10eb0864337815c80b8e01f00cdfae` is a real substantive commit,
but it is only a partial checkpoint. It adds a certified fixture loader and a
truly optional no-envelope return path. It does not complete the typed producer
contract, governed-readout temporal lifecycle, freshness/status/eligibility
matrix, end-to-end version/provenance agreement, committed all-12 fixture test
matrix, stable context index, or Track-D evidence.

The completion report also contains two incompatible current narratives: its
opening describes the new partial implementation and a dependency-install stall,
while most of the report still describes the earlier metadata-only rejected
head and states that no substantive implementation exists. Current evidence must
replace stale current-state prose rather than be appended to it.

Continue on the same branch and preserve history. Do not merge, create a pull
request, replace the task, or create a replacement branch.

## Ownership and non-overlap

This task owns only GeoX producer behavior:

- governed experiment readout construction;
- experiment-readout temporal and deterministic freshness semantics;
- schema, producer, provenance, replay, and fixture-manifest agreement;
- exact certified GeoX readout reproduction;
- GeoX handoff eligibility; and
- GeoX producer tests and evidence.

Do not implement or copy:

- the MIP active-task resolver, task selection, consumer contracts,
  orchestration, coordination engine, or downstream journey;
- MMM normalization, calibration compatibility truth, or cross-repository
  consumer fixtures;
- `CalibrationSignal`, `TrustReport`, `DecisionSurface`, recommendations,
  optimization, runtime integration, scheduling, or consumer acceptance.

MIP's resolver work is separate and may proceed independently. MMM has no active
implementation task. Producer completion does not imply MMM or MIP acceptance.

## Mandatory bootstrap

Before every execution cycle:

1. Classify the complete worktree. Permit local-only untracked content only under
   `.codex/` and `docs/tasks/`; stop on unrelated tracked changes or other
   unexpected untracked paths.
2. Fetch and prune all affected repositories, hydrate required history, switch
   GeoX to `main`, pull with `--ff-only`, and prove local `main == origin/main ==
   ee9673c13e69082367c1727568946ac4c1a01015`.
3. Verify MMM `origin/main ==
   1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421` and read its current execution
   state.
4. Fetch live MIP. Prove canonical coordination closure `3520176...` remains an
   ancestor of live MIP main, then read live MIP execution and coordination
   evidence. Later MIP governance is not a GeoX blocker unless it changes GeoX
   ownership, adds a GeoX-recorded dependency, invalidates authority, or changes
   an applicable contract.
5. Read root `AGENTS.md`, all four GeoX execution files, the complete branch
   history and diff, builder/contracts, manifest and fixture evidence, tests, and
   Track-D artifacts.
6. Verify the feature branch descends from current GeoX main and preserves all
   rejected history without rewrite.

Stop on stale evidence, duplicate ownership, unclear authority, unresolved
ancestry, or unrelated tracked changes.

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
readout-policy, MIP, or MMM path is authorized.

## Checkpointed execution contract

The agent must complete the task in the following order. Each checkpoint must
produce a substantive commit and a checkpoint result in the completion report.
A later checkpoint cannot compensate for an incomplete earlier checkpoint.

### Checkpoint A — typed contract and temporal lifecycle

Complete explicit serialization-safe typed structures for:

- producer and analytical identity;
- effect and uncertainty values and semantics;
- disposition, warnings, blockers, and failures;
- lineage, provenance, replay, schema, and transport metadata;
- pre/post boundaries, artifact creation, evidence/as-of, valid-through, and
  caller-supplied reference time.

The primary public builder must no longer use broad `Mapping[str, Any]` objects
for the core producer, analytical, uncertainty, disposition, provenance, replay,
or transport contract. An already-created-readout helper may remain only as an
explicit validation or optional-envelope helper.

Preserve every lifecycle timestamp in the governed artifact. Validate UTC
normalization, pre/post ordering and overlap, creation/as-of/valid-through
chronology, and malformed or timezone-ambiguous input.

Freshness is deterministic:

- `reference_time <= valid_through` is `fresh`;
- `reference_time > valid_through` is `stale`.

`unknown` or `stale` evidence must fail closed for
`eligible_for_compatibility_evaluation`. Computed freshness, readout status, and
handoff eligibility must agree. Never read the wall clock or silently refresh
evidence.

**Checkpoint A exit evidence:** changed contract and builder paths, focused
positive/boundary/negative tests, and no unresolved broad primary mappings.

### Checkpoint B — certified fixture, version, and envelope conformance

Use one deterministic public fixture path that loads manifest context,
immutable `source_truth.json`, certified `governed_readout.json`, and
`replay.json`; validates all identities and versions; and reproduces the
certified governed readout exactly.

Preserve all certified identifiers, effect and uncertainty values and semantics,
method family, instrument identity, statuses, handoff eligibility, warnings,
blockers, failures, lineage, replay, and provenance. Do not fabricate or default
KPI units, channel, tactic, geography, time-window labels, statuses, identifiers,
package versions, commits, schema hashes, or dispositions.

Define and enforce analytical schema identity/version, record kind, envelope
version, producer package version and commit, provenance package version and
commit, replay version, fixture-manifest version, and schema hash. Reject empty,
malformed, `unknown`, unsupported, fake, or contradictory values.

The transport envelope must be genuinely optional. When requested, every field
must be explicit, validated, non-fabricated, and downstream-blocked.

**Checkpoint B exit evidence:** all 12 manifest cases pass the committed public
fixture test path; canonical JSON round-trip and replay pass; manifest/readout/
replay/envelope agreement is demonstrated; immutable source-truth files are
unchanged.

### Checkpoint C — test, evidence, and stable handoff completion

Commit the complete positive, boundary, negative, fixture, replay, version,
provenance, authorization, import, and deterministic-serialization test matrix.
Ad hoc commands or uncommitted loops do not satisfy the all-12 requirement.

Convert `REPOSITORY_CONTEXT_INDEX.md` into a stable navigation index. It must
point to the three mutable execution files, distinguish the canonical MIP closure
from live-overlay observations, retain the MMM checkpoint, preserve authority
boundaries, and not repeat mutable task identity or status as current truth.
Strengthen `tests/test_repo_native_execution_handoff.py` semantically without
copying the MIP resolver into GeoX.

Expand both Track-D artifacts with exact contracts, supported versions,
temporal/freshness rules, per-fixture outcomes, exact changed paths, commands and
counts, GitHub-observed versus locally reported evidence, limitations, validation
debt, workstream/blocker IDs, sibling impact, consumer verification, remaining
MMM/D6 blockers, newly eligible work, recommended next artifact, and unchanged
authority.

The completion report must contain one current decision and one current evidence
narrative. Historical findings must be explicitly labeled historical.

**Checkpoint C exit evidence:** required tests and evidence are committed,
context-index invariants pass, both Track-D artifacts are complete, and exact
owned-path verification passes.

### Checkpoint D — validation and publication

Only after Checkpoints A–C pass:

1. Run the complete focused isolated-Docker/Poetry matrix for the contract,
   builder, all 12 fixtures, optional envelope, numerical-truth preservation,
   imports, replay, version/provenance agreement, and execution handoff.
2. Run Ruff on every changed Python file, configured mypy if present, JSON and
   version checks, deterministic replay checks, `git diff --check`, immutable
   source-truth verification, and exact changed-path verification.
3. Only then run the complete canonical `make validate-docker` gate or current
   repository-defined equivalent.

A full-gate attempt is invalid when any Checkpoint A–C exit condition is absent.
Do not use full validation as a substitute for unfinished implementation.

If the full gate stalls or fails, record the exact command, elapsed duration,
exit/signal/timeout/cancellation state, last completed output, container and
process diagnostics, durable log path, and available passed/failed/skipped/
unexecuted counts. Dependency installation progress or a percentage alone is not
evidence.

## Publication rules

### `ready_for_review`

Allowed only when Checkpoints A–D pass. Record one final implementation-tree SHA
that is a real commit object and an ancestor of the exact remote review head,
exact commands and counts, empty blockers, task execution authorization true,
merge and PR authorization false, null reviewed/approval SHAs, and unchanged
capability authority.

### `blocked`

Allowed only when substantive Checkpoints A–C work has been committed and a
genuine external or validation blocker prevents completion. Record the latest
substantive SHA, exact commands and counts, per-fixture outcomes reached, exact
diagnostics and log path, precise remaining blockers, and unchanged authority.

Incomplete implementation, missing committed tests/evidence, stale prose, or an
out-of-sequence full-gate run is `changes_requested`, not `blocked`.

A metadata-only, context-only, report-only, or validation-only cycle remains
`changes_requested`.

## Proposed reusable follow-up — not authorized here

After the MIP active-task resolver is reviewed, merged, and closed, MIP should
consider a separate owner task:

`MIP_REPOSITORY_EXECUTION_COMPLIANCE_GATES_001`

That proposed task should implement reusable deterministic enforcement for:

- machine-readable owned/required/immutable path manifests;
- required substantive-path and commit checks;
- checkpoint/readiness validation before full repository gates;
- publication-state validation for `changes_requested`, `blocked`, and
  `ready_for_review`;
- exact implementation-SHA object and ancestry checks;
- one-current-decision consistency across state and human-readable files; and
- command-level validation evidence requirements.

It must not modify GeoX or MMM. Later GeoX/MMM adoption would require separate
owner-repository tasks after their active work closes. This proposal is not an
authorization and does not block the current GeoX task.

## Prohibited operations and authority

Do not create a PR, merge, squash, rebase, force-push, rewrite history, delete the
branch, expand owned files, or change capabilities. This task does not authorize
production inference, method selection, design or assignment, causal-readout
production status, multicell/shared-control claims, MMM compatibility,
`ExperimentEvidence`, `CalibrationSignal`, `TrustReport`, `DecisionSurface`,
recommendations, optimization, LLM decisioning, scheduling, live integration,
real data, pilot, production, or package-side agents.
