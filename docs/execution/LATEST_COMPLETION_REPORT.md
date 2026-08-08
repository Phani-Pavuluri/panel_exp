# GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_001 — Authorized Task Handoff

- **Base main:** `8fdecae61d31af5aec83b1df1c30295471f2953f`
- **Task-authoring branch:** `docs/geox-d5-power-control-geometry-repair-001`
- **Implementation branch:** `fix/geox-d5-power-control-geometry-repair-001`
- **Status:** ready_for_review after correction
- **Execution authorized:** `true`
- **Merge/PR authorized:** `false`

This task repairs only the four D5 validation harnesses to consume the
production assignment dictionary (`assignment["test_0"]` and
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

Initial implementation `c57a64827b42cc64a74c9fffab29a4e6b4897b32` remains
historical. Metadata authorization commit `a549395` authorized the correction.
Correction implementation `b0cf0d44d19769aa4c9b4c8f4bdf06e23ebb7df5` changed
the four helpers and their focused regression tests. In the supported
devcontainer, Poetry 1.8.5 installed successfully; focused pytest passed
`20 passed, 1 warning`, and changed-path Ruff reported `All checks passed!`.
The warning is the existing NumPy divide warning; no donor-error exception
occurred. JSON parsing, compileall, and diff-check passed. No artifacts were
regenerated, and production assignment paths remain unchanged.

The exact focused command used was the prescribed Docker build image followed
by `poetry install --with dev --no-interaction`, the four D5 pytest modules,
and Ruff over the eight harness/test paths. No full Docker suite was run or
required for this continuation. Correction cycle `1 used / 0 remaining`.
