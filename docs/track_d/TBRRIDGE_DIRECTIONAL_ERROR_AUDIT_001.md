# TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` |
| **Artifact type** | `tbrridge_directional_error_audit` |
| **Status** | `completed` |
| **Scope** | `tbrridge_directional_error_audited_no_directional_error_computation_or_authorization` |
| **Base commit** | `a55db1e` (Add TBRRidge null-control false-positive audit) |
| **Final verdict** | `tbrridge_directional_error_audited_no_directional_error_computation_or_authorization` |

**Depends on:** `TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001` · `TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` · `TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` · `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001`

**Positive audit flags:** `tbrridge_directional_error_audit_completed` · `directional_error_gap_documented` · `directional_fixture_requirements_defined` · `directional_diagnostic_metrics_defined` · `false_positive_distinction_defined` · `blocker_criteria_defined` · `runtime_packet_integration_defined`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001.md`
- `docs/track_d/archives/TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001_summary.json`
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
| **Directional-error evidence** | Not generated |

D5-TRUST-TBRRIDGE-KFOLD-001 documented poor sign accuracy (~35%). Directional-error behavior is **uncharacterized** for method-promotion evidence. This audit defines evaluation requirements only.

---

## 4. Relationship to promotion evidence battery plan

`TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` lists **directional-error behavior** as evidence component #3 (`directional_error_report`), P0 blocking, depending on null-control false-positive audit completion.

This audit is artifact #3 in the ordered battery sequence. It defines signed-effect fixture families, directional diagnostic metrics, acceptance/blocker criteria, and runtime packet shape. It does **not** run simulations or compute directional-error rates.

---

## 5. Relationship to null-control false-positive audit

`TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001` defined null/no-effect false-positive evaluation under governed null worlds and introduced `directional_false_positive_rate_diagnostic` as a **separate** metric from non-directional false positives.

Directional-error audit builds on that separation:

1. **Null-control audit** — detects any effect claim under no-effect worlds (false positive)
2. **Directional-error audit** — detects **wrong-sign** claims under signed-effect worlds (positive when negative, negative when positive)

A null-world false positive is not the same as a signed-world directional error. Both must be characterized independently.

---

## 6. Relationship to interval semantics audit

`TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` established that KFold bands are **diagnostic uncertainty summaries**, not confidence intervals.

Directional-error evaluation must:

1. Use **diagnostic sign-claim** framing — wrong-sign point estimates or interval-implied direction
2. **Not** treat signed interval exclusion as significance testing
3. **Not** treat sign accuracy as validated directional correctness
4. Populate `directional_error_report` compatible with `interval_semantics_report`

---

## 7. Directional-error purpose and claim boundary

**Purpose:** Define how TBRRidge KFold must be evaluated for wrong-sign behavior under governed signed-effect worlds before method-promotion review can treat directional-error evidence as non-blocking.

**Question answered (future):** When true effect is positive, negative, or near-zero, does TBRRidge KFold avoid systematic wrong-sign diagnostic claims?

**Claim boundary:** Directional-error diagnostics are **review-only falsification evidence**. They do not authorize statistical significance, sign-correctness approval, confidence-interval coverage approval, causal lift claims, method promotion, or production readout claims.

---

## 8. Directional-error evidence gap

| Gap | Current state | Severity |
|-----|---------------|----------|
| Signed-effect worlds | D5 directional worlds referenced; not attached to promotion packets | P0 |
| Wrong-sign rate characterization | Not computed under contract | P0 |
| Positive-to-negative / negative-to-positive errors | Not separated | P0 |
| Near-zero sign instability | Not distinguished from severe reversal | P0 |
| Fold/donor/regularization directional stability | Not characterized | P0 |
| Metric-scale directional behavior | Level-percent vs ATT sign behavior not separated | P0 |
| Promotion runtime integration | `directional_error_report` missing from supplied evidence | P0 |

**Audit decision:** Requirements and packet schema are defined; evidence generation is deferred to future simulation/runtime artifacts.

---

## 9. Required directional fixture families

| # | Fixture family | Purpose |
|---|----------------|---------|
| 1 | **positive-effect synthetic injection controls** | Known positive lift; test negative-to-positive error |
| 2 | **negative-effect synthetic injection controls** | Known negative lift; test positive-to-negative error |
| 3 | **near-zero signed-effect controls** | True effect near zero; test sign instability |
| 4 | **sign-flip stress controls** | Adversarial sign-flip injection |
| 5 | **heterogeneous-effect signed controls** | Mixed positive/negative across units |
| 6 | **weak-preperiod-fit signed controls** | Poor pre-fit with known sign |
| 7 | **sparse-metric signed controls** | Sparse KPI panels with signed ground truth |
| 8 | **high-noise signed controls** | High noise; sign should remain recoverable |
| 9 | **seasonal signed controls** | Seasonal structure with signed effect |
| 10 | **outlier-contaminated signed controls** | Signed effect with outlier weeks |
| 11 | **donor-pool-shift signed controls** | Donor composition shift under signed effect |
| 12 | **fold-geometry signed controls** | Fold-count/layout variation under signed effect |

Each fixture family requires ≥3 seeds, lineage manifest entry, and explicit `sign_true` ground-truth field.

---

## 10. Required synthetic signed-effect controls

| Control type | Injection | Ground truth |
|--------------|-----------|--------------|
| Small positive lift | `lift_true = +0.05` | Positive |
| Large positive lift | `lift_true = +0.15` | Positive |
| Small negative lift | `lift_true = -0.05` | Negative |
| Large negative lift | `lift_true = -0.15` | Negative |
| Near-zero lift | `lift_true ∈ [-0.01, +0.01]` | Ambiguous / instability zone |
| Sign-flip adversarial | Injected opposite-sign noise | Stress wrong-sign detection |

Synthetic controls require documented seed policy and fixture hash in `lineage_provenance_manifest`.

---

## 11. Required historical/placebo signed controls

| Control type | Source | Use |
|--------------|--------|-----|
| D5 directional worlds | `D5_TRUST_TBRRIDGE_KFOLD_001` | Historical signed-effect replay |
| D5 effect sweep subsets | Method promotion evidence audit | Partial recovery/sign data |
| Placebo with known sign offset | Placebo calibration chain | Signed placebo stress |
| Historical campaign windows | Geo panel archives | Real signed-effect periods |

Historical controls must be tagged with `control_class: HISTORICAL_SIGNED` and `sign_true` documented per world.

---

## 12. Directional diagnostic metrics to be reported later

Metrics to be **defined and reported** by future evidence artifacts (not computed by this audit):

| Metric | Definition (diagnostic) |
|--------|---------------------------|
| `directional_error_rate_diagnostic` | Fraction of signed worlds with wrong-sign diagnostic claim |
| `positive_to_negative_error_rate_diagnostic` | True positive → diagnosed negative |
| `negative_to_positive_error_rate_diagnostic` | True negative → diagnosed positive |
| `near_zero_sign_instability_diagnostic` | Sign flip rate under near-zero true effect |
| `sign_confidence_overstatement_rate_diagnostic` | Strong sign claim when true effect is weak |
| `signed_interval_exclusion_diagnostic` | Interval-implied wrong sign under signed world |
| `directional_stability_by_fold` | Wrong-sign rate variation across fold counts |
| `directional_stability_by_donor_pool` | Wrong-sign rate variation across donor pools |
| `directional_stability_by_regularization` | Wrong-sign rate variation across ridge alpha |
| `directional_stability_by_metric_scale` | Wrong-sign rate variation across metric scales |
| `directional_stability_by_noise_regime` | Wrong-sign rate variation across noise levels |

All metrics are **diagnostic-only** and must not be labeled as validated sign accuracy.

---

## 13. Distinction from false-positive behavior

| Dimension | False-positive (null-control audit) | Directional error (this audit) |
|-----------|-------------------------------------|--------------------------------|
| **Ground truth** | No effect (null) | Signed effect (positive/negative/near-zero) |
| **Failure mode** | Any detection under null | Wrong sign under signed effect |
| **Metric** | `false_positive_rate_diagnostic` | `directional_error_rate_diagnostic` |
| **Severe case** | Effect claimed when none exists | Positive claimed when negative (or vice versa) |
| **Near-zero** | N/A (null worlds) | Sign instability, not false positive |
| **Report key** | `null_control_false_positive_report` | `directional_error_report` |
| **Runtime blocker** | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_FALSE_POSITIVE_EVIDENCE` | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_DIRECTIONAL_ERROR_EVIDENCE` |

**Rule:** Passing null-control audit does not imply passing directional-error audit. Both reports required for promotion review.

---

## 14. Acceptance criteria for future evidence artifact

Future directional-error evidence is acceptable when:

1. signed-effect fixtures cover positive, negative, near-zero, heterogeneous, high-noise, sparse, seasonal, and outlier regimes
2. diagnostics distinguish false positive from wrong-sign behavior
3. diagnostics distinguish sign instability near zero from severe wrong-sign evidence
4. outputs are diagnostic-only and compatible with interval semantics audit
5. no p-value/significance/CI claim is inferred
6. failure modes produce blockers or restrictions in promotion review runtime
7. evidence packet can populate `directional_error_report` in `generate_tbrridge_method_promotion_review()`

---

## 15. Blocker criteria for future promotion review

Promotion review blocks (`METHOD_PROMOTION_REVIEW_BLOCKED_BY_DIRECTIONAL_ERROR_EVIDENCE`) when:

- missing directional-error report
- incomplete signed-effect fixture coverage
- wrong-sign behavior not characterized
- near-zero instability not separated from severe sign reversal
- directional evidence interpreted as statistical significance support
- diagnostic intervals treated as confidence intervals
- aggregate/pooled directional behavior used without validation
- metric/estimand mismatch
- claim authorization boundary missing

Risk flag: `DIRECTIONAL_ERROR_EVIDENCE_INCOMPLETE`

---

## 16. Runtime packet integration plan

Future `directional_error_report` dict for `generate_tbrridge_method_promotion_review()`:

```json
{
  "worlds": ["dir_small_pos", "dir_small_neg", "dir_near_zero"],
  "fixture_families_covered": 12,
  "directional_error_rate_diagnostic": null,
  "positive_to_negative_error_rate_diagnostic": null,
  "negative_to_positive_error_rate_diagnostic": null,
  "near_zero_sign_instability_diagnostic": null,
  "evidence_incomplete": false,
  "directional_error_evidence_incomplete": false,
  "false_positive_distinction_maintained": true,
  "diagnostic_only": true,
  "audit_source": "TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001",
  "summary": {
    "audit_requirements_defined": true,
    "evidence_generated": false
  }
}
```

**Integration rules:**

1. `detect_tbrridge_method_promotion_risks()` flags `DIRECTIONAL_ERROR_EVIDENCE_INCOMPLETE` when `directional_error_evidence_incomplete` or `evidence_incomplete` is true
2. `evaluate_method_promotion_review()` blocks with `METHOD_PROMOTION_REVIEW_BLOCKED_BY_DIRECTIONAL_ERROR_EVIDENCE` when report missing or incomplete
3. Metric values remain null until future simulation artifact populates them
4. This audit defines schema and requirements only

---

## 17. Allowed language

- **directional-error diagnostic** — Wrong-sign characterization under signed-effect worlds
- **wrong-sign behavior audit** — Systematic sign-reversal risk assessment
- **signed-effect stress case** — Specific signed fixture family evaluation
- **review-only directional diagnostic** — Diagnostic sign summary (not validated accuracy)
- **sign instability diagnostic** — Near-zero flip behavior characterization
- **evidence input for promotion review** — Report supplied to promotion review runtime

---

## 18. Prohibited language

- **validated directional accuracy**
- **approved sign correctness**
- **statistical significance support**
- **p-value calibration**
- **confidence interval coverage approval**
- **production-ready directional behavior**
- **causal lift claim**
- **ROI claim**
- **method promotion evidence complete**

---

## 19. Stop/go criteria

### Go (audit requirements adopted — does not generate evidence)

Proceed to `TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001` when:

1. Directional fixture families documented
2. Diagnostic metrics defined
3. False-positive distinction documented
4. Acceptance and blocker criteria defined
5. Runtime packet schema defined
6. Interval semantics and null-control compatibility confirmed

### Stop

Stop when:

1. Directional evidence interpreted as sign-correctness validation or significance support
2. Diagnostic intervals treated as confidence intervals for sign claims
3. Near-zero instability conflated with severe wrong-sign reversal without separation
4. Aggregate/pooled directional paths used without geometry validation
5. Directional metrics computed without governed fixture lineage (future artifact violation)
6. Attempt to mark directional evidence as promotion-complete

---

## 20. Authorization boundary

**Allowed (true):** `tbrridge_directional_error_audit_completed`, `directional_error_gap_documented`, `directional_fixture_requirements_defined`, `directional_diagnostic_metrics_defined`, `false_positive_distinction_defined`, `blocker_criteria_defined`, `runtime_packet_integration_defined`

**Forbidden (false):** `directional_error_evidence_generated`, `directional_error_rate_computed`, `sign_accuracy_validated`, `p_value_calibrated`, `statistical_significance_authorized`, `confidence_interval_authorized`, `interval_computed`, `coverage_computed`, `simulations_implemented`, all inference/estimator/kfold/placebo implementation flags, all promotion/production/uncertainty/lift/ROI/MMM/LLM flags

TBRRidge remains **RANK_0**, **BLOCKED**, **STAGE_2_DIAGNOSTIC_ONLY**.

---

## 21. Validation results

| Check | Result |
|-------|--------|
| Audit document complete | Pass |
| Summary JSON valid | Pass |
| Governance tests | Pass |
| `failed_scenarios` | `[]` |

---

## 22. Known limitations

- **Requirements only** — No signed worlds replayed; no directional-error rates computed
- **D5 sign accuracy referenced** — ~35% sign accuracy informs gap severity; not re-run
- **Null-control separate** — False-positive characterization remains in null-control audit
- **Positive-control recovery deferred** — Magnitude recovery is `TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001`
- **Metric values null in schema** — Packet template uses null placeholders until evidence generated

---

## 23. Recommended next artifacts

| Role | Artifact |
|------|----------|
| **Primary** | `TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001` |
| **Alternative** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` |
| **Deferred** | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` |
| **Future evidence** | Directional-error simulation/runtime artifact (not yet planned as separate ID) |
