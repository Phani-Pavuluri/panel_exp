# GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001

## Artifact metadata

| Field | Value |
|-------|-------|
| **artifact_id** | `GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001` |
| **artifact_type** | `geox_trusted_readout_spend_readiness_integration_runtime` |
| **lane** | Lane B — Final trusted readout / spend / ROI readiness |
| **status** | completed |
| **scope** | `trusted_readout_spend_readiness_integration_no_roi_calculator_or_claim_authorization` |
| **final_verdict** | `trusted_readout_spend_readiness_integrated_no_roi_calculator_or_claim_authorization` |
| **module** | `panel_exp/validation/trusted_readout_spend_readiness_integration_runtime_001.py` |
| **recommended_next_artifact** | `GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001` |
| **return_to_lane_a_after** | `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001` |

## Why integration exists

`GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001` produces governed post-test spend evidence and a trusted-readout handoff packet. This runtime wires that handoff into the existing `TRUSTED_READOUT_REPORT_RUNTIME_001` output as optional spend/efficiency readiness sections — without recomputing spend_delta, computing ROI/ROAS, or duplicating claim authorization.

## Dependencies

- `GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001`
- `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001`
- `TRUSTED_READOUT_REPORT_RUNTIME_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`
- `MIP_GEOX_READOUT_INPUT_REQUIREMENTS_AND_HANDOFF_CONTRACT_001` (external MIP contract; no runtime call)

## Integration entry point

```python
from panel_exp.validation.trusted_readout_spend_readiness_integration_runtime_001 import (
    integrate_spend_readiness_into_trusted_readout,
    generate_trusted_readout_report_with_spend_readiness,
)
```

**Primary:** `integrate_spend_readiness_into_trusted_readout(trusted_readout, *, spend_evidence=None, spend_handoff=None) -> dict`

**Convenience:** `generate_trusted_readout_report_with_spend_readiness(input_data, *, spend_evidence=None, spend_handoff=None) -> dict`

Rules:

- If `spend_evidence` is provided, calls `build_trusted_readout_spend_handoff(spend_evidence)`.
- If `spend_handoff` is provided, uses it directly (validated).
- If neither is provided, attaches `NOT_REQUESTED` spend section.
- Preserves all existing trusted readout fields (copy semantics).
- Does not recompute `spend_delta`.

## Trusted readout extension fields

| Field | Source |
|-------|--------|
| `spend_readiness_summary` | Post-test spend adapter handoff |
| `post_test_spend_evidence` | Adapter handoff |
| `efficiency_metric_readiness` | Adapter handoff (`NOT_COMPUTED` for cost-per/ROAS/profit ROI) |
| `blocked_efficiency_metrics` | Adapter handoff |
| `diagnostic_efficiency_metrics` | Adapter handoff |
| `roi_claim_authorization_status` | Pass-through / `NOT_EVALUATED` |
| `spend_lineage` | Adapter handoff |
| `spend_warnings` | Adapter handoff |
| `spend_readiness_integrated` | `true` when handoff attached |
| `spend_readiness_source_artifact` | `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001` |
| `claim_authorization_owner` | `CLAIM_AUTHORIZATION_RUNTIME_001` |

## Behavior by spend evidence state

### Ready

- Spend sections attached with `readiness_status=READY`.
- `spend_delta` passed through from adapter evidence (not recomputed).
- KPI/trusted readout `report_status` unchanged.

### Blocked

- Blocking reasons and `blocked_efficiency_metrics` attached.
- `diagnostic_efficiency_metrics` may include `spend_delta`.
- KPI readout **not** blocked by missing/blocked spend.

### Missing

- `spend_readiness_summary.readiness_status = NOT_REQUESTED`.
- `spend_readiness_integrated = false`.
- KPI/lift readout fields preserved.

### Malformed handoff

- `readiness_status = BLOCKED_MALFORMED_SPEND_HANDOFF` with warnings.
- Trusted readout core packet preserved.

## Claim authorization delegation

- `roi_claim_authorization_status` remains `NOT_EVALUATED` (or pass-through if already on input).
- `claim_authorization_owner = CLAIM_AUTHORIZATION_RUNTIME_001`.
- Does not call or duplicate `authorize_readout_claims`.
- Does not authorize ROI, ROAS, business lift, decision recommendation, or production readout.

## MIP compatibility note

Integrated output exposes MIP-expected fields for future orchestration (no MIP runtime implemented here):

- `mip_post_test_spend_readiness_result`
- `mip_observed_spend_delta_readiness`
- `blocked_efficiency_metrics`
- `roi_claim_authorization_status`
- `spend_lineage` / provenance
- `spend_warnings`

## Non-goals

- No spend_delta recomputation
- No cost_per_incremental_kpi, ROAS, or profit_ROI computation
- No ROI calculator runtime
- No spend ingestion system or final-results module
- No claim authorization duplication
- No MIP orchestration or dataset loading
- No method/instrument promotion or catalog unblock

## Validation results

- `python -m pytest tests/validation/test_trusted_readout_spend_readiness_integration_runtime_001.py` — pass
- `python -m pytest tests/governance/test_geox_trusted_readout_spend_readiness_integration_runtime_001.py` — pass
- Summary JSON: `docs/track_d/archives/GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001_summary.json`

Forbidden flags (all false): `spend_delta_recomputed`, `cost_per_incremental_kpi_computed`, `roi_roas_computed`, `roi_calculator_runtime_created`, `spend_ingestion_system_created`, `final_results_module_created`, `claim_authorization_duplicated`, ROI/ROAS/business/decision/production claim authorization, method/instrument promotion, catalog unblock, MIP orchestration, dataset loading.

## Recommended next artifact

**Lane B preferred:** `GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001` — define cost-per/ROAS/profit ROI readiness mapping rules without computing numeric efficiency metrics.

**Lane A (parked):** `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001` — return after efficiency mapper contract or deliberate Lane B closeout.
