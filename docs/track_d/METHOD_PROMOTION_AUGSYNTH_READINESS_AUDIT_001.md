# METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001` |
| **Artifact type** | `method_promotion_augsynth_readiness_audit` |
| **Lane** | Lane A — Method / instrument promotion framework readiness audit |
| **Status** | `completed` |
| **Scope** | `augsynth_readiness_audit_docs_only_no_contract_no_runtime_no_promotion` |
| **Final verdict** | `proceed_with_narrowed_augsynth_scope_before_evidence_packet_contract` |

**Depends on:**

- `METHOD_PROMOTION_GENERIC_RUNTIME_001`
- `METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001`
- `METHOD_PROMOTION_GENERIC_CONTRACTS_001`
- `METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001`
- `METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001`

---

## 2. Why this audit exists

The method promotion framework now has two completed instrument applications (TBRRidge restricted-review and SCM Jackknife null-monitor), a framework checkpoint, generic contracts, generic runtime contract, and a generic adapter runtime limited to those completed applications.

`METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001` ranked `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review` as the **secondary** candidate after SCM, citing high strategic value but higher method burden than TBRRidge or SCM null-monitor.

With the generic framework in place, AugSynth is the next plausible instrument lane — but AugSynth is **higher-risk** than the completed applications because:

- Augmented synthetic-control diagnostics, inference semantics, and estimand/scale bridges are more complex
- Catalog tier is `RESEARCH_SANDBOX` (RANK_1), not governed production
- JK coverage calibration is deferred; conformal paths are characterized but not governed uncertainty
- No AugSynth-specific claim-authorization boundary audit exists yet
- SCM null-monitor evidence cannot substitute for AugSynth evidence

This audit decides whether to proceed to an AugSynth evidence packet contract and under what **narrowed scope**. It does **not** implement runtime, contracts, promotion, or claim authorization.

---

## 3. Candidate instrument identity

**Proposed canonical instrument identity:**

`geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review`

| Part | Value | Meaning |
|------|-------|---------|
| `modality` | `geo` | Geo experimentation context |
| `estimator_family` | `augsynth` | Augmented synthetic control (AugSynthCVXPY) |
| `inference_family` | `jackknife` | Unit jackknife inference path |
| `geometry` | `single_cell` | Single treated cell geometry |
| `point_estimand` | `delta_mu` | Level-shift / mean-difference estimand |
| `interval_semantics` | `diagnostic_interval` | Diagnostic interval semantics only — not production confidence intervals |
| `surface` | `restricted_review` | Restricted review surface — not production readout or claim authorization |

**Possible aliases / related catalog identities (preserved separately; no alias substitution):**

| Related identity | Source | Relationship |
|------------------|--------|----------------|
| `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only` | `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` | Catalog-registered JK path; `research_interval` ≠ `diagnostic_interval`; RANK_1 research sandbox |
| `geo.augsynth.point.single_cell.delta_mu.point_only.restricted_or_research` | Catalog triage | Point-only AugSynth path; different inference semantics |
| `AugSynthCVXPY_UnitJackKnife` | Code / classification policy | Estimator implementation label; not a substitute for canonical dotted identity |
| `AugSynthCVXPY_Point` / ASCM naming | Development roadmap | Related estimator family; distinct from JK restricted-review lane |

Canonical identity must be used in future packet contracts. Catalog aliases may be emitted alongside canonical identity but cannot substitute for it (same rule as SCM null-monitor alias handling).

---

## 4. Readiness criteria

Each dimension scored: **READY**, **PARTIAL**, **NOT_READY**, **BLOCKED**, **NOT_APPLICABLE**.

| Dimension | Status | Rationale |
|-----------|--------|-----------|
| Exact instrument identity clarity | **PARTIAL** | Proposed identity is consistent with framework naming and next-instrument audit; not yet registered exactly in catalog (closest: `research_interval.research_only`) |
| Estimator/inference pairing clarity | **PARTIAL** | `AugSynthCVXPY_UnitJackKnife` implemented; ADR-001 and promotion-gate audit document JK as retire/replace or candidate-after-adapter; not governed uncertainty |
| Diagnostic evidence availability | **PARTIAL** | D5-DIAG-SCM-AUGSYNTH, ASCM-002/003, remediation plan exist; D8/D10/D11 gaps noted in development roadmap |
| Null-control / false-positive evidence | **PARTIAL** | JK null FPR 0.0 on ASCM-002 W2/W3 slice (n_mc=4); insufficient for promotion; larger OC needed per `D5-INF-AUGSYNTH-JK-CALIBRATION-001` |
| Directional-error evidence | **NOT_READY** | No governed AugSynth directional-error audit assembled for promotion packet |
| Positive-control / recovery evidence | **PARTIAL** | ASCM-002 weak-fit recovery (1/2 worlds); outside-hull W3 does not reliably beat A26 |
| Sensitivity evidence | **PARTIAL** | Outcome-model sensitivity (D8) incomplete in archived JSON |
| Donor-pool / support diagnostics | **PARTIAL** | D6 donor-hull labels provisional; `D5-DIAG-SCM-AUGSYNTH-001` scoped |
| Pre-period fit diagnostics | **PARTIAL** | SCM bridge evidence exists; AugSynth-specific pre-period fit bundle not assembled |
| Jackknife / uncertainty semantics clarity | **PARTIAL** | Estimand ≠ A26 JK; coverage validation deferred (`AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001`) |
| Evidence quality boundary clarity | **READY** | Generic framework + TBRRidge/SCM precedent: packet metadata only; no raw scoring |
| Claim boundary clarity | **NOT_READY** | No `AUGSYNTH_JK_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` or equivalent; catalog marks research-only |
| Catalog tier clarity | **READY** | RANK_1 `RESEARCH_SANDBOX`; not production-safe per classification policy |
| Production compatibility boundary | **BLOCKED** | `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`: production inference unauthorized; promotion gate not open |
| Generic adapter compatibility | **PARTIAL** | Generic contracts/runtime exist; AugSynth profile must not be added until packet + decision runtimes exist |
| Lane B / MIP separation clarity | **READY** | Framework checkpoint and generic contracts enforce Lane B non-substitution |
| Required next contract clarity | **READY** | Narrowed scope supports `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` as docs-only contract |

---

## 5. Evidence inventory

Artifacts classified by usability for AugSynth promotion packet readiness. **No evidence fabricated.**

| Artifact | Classification | Usability notes |
|----------|----------------|-----------------|
| `METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001` | method roadmap support | Ranks AugSynth secondary; lists missing JK coverage, estimand alignment, claim boundary |
| `METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001` | method roadmap support | Identifies AugSynth/DID gaps before scaling; reusable patterns from TBRRidge/SCM |
| `METHOD_PROMOTION_GENERIC_CONTRACTS_001` | method roadmap support | Generic identity, packet, decision abstractions for future mapping |
| `METHOD_PROMOTION_GENERIC_RUNTIME_001` | method roadmap support | Adapter exists for TBRRidge/SCM only; AugSynth not supported |
| `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` | direct AugSynth readiness evidence | Registers AugSynth JK as RANK_1 research sandbox; distinct from proposed diagnostic_interval identity |
| `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001` | method roadmap support | Identity grammar; AugSynth JK research-only example |
| `AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001` | diagnostic-only support | Lane closed; P1–P6 evidence; `promotion_audit_eligible: false` |
| `AUGSYNTH_ASCM_LANE_CLOSEOUT_001` | method roadmap support | Development lane paused; not promotion-ready |
| `D5_INST_AUGSYNTH_ASCM_002_REPORT` / results JSON | direct AugSynth readiness evidence | OC comparison vs A26; JK FPR 0.0 on small slice; outside-hull weakness |
| `D5_INST_AUGSYNTH_ASCM_003_REPORT` | direct AugSynth readiness evidence | Hull/disagreement follow-up (partial) |
| `D5_DIAG_SCM_AUGSYNTH_001_REPORT` | diagnostic-only support | Donor-hull, weight concentration, false-confidence diagnostics |
| `D5_INF_AUGSYNTH_JK_CALIBRATION_001_REPORT` | future work | JK calibration path; not complete for promotion |
| `D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_REPORT` | insufficient / not usable for evidence packet | Conformal failure isolation; not governed uncertainty |
| `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001` | related SCM/synthetic-control evidence | SCM stronger candidate; AugSynth production blocked |
| `SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001` | diagnostic-only support | Threshold vocabulary provisional |
| `AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001` | direct AugSynth readiness evidence | Fidelity gaps; supports restricted-review only |
| `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001` | future work | Remediation plan; not assembled packet evidence |
| `DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001` | method roadmap support | Readout compatibility; not method-validity packet |
| `PHASE14_AUGSYNTH_CHARACTERIZATION_001` | diagnostic-only support | Characterization; research posture |
| `SCM_JACKKNIFE_NULL_MONITOR_*` (full chain) | related SCM/synthetic-control evidence | Proves framework pattern; **cannot substitute** for AugSynth categories |
| `TBRRIDGE_PROMOTION_*` (full chain) | related SCM/synthetic-control evidence | Proves restricted-review pattern; **cannot substitute** for AugSynth augmentation diagnostics |
| AugSynth-specific claim boundary audit | **missing** | Required before unrestricted restricted-review decision semantics |
| AugSynth null-control bundle for augmented path | **missing** | Listed as likely missing in next-instrument audit |
| AugSynth JK coverage validation at promotion depth | **missing** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` deferred |

---

## 6. Readiness assessment table

| Criterion | Status | Supporting artifact(s) | Gap / blocker | Implication for next artifact |
|-----------|--------|------------------------|---------------|-------------------------------|
| Identity | PARTIAL | Next-instrument audit; classification policy | Catalog uses `research_interval.research_only`; proposed `diagnostic_interval.restricted_review` must be declared in contract | Contract must fix exact canonical identity |
| Inference pairing | PARTIAL | ADR-001; promotion-gate audit; ASCM-002 | JK not governed uncertainty; estimand bridge open | Packet contract references only; no inference runtime |
| Diagnostic evidence | PARTIAL | D5-DIAG-SCM-AUGSYNTH; ASCM-002/003 | D8/D10/D11 incomplete | Require augmentation-specific diagnostic categories |
| Null-control | PARTIAL | ASCM-002 JK FPR slice | n_mc=4; not promotion depth | Category required; evidence refs may be partial |
| Claim boundary | NOT_READY | Catalog triage (research-only) | No AugSynth claim-boundary audit | Contract must prohibit all claim surfaces |
| Production/catalog | BLOCKED | Promotion-gate audit; ROADMAP blocklist | Production inference unauthorized | Defer production compatibility lane |
| Framework fit | READY | Generic contracts; TBRRidge/SCM chains | None for contract-only step | Reuse packet contract pattern |
| Generic adapter | PARTIAL | Generic runtime | No AugSynth profile until runtimes exist | Do not modify generic runtime |
| Restricted-review packet | PARTIAL | TBRRidge/SCM precedents | AugSynth-specific categories undefined | **Proceed** to evidence packet contract with narrowed scope |

---

## 7. Proposed narrowed scope

If proceeding, scope is limited to:

`geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review`

**Allowed:**

- Restricted-review evidence packet **contract** (docs/tests only)
- Diagnostic interval semantics only
- Evidence reference assembly contract definition only
- Instrument-specific AugSynth diagnostic categories as references
- Mapping to generic status families in contract text (not runtime)

**Disallowed:**

- Production readout
- Causal/business lift claims
- Statistical significance claims
- CI / p-value / power claims
- Method promotion
- Instrument promotion
- Catalog unblock
- Production compatibility authorization
- MIP DecisionSurface approval
- TrustReport or claim-authorization bypass
- Generic adapter profile for AugSynth (until packet + decision runtimes exist)

---

## 8. Required evidence categories for future packet contract

**Core categories** (shared with TBRRidge/SCM framework):

- `instrument_identity`
- `claim_boundary`
- `metric_estimand_alignment`
- `null_control_false_positive`
- `directional_error`
- `positive_control_recovery`
- `sensitivity`
- `readout_compatibility`

**AugSynth-specific categories:**

- `donor_pool_diagnostics`
- `pre_period_fit_diagnostics`
- `augmentation_component_diagnostics`
- `synthetic_weight_diagnostics`
- `regularization_or_model_component_diagnostics`
- `jackknife_stability`
- `method_disagreement_or_scm_bridge`
- `support_overlap_or_donor_hull_stress`

**Optional / future** (not required for initial contract):

- `placebo_evidence`
- `conformal_evidence`
- `bootstrap_evidence`
- `production_compatibility`
- `catalog_governance`

---

## 9. Blockers and warnings

### Blockers

- `BLOCKED_MISSING_CANONICAL_IDENTITY` — packet input without exact canonical identity
- `BLOCKED_MISSING_CLAIM_BOUNDARY` — no claim-boundary evidence reference
- `BLOCKED_MISSING_NULL_CONTROL_EVIDENCE` — null-control category absent
- `BLOCKED_MISSING_DONOR_POOL_DIAGNOSTICS` — donor-pool / hull diagnostics absent
- `BLOCKED_MISSING_PRE_PERIOD_FIT_DIAGNOSTICS` — pre-period fit diagnostics absent
- `BLOCKED_UNSUPPORTED_PRODUCTION_SURFACE` — production readout or compatibility surface requested
- `BLOCKED_UNSUPPORTED_CATALOG_SURFACE` — catalog unblock surface requested
- `BLOCKED_RAW_EVIDENCE_QUALITY_SCORING` — packet assembly inspects or scores raw evidence
- `BLOCKED_CLAIM_AUTHORIZATION_ATTEMPT` — claim authorization implied or granted
- `BLOCKED_GENERIC_ADAPTER_AS_SOURCE_OF_TRUTH` — generic adapter used instead of instrument-specific runtime

### Warnings

- AugSynth may inherit SCM **assumptions** but not SCM **evidence**
- SCM null-monitor evidence cannot substitute for AugSynth evidence categories
- TBRRidge evidence cannot substitute for AugSynth augmentation diagnostics
- Restricted-review continuation approval would not imply causal claim validity
- Diagnostic interval semantics must not be presented as production confidence intervals
- `research_interval.research_only` catalog identity must not be silently conflated with `diagnostic_interval.restricted_review`
- Outside-hull / extrapolation behavior remains a method-validity risk (ASCM-002 W3)

---

## 10. Generic framework compatibility

Compatible with generic abstractions from `METHOD_PROMOTION_GENERIC_CONTRACTS_001`:

| Abstraction | Compatibility |
|-------------|---------------|
| `MethodPromotionInstrumentIdentity` | Proposed 7-part identity fits grammar; surface = `restricted_review` |
| `MethodPromotionEvidenceReference` | Reusable; AugSynth-specific categories extend registry |
| `MethodPromotionEvidencePacket` | Reusable shape; instrument-specific readiness labels (e.g. `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT` analog) |
| `MethodPromotionReviewDecision` | Future; not in scope for this audit |
| Generic runtime adapter profile | **Not yet** — `METHOD_PROMOTION_GENERIC_RUNTIME_001` supports TBRRidge and SCM only |

Future AugSynth artifacts must map instrument-specific statuses to generic status families per `METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001`, but **must not** be added to the generic adapter runtime until AugSynth packet and decision runtimes exist and are source of truth.

---

## 11. Decision

**Decision:** `PROCEED_WITH_NARROWED_AUGSYNTH_SCOPE`

**Rationale:**

- Enough structural precedent exists (TBRRidge restricted-review + SCM null-monitor + generic contracts) to draft an AugSynth evidence packet **contract**
- Existing diagnostic and OC artifacts support a **restricted diagnostic/review lane** definition
- Evidence is **not** sufficient to promote AugSynth, unblock catalog, authorize production compatibility, or authorize production readout / causal / statistical claims
- Full unrestricted AugSynth promotion is **not** approved (`proceed_to_unrestricted_augsynth: false`)
- Future work must remain evidence-reference based with strict claim/catalog/production prohibitions

**Rejected alternatives for now:**

| Alternative | Why not now |
|-------------|-------------|
| `PROCEED_TO_AUGSYNTH_EVIDENCE_PACKET_CONTRACT` (unrestricted) | Claim boundary and several core categories NOT_READY |
| `DEFER_AUGSYNTH_PENDING_METHOD_EVIDENCE` | Sufficient diagnostic roadmap exists to define contract shape |
| `DEFER_AUGSYNTH_PENDING_IDENTITY_OR_BOUNDARY_CLARITY` | Identity grammar clear; boundary clarity achievable in contract prohibitions |

---

## 12. Recommended next artifact

**`AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001`**

| Field | Value |
|-------|-------|
| Type | docs/tests-only contract |
| Exact identity | `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| Scope | Evidence references only; restricted-review surface only |
| Excludes | Runtime, promotion, claim authorization |

---

## 13. Alternative next artifacts

| Artifact | Disposition |
|----------|-------------|
| `METHOD_PROMOTION_DID_READINESS_AUDIT_001` | Defer until AugSynth narrowed lane contract is drafted |
| `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` | Premature — contract first |
| `AUGSYNTH_REVIEW_DECISION_CONTRACT_001` | Premature — packet contract/runtime first |
| `AUGSYNTH_JK_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` | Parallel optional; packet contract can require claim_boundary category |
| Catalog unblock lane | Premature — RANK_1 research sandbox |
| Production compatibility lane | Premature — promotion gate blocked for AugSynth |

---

## 14. Non-goals

This audit explicitly does **not**:

- Implement AugSynth runtime
- Implement AugSynth evidence packet contract or decision contract
- Modify generic runtime or add AugSynth adapter profile
- Modify TBRRidge/SCM runtimes
- Promote any method or instrument
- Unblock catalog
- Authorize production compatibility
- Change claim authorization
- Authorize statistical, CI, p-value, significance, power, causal, business lift, ROI/ROAS, or decision-recommendation claims
- Authorize production readout
- Implement estimator/inference behavior
- Run new validation experiments
- Score raw evidence quality
- Modify Lane B runtime
- Implement MIP decisioning
- Bypass TrustReport or claim authorization

---

## 15. Validation results

- Summary JSON: `docs/track_d/archives/METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001_summary.json`
- Governance tests: `tests/governance/test_method_promotion_augsynth_readiness_audit_001.py`
- Safety grep: no forbidden `true` flags in audit doc or summary
- Capability grep: readiness audit completion flags `true`
