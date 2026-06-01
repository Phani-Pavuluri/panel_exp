# INV-D3-001 — SCM Unit Jackknife LOO target mismatch

**Investigation ID:** INV-D3-001  
**Track:** D (research / robustness)  
**Status:** **open** — D5-INF-002a recommends governed fix (no fix in characterization PR)  
**Opened:** 2026-06-01  
**Source finding:** [D3-FIND-001](../TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md) §8  
**Characterization:** [D5_INF_002a_results.json](../track_d/archives/D5_INF_002a_results.json)  
**Code (production):** `panel_exp/inference/unit_jackknife.py::unit_jk`  
**Research harness:** `panel_exp/validation/track_d_d5_inf_002a.py` · `tests/track_d/test_d5_inf_002a_unit_jackknife.py`

**Lane:** Research only until governed fix PR — **no** silent inference changes.

---

## 1. Problem statement

Production `unit_jk` sets the full-sample anchor to `results["y"]` (observed treated outcomes) but each leave-one-out replicate to `results["y_hat"]` (counterfactual). Literature-aligned donor jackknife for SCM uses \(\tau = Y - \hat\mu\) and \((\tau_{-i} - \tau)^2\), equivalently \((\hat\mu_{-i} - \hat\mu)^2\) on the counterfactual path.

**Risk:** Post-period treated outcome noise inflates jackknife width even when pre-fit counterfactuals are stable — undermines interpretation of `SCM_UnitJackKnife` as a null monitor tied to donor uncertainty rather than observed outcome volatility.

**Governance:** `SCM_UnitJackKnife` remains **`null_monitor_only`** and the sole `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` member until this INV closes with a fix + D5 re-run. **No lift-detection promotion.**

---

## 2. D5-INF-002a summary (n=100 replicates)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Post HW ratio (prod / ref) | mean **52.4** | Production widths much larger than literature reference |
| Post HW correlation | mean **~0** | Paths uncorrelated on treated window |
| Treated post noise Δ (production) | mean rel change **3.02** | Large sensitivity |
| Treated post noise Δ (reference) | mean **0** | Stable when only `y` noised (`y_hat` unchanged) |
| **Recommendation** | **open_inv_d3_001** | Governed fix required |

---

## 3. Proposed fix (separate PR)

1. In `unit_jk`, set full-sample anchor `mu = results["y_hat"]` (or explicit \(\tau\) on effect scale per literature).  
2. Add regression test: treated post outcome perturbation does not change post JK width when weights/counterfactuals fixed.  
3. Re-run nominal null battery / archive D5-INF-002b post-fix.  
4. Update disposition only after OC — do not expand calibration eligibility from fix alone.

---

## 4. Disposition

| Field | Value |
|-------|--------|
| **D3-FIND-001** | **open_inv_d3_001** |
| **INF-002** | null_monitor_characterized — fix pending |
| **Calibration eligibility** | Unchanged |

---

*INV-D3-001 v1.0.0 — research lane — 2026-06-01*
