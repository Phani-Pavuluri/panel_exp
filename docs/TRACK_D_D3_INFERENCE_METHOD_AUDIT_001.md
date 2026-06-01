# Track D D3 — Inference method audit 001

**Document ID:** TRACK-D-D3-INFERENCE-001  
**Type:** Research-lane audit / ADR  
**Status:** **complete (D3 package v1)** — findings are **not** production-promotion evidence  
**Date:** 2026-05-28  
**Branch / baseline:** `fix-kfold-multitreated-geometry` @ `fed7050` (post D2 estimator/donor audit)  
**Lane:** **Research / robustness** per [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) § Track D  

**Authoritative inputs:**

| Document | Role |
|----------|------|
| [`TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md`](TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md) | Estimator layer; estimator/inference separation |
| [`audits/AUDIT-006_track_d_d2_estimator_gate.md`](audits/AUDIT-006_track_d_d2_estimator_gate.md) | D2 gate; INV-D2-001 deferred |
| [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) | INF-* rows |
| [`TRACK_D_LITERATURE_CROSSCHECK_001.md`](TRACK_D_LITERATURE_CROSSCHECK_001.md) | §3.1 SCM inference, §3.8 conformal |
| [`TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`](TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md) | Instrument IDs + usage boundaries |
| [`TRACK_B_ESTIMAND_REGISTRY_001.md`](TRACK_B_ESTIMAND_REGISTRY_001.md) | Interval vs point estimand layers |
| [`PHASE15_PLACEBO_CHARACTERIZATION_001.md`](PHASE15_PLACEBO_CHARACTERIZATION_001.md) | INV-029 placebo OC |
| [`SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md) | SCM JK null battery |

**Code authority (read-only review):** `panel_exp/inference/` · `panel_exp/inference/modes/impl.py` · `panel_exp/inference/registry.py` · `panel_exp/validation/nominal_calibration.py` · `panel_exp/validation/did_interval_policy.py` · `panel_exp/track_b/trust_report.py` · `panel_exp/track_b/geo_adapter.py`

---

## ADR decision record

| Field | Value |
|-------|--------|
| **Context** | D1 closed design-period leakage; D2 audited SCM estimators and donor pools. Inference modes can now be reviewed without conflating assignment leakage with uncertainty construction. |
| **Decision** | Document D3 research-lane inference audit; **no** inference/estimator/TrustReport/eligibility code changes in this package. |
| **Consequences** | INF-001–010 receive explicit governance roles (calibration-eligible vs null-monitor vs diagnostic vs restricted vs blocked); D5 inference OC specs added; catalog recommendations are **documentation-only** until governance PRs. |
| **Alternatives rejected** | Expanding `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` because design is fixed; treating placebo bands as CIs; inline inference fixes during D3. |

---

## 1. Executive summary

D3 audited **inference modes independently** from estimator point fits, prioritizing **SCM Unit Jackknife**, **SCM/TBRRidge placebo**, **TBRRidge KFold/BRB**, **DID bootstrap**, and registry variants (**JKP**, **Conformal**, **TimeSeriesKfold**, **Bayesian**).

**Headline:** Platform inference semantics are **correctly separated at the registry and Track B layers** (`path_interval_type`, `interval_semantics`, TrustReport claim gating). **Operating-characteristic evidence** shows SCM JK is a **conservative null monitor** (FPR≈0, power≈0), placebo is a **single-treated diagnostic** (`placebo_band`, not CI), and TBRRidge intervals are **restricted** with known geometry/scale issues. **No inference mode** qualifies for **lift-detection calibration** or **decision-grade** promotion on the default geo battery.

**Overall D3 verdict (research lane):** `continue_with_characterization_required`

| Layer | Verdict |
|-------|---------|
| Registry interval typing | **Pass** — `IntervalType` + `InferenceModeSpec.path_interval_type` |
| Estimator/inference separation | **Pass** — D2 confirmed; D3 deepens per-mode |
| Interval estimand alignment (geo recovery) | **Pass with documented exceptions** — DID cumulative (DEF-003) |
| SCM JK (`INF-002`) | **null_monitor_only** — sole calibration-eligible config |
| Placebo (`INF-006`) | **diagnostic_only** — single-treated scope |
| TBRRidge KFold/BRB | **restricted** — not calibration-eligible |
| DID bootstrap (`INF-010`) | **restricted** — relative ATT interval unsupported |
| TrustReport lift claims on JK/placebo | **Blocked/inconclusive** — by design |

**Calibration eligibility registry:** **Unchanged** — `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS = {"SCM_UnitJackKnife"}` only.

---

## 2. Scope and non-goals

### In scope (D3)

| Inf ID | Mode | D3 depth |
|--------|------|----------|
| **INF-001** | point_estimate | Full |
| **INF-002** | UnitJackKnife | Full |
| **INF-003** | JKP | Medium |
| **INF-004** | Kfold | Full |
| **INF-005** | BlockResidualBootstrap | Full |
| **INF-006** | Placebo | Full |
| **INF-007** | Conformal | Medium |
| **INF-008** | Bayesian (registry) | Medium |
| **INF-009** | TimeSeriesKfold | Medium |
| **INF-010** | DID bootstrap (estimator-embedded) | Full |

**Characterized configs (Track B):** `SCM_UnitJackKnife`, `SCM_Placebo`, `TBRRidge_Kfold`, `TBRRidge_BlockResidualBootstrap`, `DID_Bootstrap`, `AugSynthCVXPY_UnitJackKnife` (characterized, not eligible).

### Out of scope (explicit)

| Exclusion | Owner |
|-----------|--------|
| Inference/estimator code changes | Separate governed PR per finding |
| TrustReport / Track B contract changes | Track B milestones |
| Eligibility/maturity/release gate code changes | Governance |
| Estimator `full_model` fix | INV-D2-001 |
| Design assignment | D1 ✅ |
| Power/MDE methods | D4 |
| MMM / planning | Forbidden |

---

## 3. Inference inventory reviewed

| Inf ID | Implementation | Path interval type | **Governance role (post-D3)** | **Robustness status** |
|--------|----------------|-------------------|------------------------------|------------------------|
| **INF-001** | `run_point_estimate` | UNAVAILABLE | **diagnostic_only** | diagnostic_only |
| **INF-002** | `unit_jk` → `run_unit_jackknife` | CONFIDENCE_INTERVAL | **null_monitor_only** | null_monitor_characterized |
| **INF-003** | `jkp` → `run_jkp` | CONFIDENCE_INTERVAL | **characterization_required** | characterization_required |
| **INF-004** | `kfold` → `run_kfold` | CONFIDENCE_INTERVAL | **restricted** | restricted |
| **INF-005** | `block_residual_bootstrap` | CONFIDENCE_INTERVAL | **restricted** | restricted |
| **INF-006** | `placebo_with_ci_inversion` | PLACEBO_BAND (+ optional effect CI) | **diagnostic_only** | diagnostic_characterized |
| **INF-007** | `conformal` | CONFORMAL_INTERVAL | **characterization_required** | characterization_required |
| **INF-008** | `run_bayesian` | CREDIBLE_INTERVAL | **blocked** | blocked |
| **INF-009** | `run_timeseries_kfold` | CONFIDENCE_INTERVAL | **characterization_required** | characterization_required |
| **INF-010** | `DID.py` block bootstrap | cumulative (policy) | **restricted** | restricted |

### Config alias → instrument mapping (unchanged)

| Config alias | Inf mode | Catalog instrument (abbrev.) |
|--------------|----------|------------------------------|
| `SCM_UnitJackKnife` | UnitJackKnife | `geo.synthetic_control.unit_jackknife...confidence_interval` |
| `SCM_Placebo` | Placebo | `geo.synthetic_control.placebo...placebo_band` |
| `TBRRidge_Kfold` | Kfold | `geo.tbrridge.kfold...confidence_interval` |
| `TBRRidge_BlockResidualBootstrap` | BlockResidualBootstrap | `geo.tbrridge.block_residual_bootstrap...` |
| `DID_Bootstrap` | DID-internal bootstrap | `geo.did.bootstrap...cumulative_att_interval` |

---

## 4. Per-method correctness checklists

### 4.1 INF-002 — UnitJackKnife (SCM primary)

| Check | Status | Notes |
|-------|--------|-------|
| Requires ≥2 control units | **pass** | Registry `estimator_check` |
| Leave-one-out over **control** donors | **pass** | `panel.drop_units(unit)` for non-treated |
| Interval applied to treated path | **pass** | `y_hat ± errors` on full time axis |
| Literature: donor jackknife for SCM | **partial** | AER 2019 / arXiv 1905.02928 cited in code |
| JK variation uses consistent estimand | **review** | Full fit stores `mu = results["y"]`; LOO compares `y_hat` to `y` — see **D3-FIND-001** |
| Null OC (geo battery) | **characterized** | FPR≈0, coverage≈1, power≈0 |
| Lift OC | **fail** | Zero power on positive DGP |
| Inherits estimator `full_model` if passed | **warn** | Each LOO refit uses estimator kwargs — couples to INV-D2-001 |

**Role:** **null_monitor_only** — not lift detector (DEF-013, Phase 11/13).

### 4.2 INF-006 — Placebo

| Check | Status | Notes |
|-------|--------|-------|
| Placebo-in-space over control units | **pass** | `_build_placebo_distribution` |
| Path output is **band**, not CI | **pass** | `IntervalType.PLACEBO_BAND`; module docstring |
| RMSPE pre-fit filter | **pass** | Stabilizes poor placebo fits |
| Effect CI via inversion (optional) | **pass** | Separate `effect_ci_*_inversion`; `InferenceResult` dual typing |
| ≥5 controls for strict mode | **pass** | `run_placebo` guards |
| Multi-treated | **fail** | Phase 15: 100% failure default DGP |
| TBR aggregated control | **fail** | Explicit `placebo_unsupported` |
| TrustReport lift via placebo band | **blocked** | `interval_sem == placebo_band` → incompatible for interval-backed lift |

**Role:** **diagnostic_only** / **null_reference** — single-treated scope (Phase 15, DEF-020).

### 4.3 INF-004 — Kfold (TBRRidge)

| Check | Status | Notes |
|-------|--------|-------|
| Temporal blocking | **pass** | `cross_fold` / panel time folds |
| Multi-treated residual aggregation | **partial** | `_aggregate_treatment_residuals` pooled geometry |
| Debias path | **pass** | Optional debias flag |
| Multi-treated failure (historical) | **mitigated** | Post-fix 0% failure; positive OC still fails |
| Calibration eligibility | **excluded** | `kfold_multi_treated_unsupported_run001` |

**Role:** **restricted** / **runnable_not_trusted** on default DGP.

### 4.4 INF-005 — BlockResidualBootstrap (TBRRidge)

| Check | Status | Notes |
|-------|--------|-------|
| Model-conditional residual bootstrap | **pass** | Documented in module |
| Cumulative + path bands | **pass** | `effect_cumulative_brb` stats |
| Donor pooling experimental | **pass** | Single-treated only when enabled |
| Positive DGP coverage | **fail** | Under-coverage (DEF-002) |
| Historical bounds inversion | **documented** | Run 001; removed from eligibility |

**Role:** **restricted** — null-viable characterization only; not lift-calibrated.

### 4.5 INF-010 — DID bootstrap

| Check | Status | Notes |
|-------|--------|-------|
| Point path scored as `relative_att_post` | **pass** | Recovery contract |
| Intervals on cumulative absolute ATT | **pass** | `did_interval_policy.py` |
| Relative ATT interval calibration | **unsupported** | `DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED` |
| Pretrend diagnostic coupling | **pass** | DG-003 / GOLD-008 |

**Role:** **restricted** — point directional read only; interval layer uses `geo.cumulative_att.did_bootstrap.absolute`.

### 4.6 INF-001, INF-003, INF-007–009, INF-008

| Mode | Checklist summary | Role |
|------|-------------------|------|
| **INF-001** | No uncertainty; point-only exports | **diagnostic_only** |
| **INF-003** | JKP time-dropout logic; registry tests only | **characterization_required** |
| **INF-007** | Conformal null grid; exchangeability unverified | **characterization_required** |
| **INF-009** | Time-series k-fold; separate from panel Kfold | **characterization_required** |
| **INF-008** | Registry JAX path ≠ full BayesianTBR MCMC | **blocked** |

---

## 5. Geometry assumptions and failure modes

| Geometry | INF-002 JK | INF-004 Kfold | INF-005 BRB | INF-006 Placebo | INF-010 DID |
|----------|------------|---------------|-------------|-----------------|-------------|
| **Single-treated** | Supported | Supported (exploratory OC) | Supported; donor pool opt | **Primary scope** | Supported |
| **Multi-treated default** | Supported (pooled path) | Supported post-fix; OC weak | Supported; aggregation semantics | **Not supported** | Supported (panel policy) |
| **Min controls** | ≥2 | fold construction | bootstrap series | ≥5 strict | design-dependent |
| **Exchangeability** | Donor exchangeability for JK | Temporal blocks ≠ iid | Residual stationarity blocks | Placebo-in-space | Parallel trends + design |
| **Donor pool** | Inherits EST fit | Inherits EST fit | Treated residuals (+ optional donor pool) | Re-fits per placebo unit | TWFE structure |

### Failure mode register

| Mode | Failure | Symptom | Disposition |
|------|---------|---------|-------------|
| JK | Too few controls | Registry pre-check error | **blocked** at run |
| JK | Conservative null | Coverage≈1, power≈0 | **accepted_deviation** (DEF-013) |
| Placebo | Multi-treated | `NotImplementedError` / failures | **geometry_blocked** |
| Placebo | TBR aggregate | `placebo_unsupported` | **blocked** |
| Kfold | Historical multi-treated | Run 001 failures | **mitigated**; stay restricted |
| BRB | Positive DGP | Under-coverage | **restricted** (DEF-002) |
| DID | Relative interval claim | Policy skip in calibration | **restricted** (DEF-003) |

---

## 6. Interval estimand alignment review

Per [`TRACK_B_ESTIMAND_REGISTRY_001.md`](TRACK_B_ESTIMAND_REGISTRY_001.md) §4 — five layers must not be conflated.

| Config | Point / scored estimand | Interval estimand | Recovery alignment | Track B adapter |
|--------|-------------------------|-------------------|--------------------|-----------------|
| `SCM_UnitJackKnife` | `geo.relative_att_post.pooled_path` | Same (path CI) | **aligned** when `interval_estimand=relative_att_post` | `confidence_interval` |
| `SCM_Placebo` | pooled path ATT | `placebo.null_envelope` / band | **aligned** single-treated | `placebo_band` |
| `TBRRidge_Kfold` | pooled path | relative path CI | aligned post-fix | `confidence_interval` |
| `TBRRidge_BlockResidualBootstrap` | pooled path | relative path CI | aligned; positive OC weak | `confidence_interval` |
| `DID_Bootstrap` | `relative_att_post` (path) | **`cumulative_att` absolute** | **misaligned for relative CI claims** | `cumulative_att_interval` |

**TrustReport rules (unchanged, verified):**

- Interval-backed **lift** claims: incompatible with `placebo_band`, `none`, or `interval_semantics_compatible=False`.
- **null_viability**: may be `supported` only when `expected_usage_boundary` is `null_monitor_only` or `null_reference_diagnostic` and export complete.
- **null_monitor_only** (SCM JK): lift claims → `inconclusive`, not `supported`.

**D3-FIND-002:** Placebo exports path `y_lower`/`y_upper` as **placebo band**; inversion CIs are **effect-level** optional fields — adapter must not treat path band as `relative_att_post` CI (current Track B: **pass**).

---

## 7. Literature grounding requirements

| Inf ID | Literature anchor | D0b action | Post-D3 decision |
|--------|-------------------|------------|------------------|
| **INF-002** | Abadie SCM inference; donor jackknife papers in code | Complete SCM inference YAML | **aligned_with_deviation** (null monitor) |
| **INF-006** | Permutation / placebo inference | Placebo ≠ CI in YAML | **aligned_with_deviation** |
| **INF-004** | Arkhangelsky et al. synthetic control t-test (k-fold) | TBR fold record | **needs_characterization** |
| **INF-005** | Block bootstrap (Künsch 1989) | BRB assumptions doc | **needs_characterization** |
| **INF-010** | DID cluster/bootstrap | Cumulative vs relative split | **aligned_with_deviation** (DEF-003) |
| **INF-007** | Conformal prediction | Exchangeability section | **unreviewed** |
| **INF-003** | Jackknife+ | Separate from unit JK | **unreviewed** |

---

## 8. Finding register (governance)

| Finding ID | Summary | Severity | Disposition | Fix track |
|------------|---------|----------|-------------|-----------|
| **D3-FIND-001** | Unit JK LOO compares leave-one-out `y_hat` to full-fit `y` (actual), not counterfactual-to-counterfactual | medium | **open_inv_d3_001** | [D5-INF-002a](track_d/archives/D5_INF_002a_results.json) · [INV-D3-001](investigations/INV-D3-001_UNIT_JACKKNIFE_LOO_TARGET.md) |
| **D3-FIND-002** | SCM JK conservative null (FPR≈0, power≈0) — not lift CI | low | **accepted_deviation** | DEF-013; INV-030 |
| **D3-FIND-003** | Placebo multi-treated unsupported on default geo DGP | medium | **geometry_blocked** | DEF-020; product scope doc |
| **D3-FIND-004** | Placebo path band must not be read as classical CI | low | **accepted_deviation** | GOLD-005; Phase 15 |
| **D3-FIND-005** | TBRRidge KFold excluded from nominal calibration | medium | **restricted** | DEF-001 |
| **D3-FIND-006** | TBRRidge BRB positive-DGP under-coverage | medium | **restricted** | DEF-002 |
| **D3-FIND-007** | DID relative ATT interval unsupported by construction | medium | **restricted** | DEF-003 |
| **D3-FIND-008** | Inference refits inherit estimator kwargs (`full_model`, etc.) | medium | **deferred** | INV-D2-001 coupling |
| **D3-FIND-009** | JKP / Conformal / TSK — registry coverage only | low | **characterization_required** | D5-INF-007a |
| **D3-FIND-010** | Registry Bayesian ≠ production BayesianTBR | high | **blocked** | Do not map to decision instruments |

**Promotion rule:** No change to `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` from D3.

### INV-D3-001 (opened by D5-INF-002a — 2026-06-01)

**Title:** Unit jackknife LOO target uses observed `y` vs leave-one-out `y_hat`  
**Artifact:** [`track_d/archives/D5_INF_002a_results.json`](track_d/archives/D5_INF_002a_results.json) — **`open_inv_d3_001`**  
**Doc:** [`investigations/INV-D3-001_UNIT_JACKKNIFE_LOO_TARGET.md`](investigations/INV-D3-001_UNIT_JACKKNIFE_LOO_TARGET.md)  
**Pattern:** Characterize → governed fix → D5 re-run (fix **not** in D5 package).

---

## 9. Required D5 / OC simulations

| Sim ID | Target | Purpose | Status |
|--------|--------|---------|--------|
| **D5-INF-002a** | SCM JK | Treated post noise invariance; prod vs literature LOO anchor | **Done** → INV-D3-001 |
| **D5-INF-002b** | SCM JK | Compare JK variation 1 vs 2 on null DGP |
| **D5-INF-002c** | SCM JK | Multi-treated vs single-treated width/concentration |
| **D5-INF-006a** | Placebo | Single-treated: band rate = 1.0; multi-treated failure rate |
| **D5-INF-006b** | Placebo | Path band vs inversion CI inclusion on null |
| **D5-INF-004a** | Kfold | Post-fix multi-treated failure rate + positive coverage |
| **D5-INF-005a** | BRB | Cumulative vs path coverage on null and positive |
| **D5-INF-010a** | DID | Confirm relative path point vs cumulative interval non-comparability |
| **D5-INF-008a** | Conformal | Null grid sensitivity (if mode enters geo exports) |

Archive under `docs/track_d/archives/` when executed.

---

## 10. Measurement Instrument Catalog status recommendations

**Documentation recommendations only** — eligibility registry and Track B contracts **unchanged** in this commit.

| Instrument / alias | Current catalog tier | D3 recommendation | Rationale |
|--------------------|---------------------|---------------------|-----------|
| `SCM_UnitJackKnife` | governed | **unchanged** — null_monitor_only | Sole calibration-eligible config |
| `SCM_Placebo` | governed | **unchanged** — diagnostic_only | Phase 15 OC; single-treated |
| `TBRRidge_BlockResidualBootstrap` | restricted | **unchanged** — restricted | DEF-002; not eligible |
| `TBRRidge_Kfold` | restricted | **unchanged** — restricted | DEF-001; not eligible |
| `TBRRidge_Placebo` | characterized | **unchanged** — diagnostic secondary | Weaker archive than SCM |
| `DID_Bootstrap` | characterized partial | **unchanged** — restricted intervals | DEF-003 |
| `AugSynthCVXPY_UnitJackKnife` | characterized | **unchanged** — not registry eligible | Mirrors JK conservatism |
| `TBR_Placebo` | registered unsupported | **unchanged** — blocked | Aggregated-control policy |

### Governance role matrix (canonical for D3)

| Role | Members |
|------|---------|
| **calibration_eligible** | `SCM_UnitJackKnife` only |
| **null_monitor_only** | SCM JK (+ characterized AugSynth JK, not eligible) |
| **diagnostic_only** | SCM Placebo, TBRRidge Placebo, point-only configs |
| **restricted** | TBRRidge KFold, TBRRidge BRB, DID Bootstrap intervals |
| **blocked** | Registry Bayesian, TBR Placebo |

---

## 11. TrustReport interpretation map

| Scenario claim | SCM JK | SCM Placebo | TBRRidge BRB/Kfold | DID Bootstrap |
|----------------|--------|-------------|-------------------|---------------|
| `lift_detection` | inconclusive | unsupported | inconclusive | inconclusive |
| `null_viability` | inconclusive / aligned* | aligned* (single-treated) | inconclusive | inconclusive |
| `interval_backed_lift` | unsupported (null monitor) | unsupported (placebo band) | inconclusive | unsupported (scale) |
| `point_directional_read` | inconclusive | inconclusive | inconclusive | inconclusive |
| `cumulative_att_read` | N/A | N/A | N/A | inconclusive |

\*When `export_status=complete`, geometry in scope, and `expected_usage_boundary` matches.

**No TrustReport changes in D3** — mapping confirms existing composer behavior in `trust_report.py`.

---

## 12. Matrix updates (D3)

Applied in [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) §8.

---

## 13. Recommended next actions

| Priority | Action | Lane |
|----------|--------|------|
| P1 | **D5** — D5-INF-002a (JK LOO target / post noise invariance) | D5 |
| P0 | **INV-D3-001** governed fix (`unit_jk` anchor → `y_hat`) + D5-INF-002b post-fix | Research → fix PR |
| P2 | **D4** power/MDE audit (match readout estimator + estimand) | D4 |
| P2 | **INV-D2-001** estimator `full_model` (inference refit coupling) | Research |
| P2 | Complete D0b YAML for INF-002, INF-006 | D0b |
| — | Do **not** expand calibration eligibility from D3 | Governance |

---

## 14. Checkpoint vs D2

| Gate | D2 | D3 |
|------|----|----|
| Estimator pre-fit (default SCM) | OK | Inference reviewed on that foundation |
| Inference semantics | Separation only | **Full INF audit** |
| CalibrationSignal | Unchanged | **Unchanged** |
| Production promotion | No | **No** |

---

## 15. Sign-off

| Role | Statement |
|------|-----------|
| **D3 audit** | Package complete; research-lane only |
| **Code changes** | None |
| **TrustReport / Track B** | Unchanged |
| **Eligibility registry** | Unchanged |

---

*TRACK-D-D3-INFERENCE-001 v1.0.0 — research lane — 2026-05-28*
