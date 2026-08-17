# Active Task

**Status:** blocked
**Task ID:** `GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_002`
**Repository:** `Phani-Pavuluri/panel_exp`
**Base SHA:** `687e4063ca9d43bcc0ea4527cac3fc9dab3fa8fd`
**Task-authoring branch:** `docs/geox-d5-power-control-geometry-repair-002`
**Implementation branch:** `fix/geox-d5-power-control-geometry-repair-002`
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
and explicitly require each helper to accept `min_control_units: int`, enforce
`len(treated) >= 1` and `len(control) >= min_control_units`, and pass
`min_control_units=cfg.min_control_units` from every production caller. The
diagnostic `ValueError` must report the actual supplied minimum (for example,
`required_min_controls=3`) and must never hard-code two.
Invalid geometry must fail clearly; production assignment, SCM and
UnitJackKnife are out of scope.

At least one focused regression must invoke a helper with a non-default
`min_control_units=3` and prove the supplied value governs the validity check
or error. Existing assignment-contract equality, disjointness, four-module
functional coverage, and donor-error regressions remain required.

## Owned paths

- `panel_exp/validation/track_d_d5_pow_001a.py`
- `panel_exp/validation/track_d_d5_pow_001b.py`
- `panel_exp/validation/track_d_d5_pow_001c.py`
- `panel_exp/validation/track_d_d5_pow_001d.py`
- the four corresponding `tests/track_d/test_d5_pow_*.py` files;
- required execution lifecycle files.

Predecessor `GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_001` is superseded. Its
rejected review head is
`e53c9fcd9396762d1d3631bdc8b1d968590ab261` and implementation is
`dc2431237e8117409386a02e3d3d37b0155e7af8`; rejection reason was hard-coded
two-control geometry. Those commits are historical evidence only and must not
be merged, cherry-picked, rebased or used as executable ancestry.

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

Implementation commit `5a7b9ff9faecb50a28bab63688c9a53594fa733f` is present.
Locked Poetry pytest passed 17 tests with one warning. The final locked Ruff,
compile, and diff receipt could not complete because the dependency-install
container exited 129 before producing a Ruff receipt. No readiness claim is
made; resolution requires complete locked-environment Ruff and compile exit
receipts.

## Reauthorization evidence

The prior feature head `0b94e9d924a565ff03df805258c6d188418f7f8b` is rejected
for authorization-order ancestry only. Its historical implementation
`b0cf0d44d19769aa4c9b4c8f4bdf06e23ebb7df5` demonstrated correct code behavior
and passed focused validation, but neither commit may be merged, cherry-picked,
rebased, or reused as executable ancestry. The corrected implementation must
be recreated manually from synchronized main after this reauthorization.

This is a new superseding task. Its correction budget is 0 used / 1 remaining,
and correction execution is not currently authorized. No D5 code or tests are
changed in this authoring phase.
