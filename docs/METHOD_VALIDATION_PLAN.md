# Method validation plan

**Date:** 2026-05-20  
**Version:** 0.2.1  
**Inputs:** `docs/CALIBRATION_RUN_001.md`, `docs/CALIBRATION_FAILURE_ANALYSIS_001.md`, `docs/VALIDATION_COVERAGE.md`, `docs/PHASE8_ALGORITHM_AUDIT.md`, `panel_exp/method_metadata.py`

## Validation path legend

| Code | Meaning |
|------|---------|
| **A** | Eligible for **relative-ATT** nominal interval calibration (`relative_att_post`) |
| **B** | Eligible for **point-estimate recovery** only (`RecoveryRunner`, `inference=None`) |
| **C** | Eligible for **different-estimand** calibration (e.g. `cumulative_att`, DID bootstrap) |
| **D** | **Research-only** reliability characterization first (smoke, diagnostics, no nominal claims) |
| **E** | **Unsupported / skip** with documented reason |

**Scored estimand (recovery):** `relative_att_post` unless noted.  
**Run 001:** n=100, seeds (0,1,2), scenarios `recovery_null_effect`, `recovery_positive_effect`.

---

## Part A — Method / config matrix

### SCM family

| Method / config | Maturity | Point estimand | Interval available | Interval estimand | Cal. eligibility (pre-Run-001) | Run 001 | Path | Next validation | Recommendation |
|-----------------|----------|----------------|--------------------|-------------------|----------------------------------|---------|------|-----------------|----------------|
| **SCM** | expert_review | relative_att_post | Optional (many modes) | varies | B only (default recovery) | — | **B** | Family recovery scenarios (`scm_*`); point bias/ATT direction | Default recovery without inference |
| **SCM_UnitJackKnife** | expert_review + UnitJackKnife | relative_att_post | Yes | relative_att_post | A | Null pass; power 0 | **A*** | Null nominal calibration on default DGP; separate power study with documented CI width | **Keep A** with caveat: null-only credibility; see failure analysis |
| **SyntheticControlCVXPY** | expert_review | relative_att_post | Optional | relative_att_post (if wired) | E (no recovery runner) | — | **E** → **B** after wiring | Add `RecoveryRunner` config + smoke | Wire recovery before any calibration |
| **AugSynth** | unvalidated | relative_att_post | Optional | unknown | E | — | **E** | Basic recovery wiring + unit tests | Skip calibration until validated |
| **AugSynthCVXPY** | expert_review | relative_att_post | Optional | relative_att_post (if wired) | E | — | **E** → **B** | Same as CVXPY SCM | Skip calibration until runner exists |

\* **A with limits:** multi-treated pooling; power not demonstrated at `true_effect=0.10`.

### TBR / TBRRidge family

| Method / config | Maturity | Point estimand | Interval available | Interval estimand | Cal. eligibility (pre-Run-001) | Run 001 | Path | Next validation | Recommendation |
|-----------------|----------|----------------|--------------------|-------------------|----------------------------------|---------|------|-----------------|----------------|
| **TBR** | expert_review | relative_att_post | Optional | varies | B (alias of TBRRidge factory) | — | **B** | Same as TBRRidge point recovery | Use TBRRidge for evidence |
| **TBRRidge** | expert_review | relative_att_post | Optional | varies | B (point recovery configs) | — | **B** | `tbrridge_*` recovery scenarios | Point recovery + expert review |
| **TBRRidge_Kfold** | expert_review | relative_att_post | Intended yes | — (never aligned on recovery_*) | A | 100% ValueError | **E** on default recovery | Single-treated scenario OR fix multi-treated k-fold | **Remove from A** on `recovery_*` |
| **TBRRidge_BlockResidualBootstrap** | expert_review | relative_att_post | Yes (mis-ordered) | relative_att_post (aligned flag true) | A | FPR 1.0, coverage 0 | **E** until inference fix | BRB path bound audit on multi-treated | **Remove from A** |

### DID family

| Method / config | Maturity | Point estimand | Interval available | Interval estimand | Cal. eligibility | Run 001 | Path | Next validation | Recommendation |
|-----------------|----------|----------------|--------------------|-------------------|------------------|---------|------|-----------------|----------------|
| **DID** | expert_review | relative_att_post (point path) | cumulative / path y | cumulative_att | E for relative ATT | — | **B** + **C** | Pretrend contract tests; pooled point recovery | No relative-ATT nominal calibration |
| **DID_Bootstrap** | expert_review | relative_att_post (point) | Yes | cumulative_att | E (policy) | — | **C** | Bootstrap coverage on **cumulative** estimand | Cumulative-att calibration only if pursued |

### Research / other

| Method / config | Maturity | Point estimand | Interval available | Interval estimand | Cal. eligibility | Run 001 | Path | Next validation | Recommendation |
|-----------------|----------|----------------|--------------------|-------------------|------------------|---------|------|-----------------|----------------|
| **SyntheticDID** | research_only | relative_att_post (intended) | point only | — | E | — | **D** | Wire `RecoveryRunner`; staggered DGP tests | Characterize before calibration |
| **TROP** | research_only | relative_att_post | point only | — | E | — | **D** | Stabilize finite recovery smoke | Skip nominal calibration |
| **BayesianTBR** | research_only | varies | MCMC | bayesian | E | — | **D** | Optional-dep CI + convergence policy | Skip until wired |
| **BayesianTBRHorseShoe** | research_only | varies | MCMC | bayesian | E | — | **D** | Same | Skip |
| **MTGP** | research_only | varies | MCMC GP | bayesian | E | — | **D** | Performance + stability | Skip |

---

## Part B — Run 001 failure cross-reference

Detailed mechanism, evidence, and confidence: **`docs/CALIBRATION_FAILURE_ANALYSIS_001.md`**.

| Config | Symptom | Root cause (short) | Category |
|--------|---------|-------------------|----------|
| SCM_UnitJackKnife | power 0, coverage 1 | Wide jackknife CIs; point estimates accurate | inference (+ scenario pooling) |
| TBRRidge_BlockResidualBootstrap | FPR 1, coverage 0 | Inverted bootstrap `y_lower`/`y_upper` → wrong relative CI + always significant | inference |
| TBRRidge_Kfold | 100% failure | Multi-treated `(T, n_treated)` broadcast error in k-fold | geometry / inference |

---

## Roadmap impact (remove vs add)

### Remove from near-term relative-ATT nominal calibration

1. **TBRRidge_BlockResidualBootstrap** — demonstrated anti-calibration on Run 001; inverted bounds.  
2. **TBRRidge_Kfold** — non-functional on default recovery DGP.

### Keep (with conditions)

1. **SCM_UnitJackKnife** — null FPR/coverage acceptable for conservative monitoring; **not** sufficient for power claims.

### Do not add (unchanged stop list)

- Package-wide production_safe promotion  
- DID relative-ATT interval calibration  
- TROP / SDID / Bayesian MCMC nominal calibration without wiring and D path completion  

### Defer (later, not deleted from long-term roadmap)

- BRB / Kfold re-eligibility after **inference** fixes  
- Single-treated calibration scenario for power benchmarking (scenario addition, not estimator math)  
- Heterogeneous-effect documentation for pooled `_path_relative_att`

---

## Production calibration feasibility

| Question | Answer |
|----------|--------|
| Can we claim “aligned inference configs are nominally calibrated”? | **No** — 2/3 Run 001 configs fail or are ineligible. |
| Can expert-review use SCM + unit jackknife on similar panels? | **Yes, with caveats** — null FPR OK; treat power as unknown; expect wide CIs. |
| Can production-tier calibration complete without code changes? | **No** — BRB and Kfold require inference fixes or eligibility removal; SCM power needs interpretation or scenario change, not threshold tuning. |

---

## Recommended next implementation PR

**Title:** Tighten nominal calibration eligibility after Run 001 failure analysis

1. Update `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` in `panel_exp/validation/nominal_calibration.py` to **`SCM_UnitJackKnife` only** (or document equivalent allowlist).  
2. Update `docs/VALIDATION_COVERAGE.md` and `docs/ROADMAP_V3.md` Phase 5 notes to reference this plan and analysis.  
3. Adjust `tests/test_nominal_calibration_production.py` expectations for reduced allowlist.  
4. **Do not** schedule TBRRidge relative-ATT calibration at n≥100 until BRB bounds and Kfold multi-treated behavior are fixed in a dedicated inference PR.

Optional follow-up PRs (ordered):

1. Inference: BRB path bound ordering + alignment guard when `ci_lower > ci_upper`.  
2. Inference: Kfold multi-treated support **or** registered single-treated calibration scenario.  
3. Validation: jackknife width characterization vs donor/treated count (docs + tests).

---

## Quick reference — config disposition after Run 001

| Config | Relative-ATT nominal cal. | Primary path |
|--------|---------------------------|--------------|
| SCM_UnitJackKnife | **Keep** (null only) | A* |
| TBRRidge_BlockResidualBootstrap | **Remove** | B until inference fix |
| TBRRidge_Kfold | **Remove** on recovery_* | B / E; D for research |
| TBRRidge (point) | N/A | B |
| DID / DID_Bootstrap | N/A | B / C |
| All research-only estimators | N/A | D or E |

---

*Maturity labels remain authoritative in `panel_exp/method_metadata.py`. This plan governs validation **strategy**, not catalog promotion.*
