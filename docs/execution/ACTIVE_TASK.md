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
- **Latest rejected remote head:** `c76bb1f486d346bf090bee9cb7eb02736b243df4`
- **Latest reviewed partial implementation:** `59e3ec6be2d125acdecd9e3870e317d575023894`
- **Prior reviewed partial implementation:** `ec73c47b826941d050b924eef8b5099eabb53895`
- **Canonical MIP coordination closure:** `Phani-Pavuluri/marketing_intelligence_platform@3520176126d129e9288a9ce37591299ec856650a`
- **Live MIP main observed:** `11c062eb785b3518d531992aa554d0a3a4c0b84b`
- **Live MMM main observed:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Capability authorizations changed:** `false`

## Current review decision

Exact remote head `c76bb1f486d346bf090bee9cb7eb02736b243df4` receives **CHANGES_REQUIRED**.

Commit `59e3ec6be2d125acdecd9e3870e317d575023894` is accepted only as narrow, in-scope test progress. It adds an exact object-to-certified-JSON comparison for the 12 manifest cases, but it does not complete the checkpointed task and does not support a valid `blocked` publication.

Continue on the same branch and preserve history. Do not create a replacement task or branch. Do not merge or create a pull request.

## Review findings

### 1. Checkpoint A was skipped

The authorized sequence requires Checkpoint A before B or C. This execution changed only the builder test and execution metadata.

The governed-readout contract still lacks dedicated artifact-creation, evidence/as-of, valid-through, and caller-reference timestamps. The primary direct construction path still carries most analytical, uncertainty, disposition, provenance, replay, and transport fields through broad `Mapping[str, Any]` values. Temporal chronology and the freshness/readout-status/handoff-eligibility matrix remain incomplete.

### 2. Exact certified equality improved, but Checkpoint B remains incomplete

The new assertion comparing the deserialized readout to certified `governed_readout.json` is useful.

However:

- source-truth immutability is not proven: the test computes two hashes consecutively after the builder call, with no pre-call baseline, no manifest hash, and no comparison against certified immutable evidence;
- deterministic replay is not executed: the test only asserts `case_id` and a stored `deterministic` flag;
- canonical serialize/deserialize/replay equivalence is not demonstrated through the public contract;
- manifest/readout/replay/package/provenance/commit/schema/record-kind/schema-hash agreement is not enforced;
- the certified fixture path does not load and validate `source_truth.json` as required;
- the legacy public fixture constructor still fabricates/defaults analytical identity and disposition values;
- the envelope-present path still defaults transport values that must be explicit and non-fabricated.

### 3. Checkpoint C was not executed

`REPOSITORY_CONTEXT_INDEX.md` still mirrors a prior task and contains contradictory MIP pins. The repository-handoff test was not strengthened in this cycle. Both Track-D artifacts remain skeletal. The complete positive, boundary, negative, temporal, replay, version, provenance, authorization, import, envelope, and deterministic-serialization matrix is absent.

### 4. The publication state is invalid

The task contract permits `blocked` only after substantive Checkpoints A-C are complete and a genuine external or validation blocker remains. Here, the listed blockers are unfinished implementation. That state is `changes_requested`, not `blocked`.

The completion report again contains two current narratives: a newly prepended blocked result and the prior `CHANGES_REQUIRED` review. Stable evidence must contain one current implementation identity, one current decision, and one current evidence narrative.

### 5. Validation evidence is incomplete

Deferring the complete Docker gate was correct because A-C are incomplete. The locally reported focused Docker success is not enough to establish completion and lacks exact command, elapsed time, and test counts. GitHub exposes no hosted status or workflow evidence for the submitted head.

## Ownership and non-overlap

This task owns only GeoX producer behavior:

- governed experiment readout construction;
- experiment-truth preservation;
- temporal and deterministic freshness semantics;
- producer schema/version/provenance/replay agreement;
- certified GeoX fixture reproduction;
- GeoX handoff eligibility; and
- GeoX producer validation and evidence.

Do not implement or copy MIP task resolution, MIP consumer contracts/orchestration, coordination infrastructure, downstream journeys, MMM normalization, MMM compatibility truth, or cross-repository consumer fixtures. Do not emit or authorize `CalibrationSignal`, `TrustReport`, `DecisionSurface`, recommendations, optimization, scheduling, live integration, or consumer acceptance.

No duplicate MIP or MMM analytical work was found in the reviewed implementation.

## Mandatory next execution sequence

### Checkpoint A — complete before any further fixture-only work

1. Define explicit serialization-safe typed structures for analytical identity and values, uncertainty, disposition, temporal lifecycle, lineage, provenance, replay, schema identity, and optional transport metadata.
2. Remove broad mappings from the primary producer contract. An already-created-readout helper may remain only as an explicit validator/optional-envelope helper.
3. Preserve pre/post bounds, creation time, evidence/as-of time, valid-through time, and caller reference time in the governed artifact.
4. Enforce UTC normalization, period ordering and overlap, lifecycle chronology, malformed/naive timestamp rejection, expiry equality, and stale/unknown behavior.
5. Enforce one fail-closed consistency matrix among computed freshness, readout status, and handoff eligibility.
6. Commit focused positive, boundary, and negative tests.

### Checkpoint B — complete certified conformance

1. Use one public certified-fixture path that loads manifest context, immutable `source_truth.json`, certified `governed_readout.json`, and `replay.json`.
2. Capture source-truth hashes before execution and compare them afterward and/or against certified manifest hashes.
3. Reproduce all 12 certified governed readouts exactly and prove canonical serialization and actual deterministic replay.
4. Enforce manifest/readout/replay/package/provenance/commit/schema/record-kind/schema-hash agreement.
5. Remove or internalize the fabricated legacy fixture constructor.
6. Require all envelope-present transport metadata explicitly; keep the envelope optional and downstream-blocked.
7. Commit the full all-12 equality, immutability, replay, version, provenance, schema, and envelope matrix.

### Checkpoint C — complete evidence and stable handoff

1. Complete the positive, boundary, negative, temporal, replay, version, provenance, authorization, import, envelope, and deterministic-serialization test matrix.
2. Convert `REPOSITORY_CONTEXT_INDEX.md` into stable navigation to `ACTIVE_TASK.md`, `EXECUTION_STATE.json`, and `LATEST_COMPLETION_REPORT.md`; remove mutable task/status mirroring and contradictory pins.
3. Strengthen `tests/test_repo_native_execution_handoff.py` semantically without copying the MIP resolver.
4. Complete both Track-D artifacts with exact contracts, supported versions, all 12 outcomes, changed paths, commands/counts, limitations, validation debt, sibling impact, consumer verification, blocker transitions, next work, and unchanged authority.
5. Replace stale completion prose with one internally consistent current narrative.

### Checkpoint D — validation and publication

Only after A-C are committed and pass:

1. Run the complete focused isolated-Docker/Poetry matrix.
2. Run Ruff on changed Python files, configured mypy, JSON/version/replay checks, `git diff --check`, immutable source-truth verification, and exact owned-path verification.
3. Confirm no other `panel-exp-validation:local` container is running before launch.
4. Run exactly one complete canonical `make validate-docker` gate.
5. Record exact command, duration, exit state, counts, and diagnostics.

`ready_for_review` requires A-D success. `blocked` is allowed only after substantive A-C completion and a genuine external/validation blocker with exact diagnostics. Incomplete implementation remains `changes_requested`.

## Owned paths

Execution may modify only the previously authorized GeoX builder, contract, export, test, governed-readout/replay fixture, Track-D, context-index, and execution-state paths. Every `tests/fixtures/geox_governed_readouts/*/source_truth.json` file is immutable. No estimator, design, assignment, inference, roadmap, investigation, MIP, or MMM path is authorized.

## Prohibited operations and authority

Do not create a PR, merge, squash, rebase, force-push, rewrite history, delete the branch, expand owned scope, or change capabilities. Production inference, assignment, MMM compatibility, `ExperimentEvidence`, `CalibrationSignal`, `TrustReport`, `DecisionSurface`, recommendations, optimization, LLM decisioning, scheduling, live integration, real data, pilot, production, and package-side agents remain unauthorized.
