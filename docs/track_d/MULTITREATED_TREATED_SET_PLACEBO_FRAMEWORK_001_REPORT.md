# MULTITREATED-TREATED-SET-PLACEBO-FRAMEWORK-001

**Artifact ID:** `MULTITREATED-TREATED-SET-PLACEBO-FRAMEWORK-001`  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/treated_set_placebo.py`  
**Validation:** `panel_exp/validation/multitreated_treated_set_placebo_framework_001.py`  
**Summary:** [`archives/MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001_summary.json`](archives/MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001_summary.json)

---

## 1. Executive summary

This artifact defines the multi-treated treated-set placebo framework using governed design-aware pseudo-assignments. It does not authorize TrustReport, CalibrationSignal, production decisioning, live API, scheduler, MMM ingestion, budget optimization, final p-values, or confidence intervals.

The framework evaluates an observed treated-set statistic against design-valid pseudo-treated sets (or falsification-only pseudo sets) with explicit semantic classification, placebo rank, and empirical tail fraction labeled **framework-only**.

**Governance verdict:** `multitreated_treated_set_placebo_framework_defined_no_inference_authorization`

**Next artifact:** `SCM_PLACEBO_GOVERNED_SEMANTICS_001`

---

## 2. Why this artifact exists

Real GeoX tests often have **multiple treated geos**. Single-treated placebo or leave-one-treated-out diagnostics are not valid substitutes for full treated-set placebo logic. This artifact answers:

> Can panel_exp evaluate observed treated-set effects against design-valid pseudo-treated sets while preserving strict semantic boundaries?

---

## 3. Dependency on DESIGN_AWARE_ASSIGNMENT_GENERATORS_001

The framework consumes `panel_exp.design.assignment_generators`:

- `AssignmentDesignSpec`, `PseudoAssignment`, `AssignmentRole`
- `generate_pseudo_assignments()` for complete, matched-pair, matched-block, stratified, rerandomized, falsification, and unknown-blocked families

Pseudo-treated sets are generated under the declared assignment design before placebo scoring.

---

## 4. Single-treated placebo vs treated-set placebo

| Concept | Scope |
|---------|--------|
| **Single-treated placebo** | One treated unit replaced by pseudo-treated controls |
| **Multi-treated treated-set placebo** | Entire observed treated set replaced by design-valid pseudo-treated sets |

This framework targets **multi-treated** experiments where the full treated set must move together under design constraints.

---

## 5. Why leave-one-treated-out is not placebo inference

Leave-one-treated-out over observed treated units is **not** multi-treated placebo inference. It is a **treated-unit sensitivity diagnostic**. Multi-treated placebo requires replacing the **full treated set** with pseudo-treated sets generated under the original assignment design or a declared falsification design.

Explicit requests to use leave-one-treated-out as placebo are rejected with decision `leave_one_treated_out_rejected_as_placebo`.

---

## 6. Treated-set placebo API and contract

Public API in `panel_exp.inference.treated_set_placebo`:

| Symbol | Role |
|--------|------|
| `PlaceboSemanticRole` | `design_based_randomization_candidate`, `falsification_diagnostic`, `blocked` |
| `PlaceboDecision` | Supported, falsification-only, blocked, LOTO rejected, too few, unknown design, multicell blocked |
| `TreatedSetPlaceboSpec` | Design spec, observed statistic, pseudo stats map, thresholds, metadata |
| `TreatedSetPlaceboResult` | Decision, rank, tail fraction, role counts, warnings |
| `evaluate_treated_set_placebo()` | Main entry point |
| `classify_placebo_semantics()` | Role from pseudo-assignments |
| `compute_placebo_rank()` | Inclusive rank and tail fraction |
| `reject_leave_one_treated_out_as_placebo()` | Explicit LOTO rejection |
| `summarize_treated_set_placebo_result()` | Validation/archive serialization |

---

## 7. Statistic contract

Deterministic statistic inputs — no full estimator runs in this artifact.

- **Kinds:** `absolute_effect`, `relative_effect`, `studentized_effect`, `signed_effect`, `rank_statistic`
- **Directions:** `greater`, `less`, `two_sided`
- **Tail rule:** inclusive count / `num_valid_placebo_sets`
- **Label:** empirical tail fraction is **framework-only** — not a production p-value

Pseudo statistics are keyed by `assignment_id` and must align exactly with valid `PseudoAssignment` objects.

---

## 8. Design-based candidate semantics

When pseudo-assignments are `DESIGN_BASED_RANDOMIZATION_CANDIDATE` and count ≥ `minimum_valid_placebo_sets`:

- `semantic_role = design_based_randomization_candidate`
- `decision = placebo_framework_supported`
- Outputs: observed statistic, pseudo vector, placebo rank, empirical tail fraction, support count, warnings

Supported design families in validation: complete randomized, matched pair, matched block, stratified, rerandomized (with explicit acceptance rule).

---

## 9. Falsification-only semantics

When assignments are `FALSIFICATION_ONLY` (greedy, thinning, fixed deterministic, rerandomized without rule):

- `semantic_role = falsification_diagnostic`
- `decision = placebo_framework_falsification_only`
- Diagnostic rank and tail fraction allowed with required warning:

> Pseudo-assignments are falsification-only because the original assignment mechanism is deterministic, design-search-based, or not known to be randomized.

---

## 10. Blocked semantics

Blocked when:

- Unknown assignment design
- Too few valid pseudo assignments
- Malformed constraints (via empty generator output)
- Invalid requested semantic role
- Multicell global/winner claim attempted
- Missing or mismatched pseudo statistics
- TrustReport / CalibrationSignal / production / budget requests

---

## 11. Rank and tail-fraction examples

From `complete_randomized_positive` scenario (toy deterministic stats):

- Inclusive rank under `two_sided` compares `|pseudo|` to `|observed|`
- `empirical_tail_fraction = rank / num_valid_placebo_sets`
- Metadata label: `framework_tail_fraction_label: not_production_p_value`

Unit tests verify `greater`, `less`, and `two_sided` tail rules deterministically.

---

## 12. Scenario results

| Category | Scenarios | Outcome |
|----------|-----------|---------|
| **Positive** | 5 design-based families | `placebo_framework_supported` |
| **Falsification-only** | 4 deterministic / downgrade paths | `placebo_framework_falsification_only` |
| **Blocked** | 10 governance / data failures | blocked decisions |

All 19 harness scenarios pass under `--strict`.

---

## 13. Multicell/global/winner claim boundary

`multicell_global_claim_requested` in metadata triggers `multicell_global_claim_blocked`. Winner selection, any-cell success, ranking, pooled causal readouts, and global TrustReport decisions are **not** supported by this framework.

---

## 14. TrustReport / CalibrationSignal / production boundary

Summary JSON invariants (all **false**):

- `trustreport_authorized`
- `calibration_signal_allowed`
- `production_decisioning_allowed`
- `live_api_authorized`
- `scheduler_authorized`
- `budget_optimization_allowed`

Harness blocks explicit authorization requests at evaluation time.

---

## 15. What this enables next

- `SCM_PLACEBO_GOVERNED_SEMANTICS_001` — wire SCM estimator statistics into treated-set placebo scoring with governed semantics
- Method-specific randomization inference validation once estimator paths supply statistics

---

## 16. Known limitations

- No SCM, TBRRidge, AugSynth, or DID estimator integration
- No production p-values or confidence intervals
- Empirical tail fraction is diagnostic/framework-only
- Does not resolve multicell multiplicity or shared-control dependence
- Sampled pseudo-assignments when combination space exceeds `max_assignments`

---

## 17. Governance verdict

`multitreated_treated_set_placebo_framework_defined_no_inference_authorization`

---

## 18. Residual Issues and Handoff

### Resolved in this artifact

- Multi-treated treated-set placebo contract defined and tested
- `INV-MULTITREATED-DESIGN-AWARE-PLACEBO-001` disposition: `TREATED_SET_PLACEBO_FRAMEWORK_DEFINED_PENDING_METHOD_SPECIFIC_VALIDATION`

### Deferred (unchanged)

- `INV-MULTICELL-MULTIPLICITY-CALIBRATION-001`
- `INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001`

### Next artifact

`SCM_PLACEBO_GOVERNED_SEMANTICS_001`

Regenerate:

```bash
poetry run python -m panel_exp.validation.multitreated_treated_set_placebo_framework_001 --overwrite
```
