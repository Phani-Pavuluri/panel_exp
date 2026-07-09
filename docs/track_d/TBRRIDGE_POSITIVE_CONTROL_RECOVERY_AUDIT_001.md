# TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001` |
| **Artifact type** | `tbrridge_positive_control_recovery_audit` |
| **Status** | `completed` |
| **Scope** | `tbrridge_positive_control_recovery_audited_no_recovery_computation_or_authorization` |
| **Base commit** | `495f599` (Add TBRRidge directional error audit) |
| **Final verdict** | `tbrridge_positive_control_recovery_audited_no_recovery_computation_or_authorization` |

**Depends on:** `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` · `TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001` · `TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` · `TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` · `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001`

**Positive audit flags:** `tbrridge_positive_control_recovery_audit_completed` · `positive_control_recovery_gap_documented` · `positive_control_fixture_requirements_defined` · `recovery_diagnostic_metrics_defined` · `directional_error_distinction_defined` · `blocker_criteria_defined` · `runtime_packet_integration_defined`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001.md`
- `docs/track_d/archives/TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001_summary.json`
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
- `docs/track_d/TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001.md`

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
| **Positive-control recovery evidence** | Not generated |

D5-TRUST-TBRRIDGE-KFOLD-001 documented partial point recovery under clean positive-lift worlds but recovery is **uncharacterized** across effect sizes, time shapes, and stress regimes for method-promotion evidence. This audit defines evaluation requirements only.

---

## 4. Relationship to promotion evidence battery plan

`TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` lists **positive-control recovery** as evidence component #4 (`positive_control_recovery_report`), P0 blocking, depending on directional-error audit completion.

This audit is artifact #4 in the ordered battery sequence. It defines injected-effect fixture families, recovery diagnostic metrics, acceptance/blocker criteria, and runtime packet shape. It does **not** run simulations or compute recovery rates.

---

## 5. Relationship to null-control false-positive audit

`TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001` defined null/no-effect false-positive evaluation under governed null worlds.

Positive-control recovery audit is **orthogonal**:

1. **Null-control audit** — any effect claim under no-effect worlds (false positive)
2. **Positive-control recovery audit** — magnitude recovery under known injected-effect worlds

A null-world pass does not imply recovery of known positive effects. Both reports are required independently.

---

## 6. Relationship to directional-error audit

`TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` defined wrong-sign evaluation under signed-effect worlds (positive when negative, negative when positive, near-zero instability).

Positive-control recovery builds on sign-correct worlds but addresses a **different failure mode**:

1. **Directional-error audit** — sign correctness under signed ground truth
2. **Positive-control recovery audit** — effect-size recovery (bias, ratio, under/over-recovery) when sign is correct or when magnitude is the primary question

Correct sign with severe under-recovery or over-recovery is a recovery failure, not a directional-error failure. Both must be characterized independently.

---

## 7. Relationship to interval semantics audit

`TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` established that KFold bands are **diagnostic uncertainty summaries**, not confidence intervals.

Positive-control recovery evaluation must:

1. Use **diagnostic recovery-claim** framing — point estimate vs injected ground truth
2. **Not** treat interval width or exclusion as power or significance evidence
3. **Not** treat near-MDE recovery as statistical power approval
4. Populate `positive_control_recovery_report` compatible with `interval_semantics_report`

---

## 8. Positive-control recovery purpose and claim boundary

**Purpose:** Define how TBRRidge KFold must be evaluated against known positive-control (and symmetry-reference negative) injected effects before method-promotion review can treat recovery evidence as non-blocking.

**Question answered (future):** When true effect is known and injected, does TBRRidge KFold recover effect magnitude within declared diagnostic tolerances across governed fixture families?

**Claim boundary:** Recovery diagnostics are **review-only falsification evidence**. They do not authorize validated recovery rates, statistical power approval, significance support, confidence-interval coverage approval, causal lift claims, method promotion, or production readout claims.

---

## 9. Positive-control recovery evidence gap

| Gap | Current state | Severity |
|-----|---------------|----------|
| Injected-effect worlds | D5 positive-lift worlds referenced; not attached to promotion packets | P0 |
| Recovery rate characterization | Not computed under contract | P0 |
| Under-recovery / over-recovery separation | Not characterized | P0 |
| Near-MDE / below-MDE behavior | Not documented as diagnostic-only | P0 |
| Delayed/decaying effect shapes | Not characterized | P0 |
| Fold/donor/regularization recovery stability | Not characterized | P0 |
| Metric-scale recovery behavior | Level-percent vs ATT recovery not separated | P0 |
| Promotion runtime integration | `positive_control_recovery_report` missing from supplied evidence | P0 |

**Audit decision:** Requirements and packet schema are defined; evidence generation is deferred to future simulation/runtime artifacts.

---

## 10. Required positive-control fixture families

| # | Fixture family | Purpose |
|---|----------------|---------|
| 1 | **small positive synthetic lift injections** | `lift_true ≈ +0.03–0.05`; baseline recovery |
| 2 | **medium positive synthetic lift injections** | `lift_true ≈ +0.08–0.12`; typical campaign scale |
| 3 | **large positive synthetic lift injections** | `lift_true ≈ +0.15–0.20`; saturation/stress |
| 4 | **negative synthetic lift injections if needed for symmetry reference** | Known negative; separate from directional-error primary battery |
| 5 | **near-MDE positive controls** | Effect at declared MDE boundary |
| 6 | **below-MDE positive controls** | Sub-MDE injected effect; diagnostic only |
| 7 | **delayed-effect positive controls** | Effect onset after intervention start |
| 8 | **decaying-effect positive controls** | Effect attenuation over post period |
| 9 | **heterogeneous market-level positive controls** | Mixed unit-level effect magnitudes |
| 10 | **sparse-metric positive controls** | Sparse KPI panels with known lift |
| 11 | **high-noise positive controls** | High noise; recovery should remain diagnosable |
| 12 | **seasonal positive controls** | Seasonal structure with known lift |
| 13 | **outlier-contaminated positive controls** | Known lift with outlier weeks |
| 14 | **weak-preperiod-fit positive controls** | Poor pre-fit with known positive lift |
| 15 | **donor-pool-shift positive controls** | Donor composition shift under known lift |
| 16 | **fold-geometry positive controls** | Fold-count/layout variation under known lift |

Each fixture family requires ≥3 seeds, lineage manifest entry, and explicit `lift_true` / `effect_true` ground-truth fields.

---

## 11. Required injected-effect controls

| Control type | Injection | Ground truth |
|--------------|-----------|--------------|
| Small positive | `lift_true = +0.05` | Recoverable positive |
| Medium positive | `lift_true = +0.10` | Recoverable positive |
| Large positive | `lift_true = +0.15` | Recoverable positive |
| Near-MDE | `lift_true = mde_declared` | Boundary diagnostic |
| Below-MDE | `lift_true < mde_declared` | Sub-threshold diagnostic |
| Delayed onset | Effect ramps weeks 2–4 | Time-shape recovery |
| Decaying | Effect decays post week 4 | Time-shape recovery |
| Symmetry negative (reference) | `lift_true = -0.05` | Magnitude reference only |

Synthetic controls require documented seed policy and fixture hash in `lineage_provenance_manifest`.

---

## 12. Required historical positive-control references

| Control type | Source | Use |
|--------------|--------|-----|
| D5 clean positive-lift worlds | `D5_TRUST_TBRRIDGE_KFOLD_001` | Historical recovery replay |
| D5 effect sweep subsets | Method promotion evidence audit | Partial recovery data |
| Power/MDE diagnostic worlds | `D5_POW_*` chains | Near-MDE reference |
| Historical campaign windows | Geo panel archives | Real positive-effect periods |

Historical controls must be tagged with `control_class: HISTORICAL_POSITIVE_CONTROL` and `lift_true` documented per world.

---

## 13. Recovery diagnostic metrics to be reported later

Metrics to be **defined and reported** by future evidence artifacts (not computed by this audit):

| Metric | Definition (diagnostic) |
|--------|---------------------------|
| `positive_control_recovery_rate_diagnostic` | Fraction of positive-control worlds with recovery within tolerance |
| `effect_size_recovery_bias_diagnostic` | Mean signed bias (estimate − true) across worlds |
| `effect_size_recovery_ratio_diagnostic` | Mean ratio (estimate / true) across worlds |
| `under_recovery_rate_diagnostic` | Fraction with estimate materially below true |
| `over_recovery_rate_diagnostic` | Fraction with estimate materially above true |
| `near_mde_recovery_stability_diagnostic` | Recovery variation at MDE boundary |
| `delayed_effect_recovery_diagnostic` | Recovery under delayed-onset shapes |
| `heterogeneous_effect_recovery_diagnostic` | Recovery under heterogeneous unit effects |
| `recovery_stability_by_fold` | Recovery variation across fold counts |
| `recovery_stability_by_donor_pool` | Recovery variation across donor pools |
| `recovery_stability_by_regularization` | Recovery variation across ridge alpha |
| `recovery_stability_by_metric_scale` | Recovery variation across metric scales |
| `recovery_stability_by_noise_regime` | Recovery variation across noise levels |

All metrics are **diagnostic-only** and must not be labeled as validated recovery rates.

---

## 14. Distinction from directional-error behavior

| Dimension | Directional error (prior audit) | Positive-control recovery (this audit) |
|-----------|--------------------------------|----------------------------------------|
| **Primary question** | Is sign correct? | Is magnitude recovered? |
| **Ground truth** | Signed effect (pos/neg/near-zero) | Known injected lift magnitude |
| **Failure mode** | Wrong sign | Under-recovery, over-recovery, instability |
| **Metric** | `directional_error_rate_diagnostic` | `positive_control_recovery_rate_diagnostic` |
| **Severe case** | Positive claimed when negative | Estimate 50% below true positive lift |
| **Near-MDE** | Sign instability zone | Recovery instability (not power evidence) |
| **Report key** | `directional_error_report` | `positive_control_recovery_report` |
| **Runtime blocker** | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_DIRECTIONAL_ERROR_EVIDENCE` | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_POSITIVE_CONTROL_RECOVERY` |

**Rule:** Passing directional-error audit does not imply passing positive-control recovery audit. Both reports required for promotion review.

---

## 15. Acceptance criteria for future evidence artifact

Future positive-control recovery evidence is acceptable when:

1. fixtures cover effect sizes, time shapes, noise regimes, metric scales, donor pools, fold geometries, and preperiod-fit quality
2. diagnostics distinguish recovery failure from directional-error failure
3. diagnostics distinguish under-recovery, over-recovery, and unstable recovery
4. near-MDE and below-MDE behavior is documented as diagnostic, not claim-authorizing
5. outputs are diagnostic-only and compatible with interval semantics audit
6. no p-value/significance/CI claim is inferred
7. failure modes produce blockers or restrictions in promotion review runtime
8. evidence packet can populate `positive_control_recovery_report` in `generate_tbrridge_method_promotion_review()`

---

## 16. Blocker criteria for future promotion review

Promotion review blocks (`METHOD_PROMOTION_REVIEW_BLOCKED_BY_POSITIVE_CONTROL_RECOVERY`) when:

- missing positive-control recovery report
- incomplete injected-effect fixture coverage
- known effects not recoverable under basic compatible regimes
- severe under-recovery or over-recovery not characterized
- recovery confused with directional correctness
- near-MDE behavior treated as power/significance evidence
- diagnostic intervals treated as confidence intervals
- aggregate/pooled recovery used without validation
- metric/estimand mismatch
- claim authorization boundary missing

Risk flag: `POSITIVE_CONTROL_RECOVERY_INCOMPLETE`

---

## 17. Runtime packet integration plan

Future `positive_control_recovery_report` dict for `generate_tbrridge_method_promotion_review()`:

```json
{
  "worlds": ["pos_small", "pos_medium", "pos_near_mde"],
  "fixture_families_covered": 16,
  "positive_control_recovery_rate_diagnostic": null,
  "effect_size_recovery_bias_diagnostic": null,
  "effect_size_recovery_ratio_diagnostic": null,
  "under_recovery_rate_diagnostic": null,
  "over_recovery_rate_diagnostic": null,
  "near_mde_recovery_stability_diagnostic": null,
  "evidence_incomplete": false,
  "positive_control_recovery_incomplete": false,
  "directional_error_distinction_maintained": true,
  "diagnostic_only": true,
  "audit_source": "TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001",
  "summary": {
    "audit_requirements_defined": true,
    "evidence_generated": false
  }
}
```

**Integration rules:**

1. `detect_tbrridge_method_promotion_risks()` flags `POSITIVE_CONTROL_RECOVERY_INCOMPLETE` when `positive_control_recovery_incomplete` or `evidence_incomplete` is true
2. `evaluate_method_promotion_review()` blocks with `METHOD_PROMOTION_REVIEW_BLOCKED_BY_POSITIVE_CONTROL_RECOVERY` when report missing or incomplete
3. Metric values remain null until future simulation artifact populates them
4. This audit defines schema and requirements only

---

## 18. Allowed language

- **positive-control recovery diagnostic** — Known-effect magnitude recovery characterization
- **known-effect recovery audit** — Systematic under/over-recovery risk assessment
- **injected-effect stress case** — Specific injected-lift fixture family evaluation
- **review-only recovery diagnostic** — Diagnostic recovery summary (not validated rate)
- **recovery stability diagnostic** — Cross-regime recovery variation characterization
- **evidence input for promotion review** — Report supplied to promotion review runtime

---

## 19. Prohibited language

- **validated recovery rate**
- **approved effect recovery**
- **statistical power approval**
- **statistical significance support**
- **p-value calibration**
- **confidence interval coverage approval**
- **production-ready recovery behavior**
- **causal lift claim**
- **ROI claim**
- **method promotion evidence complete**

---

## 20. Stop/go criteria

### Go (audit requirements adopted — does not generate evidence)

Proceed to `TBRRIDGE_REGIME_SENSITIVITY_PLAN_001` when:

1. Positive-control fixture families documented
2. Recovery diagnostic metrics defined
3. Directional-error distinction documented
4. Acceptance and blocker criteria defined
5. Runtime packet schema defined
6. Interval semantics and prior battery compatibility confirmed

### Stop

Stop when:

1. Recovery evidence interpreted as validated effect recovery or power approval
2. Diagnostic intervals treated as confidence intervals for recovery claims
3. Near-MDE recovery conflated with statistical significance or power evidence
4. Recovery failure conflated with directional-error failure without separation
5. Aggregate/pooled recovery paths used without geometry validation
6. Recovery metrics computed without governed fixture lineage (future artifact violation)
7. Attempt to mark recovery evidence as promotion-complete

---

## 21. Authorization boundary

**Allowed:** `tbrridge_positive_control_recovery_audit_completed`, `positive_control_recovery_gap_documented`, `positive_control_fixture_requirements_defined`, `recovery_diagnostic_metrics_defined`, `directional_error_distinction_defined`, `blocker_criteria_defined`, `runtime_packet_integration_defined`

**Forbidden:** `positive_control_evidence_generated`, `recovery_rate_computed`, `effect_recovery_validated`, `statistical_power_validated`, `p_value_calibrated`, `statistical_significance_authorized`, `confidence_interval_authorized`, `interval_computed`, `coverage_computed`, `simulations_implemented`, all inference/estimator/kfold/placebo implementation flags, all promotion/production/uncertainty/lift/ROI/MMM/LLM flags

TBRRidge remains **RANK_0**, **BLOCKED**, **STAGE_2_DIAGNOSTIC_ONLY**.

---

## 22. Validation results

| Check | Result |
|-------|--------|
| Audit document complete | Pass |
| Summary JSON valid | Pass |
| Governance tests | Pass |
| `failed_scenarios` | `[]` |

---

## 23. Known limitations

- **Requirements only** — No injected worlds replayed; no recovery rates computed
- **D5 recovery referenced** — Partial clean-world recovery informs gap severity; not re-run
- **Directional-error separate** — Sign characterization remains in directional-error audit
- **Regime sensitivity deferred** — Cross-regime stability is `TBRRIDGE_REGIME_SENSITIVITY_PLAN_001`
- **Metric values null in schema** — Packet template uses null placeholders until evidence generated

---

## 24. Recommended next artifacts

| Role | Artifact |
|------|----------|
| **Primary** | `TBRRIDGE_REGIME_SENSITIVITY_PLAN_001` |
| **Alternative** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` |
| **Deferred** | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` |
| **Future evidence** | Positive-control recovery simulation/runtime artifact (not yet planned as separate ID) |
