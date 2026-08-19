# GEOX_TBR_RECOVERY_CONTRACT_ALIGNMENT_001 — Authorization Report

- **Status:** `authorized`
- **Base/authorization SHA:** `7e1f4e1e5a39d22dcd67ae5448822120b9904946`
- **Implementation branch:** `fix/geox-tbr-recovery-contract-alignment-001`
- **Implementation:** not started
- **Correction budget:** `0 completed / 1 remaining`
- **Full Docker gate:** intentionally not required under the revised focused-validation policy

This task is narrowly scoped to the two synchronized-main TBR recovery
failures: the positive-effect smoke direction test and the same-seed metrics
test. Future implementation must preserve deterministic recovery behavior and
existing analytical contracts without modifying TBR production code, D5
artifacts, or unrelated baseline families.

Required validation is JSON parsing, focused and ordered/reversed TBR recovery
tests, Ruff, compile validation, diff checking, and changed-path verification.
No implementation, branch creation, PR, merge, sibling change, or authority
change has occurred.
