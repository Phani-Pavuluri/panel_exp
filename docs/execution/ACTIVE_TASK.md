# Active Task

**Status:** superseded
**Owner:** GeoX repository governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Main before supersession:** `ee9673c13e69082367c1727568946ac4c1a01015`
- **Preserved feature branch:** `feat/geox-governed-readout-builder-package-entrypoint-001`
- **Preserved branch head:** `216c53f13919ec5ee7fa060a9c052e8a074fb9cc`
- **Latest partial substantive commit:** `3dff0a75f89b507f42c76251a06a536529508afa`
- **MIP execution-standard main observed:** `369805d923454a51ce98845cea29bdb1ee3c3895`
- **MMM main observed:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Capability authorizations changed:** `false`

## Supersession decision

This task is superseded without merge. It combined several independently
reviewable outcomes in one long-lived branch: public lifecycle-contract design,
typed builder behavior, fixture migration and replay semantics, envelope and
version/provenance agreement, repository handoff evidence, and final full-suite
validation. Repeated correction cycles produced partial test progress and a
50-commit branch without a definition-ready, independently mergeable result.

Do not resume, merge, rebase, cherry-pick wholesale, create a pull request from,
or widen this branch. Preserve it as historical partial evidence. A successor
task may reuse a specific commit or hunk only when that successor explicitly
owns the behavior and independently validates it.

## Preserved partial evidence

The branch contains a non-production builder skeleton and focused fixture tests.
Commit `3dff0a75f89b507f42c76251a06a536529508afa` adds bounded before/after
source-truth hashing and deterministic repeated fixture-loader comparison across
12 cases. These are partial observations only; they do not complete the typed
temporal lifecycle, version/provenance/schema/envelope contract, semantic
handoff evidence, or full validation.

No implementation from the preserved branch is approved, merged, production
ready, or consumer accepted.

## Next eligible work

`GEOX_LEAN_REPOSITORY_DELIVERY_STANDARD_ADOPTION_001` is the sole next eligible
GeoX task. It must be a narrow governance-only task adopting the merged MIP lean
delivery, definition-ready task authoring, risk-tier validation, invocation-only
Codex prompt, durable exact-tree receipt, and terminal-outcome rules.

That task must not modify the preserved builder branch, analytical contracts,
fixtures, estimators, design, assignment, inference, or MIP/MMM repositories.
After adoption is merged and closed, builder work must resume through separately
authorized, definition-ready successor tasks with one primary mergeable outcome
each.

## Authority

Task execution, correction execution, merge, pull-request creation, sibling
adoption, and capability authority for the superseded builder are all false.
Production inference, assignment, MMM compatibility, `ExperimentEvidence`,
`CalibrationSignal`, `TrustReport`, `DecisionSurface`, recommendations,
optimization, LLM decisioning, scheduling, live integration, real data, pilot,
production, and package-side agents remain unauthorized.
