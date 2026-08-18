# GEOX_CONTRACT_TEST_IMPORT_ISOLATION_REPAIR_001 — Authorized Task Handoff

- **Status:** authorized
- **Base main:** `cdcbeaac575e9953b4b005a9b42d650b67211cb4`
- **Implementation branch:** `fix/geox-contract-test-import-isolation-repair-001`
- **Authorization provenance:** `cdcbeaac575e9953b4b005a9b42d650b67211cb4`
- **Implementation:** not started
- **Merge/PR authority:** false

This task repairs only the current pytest import-isolation defect. Repository
evidence identifies `tests/contracts/test_geox_calibration_source_manifest.py`
as the bounded contamination source because it fabricates `panel_exp` and
`panel_exp.contracts` in global `sys.modules`; the implementation must confirm
that source and use normal package imports or fully scoped/restored manipulation.

The historical repair `cc43be7d1dd69488b2a683a0180b05889cf00e72` is precedent
only. The blocked lifecycle-adoption head
`cf816fcb781b4dc5df6173e68a5a37c2b766c480` is preserved as historical evidence
and must not be reused. Lifecycle adoption must be freshly re-authored from
repaired main after this task merges.

Required validation includes focused and reversed-order regressions, Ruff,
compile and JSON checks, scope checks, and a passing full `make validate-docker`.
No implementation, PR, merge, MIP/MMM change, or authority change has occurred.
