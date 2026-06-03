# TRUSTREPORT-F-DECISION-INTEGRATION-001

**Document ID:** TRUSTREPORT-F-DECISION-INTEGRATION-001  
**Type:** TrustReport integration — consumes F-DECISION-001  
**Status:** **complete**  
**Date:** 2026-06-03  
**Prerequisite:** GOVERNANCE-PR-TRACK-F-DECISION-PACKAGE-001 (`9cfbd5a`) · F-DECISION-001 (`637bb29`)

---

## 1. Summary

TrustReport optionally attaches an **`f_decision_context`** block built from F-DECISION-001 (`resolve_eligible_readouts`, `build_evidence_decision`). Legacy TrustReport exports are **unchanged** when decision inputs are omitted.

| Layer | Module |
|-------|--------|
| Builder | [`panel_exp/track_b/f_decision_context.py`](../panel_exp/track_b/f_decision_context.py) |
| Composer hook | [`panel_exp/track_b/trust_report.py`](../panel_exp/track_b/trust_report.py) |
| Tests | [`tests/track_b/test_trustreport_f_decision_integration_001.py`](../tests/track_b/test_trustreport_f_decision_integration_001.py) |

---

## 2. Optional attachment API

### `TrustComposeContext`

| Field | Purpose |
|-------|---------|
| `decision_inputs` | `TrustReportDecisionInputs` — readout evidence + design/data/geometry/estimand profiles |
| `f_decision_context` | Pre-built context (skips builder; still runs guardrail asserts on attach) |

### `attach_trust_report_to_views`

Same optional kwargs: `decision_inputs`, `f_decision_context`.

### `TrustReportDecisionInputs`

| Field | Default |
|-------|---------|
| `readout_evidence` | Sequence of `CandidateReadout` or mappings |
| `design` / `data` / `geometry` / `estimand` | Unit-panel single-cell defaults |
| `strict` | `False` — incomplete specs warn; `True` raises |
| `allow_sensitivity_in_comparison` | `False` — A16/A21 stay `excluded` |

**Mapping keys (when not using `CandidateReadout`):**  
`estimator_name`, `inference_mode`, `geometry_mode`, `interval_readout`, `callable`, `audit_010_primary_bucket`, `point_effect`, `falsification_passed`, `track_b_config_alias`, `research_only`.

Missing `estimator_name` or `inference_mode` → `decision_context_incomplete` warning (no guessed eligibility).

---

## 3. Export shape (`f_decision_context`)

```json
{
  "eligible_readout_profiles": [],
  "evidence_decision_profile": {},
  "primary_readout": {},
  "diagnostic_comparators": [],
  "falsification_checks": [],
  "sensitivity_checks": [],
  "excluded_readouts": [],
  "blocked_readouts": [],
  "conflict_status": null,
  "agreement_status": "evidence_aligned_low_concern",
  "final_decision_posture": "proceed_with_confidence",
  "calibration_signal_action": "export_calibration_signal",
  "trust_report_action": "trust_report_only",
  "mmm_action": "exclude_from_mmm",
  "mmm_status": "not_ready_continue_track_f",
  "required_warnings": [],
  "recommended_next_action": "no_decision",
  "decision_context_complete": true,
  "promotion_candidates": []
}
```

`promotion_candidates` is **always empty** — explicit non-promotion signal.

---

## 4. Backward compatibility

| Rule | Enforcement |
|------|-------------|
| No decision inputs | No `f_decision_context` key in export |
| Scenario verdicts | Unchanged vs baseline (golden + E4 fixtures) |
| Strict mode | Opt-in only |
| Track B schema | Optional extension field only |

---

## 5. Guardrails (asserted at build time)

- `GOVERNED_UNCERTAINTY_EXPORT_ALLOWLIST` empty  
- A05/A18/A19 → `diagnostic_comparator` only when present  
- A16/A21 → `excluded` by default  
- Placebo → `falsification_check`  
- CalibrationSignal action only when primary SCM+JK eligible  
- `mmm_action` = `exclude_from_mmm`  
- `promotion_candidates` = `()`  
- No silent averaging (delegated to `build_evidence_decision`)

---

## 6. Example

```python
from panel_exp.track_b.trust_report import (
    TrustComposeContext,
    compose_trust_report,
    trust_report_to_dict,
)
from panel_exp.track_b.f_decision_context import TrustReportDecisionInputs

inputs = TrustReportDecisionInputs(readout_evidence=[...])
ctx = TrustComposeContext(
    spec=spec,
    adapter_output=adapter_output,
    decision_inputs=inputs,
)
report = trust_report_to_dict(compose_trust_report(ctx, scenarios))
assert "f_decision_context" in report
```

---

## 7. Non-goals (unchanged)

- Estimator / inference changes  
- OC batteries  
- Promotion / MMM ingress / CalibrationSignal expansion  
- Governed uncertainty allowlist changes  
- Automatic scenario verdict override from F-DECISION (context attachment only)

---

*TRUSTREPORT-F-DECISION-INTEGRATION-001 v1.0.0*
