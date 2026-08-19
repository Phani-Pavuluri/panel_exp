# GEOX_TBR_RECOVERY_CONTRACT_ALIGNMENT_001 — Ready for Review

- **Status:** `ready_for_review`
- **Base/authorization SHA:** `28bba2438ddee140061776ebc38a8c64df6ef028`
- **Implementation branch:** `fix/geox-tbr-recovery-contract-alignment-001`
- **Implementation commit:** `d3ad972df75379505993f0849c6f19ba69f41a19`
- **Validation tree:** `c6d2c7821c693120c3c7829c4ec7dccdf02f2695` plus the implementation commit
- **Correction budget:** `0 completed / 1 remaining`

## Behavior repaired

The validation-owned recovery runner now adapts unit-level synthetic worlds to
production TBR's explicit pre-aggregated contract: one treated series and one
control series. Production TBR, TBRRidge, SCM, UnitJackKnife, inference,
assignment, analytical semantics, artifacts, and public APIs were unchanged.

## Validation

- Focused nodes:
  `tests/test_estimator_recovery_smoke.py::test_smoke_positive_effect_direction[TBR]`
  and `tests/test_recovery_runner.py::test_same_seed_identical_metrics[TBR]` — **2 passed**.
- Ordered recovery modules (`tests/test_estimator_recovery_smoke.py` then
  `tests/test_recovery_runner.py`) — **11 passed**, 3 warnings.
- Reverse order — **11 passed**, 3 warnings.
- Ruff on changed validation modules and recovery tests — passed.
- Compile validation — passed.
- JSON parse — passed.
- `git diff --check` — passed.
- Full Docker gate — not run; the task's focused validation policy explicitly
  defers the repository-wide gate.

No unrelated baseline family was modified. The next local baseline task,
`GEOX_D5_COMMITTED_ARTIFACT_RECONCILIATION_001`, remains unauthorized. The
parked isolation milestone and lifecycle adoption remain separately governed
and unauthorized. No PR, merge, sibling change, or analytical/product/
capability authority change occurred.
