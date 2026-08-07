# GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001 — Blocked

- **Repository:** `Phani-Pavuluri/panel_exp`
- **Feature branch:** `fix/geox-main-test-isolation-and-checkpoint-context-recovery-001`
- **Task:** `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001`
- **Status:** `blocked`
- **Original implementation commit:** `b0b2a46f83b6c184e67f2ad34c5f17a0bcdcb4cf`
- **Correction implementation commit:** `a625a9dac6b97b05c4044dc5af5ae7875a63e889`
- **Correction cycle:** `1 of 1 completed`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Capability authority changed:** `false`

## Behavior implemented

The task-owned tests now:

- import the validator through the normally installed `panel_exp` package;
- contain no synthetic `ModuleType`, manual package `__path__`, or `sys.modules` injection;
- exercise an isolated `python -I` validator probe with sanitized environment variables;
- run the manifest builder twice in clean subprocesses outside the repository;
- prove deterministic byte equality with the committed manifest;
- prove governed-readout source-tree immutability.

The correction commit mechanically reformatted the two owned tests so Ruff passes without changing test meaning or coverage.

This checkpoint remains non-certifying. `producer_certified: false`, `mmm_compatibility_emitted: false`, and `calibration_signal_emitted: false`.

## Validation results

- Focused validator, builder, and adjacent governed-readout tests: `71 passed`.
- Ruff on both owned test files: passed.
- Repository-authored full gate: `make validate-docker` completed with
  `23 failed, 6151 passed, 28 skipped` in `3870.44s`.
- Exact clean synchronized-main replay: `22 failed, 1 passed`.
- The sole feature-specific failure was
  `tests/test_repo_native_execution_handoff.py::test_status_invariants_are_closure_safe`;
  the blocked-state invariant requiring `reviewed_head_sha == null` was
  repaired, preserving the historical SHA in `rejected_review_head_sha`.
- The remaining 22 failures reproduce on synchronized `main`; no analytical or
  runtime regression from this milestone has been established.

Terminal validation evidence was preserved locally at:

- `/private/tmp/geox-final-docker.log`
- `/private/tmp/geox-final-docker.exit`
- `/private/tmp/geox-main-failure-replay.log`
- `/private/tmp/geox-main-failure-replay.exit`

The full Docker-backed suite did not pass. No full-suite certification,
producer certification, or downstream eligibility is claimed.

## Blocker and resolution condition

Blocker: `DOCKER_GATE_MAIN_BASELINE_VALIDATION_DEBT`.

Live resolution condition: repair synchronized-main baseline debt, rerun the
complete Git-authored gate on the frozen corrected tree, and publish either:

1. an exact-tree `ready_for_review` receipt when every required gate passes; or
2. a new Git-durable `blocked` result with exact final failures and clean-main comparison evidence.

## Scope and authority

No package/runtime code, validator, builder, manifest, source fixture, sibling repository, analytical truth, producer certification, MMM compatibility, `CalibrationSignal`, simulation, optimization, planning, recommendation, real-data, runtime, pilot, or production authority changed.

No PR, merge, squash, rebase, force-push, or merge commit was created.

The successor `GEOX_CALIBRATION_SOURCE_MANIFEST_CERTIFICATION_RECOVERY_001` remains unauthorized.
