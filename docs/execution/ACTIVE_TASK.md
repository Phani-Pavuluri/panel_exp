# Active Task

**Status:** merged
**Owner:** GeoX repository governance
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30

## Identity

- **Task ID:** `GEOX_BASELINE_IMPORT_HEALTH_RECOVERY_001`
- **Base branch/SHA:** `main` / `6d88e1a7b2ea861e9f61b27aea4adbd73b0ff337`
- **Feature branch:** `fix/geox-baseline-import-health-recovery-001`
- **Execution mode:** `branch_and_fast_forward`
- **Canonical MIP V2 pin:** `Phani-Pavuluri/marketing_intelligence_platform@38f88467f55d5bc4cc64e5a58b0f08f1639a40d0`
- **Canonical MMM workflow pin:** `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **External nonconforming PR:** `#128`
- **External branch head:** `08d8fe9adeb355b91afb4dc101184bdf199ce84c`
- **External merge commit:** `6d88e1a7b2ea861e9f61b27aea4adbd73b0ff337`
- **Suspended V2 adoption branch/head:** `feat/geox-repo-native-execution-handoff-v2-adoption-001` / `315ae7c996551c0f1fdb2414791be7e63586222d`
- **Capability authorizations changed:** `false`

## Recovery trigger

PR #128 merged the blocked baseline-repair branch into `main` without exact-head
approval, despite the task prohibiting PR creation and merge. Preserve that event
as nonconforming history; do not invent approval or rewrite history.

The merged partial repair correctly removed the Track-B/artifacts circular import.
Fresh-process imports pass, but full Docker collection still reports:

`ImportError: cannot import name 'BalancedRandomization' from 'panel_exp' (unknown location)`.

Because the same import succeeds in a fresh subprocess and `panel_exp/__init__.py`
exports the class, treat the remaining failure as suite-order contamination,
namespace-package shadowing, or import provenance corruption until proven otherwise.
Do not add another compatibility shim without evidence.

## Objective

## Externally authorized validation exception

For `GEOX_BASELINE_IMPORT_HEALTH_RECOVERY_001` only, the original full
`make validate-docker` completion criterion is waived. The acceptance gate is
focused isolated-Docker validation covering the import-health tests, the
formerly failing contract test, and `tests/test_audit_fixes.py`, together with
passing Ruff, JSON validation, and `git diff --check`. The incomplete full-suite
run remains unresolved GeoX repository-validation debt; this task does not
claim that the full suite passes. This exception does not apply to future GeoX
tasks.

Reconcile the unauthorized merge, identify the first point where full test
collection resolves `panel_exp` incorrectly, apply the smallest root-cause fix,
and restore complete Docker validation. Preserve the lazy artifacts export that
resolved the real circular import unless evidence shows a safer equivalent.

## Owned files

Execution may modify only:

- `panel_exp/__init__.py`
- `panel_exp/artifacts/__init__.py`
- `tests/test_import_surface_health.py`
- `tests/conftest.py` only when diagnostic evidence proves a collection-level
  provenance guard or fixture correction is the minimal root fix
- one existing test/helper file only when it is proven to create, replace, or
  shadow the `panel_exp` module; record the exact path and evidence before edit
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not change package behavior, assignment logic, estimators, contracts,
fixtures, dependency files, pytest marker policy, validation scripts, roadmaps,
MIP, MMM, or either suspended/legacy feature branch.

## Required execution

1. Fetch/prune, hydrate history, synchronize `main`, and prove
   `main == origin/main == 6d88e1a7b2ea861e9f61b27aea4adbd73b0ff337`
   before branching.
2. Verify the suspended V2 branch still equals
   `315ae7c996551c0f1fdb2414791be7e63586222d`; do not modify it.
3. Verify PR #128 merged head `08d8fe9...` as merge commit `6d88e1a...` without
   conforming approval. Record it; do not revert or rewrite it.
4. Reproduce in Docker:
   - the full-suite `BalancedRandomization` collection failure;
   - successful fresh-process import;
   - absence of the former Track-B/artifacts circular import.
5. Instrument collection without committing temporary diagnostics. Immediately
   before the failing import, capture:
   - `panel_exp` presence in `sys.modules`;
   - `__file__`, `__path__`, `__spec__`, loader, and module attributes;
   - relevant `sys.path` entries;
   - the earliest collected module or hook that created/replaced it.
6. Prove whether the cause is namespace-package shadowing, test import ordering,
   a test/helper mutation, or another mechanism. Do not guess from the error text.
7. Apply the smallest root fix. The final package-root import must resolve to the
   repository package and expose the exact class object from
   `panel_exp.design.assign.BalancedRandomization`.
8. Keep public imports compatible:
   - `from panel_exp import BalancedRandomization`
   - `from panel_exp.artifacts import export_geo_run_bundle`
   - `from panel_exp.track_b import build_geo_run_artifact_bundle`
   - `from panel_exp.track_b._registry import CALIBRATION_SIGNAL_BY_CONFIG`
9. Strengthen focused tests to cover fresh processes and a collection-order
   reproduction that would fail under the diagnosed contamination mechanism.
10. Run targeted failing collection, focused import tests, JSON/Markdown/path
    checks, Ruff on changed Python, disposable-Docker mypy, `git diff --check`,
    and Docker-backed `make validate-docker`.
11. Nine existing unknown `slow` marker warnings and two invalid-escape warnings
    may remain; report them but do not fix them here.
12. On failure, publish accurate `blocked` state. On success, publish
    `ready_for_review` with full implementation SHA, empty blockers,
    `merge_authorized: false`, null reviewed/approval SHAs, and unchanged
    capability authority.
13. Push and verify the exact remote head. Do not create a PR, merge, rebase,
    squash, delete branches, or modify `main` during execution.

## Acceptance criteria

- The import provenance root cause is documented with evidence.
- The circular import remains resolved.
- All four public import surfaces pass in fresh processes and full collection.
- `make validate-docker` completes successfully; known warnings are reported.
- The diff is restricted to owned files and changes no analytical semantics.
- The external PR merge remains explicitly nonconforming and unapproved.

## Later sequence

This task was fast-forward merged at the approved exact head
`2981749d62084a72e65281bf53b1b05be54ad389`. The focused-validation exception
and unresolved full-suite validation debt remain task-specific records.

After review and explicit exact-head approval, merge this recovery with
`git merge --ff-only` and create one closure commit. Then author a fresh V2
adoption-recovery task from repaired `main`; do not reuse or rewrite the old
blocked V2 branch.

## Prohibited authority

No design eligibility, assignment behavior, estimator/inference status,
instrument identity, governed-readout semantics, numerical truth,
multicell/shared-control claims, production inference, CalibrationSignal,
ExperimentEvidence, TrustReport, DecisionSurface, recommendation, LLM, budget,
or package-side-agent authority is changed or authorized.
