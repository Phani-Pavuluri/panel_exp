# MIP Periodic Architecture and Robustness Audit

**Program ID:** MIP-PERIODIC-AUDIT  
**Template version:** 1.0.0  
**Status:** active  

**Binding:** [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) · [`ROADMAP_V4.md`](ROADMAP_V4.md) · [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md)

**Purpose:** Periodically ask whether the project is still building a **best-in-class governed causal Marketing Intelligence Platform**, or only accumulating partial components.

| Layer | Question |
|-------|----------|
| Roadmap | What to build |
| Alignment gate | Whether a task is allowed |
| **This audit** | Whether we are building the *right thing*, correctly |

**Cadence — run after:**

- B5d contract validator complete  
- M2 dual-write complete  
- Track D D1 / D2 / D3 packages  
- Before MMM intake promotion  
- Before planning / optimizer work  
- Before LLM interface work  
- Before any production-promotion or eligibility change  

**Non-goals:**

- Not a replacement for pytest or B5d validator  
- Not a substitute for Track D OC evidence  
- Not permission to promote methods or change release gates  
- Not a broad rewrite exercise without ADR  

**Required outputs:** audit report (this doc filled) · gap table · recommendations · roadmap adjustments (if any) · [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) update  

---

## Audit header

| Field | Value |
|-------|--------|
| **Audit ID** | `AUDIT-NNN` |
| **Date** | |
| **Auditor** | |
| **Milestone reviewed** | e.g. B5d, M2, Track D D1 |
| **Commit / branch** | |
| **Scope** | |

---

## 1. North Star Alignment

**North star:** A governed causal marketing intelligence platform that converts experiments, lift studies, holdouts, MMM, diagnostics, and calibration evidence into **trustworthy budget, planning, and recommendation decisions**.

| # | Question | Answer |
|---|----------|--------|
| 1 | What **platform capability** did the latest work enable? | |
| 2 | Which **decision risk** did it reduce? | |
| 3 | Which **governed artifacts** did it create, validate, or consume? | |
| 4 | Did it improve **causal validity**, **trust**, **calibration**, **planning**, **recommendation quality**, **explainability**, or **governance**? | |
| 5 | What is still **missing** before this can affect production, calibration, or decisioning? | |
| 6 | Did any work drift into **component-only** development without platform linkage? | |

**Verdict:** `aligned` · `partially_aligned` · `sideways_risk` · `blocked`

**Required follow-up:**

---

## 2. Current Implementation Inventory

List what is now implemented or documented. Prevents “done” confusion when only docs, fixtures, or tests exist.

**Categories:** contracts · adapters · estimators · inference methods · design/matching methods · diagnostics · power/MDE · calibration evidence · TrustReport logic · MMM integration · planning/optimization · recommendation layer · LLM interface · governance/audit tooling

| Item | Type | Implemented / doc-only / fixture-only / test-only / research-only | Production-eligible? | Track | Linked docs/tests | Current status | Known limitations |
|------|------|-------------------------------------------------------------------|----------------------|-------|-------------------|----------------|-------------------|
| | | | yes/no | | | | |

---

## 3. Architecture Soundness Audit

| # | Question | Finding |
|---|----------|---------|
| 1 | Responsibilities cleanly separated? (Spec declares · Evidence facts · DiagnosticSummary modifiers · CalibrationSignal history · TrustReport interprets · MMM governed intake only) | |
| 2 | Did any layer do another layer’s job? | |
| 3 | Identity explicit? (`estimand_id`, `measurement_instrument_id`, `interval_semantics`, `geometry`, `transform_ref`, `claim_type`, `intended_use`) | |
| 4 | Sidecars / dual-write non-breaking? | |
| 5 | Deprecated or restricted methods blocked from decision use? | |
| 6 | Findings in registry vs chat-only? | |

**Verdict:** `architecture_sound` · `minor_drift` · `major_drift` · `requires_ADR`

---

## 4. Conceptual and Causal Validity Audit

| # | Question | Finding |
|---|----------|---------|
| 1 | Causal estimand clear? | |
| 2 | Population clear? | |
| 3 | Contrast clear? | |
| 4 | Time window clear? | |
| 5 | Aggregation rule clear? | |
| 6 | Scale clear (absolute / relative / cumulative / log / response delta)? | |
| 7 | Incompatible quantities blocked from comparison? | |
| 8 | Assumptions stated? | |
| 9 | Threats to identification documented? | |
| 10 | Spillover, interference, contamination, exposure-opportunity addressed? | |

**Check specifically:**

| Pairing | Status / notes |
|---------|----------------|
| Geo relative ATT vs MMM Δμ | |
| DID cumulative ATT vs relative ATT | |
| Placebo band vs confidence interval | |
| Point estimate vs interval estimate | |
| A/B ATE vs geo ATT | |
| CLS incremental conversions vs modeled response | |
| Short-term lift vs long-term holdout lift | |

**Verdict:** `causally_clear` · `causally_ambiguous` · `unsafe_comparison_risk` · `blocked`

---

## 5. Statistical Robustness Audit

| # | Question | Finding |
|---|----------|---------|
| 1 | Estimator assumptions known? | |
| 2 | Inference valid for design geometry? | |
| 3 | Operating characteristics known? | |
| 4 | FPR, power, coverage, bias, sign error, failure modes known? | |
| 5 | Intervals semantically correct? | |
| 6 | Conservative methods labeled correctly? | |
| 7 | Restricted instruments blocked from calibration / decision use? | |
| 8 | OC simulations planned or complete? | |
| 9 | Power/MDE aligned to readout method? | |
| 10 | Runtime monitoring checks defined? | |

**Required status per method** (from Track D matrix):  
`unreviewed` · `math_review_required` · `implementation_review_required` · `characterization_required` · `restricted` · `diagnostic_only` · `calibration_eligible` · `decision_eligible` · `deprecated` · `blocked`

**Verdict:** `statistically_supported` · `research_only` · `restricted` · `insufficient_OC` · `blocked`

**Binding:** [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md)

---

## 6. Literature and Cutting-Edge Grounding Audit

| # | Question | Finding |
|---|----------|---------|
| 1 | Canonical papers per method? | |
| 2 | Which assumptions satisfied? | |
| 3 | Which violated or uncertain? | |
| 4 | Implementation faithful to literature? | |
| 5 | Method used outside intended setting? | |
| 6 | Newer methods to investigate? | |
| 7 | Accepted deviations documented? | |
| 8 | Negative findings recorded? | |

**Categories to review:** SCM / generalized SCM · augmented synthetic control · TBR / matched markets · DID / SDID · BSTS · conformal · randomization inference · geo experiment design · cluster experiments · power/MDE · MMM calibration · budget optimization under uncertainty · causal decision systems · trustworthy ML / governance

**Verdict:** `literature_grounded` · `literature_gap` · `implementation_mismatch` · `needs_research_review`

**Binding:** [`TRACK_D_LITERATURE_CROSSCHECK_001.md`](TRACK_D_LITERATURE_CROSSCHECK_001.md)

---

## 7. Product and Decision Usefulness Audit

| # | Question | Finding |
|---|----------|---------|
| 1 | What business decision can this support? | |
| 2 | Budget / design / calibration / planning / recommendation? | |
| 3 | Uncertainty and trust exposed clearly? | |
| 4 | Decision-grade vs suggestive evidence distinguished? | |
| 5 | User can understand why a recommendation was made? | |
| 6 | Missing / conflicting / stale signals surfaced? | |
| 7 | Actionable without overstating certainty? | |

**Verdict:** `decision_useful` · `diagnostic_only` · `research_only` · `not_actionable_yet`

---

## 8. Governance and Safety Audit

| # | Question | Finding |
|---|----------|---------|
| 1 | Orphan findings? | |
| 2 | Deferred items tracked? | |
| 3 | Open investigations tracked? | |
| 4 | Stop conditions clear? | |
| 5 | Promotion/demotion rules followed? | |
| 6 | Production vs research lanes separated? | |
| 7 | Eligibility/maturity/release gates unchanged unless approved? | |
| 8 | Raw results prevented from direct MMM/planning feed? | |
| 9 | LLM outputs grounded in governed artifacts? | |

**Verdict:** `governed` · `minor_governance_gap` · `orphan_findings_present` · `unsafe_promotion_risk`

**Binding:** [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) · [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) · [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md)

---

## 9. Missing Dimensions / Gap Discovery

Force blind-spot discovery across:

1. Evidence identity  
2. Measurement instrument coverage  
3. Estimand coverage  
4. Design validity  
5. Matching correctness  
6. Estimator math  
7. Inference robustness  
8. Power/MDE validity  
9. Runtime monitoring  
10. CalibrationSignal registry  
11. MMM intake compatibility  
12. Response curve validation  
13. Budget optimizer robustness  
14. Recommendation explainability  
15. LLM grounding  
16. Data lineage and reproducibility  
17. Versioning and audit trails  
18. Privacy / access / security  
19. Experiment operations workflow  
20. Human review / approval workflow  

| Gap | Severity | Type | Risk | Recommended action | Owner / track | Blocked by |
|-----|----------|------|------|-------------------|---------------|------------|
| | critical/high/medium/low | | | | | |

---

## 10. Recommendations

Classify each: `production_path` · `research_lane` · `governance_fix` · `architecture_ADR` · `implementation_fix` · `literature_review` · `OC_simulation` · `deprecation_review` · `future_track`

| Field | Content |
|-------|---------|
| **Recommendation** | |
| **Why it matters** | |
| **What risk it reduces** | |
| **Required evidence** | |
| **Stop condition** | |
| **Next artifact** | |

---

## 11. Final Audit Verdict

**Overall verdict:**

- `continue_current_path`  
- `continue_with_minor_corrections`  
- `pause_for_architecture_ADR`  
- `pause_for_statistical_review`  
- `block_production_promotion`  
- `reprioritize_roadmap`  

**Summary:**

**Top 3 strengths:**

1.  
2.  
3.  

**Top 3 risks:**

1.  
2.  
3.  

**Top 3 missing pieces:**

1.  
2.  
3.  

**Next 3 recommended actions:**

1.  
2.  
3.  

---

## Registry update

After completing this audit:

1. Add a row to [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md).  
2. Link open gaps to `OPEN_INVESTIGATIONS.md` or `DEFERRED_WORK_REGISTRY.md` where appropriate.  
3. Adjust [`ROADMAP_V4.md`](ROADMAP_V4.md) only when verdict is `reprioritize_roadmap` or explicit follow-up approved.

---

*Template MIP-PERIODIC-AUDIT v1.0.0. Copy this file or duplicate sections into `docs/audits/AUDIT-NNN_<milestone>.md` for each run.*
