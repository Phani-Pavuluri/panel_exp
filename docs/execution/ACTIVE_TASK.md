# Active Task

**Status:** blocked  
**Task ID:** `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001`  
**Repository:** `Phani-Pavuluri/panel_exp`  
**Local path:** `/Users/phani/Desktop/panel_exp`  
**Feature branch:** `fix/geox-main-test-isolation-and-checkpoint-context-recovery-001`  
**Execution mode:** `branch_and_fast_forward`  
**Risk tier:** Tier 2 test-isolation checkpoint with mandatory full Docker validation  
**Capability authority changed:** `false`  
**Unresolved execution-blocking design questions:** none

## Objective

Publish one independently reviewable GeoX test-isolation checkpoint proving
whether the existing calibration-source manifest validator and deterministic
builder work through the normally installed `panel_exp` package in clean
subprocesses.

This milestone may correct test isolation and record validation context. It must
not change the validator, builder, manifest, governed-readout fixtures,
analytical truth, producer certification, MMM compatibility, MIP consumer
mapping, `CalibrationSignal`, or any runtime or downstream authority.

A passing checkpoint establishes only:

1. normal installed-package import health for the existing validator;
2. contextual validation of the committed manifest through that import path;
3. deterministic clean-subprocess replay of the existing builder;
4. exact source-fixture immutability during replay;
5. the remaining evidence required before a separate producer-certification
   milestone may be authored.

It does **not** certify the combined GeoX producer.

## Prerequisite evidence

Re-fetch and verify before implementation:

- GeoX `main`: `b11646bab1f461964644a6526ef4967a8f04624d`.
- MIP `main`: `a293ce52a813709ca624332123019139928cc51e`.
- MMM `main`: `fe8e784923994406a2e4907d28debd872d61fd73`.
- MIP milestone `MIP_P2_CAPABILITY_CHECKPOINT_LEDGER_RECOVERY_001` is merged and
  records this task as the sole next-eligible, unauthorized GeoX milestone.
- Existing GeoX validator:
  `panel_exp/contracts/geox_calibration_source_manifest.py`.
- Existing GeoX builder:
  `scripts/build_geox_calibration_source_manifest.py`.
- Existing committed manifest:
  `tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json`.
- Existing source tree:
  `tests/fixtures/geox_governed_readouts/`.
- Existing validator tests currently synthesize `panel_exp` and
  `panel_exp.contracts` modules through `types.ModuleType`, manual `__path__`,
  and `sys.modules`; this is not normal package-import evidence.
- `fix/geox-baseline-import-health-001@08d8fe9adeb355b91afb4dc101184bdf199ce84c`
  is an ancestor of current `main` with no unmerged commits.
- `feat/geox-calibration-source-manifest-validator-b-001@2b6745b9cbcf5a17196796231a39fec4336b5d1f`
  is divergent rejected historical work. Do not merge, cherry-pick, copy, or
  treat it as approved evidence.
- Rejected manifest task head
  `c18f56341b50c58505b59fc6cacf2337ca7f9fc4` and implementation
  `89c3ded7620b85e382cecec5243ca84f8fb93c95` are historical evidence only.

Stop and publish a Git-durable blocked state if any pin, source path, task
ownership, branch ancestry, or sibling dependency has materially changed.

## Owned paths

Implementation may modify only:

1. `tests/contracts/test_geox_calibration_source_manifest.py`
2. `tests/fixtures/test_geox_calibration_source_manifest_generator.py`
3. `docs/track_d/GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001.md`
4. `docs/execution/ACTIVE_TASK.md`
5. `docs/execution/EXECUTION_STATE.json`
6. `docs/execution/LATEST_COMPLETION_REPORT.md`

The branch may contain the task-authoring update to
`docs/execution/REPOSITORY_CONTEXT_INDEX.md`, but implementation must not modify
that file.

## Prohibited paths and operations

Do not modify:

- `panel_exp/**`;
- `scripts/build_geox_calibration_source_manifest.py`;
- `tests/fixtures/geox_calibration_handoff_sources/**`;
- `tests/fixtures/geox_governed_readouts/**`;
- other tests or fixtures;
- `pyproject.toml`, `poetry.lock`, dependency metadata;
- Docker, CI, Makefile, Git hooks, execution standards, or repository governance;
- MIP or MMM;
- any rejected or divergent feature branch.

Do not create a PR, merge, squash, rebase, force-push, cherry-pick, or merge
commit. Do not delete historical branches in this task.

## Exact implementation behavior

### 1. Replace synthetic validator import isolation

In `tests/contracts/test_geox_calibration_source_manifest.py`:

- remove the synthetic `types.ModuleType` package objects;
- remove manual package `__path__` assignment;
- remove `sys.modules` injection for `panel_exp` or `panel_exp.contracts`;
- import `panel_exp.contracts.geox_calibration_source_manifest` through the
  normal installed package;
- preserve the existing validator coverage and reason-code assertions;
- do not weaken, delete, or convert source comparisons into documentation-text
  checks.

The validator test must not use a fallback dynamic loader, `runpy`, or a copied
module to bypass normal package initialization.

### 2. Add an isolated installed-package validator probe

Add focused test evidence that launches the current Poetry interpreter in an
isolated subprocess:

- use `sys.executable -I`;
- use a temporary working directory outside the repository;
- remove `PYTHONPATH` and `PYTHONHOME` from the child environment;
- import the validator from
  `panel_exp.contracts.geox_calibration_source_manifest`;
- verify the imported module resolves to the installed repository package, not a
  temporary or synthetic module;
- load the committed manifest through the public loader;
- contextually validate it against the real governed-readout source root;
- require zero validation errors and `case_count == 12`;
- capture stdout and stderr and fail with exact diagnostics.

Do not add package exports or change `panel_exp/contracts/__init__.py`.

### 3. Prove clean-subprocess builder replay

In `tests/fixtures/test_geox_calibration_source_manifest_generator.py`, preserve
all current generator and negative-path coverage and strengthen deterministic
replay so that:

- the builder is invoked by absolute script path from a temporary working
  directory outside the repository;
- the child environment has no `PYTHONPATH` or `PYTHONHOME`;
- two isolated runs write separate temporary outputs;
- both outputs are byte-identical to each other and to the committed manifest;
- the complete `tests/fixtures/geox_governed_readouts/` file tree is
  byte-identical before and after both runs;
- no source file, committed manifest, or package module is rewritten.

Dynamic loading used only to mutate a copied source tree for existing negative
builder tests may remain. It is not accepted as positive import evidence.

### 4. Record the checkpoint

Create
`docs/track_d/GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001.md`
with:

- exact GeoX, MIP, and MMM pins;
- exact validator, builder, manifest, and source-tree paths;
- the removed synthetic-import mechanism;
- isolated validator and builder commands;
- focused, adjacent, Ruff, and Docker results;
- deterministic replay and source-tree immutability results;
- whether normal package import is proven;
- explicit `producer_certified: false`;
- explicit `mmm_compatibility_emitted: false`;
- explicit `calibration_signal_emitted: false`;
- the remaining certification gap;
- successor
  `GEOX_CALIBRATION_SOURCE_MANIFEST_CERTIFICATION_RECOVERY_001`,
  still unauthorized.

The checkpoint is validation evidence only and must not claim merged producer
certification or downstream eligibility.

## Failure behavior

A test-only defect within an owned test must be corrected. If normal installed
package import fails because package/runtime code, dependency metadata, or
Docker configuration would need to change, do not widen this milestone. Publish
`blocked` with:

- the exact failing command;
- full import traceback or subprocess diagnostics;
- whether host and Docker behavior agree;
- remediation attempted within owned tests;
- the exact prohibited path that would need a separately authorized task;
- a live resolution condition.

Do not hide product failures behind an environment blocker.

## Acceptance evidence

The implementation must prove:

1. no synthetic `panel_exp` or `panel_exp.contracts` modules remain in the
   validator test;
2. normal in-process package import succeeds;
3. isolated `python -I` import succeeds outside the repository with sanitized
   environment variables;
4. the isolated validator loads and contextually validates all 12 records;
5. the imported module path is the installed repository module;
6. existing intrinsic, contextual, path, checksum, identity, source-preservation,
   timestamp, prohibited-field, and authorization tests remain;
7. the builder runs twice in sanitized subprocesses outside the repository;
8. both outputs equal the committed manifest byte for byte;
9. the governed-readout source tree is unchanged;
10. no package, builder, manifest, source fixture, analytical, or authority path
    changed;
11. the checkpoint document states the result without certifying the producer.

Documentation searches alone are not acceptance evidence.

## Validation gate

Run on one frozen task-owned tree:

1. `poetry install --with dev --no-interaction`
2. Parse every changed JSON file with `python -m json.tool`.
3. Compile changed Python tests with `python -m py_compile`.
4. `git diff --check`
5. Verify exact changed paths against the authorization ancestry.
6. Prove synthetic import removal with:
   `rg -n "ModuleType|sys\.modules|__path__" tests/contracts/test_geox_calibration_source_manifest.py`
   and require no package-injection matches.
7. Run normal and isolated import evidence:
   `env -u PYTHONPATH -u PYTHONHOME poetry run python -I -c "from panel_exp.contracts.geox_calibration_source_manifest import validate_geox_calibration_source_manifest; print('geox-validator-import-ok')"`
8. Focused validator tests:
   `poetry run pytest -q tests/contracts/test_geox_calibration_source_manifest.py`
9. Focused builder tests:
   `poetry run pytest -q tests/fixtures/test_geox_calibration_source_manifest_generator.py`
10. Adjacent governed-readout tests:
    `poetry run pytest -q tests/contracts/test_geox_governed_experiment_readout.py tests/fixtures/test_geox_certified_governed_readout_fixtures.py`
11. Ruff:
    `poetry run ruff check tests/contracts/test_geox_calibration_source_manifest.py tests/fixtures/test_geox_calibration_source_manifest_generator.py`
12. Mypy: `not_required`; the synchronized repository has no configured mypy
    dependency or gate. Do not add mypy.
13. Repository-authored full Docker gate:
    `make validate-docker`
14. Confirm clean task-owned worktree, push/fetch success, and exact local/remote
    feature-head equality.

Record exact passed, failed, skipped, deselected, xfailed, xpassed, and warning
counts for each pytest gate. Record JSON, compilation, diff, changed paths,
import probe, Ruff, deterministic replay, source-tree immutability, Docker,
worktree, and remote equality results.

## Publication contract

On success:

1. Create one implementation commit containing only the two test changes and
   checkpoint document.
2. Update the three execution files to `ready_for_review` with the implementation
   SHA, exact evidence, remaining gap, and unchanged authority.
3. Freeze the complete task-owned tree and rerun the entire required gate.
4. Create one exact-tree publication receipt commit whose message identifies the
   task, implementation parent, validation commands/results, evidence source,
   worktree state, and authority impact.
5. Do not modify task-owned files after the receipt.
6. Push only `fix/geox-main-test-isolation-and-checkpoint-context-recovery-001`,
   fetch it again, and prove local/remote exact-head equality.
7. Stop for external exact-head review.

A genuine failure must end in a pushed `blocked` state on the same branch.

## Deferred successor

`GEOX_CALIBRATION_SOURCE_MANIFEST_CERTIFICATION_RECOVERY_001` remains separate
and unauthorized. It may be authored only after this checkpoint is merged and
must independently certify the combined producer on an exact frozen GeoX tree.

No MIP or MMM task is authorized by this milestone. No `CalibrationSignal`,
compatibility, simulation, optimization, planning, recommendation, real-data,
runtime, pilot, or production behavior is authorized.
