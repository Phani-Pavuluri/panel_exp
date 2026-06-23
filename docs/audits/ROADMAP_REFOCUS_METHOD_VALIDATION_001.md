# ROADMAP-REFOCUS-METHOD-VALIDATION-001

**Artifact ID:** ROADMAP-REFOCUS-METHOD-VALIDATION-001  
**Type:** Planning / audit (governance refocus)  
**Date:** 2026-06-03  
**Branch:** `audit/roadmap-refocus-method-validation-001`  
**Summary:** [`docs/track_d/archives/ROADMAP_REFOCUS_METHOD_VALIDATION_001_summary.json`](../track_d/archives/ROADMAP_REFOCUS_METHOD_VALIDATION_001_summary.json)

---

## 1. Executive summary

The TrustReport research-mode governance stack (downstream promotion → integration dry-run → renderer → artifact export → review workflow → access control) is **complete enough for package-level governance**. Continuing TrustReport product-ops (audit log, review queue, UI, API, scheduler, platform rollout) would not increase the number of **usable causal methods** in `panel_exp`.

**Primary decision:** Refocus the package on **method validity** — blocked estimator/inference configurations, design-to-readout bridges, multi-treated placebo/randomization inference, AugSynth disposition, TBRRidge replacement inference, multicell multiplicity, and stratified estimand gaps.

**Governance verdict:** `refocus_on_method_validation`  
**TrustReport ops status:** `freeze_after_research_mode_access_control`  
**Next artifact:** `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001`

Only **two** DCM rows have restricted research-mode TrustReport paths today (DCM-001 SCM+JK, DCM-004 DID+bootstrap). Global `trust_report_authorized` remains **false**. Further ops work is deferred to the future MIP application/orchestration layer.

---

## 2. Why this audit exists

The program completed a long TrustReport qualification spine:

- Matrix reassessment (`FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001`)
- BRB variance remediation and terminal `DIAGNOSTIC_ONLY` adjudication
- Restricted row-level promotion for DCM-001/004
- Research-mode integration dry-run and renderer/export/review/access-control chain

That work answered **governance and packaging** questions for a narrow eligible subset. It did **not** resolve the broader method-validity backlog:

| Gap class | Example |
|-----------|---------|
| Design ↔ readout bridge | Rerandomization not connected to inference; supergeo/trim bridges undefined |
| Multi-treated inference | SCM Placebo single-treated only; multi-treated blocked (A28) |
| Estimator remediation | AugSynth JK diagnostic-only; TBRRidge BRB/KFold terminal |
| Multicell statistics | Familywise type-I ~27%; shared-control correlation ~0.90 |
| Stratified estimand | DCM-008 aggregate readout is characterization only |

Without this refocus, the roadmap would continue sequencing TrustReport ops artifacts that do not unblock additional causal methods.

---

## 3. Current TrustReport governance state

| Item | State |
|------|-------|
| Global `trust_report_authorized` | **false** |
| DCM-001 SCM + UnitJackknife | `ELIGIBLE_WITH_RESTRICTIONS` — restricted research-mode path only |
| DCM-004 DID + bootstrap | `ELIGIBLE_WITH_RESTRICTIONS` — restricted research-mode path only |
| DCM-005 BRB | `BRB_DIAGNOSTIC_ONLY` — null calibration failed post-remediation |
| DCM-005 KFold | `DIAGNOSTIC_ONLY` |
| DCM-005 Placebo | `NULL_MONITOR_ONLY` |
| DCM-006 multicell | `PER_CELL_RESTRICTED` — marginal per-cell; no global/winner/pooled |
| DCM-008 stratified SCM+JK | `DIAGNOSTIC_ONLY` — aggregate characterization only |
| Research-mode ops chain | ✅ Complete through access control |
| CalibrationSignal | false for all rows |
| Live API / scheduler / production decisioning | blocked |

**TrustReport ops freeze (explicit):**

> TrustReport research-mode operationalization is complete enough for package-level governance. Further operational artifacts such as audit log, review queue, UI access surface, API contract, scheduler readiness, live API readiness, and platform rollout are **deferred to the future MIP application/orchestration layer**.

`panel_exp` will refocus on method validity, blocked estimator/inference configurations, multi-treated placebo/randomization inference, AugSynth disposition, TBRRidge replacement inference, multicell multiplicity, and stratified estimand gaps.

---

## 4. Current usable method set

Methods **usable** under governed restrictions (not global platform promotion):

| Row | Combination | Usable scope | Key gates |
|-----|-------------|--------------|-----------|
| **DCM-001** | SCM + UnitJackknife | Restricted research-mode TrustReport | Null coverage ~93%; positive coverage ~90% post harness correction; type-I caveats; geometry restrictions apply |
| **DCM-004** | DID + bootstrap | Restricted research-mode TrustReport | Positive coverage ~93%; common timing + parallel-trends required; unsupported stress worlds excluded |

**Marginal readout (not TrustReport promotion):**

| Context | Combination | Scope |
|---------|-------------|-------|
| DCM-006 | SCM+JK per-cell | `PARALLEL_MARGINAL_CELLS` + `REPORT_EACH_CELL_ONLY` per [`MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001`](../MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001.md) |
| DCM-002 | AugSynth point | Point-only comparator; no governed interval path |

These are **usable for characterized scopes**, not blanket causal-interval or platform authorization.

---

## 5. Blocked / diagnostic-only method set

### Diagnostic-only (terminal or active remediation)

| Item | Combination | Verdict | Gate failure |
|------|-------------|---------|--------------|
| DCM-005-BRB | TBRRidge + BRB | `BRB_DIAGNOSTIC_ONLY` | Null type-I ~50%, null coverage ~50% post-remediation |
| DCM-005-KFOLD | TBRRidge + KFold | `DIAGNOSTIC_ONLY` | Not causal-interval eligible |
| DCM-005-PLACEBO | TBRRidge + Placebo | `NULL_MONITOR_ONLY` | Falsification only |
| DCM-008 | Stratified SCM+JK | `DIAGNOSTIC_ONLY` | Aggregate type-I ~26%; aggregate claims blocked |
| — | AugSynthCVXPY + JK | `DIAGNOSTIC_ONLY` | Estimand/scale bridge open |
| — | TBRRidge + JK | `known_failure_mode` | ~79% null FPR (A16) |
| — | SCM + Placebo | `NULL_MONITOR_ONLY` | Single-treated scope only |

### Blocked (statistical or semantic gates)

| Item | Combination | Blocker type |
|------|-------------|--------------|
| DCM-003 | TBR aggregate | Geometry mismatch |
| DCM-006 global | Multi-cell winner/pooled/simultaneous | Multiplicity unresolved (~27% familywise type-I) |
| DCM-007 | Pooled multi-cell | Permanent exclusion |
| — | SCM + Placebo multi-treated | Scope limitation (A28) |
| DCM-009–019 | Adapter combinations | `INSUFFICIENT_EVIDENCE` |

---

## 6. Roadmap items to pause

| Item | Classification | Rationale |
|------|----------------|-----------|
| `TRUSTREPORT_RESEARCH_MODE_AUDIT_LOG_001` | `DEFER_PLATFORM_LAYER` | Ops artifact; no method validity gain |
| TrustReport review queue / UI | `DEFER_PLATFORM_LAYER` | MIP application layer |
| Live API readiness | `DEFER_PLATFORM_LAYER` | Requires methods + platform |
| Scheduler readiness | `DEFER_PLATFORM_LAYER` | Orchestration layer |
| Platform rollout | `DEFER_PLATFORM_LAYER` | Premature before method expansion |
| Downstream authorization update | `DEFER_UNTIL_METHODS_PASS` | Global auth correctly false |
| CalibrationSignal production wiring | `DEFER_PRODUCT_OPS` | No eligible calibration paths |
| MMM ingestion promotion | `DEFER_UNTIL_METHODS_PASS` | Blocked by AUDIT-010 gaps |
| DCM-009–019 adapter qualification | `DEFER_UNTIL_METHODS_PASS` | Parallel later lane |
| Full matrix v2 | `DEFER_UNTIL_METHODS_PASS` | After core DCM-001–008 method gaps |

---

## 7. Roadmap items to keep active

| Priority | Artifact | Classification |
|----------|----------|----------------|
| P0 | Merge/checkpoint TrustReport stack | `KEEP_ACTIVE_METHOD_VALIDATION` |
| P1 | `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001` | `KEEP_ACTIVE_ESTIMAND_DESIGN` |
| P2 | `DESIGN_AWARE_ASSIGNMENT_GENERATORS_001` | `KEEP_ACTIVE_ESTIMAND_DESIGN` |
| P3 | `SCM_PLACEBO_GOVERNED_SEMANTICS_001` | `KEEP_ACTIVE_DIAGNOSTIC_DISPOSITION` |
| P4 | `AUGSYNTH_JK_TRUSTREPORT_DISPOSITION_001` | `KEEP_ACTIVE_ALGORITHM_REMEDIATION` |
| P5 | `TBRRIDGE_INFERENCE_REPLACEMENT_SCOUT_001` | `KEEP_ACTIVE_ALGORITHM_REMEDIATION` |
| P6 | `MULTICELL_MULTIPLICITY_CALIBRATION_001` | `KEEP_ACTIVE_METHOD_VALIDATION` |
| P7 | `MULTICELL_SHARED_CONTROL_DEPENDENCE_001` | `KEEP_ACTIVE_METHOD_VALIDATION` |
| P8 | `STRATIFIED_POOLED_ESTIMAND_CONTRACT_001` | `KEEP_ACTIVE_ESTIMAND_DESIGN` |
| — | `D5-INST-TBR-001` | `KEEP_ACTIVE_METHOD_VALIDATION` |
| — | `D5-INST-AUGSYNTH-ASCM-003` | `KEEP_ACTIVE_ALGORITHM_REMEDIATION` |

### Completed items (close, do not extend)

| Item | Classification |
|------|----------------|
| `FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001` | `CLOSE_AS_COMPLETED` |
| `TRUSTREPORT_DOWNSTREAM_PROMOTION_001` through access control | `CLOSE_AS_COMPLETED` |
| `D5-TRUST-MULTICELL-PERCELL-INFERENCE-001` | `CLOSE_AS_COMPLETED` |
| `MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001` | `CLOSE_AS_COMPLETED` |
| `DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001` | `CLOSE_AS_DIAGNOSTIC_ONLY` |
| `D5-TRUST-STRATIFIED-SCM-JK-001` | `CLOSE_AS_DIAGNOSTIC_ONLY` |

---

## 8. Open investigations triage

| Investigation | Status | Priority | Action |
|---------------|--------|----------|--------|
| `INV-MULTICELL-MULTIPLICITY-CALIBRATION-001` | `DEFERRED_WITH_TRIGGER` | **P1 method** | **KEEP_ACTIVE** → `MULTICELL_MULTIPLICITY_CALIBRATION_001` |
| `INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001` | `DEFERRED_WITH_TRIGGER` | **P2 method** | **KEEP_ACTIVE** → `MULTICELL_SHARED_CONTROL_DEPENDENCE_001` |
| `INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001` | `RESOLVED` | — | Terminal `DIAGNOSTIC_ONLY`; no reopen |
| `INV-TBRRIDGE-KFOLD-NULL-FPR-001` | `RESOLVED` | — | Terminal `DIAGNOSTIC_ONLY` |
| `INV-TBRRIDGE-PLACEBO-GOVERNED-SEMANTICS-001` | `RESOLVED` | — | `NULL_MONITOR_ONLY` |
| `INV-AUGSYNTH-JK-TRUSTREPORT-DISPOSITION-001` | `RESOLVED` | P4 | Package contract lane still needed |
| `INV-SCM-PLACEBO-GOVERNED-SEMANTICS-001` | `RESOLVED` | P3 | Package contract lane still needed |
| `INV-MULTICELL-PERCELL-INFERENCE-001` | `RESOLVED` | — | `PER_CELL_RESTRICTED` |
| `INV-STRATIFIED-SCM-JK-TRUSTREPORT-DISPOSITION-001` | `RESOLVED` | P8 | Pooled estimand contract needed |

**No method investigations closed by this audit** beyond confirming terminal dispositions already recorded.

---

## 9. Method-validity priority ranking

| Rank | Artifact | Why |
|------|----------|-----|
| **P0** | Merge/checkpoint TrustReport stack | Preserve restricted DCM-001/004 governance baseline |
| **P1** | `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001` | Placebo falsification blocked for multi-treated GeoX designs (A28) |
| **P2** | `DESIGN_AWARE_ASSIGNMENT_GENERATORS_001` | G-DES-001–014; rerandomization not connected to inference |
| **P3** | `SCM_PLACEBO_GOVERNED_SEMANTICS_001` | Null-monitor product class needs package contract |
| **P4** | `AUGSYNTH_JK_TRUSTREPORT_DISPOSITION_001` | Active development lane; estimand gap blocks usable readout |
| **P5** | `TBRRIDGE_INFERENCE_REPLACEMENT_SCOUT_001` | BRB/KFold terminal; scout replacement before more TBRRidge work |
| **P6** | `MULTICELL_MULTIPLICITY_CALIBRATION_001` | Familywise decisioning blocked |
| **P7** | `MULTICELL_SHARED_CONTROL_DEPENDENCE_001` | Cross-cell correlation ~0.90 |
| **P8** | `STRATIFIED_POOLED_ESTIMAND_CONTRACT_001` | Aggregate stratified readout undefined as causal estimand |

Order matches repo evidence: design/inference gaps (P1–P2) precede disposition contracts (P3–P4) and estimator replacement (P5); multicell/stratified follow as combination-specific lanes.

---

## 10. Next 3 recommended artifacts

1. **`MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001`** — Define governed multi-treated placebo/randomization inference scope; unblock GeoX falsification beyond single-treated SCM Placebo.

2. **`DESIGN_AWARE_ASSIGNMENT_GENERATORS_001`** — Bridge design assignment modes (rerandomization, stratified, supergeo, trim) to characterized readout contracts.

3. **`SCM_PLACEBO_GOVERNED_SEMANTICS_001`** — Package-level null-monitor contract for SCM Placebo (complement to multi-treated framework).

---

## 11. Items deferred to MIP application/orchestration layer

- `TRUSTREPORT_RESEARCH_MODE_AUDIT_LOG_001`
- TrustReport review queue and UI access surface
- Live API contract and readiness harnesses
- Scheduler readiness and job orchestration
- Global TrustReport platform rollout
- CalibrationSignal production wiring
- MMM ingestion promotion (pending AUDIT-010)
- Production decisioning and budget optimization surfaces

These belong outside core `panel_exp` method validation.

---

## 12. Risks if we continue TrustReport ops too early

| Risk | Impact |
|------|--------|
| **False progress signal** | Ops completeness mistaken for method readiness |
| **Narrow usable surface frozen** | Only DCM-001/004 research-mode paths while GeoX needs multi-treated, multicell, stratified |
| **Engineering drain** | Audit log/UI/API work does not fix BRB null calibration or multiplicity |
| **Premature authorization pressure** | Downstream auth update could erode fail-closed governance |
| **Neglected design bridges** | Rerandomization and assignment generators remain disconnected |

---

## 13. Final recommendation

1. **Freeze** TrustReport product-ops after `TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001`.
2. **Checkpoint** the TrustReport stack on main (merge when ready).
3. **Activate** method-validation lane starting with `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001`.
4. **Maintain** fail-closed global `trust_report_authorized: false` until additional combinations pass statistical and semantic gates.
5. **Do not** schedule audit log, live API, scheduler, or platform rollout in `panel_exp`.

**Answer to primary decision:** `panel_exp` should focus next on making **more estimator/inference/design combinations actually usable** — starting with multi-treated placebo/randomization and design-aware assignment bridges — not on operationalizing TrustReport for a two-row research-mode subset.

---

## 14. Residual issues and handoff

**Resolved by this audit:**

- TrustReport ops sequencing question → **frozen** after access control
- Roadmap active lane → **method validation**

**Unchanged deferred investigations:**

- `INV-MULTICELL-MULTIPLICITY-CALIBRATION-001`
- `INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001`

**Regenerate:** docs-only artifact; no simulation harness.

**Next artifact:** `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001`

---

## Appendix A — Audit question answers

| # | Question | Answer |
|---|----------|--------|
| 1 | Method-validity blockers? | Multi-treated placebo; design/readout bridges; AugSynth estimand; TBRRidge inference replacement; multicell multiplicity/shared-control; stratified pooled estimand |
| 2 | Product/ops to pause? | Audit log, API, scheduler, platform rollout, downstream auth, CalibrationSignal wiring |
| 3 | Usable combinations? | DCM-001 SCM+JK; DCM-004 DID+bootstrap (restricted research-mode) |
| 4 | Diagnostic-only? | BRB, KFold, DCM-008 aggregate, AugSynth JK, TBRRidge JK, SCM/TBRRidge Placebo |
| 5 | Failed statistical gates? | BRB null calibration; multicell familywise type-I; stratified aggregate type-I; TBRRidge JK FPR |
| 6 | Failed semantic/governance gates? | TBR aggregate geometry; pooled multicell; null-monitor as causal; global TrustReport |
| 7 | GeoX priority blockers? | Multi-treated placebo; design generators; multicell multiplicity |
| 8 | High-priority open investigations? | Multicell multiplicity (P1); shared-control dependence (P2) |
| 9 | Move to MIP layer? | TrustReport ops, live API, scheduler, platform, CalibrationSignal production |
| 10 | Next 3 artifacts? | MULTITREATED framework; design-aware generators; SCM Placebo semantics |

## Appendix B — Full classification table

See [`ROADMAP_REFOCUS_METHOD_VALIDATION_001_summary.json`](../track_d/archives/ROADMAP_REFOCUS_METHOD_VALIDATION_001_summary.json) `item_classifications` for machine-readable entries.
