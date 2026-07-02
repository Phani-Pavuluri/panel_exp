# DESIGN_ASSIGNMENT_RUNTIME_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `DESIGN_ASSIGNMENT_RUNTIME_001` |
| **Artifact type** | `design_assignment_runtime` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `deterministic_explicit_pool_assignment_only_no_matching_or_randomization` |
| **Base commit** | `0674ea2` (Define design assignment runtime contract) |
| **Final verdict** | `design_assignment_runtime_implemented_deterministic_explicit_pool_assignment_only_no_matching_or_randomization` |

This artifact implements a conservative deterministic assignment runtime that generates assignment artifacts from explicit eligible unit pools and declared cell requirements. It does not optimize matching, randomize, rerandomize, compute balance metrics, execute estimators, or authorize production.

---

## 2. Source files inspected

| File | Role |
|------|------|
| `DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001` | Contract source of truth |
| `DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001` | Assignment feasibility upstream |
| `METHOD_SUITABILITY_RUNTIME_001` | Method/instrument suitability upstream |
| `DESIGN_CELL_STRUCTURE_RUNTIME_001` | Design structure upstream |
| `DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001` | Scenario policy upstream |
| `POWER_MDE_DIAGNOSTICS_RUNTIME_001` | Power/MDE upstream |

---

## 3. Implementation scope

**Implemented:** `generate_design_assignment` / `generate_assignment_candidate`; readiness gates; deterministic explicit-pool allocation; assignment plan; one assignment candidate; unit/cell allocations; constraint trace; exclusion trace; reproducibility manifest; failure packet; method suitability preservation; multiple requests without ranking.

**Not implemented:** matching optimization, matched pairs, blocks, randomization, rerandomization, thinning design, balance optimization, balance diagnostics computation (placeholder `not_computed` only), interference adjustment, scenario/assignment feasibility/method suitability computation, estimator/inference execution, power/MDE, p-values/CIs, lift/ROI, production authorization.

---

## 4. Relationship to assignment runtime contract

Implements contract concepts from `DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001`: `AssignmentPlan`, `AssignmentCandidate`, `AssignmentUnitAllocation`, `AssignmentCellAllocation`, constraint/exclusion traces, reproducibility manifest, failure packet, and claim boundaries.

---

## 5. Relationship to assignment feasibility runtime

Consumes `assignment_feasibility_status` from upstream handoff. Blocks assignment generation when assignment feasibility is blocked. Does not recompute assignment feasibility.

---

## 6. Relationship to method suitability runtime

Consumes `method_instrument_suitability_matrix` and preserves instrument suitability statuses. Blocks when all instruments blocked; provisional when only diagnostic-only instruments remain. Does not compute method suitability.

---

## 7. Relationship to design cell structure runtime

Consumes `design_cell_structure_status`. Blocks when design structure is blocked.

---

## 8. Relationship to scenario policy feasibility runtime

Consumes `scenario_policy_feasibility_status`. Blocks or provisionalizes per config. Does not recompute scenario policy feasibility.

---

## 9. Public API

```python
from panel_exp.validation.design_assignment_runtime_001 import (
    generate_design_assignment,
    generate_assignment_candidate,
    DesignAssignmentRuntimeConfig,
    AssignmentRuntimeStatus,
)
```

Deterministic, side-effect-free, no network/randomness/LLM/MMM/estimators.

---

## 10. Input format

Per request: `design_id`, upstream statuses, `assignment_unit_universe`, `eligible_unit_pools`, `cell_requirements`, `assignment_constraints`, `assignment_algorithm_spec`, `reproducibility_config`, `method_instrument_suitability_matrix`, optional `artifact_registry_config`.

---

## 11. Output reports

`DesignAssignmentRuntimeReport` with `assignment_plan`, `assignment_candidates` (at most one), unit/cell allocation reports, constraint report/trace, exclusion trace, reproducibility manifest, failure packet, claim boundary report.

---

## 12. Runtime statuses

All 15 contract runtime statuses implemented. `ASSIGNMENT_RUNTIME_READY_TO_GENERATE` means a future attempt may proceed; it does not authorize causal readout or production.

---

## 13. Candidate statuses

All 7 candidate statuses implemented. This runtime generates at most one deterministic candidate per request.

---

## 14. Supported algorithm categories

`DETERMINISTIC_RULE_ASSIGNMENT`, `EXPLICIT_POOL_ASSIGNMENT`, `DECLARED_POOL_ASSIGNMENT`. `COMMON_CONTROL_ASSIGNMENT` and `SPLIT_CONTROL_ASSIGNMENT` supported only when cells and pools are explicitly declared.

---

## 15. Unsupported algorithm categories

`MATCHED_PAIR_ASSIGNMENT`, `BLOCKED_ASSIGNMENT`, `RERANDOMIZED_ASSIGNMENT`, `THINNING_ASSIGNMENT`, `RANDOMIZED_ASSIGNMENT`, `UNKNOWN_ASSIGNMENT_ALGORITHM` block assignment generation.

---

## 16. Readiness gates

Fourteen gates evaluated in contract order including data, geo, spend, power/MDE, design structure, scenario policy, assignment feasibility, method suitability, unit universe, cell requirements, constraints, algorithm spec, reproducibility config, artifact registry.

---

## 17. Deterministic allocation behavior

For each declared cell in stable sorted order: get explicit pool, filter by eligibility/constraints, sort by `deterministic_sort_key` (default `unit_id`), allocate first `required_unit_count` units. No backtracking, optimization, or search.

---

## 18. Method suitability behavior

Preserves instrument matrix; blocks when all instruments blocked; provisional warning when only diagnostic-only instruments; does not authorize estimator/inference.

---

## 19. Common-control and split-control behavior

Supported only when cell requirements and explicit pools declare control/treatment cells. No inference or redesign of cell structure.

---

## 20. Constraint trace behavior

Records constraints checked/passed/failed, binding constraints, per-unit trace. `constraint_relaxation_used` always false.

---

## 21. Exclusion trace behavior

Records every excluded unit with reason, source, optional cell/constraint IDs. No silent unit dropping.

---

## 22. Reproducibility manifest behavior

Records algorithm version, seed policy (`NOT_APPLICABLE_DETERMINISTIC`), input artifact IDs, config/unit/pool/cell hashes, output artifact ID/hash, deterministic sort key. `generated_at_policy`: `not_recorded_runtime_is_deterministic`.

---

## 23. Failure packet behavior

Emitted on blocking gates with blocking gates, failed constraints, insufficient units, method suitability blockers, and diagnostic-only retry categories.

---

## 24. Claim boundaries

`runtime_assignment_generation_implemented` true. `assignment_plan_generated`, `assignment_candidate_generated`, `unit_allocation_generated`, `geo_assignment_computed` true only when deterministic allocation succeeds. `assignment_candidate_selected` always false. All forbidden flags false.

---

## 25. Tests added

31 targeted tests covering success paths, blocking/failure packets, constraint/exclusion/reproducibility, claim boundaries, and multiple requests.

---

## 26. Validation results

- Runtime pytest: pass
- Contract regression: pass
- Safety grep: pass
- JSON summary: pass

---

## 27. Known limitations

- Only deterministic explicit-pool allocation; no rerandomization or balance search.
- Balance diagnostics placeholder only (`not_computed`).
- At most one candidate per request; no candidate selection.
- Common/split-control requires explicit declared cells and pools.

---

## 28. Recommended next artifact

**Primary:** `READOUT_METHOD_GOVERNANCE_CONTRACT_001`

**Alternative:** `READOUT_PLAN_CONTRACT_001`

---

## Appendix: Examples

| Example | Outcome |
|---------|---------|
| Two-cell explicit pools, sufficient units | Candidate generated; 4 unit allocations |
| Insufficient treatment units | Failure packet; candidate rejected/blocked |
| Duplicate unit in pools | Unique assignment constraint blocks/rejects |
| Blocked unit in `blocked_unit_ids` | Excluded with trace |
| Missing reproducibility config | Blocked by reproducibility requirements |
| All method instruments blocked | Blocked by method suitability |
| Diagnostic-only instruments | Provisional; no production authorization |
| Common-control C0 explicit pool | 3 control units allocated when declared |
