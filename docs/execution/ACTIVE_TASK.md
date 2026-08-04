# Active Task

**Status:** blocked
**Owner:** GeoX governed-readout producer contract and certified-fixture owner
**Last updated:** 2026-08-04
**Last verified:** 2026-08-04

## Identity

- **Task ID:** `GEOX_CERTIFIED_CALIBRATION_HANDOFF_SOURCE_FIXTURE_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Feature branch:** `feat/geox-certified-calibration-handoff-source-fixture-001`
- **Authorization head:** `0c7f13509ba8569c132513405cc12f999ab57232`
- **Authorized branch baseline:** `ef6a57382831210c085b4c1351358c3a0743be5e`
- **Rejected exact remote head:** `49059bf5baae58764c7c80e015c8ddccf590117a`
- **Rejected implementation commit:** `191ddbe918cde06ee30c12b3a3d3998e917b86f5`
- **Correction cycle:** one of one; no further correction cycle remains after this execution
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 3 — producer contract and certified cross-repository source fixture
- **Coordination workstream:** `WS-GEOX-CALIBRATION-HANDOFF-SOURCE-FIXTURE-001`
- **Capability authorizations changed:** `false`

## Frozen task contract

The complete task authorized at `0c7f13509ba8569c132513405cc12f999ab57232` remains frozen and authoritative. This correction is additive: it does not narrow the original objective, owned paths, acceptance evidence, validation gate, ownership boundary, or publication contract.

The required outcome remains a provenance-complete, deterministic, non-authorizing GeoX calibration-handoff source fixture over all 12 existing certified `GeoXGovernedExperimentReadout` fixtures. Existing governed-readout payloads and experiment truth remain immutable. GeoX must not emit or calculate MMM compatibility, construct `CalibrationSignal`, alter experiment truth, or authorize MIP, MMM, planning, recommendation, runtime, real-data, pilot, or production behavior.

## Review decision

The exact remote head `49059bf5baae58764c7c80e015c8ddccf590117a` is rejected. It must not be merged or represented as validated. The current implementation is incomplete and its `ready_for_review` publication contradicts the frozen task.

This is the only authorized correction cycle. Task-owned implementation and focused-test failures are unfinished work, not external blockers. The correction must continue until the exact remote feature branch durably records either a fully validated new `ready_for_review` head or a genuine external `blocked` state with exact diagnostics and a live resolution condition.

## Mandatory correction findings

### 1. Publication and validation state

The rejected completion report states that Docker/full validation was unreported while the branch state says `ready_for_review`. The frozen Tier-3 gate requires Docker-backed `make validate-docker`; when it cannot complete, the correct terminal state is `blocked`, not `ready_for_review`.

The correction must:

- run and report every required gate on the final frozen exact tree;
- record exact focused, adjacent, and full-suite passed, failed, skipped, deselected, xfailed, xpassed, and warning counts;
- record Ruff, mypy, JSON, compilation, diff-check, owned-path, deterministic replay, worktree, push, fetch, and local/remote equality results;
- separate GitHub-observed evidence from locally reported validation;
- record blockers, limitations, validation debt, sibling impact, and consumer verification still required;
- publish a genuine exact-tree receipt commit whose commit message identifies the task, implementation parent, exact validation gate/results, evidence source, worktree state, and authority impact;
- never label an unvalidated tree `ready_for_review`.

### 2. Contract completeness and strictness

`panel_exp/contracts/geox_calibration_handoff_source.py` is not a strict certified source contract. The correction must replace the compressed permissive implementation with a typed, readable contract that explicitly models and validates the complete source envelope.

The record must explicitly contain, rather than hide only inside an unvalidated generic payload:

- schema and record versions;
- `handoff_source_id`, `evidence_artifact_id`, and `source_readout_id`;
- source readout version, artifact version, experiment ID, fixture ID, dataset version, and truth version;
- source repository, exact 40-character merged source-fixture SHA, task authorization/base pin, producer package version, embedded producer commit, and embedded provenance fields;
- exact certified paths and SHA-256 checksums for governed readout, source truth, and replay;
- KPI, KPI units, estimand, effect scale, channel, tactic, geography scope, and geo grain;
- effect estimate, absolute lift, relative lift, incremental outcome, uncertainty availability, standard error, confidence interval, and interval semantics, preserving nulls;
- deterministic UTC time-window and freshness timestamps and `synthetic_fixture_time_scope=true`;
- method family, source method status, instrument identity, design type, feasibility status, and closed method eligibility;
- readout status, handoff eligibility, warnings, blocked reasons, and failure reasons;
- explicit lineage and replay metadata;
- explicit authorization flags, all false.

The strict parser and validator must reject at least:

- missing or unknown schema/record versions;
- missing, duplicate, malformed, or non-deterministic identities;
- missing, short, placeholder, branch, or wrong source SHA;
- path traversal, paths outside `tests/fixtures/geox_governed_readouts/`, missing files, and checksum mismatch;
- source/readout identity mismatch;
- analytical or governance field mismatch against the referenced canonical governed readout;
- malformed, non-UTC, non-deterministic, or incorrectly ordered datetimes;
- unknown terminal states or method eligibility values;
- contradictory eligibility evidence;
- any true authorization flag;
- any MMM compatibility, `CalibrationSignal`, target-model, calibration-weight, TrustReport, DecisionSurface, recommendation, optimization, assignment, LLM-decision, or equivalent prohibited field.

`from_dict` must not be a blind `cls(**data)` acceptance path. Unknown keys, missing keys, wrong types, unsupported versions, and nested-shape errors must fail with typed deterministic contract failures.

### 3. Canonical source validation and preservation

The builder must deserialize and validate every governed-readout input through `panel_exp/contracts/geox_governed_experiment_readout.py` before constructing a source record.

For all 12 cases, the builder and tests must compare the envelope against the actual governed-readout payload and preserve every required analytical and governance value exactly, including nulls. A generic copied payload does not substitute for explicit validated source fields.

The existing `tests/fixtures/geox_governed_readouts/**` tree must remain byte-identical and unmodified.

### 4. Generator path defect

The rejected generator defines `d = FIX / fixture_id` but then computes checksums using `d / case["governed_readout"]`, `d / case["source_truth"]`, and `d / case["replay"]`. The source manifest paths already include the fixture directory, so this duplicates the case path and cannot regenerate from a clean synchronized tree.

Resolve every source path exactly once from the certified fixture root. Validate the resolved path remains inside the certified root, exists, and matches the path stored in the output record. The corrected generator must run successfully from the repository root on a clean tree.

### 5. Method eligibility derivation

The rejected generator derives eligibility from method-status substrings and readout status only. That violates the frozen precedence and ignores the certified source truth.

Derive `method_eligibility_status` deterministically from actual `source_truth.json` and governed-readout fields, especially:

- `fixture_class`;
- `certification_status`;
- `mip_handoff_expectation.status`;
- readout status;
- feasibility status;
- handoff eligibility;
- blocked and failure reasons;
- source method status.

Required precedence:

1. explicitly unsupported inference -> `unsupported`;
2. failed, blocked, infeasible, or handoff-blocked evidence -> `blocked`;
3. research-only evidence -> `research_only`;
4. diagnostic-only evidence -> `diagnostic_only`;
5. only otherwise eligible candidate evidence -> `candidate`.

The unsupported-inference fixture has `method_status="SCM"`; substring inspection of method status therefore cannot identify it. The mapping must use the certified source-truth classification and must be exhaustively asserted for all 12 fixture IDs. Unknown or contradictory combinations must fail closed.

### 6. Temporal and freshness validation

Do not validate timestamps with lexical string comparison. Parse strict timezone-aware UTC datetimes and reject malformed strings, offsets not normalized to UTC when the contract requires `Z`, naive values, and invalid ordering.

Committed timestamp values may be shared where justified, but tests must prove fresh and stale records remain consistent with the source status and that generation uses no current clock or nondeterministic value.

### 7. Public package surface

Export the contract through the existing package surface consistently. Do not append an absolute import after `__all__` while omitting the symbol from `__all__`. Use the repository’s normal relative-import style and export all intended public contract/parser/serializer/validator symbols deliberately.

### 8. Acceptance tests

The rejected test file has four broad tests and does not establish the named acceptance evidence. Replace it with focused behavioral coverage that separately proves all original acceptance items.

At minimum, tests must prove:

1. strict parsing, serialization, round-trip behavior, and supported-version enforcement;
2. missing, unknown, wrong-type, and extra fields fail closed;
3. exactly 12 records and exact one-to-one fixture coverage;
4. exact identity formulas, `source_readout_id` equality, uniqueness, and deterministic replay;
5. exact certified source paths, containment, 40-character source pin, file existence, and checksums;
6. path traversal, missing file, and checksum mismatch failures;
7. exact analytical and governance field preservation for all 12 cases, including null uncertainty/effect fields;
8. strict UTC parsing, temporal ordering, deterministic freshness timestamps, and stale/fresh consistency;
9. exhaustive expected method eligibility for all 12 fixture IDs;
10. unknown and contradictory eligibility combinations fail closed;
11. candidate, warning, stale, blocked, failed/conflicting, infeasible, multicell blocked, safe blocked, diagnostic-only, research-only, unsupported, and weak-matchability coverage;
12. all authorization flags remain false;
13. prohibited MMM, MIP decision, planning, recommendation, assignment, optimization, and LLM fields are absent and rejected if introduced;
14. two fresh generator runs are byte-identical and equal the committed manifest byte for byte;
15. the existing governed-readout fixture tree is byte-identical before and after both runs;
16. the canonical governed-readout parser validates every source readout;
17. no MMM compatibility is emitted or calculated.

Tests must compare actual parsed fixtures, not documentation text or only field presence.

### 9. Documentation and report quality

Replace the seven-line Track-D note and one-line summary with the task-required evidence:

- exact source checkpoint and task pins;
- contract and fixture paths;
- all 12 supported cases and eligibility classifications;
- identity rules, temporal semantics, freshness semantics, checksums, lineage, and replay behavior;
- explicit producer/consumer boundary;
- no-compatibility and no-authority statements;
- validation and deterministic-replay evidence;
- limitations, validation debt, sibling impact, and consumer verification required.

The final completion report must contain one implementation SHA only and no placeholders or stale SHAs.

## Owned paths

Correction may modify only the original ten owned paths:

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

Do not modify `tests/fixtures/geox_governed_readouts/**`, MIP, or MMM.

## Required validation

Run the complete original Tier-3 gate on the final frozen correction tree:

- parse every changed JSON file;
- compile every changed Python file;
- `git diff --check`;
- exact owned-path verification against `ef6a57382831210c085b4c1351358c3a0743be5e`;
- focused pytest with exact counts;
- adjacent governed-readout fixture and contract tests with exact counts;
- configured Ruff for every changed Python file;
- configured mypy for changed implementation files;
- two fresh deterministic generations with byte-identical output equal to the committed manifest;
- proof that the existing governed-readout fixture tree is unchanged;
- Docker-backed `make validate-docker` with exact counts and warnings;
- clean worktree except permitted `.codex/` and `docs/tasks/` local-only content;
- exact-tree receipt commit;
- push, fetch, and exact local/remote feature-head equality.

Focused success cannot hide full-suite debt. If Docker-backed validation genuinely cannot complete because of an external environment obstruction, publish `blocked` with the exact command, complete diagnostics, attempted remediation, and live resolution condition. Do not publish `ready_for_review` without the complete gate.

## Publication contract

On success, publish a new exact remote `ready_for_review` head containing:

- one corrected implementation SHA;
- one exact-tree publication receipt;
- exact source fixture pin, paths, checksums, identities, all 12 cases, and eligibility classifications;
- exact changed paths;
- exact validation counts and results;
- GitHub-observed versus locally reported evidence;
- blockers, limitations, validation debt, sibling impact, and consumer verification;
- task execution true, correction execution false, merge and PR authority false;
- unchanged capability authority;
- exact local/remote branch equality.

Do not create a PR or merge. Do not squash, rebase, force-push, or create a merge commit.

## Cross-repository boundary

GeoX completion advances but does not resolve `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`. MMM must separately publish linked compatibility evidence, and MIP must separately verify both merged producer pins and transition the blocker. GeoX does not authorize those actions.

## Terminal condition

Progress updates are non-terminal. Stop only when the exact remote feature branch durably records:

1. a fully validated new `ready_for_review` head; or
2. a genuine external `blocked` state with exact diagnostics and a live resolution condition.

A second failed exact-head review after this correction supersedes the task without merge.
