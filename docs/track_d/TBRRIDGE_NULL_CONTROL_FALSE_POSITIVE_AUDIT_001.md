# TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001` |
| **Artifact type** | `tbrridge_null_control_false_positive_audit` |
| **Status** | `completed` |
| **Scope** | `tbrridge_null_control_false_positive_audited_no_false_positive_computation_or_authorization` |
| **Base commit** | `7f0258d` (Add TBRRidge interval semantics audit) |
| **Final verdict** | `tbrridge_null_control_false_positive_audited_no_false_positive_computation_or_authorization` |

**Depends on:** `TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` · `TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` · `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001`

**Positive audit flags:** `tbrridge_null_control_false_positive_audit_completed` · `null_control_gap_documented` · `null_control_fixture_requirements_defined` · `false_positive_diagnostic_metrics_defined` · `blocker_criteria_defined` · `runtime_packet_integration_defined`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001.md`
- `docs/track_d/archives/TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001_summary.json`
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
| **Null-control evidence** | Not generated |

TBRRidge KFold null-control false-positive behavior is **uncharacterized** for method-promotion evidence. This audit defines evaluation requirements only.

---

## 4. Relationship to promotion evidence battery plan

`TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` lists **null-control false-positive behavior** as evidence component #2 (`null_control_false_positive_report`), P0 blocking, depending on interval semantics audit completion.

This audit is artifact #2 in the ordered battery sequence. It defines fixture families, diagnostic metrics, acceptance/blocker criteria, and runtime packet shape. It does **not** run simulations or produce empirical false-positive rates.

---

## 5. Relationship to interval semantics audit

`TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` established that TBRRidge KFold bands are **diagnostic uncertainty summaries**, not confidence intervals or calibrated causal uncertainty.

Null-control false-positive evaluation must:

1. Use **diagnostic overclaim** framing — detecting when null worlds trigger apparent effects or interval exclusions
2. **Not** interpret interval exclusion as significance testing
3. **Not** treat diagnostic FPR summaries as type-I error validation
4. Populate `null_control_false_positive_report` compatible with `interval_semantics_report` from the prior audit

---

## 6. Null-control purpose and claim boundary

**Purpose:** Define how TBRRidge KFold must behave under governed no-effect worlds before method-promotion review can treat null-control evidence as non-blocking.

**Question answered (future):** Under declared null worlds, does TBRRidge KFold avoid diagnostic overclaims that could be misread as causal detection?

**Claim boundary:** Null-control diagnostics are **review-only falsification evidence**. They do not authorize statistical significance, p-value support, confidence-interval coverage approval, method promotion, or production readout claims.

---

## 7. False-positive evidence gap

| Gap | Current state | Severity |
|-----|---------------|----------|
| Governed null worlds | D5 null worlds referenced; not attached to promotion review packets | P0 |
| False-positive rate characterization | Not computed or reported under contract | P0 |
| Directional vs non-directional false signal | Not separated in governed reports | P0 |
| Fold/donor/regularization stability | Not characterized under null | P0 |
| Placebo tail behavior | Placebo diagnostic runtime exists; null FPR linkage incomplete | P0 |
| Metric-scale null behavior | Level-percent vs ATT null behavior not separated | P0 |
| Promotion runtime integration | `null_control_false_positive_report` missing from supplied evidence | P0 |

**Audit decision:** Requirements and packet schema are defined; evidence generation is deferred to future simulation/runtime artifacts.

---

## 8. Required null-control fixture families

| # | Fixture family | Purpose |
|---|----------------|---------|
| 1 | **no-treatment placebo markets** | Markets with no intervention; baseline null |
| 2 | **pre-period-only pseudo-treatment windows** | Treatment window in pre-period only |
| 3 | **shuffled treatment assignment controls** | Randomized assignment preserving marginals |
| 4 | **matched donor no-effect controls** | Donor pool matched; zero injected effect |
| 5 | **synthetic zero-lift injection controls** | Known zero lift injected post-fit |
| 6 | **low-signal sparse metric controls** | Sparse KPI panels with null ground truth |
| 7 | **high-noise stable-null controls** | High noise; effect should remain undetected |
| 8 | **seasonal-null controls** | Seasonal structure without treatment effect |
| 9 | **outlier-contaminated null controls** | Null with outlier weeks injected |
| 10 | **weak-preperiod-fit null controls** | Poor pre-period fit; null effect maintained |

Each fixture family requires ≥3 seeds, lineage manifest entry, and explicit world ID for future battery runs.

---

## 9. Required historical/placebo controls

| Control type | Source | Use |
|--------------|--------|-----|
| D5 null worlds | `D5_TRUST_TBRRIDGE_KFOLD_001` | Historical null replay baseline |
| Placebo-shift nulls | Placebo calibration diagnostic chain | Placebo contamination checks |
| Pre-period holdout nulls | Leakage diagnostic manifests | Temporal leakage null checks |
| Historical no-campaign windows | Geo panel archives | Real-world no-effect periods |

Historical controls must be tagged with `control_class: HISTORICAL_NULL` and must not be pooled across incompatible geometries.

---

## 10. Required synthetic no-effect controls

| Control type | Injection | Expected ground truth |
|--------------|-----------|----------------------|
| Zero-lift injection | `lift_true = 0` | No causal effect |
| Placebo date shift | Treatment dates shifted pre-period | No post-period effect |
| Donor swap null | Donors from non-treated pool only | No treatment contrast |
| Noise-only perturbation | Outcome noise without treatment | Null detection stress |
| Ridge overfit null | Extreme regularization on null panel | Stability under overfit |

Synthetic controls require documented seed policy and fixture hash in `lineage_provenance_manifest`.

---

## 11. False-positive diagnostic metrics to be reported later

Metrics to be **defined and reported** by future evidence artifacts (not computed by this audit):

| Metric | Definition (diagnostic) |
|--------|-------------------------|
| `false_positive_rate_diagnostic` | Fraction of null worlds where diagnostic claims effect presence |
| `directional_false_positive_rate_diagnostic` | Fraction of null worlds with incorrect directional signal |
| `null_interval_exclusion_rate_diagnostic` | Fraction of null worlds where diagnostic band excludes zero |
| `null_claim_overstatement_rate_diagnostic` | Fraction of null worlds triggering overclaim risk flags |
| `placebo_tail_miscalibration_diagnostic` | Placebo tail behavior under null (diagnostic, not calibrated) |
| `null_detection_stability_by_fold` | Null detection rate variation across fold counts |
| `null_detection_stability_by_donor_pool` | Null detection rate variation across donor pools |
| `null_detection_stability_by_regularization` | Null detection rate variation across ridge alpha grid |
| `null_detection_stability_by_metric_scale` | Null detection rate variation across metric scales |

All metrics are **diagnostic-only** and must not be labeled as validated type-I error rates.

---

## 12. Directional false-signal distinction

| Signal type | Definition | Separate metric |
|-------------|------------|-----------------|
| **Non-directional false positive** | Null world triggers any effect/detection claim | `false_positive_rate_diagnostic` |
| **Directional false signal** | Null world triggers incorrect sign/direction | `directional_false_positive_rate_diagnostic` |

Future evidence must report both metrics separately. Directional false signals are deferred to `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` for full characterization but must be **flagged** in null-control reports when detected.

**Rule:** Null-control audit pass does not imply directional-error audit pass.

---

## 13. Acceptance criteria for future evidence artifact

Future null-control evidence (simulation/runtime artifact) is acceptable when:

1. null-control fixtures cover multiple metrics, time windows, donor-pool sizes, fold geometries, noise levels, and seasonality regimes
2. reported diagnostics distinguish false positive from directional false signal
3. outputs are diagnostic-only and compatible with interval semantics audit
4. no p-value/significance/CI claim is inferred from null-control results
5. failure modes produce blockers or restrictions in promotion review runtime
6. evidence packet can populate `null_control_false_positive_report` in `generate_tbrridge_method_promotion_review()`

---

## 14. Blocker criteria for future promotion review

Promotion review blocks (`METHOD_PROMOTION_REVIEW_BLOCKED_BY_FALSE_POSITIVE_EVIDENCE`) when:

- missing null-control report
- incomplete fixture coverage
- uncharacterized false-positive behavior
- directional false-signal not separated
- null-control evidence interpreted as p-value/significance support
- diagnostic intervals treated as confidence intervals
- aggregate/pooled null behavior used without validation
- metric/estimand mismatch
- claim authorization boundary missing

Risk flag: `NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE`

---

## 15. Runtime packet integration plan

Future `null_control_false_positive_report` dict for `generate_tbrridge_method_promotion_review()`:

```json
{
  "worlds": ["null_zero", "null_placebo", "null_shuffled"],
  "fixture_families_covered": 10,
  "false_positive_rate_diagnostic": null,
  "directional_false_positive_rate_diagnostic": null,
  "null_interval_exclusion_rate_diagnostic": null,
  "evidence_incomplete": false,
  "null_control_false_positive_incomplete": false,
  "directional_false_signal_separated": true,
  "diagnostic_only": true,
  "audit_source": "TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001",
  "summary": {
    "audit_requirements_defined": true,
    "evidence_generated": false
  }
}
```

**Integration rules:**

1. `detect_tbrridge_method_promotion_risks()` flags `NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE` when `null_control_false_positive_incomplete` or `evidence_incomplete` is true
2. `evaluate_method_promotion_review()` blocks with `METHOD_PROMOTION_REVIEW_BLOCKED_BY_FALSE_POSITIVE_EVIDENCE` when report missing or incomplete
3. Metric values remain null until future simulation artifact populates them
4. This audit defines schema and requirements only

---

## 16. Allowed language

- **null-control diagnostic** — Falsification check under no-effect worlds
- **false-positive behavior audit** — Characterization of overclaim risk under null
- **no-effect stress case** — Specific null fixture family evaluation
- **review-only FPR diagnostic** — Diagnostic false-positive rate summary (not validated type-I error)
- **diagnostic overclaim risk** — Risk that null world triggers apparent detection
- **evidence input for promotion review** — Report supplied to promotion review runtime

---

## 17. Prohibited language

- **validated false-positive rate**
- **approved type-I error**
- **statistical significance support**
- **p-value calibration**
- **confidence interval coverage approval**
- **production-ready null behavior**
- **causal lift claim**
- **ROI claim**
- **method promotion evidence complete**

---

## 18. Stop/go criteria

### Go (audit requirements adopted — does not generate evidence)

Proceed to `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` when:

1. Null-control fixture families documented
2. Diagnostic metrics defined
3. Directional false-signal distinction documented
4. Acceptance and blocker criteria defined
5. Runtime packet schema defined
6. Interval semantics compatibility confirmed

### Stop

Stop when:

1. Null-control evidence interpreted as significance or type-I error validation
2. Diagnostic intervals treated as confidence intervals under null evaluation
3. Aggregate/pooled null paths used without geometry validation
4. False-positive metrics computed without governed fixture lineage (future artifact violation)
5. Attempt to mark null-control evidence as promotion-complete

---

## 19. Authorization boundary

**Allowed (true):** `tbrridge_null_control_false_positive_audit_completed`, `null_control_gap_documented`, `null_control_fixture_requirements_defined`, `false_positive_diagnostic_metrics_defined`, `blocker_criteria_defined`, `runtime_packet_integration_defined`

**Forbidden (false):** `null_control_evidence_generated`, `false_positive_rate_computed`, `type_i_error_validated`, `p_value_calibrated`, `statistical_significance_authorized`, `confidence_interval_authorized`, `interval_computed`, `coverage_computed`, `simulations_implemented`, all inference/estimator/kfold/placebo implementation flags, all promotion/production/uncertainty/lift/ROI/MMM/LLM flags

TBRRidge remains **RANK_0**, **BLOCKED**, **STAGE_2_DIAGNOSTIC_ONLY**.

---

## 20. Validation results

| Check | Result |
|-------|--------|
| Audit document complete | Pass |
| Summary JSON valid | Pass |
| Governance tests | Pass |
| `failed_scenarios` | `[]` |

---

## 21. Known limitations

- **Requirements only** — No null worlds replayed; no FPR values computed
- **D5 worlds referenced, not executed** — Historical null replay deferred to future simulation artifact
- **Placebo diagnostic separate** — Placebo calibration runtime governs placebo status; null FPR linkage is future work
- **Directional error deferred** — Full directional characterization is `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001`
- **Metric values null in schema** — Packet template uses null placeholders until evidence generated

---

## 22. Recommended next artifacts

| Role | Artifact |
|------|----------|
| **Primary** | `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` |
| **Alternative** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` |
| **Deferred** | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` |
| **Future evidence** | Null-control simulation/runtime artifact (not yet planned as separate ID) |
