# GEOX_CONTRACT_TEST_IMPORT_ISOLATION_REPAIR_001 — Ready for Review

- **Status:** `ready_for_review`
- **Implementation commit:** `254097a761dcfc08a2993bab83e256144e6ddf8c`
- **Correction receipt:** this exact-tree lifecycle correction
- **Rejected review head:** `4271837477d361580e25fdf410e0b8002b9e6a8d`
- **Correction cycles:** `1 completed / 0 remaining`
- **Merge/PR authority:** false

## Scope and repair

The sole implementation change removes fabricated `panel_exp` and
`panel_exp.contracts` modules from
`tests/contracts/test_geox_calibration_source_manifest.py`, uses normal
package imports, and verifies real package identity and the
`BalancedRandomization` export. No production or analytical code changed.

## Validation

- JSON parse: passed.
- Contract + audit order: `78 passed, 2 warnings`.
- Audit + contract reverse order: `78 passed, 2 warnings`.
- Explicit module identity/sys.modules regression: passed as part of the
  contract test file.
- Ruff: passed.
- Compile validation: passed.
- `git diff --check`: passed.
- Full command: `make validate-docker`.
- Full receipt: `/private/tmp/geox-import-isolation-correction-docker.log`.
- Full exit receipt: `/private/tmp/geox-import-isolation-correction-docker.exit`,
  exit code `1` (the wrapper’s raw shell status was not used; the Make result
  is the authoritative command result).
- Full result: `13 failed, 6162 passed, 28 skipped`, `2164367 warnings`,
  `3752.96s`.

## Exact remaining failure inventory

1. `tests/test_estimator_recovery_smoke.py::test_smoke_positive_effect_direction[TBR]`
2. `tests/test_inference_registry_equivalence.py::test_numeric_outputs_match_golden_fixture[BlockResidualBootstrap]`
3. `tests/test_recovery_runner.py::test_same_seed_identical_metrics[TBR]`
4. `tests/test_repo_native_execution_handoff.py::test_v2_state_contract_and_pins`
5. `tests/test_validation_production_isolation.py::test_production_entry_points_do_not_statically_import_validation`
6. `tests/test_validation_production_isolation.py::test_production_source_files_contain_no_validation_import_string[impact.py]`
7. `tests/test_validation_production_isolation.py::test_production_source_files_contain_no_validation_import_string[design/geo_runner.py]`
8. `tests/test_validation_production_isolation.py::test_importing_production_paths_does_not_load_validation_subprocess`
9. `tests/track_d/test_d5_stat_augsynth_point_001.py::TestD5StatAugSynthPoint001::test_committed_artifact_matches_build`
10. `tests/track_d/test_d5_stat_mcell_percell_001.py::TestD5StatMcellPercell001::test_committed_artifact_matches_build`
11. `tests/track_d/test_d5_stat_smoke_callable_001.py::TestD5StatSmokeCallable001::test_committed_artifact_matches_build`
12. `tests/track_d/test_d5_stat_tbr_agg_001.py::TestD5StatTbrAgg001::test_committed_artifact_matches_build`
13. `tests/track_d/test_d5_stat_tbrridge_inf_001.py::TestD5StatTbrridgeInf001::test_committed_artifact_matches_build`

The failing inventory contains no contract-manifest test and no
`BalancedRandomization` collection/import-poisoning failure. Every remaining
failure is outside this task’s owned import-isolation scope and remains
successor baseline debt; none is claimed resolved here.

The rejected receipt is corrected under the repository correction lifecycle.
The task is ready for external exact-head review despite the nonzero full gate
because the gate result is fully classified baseline debt and the task-owned
failure is absent. No successor task, PR, merge, analytical, runtime,
certification, sibling, or capability authority was started or changed.
