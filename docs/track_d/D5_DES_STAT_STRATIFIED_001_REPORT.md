# D5-DES-STAT-STRATIFIED-001 Report

**Verdict:** `stratified_feasibility_fixed_requires_statistical_followup` · **Selected policy:** `adaptive_strata`

The full run-level archive (`D5_DES_STAT_STRATIFIED_001_results.json`) is produced by the harness but is **not repository-tracked** due to size. Regenerate locally:

```bash
poetry run python -m panel_exp.validation.track_d_d5_des_stat_stratified_001 --overwrite
```

## 1. Executive summary

Diagnosed DES-004 StratifiedRandomization: legacy volume-gap assignment with singleton strata caused elevated global SMD (~0.94 tier-1 mean). Fix: adaptive strata + within-stratum Bernoulli. **No promotion.**

## 2. Prior tier-1 evidence

- DES-004 mean max SMD ~0.94; 100% block in tier-1 wave
- stratification_poor_strata_world (n_units=12, n_strata=12)

## 3. Current implementation

Legacy: percentile bins + volume-gap greedy assignment within strata (not Bernoulli).

## 4. Root-cause analysis

| Hypothesis | Evidence | Reproduced? | Root cause? | Fix |
|---|---|---|---|---|
| Singleton strata | n_strata≈n_units | Yes | Yes | Adaptive reduce |
| Volume-gap not randomization | High SMD vs CR | Yes | Yes | Bernoulli within stratum |
| digitize boundary artifacts | stray stratum labels | Yes | Partial | qcut + merge |
| No min occupancy | 1-unit strata | Yes | Yes | min_units_per_stratum=2 |

## 5. Stratification feasibility contract

See `panel_exp/design/stratified_feasibility.py`.

## 6. Candidate policies

- **A_legacy** (`legacy`)
- **B_preflight_fail** (`preflight_fail`)
- **C_adaptive_strata** (`adaptive_strata`)
- **D_sparse_merge** (`sparse_merge`)
- **E_complete_fallback** (`complete_randomization_fallback`)

## 7. Worlds and configuration

Worlds: 16 · Seeds: [101, 202, 303, 404, 505]

## 8. Metrics

Global/within-stratum SMD, stratum occupancy, singleton/sparse flags.

## 9. Runtime and run counts

Attempted: 57600 · Failed: 4680 · Elapsed: 128.814s

## 10. Baseline results

{'n_runs': 11520, 'assignment_success_rate': 1.0, 'mean_global_max_smd': inf, 'singleton_rate': 0.0, 'sparse_rate': 0.0, 'n_block': 5735, 'n_failed': 0}

## 11. Adaptive-strata results

{'n_runs': 11520, 'assignment_success_rate': 1.0, 'mean_global_max_smd': 0.2250010114412676, 'singleton_rate': 0.0, 'sparse_rate': 0.0, 'n_block': 1319, 'n_failed': 0}

## 12. Sparse-merge results

{'n_runs': 11520, 'assignment_success_rate': 1.0, 'mean_global_max_smd': 0.2250010114412676, 'singleton_rate': 0.0, 'sparse_rate': 0.0, 'n_block': 1319, 'n_failed': 0}

## 13. Fallback results

{'n_runs': 11520, 'assignment_success_rate': 1.0, 'mean_global_max_smd': 0.2250010114412676, 'singleton_rate': 0.0, 'sparse_rate': 0.0, 'n_block': 1319, 'n_failed': 0}

## 14. Sparse-strata findings

Legacy singleton runs: 0; Fixed: 0

## 15. Small-N findings

small_n_many_strata and n_units=8 stress feasibility reduction.

## 16. Global versus within-stratum balance

Legacy worsens global SMD when strata are singletons; fixed improves both.

## 17. Strong versus weak stratification variables

Characterized in predictive vs anti-predictive worlds.

## 18. Treatment-share fidelity

Requested vs realized tp recorded per run.

## 19. Metadata and contract findings

last_stratification_metadata on non-legacy policies.

## 20. Guardrail behavior

WARN; downstream blocked; contract_complete_allowed=False.

## 21. Selected policy

**adaptive_strata**

## 22. Implementation changes

- `panel_exp/design/stratified_feasibility.py`
- `StratifiedRandomization` in `assign.py`

## 23. Regression risks

Default policy changed; use `stratification_policy='legacy'` for baseline.

## 24. Suitability implications

Feasibility improved; statistical suitability still blocked.

## 25. Combination-matrix implications

DES-004 rows updated with feasible-regime evidence.

## 26. Remaining limitations

Single covariate; multi-dimensional stratification deferred.

## 27. Follow-up work

- Tier-1 DES-004 re-characterization
- D5-DES-STAT-MULTICELL-001

## 28. Governance verdict

**stratified_feasibility_fixed_requires_statistical_followup** — no production promotion.
