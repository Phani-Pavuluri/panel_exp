# METHOD_SUITABILITY_RUNTIME_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_SUITABILITY_RUNTIME_001` |
| **Artifact type** | `method_suitability_runtime` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `runtime_classifies_method_family_review_suitability_no_estimator_or_inference_authorization` |
| **Base commit** | `2100861` (Define method suitability handoff contract) |
| **Final verdict** | `method_suitability_runtime_implemented_review_classification_only_no_estimator_or_inference_authorization` |

This artifact implements conservative deterministic evaluation of method-family **review suitability** from typed handoff facts. It classifies method-family review targets as eligible, restricted, diagnostic-only, blocked, or not evaluated. It does not execute estimators, compute inference, calculate lift, assign markets, promote methods, or authorize production.

---

## 2. Source files inspected

| File | Role |
|------|------|
| `METHOD_SUITABILITY_HANDOFF_CONTRACT_001` | Handoff packet contract source of truth |
| `DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001` | Assignment handoff preservation pattern |
| `DESIGN_CELL_STRUCTURE_RUNTIME_001` | Design structure gate pattern |
| `DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001` | Scenario handoff preservation pattern |
| `POWER_MDE_DIAGNOSTICS_RUNTIME_001` | Power/MDE handoff pattern |
| `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` | Spend/historical-support handoff |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Geo feasibility upstream |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Profiler upstream |

---

## 3. Implementation scope

**Implemented:** `evaluate_method_suitability` / `evaluate_method_family_suitability`; handoff readiness gates; estimand gate; review requirement detection; method-family review classification; governance/scenario/assignment/power/spend handoff preservation; claim boundaries; multiple handoff packets without ranking.

**Not implemented:** estimator execution, SCM/TBR/DID/AugSynth fit, placebo/jackknife/bootstrap/conformal inference, method-family final selection, estimator selection, inference method selection, method promotion, production compatibility authorization, geo assignment, matched pairs, blocks, randomization, rerandomization, thinning design, matching optimization, balance optimization, scenario policy feasibility computation, assignment feasibility computation, power/MDE computation, p-values/CIs, lift/ROI, budget optimization, MMM runtime calls, LLM decisioning, production authorization.

---

## 4. Relationship to method suitability handoff contract

Implements runtime evaluation for contract concepts: `MethodHandoffPacket`, upstream statuses, contrast summaries, estimand summaries, governance summary, review requirements, candidate method-family review targets, method handoff statuses, method-family suitability statuses, and claim boundaries defined in `METHOD_SUITABILITY_HANDOFF_CONTRACT_001`.

---

## 5. Relationship to design assignment feasibility runtime

Consumes `assignment_feasibility_status` from assignment handoff summary and upstream statuses. Blocks or provisionalizes method handoff when assignment feasibility is blocked per config. Does not recompute assignment feasibility (`assignment_feasibility_computed` remains false).

---

## 6. Relationship to design cell structure runtime

Consumes `design_cell_structure_status` from upstream handoff. Blocks method handoff when design structure is blocked. Does not re-validate cell/contrast structure.

---

## 7. Relationship to scenario policy feasibility runtime

Preserves `scenario_policy_status`, shared-control conflict, spend contrast status, and historical support via `ScenarioPolicyHandoffReport`. Does not recompute scenario policy feasibility (`scenario_policy_feasibility_computed` remains false).

---

## 8. Relationship to power/MDE runtime

Preserves `power_mde_status` via `PowerMdeHandoffReport`. Blocks inference-ready suitability claims when power/MDE is blocked. Emits low-power/high-MDE review requirement. Does not compute power or MDE (`power_computed` and `mde_computed` remain false).

---

## 9. Public API

```python
from panel_exp.validation.method_suitability_runtime_001 import (
    evaluate_method_suitability,
    evaluate_method_family_suitability,
    MethodSuitabilityConfig,
    MethodHandoffStatus,
    MethodFamilySuitabilityStatus,
    ReviewRequirementType,
)
```

Deterministic, side-effect-free, no network/randomness/LLM/MMM.

---

## 10. Input format

Per handoff packet: `design_id`, `handoff_status`, `design_structure_type`, `contrast_summaries`, `estimand_summaries`, `scenario_policy_summary`, `assignment_feasibility_summary`, `power_mde_summary`, `spend_summary`, `governance_summary`, `review_requirements`, `candidate_method_family_review_targets`, `upstream_statuses`.

Contrast summaries support: `contrast_id`, `contrast_type`, `estimand_label`, `bau_control_preserved`, `manipulation_policy`, `shared_control_conflict`, `split_control_required`, `required_vs_achieved_spend_contrast_status`, `historical_support_status`, `method_suitability_review_required`.

---

## 11. Output reports

`MethodSuitabilityReport` with subreports: readiness, estimand gate, design compatibility, review requirements, method-family suitability entries, scenario/assignment/power/spend/governance handoff, claim boundary, issues, warnings, blocking reasons.

Multiple packets return `design_reports` with per-packet reports and aggregate summary without ranking.

---

## 12. Method handoff statuses

All 16 handoff statuses implemented including `METHOD_HANDOFF_READY_FOR_SUITABILITY_REVIEW`, blocked variants by upstream gate, review-required variants (dosage, difference-in-policy, budget reallocation, redesign recheck), provisional, and not evaluated.

`METHOD_HANDOFF_READY_FOR_SUITABILITY_REVIEW` does not mean a method family was selected, an estimator was chosen, inference was authorized, or production is approved.

---

## 13. Method-family suitability statuses

Six suitability statuses implemented: `METHOD_FAMILY_ELIGIBLE_FOR_REVIEW`, `METHOD_FAMILY_ELIGIBLE_WITH_WARNINGS`, `METHOD_FAMILY_RESTRICTED`, `METHOD_FAMILY_DIAGNOSTIC_ONLY`, `METHOD_FAMILY_BLOCKED`, `METHOD_FAMILY_NOT_EVALUATED`.

`METHOD_FAMILY_ELIGIBLE_FOR_REVIEW` is not method approval. `METHOD_FAMILY_RESTRICTED` is not production approval. `METHOD_FAMILY_DIAGNOSTIC_ONLY` cannot be used as a production method.

---

## 14. Review requirement types

Fifteen review requirement types detected including standard incrementality, dosage, difference-in-policy, budget reallocation, go-live, common-control, split-control redesign, matched-pair, blocked/clustered design, rerandomization, interference-risk, low-power/high-MDE, out-of-historical-support, assignment feasibility, and method governance review.

---

## 15. Readiness gates

Nine upstream gates evaluated: profiler/data readiness, geo feasibility, spend feasibility, power/MDE readiness, design cell structure, scenario policy, assignment feasibility, estimand declaration, governance/catalog.

Hard blocks on profiler, geo, or design structure immediately block method handoff. Scenario policy and assignment feasibility block or provisionalize per config. Power/MDE blocks inference-ready claims; blocks handoff when configured.

---

## 16. Estimand gate behavior

Validates estimand label presence. Standard go-dark/heavy-up vs BAU requires BAU control preserved. Manipulated control blocks standard incrementality interpretation. Dosage, difference-in-policy, budget reallocation, and go-live contrasts require explicit estimand labels and emit corresponding review requirements.

---

## 17. Review requirement detection

Preserves upstream `method_suitability_review_required` flags and `review_requirements`. Detects requirements from contrast type, design structure, shared-control conflict, split-control recheck, historical support, power/MDE readiness, interference risk, and governance completeness.

---

## 18. Method-family classification logic

For each candidate method-family review target: governance blocked → `METHOD_FAMILY_BLOCKED`; diagnostic-only → `METHOD_FAMILY_DIAGNOSTIC_ONLY`; restricted → `METHOD_FAMILY_RESTRICTED`; unknown → `METHOD_FAMILY_NOT_EVALUATED`; handoff blocked or missing estimand → blocked/not evaluated; clean gates with warnings → `METHOD_FAMILY_ELIGIBLE_WITH_WARNINGS`; clean gates → `METHOD_FAMILY_ELIGIBLE_FOR_REVIEW`.

---

## 19. Governance handoff behavior

Preserves instrument catalog status, method roadmap status, governed/restricted/diagnostic-only/blocked method lists. Missing governance catalog emits `METHOD_GOVERNANCE_REVIEW`. Does not promote methods or convert diagnostic-only methods to production methods.

---

## 20. Scenario handoff preservation

Preserves scenario policy status, shared-control conflict, spend contrast status, and historical support warnings. Does not recompute scenario policy feasibility.

---

## 21. Assignment handoff preservation

Preserves assignment feasibility status. Blocks or provisionalizes method handoff per config when assignment is blocked. Emits split-control redesign or assignment feasibility review when redesign/recheck required. Does not compute assignment feasibility.

---

## 22. Power/MDE handoff preservation

Preserves power/MDE readiness status. Disallows inference-ready suitability claims when blocked. Emits low-power/high-MDE review. Does not compute power or MDE.

---

## 23. Spend handoff preservation

Preserves spend feasibility status and historical support warnings. Emits out-of-historical-support review when applicable. Does not compute spend feasibility or ROI.

---

## 24. Claim boundaries

`runtime_method_suitability_implemented`, `method_family_review_classification_implemented`, `review_requirement_detection_implemented`, `governance_stance_preservation_implemented`, `estimand_gate_implemented`, and `handoff_readiness_gate_implemented` are true. All method selection, computation, and authorization flags are false.

---

## 25. Tests added

42 targeted tests in `tests/validation/test_method_suitability_runtime_001.py` covering upstream gates, estimand gates, review requirements, method-family classification, handoff preservation, claim boundaries, and multiple packets.

---

## 26. Validation results

- Runtime pytest: pass
- Handoff contract regression: pass
- Assignment feasibility runtime regression: pass
- Design-cell/scenario/power/spend/geo/profiler regressions: pass
- Safety grep: pass
- JSON summary: pass

---

## 27. Known limitations

- Does not rank method families or select a final estimator.
- Governance catalog completeness is inferred from presence of catalog/roadmap/governed lists, not full catalog validation.
- Upstream blocked status detection relies on token patterns (`BLOCKED`, `*_BLOCKED`, `*_BLOCKED_BY_*`).
- Interference risk relies on explicit status fields in packet or assignment summary.

---

## 28. Recommended next artifact

**Primary:** `DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001`

**Alternative:** `READOUT_METHOD_GOVERNANCE_CONTRACT_001`

---

## Appendix: Examples

| Example | Outcome |
|---------|---------|
| Clean gates, go-dark vs BAU, governed TBR/DID families | Ready for suitability review; families eligible for review |
| Blocked profiler upstream | `METHOD_HANDOFF_BLOCKED_BY_DATA_READINESS` |
| Blocked scenario policy (default config) | `METHOD_HANDOFF_BLOCKED_BY_SCENARIO_POLICY` |
| Blocked assignment (config allows) | `METHOD_HANDOFF_PROVISIONAL` |
| Blocked power/MDE | Low-power review; inference-ready claim disallowed |
| Diagnostic-only SCM family | `METHOD_FAMILY_DIAGNOSTIC_ONLY` |
| Missing estimand | `METHOD_HANDOFF_BLOCKED_BY_MISSING_ESTIMAND` |
