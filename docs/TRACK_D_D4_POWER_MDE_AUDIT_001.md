# Track D D4 — Power and MDE audit 001

**Document ID:** TRACK-D-D4-POWER-MDE-001  
**Type:** Research-lane audit / ADR  
**Status:** **complete (D4 package v1)** — findings are **not** production-promotion evidence  
**Date:** 2026-06-01  
**Branch / baseline:** `fix-kfold-multitreated-geometry` @ `24beae8` (post INV-D3-001 fix, Track E E0)  
**Lane:** **Research / robustness** per [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) § Track D  

**Authoritative inputs:**

| Document | Role |
|----------|------|
| [`TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md`](TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md) | Design layer; INV-D1-001 closed |
| [`TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md`](TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md) | Estimator / donor rows |
| [`TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md`](TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md) | Inference semantics |
| [`investigations/INV-D1-001_PRE_PERIOD_MATCHING_LEAKAGE.md`](investigations/INV-D1-001_PRE_PERIOD_MATCHING_LEAKAGE.md) | Pre-period assignment fix |
| [`investigations/INV-D3-001_UNIT_JACKKNIFE_LOO_TARGET.md`](investigations/INV-D3-001_UNIT_JACKKNIFE_LOO_TARGET.md) | JK target fix |
| [`track_d/archives/D5_DES_001a_results.json`](track_d/archives/D5_DES_001a_results.json) | Design OC |
| [`track_d/archives/D5_INF_002b_results.json`](track_d/archives/D5_INF_002b_results.json) | Inference OC |
| [`TRACK_E_METHOD_SUITABILITY_AND_TRIANGULATION_001.md`](TRACK_E_METHOD_SUITABILITY_AND_TRIANGULATION_001.md) | Suitability / triangulation (E0) |
| [`TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`](TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md) | Readout instruments |
| [`TRACK_B_ESTIMAND_REGISTRY_001.md`](TRACK_B_ESTIMAND_REGISTRY_001.md) | Estimand layers |

**Code authority (read-only review):** `panel_exp/design/power.py` · `panel_exp/design/geo_experiment_design.py` · `panel_exp/design/geo_runner.py` · `panel_exp/design/trimmed_match.py` · `tests/test_power_semantics.py` · `tests/test_power_contract.py`

---

## ADR decision record

| Field | Value |
|-------|--------|
| **Context** | D1–D3 closed design, estimator, and inference blockers (INV-D1-001, INV-D3-001 fixes validated). Power/MDE can now be audited against actual readout geometry, estimand, and inference semantics. |
| **Decision** | Document D4 research-lane audit; **no** power/estimator/inference/TrustReport changes in this package. |
| **Consequences** | POW-001–006 receive explicit governance roles; D5 power OC specs added; Track E suitability links documented. |
| **Alternatives rejected** | Treating `PowerAnalysis` MDE as decision-grade for SCM readout; wiring `mde_target` without D5 bridge; MMM feasibility from current power curves. |

---

## 1. Executive summary

D4 audited **power and MDE methods** against **design assignment**, **estimator/inference readout**, **geometry**, and **estimand alignment**.

**Headline:** `PowerAnalysis` is an explicit **simulation-coverage** planner (`MDE_SEMANTICS`, `power_contract`) — **not** classical analytic power. It is **documented as ranking/sensitivity only**. However, the **default GeoX design path** couples power to **`TBRRidge` + `Kfold`** on a **two-row aggregated panel** (pooled treated vs pooled control), which is **not aligned** with the governed production readout instrument **`SCM_UnitJackKnife`** on multi-unit geo panels.

**Overall D4 verdict (research lane):** `continue_with_characterization_required`

| Area | Verdict |
|------|---------|
| MDE semantics disclosure | **Pass** — `mde_semantics`, `power_contract`, tests |
| Estimand alignment | **Fail-risk** — percent grid on injected level effects ≠ registry `relative_att_post` without bridge |
| Readout method alignment | **Fail-risk** — default power ≠ SCM JK instrument |
| Design geometry | **Partial** — pre-period assignment fixed (INV-D1-001); power uses circular windows + aggregation |
| Inference for power | **Restricted** — inherits Kfold status (DEF-001) |
| Decision-grade claims | **Blocked** — contract `not_recommended_for` financial/commitment use |

---

## 2. Scope and non-goals

### In scope (D4)

| ID | Method / surface |
|----|----------------|
| **POW-001** | `PowerAnalysis` simulation-coverage MDE (`power.py`) |
| **POW-002** | ExperimentSpec `mde_target` (planning metadata) |
| **POW-003** | Geo-level / unit-level power surfaces (geo design path) |
| **POW-005** | Business ROI detectability (product framing) |
| **DES-012** | Treatment–control ratio optimization (feasibility link) |
| Geo orchestrator | `GeoExperimentDesign._run_power_analysis` / `geo_runner` step 4 |

### Light touch / defer

| ID | Disposition |
|----|-------------|
| **POW-004** | Multi-cell — Track C defer |
| **POW-006** | Long-term holdout — Track C defer |
| **TrimmedMatchDesign.power_analysis_with_cross_validation** | Separate classical-style path — note in §5 |

### Out of scope (explicit)

| Exclusion | Owner |
|-----------|--------|
| Code changes to power/MDE | Separate governed PR per finding |
| Estimator/inference fixes | D2/D3 / INV-* |
| TrustReport / Track B / CalibrationSignal | Track B |
| MMM / planning integration | Track E E7+ |
| Production promotion of power outputs | D7 |

---

## 3. Power / MDE inventory reviewed

| Pow ID | Implementation | **Post-D4 governance role** | **Robustness status** |
|--------|----------------|----------------------------|------------------------|
| **POW-001** | `PowerAnalysis` | **diagnostic_only** (design sensitivity) | characterization_required |
| **POW-002** | Spec `mde_target` | **diagnostic_only** (declared planning target) | diagnostic_only |
| **POW-003** | Geo design aggregated panel + POW-001 | **restricted** (geometry mismatch) | restricted |
| **POW-004** | Multi-cell | blocked (Track C) | unreviewed → deferred |
| **POW-005** | Business ROI narrative | **diagnostic_only** | diagnostic_only |
| **POW-006** | Holdout power | blocked (Track C) | unreviewed → deferred |

---

## 4. Estimand alignment review

Per [`TRACK_B_ESTIMAND_REGISTRY_001.md`](TRACK_B_ESTIMAND_REGISTRY_001.md) §4 (five layers).

| Layer | Power/MDE actual | Production geo readout (typical) | Aligned? |
|-------|------------------|--------------------------------|----------|
| **Declared** | Spec may set `mde_target` (optional) | `geo.relative_att_post.pooled_path` | **Partial** — field not wired to simulation |
| **Family export** | Path diff `(y - y_hat)` on injected % effect | SCM/TBR path relative lift | **Partial** |
| **Scored (recovery)** | Not used in `PowerAnalysis` | `relative_att_post` | **N/A** |
| **Interval** | `mean_ss` / `cum_ss` — interval covers zero | SCM JK CI (null monitor) | **No** — Kfold CI in default power |
| **MDE output** | `mde_percent` on **percent effect grid** | Business may read as “% lift detectable” | **Risk** — naming collision |

**D4-FIND-003:** `mde_percent` is a **simulation-grid percent injection** (level shift on treated units), not the registry ID `geo.relative_att_post.pooled_path.relative` unless an explicit transform documents the mapping.

**`power_contract` mitigates user harm:** `planning_use: ranking_and_sensitivity_only`, `not_recommended_for: guaranteed detectability claims, financial commitment thresholds`.

---

## 5. Design and geometry assumptions

### 5.1 Default GeoX power pipeline

```text
assign (pre_treatment_period=train_length)  →  INV-D1-001 path
       ↓
aggregate wide_data → 2 series: "treated" (sum of test units), "control" (sum of controls)
       ↓
PowerAnalysis(model=TBRRidge, inference=Kfold, test_length, train_length)
       ↓
mde_percent / mde_kpi_cumulative + power_contract
```

| Assumption | Status | Notes |
|------------|--------|-------|
| Pre-period design assignment | **pass** (post INV-D1-001) | `geo_runner` passes `pre_treatment_period` |
| Matched markets preserved in power panel | **fail-risk** | Aggregation to 2 rows destroys unit-level geometry |
| Multi-treated units | **partial** | Summed into single treated series |
| Supergeo / market groups | **not modeled** | No supergeo weighting in `PowerAnalysis` |
| Treatment allocation / n_test_grps | **pass** | Uses assigned `treated_units` |
| Pre-period length | **pass** | `train_length` → `TimePeriod(0, train_length)` in spec |
| Test length grid | **pass** | `test_lengths` loop |

### 5.2 `PowerAnalysis` simulation design

| Mechanism | Implication |
|-----------|-------------|
| Circular sliding train/test windows | Differs from fixed holdout post window in live experiment |
| `fake_effect` percent injection on treated wide rows | Level-shift DGP, not business revenue % without transform |
| `mean_ss` = interval covers zero on **mean** post effect | Tied to chosen inference CI semantics |
| `ci_version` 1 vs 2 | Different MDE definitions (grid vs null SD) |

### 5.3 Trimmed match (separate path)

`TrimmedMatchDesign.power_analysis_with_cross_validation` uses **classical normal-approximation CIs** on pair lifts — **not** `PowerAnalysis` semantics. Governed separately; do not conflate with POW-001.

---

## 6. Inference and readout alignment review

| Question | Finding |
|----------|---------|
| Is power tied to **actual readout** instrument? | **No** (default) — TBRRidge+Kfold vs **SCM_UnitJackKnife** |
| Does power use **post-fix** JK semantics? | Only if caller sets `inference="UnitJackKnife"` — **not** geo default |
| Does power inherit **inference OC**? | **Yes** — Kfold restricted (DEF-001); JK null-monitor only (DEF-013) |
| Placebo-based power? | **Not implemented** in `PowerAnalysis` |
| BRB / DID power? | **Not** default geo path |

**D4-FIND-001 (high):** Default geo MDE sensitivity is **not** a power analysis for the **SCM Unit Jackknife** measurement instrument.

**D4-FIND-004:** Power intervals use **Kfold** — same restricted status as `TBRRidge_Kfold` in D3; MDE thresholds are **not transferable** to SCM JK readout.

**Post INV-D3-001:** If power were re-run with `UnitJackKnife`, JK widths would reflect fixed LOO target — **separate D5 characterization required** before any trust linkage (Track E E-OQ-6).

---

## 7. Known failure modes

| Mode | Symptom | Disposition |
|------|---------|-------------|
| Readout mismatch | Plan with Kfold MDE, analyze with SCM JK | **restricted** — document in feasibility |
| Aggregation collapse | Multi-market → 2-row panel | Underestimate geo heterogeneity risk |
| Circular windows | Optimistic/pessimistic vs fixed post | **characterization_required** |
| Conservative JK in readout | Zero power on positive DGP (D3) | MDE may show high % — **not comparable** |
| `mde_target` ignored | Spec field unused in simulation | **diagnostic_only** |
| aa_calibration incomplete | `evaluate_aa_calibration` warns | Do not use for commitment |
| ci_version confusion | v1 grid vs v2 SD MDE | Document per run in `mde_semantics` |

---

## 8. Method suitability implications (Track E)

| Track E diagnostic | Power/MDE implication |
|--------------------|------------------------|
| Pre-period fit | Power uses TBRRidge on aggregated series — not SCM pre-fit |
| Multi-treated geometry | Aggregation hides per-unit suitability |
| Signal-to-noise / MDE | `mde_percent` is **planning diagnostic only** |
| Estimand alignment | Flag **estimand_disagreement** if MDE compared to SCM relative ATT |
| Inference disagreement | **high** if power Kfold vs readout JK |
| Placebo feasibility | Not in power path |

**Triangulation rule (E0):** Do **not** triangulate `PowerAnalysis` MDE against `SCM_UnitJackKnife` point/interval as same instrument — classify as **estimand_disagreement** or **geometry_disagreement** until D5-POW-001 bridge exists.

---

## 9. Track B instrument mapping

| Surface | Catalog / config | Power path uses | Compatible for joint claims? |
|---------|------------------|-----------------|------------------------------|
| Design feasibility | ExperimentSpec + evidence | TBRRidge+Kfold MDE | **No** for SCM JK claims |
| Production readout | `SCM_UnitJackKnife` | Not default | **No** |
| TrustReport | Scenarios on adapter exports | Power not in RunBundle adapter | **N/A** |
| CalibrationSignal | SCM JK only | Power excluded | **Correct** |

**TrustReport:** Power outputs must **not** populate `alignment_verdict` / lift scenarios without a governed instrument bridge (unchanged by D4).

---

## 10. Finding register (governance)

| Finding ID | Summary | Severity | Disposition | Fix track |
|------------|---------|----------|-------------|-----------|
| **D4-FIND-001** | Default geo power = TBRRidge+Kfold, not SCM JK readout | **high** | **restricted** | D5-POW-001a; optional INV-D4-001 |
| **D4-FIND-002** | Treated/control **aggregation** to 2-row panel | **medium** | **characterization_required** | D5-POW-001c |
| **D4-FIND-003** | `mde_percent` ≠ registry `relative_att_post` without transform | **medium** | **diagnostic_only** | Document bridge in E2 |
| **D4-FIND-004** | Power inherits **Kfold** restricted inference | **medium** | **restricted** | Align POW-001 with INF-004 |
| **D4-FIND-005** | `mde_target` spec field not wired to `PowerAnalysis` | **low** | **diagnostic_only** | DEF-010 / INV-022 |
| **D4-FIND-006** | Circular sliding windows ≠ fixed experiment post window | **medium** | **accepted_deviation** | D5-POW-001d |
| **D4-FIND-007** | `power_contract` correctly blocks decision-grade use | **low** | **accepted_deviation** | Maintain contracts |
| **D4-FIND-008** | `evaluate_aa_calibration` diagnostic not production gate | **low** | **characterization_required** | D5-POW-001e |

**Promotion rule:** No POW row may advance to **decision_eligible** without readout-aligned D5 OC and Track E suitability pass.

### Proposed INV-D4-001 (optional, not opened in D4)

**Title:** Geo design power/readout instrument alignment  
**Scope:** Characterize MDE curves under `TBRRidge+Kfold` vs `SyntheticControl+UnitJackKnife` on identical assignment — **D5-POW-001a complete** (verdict: **optimistic_proxy**; geo `mde_percent` ~1.5% vs ~4% pooled SCM+JK detection MDE on same assignment).

**D5-POW-001a summary:** On `scm_low_signal` + greedy pre-period assignment (n=24 MC), injection-grid point effects correlate for both paths, but pooled interval-detection curves are degenerate (100% exclude zero at all grid points). Geo `PowerAnalysis` `mde_percent` (ci_version=2) is materially **lower** than pooled SCM+JK interval MDE — **do not** use geo MDE for SCM JK feasibility or MMM planning.

---

## 11. Required D5 / OC simulations

| Sim ID | Target | Purpose | Status |
|--------|--------|---------|--------|
| **D5-POW-001a** | POW-001 | Same assignment/DGP: MDE percent under TBRRidge+Kfold vs SCM+JK | ✅ [`D5_POW_001a_results.json`](track_d/archives/D5_POW_001a_results.json) |
| **D5-POW-001b** | POW-001 | SCM+JK null-monitor / detection semantics post INV-D3-001 | ✅ [`D5_POW_001b_results.json`](track_d/archives/D5_POW_001b_results.json) |
| **D5-POW-001c** | POW-003 | Unit-level panel vs 2-row aggregation — design geometry | ✅ [`D5_POW_001c_results.json`](track_d/archives/D5_POW_001c_results.json) |
| **D5-POW-001d** | POW-001 | Circular windows vs fixed pre/post window | Planned |
| **D5-POW-001e** | aa_calibration | Null-effect FPR at n≥100 replications per inference choice | Planned |
| **D5-POW-002a** | POW-002 | Record `mde_target` vs simulated `mde_percent` when both present | Planned |

Archive under `docs/track_d/archives/`.

---

## 12. Correctness checklist per method

### POW-001 — `PowerAnalysis`

| Check | Status |
|-------|--------|
| Documented non-classical MDE | **pass** |
| Reproducible with `random_state` | **pass** |
| Null calibration helper | **pass** (`evaluate_aa_calibration`) |
| Aligned to production readout | **fail** (default geo) |
| Aligned to registry estimand | **partial** |
| Decision-grade | **blocked** (`power_contract`) |

### POW-002 — `mde_target`

| Check | Status |
|-------|--------|
| Captured on spec | **pass** |
| Drives simulation grid | **fail** |
| Track B export | **N/A** |

---

## 13. Literature grounding (D0b backlog)

| ID | Family | D0b action |
|----|--------|------------|
| POW-001 | Simulation-based planning | Document deviation from Neyman-Pearson power |
| POW-002 | Minimum detectable effect | Link to estimand registry |
| DES-012 | Allocation optimization | Feasibility literature |

---

## 14. Matrix updates (D4)

Applied in [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) §9.

---

## 15. Recommended next actions

| Priority | Action | Lane |
|----------|--------|------|
| P1 | **D5-POW-001d–e** — windows and design-tier null FPR at scale | D5 |
| P1 | **Track E E1** — suitability diagnostic inventory (power/feasibility facets) | E1 |
| P2 | Optional **INV-D4-001** if D5 shows large MDE divergence | Research |
| P2 | **Broader D5** OC (inference/design) before MMM | D5 |
| — | **Do not** feed current geo MDE to MMM CalibrationSignal | Governance |

---

## 16. Checkpoint vs D1–D3

| Prerequisite | Status |
|--------------|--------|
| Design pre-period assignment | ✅ INV-D1-001 |
| Estimator donor pool (SCM) | ✅ D2 characterized |
| Inference JK target | ✅ INV-D3-001 |
| D4 valid | ✅ |
| MMM integration | ❌ Not yet |

---

## 17. Sign-off

| Role | Statement |
|------|-----------|
| **D4 audit** | Package complete; research-lane only |
| **Code changes** | None |
| **Power promotion** | None |

---

*TRACK-D-D4-POWER-MDE-001 v1.0.0 — research lane — 2026-06-01*
