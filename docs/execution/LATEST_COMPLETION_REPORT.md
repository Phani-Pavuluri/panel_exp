# GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_001 — Authorized Task Handoff

- **Base main:** `7bee4f7f24ff909b6b60cc067ca2da8cab1077c1`
- **Task-authoring branch:** `docs/geox-d5-power-control-geometry-repair-001-reauthorization`
- **Implementation branch:** `fix/geox-d5-power-control-geometry-repair-001-reauthorized`
- **Authoring branch:** `docs/geox-d5-power-control-geometry-repair-001-reauthorization`
- **Status:** ready_for_review
- **Execution authorized:** `true`
- **Merge/PR authorized:** `false`

This reauthorization repairs only the four D5 validation harnesses to consume
the production assignment dictionary (`assignment["test_0"]` and
`assignment["control"]`) and enforce treated/control geometry. Production
assignment, SCM, UnitJackKnife, analytical/runtime behavior, artifacts,
calibration, MIP, MMM and capability authority are unchanged. D5 artifacts are
not regenerated.

Required validation is JSON parse, the four focused D5 test files, Ruff on the
owned harnesses/tests, diff-check, and the one-replicate donor-error regression.
The complete Docker gate is deferred until the remaining baseline families are
repaired.

The isolation milestone remains parked and blocked at
`fix/geox-main-test-isolation-and-checkpoint-context-recovery-001@0c16766f47cae903c9a085043dfa51949e61ea68`, implementation
`a625a9dac6b97b05c4044dc5af5ae7875a63e889`; no merge authorization is granted.
Remaining baseline families are TBR recovery, production/validation import
boundary, BlockResidualBootstrap golden reconciliation, and D5 artifact
reconciliation. The prior closure correction-cycle mismatch is recorded as
historical lifecycle-governance debt for a future single-source pilot.

No PR, merge, analytical/production change, sibling change, or capability
authority change is authorized.

The rejected feature head `0b94e9d924a565ff03df805258c6d188418f7f8b` is
rejected for authorization-order ancestry only. Historical implementation
`b0cf0d44d19769aa4c9b4c8f4bdf06e23ebb7df5` demonstrated correct behavior and
passed focused validation, but neither it nor the late authorization commit
`a549395d2d0186cfa7744283d562e4928b0405be` may be merged, cherry-picked,
rebased, or reused as executable ancestry. The corrected implementation will
be recreated manually from synchronized main after this metadata
reauthorization reaches review.

Fresh implementation commit `dc2431237e8117409386a02e3d3d37b0155e7af8` was
recreated manually from authorized main. The helpers consume
`assignment["test_0"]` and `assignment["control"]` and do not flatten the
assignment dictionary. Focused Docker validation passed: `20 passed, 1
warning`; changed-path Ruff reported `All checks passed!`. Compileall, JSON
parse, and diff-check passed. The donor-error regression did not occur.
No D5 artifacts were regenerated. The full Docker suite was not run and is
not required for this repair. Correction cycle state is `1 used / 0 remaining`.
The parked isolation branch remains unauthorized and the TBR successor remains
unauthorized.
