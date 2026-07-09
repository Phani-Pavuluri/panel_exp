# TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001` |
| **Artifact type** | `tbrridge_metric_estimand_alignment_audit` |
| **Status** | `completed` |
| **Scope** | `tbrridge_metric_estimand_alignment_audited_no_estimand_approval_or_metric_authorization` |
| **Base commit** | `db97671` (Add TBRRidge sensitivity evidence audit bundle) |
| **Final verdict** | `tbrridge_metric_estimand_alignment_audited_no_estimand_approval_or_metric_authorization` |

**Depends on:** `TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001` · `TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001` · `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` · `TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001` · `TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` · `TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` · `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001`

**Positive audit flags:** `tbrridge_metric_estimand_alignment_audit_completed` · `metric_estimand_gap_documented` · `alignment_dimensions_defined` · `transformation_requirements_defined` · `diagnostic_checks_defined` · `blocker_criteria_defined` · `runtime_packet_integration_defined`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001.md`
- `docs/track_d/archives/TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001_summary.json`
- `docs/track_d/TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001.md`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001_REPORT.md`
- `panel_exp/validation/tbrridge_method_promotion_review_runtime_001.py`
- `panel_exp/validation/tbrridge_method_promotion_review_contract_001.py`
- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`

---

## 3. Current TBRRidge posture

| Layer | Posture |
|-------|---------|
| **Catalog rank** | `RANK_0` |
| **Catalog status** | `BLOCKED` |
| **Readiness stage** | `STAGE_2_DIAGNOSTIC_ONLY` |
| **Instrument** | `TBRRidge_Kfold` |
| **Method promotion** | Not promoted |
| **Catalog unblock** | Not unblocked |
| **Production readiness** | Not production-ready |
| **Uncertainty approval** | Not uncertainty-approved |
| **Metric/estimand alignment evidence** | Not generated |

D5-TRUST-TBRRIDGE-KFOLD-001 documented level-bias and ATT vs level-percent divergence. Metric/estimand alignment for method-promotion evidence is **uncharacterized**. This audit defines alignment requirements only.

---

## 4. Relationship to promotion evidence battery plan

`TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` lists **metric/estimand alignment** as evidence component #10 (`metric_estimand_alignment_report`), P0 blocking.

This audit defines how TBRRidge KFold outputs, metric transformations, modeled targets, time windows, aggregation levels, and causal/business estimands must align before promotion review can treat alignment evidence as non-blocking. It does **not** generate alignment evidence or approve estimands.

---

## 5. Relationship to sensitivity evidence audit bundle

`TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001` defined `metric_scale_sensitivity` and `aggregate_pooled_geometry_blocker` requirements.

Metric/estimand alignment audit **closes the semantic gap**:

1. **Sensitivity bundle** — diagnostic instability across metric scales and aggregation geometries
2. **Metric/estimand alignment audit** — explicit mapping between modeled target, reporting scale, and declared causal/business estimand

Scale sensitivity without estimand mapping risks answering the wrong question.

---

## 6. Relationship to interval/null/directional/positive-control audits

| Prior audit | Alignment extension |
|-------------|---------------------|
| **Interval semantics** | Diagnostic bands are not business-scale CIs; inverse transform rules required |
| **Null-control false-positive** | FPR defined on declared estimand, not silent model scale |
| **Directional-error** | Sign claims require estimand-consistent contrast |
| **Positive-control recovery** | Recovery ratios require ground-truth estimand match |

All prior battery metrics must declare which estimand they characterize. Alignment audit does not replace prior audits.

---

## 7. Metric/estimand alignment purpose and claim boundary

**Purpose:** Define required alignment evidence and blockers between TBRRidge KFold model outputs and governed causal/business estimands before method-promotion review.

**Core principle:** A method can be stable and still answer the wrong question.

**Question answered (future):** Do TBRRidge KFold diagnostic outputs map coherently to the declared causal and business estimand?

**Claim boundary:** Alignment diagnostics are **review-only mapping evidence**. They do not authorize estimand approval, metric compatibility, business lift, ROI, method promotion, or production readout claims.

---

## 8. Alignment evidence gap

| Gap | Current state | Severity |
|-----|---------------|----------|
| Causal/business estimand declaration | Not attached to promotion packets | P0 |
| Modeled vs reporting scale distinction | D5 level-bias referenced; not formalized | P0 |
| Transformation/inverse-transform rules | Not documented under contract | P0 |
| Treatment contrast alignment | Not characterized | P0 |
| Time-window alignment | Pre/post windows not tied to estimand | P0 |
| Geography/unit scope | Donor pool vs treatment unit scope not unified | P0 |
| Aggregation/weighting rules | Pooled paths blocked but bridge not documented | P0 |
| Denominator/missing-data/outlier policies | Not explicit in alignment packet | P0 |
| Promotion runtime integration | `metric_estimand_alignment_report` missing | P0 |

**Audit decision:** Requirements and packet schema defined; evidence generation deferred.

---

## 9. Required alignment dimensions

All future evidence packets must populate:

| Dimension | Description |
|-----------|-------------|
| `outcome_metric_name` | Governed KPI identifier |
| `outcome_metric_definition` | Plain-language outcome definition |
| `numerator_definition` | Numerator for rate/ratio metrics |
| `denominator_definition` | Denominator for rate/ratio metrics |
| `transformation_applied` | Raw, log, diff, normalized, rate, count, revenue, ratio |
| `modeled_target_scale` | Scale TBRRidge ridge model optimizes on |
| `reporting_scale` | Scale presented in diagnostic readout |
| `causal_estimand` | Declared causal quantity (e.g., ATT, incremental lift) |
| `business_estimand` | Business-facing quantity (if distinct) |
| `treatment_contrast` | Treated vs control definition |
| `exposure_definition` | Spend, impression, or policy exposure |
| `time_window` | Overall analysis window |
| `pre_period_window` | Pre-intervention fit window |
| `post_period_window` | Post-intervention evaluation window |
| `geography_unit` | Market, DMA, region, or custom geo unit |
| `donor_pool_scope` | Units eligible as donors |
| `treatment_unit_scope` | Units receiving treatment |
| `aggregation_level` | Unit-level, pooled, or aggregate |
| `weighting_scheme` | Equal, population, spend-weighted, etc. |
| `missing_data_policy` | Imputation, drop, or forward-fill rule |
| `outlier_policy` | Winsorize, cap, or exclude rule |
| `seasonality_adjustment_policy` | None, fixed effects, or explicit adjustment |
| `lag_or_carryover_policy` | Lag structure and carryover handling |

---

## 10. Metric transformation requirements

1. Document whether metric is **raw**, **log-transformed**, **differenced**, **normalized**, **rate-based**, **count-based**, **revenue-based**, or **ratio-based**
2. Document whether TBRRidge output is on **model scale** or **reporting scale**
3. Document whether **inverse transform** is valid and governed (with explicit formula and domain checks)
4. **Block** silent conversion from model-scale diagnostics to business-scale claims
5. **Block** lift/ROI interpretation unless estimand mapping is explicit and separately authorized
6. Crosswalk ATT vs level-percent panels required where both scales appear in D5 evidence

---

## 11. Time-window and aggregation requirements

**Time windows:**

- `pre_period_window` must cover sufficient pre-fit for ridge donor weight estimation
- `post_period_window` must match causal estimand horizon (immediate vs cumulative)
- Delayed/decaying effect shapes require estimand-consistent window tagging

**Aggregation:**

- Unit-level diagnostics are default authorized geometry
- Pooled/aggregate paths require explicit validation or remain blocked per sensitivity bundle
- `weighting_scheme` must be compatible with declared estimand (e.g., population-weighted ATT)

---

## 12. Geography/unit-level alignment requirements

- `geography_unit` must match treatment assignment granularity
- `donor_pool_scope` must not include treated units in donor set (leakage cross-check)
- `treatment_unit_scope` must be explicit and disjoint from donor pool where required
- Donor-pool shift sensitivity results must reference same geography_unit definition

---

## 13. Treatment contrast alignment requirements

- `treatment_contrast` must declare treated vs donor/synthetic control definition
- `exposure_definition` must align with business question (spend vs organic lift)
- Multi-treated geometries require contrast-per-unit or blocked aggregate paths
- Sign and recovery diagnostics must use estimand-consistent contrast direction

---

## 14. Outcome definition and denominator requirements

- `numerator_definition` and `denominator_definition` required for rate/ratio metrics
- `denominator_stability_diagnostic` (future) flags unstable denominators across windows
- Zero or near-zero denominators require explicit handling policy
- Revenue vs count vs rate metrics must not be conflated in recovery comparisons

---

## 15. Modeled target vs causal estimand requirements

| Layer | Requirement |
|-------|-------------|
| **Modeled target** | What TBRRidge KFold ridge optimizes (transformed outcome on donor-weighted counterfactual) |
| **Reporting target** | What diagnostic readout presents |
| **Causal estimand** | What causal question is being approximated |
| **Business estimand** | What business decision would use (if distinct) |

**Rule:** If modeled target ≠ reporting target, a **governed bridge** (transform + inverse + aggregation rules) must be documented. Absent bridge → `metric_estimand_mismatch` blocker.

---

## 16. Required future diagnostic checks

Checks to be **defined and reported** by future evidence artifacts (not computed by this audit):

| Check | Purpose |
|-------|---------|
| `metric_estimand_alignment_diagnostic` | Overall alignment pass/fail summary |
| `modeled_target_reporting_scale_alignment_diagnostic` | Model vs reporting scale consistency |
| `transformation_invertibility_diagnostic` | Inverse transform validity |
| `aggregation_consistency_diagnostic` | Aggregation rules match estimand |
| `denominator_stability_diagnostic` | Denominator stability across windows |
| `time_window_alignment_diagnostic` | Pre/post windows match estimand |
| `treatment_contrast_alignment_diagnostic` | Contrast definition consistency |
| `geography_unit_alignment_diagnostic` | Geo unit scope consistency |
| `donor_pool_scope_alignment_diagnostic` | Donor pool vs treatment scope |
| `missing_data_policy_alignment_diagnostic` | Missing-data handling documented |
| `outlier_policy_alignment_diagnostic` | Outlier policy documented |
| `lag_carryover_alignment_diagnostic` | Lag/carryover policy documented |

All checks are **diagnostic-only**.

---

## 17. Acceptance criteria for future evidence artifact

Future metric/estimand alignment evidence is acceptable when:

1. all required alignment dimensions are populated
2. modeled target and reporting target are explicitly distinguished
3. metric transformations and inverse-transform rules are documented
4. time windows and treatment contrast match the estimand
5. aggregation and weighting rules are compatible with the estimand
6. geography/unit scope is aligned with treatment assignment and donor pool
7. denominator, missing-data, and outlier policies are explicit
8. no lift/ROI/production claim is inferred from diagnostic output
9. evidence packet can populate `metric_estimand_alignment_report` in `generate_tbrridge_method_promotion_review()`

---

## 18. Blocker criteria for future promotion review

Promotion review blocks (`METHOD_PROMOTION_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH`) when:

- missing metric/estimand alignment report
- undefined causal or business estimand
- modeled target differs from reporting target without governed bridge
- transformation or inverse transformation unspecified
- treatment contrast mismatch
- time-window mismatch
- geography/unit mismatch
- aggregation or weighting mismatch
- denominator instability unaddressed
- missing-data or outlier policy unspecified
- lag/carryover policy unspecified
- metric-scale diagnostic interpreted as business lift
- ROI inferred without governed cost/revenue mapping
- claim authorization boundary missing

Risk flag: `METRIC_ESTIMAND_MISMATCH`

---

## 19. Runtime packet integration plan

Future `metric_estimand_alignment_report` for `generate_tbrridge_method_promotion_review()`:

```json
{
  "estimand_id": null,
  "alignment_dimensions_populated": 22,
  "metric_estimand_alignment_diagnostic": null,
  "modeled_target_reporting_scale_alignment_diagnostic": null,
  "metric_estimand_mismatch": false,
  "alignment_incomplete": false,
  "diagnostic_only": true,
  "audit_source": "TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001",
  "summary": {
    "audit_requirements_defined": true,
    "evidence_generated": false
  }
}
```

**Integration rules:**

1. `detect_tbrridge_method_promotion_risks()` flags `METRIC_ESTIMAND_MISMATCH` when `metric_estimand_mismatch` or `alignment_incomplete` is true
2. `evaluate_method_promotion_review()` blocks with `METHOD_PROMOTION_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH`
3. Metric values remain null until future evidence artifact populates them
4. This audit defines schema and requirements only

---

## 20. Allowed language

- **metric/estimand alignment audit**
- **modeled target diagnostic**
- **reporting-scale alignment requirement**
- **estimand mapping requirement**
- **diagnostic alignment evidence**
- **future promotion-review input**

---

## 21. Prohibited language

- **estimand approved**
- **metric compatibility authorized**
- **validated business lift**
- **ROI-ready output**
- **production-ready readout**
- **confidence interval support**
- **p-value/significance support**
- **method promotion evidence complete**
- **catalog unblock support**

---

## 22. Stop/go criteria

### Go (audit requirements adopted — does not generate evidence)

Proceed to `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` when:

1. Alignment dimensions documented
2. Transformation requirements documented
3. Diagnostic checks defined
4. Blocker criteria defined
5. Runtime packet schema defined
6. Prior battery compatibility confirmed

### Stop

Stop when:

1. Alignment evidence interpreted as estimand approval or metric compatibility authorization
2. Model-scale diagnostics silently converted to business lift claims
3. ROI inferred without governed cost/revenue mapping
4. Pooled/aggregate paths authorized without alignment bridge
5. Alignment metrics computed without governed dimension manifest (future artifact violation)

---

## 23. Authorization boundary

**Allowed:** `tbrridge_metric_estimand_alignment_audit_completed`, `metric_estimand_gap_documented`, `alignment_dimensions_defined`, `transformation_requirements_defined`, `diagnostic_checks_defined`, `blocker_criteria_defined`, `runtime_packet_integration_defined`

**Forbidden:** `metric_estimand_alignment_evidence_generated`, `metric_compatibility_authorized`, `estimand_approved`, `business_lift_authorized`, `roi_authorized`, `alignment_metrics_computed`, all inference/estimator/kfold/placebo flags, all promotion/production/uncertainty/CI/significance/lift/ROI/MMM/LLM flags

TBRRidge remains **RANK_0**, **BLOCKED**, **STAGE_2_DIAGNOSTIC_ONLY**.

---

## 24. Validation results

| Check | Result |
|-------|--------|
| Audit document complete | Pass |
| Summary JSON valid | Pass |
| Governance tests | Pass |

---

## 25. Known limitations

- **Requirements only** — No alignment fixtures replayed; no alignment metrics computed
- **D5 level-bias referenced** — Historical bias informs gap severity; not re-run
- **Sensitivity bundle separate** — Scale/aggregation instability remains in sensitivity bundle
- **Claim authorization deferred** — Claim-type boundaries are `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001`
- **Metric values null in schema** — Packet template uses null placeholders until evidence generated

---

## 26. Recommended next artifacts

| Role | Artifact |
|------|----------|
| **Primary** | `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` |
| **Alternative** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` |
| **Deferred** | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` |
| **Future evidence** | Metric/estimand alignment simulation/runtime artifact (not yet planned as separate ID) |
