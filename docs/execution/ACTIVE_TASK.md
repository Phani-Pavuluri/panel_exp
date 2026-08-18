# Active Task

**Status:** merged
**Task ID:** `GEOX_CONTRACT_TEST_IMPORT_ISOLATION_REPAIR_001`
**Repository:** `Phani-Pavuluri/panel_exp`
**Base SHA:** `cdcbeaac575e9953b4b005a9b42d650b67211cb4`
**Implementation branch:** `fix/geox-contract-test-import-isolation-repair-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 2
**Task execution authorized:** `true`
**Correction execution authorized:** `false`
**Merge authorized:** `false`
**PR creation authorized:** `false`
**Implementation commit:** `254097a761dcfc08a2993bab83e256144e6ddf8c`
**Reviewed head:** `1b295f807f3ed74d2aa60cf13509142263134f67`
**Review decision:** `merged` by fast-forward; full-gate nonzero result remains classified baseline debt
**Unresolved execution-blocking design questions:** none

## Objective

Repair the bounded pytest/package-import contamination that replaces or shadows
the real `panel_exp` package during collection and causes later tests to lose
the public `BalancedRandomization` export. The current identified surface is
`tests/contracts/test_geox_calibration_source_manifest.py`, which fabricates
`panel_exp` and `panel_exp.contracts` module objects in `sys.modules`. The
implementation must verify this source from collection evidence and repair only
the actual contaminating test, fixture, or import helper.

Normal `import panel_exp` and `from panel_exp import BalancedRandomization` must
remain valid before and after the offending tests. No production package change
is authorized unless independent evidence proves a production import defect.

## Historical and lifecycle evidence

Historical precedent `cc43be7d1dd69488b2a683a0180b05889cf00e72` removed a
fabricated package from a different test and is evidence only. The blocked
lifecycle-adoption feature head
`cf816fcb781b4dc5df6173e68a5a37c2b766c480` remains untouched historical evidence;
it must not be cherry-picked, rebased, merged, or transplanted. After this
repair merges, lifecycle adoption must be freshly re-authored from repaired
main because that branch will no longer be fast-forward mergeable.

## Acceptance and validation

Require focused contamination identity tests, the identified contract group,
`tests/test_audit_fixes.py`, reversed/order-sensitive execution, no residual
`sys.modules` contamination, unchanged contract behavior, Ruff, compile
validation, JSON parsing, `git diff --check`, changed-path verification, and a
complete `make validate-docker` run. The task-owned import-poisoning/
`BalancedRandomization` collection failure must be absent, and the feature must
introduce no new full-gate failure. Remaining failures must be classified as
pre-existing, independently owned baseline families and are not repaired here.

## Scope

Owned paths are the identified contract/test/import-isolation files and the
required execution lifecycle files. Prohibited paths include `panel_exp/__init__.py`,
analytical methods, assignment, inference, TBR, SCM, UnitJackKnife,
calibration-source behavior, artifacts, P2 capability semantics, MIP, MMM,
product/runtime behavior, and authority fields. Do not start TBR, create a PR,
merge, or create the implementation branch during authoring.
