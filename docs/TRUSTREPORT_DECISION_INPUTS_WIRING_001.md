# TRUSTREPORT-DECISION-INPUTS-WIRING-001

**Document ID:** TRUSTREPORT-DECISION-INPUTS-WIRING-001  
**Type:** Product wiring — bundle metadata → F-DECISION → TrustReport  
**Status:** **complete**  
**Date:** 2026-06-03  
**Prerequisite:** TRUSTREPORT-F-DECISION-INTEGRATION-001 (`b0760f2`)

---

## 1. Summary

Representative Geo RunBundle exports can opt in to **`f_decision_context`** on TrustReport by setting:

```python
include_trust_report_decision_context=True
```

(requires `include_trust_report=True` and `include_track_b_views=True`).

Default remains **off** — legacy `trust_report_view` shape unchanged.

---

## 2. Wiring module

[`panel_exp/track_b/readout_evidence_wiring.py`](../panel_exp/track_b/readout_evidence_wiring.py)

| Function | Role |
|----------|------|
| `extract_readout_evidence_from_bundle` | Build readout evidence dicts + warnings |
| `build_decision_profiles_from_bundle` | Design / data / geometry / estimand profiles |
| `build_trust_report_decision_inputs_from_bundle` | Full `TrustReportDecisionInputs` |

---

## 3. Metadata sources (no inference)

| Priority | Source |
|----------|--------|
| 1 | `track_b_export_hints.readout_evidence` or `decision_readout_evidence` |
| 2 | `inference_metadata.readout_evidence` / `artifacts.readout_evidence` |
| 3 | Primary run: `inference_metadata` + hints + extracted `config_alias` |

**Per-record fields (when present):**  
`estimator_name`, `inference_mode`, `track_b_config_alias`, `audit_010_primary_bucket`, `point_effect` / `point_estimate`, `falsification_passed`, `interval_readout` or `interval_readout_snapshot`, `geometry_mode`, `callable`.

Missing required keys → `decision_context_incomplete` warning (not guessed).

---

## 4. Export API flags

Threaded through:

- `export_geo_run_bundle` / `build_geo_run_artifact_bundle`
- `build_run_artifact_bundle`
- `build_track_b_views` / `build_track_b_views_from_bundle`

| Flag | Default |
|------|---------|
| `include_trust_report_decision_context` | `False` |
| `trust_report_decision_inputs_strict` | `False` (raise on incomplete metadata) |

---

## 5. Example

```python
from panel_exp.artifacts.geo_run_export import export_geo_run_bundle

bundle = export_geo_run_bundle(
    evidence=evidence_dict,
    include_track_b_views=True,
    include_trust_report=True,
    include_trust_report_decision_context=True,
    trust_report_scenarios=scenarios,
)
fdc = bundle.to_dict()["track_b_views"]["trust_report_view"]["f_decision_context"]
```

---

## 6. Guardrails (unchanged)

- No estimator / inference / OC changes  
- No method reclassification beyond F-DECISION-001  
- No CalibrationSignal / MMM / promotion expansion  
- `promotion_candidates` always `[]` on export

---

*TRUSTREPORT-DECISION-INPUTS-WIRING-001 v1.0.0*
