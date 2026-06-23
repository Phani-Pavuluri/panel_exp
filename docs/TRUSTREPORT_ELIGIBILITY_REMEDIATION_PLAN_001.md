# TrustReport Eligibility Remediation Plan 001

**Artifact ID:** TRUSTREPORT-ELIGIBILITY-REMEDIATION-PLAN-001  
**Verdict:** `trustreport_eligibility_remediation_planned_promotion_blocked`

## 1. Executive summary

Converts findings from [`TRUSTREPORT_ELIGIBILITY_VALIDATION_001`](track_d/TRUSTREPORT_ELIGIBILITY_VALIDATION_001_REPORT.md) into a method-specific remediation and revalidation program. **No method is promoted.** TrustReport authorization remains BLOCKED. Zero `ELIGIBLE_CANDIDATE` combinations exist today.

This artifact identifies root causes, minimum remediations, follow-up validation artifacts, execution order, and lanes worth fixing versus permanently excluding.

## 2. Why promotion cannot proceed

| Finding | Blocker |
|---------|---------|
| Zero `ELIGIBLE_CANDIDATE` combinations | No promotion candidacy |
| SCM+JK positive coverage ~7% | Causal-interval candidacy unsupported (**superseded for DCM-001** by harness correction + partial reassessment; ~90% level positive coverage with type-I caveats) |
| DID+bootstrap positive coverage 0% | Causal-interval candidacy unsupported |
| TBRRidge DCM-005 BLOCK + scale mismatch | Path-specific evidence incomplete |
| All D5 archives `trust_role_allowed=false` | Governance forbids trust claims |
| Downstream gateway BLOCK | Authorization separate and closed |

Promotion requires: remediation → revalidation → **`FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT`** (all DCM-001–008) → **`TRUSTREPORT_DOWNSTREAM_PROMOTION_001`** → downstream authorization update. Partial **`TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001`** (DCM-001 only) and **`FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001`** (2026-06-03) are complete; global TrustReport authorization remains false; no promotion candidates.

## 2a. Combination-validation scopes (do not conflate)

| Scope | Artifact | Role |
|-------|----------|------|
| **DCM-001–019** | [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) | Design-side compatibility and geometry matrix |
| **Layer-5 (30 rows)** | [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | Estimator × inference with reference designs |
| **DCM-001–008** | TrustReport eligibility queue | Deliberately narrower near-term promotion subset |

Omitted combinations are not all accidental. Many are intentionally outside the TrustReport queue (adapter-dependent, diagnostic-only, research-only, geometry-incompatible, forecast-not-causal, or lower priority). **Genuine gaps** requiring explicit terminal decisions before full reassessment are listed in §2b.

## 2b. Disposition decisions required before full reassessment

| Combination | Current issue | Decision needed |
|-------------|---------------|-----------------|
| AugSynth + UnitJackknife | Implemented; D5-INST evidence; no TrustReport lane | Validate later or explicitly keep research-only |
| SCM + Placebo | Implemented falsification path | Define null-monitor / diagnostic product class |
| TBRRidge + JK/JKP | Implemented; poor evidence | Remediate or explicitly exclude |
| DID production bootstrap | Defect diagnosed off-main; remediation pending | If production fix required: **`DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001`** (separate from reassessment) |
| Rerandomization combinations | Runtime capability; no dedicated D5-STAT lane | Schedule or explicitly defer |
| DCM-009–014 adapters | Classified; not executed | Future product surface vs adapter-only |
| Full matrix v2 | Planned; unscheduled | Explicit place in parallel later lane |

## 3. Current eligibility findings

Source: [`TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json`](track_d/archives/TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json)

| Combination | Status | Key metrics |
|-------------|--------|-------------|
| DCM-001 SCM+JK | ELIGIBLE_WITH_RESTRICTIONS | null coverage 93%; positive coverage 7%; type-I 6.7%; bias ratio >>1 on lift |
| DCM-002 AugSynth point | ELIGIBLE_WITH_RESTRICTIONS | Point-only; no interval evidence |
| DCM-003 TBR aggregate | INELIGIBLE | Geometry mismatch |
| DCM-004 DID+bootstrap | ELIGIBLE_WITH_RESTRICTIONS | **Reassessed 2026-06-18:** positive coverage ~93%; supported null type-I ~13%; aggregate ~32% (stress world); common timing + parallel-trends gate required |
| DCM-005-BRB | INSUFFICIENT_EVIDENCE | Null metrics OK; scale/bias mismatch on lift |
| DCM-005-KFOLD | INSUFFICIENT_EVIDENCE | Directional false signal 100% on null; scale mismatch |
| DCM-005-PLACEBO | INELIGIBLE | Null-monitor; not causal |
| DCM-006 multi-cell per-cell | PER_CELL_RESTRICTED | Marginal per-cell diagnostic/restricted only; familywise/pooled/global blocked |
| DCM-007 pooled | INELIGIBLE | Permanent exclusion |
| DCM-008 stratified+SCM/JK | DIAGNOSTIC_ONLY | Per-stratum diagnostic/restricted; aggregate readout characterization only — not a governed pooled causal estimand |

## 4. Root-cause taxonomy

| Category | Description | Examples in current evidence |
|----------|-------------|------------------------------|
| **E — Estimator bias** | Point estimate systematically wrong under treatment | SCM+JK mean bias ~8.59 vs 0.08 true lift (scale/units) |
| **I — Inference calibration** | Interval width/center wrong despite reasonable point | SCM+JK null coverage OK, positive coverage collapsed |
| **G — Geometry mismatch** | Estimator/inference incompatible with design geometry | TBR aggregate on unit-panel (DCM-003) |
| **S — Semantic misuse** | Readout class does not support claimed estimand | Point-only as interval; null-monitor as causal |
| **C — Evidence completeness** | Required validation artifact missing | Stratified+SCM/JK lacks D5-STAT; DID identification diagnostics |
| **R — Registry/governance block** | DCM row or inference-boundary forbids path | DCM-005 `restricted_requires_statistical_validation` |
| **P — Provenance** | Archive marks `trust_role_allowed=false` | All current D5 Level-B artifacts |

Remediation must tag each lane with primary root-cause letter(s). Algorithm changes are out of scope for this planning artifact.

## 5. Threshold taxonomy

Three tiers — **do not conflate**:

### 5.1 Characterization thresholds

Used in D5 Level-B and design-combination execution. Label: `provisional_for_characterization_only`.

- Null FPR mixed flag: >0.35 (weak-signal up to 0.45)
- Positive coverage mixed flag: <0.50 (eligibility screening only)
- Failure rate characterization cap: 0.35
- Coverage deviation from nominal: 0.15

**The 0.50 positive-coverage screen from eligibility validation is a characterization triage threshold, not a promotion threshold.**

### 5.2 Promotion-candidate thresholds

Future `TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001` will require, per combination and readout class:

- Coverage near nominal (existing readiness profiles suggest ≥0.90 under null; positive-scenario coverage must be demonstrated, not assumed)
- Type-I error controlled (readiness: ≤0.10 on clean null)
- Bias materially below effect scale on validated worlds
- Failure rate bounded (≤0.10 for promotion candidacy)
- Worst-world failures explained, not catastrophic
- Complete provenance and valid freshness
- Explicit readout semantics matching TrustReport class

### 5.3 Production acceptance thresholds

Defined only when `TRUSTREPORT_DOWNSTREAM_PROMOTION_001` and operator policy exist. Requires Battery C+ statistical validation, n≥100 replications where calibration applies, and explicit role-specific promotion evidence. **Not set in this artifact.**

Existing governance references: `calibration_report.py` (FPR ≤0.10, null coverage ≥0.90, power ≥0.80); `METHOD_STATISTICAL_VALIDATION_PROTOCOL_001` (interval validity hard gates only).

## 6. SCM + UnitJackknife remediation

**Problem:** Null-world coverage ~93% and type-I ~6.7% are acceptable for characterization. Positive-scenario coverage ~7% with bias ratio ~107× effect scale blocks causal-interval candidacy.

**Primary root causes:** I (inference calibration under treatment), E (scale/units mismatch between percent injection and level readout), possibly G (treated-unit jackknife resampling under treatment effects).

**Required diagnostic questions:**

| Question | Hypothesis if true |
|----------|-------------------|
| Is UnitJackknife only valid as null-monitor? | Restrict to `null_monitor` class; abandon causal-interval lane |
| Is the interval centered incorrectly? | I — recentering or bias correction study |
| Is variance underestimated under treatment? | I — widen intervals or alternative resampling |
| Is treated-unit geometry invalid for JK? | G — change resampling unit or geometry |
| Are sign/bias/carryover driving misses? | E — estimator bias under lift worlds |
| Estimator bias vs inference calibration? | Separate D5 worlds with known oracle |

**Follow-up artifact:** `D5-TRUST-SCM-JK-COVERAGE-REMEDIATION-001`

**Required outputs:**

- Null coverage by world
- Positive-effect coverage by world
- Type-I error (clean, weak-signal, post-shock null)
- Bias and RMSE vs effect scale
- Interval width distribution
- Effect-size sweep (2%, 5%, 8%, 12%)
- Donor-strength sweep (donor_stress worlds)
- Worst-world diagnostics (post_shock, outside_hull)
- Verdict: `causal_interval` vs `null_monitor` only

**Minimum remediation:** Diagnose before any algorithm change. Do not assume promotable.

**Worth fixing?** **Yes — highest priority.** High downstream value; null behavior partially acceptable; causal path may be recoverable or definitively restricted.

## 7. DID + bootstrap remediation

**Problem:** Positive-scenario coverage 0%. Null FPR 0% on parallel-null worlds. Callable failure ~6.7% on clean_parallel_null.

**Primary root causes:** C (identification diagnostics missing), I (bootstrap calibration), E (parallel-trends violations), possibly serial dependence ignored.

**Required diagnostic questions:**

| Question | Hypothesis if true |
|----------|-------------------|
| Is DID point estimation biased? | E — fix estimator or restrict worlds |
| Parallel-trend violations? | C — identification failure; not bootstrap-fixable |
| Bootstrap resampling unit wrong? | I — cluster/unit resampling change |
| Serial dependence ignored? | I — block bootstrap or alternative |
| Interval construction wrong? | I — percentile vs BCa |
| Treatment timing/geometry mismatch? | G — design-estimator alignment |

**Follow-up artifact:** `D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001` — ✅ **complete** (`did_bootstrap_production_miscentering_confirmed`)

**Diagnosis complete (2026-06-03):** Canonical harness `groups.values()` assignment defect confirmed; production bootstrap cumulative-readout miscentering confirmed. Eligibility status unchanged pending:

- `D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION`
- `DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001`
- DCM-004 eligibility reassessment

**Must separate:**

1. Identification failure (parallel trends, timing)
2. Estimator bias (ATT vs percent lift scale)
3. Bootstrap calibration (coverage under null and lift)
4. Serial-correlation handling

**Minimum remediation:** Identification audit before bootstrap tuning.

**Worth fixing?** **Yes — second priority.** Useful when parallel trends hold; may prove permanently restricted on unit-panel geo experiments.

## 8. TBRRidge BRB remediation

**Problem:** DCM-005 BLOCK (`restricted_requires_statistical_validation`). Harness: INSUFFICIENT_EVIDENCE. Null-world coverage 100%, type-I 0%; positive bias ratio ~104× on residual-mean readout vs percent injection.

**Primary root causes:** R (registry block), S (causal interval claimed on unvalidated path), E/I (readout scale mismatch documented in D5-STAT-TBRRIDGE-INF-001).

**Follow-up artifact:** `D5-TRUST-TBRRIDGE-BRB-001` ✅ — `production_defect_confirmed`; **`TBRRIDGE_BRB_INTERVAL_CORRECTION_001`** ✅ applied.

**Evaluate:** geometry support, interval semantics (causal vs forecast), null vs causal inference, coverage, type-I, failure rate, DCM-005 block reason (remediable if scale + semantics resolved).

**Worth fixing?** **Medium priority.** Block may be removable with evidence; scale alignment is prerequisite.

## 9. TBRRidge KFold remediation

**Problem:** Directional false signal 100% on clean null (KFold/TSKFold paths in archive). Massive bias ratio on positive worlds. Leakage guard flagged on KFold path.

**Primary root causes:** I (split policy / leakage), R (DCM-005 block), S (causal interval unvalidated).

**Follow-up artifact:** `D5-TRUST-TBRRIDGE-KFOLD-001`

**Evaluate:** chronological split integrity, fold policy, causal vs diagnostic role, whether path should be `diagnostic_only` permanently.

**Worth fixing?** **Medium-low priority.** High misuse risk if promoted; may remain diagnostic-only even after remediation.

## 10. TBRRidge placebo remediation

**Problem:** INELIGIBLE for causal TrustReport. Null-monitor path only.

**Primary root causes:** S (semantic — placebo is null-monitor, not causal).

**Follow-up artifact:** `DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001`

**Evaluate:** null-monitor calibration only; target class `null_monitor` or `diagnostic_only`. ✅ Characterized by `D5-TRUST-TBRRIDGE-PLACEBO-001` — single-treated restricted; provisional NULL_MONITOR_ONLY.

**Worth fixing?** **Low priority for causal promotion.** Valuable for null-screening semantics only.

## 11. Stratified + SCM/JK validation

**Problem:** DCM-008 ELIGIBLE_WITH_RESTRICTIONS on design feasibility only (`D5_DES_STAT_STRATIFIED_001`). Inherits generic SCM+JK stat evidence — insufficient for stratified combination.

**Status (2026-06-03):** ✅ **`D5-TRUST-STRATIFIED-SCM-JK-001`** complete.

**Findings:** Per-stratum SCM+JK on balanced two-strata geometry: coverage ~85.9%; per-stratum null type-I ~16.7%; aggregate characterization coverage ~89.7% with aggregate null type-I ~26.0%. SCM fit mode: per-stratum panel (aggregate treated units in stratum). Within-stratum donor pool preferred over global. **Aggregate stratified readout is characterization only, not a governed pooled causal estimand.** Aggregate causal claims blocked (100%). Weight-dominance rate ~6.1%. Verdict: `stratified_scm_jk_diagnostic_only`. Production defect: `geometry_or_semantic_limitation` (not isolated code bug).

**Investigations:** `INV-STRATIFIED-SCM-JK-TRUSTREPORT-DISPOSITION-001` → RESOLVED (`DIAGNOSTIC_ONLY`).

**Next artifact:** `FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT`

**Primary root causes:** C (aggregate readout semantics), G (strata-specific donor support), I (small-stratum instability).

**Focus (addressed in artifact):**

- Per-stratum vs aggregate readout semantics
- Donor-pool policy (within-stratum vs global)
- Small-stratum and weight-dominance restrictions
- Stratified-specific behavior (distinct from DCM-006)

## 12. Multi-cell per-cell inference

**Problem:** DCM-006 ELIGIBLE_WITH_RESTRICTIONS. Cell identity preserved 100%; per-cell interval coverage and shared-control dependence previously unresolved.

**Status (2026-06-03):** ✅ **`D5-TRUST-MULTICELL-PERCELL-INFERENCE-001`** complete.

**Findings:** Per-cell SCM+JK coverage ~92.6%; familywise null type-I ~27.2% (unadjusted interval-excludes-zero only); simultaneous coverage ~85.6%; shared-control cross-cell correlation ~0.90. Pooled multi-cell readout blocked. Bonferroni/Holm proxy comparison **not valid** — SCM+JK lacks per-cell p-values and adjusted-interval reconstruction; equal FWER across proxy labels does not imply procedure ineffectiveness. Verdict: `multicell_percell_multiplicity_unresolved`. Aggregate: **INSUFFICIENT_EVIDENCE** for simultaneous multi-cell decisioning; **PER_CELL_RESTRICTED** for marginal per-cell diagnostic/restricted intervals.

**Investigations:** `INV-MULTICELL-PERCELL-INFERENCE-001` → RESOLVED. Deferred: `INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001`, `INV-MULTICELL-MULTIPLICITY-CALIBRATION-001`.

**Next artifact:** `D5-TRUST-STRATIFIED-SCM-JK-001`

**Semantic guardrail (2026-06-03):** ✅ [`MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001.md`](MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001.md) — distinguishes parallel marginal readouts (multiplicity not required) from competing-cell selection (multiplicity required). Does not authorize TrustReport.

**Primary root causes:** C (multiplicity/familywise evidence), I (simultaneous intervals), G (shared-control covariance).

**Focus (addressed in artifact):**

- Shared-control covariance structure
- Multiplicity and simultaneous intervals
- Per-cell and worst-cell coverage
- Dependence between cell estimates
- No pooled claims
- Explicit cell ID and per-cell estimand only

**Worth fixing?** **Fifth priority.** Restricted `per_cell_restricted` class is the ceiling unless bridge evidence exists.

**Pooled multi-cell (DCM-007):** Permanently excluded unless separate bridge artifact and estimand validated.

## 13. TrustReport semantic classes

Do not use one generic TrustReport eligible flag. Explicit readout classes:

| Class | Meaning | Current lanes |
|-------|---------|---------------|
| `descriptive_point` | Non-inferential point display | AugSynth point (DCM-002) |
| `null_monitor` | Null viability / placebo screen | SCM+JK placebo path; TBRRidge placebo (after validation) |
| `causal_interval` | Causal uncertainty for ATT/lift | SCM+JK (after remediation); DID+bootstrap (after remediation); TBRRidge BRB (if ever) |
| `per_cell_restricted` | Per-cell estimand only; multiplicity caveats | Multi-cell per-cell (DCM-006) |
| `diagnostic_only` | Comparator / triangulation; no export | TBRRidge KFold; conformal paths |

Future promotion artifacts must approve **class + DCM row + geometry**, not estimator name alone.

## 14. Permanent exclusions

Remain ineligible unless a **separate future artifact** explicitly changes them:

- Pooled multi-cell causal claim (DCM-007)
- Point-only estimator used as interval evidence (DCM-002 interval misuse)
- Forecast interval labeled causal
- Null-monitor interval labeled causal
- Directional sign labeled significance
- Unit-panel TBR geometry mismatch (DCM-003)
- Legacy native result
- Missing governed marker
- Missing estimator or inference identity
- Blocked inference-boundary result (without reassessment)

## 15. Evidence gaps

| Gap | Affected combinations |
|-----|----------------------|
| Positive-scenario coverage | DCM-001, DCM-004, DCM-005 |
| Dedicated stratified D5-STAT | DCM-008 |
| Per-cell interval coverage | DCM-006 |
| Identification diagnostics | DCM-004 |
| TBRRidge causal semantics proof | DCM-005 |
| Scale alignment (percent vs level readout) | DCM-001, DCM-005 |
| Battery C+ validation | All promotion candidates |
| Role-specific promotion evidence | All |

## 16. Follow-up artifacts

| ID | Lane | Blocks |
|----|------|--------|
| `D5-TRUST-SCM-JK-COVERAGE-REMEDIATION-001` | SCM+JK causal vs null-monitor | DCM-001 causal class | ✅ complete |
| `D5-STAT-SCM-JK-001-HARNESS-CORRECTION` | Canonical SCM-JK harness + archive | DCM-001 evidence baseline | ✅ complete |
| `D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001` | DID identification + bootstrap diagnosis | DCM-004 | ✅ complete |
| `D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION` | Canonical DID bootstrap harness + archive | DCM-004 evidence baseline | ✅ complete |
| `DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001` | Production DID bootstrap readout alignment | DCM-004 | ✅ complete |
| `DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001` | Partial re-run (DCM-004 only) | DCM-004 promotion candidacy | ✅ complete (DCM-004 only) |
| `D5-TRUST-TBRRIDGE-BRB-001` | TBRRidge BRB path | DCM-005-BRB | ✅ complete |
| `TBRRIDGE_BRB_INTERVAL_CORRECTION_001` | Production BRB interval alignment | DCM-005-BRB | ✅ complete |
| `INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001` | BRB variance calibration / null coverage | DCM-005-BRB | OPEN — [`OPEN_INVESTIGATIONS_001.json`](governance/OPEN_INVESTIGATIONS_001.json) |
| `D5-TRUST-TBRRIDGE-KFOLD-001` | TBRRidge KFold path | DCM-005-KFOLD | ✅ complete — not causal-interval eligible; [`OPEN_INVESTIGATIONS_001.json`](governance/OPEN_INVESTIGATIONS_001.json) |
| `D5-TRUST-TBRRIDGE-PLACEBO-001` | TBRRidge placebo null-monitor | DCM-005-PLACEBO | ✅ complete — null-monitor / falsification only; [`OPEN_INVESTIGATIONS_001.json`](governance/OPEN_INVESTIGATIONS_001.json) |
| `DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001` | DCM-005 partial re-run | DCM-005 promotion candidacy | ✅ complete — path-specific restrictions; no authorization |
| `TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001` | BRB variance remediation | DCM-005-BRB causal path | ✅ complete — candidate_only; null gates fail |
| `DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001` | Post-remediation BRB adjudication | DCM-005-BRB | ✅ complete — `BRB_DIAGNOSTIC_ONLY`; no authorization |
| `TRUSTREPORT_DOWNSTREAM_PROMOTION_001` | Restricted row-level promotion gate | DCM-001/004 | ✅ complete — row-level restricted only; no platform auth |
| `D5-TRUST-STRATIFIED-SCM-JK-001` | Stratified combination | DCM-008 | ✅ complete |
| `D5-TRUST-MULTICELL-PERCELL-INFERENCE-001` | Per-cell inference | DCM-006 | ✅ complete |
| `TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001` | Partial re-run (DCM-001 only) | DCM-001 promotion candidacy | ✅ complete (DCM-001 only) |
| `FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001` | Matrix reassessment all DCM rows | Promotion candidacy | ✅ complete — no promotion candidates; global authorization false |
| `TRUSTREPORT_DOWNSTREAM_PROMOTION_001` | Role-specific promotion | Authorization update |

## 17. Prioritization

Ranked by scientific value × likelihood of remediation × downstream usefulness ÷ (cost + misuse risk):

| Rank | Lane | Rationale |
|------|------|-----------|
| 1 | SCM+JK coverage diagnosis | Best null behavior; highest TrustReport value if causal path recoverable |
| 2 | DID+bootstrap diagnosis | Common design; may fail identification — still must diagnose |
| 3 | TBRRidge inference paths (BRB → KFold → Placebo) | Separate paths; BRB most plausible for causal if scale fixed |
| 4 | Stratified+SCM/JK | Depends on DCM-001 outcome |
| 5 | Multi-cell per-cell inference | Restricted class ceiling |
| 6 | **`FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT`** | After remediation artifacts + disposition decisions |
| 7 | TrustReport promotion decision | After full reassessment only |

**Not scheduled:** Promotion before reassessment. DCM-003, DCM-007 remain excluded. AugSynth point remains `descriptive_point` only without new interval evidence.

## 18. Dependencies

```
D5-TRUST-SCM-JK-COVERAGE-REMEDIATION-001  ✅
  → D5-STAT-SCM-JK-001-HARNESS-CORRECTION  ✅
  → TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001  ✅ (DCM-001 only — not full reassessment)
  → informs D5-TRUST-STRATIFIED-SCM-JK-001
  → informs D5-TRUST-MULTICELL-PERCELL-INFERENCE-001 (shared JK inference)

D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001  ✅
  → D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION  ✅
  → DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001  ✅
  → DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001  ✅
  → D5-TRUST-TBRRIDGE-BRB-001  ✅
  → TBRRIDGE_BRB_INTERVAL_CORRECTION_001  ✅

D5-TRUST-TBRRIDGE-{KFOLD,PLACEBO}-001  ← next
  → independent; do not collapse

Disposition decisions (§2b): AugSynth+JK · SCM+Placebo · TBRRidge JK/JKP · rerandomization · DCM-009–014

All D5-TRUST-* complete + disposition decisions recorded
  → FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT
  → TRUSTREPORT_DOWNSTREAM_PROMOTION_001 (if any ELIGIBLE_CANDIDATE)
  → downstream authorization gateway update

Parallel later lane (non-blocking): DCM-009–019 adapters → matrix v2 → broader qualification
```

## 19. Promotion prerequisites

Before any `ELIGIBLE_CANDIDATE` or authorization update:

1. Completed remediation artifact for combination
2. Reassessment pass with promotion-candidate thresholds
3. Explicit TrustReport semantic class approval
4. DCM row governance update (if block was remediable)
5. `TRUSTREPORT_DOWNSTREAM_PROMOTION_001` with role-specific evidence
6. No permanent exclusion violated
7. Operator/policy sign-off (future)

## 20. Reassessment criteria

**Partial reassessment (`TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001`):** ✅ complete for **DCM-001 only** after SCM-JK harness correction.

**Full reassessment (`FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT`):** runs when:

- Remaining `D5-TRUST-*` remediation artifacts complete with `remediation_verdict` ∈ {`causal_interval_supported`, `null_monitor_supported`, `per_cell_restricted_supported`, `descriptive_point_supported`}
- Disposition decisions in §2b recorded for AugSynth+JK, SCM+Placebo, TBRRidge JK/JKP, rerandomization, and adapter lanes as applicable
- Updated evidence ingested into eligibility harness
- Re-evaluates **all DCM-001–008** rows; may still yield zero candidates
- Must not lower thresholds to force candidates
- `trust_report_authorized` remains false until promotion artifact

## 21. Authorization constraints

- Downstream authorization gateway unchanged — all `trust_report` requests BLOCKED
- `trust_report_ready` remains false
- `trust_report_promotion_candidate` may only become true after reassessment with `ELIGIBLE_CANDIDATE`
- Eligibility and authorization remain separate layers
- No algorithm changes in this planning artifact

## 22. Roadmap updates

Authorized sequence:

```
TrustReport eligibility validation (✅)
  → eligibility remediation plan (✅ this artifact)
  → DCM-001 partial reassessment (✅ TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001)
  → governance scope reconciliation (✅)
  → method-specific revalidation (D5-TRUST-* — DID current)
  → disposition decisions (§2b)
  → FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT
  → TrustReport promotion decision
  → downstream authorization update
```

Future artifacts (blocked until prerequisites):

- `FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT`
- `TRUSTREPORT_DOWNSTREAM_PROMOTION_001`
- `DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001` (conditional)

## 23. Governance verdict

`trustreport_eligibility_remediation_planned_promotion_blocked`
