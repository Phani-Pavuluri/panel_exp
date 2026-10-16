<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `proposed`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_VALIDATION_ENTRYPOINT_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `a360c4cfcfa48eeaaf215beec6f44c47a462d9b5`
- **Authorization provenance:** `null`
- **Feature branch:** `feat/geox-validation-entrypoint-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `null`
- **Reviewed head:** `null`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `proposed`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END GEOX TASKCTL EXECUTION VIEW -->

## Primary outcome and owner direction

Materialize the owner-approved separate validation entrypoint while preserving ordinary `run_design()` behavior and the existing validation-owned guardrail boundary. Muse owns implementation; Codex independently reviews. This is a bounded validation orchestration task, not a production-default, statistical, certification, export, sibling, or analytical authority change.

## Proposed contract and scope

Add `panel_exp/validation/validated_design_runner_001.py` exposing `run_validated_design(geo, *, validate_design=None, build_contract, estimator_id=None, inference_id=None, geometry_id=None, readout_semantics=None)`. Inputs use existing runner and callback contracts. It returns the same `(mde_prc_df, mde_val_df, power_results_df)` triple, preserves error propagation and `validate_after_assign` semantics, and leaves evaluated guardrail evidence in `geo.last_evidence`. `build_contract` is required with no default: omission fails rather than selecting an inappropriate builder. Guardrail fields must be computed by the existing contract, combination and enforcement evaluators; no substituted constants, new statuses, thresholds, or vocabulary. The ordinary `run_design()` path remains unchanged and receives a dedicated regression guard.

## Scope, failure semantics and named acceptance

Owned implementation paths are exactly `panel_exp/validation/validated_design_runner_001.py` (the only new file), `tests/validation/test_design_guardrail_enforcement_001.py` (existing invocation updates plus a new dedicated default-path regression within this file), and `tests/validation/test_inference_boundary_guardrail_enforcement_001.py` (existing invocation updates only), plus the three stable execution files. Preserve every existing assertion and expected payload byte-for-byte. Existing default production orchestration, other tests, fixtures, goldens, controller, handoff tests, context index, evidence vocabulary, statistical truth, export/certification behavior, sibling repositories, and protected authority flags are read-only. Compatibility is opt-in: existing public calls remain unchanged; no schema/data migration. Muse owns implementation choices within this observable contract.

Acceptance evidence must prove computed payload identity, existing error behavior, required builder handling, and default-path output equality with guardrail fields still absent from ordinary runs. Existing `NOT_EVALUATED` and `allowed=False` semantics are evaluated outcomes when support is absent, not certification or permission to change default-deny behavior. Review existing evaluator results on the actual inputs; never manufacture meaningfulness by changing thresholds or assertions. BRB statistical truth, producer finality/certification, consumer designation and sibling readiness remain separately deferred.

## Gate and publication boundary

Tier 2 existing validation-owned orchestration. Required green for execution, exact-head review and pre/post-fast-forward: native `python -m panel_exp.execution.taskctl check`; complete `tests/execution/test_taskctl.py`, complete `tests/test_repo_native_execution_handoff.py`, and their combined suite; complete `tests/validation/test_design_guardrail_enforcement_001.py`, `tests/validation/test_inference_boundary_guardrail_enforcement_001.py`, and `tests/validation/test_design_tier1_contract_emission_001.py`; existing-assertion diff proof, JSON parsing, `git diff --check`, exact ownership, authorization ancestry and unchanged protected-authority checks. Run full `pytest tests/ -q` with zero new deselections: any inherited BRB failure must be reproduced and reported unwaived, while any new failure blocks publication. Use the verified repository environment with PYTHONPATH rooted in the actual workspace. Docker/Ruff/mypy are not required for this bounded deterministic validation orchestration; report those categories honestly. Run complete native metadata/handoff suites and state/view gates before publishing authoring. Record actual tested commit/tree, commands/results and limitations in durable evidence; never claim full suite green while BRB remains red.

The preceding native provenance audit is the merged prerequisite. Preserve rejection history and historical cross-repository pins byte-for-byte. This task is GeoX-only under `WS-GEOX-VALIDATION-ENTRYPOINT-001`; MIP and MMM remain independent.

Owner explicitly selected the separate validation entrypoint on October 16 with “proceed with recommendation,” preserving ordinary runs and validation-owned guardrails. This recorded direction permits native authorization of this bounded definition; it adds no production or statistical authority. Execution is invocation-only after Git authorization. Create the declared feature branch only from its verified finalized authorization baseline after bootstrap and remote branch-absence checks. Preserve immutable task wording after authorization, use native lifecycle/evidence recording, replace Current outcome with actual results, freeze and validate the exact task-owned tree, publish a receipt naming implementation parent and gates, prove remote equality, and stop ready_for_review or genuine blocked. One correction cycle; no implementation merge, PR, history rewrite, policy activation or successor execution. Unresolved execution-blocking design questions: none.
