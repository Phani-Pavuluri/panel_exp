# MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001` |
| **Artifact type** | `multicell_experiment_family_contrast_contract` |
| **Status** | `completed` |
| **Scope** | `multicell_experiment_family_and_contrast_contract_defined_no_runtime_or_inference` |
| **Base commit** | `90bfccf` (Define sophisticated method evidence ladder) |
| **Final verdict** | `multicell_experiment_family_and_contrast_contract_defined_no_runtime_or_inference` |

**Depends on:** `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001` · `METHOD_PROMOTION_CANDIDATE_AUDIT_001` · `METHOD_PROMOTION_REVIEW_RUNTIME_001` · `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001`

---

## 2. Source files inspected

- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`
- `docs/track_d/METHOD_PROMOTION_CANDIDATE_AUDIT_001.md`
- `docs/MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001.md`
- `docs/track_d/MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001_REPORT.md`
- `panel_exp/validation/multicell_decision_policy_contract_001.py`
- `panel_exp/validation/stratified_pooled_estimand_contract_001.py`
- `panel_exp/validation/claim_authorization_contract_001.py`
- `panel_exp/validation/production_compatibility_promotion_review_contract_001.py`
- `docs/ROADMAP_V4.md` · `docs/governance/OPEN_INVESTIGATIONS_001.json`

---

## 3. Problem statement

`SOPHISTICATED_METHOD_EVIDENCE_LADDER_001` identified multi-cell/pooled semantics as the largest shared blocker across sophisticated methods. Before multiplicity corrections or covariance computation, the platform must distinguish **when** those requirements apply.

Experiments on different platforms/channels displayed on the same dashboard are not automatically one statistical family. Applying shared multiplicity or covariance to unrelated experiments would over-restrict standalone readouts; omitting them within a shared-control multi-arm test would under-restrict winner claims.

This contract defines experiment-family applicability and contrast taxonomy **before** runtime enforcement.

---

## 4. Why independent experiments are exempt from shared multiplicity

**Core rule:** Multiplicity and shared covariance apply to planned or implied comparisons **within the same experiment/decision family**, not to unrelated experiments that merely appear in the same dashboard.

For `INDEPENDENT_EXPERIMENTS`:

- Each experiment answers a separate business question with disjoint assignment geometry.
- Standalone arm readouts do not imply cross-arm comparisons.
- `multiplicity_required=false` and `shared_covariance_required=false` for standalone surfaces.
- Cross-platform/channel **winner**, **global**, or **pooled** claims are blocked unless reclassified as `PORTFOLIO_DECISION_FAMILY` with comparable estimands and explicit decision-family evidence.

---

## 5. Experiment family taxonomy

| Family | Meaning |
|--------|---------|
| `INDEPENDENT_EXPERIMENTS` | Unrelated experiments; no shared comparison family |
| `RELATED_PARALLEL_ARMS` | Same-channel parallel arms with planned/implied comparisons |
| `SHARED_CONTROL_MULTI_ARM` | Multiple arms share control/donor pool |
| `DOSE_RESPONSE_FAMILY` | Ordered dose levels within one experiment |
| `PORTFOLIO_DECISION_FAMILY` | Cross-source decision synthesis (budget/ranking) |
| `POOLED_AGGREGATE_FAMILY` | Explicit pooled/global estimand over components |
| `UNKNOWN_FAMILY_REQUIRES_REVIEW` | Fail closed; block comparative/pooled/winner claims |

### Family identity fields

`experiment_family_id` · `decision_family_id` · `experiment_ids` · `arm_ids` · `platform` · `channel` · `campaign_objective` · `shared_budget_pool` · `shared_control_group` · `overlapping_units` · `shared_time_window` · `shared_metric` · `common_estimand` · `planned_cross_arm_comparisons` · `implied_comparison_surface` · `pooling_requested` · `global_summary_requested`

---

## 6. Contrast taxonomy

| Contrast | Use |
|----------|-----|
| `ARM_VS_CONTROL` | Single arm against shared or arm-specific control |
| `ARM_VS_ARM` | Direct arm comparison |
| `DOSE_LINEAR_TREND` | Ordered dose linear trend |
| `DOSE_NONLINEAR_RESPONSE` | Nonlinear dose-response shape |
| `GLOBAL_ANY_EFFECT` | Any-arm or family-wide effect claim |
| `POOLED_AVERAGE_EFFECT` | Weighted aggregate across components |
| `CELL_SPECIFIC_EFFECT` | Per-cell marginal effect |
| `PORTFOLIO_RANKING` | Cross-experiment ranking |
| `BUDGET_REALLOCATION_COMPARISON` | Budget shift recommendation |

---

## 7. Applicability rules

| Family | Multiplicity | Shared covariance | Standalone readout | Winner allowed |
|--------|--------------|-------------------|--------------------|----------------|
| INDEPENDENT_EXPERIMENTS | No | No | Yes | No |
| RELATED_PARALLEL_ARMS | Yes (comparisons) | No | Yes | No |
| SHARED_CONTROL_MULTI_ARM | Yes | Yes | Yes | No |
| DOSE_RESPONSE_FAMILY | Yes | No | Yes | No |
| PORTFOLIO_DECISION_FAMILY | Yes | No | Yes | No (without synthesis evidence) |
| POOLED_AGGREGATE_FAMILY | Yes | Yes | No | No |
| UNKNOWN_FAMILY_REQUIRES_REVIEW | Yes | Yes | No | No |

---

## 8. Evidence requirements by surface

| Surface | Required evidence |
|---------|-------------------|
| Standalone arm readout | arm identity, estimand, execution/readout evidence |
| Arm comparison | contrast, shared family, comparable metrics, multiplicity policy |
| Shared-control comparison | shared-control covariance semantics or conservative fallback |
| Dose response | dose ordering, units, planned contrasts, monotonic/nonlinear policy |
| Pooled/global lift | pooling weights, heterogeneity diagnostics, covariance/variance semantics, estimand alignment |
| Winner/ranking | comparable estimands, governed uncertainty, multiplicity policy |
| Budget reallocation/scale | production recommendation authorization |

---

## 9. Allowed / conditional / prohibited surfaces

**Always allowed (with base evidence):** `STANDALONE_ARM_READOUT` · `CELL_SPECIFIC_POINT_ESTIMATE` · `DESCRIPTIVE_COMPARISON_REVIEW_ONLY` · `DIAGNOSTIC_ONLY` · `RESEARCH_OR_REVIEW_ONLY`

**Conditional (family + evidence):** `ARM_COMPARISON` · `DOSE_RESPONSE_SUMMARY` · `POOLED_EFFECT_SUMMARY` · `GLOBAL_EFFECT_SUMMARY` · `PORTFOLIO_RANKING_REVIEW`

**Prohibited unless separately governed:** `WINNER_CLAIM` · `SCALE_BUDGET_CLAIM` · `PRODUCTION_RECOMMENDATION` · `ROI_COMPARISON_CLAIM` · `CAUSAL_SUPERIORITY_CLAIM` · `STATISTICAL_SIGNIFICANCE_COMPARISON` · `CONFIDENCE_INTERVAL_COMPARISON`

---

## 10. Failure packet semantics

Fields: `failure_code` · `failure_reason` · `family_type` · `blocked_surface` · `missing_evidence` · `required_remediation` · `retry_category`

Codes: `UNKNOWN_EXPERIMENT_FAMILY` · `MISSING_CONTRAST_DEFINITION` · `MISSING_MULTIPLICITY_POLICY` · `MISSING_SHARED_CONTROL_COVARIANCE_SEMANTICS` · `MISSING_DOSE_RESPONSE_SEMANTICS` · `MISSING_POOLING_WEIGHTS` · `MISSING_HETEROGENEITY_DIAGNOSTICS` · `INCOMPARABLE_ESTIMANDS` · `COMPARATIVE_SURFACE_NOT_AUTHORIZED` · `WINNER_CLAIM_BLOCKED` · `BUDGET_SCALE_CLAIM_BLOCKED`

---

## 11. Future runtime acceptance criteria

- Classifies independent experiments without forcing shared multiplicity
- Blocks cross-platform winner claim without comparable decision-family evidence
- Requires contrast definitions for related arms
- Requires multiplicity policy for arm comparisons
- Requires covariance semantics for shared-control multi-arm comparisons
- Requires dose semantics for dose-response summaries
- Blocks pooled/global lift without pooling + heterogeneity + covariance evidence
- Blocks winner/scale-budget claims without governed authorization
- Emits failure packet for unknown family
- Preserves standalone readout eligibility for independent experiments
- All forbidden computation/authorization flags remain false

---

## 12. Relationship to sophisticated method evidence ladder

This contract is the refined first step of `MULTICELL_CONTRAST_MULTIPLICITY_EVIDENCE_CONTRACT_001` recommended by `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001`. It unblocks STAGE_0→STAGE_1 advancement for:

- TBR aggregate/pooled paths
- multi-cell pooled/global paths

Without implementing multiplicity correction or covariance computation.

---

## 13. Relationship to method promotion / production compatibility

- Method promotion review may reference family/contrast gaps as blockers.
- Production compatibility review remains deferred (`PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`).
- This contract does not promote methods or unblock catalog entries.

---

## 14. Authorization boundary

| Flag | Value |
|------|-------|
| `runtime_implemented` | false |
| `multiplicity_correction_computed` | false |
| `covariance_computed` | false |
| `winner_claim_authorized` | false |
| `production_recommendation_authorized` | false |
| `method_promoted` | false |
| `production_catalog_unblocked` | false |
| `experiment_family_taxonomy_defined` | true |
| `independent_experiment_exemption_defined` | true |

---

## 15. Validation results

- Contract module validates taxonomies and surface gate scenarios
- Governance tests assert registry reference and forbidden flags
- Safety grep: no forbidden `true` flags in contract artifacts

---

## 16. Known limitations

- Contract-only; no runtime binding to readout plan or claim authorization yet.
- Does not replace `MULTICELL-CELL-RELATIONSHIP-AND-DECISION-POLICY-CONTRACT-001` for within-design cell relationships.
- Portfolio/budget semantics require human governance beyond this contract.

---

## 17. Recommended next artifact

**`MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001`**

**Alternative:** `TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001`
