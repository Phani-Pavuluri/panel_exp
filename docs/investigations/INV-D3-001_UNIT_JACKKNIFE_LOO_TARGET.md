# INV-D3-001 — SCM Unit Jackknife LOO target mismatch

**Investigation ID:** INV-D3-001  
**Track:** D (research / robustness)  
**Status:** **fix accepted** — D5-INF-002b post-fix validation passed  
**Opened:** 2026-06-01  
**Fix applied:** `unit_jk` anchors on `results["y_hat"]` (shared primitive)  
**Source finding:** [D3-FIND-001](../TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md) §8  
**Pre-fix:** [D5_INF_002a_results.json](../track_d/archives/D5_INF_002a_results.json)  
**Post-fix:** [D5_INF_002b_results.json](../track_d/archives/D5_INF_002b_results.json)  
**Code:** `panel_exp/inference/unit_jackknife.py::unit_jk`  
**Tests:** `tests/test_unit_jackknife_loo_target.py` · `tests/track_d/test_d5_inf_002b_unit_jackknife_post_fix.py`

**Lane:** Governed fix in production inference primitive; **no** eligibility or lift-promotion changes.

---

## 1. Problem statement

Production `unit_jk` set the full-sample anchor to `results["y"]` while leave-one-out replicates used `results["y_hat"]`. Literature-aligned donor jackknife uses \((\hat\mu_{-i} - \hat\mu)^2\) on counterfactuals (equivalently \((\tau_{-i} - \tau)^2\) for \(\tau = Y - \hat\mu\)).

**Risk (pre-fix):** Treated post-outcome noise inflated jackknife width independent of donor uncertainty.

---

## 2. D5-INF-002a (pre-fix)

| Metric | Value |
|--------|-------|
| Post HW ratio (prod / ref) | mean **52.4** |
| Treated post noise Δ (production) | mean **3.02** |
| Recommendation | **open_inv_d3_001** |

---

## 3. Fix

**Change:** `mu = full_est.results["y_hat"]` in `unit_jk` (variation 1 and 2).

**Scope:** Shared inference primitive — all estimators using `UnitJackKnife` inherit the fix mechanically. **Governance** updated only for **SCM_UnitJackKnife** in this INV; AugSynth/TBR JK pairings require separate D5 characterization before any trust upgrade.

---

## 4. D5-INF-002b (post-fix, n=100)

| Metric | Value |
|--------|-------|
| Post HW ratio (prod / ref) | mean **1.0** |
| Post HW correlation | mean **1.0** |
| Treated post noise Δ (production) | mean **0** |
| Recommendation | **accepted_deviation** |
| **INV disposition** | **fix_accepted** |

---

## 5. Disposition

| Field | Value |
|-------|--------|
| **D3-FIND-001** | **fix_accepted** |
| **INF-002** | null_monitor_characterized |
| **SCM_UnitJackKnife** | **calibration_eligible / null_monitor_only** (unchanged) |
| **Calibration eligibility registry** | Unchanged |
| **Other JK instruments** | No trust upgrade |

---

*INV-D3-001 v1.1.0 — fix accepted — 2026-06-01*
