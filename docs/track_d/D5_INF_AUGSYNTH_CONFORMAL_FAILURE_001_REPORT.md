# D5-INF-AUGSYNTH-CONFORMAL-FAILURE-001 — AugSynth+Conformal failure analysis

**Artifact:** [`archives/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_results.json`](archives/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inf_augsynth_conformal_failure_001.py`  

**Overall verdict:** `conformal_blocked_pending_new_design`  
**Runtime (s):** `1154.3`  

## 1. Purpose

Isolate and document **AugSynth+Conformal** failure modes after ASCM-003 and JK calibration. Determine whether failure is due to geometry, exchangeability violations, shocks, weak prefit, hull stress, or interval construction — **without promotion or governed-uncertainty change**.

## 2. Prior evidence from ASCM-002/003 and JK calibration

- `D5-INST-AUGSYNTH-ASCM-003` verdict: `promising_needs_inference_calibration`
- `D5-INF-AUGSYNTH-JK-CALIBRATION-001` verdict: `jk_unsafe_under_diagnostics`
- ASCM-003: AugSynth+Conformal retains **elevated null interval-exclusion FPR** on multiple worlds.
- JK calibration: AugSynth+JK unsafe under post-period shock (`W8`); Conformal historically worse than JK.

## 3. Design

- Monte Carlo: **n_mc=4** (target 8; reduction: 19-world conformal failure grid runtime; harness default n_mc=8 for replay)
- Worlds: **19** (ASCM-003 registry)
- Effect calibration level: **0.08**
- Primary failure target: `augsynth_cvxpy_conformal`

## 4. Worlds / strata

ASCM-003 worlds plus diagnostic strata: prefit, hull, donor pool, weak-fit severity, method disagreement, post-shock vs no-shock.

## 5. Methods compared

| Arm | Role |
|-----|------|
| `a26_scm_unit_jackknife` | Governed null-monitor reference |
| `augsynth_cvxpy_unit_jackknife` | JK comparator (JK-calibration context) |
| `augsynth_cvxpy_point` | Point comparator / disagreement anchor |
| `augsynth_cvxpy_conformal` | **Failure-analysis target** |

## 6. Diagnostics used

D5-DIAG panel fields, instrument false-confidence flags, null-world `conflict_vs_a26`, conformal semantics from D5-INST-AUGSYNTH-003.

## 7. Null FPR

| arm | mean null interval-exclusion FPR |
|-----|----------------------------------|
| A26 JK | 0.0 |
| AugSynth JK | 0.014492753623188406 |
| AugSynth Conformal | 0.014492753623188406 |

Severe worlds (FPR ≥ 0.5): `[]`  
Concerning worlds (FPR ≥ 0.35): `[]`

## 8. Effect coverage

@ 0.08:

| arm | mean covers injected effect |
|-----|----------------------------|
| A26 JK | 1.0 |
| AugSynth JK | 0.9848484848484849 |
| AugSynth Conformal | — |

## 9. Interval width / degeneracy

- Conformal mean half-width @ null: `322.99202227964884`
- Degenerate interval rate: `0.0`
- Negative half-width rate: `0.0`
- Over-wide interval rate (≥15.0): `0.2236842105263158`

## 10. Failure stratification

See artifact `failure_strata.at_null` for conformal vs JK vs A26 JK by stratum.

**prefit:**
- `good_prefit` conformal null FPR: `0.015151515151515152`
- `poor_prefit` conformal null FPR: `0.0`
- `unknown_prefit` conformal null FPR: `—`

**hull:**
- `inside_hull` conformal null FPR: `0.0`
- `other` conformal null FPR: `0.043478260869565216`
- `outside_hull` conformal null FPR: `0.0`

**post_shock:**
- `no_shock` conformal null FPR: `0.015384615384615385`
- `post_shock` conformal null FPR: `0.0`

**method_disagreement:**
- `high_disagreement` conformal null FPR: `0.017543859649122806`
- `low_disagreement` conformal null FPR: `0.0`

## 11. Likely failure mechanisms

Ranked: `['conformal_band_construction_mismatch', 'residual_exchangeability_failure']`

- **conformal_band_construction_mismatch**: over-wide interval rate 0.22; mean conformal/A26 half-width ratio 21.5
- **residual_exchangeability_failure**: pre-period residual calibration pool mismatched to post-period scale

## 12. Comparison to JK

JK null FPR generally lower than Conformal on the same worlds; JK shows shock sensitivity (`W8`) while Conformal shows broader elevated FPR consistent with exchangeability / calibration-set mismatch.

## 13. Verdict

**`conformal_blocked_pending_new_design`** — Conformal remains **restricted**; not added to governed uncertainty.

## 14. Guardrails

| Guardrail | Status |
|-----------|--------|
| Promotion | **No** |
| Governed uncertainty allowlist | **No change** |
| Inference behavior change | **No** |

## 15. Next step

If `conformal_blocked_pending_new_design`: do not invest in current conformal.py pairing without new exchangeability-aware design. If `conformal_remains_restricted`: keep A05 characterized_restricted; continue JK comparator lane (P4 follow-up).

## Findings

- **D5-CFFAIL-FIND-001**: Conformal failure battery on 19 worlds (n_mc=4) after ASCM-003 and JK calibration.
- **D5-CFFAIL-FIND-002**: Mean conformal null FPR: 0.013888888888888888; severe worlds (>=0.5): 0; concerning (>=0.35): 0.
- **D5-CFFAIL-FIND-003**: Likely mechanisms (ranked): ['conformal_band_construction_mismatch', 'residual_exchangeability_failure'].
- **D5-CFFAIL-FIND-003b**: Conformal/A26 mean half-width ratio: 60.49729542103188; over-wide interval rate: 0.2236842105263158.
- **D5-CFFAIL-FIND-004** (info): n_mc=4; 19-world conformal failure grid runtime; harness default n_mc=8 for replay
- **D5-CFFAIL-FIND-006**: Null FPR low (0.013888888888888888) but intervals unusably wide (HW ratio 60.5 vs A26).

