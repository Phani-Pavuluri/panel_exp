# Estimator Readout Guardrail Integration 001

**Artifact ID:** ESTIMATOR-READOUT-GUARDRAIL-INTEGRATION-001  
**Verdict:** `estimator_readout_guardrail_adapter_implemented_not_yet_mandatory`

## 1. Executive summary

Wires native estimator and inference result paths into the existing inference-boundary enforcement stack via a shared adapter. Governed readouts are available through `build_estimator_readout()` or `run_governed_analysis()`.

**Transitional rule:** `ImpactAnalyzer.run_analysis()` remains an **internal/native primitive**. It is **not** downstream-authorized. TrustReport, CalibrationSignal, MMM, LLM, and production-facing paths must consume `ReadoutEvidence` (see `DOWNSTREAM_READOUT_AUTHORIZATION_GATEWAY_001`).

## 2. Why inference-boundary code alone was insufficient

`INFERENCE-BOUNDARY-GUARDRAIL-ENFORCEMENT-001` required callers to supply estimator identity, inference identity, interval semantics, and scalar readout fields manually. Estimator execution paths (`ImpactAnalyzer.run_analysis`) returned native dicts without governed `ReadoutEvidence`.

## 3. Scope

- Automatic governed readout construction from native results
- Estimator/inference identity attachment from analyzer class and inference mode
- Design geometry propagation from `DesignEvidence`
- Per-cell metadata and multi-cell geometry handling
- Backward-compatible wrappers (`run_governed_analysis` additive; native `run_analysis` unchanged)

## 4. Non-goals

- Estimator or inference mathematics changes
- Production promotion
- TrustReport / CalibrationSignal / MMM / LLM integration
- Adapter or geometry bridge implementation
- Pooling multi-cell results

## 5. Architecture

```
DesignEvidence
  → estimator execution (optional via run_governed_analysis)
  → inference execution
  → estimator_readout_adapter_001.build_estimator_readout
  → readout_boundary_builder_001.build_guarded_readout
  → DCM resolution + inference-boundary enforcement
  → ReadoutEvidence
```

## 6. Design geometry versus estimator identity

Multi-cell is **design geometry** (`geometry_id=multi_cell_per_cell`), not an estimator. Estimator identity remains `scm`, `did`, etc. `cell_id`, `shared_control_policy`, and `control_reuse_policy` propagate from `design_contract.multi_cell`.

## 7. Estimator inventory

| Governed ID | Native classes | Registry |
|-------------|----------------|----------|
| `scm` | SyntheticControl, SyntheticControlCVXPY | SCM |
| `augsynth` | AugSynth, AugSynthCVXPY | AugSynth |
| `did` | DID | DID |
| `tbr` | TBR | TBR |
| `tbrridge` | TBRRidge | TBRRidge |

## 8. Inference inventory

| Governed ID | Native modes |
|-------------|--------------|
| `unit_jackknife` | UnitJackKnife |
| `placebo` | Placebo |
| `bootstrap` | DID embedded bootstrap |
| `brb` | BlockResidualBootstrap |
| `kfold` | Kfold, TimeSeriesKfold |
| `point_only` | point_estimate / none |

## 9. Native result inventory

| Estimator | Native keys adapted |
|-----------|---------------------|
| SCM/TBR/TBRRidge | `y`, `y_hat`, `y_lower`, `y_upper` → point + interval |
| AugSynth | `y`, `y_hat` → point only (no interval inference from dict fields) |
| DID | `cumulative_att`, `treatment_ci`, `treatment_pvalue` |

## 10. Shared adapter

`panel_exp/validation/estimator_readout_adapter_001.py`:

- `build_estimator_readout()` — primary API
- `run_governed_analysis()` — `run_analysis` + readout in one call
- `adapt_native_result_payload()` / `adapt_impact_analyzer_results()` — field mapping
- `extract_geometry_context()` — design geometry from evidence

Internally delegates to `build_guarded_readout()` only.

## 11–15. Method integration

- **SCM:** `unit_jackknife` / `placebo`; DCM-001 or DCM-008 (stratified); null-monitor explicit
- **AugSynth:** point-only default; interval claims BLOCK (DCM-002)
- **DID:** `bootstrap` identity; `treatment_ci` interval semantics
- **TBR:** aggregate geometry `aggregate_two_row`; unit-panel BLOCK (DCM-003)
- **TBRRidge:** BRB / KFold / placebo interval types preserved separately; DCM-005 (currently blocks research per registry)

## 16. Multi-cell geometry handling

Requires `cell_id`, `per_cell_effect` estimand, `pooled=False`. Pooled requests → DCM-007 BLOCK.

## 17–19. Readout / interval / estimand semantics

Explicit `readout_semantics` and `interval_type` required for interval claims. AugSynth does not infer uncertainty from incidental path bounds.

## 20. DCM resolution

Automatic via existing `resolve_design_combination()` inside `build_guarded_readout()`.

## 21. Enforcement behavior

Fail closed on BLOCK combinations. Research WARN does not authorize production. Adapter adds fail-closed checks for missing estimator identity and missing SCM inference on interval readouts.

## 22. Evidence serialization

`ReadoutEvidence` round-trips with `estimator_identity`, `inference_identity`, `combination_resolution`, `inference_boundary_guardrail`, `guardrail_enforcement`, `result_payload`.

## 23. Backward compatibility

`ImpactAnalyzer.run_analysis()` return shape unchanged and documented as **native/internal** in `panel_exp/impact.py`. Governed readout construction is **opt-in** via `run_governed_analysis()` or `build_estimator_readout()`. Track B bundle wiring emits `downstream_readout_not_authorized` when governed `ReadoutEvidence` is absent.

## 24. Fixture inventory

`tests/fixtures/artifact_schemas/estimator_readout_guardrail_integration_001/scenarios.json` — 16 scenarios.

## 25. Test coverage

`tests/validation/test_estimator_readout_guardrail_integration_001.py` — 43 tests.

## 26. Security/no-bypass properties

No `force=True`, `override_guardrail`, or `bypass_guardrail` APIs. Downstream roles blocked.

## 27. Current governance status

`estimator_readout_guardrail_adapter_implemented_not_yet_mandatory`

## 28. Remaining limitations

- Governed path not yet mandatory on all estimator entry points
- DCM-003/005 block research per current combination registry (statistical evidence gap, not adapter failure)
- TBRRidge/TBR aggregate paths wire correctly but guardrails fail closed

## 29. Follow-up work

- **`DOWNSTREAM_READOUT_AUTHORIZATION_GATEWAY_001`** — fail-closed gateway for TrustReport/CalibrationSignal/MMM/LLM
- Promote characterized combinations only after statistical validation artifacts complete

## 30. Verdict

**`estimator_readout_guardrail_adapter_implemented_not_yet_mandatory`**
