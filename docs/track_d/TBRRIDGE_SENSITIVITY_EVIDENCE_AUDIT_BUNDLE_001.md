# TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001` |
| **Artifact type** | `tbrridge_sensitivity_evidence_audit_bundle` |
| **Status** | `completed` |
| **Scope** | `tbrridge_sensitivity_evidence_audit_bundle_defined_no_sensitivity_computation_or_authorization` |
| **Base commit** | `f23591f` (Add TBRRidge regime sensitivity plan) |
| **Final verdict** | `tbrridge_sensitivity_evidence_audit_bundle_defined_no_sensitivity_computation_or_authorization` |

**Depends on:** `TBRRIDGE_REGIME_SENSITIVITY_PLAN_001` · `TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001` · `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` · `TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001` · `TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` · `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001`

**Supersedes (planning execution):** `TBRRIDGE_DONOR_POOL_SENSITIVITY_AUDIT_001` · `TBRRIDGE_REGULARIZATION_SENSITIVITY_AUDIT_001` · `TBRRIDGE_OUTLIER_SENSITIVITY_AUDIT_001` · `TBRRIDGE_FOLD_GEOMETRY_SENSITIVITY_AUDIT_001` · `TBRRIDGE_SPARSE_HIGH_NOISE_METRIC_SENSITIVITY_AUDIT_001` · `TBRRIDGE_SEASONALITY_PREPERIOD_FIT_SENSITIVITY_AUDIT_001` · `TBRRIDGE_METRIC_SCALE_SENSITIVITY_AUDIT_001` · `TBRRIDGE_AGGREGATE_POOLED_GEOMETRY_BLOCKER_AUDIT_001`

**Positive bundle flags:** `tbrridge_sensitivity_evidence_audit_bundle_defined` · per-family `*_requirements_defined` (×8) · `crossed_regime_testing_policy_defined` · `runtime_packet_integration_defined` · `blocker_criteria_defined`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_REGIME_SENSITIVITY_PLAN_001.md`
- `docs/track_d/archives/TBRRIDGE_REGIME_SENSITIVITY_PLAN_001_summary.json`
- `docs/track_d/TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001.md`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001_REPORT.md`
- `panel_exp/validation/tbrridge_method_promotion_review_runtime_001.py`
- `panel_exp/validation/tbrridge_method_promotion_review_contract_001.py`

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
| **Sensitivity evidence** | Not generated |

---

## 4. Why sensitivity evidence is bundled

`TBRRIDGE_REGIME_SENSITIVITY_PLAN_001` originally sequenced eight separate sensitivity audits. Separate shallow artifacts would:

1. Duplicate regime-matrix and crossed-regime policy across eight docs
2. Fragment blocker mapping and runtime packet integration
3. Risk inconsistent fixture lineage and priority interpretation

**Bundle decision:** One consolidated sensitivity evidence audit defines all eight families coherently. The eight standalone artifact IDs remain **reference names** for report keys and governance traceability but are **not** executed as separate immediate artifacts.

---

## 5. Relationship to regime sensitivity plan

| Regime sensitivity plan | This bundle |
|-------------------------|-------------|
| Coordinated regime matrix | Inherited and applied per family |
| Crossed-regime Tier 1/2/3 policy | Inherited; full factorial prohibited |
| Ordered 8-artifact sequence | Superseded by single bundle |
| `regime_sensitivity_report` umbrella | Retained as umbrella packet |

This bundle **implements** the plan's sensitivity lane requirements without generating evidence.

---

## 6. Relationship to method-promotion review runtime

`tbrridge_method_promotion_review_contract_001.py` requires:

- `regime_sensitivity_report` (P0 block)
- `donor_pool_sensitivity_report`, `regularization_sensitivity_report`, `outlier_sensitivity_report`, `fold_geometry_sensitivity_report` (P1 restrict)
- Aggregate/pooled geometry validation

This bundle maps each sensitivity family to contract report keys, risk flags, and blocker rules for `generate_tbrridge_method_promotion_review()`.

---

## 7. Sensitivity bundle scope

**In scope:** Fixture requirements, diagnostics (named only), acceptance/blocker criteria, runtime packet schema, crossed-regime policy for:

1. `donor_pool_sensitivity`
2. `regularization_sensitivity`
3. `outlier_sensitivity`
4. `fold_geometry_sensitivity`
5. `sparse_high_noise_metric_sensitivity`
6. `seasonality_preperiod_fit_sensitivity`
7. `metric_scale_sensitivity`
8. `aggregate_pooled_geometry_blocker`

**Out of scope:** Simulations, sensitivity metric computation, inference, promotion, production authorization.

---

## 8. Coordinated sensitivity matrix

Inherited from `TBRRIDGE_REGIME_SENSITIVITY_PLAN_001`:

| Axis | Levels |
|------|--------|
| `donor_pool_size` | small / medium / large |
| `donor_pool_quality` | strong / mixed / weak |
| `donor_pool_shift` | stable / moderate_shift / severe_shift |
| `regularization_strength` | low / medium / high |
| `outlier_contamination` | none / moderate / severe |
| `fold_geometry` | stable / imbalanced / sparse / leave-region-out |
| `metric_density` | dense / sparse / zero-inflated |
| `noise_regime` | low / medium / high |
| `seasonality` | none / aligned / misaligned |
| `preperiod_fit` | strong / mixed / weak |
| `metric_scale` | normalized / skewed / heavy-tailed |
| `effect_shape` | immediate / delayed / decaying / heterogeneous |
| `aggregation_geometry` | unit-level / pooled / aggregate-stress |

---

## 9. Donor-pool sensitivity requirements

| Field | Specification |
|-------|---------------|
| **Purpose** | Characterize diagnostic instability across donor-pool composition |
| **Risk tested** | Donor-pool choice materially changes null/FPR, directional, or recovery diagnostics |
| **Fixture families** | Tight pool, wide pool, sparse pool; size small/medium/large; quality strong/mixed/weak; shift stable/moderate/severe |
| **Controls** | Synthetic donor-swap manifests; D5 donor subsets; historical donor composition slices |
| **Diagnostics** | `donor_pool_sensitivity_diagnostic`, `donor_pool_shift_diagnostic`, `donor_quality_degradation_diagnostic` |
| **Report field** | `pool_variants`, `donor_pool_sensitivity_diagnostic`, `sensitivity_incomplete` |
| **Acceptance** | All size/quality/shift levels characterized; material instability flagged |
| **Blockers** | Missing donor-pool evidence; instability uncharacterized |
| **Runtime target** | `donor_pool_sensitivity_report` |
| **Priority** | P1 (restriction) |
| **Dependencies** | Regime plan matrix; null/directional/recovery battery overlays |

---

## 10. Regularization sensitivity requirements

| Field | Specification |
|-------|---------------|
| **Purpose** | Characterize ridge-alpha diagnostic instability |
| **Risk tested** | Conclusions change materially across regularization grid |
| **Fixture families** | Alpha grid low/medium/high (`{0.01, 0.1, 1.0, 10.0}` reference) |
| **Controls** | D5 alpha partial replays; synthetic alpha sweep on fixed panels |
| **Diagnostics** | `regularization_sensitivity_diagnostic`, `regularization_overconstraint_diagnostic`, `regularization_underconstraint_diagnostic` |
| **Report field** | `alpha_grid`, `regularization_sensitivity_diagnostic`, `sensitivity_incomplete` |
| **Acceptance** | Full grid evaluated; over/under-constraint patterns documented |
| **Blockers** | Missing regularization evidence; grid not characterized |
| **Runtime target** | `regularization_sensitivity_report` |
| **Priority** | P1 (restriction) |
| **Dependencies** | Donor-pool default regimes as anchor |

---

## 11. Outlier sensitivity requirements

| Field | Specification |
|-------|---------------|
| **Purpose** | Characterize outlier-week diagnostic distortion |
| **Risk tested** | Single/multi-week spikes flip sign, inflate FPR, or distort recovery |
| **Fixture families** | None/moderate/severe contamination; single-week spike; multi-week drift |
| **Controls** | Outlier injection manifests; historical outlier-tagged slices |
| **Diagnostics** | `outlier_sensitivity_diagnostic`, `outlier_directional_instability_diagnostic` |
| **Report field** | `outlier_scenarios`, `outlier_sensitivity_diagnostic`, `sensitivity_incomplete` |
| **Acceptance** | All contamination levels evaluated; directional instability separated |
| **Blockers** | Missing outlier evidence; distortion uncharacterized |
| **Runtime target** | `outlier_sensitivity_report` |
| **Priority** | P1 (restriction) |
| **Dependencies** | Positive-control and directional overlays on outlier fixtures |

---

## 12. Fold-geometry sensitivity requirements

| Field | Specification |
|-------|---------------|
| **Purpose** | Characterize K-fold count and layout diagnostic instability |
| **Risk tested** | Fold choice changes conclusions; leakage-blocked geometries used |
| **Fixture families** | Stable / imbalanced / sparse / leave-region-out; fold counts `{3, 5, 10}` |
| **Controls** | Geometry manifests cross-checked with leakage diagnostic runtime |
| **Diagnostics** | `fold_geometry_sensitivity_diagnostic`, `fold_imbalance_instability_diagnostic` |
| **Report field** | `fold_counts`, `geometry_risk_summary`, `fold_geometry_sensitivity_diagnostic` |
| **Acceptance** | All geometries evaluated; leakage-blocked remain blocked |
| **Blockers** | Missing fold-geometry evidence; blocked geometries not respected |
| **Runtime target** | `fold_geometry_sensitivity_report` |
| **Priority** | P0 (blocking component) |
| **Dependencies** | `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001` blocked geometry list |

---

## 13. Sparse/high-noise metric sensitivity requirements

| Field | Specification |
|-------|---------------|
| **Purpose** | Characterize sparse and high-noise metric panel behavior |
| **Risk tested** | Sparse/zero-inflated or high-noise KPIs produce false confidence |
| **Fixture families** | Metric density dense/sparse/zero-inflated; noise low/medium/high |
| **Controls** | Sparse KPI synthetic panels; D5 high-noise partitions |
| **Diagnostics** | `sparse_metric_sensitivity_diagnostic`, `high_noise_sensitivity_diagnostic` |
| **Report field** | `metric_density_levels`, `noise_regimes`, sub-report via `sparse_high_noise_metric_sensitivity_report` |
| **Acceptance** | All density and noise levels covered; instability flagged |
| **Blockers** | Missing sparse/high-noise evidence |
| **Runtime target** | `sparse_high_noise_metric_sensitivity_report` (optional future packet) |
| **Priority** | P1 (restriction) |
| **Dependencies** | Null-control and recovery overlays |

---

## 14. Seasonality/preperiod-fit sensitivity requirements

| Field | Specification |
|-------|---------------|
| **Purpose** | Characterize seasonal structure and weak pre-period fit effects |
| **Risk tested** | Misaligned seasonality or weak pre-fit drives wrong diagnostics |
| **Fixture families** | Seasonality none/aligned/misaligned; preperiod_fit strong/mixed/weak |
| **Controls** | Seasonal synthetic injections; weak-preperiod-fit D5 worlds |
| **Diagnostics** | `seasonality_sensitivity_diagnostic`, `preperiod_fit_sensitivity_diagnostic` |
| **Report field** | `seasonality_levels`, `preperiod_fit_levels`, sub-report via `seasonality_preperiod_fit_sensitivity_report` |
| **Acceptance** | All seasonality and pre-fit levels characterized |
| **Blockers** | Missing seasonality/preperiod-fit evidence |
| **Runtime target** | `seasonality_preperiod_fit_sensitivity_report` (optional future packet) |
| **Priority** | P1 (restriction) |
| **Dependencies** | Directional-error near-zero distinction |

---

## 15. Metric-scale sensitivity requirements

| Field | Specification |
|-------|---------------|
| **Purpose** | Characterize metric scale and variance regime effects |
| **Risk tested** | Skewed/heavy-tailed scales distort recovery and sign diagnostics |
| **Fixture families** | Metric scale normalized/skewed/heavy-tailed |
| **Controls** | Scale-transformed synthetic panels; D5 level-bias reference worlds |
| **Diagnostics** | `metric_scale_sensitivity_diagnostic` |
| **Report field** | `metric_scale_levels`, sub-report via `metric_scale_sensitivity_report` |
| **Acceptance** | All scale regimes characterized; estimand alignment noted |
| **Blockers** | Missing metric-scale evidence; estimand mismatch |
| **Runtime target** | `metric_scale_sensitivity_report` (optional future packet) |
| **Priority** | P1 (restriction) |
| **Dependencies** | Leads into `TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001` |

---

## 16. Aggregate/pooled geometry blocker requirements

| Field | Specification |
|-------|---------------|
| **Purpose** | Block or restrict aggregate/pooled readout paths without validation |
| **Risk tested** | Pooled geometry masks unit-level failures or induces bias |
| **Fixture families** | Unit-level / pooled / aggregate-stress geometries |
| **Controls** | Pooled vs unit-level replay on identical injected effects |
| **Diagnostics** | `aggregate_pooled_geometry_blocker_diagnostic` |
| **Report field** | `pooled_paths_validated`, `blocked_geometries`, `aggregate_pooled_geometry_blocker_diagnostic` |
| **Acceptance** | Pooled paths validated or explicitly blocked with rationale |
| **Blockers** | Unsupported aggregate/pooled geometry used without validation |
| **Runtime target** | `aggregate_pooled_geometry_blocker_report` |
| **Priority** | P0 (blocking component) |
| **Dependencies** | All prior families; fold-geometry and metric-scale |

---

## 17. Crossed-regime testing policy

| Tier | Policy |
|------|--------|
| **Tier 1** | Single-axis sweeps for each sensitivity family at default levels for other axes |
| **Tier 2** | Pre-declared high-risk pairs only (weak preperiod × high noise; small donor pool × severe outliers; imbalanced fold × sparse metrics; low regularization × high noise; pooled geometry × heterogeneous effects) |
| **Tier 3** | Blocked unless justified by observed Tier 1/Tier 2 failures |
| **Prohibited** | **Full factorial** crossing — explicitly blocked |

---

## 18. Fixture requirements

1. Every fixture requires `lineage_provenance_manifest` with seed, hash, regime tags, and battery overlay tags
2. Minimum ≥3 seeds per fixture family per sensitivity area
3. Each family includes one default/easy anchor cell
4. Null-control, directional-error, and positive-control scenarios referenced where relevant per family
5. Maximum 27 crossed cells per future evidence artifact
6. Leakage-blocked fold geometries must not appear in allowed fixture sets

---

## 19. Diagnostic metrics to be reported later

| Metric | Family |
|--------|--------|
| `donor_pool_sensitivity_diagnostic` | Donor pool |
| `donor_pool_shift_diagnostic` | Donor pool |
| `donor_quality_degradation_diagnostic` | Donor pool |
| `regularization_sensitivity_diagnostic` | Regularization |
| `regularization_overconstraint_diagnostic` | Regularization |
| `regularization_underconstraint_diagnostic` | Regularization |
| `outlier_sensitivity_diagnostic` | Outlier |
| `outlier_directional_instability_diagnostic` | Outlier |
| `fold_geometry_sensitivity_diagnostic` | Fold geometry |
| `fold_imbalance_instability_diagnostic` | Fold geometry |
| `sparse_metric_sensitivity_diagnostic` | Sparse/high-noise |
| `high_noise_sensitivity_diagnostic` | Sparse/high-noise |
| `seasonality_sensitivity_diagnostic` | Seasonality/preperiod |
| `preperiod_fit_sensitivity_diagnostic` | Seasonality/preperiod |
| `metric_scale_sensitivity_diagnostic` | Metric scale |
| `aggregate_pooled_geometry_blocker_diagnostic` | Aggregate/pooled |
| `crossed_regime_failure_rate_diagnostic` | Crossed regimes |
| `sensitivity_blocker_rate_diagnostic` | Bundle aggregate |

All metrics are **diagnostic-only** — not computed by this bundle.

---

## 20. Acceptance criteria by sensitivity family

| Family | Acceptance (future evidence) |
|--------|------------------------------|
| Donor pool | Size/quality/shift characterized; maps to `donor_pool_sensitivity_report` |
| Regularization | Alpha grid characterized; over/under-constraint separated |
| Outlier | Contamination levels characterized; directional instability separated |
| Fold geometry | All geometries evaluated; leakage blocks respected |
| Sparse/high-noise | Density and noise regimes covered |
| Seasonality/preperiod | Seasonality and pre-fit levels covered |
| Metric scale | Scale regimes covered; estimand noted |
| Aggregate/pooled | Pooled paths validated or blocked |

**Global:** Each family has fixture requirements and blocker rules; maps to promotion-review packets; crossed-regime scope bounded; diagnostic-only; no CI/significance/robustness claims.

---

## 21. Blocker criteria by sensitivity family

| Blocker | Trigger |
|---------|---------|
| Missing bundled sensitivity report | No umbrella `regime_sensitivity_report` with bundle reference |
| Missing donor-pool sensitivity evidence | `donor_pool_sensitivity_report` absent or incomplete |
| Missing regularization sensitivity evidence | `regularization_sensitivity_report` absent or incomplete |
| Missing outlier sensitivity evidence | `outlier_sensitivity_report` absent or incomplete |
| Missing fold-geometry sensitivity evidence | `fold_geometry_sensitivity_report` absent or incomplete |
| Missing sparse/high-noise metric evidence | Sub-report absent or incomplete |
| Missing seasonality/preperiod-fit evidence | Sub-report absent or incomplete |
| Missing metric-scale sensitivity evidence | Sub-report absent or incomplete |
| Unsupported aggregate/pooled geometry | Pooled path used without validation |
| Full-factorial uncontrolled exploration | Fixture scope violates Tier policy |
| Sensitivity interpreted as promotion/production support | Authorization boundary violation |
| Metric/estimand mismatch | Scale/aggregation inconsistency |
| Claim authorization boundary missing | No diagnostic-only framing |

Runtime: `METHOD_PROMOTION_REVIEW_BLOCKED_BY_REGIME_SENSITIVITY` when P0 components incomplete.

---

## 22. Runtime packet integration plan

**Umbrella:** `regime_sensitivity_report` references bundle and per-family status.

**Required reports:** `donor_pool_sensitivity_report`, `regularization_sensitivity_report`, `outlier_sensitivity_report`, `fold_geometry_sensitivity_report`, `aggregate_pooled_geometry_blocker_report`

**Optional future reports:** `sparse_high_noise_metric_sensitivity_report`, `seasonality_preperiod_fit_sensitivity_report`, `metric_scale_sensitivity_report`

```json
{
  "bundle_source": "TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001",
  "families_covered": 8,
  "regime_sensitivity_summary_diagnostic": null,
  "sensitivity_blocker_rate_diagnostic": null,
  "sensitivity_incomplete": false,
  "diagnostic_only": true,
  "evidence_generated": false
}
```

Integration via `generate_tbrridge_method_promotion_review()` and `detect_tbrridge_method_promotion_risks()`.

---

## 23. Allowed language

- **bundled sensitivity evidence audit**
- **diagnostic sensitivity requirements**
- **review-only sensitivity plan**
- **sensitivity blocker mapping**
- **future promotion-review input**
- **aggregate/pooled geometry blocker**

---

## 24. Prohibited language

- **validated robustness**
- **approved sensitivity behavior**
- **production-ready sensitivity**
- **confidence interval support**
- **p-value/significance support**
- **causal lift claim**
- **ROI claim**
- **method promotion evidence complete**
- **catalog unblock support**

---

## 25. Stop/go criteria

### Go

Proceed to `TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001` when bundle requirements adopted (no evidence generated).

### Stop

Stop when sensitivity evidence interpreted as robustness validation, production approval, significance support, or promotion-complete; full factorial attempted; aggregate/pooled paths authorized without validation.

---

## 26. Authorization boundary

**Allowed:** `tbrridge_sensitivity_evidence_audit_bundle_defined`, all eight `*_requirements_defined`, `crossed_regime_testing_policy_defined`, `runtime_packet_integration_defined`, `blocker_criteria_defined`

**Forbidden:** `sensitivity_evidence_generated`, `sensitivity_metrics_computed`, `simulations_implemented`, `robustness_validated`, `sensitivity_behavior_approved`, all inference/estimator/kfold/placebo flags, all promotion/production/uncertainty/CI/significance/lift/ROI/MMM/LLM flags

TBRRidge remains **RANK_0**, **BLOCKED**, **STAGE_2_DIAGNOSTIC_ONLY**.

---

## 27. Validation results

| Check | Result |
|-------|--------|
| Bundle document complete | Pass |
| Summary JSON valid | Pass |
| Governance tests | Pass |

---

## 28. Known limitations

- **Requirements only** — No sensitivity fixtures generated; no metrics computed
- **Eight standalone artifacts superseded** — IDs retained for report-key traceability only
- **Optional sub-reports** — Sparse/high-noise, seasonality/preperiod, metric-scale packets deferred to future evidence runtime
- **Metric-estimand alignment next** — Scale/estimand unification is `TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001`

---

## 29. Recommended next artifacts

| Role | Artifact |
|------|----------|
| **Primary** | `TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001` |
| **Alternative** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` |
| **Deferred** | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` |
| **Superseded (not executed separately)** | Eight standalone sensitivity audit IDs listed in section 1 |
