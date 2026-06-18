# D5-STAT-SCM-JK-001 Harness Correction — Report

**Artifact ID:** D5-STAT-SCM-JK-001-HARNESS-CORRECTION  
**Verdict:** `scm_jk_harness_corrected_level_consistent_baseline_established`  
**Canonical archive:** [`archives/D5_STAT_SCM_JK_001_results.json`](archives/D5_STAT_SCM_JK_001_results.json)  
**Historical archive:** [`archives/D5_STAT_SCM_JK_001_results_historical_pre_harness_correction.json`](archives/D5_STAT_SCM_JK_001_results_historical_pre_harness_correction.json)  
**Harness:** `panel_exp/validation/track_d_d5_stat_scm_jk_001.py`

> **Supersession:** `D5-STAT-SCM-JK-001-HARNESS-CORRECTION` supersedes the canonical rebuild/coverage interpretation for corrected assignment and truth-scale semantics. The pre-correction archive is retained as historical evidence.

## 1. Executive summary

Corrected the canonical D5-STAT-SCM-JK-001 evidence harness: assignment now uses explicit `test_0` (treated) and `control` groups; canonical coverage compares **level-unit** intervals to **level-unit** injected truth. The regenerated archive shows **null coverage ~89%** and **positive-effect level coverage ~90%** at 15 replicates/world, versus **~0% positive coverage on the erroneous fractional-percent comparison** that drove TRUSTREPORT-ELIGIBILITY-VALIDATION-001's ~7% finding. **No production SCM or UnitJackknife code changed. No TrustReport authorization.**

## 2. Historical defect

TRUSTREPORT-ELIGIBILITY-VALIDATION-001 and the committed pre-correction archive reported null coverage ~93% but positive-scenario coverage ~7%, blocking causal-interval candidacy for DCM-001. D5-TRUST-SCM-JK-COVERAGE-REMEDIATION-001 diagnosed two harness defects as the primary drivers.

## 3. Assignment bug

`_assign_greedy_pre_period` used `groups.values()`, unioning **control** and **test_0** into the treated list. That assigned all units as treated (0 controls), causing rebuild failures and invalid geometry when the harness was re-executed.

**Fix:** extract `test_0` as treated and `control` as donors; record `n_treated`, `n_control`; reject overlap.

## 4. Truth-scale bug

Coverage compared level-unit SCM effect intervals (`y − y_hat` mean) against fractional percent truth (`0.08`) without conversion. Injected effects are level deltas (`percent × mean_baseline`), so positive coverage on percent scale was structurally near zero.

**Fix:** canonical `coverage` / `coverage_level` use `true_effect_level`; `coverage_fractional_percent` retained as diagnostic showing the historical mismatch.

## 5. Correction scope

- Harness assignment and metrics in `track_d_d5_stat_scm_jk_001.py`
- Regenerated `D5_STAT_SCM_JK_001_results.json` and updated `D5_STAT_SCM_JK_001_REPORT.md`
- Preserved historical archive copy
- Tests and governance registration

## 6. Non-goals

- Production SCM mathematics
- Production UnitJackknife mathematics
- TrustReport authorization or eligibility reassessment (separate artifact)
- Unrelated archive regeneration

## 7. Corrected harness architecture

Greedy `test_0` assignment → percent-to-level injection → `SyntheticControlCVXPY` + `UnitJackKnife` → effect-scale intervals → level-consistent coverage. Six seed retries per replicate; failures preserved in `failure_register`.

## 8. Geometry validation

Post-correction feasible runs show `n_treated` ≈ 4–6, `n_control` ≈ 9–11 (16 geos), `donor_count` = `n_control`. No treated/control overlap. `min_control_units=4` enforced.

## 9. Effect-scale definition

| Scale | Definition | Coverage role |
|-------|------------|---------------|
| `level_effect` | Injected level delta on treated mean | **Canonical** |
| `fractional_percent_effect` | Injection parameter (e.g. 0.08) | Diagnostic only |
| `absolute_percent_effect` | `fractional × 100` (e.g. 8.0) | Recorded, not used for coverage |

## 10. Worlds/seeds/replicates

7 worlds (`REQUIRED_WORLD_IDS`), 15 replicates each, seed base `20260604`, up to 6 assignment attempts per replicate.

## 11. Run counts

105 total runs, 0 failures, ~16s full regeneration.

## 12. Point-estimate results

SCM point estimates track injected level effects; mean bias on level scale is small relative to injected level magnitude. Fractional-percent bias remains large by construction (wrong units).

## 13. Null coverage

Aggregate null-world **level coverage: 89.3%** (`clean_null` 86.7%, other null worlds contribute).

## 14. Positive-effect coverage

Aggregate positive-world **level coverage: 90.0%** (`clean_positive_lift` 100%, `noisy_positive_lift` 80%).  
**Fractional-percent coverage: 0.0%** (reproduces historical eligibility metric).

## 15. Negative-effect coverage

No dedicated negative-effect world in D5-STAT-SCM-JK-001 battery (unchanged from prior design).

## 16. Type-I error

Empirical null rejection (interval excludes zero) **~10.7%** across null worlds.

## 17. Bias/RMSE

Bias and RMSE computed on **level scale** in corrected archive (`mean_bias` = `mean_bias_level`).

## 18. Pre-fit relationship

`prefit_rmse_mean` recorded per world; `outside_hull_or_poor_prefit` shows lower pre-fit RMSE with somewhat elevated null FPR — pre-fit stress documented, not used for promotion.

## 19. Donor-support relationship

`donor_count_mean` ~9–11 post-correction (vs invalid 0-control geometry pre-fix). Donor-stress null world remains feasible.

## 20. Failure analysis

Pre-correction rebuild: 100% failure (insufficient controls). Post-correction: 0/105 failures in canonical regeneration.

## 21. Historical versus corrected comparison

| Metric | Historical archive | Corrected archive |
|--------|-------------------|-------------------|
| Rebuild | Failed (0% feasible) | 105/105 feasible |
| Positive coverage (canonical) | ~7% (percent scale) | **~90% (level scale)** |
| Null coverage | ~93% | ~89% |
| Assignment | All units treated | test_0 / control split |

Historical archive preserved at `D5_STAT_SCM_JK_001_results_historical_pre_harness_correction.json`.

## 22. TrustReport implications

Corrected evidence supports **level-consistent null-monitor and diagnostic characterization**. Causal-interval TrustReport promotion remains **not authorized**. **TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001** required before any DCM-001 class change.

## 23. Archive policy

Full corrected archive committed (~168 KB, under 90 MB limit). Historical archive committed alongside. CLI: `--output`, `--overwrite`, `--fast`.

## 24. Tests

`tests/track_d/test_d5_stat_scm_jk_001.py` — assignment extraction, no `groups.values()`, level-scale coverage, supersession metadata, archive/rebuild equality, historical preservation.

## 25. Limitations

15 replicates/world (characterization MC, not promotion-grade). Synthetic worlds only. Multi-treated `test_0` aggregation semantics unchanged. Eligibility evaluator not updated in this artifact.

## 26. Verdict

**`scm_jk_harness_corrected_level_consistent_baseline_established`** — corrected harness produces valid geometry and level-consistent coverage baseline. Historical ~7% positive undercoverage explained by truth-scale mismatch, not production inference failure.
