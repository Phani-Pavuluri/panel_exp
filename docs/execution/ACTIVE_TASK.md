# Active Task

**Status:** authorized — reauthorized correction
**Task ID:** `GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_001`
**Repository:** `Phani-Pavuluri/panel_exp`
**Base SHA:** `7bee4f7f24ff909b6b60cc067ca2da8cab1077c1`
**Task-authoring branch:** `docs/geox-d5-power-control-geometry-repair-001-reauthorization`
**Implementation branch:** `fix/geox-d5-power-control-geometry-repair-001-reauthorized`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 2 D5 validation-harness geometry repair
**Task execution authorized:** `true`
**Capability authority changed:** `false`
**Merge authorized:** `false`
**PR creation authorized:** `false`

## Objective

Repair the shared D5 power-characterization assignment-geometry defect in the
four Track-D harnesses. Each assignment helper must use
the dictionary returned by `greedy_match_markets(...).assign`: with
`n_test_grps=1`, consume `list(assignment["test_0"])` as treated and
`list(assignment["control"])` as controls. Never flatten all dictionary
values. Preserve existing matching, seeds, windows, methods and effect grids,
and explicitly enforce at least one treated unit and `cfg.min_control_units`
controls (currently two).
Invalid geometry must fail clearly; production assignment, SCM and
UnitJackKnife are out of scope.

## Owned paths

- `panel_exp/validation/track_d_d5_pow_001a.py`
- `panel_exp/validation/track_d_d5_pow_001b.py`
- `panel_exp/validation/track_d_d5_pow_001c.py`
- `panel_exp/validation/track_d_d5_pow_001d.py`
- the four corresponding `tests/track_d/test_d5_pow_*.py` files;
- required execution lifecycle files.

No D5 artifacts are regenerated. No production, analytical, calibration,
producer-certification, MMM, MIP, planning, recommendation, runtime or
capability authority changes are authorized.

## Required validation

JSON parsing; the four focused D5 test files; Ruff on the eight owned harness
and test files; `git diff --check`; and a focused regression proving the
one-replicate paths do not raise the UnitJackKnife donor error. The full Docker
suite is deferred until all baseline families are repaired.

## Dependencies and remaining baseline families

The isolation milestone remains parked and blocked by synchronized-main
validation debt at branch
`fix/geox-main-test-isolation-and-checkpoint-context-recovery-001`, head
`0c16766f47cae903c9a085043dfa51949e61ea68`, implementation
`a625a9dac6b97b05c4044dc5af5ae7875a63e889`; merge authorization is false.
After this family, TBR recovery, production/validation import isolation,
BlockResidualBootstrap golden reconciliation, and D5 artifact reconciliation
remain. The prior pin-schema closure's correction-cycle counter mismatch is
historical lifecycle debt for a future single-source pilot and is not repaired
by this task.

No successor task is authorized. No PR or merge is authorized.

## Reauthorization evidence

The prior feature head `0b94e9d924a565ff03df805258c6d188418f7f8b` is rejected
for authorization-order ancestry only. Its historical implementation
`b0cf0d44d19769aa4c9b4c8f4bdf06e23ebb7df5` demonstrated correct code behavior
and passed focused validation, but neither commit may be merged, cherry-picked,
rebased, or reused as executable ancestry. The corrected implementation must
be recreated manually from synchronized main after this reauthorization.

Correction cycle 1 is authorized before implementation; no D5 code or tests
are changed in this authoring phase.
