# ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001` |
| **Artifact type** | `assignment_panel_integrity_runtime` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `assignment_panel_integrity_runtime_implemented_no_assignment_generation_or_claim_authorization` |
| **Base commit** | `b705471` (Document method blocklist remediation roadmap) |
| **Final verdict** | `assignment_panel_integrity_runtime_implemented_no_assignment_generation_or_claim_authorization` |

---

## 2. Source files inspected

- `panel_exp/validation/design_assignment_runtime_001.py`
- `panel_exp/validation/design_assignment_feasibility_runtime_001.py`
- `panel_exp/validation/estimator_inference_execution_runtime_001.py`
- `panel_exp/validation/estimator_inference_did_executor_003.py`
- `panel_exp/validation/readout_did_diagnostics_002.py`
- `panel_exp/validation/readout_diagnostics_sensitivity_runtime_001.py`
- `panel_exp/validation/readout_plan_runtime_001.py`
- `panel_exp/validation/production_catalog_blocklist_001.py`
- `panel_exp/validation/did_instrument_estimand_registry_001.py`
- Audit and governance docs

---

## 3. Audit finding being addressed

Expanded adversarial audit (`AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001`) identified assignment-panel mismatch risk: governed execution could proceed when analysis panel treatment/cell labels diverge from assignment artifact allocations. Valid estimator runs on wrong treatment labels remain invalid.

---

## 4. Problem statement

Assignment lineage must be verified before execution evidence can support downstream review. Without an integrity gate, panel data could carry stale, hand-edited, or join-corrupted treatment labels that disagree with the authoritative assignment artifact.

---

## 5. Runtime purpose

`evaluate_assignment_panel_integrity` validates that analysis panel unit treatment/cell labels match assignment artifact allocations before estimator execution, diagnostics, claim review, or trusted readout. Research assignment generation and randomization are out of scope.

---

## 6. Input contract

Accepts dict, dataclass-like, or list input (multiple requests, no ranking).

Supported fields: `assignment_artifact`, `assignment_candidate`, `assignment_plan`, `assignment_allocations`, `unit_allocations`, `reproducibility_manifest`, `assignment_artifact_id`, `assignment_hash`, field-name overrides, `analysis_panel`, `panel_records`, `panel_data`, `expected_treatment_values`, `allowed_cell_labels`, `require_hash_match`, etc.

Panel formats: `list[dict]`, dict with `records` / `panel_records`, or `execution_data_contract.panel_data`.

---

## 7. Status taxonomy

- `ASSIGNMENT_PANEL_INTEGRITY_PASSED`
- `ASSIGNMENT_PANEL_INTEGRITY_PASSED_WITH_WARNINGS`
- `ASSIGNMENT_PANEL_INTEGRITY_FAILED`
- `ASSIGNMENT_PANEL_INTEGRITY_BLOCKED`
- `ASSIGNMENT_PANEL_INTEGRITY_NOT_EVALUATED`

---

## 8. Issue taxonomy

`ASSIGNMENT_ARTIFACT_MISSING`, `ASSIGNMENT_ALLOCATIONS_MISSING`, `PANEL_RECORDS_MISSING`, `UNIT_ID_FIELD_MISSING`, `TREATMENT_FIELD_MISSING`, `CELL_FIELD_MISSING`, `DUPLICATE_ASSIGNMENT_UNIT`, `CONFLICTING_ASSIGNMENT_LABELS`, `UNASSIGNED_PANEL_UNIT`, `MISSING_PANEL_UNIT`, `TREATMENT_LABEL_MISMATCH`, `CELL_LABEL_MISMATCH`, `ASSIGNMENT_HASH_MISMATCH`, `ASSIGNMENT_ARTIFACT_ID_MISMATCH`, `INVALID_TREATMENT_LABEL`, `INVALID_CELL_LABEL`, `TREATED_OR_CONTROL_GROUP_MISSING`.

---

## 9. Retry categories

`FIX_ASSIGNMENT_ARTIFACT`, `FIX_PANEL_DATA_CONTRACT`, `FIX_ASSIGNMENT_PANEL_JOIN`, `FIX_TREATMENT_LABEL_MAPPING`, `FIX_CELL_LABEL_MAPPING`, `REGENERATE_ASSIGNMENT_ARTIFACT`, `DISABLE_PRODUCTION_CONTEXT`.

---

## 10. Integrity checks

Deterministic checks: artifact/allocations/panel presence, unit ID fields, uniqueness, panel-in-assignment coverage, treatment/cell consistency, hash/id match when required, allowed label validation, treated+control presence.

Conservative defaults: require artifact, allocations, panel; block on mismatch; warn on extra assigned units not in panel when configured.

---

## 11. Execution runtime integration

`estimator_inference_execution_runtime_001` evaluates integrity when panel data is present and `enable_assignment_panel_integrity_gate=true`. Failures emit `EXECUTION_BLOCKED_BY_ASSIGNMENT_PANEL_INTEGRITY` with retry `FIX_ASSIGNMENT_PANEL_JOIN`. Dry-run requests without panel data skip the gate.

---

## 12. DID executor integration

`estimator_inference_did_executor_003` calls integrity runtime when allocations or assignment artifact accompany panel data. Default blocks on integrity failure before point-estimate computation.

---

## 13. Diagnostics/readout propagation

- `readout_did_diagnostics_002` blocks when upstream integrity report indicates failure.
- `readout_diagnostics_sensitivity_runtime_001` preserves `assignment_panel_integrity_status` in evidence aggregation.
- `readout_plan_runtime_001` emits warning when upstream integrity status failed (no planning-time execution).

Integrity pass is not diagnostic pass or claim authorization.

---

## 14. Research-vs-production boundary

Research assignment generation remains in `DESIGN_ASSIGNMENT_RUNTIME_001`. This artifact validates only; it does not generate assignments or randomize units. Production blocklist from `PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001` remains enforced separately.

---

## 15. Claim / production authorization boundary

No claim authorization runtime, trusted readout handoff, production authorization, inference execution, p-values, CIs, uncertainty, MMM, or LLM decisioning added. All authorization flags remain false.

---

## 16. Tests added

`tests/validation/test_assignment_panel_integrity_runtime_001.py` — pass, warn, fail paths, hash gating, list/dataclass input, provenance hash, execution/DID integration regressions.

---

## 17. Validation results

Targeted validation and governance pytest pass. Safety greps confirm no unauthorized capability flags.

---

## 18. Known limitations

- Does not validate time-varying treatment switches within panel (uses per-unit invariant label).
- Readout plan does not execute integrity checks at planning time (upstream status propagation only).
- Hash match requires explicit config or both hashes provided.

---

## 19. Recommended next artifact

**Recommended:** `STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001`

**Alternative:** `GOVERNED_RANDOMIZATION_RUNTIME_001`
