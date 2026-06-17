# D5-DES-STAT-TIER1-001 Report

**Artifact:** `D5-DES-STAT-TIER1-001` · **Verdict:** `tier1_designs_mixed_requires_method_specific_followup`

## 1. Executive summary

First executed tier-1 design statistical validation harness. Characterizes assignment feasibility, balance, reproducibility inputs, and contract/guardrail metadata for DES-001–004 and DES-006. **No promotion; downstream blocked.**

## 2. Scope

In scope: DES-001 greedy_match_markets, DES-002 CompleteRandomization, DES-003 BalancedRandomization, DES-004 StratifiedRandomization, DES-006 Rerandomization. Out of scope: DES-005, DES-007–011, adapters, bridges, product authorization.

## 3. Designs evaluated

- DES-001 `greedy_match_markets`
- DES-002 `complete_randomization`
- DES-003 `balanced_randomization`
- DES-004 `stratified_randomization`
- DES-006 `rerandomization`

## 4. Worlds evaluated

- `balanced_markets`
- `weak_donor_pool`
- `high_unit_heterogeneity`
- `small_n_markets`
- `high_pre_period_noise`
- `strong_seasonality`
- `trend_mismatch`
- `sparse_outcomes`
- `spend_imbalance`
- `geographic_cluster_correlation`
- `assignment_infeasibility`
- `missing_covariates`
- `outlier_markets`
- `unstable_pre_period`
- `matched_market_poor_match_world`
- `rerandomization_selection_effect_world`
- `stratification_poor_strata_world`
- `treatment_pool_exhaustion_world`

## 5. Harness architecture

Module: `panel_exp/validation/track_d_d5_des_stat_tier1_001.py` · generator `1.0.0`

## 6. Metrics

Assignment feasibility, balance (SMD, volume), population/support, reproducibility (assignment hash), design-specific diagnostics, contract/guardrail.

## 7. Runtime and run counts

- Attempted: 9500
- Completed: 9250
- Failed: 250
- Elapsed: 64.321s

## 8. Overall results

- **DES-001**: success rate 97.83%, control violation rate 23.65%, pass/warn/block/failed 0/0/2250/50, mean max SMD 0.802269726725241
- **DES-002**: success rate 97.22%, control violation rate 2.78%, pass/warn/block/failed 1070/580/100/50, mean max SMD 0.4517747656989507
- **DES-003**: success rate 97.22%, control violation rate 3.00%, pass/warn/block/failed 1053/593/104/50, mean max SMD 0.44786351513259226
- **DES-004**: success rate 97.22%, control violation rate 2.78%, pass/warn/block/failed 0/0/1750/50, mean max SMD 0.9403568312757697
- **DES-006**: success rate 97.22%, control violation rate 2.78%, pass/warn/block/failed 1070/580/100/50, mean max SMD 0.45024488270630836

## 9. DES-001 findings

Greedy exhaustion flagged runs: 450 (tp=0.35 subset: 150).

## 10. DES-002 findings

Complete randomization benchmark; Bernoulli share deviation tracked.

## 11. DES-003 findings

Volume-balance objective vs complete randomization in pairwise comparisons.

## 12. DES-004 findings

Stratum occupancy and within-stratum balance; poor-strata world stress.

## 13. DES-006 findings

Rerandomization attempts/acceptance tracked; wrapper/base identity preserved.

## 14. Pairwise comparisons

- complete_vs_balanced: exploratory; provisional_for_characterization_only
- complete_vs_stratified: exploratory; provisional_for_characterization_only
- complete_vs_rerandomization: exploratory; provisional_for_characterization_only
- greedy_vs_complete_matched_worlds: exploratory; provisional_for_characterization_only

## 15. Feasibility failures

Assignment failures: 250; block outcomes: 4304.

## 16. Greedy treatment-pool exhaustion findings

Treatment probabilities 0.20, 0.35, 0.50 tested in exhaustion world; minimum control threshold violations recorded without silent retry.

## 17. Small-N findings

`small_n_markets` world uses n_units=8.

## 18. Balance findings

SMD and volume imbalance tracked; provisional bands only.

## 19. Reproducibility findings

Assignment hashes recorded per successful run.

## 20. Contract/guardrail findings

Guardrail WARN rate (successful contract runs): 100.00%. downstream_may_proceed=False.

## 21. Statistical interpretation limits

Design-only characterization; not estimator/inference validity.

## 22. Suitability implications

Metadata may be WARN; statistical suitability still blocked; 0 downstream authorized.

## 23. Combination-matrix implications

Evidence informs matrix rows; no automatic upgrade.

## 24. Required fixes

Follow method-specific artifacts based on blocking failures (greedy feasibility, stratified sparse strata).

## 25. Follow-up artifacts

- ✅ [`D5-DES-STAT-GREEDY-FEASIBILITY-001`](D5_DES_STAT_GREEDY_FEASIBILITY_001_REPORT.md) — executed; control-reservation fix; verdict `greedy_feasibility_fixed_requires_statistical_followup`
- ✅ [`D5-DES-STAT-STRATIFIED-001`](D5_DES_STAT_STRATIFIED_001_REPORT.md) — executed; adaptive strata fix; verdict `stratified_feasibility_fixed_requires_statistical_followup`
- ✅ [`D5-DES-STAT-MULTICELL-001`](D5_DES_STAT_MULTICELL_001_REPORT.md) — executed; per-cell metadata; pooled blocked

> **Historical note:** Corrected-default comparisons for DES-001, DES-004, and DES-011 in this report reflect **legacy implementations** at tier-1 execution time. Follow-on feasibility fixes are characterized in the artifacts above; tier-1 recharacterization is pending.

## 26. Governance verdict

**tier1_designs_mixed_requires_method_specific_followup** — no production promotion.

