# Active Task

**Status:** authorized
**Task ID:** `GEOX_D5_COMMITTED_ARTIFACT_RECONCILIATION_001`
**Repository:** `Phani-Pavuluri/panel_exp`
**Base SHA:** `eeabf9c6a04f08ec082429d31fcd1a34eb14b1c3`
**Implementation branch:** `fix/geox-d5-committed-artifact-reconciliation-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 2 — D5 committed-artifact reconciliation
**Task execution authorized:** `true`
**Correction execution authorized:** `false`
**Merge authorized:** `false`
**PR creation authorized:** `false`
**Unresolved execution-blocking design questions:** none

## Objective

Reconcile the five committed D5-STAT characterization artifacts with their
deterministic repository builders. The bounded failures are the
`test_committed_artifact_matches_build` checks in:

- `tests/track_d/test_d5_stat_augsynth_point_001.py`
- `tests/track_d/test_d5_stat_mcell_percell_001.py`
- `tests/track_d/test_d5_stat_smoke_callable_001.py`
- `tests/track_d/test_d5_stat_tbr_agg_001.py`
- `tests/track_d/test_d5_stat_tbrridge_inf_001.py`

Determine whether each mismatch is stale committed evidence, nondeterministic
generation, or a builder defect. Repair only the smallest evidence/builder
surface required to make the committed artifacts reproducible.

## Scope and prohibitions

Owned implementation paths are the five named D5-STAT test modules, their
directly corresponding validation builders, the five committed JSON artifacts,
and the three stable execution lifecycle files. Do not modify assignment,
SCM, TBR/TBRRidge, UnitJackKnife, inference semantics, calibration-source
behavior, product/runtime code, P2 capability meaning, MIP, MMM, Docker/CI,
dependencies, or unrelated D5 artifacts. Do not regenerate artifacts during
authoring; regeneration is permitted only on the frozen implementation tree
after the mismatch cause is established.

## Required behavior

Preserve artifact schemas, IDs, verdict semantics, guardrail wording, method
identity, and all analytical/product authority. Generated timestamps must remain
the only intentionally volatile field where the existing tests strip them.
Builders must be deterministic for their declared configuration and committed
artifacts must match the corresponding builder output exactly after the
existing timestamp normalization.

## Focused validation policy

Use the locked repository environment. Run JSON parsing, all five complete
focused D5-STAT test modules, explicit deterministic rebuild comparisons,
changed-file Ruff, compile validation, `git diff --check`, and exact
changed-path/prohibited-path verification. The full Docker gate is not required
for this individual baseline family under the revised focused-validation policy.
Do not repair TBR, import-boundary, lifecycle-adoption, or other baseline
families here.

## Sequencing

The next task remains separately governed and unauthorized. The parked
`GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001` milestone and
its branch remain historical blocked evidence; no producer certification,
analytical, capability, or downstream authority is granted by this task.

Stop at `ready_for_review`; do not create a PR or merge.
