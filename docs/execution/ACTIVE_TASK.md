# Active Task

**Status:** authorized
**Owner:** GeoX repository governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001`
- **Pre-authoring base:** `main` / `e0cef94c063b03b29e1e1760fb1c2320ce497b56`
- **Feature branch:** `feat/geox-governed-readout-builder-package-entrypoint-001`
- **Execution mode:** `branch_and_fast_forward`
- **Canonical MIP V2 pin:** `Phani-Pavuluri/marketing_intelligence_platform@38f88467f55d5bc4cc64e5a58b0f08f1639a40d0`
- **Canonical MMM workflow pin:** `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Prior task:** `GEOX_REPO_NATIVE_EXECUTION_HANDOFF_V2_ADOPTION_RECOVERY_001`
- **Prior closure:** `e0cef94c063b03b29e1e1760fb1c2320ce497b56`
- **Capability authorizations changed:** `false`

## Purpose

Implement the deterministic, non-production package entrypoint that builds the
canonical `GeoXGovernedExperimentReadout` and its transport envelope from
explicit already-validated inputs or certified fixture metadata. Close the
producer-side temporal, deterministic freshness/expiry, record-kind/schema, and
producer package-version semantics required by the pinned MIP P2 consumer design.

This task must not run estimators, select methods, assign markets, calculate new
analytical truth, determine MMM compatibility, or authorize downstream use.
The governed readout remains the GeoX analytical artifact; the envelope remains
transport only.

## Prerequisites

Before branching or modification, complete root `AGENTS.md` bootstrap and prove
synchronized `main == origin/main`. Verify:

1. the prior execution-handoff recovery is merged at the recorded closure;
2. the exact MIP and MMM pins exist and preserve current ownership boundaries;
3. `GEOX_GOVERNED_READOUT_ARTIFACT_CONTRACT_001` exists;
4. `GEOX_CERTIFIED_GOVERNED_READOUT_FIXTURES_001` exists and recommends this task;
5. the 12-case numerical-truth validation checkpoint and
   `tests/fixtures/geox_governed_readouts/manifest.json` exist;
6. the unresolved full-suite validation debt is preserved and no prior exception
   is applied to this task.

Stop and publish an accurate blocked state if any prerequisite, exact base,
authorization boundary, branch, or repository condition cannot be verified.

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

The 12 `source_truth.json` files are immutable inputs and are not owned. No
roadmap, investigation ledger, estimator, design, assignment, inference,
readout-policy, MIP, or MMM file is authorized.

## Required implementation

### 1. Typed temporal and freshness semantics

Define deterministic serialization-safe semantics for:

- pre-period start/end;
- post-period start/end;
- artifact creation time;
- evidence/as-of time;
- valid-through or expiry time;
- explicit UTC normalization;
- `fresh`, `stale`, and `unknown` freshness states.

Freshness must be resolved from an explicit caller-supplied reference time. Do
not read the wall clock inside construction, validation, or tests. Define the
exact expiry-boundary rule and reject malformed, timezone-ambiguous, reversed,
overlapping where prohibited, or internally inconsistent periods. Never refresh
or reinterpret stale evidence silently.

### 2. Schema, kind, and package-version semantics

Define and validate explicit:

- analytical artifact schema identity/version;
- envelope schema/version;
- record/artifact kind;
- producer package version and commit;
- provenance package version;
- fixture-manifest schema/package version.

Require agreement across readout, provenance, envelope, and manifest. Reject
unknown, unsupported, or contradictory versions rather than guessing.

### 3. Deterministic builder and package entrypoint

Add a public package entrypoint that:

- consumes explicit validated typed inputs or certified fixture metadata;
- constructs `GeoXGovernedExperimentReadout` deterministically;
- validates before returning;
- may construct the corresponding `GeoXMIPArtifactEnvelope` with
  `GeoXMIPArtifactKind.READOUT_PACKET`;
- preserves source IDs, supplied numerical values, uncertainty, method status,
  lineage, warnings, blockers, failures, replay metadata, and provenance;
- does not recalculate effect estimates or uncertainty;
- does not run estimators or inference;
- does not determine MMM compatibility;
- fails closed on missing, stale, unsupported, contradictory, or unsafe inputs.

GeoX handoff eligibility remains limited to:

- `eligible_for_compatibility_evaluation`;
- `ineligible_for_calibration_handoff`;
- `blocked_for_handoff`.

All authorization flags must remain false. The transport envelope must preserve
its current non-production/blocked authorization boundary.

### 4. Package export and import health

Expose the builder through the appropriate `contracts`, `artifacts`, and package
surfaces without circular imports, synthetic package shadowing, or broad eager
imports. Preserve existing public imports and the repaired import-health path.

### 5. Certified fixture conformance

Update the 12 governed-readout fixtures and replay metadata only as needed for
the finalized schema. Preserve source numerical truth, analytical values,
method families, instrument identities, warnings, blockers, failures, and all
success/warning/stale/incompatible/blocked/failed/diagnostic-only/research-only
dispositions. Do not emit MMM compatibility decisions. Prove deterministic
serialization and replay and version agreement with the manifest.

### 6. Evidence artifact

Add the named Track-D report and machine-readable summary. Record exact input and
output contracts, temporal/freshness rules, schema/version policy, package
entrypoint, fixture compatibility decision, validation evidence, limitations,
unchanged authority, remaining MIP/MMM and D6 blockers, and the recommended next
artifact.

## External review remediation authorization

External review of implementation commit
`ce672f348b5ac45dda3935597689fa1c7f5ddb12` returned
`CHANGES_REQUIRED`. That implementation is preserved as prior-attempt evidence
but is not an approvable or mergeable review head. Continue on the same feature
branch and resolve all findings below before publishing a new review head.

1. Replace the identity validator/wrapper with an actual deterministic builder.
   The public entrypoint must construct `GeoXGovernedExperimentReadout` from
   explicit typed producer inputs or certified fixture metadata. It must not
   require an already-constructed governed readout as its only analytical input.
2. Implement the complete typed temporal contract in the governed readout:
   explicit UTC pre/post boundaries, creation time, evidence/as-of time,
   valid-through/expiry, deterministic reference-time freshness, exact expiry
   equality behavior, and validation for malformed, naive, reversed,
   prohibited-overlap, stale, unknown, and contradictory states.
3. Implement fail-closed schema, record-kind, producer commit, package version,
   provenance, envelope, and fixture-manifest consistency. Do not use a schema
   version as a schema hash and do not fabricate missing metadata such as epoch
   creation time, run identity, request identity, or data fingerprints.
4. Add complete tests for all 12 certified fixtures and for expiry equality,
   UTC normalization, missing/naive/malformed timestamps, reversed and overlapping
   periods, stale and unknown freshness, unsupported versions, contradictory
   provenance/commit/package metadata, unsafe authorization flags, deterministic
   serialization/replay, package import health, and manifest/readout/envelope
   agreement.
5. Expand the Track-D report and JSON summary to record the exact typed contracts,
   rules, supported versions, fixture migration decision, validation commands and
   results, unchanged authority, remaining D6/MIP/MMM blockers, and recommended
   next artifact.
6. Run every focused isolated-Docker gate and the complete canonical Docker gate.
   The prior Docker-unavailable result is not a pass. Host-only execution is not
   an accepted substitute. Publish `blocked` again if Docker remains unavailable
   or any required gate lacks a successful final result.

No owned-file expansion is authorized. Do not discard or rewrite the prior
implementation history; remediate with new commits on the same branch.

## Validation gate

Run focused validation in isolated Docker/Poetry, including:

- governed-readout contract tests;
- new builder/package-entrypoint tests;
- all 12 certified governed-readout fixture validations;
- GeoX/MIP envelope tests;
- numerical-truth fixture validation;
- import-surface health tests;
- repository-native execution-handoff tests.

Also run Ruff on every changed Python file, configured mypy for the changed
surface, JSON parsing/version-consistency checks, deterministic
serialization/replay checks, `git diff --check`, and exact changed-path
verification.

Run the repository's complete canonical Docker validation gate, including
`make validate-docker` or its current repository-defined equivalent. The prior
full-suite exception does not apply. If the complete gate does not finish with a
successful final result, publish `blocked` with exact evidence; do not claim the
full suite passes.

## Acceptance criteria

- A public deterministic builder/package entrypoint exists.
- The builder preserves supplied certified analytical values and computes no new
  analytical truth.
- Temporal boundaries and freshness are typed, UTC-explicit, deterministic, and
  free of wall-clock dependence.
- Schema, record kind, package version, commit, provenance, envelope, and manifest
  agreement is validated fail-closed.
- Unknown or contradictory versions are rejected.
- All 12 certified fixtures validate and round-trip without analytical or
  disposition changes.
- Import surfaces remain healthy.
- GeoX emits handoff eligibility only; MMM compatibility remains MMM-owned.
- All authorization flags remain false.
- No production inference, assignment, TrustReport, CalibrationSignal,
  ExperimentEvidence, DecisionSurface, recommendation, LLM, scheduler, live API,
  or budget-optimization authority is added.

## State transitions

On success, publish `ready_for_review` with populated implementation commit,
empty blockers, `task_execution_authorized: true`, `merge_authorized: false`,
null reviewed/approval SHAs, and unchanged capability authority. Commit and push
the exact feature-branch head, prove local/remote equality, and stop.

On failure, publish an accurate `blocked` state with specific blockers and exact
validation evidence, commit and push the branch, and stop.

Do not create a pull request, merge, squash, rebase, force-push, or delete the
branch during execution.

## Later approved merge

Only external approval of the exact remote review-head SHA authorizes a merge
session. Re-bootstrap, verify unchanged authorization boundary and exact approved
head, rerun all required validation, merge using `git merge --ff-only`, push and
verify `main`, clean the completed branch, and create exactly one post-merge
closure commit updating only the three stable execution files.

## Prohibited authority

This task does not authorize or change estimator execution, method selection,
design eligibility, assignment, inference, causal-readout production status,
multicell/shared-control claims, MMM compatibility, ExperimentEvidence,
CalibrationSignal, TrustReport, DecisionSurface, recommendation, optimization,
LLM decisioning, scheduling, live integration, real data, pilot, production, or
package-side agents.
