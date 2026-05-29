# Phase 13 governance decision 001

**Decision ID:** PHASE13-GOV-001  
**Status:** active governance record  
**Last updated:** 2026-05-28  
**Package version:** 0.2.1  

**Related:** [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) · [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) · [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) · [`ROADMAP_V4.md`](ROADMAP_V4.md)

This document **formally closes Phase 12** and records governed platform decisions from archived evidence. **No code, registry, maturity, threshold, or eligibility changes** were made in this decision.

---

## 1. Executive verdict

**Phase 12 is complete.** The TBRRidge inference investigation program produced archived operating-characteristic, geometry, aggregation-semantics, and calibration-governance evidence sufficient for a formal governance decision.

### Evidence gathered

| Track | Artifact | Outcome |
|-------|----------|---------|
| INV-017 | [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) | Archive lifecycle, eligibility evolution rules, trust-signal inputs |
| INV-008 / Run 002 | [`CALIBRATION_RUN_002.md`](CALIBRATION_RUN_002.md) | BRB bound-ordering fixed; null OC passes; positive OC fails |
| INV-007 | [`PHASE12_INV007_KFOLD_GEOMETRY_001.md`](PHASE12_INV007_KFOLD_GEOMETRY_001.md) | Single-treated viable; multi-treated 100% failure |
| INV-003 | [`PHASE12_INV003_AGGREGATION_SEMANTICS_001.md`](PHASE12_INV003_AGGREGATION_SEMANTICS_001.md) | A ≈ B on default DGP; heterogeneity drift; absolute/relative incompatibility |
| Phase 11 (input) | [`SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md) | SCM null monitor; zero power on positive |
| Run 001 / failure analysis | [`CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md) · [`CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md) | Baseline OC; eligibility tightening rationale |

### Major conclusions

1. **Nominal calibration eligibility remains `SCM_UnitJackKnife` only** — unchanged by this decision.
2. **TBRRidge BRB** — bound defect **fixed**; null monitoring **viable**; **not** nominally calibrated for lift detection (positive under-coverage).
3. **TBRRidge Kfold** — **multi-treated unsupported** on default recovery geometry; **single-treated-only** partial viability; **not** calibration-ready.
4. **Aggregation semantics** — operational stack **coherent** on homogeneous relative default DGP; **governance evolution deferred** (DEF-009) before Track B contracts.
5. **No estimator promotion, no `production_safe`, no maturity increase** — expert-review discipline preserved.

---

## 2. Evidence reviewed

| Archive | Role in decision |
|---------|------------------|
| [`CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md) | Production-tier baseline (n=100); SCM null pass; BRB/Kfold failures |
| [`CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md) | Root-cause mechanisms; eligibility removal rationale |
| [`CALIBRATION_RUN_002.md`](CALIBRATION_RUN_002.md) | Post-fix BRB OC at n=100 |
| [`SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md) | Phase 11 width/power/geometry matrix |
| [`PHASE12_INV007_KFOLD_GEOMETRY_001.md`](PHASE12_INV007_KFOLD_GEOMETRY_001.md) | Treated-count failure surface |
| [`PHASE12_INV003_AGGREGATION_SEMANTICS_001.md`](PHASE12_INV003_AGGREGATION_SEMANTICS_001.md) | Estimand A vs B characterization |
| [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) | Governance process for archives and eligibility |
| [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) | Per-estimator validation paths; promotion chain |
| [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md) | Maturity matrix; current eligibility row |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Phase 12 exit criteria; Track A/B sequencing |
| [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) | Investigation ledger (updated post-decision) |
| [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) | Dispositions for all characterized limitations |

---

## 3. SCM_UnitJackKnife decision

### Assessment

| Dimension | Finding |
|-----------|---------|
| **Null behavior** | Run 001 + Phase 11: coverage = 1.0, FPR = 0.0 across all null cells — **persistent over-conservatism**, not anti-calibration |
| **Positive behavior** | Power = 0.0 on default recovery DGP and across 144-cell matrix — accurate points, intervals never exclude zero |
| **Interval conservatism** | Width/effect ratio ≈ 8–23× depending on panel geometry; strongest driver is donor-tier geometry, not treated count alone |
| **Current role** | Sole member of `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`; best-evidenced **null-monitor** path on relative ATT |

### Governed status

**expert-review** — with **null-monitor-only** nominal calibration boundary

### Rationale

- Point recovery is excellent (recovery success = 1.0); no implementation defect analogous to BRB inversion.
- Null OC is archived at n≥100 and characterized extensively in Phase 11.
- Positive-scenario power is **zero by construction** of conservative jackknife intervals — not a tuning artifact.
- Suitable for **conservative null screening**, not lift detection or positive-scenario nominal calibration claims.
- Maturity catalog status (`expert_review`) remains appropriate; this decision **does not** expand usage beyond characterized boundary.

**Disposition:** **Accepted** limitation for positive detection → [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) **DEF-013**

---

## 4. TBRRidge_BlockResidualBootstrap decision

### Assessment

| Dimension | Finding |
|-----------|---------|
| **Run 001** | FPR = 1.0, coverage = 0.0 on null — inverted `y_lower`/`y_upper` at outcome level |
| **Bound fix** | Guard + ordering correction applied; Run 002 confirms 0 inverted bounds across 600 replications |
| **Run 002 null** | Coverage = 1.0, FPR = 0.0, failure rate = 0.0 — **anti-calibration eliminated** |
| **Run 002 positive** | Coverage = 0.0, power = 0.0 — accurate points (|bias| ≈ 0.008 vs 0.10); intervals too narrow to contain truth (width ≈ 0.043) |
| **Interval behavior** | Aligned `relative_att_post`; functional; stable across seeds |
| **Coverage / power split** | Null pass ≠ full calibration — positive OC **systematically under-covering** |

### Governed status

**expert-review** — **excluded from nominal calibration** until positive OC evidence closes DEF-002

### Rationale

- Bound-ordering **correctness defect is fixed** (disposition: partial fix → DEF-002 remains for positive OC).
- Null monitoring behavior is now **sane** — unlike Run 001.
- Positive-scenario nominal calibration **fails** frozen thresholds; null pass alone does **not** support lift-detection claims.
- Skip reason `brb_bounds_inverted_run001` remains valid as **historical record**; governance may add clarifying skip metadata in a future registry doc PR — **not in this decision**.
- **Do not re-add** to `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` without full promotion policy chain including positive OC.

**Disposition:** **Deferred** positive OC / re-eligibility → **DEF-002**

---

## 5. TBRRidge_Kfold decision

### Assessment

| Dimension | Finding |
|-----------|---------|
| **Geometry characterization** | Sharp threshold: n_treated=1 → 0% failure; n_treated≥2 → 100% `ValueError` `(n_pre, n_treated)` vs `(n_pre,)` |
| **Single-treated behavior** | Runs complete; intervals aligned; null FPR = 0 at characterization tier (n=30) |
| **Multi-treated behavior** | Default recovery DGP (~4 treated) **unsupported** — confirms Run 001 |
| **Calibration readiness** | Not demonstrated even on single-treated positive (coverage 0 / power 0 at n=30); no n≥100 production archive |

### Governed status

**research-only** for default recovery and multi-treated panels · **characterization only** for single-treated exploratory use

### Rationale

- Multi-treated path is **not a supported inference geometry** without inference-layer redesign (DEF-001).
- Single-treated execution is **viable but not calibration-ready** — positive OC failure mirrors BRB pattern at characterization scale.
- Skip reason `kfold_multi_treated_unsupported_run001` **remains appropriate**.
- Any future contract must **explicitly** restrict to single-treated scenarios and require n≥100 OC before eligibility reconsideration.
- Does not warrant nominal calibration on default multi-treated recovery DGP.

**Disposition:** **Deferred** multi-treated support → **DEF-001** · **Deferred** calibration path → **DEF-002** pattern (positive OC)

---

## 6. Eligibility implications

### Registry status

| Field | Decision |
|-------|----------|
| **`NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`** | **Unchanged:** `{"SCM_UnitJackKnife"}` |
| **TBRRidge BRB skip** | **Remain excluded** — positive OC insufficient (DEF-002) |
| **TBRRidge Kfold skip** | **Remain excluded** — multi-treated unsupported + no production OC (DEF-001) |
| **Thresholds** | **Unchanged** — no tuning to pass calibration |

### Future evidence required for re-entry

Full [`ROADMAP_V4.md`](ROADMAP_V4.md) promotion policy chain **in order**:

1. Estimand definition (explicit geometry contract for Kfold if applicable)  
2. Recovery evidence on declared scenario battery  
3. **n≥100** calibration archive per claimed geometry class  
4. Failure analysis when calibration fails  
5. OC characterization (width, power, geometry sensitivity)  
6. **Governance decision** citing archives — registry PR last  

**BRB re-entry additionally requires:** positive-scenario coverage/power characterization explaining or resolving under-coverage (DEF-002).

**Kfold re-entry additionally requires:** 0% multi-treated failure on claimed scenarios **or** permanent single-treated-only skip reason with n≥100 single-treated OC.

### Re-entry criteria summary

| Config | Minimum bar |
|--------|-------------|
| **SCM_UnitJackKnife** | Already eligible — **null monitoring only**; positive power claims require inference redesign (DEF-013) |
| **TBRRidge_BRB** | Positive OC pass at n≥100 + failure analysis if needed |
| **TBRRidge_Kfold** | Geometry fix or single-treated contract + n≥100 OC on declared scenarios |

---

## 7. Trust implications

Findings map to future Track B trust artifacts (conceptual — not implemented in v0.2.1):

| Artifact | Phase 12–13 implication |
|----------|-------------------------|
| **`ExperimentEvidence`** | Must store declared estimand, scored estimand (B), interval estimand, aggregation mode, and geometry class (single- vs multi-treated) |
| **`CalibrationSignal`** | SCM: null-monitor signal only; BRB: null-viable / positive-not-calibrated; Kfold: unsupported on default DGP |
| **`TrustReport`** | `supported_*` requires matching estimand + OC scope; `incompatible_estimand` for absolute vs relative (DEF-018); `inconclusive` for heterogeneous multi-treated without contract (DEF-009) |
| **Release gates** | **Unchanged** — no automated blocking; advisory culture preserved (DEF-008) |

**Trust boundary (immediate):** Do not interpret SCM null calibration pass as package-wide nominal calibration. Do not interpret BRB null pass as lift-detection certification. Do not enable Kfold on multi-treated panels without accepting hard failure risk.

---

## 8. Roadmap implications

| Question | Answer |
|----------|--------|
| **Is Phase 12 complete?** | **Yes** — all four tracks archived (INV-003, INV-007, INV-008, INV-017); this decision closes Phase 12 |
| **Can Track A close?** | **Partially** — TBRRidge investigation program **closed**; **Phases 14–15 remain** (DID OC, AugSynth/CVXPY validation per ROADMAP_V4) |
| **What remains before Track B?** | Phase 14 DID OC · Phase 15 CVXPY wiring · deferred registry items DEF-008–DEF-012 · re-audit → ROADMAP_V5 |

**Track B may begin planning** on governed foundation: estimand semantics characterized (INV-003), calibration archive conventions established (INV-017), TBRRidge configs bounded by evidence. **Track B implementation** should not outrun Phase 14–15 Track A completion unless explicitly re-scoped in a future roadmap amendment.

**Sequencing unchanged:** A → B → C per [`ROADMAP_V4.md`](ROADMAP_V4.md).

---

## 9. Non-claims

This governance decision **does not**:

- Promote any estimator maturity label  
- Assign **`production_safe`** to any config  
- Re-add TBRRidge modes to `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`  
- Change thresholds, recovery scoring, inference code, or estimator code  
- Expand release gates or automated blocking  
- Redefine official estimands or aggregation scoring  
- Claim package-wide nominal calibration beyond SCM null-monitor scope  

This decision **does**:

- Formally close Phase 12  
- Record governed status per config  
- Preserve eligibility registry unchanged  
- Route all open limitations to [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md)  
- Enable Track B planning on evidenced constraints  

---

## 10. Final recommendations

### Configuration actions

| Config | Action | Governed status | Eligibility | Notes |
|--------|--------|-----------------|-------------|-------|
| **SCM_UnitJackKnife** | **Retain** | expert-review | **Retain** (null monitor) | Null OC only; not lift detector |
| **TBRRidge_BlockResidualBootstrap** | **Restrict** | expert-review | **Defer** re-entry | Bound fix accepted; positive OC required |
| **TBRRidge_Kfold** | **Restrict** | research-only / characterization only | **Defer** re-entry | Single-treated exploratory; multi-treated unsupported |

### Investigation dispositions (Phase 12)

| ID | Disposition | Registry |
|----|-------------|----------|
| **INV-003** | **Escalated → Deferred** (governance evolution) | DEF-009, DEF-018 |
| **INV-007** | **Deferred** (geometry contract) | DEF-001 |
| **INV-008** | **Deferred** (positive OC) | DEF-002 |
| **INV-017** | **Deferred** (TrustReport / scaling) | DEF-008 |

### Phase 13 classification legend

| Term | Meaning |
|------|---------|
| **Retain** | Keep current governed role with documented boundary |
| **Restrict** | Narrow allowed claims or scenario geometry |
| **Defer** | No registry or maturity change; future evidence required |
| **Retire** | Remove from supported paths — **none** recommended at Phase 13 |
| **Future evidence required** | Full promotion policy chain before any expansion |

---

## Appendix — Phase 12 closure checklist

| Criterion | Status |
|-----------|--------|
| Run 002 archived | ✅ |
| KFold geometry archived | ✅ |
| Aggregation semantics archived | ✅ |
| Calibration governance framework archived | ✅ |
| Governance decision recorded | ✅ (this document) |
| Deferred work dispositions assigned | ✅ [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) |
| Eligibility unchanged unless policy chain passes | ✅ |
| OPEN_INVESTIGATIONS updated | ✅ |

---

*Governance record PHASE13-GOV-001. Phase 12 closed. Registry and code unchanged.*
