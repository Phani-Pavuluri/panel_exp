# GEOX_PRODUCTION_VALIDATION_IMPORT_BOUNDARY_REPAIR_001 — Authorization Report

- **Task:** `GEOX_PRODUCTION_VALIDATION_IMPORT_BOUNDARY_REPAIR_001`
- **Status:** authorized
- **Base/authorization SHA:** `b7ed73cfddf9025727b37edf5bd3f35af8bc7325`
- **Implementation branch:** `fix/geox-production-validation-import-boundary-repair-001`
- **Implementation:** not started
- **Risk tier:** Tier 2
- **Correction budget:** `0 completed / 1 remaining`
- **Merge/PR authority:** false

## Reason for authorization

The synchronized-main Docker gate exposes production/validation import-boundary
failures in `tests/test_validation_production_isolation.py`: static validation
references in production source and runtime loading of `panel_exp.validation`.
This task repairs only the actual offending import boundary, preserving public
APIs and analytical behavior without weakening the isolation tests.

## Validation required during implementation

JSON parsing, the complete production-validation isolation test module,
focused regressions for each changed boundary, Ruff, compile validation,
`git diff --check`, exact changed-path checks, and the complete
`make validate-docker` gate. Any unrelated TBR, D5 artifact, or other baseline
failure must be classified separately and not repaired here.

No implementation branch, implementation commit, PR, merge, or sibling change
was created in this authoring pass.
