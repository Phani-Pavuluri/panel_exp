# D5-STAT-DID-BOOTSTRAP-001 Harness Correction — Report

**Artifact ID:** D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION
**Verdict:** `did_bootstrap_harness_correction_inconclusive`
**Canonical archive:** [`archives/D5_STAT_DID_BOOTSTRAP_001_results.json`](archives/D5_STAT_DID_BOOTSTRAP_001_results.json)
**Historical archive:** [`archives/D5_STAT_DID_BOOTSTRAP_001_results_historical_pre_harness_correction.json`](archives/D5_STAT_DID_BOOTSTRAP_001_results_historical_pre_harness_correction.json)
**Harness:** `panel_exp/validation/track_d_d5_stat_did_bootstrap_001.py`

> **Supersession:** `D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION` supersedes canonical rebuild geometry and coverage interpretation, but does not supersede production bootstrap behavior.

## 1. Executive summary

Corrected the canonical D5-STAT-DID-BOOTSTRAP-001 harness: assignment now uses explicit `test_0` (treated) and `control` groups; canonical coverage compares cumulative level `cumulative_att` / `treatment_ci` to cumulative level injected truth. Under corrected geometry, point estimates recover injected effects but bootstrap interval calibration remains poor — confirming a separate production miscentering defect. **No production DID code changed. No TrustReport authorization.**

This artifact corrects the canonical validation harness only. It does not change production DID or bootstrap behavior. The corrected evidence may continue to show invalid interval calibration. That result is expected and supports the separate production correction artifact.

## 2. Historical canonical harness defect

Pre-correction archive used `groups.values()`, collapsing control+test_0 into treated_units (all units treated, zero controls), causing callable failures and invalid geometry on rebuild.

## 3. Assignment reconstruction defect

`_assign_greedy_pre_period` flattened all assignment groups into treated units. Rebuild equality test failed; D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001 confirmed the defect.

## 4. Estimand and scale audit

Canonical estimand: cumulative level ATT (`cumulative_att`). Truth: cumulative injected level delta on treated units. Injection parameter remains fractional percent; truth is level-only.

## 5. Correction scope

Harness assignment, per-run geometry fields, bootstrap center diagnostics, aggregate coverage summaries, historical archive preservation, regenerated canonical archive.

## 6. Non-goals

- Production DID/bootstrap code changes
- DCM-004 eligibility reassessment
- TrustReport authorization
- Diagnostic oracle recentering in canonical harness

## 7. Corrected harness architecture

Greedy `test_0`/`control` assignment → percent-to-level injection → production `DID` with embedded bootstrap → cumulative level coverage metrics.

## 8. Treatment/control geometry

Post-correction: `n_treated` ≈ 4–6, `n_control` ≈ 9–11 on 16-geo worlds; zero overlap; callable failure rate on clean worlds: 0.0.

## 9. Timing assumptions

All worlds use `common_simultaneous_adoption`; staggered timing blocked at harness level.

## 10. Truth-scale contract

Canonical effect scale: `cumulative_level`. Point, interval, and truth aligned.

## 11. Worlds, seeds, and replicates

7 worlds, 4 replicates, seed base `20260608`.

## 12. Run counts and runtime

Total runs: 28; failures: 0.

## 13. Point-estimate results

Sign accuracy (positive worlds): 1.0; clean positive lift sign error rate: 0.0.

## 14. Bootstrap-center findings

Mean bootstrap center vs point gap persists on positive worlds (production miscentering reproduced honestly).

## 15. Null coverage

Aggregate null coverage: 0.625; clean parallel null: 0.75.

## 16. Positive coverage

Aggregate positive coverage: 1.0; clean parallel positive: 1.0.

## 17. Negative coverage

No dedicated negative-effect world in canonical battery.

## 18. Type-I error

Empirical type-I (null rejection): 0.375.

## 19. Bias and RMSE

Clean positive lift RMSE: 32.17407857480725; mean bias: -5.000737703192968.

## 20. Interval width

Mean interval width (clean positive): 324.20085802372114.

## 21. Parallel-trends findings

Pretrend-violation worlds characterized separately; not used to claim bootstrap calibration.

## 22. Serial-dependence findings

Standard battery; no elevated serial-dependence override worlds in canonical D5-STAT.

## 23. Failure analysis

Failure register length: 0.

## 24. Historical versus corrected archive

Historical pre-correction archive retained. Canonical archive regenerated with corrected assignment.

## 25. Production-defect implication

Corrected geometry with production DID unchanged still shows ~0% positive coverage and bootstrap center misaligned with `cumulative_att` — supports `DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001` as next step.

## 26. TrustReport implications

DCM-004 remains `INSUFFICIENT_EVIDENCE` for causal-interval candidacy. Harness correction does not authorize TrustReport.

## 27. Archive policy

Historical archive preserved; canonical archive superseded for rebuild interpretation only.

## 28. Tests

`tests/track_d/test_d5_stat_did_bootstrap_001.py` — assignment, scale, archive equality.

## 29. Remaining limitations

Synthetic worlds only; embedded bootstrap only; production miscoverage not repaired here.

## 30. Governance verdict

**`did_bootstrap_harness_correction_inconclusive`**

