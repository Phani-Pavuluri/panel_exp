# Track D D2 — Estimator and SCM donor matching audit 001

**Document ID:** TRACK-D-D2-ESTIMATOR-DONOR-001  
**Type:** Research-lane audit / ADR  
**Status:** **complete (D2 package v1)** — findings are **not** production-promotion evidence  
**Date:** 2026-05-28  
**Branch / baseline:** `fix-kfold-multitreated-geometry` @ `1a31e69` (post INV-D1-001 fix + D5-DES-001a rerun)  
**Lane:** **Research / robustness** per [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) § Track D  

**Authoritative inputs:**

| Document | Role |
|----------|------|
| [`TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md`](TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md) | Design layer closed (`61a174f`) |
| [`investigations/INV-D1-001_PRE_PERIOD_MATCHING_LEAKAGE.md`](investigations/INV-D1-001_PRE_PERIOD_MATCHING_LEAKAGE.md) | P0 design boundary |
| [`track_d/archives/D5_DES_001a_results.json`](track_d/archives/D5_DES_001a_results.json) | Design OC baseline |
| [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) | EST-*, MAT-*, INF-* rows |
| [`TRACK_D_LITERATURE_CROSSCHECK_001.md`](TRACK_D_LITERATURE_CROSSCHECK_001.md) | §3.1 SCM, §3.2 AugSynth |
| [`TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`](TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md) | Instrument IDs |
| [`audits/AUDIT-004_m2_2_trust_report_gate.md`](audits/AUDIT-004_m2_2_trust_report_gate.md) | Track B boundary intact |

**Code authority (read-only review):** `panel_exp/methods/scm.py` · `panel_exp/methods/synthetic_control.py` · `panel_exp/panel_data.py` · `panel_exp/impact.py` · `panel_exp/method_metadata.py` · `panel_exp/validation/nominal_calibration.py`

---

## ADR decision record

| Field | Value |
|-------|--------|
| **Context** | D1/INV-D1-001 closed design-period leakage on geo assignment. Estimator and donor-pool math can now be audited without conflating design look-ahead with SCM weight fitting. |
| **Decision** | Document D2 research-lane audit; **no** estimator/inference code changes in this package. Suspected bugs → finding register with proposed INV/DEF + separate governed fix PRs. |
| **Consequences** | MAT-004/005 and SCM estimators receive explicit robustness statuses; D3 owns inference-only rows; D5 OC specs added. |
| **Alternatives rejected** | Inline code fixes during D2 (forbidden); promoting SCM JK because design is fixed (forbidden). |

---

## 1. Executive summary

D2 prioritized **SCM estimator family** and **donor-pool construction (MAT-004, MAT-005)** with **estimator vs inference separation**.

**Headline:** Default geo SCM path (`SyntheticControlCVXPY`, `full_model=False`, pre-period `split_control_test_units`) is **structurally aligned** with literature for donor simplex fitting and treated-unit exclusion. **High-risk deviation:** any `full_model=True` path fits weights on **post-treatment columns** while correlation filtering may still use pre-period only — parallel to pre-D1 design leakage at the **estimator** layer.

**Overall D2 verdict (research lane):** `continue_with_characterization_required`

| Area | Verdict |
|------|---------|
| Donor pool excludes treated units | **Pass** (`control_series` drops treated rows) |
| Default pre-period SCM fit | **Pass with monitoring** |
| `full_model=True` SCM / AugSynth paths | **Fail-risk** → proposed INV-D2-001 |
| Estimator vs inference separation | **Pass** (registry + `ImpactAnalyzer.run_analysis`) |
| Track B instrument mapping | **Pass** (config_alias → catalog IDs unchanged) |
| CalibrationSignal eligibility | **Unchanged** — SCM JK null-monitor only; D2 does not expand eligibility |

---

## 2. Scope and non-goals

### In scope (D2)

| ID | Item |
|----|------|
| **EST-001** | `SyntheticControl` (scipy SLSQP) |
| **EST-002** | `SyntheticControlCVXPY` (OSQP simplex) |
| **EST-003** | `AugSynth` |
| **EST-004** | `AugSynthCVXPY` |
| **MAT-004** | Donor pool construction (panel split) |
| **MAT-005** | SCM CVXPY weights + constraints |
| **INF-001, INF-002, INF-006** | Separation review only (D3 deep dive) |

### Light touch (inventory only, D3/D2b)

EST-005–007 (TBR family), EST-010 (DID), EST-011+ blocked estimators — row status unchanged except cross-reference.

### Out of scope (explicit)

| Exclusion | Owner |
|-----------|--------|
| Code changes to estimators/inference | Separate governed PR per finding |
| Design assignment (DES-001) | D1 ✅ |
| TrustReport / Track B contracts | Track B |
| Eligibility / maturity / release gates | Governance milestones |
| MMM / planning feed | Forbidden |
| Production promotion | D7 + OC bridge |

---

## 3. Estimator inventory reviewed

| Est ID | Class | D2 depth | Pre-fit window (default) | Donor constraints | **Post-D2 status** |
|--------|-------|----------|--------------------------|-------------------|---------------------|
| **EST-001** | `SyntheticControl` | Full | `period='pre'` (default split) | Simplex [0,1], sum=1 | **restricted** |
| **EST-002** | `SyntheticControlCVXPY` | Full | Pre-period `C`,`Y` | Non-neg, sum=1; optional corr filter | **characterization_required** |
| **EST-003** | `AugSynth` | Medium | SCM inner + ridge aug | Inherits SCM risks | **blocked** (unvalidated) |
| **EST-004** | `AugSynthCVXPY` | Medium | Via inner CVXPY SCM | Same as EST-002 + aug layer | **restricted** |
| **EST-005** | `TBR` | Skim | Pre (`full_model=False`) | Regression donors | unreviewed → D2b |
| **EST-006** | `TBRRidge` | Skim | Pre default | Ridge on controls | See D3/D2b (INF-004/005) |

| Match ID | D2 depth | **Post-D2 status** |
|----------|----------|---------------------|
| **MAT-004** | Full | **characterization_required** |
| **MAT-005** | Full | **characterization_required** |

---

## 4. SCM donor-pool and matching audit (MAT-004 / MAT-005)

### 4.1 Donor pool construction (MAT-004)

**Mechanism:** `PanelDataset.control_series` → `wide_data.drop(treated_units, axis=0)` then optional `period='pre'|'post'|'full'`.

| Check | Status | Evidence |
|-------|--------|----------|
| Treated units excluded from donor pool | **pass** | `panel_data.py` `control_series` L533 |
| Pre-period slice for fit | **pass** | `split_control_test_units(..., period='pre')` default |
| Multi-treated aggregation | **partial** | `aggregation_fun` on control when multiple treated — geometry assumption for pooled SCM |
| Staggered treatment starts | **warn** | Requires equal `treatment_start_index` across treated for pre slice |

**Causal read:** Donor pool is **not** the design-assignment matcher (D1); it is **analysis-time** controls only. With INV-D1-001 fix, design assignment is pre-period; SCM donors still must not include treated units — **satisfied**.

### 4.2 SCM weight fitting (MAT-005 / `SyntheticControlCVXPY`)

**Default path (`full_model=False`):**

1. `control, test = split_control_test_units(..., period='pre')` → `C` is (T_pre × n_ctrl), `Y` is (n_treated × T_pre).
2. Optional donor correlation filter uses `C_pre` and mean treated pre profile (`scm.py` L305–320).
3. QP: minimize ‖C w − y‖² s.t. w ≥ 0, Σw = 1 on **pre-period columns only**.

| Check | Status |
|-------|--------|
| Non-negative weights | **pass** |
| Weights sum to 1 per treated unit | **pass** |
| Pre-period fit only (default) | **pass** |
| Post-period not in weight objective (default) | **pass** |

**`full_model=True` path (AugSynth inner, optional configs):**

| Check | Status |
|-------|--------|
| `C` includes post-period columns | **fail-risk** |
| Correlation filter still pre-only | **partial** (filter pre, fit post) |
| Literature: weights from pre-treatment fit only | **violated** when full_model |

**Finding:** **D2-FIND-001** — document as proposed **INV-D2-001** (separate fix PR). Do not enable `full_model=True` for geo decision workflows until resolved.

### 4.3 Legacy `SyntheticControl` (EST-001 / scipy)

| Check | Status |
|-------|--------|
| Pre-period default split | **pass** |
| Optimizer stability | **fail-risk** (metadata: "optimizer sensitivity") |
| Donor correlation filter | **absent** |
| Entropy/l1 penalties | **present** |

**Status:** **restricted** — prefer `SyntheticControlCVXPY` for geo.

---

## 5. Estimator vs inference separation

| Layer | Responsibility | SCM example |
|-------|----------------|-------------|
| **Estimator** | Counterfactual weights / point effect | `fit_model`, weights simplex |
| **Inference** | Uncertainty / null distribution | `UnitJackKnife`, `Placebo` via `get_inference_registry().run` |
| **ImpactAnalyzer** | Orchestration | `run_analysis` → inference registry |

| Check | Status | Notes |
|-------|--------|-------|
| Intervals not produced inside `fit_model` | **pass** | Intervals from inference modes |
| Placebo not labeled as CI | **pass** | Track B `interval_semantics=placebo_band` (GOLD-005) |
| Config maps to one instrument | **pass** | `SCM_UnitJackKnife`, `SCM_Placebo` distinct |
| Maturity ≠ robustness | **pass** | `method_metadata` vs matrix status |

**D3** owns deep review of **INF-002** (JK FPR/power) and **INF-006** (placebo). D2 confirms **no estimator-layer bleed** of interval logic.

---

## 6. Track B instrument compatibility

| Config / instrument | Estimator | Inference | D2 compatibility |
|---------------------|-----------|-----------|------------------|
| `SCM_UnitJackKnife` | `SyntheticControlCVXPY` (typical) | `UnitJackKnife` | **aligned** if pre-fit only |
| `SCM_Placebo` | SCM family | `Placebo` | **aligned**; diagnostic only |
| `AugSynthCVXPY_Point` | AugSynthCVXPY | point | **restricted** (point + aug) |

**Adapter:** Track B maps `config_alias` only; D2 does **not** change adapter rules. If `full_model` is used in production export metadata without disclosure, adapter may still show `complete` — **governance gap** for evidence metadata, not adapter math.

**TrustReport:** Unchanged. Lift claims for SCM JK remain **inconclusive** per GOLD-001 / calibration boundary.

---

## 7. CalibrationSignal eligibility (governance only)

| Question | D2 answer |
|----------|-----------|
| Does SCM math justify expanding eligibility? | **No** |
| Current eligible config | `SCM_UnitJackKnife` only (`nominal_calibration.py`) |
| Rationale | Null-monitor FPR characterization; zero power on positive battery (DEF-013) |
| D2 impact | **No change** to `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` |

D2 confirms: eligibility is a **governance** label, not proven by estimator correctness alone.

---

## 8. Correctness checklists (literature-aligned)

### 8.1 SCM core (D0b §3.1)

| Audit check | EST-002 default | EST-002 full_model | EST-001 |
|-------------|-----------------|---------------------|---------|
| Donor-only controls | pass | pass | pass |
| Non-negative weights | pass | pass | pass |
| Sum-to-one | pass | pass | pass |
| Pre-period fit | pass | **fail** | pass |
| Post excluded from fit | pass | **fail** | pass |
| Treated not in donor pool | pass | pass | pass |
| Placebo ≠ CI | N/A (D3) | N/A | N/A |

### 8.2 Augmented SCM (D0b §3.2)

| Audit check | EST-004 |
|-------------|---------|
| SCM vs outcome model separated | partial (ridge on residuals) |
| Poor pre-fit documented | warn |
| Point-only bounded | pass when point inference |

---

## 9. Literature grounding requirements (D0b backlog)

| Inventory ID | Required D0b action | Target decision |
|--------------|---------------------|-----------------|
| EST-002 (default) | Complete §3.1 YAML | `needs_characterization` → `aligned_with_deviation` after D5 |
| EST-002 (`full_model`) | Document deviation “post in fit” | `aligned_with_deviation` until INV-D2-001 fixed |
| MAT-004 | Donor pool record | `aligned` |
| MAT-005 | Same as EST-002 | coupled |
| EST-001 | §3.1 + scipy fragility | `restricted` |
| EST-003/004 | §3.2 AugSynth | `restricted` / `blocked` |

---

## 10. Finding register (governance)

| Finding ID | Summary | Severity | Disposition | Fix track |
|------------|---------|----------|-------------|-----------|
| **D2-FIND-001** | `full_model=True` fits SCM weights on post-period `C` while corr filter may use pre-only | **high** | **investigating** → propose **INV-D2-001** | Separate PR: slice `C` to pre in QP |
| **D2-FIND-002** | Legacy `SyntheticControl` scipy path unstable; no donor filter | medium | **restricted** | Prefer CVXPY; optional DEPR |
| **D2-FIND-003** | `AugSynth` maturity UNVALIDATED; aug layer not OC'd | medium | **blocked** | D5 AugSynth slice |
| **D2-FIND-004** | Multi-treated SCM uses mean pre profile for correlation filter | low | **accepted_deviation** | Document geometry scope |
| **D2-FIND-005** | Weight concentration / min donors fallback forces top-k donors | low | **characterization_required** | D5 donor concentration metrics |
| **D2-FIND-006** | Evidence metadata does not surface `full_model` flag to Track B | medium | **deferred** | Export/metadata follow-up |

**Promotion rule:** None of the above may advance to `decision_eligible` without D5 OC + D3 inference audit + D7 bridge.

### Proposed INV-D2-001 (not implemented in D2)

**Title:** SCM `full_model` post-period weight leakage  
**Scope:** `SyntheticControlCVXPY.fit_model` — use `C_pre` for QP when `full_model` and `treated_start_idxs` available; mirror correlation logic.  
**Pattern:** Same as INV-D1-001: characterize → governed fix → D5 rerun.

---

## 11. Required D5 / OC simulations (specified, not run)

| Sim ID | Target | Purpose |
|--------|--------|---------|
| **D5-MAT-004a** | Donor pool | Assert zero weight on treated indices if mistakenly included |
| **D5-EST-002a** | CVXPY SCM | `full_model=False`: weights identical when post columns perturbed |
| **D5-EST-002b** | CVXPY SCM | `full_model=True` vs pre-only: quantify ATT bias (baseline before INV-D2-001 fix) |
| **D5-EST-002c** | CVXPY SCM | Weight sum-to-one, non-negativity, max weight concentration |
| **D5-EST-004a** | AugSynthCVXPY | Augmentation does not invert ATT sign under null DGP |

Archive under `docs/track_d/archives/` when executed.

---

## 12. Matrix updates (D2)

Applied in [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) §7–§6:

| Row | Prior | Post-D2 |
|-----|-------|---------|
| EST-001 | restricted | **restricted** (confirmed) |
| EST-002 | math_review_required | **characterization_required** |
| EST-003 | unreviewed | **blocked** |
| EST-004 | restricted | **restricted** (confirmed) |
| MAT-004 | characterization_required | **characterization_required** (donor exclusion verified) |
| MAT-005 | characterization_required | **characterization_required** (default path verified) |

---

## 13. Recommended next actions

| Priority | Action | Lane |
|----------|--------|------|
| P0 | Open **INV-D2-001** for `full_model` SCM QP period boundary | Research → governed fix |
| P1 | Run **D5-EST-002a** (post perturbation invariant) on default geo configs | D5 |
| P1 | **D3** inference audit (INF-002, INF-006, INF-004/005) | Research |
| P2 | Complete D0b YAML for EST-002 / MAT-005 | D0b |
| P2 | D2b skim TBR estimators (EST-005/006) | Research |
| — | **Do not** expand CalibrationSignal eligibility from D2 | Governance |

---

## 14. Checkpoint vs D1

| Gate | D1 | D2 |
|------|----|----|
| Design-period leakage | Closed (`61a174f`) | N/A |
| Estimator pre-fit | — | Default SCM **OK** |
| Donor pool | — | Treated excluded **OK** |
| D2 safe to proceed | Blocked | **D3** and targeted D5 allowed |
| Production promotion | No | **No** |

---

## 15. Sign-off

| Role | Statement |
|------|-----------|
| **D2 audit** | Package complete; research-lane only |
| **Code changes** | None in this commit |
| **Track B** | Unchanged |
| **CalibrationSignal** | Unchanged |

---

*TRACK-D-D2-ESTIMATOR-DONOR-001 v1.0.0 — research lane — 2026-05-28*
