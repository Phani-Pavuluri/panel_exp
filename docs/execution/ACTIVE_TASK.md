# Active Task

**Status:** blocked  
**Task ID:** `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001`  
**Repository:** `Phani-Pavuluri/panel_exp`  
**Local path:** `/Users/phani/Desktop/panel_exp`  
**Feature branch:** `fix/geox-main-test-isolation-and-checkpoint-context-recovery-001`  
**Execution mode:** `branch_and_fast_forward`  
**Risk tier:** Tier 2 test-isolation checkpoint with mandatory full Docker validation  
**Capability authority changed:** `false`  
**Correction cycle:** 1 of 1 authorized  
**Unresolved execution-blocking design questions:** none

## Objective

Complete the existing test-isolation checkpoint by correcting the task-owned Ruff formatting failures, rerunning the complete declared gate on one frozen tree, and publishing an exact-tree `ready_for_review` receipt.

The implementation at `b0b2a46f83b6c184e67f2ad34c5f17a0bcdcb4cf` is acceptable in direction and must be preserved:

- synthetic `ModuleType`, manual package `__path__`, and `sys.modules` injection are removed from the validator test;
- normal installed-package validation coverage remains;
- the isolated `python -I` package probe remains;
- clean-subprocess builder replay remains deterministic and source-tree immutable;
- the checkpoint remains non-certifying and non-authorizing.

This milestone must not change the validator, builder, manifest, governed-readout fixtures, package/runtime behavior, analytical truth, producer certification, MMM compatibility, MIP consumer mapping, `CalibrationSignal`, or downstream authority.

## Prerequisite and review evidence

- GeoX synchronized authoring main: `b3f6b9acf81ff268c21d96d1014f8780fba5644f`.
- MIP main dependency: `a293ce52a813709ca624332123019139928cc51e`.
- MMM main observation: `fe8e784923994406a2e4907d28debd872d61fd73`.
- Rejected blocked remote head: `b72ce8e1ad5141a341af8de3609a1fafdeef4908`.
- Existing implementation commit: `b0b2a46f83b6c184e67f2ad34c5f17a0bcdcb4cf`.
- Focused validation already passed at the blocked tree:
  - validator: `60 passed`;
  - builder: `8 passed`;
  - adjacent governed-readout tests: `3 passed`.
- Ruff reported 37 `E702 multiple-statements-on-one-line` violations in `tests/contracts/test_geox_calibration_source_manifest.py`.
- Full Docker validation did not run because the declared Ruff gate had not passed.

The Ruff failures are task-owned formatting defects, not an external blocker. The original task requires owned test defects to be corrected, and one correction cycle remains.

## Owned paths

The complete task may modify only:

1. `tests/contracts/test_geox_calibration_source_manifest.py`
2. `tests/fixtures/test_geox_calibration_source_manifest_generator.py`
3. `docs/track_d/GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001.md`
4. `docs/execution/ACTIVE_TASK.md`
5. `docs/execution/EXECUTION_STATE.json`
6. `docs/execution/LATEST_COMPLETION_REPORT.md`

The correction implementation itself should modify only the validator test plus the stable execution/checkpoint evidence required for final publication. Preserve the existing builder-test implementation unless a directly observed task-owned gate failure requires a minimal correction.

The branch may retain the task-authoring update to `docs/execution/REPOSITORY_CONTEXT_INDEX.md`; implementation and correction must not modify that file.

## Prohibited paths and operations

Do not modify:

- `panel_exp/**`;
- `scripts/build_geox_calibration_source_manifest.py`;
- `tests/fixtures/geox_calibration_handoff_sources/**`;
- `tests/fixtures/geox_governed_readouts/**`;
- other tests or fixtures;
- `pyproject.toml`, `poetry.lock`, dependencies;
- Docker, CI, Makefile, Git hooks, execution standards, or repository governance;
- MIP or MMM;
- rejected or divergent feature branches.

Do not create a PR, merge, squash, rebase, force-push, cherry-pick, or merge commit. Do not weaken Ruff, add ignores, add `noqa`, alter Ruff configuration, skip validation, or delete historical branches.

## Correction cycle 1 of 1

Correct all 37 `E702` findings in `tests/contracts/test_geox_calibration_source_manifest.py` by splitting semicolon-concatenated statements into ordinary Python statements on separate lines.

Required behavior:

- preserve every existing test, parameter set, assertion, reason code, fixture mutation, and failure expectation;
- do not delete or weaken coverage;
- do not convert executable evidence into documentation-string checks;
- do not add lint suppressions or configuration exceptions;
- keep the synthetic-package-injection removal intact;
- keep the isolated installed-package probe intact;
- keep all imports through the normally installed package;
- review the complete test diff after any automated Ruff fix and retain only formatting-equivalent changes;
- make no production, package, contract, builder, manifest, fixture, or analytical change.

The correction is formatting-only. If a Ruff finding cannot be corrected without changing test meaning or a prohibited path, publish a Git-durable `blocked` state with the exact finding and required separate authorization.

## Acceptance evidence

The final frozen tree must prove:

1. Ruff reports no findings on either owned test file.
2. The validator test still has 60 tests or a clearly explained higher count caused only by added acceptance coverage; no existing test is removed.
3. The builder test still passes all existing coverage.
4. Adjacent governed-readout tests still pass.
5. No `ModuleType`, `sys.modules`, or manual package `__path__` injection remains.
6. Normal in-process package import succeeds.
7. The isolated `python -I` validator probe succeeds with sanitized `PYTHONPATH` and `PYTHONHOME`.
8. Two sanitized builder subprocess runs remain byte-identical to each other and the committed manifest.
9. The governed-readout source tree remains byte-identical.
10. No prohibited path or sibling repository changes.
11. The checkpoint states `producer_certified: false`, `mmm_compatibility_emitted: false`, and `calibration_signal_emitted: false`.
12. The successor `GEOX_CALIBRATION_SOURCE_MANIFEST_CERTIFICATION_RECOVERY_001` remains unauthorized.

## Required validation

Run on one frozen task-owned tree:

```bash
poetry install --with dev --no-interaction
python -m json.tool docs/execution/EXECUTION_STATE.json >/dev/null
python -m py_compile tests/contracts/test_geox_calibration_source_manifest.py tests/fixtures/test_geox_calibration_source_manifest_generator.py
git diff --check
rg -n "ModuleType|sys\.modules|__path__" tests/contracts/test_geox_calibration_source_manifest.py
env -u PYTHONPATH -u PYTHONHOME poetry run python -I -c "from panel_exp.contracts.geox_calibration_source_manifest import validate_geox_calibration_source_manifest; print('geox-validator-import-ok')"
poetry run pytest -q tests/contracts/test_geox_calibration_source_manifest.py
poetry run pytest -q tests/fixtures/test_geox_calibration_source_manifest_generator.py
poetry run pytest -q tests/contracts/test_geox_governed_experiment_readout.py tests/fixtures/test_geox_certified_governed_readout_fixtures.py
poetry run ruff check tests/contracts/test_geox_calibration_source_manifest.py tests/fixtures/test_geox_calibration_source_manifest_generator.py
make validate-docker
```

Also verify exact changed paths against the authorization ancestry, deterministic replay, source-tree immutability, clean task-owned worktree, push/fetch success, and exact local/remote feature-head equality.

Mypy is `not_required`; do not add it.

Record exact passed, failed, skipped, deselected, xfailed, xpassed, and warning counts for every pytest gate, plus JSON, compilation, diff, import, Ruff, replay, immutability, Docker, worktree, and remote-equality results.

## Publication contract

On success:

1. Create one correction implementation commit preserving the existing implementation lineage.
2. Update the three execution files and checkpoint to `ready_for_review` with the original implementation SHA, correction SHA, exact evidence, remaining certification gap, and unchanged authority.
3. Freeze the complete task-owned tree and rerun the entire required gate.
4. Create one exact-tree publication receipt commit identifying the task, implementation/correction lineage, validation commands and exact results, evidence source, worktree state, and authority impact.
5. Do not modify task-owned files after the receipt.
6. Push only `fix/geox-main-test-isolation-and-checkpoint-context-recovery-001`, fetch again, and prove local/remote exact-head equality.
7. Stop for external exact-head review.

If any required gate remains unavailable or fails without a task-owned correction, publish a Git-durable `blocked` state with exact diagnostics and a live resolution condition.

## Final blocked validation outcome

Focused validator, builder, and adjacent validation passed: `71 passed`.
Ruff passed. The completed full Docker branch gate was `23 failed, 6151
passed, 28 skipped` (runtime `3870.44s`). The exact clean synchronized-main
replay was `22 failed, 1 passed`.

The sole feature-specific failure was
`tests/test_repo_native_execution_handoff.py::test_status_invariants_are_closure_safe`:
a blocked state must have `reviewed_head_sha == null`; that lifecycle defect is
repaired while the historical rejected SHA remains in
`rejected_review_head_sha`. The remaining 22 failures reproduce on synchronized
`main`, so no analytical or runtime regression from this milestone has been
established.

The checkpoint remains blocked because the repository-required full Docker
baseline is not green. Blocker: `DOCKER_GATE_MAIN_BASELINE_VALIDATION_DEBT`.
Live resolution requires repairing synchronized-main baseline debt and rerunning
the complete declared gate on this frozen tree. The successor remains
unauthorized.

## Deferred successor and authority

`GEOX_CALIBRATION_SOURCE_MANIFEST_CERTIFICATION_RECOVERY_001` remains separate and unauthorized. This task does not authorize producer certification, MMM compatibility, MIP work, `CalibrationSignal`, simulation, optimization, planning, recommendation, real-data, runtime, pilot, or production behavior.
