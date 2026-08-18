# Active Task

**Status:** authorized
**Task ID:** `GEOX_PRODUCTION_VALIDATION_IMPORT_BOUNDARY_REPAIR_001`
**Repository:** `Phani-Pavuluri/panel_exp`
**Base SHA:** `b7ed73cfddf9025727b37edf5bd3f35af8bc7325`
**Implementation branch:** `fix/geox-production-validation-import-boundary-repair-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 2 — production/validation import-boundary repair
**Task execution authorized:** `true`
**Correction execution authorized:** `false`
**Merge authorized:** `false`
**PR creation authorized:** `false`
**Unresolved execution-blocking design questions:** none

## Objective

Repair the current production/validation import-boundary failures exposed by
the GeoX repository Docker gate. Production entry points must not statically or
at runtime import `panel_exp.validation`, and production source must not carry
validation-import references that violate the repository isolation contract.

Bound the repair to the actual import paths demonstrated by
`tests/test_validation_production_isolation.py`; do not mask failures by
weakening those tests. Preserve production analytical behavior and public APIs.

## Scope

Owned paths are only the directly offending production import modules and the
focused isolation test, plus the three stable lifecycle files required for
publication. Do not modify assignment, inference, SCM, TBR, UnitJackKnife,
D5 artifacts, calibration-source behavior, MIP, MMM, dependencies, Docker/CI,
or capability/product authority. The merged handoff-schema and import-
isolation tasks are historical evidence, not executable ancestry.

## Validation contract

Run JSON parsing, all tests in `tests/test_validation_production_isolation.py`,
focused import-regression tests for every changed boundary, Ruff and compile
validation on changed files, `git diff --check`, exact changed-path checks, and
the complete repository `make validate-docker` gate. Compare any remaining
failures with synchronized main and classify unrelated baseline families; do
not repair TBR, D5 artifacts, or other families here.

## Sequencing and authority

TBR, D5 artifact reconciliation, lifecycle adoption, producer certification,
MIP, MMM, analytical, runtime, and downstream capability work remain separate
and unauthorized. All product, runtime, certification, sibling, and capability
authority remains false. Stop at `ready_for_review` for external exact-head
review; do not create a PR or merge.
