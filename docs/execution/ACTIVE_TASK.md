# Active Task

**Status:** authorized
**Task ID:** `GEOX_TBR_RECOVERY_CONTRACT_ALIGNMENT_001`
**Repository:** `Phani-Pavuluri/panel_exp`
**Base SHA:** `28bba2438ddee140061776ebc38a8c64df6ef028`
**Implementation branch:** `fix/geox-tbr-recovery-contract-alignment-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 2 — TBR recovery contract alignment
**Task execution authorized:** `true`
**Correction execution authorized:** `false`
**Merge authorized:** `false`
**PR creation authorized:** `false`
**Unresolved execution-blocking design questions:** none

## Objective

Align the TBR recovery contract exposed by the synchronized-main baseline. The
bounded failures are:

- `tests/test_estimator_recovery_smoke.py::test_smoke_positive_effect_direction[TBR]`
- `tests/test_recovery_runner.py::test_same_seed_identical_metrics[TBR]`

Repair only the TBR recovery harness/contract mismatch. Preserve production
TBR, TBRRidge, SCM, UnitJackKnife, inference, assignment, analytical semantics,
artifacts, calibration, MIP, MMM, and all product/capability authority.

## Required behavior

Determine the actual contract mismatch from the TBR recovery implementation and
tests. Preserve deterministic same-seed metrics and the established positive
effect-direction assertion. Do not weaken assertions, alter analytical truth,
or mask failures with retries or fixture changes.

## Owned scope

Only the directly offending TBR recovery harness/tests and the three stable
execution lifecycle files may change. D5 artifacts, production assignment,
inference, SCM, UnitJackKnife, calibration-source behavior, MIP, MMM,
dependencies, Docker/CI, and capability authority are prohibited.

## Validation policy

Run JSON parsing, both focused TBR nodes, an ordered/reversed recovery
regression proving order independence, Ruff and compile validation on changed
files, `git diff --check`, and exact changed-path verification. The full Docker
gate is intentionally not required under the revised focused-validation policy.
Do not repair D5 artifacts, handoff-schema governance, or other baseline
families here.

## Sequencing

The next local baseline task is
`GEOX_D5_COMMITTED_ARTIFACT_RECONCILIATION_001`, unauthorized. The parked
isolation milestone and lifecycle adoption remain separately governed and
unauthorized. Stop at `ready_for_review`; do not create a PR or merge.
