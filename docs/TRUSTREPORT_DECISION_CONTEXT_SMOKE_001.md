# TRUSTREPORT-DECISION-CONTEXT-SMOKE-001

**Document ID:** TRUSTREPORT-DECISION-CONTEXT-SMOKE-001  
**Type:** End-to-end export smoke — usage proof only  
**Status:** **complete**  
**Date:** 2026-06-03  
**Prerequisites:** TRUSTREPORT-F-DECISION-INTEGRATION-001 · TRUSTREPORT-DECISION-INPUTS-WIRING-001

---

## 1. Purpose

Separate **smoke PR** from the integration PR. This document records a minimal proof that:

1. A realistic Geo RunBundle export produces `f_decision_context` when opted in.
2. The same export omits `f_decision_context` when the flag is off (legacy shape).
3. Guardrails appear correctly (no promotion, MMM excluded, CS primary-only).

**No** estimator, inference, OC, or method-reclassification work.

---

## 2. Fixtures

| ID | File | Role |
|----|------|------|
| **SMOKE-001** | [`tests/fixtures/trustreport_decision_context_smoke/smoke_001_geo_rep_with_comparators.json`](../tests/fixtures/trustreport_decision_context_smoke/smoke_001_geo_rep_with_comparators.json) | REP-001 lineage + explicit `readout_evidence` (SCM+JK primary, AugSynth/TBRRidge Conformal diagnostics) |
| **SMOKE-002** | [`tests/fixtures/trustreport_decision_context_smoke/smoke_002_incomplete_metadata.json`](../tests/fixtures/trustreport_decision_context_smoke/smoke_002_incomplete_metadata.json) | Unmapped TBR pair → `decision_context_incomplete` warning |

---

## 3. Tests

[`tests/track_b/test_trustreport_decision_context_smoke_001.py`](../tests/track_b/test_trustreport_decision_context_smoke_001.py)

```bash
pytest tests/track_b/test_trustreport_decision_context_smoke_001.py -v
```

Regenerate committed golden excerpt:

```bash
python tests/track_b/test_trustreport_decision_context_smoke_001.py
```

---

## 4. Export flags (SMOKE-001)

```python
export_geo_run_bundle(
    evidence=smoke["evidence"],
    include_track_b_views=True,
    include_trust_report=True,
    include_trust_report_decision_context=True,
    trust_report_scenarios=smoke["trust_scenarios"],
)
```

**Opt-out:** set `include_trust_report_decision_context=False` (default) → `trust_report_view` has no `f_decision_context`.

---

## 5. Committed example artifact

[`docs/track_b/archives/TRUSTREPORT_DECISION_CONTEXT_SMOKE_001_export.json`](track_b/archives/TRUSTREPORT_DECISION_CONTEXT_SMOKE_001_export.json) — trimmed `f_decision_context` excerpt from SMOKE-001 export.

**Observed (SMOKE-001):**

| Check | Value |
|-------|--------|
| `primary_readout.assigned_role` | `primary_null_monitor` |
| `calibration_signal_action` | `export_calibration_signal` |
| `mmm_action` | `exclude_from_mmm` |
| `mmm_status` | `not_ready_continue_track_f` |
| `promotion_candidates` | `[]` |
| Diagnostic comparators | AugSynthCVXPY+Conformal, TBRRidge+Conformal |
| Flag off | no `f_decision_context` key |

---

## 6. Non-goals

- Estimator / inference changes  
- OC batteries  
- Promotion / MMM / CalibrationSignal expansion  
- Method reclassification  

---

*TRUSTREPORT-DECISION-CONTEXT-SMOKE-001 v1.0.0 — usage proof only.*
