# D5-INF-POSTFIX-001 — Post F-INF-003 targeted OC (A05, A19)

**Artifact:** [`archives/D5_INF_POSTFIX_001_results.json`](archives/D5_INF_POSTFIX_001_results.json)  
**Harness:** [`panel_exp/validation/track_d_d5_inf_postfix_001.py`](../../panel_exp/validation/track_d_d5_inf_postfix_001.py)  
**Prerequisite:** F-INF-003 interval orientation fix  
**Verdict:** **`remain_restricted_no_promotion`** — structural intervals fixed; behavioral null FPR acceptable on battery; **not** governed uncertainty

---

## Scope

| Tuple | Estimator | Inference | Geometry | Prior battery |
|-------|-----------|-----------|----------|---------------|
| **A05** | AugSynthCVXPY | Conformal | single_cell + k=2 per-cell | D5-INST-AUGSYNTH-003 |
| **A19** | TBRRidge | TimeSeriesKfold | single_cell (001e) | D5-INST-TBRRIDGE-002 |

No other Appendix A rows rerun. No promotion, MMM, or CalibrationSignal expansion.

---

## Pre-fix vs post-fix (single-cell null, n_mc=14)

| Metric | A05 pre (AUGSYNTH-003) | A05 post | A19 pre (TBRRIDGE-002) | A19 post |
|--------|------------------------|----------|------------------------|----------|
| Feasibility | 100% | 100% | 100% | 100% |
| Negative HW rate | **100%** | **0%** | **100%** | **0%** |
| Inverted bound rate | **100%** | **0%** | **100%** | **0%** |
| Null interval-exclusion FPR | **100%** | **0%** | **100%** | **0%** |
| Mean half-width | −8.19 | +8.16 | −21.60 | +25.38 |

**Interpretation:** F-INF-003 corrected effect-scale → outcome mapping. Prior 100% null exclusion was largely an artifact of inverted/negative bands (intervals excluded zero trivially). Post-fix bands are structurally valid; null FPR on this battery is 0% for both tuples.

**Caveat:** Point estimates on TBRRidge+TSKF remain large negative level effects (~−400) — scale ≠ SCM+JK; restricted diagnostic only.

---

## Postfix disposition (F-INF-001 classifier unchanged)

| Tuple | Disposition | F-INF classification | Governed uncertainty |
|-------|-------------|----------------------|----------------------|
| **A05** | `diagnostic_interval_only` | `diagnostic_interval_only` | No |
| **A19** | `diagnostic_interval_only` | `diagnostic_interval_only` | No |

Not `callable_unverified_interval_semantics` after OC — structural and null-FPR gates pass on this battery. Still **not** promotion or CalibrationSignal.

---

## AUDIT-010 Appendix A updates

| Row | Prior primary bucket | Post OC primary bucket | D5 OC |
|-----|---------------------|------------------------|-------|
| **A05** | `callable_unverified_interval_semantics` | **`characterized_restricted`** | **INF-POSTFIX-001** ✅ |
| **A19** | `callable_unverified_interval_semantics` | **`characterized_restricted`** | **INF-POSTFIX-001** ✅ |

Roll-up: `callable_unverified_interval_semantics` → 0 tuples; `characterized_restricted` gains A05 + A19 (5 total with A03, A07, A10).

---

## Governance (unchanged)

- **Promotion:** not authorized  
- **CalibrationSignal:** `SCM_UnitJackKnife` only — unchanged  
- **MMM ingress:** blocked (`not_ready_continue_track_f`)

---

## Next authorized Track F step

**F-INF-002** — TBRRidge multi-treated interface fix (A16, A18, A21 blocked_interface). A05/A19 do not require further interval-orientation work.

---

## Findings

1. **D5-POSTFIX-FIND-001:** F-INF-003 eliminated negative half-width and inverted bounds on A05/A19 fixtures (100% → 0%).
2. **D5-POSTFIX-FIND-002:** Null interval-exclusion FPR dropped from 100% to 0% on null battery — prior FPR was confounded with band inversion, not independent behavioral failure.
3. **D5-POSTFIX-FIND-003:** Safe classification is **restricted diagnostic** — intervals are not governed uncertainty and must not feed MMM or CalibrationSignal.

---

*D5-INF-POSTFIX-001 — targeted OC complete; A05/A19 structurally valid; remain restricted.*
