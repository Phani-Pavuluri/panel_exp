# GEOX_CONTRACT_TEST_IMPORT_ISOLATION_REPAIR_001 — Blocked Validation Report

- **Status:** blocked
- **Base main:** `769692cfee166406c5672f5197ab0c73abbde669`
- **Implementation branch:** `fix/geox-contract-test-import-isolation-repair-001`
- **Implementation commit:** `254097a761dcfc08a2993bab83e256144e6ddf8c`
- **Review decision:** blocked; no PR or merge authority

## Repair performed

`tests/contracts/test_geox_calibration_source_manifest.py` no longer fabricates
`panel_exp` or `panel_exp.contracts` modules in `sys.modules`. It uses normal
package imports and verifies that the real package identity and
`BalancedRandomization` export remain intact. The test file was mechanically
formatted so its required Ruff check is meaningful; no production code changed.

## Focused evidence

- JSON parse: passed.
- Contract test + audit order: `78 passed, 2 warnings`.
- Audit + contract reverse order: `78 passed, 2 warnings`.
- Ruff on the changed contract test: passed.
- Compile validation: passed.
- `git diff --check`: passed before lifecycle publication.
- The prior `BalancedRandomization` collection ImportError did not reproduce in
  either focused order.

## Full Docker evidence

Command: `make validate-docker`.

Receipt: `/private/tmp/geox-import-isolation-validate-docker.log`.

Exit receipt: `/private/tmp/geox-import-isolation-validate-docker.exit` (exit
code `1`). The complete gate finished normally with:

`13 failed, 6162 passed, 28 skipped, 2213912 warnings in 3772.44s`.

Remaining exact failure families are:

- `tests/test_estimator_recovery_smoke.py::test_smoke_positive_effect_direction[TBR]`
- `tests/test_inference_registry_equivalence.py::test_numeric_outputs_match_golden_fixture[BlockResidualBootstrap]`
- `tests/test_recovery_runner.py::test_same_seed_identical_metrics[TBR]`
- `tests/test_repo_native_execution_handoff.py::test_v2_state_contract_and_pins`
- four production/validation import-boundary tests;
- five D5 committed-artifact reproducibility tests.

These are outside this import-isolation repair and remain synchronized-main
baseline families. The exact full log contains their tracebacks and warning
summary.

## Blocker and resolution

The task remains blocked by `DOCKER_GATE_REMAINING_BASELINE_FAILURE_FAMILIES`.
The resolution condition is repair and focused validation of the remaining
baseline families followed by a complete repository Docker gate with exit code
0. No analytical, runtime, producer-certification, capability, sibling, PR or
merge authority changed. The blocked lifecycle-adoption head
`cf816fcb781b4dc5df6173e68a5a37c2b766c480` remains historical evidence and
must be freshly re-authored after baseline repair.

No successor task was started and no correction cycle was consumed.
