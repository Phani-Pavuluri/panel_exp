# Phase 15 governance decision 001

**Decision ID:** PHASE15-GOV-001  
**Status:** active governance record  
**Last updated:** 2026-05-20  
**Package version:** 0.2.1  

**Related:** [`PHASE15_PLACEBO_CHARACTERIZATION_001.md`](PHASE15_PLACEBO_CHARACTERIZATION_001.md) · [`PHASE15_PLACEBO_INVESTIGATION_PLAN.md`](PHASE15_PLACEBO_INVESTIGATION_PLAN.md) · [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) · [`KFOLD_GOVERNANCE_RECONCILIATION_001.md`](KFOLD_GOVERNANCE_RECONCILIATION_001.md) · [`INV031_INFERENCE_CONSERVATISM_PLAN.md`](INV031_INFERENCE_CONSERVATISM_PLAN.md) · [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) · [`ROADMAP_V4.md`](ROADMAP_V4.md)

This document **formally closes Phase 15** and records governed platform decisions from archived Placebo operating-characteristic evidence. **No code, registry, maturity, threshold, or eligibility changes** were made in this decision.

---

## 1. Executive verdict

**Phase 15 is complete.** Placebo inference on SCM/TBR-family paths has production-tier and characterization-tier OC archived sufficient for a formal governance decision.

### What was characterized

| Track | Artifact | Scope |
|-------|----------|-------|
| **INV-029A — SCM Placebo OC** | [`PHASE15_PLACEBO_CHARACTERIZATION_001.md`](PHASE15_PLACEBO_CHARACTERIZATION_001.md) | Null/positive, geometry, donor tier, heterogeneity; n=100 single-treated production cells |
| **INV-029B — Interval semantics** | Same archive | `placebo_band` vs recovery `relative_att_post` extraction; inversion CI metadata |
| **INV-029C — Geometry matrix** | Same archive | n_treated 1 / 2 / 4 / default; donor small / medium / large |
| **INV-029D — Cross-estimator** | Same archive | TBRRidge Placebo (single-treated); TBR Placebo (failure surface) |

### Conclusions supported by evidence

1. **SCM Placebo on single-treated panels** is **execution-reliable** with **sane null monitoring** (FPR = 0, coverage = 1) and **zero lift-detection power** (power = 0; intervals always include zero on positive).
2. **Placebo path semantics are honest** on the success path: **`path_interval_type = placebo_band`** on 100% of successful replications — **not** jackknife/bootstrap CIs.
3. **Default multi-treated recovery DGP is not supported** — 100% `NotImplementedError` (single-treated-only implementation).
4. **TBRRidge Placebo** mirrors SCM on **single-treated** geometry; **TBR Placebo** is **unsupported** (aggregated-control exclusion).
5. **Nominal calibration eligibility remains `SCM_UnitJackKnife` only** — Placebo is **not** added and **must not** be marketed as calibrated lift detection.
6. **Phase 15 closes the core geo inference characterization program** begun in Phase 11–12; **Track B implementation remains secondary** until [`TRACK_A_COMPLETION_REVIEW_001.md`](TRACK_A_COMPLETION_REVIEW_001.md) (planned next checkpoint).

**Headline governed role:** Placebo is an **expert-review null-reference / diagnostic inference mode** on **single-treated-only** geometry — **not** a lift detector, **not** interchangeable with confidence intervals, **not** default-DGP multi-geo ready.

---

## 2. Evidence reviewed

| Archive | Role in decision |
|---------|------------------|
| [`PHASE15_PLACEBO_CHARACTERIZATION_001.md`](PHASE15_PLACEBO_CHARACTERIZATION_001.md) | Primary OC matrix (22 cells); production n=100 single-treated |
| [`PHASE15_PLACEBO_INVESTIGATION_PLAN.md`](PHASE15_PLACEBO_INVESTIGATION_PLAN.md) | Investigation scope, acceptable outcomes, non-goals |
| [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) | Precedent for null-monitor vs lift-detection split; eligibility unchanged |
| [`SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md) | Cross-mode conservatism comparator (Phase 11) |
| [`PHASE14_AUGSYNTH_CHARACTERIZATION_001.md`](PHASE14_AUGSYNTH_CHARACTERIZATION_001.md) | Adjacent inference-mode OC context |
| [`INV031_INFERENCE_CONSERVATISM_PLAN.md`](INV031_INFERENCE_CONSERVATISM_PLAN.md) | Cross-mode zero-power framing; placebo distinct mechanism on positive |
| [`KFOLD_GOVERNANCE_RECONCILIATION_001.md`](KFOLD_GOVERNANCE_RECONCILIATION_001.md) | Geometry-boundary governance pattern (runnable vs trusted) |
| [`tests/test_inference_result_semantics.py`](../tests/test_inference_result_semantics.py) | `IntervalType.PLACEBO_BAND` contract |
| [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) | Promotion chain; SCM expert-review path |
| [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md) | Catalog lists Placebo on SCM; maturity unchanged |
| [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) | DEF-020, DEF-021, INV-030/031 dispositions |
| [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) | INV-029 closure; placebo vs CI ambiguity |
| **Local JSON** | `.phase15_placebo_characterization.json` (not committed) |

---

## 3. SCM Placebo decision

### Assessment

| Dimension | Finding |
|-----------|---------|
| **Null behavior** | Production single-treated (n=100 × 3 seeds): coverage = 1.0, FPR = 0.0, failure rate = 0.0 — **sane null monitor**, not anti-calibrated |
| **Positive behavior** | coverage = 1.0 (intervals bracket true effect); **power = 0.0**, significance = 0.0 — intervals **always include zero** |
| **Interval semantics** | Path: `placebo_band`; recovery extraction: aligned `relative_att_post` / `path_period_relative_mean` when run succeeds; `ci_via_inversion = true` |
| **Single-treated limitation** | **Required** for any OC-backed claims — only geometry with 0% failure in archive |
| **Donor sensitivity** | Width varies by donor tier (width/effect ~0.55×–3× on single-treated positive); power remains 0 |
| **Point recovery** | Excellent on successful cells (investigation harness; point estimand unchanged) |

### Governed status

**expert-review** — **null-reference / diagnostic inference** with **mandatory `placebo_band` export discipline**

### Rationale

- Null OC passes at production tier on declared single-treated geometry.
- Positive-scenario **coverage = 1** must **not** be read as lift-detection calibration — power = 0 because envelopes are **null-reference bands** that include zero ([`INV031_INFERENCE_CONSERVATISM_PLAN.md`](INV031_INFERENCE_CONSERVATISM_PLAN.md) H7).
- Recovery interval metrics are **meaningful when aligned** but measure **converted placebo envelopes**, not classical CIs — reviewers must see `placebo_band` labeling.
- Suitable for **expert-review null reference** and **diagnostic comparison** to point estimates — **not** automated lift certification.
- **Not** in `RecoveryRunner` nominal calibration registry today; this decision **does not** add eligibility.

**Disposition:** **Accepted** usage boundary (single-treated null reference) → **DEF-020** · multi-treated gap → **Deferred** (see §5)

---

## 4. TBRRidge Placebo decision

### Assessment

| Dimension | Finding |
|-----------|---------|
| **Viability** | **Single-treated only** — 0% failure on null/positive characterization cells (n=30 × 3 seeds) |
| **Null behavior** | FPR = 0.0, coverage = 1.0 on `tbrridge_single_null` |
| **Positive behavior** | coverage = 1.0, power = 0.0; width/effect ≈ 1.7× (narrower than SCM placebo ~2.3× but still zero power) |
| **Interval semantics** | Same `placebo_band` + inversion path as SCM on success |
| **Implementation limitations** | Multi-treated fails (`NotImplementedError`); not characterized at n=100 production tier; not registry-wired |

### Governed status

**expert-review** — **same role class as SCM Placebo**, **narrower evidence base** (characterization tier only; single-treated)

### Rationale

- Cross-family replication supports that placebo conservatism is **procedure-level**, not SCM-weight-construction-specific.
- **Do not** treat TBRRidge Placebo as stronger evidence than SCM for platform-wide claims — production archive exists for SCM only.
- **Do not** wire to nominal calibration without full promotion chain and geometry contract.

**Disposition:** **Accepted** as diagnostic adjunct on single-treated panels → cite Phase 15 archive · **Defer** registry wiring → **DEF-020** (wiring) remains optional future work

---

## 5. Multi-treated implications

### NotImplemented boundaries

| Geometry | SCM / TBRRidge Placebo | Evidence |
|----------|------------------------|----------|
| n_treated = 2, 4 | **100% failure** | `NotImplementedError`: placebo-in-space supports **exactly one treated unit** |
| Default recovery (~4 treated) | **100% failure** | Same — default DGP **not an OC surface** today |
| TBR (any) | **100% failure** | `AssertionError` / aggregated-control policy |

This is an **explicit implementation constraint**, not a silent scoring artifact. Failed cells correctly report unavailable interval metrics.

### Governance implications

| Topic | Decision |
|-------|----------|
| **Default recovery DGP claims** | **Forbidden** for Placebo until multi-treated implementation + OC archive |
| **Expert-review exports** | Must declare **`geometry_class: single_treated_only`** when Placebo is used |
| **Comparison to KFold** | Pre-fix KFold failed on multi-treated (bug, now fixed per [`KFOLD_GOVERNANCE_RECONCILIATION_001.md`](KFOLD_GOVERNANCE_RECONCILIATION_001.md)); Placebo fails by **documented design** — different disposition |
| **Eligibility** | **Unchanged** — multi-treated unsupported is **not** a registry skip reason today because Placebo was never eligible |

### Future work (deferred, not blockers)

| Item | Trigger |
|------|---------|
| Multi-treated placebo-in-space implementation | Product requirement + estimand contract (DEF-009) |
| n≥100 TBRRidge Placebo production archive | Registry wiring or promotion discussion |
| TBR pooled placebo path | Separate design decision — currently **rejected** by implementation policy |
| `RecoveryRunner` config for `SCM_Placebo` | Track B wiring PR — **not** required for Phase 15 closure |

---

## 6. Trust implications

Conceptual mapping for Track B artifacts ([`TRACK_B_ARCHITECTURE_PLAN.md`](TRACK_B_ARCHITECTURE_PLAN.md)) — **not implemented in v0.2.1**.

### ExperimentEvidence

| Field | Placebo requirement |
|-------|---------------------|
| `inference_mode` | `"Placebo"` |
| `path_interval_type` | **`placebo_band`** (required on success) |
| `interval_estimand` | `relative_att_post` when recovery extraction aligned — with **`uncertainty_semantics: placebo_null_envelope`** |
| `geometry_class` | **`single_treated_only`** for archived OC scope |
| `lift_detection_calibrated` | **`false`** |

### DiagnosticSummary

| Signal | Content |
|--------|---------|
| **Include** | Placebo p-value / band width when run succeeds; **`placebo_band` label** |
| **Exclude** | Language implying “95% CI for ATT” without qualifier |
| **Flag** | Multi-treated panel + Placebo requested → **`unsupported_geometry`** |

### CalibrationSignal

| Mode | Signal |
|------|--------|
| **Null monitor** | **`viable`** on single-treated null cells (FPR = 0 archived) |
| **Lift detection** | **`not_calibrated`** — power = 0 by design |
| **Nominal calibration registry** | **`excluded`** — unchanged from Phase 13 |
| **Positive coverage = 1** | **`diagnostic_only`** — do not emit `supported_positive` from coverage alone |

### TrustReport

| Outcome | When |
|---------|------|
| **`calibration_unavailable`** | Placebo used but geometry ∉ single-treated OC scope |
| **`incompatible_estimand`** | Reviewer treats placebo band as jackknife CI |
| **`inconclusive`** | Default for lift claims from Placebo alone |
| **`supported_*` (lift)** | **Do not emit** from Placebo OC archived today |

**Export discipline (immediate, documentation-level):** Product copy and experiment cards must **never** conflate **`placebo_band`** with **`confidence_interval`**.

---

## 7. Deferred-work implications

| ID | Phase 15 disposition | Action |
|----|------------------------|--------|
| **DEF-020** | **Accepted** (single-treated expert-review null reference) · wiring **Deferred** | Close INV-029 characterization gap; retain multi-treated + export-policy deferrals |
| **DEF-021** | **Unchanged** — parallel research | Jackknife family alternatives independent of Placebo decision |
| **INV-031** | **Investigating** — execution next | Placebo H7 (null-envelope semantics) feeds synthesis; **not** a Phase 15 blocker |
| **INV-030** | **Investigating** — plan committed | Orthogonal to Placebo |
| **DEF-013** | **Reinforced** | UnitJackKnife null-monitor-only; Placebo adds **second** null-reference mode with distinct semantics |
| **DEF-002** | **Unchanged** | BRB positive under-coverage remains separate mechanism |
| **DEF-016** | **Unchanged** | DID OC still deferred |
| **DEF-019** | **Unchanged** | AugSynth wiring deferred separately |

### Investigation dispositions (Phase 15)

| ID | Disposition | Registry |
|----|-------------|----------|
| **INV-029** | **Closed — characterized** | DEF-020 |
| **Placebo vs CI** (OPEN_INVESTIGATIONS) | **Closed — policy** | Export discipline in §6 |

### Recommended DEF-020 revision (future registry PR — not applied here)

| Field | Updated value |
|-------|---------------|
| **Status** | **Accepted** (usage boundary) · wiring **Deferred** |
| **Source artifact(s)** | Add [`PHASE15_PLACEBO_CHARACTERIZATION_001.md`](PHASE15_PLACEBO_CHARACTERIZATION_001.md), this decision |
| **Why deferred (remaining)** | Multi-treated implementation; optional RecoveryRunner wiring; strict export automation |

---

## 8. Roadmap implications

| Question | Answer |
|----------|--------|
| **Is Phase 15 complete?** | **Yes** — plan committed, OC archived, this governance decision recorded |
| **Is Track A characterization complete?** | **Substantively yes** for core geo instrument set (SCM, TBRRidge, AugSynth × UnitJackKnife, BRB, KFold, Placebo). **Formal closure** pending [`TRACK_A_COMPLETION_REVIEW_001.md`](TRACK_A_COMPLETION_REVIEW_001.md) checkpoint |
| **What remains before Track B becomes primary?** | (1) Track A completion review artifact; (2) INV-031 synthesis archive (planning-only today); (3) optional INV-030 execution; (4) re-audit → ROADMAP_V5 — **not** additional core OC batteries |
| **Can Track B planning proceed?** | **Yes** — contracts may be drafted using governed trust vocabulary from Phases 11–15 |
| **Can Track B implementation start?** | **Not as primary focus** until Track A completion review explicitly clears transition ([`ROADMAP_V4.md`](ROADMAP_V4.md) §3b) |

### Track A program status (post–Phase 15)

| Phase | Status |
|-------|--------|
| 11 — SCM UnitJackKnife | **Complete** |
| 12 — TBRRidge inference | **Complete** (Phase 13 decision; KFold reconciliation addendum) |
| 14 — AugSynth OC | **Complete** |
| 15 — Placebo OC | **Complete** (this decision) |
| DID OC (DEF-016) | **Deferred** — not a blocker for geo core instrument closure |
| INV-030 / INV-031 | **Future research** — defined, not blockers |

**Sequencing:** Track A completion review → Track B implementation prioritization (`ExperimentSpec` → `ExperimentEvidence` → …) per user-directed checkpoint.

---

## 9. Non-claims

This governance decision **does not**:

- Promote Placebo (or any config) to **`production_safe`**  
- Add Placebo to **`NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`**  
- Certify Placebo as **nominally calibrated** for lift detection  
- Advance **maturity labels** in [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md)  
- Change **release gates** or automated blocking  
- Modify **placebo implementation**, thresholds, recovery scoring, or inference code  
- Claim **default multi-geo recovery DGP** support for Placebo  
- Conflate **`placebo_band`** with jackknife/bootstrap **confidence intervals**  
- Imply **package-wide** inference trust from single-mode null FPR = 0  

This decision **does**:

- Formally **close Phase 15**  
- Assign **honest governed roles** per Placebo path  
- Preserve **eligibility registry unchanged**  
- Route remaining gaps to **DEF-020** and Track B export discipline  
- Enable **Track A completion review** as the next governance gate before Track B implementation primacy  

---

## 10. Final recommendation table

| Path | Governed role | Evidence quality | Limitations | Future evidence required |
|------|---------------|------------------|-------------|-------------------------|
| **SCM + Placebo (single-treated)** | **Expert-review null-reference / diagnostic** | **Production** n=100 × 3 seeds; 22-cell matrix | Single-treated only; power = 0; not a CI | Multi-treated OC if product requires; RecoveryRunner wiring optional |
| **SCM + Placebo (multi-treated / default DGP)** | **Restrict — unsupported** | **Characterization** — 100% failure documented | `NotImplementedError` by design | Implementation + full OC + governance decision |
| **TBRRidge + Placebo (single-treated)** | **Expert-review diagnostic** (secondary to SCM) | **Characterization** n=30 only | Not production-tier archived; zero power | n≥100 archive; registry wiring if promoted |
| **TBRRidge + Placebo (multi-treated)** | **Restrict — unsupported** | Failure surface only | Same implementation bound as SCM | Same as multi-treated SCM |
| **TBR + Placebo** | **Research-only / unsupported** | Failure surface (`AssertionError`) | Aggregated-control exclusion | New design if ever required |
| **Placebo as CalibrationSignal** | **Null-monitor viable** (single-treated); **lift not calibrated** | Cross-mode context via INV-031 | Must not aggregate with CI modes | INV-031 synthesis; Track B schema |
| **Placebo as TrustReport lift signal** | **Do not use** | N/A | power = 0 | N/A until new inference design |

### Configuration actions

| Config | Action | Governed status | Eligibility | Notes |
|--------|--------|-----------------|-------------|-------|
| **SCM + Placebo** | **Restrict** | expert-review null-reference | **Exclude** | Single-treated OC only; `placebo_band` labeling mandatory |
| **TBRRidge + Placebo** | **Restrict** | expert-review diagnostic | **Exclude** | Characterization-tier evidence |
| **TBR + Placebo** | **Restrict** | unsupported | **Exclude** | Do not use in workflows |
| **SCM_UnitJackKnife** | **Retain** (unchanged) | expert-review null monitor | **Retain** | Sole eligible config |

### Phase 15 classification legend

| Term | Meaning |
|------|---------|
| **Expert-review null-reference** | Usable by reviewers as placebo null envelope with strict semantics |
| **Diagnostic** | Supports reviewer comparison; not automated decisioning |
| **Restrict** | Narrow geometry or export requirements |
| **Unsupported** | Hard failure or policy exclusion — do not enable silently |
| **Defer** | Future evidence or wiring — not abandonment |

---

## Appendix — Phase 15 closure checklist

| Criterion | Status |
|-----------|--------|
| Investigation plan committed | ✅ [`PHASE15_PLACEBO_INVESTIGATION_PLAN.md`](PHASE15_PLACEBO_INVESTIGATION_PLAN.md) |
| OC archive executed | ✅ [`PHASE15_PLACEBO_CHARACTERIZATION_001.md`](PHASE15_PLACEBO_CHARACTERIZATION_001.md) |
| Governance decision recorded | ✅ (this document) |
| INV-029 disposition assigned | ✅ → DEF-020 |
| Eligibility unchanged | ✅ |
| Maturity / release gates unchanged | ✅ |
| OPEN_INVESTIGATIONS updated | ☐ Recommended in follow-up editorial PR |
| DEF-020 registry text updated | ☐ Recommended in follow-up registry PR |
| Track A completion review | ☐ Next checkpoint — [`TRACK_A_COMPLETION_REVIEW_001.md`](TRACK_A_COMPLETION_REVIEW_001.md) (planned) |

---

*Governance record PHASE15-GOV-001. Phase 15 closed. Registry and code unchanged.*
