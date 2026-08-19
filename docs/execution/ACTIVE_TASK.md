# Active Task

**Status:** authorized
**Task ID:** `GEOX_SYNTHETIC_CONTROL_PLACEBO_STRICT_COMPATIBILITY_REPAIR_001`
**Repository:** `Phani-Pavuluri/panel_exp`
**Base SHA:** `ea886d7b73cc988b8440861ddcf9bc0c4fc4d246`
**Implementation branch:** `fix/geox-synthetic-control-placebo-strict-compatibility-repair-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 2 — validation/inference compatibility boundary
**Task execution authorized:** `true`
**Correction execution authorized:** `false`
**Merge authorized:** `false`
**PR creation authorized:** `false`
**Unresolved execution-blocking design questions:** none

## Objective

Repair the bounded D5 smoke-callable compatibility defect in which the
validation builder invokes the `SyntheticControlCVXPY` placebo path with the
inference-only `placebo_strict` keyword, which is not accepted by the placebo
model-construction path. Preserve the explicit `fail_requires_fix` evidence
until the compatibility behavior is correctly repaired and revalidated.

Preserve public estimator APIs, analytical semantics, placebo strictness
meaning, artifact schemas, guardrail wording, and all capability, producer,
product, and runtime authority. Do not mask the defect by deleting the smoke
case or weakening its verdict assertions.

## Owned scope

Only the directly offending validation smoke builder, its focused test module,
the narrowly required inference compatibility helper if repository evidence
proves it is the correct boundary, the affected D5 smoke artifact, and the
three stable execution lifecycle files may change. Do not modify assignment,
SCM analytical behavior, TBR, UnitJackKnife, unrelated D5 artifacts, MIP,
MMM, dependencies, Docker/CI, or capability state.

## Validation policy

Use the locked environment. Run the complete D5 smoke-callable focused module,
an explicit regression for the placebo_strict path and unsupported-placebo
classification, changed-scope Ruff, compile validation, JSON parsing,
`git diff --check`, and exact changed/prohibited-path verification. The full
Docker gate is not required under the revised focused-validation policy.

## Sequencing

The task does not authorize lifecycle adoption, producer certification, or any
successor. The parked isolation milestone remains separately governed and
unauthorized. Stop at `ready_for_review`; do not create a PR or merge.
