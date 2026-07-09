# TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` |
| **Artifact type** | `tbrridge_promotion_evidence_battery_plan` |
| **Status** | `completed` |
| **Scope** | `tbrridge_promotion_evidence_battery_planned_no_evidence_generated_or_promotion` |
| **Base commit** | `4334368` (Implement TBRRidge method promotion review runtime) |
| **Final verdict** | `tbrridge_promotion_evidence_battery_planned_no_evidence_generated_or_promotion` |

**Depends on:** `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001` · `TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001` · `TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001`

**Positive plan flags:** `tbrridge_promotion_evidence_battery_plan_defined` · `missing_evidence_inventory_defined` · `evidence_artifact_sequence_defined` · `fixture_requirements_defined` · `simulation_control_requirements_defined` · `acceptance_criteria_defined` · `runtime_packet_integration_plan_defined`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001_REPORT.md`
- `docs/track_d/archives/TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001_summary.json`
- `panel_exp/validation/tbrridge_method_promotion_review_runtime_001.py`
- `panel_exp/validation/tbrridge_method_promotion_review_contract_001.py`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001_REPORT.md`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001.md`
- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`

---

## 3. Current TBRRidge posture

| Layer | Posture |
|-------|---------|
| **Catalog rank** | `RANK_0` |
| **Catalog status** | `BLOCKED` |
| **Readiness stage** | `STAGE_2_DIAGNOSTIC_ONLY` |
| **Method promotion** | Not promoted |
| **Catalog unblock** | Not unblocked |
| **Production readiness** | Not production-ready |
| **Uncertainty approval** | Not uncertainty-approved |
| **Review machinery** | Method-promotion review contract + runtime complete |
| **Evidence batteries** | Not yet produced |

TBRRidge KFold has governed diagnostic scaffolding (leakage, placebo, coverage validation, uncertainty-candidate review) and method-promotion review machinery, but **no credible promotion evidence batteries** have been generated. This plan defines what must be produced before the method-promotion review runtime can receive non-blocking evidence packets.

---

## 4. Relationship to method-promotion review runtime

`TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001` (`generate_tbrridge_method_promotion_review`) evaluates **supplied** evidence packets against contract rules. It does not compute evidence. When required reports are missing or flagged incomplete, the runtime emits blockers such as:

- `METHOD_PROMOTION_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS`
- `METHOD_PROMOTION_REVIEW_BLOCKED_BY_FALSE_POSITIVE_EVIDENCE`
- `METHOD_PROMOTION_REVIEW_BLOCKED_BY_DIRECTIONAL_ERROR_EVIDENCE`
- `METHOD_PROMOTION_REVIEW_BLOCKED_BY_POSITIVE_CONTROL_RECOVERY`
- `METHOD_PROMOTION_REVIEW_BLOCKED_BY_REGIME_SENSITIVITY`
- `METHOD_PROMOTION_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH`
- `METHOD_PROMOTION_REVIEW_BLOCKED_BY_AGGREGATE_POOLED_GEOMETRY`

This plan converts those runtime gaps into an **ordered implementation roadmap** of audits, plans, simulations, fixtures, and report artifacts. Completing the plan does **not** generate evidence; it defines what future artifacts must produce.

---

## 5. Missing evidence inventory

Evidence already present (diagnostic chain — not re-planned here):

| Report key | Source |
|------------|--------|
| `method_promotion_evidence_audit_report` | `TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001` |
| `uncertainty_candidate_review_packet` | `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001` |
| `false_confidence_audit_report` | `TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001` |
| `leakage_diagnostic_report` | `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001` |
| `placebo_calibration_diagnostic_report` | `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001` |
| `coverage_validation_report` | `TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001` |
| `production_catalog_status_report` | Blocklist enforcement (KFold blocked) |
| `production_compatibility_boundary_report` | Platform contract only; TBRRidge-specific review deferred |

**Missing or incomplete evidence components** (this plan's scope):

| # | Component | Runtime report key | Priority | Gap severity |
|---|-----------|-------------------|----------|--------------|
| 1 | interval semantics | `interval_semantics_report` | P0 | Blocking |
| 2 | null-control false-positive behavior | `null_control_false_positive_report` | P0 | Blocking |
| 3 | directional-error behavior | `directional_error_report` | P0 | Blocking |
| 4 | positive-control recovery | `positive_control_recovery_report` | P0 | Blocking |
| 5 | regime sensitivity | `regime_sensitivity_report` | P0 | Blocking |
| 6 | donor-pool sensitivity | `donor_pool_sensitivity_report` | P1 | Restricted |
| 7 | regularization sensitivity | `regularization_sensitivity_report` | P1 | Restricted |
| 8 | outlier sensitivity | `outlier_sensitivity_report` | P1 | Restricted |
| 9 | fold-geometry sensitivity | `fold_geometry_sensitivity_report` | P0 | Blocking |
| 10 | metric/estimand alignment | `metric_estimand_alignment_report` | P0 | Blocking |
| 11 | aggregate/pooled geometry blocker | `aggregate_pooled_geometry_blocker_report` | P0 | Blocking |
| 12 | claim authorization boundary | `claim_authorization_boundary_report` | P0 | Blocking |
| 13 | production catalog boundary | `production_catalog_status_report` | P0 | Maintain block |
| 14 | downstream readout safety | `downstream_readout_safety_report` | P1 | Restricted |

---

## 6. Evidence battery design principles

1. **Supplied evidence only** — Future batteries produce report dicts consumed by `generate_tbrridge_method_promotion_review`; no runtime computes statistics at review time.
2. **D5-world anchored** — Synthetic and historical controls reuse D5-TRUST-TBRRIDGE-KFOLD worlds where possible; new worlds must declare lineage.
3. **Fail-closed** — Incomplete batteries block promotion review; partial batteries yield `READY_WITH_RESTRICTIONS` at best.
4. **No promotion by default** — Passing a battery audit does not promote TBRRidge or unblock catalog status.
5. **Ordered dependencies** — Interval semantics and null-control behavior must precede directional-error and recovery batteries.
6. **Aggregate/pooled remains blocked** — Batteries must confirm block, not seek unblock.
7. **Platform boundaries separate** — Claim authorization and production compatibility remain platform-governed; TBRRidge-specific boundary audits document method-local posture only.
8. **Deterministic manifests** — Each battery declares fixture IDs, world IDs, seed policy, and expected packet field shapes for assembly runtime.

---

## 7. Ordered evidence artifact sequence

| Order | Artifact | Produces report key | Depends on |
|-------|----------|---------------------|------------|
| 1 | `TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` | `interval_semantics_report` | D5 KFold replay, `INFERENCE_READOUT_SEMANTICS_001` |
| 2 | `TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001` | `null_control_false_positive_report` | Interval semantics audit |
| 3 | `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` | `directional_error_report` | Null-control audit |
| 4 | `TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001` | `positive_control_recovery_report` | Directional-error audit |
| 5 | `TBRRIDGE_REGIME_SENSITIVITY_PLAN_001` | `regime_sensitivity_report` | Positive-control audit |
| 6 | `TBRRIDGE_DONOR_POOL_SENSITIVITY_AUDIT_001` | `donor_pool_sensitivity_report` | Regime sensitivity plan |
| 7 | `TBRRIDGE_REGULARIZATION_SENSITIVITY_AUDIT_001` | `regularization_sensitivity_report` | Regime sensitivity plan |
| 8 | `TBRRIDGE_OUTLIER_SENSITIVITY_AUDIT_001` | `outlier_sensitivity_report` | Regime sensitivity plan |
| 9 | `TBRRIDGE_FOLD_GEOMETRY_SENSITIVITY_AUDIT_001` | `fold_geometry_sensitivity_report` | Regime + leakage diagnostics |
| 10 | `TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001` | `metric_estimand_alignment_report` | Interval semantics + D5 level-bias evidence |
| 11 | `TBRRIDGE_AGGREGATE_POOLED_GEOMETRY_BLOCKER_AUDIT_001` | `aggregate_pooled_geometry_blocker_report` | Metric/estimand alignment audit |
| 12 | `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` | `claim_authorization_boundary_report` | Aggregate blocker audit |
| 13 | `TBRRIDGE_DOWNSTREAM_READOUT_SAFETY_AUDIT_001` | `downstream_readout_safety_report` | Claim boundary audit |
| 14 | `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001` | Full promotion review input bundle | All prior audits complete |

---

## 8. Fixture requirements

| Fixture class | Purpose | Minimum set |
|---------------|---------|-------------|
| **D5 null worlds** | False-positive characterization | `null_zero`, `null_placebo`, `null_shock` (≥3 seeds each) |
| **D5 directional worlds** | Directional-error characterization | `dir_small_pos`, `dir_small_neg`, `dir_large_pos` |
| **D5 positive-control worlds** | Recovery characterization | `pos_known_lift_5pct`, `pos_known_lift_10pct` |
| **Regime manifests** | Sample-size / horizon / spend regimes | Small-N, medium-N, long-horizon, short-horizon |
| **Donor-pool variants** | Donor composition sensitivity | Tight pool, wide pool, sparse pool |
| **Regularization grid** | Ridge alpha sensitivity | `{0.01, 0.1, 1.0, 10.0}` documented grid |
| **Outlier injection** | Outlier-week sensitivity | Single-week spike, multi-week drift |
| **Fold geometry grid** | K-fold layout sensitivity | `{3, 5, 10}` folds; blocked vs allowed geometries |
| **Aggregate/pooled negative controls** | Confirm block | Multi-treated, pooled-lift, aggregate-TBR paths |
| **Lineage manifest template** | Provenance for all batteries | `run_id`, `world_id`, `seed`, `fixture_hash`, `policy_version` |

All fixtures must be versioned and referenced in `lineage_provenance_manifest` when attached to promotion review packets.

---

## 9. Simulation/control requirements

| Battery type | Synthetic controls | Historical controls | Output |
|--------------|-------------------|---------------------|--------|
| Interval semantics | KFold interval definition replay on D5 panels | None required initially | Semantics closure report |
| Null-control false-positive | Governed null worlds with declared FPR thresholds | D5 null replay | FPR summary per world |
| Directional-error | Signed-effect injection worlds | D5 directional diagnostics | Directional error rates |
| Positive-control recovery | Known-lift injection | D5 effect sweep subsets | Recovery pass/fail matrix |
| Regime sensitivity | Regime-tagged world grid | D5 regime partitions | Per-regime diagnostic status |
| Donor-pool sensitivity | Donor-pool swap manifests | Historical donor subsets | Sensitivity flags |
| Regularization sensitivity | Alpha grid replay | D5 alpha partial runs | Grid stability summary |
| Outlier sensitivity | Outlier injection manifests | Outlier-week historical slices | Sensitivity flags |
| Fold-geometry sensitivity | Fold-count / fold-layout grid | Leakage diagnostic cross-check | Geometry risk summary |
| Metric/estimand alignment | ATT vs level-percent crosswalk | D5 level-bias ~395%, sign ~35% | Alignment verdict |
| Aggregate/pooled blocker | Negative-control aggregate paths | False-confidence aggregate block | `aggregate_pooled_unsupported: true` |
| Claim authorization boundary | N/A (policy audit) | Claim authorization contract/runtime | TBRRidge-local boundary map |
| Downstream readout safety | N/A (policy audit) | Trusted readout / claim runtime | Readout safety posture |

**No simulations are implemented by this plan.** Each row defines requirements for future audit/runtime artifacts.

---

## 10. Acceptance criteria by evidence component

### 10.1 Interval semantics

| Field | Specification |
|-------|---------------|
| **Purpose** | Close KFold interval centering, width, and estimand semantics for promotion review |
| **Question answered** | Are TBRRidge KFold interval semantics defined, consistent, and non-contradictory? |
| **Required fixtures** | D5 KFold replay panels; interval definition manifest |
| **Required controls** | Synthetic panels with known ATT and level-percent ground truth |
| **Expected output artifact** | `TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` report + `interval_semantics_report` dict |
| **Expected packet fields** | `centering`, `width_semantics`, `estimand_id`, `semantics_undefined: false`, `interval_semantics_incomplete: false` |
| **Acceptance criteria** | All required semantics fields populated; no undefined centering; estimand documented |
| **Blocker criteria** | `semantics_undefined: true` or `interval_semantics_incomplete: true` |
| **Runtime integration target** | `interval_semantics_report` → `generate_tbrridge_method_promotion_review` |
| **Priority** | P0 |
| **Dependency order** | 1 |

### 10.2 Null-control false-positive behavior

| Field | Specification |
|-------|---------------|
| **Purpose** | Characterize false-positive rate under governed null worlds |
| **Question answered** | Does TBRRidge KFold maintain acceptable null-control false-positive behavior? |
| **Required fixtures** | D5 null worlds (≥3 types × ≥3 seeds) |
| **Required controls** | Pure null synthetic panels; placebo-shift nulls |
| **Expected output artifact** | `TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001` + `null_control_false_positive_report` |
| **Expected packet fields** | `worlds`, `fpr_summary`, `evidence_incomplete: false`, `null_control_false_positive_incomplete: false` |
| **Acceptance criteria** | All declared null worlds evaluated; FPR within documented thresholds or explicitly flagged |
| **Blocker criteria** | Missing worlds; `evidence_incomplete: true` |
| **Runtime integration target** | `null_control_false_positive_report` |
| **Priority** | P0 |
| **Dependency order** | 2 (after interval semantics) |

### 10.3 Directional-error behavior

| Field | Specification |
|-------|---------------|
| **Purpose** | Characterize sign/direction error under signed-effect worlds |
| **Question answered** | Does TBRRidge KFold avoid systematic directional errors? |
| **Required fixtures** | D5 directional worlds; signed synthetic injections |
| **Required controls** | Small positive, small negative, large positive effect worlds |
| **Expected output artifact** | `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` + `directional_error_report` |
| **Expected packet fields** | `directional_error_rate`, `worlds`, `evidence_incomplete: false` |
| **Acceptance criteria** | Directional error rates documented per world; thresholds declared |
| **Blocker criteria** | `directional_error_evidence_incomplete: true` |
| **Runtime integration target** | `directional_error_report` |
| **Priority** | P0 |
| **Dependency order** | 3 |

### 10.4 Positive-control recovery

| Field | Specification |
|-------|---------------|
| **Purpose** | Verify recovery of known positive effects |
| **Question answered** | Does TBRRidge KFold recover injected positive controls within tolerance? |
| **Required fixtures** | D5 positive-control worlds; known-lift synthetic panels |
| **Required controls** | 5% and 10% known-lift worlds |
| **Expected output artifact** | `TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001` + `positive_control_recovery_report` |
| **Expected packet fields** | `worlds`, `recovery_pass_matrix`, `recovery_failure: false` |
| **Acceptance criteria** | Recovery documented per world; failures explicitly listed |
| **Blocker criteria** | `positive_control_recovery_incomplete: true` or `recovery_failure: true` without remediation plan |
| **Runtime integration target** | `positive_control_recovery_report` |
| **Priority** | P0 |
| **Dependency order** | 4 |

### 10.5 Regime sensitivity

| Field | Specification |
|-------|---------------|
| **Purpose** | Document sensitivity across sample-size, horizon, and spend regimes |
| **Question answered** | Is TBRRidge KFold behavior stable across declared regimes? |
| **Required fixtures** | Regime manifests (small-N, medium-N, long/short horizon) |
| **Required controls** | Regime-tagged D5 partitions |
| **Expected output artifact** | `TBRRIDGE_REGIME_SENSITIVITY_PLAN_001` + `regime_sensitivity_report` |
| **Expected packet fields** | `regimes`, `per_regime_status`, `sensitivity_incomplete: false` |
| **Acceptance criteria** | All declared regimes evaluated; instability flagged not hidden |
| **Blocker criteria** | `regime_sensitivity_incomplete: true` |
| **Runtime integration target** | `regime_sensitivity_report` |
| **Priority** | P0 |
| **Dependency order** | 5 |

### 10.6 Donor-pool sensitivity

| Field | Specification |
|-------|---------------|
| **Purpose** | Document donor-pool composition sensitivity |
| **Question answered** | Does donor-pool choice materially affect KFold conclusions? |
| **Required fixtures** | Tight, wide, sparse donor-pool variants |
| **Required controls** | Donor-swap synthetic manifests |
| **Expected output artifact** | `TBRRIDGE_DONOR_POOL_SENSITIVITY_AUDIT_001` + `donor_pool_sensitivity_report` |
| **Expected packet fields** | `pool_variants`, `sensitivity_incomplete: false` |
| **Acceptance criteria** | All pool variants documented; material sensitivity flagged |
| **Blocker criteria** | `donor_pool_sensitivity_incomplete: true` (yields restrictions, not hard block if other P0 clear) |
| **Runtime integration target** | `donor_pool_sensitivity_report` |
| **Priority** | P1 |
| **Dependency order** | 6 |

### 10.7 Regularization sensitivity

| Field | Specification |
|-------|---------------|
| **Purpose** | Document ridge-alpha sensitivity |
| **Question answered** | Are KFold conclusions stable across regularization grid? |
| **Required fixtures** | Alpha grid `{0.01, 0.1, 1.0, 10.0}` |
| **Required controls** | D5 alpha partial replays |
| **Expected output artifact** | `TBRRIDGE_REGULARIZATION_SENSITIVITY_AUDIT_001` + `regularization_sensitivity_report` |
| **Expected packet fields** | `alpha_grid`, `stability_summary`, `sensitivity_incomplete: false` |
| **Acceptance criteria** | Full grid evaluated; instability documented |
| **Blocker criteria** | `regularization_sensitivity_incomplete: true` |
| **Runtime integration target** | `regularization_sensitivity_report` |
| **Priority** | P1 |
| **Dependency order** | 7 |

### 10.8 Outlier sensitivity

| Field | Specification |
|-------|---------------|
| **Purpose** | Document outlier-week sensitivity |
| **Question answered** | Do outlier weeks materially distort KFold readouts? |
| **Required fixtures** | Single-week spike; multi-week drift injections |
| **Required controls** | Outlier-tagged historical slices |
| **Expected output artifact** | `TBRRIDGE_OUTLIER_SENSITIVITY_AUDIT_001` + `outlier_sensitivity_report` |
| **Expected packet fields** | `outlier_scenarios`, `sensitivity_incomplete: false` |
| **Acceptance criteria** | All scenarios evaluated; distortion flagged |
| **Blocker criteria** | `outlier_sensitivity_incomplete: true` |
| **Runtime integration target** | `outlier_sensitivity_report` |
| **Priority** | P1 |
| **Dependency order** | 8 |

### 10.9 Fold-geometry sensitivity

| Field | Specification |
|-------|---------------|
| **Purpose** | Document K-fold count and layout sensitivity |
| **Question answered** | Is KFold behavior stable across fold geometries? |
| **Required fixtures** | Fold grid `{3, 5, 10}`; blocked geometries from leakage diagnostic |
| **Required controls** | Geometry manifests cross-checked with leakage runtime |
| **Expected output artifact** | `TBRRIDGE_FOLD_GEOMETRY_SENSITIVITY_AUDIT_001` + `fold_geometry_sensitivity_report` |
| **Expected packet fields** | `fold_counts`, `geometry_risk_summary`, `sensitivity_incomplete: false` |
| **Acceptance criteria** | All geometries evaluated; leakage-blocked geometries remain blocked |
| **Blocker criteria** | `fold_geometry_sensitivity_incomplete: true` |
| **Runtime integration target** | `fold_geometry_sensitivity_report` |
| **Priority** | P0 |
| **Dependency order** | 9 |

### 10.10 Metric/estimand alignment

| Field | Specification |
|-------|---------------|
| **Purpose** | Close metric/estimand alignment for promotion review |
| **Question answered** | Are point estimates and intervals aligned to declared estimand? |
| **Required fixtures** | ATT vs level-percent crosswalk panels |
| **Required controls** | D5 level-bias and sign-accuracy evidence |
| **Expected output artifact** | `TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001` + `metric_estimand_alignment_report` |
| **Expected packet fields** | `estimand_id`, `metric_estimand_mismatch: false`, `alignment_verdict` |
| **Acceptance criteria** | Estimand documented; mismatch explicitly resolved or blocked |
| **Blocker criteria** | `metric_estimand_mismatch: true` |
| **Runtime integration target** | `metric_estimand_alignment_report` |
| **Priority** | P0 |
| **Dependency order** | 10 |

### 10.11 Aggregate/pooled geometry blocker

| Field | Specification |
|-------|---------------|
| **Purpose** | Confirm aggregate/pooled paths remain blocked for TBRRidge KFold |
| **Question answered** | Are aggregate/pooled geometries correctly blocked? |
| **Required fixtures** | Multi-treated, pooled-lift, aggregate-TBR negative controls |
| **Required controls** | False-confidence aggregate block cases |
| **Expected output artifact** | `TBRRIDGE_AGGREGATE_POOLED_GEOMETRY_BLOCKER_AUDIT_001` + `aggregate_pooled_geometry_blocker_report` |
| **Expected packet fields** | `aggregate_pooled_unsupported: true`, `blocked_geometries` |
| **Acceptance criteria** | All aggregate/pooled paths documented as unsupported |
| **Blocker criteria** | Any aggregate path marked supported |
| **Runtime integration target** | `aggregate_pooled_geometry_blocker_report` |
| **Priority** | P0 |
| **Dependency order** | 11 |

### 10.12 Claim authorization boundary

| Field | Specification |
|-------|---------------|
| **Purpose** | Map TBRRidge-local claim authorization posture |
| **Question answered** | Which claim types remain blocked for TBRRidge KFold? |
| **Required fixtures** | N/A (policy audit) |
| **Required controls** | Claim authorization contract/runtime crosswalk |
| **Expected output artifact** | `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` + `claim_authorization_boundary_report` |
| **Expected packet fields** | `allowed_claims`, `blocked_claims`, `boundary_missing: false` |
| **Acceptance criteria** | All promotion/prod/uncertainty claims explicitly blocked |
| **Blocker criteria** | `claim_authorization_boundary_missing: true` |
| **Runtime integration target** | `claim_authorization_boundary_report` |
| **Priority** | P0 |
| **Dependency order** | 12 |

### 10.13 Production catalog boundary

| Field | Specification |
|-------|---------------|
| **Purpose** | Document and maintain TBRRidge KFold catalog block |
| **Question answered** | Is production catalog block correctly enforced? |
| **Required fixtures** | N/A (status audit) |
| **Required controls** | Production catalog blocklist enforcement |
| **Expected output artifact** | Existing `production_catalog_status_report` reaffirmed |
| **Expected packet fields** | `catalog_blocked: true`, `catalog_rank: RANK_0` |
| **Acceptance criteria** | Block active; no unblock path without separate governance |
| **Blocker criteria** | `catalog_unblocked: true` without authorization |
| **Runtime integration target** | `production_catalog_status_report` |
| **Priority** | P0 |
| **Dependency order** | Maintained throughout |

### 10.14 Downstream readout safety

| Field | Specification |
|-------|---------------|
| **Purpose** | Document downstream readout safety posture for TBRRidge |
| **Question answered** | Are production readout paths safely blocked? |
| **Required fixtures** | N/A (policy audit) |
| **Required controls** | Trusted readout / claim runtime crosswalk |
| **Expected output artifact** | `TBRRIDGE_DOWNSTREAM_READOUT_SAFETY_AUDIT_001` + `downstream_readout_safety_report` |
| **Expected packet fields** | `readout_paths_blocked`, `safety_incomplete: false` |
| **Acceptance criteria** | All production readout paths documented as blocked |
| **Blocker criteria** | `downstream_readout_safety_incomplete: true` |
| **Runtime integration target** | `downstream_readout_safety_report` |
| **Priority** | P1 |
| **Dependency order** | 13 |

---

## 11. Stop/go criteria

### Go criteria (future battery completion — does not promote TBRRidge)

Proceed to `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001` when:

1. All P0 evidence components (1–5, 9–12) have completed audits with non-blocking reports
2. `interval_semantics_report` has `semantics_undefined: false` and `interval_semantics_incomplete: false`
3. Null-control, directional-error, positive-control, and regime batteries pass documented thresholds
4. Metric/estimand alignment reports `metric_estimand_mismatch: false`
5. Aggregate/pooled geometry reports `aggregate_pooled_unsupported: true` (block confirmed)
6. Uncertainty-candidate review packet remains non-blocking
7. Production catalog remains `BLOCKED` / `RANK_0`
8. `generate_tbrridge_method_promotion_review` returns `READY_FOR_RESTRICTED_REVIEW` or `READY_WITH_RESTRICTIONS` on assembled bundle

### Stop criteria

Stop and do not advance when:

1. Interval semantics remain undefined or incomplete
2. Null-control false-positive evidence incomplete
3. Metric/estimand mismatch unresolved
4. Aggregate/pooled geometry incorrectly marked supported
5. Uncertainty-candidate review blocking
6. Any attempt to set promotion, catalog-unblock, or production-authorization flags to an authorized state
7. Production compatibility review attempted before P0 batteries complete

---

## 12. Runtime packet integration plan

1. Each completed battery audit emits a report dict matching contract `REQUIRED_EVIDENCE` keys
2. `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001` (future) collects reports into a single input bundle
3. Bundle passed to `generate_tbrridge_method_promotion_review(input_bundle)`
4. Runtime evaluates presence flags via `build_evidence_presence` and risks via `detect_tbrridge_method_promotion_risks`
5. Status delegated to `evaluate_method_promotion_review` in contract module
6. Failure packets emitted per contract failure codes when blocking
7. `lineage_provenance_manifest` aggregates fixture/world lineage from all batteries
8. Deterministic `review_id` and `provenance_hash` computed by runtime (no recomputation of statistics)

**Integration test target (future):** Assembled bundle → `METHOD_PROMOTION_REVIEW_READY_FOR_RESTRICTED_REVIEW` with all forbidden authorization flags false.

---

## 13. Governance registry integration plan

| Registry action | Detail |
|-----------------|--------|
| Investigation | `INV-TBRRIDGE-PROMOTION-EVIDENCE-BATTERY-PLAN-001` → RESOLVED |
| Lane | `TBRRIDGE-PROMOTION-EVIDENCE-BATTERY-PLAN-001` → complete |
| Next artifact | `TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` |
| Alternative | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` |
| Deferred | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` |
| MIP audit registry | New section for battery plan |
| Roadmap | Mark plan complete; next = interval semantics audit |

---

## 14. Risks and known limitations

- **D5 replay dependency** — Batteries assume D5-TRUST-TBRRIDGE-KFOLD worlds remain valid; world drift requires re-baselining
- **No empirical evidence in this plan** — Plan only; no simulations run
- **P1 gaps allow restrictions** — Donor-pool, regularization, outlier, downstream safety gaps yield `READY_WITH_RESTRICTIONS`, not promotion
- **Platform vs method boundaries** — Claim authorization and production compatibility are platform-governed; TBRRidge audits document local posture only
- **Production compatibility deferred** — Separate lane until STAGE_6 / RANK_4 candidate exists
- **Historical evidence partial** — D5 level-bias and sign-accuracy data inform but do not close metric/estimand alignment alone

---

## 15. Authorization boundary

**Allowed (true):** `tbrridge_promotion_evidence_battery_plan_defined`, `missing_evidence_inventory_defined`, `evidence_artifact_sequence_defined`, `fixture_requirements_defined`, `simulation_control_requirements_defined`, `acceptance_criteria_defined`, `runtime_packet_integration_plan_defined`

**Forbidden (false):** `evidence_generated`, `simulations_implemented`, `promotion_evidence_runtime_implemented`, `method_promoted`, `method_unblocked`, `method_promotion_authorized`, `production_catalog_unblocked`, `production_compatibility_authorized`, `production_authorization_granted`, `production_readout_authorized`, `uncertainty_candidate_approved`, `uncertainty_authorized`, all CI/p-value/significance/coverage/inference/computation/lift/ROI/MMM/LLM flags

TBRRidge remains **RANK_0**, **BLOCKED**, **STAGE_2_DIAGNOSTIC_ONLY**, not promoted, not catalog-unblocked, not production-ready, not uncertainty-approved.

---

## 16. Validation results

| Check | Result |
|-------|--------|
| Plan document complete | Pass |
| Summary JSON valid | Pass |
| Governance tests | Pass |
| `failed_scenarios` | `[]` |

---

## 17. Recommended next artifacts

| Role | Artifact |
|------|----------|
| **Primary** | `TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` |
| **Alternative** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` |
| **Deferred** | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` |
| **Terminal assembly** | `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001` (after all battery audits) |
