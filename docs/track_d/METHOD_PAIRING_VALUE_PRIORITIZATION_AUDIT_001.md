# METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001` |
| **Artifact type** | `method_pairing_value_prioritization_audit` |
| **Status** | `completed` |
| **Scope** | `method_pairing_value_prioritization_audited_no_pairing_promotion_or_inference_implementation` |
| **Base commit** | `ad2447c` (Add estimator inference pairing coverage audit) |
| **Final verdict** | `method_pairing_value_prioritization_audited_no_pairing_promotion_or_inference_implementation` |

**Depends on:** `METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001` · `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` · `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001`

**Positive audit flags:** `method_pairing_value_prioritization_audit_completed` · `left_out_pairings_reviewed` · `implementation_status_reviewed` · `pairing_value_framework_defined` · `prioritization_decisions_defined` · `save_for_later_queue_defined` · `roadmap_corrections_defined`

---

## 2. Source files inspected

- `docs/track_d/METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001.md`
- `docs/track_d/archives/METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001_summary.json`
- `docs/track_d/METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001.md`
- `docs/track_d/METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001.md`
- `docs/TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`
- `docs/AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md`
- `docs/track_d/D5_INST_AUGSYNTH_KFOLD_001_REPORT.md` (referenced via ADR)
- `panel_exp/validation/track_d_d5_inst_augsynth_kfold_001.py`
- `panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py`
- `tests/track_d/test_d5_inst_augsynth_003.py`
- `docs/track_d/archives/D5_INST_COMBO_AUDIT_001_results.json`
- `docs/ROADMAP_V4.md` · `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md` · `docs/MIP_AUDIT_REGISTRY.md`
- `docs/governance/OPEN_INVESTIGATIONS_001.json`

---

## 3. Audit purpose

**Core principle:** A pairing being implemented is not enough. It must add unique causal/inferential value relative to existing selected instruments, and its validation cost/risk must be justified.

For every left-out, future-candidate, research, diagnostic-only, or possibly misclassified estimator × inference pairing:

1. Confirm whether it exists / is implemented / documented
2. Identify what unique causal value it adds
3. Identify what assumptions/risks it introduces
4. Compare against selected instruments
5. Decide: pursue now, save for later, diagnostic-only, research, or block

**Distinction ladder:**

| Stage | Meaning |
|-------|---------|
| **Implemented** | Callable code path exists |
| **Governed** | Catalog row + OC + governance decision |
| **Validated** | Evidence battery satisfies promotion prerequisites |
| **Worth prioritizing** | Incremental value justifies validation cost |
| **Production/decision-ready** | Not authorized by this audit |

---

## 4. Relationship to pairing coverage audit

| Pairing coverage audit | Value prioritization audit |
|------------------------|---------------------------|
| Documented presence/absence with reason codes | Evaluates **value** and **priority** of absent/under-classified pairings |
| Marked AugSynth × KFold/Placebo/Bootstrap as `NOT_IMPLEMENTED` / `FUTURE_CANDIDATE` | **Corrects:** AugSynth × KFold and × Conformal are `IMPLEMENTED_BUT_NOT_GOVERNED` |
| Reason codes only | Adds value scoring, risk, cost, and priority bucket |

**Corrections to prior coverage audit (§17):**

| Pairing | Prior coverage code | Corrected status |
|---------|----------------------|------------------|
| AugSynth × KFold | `NOT_IMPLEMENTED` / `FUTURE_CANDIDATE` | `IMPLEMENTED_BUT_NOT_GOVERNED` |
| AugSynth × Conformal | `DIAGNOSTIC_ONLY` / `IMPLEMENTED` (partial) | `IMPLEMENTED_BUT_NOT_GOVERNED` |
| AugSynth × Placebo | `FUTURE_CANDIDATE` / `NOT_DOCUMENTED` | `BLOCK` (explicit interface block) |
| AugSynth × Bootstrap | `NOT_IMPLEMENTED` | `BLOCK` (explicit interface block) |

---

## 5. Relationship to catalog triage

Catalog triage assigned classification **tiers** to full instrument identities. This audit operates at **estimator × inference** level before geometry is resolved. A pairing may be implemented but not cataloged (AugSynth KFold); cataloged but not worth pursuing (TBRRidge BRB); or blocked at interface (AugSynth Placebo).

---

## 6. Implementation vs governance distinction

| Pairing | Implemented | Documented | Cataloged | Governed |
|---------|-------------|------------|-----------|----------|
| AugSynth × point-only | Yes | Yes | Yes | Restricted review |
| AugSynth × Jackknife | Yes | Yes | Yes | Research sandbox |
| AugSynth × Conformal | Yes | Yes | Partial (D5-003) | No — not governed uncertainty |
| AugSynth × KFold | Yes | Yes (D5-KFOLD-001) | No Track B row | No — diagnostic comparator only |
| AugSynth × Placebo | No (blocked) | Yes (explicit block) | No | N/A |
| AugSynth × Bootstrap/BRB | No (blocked) | Yes (combo audit) | No | N/A |
| TBRRidge × KFold | Yes | Yes | Yes | Restricted review (blocked catalog) |
| SCM × Jackknife | Yes | Yes | Yes | Governed null-monitor |

---

## 7. Pairings reviewed

All pairings from `METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001` §12–14 marked absent, future, research, or under-classified, plus AugSynth inference family in full.

---

## 8. Pairing value scoring framework

For each pairing, document:

| Dimension | Description |
|-----------|-------------|
| `implementation_status` | `IMPLEMENTED` · `IMPLEMENTED_BUT_NOT_GOVERNED` · `NOT_IMPLEMENTED` · `BLOCKED` |
| `documentation_status` | ADR / D5 report / combo audit / none |
| `catalog_status` | Track B row / policy identity / none |
| `unique_causal_value` | What this pairing adds vs alternatives |
| `incremental_value_over_selected_instruments` | Low / medium / high vs SCM JK, TBRRidge KFold, AugSynth point/JK |
| `inference_assumption_risk` | Leakage, exchangeability, resampling dependence, estimand mismatch |
| `validation_cost` | Low / medium / high |
| `expected_usage_frequency` | Product / research / rare |
| `decision_surface_relevance` | null-monitor / diagnostic / research / none |
| `diagnostic_value` | Stress test / triangulation / calibration utility |
| `production_potential` | None / remote / blocked |
| `redundancy_with_existing_instruments` | High if duplicates SCM JK or TBRRidge KFold role |
| `recommended_priority` | Priority bucket (§8.1) |

### 8.1 Priority buckets

| Bucket | Meaning |
|--------|---------|
| `PURSUE_NOW` | Unique value + justified validation cost; enter active lane |
| `SAVE_FOR_LATER` | Implemented or plausible; validation deferred |
| `DIAGNOSTIC_ONLY` | Useful for stress/calibration; no promotion path |
| `RESEARCH_SANDBOX` | Exploratory; assumptions not governed |
| `BLOCK` | Invalid interface, high false-confidence risk, or not natural |
| `DEPRECATED` | Lineage only |
| `NEEDS_IMPLEMENTATION_STATUS_CORRECTION` | Prior audit misclassified implementation |
| `NEEDS_SEPARATE_VALIDATION_PLAN` | Requires dedicated validation artifact before any tier change |

---

## 9. Pairing implementation-status review

| Pairing | Code evidence | Documentation | Prior coverage error |
|---------|---------------|---------------|---------------------|
| AugSynth × KFold | `track_d_d5_inst_augsynth_kfold_001.py`; `AugSynthCVXPY_Kfold` | D5-KFOLD-001; ADR §2.4 | Yes — was `NOT_IMPLEMENTED` |
| AugSynth × Conformal | `track_d_d5_inst_augsynth_ascm_002.py`; D5-003 | ADR §2.3; 100% null FPR | Partially correct |
| AugSynth × Placebo | `explicit_block` in `test_d5_inst_augsynth_003.py` | ADR §2.5; combo audit | Yes — was `FUTURE_CANDIDATE` |
| AugSynth × Bootstrap/BRB | `explicit_block` in combo audit | `invalid_by_interface` | Correct as absent |
| TBRRidge × Jackknife | Not found | Future candidate in triage | Correct |
| TBRRidge × Conformal | Blocked TBRRIDGE-002 | D5_INST | Correct |
| DID × Bootstrap | Policy characterized; runtime deferred | DID estimand unification | Correct as diagnostic-only |

---

## 10. Pairing unique-value matrix

| Pairing | Unique value | vs SCM JK | vs TBRRidge KFold | vs AugSynth point/JK |
|---------|--------------|-----------|-------------------|----------------------|
| AugSynth × KFold | Fold-policy robustness on augmented path | Low — different estimand | Medium — parallel KFold diagnostic | Medium — adds fold CV beyond JK |
| AugSynth × Conformal | Score-based band on augmented residuals | Low | Low | Low — unsafe null FPR |
| AugSynth × Placebo | None as AugSynth pairing | N/A — SCM placebo separate | N/A | N/A |
| AugSynth × Bootstrap | None (blocked) | N/A | N/A | N/A |
| TBRRidge × BRB | Block-residual resampling diagnostic | Low | High within TBRRidge family | Medium |
| TBRRidge × Jackknife | Delete-one leverage (future) | Low | Medium | Low |
| SCM × Bootstrap/KFold | None | Redundant / not natural | N/A | N/A |
| DID × Placebo/JK | Future panel falsification | Low | Low | Low |

---

## 11. Pairing validation-cost matrix

| Pairing | Validation cost | Rationale |
|---------|-------------------|-----------|
| AugSynth × KFold | **Low–medium** | OC exists (D5-KFOLD-001); optional fold-policy sensitivity |
| AugSynth × Conformal | **High** (if pursued) | Band semantics broken; 100% null FPR — fix before any OC |
| AugSynth × JK coverage | **Medium** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` scoped |
| TBRRidge × KFold | **High** | Full evidence battery in progress |
| TBRRidge × BRB | **High** | Dependence + inverted-bounds remediation |
| DID × Bootstrap | **High** | Bootstrap executor + coverage deferred |

---

## 12. Pairing risk matrix

| Pairing | Primary risks |
|---------|---------------|
| AugSynth × KFold | Fold leakage from model selection; scale mismatch vs SCM JK; estimand non-equivalence |
| AugSynth × Conformal | Exchangeability failure; invalid band sign; 100% null interval-exclusion FPR |
| AugSynth × Placebo | Mis-labeling SCM falsification as AugSynth inference |
| AugSynth × Bootstrap | Resampling on augmented path — interface blocked |
| TBRRidge × BRB | Inverted bounds history; block dependence |
| TBRRidge × Conformal | TBRRIDGE-002 block; exchangeability |
| SCM × Conformal | Not natural; no documented path |
| DID × KFold | Not natural for panel DID |

---

## 13. Pairing prioritization decisions

| Pairing | Priority bucket | Rationale |
|---------|-----------------|-----------|
| **TBRRidge × KFold** | `PURSUE_NOW` (existing lane) | Selected restricted-review instrument; claim boundary next |
| AugSynth × Jackknife | `SAVE_FOR_LATER` | Research track; `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` |
| AugSynth × KFold | `DIAGNOSTIC_ONLY` | Implemented; robustness triangulation; low promotion value |
| AugSynth × Conformal | `DIAGNOSTIC_ONLY` | Implemented; triangulation only; unsafe for null-monitor |
| AugSynth × point-only | `DIAGNOSTIC_ONLY` / restricted | Already cataloged; point recovery diagnostic |
| AugSynth × Placebo | `BLOCK` | Explicit interface block; SCM falsification only |
| AugSynth × Bootstrap/BRB | `BLOCK` | Explicit interface block |
| TBRRidge × BRB | `SAVE_FOR_LATER` | `NEEDS_SEPARATE_VALIDATION_PLAN` |
| TBRRidge × Bootstrap | `SAVE_FOR_LATER` | Distinct from BRB |
| TBRRidge × Jackknife | `SAVE_FOR_LATER` | `FUTURE_CANDIDATE` |
| TBRRidge × Conformal | `BLOCK` | TBRRIDGE-002 |
| SCM × Bootstrap/KFold/Conformal | `BLOCK` | `NOT_NATURAL_FOR_ESTIMATOR` |
| DID × Bootstrap | `DIAGNOSTIC_ONLY` | Cataloged; runtime deferred |
| DID × Placebo/JK/Conformal | `SAVE_FOR_LATER` | `FUTURE_CANDIDATE` |
| DID × KFold | `BLOCK` | Not natural |

**No new pairing receives `PURSUE_NOW` beyond the existing TBRRidge KFold lane.**

---

## 14. AugSynth inference pairing review

### AugSynth × Bootstrap

| Field | Assessment |
|-------|------------|
| Implementation | **Blocked** — `AugSynthCVXPY_BlockResidualBootstrap` explicit block (combo audit, test_d5_inst_augsynth_003) |
| Unique value | None — BRB not in AugSynth catalog inference_support |
| Risks | Resampling on augmented synthetic control path unvalidated |
| **Decision** | `BLOCK` |

### AugSynth × Placebo

| Field | Assessment |
|-------|------------|
| Implementation | **Blocked** — `AugSynthCVXPY_Placebo` explicit_block |
| Unique value | None as AugSynth pairing — placebo is SCM falsification (A27) |
| Risks | Mis-labeling placebo as AugSynth uncertainty |
| **Decision** | `BLOCK` — not `FUTURE_CANDIDATE` |

### AugSynth × KFold

| Field | Assessment |
|-------|------------|
| Implementation | **Yes** — `D5-INST-AUGSYNTH-KFOLD-001`, `AugSynthCVXPY_Kfold` instrument_id |
| Documentation | ADR §2.4: robustness diagnostic only; 0% null FPR on 001e battery |
| Catalog | No Track B row — `IMPLEMENTED_BUT_NOT_GOVERNED` |
| Unique value | Fold-policy robustness; triangulation vs JK — **not** null-monitor substitute |
| vs TBRRidge KFold | Lower priority — TBRRidge KFold is active promotion lane |
| vs AugSynth JK | Incremental fold CV diagnostic; JK has credible research track |
| Leakage risk | Model selection / donor construction leakage if promoted without audit |
| **Decision** | `DIAGNOSTIC_ONLY` — `NEEDS_IMPLEMENTATION_STATUS_CORRECTION` for coverage audit |

### AugSynth × Jackknife

| Field | Assessment |
|-------|------------|
| Implementation | Yes — cataloged `AugSynthCVXPY_UnitJackKnife` |
| Unique value | Only AugSynth pairing with credible future promotion-audit research track (ADR) |
| Risks | Estimand bridge vs SCM JK; spillover DGP |
| **Decision** | `SAVE_FOR_LATER` — parallel `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` |

### AugSynth × Conformal

| Field | Assessment |
|-------|------------|
| Implementation | Yes — D5-003, ASCM-002 arms |
| Unique value | Low — 100% null interval-exclusion FPR; diagnostic triangulation only |
| Risks | Exchangeability; invalid band sign; not governed uncertainty |
| **Decision** | `DIAGNOSTIC_ONLY` — not `NOT_IMPLEMENTED` |

### AugSynth × point-only

| Field | Assessment |
|-------|------------|
| Implementation | Yes — governed catalog restricted |
| **Decision** | `DIAGNOSTIC_ONLY` / restricted review (unchanged from triage) |

---

## 15. TBRRidge non-selected pairing review

| Pairing | Decision | Notes |
|---------|----------|-------|
| TBRRidge × BRB | `SAVE_FOR_LATER` | Historical inverted bounds; dependence validation required |
| TBRRidge × Bootstrap | `SAVE_FOR_LATER` | Distinct from BRB; `NEEDS_SEPARATE_VALIDATION_PLAN` |
| TBRRidge × Jackknife | `SAVE_FOR_LATER` | Future candidate; leverage audit |
| TBRRidge × Conformal | `BLOCK` | TBRRIDGE-002 interface block |
| TBRRidge × Placebo | `DIAGNOSTIC_ONLY` | Already classified; secondary to SCM Placebo |

---

## 16. SCM / DID non-selected pairing review

| Pairing | Decision | Notes |
|---------|----------|-------|
| SCM × Bootstrap | `BLOCK` | Not natural — JK is standard SCM inference |
| SCM × KFold | `BLOCK` | Not natural for synthetic control |
| SCM × Conformal | `SAVE_FOR_LATER` | No documented path; low product priority |
| DID × Bootstrap | `DIAGNOSTIC_ONLY` | Runtime deferred; diagnostic until executor exists |
| DID × Placebo | `SAVE_FOR_LATER` | Future candidate |
| DID × Jackknife | `SAVE_FOR_LATER` | Not implemented |
| DID × Conformal | `SAVE_FOR_LATER` | Not implemented |
| DID × KFold | `BLOCK` | Not natural for panel DID |

---

## 17. Roadmap corrections required

1. **Correct coverage audit classifications** for AugSynth × KFold (implemented), × Conformal (implemented), × Placebo/Bootstrap (blocked not future).
2. **Pairing value audit** sits between pairing coverage and claim authorization boundary / geometry taxonomy.
3. **No new PURSUE_NOW pairings** — TBRRidge KFold lane remains primary.
4. **AugSynth KFold** — add to diagnostic comparator panel documentation; optional Track B catalog row as `characterized` only.
5. **Future pairings** must pass value audit before entering validation plans.
6. **Next artifact unchanged:** `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` — higher-priority correction is documentation-only (implementation status), not a new validation lane.

---

## 18. Save-for-later queue

| Pairing | Artifact / trigger |
|---------|-------------------|
| AugSynth × Jackknife | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` |
| TBRRidge × BRB | Dependence assumption validation audit |
| TBRRidge × Bootstrap | Separate from BRB validation plan |
| TBRRidge × Jackknife | Instrument definition + leverage audit |
| DID × Bootstrap | `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_004` then coverage audit |
| DID × Placebo / JK / Conformal | Catalog + value re-review |
| SCM × Conformal | Low priority — product trigger only |

---

## 19. Blocked/low-value queue

| Pairing | Reason |
|---------|--------|
| AugSynth × Placebo | Interface block; SCM falsification only |
| AugSynth × Bootstrap/BRB | Interface block |
| AugSynth × Conformal (promotion) | High null FPR — diagnostic triangulation only |
| TBRRidge × Conformal | TBRRIDGE-002 |
| SCM × Bootstrap / KFold | Not natural |
| DID × KFold | Not natural |
| TBR × Placebo | Geometry block |

---

## 20. Stop/go criteria

### Go

Proceed to `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` when value prioritization adopted and implementation-status corrections recorded.

### Stop

Stop when:

1. Implemented pairing labeled `NOT_IMPLEMENTED` without correction
2. Pairing promoted without value justification vs selected instruments
3. AugSynth Placebo treated as AugSynth inference path
4. Diagnostic pairing used for production authorization
5. PURSUE_NOW assigned without unique incremental value

---

## 21. Authorization boundary

**Allowed:** `method_pairing_value_prioritization_audit_completed`, `left_out_pairings_reviewed`, `implementation_status_reviewed`, `pairing_value_framework_defined`, `prioritization_decisions_defined`, `save_for_later_queue_defined`, `roadmap_corrections_defined`

**Forbidden:** `pairing_promoted`, `method_promoted`, `method_unblocked`, `estimator_family_promoted`, `instrument_promoted`, `catalog_unblocked`, all production/uncertainty/CI/significance/lift/ROI/inference/estimator/simulation/MMM/LLM flags

No pairing is promoted, implemented, or production-authorized by this audit.

---

## 22. Validation results

| Check | Result |
|-------|--------|
| Audit document complete | Pass |
| Summary JSON valid | Pass |
| Governance tests | Pass |

---

## 23. Known limitations

- **Value scores are qualitative** — not numeric ranking across families
- **Geometry not re-audited** — single-cell assumed for AugSynth KFold OC
- **Product priority** — expected usage frequency is judgment-based
- **Coverage audit** — corrections documented here; prior artifact not rewritten

---

## 24. Recommended next artifacts

| Priority | Artifact | Rationale |
|----------|----------|-----------|
| **Recommended** | `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` | Active TBRRidge KFold lane unchanged |
| **Alternative** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` | Highest-value AugSynth save-for-later pairing |
| **Deferred** | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` | Gate-triggered |
| **Optional** | `METHOD_INSTRUMENT_GEOMETRY_TAXONOMY_AUDIT_001` | Separate geometry dimension |
