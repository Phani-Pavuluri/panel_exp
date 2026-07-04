# GOVERNED_RANDOMIZATION_RUNTIME_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `GOVERNED_RANDOMIZATION_RUNTIME_001` |
| **Artifact type** | `governed_randomization_runtime` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `governed_randomization_runtime_implemented_no_inference_or_claim_authorization` |
| **Base commit** | `67bd528` (Enforce statistical promotion thresholds) |
| **Final verdict** | `governed_randomization_runtime_implemented_no_inference_or_claim_authorization` |

---

## 2. Source files inspected

- `panel_exp/validation/design_assignment_runtime_001.py`
- `panel_exp/validation/design_assignment_runtime_contract_001.py`
- `panel_exp/validation/design_assignment_feasibility_runtime_001.py`
- `panel_exp/validation/assignment_panel_integrity_runtime_001.py`
- `panel_exp/validation/statistical_promotion_thresholds_001.py`
- `panel_exp/validation/method_suitability_runtime_001.py`
- `panel_exp/validation/readout_plan_runtime_001.py`
- Audit and governance docs

---

## 3. Audit finding being addressed

P0 governed runtime hardening identified missing governed causal randomization: assignment artifacts could be hand-specified or non-reproducible, undermining panel-integrity, execution, and claim-review gates for randomized experiments.

---

## 4. Problem statement

Unguided or manual assignment generation risks non-reproducible treatment/control labels. Randomized experiment readouts require auditable, seed-governed assignment artifacts before downstream review.

---

## 5. Runtime purpose

`generate_governed_randomization` produces deterministic, constraint-aware assignment artifacts from declared eligible units and cell requirements. It validates readiness, applies seed policy, allocates units via hashed pseudo-random ordering (no optimization), and emits reproducibility manifests compatible with assignment-panel integrity.

---

## 6. Input contract

Accepts dict, dataclass-like, or list input (multiple requests, no ranking).

Supported fields include: `design_id`, `randomization_type`, `eligible_units`, `excluded_units`, `cells`/`cell_requirements`, `allocation_ratio`, `target_cell_sizes`, `seed`, `seed_policy`, `strata_field`, `block_field`, `common_control_cell_id`, `split_control_cells`, upstream feasibility/suitability status, `production_context`.

---

## 7. Supported randomization types

- `TWO_CELL_COMPLETE_RANDOMIZATION`
- `MULTI_CELL_COMPLETE_RANDOMIZATION`
- `STRATIFIED_RANDOMIZATION` (requires `strata_field`)
- `BLOCK_RANDOMIZATION` (requires `block_field`)
- `COMMON_CONTROL_RANDOMIZATION` (requires `common_control_cell_id`)

Unsupported types fail closed with typed failure packets. Split-control requests without explicit multi-cell support return `SPLIT_CONTROL_REQUIRES_RECHECK`.

---

## 8. Seed policy

- Explicit seed: recorded and used when provided.
- Derived seed: stable request-payload hash when config allows (`allow_derived_seed=True`).
- Production context: blocks when explicit seed missing and derived seed disallowed.
- No wall-clock randomness.

---

## 9. Status taxonomy

- `GOVERNED_RANDOMIZATION_COMPLETED`
- `GOVERNED_RANDOMIZATION_COMPLETED_WITH_WARNINGS`
- `GOVERNED_RANDOMIZATION_BLOCKED`
- `GOVERNED_RANDOMIZATION_FAILED`
- `GOVERNED_RANDOMIZATION_NOT_EVALUATED`

Candidate statuses: `ASSIGNMENT_ARTIFACT_GENERATED`, `ASSIGNMENT_ARTIFACT_NOT_GENERATED`, `ASSIGNMENT_ARTIFACT_BLOCKED`.

---

## 10. Issue taxonomy

Includes: eligible units missing, duplicate unit IDs, cell requirements missing, insufficient units, invalid allocation ratio/target sizes, seed policy missing, unsupported randomization type, strata/block field missing or insufficient, common-control invalid, split-control recheck, feasibility/suitability blocked, production context requires governed randomization.

---

## 11. Retry categories

`FIX_ELIGIBLE_UNIT_POOL`, `FIX_CELL_REQUIREMENTS`, `FIX_RANDOMIZATION_CONFIG`, `ADD_SEED_POLICY`, `ADD_STRATIFICATION_FIELDS`, `ADD_BLOCK_FIELDS`, `RERUN_ASSIGNMENT_FEASIBILITY`, `RERUN_METHOD_SUITABILITY`, `REDESIGN_EXPERIMENT_STRUCTURE`, `DISABLE_PRODUCTION_CONTEXT`.

---

## 12. Algorithm description

Deterministic pseudo-random ordering from SHA-256 hash of `seed|unit_id|stratum|block`. Units sorted by hash; allocated to cells by declared target sizes or allocation ratios. Stratified/block randomization operates within strata/blocks. No optimization, search, or balance tuning.

---

## 13. Assignment artifact schema

Artifact includes: `assignment_artifact_id`, `assignment_candidate_id`, `assignment_hash`, `randomization_type`, `seed`, `seed_policy`, `cells`, `unit_allocations`, `reproducibility_manifest`.

Each allocation includes: `unit_id`, `assigned_cell_id`, `assigned_cell_role`, `treated`, `assignment_source=GOVERNED_RANDOMIZATION_RUNTIME_001`, optional stratum/block.

---

## 14. Assignment-panel integrity compatibility

Generated artifacts pass `evaluate_assignment_panel_integrity` when analysis panel labels match allocations. Mismatched panels fail integrity as expected. Integration tested.

---

## 15. Design assignment runtime integration

When `assignment_algorithm_spec.algorithm_category` is `RANDOMIZED_ASSIGNMENT` and `enable_governed_randomization=True`, `generate_design_assignment` delegates to governed randomization. Explicit-pool deterministic assignment path unchanged.

---

## 16. Research vs production boundary

Randomization artifact generation only. No estimator/inference execution, no claim authorization, no production authorization. Feasibility/suitability upstream gates preserved when supplied.

---

## 17. Claim / production authorization boundary

All authorization flags remain false. Positive capability flags: `governed_randomization_runtime_implemented`, `governed_randomization_artifact_generated`, `deterministic_seed_policy_enforced`, `randomization_reproducibility_manifest_recorded`, `assignment_panel_integrity_compatible_artifact_generated`.

---

## 18. Tests added

`tests/validation/test_governed_randomization_runtime_001.py` — public API, deterministic assignments, seed policy, validation failures, stratified/block/common-control, panel integrity integration, design assignment integration, list/dataclass input, authorization boundary.

---

## 19. Validation results

Targeted pytest passes. Summary JSON validates. Safety grep confirms no false authorization flags.

---

## 20. Known limitations

- No rerandomization optimization, balance optimization, or matched-market optimization.
- Split-control requires explicit multi-cell declaration; otherwise blocked.
- Multi-cell with implicit equal split when targets unspecified.
- Readout plan / method suitability integration deferred (optional, not required for this artifact).

---

## 21. Recommended next artifact

**Recommended:** `SRM_BALANCE_READOUT_DIAGNOSTIC_001`

**Alternative:** `CLAIM_AUTHORIZATION_RUNTIME_001`
