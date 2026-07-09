# TBRRIDGE_REGIME_SENSITIVITY_PLAN_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_REGIME_SENSITIVITY_PLAN_001` |
| **Artifact type** | `tbrridge_regime_sensitivity_plan` |
| **Status** | `completed` |
| **Scope** | `tbrridge_regime_sensitivity_planned_no_sensitivity_computation_or_authorization` |
| **Base commit** | `b45657a` (Add TBRRidge positive-control recovery audit) |
| **Final verdict** | `tbrridge_regime_sensitivity_planned_no_sensitivity_computation_or_authorization` |

**Depends on:** `TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001` · `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` · `TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001` · `TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` · `TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` · `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001`

**Positive plan flags:** `tbrridge_regime_sensitivity_plan_defined` · `sensitivity_evidence_inventory_defined` · `coordinated_regime_matrix_defined` · `crossed_regime_testing_plan_defined` · `sensitivity_artifact_sequence_defined` · `runtime_packet_integration_defined` · `blocker_criteria_defined`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001.md`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001_REPORT.md`
- `panel_exp/validation/tbrridge_method_promotion_review_runtime_001.py`
- `panel_exp/validation/tbrridge_method_promotion_review_contract_001.py`
- `docs/track_d/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001_REPORT.md`

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
| **Regime sensitivity evidence** | Not generated |

TBRRidge KFold behavior under donor-pool, regularization, outlier, fold-geometry, sparse-metric, high-noise, seasonality, weak-preperiod-fit, and metric-scale regimes is **unplanned as a coordinated matrix** for method-promotion evidence. This plan defines the coordination layer only.

---

## 4. Relationship to promotion evidence battery plan

`TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` lists **regime sensitivity** as evidence component #5 (`regime_sensitivity_report`), P0 blocking, depending on positive-control recovery audit completion. Components #6–#14 are separate sensitivity artifacts (donor-pool, regularization, outlier, fold-geometry, etc.).

This plan is artifact #5 in the ordered battery sequence. It coordinates the remaining sensitivity lane before those separate audits are implemented. It does **not** run simulations or compute sensitivity metrics.

---

## 5. Relationship to positive-control recovery audit

`TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001` defined known-effect recovery evaluation under injected positive-control worlds.

Regime sensitivity plan extends recovery characterization across **stress regimes**:

1. **Positive-control recovery audit** — magnitude recovery under known lift in baseline-compatible worlds
2. **Regime sensitivity plan** — how recovery, directional behavior, and false-positive rates vary across donor-pool, noise, fold, and geometry regimes

Recovery stability by regime is a planned diagnostic (`recovery_stability_by_regime`), not a validated robustness claim.

---

## 6. Relationship to directional-error and null-control audits

| Prior audit | Regime sensitivity plan extension |
|-------------|-----------------------------------|
| **Null-control false-positive audit** | `false_positive_stability_by_regime` — FPR variation across regimes |
| **Directional-error audit** | `directional_stability_by_regime` — wrong-sign rate variation across regimes |
| **Positive-control recovery audit** | `recovery_stability_by_regime` — recovery variation across regimes |

Each prior battery metric must be re-evaluated under regime-tagged fixtures where relevant. Regime sensitivity does not subsume or replace prior audits.

---

## 7. Regime sensitivity purpose and claim boundary

**Purpose:** Define the coordinated regime matrix, crossed-regime testing plan, ordered sensitivity artifact sequence, diagnostic metrics, and runtime packet integration for TBRRidge KFold before method-promotion review can treat regime sensitivity evidence as non-blocking.

**Question answered (future):** Is TBRRidge KFold diagnostic behavior stable and characterized across declared regime families, or are regime-specific failures documented with blocker/restriction mapping?

**Claim boundary:** Regime sensitivity plans and diagnostics are **review-only stress planning**. They do not authorize validated regime robustness, production-ready sensitivity behavior, significance support, or method promotion.

---

## 8. Remaining sensitivity evidence inventory

| # | Evidence component | Report key | Priority | Status |
|---|-------------------|------------|----------|--------|
| 5 | Regime sensitivity (this plan) | `regime_sensitivity_report` | P0 | Plan defined; evidence not generated |
| 6 | Donor-pool sensitivity | `donor_pool_sensitivity_report` | P1 | Not started |
| 7 | Regularization sensitivity | `regularization_sensitivity_report` | P1 | Not started |
| 8 | Outlier sensitivity | `outlier_sensitivity_report` | P1 | Not started |
| 9 | Fold-geometry sensitivity | `fold_geometry_sensitivity_report` | P0 | Not started |
| 10 | Sparse/high-noise metric sensitivity | (sub-reports) | P1 | Not started |
| 11 | Seasonality / weak-preperiod-fit | (sub-reports) | P1 | Not started |
| 12 | Metric-scale sensitivity | (sub-reports) | P1 | Not started |
| 13 | Aggregate/pooled geometry blocker | `aggregate_pooled_geometry_blocker_report` | P0 | Not started |

**Plan decision:** This artifact inventories and sequences the remaining lane; individual audits implement per-family requirements.

**Regime families covered by this plan:**

1. donor-pool size and quality
2. donor-pool shift / instability
3. regularization strength
4. outlier contamination
5. fold geometry
6. sparse metrics
7. high-noise metrics
8. seasonal structure
9. weak pre-period fit
10. metric scale / variance regime
11. treatment timing shape
12. heterogeneous market response
13. delayed / decaying effects
14. low sample size
15. aggregate / pooled geometry stress

---

## 9. Coordinated regime matrix

Axes and levels (defined, not generated):

| Axis | Levels | Regime family |
|------|--------|---------------|
| `donor_pool_size` | small / medium / large | Donor-pool size and quality |
| `donor_pool_quality` | strong / mixed / weak | Donor-pool size and quality |
| `donor_pool_shift` | stable / moderate_shift / severe_shift | Donor-pool shift / instability |
| `regularization_strength` | low / medium / high | Regularization strength |
| `outlier_contamination` | none / moderate / severe | Outlier contamination |
| `fold_geometry` | stable / imbalanced / sparse / leave-region-out | Fold geometry |
| `metric_density` | dense / sparse / zero-inflated | Sparse metrics |
| `noise_regime` | low / medium / high | High-noise metrics |
| `seasonality` | none / aligned / misaligned | Seasonal structure |
| `preperiod_fit` | strong / mixed / weak | Weak pre-period fit |
| `metric_scale` | normalized / skewed / heavy-tailed | Metric scale / variance regime |
| `effect_shape` | immediate / delayed / decaying / heterogeneous | Treatment timing shape; heterogeneous market response |
| `sample_size` | low / medium / high | Low sample size |
| `aggregation_geometry` | unit-level / pooled / aggregate-stress | Aggregate / pooled geometry stress |

**Crossing policy:** See section 11. Full factorial crossing is prohibited; governed sparse crossing only.

---

## 10. Fixture design principles

1. **Lineage required** — Every fixture has `lineage_provenance_manifest` entry with seed, hash, and regime tags
2. **Battery overlay** — Each fixture tags applicable battery: null-control, directional-error, positive-control recovery
3. **Bounded scope** — Maximum 3 levels per axis in any single artifact; crossed combinations capped at 27 cells per artifact
4. **Default-regime anchor** — Each artifact includes one default/easy regime cell for comparison
5. **Diagnostic-only outputs** — No significance, power, or CI claims from fixture results
6. **Leakage cross-check** — Fold-geometry fixtures must cross-check `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001` blocked geometries
7. **Estimand consistency** — Metric scale and aggregation geometry must declare estimand alignment

---

## 11. Crossed-regime testing plan

**Tier 1 — Single-axis sweeps (per sensitivity artifact):** Vary one axis at default levels for all others. Example: donor-pool size sweep at medium noise, stable fold, strong preperiod fit.

**Tier 2 — Paired crosses (regime sensitivity report):** Pre-declared high-risk pairs only:

| Pair | Rationale |
|------|-----------|
| weak `preperiod_fit` × high `noise_regime` | False-confidence risk |
| small `donor_pool_size` × severe `outlier_contamination` | Donor fragility |
| imbalanced `fold_geometry` × sparse `metric_density` | Geometry instability |
| low `regularization_strength` × high `noise_regime` | Overfitting risk |
| pooled `aggregation_geometry` × heterogeneous `effect_shape` | Aggregate bias risk |

**Tier 3 — Blocked:** Full factorial or unbounded multi-axis crosses. Artifacts must document `crossed_regime_failure_rate_diagnostic` only for Tier 1 and Tier 2 cells.

---

## 12. Ordered sensitivity artifact sequence

| Order | Artifact | Report key | Depends on |
|-------|----------|------------|------------|
| 1 | `TBRRIDGE_DONOR_POOL_SENSITIVITY_AUDIT_001` | `donor_pool_sensitivity_report` | This plan |
| 2 | `TBRRIDGE_REGULARIZATION_SENSITIVITY_AUDIT_001` | `regularization_sensitivity_report` | Donor-pool audit |
| 3 | `TBRRIDGE_OUTLIER_SENSITIVITY_AUDIT_001` | `outlier_sensitivity_report` | Regularization audit |
| 4 | `TBRRIDGE_FOLD_GEOMETRY_SENSITIVITY_AUDIT_001` | `fold_geometry_sensitivity_report` | Outlier audit |
| 5 | `TBRRIDGE_SPARSE_HIGH_NOISE_METRIC_SENSITIVITY_AUDIT_001` | (sparse + high-noise sub-reports) | Fold-geometry audit |
| 6 | `TBRRIDGE_SEASONALITY_PREPERIOD_FIT_SENSITIVITY_AUDIT_001` | (seasonality + preperiod sub-reports) | Sparse/high-noise audit |
| 7 | `TBRRIDGE_METRIC_SCALE_SENSITIVITY_AUDIT_001` | (metric-scale sub-report) | Seasonality/preperiod audit |
| 8 | `TBRRIDGE_AGGREGATE_POOLED_GEOMETRY_BLOCKER_AUDIT_001` | `aggregate_pooled_geometry_blocker_report` | Metric-scale audit |

**Primary next artifact:** `TBRRIDGE_DONOR_POOL_SENSITIVITY_AUDIT_001`

---

## 13. Diagnostic metrics to be reported later

Metrics to be **defined and reported** by future evidence artifacts (not computed by this plan):

| Metric | Definition (diagnostic) |
|--------|---------------------------|
| `regime_sensitivity_summary_diagnostic` | Aggregate per-regime instability summary |
| `donor_pool_sensitivity_diagnostic` | Diagnostic instability across donor-pool axes |
| `regularization_sensitivity_diagnostic` | Diagnostic instability across ridge alpha |
| `outlier_sensitivity_diagnostic` | Diagnostic distortion under outlier contamination |
| `fold_geometry_sensitivity_diagnostic` | Diagnostic instability across fold layouts |
| `sparse_metric_sensitivity_diagnostic` | Diagnostic behavior under sparse metrics |
| `high_noise_sensitivity_diagnostic` | Diagnostic behavior under high noise |
| `seasonality_sensitivity_diagnostic` | Diagnostic behavior under seasonal structure |
| `weak_preperiod_fit_sensitivity_diagnostic` | Diagnostic behavior under weak pre-fit |
| `metric_scale_sensitivity_diagnostic` | Diagnostic behavior across metric scales |
| `crossed_regime_failure_rate_diagnostic` | Failure rate on Tier 2 crossed cells |
| `regime_specific_blocker_rate_diagnostic` | Fraction of regimes triggering blockers |
| `recovery_stability_by_regime` | Recovery metric variation by regime tag |
| `directional_stability_by_regime` | Directional-error variation by regime tag |
| `false_positive_stability_by_regime` | False-positive rate variation by regime tag |

All metrics are **diagnostic-only** and must not be labeled as validated robustness.

---

## 14. Acceptance criteria by regime family

| Regime family | Acceptance (future evidence) |
|---------------|------------------------------|
| Donor-pool size/quality/shift | All size and quality levels characterized; shift instability flagged |
| Regularization strength | Low/medium/high alpha grid evaluated |
| Outlier contamination | None/moderate/severe scenarios evaluated |
| Fold geometry | Stable/imbalanced/sparse/leave-region-out evaluated; leakage-blocked remain blocked |
| Sparse/high-noise metrics | Dense/sparse/zero-inflated and low/medium/high noise covered |
| Seasonality / weak preperiod | None/aligned/misaligned seasonality; strong/mixed/weak pre-fit covered |
| Metric scale | Normalized/skewed/heavy-tailed scales covered |
| Effect shape / heterogeneity | Immediate/delayed/decaying/heterogeneous shapes covered |
| Low sample size | Low-N regimes documented as diagnostic restrictions |
| Aggregate/pooled geometry | Pooled paths validated or blocked with explicit rationale |

**Global acceptance:** Sensitivity artifacts cover null-control, directional-error, and positive-control scenarios where relevant; each distinguishes diagnostic instability from claim authorization; crossed-regime combinations stay bounded; blocker rules map to promotion review runtime.

---

## 15. Blocker criteria for future promotion review

Promotion review blocks or restricts when:

- missing regime sensitivity report
- sensitivity only tested in easy/default regimes
- donor-pool instability uncharacterized
- regularization sensitivity uncharacterized
- outlier sensitivity uncharacterized
- fold geometry sensitivity uncharacterized
- sparse/high-noise metrics uncharacterized
- weak pre-period fit behavior uncharacterized
- metric scale sensitivity uncharacterized
- aggregate/pooled behavior used without validation
- metric/estimand mismatch
- claim authorization boundary missing

Risk flags: `REGIME_SENSITIVITY_INCOMPLETE`, `DONOR_POOL_SENSITIVITY_INCOMPLETE`, `REGULARIZATION_SENSITIVITY_INCOMPLETE`, `OUTLIER_SENSITIVITY_INCOMPLETE`, `FOLD_GEOMETRY_SENSITIVITY_INCOMPLETE`

Runtime block: `METHOD_PROMOTION_REVIEW_BLOCKED_BY_REGIME_SENSITIVITY` when `regime_sensitivity_report` missing or incomplete.

---

## 16. Runtime packet integration plan

Future artifacts populate reports consumed by `generate_tbrridge_method_promotion_review()`:

**`regime_sensitivity_report` (umbrella):**

```json
{
  "regime_axes": ["donor_pool_size", "noise_regime", "fold_geometry"],
  "per_regime_status": {},
  "regime_sensitivity_summary_diagnostic": null,
  "crossed_regime_failure_rate_diagnostic": null,
  "sensitivity_incomplete": false,
  "diagnostic_only": true,
  "audit_source": "TBRRIDGE_REGIME_SENSITIVITY_PLAN_001"
}
```

**Per-family reports:** `donor_pool_sensitivity_report`, `regularization_sensitivity_report`, `outlier_sensitivity_report`, `fold_geometry_sensitivity_report`, `aggregate_pooled_geometry_blocker_report`

**Integration rules:**

1. `detect_tbrridge_method_promotion_risks()` flags incomplete sensitivity reports per contract
2. `evaluate_method_promotion_review()` blocks on missing `regime_sensitivity_report`; restricts on incomplete P1 family reports
3. Metric values remain null until future sensitivity artifacts populate them
4. This plan defines schema and sequencing only

---

## 17. Governance registry integration plan

1. Add `INV-TBRRIDGE-REGIME-SENSITIVITY-PLAN-001` investigation (RESOLVED upon plan completion)
2. Add `TBRRIDGE-REGIME-SENSITIVITY-PLAN-001` roadmap lane binding
3. Set lane `next_artifact` to `TBRRIDGE_DONOR_POOL_SENSITIVITY_AUDIT_001`
4. Update `ROADMAP_V4.md`, `METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`, `MIP_AUDIT_REGISTRY.md`
5. Preserve TBRRidge RANK_0/BLOCKED/STAGE_2_DIAGNOSTIC_ONLY posture in all registry entries

---

## 18. Allowed language

- **regime sensitivity plan** — Coordinated regime matrix and artifact sequencing
- **diagnostic sensitivity matrix** — Axis/level definition for future stress testing
- **review-only stress plan** — Planning artifact without evidence generation
- **sensitivity evidence requirements** — Per-family fixture and metric requirements
- **future promotion-review input** — Reports destined for promotion review runtime
- **blocker mapping** — Regime-specific blocker and restriction rules

---

## 19. Prohibited language

- **validated regime robustness**
- **approved sensitivity behavior**
- **production-ready sensitivity**
- **confidence interval support**
- **p-value/significance support**
- **causal lift claim**
- **ROI claim**
- **method promotion evidence complete**
- **catalog unblock support**

---

## 20. Stop/go criteria

### Go (plan requirements adopted — does not generate evidence)

Proceed to `TBRRIDGE_DONOR_POOL_SENSITIVITY_AUDIT_001` when:

1. Coordinated regime matrix documented
2. Crossed-regime testing plan bounded
3. Sensitivity artifact sequence ordered
4. Diagnostic metrics defined
5. Blocker criteria and runtime packet schema defined
6. Prior battery compatibility confirmed

### Stop

Stop when:

1. Sensitivity evidence interpreted as validated robustness or production approval
2. Diagnostic intervals treated as confidence intervals for sensitivity claims
3. Crossed-regime scope explodes into unbounded factorial fixtures
4. Easy/default-only testing treated as sufficient sensitivity evidence
5. Aggregate/pooled paths authorized without geometry validation
6. Sensitivity metrics computed without governed fixture lineage (future artifact violation)
7. Attempt to mark sensitivity evidence as promotion-complete

---

## 21. Authorization boundary

**Allowed:** `tbrridge_regime_sensitivity_plan_defined`, `sensitivity_evidence_inventory_defined`, `coordinated_regime_matrix_defined`, `crossed_regime_testing_plan_defined`, `sensitivity_artifact_sequence_defined`, `runtime_packet_integration_defined`, `blocker_criteria_defined`

**Forbidden:** `regime_sensitivity_evidence_generated`, `sensitivity_metrics_computed`, `simulations_implemented`, `robustness_validated`, `sensitivity_behavior_approved`, all inference/estimator/kfold/placebo implementation flags, all promotion/production/uncertainty/CI/significance/lift/ROI/MMM/LLM flags

TBRRidge remains **RANK_0**, **BLOCKED**, **STAGE_2_DIAGNOSTIC_ONLY**.

---

## 22. Validation results

| Check | Result |
|-------|--------|
| Plan document complete | Pass |
| Summary JSON valid | Pass |
| Governance tests | Pass |

---

## 23. Known limitations

- **Planning only** — No regime fixtures generated; no sensitivity metrics computed
- **Separate artifacts deferred** — Eight downstream sensitivity audits implement per-family detail
- **Crossing bounded** — Tier 2 pairs only; full factorial explicitly blocked
- **D5 regime partitions referenced** — Historical regime tags inform planning; not replayed
- **Metric values null in schema** — Packet templates use null placeholders until evidence generated

---

## 24. Recommended next artifacts

| Role | Artifact |
|------|----------|
| **Primary** | `TBRRIDGE_DONOR_POOL_SENSITIVITY_AUDIT_001` |
| **Alternative** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` |
| **Deferred** | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` |
| **Sensitivity sequence** | Regularization → Outlier → Fold-geometry → Sparse/high-noise → Seasonality/preperiod → Metric-scale → Aggregate/pooled geometry blocker |
