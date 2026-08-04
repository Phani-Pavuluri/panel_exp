# TASK_REVIEW_REPORT

## Decision

**CHANGES REQUESTED**

- Task: `GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001`
- Rejected exact remote head: `6860d54796ae999184b9ffe3ac5bd16b69e5d745`
- Rejected implementation commit: `8002e83556c324a73b9b51e8cbcb2038a9a2888f`
- Feature branch: `feat/geox-certified-calibration-source-manifest-001`
- Correction cycles used: 1 of 1
- Merge, PR, sibling, analytical, compatibility, `CalibrationSignal`, runtime, planning, recommendation, real-data, and capability authority: false

The blocked publication is rejected. The task's only correction cycle is authorized on the existing feature branch. The complete correction contract is recorded in `docs/execution/ACTIVE_TASK.md`.

## GitHub-observed review findings

### Invalid durable state

`docs/execution/EXECUTION_STATE.json` at the rejected head is not valid JSON: the `blockers` array is missing a comma before `dependencies`. Therefore the claimed changed-JSON parse could not have passed on the published tree.

### Contract and validator failures

The contract is a compressed 28-line implementation with broad `dict`, `list`, and `object` annotations. It checks only top-level key presence, two version strings, loose UTC-offset parsing, lexicographic timestamp ordering, two provenance pins, and false authorization flags. It does not enforce the strict field/nested types, closed vocabularies, exact IDs, exact `Z` form, contextual source equality, path containment, file existence, checksums, prohibited fields, or canonical readout validation required by the task.

The returned `validate()` errors are not enforced by parsing or generation. No contextual validator exists.

### Builder and manifest failures

The builder:

- reconstructs fixture paths instead of using the source manifest paths;
- does not require the exact 12 case IDs or reject duplicates/omissions;
- does not validate governed readouts through the canonical parser and validator;
- does not support isolated output paths;
- does not contextually validate generated records;
- incorrectly sets `certification_status` from readout `method_status` instead of source truth;
- assigns fresh timestamps to every case;
- uses the wrong fresh `freshness_evaluated_at` value;
- does not implement the required stale timestamp mapping.

The committed manifest lacks required top-level case count, repository, source pins, synthetic-scope, compatibility/CalibrationSignal false flags, and production false flag. It uses the record schema as the manifest schema.

### Acceptance and documentation failures

Only three broad tests were added. They do not prove the named behavioral matrix, mutate the committed manifest, do not run two isolated builder outputs, and do not prove source-tree immutability. The Track-D document and archive summary are placeholders rather than required evidence.

### Validation and blocker disposition

Locally reported focused results were `3 passed`; adjacent results were `2 passed`; compilation and diff check were reported passed. No GitHub-observed evidence validates those local counts.

The report does not provide Ruff evidence, exact changed-path verification, changed-JSON parsing, two-run replay, manifest SHA-256, source-tree immutability, worktree state, or exact local/remote verification. No exact-tree receipt exists.

The Docker statement says only that `make validate-docker` stalled during dependency installation. It provides no command transcript, elapsed time, dependency/failure location, Docker/build state, timeout, attempted remediation, or live resolution condition. That is insufficient for a genuine external blocker. Regardless, the task-owned implementation failures above must be corrected before an environment blocker can be accepted.

## Required correction

Replace the rejected contract, builder, tests, manifest, and placeholder documentation with the strict implementation described in `ACTIVE_TASK.md`. Preserve the exact 12 certified source cases and all producer truth. Do not derive method eligibility, emit MMM compatibility, construct `CalibrationSignal`, modify existing governed-readout fixtures, or change authority.

The correction must run all non-Docker gates, two isolated deterministic replays, source-tree immutability proof, and the fresh repository-authored `make validate-docker` path. A future blocked publication must satisfy the full diagnostic and live-resolution contract.

A second failed exact-head review supersedes this task without merge.