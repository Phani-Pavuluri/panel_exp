# Active Task

**Status:** blocked
**Owner:** GeoX repository governance
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** GeoX `main` / `1262b14fcbacc8947af9ecffd6ad2704c1cb8cce`

## Identity

- **Task ID:** `GEOX_BASELINE_IMPORT_HEALTH_REPAIR_001`
- **Base branch/SHA:** `main` / `1262b14fcbacc8947af9ecffd6ad2704c1cb8cce`
- **Feature branch:** `fix/geox-baseline-import-health-001`
- **Execution mode:** `branch_and_fast_forward`
- **Canonical MIP V2 pin:** `Phani-Pavuluri/marketing_intelligence_platform@38f88467f55d5bc4cc64e5a58b0f08f1639a40d0`
- **Canonical MMM workflow pin:** `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Suspended task:** `GEOX_REPO_NATIVE_EXECUTION_HANDOFF_V2_ADOPTION_001`
- **Suspended branch/head:** `feat/geox-repo-native-execution-handoff-v2-adoption-001` / `315ae7c996551c0f1fdb2414791be7e63586222d`
- **Suspended implementation:** `6dc5fe455c49d764932ee9abf05c5ab2f55f609c`
- **Capability authorizations changed:** `false`

## Why this repair is required

A clean detached worktree at exact `origin/main` reproduces the same Docker
collection failures seen on the suspended V2 adoption branch. The adoption
branch changes only workflow-owned files and did not introduce either failure.

Baseline failure 1 is an eager-import cycle:

`panel_exp.track_b._registry` -> `panel_exp.track_b.__init__` ->
`panel_exp.track_b.export` -> `panel_exp.artifacts.run_bundle` ->
`panel_exp.artifacts.__init__` -> `panel_exp.artifacts.geo_run_export` ->
`panel_exp.track_b.export`.

Baseline failure 2 is `from panel_exp import BalancedRandomization`. The class is
already defined in `panel_exp/design/assign.py` and already exported by
`panel_exp/__init__.py`; therefore treat this as likely fallout from the earlier
package-initialization failure. Do not change the public export unless it still
fails after the cycle is removed.

Nine `pytest.mark.slow` warnings and two unrelated invalid-escape deprecation
warnings are non-blocking and outside this repair unless a changed file directly
requires an adjustment.

## Objective

Restore deterministic package import health and clean Docker test collection
with the smallest import-topology repair. Preserve all current public import
surfaces and runtime behavior. This task does not authorize or alter GeoX
analytical semantics.

## Owned files

Execution may modify only:

- `panel_exp/artifacts/__init__.py`
- `panel_exp/artifacts/geo_run_export.py` only if required
- `panel_exp/track_b/__init__.py` only if required
- `panel_exp/track_b/export.py` only if required
- `panel_exp/__init__.py` only if `BalancedRandomization` still fails after the
  cycle repair
- `tests/test_import_surface_health.py`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify estimators, designs, assignment algorithms, evidence contracts,
fixtures, governed-readout semantics, validation registries, roadmaps,
`pyproject.toml`, lock files, MIP, MMM, or the suspended V2 branch.

## Required implementation

1. Synchronize exact `main` and verify `main == origin/main ==
   1262b14fcbacc8947af9ecffd6ad2704c1cb8cce` before branching.
2. Verify the suspended V2 branch still equals
   `315ae7c996551c0f1fdb2414791be7e63586222d`; do not modify, rebase, merge,
   reset, delete, or force-update it.
3. Reproduce both clean-main import failures before changing code.
4. Break the eager-import cycle with the least invasive mechanism. Prefer a
   lazy package re-export or function-boundary import over moving business logic
   or changing public API names.
5. Preserve these public imports:
   - `from panel_exp.artifacts import export_geo_run_bundle`
   - `from panel_exp.track_b import build_geo_run_artifact_bundle`
   - `from panel_exp.track_b._registry import CALIBRATION_SIGNAL_BY_CONFIG`
   - `from panel_exp import BalancedRandomization`
6. Do not change the behavior, signature, or returned values of
   `export_geo_run_bundle` or `build_geo_run_artifact_bundle`.
7. Add focused import-health tests using fresh Python subprocesses so import
   order cannot be hidden by module cache. Cover the four imports above in
   isolation and in both artifact/Track-B orderings. Verify top-level
   `BalancedRandomization` is the same class as
   `panel_exp.design.assign.BalancedRandomization`.
8. Run the previously failing collection tests directly, the focused import
   tests, JSON/Markdown/path checks, Ruff on changed Python files, mypy in a
   disposable Docker Poetry environment without changing dependency files,
   `git diff --check`, and Docker-backed `make validate-docker`.
9. Do not register the slow marker or repair unrelated deprecation warnings in
   this task.
10. If any required validation fails, publish an accurate `blocked` branch
    state and stop.
11. If all gates pass, publish `ready_for_review` with a full 40-character
    implementation SHA, empty blockers, `merge_authorized: false`, null
    reviewed/approval SHAs, and unchanged capability authority.
12. Push and verify the exact remote branch head, then stop. Do not create a PR,
    merge, or delete any branch during execution.

## Acceptance criteria

- Clean Docker collection no longer reports the Track-B/artifacts circular
  import.
- `BalancedRandomization` imports successfully from the package root without a
  new compatibility shim unless one is proven necessary after cycle removal.
- Existing artifact and Track-B package-root imports remain valid.
- Full `make validate-docker` passes; the nine known slow-marker warnings may
  remain and must be reported accurately.
- The diff is limited to owned files and contains no analytical behavior change.

## Completion report requirements

Record exact baseline reproduction, root cause, changed paths, public-import
compatibility evidence, targeted and full validation, warnings, implementation
commit, exact remote review head, suspended V2 branch integrity, limitations,
and authority impact.

## Later sequence

After exact-head approval, merge this repair by fast-forward and create one
closure commit. Do not resume or rewrite the suspended V2 branch. After repair
closure, author a fresh GeoX V2 adoption-recovery task from the repaired `main`;
the old blocked V2 branch will be preserved as superseded evidence until that
new task defines cleanup.

## Prohibited authority

Do not change or authorize design eligibility, assignment behavior, estimator or
inference status, instrument identity, governed-readout semantics, numerical
truth, multicell/shared-control claims, production inference, CalibrationSignal,
ExperimentEvidence, TrustReport, DecisionSurface, recommendations, LLM
orchestration, budget authority, or package-side agents.
