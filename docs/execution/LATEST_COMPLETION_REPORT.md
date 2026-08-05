# TASK_AUTHORIZATION_REPORT

## Superseded disposition

- **Disposition:** `superseded_without_merge`
- **Task ID:** `GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001`
- **Rejected remote head:** `c18f56341b50c58505b59fc6cacf2337ca7f9fc4`
- **Recorded correction implementation:** `89c3ded7620b85e382cecec5243ca84f8fb93c95`
- **Reason:** The sole correction did not satisfy the Git-authored correction contract or complete the required validation gate; no correction cycles remain.
- The feature branch is preserved as historical evidence only. It is not merged, cherry-picked, reused, or reinterpreted.

## Current decision

- **Current decision:** `task_authored_pending_state_authorization`
- **Task ID:** `GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Pre-authoring base:** `80dbe14c6b2ce74b33a2b776c5e567afba582bf5`
- **Intended feature branch:** `feat/geox-certified-calibration-source-manifest-001`
- **Risk tier:** Tier 3 certified cross-repository producer fixture
- **Implementation SHA:** not yet created
- **Capability authority:** unchanged

## GitHub-observed orientation evidence

- GeoX `main` was synchronized at `80dbe14c6b2ce74b33a2b776c5e567afba582bf5` before task authoring.
- The prior calibration-source fixture task is superseded without merge. Its preserved branch at `a84d85277f9bbc35c08a40308d65858adbd36713` is historical failed-attempt evidence only and is explicitly excluded from implementation reuse.
- Certified `GeoXGovernedExperimentReadout` fixtures remain under `tests/fixtures/geox_governed_readouts/`; the canonical manifest contains exactly 12 source cases and records `mmm_compatibility_emitted: false`.
- The certified source checkpoint is `860182386c39f487747de5f43e67a31e9978e57c`; the canonical readout contract is `panel_exp/contracts/geox_governed_experiment_readout.py`.
- Source truth demonstrates that certification, MIP handoff expectation, method status, readout status, and handoff eligibility are distinct producer concepts. This successor therefore preserves those fields verbatim and does not invent a derived eligibility verdict.
- MIP `main` was observed at `0b4cd1fca73716e4968c2ceb70c594ad8aadd8ca`.
- MIP task `MIP_P2_GEOX_MMM_COMPATIBILITY_FIXTURE_BRIDGE_001` remains blocked on branch head `480b32040ce185b8ff091435121c4bea6fc6c453` by `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`.
- MMM `main` was observed at `f2e0eade0ad917c1b28ab5521e6d35a35047d988`; its current task is an unrelated proposed governance task with no execution authority.
- No active or proposed executable GeoX work overlaps the new source-manifest surface.

## Authorized outcome after the state-only boundary

Publish one strict, deterministic, non-authorizing 12-record GeoX calibration-handoff source manifest.

The task adds:

- a narrow typed source-record contract and contextual validator;
- a deterministic manifest builder;
- one committed manifest with stable IDs, exact paths, checksums, synthetic fixture timestamps, freshness provenance, and copied producer status/lineage fields;
- behavioral tests over all 12 existing certified fixtures;
- producer documentation and durable execution evidence.

The task deliberately does not export a new public package entrypoint and does not modify `panel_exp/contracts/__init__.py`.

## Ownership and non-actions

GeoX owns the source evidence identity, producer provenance, fixture time scope, experiment/readout truth, method and instrument fields, certification fields, and handoff fields.

MMM owns compatibility. MIP owns consumer reconciliation and canonical `CalibrationSignal` construction.

This task does not authorize compatibility evaluation, compatibility fixtures, `CalibrationSignal`, analytical recomputation, runtime integration, TrustReport, DecisionSurface, simulation, optimization, planning, recommendation, LLM behavior, real data, pilot, production, or modifications to MIP/MMM.

## Validation requirement

The frozen task requires:

- `poetry install --with dev --no-interaction` before host validation;
- changed JSON parsing and Python compilation;
- exact owned-path and `git diff --check` verification;
- focused and adjacent certified-readout tests with exact counts;
- Ruff on all changed Python files;
- mypy recorded as `not_required` because the synchronized repository has no configured mypy dependency or gate;
- two isolated byte-identical builder runs matching the committed manifest;
- complete source-tree immutability proof;
- fresh-image repository-authored `make validate-docker` validation with exact counts and warnings;
- exact-tree publication receipt;
- clean task-owned worktree and exact local/remote branch equality.

Host missing dependencies or a stale prebuilt image do not establish a blocker unless the declared repository-authored installation or Docker command itself fails with external diagnostics.

## Cross-repository impact

Successful GeoX merge advances only the GeoX producer-source portion of `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`.

The blocker remains unresolved until MMM separately publishes linked compatibility evidence and MIP performs consumer verification and its own blocker transition. No sibling task is authorized by this report.

## Task-authoring boundary

The task-authoring range begins at `80dbe14c6b2ce74b33a2b776c5e567afba582bf5` and changes only:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

This commit is the final task-authoring head. The immediate next commit must change only `docs/execution/EXECUTION_STATE.json`, record this exact task-authoring head as `authorization_head_sha`, and authorize the declared feature branch. The branch must then be created from the resulting state-only authorization head.

## Publication and review boundary

Successful execution must publish one exact remote `ready_for_review` head containing exactly one implementation SHA and one exact-tree receipt. Merge and PR authority remain false until external exact-head approval.

At most one externally directed correction cycle is permitted. A second failed exact-head review supersedes the task without merge.
