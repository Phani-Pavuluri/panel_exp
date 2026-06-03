# D5-INST-TBR-001 — Class TBR aggregate two-series characterization

**Artifact:** [`archives/D5_INST_TBR_001_results.json`](archives/D5_INST_TBR_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inst_tbr_001.py`  
**Lane:** Research — no promotion, no CalibrationSignal ingress

**Prior:** [`D5_INST_AUDIT_001_REPORT.md`](D5_INST_AUDIT_001_REPORT.md) · [`D5_INST_COMBO_AUDIT_001_REPORT.md`](D5_INST_COMBO_AUDIT_001_REPORT.md) · [`AUDIT-010A_roadmap_consistency_pre_mmm_gate.md`](../audits/AUDIT-010A_roadmap_consistency_pre_mmm_gate.md)

---

## Summary

**Primary estimator:** class **`TBR`** (`panel_exp.methods.tbr.TBR`) — **not TBRRidge**.

**Geometry:** **aggregate two-series only** (1 treated row + 1 control row), built from flat geo assignment via sum aggregation ([`D5-POW-001c`](../../panel_exp/validation/track_d_d5_pow_001c.py) pattern).

**Overall verdict:** `remain_restricted_aggregate_diagnostic`

| Governance | Value |
|------------|-------|
| CalibrationSignal | **No** |
| MMM ingress | **No** |
| Unit-level TBR | **Blocked** (assert) |
| geo.relative_att_post default | **No** — aggregate level contrast only |
| AUDIT-010 prerequisites met | **No** |

---

## TBR call path (code-grounded)

| Requirement | Implementation |
|-------------|----------------|
| Treated rows | Exactly **1** (`len(treated_units) == 1`) |
| Control rows | Exactly **1** (`num_control_units == 1`) |
| Fit | `LinearRegression` on **pre-period** (default `full_model=False`) |
| Estimand | Post-window **aggregate** treated vs control contrast: mean\((y - \hat y)\) |
| **Not** | TBRRidge multi-control unit path · geo `PowerAnalysis` default (uses **TBRRidge**) |

---

## Callable inference modes (aggregate 1×1)

| Mode | Feasibility @ null | Null interval-exclusion FPR | Status |
|------|-------------------:|----------------------------:|--------|
| **point_estimate** | **100%** | n/a | **Callable** — primary aggregate readout |
| **Kfold** | **100%** | **0.0** | **Callable** — restricted diagnostic CI |
| **JKP** | **100%** | **1.0** | **Callable but unverified** — not governed (degenerate/null semantics on 1 control) |
| **UnitJackKnife** | **0%** | n/a | **Blocked** — `ValueError: requires at least 2 control units` |
| **Placebo** | **0%** | n/a | **Blocked** — interface excludes TBR class |

**Catalog note:** `method_metadata` lists JK on TBR, but **aggregate geometry cannot support LOO** with one control row.

---

## Single-cell aggregate results (n_mc=14, train=28, test=8)

| Metric @ null | TBR point | TBR Kfold |
|---------------|----------:|----------:|
| Mean point effect | ~−0.54 | ~−0.47 |
| Null FPR | n/a | **0.0** |
| Mean half-width | n/a | ~6.7 |

@ **8% injected aggregate contrast:**

| Metric | TBR point | TBR Kfold |
|--------|----------:|----------:|
| Mean point | ~39.7 | ~39.7 |
| Point / injected ratio | **~0.99** | **~0.99** |

**Scale interpretation:** Point tracks injected **aggregate level shift** (~percent × treated baseline mean) — **not** unit SCM+JK relative-att scale.

---

## Blocked geometries (explicit)

| Geometry | Status | Reason |
|----------|--------|--------|
| Unit panel (multi-control) | **Blocked** | `TBR.fit_data` assert |
| Placebo on agg2 | **Blocked** | TBR excluded from placebo-in-space |
| Pooled multi-cell aggregate | **Blocked** | No governed pooling rule |
| Multi-cell **per-cell** agg2 | **Feasible** (100% point) | Per-cell treated sum vs shared control only |

---

## Diagnostic context (not equivalence)

| Comparator | Geometry | Null mean point | Note |
|------------|----------|----------------:|------|
| SCM + JK | unit single-cell | ~−0.03 (typical) | Reference null-monitor — **different estimand/scale** |
| TBRRidge + Kfold | same agg2 panel | differs (~0.47× ratio mean) | **Conflation check** — PowerAnalysis path |
| AugSynthCVXPY point | unit (optional) | context only | Not aggregate TBR |

---

## Multi-cell k=2 (per-cell aggregate)

- **28** per-cell agg2 runs (14 reps × 2 cells): **100%** TBR point feasibility  
- **Policy:** per-cell only — no pooled cross-cell treated series  

---

## Before AUDIT-010 (remaining)

1. **AUDIT-010** MMM readiness/gap execution  
2. Track F **P0:** `recovery_runner` TBR→TBRRidge label (F-P0-002)  
3. Track F **P0:** `full_model` export guard (F-P0-001)  
4. Track B alias / instrument card for class TBR aggregate (if product needs one)  
5. JKP interval semantics on agg2 — **do not treat as governed** without fix/bridge  

---

## Stop-condition answer

**Class TBR supports aggregate 1×1** with **point** and **Kfold** as **restricted diagnostic** instruments. **JK** is **not supported** on this geometry. **JKP** runs but **interval semantics are not trustworthy** at null on this battery. **Unit, placebo, and pooled multi-cell paths are blocked.** This is **not** MMM-ready and **not** geo.relative_att_post by default.

**Next:** **AUDIT-010** (MMM readiness/gap).

---

**Rules acknowledged:** No production, estimator, inference, TrustReport, Track B, or MMM changes in this package.
