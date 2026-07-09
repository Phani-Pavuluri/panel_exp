# METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001` |
| **Artifact type** | `method_estimator_inference_pairing_coverage_audit` |
| **Status** | `completed` |
| **Scope** | `estimator_inference_pairing_coverage_audited_no_method_promotion_or_inference_implementation` |
| **Base commit** | `be15f48` (Add method instrument catalog triage audit) |
| **Final verdict** | `estimator_inference_pairing_coverage_audited_no_method_promotion_or_inference_implementation` |

**Depends on:** `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001` · `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` · `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001` · `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001`

**Positive audit flags:** `estimator_inference_pairing_coverage_audit_completed` · `estimator_families_reviewed` · `inference_families_reviewed` · `pairing_coverage_matrix_defined` · `missing_pairing_reason_codes_defined` · `evidence_inheritance_implications_defined` · `future_pairing_cataloging_required`

---

## 2. Source files inspected

- `docs/track_d/METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001.md`
- `docs/track_d/METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001.md`
- `docs/TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`
- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`
- `docs/track_d/METHOD_PROMOTION_CANDIDATE_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001_REPORT.md`
- `docs/track_d/TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001.md`
- `docs/track_d/TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001.md`
- `docs/track_d/TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001.md`
- `docs/ROADMAP_V4.md` · `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md` · `docs/MIP_AUDIT_REGISTRY.md`
- `docs/governance/OPEN_INVESTIGATIONS_001.json`

---

## 3. Audit purpose

**Core question:** Are estimator × inference pairings missing because they are invalid, not natural, redundant, unsafe, not implemented, not prioritized, or requiring separate validation — or are we accidentally missing them?

Create a platform-wide estimator × inference pairing coverage audit. Inventory estimator families against inference families, classify each pairing with explicit inclusion/exclusion reason codes, and document evidence inheritance boundaries.

**This audit does not prove geometry coverage.** Geometry (single-treated, multi-treated, null-monitor, aggregate 1×1, panel delta) is a separate dimension addressed by optional `METHOD_INSTRUMENT_GEOMETRY_TAXONOMY_AUDIT_001`.

---

## 4. Relationship to instrument classification policy

| Classification policy rule | Application in pairing coverage |
|---------------------------|--------------------------------|
| Promote instruments, not estimator families | Each cell is estimator × inference only; promotion requires full instrument identity including geometry |
| Three-class evidence inheritance | Documented per pairing in §17 |
| Inference evidence non-transferable | Each pairing requires its own inference-family validation |
| Unsupported surfaces blocked by default | Absent pairings carry explicit reason codes — not silent omission |

Classification policy defines **what** a governed instrument is. This audit defines **which estimator × inference pairings exist, are absent, or are excluded** and **why**.

---

## 5. Relationship to catalog triage audit

| Catalog triage audit | Pairing coverage audit |
|---------------------|------------------------|
| Classified **known/cataloged instruments** (full identity including geometry) | Classifies **all estimator × inference cells** regardless of catalog presence |
| Assigned RESTRICTED_REVIEW / DIAGNOSTIC_ONLY / etc. | Assigns IMPLEMENTED / NOT_IMPLEMENTED / FUTURE_CANDIDATE / etc. |
| Did not prove missing pairings were intentional | **Explicitly documents every missing pairing with reason code** |
| TBRRidge lane scoped to KFold instrument | Confirms TBRRidge × KFold is only active restricted-review pairing; other TBRRidge inference pairings classified |

**Gap closed:** Catalog triage answered "what tier is this instrument?" Pairing coverage answers "why is TBRRidge × Conformal absent?"

---

## 6. Why this is not a geometry taxonomy audit

| Dimension | Pairing coverage audit | Geometry taxonomy audit (separate) |
|-----------|------------------------|----------------------------------|
| **Scope** | Estimator family × inference family | Assignment/readout shape (single-treated, multi-treated, null-monitor, aggregate, panel) |
| **Question** | Is this inference natural/implementable for this estimator? | Which geometries does this instrument support? |
| **Example** | SCM × Bootstrap — not natural | SCM Placebo — single-treated only |
| **TBRRidge KFold** | Cataloged pairing at estimator×inference level | Single-cell vs multi-treated geometry validated separately |

Pairing coverage is a **necessary bridge** between catalog triage and instrument validation; geometry taxonomy is an **optional follow-up** (`METHOD_INSTRUMENT_GEOMETRY_TAXONOMY_AUDIT_001`).

---

## 7. Estimator families reviewed

| Estimator family | Catalog / docs presence | Notes |
|------------------|------------------------|-------|
| **TBRRidge** | Active; multiple inference configs | Primary sophisticated-method lane |
| **TBR (classical)** | Aggregate 1×1 diagnostic | Distinct from TBRRidge; unit-panel blocked |
| **SCM** | Active; JK + Placebo cataloged | Highest RANK_3 null-monitor path |
| **AugSynth** (AugSynthCVXPY) | Active; point + JK + Conformal smoke | Research/diagnostic posture |
| **DID** | Active; point + bootstrap (blocked) | Bootstrap runtime deferred |
| **SyntheticDID** | Registered research-only | Not in scope for geo pairing matrix |
| **BayesianTBR** | Research-only | NOT_IN_SCOPE for current geo pairing matrix |
| **TROP / MTGP** | Research smoke | NOT_IN_SCOPE for current geo pairing matrix |

---

## 8. Inference families reviewed

| Inference family | Registry / docs presence | Notes |
|------------------|-------------------------|-------|
| **KFold** | TBRRidge_Kfold; TBR Kfold (aggregate) | Fold leakage geometry-specific |
| **Placebo** | SCM_Placebo; TBRRidge_Placebo | Single-treated constraint at geometry layer |
| **Jackknife / UnitJackknife** | SCM_UnitJackKnife; AugSynth JK | Delete-one / leverage semantics |
| **Bootstrap** | DID_Bootstrap; general deferred | Panel dependence assumptions |
| **BRB** (Block Residual Bootstrap) | TBRRidge_BlockResidualBootstrap | Block dependence; inverted-bounds history |
| **Conformal** | AugSynthCVXPY_Conformal smoke; TBRRidge blocked | Exchangeability / score calibration |
| **point-only** | AugSynth point; DID 2×2 point; TBR point | No interval semantics |

---

## 9. Estimator × inference coverage matrix

**Legend:** Status abbreviations map to reason codes in §10.

| Estimator ↓ / Inference → | KFold | Placebo | Jackknife | Bootstrap | BRB | Conformal | point-only |
|---------------------------|-------|---------|-----------|-----------|-----|-----------|------------|
| **TBRRidge** | RESTRICTED_REVIEW / CATALOGED | DIAGNOSTIC_ONLY / CATALOGED | FUTURE_CANDIDATE / NOT_IMPLEMENTED | REQUIRES_SEPARATE_VALIDATION | RESEARCH_SANDBOX / CATALOGED | FUTURE_CANDIDATE / NOT_IMPLEMENTED | REDUNDANT / NOT_PRIORITIZED |
| **TBR** | DIAGNOSTIC_ONLY / CATALOGED | BLOCKED_BY_GEOMETRY | NOT_NATURAL | NOT_IMPLEMENTED | NOT_IMPLEMENTED | NOT_IMPLEMENTED | DIAGNOSTIC_ONLY / CATALOGED |
| **SCM** | NOT_NATURAL / NOT_PRIORITIZED | DIAGNOSTIC_ONLY / CATALOGED | RESTRICTED_REVIEW / GOVERNED | NOT_NATURAL / NOT_IMPLEMENTED | NOT_NATURAL | NOT_IMPLEMENTED / FUTURE_CANDIDATE | REDUNDANT |
| **AugSynth** | FUTURE_CANDIDATE / NOT_IMPLEMENTED | FUTURE_CANDIDATE / NOT_IMPLEMENTED | RESEARCH_SANDBOX / CATALOGED | NOT_IMPLEMENTED | NOT_NATURAL | DIAGNOSTIC_ONLY / IMPLEMENTED | RESTRICTED_REVIEW / CATALOGED |
| **DID** | NOT_NATURAL / NOT_IMPLEMENTED | NOT_IMPLEMENTED / FUTURE_CANDIDATE | NOT_IMPLEMENTED / FUTURE_CANDIDATE | DIAGNOSTIC_ONLY / CATALOGED | NOT_NATURAL | NOT_IMPLEMENTED / FUTURE_CANDIDATE | RESTRICTED_REVIEW / GOVERNED |

### Minimum pairings — explicit evaluation

| Pairing | Status | Reason code | Instrument identity (if present) |
|---------|--------|-------------|----------------------------------|
| TBRRidge × KFold | CATALOGED / RESTRICTED_REVIEW | `CATALOGED` + `RESTRICTED_REVIEW` | `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| TBRRidge × Placebo | CATALOGED / DIAGNOSTIC_ONLY | `CATALOGED` + `DIAGNOSTIC_ONLY` | `geo.tbrridge.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only` |
| TBRRidge × BRB | CATALOGED / RESEARCH_SANDBOX | `CATALOGED` + `RESEARCH_SANDBOX` | `geo.tbrridge.brb.single_cell.delta_mu.resampling_diagnostic.research_or_restricted` |
| TBRRidge × Jackknife | NOT_IMPLEMENTED | `FUTURE_CANDIDATE` | — (not in Track B catalog) |
| TBRRidge × Bootstrap | NOT_IMPLEMENTED | `REQUIRES_SEPARATE_VALIDATION` | — (BRB is distinct resampling path) |
| TBRRidge × Conformal | NOT_IMPLEMENTED | `FUTURE_CANDIDATE` | TBRRidge_Conformal blocked per D5_INST (TBRRIDGE-002) |
| SCM × Jackknife | GOVERNED / RESTRICTED_REVIEW | `GOVERNED` + `RESTRICTED_REVIEW` | `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review` |
| SCM × Placebo | CATALOGED / DIAGNOSTIC_ONLY | `CATALOGED` + `DIAGNOSTIC_ONLY` | `geo.scm.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only` |
| SCM × Bootstrap | NOT_IMPLEMENTED | `NOT_NATURAL_FOR_ESTIMATOR` | SCM uses JK/Placebo paths; bootstrap not natural |
| SCM × KFold | NOT_IMPLEMENTED | `NOT_NATURAL_FOR_ESTIMATOR` | KFold not standard SCM inference |
| SCM × Conformal | NOT_IMPLEMENTED | `FUTURE_CANDIDATE` | No catalog row; conformal not documented for SCM |
| AugSynth × point-only | CATALOGED / RESTRICTED_REVIEW | `CATALOGED` + `RESTRICTED_REVIEW` | `geo.augsynth.point.single_cell.delta_mu.point_only.restricted_or_research` |
| AugSynth × Jackknife | CATALOGED / RESEARCH_SANDBOX | `CATALOGED` + `RESEARCH_SANDBOX` | `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only` |
| AugSynth × Bootstrap | NOT_IMPLEMENTED | `NOT_IMPLEMENTED` | No recovery config or catalog row |
| AugSynth × Placebo | NOT_IMPLEMENTED | `FUTURE_CANDIDATE` | Not documented in Track B |
| AugSynth × KFold | NOT_IMPLEMENTED | `FUTURE_CANDIDATE` | Not documented in Track B |
| DID × Bootstrap | CATALOGED / DIAGNOSTIC_ONLY | `CATALOGED` + `DIAGNOSTIC_ONLY` | `geo.did.bootstrap.panel_delta.delta_mu.bootstrap_interval.diagnostic_only` |
| DID × Placebo | NOT_IMPLEMENTED | `FUTURE_CANDIDATE` | No catalog row |
| DID × Jackknife | NOT_IMPLEMENTED | `NOT_IMPLEMENTED` | No catalog row |
| DID × KFold | NOT_IMPLEMENTED | `NOT_NATURAL_FOR_ESTIMATOR` | Panel DID uses bootstrap or point; KFold not natural |
| DID × Conformal | NOT_IMPLEMENTED | `FUTURE_CANDIDATE` | No catalog row |
| DID × point-only | GOVERNED / RESTRICTED_REVIEW | `GOVERNED` + `RESTRICTED_REVIEW` | `geo.did.point.panel_2x2.delta_mu.point_only.restricted_review` |

---

## 10. Pairing status reason codes

| Code | Meaning |
|------|---------|
| `IMPLEMENTED` | Callable in recovery/tests with documented interface |
| `CATALOGED` | Track B or policy instrument row exists |
| `GOVERNED` | Production OC + governance decision attached |
| `RESTRICTED_REVIEW` | May support review-only summaries under claim boundaries |
| `DIAGNOSTIC_ONLY` | Stress test / calibration / falsification only |
| `RESEARCH_SANDBOX` | Exploratory; no governed downstream claim surface |
| `BLOCKED_BY_ASSUMPTION` | Inference assumptions fail for estimator (e.g., exchangeability) |
| `BLOCKED_BY_GEOMETRY` | Pairing invalid at geometry layer (see geometry taxonomy) |
| `NOT_NATURAL_FOR_ESTIMATOR` | Inference not standard or sensible for estimator family |
| `REDUNDANT_WITH_EXISTING_INSTRUMENT` | Covered by another pairing (e.g., point-only when JK exists) |
| `NOT_IMPLEMENTED` | No code path or recovery config |
| `NOT_DOCUMENTED` | No docs/catalog reference |
| `NOT_PRIORITIZED` | Valid in principle but deferred by roadmap |
| `REQUIRES_SEPARATE_VALIDATION` | Must enter through cataloging before validation |
| `FUTURE_CANDIDATE` | May be cataloged later; absent intentionally for now |
| `DEPRECATED` | Retained for lineage only |
| `NOT_IN_SCOPE` | Research estimator outside current geo pairing matrix |

**Rule:** Every absent cell must carry at least one reason code. Silent omission is prohibited.

---

## 11. Included pairings and why

| Pairing | Why included |
|---------|--------------|
| TBRRidge × KFold | Active restricted-review lane; evidence battery defined; catalog row `TBRRidge_Kfold` |
| TBRRidge × Placebo | Diagnostic calibration; characterized Phase 15; `TBRRidge_Placebo` |
| TBRRidge × BRB | Historical OC; post-fix restricted; `TBRRidge_BlockResidualBootstrap` |
| SCM × Jackknife | Sole nominal-calibration eligible config; governed null-monitor |
| SCM × Placebo | Governed falsification diagnostic; Phase 15 |
| AugSynth × point-only | Point recovery characterized; `AugSynthCVXPY_Point` |
| AugSynth × Jackknife | JK track Phase 14; research interval |
| AugSynth × Conformal | Interface-valid smoke (D5_INST); diagnostic-only triangulation |
| DID × Bootstrap | Policy characterized; bootstrap runtime deferred |
| DID × point-only | First governed DID executor; 2×2 point estimate |
| TBR × point-only | Aggregate 1×1 diagnostic comparator |

---

## 12. Missing pairings and why

| Pairing | Reason code(s) | Rationale |
|---------|----------------|-----------|
| TBRRidge × Jackknife | `FUTURE_CANDIDATE`, `NOT_IMPLEMENTED` | No catalog row; delete-one instability unvalidated |
| TBRRidge × Bootstrap | `REQUIRES_SEPARATE_VALIDATION`, `NOT_IMPLEMENTED` | BRB is the resampling path; generic bootstrap not wired |
| TBRRidge × Conformal | `FUTURE_CANDIDATE`, `BLOCKED_BY_ASSUMPTION` | TBRRidge_Conformal blocked (TBRRIDGE-002); exchangeability unvalidated |
| SCM × Bootstrap | `NOT_NATURAL_FOR_ESTIMATOR` | SCM standard inference is JK or Placebo |
| SCM × KFold | `NOT_NATURAL_FOR_ESTIMATOR` | KFold not standard for synthetic control |
| SCM × Conformal | `FUTURE_CANDIDATE`, `NOT_IMPLEMENTED` | No documented SCM conformal path |
| AugSynth × Bootstrap | `NOT_IMPLEMENTED` | No recovery config |
| AugSynth × Placebo | `FUTURE_CANDIDATE`, `NOT_DOCUMENTED` | Not in Track B catalog |
| AugSynth × KFold | `FUTURE_CANDIDATE`, `NOT_IMPLEMENTED` | Not in Track B catalog |
| DID × Placebo | `FUTURE_CANDIDATE`, `NOT_IMPLEMENTED` | No catalog row |
| DID × Jackknife | `NOT_IMPLEMENTED` | No catalog row |
| DID × KFold | `NOT_NATURAL_FOR_ESTIMATOR` | Panel DID uses bootstrap or point |
| DID × Conformal | `FUTURE_CANDIDATE`, `NOT_IMPLEMENTED` | No catalog row |
| TBR × Bootstrap / BRB / Conformal | `NOT_IMPLEMENTED` | Aggregate TBR diagnostic only |
| TBR × Jackknife | `NOT_NATURAL_FOR_ESTIMATOR` | JKP optional OC only (F-INF-004); not primary path |

**No accidental exclusion:** All cells in §9 matrix are explicitly classified. Absence is documented, not silent.

---

## 13. Blocked pairings and why

| Pairing | Reason code | Blocker |
|---------|-------------|---------|
| TBRRidge × Conformal | `BLOCKED_BY_ASSUMPTION` | Interface blocked TBRRIDGE-002; conformal exchangeability |
| TBR × Placebo | `BLOCKED_BY_GEOMETRY` | 100% failure — aggregated-control policy (Phase 15) |
| TBR × unit-panel × * | `BLOCKED_BY_GEOMETRY` | Invalid geometry (F-GEO-001) |
| SCM multi-treated production inference | `BLOCKED_BY_ASSUMPTION` | Unresolved production inference path |
| Multi-cell pooled/global lift | `BLOCKED_BY_GEOMETRY` | Dependence/multiplicity unresolved |

---

## 14. Research/future candidate pairings

| Pairing | Reason code | Next action |
|---------|-------------|-------------|
| TBRRidge × Jackknife | `FUTURE_CANDIDATE` | Define instrument identity; leverage diagnostic audit |
| TBRRidge × Conformal | `FUTURE_CANDIDATE` | Remediate TBRRIDGE-002; exchangeability audit |
| AugSynth × Placebo / KFold | `FUTURE_CANDIDATE` | Catalog if product need emerges |
| SCM × Conformal | `FUTURE_CANDIDATE` | Separate validation if pursued |
| DID × Placebo / Jackknife / Conformal | `FUTURE_CANDIDATE` | Catalog before validation |
| SyntheticDID × * | `NOT_IN_SCOPE` | Implementation-readiness plan separate |

---

## 15. Redundant or low-value pairings

| Pairing | Reason code | Notes |
|---------|-------------|-------|
| TBRRidge × point-only | `REDUNDANT_WITH_EXISTING_INSTRUMENT`, `NOT_PRIORITIZED` | Point path exists via estimator; inference pairings are the governance unit |
| SCM × point-only | `REDUNDANT_WITH_EXISTING_INSTRUMENT` | SCM point covered by estimator; JK is primary inference |
| AugSynth × BRB | `NOT_NATURAL_FOR_ESTIMATOR` | BRB specific to TBRRidge block structure |

---

## 16. Pairings requiring separate validation

| Pairing | Reason code | Requirement |
|---------|-------------|-------------|
| TBRRidge × Bootstrap | `REQUIRES_SEPARATE_VALIDATION` | Distinct from BRB; panel/block dependence audit |
| TBRRidge × BRB | `REQUIRES_SEPARATE_VALIDATION` | Dependence assumptions; inverted-bounds remediation |
| TBRRidge × KFold | `REQUIRES_SEPARATE_VALIDATION` | Full evidence battery before any promotion path |
| AugSynth × Conformal | `REQUIRES_SEPARATE_VALIDATION` | Interval semantics distinct from JK/KFold |
| DID × Bootstrap | `REQUIRES_SEPARATE_VALIDATION` | Bootstrap executor + coverage before any unblock |

---

## 17. Evidence inheritance implications

**Platform rules (from classification policy):**

- Pairings may inherit **estimator-level** design patterns only when metric, geography, contrast, time window, and modeled target match.
- Pairings may **not** inherit **inference-family-specific** evidence.

| Source inference evidence | Cannot validate |
|---------------------------|-----------------|
| KFold leakage / fold geometry | Placebo, Jackknife, Bootstrap, BRB, Conformal |
| Placebo tail calibration | KFold, Jackknife, Bootstrap, BRB, Conformal |
| Jackknife leverage / delete-one | KFold, Placebo, Bootstrap, BRB, Conformal |
| Bootstrap / BRB dependence | KFold, Placebo, Jackknife, Conformal |
| Conformal exchangeability / scores | KFold, Placebo, Jackknife, Bootstrap, BRB |

**Per-estimator notes:**

- **TBRRidge:** KFold evidence battery applies to TBRRidge × KFold only; cannot authorize Placebo/BRB/JK/Bootstrap/Conformal pairings.
- **SCM:** JK null-monitor evidence cannot authorize Bootstrap/KFold/Conformal; Placebo is falsification-only.
- **AugSynth:** Point recovery may inform JK point structure; JK intervals cannot authorize Conformal or Bootstrap without separate validation.
- **DID:** Point-estimate path separate from bootstrap; bootstrap cannot inherit point path uncertainty authorization.

Any future promotion contract/runtime must name **exact estimator × inference pairing** and **full instrument identity**.

---

## 18. Roadmap corrections

1. **Pairing coverage audit** inserted as bridge between catalog triage and instrument validation — complete in this artifact.
2. **Missing pairings** must carry explicit reason codes before being ignored in roadmap or audits.
3. **Future pairings** must enter through cataloging and classification before validation work.
4. **TBRRidge + KFold** remains current restricted-review lane; other TBRRidge inference pairings are diagnostic/research/future only.
5. **TBRRidge claim authorization boundary** proceeds next only after pairing coverage is recorded.
6. **Geometry taxonomy** remains separate optional follow-up (`METHOD_INSTRUMENT_GEOMETRY_TAXONOMY_AUDIT_001`).
7. **No global estimator-family promotion** — roadmap language must reference pairings or full instrument IDs.

---

## 19. Stop/go criteria

### Go

Proceed to `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` when pairing matrix adopted and all absent cells have reason codes.

### Stop

Stop when:

1. Absent pairing treated as accidental omission without reason code
2. Inference evidence transferred across pairing boundaries
3. Estimator-family promotion attempted without pairing + instrument identity
4. Pairing added to roadmap without cataloging requirement
5. Geometry taxonomy conflated with pairing coverage

---

## 20. Authorization boundary

**Allowed:** `estimator_inference_pairing_coverage_audit_completed`, `estimator_families_reviewed`, `inference_families_reviewed`, `pairing_coverage_matrix_defined`, `missing_pairing_reason_codes_defined`, `evidence_inheritance_implications_defined`, `future_pairing_cataloging_required`

**Forbidden:** `method_promoted`, `method_unblocked`, `estimator_family_promoted`, `global_tbrridge_promotion_authorized`, `instrument_promoted`, `pairing_promoted`, `catalog_unblocked`, all production/uncertainty/CI/significance/lift/ROI/inference/estimator/simulation/MMM/LLM flags

No pairing is promoted, implemented, or production-authorized by this audit.

---

## 21. Validation results

| Check | Result |
|-------|--------|
| Audit document complete | Pass |
| Summary JSON valid | Pass |
| Governance tests | Pass |
| Safety grep | Pass |
| Capability grep | Pass |

---

## 22. Known limitations

- **Pairing level only** — Geometry variants within a pairing deferred to geometry taxonomy audit
- **Research estimators** — SyntheticDID, BayesianTBR, TROP, MTGP marked NOT_IN_SCOPE for geo matrix
- **Catalog vs implementation** — CATALOGED ≠ IMPLEMENTED; DID bootstrap is cataloged but runtime deferred
- **Reason codes** — Subjective judgment documented; revisit on product priority change

---

## 23. Recommended next artifacts

| Priority | Artifact | Rationale |
|----------|----------|-----------|
| **Recommended** | `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` | Next TBRRidge KFold instrument-scoped gate after pairing coverage recorded |
| **Alternative** | `METHOD_INSTRUMENT_GEOMETRY_TAXONOMY_AUDIT_001` | Optional geometry dimension follow-up |
| **Deferred** | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` | Gate-triggered after RANK_4 candidate |
| **Secondary** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` | Research-sandbox AugSynth × Jackknife path |
