# D5-DES-STAT-TIER1-RECHARACTERIZATION-001 Report

**Verdict:** `tier1_recharacterized_mixed_method_specific_restrictions`

> **Supersession:** This report supersedes corrected-default comparisons in [D5_DES_STAT_TIER1_001_REPORT.md](D5_DES_STAT_TIER1_001_REPORT.md). The original tier-1 archive remains historical evidence.

Full archive (local only):

```bash
poetry run python -m panel_exp.validation.track_d_d5_des_stat_tier1_recharacterization_001 \
  --output-local /tmp/D5_DES_STAT_TIER1_RECHARACTERIZATION_001_results.json \
  --summary-output docs/track_d/archives/D5_DES_STAT_TIER1_RECHARACTERIZATION_001_summary.json \
  --overwrite
```

## 1. Executive summary

Post-fix tier-1 recharacterization across corrected defaults, legacy references, and a separate multi-cell per-cell-only lane. **No promotion.**

## 2. Why recharacterization was required

Greedy, stratified, and multi-cell defaults changed after D5-DES-STAT-TIER1-001.

## 3. Historical tier-1 baseline

See `D5-DES-STAT-TIER1-001` archive and report (retained as historical).

## 4. Corrected implementations

- DES-001: `control_reservation`
- DES-004: `adaptive_strata`
- DES-011: `control_reservation` (separate lane)

## 5. Scope and lanes

['single_cell_tier1', 'legacy_reference', 'multicell_per_cell_only']

## 6. Worlds and configuration

{'single_cell': ['balanced_markets', 'weak_donor_pool', 'high_unit_heterogeneity', 'small_n_markets', 'high_pre_period_noise', 'strong_seasonality', 'trend_mismatch', 'sparse_outcomes', 'spend_imbalance', 'geographic_cluster_correlation', 'assignment_infeasibility', 'missing_covariates', 'outlier_markets', 'unstable_pre_period', 'matched_market_poor_match_world', 'rerandomization_selection_effect_world', 'stratification_poor_strata_world', 'treatment_pool_exhaustion_world'], 'multicell': ['balanced_two_cell', 'balanced_three_cell', 'shared_control_overload_world', 'pooled_claim_trap_world', 'cell_size_imbalance', 'concurrent_experiment_pressure']}

## 7. Metrics

Feasibility, balance/SMD, greedy/stratified/multicell diagnostics, contract/guardrail.

## 8. Runtime and run counts

Matrix: `designs × worlds × treatment_points × replicates × seeds` (replicates and seeds are independent, matching tier-1 harness).

Attempted: 6500 · Expected: 6500 · Failed: 300 · Elapsed: 53.301s
Per-lane actual: {'single_cell_tier1': 4700, 'legacy_reference': 900, 'multicell_per_cell_only': 900} · Expected: {'single_cell_tier1': 4700, 'legacy_reference': 900, 'multicell_per_cell_only': 900, 'total': 6500}

## 9. Current-default aggregate results

{'single_cell_tier1:greedy_corrected': {'design_inventory_id': 'DES-001', 'lane': 'single_cell_tier1', 'label': 'greedy_corrected', 'n_runs': 1100, 'assignment_success_rate': 0.9545454545454546, 'control_violation_rate': 0.0, 'block_rate': 0.045454545454545456, 'mean_max_smd': 0.5862078397888353}, 'single_cell_tier1:complete_randomization': {'design_inventory_id': 'DES-002', 'lane': 'single_cell_tier1', 'label': 'complete_randomization', 'n_runs': 900, 'assignment_success_rate': 0.9444444444444444, 'control_violation_rate': 0.0, 'block_rate': 0.05555555555555555, 'mean_max_smd': 0.38073269332513976}, 'single_cell_tier1:balanced_randomization': {'design_inventory_id': 'DES-003', 'lane': 'single_cell_tier1', 'label': 'balanced_randomization', 'n_runs': 900, 'assignment_success_rate': 0.9444444444444444, 'control_violation_rate': 0.002352941176470588, 'block_rate': 0.057777777777777775, 'mean_max_smd': 0.3576505613701057}, 'single_cell_tier1:stratified_corrected': {'design_inventory_id': 'DES-004', 'lane': 'single_cell_tier1', 'label': 'stratified_corrected', 'n_runs': 900, 'assignment_success_rate': 0.9444444444444444, 'control_violation_rate': 0.0, 'block_rate': 0.05555555555555555, 'mean_max_smd': 0.10800355917098184}, 'single_cell_tier1:rerandomization': {'design_inventory_id': 'DES-006', 'lane': 'single_cell_tier1', 'label': 'rerandomization', 'n_runs': 900, 'assignment_success_rate': 0.9444444444444444, 'control_violation_rate': 0.0, 'block_rate': 0.05555555555555555, 'mean_max_smd': 0.38073269332513976}, 'legacy_reference:greedy_legacy': {'design_inventory_id': 'DES-001', 'lane': 'legacy_reference', 'label': 'greedy_legacy', 'n_runs': 450, 'assignment_success_rate': 0.9444444444444444, 'control_violation_rate': 0.2211764705882353, 'block_rate': 0.9444444444444444, 'mean_max_smd': 0.6467356928026545}, 'legacy_reference:stratified_legacy': {'design_inventory_id': 'DES-004', 'lane': 'legacy_reference', 'label': 'stratified_legacy', 'n_runs': 450, 'assignment_success_rate': 0.9444444444444444, 'control_violation_rate': 0.0, 'block_rate': 0.9444444444444444, 'mean_max_smd': 0.9030434029821387}, 'multicell_per_cell_only:multicell_corrected': {'design_inventory_id': 'DES-011', 'lane': 'multicell_per_cell_only', 'label': 'multicell_corrected', 'n_runs': 450, 'assignment_success_rate': 1.0, 'control_violation_rate': 0.0, 'block_rate': 0.0, 'mean_max_smd': 1.6355350695383792}, 'multicell_per_cell_only:multicell_legacy': {'design_inventory_id': 'DES-011', 'lane': 'multicell_per_cell_only', 'label': 'multicell_legacy', 'n_runs': 450, 'assignment_success_rate': 1.0, 'control_violation_rate': 0.0, 'block_rate': 0.0, 'mean_max_smd': 1.721986124873091}}

## 10. Greedy corrected findings

Corrected control violations: 50

## 11. Stratified corrected findings

Poor-strata high-SMD legacy: 24 · corrected: 1

## 12. Complete-randomization benchmark

DES-002 reference in single_cell_tier1 lane.

## 13. Balanced-randomization findings

See pairwise complete_vs_balanced.

## 14. Rerandomization findings

DES-006 wrapper with attempt diagnostics.

## 15. Legacy versus corrected greedy

{'legacy_label': 'greedy_legacy', 'corrected_label': 'greedy_corrected', 'n_paired': 425, 'median_smd_change_corrected_minus_legacy': -0.055216987763195155, 'control_violations_legacy': 94, 'control_violations_corrected': 0, 'high_smd_blocks_legacy': 260, 'high_smd_blocks_corrected': 231}

## 16. Legacy versus corrected stratified

{'legacy_label': 'stratified_legacy', 'corrected_label': 'stratified_corrected', 'n_paired': 425, 'median_smd_change_corrected_minus_legacy': -0.81270684154212, 'control_violations_legacy': 0, 'control_violations_corrected': 0, 'high_smd_blocks_legacy': 374, 'high_smd_blocks_corrected': 13}

## 17. Multi-cell per-cell-only findings

{'pooled_claims_blocked': True, 'cell_collision_rate': 0.0, 'mean_worst_cell_smd_corrected': 1.6355350695383792}

## 18. Pairwise comparisons

[{'comparison_id': 'complete_vs_balanced', 'median_smd_a': 0.3407985751460906, 'median_smd_b': 0.3573080916475164, 'median_smd_change_a_minus_b': -0.016509516501425847, 'note': 'single_cell_tier1 lane only'}, {'comparison_id': 'complete_vs_stratified_corrected', 'median_smd_a': 0.3407985751460906, 'median_smd_b': 0.10800355917098184, 'median_smd_change_a_minus_b': 0.23279501597510874, 'note': 'single_cell_tier1 lane only'}, {'comparison_id': 'complete_vs_rerandomization', 'median_smd_a': 0.3407985751460906, 'median_smd_b': 0.3407985751460906, 'median_smd_change_a_minus_b': 0.0, 'note': 'single_cell_tier1 lane only'}, {'comparison_id': 'greedy_corrected_vs_complete', 'median_smd_a': 0.4803258369099481, 'median_smd_b': 0.3407985751460906, 'median_smd_change_a_minus_b': 0.13952726176385755, 'note': 'single_cell_tier1 lane only'}]

## 19. Feasibility findings

{'n_assignment_failures': 300, 'n_blocks': 1102, 'greedy_corrected_control_violations': 50, 'greedy_legacy_control_violations': 119, 'stratified_poor_strata_high_smd_legacy': 24, 'stratified_poor_strata_high_smd_corrected': 1}

## 20. Balance findings

{'corrected_mean_max_smd_by_design': {'single_cell_tier1:greedy_corrected': 0.5862078397888353, 'single_cell_tier1:complete_randomization': 0.38073269332513976, 'single_cell_tier1:balanced_randomization': 0.3576505613701057, 'single_cell_tier1:stratified_corrected': 0.10800355917098184, 'single_cell_tier1:rerandomization': 0.38073269332513976}}

## 21. Worst-case behavior

Captured via block_rate and high-SMD counts per design.

## 22. Contract and guardrail findings

{'downstream_may_proceed': False, 'contract_complete_allowed': False, 'pooled_claims_allowed': False}

## 23. Supersession statement

{'historical_artifact_id': 'D5-DES-STAT-TIER1-001', 'historical_report': 'docs/track_d/D5_DES_STAT_TIER1_001_REPORT.md', 'supersedes_default_comparisons_for': ['DES-001', 'DES-004', 'DES-011'], 'historical_evidence_retained': True, 'note': 'Original tier-1 archive remains historical; greedy/stratified/multicell default comparisons in that report are superseded for corrected-default policy.', 'historical_baseline_notes': {'greedy_legacy_control_floor_rate_approx': 0.28, 'stratified_legacy_high_smd_reduction_approx': 0.82, 'multicell_pooled_claims_blocked': True}}

## 24. Suitability implications

0 downstream suitable; statistical validation still required per design.

## 25. Combination-matrix implications

Corrected-default evidence updates DCM rows; pooled multi-cell remains blocked.

## 26. Remaining limitations

- Design-only recharacterization; no promotion or downstream authorization.
- Multi-cell lane excluded from single-cell rankings.
- Legacy lanes are reference-only, not supported defaults.

## 27. Recommended next work

DESIGN_GUARDRAIL_ENFORCEMENT_001 or DESIGN_COMBINATION_VALIDATION_EXECUTION_001.

## 28. Governance verdict

**tier1_recharacterized_mixed_method_specific_restrictions** — no production promotion.
