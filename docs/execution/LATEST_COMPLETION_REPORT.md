# GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_002 — Merged and Closed

- **Base main:** `687e4063ca9d43bcc0ea4527cac3fc9dab3fa8fd`
- **Task-authoring branch:** `docs/geox-d5-power-control-geometry-repair-002`
- **Implementation branch:** `fix/geox-d5-power-control-geometry-repair-002`
- **Authoring branch:** `docs/geox-d5-power-control-geometry-repair-002`
- **Status:** merged
- **Execution authorized:** `false`
- **Merge/PR authorized:** `false`
- **Authorization-bearing contract SHA:** `5503ef3b8214a0f2bdb1f444c9b673ddce1ed587`

This task repairs only the four D5 validation harnesses to consume
the production assignment dictionary (`assignment["test_0"]` and
`assignment["control"]`) and enforce the supplied configurable
`min_control_units` geometry. Production
assignment, SCM, UnitJackKnife, analytical/runtime behavior, artifacts,
calibration, MIP, MMM and capability authority are unchanged. D5 artifacts are
not regenerated.

Each helper must accept `min_control_units: int`; each caller must pass
`min_control_units=cfg.min_control_units`; and geometry errors must report the
actual supplied minimum. A focused non-default `min_control_units=3`
regression is required and must fail if the helper falls back to literal two.

This is a new superseding task, not a reauthorized correction. Its correction
budget is 0 used / 1 remaining, with correction execution unauthorized.

Predecessor 001 was superseded; rejected review head
`e53c9fcd9396762d1d3631bdc8b1d968590ab261` and implementation
`dc2431237e8117409386a02e3d3d37b0155e7af8` are historical evidence only.

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

Implementation commit `5a7b9ff9faecb50a28bab63688c9a53594fa733f` changed only
the eight authorized harness/test paths. Focused pytest collection failed with
Locked Poetry pytest passed `17 passed, 1 warning`; Ruff reported `All checks
passed`; compileall passed; JSON parsing and host `git diff --check` passed.
The container scope command was not applicable because `.git` is excluded from
the mounted source copy; host scope verification was exact. Approved head
`9d17ad44f3a8cb860dfed36af860487c0877d12b` was fast-forwarded to main and the
implementation branch was deleted locally and remotely. Implementation commit:
`5a7b9ff9faecb50a28bab63688c9a53594fa733f`. The full Docker gate is not
required for this family.

The implementation was created from authorized main ancestry; no predecessor
implementation was reused. Parked isolation and the TBR successor remain
unauthorized. No PR was created and no merge commit was created.
