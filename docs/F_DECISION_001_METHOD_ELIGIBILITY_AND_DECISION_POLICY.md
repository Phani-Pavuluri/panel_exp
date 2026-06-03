# F-DECISION-001 — Method eligibility resolver and evidence decision policy

**Status:** Complete (policy layer)  
**Code:** [`panel_exp/governance/decision_policy.py`](../panel_exp/governance/decision_policy.py)  
**Tests:** [`tests/governance/test_f_decision_001_decision_policy.py`](../tests/governance/test_f_decision_001_decision_policy.py)  
**Prerequisite:** TRACK-F-IMPLEMENTATION-CHECKPOINT-001 (`9ed6b5d`)

---

## Why this layer exists

Track F (F-INF / F-GEO / F-CAT / OC batteries) answers: *Is this estimator × inference tuple structurally valid, geometry-allowed, and catalog-consistent?*

It does **not** answer:

- Which readouts may be used together for a **given experiment design**
- What **role** each allowed readout plays (null monitor vs diagnostic vs falsification)
- How to **compare** evidence without silent averaging
- What **decision posture** TrustReport / decision support should emit

**F-DECISION-001** is that higher layer. It **consumes** governance contracts; it does **not** re-run estimators or weaken Track F classifications.

---

## Inputs

| Profile | Fields |
|---------|--------|
| **DesignProfile** | `design_method_id`, `track_b_allows_primary_null_monitor`, `pooling_rule_id` |
| **DataProfile** | `n_treated`, `n_control`, `n_test_grps` |
| **GeometryProfile** | `geometry_type`, adapter/bridge ids, `pooled_claim`, `single_treated_geometry` |
| **EstimandProfile** | `target_estimand` |
| **CandidateReadout** | `estimator_name`, `inference_mode`, optional `IntervalReadout`, `audit_010_primary_bucket`, `point_effect`, falsification outcomes, Track B alias |

Resolver gates (order):

1. **F-GEO-001** — `classify_geometry_support` (geometry blocks first)
2. **F-INF-001** — `classify_interval_semantics` + `assert_not_governed_uncertainty`
3. **F-CAT / E5** — `track_b_alias_governance`, INV-015 production blocks
4. **AUDIT-010 buckets** — `AUDIT_010_DECISION_BUCKETS` for post-checkpoint tuples (A05, A16, A18, A19, A21, …)
5. **Role assignment** — decision taxonomy below

---

## Role taxonomy

| Role | Meaning |
|------|---------|
| `primary_null_monitor` | SCM + UnitJackKnife on unit panel when Track B policy allows — **null_monitor_only**, not MMM lift |
| `diagnostic_comparator` | Characterized restricted readouts (e.g. A05, A18, A19) — compare direction only |
| `falsification_check` | Placebo (inference layer on SCM estimator) — not an estimator |
| `sensitivity_check` | Callable-unverified (optional policy flag; default **excluded**) |
| `excluded` | Callable-unverified by default (A16, A21), invalid intervals, not runnable |
| `blocked` | Geometry / pooling / adapter / TBR-on-unit-panel |
| `research_only` | TROP, BayesianTBR MCMC paths |

**Hard rules:**

- No `governed_uncertainty` unless `GOVERNED_UNCERTAINTY_EXPORT_ALLOWLIST` permits (currently **empty**).
- No CalibrationSignal except `SCM_UnitJackKnife` governed alias.
- No MMM readiness (`MMM_READINESS_GOVERNED_ALIASES` empty; status `not_ready_continue_track_f`).

---

## Evidence comparison policy

`build_evidence_decision` compares **role-eligible** readouts using **signed point effects** — **no silent averaging**.

| Agreement status | When |
|------------------|------|
| `evidence_aligned_low_concern` | Primary and diagnostics same sign (or diagnostics absent) |
| `evidence_aligned_positive_with_caveats` | Aligned positive with diagnostic support |
| `diagnostic_disagreement` | Primary vs diagnostic sign mismatch → TrustReport warning |
| `falsification_failure` | Placebo/falsification failed → block posture |
| `insufficient_valid_evidence` | No primary null monitor |
| `blocked_for_decision_use` | Falsification failure or policy block |

| Decision posture | When |
|------------------|------|
| `proceed_with_confidence` | Primary only, low concern |
| `proceed_with_caveats` | Diagnostic disagreement or caveats |
| `diagnostic_only` | Diagnostics only, no primary |
| `trust_report_only` | Default safe export |
| `blocked_for_decision_use` | Falsification failed |
| `inconclusive` | No primary |

| Action | Policy |
|--------|--------|
| `calibration_signal_action` | `export_calibration_signal` **only** for governed SCM+JK primary |
| `mmm_action` | Always `exclude_from_mmm` |
| `trust_report_action` | `emit_warning` on conflict; else `trust_report_only` |

---

## Examples

### Single-cell unit panel (001e)

- **SCM + UnitJackKnife** → `primary_null_monitor`
- **AugSynthCVXPY / TBRRidge + Conformal** (A05, A18) → `diagnostic_comparator`
- **TBRRidge + TimeSeriesKfold** (A19) → `diagnostic_comparator`
- **TBRRidge + UnitJackKnife / JKP** (A16, A21) → `excluded` (callable-unverified)

### Multi-treated

Same roles; geometry `UNIT_PANEL` with `n_treated > 1`. Placebo blocked unless `single_treated_geometry`.

### Multi-cell

- **Per-cell** — follow single-cell row per cell (no pooling claim).
- **Pooled multi-cell** — `blocked` without `pooling_rule_id` (F-P0-006).

### Aggregate class TBR

- **Unit panel** → `blocked` (requires aggregate 1×1).
- **Aggregate 1×1** → diagnostic / unverified (A09 JKP) — not primary.

### Supergeo / trim

- **Supergeo** → `blocked` without `supergeo_adapter_id`
- **Trimmed** → `blocked` without `trim_estimand_bridge_id`

---

## Explicit non-goals

- Estimator or inference rewrites
- New OC batteries
- Promotion, MMM ingestion, CalibrationSignal expansion
- TrustReport schema changes (policy outputs only)
- Changing AUDIT-010 Appendix A buckets for A05/A16/A18/A19/A21
- Silent averaging of point estimates across methods

---

## Next steps (program)

1. **Governance PR** — package Track F checkpoint + F-DECISION-001 as decision-safe layer
2. Wire resolver outputs into TrustReport / decision support (separate integration PR)
3. Optional **F-INF-004** (A09) only on product pull
4. Design ADRs: supergeo, trim, pooling (parallel)

---

*F-DECISION-001 v1.0.0 — resolver/policy only; consumes Track F contracts.*
