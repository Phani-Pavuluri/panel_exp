<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `merged`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_NATIVE_OUTPUT_PROVENANCE_AUDIT_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `6edfa269c3976bebb057f5ecd2fb459aaba2ae62`
- **Authorization provenance:** `77216eea718267e0e4b5178f429f7f83556144e6`
- **Feature branch:** `tests/geox-native-output-provenance-audit-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `b33c9baf8c265e29b7c60f6e6c2a18bb53c39b1c`
- **Reviewed head:** `4c5e511e2d08e25d93fcbaa31bd7b2920dcaf7b8`
- **Rejected review head:** `255a610682ae72b2a23b6f16c6c813df5406d1c7`
- **Rejected implementation commit:** `b33c9baf8c265e29b7c60f6e6c2a18bb53c39b1c`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `1`
- **Correction cycles remaining:** `0`
- **Review decision:** `merged`
- **Local feature-branch cleanup:** `observed_deleted`
- **Remote feature-branch cleanup:** `observed_deleted`
- **Capability authorizations changed:** `false`
<!-- END GEOX TASKCTL EXECUTION VIEW -->

## Primary outcome and existing owner direction

Add tests/validation/test_native_output_provenance_audit_001.py as a standing audit of provenance in actually generated native outputs and existing run-bundle passthrough. The owner requested Muse-owned bounded milestones and parallel progress within existing goals, and approved the preceding definition publication. Muse owns test approach and implementation; Codex independently reviews. One independently mergeable tests-only outcome, not producer certification or a new export boundary.

## Observable behavior and existing inputs/outputs

Using deterministic caller-provided inputs and the existing builder/pipeline APIs, cover at least one actual DesignEvidence and ExperimentEvidence output: recompute spec_hash, assignment_hash and input_data_hash using their existing canonicalization semantics and compare to the produced fields; verify package_version comes from live distribution __version__, and existing evidence_version presence/shape expectations. Assert existing run-bundle provenance fields survive its current serialization/passthrough without substitution. Use actual builder outputs, not fixture-generator version literals as authority. Separate native ReadoutEvidence coverage: it carries evidence_version, builder_version, identities, guardrails and payload, but does NOT carry package_version or the input-hash fields. Test only fields that type actually owns and preserve that limitation explicitly. Version strings are not a certification check or a new conformance rule. No new global version equality or opaque readout/artifact revision meaning. Freeze time or compare field-wise where created_at is inherently nondeterministic. Do not weaken guardrail/statistical assertions to obtain a passing output.

## Scope, failure semantics and named acceptance

Owned implementation: only the new tests/validation/test_native_output_provenance_audit_001.py plus the stable3 execution files for lifecycle/evidence. All product modules, existing tests, fixtures, golden data, schema/serialization, package/version values, gateways, estimators, numerical math, policies, snapshots, roadmap, context index and sibling files are read-only. No new fields, hashes, production stamping, export constructor, designated triple, certification or consumer readiness. API/compatibility/migration not_applicable: test addition only, no public bytes or behavior changed. Failed recomputation, missing owned field or altered passthrough must fail the new audit with the observed mismatch, never become a synthetic success. If an existing implementation defect blocks these tests, report the actual failure and distinct repair need under current task authority; do not change production to make the audit pass.

Acceptance evidence: actual generated design and experiment hash/package linkage, readout-only owned-field assertions with missing-field limitations, and existing run-bundle passthrough equality; all new audit cases green with source-backed rationale. Existing canonicalizers are source evidence, not a reason to assert fields absent from a type. No claim that this audit proves every workflow, numerical correctness, export readiness or a certified producer. Useful coverage and limitations must both appear in the human completion report.

## Gate and authority

Tier1 existing tests-only outcome. Required for execution, exact-head review and pre/post-FF: the entire new audit file; full focused tests/execution/test_taskctl.py; full tests/test_repo_native_execution_handoff.py; their combined suite; native python -m panel_exp.execution.taskctl check; json.tool, git diff --check, exact owned-path, source/authorization ancestry and unchanged-authority checks. Use repository .venv and PYTHONPATH rooted in the actual workspace. Full analytical/Docker/Ruff/mypy not_required for this narrow test addition; inherited two guardrail and one BRB failures remain named, unresolved and unwaived. Do not deselect or modify them to claim the analytical suite green.

Prerequisite: preceding GEOX_PRODUCER_PROVENANCE_FINALITY_DEFINITION_001 genuinely merged/closed at this task base, reviewed a52c5f49674be8ff06d6fa77c571b73815f49843. MIP/MMM are independent read-only context; no blocking certified pair or final designation is needed for test implementation. Preserve rejection_history and historical geox_main_pin/mip_main_pin/mmm_main_pin byte-for-byte. GeoX-only WS-GEOX-NATIVE-OUTPUT-PROVENANCE-AUDIT-001, owner geox_existing_native_provenance_validation. No coordination refresh, capability grant or sibling verification follows. Existing-field consumer export, final designation, gateway enforcement and certification remain separately gated successors.

Use native lifecycle/evidence recording and generated projections; task wording stays unchanged after authorization, with review findings in completion evidence. Rewrite Current outcome with actual results before publication, distinguishing implementation, validation, review and merge. Freeze the task-owned tree and run the declared gate on that exact tree. Publish a complete durable validation receipt naming actual implementation parent, gate commands/results and evidence, worktree and authority impact; keep the owned-path count and baseline factual. Verify exact remote head, then stop ready_for_review or genuine blocked. One existing correction cycle; no merge/PR/history rewrite/successor execution. Future routine publication eligibility follows the adopted policy and independent exact-head evidence, never a self-approval. Unresolved execution-blocking design questions: none.
