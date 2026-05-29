# KFold governance reconciliation 001

**Reconciliation ID:** KFOLD-GOV-RECON-001  
**Status:** governance addendum (supersedes no prior decision; amends interpretive reading only)  
**Last updated:** 2026-05-20  
**Package version:** 0.2.1  
**Trigger commit:** `391c64c` — *Fix KFold multi-treated geometry and archive validation*

**Related:** [`PHASE12_INV007_KFOLD_GEOMETRY_001.md`](PHASE12_INV007_KFOLD_GEOMETRY_001.md) · [`PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md`](PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md) · [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) · [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) · [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md)

**Scope of this document:** Reconcile governance language after the INV-007 geometry **correctness fix**. This addendum **does not** change eligibility, maturity labels, release gates, or estimator status in code or registry.

---

## 1. Executive summary

Commit `391c64c` fixes the localized TBRRidge KFold broadcasting defect identified in INV-007. Post-fix validation ([`PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md`](PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md)) shows **0% failure rate** on default recovery geometry for `n_treated` ∈ {1, 2, 4, default} at **n=100 × seeds 0–2**.

**What changed:** Execution geometry — KFold **runs** on multi-treated panels where it previously hard-failed.

**What did not change:** Governed trust boundary. KFold remains **excluded from nominal calibration**, **research-only / restrict** in Phase 13 terms, and **not calibration-ready**. Positive-scenario coverage and power remain **0.0** across all treated counts.

**Headline reconciliation:** Replace the phrase **“multi-treated unsupported”** (meaning hard execution failure) with **“multi-treated runnable; OC and eligibility not validated”**. The persisted skip reason `kfold_multi_treated_unsupported_run001` remains a **historical eligibility record** until a separate governance/registry PR explicitly revises it — this reconciliation doc does **not** trigger that change.

---

## 2. Evidence timeline

| Stage | Artifact | Commit / tier | Multi-treated execution | Nominal calibration |
|-------|----------|---------------|-------------------------|---------------------|
| Run 001 | [`CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md) | pre-fix | 100% `ValueError` | Excluded |
| INV-007 pre-fix | [`PHASE12_INV007_KFOLD_GEOMETRY_001.md`](PHASE12_INV007_KFOLD_GEOMETRY_001.md) | n=30 | 100% `ValueError` (n≥2) | Not demonstrated |
| Phase 13 decision | [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) | at `8782870` era | **Unsupported** (geometry) | Excluded |
| INV-007 post-fix | [`PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md`](PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md) | `391c64c`, n=100 | **0% failure** | Still not demonstrated |

**Interpretation rule:** Pre-fix archives remain **valid historical evidence** for the defect and for why eligibility was tightened. They are **superseded for execution-geometry claims** only after `391c64c`.

---

## 3. Question 1 — Which Phase 13 statements are no longer technically correct?

The following statements in [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) were **correct at Phase 13 closure** but are **no longer technically accurate** as descriptions of **current code behavior** after `391c64c`:

| Location | Statement (paraphrased) | Why superseded |
|----------|-------------------------|----------------|
| §1 Major conclusions (item 3) | “TBRRidge Kfold — **multi-treated unsupported** on default recovery geometry” | Multi-treated panels **execute**; 0% failure in post-fix n=100 archive |
| §1 Evidence table (INV-007 row) | “Single-treated viable; **multi-treated 100% failure**” | Pre-fix finding; multi-treated no longer 100% failure |
| §5 Assessment — Geometry | “n_treated≥2 → **100% ValueError**” | Correctness defect fixed in `debias()` via aggregate residuals |
| §5 Assessment — Multi-treated | “Default recovery DGP (~4 treated) **unsupported**” | **Unsupported for calibration/trust**, not for execution — wording conflates geometry failure with governance restriction |
| §5 Rationale | “Multi-treated path is **not a supported inference geometry** without inference-layer redesign (DEF-001)” | Redesign **implemented** for the known broadcasting path; “supported” must be redefined as OC/eligibility, not runnability |
| §5 Rationale | “Skip reason `kfold_multi_treated_unsupported_run001` **remains appropriate**” | **Partially stale** as a *literal* description of behavior; still **valid as persisted exclusion record** until governance/registry update |
| §5 Rationale | “Any future contract must **explicitly restrict to single-treated scenarios**” | Single-treated-only is no longer **required for execution**; may still be required for **conservative claims** |
| §6 Re-entry — Kfold | “**Geometry fix** or single-treated contract + n≥100 OC” | Geometry fix **done**; remaining bar is OC + governance decision |
| §7 Trust — CalibrationSignal | “Kfold: **unsupported on default DGP**” | Ambiguous — should read **not calibration-trusted**, not **non-runnable** |
| §7 Trust boundary | “Do not enable Kfold on multi-treated panels **without accepting hard failure risk**” | Hard failure risk from broadcast bug **removed**; residual risks are **statistical / OC**, not `ValueError` |
| §10 Final recommendations | “multi-treated **unsupported**” (TBRRidge_Kfold row) | Replace with runnable-but-unvalidated framing |
| Appendix INV-007 disposition | “**Deferred** (geometry contract)” | Geometry contract for the known bug is **implemented**; deferral shifts to OC/eligibility |

**Statements that remain correct (Phase 13 still governs):**

- `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS = {"SCM_UnitJackKnife"}` — unchanged  
- TBRRidge_Kfold **Restrict** / **Defer re-entry** / **research-only** governed posture  
- **Not calibration-ready** even on single-treated positive (coverage 0 / power 0 at n=100 post-fix)  
- No maturity promotion, no `production_safe`, no release-gate expansion  
- Positive OC insufficient (parallel to DEF-002 / BRB pattern)  
- Single-treated null monitoring behavior (FPR = 0, coverage = 1 at n=100 post-fix for n=1)

---

## 4. Question 2 — Which findings remain valid?

### Still valid from pre-fix INV-007 ([`PHASE12_INV007_KFOLD_GEOMETRY_001.md`](PHASE12_INV007_KFOLD_GEOMETRY_001.md))

| Finding | Status after fix |
|---------|------------------|
| Root-cause diagnosis: `(n_pre, n_treated)` vs `(n_pre,)` broadcast in legacy `debias()` | **Valid historical record**; mechanism confirmed and fixed |
| Single-treated (n=1) runs complete with aligned intervals | **Still valid** |
| Single-treated positive: coverage 0, power 0 at characterization scale | **Still valid** (confirmed at n=100 post-fix) |
| Sharp treated-count threshold (0% vs 100% failure) **pre-fix** | **Valid as historical evidence**; not a statement about current code |
| Nominal calibration readiness **not demonstrated** | **Still valid** |
| Eligibility exclusion recommendation on default DGP | **Still valid for eligibility** (governance choice unchanged) |
| Fold construction / recovery extraction ruled out as primary cause | **Still valid** |

### Still valid from Phase 13 ([`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md))

| Finding | Status after fix |
|---------|------------------|
| Phase 12 closed; TBRRidge investigation program bounded | **Valid** |
| SCM retain; BRB restrict; Kfold restrict | **Valid** (restrict = narrow claims, not “cannot run”) |
| Eligibility registry unchanged | **Valid** |
| Full promotion policy chain required before re-entry | **Valid** |
| DEF-002 positive OC gap for BRB | **Valid** (analogous KFold positive OC gap remains) |

### New findings from post-fix archive ([`PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md`](PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md))

| Finding | Implication |
|---------|-------------|
| 0% failure, 100% interval alignment, 100% bound ordering (when aligned) for n=1,2,4,default | Geometry **correctness** restored |
| Null multi-treated: FPR = 0, coverage = 1 at n=100 | Null OC **promising** on default DGP — **not** eligibility-enabling without governance |
| Null multi-treated: `recovery_success_rate = 0` for n≥2 | Point-recovery scoring still tight; **not** a geometry defect |
| Positive all cells: coverage = 0, power = 0 | **Primary remaining OC gap** (same class as pre-fix single-treated) |
| Pooled-counterfactual debias semantics | Documented limitation; interacts with DEF-009 heterogeneity |

---

## 5. Question 3 — What should replace “multi-treated unsupported”?

Use **precision by layer**. One phrase should not conflate execution, statistics, and eligibility.

### Recommended replacement taxonomy

| Layer | Old label (ambiguous) | New label (post-391c64c) |
|-------|----------------------|---------------------------|
| **Execution / correctness** | multi-treated unsupported | **multi-treated geometry runnable** (broadcast defect fixed) |
| **Statistical / OC trust** | unsupported | **OC-unvalidated for nominal calibration** — positive under-coverage; multi-treated recovery_success deficits |
| **Eligibility / registry** | unsupported (skip reason) | **excluded from nominal calibration** — skip reason **unchanged** pending governance PR |
| **Governed usage (Phase 13)** | research-only on default DGP | **restrict** — expert-review / research characterization only; **not** null-monitor certified for lift |

### Canonical short form

> **TBRRidge_Kfold: multi-treated runnable; not calibration-trusted; eligibility unchanged.**

### Phrases to retire (when describing *current* behavior)

- “multi-treated unsupported” *(when meaning hard failure)*  
- “100% ValueError on n_treated≥2” *(as present tense)*  
- “hard failure risk on multi-treated panels” *(for the broadcast bug)*  

### Phrases to keep

- “not calibration-ready”  
- “excluded from `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`”  
- “restrict / defer re-entry”  
- “runnable ≠ trusted”  

### Skip reason note

`kfold_multi_treated_unsupported_run001` is now a **misleading literal descriptor** of runtime behavior but remains the **authoritative exclusion token** in registry until an explicit governance/registry amendment renames or supersedes it with a new skip reason citing this reconciliation and post-fix OC.

---

## 6. Question 4 — What evidence gap remains?

Geometry fix closes the **correctness** gap from INV-007. It does **not** close the **trust / eligibility** gap.

### Remaining evidence gaps (ordered by governance salience)

| Gap | Detail | Blocks eligibility? |
|-----|--------|---------------------|
| **Positive-scenario OC** | coverage = 0, power = 0 at n=100 for all treated counts (null pass ≠ full calibration) | **Yes** — same class as DEF-002 |
| **Governance decision** | No Phase 13+ memo re-evaluating KFold exclusion after fix archive | **Yes** — registry change requires policy chain |
| **Skip reason hygiene** | Persisted token describes pre-fix failure mode | **Procedural** — does not block investigation runs |
| **Multi-treated recovery_success** | Null n≥2: recovery_success_rate = 0 despite 0% failures | **Partial** — point scoring / aggregation semantics (DEF-009), not geometry |
| **Heterogeneous multi-treated** | Post-fix matrix uses homogeneous default DGP only | **Yes** for broad multi-treated claims |
| **Non-recovery scenarios** | Fix validated on `recovery_null_effect` / `recovery_positive_effect` only | **Yes** for general promotion |
| **Pooled debias semantics** | Aggregate-residual bias under per-unit ATT paths; heterogeneity interaction | **Yes** for strong multi-treated trust claims |
| **Cross-mode comparison** | KFold vs BRB vs SCM positive OC not reconciled for re-entry ranking | **Advisory** |
| **Production calibration run** | No new `CALIBRATION_RUN_003` style batch with KFold eligible configs | **Yes** — KFold still excluded |

### What the fix **did** satisfy (from Phase 13 §6 re-entry list)

| Former requirement | Status |
|--------------------|--------|
| “0% multi-treated failure on claimed scenarios” (geometry) | **Met** on default recovery battery at n=100 |
| “n≥100 OC on declared scenarios” (partial) | **Met** for archived matrix — **but** positive OC fails thresholds |
| “acceptable null FPR/coverage” | **Met** on null cells at n=100 |
| “documented positive OC” | **Met as negative result** — power/coverage fail |

**Conclusion:** Re-entry remains blocked by **positive OC failure + explicit governance decision**, not by execution geometry.

---

## 7. Question 5 — Should DEF-001 be revised?

**Yes — revise disposition and wording; do not delete the entry.**

DEF-001 should follow the same pattern as the registry’s **partial fix** treatment for BRB bounds (DEF-002): geometry correctness **fixed**; **operating-characteristic and eligibility work remains deferred**.

### Recommended DEF-001 revision (for a future registry PR — not applied in this document)

| Field | Current (DEF-001) | Recommended |
|-------|-------------------|-------------|
| **Title** | Multi-treated KFold support | **Post-fix KFold operating characteristics (multi-treated)** |
| **Status** | Deferred | **Partial fix (geometry) · Deferred (OC / eligibility)** |
| **Why deferred** | 100% ValueError; redesign required | Geometry defect **fixed** (`391c64c`); deferral now because **positive OC fails**, multi-treated **recovery_success** deficits, pooled-semantics limits, and **eligibility unchanged by policy** |
| **Source artifact(s)** | INV-007 geometry only | Add [`PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md`](PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md) · [`KFOLD_GOVERNANCE_RECONCILIATION_001.md`](KFOLD_GOVERNANCE_RECONCILIATION_001.md) |
| **Future work** | “Implement multi-treated path geometry **or** single-treated-only contract” | **Characterize post-fix OC** across treated counts and scenarios; optional single-treated-only **claim boundary**; governance decision on skip reason and eligibility; **do not** conflate runnable with supported for calibration |
| **Revisit trigger** | Need for multi-treated inference | **Eligibility reconsideration**; positive OC pass or governed monitor-only role; TrustReport KFold signal definition |
| **Resolved appendix row** | “INV-007 KFold geometry — failure surface archived” | Split: **Fixed** (broadcast geometry, `391c64c`) · **Deferred** (OC/eligibility — this DEF-001) |

### Should “support multi-treated KFold” remain the framing?

**No.** “Support” implied execution geometry that was broken. Post-fix framing should be:

1. **Fixed:** multi-treated execution geometry (correctness).  
2. **Deferred:** whether KFold **should** be trusted or eligible for multi-treated nominal calibration on default recovery DGP — requires positive OC, aggregation semantics alignment (DEF-009), and governance decision.

Single-treated-only contract remains a **valid conservative claim boundary** but is no longer the **only** way to avoid hard failures.

---

## 8. Cross-artifact reconciliation map

| Artifact | Action recommended | Auto-updated by this doc? |
|----------|-------------------|---------------------------|
| [`PHASE12_INV007_KFOLD_GEOMETRY_001.md`](PHASE12_INV007_KFOLD_GEOMETRY_001.md) | Add header **“Superseded for execution claims post-391c64c”**; retain as historical | No — optional editorial PR |
| [`PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md`](PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md) | Primary **current** geometry + OC evidence | Already current |
| [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) | Add footnote or § addendum pointer to this reconciliation; **do not rewrite** closed decision text | No — historical record |
| [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) | Revise DEF-001 per §7; update partial-fix table | Future registry PR |
| [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) | Update INV-007 resolution line: “geometry **fixed**; OC/eligibility deferred (DEF-001)” | Future editorial PR |
| `nominal_calibration.py` / skip reason | Unchanged until governance PR | **No change** (this task) |

---

## 9. Eligibility, maturity, and release gates (unchanged)

This reconciliation **explicitly preserves**:

| Control | Value |
|---------|--------|
| **`NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`** | `{"SCM_UnitJackKnife"}` |
| **TBRRidge_Kfold registry skip** | `kfold_multi_treated_unsupported_run001` |
| **Maturity labels** | Unchanged |
| **Release gates** | Unchanged |
| **Estimator status in validation docs** | Unchanged |

**Principle (unchanged):** Fixing KFold makes it **runnable**. It does **not** make it **trusted** or **eligible**.

---

## 10. Non-claims

This reconciliation **does not**:

- Re-add `TBRRidge_Kfold` to nominal calibration eligibility  
- Promote KFold maturity or declare `production_safe`  
- Invalidate Phase 13 as a historical governance record  
- Require code changes  
- Rename skip reasons or registry tokens  
- Certify multi-treated KFold intervals as unbiased or well-calibrated  
- Assert that null OC pass on multi-treated cells implies re-entry  

This reconciliation **does**:

- Supersede **present-tense execution-failure** language after `391c64c`  
- Prescribe vocabulary for docs, DEF-001, and future governance reviews  
- Separate **correctness**, **OC trust**, and **eligibility** layers  
- Document remaining evidence gaps blocking re-entry  

---

## Appendix — Side-by-side language guide

| Context | Before (pre-391c64c) | After (post-391c64c) |
|---------|----------------------|----------------------|
| User runs KFold on 4-treated panel | “Will fail with ValueError” | “Will run; intervals extract; not eligibility-backed” |
| Phase 13 §5 headline | “multi-treated unsupported” | “multi-treated runnable; restrict/defer unchanged” |
| DEF-001 title | “Multi-treated KFold support” | “Post-fix KFold OC (multi-treated)” |
| INV-007 status | Deferred (geometry) | Geometry **fixed**; OC **deferred** |
| Re-entry blocker | Geometry fix **or** OC | **OC + governance** (geometry fix satisfied) |

---

*Governance addendum KFOLD-GOV-RECON-001. Eligibility, maturity, release gates, and estimator status unchanged. Next optional step: registry PR revising DEF-001 and skip-reason metadata under full promotion policy chain.*
