# AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001

## Artifact ID, status, and base

| Field | Value |
|-------|-------|
| **Artifact ID** | `AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001` |
| **Artifact type** | `audit_driven_roadmap_correction` |
| **Status** | `active` |
| **Base commit** | `5f93625` (Define claim authorization contract) |
| **Lane ID** | `AUDIT-P0-GOVERNED-RUNTIME-HARDENING-001` |
| **Investigation ID** | `INV-AUDIT-P0-GOVERNED-RUNTIME-HARDENING-001` |

## Audit-driven roadmap correction

Expanded adversarial audit (2026-07-03) verdict: **promising but incomplete**.

`CLAIM_AUTHORIZATION_CONTRACT_001` is complete and safe as a contract-only artifact. `CLAIM_AUTHORIZATION_RUNTIME_001` remains planned but **must not** be the immediate next implementation artifact.

Current governed execution has only:

- one DID point-estimate executor (`estimator_inference_did_executor_003.py`),
- one structural DID diagnostic (`readout_did_diagnostics_002.py`),
- no governed production-safe inference path,
- no assignment-panel integrity runtime,
- no enforced production blocklist,
- no statistical promotion threshold enforcement,
- and no governed randomization runtime.

The roadmap now inserts **P0 governed runtime hardening** before claim authorization runtime.

## Revised execution sequence

```text
CLAIM_AUTHORIZATION_CONTRACT_001 (complete)
→ PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001
→ DID_INSTRUMENT_ESTIMAND_UNIFICATION_001
→ ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001
→ STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001
→ GOVERNED_RANDOMIZATION_RUNTIME_001
→ SRM_BALANCE_READOUT_DIAGNOSTIC_001
→ CLAIM_AUTHORIZATION_RUNTIME_001
→ TRUSTED_READOUT_REPORT_CONTRACT_001
→ TRUSTED_READOUT_REPORT_RUNTIME_001
```

## P0 hardening lane artifacts

| Order | Artifact | Priority |
|------:|----------|----------|
| 1 | `PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001` | P0 |
| 2 | `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001` | P0 |
| 3 | `ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001` | P0 |
| 4 | `STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001` | P0 |
| 5 | `GOVERNED_RANDOMIZATION_RUNTIME_001` | P0/P1 |
| 6 | `SRM_BALANCE_READOUT_DIAGNOSTIC_001` | P1 |

## Artifact disposition

| Artifact | Action | Reason | Dependency | Acceptance criteria |
|----------|--------|--------|------------|---------------------|
| `CLAIM_AUTHORIZATION_CONTRACT_001` | complete / keep | Contract-only safe | Completed at `5f93625` | No runtime authorization |
| `CLAIM_AUTHORIZATION_RUNTIME_001` | keep but delay | Must not authorize claims before P0 hardening | P0 hardening lane | No authorization without evidence, lineage, catalog gates |
| `PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001` | insert P0 | Failed/uncalibrated combos must be blocked | `method_metadata`, promotion criteria, D5 archives | Blocked combos cannot be production candidates |
| `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001` | insert P0 | `DID_BOOTSTRAP` naming vs 2×2-vs-TWFE split | DID executor, library DID | One instrument = one estimand/inference contract |
| `ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001` | insert P0 | Panel treatment labels must match assignment artifact | Assignment runtime, execution runtime | Mismatch blocks execution |
| `STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001` | complete | Numeric FPR/coverage/bias gates enforced in runtime/tests |
| `GOVERNED_RANDOMIZATION_RUNTIME_001` | insert P0/P1 | Safe path lacks causal randomization | `design/assign.py`, assignment runtime | Seeded immutable assignment artifact |
| `SRM_BALANCE_READOUT_DIAGNOSTIC_001` | insert P1 | No SRM/balance gate in readout evidence | Diagnostics runtime | SRM/balance evidence packet emitted |
| `TRUSTED_READOUT_REPORT_CONTRACT_001` | keep deferred | After claim runtime | Claim runtime | Only authorized claims displayed |
| `TRUSTED_READOUT_REPORT_RUNTIME_001` | keep deferred | After trusted report contract | Report contract | No consumer-facing unauthorized readout |
| `AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001` | pause / defer | Sophistication before P0 validity closure | P0 hardening | Resume only after blocklist/threshold gates |
| `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_004_BOOTSTRAP_INFERENCE` | defer | Bootstrap inference waits for DID remediation | Statistical threshold enforcement | Recovery/calibration gates pass |
| TROP / MTGP / BayesianTBR production | keep research-only | Insufficient production evidence | Future research lane | No promotion without recovery evidence |

## Maturity policy

- No estimator is currently `PRODUCTION_SAFE` in `panel_exp/method_metadata.py`.
- **Implemented** is not production-safe.
- **Characterized** is not production-safe.
- **Governed runtime supported** is not claim-authorized.
- **Evidence sufficiency** is not authorization (`readout_diagnostics_sensitivity_runtime_001`: `claim_authorized: false`).
- **Point estimate** is not causal lift.
- **Diagnostic pass** is not production approval.

## Production blocklist stance (target enforcement)

The production catalog must eventually enforce:

- `DID_BOOTSTRAP` production claims blocked until bootstrap inference is corrected/calibrated (`D5_STAT_DID_BOOTSTRAP_001`: positive coverage ~4.4%).
- `TBRRidge` + `UnitJackKnife`, `TBRRidge` + `Conformal`, `TBRRidge` + `JKP`, and `TBRRidge` + `TimeSeriesKfold` production claims blocked while negative/invalid interval evidence remains (`D5_INST_TBRRIDGE_002`).
- `TBR` aggregate production path blocked unless unit-panel semantics are resolved.
- `AugSynth` / `AugSynthCVXPY` + `Conformal` remain diagnostic/research-only until null calibration and adapter gates pass.
- `SyntheticDID`, `TROP`, `MTGP`, `BayesianTBR`, `BayesianTBRHorseShoe` remain research-only.

## Do not build yet

- production TrustReport operations
- LLM/MIP/MMM downstream decisioning
- estimator-shopping UI
- automatic estimator ensemble selection
- advanced estimator production exposure: SDID, TROP, MTGP, BayesianTBR
- adaptive experimentation / bandits
- bootstrap inference runtime before DID bootstrap remediation and statistical threshold enforcement
- AugSynth/ASCM production remediation before P0 validity closure

## P0 lane acceptance criteria

P0 hardening is done only when:

1. Production blocklist exists and is enforced in governed planning/execution path.
2. DID instrument IDs align with actual estimand and inference behavior.
3. Assignment-panel integrity mismatch blocks execution.
4. Statistical promotion thresholds are numeric and enforced in tests/CI for at least major characterized paths.
5. Governed randomization emits immutable seeded assignment artifacts.
6. SRM/balance diagnostic emits evidence packets.
7. `CLAIM_AUTHORIZATION_RUNTIME_001` consumes these gates and cannot authorize claims without them.

## Recommended next artifact

**Immediate:** `PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001`

**Alternative:** `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001`
