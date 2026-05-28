# Phase 12 investigation plan — TBRRidge inference

**Status:** governed investigation plan (pre-execution)  
**Last updated:** 2026-05-28  
**Package version:** 0.2.1  
**Phase:** 12 — TBRRidge inference investigation program  
**Prerequisite:** BRB bound-ordering fix merged to `main` (correctness preservation; eligibility unchanged)

**Related:** [`ROADMAP_V4.md`](ROADMAP_V4.md) § Phase 12 · [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) § Phase 12 program · [`CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md) · [`CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md) · [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) · [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md)

**This document does not:** modify code, change eligibility, run calibration jobs, tune thresholds, or make promotion claims.

---

## 1. Executive purpose

Phase 12 is an **investigation program**, not a fix effort and not a path to “make TBRRidge production-ready.”

The program asks one governing question:

> **Can TBRRidge inference modes support calibrated expert-review workflows** — with honest operating characteristics, documented failure surfaces, and traceable evidence — under the project’s estimand and interval contracts?

TBRRidge **point recovery** (`inference=None`) remains available today. Phase 12 concerns **inference-enabled configs** removed from nominal calibration after Run 001:

| Config | Skip reason (current) | Run 001 headline |
|--------|----------------------|------------------|
| `TBRRidge_BlockResidualBootstrap` | `brb_bounds_inverted_run001` | Null FPR = 1.0, coverage = 0.0 (inverted bounds) |
| `TBRRidge_Kfold` | `kfold_multi_treated_unsupported_run001` | 100% `ValueError` on default multi-treated `recovery_*` panels |

**Scientific posture:** Characterize reality honestly. You are not trying to “win.” A successful Phase 12 may conclude that BRB or Kfold should **remain excluded**, be **single-treated-only**, or be **permanently research-only** — if evidence supports it.

**Current eligibility (frozen for Phase 12 planning):** `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS = {"SCM_UnitJackKnife"}` only. No registry change without archived evidence and the full advancement policy chain ([`ROADMAP_V4.md`](ROADMAP_V4.md) § Promotion policy).

---

## 2. Investigation tracks

Four tracks run in parallel where possible. Each produces an archived artifact before any governance decision (Phase 13).

### INV-008 — BRB operating characteristics after bound-ordering fix

**Hypothesis (to test, not assume):** Correcting `apply_bounds_to_results` removes the Run 001 anti-calibration mechanism; remaining OC may still fail null FPR/coverage targets or show unstable geometry.

**Questions:**

- Did the BRB bound-ordering fix restore **valid intervals** (`ci_lower ≤ ci_upper`, finite width)?
- What are **null FPR**, **coverage**, **power**, **interval width**, and **failure rate** at n≥100 after the fix?
- Does BRB remain **unstable across seeds** (high cross-seed std on FPR/coverage)?
- Should BRB **remain excluded**, become **conditionally eligible**, or be **retired** from relative-ATT nominal calibration?

**OPEN_INVESTIGATIONS cross-links:** [TBRRidge BRB inference behavior](OPEN_INVESTIGATIONS.md#tbrridge-brb-inference-behavior)

---

### INV-007 — KFold geometry characterization

**Hypothesis (to test, not assume):** Kfold failure on Run 001 is a **multi-treated geometry** limitation, not insufficient pre-period length; single-treated panels may behave differently.

**Questions:**

- Does KFold work only for **single-treated** panels (as in existing smoke test)?
- Does it **fail systematically** for multi-treated default `recovery_*` panels?
- Is failure due to **shape/broadcast assumptions** in the inference path vs **estimator limitations**?
- Should KFold be **single-treated-only**, **fixed** for multi-treated, or **retired** from calibration scope?

**OPEN_INVESTIGATIONS cross-links:** [TBRRidge Kfold multi-treated geometry](OPEN_INVESTIGATIONS.md#tbrridge-kfold-multi-treated-geometry)

---

### INV-003 — Multi-treated aggregation semantics

**Hypothesis (to test, not assume):** Recovery scoring via pooled `_path_relative_att` may diverge from canonical treated-cell mean ATT when effects are heterogeneous — affecting interpretation of TBRRidge (and other families) on default multi-treated DGP.

**Questions:**

- When does **pooled/path relative ATT** differ from **canonical treated-cell mean ATT**?
- Which estimand should TBRRidge recovery **report** for multi-treated panels?
- Are **heterogeneous effects** safely interpretable under current aggregation?

**Scope note:** Broader than TBRRidge; informs calibration scenario design and expert-review language.

**OPEN_INVESTIGATIONS cross-links:** [Multi-treated default recovery DGP](OPEN_INVESTIGATIONS.md#multi-treated-default-recovery-dgp) · [Heterogeneous vs pooled recovery scoring](OPEN_INVESTIGATIONS.md#heterogeneous-vs-pooled-recovery-scoring)

---

### INV-017 — Calibration scaling and governance

**Hypothesis (to test, not assume):** Run 002 and Phase 12 OC archives can establish **repeatable archival conventions** and **eligibility-evolution rules** without implying package-wide calibration or automated trust scores.

**Questions:**

- What artifacts must be archived for **n≥100** calibration runs?
- What evidence is required before a config becomes **eligible again**?
- What is the **promotion chain** from investigation → eligible → expert-review supported?
- How should future **`CalibrationSignal` / `TrustReport`** inputs be derived from archived OC (Track B foundation)?

**OPEN_INVESTIGATIONS cross-links:** [Calibration scaling (CI n ≪ production n)](OPEN_INVESTIGATIONS.md#calibration-scaling-ci-n--production-n) · [Trust-score / TrustReport evolution](OPEN_INVESTIGATIONS.md#trust-score--trustreport-evolution)

---

## 3. Experimental design

Shared constants (from Run 001 and production harness — **do not tune for Phase 12**):

| Parameter | Value | Source |
|-----------|-------|--------|
| Nominal α | 0.05 | `production_nominal_calibration` |
| Production `n_simulations` | **100** per config × scenario × seed | `PRODUCTION_N_SIMULATIONS_DEFAULT` |
| Production seeds | **0, 1, 2** | `PRODUCTION_RANDOM_SEEDS_DEFAULT` |
| Null thresholds | coverage ≥ **0.90**, FPR ≤ **0.10**, failure_rate < **0.05** | `calibration_report.py`, Run 001 §3 |
| Power (informative) | target **0.80** on positive scenario | Run 001 / readiness diagnostics |
| Interval estimand | `relative_att_post` (aligned paths only) | `recovery_intervals.py` |
| Harness | `run_production_nominal_calibration()` + `RecoveryRunner` | No estimator math changes |

Default multi-treated recovery DGP (Run 001 baseline):

- Scenarios: `recovery_null_effect`, `recovery_positive_effect`
- `missingness_policy=none`, `true_effect` ∈ {0.0, 0.10}
- Default panel: `n_geos=20` → **~4 treated units**, `pre_t=35`, `post=15`

---

### INV-008 — BRB operating characteristics (Run 002)

| Field | Specification |
|-------|----------------|
| **Configs** | `TBRRidge_BlockResidualBootstrap` only |
| **Scenarios** | `recovery_null_effect`, `recovery_positive_effect` (same as Run 001 for comparability) |
| **Seeds** | 0, 1, 2 (match Run 001); optional **supplementary** seeds 3–4 if seed instability flagged in primary run |
| **n_simulations** | **100** per config × scenario × seed |
| **Metrics** | coverage, FPR (null), power (positive), recovery_success_rate, failure_rate, failure_types; **interval width** (mean/std); **inverted-bound rate** (`ci_lower > ci_upper` or guard `PATH_INTERVAL_BOUNDS_INVERTED`); `interval_estimand`, `interval_aligned`, `eligible_for_nominal_calibration` |
| **Failure criteria (investigation)** | Any replication with inverted scalar CI; null FPR > 0.10 or coverage < 0.90; failure_rate ≥ 0.05; cross-seed std on FPR or coverage > **0.05** (`_STABILITY_STD_THRESHOLD`) |
| **Comparison baseline** | Run 001 BRB rows ([`CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md) §2) |
| **Primary archive** | `docs/CALIBRATION_RUN_002.md` |
| **Raw JSON (local, not committed)** | `.calibration_run_002.json` |
| **OC deep-dive archive** | `docs/PHASE12_INV008_BRB_OC_001.md` (width, seed stability, geometry notes) |
| **Failure analysis (if needed)** | `docs/CALIBRATION_FAILURE_ANALYSIS_002.md` |

**Pre-run checklist:** Confirm bound-ordering fix on `main`; confirm config still skipped in registry with `brb_bounds_inverted_run001` until Phase 13 decision; run harness **without** adding config back to `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` (harness may evaluate removed configs when explicitly requested — document invocation).

---

### INV-007 — KFold geometry matrix

| Field | Specification |
|-------|----------------|
| **Configs** | `TBRRidge_Kfold` |
| **Scenarios** | **A.** Default multi-treated: `recovery_null_effect`, `recovery_positive_effect` · **B.** Single-treated null/positive (documented variants; prototype params from `tests/test_recovery_inference_calibration.py`: `n_geos=12`, `treated_units=("geo_0",)`, `n_periods=40`, `treatment_start=28`, `true_effect` ∈ {0.0, 0.10}) · **C.** Optional sensitivity: single-treated with `n_geos` ∈ {12, 20} (donor-count sensitivity) |
| **Seeds** | 0, 1, 2 for production-tier cells; seed 0 only for exploratory sensitivity cells |
| **n_simulations** | **100** for A and B production cells; **25** for optional C sensitivity |
| **Metrics** | failure_rate, failure_types (expect `ValueError` on A); coverage, FPR, power when intervals align; `interval_estimand`, `interval_aligned`, `ineligible_reason`; pre-period / treated-count metadata |
| **Failure criteria (investigation)** | Multi-treated: document **100% failure** vs partial; single-treated: failure_rate ≥ 0.05 or null FPR/coverage threshold miss; any aligned run with inverted CI |
| **Primary archive** | `docs/PHASE12_INV007_KFOLD_GEOMETRY_001.md` |
| **Raw JSON (local, optional)** | `.phase12_inv007_kfold_geometry.json` |

**Do not** fix broadcasting or change inference code as part of this investigation artifact — characterize first; code changes are a **separate** decision after evidence.

---

### INV-003 — Multi-treated aggregation semantics

| Field | Specification |
|-------|----------------|
| **Configs** | `TBRRidge` (point), `TBRRidge_BlockResidualBootstrap` (where runs complete), `SCM_UnitJackKnife` (reference); not limited to TBRRidge |
| **Scenarios** | **Homogeneous:** default `recovery_*` · **Heterogeneous:** explicit `heterogeneous_effects=True` with documented per-unit effect spread (new scenario names documented in archive, e.g. `recovery_positive_heterogeneous`) · **Single-treated:** B from INV-007 |
| **Seeds** | 0–49 for aggregation statistics (matches failure-analysis diagnostic scale); primary tables on seeds 0, 1, 2 |
| **n_simulations** | **50** minimum for equivalence tables; **100** for primary homogeneous vs heterogeneous comparison cells |
| **Metrics** | `_path_relative_att` vs canonical `relative_att_post` (see `tests/test_estimand_metric_alignment.py`); absolute/relative error; bias direction under heterogeneity; interval width where available |
| **Failure criteria (investigation)** | Unbounded divergence without documented contract; ambiguous expert-review language if pooled score used as canonical ATT |
| **Primary archive** | `docs/PHASE12_INV003_AGGREGATION_SEMANTICS_001.md` |

**Output:** Estimand contract recommendation for recovery reporting and calibration scenarios — not a code change in Phase 12 plan execution unless separately approved.

---

### INV-017 — Calibration scaling and governance

| Field | Specification |
|-------|----------------|
| **Inputs** | Run 002 archive structure; Phase 11 template [`SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md); Run 001 threshold assessment |
| **Configs / scenarios** | N/A (meta-investigation) |
| **Seeds / n_simulations** | N/A — defines rules for INV-008/007/003 archives |
| **Metrics** | Archive completeness checklist; eligibility-evolution gate table; promotion-chain mapping |
| **Failure criteria (investigation)** | Missing metadata in any Phase 12 archive; eligibility change proposed without failure analysis + OC |
| **Primary archive** | `docs/PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md` |

**Deliverables:**

1. **Archive schema** — required fields: run ID, commit, branch, configs, scenarios, seeds, n_simulations, α, threshold assessment, raw JSON path, markdown summary path  
2. **Re-eligibility gate** — explicit checklist mapping to advancement policy steps 1–5  
3. **Smoke vs production tier tags** — runs with n < 100 labeled non-production (per `MIN_REPLICATIONS_FOR_STABLE_CALIBRATION`)  
4. **Trust-signal inputs (future)** — which OC fields may feed `CalibrationSignal` / `TrustReport` without implying certification

---

## 4. Acceptable outcomes

**All outcomes below are acceptable** if supported by archived evidence. None require estimator promotion.

| Track | Acceptable outcomes |
|-------|---------------------|
| **INV-008 (BRB)** | Re-enable for nominal null monitoring · **conditionally** re-enable (e.g. single-treated-only, null-only) · **keep excluded** with updated skip reason · **retire** from relative-ATT calibration path · open **inference redesign** investigation if bounds sane but OC still fails |
| **INV-007 (Kfold)** | **Restrict to single-treated-only** with documented scenario · fix deferred to future code PR after characterization · **retire from calibration** on multi-treated panels · permanently research-only |
| **INV-003 (aggregation)** | Document pooled `_path_relative_att` as scoring estimand only · add single-treated calibration scenario catalog · define alternate scoring path (future) · no change if divergence bounded and documented |
| **INV-017 (governance)** | Publish eligibility-evolution playbook · confirm no re-eligibility without Run 002-class archive · defer trust scores until Track B |

**Examples of successful Phase 12:**

- “BRB intervals valid after fix but FPR still > 0.10 → remain excluded.”
- “Kfold works single-treated only → permanent geometry contract.”
- “No TBRRidge inference config re-enters `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`.”

---

## 5. Non-goals

Phase 12 investigation execution **must not** include:

| Non-goal | Rationale |
|----------|-----------|
| Estimator or inference **code changes** (except already-merged BRB correctness fix) | Characterize before fix |
| **Eligibility registry** updates | Phase 13 governance decision only |
| **Threshold tuning** (coverage/FPR/power targets) | Run 001 policy frozen |
| **`production_safe` labels** or maturity promotion | Expert-review platform |
| **New inference methods** or modes | Scope creep |
| **Tuning DGP** (`true_effect`, noise) to pass calibration | Invalidates OC |
| **Artifact schema expansion** (cards, bundles v2) | Track B / deferred architecture |
| Package-wide **“nominal calibration achieved”** claims | Only SCM jackknife null monitoring evidenced today |

---

## 6. Evidence and artifact rules

Every investigation track **must** produce before closing:

| Requirement | Detail |
|-------------|--------|
| **Markdown archive in `docs/`** | Named per §3; committed after run completes |
| **Config / scenario / seed metadata** | Table in archive header (match Run 001 format) |
| **Threshold assessment** | Explicit pass/fail vs frozen thresholds; distinguish unavailable metrics |
| **Failure analysis** | Mechanism doc when any threshold fail or inverted CI (not threshold adjustment) |
| **Recommendation** | Per-config: exclude / conditional / monitor-only / research-only / redesign |
| **No silent eligibility change** | Registry changes only in Phase 13 PR with citations to archives |

**Raw JSON policy:** Large run payloads stay **local** (e.g. `.calibration_run_002.json`), same as Run 001. Markdown archives are the committed evidence surface.

**Investigation closure:** Update [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) entry status with link to archive — do not delete entries without resolution evidence.

---

## 7. Phase 13 decision criteria

Phase 13 is a **governance decision doc only** ([`ROADMAP_V4.md`](ROADMAP_V4.md) § Phase 13). It may be written only when:

### Required evidence (all must be present)

1. **INV-008 closed** — `CALIBRATION_RUN_002.md` + OC archive; comparison to Run 001; failure analysis if thresholds not met  
2. **INV-007 closed** — geometry matrix archive with multi-treated vs single-treated outcomes  
3. **INV-003 closed** — aggregation semantics contract (even if outcome is “document only”)  
4. **INV-017 closed** — governance playbook for archives and re-eligibility  

### Advancement policy chain (per config under consideration)

For any config proposed to move **toward** nominal eligibility or expanded expert-review support:

| Step | Evidence required |
|------|-------------------|
| 1. Estimand | Documented mapping to `relative_att_post` or declared alternate |
| 2. Recovery | Finite metrics or typed failures on standard battery |
| 3. Calibration | Null FPR/coverage (and power if claimed) at **n≥100**, archived |
| 4. Failure analysis | Root-cause doc if calibration fails or skip reason applies |
| 5. OC characterization | Width, geometry sensitivity, failure modes for reviewers |

**Phase 13 may record:** go / no-go / monitor-only / single-treated-only / research-only **per config** — without `production_safe`.

**Phase 13 may not:** auto-promote; relax thresholds; claim package-wide calibration.

---

## 8. Links to investigations

| Track | OPEN_INVESTIGATIONS ID | Backlog sections | Primary artifact(s) |
|-------|------------------------|------------------|---------------------|
| BRB OC after fix | **INV-008** | Inference concerns → TBRRidge BRB | `CALIBRATION_RUN_002.md`, `PHASE12_INV008_BRB_OC_001.md` |
| KFold geometry | **INV-007** | Inference concerns → TBRRidge Kfold | `PHASE12_INV007_KFOLD_GEOMETRY_001.md` |
| Multi-treated aggregation | **INV-003** | Medium → multi-treated DGP; heterogeneous vs pooled | `PHASE12_INV003_AGGREGATION_SEMANTICS_001.md` |
| Calibration governance | **INV-017** | DGP realism → calibration scaling; deferred architecture → TrustReport | `PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md` |

**Roadmap:** [`ROADMAP_V4.md`](ROADMAP_V4.md) § Phase 12 · **Validation paths:** [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) TBRRidge family · **Registry:** [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md) nominal calibration table

---

## Execution order (recommended)

| Order | Action | Track |
|-------|--------|-------|
| 1 | Draft INV-017 governance template (before runs) | INV-017 |
| 2 | Execute Run 002 / archive | INV-008 |
| 3 | Execute KFold geometry matrix | INV-007 |
| 4 | Execute aggregation semantics study | INV-003 |
| 5 | Finalize INV-017 playbook from actual archives | INV-017 |
| 6 | Phase 13 governance decision doc | Phase 13 |

---

*Governed investigation plan. Does not modify code, eligibility, thresholds, or maturity labels. Execute only after review of this plan; update plan if prerequisites or registry policy change.*
