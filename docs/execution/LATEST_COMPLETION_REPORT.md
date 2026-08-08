# GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_001 — Authorized Task Handoff

- **Base main:** `8fdecae61d31af5aec83b1df1c30295471f2953f`
- **Task-authoring branch:** `docs/geox-d5-power-control-geometry-repair-001`
- **Implementation branch:** `fix/geox-d5-power-control-geometry-repair-001`
- **Status:** blocked after implementation
- **Execution authorized:** `true`
- **Merge/PR authorized:** `false`

This task repairs only the four D5 validation harnesses to consume
`assigned_panel.treated_units` and enforce treated/control geometry. Production
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

Implementation commit `c57a64827b42cc64a74c9fffab29a4e6b4897b32` changed only the eight authorized harness/test
paths. Focused pytest and Ruff could not complete: host Poetry reported no
Python, and Docker Poetry dependency installation did not reach test execution.
The task remains blocked pending a usable validation environment; no readiness
or baseline-repair claim is made.
