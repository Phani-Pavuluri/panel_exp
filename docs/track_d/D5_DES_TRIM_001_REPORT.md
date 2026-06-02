# D5-DES-TRIM-001 — Trimmedmatch separate-population characterization

**Artifact:** [`archives/D5_DES_TRIM_001_results.json`](archives/D5_DES_TRIM_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_des_trim_001.py`  
**Lane:** Research (no production, estimator, TrustReport, or MMM changes)

---

## Summary

`trimmedmatch` (`TrimmedMatchDesign`) is a **registered, geo-run-unsupported** design that selects **paired subsets** of markets using a **Tp/Te time split**, **Hungarian optimal pairing** on Tp, **distribution-based pair trimming**, and **within-pair rerandomization** into test vs control. Native power is **classical pair-lift confidence intervals on Te** — not SCM+JK or geo `PowerAnalysis`.

**Overall verdict:** `target_population_shift_severe` — Track E **GEO-004** stays **`characterization_required`** (`separate_population_design`).

---

## What trimmedmatch produces

| Stage | Behavior |
|-------|----------|
| **Input** | `PanelDataset` (markets × periods); optional spend panel |
| **Tp / Te** | `test_size` (default 0.3) → Te = last fraction; Tp = earlier periods for pairing |
| **Pairing** | `generate_optimal_pairs(Tp, num_pairs)` — distance or correlation Hungarian match |
| **Trim** | Remove pairs with extreme \|ΔTp total response\| (quantile tails, `trim_rate`) |
| **Assign** | Per trimmed pair: one geo → test group, other → control; 100 rerandomization iterations |
| **Power** | `power_analysis_with_cross_validation` — normal-approx CIs on pair lifts in Te |
| **Output** | `best_design` dict: `test_groups`, `control_group`, `geo_pairs`, imbalance score, `power` |

**Not produced:** `control` / `test_*` flat dict for `geo_runner`; full-universe assignment.

---

## Population / estimand (primary risk)

On the `scm_low_signal` battery:

- **Pair cap** (`num_pairs`) limits how many markets can enter pairing (≤ `2 × num_pairs`).
- **Trim** removes whole pairs → both markets leave the effective experiment.
- **Typical outcome:** majority of candidate markets **never paired** or **trimmed out**; retained share of Tp response mass ≪ 100%.

**Estimand:** Lift / power on the **retained trimmed-pair population** in Te — **not** `geo.relative_att_post` on the full eligible universe without an explicit **estimand bridge** (E-ESTIMAND-007).

**Governance:** Do **not** claim full-universe lift after trimming.

---

## Readout compatibility

| Path | Status |
|------|--------|
| SCM+JK @ full universe | **Blocked** |
| SCM+JK @ retained only | **Blocked** (pair geometry ≠ shared-donor SCM+JK) |
| TBRRidge unit panel | **Blocked** without bridge |
| Native pair power (Te) | **Diagnostic only** |
| D5-POW-001e | **Excluded** |

---

## Top findings

1. **D5-TRIM-FIND-001:** Severe **target-population shift** — trimming + pair cap exclude most markets.
2. **D5-TRIM-FIND-002:** Native **classical pair power** — not governed SCM+JK / geo PowerAnalysis.
3. **D5-TRIM-FIND-003:** **Pair-level** test/control lists — incompatible with tier-1 multi-cell donor geometry.

---

## Track E recommendation

Keep **GEO-004** at **`characterization_required`**. Native pair power may be cited as **diagnostic_only** only. No CalibrationSignal / MMM ingress without estimand bridge.

**Next:** D5-MCELL optimal-cell-count characterization.
