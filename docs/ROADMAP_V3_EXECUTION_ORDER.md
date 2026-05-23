# ROADMAP v3 — Frozen execution order (Phases 5–8)

**Status:** **FROZEN** — approved sequence; do not reorder without explicit reassessment  
**Effective:** 2026-05-20  
**Authority:** `docs/ROADMAP_V3.md` (scope and success criteria), `docs/ALGORITHM_REASSESSMENT.md` (risk inventory), `docs/VALIDATION_COVERAGE.md` (wiring truth)  
**Package version at freeze:** 0.2.1

This document turns roadmap v3 “top 3 PRs” and audit gates into an **approved execution sequence**. It is planning only: **no implementation is authorized by this file alone.**

---

## Scope lock (all phases)

The following are **out of scope** for Phases 5–8 unless a future roadmap revision explicitly reopens them:

| Category | Locked out |
|----------|------------|
| **Estimators** | No new estimator classes; no `production_safe` promotions; no SDID/TROP/Bayesian recovery wiring |
| **Inference** | No new inference modes; no Jackknife+ / time Jackknife+; no new registry entries |
| **Artifacts** | No new experiment cards, bundles, readiness schema versions, or blocking go/no-go gates |
| **Estimation math** | Phases must not change point estimates, inference algorithms, or default `run_analysis` result keys |
| **Deferred product** | BayesianTBR expansion, TROP productionization, spillover estimation, consensus ATT, automated blocking readiness |

**Allowed change types:** validation harnesses, calibration jobs, documentation, opt-in review/diagnostic attachments, tests that assert existing contracts, and focused audit write-ups.

---

## Execution phases (summary)

| Phase | Name | Depends on | Blocks audit? |
|-------|------|------------|---------------|
| **5** | Production calibration proof | Phases 1–4 shipped (estimand alignment, interval gating, smoke helper, DGP semantics) | **Yes** — Phase 8 gate #1 |
| **6** | DID interval policy | Phase 5 not required; parallel-safe with 7 | **Yes** — Phase 8 gate #2 |
| **7** | Operational stability (review flags) | Opt-in diagnostics API shipped (`build_estimator_review`) | Partial — Phase 8 gate #5 |
| **8** | Focused re-audit | Phases 5–7 complete (or explicitly waived with documented rationale) | N/A (deliverable is the audit) |

**Approved order:** **5 → 6 → 7 → 8**  
Phase 6 may start in parallel with Phase 5 only if DID policy work is **docs + tests of existing gating** (no estimator changes). Phase 7 must not precede Phase 6 if DID support matrix is referenced from review docs.

---

## Phase 5 — Production calibration proof

### Objective

Establish whether **aligned** recovery interval configs are **nominally calibrated** at production replication scale—not merely smoke-tested at n≈2–6.

**In scope configs only:**

- `SCM_UnitJackKnife`
- `TBRRidge_Kfold`
- `TBRRidge_BlockResidualBootstrap`

**Scenarios:** `recovery_null_effect`, `recovery_positive_effect` (both must use `missingness_policy=none` per existing calibration scenarios).

**Deliverables (validation layer only):**

- Separate **CI smoke** tier (n = 5–10, fast, no production pass/fail claims)
- **Calibration job** tier (n = 100–300, multi-seed)
- Archived metrics: coverage, FPR, power, failure rate, seed variability
- Acceptance evaluator tied to `calibration_report.py` thresholds

### Risks reduced

| Risk (from reassessment / v3) | How |
|-------------------------------|-----|
| Statistical #6–7 — interval coverage unobserved / tiny n | Finite FPR/coverage/power at n≥100 for aligned configs |
| v3 unresolved #1 — no production-scale nominal calibration | Evidence artifact + enforced acceptance criteria |
| Must-fix #2 — recovery at scale with production inference modes | Uses existing inference recovery configs; no new modes |
| Silent NaN calibration | Explicit pass/fail; smoke tier labeled non-production |

### Acceptance criteria

| # | Criterion | Target |
|---|-----------|--------|
| 5.1 | **Replication scale** | Production tier: n ≥ 100 per config × scenario × seed run |
| 5.2 | **FPR (null)** | Mean FPR ≤ 0.10 across ≥3 seeds on `recovery_null_effect` |
| 5.3 | **Coverage (null)** | Mean coverage ≥ 0.90 on `recovery_null_effect` (or documented misspecification with explicit failure code—not NaN) |
| 5.4 | **Failure rate** | &lt; 5% failed simulations per config; all failures carry `failure_type` |
| 5.5 | **Seed stability** | Coverage and FPR spread across 3 seeds ≤ 0.12 (or documented wider tolerance with rationale) |
| 5.6 | **Power (positive)** | `power_status=computed` on `recovery_positive_effect`; power ≥ 0.80 **should** pass (strong signal, not hard blocker for Phase 8 if documented) |
| 5.7 | **Eligibility** | Only configs in `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`; **exclude** `DID_Bootstrap` until Phase 6 resolves policy |
| 5.8 | **No mismatch coverage** | Zero finite coverage when `interval_estimand != relative_att_post` (regression on existing gating) |

### Dependencies

| Dependency | Status |
|------------|--------|
| `run_nominal_calibration_check()` / `RecoveryRunner` inference configs | **Shipped** |
| `recovery_intervals.py` aligned path for SCM/TBR | **Shipped** |
| `calibration_report.py` thresholds | **Shipped** |
| `recovery_null_effect` / `recovery_positive_effect` with `missingness_policy=none` | **Shipped** |
| CI runner or manual job slot for n≥100 | **Required before Phase 5 close** |

### Expected runtime / CI impact

| Tier | n | Configs × scenarios × seeds | CI role |
|------|---|----------------------------|---------|
| CI smoke | 5–10 | 3 × 2 × 1 | **Default PR CI** — structure + eligibility tests only; **must not** claim production calibration |
| Production job | 100–300 | 3 × 2 × 3 | **Nightly or manual** — expect **tens of minutes to hours** depending on hardware; **not** on every PR by default |
| Unit tests | 2–6 | Subset | Existing fast tests remain; add `@pytest.mark.slow` for optional local/ nightly full battery |

**CI policy:** PR pipeline stays green with smoke tier; production tier failure blocks Phase 8 sign-off, not necessarily every PR merge (team choice: nightly gate vs release gate—document in job README).

---

## Phase 6 — DID interval policy

### Objective

Make the **DID point vs interval estimand split** explicit and auditable: support **relative ATT point** scoring and **cumulative ATT intervals** on the estimator, while **excluding relative ATT interval calibration** unless a mathematically justified relative-ATT interval path is built (Option A—**not** the default plan).

**Preferred path (Option B):** Document and test the support matrix; no hidden conversion from cumulative bootstrap CI to relative coverage.

### Risks reduced

| Risk | How |
|------|-----|
| v3 unresolved #2 — DID intervals not aligned with scored relative ATT | Policy visible; recovery cannot claim relative coverage for DID |
| False calibration from scaled cumulative CI | Permanently rejected approach; tests guard regression |
| Algorithm reassessment #5 — ATT under pretrend violation | Complementary to existing `did_pretrend_contract`; does not block export |
| Interval estimand mismatch (partially closed) | Completes **documentation + support matrix** side |

### Acceptance criteria

| # | Criterion | Target |
|---|-----------|--------|
| 6.1 | **Support matrix published** | Table: point `relative_att_post` ✓; interval `cumulative_att` ✓; relative ATT interval calibration ✗ |
| 6.2 | **No hidden conversions** | No recovery code path computes DID relative coverage via cumulative CI scaling |
| 6.3 | **Tests** | `DID_Bootstrap` remains `interval_estimand_mismatch` / not nominal-eligible |
| 6.4 | **Docs** | `VALIDATION_COVERAGE.md` and/or dedicated policy module docstring reference the matrix |
| 6.5 | **Option A bar** | If pursued later: separate roadmap amendment + proof of estimand equivalence; **not** part of Phase 6 default |

### Dependencies

| Dependency | Status |
|------------|--------|
| `recovery_intervals.py` DID gating (`f1a276c`) | **Shipped** |
| `nominal_calibration` DID ineligibility | **Shipped** |
| Phase 5 | **Independent** (Phase 5 already excludes DID) |

### Expected runtime / CI impact

| Work | CI impact |
|------|-----------|
| Docs + policy module + regression tests | **Low** — seconds added to pytest |
| Option A (relative ATT intervals) | **Deferred** — would touch `DID.py` + bootstrap path; **not** Phase 6 |

---

## Phase 7 — Operational stability (review flags)

### Objective

Use existing stability/diagnostic machinery for **human review**, not passive reporting: opt-in `review_flags` (e.g. donor concentration, residual drift, fold instability) **without** changing estimates, blocking runs, or default `results` schema.

**Flag families:**

| Estimator family | Flags (review-only) |
|------------------|---------------------|
| SCM / AugSynth (simplex weights) | `high_donor_concentration`, `donor_instability`, `residual_drift` |
| TBRRidge (incl. k-fold) | `coefficient_instability`, `residual_drift`, `fold_instability` (when inference is k-fold) |

### Risks reduced

| Risk | How |
|------|-----|
| Algorithm correctness #6 — SCM post-period extrapolation blind spot | Visible on `scm_structural_break` / `scm_trend_mismatch` |
| v3 unresolved #5 — stability not default | Operational via `build_estimator_review(..., attach_review_flags=True)` |
| v3 PR 3 (stability summary) | Delivers review flags without default attach |
| Structural-break scenario unwired to assertions | Scenario triggers **warnings** in review output |

### Acceptance criteria

| # | Criterion | Target |
|---|-----------|--------|
| 7.1 | **Opt-in only** | Default `run_analysis` results keys unchanged (no `review_flags` unless requested) |
| 7.2 | **No estimate changes** | Bit-identical point/interval outputs vs pre-phase for same inputs |
| 7.3 | **Structural break** | `scm_structural_break` → `residual_drift` at least `warn` via review API |
| 7.4 | **No blocking** | Flags never raise or abort `run_analysis` |
| 7.5 | **Reuse** | Prefer `counterfactual_stability_tests.py` / existing diagnostic collectors over duplicate math |
| 7.6 | **Schema** | `review_flags` values: bool and/or `ok` / `warn` / `fail` / `unavailable` |

### Dependencies

| Dependency | Status |
|------------|--------|
| `build_estimator_review`, `collect_estimator_diagnostics` | **Shipped** |
| `scm_structural_break` in SCM recovery battery | **Shipped** |
| Phase 6 | **Soft** — support matrix should be frozen before external docs cite DID |

### Expected runtime / CI impact

| Work | CI impact |
|------|-----------|
| Review flag collection on smoke panels | **Low–medium** — a few extra `run_analysis` calls in new tests |
| Full stability suite on every PR | **Out of scope** — keep structural-break checks targeted |

---

## Phase 8 — Focused re-audit

### Objective

Answer five algorithm/statistical questions **without** rerunning the large architecture/governance audit. Produce a short evidence doc (e.g. `docs/ALGORITHM_AUDIT_V4.md`) referencing Phase 5–7 artifacts.

### Audit questions (must answer)

1. **Nominal calibration demonstrated?** — Phase 5 production-tier artifacts  
2. **Estimand consistency?** — Point vs interval vs scored target; Phase 6 DID policy  
3. **DGP behavior honest?** — Missingness, stagger metadata; no regression on calibration scenarios  
4. **Intervals statistically valid?** — Aligned configs only; DID excluded from relative calibration claims  
5. **Stability risks visible?** — Phase 7 review flags on stress scenarios  

### Risks reduced

| Risk | How |
|------|-----|
| Over-claiming from smoke tests | Audit tied to n≥100 evidence |
| Stale reassessment | Closes loop on `ALGORITHM_REASSESSMENT.md` open items relevant to Phases 5–7 |

### Acceptance criteria

| # | Criterion | Target |
|---|-----------|--------|
| 8.1 | **Evidence links** | Each question cites job output, test module, or doc section |
| 8.2 | **Pass/fail explicit** | Per question: Met / Partial / Not met |
| 8.3 | **No scope creep** | No new estimator/inference/artifact recommendations in audit body |
| 8.4 | **Suite green** | `poetry run pytest tests/ -q` at audit commit |
| 8.5 | **v3 §6.1 gates** | Report against must-pass table in `ROADMAP_V3.md` §6.1 |

### Dependencies

| Dependency | Required? |
|------------|-----------|
| Phase 5 production job complete | **Yes** for Q1, Q4 |
| Phase 6 policy frozen | **Yes** for Q2, Q4 |
| Phase 7 review flags | **Yes** for Q5 (or document waiver) |
| Phases 1–4 (shipped) | **Yes** (baseline) |

### Expected runtime / CI impact

| Work | CI impact |
|------|-----------|
| Doc-only audit | **None** |
| Optional re-run of production job for audit snapshot | Manual/nightly |

---

## Hard blockers vs optional vs deferred

### Hard blockers (must complete before Phase 8 sign-off)

| ID | Blocker | Phase |
|----|---------|-------|
| B1 | Production-tier calibration job (n≥100) for all three aligned configs | 5 |
| B2 | FPR ≤ 0.10 and coverage ≥ 0.90 on null (or explicit documented failure) | 5 |
| B3 | DID relative ATT interval calibration **not** claimed without Option A | 6 |
| B4 | Zero finite coverage when `interval_estimand != relative_att_post` | 5–6 regression |
| B5 | Full test suite green | All |

### Optional (strong signal, not Phase 8 hard blockers)

| ID | Item | Phase |
|----|------|-------|
| O1 | Power ≥ 0.80 on positive scenario at n≥100 | 5 |
| O2 | Recovery failure rate &lt; 5% at n≥50 on core battery | 5 |
| O3 | Heterogeneous-effect documentation (pooled vs canonical truth) | 8 appendix |
| O4 | `fold_instability` for TBRRidge k-fold when diagnostics available | 7 |
| O5 | Nightly archival of calibration JSON/CSV artifacts | 5 |

### Deferred (explicitly not in Phases 5–8)

| ID | Item | Reason |
|----|------|--------|
| D1 | BayesianTBR / BayesianTBRHorseShoe expansion | Research-only; scope lock |
| D2 | TROP productionization / validation runner wiring | `SKIPPED_ESTIMATORS`; smoke only today |
| D3 | SyntheticDID / SDID recovery wiring | No `RecoveryRunner` config |
| D4 | New readiness rules, cards, bundles | Artifact scope lock |
| D5 | `production_safe` label promotions | Policy: no estimator meets bar |
| D6 | Spillover estimation in core estimators | DGP-only stress today |
| D7 | New inference modes (Jackknife+, etc.) | Scope lock |
| D8 | DID Option A — relative ATT intervals | Requires roadmap amendment |
| D9 | Multi-treated / heterogeneous estimand unification | Beyond current recovery contract |
| D10 | Unified power-null vs recovery-null DGP | Separate systems |
| D11 | Automated blocking readiness gates | Advisory-only policy |
| D12 | Large architecture/governance re-audit | Phase 8 is focused mini-audit only |

---

## Confirmation: no new surface area

| Check | Phase 5 | Phase 6 | Phase 7 | Phase 8 |
|-------|---------|---------|---------|---------|
| New estimators | ✗ | ✗ | ✗ | ✗ |
| New inference methods | ✗ | ✗ | ✗ | ✗ |
| New artifacts (cards/bundles/readiness) | ✗ | ✗ | ✗ | ✗ |
| Changes default `run_analysis` keys | ✗ | ✗ | ✗ | ✗ |
| Changes estimator/inference math | ✗ | ✗ | ✗ | ✗ |

---

## Implementation PR sequence (after freeze)

When implementation is authorized, use **one PR per phase** (minimum):

1. **PR-5** — Production calibration harness + smoke/production tiers + acceptance evaluator + slow/nightly job docs  
2. **PR-6** — DID interval policy doc/module + regression tests (no DID math change)  
3. **PR-7** — `review_flags` via opt-in `build_estimator_review` + structural-break tests  
4. **PR-8** — `ALGORITHM_AUDIT_V4.md` only (plus links from `ROADMAP_V3.md`)

Do **not** combine phases in a single PR unless explicitly approved for emergency fix.

---

*Frozen execution order. Supersedes informal ordering in chat and cancelled partial implementations. Package code changes require a separate implementation PR per phase.*
