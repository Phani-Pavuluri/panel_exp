<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `authorized`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_PRODUCER_PROVENANCE_FINALITY_DEFINITION_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `2ff493c884ac06aaf8359e349fc8008f1872528a`
- **Authorization provenance:** `6e9adb0895912a905c15943788f499ea50802d06`
- **Feature branch:** `docs/geox-producer-provenance-finality-definition-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `true`
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
- **Review decision:** `authorized`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END GEOX TASKCTL EXECUTION VIEW -->

## One outcome and explicit owner adoption

Publish docs/GEOX_PRODUCER_PROVENANCE_FINALITY_DEFINITION_001.md as the bounded producer provenance/finality definition direction the owner explicitly adopted. In the coordinating conversation, the owner selected “Adopt the definition direction” after the concrete question: keep package, builder and schema identities separate using the existing fields, then prepare a bounded definition document; no estimator changes, export implementation or certification. This task materializes that choice in documentation only. Muse owns the definition document and approach; Codex independently reviews it. Actual numbers/pins, implementation, certification and downstream readiness remain separate.

## Defined behavior and compatibility boundary

Document the source-backed current boundary: native build_guarded_readout returns ReadoutEvidence; no production constructor/mapping to GeoXGovernedExperimentReadout exists. Classify that export translation as a future implementation gap, not a completed stamp call. Preserve GeoXReadoutProvenance's existing four fields: source_repo, source_commit, producer_package_version and created_by. Keep package, builder and evidence-schema identity domains distinct; builder identity is documented through the existing created_by convention, without adding builder_version or changing serialization. Existing readout_version and artifact_version remain opaque strings carried verbatim: do not invent revision semantics, synchronize all version namespaces or designate actual version numbers.

Document how a later explicit owner designation names the exact consumer-required producer identity and evidence before finality is asserted. No final designation occurs in this task. Distinguish producer evidence, final designation, downstream consumer verification and certification. Version naming alone cannot certify a producer, resolve BRB numerical issues or unblock calibration pairing. Keep the existing field shape and mixed-version reader/writer behavior unchanged; a future new field would require separate versioned compatibility work. The direction choices above are owner-adopted; any unresolved materially different meaning must remain a named future decision, not an invented implementation choice.

## Scope and acceptance evidence

Owned implementation: the one definition document plus stable3 lifecycle/evidence files. No Python, tests, fixtures, schemas, serializers, controller, gateways, version bumps, roadmap, snapshot or sibling edits. No actual export builder, enforcement, producer certification, numerical truth, BRB formula/golden change or calibration eligibility. Named source evidence: panel_exp/contracts/geox_governed_experiment_readout.py, panel_exp/validation/readout_boundary_builder_001.py, panel_exp/validation/estimator_readout_adapter_001.py, package metadata and existing governed-readout fixtures. Verify each claim against exact source/pin. The document must give domain meanings, existing-field mapping with opaque passthrough, an illustrative future designation-record shape marked non-operative, compatibility impact and independently gated next steps. No exact version triple or certification grant is selected.

## Gate, lineage and protected history

Tier2 owner-adopted definition documentation. Required for execution, exact-head review and pre/post-FF: taskctl check; full focused controller suite tests/execution/test_taskctl.py; full handoff suite tests/test_repo_native_execution_handoff.py; their combined suite; json.tool, git diff --check; owned-path, authorization ancestry and source-reference checks. Run tests with the repository .venv and PYTHONPATH rooted here. Full analytical/Docker/Ruff/mypy are not_required for this documentation-only changed surface, not waived; inherited two guardrail-emission failures and BRB golden mismatch remain separately reported and unresolved. Do not deselect them to claim a green analytical suite. Carry all rejection_history entries and preserved historical geox_main_pin/mip_main_pin/mmm_main_pin byte-for-byte; these are historical observations, not current branch baselines. Record live sibling observations separately without refreshing the snapshot. Modified GeoX only; workstream WS-GEOX-PRODUCER-PROVENANCE-FINALITY-DEFINITION-001, owner geox_producer_provenance_documentation. No consumer dependency is resolved.

Use native taskctl for lifecycle/projections and typed v6 completion evidence, with accurate Current outcome. Freeze the exact task-owned tree, run the required gate and publish a durable receipt naming implementation parent, gates/results/evidence, worktree and authority impact. Verify exact remote feature head and stop ready_for_review or genuine blocked. One correction cycle, no PR/merge/history rewrite or successor execution. Publication is outside Tier1 routine delegation; exact-head owner approval is required later. Unresolved execution-blocking design questions: none.
