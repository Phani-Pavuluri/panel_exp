# AUDIT-008 — Track D D4 power and MDE gate

**Audit ID:** AUDIT-008  
**Date:** 2026-06-01  
**Lane:** Research / robustness  
**Baseline commit:** `24beae8`  
**Primary report:** [`TRACK_D_D4_POWER_MDE_AUDIT_001.md`](../TRACK_D_D4_POWER_MDE_AUDIT_001.md)

---

## Scope

Track D D4 — power/MDE methods (POW-001–006), estimand alignment, design geometry, inference/readout coupling, Track E suitability links.

## Stop conditions

| Criterion | Met |
|-----------|-----|
| D4 ADR audit committed | Yes |
| POW rows explicit statuses | Yes |
| D5 power OC specs defined | Yes |
| No production behavior changes | Yes |

## Verdict

**`continue_with_characterization_required`**

## Top findings

1. **D4-FIND-001** — Default geo power uses TBRRidge+Kfold, not SCM JK readout.  
2. **D4-FIND-002** — Two-row treated/control aggregation.  
3. **D4-FIND-003** — `mde_percent` ≠ registry relative ATT without bridge.

## Next

Track E E1; D5-POW-001e; broader D5 OC — not MMM integration.

## D5-POW-001d follow-up (2026-06-01)

**Artifact:** [`D5_POW_001d_results.json`](../track_d/archives/D5_POW_001d_results.json)  
**Verdict:** **`fixed_window_preferred`** — window sensitivity characterized; E-POW-WIN-* suitability diagnostics for Track E.

## D5-POW-001c follow-up (2026-06-01)

**Artifact:** [`D5_POW_001c_results.json`](../track_d/archives/D5_POW_001c_results.json)  
**Verdict:** **`narrow_diagnostics_only`** — 2-row aggregation preserves assignment but not unit readout scale; SCM+JK infeasible on agg panel.

## D5-POW-001b follow-up (2026-06-01)

**Artifact:** [`D5_POW_001b_results.json`](../track_d/archives/D5_POW_001b_results.json)  
**Verdict:** **`null_monitor_only`** — interval-excludes-zero invalid for SCM+JK power/MDE; 001a degeneracy = harness endpoint swap.

## D5-POW-001a follow-up (2026-06-01)

**Artifact:** [`D5_POW_001a_results.json`](../track_d/archives/D5_POW_001a_results.json)  
**Proxy verdict:** **`optimistic_proxy`** — geo `mde_percent` understates SCM+JK interval-detection MDE on matched assignment; not feasibility evidence for governed readout.

---

*AUDIT-008 v1.0.1 — D5-POW-001a characterized (research lane)*
