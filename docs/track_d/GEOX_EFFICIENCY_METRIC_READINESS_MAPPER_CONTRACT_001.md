# GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001` |
| **Artifact type** | `geox_efficiency_metric_readiness_mapper_contract` |
| **Lane** | **Lane B — Final trusted readout / spend / ROI readiness** |
| **Status** | `completed` |
| **Base commit** | `9039fda` |
| **Scope** | `efficiency_metric_readiness_mapping_contract_defined_no_runtime_or_claim_authorization` |
| **Final verdict** | `efficiency_metric_readiness_mapping_contract_defined_no_runtime_or_claim_authorization` |
| **Recommended next** | `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001` (Lane A) |
| **Optional future runtime** | `GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_RUNTIME_001` |

**Depends on:**

- `GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001`
- `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001`
- `GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001`
- `TRUSTED_READOUT_REPORT_CONTRACT_001` / `TRUSTED_READOUT_REPORT_RUNTIME_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`
- `TRACK_B_ESTIMAND_REGISTRY_001`
- `INFERENCE_READOUT_SEMANTICS_001`

---

## 2. Why this contract exists

Lane B now has executable and integrated post-test spend readiness:

- `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001` derives observed `PostTestSpendEvidence` and `spend_delta` readiness.
- `GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001` attaches spend readiness sections to trusted readout output.
- Trusted readout can carry `spend_delta` readiness, `blocked_efficiency_metrics`, lineage, warnings, and claim-authorization pass-through.

The remaining gap is a **formal semantic mapping** for efficiency metrics — cost-per, ROAS, profit ROI — including which inputs are required, which readiness statuses apply when inputs are missing, and how numeric readiness differs from claim authorization. Without this contract, a future runtime could invent inconsistent formulas or conflate “computable” with “claim-authorized.”

This artifact is **contract-only**. It defines mapping rules; it does not compute metrics or authorize claims.

---

## 3. Explicit reuse decision

### Reuses

| Owner | Role |
|-------|------|
| `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001` | `spend_delta`, spend readiness status, spend lineage |
| `GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001` | Trusted readout attachment of spend sections |
| `TRUSTED_READOUT_REPORT_*` | Report assembly and section redaction policy |
| `TRACK_B_ESTIMAND_REGISTRY_001` | Metric and estimand definitions (`delta_mu`, lift, ROI estimands) |
| `INFERENCE_READOUT_SEMANTICS_001` | Observed/counterfactual/delta semantics |
| `CLAIM_AUTHORIZATION_RUNTIME_001` | Sole package-level claim authorization owner |

### Does not create

- ROI calculator runtime
- Final-results module
- Spend ingestion system
- Claim authorization runtime
- MIP orchestration runtime
- Trusted readout integration duplicate

**Reuse verdict:** `EXTEND_EXISTING_ARTIFACT` — map readiness onto integrated trusted readout + spend evidence chain.

---

## 4. Efficiency metric readiness inputs

### Estimator / readout inputs

| Field | Description |
|-------|-------------|
| `delta_mu` | Governed incremental KPI effect (point estimate) |
| `counterfactual_kpi` | Baseline/counterfactual KPI level for lift denominator |
| `observed_kpi` | Observed KPI level when needed for diagnostics |
| `kpi_metric_name` | Declared KPI name |
| `kpi_unit` | Unit of KPI (count, revenue, etc.) |
| `inference_readout_status` | Estimator/inference execution status |
| `uncertainty_available` | Whether governed interval/uncertainty exists (diagnostic only) |

### Spend inputs (from post-test spend adapter / integration)

| Field | Description |
|-------|-------------|
| `spend_delta` | Observed post-test spend contrast |
| `spend_delta_definition` | Experiment-type formula identifier |
| `spend_baseline_policy` | Baseline/counterfactual spend policy |
| `spend_readiness_status` | `PostTestSpendReadinessStatus` from adapter |
| `spend_lineage` | Profiler/adapter provenance |
| `currency` | Spend currency |

### Value / margin inputs

| Field | Description |
|-------|-------------|
| `value_per_incremental_kpi` | Revenue (or value) per incremental KPI unit |
| `incremental_revenue` | Pre-derived revenue increment |
| `revenue_metric_delta_mu` | `delta_mu` when KPI is already revenue |
| `margin_rate` | Profit margin rate on incremental revenue |
| `profit_per_incremental_kpi` | Profit per incremental KPI unit |
| `incremental_profit` | Pre-derived profit increment |
| `value_source` | Mapping provenance (user, MMM, default) |
| `margin_source` | Margin mapping provenance |
| `currency_compatible` | KPI value currency matches spend currency |

### Claim / trust inputs

| Field | Description |
|-------|-------------|
| `claim_authorization_status` | Per-claim-type status from claim authorization runtime |
| `trusted_readout_status` | Trusted report readiness |
| `blocked_claims` | Claim types blocked upstream |
| `warnings` | Advisory flags |

---

## 5. Metric readiness mapping table

| Metric | Numeric formula | Required inputs | Readiness if ready | Blocked if missing |
|--------|-----------------|-----------------|--------------------|--------------------|
| `absolute_increment` | `delta_mu` | `delta_mu` | `READY_NUMERIC_ONLY` | `BLOCKED_MISSING_DELTA_MU` |
| `lift_pct` | `delta_mu / counterfactual_kpi` | `delta_mu`, `counterfactual_kpi` | `READY_NUMERIC_ONLY` | `BLOCKED_MISSING_COUNTERFACTUAL` |
| `cost_per_incremental_kpi` | `spend_delta / delta_mu` | `spend_delta`, `delta_mu` | `READY_NUMERIC_ONLY` | `BLOCKED_MISSING_SPEND_DELTA_OR_DELTA_MU` |
| `incremental_revenue` | `delta_mu * value_per_incremental_kpi` **or** `revenue_metric_delta_mu` | `delta_mu` + value mapping **or** revenue KPI `delta_mu` | `READY_NUMERIC_ONLY` | `BLOCKED_MISSING_VALUE_MAPPING` |
| `ROAS` | `incremental_revenue / spend_delta` | `incremental_revenue`, `spend_delta` | `READY_NUMERIC_ONLY` | `BLOCKED_MISSING_REVENUE_OR_SPEND` |
| `incremental_profit` | `incremental_revenue * margin_rate` **or** `delta_mu * profit_per_incremental_kpi` | revenue/value + margin **or** profit mapping | `READY_NUMERIC_ONLY` | `BLOCKED_MISSING_MARGIN_MAPPING` |
| `profit_ROI` | `incremental_profit / spend_delta` | `incremental_profit`, `spend_delta` | `READY_NUMERIC_ONLY` | `BLOCKED_MISSING_PROFIT_OR_SPEND` |

**Notes:**

- Formulas describe **readiness preconditions** for a future mapper runtime; this contract does not compute numeric outputs.
- `spend_delta` must come from `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001` with `spend_readiness_status=READY`; otherwise efficiency metrics that require spend are blocked at spend layer first.
- Division-by-zero and sign conventions are runtime concerns; mapper runtime must emit warnings, not authorize claims.

---

## 6. Readiness status enum

| Status | Meaning |
|--------|---------|
| `READY_NUMERIC_ONLY` | Required inputs present; metric may be computed numerically (not claim-authorized) |
| `READY_DIAGNOSTIC_ONLY` | Metric allowed for diagnostic display only |
| `NOT_REQUESTED` | User/MIP did not request this efficiency metric |
| `NOT_COMPUTED` | Contract/runtime has not evaluated this metric |
| `PARTIAL_DIAGNOSTIC_ONLY` | Some inputs present; diagnostic subset only |
| `BLOCKED_MISSING_DELTA_MU` | Missing `delta_mu` |
| `BLOCKED_MISSING_COUNTERFACTUAL` | Missing `counterfactual_kpi` for lift |
| `BLOCKED_MISSING_SPEND_DELTA` | Missing observed `spend_delta` |
| `BLOCKED_MISSING_SPEND_DELTA_OR_DELTA_MU` | Missing spend or KPI increment |
| `BLOCKED_MISSING_VALUE_MAPPING` | Missing value/revenue mapping |
| `BLOCKED_MISSING_MARGIN_MAPPING` | Missing margin/profit mapping |
| `BLOCKED_MISSING_REVENUE_OR_SPEND` | Missing incremental revenue or spend_delta |
| `BLOCKED_MISSING_PROFIT_OR_SPEND` | Missing incremental profit or spend_delta |
| `BLOCKED_CURRENCY_MISMATCH` | Spend and value currencies incompatible |
| `BLOCKED_INCOMPATIBLE_TIME_WINDOW` | KPI and spend windows misaligned |
| `BLOCKED_INCOMPATIBLE_SCOPE` | Geo/cell scope mismatch across inputs |
| `BLOCKED_CLAIM_NOT_AUTHORIZED` | Inputs sufficient but claim type blocked |
| `BLOCKED_TRUSTED_READOUT_NOT_AVAILABLE` | Trusted readout packet not ready |

---

## 7. Numeric readiness vs claim authorization

| Concept | Definition |
|---------|------------|
| **Numeric readiness** | Required inputs are present and consistent enough to calculate a metric value |
| **Claim authorization** | Package is allowed to present that metric as an authorized claim in trusted readout |

**Rules:**

1. Numeric readiness **never implies** `ROI_CLAIM`, `ROAS_CLAIM`, `BUSINESS_LIFT_CLAIM`, `DECISION_RECOMMENDATION`, or `PRODUCTION_READOUT` authorization.
2. `CLAIM_AUTHORIZATION_RUNTIME_001` remains the **sole package-level** claim-status owner.
3. A metric may be `READY_NUMERIC_ONLY` while `roi_claim_authorization_status = NOT_EVALUATED` or blocked.
4. TrustReport / F-DECISION / DecisionSurface / RecommendationContract remain **MIP-level** decision and trust owners where applicable.
5. This contract does not duplicate claim authorization logic or trusted readout integration.

---

## 8. Trusted readout representation

Future mapper runtime (or integrated trusted readout extension) should represent readiness as:

### `efficiency_metric_readiness` (per metric)

```yaml
metric_name: cost_per_incremental_kpi
numeric_readiness_status: BLOCKED_MISSING_SPEND_DELTA_OR_DELTA_MU
required_inputs: [spend_delta, delta_mu]
missing_inputs: [spend_delta]
source_fields:
  delta_mu: effect_estimate_report.point_estimate
  spend_delta: post_test_spend_evidence.spend_delta
lineage: { spend: GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001 }
warnings: []
claim_authorization_status: NOT_EVALUATED
claim_authorization_owner: CLAIM_AUTHORIZATION_RUNTIME_001
```

### `blocked_efficiency_metrics`

```yaml
- metric_name: ROAS
  blocked_status: BLOCKED_MISSING_REVENUE_OR_SPEND
  blocking_reasons: [BLOCKED_MISSING_VALUE_MAPPING, BLOCKED_MISSING_SPEND_DELTA]
  recoverable_by_user_input: true
  required_missing_inputs: [value_per_incremental_kpi, spend_delta]
```

### `diagnostic_efficiency_metrics`

```yaml
- metric_name: lift_pct
  numeric_value_available: true
  diagnostic_only_reason: UNCERTAINTY_NOT_GOVERNED
  claim_status: NOT_EVALUATED
```

Current integration runtime emits placeholder `NOT_COMPUTED` for efficiency metrics; this contract defines the mapping rules a future runtime must follow.

---

## 9. User / MIP-facing interpretation

MIP (or user-facing orchestration) may state:

- “Increment/lift are available, but cost-per requires `spend_delta`.”
- “ROAS requires incremental revenue or a value mapping plus `spend_delta`.”
- “Profit ROI requires margin/profit mapping plus `spend_delta`.”
- “Metric may be numerically ready but not claim-authorized.”
- “Budget recommendations require DecisionSurface/RecommendationContract, not raw readout.”

MIP must not present `READY_NUMERIC_ONLY` as authorized ROI/ROAS without `CLAIM_AUTHORIZATION_RUNTIME_001` pass-through.

---

## 10. Future runtime plan

**Recommended future artifact:** `GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_RUNTIME_001`

| Responsibility | Owner |
|----------------|-------|
| Consume trusted readout + integrated spend readiness section | Mapper runtime |
| Inspect `delta_mu`, counterfactual, `spend_delta`, value/margin inputs | Mapper runtime |
| Emit `efficiency_metric_readiness`, `blocked_efficiency_metrics`, `diagnostic_efficiency_metrics` | Mapper runtime |
| Compute numeric metric values | **Optional later** — not in scope of this contract |
| Authorize ROI/ROAS claims | **No** — claim authorization only |
| Make budget/decision recommendations | **No** — MIP DecisionSurface |

---

## 11. Lane B closure rule

After this contract, Lane B has the **minimum semantic chain**:

1. Post-test spend evidence derivation (`GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001`)
2. Trusted readout spend readiness integration (`GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001`)
3. Efficiency metric readiness mapping contract (this artifact)

Unless a blocker is found, **return to Lane A:**

`TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001`

Lane B optional follow-up (not blocking Lane A): `GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_RUNTIME_001`

---

## 12. Non-goals

- No runtime implemented
- No cost-per computation implemented
- No ROAS computation implemented
- No profit ROI computation implemented
- No ROI calculator runtime created
- No `spend_delta` recomputation
- No spend ingestion system
- No final-results module
- No claim authorization duplication
- No ROI/ROAS claim authorization
- No business recommendation authorization
- No production readout authorization
- No MIP orchestration implemented
- No estimator/inference implementation
- No method/instrument promotion
- No catalog unblock

---

## 13. Validation results

- Governance tests: `tests/governance/test_geox_efficiency_metric_readiness_mapper_contract_001.py`
- Summary JSON: `docs/track_d/archives/GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001_summary.json`
- Safety grep: forbidden capability flags must remain `false`
- Capability grep: contract completion flags must be `true`
