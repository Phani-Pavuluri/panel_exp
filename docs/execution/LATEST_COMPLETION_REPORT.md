# GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001 — Changes Requested

- **Repository:** `Phani-Pavuluri/panel_exp`
- **Feature branch:** `fix/geox-main-test-isolation-and-checkpoint-context-recovery-001`
- **Rejected remote head:** `b72ce8e1ad5141a341af8de3609a1fafdeef4908`
- **Implementation commit:** `b0b2a46f83b6c184e67f2ad34c5f17a0bcdcb4cf`
- **Current decision:** `changes_requested`
- **Correction cycle:** `1 of 1 authorized`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Capability authority changed:** `false`

## Review finding

The implementation is accepted in direction. It removes synthetic package-module injection, adds isolated installed-package validation evidence, strengthens clean-subprocess deterministic builder replay, and records a non-certifying checkpoint without modifying package/runtime code, the builder, manifests, source fixtures, MIP, or MMM.

Focused evidence at the rejected head passed:

- validator tests: `60 passed`;
- builder tests: `8 passed`;
- adjacent governed-readout tests: `3 passed`.

The branch is not ready for review because Ruff reports 37 task-owned `E702 multiple-statements-on-one-line` violations in `tests/contracts/test_geox_calibration_source_manifest.py`. The full Docker gate was not run because the required Ruff gate had not passed.

This is a task-owned formatting defect, not an external blocker. The active task requires owned test defects to be corrected, and one correction cycle remains.

## Required correction

Modify the owned validator test only as needed to split every semicolon-concatenated statement into ordinary statements on separate lines.

Preserve all tests, parameters, assertions, reason codes, fixture mutations, subprocess evidence, and source comparisons. Do not delete or weaken coverage. Do not add `noqa`, lint ignores, Ruff configuration changes, dependency changes, or prohibited-path changes.

Preserve the implementation at `b0b2a46f83b6c184e67f2ad34c5f17a0bcdcb4cf`, including:

- normal installed-package imports;
- no synthetic `ModuleType`, manual `__path__`, or `sys.modules` injection;
- isolated `python -I` validator probe with sanitized environment;
- two clean builder subprocess runs;
- byte equality with the committed manifest;
- governed-readout source-tree immutability;
- `producer_certified: false`;
- `mmm_compatibility_emitted: false`;
- `calibration_signal_emitted: false`;
- unauthorized successor and unchanged authority.

## Required validation

Run the complete active-task gate on one frozen task-owned tree:

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

Also verify exact changed paths, deterministic replay, source-tree immutability, clean worktree, push/fetch success, and exact local/remote feature-head equality. Mypy remains `not_required`.

Publish `ready_for_review` only when every required gate passes on the exact frozen tree and an exact-tree receipt commit is pushed. Otherwise publish a Git-durable `blocked` state with exact diagnostics and a live resolution condition.

## Authority and limitations

No producer certification, MMM compatibility, `CalibrationSignal`, simulation, optimization, planning, recommendation, real-data, runtime, pilot, production, sibling, merge, PR, or capability authority is granted. The successor `GEOX_CALIBRATION_SOURCE_MANIFEST_CERTIFICATION_RECOVERY_001` remains unauthorized.
## Blocked validation disposition

The corrected implementation is committed at
`a625a9d`. `make validate-docker` was run with complete output captured at
`/private/tmp/geox-checkpoint-full.log`, but the process terminated at roughly
49% without emitting a final pytest summary, exit code, failure node IDs, or
tracebacks. This is not terminal validation evidence. No ready-for-review claim
is made. The live resolution condition is a persistent Docker gate that reaches
a final exit code, followed by exact branch-versus-clean-main replay of every
failure. No authority or prohibited path changed.
## Validation retry

The detached focused gate passed: `71 passed` and Ruff passed. The repository
`make validate-docker` command was then executed in the detached container and
terminated with exit code `2`:

`Docker is required for make validate-docker but is not available.`

Receipts are preserved at `/private/tmp/geox-gate-focused.log`,
`/private/tmp/geox-gate-ruff.log`, `/private/tmp/geox-gate-full.log`, and
`/private/tmp/geox-gate-full.exit`. This is an external Docker-in-Docker
obstruction; the live resolution condition is running the same gate on a host
with Docker API access. The task remains blocked and no authority changed.
