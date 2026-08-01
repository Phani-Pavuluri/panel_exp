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
- **Latest reviewed partial substantive implementation:** `ec73c47b826941d050b924eef8b5099eabb53895`
- **Prior partial implementation:** `722090d03b10eb0864337815c80b8e01f00cdfae`
- **Canonical MIP coordination closure:** `Phani-Pavuluri/marketing_intelligence_platform@3520176126d129e9288a9ce37591299ec856650a`
- **Live MIP main observed:** `11c062eb785b3518d531992aa554d0a3a4c0b84b`
- **MMM checkpoint:** `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Capability authorizations changed:** `false`

## Current review decision

The latest work receives **CHANGES_REQUIRED**.

Commit `ec73c47b826941d050b924eef8b5099eabb53895` is a real, in-scope test commit. It adds a manifest loop over all 12 certified fixture IDs and an optional no-envelope assertion. This is useful partial progress, but it does not satisfy Checkpoints A-C and does not justify a full repository gate or a `blocked` publication.

The task remains authorized for correction on the same branch. Preserve history. Do not merge, create a pull request, replace the branch, or create a replacement task.

## Review findings

### Checkpoint A remains incomplete

- The governed-readout contract was not changed.
- The primary direct builder still accepts broad `Mapping[str, Any]` payloads for analytical, uncertainty, disposition, provenance, replay, and transport data.
- Artifact creation, evidence/as-of, valid-through, and reference-time values are not preserved as dedicated governed-readout fields.
- Temporal chronology remains incomplete and the current comparison logic is not a complete lifecycle contract.
- Freshness, readout status, and handoff eligibility are not enforced as one fail-closed matrix.

### Checkpoint B remains materially incomplete

- The 12-case test checks only manifest count, fixture IDs, lineage fixture IDs, and absence of an envelope.
- It does not compare the produced object to certified `governed_readout.json` exactly.
- It does not load or hash immutable `source_truth.json`.
- It does not prove canonical serialization round-trip, deterministic replay, or all certified analytical/disposition fields.
- It does not enforce manifest/readout/replay/package/provenance/commit/schema/record-kind/schema-hash agreement.
- The envelope-present path still permits defaults for fields that must be explicit and non-fabricated.
- The legacy fixture-construction path still fabricates/defaults analytical identity and disposition values and must not remain a public certified path.

### Checkpoint C remains incomplete

- The committed test matrix is still only four tests and lacks the required positive, boundary, negative, replay, version, provenance, authorization, import, and deterministic-serialization coverage.
- `REPOSITORY_CONTEXT_INDEX.md` still mirrors a stale prior task and contains contradictory MIP pins.
- Both Track-D artifacts remain skeletal and lack per-fixture outcomes, exact contracts, supported versions, validation commands/counts, limitations, sibling impact, consumer verification, and validation debt.
- The completion report again contained two current narratives: a new blocked opening followed by the prior `CHANGES_REQUIRED` report. Current evidence must replace stale prose, not be prepended to it.

### Checkpoint D was entered out of sequence

The complete Docker gate was started while Checkpoints A-C were not complete. A dependency-install stall before pytest execution is not a repository validation result and cannot convert incomplete implementation into `blocked`.

No valid full-gate evidence was supplied: exact elapsed duration, exit/signal/timeout/cancellation state, final output, process/container diagnostics, durable log path, and passed/failed/skipped/unexecuted counts remain absent.

## Ownership and non-overlap

GeoX owns only producer readout construction, experiment-truth preservation, temporal/freshness semantics, handoff eligibility, certified GeoX fixture reproduction, and producer evidence.

Do not implement or copy MIP task resolution, orchestration, consumer contracts, coordination infrastructure, or downstream journeys. Do not implement MMM normalization, calibration compatibility truth, or cross-repository consumer fixtures. Do not emit or authorize `CalibrationSignal`, `TrustReport`, `DecisionSurface`, recommendations, optimization, runtime integration, scheduling, or consumer acceptance.

MIP main and MMM main remain unchanged at the observed checkpoints. No duplicate analytical ownership was found.

## Required next execution

Execute only in this order. Each checkpoint must produce committed substantive evidence before moving forward.

### Checkpoint A — typed contract and temporal lifecycle

1. Replace broad primary mappings with explicit serialization-safe types for analytical identity/values, uncertainty, disposition, lineage, provenance, replay, schema/version identity, temporal lifecycle, and optional transport metadata.
2. Preserve pre/post bounds, creation time, evidence/as-of time, valid-through time, and caller reference time in the governed artifact.
3. Enforce UTC normalization, period ordering/overlap, lifecycle chronology, and malformed/naive timestamp rejection.
4. Enforce one fail-closed freshness/status/handoff matrix, including equality-at-expiry and stale/unknown restrictions.
5. Commit focused positive, boundary, and negative tests.

### Checkpoint B — certified fixture, version, and envelope conformance

1. Use one public certified-fixture path that loads manifest context, immutable `source_truth.json`, certified `governed_readout.json`, and `replay.json`.
2. Reproduce each certified governed readout exactly and prove canonical round-trip/replay.
3. Enforce manifest/readout/replay/package/provenance/commit/schema/record-kind/schema-hash agreement.
4. Remove or internalize the legacy fabricated fixture-construction path.
5. Make the envelope optional; when present, require every transport field explicitly and keep it downstream-blocked.
6. Commit the complete 12-case equality, replay, immutability, version, provenance, and envelope matrix.

### Checkpoint C — evidence and stable execution handoff

1. Complete the positive, boundary, negative, authorization, import, replay, version, provenance, and deterministic-serialization test matrix.
2. Convert `REPOSITORY_CONTEXT_INDEX.md` into stable navigation pointing to the three mutable execution files; remove mutable task/status mirroring and contradictory pins.
3. Strengthen the repository-handoff test without copying the MIP resolver.
4. Complete both Track-D artifacts with exact contracts, supported versions, all 12 outcomes, changed paths, commands/counts, limitations, validation debt, sibling impact, consumer verification, blockers, next work, and unchanged authority.
5. Publish one internally consistent completion report narrative.

### Checkpoint D — validation and publication

Only after A-C pass:

1. Run the full focused isolated-Docker/Poetry matrix.
2. Run Ruff on all changed Python files, configured mypy, JSON/version/replay checks, `git diff --check`, immutable source-truth verification, and exact owned-path verification.
3. Run the complete canonical `make validate-docker` gate.

`ready_for_review` requires A-D success. `blocked` is permitted only after A-C are substantively complete and exact external/validation diagnostics are recorded. Incomplete implementation, stale reporting, or an out-of-sequence full gate remains `changes_requested`.

## Owned files

Execution may modify only the existing authorized builder, contract, export, tests, certified governed-readout/replay fixture, Track-D, context-index, and execution-state paths already listed by this task. Every `tests/fixtures/geox_governed_readouts/*/source_truth.json` file is immutable. No estimator, design, assignment, inference, roadmap, investigation, MIP, or MMM path is authorized.

## Prohibited operations and authority

Do not create a PR, merge, squash, rebase, force-push, rewrite history, delete the branch, expand owned scope, or change capabilities. Production inference, assignment, MMM compatibility, `ExperimentEvidence`, `CalibrationSignal`, `TrustReport`, `DecisionSurface`, recommendations, optimization, LLM decisioning, scheduling, live integration, real data, pilot, production, and package-side agents remain unauthorized.
