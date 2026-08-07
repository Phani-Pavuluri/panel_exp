# Active Task

**Status:** authorized
**Task ID:** `GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_001`
**Repository:** `Phani-Pavuluri/panel_exp`
**Base SHA:** `8fdecae61d31af5aec83b1df1c30295471f2953f`
**Task-authoring branch:** `docs/geox-d5-power-control-geometry-repair-001`
**Implementation branch:** `fix/geox-d5-power-control-geometry-repair-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 2 D5 validation-harness geometry repair
**Task execution authorized:** `true`
**Capability authority changed:** `false`
**Merge authorized:** `false`
**PR creation authorized:** `false`

## Objective

Repair the shared D5 power-characterization assignment-geometry defect in the
four Track-D harnesses. Each assignment helper must use
`list(assigned_panel.treated_units)` from `Design.assign`, preserve existing
matching, seeds, windows, methods and effect grids, and explicitly enforce at
least one treated unit and `cfg.min_control_units` controls (currently two).
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
