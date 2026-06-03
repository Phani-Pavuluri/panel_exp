# AUGSYNTH-ASCM-IMPLEMENTATION-FIDELITY-AUDIT-001

**Document ID:** AUGSYNTH-ASCM-IMPLEMENTATION-FIDELITY-AUDIT-001  
**Type:** Implementation fidelity audit — **docs + code inspection only**  
**Status:** **complete**  
**Date:** 2026-06-03  
**Verdict:** **`fidelity_confirmed_with_caveats`** — ASCM-003 may proceed as planned with documented caveats; no mandatory estimator fix before OC  
**Scope:** `AugSynthCVXPY` production comparator path only (charter §2.1)

**Primary inputs:** [`AUGSYNTH_ASCM_STRENGTHENING_001.md`](AUGSYNTH_ASCM_STRENGTHENING_001.md) §4 · [`track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md) · [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md) · [`panel_exp/methods/scm.py`](../panel_exp/methods/scm.py) · [`panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py`](../panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py)

**Related:** D5-DIAG-SCM-AUGSYNTH-001 — [`scm_augsynth_diagnostics.py`](../panel_exp/validation/scm_augsynth_diagnostics.py) · [`D5_DIAG_SCM_AUGSYNTH_001_REPORT.md`](track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md)

**Guardrails:** No estimator behavior change in this PR. No promotion, eligibility, inference, TrustReport/F-DECISION, CalibrationSignal/MMM, or LLM changes.

---

## 1. Audit purpose

Verify whether the **current** in-repo AugSynth/ASCM implementation matches the **intended** augmented-SCM behavior (Ben-Michael et al. family: SCM counterfactual + outcome-model correction on residuals) **before** running **D5-INST-AUGSYNTH-ASCM-003**.

This audit **does not** replace OC evidence. It closes charter §4 **I1–I8** inspection items and gates ASCM-003 planning.

---

## 2. Verdict summary

| Verdict code | Selected? | Meaning |
|--------------|-----------|---------|
| `fidelity_confirmed` | — | Implementation fully matches intended ASCM without material gaps |
| **`fidelity_confirmed_with_caveats`** | **✅** | Core two-step ASCM structure is implemented; documented gaps affect metadata, diagnostics comparability, and estimand reporting — **not** a blocker for stratified OC |
| `implementation_gap_found` | — | Material algorithm mismatch requiring fix before OC |
| `blocked_pending_implementation_fix` | — | OC must not run until implementation PR lands |

### Recommendation for ASCM-003

| Question | Answer |
|----------|--------|
| May ASCM-003 run as planned? | **Yes**, with caveats recorded in OC JSON metadata |
| Mandatory pre-OC implementation fix? | **No** — caveats are disclosure + diagnostic interpretation issues, not silent wrong algorithm |
| Optional follow-on fixes (separate PRs) | Align D1 SCM diagnostic leg with `SyntheticControlCVXPY`; archive ridge-λ sensitivity (D8); document level vs relative estimand in reports |

---

## 3. Implementation map

| Layer | Class / path | Role in repo |
|-------|--------------|--------------|
| **Production comparator** | `AugSynthCVXPY` · `panel_exp/methods/scm.py` | Track D ASCM-002/003 batteries, Track B `AugSynthCVXPY_Point`, F-DECISION diagnostic comparator |
| **Inner SCM leg** | `SyntheticControlCVXPY` (OSQP QP) | Donor weighting; non-neg + sum-to-one per treated unit |
| **Outcome leg** | `sklearn.linear_model.Ridge` (default) | Fit on donor pre-period features × SCM residuals |
| **Probe only** | `AugSynth` (non-CVXPY wrapper) | D5-INST-AUGSYNTH-001 probe; **not** ASCM-002 primary arm |
| **Legacy SCM** | `SyntheticControl` (SciPy SLSQP) | A26 baseline; **also used for D1 `scm_pre_rmse` in ASCM-002 diagnostics** (see gap G4) |

---

## 4. Audit questions (15)

### Q1. What exact estimator class/function is “AugSynth/ASCM”?

**Answer:** **`AugSynthCVXPY`** in [`panel_exp/methods/scm.py`](../panel_exp/methods/scm.py) (lines 419–530). Validation harnesses instantiate:

```python
AugSynthCVXPY(inference=..., alpha=..., min_donors=..., donor_correlation_threshold=..., lambda_reg=...)
```

Registry: `method_metadata.py` → `AugSynthCVXPY`, maturity `EXPERT_REVIEW`. Base `AugSynth` is **`UNVALIDATED`** and excluded from ASCM charter OC arms.

---

### Q2. What optimization objective is implemented?

**Answer:** Two-stage — no single joint objective.

| Stage | Objective |
|-------|-----------|
| **Inner SCM** (`SyntheticControlCVXPY.fit_model`) | QP: minimize \(\|C w - y\|^2 + \lambda_{reg}\|w\|^2\) subject to \(w \ge 0\), \(\sum w = 1\) per treated unit (OSQP) |
| **Outcome model** | Ridge regression: minimize \(\|X \beta - r\|^2 + \alpha_{ridge}\|\beta\|^2\) on SCM residuals \(r\) |

Combined prediction: \(\hat{y}_t = C_t w + X_t \beta\) (see `Model.predict` in `AugSynthCVXPY.fit_model`).

**Caveat (G1):** Constructor `penalty` / `penalty_strength` are **stored** on `SyntheticControlCVXPY` but **not applied** in the OSQP solve (docstring lines 244–247). Only `lambda_reg` affects the inner objective.

---

### Q3. What loss function is used?

**Answer:**

- SCM leg: **squared error** (L2) between treated path and donor-weighted synthetic control.
- Outcome leg: **Ridge (L2)** loss on residualized outcomes via sklearn `Ridge` default.

No entropy/L1 penalty is active on the production OSQP path despite default `penalty="entropy"` in constructor.

---

### Q4. What regularization or penalty is used?

**Answer:**

| Parameter | Default | Applied? |
|-----------|---------|----------|
| `lambda_reg` (SCM weights) | `0.0` | **Yes** — adds \(\lambda I\) to QP Hessian when > 0 |
| `Ridge.alpha` (outcome model) | `1.0` (sklearn default unless `model_args`) | **Yes** |
| `penalty` / `penalty_strength` | `"entropy"` / `0.01` | **No** on OSQP path (API compatibility only) |

Batteries use defaults unless overridden. **D8 ridge sensitivity grid is not implemented** in estimator or OC harness (gap G5).

---

### Q5. Are donor weights constrained? If yes, how?

**Answer:** **Yes** — per treated unit on the filtered donor set:

- **Non-negativity:** \(w_j \ge 0\) (OSQP bounds; post-solve clip)
- **Simplex:** \(\sum_j w_j = 1\) (equality constraint)
- **Donor pool:** optional correlation pre-filter (`donor_correlation_threshold`, `min_donors` fallback to top-\(k\) donors)

Weights are mapped back to full control index space (`weights_full`); filtered-out donors receive weight 0.

---

### Q6. Are negative weights allowed?

**Answer:** **No** on the production `SyntheticControlCVXPY` path. Weights are clipped to \(\ge 0\) after solve. `n_negative_weights` in diagnostics should be **0** for feasible AugSynth runs (ASCM-002 sample: all 0).

Legacy `SyntheticControl` (SciPy) uses `[0,1]` bounds — also non-negative.

---

### Q7. Are weights normalized to sum to one?

**Answer:** **Yes** — explicit renormalization after OSQP (`w_j / w_sum`) per treated column. [`tests/test_scm.py`](../tests/test_scm.py) asserts `abs(w.sum() - 1.0) < 1e-4`.

---

### Q8. How are treated units handled?

**Answer:**

- `PanelDataset.treated_units` + `treated_periods` define treatment window.
- `split_control_test_units` returns control wide matrix and treated matrix (all listed treated units).
- Inner SCM solves **one weight vector per treated column** (`weights` shape `(n_ctrl, n_treated)`).
- Ridge fits **multi-output** residuals `(T_pre, n_treated)` against donor features `(T_pre, n_ctrl)`.
- Post-period counterfactual uses full `predict` on all periods.

**Single-treated** is the primary governed geometry. Multi-treated is supported in code but OC readout collapses to scalar `mean_point_effect` via temporal (and unit) averaging in `_post_window_arrays`.

---

### Q9. How are donor units selected/excluded?

**Answer:**

1. All `panel.control_units` are candidates.
2. If `donor_correlation_threshold > 0`: keep donors with pre-period correlation to treated (or treated mean profile if `full_model`) ≥ threshold.
3. If fewer than `min_donors` pass: keep top `min_donors` by correlation (warning).
4. Metadata: `_donor_correlations`, `_kept_donor_indices`, `_n_donors_filtered` exposed on inner SCM and forwarded to `AugSynthCVXPY`.

Default batteries: `donor_correlation_threshold=0.0` (no filter), `min_donors=5` (feasibility gate only).

---

### Q10. How is multi-treated behavior handled?

**Answer:**

| Context | Behavior |
|---------|----------|
| **`AugSynthCVXPY.fit_model`** | Separate SCM weights per treated unit; joint Ridge on all treated residual columns |
| **ASCM-002 W11** | Multi-treated unit panel world; per-unit assignment (no aggregation) |
| **`check_AugSynthCVXPY_weight_health`** | **Aggregates** treated units to `__treated__` before fit — **different** from raw multi-treated OC path (gap G6) |
| **Aggregate JK / pooled estimand** | **Not supported** — F-GEO blocks flat SCM+JK on multi-treated |

Multi-treated OC is **exploratory**; promotion claims remain single-treated only.

---

### Q11. What estimand is emitted?

**Answer:** **Two reporting surfaces — not equivalent**

| Surface | Definition |
|---------|------------|
| **`ImpactAnalyzer.summary()`** | Post-period **relative** effect: `rel_effect_mean = mean(y - ŷ) / mean(ŷ) × 100` |
| **Track D readout** (`_readout_metrics`) | Post-window **level** mean: `mean_point_effect = mean(y - ŷ)` over last `test_length` periods (units averaged if 2D) |

ASCM-002 recovery metrics (`effect_recovery_mae`, null FPR) use **level** `mean_point_effect`, compared to injected **percent** effect — scale bridge documented (D5-AS-FIND-004, gap G7).

A26 SCM+JK uses the same readout helper family but estimand semantics differ from AugSynth point path at null (100% material mismatch in ASCM-002).

---

### Q12. What metadata is emitted?

**Answer:**

| Source | Fields |
|--------|--------|
| **Estimator instance** (post-fit) | `_donor_correlations`, `_kept_donor_indices`, `_n_donors_filtered`, `_lambda_reg_used`; inner `scm.model.weights`; `outcome_model.coef_`, `.alpha` |
| **ASCM-002 JSON (inline diagnostics)** | D1–D7: `scm_pre_rmse`, `augsynth_pre_rmse`, `fit_improvement_rmse`, `donor_sparsity_n_control`, `weight_herfindahl`, `max_weight`, `n_negative_weights`, `hull_min_donor_z_distance`, `diagnostics_feasible`, `blocked_reason` |
| **D5-DIAG module** | Adds normalized RMSE, scale bridge, outcome-model descriptors, instrument flags via [`scm_augsynth_diagnostics.py`](../panel_exp/validation/scm_augsynth_diagnostics.py) |
| **Production TrustReport / Track B export** | Maturity metadata via `estimator_metadata`; **no** automatic export of weight vector or hull labels to product |

---

### Q13. Are diagnostic weights available to D5-DIAG?

**Answer:** **Partial — yes with access pattern caveats**

- Weights accessible via `aug.scm.model.weights` after `run_analysis` (see `_weight_diagnostics` in ASCM-002 harness).
- D5-DIAG helper `_extract_scm_weights` uses same path.
- **Not serialized** as full vector in OC JSON — only concentration scalars (Herfindahl, max weight, effective donor count on D5-DIAG branch).
- Blocked / infeasible runs → `NaN` weight fields + `diagnostics_feasible=0`.

---

### Q14. Does the implementation support inside-hull / outside-hull diagnostics?

**Answer:** **Proxy only — not convex-hull membership**

- Harness computes `hull_min_donor_z_distance`: minimum L2 distance between **z-scored** treated pre-profile and each donor pre-profile (ASCM-002 `_hull_extrapolation_z`).
- World labels (`W2` inside, `W3` outside) are **DGP/design tags**, not derived from hull test.
- Threshold audit uses distance percentiles provisionally — ASCM-002 showed **non-monotonic** RMSE vs world label at n_mc=4.
- **Supported for OC stratification** as stress proxy; **not** a certified extrapolation detector.

---

### Q15. Behavior gaps vs intended AugSynth/ASCM?

**Answer:** See gap register §5. Core ASCM **structure matches** (SCM + ridge on residuals). Material gaps are **interpretation, diagnostic alignment, and metadata completeness** — not a missing augmentation step.

---

## 5. Gap register

| ID | Gap | Severity | Blocks ASCM-003? | Remediation |
|----|-----|----------|------------------|-------------|
| **G1** | `penalty` / `penalty_strength` unused on OSQP SCM leg | Low | No | Document in metadata; optional rename in future API cleanup PR |
| **G2** | Class name `*CVXPY` but solve uses OSQP directly | Low | No | Doc-only; historical naming |
| **G3** | `full_model=True` post-fit leakage risk (INV-D2-001) | Medium (governance) | No for default OC | Remains blocked for export; not default in batteries |
| **G4** | D1 `scm_pre_rmse` uses **`SyntheticControl` (SciPy)** while AugSynth inner leg is **`SyntheticControlCVXPY`** | **Medium** | No — disclose in ASCM-003 | Optional harness fix: use CVXPY SCM for D1 baseline |
| **G5** | D8 outcome-model ridge sensitivity grid not implemented | Medium | No | ASCM-003 optional grid; not estimator change |
| **G6** | `check_AugSynthCVXPY_weight_health` aggregates multi-treated; OC W11 does not | Low | No | Document; keep worlds separate |
| **G7** | Level vs relative estimand split (`summary` vs readout) | **Medium** | No — already flagged | Estimand bridge ADR (post ASCM-003) |
| **G8** | Hull diagnostic is z-distance proxy, not convex hull | Medium | No | Threshold calibration in ASCM-003 |
| **G9** | D8/D10/D11 incomplete on `main` inline harness | Medium | No if D5-DIAG merged first | Merge D5-DIAG before ASCM-003 execution |

---

## 6. Charter §4 checklist closure

| ID | Item | Audit result |
|----|------|--------------|
| I1 | Objective / loss | **Pass with G1** — two-stage L2 + Ridge documented |
| I2 | Constraints | **Pass** — simplex + optional correlation filter |
| I3 | Regularization | **Pass with G5** — defaults recorded; sensitivity grid open |
| I4 | Donor weights export | **Partial** — scalars in OC; full vector not archived |
| I5 | Outcome-model component | **Pass** — residual ridge + combined predict |
| I6 | Treated/control geometry | **Pass** — unit panel; aggregate paths blocked |
| I7 | Point estimand | **Pass with G7** — level readout documented vs A26 |
| I8 | Metadata emitted | **Partial** — D1–D7 yes; D8/D10/D11 via D5-DIAG branch |
| I9 | Unsupported modes | **Pass** — blocked per F-CAT / AUDIT-010 |

---

## 7. ASCM-003 gate

| Criterion | Status |
|-----------|--------|
| Fidelity audit complete | ✅ this document |
| Verdict allows OC | ✅ `fidelity_confirmed_with_caveats` |
| D5-DIAG diagnostics available | ✅ merged — [`scm_augsynth_diagnostics.py`](../panel_exp/validation/scm_augsynth_diagnostics.py) |
| Implementation fix required first | ❌ no mandatory fix |
| Promotion / eligibility change | ❌ none |

**Next artifact:** **D5-INST-AUGSYNTH-ASCM-003** — stratified OC with caveats G4/G7/G8 recorded in report limitations.

---

## 8. Guardrails (confirmed)

| Guardrail | Status |
|-----------|--------|
| No silent estimator behavior change | ✅ |
| No threshold finalization | ✅ |
| No promotion / demotion | ✅ |
| No eligibility change | ✅ |
| No inference behavior change | ✅ |
| No TrustReport / F-DECISION change | ✅ |
| No CalibrationSignal / MMM change | ✅ |
| No LLM integration | ✅ |

---

*AUGSYNTH-ASCM-IMPLEMENTATION-FIDELITY-AUDIT-001 v1.0.0 — verdict `fidelity_confirmed_with_caveats`; ASCM-003 cleared with caveats.*
