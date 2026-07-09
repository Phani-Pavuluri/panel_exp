# METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001` |
| **Artifact type** | `method_instrument_classification_policy` |
| **Status** | `completed` |
| **Scope** | `method_instrument_classification_policy_defined_no_method_promotion_or_catalog_unblock` |
| **Base commit** | `1c29589` (Add TBRRidge metric estimand alignment audit) |
| **Final verdict** | `method_instrument_classification_policy_defined_no_method_promotion_or_catalog_unblock` |

**Depends on:** `TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001` · `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001` · `TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` · `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001`

**Positive policy flags:** `method_instrument_classification_policy_defined` · `governed_instrument_identity_defined` · `classification_tiers_defined` · `evidence_inheritance_rules_defined` · `estimator_family_promotion_prohibited` · `instrument_level_promotion_required` · `pairing_specific_validation_required` · `catalog_triage_audit_recommended`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001.md`
- `docs/track_d/TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001.md`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001_REPORT.md`
- `docs/track_d/METHOD_PROMOTION_CANDIDATE_AUDIT_001.md`
- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`
- `docs/TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`
- `docs/track_d/TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001.md`

---

## 3. Policy purpose

Define platform-wide rules for **governed instrument identity**, **classification tiers**, **evidence inheritance**, and **promotion boundaries** so that validation and promotion apply to **exact method instruments**, not estimator families globally.

**Core principle:** Promote instruments, not estimator families.

---

## 4. Architecture correction

Recent TBRRidge work revealed that estimator-family-level validation and promotion paths are architecturally incorrect.

| Prior (incorrect) | Corrected |
|-----------------|-----------|
| "TBRRidge is characterized" | TBRRidge + KFold + single-cell + diagnostic interval is characterized |
| "SCM is production-ready" | SCM + Jackknife + null-monitor is restricted-review only |
| Family-level promotion batteries | Instrument-specific promotion batteries |
| Inference evidence transfers across families | Inference evidence is pairing-specific |

This policy codifies the correction for all modalities and estimator families.

---

## 5. Governed instrument identity

The canonical governed unit comprises:

| Field | Description |
|-------|-------------|
| `modality` | Experiment paradigm (e.g., `geo`) |
| `estimator_family` | Point-estimation family (e.g., `tbrridge`, `scm`, `augsynth`, `did`) |
| `inference_family` | Uncertainty procedure (e.g., `kfold`, `placebo`, `jackknife`, `bootstrap`) |
| `geometry` | Assignment/readout shape (e.g., `single_cell`, `single_treated`, `null_monitor`) |
| `estimand` | Declared estimand (e.g., `delta_mu`, `relative_att_post`) |
| `interval_semantics` | Uncertainty meaning (e.g., `diagnostic_interval`, `placebo_tail`, `delete_one_diagnostic`) |
| `metric_scope` | Metric and geography scope |
| `treatment_contrast` | Treatment vs control definition |
| `allowed_surface` | Governed claim surface |

**Conceptual identity format:**

```
{modality}.{estimator_family}.{inference_family}.{geometry}.{estimand}.{interval_semantics}.{surface}
```

**Example identities:**

| Identity | Meaning |
|----------|---------|
| `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` | TBRRidge KFold single-cell diagnostic interval |
| `geo.tbrridge.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only` | TBRRidge Placebo single-treated diagnostic |
| `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review` | SCM Jackknife null-monitor restricted review |
| `geo.scm.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only` | SCM Placebo single-treated diagnostic |
| `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only` | AugSynth JK research-only |
| `geo.did.bootstrap.panel_delta.bootstrap_interval.diagnostic_only` | DID Bootstrap diagnostic readout |

---

## 6. Why estimator-family promotion is prohibited

1. **Inference semantics differ** — KFold leakage rules ≠ Placebo pool validity ≠ Jackknife leverage
2. **Geometry differs** — single-treated ≠ multi-treated ≠ null-monitor
3. **Interval semantics differ** — diagnostic interval ≠ placebo tail ≠ delete-one band
4. **Evidence batteries differ** — TBRRidge KFold battery ≠ TBRRidge Placebo battery
5. **False confidence risk** — family-level promotion hides wrong-inference or wrong-geometry authorization

**Rule:** No catalog row, audit, or runtime may authorize promotion of an estimator family without an exact instrument identity.

---

## 7. Classification tiers

| Tier | Meaning |
|------|---------|
| **PROMOTION_CANDIDATE** | Selected exact instrument may enter full promotion evidence path; still not promoted until runtime/review passes |
| **RESTRICTED_REVIEW** | Review-only or diagnostic summaries under strict claim boundaries |
| **DIAGNOSTIC_ONLY** | Stress tests, triangulation, calibration, warnings; no promotion path by default |
| **RESEARCH_SANDBOX** | Exploratory only; no governed downstream claim surface |
| **BLOCKED** | Prohibited for governed surfaces |
| **DEPRECATED** | Lineage/backward compatibility only; not for new use |

Tiers map to but do not replace ladder stages in `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001`. Tier is **instrument-specific**; ladder stage may differ across instruments within the same estimator family.

---

## 8. Evidence inheritance rules

Three evidence classes:

### Class 1 — Estimator-level reusable evidence

Reusable **only** when metric, geography, contrast, and time window match:

- Point-estimate recovery design patterns
- Metric/estimand alignment structure
- Donor-pool sensitivity structure
- Claim-boundary language patterns

### Class 2 — Inference-family-specific evidence

**Non-transferable** across inference families:

- KFold leakage / fold geometry
- Placebo pool validity / tail calibration
- Jackknife leverage / delete-one instability
- Bootstrap/BRB resampling dependence assumptions
- Conformal exchangeability / score calibration

### Class 3 — Instrument-specific non-transferable evidence

- Exact interval semantics
- Allowed surfaces
- Geometry-specific blockers
- Aggregation/pooled support
- Production compatibility
- Promotion eligibility

**Hard rules:**

1. Evidence from one inference family cannot promote another inference family
2. Evidence from one geometry cannot authorize another geometry
3. Evidence from diagnostic surfaces cannot authorize production surfaces
4. Estimator-family names cannot be promoted globally
5. Promotion applies only to exact cataloged instrument identities
6. Unsupported surfaces are blocked by default
7. All evidence inheritance must be explicit and recorded

---

## 9. Promotion eligibility rules

An instrument may enter **PROMOTION_CANDIDATE** tier only when:

1. Exact instrument identity is cataloged
2. Classification tier explicitly set to `PROMOTION_CANDIDATE`
3. Full instrument-specific evidence battery defined (if applicable)
4. Pairing-specific validation requirements satisfied or planned
5. No BLOCKED or DEPRECATED flags on the identity
6. Method promotion review runtime accepts instrument-scoped evidence packet

**Promotion** (catalog unblock, production authorization) requires additional runtime gates beyond this policy. This policy defines eligibility only.

---

## 10. Required catalog fields

Every governed instrument catalog row must include:

| Field | Required |
|-------|----------|
| `instrument_identity` | Full canonical identity string |
| `classification_tier` | One of six tiers |
| `ladder_stage` | Cross-reference to evidence ladder |
| `catalog_rank` | RANK_0–RANK_4 |
| `catalog_status` | BLOCKED / RESTRICTED / etc. |
| `allowed_surfaces` | Explicit list |
| `blocked_surfaces` | Explicit list |
| `evidence_battery_id` | Instrument-specific battery reference |
| `evidence_inheritance_manifest` | Explicit reusable vs non-transferable evidence |
| `pairing_validation_requirements` | Inference/geometry-specific checks |
| `interval_semantics_id` | Interval meaning reference |
| `estimand_id` | Registry crosswalk |
| `lineage_provenance` | Audit artifact references |

---

## 11. Allowed/prohibited surfaces by tier

| Tier | Allowed surfaces | Prohibited surfaces |
|------|------------------|---------------------|
| **PROMOTION_CANDIDATE** | Restricted review; promotion evidence assembly | Production readout; catalog unblock (until review passes) |
| **RESTRICTED_REVIEW** | Diagnostic summaries; review-only falsification | Production claims; uncertainty approval |
| **DIAGNOSTIC_ONLY** | Stress tests; triangulation; calibration warnings | Promotion path; production claims |
| **RESEARCH_SANDBOX** | Offline exploration | Any governed downstream claim |
| **BLOCKED** | None on governed surfaces | All governed surfaces |
| **DEPRECATED** | Lineage lookup only | New experiments; promotion |

---

## 12. Pairing-specific validation requirements

| Pairing | Required validation |
|---------|---------------------|
| TBRRidge + KFold | Leakage diagnostic, fold geometry, interval semantics, sensitivity bundle |
| TBRRidge + Placebo | Placebo pool validity, tail calibration, single-treated geometry |
| SCM + Jackknife | Delete-one stability, null-monitor semantics, leverage diagnostics |
| SCM + Placebo | Placebo pool, single-treated geometry, null FPR |
| AugSynth + JK | Research interval semantics, CVXPY reliability, spillover risk |
| DID + Bootstrap | Randomization suitability, estimand unification, diagnostic-only interval |

Validation requirements are **per instrument identity**, not per estimator family.

---

## 13. Reusable evidence framework

Reusable evidence must declare:

1. Source instrument identity
2. Target instrument identity
3. Matching dimensions (metric, geography, contrast, time window)
4. Evidence class (estimator-level only)
5. Explicit inheritance approval record

Without inheritance manifest entry, evidence is **instrument-local only**.

---

## 14. Non-reusable inference evidence

The following never inherit across inference families:

- Interval semantics audits
- Null-control false-positive characterization
- Directional-error characterization
- Positive-control recovery characterization
- Sensitivity bundle results
- Leakage / placebo / jackknife / bootstrap diagnostics
- Coverage validation results

Each inference pairing requires its own evidence path.

---

## 15. Roadmap impact

1. TBRRidge promotion evidence battery applies to **`geo.tbrridge.kfold.*`** identity only
2. New instruments require separate batteries or explicit inheritance manifests
3. `METHOD_PROMOTION_CANDIDATE_AUDIT_001` rankings must reference instrument identities
4. `TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001` remains architecture authority; this policy adds **classification tier** and **evidence inheritance** governance
5. Future catalog triage audit assigns tiers to all catalog rows

---

## 16. Required next triage audit

`METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` must:

1. Inventory all catalog instrument rows
2. Assign classification tier per identity
3. Document evidence inheritance manifests
4. Flag family-level promotion language for removal
5. Map pairing-specific validation requirements
6. Produce triage report without promoting any instrument

---

## 17. Stop/go criteria

### Go

Proceed to `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` when policy requirements adopted.

### Stop

Stop when:

1. Estimator-family promotion attempted without instrument identity
2. Inference evidence transferred without inheritance manifest
3. Diagnostic surface evidence used for production authorization
4. Unsupported surface authorized by default
5. Classification tier omitted from catalog row

---

## 18. Authorization boundary

**Allowed:** `method_instrument_classification_policy_defined`, `governed_instrument_identity_defined`, `classification_tiers_defined`, `evidence_inheritance_rules_defined`, `estimator_family_promotion_prohibited`, `instrument_level_promotion_required`, `pairing_specific_validation_required`, `catalog_triage_audit_recommended`

**Forbidden:** `method_promoted`, `method_unblocked`, `estimator_family_promoted`, `global_tbrridge_promotion_authorized`, all production/uncertainty/CI/significance/lift/ROI/inference/estimator/simulation/MMM/LLM flags

No instrument is promoted, unblocked, or production-authorized by this policy.

---

## 19. Validation results

| Check | Result |
|-------|--------|
| Policy document complete | Pass |
| Summary JSON valid | Pass |
| Governance tests | Pass |

---

## 20. Known limitations

- **Policy only** — No catalog rows re-tiered; triage deferred to next audit
- **TBRRidge-heavy examples** — Illustrative; policy applies platform-wide
- **Track B catalog** — Architecture reference; triage audit harmonizes rows
- **Promotion runtime** — Existing runtimes may require instrument-scoped packet updates in future artifacts

---

## 21. Recommended next artifacts

| Role | Artifact |
|------|----------|
| **Primary** | `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` |
| **Alternative** | `TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001` |
| **Deferred** | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` |
| **TBRRidge lane (continuing)** | `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` |
