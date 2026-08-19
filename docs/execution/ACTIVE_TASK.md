# Active Task

**Status:** ready_for_review
**Task ID:** `GEOX_D5_COMMITTED_ARTIFACT_RECONCILIATION_LINEAGE_REPAIR_001`
**Repository:** `Phani-Pavuluri/panel_exp`
**Base SHA:** `c81e9180ca92e3c18ad81c8538cc20039bc5ea75`
**Implementation branch:** `fix/geox-d5-committed-artifact-reconciliation-lineage-repair-001-correction`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 1 — merge-lineage and lifecycle receipt repair
**Task execution authorized:** `true`
**Correction execution authorized:** `false`
**Merge authorized:** `false`
**PR creation authorized:** `false`
**Unresolved execution-blocking design questions:** none

## Objective

Create a fresh implementation lineage descended directly from current
`main@3656674837bec64f3527ace1efa08e101ec4ab7a` for the completed
`GEOX_D5_COMMITTED_ARTIFACT_RECONCILIATION_001` milestone. Preserve the already
reviewed D5 artifact contents and corrected smoke-callable `fail_requires_fix`
classification exactly; this task repairs Git ancestry and publication
receipts only.

The previously reviewed head
`6a6f433f734552821e298dadb8a6053efe91e2b5` is historical evidence and must not
be rebased, cherry-picked, merged, force-updated, or reused as executable
ancestry. No artifact regeneration is permitted.

## Owned scope

Only the five already-reviewed D5 artifact JSON files and the three stable
execution lifecycle files may be carried into the fresh lineage as exact
content. No content changes are authorized to artifacts, builders, tests,
production, analytical, inference, TBR, assignment, MIP, MMM, or capability
surfaces. The implementation must prove byte/content preservation against the
reviewed head and publish a fresh descendant from current main.

## Validation policy

Run JSON parsing, exact artifact-content comparison against reviewed head,
changed-path verification, `git diff --check`, and the focused D5 artifact
tests without regenerating artifacts. The full Docker gate is not required for
this lineage-only repair. No analytical or product authority is granted.

## External metadata correction

Rejected review head: `44bf08ee2989777362ff78d0e07b935350cd1076`.
The correction is metadata-only: align risk tier, no-regeneration validation
scope, correction state, and current GeoX main pin with this lineage-repair
contract. The five preserved artifacts remain untouched.

## Sequencing

This repair does not authorize lifecycle adoption, producer certification, TBR,
or import-boundary work. The next bounded task is
`GEOX_SYNTHETIC_CONTROL_PLACEBO_STRICT_COMPATIBILITY_REPAIR_001`, and it
remains unauthorized. Stop at `ready_for_review`; do not create a PR or merge.

Correction receipt: implementation `6f93071e2d8db3cd55f26659a8afb4786f08e071`
restores the five reviewed artifacts byte-for-byte from current-main lineage;
the correction cycle is consumed (`1 completed / 0 remaining`).
