# METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` |
| **Artifact type** | `method_instrument_catalog_triage_audit` |
| **Status** | `completed` |
| **Scope** | `method_instrument_catalog_triaged_no_method_promotion_or_catalog_unblock` |
| **Base commit** | `0188b04` (Add method instrument classification policy) |
| **Final verdict** | `method_instrument_catalog_triaged_no_method_promotion_or_catalog_unblock` |

**Depends on:** `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001` · `TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001` · `TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001` · `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001` · `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001`

**Positive audit flags:** `method_instrument_catalog_triage_audit_completed` · `classification_policy_applied` · `instrument_triage_matrix_defined` · `evidence_inheritance_matrix_defined` · `roadmap_correction_defined` · `exact_instrument_id_required_for_future_promotion` · `estimator_family_global_promotion_blocked`

---

## 2. Source files inspected

- `docs/track_d/METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001.md`
- `docs/track_d/archives/METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001_summary.json`
- `docs/TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`
- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`
- `docs/track_d/METHOD_PROMOTION_CANDIDATE_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001_REPORT.md`
- `docs/track_d/TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001.md`
- `docs/track_d/TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001.md`
- `docs/track_d/TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001.md`
- `docs/ROADMAP_V4.md` · `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md` · `docs/MIP_AUDIT_REGISTRY.md`
- `docs/governance/OPEN_INVESTIGATIONS_001.json`

---

## 3. Audit purpose

Apply `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001` to the current method/instrument catalog and roadmap. Classify known estimator + inference + geometry pairings into governed classification tiers, document evidence inheritance manifests, and correct roadmap language that implies global estimator-family promotion.

**Core principle:** Every pairing should be classified, but only selected exact instruments should proceed into full validation. This audit prevents global estimator-family promotion and roadmap explosion.

---

## 4. Classification policy applied

| Policy element | Application in this audit |
|----------------|---------------------------|
| Governed instrument identity (9 fields) | All triage rows use policy identity format |
| Six classification tiers | Assigned per instrument below |
| Three-class evidence inheritance | Documented in §14 matrix |
| Estimator-family promotion prohibited | Family-level promotion language flagged for removal |
| Instrument-level promotion required | Future contracts/runtimes must name exact instrument ID |
| Unsupported surfaces blocked by default | Non-selected pairings marked diagnostic/research/blocked |

---

## 5. Current catalog posture

| Source | Posture |
|--------|---------|
| **Track B catalog** | 9 primary geo instruments + registered unsupported entries |
| **Promotion candidate audit** | RANK_0–RANK_4 taxonomy; no RANK_4 candidates |
| **TBRRidge lane** | `geo.tbrridge.kfold.*` scoped; RANK_0 / BLOCKED / STAGE_2_DIAGNOSTIC_ONLY |
| **Production blocklist** | Enforced; nominal eligibility excludes most inference paths |
| **This audit** | Assigns classification tiers; **does not change catalog status or ranks** |

---

## 6. Instrument identity rule

Canonical governed unit (from classification policy):

`modality` + `estimator_family` + `inference_family` + `geometry` + `estimand` + `interval_semantics` + `metric_scope` + `treatment_contrast` + `allowed_surface`

**Policy identity format:**

```
{modality}.{estimator_family}.{inference_family}.{geometry}.{estimand}.{interval_semantics}.{surface}
```

**Track B crosswalk:** Track B uses a longer legacy format (`relative_att_post`, `multi_treated_default`, `confidence_interval`). This audit maps Track B aliases to policy identities where evidence exists. Where policy identity differs from Track B row, both are recorded; policy identity is authoritative for future promotion contracts.

---

## 7. Triage classification matrix

| Policy instrument identity | Track B alias / catalog row | Catalog rank | Classification tier | Notes |
|----------------------------|----------------------------|--------------|---------------------|-------|
| `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` | `TBRRidge_Kfold` | RANK_0 / blocked | **RESTRICTED_REVIEW** | Promotion-candidate path for **diagnostic surfaces only**; not production |
| `geo.tbrridge.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only` | `TBRRidge_Placebo` | RANK_2 | **DIAGNOSTIC_ONLY** | Placebo calibration support; secondary to SCM Placebo |
| `geo.tbrridge.brb.single_cell.delta_mu.resampling_diagnostic.research_or_restricted` | `TBRRidge_BlockResidualBootstrap` | RANK_0 / blocked | **RESEARCH_SANDBOX** | Research or restricted only until dependence assumptions validated |
| `geo.tbrridge.jackknife.single_cell.delta_mu.delete_one_diagnostic.diagnostic_only` | *not found / future candidate* | — | **DIAGNOSTIC_ONLY** | Not in Track B catalog; diagnostic only unless separately justified |
| `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review` | `SCM_UnitJackKnife` | RANK_3 | **RESTRICTED_REVIEW** | Null-monitor only; sole nominal-calibration eligible config |
| `geo.scm.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only` | `SCM_Placebo` | RANK_2 | **DIAGNOSTIC_ONLY** | Single-treated falsification diagnostic |
| `geo.scm.multi_treated.delta_mu.production_inference.blocked` | SCM multi-treated production inference | RANK_1 / blocked | **BLOCKED** | Production inference blocked unless separately validated |
| `geo.augsynth.point.single_cell.delta_mu.point_only.restricted_or_research` | `AugSynthCVXPY_Point` | RANK_2 | **RESTRICTED_REVIEW** | Point-only; restricted expert review; no interval claims |
| `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only` | `AugSynthCVXPY_UnitJackKnife` | RANK_1 | **RESEARCH_SANDBOX** | Research-only; future coverage-validation candidate |
| `geo.did.bootstrap.panel_delta.delta_mu.bootstrap_interval.diagnostic_only` | `DID_Bootstrap` | RANK_0 / blocked | **DIAGNOSTIC_ONLY** | Diagnostic only; assumptions and coverage not validated |
| `geo.did.point.panel_2x2.delta_mu.point_only.restricted_review` | DID 2×2 point estimate | RANK_3 | **RESTRICTED_REVIEW** | Point estimate only; no uncertainty authorization |
| `geo.tbr.point.aggregate_1x1.delta_mu.point_only.diagnostic_only` | Class TBR aggregate 1×1 | blocked | **DIAGNOSTIC_ONLY** | Aggregate diagnostic comparator only |
| `geo.tbr.placebo.single_treated.delta_mu.placebo_tail.blocked` | `geo.tbr.placebo.*` | registered unsupported | **BLOCKED** | 100% failure per Phase 15 |
| `geo.synthetic_did.*` | SyntheticDID | RANK_1 | **RESEARCH_SANDBOX** | Research-only; unwired recovery |
| `geo.bayesian_tbr.*` | BayesianTBR | RANK_1 | **RESEARCH_SANDBOX** | Research-only |
| `geo.trop.*` / `geo.mtgp.*` | TROP / MTGP | RANK_1 | **RESEARCH_SANDBOX** | Smoke/research only |

**Promotion-candidate note:** Only `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` may enter a **PROMOTION_CANDIDATE** evidence path — and only after the TBRRidge KFold evidence battery completes with explicit inheritance manifest. Tier remains RESTRICTED_REVIEW until runtime/review passes; catalog stays blocked for production.

---

## 8. Promotion-candidate instruments

| Instrument | Eligibility | Blockers |
|------------|-------------|----------|
| `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` | May enter full promotion evidence path for **diagnostic/restricted-review surfaces only** | RANK_0; STAGE_2; claim authorization boundary incomplete; sensitivity/null/positive-control evidence not generated; production catalog blocked |

No other instrument is designated PROMOTION_CANDIDATE in this audit. SCM UnitJackKnife remains RESTRICTED_REVIEW (null-monitor), not promotion-candidate for lift/production.

---

## 9. Restricted-review instruments

| Instrument | Allowed surfaces | Prohibited surfaces |
|------------|------------------|---------------------|
| `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` | Diagnostic interval summaries; restricted review packets | Production readout; lift/ROI; trust-report causal claims |
| `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review` | Null-monitor; governed expert review | Lift detection; production causal claims |
| `geo.augsynth.point.single_cell.delta_mu.point_only.restricted_or_research` | Point recovery diagnostic; expert review | Interval claims; production readout |
| `geo.did.point.panel_2x2.delta_mu.point_only.restricted_review` | Point estimate under assignment integrity | Uncertainty; bootstrap; production inference |

---

## 10. Diagnostic-only instruments

| Instrument | Role |
|------------|------|
| `geo.tbrridge.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only` | Placebo calibration / falsification support |
| `geo.tbrridge.jackknife.single_cell.delta_mu.delete_one_diagnostic.diagnostic_only` | Future candidate — delete-one instability diagnostic |
| `geo.scm.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only` | Single-treated null-reference diagnostic |
| `geo.did.bootstrap.panel_delta.delta_mu.bootstrap_interval.diagnostic_only` | Bootstrap diagnostic; inference not implemented in governed runtime |
| `geo.tbr.point.aggregate_1x1.delta_mu.point_only.diagnostic_only` | Aggregate 1×1 diagnostic comparator |

---

## 11. Research-sandbox instruments

| Instrument | Role |
|------------|------|
| `geo.tbrridge.brb.single_cell.delta_mu.resampling_diagnostic.research_or_restricted` | BRB resampling diagnostic; dependence assumptions unvalidated |
| `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only` | JK research interval; coverage validation deferred |
| `geo.synthetic_did.*` | Implementation-readiness research |
| `geo.bayesian_tbr.*` | MCMC research path |
| `geo.trop.*` / `geo.mtgp.*` | Research smoke paths |

---

## 12. Blocked instruments

| Instrument | Blocker |
|------------|---------|
| `geo.scm.multi_treated.delta_mu.production_inference.blocked` | Multi-treated production inference unresolved |
| `geo.tbr.placebo.single_treated.delta_mu.placebo_tail.blocked` | Aggregated-control policy failure |
| `geo.tbr.point.unit_panel.*` | Invalid geometry (unit panel) |
| Multi-cell pooled/global lift | `multicell_pooled_lift_blocked` |
| TBR aggregate / pooled paths | Catalog blocklist |

---

## 13. Deprecated instruments if any

| Instrument | Status |
|------------|--------|
| `TBRRidge_BlockResidualBootstrap` (pre-Run-002 interpretation) | **DEPRECATED** lineage — superseded by post-fix signal version; same Track B ID with updated CalibrationSignal |
| Classic TBR unit-panel paths | **DEPRECATED** for new use — retain lineage only |

No active catalog row is retired; deprecated entries are historical interpretation only.

---

## 14. Evidence inheritance matrix

| Instrument | Estimator-level reusable | Inference-specific required | Instrument-specific required | Inherited allowed | Inherited prohibited | Next validation depth |
|------------|-------------------------|----------------------------|------------------------------|-------------------|---------------------|------------------------|
| `geo.tbrridge.kfold.single_cell...` | Metric/estimand alignment structure; donor-pool sensitivity patterns; claim-boundary language | KFold leakage; fold geometry; coverage validation | Interval semantics; single-cell geometry; diagnostic surface manifest | TBRRidge point-recovery design patterns (geometry-matched) | Placebo/JK/BRB evidence; multi-treated geometry; production surfaces | Full KFold evidence battery + claim boundary audit |
| `geo.tbrridge.placebo.single_treated...` | TBRRidge estimand structure | Placebo pool validity; tail calibration | Placebo tail semantics; single-treated geometry | None from KFold promotion path | KFold coverage; production authorization | Placebo calibration diagnostic runtime evidence |
| `geo.tbrridge.brb.single_cell...` | TBRRidge point structure | BRB block dependence; resampling assumptions | Resampling diagnostic semantics | None from KFold | KFold/Placebo promotion evidence | Dependence assumption validation audit |
| `geo.tbrridge.jackknife...` | — | Delete-one leverage (if implemented) | JK diagnostic semantics | None | All other TBRRidge inference evidence | Future instrument definition audit |
| `geo.scm.jackknife.null_monitor...` | Donor-pool sensitivity; null-monitor claim patterns | Jackknife leverage; delete-one stability | Null-monitor surface; multi-treated default geometry | SCM point-recovery (geometry-matched) | Placebo promotion; TBRRidge evidence | SCM unit JK promotion evidence audit |
| `geo.scm.placebo.single_treated...` | SCM estimand structure | Placebo pool; single-treated constraint | Placebo band semantics | SCM JK null-monitor patterns (diagnostic only) | JK production paths | SCM placebo governed semantics |
| `geo.scm.multi_treated.production...` | — | Multi-treated inference validity | Production inference surface | None | All SCM JK evidence for production lift | Separate multi-treated validation plan |
| `geo.augsynth.point...` | Point recovery patterns | None (point-only) | Spillover DGP exclusions; point-only surface | None from SCM/TBRRidge | JK/Conformal evidence | AugSynth point validation evidence audit |
| `geo.augsynth.jackknife...` | Point recovery (matched) | JK leverage; coverage | Research interval semantics | None from SCM JK promotion | SCM JK null-monitor authorization | AugSynth JK coverage validation audit |
| `geo.did.bootstrap.panel_delta...` | Panel delta estimand structure | Bootstrap dependence; panel resampling | Bootstrap interval semantics | DID point path (restricted) | SCM/TBRRidge evidence; production inference | Bootstrap executor + coverage audit (deferred) |

**Hard inheritance rules applied:** No cross-inference-family promotion; no cross-geometry authorization; diagnostic evidence cannot authorize production; estimator-family names cannot be promoted globally.

---

## 15. Pairing-specific validation requirements

| Pairing | Required validation |
|---------|---------------------|
| TBRRidge + KFold | Leakage diagnostic; interval semantics; null FPR; directional error; positive-control recovery; sensitivity bundle; metric/estimand alignment; claim authorization boundary |
| TBRRidge + Placebo | Placebo pool validity; tail calibration; single-treated geometry enforcement |
| TBRRidge + BRB | Block dependence assumptions; resampling diagnostic; inverted-bounds remediation evidence |
| TBRRidge + Jackknife | Delete-one instability; leverage diagnostics (future) |
| SCM + Jackknife | Null FPR/coverage; null-monitor claim boundary; donor sensitivity |
| SCM + Placebo | Single-treated enforcement; placebo band semantics |
| SCM multi-treated production | Separate multi-treated inference validation — blocked until plan exists |
| AugSynth point | Point recovery; spillover DGP characterization; ASCM remediation |
| AugSynth + JK | Coverage validation; estimand/scale bridge |
| DID + Bootstrap | Bootstrap executor; panel dependence; coverage; relative-interval policy closure |

---

## 16. Roadmap changes required

1. **Insert instrument catalog triage** before future method-promotion lanes — complete in this artifact
2. **TBRRidge work scoped** to `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` unless explicit inheritance manifest names another identity
3. **Exact instrument ID required** in all future promotion contracts, runtimes, and audits
4. **Non-selected pairings** marked diagnostic/research/blocked — remove vague "TBRRidge promotion" or "SCM production" language
5. **Production compatibility** remains downstream of exact instrument review only
6. **METHOD_PROMOTION_CANDIDATE_AUDIT_001** rankings must be read with instrument identities from §7

---

## 17. TBRRidge lane correction

| Prior (incorrect) | Corrected |
|-------------------|-----------|
| "TBRRidge promotion evidence battery" | Applies to **`geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review`** only |
| "TBRRidge method promotion review" | Instrument-scoped; posture RANK_0 / BLOCKED / STAGE_2 unchanged |
| "TBRRidge characterized" | Only KFold single-cell diagnostic interval under restricted review |
| TBRRidge Placebo / BRB / JK | Separate tiers — diagnostic, research, or blocked; no family inheritance |

TBRRidge lane **next artifact:** `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` (scoped to KFold instrument identity).

---

## 18. SCM / AugSynth / DID lane implications

### SCM

- **UnitJackKnife:** RESTRICTED_REVIEW null-monitor — highest-ranked geo instrument (RANK_3); not promotion-candidate for lift
- **Placebo:** DIAGNOSTIC_ONLY falsification; governed semantics still required
- **Multi-treated production:** BLOCKED — do not conflate with JK null-monitor success

### AugSynth

- **Point:** RESTRICTED_REVIEW point-only; spillover and ASCM remediation block broader claims
- **JK:** RESEARCH_SANDBOX; parallel path `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001`

### DID

- **2×2 point:** RESTRICTED_REVIEW; point executor exists; uncertainty blocked
- **Bootstrap:** DIAGNOSTIC_ONLY; inference not implemented; bootstrap runtime deferred (`ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_004`)

---

## 19. Allowed/prohibited surfaces by tier

| Tier | Allowed surfaces | Prohibited surfaces |
|------|------------------|---------------------|
| **PROMOTION_CANDIDATE** | Instrument-specific evidence battery entry (diagnostic/restricted only for TBRRidge KFold) | Production; lift/ROI; trust-report causal; MMM ingestion |
| **RESTRICTED_REVIEW** | Review-only summaries; null-monitor; diagnostic intervals under claim boundary | Production readout; ungoverned CI/significance |
| **DIAGNOSTIC_ONLY** | Stress tests; calibration; warnings; falsification | Promotion path; production |
| **RESEARCH_SANDBOX** | Exploratory OC; research notebooks | Any governed downstream claim |
| **BLOCKED** | Lineage reference only | All governed surfaces |
| **DEPRECATED** | Historical signal versions | New TrustReport references |

---

## 20. Stop/go criteria

### Go

Proceed to `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` when triage matrix adopted and instrument IDs referenced in TBRRidge lane artifacts.

### Stop

Stop when:

1. Estimator-family promotion attempted without instrument identity
2. TBRRidge evidence applied to Placebo/BRB/JK without inheritance manifest
3. SCM JK null-monitor evidence used to authorize multi-treated production inference
4. Diagnostic-tier instrument used for production authorization
5. Catalog rank or blocklist status changed without separate promotion runtime

---

## 21. Authorization boundary

**Allowed:** `method_instrument_catalog_triage_audit_completed`, `classification_policy_applied`, `instrument_triage_matrix_defined`, `evidence_inheritance_matrix_defined`, `roadmap_correction_defined`, `exact_instrument_id_required_for_future_promotion`, `estimator_family_global_promotion_blocked`

**Forbidden:** `method_promoted`, `method_unblocked`, `estimator_family_promoted`, `global_tbrridge_promotion_authorized`, `instrument_promoted`, `catalog_unblocked`, `production_catalog_unblocked`, `production_compatibility_authorized`, `production_authorization_granted`, `production_readout_authorized`, all uncertainty/CI/p-value/significance/lift/ROI/inference/estimator/simulation/MMM/LLM flags

No instrument is promoted, unblocked, or production-authorized by this audit.

---

## 22. Validation results

| Check | Result |
|-------|--------|
| Audit document complete | Pass |
| Summary JSON valid | Pass |
| Governance tests | Pass |
| Safety grep | Pass |
| Capability grep | Pass |

---

## 23. Known limitations

- **Audit only** — Classification tiers assigned; catalog ranks and blocklist enforcement unchanged
- **Track B / policy ID harmonization** — Legacy Track B format retained; policy identity is forward authority
- **Future candidates** — `geo.tbrridge.jackknife.*` documented as not found / future candidate
- **Evidence not generated** — Inheritance matrix defines requirements only
- **RANK vs tier** — Catalog RANK_0–RANK_4 coexists with classification tiers; both must be consulted

---

## 24. Recommended next artifacts

| Priority | Artifact | Rationale |
|----------|----------|-----------|
| **Recommended** | `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` | Next TBRRidge KFold instrument-scoped gate |
| **Alternative** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` | Parallel research-sandbox instrument path |
| **Deferred** | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` | Gate-triggered after STAGE_6 / RANK_4 candidate |
| **Secondary** | `SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001` | Highest RANK_3 restricted-review instrument |
