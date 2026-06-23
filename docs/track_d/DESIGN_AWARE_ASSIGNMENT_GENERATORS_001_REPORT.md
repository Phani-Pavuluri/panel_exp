# DESIGN-AWARE-ASSIGNMENT-GENERATORS-001

**Artifact ID:** DESIGN-AWARE-ASSIGNMENT-GENERATORS-001  
**Type:** Package capability + validation  
**Date:** 2026-06-03  
**Module:** `panel_exp/design/assignment_generators.py`  
**Summary:** [`DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_summary.json`](archives/DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_summary.json)

**Regenerate:** `poetry run python -m panel_exp.validation.design_aware_assignment_generators_001 --summary-output docs/track_d/archives/DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_summary.json --overwrite`

---

## 1. Executive summary

Implemented the first governed **design-aware pseudo-assignment generator** layer in `panel_exp`. The module exposes a deterministic contract for generating pseudo-treated assignments that preserve original design constraints (treated-set size, eligibility, block/stratum/pair structure).

**Governance verdict:** `design_aware_assignment_generators_defined_no_inference_authorization`  
**Next artifact:** `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001`

This artifact defines and validates design-aware pseudo-assignment generation. It does not implement placebo p-values, randomization inference, TrustReport promotion, CalibrationSignal export, production decisioning, live API, scheduler, MMM ingestion, or budget optimization.

---

## 2. Why this artifact exists

[`INFERENCE_REPLACEMENT_SCOUT_001`](../audits/INFERENCE_REPLACEMENT_SCOUT_001.md) selected **design-aware assignment generation** as the binding prerequisite before treated-set placebo, permutation, or randomization-style inference can be trusted.

Design-aware pseudo-assignment generation is a prerequisite for treated-set placebo, permutation, and randomization-style inference. A pseudo-assignment that ignores the original design can produce misleading null distributions and invalid p-values.

---

## 3. Relationship to INFERENCE_REPLACEMENT_SCOUT_001

| Scout recommendation | This artifact |
|---------------------|---------------|
| Primary: `DESIGN_AWARE_ASSIGNMENT_GENERATORS_001` | **Implemented** |
| Secondary: `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001` | **Next** |
| Reject BRB/KFold tuning | Unchanged — no resampling work |
| Defer conformal/Bayesian lanes | Unchanged |

---

## 4. Assignment generator contract

**API:**

- `AssignmentFamily` / `AssignmentRole` / `ValidityStatus` enums
- `AssignmentUnit`, `AssignmentDesignSpec`, `PseudoAssignment` dataclasses
- `generate_pseudo_assignments(spec) -> list[PseudoAssignment]`
- `validate_pseudo_assignment(spec, assignment) -> PseudoAssignment`
- `summarize_assignment_generation(spec, assignments) -> dict`

---

## 5. Supported assignment families

| Family | Generator behavior |
|--------|-------------------|
| `complete_randomized_set` | Combinatorial/sampled treated sets from eligible units |
| `matched_pair_randomized` | Exactly one treated per pair |
| `matched_block_randomized` | Preserved treated count per block |
| `stratified_randomized` | Preserved treated count per stratum |
| `rerandomized_design_candidate` | Balance filter when rule present; else downgrade |
| `greedy_matched_market_falsification` | Falsification pseudo-sets |
| `kernel_thinning_falsification` | Falsification pseudo-sets |
| `fixed_deterministic_falsification` | Falsification pseudo-sets |
| `unknown_assignment_blocked` | Empty output (blocked) |

---

## 6. Design-based candidate families

- `complete_randomized_set`
- `matched_pair_randomized`
- `matched_block_randomized`
- `stratified_randomized`
- `rerandomized_design_candidate` (only when explicit balance/acceptance rule supplied)

Role: `DESIGN_BASED_RANDOMIZATION_CANDIDATE`

---

## 7. Falsification-only families

- `greedy_matched_market_falsification`
- `kernel_thinning_falsification`
- `fixed_deterministic_falsification`
- `rerandomized_design_candidate` when acceptance rule missing (downgraded)

Role: `FALSIFICATION_ONLY`

---

## 8. Blocked families

- `unknown_assignment_blocked` — `UNKNOWN_ASSIGNMENT_DESIGN_BLOCKED`, no assignments
- Malformed pairs/blocks/strata — empty output with blocked decision class
- Too few valid combinations — `ASSIGNMENT_GENERATION_BLOCKED_TOO_FEW_VALID_ASSIGNMENTS`

---

## 9. Constraint preservation rules

1. No duplicate treated units; no excluded/ineligible treated units  
2. Treated-set size matches observed assignment  
3. Treated/control disjoint within eligible universe  
4. Pair: exactly one treated per pair  
5. Block/stratum: preserved treated counts per group  
6. Deterministic under fixed `(spec, seed)`  
7. Deterministic/falsification families never marked design-based candidates  

---

## 10. Determinism and reproducibility

Harness `determinism_checks.passed: true` — identical pseudo-assignment sequences for repeated calls with the same `AssignmentDesignSpec`. Different seeds produce different sampled orders/selections where sampling is used.

---

## 11. Scenario results

| Scenario | Result |
|----------|--------|
| `complete_randomized_positive` | PASS |
| `complete_randomized_blocked_too_few` | PASS (blocked) |
| `matched_pair_positive` | PASS |
| `matched_pair_malformed_blocked` | PASS (blocked) |
| `matched_block_positive` | PASS |
| `stratified_positive` | PASS |
| `rerandomized_downgrade_without_rule` | PASS (falsification only) |
| `rerandomized_balance_filtered` | PASS (design-based) |
| `greedy_falsification_only` | PASS |
| `kernel_thinning_falsification_only` | PASS |
| `fixed_deterministic_falsification_only` | PASS |
| `unknown_assignment_blocked` | PASS (empty) |

All scenarios passed; `failed_scenarios: []`.

---

## 12. What this enables next

- `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001` — governed treated-set placebo semantics on valid pseudo-assignments  
- Permutation/rerandomization inference scaffolding (future)  
- SCM/TBRRidge/AugSynth falsification tests with design-respecting nulls  

---

## 13. What this does not authorize

| Surface | Authorized |
|---------|------------|
| TrustReport | **false** |
| CalibrationSignal | **false** |
| Production decisioning | **false** |
| Live API | **false** |
| Scheduler | **false** |
| MMM ingestion | **false** |
| Budget optimization | **false** |
| Placebo p-values / CIs | **not implemented** |

---

## 14. Known limitations

- No placebo p-value or interval computation  
- Rerandomization without explicit acceptance rule downgrades to falsification only  
- Greedy/thinning/fixed outputs never promoted to design-based randomization  
- Large combination spaces sampled (not exhaustive) above `max_assignments`  
- Does not connect to live `design/assign.py` runtime yet — contract-first module  

---

## 15. Governance verdict

`design_aware_assignment_generators_defined_no_inference_authorization`

---

## 16. Residual Issues and Handoff

### Resolved in this artifact

- Design-aware pseudo-assignment contract defined and tested  
- `INV-MULTITREATED-DESIGN-AWARE-PLACEBO-001` disposition: `TREATED_SET_PLACEBO_FRAMEWORK_DEFINED_PENDING_METHOD_SPECIFIC_VALIDATION`

### Deferred (unchanged)

- `INV-MULTICELL-MULTIPLICITY-CALIBRATION-001`  
- `INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001`

### Next artifact

`MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001` (completed — see treated-set placebo framework report)
