# METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001` |
| **Artifact type** | `method_promotion_next_instrument_selection_audit` |
| **Lane** | **Lane A — Method / instrument promotion framework** |
| **Status** | `completed` |
| **Scope** | `next_instrument_selection_audit_docs_only_no_runtime_no_promotion` |
| **Final verdict** | `next_instrument_selected_for_framework_application_no_runtime_no_promotion` |
| **Recommended next** | `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` |

**Depends on:**

- `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001`
- `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001`
- `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001`
- `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001`
- `METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001`
- `METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001`

**Pilot instrument (complete, do not deepen):** `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review`

---

## 2. Why this audit exists

The TBRRidge × KFold restricted-review pilot is complete through evidence packet assembly, review decision contract/runtime, and framework generalization. **The next instrument lane must be chosen by explicit criteria — not intuition, not estimator-family habit, and not by continuing to deepen the TBRRidge KFold config.**

This audit ranks five candidate instruments using evidence availability, missing-evidence burden, methodological risk, governance risk, platform value, implementation cost, framework fit, and roadmap priority. It avoids over-investing in one config and prevents accidental method-family promotion.

---

## 3. Selection criteria

Each criterion scored **1–5** (higher is better). Reverse-scored dimensions use **5 = lowest burden / lowest risk / lowest cost**.

| Criterion | 1 (worst) | 5 (best) | Notes |
|-----------|-----------|----------|-------|
| **Evidence availability** | No assembled evidence | Strong governed evidence chain | Existing audits, diagnostics, catalog refs |
| **Missing evidence burden** (reverse) | Large evidence gap | Minimal gap to packet-ready | Core categories + method-specific diagnostics |
| **Methodological risk** (reverse) | High validity uncertainty | Well-characterized method path | Inference semantics, calibration history |
| **Governance risk** (reverse) | High claim/catalog risk | Clean null-monitor / restricted surfaces | Claim boundary clarity |
| **Platform/readout value** | Minimal readout utility | High strategic readout value | Trusted readout / MIP handoff potential |
| **Implementation cost** (reverse) | High new artifact cost | Reuses existing stack | Contract/runtime pattern reuse |
| **Framework fit** | TBRRidge-specific inheritance trap | Clean second framework application | Proves generalization |
| **Roadmap priority** | Deferred / blocked | Active parallel lane | ROADMAP, pairing value, catalog tier |

**Weighting:** Equal weight (1× each); **total max = 40**. Narrative notes required per candidate; scores alone do not authorize promotion.

---

## 4. Candidate evaluation table

Catalog references from `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` and pairing audits. Where exact promotion-packet evidence is absent: `evidence_unknown_or_not_yet_assembled`.

| Candidate instrument | Status / tier | Evid | Miss↓ | Meth↓ | Gov↓ | Value | Cost↓ | Fit | Road | **Total** | Blockers | Recommended action |
|----------------------|---------------|------|-------|-------|------|-------|-------|-----|------|-----------|----------|-------------------|
| `geo.tbrridge.brb.single_cell.delta_mu.diagnostic_interval.restricted_review` | RESEARCH_SANDBOX / RANK_0 blocked | 2 | 2 | 2 | 3 | 2 | 3 | 3 | 2 | **19** | BRB dependence; inverted-bounds history; cannot inherit KFold packet | **WAIT** — BRB validation plan first |
| `geo.tbrridge.placebo.single_cell.delta_mu.diagnostic_interval.restricted_review` | DIAGNOSTIC_ONLY / RANK_2 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 2 | **24** | Placebo ≠ interval semantics; TBRRidge claim boundary not defined for placebo surface | **WAIT** — claim-boundary audit first |
| `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review` | RESEARCH_SANDBOX / RANK_1 | 3 | 2 | 2 | 2 | 5 | 2 | 4 | 4 | **24** | Estimand bridge open; JK coverage deferred; high method burden | **SECONDARY** — after framework sanity check |
| `geo.scm.jackknife.single_cell.delta_mu.null_monitor` | GOVERNED / RESTRICTED_REVIEW RANK_3 | 3 | 4 | 4 | 5 | 3 | 4 | 5 | 4 | **32** | SCM JK promotion evidence not fully assembled; catalog identity variant | **SELECT** — primary next lane |
| `geo.did.bootstrap.single_cell.delta_mu.diagnostic_interval.restricted_review` | DIAGNOSTIC_ONLY / RANK_0 blocked | 2 | 1 | 2 | 2 | 4 | 2 | 3 | 2 | **18** | Bootstrap runtime deferred; parallel-trends burden | **DEFER** — remediation chain first |

**Catalog identity note:** Triaged SCM JK null-monitor is registered as `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review` (`SCM_UnitJackKnife`, RANK_3). Candidate identity uses `single_cell` geometry and `null_monitor` surface — aligned in intent; packet contract must reconcile exact identity string.

---

## 5. Candidate-specific notes

### A. `geo.tbrridge.brb.single_cell.delta_mu.diagnostic_interval.restricted_review`

**Plausible:** Adjacent to TBRRidge pilot; shares estimator-family point structure; BRB resampling diagnostic has catalog entry (`geo.tbrridge.brb.single_cell.delta_mu.resampling_diagnostic.research_or_restricted`).

**Risky:** BRB inference semantics differ from KFold; `METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001` marks TBRRidge × BRB as `SAVE_FOR_LATER` with **high** validation cost (dependence + inverted-bounds remediation). Must **not** inherit KFold review decision or evidence packet.

**Likely missing:** Dependence assumption validation; resampling diagnostic evidence; BRB-specific claim boundary; inverted-bounds remediation proof.

**First artifact if selected later:** `TBRRIDGE_BRB_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` then evidence packet contract.

**Framework now?** **Wait** — insufficient BRB-specific evidence; would re-TBRRidge the lane.

---

### B. `geo.tbrridge.placebo.single_cell.delta_mu.diagnostic_interval.restricted_review`

**Plausible:** TBRRidge placebo calibration path exists (`geo.tbrridge.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only`, DIAGNOSTIC_ONLY); placebo diagnostics may be framework-friendly.

**Risky:** Placebo tail semantics ≠ diagnostic interval semantics; risk of conflating falsification support with interval/claim authorization. Secondary to SCM Placebo per catalog triage.

**Likely missing:** TBRRidge placebo claim-boundary audit; single_cell vs single_treated geometry alignment; tail calibration evidence bundle.

**First artifact if selected later:** `TBRRIDGE_PLACEBO_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001`.

**Framework now?** **Wait** — claim-boundary audit required before packet contract.

---

### C. `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review`

**Plausible:** High strategic value; connects to AugSynth/ASCM roadmap; JK implemented (`AugSynthCVXPY_UnitJackKnife`); `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` scoped in ROADMAP.

**Risky:** Higher method-risk and evidence burden; estimand/scale bridge open; research-only posture (RANK_1); not governed uncertainty path.

**Likely missing:** JK coverage validation; estimand alignment; AugSynth-specific claim boundary; null-control bundle for augmented path.

**First artifact if selected later:** `AUGSYNTH_JK_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` or scoped coverage audit completion.

**Framework now?** **Secondary candidate** — apply generalized framework after SCM null-monitor proves cross-estimator pattern; roadmap priority high but burden exceeds SCM for second application.

---

### D. `geo.scm.jackknife.single_cell.delta_mu.null_monitor` ✅ **Primary recommendation**

**Plausible:** Safest diagnostic/null-monitor lane; `GOVERNED` + `RESTRICTED_REVIEW` (RANK_3); sole nominal-calibration-eligible null-monitor config per catalog; `SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001` already listed as parallel Lane A alternative in ROADMAP.

**Risky:** Lower production/readout lift value than full diagnostic-interval restricted-review; multi-treated geometry defaults differ from single_cell framing; promotion evidence not yet assembled into packet form.

**Likely missing:** SCM JK promotion evidence audit completion; claim-boundary report for null-monitor surface; metric/estimand alignment audit for JK delete-one path.

**First artifact:** `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001`.

**Framework now?** **Yes** — best second application: proves framework is not TBRRidge-specific; lowest governance/claim risk.

---

### E. `geo.did.bootstrap.single_cell.delta_mu.diagnostic_interval.restricted_review`

**Plausible:** Broadly useful estimator; panel delta estimand characterized; DID point path has RESTRICTED_REVIEW tier.

**Risky:** Bootstrap runtime deferred; RANK_0 blocked; high parallel-trends and bootstrap calibration burden; `METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001` marks DID × Bootstrap validation cost **high**.

**Likely missing:** Bootstrap executor evidence; coverage calibration; DID claim boundary for bootstrap intervals; remediated bootstrap inference runtime.

**First artifact if selected later:** `DID_BOOTSTRAP_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` after bootstrap remediation.

**Framework now?** **Defer** — evidence burden and runtime deferral block framework application.

---

## 6. Recommended next instrument

### Primary recommendation

**`geo.scm.jackknife.single_cell.delta_mu.null_monitor`**

**Reasons:**

1. **Lowest claim/governance risk** — null-monitor semantics; no interval/significance claim surface
2. **Clean second framework application** — different estimator family from TBRRidge; proves generalization
3. **Catalog alignment** — GOVERNED / RESTRICTED_REVIEW (RANK_3); not production promotion
4. **Roadmap support** — `SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001` parallel lane; method candidate audit historically recommended SCM JK path
5. **Avoids TBRRidge rabbit hole** — does not deepen KFold, BRB, or placebo variants

### Secondary candidate

**`geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review`**

Apply generalized framework **after** SCM null-monitor packet contract demonstrates cross-estimator reuse. High strategic value; higher method and evidence burden.

### Deferred candidates

| Instrument | Defer reason |
|------------|--------------|
| `geo.tbrridge.brb.single_cell...` | BRB dependence + inverted-bounds; SAVE_FOR_LATER |
| `geo.tbrridge.placebo.single_cell...` | Claim-boundary undefined for placebo surface |
| `geo.did.bootstrap.single_cell...` | Bootstrap runtime deferred; highest missing-evidence burden |

---

## 7. Recommended next artifact

**`SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001`**

**Scope:**

- Exact instrument: `geo.scm.jackknife.single_cell.delta_mu.null_monitor`
- Evidence packet **contract only** (reuse generalized framework pattern from TBRRidge pilot)
- No runtime
- No promotion
- No catalog unblock
- No claim authorization

**May consume:** `SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001` (when complete) as evidence source — does not substitute for packet contract.

---

## 8. Blockers and unknowns

| Blocker | Affected candidates |
|---------|---------------------|
| Promotion evidence not yet assembled into packet form | All five |
| Method-specific claim-boundary audit missing | TBRRidge placebo, AugSynth JK, DID bootstrap |
| Catalog identity string reconciliation (`null_monitor` vs `single_cell`) | SCM JK primary |
| BRB dependence / inverted-bounds remediation incomplete | TBRRidge BRB |
| Bootstrap inference runtime deferred | DID bootstrap |
| Framework generic runtime not implemented | All — contracts reuse pilot pattern |
| `SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001` not complete | SCM JK — may precede or parallel packet contract |

**Framework gaps discovered:** Generic runtime contract (`METHOD_PROMOTION_REVIEW_FRAMEWORK_RUNTIME_CONTRACT_001`) still future; second instrument will reuse TBRRidge-shaped contract/runtime pattern until generic layer exists.

---

## 9. Non-goals

- No runtime implemented
- No method or instrument promoted
- No catalog unblock
- No production compatibility authorization
- No claim authorization change
- No statistical/CI/p-value/significance claim authorization
- No causal/business lift or ROI/ROAS claim authorization
- No decision recommendation authorization
- No estimator/inference implementation
- No new validation experiments
- No Lane B runtime changes
- No MIP decisioning
- No TrustReport bypass
- No modification of TBRRidge pilot runtimes

---

## 10. Validation results

- Audit doc: `docs/track_d/METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001.md`
- Summary JSON: `docs/track_d/archives/METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001_summary.json`
- Governance tests: `tests/governance/test_method_promotion_next_instrument_selection_audit_001.py`

Capability flags (all true): `next_instrument_selection_audit_completed`, `selection_criteria_defined`, `candidate_set_evaluated`, `candidate_scores_recorded`, `primary_recommendation_selected`, `framework_application_not_tbr_specific`.

Forbidden flags (all false): runtime implemented, promotion, catalog unblock, claim authorization changes, statistical claims, estimator/inference implementation, Lane B changes, MIP decisioning, TrustReport bypass.
